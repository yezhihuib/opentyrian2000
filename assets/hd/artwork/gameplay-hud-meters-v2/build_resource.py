#!/usr/bin/env python3
"""Build exact frozen HUM2 from materials.py and selected RGB metadata only.

Outputs must be a new, external, nonsymlinked directory. No canonical resource,
original game data, image input or runtime capture is read.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import struct
import sys
sys.dont_write_bytecode = True
import numpy as np
import PIL
from materials import material
ROOT = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fnv(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return f'{value:016x}'

def json_bytes(value):
    return (json.dumps(value, indent=2) + '\n').encode()

def external_output(path):
    lexical = Path(os.path.abspath(path))
    for component in (lexical, *lexical.parents):
        require(not component.is_symlink(), 'Output path must not contain symlinks')
    output = lexical.resolve()
    require(output != ROOT and ROOT not in output.parents,
            'Output must be outside the source package')
    require(output not in ROOT.parents, 'Output must not contain the source package')
    require(not output.exists(), 'Output directory must not already exist')
    return output

def build(output):
    output = external_output(output)
    contract = json.loads((ROOT / 'contract.json').read_text())
    for name, digest in contract['source_files_sha256'].items():
        require(name in ('materials.py', 'selected-rgb.json'), 'Unexpected source input')
        require(sha((ROOT / name).read_bytes()) == digest, f'{name}: source hash mismatch')
    colors = json.loads((ROOT / 'selected-rgb.json').read_text())
    rgb = {role: {int(key): np.array(value, dtype=float) for key, value in entries.items()}
           for role, entries in colors.items()}
    require(set(rgb) == {'firepower', 'armor', 'generator'}, 'Unexpected color roles')
    sections = {}
    layouts = {}
    for kind, specs, width in (
        ('firepower', [(i, 3) for i in range(116, 127)], 2),
        ('armor', [(226, h) for h in (2, 4, 6)] +
         [(i, h) for i in range(227, 240) for h in (2, 4)], 9)):
        raw = bytearray()
        records = []
        for index, height in specs:
            tile = material(rgb[kind][index], width, height, kind).convert('RGBA')
            require(tile.getextrema()[3] == (255, 255), 'Nonopaque material')
            data = tile.tobytes()
            records.append({'source_palette_role': index, 'logical_height': height,
                            'width': width * 4, 'height': height * 4,
                            'rgba_offset_bytes': len(raw), 'rgba_bytes': len(data),
                            'rgba_sha256': sha(data),
                            'png': f'{kind}-{index}-h{height}-4x.png'})
            raw.extend(data)
        sections[f'{kind}-tiles.rgba'] = bytes(raw)
        layouts[kind] = records
    require(sha(json_bytes(layouts)) == contract['tile_layout_json_sha256'],
            'Tile offsets or hashes changed')
    rows, row_ids, lookup, hashes = [], {}, [], []
    for index in range(113, 126):
        for height in range(1, 93):
            data = material(rgb['generator'][index], 8, height, 'generator').convert('RGBA').tobytes()
            start = len(lookup)
            require(start == (index - 113) * 17112 + 2 * height * (height - 1),
                    'Lookup start formula mismatch')
            for row_number in range(height * 4):
                row = data[row_number * 128:(row_number + 1) * 128]
                require(len(row) == 128 and all(a == 255 for a in row[3::4]),
                        'Generator row dimensions or alpha mismatch')
                if row not in row_ids:
                    row_ids[row] = len(rows)
                    rows.append(row)
                lookup.append(row_ids[row])
            require(b''.join(rows[n] for n in lookup[start:]) == data,
                    'Generator material reconstruction mismatch')
            hashes.append({'palette_role': index, 'logical_run_height': height, 'sha256': sha(data)})
    require(len(hashes) == 1196 and len(rows) == 944 and len(lookup) == 222456,
            'Generator counts mismatch')
    require(min(lookup) == 0 and max(lookup) == 943, 'Generator lookup out of bounds')
    require(sha(json_bytes(hashes)) == contract['generator']['material_hash_list_json_sha256'],
            'One or more of the 1196 original material hashes changed')
    sections['generator-material-rows.rgba'] = b''.join(rows)
    sections['generator-run-row-lookup.u16le'] = struct.pack('<222456H', *lookup)
    require(list(sections) == contract['section_order'], 'Section order mismatch')
    for name, data in sections.items():
        target = contract['sections'][name]
        require((len(data), sha(data), fnv(data)) ==
                (target['bytes'], target['sha256'], target['fnv64']), f'{name}: section mismatch')
    payload = b''.join(sections.values())
    require((len(payload), sha(payload), fnv(payload)) ==
            (contract['payload_bytes'], contract['payload_sha256'], contract['payload_fnv64']),
            'Combined payload mismatch')
    fields = contract['u32_values']
    require(fields == [2, 112, 4, 320, 200, 4224, 51840, 120832, 444912, 944, 222456],
            'Unexpected HUM2 dimensions')
    stamps = [int(value, 16) for value in contract['u64_values_hex']]
    header = struct.pack('<4s11I8Q', b'HUM2', *fields, *stamps)
    require(len(header) == 112 and stamps[-1] == 0, 'Unexpected header')
    resource = header + payload
    require((len(resource), sha(resource), fnv(resource)) ==
            (contract['resource_bytes'], contract['resource_sha256'], contract['resource_fnv64']),
            'HUM2 canonical hash mismatch')
    scope = bytearray(64000)
    for x0, y0, x1, y1 in contract['logical_boxes_half_open'].values():
        for y in range(y0, y1):
            scope[y * 320 + x0:y * 320 + x1] = bytes([255]) * (x1 - x0)
    require(scope.count(255) == 1390 and sha(scope) == contract['scope_mask_sha256'],
            'Scope differs from exact1390 cells')
    # Validate and reserve output only after every material/hash check has passed.
    require(external_output(output) == output, 'Output path changed during build')
    output.mkdir(parents=True, exist_ok=False)
    for name, data in sections.items():
        (output / name).write_bytes(data)
    (output / 'gameplay-hud-meters-v2.hda').write_bytes(resource)
    (output / 'meter-scope-1390.mask').write_bytes(scope)
    (output / 'tile-layout.json').write_bytes(json_bytes(layouts))
    report = {
        'status': 'PASS', 'source_recipe_sha256': sha((ROOT / 'materials.py').read_bytes()),
        'selected_rgb_sha256': sha((ROOT / 'selected-rgb.json').read_bytes()),
        'versions': {'python': platform.python_version(), 'Pillow': PIL.__version__, 'numpy': np.__version__},
        'sections': {name: {'bytes': len(data), 'sha256': sha(data), 'fnv64': fnv(data)}
                     for name, data in sections.items()},
        'payload_bytes': len(payload), 'payload_sha256': sha(payload), 'payload_fnv64': fnv(payload),
        'resource_bytes': len(resource), 'resource_sha256': sha(resource), 'resource_fnv64': fnv(resource),
        'header_unpacked_matches_contract': struct.unpack('<4s11I8Q', resource[:112]) == (b'HUM2', *fields, *stamps),
        'exact_eof': len(resource) == 621920,
        'firepower_tiles': 11, 'coarse_armor_tiles': 29,
        'generator_runs_reconstructed_and_hashed': 1196,
        'generator_hash_list_matches_frozen_sha256': sha(json_bytes(hashes)),
        'generator_unique_rows': len(rows), 'generator_lookup_entries': len(lookup),
        'generator_lookup_min_id': min(lookup), 'generator_lookup_max_id': max(lookup),
        'every_lookup_start_formula_verified': True,
        'scope_cells': scope.count(255), 'scope_mask_sha256': sha(scope),
        'canonical_resource_or_image_input_used': False,
        'original_game_data_input_used': False, 'runtime_installed_or_executed': False,
        'external_new_output_only': True}
    (output / 'build-proof.json').write_bytes(json_bytes(report))
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New external output directory; existing/source/symlink paths are rejected')
    args = parser.parse_args()
    result = build(args.output)
    print(json.dumps({key: result[key] for key in ('status', 'resource_sha256',
                      'generator_runs_reconstructed_and_hashed', 'generator_lookup_max_id')}, indent=2))

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(f'HUM2 build failed: {error}', file=sys.stderr)
        sys.exit(1)
