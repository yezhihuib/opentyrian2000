#!/usr/bin/env python3
"""Bounded production-function tests; synthetic sprites, no game data or UI.

Run with an existing Linux C compiler (including WSL). SDL is a structural shim.
Unrelated feature observers are disabled explicitly; this is not native-game proof.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def extract(text, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + re.escape(name) + r'\([^;{}]*\)\s*\{', text, re.M)
    if not match:
        raise RuntimeError('Missing production function: ' + name)
    end = text.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[match.start():end] + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-ref')
    parser.add_argument('--expect-baseline-defects', action='store_true')
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()

    def read(path):
        if args.source_ref:
            return subprocess.check_output(['git', 'show', args.source_ref + ':' + path], cwd=ROOT, text=True)
        return (ROOT / path).read_text(encoding='utf-8')

    mirror = read('src/render_mirror.c')
    sprite = read('src/sprite.c')
    entity = read('src/entity_draw.c')
    names = ['decode_tile', 'get_asset', 'palette_rgb', 'blend_rgba', 'darken_rgba',
             'cloud_shadow_rgba', 'draw_asset_filtered', 'draw_asset',
             'render_mirror_entity', 'render_mirror_pixel', 'render_mirror_entity_end']
    bodies = {name: extract(mirror, name) for name in names}
    for name in ['blit_sprite2', 'blit_sprite2x2']:
        bodies[name] = extract(sprite, name)
    bodies['draw_entity_sprite2'] = extract(entity, 'draw_entity_sprite2')
    # Disable only unrelated owners; the tested cache/compositor/indexed blitter
    # and generic wrapper are the unmodified extracted production functions.
    voids = ['data_frame_pixel', 'data_portrait_pixel', 'storm_pixel', 'settings_font_pixel',
             'load_font_pixel', 'selector_font_pixel', 'pregame_font_pixel', 'font_final_pixel',
             'common_pause_pixel', 'render_mirror_shadow_end', 'vulcan_shadow_clear',
             'font_before_effect', 'restore_classic_rect', 'game_probe_draw', 'game_probe_scene_draw',
             'asteroid1_talon_blend_begin', 'asteroid1_talon_blend_end', 'load_font_arrow_sprite_begin',
             'load_font_arrow_sprite_end', 'pregame_font_sprite2_begin', 'pregame_font_sprite2_end',
             'pregame_font_quad_begin', 'pregame_font_quad_end', 'asset_debug_effect']
    falses = ['vulcan_shadow_pixel', 'font_pixel', 'cloud_asset', 'fixed_pickup_flash_draw',
              'data_value_draw', 'cash25_surface_ready', 'cash25_family_ready', 'cash75_family_ready',
              'cash50_family_ready', 'gem100_family_ready', 'gem250_family_ready', 'draw_vulcan_shadow']
    families = ['talon', 'shield', 'pulse', 'hitflare', 'smoke', 'green', 'small_explosion',
                'cash25', 'rotor', 'vulcan']
    for family in families:
        voids += ['global_' + family + '_final_pixel', 'global_' + family + '_end']
        falses += ['global_' + family + '_pixel', 'global_' + family + '_is_index']
    stubs = ['#define ' + name + '(...) ((void)0)' for name in voids]
    stubs += ['#define ' + name + '(...) (false)' for name in falses]
    for name in sorted(set(re.findall(r'\b(sonic_\w+|mint27_source_matches|explosion_asset_slot)\(', bodies['get_asset']))):
        stubs.append('#define ' + name + '(...) ' + ('(-1)' if name.endswith('member') or name == 'explosion_asset_slot' else '(false)'))
    stubs += ['#define vulcan_shadow_member(...) (-1)', '#define talon_frame(...) (NULL)',
              '#define green_background_peak(...) (0u)', '#define green_head_composite(...) (0u)']
    for name in ['ground101_select', 'plateau_cap_select', 'forest13_select', 'enemy_filter_rgba',
                 'explosion_asset_blend_rgba', 'green_background_snapshot', 'blit_sprite2_blend',
                 'blit_sprite2_darken', 'blit_sprite2x2_blend', 'blit_sprite2x2_darken']:
        stubs.append('#define ' + name + '(...) assert(!"unexpected unrelated effect")')
    enums = re.search(r'enum \{ ASSET_NEWSH2=.*?\};', mirror).group()
    code = (ROOT / 'tests/render_boundary_test.c').read_text(encoding='utf-8')
    code = code.replace('/* PRODUCTION_ENUMS */', enums).replace('/* FEATURE_STUBS */', '\n'.join(stubs))
    code = code.replace('/* PRODUCTION_FUNCTIONS */', '\n'.join(bodies.values()))
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    report = {'source_ref': args.source_ref or 'working-tree', 'expected_baseline_defects': args.expect_baseline_defects,
              'scope': 'Actual generic cache, compositor, pixel observer, wrapper and original indexed blitter; synthetic RLE; SDL structural shim; other owners disabled. No gameplay/native SDL acceptance.',
              'function_sha256_lf_utf8': {name: hashlib.sha256(body.encode()).hexdigest() for name, body in bodies.items()}, 'runs': []}
    with tempfile.TemporaryDirectory(prefix='render-boundary-') as temporary:
        directory = Path(temporary)
        c = directory / 'test.c'
        c.write_text(code, encoding='utf-8')
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=1:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        for mode, flags in [('optimized', ['-O2']), ('asan-ubsan', ['-O1', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-no-pie'])]:
            exe = directory / mode
            command = ['cc', '-std=c99', '-Wall', '-Wextra', '-Werror=implicit-function-declaration',
                       '-Wno-unused-function', '-Wno-unused-variable', '-Wno-unused-parameter', '-Wno-misleading-indentation'] + flags + [str(c), '-o', str(exe)]
            compiled = subprocess.run(command, capture_output=True, text=True, timeout=60)
            if compiled.returncode:
                raise RuntimeError(compiled.stdout + compiled.stderr)
            run = subprocess.run([str(exe), 'baseline' if args.expect_baseline_defects else 'fixed'], capture_output=True, text=True, timeout=30, env=env)
            report['runs'].append({'mode': mode, 'exit': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
            if run.returncode:
                report['status'] = 'FAIL'
                args.receipt.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
                raise RuntimeError(run.stdout + run.stderr)
    report['status'] = 'PASS'
    args.receipt.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
