#!/usr/bin/env python3
"""Complete-file boss-body preservation against published 5629b3d. No game run."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET

BASE = '5629b3dda05b2aa77af3c624841320d05c0f7130'
TREE = '38bb894192f1f763784df9e43c54543e161d51e3'
ALLOWED = {'src/render_mirror.c', 'assets/hd/manifest.json', 'prototype/build-hd-assets.py', 'prototype/build-newsh4-entry6-art.py'}
sha = lambda b: hashlib.sha256(b).hexdigest()
sys.dont_write_bytecode = True


def require(condition, message):
    if not condition:
        raise ValueError(message)


def revision_preservation(repo, boss, git):
    """V2 may replace only the finite body binding, preserving the V1 audit."""
    revision = 'dc9e706192dea9e35f529544ca47d757d908c1d7'
    prior = lambda name: git('show',revision+':'+name)
    old = json.loads(prior('assets/hd/manifest.json'))
    current = boss.load(repo/'assets/hd/manifest.json')
    before_family = old['boss_whole_family_v1']
    after_family = current[boss.FAMILY]
    require([e['id'] for e in before_family['entries']] == [e['id'] for e in after_family['entries']] == boss.IDS,
            'revision member scope changed')
    allowed_assets = {old['source_pngs'][e['HDA_sha256']]['path'] for e in before_family['entries']}
    allowed_assets.update(f'assets/hd/packs/{pack}/enemy-newsh4-{base}-8.hda' for pack in boss.DEFAULTS for base in boss.IDS)
    allowed_code = {'src/render_mirror.c','assets/hd/manifest.json','prototype/build-boss-whole-family-art.py',
        'prototype/build-hd-assets.py','prototype/build-newsh4-entry6-art.py',
        'prototype/test-boss-whole-family-source-guards.py','prototype/test-boss-whole-family-preservation.py',
        'prototype/test-boss-whole-family-pixels.py','prototype/test-boss-whole-family-pixels.c',
        'prototype/test-boss-whole-family-binding.py','prototype/test-boss-whole-family-binding.c',
        'prototype/README-boss-whole-family.md'}
    count, asset_bytes, historical_files, changed = 0, 0, 0, []
    for row in git('ls-tree','-rz',revision).split(b'\0'):
        if not row: continue
        metadata,name = row.split(b'\t',1)
        mode,kind,blob = metadata.decode().split();name=name.decode();path=repo/name
        require(kind=='blob' and mode in ['100644','100755'],'unexpected revision tree type')
        count+=1
        if not path.exists():
            require(name in allowed_assets and name.startswith('assets/hd/source/'),'unexpected deleted prior file: '+name)
            changed.append(name);continue
        raw=boss.read_regular(path)
        require(('100755' if stat.S_IMODE(path.stat().st_mode)&0o111 else '100644')==mode,'revision file mode changed: '+name)
        identical=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob
        if not identical:
            changed.append(name)
            require(name in allowed_assets|allowed_code,'unapproved V2 revision file: '+name)
        elif name.startswith('assets/'):
            asset_bytes+=len(raw)
        if name.startswith('assets/hd/artwork/boss-whole-family-v1/') or name.startswith('docs/boss-whole-family/'):
            require(identical,'historical V1 artwork/proof changed: '+name)
            historical_files+=1
    renderer=(repo/'src/render_mirror.c').read_text()
    stamps=lambda family: 'static const uint64_t rgba_stamps[40]={'+','.join('UINT64_C(0x'+e['RGBA_FNV1a64']+')' for e in family['entries'])+'};'
    require(renderer.count(stamps(after_family))==1,'revision stamp array mismatch')
    restored=renderer.replace(stamps(after_family),stamps(before_family),1).replace(
        'The V2 stamps pin inward-only authored alpha and byte-exact V1 RGB.',
        'The complete frozen RGBA stamps include exact source alpha and matte bytes.')
    require(restored.encode()==prior('src/render_mirror.c'),'V2 renderer changed beyond stamps/comment')
    projected=json.loads(json.dumps(current))
    projected={('boss_whole_family_v1' if k==boss.FAMILY else k):(before_family if k==boss.FAMILY else v) for k,v in projected.items()}
    for pack in boss.DEFAULTS:
        for base in boss.IDS:
            name=f'enemy-newsh4-{base}-8.hda'
            projected['packs'][pack]['files'][name]=old['packs'][pack]['files'][name]
    for entry in after_family['entries']: del projected['source_pngs'][entry['HDA_sha256']]
    # Preserve prior ordering as well as content when projecting body bindings.
    projected['source_pngs']={digest:(old['source_pngs'][digest] if digest in {e['HDA_sha256'] for e in before_family['entries']} else projected['source_pngs'][digest]) for digest in old['source_pngs']}
    require((json.dumps(projected,indent=2)+'\n').encode()==prior('assets/hd/manifest.json'),'V2 manifest changed outside finite body')
    for name in ['prototype/build-hd-assets.py','prototype/build-newsh4-entry6-art.py']:
        require((repo/name).read_text().replace(boss.FAMILY,'boss_whole_family_v1').encode()==prior(name),
                'revision hook changed beyond family key: '+name)
    return {'prior_revision':revision,'prior_files_checked':count,'changed_files':changed,
            'unchanged_asset_bytes':asset_bytes,'historical_V1_artwork_and_receipt_files_preserved':historical_files,
            'renderer_only_forty_stamps_and_comment':True,'manifest_only_finite_body':True,
            'prior_V1_runtime_receipts':'Historical; not V2 acceptance'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('boss_art', repo / 'prototype/build-boss-whole-family-art.py')
    boss = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(boss)
    out = boss.safe_output(args.out, repo)
    git = lambda *args: subprocess.check_output(['git','-C',str(repo),*args])
    require(git('rev-parse',BASE).decode().strip() == BASE and
            git('rev-parse',BASE + '^{tree}').decode().strip() == TREE, 'baseline commit/tree identity mismatch')
    baseline = lambda name: git('show',BASE + ':' + name)
    renderer = boss.read_regular(repo / 'src/render_mirror.c')
    restored = renderer.decode()
    require(restored.count('static Asset assets[462];') == 1, 'finite462 asset array required')
    restored = restored.replace('static Asset assets[462];','static Asset assets[422];')
    for first, last in [
        ('/* Approved whole-boss bank2 family:', 'bool render_mirror_enemy_tile('),
        (' /* Whole boss remains twenty original actors with four ordered calls each.', ' /* Entry craft remains'),
    ]:
        require(restored.count(first) == restored.count(last) == 1, 'renderer restoration marker mismatch')
        start, end = restored.index(first), restored.index(last,restored.index(first))
        restored = restored[:start] + restored[end:]
    require(restored.encode() == baseline('src/render_mirror.c'), 'renderer does not restore exact published baseline')
    manifest = boss.load(repo / 'assets/hd/manifest.json')
    family = manifest[boss.FAMILY]
    projected = json.loads(json.dumps(manifest))
    del projected[boss.FAMILY]
    for pack_name in boss.DEFAULTS:
        pack = projected['packs'][pack_name]
        for base in boss.IDS:
            del pack['files'][f'enemy-newsh4-{base}-8.hda']
        pack['count'] -= 40
    for entry in family['entries']:
        del projected['source_pngs'][entry['HDA_sha256']]
    require(projected == json.loads(baseline('assets/hd/manifest.json')), 'prior manifest semantics changed')
    require((json.dumps(projected,indent=2)+'\n').encode() == baseline('assets/hd/manifest.json'),
            'manifest cannot restore byte-exact baseline formatting/order')
    entry_source = boss.read_regular(repo / 'prototype/build-newsh4-entry6-art.py').decode()
    first, last = '# BEGIN validated boss full-composite coexistence\n', '# END validated boss full-composite coexistence\n\n\n'
    require(entry_source.count(first) == entry_source.count(last) == 1, 'entry coexistence markers mismatch')
    start = entry_source.index(first)
    end = entry_source.index(last,start) + len(last)
    entry_restored = entry_source[:start] + entry_source[end:]
    inverse = [
        ('    boss_hashes, boss_packed, boss_canonical = validated_boss_full_composites(repo, manifest)\n',''),
        ('            if digest not in boss_hashes:\n                indexed_family.add(digest)', '            indexed_family.add(digest)'),
        ("                    if (family_name(name) or entry['header_u32'][0] in KEYS)\n                    and f'{pack_name}/{name}' not in boss_packed}",
         "                    if family_name(name) or entry['header_u32'][0] in KEYS}"),
        ('        if (family_name(path.name) or key_matches) and path.relative_to(pack_root).as_posix() not in boss_packed:',
         '        if family_name(path.name) or key_matches:'),
        ('        if match and int(match[1]) in TILES and path.relative_to(repo).as_posix() not in boss_canonical:',
         '        if match and int(match[1]) in TILES:'),
    ]
    for before, after in inverse:
        require(entry_restored.count(before) == 1, 'entry coexistence inverse mismatch')
        entry_restored = entry_restored.replace(before,after,1)
    require(entry_restored.encode() == baseline('prototype/build-newsh4-entry6-art.py'),
            'entry validator does not restore exact published baseline')
    aggregate = boss.read_regular(repo / 'prototype/build-hd-assets.py').decode()
    first, last = 'boss_whole_count=0\n', 'print(json.dumps('
    require(aggregate.count(first) == 1, 'aggregate boss hook missing')
    start, end = aggregate.index(first), aggregate.index(last,aggregate.index(first))
    aggregate_restored = aggregate[:start] + aggregate[end:]
    fields = "'verified_boss_whole_family_members':boss_whole_count,'verified_boss_intentional_empty_members':3 if boss_whole_count else 0,"
    require(aggregate_restored.count(fields) == 1, 'aggregate boss counters mismatch')
    aggregate_restored = aggregate_restored.replace(fields,'',1)
    require(aggregate_restored.encode() == baseline('prototype/build-hd-assets.py'),
            'aggregate validator does not restore exact published baseline')
    changed, count, asset_bytes = [], 0, 0
    sensitive = {}
    for row in git('ls-tree','-rz',BASE).split(b'\0'):
        if not row:
            continue
        meta, name = row.split(b'\t',1)
        mode, kind, blob = meta.decode().split()
        name = name.decode()
        path = repo / name
        require(kind == 'blob' and mode in ['100644','100755'], 'unexpected baseline tree type: ' + name)
        raw = boss.read_regular(path)
        actual_mode = '100755' if stat.S_IMODE(path.stat().st_mode) & 0o111 else '100644'
        require(actual_mode == mode, 'prior file mode changed: ' + name)
        identical = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blob
        count += 1
        if not identical:
            changed.append(name)
        elif name.startswith('assets/'):
            asset_bytes += len(raw)
        if name in ['src/tyrian2.c','src/mainint.c','src/varz.c','src/entity_draw.c','src/sprite.c','src/episodes.c']:
            require(identical, 'gameplay/source file changed: ' + name)
            sensitive[name] = sha(raw)
    require(set(changed) <= ALLOWED and {'src/render_mirror.c','assets/hd/manifest.json'} <= set(changed),
            'unexpected existing-file diff: ' + repr(changed))
    # The exact renderer inverse proves all prior body, player/enemy shot, effects,
    # world-material, bossbar/HUD paths and their original ordered calls unchanged.
    # Check the project source list as metadata only; no Windows build is implied.
    project = repo / 'visualc/opentyrian.vcxproj'
    require(project.read_bytes() == baseline('visualc/opentyrian.vcxproj'), 'Windows XML changed')
    xml = ET.parse(project)
    ns = {'m':'http://schemas.microsoft.com/developer/msbuild/2003'}
    items = [x.attrib['Include'] for x in xml.findall('.//m:ClCompile',ns) if 'Include' in x.attrib]
    require(len(items) == len(set(items)) and {Path(x.replace('\\','/')).name for x in items} ==
            {x.name for x in (repo/'src').glob('*.c')}, 'Windows source inventory mismatch')
    require(all((project.parent/item.replace('\\','/')).is_file() for item in items), 'Windows source path missing')
    revision = revision_preservation(repo,boss,git)
    source_validation = boss.validate(repo)
    report = {'status':'PASS', 'V2_revision_preservation':revision, 'baseline_commit':BASE, 'baseline_tree':TREE,
              'previous_files_checked':count, 'previous_changed_files':changed,
              'prior_file_modes_unchanged':True, 'prior_asset_bytes_identical':asset_bytes,
              'renderer_sha256':sha(renderer), 'renderer_restores_exact_published_baseline':True,
              'manifest_restores_exact_published_baseline':True,
              'entry_validator_restores_exact_published_baseline':True,
              'aggregate_validator_restores_exact_published_baseline':True, 'gameplay_files_unchanged':sensitive,
              'prior_families_orbs_effects_weapon81_and_bossbar_source_preserved':True,
              'finite_body_source_validation':source_validation,
              'Windows':'XML preservation only; no compile/runtime claim',
              'game_runs':0, 'captures':0, 'native_output':False}
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc),file=sys.stderr)
        sys.exit(1)
