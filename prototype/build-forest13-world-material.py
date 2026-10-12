#!/usr/bin/env python3
"""Build the finite forest bundle in a fresh directory, or verify selected files."""
from pathlib import Path
import argparse,json,subprocess,sys
from forest13_bundle import build_bundle,render_header,FILENAME,POLICY,sha
repo=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--package',type=Path,default=repo/'assets/hd/artwork/forest13-world-canopy-v1')
g=p.add_mutually_exclusive_group(required=True)
g.add_argument('--output',type=Path)
g.add_argument('--verify-pack',type=Path)
p.add_argument('--rebuild-art',action='store_true')
a=p.parse_args()
if a.rebuild_art and not a.output:p.error('--rebuild-art requires --output')
blob,records,receipt=build_bundle(a.package);header=render_header(records,receipt)
if a.output:
    raw=a.output.absolute();out=raw.resolve();protected=[repo,a.package.resolve()]
    if any(x.is_symlink() for x in [raw,*raw.parents]) or out.exists() or any(out==x or x in out.parents or out in x.parents for x in protected):p.error('Choose a fresh external directory without symlink components')
    out.mkdir(parents=True)
    if a.rebuild_art:subprocess.run([sys.executable,str(a.package/'rebuild.py'),'--output-dir',str(out/'authored-source')],check=True)
    (out/FILENAME).write_bytes(blob);(out/'forest13.policy').write_bytes(POLICY)
    (out/'forest13_bundle_index.h').write_text(header)
    (out/'bundle-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
else:
    policy=a.verify_pack/'forest13.policy'
    if policy.is_symlink() or not policy.is_file():raise SystemExit('Selected forest declaration must be a regular file')
    if (a.verify_pack/FILENAME).read_bytes()!=blob or (a.verify_pack/'forest13.policy').read_bytes()!=POLICY:raise SystemExit('Selected forest bundle/policy mismatch')
    for row in receipt['sources']:
        selected=a.verify_pack/f'terrain-shapesz-{row["id"]}-8.hda'
        if sha(selected.read_bytes())!=row['hda_sha256']:raise SystemExit('Selected forest HDA mismatch: '+str(row['id']))
    if (repo/'src/forest13_bundle_index.h').read_text()!=header:raise SystemExit('Generated forest index mismatch')
print(json.dumps({'status':'passed',**receipt},indent=2))
