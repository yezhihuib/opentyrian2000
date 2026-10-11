#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
bash "$HERE/source/extract_generated_tiles.sh"
bash "$HERE/source/build_ground_candidate.sh"
python3 "$HERE/source/pack_overlay.py"
