from pathlib import Path
from PIL import Image
import json,struct,hashlib,sys
P=Path(__file__).resolve().parent;out=Path(sys.argv[1]).absolute();sha=lambda b:hashlib.sha256(b).hexdigest()
if out.exists():raise SystemExit('Output must not exist')
i=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
if i:
 for f,h in i['inputs'].items():assert sha((P/f).read_bytes())==h,f
out.mkdir(parents=True);a=Image.open(P/'sources/generated-six-frame.png').convert('RGBA');rows=[]
for k,b in enumerate([171,190,209,228,247,266]):
 alpha=Image.open(P/f'masks/alpha-{b}.png').convert('L');box=alpha.getbbox();cell=a.crop((k%3*a.width//3,k//3*a.height//2,(k%3+1)*a.width//3,(k//3+1)*a.height//2));gb=cell.getchannel('A').point(lambda v:255 if v>128 else 0).getbbox();piece=cell.crop(gb).resize(((box[2]-box[0])*8,(box[3]-box[1])*8),Image.Resampling.LANCZOS);im=Image.new('RGBA',(96,112),(8,6,2,255));im.alpha_composite(piece,(box[0]*8,box[1]*8));im.putalpha(alpha.resize(im.size,Image.Resampling.NEAREST));png=out/f'enemy-newsh2-{b}-8.png';im.save(png);raw=im.tobytes();hda=b'HDR1'+struct.pack('<6I',1010000+b,8,12,14,0,0)+raw;(out/f'enemy-newsh2-{b}-8.hda').write_bytes(hda);r={'base':b,'RGBA_SHA256':sha(raw),'PNG_SHA256':sha(png.read_bytes()),'HDA_SHA256':sha(hda),'source_bbox':box,'generated_bbox':gb};rows.append(r)
 if i:
  e=next(r for r in i['outputs']if r['base']==b);assert r['RGBA_SHA256']==e['RGBA_SHA256']and r['HDA_SHA256']==e['HDA_SHA256']
(out/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n');print('PASS six exact small RGBA/HDA outputs')
