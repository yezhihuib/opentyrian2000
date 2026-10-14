#!/usr/bin/env python3
"""Rebuild the frozen generated-only rear534 resources. Never reads game data."""
from pathlib import Path
from PIL import Image
from scipy.ndimage import label
import numpy as np,json,hashlib,struct,sys
P=Path(__file__).resolve().parent
O=Path(sys.argv[1]).absolute()if len(sys.argv)>1 else P/'output'
if O.exists():raise SystemExit('Output directory must not exist; choose a new path.')
sha=lambda b:hashlib.sha256(b).hexdigest()
I=json.loads((P/'inventory.json').read_text())if(P/'inventory.json').exists()else None
if I:
 for f,h in I['inputs'].items():assert sha((P/f).read_bytes())==h,f
master=Image.open(P/'sources/generated-master-207.png').convert('RGBA')
raw=np.asarray(master); labels,n=label(raw[:,:,3]>=32);sizes=np.bincount(labels.ravel());sizes[0]=0
ys,xs=np.where(labels==sizes.argmax());l,t,r,b=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
piece=master.crop((l-2,t-2,r+2,b+2)).resize((184,136),Image.Resampling.LANCZOS)
registered=Image.new('RGBA',(192,224));registered.alpha_composite(piece,(8,56))
a=np.array(registered);rgb=a[:,:,:3].astype('float64');r,g,b=rgb.transpose(2,0,1)
w=np.clip((np.maximum(r,g)-b-20.)/60.,0.,1.)*(np.maximum(r,g)>60.)*(a[:,:,3]>0)
alpha=a[:,:,3].tobytes();rows=[];O.mkdir(parents=True)
for base,level,slot in[(203,.30,507),(205,.64,508),(207,1.,509)]:
 out=a.copy();out[:,:,:3]=np.rint(np.clip(rgb*(1-(1-level)*w)[:,:,None],0,255)).astype('uint8');out[out[:,:,3]==0,:3]=0
 assert out[:,:,3].tobytes()==alpha
 assert np.array_equal(out[:,:,:3][w==0],a[:,:,:3][w==0]*(a[:,:,3][w==0,None]>0))
 raw=out.tobytes();im=Image.fromarray(out);prefix=f'rear534-bank11-{base}-8';png=O/f'{prefix}.png';im.save(png)
 key=1230000+base;hda=b'HDR1'+struct.pack('<6I',key,8,24,28,6,7)+raw;assert len(raw)==172032 and len(hda)==172060
 assert struct.unpack('<6I',hda[4:28])==(key,8,24,28,6,7)
 (O/f'{prefix}.hda').write_bytes(hda)
 fnv=14695981039346656037
 for v in raw:fnv=((fnv^v)*1099511628211)&0xffffffffffffffff
 vals,counts=np.unique(out[:,:,3],return_counts=True)
 row={'id':base,'role':123,'slot':slot,'key':key,'png':png.name,'hda':f'{prefix}.hda','PNG_SHA256':sha(png.read_bytes()),'RGBA_SHA256':sha(raw),'HDA_SHA256':sha(hda),'RGBA_FNV1a64':f'{fnv:016x}','ALPHA_SHA256':sha(alpha),'nonzero_samples':int((out[:,:,3]>0).sum()),'fractional_samples':int(((out[:,:,3]>0)&(out[:,:,3]<255)).sum()),'alpha_histogram':{str(int(v)):int(n)for v,n in zip(vals,counts)}}
 rows.append(row)
 if I:assert row==next(q for q in I['outputs']if q['id']==base),base
(O/'rebuild-receipt.json').write_text(json.dumps({'pass':True,'generated_master_only':True,'all_phase_alpha_identical':True,'neutral_housing_unchanged':True,'outputs':rows},indent=2)+'\n')
print('PASS: three exact generated-only rear534 resources.')
