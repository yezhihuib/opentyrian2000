#!/usr/bin/env python3
"""Rebuild generated-only circuit10 into a new external directory. No game data needed."""
from pathlib import Path
from PIL import Image
import json,subprocess,tempfile,sys,struct,hashlib
P=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('usage: rebuild.py NEW_OUTPUT_DIRECTORY')
out=Path(sys.argv[1]).absolute()
if out.exists()or out.is_symlink():raise SystemExit('Output must not exist')
C=json.loads((P/'contract.json').read_text());I=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
sha=lambda b:hashlib.sha256(b).hexdigest()
if I:
 for rel,expected in I['inputs'].items():
  if sha((P/rel).read_bytes())!=expected:raise SystemExit('Input hash mismatch: '+rel)
out.mkdir(parents=True)
with tempfile.TemporaryDirectory(prefix='circuit10-rebuild-')as tmp:
 t=Path(tmp);masters={}
 for e in C['entries']:
  key=e['master']
  if key not in masters:
   w,h=e['registered_master_size'];raw=subprocess.check_output(['convert',str(P/key),'-filter','Lanczos','-resize',f'{w}x{h}!','-depth','8','RGBA:-']);masters[key]=Image.frombytes('RGBA',(w,h),raw)
  (t/f"raw-{e['source_id']}.rgba").write_bytes(masters[key].crop(tuple(e['crop'])).tobytes());(t/f"mask-{e['source_id']}.raw").write_bytes(Image.open(P/e['mask']).convert('L').tobytes())
 (t/'base132.rgba').write_bytes(Image.open(P/C['base']).convert('RGBA').tobytes())
 for name in ['compose','fit_ports']:
  subprocess.run(['g++','-O2','-std=c++17',str(P/(name+'.cpp')),'-o',str(t/name)],check=True);subprocess.run([str(t/name),str(t)],check=True)
 outputs=[]
 for e in C['entries']:
  i=e['source_id'];rgba=(t/f'fitted-{i}.rgba').read_bytes();png=out/f'terrain-shapesz-{i}-8.png';Image.frombytes('RGBA',(192,224),rgba).save(png);hda=b'HDR1'+struct.pack('<6I',e['hda_id'],8,24,28,0,0)+rgba;(out/f"{e['hda_id']}.hda").write_bytes(hda)
  item={'source_id':i,'RGBA_SHA256':sha(rgba),'HDA_SHA256':sha(hda),'PNG_SHA256':sha(png.read_bytes())};outputs.append(item)
  if I:
   expected=next(x for x in I['outputs']if x['source_id']==i)
   assert item['RGBA_SHA256']==expected['RGBA_SHA256']and item['HDA_SHA256']==expected['HDA_SHA256'],f'Output mismatch {i}'
 (out/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':outputs,'PNG_encoding_note':'DecodedRGBA and HDA exact; encoder metadata/file bytes may differ from canonical PNG.'},indent=2)+'\n')
print('PASS: 10 exact decodedRGBA/HDA outputs'if I else'Created10 outputs; inventory not yet frozen')
