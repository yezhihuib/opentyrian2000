"""Rebuild terrain113 and the complete six-tile stone foundation without original game data."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];out=a.output.resolve();assert not out.exists() and repo not in out.parents
for family in ['terrain113-v1','terrain341-353-v1']:
 src=repo/'assets/hd/artwork'/family;dst=out/family;shutil.copytree(src,dst/'source-package')
 (dst/'source-package/output').mkdir()
 for e in json.loads((src/'selected-manifest.json').read_text()):
  committed=repo/e['source_png'];assert hashlib.sha256(committed.read_bytes()).hexdigest()==e['source_png_sha256'];shutil.copy2(committed,dst/'source-package/output'/f"terrain-shapesz-{e['id']}-8.png")
 subprocess.run(['bash',str(dst/'source-package/rebuild-selected.sh'),str(dst/'rebuilt')],check=True)
 for e in json.loads((src/'selected-manifest.json').read_text()):
  name=f"terrain-shapesz-{e['id']}-8";raw=(dst/'rebuilt/runtime-overlay'/f'{name}.hda').read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'];assert Image.open(dst/'rebuilt/output'/f'{name}.png').tobytes()==Image.open(repo/e['source_png']).tobytes();assert hashlib.sha256((repo/e['source_png']).read_bytes()).hexdigest()==e['source_png_sha256']
print('Verified all seven HDA/RGBA bytes and committed PNG hashes; no original game data or base checkout required.')
