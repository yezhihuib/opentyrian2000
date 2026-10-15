#!/usr/bin/env python3
"""Exact finite Sonic63/82 production, artwork and resource scope. No game run."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '2f08b596d7c40fdf45915798d7ec8eef2723d7f3'
ART = 'assets/hd/artwork/player-sonic-shallow-pair-v1'
IDS = (63, 82)
SHA = lambda value: hashlib.sha256(value).hexdigest()
MODIFIED = {'src/render_mirror.c', 'assets/hd/manifest.json', 'prototype/build-hd-assets.py'}
DOCS = ('README.md', 'ART_CHECK.json', 'SOURCE_SCOPE.json', 'BUILD.json',
        'UNITS.json', 'RUNTIME.json', 'AUTHOR_REVIEW.json')


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def replace_once(source, before, after):
    assert source.count(before) == 1, 'Missing/ambiguous exact inverse: ' + before[:100]
    return source.replace(before, after)


def tree():
    result = {}
    for row in git('ls-tree', '-r', '-z', BASE).split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t', 1)
        mode, kind, blob = meta.decode().split()
        assert kind == 'blob' and mode in {'100644', '100755'}, name
        result[name.decode()] = (mode, blob)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    output = parser.parse_args().out.resolve()
    assert not output.exists() and output != ROOT and ROOT not in output.parents and output.parent.is_dir()
    baseline = tree()
    source = (ROOT / 'src/render_mirror.c').read_text()
    helper = ('/* Sonic Wave shallow pair63/82: two normal player heads; other identities stay independent.\n'
              ' * Validate current selected indices AND coverage before EVERY cold/warm lookup. */\n'
              + extract(source, 'sonic_shallow_pair_member') + '\n'
              + extract(source, 'sonic_shallow_pair_source_matches') + '\n')
    binding = ''' /* Sonic Wave shallow pair63/82 only; original/Christmas/diagnostic fallbacks stay classic. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_shallow_pair_member(index)>=0) {
  if((game_probe_density!=4&&game_probe_density!=8)||game_probe_missing||game_probe_invalid||
     game_probe_original_reference||!game_probe_assets||!sonic_shallow_pair_source_matches(bank,index))return NULL;
  slot=549+sonic_shallow_pair_member(index);role=8;
 }
'''
    shadow = ''' /* Sonic Wave shallow pair63/82 retain original indexed shadow silhouettes, origin and order. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_shallow_pair_member(index)>=0&&style==MIRROR_SHADOW)return false;
'''
    restored = source
    for before, after in [('static Asset assets[551];', 'static Asset assets[549];'),
                          (helper, ''), (binding, ''), (shadow, '')]:
        restored = replace_once(restored, before, after)
    assert restored.encode() == git('show', BASE + ':src/render_mirror.c'), 'Unexpected production renderer change'
    production_names = {name for name in baseline if name.startswith('src/')}
    assert len(production_names) == 153
    assert {str(path.relative_to(ROOT)) for path in (ROOT / 'src').rglob('*') if path.is_file()} == production_names
    production = {name: SHA((ROOT / name).read_bytes()) for name in sorted(production_names)}

    manifest_path = ROOT / 'assets/hd/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    reverse = json.loads(manifest_path.read_text())
    family = reverse.pop('player_sonic_shallow_pair_v1')
    assert family['source'] == ART and family['ids'] == list(IDS)
    assert [(entry['id'], entry['slot']) for entry in family['entries']] == [(63, 549), (82, 550)]
    artwork = ROOT / ART
    contract_raw = (artwork / 'contract.json').read_bytes()
    assert SHA(contract_raw) == family['contract_sha256']
    contract = json.loads(contract_raw)
    assert [(entry['id'], entry['slot']) for entry in contract['entries']] == [(63, 549), (82, 550)]
    assert family['entries'] == [{key: entry[key] for key in ('id', 'slot', 'HDA_sha256')}
                                 for entry in contract['entries']]
    master = contract['source']
    assert re.fullmatch(r'sources/generated-sonic63-r[1-9][0-9]*\.png', master), master
    assert SHA((artwork / master).read_bytes()) == contract['source_sha256']
    art_names = {master, 'contract.json', 'rebuild.py', 'README.md'} | {
        f'output/bullet-{identity}-8.{suffix}' for identity in IDS for suffix in ('png', 'hda')}
    assert {str(path.relative_to(artwork)) for path in artwork.rglob('*') if path.is_file()} == art_names
    expected_new = {ART + '/' + name for name in art_names} | {
        'prototype/build-sonic-shallow-pair-art.py',
        'prototype/test-sonic-shallow-pair-scope.py',
        'prototype/test-sonic-shallow-pair-binding.py',
        'prototype/test-sonic-shallow-pair-binding.c',
        'prototype/test-sonic-shallow-pair-shots.c'} | {
        'docs/player-sonic-shallow-pair-v1/' + name for name in DOCS}
    for entry in contract['entries']:
        identity, digest = entry['id'], entry['HDA_sha256']
        canonical = f'assets/hd/source/bullet-{identity}-8-{digest[:12]}.png'
        assert reverse['source_pngs'][digest]['path'] == canonical
        assert (ROOT / canonical).read_bytes() == (artwork / f'output/bullet-{identity}-8.png').read_bytes()
        del reverse['source_pngs'][digest]
        expected_new.add(canonical)

    old_manifest = json.loads(git('show', BASE + ':assets/hd/manifest.json'))
    packs = {}
    for key in ('default_preview_pack', 'default_debug_pack'):
        name = manifest[key]
        assert name == old_manifest[key]
        prefix = 'assets/hd/packs/' + name + '/'
        listed_before = set(old_manifest['packs'][name]['files'])
        listed_after = set(manifest['packs'][name]['files'])
        added = {f'bullet-{identity}-8.hda' for identity in IDS}
        assert old_manifest['packs'][name]['count'] == len(listed_before) == 557
        assert manifest['packs'][name]['count'] == len(listed_after) == 559
        assert listed_after == listed_before | added and not listed_before & added
        physical_before = {path[len(prefix):] for path in baseline if path.startswith(prefix) and path.endswith('.hda')}
        physical_after = {path.name for path in (ROOT / prefix).glob('*.hda')}
        assert len(physical_before) == 563 and len(physical_after) == 565
        assert physical_after == physical_before | added
        unlisted = physical_before - listed_before
        assert len(unlisted) == 6 and physical_after - listed_after == unlisted
        for identity in IDS:
            filename = f'bullet-{identity}-8.hda'
            assert (ROOT / prefix / filename).read_bytes() == (artwork / 'output' / filename).read_bytes()
            del reverse['packs'][name]['files'][filename]
            expected_new.add(prefix + filename)
        reverse['packs'][name]['count'] -= 2
        packs[key] = {'name': name, 'listed_before': 557, 'listed_after': 559,
                      'physical_before': 563, 'physical_after': 565,
                      'unlisted_preserved': 6, 'unlisted_filenames': sorted(unlisted)}
    assert (json.dumps(reverse, indent=2, ensure_ascii=True) + '\n').encode() == git('show', BASE + ':assets/hd/manifest.json'), 'Unrelated manifest change'

    builder = (ROOT / 'prototype/build-hd-assets.py').read_text()
    builder_block = '''sonic_shallow_pair_count=0
if manifest.get('player_sonic_shallow_pair_v1'):
 import subprocess,sys
 subprocess.run([sys.executable,str(repo/'prototype/build-sonic-shallow-pair-art.py')],check=True,capture_output=True,text=True)
 sonic_shallow_pair_count=2
'''
    restored_builder = replace_once(builder, builder_block, '')
    restored_builder = replace_once(restored_builder, "'verified_player_sonic_shallow_pair_members':sonic_shallow_pair_count,", '')
    assert restored_builder.encode() == git('show', BASE + ':prototype/build-hd-assets.py'), 'Unrelated asset-builder change'

    tracked = [row.split('\t') for row in git('diff', '--no-renames', '--name-status', BASE).decode().splitlines()]
    assert all(row[0] in {'M', 'A'} for row in tracked), tracked
    modified = {row[1] for row in tracked if row[0] == 'M'}
    assert modified == MODIFIED, modified
    added = {row[1] for row in tracked if row[0] == 'A'}
    untracked = set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    actual_new = added | untracked
    assert len(expected_new) == 26
    assert actual_new == expected_new, 'Unexpected/missing new files: ' + str(sorted(actual_new ^ expected_new))
    assert len(modified | actual_new) == 29
    for name in actual_new:
        assert name not in baseline and (ROOT / name).is_file() and not (ROOT / name).is_symlink(), name
        assert not any(word in name.lower() for word in ('original', 'private', 'capture', 'reference')), name

    # Hash every baseline blob, not only the renderer/resources most likely to change.
    # This includes the prior Sonic6/44 and73 art, tests, docs, defaults and six
    # physical-but-unlisted resources in each default pack.
    preserved = 0
    for name, (mode, blob) in baseline.items():
        if name in MODIFIED:
            continue
        path = ROOT / name
        assert path.is_file() and not path.is_symlink(), name
        raw = path.read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blob, name
        assert bool(path.stat().st_mode & 0o111) == (mode == '100755'), 'Mode changed: ' + name
        preserved += 1
    report = {'status': 'PASS', 'baseline': BASE,
              'production_tracked_src_files_checked': 153,
              'production_code_files_checked': sum(Path(name).suffix in {'.c', '.h', '.inc'} for name in production_names),
              'only_production_file_changed': 'src/render_mirror.c',
              'renderer_sha256': SHA(source.encode()), 'exact_production_inverse': True,
              'manifest_exact_byte_inverse': True, 'asset_builder_exact_byte_inverse': True,
              'baseline_files_preserved_byte_exact': preserved,
              'prior_sonic6_44_and73_art_tests_docs_and_bindings_unchanged': True,
              'remaining_original_family_ids': 16, 'modified_files': sorted(modified),
              'new_files': sorted(actual_new), 'overlay_paths': sorted(modified | actual_new),
              'overlay_path_count': 29, 'modified_path_count': 3, 'new_path_count': 26,
              'packs': packs, 'frozen_art_contract_sha256': SHA(contract_raw),
              'source_sha256': production, 'game_runs': 0,
              'scope': 'Normal player63/82 only. Existing6/44/73, other16 Sonic identities, original shots/shadows/indexed blitters/gameplay/RNG preserved. Runtime/visual acceptance separate.'}
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS exact29-path overlay:3modified26new;153 production src, renderer/manifest/builder inverse; prior6/44/73 exact; defaults557to559, six unlisted retained')


if __name__ == '__main__':
    main()
