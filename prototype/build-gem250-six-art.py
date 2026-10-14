#!/usr/bin/env python3
"""Verify frozen generated-only gem250 provenance and exact six-output rebuild."""
import hashlib,json,struct,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCE='assets/hd/artwork/gem250-six-v1'
INVENTORY='e0b29e08ce061510940701831c259155d2fafdb9a7f146885d1ae549c8a5fc09'
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def read(p):
 assert p.is_file() and not p.is_symlink(),str(p)
 return p.read_bytes()
def main():
 source=ROOT/SOURCE;raw=read(source/'inventory.json');assert sha(raw)==INVENTORY;inv=json.loads(raw);m=json.loads(read(ROOT/'assets/hd/manifest.json'));defaults=[m['default_preview_pack'],m['default_debug_pack']]
 assert [r['id'] for r in inv['outputs']]==[14,15,16,17,18,188]
 for name,digest in inv['inputs'].items():
  assert not Path(name).is_absolute() and '..' not in Path(name).parts
  assert sha(read(source/name))==digest,name
 expected=[];names=set();canonical=set();bodies=[]
 for slot,r in enumerate(inv['outputs'],499):
  stem=f"{r['prefix']}-{r['id']}-8";raw=read(source/'output'/f'{stem}.hda');png=read(source/'output'/f'{stem}.png');header=[r['key'],8,12,14,0,0]
  assert len(raw)==43036 and raw[:28]==struct.pack('<4s6I',b'HDR1',*header);assert sha(raw)==r['HDA_SHA256'] and sha(raw[28:])==r['RGBA_SHA256'] and sha(png)==r['PNG_SHA256']
  with Image.open(source/'output'/f'{stem}.png') as im:assert im.mode=='RGBA' and im.size==(96,112) and im.tobytes()==raw[28:]
  with Image.open(source/f"masks/mask-{r['id']}.png") as mask:support=mask.resize((96,112),Image.Resampling.NEAREST).tobytes()
  alpha=raw[31::4];
  if r['id']!=188:bodies.append(raw[28:])
  assert all(not a or b for a,b in zip(alpha,support));assert sum(0<a<255 for a in alpha)==r['fractional_samples'] and 0 in alpha
  digest=sha(raw);p=f'assets/hd/source/{stem}-{digest[:12]}.png';assert read(ROOT/p)==png;assert m['source_pngs'][digest]=={'path':p,'sha256':sha(png),'RGBA_sha256':sha(raw[28:])};canonical.add(p)
  for pack in defaults:
   assert m['packs'][pack]['files'][stem+'.hda']=={'header_u32':header,'sha256':digest,'source_png':p,'source_png_sha256':sha(png)}
   assert read(ROOT/'assets/hd/packs'/pack/(stem+'.hda'))==raw
  stamp=0xcbf29ce484222325
  for b in raw[28:]:stamp=((stamp^b)*0x100000001b3)&((1<<64)-1)
  expected.append({'id':r['id'],'slot':slot,'key':r['key'],'HDA_sha256':digest,'RGBA_FNV1a64':f'{stamp:016x}'});names.add(stem+'.hda')
 assert len(bodies)==5 and len({b[3::4] for b in bodies})==1
 for previous,current in zip(bodies,bodies[1:]):
  assert all(current[i]>=previous[i] for i in range(len(current)) if i%4!=3 and current[i-i%4+3])
 assert m['gem250_six_v1']['entries']==expected and m['gem250_six_v1']['inventory_sha256']==INVENTORY
 assert {p.relative_to(ROOT).as_posix() for p in (ROOT/'assets/hd/source').glob('gem250-*')}==canonical
 for pack,data in m['packs'].items():
  assert data['count']==len(data['files'])
  relevant={name for name,item in data['files'].items() if name.startswith('gem250-') or item['header_u32'][0]//10000 in [120,121]}
  assert relevant==(names if pack in defaults else set())
 actual={p.relative_to(ROOT/'assets/hd/packs').as_posix() for p in (ROOT/'assets/hd/packs').rglob('gem250-*')};assert actual=={pack+'/'+name for pack in defaults for name in names}
 with tempfile.TemporaryDirectory(prefix='gem250-rebuild-') as tmp:
  subprocess.run([sys.executable,str(source/'rebuild.py'),str(Path(tmp)/'output')],check=True)
  for p in (source/'output').iterdir():assert (Path(tmp)/'output'/p.name).read_bytes()==p.read_bytes(),p.name
 print(json.dumps({'status':'PASS','inventory_sha256':INVENTORY,'members':6,'default_bindings':12,'exact_rebuild':True,'game_runs':0,'entries':expected},indent=2))
if __name__=='__main__':main()
