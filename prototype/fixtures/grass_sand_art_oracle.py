"""Frozen grass/sand v3 and strict 7c7 artifact checks, without gameplay."""
from pathlib import Path
import hashlib, io, json, struct
from PIL import Image
BASE = '7c7aee388e384840915bd2532bbcc038c3d5047e'
BASE_MANIFEST_SHA = 'e8356da33211cdcc4d5bacae611a260c9aa1c3df7315535ea480481717e15f1f'
FREEZE_SHA = '01cab117a442828ecf499c5c8955bba29d64658afe5b6dd2f35f9019945083a4'
CONTRACT_SHA = '7b487e929a0c744227b474f16362a704a6938a6ab3cc5ae8ffe201eba05ac9b4'
REBUILD_SHA = 'a2eaaa07e6e50fc143342f7fe9134be1264c7e7689fefe7693666cb46588ca64'
IDS = [66,67,69,76,78,79,80,89,90]
NEW = {f'terrain-shapesz-{i}-8.hda' for i in IDS}
CLOUD64_HDA = '1f9378615e16157f59113a47066dd28a52433c28e5a36d8845491b355e64a3b8'
CLOUD64_PNG = '5a7b79fac3399d87cde0fb2d855e92e2121ed127a5112f7afcb5216e70deead3'
FROZEN_PURPLE_METADATA = {
 'assets/hd/artwork/purple-installation32-41-v2/selected-manifest.json':'33a08293409f559f95890cb33560c81f668bc784ad8d8ff848df4cf338a2bc0f',
 'assets/hd/artwork/purple-installation32-41-v2/original-alpha-contract.json':'44060a4deec2a9bbeb4a9c7c0498b9a2d2b4b97b76b513f9cab0ca65e797610a',
 'assets/hd/artwork/layer3-purple13-v4/runtime-overlay/manifest.json':'8b0d2ad2f11125657f5fea3739c5fae9368cc12a0e0e512919fc73ed5b936f3a'}
def sha(data): return hashlib.sha256(data).hexdigest()
def owned(root, relative):
 root=Path(root).resolve();p=root/relative
 assert not p.is_symlink(), ('Symlink is not a canonical artifact', relative)
 p=p.resolve();assert p.is_relative_to(root), ('Artifact path escaped root', relative)
 return p
def freeze():
 data=Path(__file__).with_name('grass-sand9-v3-frozen-runtime-manifest.json').read_bytes()
 assert sha(data)==FREEZE_SHA, 'Frozen runtime manifest changed'
 f=json.loads(data);assert f['ids']==IDS and f['base_commit']==BASE
 assert f['capacity']==321 and f['terrain_registry']==162
 assert [r['source_id'] for r in f['assets']]==IDS
 return f
def baseline(data):
 assert sha(data)==BASE_MANIFEST_SHA, 'Baseline must be the exact current7c7 manifest, including accepted cloud64'
 return json.loads(data)
def delta(files, prior):
 assert set(files)-set(prior)==NEW and not(set(prior)-set(files)), 'Expected exactly nine additions and no removals'
 for name, record in prior.items():assert files[name]==record, ('Prior manifest record changed',name)
 assert files['terrain-shapesz-64-8.hda']['sha256']==CLOUD64_HDA, 'Current cloud64 HDA changed'
 assert files['terrain-shapesz-64-8.hda']['source_png_sha256']==CLOUD64_PNG, 'Current cloud64 PNG changed'
def image_bytes(data, size, require_rgba=True):
 with Image.open(io.BytesIO(data)) as im:
  assert list(im.size)==list(size) and (not require_rgba or im.mode=='RGBA'), ('Canonical PNG size/mode mismatch',im.size,im.mode)
  return im.convert('RGBA').tobytes()
def selected_asset(record, png, hda):
 i=record['source_id'];assert i in IDS
 assert record['layer']==1 and record['slot']==312+IDS.index(i)
 assert record['header_u32']==[2010000+i,8,24,28,0,0] and record['size']==[192,224]
 assert record['opacity']=='all255'
 assert sha(png)==record['png_sha256'], ('Frozen PNG file changed',i)
 rgba=image_bytes(png,[192,224]);assert sha(rgba)==record['rgba_sha256'], ('Frozen decoded RGBA changed',i)
 assert len(hda)==172060 and hda[:4]==b'HDR1', ('HDA size/magic mismatch',i)
 assert list(struct.unpack('<6I',hda[4:28]))==record['header_u32'], ('HDA header mismatch',i)
 assert hda[28:]==rgba and set(rgba[3::4])=={255}, ('HDA/PNG or alpha mismatch',i)
 assert sha(hda)==record['hda_sha256'], ('Frozen HDA changed',i)
 return {'id':i,'slot':record['slot'],'png_sha256':sha(png),'rgba_sha256':sha(rgba),'hda_sha256':sha(hda),'all_alpha255':True}
