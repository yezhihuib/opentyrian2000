#!/usr/bin/env python3
"""Actual record166 bank10 present/missing comparison with exact external-input binding.

Natural E5L4 covers base87/89 at tick180 and base85 at tick205;
all three are not simultaneous. A 154–220 capture spans all three; instrumented
typed-underlay diagnostics remain separate. Original game data remains outside the checkout.
No Windows or full-campaign acceptance is implied.
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
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('sysroot','data','base-pack','out'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--build',type=Path)
 p.add_argument('--density',type=int,choices=(4,8),default=8)
 p.add_argument('--output-scale',type=int,choices=(2,4),default=4)
 p.add_argument('--native-capture',action='store_true',help='Also capture native INDEX8 and internal-density RGB, not a physical8x window')
 p.add_argument('--episode',type=int,default=5)
 p.add_argument('--level',type=int,default=4)
 p.add_argument('--start',type=int,default=180);p.add_argument('--count',type=int,default=1)
 p.add_argument('--baseline-build',type=Path,help='Optional frozen old-family build for missing-new byte equality')
 p.add_argument('--baseline-root',type=Path,help='Required with baseline-build: exact frozen qualified source checkout')
 p.add_argument('--expect-all-poses',action='store_true',help='Require all three natural original bases in captured window')
 p.add_argument('--expect-interceptor',action='store_true',help='Require target body draw and visible scoped HD difference')
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() if isinstance(v,Path) else v for k,v in vars(a).items()})
 q=a.out;q.mkdir(exist_ok=False);r=a.root;initial=inventory(r);driver_before=SHA(Path(__file__))
 helper_names=tuple(sorted(f.name for f in (r/'scripts').glob('*.py')))
 helpers={str(r/'scripts'/n):SHA(r/'scripts'/n) for n in helper_names}
 baseline_source=None
 if a.baseline_build:
  assert a.baseline_root is not None,'baseline-root required to bind qualified baseline source'
  baseline_source=inventory(a.baseline_root)
  baseline=json.loads((a.baseline_build/'build-receipt.json').read_text())
  assert baseline['status']=='PASS' and SHA(a.baseline_build/'opentyrian2000')==baseline['binary_sha256']
  assert all(SHA(a.baseline_build/n)==h for n,h in baseline['source_before'].items())
  assert {n:h for n,h in baseline['source_before'].items() if n.startswith('src/')}==baseline_source
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu')}
 build=a.build or q/'build'
 if a.build:
  receipt=json.loads((build/'build-receipt.json').read_text())
  assert receipt['status']=='PASS' and all(receipt['source_before'].get(n)==h for n,h in initial.items())
  assert {n for n in receipt['source_before'] if n.startswith('src/')}==set(initial)
  assert SHA(build/'opentyrian2000')==receipt['binary_sha256']
 else:
  build.mkdir();files={**initial,'Makefile':SHA(r/'Makefile')}
  files.update({x.relative_to(r).as_posix():SHA(x) for x in (r/'assets/hd/shared-menu-runs-v1').glob('reconstructed*specs.h')})
  for n in files:
   dst=build/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/n,dst)
  cmd=['make','-j4','VCS_IDREV=printf interceptor166-hd-on','CPPFLAGS=-MMD -DNDEBUG -DNEWSHF_HD_COMPOSITOR=1 -I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),'LDFLAGS=-Wl,-rpath,'+str(a.sysroot/'usr/lib/x86_64-linux-gnu')]
  with (build/'build.log').open('w') as f:z=subprocess.run(cmd,cwd=build,env=env,stdout=f,stderr=subprocess.STDOUT)
  stable=initial==inventory(r) and all(SHA(build/n)==h for n,h in files.items())
  report=dict(status='PASS' if z.returncode==0 and stable else 'FAIL',source_before=files,source_after=inventory(r),source_unchanged=stable,command=cmd,exit=z.returncode,binary_sha256=SHA(build/'opentyrian2000') if (build/'opentyrian2000').exists() else None)
  (build/'build-receipt.json').write_text(json.dumps(report,indent=2)+'\n');assert report['status']=='PASS'
 exe=build/'opentyrian2000';pack=q/'pack';pack.mkdir();old_pack=q/'old-pack';old_pack.mkdir()
 for f in a.base_pack.rglob('*'):
  if f.is_file():
   d=pack/f.relative_to(a.base_pack);d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
 # Earlier scene-specific packs can omit families not visible in that scene.
 # Bind and include all 34 prior NEWSHF/NEWSHI resources in BOTH variants.
 sys.path.insert(0,str(r/'scripts'));prior=[]
 for family in ('newshf','linked_newshf','dualmissile_newshf','turret_newshf','large_newshi','scout164_newshf','fighter165_newshf'):
  mapping=importlib.import_module('current_'+family+'_compatibility').load(r)
  for destination,row in mapping.items():
   assert destination.startswith('assets/global/')
   src=r/row['source_path'];target=pack/destination.removeprefix('assets/global/')
   if target.exists():assert SHA(target)==SHA(src),('stale prior resource',destination)
   else:target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(src.resolve())
   prior.append(dict(destination=destination,source=str(src),sha256=SHA(src)))
 assert len(prior)==34
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
 assets=sorted((r/'assets/hd/current-compat/newshf-interceptor166').glob('*.hda'));assert len(assets)==3
 for f in assets:
  target=pack/'newshf-interceptor166'/f.name;target.parent.mkdir(exist_ok=True);assert not target.exists();target.symlink_to(f.resolve())
 results=[]
 for variant in (('missing','present','frozen') if a.baseline_build else ('missing','present')):
  out=q/variant;out.mkdir();cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {a.output_scale}x\nitem fullscreen -1\n')
  use=pack if variant=='present' else old_pack
  run_exe=a.baseline_build/'opentyrian2000' if variant=='frozen' else exe
  e={**env,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'TYRIAN_CYAN_BORROW_TRACE':'1'}
  cmd=[str(run_exe),f'--data={a.data}','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom',f'--asset-debug-episode={a.episode}',f'--asset-debug-level={a.level}',f'--asset-debug-tick={a.start}','--asset-debug-running',f'--render-ticks={a.start+a.count}',f'--render-assets={use}',f'--global-assets={use}','--asset-debug-capture',f'--asset-debug-capture-start={a.start}',f'--asset-debug-capture-count={a.count}','--asset-debug-window-only',f'--render-test={a.density}']
  if a.native_capture:cmd.remove('--asset-debug-window-only')
  inputs=dict(binary={str(run_exe):SHA(run_exe)},pack=tree_inputs(use),game_data=tree_inputs(a.data))
  (out/'inputs-before.json').write_text(json.dumps(inputs,indent=2)+'\n')
  with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as err:z=subprocess.run(cmd,cwd=out,env=e,stdout=f,stderr=err,timeout=600)
  captures={f.name:SHA(f) for f in out.glob('*.bmp')};archive=out/'captures.zip'
  with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zz:
   for f in sorted(out.glob('*.bmp')):Image.open(f).save(f.with_suffix('.png'));zz.write(f,f.name)
  with zipfile.ZipFile(archive) as zz:assert set(zz.namelist())==set(captures) and all(hashlib.sha256(zz.read(n)).hexdigest()==h for n,h in captures.items())
  for f in out.glob('*.bmp'):f.unlink()
  after_inputs=dict(binary={str(run_exe):SHA(run_exe)},pack=tree_inputs(use),game_data=tree_inputs(a.data))
  (out/'inputs-after.json').write_text(json.dumps(after_inputs,indent=2)+'\n')
  results.append(dict(variant=variant,density=a.density,physical_output_scale=a.output_scale,capture_sizes={f.name:list(Image.open(f).size) for f in out.glob('*.png')},exit=z.returncode,argv=cmd,captures=captures,inputs=inputs,unchanged=inputs==after_inputs,inputs_after=after_inputs,archive_sha256=SHA(archive)))
  (q/'runs.json').write_text(json.dumps(results,indent=2)+'\n');assert z.returncode==0 and len(captures)==a.count*(3 if a.native_capture else 1)
 # Decode original sprite-quartet support without publishing original pixels.
 from build_newshf_prototype_pins import decode
 raw=(a.data/'newshf.shp').read_bytes();bases=(87,85,89)
 masks={b+q:np.frombuffer(decode(raw,b+q)[168:],dtype=np.uint8).reshape(14,12)>0
        for b in bases for q in (0,1,19,20)}
 left=q/'missing';right=q/'present'
 native={n:(left/n).read_bytes()==(right/n).read_bytes() for n in ('state.tsv','enemy-projectiles.tsv','collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv')}
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
 okay=all(native.values()) and all(x['outside_support']==0 for x in pixels) and initial==inventory(r) and all(x['unchanged'] for x in results)
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
 if a.expect_interceptor:okay=okay and bool(drawn) and any(x['changed'] for x in pixels)
 frames=list(csv.DictReader((right/'frames.tsv').open(),delimiter='\t'))
 visible_frames=[f for f in frames if a.start<=int(f['tick'])<a.start+a.count]
 frame_hd_ok=bool(visible_frames) and all(f['reason']=='hd-ordered' and int(f['coverage_mismatch'])==0 for f in visible_frames)
 if a.expect_interceptor:okay=okay and frame_hd_ok
 if a.expect_all_poses:okay=okay and drawn==set(bases) and all(pose_changed.values())
 report=dict(per_pose_changed=pose_changed,visible_frames=visible_frames,whole_frame_hd_valid=frame_hd_ok,helpers_before=helpers,helpers_after=helpers_after,status='PASS' if okay else 'FAIL',internal_density=a.density,physical_output_scale=a.output_scale,native_capture=a.native_capture,baseline_source=baseline_source,driver_sha256=driver_before,driver_after_sha256=SHA(Path(__file__)),native_equal=native,owner_dependent_blend_log_equal=blend_raw_equal,blend_log_limitation="Existing blend-writes.tsv omits owner-handled writes; raw differences retained, not a complete native-write audit",classic_indexed_capture_equal=classic_equal,output_sizes_valid=sizes_ok,drawn_interceptor_bases=sorted(drawn),frozen_missing_new_equal=frozen_equal,pixels=pixels,aircraft_cyan_consumption=borrows,source_before=initial,source_after=inventory(r),data_sha256=SHA(a.data/'newshf.shp'),episode=a.episode,physical_level=a.level,scope='Actual bounded natural interceptor166-only delta, prior families present in both; native logs include state/RNG; natural original poses are explicitly reported; no recursive-underlay assertion')
 (q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True);assert okay
if __name__=='__main__':main()
