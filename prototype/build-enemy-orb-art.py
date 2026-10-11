"""Reproduce the two selected enemy-only energy orb PNGs outside the checkout."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];src=repo/'assets/hd/artwork/enemy-orb112-113-v1';out=a.output.resolve();assert not out.exists() and repo not in out.parents
shutil.copytree(src,out);subprocess.run([sys.executable,str(out/'extract_final.py')],check=True)
for e in json.loads((src/'selected-manifest.json').read_text()):
 b=(out/f"frames8x/bank8-id{e['id']}-96x112.png").read_bytes();assert hashlib.sha256(b).hexdigest()==e['source_png_sha256'];assert b==(repo/e['source_png']).read_bytes()
print('Verified both enemy-only orb PNG bytes exactly.')
