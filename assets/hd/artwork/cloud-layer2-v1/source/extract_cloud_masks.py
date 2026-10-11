"""Extract only the 15 runtime opacity masks from user-owned original data.
This is not raster drawing: it decodes the engine's index0 transparency rule.
No original RGB or complete game atlas is embedded in this candidate package.
"""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
ids={41,42,43,44,45,51,52,53,54,55,61,62,63,64,65};data=(a.data/'shapesz.dat').read_bytes();off=0;a.out.mkdir(parents=True,exist_ok=True);records=[]
for i in range(1,601):
 blank=data[off];off+=1
 indices=bytes(672) if blank else data[off:off+672]
 if not blank:off+=672
 if i in ids:
  pixels=b''.join(bytes((0,0,0,255 if v else 0)) for v in indices)
  Image.frombytes('RGBA',(24,28),pixels).save(a.out/f'shapesz-{i}-rgba.png');records.append({'id':i,'indices_sha256':hashlib.sha256(indices).hexdigest()})
(a.out/'source-mask-hashes.json').write_text(json.dumps({'shapesz_sha256':hashlib.sha256(data).hexdigest(),'masks':records},indent=2))
