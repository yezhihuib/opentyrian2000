"""Rebuild the generated low-grass/sand9 source and verify the selected runtime assets."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[1];source=repo/'assets/hd/artwork/grass-sand9-v3';out=a.output.resolve()
if out.exists() or out==repo or repo in out.parents:p.error('Choose a new directory outside the repository')
subprocess.run([sys.executable,str(source/'rebuild.py'),'--output-dir',str(out)],check=True)
m=json.loads((repo/'assets/hd/manifest.json').read_text());pack=m['packs'][m['default_debug_pack']]['files']
for i in m['terrain_grass_sand9_v3']['ids']:
 name=f'terrain-shapesz-{i}-8.hda';e=pack[name];raw=(out/'runtime-overlay'/name).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==e['sha256'];png=repo/e['source_png']
 assert hashlib.sha256(png.read_bytes()).hexdigest()==e['source_png_sha256']
 assert Image.open(png).convert('RGBA').tobytes()==raw[28:]
print('Verified all9 canonical PNGs, regenerated RGBA and exact HDR1 assets.')
