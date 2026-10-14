#!/usr/bin/env python3
"""Validate the frozen shell pair and exact HDR1 wrapping; no art edit or game."""
import argparse,hashlib,json,struct
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCE='assets/hd/artwork/enemy-tank-shell-pair-v1'
INVENTORY='0f5b3c9530dba5c15fc1384a91c528db3da2ace6dd64f3b74f8672d5b9504f74'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def validate(root=ROOT):
 art=root/SOURCE;raw=(art/'inventory.json').read_bytes();assert SHA(raw)==INVENTORY
 inv=json.loads(raw);m=json.loads((root/'assets/hd/manifest.json').read_text());packs=[m['default_preview_pack'],m['default_debug_pack']]
 for name,h in inv['inputs'].items():
  assert not Path(name).is_absolute() and '..' not in Path(name).parts
  assert SHA((art/name).read_bytes())==h,name
 rows=[];names=set();canonical=set();rebuild={}
 for row in inv['outputs']:
  i=row['id'];assert i in [146,147];png=(art/row['source']).read_bytes();assert SHA(png)==row['PNG_SHA256']
  with Image.open(art/row['source']) as im:assert im.mode=='RGBA' and im.size==(96,112);rgba=im.tobytes()
  header=[1220000+i,8,12,14,0,0];hda=struct.pack('<4s6I',b'HDR1',*header)+rgba
  assert len(hda)==43036 and SHA(hda)==row['HDA_SHA256'] and SHA(rgba)==row['RGBA_SHA256']
  stamp=0xcbf29ce484222325
  for b in rgba:stamp=((stamp^b)*0x100000001b3)&((1<<64)-1)
  assert f'{stamp:016x}'==row['RGBA_FNV1a64'];assert sum(0<a<255 for a in rgba[3::4])==row['fractional_alpha_samples']
  name=f'enemy-tank-shell-{i}-8.hda';digest=SHA(hda);p=f'assets/hd/source/enemy-tank-shell-{i}-8-{digest[:12]}.png';assert (root/p).read_bytes()==png
  assert m['source_pngs'][digest]=={'path':p,'sha256':SHA(png),'RGBA_sha256':SHA(rgba)}
  for pack in packs:
   assert (root/'assets/hd/packs'/pack/name).read_bytes()==hda
   assert m['packs'][pack]['files'][name]=={'header_u32':header,'sha256':digest,'source_png':p,'source_png_sha256':SHA(png)}
  rows.append({'id':i,'slot':505+i-146,'key':1220000+i,'HDA_sha256':digest,'RGBA_FNV1a64':f'{stamp:016x}'});names.add(name);canonical.add(p);rebuild[name]=hda
 assert m['enemy_tank_shell_pair_v1']=={'source':SOURCE,'inventory_sha256':INVENTORY,'role':122,'density':8,'logical_size':[12,14],'anchor':[0,0],'ids':[146,147],'scope':'enemy-only; shared records15/194/195 and weapons2/3/6/7; player and newsh6 paths unchanged','fallback':'all-two-or-classic; density8 only; startup-selected lifetime cache','entries':rows}
 for pack,data in m['packs'].items():
  assert data['count']==len(data['files'])
  relevant={n for n,v in data['files'].items() if n.startswith('enemy-tank-shell-') or v['header_u32'][0]//10000==122}
  assert relevant==(names if pack in packs else set()),pack
 assert {p.relative_to(root).as_posix() for p in (root/'assets/hd/source').glob('enemy-tank-shell-*')}==canonical
 assert {p.relative_to(root/'assets/hd/packs').as_posix() for p in (root/'assets/hd/packs').glob('*/enemy-tank-shell-*')}=={p+'/'+n for p in packs for n in names}
 return {'status':'PASS','inventory_sha256':INVENTORY,'members':2,'default_bindings':4,'canonical_rgba_unchanged':True,'exact_wrapper_rebuild_in_memory':True,'entries':rows,'game_runs':0},rebuild
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path);a=p.parse_args();report,outputs=validate()
 if a.out:
  a.out.mkdir(parents=True,exist_ok=False)
  for name,raw in outputs.items():(a.out/name).write_bytes(raw)
 print(json.dumps(report,indent=2))
