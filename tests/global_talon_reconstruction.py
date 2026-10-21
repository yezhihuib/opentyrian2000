#!/usr/bin/env python3
"""Fresh Talon13 reconstruction observer, not an integrated engine proof.

Original sprite/palette bytes are read-only and passed to the child on stdin.
Only authored HD files, extracted production code and receipts may be persisted.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shlex
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + re.escape(name) + r'\([^;{}]*\)\s*\{', source, re.M)
    if not match:
        raise RuntimeError('Missing current production function: ' + name)
    pos = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[pos] == '{') - (source[pos] == '}')
        pos += 1
    return source[match.start():pos] + '\n'


def fnv64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return value


def reference_decode(bank, index):
    """Independent row-major decoder; no generated/production implementation."""
    assert index > 0 and 2 * index <= len(bank)
    pos = int.from_bytes(bank[(index - 1) * 2:index * 2], 'little')
    pixels, coverage = bytearray(168), bytearray(168)
    cell = 0
    for _ in range(len(bank)):
        assert pos < len(bank)
        command = bank[pos]
        pos += 1
        if command == 15:
            return bytes(pixels + coverage)
        cell += command & 15
        for _ in range(command >> 4):
            assert cell < 168 and pos < len(bank)
            pixels[cell] = bank[pos]
            coverage[cell] = 255
            cell += 1
            pos += 1
    raise AssertionError('Unterminated tile')


def original_payload(data, registry):
    """Keep all original bytes in memory, including decoded source witnesses."""
    shape = (data / 'tyrian.shp').read_bytes()
    count, = struct.unpack_from('<H', shape)
    assert count == 13
    offsets = struct.unpack_from('<13I', shape, 2)
    bank = shape[offsets[8]:offsets[9]]
    family = registry['families'][0]
    assert family['name'] == 'normal-talon'
    source = family['source_identity']
    assert len(bank) == source['bank_bytes'] == 33484
    for tile in source['tiles']:
        assert fnv64(reference_decode(bank, tile['index'])) == int(tile['source_fnv64'], 16)
    raw = (data / 'palette.dat').read_bytes()[5 * 768:6 * 768]
    assert len(raw) == 768 and max(raw) < 64
    rgb = bytes((value << 2) | (value >> 4) for value in raw)
    assert rgb[48:96].hex() == ''.join(source['palette']['rgb_hex'])
    palette = b''.join(struct.pack('<I', int.from_bytes(rgb[n:n + 3], 'big')) for n in range(0, 768, 3))
    return struct.pack('<I', len(bank)) + bank + palette


def verify_registry(root, registry):
    family = registry['families'][0]
    assert len(family['visuals']) == 13
    assert [v['visual_index'] for v in family['visuals']] == list(range(13))
    assert family['draw_semantics']['role'] == 'player_ship'
    assert family['draw_semantics']['layout'] == 'quad'
    assert family['draw_semantics']['operators'] == ['normal', 'invulnerability_blend', 'shadow']
    by_id = {item['identity']: item for item in registry['resources']}
    talon = [by_id[v['resource_identity']] for v in family['visuals']]
    for item in talon:
        raw = (root / item['path']).read_bytes()
        assert len(raw) == item['bytes'] == 172060
        assert hashlib.sha256(raw).hexdigest() == item['sha256']
        assert raw[:4] == b'HDR1' and list(struct.unpack_from('<6I', raw, 4)) == item['header_u32']
        assert fnv64(raw[28:]) == int(item['payload_fnv64'], 16)
    return talon


def resource_fixtures(temp, assets, registry, talon):
    """Corrupt authored replacements only; never write original game data."""
    for visual, item in enumerate(talon):
        raw = (assets / item['path']).read_bytes()
        for mode in ('missing', 'corrupt', 'header', 'trailing'):
            root = temp / (mode + str(visual))
            (root / 'content').mkdir(parents=True)
            for other in talon:
                target = root / other['path']
                if other is not item:
                    target.symlink_to((assets / other['path']).resolve())
                elif mode == 'corrupt':
                    damaged = bytearray(raw)
                    damaged[31] ^= 1
                    target.write_bytes(damaged)
                elif mode == 'header':
                    damaged = bytearray(raw)
                    damaged[4] ^= 1
                    target.write_bytes(damaged)
                elif mode == 'trailing':
                    target.write_bytes(raw + b'!')
    # This is a positive isolation fixture: every non-Talon family is absent.
    only = temp / 'talon-only'
    (only / 'content').mkdir(parents=True)
    for item in talon:
        (only / item['path']).symlink_to((assets / item['path']).resolve())
    (temp / 'empty').mkdir()


def child_limits():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (32 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (180, 180))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--assets', type=Path, default=ROOT / 'assets/hd/global-assets-v1')
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--sanitize', action='store_true')
    parser.add_argument('--case', default='all', choices=['all','night','guards','resources','alpha','source','pose','output','cache','underlay','transactions','finish','role','alias','reset','fade','fade_bad','fade_presave','geometry'])
    args = parser.parse_args()
    registry = json.loads((args.assets / 'registry.json').read_text())
    talon = verify_registry(args.assets, registry)
    payload = original_payload(args.data, registry)
    sources = [ROOT / 'src/render_mirror.c', ROOT / 'src/global_asset_registry.h',
               ROOT / 'src/global_talon_mirror.inc', ROOT / 'src/render_mirror.h', ROOT / 'src/sprite.c', HERE / 'global_talon_reconstruction.c',
               HERE / 'global_talon_reconstruction.py', HERE / 'global_talon_reconstruction.md']
    snapshot = {path: path.read_bytes() for path in sources}
    mirror = snapshot[ROOT / 'src/render_mirror.c'].decode()
    names = ['palette_rgb', 'blend_rgba', 'darken_rgba', 'decode_tile', 'upscale', 'cloud_shadow_rgba', 'normal15_palette', 'normal15_branch', 'normal15_index', 'normal15_channel', 'normal15_rgba', 'normal15_indices_match']
    with tempfile.TemporaryDirectory(prefix='global-talon-reconstruction-') as directory:
        temp = Path(directory)
        for path, content in snapshot.items():
            if path.suffix in ('.c', '.h', '.inc'):
                (temp / path.name).write_bytes(content)
        (temp / 'primitives.inc').write_text('\n'.join(extract(mirror, name) for name in names))
        (temp / 'pixel.inc').write_text(extract(mirror, 'render_mirror_pixel'))
        (temp / 'root.inc').write_text(extract(mirror, 'render_mirror_set_global_assets'))
        (temp / 'blend.inc').write_text(extract(mirror, 'render_mirror_sprite2_blend_pixel'))
        (temp / 'finish.inc').write_text(extract(mirror, 'render_mirror_finish'))
        (temp / 'fade.inc').write_text(extract(mirror, 'render_mirror_fade_start') + extract(mirror, 'render_mirror_fade_step'))
        (temp / 'generic.inc').write_text(extract(mirror, 'render_mirror_entity'))
        (temp / 'blitter.inc').write_text(extract(snapshot[ROOT / 'src/sprite.c'].decode(), 'blit_sprite2_blend'))
        resource_fixtures(temp, args.assets, registry, talon)
        (temp / 'feature_off.c').write_text('''#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#define SPRITE_H
#define GROUND101_MATERIAL_H
#define GAMEPLAY_HUD_METERS_H
#define RENDER_MIRROR_DISABLED
#include "render_mirror.h"
int main(void) {
 if (!render_mirror_set_global_assets("/not-read-by-feature-off")) return 1;
 if (render_mirror_global_player_ship(NULL, 0, 0, 0, 233, 0, 1, 233) != -1) return 2;
 render_mirror_global_reset();
 return 0;
}
''')
        command = shlex.split(os.environ.get('CC', 'cc'))
        command += ['-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror=implicit-function-declaration',
                    '-Wno-unused-function', '-Wno-unused-parameter', '-Wno-unused-variable',
                    '-Wno-misleading-indentation', '-I' + str(temp), '-I' + str(ROOT / 'src')]
        if args.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
        command += [str(temp / 'global_talon_reconstruction.c'), '-o', str(temp / 'observer')]
        subprocess.run(command, check=True, timeout=180, preexec_fn=child_limits)
        off_command = shlex.split(os.environ.get('CC', 'cc')) + ['-std=c99', '-Wall', '-Wextra', '-Werror',
                      '-I' + str(temp), '-I' + str(ROOT / 'src'), str(temp / 'feature_off.c'), '-o', str(temp / 'feature_off')]
        subprocess.run(off_command, check=True, timeout=60, preexec_fn=child_limits)
        subprocess.run([str(temp / 'feature_off')], check=True, timeout=10, preexec_fn=child_limits)
        env = {**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0:halt_on_error=1',
               'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'}
        result = subprocess.run([str(temp / 'observer'), str(args.assets.resolve()), str(temp), args.case],
                                input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=env, timeout=180, preexec_fn=child_limits)
        stdout, stderr = result.stdout.decode(), result.stderr.decode()
        print(stdout, end='')
        print(stderr, end='')
        receipt = {'status': 'PASS' if result.returncode == 0 else 'FAIL',
                   'scope': 'Extracted current production Talon13 observer; not integrated engine proof',
                   'original_bytes_persisted': False, 'feature_off_header_compile_and_run': 'PASS',
                   'sanitizers': 'ASan+UBSan' if args.sanitize else 'none',
                   'leak_detection': 'disabled because executor ptrace is incompatible with LeakSanitizer',
                   'case': args.case, 'returncode': result.returncode, 'stdout': stdout, 'stderr': stderr,
                   'production_helpers': names + ['render_mirror_pixel', 'render_mirror_set_global_assets', 'render_mirror_sprite2_blend_pixel', 'blit_sprite2_blend', 'render_mirror_finish', 'render_mirror_entity', 'render_mirror_fade_start', 'render_mirror_fade_step'],
                   'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(b).hexdigest() for p, b in snapshot.items()},
                   'source_unchanged_at_completion': all(p.read_bytes() == b for p, b in snapshot.items()),
                   'resource_sha256': {str(item['identity']): item['sha256'] for item in talon}}
        destination = args.receipt.resolve()
        assert ROOT not in destination.parents and args.data.resolve() not in destination.parents
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(receipt, indent=2) + '\n')
        raise SystemExit(0 if result.returncode == 0 else 1)


if __name__ == '__main__':
    main()
