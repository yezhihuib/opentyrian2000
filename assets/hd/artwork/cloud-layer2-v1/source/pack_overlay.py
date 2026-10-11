"""Pack only the 15 selected generated cloud assets; no repo or original RGB required."""
from pathlib import Path
from PIL import Image
import struct,json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('--png-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
records=[]
for id in [41,42,43,44,45,51,52,53,54,55,61,62,63,64,65]:
 name=f'terrain-shapesz-{id}-8';png=a.png_dir/(name+'.png');im=Image.open(png);assert im.mode=='RGBA' and im.size==(192,224)
 header=[2010000+id,8,24,28,0,0];raw=b'HDR1'+struct.pack('<6I',*header)+im.tobytes();(a.output/(name+'.hda')).write_bytes(raw)
 records.append({'id':id,'bank':'shapesz.dat','layer':2,'logical_size':[24,28],'anchor':[0,0],'density':8,'png':str(png.name),'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'hda':name+'.hda','header_u32':header,'sha256':hashlib.sha256(raw).hexdigest()})
(a.output/'cloud-selected-manifest.json').write_text(json.dumps({'schema':'opentyrian-selected-cloud-family-v1','assets':records,'original_game_RGB_included':False,'palette_blended_wild':'Original fallback, not HD; requires binder guard','scope':'15 cloud family IDs observed in first522ticks of episode1 physical-level9; does not upgrade ground or assert whole-level topology.'},indent=2))
