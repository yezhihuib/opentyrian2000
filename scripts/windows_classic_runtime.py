#!/usr/bin/env python3
"""Prepare/check a new isolated Windows CLASSIC run. No implicit launch or HD.
Original data stays external. A trusted receipt digest is mandatory before launch.
"""
import argparse,hashlib,json,os,re,shutil,stat,struct,subprocess,sys,time
from pathlib import Path,PurePosixPath
WINDOWS=(os.name=='nt')
SCHEMA='opentyrian-windows-classic-runtime-v1'
SCRIPT='tools/windows_classic_runtime.py'
DATA_FILES=('tyrian1.lvl','tyrian.hdt','tyrian.cdt','tyrian.snd','voices.snd','music.mus','palette.dat')
ALLOWED_FILES={'bin/opentyrian2000-level2.exe','bin/SDL2.dll','bin/SDL2_net.dll',SCRIPT,'trust/BUILD-WINDOWS.json','trust/STAGE.json'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def valid_digest(value):
 if not re.fullmatch('[0-9a-fA-F]{64}',value):raise ValueError('Expected externally verified SHA256')
 return value.lower()
def safe_path(value,must_exist=True):
 p=Path(value).expanduser()
 if not p.is_absolute() or '..' in p.parts:raise ValueError('Use an absolute path without parent traversal')
 p=Path(os.path.abspath(p))
 for node in reversed((p,)+tuple(p.parents)):
  try:s=node.lstat()
  except FileNotFoundError:
   if node==p and not must_exist:continue
   raise ValueError('Missing path/parent: '+str(node))
  if stat.S_ISLNK(s.st_mode) or getattr(s,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024):raise ValueError('Symlink/reparse path rejected: '+str(node))
 return p

def read_trusted(path,digest):
 p=safe_path(path)
 if not p.is_file():raise ValueError('Expected regular file: '+str(p))
 raw=p.read_bytes()
 if sha(raw)!=valid_digest(digest):raise ValueError('SHA256 mismatch: '+str(p))
 return p,raw

def pe_amd64(raw,is_dll=False):
 if len(raw)<64 or raw[:2]!=b'MZ':raise ValueError('Not PE')
 pe=struct.unpack_from('<I',raw,60)[0]
 if pe+24>len(raw) or raw[pe:pe+4]!=b'PE\0\0' or struct.unpack_from('<H',raw,pe+4)[0]!=0x8664:raise ValueError('Not AMD64 PE')
 characteristics=struct.unpack_from('<H',raw,pe+22)[0]
 if bool(characteristics&0x2000)!=is_dll:raise ValueError('Wrong PE EXE/DLL role')

def json_bytes(raw):return json.loads(raw.decode('utf-8-sig'))
def data_inventory(path):
 p=safe_path(path)
 if not p.is_dir():raise ValueError('Original data must be a directory')
 files={}
 for name in DATA_FILES:
  f=safe_path(p/name)
  if not f.is_file() or not f.stat().st_size:raise ValueError('Missing/empty required original data: '+name)
  with f.open('rb') as stream:
   h=hashlib.sha256()
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
  files[name]={'bytes':f.stat().st_size,'sha256':h.hexdigest()}
 return p,files

def prepare_plan(args):
 if getattr(args,'hd',False) or getattr(args,'public_candidates',False):raise ValueError('This isolated launcher is classic-only; HD resource preparation is not yet supported')
 output=safe_path(args.output,False)
 if output.exists():raise ValueError('Output must be new; never adopt an existing profile')
 data,inventory=data_inventory(args.data)
 stagepath,stageraw=read_trusted(args.stage_receipt,args.stage_sha256)
 buildpath,buildraw=read_trusted(args.build_receipt,args.build_sha256)
 stage=json_bytes(stageraw);build=json_bytes(buildraw)
 if stage.get('schema')!=1 or stage.get('status')!='STAGED_NOT_BUILT' or stage.get('translation_units')!=112:raise ValueError('Unsupported source stage receipt')
 if build.get('schema')!=1 or build.get('status')!='BUILT_NOT_RUN' or build.get('exit_code')!=0 or build.get('pe_machine')!='AMD64' or build.get('inputs_unchanged_after_build') is not True:raise ValueError('Build is not verified successful AMD64')
 if build.get('stage_sha256')!=sha(stageraw) or build.get('source_digest')!=stage.get('source_digest'):raise ValueError('Stage/build identity mismatch')
 inputs={};sources={};source_paths=[]
 for attr,name,dll in (('exe','opentyrian2000-level2.exe',False),('sdl2','SDL2.dll',True),('sdl_net','SDL2_net.dll',True)):
  p,raw=read_trusted(getattr(args,attr),getattr(args,attr+'_sha256'));pe_amd64(raw,dll)
  source_paths.append(p);inputs['bin/'+name]=raw;sources['bin/'+name]=p
  if attr=='exe' and build.get('binary',{}).get('sha256')!=sha(raw):raise ValueError('EXE differs from trusted build receipt')
  dep=build.get('dependencies',{}).get('SDL2' if attr=='sdl2' else 'SDL2_net',{}).get('runtime_dll_inventory')
  if dll and dep and dep.get('sha256')!=sha(raw):raise ValueError('DLL differs from build inventory')
 script=safe_path(Path(__file__).absolute());inputs[SCRIPT]=script.read_bytes()
 inputs['trust/BUILD-WINDOWS.json']=buildraw;inputs['trust/STAGE.json']=stageraw
 sources[SCRIPT]=script;sources['trust/BUILD-WINDOWS.json']=buildpath;sources['trust/STAGE.json']=stagepath
 protected=[data,script.parent,buildpath.parent,stagepath.parent]+[x.parent for x in source_paths]
 for root in protected:
  if output==root or root in output.parents or output in root.parents:raise ValueError('Runroot must be outside all source/data/build trees')
 receipt={'schema':SCHEMA,'mode':'classic','created_utc':time.time(),'data_directory':str(data),'data_files':inventory,'source_digest':stage['source_digest'],'build_sha256':sha(buildraw),'stage_sha256':sha(stageraw),'files':{name:{'bytes':len(raw),'sha256':sha(raw)} for name,raw in sorted(inputs.items())},'launcher_sha256':sha(inputs[SCRIPT]),'game_started':False,'runtime_acceptance':False,'single_launch_only':True,'data_check':'Required startup files readable and hashed, not complete game-data semantic validation','menu_assets':'Native UI fallback; no optional HD art bundled'}
 return output,receipt,inputs,sources

def copy_preserving_streams(source,target):
 # Windows native CopyFile preserves alternate streams/Zone.Identifier and refuses replacement.
 safe_path(source);safe_path(target.parent)
 if target.exists():raise ValueError('Refusing replacement: '+str(target))
 if WINDOWS:
  import ctypes
  api=ctypes.WinDLL('kernel32',use_last_error=True).CopyFileW
  api.argtypes=(ctypes.c_wchar_p,ctypes.c_wchar_p,ctypes.c_int);api.restype=ctypes.c_int
  if not api(str(source),str(target),1):raise ctypes.WinError(ctypes.get_last_error())
 else:
  # Offline test path only. Windows launch is never emulated here.
  shutil.copy2(source,target,follow_symlinks=False)
 safe_path(target)

def prepare(args):
 output,receipt,inputs,sources=prepare_plan(args)
 if not args.prepare:return {'status':'CHECK_ONLY','output':str(output),'immutable_files':list(inputs),'mode':'classic','game_started':False,'output_created':False}
 output.mkdir(exist_ok=False)
 for name,raw in inputs.items():
  target=output/name;target.parent.mkdir(exist_ok=True)
  safe_path(target.parent)
  copy_preserving_streams(sources[name],target)
  if sha(target.read_bytes())!=sha(raw):raise OSError('Copied byte mismatch: '+name)
 raw=(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode()
 with (output/'RUNTIME.json').open('xb') as f:f.write(raw)
 return {'status':'PREPARED_NOT_RUN','root':str(output),'runtime_receipt_sha256':sha(raw),'immutable_files':len(inputs),'mode':'classic','game_started':False,'output_created':True,'trust_note':'Preserve receipt digest independently; launch requires it explicitly'}

def verify_run(root,trusted_sha256):
 root=safe_path(root)
 if not root.is_dir():raise ValueError('Runroot missing')
 _,raw=read_trusted(root/'RUNTIME.json',trusted_sha256);receipt=json_bytes(raw)
 if receipt.get('schema')!=SCHEMA or receipt.get('mode')!='classic' or receipt.get('single_launch_only') is not True:raise ValueError('Unsupported runtime receipt')
 files=receipt.get('files',{})
 if set(files)!=ALLOWED_FILES or len({x.casefold() for x in files})!=len(files):raise ValueError('Unexpected immutable manifest')
 for relative,entry in files.items():
  p=PurePosixPath(relative)
  if p.is_absolute() or '..' in p.parts or '\\' in relative or ':' in relative:raise ValueError('Unsafe manifest path')
  _,content=read_trusted(root/relative,entry['sha256'])
  if len(content)!=entry['bytes']:raise ValueError('Changed length: '+relative)
  if relative.startswith('bin/'):pe_amd64(content,relative.lower().endswith('.dll'))
 expected=ALLOWED_FILES|{'RUNTIME.json'}
 # First launch only. No preexisting saves, extra executable/DLL or stale logs.
 for p in root.rglob('*'):
  safe_path(p)
  if p.is_file() and p.relative_to(root).as_posix() not in expected:raise ValueError('Unexpected/preexisting run file: '+str(p))
 self_path=safe_path(Path(__file__).absolute())
 if sha(self_path.read_bytes())!=receipt['launcher_sha256'] or receipt['launcher_sha256']!=files[SCRIPT]['sha256']:raise ValueError('Launcher identity mismatch')
 data,inventory=data_inventory(receipt['data_directory'])
 if inventory!=receipt['data_files']:raise ValueError('Original data changed since preparation')
 build=json_bytes((root/'trust/BUILD-WINDOWS.json').read_bytes());stage=(root/'trust/STAGE.json').read_bytes()
 if sha(stage)!=receipt['stage_sha256'] or sha((root/'trust/BUILD-WINDOWS.json').read_bytes())!=receipt['build_sha256'] or build.get('binary',{}).get('sha256')!=files['bin/opentyrian2000-level2.exe']['sha256']:raise ValueError('Broken build chain')
 return root,receipt,data

def child_environment(root,inherited):
 # Short allowlist drops mixed-case candidate/SDL/dummy controls by construction.
 values={k.upper():v for k,v in inherited.items()}
 result={k:values[k] for k in ('SYSTEMROOT','WINDIR','SYSTEMDRIVE','TEMP','TMP','USERPROFILE','LOCALAPPDATA','APPDATA') if k in values}
 system=values.get('SYSTEMROOT')
 if not system:raise ValueError('Missing trusted Windows SYSTEMROOT')
 system=safe_path(system)
 result['PATH']=str(root/'bin')+os.pathsep+str(system/'System32')+os.pathsep+str(system)
 return result

def run(args):
 root,receipt,data=verify_run(args.root,args.trust_sha256)
 plan={'status':'CHECK_ONLY','mode':'classic','argv':[str(root/'bin/opentyrian2000-level2.exe'),'--data='+str(data)],'cwd':str(root),'game_started':False,'runtime_acceptance':False}
 if not args.launch:return plan
 if not WINDOWS:raise ValueError('Actual launch supported only on Windows; no emulation or permission bypass')
 env=child_environment(root,dict(os.environ))
 # No mutation of process cwd/environment; child inherits ordinary console handles.
 started={'status':'STARTING','started_utc':time.time(),'receipt_sha256':args.trust_sha256.lower(),'mode':'classic','runtime_acceptance':False}
 with (root/'launch-start.json').open('x',encoding='utf-8') as f:json.dump(started,f,indent=2)
 try:
  child=subprocess.Popen(plan['argv'],cwd=root,env=env)
  result={'status':'EXITED','pid':child.pid,'exit_code':child.wait(),'game_started':True,'runtime_acceptance':False}
 except (Exception,KeyboardInterrupt) as exc:
  result={'status':'START_OR_WAIT_FAILED','error':str(exc),'game_started':False,'runtime_acceptance':False}
  # If wait failed after process creation, report that the process may still run.
  if 'child' in locals():result.update(game_started=True,pid=child.pid,may_still_be_running=child.poll() is None)
 result['ended_utc']=time.time();result['receipt_sha256']=args.trust_sha256.lower()
 with (root/'launch-end.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
 return result

def parser():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 q=sub.add_parser('prepare');q.add_argument('--output',required=True);q.add_argument('--data',required=True)
 for name in ('exe','sdl2','sdl-net','build-receipt','stage-receipt'):
  q.add_argument('--'+name,required=True)
  digest_name={'build-receipt':'build','stage-receipt':'stage'}.get(name,name)
  q.add_argument('--'+digest_name+'-sha256',required=True)
 q.add_argument('--prepare',action='store_true');q.add_argument('--hd',action='store_true');q.add_argument('--public-candidates',action='store_true')
 q=sub.add_parser('run');q.add_argument('--root',required=True);q.add_argument('--trust-sha256',required=True);q.add_argument('--launch',action='store_true')
 return p
if __name__=='__main__':
 try:
  a=parser().parse_args();result=prepare(a) if a.command=='prepare' else run(a);print(json.dumps(result,indent=2))
  if result.get('status')=='START_OR_WAIT_FAILED' or result.get('exit_code',0):sys.exit(2)
 except (OSError,ValueError,KeyError,TypeError) as exc:print('windows-classic-runtime: '+str(exc),file=sys.stderr);sys.exit(2)
