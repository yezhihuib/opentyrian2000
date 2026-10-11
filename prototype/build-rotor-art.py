"""Rebuild selected physical rotor phases outside the checkout (Blender4.3.2/Pillow)."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--blender',default='blender');a=p.parse_args()
repo=Path(__file__).resolve().parents[1];src=repo/'assets/hd/artwork/enemy-rotor-type5-11-v1';out=a.output.resolve();assert not out.exists();assert repo not in out.parents
shutil.copytree(src,out);(out/'frames8x').mkdir();subprocess.run([a.blender,'-b','-t','4','-P',str(out/'build_rotor.py')],check=True);subprocess.run([sys.executable,str(out/'assemble_frames.py')],check=True)
for e in json.loads((src/'selected-manifest.json').read_text()):
 f=out/f"frames8x/newsh2-base-{e['base']}-192x224.png";actual=Image.open(f);expected=Image.open(repo/e['source_png']);assert actual.mode=='RGBA' and actual.size==(192,224);assert actual.tobytes()==expected.tobytes(),f
 assert hashlib.sha256(f.read_bytes()).hexdigest()==e['source_png_sha256'],f
print('Verified all8 selected phase PNG/RGBA bytes exactly; no original game data required.')
