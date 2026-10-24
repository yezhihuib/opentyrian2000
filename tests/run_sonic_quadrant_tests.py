#!/usr/bin/env python3
"""Bounded, portable extracted-production Sonic quadrant regression tests.

Usage: python3 tests/run_sonic_quadrant_tests.py --data /path/to/original/data \
  --out /tmp/sonic-quadrant-results --sanitize --mutants

Only a C compiler and Python standard library are needed. Private original data
is never copied into the repository. --art selects a directory containing the
four authored bullet-{105,106,124,125}-8.hda files. By default the new artwork's
output directory is used. --synthetic-art is a clearly labeled loader-only smoke
test, not an authored-art acceptance result. The game is never launched.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
IDS = (105, 106, 124, 125)
PREVIOUS = (6, 44, 73, 63, 82, 16, 54, 130, 131, 149, 150, 223, 224, 242, 243, 143, 144)
FNV = {105: 0x66cdc314034152a6, 106: 0xee609a977010a3e0,
       124: 0x836f9ec6407ea3aa, 125: 0xbad7de0256394e9c}
SHA = lambda b: hashlib.sha256(b).hexdigest()


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + re.escape(name) + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, 'Missing production function: ' + name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def bank_from(path):
    raw = path.read_bytes()
    count = struct.unpack_from('<H', raw)[0]
    offsets = list(struct.unpack_from('<' + str(count) + 'I', raw, 2)) + [len(raw)]
    assert count >= 8 and offsets == sorted(offsets)
    assert offsets[0] >= 2 + 4 * count and offsets[-1] == len(raw)
    return raw[offsets[7]:offsets[8]], SHA(raw)


def decode(bank, index):
    assert index > 0 and 2 * index <= len(bank)
    pos = struct.unpack_from('<H', bank, 2 * (index - 1))[0]
    cell, colors, coverage = 0, bytearray(168), bytearray(168)
    for _ in range(len(bank)):
        assert pos < len(bank), 'Truncated RLE'
        code = bank[pos]
        pos += 1
        if code == 15:
            return bytes(colors + coverage)
        cell += code & 15
        for _ in range(code >> 4):
            assert 0 <= cell < 168 and not coverage[cell] and pos < len(bank)
            colors[cell], coverage[cell] = bank[pos], 255
            pos += 1
            cell += 1
    raise AssertionError('Unterminated RLE')


def fnv(raw):
    value = 0xcbf29ce484222325
    for byte in raw:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return value


def header(index, density):
    return struct.pack('<4s6I', b'HDR1', 80000 + index, density, 12, 14, 0, 0)


def synthetic(index, density, decoded):
    return header(index, density) + b''.join(
        bytes(((index * 23 + x) % 256, (y * 31) % 256, 193, decoded[168 + (y // density) * 12 + x // density]))
        for y in range(14 * density) for x in range(12 * density))


def reduced(raw, index):
    pixels = raw[28:]
    return header(index, 4) + b''.join(pixels[(y * 2 * 96 + x * 2) * 4:(y * 2 * 96 + x * 2) * 4 + 4]
                                      for y in range(56) for x in range(48))


def mutate(raw, index, kind, density):
    raw = bytearray(raw)
    fields = {'role': (4, 90000 + index), 'identity': (4, 80000 + IDS[(IDS.index(index) + 1) % len(IDS)]),
              'density': (8, 4 if density == 8 else 8), 'width': (12, 11), 'height': (16, 13),
              'anchor-x': (20, 1), 'anchor-y': (24, 1)}
    if kind in fields:
        struct.pack_into('<I', raw, *fields[kind])
    if kind == 'magic': raw[:4] = b'BAD!'
    if kind == 'short-header': raw = raw[:27]
    if kind == 'truncated': raw = raw[:-1]
    if kind == 'extra': raw += b'X'
    return bytes(raw)


def fixtures(out, art, bank):
    full = out / 'complete'
    full.mkdir()
    # Existing routes get independent small synthetic loader fixtures. This is
    # coexistence/cache testing, not acceptance of archived artwork.
    for index in IDS + PREVIOUS:
        for density in (8, 4):
            raw = art[index] if index in art else synthetic(index, 8, decode(bank, index))
            (full / f'bullet-{index}-{density}.hda').write_bytes(raw if density == 8 else reduced(raw, index))
    variants = out / 'fixtures'
    variants.mkdir()
    rows = []
    def add(index, name, specs):
        folder = variants / f'{name}-{index}'
        folder.mkdir()
        for density, kind in specs.items():
            raw = art[index] if density == 8 else reduced(art[index], index)
            if kind != 'valid': raw = mutate(raw, index, kind, density)
            (folder / f'bullet-{index}-{density}.hda').write_bytes(raw)
        ok8, ok4 = specs.get(8) == 'valid', specs.get(4) == 'valid'
        rows.append((folder.name, index, int(ok8 or ok4), 8 if ok8 else 4, int(ok4), 4))
    for index in IDS:
        for name, spec in [('missing', {}), ('only8', {8: 'valid'}), ('only4', {4: 'valid'}),
                           ('both', {8: 'valid', 4: 'valid'})]:
            add(index, name, spec)
        for kind in ('magic', 'role', 'identity', 'density', 'width', 'height', 'anchor-x', 'anchor-y', 'short-header', 'truncated', 'extra'):
            for suffix, spec in [('8', {8: kind}), ('8-valid4', {8: kind, 4: 'valid'}),
                                 ('4', {4: kind}), ('both', {8: kind, 4: kind}),
                                 ('valid8-bad4', {8: 'valid', 4: kind})]:
                add(index, kind + '-' + suffix, spec)
    (variants / 'variants.tsv').write_text(''.join(' '.join(map(str, row)) + '\n' for row in rows))
    return full, variants, len(rows)


def production_units(out, source):
    names = ['decode_tile', 'read_asset', 'explosion_asset_slot', 'mint27_source_matches']
    names += re.findall(r'^static (?:int|bool) (sonic_\w+(?:_member|_source_matches))\(', source, re.M)
    assert 'sonic_quadrant_member' in names and 'sonic_quadrant_source_matches' in names
    names += ['get_asset', 'render_mirror_entity', 'render_mirror_unsupported']
    functions = {name: extract(source, name) for name in names}
    (out / 'functions.inc').write_text('\n'.join(value[:value.index('{')].strip() + ';' for value in functions.values()) + '\n' + ''.join(functions.values()))
    patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',
                r'static Asset assets\[\d+\];', r'enum \{ ASSET_NEWSH2=.*?\};']
    (out / 'types.inc').write_text('\n'.join(re.search(p, source, re.S).group() for p in patterns))
    sprite_type = re.search(r'typedef struct\s*\{\s*size_t size;\s*Uint8 \*data;\s*\}\s*Sprite2_array;', (ROOT / 'src/sprite.h').read_text()).group()
    (out / 'sprite-type.inc').write_text(sprite_type)
    blitters = {name: extract((ROOT / 'src/sprite.c').read_text(), name) for name in ('blit_sprite2', 'blit_sprite2_blend', 'blit_sprite2_darken')}
    (out / 'blitters.inc').write_text(''.join(value.replace('void ' + name + '(', 'void production_' + name + '(', 1) for name, value in blitters.items()))
    wrapper = extract((ROOT / 'src/entity_draw.c').read_text(), 'draw_entity_sprite2')
    (out / 'wrappers.inc').write_text(wrapper)
    # Check only relevant gameplay/blitter boundaries against the current commit.
    # No repository walk, inventory hash, or broad tree pin is performed.
    unchanged = {}
    for name in ('src/shots.c', 'src/entity_draw.c', 'src/sprite.c', 'src/episodes.c'):
        current = (ROOT / name).read_bytes()
        base = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + name])
        assert current == base, 'Out-of-scope production change: ' + name
        unchanged[name] = SHA(current)
    helper = functions['sonic_quadrant_source_matches']
    for value in FNV.values(): assert f'0x{value:016x}' in helper.lower()
    assert not re.search(r'\b(?:rand|random|mt_rand|mt_rand_1|srand)\s*\(', ''.join(functions.values()))
    return functions, {name: SHA(value.encode()) for name, value in {**functions, **blitters, 'draw_entity_sprite2': wrapper}.items()}, unchanged


def source_rows(data_dir):
    """Decode only the five requested rows and their exact +1000 copies."""
    fields = 'drain shotrepeat multi weapani max tx ty aim attack del sx sy bx by sg acceleration accelerationx circlesize sound trail shipblastfilter'.split()
    tokens = 'H B B H B B B B 8B 8B 8b 8b 8b 8b 8H b b B B B B'.split()
    assert struct.calcsize('<' + ''.join(tokens)) == 80
    formats = {'u8': 'B', 's8': 'b', 'u16': 'H', 's16': 'h'}
    schema = [(name, (count if count != '1' else '') + formats[kind]) for kind, name, count in
              re.findall(r'fread_(u8|s8|u16|s16)_die\(\s*&?weapons\[i\]\.(\w+),\s*(\d+),\s*f\)', (ROOT / 'src/episodes.c').read_text())]
    assert schema == list(zip(fields, tokens)), 'Original weapon schema changed'
    tables = []
    for name in ('tyrian.hdt', 'tyrian4.lvl', 'tyrian5.lvl'):
        path = data_dir / name
        if not path.exists():
            continue
        raw = path.read_bytes()
        if name == 'tyrian.hdt':
            start = struct.unpack_from('<i', raw)[0]
        else:
            levels = struct.unpack_from('<H', raw)[0]
            start = struct.unpack_from('<I', raw, 2 + 4 * (levels - 1))[0]
        assert struct.unpack_from('<7H', raw, start) == (818, 60, 6, 18, 37, 11, 850)
        rows = []
        for rid in range(282, 287):
            offset = start + 14 + rid * 80
            record_bytes = raw[offset:offset + 80]
            assert record_bytes == raw[offset + 819 * 80:offset + 820 * 80]
            position = offset
            record = {}
            for field, token in zip(fields, tokens):
                values = list(struct.unpack_from('<' + token, raw, position))
                position += struct.calcsize('<' + token)
                record[field] = values if len(values) > 1 else values[0]
            assert record['multi'] == record['max'] == (6, 6, 7, 7, 8)[rid - 282]
            assert record['weapani'] == 0 and record['sg'][:4] == list(IDS)
            for field, wanted in [('bx', [-2, 2, -2, 2]), ('by', [-7, -7, 7, 7]),
                                  ('sx', [-13, 13, -13, 13]), ('sy', [0, 0, 0, 0]), ('del', [100] * 4)]:
                assert record[field][:4] == wanted, (name, rid, field)
            assert not set((143, 144)) & set(record['sg'][:record['max']])
            rows.append({'record': rid, 'power': rid - 275, 'offset': offset,
                         'sha256': SHA(record_bytes), 'plus1000_byte_equal': True,
                         'full_original_record': record})
        port_offset = start + 14 + 1638 * 80 + 11 * 82
        port = raw[port_offset:port_offset + 82]
        assert struct.unpack_from('<11H', port, 32) == tuple(range(276, 287))
        assert struct.unpack_from('<11H', port, 54) == tuple(range(287, 298))
        tables.append({'file': name, 'file_sha256': SHA(raw), 'rows': rows,
                       'port11_mode1_p7_p11': list(range(282, 287)), 'four_static_simultaneous_ordinals': [1, 2, 3, 4]})
    return tables


def limited(memory_mb):
    def set_limits():
        resource.setrlimit(resource.RLIMIT_AS, (memory_mb * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    return set_limits


def run(argv, log, memory_mb=None, env=None, expect_failure=False):
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=180,
                            preexec_fn=limited(memory_mb) if memory_mb else None, env=env)
    log.write_text(result.stdout + result.stderr)
    if expect_failure:
        assert result.returncode, 'Weakened production mutant incorrectly survived: ' + log.name
    elif result.returncode:
        raise RuntimeError('Command failed: ' + ' '.join(map(str, argv)) + '\n' + result.stdout + result.stderr)
    return result


def compile_and_run(out, bank_paths, full, variants, sanitized=False, expect_failure=False):
    flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-DSANITIZED=1'] if sanitized else ['-O2']
    name = 'sanitized' if sanitized else 'optimized'
    command = [os.environ.get('CC', 'cc'), '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-Wno-unused-function', '-Wno-unused-variable',
               '-DQUADRANT_SLOT=563', '-DQUADRANT_MEMBER=sonic_quadrant_member', *flags, '-I' + str(out), ROOT / 'tests/sonic_quadrant_binding.c',
               '-Wl,--wrap=fopen', '-Wl,--wrap=malloc', '-o', out / name]
    run(command, out / (name + '-compile.log'), 1024)
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:hard_rss_limit_mb=512', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    result = run([out / name, *bank_paths, full, out / 'reference.bin', variants], out / (name + '.log'),
                 None if sanitized else 512, env, expect_failure)
    return {'expected_rejection': True, 'returncode': result.returncode} if expect_failure else json.loads(result.stdout)


def mutants(out, source, bank_paths, full, variants, sanitized):
    original = (out / 'functions.inc').read_text()
    helper = extract(source, 'sonic_quadrant_source_matches')
    get_asset = extract(source, 'get_asset')
    start = get_asset.index('if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_quadrant_member(index)>=0)')
    end = get_asset.index('\n }', start) + 3
    route = get_asset[start:end]
    # game_probe_missing also has an identical shared pre-cache guard. Removing
    # just its local duplicate is behaviorally equivalent, so it is not a valid
    # runtime mutation oracle. Both cold/warm denial paths are tested normally.
    edits = {}
    for flag in ('twoPlayerMode', 'galagaMode', 'twoPlayerLinked', 'game_probe_invalid', 'game_probe_original_reference'):
        assert flag + '||' in route
        edits['omit-' + flag] = (route, route.replace(flag + '||', '', 1))
    edits['omit-no-assets'] = (route, route.replace('!game_probe_assets||', '', 1))
    edits['omit-density'] = (route, route.replace('(game_probe_density!=4&&game_probe_density!=8)||', '', 1))
    edits['omit-source'] = (route, route.replace('||!sonic_quadrant_source_matches(bank,index)', '', 1))
    edits['trust-warm-cache'] = (helper, helper.replace('{', '{\n if(assets[563+sonic_quadrant_member(index)].initialized)return true;', 1))
    edits['omit-explicit-xmas'] = (helper, helper.replace('xmas||', '', 1))
    for label, begin in [('indices-only', 0), ('coverage-only', 168)]:
        changed = helper
        for index, value in FNV.items():
            ref = decode(bank_paths.normal_bank, index)
            changed = changed.replace(f'0x{value:016x}', f'0x{fnv(ref[begin:begin+168]):016x}')
        changed = changed.replace('for(size_t i=0;i<sizeof(source);i++)', f'for(size_t i={begin};i<{begin+168};i++)')
        edits[label] = (helper, changed)
    line = next(line for line in extract(source, 'render_mirror_entity').splitlines(True) if 'sonic_quadrant_member' in line and 'MIRROR_SHADOW' in line)
    edits['omit-early-shadow'] = (line, '')
    if sanitized:
        edits['read-cache-before-gates'] = (route, route.replace('{', '{\n volatile bool bad=assets[563+sonic_quadrant_member(index)].initialized;(void)bad;', 1))
    results = {}
    for label, (before, after) in edits.items():
        assert before != after and original.count(before) == 1, label
        folder = out / ('mutant-' + label)
        folder.mkdir()
        for name in ('sprite-type.inc', 'types.inc', 'blitters.inc', 'wrappers.inc', 'reference.bin'):
            shutil.copyfile(out / name, folder / name)
        (folder / 'functions.inc').write_text(original.replace(before, after, 1))
        result = compile_and_run(folder, bank_paths, full, variants, sanitized and label == 'read-cache-before-gates', True)
        if label == 'read-cache-before-gates': assert 'use-after-poison' in (folder / 'sanitized.log').read_text()
        results[label] = result
        print(label + ': rejected', flush=True)
    return results


class BankPaths(list):
    pass


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--out', type=Path)
    p.add_argument('--art', type=Path, default=ROOT / 'assets/hd/artwork/player-sonic-quadrants-v1/output')
    p.add_argument('--synthetic-art', action='store_true')
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--mutants', action='store_true')
    p.add_argument('--min-free-mib',type=int,default=None,help='Explicit disk reserve, minimum 512 MiB; default retains 5 GB reserve')
    args = p.parse_args()
    if args.min_free_mib is not None and args.min_free_mib<512:p.error('--min-free-mib must be at least 512')
    reserve=5_000_000_000 if args.min_free_mib is None else args.min_free_mib*1024*1024
    out = args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='sonic-quadrant-'))
    assert out != ROOT and ROOT not in out.parents, 'Results must remain outside the checkout'
    if args.out: out.mkdir(parents=True, exist_ok=False)
    assert shutil.disk_usage(out).free >= reserve, 'Insufficient explicit disk reserve'
    free_before=shutil.disk_usage(out).free
    path = args.data / 'tyrian.shp' if args.data.is_dir() else args.data
    normal, normal_sha = bank_from(path)
    christmas_path = path.with_name('tyrianc.shp')
    christmas, christmas_sha = bank_from(christmas_path) if christmas_path.exists() else (None, None)
    decoded = {index: decode(normal, index) for index in IDS}
    for index, raw in decoded.items(): assert fnv(raw) == FNV[index], (index, hex(fnv(raw)))
    source = (ROOT / 'src/render_mirror.c').read_text()
    _, hashes, boundaries = production_units(out, source)
    art = {}
    for index in IDS:
        raw = synthetic(index, 8, decoded[index]) if args.synthetic_art else (args.art / f'bullet-{index}-8.hda').read_bytes()
        assert len(raw) == 43036 and raw[:28] == header(index, 8), index
        art[index] = raw
    full, variants, count = fixtures(out, art, normal)
    normal_path = out / 'normal.bank8'; normal_path.write_bytes(normal)
    cp = '-'
    if christmas is not None:
        cp = out / 'christmas.bank8'; cp.write_bytes(christmas)
    bank_paths = BankPaths([normal_path, cp]); bank_paths.normal_bank = normal
    (out / 'reference.bin').write_bytes(b''.join(decoded.values()) + b''.join(decode(christmas or normal, index) for index in IDS))
    report = {'status': 'PASS', 'authored_art': not args.synthetic_art, 'original_data_sha256': normal_sha,
              'christmas_data_sha256': christmas_sha, 'resource_variants': count,
              'source_facts': {str(index): {'fnv1a64': f'{FNV[index]:016x}', 'indices_sha256': SHA(decoded[index][:168]),
                                             'coverage_sha256': SHA(decoded[index][168:]), 'hda_sha256': SHA(art[index])} for index in IDS},
              'production_function_sha256': hashes, 'unchanged_production_boundaries': boundaries,
              'bounded_original_weapon_rows': source_rows(path.parent), 'runs': {}}
    report['runs']['optimized'] = compile_and_run(out, bank_paths, full, variants)
    print('optimized: ' + json.dumps(report['runs']['optimized']), flush=True)
    if args.sanitize:
        report['runs']['sanitized'] = compile_and_run(out, bank_paths, full, variants, True)
        print('sanitized: ' + json.dumps(report['runs']['sanitized']), flush=True)
    if args.mutants: report['guard_mutants'] = mutants(out, source, bank_paths, full, variants, args.sanitize)
    report['peak_child_rss_kib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    assert report['peak_child_rss_kib'] < 512 * 1024, 'Test/compiler peak resident memory exceeded 512 MiB'
    assert shutil.disk_usage(out).free >= reserve, 'Disk reserve dropped below explicit threshold'
    report['disk_reserve_bytes']=reserve
    report['disk_free_before_bytes']=free_before
    report['disk_free_after_bytes']=shutil.disk_usage(out).free
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: ' + str(out / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
