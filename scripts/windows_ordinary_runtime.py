#!/usr/bin/env python3
"""New isolated ordinary HD first play, not the experimental family overlay."""
import argparse,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import windows_classic_runtime as core
HERE=Path(__file__).absolute().parent
EXE='opentyrian2000-ordinary.exe'
MANIFEST_SHA='4db5778fd0f8372469f01b121abc23ee25f501dcbdfffadb1fb78143f8004236'
VALIDATION_SHA='5f9925c665d37a7b6c185c3737190d953bb11099378316bd92e5966d2f8cf457'
TOOLS=('windows_ordinary_runtime.py','windows_classic_runtime.py','runtime-assets-v1.json')
CONFIG=b"section 'video'\n    item 'fullscreen' '-1'\n    item 'scaler' '4x'\n    item 'scaling_mode' 'Integer'\n"
ASSET_ARGUMENTS={'manual-hd-assets':'assets/gameplay','startup-assets':'assets/startup','common-menu-assets':'assets/startup','global-assets':'assets/global','hud-assets':'assets/shared-ui','data-text-assets':'assets/data-text-zh-CN-v1','data-frame-assets':'assets/data-frame-v1','data-portrait-assets':'assets/data-portrait-v1'}

def resources():
 _,raw=core.read_trusted(HERE/'runtime-assets-v1.json',MANIFEST_SHA)
 document=core.json_bytes(raw)
 if document.get('schema')!='opentyrian-runtime-package-v1':raise ValueError('Wrong runtime resource schema')
 result={}
 for item in document['files']:
  name=item['destination'];path=core.PurePosixPath(name)
  if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name or name.casefold() in {x.casefold() for x in result}:raise ValueError('Unsafe/duplicate resource destination')
  result[name]={'bytes':item['bytes'],'sha256':core.valid_digest(item['sha256'])}
 if len(result)!=1163 or sum(x['bytes'] for x in result.values())!=166516707:raise ValueError('Incomplete ordinary production package')
 return result

def exact_files():
 return (core.ALLOWED_FILES-{'bin/opentyrian2000-level2.exe'})|{'bin/'+EXE}|{'tools/'+x for x in TOOLS}|set(resources())|{'opentyrian.cfg'}

def prepare(args):
 if not args.hd:raise ValueError('Explicit --hd required for ordinary HD')
 if args.public_candidates:raise ValueError('Family candidates cannot be combined with ordinary HD')
 plain=argparse.Namespace(**vars(args));plain.hd=False
 output,receipt,inputs,sources=core.prepare_plan(plain,stage_units=86,stage_flavor='ordinary-production',exe_name=EXE)
 stage=core.json_bytes(inputs['trust/STAGE.json'])
 validate_build(core.json_bytes(inputs['trust/BUILD-WINDOWS.json']))
 if stage.get('production_validation_sha256')!=VALIDATION_SHA:raise ValueError('Different canonical production source binding')
 package=core.safe_path(args.assets)
 if not package.is_dir() or output==package or package in output.parents or output in package.parents:raise ValueError('Runroot must be outside resource package')
 for name,item in resources().items():
  path,raw=core.read_trusted(package/name,item['sha256'])
  if len(raw)!=item['bytes']:raise ValueError('Wrong resource size: '+name)
  inputs[name]=raw;sources[name]=path
 for name in TOOLS:
  path=core.safe_path(HERE/name);inputs['tools/'+name]=path.read_bytes();sources['tools/'+name]=path
 # Our initial config is generated, not copied from an old profile. For use by the
 # shared ADS-preserving materializer it is supplied as an exact bundled template.
 path,raw=core.read_trusted(HERE/'ordinary-initial.cfg',core.sha(CONFIG))
 inputs['opentyrian.cfg']=raw;sources['opentyrian.cfg']=path
 receipt.update(mode='ordinary-hd',observer_required=True,production_validation_sha256=VALIDATION_SHA,
  files={name:{'bytes':len(raw),'sha256':core.sha(raw)} for name,raw in sorted(inputs.items())},
  launcher_sha256=core.sha(inputs[core.SCRIPT]),menu_assets='Complete pinned ordinary startup/menu/gameplay/global/HUD/Data UI package',
  environment={},extra_arguments=arguments(output))
 if set(inputs)!=exact_files():raise ValueError('Unexpected ordinary immutable set')
 return core.materialize(args,output,receipt,inputs,sources)

def validate_build(build):
 if build.get('build_flavor')!='ordinary-production' or build.get('translation_units')!=86 or build.get('production_validation_sha256')!=VALIDATION_SHA:raise ValueError('Not an ordinary86 production build receipt')

def arguments(root):return ['--'+key+'='+str(root/value) for key,value in ASSET_ARGUMENTS.items()]

def verify(args):
 if not args.hd:raise ValueError('Explicit --hd required')
 root,receipt,data=core.verify_run(args.root,args.trust_sha256,mode='ordinary-hd',allowed_files=exact_files(),script_path=HERE/'windows_classic_runtime.py',exe_name=EXE)
 if receipt.get('observer_required') is not True or receipt.get('production_validation_sha256')!=VALIDATION_SHA:raise ValueError('Wrong ordinary runtime policy')
 for name in TOOLS:
  if core.sha(core.safe_path(HERE/name).read_bytes())!=receipt['files']['tools/'+name]['sha256']:raise ValueError('Active tool changed: '+name)
 for name,item in resources().items():
  if receipt['files'][name]!=item:raise ValueError('Resource no longer matches production pin')
 stage=core.json_bytes((root/'trust/STAGE.json').read_bytes())
 validate_build(core.json_bytes((root/'trust/BUILD-WINDOWS.json').read_bytes()))
 if stage.get('translation_units')!=86 or stage.get('build_flavor')!='ordinary-production' or stage.get('production_validation_sha256')!=VALIDATION_SHA:raise ValueError('Not an ordinary86 production build')
 if receipt.get('environment')!={} or receipt.get('extra_arguments')!=arguments(root):raise ValueError('Changed ordinary CLI/profile binding')
 if (root/'opentyrian.cfg').read_bytes()!=CONFIG:raise ValueError('Unexpected initial config')
 return root,receipt,data

def run(args):
 root,receipt,data=verify(args)
 if args.launch and not args.observer_present:raise ValueError('A person must be present to observe first play')
 return core.run_verified(args,root,receipt,data,exe_name=EXE,extra_arguments=arguments(root))

def parser():
 p=core.parser();commands=next(x for x in p._actions if isinstance(x,argparse._SubParsersAction)).choices
 commands['prepare'].add_argument('--assets',required=True,help='Exact destination-layout resource package root')
 commands['run'].add_argument('--hd',action='store_true');commands['run'].add_argument('--observer-present',action='store_true')
 return p
if __name__=='__main__':
 try:
  a=parser().parse_args();result=prepare(a) if a.command=='prepare' else run(a);print(json.dumps(result,indent=2))
  if result.get('status')=='START_OR_WAIT_FAILED' or result.get('exit_code',0):sys.exit(2)
 except (OSError,ValueError,KeyError,TypeError) as exc:print('windows-ordinary-runtime: '+str(exc),file=sys.stderr);sys.exit(2)
