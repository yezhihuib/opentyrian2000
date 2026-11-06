#!/usr/bin/env python3
"""Build the optional level-2 HD layer without modifying the production tree."""
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

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'experimental/level2-family/src'
DEFINES = (
    'B313_FAMILY_CACHE_DIAGNOSTIC', 'B313_FAMILY_CANVAS_DIAGNOSTIC',
    'B313_FAMILY_OBSERVER_DIAGNOSTIC', 'B313_V6_ANIMATION_DIAGNOSTIC',
    'B313_V6_BINDING_DIAGNOSTIC', 'B313_V6_LOCK_DIAGNOSTIC',
    'B313_V6_PREPARATION_DIAGNOSTIC', 'B313_V6_RECOVERY_DIAGNOSTIC',
    'B313_V6_SEQUENCE_DIAGNOSTIC', 'B313_V6_TRANSACTION_DIAGNOSTIC',
    'BUILDING313_FINAL_PROOF_DIAGNOSTIC', 'BUILDING313_IDENTITY_DIAGNOSTIC',
    'BUILDING313_LINEAGE_DIAGNOSTIC', 'BUILDING313_PRECOMMIT_DIAGNOSTIC',
    'BUILDING313_SNAPSHOT_TRANSACTION_DIAGNOSTIC',
    'NATIVE_WRITER_OBSERVER_DIAGNOSTIC', 'NATIVE_WRITER_SCOPE_DIAGNOSTIC',
    'OLD_HD_SAMPLE_OBSERVER_DIAGNOSTIC',
)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=2, choices=range(1, 17))
    parser.add_argument('--check-only', action='store_true',
                        help='inspect inputs and compiler flags without writing or compiling')
    args = parser.parse_args(argv)
    if os.name != 'posix':
        parser.error('This optional builder is currently validated for POSIX toolchains only.')
    sources = {}
    for base in (ROOT / 'src', OVERLAY):
        for path in sorted(base.rglob('*')):
            if path.is_file() and path.suffix in ('.c', '.h', '.inc'):
                sources[path.relative_to(base).as_posix()] = path.read_bytes()
    units = sorted(name for name in sources if name.endswith('.c') and '/' not in name)
    if len(units) != 112 or not OVERLAY.is_dir():
        raise RuntimeError('Expected the reviewed 112-unit production-plus-overlay source tree.')
    asset_names = ('reconstructed_run_specs.h', 'reconstructed_numeric_specs.h',
                   'reconstructed_name_source_specs.h')
    assets = {'hd/shared-menu-runs-v1/' + name:
              (ROOT / 'assets/hd/shared-menu-runs-v1' / name).read_bytes()
              for name in asset_names}
    asset_pins = {name: sha(raw) for name, raw in sorted(assets.items())}
    source_pins = {name: sha(raw) for name, raw in sorted(sources.items())}
    source_digest = sha(json.dumps(source_pins, sort_keys=True).encode())
    stage = ROOT / '.level2-family-build' / source_digest[:16]
    cc = shlex.split(os.environ.get('CC', 'cc'))
    pc = shlex.split(os.environ.get('PKG_CONFIG', 'pkg-config'))
    def pkg(option):
        return shlex.split(subprocess.check_output(
            pc + [option, 'sdl2', 'SDL2_net', 'libcrypto'], text=True).strip())
    cpp = ['-DTARGET_UNIX', '-DWITH_NETWORK', '-DNDEBUG', '-DNEWSHF_HD_COMPOSITOR=0',
           '-DOPENTYRIAN_VERSION="level2-family-v1"',
           '-DTYRIAN_DIR="/usr/local/share/games/opentyrian2000"']
    cpp += ['-D' + name + '=1' for name in DEFINES]
    cpp += pkg('--cflags') + shlex.split(os.environ.get('CPPFLAGS', ''))
    cpp += ['-I' + str(stage / 'src'), '-I' + str(stage / 'assets')]
    cflags = ['-std=c99', '-O2', '-Wall', '-Wextra'] + shlex.split(os.environ.get('CFLAGS', ''))
    ldflags = shlex.split(os.environ.get('LDFLAGS', ''))
    libs = pkg('--libs') + ['-lm']
    plan = {'source_digest': source_digest, 'source_sha256': source_pins,
            'asset_header_sha256': asset_pins,
            'build_input_digest': sha(json.dumps({'source': source_pins, 'assets': asset_pins}, sort_keys=True).encode()),
            'translation_units': len(units), 'compiler': cc,
            'cppflags': cpp, 'cflags': cflags, 'ldflags': ldflags, 'libs': libs,
            'stage': str(stage), 'binary': str(ROOT / 'opentyrian2000-family'),
            'production_tree_modified': False, 'game_started': False}
    if args.check_only:
        print(json.dumps(plan, indent=2))
        return 0
    for name, raw in sources.items():
        target = stage / 'src' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    for name, raw in assets.items():
        target = stage / 'assets' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    objects = stage / 'obj'
    objects.mkdir(exist_ok=True)
    def compile_one(name):
        out = objects / (Path(name).stem + '.o')
        command = cc + cpp + cflags + ['-MMD', '-MF', str(out.with_suffix('.d')),
                    '-c', str(stage / 'src' / name), '-o', str(out)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        out.with_suffix('.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('Compilation failed for ' + name + ':\n' + result.stderr[-6000:])
        return str(out)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        linked = list(pool.map(compile_one, units))
    candidate = stage / 'opentyrian2000-family'
    subprocess.run(cc + ldflags + ['-o', str(candidate)] + linked + libs,
                   cwd=ROOT, check=True)
    plan['binary_sha256'] = sha(candidate.read_bytes())
    plan['object_sha256'] = {Path(p).name: sha(Path(p).read_bytes()) for p in linked}
    (stage / 'BUILD.json').write_text(json.dumps(plan, indent=2) + '\n')
    destination = ROOT / 'opentyrian2000-family'
    temporary = ROOT / 'opentyrian2000-family.tmp'
    shutil.copyfile(candidate, temporary)
    temporary.chmod(0o755)
    temporary.replace(destination)
    print(json.dumps({'status': 'BUILD_OK', 'translation_units': len(units),
                      'binary': str(destination), 'sha256': plan['binary_sha256'],
                      'game_started': False}, indent=2))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
