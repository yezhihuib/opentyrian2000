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
print(json.dumps({'verified_pack_count':len(manifest['packs']),'verified_HDA_entries':checked,'verified_exact_source_pngs':len(payloads),'verified_material_sidecars':material_count,'default_pack_counts':[manifest['packs'][manifest[k]]['count'] for k in ['default_preview_pack','default_debug_pack']],'rebuild_output':str(output) if a.output else None,'all_runtime_RGBA_and_header_bytes_exact':True},indent=2))
