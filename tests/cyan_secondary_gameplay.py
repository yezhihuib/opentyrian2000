#!/usr/bin/env python3
"""Bounded actual E1L12 SECONDARY cyan overlay comparison (old quartet remains present). Original game data stays external.

Builds a fresh exact-source Linux executable, runs present/missing cyan pairs,
archives each BMP byte-exact before removing only that redundant temporary,
and checks native state/RNG/writes and original-index support. This is not a
Windows, full campaign, or controlled-recursive-underlay qualification.
"""
from pathlib import Path
import argparse, csv, hashlib, json, os, re, shutil, subprocess, zipfile
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(root):
 return {p.relative_to(root).as_posix():SHA(p) for p in sorted((root/'src').rglob('*')) if p.is_file()}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('sysroot','data','base-pack','out'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--build',type=Path)
 p.add_argument('--density',type=int,choices=(4,8),default=8)
 p.add_argument('--output-scale',type=int,choices=(2,4),default=4)
 p.add_argument('--native-capture',action='store_true',help='Also capture native INDEX8 and internal-density RGB, not a physical8x window')
 p.add_argument('--start',type=int,default=150);p.add_argument('--count',type=int,default=1)
 p.add_argument('--baseline-build',type=Path,help='Optional frozen old-family build for missing-new byte equality')
 p.add_argument('--expect-secondary',action='store_true',help='Require all five secondary IDs admitted in captured window')
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() if isinstance(v,Path) else v for k,v in vars(a).items()})
 q=a.out;q.mkdir(exist_ok=False);r=a.root;initial=inventory(r);driver_before=SHA(Path(__file__))
 if a.baseline_build:
  baseline=json.loads((a.baseline_build/'build-receipt.json').read_text())
  assert baseline['status']=='PASS' and SHA(a.baseline_build/'opentyrian2000')==baseline['binary_sha256']
  assert all(SHA(a.baseline_build/n)==h for n,h in baseline['source_before'].items())
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
  cmd=['make','-j4','VCS_IDREV=printf cyan-layer2-hd-on','CPPFLAGS=-MMD -DNDEBUG -DNEWSHF_HD_COMPOSITOR=1 -I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),'LDFLAGS=-Wl,-rpath,'+str(a.sysroot/'usr/lib/x86_64-linux-gnu')]
  with (build/'build.log').open('w') as f:z=subprocess.run(cmd,cwd=build,env=env,stdout=f,stderr=subprocess.STDOUT)
  stable=initial==inventory(r) and all(SHA(build/n)==h for n,h in files.items())
  report=dict(status='PASS' if z.returncode==0 and stable else 'FAIL',source_before=files,source_after=inventory(r),source_unchanged=stable,command=cmd,exit=z.returncode,binary_sha256=SHA(build/'opentyrian2000') if (build/'opentyrian2000').exists() else None)
  (build/'build-receipt.json').write_text(json.dumps(report,indent=2)+'\n');assert report['status']=='PASS'
 exe=build/'opentyrian2000';pack=q/'pack';pack.mkdir();old_pack=q/'old-pack';old_pack.mkdir()
 for f in a.base_pack.rglob('*'):
  if f.is_file():
   d=pack/f.relative_to(a.base_pack);d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
 for f in (r/'assets/hd/current-compat/shapesy-cyan').glob('*.hda'):
  if not (pack/f.name).exists():(pack/f.name).symlink_to(f.resolve())
 for f in pack.rglob('*'):
  if f.is_file():
   d=old_pack/f.relative_to(pack);d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
 for f in (r/'assets/hd/current-compat/shapesy-cyan-secondary').glob('*.hda'):(pack/f.name).symlink_to(f.resolve())
 results=[]
 for variant in (('missing','present','frozen') if a.baseline_build else ('missing','present')):
  out=q/variant;out.mkdir();cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {a.output_scale}x\nitem fullscreen -1\n')
  use=pack if variant=='present' else old_pack
  run_exe=a.baseline_build/'opentyrian2000' if variant=='frozen' else exe
  e={**env,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'TYRIAN_CYAN_BORROW_TRACE':'1'}
  cmd=[str(run_exe),f'--data={a.data}','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=12',f'--asset-debug-tick={a.start}','--asset-debug-running',f'--render-ticks={a.start+a.count}',f'--render-assets={use}',f'--global-assets={use}','--asset-debug-capture',f'--asset-debug-capture-start={a.start}',f'--asset-debug-capture-count={a.count}','--asset-debug-window-only',f'--render-test={a.density}']
  if a.native_capture:cmd.remove('--asset-debug-window-only')
  inputs={str(run_exe):SHA(run_exe),**{str(f):SHA(f) for f in use.rglob('*') if f.is_file()},**{str(f):SHA(f) for f in a.data.iterdir() if f.is_file()}}
  with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as err:z=subprocess.run(cmd,cwd=out,env=e,stdout=f,stderr=err,timeout=600)
  captures={f.name:SHA(f) for f in out.glob('*.bmp')};archive=out/'captures.zip'
  with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zz:
   for f in sorted(out.glob('*.bmp')):Image.open(f).save(f.with_suffix('.png'));zz.write(f,f.name)
  with zipfile.ZipFile(archive) as zz:assert set(zz.namelist())==set(captures) and all(hashlib.sha256(zz.read(n)).hexdigest()==h for n,h in captures.items())
  for f in out.glob('*.bmp'):f.unlink()
  results.append(dict(variant=variant,density=a.density,physical_output_scale=a.output_scale,capture_sizes={f.name:list(Image.open(f).size) for f in out.glob('*.png')},exit=z.returncode,argv=cmd,captures=captures,inputs=inputs,unchanged=all(SHA(Path(n))==h for n,h in inputs.items()),archive_sha256=SHA(archive)))
  (q/'runs.json').write_text(json.dumps(results,indent=2)+'\n');assert z.returncode==0 and len(captures)==a.count*(3 if a.native_capture else 1)
 # Decode only original support; never save original data into the checkout.
 raw=(a.data/'shapesy.dat').read_bytes();at=0;masks={}
 for i in range(1,601):
  blank=raw[at];at+=1
  data=bytes(672) if blank else raw[at:at+672]
  if not blank:at+=672
  if i in (172,181,182,191,192):masks[i]=np.frombuffer(data,dtype=np.uint8).reshape(28,24)>0
 left=q/'missing';right=q/'present'
 native={n:(left/n).read_bytes()==(right/n).read_bytes() for n in ('state.tsv','enemy-projectiles.tsv','collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv','blend-writes.tsv')}
 rows=list(csv.DictReader((right/'asset-debug-materials.tsv').open(),delimiter='\t'));pixels=[]
 for f in sorted(left.glob('*.png')):
  delta=np.any(np.array(Image.open(f).convert('RGB'))!=np.array(Image.open(right/f.name).convert('RGB')),axis=2);support=np.zeros(delta.shape,dtype=bool);tick=int(re.search(r'(\d+)\.png$',f.name).group(1))
  factor=delta.shape[1]//320;assert factor in (1,2,4,8) and delta.shape==(200*factor,320*factor)
  for row in rows:
   if int(row['tick'])!=tick or row['category']!='terrain-layer2' or row['sheet'].lower()!='shapesy.dat' or int(row['id']) not in masks:continue
   for ny,nx in zip(*np.where(masks[int(row['id'])])):
    x=int(row['x'])-24+int(nx);y=int(row['y'])+int(ny)
    if 0<=x<264 and 0<=y<184:support[y*factor:(y+1)*factor,x*factor:(x+1)*factor]=True
  pixels.append(dict(file=f.name,changed=int(delta.sum()),outside_support=int((delta&~support).sum())))
 text=(right/'stderr.log').read_text();borrows=re.findall(r'CYAN_AIRCRAFT_BORROW[^\n]*',text)
 okay=all(native.values()) and all(x['outside_support']==0 for x in pixels) and initial==inventory(r) and all(x['unchanged'] for x in results)
 admitted={int(m[1]) for m in re.findall(r'cyan-tile tick=(\d+) logic_tick=\d+ id=(\d+) [^\n]*hd=1',text) if a.start<=int(m[0])<a.start+a.count}
 expected_sizes={'asset-debug-window':(320*a.output_scale,200*a.output_scale),'classic':(320,200),'display':(320*a.density,200*a.density)}
 sizes_ok=all(tuple(size)==expected_sizes[next(k for k in expected_sizes if name.startswith(k+'-'))] for run in results for name,size in run['capture_sizes'].items())
 classic_equal=all((left/f.name).read_bytes()==(right/f.name).read_bytes() for f in left.glob('classic-*.png')) and all(results[0]['captures'][n]==results[1]['captures'][n] for n in results[0]['captures'] if n.startswith('classic-'))
 frozen_equal={}
 if a.baseline_build:
  frozen=q/'frozen'
  for f in left.glob('*.png'):frozen_equal[f.name]=f.read_bytes()==(frozen/f.name).read_bytes()
  for name in native:frozen_equal[name]=(left/name).read_bytes()==(frozen/name).read_bytes()
 okay=okay and sizes_ok and classic_equal and all(frozen_equal.values()) and SHA(Path(__file__))==driver_before
 if a.density==8 and a.expect_secondary:okay=okay and {172,181,182,191,192}<=admitted and any(x['changed'] for x in pixels)
 elif a.density==4:okay=okay and not borrows and not any(x['changed'] for x in pixels)
 report=dict(status='PASS' if okay else 'FAIL',internal_density=a.density,physical_output_scale=a.output_scale,native_capture=a.native_capture,driver_sha256=driver_before,driver_after_sha256=SHA(Path(__file__)),native_equal=native,classic_indexed_capture_equal=classic_equal,output_sizes_valid=sizes_ok,secondary_admitted_ids=sorted(admitted&{172,181,182,191,192}),frozen_missing_new_equal=frozen_equal,pixels=pixels,aircraft_cyan_consumption=borrows,source_before=initial,source_after=inventory(r),data_sha256=SHA(a.data/'shapesy.dat'),scope='Actual E1L12 secondary-only delta, old quartet present in both; all native logs include state/RNG; no natural recursive platform dependency assertion')
 (q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True);assert okay
if __name__=='__main__':main()
