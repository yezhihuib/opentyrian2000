#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
BASE=${TYRIAN_CLOUD_V1_PNG_DIR:-$HERE/../cloud-v1/output}
mkdir -p "$HERE/output" "$HERE/work"
for id in 41 42 43 44 45 51 52 53 54 55 61 62 63 64 65; do cp "$BASE/terrain-shapesz-$id-8.png" "$HERE/output/terrain-shapesz-$id-8.png"; done
magick "$HERE/source/imagegen-edge-context-v2.png" -filter Lanczos -resize 576x672\! -crop 192x224+384+224 +repage -depth 8 "RGBA:$HERE/work/55-generated.rgba"
magick "$BASE/terrain-shapesz-55-8.png" -depth 8 "RGBA:$HERE/work/55-v1.rgba"
g++ -std=c++17 -O2 "$HERE/source/register_edge.cpp" -o "$HERE/work/register_edge"
"$HERE/work/register_edge" "$HERE/work/55-v1.rgba" "$HERE/work/55-generated.rgba" "$HERE/work/55-v2.rgba"
magick -size 192x224 -depth 8 "RGBA:$HERE/work/55-v2.rgba" -define png:exclude-chunks=date,time "PNG32:$HERE/output/terrain-shapesz-55-8.png"
python3 "$HERE/source/pack_overlay.py" --png-dir "$HERE/output" --output "$HERE/runtime-overlay"
