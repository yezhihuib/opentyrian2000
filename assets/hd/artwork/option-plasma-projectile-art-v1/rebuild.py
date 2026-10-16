#!/usr/bin/env python3
"""Reproduce Plasma Storm9 pilot using only its generated master.

No original game source, mask, palette, gameplay capture or private audit is read.
Optional HDA IDs are supplied by the integrating renderer; no namespace is guessed.
"""
from pathlib import Path
from PIL import Image, __version__ as pillow_version
import argparse, hashlib, json, struct

HERE=Path(__file__).resolve().parent
SHA=lambda data:hashlib.sha256(data).hexdigest()
ap=argparse.ArgumentParser()
ap.add_argument('--output',type=Path,required=True,help='New output directory')
ap.add_argument('--resource-ids',type=int,nargs=3,help='Explicit renderer HDA IDs for pieces 22,23,24')
args=ap.parse_args()
contract=json.loads((HERE/'contract.json').read_text())
master_path=HERE/contract['master']['path']
assert SHA(master_path.read_bytes())==contract['master']['sha256']
im=Image.open(master_path).convert('RGBA')
assert im.size==(1167,1347)
fitted=im.resize((520,600),Image.Resampling.LANCZOS)
args.output.mkdir(parents=True,exist_ok=False)
records=[]
for slot,(idx,w,h,y) in enumerate([(22,62,24,0),(23,65,28,24),(24,62,23,52)]):
    p8=fitted.crop((0,y*8,w*8,(y+h)*8))
    for density in [8,4]:
        image=p8 if density==8 else p8.resize((w*density,h*density),Image.Resampling.LANCZOS)
        name=f'option-table5-{idx}-{density}.png'
        path=args.output/name
        image.save(path)
        rgba=image.tobytes()
        expected=next(e for e in contract['pieces'] if e['index']==idx and e['density']==density)
        assert SHA(path.read_bytes())==expected['png_sha256'],name
        assert SHA(rgba)==expected['rgba_sha256'],name
        entry={'index':idx,'density':density,'logical_size':[w,h],'anchor':[0,0],
            'png':name,'png_sha256':SHA(path.read_bytes()),'rgba_sha256':SHA(rgba)}
        if args.resource_ids:
            header=[args.resource_ids[slot],density,w,h,0,0]
            hda=struct.pack('<4s6I',b'HDR1',*header)+rgba
            hp=path.with_suffix('.hda');hp.write_bytes(hda)
            entry.update(hda=hp.name,hda_header_u32=header,hda_sha256=SHA(hda))
        records.append(entry)
receipt={'pillow':pillow_version,'master_sha256':contract['master']['sha256'],'generated_only':True,'outputs':records}
(args.output/'rebuild-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
