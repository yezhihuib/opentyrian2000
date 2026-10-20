#!/usr/bin/env python3
"""Register three imagegen clamshell poses to exact original per-pose support."""
from pathlib import Path
import argparse,hashlib,json,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-clamshell285-v1'
BASES=(157,159,161)
MASTERS={157:'master157-v2.png',159:'master159-v1.png',161:'master161-v1.png'}
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
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 bank=(a.data/'newshd.shp').read_bytes();assert len(bank)==42012 and fnv(bank)=='0x913975450e0fc00d';inventory={}
 for b in BASES:
  indices,coverage=decode(bank,b);mask=coverage!=0;y,x=np.where(mask);box=(int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1));im=Image.open(ART/MASTERS[b]).convert('RGBA');v=np.array(im);my,mx=np.where(v[:,:,3]>128);crop=(int(mx.min()),int(my.min()),int(mx.max()+1),int(my.max()+1));piece=im.crop(crop).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.LANCZOS)
  rgba=np.zeros((224,192,4),np.uint8);rgba[box[1]*8:box[3]*8,box[0]*8:box[2]*8]=np.array(piece);support=np.repeat(np.repeat(mask,8,0),8,1);rgba[~support]=0
  out=Image.fromarray(rgba,'RGBA');stem=f'enemy-newshd-{b}-8';out.save(a.out/(stem+'.png'));raw=struct.pack('<4s6I',b'HDR1',1430000+b,8,24,28,0,0)+out.tobytes();(a.out/(stem+'.hda')).write_bytes(raw)
  inventory[stem]={'record':285,'source_bank':'newshd.shp','logical_bank':8,'material_role':143,'base':b,'logical_size':[24,28],'source_occupied_cells':int(mask.sum()),'represented_logical_cells':int((rgba[:,:,3]>0).reshape(28,8,24,8).any(axis=(1,3)).sum()),'source_bbox':box,'master':MASTERS[b],'master_crop':crop,'rgba_fnv64':fnv(out.tobytes()),'sha256':hashlib.sha256(raw).hexdigest()}
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
