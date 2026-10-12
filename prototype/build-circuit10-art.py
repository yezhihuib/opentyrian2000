"""Rebuild the generated circuit/deck10 package and verify selected runtime bytes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[1];source=repo/'assets/hd/artwork/circuit10-v1';given=a.output.absolute();out=given.resolve()
if any(q.is_symlink()for q in [given,*given.parents]) or out.exists() or out==repo or repo in out.parents or out in repo.parents:p.error('Choose a fresh directory outside the repository, without symlink path components')
subprocess.run([sys.executable,str(source/'rebuild.py'),str(out)],check=True)
m=json.loads((repo/'assets/hd/manifest.json').read_text());pack=m['packs'][m['default_debug_pack']]['files']
for i in m['terrain_layer3_circuit10_v1']['ids']:
 e=pack[f'terrain-shapesz-{i}-8.hda'];raw=(out/f'{2010000+i}.hda').read_bytes();png=repo/e['source_png']
 assert hashlib.sha256(raw).hexdigest()==e['sha256']
 assert hashlib.sha256(png.read_bytes()).hexdigest()==e['source_png_sha256']
 assert Image.open(png).convert('RGBA').tobytes()==raw[28:]
print('Verified all10 canonical PNGs, rebuilt RGBA and exact runtime HDR1 bytes; package numeric names map to canonical runtime names.')
