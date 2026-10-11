"""Exercise extracted production head-layer drawing against an independent oracle."""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess
import tempfile


def extract_function(source, name):
    match = re.search(r'^(?:static )?(?:Uint32|unsigned int|int|void|bool) ' + name
                      + r'\([^\n]*\)\s*\{', source, re.MULTILINE)
    if match is None:
        raise RuntimeError('Production helper not found: ' + name)
    start = source.index('{', match.start())
    depth = 1
    end = start + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true', help='enable ASan and UBSan')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    source = (repo / 'src/render_mirror.c').read_text()
    type_patterns = [
        r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
        r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',
        r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',
        r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',
    ]
    definitions = []
    for pattern in type_patterns:
        match = re.search(pattern, source, re.DOTALL)
        if match is None:
            raise RuntimeError('Production type no longer matches: ' + pattern)
        definitions.append(match.group())
    names = [
        'palette_rgb', 'complete_turret_group', 'restore_classic_rect',
        'blend_rgba', 'darken_rgba', 'brightness_rgba',
        'explosion_asset_slot', 'enemy_filter_rgba', 'explosion_asset_blend_rgba',
        'green_background_snapshot', 'green_background_peak', 'green_head_composite',
        'draw_asset_filtered', 'render_mirror_pixel', 'render_mirror_brightness_pixel',
    ]
    if 'static Uint32 cloud_shadow_rgba(' in source:
        names[1:1] = ['cloud_shadow_rgba', 'cloud_asset']
    with tempfile.TemporaryDirectory(prefix='green-head-layer-test-') as directory:
        root = Path(directory)
        (root / 'production-types.inc').write_text('\n'.join(definitions))
        (root / 'production-helpers.inc').write_text(
            '\n'.join(extract_function(source, name) for name in names))
        shutil.copy2(Path(__file__).with_suffix('.c'), root / 'test.c')
        executable = root / ('test.exe' if os.name == 'nt' else 'test')
        command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra']
        if args.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        subprocess.run(command + [str(root / 'test.c'), '-o', str(executable)], check=True)
        environment = dict(os.environ)
        if args.sanitize:
            # LeakSanitizer cannot run under the executor's ptrace sandbox.
            environment.setdefault('ASAN_OPTIONS', 'detect_leaks=0:halt_on_error=1')
            environment.setdefault('UBSAN_OPTIONS', 'halt_on_error=1:print_stacktrace=1')
        subprocess.run([str(executable)], env=environment, check=True)


if __name__ == '__main__':
    main()
