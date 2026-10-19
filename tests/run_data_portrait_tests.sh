#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
cd "$(dirname "$0")/.."
if [[ $# != 4 ]]; then echo "Usage: $0 ORIGINAL_DATA_DIR PORTRAIT_RESOURCE_DIR FRAME_RESOURCE_DIR NEW_FIXTURE_DIRECTORY" >&2; exit 2; fi
data=$(realpath "$1"); art=$(realpath "$2"); frame=$(realpath "$3")
mkdir "$4"
binary=$(mktemp /tmp/data-portrait-test.XXXXXX)
(ulimit -v 524288; ${CC:-cc} -std=c99 -O1 -g -Wall -Wextra -Werror -Wno-misleading-indentation \
 ${SANITIZER_FLAGS:-} ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc src/hd_cursor.c tests/data_portrait_test.c src/data_frame.c \
 ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$binary")
(ulimit -v 524288; SDL_VIDEODRIVER=dummy "$binary" "$data" "$art" "$frame" "$4")
