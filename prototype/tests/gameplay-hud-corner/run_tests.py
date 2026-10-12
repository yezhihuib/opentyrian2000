#!/usr/bin/env python3
"""Exact-mask HUD1 corner tests; synthetic source/RGBA, no game data or art."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 'f82630507ab7f405117dc84ca70095ca04dc470a'
sys.path.insert(0, str(HERE.parent / 'gameplay-hud'))
from run_tests import checked_points
from test_renderer import fnv, extract, INDICATOR_FUNCTIONS
from test_writers import extract as extract_writer

MASK_SHA = 'dfc1e98e0d25b1a45645fc572d42396cf0407db975e44b3aefe91662255811b8'
V5_SHA = '2d4ce5ecc102b131cadee22dc28cea86e0c97ec89420a715f46274ed8a4e77a8'
OLD_CORNER = [
    '#####################', '#####################', '#####################',
    '.####################', '.####################', '................#####',
    '................#####', '................###.#', '................###.#',
    '................###.#', '................###.#', '................###.#',
    '................###.#', '................###.#', '................####.',
    '................#####',
]


def fixtures(directory):
    mask = bytearray(64000)
    for x, y in checked_points(HERE / 'approved-corner-union.spans', 6853, MASK_SHA):
        mask[y * 320 + x] = 255
    assert fnv(mask) == 0xb0f84ef16e11c6a2
    old = mask[:]
    for y, row in enumerate(OLD_CORNER, 184):
        assert len(row) == 21
        old[y * 320 + 248:y * 320 + 269] = bytes(255 if c == '#' else 0 for c in row)
    assert old.count(255) == 6667 and hashlib.sha256(old).hexdigest() == V5_SHA
    added = [i for i in range(64000) if mask[i] and not old[i]]
    assert len(added) == 186
    source = bytearray([7]) * 64000
    for x, count in [(285, 6), (296, 5)]:
        for y in range(138, 138 + count * 6, 6):
            for yy in range(y - 1, y + 6):
                for xx in range(x - 1, x + 6):
                    if not (x <= xx < x + 5 and y <= yy < y + 5):
                        source[yy * 320 + xx] = 0
    # Synthetic black cells, deliberately confined to previously unowned points.
    for i in added[:46]:
        source[i] = 0
    region = bytes(source[y * 320 + x] for y in range(184, 200) for x in range(248, 269))
    assert region.count(0) == 46 and all(source[i] for i in range(64000) if old[i])
    rgba = bytearray(4096000)
    for y in range(800):
        for x in range(1280):
            i = 4 * (y * 1280 + x)
            rgba[i:i + 4] = bytes(((x // 4 * 13 + x % 4 * 3) % 256,
                                  (y // 4 * 7 + y % 4 * 5) % 256,
                                  (x % 4 + y % 4 * 4) * 9,
                                  mask[y // 4 * 320 + x // 4]))

    def raw_for(ownership):
        image = rgba[:]
        for y in range(800):
            image[y * 1280 * 4 + 3:(y + 1) * 1280 * 4:4] = bytes(
                ownership[y // 4 * 320 + x // 4] for x in range(1280))
        header = struct.pack('<4s8I3QI', b'HUD1', 1, 320, 200, 4, 0, 0,
                             64000, 4096000, fnv(source), fnv(ownership), fnv(image), 0)
        return bytearray(header + ownership + image)

    def save(name, raw, ownership=mask):
        path = directory / name
        path.mkdir()
        (path / 'gameplay-hud-v1.hda').write_bytes(raw)
        (path / 'source.indices').write_bytes(source)
        (path / 'synthetic.mask').write_bytes(ownership)

    raw = raw_for(mask)
    save('corner', raw)
    save('legacy', raw_for(old), old)
    (directory / 'none').mkdir()
    partial = mask[:]
    partial[added[0]] = 0
    save('partial', raw_for(partial))
    wrong = mask[:]
    outside = next(i for i in range(64000) if mask[i] and not (184 <= i // 320 < 200 and 248 <= i % 320 < 269))
    wrong[outside] = 0
    wrong[0] = 255
    save('wrong-mask', raw_for(wrong))
    for name, offset in [('rgba-corrupt', 65000), ('mask-corrupt', 64),
                         ('source-pin', 36), ('mask-header', 44)]:
        corrupt = raw[:]
        corrupt[offset] ^= 1
        save(name, corrupt)
    corrupt = raw[:]
    corrupt[64064 + 4 * ((184 * 4) * 1280 + 248 * 4) + 3] = 254
    struct.pack_into('<Q', corrupt, 52, fnv(corrupt[64064:]))
    save('alpha', corrupt)
    nonbinary = mask[:]
    nonbinary[added[0]] = 128
    save('nonbinary', raw_for(nonbinary))
    outside_zero = source[:]
    outside_zero[outside] = 0
    changed_source = raw[:]
    struct.pack_into('<Q', changed_source, 36, fnv(outside_zero))
    save('outside-zero', changed_source)
    (directory / 'outside-zero/source.indices').write_bytes(outside_zero)
    return [f'-DHUD_CORNER_PIC3_FNV=UINT64_C(0x{fnv(source):016x})',
            f'-DHUD_CORNER_REGION_FNV=UINT64_C(0x{fnv(region):016x})']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    loader = (ROOT / 'src/gameplay_hud.c').read_text()
    for name, value in [('MASK', 'b0f84ef16e11c6a2'), ('PIC3', '14c1441f3d5dc0e2'),
                        ('REGION', 'ca5548b4cdd8767a')]:
        assert f'#define HUD_CORNER_{name}_FNV UINT64_C(0x{value})' in loader
    common = ['palette_rgb', 'upscale', 'render_mirror_unsupported']
    helpers = ['components_owned', 'components_source_matches', 'components_cached_indices_match',
               'components_clear_cached', 'components_reset', 'components_check_mode',
               'components_start', 'components_begin', 'render_mirror_hud_shield_wiped',
               'render_mirror_hud_shield_drawn', 'components_compose', 'hud_source_matches',
               'hud_cached_indices_match', 'hud_clear_cached', 'hud_frame_reset',
               'render_mirror_hud_reset', 'render_mirror_hud_shutdown', 'hud_runtime_compatible',
               'hud_check_mode', 'render_mirror_hud_start', 'render_mirror_hud_suspend',
               'hud_begin', 'hud_compose', 'render_mirror_begin', 'render_mirror_finish',
               'render_mirror_fade_start', 'render_mirror_fade_step', 'render_mirror_present',
               'render_mirror_release_texture']
    with tempfile.TemporaryDirectory(prefix='hud-corner-') as temp:
        path = Path(temp)
        guards = fixtures(path)
        flags = ['-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Wno-unused-parameter',
                 '-Wno-unused-variable', '-Wno-unused-function', '-Wno-misleading-indentation',
                 '-I' + str(ROOT / 'src'), '-I' + str(path)] + guards
        if args.sanitize:
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
        cc = [os.environ.get('CC', 'cc')]
        environment = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                           UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        executable = path / 'loader-test'
        subprocess.run(cc + flags + [str(HERE / 'test_loader.c'), str(ROOT / 'src/gameplay_hud.c'),
                                     '-o', str(executable)], check=True)
        subprocess.run([str(executable), str(path)], check=True, env=environment)
        # Re-pin only the synthetic full picture to make source-zero rejection
        # independent of the full checksum. A separate build exercises the
        # region identity with the exact unchanged full-picture checksum.
        for name, changed in [('outside-zero', 'PIC3'), ('corner', 'REGION')]:
            special_flags = [f for f in flags if not f.startswith(f'-DHUD_CORNER_{changed}_FNV=')]
            value = fnv((path / name / 'source.indices').read_bytes()) if changed == 'PIC3' else 0
            special_flags += [f'-DHUD_CORNER_{changed}_FNV=UINT64_C(0x{value:016x})']
            executable = path / ('reject-' + name)
            subprocess.run(cc + special_flags + [str(HERE / 'test_loader.c'), str(ROOT / 'src/gameplay_hud.c'),
                                                 '-o', str(executable)], check=True)
            subprocess.run([str(executable), str(path / name), 'reject-capture'], check=True, env=environment)
        snippets = []
        for filename, name in [('sprite.c', 'blit_sprite_hv_unsafe'),
                               ('fonthand.c', 'JE_outText'), ('mainint.c', 'JE_drawTextWindow')]:
            snippets.append(extract_writer((ROOT / 'src' / filename).read_text(), name))
        (path / 'message-writers.inc').write_text('\n'.join(snippets))
        results = {}
        for variant in ['baseline', 'candidate']:
            renderer = (ROOT / 'src/render_mirror.c').read_text() if variant == 'candidate' else subprocess.check_output(
                ['git', 'show', BASE + ':src/render_mirror.c'], cwd=ROOT, text=True)
            (path / 'production.inc').write_text('\n'.join(extract(renderer, name)
                for name in common + INDICATOR_FUNCTIONS + helpers))
            source = ROOT / 'src/gameplay_hud.c'
            extra = []
            if variant == 'baseline':
                source = path / 'old-gameplay-hud.c'
                source.write_text(subprocess.check_output(['git', 'show', BASE + ':src/gameplay_hud.c'], cwd=ROOT, text=True))
                extra = ['-DCORNER_BASELINE']
            executable = path / variant
            subprocess.run(cc + flags + extra + [str(HERE / 'test_renderer.c'), str(source),
                str(ROOT / 'src/gameplay_hud_components.c'), str(ROOT / 'src/gameplay_hud_indicators.c'),
                '-o', str(executable)], check=True)
            results[variant] = subprocess.check_output([str(executable), str(path)], env=environment, text=True)
            print(variant + ': ' + results[variant].strip())
        before = re.search(r'LEGACY ([0-9a-f]+)', results['baseline']).group(1)
        after = re.search(r'LEGACY ([0-9a-f]+)', results['candidate']).group(1)
        assert before == after, (before, after)
        print('Exact old-mask output/cache/fade digest equals published base; no-corner behavior unchanged.')


if __name__ == '__main__':
    main()
