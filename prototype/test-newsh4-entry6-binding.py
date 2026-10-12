#!/usr/bin/env python3
"""Extract production functions and test entry-six coherence under ASan/UBSan.
Unit recorder only. Optional --original-data performs original RLE differentials;
neither this recorder nor its original-data mode runs the game or captures art.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess

BASE = 'fe5f5d7922105dccf67bfe2648ac366c3031bc66'
SOURCE_SHA = 'ab8881b4a26e723650780b19d5aed4ebfe410ea450d4bf7b80840628d61fd89b'
IDS = [81, 83, 85, 119, 121, 123]
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--baseline', default=BASE)
group = p.add_mutually_exclusive_group()
group.add_argument('--original-data', type=Path, help='Original newsh4.shp; exact source hash required')
group.add_argument('--data-dir', type=Path, help='Original data directory containing newsh4.shp')
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
given = a.out.absolute()
out = given.resolve()
if out.exists() or any(q.is_symlink() for q in [given, *given.parents]) or out == repo or out in repo.parents or repo in out.parents:
    p.error('Fresh output outside repository required')
source_path = a.original_data or (a.data_dir / 'newsh4.shp' if a.data_dir else None)
if source_path:
    assert sha(source_path.read_bytes()) == SOURCE_SHA, 'Original newsh4 sheet hash mismatch'
assert re.findall(r'game_probe_assets\s*=', (repo / 'src/game_probe.c').read_text()) == ['game_probe_assets='], 'Selected pack must remain startup-only; reassess invalidation for a new reload writer'
assert 'reload-fresh-process' in (repo / 'src/asset_debug.c').read_text() and 'asset_debug_exit_code=75' in (repo / 'src/asset_debug.c').read_text()
out.mkdir(parents=True)
git = lambda *args: subprocess.check_output(['git', '-C', str(repo), *args])
baseline = git('show', a.baseline + ':src/render_mirror.c').decode()
current = (repo / 'src/render_mirror.c').read_text()
original = (repo / 'src/sprite.c').read_text()
recorder_pins = {name: sha((repo / name).read_bytes()) for name in ['prototype/test-newsh4-entry6-binding.c', 'prototype/test-newsh4-entry6-binding.py']}
manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
pack = repo / 'assets/hd/packs' / manifest['default_preview_pack']
debug_pack = repo / 'assets/hd/packs' / manifest['default_debug_pack']
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
traces, debug_traces, functions, source_pins = {}, {}, {}, {}
# All original gameplay/call-site files must remain unchanged, including the
# recycled scoreitem behavior. The recorder never simulates that state itself.
for path in git('ls-tree', '-r', '--name-only', a.baseline, 'src').decode().splitlines():
    if path == 'src/render_mirror.c':
        continue
    before, after = git('show', a.baseline + ':' + path), (repo / path).read_bytes()
    assert before == after, 'Changed original source: ' + path
    source_pins[path] = sha(after)
for label, source in [('baseline', baseline), ('candidate', current)]:
    d = out / label
    d.mkdir()
    patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;', r'static Asset assets\[\d+\];', r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];']
    declarations = '\n'.join(re.search(pattern, source, re.S).group() for pattern in patterns)
    families = ['linked31', 'newsh4_long7', 'newsh4_opposite7', 'type15_eightheading', 'late_spike']
    if label == 'candidate':
        families += ['newsh4_entry6']
    declarations += ''.join('\nstatic bool ' + family + '_checked,' + family + '_valid;\n' for family in families)
    (d / 'production-types.inc').write_text(declarations)
    names = ['read_asset', 'scene_asset'] + [family + '_family_ready' for family in families] + ['render_mirror_enemy_tile', 'render_mirror_map_begin']
    names += re.findall(r'static int (\w+_slot)\(unsigned int id\)', source)
    names += ['render_mirror_bind_terrain', 'render_mirror_terrain_row', 'palette_rgb', 'enemy_filter_rgba']
    helpers = {name: extract(source, name) for name in names}
    (d / 'production-helpers.inc').write_text('\n'.join(helpers.values()))
    (d / 'production-original.inc').write_text(extract(original, 'blit_sprite2_filter'))
    functions[label] = {name: sha(value.encode()) for name, value in helpers.items()}
    command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-DBASELINE=' + str(int(label == 'baseline')), '-I' + str(d), str(repo / 'prototype/test-newsh4-entry6-binding.c'), '-o', str(d / 'test')]
    result = subprocess.run(command, capture_output=True, text=True)
    (d / 'compile.log').write_text(result.stdout + result.stderr)
    result.check_returncode()
    result = subprocess.run([str(d / 'test'), str(pack), 'trace', '1'], env=env, capture_output=True, text=True, timeout=120)
    (d / 'trace.log').write_text(result.stdout + result.stderr)
    result.check_returncode()
    traces[label] = {tuple(line.split()[:3]): int(line.split()[3]) for line in result.stdout.splitlines()}
    result = subprocess.run([str(d / 'test'), str(debug_pack), 'trace', '1'], env=env, capture_output=True, text=True, timeout=120)
    (d / 'debug-trace.log').write_text(result.stdout + result.stderr)
    result.check_returncode()
    debug_traces[label] = {tuple(line.split()[:3]): int(line.split()[3]) for line in result.stdout.splitlines()}
for name, digest in functions['baseline'].items():
    if name != 'render_mirror_enemy_tile':
        assert functions['candidate'][name] == digest, 'Changed prior helper: ' + name
expected = dict(traces['baseline'])
assert all(('a', '2', str(index)) not in expected for index in IDS)
expected.update({('a', '2', str(index)): 410 + k for k, index in enumerate(IDS)})
assert traces['candidate'] == expected, 'Only six bank2 composite bindings may be added'
expected_debug = dict(debug_traces['baseline'])
assert all(('a', '2', str(index)) not in expected_debug for index in IDS)
expected_debug.update({('a', '2', str(index)): 410 + k for k, index in enumerate(IDS)})
assert debug_traces['candidate'] == expected_debug, 'Only six debug-pack bank2 composite bindings may be added'
results = []


def check(directory, mode, argument, label):
    result = subprocess.run([str(out / 'candidate/test'), str(directory), mode, str(argument)], env=env, capture_output=True, text=True, timeout=120)
    (out / (label + '.log')).write_text(result.stdout + result.stderr)
    result.check_returncode()
    results.append(label)
    return result.stdout


check(pack, 'test', 1, 'complete-preview-six')
check(debug_pack, 'test', 1, 'complete-debug-six')
check(pack, 'geometry', 1, 'physical-row-boundaries')
check(out / 'absent-selected-pack', 'unavailable', 0, 'absent-selected-pack')
original_log = check(pack, 'original', str(source_path.resolve()), 'original-rle') if source_path else None
fixtures = out / 'fixtures'
fixtures.mkdir()
names = [f'enemy-newsh4-{index}-8.hda' for index in IDS]
family_files = {
    'long7': [f'enemy-newsh4-{index}-8.hda' for index in [153, 155, 157, 159, 191, 193, 195]],
    'opposite7': [f'enemy-newsh4-{index}-8.hda' for index in [231, 233, 235, 267, 269, 271, 273]],
    'spike': [f'enemy-newsh2-{index}-8.hda' for index in [1, 3, 5, 7, 9, 11]],
    'type15': [f'enemy-newsh2-{index}-8.hda' for index in [39, 41, 43, 45, 91, 93, 129, 131]],
    'linked31': [f'enemy-newsh2-{index}-8.hda' for index in [15, 17, 53, 55]] + [f'terrain-shapesz-{index}-8.hda' for index in [161, 162, 171, 172]],
}
neighbors = ['enemy-newsh2-153-8.hda'] + [f'enemy-newsh2-{index}-8.hda' for index in [81, 83, 119, 121]] + [name for family in family_files.values() for name in family]
all_files = names + neighbors
assert len(all_files) == len(set(all_files))
before_hashes = {name: sha((pack / name).read_bytes()) for name in all_files}


def fixture(label, target, replacement):
    directory = fixtures / label
    directory.mkdir()
    # Never mutate a hardlinked asset: only the excluded target gets a new inode.
    for other in all_files:
        if other != target:
            os.link(pack / other, directory / other)
    if replacement is not None:
        (directory / target).write_bytes(replacement)
    return directory


four_only = fixtures / 'four-only'
four_only.mkdir()
for name in names:
    raw = (pack / name).read_bytes()
    rgba = raw[28:]
    four = b''.join(rgba[(y * 2 * 192 + x * 2) * 4:(y * 2 * 192 + x * 2) * 4 + 4] for y in range(112) for x in range(96))
    header = list(struct.unpack('<6I', raw[4:28]))
    header[1] = 4
    (four_only / name.replace('-8.hda', '-4.hda')).write_bytes(b'HDR1' + struct.pack('<6I', *header) + four)
check(four_only, 'unavailable', 0, 'four-only-no-retry')
for name in names:
    raw = (pack / name).read_bytes()
    invalid = {'missing': None, 'magic': b'BAD!' + raw[4:], 'truncated': raw[:-1], 'trailing': raw + b'\0', 'alpha': raw[:31] + bytes([raw[31] ^ 255]) + raw[32:], 'partial-alpha': raw[:31] + b'\x7f' + raw[32:], 'rgb': raw[:28] + bytes([raw[28] ^ 1]) + raw[29:]}
    for field in range(6):
        changed = bytearray(raw)
        struct.pack_into('<I', changed, 4 + field * 4, struct.unpack_from('<I', changed, 4 + field * 4)[0] + 1)
        invalid['field-' + str(field)] = bytes(changed)
    for kind, replacement in invalid.items():
        label = name + '-' + kind
        check(fixture(label, name, replacement), 'test', 0, label)
for family, targets in family_files.items():
    for target in targets:
        for kind in ['missing', 'integrity']:
            raw = (pack / target).read_bytes()
            # Linked31 validates opaque alpha; other prior families pin full RGBA.
            replacement = None if kind == 'missing' else raw[:31] + b'\x7f' + raw[32:]
            label = 'independent-' + target + '-' + kind
            check(fixture(label, target, replacement), 'independent', family, label)
# Demonstrate actual disk repair/corruption does not invalidate a live cache.
# Mutated targets always have independent inodes; only reset permits a reread.
for name in names:
    good = (pack / name).read_bytes()
    for kind in ['missing', 'rgb']:
        bad = None if kind == 'missing' else good[:28] + bytes([good[28] ^ 1]) + good[29:]
        for present in [0, 1]:
            label = 'cache-' + name + '-' + kind + '-' + str(present)
            directory = fixture(label, name, good if present else bad)
            process = subprocess.Popen([str(out / 'candidate/test'), str(directory), 'cache', str(present)], env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            ready = process.stdout.readline()
            if ready != 'READY\n':
                stdout, stderr = process.communicate(timeout=120)
                (out / (label + '.log')).write_text(ready + stdout + stderr)
                raise AssertionError('Cache recorder did not reach mutation barrier: ' + label)
            target = directory / name
            replacement = bad if present else good
            if replacement is None:
                target.unlink()
            else:
                target.write_bytes(replacement)
            stdout, stderr = process.communicate('\n', timeout=120)
            (out / (label + '.log')).write_text(ready + stdout + stderr)
            assert process.returncode == 0, label
            results.append(label)
assert before_hashes == {name: sha((pack / name).read_bytes()) for name in all_files}, 'Original pack changed'
assert (repo / 'src/render_mirror.c').read_text() == current, 'Renderer changed during recorder run'
assert source_pins == {name: sha((repo / name).read_bytes()) for name in source_pins}, 'Gameplay source changed during recorder run'
assert recorder_pins == {name: sha((repo / name).read_bytes()) for name in recorder_pins}, 'Recorder changed during run'
report = {
    'status': 'passed', 'baseline': a.baseline,
    'recorder_source_sha256': recorder_pins,
    'renderer_source_sha256': {'baseline': sha(baseline.encode()), 'candidate': sha(current.encode())},
    'sanitizers': ['address', 'undefined'], 'leak_detection': False,
    'leak_detection_reason': 'LSan cannot run under this executor ptrace; recorder reset frees all allocations',
    'unchanged_prior_bindings': len(traces['baseline']), 'unchanged_debug_prior_bindings': len(debug_traces['baseline']), 'new_bindings': 6,
    'entry_asset_open_counts': 'Exactly one 8x attempt/member per preflight, zero 4x attempts; cached calls do not reread',
    'four_only_family_fallback': True, 'absent_selected_directory_fallback': True,
    'all_sheet_identities_checked': list(range(37)), 'actor_bases_checked': [0, 700],
    'terrain_layers_checked': [1, 2, 3], 'terrain_ids_checked': [1, 600],
    'first_member_quadrant_orders': 24, 'preflight_allocation_failure_positions': list(range(6)),
    'all_six_all_parts_all_256_filters': True, 'empty_right_quadrants_85_123_preserved': True,
    'geometric_quadrant_fallback': {
        'family_only': True, 'required_layout': [320, 200, 320, 8, 1], 'safe_x': [0, 308], 'safe_y': [-13, 199],
        'pitch_cases': ['INT_MIN', -1, 0, 11, 12, 319, 320, 321, 'INT_MAX'],
        'clipped_y_cases': ['INT_MIN', 'INT_MIN+13', 'INT_MIN+14', -214, -28, -15, -14, -13, -12, -1, 0, 1, 185, 186, 198, 199, 200, 213, 214, 'INT_MAX-14', 'INT_MAX'],
        'all_six_all_parts_all_256_filters': True, 'extreme_xy_cartesian': True,
        'invalid_width_height_bpp_null_format': True, 'neighbor_edge_routes_unchanged': True,
    },
    'fixture_mirrors': 'Never-mutated hardlinks; corrupted/repaired targets use independent inodes; source hashes verified afterward',
    'disabled_scene_combinations': [0, 2], 'scene_combinations_checked': [0, 1, 2, 3],
    'cache_lifecycle': 'Startup-selected pack. Actual disk changes leave success/failure cached; reset rereads. No mid-session reload writer.',
    'cache_disk_change_cases': 24, 'independent_prior_families': list(family_files),
    'both_selected_default_packs_checked': [manifest['default_preview_pack'], manifest['default_debug_pack']],
    'family_fallback_cases': results, 'functions': functions,
    'original_blitter_sha256': sha(extract(original, 'blit_sprite2_filter').encode()),
    'original_rle_differential': {'executed': bool(source_path), 'source_sha256': SOURCE_SHA if source_path else None, 'result': original_log.strip() if original_log else 'Not requested; pass --original-data or --data-dir', 'method': 'Unchanged extracted original blitter versus independently decoded source cells and linear-address clipping, padded storage under sanitizers; HD route recorder does not claim final RGB'},
    'unchanged_gameplay_sources': source_pins,
    'limitations': ['Unit recorder only; no game runs, captures, actual actor-state observations, final rendered pixels, or Windows runtime.'],
}
(out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: value for key, value in report.items() if key not in ['functions', 'family_fallback_cases', 'unchanged_gameplay_sources']}, indent=2))
print('Cases:', len(results))
