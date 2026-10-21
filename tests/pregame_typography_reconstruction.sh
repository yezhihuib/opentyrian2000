#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -f ../recovery-build-deps-20261020/env.sh ]]; then source ../recovery-build-deps-20261020/env.sh; fi
out=${TYRIAN_TEST_OUTPUT:-build/pregame-typography-tests}
export TYRIAN_TEST_OUTPUT="$out"
mkdir -p "$out"
sanitize=()
optimization=-O1
if [[ ${1:-} == --sanitize ]]; then sanitize=(-fsanitize=address,undefined -fno-omit-frame-pointer);optimization=-O0;export ASAN_OPTIONS=detect_leaks=0;shift;fi
cc -std=c99 "$optimization" -g -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wno-misleading-indentation "${sanitize[@]}" \
 $(pkg-config --cflags sdl2) -Isrc src/hd_cursor.c tests/pregame_typography_reconstruction.c src/common_menu_runs.c src/selector_font_output.c \
 src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c \
 src/font.c src/sprite.c src/data_text.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c \
 -Wl,--gc-sections $(pkg-config --libs sdl2) -lm -o "$out/pregame-typography-test"
SDL_VIDEODRIVER=dummy "$out/pregame-typography-test" "$@" | tee "$out/latest-test.log"
