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
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('hd_pack_catalog', ROOT / 'prototype/hd_pack_catalog.py')
CATALOG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CATALOG)
SHA = lambda data: hashlib.sha256(data).hexdigest()


def rejects(action, expected=(AssertionError, FileNotFoundError), *, before_frozen=False):
    try:
        action()
    except expected as error:
        if before_frozen:
            assert str(error) != 'Frozen optional catalog changed', 'Identity exclusion must not rely on the frozen digest'
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
    parser.add_argument('--asset-root', action='append', type=Path, default=[])
    args = parser.parse_args()
    out = args.out.absolute()
    assert not out.exists() and not out.is_symlink() and out != ROOT and ROOT not in out.parents
    out.mkdir(parents=True)
    manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    assert set(manifest['packs']) == defaults
    assert [manifest['packs'][manifest[key]]['count'] for key in ('default_preview_pack', 'default_debug_pack')] == [629, 629]
    optional = CATALOG.verify_optional_inventory(manifest)
    assert len(optional['asteroid1-ten-v1']['files']) == 57
    actual = CATALOG.verify_pack_catalog(manifest, ROOT, defaults=False, asset_roots=args.asset_root)
    assert actual['verified_HDA_entries'] == 0 and actual['verified_optional_HDA_entries'] == 57
    # Frozen metadata catches missing images, foreign rows and provenance changes.
    mutations = ('missing', 'digest', 'scope', 'bank-filename', 'bank-identity', 'role-collision',
                 'newshp-material', 'newshp-header', 'newshp-default-collision',
                 'pulsing272-bank', 'pulsing272-source-bank', 'pulsing272-record',
                 'pulsing272-bases', 'pulsing272-material108', 'pulsing272-material135',
                 'pulsing272-header108', 'pulsing272-header135',
                 'firing325-header136', 'firing325-material136',
                 'newshd-header136', 'newshp-header136', 'pulsing272-default-collision',
                 'same-base-crossbank-swap', 'newshd-family-material136',
                 'newshd-family-bank23', 'newshs-foreign-filename', 'source-bank-provenance') + tuple(
                     f'pulsing272-missing-{base}' for base in (229, 231, 233, 235))
    for mutation in mutations:
        changed = copy.deepcopy(manifest)
        pack = changed['optional_packs']['asteroid1-ten-v1']
        if mutation == 'missing':
            pack['files'].pop(next(iter(pack['files'])))
        elif mutation == 'digest':
            pack['files'][next(iter(pack['files']))]['sha256'] = '0' * 64
        elif mutation == 'bank-filename':
            pack['files']['enemy-newshd-11-8.hda'] = pack['files'].pop('enemy-newshs-11-8.hda')
        elif mutation == 'bank-identity':
            pack['families']['firing325']['logical_bank'] = 8
        elif mutation == 'role-collision':
            pack['files']['enemy-newshs-11-8.hda']['header_u32'][0] = 1080277
        elif mutation == 'newshp-material':
            pack['families']['linked338']['material_role'] = 108
        elif mutation == 'newshp-header':
            pack['files']['enemy-newshp-121-8.hda']['header_u32'][0] = 1080121
        elif mutation == 'newshp-default-collision':
            next(iter(changed['packs'][changed['default_preview_pack']]['files'].values()))['header_u32'][0] = 1350121
        elif mutation == 'pulsing272-bank':
            pack['families']['pulsing272']['logical_bank'] = 8
        elif mutation == 'pulsing272-source-bank':
            pack['families']['pulsing272']['source_bank'] = 'newshp.shp'
        elif mutation == 'pulsing272-record':
            pack['families']['pulsing272']['source_records'] = [325]
        elif mutation == 'pulsing272-bases':
            pack['families']['pulsing272']['image_bases'][0] = 11
        elif mutation in ('pulsing272-material108', 'pulsing272-material135'):
            pack['families']['pulsing272']['material_role'] = int(mutation[-3:])
        elif mutation in ('pulsing272-header108', 'pulsing272-header135'):
            pack['files']['enemy-newshs-229-8.hda']['header_u32'][0] = int(mutation[-3:]) * 10000 + 229
        elif mutation == 'firing325-header136':
            pack['files']['enemy-newshs-11-8.hda']['header_u32'][0] = 1360011
        elif mutation == 'firing325-material136':
            pack['families']['firing325']['material_role'] = 136
        elif mutation == 'newshd-header136':
            pack['files']['enemy-newshd-229-8.hda']['header_u32'][0] = 1360229
        elif mutation == 'newshp-header136':
            pack['files']['enemy-newshp-229-8.hda']['header_u32'][0] = 1360229
        elif mutation == 'pulsing272-default-collision':
            next(iter(changed['packs'][changed['default_debug_pack']]['files'].values()))['header_u32'][0] = 1360235
        elif mutation == 'same-base-crossbank-swap':
            a, b = pack['files']['enemy-newshs-231-8.hda'], pack['files']['enemy-newshd-231-8.hda']
            a['header_u32'], b['header_u32'] = b['header_u32'], a['header_u32']
        elif mutation == 'newshd-family-material136':
            pack['families']['random286']['material_role'] = 136
        elif mutation == 'newshd-family-bank23':
            pack['families']['random286']['logical_bank'] = 23
        elif mutation == 'newshs-foreign-filename':
            pack['files']['enemy-newshp-235-8.hda'] = pack['files'].pop('enemy-newshs-235-8.hda')
        elif mutation.startswith('pulsing272-missing-'):
            pack['files'].pop(f'enemy-newshs-{mutation.rsplit("-", 1)[1]}-8.hda')
        elif mutation == 'source-bank-provenance':
            pack['files']['enemy-newshs-229-8.hda']['source_png'] = pack['files']['enemy-newshd-229-8.hda']['source_png']
        else:
            pack['scope'] += ' altered'
        rejects(lambda: CATALOG.verify_optional_inventory(changed),
                before_frozen=mutation not in ('digest', 'scope', 'source-bank-provenance'))
    # Reuse one existing exact PNG/HDR1 pair for tiny default-only fixtures.
    entry = manifest['packs'][manifest['default_preview_pack']]['files']['bullet-105-8.hda']
    def resource(path):
        for root in [ROOT, *args.asset_root]:
            candidate = root / path
            if candidate.exists() or candidate.is_symlink():
                return candidate.read_bytes()
        raise FileNotFoundError(path)
    png = resource(entry['source_png'])
    hda = resource(Path('assets/hd/packs') / manifest['default_preview_pack'] / 'bullet-105-8.hda')
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
    # Each new resource is independently protected from local corrupt overrides.
    # The fallback fills absent catalog paths but must never hide these bytes.
    resource_rejections = []
    for base in (229, 231, 233, 235):
        filename = f'enemy-newshs-{base}-8.hda'
        row = pack['files'][filename]
        original = (ROOT / 'assets/hd/packs/asteroid1-ten-v1' / filename).read_bytes()
        corrupt = out / f'pulsing272-corrupt-{base}'
        path = Path('assets/hd/packs/asteroid1-ten-v1') / filename
        variants = {
            'material108': original[:4] + struct.pack('<I', 1080000 + base) + original[8:],
            'material135': original[:4] + struct.pack('<I', 1350000 + base) + original[8:],
            'density': original[:8] + struct.pack('<I', 4) + original[12:],
            'anchor': original[:20] + struct.pack('<I', 1) + original[24:],
            'short': original[:-1], 'long': original + b'corrupt',
            'payload': original[:-1] + bytes([original[-1] ^ 1]),
        }
        for name, raw in variants.items():
            write(corrupt, path, raw)
            rejects(lambda: CATALOG.verify_pack_catalog(manifest, corrupt, defaults=False, asset_roots=[ROOT]))
            resource_rejections.append(f'{base}:{name}')
        write(corrupt, path, original)
        png = (ROOT / row['source_png']).read_bytes()
        write(corrupt, row['source_png'], png + b'corrupt')
        rejects(lambda: CATALOG.verify_pack_catalog(manifest, corrupt, defaults=False, asset_roots=[ROOT]))
        resource_rejections.append(f'{base}:source-png')
        write(corrupt, row['source_png'], png)
        assert CATALOG.verify_pack_catalog(manifest, corrupt, defaults=False, asset_roots=[ROOT])['verified_optional_HDA_entries'] == 57
    command = [sys.executable, str(ROOT / 'prototype/build-hd-assets.py'), '--catalog-only', '--output', str(out / 'must-not-exist')]
    command_result = subprocess.run(command, capture_output=True, text=True)
    assert command_result.returncode != 0 and '--catalog-only cannot be combined with --output' in command_result.stderr
    assert not (out / 'must-not-exist').exists()
    report = {'status': 'PASS', 'current_default_catalog_counts': [629, 629],
              'real_optional_HDR1_and_source_PNG_pairs_verified': 57,
              'optional_catalog_sha256': CATALOG.ASTEROID1_OPTIONAL_CATALOG_SHA256,
              'metadata_mutations_rejected': list(mutations),
              'explicit_family_base_material_identity_checks_before_frozen_digest': True,
              'pulsing272_resource_mutations_rejected': resource_rejections,
              'NEWSHS_family_materials': {'firing325': 108, 'pulsing272': 136},
              'synthetic_default_only_entries_verified': 2,
              'missing_and_corrupt_default_optional_cases_rejected': True,
              'existing_resources_unchanged': True,
              'scope': 'Finite catalog integration; complete historical default payload acceptance is separate.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
