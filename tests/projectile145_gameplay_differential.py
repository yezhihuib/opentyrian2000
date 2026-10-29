#!/usr/bin/env python3
"""One natural-shot tick1162 triple; ordinary source-bound derivative, not fresh/full game build.

Original actors/shots; identical existing deterministic no-fire player input.
Only output instrumentation. No production source or game-data changes.
"""
from pathlib import Path
import argparse,csv,hashlib,json,os,resource,shutil,signal,subprocess,sys,time,zipfile
import numpy as np
from PIL import Image
import projectile145_gameplay_observer as obs
SHA=obs.SHA
TICK=1162
BLEND_HEADER='tick\tw\th\tpitch\tindex\torigin_x\torigin_y\twrite_x\twrite_y\tbefore\tsource\tafter\n'
DUMP=r'''
 if(game_probe_enabled&&game_probe_tick==1162){
  SDL_Surface *surfaces[2]={game_screen,VGAScreenSeg};const char *names[2]={"native-game-screen.index8","native-vga-screen.index8"};
  for(unsigned k=0;k<2;k++){SDL_Surface *v=surfaces[k];if(!v||!v->format||v->format->BytesPerPixel!=1)abort();FILE *f=fopen(names[k],"wb");if(!f)abort();for(int y=0;y<v->h;y++)if(fwrite((Uint8*)v->pixels+y*v->pitch,1,v->w,f)!=(size_t)v->w)abort();fclose(f);}
  FILE *f=fopen("native-palette.rgb","wb");if(!f)abort();for(unsigned i=0;i<256;i++){Uint8 bytes[3]={rgb_palette[i]>>16,rgb_palette[i]>>8,rgb_palette[i]};if(fwrite(bytes,1,3,f)!=3)abort();}fclose(f);
 }
'''
BLEND_ORIGINAL='{ *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0); render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }'
BLEND_REPLACEMENT=r'''{ unsigned before=*pixels;
 *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0);
 if(game_probe_enabled&&game_probe_tick>=1158&&game_probe_tick<=1162){
  static FILE *trace;if(!trace){trace=fopen("native-blend-writes.tsv","a");if(!trace)abort();}
  long offset=pixels-(Uint8*)surface->pixels;
  fprintf(trace,"%u\t%d\t%d\t%d\t%u\t%d\t%d\t%ld\t%ld\t%u\t%u\t%u\n",game_probe_tick,surface->w,surface->h,surface->pitch,(unsigned)index,x,y,offset%surface->pitch,offset/surface->pitch,before,(unsigned)*data,(unsigned)*pixels);fflush(trace);
 }
 render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }'''
def sprite_text(text):
 assert text.count(BLEND_ORIGINAL)==1
 return text.replace('#include "asset_debug.h"','#include "asset_debug.h"\n#include "game_probe.h"').replace(BLEND_ORIGINAL,BLEND_REPLACEMENT)
def asset_text(text):
 marker='static bool window_only,explosion_log_enabled;';assert text.count(marker)==1
 # All call arguments remain evaluated; return values unused. No branches changed.
 assert 'if(fprintf' not in text and '=fprintf' not in text
 return text.replace(marker,obs.LOG_FILTER+'\n'+marker)
def renderer_text(text):
 marker='void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)\n{';assert text.count(marker)==1
 return text.replace(marker,marker+DUMP)
def baseline_shot_text(text):
 marker='inline static void blit_enemy';assert marker in text
 text=text.replace(marker,obs.SHOT_LOG+'\n'+marker,1)
 marker='enemyShot[b].sgr = weapons[temp3].sg[tempPos];';assert text.count(marker)==1
 text=text.replace(marker,marker+'\n projectile145_actual_log("emit",b,temp3,enemy[i].enemytype,enemy[i].linknum,enemyShot[b].sgr,enemyShot[b].sgr,enemyShot[b].sx,enemyShot[b].sy,enemyShot[b].animate,enemyShot[b].animax);')
 marker='unsigned int sprite = enemyShot[z].sgr + enemyShot[z].animate;';assert text.count(marker)==1
 return text.replace(marker,marker+'\n projectile145_actual_log("draw",z,-1,-1,-1,enemyShot[z].sgr,sprite,enemyShot[z].sx,enemyShot[z].sy,enemyShot[z].animate,enemyShot[z].animax);')
