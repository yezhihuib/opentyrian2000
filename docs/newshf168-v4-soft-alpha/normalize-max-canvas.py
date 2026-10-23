from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,binary_erosion
O=Path(__file__).resolve().parent;R=O.parent;W=R.parent
O=O/'max-canvas-alternative';O.mkdir(exist_ok=True)
src=W/'generated_images/exec-71f206f9-fa06-43eb-a4b9-a8bcfb91aad1.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bb(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
for d in ['raw','candidate-assets','comparisons']:(O/d).mkdir(exist_ok=True)
rawdest=O/'raw/enemy-168-v4-three-poses-imagegen-exec-71f206f9-fa06-43eb-a4b9-a8bcfb91aad1.png';shutil.copyfile(src,rawdest);raw=Image.open(src).convert('RGBA');a=np.array(raw);cols=np.flatnonzero((a[:,:,3]>=2).any(0));runs=np.split(cols,np.where(np.diff(cols)>1)[0]+1);assert len(runs)==3
# Documented global alpha correction for the dominant nominal opaque253 source.
b=a.copy();b[:,:,3]=np.minimum(255,np.rint(b[:,:,3].astype(float)*255/253)).astype('uint8');b[b[:,:,3]<2]=0;b[b[:,:,3]==0]=0;clean=Image.fromarray(b)
segments=[]
for run in runs:
 l,r=int(run[0]),int(run[-1])+1;m=a[:,l:r,3]>=128;box=bb(m);box[0]+=l;box[2]+=l;yy,xx=np.where(m);end=yy>=yy.max()-3;nose=[float(np.median(xx[end])+l+.5),float(yy.max()+1)];segments.append((l,r,box,nose))
left=max(s[3][0]-s[0] for s in segments);right=max(s[1]-s[3][0] for s in segments);scale=min(190/(left+right),208/max(s[3][1] for s in segments));nose_target=1+left*scale;outims=[]
M=dict(status='CANDIDATE ONLY / SOFT ALPHA CONTRACT NOT CURRENTLY SUPPORTED / NO PRODUCTION INSTALL',intended_slot_order=[55,17,93],direction_calibration='55 neutral;17 and93 intended slots only; engine roll direction unconfirmed',raw=dict(file=str(rawdest.relative_to(O)),sha256=sha(src),size=raw.size,left_border_core_pixels=8,crop_warning='neutral left-wing edge touches raw x0 for8 alpha>=128 pixels, y327..334. Cannot certify complete uncropped outline; no invented repair.'),normalizer_sha256=sha(Path(__file__)),parameters=dict(cell_size=[192,224],logical_size=[24,28],anchor=[6,7],density=8,common_uniform_scale=scale,common_nose_target=[nose_target,208],registration='all source nose tips (median of last4 core-alpha rows) -> (common optimized noseX,208); feature alignment distinct from logical anchor[6,7]; common scale both axes, no per-side bbox fit',alpha_policy='global round(alpha*255/253) clamp255 because source modal opacity253; alpha<2 cleared before resize only; final alpha retained including1, no hardening; RGB zero if finalalpha0',resampling='Pillow RGBA LANCZOS resize with internal premultiplied-alpha; straight RGBA output; no blur/sharpen filters'),poses=[])
for i,(base,(l,r,box,nose)) in enumerate(zip([55,17,93],segments)):
 # Pad each entire source column before scaling, preserving all edge coverage.
 # Common scale with round-to-nearest pixel crop extent; x/y quantization is documented.
 crop=clean.crop((l,0,r,raw.height));dims=(round(crop.width*scale),round(crop.height*scale));tile=crop.resize(dims,Image.Resampling.LANCZOS)
 x=round(nose_target-(nose[0]-l)*scale);y=round(208-nose[1]*scale);assert x>=0 and y>=0 and x+dims[0]<=192 and y+dims[1]<=224,(x,y,dims)
 out=Image.new('RGBA',(192,224));out.paste(tile,(x,y));arr=np.array(out);arr[arr[:,:,3]==0]=0;out=Image.fromarray(arr);dest=O/f'candidate-assets/enemy-168-v4-intended-base{base}.png';out.save(dest);outims.append(out)
 al=arr[:,:,3];core=al>=128;ys,xs=np.where(core);labs,n=label(al>0,np.ones((3,3)));counts=np.bincount(labs.ravel())[1:];interior=binary_erosion(core,iterations=2);soft=(al>0)&(al<255)
 M['poses'].append(dict(column=i,intended_base=base,direction_confirmed=False,raw_core_bbox=box,raw_nose_landmark=nose,scaled_size=dims,paste=[x,y],effective_quantized_scale=[dims[0]/crop.width,dims[1]/crop.height],registered_nose=[x+(nose[0]-l)*scale,y+nose[1]*scale],file=str(dest.relative_to(O)),sha256=sha(dest),stats=dict(core_bbox=bb(core),nonzero_bbox=bb(al>0),core_centroid=[float(xs.mean()+.5),float(ys.mean()+.5)],alpha_unique_count=len(np.unique(al)),alpha_unique_values=np.unique(al).tolist(),soft_pixel_count=int(soft.sum()),interior_soft_pixels=int((soft&interior).sum()),isolated_alpha_component_sizes=sorted(counts.tolist(),reverse=True),rgb_at_alpha0_zero=not arr[al==0,:3].any(),canvas_border_alpha_pixels=int((al[0]>0).sum()+(al[-1]>0).sum()+(al[:,0]>0).sum()+(al[:,-1]>0).sum()))))
old=[Image.open(R/f'enemy-168-fine-v3/candidate-assets/enemy-168-fine-v3-base{b}.png').convert('RGBA') for b in [55,17,93]]
for tone,color in [('dark',(24,27,32)),('light',(240,240,240))]:
 for cw,ch in [(48,56),(96,112),(192,224),(384,448)]:
  v=Image.new('RGB',(120+3*(cw+12),2*(ch+30)+34),color);d=ImageDraw.Draw(v);ink='white' if tone=='dark' else 'black';d.text((6,8),f'V3 vs V4 / {cw}x{ch} '+('2x NEAREST review' if cw==384 else 'actual pixels / LANCZOS display'),fill=ink)
  for j,(title,ims) in enumerate([('V3 rejected',old),('V4 candidate',outims)]):
   y=34+j*(ch+30);d.text((5,y+18),title,fill=ink)
   for i,im in enumerate(ims):
    x=120+i*(cw+12);d.text((x,y),['55','17 slot','93 slot'][i],fill=ink);res=im.resize((cw,ch),Image.Resampling.NEAREST if cw==384 else Image.Resampling.LANCZOS);bg=Image.new('RGBA',(cw,ch),color+(255,));bg.alpha_composite(res);v.paste(bg.convert('RGB'),(x,y+20))
  v.save(O/f'comparisons/v3-v4-{tone}-{cw}x{ch}.png')
M['raw_unchanged']=sha(src)==sha(rawdest);assert M['raw_unchanged'];(O/'validation.json').write_text(json.dumps(M,indent=2)+'\n');print([(p['intended_base'],p['stats']['core_bbox'],p['stats']['alpha_unique_count']) for p in M['poses']])
