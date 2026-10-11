"""Reproduce four plateau edge assets from generated-only crops and checked frozen HD neighbors."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];art=repo/'assets/hd/artwork/plateau-four-v1';out=a.output.resolve();assert not out.exists() and repo not in out.parents;m=json.loads((repo/'assets/hd/manifest.json').read_text());pack=repo/'assets/hd/packs'/m['default_debug_pack']
subprocess.run([sys.executable,str(art/'source/rebuild_selected.py'),'--base-pack',str(pack),'--output-root',str(out)],check=True)
for e in json.loads((art/'selected-manifest.json').read_text()):
 p=out/'output'/f"terrain-shapesz-{e['id']}-8.png";assert hashlib.sha256(p.read_bytes()).hexdigest()==e['png_sha256'];assert Image.open(p).tobytes()==Image.open(repo/e['source_png']).tobytes();assert hashlib.sha256((out/'runtime-overlay'/f"terrain-shapesz-{e['id']}-8.hda").read_bytes()).hexdigest()==e['hda_sha256']
print('Verified all4 PNG/RGBA/HDA bytes exactly; frozen neighbor hashes checked.')
