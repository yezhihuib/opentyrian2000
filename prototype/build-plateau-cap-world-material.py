#!/usr/bin/env python3
"""Reproduce the additive cap sidecar without modifying HDA or lower bundles."""
from pathlib import Path
import argparse,json,subprocess,sys
from plateau_cap_bundle import build_bundle,render_header,FILENAME
repo=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--package',type=Path,default=repo/'assets/hd/artwork/plateau-cap-atlas-v1')
p.add_argument('--selected-pack',type=Path,required=True)
g=p.add_mutually_exclusive_group(required=True)
g.add_argument('--output',type=Path,help='fresh external directory')
g.add_argument('--verify',action='store_true',help='verify generated header and selected-pack sidecar')
p.add_argument('--rebuild-art',action='store_true',help='also invoke frozen authored-source rebuilder; requires --output')
a=p.parse_args()
if a.rebuild_art and not a.output:p.error('--rebuild-art requires --output')
blob,records,receipt=build_bundle(a.package,a.selected_pack)
header=render_header(records,receipt)
if a.output:
    raw=a.output.absolute();out=raw.resolve()
    protected=[repo,a.package.resolve(),a.selected_pack.resolve()]
    if any(x.is_symlink() for x in [raw,*raw.parents]) or out.exists() or any(out==x or x in out.parents or out in x.parents for x in protected):p.error('output must be new, outside all inputs, and without symlink components')
    out.mkdir(parents=True)
    if a.rebuild_art:subprocess.run([sys.executable,str(a.package/'rebuild.py'),'--out',str(out/'authored-source')],check=True)
    (out/FILENAME).write_bytes(blob)
    (out/'plateau_cap_bundle_index.h').write_text(header)
    (out/'bundle-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
else:
    if (a.selected_pack/FILENAME).read_bytes()!=blob:raise SystemExit('Selected cap sidecar mismatch')
    if (repo/'src/plateau_cap_bundle_index.h').read_text()!=header:raise SystemExit('Generated cap C index mismatch')
print(json.dumps({'status':'passed',**receipt},indent=2))
