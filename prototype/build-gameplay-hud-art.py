"""Rebuild immutable component HUD source into a fresh external directory."""
from pathlib import Path
import argparse,subprocess,sys,hashlib
from gameplay_hud_bundle import build_bundle,FILENAME
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[1];given=a.output.absolute();out=given.resolve()
if any(q.is_symlink()for q in [given,*given.parents]) or out.exists() or out==repo or repo in out.parents or out in repo.parents:p.error('Choose a fresh external directory without symlink path components')
raw,receipt=build_bundle(repo)
subprocess.run([sys.executable,str(repo/'assets/hd/artwork/gameplay-hud-v5/export_frozen.py'),'--output',str(out)],check=True)
assert (out/FILENAME).read_bytes()==raw
print('Verified component source rebuild and exact HUD1 bytes:',receipt)
