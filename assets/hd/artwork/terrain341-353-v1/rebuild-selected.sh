#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/source/rebuild_selected.py" --output-root "${1:?Specify a new output directory}"
