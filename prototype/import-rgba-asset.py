"""Validate a completed dot PNG and pack exact unpremultiplied RGBA bytes.
No painting, resizing, palette quantization or silhouette changes occur here.
"""
from pathlib import Path
import argparse,hashlib,json,struct
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('png',type=Path);p.add_argument('--kind',choices=['ship','bullet'],required=True);p.add_argument('--id',type=int,required=True);p.add_argument('--density',type=int,choices=[4,8],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if (a.kind=='ship' and a.id not in [229,231,233,235,237]) or (a.kind=='bullet' and a.id!=59):raise SystemExit('Unsupported asset identity')
w,h,ax,ay,bank=(24,28,5,7,9) if a.kind=='ship' else (12,14,-1,0,8)
im=Image.open(a.png);im.load()
if im.size!=(w*a.density,h*a.density):raise SystemExit(f'Wrong canvas: expected {(w*a.density,h*a.density)}, got {im.size}; no resize is performed')
if 'A' not in im.getbands() and 'transparency' not in im.info:raise SystemExit('PNG must contain explicit transparency')
rgba=im.convert('RGBA');raw=rgba.tobytes();header=struct.pack('<4sIIIIii',b'HDR1',bank*10000+a.id,a.density,w,h,ax,ay)
a.output.mkdir(parents=True,exist_ok=True);dest=a.output/f'{a.kind}-{a.id}-{a.density}.hda';dest.write_bytes(header+raw)
assert dest.read_bytes()[28:]==raw
record={'source_png':a.png.name,'source_sha256':hashlib.sha256(a.png.read_bytes()).hexdigest(),'packed_file':dest.name,'packed_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'logical_size':[w,h],'pixel_size':list(rgba.size),'anchor_xy':[ax,ay],'density':a.density,'rgba_bytes_preserved':True,'opaque_or_partial_colors':len(set((r,g,b,a) for r,g,b,a in rgba.getdata() if a)),'alpha_bbox':rgba.getbbox(),'quantized':False}
(dest.with_suffix('.json')).write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
