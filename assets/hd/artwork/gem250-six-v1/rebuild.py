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
 b=r['id'];sb=r['alpha_bbox_xyxy_exclusive'];im=Image.open(P/'sources'/('generated-gem.png'if b!=188 else'generated-popup250.png')).convert('RGBA');gb=im.getchannel('A').point(lambda x:255 if x>12 else 0).getbbox();piece=im.crop(gb).resize(((sb[2]-sb[0])*8,(sb[3]-sb[1])*8),Image.Resampling.LANCZOS);im=Image.new('RGBA',(96,112));im.paste(piece,(sb[0]*8,sb[1]*8));a=np.array(im);support=np.array(Image.open(P/f'masks/mask-{b}.png').resize((96,112),Image.Resampling.NEAREST))>0;soft=np.clip((gaussian_filter(support.astype(float),2)-.5)/.35,0,1);a[:,:,3]=np.minimum(a[:,:,3],np.rint(soft*255).astype('uint8'))*support;assert not np.any((a[:,:,3]>0)&~support)
 if b!=188:
  rgb=a[:,:,:3].astype(float)*.88;lum=rgb.max(2)/255;a[:,:,:3]=np.rint(np.clip(rgb+(b-14)*np.array([13,17,10])*(.25+1.05*lum[:,:,None]),0,255)).astype('uint8');alphas.append(a[:,:,3].tobytes())
 a[a[:,:,3]==0,:3]=0
 im=Image.fromarray(a);prefix='gem250-bank11'if b!=188 else'gem250-value-newsh6';key=1200000+b if b!=188 else 1210188;f=O/f'{prefix}-{b}-8.png';im.save(f);raw=im.tobytes();hda=b'HDR1'+struct.pack('<6I',key,8,12,14,0,0)+raw;assert len(hda)==43036;hf=O/f'{prefix}-{b}-8.hda';hf.write_bytes(hda);fnv=14695981039346656037
 for v in raw:fnv=((fnv^v)*1099511628211)&0xffffffffffffffff
 alpha=a[:,:,3];unique,counts=np.unique(alpha,return_counts=True)
 row={'id':b,'key':key,'prefix':prefix,'png':f.name,'hda':hf.name,'PNG_SHA256':sha(f.read_bytes()),'RGBA_SHA256':sha(raw),'HDA_SHA256':sha(hda),'RGBA_FNV1a64':f'{fnv:016x}','ALPHA_SHA256':sha(alpha.tobytes()),'outside_source_support':0,'nonzero_samples':int((alpha>0).sum()),'fractional_samples':int(((alpha>0)&(alpha<255)).sum()),'alpha_histogram':{str(int(v)):int(n)for v,n in zip(unique,counts)}};rows.append(row)
 if I:assert row==next(q for q in I['outputs']if q['id']==b),b
assert len(set(alphas))==1
(O/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'all_body_alpha_identical':True,'outputs':rows},indent=2)+'\n');print('PASS six exact red/orange250 outputs')
