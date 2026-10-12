"""Rebuild fixed green labels from vector source in a fresh external directory."""
from pathlib import Path
import argparse,subprocess,sys,json
from gameplay_hud_fixed_text_bundle import build_bundle,FILENAME
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[1];given=a.output.absolute();out=given.resolve()
if any(q.is_symlink()for q in [given,*given.parents]) or out.exists() or out==repo or repo in out.parents or out in repo.parents:p.error('Choose a fresh external directory without symlink path components')
raw,receipt=build_bundle(repo);m=json.loads((repo/'assets/hd/manifest.json').read_text())['gameplay_hud_fixed_text_v1'];source=repo/m['source']
subprocess.run([sys.executable,str(source/'build_assets.py'),'--output',str(out)],check=True)
assert (out/FILENAME).read_bytes()==raw
for t in m['tiles']:assert (out/t['authored']).read_bytes()==(source/t['authored']).read_bytes()
print(json.dumps(receipt,indent=2))
