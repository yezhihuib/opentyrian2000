#!/usr/bin/env python3
"""Natural ShapesY356 E1 physical12/map3 tick414 comparison.

Exact source-derived bounded window includes bronze356 and unchanged old28.
Only unconditional native INDEX8/palette/blend audit instrumentation is active;
no actor replacement, pose override or tile placement environment flag is set.
Same audit transformations are used in current and qualified169 binaries.
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
from aircraft170_controlled_gameplay import verify_instrumented_build

def natural_environment(env):
 # A parent shell's controlled flag must never turn a natural receipt into a
 # secretly controlled run. Copy first so caller state remains untouched.
 clean=dict(env);clean.pop('AIRCRAFT170_DIFFERENTIAL_POSE',None)
 return clean

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('sysroot','data','base-pack','out'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--build',type=Path,required=True)
 p.add_argument('--density',type=int,choices=(4,8),default=8)
 p.add_argument('--output-scale',type=int,choices=(2,4),default=4)
 p.add_argument('--native-capture',action='store_true',help='Also capture native INDEX8 and internal-density RGB, not a physical8x window')
 p.add_argument('--episode',type=int,choices=(1,),default=1)
 p.add_argument('--level',type=int,choices=(12,),default=12)
 p.add_argument('--start',type=int,choices=(414,425),default=414);p.add_argument('--count',type=int,default=1)
 p.add_argument('--baseline-build',type=Path,required=True,help='Optional frozen old-family build for missing-new byte equality')
 p.add_argument('--baseline-root',type=Path,required=True,help='Required with baseline-build: exact frozen qualified source checkout')
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() if isinstance(v,Path) else v for k,v in vars(a).items()})
 assert a.start in (414,425) and a.count==1 and a.density==8 and a.native_capture,'bounded natural mixed tile window, exact8x payload, all native captures required'
 sys.path.insert(0,str(a.root/'scripts'))
 from check_shapesy_bronze356_pins import verify
 import current_shapesy_bronze356_compatibility as selected
 verify(a.root,a.data);assert len(selected.load(a.root))==1
 q=a.out;q.mkdir(exist_ok=False);r=a.root;initial=inventory(r);driver_before=SHA(Path(__file__));helper_before=SHA(Path(__file__).with_name('aircraft170_controlled_gameplay.py'))
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
 assets=sorted((r/'assets/hd/current-compat/shapesy-bronze356').glob('*.hda'));assert len(assets)==1
 for f in assets:
  target=pack/f.name;target.parent.mkdir(exist_ok=True);assert not target.exists();target.symlink_to(f.resolve())
 results=[]
 for variant in (('missing','present','frozen') if a.baseline_build else ('missing','present')):
  out=q/variant;out.mkdir();cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {a.output_scale}x\nitem fullscreen -1\n')
  use=pack if variant=='present' else old_pack
  run_exe=a.baseline_build/'opentyrian2000' if variant=='frozen' else exe
  e={**natural_environment(env),'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'TYRIAN_CYAN_BORROW_TRACE':'1','AIRCRAFT170_DIFFERENTIAL_TICK':str(a.start)}
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
  results.append(dict(variant=variant,environment={k:e.get(k) for k in ('SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER','HOME','XDG_CONFIG_HOME','LD_LIBRARY_PATH','TYRIAN_CYAN_BORROW_TRACE','AIRCRAFT170_DIFFERENTIAL_TICK')},controlled_pose_key_present='AIRCRAFT170_DIFFERENTIAL_POSE' in e,density=a.density,physical_output_scale=a.output_scale,capture_sizes={f.name:list(Image.open(f).size) for f in out.glob('*.png')},exit=z.returncode,argv=cmd,captures=captures,inputs=inputs,unchanged=inputs==after_inputs,inputs_after=after_inputs,archive_sha256=SHA(archive)))
  (q/'runs.json').write_text(json.dumps(results,indent=2)+'\n');assert z.returncode==0 and len(captures)==a.count*(3 if a.native_capture else 1)
 # Only logged native layer1 tile footprints define the permitted HD delta.
 left=q/'missing';right=q/'present';frozen=q/'frozen'
 names=('state.tsv','enemy-projectiles.tsv','collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv','native-blend-writes.tsv','native-game-screen.index8','native-vga-screen.index8','native-palette.rgb')
 native={n:(left/n).read_bytes()==(right/n).read_bytes()==(frozen/n).read_bytes() for n in names}
 rows=list(csv.DictReader((right/'asset-debug-materials.tsv').open(),delimiter='\t'))
 target=[x for x in rows if int(x['tick'])==a.start and x['category']=='terrain-layer1' and x['sheet'].lower()=='shapesy.dat' and int(x['id'])==356]
 from current_shapesy_platform_compatibility import IDS as old_ids
 oldrows=[x for x in rows if int(x['tick'])==a.start and x['category']=='terrain-layer1' and x['sheet'].lower()=='shapesy.dat' and int(x['id']) in old_ids]
 assert target and oldrows,'source-derived natural mixed356/old28 window was not drawn'
 pixels=[];frozen_equal={};old_hd=[];bronze_hd=[]
 for file in sorted(left.glob('*.png')):
  before=np.array(Image.open(file).convert('RGB'));after=np.array(Image.open(right/file.name).convert('RGB'));factor=before.shape[1]//320
  assert before.shape==after.shape==(200*factor,320*factor,3) and factor in (1,2,4,8)
  delta=np.any(before!=after,axis=2);support=np.zeros(delta.shape,dtype=bool)
  for row in target:
   x=int(row['x'])-24;y=int(row['y']);x0=max(0,x);x1=min(264,x+24);y0=max(0,y);y1=min(184,y+28)
   if x0<x1 and y0<y1:support[y0*factor:y1*factor,x0*factor:x1*factor]=True
  pixels.append({'file':file.name,'changed':int(delta.sum()),'outside356':int((delta&~support).sum())})
  frozen_equal[file.name]=file.read_bytes()==(frozen/file.name).read_bytes()
  if file.name.startswith('display-'):
   assert factor==8
   classic=np.array(Image.open(left/('classic-'+str(a.start).zfill(4)+'.png')).convert('RGB'))
   assert classic.shape==(200,320,3);classic8=np.repeat(np.repeat(classic,8,axis=0),8,axis=1)
   raw=(pack/'terrain-shapesy-356-8.hda').read_bytes();assert len(raw)==28+192*224*4
   rgba356=np.frombuffer(raw[28:],dtype=np.uint8).reshape(224,192,4);assert np.all(rgba356[:,:,3]==255)
   for row in target:
    x=int(row['x'])-24;y=int(row['y']);matched=0
    for yy in range(max(0,-y*8),min(224,(184-y)*8)):
     lo=max(0,-x*8);hi=min(192,(264-x)*8)
     if lo>=hi:continue
     shown=after[y*8+yy,x*8+lo:x*8+hi];prior=before[y*8+yy,x*8+lo:x*8+hi]
     matched+=int((np.all(shown==rgba356[yy,lo:hi,:3],axis=1)&np.any(shown!=prior,axis=1)).sum())
    bronze_hd.append({'x':x,'y':y,'changed_pixels_matching_authored356':matched})
   # Exact rendered authored pixels on old28 prove its continued independent
   # HD contribution in missing356, rather than merely a loaded old asset.
   for row in oldrows:
    tile=int(row['id']);raw=(pack/f'terrain-shapesy-{tile}-8.hda').read_bytes();assert len(raw)==28+192*224*4
    rgba=np.frombuffer(raw[28:],dtype=np.uint8).reshape(224,192,4);x=int(row['x'])-24;y=int(row['y']);matched=0
    for yy in range(max(0,-y*8),min(224,(184-y)*8)):
     lo=max(0,-x*8);hi=min(192,(264-x)*8)
     if lo>=hi:continue
     strip=before[y*8+yy,x*8+lo:x*8+hi];expected=rgba[yy,lo:hi]
     matched+=int((np.all(strip==expected[:,:3],axis=1)&(expected[:,3]==255)&np.any(strip!=classic8[y*8+yy,x*8+lo:x*8+hi],axis=1)).sum())
    old_hd.append({'id':tile,'x':x,'y':y,'authored_opaque_pixels_matched_missing356':matched})
 frames={v:[x for x in csv.DictReader((q/v/'frames.tsv').open(),delimiter='\t') if int(x['tick'])==a.start] for v in ('missing','present','frozen')}
 frame_hd=all(v and all(x['reason']=='hd-ordered' and int(x['coverage_mismatch'])==0 for x in v) for v in frames.values())
 expected_sizes={'asset-debug-window':(320*a.output_scale,200*a.output_scale),'classic':(320,200),'display':(320*a.density,200*a.density)}
 sizes_ok=all(tuple(size)==expected_sizes[next(k for k in expected_sizes if name.startswith(k+'-'))] for run in results for name,size in run['capture_sizes'].items())
 classic_equal=all(results[0]['captures'][n]==results[1]['captures'][n]==results[2]['captures'][n] for n in results[0]['captures'] if n.startswith('classic-'))
 helper=Path(__file__).with_name('aircraft170_controlled_gameplay.py');helper_after=SHA(helper)
 okay=all(native.values()) and all(frozen_equal.values()) and all(x['outside356']==0 for x in pixels) and any(x['changed']>0 for x in pixels) and any(x['authored_opaque_pixels_matched_missing356']>512 for x in old_hd) and any(x['changed_pixels_matching_authored356']>512 for x in bronze_hd) and frame_hd and sizes_ok and classic_equal
 okay=okay and initial==inventory(r) and baseline_source==inventory(a.baseline_root) and all(x['unchanged'] for x in results) and driver_before==SHA(Path(__file__)) and helper_before==helper_after and helpers=={n:SHA(Path(n)) for n in helpers}
 okay=okay and (right/'native-palette.rgb').stat().st_size==768 and all((right/n).stat().st_size==64000 for n in ('native-game-screen.index8','native-vga-screen.index8'))
 report={'status':'PASS' if okay else 'FAIL','scope':__doc__,'episode':1,'physical_level':12,'map':3,'tick':a.start,'natural_tile_placement':True,'controlled_actor_or_pose':False,'source_before':initial,'source_after':inventory(r),'baseline_source':baseline_source,'native_equal_all_three':native,'missing_equals_qualified169':frozen_equal,'classic_index8_capture_equal':classic_equal,'output_sizes_valid':sizes_ok,'pixels':pixels,'visible356':target,'visible_old28':oldrows,'old28_hd_in_missing356':old_hd,'authored356_hd_contribution':bronze_hd,'all_three_whole_frame_hd':frame_hd,'frames':frames,'driver_before_sha256':driver_before,'driver_after_sha256':SHA(Path(__file__)),'helper_before_sha256':helper_before,'helper_after_sha256':helper_after,'native_capture':a.native_capture,'physical_output_scale':a.output_scale,'internal_density':a.density,'runs':results}
 (q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True);assert okay
if __name__=='__main__':main()
