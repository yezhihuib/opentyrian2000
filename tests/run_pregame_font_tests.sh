#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sanitize=()
if [[ ${1:-} == --sanitize ]]; then sanitize=(-fsanitize=address,undefined -fno-omit-frame-pointer); shift; fi
if [[ ${1:-} == --ubsan ]]; then sanitize=(-fsanitize=undefined -fno-sanitize-recover=all -fno-omit-frame-pointer); shift; fi
if [[ $# != 2 && $# != 3 && $# != 4 && $# != 5 && $# != 6 ]]; then echo "Usage: $0 [--sanitize|--ubsan] ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR [SFN1_WITH_METAL_DIR [SFN1_WITH_SPRITE_DIR [SFN1_WITH_EQUIPMENT_DIR [SFN1_WITH_GENERATOR_DIR]]]]" >&2; exit 2; fi
binary=$(mktemp /tmp/pregame-font-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
${CC:-cc} -std=c99 -O1 -g -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wno-misleading-indentation "${sanitize[@]}" \
 ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc src/hd_cursor.c tests/pregame_font_test.c src/selector_font_output.c \
 src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c \
 src/font.c src/sprite.c src/data_text.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c \
 -Wl,--gc-sections ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$binary"
if [[ -n ${PREGAME_TEST_MAX_KIB:-} ]]; then
 (ulimit -v "$PREGAME_TEST_MAX_KIB"; SDL_VIDEODRIVER=dummy "$binary" "$@")
else
 SDL_VIDEODRIVER=dummy "$binary" "$@"
fi
