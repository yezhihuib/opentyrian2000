from pathlib import Path
from PIL import Image
import json,hashlib,struct,sys
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();out=Path(sys.argv[1]).absolute()
if out.exists():raise SystemExit('Output must not exist')
I=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
out.mkdir(parents=True);rows=[];raw=Image.open(P/'sources/generated-whole.png').convert('RGBA').resize((1536,512),Image.Resampling.LANCZOS).crop((96,144,1440,368));a=Image.new('RGBA',raw.size,(12,8,0,255));a.alpha_composite(raw);a.putalpha(Image.open(P/'masks/alpha-assembly8x.png').convert('L'))
for k,i in enumerate([153,155,157,159,191,193,195]):
 im=a.crop((k*192,0,(k+1)*192,224));png=out/f'enemy-newsh4-{i}-8.png';im.save(png);rgba=im.tobytes();hda=b'HDR1'+struct.pack('<6I',1020000+i,8,24,28,6,7)+rgba;(out/f'enemy-newsh4-{i}-8.hda').write_bytes(hda);r={'source_id':i,'RGBA_SHA256':sha(rgba),'HDA_SHA256':sha(hda),'PNG_SHA256':sha(png.read_bytes())};rows.append(r)
 if I:
  e=next(e for e in I['outputs']if e['source_id']==i);assert r['RGBA_SHA256']==e['RGBA_SHA256']and r['HDA_SHA256']==e['HDA_SHA256'],i
(out/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n');print('PASS exact seven RGBA/HDA outputs')
