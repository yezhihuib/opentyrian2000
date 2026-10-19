#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
cd "$(dirname "$0")/.."
if [[ $# != 1 ]]; then echo "Usage: $0 ORIGINAL_DATA_DIR" >&2; exit 2; fi
binary=$(mktemp /tmp/hd-cursor-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
(ulimit -v 1048576; ${CC:-cc} -std=c99 -O1 -g -Wall -Wextra -Werror -Wno-misleading-indentation \
 ${SANITIZER_FLAGS:-} ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc \
 -DHD_CURSOR_FAULT_TEST tests/hd_cursor_test.c src/hd_cursor.c \
 -Wl,--wrap=SDL_CreateTexture -Wl,--wrap=SDL_SetTextureBlendMode -Wl,--wrap=SDL_SetTextureScaleMode \
 -Wl,--wrap=SDL_UpdateTexture -Wl,--wrap=SDL_RenderCopyF \
 ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$binary")
(ulimit -v 524288; SDL_VIDEODRIVER=dummy "$binary" "$1/newsh1.shp")
