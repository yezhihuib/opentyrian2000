#!/usr/bin/env python3
"""Rebuild and audit the finite generated Layer3 left-mechanical family.

The optional shapesZ audit reads original indices only to check exact alpha and
source identity. Original RGB is never an artwork rebuild dependency.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from PIL import Image

IDS = [186, 187, 196, 197]
sha = lambda data: hashlib.sha256(data).hexdigest()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--original-data', type=Path, help='Optional local shapesz.dat, never bundled')
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
source = repo / 'assets/hd/artwork/mechanical-left4-v1'
given = a.output.absolute()
out = given.resolve()
if (any(q.is_symlink() for q in [given, *given.parents]) or out.exists()
        or out == repo or repo in out.parents or out in repo.parents):
    p.error('Choose a fresh directory outside the repository, without symlink path components')
manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
family = manifest['terrain_layer3_mechanical_left4_v1']
assert family['ids'] == IDS and family['slots'] == [363, 364, 365, 366]
assert family['layer'] == 3 and family['style'] == 'NORMAL'
assert family['logical_size'] == [24, 28] and family['anchor'] == [0, 0]
assert family['source'] == 'assets/hd/artwork/mechanical-left4-v1'
assert sha((source / 'inventory.json').read_bytes()) == family['source_inventory_sha256']
imported = json.loads((source / 'IMPORT.json').read_text())
assert imported['source_inventory_sha256'] == family['source_inventory_sha256']
for entry in imported['files']:
    assert sha((source / entry['path']).read_bytes()) == entry['sha256'], entry['path']
guards = json.loads((source / 'proof/unchanged-guards.json').read_text())
for entry in guards['guards']:
    assert sha((repo / entry['source_png']).read_bytes()) == entry['sha256'], entry['id']
mask = Image.open(source / 'masks/source-alpha-density8.png').convert('L')
assert mask.size == (384, 448)
assert set(mask.tobytes()) == {0, 255}
assert mask.resize((48, 56), Image.Resampling.NEAREST).resize(mask.size, Image.Resampling.NEAREST).tobytes() == mask.tobytes()
subprocess.run([sys.executable, str(source / 'rebuild.py'), str(out)], check=True)
for offset, sprite_id in enumerate(IDS):
    x, y = (offset % 2) * 192, (offset // 2) * 224
    alpha = mask.crop((x, y, x + 192, y + 224)).tobytes()
    assert alpha.count(0) == (38 if sprite_id in (186, 196) else 0) * 64
    rebuilt = (out / f'{2010000 + sprite_id}.hda').read_bytes()
    assert rebuilt[:28] == b'HDR1' + struct.pack('<6I', 2010000 + sprite_id, 8, 24, 28, 0, 0)
    assert len(rebuilt) == 28 + 192 * 224 * 4
    assert rebuilt[31::4] == alpha
    for key in ('default_preview_pack', 'default_debug_pack'):
        pack = manifest['packs'][manifest[key]]
        assert pack['count'] == len(pack['files'])
        name = f'terrain-shapesz-{sprite_id}-8.hda'
        entry = pack['files'][name]
        assert entry['header_u32'] == [2010000 + sprite_id, 8, 24, 28, 0, 0]
        raw = (repo / 'assets/hd/packs' / manifest[key] / name).read_bytes()
        canonical = repo / entry['source_png']
        png = out / f'terrain-shapesz-{sprite_id}-8.png'
        assert sha(raw) == sha(rebuilt) == entry['sha256']
        assert sha(canonical.read_bytes()) == sha(png.read_bytes()) == entry['source_png_sha256']
        assert Image.open(canonical).convert('RGBA').tobytes() == rebuilt[28:]
    for pack_name, pack in manifest['packs'].items():
        if pack_name not in (manifest['default_preview_pack'], manifest['default_debug_pack']):
            assert f'terrain-shapesz-{sprite_id}-8.hda' not in pack['files']
# The later round-insert family is independent of this four-tile rebuild.
# Preserve the historical exclusion unless that exact finite addition is declared.
round_inserts = manifest.get('terrain_layer3_mechanical_round_inserts_v1')
if round_inserts:
    assert round_inserts['ids'] == [190, 200] and round_inserts['slots'] == [367, 368]
    assert round_inserts['layer'] == 3 and round_inserts['style'] == 'NORMAL'
for key in ('default_preview_pack', 'default_debug_pack'):
    files = manifest['packs'][manifest[key]]['files']
    for i in (190, 200):
        assert f'terrain-shapesz-{i}-4.hda' not in files
        assert (f'terrain-shapesz-{i}-8.hda' in files) == bool(round_inserts)
if a.original_data:
    original = a.original_data.read_bytes()
    proof = json.loads((source / 'proof/source-proof.json').read_text())
    assert sha(original) == proof['data_sha256']
    position = 0
    original_mask = Image.new('L', (48, 56))
    for sprite_id in range(1, 601):
        start = position
        blank = original[position]
        position += 1
        indices = bytes(672) if blank else original[position:position + 672]
        position += 0 if blank else 672
        if str(sprite_id) in proof['tiles']:
            entry = proof['tiles'][str(sprite_id)]
            assert start == entry['offset'] and sha(indices) == entry['index_sha256']
            assert indices.count(0) == entry['transparent_pixels']
        if sprite_id in IDS:
            offset = IDS.index(sprite_id)
            tile_mask = Image.frombytes('L', (24, 28), bytes(255 if v else 0 for v in indices))
            original_mask.paste(tile_mask, ((offset % 2) * 24, (offset // 2) * 28))
    assert original_mask.resize(mask.size, Image.Resampling.NEAREST).tobytes() == mask.tobytes()
    assert guards['excluded_original190'] == proof['tiles']['190']
print('PASS exact canonical PNG/RGBA/HDR1 in both default packs; finite scope, imported source, alpha and neighbor guards.'
      + (' Original shapesZ identity, all four index masks and excluded190 verified.' if a.original_data else ''))
