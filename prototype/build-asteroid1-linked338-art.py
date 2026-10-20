#!/usr/bin/env python3
"""Deterministic conversion of the imagegen-authored linked NEWSHP master.

Reads only named generated masters and the explicitly selected original bank.
Keeps exact original coverage, aligned live-state differences, and slices one
coherent platform. No generated geometry, recoloring or original-input edits.
"""
from pathlib import Path
import argparse, hashlib, json, struct
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/hd/artwork/asteroid1-linked338-v1'
BASES = (115,117,119,121,229,231,267,269)
STATES = ((115,'lower'),(117,'middle'),(119,'upper'),(121,'wreck'))
PLATFORM_CROP = (29,535,918,1583)
def fnv(raw):
    h=0xcbf29ce484222325
    for v in raw: h=((h^v)*0x100000001b3)&0xffffffffffffffff
    return f'0x{h:016x}'
def decode(bank, base):
    index=np.zeros((28,24),np.uint8); mask=np.zeros_like(index)
    for delta,dx,dy in ((0,0,0),(1,12,0),(19,0,14),(20,12,14)):
        p=struct.unpack_from('<H',bank,(base+delta-1)*2)[0];x=y=0
        while True:
            v=bank[p];p+=1
            if v==15: break
            x+=v&15; n=v>>4
            if not n: y+=1;x-=12
            else:
                for _ in range(n):
                    assert 0<=x<12 and 0<=y<14
                    index[y+dy,x+dx]=bank[p];mask[y+dy,x+dx]=255;p+=1;x+=1
    return index,mask
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    bank=(a.data/'newshp.shp').read_bytes();assert len(bank)==46204 and fnv(bank)=='0xe2413e3aeab4d908'
    decoded={b:decode(bank,b) for b in BASES}
    union=np.zeros((28,24),bool)
    for base in (117,119):union|=decoded[base][0]!=decoded[115][0]
    assert union.sum()==279
    enlarged_union=np.repeat(np.repeat(union,8,axis=0),8,axis=1)
    masters={name:Image.open(ART/f'imagegen-master-{name}.png').convert('RGBA') for _,name in STATES}
    # Uniform full-canvas registration keeps all four cap variants aligned.
    caps={name:np.array(im.resize((384,672),Image.Resampling.LANCZOS).crop((0,0,192,224))) for name,im in masters.items()}
    # The platform is one generated master, normalized once, then sliced.
    platform=masters['lower'].crop(PLATFORM_CROP).resize((384,448),Image.Resampling.LANCZOS)
    images={229:platform.crop((0,0,192,224)),231:platform.crop((192,0,384,224)),267:platform.crop((0,224,192,448)),269:platform.crop((192,224,384,448))}
    for base,name in STATES:
        array=caps['lower'].copy() if base in (117,119) else caps[name].copy()
        if base in (117,119): array[enlarged_union]=caps[name][enlarged_union]
        images[base]=Image.fromarray(array,'RGBA')
    inventory={};a.out.mkdir(parents=True,exist_ok=True)
    for base in BASES:
        array=np.array(images[base]);alpha=np.repeat(np.repeat(decoded[base][1],8,axis=0),8,axis=1)
        array[:,:,3]=alpha;array[alpha==0,:3]=0;image=Image.fromarray(array,'RGBA')
        stem=f'enemy-newshp-{base}-8';image.save(a.out/(stem+'.png'))
        raw=struct.pack('<4s6I',b'HDR1',1350000+base,8,24,28,0,0)+image.tobytes();assert len(raw)==172060
        (a.out/(stem+'.hda')).write_bytes(raw)
        inventory[stem]={'record':338 if base<200 else {229:341,231:342,267:339,269:340}[base],'source_bank':'newshp.shp','logical_bank':20,'material_role':135,'base':base,'logical_size':[24,28],'source_occupied_cells':int((decoded[base][1]>0).sum()),'rgba_fnv64':fnv(image.tobytes()),'sha256':hashlib.sha256(raw).hexdigest()}
    (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
