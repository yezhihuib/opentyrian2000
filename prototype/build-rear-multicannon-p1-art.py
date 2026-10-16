#!/usr/bin/env python3
"""Verify frozen rear P1 artwork; optionally rerender SVGs with the pinned toolchain.

The ordinary pack builder needs Python/Pillow only. --vector-output additionally
requires the exact Node/Sharp versions recorded by the artwork package and writes
to a new directory, never to accepted resources.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ART = 'assets/hd/artwork/player-rear-multicannon-p1-six-v1'
BINDING = '369ae362f6d8be80b79b56a764973da6bdc3295ccdf3bfa5d00feba66dcda296'
INVENTORY = '85316c9fe27166fa5541d977e55d93fd7436bd9dcf62e68d0334e48fb2cc8a40'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vector-output', type=Path)
    args = parser.parse_args()
    art = ROOT / ART
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(art / 'binding.json') == BINDING
    assert sha(art / 'inventory.json') == INVENTORY
    subprocess.run([sys.executable, str(ROOT / 'tests/test_rear_multi_p1_assets.py')], check=True)
    binding = json.loads((art / 'binding.json').read_text())
    manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    assert len(defaults) == 2
    for entry in binding['resources']:
        source = ('assets/hd/source/' + Path(entry['filename']).stem + '-'
                  + entry['hda_sha256'][:12] + '.png')
        assert (ROOT / source).read_bytes() == (art / entry['png']).read_bytes()
        assert manifest['source_pngs'][entry['hda_sha256']] == {
            'path': source, 'sha256': entry['png_sha256'],
            'RGBA_sha256': entry['rgba_sha256']}
        expected = {'sha256': entry['hda_sha256'],
                    'header_u32': [entry['key'], entry['density'], 12, 14, 0, 0],
                    'source_png': source, 'source_png_sha256': entry['png_sha256']}
        assert set(entry['pack_paths']) == {
            'assets/hd/packs/' + pack + '/' + entry['filename'] for pack in defaults}
        for pack, items in manifest['packs'].items():
            assert items['count'] == len(items['files'])
            if pack in defaults:
                assert items['files'][entry['filename']] == expected
            else:
                assert entry['filename'] not in items['files']
                assert not (ROOT / 'assets/hd/packs' / pack / entry['filename']).exists()
    family = manifest['player_rear_multicannon_p1_six_v1']
    assert family['source'] == ART and family['binding_sha256'] == BINDING
    assert family['inventory_sha256'] == INVENTORY and family['role'] == 131
    assert family['ids'] == [1, 39, 281, 282, 300, 301]
    assert family['densities'] == [4, 8] and family['logical_size'] == [12, 14]
    assert family['anchor'] == [0, 0]
    assert family['entries'] == [
        {'id': e['source_id'], 'density': e['density'], 'HDA_sha256': e['hda_sha256']}
        for e in binding['resources']]
    if args.vector_output:
        output = args.vector_output.resolve()
        if output.exists():
            parser.error('Choose a new vector output directory; existing files are never overwritten')
        subprocess.run(['node', str(art / 'rebuild.cjs'), str(output)], check=True)
        for entry in binding['resources']:
            for key in ('png', 'rgba'):
                assert (output / Path(entry[key]).name).read_bytes() == (art / entry[key]).read_bytes()
    print('PASS: rear P1 R2 frozen vector sources, 12 exact-density payloads, '
          'canonical PNGs, both default packs, rollback exclusions and role131 pins.')


if __name__ == '__main__':
    main()
