#!/usr/bin/env python3
"""Finite Charge252..254 binding gate. No captures; legal data and accepted pack stay external."""
import argparse
import collections
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

SPEC = importlib.util.spec_from_file_location('charge_preview', Path(__file__).with_name('test-charge-preview.py'))
PREVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREVIEW)
rows, digest = PREVIEW.rows, PREVIEW.digest
IDS = {252, 253, 254}
FROZEN_MANIFEST = 'e66f9b47a48233164b9f9537440d620f90b9c3de63998d1da4f09c5659df60be'
LOGICAL = ['state.tsv', 'collisions.tsv', 'weapon-loadout.tsv', 'sidekick-loadout.tsv', 'sidekick-states.tsv',
           'player-shot-requests.tsv', 'player-shot-emissions.tsv', 'player-shot-results.tsv', 'player-shot-draws.tsv',
           'poses.tsv', 'fire-events.tsv', 'player-projectiles.tsv', 'enemy-projectiles.tsv', 'scene-enemies.tsv', 'scene-hits.tsv']


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('exe', 'baseline-exe', 'data', 'assets', 'manifest', 'out'):
        p.add_argument('--' + arg, type=Path, required=True)
    p.add_argument('--candidate-pack', type=Path, help='Directory containing the three frozen HDA files; defaults to manifest-relative paths')
    p.add_argument('--resume', action='store_true', help='Reuse only completed runs with exact commands and zero-exit receipts')
    a = p.parse_args()
    exe, base, data, accepted, manifest, out = (getattr(a, x).resolve() for x in
                                              ('exe', 'baseline_exe', 'data', 'assets', 'manifest', 'out'))
    assert digest(manifest) == FROZEN_MANIFEST
    art = json.loads(manifest.read_text())
    assert {f['sprite_id'] for f in art['frames']} == IDS
    frozen = {}
    for frame in art['frames']:
        source = (a.candidate_pack.resolve() / Path(frame['hda']).name) if a.candidate_pack else manifest.parent / frame['hda']
        raw = source.read_bytes()
        assert digest(source) == frame['hda_sha256']
        assert raw[:4] == b'HDR1' and struct.unpack('<6I', raw[4:28]) == (80000 + frame['sprite_id'], 8, 12, 14, 0, 0)
        assert len(raw) == 28 + 96 * 112 * 4
        frozen[frame['sprite_id']] = source
    # Permit the current public pack as input after integration. Baseline links
    # always exclude the three candidate filenames, then each test overlays only
    # its explicitly verified frozen candidate identities.
    candidate_names = {f.name for f in frozen.values()}
    accepted_files = [f for f in accepted.iterdir() if f.name not in candidate_names]
    out.mkdir(parents=True, exist_ok=a.resume)
    packs = out / 'packs'
    packs.mkdir(exist_ok=a.resume)
    packs_by_case = {}
    for label, missing, bad in [('full', set(), set()), ('missing-all', IDS, set())] + \
            [('missing-' + str(i), {i}, set()) for i in sorted(IDS)] + \
            [('invalid-' + str(i), set(), {i}) for i in sorted(IDS)]:
        pack = packs / label
        if pack.exists():
            assert a.resume
            assert {f.name for f in pack.iterdir()} == {f.name for f in accepted_files} | {f.name for i, f in frozen.items() if i not in missing}
            for f in accepted_files:
                assert (pack / f.name).is_symlink() and (pack / f.name).resolve() == f
            for i, f in frozen.items():
                if i in missing:
                    continue
                if i in bad:
                    raw = bytearray(f.read_bytes())
                    raw[20:24] = struct.pack('<I', 1)
                    assert (pack / f.name).read_bytes() == raw
                else:
                    assert (pack / f.name).is_symlink() and (pack / f.name).resolve() == f
            packs_by_case[label] = pack
            continue
        pack.mkdir()
        for f in accepted_files:
            assert f.is_file(), f
            (pack / f.name).symlink_to(f)
        for i, f in frozen.items():
            if i in missing:
                continue
            if i in bad:
                raw = bytearray(f.read_bytes())
                raw[20:24] = struct.pack('<I', 1)  # Invalid anchor, only in a new private test file.
                (pack / f.name).write_bytes(raw)
            else:
                (pack / f.name).symlink_to(f)
        packs_by_case[label] = pack
    receipts = []

    def run(name, *, baseline=False, episode=1, scale=2, mode='8', pack='full', mirrored=IDS, level=None, known_water_fallback=False):
        dest = out / name
        conf = dest / 'config' / 'opentyrian2000'
        reused = dest.exists()
        assert not reused or a.resume
        conf.mkdir(parents=True, exist_ok=a.resume)
        config = PREVIEW.CONFIG.replace("'2x'", "'%dx'" % scale)
        if reused:
            assert (conf / 'opentyrian.cfg').read_text() == config
        else:
            (conf / 'opentyrian.cfg').write_text(config)
        command = [str(base if baseline else exe), '--data=' + str(data), '--no-sound', '--no-joystick', '--no-xmas',
                   '--asset-debug=custom', '--asset-debug-index-only', '--asset-debug-reference', '--render-scene=v1',
                   '--render-test=' + mode, '--render-assets=' + str(packs_by_case[pack]), '--render-scene-assets=all',
                   '--render-no-capture', '--render-front-port=0', '--render-rear-port=0',
                   '--render-left-sidekick=3', '--render-right-sidekick=3', '--render-sidekick-input=charge-stages',
                   '--asset-debug-episode=' + str(episode)]
        if level is None:
            level = 3 if episode == 4 else 1 if episode == 5 else 9
        command.append('--asset-debug-level=' + str(level))
        exit_receipt = {'game': 0, 'fifo_reader': 0, 'executable_sha256': digest(base if baseline else exe)}
        if reused:
            assert json.loads((dest / 'command.json').read_text()) == command
            assert json.loads((dest / 'game-exit.json').read_text()) == exit_receipt
        else:
            (dest / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
            fifo = dest / 'blend-writes.tsv'
            os.mkfifo(fifo)
            env = dict(os.environ, XDG_CONFIG_HOME=str(conf.parent), HOME=str(dest),
                       SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy', SDL_RENDER_DRIVER='software')
            with (dest / 'blend-proof.log').open('w') as proof_log:
                reader = subprocess.Popen([sys.executable, str(Path(__file__).with_name('stream-blend-proof.py')),
                                           '--input', str(fifo), '--output', str(dest / 'blend-proof.json')],
                                          stdout=proof_log, stderr=subprocess.STDOUT)
                try:
                    with (dest / 'stdout.log').open('w') as stdout, (dest / 'stderr.log').open('w') as stderr:
                        proc = subprocess.run(command, cwd=dest, env=env, stdout=stdout, stderr=stderr, timeout=240)
                    assert proc.returncode == 0, (name, proc.returncode, (dest / 'stderr.log').read_text())
                    reader.wait(timeout=60)
                    assert reader.returncode == 0, (name, (dest / 'blend-proof.log').read_text())
                finally:
                    if reader.poll() is None:
                        reader.terminate()
                        reader.wait(timeout=10)
            (dest / 'game-exit.json').write_text(json.dumps(exit_receipt) + '\n')
        assert (conf / 'opentyrian.cfg').read_text() == config
        assert not [f for f in dest.rglob('*') if f.suffix.lower() in ('.bmp', '.png', '.gif', '.mp4', '.webm')]
        coverage = PREVIEW.verify_charge(dest, [0, 1], episode)
        frames = rows(dest / 'frames.tsv')
        assert len(rows(dest / 'state.tsv')) == len(frames) == 90
        if known_water_fallback:
            assert episode == 4 and level == 9
            assert all(r['reason'] == 'smoothie-surface-routing' and 'water_filter' in r['all_rejections'] for r in frames)
        else:
            assert all(r['coverage_mismatch'] == '0' for r in frames), (name, frames[:3])
        assert not any('capacity' in r['all_rejections'] for r in frames), (name, 'renderer capacity rejection')
        if mode != 'classic':
            runtime = rows(dest / 'sdl-runtime.tsv')[0]
            assert (int(runtime['window_w']), int(runtime['window_h']), int(runtime['render_output_w']), int(runtime['render_output_h'])) == (320 * scale, 200 * scale) * 2
            assert runtime['renderer_info_ok'] == runtime['render_output_ok'] == '1'
        assert all(r['rng_before'] == r['rng_after'] for r in rows(dest / 'presentation.tsv'))
        assert all(r['classic_mismatches'] == '0' for r in rows(dest / 'rgb-audit.tsv'))
        assert all(r['restored_mismatches'] == '0' for r in rows(dest / 'effects.tsv'))
        commands = [r for r in rows(dest / 'draw-commands.tsv') if r['bank'] == '8' and int(r['index']) in IDS]
        normal = [r for r in commands if r['style'] == '0']
        shadows = [r for r in commands if r['style'] == '2']
        assert normal, name
        assert all(r['layout'] == '0' for r in commands)
        assert all(r['mirrored'] == '0' for r in shadows), name + ': changed original shadow path'
        assert all(int(r['mirrored']) == int(int(r['index']) in mirrored) for r in normal), name + ': per-ID HD/fallback mismatch'
        blend = json.loads((dest / 'blend-proof.json').read_text())
        result = dict(case=name, episode=episode, level=level, scale=scale, mode=mode, pack=pack, baseline=baseline,
                      known_water_fallback=known_water_fallback,
                      coverage=coverage, frames=90, window=[320 * scale, 200 * scale] if mode != 'classic' else None,
                      hd_draws=sum(int(r['hd_draws']) for r in frames),
                      head_draws=dict(collections.Counter(r['index'] for r in normal)), shadow_draws=len(shadows),
                      mirrored_ids=sorted(mirrored), blend_rows=blend['raw_rows'], blend_bytes=blend['raw_bytes'],
                      tsv_sha256={f.name: digest(f) for f in dest.glob('*.tsv') if f.is_file()}, media_bytes=0)
        receipts.append(result)
        print('PASS: ' + name + ' ' + json.dumps({k: result[k] for k in ('head_draws', 'shadow_draws', 'mirrored_ids', 'hd_draws')}), flush=True)
        return dest

    def compare_logic(before, after, compare_scene=True):
        for name in LOGICAL:
            assert digest(before / name) == digest(after / name), (before, after, name)
        for name, keys in [('effects.tsv', ('tick', 'invulnerable_ticks', 'level_brightness', 'filter_fade')),
                           ('draw-commands.tsv', ('tick', 'bank', 'index', 'x', 'y', 'style', 'layout')),
                           ('scene-draw-commands.tsv', ('tick', 'role', 'index', 'x', 'y', 'part', 'style'))]:
            if name == 'scene-draw-commands.tsv' and not compare_scene:
                continue
            assert [tuple(r[k] for k in keys) for r in rows(before / name)] == [tuple(r[k] for k in keys) for r in rows(after / name)], name
        b, c = (json.loads((path / 'blend-proof.json').read_text()) for path in (before, after))
        assert b['raw_rows'] == c['raw_rows'] and b['original_normalized_sha256'] == c['original_normalized_sha256']
        assert [(r['tick'], r['rows'], r['original_normalized_sha256']) for r in b['tick_proofs']] == \
               [(r['tick'], r['rows'], r['original_normalized_sha256']) for r in c['tick_proofs']]

    def compare_exact(before, after):
        a_files = {f.name for f in before.glob('*.tsv') if f.is_file()}
        b_files = {f.name for f in after.glob('*.tsv') if f.is_file()}
        assert a_files == b_files
        for name in sorted(a_files):
            assert digest(before / name) == digest(after / name), (before, after, name)
        assert (before / 'blend-proof.json').read_bytes() == (after / 'blend-proof.json').read_bytes()

    before, after = {}, {}
    for episode in (1, 4, 5):
        before[episode] = run('e%d-baseline-2x' % episode, baseline=True, episode=episode, mirrored=set())
        after[episode] = run('e%d-candidate-2x' % episode, episode=episode)
        compare_logic(before[episode], after[episode])
        assert digest(before[episode] / 'rgb-audit.tsv') != digest(after[episode] / 'rgb-audit.tsv'), 'Art made no visible RGB change'
    wb = run('e4-level9-baseline-fallback', baseline=True, episode=4, level=9, mirrored=set(), known_water_fallback=True)
    wc = run('e4-level9-candidate-fallback', episode=4, level=9, mirrored=set(), known_water_fallback=True)
    compare_exact(wb, wc)
    b4 = run('e1-baseline-4x', baseline=True, scale=4, mirrored=set())
    c4 = run('e1-candidate-4x', scale=4)
    compare_logic(b4, c4)
    compare_logic(after[1], c4)
    assert digest(after[1] / 'rgb-audit.tsv') == digest(c4 / 'rgb-audit.tsv'), 'Logical compositor changed with native output size'
    repeat = run('e1-candidate-repeat')
    compare_exact(after[1], repeat)
    absent = run('e1-family-all-missing', pack='missing-all', mirrored=set())
    compare_exact(before[1], absent)
    baseline_rgb = {r['tick']: r for r in rows(before[1] / 'rgb-audit.tsv')}
    for prefix in ('missing', 'invalid'):
        for index in sorted(IDS):
            dest = run('e1-' + prefix + '-' + str(index), pack=prefix + '-' + str(index), mirrored=IDS - {index})
            compare_logic(before[1], dest)
            # Charge heads never overlap between stages in this finite route.
            # In every live tick of the missing/invalid identity, exact full-frame
            # RGBA must equal the unchanged baseline. Other two heads still draw HD.
            commands = [r for r in rows(dest / 'player-shot-draws.tsv') if r['style'] == '0']
            per_tick = collections.defaultdict(set)
            for r in commands:
                per_tick[r['tick']].add(int(r['index']))
            ticks = {t for t, ids in per_tick.items() if ids == {index}}
            assert ticks
            actual = {r['tick']: r for r in rows(dest / 'rgb-audit.tsv')}
            assert all(actual[t] == baseline_rgb[t] for t in ticks), (dest, 'fallback RGB differs from original')
    for mode in ('classic', 'missing', 'invalid', '4'):
        b = run('e1-baseline-' + mode, baseline=True, mode=mode, mirrored=set())
        c = run('e1-candidate-' + mode, mode=mode, mirrored=set())
        compare_exact(b, c)
        compare_logic(before[1], c, compare_scene=False)
    assert digest(manifest) == FROZEN_MANIFEST
    assert all(digest(frozen[f['sprite_id']]) == f['hda_sha256'] for f in art['frames'])
    summary = dict(status='passed', source_baseline='85cdb5dd31f97f8bf10dd564027cd26ff24c4891',
                   candidate_manifest_sha256=FROZEN_MANIFEST, candidate_hda_sha256={str(f['sprite_id']): f['hda_sha256'] for f in art['frames']},
                   baseline_executable_sha256=digest(base), candidate_executable_sha256=digest(exe),
                   game_runs=len(receipts), logic_ticks=sum(r['frames'] for r in receipts), media_bytes=0,
                   scope='Finite bank8 tile252..254 heads; original indexed shadows and bank9 launchers. Latent793/1793 reuse untested.',
                   effects_comparison='Exact indexed state includes particles, RNG and collision state. Effect semantic fields exact; renderer ownership counters may differ. Restored/classic pixel mismatches must remain zero.',
                   mount_boundaries='Runtime both mounts; standalone0/3 selection proof reused from published fixture. Binder neighbor/bank/layout/cache boundaries separately tested.',
                   cases=receipts)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('PASS: %d runs, %d renderer frames, no captures' % (len(receipts), summary['logic_ticks']), flush=True)


if __name__ == '__main__':
    main()
