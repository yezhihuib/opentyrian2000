#!/usr/bin/env python3
"""Rebuild one generated periodic world atlas. No game data, raster invention or baked variants."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,tempfile,os,shutil
P=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def J(p):return json.loads(p.read_text())
def check(ok,s):
 if not ok:raise ValueError(s)
def run(*a):subprocess.run([str(x) for x in a],check=True,stdout=subprocess.DEVNULL)
def decoded(p,mode='RGBA'):return Image.open(p).convert(mode).tobytes()
def main(value):
 raw=Path(os.path.abspath(value));check(not any(p.is_symlink() for p in [raw,*raw.parents]),'No symlink output paths');out=raw.resolve();check(not out.exists(),'A NEW output directory is required');check(P!=out and P not in out.parents and out not in P.parents,'Output cannot overlap source');check(out.parent.is_dir(),'Output parent must exist');check(not any((q/'assets/hd/manifest.json').exists() for q in out.parents),'Output cannot be in main game checkout');check(not any((q/'.git').exists() and q not in P.parents for q in out.parents),'Output cannot be in another Git checkout')
 inv=J(P/'package-files.json')['files'];actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() or f.is_symlink()};check(actual==set(inv)|{'package-files.json'},'Source inventory mismatch')
 for name,r in inv.items():check(not (P/name).is_symlink() and sha((P/name).read_bytes())==r['sha256'],'Input changed: '+name)
 reg=J(P/'contracts/atlas-registration.json');out.mkdir()
 def verify(p,key):check(sha(decoded(p,reg[key]['decoded_mode']))==reg[key]['decoded_sha256'],'Registration mismatch: '+key)
 def calibrate(src,dst,f):
  a=['convert',src]
  for c,z in zip('RGB',f):a+=['-channel',c,'-fx',f'floor(u*{z:.17g}*255+0.5)/255']
  run(*a,'+channel','-depth','8','PNG32:'+str(dst))
 with tempfile.TemporaryDirectory(prefix='.atlas-',dir=out) as td:
  t=Path(td);run('convert',P/'source/generated-independent-continuous-master.png','-resize','768x896!','-depth','8','PNG32:'+str(t/'registered.png'));verify(t/'registered.png','registered')
  calibrate(t/'registered.png',t/'base.png',reg['calibration']['material']);verify(t/'base.png','base');run('convert',t/'base.png','-roll','+384+448','PNG32:'+str(t/'offset.png'));verify(t/'offset.png','offset')
  run('convert',P/'source/generated-central-seam.png','-resize','768x896!','PNG32:'+str(t/'central.png'));verify(t/'central.png','central_registered');calibrate(t/'central.png',t/'central-calibrated.png',reg['calibration']['central']);verify(t/'central-calibrated.png','central_calibrated')
  run('convert',P/'source/generated-horizontal-seam.png','-resize','768x256!','PNG32:'+str(t/'horizontal.png'));verify(t/'horizontal.png','horizontal_registered');calibrate(t/'horizontal.png',t/'horizontal-calibrated.png',reg['calibration']['horizontal']);verify(t/'horizontal-calibrated.png','horizontal_calibrated')
  run('c++','-O2','-std=c++17','-ffp-contract=off',P/'source/compose_wrap.cpp','-o',t/'compose')
  for n,f in [('old','offset'),('gen','central-calibrated'),('hor','horizontal-calibrated')]:run('convert',t/(f+'.png'),'-depth','8','RGBA:'+str(t/(n+'.rgba')))
  run(t/'compose',t/'old.rgba',t/'gen.rgba',t/'hor.rgba',t/'out.rgba',t/'weight.gray');run('convert','-size','768x896','-depth','8','RGBA:'+str(t/'out.rgba'),'PNG32:'+str(out/'atlas.png'));verify(out/'atlas.png','atlas');check(decoded(out/'atlas.png')==decoded(P/'selected/atlas.png'),'Selected atlas differs')
  run('convert','-size','768x896','-depth','8','GRAY:'+str(t/'weight.gray'),out/'seam-edit-weight.png');verify(out/'seam-edit-weight.png','weight')
  run('convert',P/'source/cliff-footer/generated-cliff-foot.png','-filter','Lanczos','-resize','576x672!','PNG32:'+str(t/'footer.png'));check(sha(decoded(t/'footer.png'))==reg['footer_registered_rgba_sha256'],'Footer registration mismatch')
  bindings=J(P/'contracts/material-bindings.json');check(len(bindings)==62 and sum(x['changed'] for x in bindings.values())==61,'Finite source scope changed');guard_count=0
  for name,b in bindings.items():
   src=decoded(P/b['source']);check(sha(src)==b['source_rgba_sha256'],'Published source mismatch: '+name);check(sha(bytes.fromhex(b['header_hex'])+src)==b['source_hda_sha256'],'Original HDA mismatch: '+name)
   weight=bytes([255])*43008 if b['weight'] is None else decoded(P/b['weight'],'L');check(len(weight)==43008,'Invalid mask');check(all(not w or src[p*4+3]==255 for p,w in enumerate(weight)),'Weight changes partial/zero alpha: '+name);guard_count+=sum(w==0 for w in weight)
   if b['guard']:
    g=decoded(P/b['guard'],'L');check(all(not a or not w for a,w in zip(g,weight)),'Strict guard overlaps material: '+name)
   if 'footer' in b:
    f=b['footer'];x,y,w,h=f['registered_crop'];q=out/f'footer-{f["id"]}.png';run('convert',t/'footer.png','-crop',f'{w}x{h}+{x}+{y}','+repage','PNG32:'+str(q));check(sha(decoded(q))==f['generated_input']['decoded_sha256'],'Footer crop mismatch')
    for k in ['generated_weight','ground_weight']:check(not any(decoded(P/f[k],'L')[:184*192]),'Footer upper guard violation')
   if b['scope_group']=='road_dark_backing12':
    n=int(name.split('-')[-2]);sand=decoded(P/f'contracts/sand-guards/protected-sand-{n}.png','L');check(all(not s or not w for s,w in zip(sand,weight)),'Sand mask overlap: '+name)
  receipt={'status':'PASS: exact generated atlas/footers and immutable finite mask/source contract; runtime pending','rgba_sha256':sha(decoded(out/'atlas.png')),'atlas_png_sha256':sha((out/'atlas.png').read_bytes()),'resources':62,'material_consumers':61,'unchanged_guard':['terrain-shapesz-111-8'],'all_alpha_and_semantic_mask_guards_verified':True,'source_zero_weight_pixels':guard_count,'package_inventory_sha256':sha((P/'package-files.json').read_bytes())};(out/'rebuild-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: python3 rebuild.py NEW_EXTERNAL_OUTPUT_DIRECTORY')
 try:main(sys.argv[1])
 except Exception as e:raise SystemExit('REBUILD FAILED: '+str(e))
