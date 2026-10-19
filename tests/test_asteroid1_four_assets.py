#!/usr/bin/env python3
"""Bounded extracted-production tests for the optional event12 four-rock family.

Reads only the named ten-family harness/helper, production sources, four HDA
files and external newshd.shp/tyrian.hdt. No other test payload is imported.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import resource
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'assets/hd/packs/asteroid1-ten-v1'
BASES = [45, 47, 7, 9]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sdl-include', action='append', default=[])
    p.add_argument('--sanitize', action='store_true')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('ten_harness', ROOT / 'tests/test_asteroid1_ten_assets.py')
    ten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ten)
    source = (ROOT / 'src/render_mirror.c').read_text()
    original = (ROOT / 'src/asteroid1_ten_mirror.inc').read_text()
    family = (ROOT / 'src/asteroid1_four_mirror.inc').read_text()
    scopes = ten.extract(source, 'asteroid1_level_scope') + ten.extract(source, 'asteroid1_scope')
    shared = ten.extract(original, 'asteroid1_stamp') + '#include "asteroid1_source_snapshot.inc"\n' + ten.extract(original, 'asteroid1_record_stamp')
    code = ten.HARNESS.replace('asteroid1_', 'asteroid4_').replace('asteroid4_scope', 'asteroid1_scope')
    code = code.replace('t=444;t<=453', 't=440;t<=443').replace('{444,0,0,0', '{440,0,0,1')
    code = code.replace('k<10', 'k<4').replace('accepted==28&&logged==28', 'accepted==16&&logged==16')
    code = code.replace('source,31,', 'source,45,').replace('source,32,', 'source,46,')
    code = code.replace('c.type=443;', 'c.type=439;').replace('c.type=444;', 'c.type=440;')
    code = code.replace('c.size=1;assert(!asteroid4_draw', 'c.size=0;assert(!asteroid4_draw')
    code = code.replace('));c.size=0;', '));c.size=1;')
    code = code.replace('source,45,1,0,&c)', 'source,45,2,0,&c)')
    code = code.replace('enemyDat[444].egraphic[19]=99;assert(!asteroid4_source(source));enemyDat[444].egraphic[19]=0;',
                        'for(unsigned i=440;i<=443;i++){enemyDat[i].egraphic[19]=99;assert(!asteroid4_source(source));enemyDat[i].egraphic[19]=0;}')
    code = code.replace('if(strcmp(argv[4],"reject")==0){',
                        'assert(c.type==440&&c.pool_slot==0&&c.availability==0&&c.size==1&&c.static_animation);\n'
                        ' if(strcmp(argv[4],"reject")==0){assert(!asteroid4_family_ready());')
    code = code.replace('28-call geometry', '16-call geometry')
    code = code.replace('@SCOPE@', scopes).replace('@FAMILY@', shared + family)
    harness = args.out / 'harness.c'
    harness.write_text(code)
    raw = (args.data / 'tyrian.hdt').read_bytes()
    start = struct.unpack_from('<i', raw)[0] + 14 + 1638 * 80 + 61 * 82 + 55 * 37 + 7 * 37 + 19 * 41 + 38 * 86 + 12 * 37
    recordfile = args.out / 'original-four-records.bin'
    recordfile.write_bytes(raw[start + 440 * 77:start + 444 * 77])
    files = [PACK / f'enemy-newshd-{base}-8.hda' for base in BASES]
    fixtures = args.out / 'fixtures'
    fixtures.mkdir()
    specs = [(f.name, k) for f in files for k in ['missing', 'payload']]
    specs += [(files[0].name, k) for k in ['magic', 'role', 'density', 'width', 'height', 'anchor-x', 'anchor-y', 'short', 'extra', 'fifo', 'directory']]
    variants = []
    for number, (target, kind) in enumerate(specs):
        d = fixtures / f'{number:02d}-{kind}'
        d.mkdir()
        for f in files:
            dest = d / f.name
            if f.name != target:
                dest.symlink_to(f)
            elif kind == 'missing':
                continue
            elif kind == 'fifo':
                os.mkfifo(dest)
            elif kind == 'directory':
                dest.mkdir()
            else:
                b = bytearray(f.read_bytes())
                if kind == 'payload': b[40] ^= 1
                elif kind == 'magic': b[:4] = b'NOPE'
                elif kind in ['role', 'density', 'width', 'height', 'anchor-x', 'anchor-y']:
                    offset = dict(role=4, density=8, width=12, height=16, **{'anchor-x': 20, 'anchor-y': 24})[kind]
                    struct.pack_into('<I', b, offset, 1)
                elif kind == 'short': b = b[:-1]
                elif kind == 'extra': b += b'X'
                dest.write_bytes(b)
        variants.append(d)
    flags = ['-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-I' + str(ROOT / 'src')]
    flags += ['-I' + path for path in args.sdl_include]
    if not args.sdl_include:
        flags += subprocess.check_output(['pkg-config', '--cflags', 'sdl2'], text=True).split()
    runs = []
    for mode in ['optimized'] + (['asan-ubsan'] if args.sanitize else []):
        exe = args.out / mode
        compiler = ['cc', *flags, '-O2']
        if mode == 'asan-ubsan': compiler += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
        def compile_limits(): resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024**2,) * 2)
        subprocess.run([*compiler, str(harness), '-o', str(exe)], check=True, preexec_fn=compile_limits)
        for directory, expected in [(PACK, 'accept')] + [(d, 'reject') for d in variants]:
            subprocess.run([str(exe), str(args.data / 'newshd.shp'), str(recordfile), str(directory), expected], check=True, timeout=10,
                           env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0'})
        runs.append(dict(mode=mode, positive=1, negative=len(variants), binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    result = dict(runs=runs, source_sha256=hashlib.sha256(family.encode()).hexdigest(),
                  peak_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
                  leak_sanitizer=False, scope='Extracted production four-family scope/source/loader/16-quadrant geometry. Actual engine pairs are separate.')
    (args.out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
