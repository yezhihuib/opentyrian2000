"""Check same-scale point/smooth green-review capture pairs (Pillow + NumPy)."""
from pathlib import Path
import argparse, csv, json
import numpy as np
from PIL import Image

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline', type=Path, required=True)
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--assets', type=Path, required=True)
p.add_argument('--output', type=Path)
a = p.parse_args()
read = lambda path: list(csv.DictReader(path.open(), delimiter='\t'))
for name in ['state.tsv', 'collisions.tsv', 'fx-created-shots.tsv', 'fx-setup.tsv', 'fx-trail.tsv']:
 assert (a.baseline/name).read_bytes() == (a.candidate/name).read_bytes(), name
assert all(e['rng_before'] == e['rng_after'] for e in read(a.candidate/'presentation.tsv'))
assert all(e['coverage_mismatch'] == '0' for e in read(a.candidate/'frames.tsv'))
assert all(e['classic_mismatches'] == '0' for e in read(a.candidate/'rgb-audit.tsv'))
events = read(a.candidate/'ae-events.tsv')
assert len(events) == 448 and len(read(a.candidate/'fx-setup.tsv')) == 64
assert set(int(e['id']) for e in events) == set(range(78,85))
assert all(int(e['ttl_before']) == 7-int(e['frame0']) for e in events)
per_tick = []
for file in sorted(a.candidate.glob('asset-debug-window-*.png')):
 tick = int(file.stem.rsplit('-',1)[1])
 before = np.array(Image.open(a.baseline/file.name))
 after = np.array(Image.open(file))
 assert before.shape == after.shape
 scale = before.shape[1]//320
 assert before.shape[:2] == (200*scale,320*scale)
 diff = np.any(before != after, axis=2)
 mask = np.zeros(diff.shape, bool)
 for e in events:
  if int(e['tick']) != tick: continue
  x,y = (int(e['x'])-24)*scale,int(e['y'])*scale
  mask[max(0,y):min(mask.shape[0],y+14*scale),max(0,x):min(mask.shape[1],x+12*scale)] = True
 assert not np.any(diff & ~mask), (tick,'RGB difference outside current green tile')
 per_tick.append({'tick':tick,'changed_pixels':int(diff.sum()),'outside_green':0})
heads = read(a.candidate/'green-head-draws.tsv') if (a.candidate/'green-head-draws.tsv').exists() else []
checked = transparent = protected_excluded = 0
for e in events:
 prefix = 'ae-%04d-%03d' % (int(e['tick']),int(e['call']))
 file = a.candidate/(prefix+'-before.png')
 if not file.exists(): continue
 before = np.array(Image.open(file).convert('RGBA'),dtype=np.uint32)
 body = np.array(Image.open(a.candidate/(prefix+'-body.png')).convert('RGBA'),dtype=np.uint32)
 owner = np.frombuffer((a.candidate/(prefix+'-before-owner.bin')).read_bytes(),dtype=np.uint8).reshape(112,96)
 raw = (a.assets/('explosion-newsh6-%s-8.hda'%e['id'])).read_bytes()
 src = np.frombuffer(raw[28:],dtype=np.uint8).reshape(112,96,4).astype(np.uint32)
 sp,dp = src[:,:,:3].max(2),before[:,:,:3].max(2)
 next_peak = (sp+dp+1)//2
 rgba = np.where(sp[:,:,None]>0,(src[:,:,:3]*next_peak[:,:,None]+sp[:,:,None]//2)//np.maximum(sp[:,:,None],1),0)
 alpha = src[:,:,3,None]
 expected = (rgba*alpha+before[:,:,:3]*(255-alpha)+127)//255
 mask = (owner==1)&(src[:,:,3]>0)
 # Green heads intentionally sit above this family. Their saved underlay is
 # checked by test-green-head-layer.py, not the old visible-destination oracle.
 protected = np.zeros(mask.shape, bool)
 for head in heads:
  if head['tick'] != e['tick'] or head['style'] != '0' or head['mirrored'] != '1': continue
  x,y=(int(head['x'])-int(e['x']))*8,(int(head['y'])-int(e['y']))*8
  x0,y0,x1,y1=max(0,x),max(0,y),min(96,x+96),min(112,y+112)
  if x0<x1 and y0<y1: protected[y0:y1,x0:x1]=True
 protected_excluded += int((mask & protected).sum())
 mask &= ~protected
 assert np.array_equal(body[:,:,:3][mask],expected[mask]),(prefix,'HD overlap blend changed')
 zero = src[:,:,3]==0
 assert np.array_equal(body[:,:,:3][zero],before[:,:,:3][zero])
 checked += int(mask.sum()); transparent += int(zero.sum())
report = {'state_collision_indexed_pixels_exact':True,'rng_neutral':True,'coverage_restoration_mismatch':0,
          'spawns':64,'draws':448,'all7frames_original_ttl':True,'existing_HD_pixels_exact_original_equation':checked,
          'transparent_pixels_unchanged':transparent,'head_footprint_pixels_excluded_from_visible_destination_oracle':protected_excluded,'window_frames':per_tick}
if a.output: a.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
