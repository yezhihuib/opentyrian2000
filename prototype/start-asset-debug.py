"""Portable launcher for the existing C asset debugger; no engine protocol changes."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

from launcher_paths import dependency

REPO = Path(__file__).resolve().parent.parent


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe', help='Game executable; default: repo/opentyrian-x64-Release.exe')
    p.add_argument('--assets', help='Existing HD pack; omitted: build current debug view')
    p.add_argument('--data', help='Original data directory; default: ../runtime-data/tyrian2000')
    p.add_argument('--episode', type=int, default=1)
    p.add_argument('--level', type=int, default=9)
    p.add_argument('--tick', type=int, required=True)
    p.add_argument('--until', type=int, default=6000)
    p.add_argument('--capture-start', type=int, default=-1)
    p.add_argument('--capture-count', type=int, default=36)
    p.add_argument('--max-replays', type=int, default=20, help='Maximum fresh restarts after exit 75 (default: 20)')
    p.add_argument('--talon-bank', choices=['5', '13'], default='13')
    for flag in ['headless', 'running', 'capture', 'window-only', 'explosion-log']:
        p.add_argument('--' + flag, action='store_true')
    return p


def validate(p, a):
    if not 0 <= a.max_replays <= 1000:
        p.error('--max-replays must be 0..1000')
    if not 1 <= a.episode <= 5 or not 1 <= a.level <= 255:
        p.error('Episode must be 1..5 and level 1..255')
    if not 0 <= a.tick < a.until or not 60 <= a.until <= 6000:
        p.error('Require 0 <= tick < until and until 60..6000')
    if not -1 <= a.capture_start <= 5999 or not 1 <= a.capture_count <= 120:
        p.error('Capture bounds require start -1..5999 and count 1..120')
    if (a.capture_start >= 0 or a.capture_count != 36 or a.window_only) and not a.capture:
        p.error('Capture bounds/window-only require --capture')


def command(a, exe, data, assets, control):
    args = [str(exe), '--data=' + str(data), '--no-sound', '--no-joystick', '--no-xmas',
            '--asset-debug=custom', f'--asset-debug-episode={a.episode}',
            f'--asset-debug-level={a.level}', f'--asset-debug-tick={a.tick}',
            f'--render-ticks={a.until}', '--render-assets=' + str(assets),
            '--asset-debug-control=' + str(control), '--render-talon-bank=' + a.talon_bank]
    for flag in ['running', 'capture', 'window-only', 'explosion-log']:
        if getattr(a, flag.replace('-', '_')):
            args.append('--asset-debug-' + flag)
    if a.capture:
        args.append(f'--asset-debug-capture-count={a.capture_count}')
    if a.capture_start >= 0:
        args.append(f'--asset-debug-capture-start={a.capture_start}')
    return args


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    p = parser()
    a = p.parse_args(argv)
    validate(p, a)
    exe = dependency(p, a.exe, REPO / 'opentyrian-x64-Release.exe', 'exe')
    data = dependency(p, a.data, REPO.parent / 'runtime-data/tyrian2000', 'data')
    if a.assets is None:
        sys.path.insert(0, str(REPO / 'scripts'))
        from build_current_craft267 import view
        a.assets = view(REPO, 'debug', REPO.parent / 'current-craft267-packs' / ('debug-' + uuid.uuid4().hex))['path']
    assets = dependency(p, a.assets, None, 'assets')
    env = dict(os.environ)
    if a.headless:
        env.update(SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software')
    runs = REPO.parent / 'controlled-runs'
    runs.mkdir(parents=True, exist_ok=True)
    for replay in range(a.max_replays + 1):
        out = Path(tempfile.mkdtemp(prefix='asset-debug-', dir=runs))
        (out / 'opentyrian.cfg').write_text("section 'video'\n    item 'fullscreen' '-1'\n    item 'scaler' '4x'\n    item 'scaling_mode' 'Integer'\n", encoding='utf-8')
        env = dict(env, HOME=str(out / 'home'), XDG_CONFIG_HOME=str(out / 'config'))
        Path(env['HOME']).mkdir()
        config_dir = Path(env['XDG_CONFIG_HOME']) / 'opentyrian2000'
        config_dir.mkdir(parents=True)
        (config_dir / 'opentyrian.cfg').write_bytes((out / 'opentyrian.cfg').read_bytes())
        control = out / 'debug-control.txt'
        control.write_text('', encoding='utf-8')
        cmd = command(a, exe, data, assets, control)
        metadata = {'argv': cmd, 'exe_sha256': sha(exe), 'source_sha256': {
            name: sha(REPO / name) for name in ['src/asset_debug.c', 'src/tyrian2.c', 'src/game_probe.c', 'src/render_mirror.c']},
            'launcher': 'start-asset-debug.py', 'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        def save():
            (out / 'asset-debug-run.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
        save()
        print(f'ASSET DEBUG run: {out}\nSpace/P pause; N step; R fresh replay; Esc quit. Control queue: {control}', flush=True)
        with (out / 'launcher-game-stdout.log').open('w', encoding='utf-8') as stdout, (out / 'launcher-game-stderr.log').open('w', encoding='utf-8') as stderr:
            result = subprocess.run(cmd, cwd=out, env=env, stdout=stdout, stderr=stderr)
        metadata.update(exit_code=result.returncode, end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        save()
        for name in ['launcher-game-stdout.log', 'launcher-game-stderr.log']:
            print((out / name).read_text(encoding='utf-8', errors='replace'), end='')
        if result.returncode == 75 and replay == a.max_replays:
            print(f'Replay limit exhausted ({a.max_replays}); inspect {out}', file=sys.stderr)
        if result.returncode != 75 or replay == a.max_replays:
            return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
