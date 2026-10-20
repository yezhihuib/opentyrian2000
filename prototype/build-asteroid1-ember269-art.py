#!/usr/bin/env python3
"""Pack the imagegen-authored four-state NEWSHD record269 shared master.

Only deterministic raster resizing and aligned generated-state compositing.
All state changes remain in original logical x8..12/y6..18. No original data
writes, procedural recoloring, code-drawn geometry or additional animation.
"""
from pathlib import Path
import argparse,hashlib,json,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-ember269-v1'
STATES=((267,'dark'),(269,'dim'),(271,'orange'),(273,'bright'))
STATE_REGION=(64,48,104,152)
def fnv(raw):
 h=0xcbf29ce484222325
 for v in raw:h=((h^v)*0x100000001b3)&0xffffffffffffffff
 return f'0x{h:016x}'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 bank=(a.data/'newshd.shp').read_bytes();assert len(bank)==42012 and fnv(bank)=='0x913975450e0fc00d'
 images={name:Image.open(ART/f'imagegen-master-{name}.png').convert('RGBA').resize((192,224),Image.Resampling.LANCZOS)for _,name in STATES}
 master=images['dark'];inventory={};arrays=[];a.out.mkdir(parents=True,exist_ok=True)
 for base,name in STATES:
  image=master.copy();image.paste(images[name].crop(STATE_REGION),STATE_REGION[:2])
  rgba=np.array(image);rgba[:,:,3]=255;image=Image.fromarray(rgba,'RGBA');arrays.append(rgba)
  stem=f'enemy-newshd-{base}-8';image.save(a.out/(stem+'.png'))
  raw=struct.pack('<4s6I',b'HDR1',1080000+base,8,24,28,0,0)+image.tobytes();assert len(raw)==172060;(a.out/(stem+'.hda')).write_bytes(raw)
  inventory[stem]={'record':269,'source_bank':'newshd.shp','logical_bank':8,'base':base,'size':1,'logical_size':[24,28],'source_occupied_cells':672,'state':name,'rgba_fnv64':fnv(image.tobytes()),'sha256':hashlib.sha256(raw).hexdigest()}
 allowed=np.zeros((224,192),bool);allowed[48:152,64:104]=True
 for i in range(4):
  for j in range(i):assert np.any(arrays[i]!=arrays[j]) and not np.any(np.any(arrays[i]!=arrays[j],axis=2)&~allowed)
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
