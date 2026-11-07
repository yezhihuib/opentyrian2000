#!/usr/bin/env python3
"""Fully rebuild the isolated, default-off experimental source candidate. Never run it."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BUDGET = 500_000_000
FREE_FLOOR = 500_000_000


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_sources():
    manifest = json.loads((ROOT / 'SOURCE.json').read_text())
    units = manifest['translation_units']
    if len(units) != 112 or 'entry-shim' in units:
        raise RuntimeError('Expected 112 production units and no entry shim.')
    for name, expected in manifest['source_sha256'].items():
        path = ROOT / name
        if not path.is_relative_to(ROOT) or digest(path) != expected:
            raise RuntimeError('Source integrity check failed: ' + name)
    for unit in units.values():
        if any(value.startswith('main=') for value in unit['defines']):
            raise RuntimeError('Main renaming is not permitted.')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=2, choices=range(1, 17))
    parser.add_argument('--check-only', action='store_true',
                        help='verify source pins and resolve dependency flags without compiling')
    parser.add_argument('--build-dir', type=Path,
                        help='new, empty output directory; default: this package/build')
    args = parser.parse_args(argv)
    if os.name != 'posix':
        parser.error('Only POSIX toolchains have been build-validated.')
    manifest = inspect_sources()
    cc = shlex.split(os.environ.get('CC', 'cc'))
    pc = shlex.split(os.environ.get('PKG_CONFIG', 'pkg-config'))
    def pkg(option):
        return shlex.split(subprocess.check_output(
            pc + [option, 'sdl2', 'SDL2_net', 'libcrypto'], text=True).strip())
    dependency_cflags = pkg('--cflags')
    libs = pkg('--libs') + ['-lm']
    cppflags = shlex.split(os.environ.get('CPPFLAGS', ''))
    cflags = ['-std=c99', '-O2', '-Wall', '-Wextra'] + shlex.split(os.environ.get('CFLAGS', ''))
    ldflags = shlex.split(os.environ.get('LDFLAGS', ''))
    build = (args.build_dir or ROOT / 'build').resolve()
    report = {'translation_units': 112, 'cached_objects_reused': 0,
              'entry_shims': 0, 'game_runs': 0, 'runtime_art_included': False,
              'activation_launcher_included': False,
              'source_manifest_sha256': digest(ROOT / 'SOURCE.json'),
              'compiler': cc, 'dependency_cflags': dependency_cflags,
              'cppflags': cppflags, 'cflags': cflags, 'ldflags': ldflags, 'libs': libs,
              'binary': str(build / 'opentyrian2000-late-level')}
    if args.check_only:
        report['status'] = 'SOURCE_AND_DEPENDENCY_PLAN_OK'
        print(json.dumps(report, indent=2))
        return 0
    if build.exists():
        raise RuntimeError('Build output exists. Choose a new --build-dir; no cached objects are reused.')
    if ROOT == build or ROOT.is_relative_to(build) or build.is_relative_to(ROOT / 'sources'):
        raise RuntimeError('Build directory must not overlap source inputs.')
    owned = sum(path.stat().st_size for path in ROOT.rglob('*') if path.is_file())
    if owned + 100_000_000 >= BUDGET or shutil.disk_usage(ROOT).free <= FREE_FLOOR + 100_000_000:
        raise RuntimeError('Insufficient budget or free disk space for a full build.')
    build.mkdir(parents=True)
    objects = build / 'objects'
    objects.mkdir()
    def compile_one(item):
        name, unit = item
        obj = objects / (name + '.o')
        dep = obj.with_suffix('.d')
        # Relative source paths avoid embedding checkout paths through __FILE__.
        command = cc + cflags + dependency_cflags + cppflags
        command += ['-D' + define for define in unit['defines']]
        command += ['-DOPENTYRIAN_VERSION="experimental-late-level"',
                    '-DTYRIAN_DIR="data"']
        command += ['-I' + value for value in unit['include_dirs']]
        command += ['-MMD', '-MF', str(dep), '-c', unit['source'], '-o', str(obj)]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        obj.with_suffix('.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('Compilation failed for ' + name + ':\n' + result.stderr[-8000:])
        observed = shlex.split(dep.read_text().replace('\\\n', ' ').split(':', 1)[1])
        local = set()
        for value in observed:
            path = Path(value)
            if not path.is_absolute():
                path = ROOT / path
            path = path.resolve()
            if path.is_relative_to(ROOT):
                local.add(path.relative_to(ROOT).as_posix())
            # System/development headers come from pkg-config, not this release.
        if local != set(unit['local_dependencies']):
            raise RuntimeError('Per-unit header selection changed for ' + name + ': ' +
                               repr({'missing': sorted(set(unit['local_dependencies']) - local),
                                     'extra': sorted(local - set(unit['local_dependencies']))}))
        return name, {'object': str(obj), 'sha256': digest(obj),
                      'local_dependencies_verified': len(local),
                      'warnings': result.stderr.count('warning:')}
    report['status'] = 'BUILD_IN_PROGRESS'
    (build / 'BUILD.json').write_text(json.dumps(report, indent=2) + '\n')
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            compiled = dict(pool.map(compile_one, sorted(manifest['translation_units'].items())))
        binary = build / 'opentyrian2000-late-level'
        command = cc + ldflags + ['-o', str(binary)]
        command += [value['object'] for value in compiled.values()] + libs
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (build / 'link.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('Link failed:\n' + result.stderr[-8000:])
        report.update(status='FULL_SOURCE_BUILD_OK', objects=compiled,
                      binary_sha256=digest(binary),
                      warnings=sum(value['warnings'] for value in compiled.values()),
                      build_bytes=sum(path.stat().st_size for path in build.rglob('*') if path.is_file()))
        if report['build_bytes'] + owned >= BUDGET or shutil.disk_usage(build).free <= FREE_FLOOR:
            raise RuntimeError('Completed build exceeds the package budget or free-space floor.')
    except BaseException as error:
        report.update(status='STOPPED_ATTEMPT_PRESERVED', error=str(error))
        raise
    finally:
        (build / 'BUILD.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in (
        'status', 'translation_units', 'cached_objects_reused', 'entry_shims',
        'game_runs', 'warnings', 'binary', 'binary_sha256')}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
