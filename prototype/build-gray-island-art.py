"""Rebuild the selected gray18 v2 generated source and verify formal runtime inputs."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];source=repo/'assets/hd/artwork/layer3-gray18-v2';out=a.output.resolve();assert not out.exists() and repo not in out.parents
subprocess.run([sys.executable,str(source/'source/rebuild_selected.py'),'--output-root',str(out)],check=True)
m=json.loads((repo/'assets/hd/manifest.json').read_text());pack=m['packs'][m['default_debug_pack']]['files']
for i in m['terrain_layer3_gray18_v2']['ids']:
 name=f'terrain-shapesz-{i}-8.hda';e=pack[name];raw=(out/'runtime-overlay'/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'];png=repo/e['source_png'];assert hashlib.sha256(png.read_bytes()).hexdigest()==e['source_png_sha256'];assert Image.open(png).convert('RGBA').tobytes()==raw[28:]
print('Verified all18 selected formal PNG files, regenerated RGBA and exact HDR1; four PNG encodings may differ as documented.')
