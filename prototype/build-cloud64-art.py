"""Rebuild the cloud64 lower-edge correction from generated-only bundled inputs."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];out=a.output.resolve();assert not out.exists() and repo not in out.parents
subprocess.run([sys.executable,str(repo/'assets/hd/artwork/cloud64-v3/rebuild.py'),'--output-dir',str(out)],check=True)
m=json.loads((repo/'assets/hd/manifest.json').read_text());e=m['packs'][m['default_debug_pack']]['files']['terrain-shapesz-64-8.hda'];raw=(out/'runtime-overlay/terrain-shapesz-64-8.hda').read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'];png=repo/e['source_png'];assert hashlib.sha256(png.read_bytes()).hexdigest()==e['source_png_sha256'];assert Image.open(png).convert('RGBA').tobytes()==raw[28:]
print('PASS: selected cloud64 canonical PNG hash and generated RGBA/HDR1 exact; PNG encoding may differ.')
