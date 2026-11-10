#!/usr/bin/env python3
"""Measure bounded asset-debug level2 continuity with unchanged engine objects.

Build the family binary first. Keeps all original data, output frames and profiles
outside this checkout. The wrapper only reads family status at actual Present;
no gameplay or rendering hooks are changed. Software output is not Windows/GPU
acceptance. Compare --baseline against a prior output directory when requested.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_PINS = {
    'tyrian.shp': '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0',
    'newshd.shp': '08c7c81b4ed590609f97347b1a4ec60aba56925ecc7193a6718c34cb8d698adf',
}
NATIVE_STREAMS = ('state.tsv', 'collisions.tsv', 'player-projectiles.tsv',
                  'player-shot-emissions.tsv', 'player-shot-results.tsv', 'scene-hits.tsv')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(rows):
    previous = 0
    frames = []
    for row in rows:
        accepted = int(row['accepted'])
        tick = int(row['tick'])
        if accepted < previous:
            raise ValueError('Accepted counter moved backwards.')
        full = accepted > previous and not int(row['failed'])
        terrain = bool(int(row.get('terrain_presenting', 0)))
        if full and terrain:
            raise ValueError('Two compositors claimed the same Present.')
        frames.append({'tick': tick, 'hd': full or terrain, 'family': full, 'terrain': terrain,
                       'failed': bool(int(row['failed']))})
        previous = accepted
    runs = []
    for frame in frames:
        if runs and runs[-1]['hd'] == frame['hd'] and runs[-1]['last'] + 1 == frame['tick']:
            runs[-1]['last'] = frame['tick']
        else:
            runs.append({'first': frame['tick'], 'last': frame['tick'], 'hd': frame['hd']})
    return {'visible_presents': len(frames), 'hd_presents': sum(r['hd'] for r in frames),
            'classic_presents': sum(not r['hd'] for r in frames),
            'family_hd_presents': sum(r['family'] for r in frames),
            'terrain_only_presents': sum(r['terrain'] for r in frames),
            'family_mode_switches': sum(a['family'] != b['family'] for a, b in zip(frames, frames[1:])),
            'mode_switches': sum(a['hd'] != b['hd'] for a, b in zip(frames, frames[1:])),
            'runs': runs}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--build-receipt', type=Path, help='Explicit immutable historical build snapshot; default checks current source')
    parser.add_argument('--terrain-fallback', action='store_true')
    parser.add_argument('--static-hud', action='store_true')
    parser.add_argument('--dynamic-hud', action='store_true')
    parser.add_argument('--scale', type=int, choices=(2, 4), default=2)
    parser.add_argument('--capture-start', type=int, default=298)
    parser.add_argument('--capture-count', type=int, default=12)
    args = parser.parse_args(argv)
    if args.dynamic_hud and not args.static_hud:
        parser.error('--dynamic-hud requires --static-hud')
    data, out = args.data.resolve(), args.out.resolve()
    if out.exists() or out == ROOT or ROOT in out.parents:
        parser.error('Use a fresh output directory outside the repository.')
    if out == data or data in out.parents or out in data.parents:
        parser.error('Keep output separate from the original input directory.')
    if not 245 <= args.capture_start < 600 or not 1 <= args.capture_count <= 120 or args.capture_start + args.capture_count > 600:
        parser.error('Capture must fit the visible 245..599 interval, at most 120 frames.')
    for name, digest in DATA_PINS.items():
        if not (data/name).is_file() or sha(data/name) != digest:
            parser.error('Original input fingerprint mismatch: ' + name)
    baseline = args.baseline.resolve() if args.baseline else None
    if baseline and any(not (baseline/name).is_file() for name in NATIVE_STREAMS):
        parser.error('Baseline lacks a required native stream.')
    before = {p.name: sha(p) for p in data.iterdir() if p.is_file()}
    if args.build_receipt:
        receipt_path = args.build_receipt.resolve()
        build = json.loads(receipt_path.read_text())
        stage = receipt_path.parent
        if stage != Path(build['stage']):
            raise ValueError('Build receipt must remain at its original stage location.')
    else:
        plan = json.loads(subprocess.check_output([sys.executable, 'scripts/build_level2_family.py', '--check-only'], cwd=ROOT, text=True))
        stage = Path(plan['stage'])
        build = json.loads((stage/'BUILD.json').read_text())
        for key in ('source_sha256', 'asset_header_sha256', 'compiler', 'cppflags', 'cflags', 'ldflags', 'libs'):
            if plan[key] != build[key]:
                raise ValueError('Rebuild current family sources/toolchain before checking.')
    for name, digest in build['source_sha256'].items():
        if sha(stage/'src'/name) != digest:
            raise ValueError('Changed staged source: ' + name)
    for name, digest in build['asset_header_sha256'].items():
        if sha(stage/'assets'/name) != digest:
            raise ValueError('Changed staged header: ' + name)
    for name, digest in build['object_sha256'].items():
        if sha(stage/'obj'/name) != digest:
            raise ValueError('Changed staged object: ' + name)
    out.mkdir(mode=0o700)
    receipt = {'status': 'RUNNING', 'source_digest': build['source_digest'], 'scale': args.scale,
               'original_data_sha256': before, 'capture': [args.capture_start, args.capture_count],
               'wrapper_sha256': sha(ROOT/'tests/fixtures/level2_preview_observer.c'),
               'build_receipt': str(stage/'BUILD.json'), 'historical_snapshot': bool(args.build_receipt),
               'terrain_fallback': args.terrain_fallback, 'static_hud': args.static_hud, 'dynamic_hud': args.dynamic_hud}
    def save():
        (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    save()
    try:
        wrapper = out/'observe.o'
        extra = ['-DTERRAIN_FALLBACK_OBSERVER=1'] if 'b313_terrain_fallback.h' in build['source_sha256'] else []
        if args.terrain_fallback and not extra:
            raise ValueError('This staged source has no independent terrain fallback.')
        subprocess.run(build['compiler']+build['cppflags']+extra+build['cflags']+
                       ['-c', str(ROOT/'tests/fixtures/level2_preview_observer.c'), '-o', str(wrapper)], check=True)
        exe = out/'observer'
        subprocess.run(build['compiler']+build['ldflags']+[str(stage/'obj'/n) for n in build['object_sha256']]+
                       [str(wrapper)]+build['libs']+['-Wl,--wrap=SDL_RenderPresent', '-o', str(exe)], check=True)
        receipt['observer_sha256'] = sha(exe)
        cfg = out/'profile/config/opentyrian2000'
        cfg.mkdir(parents=True)
        (cfg/'opentyrian.cfg').write_text(f'section video\nitem scaler {args.scale}x\nitem fullscreen -1\n')
        (out/'assets').symlink_to(ROOT/'assets', target_is_directory=True)
        spec = importlib.util.spec_from_file_location('preview', ROOT/'scripts/preview_level2_frozen.py')
        preview = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(preview)
        # Reproduce the frozen launch controls without invoking its Windows dispatcher.
        # The current built engine is separately identified above, never called frozen.
        env = dict(os.environ, HOME=str(out/'profile'), XDG_CONFIG_HOME=str(out/'profile/config'),
                   SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software')
        launcher_spec = importlib.util.spec_from_file_location('launch', ROOT/'scripts/launch_level2_family.py')
        launcher = importlib.util.module_from_spec(launcher_spec)
        launcher_spec.loader.exec_module(launcher)
        env = {k: v for k, v in env.items() if not launcher.controlled_name(k)}
        env.update(preview.environment(ROOT))
        if args.terrain_fallback:
            env['BUILDING313_TERRAIN_FALLBACK_ENABLE'] = '1'
        if args.static_hud:
            hud = ROOT/'assets/hd/shared-ui-v1/gameplay-hud-v1.hda'
            if hud.stat().st_size != 4160064 or sha(hud) != '98cd6cfefa02a9ae79b75a65e02dd2566d3dec1492552f20b042b3c61c19cd17':
                raise ValueError('Changed static HUD asset.')
            env['BUILDING313_FAMILY_HUD_ENABLE'] = '1'
        if args.dynamic_hud:
            for name, (size, digest) in launcher.DYNAMIC_HUD_PINS.items():
                asset = ROOT/'assets/hd/shared-ui-v1'/name
                if asset.stat().st_size != size or sha(asset) != digest:
                    raise ValueError('Changed dynamic HUD asset: ' + name)
            env['BUILDING313_FAMILY_DYNAMIC_HUD_ENABLE'] = '1'
        command = [str(exe), '--data='+str(data), '--no-sound', '--no-joystick', '--no-xmas',
                   *preview.PREVIEW_ARGS[:-1], '--asset-debug-capture', '--asset-debug-window-only',
                   f'--asset-debug-capture-start={args.capture_start}', f'--asset-debug-capture-count={args.capture_count}']
        receipt['argv'] = command
        save()
        with (out/'run.log').open('w') as stream:
            subprocess.run(command, cwd=out, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=180)
        with (out/'continuity-present.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        if [int(r['tick']) for r in rows] != list(range(245, 600)):
            raise AssertionError('Expected exactly 355 visible actual Present calls at ticks245..599.')
        receipt.update(summarize(rows))
        receipt['canvas'] = json.loads((out/'building313-family-canvas.json').read_text())
        if receipt['canvas']['frames'] != 600 or receipt['canvas']['presents'] != receipt['family_hd_presents']:
            raise AssertionError('Native frame/presentation totals disagree.')
        terrain_total = int(rows[-1].get('terrain_presents', 0)) + int(rows[-1].get('terrain_presenting', 0))
        if terrain_total != receipt['terrain_only_presents']:
            raise AssertionError('Independent terrain Present total disagrees.')
        receipt['native_stream_sha256'] = {name: sha(out/name) for name in NATIVE_STREAMS}
        if baseline:
            receipt['baseline'] = str(baseline)
            receipt['native_streams_equal'] = {name: sha(out/name) == sha(baseline/name) for name in NATIVE_STREAMS}
            if not all(receipt['native_streams_equal'].values()):
                raise AssertionError('Original native state or event stream changed.')
        receipt['captures'] = {p.name: sha(p) for p in sorted(out.glob('asset-debug-window-*.bmp'))}
        if len(receipt['captures']) != args.capture_count:
            raise AssertionError('Missing actual Present capture.')
        if before != {p.name: sha(p) for p in data.iterdir() if p.is_file()}:
            raise AssertionError('Original data changed.')
        receipt['status'] = 'PASS_BOUNDED_CONTINUITY_MEASURED'
        save()
        print(json.dumps({k: receipt[k] for k in ('status', 'hd_presents', 'classic_presents', 'mode_switches')}))
    except Exception as exc:
        receipt.update(status='FAILED', error=str(exc))
        save()
        raise
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
