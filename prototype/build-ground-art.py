"""Rebuild the bounded nine-tile plateau outside the checkout, using frozen HD101."""
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];src=repo/'assets/hd/artwork/ground-nine-v1';out=a.output.resolve();assert not out.exists() and repo not in out.parents
shutil.copytree(src,out);m=json.loads((repo/'assets/hd/manifest.json').read_text());env=dict(os.environ,TYRIAN_HD_BASE_PACK=str(repo/'assets/hd/packs'/m['default_debug_pack']));subprocess.run(['bash',str(out/'rebuild-selected.sh')],check=True,env=env)
for e in json.loads((src/'selected-manifest.json').read_text())['assets']:
 name=f"terrain-shapesz-{e['id']}-8.hda";assert hashlib.sha256((out/'runtime-overlay'/name).read_bytes()).hexdigest()==e['hda_sha256'];assert Image.open(out/'output'/e['png']).tobytes()==Image.open(repo/e['source_png']).tobytes();assert hashlib.sha256((repo/e['source_png']).read_bytes()).hexdigest()==e['png_sha256']
print('Verified all9 HDA and decodedRGBA bytes; committed PNG hashes verified separately.')
