from pathlib import Path
from PIL import Image
import json,hashlib,struct,sys
P=Path(__file__).resolve().parent;sha=lambda b:hashlib.sha256(b).hexdigest();out=Path(sys.argv[1]).absolute()
if out.exists():raise SystemExit('Output must not exist')
I=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
out.mkdir(parents=True);rows=[];master=Image.open(P/'sources/generated-fivepose.png').convert('RGBA').resize((768,640),Image.Resampling.LANCZOS)
for k,i in enumerate([159,161,163,165,167]):
 x=k%3*256+32;y=k//3*320+48;raw=master.crop((x,y,x+192,y+224));im=Image.new('RGBA',raw.size,(12,12,12,255));im.alpha_composite(raw);im.putalpha(Image.open(P/f'masks/alpha-{i}.png').convert('L'));png=out/f'enemy-newsh2-{i}-8.png';im.save(png);rgba=im.tobytes();hda=b'HDR1'+struct.pack('<6I',1010000+i,8,24,28,6,7)+rgba;(out/f'{1010000+i}.hda').write_bytes(hda);r={'source_id':i,'RGBA_SHA256':sha(rgba),'HDA_SHA256':sha(hda),'PNG_SHA256':sha(png.read_bytes())};rows.append(r)
 if I:
  e=next(e for e in I['outputs']if e['source_id']==i);assert r['RGBA_SHA256']==e['RGBA_SHA256']and r['HDA_SHA256']==e['HDA_SHA256'],i
(out/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n');print('PASS exact five RGBA/HDA outputs')
