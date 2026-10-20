#!/usr/bin/env python3
"""Pack one imagegen-authored installation as three independent 24x28 roles.

The common aligned master preserves the exact upper/lower seam. Only original
23 lamp cells sample the generated alternate state. Exact original support,
including the opaque grey rails, is retained. No gameplay data is rewritten.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-paired287-288-v1'
LAMP=((8,2),(9,2),(10,2),(11,2),(12,2),(8,3),(9,3),(10,3),(11,3),(12,3),
      (8,5),(9,5),(10,5),(11,5),(12,5),(8,6),(9,6),(10,6),(11,6),(12,6),(9,7),(10,7),(11,7))
# The solid rectangle is explicitly authored by imagegen; exclude its magenta
# exterior only. No color replacement, vector redraw or geometry synthesis.
CROP=(384,17,870,1238)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 spec=importlib.util.spec_from_file_location('asteroid_art',ROOT/'prototype/build-asteroid1-ten-art.py');art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
 bank=(a.data/'newshd.shp').read_bytes();assert len(bank)==42012 and art.fnv(bank)=='0x913975450e0fc00d'
 red=np.array(Image.open(ART/'imagegen-master-red.png').convert('RGBA').crop(CROP).resize((192,448),Image.Resampling.LANCZOS))
 amber=np.array(Image.open(ART/'imagegen-master-amber.png').convert('RGBA').crop(CROP).resize((192,448),Image.Resampling.LANCZOS))
 red[:,:,3]=255;amber[:,:,3]=255
 upper=red[:224].copy();lower=red[224:].copy();lit=lower.copy()
 # Restrict generated state differences to the exact 23 original lamp cells.
 for x,y in LAMP:lit[y*8:(y+1)*8,x*8:(x+1)*8]=amber[224+y*8:224+(y+1)*8,x*8:(x+1)*8]
 inventory={};a.out.mkdir(parents=True,exist_ok=True)
 for base,rgba in [(245,upper),(281,lit),(283,lower)]:
  mask=np.zeros((28,24),np.uint8)
  for d,x,y in ((0,0,0),(1,12,0),(19,0,14),(20,12,14)):
   _,coverage=art.decode(bank,base+d);mask[y:y+14,x:x+12]=coverage
  assert np.count_nonzero(mask)==(672 if base==245 else 670)
  rgba[:,:,3]=np.repeat(np.repeat(mask,8,axis=0),8,axis=1);rgba[rgba[:,:,3]==0,:3]=0
  im=Image.fromarray(rgba,'RGBA');stem=f'enemy-newshd-{base}-8';im.save(a.out/(stem+'.png'))
  raw=struct.pack('<4s6I',b'HDR1',1080000+base,8,24,28,0,0)+im.tobytes();(a.out/(stem+'.hda')).write_bytes(raw)
  inventory[stem]={'record':287 if base==245 else 288,'base':base,'size':1,'logical_size':[24,28],'source_occupied_cells':int(np.count_nonzero(mask)),'rgba_fnv64':art.fnv(im.tobytes()),'sha256':hashlib.sha256(raw).hexdigest()}
 assert np.array_equal(lit[:,:,3],lower[:,:,3])
 changed=np.any(lit!=lower,axis=2);allowed=np.zeros((224,192),bool)
 for x,y in LAMP:allowed[y*8:(y+1)*8,x*8:(x+1)*8]=True
 assert not np.any(changed&~allowed)
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
