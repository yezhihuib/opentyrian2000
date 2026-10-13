#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sanitize=()
if [[ ${1:-} == --sanitize ]]; then
  sanitize=(-fsanitize=address,undefined -fno-omit-frame-pointer)
  shift
fi
if [[ $# != 2 ]]; then echo "Usage: $0 [--sanitize] ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR" >&2; exit 2; fi
binary=$(mktemp /tmp/settings-font-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
${CC:-cc} -std=c99 -O1 -g -ffunction-sections -fdata-sections \
  -Wall -Wextra -Werror -Wno-misleading-indentation "${sanitize[@]}" \
  $(pkg-config --cflags sdl2) -Isrc tests/settings_font_test.c \
  src/fonthand.c src/font.c src/sprite.c src/nortvars.c src/vga256d.c \
  -Wl,--gc-sections $(pkg-config --libs sdl2) -o "$binary"
"$binary" "$1" "$2"
