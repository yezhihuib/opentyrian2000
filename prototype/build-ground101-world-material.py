"""Rebuild the authored world atlas and its finite optional runtime sidecar."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from world_material_bundle import build_bundle, render_header

repo = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--output", type=Path, help="new external directory; also rebuilds authored source")
group.add_argument("--verify", action="store_true", help="verify committed sidecars and generated C header")
args = parser.parse_args()

if args.output:
    raw_output = args.output.absolute()
    if any(p.is_symlink() for p in [raw_output, *raw_output.parents]):
        parser.error("Output paths may not contain symlinks")
    output = raw_output.resolve()
    if output.exists() or output == repo or repo in output.parents or output in repo.parents:
        parser.error("Choose a fresh output directory outside the repository and its ancestors")
    output.mkdir(parents=True)
    package = repo / "assets/hd/artwork/ground101-world-atlas-v1"
    subprocess.run([sys.executable, str(package/"rebuild.py"), str(output/"authored-source")], check=True)

blob, records, receipt = build_bundle(repo)
header = render_header(records, receipt)
if args.verify:
    manifest = json.loads((repo/"assets/hd/manifest.json").read_text())
    for pack, expected in manifest["material_bundles"].items():
        if receipt != expected or any((repo/"assets/hd/packs"/pack/part["file"]).read_bytes() != blob[part["offset"]:part["offset"]+part["bytes"]] for part in receipt["parts"]):
            raise SystemExit("Material sidecar mismatch: "+pack)
    if (repo/"src/ground101_bundle_index.h").read_text() != header:
        raise SystemExit("Generated material C header mismatch")
else:
    for part in receipt["parts"]:
        (output/part["file"]).write_bytes(blob[part["offset"]:part["offset"]+part["bytes"]])
    (output/"ground101_bundle_index.h").write_text(header)
    (output/"bundle-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps({"status":"passed","output":str(output) if args.output else None,**receipt},indent=2))
