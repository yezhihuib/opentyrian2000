"""Audit the accepted purple22 asset import without game execution or source edits.

Checks both default packs, canonical PNG transports and original alpha contracts.
An optional Git baseline verifies that precisely the22 reviewed files were added.
"""
from pathlib import Path
import argparse,hashlib,io,json,struct,subprocess,tempfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',type=Path,default=ROOT)
p.add_argument('--baseline',help='Optional Git revision for preserved-prior-file verification')
p.add_argument('--report',type=Path)
a=p.parse_args();root=a.source.resolve();manifest_path=root/'assets/hd/manifest.json';manifest=json.loads(manifest_path.read_text())
PURPLE=[150,156,157,158,159,160,166,168,169,170,176,177,178]
ENTITY=[169,207,245,273,275,277,279,281,283]
NEW={f'terrain-shapesz-{i}-8.hda'for i in PURPLE}|{f'enemy-newsh2-{i}-8.hda'for i in ENTITY}
def digest(data):return hashlib.sha256(data).hexdigest()
def owned(relative):
 path=(root/relative).resolve();assert path.is_relative_to(root),relative;return path
old=None
if a.baseline:
 old=json.loads(subprocess.check_output(['git','-C',str(root),'show',a.baseline+':assets/hd/manifest.json']))
contract_path=owned('assets/hd/artwork/purple-installation32-41-v2/original-alpha-contract.json');contract=json.loads(contract_path.read_text())
selected_path=owned('assets/hd/artwork/purple-installation32-41-v2/selected-manifest.json');selected=json.loads(selected_path.read_text());assert sorted(r['id']for r in selected)==ENTITY
terrain_path=owned('assets/hd/artwork/layer3-purple13-v4/runtime-overlay/manifest.json');terrain=json.loads(terrain_path.read_text());assert terrain['source_ids']==PURPLE and terrain['slots']==list(range(290,303))
reports=[];seen={}
for key,count in [('default_preview_pack',316),('default_debug_pack',320)]:
 name=manifest[key];info=manifest['packs'][name];files=info['files'];assert info['count']==len(files)==count
 directory=owned('assets/hd/packs/'+name);assert {f.name for f in directory.glob('*.hda')}==set(files)
 prior_count=None
 if old:
  prior=old['packs'][old[key]]['files'];prior_count=len(prior)
  assert set(files)-set(prior)==NEW and not(set(prior)-set(files))
  for filename,record in prior.items():assert files[filename]==record,filename
 for filename,record in files.items():
  data=(directory/filename).read_bytes();assert digest(data)==record['sha256'];assert data[:4]==b'HDR1'
  header=list(struct.unpack_from('<6I',data,4));assert header==record['header_u32'];_,density,width,height,_,_=header
  assert len(data)==28+width*height*density*density*4
  if filename not in NEW:continue
  png_path=owned(record['source_png']);png=png_path.read_bytes();assert digest(png)==record['source_png_sha256']
  im=Image.open(io.BytesIO(png)).convert('RGBA');assert im.size==(192,224)and im.tobytes()==data[28:]
  if filename.startswith('terrain'):
   id=int(filename.split('-')[2]);assert header==[2010000+id,8,24,28,0,0]
   assert set(data[31::4])=={255}and record['sha256']==terrain['files'][filename]
  else:
   id=int(filename.split('-')[2]);assert header==[1010000+id,8,24,28,6,7]
   holes=set(map(tuple,contract[str(id)]));alpha=data[31::4]
   assert len(alpha)==192*224
   for y in range(224):
    for x in range(192):assert alpha[y*192+x]==(0 if (x//8,y//8)in holes else 255)
   sel=next(r for r in selected if r['id']==id)
   assert all(sel[k]==record[k]for k in ['sha256','header_u32','source_png','source_png_sha256'])
  if filename in seen:assert digest(data)==seen[filename]
  seen[filename]=digest(data)
 reports.append({'pack':name,'count':count,'every_manifest_hash_and_header_exact':True,'prior_count':prior_count,'prior_entries_unchanged':True if old else None,'exact22_additions':True if old else None,'all22_canonical_png_payloads_exact':True})
assert set(seen)==NEW
report={'status':'passed','packs':reports,'new_asset_sha256':seen,'all13_terrain_opaque':True,'all9_entity_sparse_alpha_exact':True,'geometry_and_anchors_exact':True,'manifest_sha256':digest(manifest_path.read_bytes()),'alpha_contract_sha256':digest(contract_path.read_bytes()),'entity_selected_manifest_sha256':digest(selected_path.read_bytes()),'terrain_manifest_sha256':digest(terrain_path.read_bytes()),'baseline':a.baseline,'scope':'Read-only artifact/manifest import audit; no game run, capture or visual acceptance claim.'}
out=a.report or Path(tempfile.mkdtemp(prefix='purple-selected-pack-audit-'))/'result.json';out.write_text(json.dumps(report,indent=2)+'\n');print('PASS: default packs316/320; all manifest SHA/header/size checks; all22 canonical PNG/HDA exact;13 opaque terrain and9 exact sparse-alpha entities;'+(' exactly22 additions with all prior manifest entries unchanged.'if old else ' no baseline comparison requested.'));print('Report:',out)
