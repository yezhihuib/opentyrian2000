from pathlib import Path
from PIL import Image
import json,hashlib,struct,sys
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();out=Path(sys.argv[1]).absolute()
if out.exists():raise SystemExit('Output must not exist')
I=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
out.mkdir(parents=True);rows=[]
for i in [190,200]:
 im=Image.open(P/f'sources/generated{i}-context.png').convert('RGBA').resize((576,672),Image.Resampling.LANCZOS).crop((192,224,384,448));im.putalpha(255);png=out/f'terrain-shapesz-{i}-8.png';im.save(png);raw=im.tobytes();hda=b'HDR1'+struct.pack('<6I',2010000+i,8,24,28,0,0)+raw;(out/f'{2010000+i}.hda').write_bytes(hda);r={'source_id':i,'RGBA_SHA256':sha(raw),'HDA_SHA256':sha(hda),'PNG_SHA256':sha(png.read_bytes())};rows.append(r)
 if I:
  e=next(e for e in I['outputs']if e['source_id']==i);assert r['RGBA_SHA256']==e['RGBA_SHA256']and r['HDA_SHA256']==e['HDA_SHA256'],i
(out/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n');print('PASS exact two RGBA/HDA outputs')
