#!/usr/bin/env python3
"""Prove the bounded six-member append preserves the local baseline.

Reads every previously tracked file. Does not run the game, mutate old files,
restore Git state, or imply Windows compilation/runtime acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import json
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET

BASELINE = 'fe5f5d7922105dccf67bfe2648ac366c3031bc66'
ALLOWED = {'src/render_mirror.c', 'assets/hd/manifest.json', 'prototype/build-hd-assets.py',
           'prototype/tests/startup-manufacturer/test_package.py',
           'prototype/tests/title-package/test_package.py'}
IDS = [81, 83, 85, 119, 121, 123]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--baseline', default=BASELINE)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    given = args.out.expanduser()
    require(given.is_absolute(), 'absolute external report required')
    require(not any(p.is_symlink() for p in [given, *given.parents]), 'report symlinks forbidden')
    out = given.resolve()
    require(not out.exists() and out.parent.is_dir(), 'fresh report with existing parent required')
    require(out != repo and out not in repo.parents and repo not in out.parents, 'external report required')

    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])

    require(git('rev-parse', args.baseline + '^{commit}').decode().strip() == BASELINE,
            'baseline must resolve to the approved local commit')
    previous_renderer = git('show', BASELINE + ':src/render_mirror.c')
    current = (repo / 'src/render_mirror.c').read_text()
    require(current.count('static Asset assets[416];') == 1, 'finite renderer capacity')
    restored_renderer = current.replace('static Asset assets[416];', 'static Asset assets[410];')
    for start_marker, end_marker in [
        ('/* Approved newsh4 entry six-member bank2 family,', 'bool render_mirror_enemy_tile('),
        ('  /* Entry craft remains six independent source actors with ordered overlap.',
         '\n }\n if(role==ASSET_NEWSHE)'),
    ]:
        require(restored_renderer.count(start_marker) == 1, 'unique renderer append marker')
        start = restored_renderer.index(start_marker)
        end = restored_renderer.index(end_marker, start)
        restored_renderer = restored_renderer[:start] + restored_renderer[end:]
        if start_marker.startswith('  /* Entry craft'):
            restored_renderer = restored_renderer[:start-1] + restored_renderer[start:]
    require(restored_renderer.encode() == previous_renderer, 'nonfinite renderer delta')
    changed, checked, previous_asset_bytes = [], 0, 0
    # NUL-separated names preserve literal paths. Verify Git mode as well as blob bytes.
    for line in git('ls-tree', '-rz', BASELINE).split(b'\0'):
        if not line:
            continue
        metadata, encoded_name = line.split(b'\t', 1)
        mode, kind, blob = metadata.decode().split()
        name = encoded_name.decode()
        require(kind == 'blob' and mode in ['100644', '100755'], 'unexpected baseline file kind: ' + name)
        path = repo / name
        require(path.is_file() and not path.is_symlink(), 'prior file missing or replaced by symlink: ' + name)
        require(not any(parent.is_symlink() for parent in path.parents), 'prior directory symlink: ' + name)
        actual_mode = '100755' if stat.S_IMODE(path.stat().st_mode) & 0o111 else '100644'
        require(actual_mode == mode, 'prior executable mode changed: ' + name)
        raw = path.read_bytes()
        actual_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        checked += 1
        if actual_blob != blob:
            changed.append(name)
        elif name.startswith('assets/'):
            previous_asset_bytes += len(raw)
    require(set(changed) == ALLOWED, 'previous-file changes outside exact allowance: ' + repr(changed))
    manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
    previous_bytes = git('show', BASELINE + ':assets/hd/manifest.json')
    previous_manifest = json.loads(previous_bytes)
    restored = json.loads(json.dumps(manifest))
    family = restored.pop('newsh4_entry6_v1')
    require(family['ids'] == IDS and family['slots'] == list(range(410, 416))
            and [entry['id'] for entry in family['entries']] == IDS, 'exact appended family required')
    defaults = [restored['default_preview_pack'], restored['default_debug_pack']]
    require(defaults == [previous_manifest['default_preview_pack'], previous_manifest['default_debug_pack']]
            and len(set(defaults)) == 2, 'default pack identity changed')
    removed_hashes = set()
    for base in IDS:
        name = f'enemy-newsh4-{base}-8.hda'
        hashes = set()
        for pack_name in defaults:
            pack = restored['packs'][pack_name]
            require(name not in previous_manifest['packs'][pack_name]['files'], 'append overwrote prior member')
            entry = pack['files'].pop(name)
            pack['count'] -= 1
            hashes.add(entry['sha256'])
        require(len(hashes) == 1, 'default packs disagree on appended bytes')
        digest = hashes.pop()
        require(digest not in previous_manifest['source_pngs'] and digest not in removed_hashes,
                'append reused prior or duplicate source index')
        removed_hashes.add(digest)
        restored['source_pngs'].pop(digest)
    require(restored == previous_manifest, 'previous manifest semantics changed')
    require((json.dumps(restored, indent=2) + '\n').encode() == previous_bytes,
            'previous manifest does not restore byte-exactly')
    project = repo / 'visualc/opentyrian.vcxproj'
    xml = ET.parse(project)
    ns = {'m': 'http://schemas.microsoft.com/developer/msbuild/2003'}
    items = [node.attrib['Include'] for node in xml.findall('.//m:ClCompile', ns) if 'Include' in node.attrib]
    require('..\\src\\render_mirror.c' in items, 'Windows renderer translation unit missing')
    for name in items:
        require((project.parent / name.replace('\\', '/')).is_file(), 'Windows compile reference missing: ' + name)
    require(project.read_bytes() == git('show', BASELINE + ':visualc/opentyrian.vcxproj')
            and len(items) == len(set(items))
            and {Path(name.replace('\\', '/')).name for name in items}
            == {path.name for path in (repo / 'src').glob('*.c')}, 'Windows project preservation mismatch')
    require('terrain_sources[199]' in current and 'terrain_source_count<199' in current,
            'prior terrain registry changed')
    report = {
        'status': 'PASS', 'baseline': BASELINE,
        'renderer_reverts_exactly_after_finite_family_removal': True,
        'all_prior_family_caches_and_routes_unchanged': True,
        'previous_tracked_files_checked': checked, 'previous_changed_files': changed,
        'prior_file_modes_unchanged': True,
        'previous_asset_payload_bytes_identical': previous_asset_bytes,
        'previous_manifest_restored_exactly': True, 'all_gameplay_startup_sources_unchanged': True,
        'Windows_project_XML': 'parsed; all compile references exist; unchanged existing renderer unit listed',
        'Windows_compilation_runtime': False, 'game_runs': 0,
        'render_source_sha256': hashlib.sha256(current.encode()).hexdigest(),
        'default_pack_counts': [manifest['packs'][name]['count'] for name in defaults],
    }
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, ET.ParseError, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
