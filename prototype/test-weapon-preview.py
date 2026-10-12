#!/usr/bin/env python3
"""Bounded, capture-free real-game weapon previews. Legal data stays outside Git."""
import argparse
import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', type=Path, required=True)
    parser.add_argument('--baseline-exe', type=Path)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    exe, data, assets, out = (p.resolve() for p in (args.exe, args.data, args.assets, args.out))
    out.mkdir(parents=True, exist_ok=False)
    config = "section 'video'\n item 'fullscreen' '-1'\n item 'scaler' '2x'\n item 'scaling_mode' 'Integer'\n"
    results = []

    def run(name, mode='classic', flags=(), ticks=120, baseline=False, invalid=False, probe=True, live_debug=False):
        dest = out / name
        conf = dest / 'config' / 'opentyrian2000'
        conf.mkdir(parents=True)
        config_file = conf / 'opentyrian.cfg'
        config_file.write_text(config)
        command = [str(args.baseline_exe.resolve() if baseline else exe), '--data=' + str(data),
                   '--no-sound', '--no-joystick', '--no-xmas']
        if probe:
            # Index-only already suppresses captures in the unchanged baseline.
            command += ['--asset-debug=custom', '--asset-debug-index-only', '--asset-debug-reference', '--render-scene=v1',
                        '--render-test=' + mode, '--render-ticks=' + str(ticks),
                        '--render-assets=' + str(assets), '--render-scene-assets=off']
            if not baseline:
                command += ['--render-no-capture']
        command += list(flags)
        if live_debug:
            command.remove('--asset-debug-index-only')
        env = dict(os.environ, XDG_CONFIG_HOME=str(conf.parent), HOME=str(dest),
                   SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software')
        with (dest / 'stdout.log').open('w') as stdout, (dest / 'stderr.log').open('w') as stderr:
            proc = subprocess.run(command, cwd=dest, env=env, stdout=stdout, stderr=stderr, timeout=120)
        assert proc.returncode == (2 if invalid else 0), (name, proc.returncode, (dest / 'stderr.log').read_text())
        assert not list(dest.rglob('*.bmp')), name + ': unexpected screenshot'
        assert config_file.read_text() == config, name + ': input config mutated'
        if invalid:
            assert 'Weapon preview' in (dest / 'stderr.log').read_text(), name
            assert not (dest / 'state.tsv').exists() or len(rows(dest / 'state.tsv')) == 0, name
            results.append({'case': name, 'rejected': True, 'flags': list(flags)})
            return dest
        state = rows(dest / 'state.tsv')
        assert len(state) == ticks, (name, len(state))
        assert "failed to open 'opentyrian.cfg'" not in (dest / 'stderr.log').read_text(), name
        presentations = rows(dest / 'presentation.tsv')
        frames = rows(dest / 'frames.tsv')
        assert len(frames) == ticks, (name, 'renderer did not execute', len(frames))
        if mode != 'classic':
            assert len(presentations) >= ticks, (name, 'presentation did not execute')
        assert all(p['rng_before'] == p['rng_after'] for p in presentations), name
        result = {'case': name, 'ticks': ticks, 'state_sha256': digest(dest / 'state.tsv'),
                  'collisions_sha256': digest(dest / 'collisions.tsv'),
                  'config_sha256': digest(config_file), 'collisions': len(rows(dest / 'collisions.tsv')),
                  'render_frames': len(frames), 'hd_draws': sum(int(f['hd_draws']) for f in frames)}
        if not baseline:
            requests = rows(dest / 'player-shot-requests.tsv')
            emitted = rows(dest / 'player-shot-emissions.tsv')
            finished = rows(dest / 'player-shot-results.tsv')
            assert [r['call'] for r in requests] == [r['call'] for r in finished], name
            counts = collections.Counter(e['call'] for e in emitted)
            assert sum(int(r['emitted']) for r in finished) == len(emitted), name
            assert all(counts[r['call']] == int(r['emitted']) for r in finished), name
            assert all(int(e['pattern']) in range(1, 9) for e in emitted), name
            draws = rows(dest / 'player-shot-draws.tsv')
            commands = rows(dest / 'draw-commands.tsv')
            observed = {(int(d['bank']), int(d['index'])) for d in draws if d['style'] != '2'}
            # One exact generic draw-command counterpart per gameplay head/shadow.
            fields = ('tick', 'bank', 'index', 'x', 'y', 'style')
            shot_commands = collections.Counter(tuple(d[k] for k in fields) for d in draws)
            all_commands = collections.Counter(tuple(d[k] for k in fields) for d in commands if d['bank'] in ('5', '8', '12'))
            assert shot_commands == all_commands, name + ': missing/extra head or shadow command'
            if name.startswith('pulse-p1-'):
                mirrored = [d for d in commands if d['bank'] == '8' and d['index'] == '59' and d['style'] == '0' and d['mirrored'] == '1']
                if mode in ('8', 'repeat'):
                    assert mirrored and result['hd_draws'] > 0, name + ': known-supported HD bullet did not draw'
                elif mode in ('classic', '4', 'missing', 'invalid'):
                    assert not mirrored and result['hd_draws'] == 0, name + ': expected classic fallback'
                    assert all(f['reason'] == 'classic-assets' for f in frames), name + ': unexpected fallback reason'
            result.update(loadout=rows(dest / 'weapon-loadout.tsv')[0], requests=len(requests), emissions=len(emitted), draws=len(draws),
                          identities=sorted('%d:%d' % pair for pair in observed),
                          results=dict(collections.Counter(r['result'] for r in finished)))
        results.append(result)
        print(json.dumps(result), flush=True)
        return dest

    def equal(paths, filenames):
        for filename in filenames:
            assert len({digest(p / filename) for p in paths}) == 1, (filename, [str(p) for p in paths])

    unchanged = run('default')
    if args.baseline_exe:
        baseline = run('baseline', baseline=True)
        equal([baseline, unchanged], ['state.tsv', 'collisions.tsv', 'poses.tsv',
                                    'fire-events.tsv', 'player-projectiles.tsv', 'presentation.tsv'])
        hd_default = run('default8', '8')
        hd_baseline = run('baseline8', '8', baseline=True)
        equal([hd_baseline, hd_default], ['state.tsv', 'collisions.tsv', 'poses.tsv', 'fire-events.tsv',
                                        'player-projectiles.tsv', 'presentation.tsv', 'frames.tsv', 'rgb-audit.tsv'])
    for power, expected in ((1, {'8:59'}), (2, {'8:60'}), (6, {'8:58', '8:165'}), (11, {'8:59', '8:62'})):
        group = [run('pulse-p%d-%s' % (power, mode), mode, ['--render-front-port=1',
                     '--render-front-power=' + str(power)]) for mode in ('classic', '4', '8', 'missing', 'invalid', 'repeat')]
        equal(group, ['state.tsv', 'collisions.tsv', 'weapon-loadout.tsv', 'player-shot-requests.tsv',
                      'player-shot-emissions.tsv', 'player-shot-results.tsv', 'player-shot-draws.tsv'])
        if power == 1:
            equal([unchanged, group[0]], ['state.tsv', 'collisions.tsv'])
        assert all(set(r['identities']) == expected for r in results[-6:]), (power, results[-6:])
    cases = [
        ('bank12', ['--render-front-port=3', '--render-front-power=6'], 120, {'12:98', '12:99', '12:117', '12:118'}),
        ('rear-mode1', ['--render-front-port=0', '--render-rear-port=10', '--render-rear-power=6', '--render-rear-mode=1'], 120, {'8:3', '8:41', '8:77'}),
        ('rear-mode2', ['--render-front-port=0', '--render-rear-port=10', '--render-rear-power=6', '--render-rear-mode=2'], 120, {'8:182', '8:183', '8:277', '8:278', '8:77'}),
        ('option-child', ['--render-front-port=0', '--render-rear-port=24', '--render-rear-power=6'], 900, {'5:33'}),
        ('poison-child', ['--render-front-port=33'], 360, {'8:103', '8:214', '8:215', '8:216', '8:217'}),
        ('episode4', ['--asset-debug-episode=4', '--render-front-power=11'], 120, {'8:59', '8:62'}),
        ('episode5', ['--asset-debug-episode=5', '--asset-debug-level=1', '--render-front-power=11'], 120, {'8:59', '8:62'}),
    ]
    for name, flags, ticks, expected in cases:
        group = [run(name + '-' + mode, mode, flags, ticks) for mode in ('classic', '8')]
        equal(group, ['state.tsv', 'collisions.tsv', 'weapon-loadout.tsv', 'player-shot-requests.tsv',
                      'player-shot-emissions.tsv', 'player-shot-results.tsv', 'player-shot-draws.tsv'])
        if expected:
            assert all(expected <= set(r['identities']) for r in results[-2:]), (name, results[-2:])
        if name in ('option-child', 'poison-child'):
            child = '87' if name == 'option-child' else '71'
            for path in group:
                assert any(r['weapon'] == child and r['bay'] == '4' for r in rows(path / 'player-shot-requests.tsv')), name
    invalid = [
        ['--render-front-port=' + value] for value in ('', '-1', '+1', ' 1', '1x', '16', '48', '99999999999999999999999999')
    ] + [['--render-front-power=' + value] for value in ('0', '12', '1.5', '')] + [
        ['--render-rear-mode=0'], ['--render-rear-mode=3'], ['--render-rear-mode=2'],
        ['--render-rear-port=15', '--render-rear-mode=2'], ['--render-rear-power=2'],
        ['--render-front-port=0', '--render-front-power=2'], ['--render-rear-port=16']]
    for i, flags in enumerate(invalid):
        run('invalid-%02d' % i, flags=flags, invalid=True)
    run('requires-probe', flags=['--render-front-power=6'], invalid=True, probe=False)
    run('no-capture-requires-probe', flags=['--render-no-capture'], invalid=True, probe=False)
    # Explicit debug-window capture must also honor the no-capture switch.
    run('capture-disabled', flags=['--asset-debug-tick=0', '--asset-debug-capture',
                                 '--asset-debug-capture-count=1', '--asset-debug-running'], live_debug=True)
    summary = {'scope': 'Debug fixture and observability; no new HD art is included.',
               'data_sha256': {name: digest(data / name) for name in ('tyrian.hdt', 'tyrian4.lvl', 'tyrian5.lvl')},
               'no_capture_media_bytes': 0, 'baseline_checked': bool(args.baseline_exe), 'results': results}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('PASS: %d bounded runs; no screenshots; output %s' % (len(results), out), flush=True)


if __name__ == '__main__':
    main()
