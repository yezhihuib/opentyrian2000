#!/usr/bin/env python3
"""Bounded61 real-production-TU probe, not a fresh61 game build.

The exact inherited107 harness/stdin/stdout is preserved in its own process mode.
82 unchanged ASan/UBSan objects are read-only reused from the retained145 fresh
build; three successful v1 TUs are reused by exact object/source/dependency pins.
Only renderer/harness compiles anew; the failed v1 partial ELF is never reused.
All86 consumed project TUs are instrumented; SDL/system libraries are native.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,resource,shlex,shutil,signal,struct,subprocess,time,threading
PEAK=128*1024**2;FINAL_CAP=64*1024**2;RESERVE=250*1024**2;EXPECTED_NEW_CASES=157
FRESH_SHA='86975d21f38d876c6b7f5c610c67ef051898aefb9c6d998cf6394c89318d691a'
DISPOSITION_SHA='bd037a3f7992c1d3aec69a1ecc8844f0eb4967eb32425b60739a579c51761847'
ARCHIVE_INDEX_SHA='5341714848412f7fbd7ff3d76d078cccdc767c46f2363da3d5f02788aa27bdaf'
LEGACY_SHA='8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac'
CHANGED={'render_mirror.c','global_projectile91_mirror.inc','entity_draw.c','tyrian2.c'}
ADDED={'enemy_projectile61_mirror.inc','current_projectile61_payload_pins.h'}
REBUILD={'render_mirror','opentyr','entity_draw','tyrian2'}
REUSE_RECEIPT_SHA='b4f3c9f2bcfea9a416c1dd628b335bb0d52aa4e31d2a70e28bba76d7191d826e'
REUSE_DIAGNOSIS_SHA='1dfad17e66b48dc69fae8cf75536d63b01654767c5e437c8d0674fa1bbd5d05f'
REUSE_DRIVER_SHA='cbb5a63645877fd2c52458c20b560e6998df32bf450bbaac4ccf884207fc9e73'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inv(root):return {p.relative_to(root).as_posix():SHA(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
def allocated(root):return sum(p.lstat().st_blocks*512 for p in root.rglob('*'))
def dependency_tokens(text):
 text=text.replace('\\\n',' ');assert ':' in text
 return shlex.split(text.split(':',1)[1])
def budget_ok(used,free,final=False):return used<= (FINAL_CAP if final else PEAK) and free>=RESERVE
def parse_native61_stdout(stdout):
 summary=re.findall(r'^PASS shared61 native lifecycle: (\d+) cases (\d+) assertions; internal8 only; not gameplay/full build$',stdout,re.M)
 assert len(summary)==1 and int(summary[0][0])==EXPECTED_NEW_CASES and int(summary[0][1])>0
 copied=re.findall(r'^61_TO_TALON copied=(\d+) cached=([01])$',stdout,re.M)
 assert len(copied)==2 and {k for _,k in copied}=={'0','1'} and all(int(n)>0 for n,_ in copied)
 return tuple(map(int,summary[0]))
def sanitized_env(parent,sysroot,tmp):
 env=dict(parent)
 for key in tuple(env):
  if key.startswith(('AIRCRAFT','SHARED','PROJECTILE','TYRIAN_GAME_PROBE','TYRIAN_CYAN_BORROW','OT_')):env.pop(key)
 env.update(PKG_CONFIG_SYSROOT_DIR=str(sysroot),PKG_CONFIG_LIBDIR=str(sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),LD_LIBRARY_PATH=str(sysroot/'usr/lib/x86_64-linux-gnu'),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TMPDIR=str(tmp))
 return env
WRAPPER='''#define main inherited145_main
#include "inherited145_harness.c"
#undef main
#include "projectile61_native_additions.c.inc"
int main(int argc,char **argv)
{
 if(argc==7&&!strcmp(argv[1],"--inherited107"))return inherited145_main(argc-1,argv+1);
 CHECK(argc==10&&!strcmp(argv[1],"--projectile61"));
 valid_root=argv[2];missing_root=argv[3];
 read_exact(original,sizeof(original));read_exact(palette0,sizeof(palette0));
 Uint32 n;read_exact(&n,4);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 Uint32 xn;read_exact(&xn,4);CHECK(xn==32404);Uint8 *xb=malloc(xn);CHECK(xb);read_exact(xb,xn);CHECK(fgetc(stdin)==EOF);
 projectile61_cases(argv[4],argv[5],argv[6],argv[7],argv[8],argv[9],xb,xn);
 free(xb);return 0;
}
'''
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for key in ('source-root','baseline','fresh-proof','fresh-disposition','archive-index','data','sysroot','reuse-proof','reuse-diagnosis','reuse-producer','out'):parser.add_argument('--'+key,type=Path,required=True)
 a=parser.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.source_root;q=a.out
 assert not q.exists() and shutil.disk_usage(q.parent).free>=RESERVE+PEAK
 assert SHA(a.fresh_proof/'receipt.json')==FRESH_SHA and SHA(a.fresh_disposition)==DISPOSITION_SHA and SHA(a.archive_index)==ARCHIVE_INDEX_SHA
 fresh=json.loads((a.fresh_proof/'receipt.json').read_text());disposition=json.loads(a.fresh_disposition.read_text());archive=json.loads(a.archive_index.read_text())
 assert fresh['status']=='FAIL_BINDING_RETAINED' and fresh['status_before_final_checks']=='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED107'
 assert disposition['status']=='ACCEPTED_FUNCTIONAL_RESULTS_WITH_RAW_INDEX_STAT_CACHE_DEVIATION' and disposition['original_receipt_sha256']==FRESH_SHA
 source=inv(r/'src');old=fresh['source_sha256'];assert len(source)==310 and len(old)==308
 assert {n for n in old if source.get(n)!=old[n]}==CHANGED and set(source)-set(old)==ADDED
 build=a.fresh_proof/'hd-on-asan-ubsan-build';assert inv(build/'src')==old
 frozen_objects=fresh['modes']['hd-on-asan-ubsan']['objects_sha256'];assert len(frozen_objects)==86
 objects=[build/'obj'/n for n in sorted(frozen_objects) if Path(n).stem not in REBUILD];assert len(objects)==82
 bound={build/'obj'/n:h for n,h in frozen_objects.items()};assert all(SHA(p)==h for p,h in bound.items())
 project_dependencies={};system_dependencies={};dep_pins={}
 for obj in objects:
  dep=obj.with_suffix('.d');key=dep.relative_to(a.fresh_proof.parent.parent).as_posix();pin=archive['files'][key];assert SHA(dep)==pin['sha256'];dep_pins[str(dep)]=SHA(dep)
  for token in dependency_tokens(dep.read_text()):
   depfile=(build/token).resolve() if not Path(token).is_absolute() else Path(token)
   if token.startswith('src/') and not token.startswith('src/../'):
    name=token[4:];assert name not in CHANGED|ADDED and old[name]==source[name];assert SHA(depfile)==old[name];project_dependencies[str(depfile)]=SHA(depfile);project_dependencies[str(r/'src'/name)]=source[name]
   elif token.startswith('src/../assets/'):
    rel=Path(token).parts[2:];current=a.baseline.joinpath(*rel);assert SHA(depfile)==SHA(current);project_dependencies[str(depfile)]=SHA(depfile);project_dependencies[str(current)]=SHA(current)
   else:
    assert depfile.is_relative_to(a.sysroot),token;system_dependencies[str(depfile)]=SHA(depfile)
 legacy=a.fresh_proof/'harness.c';assert SHA(legacy)==LEGACY_SHA and LEGACY_SHA==fresh['generated_harness_sha256']
 driver=Path(__file__).resolve();companion=driver.with_name('projectile61_native_additions.c.inc');assert companion.is_file()
 producers={str(p):SHA(p) for p in (driver,companion,driver.with_name('test_projectile61_native_adapter.py'),legacy,a.fresh_proof/'receipt.json',a.fresh_disposition,a.archive_index,r/'tests/projectile145_native_additions.c.inc',r/'tests/test_projectile91_global_runtime.py')}
 scripts=inv(r/'scripts');assets={}
 # Pin current sysroot headers before compilation, then intersect actual fresh .d closures.
 current_headers={str(p.resolve()):SHA(p) for p in (a.sysroot/'usr/include').rglob('*') if p.is_file()}
 content=a.baseline/'assets/hd/global-assets-v1/content'
 for p in content.rglob('*'):
  if p.is_file():assets[str(p)]=SHA(p)
 hdas={i:r/f'assets/hd/current-compat/projectile{i}/enemy-projectile{i}-{i}-8.hda' for i in (91,145,61)}
 assets.update({str(p):SHA(p) for p in hdas.values()})
 headers=[a.baseline/'assets/hd/shared-menu-runs-v1'/n for n in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')]
 for p in headers:assert SHA(p)==SHA(build/p.relative_to(a.baseline));assets[str(p)]=SHA(p)
 data={str(a.data/n):SHA(a.data/n) for n in ('tyrian.shp','tyrianc.shp','palette.dat')}
 assert data[str(a.data/'tyrian.shp')]=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'
 assert data[str(a.data/'tyrianc.shp')]=='e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d'
 assert data[str(a.data/'palette.dat')]=='f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'
 assert SHA(a.reuse_proof/'receipt.json')==REUSE_RECEIPT_SHA and SHA(a.reuse_diagnosis)==REUSE_DIAGNOSIS_SHA and SHA(a.reuse_producer)==REUSE_DRIVER_SHA
 reuse=json.loads((a.reuse_proof/'receipt.json').read_text());diagnosis=json.loads(a.reuse_diagnosis.read_text())
 assert reuse['status']=='FAIL_RETAINED' and reuse['error'].startswith('AssertionError((102666240, 255295488))')
 assert reuse['source_sha256']==source and inv(a.reuse_proof/'src')==source
 assert reuse['current_sysroot_header_sha256']==current_headers
 assert len(reuse['commands'])==4 and [row['returncode'] for row in reuse['commands']]==[0,0,0,-15]
 assert reuse['commands'][-1]['stopped'] and not (a.reuse_proof/'inherited107.stdout').exists() and not (a.reuse_proof/'native61.stdout').exists()
 reuse_bound={str(a.reuse_proof/'receipt.json'):REUSE_RECEIPT_SHA,str(a.reuse_diagnosis):REUSE_DIAGNOSIS_SHA,str(a.reuse_producer):REUSE_DRIVER_SHA}
 newobjects=[]
 for name in ('entity_draw','tyrian2','opentyr'):
  entry=diagnosis['successful_three_compile_objects'][name];obj=a.reuse_proof/(name+'-sanitized.o');dep=a.reuse_proof/(name+'.d')
  assert str(obj)==entry['path'] and SHA(obj)==entry['sha256'] and SHA(dep)==entry['depfile_sha256']
  actual={}
  for token in dependency_tokens(dep.read_text()):
   dp=(a.reuse_proof/token).resolve() if not Path(token).is_absolute() else Path(token).resolve();h=SHA(dp);actual[str(dp)]=h
   if dp.is_relative_to(a.reuse_proof/'src'):assert h==source[dp.relative_to(a.reuse_proof/'src').as_posix()]
   else:assert dp.is_relative_to(a.sysroot) and current_headers[str(dp)]==h
  assert actual==entry['dependency_sha256'];reuse_bound.update(actual);reuse_bound[str(obj)]=entry['sha256'];reuse_bound[str(dep)]=entry['depfile_sha256'];newobjects.append(obj)
 git=lambda *args:subprocess.check_output(['git','--no-optional-locks','-C',str(r),*args],env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
 index=Path(git('rev-parse','--path-format=absolute','--git-path','index').decode().strip());index_sha=SHA(index);semantic=hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()
 q.mkdir();(q/'tmp').mkdir();shutil.copytree(r/'src',q/'src')
 for p in headers:dest=q/p.relative_to(a.baseline);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 (q/'inherited145_harness.c').write_bytes(legacy.read_bytes());(q/'projectile61_native_additions.c.inc').write_bytes(companion.read_bytes());(q/'harness.c').write_text(WRAPPER)
 packs=[]
 for name,missing,bad in [('valid',set(),None),('missing91',{91},None),('missing145',{145},None),('bad145',set(),145),('bad91',set(),91),('missing61',{61},None),('bad61',set(),61),('only61',{91,145},None)]:
  pack=q/name;pack.mkdir();(pack/'content').symlink_to(content,target_is_directory=True)
  for selector,p in hdas.items():
   if selector not in missing:
    b=bytearray(p.read_bytes())
    if selector==bad:b[128]^=1
    (pack/p.name).write_bytes(b)
  packs.append(pack)
 env=sanitized_env(os.environ,a.sysroot,q/'tmp');cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 flags=['-std=c99','-O1','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(q/'src'),'-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
 report={'status':'RUNNING','scope':__doc__,'source_sha256':source,'old_source_sha256':old,'scripts_sha256':scripts,'producer_sha256':producers,'all86_baseline_object_sha256':{str(p):h for p,h in bound.items()},'reused82_objects':[str(p) for p in objects],'archived_dependency_file_sha256':dep_pins,'project_dependency_sha256':project_dependencies,'current_system_dependency_sha256':system_dependencies,'system_dependency_scope':'Current system header bytes pinned before/after; baseline archive proves old .d names and object bytes, not a historical standalone system-header snapshot.','assets_sha256':assets,'data_sha256':data,'original_index_sha256':index_sha,'semantic_index_sha256':semantic,'original107_harness_sha256':LEGACY_SHA,'original145_wrapper_status_retained':'FAIL_BINDING_RETAINED with separately accepted exact stat-only deviation','original_game_bytes_persisted':False,'reused_three_v1_objects':{str(p):SHA(p) for p in newobjects},'reuse_v1_dependency_sha256':reuse_bound,'v1_original_status_retained':'FAIL_RETAINED budget stop before any native run; partial ELF excluded','fresh_dependency_sha256':{},'fresh_dependency_files_sha256':{},'current_sysroot_header_sha256':current_headers,'commands':[],'peak_budget_bytes':PEAK,'final_cap_bytes':FINAL_CAP,'reserve_bytes':RESERVE,'minimum_free_bytes':shutil.disk_usage(q).free,'peak_allocated_bytes':allocated(q),'sample_interval_seconds':.25,'sanitizer_scope':'82 reused full145-fresh ASan+UBSan project objects +3 exact successful v1 ASan/UBSan TUs (entity_draw,tyrian2,renamed main) +1 newly compiled renderer/harness;86 project TUs instrumented, external SDL/system native,LSan disabled. Not a fresh61 whole-game build.'}
 def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def measure():
  used=allocated(q);free=shutil.disk_usage(q).free
  if used>report['peak_allocated_bytes']:
   report['peak_allocated_bytes']=used
   samples=[]
   for path in q.rglob('*'):
    try:stat=path.lstat()
    except FileNotFoundError:continue
    samples.append({'path':path.relative_to(q).as_posix(),'bytes':stat.st_size,'allocated':stat.st_blocks*512})
   report['peak_largest_paths_nonatomic_sample']=sorted(samples,key=lambda row:row['allocated'],reverse=True)[:16]
  report['minimum_free_bytes']=min(report['minimum_free_bytes'],free);assert budget_ok(used,free),(used,free)
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 def run(cmd,label,payload=None):
  row={'argv':list(map(str,cmd)),'label':label};report['commands'].append(row);save()
  with (q/(label+'.stdout')).open('wb') as out,(q/(label+'.stderr')).open('wb') as err:
   proc=subprocess.Popen(row['argv'],cwd=q,env=env,stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,preexec_fn=no_core);row['pid']=proc.pid;save();start=time.monotonic()
   writer_errors=[]
   def feed():
    try:proc.stdin.write(payload);proc.stdin.close()
    except BaseException as error:writer_errors.append(repr(error))
   feeder=threading.Thread(target=feed,daemon=True) if payload is not None else None
   try:
    if feeder:feeder.start()
    while proc.poll() is None:measure();assert time.monotonic()-start<900,'Timeout';time.sleep(.25)
   except BaseException:
    if proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM);proc.wait()
    row['stopped']=True;raise
   finally:
    if feeder:feeder.join(timeout=2)
    row.update(returncode=proc.poll(),seconds=time.monotonic()-start,stdin_writer_errors=writer_errors);save()
   assert not writer_errors and (feeder is None or not feeder.is_alive()),'stdin transfer'
   assert row['returncode']==0,label
   assert not (q/(label+'.stderr')).read_bytes(),label+' emitted stderr'
  measure()
 start=time.monotonic();save()
 try:
  for name in ('entity_draw','tyrian2','opentyr'):
   obj=q/(name+'-sanitized.o');extra=['-Dmain=unused_game_main'] if name=='opentyr' else []
   expected=list(map(str,['cc',*flags,*extra,'-MMD','-MF',q/(name+'.d'),'-c',q/'src'/f'{name}.c','-o',obj]))
   prior=next(row for row in reuse['commands'] if row['label']==name+'-compile')
   assert [arg.replace(str(a.reuse_proof),str(q)) for arg in prior['argv']]==expected
  exe=q/'projectile61-test';run(['cc',*flags,'-MMD','-MF',q/'renderer-harness.d',q/'harness.c',*objects,*newobjects,*libs,'-lm','-o',exe],'renderer-link')
  for dep in sorted(q.glob('*.d')):
   report['fresh_dependency_files_sha256'][str(dep)]=SHA(dep)
   for token in dependency_tokens(dep.read_text()):
    dp=(q/token).resolve() if not Path(token).is_absolute() else Path(token).resolve()
    h=SHA(dp)
    if dp.is_relative_to(q/'src'):assert h==source[dp.relative_to(q/'src').as_posix()]
    elif dp.is_relative_to(q/'assets'):assert h==assets[str(a.baseline/dp.relative_to(q))]
    elif dp.is_relative_to(a.sysroot):assert current_headers[str(dp)]==h
    else:assert dp in (q/'harness.c',q/'inherited145_harness.c',q/'projectile61_native_additions.c.inc')
    report['fresh_dependency_sha256'][str(dp)]=h
  assert len(report['fresh_dependency_files_sha256'])==1
  raw=(a.data/'tyrian.shp').read_bytes();offsets=struct.unpack_from('<13I',raw,2);bank=raw[offsets[7]:offsets[8]];talon=raw[offsets[8]:offsets[9]];assert hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
  pal=(a.data/'palette.dat').read_bytes()[:768];rgb=bytes((v<<2)|(v>>4) for v in pal);old_stdin=bank+b''.join(struct.pack('<I',int.from_bytes(rgb[i:i+3],'big')) for i in range(0,768,3))+struct.pack('<I',len(talon))+talon;assert hashlib.sha256(old_stdin).hexdigest()==fresh['stdin_sha256']
  raw=(a.data/'tyrianc.shp').read_bytes();offsets=struct.unpack_from('<13I',raw,2);xmas=raw[offsets[7]:offsets[8]];assert len(xmas)==32404 and hashlib.sha256(xmas).hexdigest()=='26eb4fe91672bcef4bc88d7162d5f531144ad98eba64f5c0314e35fec85241e4'
  new_stdin=old_stdin+struct.pack('<I',len(xmas))+xmas;report['old107_stdin_sha256']=hashlib.sha256(old_stdin).hexdigest();report['new61_stdin_sha256']=hashlib.sha256(new_stdin).hexdigest()
  run([exe,'--inherited107',*packs[:5]],'inherited107',old_stdin);assert (q/'inherited107.stdout').read_text()==fresh['native_stdout']
  run([exe,'--projectile61',*packs],'native61',new_stdin)
  stdout=(q/'native61.stdout').read_text();new_cases,new_assertions=parse_native61_stdout(stdout)
  report.update(status='PASS_107_AND_REAL61_PRODUCTION_TU_PROBE',inherited107_stdout=fresh['native_stdout'],new61_stdout=stdout,new61_cases=new_cases,new61_assertions=new_assertions,binary_sha256=SHA(exe),reused_v1_object_sha256_after={str(p):SHA(p) for p in newobjects},generated_wrapper_sha256=SHA(q/'harness.c'))
 except BaseException as error:report.update(status='FAIL_RETAINED',error=repr(error));raise
 finally:
  binding={**reuse_bound,**producers,**assets,**data,**project_dependencies,**system_dependencies,**current_headers,**report['fresh_dependency_sha256'],**report['fresh_dependency_files_sha256'],**dep_pins,**{str(p):h for p,h in bound.items()}}
  checks={'source_unchanged':inv(r/'src')==source,'scripts_unchanged':inv(r/'scripts')==scripts,'source_copy_exact':inv(q/'src')==source,'all_bound_inputs_unchanged':all(SHA(Path(p))==h for p,h in binding.items()),'index_raw_unchanged':SHA(index)==index_sha,'semantic_index_unchanged':hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()==semantic,'legacy_harness_byte_exact':SHA(q/'inherited145_harness.c')==LEGACY_SHA,'companion_exact':SHA(q/'projectile61_native_additions.c.inc')==SHA(companion)}
  used=allocated(q);free=shutil.disk_usage(q).free;checks['final_budget_with_receipt_margin']=budget_ok(used+4096,free-4096,True)
  report.update(status_before_final_checks=report['status'],checks=checks,final_allocated_bytes=used,free_after=free,seconds=time.monotonic()-start)
  if not checks['final_budget_with_receipt_margin']:report['status']='FAIL_BUDGET_RETAINED'
  elif not all(checks.values()):report['status']='FAIL_BINDING_RETAINED'
  save()
  if not budget_ok(allocated(q),shutil.disk_usage(q).free,True):report['status']='FAIL_BUDGET_AFTER_RECEIPT';save();raise AssertionError('Final receipt budget')
  print(json.dumps({k:report.get(k) for k in ('status','new61_cases','new61_assertions','checks','peak_allocated_bytes','minimum_free_bytes','final_allocated_bytes','free_after','error')},indent=2))
 assert report['status']=='PASS_107_AND_REAL61_PRODUCTION_TU_PROBE'
if __name__=='__main__':main()
