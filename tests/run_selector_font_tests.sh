#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sanitize=()
if [[ ${1:-} == --sanitize ]]; then sanitize=(-fsanitize=address,undefined -fno-omit-frame-pointer); shift; fi
if [[ $# != 2 ]]; then echo "Usage: $0 [--sanitize] ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR" >&2; exit 2; fi
binary=$(mktemp /tmp/selector-font-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
${CC:-cc} -std=c99 -O1 -g -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wno-misleading-indentation "${sanitize[@]}" \
 $(pkg-config --cflags sdl2) -Isrc tests/selector_font_test.c src/selector_font_output.c src/pregame_font.c src/helptext.c tests/load_font_globals.c \
 src/settings_font.c src/load_font.c src/font.c src/sprite.c src/fonthand.c src/video_scale.c src/video_scale_hqNx.c \
 -Wl,--gc-sections $(pkg-config --libs sdl2) -lm -o "$binary"
SDL_VIDEODRIVER=dummy "$binary" "$1" "$2"
