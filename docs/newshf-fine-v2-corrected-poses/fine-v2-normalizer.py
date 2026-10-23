#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label
O=Path(__file__).resolve().parent;R=O.parent;W=R.parent
CONFIG={163:('f338b63e-5de9-4a6b-9fdb-c6effed12873',[125,123,127]),167:('df6740df-7daf-4d8d-998b-d8a9e3cf66f8',[1,3,5]),168:('73a63a29-321e-4c25-9b19-1248c73e0b73',[17,55,93])}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mask(im):return np.asarray(im)[:,:,3]>=128
def bbox(m):
 y,x=np.where(m);return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
def stats(im,ref,old):
 m=mask(im);y,x=np.where(m);d=dict(bbox=bbox(m),opaque_pixels=int(m.sum()),centroid=[float(x.mean()+.5),float(y.mean()+.5)])
 for n,a in [('original',ref),('prior',old)]:
  r=mask(a);ry,rx=np.where(r);d[n]=dict(iou=float((m&r).sum()/(m|r).sum()),centroid_delta=[float(x.mean()-rx.mean()),float(y.mean()-ry.mean())],area_ratio=float(m.sum()/r.sum()))
 return d
def clean(im):
 a=np.array(im);m=a[:,:,3]>=128;a[~m]=0;a[m,3]=255;return Image.fromarray(a)
for d in ['raw','candidate-assets','alternatives','comparisons']: (O/d).mkdir(exist_ok=True)
M=dict(status='CANDIDATE ONLY; NOT INSTALLED; NO RUNTIME CLAIM',provenance='imagegen edits of previously selected normalized three-pose sources; deterministic Python segmentation/resize/alpha cleanup only',normalizer_sha256=sha(Path(__file__)),prior_normalizers={x:sha(R/f'enemy-hd-normalized-{x}-v1/normalize.py') for x in ['gray','green']},parameters=dict(pixel_size=[192,224],logical_size=[24,28],density=8,logical_anchor=[6,7],canvas_registration=[48,56],alpha_threshold=128,alpha_policy='threshold source before resize and result after resize; alpha binary; RGB straight/unpremultiplied and zero where transparent',resampling='Compare NEAREST, BOX, LANCZOS; Pillow RGBA resize performs premultiplied-alpha interpolation then returns straight RGBA; no blur/sharpen filters',alignment='fit whole source alpha bbox to current selected bbox; no mask clipping or row warping'),records=[])
for rid,(uid,bases) in CONFIG.items():
 src=W/f'generated_images/exec-{uid}.png';rawdest=O/f'raw/enemy-{rid}-fine-v2-imagegen-exec-{uid}.png';shutil.copyfile(src,rawdest)
 raw=Image.open(src).convert('RGBA');m=mask(raw);cols=np.flatnonzero(m.any(0));runs=np.split(cols,np.where(np.diff(cols)>1)[0]+1);assert len(runs)==3
 refpath=R/f'material-collection/enemies/redraw-inputs/newshf-record{rid}-three-poses-transparent.png';refs=Image.open(refpath).convert('RGBA');rec=dict(record=rid,base_order=bases,raw=dict(file=str(rawdest.relative_to(O)),original_path=str(src),sha256=sha(src),size=raw.size),reference=dict(path=str(refpath),sha256=sha(refpath)),poses=[]);rows={x:[] for x in ['prior','NEAREST','BOX','LANCZOS']}
 for i,(run,base) in enumerate(zip(runs,bases)):
  oldpath=R/f'enemy-hd-normalized-gray-v1/enemy-163-normalized-base{base}.png' if rid==163 else R/f'enemy-hd-normalized-green-v1/enemy-{rid}-v1-bbox-fit-base{base}.png'
  old=Image.open(oldpath).convert('RGBA');ref=refs.crop((192*i,0,192*(i+1),224));rows['prior'].append(old);t=bbox(mask(old));b=bbox(m[:,run[0]:run[-1]+1]);b[0]+=int(run[0]);b[2]+=int(run[0]);crop=clean(raw).crop(b);dims=(t[2]-t[0],t[3]-t[1]);sx,sy=dims[0]/crop.width,dims[1]/crop.height
  labs,n=label(mask(crop),np.ones((3,3)));p=dict(base=base,prior=dict(path=str(oldpath),sha256=sha(oldpath)),source_bbox=b,target_bbox=t,scale_xy=[sx,sy],anisotropy_percent=100*(max(sx,sy)/min(sx,sy)-1),component_sizes=sorted(np.bincount(labs.ravel())[1:].tolist(),reverse=True),variants={})
  for mode in ['NEAREST','BOX','LANCZOS']:
   tile=clean(crop.resize(dims,getattr(Image.Resampling,mode)));out=Image.new('RGBA',(192,224));out.paste(tile,(t[0],t[1]));dest=O/f'alternatives/enemy-{rid}-fine-v2-{mode.lower()}-base{base}.png';out.save(dest);rows[mode].append(out);p['variants'][mode]=dict(file=str(dest.relative_to(O)),sha256=sha(dest),stats=stats(out,ref,old))
  rec['poses'].append(p)
 # Every cell is rendered at the stated pixel size, without stretching the whole contact sheet.
 for size in [(48,56),(96,112),(192,224),(384,448)]:
  cw,ch=size;pad=12;labelw=100;view=Image.new('RGB',(labelw+3*(cw+pad)+pad,4*(ch+30)+30),(30,33,39));draw=ImageDraw.Draw(view);draw.text((8,8),f'{rid}: {cw}x{ch} / display NEAREST (384 = 2x review)',fill='white')
  for j,(mode,ims) in enumerate(rows.items()):
   y=30+j*(ch+30);draw.text((5,y+10),mode,fill='white')
   for i,im in enumerate(ims):
    x=labelw+i*(cw+pad);draw.text((x,y),f'base {bases[i]}',fill='white');bg=Image.new('RGBA',size,(30,33,39,255));bg.alpha_composite(im.resize(size,Image.Resampling.NEAREST));view.paste(bg.convert('RGB'),(x,y+20))
  view.save(O/f'comparisons/record{rid}-{cw}x{ch}-all-resamplers.png')
 M['records'].append(rec)
