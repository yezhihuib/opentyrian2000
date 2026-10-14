#!/usr/bin/env python3
"""Verify the authored-vector frozen Data513 family and exact output rebuild."""
from pathlib import Path
import argparse,hashlib,json,struct,subprocess,sys,tempfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCE='assets/hd/artwork/data513-twelve-v1'
INVENTORY='c77080d8b66aa8b6426505d8a61e5c571cca5bc0ee20950b0aa15da46e06a642'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def validate(root=ROOT,rebuild=True):
 art=root/SOURCE;raw=(art/'inventory.json').read_bytes();assert SHA(raw)==INVENTORY
 inv=json.loads(raw);m=json.loads((root/'assets/hd/manifest.json').read_text());packs=[m['default_preview_pack'],m['default_debug_pack']]
 wanted=set(inv['inputs'])|{'inventory.json','output/rebuild-receipt.json','proof/source-only-rebuild.json','SHA256SUMS'}|{f"output/{r[k]}" for r in inv['outputs'] for k in ['png','hda']}
 assert {p.relative_to(art).as_posix() for p in art.rglob('*') if p.is_file()}==wanted
 for n,h in inv['inputs'].items():assert not Path(n).is_absolute() and '..' not in Path(n).parts and SHA((art/n).read_bytes())==h,n
 rows=[];raws={};alphas=[]
 for row in inv['outputs']:
  i=row['id'];assert i in [159,161,163,197,199,201,235,237,239,273,275,277];png=(art/'output'/row['png']).read_bytes();assert SHA(png)==row['PNG_SHA256']
  with Image.open(art/'output'/row['png']) as im:assert im.mode=='RGBA' and im.size==(192,224);rgba=im.tobytes()
  header=[1240000+i,8,24,28,6,7];hda=struct.pack('<4s6I',b'HDR1',*header)+rgba
  assert hda==(art/'output'/row['hda']).read_bytes() and len(hda)==172060 and SHA(hda)==row['HDA_SHA256'] and SHA(rgba)==row['RGBA_SHA256']
  stamp=0xcbf29ce484222325
  for b in rgba:stamp=((stamp^b)*0x100000001b3)&((1<<64)-1)
  assert f'{stamp:016x}'==row['RGBA_FNV1a64'];assert sum(0<a<255 for a in rgba[3::4])==row['fractional_samples'];alphas.append(rgba[3::4])
  name=f'data513-bank11-{i}-8.hda';digest=SHA(hda);p=f'assets/hd/source/data513-bank11-{i}-8-{digest[:12]}.png';assert (root/p).read_bytes()==png
  assert m['source_pngs'][digest]=={'path':p,'sha256':SHA(png),'RGBA_sha256':SHA(rgba)}
  for pack in packs:
   assert (root/'assets/hd/packs'/pack/name).read_bytes()==hda
   assert m['packs'][pack]['files'][name]=={'header_u32':header,'sha256':digest,'source_png':p,'source_png_sha256':SHA(png)}
  rows.append({'id':i,'slot':510+len(rows),'key':1240000+i,'HDA_sha256':digest,'RGBA_FNV1a64':f'{stamp:016x}'});raws[name]=hda
 assert len(alphas)==12 and all(a==alphas[0] for a in alphas)
 assert m['data513_twelve_v1']=={'source':SOURCE,'inventory_sha256':INVENTORY,'role':124,'density':8,'logical_size':[24,28],'anchor':[6,7],'ids':[159,161,163,197,199,201,235,237,239,273,275,277],'scope':'record513 size1 actual spriteSheet11 only; shared512 and fixed266 unchanged','fallback':'all-twelve-or-classic; density8 only; startup-selected lifetime cache','entries':rows}
 for pack,data in m['packs'].items():
  assert data['count']==len(data['files'])
  relevant={n for n,v in data['files'].items() if n.startswith('data513-') or v['header_u32'][0]//10000==124}
  assert relevant==(set(raws) if pack in packs else set()),pack
 if rebuild:
  with tempfile.TemporaryDirectory(prefix='data513-art-rebuild-') as tmp:
   result=subprocess.run(['node',str(art/'rebuild.cjs'),str(Path(tmp)/'output')],capture_output=True,text=True)
   if result.returncode:raise AssertionError(result.stdout+result.stderr)
   for row in inv['outputs']:
    for key in ('png','hda'):assert (Path(tmp)/'output'/row[key]).read_bytes()==(art/'output'/row[key]).read_bytes()
 return {'status':'PASS','inventory_sha256':INVENTORY,'members':12,'default_bindings':24,'canonical_rgba_unchanged':True,'exact_rebuild':rebuild,'entries':rows,'game_runs':0},raws
if __name__=='__main__':print(json.dumps(validate()[0],indent=2))
