#!/usr/bin/env python3
"""Portable renderer binding oracle: extracted production C, bounded ASan/UBSan.

No game, display, authored assets, network, or writes to the candidate checkout.
Synthetic HDAs and every generated/compiled result are confined to --out.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess

HERE = Path(__file__).resolve().parent
CIRCUIT = [181,182,184,185,192,193,194,195,201,202]
MECHANICAL = [188,189,198,199,186,187,196,197]
FOREST = [211, 212, 213, 215, 221, 222, 223, 224, 225, 231, 232, 233, 234]
OLD = [101,37,57,49,50,321,322,331,332,99,100,106,107,109,110,118,119,120,
       96,97,98,108,323,324,333,334,36,39,40,46,48,56,58,38,47,111,114,113,
       341,342,343,351,352,353]
GRASS = [66,67,69,76,78,79,80,89,90]
CLOUD = [41,42,43,44,45,51,52,53,54,55,61,62,63,64,65]
GRAY = [121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154]
PURPLE = [150,156,157,158,159,160,166,168,169,170,176,177,178]
SLOT_FUNCTIONS = ['cloud_terrain_slot', 'ground_terrain_slot', 'plateau_terrain_slot',
                  'underlay_terrain_slot', 'road_terrain_slot', 'terrain_holes_slot',
                  'stone_foundation_slot', 'layer3_gray_slot', 'layer3_purple_slot',
                  'grass_sand_slot']
FUNCTIONS = ['read_asset', 'scene_asset', 'render_mirror_map_begin'] + SLOT_FUNCTIONS + [
    'forest_terrain_slot', 'layer3_circuit_slot', 'layer3_mechanical_slot', 'render_mirror_bind_terrain', 'plateau_cap_selected_source',
    'render_mirror_ground101_layer1', 'render_mirror_terrain_row']
UNMODIFIED_FILES = ['ground101_material.c', 'ground101_material.h', 'plateau_cap_material.c',
                    'plateau_cap_material.h', 'world_material.c', 'world_material.h',
                    'world_material_fast.c', 'world_material_fast.h']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def brace_end(source, start):
    """Balance C braces while ignoring quoted strings and comments."""
    depth, i, state = 0, start, 'code'
    while i < len(source):
        c = source[i]
        nxt = source[i:i+2]
        if state in ('string', 'char'):
            if c == '\\':
                i += 2
                continue
            if c == ('"' if state == 'string' else "'"):
                state = 'code'
        elif state == 'line':
            if c == '\n':
                state = 'code'
        elif state == 'comment':
            if nxt == '*/':
                state = 'code'
                i += 2
                continue
        elif nxt in ('//', '/*'):
            state = 'line' if nxt == '//' else 'comment'
            i += 2
            continue
        elif c in ('"', "'"):
            state = 'string' if c == '"' else 'char'
        elif c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise AssertionError('Unbalanced C source')


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + re.escape(name) + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, 'Missing function ' + name
    start = source.index('{', match.start())
    return source[match.start():brace_end(source, start)] + '\n'


def loader_loop(source):
    anchor = source.index('/* Read Shapes.DAT */')
    start = source.index('for (int z = 0; z < 600; z++)', anchor)
    opening = source.index('{', start)
    return source[start:brace_end(source, opening)] + '\n'


def finite_snapshots(source, loader):
    result = {name: sha(extract(source, name).encode())
              for name in SLOT_FUNCTIONS + ['explosion_asset_slot', 'read_asset', 'scene_asset']}
    # These unchanged selector prefixes include all entity IDs/roles/slots, but
    # exclude later material dispatch whose signature deliberately gains forest.
    for name, marker in [('get_asset', ' if(slot<0||game_probe_density'),
                         ('render_mirror_enemy_tile', ' if(!role||slot<0)')]:
        function = extract(source, name)
        assert marker in function, (name, marker)
        result[name + '_selection'] = sha(function[:function.index(marker)].encode())
    result['original_engine_registration_loop'] = sha(loader.encode())
    return result


def make_hda(sprite_id, density, shift=0, alpha=255):
    return (b'HDR1' + struct.pack('<6I', 2010000 + sprite_id, density, 24, 28, 0, 0)
            + bytes([(sprite_id + shift) % 256, sprite_id >> 8, 77 + shift, alpha])
            * (24 * 28 * density * density))


def fixtures(out):
    root = out / 'fixtures'
    root.mkdir()
    base = root / 'canonical8'
    base.mkdir()
    for sprite_id in sorted(set(OLD + GRASS + CLOUD + GRAY + PURPLE + FOREST + CIRCUIT + MECHANICAL + [190,191,200])):
        for density in (8, 4):
            (base / f'terrain-shapesz-{sprite_id}-{density}.hda').write_bytes(make_hda(sprite_id, density))
    def variant(label, overrides, omissions=()):
        directory = root / label
        directory.mkdir()
        for file in base.iterdir():
            if file.name in omissions:
                continue
            if file.name in overrides:
                (directory / file.name).write_bytes(overrides[file.name])
            else:
                os.link(file, directory / file.name)
    for label in ('custom8', 'mixed8', 'custom4', 'canonical4', 'custom-alpha8'):
        changes, omit = {}, set()
        for i, sprite_id in enumerate(FOREST):
            shift = 31 if label in ('custom8', 'custom4', 'custom-alpha8') or (label == 'mixed8' and i % 2) else 0
            for density in (8, 4):
                name = f'terrain-shapesz-{sprite_id}-{density}.hda'
                if density == 8 and label in ('custom4', 'canonical4'):
                    omit.add(name)
                else:
                    changes[name] = make_hda(sprite_id, density, shift, alpha=127 if label == 'custom-alpha8' else 255)
        variant(label, changes, omit)
    for sprite_id in FOREST:
        high = f'terrain-shapesz-{sprite_id}-8.hda'
        low = f'terrain-shapesz-{sprite_id}-4.hda'
        variant(f'missing-{sprite_id}', {}, {high, low})
        variant(f'invalid-{sprite_id}', {high: b'INVALID'}, {low})
        variant(f'corrupt-{sprite_id}', {high: make_hda(sprite_id, 8, 31)})
        variant(f'alpha-{sprite_id}', {high: make_hda(sprite_id, 8, alpha=254)})
        variant(f'density4-{sprite_id}', {}, {high})
    for sprite_id in CIRCUIT + MECHANICAL:
        high = f'terrain-shapesz-{sprite_id}-8.hda'
        low = f'terrain-shapesz-{sprite_id}-4.hda'
        variant(f'circuit-missing-{sprite_id}', {}, {high, low})
        variant(f'circuit-invalid-{sprite_id}', {high: b'INVALID'}, {low})
        variant(f'circuit-density4-{sprite_id}', {}, {high})
        variant(f'circuit-invalid8-valid4-{sprite_id}', {high: b'INVALID'})
        variant(f'circuit-selected-{sprite_id}', {high: make_hda(sprite_id, 8, 31)})
        if sprite_id in MECHANICAL:
            variant(f'mechanical-selected4-{sprite_id}', {high: b'INVALID', low: make_hda(sprite_id, 4, 47)})
        valid = make_hda(sprite_id,8)
        bads = {
          'wrong-id': valid[:4] + struct.pack('<I',2010000+sprite_id+1) + valid[8:],
          'wrong-bank': valid[:4] + struct.pack('<I',1010000+sprite_id) + valid[8:],
          'wrong-density': valid[:8] + struct.pack('<I',4) + valid[12:],
          'wrong-width': valid[:12] + struct.pack('<I',12) + valid[16:],
          'wrong-height': valid[:16] + struct.pack('<I',14) + valid[20:],
          'wrong-anchorx': valid[:20] + struct.pack('<I',1) + valid[24:],
          'wrong-anchory': valid[:24] + struct.pack('<I',1) + valid[28:],
          'truncated': valid[:-1], 'trailing': valid+b'X',
        }
        for reason,data in bads.items():
            variant(f'circuit-{reason}-{sprite_id}', {high:data}, {low})
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True, help='Read-only checkout root')
    parser.add_argument('--out', type=Path, required=True, help='New output directory outside checkout/package')
    parser.add_argument('--leak-detection', action='store_true', help='Enable LSan only on hosts without ptrace restrictions')
    args = parser.parse_args()
    candidate, out = args.candidate.resolve(), args.out.resolve()
    if out.exists():
        parser.error('--out must not already exist')
    if any(out == path or path in out.parents for path in (candidate, HERE)):
        parser.error('--out must be outside checkout and test package')
    source_path = candidate / 'src' / 'render_mirror.c'
    source_bytes = source_path.read_bytes()
    forest_header_bytes = (candidate / 'src' / 'forest13_material.h').read_bytes()
    source = source_bytes.decode()
    loader_path = candidate / 'src' / 'tyrian2.c'
    loader_bytes = loader_path.read_bytes()
    loader = loader_loop(loader_bytes.decode())
    frozen = json.loads((HERE / 'frozen-prior-mappings.json').read_text())
    selected = finite_snapshots(source, loader)
    assert selected == frozen['renderer_and_loader'], 'An existing finite mapping/loader changed'
    unchanged = {name: sha((candidate / 'src' / name).read_bytes()) for name in UNMODIFIED_FILES}
    assert unchanged == frozen['lower_cap_sources'], 'Existing lower/cap implementation changed'
    helpers = {name: extract(source, name) for name in FUNCTIONS}
    preflight = helpers['render_mirror_ground101_layer1']
    assert preflight.index('forest13_policy_check(game_probe_assets);') < preflight.index('return;'), 'Policy detection must precede every lower early return'
    row = helpers['render_mirror_terrain_row']
    assert row.index('if(forest_slot>=0&&style!=MIRROR_NORMAL)continue;') < row.index('scene_asset('), 'Forest style rejection must precede source load'
    assert 'if(forest_slot>=0&&forest13_declared()&&!forest)continue;' in row
    assert row.index('if(forest_slot>=0&&forest13_declared()&&!forest)continue;') < row.index('draw_asset_filtered(')
    assert 'const Forest13Record *forest' in extract(source, 'draw_asset_filtered')
    circuit_guard = 'if((gray_slot>=0||purple_slot>=0||circuit_slot>=0||mechanical_slot>=0)&&style!=MIRROR_NORMAL)continue;'
    assert row.index(circuit_guard) < row.index('scene_asset('), 'Circuit NORMAL-only skip must precede source load'
    definitions = []
    for pattern in [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                    r'static Asset assets\[\d+\];',
                    r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];']:
        match = re.search(pattern, source, re.S)
        assert match, pattern
        definitions.append(match.group())
    out.mkdir(parents=True)
    (out / 'production-types.inc').write_text('\n'.join(definitions) + '\n')
    (out / 'production-helpers.inc').write_text('\n'.join(helpers.values()))
    (out / 'production-loader.inc').write_text(loader)
    fixture_root = fixtures(out)
    command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
               '-Wno-misleading-indentation', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
               '-fno-pie', '-no-pie', '-I' + str(out), '-I' + str(candidate / 'src'),
               str(HERE / 'test-forest13-binding.c'), '-o', str(out / 'oracle')]
    compile_result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    (out / 'compile.log').write_text(compile_result.stdout + compile_result.stderr)
    if compile_result.returncode:
        print(compile_result.stderr)
    compile_result.check_returncode()
    environment = dict(os.environ, ASAN_OPTIONS=f'detect_leaks={int(args.leak_detection)}:halt_on_error=1',
                       UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    results = []
    for mode in ('suite', 'lower-missing', 'preflight-failed', 'lower-source-failed',
                 'terrain-only', 'density4', 'original-reference'):
        run = subprocess.run([str(out / 'oracle'), str(fixture_root), mode], capture_output=True,
                             text=True, env=environment, timeout=90)
        (out / (mode + '.log')).write_text(run.stdout + run.stderr)
        print(run.stdout.strip(), flush=True)
        if run.returncode:
            print(run.stderr, flush=True)
        run.check_returncode()
        assert not run.stderr, run.stderr
        results.append(dict(mode=mode, stdout=run.stdout.strip(), exit_code=run.returncode))
    assert source_path.read_bytes() == source_bytes, 'Candidate renderer changed during run'
    assert loader_path.read_bytes() == loader_bytes, 'Engine loader changed during run'
    assert (candidate / 'src' / 'forest13_material.h').read_bytes() == forest_header_bytes, 'Forest header changed during run'
    assert {name: sha((candidate / 'src' / name).read_bytes()) for name in UNMODIFIED_FILES} == unchanged, 'Lower/cap files changed during run'
    report = dict(status='passed', sanitizers=['address', 'undefined'], leak_detection=args.leak_detection,
                  source_sha256=sha(source_bytes), engine_loader_sha256=sha(loader_bytes),
                  forest_header_sha256=sha(forest_header_bytes),
                  test_package_sha256={name: sha((HERE / name).read_bytes()) for name in
                                       ('run-oracle.py', 'test-forest13-binding.c', 'frozen-prior-mappings.json')},
                  mechanical_ids=MECHANICAL, mechanical_slots=list(range(359,367)),
                  explicitly_excluded_mechanical_ids=[190,200],
                  expected_asset_capacity=367, expected_registry_capacity=193,
                  production_function_sha256={k: sha(v.encode()) for k, v in helpers.items()},
                  preserved_prior_mappings=selected, preserved_lower_cap_sources=unchanged,
                  source_assertions=['policy detection before lower early returns',
                                     'forest NORMAL-only skip before scene_asset',
                                     'declared forest skip before draw', 'Forest13Record draw signature',
                                     'circuit NORMAL-only skip before source load'],
                  compile_command=command, runs=results,
                  limitations=['LeakSanitizer is optional because ptrace-based hosts cannot run it; ASan/UBSan are always enabled.',
                               'Material policy/preparation/world context, font-before-effect and draw calls are explicit test doubles.',
                               'Uses actual HDA loader and actual source callbacks with synthetic HDAs.',
                               'Does not validate canonical checksums, policy file parser, sidecar parser, blending, pixels, gameplay, or appearance.',
                               'No game process, captures, authored art, network, candidate checkout edits, or publication.'])
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Report: ' + str(out / 'result.json'))


if __name__ == '__main__':
    main()
