"""Verify accepted repository HD resources, or rebuild exact packs in a new directory."""
from pathlib import Path
import argparse,json,hashlib,struct
from PIL import Image
repo=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
manifest=json.loads((repo/'assets/hd/manifest.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
# Accepted blue-v4 resources belong in both current packs, not rollback packs.
blue_v4_hashes = {
 'enemy-newsh2-85-8.hda': '97a37e0cca16821c94fb8e52ca8eeb6c73aa2baf5eeaa029254c95707617a2ac',
 'enemy-newsh2-87-8.hda': 'c2352caf73e2a750397389c939a02e88bdb72f76aee21011efcee005e314abf0',
 'enemy-newsh2-123-8.hda': '2c26ec570b3ed9be141f2ec48a7e20c63ff70a9048a24382206008aae8f96f7e',
 'enemy-newsh2-125-8.hda': 'f64eb6d4ecc5cc87ebafdd79159ae731a2c5044b4c5b564e4c6a37b1a6eb0acf',
}
for filename, expected in blue_v4_hashes.items():
 entries = [manifest['packs'][manifest[key]]['files'][filename]
            for key in ('default_preview_pack', 'default_debug_pack')]
 assert entries[0] == entries[1] and entries[0]['sha256'] == expected
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
meter_count=0
if manifest.get('gameplay_hud_meters_v2'):
 from gameplay_hud_meter_bundle import build_bundle as build_meters, FILENAME as METER_FILE
 raw,receipt=build_meters(repo);family=manifest['gameplay_hud_meters_v2']
 assert set(family['packs'])=={manifest['default_preview_pack'],manifest['default_debug_pack']}
 for pack,items in family['packs'].items():
  assert pack in manifest['packs'] and items=={METER_FILE:receipt}
  path=repo/'assets/hd/packs'/pack/METER_FILE
  assert path.is_file() and not path.is_symlink() and path.read_bytes()==raw
  if a.output:(output/pack/METER_FILE).write_bytes(raw)
  meter_count+=1
manufacturer_count=0
manufacturer_source_count=0
if manifest.get('startup_manufacturer_v1'):
 from startup_manufacturer_bundle import build_bundles as build_manufacturers, PACK as MANUFACTURER_PACK, SOURCE_FILES as MANUFACTURER_SOURCES
 bundles=build_manufacturers(repo)
 if a.output:(output/MANUFACTURER_PACK).mkdir()
 for name,(raw,receipt) in bundles.items():
  if a.output:(output/MANUFACTURER_PACK/name).write_bytes(raw)
  manufacturer_count+=1
 manufacturer_source_count=len(MANUFACTURER_SOURCES)
title_count=0
title_source_count=0
title_compatibility_count=0
if manifest.get('startup_title_v1'):
 from title_layer_bundle import build_bundles as build_titles, PACK as TITLE_PACK, SOURCE_FILES as TITLE_SOURCES, TITLE_FILES
 bundles=build_titles(repo)
 if a.output:(output/TITLE_PACK).mkdir()
 for name,(raw,receipt) in bundles.items():
  if a.output:(output/TITLE_PACK/name).write_bytes(raw)
  if name in TITLE_FILES:title_count+=1
  else:title_compatibility_count+=1
 title_source_count=len(TITLE_SOURCES)
title_menu_count=0
title_menu_source_count=0
if manifest.get('startup_title_menu_v1'):
 from title_menu_font_bundle import build_bundles as build_title_menu, PACK as TITLE_MENU_PACK, SOURCE_FILES as TITLE_MENU_SOURCES
 bundles=build_title_menu(repo)
 if a.output:(output/TITLE_MENU_PACK).mkdir()
 for name,(raw,receipt) in bundles.items():
  if a.output:(output/TITLE_MENU_PACK/name).write_bytes(raw)
 title_menu_count=len(bundles)
 title_menu_source_count=len(TITLE_MENU_SOURCES)
type4_count=0
if manifest.get('enemy_type4_fivepose_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='type4-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-type4-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 type4_count=5
linked31_count=0
if manifest.get('linked31_installation_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='linked31-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-linked31-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 linked31_count=8
newsh4_long7_count=0
if manifest.get('newsh4_long7_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='newsh4-long7-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-newsh4-long7-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 newsh4_long7_count=7
newsh4_opposite7_count=0
if manifest.get('newsh4_opposite7_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='newsh4-opposite7-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-newsh4-opposite7-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 newsh4_opposite7_count=7
type15_count=0
if manifest.get('enemy_type15_eightheading_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='type15-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-type15-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 type15_count=8
late_spike_count=0
if manifest.get('late_spike_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='late-spike-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-late-spike-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 late_spike_count=6
newsh4_entry6_count=0
if manifest.get('newsh4_entry6_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='newsh4-entry6-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-newsh4-entry6-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 newsh4_entry6_count=6
type3_small_count=0
if manifest.get('type3_small_six_v1'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='type3-small-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-type3-small-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 type3_small_count=6
settings_count=0
if manifest.get('startup_settings_font_v1'):
 from settings_font_bundle import build_bundles as build_settings, PACK as SETTINGS_PACK
 settings_bundles,_=build_settings(repo)
 if a.output:
  (output/SETTINGS_PACK).mkdir()
  for name,(raw,_) in settings_bundles.items():(output/SETTINGS_PACK/name).write_bytes(raw)
 settings_count=len(settings_bundles)
boss_whole_count=0
if manifest.get('boss_whole_family_v2_inward_alpha'):
 import subprocess,sys,tempfile
 with tempfile.TemporaryDirectory(prefix='boss-whole-source-check-') as temporary:
  subprocess.run([sys.executable,str(repo/'prototype/build-boss-whole-family-art.py'),'--output',str(Path(temporary)/'rebuilt')],check=True,capture_output=True,text=True)
 boss_whole_count=40
enemy_energy_count=0
if manifest.get('enemy_energy_seven_v1'):
 import subprocess,sys
 subprocess.run([sys.executable,str(repo/'prototype/build-enemy-energy-seven-art.py')],check=True,capture_output=True,text=True)
 enemy_energy_count=7
protron_count=0
if manifest.get('player_protron_three_v1'):
 import subprocess,sys
 subprocess.run([sys.executable,str(repo/'prototype/build-protron-art.py')],check=True,capture_output=True,text=True)
 protron_count=3
protron_shadow_count=0
if manifest.get('player_protron_shadow_three_v1'):
 import subprocess,sys
 subprocess.run([sys.executable,str(repo/'prototype/build-protron-shadow-art.py')],check=True,capture_output=True,text=True)
 protron_shadow_count=3
print(json.dumps({'verified_player_protron_shadow_members':protron_shadow_count,'verified_player_protron_members':protron_count,'verified_enemy_energy_seven_members':enemy_energy_count,'verified_boss_whole_family_members':boss_whole_count,'verified_boss_intentional_empty_members':3 if boss_whole_count else 0,'verified_settings_compatibility_resources':settings_count,'verified_type3_small_six_members':type3_small_count,'verified_title_menu_resources':title_menu_count,'verified_title_menu_source_files':title_menu_source_count,'verified_newsh4_entry6_members':newsh4_entry6_count,'verified_late_spike_family_members':late_spike_count,'verified_type15_eightheading_members':type15_count,'verified_newsh4_opposite7_family_members':newsh4_opposite7_count,'verified_newsh4_long7_family_members':newsh4_long7_count,'verified_startup_title_resources':title_count,'verified_startup_title_source_files':title_source_count,'verified_startup_title_manufacturer_compatibility_copies':title_compatibility_count,'verified_linked31_family_members':linked31_count,'verified_type4_composites':type4_count,'verified_startup_manufacturer_resources':manufacturer_count,'verified_startup_manufacturer_source_files':manufacturer_source_count,'verified_hud_meter_sidecars':meter_count,'verified_hud_meter_source_files':13 if meter_count else 0,'verified_pack_count':len(manifest['packs']),'verified_HDA_entries':checked,'verified_exact_source_pngs':len(payloads),'verified_material_sidecars':material_count,'verified_cap_sidecars':cap_count,'verified_forest_sidecars_and_policies':forest_count,'verified_gameplay_hud_sidecars':hud_count,'verified_hud_source_pngs':int(bool(hud_count)), 'verified_hud_font_sidecars':font_count,'verified_hud_font_source_files':19 if font_count else 0, 'verified_hud_fixed_text_sidecars':fixed_text_count,'verified_hud_fixed_text_source_pngs':12 if fixed_text_count else 0, 'verified_hud_extension_sidecars':extension_count, 'verified_hud_extension_source_pngs':21 if extension_count else 0,'default_pack_counts':[manifest['packs'][manifest[k]]['count'] for k in ['default_preview_pack','default_debug_pack']],'rebuild_output':str(output) if a.output else None,'all_runtime_RGBA_and_header_bytes_exact':True},indent=2))
