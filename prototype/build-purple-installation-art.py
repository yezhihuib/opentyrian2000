"""Rebuild nine independent purple installation components from the authored atlas, without original game data."""
from pathlib import Path
import argparse,hashlib,json,shutil,struct,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];src=repo/'assets/hd/artwork/purple-installation32-41-v2';out=a.output.resolve();assert not out.exists() and repo not in out.parents
shutil.copytree(src,out);subprocess.run([sys.executable,str(out/'export_final.py')],check=True);records=json.loads((src/'selected-manifest.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
for e in records:
 f=out/'frames8x'/f"newsh2-base{e['id']}-8.png";im=Image.open(f);assert im.mode=='RGBA' and im.size==(192,224);assert sha(f.read_bytes())==e['source_png_sha256'];assert f.read_bytes()==(repo/e['source_png']).read_bytes();raw=b'HDR1'+struct.pack('<6I',*e['header_u32'])+im.tobytes();assert sha(raw)==e['sha256']
print('Verified all nine purple installation PNGs, RGBA and HDR1 bytes; no original game data used.')
