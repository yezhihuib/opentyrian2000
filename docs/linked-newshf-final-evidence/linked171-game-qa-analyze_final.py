from pathlib import Path
import csv,json,hashlib
import numpy as np
from PIL import Image
q=Path(__file__).resolve().parent;b=q.parent
rows=lambda p:list(csv.DictReader(p.open(),delimiter='\t'))
summary=[]
for scale in (4,8):
 p=q/'runs'/f'{scale}x-present';m=q/'runs'/f'{scale}x-missing'
 materials=[r for r in rows(p/'asset-debug-materials.tsv') if r['category']=='enemy' and r['sheet']=='newshf.shp' and r['id'] in ('43','45','81','83','119','121')]
 assert materials
 assert not any(r['id'] in ('45','83') for r in materials),'latent top/middle must not naturally fire'
 assert any(r['id']=='121' for r in materials)
 frames=rows(p/'frames.tsv');assert all(r['coverage_mismatch']=='0' for r in frames)
 total=0;bounds=[]
 masks={base:np.array(Image.open(b/f'linked171-private/authoring-inputs/newshf-linked/mask-{base}.png'))>0 for base in (43,45,81,83,119,121)}
 for im in sorted(p.glob('*.bmp')):
  tick=int(im.stem.split('-')[-1]);a=np.array(Image.open(im).convert('RGB'));c=np.array(Image.open(m/im.name).convert('RGB'));diff=np.any(a!=c,axis=2);h,w=diff.shape
  assert (w,h)==(640,400)
  allowed=np.zeros((200,320),bool)
  # Exact quadrant draw rows carry base id and physical tile, not postupdate cycle.
  for r in materials:
   if int(r['tick'])!=tick:continue
   base=int(r['id']);part=int(r['tile_id'])-base
   if part not in (0,1,19,20):continue
   dx=12 if part in (1,20) else 0;dy=14 if part in (19,20) else 0
   mask=masks[base][dy:dy+14,dx:dx+12];x=int(r['x'])-24;y=int(r['y'])
   for yy,xx in np.argwhere(mask):
    if 0<=y+yy<184 and 0<=x+xx<264:allowed[y+yy,x+xx]=True
  allowed=np.repeat(np.repeat(allowed,2,0),2,1)
  assert not (diff&~allowed).any(),(scale,tick,'outside-native-geometry',int((diff&~allowed).sum()))
  total+=int(diff.sum())
  if diff.any():
   yy,xx=np.where(diff);bounds.append(dict(tick=tick,pixels=int(diff.sum()),bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]))
 assert total>0
 summary.append(dict(internal_density=scale,window_pixels=[640,400],captured_frames=75,changed_pixels=total,exact_native_support_only=True,natural_bases=sorted(set(int(r['id']) for r in materials)),bounds=bounds))
(q/'final-visual-evidence.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps([{k:v for k,v in x.items() if k!='bounds'} for x in summary],indent=2))
