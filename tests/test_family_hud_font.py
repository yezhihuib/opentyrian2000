#!/usr/bin/env python3
"""Original-input persistent glyph adapter oracle; no native scene claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from shared_hud_reconstruction import extract, original_payload

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--sanitize', action='store_true')
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    overlay = ROOT / 'experimental/level2-family/src'
    mirror = (overlay / 'render_mirror.c').read_text()
    canvas = (overlay / 'b313_family_canvas_mirror.inc').read_text()
    helpers = '\n'.join(extract(mirror, name) for name in
                        ('hud_sprite_decode', 'hud_runtime_compatible', 'shared_hud_palette_matches'))
    helpers += '\n'.join(extract(canvas, name) for name in ('family_indexed', 'family_rgb'))
    suffixes = ('', '_components', '_meters', '_indicators', '_fixed_text', '_font')
    paths = [ROOT / 'src' / ('gameplay_hud' + suffix + ext)
             for suffix in suffixes for ext in ('.c', '.h')]
    paths += [overlay / name for name in ('family_hud_font_mirror.inc', 'family_static_hud_mirror.inc',
                                         'family_dynamic_hud_mirror.inc', 'render_mirror.c', 'b313_family_canvas_mirror.inc')]
    paths += [ROOT / 'tests' / name for name in ('family_hud_font_test.c', 'family_static_hud_test.c', 'shared_hud_reconstruction.py')]
    pins = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    pkg = shlex.split(os.environ.get('PKG_CONFIG', 'pkg-config'))
    flags = shlex.split(subprocess.check_output(pkg + ['--cflags', 'sdl2'], text=True))
    libs = shlex.split(subprocess.check_output(pkg + ['--libs', 'sdl2'], text=True))
    results = []
    with tempfile.TemporaryDirectory(prefix='family-hud-font-') as directory:
        temp = Path(directory)
        (temp / 'family_static_hud_helpers.inc').write_text(helpers)
        exe = temp / 'test'
        command = shlex.split(os.environ.get('CC', 'cc')) + [
            '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
            '-I' + str(temp), '-I' + str(overlay), '-I' + str(ROOT / 'src')] + flags
        if args.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
        command += [str(ROOT / 'tests/family_hud_font_test.c')]
        command += [str(ROOT / 'src' / ('gameplay_hud' + suffix + '.c')) for suffix in suffixes]
        command += ['-o', str(exe)] + libs
        subprocess.run(command, check=True)
        payload = original_payload(args.data.resolve())
        for case in ('valid', 'missing', 'corrupt'):
            work = temp / case
            resources = work / 'assets/hd/shared-ui-v1'
            resources.mkdir(parents=True)
            (resources / 'gameplay-hud-v1.hda').symlink_to(ROOT / 'assets/hd/shared-ui-v1/gameplay-hud-v1.hda')
            path = resources / 'gameplay-hud-font-v1.hda'
            if case == 'valid':
                path.symlink_to(ROOT / 'assets/hd/shared-ui-v1/gameplay-hud-font-v1.hda')
            elif case == 'corrupt':
                path.write_bytes(b'invalid')
            result = subprocess.run([str(exe), case], cwd=work, input=payload, capture_output=True,
                                    env={**os.environ, 'SDL_VIDEODRIVER': 'dummy',
                                         'ASAN_OPTIONS': 'detect_leaks=0:halt_on_error=1',
                                         'UBSAN_OPTIONS': 'halt_on_error=1'})
            print(result.stdout.decode(), end='')
            print(result.stderr.decode(), end='')
            results.append({'case': case, 'returncode': result.returncode,
                            'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()})
            if result.returncode:
                break
    receipt = {'status': 'PASS' if len(results) == 3 and all(r['returncode'] == 0 for r in results) else 'FAIL',
               'original_bytes_persisted': False, 'source_sha256': pins, 'results': results,
               'source_unchanged': all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in pins.items())}
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