def environment(parent,sysroot,out,tmp):
 env=dict(parent)
 for key in tuple(env):
  if key.startswith(('AIRCRAFT170_','SHARED170_','TYRIAN_CYAN_BORROW','TYRIAN_GAME_PROBE','OT_','PROJECTILE145_')):env.pop(key)
 env.update(PKG_CONFIG_SYSROOT_DIR=str(sysroot),PKG_CONFIG_LIBDIR=str(sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),LD_LIBRARY_PATH=str(sysroot/'usr/lib/x86_64-linux-gnu'),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',HOME=str(out),XDG_CONFIG_HOME=str(out/'config'),TMPDIR=str(tmp))
 return env

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','baseline','observation','sysroot','data','out'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.root;q=a.out;o=a.observation;b=a.baseline
 peak,reserve=64*1024**2,250*1024**2
 assert not q.exists() and shutil.disk_usage(q.parent).free>=peak+reserve
 old=json.loads((o/'receipt.json').read_text());assert old['status']=='PASS_BOUNDED_NATURAL_OBSERVATION' and all(old['checks'].values())
 source=obs.inv(r/'src');base=obs.inv(b/'src');assert source==old['source_sha256'] and obs.inv(o/'build/src')==old['instrumented_source_sha256']
 assert {n for n in base if source.get(n)!=base[n]}=={'render_mirror.c','global_projectile91_mirror.inc','tyrian2.c','entity_draw.c'}
 assert set(source)-set(base)=={'enemy_projectile145_mirror.inc','current_projectile145_payload_pins.h'}
 index=Path(subprocess.check_output(['git','--no-optional-locks','-C',str(r),'rev-parse','--path-format=absolute','--git-path','index'],text=True).strip());assert SHA(index)==old['index_sha256']
 inputs={**old['producer_sha256'],**old['objects_sha256'],**old['original_data_sha256'],**old['pack_target_sha256'],**old['external_header_sha256']}
 inputs.update({str(o/'receipt.json'):SHA(o/'receipt.json'),str(o/'build/opentyrian2000'):old['binary_sha256'],str(Path(__file__).resolve()):SHA(Path(__file__).resolve())})
 for n in ('tyrian2','entity_draw','game_probe'):inputs[str(o/'build'/(n+'.o'))]=SHA(o/'build'/(n+'.o'))
 for n in base:inputs[str(b/'src'/n)]=base[n]
 for n in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h'):
  inputs[str(b/'assets/hd/shared-menu-runs-v1'/n)]=SHA(b/'assets/hd/shared-menu-runs-v1'/n)
 assert all(SHA(Path(n))==h for n,h in inputs.items())
 sys.path.insert(0,str(r/'scripts'));import current_projectile145_compatibility as art
 art.load(r);mask=np.array(list(art.MASK))=='1';mask=mask.reshape(14,12)
 for n in art.input_paths(r):inputs[str(r/n)]=SHA(r/n)
 primary=Path(next(n for n in old['objects_sha256'] if n.endswith('/sprite.o'))).parent
 # Dependency closure of every reused primary object was verified in observer;
 # sprite and asset_debug now change only diagnostic outputs, so are replaced.
 reused=[f for f in sorted(primary.glob('*.o')) if f.stem not in ('render_mirror','sprite','asset_debug','tyrian2','entity_draw','game_probe')];assert len(reused)==80
 # Baseline production entity TU and all unchanged primary source are exact.
 from_primary=json.loads(Path(o.parent/'aircraft170-native-primary-20261028/native-receipt.json').read_text())['source_sha256']
 assert {n.removeprefix('src/'):h for n,h in from_primary.items()}==base
 q.mkdir();(q/'tmp').mkdir();build=q/'build';build.mkdir()
 texts={
  'current-render_mirror.c':renderer_text((o/'build/src/render_mirror.c').read_text()),
  'baseline-render_mirror.c':renderer_text((b/'src/render_mirror.c').read_text()),
  'baseline-tyrian2.c':baseline_shot_text((b/'src/tyrian2.c').read_text()),
  'sprite.c':sprite_text((b/'src/sprite.c').read_text()),
  'asset_debug.c':asset_text((b/'src/asset_debug.c').read_text())}
 for n,t in texts.items():(build/n).write_text(t)
 emitted=obs.inv(build)
 for n in ('sprite.c','asset_debug.c','game_probe.c'):assert (b/'src'/n).read_bytes()==(r/'src'/n).read_bytes()
 # Reuse the identical output-only game_probe filter object, never a new renderer in baseline.
 assert (o/'build/src/game_probe.c').read_text()==(b/'src/game_probe.c').read_text().replace('static unsigned int tick_limit = 600;',obs.LOG_FILTER+'\nstatic unsigned int tick_limit = 600;')
 env=environment(os.environ,a.sysroot,q,q/'tmp')
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 report=dict(status='RUNNING',scope=__doc__,source_sha256=source,baseline_source_sha256=base,inputs_sha256=inputs,instrumented_sha256=emitted,index_sha256=SHA(index),observation_receipt_sha256=SHA(o/'receipt.json'),commands=[],runs=[],peak_budget_bytes=peak,reserve_bytes=reserve,peak_allocated_sample=0,minimum_free_sample=shutil.disk_usage(q).free,sample_interval_seconds=.25,free_before=shutil.disk_usage(q).free)
 def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def check_budget():
  used=obs.blocks(q);free=shutil.disk_usage(q).free;report['peak_allocated_sample']=max(used,report['peak_allocated_sample']);report['minimum_free_sample']=min(free,report['minimum_free_sample'])
  assert used<=peak and free>=reserve,('budget',used,free)
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 def run(cmd,label,cwd,env):
  row=dict(argv=list(map(str,cmd)),label=label,cwd=str(cwd));report['commands'].append(row);save()
  with (q/(label+'.stdout')).open('wb') as stdout,(q/(label+'.stderr')).open('wb') as stderr:
   z=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=no_core);row['pid']=z.pid;save();start=time.monotonic()
   try:
    while z.poll() is None:check_budget();assert time.monotonic()-start<600,'timeout';time.sleep(.25)
   except BaseException:
    os.killpg(z.pid,signal.SIGTERM);z.wait();row['stopped']=True;raise
   finally:row.update(returncode=z.poll(),seconds=time.monotonic()-start);save()
   assert row['returncode']==0,(label,row['returncode'])
 save();start=time.monotonic()
 try:
  for name in texts:
   include=o/'build/src' if name.startswith('current-') else b/'src'
   flags=['-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(include)]
   run(['cc',*flags,'-c',build/name,'-o',build/(name.removesuffix('.c')+'.o')],name+'-compile',build,env)
  common=[*reused,build/'sprite.o',build/'asset_debug.o',o/'build/game_probe.o']
  for variant,extra in [('current',[build/'current-render_mirror.o',o/'build/tyrian2.o',o/'build/entity_draw.o']),('baseline',[build/'baseline-render_mirror.o',build/'baseline-tyrian2.o',primary/'entity_draw.o'])]:
   assert len(common+extra)==86
   run(['cc',*common,*extra,*libs,'-lm','-o',build/variant],variant+'-link',build,env)
  # Read-only symlink packs, all target bytes bound. Exactly one optional difference.
  for kind in ('present','missing'):
   pack=q/(kind+'-pack');pack.mkdir()
   for f in sorted((o/'pack').rglob('*')):
    if f.is_file() and not(kind=='missing' and f.name==art.name(1500145)):
     d=pack/f.relative_to(o/'pack');d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
  for kind in ('present','missing','baseline'):
   out=q/kind;cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 2x\nitem fullscreen -1\n');(out/'native-blend-writes.tsv').write_text(BLEND_HEADER)
   e=environment(os.environ,a.sysroot,out,q/'tmp');pack=q/('present-pack' if kind=='present' else 'missing-pack');exe=build/('baseline' if kind=='baseline' else 'current')
   cmd=[exe,'--data='+str(a.data),'--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=2','--asset-debug-tick=1158','--asset-debug-running','--render-ticks=1163','--render-assets='+str(pack),'--global-assets='+str(pack),'--asset-debug-capture','--asset-debug-capture-start=1162','--asset-debug-capture-count=1','--render-test=8']
   run(cmd,kind+'-game',out,e)
   captures={f.name:dict(sha256=SHA(f),bytes=f.stat().st_size) for f in sorted(out.glob('*.bmp'))};assert set(captures)=={'classic-1162.bmp','display-1162.bmp','asset-debug-window-1162.bmp'}
   archive=out/'captures.zip'
   with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zz:
    for name in captures:
     check_budget();Image.open(out/name).save((out/name).with_suffix('.png'));zz.write(out/name,name)
   # Byte equality of complete decompressed members, not just CRC/listing.
   with zipfile.ZipFile(archive) as zz:
    assert set(zz.namelist())==set(captures)
    for n,pin in captures.items():assert zz.read(n)==(out/n).read_bytes() and hashlib.sha256(zz.read(n)).hexdigest()==pin['sha256']
   recovery=dict(archive='captures.zip',archive_sha256=SHA(archive),members=captures,verification='full decompressed bytes equal actual BMP before removing only duplicate BMP',status='VERIFIED_LOSSLESS_DUPLICATES_COMPACTED')
   (out/'bmp-recovery-map.json').write_text(json.dumps(recovery,indent=2)+'\n')
   for name in captures:(out/name).unlink()
   report['runs'].append(dict(variant=kind,binary_sha256=SHA(exe),argv=list(map(str,cmd)),environment={k:e.get(k) for k in ('SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER','HOME','XDG_CONFIG_HOME','LD_LIBRARY_PATH')},control_keys_present=[k for k in e if k.startswith(('AIRCRAFT170_','SHARED170_','TYRIAN_CYAN_BORROW','TYRIAN_GAME_PROBE','OT_','PROJECTILE145_'))],capture_recovery=recovery));check_budget();save()
  paths=[q/k for k in ('present','missing','baseline')]
  names=('state.tsv','enemy-projectiles.tsv','collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv','native-blend-writes.tsv','native-game-screen.index8','native-vga-screen.index8','native-palette.rgb','actual145-native.tsv')
  equal={n:len({(x/n).read_bytes() for x in paths})==1 for n in names};assert all(equal.values()),equal
  assert [(paths[0]/n).stat().st_size for n in ('native-game-screen.index8','native-vga-screen.index8','native-palette.rgb')]==[64000,64000,768]
  def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
  shots=[x for x in rows(paths[0]/'actual145-native.tsv') if x['kind']=='draw' and int(x['tick'])==TICK and x['index']=='145'];assert len(shots)==1 and (int(shots[0]['x']),int(shots[0]['y']))==(239,82)
  assert any(x['kind']=='emit' and x['weapon']=='4' and x['actor']=='194' and x['link']=='3' and int(x['tick'])==TICK for x in rows(paths[0]/'actual145-native.tsv'))
  assert any(x['role']=='150' and x['index']=='145' and x['mirrored']=='1' and int(x['tick'])==TICK for x in rows(paths[0]/'scene-draw-commands.tsv'))
  pixels=[];frozen={};oldhd=0;opaque=0
  for name in ('classic-1162.png','display-1162.png','asset-debug-window-1162.png'):
   arrays=[np.array(Image.open(x/name).convert('RGB')) for x in paths];after,before,baseline=arrays;factor=after.shape[1]//320;assert after.shape==before.shape==baseline.shape==(200*factor,320*factor,3)
   assert factor=={'classic-1162.png':1,'display-1162.png':8,'asset-debug-window-1162.png':2}[name]
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
    classic=np.array(Image.open(paths[0]/'classic-1162.png').convert('RGB'));classic8=np.repeat(np.repeat(classic,8,0),8,1)
    oldhd=int((np.any(before!=classic8,axis=2)&~support).sum());assert oldhd>512
    raw=np.frombuffer((r/art.ROOT/art.name(1500145)).read_bytes()[28:],dtype=np.uint8).reshape(112,96,4)
    x,y=(int(shots[0]['x'])-24)*8,int(shots[0]['y'])*8;region=after[y:y+112,x:x+96];orig=classic8[y:y+112,x:x+96]
    opaque=int(((raw[:,:,3]==255)&np.all(region==raw[:,:,:3],axis=2)&np.any(region!=orig,axis=2)).sum());assert opaque==130
  report.update(status='PASS_NATURAL_TICK1162_TRIPLE',native_equal=equal,frozen_missing_equal=frozen,pixels=pixels,old_hd_outside145_not_classic=oldhd,opaque_authored_not_classic=opaque,native_blend_writes=len(rows(paths[0]/'native-blend-writes.tsv')),actual_shots=shots,internal_density=8,physical_output_scale=2,controlled_emitter_or_pose=False,controlled_player_input='unchanged existing asset-debug stationary/no-firing input')
 except BaseException as e:
  report.update(status='FAIL_RETAINED',error=repr(e));raise
 finally:
  checks=dict(source_unchanged=obs.inv(r/'src')==source,baseline_unchanged=obs.inv(b/'src')==base,index_unchanged=SHA(index)==old['index_sha256'],inputs_unchanged=all(SHA(Path(n))==h for n,h in inputs.items()),instrumented_unchanged=all(SHA(build/n)==h for n,h in emitted.items()))
  report.update(checks=checks,seconds=time.monotonic()-start,final_allocated_bytes=obs.blocks(q),free_after=shutil.disk_usage(q).free)
  if not all(checks.values()):report['status']='FAIL_BINDING'
  save();print(json.dumps({k:report.get(k) for k in ('status','pixels','native_equal','frozen_missing_equal','old_hd_outside145_not_classic','opaque_authored_not_classic','native_blend_writes','checks','peak_allocated_sample','minimum_free_sample','final_allocated_bytes','free_after','error')},indent=2))
 assert report['status']=='PASS_NATURAL_TICK1162_TRIPLE'
if __name__=='__main__':main()
