#!/usr/bin/env python3
"""Deterministically register imagegen NEWSHS272 pulse artwork.

Only named authored masters and the exact original NEWSHS bank are read.
One common opaque metal housing is shared outside the original288-cell index
difference union. Generated state samples supply that union without recoloring,
code-drawn geometry, additional states or original-input changes.
"""
from pathlib import Path
import argparse, hashlib, json, struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-pulsing272-v1'
BASES=(229,231,233,235)
def fnv(raw):
    h=0xcbf29ce484222325
    for v in raw:h=((h^v)*0x100000001b3)&0xffffffffffffffff
    return f'0x{h:016x}'
def decode(bank,base):
    indices=np.zeros((28,24),np.uint8);coverage=np.zeros_like(indices)
    for delta,dx,dy in ((0,0,0),(1,12,0),(19,0,14),(20,12,14)):
        p=struct.unpack_from('<H',bank,2*(base+delta-1))[0];x=y=0
        while True:
            v=bank[p];p+=1
            if v==15:break
            x+=v&15;n=v>>4
            if not n:y+=1;x-=12
            else:
                for _ in range(n):
                    assert 0<=x<12 and 0<=y<14
                    indices[y+dy,x+dx]=bank[p];coverage[y+dy,x+dx]=255;p+=1;x+=1
    return indices,coverage
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    bank=(a.data/'newshs.shp').read_bytes();assert len(bank)==46566 and fnv(bank)=='0xf22ec1295ced5d11'
    decoded={b:decode(bank,b)for b in BASES};union=np.zeros((28,24),bool)
    for b in BASES[1:]:union|=decoded[b][0]!=decoded[229][0]
    yy,xx=np.where(union);assert union.sum()==288 and [int(xx.min()),int(yy.min()),int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)]==[4,4,15,20]
    allowed=np.repeat(np.repeat(union,8,axis=0),8,axis=1)
    masters={b:np.array(Image.open(ART/f'imagegen-master-{b}.png').convert('RGBA').resize((192,224),Image.Resampling.LANCZOS))for b in BASES}
    inventory={};a.out.mkdir(parents=True,exist_ok=True)
    for b in BASES:
        rgba=masters[229].copy();rgba[allowed]=masters[b][allowed];rgba[:,:,3]=255
        assert np.all(decoded[b][1]==255)
        im=Image.fromarray(rgba,'RGBA');stem=f'enemy-newshs-{b}-8';im.save(a.out/(stem+'.png'))
        raw=struct.pack('<4s6I',b'HDR1',1360000+b,8,24,28,0,0)+im.tobytes();assert len(raw)==172060
        (a.out/(stem+'.hda')).write_bytes(raw)
        inventory[stem]={'record':272,'source_bank':'newshs.shp','logical_bank':23,'material_role':136,'base':b,'size':1,'logical_size':[24,28],'source_occupied_cells':672,'rgba_fnv64':fnv(im.tobytes()),'sha256':hashlib.sha256(raw).hexdigest()}
    (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
