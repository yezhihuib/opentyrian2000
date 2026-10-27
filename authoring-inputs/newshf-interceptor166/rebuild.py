#!/usr/bin/env python3
"""Deterministic registration and exact native-zero alpha enforcement; no painting."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy.ndimage import label
ROOT=Path(__file__).resolve().parent
STATS={}
for base in (87,85,89):
    raw=Image.open(ROOT/f'raw-base{base}.png').convert('RGBA')
    a=np.array(raw); yy,xx=np.nonzero(a[:,:,3]>32)
    box=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
    native=Image.open(ROOT/f'native-mask-base{base}.png').convert('L')
    m=np.array(native)>0; y,x=np.nonzero(m); target=(int(x.min()*8),int(y.min()*8),int((x.max()+1)*8),int((y.max()+1)*8))
    crop=raw.crop(box); reg=Image.new('RGBA',(192,224)); reg.paste(crop.resize((target[2]-target[0],target[3]-target[1]),Image.Resampling.LANCZOS),target[:2])
    ar=np.array(reg); support=np.repeat(np.repeat(m,8,0),8,1)
    # Conservative supersampled mask intersection, alpha softened inward at native boundary.
    hard=Image.fromarray(support.astype('uint8')*255)
    soft=np.array(hard.filter(ImageFilter.GaussianBlur(3.5)),dtype=np.float32)/255
    maskalpha=np.clip((soft-.58)/.30,0,1)*support
    ar[:,:,3]=np.rint(ar[:,:,3]*maskalpha).astype('uint8')
    ar[~support]=0
    labels, count=label(ar[:,:,3]>0)
    sizes=np.bincount(labels.ravel()); sizes[0]=0
    keep=int(sizes.argmax()); dust=(labels!=keep)&(labels>0)
    removed_pixels=int(dust.sum()); removed_alpha_sum=int(ar[dust,3].astype('int64').sum())
    ar[dust]=0; ar[ar[:,:,3]==0]=0
    im=Image.fromarray(ar); im.save(ROOT/f'master-base{base}.png')
    STATS[str(base)]={'raw_bbox_alpha_gt32':box,'target_bbox':target,'native_cells':int(m.sum()),'native_zero_nonzero_rgba':int(np.count_nonzero(ar[~support])),'visible_pixels':int(np.count_nonzero(ar[:,:,3])),'empty_source_cells':sum(not ar[j*8:(j+1)*8,i*8:(i+1)*8,3].any() for j,i in zip(*np.nonzero(m))),'partial_alpha_pixels':int(np.count_nonzero((ar[:,:,3]>0)&(ar[:,:,3]<255))),'alpha_levels':len(np.unique(ar[:,:,3])),'connected_components':1,'visible_alpha_median':float(np.median(ar[:,:,3][ar[:,:,3]>0])),'opaque_interior_reference_alpha':253,'background_weight_at_alpha253':2/255,'visible_alpha_ge240_pixels':int(np.sum(ar[:,:,3]>=240)),'removed_disconnected_pixels':removed_pixels,'removed_disconnected_alpha_sum':removed_alpha_sum}
for scale in (4,8):
    width=24*scale; height=28*scale
    out=Image.new('RGB',(width*3,height+24),(28,43,53));d=ImageDraw.Draw(out)
    for i,b in enumerate((85,87,89)):
        im=Image.open(ROOT/f'master-base{b}.png').resize((width,height),Image.Resampling.LANCZOS)
        out.paste(im,(width*i,24),im);d.text((width*i+4,5),f'base {b}',fill=(230,230,230))
    out.save(ROOT/f'preview-{scale}x.png')
(ROOT/'stats.json').write_text(json.dumps(STATS,indent=2)+'\n')
print(json.dumps(STATS,indent=2))
