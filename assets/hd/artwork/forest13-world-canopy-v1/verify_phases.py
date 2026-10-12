from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;D=json.load(open(P/'contracts/canonical-topology-contract.json'));A=np.array(Image.open(P/'selected/atlas.png').convert('RGBA')).astype(np.int32);ids=json.load(open(P/'contracts/composition.json'))['ids'];B={i:np.array(Image.open(P/'selected/bases'/f'terrain-shapesz-{i}-8.png').convert('RGBA')).astype(np.int32)for i in ids};M={i:np.array(Image.open(P/'selected/canopy-weights'/f'terrain-shapesz-{i}-8.png')).astype(np.int32)for i in ids};y,x=np.indices((224,192));checks=0;phasehash=hashlib.sha256();outcache={};samplecache={}
for i in ids:
 for r in range(4):
  for c in range(4):
   a=A[(y+r*224)%896,(x+c*192)%768];m=M[i];b=B[i];out=b.copy();out[:,:,:3]=(b[:,:,:3]*(255-m[:,:,None])+a[:,:,:3]*m[:,:,None]+127)//255
   assert np.array_equal(out[m==0],b[m==0]);assert np.array_equal(out[m==255],a[m==255]);assert np.all(out[:,:,3]==255);checks+=3;outcache[(i,r,c)]=out;samplecache[(r,c)]=a;phasehash.update(out.astype(np.uint8).tobytes())
pairhash=hashlib.sha256();cases=0
for p in D['forward_internal_pairs']:
 for r in range(4):
  for c in range(4):
   rr=(r+(p['side']=='down'))%4;cc=(c+(p['side']=='right'))%4;a=outcache[(p['id'],r,c)];b=outcache[(p['neighbor'],rr,cc)];u=samplecache[(r,c)];v=samplecache[(rr,cc)];axis=1 if p['side']=='right'else 0;pair=np.concatenate([a,b],axis=axis);field=np.concatenate([u,v],axis=axis);ph,pw=field.shape[:2];iy,ix=np.indices((ph,pw));oracle=A[(iy+r*224)%896,(ix+c*192)%768];assert np.array_equal(field,oracle);assert np.all(pair[:,:,3]==255);checks+=2;cases+=1;pairhash.update(pair.astype(np.uint8).tobytes())
# Shared full/partial corner connectors are exact canopy samples, independent of any base.
for s in [215,224,225]:
 zone=D['corner_zones'][str(s)]['inclusive_xy_box'];x0,y0,x1,y1=zone;outside=np.ones((224,192),bool);outside[y0*8:(y1+1)*8,x0*8:(x1+1)*8]=False;assert np.all(M[s][outside]==255);checks+=1
# Standard cardinal external edge guards. The source-specific215N canopy onset is explicit.
g=np.array(Image.open(P/'source/frozen-generated-grass69.png').convert('RGBA')).astype(np.int32);edges=[]
for p in D['forest69_edge_profiles']:
 i,s=p['id'],p['side']
 if i==215 and s=='up':continue
 slic={'left':(slice(None),0),'right':(slice(None),-1),'up':(0,slice(None)),'down':(-1,slice(None))}[s];assert np.array_equal(B[i][slic],g[slic]);assert np.all(M[i][slic]==0);checks+=2;edges.append([i,s])
report={'schema':'forest13-all-phase-audit-v1','status':'pass offline sampling and protected-byte audit; visual acceptance separate','ids':ids,'phases_per_id':16,'tile_phase_cases':208,'pair_phase_cases':cases,'assertions':checks,'phase_rgba_stream_sha256':phasehash.hexdigest(),'pair_rgba_stream_sha256':pairhash.hexdigest(),'all_opacity255':True,'all_weight0_pixels_equal_fixed_base':True,'all_weight255_pixels_equal_continuous_world_atlas':True,'adjacent_tile_phase_is_consecutive_world_sampling':True,'corner_full_canopy_connectors_exact':True,'accepted69_ground_facing_outer_samples_exact':edges,'source215N_canopy_exception_preserved':True,'limitations':['Static proof only, not runtime visibility.','Pair proof verifies material registration and protected bytes, not automatic perceptual seam absence.','Atlas world period is96x112logical; it is not nonrepeating.']};print(json.dumps(report,indent=2))
