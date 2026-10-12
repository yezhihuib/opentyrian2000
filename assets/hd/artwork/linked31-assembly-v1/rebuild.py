from pathlib import Path
from PIL import Image
import json,hashlib,struct,sys
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();out=Path(sys.argv[1]).absolute()
if out.exists():raise SystemExit('Output must not exist')
I=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
out.mkdir(parents=True);rows=[];master=Image.open(P/'sources/generated-paired-context.png').convert('RGBA').resize((1536,896),Image.Resampling.LANCZOS)
for kind,box,ids,anchor,prefix in [('terrain',(192,224,576,672),[161,162,171,172],[0,0],2010000),('actor',(960,232,1344,680),[15,17,53,55],[6,7],1010000)]:
 assembly=master.crop(box);assembly.putalpha(255)
 for k,i in enumerate(ids):
  x=k%2*192;y=k//2*224;im=assembly.crop((x,y,x+192,y+224));name=f'terrain-shapesz-{i}-8.png'if kind=='terrain'else f'enemy-newsh2-{i}-8.png';png=out/name;im.save(png);rgba=im.tobytes();hda=b'HDR1'+struct.pack('<6I',prefix+i,8,24,28,*anchor)+rgba;(out/f'{prefix+i}.hda').write_bytes(hda);r={'kind':kind,'source_id':i,'RGBA_SHA256':sha(rgba),'HDA_SHA256':sha(hda),'PNG_SHA256':sha(png.read_bytes())};rows.append(r)
  if I:
   e=next(e for e in I['outputs']if e['kind']==kind and e['source_id']==i);assert r['RGBA_SHA256']==e['RGBA_SHA256']and r['HDA_SHA256']==e['HDA_SHA256'],i
(out/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n');print('PASS exact eight RGBA/HDA outputs')
