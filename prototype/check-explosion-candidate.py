"""Read-only contract/candidate checks for unbound remaining explosion art.

This utility never installs HDA files, changes palettes or enables renderer slots.
Use the exported real-call catalog, not guessed sprite ranges or recentered pieces.
"""
from pathlib import Path
import argparse,hashlib,json,struct
from PIL import Image

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write_new(path,value):
 path=path.resolve();path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')

p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
c=sub.add_parser('contract');c.add_argument('--catalog',type=Path,required=True);c.add_argument('--output',type=Path,required=True)
c=sub.add_parser('check');c.add_argument('--catalog',type=Path,required=True);select=c.add_mutually_exclusive_group(required=True);select.add_argument('--assembly');select.add_argument('--type',type=int);c.add_argument('--candidate',type=Path,required=True,help='JSON manifest with sheet,density,logical_size,anchor and frames[{id_1_based,png,sha256}]');c.add_argument('--report',type=Path,required=True)
a=p.parse_args();catalog=json.loads(a.catalog.read_text(encoding='utf-8'))
assert catalog['sheet']=='newsh6.shp' and catalog['logical_tile_size']==[12,14] and catalog['tile_anchor']==[0,0]
protected=set(catalog['protected_existing_ids']);assert set(range(122,134)).issubset(protected)
families={x['type']:x for x in catalog['families']};frames=catalog['shared_frames']
assert all(int(k) not in protected for k in frames),'Protected accepted type1 must not be staged again'
def binding(id):
 original=frames[str(id)];assert original['size']==[12,14] and original['anchor']==[0,0]
 return {'sheet':'newsh6.shp','id_1_based':id,'logical_size':[12,14],'anchor':[0,0],'density':8,'rgba_size':[96,112],'future_filename':f'explosion-newsh6-{id}-8.hda','future_header_values':[106*10000+id,8,12,14,0,0],'uses':original['uses'],'production_status':'unbound; renderer does not consume this candidate','original_png':original['png'],'original_png_sha256':original['sha256']}
if a.command=='contract':
 report={'schema':'opentyrian-remaining-explosion-staging-contract-v1','catalog_sha256':sha(a.catalog),'catalog_path':str(a.catalog.resolve()),'active_protected_type1_ids':sorted(protected),'active_renderer_bindings_changed':False,'pending_unique_bindings':[binding(int(k)) for k in sorted(frames,key=int)],'families':catalog['families'],'assemblies':catalog['assemblies'],'blend_contract':'Original engine retains integer indexed hue-overwrite/value-average or opaque. Future true-color consumption requires narrow reviewed integration; never bake 50% alpha into art.','png_manifest_schema':{'sheet':'newsh6.shp','density':8,'logical_size':[12,14],'anchor':[0,0],'frames':[{'id_1_based':192,'png':'frames8x/newsh6-192.png','sha256':'complete lowercase SHA256'}]},'visual_review_required':['All frames at actual display size','Original per-piece offsets and fixed canvases','Mixed/opaque overlap and cleanup tail','No crop/flash/missing frame fallback'],'runtime_activation_done':False}
 write_new(a.output,report);print(json.dumps({'contract':str(a.output.resolve()),'pending_unique_bindings':len(frames),'runtime_activation_done':False},indent=2));raise SystemExit()
if a.assembly:
 assemblies=[x for x in catalog['assemblies'] if x['id']==a.assembly];assert len(assemblies)==1,'Unknown assembly'
 assembly=assemblies[0];types=assembly['types']
else:
 assert a.type in families and a.type!=1,'Unknown or protected type1';types=[a.type];assembly=None
assert all(t!=1 for t in types),'Protected type1 may not be staged'
expected=set(id for t in types for id in families[t]['unique_ids_1_based'])
assert expected and not expected&protected,'No active protected ID or empty family'
assert expected.issubset(set(map(int,frames))),'Family references lookup-only/not exported frames; do not invent art'
manifest=json.loads(a.candidate.read_text(encoding='utf-8'))
assert manifest['sheet']=='newsh6.shp' and manifest['density']==8 and manifest['logical_size']==[12,14] and manifest['anchor']==[0,0]
entries=manifest['frames'];ids=[x['id_1_based'] for x in entries];assert len(ids)==len(set(ids)) and set(ids)==expected,'Exact selected shared ID set required; no omissions, extras or duplicate frames'
verified=[];root=a.candidate.resolve().parent
for item in sorted(entries,key=lambda x:x['id_1_based']):
 image=(root/item['png']).resolve();assert image.is_relative_to(root) and image.suffix.lower()=='.png','PNG must be inside candidate root'
 assert len(item['sha256'])==64 and sha(image)==item['sha256'],'Candidate SHA does not match file bytes'
 with Image.open(image) as im:
  assert im.mode=='RGBA' and im.size==(96,112),'Exact straight RGBA fixed 96x112 canvas required'
  im.verify()
 b=binding(item['id_1_based']);b['candidate_png']=str(image);b['candidate_sha256']=sha(image);b['expected_hda_header_hex']=(b'HDR1'+struct.pack('<6I',*b['future_header_values'])).hex();verified.append(b)
report={'schema':'opentyrian-remaining-explosion-candidate-check-v1','status':'Structural staging check passed; no visual approval or activation','catalog_sha256':sha(a.catalog),'candidate_manifest_sha256':sha(a.candidate),'types':types,'unique_frame_count':len(verified),'frames':verified,'assembly':assembly,'original_per_tick_family_sequences':[{'type':t,'ids_1_based':families[t]['ids_1_based'],'mode':families[t]['mode'],'ttl_initial':families[t]['ttl_initial']} for t in types],'runtime_activation_done':False,'visual_review_done':False,'type1_protected':True}
write_new(a.report,report);print(json.dumps({'report':str(a.report.resolve()),'unique_frame_count':len(verified),'runtime_activation_done':False,'visual_review_done':False},indent=2))
