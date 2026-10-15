#!/usr/bin/env python3
"""Source-pinned original shapesZ cloud blend units; no engine or authored assets.

Fixture bytes and compiler outputs remain in a fresh external directory. Every
production body executed here is extracted from the current checkout.
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
BASE = '16810f07ce6ffe58df04f07d97287b5329450d9b'
DATA_SHA = '3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248'
IDS = [*range(41, 46), *range(51, 56), *range(61, 66)]
PINS = [0x1e1978471660308e, 0xf827022613316057, 0xa8cbc7adae4db91f,
        0x1c86f35edb926029, 0x27ec422415762368, 0x5bd2c58855182732,
        0xe2b1309cbd1fcece, 0x3ab26c5cda44cde1, 0xf35212a11fb5188b,
        0xb4e6e16ac2e7de2d, 0xfae994aab7685046, 0x3b671118097700be,
        0xff82eada994a23ad, 0xa8af8a7b2806f91a, 0x8567e7d4a59c3882]
SLOTS = ['cloud_terrain_slot', 'ground_terrain_slot', 'plateau_terrain_slot',
         'underlay_terrain_slot', 'road_terrain_slot', 'terrain_holes_slot',
         'stone_foundation_slot', 'layer3_gray_slot', 'layer3_purple_slot',
         'grass_sand_slot', 'forest_terrain_slot', 'layer3_circuit_slot',
         'layer3_mechanical_slot', 'layer3_linked31_slot']
UNCHANGED = [*SLOTS, 'render_mirror_bind_terrain', 'render_mirror_terrain_pixel',
             'explosion_blend_rgba', 'effect_ramp_monotone_to', 'effect_ramp_monotone',
             'palette_rgb', 'cloud_shadow_rgba', 'darken_rgba', 'complete_turret_group',
             'restore_classic_rect', 'render_mirror_pixel', 'render_mirror_unsupported']
ADDED = ['render_mirror_cloud_blend_row', 'render_mirror_cloud_blend_pixel']
SHA = lambda data: hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def extract(source, name):
    found = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert found, name
    pos = source.index('{', found.start()) + 1
    depth = 1
    while depth:
        depth += (source[pos] == '{') - (source[pos] == '}')
        pos += 1
    return source[found.start():pos] + '\n'


def source_units():
    renderer = (ROOT / 'src/render_mirror.c').read_text()
    background = (ROOT / 'src/backgrnd.c').read_text()
    header = (ROOT / 'src/render_mirror.h').read_text()
    original = {path: git('show', BASE + ':' + path) for path in
                ['src/render_mirror.c', 'src/backgrnd.c', 'src/render_mirror.h']}
    functions = {name: extract(renderer, name) for name in UNCHANGED + ADDED}
    for name in UNCHANGED:
        assert functions[name] == extract(original['src/render_mirror.c'], name), name + ' changed'
    start = renderer.index('/* Wild layer2 clouds use ORIGINAL indices,')
    end = renderer.index('/* Weapon88/1088 keeps three independent', start)
    added_block = renderer[start:end]
    assert all(added_block.count(functions[name]) == 1 for name in ADDED)
    assert renderer[:start] + renderer[end:] == original['src/render_mirror.c'], 'Broad renderer source inverse failed'
    admission = '\tunsigned int compatible_clouds=render_mirror_cloud_blend_row(surface,x,y,map);\n'
    hook = 'render_mirror_cloud_blend_pixel(surface,pixels,*data,(compatible_clouds&(1u<<tile))!=0,(hd_tiles&(1u<<tile))!=0);'
    prior = 'render_mirror_terrain_pixel(surface,pixels,*data,MIRROR_BLEND,(hd_tiles&(1u<<tile))!=0);'
    assert background.count(admission) == background.count(hook) == 1
    assert background.replace(admission, '').replace(hook, prior) == original['src/backgrnd.c'], 'Background inverse failed'
    header_lines = [line for line in header.splitlines(keepends=True)
                    if not any(name in line for name in ADDED)]
    assert len(header.splitlines()) - len(header_lines) == 4
    assert ''.join(header_lines) == original['src/render_mirror.h'], 'Header inverse failed'
    candidate = extract(background, 'blit_background_row_blend')
    baseline = extract(original['src/backgrnd.c'], 'blit_background_row_blend')
    assert candidate.replace(admission, '').replace(hook, prior) == baseline
    return functions, candidate, baseline


def originals(path):
    raw = path.read_bytes()
    assert SHA(raw) == DATA_SHA, 'Unexpected shapesz.dat'
    pos, tiles, metadata = 0, {}, []
    for index in range(1, 601):
        start = pos
        blank = raw[pos]
        pos += 1
        assert blank in (0, 1)
        if blank == 0:
            value = raw[pos:pos + 672]
            assert len(value) == 672
            pos += 672
            if index in IDS:
                slot = IDS.index(index)
                stamp = 14695981039346656037
                for byte in value:
                    stamp = ((stamp ^ byte) * 1099511628211) & ((1 << 64) - 1)
                assert stamp == PINS[slot]
                assert {byte & 240 for byte in value if byte} <= {0x30, 0x60, 0x80}
                tiles[index] = value
                metadata.append({'id': index, 'slot': 186 + slot, 'byte_range': [start, pos],
                                 'sha256': SHA(value), 'fnv1a64': f'{stamp:016x}',
                                 'covered': sum(bool(byte) for byte in value),
                                 'covered_ramp_zero': value.count(0x80), 'transparent': value.count(0),
                                 'hues': sorted({byte & 240 for byte in value if byte})})
    assert list(tiles) == IDS and sum(t.count(0x80) for t in tiles.values()) > 0
    return b''.join(tiles.values()), metadata


def run(command, log, env=None):
    result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=900)
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
    hashes.update(candidate_blit=SHA(candidate.encode()), baseline_blit=SHA(baseline.encode()))
    if args.source_only:
        print(json.dumps({'status': 'PASS', 'base': BASE, 'whole_source_inverse': True,
                          'unchanged_helpers': UNCHANGED, 'production_sha256': hashes}, indent=2))
        return
    assert args.data and args.out, 'Supply --data and --out, or --source-only'
    out = args.out.resolve()
    assert not out.exists() and out != ROOT and ROOT not in out.parents and out not in ROOT.parents, 'Fresh external --out required'
    out.mkdir(parents=True, mode=0o700)
    inputs = {name: SHA((args.data / name).read_bytes()) for name in ['shapesz.dat', 'palette.dat']}
    fixture, metadata = originals(args.data / 'shapesz.dat')
    (out / 'clouds.bin').write_bytes(fixture)
    palette = (args.data / 'palette.dat').read_bytes()
    assert len(palette) >= 6 * 768
    (out / 'palette.bin').write_bytes(palette[5 * 768:6 * 768])
    extracted = dict(functions)
    for name in [*ADDED, 'render_mirror_pixel', 'render_mirror_terrain_pixel']:
        extracted[name] = extracted[name].replace(name + '(', 'production_' + name + '(', 1)
    (out / 'functions.inc').write_text('\n'.join(body[:body.index('{')].strip() + ';' for body in extracted.values()) + '\n' + ''.join(extracted.values()))
    (out / 'candidate-blit.inc').write_text(candidate.replace('void blit_background_row_blend(', 'void production_blit_background_row_blend(', 1))
    (out / 'baseline-blit.inc').write_text(baseline.replace('void blit_background_row_blend(', 'void production_baseline_blit_background_row_blend(', 1))
    runs = {}
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    for kind, flags in [('optimized', ['-O2']), ('sanitized', ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie'])]:
        work = out / kind
        work.mkdir()
        command = [*shlex.split(os.environ.get('CC', 'cc')), '-std=c99', '-Wall', '-Wextra', '-Werror',
                   '-Wno-misleading-indentation', '-Wno-unused-function', *flags, '-I' + str(out),
                   str(Path(__file__).with_suffix('.c')), '-o', str(work / 'units')]
        run(command, work / 'compile.log')
        result = run([str(work / 'units'), str(out / 'clouds.bin'), str(out / 'palette.bin')], work / 'run.log', env)
        runs[kind] = json.loads(result)
        print(kind + ': ' + result.strip(), flush=True)
    negative_controls = {}
    mutations = {
        'covered_ramp_zero_treated_transparent': ('functions.inc', 'if(!source||', 'if(!source||source==0x80||'),
        'hd_detail_flattened_to_palette': ('functions.inc', 'p[sx]=owner[sx]==1?explosion_blend_rgba(p[sx],source):palette_rgb(*address);', 'p[sx]=palette_rgb(*address);'),
        'current_source_hash_bypassed': ('functions.inc', 'if(stamp!=pins[slot-186])continue;', 'if(false&&stamp!=pins[slot-186])continue;'),
        'cloud_shadow_provenance_cleared': ('functions.inc', 'cloud_owner[n]=owner[sx]==1?1:0;', 'cloud_owner[n]=0;'),
        'indexed_average_rounded_instead_of_truncated': ('candidate-blit.inc', '((*pixels & 0x0f) + (*data & 0x0f)) / 2', '((*pixels & 0x0f) + (*data & 0x0f) + 1) / 2'),
    }
    for label, (filename, before, after) in mutations.items():
        work = out / ('negative-' + label)
        work.mkdir()
        body = (out / filename).read_text()
        assert body.count(before) == 1, (label, body.count(before))
        (work / filename).write_text(body.replace(before, after, 1))
        command = [*shlex.split(os.environ.get('CC', 'cc')), '-std=c99', '-O2',
                   '-I' + str(work), '-I' + str(out), str(Path(__file__).with_suffix('.c')), '-o', str(work / 'units')]
        run(command, work / 'compile.log')
        result = subprocess.run([str(work / 'units'), str(out / 'clouds.bin'), str(out / 'palette.bin')],
                                capture_output=True, text=True, timeout=900, env=env)
        (work / 'run.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 1 and 'FAIL line ' in result.stderr, (label, result.returncode, result.stderr)
        negative_controls[label] = {'status': 'REJECTED_AS_EXPECTED', 'failure': result.stderr.strip()}
        print('negative ' + label + ': rejected as expected', flush=True)
    assert inputs == {name: SHA((args.data / name).read_bytes()) for name in inputs}, 'Input bytes changed'
    report = {'status': 'PASS', 'base': BASE, 'whole_source_inverse': True, 'unchanged_helpers': UNCHANGED,
              'production_sha256': hashes, 'source_shapesz_sha256': DATA_SHA, 'clouds': metadata,
              'palette_sha256': inputs['palette.dat'], 'original_inputs_unchanged': True, 'runs': runs,
              'negative_controls': negative_controls,
              'game_runs': 0, 'authored_asset_loads': 0,
              'collaborator_stubs': ['Minimal SDL layouts and font/Vulcan no-op claims; production generic pixel, restoration, binding and slot bodies execute.',
                                     'Terrain-row replacement mask is test-supplied to cover existing replaced-tile suppression without loading assets.',
                                     'The original baseline raw blit callback only records the write trace. Candidate callbacks execute production renderer bodies.'],
              'limitations': ['Finite extracted units do not establish gameplay appearance, frame pacing, GPU or Windows behavior.',
                              'HD underlay colors/ownership and replacement mask are synthetic; no art or engine data is changed.',
                              'Extreme coordinates are admission-only; safe padded negative coordinates exercise the unchanged legacy raw loop.',
                              'LeakSanitizer is disabled for executor compatibility. ASan and UBSan remain enabled.']}
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
