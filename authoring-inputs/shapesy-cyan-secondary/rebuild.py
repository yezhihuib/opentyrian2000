#!/usr/bin/env python3
"""Art-only deterministic registration. External original source mask is required; not packaged."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,binary_fill_holes,label,distance_transform_edt,binary_erosion
D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source-mask',required=True);args=p.parse_args()
native=np.array(Image.open(args.source_mask).convert('L'))>0
assert native.shape==(84,48) and native.sum()==669
mask=native.repeat(8,0).repeat(8,1)
raw=Image.open(D/'raw-generated.png').convert('RGBA')
# Remove only near-zero isolated generator speckle; crop bbox at alpha >3.
r=np.array(raw); r[r[:,:,3]<=3]=0
crop=Image.fromarray(r).crop((187,158,789,1437)).resize((184,376),Image.Resampling.LANCZOS)
a=np.zeros((672,384,4),dtype=np.uint8);a[136:512,112:296]=np.array(crop)
# Smooth inset support, preserving strict native zero-cell exclusion.
b=gaussian_filter(mask.astype(float),sigma=5,mode='constant')
t=np.clip((b-.55)/.35,0,1);matte=t*t*(3-2*t);matte[~mask]=0
distance=distance_transform_edt(mask)
u=np.clip((distance-0.5)/7.5,0,1);matte*=u*u*(3-2*u)
# Targeted right lower-lobe cap only; preserve RGB and all pixels outside this window.
yy,xx=np.mgrid[:672,:384]
def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
window=smooth((yy-402)/8)*smooth((452-yy)/8)*smooth((xx-262)/6)
curve=287.0-0.012*(yy-427.0)**2
cap=smooth((curve-xx)/4.0)
matte*=1-window*(1-cap)
out=a.copy();out[:,:,3]=np.rint(a[:,:,3]*matte).astype('uint8');out[out[:,:,3]<=3]=0
Image.fromarray(out).save(D/'master-384x672.png')
rebuilt=np.zeros_like(out);parts=[]
for tid,x,y in [(172,192,0),(181,0,224),(182,192,224),(191,0,448),(192,192,448)]:
 tile=out[y:y+224,x:x+192];Image.fromarray(tile).save(D/f'shapesy-{tid}-8x.png');rebuilt[y:y+224,x:x+192]=tile
 parts.append({'tile':tid,'offset':[x,y],'visible_pixels':int((tile[:,:,3]>0).sum())})
Image.fromarray(rebuilt).save(D/'reassembled-384x672.png')
for scale in [4,8]:
 size=(48*scale,84*scale);im=Image.fromarray(out).resize(size,Image.Resampling.LANCZOS)
 can=Image.new('RGB',(size[0]*3,size[1]+42),(40,40,40));dr=ImageDraw.Draw(can)
 for i,(name,c) in enumerate([('dark',(8,18,24)),('light',(238,233,218)),('map-like',(35,75,81))]):
  bg=Image.new('RGBA',size,c+(255,));bg.alpha_composite(im);can.paste(bg.convert('RGB'),(i*size[0],42));dr.text((i*size[0]+5,24),f'{scale}x {name}',fill='white')
 dr.text((5,5),'ART PREVIEW / NOT ACTUAL GAME',fill='white');can.save(D/f'preview-{scale}x.png')
v=out[:,:,3]>0;holes=binary_fill_holes(v)&~v
stats={'runtime_qualified':False,'native_cells':int(native.sum()),'support_pixels':int(mask.sum()),'visible_pixels':int(v.sum()),'support_loss_pixels':int((mask&~v).sum()),'support_loss_fraction':float((mask&~v).sum()/mask.sum()),'outside_support_pixels':int((v&~mask).sum()),'source_zero_rgba_nonzero_channels':int(np.count_nonzero(out[~mask])),'alpha_levels':len(np.unique(out[:,:,3])),'partial_alpha_pixels':int(((out[:,:,3]>0)&(out[:,:,3]<255)).sum()),'max_alpha':int(out[:,:,3].max()),'internal_hole_pixels':int(holes.sum()),'connected_components':int(label(v)[1]),'native_cells_without_visible_subpixel':int((native&~v.reshape(84,8,48,8).any(axis=(1,3))).sum()),'registered_alpha_equivalent_pixels':float(a[:,:,3].sum()/255),'final_alpha_equivalent_pixels':float(out[:,:,3].sum()/255),'registration_alpha_attenuation_fraction':float(1-out[:,:,3].sum()/a[:,:,3].sum()),'reassembly_mismatched_channels':int(np.count_nonzero(out!=rebuilt)),'parts':parts}
edge=mask&~binary_erosion(mask)
stats.update(native_support_boundary_max_alpha=int(out[:,:,3][edge].max()),native_support_boundary_alpha_over_32=int((out[:,:,3][edge]>32).sum()),visible_bbox=list(Image.fromarray(out).getbbox()))
(D/'stats.json').write_text(json.dumps(stats,indent=2)+'\n');print(json.dumps(stats,indent=2))
