#!/usr/bin/env python3
"""Bounded actual E1L12 cyan overlay comparison. Original game data stays external.

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
 p.add_argument('--start',type=int,default=340);p.add_argument('--count',type=int,default=71)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() if isinstance(v,Path) else v for k,v in vars(a).items()})
 q=a.out;q.mkdir(exist_ok=False);r=a.root;initial=inventory(r)
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
 exe=build/'opentyrian2000';pack=q/'pack';pack.mkdir()
 for f in a.base_pack.rglob('*'):
  if f.is_file():
   d=pack/f.relative_to(a.base_pack);d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(f.resolve())
 for f in (r/'assets/hd/current-compat/shapesy-cyan').glob('*.hda'):(pack/f.name).symlink_to(f.resolve())
 results=[]
 for variant in ('missing','present'):
  out=q/variant;out.mkdir();cfg=out/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {a.output_scale}x\nitem fullscreen -1\n')
  use=pack if variant=='present' else a.base_pack
  e={**env,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out),'XDG_CONFIG_HOME':str(out/'config'),'TYRIAN_CYAN_BORROW_TRACE':'1'}
  cmd=[str(exe),f'--data={a.data}','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=12','--asset-debug-tick=340','--asset-debug-running','--render-ticks=411',f'--render-assets={use}',f'--global-assets={use}','--asset-debug-capture',f'--asset-debug-capture-start={a.start}',f'--asset-debug-capture-count={a.count}','--asset-debug-window-only',f'--render-test={a.density}']
  if a.native_capture:cmd.remove('--asset-debug-window-only')
  inputs={str(exe):SHA(exe),**{str(f):SHA(f) for f in use.rglob('*') if f.is_file()},**{str(f):SHA(f) for f in a.data.iterdir() if f.is_file()}}
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
  if i in (111,112,121,122):masks[i]=np.frombuffer(data,dtype=np.uint8).reshape(28,24)>0
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
 if a.density==8:okay=okay and bool(borrows) and 'hd=1' in text
 else:okay=okay and not borrows and not any(x['changed'] for x in pixels)
 report=dict(status='PASS' if okay else 'FAIL',internal_density=a.density,physical_output_scale=a.output_scale,native_capture=a.native_capture,native_equal=native,pixels=pixels,aircraft_cyan_consumption=borrows,source_before=initial,source_after=inventory(r),data_sha256=SHA(a.data/'shapesy.dat'),scope='Actual E1L12; no natural recursive platform dependency assertion')
 (q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True);assert okay
if __name__=='__main__':main()
