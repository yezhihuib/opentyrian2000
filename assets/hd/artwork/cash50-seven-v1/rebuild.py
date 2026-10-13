from pathlib import Path
from PIL import Image
from scipy.ndimage import gaussian_filter
import numpy as np,json,hashlib,struct,sys
P=Path(__file__).resolve().parent;O=Path(sys.argv[1]).absolute();sha=lambda b:hashlib.sha256(b).hexdigest()
if O.exists():raise SystemExit('Output must not exist')
I=json.load(open(P/'inventory.json'))if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
O.mkdir(parents=True);C=json.load(open(P/'proof/geometry-and-source-hashes.json'));master=Image.open(P/'sources/generated-coins.png').convert('RGBA');rows=[]
for k,r in enumerate(C['frames']):
 b=r['id'];sb=r['alpha_bbox_xyxy_exclusive'];cell=master.crop((k%3*master.width//3,k//3*master.height//2,(k%3+1)*master.width//3,(k//3+1)*master.height//2))if b!=204 else Image.open(P/'sources/generated-popup50.png').convert('RGBA');gb=cell.getchannel('A').point(lambda x:255 if x>12 else 0).getbbox();piece=cell.crop(gb).resize(((sb[2]-sb[0])*8,(sb[3]-sb[1])*8),Image.Resampling.LANCZOS);im=Image.new('RGBA',(96,112));im.alpha_composite(piece,(sb[0]*8,sb[1]*8));a=np.array(im);support=np.array(Image.open(P/f'masks/mask-{b}.png').resize((96,112),Image.Resampling.NEAREST))>0;soft=np.clip((gaussian_filter(support.astype(float),2)-.5)/.35,0,1);a[:,:,3]=np.minimum(a[:,:,3],np.round(soft*255))*support;assert not np.any((a[:,:,3]>0)&~support);im=Image.fromarray(a)
 prefix='coin50-bank11'if b!=204 else'coin50-value-newsh6';key=1160000+b if b!=204 else 1170204;f=O/f'{prefix}-{b}-8.png';im.save(f);raw=im.tobytes();hda=b'HDR1'+struct.pack('<6I',key,8,12,14,0,0)+raw;assert len(hda)==43036;(O/f'{prefix}-{b}-8.hda').write_bytes(hda);row={'id':b,'key':key,'prefix':prefix,'PNG_SHA256':sha(f.read_bytes()),'RGBA_SHA256':sha(raw),'HDA_SHA256':sha(hda),'outside_source_support':0,'fractional_samples':int(((a[:,:,3]>0)&(a[:,:,3]<255)).sum())};rows.append(row)
 if I:assert row==next(q for q in I['outputs']if q['id']==b),b
(O/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'outputs':rows},indent=2)+'\n');print('PASS seven exact coin50 outputs')
