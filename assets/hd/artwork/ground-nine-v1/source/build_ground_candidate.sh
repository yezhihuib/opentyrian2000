#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$HERE/work" "$HERE/output"
/usr/bin/python3 "$HERE/source/periodize_fill.py" "$HERE/output-raw/shapesz-id109-8x-candidate.png" "$HERE/work/109-periodic.png"
for id in 99 100 106 107 109 110 118 119 120; do
 src="$HERE/output-raw/shapesz-id$id-8x-candidate.png"
 if [ "$id" = 109 ]; then src="$HERE/work/109-periodic.png"; fi
 magick "$src" -depth 8 "RGBA:$HERE/work/$id.rgba"
done
: "${TYRIAN_HD_BASE_PACK:?Set TYRIAN_HD_BASE_PACK to the existing accepted HD pack containing frozen101.}"
python3 "$HERE/source/read_frozen101.py" "$TYRIAN_HD_BASE_PACK" "$HERE/work/101.rgba"
g++ -std=c++17 -O2 "$HERE/source/register_ground_edges.cpp" -o "$HERE/work/register_ground_edges"
"$HERE/work/register_ground_edges" "$HERE/work" "$HERE/source/registered-edge-pairs.txt"
for id in 99 100 106 107 109 110 118 119 120; do magick -size 192x224 -depth 8 "RGBA:$HERE/work/$id-registered.rgba" -define png:exclude-chunks=date,time "PNG32:$HERE/output/terrain-shapesz-$id-8.png"; done
