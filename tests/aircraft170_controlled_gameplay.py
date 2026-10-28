#!/usr/bin/env python3
"""Controlled original170 E1L12 comparison, never a natural encounter claim.

Identical external-only allocation/pose/INDEX8/palette/blend instrumentation is
used in new and qualified169 builds. Production checkouts stay byte-exact. The predecessor controlled169 recipe is SHA-locked in the new authoring test;
this driver only consumes preverified test-only instrumented builds.
"""
from pathlib import Path
import argparse, csv, hashlib, importlib, json, os, re, shutil, subprocess, sys, zipfile
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(root):
 return {p.relative_to(root).as_posix():SHA(p) for p in sorted((root/'src').rglob('*')) if p.is_file()}
def tree_inputs(root):
 # Symlink-backed test packs are allowed, but every path, target and byte is bound.
 return {str(f):dict(sha256=SHA(f),resolved=str(f.resolve()),symlink=f.is_symlink())
         for f in sorted(root.rglob('*')) if f.is_file()}
INSTRUMENTED_PATHS=('src/tyrian2.c','src/newshf_identity_validation.inc','src/sprite.c','src/render_mirror.c')
def instrument_texts(original):
 result=dict(original)
 def patch(name,marker,insertion):
  body=result[name];assert body.count(marker)==1,('instrumentation marker drift',name,marker)
  result[name]=body.replace(marker,insertion)
 marker='uint JE_makeEnemy(struct JE_SingleEnemyType *enemy, Uint16 eDatI, Sint16 uniqueShapeTableI)\n{'
 patch('src/tyrian2.c',marker,marker+'\n if(getenv("AIRCRAFT170_DIFFERENTIAL_POSE")&&eDatI>=302&&eDatI<=308)eDatI=170;')
 marker='void render_mirror_newshf_validation_observe(unsigned s)\n{'
 patch('src/newshf_identity_validation.inc',marker,marker+'\n if(s<100&&enemy[s].enemytype==170&&getenv("AIRCRAFT170_DIFFERENTIAL_POSE"))enemy[s].enemycycle=(unsigned)atoi(getenv("AIRCRAFT170_DIFFERENTIAL_POSE"));')
 patch('src/sprite.c','#include "asset_debug.h"','#include "asset_debug.h"\n#include "game_probe.h"')
 patch('src/sprite.c','{ *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0); render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }','{ unsigned before=*pixels; static FILE *trace; if(!trace){trace=fopen("native-blend-writes.tsv","w");assert(trace);fprintf(trace,"tick\\tw\\th\\tpitch\\tindex\\torigin_x\\torigin_y\\twrite_x\\twrite_y\\tbefore\\tsource\\tafter\\n");}\n *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0);\n long offset=pixels-(Uint8*)surface->pixels;\n fprintf(trace,"%u\\t%d\\t%d\\t%d\\t%u\\t%d\\t%d\\t%ld\\t%ld\\t%u\\t%u\\t%u\\n",game_probe_tick,surface->w,surface->h,surface->pitch,(unsigned)index,x,y,offset%surface->pitch,offset/surface->pitch,before,(unsigned)*data,(unsigned)*pixels);\n render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }')
 marker='void render_mirror_finish(MirrorOutputKind kind,int lightx,int lighty)\n{'
 patch('src/render_mirror.c',marker,marker+'\n if(getenv("AIRCRAFT170_DIFFERENTIAL_TICK")&&game_probe_tick==(unsigned)atoi(getenv("AIRCRAFT170_DIFFERENTIAL_TICK"))){\n  SDL_Surface *surfaces[2]={game_screen,VGAScreenSeg};const char *names[2]={"native-game-screen.index8","native-vga-screen.index8"};\n  for(unsigned k=0;k<2;k++){SDL_Surface *v=surfaces[k];if(!v||!v->format||v->format->BytesPerPixel!=1)abort();FILE *f=fopen(names[k],"wb");if(!f)abort();for(int y=0;y<v->h;y++)if(fwrite((Uint8*)v->pixels+y*v->pitch,1,v->w,f)!=(size_t)v->w)abort();fclose(f);}\n  FILE *f=fopen("native-palette.rgb","wb");if(!f)abort();for(unsigned i=0;i<256;i++){Uint8 bytes[3]={rgb_palette[i]>>16,rgb_palette[i]>>8,rgb_palette[i]};if(fwrite(bytes,1,3,f)!=3)abort();}fclose(f);\n }\n')
 return result

