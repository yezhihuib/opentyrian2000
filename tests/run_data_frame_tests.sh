#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
cd "$(dirname "$0")/.."
if [[ $# != 3 ]]; then echo "Usage: $0 ORIGINAL_DATA_DIR DATA_FRAME_RESOURCE_DIR NEW_FIXTURE_DIRECTORY" >&2; exit 2; fi
mkdir "$3"
binary=$(mktemp /tmp/data-frame-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
(ulimit -v 1048576; ${CC:-cc} -std=c99 -O1 -g -Wall -Wextra -Werror -Wno-misleading-indentation \
 ${SANITIZER_FLAGS:-} ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc src/hd_cursor.c tests/data_frame_test.c \
 ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$binary")
(ulimit -v 524288; SDL_VIDEODRIVER=dummy "$binary" "$1" "$2" "$3")
