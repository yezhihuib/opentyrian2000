"""Reproduce trial HUD art from the generated component atlas and reviewed mask.
No source game pixel data is bundled. No repaint, sharpening, recoloring or internal warping.
"""
from pathlib import Path
import argparse,struct,json,hashlib
from PIL import Image
P=Path(__file__).parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.exists():p.error('Choose a new output directory')
out.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for c in b:h=((h^c)*1099511628211)&((1<<64)-1)
 return h
src=Image.open(P/'generated-component-master.png').convert('RGB');assert src.size==(1254,1254)
mask=Image.open(P/'approved-mask-6667.png').convert('L');assert mask.size==(320,200);m=mask.tobytes();assert set(m)<={0,255} and sum(c>0 for c in m)==6667
for y in range(184):assert not any(m[y*320:y*320+264])
parts=[([28,27,575,1124],[264,0,320,112]),([654,27,1202,890],[264,112,320,200]),([28,1164,1100,1229],[0,184,264,200])]
frame=Image.new('RGBA',(1280,800))
for crop,(x1,y1,x2,y2) in parts:frame.paste(src.crop(crop).resize(((x2-x1)*4,(y2-y1)*4),Image.Resampling.LANCZOS),(x1*4,y1*4))
frame.putalpha(mask.resize(frame.size,Image.Resampling.NEAREST));raw=frame.tobytes();frame.save(out/'hud-static-overlay-4x.png');mask.save(out/'static-mask-1x.png')
source_hash=0x14c1441f3d5dc0e2
header=struct.pack('<4s8I3QI',b'HUD1',1,320,200,4,0,0,64000,4096000,source_hash,fnv(m),fnv(raw),0);assert len(header)==64
resource=header+m+raw;(out/'gameplay-hud-v1.hda').write_bytes(resource)
v={'art_revision':'v5-components','status':'Frozen candidate for guarded trial only; pending user feedback','format':'HUD1-v1','source_pic3_fnv1a64':f'{source_hash:016x}','mask_fnv1a64':f'{fnv(m):016x}','rgba_fnv1a64':f'{fnv(raw):016x}','mask_decoded_sha256':sha(m),'rgba_decoded_sha256':sha(raw),'overlay_png_sha256':sha((out/'hud-static-overlay-4x.png').read_bytes()),'hda_sha256':sha(resource),'hda_bytes':len(resource),'owned_logical_pixels':6667,'added_reviewed_static_pixels':310,'source_game_pixels_in_resource':False,'whole_component_crops_and_logical_placements':parts}
(out/'reproduction-validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
