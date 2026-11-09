#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
binary=$(mktemp /tmp/hd-gameplay-scaling.XXXXXX)
trap 'rm -f "$binary"' EXIT
${CC:-cc} -std=c99 -O1 -g -Wall -Wextra -Werror -pedantic \
  ${SANITIZER_FLAGS:-} \
  ${SDL_CFLAGS:-$(pkg-config --cflags sdl2)} -Iexperimental/level2-family/src -Isrc \
  tests/hd_gameplay_scaling_test.c \
  -Wl,--wrap=SDL_SetTextureScaleMode \
  ${SDL_LIBS:-$(pkg-config --libs sdl2)} -lm -o "$binary"
SDL_VIDEODRIVER=dummy "$binary" "$@"
