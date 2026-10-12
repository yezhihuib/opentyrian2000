#!/usr/bin/env python3
"""Verify frozen HUT1 assets; optionally compare the original authored pilot.

This verifier does not import the reproducer or read game PIC/font/capture data.
"""

import argparse
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fnv(data):
    result = 14695981039346656037
    for value in data:
        result = ((result ^ value) * 1099511628211) % (1 << 64)
    return result


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(package, pilot=None):
    manifest = json.loads((package / 'manifest.json').read_text())
    provenance = json.loads((package / 'provenance.json').read_text())
    for name, expected in manifest['source_input_sha256'].items():
        require(digest((package / name).read_bytes()) == expected,
                f'Frozen source hash mismatch: {name}')
    for record in manifest['artifacts']:
        data = (package / record['path']).read_bytes()
        require(len(data) == record['bytes'], f'Length mismatch: {record["path"]}')
        require(digest(data) == record['sha256'], f'Hash mismatch: {record["path"]}')

    expected = [('MODE', (284, 54, 303, 59))]
    for word, x in [('SHIELD', 285), ('ARMOR', 296)]:
        for index, char in enumerate(word):
            y = 138 + index * 6
            expected.append((f'{word}_{char}{index}', (x, y, x + 5, y + 5)))
    require(len(manifest['tiles']) == len(provenance['tiles']) == 12,
            'Exactly 12 tiles are required.')
    mask = bytearray(320 * 200)
    payload_parts = []
    comparisons = []
    offset = 64
    for index, ((name, box), tile, frozen) in enumerate(
            zip(expected, manifest['tiles'], provenance['tiles'], strict=True)):
        require(tile['name'] == frozen['name'] == name, f'Tile order mismatch at {index}')
        require(tile['logical_box_half_open'] == frozen['logical_box_half_open'] == list(box),
                f'Logical bounds mismatch: {name}')
        x0, y0, x1, y1 = box
        for y in range(y0, y1):
            for x in range(x0, x1):
                require(mask[y * 320 + x] == 0, f'Overlapping tile: {name}')
                mask[y * 320 + x] = 255
        path = package / tile['png_path']
        file_bytes = path.read_bytes()
        with Image.open(path) as image:
            require(image.mode == 'RGBA', f'PNG is not native RGBA: {name}')
            require(image.size == ((x1 - x0) * 4, (y1 - y0) * 4),
                    f'PNG dimensions mismatch: {name}')
            rgba = image.tobytes()
        require(set(rgba[3::4]) == {255}, f'Nonopaque alpha: {name}')
        require(digest(file_bytes) == frozen['png_sha256'], f'Pilot PNG hash mismatch: {name}')
        require(digest(rgba) == frozen['decoded_rgba_sha256'],
                f'Pilot decoded RGBA hash mismatch: {name}')
        require(f'{fnv(rgba):016x}' == frozen['decoded_rgba_fnv1a64'],
                f'Decoded RGBA FNV mismatch: {name}')
        require(tile['tile_index'] == index and tile['resource_offset'] == offset and
                tile['payload_offset'] == offset - 64 and tile['rgba_bytes'] == len(rgba),
                f'Payload layout mismatch: {name}')
        comparison = {'name': name, 'png_sha256': digest(file_bytes),
                      'decoded_rgba_sha256': digest(rgba), 'alpha_min': 255,
                      'alpha_max': 255, 'reference_hashes_match': True}
        if pilot:
            original = pilot / 'generated' / path.name
            require(file_bytes == original.read_bytes(), f'Direct PNG mismatch: {name}')
            with Image.open(original) as image:
                require(image.mode == 'RGBA' and image.tobytes() == rgba,
                        f'Direct RGBA mismatch: {name}')
            comparison['direct_pilot_png_byte_equal'] = True
            comparison['direct_pilot_rgba_byte_equal'] = True
        comparisons.append(comparison)
        payload_parts.append(rgba)
        offset += len(rgba)

    mask = bytes(mask)
    require(mask.count(255) == 370 and mask.count(0) == 63630, 'Incorrect ownership count.')
    require((package / 'fixed-label-mask-370.bin').read_bytes() == mask, 'Mask bounds mismatch.')
    require(digest(mask) == '40360dde85cdcd98eb1a65c6e9b0972c5fa596618adc4a07ce79953ce19483b0',
            'Exact mask signature mismatch.')
    with Image.open(package / 'fixed-label-mask-370.png') as image:
        require(image.mode == 'L' and image.size == (320, 200) and image.tobytes() == mask,
                'Mask PNG mismatch.')
    if pilot:
        for name in ['fixed-label-mask-370.bin', 'fixed-label-mask-370.png']:
            require((package / name).read_bytes() == (pilot / name).read_bytes(),
                    f'Direct pilot mask mismatch: {name}')
    # Check disjointness against the two already-published component layouts.
    ownership = provenance['existing_ownership']
    overlaps = {}
    for role, key in [('HUC1', 'HUC1_boxes_including_max_shield_window'),
                      ('HUL1', 'HUL1_spatial_union_boxes')]:
        count = 0
        for x0, y0, x1, y1 in ownership[key]:
            count += sum(mask[y * 320 + x] != 0
                         for y in range(y0, y1) for x in range(x0, x1))
        require(count == 0, f'Unexpected {role} overlap.')
        overlaps[role] = count

    payload = b''.join(payload_parts)
    resource = (package / 'gameplay-hud-fixed-text-v1.hda').read_bytes()
    require(len(resource) == 23744 and len(payload) == 23680, 'Resource size mismatch.')
    require(resource[64:] == payload, 'Resource payload is not the exact ordered tile RGBA.')
    expected_header = (b'HUT1', 1, 4, 12, 370, 23680, 1, 0,
                       0x14c1441f3d5dc0e2, 0x5e80e83992be2927,
                       0xb110512dd1fc63f4, fnv(payload))
    require(struct.unpack('<4s7I4Q', resource[:64]) == expected_header,
            'HUT1 header mismatch.')
    require(digest(resource) == manifest['resource']['sha256'], 'Resource SHA256 mismatch.')
    require(fnv(payload) == 0xa2433de596bd3873, 'Frozen payload signature mismatch.')
    require(provenance['source_370']['sha256'] ==
            '272f2995359bd118dd62cb3b597ad937034527a25180115b399f8978777c59f6',
            'Original source signature metadata mismatch.')
    return {'status': 'PASS', 'tile_count': 12, 'png_count_including_mask': 13,
            'logical_cells': 370, 'opaque_rgba_pixels': len(payload) // 4,
            'resource_bytes': len(resource), 'resource_sha256': digest(resource),
            'payload_sha256': digest(payload), 'payload_fnv1a64': f'{fnv(payload):016x}',
            'exact_mask_verified': True, 'component_overlap_cells': overlaps,
            'direct_pilot_comparison': pilot is not None, 'tiles': comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--pilot', type=Path, help='Optional original authored pilot directory.')
    parser.add_argument('--report', type=Path, help='Optional new JSON report path.')
    args = parser.parse_args()
    report = verify(args.package.resolve(), args.pilot.resolve() if args.pilot else None)
    encoded = json.dumps(report, indent=2) + '\n'
    if args.report:
        if args.report.exists():
            require(args.report.read_text() == encoded, 'Refusing to overwrite a different report.')
        else:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(encoded)
    print(encoded, end='')


if __name__ == '__main__':
    main()
