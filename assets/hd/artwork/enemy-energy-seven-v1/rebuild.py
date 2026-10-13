from pathlib import Path
from PIL import Image
from scipy.ndimage import gaussian_filter
import numpy as np,json,hashlib,struct,sys
P=Path(__file__).resolve().parent;O=Path(sys.argv[1]).absolute()
if O.exists():raise SystemExit('Output must not exist')
sha=lambda b:hashlib.sha256(b).hexdigest()
I=json.load(open(P/'inventory.json'))if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
O.mkdir(parents=True)
C=json.load(open(P/'proof/source-contract.json'));master=Image.open(P/'sources/generated-master.png').convert('RGBA');rows=[]
for k,r in enumerate(C['sprites']):
 b=r['id'];x=k%4*master.width//4;y=k//4*master.height//2
 cell=master.crop((x,y,(k%4+1)*master.width//4,(k//4+1)*master.height//2));gb=cell.getchannel('A').point(lambda x:255 if x>12 else 0).getbbox();sb=r['bbox']
 piece=cell.crop(gb).resize(((sb[2]-sb[0])*8,(sb[3]-sb[1])*8),Image.Resampling.LANCZOS)
 im=Image.new('RGBA',(96,112));im.alpha_composite(piece,(sb[0]*8,sb[1]*8));a=np.array(im)
 support=np.array(Image.open(P/f'masks/mask-bank8-{b}.png').resize((96,112),Image.Resampling.NEAREST))>0
 soft=np.clip((gaussian_filter(support.astype(float),2)-.5)/.35,0,1);a[:,:,3]=np.minimum(a[:,:,3],np.round(soft*255))*support
 assert not np.any((a[:,:,3]>0)&~support)
 im=Image.fromarray(a);png=O/f'enemy-energy-{b}-8.png';im.save(png);raw=im.tobytes();hda=b'HDR1'+struct.pack('<6I',1110000+b,8,12,14,0,0)+raw;(O/f'enemy-energy-{b}-8.hda').write_bytes(hda)
 row={'id':b,'PNG_SHA256':sha(png.read_bytes()),'RGBA_SHA256':sha(raw),'HDA_SHA256':sha(hda),'source_bbox':sb,'generated_cell_bbox':list(gb),'outside_support':0,'fractional_alpha_samples':int(((a[:,:,3]>0)&(a[:,:,3]<255)).sum())};rows.append(row)
 if I:assert row==next(q for q in I['outputs']if q['id']==b),b
(O/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n')
print('PASS seven enemy energy outputs, exact source support outer bound')
