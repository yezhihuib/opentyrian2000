#!/usr/bin/env python3
"""Verify/rebuild frozen normal-player Vulcan art. Does not run the game."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
from PIL import Image

IDS = [67, 70]
SOURCE = 'assets/hd/artwork/player-vulcan-two-v1'
INVENTORY_SHA = '2099589202e779b0b41c7fed9f50bb71a5f99f84c8eabd79c580f3214ee2e460'
sha = lambda data: hashlib.sha256(data).hexdigest()


def read(path):
    assert path.is_file() and not path.is_symlink(), str(path)
    return path.read_bytes()


def validate(repo):
    source = repo / SOURCE
    inventory_raw = read(source / 'inventory.json')
    assert sha(inventory_raw) == INVENTORY_SHA
    inventory = json.loads(inventory_raw)
    assert [row['id'] for row in inventory['outputs']] == IDS
    for name, digest in inventory['inputs'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(read(source / name)) == digest, name
    manifest = json.loads(read(repo / 'assets/hd/manifest.json'))
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    entries, total_fractional = [], 0
    for slot, row in enumerate(inventory['outputs'], 522):
        index = row['id']; stem = f'bullet-{index}-8'
        raw = read(source / 'output' / (stem + '.hda'))
        png = read(source / 'output' / (stem + '.png'))
        header = [80000 + index, 8, 12, 14, 0, 0]
        assert len(raw) == 43036 and raw[:28] == b'HDR1' + struct.pack('<6I', *header)
        assert sha(raw) == row['HDA_SHA256'] and sha(raw[28:]) == row['RGBA_SHA256']
        assert sha(png) == row['PNG_SHA256']
        with Image.open(source / 'output' / (stem + '.png')) as image:
            assert image.mode == 'RGBA' and image.size == (96, 112) and image.tobytes() == raw[28:]
        alpha = raw[31::4]
        fractional = sum(0 < a < 255 for a in alpha)
        assert fractional == row['fractional_samples'] and fractional > 0 and any(alpha)
        xs = [i % 96 for i, a in enumerate(alpha) if a]
        ys = [i // 96 for i, a in enumerate(alpha) if a]
        assert [min(xs), min(ys), max(xs)+1, max(ys)+1] == row['bbox']
        total_fractional += fractional
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
        entries.append({'id': index, 'slot': slot, 'HDA_sha256': digest})
    assert manifest['player_vulcan_two_v1'] == {
        'source': SOURCE, 'inventory_sha256': INVENTORY_SHA, 'role': 8, 'density': 8,
        'logical_size': [12, 14], 'anchor': [0, 0], 'ids': IDS,
        'scope': 'normal-data player TILE heads; shared options 1/30 and rear15 charge0/1; Christmas, indexed shadows, enemy and direct menu routes unchanged',
        'fallback': 'independent per-head existing player loader; existing 8-to4 fallback', 'entries': entries}
    return {'status': 'PASS', 'members': 2, 'bindings': 4, 'fractional_alpha_samples': total_fractional,
            'inventory_sha256': INVENTORY_SHA, 'game_runs': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    result = validate(repo)
    if args.output:
        destination = args.output.absolute()
        assert not destination.exists() and not any(p.is_symlink() for p in [destination, *destination.parents])
        assert repo != destination and repo not in destination.parents and destination not in repo.parents
        subprocess.run(['node', str(repo / SOURCE / 'rebuild.cjs'), str(destination)], check=True)
    else:
        with tempfile.TemporaryDirectory(prefix='vulcan-art-rebuild-') as temporary:
            subprocess.run(['node', str(repo / SOURCE / 'rebuild.cjs'), str(Path(temporary) / 'output')], check=True)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
