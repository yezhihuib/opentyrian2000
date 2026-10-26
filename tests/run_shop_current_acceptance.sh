#!/usr/bin/env bash
# Explicit fresh Linux SHOP acceptance; archival missing proofs stay separate.
set -euo pipefail
cd "$(dirname "$0")/.."
root=$PWD
san=(); mode=plain
if [[ ${1:-} == --ubsan ]]; then mode=ubsan;san=(-fsanitize=undefined -fno-sanitize-recover=all -fno-omit-frame-pointer);shift;fi
if [[ $# != 2 ]]; then echo "Usage: $0 [--ubsan] ORIGINAL_DATA_DIR EXTERNAL_OUTPUT_DIR" >&2;exit 2;fi
data=$(realpath "$1");out=$(realpath -m "$2");mkdir -p "$out/resources" "$out/pictures-$mode"
PYTHONPATH=tests python3 -m unittest -v test_shop_current_acceptance test_shop_projectile91_compatibility >"$out/static-$mode.log" 2>&1
python3 - "$root" "$out" <<'PY'
from pathlib import Path
import sys,shutil
r,o=map(Path,sys.argv[1:]);s=(r/'tests/pregame_typography_reconstruction.c').read_text()
old='int main(int argc,char **argv)';assert s.count(old)==1
s=s.replace(old,'int typography_original_main(int argc,char **argv)')
s=s.replace('#include "pregame_font_test.c"',f'#include "{r}/tests/pregame_font_test.c"').replace('#include "../src/common_pause.h"',f'#include "{r}/src/common_pause.h"')
(o/'shop_current_fixture.inc').write_text(s)
files=list((r/'assets/hd/artwork/settings-font-v1/canonical').glob('*.hda'))
for name,part in [('fonts',None),('metal','shop-frame-v1/shop-frame-metal-v1.hda'),('talon','shop-talon-v1/shop-talon-option31-v1.hda'),('front','shop-front-v1/shop-front-weapon00-v1.hda'),('generator','shop-generator-v1/shop-generator-weapon16-v1.hda'),('menu',None)]:
 if part:files.append(r/'assets'/part)
 d=o/'resources'/name;assert not d.is_symlink();d.mkdir(exist_ok=True)
 expected={f.name for f in files}
 if name=='menu':expected.update(f.name for ext in ('*.rfr','*.nfr') for f in (r/'assets/hd/shared-menu-runs-v1').glob(ext))
 assert not (set(p.name for p in d.iterdir())-expected),f'Unexpected existing staged resources: {d}'
 assert not any(p.is_symlink() or not p.is_file() for p in d.iterdir()),f'Nonregular staged resource: {d}'
 for f in files:shutil.copy2(f,d/f.name)
 if name=='menu':
  for ext in ('*.rfr','*.nfr'):
   for f in (r/'assets/hd/shared-menu-runs-v1').glob(ext):shutil.copy2(f,d/f.name)
PY
if [[ -z ${SDL_CFLAGS:-} ]];then SDL_CFLAGS=$(pkg-config --cflags sdl2);fi
if [[ -z ${SDL_LIBS:-} ]];then SDL_LIBS=$(pkg-config --libs sdl2);fi
read -r -a cflags <<<"$SDL_CFLAGS";read -r -a libs <<<"$SDL_LIBS"
(ulimit -v "${SHOP_BUILD_MAX_KIB:-1048576}"; ${CC:-cc} -std=c99 -O1 -g -ffunction-sections -fdata-sections -Wall -Wextra -Werror -Wno-misleading-indentation "${san[@]}" "${cflags[@]}" -Isrc -I"$out" tests/shop_current_runtime.c src/hd_cursor.c src/common_menu_runs.c src/selector_font_output.c src/settings_font.c src/load_font.c src/selector_font.c src/helptext.c tests/load_font_globals.c src/font.c src/sprite.c src/data_text.c src/fonthand.c src/nortvars.c src/vga256d.c src/video_scale.c src/video_scale_hqNx.c -Wl,--gc-sections "${libs[@]}" -lm -o "$out/shop-current-$mode") >"$out/build-$mode.log" 2>&1
(ulimit -c 0;ulimit -v "${PREGAME_TEST_MAX_KIB:-524288}";SDL_VIDEODRIVER=dummy "$out/shop-current-$mode" --core "$data" "$out/resources/fonts" "$out/resources/metal" "$out/resources/talon" "$out/resources/front" "$out/resources/generator") >"$out/core-$mode.log" 2>&1
(ulimit -c 0;ulimit -v "${PREGAME_TEST_MAX_KIB:-524288}";SDL_VIDEODRIVER=dummy TYRIAN_TEST_OUTPUT="$out/pictures-$mode" "$out/shop-current-$mode" "$data" "$out/resources/generator" "$out/resources/menu") >"$out/typography-$mode.log" 2>&1
export SDL_CFLAGS SDL_LIBS
python3 tests/shop_current_runtime_mutations.py "$data" "$out" >"$out/mutations-$mode.log" 2>&1
python3 tests/shop_current_capture.py "$data" "$out" >"$out/capture-$mode.log" 2>&1
cat "$out/core-$mode.log" "$out/typography-$mode.log"
echo 'PASS fresh current Linux SHOP gate; synthetic fixtures / SDL software presenter, not game-loop navigation or historical recovery'
