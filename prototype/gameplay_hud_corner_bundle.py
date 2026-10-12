"""Reconstruct the finite V2 corner from its pinned generated V5 dependency."""
import json,hashlib,struct
from pathlib import Path
from PIL import Image,ImageDraw
from gameplay_hud_bundle import fnv

def sha(b):return hashlib.sha256(b).hexdigest()
def apply_corner(repo, baseline):
 repo=Path(repo);m=json.loads((repo/'assets/hd/manifest.json').read_text())['gameplay_hud_corner_v2'];p=repo/m['source']
 assert sha(baseline)==m['baseline_sha256']=='4ff6cd95d4c3ec5b7e4825e38a5242fc96c1cd305987a873bea4a55fa5a04482'
 assert sha((p/'manifest.json').read_bytes())==m['source_manifest_sha256']
 assert sha((p/'IMPORT.json').read_bytes())==m['import_sha256']
 inventory=json.loads((p/'manifest.json').read_text())['files'];imported=json.loads((p/'IMPORT.json').read_text())
 for name in imported['selected_files']:
  q=p/name;assert q.resolve().is_relative_to(p.resolve()) and q.is_file() and not q.is_symlink()
  assert sha(q.read_bytes())==imported['selected_sha256'][name]
  if name in inventory:
   b=q.read_bytes();assert len(b)==inventory[name]['bytes'] and sha(b)==inventory[name]['sha256']
 base_mask=baseline[64:64064];base_rgba=baseline[64064:]
 tile=Image.open(p/'sources/generated-junction-master.png').convert('RGBA').resize((120,72),Image.Resampling.LANCZOS).crop((16,8,100,72))
 frame=Image.frombytes('RGBA',(1280,800),base_rgba);existing=frame.crop((992,736,1076,800));tile.paste(existing,(0,0),existing.getchannel('A'))
 draw=ImageDraw.Draw(tile)
 for x,y in [(0,3),(0,4)]+[(19,y)for y in range(7,14)]+[(20,14)]:draw.rectangle((x*4,y*4,x*4+3,y*4+3),fill=(0,0,0,255))
 assert tile.tobytes()==(p/'corner-4x.rgba').read_bytes()
 mask=bytearray(base_mask)
 for y in range(184,200):mask[y*320+248:y*320+269]=b'\xff'*21
 assert bytes(mask)==(p/'combined-6853.mask').read_bytes() and mask.count(255)==6853
 frame.paste(tile,(992,736));rgba=frame.tobytes()
 canonical=repo/m['source_png'];assert sha(canonical.read_bytes())==m['source_png_sha256'];assert Image.open(canonical).convert('RGBA').tobytes()==rgba
 assert frame.getchannel('A').tobytes()==Image.frombytes('L',(320,200),bytes(mask)).resize((1280,800),Image.Resampling.NEAREST).tobytes()
 raw=struct.pack('<4s8I3QI',b'HUD1',1,320,200,4,0,0,64000,4096000,0x14c1441f3d5dc0e2,fnv(mask),fnv(rgba),0)+mask+rgba
 assert {'bytes':len(raw),'sha256':sha(raw)}==m['runtime']
 return raw
