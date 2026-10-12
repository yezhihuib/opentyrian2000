#!/usr/bin/env python3
"""Build and test asset-only HUD loading using generated, non-artwork fixtures."""
import argparse
import hashlib
import os
import re
from pathlib import Path
import shlex
import subprocess
import tempfile


def checked_points(path, count, digest):
    """Reconstruct an independent coordinate-only audit fixture, never game data."""
    mask = bytearray(64000)
    for line in path.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        y, start, end = map(int, line.split())
        assert 0 <= y < 200 and 0 <= start < end <= 320, (path, line)
        for x in range(start, end):
            assert not mask[y * 320 + x], (path, 'duplicate', x, y)
            mask[y * 320 + x] = 255
    assert mask.count(255) == count, (path, 'count')
    assert hashlib.sha256(mask).hexdigest() == digest, (path, 'coordinate hash')
    return [(i % 320, i // 320) for i, value in enumerate(mask) if value]


def write_audit_fixtures(here, build):
    fixtures = [
        ('approved_points', 'approved-rails.spans', 310,
         '903328448558ea0a8b7ea1e895339602736664bad73b0828b8ace4b3732263d2'),
        ('rejected_points', 'rejected-candidates.spans', 261,
         'f318812df425dd11419446752272f32917ee97f2c4e8541893c7bc16ed0fe10e'),
    ]
    lines = ['/* Generated from separately hash-checked coordinate-only fixtures. */']
    sets = []
    for name, filename, count, digest in fixtures:
        points = checked_points(here / filename, count, digest)
        sets.append(set(points))
        lines += ['static const uint16_t ' + name + '[][2] = {',
                  ',\n'.join('    {%d, %d}' % point for point in points), '};']
    assert not sets[0] & sets[1]
    (build / 'audit_fixtures.h').write_text('\n'.join(lines) + '\n')


def check_production_allowlist(root, here):
    """Pin the production rectangle union to the independent audited coordinates."""
    source = (root / 'src/gameplay_hud.c').read_text()
    match = re.search(r'static const uint16_t spans\[\]\[4\] = \{(.*?)\n\t\};',
                      source, re.S)
    assert match, 'missing finite expansion span table'
    mask = bytearray(64000)
    for rectangle in re.findall(r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}',
                                match.group(1)):
        x0, y0, x1, y1 = map(int, rectangle)
        assert 0 <= x0 < x1 <= 320 and 0 <= y0 < y1 <= 200
        for y in range(y0, y1):
            for x in range(x0, x1):
                assert not mask[y * 320 + x], ('overlapping expansion spans', x, y)
                mask[y * 320 + x] = 255
    points = checked_points(here / 'approved-rails.spans', 310,
                            '903328448558ea0a8b7ea1e895339602736664bad73b0828b8ace4b3732263d2')
    assert {(i % 320, i // 320) for i, value in enumerate(mask) if value} == set(points)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true', help='Enable ASan and UBSan')
    parser.add_argument('--leak-check', action='store_true', help='Enable LeakSanitizer (unsupported under ptrace)')
    parser.add_argument('--cc', default=os.environ.get('CC', 'cc'))
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    check_production_allowlist(root, here)
    with tempfile.TemporaryDirectory(prefix='gameplay-hud-tests-') as temporary:
        build = Path(temporary)
        write_audit_fixtures(here, build)
        flags = ['-std=c99', '-O1' if args.sanitize else '-O2', '-g', '-Wall', '-Wextra',
                 '-Werror', '-Wpedantic', '-I', str(root / 'src'), '-I', str(here),
                 '-I', str(build)]
        if args.sanitize:
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        cc = shlex.split(args.cc)
        subprocess.run(cc + flags + ['-include', str(here / 'allocation_probe.h'),
                       '-Dmalloc=gameplay_hud_test_malloc', '-Dfree=gameplay_hud_test_free',
                       '-c', str(root / 'src/gameplay_hud.c'), '-o', str(build / 'loader.o')], check=True)
        subprocess.run(cc + flags + [str(here / 'test_gameplay_hud.c'), str(build / 'loader.o'),
                       '-o', str(build / 'test_gameplay_hud')], check=True)
        pack = build / 'synthetic-pack'
        pack.mkdir()
        environment = os.environ.copy()
        if args.sanitize:
            environment['ASAN_OPTIONS'] = f'detect_leaks={int(args.leak_check)}:halt_on_error=1'
            environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
        subprocess.run([str(build / 'test_gameplay_hud'), str(pack)], check=True, env=environment)


if __name__ == '__main__':
    main()
