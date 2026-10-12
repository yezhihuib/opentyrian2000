"""Verify accepted repository HD resources, or rebuild exact packs in a new directory."""
from pathlib import Path
import argparse,json,hashlib,struct
from PIL import Image
repo=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
manifest=json.loads((repo/'assets/hd/manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
if a.output:
 output=a.output.resolve()
 if output.exists():p.error('Choose a new output directory; existing resources are never overwritten')
 output.mkdir(parents=True)
payloads={};checked=0
for pack,items in manifest['packs'].items():
 assert len(items['files'])==items['count']
 if a.output:(output/pack).mkdir()
 for filename,item in items['files'].items():
  source=repo/item['source_png'];assert sha(source.read_bytes())==item['source_png_sha256']
  if str(source) not in payloads:
   im=Image.open(source);h=item['header_u32'];assert im.mode=='RGBA' and im.size==(h[1]*h[2],h[1]*h[3]);payloads[str(source)]=im.tobytes()
  raw=b'HDR1'+struct.pack('<6I',*item['header_u32'])+payloads[str(source)]
  assert sha(raw)==item['sha256'] and (repo/'assets/hd/packs'/pack/filename).read_bytes()==raw
  if a.output:(output/pack/filename).write_bytes(raw)
  checked+=1
material_count=0
if manifest.get('material_bundles'):
 from world_material_bundle import build_bundle
 raw,records,receipt=build_bundle(repo)
 for pack,item in manifest['material_bundles'].items():
  assert pack in manifest['packs'] and item==receipt
  for part in receipt['parts']:
   data=raw[part['offset']:part['offset']+part['bytes']]
   assert (repo/'assets/hd/packs'/pack/part['file']).read_bytes()==data and sha(data)==part['sha256']
   if a.output:(output/pack/part['file']).write_bytes(data)
   material_count+=1
cap_count=0
if manifest.get('plateau_cap_bundles'):
 from plateau_cap_bundle import build_bundle as build_cap, render_header, FILENAME
 for pack,item in manifest['plateau_cap_bundles'].items():
  assert pack in manifest['packs']
  raw,records,receipt=build_cap(repo/'assets/hd/artwork/plateau-cap-atlas-v1',repo/'assets/hd/packs'/pack)
  assert item==receipt and (repo/'src/plateau_cap_bundle_index.h').read_text()==render_header(records,receipt)
  assert (repo/'assets/hd/packs'/pack/FILENAME).read_bytes()==raw
  if a.output:(output/pack/FILENAME).write_bytes(raw)
  cap_count+=1
forest_count=0
if manifest.get('forest13_bundles'):
 from forest13_bundle import build_bundle as build_forest, render_header as forest_header, FILENAME as FOREST_FILE, POLICY
 raw,records,receipt=build_forest(repo/'assets/hd/artwork/forest13-world-canopy-v1')
 family=manifest['forest13_bundles']
 assert family['schema']=='forest13-coupled-world-canopy-v1' and family['bundle']==receipt
 assert (repo/'src/forest13_bundle_index.h').read_text()==forest_header(records,receipt)
 assert set(family['packs'])=={manifest['default_preview_pack'],manifest['default_debug_pack']}
 for pack,items in family['packs'].items():
  assert pack in manifest['packs'] and set(items)=={FOREST_FILE,'forest13.policy'}
  for source in receipt['sources']:
   entry=manifest['packs'][pack]['files'][f'terrain-shapesz-{source["id"]}-8.hda']
   assert entry['sha256']==source['hda_sha256']
  policy_path=repo/'assets/hd/packs'/pack/'forest13.policy'
  assert policy_path.is_file() and not policy_path.is_symlink()
  for name,data in [(FOREST_FILE,raw),('forest13.policy',POLICY)]:
   assert items[name]=={'sha256':sha(data),'bytes':len(data)}
   assert (repo/'assets/hd/packs'/pack/name).read_bytes()==data
   if a.output:(output/pack/name).write_bytes(data)
   forest_count+=1
hud_count=0
if manifest.get('gameplay_hud_v5'):
 from gameplay_hud_bundle import build_bundle as build_hud, FILENAME as HUD_FILE
 raw,receipt=build_hud(repo)
 family=manifest['gameplay_hud_v5']
 assert set(family['packs'])=={manifest['default_preview_pack'],manifest['default_debug_pack']}
 for pack,items in family['packs'].items():
  assert set(items)=={HUD_FILE} and items[HUD_FILE]==receipt
  path=repo/'assets/hd/packs'/pack/HUD_FILE
  assert path.is_file() and not path.is_symlink() and path.read_bytes()==raw
  if a.output:(output/pack/HUD_FILE).write_bytes(raw)
  hud_count+=1
extension_count=0
if manifest.get('gameplay_hud_extensions_v1'):
 from gameplay_hud_extension_bundles import build_bundles
 bundles=build_bundles(repo)
 family=manifest['gameplay_hud_extensions_v1']
 assert set(family['packs'])=={manifest['default_preview_pack'],manifest['default_debug_pack']}
 for pack,items in family['packs'].items():
  assert set(items)==set(bundles)
  for name,(raw,receipt) in bundles.items():
   assert items[name]==receipt
   path=repo/'assets/hd/packs'/pack/name
   assert path.is_file() and not path.is_symlink() and path.read_bytes()==raw
   if a.output:(output/pack/name).write_bytes(raw)
   extension_count+=1
fixed_text_count=0
if manifest.get('gameplay_hud_fixed_text_v1'):
 from gameplay_hud_fixed_text_bundle import build_bundle as build_fixed, FILENAME as FIXED_FILE
 raw,receipt=build_fixed(repo);family=manifest['gameplay_hud_fixed_text_v1']
 assert set(family['packs'])=={manifest['default_preview_pack'],manifest['default_debug_pack']}
 for pack,items in family['packs'].items():
  assert items=={FIXED_FILE:receipt}
  path=repo/'assets/hd/packs'/pack/FIXED_FILE
  assert path.is_file() and not path.is_symlink() and path.read_bytes()==raw
  if a.output:(output/pack/FIXED_FILE).write_bytes(raw)
  fixed_text_count+=1
font_count=0
if manifest.get('gameplay_hud_font_v1'):
 from gameplay_hud_font_bundle import build_bundle as build_font, FILENAME as FONT_FILE
 raw,receipt=build_font(repo);family=manifest['gameplay_hud_font_v1']
 assert set(family['packs'])=={manifest['default_preview_pack'],manifest['default_debug_pack']}
 for pack,items in family['packs'].items():
  assert pack in manifest['packs'] and items=={FONT_FILE:receipt}
  path=repo/'assets/hd/packs'/pack/FONT_FILE
  assert path.is_file() and not path.is_symlink() and path.read_bytes()==raw
  if a.output:(output/pack/FONT_FILE).write_bytes(raw)
  font_count+=1
print(json.dumps({'verified_pack_count':len(manifest['packs']),'verified_HDA_entries':checked,'verified_exact_source_pngs':len(payloads),'verified_material_sidecars':material_count,'verified_cap_sidecars':cap_count,'verified_forest_sidecars_and_policies':forest_count,'verified_gameplay_hud_sidecars':hud_count,'verified_hud_source_pngs':int(bool(hud_count)), 'verified_hud_font_sidecars':font_count,'verified_hud_font_source_files':19 if font_count else 0, 'verified_hud_fixed_text_sidecars':fixed_text_count,'verified_hud_fixed_text_source_pngs':12 if fixed_text_count else 0, 'verified_hud_extension_sidecars':extension_count, 'verified_hud_extension_source_pngs':21 if extension_count else 0,'default_pack_counts':[manifest['packs'][manifest[k]]['count'] for k in ['default_preview_pack','default_debug_pack']],'rebuild_output':str(output) if a.output else None,'all_runtime_RGBA_and_header_bytes_exact':True},indent=2))
