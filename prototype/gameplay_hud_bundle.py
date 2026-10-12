"""Reconstruct the finite generated HUD1 resource; checksums detect corruption only."""
from pathlib import Path
import hashlib,struct,json
from PIL import Image
FILENAME='gameplay-hud-v1.hda'
def sha(b):return hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for c in b:h=((h^c)*1099511628211)&0xffffffffffffffff
 return h
def build_bundle(repo):
 repo=Path(repo);m=json.loads((repo/'assets/hd/manifest.json').read_text())['gameplay_hud_v5'];p=repo/m['source'];f=p/'manifest.json'
 assert sha(f.read_bytes())==m['source_manifest_sha256']
 authored=json.loads(f.read_text())
 for name,v in authored['files'].items():
  q=p/name;assert q.resolve().is_relative_to(p.resolve()) and q.is_file() and not q.is_symlink()
  b=q.read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256']
 source=repo/m['source_png'];assert sha(source.read_bytes())==m['source_png_sha256']
 im=Image.open(source);assert im.mode=='RGBA' and im.size==(1280,800);rgba=im.tobytes()
 mask=Image.open(p/'approved-mask-6667.png');assert mask.mode=='L' and mask.size==(320,200);rawmask=mask.tobytes();assert set(rawmask)<={0,255} and rawmask.count(255)==6667
 assert im.getchannel('A').tobytes()==mask.resize((1280,800),Image.Resampling.NEAREST).tobytes()
 assert all(not any(rawmask[y*320:y*320+264])for y in range(184))
 assert m['schema']=='singleplayer-pic3-static-hud1-v1' and m['density']==4 and m['logical_size']==[320,200] and m['owned_pixels']==6667
 assert m['source_pic3_fnv1a64']=='14c1441f3d5dc0e2'
 header=struct.pack('<4s8I3QI',b'HUD1',1,320,200,4,0,0,64000,4096000,int(m['source_pic3_fnv1a64'],16),fnv(rawmask),fnv(rgba),0)
 raw=header+rawmask+rgba;assert len(raw)==4160064 and raw==(p/FILENAME).read_bytes()
 return raw,{'bytes':len(raw),'sha256':sha(raw)}
