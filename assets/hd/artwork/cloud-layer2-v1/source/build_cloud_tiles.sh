#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
REF="${TYRIAN_CLOUD_REFERENCE_DIR:-$HERE/../scene-analysis/original-tiles}"
mkdir -p "$HERE/output" "$HERE/source/registered" "$HERE/runtime"
magick "$HERE/source/imagegen-atlas-v1.png" -filter Lanczos -resize 960x672\! "$HERE/source/atlas-8x.png"
magick "$HERE/source/atlas-8x.png" -crop 192x224+576+224 +repage "$HERE/source/core54.png"
/usr/bin/python3 "$HERE/source/periodize_gegl.py"
# Native ImageMagick registration mask. Forty HD pixels = five logical
# pixels; matching periodic RGB is confined to boundary neighborhoods. Distinct
# source interiors survive at full opacity away from crop boundaries.
magick -size 192x224 xc:black -fx 'blend=min(min(i,191-i),min(j,223-j))/40; blend=min(1,blend); blend*blend*(3-2*blend)' "$HERE/source/interior-weight.png"
IDS=(41 42 43 44 45 51 52 53 54 55 61 62 63 64 65)
for n in "${!IDS[@]}"; do
 id=${IDS[$n]}; x=$((n%5*192)); y=$((n/5*224)); r="$HERE/source/registered/$id"
 magick "$HERE/source/atlas-8x.png" -crop 192x224+$x+$y +repage "$r-generated.png"
 # Original binary mask is geometry evidence only. Cubic reconstruction and a
 # sub-logical-pixel feather remove low-res stairs without carving rock facets.
 magick "$REF/shapesz-$id-rgba.png" -alpha extract -filter Cubic -resize 192x224\! -blur 0x2.2 -level 1%,99% "$r-alpha.png"
 magick "$r-generated.png" -alpha extract "$HERE/source/interior-weight.png" -compose Multiply -composite "$r-weight.png"
 magick "$r-generated.png" "$r-weight.png" -alpha off -compose CopyOpacity -composite "$r-interior.png"
 magick "$HERE/source/core-periodic.png" "$r-interior.png" -compose Over -composite "$r-rgb.png"
 magick "$r-rgb.png" "$r-alpha.png" -alpha off -compose CopyOpacity -composite -depth 8 "PNG32:$HERE/output/terrain-shapesz-$id-8.png"
done
