#!/usr/bin/env bash
set -euo pipefail
: "${TYRIAN_HD_BASE_PACK:?Set TYRIAN_HD_BASE_PACK to the accepted road-aware pack}"
python3 "$(dirname "$0")/source/rebuild_selected.py" --base-pack "$TYRIAN_HD_BASE_PACK" --output-root "${1:?Specify a new output directory}"
