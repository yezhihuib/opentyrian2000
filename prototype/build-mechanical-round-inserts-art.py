#!/usr/bin/env python3
"""Rebuild/audit the two independently generated static Layer3 round inserts.

Original game data is optional for source-index/opacity audit, never an artwork
rebuild dependency. Output must be a fresh directory outside the repository.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from PIL import Image

IDS = [190, 200]
SLOTS = [367, 368]
sha = lambda data: hashlib.sha256(data).hexdigest()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--original-data', type=Path, help='Optional local shapesz.dat; never bundled')
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
source = repo / 'assets/hd/artwork/mechanical-round-inserts-v1'
given = a.output.absolute()
out = given.resolve()
if (any(q.is_symlink() for q in [given, *given.parents]) or out.exists()
        or out == repo or repo in out.parents or out in repo.parents):
    p.error('Choose a fresh directory outside the repository, without symlink path components')
manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
family = manifest['terrain_layer3_mechanical_round_inserts_v1']
assert family['ids'] == IDS and family['slots'] == SLOTS
assert family['layer'] == 3 and family['style'] == 'NORMAL' and family['density'] == 8
assert family['logical_size'] == [24, 28] and family['anchor'] == [0, 0]
assert family['source'] == 'assets/hd/artwork/mechanical-round-inserts-v1'
assert sha((source / 'inventory.json').read_bytes()) == family['source_inventory_sha256']
imported = json.loads((source / 'IMPORT.json').read_text())
assert imported['source_inventory_sha256'] == family['source_inventory_sha256']
assert {e['path'] for e in imported['files']} == {
    str(f.relative_to(source)) for f in source.rglob('*') if f.is_file() and f.name != 'IMPORT.json'
}
for entry in imported['files']:
    assert sha((source / entry['path']).read_bytes()) == entry['sha256'], entry['path']
inventory = json.loads((source / 'inventory.json').read_text())
contract = json.loads((source / 'contract.json').read_text())
assert contract['output_ids'] == IDS and contract['layer'] == 3 and contract['mode'] == 'NORMAL'
assert [e['source_id'] for e in contract['entries']] == IDS
for e in contract['entries']:
    assert e['hda_id'] == 2010000 + e['source_id'] and e['logical_size'] == [24, 28]
    assert e['density'] == 8 and e['anchor'] == [0, 0]
    assert e['registered_master_size'] == [576, 672] and e['crop'] == [192, 224, 384, 448]
guards = json.loads((source / 'proof/unchanged-guards.json').read_text())
for entry in guards['guards']:
    assert sha((repo / entry['source_png']).read_bytes()) == entry['sha256'], entry['id']
proof = json.loads((source / 'proof/source-proof.json').read_text())
assert proof['ids'] == IDS and proof['transparent_pixels'] == {'190': 0, '200': 0}
assert len(proof['contexts']) == 7
subprocess.run([sys.executable, str(source / 'rebuild.py'), str(out)], check=True)
for sprite_id in IDS:
    expected = next(e for e in inventory['outputs'] if e['source_id'] == sprite_id)
    png = out / f'terrain-shapesz-{sprite_id}-8.png'
    rebuilt = (out / f'{2010000 + sprite_id}.hda').read_bytes()
    header = [2010000 + sprite_id, 8, 24, 28, 0, 0]
    assert rebuilt[:28] == b'HDR1' + struct.pack('<6I', *header)
    assert len(rebuilt) == 28 + 192 * 224 * 4
    assert set(rebuilt[31::4]) == {255}
    assert sha(rebuilt) == expected['HDA_SHA256']
    assert sha(rebuilt[28:]) == expected['RGBA_SHA256']
    assert sha(png.read_bytes()) == expected['PNG_SHA256']
    assert Image.open(png).mode == 'RGBA' and Image.open(png).size == (192, 224)
    for key in ('default_preview_pack', 'default_debug_pack'):
        pack = manifest['packs'][manifest[key]]
        assert pack['count'] == len(pack['files'])
        name = f'terrain-shapesz-{sprite_id}-8.hda'
        entry = pack['files'][name]
        assert entry['header_u32'] == header
        raw = (repo / 'assets/hd/packs' / manifest[key] / name).read_bytes()
        canonical = repo / entry['source_png']
        assert sha(raw) == sha(rebuilt) == entry['sha256']
        assert sha(canonical.read_bytes()) == sha(png.read_bytes()) == entry['source_png_sha256']
        assert Image.open(canonical).convert('RGBA').tobytes() == rebuilt[28:]
        indexed = manifest['source_pngs'][sha(raw)]
        assert indexed['path'] == entry['source_png'] and indexed['sha256'] == entry['source_png_sha256']
        assert indexed['RGBA_sha256'] == sha(rebuilt[28:])
    for pack_name, pack in manifest['packs'].items():
        for density in (4, 8):
            present = f'terrain-shapesz-{sprite_id}-{density}.hda' in pack['files']
            assert present == (density == 8 and pack_name in (manifest['default_preview_pack'], manifest['default_debug_pack']))
if a.original_data:
    original = a.original_data.read_bytes()
    position = 0
    found = set()
    for sprite_id in range(1, 601):
        blank = original[position]
        position += 1
        indices = bytes(672) if blank else original[position:position + 672]
        position += 0 if blank else 672
        assert len(indices) == 672
        if sprite_id in IDS:
            assert sha(indices) == proof['indices_sha256'][str(sprite_id)]
            assert indices.count(0) == proof['transparent_pixels'][str(sprite_id)] == 0
            found.add(sprite_id)
    assert found == set(IDS)
print('PASS exact canonical PNG/RGBA/HDR1 in both default packs; finite manifest scope, imported generated source, opaque alpha and unchanged-neighbor guards.'
      + (' Both original shapesZ index identities and exact alpha verified.' if a.original_data else ''))
