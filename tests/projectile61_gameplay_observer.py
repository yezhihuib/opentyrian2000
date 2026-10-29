#!/usr/bin/env python3
"""Bounded naturally scheduled enemy61 observation with deterministic probe input.

81 ordinary145-fresh HD-on objects plus five fresh changed/instrumented TUs.
Output-only instrumentation, no actor/weapon/shot/pose injection; not a fresh
full61 game build, sanitizer run, differential comparison, or qualification.
"""
from pathlib import Path
import argparse,csv,hashlib,json,os,re,resource,shlex,shutil,signal,subprocess,sys,time
import projectile61_gameplay_instrumentation as instr
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PEAK=50*1024**2;RESERVE=250*1024**2;LOG_CAP=8*1024**2
FRESH_SHA='86975d21f38d876c6b7f5c610c67ef051898aefb9c6d998cf6394c89318d691a'
DISPOSITION_SHA='bd037a3f7992c1d3aec69a1ecc8844f0eb4967eb32425b60739a579c51761847'
ARCHIVE_SHA='5341714848412f7fbd7ff3d76d078cccdc767c46f2363da3d5f02788aa27bdaf'
PACK_RECEIPT_SHA='dde92d1ea25569c605550456fc5ee74de70dd124c7e537e2e2d2de7147a9d82c'
UNITS=('render_mirror','tyrian2','entity_draw','game_probe','asset_debug')
CHANGED={'render_mirror.c','global_projectile91_mirror.inc','entity_draw.c','tyrian2.c'}
ADDED={'enemy_projectile61_mirror.inc','current_projectile61_payload_pins.h'}
def inv(p):return {f.relative_to(p).as_posix():SHA(f) for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
def allocated(root):
 n=0
 for p in root.rglob('*'):
  try:n+=p.lstat().st_blocks*512
  except FileNotFoundError:pass
 return n
def budget_ok(used,free,logs):return used<=PEAK and free>=RESERVE and logs<=LOG_CAP
def dep_tokens(text):return shlex.split(text.replace('\\\n',' ').split(':',1)[1])
def environment(parent,sysroot,out,tmp):
 env=dict(parent);removed=[]
 for k in tuple(env):
  if k.startswith(('AIRCRAFT','PROJECTILE','SHARED','TYRIAN_CYAN_BORROW','TYRIAN_GAME_PROBE','OT_')):removed.append(k);env.pop(k)
 env.update(PKG_CONFIG_SYSROOT_DIR=str(sysroot),PKG_CONFIG_LIBDIR=str(sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),LD_LIBRARY_PATH=str(sysroot/'usr/lib/x86_64-linux-gnu'),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',HOME=str(out),XDG_CONFIG_HOME=str(out/'config'),TMPDIR=str(tmp))
 return env,removed
def rows(root,name):
 p=root/name
 if not p.exists():return []
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def classify_observation(actual,final,admission):
 emits=[row for row in actual if row['kind']=='emit' and row['weapon'] in ('131','1131') and row['index']=='61']
 draws=[row for row in actual if row['kind']=='draw' and row['index']=='61']
 admitted=[row for row in admission if row['role']=='151' and row['index']=='61' and row['mirrored']=='1']
 visible=[]
 for row in final:
  witness=int(row['opaque_authored_not_classic']);owned=int(row['opaque_owned']);supported=int(row['opaque_visible_supported'])
  flags=('ready','last_valid','cached','resource_valid','metadata_ok','palette12_ok','normal_bank_ok','native_mask_ok','layout_ok')
  if all(row[key]=='1' for key in flags) and row['fault']=='0' and int(row['member_mask'])&4 and row['density']=='8' and row['role']=='151' and row['index']=='61' and int(row['opaque_authored_total'])==246 and int(row['opaque_outside_native_mask'])==0 and 0<witness<=owned<=supported<=246:visible.append(row)
 candidates=[row for row in visible if any(d['tick']==row['tick'] and d['slot']==row['slot'] and d['x']==row['x'] and d['y']==row['y'] for d in draws) and any(e['slot']==row['slot'] and int(e['tick'])<=int(row['tick']) for e in emits) and any(a['tick']==row['tick'] and a['x']==row['x'] and a['y']==row['y'] for a in admitted)]
 return emits,draws,admitted,candidates
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('source-root','baseline','fresh-proof','fresh-disposition','archive-index','base-pack','data','sysroot','out'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.source_root;q=a.out
 assert not q.exists() and shutil.disk_usage(q.parent).free>=PEAK+RESERVE
 assert SHA(a.fresh_proof/'receipt.json')==FRESH_SHA and SHA(a.fresh_disposition)==DISPOSITION_SHA and SHA(a.archive_index)==ARCHIVE_SHA
 f=json.loads((a.fresh_proof/'receipt.json').read_text());accept=json.loads(a.fresh_disposition.read_text());archive=json.loads(a.archive_index.read_text())
 assert f['status']=='FAIL_BINDING_RETAINED' and accept['status']=='ACCEPTED_FUNCTIONAL_RESULTS_WITH_RAW_INDEX_STAT_CACHE_DEVIATION' and accept['original_receipt_sha256']==FRESH_SHA
 old=f['source_sha256'];source=inv(r/'src');assert len(source)==310 and len(old)==308 and inv(a.baseline/'src')==old
 assert {n for n in old if source.get(n)!=old[n]}==CHANGED and set(source)-set(old)==ADDED
 base=a.fresh_proof/'hd-on-build';assert inv(base/'src')==old
 objects={str(base/'obj'/n):h for n,h in f['modes']['hd-on']['objects_sha256'].items()};assert len(objects)==86 and all(SHA(Path(n))==h for n,h in objects.items())
 borrowed=[Path(n) for n in sorted(objects) if Path(n).stem not in UNITS];assert len(borrowed)==81
 deps={};old_depfiles={}
 for obj in borrowed:
  dep=obj.with_suffix('.d');pin=archive['files'][dep.relative_to(a.fresh_proof.parent.parent).as_posix()];assert SHA(dep)==pin['sha256'];old_depfiles[str(dep)]=SHA(dep)
  for token in dep_tokens(dep.read_text()):
   path=(base/token).resolve() if not Path(token).is_absolute() else Path(token).resolve();h=SHA(path)
   if token.startswith('src/') and not token.startswith('src/../'):assert h==old[token[4:]]==source[token[4:]]
   elif token.startswith('src/../assets/'):assert h==SHA(a.baseline/Path(token).relative_to('src/..'))
   else:assert path.is_relative_to(a.sysroot)
   deps[str(path)]=h
 headers=[a.baseline/'assets/hd/shared-menu-runs-v1'/n for n in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')]
 for path in headers:assert SHA(path)==SHA(base/path.relative_to(a.baseline));deps[str(path)]=SHA(path)
 sysheaders={str(path.resolve()):SHA(path) for path in (a.sysroot/'usr/include').rglob('*') if path.is_file()}
 data={str(path):SHA(path) for path in a.data.iterdir() if path.is_file()};scripts=inv(r/'scripts')
 assert data[str(a.data/'tyrian.shp')]=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'
 # The retained145 scene pack is a read-only set of qualified asset targets.
 pack_receipt=a.base_pack.parent/'receipt.json';assert SHA(pack_receipt)==PACK_RECEIPT_SHA;pr=json.loads(pack_receipt.read_text());assert pr['status']=='PASS_BOUNDED_NATURAL_OBSERVATION'
 pack_inputs={str(path.resolve()):SHA(path) for path in a.base_pack.rglob('*') if path.is_file()}
 assert pack_inputs==pr['pack_target_sha256'] and len(pack_inputs)==733
 hda=r/'assets/hd/current-compat/projectile61/enemy-projectile61-61-8.hda';assert SHA(hda)=='3530c27302a2cb3d26830711cd4b94a01aacbfad748c91aea219bbc81b0c5c29'
 pack_inputs[str(hda)]=SHA(hda)
 driver=Path(__file__).resolve();helper=driver.with_name('projectile61_gameplay_instrumentation.py');pure=driver.with_name('test_projectile61_gameplay_instrumentation.py');adapter=driver.with_name('test_projectile61_gameplay_observer.py')
 extractor=r/'tests/global_talon_reconstruction.py';sys.path.insert(0,str(r/'tests'))
 producer={str(path):SHA(path) for path in (driver,helper,pure,adapter,extractor,pack_receipt,a.fresh_proof/'receipt.json',a.fresh_disposition,a.archive_index)}
 texts={n:(r/'src'/n).read_text() for n in ('game_probe.c','asset_debug.c','tyrian2.c','render_mirror.c')};modified=instr.instrument(texts);assert set(modified)==set(texts)
 git=lambda *args:subprocess.check_output(['git','--no-optional-locks','-C',str(r),*args],env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
 index=Path(git('rev-parse','--path-format=absolute','--git-path','index').decode().strip());index_sha=SHA(index);semantic=hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()
 q.mkdir();build=q/'build';shutil.copytree(r/'src',build/'src');(q/'tmp').mkdir()
 for name,text in modified.items():(build/'src'/name).write_text(text)
 for path in headers:dest=build/path.relative_to(a.baseline);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
 pack=q/'pack';pack.mkdir()
 for path in a.base_pack.rglob('*'):
  if path.is_file():dest=pack/path.relative_to(a.base_pack);dest.parent.mkdir(parents=True,exist_ok=True);dest.symlink_to(path.resolve())
 assert not (pack/hda.name).exists();(pack/hda.name).symlink_to(hda)
 out=q/'observation';cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 2x\nitem fullscreen -1\n')
 env,removed=environment(os.environ,a.sysroot,out,q/'tmp')
 cflags=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True));libs=shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True))
 flags=['-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(build/'src')]
 report={'status':'RUNNING','scope':__doc__,'source_sha256':source,'baseline_source_sha256':old,'instrumented_source_sha256':inv(build/'src'),'scripts_sha256':scripts,'producer_sha256':producer,'all86_baseline_objects_sha256':objects,'reused81_objects':[str(x) for x in borrowed],'archived_depfile_sha256':old_depfiles,'dependency_sha256':deps,'current_sysroot_header_sha256':sysheaders,'fresh_dependency_sha256':{},'fresh_depfile_sha256':{},'original_data_sha256':data,'pack_target_sha256':pack_inputs,'source_index_sha256':index_sha,'semantic_index_sha256':semantic,'original145_fresh_wrapper_FAIL_retained':True,'episode':2,'physical_level':9,'source_event_candidate':150,'observed_tick_not_assumed':True,'custom_log_window':[instr.FIRST,instr.LAST],'max_ticks':261,'natural_scheduled_enemies_and_shots':True,'controlled_player_input':'Existing asset-debug deterministic stationary/no-player-fire input; no actor/weapon/shot/pose injection','actual_environment':{k:env[k] for k in ('SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER','HOME','XDG_CONFIG_HOME','LD_LIBRARY_PATH','TMPDIR')},'removed_control_key_names':removed,'commands':[],'peak_cap':PEAK,'reserve':RESERVE,'log_cap':LOG_CAP,'sample_interval_seconds':.25,'peak_allocated':allocated(q),'minimum_free':shutil.disk_usage(q).free}
 def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def measure():
  used=allocated(q);free=shutil.disk_usage(q).free;logs=allocated(out);report['peak_allocated']=max(report['peak_allocated'],used);report['minimum_free']=min(report['minimum_free'],free)
  assert budget_ok(used,free,logs),(used,free,logs)
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 def run(cmd,label,cwd):
  row={'label':label,'argv':list(map(str,cmd)),'cwd':str(cwd)};report['commands'].append(row);save()
  with (q/(label+'.stdout')).open('wb') as stdout,(q/(label+'.stderr')).open('wb') as stderr:
   proc=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=no_core);row['pid']=proc.pid;start=time.monotonic();save()
   try:
    while proc.poll() is None:measure();assert time.monotonic()-start<300,'bounded timeout';time.sleep(.25)
   except BaseException:
    if proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM);proc.wait()
    row['stopped']=True;raise
   finally:row.update(returncode=proc.poll(),seconds=time.monotonic()-start);save()
   assert row['returncode']==0,label
   if label!='natural-observation':assert not (q/(label+'.stderr')).read_bytes(),label+' stderr'
  measure()
 save();start=time.monotonic()
 try:
  fresh=[]
  for unit in UNITS:
   obj=build/(unit+'.o');run(['cc',*flags,'-MMD','-MF',build/(unit+'.d'),'-c',build/'src'/(unit+'.c'),'-o',obj],unit+'-compile',build);fresh.append(obj)
  exe=build/'opentyrian2000';run(['cc',*borrowed,*fresh,*libs,'-lm','-o',exe],'link',build)
  for dep in build.glob('*.d'):
   report['fresh_depfile_sha256'][str(dep)]=SHA(dep)
   for token in dep_tokens(dep.read_text()):
    path=(build/token).resolve() if not Path(token).is_absolute() else Path(token).resolve();h=SHA(path)
    if path.is_relative_to(build/'src'):assert h==report['instrumented_source_sha256'][path.relative_to(build/'src').as_posix()]
    elif path.is_relative_to(build/'assets'):assert h==deps[str(a.baseline/path.relative_to(build))]
    else:assert path.is_relative_to(a.sysroot) and h==sysheaders[str(path)]
    report['fresh_dependency_sha256'][str(path)]=h
  assert len(report['fresh_depfile_sha256'])==5
  command=[exe,'--data='+str(a.data),'--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=2','--asset-debug-level=9','--asset-debug-tick=140','--asset-debug-running','--render-ticks=261','--render-assets='+str(pack),'--global-assets='+str(pack),'--render-no-capture','--render-test=8']
  run(command,'natural-observation',out)
  assert not list(out.rglob('*.bmp')) and not list(out.rglob('*.png'))
  actual=rows(out,'actual61-native.tsv');final=rows(out,'actual61-final.tsv');admission=rows(out,'actual61-admission.tsv')
  emits,draws,admitted,candidates=classify_observation(actual,final,admission)
  report.update(status='PASS_BOUNDED_NATURAL61_OBSERVATION' if emits and candidates else 'NO_CONFIRMED_61_WINDOW',emissions=emits,actual_draw_count=len(draws),actual_admission_count=len(admitted),actual_palette_rows=rows(out,'actual61-palette.tsv'),visible_candidates=candidates,first_visible=candidates[0] if candidates else None,binary_sha256=SHA(exe),fresh_object_sha256={str(x):SHA(x) for x in fresh},no_capture_performed=True)
 except BaseException as error:report.update(status='FAIL_RETAINED',error=repr(error));raise
 finally:
  binding={**objects,**deps,**old_depfiles,**sysheaders,**producer,**data,**pack_inputs,**report['fresh_dependency_sha256'],**report['fresh_depfile_sha256']}
  checks={'source_unchanged':source==inv(r/'src'),'baseline_source_unchanged':old==inv(a.baseline/'src'),'scripts_unchanged':scripts==inv(r/'scripts'),'all_bound_inputs_unchanged':all(SHA(Path(n))==h for n,h in binding.items()),'instrumented_source_unchanged':report['instrumented_source_sha256']==inv(build/'src'),'index_raw_unchanged':SHA(index)==index_sha,'semantic_index_unchanged':hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()==semantic,'final_budget_with_receipt_margin':budget_ok(allocated(q)+4096,shutil.disk_usage(q).free-4096,allocated(out))}
  report.update(status_before_final_checks=report['status'],checks=checks,seconds=time.monotonic()-start,final_allocated=allocated(q),observation_allocated=allocated(out),free_after=shutil.disk_usage(q).free)
  if not all(checks.values()):report['status']='FAIL_BINDING_OR_BUDGET_RETAINED'
  save()
  if not budget_ok(allocated(q),shutil.disk_usage(q).free,allocated(out)):report['status']='FAIL_AFTER_RECEIPT_BUDGET_RETAINED';save();raise AssertionError('after receipt budget')
  print(json.dumps({k:report.get(k) for k in ('status','actual_draw_count','first_visible','checks','peak_allocated','minimum_free','final_allocated','observation_allocated','free_after','error')},indent=2))
 assert report['status'] in ('PASS_BOUNDED_NATURAL61_OBSERVATION','NO_CONFIRMED_61_WINDOW')
if __name__=='__main__':main()
