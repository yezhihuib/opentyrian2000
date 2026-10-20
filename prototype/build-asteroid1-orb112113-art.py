#!/usr/bin/env python3
"""Reuse verified existing fireball RGB with exact original source registration.

Defaults and retained PNGs are unchanged. This compiler masks optional assets,
not a redraw or new procedural artwork.
"""
from pathlib import Path
import argparse,hashlib,json,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'assets/hd/artwork/asteroid1-orb112113-v1'
PINS={112:'c28da6740c5827bab6e2ab44faf0e5218fb8f033af7c6bc500d80167cf47405b',113:'49a4ef3fe0c25cb5cabe153a83d4cf72fc204c45872af83178521d33a902d412'}
def fnv(raw):
 h=0xcbf29ce484222325
 for v in raw:h=((h^v)*0x100000001b3)&0xffffffffffffffff
 return f'0x{h:016x}'
def decode(data,index):
 raw=(data/'tyrian.shp').read_bytes();o=struct.unpack_from('<13i',raw,2);bank=raw[o[7]:o[8]];assert len(bank)==32060 and hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
 mask=np.zeros((14,12),bool);indices=np.zeros((14,12),np.uint8);p=struct.unpack_from('<H',bank,2*(index-1))[0];x=y=0
 while True:
  v=bank[p];p+=1
  if v==15:break
  x+=v&15;n=v>>4
  if not n:y+=1;x-=12
  else:
   for _ in range(n):
    assert 0<=x<12 and 0<=y<14
    indices[y,x]=bank[p];mask[y,x]=True;p+=1;x+=1
 assert mask.sum()==45
 return bank,mask,indices
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);inventory={}
 for b in (112,113):
  bank,mask,indices=decode(a.data,b);source=ART/f'retained-source-{b}.png';assert hashlib.sha256(source.read_bytes()).hexdigest()==PINS[b];im=Image.open(source).convert('RGBA');assert im.size==(96,112);rgba=np.array(im);support=np.repeat(np.repeat(mask,8,axis=0),8,axis=1);rgba[~support]=0
  assert np.all((rgba[:,:,3]>0).reshape(14,8,12,8).any(axis=(1,3))==mask)
  out=Image.fromarray(rgba,'RGBA');stem=f'enemy-orb112113-{b}-8';out.save(a.out/(stem+'.png'));raw=struct.pack('<4s6I',b'HDR1',1420000+b,8,12,14,0,0)+out.tobytes();(a.out/(stem+'.hda')).write_bytes(raw)
  inventory[str(b)]={'source_bank':'tyrian.shp/player-shot-bank','source_bank_bytes':len(bank),'source_bank_fnv64':fnv(bank),'source_index':b,'material_role':142,'logical_size':[12,14],'density':8,'anchor':[0,0],'source_occupied_cells':45,'retained_source_sha256':PINS[b],'rgba_fnv64':fnv(out.tobytes()),'hda_sha256':hashlib.sha256(raw).hexdigest(),'source_png_sha256':hashlib.sha256((a.out/(stem+'.png')).read_bytes()).hexdigest()}
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
