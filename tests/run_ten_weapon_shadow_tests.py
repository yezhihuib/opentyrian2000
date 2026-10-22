#!/usr/bin/env python3
"""Finite authored-alpha tests for Missile31–33, Charge252–254 and green214–217.

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
IDS = (31, 32, 33, 252, 253, 254, 214, 215, 216, 217)
# Independent frozen source+payload expectations, separate from production.
PINS = (
 (31,333,0xf63d654f4b2f50f5,0x7db65bd3d0e1d1df),
 (32,334,0xc261e2eb4d71452b,0xdb04017352ef16ca),
 (33,335,0xd47ab80283718879,0xcf349119e8c136ab),
 (252,330,0x294a9d4afd93d8a4,0x685a3572f08e508a),
 (253,331,0xbcdf97bf4b75c746,0xa4efdc2b3a6f26ed),
 (254,332,0xf471322126d86fdd,0xffdbece0353e10fe),
 (214,182,0x17da292b54af394c,0xa1bc11025ec02c94),
 (215,183,0x46b4c47c5e741b0f,0x71db2412311dc9af),
 (216,184,0xcb04c4fc86a8cbb7,0x62a2f5619503960f),
 (217,185,0xfab1a11e30972f37,0x4c366cbc9efc7cef),
)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--pack', type=Path, required=True)
    p.add_argument('--out', type=Path)
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--mutants', action='store_true')
    args = p.parse_args()
    out = args.out.resolve() if args.out else Path(tempfile.mkdtemp(prefix='ten-weapon-shadow-'))
    assert ROOT not in out.parents and out != ROOT
    if args.out: out.mkdir(parents=True, exist_ok=False)
    assert shutil.disk_usage(out).free >= 5_000_000_000
    source = (ROOT / 'src/render_mirror.c').read_text()
    prior = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:src/render_mirror.c'], text=True)
    prior_header = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:src/current_art_payload_pins.h'], text=True)
    pinrows = lambda s: re.findall(r'^ \{\d+,\d+,UINT64_C\(0x[0-9a-f]+\),UINT64_C\(0x[0-9a-f]+\),\d+,(?:UINT64_C\(0x[0-9a-f]+\)|0)\}', s, re.M)
    assert pinrows(shadow.resolve_current_payload_pins(source))[:35] == pinrows(shadow.resolve_current_payload_pins(prior, prior_header))[:35], 'Previous thirty-five shadow pins changed'
    wanted = [f' {{{i},{slot},UINT64_C(0x{src:016x}),UINT64_C(0x{rgba:016x}),0,0}}' for i, slot, src, rgba in PINS]
    assert pinrows(shadow.resolve_current_payload_pins(source))[35:] == wanted and len(pinrows(shadow.resolve_current_payload_pins(source))) == 45
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
    for i in shadow.OLD_IDS + (105, 106, 124, 125, 6, 44, 73, 63, 82, 16, 54, 130, 131, 149, 150, 223, 224, 242, 243, 143, 144, 27):
        shutil.copyfile(args.pack / f'bullet-{i}-8.hda', full / f'bullet-{i}-8.hda')
    for i in (225, 244, 226):
        shutil.copyfile(args.pack / f'protron-shadow-{i}-8.hda', full / f'protron-shadow-{i}-8.hda')
    (out / 'normal.bank8').write_bytes(normal)
    if christmas is not None: (out / 'christmas.bank8').write_bytes(christmas)
    paths = [out / 'normal.bank8', out / 'christmas.bank8' if christmas is not None else '-']
    (out / 'reference.bin').write_bytes(b''.join(base.decode(normal, i) for i in IDS))
    case = out / 'ten-weapon-test.c'
    case.write_text('#define TEN_WEAPON_SHADOW_BATCH 1\n#include "' + str(ROOT / 'tests/sonic_quadrant_shadow_test.c') + '"\n')
    shadow.CASE_SOURCE = case
    report = {'status': 'PASS', 'scope': '10 finite canonical head-alpha shadows; pairwise bounded geometry and exhaustive per-ID guard cases',
              'source_sha256': source_sha, 'christmas_sha256': christmas_sha, 'production_sha256': hashes,
              'unchanged_production_boundaries': boundaries, 'previous_thirty_five_pins_unchanged': True,
              'resource_variants': count, 'frozen_pins': receipts, 'runs': {}}
    report['runs']['optimized'] = shadow.build_run(out, paths, full, variants)
    print('optimized: ' + json.dumps(report['runs']['optimized']), flush=True)
    if args.sanitize:
        report['runs']['sanitized'] = shadow.build_run(out, paths, full, variants, True)
        print('sanitized: ' + json.dumps(report['runs']['sanitized']), flush=True)
        report['leak_checking'] = 'unavailable under executor ptrace; ASan/UBSan enabled'
    if args.mutants: report['guard_mutants'] = shadow.mutants(out, source, paths, full, variants, loader_mode=False)
    report['peak_child_rss_kib'] = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    assert report['peak_child_rss_kib'] < 512 * 1024
    assert shutil.disk_usage(out).free >= 5_000_000_000
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: ' + str(out / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
