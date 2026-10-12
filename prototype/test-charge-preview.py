#!/usr/bin/env python3
"""Capture-free Charge Cannon input proof; legal data/assets stay outside the source tree."""
import argparse
import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

CONFIG = "section 'video'\n item 'fullscreen' '-1'\n item 'scaler' '2x'\n item 'scaling_mode' 'Integer'\n"
PRESS = {2: (0, 101, 252, 2, -12, 6), 24: (1, 102, 253, 5, -10, 10),
         66: (2, 103, 254, 10, -8, 16)}


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter='\t'))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify_charge(dest, mounts, episode):
    requests = rows(dest / 'player-shot-requests.tsv')
    emissions = rows(dest / 'player-shot-emissions.tsv')
    results = rows(dest / 'player-shot-results.tsv')
    draws = rows(dest / 'player-shot-draws.tsv')
    states = rows(dest / 'sidekick-states.tsv')
    snapshots = {(int(s['tick']), s['phase'], int(s['mount'])): s for s in states}
    assert len(states) == len(snapshots) == 360, dest
    expected = [(tick, mount + 2, values[1]) for tick, values in PRESS.items() for mount in mounts]
    assert [(int(r['tick']), int(r['bay']), int(r['weapon'])) for r in requests] == expected, dest
    assert len(requests) == len(emissions) == len(results) == 3 * len(mounts), dest
    assert [r['call'] for r in requests] == [e['call'] for e in emissions] == [r['call'] for r in results], dest
    assert all(r['result'] == 'complete' and r['emitted'] == '1' for r in results), dest
    loadout = rows(dest / 'sidekick-loadout.tsv')
    assert len(loadout) == 2, dest
    for mount, record in enumerate(loadout):
        assert int(record['episode']) == episode and int(record['mount']) == mount, dest
        assert int(record['item']) == (3 if mount in mounts else 0), dest
        assert record['input'] == 'charge-stages' and record['ticks'] == '90', dest
        if mount in mounts:
            assert (record['max_charge'], record['port'], record['base_shot']) == ('2', '16', '101'), dest
    for tick in range(90):
        for mount in range(2):
            before, after = (snapshots[tick, phase, mount] for phase in ('input', 'end'))
            present = mount in mounts
            assert int(before['button']) == int(after['button']) == int(present and tick in PRESS), dest
            assert before['main_button'] == after['main_button'] == '0', dest
            assert int(before['item']) == int(after['item']) == (3 if present else 0), dest
            # Original style-0 origin uses the incoming mouse target. On tick 0,
            # the player is clamped from y=180 to160 after this target is sampled.
            assert int(after['x']) == int(before['player_x']) + (-14 if mount == 0 else 16), dest
            assert after['y'] == before['player_y'], dest
            if tick == 0:
                assert (before['charge'], before['charge_ticks'], before['repeat']) == ('0', '20', '1'), dest
            if tick:
                prev = snapshots[tick - 1, 'end', mount]
                assert (before['charge'], before['charge_ticks'], before['repeat']) == (prev['charge'], prev['charge_ticks'], prev['repeat']), dest
            if present and tick in PRESS:
                stage, _, _, _, _, repeat = PRESS[tick]
                assert int(before['charge']) == stage and before['repeat'] == '0', dest
                assert (after['charge'], after['charge_ticks'], int(after['repeat'])) == ('0', '19', repeat), dest
            else:
                charge, ticks = int(before['charge']), int(before['charge_ticks']) - 1
                if ticks == 0:
                    charge, ticks = min(charge + 1, 2 if present else 0), 20
                assert (int(after['charge']), int(after['charge_ticks'])) == (charge, ticks), dest
                expected_repeat = max(int(before['repeat']) - 1, 0) if present else int(before['repeat'])
                assert int(after['repeat']) == expected_repeat, dest
            # Power consumed only by the real two/single selected shots, not by
            # the observer. Generator regeneration precedes the input snapshot.
            consumed = 10 * len(mounts) if tick in PRESS else 0
            assert int(after['power']) == int(before['power']) - consumed, dest
    all_draws = collections.Counter(tuple(d[k] for k in ('tick', 'bank', 'index', 'x', 'y', 'style')) for d in draws)
    commands = collections.Counter(tuple(d[k] for k in ('tick', 'bank', 'index', 'x', 'y', 'style'))
                                   for d in rows(dest / 'draw-commands.tsv') if d['bank'] in ('5', '8', '12'))
    assert all_draws == commands, dest
    assert {(d['bank'], d['index']) for d in draws} == {('8', '252'), ('8', '253'), ('8', '254')}, dest
    expected_heads = [(e['slot'], e['raw_index']) for e in emissions]
    assert len(set(expected_heads)) == len(expected_heads), dest
    assert set((d['slot'], d['index']) for d in draws) == set(expected_heads), dest
    assert all(d['player'] == '1' and d['style'] in ('0', '2') for d in draws), dest
    for req, emission, result in zip(requests, emissions, results):
        tick, mount = int(req['tick']), int(req['bay']) - 2
        _, _, index, damage, vy, _ = PRESS[tick]
        end = snapshots[tick, 'end', mount]
        assert req['port'] == '16' and req['player'] == '1', dest
        assert (req['x'], req['y']) == (end['x'], end['y']) == (emission['x'], emission['y']), dest
        assert emission['slot'] == result['last_slot'], dest
        for key, value in dict(multi=1, pattern=1, player=1, vx=0, vy=vy, ax=0, ay=0, raw_index=index,
                               animation=0, animation_max=1, ttl=255, damage=damage, chain=0, trail=255, aim=0).items():
            assert int(emission[key]) == value, (dest, key, emission)
        # Slots are reused; pair draws to this request by slot + unique raw head.
        shot_draws = [d for d in draws if d['slot'] == emission['slot'] and int(d['index']) == index]
        normal = [d for d in shot_draws if d['style'] == '0']
        assert normal and int(normal[0]['tick']) == tick + 1, dest
        assert int(normal[0]['x']) == int(req['x']) + 1 and int(normal[0]['y']) == int(req['y']) + vy, dest
        assert all(d['raw_index'] == str(index) and d['width'] == '12' and d['height'] == '14'
                   and int(d['x']) == int(req['x']) + 1 for d in shot_draws), dest
        assert all(int(b['tick']) == int(a['tick']) + 1 and int(b['y']) == int(a['y']) + vy
                   for a, b in zip(normal, normal[1:])), dest
    return {'requests': len(requests), 'emissions': len(emissions), 'draws': len(draws),
            'head_ids': [252, 253, 254], 'mounts': mounts,
            'natural_collisions': len(rows(dest / 'collisions.tsv')),
            'passive_charge_and_reset_proved': True, 'power_rejections': 0, 'capacity_rejections': 0}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('exe', 'baseline-exe', 'data', 'assets', 'out'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--blend-proof-script', type=Path, default=Path(__file__).with_name('stream-blend-proof.py'))
    args = p.parse_args()
    exe, baseline, data, assets, proof, out = (getattr(args, n).resolve() for n in
                                             ('exe', 'baseline_exe', 'data', 'assets', 'blend_proof_script', 'out'))
    assert all(path.is_file() for path in (exe, baseline, proof))
    out.mkdir(parents=True, exist_ok=False)
    receipts = []

    def run(name, mode='classic', flags=(), ticks=90, base=False, invalid=False, probe=True, preset=False):
        dest = out / name
        conf = dest / 'config' / 'opentyrian2000'
        conf.mkdir(parents=True)
        (conf / 'opentyrian.cfg').write_text(CONFIG)
        command = [str(baseline if base else exe), '--data=' + str(data), '--no-sound', '--no-joystick', '--no-xmas']
        if probe:
            command += ['--asset-debug=custom', '--asset-debug-index-only', '--asset-debug-reference', '--render-scene=v1',
                        '--render-test=' + mode, '--render-assets=' + str(assets), '--render-scene-assets=off', '--render-no-capture']
            if not preset:
                command += ['--render-ticks=' + str(ticks)]
        command += list(flags)
        (dest / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        fifo = dest / 'blend-writes.tsv'
        os.mkfifo(fifo)
        env = dict(os.environ, XDG_CONFIG_HOME=str(conf.parent), HOME=str(dest),
                   SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software')
        with (dest / 'blend-proof.log').open('w') as log:
            reader = subprocess.Popen([sys.executable, str(proof), '--input', str(fifo), '--output', str(dest / 'blend-proof.json')],
                                      stdout=log, stderr=subprocess.STDOUT)
            try:
                with (dest / 'stdout.log').open('w') as stdout, (dest / 'stderr.log').open('w') as stderr:
                    proc = subprocess.run(command, cwd=dest, env=env, stdout=stdout, stderr=stderr, timeout=120)
                assert proc.returncode == (2 if invalid else 0), (name, proc.returncode, (dest / 'stderr.log').read_text())
                if invalid and not (dest / 'state.tsv').exists():
                    reader.terminate()  # Parse-time failure never opens the FIFO.
                reader.wait(timeout=30)
            finally:
                if reader.poll() is None:
                    reader.terminate()
                    reader.wait(timeout=10)
        assert (conf / 'opentyrian.cfg').read_text() == CONFIG, name
        assert not [f for f in dest.rglob('*') if f.suffix.lower() in ('.bmp', '.png', '.mp4', '.webm', '.gif')], name
        if invalid:
            assert not (dest / 'state.tsv').exists() or not rows(dest / 'state.tsv'), name
            receipts.append({'case': name, 'rejected': True, 'flags': list(flags)})
            return dest
        assert reader.returncode == 0 and stat.S_ISFIFO(fifo.stat().st_mode), name
        frames, state = rows(dest / 'frames.tsv'), rows(dest / 'state.tsv')
        assert len(frames) == len(state) == ticks, name
        presentations = rows(dest / 'presentation.tsv')
        if mode != 'classic':
            assert len(presentations) >= ticks, name
        assert all(r['rng_before'] == r['rng_after'] for r in presentations), name
        hashes = {f.name: digest(f) for f in dest.glob('*.tsv') if f.is_file()}
        blend = json.loads((dest / 'blend-proof.json').read_text())
        assert blend['status'] == 'passed' and not blend['retained_raw_copy'], name
        receipt = {'case': name, 'ticks': ticks, 'renderer_frames': len(frames), 'hd_draws': sum(int(f['hd_draws']) for f in frames),
                   'tsv_sha256': hashes, 'blend_raw_sha256': blend['raw_sha256'], 'blend_rows_streamed': blend['raw_rows'],
                   'blend_bytes_streamed': blend['raw_bytes'], 'media_bytes': 0}
        receipts.append(receipt)
        print('PASS: ' + name + ' (' + str(ticks) + ' renderer frames)', flush=True)
        return dest

    def exact(a, b, names=None, blend=False):
        names = names or sorted(f.name for f in a.glob('*.tsv') if f.is_file())
        assert all(digest(a / name) == digest(b / name) for name in names), (a, b, names)
        if blend:
            assert json.loads((a / 'blend-proof.json').read_text()) == json.loads((b / 'blend-proof.json').read_text()), (a, b)

    defaults = {}
    for mode in ('classic', '8'):
        before = run('baseline-' + mode, mode, base=True, ticks=120)
        current = run('default-' + mode, mode, ticks=120)
        exact(before, current, blend=True)
        if mode == '8':
            assert receipts[-1]['hd_draws'] > 0, 'Baseline comparison requires the actual accepted HD pack'
        assert not (current / 'sidekick-states.tsv').exists() and not (current / 'sidekick-loadout.tsv').exists()
        zero = run('zero-sidekicks-' + mode, mode, ticks=120,
                   flags=['--render-left-sidekick=0', '--render-right-sidekick=0'])
        exact(current, zero, blend=True)
        defaults[mode] = current
    common = ['--render-front-port=0', '--render-rear-port=0', '--render-sidekick-input=charge-stages']
    selected = []
    comparable = ['state.tsv', 'collisions.tsv', 'weapon-loadout.tsv', 'sidekick-loadout.tsv', 'sidekick-states.tsv',
                  'player-shot-requests.tsv', 'player-shot-emissions.tsv', 'player-shot-results.tsv', 'player-shot-draws.tsv']
    for episode in (1, 4, 5):
        group = []
        for mode in ('classic', '8'):
            flags = common + ['--render-left-sidekick=3', '--render-right-sidekick=3', '--asset-debug-episode=' + str(episode)]
            if episode == 5:
                flags += ['--asset-debug-level=1']
            dest = run('episode%d-both-%s' % (episode, mode), mode, flags, preset=True)
            receipts[-1].update(verify_charge(dest, [0, 1], episode))
            group.append(dest)
        exact(*group, names=comparable)
        selected.append(group[0])
    repeat = run('episode1-both-repeat', flags=common + ['--render-left-sidekick=3', '--render-right-sidekick=3'], preset=True)
    receipts[-1].update(verify_charge(repeat, [0, 1], 1))
    exact(selected[0], repeat, blend=True)
    for mount, label in ((0, 'left'), (1, 'right')):
        dest = run('episode1-' + label, flags=common + ['--render-' + label + '-sidekick=3'], preset=True)
        receipts[-1].update(verify_charge(dest, [mount], 1))
    passive = run('passive-main-button', flags=['--render-front-port=0', '--render-rear-port=0',
                  '--render-left-sidekick=3', '--render-right-sidekick=3'])
    assert not rows(passive / 'player-shot-requests.tsv'), passive
    end = [s for s in rows(passive / 'sidekick-states.tsv') if s['tick'] == '89' and s['phase'] == 'end']
    assert len(end) == 2 and all(s['charge'] == '2' and s['button'] == '0' and s['main_button'] == '1' for s in end), passive
    receipts[-1]['passive_charge_without_dedicated_fire_proved'] = True
    bad = []
    for mount in ('left', 'right'):
        bad += [[f'--render-{mount}-sidekick={v}'] for v in ('', '1', '2', '4', '-1', '+3', ' 3', '3x', '3.0', '999999999999999999999')]
    bad += [['--render-sidekick-input=' + v] for v in ('', 'unknown', 'charge-stagesx')]
    bad += [common, common + ['--render-left-sidekick=3', '--render-front-port=1'],
            common + ['--render-right-sidekick=3', '--render-rear-port=1']]
    bad += [common + ['--render-left-sidekick=3', '--render-ticks=' + v]
            for v in ('', '0', '-1', '+90', ' 90', '90', '91', '90x', '999999999999999999999')]
    for i, flags in enumerate(bad):
        run('invalid-%02d' % i, flags=flags, invalid=True, preset=True)
    for i, flags in enumerate((['--render-left-sidekick=3'], ['--render-right-sidekick=0'], ['--render-sidekick-input=charge-stages'])):
        run('requires-probe-%d' % i, flags=flags, invalid=True, probe=False, preset=True)
    summary = {'status': 'passed', 'scope': 'Charge Cannon debug input fixture, no new art; no campaign acquisition or hit-effect acceptance.',
               'baseline_executable_sha256': digest(baseline), 'candidate_executable_sha256': digest(exe),
               'data_sha256': {name: digest(data / name) for name in ('tyrian.hdt', 'tyrian4.lvl', 'tyrian5.lvl')},
               'default_classic_hd_exact': True, 'no_capture_media_bytes': 0, 'results': receipts}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('PASS: %d runs, %d invalid rejections, %d real renderer frames, no captures' %
          (sum(not r.get('rejected') for r in receipts), sum(bool(r.get('rejected')) for r in receipts),
           sum(r.get('renderer_frames', 0) for r in receipts)), flush=True)


if __name__ == '__main__':
    main()
