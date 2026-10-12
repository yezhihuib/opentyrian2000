"""Rebuild the four generated guided-bomb/shared-fragment assets in a new directory."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
r=Path(__file__).resolve().parents[1];art=r/'assets/hd/artwork/guided-bomb-family-v1'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if a.output.is_symlink() or out.exists() or out==r or r in out.parents:p.error('Choose a new directory outside the repository')
shutil.copytree(art,out);subprocess.run([sys.executable,str(out/'export_final.py')],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((art/'candidate-manifest.json').read_text())
for f in m['frames']:
 assert sha(out/f['source_png'])==f['source_png_sha256']
 assert sha(out/f['hda'])==f['hda_sha256']
print('PASS: Four guided PNG/HDA outputs byte-exact; all prior assets unchanged')
