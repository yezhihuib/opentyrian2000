#!/usr/bin/env python3
"""Deterministic registration only: generated master -> one opaque tile.
No game/source data, material masks, palettes, borrowed backgrounds or artwork synthesis.
"""
from pathlib import Path
import argparse, hashlib, json
from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=ROOT);a=p.parse_args();O=a.output_dir;O.mkdir(parents=True,exist_ok=True)
source=ROOT/'raw/generated-master-03.png';src_bytes=source.read_bytes()
assert hashlib.sha256(src_bytes).hexdigest()==json.loads((ROOT/'registration.json').read_text())['master_sha256']
im=Image.open(source);assert im.size==(1161, 1354) and im.mode=='RGB'
# Full-frame registration; generated master is the sole creative pixel source.
tile=im.convert('RGBA').resize((192,224),Image.Resampling.LANCZOS)
assert tile.getchannel('A').getextrema()==(255,255)
tile.save(O/'tile356-192x224.png')
def fnv(data):
 h=14695981039346656037
 for v in data:h=((h^v)*1099511628211)&0xffffffffffffffff
 return f'{h:016x}'
rgba=tile.tobytes();receipt={'master_sha256':hashlib.sha256(src_bytes).hexdigest(),'png_sha256':hashlib.sha256((O/'tile356-192x224.png').read_bytes()).hexdigest(),'rgba_sha256':hashlib.sha256(rgba).hexdigest(),'rgba_fnv1a64':fnv(rgba),'rgba_bytes':len(rgba),'size':[192,224],'all_43008_pixels_fully_opaque':True,'anchor':[0,0],'density':8,'role':202,'hda_identity':2020356,'pillow_version':pillow_version,'crop':[0, 0, 1161, 1354],'rotation_degrees':0,'flip':False,'resampler':'Pillow Image.Resampling.LANCZOS','source_native_pixels_used_by_rebuild':False,'alpha_mask_used':False,'palette_used':False}
(O/'payload-pins.json').write_text(json.dumps(receipt,indent=2)+'\n')
# Clean authored-art sheet: only newly generated tile pixels, no original source/context.
preview=Image.new('RGB',(1000,660),(20,24,28));d=ImageDraw.Draw(preview)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(size):return ImageFont.truetype(font,size)
d.text((32,24),'BRONZE 356',font=f(30),fill=(239,224,187));d.text((32,65),'Opaque ground tile  /  generated artwork candidate',font=f(17),fill=(172,181,188))
d.text((32,113),'192 × 224  ·  enlarged 2×',font=f(16),fill=(218,222,225));preview.paste(tile.convert('RGB').resize((384,448),Image.Resampling.NEAREST),(32,143))
d.text((458,113),'24 × 28 check  ·  4×',font=f(16),fill=(218,222,225));preview.paste(tile.convert('RGB').resize((24,28),Image.Resampling.LANCZOS).resize((96,112),Image.Resampling.NEAREST),(458,143))
d.text((458,295),'Self-stack',font=f(16),fill=(218,222,225));d.text((458,319),'Same tile repeated vertically',font=f(13),fill=(172,181,188));
for y in [351,463]:preview.paste(tile.convert('RGB').resize((96,112),Image.Resampling.LANCZOS),(458,y))
d.text((655,113),'Delivery size  ·  1×',font=f(16),fill=(218,222,225));preview.paste(tile.convert('RGB'),(655,143))
for i,line in enumerate(['• Bronze object + generated earth','• No transparency, no water','• Existing neighboring tiles unchanged','• Offline art review; not runtime QA']):d.text((655,403+i*29),line,font=f(13),fill=(187,195,202))
d.line((32,614,968,614),fill=(64,70,75));d.text((32,629),'Clean preview — original game pixels excluded.',font=f(13),fill=(144,154,163))
(O/'preview').mkdir(exist_ok=True);preview.save(O/'preview/bronze356-clean-preview.png')
print(json.dumps(receipt,indent=2))
