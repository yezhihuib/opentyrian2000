#!/usr/bin/env python3
"""Source-extracted draw/ownership pixel unit; never runs the game or captures it."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess

BASE = 'e6fd18a8d53c31f90d15c0ac1bce9d0e927336ac'
IDS = [171, 190, 209, 228, 247, 266]
SOURCE_SHA = '8773ebcae4be992ecfbb476c0797b0bef4d43faa4c99449890bfaa28c8d9cbcc'
FREEZE_SHA = '5012962c54ab3fd0b22cc8a2534fddee272704fa73447e267ffeb4938f787c33'
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
p.add_argument('--original-data', type=Path, required=True, help='Read-only exact newsh2.shp')
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
given = a.out.absolute()
out = given.resolve()
assert not out.exists() and not any(q.is_symlink() for q in [given, *given.parents]), 'Fresh nonsymlink output required'
assert out != repo and repo not in out.parents and out not in repo.parents, 'External output required'
original = a.original_data.read_bytes()
assert sha(original) == SOURCE_SHA
source = (repo / 'src/render_mirror.c').read_text()
sprite = (repo / 'src/sprite.c').read_text()
source_pins = {n: sha((repo / n).read_bytes()) for n in ['src/render_mirror.c', 'src/sprite.c', 'prototype/test-type3-small-pixels.c', 'prototype/test-type3-small-pixels.py']}
art = repo / 'assets/hd/artwork/type3-small-six-v1'
assert sha((art / 'inventory.json').read_bytes()) == FREEZE_SHA
inventory = json.loads((art / 'inventory.json').read_text())
manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
reference = bytearray()
asset_pins = {}
for k, base in enumerate(IDS):
    pos = struct.unpack_from('<H', original, (base - 1) * 2)[0]
    cell = 0
    mask, indices = bytearray(168), bytearray(168)
    while original[pos] != 15:
        code = original[pos]
        pos += 1
        cell += code & 15
        count = code >> 4
        for _ in range(count):
            assert 0 <= cell < 168 and not mask[cell]
            mask[cell], indices[cell] = 255, original[pos]
            pos += 1
            cell += 1
    assert sum(bool(v) for v in mask) == [98, 82, 82, 74, 82, 82][k]
    name = f'enemy-newsh2-{base}-8.hda'
    raw = (art / 'output' / name).read_bytes()
    assert len(raw) == 43036 and raw[:28] == b'HDR1' + struct.pack('<6I', 1010000 + base, 8, 12, 14, 0, 0)
    assert sha(raw) == inventory['outputs'][k]['HDA_SHA256']
    for y in range(112):
        for x in range(96):
            rgba = raw[28 + (y * 96 + x) * 4:32 + (y * 96 + x) * 4]
            assert rgba[3] == mask[(y // 8) * 12 + x // 8]
            # Frozen whole-RGBA digest also preserves RGB beneath alpha=0.
    for pack in [manifest['default_preview_pack'], manifest['default_debug_pack']]:
        assert (repo / 'assets/hd/packs' / pack / name).read_bytes() == raw
    asset_pins[name] = sha(raw)
    reference.extend(indices + mask + raw[28:])

families = ['linked31', 'newsh4_long7', 'newsh4_opposite7', 'type15_eightheading', 'late_spike', 'newsh4_entry6', 'type3_small']
names = ['palette_rgb', 'blend_rgba', 'cloud_shadow_rgba', 'cloud_asset', 'darken_rgba', 'explosion_asset_slot', 'enemy_filter_rgba', 'explosion_asset_blend_rgba', 'green_background_snapshot', 'green_background_peak', 'green_head_composite', 'draw_asset_filtered', 'render_mirror_pixel', 'render_mirror_entity_end', 'read_asset', 'scene_asset']
names += [f + '_family_ready' for f in families] + ['render_mirror_enemy_tile']
helpers = {name: extract(source, name) for name in names}
helpers.update({name: extract(sprite, name) for name in ['blit_sprite2', 'blit_sprite2_filter']})
# The selected source excerpt is the unchanged ordinary-output crop inside
# render_mirror_finish, wrapped only to remove unrelated frame/HUD state.
crop = re.search(r'  int d=game_probe_density;\n  for\(int y=0;y<184\*d;y\+\+\) memcpy\([^\n]+;', extract(source, 'render_mirror_finish')).group()
helpers['production_crop_excerpt'] = 'static void production_crop_excerpt(void) {\n' + crop + '\n}\n'

declarations = '\n'.join(re.search(pattern, source, re.S).group() for pattern in [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;', r'static Asset assets\[\d+\];'])
declarations += ''.join('\nstatic bool ' + f + '_checked,' + f + '_valid;\n' for f in families)
out.mkdir(parents=True)
(out / 'production-types.inc').write_text(declarations)
(out / 'production-functions.inc').write_text('\n'.join(helpers.values()))
(out / 'reference-data.bin').write_bytes(reference)
command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-I' + str(out), str(repo / 'prototype/test-type3-small-pixels.c'), '-o', str(out / 'test')]
r = subprocess.run(command, capture_output=True, text=True)
(out / 'compile.log').write_text(r.stdout + r.stderr)
r.check_returncode()
env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
results = {}
for kind in ['preview', 'debug']:
    pack = repo / 'assets/hd/packs' / manifest['default_' + kind + '_pack']
    r = subprocess.run([str(out / 'test'), str(pack), str(a.original_data.resolve()), str(out / 'reference-data.bin')], capture_output=True, text=True, env=env, timeout=240)
    (out / (kind + '.log')).write_text(r.stdout + r.stderr)
    r.check_returncode()
    results[kind] = r.stdout.strip()
    print(kind + ': ' + r.stdout.strip())
assert source_pins == {n: sha((repo / n).read_bytes()) for n in source_pins}, 'Test/source changed during run'
receipt = {'status': 'PASS', 'unit_only_no_game_or_native_capture': True, 'parent': BASE,
    'original_newsh2_sha256': SOURCE_SHA, 'source_inventory_sha256': FREEZE_SHA,
    'source_pins': source_pins, 'asset_sha256': asset_pins,
    'extracted_production_functions_sha256': {n: sha(v.encode()) for n, v in helpers.items()},
    'sanitizers': ['AddressSanitizer', 'UndefinedBehaviorSanitizer'],
    'results': results, 'coverage': {
      'original_source_masks': 'All six, 500 logical opaque cells, exact 64-subpixel binary alpha and transparent RGB technical matte',
      'filter_operator': 'All 256 filters x 256 source peaks x six alpha values x three nonmonotonic palettes; actual enemy_filter_rgba with independent integer oracle',
      'actual_draw': 'All six x 256 filters on authored RGBA; normal/filter original RLE and actual ownership hook',
      'clipping': 'Top/bottom partial visibility and fully-offscreen guards; physical x=0/308; exact source-extracted output crop x=24..287/y=0..183, with 144 crossing/outside-edge cases per pack',
      'fallback': 'Entire draw rejected on x<0 or x>308, original physical-row wrapped RLE writes take classic ownership',
      'ownership': 'Mixed pre-existing ownership 0/1/2, cloud provenance, green-layer markers, selected and RGB; transparent/neighbor cells preserved; exact all-64-subpixel checks',
      'memory': 'Padded indexed array keeps original before/after-surface pointer arithmetic inside allocation; all allocations have canaries; whole-frame RGB/index/selection/ownership byte comparisons after every transaction, plus full under-layer/canary comparisons at phase boundaries'},
    'limitations': ['LeakSanitizer is disabled: the executor ptrace environment rejects leak inspection at exit; all harness allocations are explicitly freed', 'No SDL/game initialization, gameplay/state/event execution, native images, or visual acceptance', 'Unrelated material/font/local-blend branches are fail-if-entered stubs; relevant draw/filter/pixel/RLE functions are exact extracted production source; output crop is a verbatim loop excerpt with a unit-only wrapper']}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
