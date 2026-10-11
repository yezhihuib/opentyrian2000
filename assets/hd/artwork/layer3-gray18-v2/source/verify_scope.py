#!/usr/bin/env python3
"""Independent read-only verification of reconstructed baseline and selected scope."""
from pathlib import Path
from PIL import Image
from collections import deque
import argparse, hashlib, json, math, struct
IDS = [121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154]
OVERRIDES = [134,141,142,143]
W,H = 192,224
OFFSETS = sorted((dx*dx+dy*dy,dx,dy) for dy in range(-20,21) for dx in range(-20,21) if dx*dx+dy*dy<400)
def sha(b): return hashlib.sha256(b).hexdigest()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def components(alpha, threshold):
    mask = bytearray(v >= threshold for v in alpha)
    count=0
    for p in range(W*H):
        if not mask[p]: continue
        count+=1;mask[p]=0;q=deque([p])
        while q:
            n=q.popleft();x=n%W;y=n//W
            for a in ([n-1] if x else [])+([n+1] if x<W-1 else [])+([n-W] if y else [])+([n+W] if y<H-1 else []):
                if mask[a]:mask[a]=0;q.append(a)
    return count

def verify_tile_scope(before, after):
    require(len(before)==len(after)==W*H*4,'RGBA length mismatch')
    rgb_count=alpha_count=rgba_count=0;max_rgb=0;max_alpha=0;floor_count=0
    for p in range(0,len(before),4):
        a=before[p:p+4];b=after[p:p+4];x=(p//4)%W;y=(p//4)//W
        require((a[3]>0)==(b[3]>0),'Original occupied support changed')
        if a[3]==0:require(a==b==bytes(4),'Original zero RGBA changed')
        if min(x,y,W-1-x,H-1-y)<2:require(a==b,'Outer two HD rows/columns changed')
        floor_count+=b[3]==1
        if a==b:continue
        rgba_count+=1
        d2=400
        for dist,dx,dy in OFFSETS:
            xx=x+dx;yy=y+dy
            if 0<=xx<W and 0<=yy<H and before[(yy*W+xx)*4+3]==0:
                d2=dist;break
        if a[:3]!=b[:3]:
            rgb_count+=1;max_rgb=max(max_rgb,math.sqrt(d2))
            require(a[3]>0 and max(a[:3])<52 and d2<400,'RGB outside dark free-rim band')
        if a[3]!=b[3]:
            alpha_count+=1;max_alpha=max(max_alpha,math.sqrt(d2))
            require(a[3]>0 and d2<64 and 1<=b[3]<=a[3],'Alpha outside occupied-side <8HD band')
    return {'changed_rgba_subpixels':rgba_count,'rgb_changed':rgb_count,'alpha_changed':alpha_count,
            'max_rgb_distance_hd':max_rgb,'max_alpha_distance_hd':max_alpha,
            'zero_nonzero_support_exact':True,'original_zero_rgba_exact':True,
            'border_2hd_px_byte_exact':True,'rgb_dark_threshold_exclusive':52,'rgb_band_hd_exclusive':20,
            'alpha_band_hd_exclusive':8,'new_zero_alpha_subpixels':0,'new_enclosed_transparent_components':0,
            'alpha_floor_1_subpixels':floor_count,
            'occupied_components_v1_v2':[components(before[3::4],1),components(after[3::4],1)],
            'visible128_components_v1_v2':[components(before[3::4],128),components(after[3::4],128)]}

def verify(package,rebuild):
    contract=json.loads((package/'source/rebuild-contract.json').read_text())
    baseline=json.loads((package/'source/baseline-v1-contract.json').read_text())
    require(contract['ids']==baseline['ids']==IDS,'Finite 18 ID oracle mismatch')
    require(contract['override_ids']==OVERRIDES,'Finite four override oracle mismatch')
    require(sorted(p.name for p in (rebuild/'output').iterdir())==sorted(f'terrain-shapesz-{i}-8.png' for i in IDS),'Output file scope mismatch')
    require(sorted(p.name for p in (rebuild/'runtime-overlay').iterdir())==sorted(['manifest.json']+[f'terrain-shapesz-{i}-8.hda' for i in IDS]),'HDA file scope mismatch')
    changed=[];items=[]
    for row,old in zip(contract['items'],baseline['items']):
        i=row['id'];stem=f'terrain-shapesz-{i}-8'
        before=(rebuild/f'work/{i}-baseline.rgba').read_bytes()
        require(sha(before)==old['selected_rgba_sha256'],'Reconstructed v1 baseline mismatch')
        with Image.open(rebuild/f'output/{stem}.png') as im:
            require(im.size==(W,H),'Selected dimensions mismatch');after=im.convert('RGBA').tobytes()
        require(sha(after)==row['selected_rgba_sha256'],'Selected RGBA mismatch')
        hda=(rebuild/f'runtime-overlay/{stem}.hda').read_bytes()
        require(hda==b'HDR1'+struct.pack('<6I',2010000+i,8,24,28,0,0)+after,'Header or HDA data mismatch')
        require(sha(hda)==row['selected_hda_sha256'],'Selected HDA mismatch')
        if before!=after:changed.append(i)
        r={'id':i,**verify_tile_scope(before,after)}
        if i not in OVERRIDES:
            require(before==after,'Unrequested RGBA edit')
            require(row['selected_png_sha256']==old['selected_png_sha256'],'Preserved committed PNG changed')
            require(row['selected_hda_sha256']==old['selected_hda_sha256'],'Preserved HDA changed')
            r['full_tile_v1_equal']=True
        items.append(r)
    require(changed==OVERRIDES,'Actual changed IDs must be precisely the four requested')
    require(next(r for r in contract['items'] if r['id']==144)['selected_png_sha256']=='c4cd3a9dea6c5ecd14707ec5e0fef822407bb372f47b61cdbedd91da490772e8','Frozen144 PNG changed')
    return {'status':'PASS','total_tiles':18,'changed_ids':changed,'preserved_ids':[i for i in IDS if i not in OVERRIDES],
            'finite_4_override_and_18_total_oracle':True,'frozen144_exact':True,
            'all18_original_zero_nonzero_support_exact_relative_to_baked_source':True,
            'outer2hd_rows_columns_exact':True,'rgb_dark_band_and_alpha_band_verified':True,
            'preserved14_committed_png_and_hda_hashes_equal_v1':True,'items':items,
            'runtime_approval':'Bounded actual visual accepted separately; numeric verification is not an integration test'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rebuild-root',required=True,type=Path);a=p.parse_args()
    print(json.dumps(verify(Path(__file__).resolve().parent.parent,a.rebuild_root.resolve()),indent=2))
