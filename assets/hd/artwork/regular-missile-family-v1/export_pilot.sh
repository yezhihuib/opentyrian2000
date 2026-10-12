#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Whole-object crops enclose all alpha >=2 plus a 2px margin.
# Remote generated alpha=1 background speckles are outside these rectangles.
# No silhouette/alpha repaint, palette edit, sharpening or per-part transforms.
magick -size 96x112 xc:none \( sources/missile-31-generated-v1.png -crop 327x1085+417+114 +repage -filter Lanczos -resize '56x104!' \) -geometry +24+8 -composite -strip PNG32:frames/bank8-id31-96x112.png
magick -size 96x112 xc:none \( sources/missile-32-generated-v1.png -crop 587x1298+210+72 +repage -filter Lanczos -resize '72x112!' \) -geometry +16+0 -composite -strip PNG32:frames/bank8-id32-96x112.png
magick -size 96x112 xc:none \( sources/missile-33-generated-v1.png -crop 785x1500+91+17 +repage -filter Lanczos -resize '72x112!' \) -geometry +8+0 -composite -strip PNG32:frames/bank8-id33-96x112.png
