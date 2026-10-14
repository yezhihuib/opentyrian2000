#!/usr/bin/env python3
"""Verify/rebuild frozen independent Protron shadow coverage. Never runs the game."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from PIL import Image

IDS = [225, 244, 226]
SOURCE = 'assets/hd/artwork/player-protron-shadow-three-v1'
INVENTORY_SHA = '66bdfa62d95199106445ea74ac0756b69de27276f3d57ea6efeef942238f8946'
sha = lambda data: hashlib.sha256(data).hexdigest()


def read(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    return path.read_bytes()


def fnv(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'{value:016x}'


def validate(repo):
    source = repo / SOURCE
    inventory_raw = read(source / 'inventory.json')
    assert sha(inventory_raw) == INVENTORY_SHA
    inventory = json.loads(inventory_raw)
    assert [row['id'] for row in inventory['outputs']] == IDS
    assert inventory['original_game_pixel_inputs'] == inventory['head_asset_edits'] == 0
    for name, digest in inventory['inputs'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(read(source / name)) == digest, name
    manifest = json.loads(read(repo / 'assets/hd/manifest.json'))
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    entries, coverage_counts = [], []
    for slot, row in enumerate(inventory['outputs'], 532):
        index = row['id']; stem = f'protron-shadow-{index}-8'
        raw = read(source / 'output' / (stem + '.hda'))
        png = read(source / 'output' / (stem + '.png'))
        header = [1250000 + index, 8, 12, 14, 0, 0]
        assert len(raw) == 43036 and raw[:28] == b'HDR1' + struct.pack('<6I', *header)
        assert sha(raw) == row['HDA_SHA256'] and sha(raw[28:]) == row['RGBA_SHA256']
        assert sha(png) == row['PNG_SHA256'] and fnv(raw[28:]) == row['RGBA_FNV1a64']
        with Image.open(source / 'output' / (stem + '.png')) as image:
            assert image.mode == 'RGBA' and image.size == (96, 112) and image.tobytes() == raw[28:]
        alpha = raw[31::4]
        assert alpha == read(source / 'output' / (stem + '.coverage.bin'))
        assert sha(alpha) == row['COVERAGE_SHA256'] and fnv(alpha) == row['COVERAGE_FNV1a64']
        assert set(raw[28::4]) == set(raw[29::4]) == set(raw[30::4]) == {255}, 'Frozen unused RGB changed'
        counts = [sum(a == 0 for a in alpha), sum(0 < a < 255 for a in alpha), sum(a == 255 for a in alpha)]
        assert all(counts), 'Need exterior, vector boundary AA and full-strength core'
        coverage_counts.append({'id': index, 'zero_partial_full': counts})
        digest = sha(raw); canonical = f'assets/hd/source/{stem}-{digest[:12]}.png'
        assert read(repo / canonical) == png
        assert manifest['source_pngs'][digest] == {'path': canonical, 'sha256': sha(png), 'RGBA_sha256': sha(raw[28:])}
        item = {'header_u32': header, 'sha256': digest, 'source_png': canonical, 'source_png_sha256': sha(png)}
        for pack, content in manifest['packs'].items():
            assert content['count'] == len(content['files'])
            if pack in defaults:
                assert content['files'][stem + '.hda'] == item
                assert read(repo / 'assets/hd/packs' / pack / (stem + '.hda')) == raw
            else:
                assert stem + '.hda' not in content['files']
        entries.append({'id': index, 'slot': slot, 'HDA_sha256': digest, 'RGBA_FNV1a64': row['RGBA_FNV1a64']})
    assert manifest['player_protron_shadow_three_v1'] == {
        'source': SOURCE, 'inventory_sha256': INVENTORY_SHA, 'role': 125, 'density': 8,
        'logical_size': [12, 14], 'anchor': [0, 0], 'ids': IDS,
        'scope': 'normal-data player TILE shadows only; independent geometric coverage; original indexed writes and all head resources unchanged',
        'coverage': 'frozen alpha only; stored white RGB is unused; full-strength existing shadow operator followed by exact coverage blend',
        'fallback': 'independent per-mask density8 only; missing/invalid mask declines only shadow; unchanged heads retain existing 8-to4 fallback',
        'entries': entries}
    return {'status': 'PASS', 'members': 3, 'bindings': 6, 'coverage_counts': coverage_counts,
            'inventory_sha256': INVENTORY_SHA, 'game_runs': 0, 'head_resources_modified': 0}


def rebuild(repo, destination):
    source = repo / SOURCE
    assert not destination.exists() and not any(p.is_symlink() for p in [destination, *destination.parents])
    assert repo != destination and repo not in destination.parents and destination not in repo.parents
    shutil.copytree(source, destination)
    subprocess.run(['node', str(destination / 'rebuild.mjs')], check=True, capture_output=True, text=True)
    checked = []
    for path in sorted(source.rglob('*')):
        if path.is_file():
            relative = path.relative_to(source)
            assert read(destination / relative) == read(path), str(relative)
            checked.append(str(relative))
    assert {str(p.relative_to(destination)) for p in destination.rglob('*') if p.is_file()} == set(checked)
    return len(checked)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New external directory for the complete relocated package')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    result = validate(repo)
    if args.output:
        result['relocated_files_exact'] = rebuild(repo, args.output.absolute())
    else:
        with tempfile.TemporaryDirectory(prefix='protron-shadow-art-check-') as temporary:
            result['relocated_files_exact'] = rebuild(repo, Path(temporary) / 'rebuilt')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