(O/'validation.json').write_text(json.dumps(M,indent=2)+'\n')
print('Created normalization alternatives and comparisons')
# Selection after visual review: LANCZOS is less speckled than NEAREST and retains
# panel lines better than BOX. This is quality downsampling, not a blur filter.
M['selection']=dict(mode='LANCZOS',reason='Fine panel edges with lower sampling noise than nearest; BOX slightly reduces panel contrast. No blur filter or procedural drawing.',runtime_verified=False)
public=dict(status=M['status'],logical_size=[24,28],density=8,logical_anchor=[6,7],pixel_size=[192,224],resample='LANCZOS',alpha='binary 0/255, transparent RGB zero',records=[])
for rec in M['records']:
 members=[]
 for p in rec['poses']:
  src=O/p['variants']['LANCZOS']['file'];dst=O/f"candidate-assets/enemy-{rec['record']}-fine-v2-base{p['base']}.png";shutil.copyfile(src,dst)
  a=np.asarray(Image.open(dst));assert set(np.unique(a[:,:,3]))=={0,255};assert not a[a[:,:,3]==0,:3].any();assert p['target_bbox']==bbox(a[:,:,3]>0)
  members.append(dict(base=p['base'],file=dst.name,sha256=sha(dst)))
 public['records'].append(dict(source_id=f"newshf record{rec['record']}",selected_mode='bbox-fit-lanczos',members=members))
