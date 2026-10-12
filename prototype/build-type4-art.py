#!/usr/bin/env python3
"""Reproduce the approved five complete type4 composites in a fresh directory.

Original newsh2 data is optional for an independent source-occupancy audit;
it is neither an artwork input nor copied to the output or repository.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
from PIL import Image

IDS = [159, 161, 163, 165, 167]
ORDER = [159, 159, 161, 161, 163, 163, 165, 165, 167, 167,
         165, 165, 163, 163, 161, 161, 159, 159, 159, 159]
sha = lambda data: hashlib.sha256(data).hexdigest()
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--original-data', type=Path, help='Optional original newsh2.shp, read only')
p.add_argument('--enemy-data', type=Path, help='Optional original tyrian.hdt for all1701 bank-qualified record identities')
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
source = repo / 'assets/hd/artwork/type4-fivepose-v1'
given = a.output.absolute()
out = given.resolve()
if (any(q.is_symlink() for q in [given, *given.parents]) or out.exists()
        or out == repo or repo in out.parents or out in repo.parents):
    p.error('Choose a fresh directory outside the repository, without symlink path components')
assert all(not q.is_symlink() for q in source.rglob('*'))
manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
family = manifest['enemy_type4_fivepose_v1']
assert family['ids'] == IDS and family['slots'] == list(range(369, 374))
assert family['bank'] == 'newsh2.shp' and family['bank_role'] == 101
assert family['enemy_type'] == 4 and family['style'] == 'NORMAL'
assert family['logical_size'] == [24, 28] and family['anchor'] == [6, 7]
assert family['density'] == 8 and family['runtime_components'] == [0, 1, 19, 20]
assert family['order'] == ORDER
assert family['source'] == 'assets/hd/artwork/type4-fivepose-v1'
assert sha((source / 'inventory.json').read_bytes()) == family['source_inventory_sha256']
imported = json.loads((source / 'IMPORT.json').read_text())
assert imported['source_inventory_sha256'] == family['source_inventory_sha256']
assert len(imported['files']) == len({e['path'] for e in imported['files']})
assert {e['path'] for e in imported['files']} == {
    str(f.relative_to(source)) for f in source.rglob('*') if f.is_file() and f.name != 'IMPORT.json'
}
for entry in imported['files']:
    path = source / entry['path']
    assert source in path.resolve().parents
    assert sha(path.read_bytes()) == entry['sha256'], entry['path']
inventory = json.loads((source / 'inventory.json').read_text())
contract = json.loads((source / 'contract.json').read_text())
proof = json.loads((source / 'proof/type4-source-proof.json').read_text())
assert contract['output_bases'] == IDS and contract['bank'] == 'newsh2.shp'
assert contract['enemy_type'] == 4 and contract['runtime_components'] == [0, 1, 19, 20]
assert contract['order'] == ORDER == proof['record4']['egraphic'] == proof['animation']['order']
assert proof['record4']['shapebank'] == 1 and proof['record4']['ani'] == 20
assert [proof['record4'][k] for k in ('dgr', 'dani', 'dlevel', 'eenemydie')] == [0] * 4
assert [e['base'] for e in contract['entries']] == IDS
for k, e in enumerate(contract['entries']):
    assert e['hda_id'] == 1010000 + e['base'] and e['logical_size'] == [24, 28]
    assert e['density'] == 8 and e['anchor'] == [6, 7]
    x, y = k % 3 * 256 + 32, k // 3 * 320 + 48
    assert e['crop'] == [x, y, x + 192, y + 224]
assert contract['registered_master_size'] == [768, 640]
if a.enemy_data:
    data = a.enemy_data.read_bytes()
    assert sha(data) == proof['original_sources_sha256']['tyrian.hdt']
    source_reader = (repo / 'src/episodes.c').read_text()
    formats = {'u8': 'B', 's8': 'b', 'u16': 'H', 's16': 'h'}
    def schema(variable):
        return [(m[2], formats[m[1]], int(m[3])) for m in re.finditer(
            r'fread_(u8|s8|u16|s16)_die\(\s*&?' + variable + r'\[i\]\.(\w+),\s*(\d+),\s*f\)', source_reader)]
    weapon_schema, enemy_schema = schema('weapons'), schema('enemyDat')
    assert len(enemy_schema) == 28 and weapon_schema
    position = struct.unpack_from('<i', data)[0] + 14
    position += 1638 * sum(n * struct.calcsize(fmt) for _, fmt, n in weapon_schema)
    position += 61 * 82 + sum(n * size for n, size in [(55, 37), (7, 37), (19, 41), (38, 86), (12, 37)])
    users = []
    record_ids = list(range(851)) + list(range(1001, 1851))
    assert len(record_ids) == 1701
    for record_id in record_ids:
        record = {'id': record_id}
        for name, fmt, count in enemy_schema:
            values = list(struct.unpack_from('<' + str(count) + fmt, data, position))
            position += count * struct.calcsize(fmt)
            record[name] = values[0] if count == 1 else values
        if record_id == 4:
            assert record == proof['record4']
        if record['shapebank'] == 1 and (set(record['egraphic']) & set(IDS)
                or (not record['dani'] and record['dgr'] in IDS)):
            users.append(record_id)
    assert position <= len(data) and users == [4]
subprocess.run([sys.executable, str(source / 'rebuild.py'), str(out)], check=True)
original = a.original_data.read_bytes() if a.original_data else None
if original:
    assert sha(original) == proof['original_sources_sha256']['newsh2.shp']
for sprite_id in IDS:
    expected = next(e for e in inventory['outputs'] if e['source_id'] == sprite_id)
    source_frame = next(e for e in proof['frames'] if e['base_id'] == sprite_id)
    png = out / f'enemy-newsh2-{sprite_id}-8.png'
    rebuilt = (out / f'{1010000 + sprite_id}.hda').read_bytes()
    header = [1010000 + sprite_id, 8, 24, 28, 6, 7]
    assert rebuilt[:28] == b'HDR1' + struct.pack('<6I', *header)
    assert len(rebuilt) == 28 + 192 * 224 * 4
    assert sha(rebuilt) == expected['HDA_SHA256']
    assert sha(rebuilt[28:]) == expected['RGBA_SHA256']
    assert sha(png.read_bytes()) == expected['PNG_SHA256']
    image = Image.open(png)
    assert image.mode == 'RGBA' and image.size == (192, 224)
    alpha = image.getchannel('A')
    assert set(alpha.tobytes()) == {0, 255}
    native = alpha.resize((24, 28), Image.Resampling.NEAREST)
    assert native.resize((192, 224), Image.Resampling.NEAREST).tobytes() == alpha.tobytes()
    assert sha(native.tobytes()) == source_frame['alpha_sha256']
    assert list(native.getbbox()) == source_frame['alpha_bbox_xyxy_exclusive']
    assert native.tobytes().count(255) == source_frame['opaque_pixels']
    assert [c['id'] for c in source_frame['cells']] == [sprite_id + d for d in (0, 1, 19, 20)]
    if original:
        mask = bytearray(24 * 28)
        for cell, (delta, x, y) in zip(source_frame['cells'], [(0, 0, 0), (1, 12, 0), (19, 0, 14), (20, 12, 14)]):
            pos = struct.unpack_from('<H', original, (sprite_id + delta - 1) * 2)[0]
            start, linear = pos, 0
            while original[pos] != 15:
                command = original[pos]
                pos += 1
                linear += command & 15
                count = command >> 4
                assert 0 <= linear <= 168 and linear + count <= 168
                for n in range(linear, linear + count):
                    mask[(y + n // 12) * 24 + x + n % 12] = 255
                linear += count
                pos += count
            assert sha(original[start:pos + 1]) == cell['source_record_sha256']
        assert bytes(mask) == native.tobytes()
    for key in ('default_preview_pack', 'default_debug_pack'):
        pack = manifest['packs'][manifest[key]]
        assert pack['count'] == len(pack['files'])
        name = f'enemy-newsh2-{sprite_id}-8.hda'
        entry = pack['files'][name]
        assert entry['header_u32'] == header
        raw = (repo / 'assets/hd/packs' / manifest[key] / name).read_bytes()
        canonical = repo / entry['source_png']
        assert sha(raw) == sha(rebuilt) == entry['sha256']
        assert canonical.read_bytes() == png.read_bytes()
        assert sha(canonical.read_bytes()) == entry['source_png_sha256']
        indexed = manifest['source_pngs'][sha(raw)]
        assert indexed['path'] == entry['source_png'] and indexed['sha256'] == entry['source_png_sha256']
        assert indexed['RGBA_sha256'] == sha(rebuilt[28:])
    for pack_name, pack in manifest['packs'].items():
        for density in (4, 8):
            present = f'enemy-newsh2-{sprite_id}-{density}.hda' in pack['files']
            assert present == (density == 8 and pack_name in (manifest['default_preview_pack'], manifest['default_debug_pack']))
print('PASS five exact approved PNG/RGBA/HDR1 composites in both defaults; generated-only import, binary source occupancy, anchors, order and finite namespace.'
      + (' Original four-cell RLE occupancy independently verified.' if original else '')
      + (' All1701 records checked: only record4 uses these newsh2 bases.' if a.enemy_data else ''))
