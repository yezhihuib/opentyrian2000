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


def contained_file(root: Path, value: str) -> Path:
    path = root / relative_path(value)
    # Reject symlinks in *any* component, including a directory symlink.
    cursor = root
    for component in PurePosixPath(value).parts:
        cursor = cursor / component
        if cursor.is_symlink():
            raise ValueError(f'Symlink source is not accepted: {cursor}')
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
    parser.add_argument('--report', type=Path, help='Optional new JSON report outside source roots')
    args = parser.parse_args(argv)
    roots = [args.source_root.resolve()] + [p.resolve() for p in args.asset_root]
    manifest = load_manifest(args.manifest or roots[0] / 'packaging/runtime-assets-v1.json')
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
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not missing else 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Packaging refused: {error}', file=sys.stderr)
        raise SystemExit(1)
