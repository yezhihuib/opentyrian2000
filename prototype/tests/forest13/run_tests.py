#!/usr/bin/env python3
"""Portable forest loader/sampler tests. No SDL, game, images, or third-party Python.

Synthetic checks run with only the five existing dependency source/header files.
Optional frozen checks also verify the approved bundle and all13 selected HDAs.
All compilation and malformed fixtures are isolated under --output/a tempdir.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shlex
import shutil
import struct
import subprocess
import tempfile

IDS = (211, 212, 213, 215, 221, 222, 223, 224, 225, 231, 232, 233, 234)
ATLAS, TILE, HEADER, PAYLOAD = 2752512, 43008, 188, 3311616
MARKER = b'forest13-coupled-original-v1\n'
HERE = Path(__file__).resolve().parent


def fnv(blob):
    h = 14695981039346656037
    for b in blob:
        h = ((h ^ b) * 1099511628211) & ((1 << 64) - 1)
    return h


def make_synthetic(root):
    root.mkdir()
    atlas = bytearray(ATLAS)
    for y in range(896):
        for x in range(768):
            at = 4 * (y * 768 + x)
            atlas[at:at + 4] = bytes(((x ^ y) & 255, (x // 3 + 5 * y) & 255,
                                     (7 * x + y // 2) & 255, 255))
    payload = atlas
    records = []
    for i, identity in enumerate(IDS):
        source = bytearray(TILE * 4)
        for n in range(TILE):
            source[n * 4:n * 4 + 4] = bytes(((n + 31 * i) & 255,
                (3 * n + i) & 255, (n // 17 + 11 * i) & 255, 255))
        (root / f'terrain-shapesz-{identity}-8.hda').write_bytes(
            b'HDR1' + struct.pack('<6I', 2010000 + identity, 8, 24, 28, 0, 0) + source)
        records.append((identity, 336 + i, len(payload), fnv(source)))
        payload.extend(bytes((n + 17 * i) & 255 for n in range(TILE)))
    assert len(payload) == PAYLOAD
    header = b'FCANAT1\0' + struct.pack('<6I', 1, 13, 768, 896, 8, PAYLOAD)
    header += b''.join(struct.pack('<3I', 201, identity, offset)
                       for identity, _, offset, _ in records)
    blob = header + payload
    assert len(header) == HEADER and len(blob) == HEADER + PAYLOAD
    (root / 'forest13-world-material.fcan').write_bytes(blob)
    (root / 'forest13.policy').write_bytes(MARKER)
    lines = ['/* Test-only synthetic contract; never install as production art. */',
             '#define FOREST13_BUNDLE_RECORD_COUNT 13u',
             '#define FOREST13_BUNDLE_HEADER_BYTES 188u',
             '#define FOREST13_BUNDLE_PAYLOAD_BYTES 3311616u',
             '#define FOREST13_BUNDLE_FILE_BYTES 3311804u',
             f'#define FOREST13_BUNDLE_FNV64 UINT64_C(0x{fnv(blob):016x})',
             'static const Forest13Record forest13_records[13]={']
    lines += [f' {{{i}u,{s}u,{o}u,UINT64_C(0x{h:016x})}},' for i, s, o, h in records]
    lines.append('};')
    (root / 'forest13_bundle_index.h').write_text('\n'.join(lines) + '\n')
    return root


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--src', type=Path, default=HERE.parents[2] / 'src', help='forest module source directory')
    p.add_argument('--reference-src', type=Path, required=True,
                   help='existing ground101/world_material source directory, read only')
    p.add_argument('--output', type=Path, help='new output directory outside source')
    p.add_argument('--frozen-bundle-dir', type=Path)
    p.add_argument('--frozen-sources', type=Path)
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--leak-check', action='store_true', help='enable LSan on hosts that support it')
    a = p.parse_args()
    if bool(a.frozen_bundle_dir) != bool(a.frozen_sources):
        p.error('supply both frozen input options, or neither')
    module, reference = a.src.resolve(), a.reference_src.resolve()
    if a.output:
        root = a.output.resolve()
        if a.output.is_symlink() or root == module or root == reference or \
                module in root.parents or reference in root.parents:
            p.error('output must be a fresh directory outside source trees')
        root.mkdir(parents=True, exist_ok=False)
    else:
        root = Path(tempfile.mkdtemp(prefix='forest13-tests-'))
    compiler = shlex.split(os.environ.get('CC', 'cc'))
    flags = ['-std=c99', '-O2', '-Wall', '-Wextra', '-Werror', '-DFOREST13_MATERIAL_TEST']
    if a.sanitize:
        flags += ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        # Avoid distro PIE/ASan shadow-address collisions; no linker wrapping.
        if os.name == 'posix':
            flags += ['-fno-pie', '-no-pie']
    env = dict(os.environ)
    if a.sanitize:
        env['ASAN_OPTIONS'] = f'detect_leaks={int(a.leak_check)}:halt_on_error=1'
        env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
    receipt = {'status': 'running', 'sanitized': a.sanitize, 'leak_check': a.leak_check, 'cases': {}, 'skipped': []}

    def compile_profile(name, contract, test_name):
        stage = root / ('compile-' + name)
        stage.mkdir()
        for filename in ('forest13_material.c', 'forest13_material.h'):
            shutil.copyfile(module / filename, stage / filename)
        for filename in ('ground101_material.h', 'world_material.h', 'world_material.c',
                         'world_material_fast.h', 'world_material_fast.c'):
            shutil.copyfile(reference / filename, stage / filename)
        shutil.copyfile(contract, stage / 'forest13_bundle_index.h')
        (stage / 'game_probe.h').write_text('#include <stdint.h>\n#include <stddef.h>\n'
            'uint64_t game_probe_hash(uint64_t,const void *,size_t);\n')
        (stage / 'alloc_probe.h').write_text('#include <stddef.h>\n'
            'void *forest13_test_malloc(size_t);\nvoid forest13_test_free(void *);\n')
        cmd = compiler + flags + ['-I' + str(stage)]
        io_flags = ['-Dfread=forest13_test_fread', '-Dferror=forest13_test_ferror'] \
            if test_name == 'validate_loader.c' else []
        subprocess.run(cmd + io_flags + ['-Dmalloc=forest13_test_malloc', '-Dfree=forest13_test_free',
            '-include', str(stage / 'alloc_probe.h'), '-c', str(stage / 'forest13_material.c'),
            '-o', str(stage / 'forest.o')], check=True)
        exe = stage / 'check-forest'
        subprocess.run(cmd + [str(stage / 'forest.o'), str(stage / 'world_material.c'),
            str(stage / 'world_material_fast.c'), str(HERE / test_name), '-o', str(exe)], check=True)
        return exe

    synthetic = make_synthetic(root / 'synthetic')
    exe = compile_profile('synthetic-loader', synthetic / 'forest13_bundle_index.h', 'validate_loader.c')

    def suite(tag, exe, bundle_dir, sources):
        blob = (bundle_dir / 'forest13-world-material.fcan').read_bytes()
        assert len(blob) == HEADER + PAYLOAD
        pack = root / (tag + '-pack')
        pack.mkdir()
        marker, sidecar = pack / 'forest13.policy', pack / 'forest13-world-material.fcan'

        def clear(path):
            if path.is_symlink() or path.is_file() or path.exists() and not path.is_dir():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

        def run(name, data=blob, declaration=MARKER, declared=True, policy=True,
                ready=False, alloc=0, mismatch=0, source_mode=0, lower=True,
                allocation_failure=False, special=None, directory=None, relocate=False):
            clear(marker); clear(sidecar)
            if declaration is not None:
                marker.write_bytes(declaration)
            if data is not None:
                sidecar.write_bytes(data)
            if special:
                special(marker, sidecar)
            moved = root / (tag + "-renamed-moved-pack")
            if relocate:
                pack.rename(moved)
                directory = moved
            result = subprocess.run([str(exe), str(pack if directory is None else directory),
                str(sources), str(int(declared)), str(int(policy)), str(int(ready)), str(alloc),
                str(mismatch), str(source_mode), str(int(lower)), str(int(allocation_failure))],
                capture_output=True, text=True, env=env, timeout=20)
            if relocate:
                moved.rename(pack)
            key = tag + '/' + name
            if result.returncode:
                raise AssertionError((key, result.returncode, result.stdout, result.stderr))
            receipt['cases'][key] = result.stdout.strip()

        run('valid', ready=True, alloc=1)
        # An explicit lower=false variant proves no allocation or callback.
        run('lower-unavailable', lower=False)
        run('allocation-failure', alloc=1, allocation_failure=True)
        run('marker-read-error', policy=False, source_mode=4)
        run('header-read-error', source_mode=5)
        run('payload-read-error', alloc=1, source_mode=6)
        for name, data in [('valid', blob), ('missing', None), ('bad', b'bad')]:
            run('absent-marker-' + name, data=data, declaration=None, declared=False, policy=False)
        for n in range(len(MARKER)):
            run('marker-truncate-' + str(n), declaration=MARKER[:n], policy=False)
        for n in range(len(MARKER)):
            bad = bytearray(MARKER); bad[n] ^= 1
            run('marker-byte-' + str(n), declaration=bad, policy=False)
        for name, data in [('extra', MARKER + b'\0'), ('oversized', MARKER * 32768),
                           ('unknown-version', MARKER.replace(b'v1', b'v2'))]:
            run('marker-' + name, declaration=data, policy=False)
        run('marker-directory', declaration=None, policy=False,
            special=lambda marker, _: marker.mkdir())
        if hasattr(os, 'mkfifo'):
            run('marker-fifo', declaration=None, policy=False,
                special=lambda marker, _: os.mkfifo(marker))
            run('bundle-fifo', data=None, special=lambda _, sidecar: os.mkfifo(sidecar))
        if hasattr(os, 'symlink'):
            run('marker-dangling-link', declaration=None, policy=False,
                special=lambda marker, _: marker.symlink_to('missing-declaration'))
            run('marker-link-loop', declaration=None, policy=False,
                special=lambda marker, _: marker.symlink_to(marker.name))
            run('marker-valid-link', declaration=None, policy=False,
                special=lambda marker, _: marker.symlink_to(bundle_dir / 'forest13.policy'))
        if hasattr(os, 'geteuid') and os.geteuid() != 0:
            run('marker-unreadable', policy=False, special=lambda marker, _: marker.chmod(0))
            run('bundle-unreadable', special=lambda _, sidecar: sidecar.chmod(0))
        else:
            receipt['skipped'].append(tag + ': permission-denial tests require a non-root POSIX user')
        run('empty-directory', directory='', declared=False, policy=False)
        run('overlong-directory', directory='a' * 1100, declared=True, policy=False)
        for name, data in [('missing', None), ('empty', b''), ('short-header', blob[:31]),
                           ('short-records', blob[:187]), ('short-payload', blob[:-1]),
                           ('extra-byte', blob + b'\0')]:
            run('bundle-' + name, data=data)
        run('bundle-directory', data=None, special=lambda _, sidecar: sidecar.mkdir())
        for off in range(8):
            bad = bytearray(blob); bad[off] ^= 1
            run('magic-byte-' + str(off), data=bad)
        for off, name, values in [(8, 'version', (0, 2, 0xffffffff)),
                (12, 'count', (0, 12, 14, 0xffffffff)), (16, 'width', (0, 767, 769, 0xffffffff)),
                (20, 'height', (0, 895, 897, 0xffffffff)), (24, 'density', (0, 4, 7, 9, 0xffffffff)),
                (28, 'payload-size', (0, PAYLOAD - 1, PAYLOAD + 1, 0xffffffff))]:
            for value in values:
                bad = bytearray(blob); struct.pack_into('<I', bad, off, value)
                run(f'header-{name}-{value}', data=bad)
        for i, identity in enumerate(IDS):
            for field, value in ((0, 101), (4, IDS[(i + 1) % 13]), (8, ATLAS + i * TILE + 1),
                                 (8, 0xffffffff), (8, 0)):
                bad = bytearray(blob); struct.pack_into('<I', bad, 32 + i * 12 + field, value)
                run(f'record-{identity}-field-{field}-{value}', data=bad)
            bad = bytearray(blob); bad[HEADER + ATLAS + i * TILE] ^= 1
            run('mask-corrupt-' + str(identity), data=bad, alloc=1)
            for mode, name in [(1, 'missing'), (2, 'rgb-mismatch'), (3, 'nonopaque')]:
                run(f'source-{identity}-{name}', alloc=1, mismatch=identity, source_mode=mode)
        bad = bytearray(blob); bad[32:44], bad[44:56] = blob[44:56], blob[32:44]
        run('record-order', data=bad)
        for name, off in [('atlas-rgb', HEADER), ('atlas-alpha', HEADER + 3),
                          ('last-atlas-alpha', HEADER + ATLAS - 1), ('last-mask', len(blob) - 1)]:
            bad = bytearray(blob); bad[off] ^= 1
            run('payload-corrupt-' + name, data=bad, alloc=1)
        run('renamed-pack', ready=True, alloc=1, relocate=True)
        receipt[tag + '_bundle_sha256'] = hashlib.sha256(blob).hexdigest()

    suite('synthetic', exe, synthetic, synthetic)
    sampler = compile_profile('synthetic-sampler', synthetic / 'forest13_bundle_index.h', 'test_sampler.c')
    result = subprocess.run([str(sampler), str(synthetic)], check=True, capture_output=True,
                            text=True, env=env, timeout=180)
    receipt['sampler'] = result.stdout.strip()
    print(result.stdout.strip())
    if a.frozen_bundle_dir:
        frozen = a.frozen_bundle_dir.resolve()
        exe = compile_profile('frozen-loader', frozen / 'forest13_bundle_index.h', 'validate_loader.c')
        suite('frozen', exe, frozen, a.frozen_sources.resolve())
    receipt['status'] = 'passed'
    (root / 'test-results.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'PASS {len(receipt["cases"])} isolated loader cases; results: {root / "test-results.json"}')
    for skip in receipt['skipped']:
        print('SKIP', skip)


if __name__ == '__main__':
    main()
