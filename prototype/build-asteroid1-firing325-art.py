#!/usr/bin/env python3
"""Pack the imagegen-authored NEWSHS record325 shared-master indicator family.

Only deterministic resizing and aligned compositing are done here. The common
unlit housing is identical in all states; generated indicator samples are fit
inside the original logical x9..15/y2..5 state region. No hand-drawn geometry,
color replacement, source game-data rewrite or new animation frame.
"""
from pathlib import Path
import argparse, hashlib, json, struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-firing325-v1'
# Rectangles in the common 192x224 density8 image coordinates. The original
# imagegen panel is normalized into the original source's 7x4 state rectangle.
PANEL_SAMPLE=(72,28,128,50)
STATE_REGION=(72,16,128,48)
STATES=((11,'unlit'),(125,'bright'),(277,'dim'))
def fnv(raw):
 h=0xcbf29ce484222325
 for v in raw:h=((h^v)*0x100000001b3)&0xffffffffffffffff
 return f'0x{h:016x}'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 bank=(a.data/'newshs.shp').read_bytes();assert len(bank)==46566 and fnv(bank)=='0xf22ec1295ced5d11'
 images={name:Image.open(ART/f'imagegen-master-{name}.png').convert('RGBA').resize((192,224),Image.Resampling.LANCZOS)for _,name in STATES}
 master=images['unlit'];inventory={};arrays=[];a.out.mkdir(parents=True,exist_ok=True)
 for base,name in STATES:
  image=master.copy();image.paste(images[name].crop(PANEL_SAMPLE).resize((56,32),Image.Resampling.LANCZOS),STATE_REGION[:2])
  rgba=np.array(image);rgba[:,:,3]=255;image=Image.fromarray(rgba,'RGBA');arrays.append(rgba)
  stem=f'enemy-newshs-{base}-8';image.save(a.out/(stem+'.png'))
  raw=struct.pack('<4s6I',b'HDR1',1080000+base,8,24,28,0,0)+image.tobytes();assert len(raw)==172060;(a.out/(stem+'.hda')).write_bytes(raw)
  inventory[stem]={'record':325,'source_bank':'newshs.shp','logical_bank':23,'base':base,'size':1,'logical_size':[24,28],'source_occupied_cells':672,'state':name,'rgba_fnv64':fnv(image.tobytes()),'sha256':hashlib.sha256(raw).hexdigest()}
 allowed=np.zeros((224,192),bool);allowed[16:48,72:128]=True
 for i in range(3):
  for j in range(i):assert not np.any(np.any(arrays[i]!=arrays[j],axis=2)&~allowed)
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
