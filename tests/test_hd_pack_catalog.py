#!/usr/bin/env python3
"""Bounded default/optional catalog regression; no original data or game build.

Only the explicit catalog entries are read. New fixtures stay below 1 MiB,
inside a required new output directory. Existing resources are never modified.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('hd_pack_catalog', ROOT / 'prototype/hd_pack_catalog.py')
CATALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CATALOG)
SHA = lambda data: hashlib.sha256(data).hexdigest()


def rejects(action, expected=(AssertionError, FileNotFoundError)):
    try:
        action()
    except expected:
        return
    raise AssertionError('Expected rejection')


def write(root, path, data):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.absolute()
    assert not out.exists() and not out.is_symlink() and out != ROOT and ROOT not in out.parents
    out.mkdir(parents=True)
    manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    assert set(manifest['packs']) == defaults
    assert [manifest['packs'][manifest[key]]['count'] for key in ('default_preview_pack', 'default_debug_pack')] == [629, 629]
    optional = CATALOG.verify_optional_inventory(manifest)
    assert len(optional['asteroid1-ten-v1']['files']) == 35
    actual = CATALOG.verify_pack_catalog(manifest, ROOT, defaults=False)
    assert actual['verified_HDA_entries'] == 0 and actual['verified_optional_HDA_entries'] == 35
    # Frozen metadata catches missing images, foreign rows and provenance changes.
    for mutation in ('missing', 'digest', 'scope'):
        changed = copy.deepcopy(manifest)
        pack = changed['optional_packs']['asteroid1-ten-v1']
        if mutation == 'missing':
            pack['files'].pop(next(iter(pack['files'])))
        elif mutation == 'digest':
            pack['files'][next(iter(pack['files']))]['sha256'] = '0' * 64
        else:
            pack['scope'] += ' altered'
        rejects(lambda: CATALOG.verify_optional_inventory(changed))
    # Reuse one existing exact PNG/HDR1 pair for tiny default-only fixtures.
    entry = manifest['packs'][manifest['default_preview_pack']]['files']['bullet-105-8.hda']
    png = (ROOT / entry['source_png']).read_bytes()
    hda = (ROOT / 'assets/hd/packs' / manifest['default_preview_pack'] / 'bullet-105-8.hda').read_bytes()
    row = dict(entry, source_png='assets/hd/source/catalog-fixture.png')
    fixture = {'default_preview_pack': 'fixture-preview', 'default_debug_pack': 'fixture-debug',
               'packs': {name: {'count': 1, 'files': {'bullet-105-8.hda': copy.deepcopy(row)}}
                         for name in ('fixture-preview', 'fixture-debug')}}
    default_root = out / 'default-only'
    source = write(default_root, row['source_png'], png)
    for name in fixture['packs']:
        write(default_root, Path('assets/hd/packs') / name / 'bullet-105-8.hda', hda)
    result = CATALOG.verify_pack_catalog(fixture, default_root)
    assert result['verified_HDA_entries'] == 2 and result['verified_optional_HDA_entries'] == 0
    runtime = default_root / 'assets/hd/packs/fixture-preview/bullet-105-8.hda'
    runtime.write_bytes(hda[:-1] + bytes([hda[-1] ^ 1]))
    rejects(lambda: CATALOG.verify_pack_catalog(fixture, default_root))
    runtime.write_bytes(hda)
    source.write_bytes(png + b'corrupt')
    rejects(lambda: CATALOG.verify_pack_catalog(fixture, default_root))
    source.write_bytes(png)
    missing = out / 'missing-default'
    write(missing, row['source_png'], png)
    rejects(lambda: CATALOG.verify_pack_catalog(fixture, missing))
    rejects(lambda: CATALOG.verify_pack_catalog(manifest, out / 'missing-optional', defaults=False))
    # Fallbacks fill absent files only. A corrupt local override cannot be hidden.
    pack = optional['asteroid1-ten-v1']
    filename, optional_row = next(iter(pack['files'].items()))
    corrupt = out / 'corrupt-optional-runtime'
    original = (ROOT / 'assets/hd/packs/asteroid1-ten-v1' / filename).read_bytes()
    write(corrupt, Path('assets/hd/packs/asteroid1-ten-v1') / filename,
          original[:-1] + bytes([original[-1] ^ 1]))
    rejects(lambda: CATALOG.verify_pack_catalog(manifest, corrupt, defaults=False, asset_roots=[ROOT]))
    corrupt = out / 'corrupt-optional-source'
    write(corrupt, optional_row['source_png'], (ROOT / optional_row['source_png']).read_bytes() + b'corrupt')
    rejects(lambda: CATALOG.verify_pack_catalog(manifest, corrupt, defaults=False, asset_roots=[ROOT]))
    command = [sys.executable, str(ROOT / 'prototype/build-hd-assets.py'), '--catalog-only', '--output', str(out / 'must-not-exist')]
    command_result = subprocess.run(command, capture_output=True, text=True)
    assert command_result.returncode != 0 and '--catalog-only cannot be combined with --output' in command_result.stderr
    assert not (out / 'must-not-exist').exists()
    report = {'status': 'PASS', 'current_default_catalog_counts': [629, 629],
              'real_optional_HDR1_and_source_PNG_pairs_verified': 35,
              'optional_catalog_sha256': CATALOG.ASTEROID1_OPTIONAL_CATALOG_SHA256,
              'synthetic_default_only_entries_verified': 2,
              'missing_and_corrupt_default_optional_cases_rejected': True,
              'existing_resources_unchanged': True,
              'scope': 'Finite catalog integration; complete historical default payload acceptance is separate.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
