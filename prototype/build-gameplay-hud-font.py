"""Rebuild frozen HUF1 from vectors into a fresh external directory."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from gameplay_hud_font_bundle import build_bundle, FILENAME, SOURCE

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[1]
given = args.output.absolute()
output = given.resolve()
if (any(p.is_symlink() for p in [given, *given.parents]) or output.exists() or
        output == repo or repo in output.parents or output in repo.parents):
    parser.error('Choose a fresh external directory without symlink path components')
raw, receipt = build_bundle(repo)
source = repo / SOURCE
# Separate fresh outputs; no canonical PNG/alpha/resource is passed to the builder.
subprocess.run([sys.executable, str(source / 'build_resource.py'),
    '--output', str(output / FILENAME), '--proof-output', str(output / 'vector-proof')], check=True)
assert (output / FILENAME).read_bytes() == raw
for name in ('tiny-coverage-atlas-4x.png', 'tiny-coverage-atlas-4x.alpha.bin', 'tiny-vector-atlas.svg'):
    assert (output / 'vector-proof' / name).read_bytes() == (source / 'canonical' / name).read_bytes()
print(json.dumps(receipt, indent=2))
