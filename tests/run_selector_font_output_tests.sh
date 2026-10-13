#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sanitize=()
if [[ ${1:-} == --sanitize ]]; then
  sanitize=(-fsanitize=address,undefined -fno-omit-frame-pointer)
  shift
fi
if [[ $# != 0 ]]; then echo "Usage: $0 [--sanitize]" >&2; exit 2; fi
binary=$(mktemp /tmp/selector-font-output-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
${CC:-cc} -std=c99 -O1 -g -Wall -Wextra -Werror "${sanitize[@]}" \
  $(pkg-config --cflags sdl2) -Isrc tests/selector_font_output_test.c \
  src/video_scale.c src/video_scale_hqNx.c $(pkg-config --libs sdl2) -lm -o "$binary"
"$binary"
