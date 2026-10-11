#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
: "${TYRIAN_DATA_DIR:?Set TYRIAN_DATA_DIR to the existing legal Tyrian2000 data directory.}"
export TYRIAN_CLOUD_REFERENCE_DIR="$HERE/work-mask-reference"
python3 "$HERE/source/extract_cloud_masks.py" --data "$TYRIAN_DATA_DIR" --out "$TYRIAN_CLOUD_REFERENCE_DIR"
bash "$HERE/source/build_cloud_tiles.sh"
g++ -std=c++17 -O2 "$HERE/source/reconcile_edges.cpp" -o "$HERE/source/reconcile_edges"
for id in 41 42 43 44 45 51 52 53 54 55 61 62 63 64 65; do magick "$HERE/output/terrain-shapesz-$id-8.png" -depth 8 "RGBA:$HERE/source/registered/$id.rgba"; done
"$HERE/source/reconcile_edges" "$HERE/source/registered" "$HERE/source/actual-edge-pairs.txt"
for id in 41 42 43 44 45 51 52 53 54 55 61 62 63 64 65; do magick -size 192x224 -depth 8 "RGBA:$HERE/source/registered/$id-registered.rgba" "PNG32:$HERE/output/terrain-shapesz-$id-8.png"; done
python3 "$HERE/source/pack_overlay.py" --png-dir "$HERE/output" --output "$HERE/runtime-overlay"
