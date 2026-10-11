from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent
im=Image.open(P/'earth-corrected-assembly.png').convert('RGBA')
assert im.getchannel('A').getextrema()==(255,255)
a=im.resize((384,448),Image.Resampling.LANCZOS);a.save(P/'assembly8x.png')
(P/'tiles8x').mkdir(exist_ok=True)
records=[]
for n,x,y in [(323,0,0),(324,192,0),(333,0,224),(334,192,224)]:
 name=f'terrain-shapesz-{n}-8.png';p=P/'tiles8x'/name
 a.crop((x,y,x+192,y+224)).save(p)
 records.append(dict(id=n,file='tiles8x/'+name,namespace='shapesZ',layer=1,logical_size=[24,28],anchor=[0,0],assembly_offset=[x//8,y//8],sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
r=Image.new('RGBA',(384,448))
for v in records:r.paste(Image.open(P/v['file']),tuple(z*8 for z in v['assembly_offset']))
assert r.tobytes()==a.tobytes()
manifest=dict(identity='terrain-underlay323-324-333-334-hd-v1',classification='static opaque physical metal/ochre terrain assembly',logical_assembly=[48,56],density=8,source_size=list(im.size),transform='Full source extent to 384x448 LANCZOS once, then exact fixed quadrants; no crop, per-tile movement or runtime anchor change.',alpha=255,tiles=records,registration='Terrain is one logical pixel above accepted enemy installation; preserve original tile draws. Enemy overlay unchanged.',scope='Layer1 shapesZ IDs323,324,333,334 only. Roads and accepted sibling321/322/331/332 excluded.',limitations=['Offline contexts include provisional roads. Actual runtime intact and linked-destruction reveal review pending.','Earth texture phase is not pixel-identical at all neighboring boundaries.'],source_sha256=hashlib.sha256((P/'earth-corrected-assembly.png').read_bytes()).hexdigest())
(P/'candidate-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(opaque=True,exact_reassembly=True,tiles=records),indent=2))
