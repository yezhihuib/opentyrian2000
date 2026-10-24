#!/usr/bin/env python3
"""Build an allowlisted, verified runtime copy. Never modifies source files.

Default is a dry run. This tool has no network, delete, overwrite or Git actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile

MIB = 1024 * 1024
RUNTIME_LIMIT = 512 * MIB
BUILD_LIMIT = 1024 * MIB
FREE_RESERVE = 4 * 1024 * MIB
RESERVED_OUTPUTS = {'runtime-inventory.json', 'runtime-status.json', 'incomplete', 'copy-verified.txt'}
WINDOWS_DEVICES = {'CON', 'PRN', 'AUX', 'NUL'} | {f'{prefix}{number}' for prefix in ('COM', 'LPT') for number in range(1, 10)}


def relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or '\\' in value or '..' in path.parts or str(path) != value:
        raise ValueError(f'Unsafe relative path: {value!r}')
    for component in path.parts:
        if any(ord(c) < 32 or c in '<>:\"|?*' for c in component) or component.endswith((' ', '.')) or component.split('.')[0].upper() in WINDOWS_DEVICES:
            raise ValueError(f'Unsafe cross-platform path component: {component!r}')
    return value


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def fingerprints(path: Path, expected_bytes: int) -> tuple[str, str]:
    # Do not follow symlinks or accept devices/FIFOs. Bound size before opening.
    mode = path.lstat()
    if not stat.S_ISREG(mode.st_mode) or mode.st_size != expected_bytes:
        raise ValueError(f'Not a regular file of {expected_bytes} bytes: {path}')
    sha1 = hashlib.sha1(b'blob ' + str(expected_bytes).encode('ascii') + b'\0')
    sha256 = hashlib.sha256()
    with path.open('rb') as stream:
        remaining = expected_bytes
        while remaining:
            chunk = stream.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError(f'Truncated source: {path}')
            sha1.update(chunk)
            sha256.update(chunk)
            remaining -= len(chunk)
        if stream.read(1):
            raise ValueError(f'Source grew during verification: {path}')
    return sha1.hexdigest(), sha256.hexdigest()


def checked_source(path: Path, row: dict) -> dict:
    blob, sha256 = fingerprints(path, row['bytes'])
    if blob != row['git_blob'] or (row.get('sha256') and sha256 != row['sha256']):
        raise ValueError(f'Content fingerprint mismatch: {path}')
    return {**row, 'source': str(path), 'sha256': sha256}


def reparse_point(path: Path) -> bool:
    try:
        return bool(getattr(path.lstat(), 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024))
    except FileNotFoundError:
        return False


def contained_file(root: Path, value: str) -> Path:
    path = root / relative_path(value)
    # Reject symlinks in *any* component, including a directory symlink.
    cursor = root
    if root.is_symlink() or reparse_point(root):
        raise ValueError(f'Reparse or symlink root is not accepted: {root}')
    for component in PurePosixPath(value).parts:
        cursor = cursor / component
        if cursor.is_symlink():
            raise ValueError(f'Symlink source is not accepted: {cursor}')
        # Windows directory junctions are reparse points but are not symlinks
        # on Python 3.11. Reject aliases before reading or replacing outputs.
        if reparse_point(cursor):
            raise ValueError(f'Reparse source is not accepted: {cursor}')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Source resolves outside root: {path}')
    return path


def load_manifest(path: Path) -> dict:
    manifest = read_json(path)
    if manifest.get('schema') != 'opentyrian-runtime-package-v1':
        raise ValueError('Unrecognized runtime manifest schema')
    rows = manifest['files']
    if not rows or len(rows) > 4096:
        raise ValueError('Empty or oversized manifest')
    destinations = set()
    destination_parts = []
    for row in rows:
        relative_path(row['source_path'])
        destination = relative_path(row['destination'])
        normalized = destination.casefold()
        if normalized in destinations or PurePosixPath(destination).parts[0].casefold() in RESERVED_OUTPUTS:
            raise ValueError(f'Duplicate or reserved destination: {destination}')
        parts = tuple(part.casefold() for part in PurePosixPath(destination).parts)
        if any(parts[:len(old)] == old or old[:len(parts)] == parts for old in destination_parts):
            raise ValueError(f'File/directory destination collision: {destination}')
        destination_parts.append(parts)
        destinations.add(normalized)
        if not isinstance(row['bytes'], int) or not 0 <= row['bytes'] <= 64 * MIB:
            raise ValueError('Invalid or oversized file length')
        if len(row['git_blob']) != 40 or any(c not in '0123456789abcdef' for c in row['git_blob']):
            raise ValueError('Invalid Git blob SHA1')
    if sum(row['bytes'] for row in rows) > RUNTIME_LIMIT:
        raise ValueError('Manifest exceeds the 512 MiB runtime limit')
    return manifest



def content_catalog(verified: list[dict], platform: str) -> dict:
    """Project fully verified files into whole-byte identities, never aliases.

    The caller must first complete checked_source for every selected file.
    Resolved local paths and source roots are intentionally not serialized.
    HDA headers/anchors participate in the hash just like all other bytes.
    """
    contents = {}
    files = []
    for row in sorted(verified, key=lambda r: r['destination']):
        digest = row['sha256']
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Invalid content SHA256')
        identity = f"sha256:{digest}:{row['bytes']}"
        item = contents.setdefault(identity, {'id': identity, 'sha256': digest, 'bytes': row['bytes'], 'destinations': []})
        item['destinations'].append(row['destination'])
        files.append({key: row[key] for key in ('source_path', 'destination', 'group', 'bytes', 'git_blob', 'sha256')} | {'content_id': identity})
    groups = sorted(contents.values(), key=lambda item: item['id'])
    duplicates = [item for item in groups if len(item['destinations']) > 1]
    logical_bytes = sum(row['bytes'] for row in files)
    unique_bytes = sum(item['bytes'] for item in groups)
    return {
        'schema': 'opentyrian-runtime-content-catalog-v1',
        'platform': platform,
        'identity_scope': 'whole-file bytes including headers; not role, lifetime or rendering authority',
        'storage_policy': 'audit only; keep all logical paths as separate regular files',
        'summary': {
            'logical_files': len(files), 'unique_contents': len(groups),
            'duplicate_groups': len(duplicates),
            'duplicate_participating_files': sum(len(item['destinations']) for item in duplicates),
            'logical_bytes': logical_bytes, 'unique_content_bytes': unique_bytes,
            'duplicate_bytes': logical_bytes - unique_bytes,
            'bytes_saved_by_this_tool': 0,
        },
        'contents': groups, 'files': files,
    }


def catalog_bytes(catalog: dict) -> bytes:
    return (json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=True) + '\n').encode('utf-8')


def read_content_catalog(path: Path) -> dict:
    """Bounded snapshot input. It never controls which files are packaged."""
    path = path.absolute()
    if path.resolve() != path or not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Catalog snapshot must be a regular file without symlink components')
    if path.stat().st_size > 16 * MIB:
        raise ValueError('Catalog snapshot exceeds 16 MiB')
    # Reject duplicate JSON keys rather than silently accepting one value.
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate catalog JSON key: ' + key)
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('Non-finite catalog JSON number: ' + value)
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_keys, parse_constant=invalid_constant)


def parent_for_new(path: Path) -> Path:
    if path.exists() or path.is_symlink():
        raise ValueError(f'Output already exists; choose a new path: {path}')
    if not path.parent.is_dir():
        raise ValueError(f'Output parent does not exist: {path.parent}')
    if path.parent.resolve() != path.parent.absolute():
        raise ValueError(f'Output parent contains a symlink: {path.parent}')
    return path.parent


def assert_external(path: Path, roots: list[Path]):
    for root in roots:
        if path == root or root in path.parents:
            raise ValueError(f'Output must be outside each source root: {path}')


def zip_directory(directory: Path, target: Path):
    # Stable timestamps, ordering, permissions and compression parameters.
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(directory.rglob('*')):
            if not path.is_file():
                continue
            name = path.relative_to(directory).as_posix()
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | (0o755 if name.endswith('.sh') or name == 'opentyrian2000' else 0o644)) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info._compresslevel = 9
            with path.open('rb') as source, archive.open(info, 'w') as output:
                shutil.copyfileobj(source, output, 1024 * 1024)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--asset-root', action='append', type=Path, default=[], help='Additional repository-layout source roots')
    parser.add_argument('--source-map', type=Path, help='Explicit source_path -> existing local regular file mapping; every byte is verified')
    parser.add_argument('--manifest', type=Path, help='Defaults to SOURCE_ROOT/packaging/runtime-assets-v1.json')
    parser.add_argument('--executable', type=Path, help='Optional prebuilt binary; no build or dependency downloads are performed')
    parser.add_argument('--platform', choices=['linux', 'windows'], default='linux')
    parser.add_argument('--build', action='store_true', help='Create a new runtime copy; otherwise dry run')
    parser.add_argument('--output', type=Path, help='New directory outside all source roots')
    parser.add_argument('--zip', type=Path, help='Optional new deterministic ZIP, outside source roots and output')
    parser.add_argument('--content-catalog', type=Path, help='Export a new verified whole-file content catalog outside source roots; no storage changes')
    parser.add_argument('--check-content-catalog', type=Path, help='Require an existing catalog to match this fully verified selection exactly')
    parser.add_argument('--report', type=Path, help='Optional new JSON report outside source roots')
    args = parser.parse_args(argv)
    roots = [args.source_root.resolve()] + [p.resolve() for p in args.asset_root]
    manifest_path = args.manifest or roots[0] / 'packaging/runtime-assets-v1.json'
    manifest = load_manifest(manifest_path)
    # Default deployment and explicit current Sonic references require the
    # complete current quartet. Historical/custom manifests retain their frozen
    # semantics and need no current authoring inputs. This packages resources;
    # it does not change the executable's default-off renderer eligibility.
    sonic_prefix = 'assets/hd/current-compat/sonic/'
    sonic_names = {f'bullet-{i}-8.hda' for i in (105,106,124,125)}
    sonic_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in sonic_names for key in ('destination','source_path')) or
        row['source_path'].casefold().startswith(sonic_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-sonic')]
    sonic_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(sonic_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-sonic')
        for row in manifest['files'])
    if sonic_current:
        from current_sonic_compatibility import load as sonic_load
        expected = {'assets/gameplay/'+name for name in sonic_names}
        if len(sonic_rows)!=4 or {row['destination'] for row in sonic_rows}!=expected:
            raise ValueError('Sonic packaging requires exactly four current consumers')
        selected = sonic_load(roots[0])
        for row in sonic_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-sonic'):
                raise ValueError('Stale Sonic runtime selection')
    # Guided replaces four existing destinations; no new runtime resources.
    guided_prefix = 'assets/hd/current-compat/guided/'
    guided_names = {f'bullet-{i}-8.hda' for i in (19,171,20,21)}
    guided_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in guided_names for key in ('destination','source_path')) or
        row['source_path'].casefold().startswith(guided_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-guided')]
    guided_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(guided_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-guided')
        for row in manifest['files'])
    if guided_current:
        from current_guided_compatibility import load as guided_load
        expected = {'assets/gameplay/'+name for name in guided_names}
        if len(guided_rows)!=4 or {row['destination'] for row in guided_rows}!=expected:
            raise ValueError('Guided packaging requires exactly four current consumers')
        selected = guided_load(roots[0])
        for row in guided_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-guided'):
                raise ValueError('Stale Guided runtime selection')
    # Mint27 replaces one existing destination; no new runtime resources.
    mint27_prefix = 'assets/hd/current-compat/mint27/'
    mint27_names = {f'bullet-{i}-8.hda' for i in (27,)}
    mint27_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in mint27_names for key in ('destination','source_path')) or
        row['source_path'].casefold().startswith(mint27_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-mint27')]
    mint27_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(mint27_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-mint27')
        for row in manifest['files'])
    if mint27_current:
        from current_mint27_compatibility import load as mint27_load
        expected = {'assets/gameplay/'+name for name in mint27_names}
        if len(mint27_rows)!=1 or {row['destination'] for row in mint27_rows}!=expected:
            raise ValueError('Mint27 packaging requires exactly one current consumer')
        selected = mint27_load(roots[0])
        for row in mint27_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-mint27'):
                raise ValueError('Stale Mint27 runtime selection')
    # Missile replaces three existing destinations; no new runtime resources.
    missile_prefix = 'assets/hd/current-compat/missile/'
    missile_names = {f'bullet-{i}-8.hda' for i in (31,32,33)}
    missile_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in missile_names for key in ('destination','source_path')) or
        row['source_path'].casefold().startswith(missile_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-missile')]
    missile_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(missile_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-missile')
        for row in manifest['files'])
    if missile_current:
        from current_missile_compatibility import load as missile_load
        expected = {'assets/gameplay/'+name for name in missile_names}
        if len(missile_rows)!=3 or {row['destination'] for row in missile_rows}!=expected:
            raise ValueError('Missile packaging requires exactly three current consumers')
        selected = missile_load(roots[0])
        for row in missile_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-missile'):
                raise ValueError('Stale Missile runtime selection')
    # Rear P7 replaces four existing destinations; no new runtime resources.
    rear_p7_prefix = 'assets/hd/current-compat/rear-p7/'
    rear_p7_names = {f'rear-multicannon-p1-bank8-{i}-{d}.hda' for i in (294,295) for d in (4,8)}
    rear_p7_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in rear_p7_names for key in ('destination','source_path')) or
        row['source_path'].casefold().startswith(rear_p7_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-rear-p7')]
    rear_p7_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(rear_p7_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-rear-p7')
        for row in manifest['files'])
    if rear_p7_current:
        from current_rear_p7_compatibility import load as rear_p7_load
        expected = {'assets/gameplay/'+name for name in rear_p7_names}
        if len(rear_p7_rows)!=4 or {row['destination'] for row in rear_p7_rows}!=expected:
            raise ValueError('Rear P7 packaging requires exactly four current consumers')
        selected = rear_p7_load(roots[0])
        for row in rear_p7_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-rear-p7'):
                raise ValueError('Stale Rear P7 runtime selection')
    # Rear39 replaces six existing destinations; no new runtime resources.
    rear39_prefix = 'assets/hd/current-compat/rear39/'
    rear39_names = {f'rear-multicannon-p1-bank8-{i}-{d}.hda' for i in (39,40,41) for d in (4,8)}
    rear39_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in rear39_names for key in ('destination','source_path')) or
        row['source_path'].casefold().startswith(rear39_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-rear39')]
    rear39_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(rear39_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-rear39')
        for row in manifest['files'])
    if rear39_current:
        from current_rear39_compatibility import load as rear39_load
        expected = {'assets/gameplay/'+name for name in rear39_names}
        if len(rear39_rows)!=6 or {row['destination'] for row in rear39_rows}!=expected:
            raise ValueError('Rear39 packaging requires exactly six current consumers')
        selected = rear39_load(roots[0])
        for row in rear39_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-rear39'):
                raise ValueError('Stale Rear39 runtime selection')
    # Current NEWSHF keeps the same nine opt-in destinations, with six poses
    # derived from two authored three-pose masters and three frozen 168 V4 PNGs.
    # The older revision marker also appears in historical manifests, so it
    # selects members but does not itself opt those manifests into this contract.
    newshf_prefix = 'assets/hd/current-compat/newshf/'
    newshf_names = {f'newshf-role{i}-8.hda' for i in range(2100000, 2100009)}
    newshf_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in newshf_names for key in ('destination', 'source_path')) or
        row['source_path'].casefold().startswith(newshf_prefix) or
        (isinstance(row.get('revision'), str) and row['revision'].casefold() == 'current-single-source-newshf-nine')]
    newshf_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(newshf_prefix) for row in manifest['files'])
    if newshf_current:
        from current_newshf_compatibility import load as newshf_load
        expected = {'assets/global/newshf/'+name for name in newshf_names}
        if len(newshf_rows) != 9 or {row['destination'] for row in newshf_rows} != expected:
            raise ValueError('NEWSHF packaging requires exactly nine current consumers')
        selected = newshf_load(roots[0])
        for row in newshf_rows:
            current = selected[row['destination']]
            if (row['source_path'] != current['source_path'] or row.get('sha256') != current['sha256'] or
                    row.get('group') != 'newshf-optin' or row.get('revision') != 'current-single-source-newshf-nine'):
                raise ValueError('Stale NEWSHF runtime selection')
    if args.content_catalog or args.check_content_catalog:
        for row in manifest['files']:
            if 'sha256' in row:
                digest = row['sha256']
                if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                    raise ValueError('Invalid manifest content SHA256')
    # Historical/custom manifests with no Charge consumers retain their exact
    # generic semantics. Any Charge request must close over all nine current
    # consumers and prove their source pixels, not only transport hashes.
    charge_rows = [row for row in manifest['files'] if
                   Path(row['destination']).name.casefold().startswith('option-charge-') or
                   Path(row['source_path']).name.casefold().startswith('option-charge-')]
    if charge_rows:
        from current_sidekick_body_compatibility import charge_load, CHARGE_IDS, charge_name
        expected = {'assets/gameplay/'+charge_name(i) for i in CHARGE_IDS}
        if len(charge_rows)!=9 or {row['destination'] for row in charge_rows}!=expected:
            raise ValueError('Charge packaging requires exactly nine current consumers')
        selected = charge_load(roots[0])
        for row in charge_rows:
            current = selected[row['destination']]
            if row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256']:
                raise ValueError('Stale Charge runtime selection')
    # Historical manifests retain their original Mint/Front pack semantics.
    # Current authoring references opt into the complete four-consumer closure;
    # the default current manifest cannot silently remove every such reference.
    mf_prefix = 'assets/hd/current-compat/mint-front-body/'
    mf_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold().startswith(('option-mint-', 'option-frontblaster-'))
        for key in ('destination', 'source_path')) or
        row['source_path'].casefold().startswith(mf_prefix)]
    mf_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(mf_prefix) or
        (isinstance(row.get('revision'), str) and
         row['revision'].casefold() == 'current-single-source-mint-front-body')
        for row in manifest['files'])
    if mf_current:
        from current_sidekick_body_compatibility import MF_IDS, mf_name, mf_load
        expected = {'assets/gameplay/'+mf_name(i) for i in MF_IDS}
        if len(mf_rows)!=4 or {row['destination'] for row in mf_rows}!=expected:
            raise ValueError('Mint/Front packaging requires exactly four current consumers')
        selected = mf_load(roots[0])
        for row in mf_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-mint-front-body'):
                raise ValueError('Stale Mint/Front runtime selection')
    # The six Plasma projectile consumers already exist historically. Only
    # current references/default deployment opt into the single-master closure;
    # frozen/custom manifests with historical rows retain generic semantics.
    plasma_prefix = 'assets/hd/current-compat/plasma-projectile/'
    plasma_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold().startswith('option-plasma-projectile-')
        for key in ('destination', 'source_path')) or
        row['source_path'].casefold().startswith(plasma_prefix)]
    plasma_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(plasma_prefix) or
        (isinstance(row.get('revision'), str) and
         row['revision'].casefold() == 'current-single-source-plasma-projectile')
        for row in manifest['files'])
    if plasma_current:
        from current_plasma_projectile_compatibility import PAIRS, name as plasma_name, load as plasma_load
        expected = {'assets/gameplay/'+plasma_name(i,d) for i,d in PAIRS}
        if len(plasma_rows)!=6 or {row['destination'] for row in plasma_rows}!=expected:
            raise ValueError('Plasma packaging requires exactly six current consumers')
        selected = plasma_load(roots[0])
        for row in plasma_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-plasma-projectile'):
                raise ValueError('Stale Plasma runtime selection')
    # Front Multi only opts into exact8 current closure for default deployment
    # or explicit current references. Frozen/custom bullet manifests still work
    # standalone, without importing today's authoring module or its inputs.
    front_multi_prefix = 'assets/hd/current-compat/front-multi/'
    front_multi_names = {f'bullet-{identity}-8.hda' for identity in (121,122,163,164,201,202,279,280)}
    front_multi_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in front_multi_names for key in ('destination','source_path')) or
        row['source_path'].casefold().startswith(front_multi_prefix)]
    front_multi_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(front_multi_prefix) or
        (isinstance(row.get('revision'),str) and row['revision'].casefold() == 'current-single-source-front-multi')
        for row in manifest['files'])
    if front_multi_current:
        from current_front_multi_compatibility import IDS, name as front_multi_name, load as front_multi_load
        expected = {'assets/gameplay/'+front_multi_name(identity) for identity in IDS}
        if len(front_multi_rows)!=8 or {row['destination'] for row in front_multi_rows}!=expected:
            raise ValueError('Front Multi packaging requires exactly eight current consumers')
        selected = front_multi_load(roots[0])
        for row in front_multi_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-front-multi'):
                raise ValueError('Stale Front Multi runtime selection')
    # Ordinary role8 is mandatory only for the default/current selection.
    # Role142 remains an explicit opt-in pair; historical pack manifests retain
    # their frozen semantics and never acquire current authoring dependencies.
    orb_prefix = 'assets/hd/current-compat/enemy-orb/'
    orb_names = {'bullet-112-8.hda', 'bullet-113-8.hda',
                 'enemy-orb112113-112-8.hda', 'enemy-orb112113-113-8.hda'}
    orb_rows = [row for row in manifest['files'] if any(
        Path(row[key]).name.casefold() in orb_names for key in ('destination', 'source_path')) or
        row['source_path'].casefold().startswith(orb_prefix)]
    orb_current = manifest_path.resolve() == (roots[0]/'packaging/runtime-assets-v1.json').resolve() or any(
        row['source_path'].casefold().startswith(orb_prefix) or
        (isinstance(row.get('revision'), str) and row['revision'].casefold() == 'current-single-source-enemy-orb')
        for row in manifest['files'])
    if orb_current:
        from current_enemy_orb_compatibility import ORDINARY_IDS, OPTIN_IDS, name as orb_name, load as orb_load
        ordinary = {'assets/gameplay/'+orb_name(identity) for identity in ORDINARY_IDS}
        optin = {'assets/gameplay/'+orb_name(identity) for identity in OPTIN_IDS}
        expected = ordinary
        if any(Path(row[key]).name.casefold().startswith('enemy-orb112113-')
               for row in orb_rows for key in ('destination', 'source_path')):
            expected = ordinary | optin
        if len(orb_rows)!=len(expected) or {row['destination'] for row in orb_rows}!=expected:
            raise ValueError('Enemy orb packaging requires ordinary pair and complete explicitly selected opt-in pair')
        selected = orb_load(roots[0])
        for row in orb_rows:
            current = selected[row['destination']]
            if (row['source_path']!=current['source_path'] or row.get('sha256')!=current['sha256'] or
                    row.get('group')!='gameplay' or row.get('revision')!='current-single-source-enemy-orb'):
                raise ValueError('Stale enemy orb runtime selection')
    source_map = read_json(args.source_map) if args.source_map else {}
    verified, missing = [], []
    for row in manifest['files']:
        candidates = [contained_file(root, row['source_path']) for root in roots]
        if row['source_path'] in source_map:
            mapped = Path(source_map[row['source_path']]).absolute()
            # A mapped source is explicitly selected, but must still be regular, unlinked and hashed.
            if mapped.resolve() != mapped:
                raise ValueError(f'Mapped source contains symlinks: {mapped}')
            candidates.append(mapped)
        errors = []
        for candidate in candidates:
            if not candidate.exists():
                continue
            try:
                verified.append(checked_source(candidate, row))
                break
            except (OSError, ValueError) as error:
                errors.append(str(error))
        else:
            missing.append({'source_path': row['source_path'], 'bytes': row['bytes'], 'errors': errors})
    if args.executable:
        binary_destination = 'opentyrian2000.exe' if args.platform == 'windows' else 'opentyrian2000'
        if any(row['destination'].casefold() == binary_destination.casefold() or row['destination'].casefold().startswith(binary_destination.casefold() + '/') for row in manifest['files']):
            raise ValueError('Selected manifest collides with the explicit executable destination')
        binary = args.executable.absolute()
        size = binary.stat().st_size
        if not 0 < size <= 64 * MIB:
            raise ValueError('Invalid executable size')
        blob, sha256 = fingerprints(binary, size)
        verified.append({'source_path': '(explicit prebuilt executable)', 'destination': binary_destination, 'bytes': size, 'git_blob': blob, 'sha256': sha256, 'source': str(binary), 'group': 'executable'})
    # Opt-in catalog runs after complete byte verification and before any writes.
    # Default report, runtime metadata, inventory and archive remain unchanged.
    catalog_output = None
    catalog_payload = None
    if args.content_catalog or args.check_content_catalog:
        if missing:
            raise ValueError('Refusing catalog for incomplete or mismatched runtime selection')
        catalog = content_catalog(verified, args.platform)
        if args.check_content_catalog:
            snapshot = read_content_catalog(args.check_content_catalog)
            if catalog_bytes(snapshot) != catalog_bytes(catalog):
                raise ValueError('Content catalog drift: selection, logical metadata or whole-file identity changed')
        if args.content_catalog:
            catalog_output = args.content_catalog.absolute()
            parent_for_new(catalog_output)
            assert_external(catalog_output, roots)
            # Prevent aliases/nesting among outputs before any directory is made.
            other_paths = [p.absolute() for p in (args.output, args.zip, args.report, args.check_content_catalog) if p]
            for other in other_paths:
                if catalog_output == other or catalog_output in other.parents or other in catalog_output.parents:
                    raise ValueError('Catalog path overlaps another input/output path')
            catalog_payload = catalog_bytes(catalog)
    expected = sum(row['bytes'] for row in manifest['files']) + (size if args.executable else 0)
    if expected > RUNTIME_LIMIT:
        raise ValueError('Runtime selection exceeds 512 MiB')
    report = {'schema': 'opentyrian-runtime-preflight-v1', 'mode': 'build' if args.build else 'dry-run', 'assets_complete': not missing, 'expected_files': len(manifest['files']) + bool(args.executable), 'expected_payload_bytes': expected, 'verified_files': len(verified), 'verified_payload_bytes': sum(row['bytes'] for row in verified), 'missing': missing, 'executable_included': bool(args.executable), 'platform': args.platform, 'external_dependencies': manifest['external_dependencies'], 'source_unchanged': True}
    if args.zip and not args.build:
        raise ValueError('--zip requires --build')
    if args.report:
        report_path = args.report.absolute()
        parent_for_new(report_path)
        assert_external(report_path, roots)
    if args.build:
        if missing:
            raise ValueError(f'Refusing incomplete runtime: {len(missing)} missing or mismatched files; run dry-run for details')
        if not args.output:
            raise ValueError('--build requires --output')
        output = args.output.absolute()
        parent = parent_for_new(output)
        assert_external(output, roots)
        if args.zip:
            archive = args.zip.absolute()
            parent_for_new(archive)
            assert_external(archive, roots + [output])
            if archive == output:
                raise ValueError('Archive path equals output path')
        # The extra 1 MiB covers inventory/report metadata; ZIP upper bound is conservative.
        worst_build = 2 * (expected + MIB) if args.zip else expected + MIB
        if worst_build > BUILD_LIMIT:
            raise ValueError('Directory plus archive exceeds 1 GiB build budget')
        if shutil.disk_usage(parent).free < FREE_RESERVE + worst_build:
            raise ValueError('Build would leave less than 4 GiB free')
        output.mkdir()
        # A failed copy leaves a marked incomplete directory, never deletes/replaces it.
        marker = output / 'INCOMPLETE'
        marker.write_text('If named INCOMPLETE, copying has not finished. If named COPY-VERIFIED.txt, every selected copied file passed hash verification. External dependency and runtime acceptance limits remain in RUNTIME-STATUS.json.\n', encoding='utf-8')
        inventory = []
        for row in sorted(verified, key=lambda r: r['destination']):
            destination = output / row['destination']
            destination.parent.mkdir(parents=True, exist_ok=True)
            with Path(row['source']).open('rb') as source, destination.open('xb') as target:
                remaining = row['bytes']
                while remaining:
                    chunk = source.read(min(MIB, remaining))
                    if not chunk:
                        raise ValueError(f'Source truncated during copy: {destination}')
                    target.write(chunk)
                    remaining -= len(chunk)
                if source.read(1):
                    raise ValueError(f'Source grew during copy: {destination}')
            blob, sha256 = fingerprints(destination, row['bytes'])
            if blob != row['git_blob'] or sha256 != row['sha256']:
                raise ValueError(f'Copied file failed verification: {destination}')
            destination.chmod(0o755 if row['destination'].endswith('.sh') or row['destination'] == 'opentyrian2000' else 0o644)
            inventory.append({k: v for k, v in row.items() if k != 'source'})
        (output / 'RUNTIME-INVENTORY.json').write_text(json.dumps({'schema': 'opentyrian-runtime-inventory-v1', 'source_revision': manifest['source_revision'], 'files': inventory}, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        report['runtime_ready'] = False
        report['runtime_ready_reason'] = 'Original game data and platform dependencies are external; runtime launch acceptance is separate.'
        report['missing'] = []
        (output / 'RUNTIME-STATUS.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        # Completion marker is renamed, preserving even its small original contents.
        marker.rename(output / 'COPY-VERIFIED.txt')
        if args.zip:
            zip_directory(output, archive)
            report['archive_bytes'] = archive.stat().st_size
            digest = hashlib.sha256()
            with archive.open('rb') as stream:
                for chunk in iter(lambda: stream.read(MIB), b''):
                    digest.update(chunk)
            report['archive_sha256'] = digest.hexdigest()
        report['output_payload_bytes'] = sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
    if args.report:
        target = args.report.absolute()
        parent_for_new(target)
        assert_external(target, roots)
        target.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if catalog_output is not None:
        # Exclusive creation: never replace a snapshot or a source file.
        with catalog_output.open('xb') as stream:
            stream.write(catalog_payload)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not missing else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Packaging refused: {error}', file=sys.stderr)
        raise SystemExit(1)
