#!/usr/bin/env python3
"""Bounded preview companion for the unchanged 562e8fc Windows family build.

Check-only by default. Copy immutable inputs to a new CWD, never existing saves.
This is scripted asset-debug playback, not normal or full-level gameplay.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import stat
import struct
import subprocess
import sys
import threading
import time

sys.dont_write_bytecode = True
SOURCE_COMMIT = '562e8fc4ad0f7916734bc40624b867a152d89b0c'
SOURCE_DIGEST = '8c85faa18d5427e4f3af2015cbdbbae2e82b3631d27ef0774236c22be106ca54'
TOOL_PINS = {
    'HD-ASSET-PINS.json': '341aa0d68dcfa5b1aa66defa0ab52517099f54976b6c3825d505d0f49af23dbe',
    'launch_level2_family.py': '7fd9ae2502ac8029d0e157360f38fd3a0d77a8357b4a827418eacf23f71f15d4',
    'windows_classic_runtime.py': 'a6dccec3aa5a16561467f2aacfd4178fb00e921926846eece8a0a3272fbcbb6e',
    'windows_hd_runtime.py': 'df28c612f8c18889d162fa7ac101e6b68e29ba68caa0859f8948958de84b1b22',
}
FAMILY_MANIFEST = 'assets/hd/level2-family-v1/MANIFEST.json'
FAMILY_SHA = '63f27ca5e875d1fd2847c9305db9e66afe2591cacbcd310c4161874abaf14aa9'
BASE_FILES = {'bin/opentyrian2000-level2.exe', 'bin/SDL2.dll', 'bin/SDL2_net.dll',
              'trust/BUILD-WINDOWS.json', 'trust/STAGE.json'}
PREVIEW_ARGS = ('--asset-debug=custom', '--asset-debug-episode=1', '--asset-debug-level=2',
                '--asset-debug-event=18', '--asset-debug-running', '--render-ticks=600',
                '--render-no-capture')
ENABLES = ('BUILDING313_FAMILY_OBSERVER_ENABLE', 'BUILDING313_FAMILY_CANVAS_ENABLE',
           'BUILDING313_FAMILY_GROUND_ENABLE', 'BUILDING313_FAMILY_CLIFF_ENABLE',
           'BUILDING313_FAMILY_CORNER_ENABLE', 'BUILDING313_TERRAIN_CONTINUITY_ENABLE',
           'BUILDING313_FAMILY_STATIC340_ENABLE', 'LAMP272_FAMILY_CANVAS_ENABLE',
           'GRAY325_FAMILY_CANVAS_ENABLE', 'LONGFACE573_FAMILY_CANVAS_ENABLE',
           'TRIPLE275_FAMILY_CANVAS_ENABLE', 'BUILDING313_TERRAIN_BLEND_RETIRE_ENABLE',
           'LAMP272_LATER_THREE_ENABLE', 'LAMP272_MIDDLE_PAIR_ENABLE', 'EMBER269_FAMILY_CANVAS_ENABLE')
CONFIG = b"section 'video'\n    item 'fullscreen' '-1'\n    item 'scaler' '4x'\n    item 'scaling_mode' 'Integer'\n"
SCHEMA = 'opentyrian-frozen-level2-preview-v1'
MAX_SECONDS = 90
MAX_OUTPUT = 64 * 1024 * 1024
WINDOWS = os.name == 'nt'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(value, new=False):
    p = Path(value).expanduser()
    if not p.is_absolute() or '..' in p.parts:
        raise ValueError('Use an absolute path without parent traversal')
    for node in reversed((p,) + tuple(p.parents)):
        try:
            s = node.lstat()
        except FileNotFoundError:
            if node == p and new:
                continue
            raise ValueError('Missing path or parent: ' + str(node))
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 1024:
            raise ValueError('Symlink/reparse path rejected: ' + str(node))
    return p


def trusted(path, digest, size=None):
    p = safe_path(path)
    if not p.is_file():
        raise ValueError('Expected regular file: ' + str(p))
    raw = p.read_bytes()
    if sha(raw) != digest or (size is not None and len(raw) != size):
        raise ValueError('Changed pinned input: ' + str(p))
    return raw


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def pe(raw, dll):
    if len(raw) < 64 or raw[:2] != b'MZ':
        raise ValueError('Not a PE input')
    offset = struct.unpack_from('<I', raw, 60)[0]
    if offset + 24 > len(raw) or raw[offset:offset+4] != b'PE\0\0' or struct.unpack_from('<H', raw, offset+4)[0] != 0x8664:
        raise ValueError('Require AMD64 PE input')
    if bool(struct.unpack_from('<H', raw, offset+22)[0] & 0x2000) != dll:
        raise ValueError('Wrong EXE/DLL role')


def inspect_inputs(root, receipt):
    """Read only immutable package files and original startup data, never saves."""
    if receipt.get('source_digest') != SOURCE_DIGEST:
        raise ValueError('Not the frozen 562e8fc source digest')
    for name, pin in TOOL_PINS.items():
        trusted(root / 'tools' / name, pin)
    inventory = read_json(root / 'tools/HD-ASSET-PINS.json')
    pins = {}
    for item in inventory['files']:
        name = item['path']
        p = PurePosixPath(name)
        if not name.startswith('assets/hd/') or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or name.casefold() in {n.casefold() for n in pins}:
            raise ValueError('Unsafe asset path')
        pins[name] = {'bytes': item['bytes'], 'sha256': item['sha256']}
    if len(pins) != 101 or sum(i['bytes'] for i in pins.values()) != 18410168:
        raise ValueError('Require the exact frozen 101 asset inventory')
    expected = BASE_FILES | {'tools/' + n for n in TOOL_PINS} | set(pins) | {FAMILY_MANIFEST}
    files = receipt.get('files', {})
    if set(files) != expected:
        raise ValueError('Wrong immutable file inventory')
    for name, entry in files.items():
        raw = trusted(root / name, entry['sha256'], entry['bytes'])
        if name.startswith('bin/'):
            pe(raw, name.endswith('.dll'))
    if any(files[name] != pin for name, pin in pins.items()) or files[FAMILY_MANIFEST]['sha256'] != FAMILY_SHA:
        raise ValueError('Resource receipt differs from frozen public pins')
    build_raw = (root / 'trust/BUILD-WINDOWS.json').read_bytes()
    stage_raw = (root / 'trust/STAGE.json').read_bytes()
    build, stage = json.loads(build_raw), json.loads(stage_raw)
    if (build.get('status') != 'BUILT_NOT_RUN' or build.get('exit_code') != 0 or
            build.get('pe_machine') != 'AMD64' or build.get('inputs_unchanged_after_build') is not True or
            stage.get('status') != 'STAGED_NOT_BUILT' or stage.get('translation_units') != 112 or
            build.get('source_digest') != SOURCE_DIGEST or stage.get('source_digest') != SOURCE_DIGEST or
            build.get('stage_sha256') != sha(stage_raw) or receipt.get('stage_sha256') != sha(stage_raw) or
            receipt.get('build_sha256') != sha(build_raw) or
            build.get('binary', {}).get('sha256') != files['bin/opentyrian2000-level2.exe']['sha256']):
        raise ValueError('Broken frozen build chain')
    for key, name in (('SDL2', 'SDL2.dll'), ('SDL2_net', 'SDL2_net.dll')):
        pin = build.get('dependencies', {}).get(key, {}).get('runtime_dll_inventory')
        if pin and pin.get('sha256') != files['bin/' + name]['sha256']:
            raise ValueError('Runtime DLL differs from build')
    data = safe_path(receipt['data_directory'])
    if not data.is_dir():
        raise ValueError('Original data directory missing')
    for name, item in receipt['data_files'].items():
        if PurePosixPath(name).name != name or '\\' in name or ':' in name:
            raise ValueError('Unsafe original data name')
        trusted(data / name, item['sha256'], item['bytes'])
    required = {'tyrian1.lvl', 'tyrian.hdt', 'tyrian.cdt', 'tyrian.snd', 'voices.snd', 'music.mus', 'palette.dat'}
    if not required.issubset(receipt['data_files']):
        raise ValueError('Missing original startup data inventory')
    return data


def environment(root):
    values = dict.fromkeys(ENABLES, '1')
    base = root / 'assets/hd/level2-family-v1'
    values.update({f'BUILDING313_V6_PHASE{n}': str(base / 'building' / f'phase{n}.argb32le') for n in range(3)})
    for name in ('LAMP272', 'GRAY325', 'TRIPLE275', 'EMBER269'):
        values[name + '_FAMILY_ASSET_DIR'] = str(root / 'assets/hd/packs/asteroid1-ten-v1')
    values['LONGFACE573_FAMILY_ASSET_DIR'] = str(base / 'longface')
    return values


def prepare(args):
    source = safe_path(args.runtime)
    raw = trusted(source / 'RUNTIME.json', args.trust_sha256)
    receipt = json.loads(raw)
    if receipt.get('schema') != 'opentyrian-windows-classic-runtime-v1' or receipt.get('mode') != 'hd' or receipt.get('public_candidates') is not True:
        raise ValueError('Require the verified frozen public-candidate runtime')
    data = inspect_inputs(source, receipt)
    root = safe_path(args.output, new=True)
    if root.exists():
        raise ValueError('Output must be new; existing profiles are never reused')
    for protected in (source, data):
        if root == protected or protected in root.parents or root in protected.parents:
            raise ValueError('Output must be separate from inputs and original data')
    result = {'status': 'CHECK_ONLY', 'source_commit': SOURCE_COMMIT, 'output': str(root),
              'asset_files': 101, 'active_controls': 23, 'game_started': False,
              'normal_gameplay': False, 'argv': [str(root / 'bin/opentyrian2000-level2.exe'), '--data=' + str(data), *PREVIEW_ARGS]}
    if not args.prepare:
        return result
    root.mkdir(mode=0o700)
    # Copy only the exact immutable inventory. Never scan/import the old profile.
    for name, item in receipt['files'].items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if WINDOWS:
            import ctypes
            api = ctypes.WinDLL('kernel32', use_last_error=True).CopyFileW
            api.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int)
            api.restype = ctypes.c_int
            if not api(str(source / name), str(target), 1):
                raise ctypes.WinError(ctypes.get_last_error())
        else:
            shutil.copy2(source / name, target)
        trusted(target, item['sha256'], item['bytes'])
    with (root / 'opentyrian.cfg').open('xb') as f:
        f.write(CONFIG)
    self_raw = Path(__file__).read_bytes()
    with (root / 'preview_level2_frozen.py').open('xb') as f:
        f.write(self_raw)
    new_receipt = {'schema': SCHEMA, 'source_runtime_sha256': sha(raw), 'runtime': receipt,
                   'arguments': list(PREVIEW_ARGS), 'environment': environment(root),
                   'launcher_sha256': sha(self_raw), 'config_sha256': sha(CONFIG),
                   'max_seconds': MAX_SECONDS, 'max_output_bytes': MAX_OUTPUT,
                   'source_commit': SOURCE_COMMIT, 'normal_gameplay': False}
    out = (json.dumps(new_receipt, indent=2, sort_keys=True) + '\n').encode()
    with (root / 'PREVIEW.json').open('xb') as f:
        f.write(out)
    result.update(status='PREPARED_NOT_RUN', preview_sha256=sha(out))
    return result


def verify(args):
    root = safe_path(args.root)
    receipt = json.loads(trusted(root / 'PREVIEW.json', args.trust_sha256))
    if (receipt.get('schema') != SCHEMA or receipt.get('arguments') != list(PREVIEW_ARGS) or
            receipt.get('environment') != environment(root) or receipt.get('max_seconds') != MAX_SECONDS or
            receipt.get('max_output_bytes') != MAX_OUTPUT or receipt.get('source_commit') != SOURCE_COMMIT):
        raise ValueError('Changed bounded preview contract')
    trusted(root / 'preview_level2_frozen.py', receipt['launcher_sha256'])
    if sha(Path(__file__).read_bytes()) != receipt['launcher_sha256']:
        raise ValueError('Active preview launcher changed')
    trusted(root / 'opentyrian.cfg', sha(CONFIG))
    data = inspect_inputs(root, receipt['runtime'])
    expected = set(receipt['runtime']['files']) | {'PREVIEW.json', 'opentyrian.cfg', 'preview_level2_frozen.py'}
    for path in root.rglob('*'):
        safe_path(path)
        if path.is_file() and path.relative_to(root).as_posix() not in expected:
            raise ValueError('Unexpected/preexisting run output; prepare a fresh preview')
    return root, data


def child_environment(root, inherited):
    source = {k.upper(): v for k, v in inherited.items()}
    allowed = ('SYSTEMROOT', 'WINDIR', 'SYSTEMDRIVE', 'COMSPEC', 'TEMP', 'TMP')
    values = {k: source[k] for k in allowed if k in source}
    system = safe_path(values['SYSTEMROOT'])
    values['PATH'] = os.pathsep.join((str(root / 'bin'), str(system / 'System32'), str(system)))
    values.update(environment(root))
    return values


def supervise(argv, root, env, *, seconds=MAX_SECONDS, output_limit=MAX_OUTPUT):
    """Drain child output without unbounded buffering and impose a total disk budget."""
    baseline = {path.relative_to(root).as_posix(): path.stat().st_size
                for path in root.rglob('*') if path.is_file()}
    started = time.monotonic()
    child = subprocess.Popen(argv, cwd=root, env=env, stdin=subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
    overflow = threading.Event()
    failure = []
    count = [0]
    def drain():
        try:
            with (root / 'preview-output.log').open('xb') as log:
                while True:
                    block = child.stdout.read(8192)
                    if not block:
                        break
                    remaining = max(0, output_limit - count[0])
                    log.write(block[:remaining])
                    count[0] += len(block)
                    if count[0] > output_limit:
                        overflow.set()
        except Exception as exc:
            failure.append(str(exc))
            overflow.set()
    reader = threading.Thread(target=drain, daemon=True)
    reader.start()
    reason = None
    try:
        while child.poll() is None:
            if time.monotonic() - started >= seconds:
                reason = 'wall-time-budget'
            elif overflow.is_set():
                reason = 'output-budget-or-write-error'
            else:
                # Native diagnostics write directly into CWD too, not just stdout.
                total = 0
                for path in root.rglob('*'):
                    if path.is_file():
                        name = path.relative_to(root).as_posix()
                        total += max(0, path.stat().st_size - baseline.get(name, 0))
                if total > output_limit:
                    reason = 'diagnostic-output-budget'
            if reason:
                child.kill()
                break
            time.sleep(0.025)
        code = child.wait(timeout=5)
    except BaseException:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)
        raise
    finally:
        reader.join(timeout=5)
        child.stdout.close()
    final_bytes = sum(max(0, path.stat().st_size - baseline.get(path.relative_to(root).as_posix(), 0))
                      for path in root.rglob('*') if path.is_file())
    if final_bytes > output_limit and reason is None:
        reason = 'diagnostic-output-budget'
    if overflow.is_set() and reason is None:
        reason = 'output-budget-or-write-error'
    if reader.is_alive():
        failure.append('Output reader did not finish')
        reason = reason or 'output-reader-incomplete'
    return {'status': 'STOPPED' if reason else 'EXITED', 'exit_code': code,
            'stop_reason': reason, 'output_bytes': count[0], 'generated_file_bytes': final_bytes, 'output_errors': failure,
            'elapsed_seconds': time.monotonic() - started, 'game_started': True,
            'normal_gameplay': False, 'runtime_acceptance': False}


def assess_preview(root):
    # Native diagnostics establish bounded admission, not visual acceptance.
    target, completed = False, False
    with (root / 'preview-output.log').open(encoding='utf-8', errors='replace') as log:
        for line in log:
            if re.search(r'Asset debug target reached at tick\d+ eventLoc19\b', line):
                target = True
            if 'Controlled scene completed 600 logic ticks' in line:
                completed = True
    canvas = root / 'building313-family-canvas.json'
    accepted = read_json(canvas).get('accepted_frames', 0) if canvas.is_file() else 0
    if type(accepted) is not int or not 0 <= accepted <= 600:
        raise ValueError('Invalid family admission result')
    return {'preview_target_reached': target, 'hd_accepted_frames': accepted,
            'completed_600_ticks': completed}


def run(args):
    root, data = verify(args)
    argv = [str(root / 'bin/opentyrian2000-level2.exe'), '--data=' + str(data), *PREVIEW_ARGS]
    if not args.launch:
        return {'status': 'CHECK_ONLY', 'argv': argv, 'cwd': str(root), 'game_started': False,
                'environment': environment(root), 'normal_gameplay': False}
    if not args.observer_present:
        raise ValueError('A person must be present for the preview')
    if not WINDOWS:
        raise ValueError('Windows launch only; offline checks are not a native test')
    env = child_environment(root, os.environ)
    with (root / 'preview-start.json').open('x', encoding='utf-8') as f:
        json.dump({'preview_sha256': args.trust_sha256, 'argv': argv, 'cwd': str(root)}, f, indent=2)
    try:
        result = supervise(argv, root, env)
        receipt = read_json(root / 'PREVIEW.json')
        inspect_inputs(root, receipt['runtime'])
        result['immutable_inputs_and_original_data_unchanged'] = True
        result.update(assess_preview(root))
        if result['status'] == 'EXITED' and (not result['preview_target_reached'] or not result['hd_accepted_frames']):
            result['status'] = 'FAILED_ADMISSION'
        elif result['status'] == 'EXITED' and not result['completed_600_ticks']:
            result['status'] = 'ENDED_EARLY'
    except (Exception, KeyboardInterrupt) as exc:
        result = {'status': 'FAILED', 'error': str(exc), 'runtime_acceptance': False}
    with (root / 'preview-end.json').open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    q = sub.add_parser('prepare')
    q.add_argument('--runtime', required=True)
    q.add_argument('--trust-sha256', required=True)
    q.add_argument('--output', required=True)
    q.add_argument('--prepare', action='store_true')
    q = sub.add_parser('run')
    q.add_argument('--root', required=True)
    q.add_argument('--trust-sha256', required=True)
    q.add_argument('--launch', action='store_true')
    q.add_argument('--observer-present', action='store_true')
    a = p.parse_args()
    try:
        result = prepare(a) if a.command == 'prepare' else run(a)
        print(json.dumps(result, indent=2))
        return 0 if result['status'] in ('CHECK_ONLY', 'PREPARED_NOT_RUN', 'EXITED') and not result.get('exit_code') else 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('level2-preview: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
