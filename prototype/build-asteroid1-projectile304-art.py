#!/usr/bin/env python3
"""Register one imagegen projectile inside the exact original 13-cell mask."""
from pathlib import Path
import argparse,hashlib,json,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-projectile304-v1'
def fnv(raw):
 h=0xcbf29ce484222325
 for v in raw:h=((h^v)*0x100000001b3)&0xffffffffffffffff
 return f'0x{h:016x}'
def decode(data):
 raw=(data/'tyrian.shp').read_bytes();offsets=struct.unpack_from('<13i',raw,2);bank=raw[offsets[7]:offsets[8]]
 assert len(bank)==32060 and hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
 p=struct.unpack_from('<H',bank,606)[0];x=y=0;mask=np.zeros((14,12),bool);indices=np.zeros((14,12),np.uint8)
 while True:
  v=bank[p];p+=1
  if v==15:break
  x+=v&15;n=v>>4
  if not n:y+=1;x-=12
  else:
   for _ in range(n):
    assert 0<=x<12 and 0<=y<14
    mask[y,x]=True;indices[y,x]=bank[p];p+=1;x+=1
 assert mask.sum()==13
 return bank,mask,indices
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();bank,mask,indices=decode(a.data)
 master=Image.open(ART/'imagegen-master.png').convert('RGBA');im=np.array(master.resize((96,112),Image.Resampling.LANCZOS));coverage=np.repeat(np.repeat(mask,8,axis=0),8,axis=1)
 im[~coverage]=0;im[coverage,3]=255
 out=Image.fromarray(im,'RGBA');raw=struct.pack('<4s6I',b'HDR1',1400304,8,12,14,0,0)+out.tobytes();a.out.mkdir(parents=True,exist_ok=True);stem='enemy-projectile304-304-8';out.save(a.out/(stem+'.png'));(a.out/(stem+'.hda')).write_bytes(raw)
 receipt={'source':'tyrian.shp/player-shot-bank','source_bank_bytes':len(bank),'source_bank_fnv64':fnv(bank),'source_bank_sha256':hashlib.sha256(bank).hexdigest(),'source_index':304,'material_role':140,'occupied_logical_cells':13,'logical_bbox':[4,5,5,5],'dimensions':[96,112],'logical_dimensions':[12,14],'anchor':[0,0],'rgba_fnv64':fnv(out.tobytes()),'hda_sha256':hashlib.sha256(raw).hexdigest(),'source_png_sha256':hashlib.sha256((a.out/(stem+'.png')).read_bytes()).hexdigest(),'master_sha256':hashlib.sha256((ART/'imagegen-master.png').read_bytes()).hexdigest(),'registration':'Full canvas LANCZOS; exact original opaque-cell mask, zero transparent RGB outside. No drawn/recolored pixels or changed game coordinates.'}
 (a.out/'art-inventory.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
