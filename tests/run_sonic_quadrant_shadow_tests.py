#!/usr/bin/env python3
"""Bounded extracted-production Sonic-quartet alpha-shadow regression.

Uses original bank8 data and selected current authored HDR1s. Does not launch the game,
walk the repository, inspect unrelated source projections, or alter assets.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import tempfile

import run_sonic_quadrant_tests as base

ROOT = base.ROOT
CASE_SOURCE = ROOT / 'tests/sonic_quadrant_shadow_test.c'
OLD_IDS = (67, 70, 121, 122, 163, 164, 201, 202, 279, 280, 225, 244, 226)



# Independent original-source/slot oracle; payloads are read from the eight
# selected PNGs, not accepted merely because a generated header declares them.
FRONT_MULTI_PINS = (
    (121, 524, 0xba0e9fed90289c7a), (122, 525, 0x4f9d6fbe1da41b7c),
    (163, 526, 0xa34174ba65a5e3b2), (164, 527, 0xd118e1292d0f1044),
    (201, 528, 0xfb2f8d2713f98f50), (202, 529, 0xd92e815af85b74c6),
    (279, 530, 0x1edad45847d64c25), (280, 531, 0x0842bfe453e6cb1d),
)
FRONT_MULTI_HEADER = 'hd_front_multi_current.h'
PROTRON_HEADER = 'current_protron_payload_pins.h'
SONIC_HEADER = 'current_sonic_payload_pins.h'
PROTRON_PINS = (
    (225,469,0xcc2d73d8d3e08e9b,532,0x9115d94f761d41b6),
    (244,470,0x536ebd180af638d6,533,0xa0f35ce4562bb3a9),
    (226,471,0x6f6f9c2a049b7953,534,0xb5ae06163e59f3f6),
)
SONIC_PINS = (
    (105,563,0x66cdc314034152a6,0,0), (106,564,0xee609a977010a3e0,0,0),
    (124,565,0x836f9ec6407ea3aa,0,0), (125,566,0xbad7de0256394e9c,0,0),
)


def master_payloads(family, root=ROOT):
    """Reconstruct selected master pixels; generated pin text is not an oracle."""
    import importlib
    if str(root/'scripts') not in sys.path:
        sys.path.insert(0,str(root/'scripts'))
    compat=importlib.import_module('current_'+family+'_compatibility')
    _,_,blobs=compat.generate(root,compat.read(root,compat.SELECTION))
    expected=compat.payload_header({pair:f'{base.fnv(raw[28:]):016x}' for pair,raw in blobs.items()})
    assert compat.read(root,compat.HEADER)==expected, family+' generated header differs from selected master derivation'
    return {identity-80000:base.fnv(raw[28:]) for (identity,density),raw in blobs.items() if identity//10000==8}



def resolve_current_payload_pins(source, header=None, front_header=None, protron_header=None, sonic_header=None):
    """Expand only declared payload tokens; never silently drop unknown rows."""
    if header is None:
        header = (ROOT / 'src/current_art_payload_pins.h').read_text()
    pins = dict(re.findall(r'^#define (CURRENT_(?:VULCAN_(?:67|70)|GREEN_8021[4-7])_RGBA) (UINT64_C\(0x[0-9a-f]{16}\))$', header, re.M))
    tokens = set(re.findall(r'\bCURRENT_(?:VULCAN|GREEN)_\w+_RGBA\b', source))
    front_tokens = set(re.findall(r'\bHD_FRONT_MULTI_CURRENT_PAYLOAD_\w+_HASH\b', source))
    if front_tokens:
        if front_header is None:
            front_header = (ROOT / 'src' / FRONT_MULTI_HEADER).read_text()
        entries = re.findall(r'^#define (HD_FRONT_MULTI_CURRENT_PAYLOAD_\w+_HASH) (UINT64_C\(0x[0-9a-f]{16}\))$', front_header, re.M)
        expected = {'HD_FRONT_MULTI_CURRENT_PAYLOAD_%d_HASH' % (80000+i) for i, _, _ in FRONT_MULTI_PINS}
        assert len(entries) == 8 and {name for name, _ in entries} == expected, 'Unknown/missing/duplicate Front Multi generated payload pin'
        pins.update(entries)
    tokens |= front_tokens
    for family, supplied, filename, identities in (
            ('PROTRON',protron_header,PROTRON_HEADER,(80225,80244,80226,1470227)),
            ('SONIC',sonic_header,SONIC_HEADER,(80105,80106,80124,80125))):
        family_tokens=set(re.findall(r'\bCURRENT_'+family+r'_\w+_PAYLOAD_FNV\b',source))
        if not family_tokens:
            continue
        text=(ROOT/'src'/filename).read_text() if supplied is None else supplied
        entries=re.findall(r'^#define (CURRENT_'+family+r'_\w+_PAYLOAD_FNV) (UINT64_C\(0x[0-9a-f]{16}\))$',text,re.M)
        expected={f'CURRENT_{family}_{identity}_D8_PAYLOAD_FNV' for identity in identities}
        assert len(entries)==4 and {key for key,_ in entries}==expected, 'Unknown/missing/duplicate '+family+' generated payload pin'
        pins.update(entries);tokens|=family_tokens
    if not tokens <= pins.keys():
        raise AssertionError('Unknown/missing generated shadow payload pin: ' + str(tokens - pins.keys()))
    for name in tokens:
        source = re.sub(r'\b' + name + r'\b', pins[name], source)
    return source


def shadow_pin_rows(source, header=None, front_header=None, protron_header=None, sonic_header=None):
    source = resolve_current_payload_pins(source, header, front_header, protron_header, sonic_header)
    table = re.search(r'vulcan_shadow_pins\[(\d+)\]=\{(.*?)\n\};', source, re.S)
    assert table and table[1] == '45', 'Expected exactly 45 declared shadow rows'
    body = re.sub(r'/\*.*?\*/', '', table[2], flags=re.S)
    lines = [line.rstrip(',') for line in body.splitlines() if line.strip()]
    pattern = r' \{\d+,\d+,UINT64_C\(0x[0-9a-f]{16}\),UINT64_C\(0x[0-9a-f]{16}\),\d+,(?:UINT64_C\(0x[0-9a-f]{16}\)|0)\}'
    assert len(lines) == 45 and all(re.fullmatch(pattern, line) for line in lines), 'Expected exactly 45 fully resolved shadow rows'
    return lines


def front_multi_payloads(root=ROOT):
    """Independent PNG decoder: exact roles, geometry and selected byte hashes."""
    import io
    from PIL import Image
    selected = json.loads((root / 'assets/hd/authoring/front-multi-current.json').read_bytes())
    rows = selected['resources']
    assert len(rows) == 8 and [r['identity'] for r in rows] == [80000+i for i, _, _ in FRONT_MULTI_PINS], 'Front Multi source identity/order'
    result = {}
    for row in rows:
        path = Path(row['source_png'])
        assert not path.is_absolute() and '..' not in path.parts and path.parts[0] == 'authoring-inputs', 'Front Multi source path'
        raw = (root / path).read_bytes()
        assert base.SHA(raw) == row['source_sha256'], 'Front Multi selected PNG pin'
        with Image.open(io.BytesIO(raw)) as frame:
            assert (frame.format, frame.mode, frame.size, getattr(frame, 'n_frames', 1)) == ('PNG', 'RGBA', (96,112), 1), 'Front Multi PNG geometry'
            result[row['identity'] - 80000] = base.fnv(frame.tobytes())
    return result


def verify_front_multi_rows(source, header=None, front_header=None, payloads=None):
    rows = shadow_pin_rows(source, header, front_header)
    payloads = front_multi_payloads() if payloads is None else payloads
    expected = [f' {{{i},{slot},UINT64_C(0x{stamp:016x}),UINT64_C(0x{payloads[i]:016x}),0,0}}' for i, slot, stamp in FRONT_MULTI_PINS]
    assert rows[2:10] == expected, 'Front Multi source/slot/payload/coverage oracle mismatch'
    return rows


def verify_master_rows(source):
    rows=verify_front_multi_rows(source)
    for family,pins,start in (('protron',PROTRON_PINS,10),('sonic',SONIC_PINS,13)):
        payloads=master_payloads(family)
        expected=[f' {{{i},{slot},UINT64_C(0x{stamp:016x}),UINT64_C(0x{payloads[i]:016x}),{coverage},'+
                  (f'UINT64_C(0x{coverage_stamp:016x})' if coverage else '0')+'}'
                  for i,slot,stamp,coverage,coverage_stamp in pins]
        assert rows[start:start+len(pins)]==expected, family+' source/slot/payload/coverage oracle mismatch'
    return rows


def compare_previous_shadow_pins(source, prior, count, prior_header=None, prior_front_header=None,
                                 prior_protron_header=None, prior_sonic_header=None):
    current = verify_master_rows(source)
    previous = shadow_pin_rows(prior, prior_header, prior_front_header, prior_protron_header, prior_sonic_header)
    # Only independently rederived selected payloads may differ. Every source
    # stamp, cache slot, coverage slot/pin, ordering and other row stays fixed.
    for offset, (i, slot, stamp) in enumerate(FRONT_MULTI_PINS, 2):
        expected = f' {{{i},{slot},UINT64_C(0x{stamp:016x}),'
        assert previous[offset].startswith(expected) and previous[offset].endswith(',0,0}'), 'Previous Front Multi structural oracle mismatch'
        previous[offset] = current[offset]
    for pins,start in ((PROTRON_PINS,10),(SONIC_PINS,13)):
        for offset,(i,slot,stamp,coverage,coverage_stamp) in enumerate(pins,start):
            prefix=f' {{{i},{slot},UINT64_C(0x{stamp:016x}),'
            suffix=f',{coverage},'+(f'UINT64_C(0x{coverage_stamp:016x})' if coverage else '0')+'}'
            assert previous[offset].startswith(prefix) and previous[offset].endswith(suffix), 'Previous master-family structural oracle mismatch'
            previous[offset]=current[offset]
    assert current[:count] == previous[:count], f'Previous {count} shadow pins changed outside independently derived current payloads'
    return current


def current_head_path(pack, index):
    if index in {i for i, _, _ in FRONT_MULTI_PINS}:
        return ROOT / 'assets/hd/current-compat/front-multi' / f'bullet-{index}-8.hda'
    if index in (225,244,226):
        return ROOT / 'assets/hd/current-compat/protron' / f'bullet-{index}-8.hda'
    return pack / f'bullet-{index}-8.hda'


def units(out, source):
    names = ['decode_tile', 'read_asset', 'explosion_asset_slot', 'mint27_source_matches']
    names += re.findall(r'^static (?:int|bool) (sonic_\w+(?:_member|_source_matches))\(', source, re.M)
    names += ['get_asset', 'render_mirror_entity', 'vulcan_shadow_member', 'vulcan_shadow_clear',
              'vulcan_shadow_stamp', 'vulcan_shadow_coverage_asset', 'vulcan_shadow_coverage_valid',
              'draw_vulcan_shadow', 'render_mirror_shadow_begin', 'render_mirror_shadow_end',
              'vulcan_shadow_pixel', 'render_mirror_pixel', 'render_mirror_unsupported',
              'palette_rgb', 'blend_rgba', 'cloud_shadow_rgba', 'darken_rgba', 'render_mirror_entity_end']
    funcs = {name: base.extract(source, name) for name in names}
    # The observation shim forwards to the unchanged complete production pixel
    # function. Every original write still reaches the real compositor.
    funcs['render_mirror_pixel'] = funcs['render_mirror_pixel'].replace('void render_mirror_pixel(', 'void production_render_mirror_pixel(', 1)
    (out / 'functions.inc').write_text('\n'.join(s[:s.index('{')].strip() + ';' for s in funcs.values()) + '\n' + ''.join(funcs.values()))
    patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',
                r'typedef struct \{\s*bool live,entered,rear;.*?\} VulcanShadowCall;',
                r'static Asset assets\[\d+\];', r'enum \{ ASSET_NEWSH2=.*?\};',
                r'static const struct \{unsigned int index;int slot;uint64_t source,rgba;int coverage_slot;uint64_t coverage_rgba;\} vulcan_shadow_pins\[\d+\]=\{.*?\n\};']
    (out / 'types.inc').write_text('#include \"current_art_payload_pins.h\"\n#include \"hd_front_multi_current.h\"\n#include \"current_protron_payload_pins.h\"\n#include \"current_sonic_payload_pins.h\"\n' + '\n'.join(re.search(p, source, re.S).group() for p in patterns))
    (out / 'current_art_payload_pins.h').write_bytes((ROOT / 'src/current_art_payload_pins.h').read_bytes())
    for name in (FRONT_MULTI_HEADER,PROTRON_HEADER,SONIC_HEADER):
        (out/name).write_bytes((ROOT/'src'/name).read_bytes())
    sprite = re.search(r'typedef struct\s*\{\s*size_t size;\s*Uint8 \*data;\s*\}\s*Sprite2_array;', (ROOT / 'src/sprite.h').read_text()).group()
    (out / 'sprite-type.inc').write_text(sprite)
    blitters = {name: base.extract((ROOT / 'src/sprite.c').read_text(), name) for name in ('blit_sprite2', 'blit_sprite2_blend', 'blit_sprite2_darken')}
    (out / 'blitters.inc').write_text(''.join(s.replace('void ' + n + '(', 'void production_' + n + '(', 1) for n, s in blitters.items()))
    wrapper = base.extract((ROOT / 'src/entity_draw.c').read_text(), 'draw_entity_sprite2')
    (out / 'wrappers.inc').write_text(wrapper)
    prior = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:src/render_mirror.c'], text=True)
    prior_header = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:src/current_art_payload_pins.h'], text=True)
    prior_front_header = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:src/' + FRONT_MULTI_HEADER], text=True) if 'HD_FRONT_MULTI_CURRENT_PAYLOAD_' in prior else None
    prior_protron_header = subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:src/'+PROTRON_HEADER],text=True) if 'CURRENT_PROTRON_' in prior else None
    prior_sonic_header = subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:src/'+SONIC_HEADER],text=True) if 'CURRENT_SONIC_' in prior else None
    compare_previous_shadow_pins(source, prior, 13, prior_header, prior_front_header, prior_protron_header, prior_sonic_header)
    # Classic exclusions must stay byte-for-byte at their established boundary.
    classic = lambda s: [line for line in base.extract(s, 'render_mirror_entity').splitlines() if 'MIRROR_SHADOW' in line and 'return false' in line and any(token in line for token in ('index>=31&&index<=33', 'index>=252&&index<=254', 'index>=214&&index<=217'))]
    assert classic(source) == classic(prior), 'Existing classic shadow exclusion changed'
    unchanged = {}
    for name in ('src/shots.c', 'src/entity_draw.c', 'src/sprite.c', 'src/episodes.c'):
        raw = (ROOT / name).read_bytes()
        assert raw == subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + name]), name
        unchanged[name] = base.SHA(raw)
    assert not re.search(r'\b(?:rand|random|mt_rand|mt_rand_1|srand)\s*\(', ''.join(funcs.values()))
    return {name: base.SHA(s.encode()) for name, s in {**funcs, **blitters, 'draw_entity_sprite2': wrapper}.items()}, unchanged


def build_run(out, paths, full, variants, sanitized=False, expect_failure=False):
    name = 'sanitized' if sanitized else 'optimized'
    flags = ['-O1', '-g', '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie', '-DSANITIZED=1'] if sanitized else ['-O2']
    cc = [os.environ.get('CC', 'cc'), '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-Wno-unused-function', '-Wno-unused-variable',
          *flags, '-I' + str(out), CASE_SOURCE, '-Wl,--wrap=fopen', '-Wl,--wrap=malloc', '-o', out / name]
    base.run(cc, out / (name + '-compile.log'), 1024)
    # LSan cannot inspect processes under the executor's ptrace sandbox.
    # ASan/UBSan retain halt-on-error and the same RSS ceiling.
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:hard_rss_limit_mb=512', UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    if expect_failure: env['SONIC_SHADOW_FAULTS_ONLY'] = '1'
    # The full cross-product deliberately checks >1.6 billion indexed bytes.
    # Bound its sanitizer run separately without weakening either memory cap.
    result = subprocess.run(list(map(str, [out / name, *paths, full, out / 'reference.bin', variants])),
                            capture_output=True, text=True, timeout=360,
                            preexec_fn=None if sanitized else base.limited(512), env=env)
    (out / (name + '.log')).write_text(result.stdout + result.stderr)
    if expect_failure:
        assert result.returncode and 'Assertion' in result.stderr, 'Weakened guard survived or failed outside a test assertion: ' + str(out)
        return {'expected_rejection': True, 'returncode': result.returncode, 'assertion': result.stderr.strip()}
    if result.returncode: raise RuntimeError(name + ' failed:\n' + result.stdout + result.stderr)
    return json.loads(result.stdout)


def mutants(out, source, paths, full, variants, loader_mode=True):
    original = (out / 'functions.inc').read_text()
    prep = base.extract(source, 'draw_vulcan_shadow')
    begin = base.extract(source, 'render_mirror_shadow_begin')
    pixel = base.extract(source, 'vulcan_shadow_pixel')
    asset = base.extract(source, 'get_asset')
    mode = '(k>=13&&(twoPlayerMode||galagaMode||twoPlayerLinked))||'
    pixel_mode = '(vulcan_shadow_member(v->index)>=13&&(twoPlayerMode||galagaMode||twoPlayerLinked))||'
    rgba = 'vulcan_shadow_stamp(a->rgba,12*14*8*8*4)!=vulcan_shadow_pins[k].rgba'
    src = 'vulcan_shadow_stamp(source,sizeof(source))!=vulcan_shadow_pins[k].source'
    root = 'strcmp(path,vulcan_shadow_resource[k].path)'
    changes = {
        'omit-begin-mode': [(begin, begin.replace(mode, '', 1))],
        'omit-pixel-mode': [(pixel, pixel.replace(pixel_mode, '', 1))],
        'omit-prep-rgba-pin': [(prep, prep.replace(rgba, 'false', 1))],
        'omit-prep-resource-root': [(prep, prep.replace(root, 'false', 1))],
        'omit-begin-source-pin': [(begin, begin.replace(src, 'false', 1))],
    }
    # The unchanged head loader independently repeats the quartet mode gate.
    # Remove both barriers for this deliberately compound preflight mutant;
    # deleting only the outer duplicate is behaviorally equivalent.
    if loader_mode:
        start = asset.index('if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_quadrant_member(index)>=0)')
        end = asset.index('\n }', start) + 3
        route = asset[start:end]
        weakened = asset.replace(route, route.replace('twoPlayerMode||galagaMode||twoPlayerLinked||', '', 1), 1)
        changes['omit-prep-and-loader-mode'] = [(prep, prep.replace(mode, '', 1)), (asset, weakened)]
    else:
        changes['omit-prep-mode'] = [(prep, prep.replace(mode, '', 1))]
    results = {}
    for label, edits in changes.items():
        folder = out / ('mutant-' + label)
        folder.mkdir()
        text = original
        for before, after in edits:
            assert before != after and text.count(before) == 1, label
            text = text.replace(before, after, 1)
        for name in ('types.inc', 'sprite-type.inc', 'blitters.inc', 'wrappers.inc', 'reference.bin', 'current_art_payload_pins.h', FRONT_MULTI_HEADER, PROTRON_HEADER, SONIC_HEADER):
            shutil.copyfile(out / name, folder / name)
        (folder / 'functions.inc').write_text(text)
        results[label] = build_run(folder, paths, full, variants, expect_failure=True)
        print(label + ': rejected', flush=True)
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--out', type=Path)
    p.add_argument('--pack', type=Path, required=True, help='Retained candidate pack for prior thirteen pinned shadow resources')
    p.add_argument('--art', type=Path, default=ROOT / 'assets/hd/artwork/player-sonic-quadrants-v1/output')
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--mutants', action='store_true')
    p.add_argument('--min-free-mib',type=int,default=None,help='Explicit disk reserve, minimum 512 MiB; default retains 5 GB reserve')
    args = p.parse_args()
    if args.min_free_mib is not None and args.min_free_mib<512:p.error('--min-free-mib must be at least 512')
    reserve=5_000_000_000 if args.min_free_mib is None else args.min_free_mib*1024*1024
    out = args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='sonic-quartet-shadow-'))
    assert ROOT not in out.parents and out != ROOT
    if args.out: out.mkdir(parents=True, exist_ok=False)
    assert shutil.disk_usage(out).free >= reserve, 'Insufficient explicit disk reserve'
    free_before=shutil.disk_usage(out).free
    source = (ROOT / 'src/render_mirror.c').read_text()
    hashes, boundaries = units(out, source)
    path = args.data / 'tyrian.shp' if args.data.is_dir() else args.data
    normal, source_sha = base.bank_from(path)
    cpath = path.with_name('tyrianc.shp')
    christmas, christmas_sha = base.bank_from(cpath) if cpath.exists() else (None, None)
    art = {i: (args.art / f'bullet-{i}-8.hda').read_bytes() for i in base.IDS}
    for i in base.IDS:
        assert base.fnv(base.decode(normal, i)) == base.FNV[i]
        assert len(art[i]) == 43036 and art[i][:28] == base.header(i, 8)
    full, variants, count = base.fixtures(out, art, normal)
    for i in OLD_IDS:
        shutil.copyfile(current_head_path(args.pack, i), full / f'bullet-{i}-8.hda')
    for i in (225, 244, 226):
        shutil.copyfile(args.pack / f'protron-shadow-{i}-8.hda', full / f'protron-shadow-{i}-8.hda')
    (out / 'normal.bank8').write_bytes(normal)
    if christmas is not None: (out / 'christmas.bank8').write_bytes(christmas)
    paths = [out / 'normal.bank8', out / 'christmas.bank8' if christmas is not None else '-']
    (out / 'reference.bin').write_bytes(b''.join(base.decode(normal, i) for i in base.IDS))
    report = {'disk_reserve_bytes':reserve,'disk_free_before_bytes':free_before,'status': 'PASS', 'authored_art': True, 'source_sha256': source_sha, 'christmas_sha256': christmas_sha,
              'production_sha256': hashes, 'unchanged_production_boundaries': boundaries,
              'previous_thirteen_structure_and_classic_exclusions_unchanged': True,
              'current_master_payload_headers_independently_rederived': ['protron','sonic'],
              'resource_variants': count, 'selected_rgba_fnv1a64': {str(i): f'{base.fnv(art[i][28:]):016x}' for i in base.IDS}, 'runs': {}}
    report['runs']['optimized'] = build_run(out, paths, full, variants)
    print('optimized: ' + json.dumps(report['runs']['optimized']), flush=True)
    if args.sanitize:
        report['runs']['sanitized'] = build_run(out, paths, full, variants, True)
        print('sanitized: ' + json.dumps(report['runs']['sanitized']), flush=True)
        report['leak_checking'] = 'unavailable under executor ptrace; ASan and UBSan checks enabled'
    if args.mutants: report['guard_mutants'] = mutants(out, source, paths, full, variants)
    report['peak_child_rss_kib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    assert report['peak_child_rss_kib'] < 512 * 1024
    assert shutil.disk_usage(out).free >= reserve, 'Insufficient explicit disk reserve'
    report['disk_free_after_bytes']=shutil.disk_usage(out).free
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: ' + str(out / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
