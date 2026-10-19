#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
cd "$(dirname "$0")/.."
if [[ $# != 3 ]]; then echo "Usage: $0 ORIGINAL_DATA_DIR DATA_TEXT_RESOURCE_DIR NEW_CAPTURE_DIRECTORY" >&2; exit 2; fi
mkdir "$3"
binary=$(mktemp /tmp/data-text-test.XXXXXX)
trap 'rm -f "$binary"' EXIT
(ulimit -v 1048576; ${CC:-cc} -std=c99 -O1 -g -Wall -Wextra -Werror -Wno-misleading-indentation \
 ${SANITIZER_FLAGS:-} ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc src/hd_cursor.c tests/data_text_test.c \
 ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$binary")
(ulimit -v 524288; SDL_VIDEODRIVER=dummy "$binary" "$1" "$2" "$3")

config_binary=$(mktemp /tmp/data-text-config-test.XXXXXX)
trap 'rm -f "$binary" "$config_binary"' EXIT
(ulimit -v 1048576; ${CC:-cc} -std=c99 -D_POSIX_C_SOURCE=200809L -DTARGET_UNIX -DTYRIAN_DIR='"."' -O1 -g \
 -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wno-misleading-indentation \
 ${SANITIZER_FLAGS:-} ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Isrc src/hd_cursor.c tests/data_text_config_test.c \
 src/config.c src/config_file.c src/file.c src/data_text.c -Wl,--gc-sections \
 ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$config_binary")
profile=$(realpath "$3")/config-test
mkdir -p "$profile/opentyrian2000"
export XDG_CONFIG_HOME="$profile"
(ulimit -v 524288; "$config_binary" default)
printf 'ordinary cfg sentinel' > "$profile/opentyrian2000/tyrian.cfg"
printf 'ordinary save sentinel' > "$profile/opentyrian2000/tyrian.sav"
cat > "$profile/opentyrian2000/opentyrian.cfg" <<'CONFIG'
section 'data'
 item 'language' 'en'
section 'video'
 item 'fullscreen' '2'
 item 'scaler' '4x'
 item 'scaling_mode' 'Integer'
section 'keyboard'
 item 'up' 'W'
section 'mouse'
 item 'left mouse' 'fire right sidekick'
section 'unrelated'
 item 'preserve' 'sentinel'
CONFIG
for stage in zh read-zh read-en; do (ulimit -v 524288; "$config_binary" "$stage"); done
sed -i "s/'language' 'en'/'language' 'zh-TW'/" "$profile/opentyrian2000/opentyrian.cfg"
(ulimit -v 524288; "$config_binary" invalid)
test "$(cat "$profile/opentyrian2000/tyrian.cfg")" = 'ordinary cfg sentinel'
test "$(cat "$profile/opentyrian2000/tyrian.sav")" = 'ordinary save sentinel'
