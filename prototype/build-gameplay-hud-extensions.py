"""Rebuild frozen label/shield and indicator source in a fresh external directory."""
from pathlib import Path
import argparse, subprocess, sys, shutil, json
from gameplay_hud_extension_bundles import build_bundles
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args(); repo=Path(__file__).resolve().parents[1]
given=a.output.absolute();out=given.resolve()
if any(x.is_symlink() for x in [given,*given.parents]) or out.exists() or out==repo or repo in out.parents or out in repo.parents:
    p.error('Choose a fresh external directory without symlink path components')
bundles=build_bundles(repo)
manifest=json.loads((repo/'assets/hd/manifest.json').read_text())['gameplay_hud_extensions_v1']
out.mkdir(parents=True)
for kind, entry in manifest['resources'].items():
    source=repo/entry['source'];target=out/kind
    if kind=='components':
        target.mkdir()
        for name in ('build_assets.py','provenance.json'): shutil.copyfile(source/name,target/name)
        subprocess.run([sys.executable,str(target/'build_assets.py')],check=True)
    else:
        subprocess.run([sys.executable,str(source/'reproduce_generated_only.py'),'--output-dir',str(target)],check=True)
    assert (target/entry['filename']).read_bytes()==bundles[entry['filename']][0]
    for tile in entry['tiles']:
        assert (target/tile['authored']).read_bytes()==(source/tile['authored']).read_bytes()
print(json.dumps({name:receipt for name,(raw,receipt) in bundles.items()},indent=2))
