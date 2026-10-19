#!/usr/bin/env python3
"""Finite authored-alpha tests for the remaining seventeen Sonic heads and Mint27.

Only explicit production/test files and original selected bank8 data are read.
No repository walk, asset rewrite, engine launch or unrelated projection is used.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import resource
import shutil
import subprocess
import tempfile

import run_sonic_quadrant_tests as base
import run_sonic_quadrant_shadow_tests as shadow

ROOT = base.ROOT
IDS = (6, 44, 73, 63, 82, 16, 54, 130, 131, 149, 150, 223, 224, 242, 243, 143, 144, 27)
# Independent frozen source+payload expectations, kept separate from production.
PINS = (
 (6,546,0x3dcaa5f888996bce,0xae046f94e09ccd3b),
 (44,547,0x825f39ac9ec84b84,0x1c67a154f2f39893),
 (73,548,0x898413e19195c1be,0x8a74e8acd1362144),
 (63,549,0xa79a9f93c7439a27,0x8d8b870aa1224e54),
 (82,550,0x4f84a37be2ca17d7,0x4e2d079e0dfa5e80),
 (16,551,0x92a9608038427256,0x87f924779ed224e9),
 (54,552,0x3e1fc5eeeda214e0,0x6f424c42e9cf13f1),
 (130,553,0x0f527e20ee1119ba,0x849cfdb8342e4614),
 (131,554,0x184b6e120d7c65d0,0xae1db059a985d4d8),
 (149,555,0x5fd2500d1c31f756,0x032f1516fddf74b0),
 (150,556,0x24befa80f34416fc,0x746afddcb179e284),
 (223,557,0x5a22bdd5533d1d0d,0x66f621263659c742),
 (224,558,0x904489b42f2a3cd1,0xb8512cf2e3efc79e),
 (242,559,0xc114b5f56dfe2a85,0x171c50999a8dcfa2),
 (243,560,0xc571f14777146519,0x2e13f3347c8f6f1e),
 (143,561,0x9d732d4562f86474,0x278a51603a580f3a),
 (144,562,0xa9ede9c9164a8044,0x6ba1a5c42991552e),
 (27,535,0xd25ba01692cfa4b7,0xe75bfc31a0616e75),
)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--pack', type=Path, required=True)
    p.add_argument('--out', type=Path)
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--mutants', action='store_true')
    args = p.parse_args()
    out = args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='energy-shadow-'))
    assert ROOT not in out.parents and out != ROOT
    if args.out: out.mkdir(parents=True, exist_ok=False)
    assert shutil.disk_usage(out).free >= 5_000_000_000
    source = (ROOT / 'src/render_mirror.c').read_text()
    prior = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:src/render_mirror.c'], text=True)
    pinrows = lambda s: re.findall(r'^ \{\d+,\d+,UINT64_C\(0x[0-9a-f]+\),UINT64_C\(0x[0-9a-f]+\),\d+,(?:UINT64_C\(0x[0-9a-f]+\)|0)\}', s, re.M)
    assert pinrows(source)[:17] == pinrows(prior)[:17], 'Previous seventeen shadow pins changed'
    wanted = [f' {{{i},{slot},UINT64_C(0x{src:016x}),UINT64_C(0x{rgba:016x}),0,0}}' for i, slot, src, rgba in PINS]
    assert pinrows(source)[17:35] == wanted and len(pinrows(source)) == 45
    hashes, boundaries = shadow.units(out, source)
    path = args.data / 'tyrian.shp' if args.data.is_dir() else args.data
    normal, source_sha = base.bank_from(path)
    cpath = path.with_name('tyrianc.shp')
    christmas, christmas_sha = base.bank_from(cpath) if cpath.exists() else (None, None)
    manifest_path = ROOT / 'assets/hd/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest_path.read_bytes() == subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:assets/hd/manifest.json'])
    accepted = manifest['packs'][manifest['default_preview_pack']]['files']
    art, receipts = {}, []
    for i, slot, src, rgba in PINS:
        raw = (args.pack / f'bullet-{i}-8.hda').read_bytes()
        assert len(raw) == 43036 and raw[:28] == base.header(i, 8)
        assert base.fnv(base.decode(normal, i)) == src
        assert base.fnv(raw[28:]) == rgba
        assert base.SHA(raw) == accepted[f'bullet-{i}-8.hda']['sha256']
        art[i] = raw
        receipts.append({'index': i, 'slot': slot, 'source_fnv': f'{src:016x}', 'rgba_fnv': f'{rgba:016x}', 'sha256': base.SHA(raw)})
    base.IDS = IDS
    full, variants, count = base.fixtures(out, art, normal)
    for i in shadow.OLD_IDS + (105, 106, 124, 125):
        shutil.copyfile(args.pack / f'bullet-{i}-8.hda', full / f'bullet-{i}-8.hda')
    for i in (225, 244, 226):
        shutil.copyfile(args.pack / f'protron-shadow-{i}-8.hda', full / f'protron-shadow-{i}-8.hda')
    (out / 'normal.bank8').write_bytes(normal)
    if christmas is not None: (out / 'christmas.bank8').write_bytes(christmas)
    paths = [out / 'normal.bank8', out / 'christmas.bank8' if christmas is not None else '-']
    (out / 'reference.bin').write_bytes(b''.join(base.decode(normal, i) for i in IDS))
    case = out / 'energy-test.c'
    case.write_text('#define ENERGY_SHADOW_BATCH 1\n#include "' + str(ROOT / 'tests/sonic_quadrant_shadow_test.c') + '"\n')
    shadow.CASE_SOURCE = case
    report = {'status': 'PASS', 'scope': '18 finite canonical head-alpha shadows; pairwise bounded geometry and exhaustive per-ID guard cases',
              'source_sha256': source_sha, 'christmas_sha256': christmas_sha, 'production_sha256': hashes,
              'unchanged_production_boundaries': boundaries, 'previous_seventeen_pins_unchanged': True,
              'resource_variants': count, 'frozen_pins': receipts, 'runs': {}}
    report['runs']['optimized'] = shadow.build_run(out, paths, full, variants)
    print('optimized: ' + json.dumps(report['runs']['optimized']), flush=True)
    if args.sanitize:
        report['runs']['sanitized'] = shadow.build_run(out, paths, full, variants, True)
        print('sanitized: ' + json.dumps(report['runs']['sanitized']), flush=True)
        report['leak_checking'] = 'unavailable under executor ptrace; ASan/UBSan enabled'
    if args.mutants: report['guard_mutants'] = shadow.mutants(out, source, paths, full, variants)
    report['peak_child_rss_kib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    assert report['peak_child_rss_kib'] < 512 * 1024
    assert shutil.disk_usage(out).free >= 5_000_000_000
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: ' + str(out / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