def apply_instrumentation(build):
 for name,text in instrument_texts({n:(build/n).read_text() for n in INSTRUMENTED_PATHS}).items():(build/name).write_text(text)

def verify_instrumented_build(root,build,receipt):
 assert receipt['status']=='PASS' and receipt['production_source']==inventory(root)
 expected=instrument_texts({n:(root/n).read_text() for n in INSTRUMENTED_PATHS})
 for name,h in receipt['source_before'].items():
  assert SHA(build/name)==h,('compiled input drift',name)
  if name.startswith('src/'):
   assert (build/name).read_bytes()==(expected[name].encode() if name in expected else (root/name).read_bytes()),('wrong instrumentation',name)
 assert {n for n in receipt['source_before'] if n.startswith('src/')}==set(receipt['production_source'])
 assert SHA(build/'opentyrian2000')==receipt['binary_sha256']

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('sysroot','data','base-pack','out'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--build',type=Path,required=True)
 p.add_argument('--density',type=int,choices=(4,8),default=8)
 p.add_argument('--output-scale',type=int,choices=(2,4),default=4)
 p.add_argument('--native-capture',action='store_true',help='Also capture native INDEX8 and internal-density RGB, not a physical8x window')
 p.add_argument('--episode',type=int,choices=(1,),default=1)
 p.add_argument('--level',type=int,choices=(12,),default=12)
 p.add_argument('--pose',type=int,choices=(1,2,3),required=True)
 p.add_argument('--start',type=int,default=362);p.add_argument('--count',type=int,default=1)
 p.add_argument('--baseline-build',type=Path,required=True,help='Optional frozen old-family build for missing-new byte equality')
 p.add_argument('--baseline-root',type=Path,required=True,help='Required with baseline-build: exact frozen qualified source checkout')
 p.add_argument('--expect-all-poses',action='store_true',help='Require all three natural original bases in captured window')
 p.add_argument('--expect-aircraft',action='store_true',help='Require target body draw and visible scoped HD difference')
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() if isinstance(v,Path) else v for k,v in vars(a).items()})
 assert a.start==362 and a.count==1,'bounded controlled window only'
 sys.path.insert(0,str(a.root/'scripts'))
 from check_aircraft170_newshf_pins import verify
 import current_aircraft170_newshf_compatibility as selected
 verify(a.root,a.data);assert len(selected.load(a.root))==3
 q=a.out;q.mkdir(exist_ok=False);r=a.root;initial=inventory(r);driver_before=SHA(Path(__file__))
 helper_names=tuple(sorted(f.name for f in (r/'scripts').glob('*.py')))
 helpers={str(r/'scripts'/n):SHA(r/'scripts'/n) for n in helper_names}
 baseline_source=None
 if a.baseline_build:
  assert a.baseline_root is not None,'baseline-root required to bind qualified baseline source'
  baseline_source=inventory(a.baseline_root)
  baseline=json.loads((a.baseline_build/'build-receipt.json').read_text())
  verify_instrumented_build(a.baseline_root,a.baseline_build,baseline)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu')}
 build=a.build or q/'build'
 if a.build:
  receipt=json.loads((build/'build-receipt.json').read_text())
  verify_instrumented_build(r,build,receipt)
 exe=build/'opentyrian2000';pack=q/'pack';pack.mkdir();old_pack=q/'old-pack';old_pack.mkdir()
 for f in a.base_pack.rglob('*'):
  if f.is_file():
   d=pack/f.relative_to(a.base_pack);d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
 # Earlier scene-specific packs can omit families not visible in that scene.
 # Bind and include all 40 prior NEWSHF/NEWSHI resources in BOTH variants.
 sys.path.insert(0,str(r/'scripts'));prior=[]
 for family in ('newshf','linked_newshf','dualmissile_newshf','turret_newshf','large_newshi','scout164_newshf','fighter165_newshf','interceptor166_newshf','aircraft169_newshf'):
  mapping=importlib.import_module('current_'+family+'_compatibility').load(r)
  for destination,row in mapping.items():
   assert destination.startswith('assets/global/')
   src=r/row['source_path'];target=pack/destination.removeprefix('assets/global/')
   if target.exists():assert SHA(target)==SHA(src),('stale prior resource',destination)
   else:target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(src.resolve())
   prior.append(dict(destination=destination,source=str(src),sha256=SHA(src)))
 assert len(prior)==40
 # Actual Talon-copy fixtures require the canonical content-addressed aliases.
 talon=sorted((r/'assets/hd/current-compat/talon').glob('*.hda'));assert len(talon)==13
 for f in talon:
  target=pack/'content'/(SHA(f)+'.hda');target.parent.mkdir(exist_ok=True)
  if target.exists():assert SHA(target)==SHA(f)
  else:target.symlink_to(f.resolve())
 (q/'prior-family-pack.json').write_text(json.dumps(prior,indent=2)+'\n')
 for f in pack.rglob('*'):
  if f.is_file():
   d=old_pack/f.relative_to(pack);d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
 assets=sorted((r/'assets/hd/current-compat/newshf-aircraft170').glob('*.hda'));assert len(assets)==3
 for f in assets:
  target=pack/'newshf-aircraft170'/f.name;target.parent.mkdir(exist_ok=True);assert not target.exists();target.symlink_to(f.resolve())
 results=[]
 for variant in (('missing','present','frozen') if a.baseline_build else ('missing','present')):
  out=q/variant;out.mkdir();cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {a.output_scale}x\nitem fullscreen -1\n')
  use=pack if variant=='present' else old_pack
  run_exe=a.baseline_build/'opentyrian2000' if variant=='frozen' else exe
  e={**env,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'TYRIAN_CYAN_BORROW_TRACE':'1','AIRCRAFT170_DIFFERENTIAL_POSE':str(a.pose),'AIRCRAFT170_DIFFERENTIAL_TICK':str(a.start)}
  cmd=[str(run_exe),f'--data={a.data}','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom',f'--asset-debug-episode={a.episode}',f'--asset-debug-level={a.level}',f'--asset-debug-tick={a.start}','--asset-debug-running',f'--render-ticks={a.start+a.count}',f'--render-assets={use}',f'--global-assets={use}','--asset-debug-capture',f'--asset-debug-capture-start={a.start}',f'--asset-debug-capture-count={a.count}','--asset-debug-window-only',f'--render-test={a.density}']
  if a.native_capture:cmd.remove('--asset-debug-window-only')
  run_build=a.baseline_build if variant=='frozen' else build
  inputs=dict(binary={str(run_exe):SHA(run_exe)},instrumented_source=inventory(run_build),native_objects=tree_inputs(run_build/'obj'),pack=tree_inputs(use),game_data=tree_inputs(a.data))
  (out/'inputs-before.json').write_text(json.dumps(inputs,indent=2)+'\n')
  with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as err:z=subprocess.run(cmd,cwd=out,env=e,stdout=f,stderr=err,timeout=600)
  captures={f.name:SHA(f) for f in out.glob('*.bmp')};archive=out/'captures.zip'
  with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zz:
   for f in sorted(out.glob('*.bmp')):Image.open(f).save(f.with_suffix('.png'));zz.write(f,f.name)
  with zipfile.ZipFile(archive) as zz:assert set(zz.namelist())==set(captures) and all(hashlib.sha256(zz.read(n)).hexdigest()==h for n,h in captures.items())
  for f in out.glob('*.bmp'):f.unlink()
  after_inputs=dict(binary={str(run_exe):SHA(run_exe)},instrumented_source=inventory(run_build),native_objects=tree_inputs(run_build/'obj'),pack=tree_inputs(use),game_data=tree_inputs(a.data))
  (out/'inputs-after.json').write_text(json.dumps(after_inputs,indent=2)+'\n')
  results.append(dict(variant=variant,density=a.density,physical_output_scale=a.output_scale,capture_sizes={f.name:list(Image.open(f).size) for f in out.glob('*.png')},exit=z.returncode,argv=cmd,captures=captures,inputs=inputs,unchanged=inputs==after_inputs,inputs_after=after_inputs,archive_sha256=SHA(archive)))
  (q/'runs.json').write_text(json.dumps(results,indent=2)+'\n');assert z.returncode==0 and len(captures)==a.count*(3 if a.native_capture else 1)
 # Decode original sprite-quartet support without publishing original pixels.
 from build_newshf_prototype_pins import decode
 raw=(a.data/'newshf.shp').read_bytes();bases=(53,15,91)
 masks={b+q:np.frombuffer(decode(raw,b+q)[168:],dtype=np.uint8).reshape(14,12)>0
        for b in bases for q in (0,1,19,20)}
 left=q/'missing';right=q/'present'
 native={n:(left/n).read_bytes()==(right/n).read_bytes() for n in ('state.tsv','enemy-projectiles.tsv','collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv','native-blend-writes.tsv','native-game-screen.index8','native-vga-screen.index8','native-palette.rgb')}
 blend_raw_equal=(left/'blend-writes.tsv').read_bytes()==(right/'blend-writes.tsv').read_bytes()
 rows=list(csv.DictReader((right/'asset-debug-materials.tsv').open(),delimiter='\t'));pixels=[];pose_changed={b:0 for b in bases}
 for f in sorted(left.glob('*.png')):
  delta=np.any(np.array(Image.open(f).convert('RGB'))!=np.array(Image.open(right/f.name).convert('RGB')),axis=2);support=np.zeros(delta.shape,dtype=bool);tick=int(re.search(r'(\d+)\.png$',f.name).group(1))
  pose_support={b:np.zeros(delta.shape,dtype=bool) for b in bases}
  factor=delta.shape[1]//320;assert factor in (1,2,4,8) and delta.shape==(200*factor,320*factor)
  for row in rows:
   if int(row['tick'])!=tick or row['category']!='enemy' or row['sheet'].lower()!='newshf.shp' or int(row['id']) not in bases or int(row['tile_id']) not in masks:continue
   for ny,nx in zip(*np.where(masks[int(row['tile_id'])])):
    x=int(row['x'])-24+int(nx);y=int(row['y'])+int(ny)
    if 0<=x<264 and 0<=y<184:
     support[y*factor:(y+1)*factor,x*factor:(x+1)*factor]=True
     pose_support[int(row['id'])][y*factor:(y+1)*factor,x*factor:(x+1)*factor]=True
  per_pose={b:int((delta&mask).sum()) for b,mask in pose_support.items()}
  for b,n in per_pose.items():pose_changed[b]+=n
  pixels.append(dict(file=f.name,changed=int(delta.sum()),outside_support=int((delta&~support).sum()),per_pose_changed=per_pose))
 text=(right/'stderr.log').read_text();borrows=re.findall(r'CYAN_AIRCRAFT_BORROW[^\n]*',text)
 objects_before={str(f):SHA(f) for f in (build/'obj').rglob('*') if f.is_file()}
 native_blend_writes=len((right/'native-blend-writes.tsv').read_text().splitlines())-1
 native_index8_sizes={n:(right/n).stat().st_size for n in ('native-game-screen.index8','native-vga-screen.index8')}
 okay=(right/'native-palette.rgb').stat().st_size==768 and native_blend_writes>0 and all(n==64000 for n in native_index8_sizes.values()) and all(native.values()) and all(x['outside_support']==0 for x in pixels) and initial==inventory(r) and all(x['unchanged'] for x in results)
 drawn={int(row['id']) for row in rows if a.start<=int(row['tick'])<a.start+a.count and row['category']=='enemy' and row['sheet'].lower()=='newshf.shp' and int(row['id']) in bases}
 expected_sizes={'asset-debug-window':(320*a.output_scale,200*a.output_scale),'classic':(320,200),'display':(320*a.density,200*a.density)}
 sizes_ok=all(tuple(size)==expected_sizes[next(k for k in expected_sizes if name.startswith(k+'-'))] for run in results for name,size in run['capture_sizes'].items())
 classic_equal=all((left/f.name).read_bytes()==(right/f.name).read_bytes() for f in left.glob('classic-*.png')) and all(results[0]['captures'][n]==results[1]['captures'][n] for n in results[0]['captures'] if n.startswith('classic-'))
 frozen_equal={}
 if a.baseline_build:
  frozen=q/'frozen'
  for f in left.glob('*.png'):frozen_equal[f.name]=f.read_bytes()==(frozen/f.name).read_bytes()
  for name in native:frozen_equal[name]=(left/name).read_bytes()==(frozen/name).read_bytes()
 helpers_after={n:SHA(Path(n)) for n in helpers}
 okay=okay and helpers==helpers_after and sizes_ok and classic_equal and all(frozen_equal.values()) and SHA(Path(__file__))==driver_before and (baseline_source is None or baseline_source==inventory(a.baseline_root))
 if a.expect_aircraft:okay=okay and bool(drawn) and any(x['changed'] for x in pixels)
 frames=list(csv.DictReader((right/'frames.tsv').open(),delimiter='\t'))
 visible_frames=[f for f in frames if a.start<=int(f['tick'])<a.start+a.count]
 frame_hd_ok=bool(visible_frames) and all(f['reason']=='hd-ordered' and int(f['coverage_mismatch'])==0 for f in visible_frames)
 if a.expect_aircraft:okay=okay and frame_hd_ok
 if a.expect_all_poses:raise AssertionError('one controlled pose per invocation, never claim natural all-pose capture')
 okay=okay and drawn=={bases[a.pose-1]} and pose_changed[bases[a.pose-1]]>0 and frame_hd_ok
 report=dict(native_blend_writes=native_blend_writes,native_index8_sizes=native_index8_sizes,controlled=True,controlled_pose=a.pose,natural_gameplay_claimed=False,instrumented_source=receipt['source_before'],production_source=initial,native_objects_after=objects_before,per_pose_changed=pose_changed,visible_frames=visible_frames,whole_frame_hd_valid=frame_hd_ok,helpers_before=helpers,helpers_after=helpers_after,status='PASS' if okay else 'FAIL',internal_density=a.density,physical_output_scale=a.output_scale,native_capture=a.native_capture,baseline_source=baseline_source,driver_sha256=driver_before,driver_after_sha256=SHA(Path(__file__)),native_equal=native,owner_dependent_blend_log_equal=blend_raw_equal,blend_log_limitation="Existing blend-writes.tsv omits owner-handled writes; raw differences retained, not a complete native-write audit",classic_indexed_capture_equal=classic_equal,output_sizes_valid=sizes_ok,drawn_aircraft_bases=sorted(drawn),frozen_missing_new_equal=frozen_equal,pixels=pixels,aircraft_cyan_consumption=borrows,source_before=initial,source_after=inventory(r),data_sha256=SHA(a.data/'newshf.shp'),episode=a.episode,physical_level=a.level,scope='Explicitly controlled original170 allocation/pose on E1L12, identical instrumentation in present/missing; scoped HD delta plus unconditional native INDEX8/palette/blend/state/RNG equality; NOT natural170 gameplay')
 (q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True);assert okay
if __name__=='__main__':main()
