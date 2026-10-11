from pathlib import Path
from PIL import Image
import struct,json,hashlib
R=Path(__file__).resolve().parent.parent;P=R/'output';O=R/'runtime-overlay';O.mkdir(exist_ok=True)
rows=[]
for id in [99,100,106,107,109,110,118,119,120]:
 name=f'terrain-shapesz-{id}-8';png=P/(name+'.png');im=Image.open(png);assert im.mode=='RGBA' and im.size==(192,224) and im.getchannel('A').getextrema()==(255,255);header=[2010000+id,8,24,28,0,0];raw=b'HDR1'+struct.pack('<6I',*header)+im.tobytes();(O/(name+'.hda')).write_bytes(raw);rows.append({'id':id,'layer':1,'bank':'shapesz.dat','header':header,'logical_size':[24,28],'density':8,'anchor':[0,0],'png':png.name,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest(),'hda_sha256':hashlib.sha256(raw).hexdigest()})
(O/'ground-nine-candidate-manifest.json').write_text(json.dumps({'status':'selected independent candidate; bounded visual/runtime checks passed, engineering integration pending','scope':'first15 brown nine-ID family only; no fulllevel claim','assets':rows},indent=2)+'\n');print('Packed9 opaque ground HDR1 assets')
