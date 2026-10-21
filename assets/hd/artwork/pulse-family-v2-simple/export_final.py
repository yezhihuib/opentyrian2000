#!/usr/bin/env python3
"""Approved whole-image crop, isotropic 1/10 resize, transparent padding only.
No recoloring, alpha cleaning, repainting or independent lobe placement.
The HDR1 payload is an exact copy of final straight RGBA pixels.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,struct
ROOT=Path(__file__).resolve().parent
RECIPES={58:([450,260,710,1080],[35,2]),59:([300,240,860,1060],[20,1]),60:([240,250,920,1130],[14,1]),62:([130,250,1030,1070],[3,2]),165:([250,190,910,990],[15,3])}
def sha(b):return hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for v in b:h=((h^v)*1099511628211)&((1<<64)-1)
 return f'{h:016x}'
def main():
 for d in ('exports','runtime'): (ROOT/d).mkdir(exist_ok=True)
 rows=[]
 for i,(crop,offset) in RECIPES.items():
  p=ROOT/'selected-masters'/f'pulse-{i}-master.png'; im=Image.open(p).convert('RGBA')
  c=im.crop(crop);size=(c.width//10,c.height//10);assert c.width%10==c.height%10==0
  v=c.resize(size,Image.Resampling.LANCZOS);out=Image.new('RGBA',(96,112));out.paste(v,tuple(offset))
  png=ROOT/'exports'/f'bullet-{i}-8.png';out.save(png)
  header=[80000+i,8,12,14,4294967295 if i==59 else 0,0]
  payload=out.tobytes();data=b'HDR1'+struct.pack('<6I',*header)+payload;hda=ROOT/'runtime'/f'bullet-{i}-8.hda';hda.write_bytes(data)
  a=out.getchannel('A');edge=list(a.crop((0,0,96,1)).getdata())+list(a.crop((0,111,96,112)).getdata())+list(a.crop((0,0,1,112)).getdata())+list(a.crop((95,0,96,112)).getdata())
  rows.append(dict(identity=80000+i,master=str(p.relative_to(ROOT)),master_sha256=sha(p.read_bytes()),master_size=list(im.size),crop=crop,resize=list(size),scale=[1,10],resampler='Lanczos',paste=offset,canvas=[96,112],source_png=str(png.relative_to(ROOT)),source_png_sha256=sha(png.read_bytes()),hda=str(hda.relative_to(ROOT)),sha256=sha(data),bytes=len(data),header_u32=header,payload_fnv64=fnv(payload),alpha_bbox_gt16=a.point(lambda v:255 if v>16 else 0).getbbox(),alpha_bbox_gt128=a.point(lambda v:255 if v>128 else 0).getbbox(),max_outer_alpha=max(edge)))
 j=dict(schema='opentyrian-pulse-art-revision-v2',scope='Exactly five revised Pulse head payloads; source identities, weapon records and roles unchanged.',approval='User accepted simpler imagegen direction and whole-image crop, equal resize and transparent padding. No approval of gameplay or other assets is inferred.',image_editing='Whole-image crop, uniform scale 1/10, transparent padding only; no recolor, alpha cleanup, per-lobe shift or procedural drawing.',anchor='Resource59 retains metadata(-1,0), registration baked in canvas; do not apply second offset.',frames=rows)
 (ROOT/'candidate-manifest.json').write_text(json.dumps(j,indent=2)+'\n')
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
