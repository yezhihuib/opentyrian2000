#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "$0")/rebuild.py" "${1:?Specify a new external output directory}"
