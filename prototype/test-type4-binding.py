#!/usr/bin/env python3
"""Finite current-source type4 loader/route/filter units; never launches a game.

Production src must project byte-for-byte to 317bf551. The sole exception is
the exact approved eight C-v2 FNV pins and their adjacent contract comment.
Only recording and material/telemetry boundaries are substituted. The actual
current loader, family gates, bank routes and palette helper are extracted.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import type15_source_projection as projection

BASE = '317bf551db59df9c4e3754d2072446c7313ab1f4'
IDS = [159, 161, 163, 165, 167]
ORDER = [159,159,161,161,163,163,165,165,167,167,165,165,163,163,161,161,159,159,159,159]
FAMILIES = ['cash25', 'cash75', 'cash50', 'gem100', 'linked31', 'newsh4_long7',
            'newsh4_opposite7', 'type15_eightheading', 'late_spike',
            'newsh4_entry6', 'type3_small', 'boss_whole']
FUNCTIONS = (['read_asset', 'scene_asset'] + [f + '_family_ready' for f in FAMILIES]
             + ['cash25_surface_ready', 'cash25_pickup', 'cash75_pickup',
                'cash50_pickup', 'gem100_pickup', 'boss_whole_base_allowed',
                'render_mirror_enemy_tile', 'palette_rgb', 'enemy_filter_rgba'])
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--baseline', default=BASE, help='Must resolve to the fixed current-source base 317bf551')
    args = p.parse_args()
    repo, given = args.repo.resolve(), args.out.absolute()
    out = given.resolve()
    if (out.exists() or any(q.is_symlink() for q in [given, *given.parents])
            or repo == out or repo in out.parents or out in repo.parents):
        p.error('Use a fresh output directory outside the repository, without symlink components')
    git = lambda *a: subprocess.check_output(['git', '-C', str(repo), *a])
    assert git('rev-parse', args.baseline + '^{commit}').decode().strip() == BASE, 'Wrong baseline'
    source_bytes, baseline_bytes, c_version = projection.audit_sources(repo)
    tracked = sorted(source_bytes)
    actual = set(tracked)
    source_pins = {n: sha(raw) for n, raw in source_bytes.items()}
    projection_rejections = projection.rejection_tests(baseline_bytes)
    recorder_names = ['prototype/test-type4-binding.py', 'prototype/test-type4-binding.c',
                      'prototype/type15_source_projection.py']
    recorder_pins = {n: sha((repo / n).read_bytes()) for n in recorder_names}
    current = (repo / 'src/render_mirror.c').read_text()
    baseline = git('show', BASE + ':src/render_mirror.c').decode()
    proof_name = 'assets/hd/artwork/type4-fivepose-v1/proof/type4-source-proof.json'
    proof_raw = (repo / proof_name).read_bytes()
    assert proof_raw == git('show', BASE + ':' + proof_name), 'Historical order proof changed'
    record = json.loads(proof_raw)['record4']
    assert record['egraphic'] == ORDER and record['ani'] == 20
    assert record['esize'] == 1 and record['shapebank'] == 1
    caller = (repo / 'src/tyrian2.c').read_text()
    block = re.search(r'if \(enemy\[i\]\.size == 1\) // 2x2 enemy(.*?)\n\s*else', caller, re.S).group(1)
    quadrants = [tuple(map(int, x)) for x in re.findall(r'blit_enemy\(VGAScreen, i,\s*(-?\d+),\s*(-?\d+),\s*(\d+)\);', block)]
    assert quadrants == [(-6,-7,0), (6,-7,1), (-6,7,19), (6,7,20)]
    assert 'enemy[i].ey > -13' in block and 'enemy[i].ey > -26 && enemy[i].ey < 182' in block
    out.mkdir(parents=True)
    manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
    packs = {kind: repo / 'assets/hd/packs' / manifest['default_' + kind + '_pack'] for kind in ('preview','debug')}
    c_art_pins = {kind: projection.validate_pack(pack, c_version) for kind, pack in packs.items()}
    baseline_packs = {kind: projection.baseline_pack(repo, pack, out / ('baseline-' + kind + '-pack'))
                      for kind, pack in packs.items()}
    pack_pins = {kind: {q.name: sha(q.read_bytes()) for q in sorted(pack.glob('*.hda'))} for kind, pack in packs.items()}
    for pack in packs.values():
        for sprite_id in IDS:
            assert not (pack / f'enemy-newsh2-{sprite_id}-4.hda').exists(), 'Unexpected type4 4x artwork'
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
               UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    traces, compiled_receipts, commands, cases = {}, [], [], []

    def run(command, log):
        commands.append(command)
        result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=240)
        (out / log).write_text(result.stdout + result.stderr)
        result.check_returncode()
        return result.stdout

    for label, source in [('baseline', baseline), ('candidate', current)]:
        directory = out / label
        directory.mkdir()
        patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                    r'enum \{ ASSET_NEWSH2=.*?\};', r'static Asset assets\[\d+\];']
        declarations = '\n'.join(re.search(pattern, source, re.S).group() for pattern in patterns)
        declarations += '\n' + '\n'.join(re.search(r'static bool ' + f + r'_checked,' + f + r'_valid;', source).group() for f in FAMILIES)
        context_source = (repo / 'src/ground101_material.h').read_text()
        declarations += '\n' + re.search(r'typedef struct \{\s*unsigned type,pool_slot,availability,size;.*?\} G101EnemyContext;', context_source, re.S).group()
        (directory / 'production-types.inc').write_text(declarations + '\n')
        helpers = {name: extract(source, name) for name in FUNCTIONS}
        (directory / 'production-helpers.inc').write_text('\n'.join(helpers.values()))
        (directory / 'production-reset.inc').write_text('\n'.join(f'{f}_checked={f}_valid=false;' for f in FAMILIES) + '\n')
        (directory / 'production-order.inc').write_text('static const unsigned order[20]={' + ','.join(map(str, ORDER)) + '};\n'
            + 'static const int quadrants[4][3]={' + ','.join('{' + ','.join(map(str,q)) + '}' for q in quadrants) + '};\n')
        command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-Wno-misleading-indentation', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                   '-fno-pie', '-no-pie', '-I' + str(directory), str(repo / recorder_names[1]), '-o', str(directory / 'test')]
        run(command, label + '/compile.log')
        lane_packs = baseline_packs if label == 'baseline' else packs
        traces[label] = {kind: run([str(directory / 'test'), str(pack), 'trace', '31'], label + '/' + kind + '-trace.log') for kind, pack in lane_packs.items()}
        for kind, trace in traces[label].items():
            rows = {tuple(line.split()) for line in trace.splitlines()}
            assert all(('enemy', '1', str(sprite_id), str(396+k)) in rows
                       for k, sprite_id in enumerate(projection.IDS)), 'Incomplete C trace: ' + label + '/' + kind
        compiled_receipts.append({'label': label, 'functions_sha256': {n:sha(t.encode()) for n,t in helpers.items()},
                                  'declarations_sha256': sha(declarations.encode()), 'compile_command': command})
    projected_helpers = {name: sha(extract(projection.project_render(current.encode(), baseline.encode())[0].decode(), name).encode())
                         for name in FUNCTIONS}
    assert compiled_receipts[0]['functions_sha256'] == projected_helpers, 'Non-C production helper changed'
    assert traces['baseline'] == traces['candidate'], 'Namespace/route difference from source baseline'
    executable = str(out / 'candidate/test')

    def check(directory, mode, mask, label):
        output = run([executable, str(directory), mode, str(mask)], label + '.log')
        cases.append({'label': label, 'mode': mode, 'present_mask': mask, 'result': output.strip()})
        return output

    for kind, pack in packs.items():
        check(pack, 'test', 31, kind + '-all-present')
        check(pack, 'filter', 31, kind + '-all-byte-filters')
    fixtures = out / 'fixtures'
    fixtures.mkdir()
    pack = packs['preview']
    directory = fixtures / 'current'
    directory.mkdir()
    # Reuse one fixture. Every unmodified file is a symlink, opened only rb by
    # extracted read_asset; never write/chmod a source asset or a symlink target.
    for name in pack_pins['preview']:
        (directory / name).symlink_to(pack / name)
    mutations = 0
    for k, sprite_id in enumerate(IDS):
        name = f'enemy-newsh2-{sprite_id}-8.hda'
        raw = (pack / name).read_bytes()
        invalid = {'missing': None, 'magic': b'BAD!' + raw[4:], 'short-header': raw[:27],
                   'truncated': raw[:-1], 'trailing': raw + b'\0'}
        for field in range(6):
            bad = bytearray(raw)
            struct.pack_into('<I', bad, 4 + field * 4, struct.unpack_from('<I', bad, 4 + field * 4)[0] + 1)
            invalid['header-' + str(field)] = bytes(bad)
        for kind, data in invalid.items():
            target = directory / name
            if target.exists() or target.is_symlink():
                target.unlink()
            if data is not None:
                target.write_bytes(data)
            check(directory, 'test', 31 ^ (1 << k), f'{sprite_id}-{kind}')
            mutations += 1
        (directory / name).unlink()
        (directory / name).symlink_to(pack / name)
        # Type4 intentionally has no payload checksum/family latch. A correctly
        # framed payload mutation still loads; do not invent new reject policy.
        target = directory / name
        target.unlink()
        bad = bytearray(raw)
        bad[28] ^= 1
        bad[31] = 127
        target.write_bytes(bad)
        check(directory, 'test', 31, f'{sprite_id}-valid-payload-change')
        target.unlink()
        target.symlink_to(pack / name)
    for sprite_id in IDS:
        (directory / f'enemy-newsh2-{sprite_id}-8.hda').unlink()
    check(directory, 'test', 0, 'missing-all-five')
    missing_trace = check(directory, 'trace', 0, 'missing-all-five-namespace')
    expected = '\n'.join(line for line in traces['candidate']['preview'].splitlines()
                         if not (line.split()[0] == 'enemy' and int(line.split()[1]) == 1 and int(line.split()[2]) in IDS)) + '\n'
    assert missing_trace == expected, 'Missing type4 affected another namespace/binding'
    check(packs['preview'], 'gates', 31, 'gates-cache-allocation')
    assert source_pins == {n:sha((repo / n).read_bytes()) for n in tracked}, 'Production sources changed during units'
    assert actual == {str(q.relative_to(repo)) for q in (repo / 'src').rglob('*') if q.is_file() or q.is_symlink()}
    assert recorder_pins == {n:sha((repo / n).read_bytes()) for n in recorder_names}
    assert pack_pins == {kind:{q.name:sha(q.read_bytes()) for q in sorted(pack.glob('*.hda'))} for kind,pack in packs.items()}, 'Input pack changed during units'
    report = {'status':'PASS', 'baseline':BASE, 'production_source_exact_after_finite_C_projection':True,
              'C_revision':c_version, 'C_projection_rejection_tests':projection_rejections,
              'C_projection_allowed_differences':'exact eight ordered C-v2 FNV stamps plus exact adjacent contour-contract comment',
              'C_art_sha256':c_art_pins,
              'trace_lanes':'raw baseline source with pinned v1 C art; raw current source with matching pinned current C art',
              'production_source_files':len(tracked), 'source_sha256':source_pins,
              'recorder_sha256':recorder_pins, 'historical_order_proof_sha256':sha(proof_raw),
              'source_quadrants':quadrants, 'record4_order':ORDER,
              'unit_only_no_game_or_capture':True, 'sanitizers':['AddressSanitizer','UndefinedBehaviorSanitizer'],
              'leak_detection':False, 'runs':compiled_receipts, 'commands':commands,
              'namespace_trace_sha256':{k:sha(v.encode()) for k,v in traces['candidate'].items()},
              'namespace_trace_records':{k:len(v.splitlines()) for k,v in traces['candidate'].items()},
              'asset_input_sha256':pack_pins, 'per_member_rejection_cases':mutations,
              'case_count':len(cases), 'cases':cases,
              'coverage':{'ids':IDS,'slots':[369,370,371,372,373],'dimensions':[24,28],'anchor':[6,7],
                          'density':8,'all_256_filters':True,'missing_all_five':True,
                          'per_member_cache_and_allocation_failure':True,'atomic_type4_family':False,
                          'same_base_newsh4_159_slot':385,'newsh2_153_neighbor_slot':269,
                          'valid_payload_edits_accepted_by_existing_loader':True,
                          'source_pack_content_unchanged':True},
              'limitations':['Extracted unit recorder only; no game process, rendered pixels, visibility, native window or Windows acceptance.',
                             'Material eligibility and telemetry are stubbed; all bank/family loader and route helpers are production text.',
                             'The 20-step input comes from the unchanged historical record4 proof, not a newly executed game lifecycle.',
                             'Current type4 loader retries a missing/invalid 8x member at 4x; selected packs contain no type4 4x file, so it declines to classic independently.',
                             'No type4 payload checksum exists: malformed framing/header/length is rejected; otherwise payload bytes load unchanged.',
                             'LeakSanitizer is disabled; harness reset frees every loaded Asset allocation.']}
    (out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS:', out / 'receipt.json')


if __name__ == '__main__':
    main()
