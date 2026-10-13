from pathlib import Path
from PIL import Image
from scipy.ndimage import gaussian_filter
import numpy as np,json,hashlib,struct,sys
P=Path(__file__).resolve().parent;O=Path(sys.argv[1]).absolute();sha=lambda b:hashlib.sha256(b).hexdigest()
if O.exists():raise SystemExit('Output must not exist')
I=json.load(open(P/'inventory.json'))if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
O.mkdir(parents=True);C=json.load(open(P/'proof/geometry-and-source-hashes.json'));rows=[];alphas=[]
for r in C['frames']:
 b=r['id'];sb=r['alpha_bbox_xyxy_exclusive'];im=Image.open(P/'sources'/('generated-gem.png'if b!=169 else'generated-popup100.png')).convert('RGBA');gb=im.getchannel('A').point(lambda x:255 if x>12 else 0).getbbox();piece=im.crop(gb).resize(((sb[2]-sb[0])*8,(sb[3]-sb[1])*8),Image.Resampling.LANCZOS);im=Image.new('RGBA',(96,112));im.paste(piece,(sb[0]*8,sb[1]*8));a=np.array(im);support=np.array(Image.open(P/f'masks/mask-{b}.png').resize((96,112),Image.Resampling.NEAREST))>0;soft=np.clip((gaussian_filter(support.astype(float),2)-.5)/.35,0,1);a[:,:,3]=np.minimum(a[:,:,3],np.rint(soft*255).astype('uint8'))*support;assert not np.any((a[:,:,3]>0)&~support)
 if b!=169:
  rgb=a[:,:,:3].astype(float)*.85;lum=rgb.max(2)/255;a[:,:,:3]=np.rint(np.clip(rgb+(b-32)*np.array([20,20,16])*(.20+1.20*lum[:,:,None]),0,255)).astype('uint8');alphas.append(a[:,:,3].tobytes())
 im=Image.fromarray(a);prefix='gem100-bank11'if b!=169 else'gem100-value-newsh6';key=1180000+b if b!=169 else 1190169;f=O/f'{prefix}-{b}-8.png';im.save(f);raw=im.tobytes();hda=b'HDR1'+struct.pack('<6I',key,8,12,14,0,0)+raw;assert len(hda)==43036;(O/f'{prefix}-{b}-8.hda').write_bytes(hda);fnv=14695981039346656037
 for v in raw:fnv=((fnv^v)*1099511628211)&0xffffffffffffffff
 row={'id':b,'key':key,'prefix':prefix,'PNG_SHA256':sha(f.read_bytes()),'RGBA_SHA256':sha(raw),'HDA_SHA256':sha(hda),'RGBA_FNV1a64':f'{fnv:016x}','outside_source_support':0,'fractional_samples':int(((a[:,:,3]>0)&(a[:,:,3]<255)).sum())};rows.append(row)
 if I:assert row==next(q for q in I['outputs']if q['id']==b),b
assert len(set(alphas))==1
(O/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'all_body_alpha_identical':True,'outputs':rows},indent=2)+'\n');print('PASS six exact green100 outputs')
