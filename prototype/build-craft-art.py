"""Rebuild calibrated static craft17/24/25 from the authored atlas, without original game data."""
from pathlib import Path
import argparse,hashlib,json,shutil,struct,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];src=repo/'assets/hd/artwork/enemy-craft17-24-25-v1';out=a.output.resolve();assert not out.exists() and repo not in out.parents
shutil.copytree(src,out);subprocess.run([sys.executable,str(out/'export_final.py')],check=True);records=json.loads((src/'selected-manifest.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for e in records:
 f=out/'frames8x'/f"newsh2-base-{e['base']}-192x224.png";im=Image.open(f);assert im.mode=='RGBA' and im.size==(192,224);assert sha(f.read_bytes())==e['source_png_sha256'];assert f.read_bytes()==(repo/e['source_png']).read_bytes();raw=b'HDR1'+struct.pack('<6I',*e['header_u32'])+im.tobytes();assert sha(raw)==e['sha256']
print('Verified all three calibrated PNGs, RGBA and HDR1 bytes; no original game data used.')
