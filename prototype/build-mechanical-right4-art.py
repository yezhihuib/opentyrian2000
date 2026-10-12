"""Rebuild and verify the finite generated Layer3 right-mechanical family."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
repo=Path(__file__).resolve().parents[1]
source=repo/'assets/hd/artwork/mechanical-right4-v1'
given=a.output.absolute();out=given.resolve()
if any(q.is_symlink() for q in [given,*given.parents]) or out.exists() or out==repo or repo in out.parents or out in repo.parents:
 p.error('Choose a fresh directory outside the repository, without symlink path components')
manifest=json.loads((repo/'assets/hd/manifest.json').read_text())
family=manifest['terrain_layer3_mechanical_right4_v1']
sha=lambda b:hashlib.sha256(b).hexdigest()
assert family['ids']==[188,189,198,199] and family['slots']==[359,360,361,362]
assert sha((source/'inventory.json').read_bytes())==family['source_inventory_sha256']
subprocess.run([sys.executable,str(source/'rebuild.py'),str(out)],check=True)
for key in ('default_preview_pack','default_debug_pack'):
 pack=manifest['packs'][manifest[key]]['files']
 for i in family['ids']:
  e=pack[f'terrain-shapesz-{i}-8.hda'];raw=(out/f'{2010000+i}.hda').read_bytes();png=repo/e['source_png']
  assert sha(raw)==e['sha256'] and sha(png.read_bytes())==e['source_png_sha256']
  assert Image.open(png).convert('RGBA').tobytes()==raw[28:]
print('Verified all four canonical PNGs and exact rebuilt RGBA/HDR1 bytes in both selected packs.')
