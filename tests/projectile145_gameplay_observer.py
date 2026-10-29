#!/usr/bin/env python3
"""One bounded natural enemy145 observation, output-only instrumentation.

No actor/shot/pose insertion; no original-data edit. Reuses source-bound native
objects, recompiles four changed/instrumented TUs. No BMP or gameplay comparison.
"""
from pathlib import Path
import argparse, csv, hashlib, json, os, resource, shutil, signal, subprocess, sys, time
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FIRST,LAST=1158,1185
def inv(p):return {q.relative_to(p).as_posix():SHA(q) for q in sorted(p.rglob('*')) if q.is_file() and '__pycache__' not in q.parts}
def blocks(p):return sum(q.lstat().st_blocks*512 for q in p.rglob('*'))

LOG_FILTER=r'''
#include <stdarg.h>
/* Diagnostic output only. Function arguments retain original evaluation. */
static int projectile145_window_fprintf(FILE *stream,const char *format,...)
{
 if(stream!=stdout&&stream!=stderr&&game_probe_tick!=0&&
    !(game_probe_tick>=1158&&game_probe_tick<=1185)&&strchr(format,'%'))return 0;
 va_list args;va_start(args,format);int result=vfprintf(stream,format,args);va_end(args);return result;
}
#define fprintf projectile145_window_fprintf
'''
SHOT_LOG=r'''
static void projectile145_actual_log(const char *kind,unsigned slot,int weapon,int actor,int link,unsigned raw,unsigned index,int x,int y,unsigned animation,unsigned animation_max)
{
 if(!game_probe_enabled||game_probe_tick<1158||game_probe_tick>1185||index!=145)return;
 static FILE *f;if(!f){f=fopen("actual145-native.tsv","w");if(!f)abort();fprintf(f,"kind\ttick\tcurLoc\tslot\tweapon\tactor\tlink\traw\tindex\tx\ty\tanimation\tanimation_max\n");}
 fprintf(f,"%s\t%u\t%u\t%u\t%d\t%d\t%d\t%u\t%u\t%d\t%d\t%u\t%u\n",kind,game_probe_tick,(unsigned)curLoc,slot,weapon,actor,link,raw,index,x,y,animation,animation_max);fflush(f);
}
'''
FINISH_OBSERVER=r'''
void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)
{
 projectile145_observation_inner_finish(kind,lightx,lighty);
 if(!game_probe_enabled||game_probe_tick<1158||game_probe_tick>1185)return;
 static FILE *f;if(!f){f=fopen("actual145-final.tsv","w");if(!f)abort();fprintf(f,"tick\tslot\tx\ty\tready\tlast_valid\tmember_mask\tcached\tfault\topaque_authored_not_classic\n");}
 for(unsigned slot=0;slot<ENEMY_SHOT_MAX;slot++){
  if(enemyShotAvail[slot]||enemyShot[slot].sgr+enemyShot[slot].animate!=145)continue;
  int x=enemyShot[slot].sx,y=enemyShot[slot].sy;unsigned witness=0;
  if(ready&&last_output_valid&&global_projectile91_cached&&(global_projectile91_used_members&2u)&&
     projectile145_resources.member.valid&&projectile145_resources.member.rgba&&game_probe_density==8&&
     x>=24&&x+12<=288&&y>=0&&y+14<=184){
   for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){
    const Uint8 *a=projectile145_resources.member.rgba+4*(ay*96+ax);if(a[3]!=255)continue;
    int px=x*8+ax,py=y*8+ay;size_t n=(size_t)py*canvas->w+px;
    Uint32 got=((Uint32*)((Uint8*)output->pixels+py*output->pitch))[px-24*8];
    Uint32 want=0xff000000u|((Uint32)a[0]<<16)|((Uint32)a[1]<<8)|a[2];
    Uint32 classic=palette_rgb(((Uint8*)game_screen->pixels)[(y+ay/8)*320+x+ax/8]);
    if(global_projectile91_owner[n]&&got==want&&got!=classic)witness++;
   }
  }
  fprintf(f,"%u\t%u\t%d\t%d\t%d\t%d\t%u\t%d\t%d\t%u\n",game_probe_tick,slot,x,y,ready,last_output_valid,global_projectile91_used_members,global_projectile91_cached,global_projectile91_fault,witness);
 }
 fflush(f);
}
'''
def instrument(texts):
 from global_talon_reconstruction import extract
 out=dict(texts);marker='static unsigned int tick_limit = 600;'
 assert out['game_probe.c'].count(marker)==1
 out['game_probe.c']=out['game_probe.c'].replace(marker,LOG_FILTER+'\n'+marker)
 # Output return values are unused in the original probe, so filtering cannot
 # choose a gameplay branch. Header literals and stderr/stdout remain visible.
 assert 'if(fprintf' not in texts['game_probe.c'] and '=fprintf' not in texts['game_probe.c']
 marker='inline static void blit_enemy';assert marker in out['tyrian2.c']
 out['tyrian2.c']=out['tyrian2.c'].replace(marker,SHOT_LOG+'\n'+marker,1)
 marker='enemyShot[b].sgr = weapons[temp3].sg[tempPos];';assert out['tyrian2.c'].count(marker)==1
 out['tyrian2.c']=out['tyrian2.c'].replace(marker,marker+'\n projectile145_actual_log("emit",b,temp3,enemy[i].enemytype,enemy[i].linknum,enemyShot[b].sgr,enemyShot[b].sgr,enemyShot[b].sx,enemyShot[b].sy,enemyShot[b].animate,enemyShot[b].animax);')
 marker='unsigned int sprite = enemyShot[z].sgr + enemyShot[z].animate;';assert out['tyrian2.c'].count(marker)==1
 out['tyrian2.c']=out['tyrian2.c'].replace(marker,marker+'\n projectile145_actual_log("draw",z,-1,-1,-1,enemyShot[z].sgr,sprite,enemyShot[z].sx,enemyShot[z].sy,enemyShot[z].animate,enemyShot[z].animax);')
 original=extract(out['render_mirror.c'],'render_mirror_finish');assert out['render_mirror.c'].count(original)==1
 out['render_mirror.c']=out['render_mirror.c'].replace(original,original.replace('void render_mirror_finish(', 'static void projectile145_observation_inner_finish(',1)+'\n'+FINISH_OBSERVER)
 return out

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','baseline','fresh-proof','object-proof','base-pack','data','sysroot','out'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.root;q=a.out;reserve=250*1024**2;peak=50*1024**2
 assert not q.exists() and shutil.disk_usage(q.parent).free>=reserve+peak
 source=inv(r/'src');proof=json.loads((a.fresh_proof/'native-receipt.json').read_text());old={n.removeprefix('src/'):h for n,h in proof['source_sha256'].items()};assert proof['status']=='PASS'
 assert {n for n in old if source.get(n)!=old[n]}=={'render_mirror.c','global_projectile91_mirror.inc','tyrian2.c','entity_draw.c'}
 assert set(source)-set(old)=={'enemy_projectile145_mirror.inc','current_projectile145_payload_pins.h'}
 assert inv(a.fresh_proof/'hd-on-build/src')==old
 op=json.loads(a.object_proof.read_text());assert op['status']=='PASS' and op['fresh_objects_before']==op['fresh_objects_after']
 objroot=a.fresh_proof/'hd-on-build/obj';objects={str(objroot/n):h for n,h in op['fresh_objects_before'].items()};assert all(SHA(Path(n))==h for n,h in objects.items())
 units=('render_mirror','tyrian2','entity_draw','game_probe');borrowed=[p for p in sorted(objroot.glob('*.o')) if p.stem not in units];assert len(borrowed)==82
 deps={}
 for obj in borrowed:
  for token in obj.with_suffix('.d').read_text().replace('\\\n',' ').split()[1:]:
   if token.endswith(':') or not token.startswith('src/'):continue
   name=token[4:]
   if name.startswith('../assets/'):
    f=a.baseline/name[3:];original=a.fresh_proof/'hd-on-build'/name[3:];assert SHA(f)==SHA(original);deps[str(f)]=SHA(f)
   else:assert name in old and source[name]==old[name],(obj,name)
 driver=Path(__file__).resolve();sys.path.insert(0,str(r/'tests'));helper=r/'tests/global_talon_reconstruction.py';producer={str(driver):SHA(driver),str(helper):SHA(helper)}
 originals={n:(r/'src'/n).read_text() for n in ('game_probe.c','tyrian2.c','render_mirror.c')};modified=instrument(originals)
 scripts=inv(r/'scripts');data={str(f):SHA(f) for f in sorted(a.data.iterdir()) if f.is_file()}
 pack_inputs={str(f.resolve()):SHA(f) for f in sorted(a.base_pack.rglob('*')) if f.is_file()};hda=r/'assets/hd/current-compat/projectile145/enemy-projectile145-145-8.hda';pack_inputs[str(hda)]=SHA(hda)
 index=Path(subprocess.check_output(['git','--no-optional-locks','-C',str(r),'rev-parse','--path-format=absolute','--git-path','index'],text=True).strip());index_sha=SHA(index)
 q.mkdir();build=q/'build';(build/'src').mkdir(parents=True);(q/'tmp').mkdir()
 for n in source:(build/'src'/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/'src'/n,build/'src'/n)
 for n,text in modified.items():(build/'src'/n).write_text(text)
 for name in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h'):
  src=a.baseline/'assets/hd/shared-menu-runs-v1'/name;target=build/src.relative_to(a.baseline);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target);deps[str(src)]=SHA(src)
 pack=q/'pack';pack.mkdir()
 for f in sorted(a.base_pack.rglob('*')):
  if f.is_file():d=pack/f.relative_to(a.base_pack);d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
 assert not (pack/hda.name).exists();(pack/hda.name).symlink_to(hda)
 out=q/'observation';cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 2x\nitem fullscreen -1\n')
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'TMPDIR':str(q/'tmp')}
 removed=[]
 for key in tuple(env):
  if key.startswith(('AIRCRAFT170_','SHARED170_','TYRIAN_CYAN_BORROW','TYRIAN_GAME_PROBE','OT_','PROJECTILE145_')):removed.append(key);env.pop(key)
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 flags=['-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(build/'src')]
 report=dict(status='RUNNING',scope=__doc__,source_sha256=source,instrumented_source_sha256=inv(build/'src'),producer_sha256=producer,scripts_sha256=scripts,objects_sha256=objects,original_data_sha256=data,pack_target_sha256=pack_inputs,external_header_sha256=deps,index_sha256=index_sha,source_proof_sha256=SHA(a.fresh_proof/'native-receipt.json'),object_proof_sha256=SHA(a.object_proof),window=[FIRST,LAST],event_candidate=1162,episode=1,physical_level=2,natural_actors_and_shots=True,controlled_input='Existing asset-debug enemy-hit stationary/no-firing input; no emitter/shot/pose injection',environment={k:env[k] for k in ('SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER','HOME','XDG_CONFIG_HOME','LD_LIBRARY_PATH')},removed_control_keys=removed,commands=[],peak_budget_bytes=peak,reserve_bytes=reserve,peak_allocated_sample=blocks(q),minimum_free_sample=shutil.disk_usage(q).free,sample_interval_seconds=.25,free_before=shutil.disk_usage(q).free)
 def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 def run(cmd,label,cwd,timeout=300):
  row=dict(argv=list(map(str,cmd)),label=label,cwd=str(cwd));report['commands'].append(row);save()
  with (q/(label+'.stdout')).open('wb') as stdout,(q/(label+'.stderr')).open('wb') as stderr:
   z=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=no_core);row['pid']=z.pid;save();start=time.monotonic()
   while z.poll() is None:
    used=blocks(q);free=shutil.disk_usage(q).free;report['peak_allocated_sample']=max(used,report['peak_allocated_sample']);report['minimum_free_sample']=min(free,report['minimum_free_sample'])
    if used>peak or free<reserve or blocks(out)>8*1024**2 or time.monotonic()-start>timeout:os.killpg(z.pid,signal.SIGTERM);row['stopped_for_budget_or_timeout']=True;break
    time.sleep(.25)
   row['returncode']=z.wait();row['seconds']=time.monotonic()-start;save()
   if row['returncode'] or row.get('stopped_for_budget_or_timeout'):raise RuntimeError(label+' failed; logs retained')
 save();start=time.monotonic()
 try:
  fresh=[]
  for unit in units:
   obj=build/(unit+'.o');run(['cc',*flags,'-c',build/'src'/(unit+'.c'),'-o',obj],unit+'-compile',build);fresh.append(obj)
  exe=build/'opentyrian2000';run(['cc',*borrowed,*fresh,*libs,'-lm','-o',exe],'link',build)
  command=[exe,'--data='+str(a.data),'--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=2','--asset-debug-tick=1158','--asset-debug-running','--render-ticks=1186','--render-assets='+str(pack),'--global-assets='+str(pack),'--render-no-capture','--render-test=8']
  run(command,'natural-observation',out,600)
  assert not list(out.rglob('*.bmp')) and not list(out.rglob('*.png'))
  def rows(name):
   f=out/name
   if not f.exists():return []
   with f.open() as stream:return list(csv.DictReader(stream,delimiter='\t'))
  actual=rows('actual145-native.tsv');final=rows('actual145-final.tsv');scene=rows('scene-draw-commands.tsv')
  emits=[z for z in actual if z['kind']=='emit' and z['weapon']=='4' and z['actor']=='194' and z['link']=='3']
  draws=[z for z in actual if z['kind']=='draw' and z['index']=='145']
  admitted=[z for z in scene if z['role']=='150' and z['index']=='145' and z['mirrored']=='1']
  visible=[z for z in final if int(z['opaque_authored_not_classic'])>0 and z['ready']=='1' and z['last_valid']=='1' and z['cached']=='1' and z['fault']=='0']
  candidates=[z for z in visible if any(d['tick']==z['tick'] and d['slot']==z['slot'] and d['x']==z['x'] and d['y']==z['y'] for d in draws) and any(d['tick']==z['tick'] and d['x']==z['x'] and d['y']==z['y'] for d in admitted)]
  report.update(status='PASS_BOUNDED_NATURAL_OBSERVATION' if emits and candidates else 'NO_CONFIRMED_145_WINDOW',actual_emission_count=len(emits),actual_draw_count=len(draws),hd_admission_count=len(admitted),visible_witness_count=len(candidates),first_visible=candidates[0] if candidates else None,emissions=emits,visible_candidates=candidates,binary_sha256=SHA(exe),actual_capture_performed=False)
 finally:
  checks=dict(source_unchanged=source==inv(r/'src'),scripts_unchanged=scripts==inv(r/'scripts'),objects_unchanged=all(SHA(Path(n))==h for n,h in objects.items()),inputs_unchanged=all(SHA(Path(n))==h for n,h in {**producer,**data,**pack_inputs,**deps}.items()),instrumented_unchanged=report['instrumented_source_sha256']==inv(build/'src'),index_unchanged=SHA(index)==index_sha)
  report.update(checks=checks,seconds=time.monotonic()-start,final_allocated_bytes=blocks(q),observation_allocated_bytes=blocks(out),free_after=shutil.disk_usage(q).free)
  if not all(checks.values()) or report['final_allocated_bytes']>peak or report['free_after']<reserve:report['status']='FAIL_BINDING_OR_BUDGET'
  save();print(json.dumps({k:report.get(k) for k in ('status','actual_emission_count','actual_draw_count','hd_admission_count','visible_witness_count','first_visible','checks','peak_allocated_sample','minimum_free_sample','final_allocated_bytes','observation_allocated_bytes','free_after','seconds')},indent=2))
 assert report['status']=='PASS_BOUNDED_NATURAL_OBSERVATION'
if __name__=='__main__':main()
