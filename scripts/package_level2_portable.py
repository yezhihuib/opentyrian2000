#!/usr/bin/env python3
"""Verify, then explicitly assemble the frozen Windows x64 level-2 preview.

Default/check-only is read-only: no compile, output, downloads, launch or cleanup.
Only --assemble creates a fresh directory and deterministic, inspected ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MIB = 1024 * 1024
GAME = 'bin/opentyrian-level2.exe'
LAUNCHER = 'Start-Level2-Preview.exe'
ASSET_PINS = 'scripts/HD-ASSET-PINS.json'
ORIGINAL_PINS = 'packaging/level2-original-data-hashes.json'
CONTROL_PINS = 'packaging/level2-preview-controls.json'
MANIFEST_PINS = {
    ASSET_PINS: '7fe6be044d8e5d681fbeeb1de9edee52ed2bb4a3d02e1f16400a5e878311e166',
    'assets/hd/level2-family-v1/MANIFEST.json': '63f27ca5e875d1fd2847c9305db9e66afe2591cacbcd310c4161874abaf14aa9',
    ORIGINAL_PINS: '862b08349dc076e55318cf1187273ac73c6d2f1c4d08922168d27bb58286ed99',
    CONTROL_PINS: '3ca24e3e510ba92d93fb38d40681b73ddf8ce6cff23d6043046402b61e0d80f3',
}
HUD = {'path': 'assets/hd/shared-ui-v1/gameplay-hud-v1.hda', 'bytes': 4160064,
       'sha256': '98cd6cfefa02a9ae79b75a65e02dd2566d3dec1492552f20b042b3c61c19cd17'}
DATA_EXTENSIONS = {'.shp', '.lvl', '.dat', '.cdt', '.hdt', '.snd', '.mus', '.pic', '.anm'}
SYSTEM_DLLS = {name.casefold() for name in (
    'ADVAPI32.dll', 'bcrypt.dll', 'COMCTL32.dll', 'COMDLG32.dll', 'CRYPT32.dll',
    'GDI32.dll', 'IMM32.dll', 'IPHLPAPI.dll', 'KERNEL32.dll', 'msvcrt.dll', 'ole32.dll',
    'OLEAUT32.dll', 'RPCRT4.dll', 'SETUPAPI.dll', 'SHELL32.dll', 'SHLWAPI.dll',
    'USER32.dll', 'VERSION.dll', 'WINMM.dll', 'WS2_32.dll', 'dinput8.dll')}
LICENSES = ('SDL2-LICENSE.txt', 'SDL2_net-LICENSE.txt', 'MinGW-w64-copyright.txt',
            'GCC-runtime-copyright.txt')
LICENSE_PINS = dict(zip(LICENSES, (
    '97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127',
    'fcb07e07ac6bc8b2fcf047b50431ef4ebe5b619d7ca7c82212018309a9067426',
    '50e5bb66d222c7d4692c2d13670ddcd3664779358e389a026b69a0e0e18e7be5',
    'f891d7e0c56f503a92c7258d540b3d8215852d8387cbca8f1f07c6f4b6e67da6')))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + '\n').encode()


def relative_path(value, flat=False):
    if not isinstance(value, str) or not value or not value.isascii():
        raise ValueError('Paths must be nonempty relative ASCII names')
    parts = value.split('/')
    if flat and len(parts) != 1:
        raise ValueError('Original data names must be flat')
    for part in parts:
        stem = part.split('.')[0].upper()
        if (part in ('', '.', '..') or part.endswith((' ', '.')) or
                any(ord(c) < 32 or c in '\\<>:"|?*' for c in part) or
                stem in {'CON', 'PRN', 'AUX', 'NUL'} or re.fullmatch(r'(COM|LPT)[1-9]', stem)):
            raise ValueError('Unsafe relative path: ' + value)
    return value


def plain_path(path):
    """Reject aliases in every existing component, including dangling links."""
    path = Path(path).absolute()
    if '..' in path.parts:
        raise ValueError('Traversal in local path: ' + str(path))
    cursor = Path(path.anchor)
    for part in path.parts[1:]:
        cursor /= part
        try:
            info = cursor.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 1024:
            raise ValueError('Symlink/reparse point rejected: ' + str(cursor))
    return path


def read_file(path, limit=64 * MIB):
    path = plain_path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
        raise ValueError('Not a bounded regular file: ' + str(path))
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) != info.st_size or len(raw) > limit:
        raise ValueError('File changed while reading: ' + str(path))
    return raw


def checked_file(path, row):
    if (not isinstance(row, dict) or type(row.get('bytes')) is not int or
            not 0 <= row['bytes'] <= 64 * MIB or
            not re.fullmatch(r'[0-9a-f]{64}', str(row.get('sha256', '')))):
        raise ValueError('Invalid size/hash identity')
    raw = read_file(path)
    if len(raw) != row['bytes'] or sha(raw) != row['sha256']:
        raise ValueError('Size/SHA256 mismatch: ' + str(path))
    return raw


def load_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + x)))


def validate_names(names):
    seen = set()
    for name in names:
        key = relative_path(name).casefold()
        if key in seen or any(key.startswith(old + '/') or old.startswith(key + '/') for old in seen):
            raise ValueError('Duplicate or file/directory collision: ' + name)
        seen.add(key)


def pe_image(raw, dll):
    """Read AMD64 PE32+ headers and normal imports without executing an image/tool."""
    def u16(offset):
        return struct.unpack_from('<H', raw, offset)[0]
    def u32(offset):
        return struct.unpack_from('<I', raw, offset)[0]
    try:
        if len(raw) < 64 or raw[:2] != b'MZ':
            raise ValueError('Missing DOS header')
        pe = u32(60)
        if raw[pe:pe+4] != b'PE\0\0' or u16(pe + 4) != 0x8664:
            raise ValueError('Require PE AMD64')
        characteristics = u16(pe + 22)
        if not characteristics & 2 or bool(characteristics & 0x2000) != dll:
            raise ValueError('Wrong executable/DLL role')
        opt, opt_size, sections = pe + 24, u16(pe + 20), u16(pe + 6)
        if opt_size < 240 or u16(opt) != 0x20b or not 1 <= sections <= 96:
            raise ValueError('Invalid PE32+ optional header')
        table = opt + opt_size
        if table + sections * 40 > len(raw):
            raise ValueError('Truncated PE sections')
        for index in range(sections):
            sec = table + index * 40
            if u32(sec + 16) and u32(sec + 20) + u32(sec + 16) > len(raw):
                raise ValueError('Truncated PE section data')
        def offset(rva, length=1):
            for index in range(sections):
                sec = table + index * 40
                start, size, position = u32(sec + 12), u32(sec + 16), u32(sec + 20)
                if start <= rva and rva + length <= start + size and position + rva - start + length <= len(raw):
                    return position + rva - start
            raise ValueError('Unmapped PE RVA')
        if u32(opt + 108) < 14:
            raise ValueError('Missing PE data directories')
        # Delay-loaded imports require separate dependency validation, not guesses.
        if u32(opt + 112 + 13 * 8):
            raise ValueError('Delay imports unsupported')
        imports = []
        rva, size = u32(opt + 120), u32(opt + 124)
        if not rva or size < 20:
            raise ValueError('Missing normal PE imports')
        for index in range(min(size // 20, 4096)):
            pos = offset(rva + index * 20, 20)
            if raw[pos:pos+20] == bytes(20):
                return sorted(imports, key=str.casefold)
            name_pos = offset(u32(pos + 12))
            end = raw.find(b'\0', name_pos, name_pos + 256)
            if end < 0:
                raise ValueError('Unterminated DLL import')
            name = raw[name_pos:end].decode('ascii')
            relative_path(name, flat=True)
            if not name.casefold().endswith('.dll'):
                raise ValueError('Invalid DLL import')
            imports.append(name)
        raise ValueError('Unterminated PE import table')
    except (struct.error, UnicodeError) as error:
        raise ValueError('Malformed PE image') from error


def fresh_output(output, zip_path, roots):
    paths = [plain_path(output), plain_path(zip_path)]
    for path in paths:
        if path.exists() or not path.parent.is_dir():
            raise ValueError('Use a new output with an existing parent: ' + str(path))
        for root in roots:
            if path == root or path in root.parents or root in path.parents:
                raise ValueError('Output overlaps an input: ' + str(path))
    if paths[0] == paths[1] or paths[0] in paths[1].parents or paths[1] in paths[0].parents:
        raise ValueError('Output directory and ZIP overlap')
    return paths


def git(repo, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(repo), *args])


def source_module(repo, filename):
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location('_portable_' + Path(filename).stem, repo / filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous


def verify_controls(repo, binary):
    launch = source_module(repo, 'scripts/launch_level2_family.py')
    args = launch.parser().parse_args(['--data', str(repo), '--binary', str(binary),
        '--profile', str(repo.parent / 'unused-preview-profile'), '--hd', '--public-candidates',
        '--terrain-fallback', '--player-fallback', '--tank-fallback', '--static-hud'])
    _, environment = launch.build_plan(args, inherited={}, root=repo)
    actual = {key: value.replace(str(repo) + '/', '') for key, value in environment.items()
              if launch.controlled_name(key)}
    reviewed = load_json(read_file(repo / CONTROL_PINS))
    if actual != reviewed or len(actual) != 53:
        raise ValueError('Current launcher disagrees with the 53 reviewed controls')
    for key, value in actual.items():
        if not re.fullmatch('[A-Z0-9_]+', key) or any(bad in key for bad in ('CLIP', 'REDVENT', 'INVULNERABLE', 'PROBE', 'DEBUG')):
            raise ValueError('Unapproved control: ' + key)
        if value != '1':
            relative_path(value)
    return actual


def identity(path, raw):
    return {'path': path, 'bytes': len(raw), 'sha256': sha(raw)}


def make_header(payload, originals, controls, bundle_id, revision):
    lines = ['/* Generated from verified, pinned inputs. Do not edit. */',
             '#define PREVIEW_GAME_EXE L' + json.dumps(GAME),
             '#define PREVIEW_BUNDLE_ID L' + json.dumps(bundle_id),
             '#define PREVIEW_SOURCE_COMMIT L' + json.dumps(revision)]
    for name, entries in (('payload', payload), ('original', originals)):
        lines.append('static const PreviewFile preview_' + name + '[] = {')
        for row in sorted(entries, key=lambda row: row['path']):
            relative_path(row['path'], flat=name == 'original')
            lines.append('    {L%s, %s, %dULL},' % (json.dumps(row['path']), json.dumps(row['sha256']), row['bytes']))
        lines += ['};', '#define PREVIEW_%s_COUNT (sizeof(preview_%s) / sizeof(preview_%s[0]))' % (name.upper(), name, name)]
    lines.append('static const PreviewEnv preview_env[] = {')
    lines.extend('    {L%s, L%s},' % (json.dumps(key), json.dumps(value)) for key, value in sorted(controls.items()))
    lines += ['};', '#define PREVIEW_ENV_COUNT (sizeof(preview_env) / sizeof(preview_env[0]))', '']
    return '\n'.join(lines).encode('ascii')


def make_plan(args):
    repo, build, dependency = map(plain_path, (args.repo, args.build_dir, args.dependencies))
    output, archive = fresh_output(args.output, args.zip, [repo, build, dependency])
    revision = args.source_revision
    if not re.fullmatch('[0-9a-f]{40}', revision) or git(repo, 'rev-parse', 'HEAD').decode().strip() != revision:
        raise ValueError('Require the exact frozen full source revision at HEAD')
    if git(repo, 'status', '--porcelain', '--untracked-files=no').strip():
        raise ValueError('Tracked source must be clean before packaging')
    for name in ('scripts/build_level2_mingw.py', 'scripts/launch_level2_family.py'):
        if read_file(repo / name) != git(repo, 'show', revision + ':' + name):
            raise ValueError('Module is not frozen in source revision: ' + name)
    receipt_raw = read_file(build / 'BUILD-MINGW.json', 8 * MIB)
    if not re.fullmatch('[0-9a-f]{64}', args.build_sha256) or sha(receipt_raw) != args.build_sha256:
        raise ValueError('BUILD-MINGW receipt differs from caller-pinned SHA256')
    receipt = load_json(receipt_raw)
    if (receipt.get('schema') != 'level2-mingw-cloud-build-v1' or receipt.get('status') != 'BUILT_NOT_RUN' or
            receipt.get('target') != 'x86_64-w64-mingw32' or receipt.get('repository_revision') != revision or
            receipt.get('repository_dirty') is not False or receipt.get('inputs_unchanged_after_build') is not True):
        raise ValueError('Build is not bound to the frozen clean source revision')
    # Reject directory aliases before the legacy source enumerator reads them.
    for subtree in ('src', 'experimental/level2-family/src', 'assets/hd/shared-menu-runs-v1', 'visualc'):
        base = plain_path(repo / subtree)
        for path in base.rglob('*'):
            plain_path(path)
    builder = source_module(repo, 'scripts/build_level2_mingw.py')
    source, origins, units, _ = builder.source_inputs(repo)
    pins = {name: sha(raw) for name, raw in sorted(source.items())}
    source_pins = {name[4:]: digest for name, digest in pins.items() if name.startswith('src/')}
    if (pins != receipt['input_sha256'] or origins != receipt['source_origins'] or len(units) != 112 or
            sha(json.dumps(pins, sort_keys=True).encode()) != receipt['build_input_digest'] or
            sha(json.dumps(source_pins, sort_keys=True).encode()) != receipt['source_digest']):
        raise ValueError('Frozen build inputs/source digest mismatch')
    files = {}
    # Include every effective input at its original repository path. Add replaced
    # base source files too, making the overlay build reproducible from source/.
    tracked = git(repo, 'ls-files', '-z', 'src', 'experimental/level2-family/src').decode().split('\0')
    source_names = set(origins.values()) | {name for name in tracked if name and Path(name).suffix in ('.c', '.h', '.inc')}
    source_names |= {'COPYING', 'Makefile', 'scripts/package_level2_portable.py', 'scripts/launch_level2_family.py',
                     'tools/level2_preview_launcher.c', 'tools/level2_preview_launcher_policy.h',
                     'packaging/level2-portable-README.txt', 'docs/LEVEL2_PORTABLE.md', 'docs/WINDOWS_CLOUD_BUILD.md',
                     'assets/hd/shared-menu-runs-v1/FONT-LICENSE.txt',
                     'assets/hd/shared-menu-runs-v1/OSIFONT-LICENSE.txt'} | set(MANIFEST_PINS)
    for name in sorted(source_names):
        relative_path(name)
        raw = read_file(repo / name)
        if git(repo, 'show', revision + ':' + name) != raw:
            raise ValueError('Source not frozen at revision: ' + name)
        files['source/' + name] = raw
    for name, digest in MANIFEST_PINS.items():
        if sha(read_file(repo / name)) != digest:
            raise ValueError('Reviewed manifest changed: ' + name)
    asset_manifest = load_json(read_file(repo / ASSET_PINS))
    asset_rows = asset_manifest['files']
    if len(asset_rows) != 103 or asset_manifest.get('original_data_included') is not False:
        raise ValueError('Expected exactly 103 approved public assets')
    for row in asset_rows + [HUD]:
        name = relative_path(row['path'])
        if not name.startswith('assets/hd/') or Path(name).suffix not in ('.hda', '.argb32le'):
            raise ValueError('Unexpected public asset type')
        files[name] = checked_file(repo / name, row)
    runtime = receipt['runtime_files']
    if set(runtime) != {'opentyrian2000-level2.exe', 'SDL2.dll', 'SDL2_net.dll'}:
        raise ValueError('Unexpected runtime file set')
    imports = {}
    for name, row in sorted(runtime.items()):
        expected_path = build / 'bin' / name
        if plain_path(row['path']) != expected_path:
            raise ValueError('Build runtime path does not match its role')
        raw = checked_file(expected_path, row)
        imports[name] = pe_image(raw, dll=name.endswith('.dll'))
        if sorted(imports[name], key=str.casefold) != sorted(receipt['pe_imports'][name], key=str.casefold):
            raise ValueError('PE imports disagree with build receipt')
        if any(dll.casefold() not in SYSTEM_DLLS | {'sdl2.dll', 'sdl2_net.dll'} for dll in imports[name]):
            raise ValueError('Missing non-system runtime dependency')
        files[GAME if name.endswith('.exe') else 'bin/' + name] = raw
    if receipt['binary'] != runtime['opentyrian2000-level2.exe']:
        raise ValueError('Build binary identity inconsistent')
    controls = verify_controls(repo, build / 'bin/opentyrian2000-level2.exe')
    original_manifest = load_json(read_file(repo / ORIGINAL_PINS))
    originals = original_manifest['files']
    validate_names(row['path'] for row in originals)
    for row in originals:
        relative_path(row['path'], flat=True)
        if Path(row['path']).suffix not in DATA_EXTENSIONS or not re.fullmatch('[0-9a-f]{64}', row['sha256']) or type(row['bytes']) is not int or not 0 < row['bytes'] <= 64 * MIB:
            raise ValueError('Unsafe original data whitelist')
    if len(originals) != 74 or original_manifest['original_bytes_included'] is not False:
        raise ValueError('Original data whitelist changed')
    cc = plain_path(receipt['tools']['cc']['path'])
    checked_file(cc, receipt['tools']['cc'])
    dep_raw = read_file(dependency / 'DEPENDENCIES.json', 8 * MIB)
    if sha(dep_raw) != args.dependencies_sha256:
        raise ValueError('Dependency provenance differs from caller-pinned SHA256')
    dep = load_json(dep_raw)
    if dep['schema'] != 'level2-cloud-windows-dependencies-v1' or dep['target'] != receipt['target']:
        raise ValueError('Wrong dependency provenance')
    for name in ('SDL2.dll', 'SDL2_net.dll'):
        if dep['dlls'][name] != {key: runtime[name][key] for key in ('sha256', 'bytes')}:
            raise ValueError('Runtime DLL disagrees with dependency provenance')
    for name in LICENSES:
        raw = read_file(dependency / 'runtime-licenses' / name, 2 * MIB)
        if sha(raw) != LICENSE_PINS[name]:
            raise ValueError('Dependency license notice changed: ' + name)
        files['licenses/' + name] = raw
    files['licenses/OpenTyrian-COPYING.txt'] = read_file(repo / 'COPYING')
    for name in ('FONT-LICENSE.txt', 'OSIFONT-LICENSE.txt'):
        files['licenses/' + name] = read_file(repo / 'assets/hd/shared-menu-runs-v1' / name)
    files['metadata/DEPENDENCIES.json'] = dep_raw
    files['metadata/ORIGINAL-DATA-HASHES.json'] = read_file(repo / ORIGINAL_PINS)
    files['metadata/HD-ASSET-PINS.json'] = read_file(repo / ASSET_PINS)
    files['metadata/LEVEL2-FAMILY-ASSETS.json'] = read_file(repo / 'assets/hd/level2-family-v1/MANIFEST.json')
    files['metadata/CONTROLS.json'] = json_bytes(controls)
    payload = [identity(name, files[name]) for name in sorted(files) if name.startswith(('assets/', 'bin/'))]
    bundle_id = 'level2-' + revision[:12] + '-' + sha(json_bytes(payload))[:12]
    files['source/generated_manifest.h'] = make_header(payload, originals, controls, bundle_id, revision)
    # Explicit projection keeps local absolute paths/private build logs out.
    public_build = {key: receipt[key] for key in ('schema', 'status', 'repository_revision', 'repository_dirty',
        'source_origins', 'input_sha256', 'source_digest', 'build_input_digest', 'target', 'translation_units',
        'inputs_unchanged_after_build', 'pe_imports', 'object_sha256')}
    public_build.update(receipt_sha256=args.build_sha256,
                        runtime_files={name: {k: row[k] for k in ('sha256', 'bytes')} for name, row in runtime.items()},
                        compiler={k: receipt['tools']['cc'][k] for k in ('sha256', 'bytes')})
    files['metadata/BUILD-MINGW.json'] = json_bytes(public_build)
    files['README.txt'] = read_file(repo / 'packaging/level2-portable-README.txt').replace(b'@BUNDLE_ID@', bundle_id.encode()).replace(b'@SOURCE_COMMIT@', revision.encode())
    files['Start-2x.cmd'] = b'@echo off\r\nsetlocal DisableDelayedExpansion\r\n"%~dp0Start-Level2-Preview.exe" --scale=2\r\n'
    validate_names(files)
    if sum(map(len, files.values())) > 256 * MIB:
        raise ValueError('Package exceeds the 256 MiB safety bound')
    return {'repo': repo, 'build': build, 'dependency': dependency, 'output': output, 'zip': archive,
            'files': files, 'payload': payload, 'originals': originals, 'controls': controls,
            'bundle_id': bundle_id, 'revision': revision, 'cc': cc, 'receipt': receipt}


def write_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as output:
        output.write(raw)


def inspect_tree(root, expected):
    actual = set()
    for path in root.rglob('*'):
        plain_path(path)
        if path.is_dir():
            continue
        name = path.relative_to(root).as_posix()
        actual.add(name)
        if name not in expected or read_file(path) != expected[name]:
            raise ValueError('Unexpected or altered package file: ' + name)
    if actual != set(expected):
        raise ValueError('Incomplete package tree')


def write_zip(target, files):
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in sorted(files.items()):
            relative_path(name)
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, raw, compresslevel=9)
    with zipfile.ZipFile(target) as archive:
        if archive.namelist() != sorted(files) or archive.testzip():
            raise ValueError('ZIP inventory/CRC check failed')
        for name, raw in files.items():
            if archive.read(name) != raw:
                raise ValueError('ZIP content check failed: ' + name)


def assemble(plan):
    output, archive, files = plan['output'], plan['zip'], dict(plan['files'])
    fresh_output(output, archive, [plan['repo'], plan['build'], plan['dependency']])
    checked_file(plan['cc'], plan['receipt']['tools']['cc'])
    output.mkdir()
    for name, raw in sorted(files.items()):
        write_new(output / name, raw)
    command = [str(plan['cc']), '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-municode',
        '-mwindows', '-static-libgcc', '-Wl,--no-insert-timestamp', '-finput-charset=UTF-8',
        '-ffile-prefix-map=' + str(output) + '=bundle', '-DPREVIEW_MANIFEST_HEADER="' + str(output / 'source/generated_manifest.h') + '"',
        str(output / 'source/tools/level2_preview_launcher.c'), '-o', str(output / LAUNCHER),
        '-lbcrypt', '-lshell32', '-lole32']
    result = subprocess.run(command, cwd=output, capture_output=True, text=True,
                            env={**os.environ, 'SOURCE_DATE_EPOCH': '315532800'})
    if result.returncode:
        raise ValueError('Launcher compile failed; partial output retained for inspection:\n' + result.stderr[-6000:])
    raw = read_file(output / LAUNCHER)
    imports = pe_image(raw, dll=False)
    if any(name.casefold() not in SYSTEM_DLLS for name in imports):
        raise ValueError('Launcher requires an unbundled non-system DLL')
    files[LAUNCHER] = raw
    launcher_build = {'schema': 'level2-native-launcher-build-v1', 'compiler': {key: plan['receipt']['tools']['cc'][key] for key in ('sha256', 'bytes')},
        'command': [part.replace(str(output), '<bundle>').replace(str(plan['cc']), '<x86_64-w64-mingw32-gcc>') for part in command],
        'launcher': identity(LAUNCHER, raw), 'pe_imports': imports, 'SOURCE_DATE_EPOCH': 315532800,
        'inputs': [identity(name, files[name]) for name in ('source/tools/level2_preview_launcher.c',
            'source/tools/level2_preview_launcher_policy.h', 'source/generated_manifest.h')],
        'native_windows_acceptance': False, 'physical_gpu_acceptance': False, 'game_started': False}
    files['metadata/LAUNCHER-BUILD.json'] = json_bytes(launcher_build)
    inventory = {'schema': 'level2-portable-package-v1', 'bundle_id': plan['bundle_id'], 'source_revision': plan['revision'],
        'files': [identity(name, raw) for name, raw in sorted(files.items())],
        'payload_count': len(plan['payload']), 'public_assets': 104, 'original_data_included': False,
        'profiles_or_logs_included': False, 'private_extensions_included': False,
        'native_windows_acceptance': False, 'physical_gpu_acceptance': False, 'game_started': False}
    files['metadata/PACKAGE.json'] = json_bytes(inventory)
    for name in ('metadata/LAUNCHER-BUILD.json', 'metadata/PACKAGE.json'):
        write_new(output / name, files[name])
    inspect_tree(output, files)
    write_zip(archive, files)
    return {'status': 'ASSEMBLED_NOT_RUN', 'bundle_id': plan['bundle_id'], 'files': len(files),
            'zip': identity(archive.name, read_file(archive, 256 * MIB)), 'game_started': False,
            'native_windows_acceptance': False, 'physical_gpu_acceptance': False}


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--repo', type=Path, default=ROOT)
    result.add_argument('--build-dir', required=True, type=Path)
    result.add_argument('--build-sha256', required=True)
    result.add_argument('--source-revision', required=True)
    result.add_argument('--dependencies', required=True, type=Path, help='Directory containing DEPENDENCIES.json and runtime-licenses/')
    result.add_argument('--dependencies-sha256', required=True)
    result.add_argument('--output', required=True, type=Path)
    result.add_argument('--zip', required=True, type=Path)
    mode = result.add_mutually_exclusive_group()
    mode.add_argument('--assemble', action='store_true')
    mode.add_argument('--check-only', action='store_true')
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        plan = make_plan(args)
        summary = assemble(plan) if args.assemble else {'status': 'CHECK_ONLY', 'bundle_id': plan['bundle_id'],
            'payload_files': len(plan['payload']), 'public_assets': 104, 'original_hashes': len(plan['originals']),
            'controls': len(plan['controls']), 'output_created': False, 'compiler_started': False, 'game_started': False}
        print(json.dumps(summary, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('level2-portable: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
