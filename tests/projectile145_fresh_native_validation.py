#!/usr/bin/env python3
"""Four complete fresh production builds and unchanged107-case145/91 lifecycle oracle.

All86 project TUs instrumented in ASan/UBSan HD-on mode; external SDL/system
libraries remain native and LSan is disabled. No game loop or full gate claim.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,resource,shutil,signal,struct,subprocess,time
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inv(p):return {q.relative_to(p).as_posix():SHA(q) for q in sorted(p.rglob('*')) if q.is_file() and '__pycache__' not in q.parts}
def blocks(p):return sum(q.lstat().st_blocks*512 for q in p.rglob('*'))
MODES={'default-off':'','hd-on':'-DNEWSHF_HD_COMPOSITOR=1','mirror-disabled':'-DNEWSHF_HD_COMPOSITOR=1 -DRENDER_MIRROR_DISABLED','hd-on-asan-ubsan':'-DNEWSHF_HD_COMPOSITOR=1'}
SAN=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie']
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('root','prior-native','data','sysroot','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.root;q=a.out;peak=256*1024**2;reserve=250*1024**2
 assert not q.exists() and shutil.disk_usage(q.parent).free>=peak+reserve
 tagged=subprocess.check_output(['git','--no-optional-locks','-C',str(r),'ls-files','-t','-z']);assert not any(x.startswith(b'S ') for x in tagged.split(b'\0')),'Must use completely hydrated source'
 for name in subprocess.check_output(['git','--no-optional-locks','-C',str(r),'ls-files','-z']).decode().split('\0'):
  if name:assert (r/name).is_file() and not (r/name).is_symlink()
 source=inv(r/'src');prior=json.loads((a.prior_native/'receipt.json').read_text());assert prior['status']=='PASS' and prior['source_sha256']==source
 assert len(source)==308;units=sorted(p.stem for p in (r/'src').glob('*.c'));assert len(units)==86
 producers={str(Path(__file__)):SHA(Path(__file__)),str(a.prior_native/'receipt.json'):SHA(a.prior_native/'receipt.json')}
 for name in ('tests/projectile145_native_additions.c.inc','tests/test_projectile91_global_runtime.py','Makefile'):
  producers[str(r/name)]=SHA(r/name)
 oldtest=r/'tests/test_projectile91_global_runtime.py';tree=ast.parse(oldtest.read_text());node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HARNESS' for t in x.targets));old=ast.literal_eval(node.value)
 assert hashlib.sha256(old.encode()).hexdigest()=='4edcb186f10a47b8d331b6ecaefe15f12c620d7967145f5f9cdbf93c0e76ce89'
 marker='int main(int argc,char **argv)\n{';assert old.count(marker)==1;harness=old.split(marker)[0]+(r/'tests/projectile145_native_additions.c.inc').read_text()
 assert hashlib.sha256(harness.encode()).hexdigest()==prior['generated_harness_sha256'],'Do not relax or replace previous107 oracles'
 scripts=inv(r/'scripts');assets={}
 for group in ('projectile91','projectile145'):
  for f in (r/'assets/hd/current-compat'/group).glob('*'):assets[str(f)]=SHA(f)
 for f in (r/'assets/hd/global-assets-v1/content').glob('*'):
  if f.is_file():assets[str(f)]=SHA(f)
 headers=[]
 for name in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h'):
  f=r/'assets/hd/shared-menu-runs-v1'/name;assets[str(f)]=SHA(f);headers.append(f)
 data={str(a.data/n):SHA(a.data/n) for n in ('tyrian.shp','palette.dat')}
 index=Path(subprocess.check_output(['git','--no-optional-locks','-C',str(r),'rev-parse','--path-format=absolute','--git-path','index'],text=True).strip());index_sha=SHA(index)
 q.mkdir();(q/'tmp').mkdir();(q/'harness.c').write_text(harness)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1','TMPDIR':str(q/'tmp')}
 for k in tuple(env):
  if k.startswith(('AIRCRAFT170_','SHARED170_','TYRIAN_GAME_PROBE','TYRIAN_CYAN_BORROW','PROJECTILE145_','OT_')):env.pop(k)
 report={'status':'RUNNING','scope':__doc__,'source_sha256':source,'producer_sha256':producers,'scripts_sha256':scripts,'asset_sha256':assets,'original_data_sha256':data,'index_sha256':index_sha,'commands':[],'modes':{},'peak_budget_bytes':peak,'reserve_bytes':reserve,'sample_interval_seconds':.25,'peak_allocated_sample':0,'minimum_free_sample':shutil.disk_usage(q).free,'free_before':shutil.disk_usage(q).free,'original_stdin_persisted':False,'all_builds_fresh':True,'reused_project_objects':0,'sanitizer_scope':'All86 project production TUs in hd-on-asan-ubsan plus full renderer/harness and renamed main; external SDL/system libraries native; leak sanitizer disabled.'}
 def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 def measure():
  free=shutil.disk_usage(q).free;used=blocks(q);report['peak_allocated_sample']=max(used,report['peak_allocated_sample']);report['minimum_free_sample']=min(free,report['minimum_free_sample']);assert free>=reserve and used<=peak,('budget',free,used)
 def run(cmd,label,cwd,payload=None):
  row={'argv':list(map(str,cmd)),'label':label,'cwd':str(cwd)};report['commands'].append(row);save()
  with (q/(label+'.stdout')).open('wb') as out,(q/(label+'.stderr')).open('wb') as err:
   z=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,preexec_fn=no_core);row['pid']=z.pid;save();start=time.monotonic()
   if payload is not None:z.stdin.write(payload);z.stdin.close()
   try:
    while z.poll() is None:measure();assert time.monotonic()-start<900,'timeout';time.sleep(.25)
   except BaseException:
    if z.poll() is None:os.killpg(z.pid,signal.SIGTERM);z.wait()
    row['stopped']=True;raise
   finally:row.update(returncode=z.poll(),seconds=time.monotonic()-start);save()
   assert row['returncode']==0,(label,row['returncode'])
 save();start=time.monotonic()
 try:
  for mode,macro in MODES.items():
   build=q/(mode+'-build');build.mkdir();shutil.copytree(r/'src',build/'src');shutil.copyfile(r/'Makefile',build/'Makefile')
   for f in headers:d=build/f.relative_to(r);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
   cpp='-MMD -DNDEBUG '+macro+' -I'+str(a.sysroot/'usr/include/x86_64-linux-gnu');ld='-Wl,-rpath,'+str(a.sysroot/'usr/lib/x86_64-linux-gnu')
   cmd=['make','-j2','VCS_IDREV=printf projectile145-fresh-native','CPPFLAGS='+cpp,'LDFLAGS='+ld]
   if mode=='hd-on-asan-ubsan':cmd[-1]+=' -fsanitize=address,undefined -no-pie';cmd+=['CFLAGS=-O1 -g '+' '.join(SAN)]
   run(cmd,mode+'-build',build)
   objects={f.name:SHA(f) for f in (build/'obj').glob('*.o')};assert set(objects)=={n+'.o' for n in units}
   assert inv(build/'src')==source
   if mode=='hd-on-asan-ubsan':
    compilelog=(q/(mode+'-build.stdout')).read_text();assert compilelog.count(' -c -o obj/')==86
    lines=[x for x in compilelog.splitlines() if ' -c -o obj/' in x];assert len(lines)==86 and all('-fsanitize=address,undefined' in x for x in lines)
   report['modes'][mode]={'binary_sha256':SHA(build/'opentyrian2000'),'objects_sha256':objects,'source_sha256':inv(build/'src'),'fresh_object_count':len(objects),'all_project_tus_sanitized':mode=='hd-on-asan-ubsan'};measure();save()
  build=q/'hd-on-asan-ubsan-build';cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
  flags=['-std=c99','-O1','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(build/'src'),*SAN,'-no-pie']
  renamed=build/'opentyr-test.o';run(['cc',*flags,'-Dmain=unused_game_main','-c',build/'src/opentyr.c','-o',renamed],'renamed-main',build)
  objects=[f for f in sorted((build/'obj').glob('*.o')) if f.stem not in ('render_mirror','opentyr')];assert len(objects)==84
  exe=q/'projectile145-fresh-test';run(['cc',*flags,q/'harness.c',renamed,*objects,*libs,'-lm','-o',exe],'full-sanitized-harness',q)
  packs=[]
  for name,missing,bad in [('valid',None,None),('missing91',91,None),('missing145',145,None),('bad145',None,145),('bad91',None,91)]:
   pack=q/name;pack.mkdir();(pack/'content').symlink_to(r/'assets/hd/global-assets-v1/content',target_is_directory=True)
   for sel in (91,145):
    if sel==missing:continue
    f=r/'assets/hd/current-compat'/('projectile'+str(sel))/('enemy-projectile'+str(sel)+'-'+str(sel)+'-8.hda');raw=bytearray(f.read_bytes())
    if sel==bad:raw[128]^=1
    (pack/f.name).write_bytes(raw)
   packs.append(pack)
  raw=(a.data/'tyrian.shp').read_bytes();offs=struct.unpack_from('<13I',raw,2);bank=raw[offs[7]:offs[8]];assert hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
  pal=(a.data/'palette.dat').read_bytes()[:768];rgb=bytes((v<<2)|(v>>4) for v in pal);talon=raw[offs[8]:offs[9]];payload=bank+b''.join(struct.pack('<I',int.from_bytes(rgb[i:i+3],'big')) for i in range(0,768,3))+struct.pack('<I',len(talon))+talon
  report['stdin_sha256']=hashlib.sha256(payload).hexdigest();assert report['stdin_sha256']==prior['stdin_sha256']
  run([exe,*packs],'native107',q,payload)
  stdout=(q/'native107.stdout').read_text();assert stdout==prior['stdout'],'Unchanged107-case oracle output must match'
  report.update(status='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED107',native_stdout=stdout,binary_sha256=SHA(exe),generated_harness_sha256=SHA(q/'harness.c'))
 except BaseException as e:report.update(status='FAIL_RETAINED',error=repr(e));raise
 finally:
  checks={'source_unchanged':inv(r/'src')==source,'scripts_unchanged':inv(r/'scripts')==scripts,'all_inputs_unchanged':all(SHA(Path(n))==h for n,h in {**producers,**assets,**data}.items()),'index_unchanged':SHA(index)==index_sha,'build_source_copies_unchanged':all(inv(q/(mode+'-build/src'))==source for mode in report['modes'])}
  report.update(checks=checks,seconds=time.monotonic()-start,final_allocated_bytes=blocks(q),free_after=shutil.disk_usage(q).free)
  report['status_before_final_checks']=report['status']
  checks['final_budget_with_receipt_margin']=(report['final_allocated_bytes']+4096<=peak and report['free_after']>=reserve+4096)
  if not checks['final_budget_with_receipt_margin']:report['status']='FAIL_BUDGET_RETAINED'
  elif not all(checks.values()):report['status']='FAIL_BINDING_RETAINED'
  save()
  # Verify actual allocation after the final receipt write as well as sampling.
  if blocks(q)>peak or shutil.disk_usage(q).free<reserve:
   report['status']='FAIL_BUDGET_AFTER_RECEIPT';save();raise AssertionError('Final receipt exceeded reserved budget; retained failure')
  print(json.dumps({k:report.get(k) for k in ('status','native_stdout','checks','peak_allocated_sample','minimum_free_sample','final_allocated_bytes','free_after','error')},indent=2))
 assert report['status']=='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED107'
if __name__=='__main__':main()
