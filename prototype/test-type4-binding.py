#!/usr/bin/env python3
"""Production-function ASan/UBSan oracle and complete baseline preservation audit.

Draw calls are recorded, not rendered. This is source/loader coverage and does
not establish actual game visibility, native RGB appearance or Windows runtime.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess

BASE = '93de0fe4cb935f1d7cf7d737c86e0ff3f3f8c218'
IDS = [159, 161, 163, 165, 167]
ADDITION = ''' /* Type4: five complete24x28 newsh2 composites, never individual cells.
  * Keep the original four ordered quadrant calls, cycle, filters and death. */
 if(role==ASSET_NEWSH2) {
  static const unsigned int type4_ids[5]={159,161,163,165,167};
  for(int i=0;i<5;i++)if(base==type4_ids[i]){slot=369+i;break;}
 }
'''
FUNCTIONS = ['read_asset', 'scene_asset', 'render_mirror_enemy_tile',
             'palette_rgb', 'enemy_filter_rgba']
sha = lambda data: hashlib.sha256(data).hexdigest()


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    start = source.index('{', match.start())
    end, depth = start + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--baseline', default=BASE, help='Exact pre-type4 baseline commit; permits a later additive source merge')
    args = p.parse_args()
    repo, given = args.repo.resolve(), args.out.absolute()
    baseline_commit = args.baseline
    out = given.resolve()
    if (out.exists() or any(q.is_symlink() for q in [given, *given.parents])
            or repo == out or repo in out.parents or out in repo.parents):
        p.error('Use a fresh output directory outside the repository, without symlink components')

    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])

    baseline = git('show', baseline_commit + ':src/render_mirror.c').decode()
    current = (repo / 'src/render_mirror.c').read_text()
    assert current.count('static Asset assets[374];') == current.count(ADDITION) == 1
    restored = current.replace('static Asset assets[374];', 'static Asset assets[369];').replace(ADDITION, '')
    assert restored == baseline, 'Renderer changed beyond the finite two-fragment append'
    tracked = git('ls-tree', '-r', '--name-only', baseline_commit).decode().splitlines()
    changed = []
    allowed = {'src/render_mirror.c', 'prototype/build-hd-assets.py', 'assets/hd/manifest.json'}
    compatibility_test = 'prototype/tests/startup-manufacturer/test_package.py'
    if compatibility_test in tracked:
        allowed.add(compatibility_test)
    for name in tracked:
        if (repo / name).is_file() and (repo / name).read_bytes() != git('show', baseline_commit + ':' + name):
            changed.append(name)
    assert set(changed) == allowed, changed
    old_manifest = json.loads(git('show', baseline_commit + ':assets/hd/manifest.json'))
    manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
    restored_manifest = json.loads(json.dumps(manifest))
    restored_manifest.pop('enemy_type4_fivepose_v1')
    for key in ('default_preview_pack', 'default_debug_pack'):
        pack = restored_manifest['packs'][manifest[key]]
        for sprite_id in IDS:
            entry = pack['files'].pop(f'enemy-newsh2-{sprite_id}-8.hda')
            restored_manifest['source_pngs'].pop(entry['sha256'], None)
        pack['count'] -= 5
    assert restored_manifest == old_manifest, 'Preexisting manifest content changed'
    assert 'terrain_sources[195]' in current
    out.mkdir(parents=True)
    pack = repo / 'assets/hd/packs' / manifest['default_preview_pack']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
               UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    trace = {}
    receipts = []
    for label, source in [('baseline', baseline), ('candidate', current)]:
        directory = out / label
        directory.mkdir()
        definition = re.search(r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;', source, re.S).group()
        array = re.search(r'static Asset assets\[\d+\];', source).group()
        (directory / 'production-types.inc').write_text(definition + '\n' + array + '\n')
        helpers = {name: extract(source, name) for name in FUNCTIONS}
        (directory / 'production-helpers.inc').write_text('\n'.join(helpers.values()))
        command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                   '-Wno-misleading-indentation', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                   '-fno-pie', '-no-pie', '-DBASELINE=' + str(int(label == 'baseline')),
                   '-I' + str(directory), str(repo / 'prototype/test-type4-binding.c'), '-o', str(directory / 'test')]
        compiled = subprocess.run(command, capture_output=True, text=True)
        (directory / 'compile.log').write_text(compiled.stdout + compiled.stderr)
        compiled.check_returncode()
        run = subprocess.run([str(directory / 'test'), str(pack), 'trace', '31'], env=env,
                             capture_output=True, text=True, timeout=90)
        (directory / 'trace.log').write_text(run.stdout + run.stderr)
        run.check_returncode()
        trace[label] = {tuple(map(int, line.split()[:2])): int(line.split()[2]) for line in run.stdout.splitlines()}
        receipts.append({'label': label, 'compile_command': command,
                         'functions': {name: sha(text.encode()) for name, text in helpers.items()}})
    expected = dict(trace['baseline'])
    expected.update({(1, sprite_id): 369 + k for k, sprite_id in enumerate(IDS)})
    assert trace['candidate'] == expected
    executable = out / 'candidate/test'
    results = []

    def check(directory, mask, label):
        result = subprocess.run([str(executable), str(directory), 'test', str(mask)], env=env,
                                capture_output=True, text=True, timeout=90)
        (out / (label + '.log')).write_text(result.stdout + result.stderr)
        result.check_returncode()
        results.append(label)

    check(pack, 31, 'all-present')
    fixtures = out / 'fixtures'
    fixtures.mkdir()
    for k, sprite_id in enumerate(IDS):
        name = f'enemy-newsh2-{sprite_id}-8.hda'
        raw = (pack / name).read_bytes()
        invalid = {'missing': None, 'magic': b'BAD!' + raw[4:], 'truncated': raw[:-1],
                   'trailing': raw + b'\0'}
        for field in range(6):
            bad = bytearray(raw)
            old = struct.unpack_from('<I', bad, 4 + field * 4)[0]
            struct.pack_into('<I', bad, 4 + field * 4, old + 1)
            invalid['field-' + str(field)] = bytes(bad)
        for label, data in invalid.items():
            directory = fixtures / f'{sprite_id}-{label}'
            directory.mkdir()
            for other in IDS + [153]:
                other_name = f'enemy-newsh2-{other}-8.hda'
                if other != sprite_id:
                    (directory / other_name).symlink_to(pack / other_name)
            if data is not None:
                (directory / name).write_bytes(data)
            check(directory, 31 ^ (1 << k), f'{sprite_id}-{label}')
    report = {'status': 'passed', 'baseline': baseline_commit, 'exact_renderer_fragments': 2,
              'all_preexisting_files_checked': len(tracked), 'preexisting_changed_files': changed,
              'old_manifest_restored_exactly': True, 'terrain_registry_capacity': 195,
              'unchanged_old_enemy_bindings': len(trace['baseline']),
              'new_bindings': [{'bank': 1, 'id': i, 'slot': 369 + k} for k, i in enumerate(IDS)],
              'sanitizers': ['address', 'undefined'], 'leak_detection': False,
              'runs': receipts, 'fallback_cases': results,
              'limitations': ['Draw recorder, no rendered pixel/visibility/aesthetic claim.',
                             'No game process or capture; actual full-cycle original-state, native-window and author review pending.',
                             'No Windows compilation or runtime acceptance.']}
    (out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