def package(root):
 f=freeze();contract_bytes=owned(root,'contract.json').read_bytes()
 assert sha(contract_bytes)==CONTRACT_SHA, 'Frozen package contract changed'
 c=json.loads(contract_bytes)
 assert c['selected']==f['assets'] and c['ids']==IDS and c['slots']==list(range(312,321))
 assert c['base_commit']==BASE and c['layer']==1 and c['capacity']==321 and c['terrain_registry']==162
 assert c['original_game_data_required'] is False and c['generation_at_rebuild'] is False
 assert sha(owned(root,'rebuild.py').read_bytes())==REBUILD_SHA, 'Corrected revision2 rebuilder changed'
 for relative,expected in c['inputs'].items():
  data=owned(root,relative).read_bytes();assert len(data)==expected['bytes'] and sha(data)==expected['file_sha256'], ('Canonical input changed',relative)
  if relative.endswith('.png'):assert sha(image_bytes(data,expected['size'],require_rgba=False))==expected['rgba_sha256']
 selected=[selected_asset(r,owned(root,r['png']).read_bytes(),owned(root,r['hda']).read_bytes()) for r in c['selected']]
 assert {p.name for p in owned(root,'runtime-overlay').glob('*.hda')}==NEW, 'Extra/missing formal HDA'
 assert {p.name for p in owned(root,'output').glob('*.png')}=={n.replace('.hda','.png') for n in NEW}, 'Extra/missing formal PNG'
 inventory_data=owned(root,'handoff-inventory.json').read_bytes()
 assert sha(inventory_data)=='e875ecd3fe33b0867ab5dd18ff664035c62b2276a48e4d75a6e31bb2df67edf6', 'Frozen corrected inventory changed'
 inventory=json.loads(inventory_data)
 assert inventory['source_freeze_revision']==2, 'Corrected source inventory revision2 required'
 listed={r['path']:r for r in inventory['files']}
 assert len(listed)==inventory['file_count'] and sum(r['bytes'] for r in listed.values())==inventory['bytes']
 actual={str(p.relative_to(root)) for p in Path(root).rglob('*') if p.is_file() and p.name!='handoff-inventory.json'}
 assert actual==set(listed), 'Formal package inventory differs'
 for relative,r in listed.items():
  data=owned(root,relative).read_bytes();assert len(data)==r['bytes'] and sha(data)==r['sha256'], ('Frozen inventory mismatch',relative)
 return {'selected':selected,'input_count':len(c['inputs']),'inventory_files':len(listed),'source_freeze_revision':2,'contract_sha256':CONTRACT_SHA,'rebuild_sha256':REBUILD_SHA,'frozen_runtime_manifest_sha256':FREEZE_SHA}

def manifest_delta(current, prior):
 """Only the two existing defaults and nine new canonical source records grow."""
 defaults={prior['default_preview_pack'],prior['default_debug_pack']}
 for key in ['default_preview_pack','default_debug_pack']:
  assert current[key]==prior[key], ('Default pack changed',key)
 assert set(current['packs'])==set(prior['packs']), 'Pack inventory changed'
 for name,record in prior['packs'].items():
  if name not in defaults:assert current['packs'][name]==record, ('Nondefault pack changed',name)
  else:delta(current['packs'][name]['files'],record['files'])
 expected={r['hda_sha256']:r for r in freeze()['assets']}
 before=prior['source_pngs'];after=current['source_pngs']
 assert set(after)-set(before)==set(expected) and not(set(before)-set(after)), 'Canonical source catalog requires exactly nine additions'
 for key,record in before.items():assert after[key]==record, ('Prior canonical source changed',key)
 for key,r in expected.items():
  record=after[key]
  assert record['sha256']==r['png_sha256'] and record['RGBA_sha256']==r['rgba_sha256'], ('New canonical source record mismatch',r['source_id'])
  filename=Path(r['hda']).name
  for name in defaults:assert current['packs'][name]['files'][filename]['source_png']==record['path'], ('Canonical source path mismatch',filename)
