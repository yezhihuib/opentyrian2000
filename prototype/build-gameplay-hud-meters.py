"""Rebuild frozen HUM2 materials into a fresh external directory."""
from pathlib import Path
import argparse,json,subprocess,sys
from gameplay_hud_meter_bundle import build_bundle,FILENAME,SOURCE
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
repo=Path(__file__).resolve().parents[1];given=a.output.absolute();out=given.resolve()
if any(q.is_symlink()for q in [given,*given.parents]) or out.exists() or out==repo or repo in out.parents or out in repo.parents:
 p.error('Choose a fresh external directory without symlink path components')
raw,receipt=build_bundle(repo);source=repo/SOURCE
subprocess.run([sys.executable,str(source/'build_resource.py'),'--output',str(out)],check=True)
assert(out/FILENAME).read_bytes()==raw
assert(out/'meter-scope-1390.mask').read_bytes()==(source/'canonical/meter-scope-1390.mask').read_bytes()
print(json.dumps(receipt,indent=2))
