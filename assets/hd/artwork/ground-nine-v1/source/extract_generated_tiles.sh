#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$HERE/work" "$HERE/output-raw"
magick "$HERE/source/imagegen-main-plateau-v1.png" -filter Lanczos -resize 1920x1344\! "$HERE/work/main-registered.png"
magick "$HERE/source/imagegen-diagonal-v1.png" -filter Lanczos -resize 576x672\! "$HERE/work/diagonal-registered.png"
while read -r id kind x y; do
 magick "$HERE/work/$kind-registered.png" -crop 192x224+$x+$y +repage -depth 8 -define png:exclude-chunks=date,time "PNG32:$HERE/output-raw/shapesz-id$id-8x-candidate.png"
done <<'CROPS'
99 main 960 0
100 main 1536 0
106 main 192 672
107 diagonal 192 224
109 main 768 448
110 main 1536 448
118 main 192 896
119 main 960 896
120 main 1536 896
CROPS