for size in [(48,56),(96,112),(192,224),(384,448)]:
 cw,ch=size;v=Image.new('RGB',(110+3*(cw+12),6*(ch+30)+30),(30,33,39));d=ImageDraw.Draw(v);d.text((8,8),f'Old vs fine-v2 / {cw}x{ch} / NEAREST display / no game context',fill='white')
 for ri,rec in enumerate(M['records']):
  for j in range(2):
   y=30+(ri*2+j)*(ch+30);d.text((5,y+20),f"{rec['record']} "+('OLD' if j==0 else 'FINE V2'),fill='white')
   for i,p in enumerate(rec['poses']):
    im=Image.open(p['prior']['path'] if j==0 else O/p['variants']['LANCZOS']['file']).convert('RGBA');x=110+i*(cw+12);d.text((x,y),f"base {p['base']}",fill='white');bg=Image.new('RGBA',size,(30,33,39,255));bg.alpha_composite(im.resize(size,Image.Resampling.NEAREST));v.paste(bg.convert('RGB'),(x,y+20))
 v.save(O/f'comparisons/selected-old-vs-fine-v2-{cw}x{ch}.png')
M['source_hashes_unchanged']=all(sha(Path(r['raw']['original_path']))==r['raw']['sha256'] and sha(Path(r['reference']['path']))==r['reference']['sha256'] and all(sha(Path(p['prior']['path']))==p['prior']['sha256'] for p in r['poses']) for r in M['records']);assert M['source_hashes_unchanged']
(O/'validation.json').write_text(json.dumps(M,indent=2)+'\n');(O/'candidate-assets/candidate-manifest.json').write_text(json.dumps(public,indent=2)+'\n')
(O/'README.md').write_text('''# Small aircraft fine-v2 — candidate only

Nine independently versioned PNGs; production repository and pins not modified. No runtime pass claimed.

## Choice
Imagegen supplied finer panel artwork; deterministic Python only segments, resizes and cleans alpha. Selected LANCZOS quality downsampling, then binary alpha128 threshold; no blur, sharpen, generated procedural details, silhouette clipping, or row warp. NEAREST and BOX alternatives retained for audit. RGB is straight/unpremultiplied; transparent pixels are RGBA zero. Source is thresholded before interpolation too. Pillow internally premultiplies RGBA interpolation and returns straight RGBA.

All nine 192x224 cells retain EXACT prior selected opaque bounding boxes, [6,7] logical anchor, [48,56] pixel registration, density8 and original base ordering (163:125,123,127; 167:1,3,5; 168:17,55,93). Whole-source bbox fitting incurs 0.22–4.02% axis anisotropy; no larger envelope. Current original refs and prior selected images are read-only and hashed, not overwritten. All old source and normalized bundles remain untouched.

## Honest limitations
Generated forms are not exact silhouette copies. Against prior selections, gray IoU is 0.731–0.747; green167 0.847–0.899; green168 0.907–0.940. New opaque area is 93.3–98.8% of prior, so none is bulked up. Gray centroid shifts down about 3.8–4.4 pixels at 192x224; green167 about 2.8–3.5 pixels; green168 up 1.2–1.8 pixels. These are artwork differences, not runtime movement or altered registration. Bank pose sequence is retained; generated bank asymmetry is subtle, especially gray, not a claim of original pose fidelity. Original masks, centroid deltas and per-pose aspect transforms are fully recorded in validation.json.

## Review
comparisons/ contains each record at literal 48x56, 96x112, 192x224, and 384x448 (2x nearest review), comparing prior / nearest / BOX / LANCZOS, plus all-three-record selected old/new sheets. Display scaling uses NEAREST consistently; these are static neutral contact sheets, not fabricated game screenshots. At 48x56 fine details necessarily collapse; improvement is clearest at 96x112 and above. Binary alpha retains a pixel-crisp outer edge and does not promise smooth vector contours.

## Reproduce / provenance
Run `python normalize.py` in the original workspace layout (Pillow, NumPy, SciPy). raw/ contains exact imagegen originals with execution IDs in filenames. validation.json includes hashes of raw files, prior normalizers, reference strips, prior selected assets, this normalizer, and all variant assets. candidate-assets/candidate-manifest.json maps the nine selected PNGs. No original game binary included.
''')
(O/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.relative_to(O)}\n' for p in sorted(O.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
print('Selected nine LANCZOS candidates; source hashes unchanged; exact bboxes; binary clean alpha verified')
