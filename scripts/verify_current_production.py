#!/usr/bin/env python3
"""Verify a fixed source inventory, not generate acceptance from mutable files.

Historical validation receipts retain their original scope. This binding covers
every file below src recursively (including non-code files), never Git's ignore
rules or a suffix allowlist. It is not a new runtime or platform acceptance test.
"""
import argparse
import hashlib
import json
from pathlib import Path

BUILD_INPUTS = ('Makefile', 'visualc/opentyrian.vcxproj',
                'assets/hd/shared-menu-runs-v1/reconstructed_run_specs.h',
                'assets/hd/shared-menu-runs-v1/reconstructed_numeric_specs.h',
                'assets/hd/shared-menu-runs-v1/reconstructed_name_source_specs.h')


def source_inventory(root):
    source = root / 'src'
    if source.is_symlink() or not source.is_dir():
        raise ValueError('Expected regular source directory')
    result = {}
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlink in production source: ' + str(path))
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError('Nonregular production source: ' + str(path))
        result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def source_manifest_digest(inventory):
    """SHA256 of UTF-8 JSON, sorted keys, compact separators, no newline."""
    return hashlib.sha256(json.dumps(inventory, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')).hexdigest()


def verify(root, receipt):
    if receipt['schema'] != 'opentyrian-current-production-binding-v1':
        raise ValueError('Unexpected production binding schema')
    if set(receipt['historical_validation_sha256']) != {
            'packaging/frontend-validation.json', 'packaging/global-validation.json'}:
        raise ValueError('Expected both historical validation bindings')
    if set(receipt['build_input_sha256']) != set(BUILD_INPUTS):
        raise ValueError('Expected exact external build input bindings')
    for name, digest in receipt['build_input_sha256'].items():
        path = root / name
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Build input changed: ' + name)
    actual = source_inventory(root)
    expected = receipt['source_sha256']
    if ('production_source_manifest_sha256' in receipt and
            receipt['production_source_manifest_sha256'] != source_manifest_digest(expected)):
        raise ValueError('Production source manifest digest mismatch')
    if actual != expected:
        raise ValueError('Production source mismatch: missing=%s extra=%s changed=%s' % (
            sorted(expected.keys() - actual.keys()), sorted(actual.keys() - expected.keys()),
            sorted(p for p in actual.keys() & expected.keys() if actual[p] != expected[p])))
    for name, digest in receipt['historical_validation_sha256'].items():
        if name not in ('packaging/frontend-validation.json', 'packaging/global-validation.json'):
            raise ValueError('Unexpected historical receipt path')
        path = root / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Historical validation changed: ' + name)
    return len(actual)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    receipt = json.loads((args.root / 'packaging/current-production-validation.json').read_text())
    count = verify(args.root, receipt)
    print(json.dumps({'status': 'PASS', 'source_files': count, 'scope': 'exact source binding only'}))


if __name__ == '__main__':
    main()
