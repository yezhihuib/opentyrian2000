#!/usr/bin/env python3
"""One natural E2 physical9 tick150 triple; ordinary source-bound derivative.

Present61/current-missing61/qualified145 baseline. Output-only diagnostics and
unchanged existing stationary/no-player-fire probe input; no actor/shot fixture.
Five fresh ordinary TUs plus bound existing objects, not full fresh61/SAN/gate.
"""
from pathlib import Path
import argparse,csv,hashlib,io,json,os,resource,shlex,shutil,signal,subprocess,sys,time,zipfile
import numpy as np
from PIL import Image
import projectile61_gameplay_observer as obs
import projectile61_gameplay_instrumentation as instr
SHA=obs.SHA
TICK=150
PEAK=64*1024**2;RESERVE=250*1024**2
OBSERVATION_SHA='416d6fce3186e3a4a22c681323f97e2c1d2dc56337f7f9383f0a4627991e66c8'
OBS_REVIEW_SHA='f095e72bc2175035faea1d5b0db726bdd46d4eb4b0d12edbd18eb5bae3e04804'
BLEND_HEADER='tick\tw\th\tpitch\tindex\torigin_x\torigin_y\twrite_x\twrite_y\tbefore\tsource\tafter\n'
DUMP=r'''
 if(game_probe_enabled&&game_probe_tick==150){
  SDL_Surface *surfaces[2]={game_screen,VGAScreenSeg};const char *names[2]={"native-game-screen.index8","native-vga-screen.index8"};
  for(unsigned k=0;k<2;k++){SDL_Surface *v=surfaces[k];if(!v||!v->format||v->format->BytesPerPixel!=1)abort();FILE *f=fopen(names[k],"wb");if(!f)abort();for(int y=0;y<v->h;y++)if(fwrite((Uint8*)v->pixels+y*v->pitch,1,v->w,f)!=(size_t)v->w)abort();if(fclose(f))abort();}
  FILE *f=fopen("native-palette.rgb","wb");if(!f)abort();for(unsigned i=0;i<256;i++){Uint8 bytes[3]={rgb_palette[i]>>16,rgb_palette[i]>>8,rgb_palette[i]};if(fwrite(bytes,1,3,f)!=3)abort();}if(fclose(f))abort();
 }
'''
BLEND_ORIGINAL='{ *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0); render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }'
BLEND_REPLACEMENT=r'''{ unsigned before=*pixels;
 *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0);
 if(game_probe_enabled&&game_probe_tick==150){
  static FILE *trace;if(!trace){trace=fopen("native-blend-writes.tsv","a");if(!trace)abort();}
  long offset=pixels-(Uint8*)surface->pixels;
  if(fprintf(trace,"%u\t%d\t%d\t%d\t%u\t%d\t%d\t%ld\t%ld\t%u\t%u\t%u\n",game_probe_tick,surface->w,surface->h,surface->pitch,(unsigned)index,x,y,offset%surface->pitch,offset/surface->pitch,before,(unsigned)*data,(unsigned)*pixels)<0)abort();if(fflush(trace))abort();
 }
 render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }'''
PROBE_FILTER=instr.LOG_FILTER.replace('game_probe_tick!=0&&','game_probe_tick!=0&&game_probe_tick!=150&&')
environment=obs.environment

def budget_ok(used,free):return used<=PEAK and free>=RESERVE
def capture_names():return {'classic-0150.bmp','display-0150.bmp','asset-debug-window-0150.bmp'}
def once(text,marker,new):
 assert text.count(marker)==1,marker
 return text.replace(marker,new,1)
def renderer_text(text):
 marker=instr.FINISH_DECL+'\n{'
 return once(text,marker,marker+DUMP)
def baseline_shot_text(text):
 assert 'projectile61_actual_log' not in text
 text=once(text,instr.SHOT_DECL,instr.SHOT_LOG+'\n'+instr.SHOT_DECL)
 text=once(text,instr.EMIT_MARKER,instr.EMIT_MARKER+'\n '+instr.EMIT_CALL)
 return once(text,instr.DRAW_MARKER,instr.DRAW_MARKER+'\n '+instr.DRAW_CALL)
