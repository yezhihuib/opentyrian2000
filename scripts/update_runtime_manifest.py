#!/usr/bin/env python3
"""Refresh the explicit runtime allowlist from a complete, pinned public tree.

No network requests, source moves or deletions. Requires a supplied GitHub
recursive-tree JSON; it does not inspect test fixtures or development artwork.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PUBLIC_REVISION = 'fedc541cc6b6e93f7748a85e6c40318b6ca9f5a8'


def local_row(root, source, destination, group):
    path = root / source
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError('Missing, linked, or oversized selected source: ' + source)
    data = path.read_bytes()
    return {'source_path': source, 'destination': destination, 'group': group, 'bytes': len(data), 'git_blob': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(), 'sha256': hashlib.sha256(data).hexdigest(), 'revision': 'local-reviewed-source'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-tree', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, help='Defaults to SOURCE_ROOT/packaging/runtime-assets-v1.json')
    args = parser.parse_args()
    root = args.source_root.resolve()
    selection = json.loads((root / 'packaging/runtime-selection-v1.json').read_text())
    tree = json.loads(args.public_tree.read_text())
    if tree.get('truncated') is not False or tree.get('sha') != PUBLIC_REVISION:
        raise ValueError('Expected complete recursive tree for pinned public revision ' + PUBLIC_REVISION)
    blobs = {row['path']: row for row in tree['tree'] if row['type'] == 'blob'}
    rows = []
    for kind in ('gameplay', 'startup'):
        prefix = selection[kind + '_pack'] + '/'
        group = [row for path, row in blobs.items() if path.startswith(prefix)]
        if len(group) != (637 if kind == 'gameplay' else 9):
            raise ValueError('Selected public pack inventory changed; review closure before refresh')
        for row in group:
            rows.append({'source_path': row['path'], 'destination': selection[kind + '_destination'] + '/' + row['path'][len(prefix):], 'group': kind, 'bytes': row['size'], 'git_blob': row['sha'], 'revision': PUBLIC_REVISION})
    shop_count = 0
    for directory in selection['shop_runtime_directories']:
        paths = sorted((root / directory).glob('*.hda'))
        if not paths:
            raise ValueError('Missing selected shop runtime directory: ' + directory)
        for path in paths:
            source = path.relative_to(root).as_posix()
            row = local_row(root, source, 'assets/startup/' + path.name, 'shop')
            if source in blobs:
                if row['bytes'] != blobs[source]['size'] or row['git_blob'] != blobs[source]['sha']:
                    raise ValueError('Published shop resource changed; review before refresh: ' + source)
                row['revision'] = PUBLIC_REVISION
            rows.append(row)
            shop_count += 1
    if shop_count != 11:
        raise ValueError('Expected all eleven current shop runtime resources')
    notices = ['COPYING', 'assets/shop-menu-font-v1/LICENSE-DejaVu.txt', 'assets/shop-menu-font-v1/FONT-PROVENANCE.txt', 'src/third_party/dr_mp3-LICENSE', 'src/third_party/dr_mp3-PROVENANCE.md']
    for source in notices:
        rows.append(local_row(root, source, 'licenses/' + Path(source).name, 'notice'))
    for source, destination in [('packaging/start-hd.sh', 'start-hd.sh'), ('packaging/start-hd.ps1', 'start-hd.ps1'), ('packaging/runtime-README.txt', 'README.txt')]:
        rows.append(local_row(root, source, destination, 'launcher-and-config'))
    manifest = {'schema': 'opentyrian-runtime-package-v1', 'source_revision': {'public_assets': PUBLIC_REVISION, 'generator_integration': '55d418de4f914d4694eb7f074458207b1cf6a2d2', 'packaging': 'local working source; artifact rows pin exact SHA256'}, 'closure': {'gameplay_files': 637, 'startup_files': 9, 'shop_files': 11, 'fonts': ['settings-font-large-v1.hda', 'settings-font-medium-v1.hda', 'settings-font-tiny-v1.hda', 'title-menu-font-v1.hda'], 'shared_startup_directory': True, 'all_active_pack_files_and_fallbacks_retained': True}, 'external_dependencies': {'original_game_data': 'Complete separately obtained Tyrian 2000 data; no game data or save files are bundled.', 'linux': 'Compatible SDL2, SDL2_net and system C/math runtime; dynamic library resolution must be checked on the target.', 'windows': 'Matching-architecture prebuilt EXE, SDL2.dll, SDL2_net.dll and their license notices from official SDL distributions. Windows runtime acceptance remains separate.', 'optional_music': 'User-supplied music stays external; --music-dir is optional.', 'python_and_pillow': 'Needed only for development/rebuilding, not for the compiled game runtime.'}, 'excluded': selection['preserve_in_development_only'], 'files': sorted(rows, key=lambda row: row['destination'])}
    destinations = [row['destination'] for row in rows]
    if len(destinations) != len(set(destinations)):
        raise ValueError('Destination collision')
    output = args.output or root / 'packaging/runtime-assets-v1.json'
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'files': len(rows), 'payload_bytes': sum(row['bytes'] for row in rows), 'output': str(output)}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print('Manifest refresh refused: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
