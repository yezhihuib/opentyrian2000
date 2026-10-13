from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json,hashlib,struct,sys
P=Path(__file__).resolve().parent;out=Path(sys.argv[1]).absolute();sha=lambda b:hashlib.sha256(b).hexdigest()
if out.exists():raise SystemExit('Output must not exist')
I=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
out.mkdir(parents=True);C=json.load(open(P/'proof/source-contract.json'));reg=json.load(open(P/'proof/intact-registration.json'));sb=reg['source_bbox'];gb=reg['generated_bbox']
def registered(name):
 raw=Image.open(P/'sources'/name).convert('RGBA');piece=raw.crop(gb).resize(((sb[2]-sb[0])*8,(sb[3]-sb[1])*8),Image.Resampling.LANCZOS);im=Image.new('RGBA',(960,896),(12,10,7,255));im.alpha_composite(piece,(sb[0]*8,sb[1]*8));return im
intact=registered('generated-intact-v2.png');intact.putalpha(Image.open(P/'masks/intact-alpha.png').resize((960,896),Image.Resampling.NEAREST));damage=Image.composite(registered('generated-damage.png'),intact,Image.open(P/'masks/damage-change-mask8x.png').convert('L'));damage.putalpha(Image.open(P/'masks/damage-alpha.png').resize((960,896),Image.Resampling.NEAREST));imgs={}
for c in C['components']:
 x,y=c['assembly_origin'];box=(x*8,y*8,(x+24)*8,(y+28)*8);b=c['intact_base'];imgs[b]=intact.crop(box);db=c.get('damage_base')
 if db is not None and db!=b:imgs[db]=damage.crop(box)
imgs[280]=imgs[128].copy()
for b in[238,278,282]:imgs[b]=Image.new('RGBA',(192,224))
base=intact.crop((384,224,576,448));a=Image.open(P/'sources/generated-center-lights.png').convert('RGBA');mask=Image.new('L',(36,36));ImageDraw.Draw(mask).ellipse((1,1,34,34),fill=255);mask=mask.filter(ImageFilter.GaussianBlur(1))
for k,b in enumerate([1,3,5,7,39,41,43,45]):
 cell=a.crop((k%4*a.width//4,k//4*a.height//2,(k%4+1)*a.width//4,(k//4+1)*a.height//2));box=cell.getchannel('A').point(lambda v:255 if v>160 else 0).getbbox();tile=cell.crop(box).resize((192,224),Image.Resampling.LANCZOS);im=base.copy();im.paste(tile.crop((78,128,114,164)),(78,166),mask);imgs[b]=im
rows=[]
for b,im in sorted(imgs.items()):
 im.putalpha(Image.open(P/f'masks/mask-newsh4-{b}.png').resize((192,224),Image.Resampling.NEAREST));png=out/f'enemy-newsh4-{b}-8.png';im.save(png);raw=im.tobytes();hda=b'HDR1'+struct.pack('<6I',1020000+b,8,24,28,6,7)+raw;(out/f'enemy-newsh4-{b}-8.hda').write_bytes(hda);r={'base':b,'PNG_SHA256':sha(png.read_bytes()),'RGBA_SHA256':sha(raw),'HDA_SHA256':sha(hda),'empty':b in[238,278,282]};rows.append(r)
 if I:
  e=next(r for r in I['outputs']if r['base']==b);assert all(r[f]==e[f]for f in['RGBA_SHA256','HDA_SHA256']),b
assert len(rows)==43
(out/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n');print('PASS43 outputs:40 nonempty and3 intentionalempty')
