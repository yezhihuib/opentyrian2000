#!/usr/bin/env python3
"""Finite original-art Plasma blend units. Extract production bodies; never launch the engine.

Original data and generated fixture/build files stay outside the checkout. Tests
need only a C99 compiler, not SDL or a previously built engine.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd98556a7798d79980c785b5a25ba67566697bdb0'
DATA_PINS = {
    'tyrian.shp': '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0',
    'tyrianc.shp': 'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d',
}
DECODED_PINS = [0x6d5e2fcad8f0a564, 0xe38948558d55665d, 0x2aae962a99b61745]
UNCHANGED = ['hud_sprite_decode', 'explosion_blend_rgba', 'effect_ramp_monotone_to',
             'effect_ramp_monotone', 'palette_rgb', 'cloud_shadow_rgba', 'darken_rgba',
             'complete_turret_group', 'restore_classic_rect', 'render_mirror_pixel',
             'render_mirror_unsupported']
ADDED = ['render_mirror_plasma_projectile_begin', 'render_mirror_plasma_projectile_pixel']
SHA = lambda raw: hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    pos = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[pos] == '{') - (source[pos] == '}')
        pos += 1
    return source[match.start():pos] + '\n'


def source_units():
    renderer = (ROOT / 'src/render_mirror.c').read_text()
    sprite = (ROOT / 'src/sprite.c').read_text()
    old_renderer = git('show', BASE + ':src/render_mirror.c')
    old_sprite = git('show', BASE + ':src/sprite.c')
    functions = {name: extract(renderer, name) for name in UNCHANGED + ADDED}
    for name in UNCHANGED:
        assert functions[name] == extract(old_renderer, name), name + ' changed outside compatibility path'
    candidate = extract(sprite, 'blit_sprite_blend')
    baseline = extract(old_sprite, 'blit_sprite_blend')
    admission = '\tconst bool plasma_blend = render_mirror_plasma_projectile_begin(surface, x, y, table, index);\n'
    hook = 'render_mirror_plasma_projectile_pixel(surface,pixels,*data,plasma_blend);'
    assert candidate.count(admission) == candidate.count(hook) == 1
    assert candidate.replace(admission, '').replace(hook, 'render_mirror_pixel(surface,pixels,*data,MIRROR_BLEND);') == baseline
    return functions, candidate, baseline


def decode(width, height, data):
    # Independent linear-cell decoder, separate from the production x/y decoder.
    pixels, coverage = bytearray(width * height), bytearray(width * height)
    cell = pos = 0
    while pos < len(data):
        value = data[pos]
        pos += 1
        assert cell < width * height
        if value == 255:
            assert pos < len(data)
            count = data[pos]
            pos += 1
            assert count <= width - cell % width
            cell += count
        elif value == 254:
            cell += width - cell % width
        elif value == 253:
            cell += 1
        else:
            assert not coverage[cell]
            pixels[cell], coverage[cell] = value, 255
            cell += 1
    return bytes(pixels), bytes(coverage)


def original_records(path):
    raw = path.read_bytes()
    assert SHA(raw) == DATA_PINS[path.name], 'Unexpected original data: ' + path.name
    count = struct.unpack_from('<H', raw)[0]
    offsets = list(struct.unpack_from('<' + str(count) + 'I', raw, 2)) + [len(raw)]
    table = raw[offsets[5]:offsets[6]]
    pos = 2
    records = []
    for index in range(struct.unpack_from('<H', table)[0]):
        populated = table[pos]
        pos += 1
        if not populated:
            continue
        width, height, size = struct.unpack_from('<3H', table, pos)
        pos += 6
        data = table[pos:pos + size]
        pos += size
        if index in (22, 23, 24):
            pixels, mask = decode(width, height, data)
            stamp = 14695981039346656037
            for value in pixels + mask:
                stamp = ((stamp ^ value) * 1099511628211) & ((1 << 64) - 1)
            assert stamp == DECODED_PINS[index - 22]
            assert {p & 240 for p, m in zip(pixels, mask) if m} == {0x70}
            records.append((width, height, data, pixels, mask))
    assert len(records) == 3
    return records, {'file_sha256': SHA(raw), 'option_table_sha256': SHA(table), 'pieces': [
        {'id': i + 22, 'width': w, 'height': h, 'raw_bytes': len(d), 'raw_sha256': SHA(d),
         'indices_sha256': SHA(p), 'coverage_sha256': SHA(m), 'opaque_pixels': sum(bool(v) for v in m),
         'decoded_fnv1a64': f'{DECODED_PINS[i]:016x}'}
        for i, (w, h, d, p, m) in enumerate(records)]}


def run(command, log, env=None):
    result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=600)
    log.write_text('$ ' + shlex.join(map(str, command)) + '\n' + result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f'{log}: exit {result.returncode}\n{result.stdout[-2000:]}{result.stderr[-6000:]}')
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--source-only', action='store_true')
    args = parser.parse_args()
    functions, candidate, baseline = source_units()
    hashes = {name: SHA(body.encode()) for name, body in functions.items()}
    hashes.update(candidate_raw_blit=SHA(candidate.encode()), baseline_raw_blit=SHA(baseline.encode()))
    if args.source_only:
        print(json.dumps({'status': 'PASS', 'baseline': BASE, 'exact_raw_blit_inverse': True,
                          'unchanged_production_helpers': UNCHANGED, 'source_sha256': hashes}, indent=2))
        return
    assert args.data and args.out, 'Supply --data and --out, or --source-only'
    out = args.out.resolve()
    assert not out.exists() and out != ROOT and ROOT not in out.parents and out not in ROOT.parents, 'Fresh external --out required'
    out.mkdir(parents=True, mode=0o700)
    original_hashes = {name: SHA((args.data / name).read_bytes()) for name in [*DATA_PINS, 'palette.dat']}
    sources = {}
    decoded_records = []
    for name in DATA_PINS:
        records, sources[name] = original_records(args.data / name)
        decoded_records.append(records)
        fixture = b''.join(struct.pack('<3H', w, h, len(d)) + d + p + m for w, h, d, p, m in records)
        (out / (name + '.pieces')).write_bytes(fixture)
    assert decoded_records[0] == decoded_records[1], 'Normal and Christmas originals differ'
    palette = (args.data / 'palette.dat').read_bytes()
    assert len(palette) >= 6 * 768
    (out / 'palette.bin').write_bytes(palette[5 * 768:6 * 768])
    extracted = dict(functions)
    # Only observation function names change. Production function bodies stay byte-exact.
    for name in ['hud_sprite_decode', *ADDED, 'render_mirror_pixel']:
        extracted[name] = extracted[name].replace(name + '(', 'production_' + name + '(', 1)
    (out / 'functions.inc').write_text('\n'.join(body[:body.index('{')].strip() + ';' for body in extracted.values()) + '\n' + ''.join(extracted.values()))
    (out / 'candidate-blit.inc').write_text(candidate.replace('void blit_sprite_blend(', 'void production_blit_sprite_blend(', 1))
    (out / 'baseline-blit.inc').write_text(baseline.replace('void blit_sprite_blend(', 'void baseline_blit_sprite_blend(', 1))
    sprite_types = 'typedef struct\n' + (ROOT / 'src/sprite.h').read_text().split('typedef struct\n', 1)[1].split('extern Sprite_array', 1)[0]
    (out / 'sprite-types.inc').write_text(sprite_types)
    runs = {}
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    for kind, flags in [('optimized', ['-O2']), ('sanitized', ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie'])]:
        command = [*shlex.split(os.environ.get('CC', 'cc')), '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-Wno-unused-function', *flags,
                   '-I' + str(out), str(Path(__file__).with_suffix('.c')), '-o', str(out / kind)]
        run(command, out / (kind + '-compile.log'))
        result = run([str(out / kind), str(out / 'tyrian.shp.pieces'), str(out / 'tyrianc.shp.pieces'), str(out / 'palette.bin')], out / (kind + '.log'), env)
        runs[kind] = json.loads(result)
        print(kind + ': ' + result.strip(), flush=True)
    assert original_hashes == {name: SHA((args.data / name).read_bytes()) for name in original_hashes}, 'Original inputs changed'
    report = {'status': 'PASS', 'baseline': BASE, 'exact_raw_blit_inverse': True, 'production_functions_sha256': hashes,
              'originals': sources, 'normal_christmas_decoded_and_raw_equal': True, 'original_data_unchanged': True,
              'palette_sha256': original_hashes['palette.dat'], 'runs': runs, 'game_runs': 0, 'resource_files_loaded': 0,
              'resource_scope': 'These three original-art pieces have no HDA/new-art resource path. No HDA lookup or resource mutation is applicable. Owner0 and owner2 plus mixed-owner cases represent classic/indexed-copy or absent/rejected-HD underlays.',
              'observation_shims': ['Function-name-only observation wrappers count each raw draw, admission, decode and pixel callback.',
                                    'Baseline raw blit body is exact d98556a; callback name is redirected with a C macro to a write-trace observer.'],
              'collaborator_stubs': ['Minimal SDL surface/type layouts; no SDL calls, graphics driver, or engine entry point.',
                                     'Font hooks are no-ops; Vulcan/font pixel claims return false; actual generic fallback and local-restore bodies execute.',
                                     'Local-restore trace hook is a no-op. Synthetic full-screen region makes fallback results independently auditable.'],
              'limitations': ['Finite extracted units do not establish actual gameplay, Windows/GPU behavior, performance, or visual aesthetics.',
                              'Malformed RLE mutations run admission/decode only; the intentionally unsafe original raw blitter is never run on malformed input.',
                              'HD scene colors/ownership are synthetic test-only; no authored resources are loaded or modified.',
                              'LeakSanitizer disabled for executor compatibility; AddressSanitizer and UndefinedBehaviorSanitizer are enabled.']}
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
