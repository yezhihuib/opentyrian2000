#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sanitize=()
if [[ ${1:-} == --ubsan ]]; then sanitize=(-fsanitize=undefined -fno-sanitize-recover=all -fno-omit-frame-pointer); shift; fi
if [[ $# != 2 ]]; then echo "Usage: $0 [--ubsan] ORIGINAL_DATA_DIR SFN1_METAL_TALON_MENU_DIR" >&2; exit 2; fi
binary=$(mktemp /tmp/shop-menu-font-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
${CC:-cc} -std=c99 -O1 -g -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wno-misleading-indentation "${sanitize[@]}" \
 ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc tests/shop_menu_font_test.c src/selector_font_output.c \
 src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c \
 src/font.c src/sprite.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c \
 -Wl,--gc-sections ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$binary"
(ulimit -v "${PREGAME_TEST_MAX_KIB:-524288}"; SDL_VIDEODRIVER=dummy "$binary" "$@")
