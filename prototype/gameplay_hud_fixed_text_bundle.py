"""Rebuild the finite 370-cell HUT1; checksums detect corruption, not trust."""
from pathlib import Path
import json,struct
from PIL import Image
from gameplay_hud_extension_bundles import checked_file,sha,fnv
FILENAME='gameplay-hud-fixed-text-v1.hda'
def build_bundle(repo):
 repo=Path(repo);m=json.loads((repo/'assets/hd/manifest.json').read_text())['gameplay_hud_fixed_text_v1'];p=repo/m['source']
 assert m['schema']=='finite-pic3-hut1-fixed370-v1' and m['filename']==FILENAME
 assert p.resolve().is_relative_to(repo.resolve())
 assert {str(q.relative_to(p))for q in p.rglob('*')if q.is_file()}==set(m['source_files'])
 for name,spec in m['source_files'].items():
  b=checked_file(p,name).read_bytes();assert {'bytes':len(b),'sha256':sha(b)}==spec
 pieces=[]
 for t in m['tiles']:
  a=checked_file(p,t['authored']).read_bytes();q=checked_file(repo,t['source_png']);assert q.read_bytes()==a and sha(a)==t['png_sha256']
  im=Image.open(q);assert im.mode=='RGBA' and list(im.size)==t['size'];b=im.tobytes();assert sha(b)==t['rgba_sha256'] and set(b[3::4])=={255};pieces.append(b)
 assert len(pieces)==12 and list(map(len,pieces))==[6080]+[1600]*11
 payload=b''.join(pieces);raw=struct.pack('<4s7I4Q',b'HUT1',1,4,12,370,23680,1,0,0x14c1441f3d5dc0e2,0x5e80e83992be2927,0xb110512dd1fc63f4,fnv(payload))+payload
 receipt={'bytes':len(raw),'sha256':sha(raw)};assert raw==checked_file(p,FILENAME).read_bytes() and receipt==m['bundle']
 return raw,receipt
