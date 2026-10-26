from pathlib import Path
import csv,json,hashlib
import numpy as np
from PIL import Image
q=Path(__file__).resolve().parent
rows=lambda p:list(csv.DictReader(p.open(),delimiter='\t'))
summary=[]
for consumer in (173,285):
 base=q/'final-runs'/f'{consumer}-missing';present=q/'final-runs'/f'{consumer}-present'
 state0=rows(base/'state.tsv');fields=[k for k in state0[0] if k!='output_pixels']
 for variant in ('present','corrupt','public-baseline','reference'):
  p=q/'final-runs'/f'{consumer}-{variant}';other=rows(p/'state.tsv')
  assert len(other)==len(state0)
  assert all(all(a[k]==b[k] for k in fields) for a,b in zip(state0,other)),(consumer,variant,'state')
  for name in ('enemy-projectiles.tsv','collisions.tsv','player-projectiles.tsv','player-shot-emissions.tsv'):
   assert (p/name).read_bytes()==(base/name).read_bytes(),(consumer,variant,name)
 reference=rows(q/'final-runs'/f'{consumer}-reference'/'scene-draw-commands.tsv');assert not [r for r in reference if r['role']=='149' and r['mirrored']=='1']
 scene=rows(present/'scene-draw-commands.tsv');hd=[r for r in scene if r['role']=='149' and r['mirrored']=='1'];assert hd
 assert all(r['coverage_mismatch']=='0' for r in rows(present/'frames.tsv'))
 changes=0; bounds=[]
 for im in sorted(present.glob('*.bmp')):
  a=np.array(Image.open(im).convert('RGB'));b=np.array(Image.open(base/im.name).convert('RGB'));diff=np.any(a!=b,axis=2);changes+=int(diff.sum());tick=int(im.stem.split('-')[-1]);h,w=diff.shape;assert (w,h)==(640,400)
  allowed=np.zeros((200,320),dtype=bool);mask=np.array(Image.open(q.parent/'art-draft-projectile91/original-bank8-selector91-mask.png'))>0
  for r in hd:
   if int(r['tick'])!=tick:continue
   x,y=int(r['x']),int(r['y'])
   for my,mx in np.argwhere(mask):
    if 0<=y+my<184 and 24<=x+mx<288:allowed[y+my,x+mx-24]=True
  allowed=np.repeat(np.repeat(allowed,2,0),2,1)
  assert not (diff&~allowed).any(),(consumer,tick,'outside-original-mask',int((diff&~allowed).sum()))
  for variant in ('corrupt','public-baseline'):
   assert (q/'final-runs'/f'{consumer}-{variant}'/im.name).read_bytes()==(base/im.name).read_bytes(),(consumer,variant,im.name)
  if diff.any():
   yy,xx=np.where(diff);bounds.append([tick,int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)])
 assert changes>0
 summary.append(dict(consumer=consumer,logic_ticks=len(state0),capture_pairs=8,hd91_draws=len(hd),changed_physical_pixels=changes,all_changes_inside_original62cell_support=True,bounds=bounds,logical_state_rng_index8_equal=True,missing_corrupt_public_baseline_bmp_exact=True))
 (present/'preview.png').write_bytes(b'') if False else None
 first=sorted(present.glob('*.bmp'))[0];Image.open(first).save(q/f'consumer{consumer}-hd.png');Image.open(base/first.name).save(q/f'consumer{consumer}-classic91.png')
(q/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
