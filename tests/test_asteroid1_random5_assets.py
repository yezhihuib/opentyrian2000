#!/usr/bin/env python3
"""Bounded extracted-production tests for the one-image random base5 family.

Reads only the named ten-family harness/helper, production sources, one HDA,
external newshd.shp and the three exact tyrian.hdt records. No other tests or
private projection are opened. Actual-engine random-spawn pairs are separate.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--sdl-include', action='append', default=[])
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('ten_harness', ROOT / 'tests/test_asteroid1_ten_assets.py')
    ten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ten)
    source = (ROOT / 'src/render_mirror.c').read_text()
    original = (ROOT / 'src/asteroid1_ten_mirror.inc').read_text()
    family = (ROOT / 'src/asteroid1_random5_mirror.inc').read_text()
    scopes = ten.extract(source, 'asteroid1_level_scope') + ten.extract(source, 'asteroid1_scope')
    shared = ten.extract(original, 'asteroid1_stamp') + '#include "asteroid1_source_snapshot.inc"\n' + ten.extract(original, 'asteroid1_record_stamp')
    code = ten.HARNESS.replace('asteroid1_', 'asteroid_random5_').replace('asteroid_random5_scope', 'asteroid1_scope')
    code = code.replace('t=444;t<=453', 't=135;t<=137').replace('{444,0,0,0', '{135,0,0,1')
    code = code.replace('k<10', 'k<3').replace('accepted==28&&logged==28', 'accepted==12&&logged==12')
    code = code.replace('source,31,', 'source,5,').replace('source,32,', 'source,6,')
    code = code.replace('c.type=443;', 'c.type=134;').replace('c.type=444;', 'c.type=135;')
    code = code.replace('c.size=1;assert(!asteroid_random5_draw', 'c.size=0;assert(!asteroid_random5_draw')
    code = code.replace('));c.size=0;', '));c.size=1;')
    code = code.replace('source,5,1,0,&c)', 'source,5,2,0,&c)')
    code = code.replace('enemyDat[444].egraphic[19]=99;assert(!asteroid_random5_source(source));enemyDat[444].egraphic[19]=0;',
                        'for(unsigned i=135;i<=137;i++){enemyDat[i].egraphic[19]=99;assert(!asteroid_random5_source(source));enemyDat[i].egraphic[19]=0;}'
                        'for(unsigned i=135;i<=137;i++){enemyDat[i].ymove++;assert(!asteroid_random5_source(source));enemyDat[i].ymove--;}')
    code = code.replace('if(strcmp(argv[4],"reject")==0){',
                        'assert(c.type==135&&c.pool_slot==0&&c.availability==0&&c.size==1&&c.static_animation);\n'
                        ' if(strcmp(argv[4],"reject")==0){assert(!asteroid_random5_family_ready());')
    code = code.replace('member[3].rgba', 'member[0].rgba').replace('28-call geometry', '12-call geometry')
    extra = r'''
 c.availability=2;assert(asteroid_random5_draw(&surface,100,80,source,5,0,0,&c));c.availability=0;
 c.availability=3;assert(!asteroid_random5_draw(&surface,100,80,source,5,0,0,&c));c.availability=0;
 c.type=138;assert(!asteroid_random5_draw(&surface,100,80,source,5,0,0,&c));c.type=135;
 assert(!asteroid_random5_draw(&surface,100,80,source,5,0,-1,&c));
 assert(!asteroid_random5_draw(&surface,100,80,source,5,0,256,&c));
 assert(!asteroid_random5_draw(&surface,100,80,source,5,0,0,NULL));
 asteroid_hd_enabled=false;assert(!asteroid_random5_draw(&surface,100,80,source,5,0,0,&c));asteroid_hd_enabled=true;
 surface.pitch=321;assert(!asteroid_random5_draw(&surface,100,80,source,5,0,0,&c));surface.pitch=320;
 format.format=SDL_PIXELFORMAT_ARGB8888;assert(!asteroid_random5_draw(&surface,100,80,source,5,0,0,&c));format.format=SDL_PIXELFORMAT_INDEX8;
 source.size--;assert(!asteroid_random5_source(source));source.size++;
 for(unsigned i=0;i<3;i++) {
  c.type=135+i;
  assert(asteroid_random5_draw(&surface,0,-13,source,5,0,255,&c));
  assert(asteroid_random5_draw(&surface,308,199,source,5,20,0,&c));
 }
 c.type=135;
'''
    code = code.replace('asteroid_random5_shutdown();assert(asteroid_random5_family_ready());',
                        'asteroid_random5_shutdown();assert(asteroid_random5_family_ready());' + extra)
    code = code.replace('@SCOPE@', scopes).replace('@FAMILY@', shared + family)
    harness = args.out / 'harness.c'
    harness.write_text(code)
    raw = (args.data / 'tyrian.hdt').read_bytes()
    start = struct.unpack_from('<i', raw)[0] + 14 + 1638 * 80 + 61 * 82 + 55 * 37 + 7 * 37 + 19 * 41 + 38 * 86 + 12 * 37
    recordfile = args.out / 'original-random5-records.bin'
    recordfile.write_bytes(raw[start + 135 * 77:start + 138 * 77])
    file = PACK / 'enemy-newshd-5-8.hda'
    fixtures = args.out / 'fixtures'
    fixtures.mkdir()
    variants = []
    for kind in ['missing', 'payload', 'magic', 'role', 'density', 'width', 'height', 'anchor-x', 'anchor-y', 'short', 'extra', 'fifo', 'directory']:
        directory = fixtures / kind
        directory.mkdir()
        dest = directory / file.name
        if kind == 'missing':
            pass
        elif kind == 'fifo':
            os.mkfifo(dest)
        elif kind == 'directory':
            dest.mkdir()
        else:
            data = bytearray(file.read_bytes())
            if kind == 'payload': data[40] ^= 1
            elif kind == 'magic': data[:4] = b'NOPE'
            elif kind in ['role', 'density', 'width', 'height', 'anchor-x', 'anchor-y']:
                offset = dict(role=4, density=8, width=12, height=16, **{'anchor-x': 20, 'anchor-y': 24})[kind]
                struct.pack_into('<I', data, offset, 1)
            elif kind == 'short': data = data[:-1]
            elif kind == 'extra': data += b'X'
            dest.write_bytes(data)
        variants.append(directory)
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
        for directory, expected in [(PACK, 'accept')] + [(directory, 'reject') for directory in variants]:
            subprocess.run([str(exe), str(args.data / 'newshd.shp'), str(recordfile), str(directory), expected], check=True, timeout=10,
                           env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0'})
        runs.append(dict(mode=mode, positive=1, negative=len(variants), binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    result = dict(runs=runs, source_sha256=hashlib.sha256(family.encode()).hexdigest(),
                  peak_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
                  leak_sanitizer=False, scope='Extracted production full-three-record source guard, one coherent resource, twelve ordered quadrant calls, clipping/mode/format/filter/warm corruption checks. Actual-engine random-spawn pairs are separate.')
    (args.out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
