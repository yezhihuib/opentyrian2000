#!/usr/bin/env python3
"""Exercise real renderer region registration, fallback and same-frame redraw.

Synthetic opaque assets and indexed writes only. No original data, SDL, game
launch, generated art or repository build is needed. Work files are retained.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = [
    'palette_rgb', 'complete_turret_group', 'restore_classic_rect',
    'blend_rgba', 'cloud_shadow_rgba', 'cloud_asset', 'darken_rgba',
    'explosion_asset_slot', 'enemy_filter_rgba', 'explosion_asset_blend_rgba',
    'green_background_snapshot', 'green_background_peak', 'green_head_composite',
    'draw_asset_filtered', 'draw_asset', 'render_mirror_pixel',
    'render_mirror_entity_end',
]
PATTERNS = [
    r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
    r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',
    r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',
    r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',
]


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'src/render_mirror.c')
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--sanitize', action='store_true')
    parser.add_argument('--expect-stale', action='store_true',
                        help='diagnostic control: require the historical stale-sibling defect')
    args = parser.parse_args()
    source = args.source.read_text()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    types = []
    for pattern in PATTERNS:
        match = re.search(pattern, source, re.S)
        assert match, pattern
        types.append(match.group())
    functions = {name: extract(source, name) for name in FUNCTIONS}
    (out / 'types.inc').write_text('\n'.join(types))
    (out / 'functions.inc').write_text('\n'.join(functions.values()))
    command = shlex.split(os.environ.get('CC', 'cc')) + [
        '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
        '-I' + str(out), str(Path(__file__).with_suffix('.c')),
        '-o', str(out / 'test'),
    ]
    if args.sanitize:
        command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
    subprocess.run(command, check=True)
    env = dict(os.environ)
    if args.sanitize:
        env.setdefault('ASAN_OPTIONS', 'detect_leaks=0:halt_on_error=1')
        env.setdefault('UBSAN_OPTIONS', 'halt_on_error=1:print_stacktrace=1')
    result = subprocess.run([str(out / 'test'), str(int(args.expect_stale))],
                            capture_output=True, text=True, env=env, timeout=180)
    (out / 'stdout.log').write_text(result.stdout)
    (out / 'stderr.log').write_text(result.stderr)
    report = {
        'status': 'PASS' if result.returncode == 0 else 'FAIL',
        'expected_stale_siblings': args.expect_stale,
        'source': str(args.source.resolve()),
        'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'function_sha256': {name: hashlib.sha256(body.encode()).hexdigest()
                            for name, body in functions.items()},
        'sanitizers': 'address,undefined' if args.sanitize else None,
        'returncode': result.returncode,
        'results': result.stdout.splitlines(),
        'qualification': 'Extracted production draw/registration, restoration and pixel callbacks; synthetic same-frame inputs. No natural gameplay witness or Windows acceptance.',
    }
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(result.stdout, end='')
    print(result.stderr, end='')
    print('Report:', out / 'report.json')
    result.check_returncode()


if __name__ == '__main__':
    main()
