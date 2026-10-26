#!/usr/bin/env python3
"""Rebuild the finite ShapesY candidate from one generated bitmap component board.

No original palette RGB or original source tile pixels are embedded here. Geometry
labels retain source water/dark-shadow/black footprints; explicit reviewed plane
annotations select generated components. Private map previews are a separate step.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image

BASE='authoring-inputs/shapesy-platform-current'
IDS=(321,322,323,324,325,326,331,332,333,334,336,341,342,343,346,351,352,353,354,361,362,363,364,365,374,375,384,385)

def input_paths(root):
    p=Path(root)/BASE
    names=['master-platform.png','generation-provenance.txt','recipe.json','README.md']
    names += [f'geometry-masks/{i}-{kind}.png' for i in IDS for kind in ('semantic','red')]
    return tuple(p/name for name in sorted(names))

def register_period(a,axis,width):
    """Symmetric local linear color registration of shared material repeat only."""
    a=a.astype(np.float64); n=a.shape[axis]
    l=np.take(a,0,axis); r=np.take(a,n-1,axis); target=(l+r)*.5
    for k in range(width):
        w=(1-k/width)**2
        s=[slice(None)]*3;s[axis]=k;a[tuple(s)]+=(target-l)*w
        s[axis]=n-1-k;a[tuple(s)]+=(target-r)*w
    return np.uint8(np.rint(np.clip(a,0,255)))

def generate(root):
    p=Path(root)/BASE; recipe=json.loads((p/'recipe.json').read_text())
    assert tuple(r['id'] for r in recipe['tiles'])==IDS
    assert hashlib.sha256((p/recipe['master']).read_bytes()).hexdigest()==recipe['master_sha256']
    master=Image.open(p/recipe['master']).convert('RGBA'); comp={}
    for name,c in recipe['components'].items():
        im=master.crop(c['crop']).resize(tuple(c['size']),Image.Resampling.LANCZOS)
        a=np.array(im)[:,:,:3]
        if 'periodic_registration' in c:
            a=register_period(a,0,c['periodic_registration']);a=register_period(a,1,c['periodic_registration'])
        if 'periodic_registration_x' in c:a=register_period(a,1,c['periodic_registration_x'])
        comp[name]=a
    yy,xx=np.mgrid[:224,:192]; ly=yy/8;lx=xx/8
    result={}
    for row in recipe['tiles']:
        i=row['id']
        assert row['logical_size']==[24,28] and row['anchor']==[0,0] and row['density']==8
        assert row['semantic_mask']==f'geometry-masks/{i}-semantic.png'
        assert row['red_mask']==f'geometry-masks/{i}-red.png'
        assert hashlib.sha256((p/row['semantic_mask']).read_bytes()).hexdigest()==row['semantic_sha256']
        assert hashlib.sha256((p/row['red_mask']).read_bytes()).hexdigest()==row['red_sha256']
        labels=np.array(Image.open(p/row['semantic_mask']))
        assert labels.shape==(28,24) and labels.max()<=8
        labels=np.repeat(np.repeat(labels,8,0),8,1)
        red=np.repeat(np.repeat(np.array(Image.open(p/row['red_mask'])),8,0),8,1)>0
        out=np.zeros((224,192,4),np.uint8)
        wallv=(ly+row['wall_v_offset'])*8
        if row['default_plane']==3:wallv=(ly-lx+row['wall_v_offset'])*8
        elif row['default_plane']==4:wallv=(ly+lx+row['wall_v_offset'])*8
        if row['split_wall_offset'] is not None:
            wallv=np.where(lx<12,(ly-lx+row['split_wall_offset'])*8,wallv)
        wallv=np.clip(wallv.astype(int),0,455)
        deck=comp['deck'][yy,xx]
        front=np.rint(comp['front'][wallv,xx]*recipe['lighting']['front_wall']).astype(np.uint8)
        side_raw=comp['side'][wallv,xx]
        side=np.rint(side_raw*recipe['lighting']['left_wall']).astype(np.uint8)
        right=np.rint(side_raw*recipe['lighting']['right_wall']).astype(np.uint8)
        bevel=np.rint(comp['bevel'][yy%16,xx]*recipe['lighting']['beveled_rim']).astype(np.uint8)
        recess=np.rint(comp['recess'][yy,xx]*recipe['lighting']['recess']).astype(np.uint8)
        # Root-reviewed V2: coherent generated recess replaces the original
        # pixel red stencil; immutable red mask is location/provenance only.
        for label,a in [(1,deck),(2,front),(3,side),(4,right),(5,bevel),(6,recess)]:out[labels==label,:3]=a[labels==label]
        shadow=np.rint(side_raw*recipe['lighting']['original_shadow']).astype(np.uint8)
        out[labels==7,:3]=shadow[labels==7]
        out[labels!=0,3]=255
        assert int((labels[::8,::8]==0).sum())==row['native_water_cells']
        assert np.all(out[labels==0]==0) and np.all(out[labels==8,:3]==0)
        result[i]=Image.fromarray(out,'RGBA')
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    for i,im in generate(a.root).items():im.save(a.out/f'terrain-shapesy-{i}-8.png')
if __name__=='__main__':main()
