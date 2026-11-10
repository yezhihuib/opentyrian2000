#!/usr/bin/env python3
"""Cross-build the level-2 Windows x64 engine in a NEW directory outside the repo.

Dependencies must already exist locally. This script never downloads, installs,
launches the game, copies original data, or modifies an existing output directory.
MinGW is a separate build route; it does not imply MSVC or Windows/GPU validation.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SYSTEM_DLLS = frozenset(name.casefold() for name in (
    'ADVAPI32.dll', 'bcrypt.dll', 'COMCTL32.dll', 'COMDLG32.dll', 'CRYPT32.dll',
    'GDI32.dll', 'IMM32.dll', 'IPHLPAPI.dll', 'KERNEL32.dll', 'msvcrt.dll', 'ole32.dll',
    'OLEAUT32.dll', 'RPCRT4.dll', 'SETUPAPI.dll', 'SHELL32.dll', 'SHLWAPI.dll',
    'USER32.dll', 'VERSION.dll', 'WINMM.dll', 'WS2_32.dll', 'dinput8.dll',
))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_entry(path):
    path = Path(path)
    return {'path': str(path), 'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}


def validate_pe_x64(path):
    raw = Path(path).read_bytes()
    if len(raw) < 64 or raw[:2] != b'MZ':
        raise ValueError('Not a PE image: ' + str(path))
    offset = struct.unpack_from('<I', raw, 60)[0]
    if offset + 26 > len(raw) or raw[offset:offset + 4] != b'PE\0\0':
        raise ValueError('Invalid PE header: ' + str(path))
    if struct.unpack_from('<H', raw, offset + 4)[0] != 0x8664:
        raise ValueError('Not PE AMD64: ' + str(path))
    if struct.unpack_from('<H', raw, offset + 24)[0] != 0x20b:
        raise ValueError('Not PE32+: ' + str(path))
    return 'AMD64'


def source_inputs(repo):
    repo = Path(repo).resolve()
    files, origins = {}, {}
    for base in (repo / 'src', repo / 'experimental/level2-family/src'):
        for path in sorted(base.rglob('*')):
            if path.is_file() and path.suffix in ('.c', '.h', '.inc'):
                name = path.relative_to(base).as_posix()
                files['src/' + name] = path.read_bytes()
                origins['src/' + name] = path.relative_to(repo).as_posix()
    units = sorted(name for name in files if name.endswith('.c') and name.count('/') == 1)
    if len(units) != 112 or 'src/b313_platform.h' not in files:
        raise ValueError('Require the reviewed 112-unit production-plus-overlay tree')
    for name in ('reconstructed_run_specs.h', 'reconstructed_numeric_specs.h',
                 'reconstructed_name_source_specs.h'):
        path = 'assets/hd/shared-menu-runs-v1/' + name
        files[path] = (repo / path).read_bytes()
        origins[path] = path
    for name in ('resources.rc', 'tyrian2000.ico'):
        path = 'visualc/' + name
        files[path] = (repo / path).read_bytes()
        origins[path] = path
    for name in ('build_level2_family.py', 'build_level2_mingw.py'):
        path = 'scripts/' + name
        files[path] = (repo / path).read_bytes()
        origins[path] = path
    tree = ast.parse(files['scripts/build_level2_family.py'].decode())
    defines = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'DEFINES' for t in node.targets):
            defines = ast.literal_eval(node.value)
    if not defines or not all(re.fullmatch(r'[A-Z0-9_]+', name) for name in defines):
        raise ValueError('Missing reviewed diagnostic definitions')
    return files, origins, units, defines


def fresh_destination(repo, destination):
    repo, destination = Path(repo).resolve(), Path(destination).resolve()
    if destination.exists() or destination == repo or repo in destination.parents:
        raise ValueError('Use a new build directory outside the checkout')
    return destination


def build(args):
    repo = Path(args.repo).resolve()
    destination = fresh_destination(repo, args.output)
    files, origins, units, defines = source_inputs(repo)
    tools = {}
    for name in ('cc', 'windres', 'objdump'):
        value = getattr(args, name)
        resolved = shutil.which(value)
        if not resolved:
            raise ValueError('Missing local tool: ' + value)
        tools[name] = str(Path(resolved).resolve())
    target = subprocess.check_output([tools['cc'], '-dumpmachine'], text=True).strip()
    if target != 'x86_64-w64-mingw32':
        raise ValueError('Require x86_64-w64-mingw32 compiler, got ' + target)
    dependency = Path(args.sdl_prefix).resolve()
    required = ['include/SDL2/SDL.h', 'include/SDL2/SDL_net.h', 'lib/libSDL2.dll.a',
                'lib/libSDL2main.a', 'lib/libSDL2_net.dll.a', 'bin/SDL2.dll', 'bin/SDL2_net.dll']
    dependencies = {name: file_entry(dependency / name) for name in required}
    for name in ('SDL2.dll', 'SDL2_net.dll'):
        validate_pe_x64(dependency / 'bin' / name)
    pins = {name: sha(raw) for name, raw in sorted(files.items())}
    source_pins = {name[4:]: value for name, value in pins.items() if name.startswith('src/')}
    cpp = ['-DTARGET_WIN32', '-DWITH_NETWORK', '-DNDEBUG', '-DNEWSHF_HD_COMPOSITOR=0',
           '-DOPENTYRIAN_VERSION="level2-cloud-mingw-candidate"', '-DTYRIAN_DIR="C:\\\\TYRIAN"']
    cpp += ['-D' + name + '=1' for name in defines]
    cpp += ['-I' + str(dependency / 'include/SDL2'), '-I' + str(destination / 'src'),
            '-I' + str(destination / 'assets')]
    cflags = ['-std=c99', '-O2', '-Wall', '-Wextra', '-Wno-unknown-pragmas',
              '-finput-charset=UTF-8', '-ffile-prefix-map=' + str(destination) + '=stage']
    ldflags = ['-mwindows', '-static-libgcc', '-Wl,--no-insert-timestamp']
    libs = ['-L' + str(dependency / 'lib'), '-lmingw32', '-lSDL2main', '-lSDL2',
            '-lSDL2_net', '-lbcrypt', '-lm']
    try:
        revision = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
        repository_status = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain'], text=True)
    except subprocess.CalledProcessError:
        revision = None
        repository_status = None
    receipt = {'schema': 'level2-mingw-cloud-build-v1', 'status': 'CHECK_ONLY',
               'repository_revision': revision, 'repository_dirty': bool(repository_status) if repository_status is not None else None,
               'repository_status': repository_status, 'source_origins': origins,
               'input_sha256': pins, 'source_digest': sha(json.dumps(source_pins, sort_keys=True).encode()),
               'build_input_digest': sha(json.dumps(pins, sort_keys=True).encode()),
               'translation_units': len(units), 'target': target, 'tools': {k: file_entry(v) for k, v in tools.items()},
               'compiler_version': subprocess.check_output([tools['cc'], '-v'], stderr=subprocess.STDOUT, text=True),
               'dependencies': dependencies, 'cppflags': cpp, 'cflags': cflags, 'ldflags': ldflags,
               'libs': libs, 'build_started': False, 'game_started': False,
               'native_windows_acceptance': False, 'physical_gpu_acceptance': False}
    if args.check_only:
        return receipt
    destination.mkdir(parents=True, exist_ok=False)
    for name, raw in files.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    objects, binary_dir = destination / 'obj', destination / 'bin'
    objects.mkdir(); binary_dir.mkdir()
    receipt['status'] = 'BUILDING'; receipt['build_started'] = True
    receipt_file = destination / 'BUILD-MINGW.json'
    receipt_file.write_text(json.dumps(receipt, indent=2) + '\n')
    commands = []
    def run(command, logfile):
        commands.append(command)
        result = subprocess.run(command, cwd=destination, capture_output=True, text=True)
        logfile.write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('Command failed, see ' + str(logfile) + ':\n' + result.stderr[-4000:])
    try:
        def compile_one(name):
            output = objects / (Path(name).stem + '.o')
            run([tools['cc']] + cpp + cflags + ['-c', str(destination / name), '-o', str(output)], output.with_suffix('.log'))
            return output
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            linked = list(pool.map(compile_one, units))
        resource = objects / 'resources.o'
        run([tools['windres'], '--target=pe-x86-64', '--preprocessor=' + tools['cc'],
             '--preprocessor-arg=-E', '--preprocessor-arg=-xc', '--preprocessor-arg=-DRC_INVOKED',
             '-I', str(destination / 'visualc'), str(destination / 'visualc/resources.rc'), str(resource)], objects / 'resources.log')
        exe = binary_dir / 'opentyrian2000-level2.exe'
        run([tools['cc']] + ldflags + ['-o', str(exe)] + [str(p) for p in linked] + [str(resource)] + libs,
            destination / 'link.log')
        for name in ('SDL2.dll', 'SDL2_net.dll'):
            shutil.copyfile(dependency / 'bin' / name, binary_dir / name)
        imports = {}
        supplied = {p.name.casefold() for p in binary_dir.iterdir()}
        for path in sorted(binary_dir.iterdir()):
            validate_pe_x64(path)
            output = subprocess.check_output([tools['objdump'], '-p', str(path)], text=True)
            (destination / (path.name + '.pe.txt')).write_text(output)
            imported = re.findall(r'DLL Name:\s*(\S+)', output)
            unresolved = [name for name in imported if name.casefold() not in SYSTEM_DLLS | supplied]
            if unresolved:
                raise ValueError('Unbundled non-system DLL imports in ' + path.name + ': ' + ', '.join(unresolved))
            imports[path.name] = imported
        if any(sha((destination / name).read_bytes()) != expected for name, expected in pins.items()):
            raise ValueError('Staged source changed during build')
        if any(sha((repo / origins[name]).read_bytes()) != expected for name, expected in pins.items()):
            raise ValueError('Repository source changed during build; rebuild after source freeze')
        if any(sha((dependency / name).read_bytes()) != expected['sha256'] for name, expected in dependencies.items()):
            raise ValueError('Dependency changed during build')
        receipt.update(status='BUILT_NOT_RUN', binary=file_entry(exe), pe_machine='AMD64',
                       runtime_files={p.name: file_entry(p) for p in sorted(binary_dir.iterdir())},
                       pe_imports=imports, inputs_unchanged_after_build=True,
                       object_sha256={p.name: sha(p.read_bytes()) for p in linked + [resource]})
    except Exception as error:
        receipt.update(status='BUILD_FAILED', error=str(error))
        raise
    finally:
        receipt['commands'] = commands
        receipt_file.write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sdl-prefix', type=Path, required=True)
    parser.add_argument('--cc', default='x86_64-w64-mingw32-gcc')
    parser.add_argument('--windres', default='x86_64-w64-mingw32-windres')
    parser.add_argument('--objdump', default='x86_64-w64-mingw32-objdump')
    parser.add_argument('--jobs', type=int, choices=range(1, 17), default=4)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args(argv)
    try:
        receipt = build(args)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(receipt if args.check_only else {k: receipt[k] for k in
                     ('status', 'source_digest', 'build_input_digest', 'translation_units', 'binary', 'game_started')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
