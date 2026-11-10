#!/usr/bin/env python3
"""Audit all observed terrain joins without exporting original map/pixel arrays."""
from collections import Counter,defaultdict
import argparse,json
from pathlib import Path
import struct
import numpy as np
from PIL import Image
from audit_level2_inventory import parse_level,PINS
from build_level2_terrain_completion import ROOT,IDS,GROUPS,checked,sha,decode_shapes,SHAPES_PIN

PACK=ROOT/'assets/hd/packs/level2-terrain-completion-v1'

def edges(a,b,d):
 if d not in ('R','D'): raise ValueError('Invalid join direction')
 return (a[:,-1],b[:,0]) if d=='R' else (a[-1,:],b[0,:])

def validate_candidate(pack, native):
 """Verify full resource bytes, manifest identities and exact source coverage."""
 pack=Path(pack)
 manifest=json.loads((pack/'MANIFEST.json').read_text())
 entries=manifest['tiles']
 if manifest['ids']!=list(IDS) or sorted(e['id'] for e in entries)!=list(IDS):
  raise ValueError('Incomplete or duplicate candidate manifest')
 for entry in entries:
  tile=entry['id'];stem=f'terrain-shapesz-{tile}-8'
  raw=checked(pack/(stem+'.hda'),entry['hda_sha256'],172060)
  if struct.unpack('<4s4I2i',raw[:28])!=(b'HDR1',2010000+tile,8,24,28,0,0):
   raise ValueError('Malformed HDA')
  rgba=np.frombuffer(raw[28:],dtype=np.uint8).reshape(224,192,4)
  source=native[tile]
  mask=np.repeat(np.repeat(np.frombuffer(source,dtype=np.uint8).reshape(28,24)!=0,8,axis=0),8,axis=1)
  if (not np.array_equal(rgba[:,:,3],mask*255) or np.any(rgba[~mask,:3]) or
      sha(source)!=entry['source_sha256'] or source.count(0)!=entry['source_zero_cells'] or
      int(mask.sum())!=entry['opaque_hd_pixels'] or sha(raw[28:])!=entry['rgba_sha256']):
   raise ValueError('Source coverage or RGBA mismatch')
  png=pack/(stem+'.png');checked(png,entry['png_sha256'])
  with Image.open(png) as im:
   if im.mode!='RGBA' or im.size!=(192,224) or im.tobytes()!=raw[28:]:
    raise ValueError('PNG and HDA mismatch')
 return len(entries)

def audit(data_dir,pack=PACK):
 native=decode_shapes(checked(Path(data_dir)/'shapesz.dat',SHAPES_PIN,318976))
 validated=validate_candidate(pack,native)
 _,_,lookup,cells,_=parse_level(checked(Path(data_dir)/'tyrian1.lvl',PINS['tyrian1.lvl']))
 grid=np.array([lookup[0][i] for i in cells[0]]).reshape(300,14)
 pairs=Counter()
 for y in range(300):
  for x in range(14):
   a=int(grid[y,x])
   for d,dx,dy in [('R',1,0),('D',0,1)]:
    if x+dx<14 and y+dy<300:
     b=int(grid[y+dy,x+dx])
     if a in IDS or b in IDS:pairs[a,b,d]+=1
 images={};missing=[]
 for tile in sorted(set(int(i) for i in grid.flatten())-{1}):
  roots=[Path(pack),ROOT/'assets/hd/current-terrain23',ROOT/'assets/hd/current-terrain24']
  file=next((r/f'terrain-shapesz-{tile}-8.hda' for r in roots if (r/f'terrain-shapesz-{tile}-8.hda').is_file()),None)
  if file is None:missing.append(tile);continue
  raw=file.read_bytes()
  if len(raw)!=172060 or struct.unpack('<4s4I2i',raw[:28])!=(b'HDR1',2010000+tile,8,24,28,0,0):raise ValueError('Malformed HDA')
  images[tile]=np.frombuffer(raw[28:],dtype=np.uint8).reshape(224,192,4)
 assembly=[]
 for name,rows in list(GROUPS.items())[:5]:
  pattern=np.array(rows);h,w=pattern.shape;counts=Counter(int(i) for i in grid.flatten())
  matches=sum(np.array_equal(grid[y:y+h,x:x+w],pattern) for y in range(301-h) for x in range(15-w))
  assembly.append({'family':name,'layout':rows,'complete_map_occurrences':matches,
   'tile_occurrence_counts':{str(i):counts[i] for row in rows for i in row},
   'all_member_occurrences_in_complete_assembly':all(counts[i]==matches for row in rows for i in row)})
 joins=[];constraints=defaultdict(list)
 for (a,b,d),count in sorted(pairs.items()):
  if a not in images or b not in images:continue
  aa,bb=edges(images[a],images[b],d);mask=(aa[:,3]>0)&(bb[:,3]>0)
  difference=np.abs(aa[:,:3].astype(float)-bb[:,:3].astype(float))[mask]
  joins.append({'a':a,'b':b,'direction':d,'map_occurrences':count,
   'opaque_edge_samples':int(mask.sum()),'mean_rgb_jump':round(float(difference.mean()),4) if difference.size else 0,
   'max_channel_jump':int(difference.max()) if difference.size else 0})
  if a in IDS and b not in IDS:constraints[a,('right' if d=='R' else 'bottom')].append((b,bb))
  if b in IDS and a not in IDS:constraints[b,('left' if d=='R' else 'top')].append((a,aa))
 conflicts=[]
 for (tile,side),values in sorted(constraints.items()):
  if len(values)<2:continue
  common=np.all(np.stack([v[:,3]>0 for _,v in values]),axis=0)
  if not np.any(common):continue
  stack=np.stack([v[:,:3].astype(float) for _,v in values]);span=(stack.max(axis=0)-stack.min(axis=0))[common]
  if np.any(span):conflicts.append({'tile':tile,'side':side,'fixed_neighbor_ids':[i for i,_ in values],
    'mean_target_range':round(float(span.mean()),4),'max_target_range':int(span.max()),
    'meaning':'One reusable edge cannot be pixel-identical to every unchanged neighbor. Visual material continuity needs scene review, not a claim of equal RGB.'})
 return {'schema':'level2-terrain-neighbor-audit-v1','source_map_sha256':PINS['tyrian1.lvl'],
  'validated_candidate_resources':validated,'candidate_source_coverage_verified':True,
  'blank_neighbor_joins_excluded':sum(count for (a,b,d),count in pairs.items() if a==1 or b==1),
  'complete_map_cells_read':4200,'all_nonblank_resources_found':not missing,'missing_resource_ids':missing,
  'assembly_evidence':assembly,'distinct_audited_directed_joins':len(joins),
  'audited_join_occurrences':sum(j['map_occurrences'] for j in joins),
  'joins':joins,'fixed_neighbor_exact_equality_conflicts':conflicts,
  'scope':'Every stored horizontal/vertical adjacency involving new art, not runtime sightings. RGB jumps include intentional structural transitions and are review measurements, not pass/fail seam proof.',
  'visual_scene_review_complete':False,'all_neighbor_joins_verified':False}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--data',required=True,type=Path);ap.add_argument('--pack',type=Path,default=PACK);ap.add_argument('--output',required=True,type=Path)
 args=ap.parse_args();report=audit(args.data,args.pack)
 if args.output.exists():raise SystemExit('Refusing overwrite')
 args.output.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['all_nonblank_resources_found','distinct_audited_directed_joins','audited_join_occurrences']}))
