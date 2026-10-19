#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
cd "$(dirname "$0")/.."
sanitize=()
if [[ ${1:-} == --ubsan ]]; then sanitize=(-fsanitize=undefined -fno-sanitize-recover=all -fno-omit-frame-pointer); shift; fi
if [[ $# != 2 ]]; then echo "Usage: $0 [--ubsan] ORIGINAL_DATA_DIR SFN1_RESOURCE_DIR" >&2; exit 2; fi
original=$(realpath "$1")
fonts=$(realpath "$2")
work=$(mktemp -d /tmp/shop-shield-test.XXXXXX)
trap 'rm -rf -- "$work"' EXIT
mkdir "$work/resources"
for size in large medium tiny; do ln -s "$fonts/settings-font-$size-v1.hda" "$work/resources/"; done
for item in shop-frame-v1/shop-frame-metal-v1.hda shop-talon-v1/shop-talon-option31-v1.hda shop-front-v1/shop-front-weapon00-v1.hda shop-generator-v1/shop-generator-weapon16-v1.hda shop-shield-v1/shop-shield-option26-v1.hda; do
 test -f "assets/$item"
 ln -s "$PWD/assets/$item" "$work/resources/"
done
for run in {0..6}; do ln -s "$PWD/assets/shop-menu-font-v1/shop-menu-run$run-v1.hda" "$work/resources/"; done
(
 ulimit -v 1048576
 ${CC:-cc} -std=c99 -O1 -g -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wno-misleading-indentation "${sanitize[@]}" \
  ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc src/hd_cursor.c tests/shop_shield_test.c src/selector_font_output.c \
  src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c \
  src/font.c src/sprite.c src/data_text.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c \
  -Wl,--gc-sections ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$work/test"
)
(ulimit -v 524288; SDL_VIDEODRIVER=dummy "$work/test" "$original" "$work/resources")