def game_probe_text(text):
 instr._diagnostics_only(text,'game_probe.c')
 assert 'projectile61_tickzero_fprintf' not in text
 text=once(text,instr.PROBE_MARKER,instr.ADMISSION_LOG+'\n'+PROBE_FILTER+'\n'+instr.PROBE_MARKER)
 return once(text,instr.ADMISSION_DECL,instr.ADMISSION_DECL+'\n'+instr.ADMISSION_CALL)
def sprite_text(text):
 text=once(text,'#include "asset_debug.h"','#include "asset_debug.h"\n#include "game_probe.h"')
 return once(text,BLEND_ORIGINAL,BLEND_REPLACEMENT)
def rows(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
def identity(root):
 ix=Path(git(root,'rev-parse','--path-format=absolute','--git-path','index').decode().strip())
 return {'head':git(root,'rev-parse','HEAD').decode().strip(),'index_path':str(ix),'raw_sha256':SHA(ix),'semantic_sha256':hashlib.sha256(git(root,'ls-files','--stage','-z')).hexdigest()}

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for name in ('root','baseline','observation','observer-review','sysroot','data','out'):parser.add_argument('--'+name,type=Path,required=True)
 a=parser.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.root;b=a.baseline;o=a.observation;q=a.out
 assert not q.exists() and shutil.disk_usage(q.parent).free>=PEAK+RESERVE
 assert SHA(o/'receipt.json')==OBSERVATION_SHA and SHA(a.observer_review)==OBS_REVIEW_SHA
 old=json.loads((o/'receipt.json').read_text());assert old['status']=='PASS_BOUNDED_NATURAL61_OBSERVATION' and all(old['checks'].values())
 source=obs.inv(r/'src');base=obs.inv(b/'src');scripts=obs.inv(r/'scripts')
 assert source==old['source_sha256'] and base==old['baseline_source_sha256'] and scripts==old['scripts_sha256']
 assert len(source)==310 and len(base)==308
 assert {n for n in base if source.get(n)!=base[n]}==obs.CHANGED and set(source)-set(base)==obs.ADDED
 assert obs.inv(o/'build/src')==old['instrumented_source_sha256']
 roots={str(root):identity(root) for root in (r,b)}
 assert roots[str(r)]['raw_sha256']==old['source_index_sha256'] and roots[str(r)]['semantic_sha256']==old['semantic_index_sha256']
 inputs={}
 for key in ('producer_sha256','all86_baseline_objects_sha256','archived_depfile_sha256','dependency_sha256','current_sysroot_header_sha256','fresh_dependency_sha256','fresh_depfile_sha256','original_data_sha256','pack_target_sha256','fresh_object_sha256'):inputs.update(old[key])
 inputs.update({str(o/'receipt.json'):OBSERVATION_SHA,str(a.observer_review):OBS_REVIEW_SHA,str(o/'build/opentyrian2000'):old['binary_sha256']})
 for name,h in source.items():inputs[str(r/'src'/name)]=h
 for name,h in base.items():inputs[str(b/'src'/name)]=h
 for name,h in old['instrumented_source_sha256'].items():inputs[str(o/'build/src'/name)]=h
 driver=Path(__file__).resolve()
 for n in (driver.name,'projectile61_gameplay_observer.py','projectile61_gameplay_instrumentation.py','test_projectile61_gameplay_differential.py'):inputs[str(driver.with_name(n))]=SHA(driver.with_name(n))
 for n in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h'):
  p=b/'assets/hd/shared-menu-runs-v1'/n;inputs[str(p)]=SHA(p)
 assert all(SHA(Path(n))==h for n,h in inputs.items())
 sys.path.insert(0,str(r/'scripts'));import current_projectile61_compatibility as art
 art.load(r);mask=np.array(list(art.MASK)).reshape(14,12)=='1';assert int(mask.sum())==74 and not mask[:,4:8].any()
 for n in art.input_paths(r):inputs[str(r/n)]=SHA(r/n)
 assert len(old['pack_target_sha256'])==734
 pack_now={str(p.resolve()):SHA(p) for p in (o/'pack').rglob('*') if p.is_file()};assert pack_now==old['pack_target_sha256']
 hda=r/art.ROOT/art.name(1510061);assert SHA(hda)=='3530c27302a2cb3d26830711cd4b94a01aacbfad748c91aea219bbc81b0c5c29'
 objects={Path(n):h for n,h in old['all86_baseline_objects_sha256'].items()};assert len(objects)==86
 primary=next(p.parent for p in objects if p.name=='sprite.o')
 excluded={'render_mirror','sprite','asset_debug','tyrian2','entity_draw','game_probe'}
 reused=sorted(p for p in objects if p.stem not in excluded);assert len(reused)==80
 # The observer has already independently bound each old .d, actual dependency,
 # normal object, and its five new source+object closures; bind all again here.
 assert all(str(p) in old['reused81_objects'] for p in reused)
 for n in ('sprite.c','asset_debug.c','game_probe.c'):assert source[n]==base[n]
 assert (o/'build/src/asset_debug.c').read_text()==(b/'src/asset_debug.c').read_text().replace(instr.ASSET_MARKER,instr.LOG_FILTER+'\n'+instr.ASSET_MARKER,1)
 texts={
  'current-render_mirror.c':renderer_text((o/'build/src/render_mirror.c').read_text()),
  'baseline-render_mirror.c':renderer_text((b/'src/render_mirror.c').read_text()),
  'baseline-tyrian2.c':baseline_shot_text((b/'src/tyrian2.c').read_text()),
  'sprite.c':sprite_text((b/'src/sprite.c').read_text()),
  'game_probe.c':game_probe_text((b/'src/game_probe.c').read_text())}
 assert 'projectile61_resources' not in texts['baseline-render_mirror.c']
 q.mkdir();(q/'tmp').mkdir();build=q/'build';build.mkdir()
 for n,t in texts.items():(build/n).write_text(t)
 emitted=obs.inv(build)
 env,_=environment(os.environ,a.sysroot,q,q/'tmp')
 cflags=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True));libs=shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True))
 report=dict(status='RUNNING',scope=__doc__,source_sha256=source,baseline_source_sha256=base,scripts_sha256=scripts,inputs_sha256=inputs,instrumented_sha256=emitted,roots=roots,observation_receipt_sha256=OBSERVATION_SHA,observer_review_sha256=OBS_REVIEW_SHA,commands=[],runs=[],fresh_depfile_sha256={},fresh_dependency_sha256={},peak_budget_bytes=PEAK,reserve_bytes=RESERVE,peak_allocated_sample=0,minimum_free_sample=shutil.disk_usage(q).free,sample_interval_seconds=.25,free_before=shutil.disk_usage(q).free,internal_density=8,physical_output_scale=2,episode=2,physical_level=9,actual_tick=TICK,controlled_emitter_or_pose=False,controlled_player_input='unchanged existing asset-debug stationary/no-firing input',original145_fresh_FAIL_and_independent_acceptance_retained=True)
 def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def measure():
  used=obs.allocated(q);free=shutil.disk_usage(q).free;report['peak_allocated_sample']=max(used,report['peak_allocated_sample']);report['minimum_free_sample']=min(free,report['minimum_free_sample']);assert budget_ok(used,free),('budget',used,free)
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 def run(cmd,label,cwd,e):
  row=dict(argv=list(map(str,cmd)),label=label,cwd=str(cwd));report['commands'].append(row);save()
  with (q/(label+'.stdout')).open('wb') as stdout,(q/(label+'.stderr')).open('wb') as stderr:
   z=subprocess.Popen(row['argv'],cwd=cwd,env=e,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=no_core);row['pid']=z.pid;save();start=time.monotonic()
   try:
    while z.poll() is None:measure();assert time.monotonic()-start<300,'bounded timeout';time.sleep(.25)
   except BaseException:
    if z.poll() is None:os.killpg(z.pid,signal.SIGTERM);z.wait()
    row['stopped']=True;raise
   finally:row.update(returncode=z.poll(),seconds=time.monotonic()-start);save()
   assert row['returncode']==0,(label,row['returncode'])
   if not label.endswith('-game'):assert not (q/(label+'.stderr')).read_bytes(),label+' stderr'
  measure()
 save();start=time.monotonic()
 try:
  for name in texts:
   include=o/'build/src' if name.startswith('current-') else b/'src'
   flags=['-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(include)]
   obj=build/(name.removesuffix('.c')+'.o');dep=obj.with_suffix('.d')
   run(['cc',*flags,'-MMD','-MF',dep,'-c',build/name,'-o',obj],name+'-compile',build,env)
   report['fresh_depfile_sha256'][str(dep)]=SHA(dep)
   for token in obs.dep_tokens(dep.read_text()):
    p=(build/token).resolve() if not Path(token).is_absolute() else Path(token).resolve();h=SHA(p)
    expected=emitted.get(p.name) if p.parent==build else inputs.get(str(p))
    assert expected==h,('fresh dependency not previously bound',str(p),expected,h)
    report['fresh_dependency_sha256'][str(p)]=h
  assert len(report['fresh_depfile_sha256'])==5
  common=[*reused,build/'sprite.o',build/'game_probe.o',o/'build/asset_debug.o']
  variant_objects={
   'current':[*common,build/'current-render_mirror.o',o/'build/tyrian2.o',o/'build/entity_draw.o'],
   'baseline':[*common,build/'baseline-render_mirror.o',build/'baseline-tyrian2.o',primary/'entity_draw.o']}
  report['linked_objects_sha256']={}
  for kind,objs in variant_objects.items():
   assert len(objs)==len(set(objs))==86
   report['linked_objects_sha256'][kind]={str(p):SHA(p) for p in objs}
   run(['cc',*objs,*libs,'-lm','-o',build/kind],kind+'-link',build,env)
  for kind in ('present','missing'):
   pack=q/(kind+'-pack');pack.mkdir()
   for f in sorted((o/'pack').rglob('*')):
    if f.is_file() and not(kind=='missing' and f.name==hda.name):
     d=pack/f.relative_to(o/'pack');d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
  packsets={kind:{str(p.resolve()):SHA(p) for p in (q/(kind+'-pack')).rglob('*') if p.is_file()} for kind in ('present','missing')}
  assert packsets['present']==pack_now and packsets['missing']=={n:h for n,h in pack_now.items() if n!=str(hda)}
  report['pack_target_sha256']=packsets
  for kind in ('present','missing','baseline'):
   out=q/kind;cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 2x\nitem fullscreen -1\n');(out/'native-blend-writes.tsv').write_text(BLEND_HEADER)
   e,removed=environment(os.environ,a.sysroot,out,q/'tmp');pack=q/('present-pack' if kind=='present' else 'missing-pack');exe=build/('baseline' if kind=='baseline' else 'current')
   cmd=[exe,'--data='+str(a.data),'--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=2','--asset-debug-level=9','--asset-debug-tick=140','--asset-debug-running','--render-ticks=151','--render-assets='+str(pack),'--global-assets='+str(pack),'--asset-debug-capture','--asset-debug-capture-start=150','--asset-debug-capture-count=1','--render-test=8']
   run(cmd,kind+'-game',out,e)
   captures={p.name:dict(sha256=SHA(p),bytes=p.stat().st_size,mode=p.stat().st_mode&0o777) for p in sorted(out.glob('*.bmp'))};assert set(captures)==capture_names()
   archive=out/'captures.zip'
   with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zz:
    for name in captures:
     measure();Image.open(out/name).save((out/name).with_suffix('.png'));measure();zz.write(out/name,name);measure()
   measure() # Include ZIP close/central directory before any duplicate removal.
   with zipfile.ZipFile(archive) as zz:
    assert set(zz.namelist())==set(captures) and zz.testzip() is None
    for name,pin in captures.items():
     raw=zz.read(name);assert raw==(out/name).read_bytes() and hashlib.sha256(raw).hexdigest()==pin['sha256'] and len(raw)==pin['bytes']
     assert np.array_equal(np.array(Image.open(io.BytesIO(raw)).convert('RGBA')),np.array(Image.open((out/name).with_suffix('.png')).convert('RGBA')))
   recovery=dict(archive='captures.zip',archive_sha256=SHA(archive),members=captures,verification='complete decompressed bytes/SHA/size equal actual BMP and corresponding PNG pixels equal; only these three duplicate BMP paths removed',status='VERIFIED_LOSSLESS_DUPLICATES_RETAINED')
   (out/'bmp-recovery-map.json').write_text(json.dumps(recovery,indent=2)+'\n')
   measure() # PNG/ZIP/map high-water must pass while all original BMPs still exist.
   for name,pin in captures.items():
    path=out/name;assert path.is_file() and not path.is_symlink() and SHA(path)==pin['sha256'] and path.stat().st_nlink==1;path.unlink()
   recovery['status']='VERIFIED_LOSSLESS_DUPLICATES_COMPACTED'
   (out/'bmp-recovery-map.json').write_text(json.dumps(recovery,indent=2)+'\n');measure()
   report['runs'].append(dict(variant=kind,binary_sha256=SHA(exe),argv=list(map(str,cmd)),environment={k:e[k] for k in ('SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER','HOME','XDG_CONFIG_HOME','LD_LIBRARY_PATH','TMPDIR')},removed_control_key_names=removed,control_keys_present=[k for k in e if k.startswith(('AIRCRAFT','PROJECTILE','SHARED','TYRIAN_CYAN_BORROW','TYRIAN_GAME_PROBE','OT_'))],capture_recovery=recovery));measure();save()
  paths=[q/k for k in ('present','missing','baseline')]
  names=('state.tsv','enemy-projectiles.tsv','collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv','native-blend-writes.tsv','native-game-screen.index8','native-vga-screen.index8','native-palette.rgb','actual61-native.tsv')
  equal={n:len({(x/n).read_bytes() for x in paths})==1 for n in names};assert all(equal.values()),equal
  assert [(paths[0]/n).stat().st_size for n in ('native-game-screen.index8','native-vga-screen.index8','native-palette.rgb')]==[64000,64000,768]
  states=[row for row in rows(paths[0]/'state.tsv') if row['tick']=='150'];assert len(states)==1
  actual=rows(paths[0]/'actual61-native.tsv');shots=[x for x in actual if x['kind']=='draw' and x['tick']=='150' and x['index']=='61']
  assert len(shots)==1 and (shots[0]['slot'],int(shots[0]['x']),int(shots[0]['y']),shots[0]['curLoc'])==('43',112,29,'151')
  emits=[x for x in actual if x['kind']=='emit' and x['tick']=='150'];assert len(emits)==1
  assert all(emits[0][k]==v for k,v in {'slot':'43','weapon':'131','actor':'795','link':'10','actor_slot':'50','x':'112','y':'23','index':'61'}.items())
  admissions=rows(paths[0]/'actual61-admission.tsv');assert any(x['tick']=='150' and x['role']=='151' and x['index']=='61' and x['mirrored']=='1' for x in admissions)
  missing_admissions=rows(paths[1]/'actual61-admission.tsv');assert any(x['tick']=='150' and x['role']=='151' and x['index']=='61' and x['mirrored']=='0' for x in missing_admissions)
  _,_,_,candidates=obs.classify_observation(actual,rows(paths[0]/'actual61-final.tsv'),admissions);assert any(x['tick']=='150' and x['slot']=='43' and x['opaque_authored_not_classic']=='246' for x in candidates)
  pixels=[];frozen={};oldhd=0;opaque=0
  for bmp in sorted(capture_names()):
   name=bmp.replace('.bmp','.png');arrays=[np.array(Image.open(x/name).convert('RGB')) for x in paths];after,before,baseline=arrays;factor=after.shape[1]//320
   assert after.shape==before.shape==baseline.shape==(200*factor,320*factor,3)
   assert factor=={'classic-0150.png':1,'display-0150.png':8,'asset-debug-window-0150.png':2}[name]
   frozen[name]=bool(np.array_equal(before,baseline));assert frozen[name]
   support=np.zeros(after.shape[:2],dtype=bool)
   for shot in shots:
    x,y=int(shot['x'])-24,int(shot['y'])
    for yy,xx in zip(*np.where(mask)):
     if 0<=x+xx<264 and 0<=y+yy<184:support[(y+yy)*factor:(y+yy+1)*factor,(x+xx)*factor:(x+xx+1)*factor]=True
   delta=np.any(after!=before,axis=2);outside=int((delta&~support).sum());changed=int(delta.sum());assert outside==0
   assert changed==0 if factor==1 else changed>0
   pixels.append(dict(file=name,factor=factor,changed=changed,outside_native_mask_support=outside))
   if factor==8:
    classic=np.array(Image.open(paths[0]/'classic-0150.png').convert('RGB'));classic8=np.repeat(np.repeat(classic,8,0),8,1)
    oldhd=int((np.any(before!=classic8,axis=2)&~support).sum());assert oldhd>512
    raw=np.frombuffer(hda.read_bytes()[28:],dtype=np.uint8).reshape(112,96,4)
    x,y=(int(shots[0]['x'])-24)*8,int(shots[0]['y'])*8;region=after[y:y+112,x:x+96];orig=classic8[y:y+112,x:x+96]
    opaque=int(((raw[:,:,3]==255)&np.all(region==raw[:,:,:3],axis=2)&np.any(region!=orig,axis=2)).sum());assert opaque==246
  report.update(status='PASS_NATURAL_TICK150_TRIPLE',native_equal=equal,frozen_missing_equal=frozen,pixels=pixels,old_hd_outside61_not_classic=oldhd,opaque_authored_not_classic=opaque,native_blend_writes=len(rows(paths[0]/'native-blend-writes.tsv')),actual_shots=shots,actual_same_tick_emissions=emits,tick150_native_state=states[0],zero_or_hit_counts={n:len(rows(paths[0]/n)) for n in ('collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv','native-blend-writes.tsv')})
 except BaseException as error:report.update(status='FAIL_RETAINED',error=repr(error));raise
 finally:
  checks=dict(source_unchanged=obs.inv(r/'src')==source,baseline_unchanged=obs.inv(b/'src')==base,scripts_unchanged=obs.inv(r/'scripts')==scripts,roots_unchanged=all(identity(Path(n))==h for n,h in roots.items()),inputs_unchanged=all(SHA(Path(n))==h for n,h in inputs.items()),instrumented_unchanged=all(SHA(build/n)==h for n,h in emitted.items()),fresh_dependencies_unchanged=all(SHA(Path(n))==h for n,h in report['fresh_dependency_sha256'].items()),fresh_depfiles_unchanged=all(SHA(Path(n))==h for n,h in report['fresh_depfile_sha256'].items()),linked_objects_unchanged=all(SHA(Path(n))==h for values in report.get('linked_objects_sha256',{}).values() for n,h in values.items()),final_budget_with_receipt_margin=budget_ok(obs.allocated(q)+4096,shutil.disk_usage(q).free-4096))
  report.update(status_before_final_checks=report['status'],checks=checks,seconds=time.monotonic()-start,final_allocated_bytes=obs.allocated(q),free_after=shutil.disk_usage(q).free)
  if not all(checks.values()):report['status']='FAIL_BINDING_OR_BUDGET_RETAINED'
  save()
  if not budget_ok(obs.allocated(q),shutil.disk_usage(q).free):report['status']='FAIL_AFTER_RECEIPT_BUDGET_RETAINED';save();raise AssertionError('after receipt budget')
  print(json.dumps({k:report.get(k) for k in ('status','pixels','native_equal','frozen_missing_equal','old_hd_outside61_not_classic','opaque_authored_not_classic','native_blend_writes','checks','peak_allocated_sample','minimum_free_sample','final_allocated_bytes','free_after','error')},indent=2))
 assert report['status']=='PASS_NATURAL_TICK150_TRIPLE'
if __name__=='__main__':main()
