#!/usr/bin/env python3
"""Bounded extracted-production Sonic-quartet alpha-shadow regression.

Uses original bank8 data and frozen authored HDR1s. Does not launch the game,
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
import tempfile

import run_sonic_quadrant_tests as base

ROOT = base.ROOT
CASE_SOURCE = ROOT / 'tests/sonic_quadrant_shadow_test.c'
OLD_IDS = (67, 70, 121, 122, 163, 164, 201, 202, 279, 280, 225, 244, 226)


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
    (out / 'types.inc').write_text('\n'.join(re.search(p, source, re.S).group() for p in patterns))
    sprite = re.search(r'typedef struct\s*\{\s*size_t size;\s*Uint8 \*data;\s*\}\s*Sprite2_array;', (ROOT / 'src/sprite.h').read_text()).group()
    (out / 'sprite-type.inc').write_text(sprite)
    blitters = {name: base.extract((ROOT / 'src/sprite.c').read_text(), name) for name in ('blit_sprite2', 'blit_sprite2_blend', 'blit_sprite2_darken')}
    (out / 'blitters.inc').write_text(''.join(s.replace('void ' + n + '(', 'void production_' + n + '(', 1) for n, s in blitters.items()))
    wrapper = base.extract((ROOT / 'src/entity_draw.c').read_text(), 'draw_entity_sprite2')
    (out / 'wrappers.inc').write_text(wrapper)
    prior = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:src/render_mirror.c'], text=True)
    pinrows = lambda s: [row.rstrip(',') for row in re.findall(r'^ \{\d+,\d+,UINT64_C\(0x[0-9a-f]+\),UINT64_C\(0x[0-9a-f]+\),\d+,(?:UINT64_C\(0x[0-9a-f]+\)|0)\},?', s, re.M)]
    assert pinrows(source)[:13] == pinrows(prior)[:13], 'Existing thirteen shadow pins changed'
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
        for name in ('types.inc', 'sprite-type.inc', 'blitters.inc', 'wrappers.inc', 'reference.bin'):
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
    args = p.parse_args()
    out = args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='sonic-quartet-shadow-'))
    assert ROOT not in out.parents and out != ROOT
    if args.out: out.mkdir(parents=True, exist_ok=False)
    assert shutil.disk_usage(out).free >= 5_000_000_000
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
        shutil.copyfile(args.pack / f'bullet-{i}-8.hda', full / f'bullet-{i}-8.hda')
    for i in (225, 244, 226):
        shutil.copyfile(args.pack / f'protron-shadow-{i}-8.hda', full / f'protron-shadow-{i}-8.hda')
    (out / 'normal.bank8').write_bytes(normal)
    if christmas is not None: (out / 'christmas.bank8').write_bytes(christmas)
    paths = [out / 'normal.bank8', out / 'christmas.bank8' if christmas is not None else '-']
    (out / 'reference.bin').write_bytes(b''.join(base.decode(normal, i) for i in base.IDS))
    report = {'status': 'PASS', 'authored_art': True, 'source_sha256': source_sha, 'christmas_sha256': christmas_sha,
              'production_sha256': hashes, 'unchanged_production_boundaries': boundaries,
              'previous_thirteen_pins_and_classic_exclusions_unchanged': True,
              'resource_variants': count, 'frozen_rgba_fnv1a64': {str(i): f'{base.fnv(art[i][28:]):016x}' for i in base.IDS}, 'runs': {}}
    report['runs']['optimized'] = build_run(out, paths, full, variants)
    print('optimized: ' + json.dumps(report['runs']['optimized']), flush=True)
    if args.sanitize:
        report['runs']['sanitized'] = build_run(out, paths, full, variants, True)
        print('sanitized: ' + json.dumps(report['runs']['sanitized']), flush=True)
        report['leak_checking'] = 'unavailable under executor ptrace; ASan and UBSan checks enabled'
    if args.mutants: report['guard_mutants'] = mutants(out, source, paths, full, variants)
    report['peak_child_rss_kib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    assert report['peak_child_rss_kib'] < 512 * 1024
    assert shutil.disk_usage(out).free >= 5_000_000_000
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: ' + str(out / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
