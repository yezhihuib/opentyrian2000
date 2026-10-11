"""Rebuild the selected opaque physical installation components outside the checkout."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];src=repo/'assets/hd/artwork/installation125-128-v1';out=a.output.resolve();assert not out.exists() and repo not in out.parents
shutil.copytree(src,out);subprocess.run([sys.executable,str(out/'export_final.py')],check=True)
for e in json.loads((src/'selected-manifest.json').read_text()):
 f=out/f"components8x/newsh2-base-{e['base']}-192x224.png";im=Image.open(f);assert im.mode=='RGBA' and im.size==(192,224) and im.getchannel('A').getextrema()==(255,255)
 b=f.read_bytes();assert hashlib.sha256(b).hexdigest()==e['source_png_sha256'];assert b==(repo/e['source_png']).read_bytes()
print('Verified four opaque installation component PNG bytes exactly; no original game data required.')
