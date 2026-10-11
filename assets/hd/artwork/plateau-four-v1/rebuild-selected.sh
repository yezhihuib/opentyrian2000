#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
: "${TYRIAN_HD_BASE_PACK:?Set to the frozen accepted pack containing ground9 and101}"
python3 "$HERE/source/rebuild_selected.py" --base-pack "$TYRIAN_HD_BASE_PACK" --output-root "${1:?Give a new output directory}"
