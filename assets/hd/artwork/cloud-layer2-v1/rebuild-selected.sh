#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
bash "$HERE/rebuild-base-selected.sh"
mkdir -p "$HERE/work-v1-output"
for id in 41 42 43 44 45 51 52 53 54 55 61 62 63 64 65; do cp "$HERE/output/terrain-shapesz-$id-8.png" "$HERE/work-v1-output/"; done
TYRIAN_CLOUD_V1_PNG_DIR="$HERE/work-v1-output" bash "$HERE/source/apply_edge_revision.sh"
