#!/usr/bin/env python3
"""Cheap, read-only runtime/source metadata consistency check (not qualification).

This does not hash production files, load artwork, or replace the complete source,
package, or deterministic rebuild checks. It never updates acceptance metadata.
"""
import argparse
import hashlib
import json
from pathlib import Path
from verify_current_production import source_manifest_digest

SOURCE = 'packaging/current-production-validation.json'
DESTINATION = 'CURRENT-PRODUCTION-VALIDATION.json'
DIGEST = 'current_production_source_manifest_sha256'
ACTION = 'Runtime source binding inconsistent; rebuild the runtime manifest with scripts/rebuild_recovered_runtime_manifest.py into a separate output and review it (do not edit hashes by hand): '


def fail(reason):
    raise ValueError(ACTION + reason)


def read_object(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                fail('duplicate JSON key: ' + key)
            result[key] = value
        return result
    try:
        raw = path.read_bytes()
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda value: fail('nonfinite JSON value'))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail('cannot read JSON metadata: ' + str(error))
    if not isinstance(value, dict):
        fail('expected JSON object')
    return raw, value


def digest_string(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def check(root, manifest_path):
    root, manifest_path = Path(root).resolve(), Path(manifest_path)
    _, manifest = read_object(manifest_path)
    revision, rows = manifest.get('source_revision'), manifest.get('files')
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        fail('invalid runtime metadata shape')
    # Content markers keep renamed/copied current manifests in the current regime.
    selected = [row for row in rows if any(isinstance(row.get(key), str) and row[key].casefold() == value.casefold()
                for key, value in (('source_path', SOURCE), ('destination', DESTINATION), ('group', 'current-production-validation')))]
    current = manifest_path.resolve() == (root / 'packaging/runtime-assets-v1.json').resolve() or (isinstance(revision, dict) and DIGEST in revision) or bool(selected)
    if not current:
        return {'status': 'NOT_APPLICABLE', 'scope': 'historical/custom manifest without current binding markers'}
    if manifest.get('schema') != 'opentyrian-runtime-package-v1' or len(selected) != 1:
        fail('expected exactly one current production binding row')
    row = selected[0]
    if row.get('source_path') != SOURCE or row.get('destination') != DESTINATION or row.get('group') != 'current-production-validation':
        fail('noncanonical current production binding row')
    if not isinstance(revision, dict) or not digest_string(revision.get(DIGEST)):
        fail('missing or invalid current source revision digest')
    receipt_path = root / SOURCE
    if (root / 'packaging').is_symlink() or receipt_path.is_symlink() or not receipt_path.is_file():
        fail('expected regular current production receipt')
    raw, receipt = read_object(receipt_path)
    inventory = receipt.get('source_sha256')
    if receipt.get('schema') != 'opentyrian-current-production-binding-v1' or not isinstance(inventory, dict) or not inventory:
        fail('invalid current production receipt/inventory')
    if any(not isinstance(key, str) or not digest_string(value) for key, value in inventory.items()):
        fail('invalid declared source inventory entry')
    digest = source_manifest_digest(inventory)
    if receipt.get('production_source_manifest_sha256') != digest or revision[DIGEST] != digest:
        fail('top-level and declared production source digests differ')
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if type(row.get('bytes')) is not int or row['bytes'] != len(raw) or row.get('sha256') != hashlib.sha256(raw).hexdigest() or row.get('git_blob') != blob:
        fail('current production binding row does not match receipt bytes')
    return {'status': 'PASS', 'scope': 'metadata consistency only; full qualification still required', 'declared_source_files': len(inventory)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--manifest', type=Path)
    args = parser.parse_args()
    try:
        result = check(args.root, args.manifest or args.root / 'packaging/runtime-assets-v1.json')
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
