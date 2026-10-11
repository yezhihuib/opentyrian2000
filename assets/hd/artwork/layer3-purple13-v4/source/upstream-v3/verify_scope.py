#!/usr/bin/env python3
"""Read-only, finite pixel-difference and HDR1 scope check for purple13 v3."""
from pathlib import Path
from PIL import Image
import argparse
import hashlib
import json
import struct

IDS = [150, 156, 157, 158, 159, 160, 166, 168, 169, 170, 176, 177, 178]
OVERRIDES = [150, 166, 168, 176, 177, 178]
MANIFEST_SHA = 'b733a687a181ab6f1d7ec8d5d6bafdd4af91cd4d9c4cc956de4293ad3ee0b26a'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgba(path, size=(192, 224)):
    with Image.open(path) as image:
        require(image.size == size, 'Unexpected image size: ' + str(path))
        return image.convert('RGBA').tobytes()


def verify(package, target):
    manifest_path = package / 'runtime-overlay/manifest.json'
    require(sha(manifest_path.read_bytes()) == MANIFEST_SHA, 'Frozen manifest changed')
    manifest = json.loads(manifest_path.read_text())
    source_manifest = json.loads((package / 'source/selected-crops.json').read_text())
    require(sorted(map(int, manifest)) == IDS, 'Unexpected selected IDs')
    png_names = {f'terrain-shapesz-{i}-8.png' for i in IDS}
    hda_names = {f'terrain-shapesz-{i}-8.hda' for i in IDS} | {'manifest.json'}
    require({p.name for p in (target / 'output').iterdir()} == png_names,
            'Unexpected output PNG scope')
    require({p.name for p in (target / 'runtime-overlay').iterdir()} == hda_names,
            'Unexpected HDA scope')
    require((target / 'runtime-overlay/manifest.json').read_bytes() == manifest_path.read_bytes(),
            'Target manifest differs')
    results = []
    changed_ids = []
    for index, tile in enumerate(IDS):
        row = manifest[str(tile)]
        stem = f'terrain-shapesz-{tile}-8'
        before = rgba(package / 'source/generated-crops' / (stem + '.png'))
        require(sha(before) == source_manifest[str(tile)]['rgba_sha256'],
                f'Authored source RGBA differs: {tile}')
        after = rgba(target / 'output' / (stem + '.png'))
        require(set(before[3::4]) == {255} and set(after[3::4]) == {255},
                f'Alpha is not fully opaque: {tile}')
        require(sha(after) == row['rgba_sha256'], f'Selected RGBA mismatch: {tile}')
        changes = []
        max_delta = 0
        allowed_y = range(216, 224) if tile in (150, 166, 168) else range(0, 8)
        for pixel in range(192 * 224):
            offset = pixel * 4
            a, b = before[offset:offset + 4], after[offset:offset + 4]
            require(a[3] == b[3], f'Alpha changed: {tile}')
            if a != b:
                x, y = pixel % 192, pixel // 192
                require(tile in OVERRIDES and y in allowed_y,
                        f'Pixel changed outside finite connector ROI: {tile}, {x}, {y}')
                changes.append((x, y))
                max_delta = max(max_delta, *(abs(a[c] - b[c]) for c in range(3)))
        bounds = ([min(x for x, y in changes), min(y for x, y in changes),
                   max(x for x, y in changes), max(y for x, y in changes)] if changes else None)
        require(max_delta <= 20, f'RGB channel delta exceeds 20: {tile}')
        require(len(changes) == row['tone_changed_hd_pixels'], f'Change count differs: {tile}')
        require(bounds == row['changed_roi_bbox_inclusive'], f'Change bounds differ: {tile}')
        require(max_delta == row['max_rgb_delta_from_v1'], f'Maximum delta differs: {tile}')
        require(row['slot'] == 290 + index, f'Slot differs: {tile}')
        require(row['source_id'] == tile and row['source_layer'] == 3,
                f'Source identity differs: {tile}')
        require(row['semantic_asset_id'] == 2010000 + tile and row['scale'] == 8 and
                row['logical_size'] == [24, 28] and row['anchor'] == [0, 0],
                f'Manifest geometry differs: {tile}')
        hda = (target / 'runtime-overlay' / (stem + '.hda')).read_bytes()
        expected_header = b'HDR1' + struct.pack('<6I', 2010000 + tile, 8, 24, 28, 0, 0)
        require(len(hda) == 172060 and hda[:28] == expected_header and hda[28:] == after,
                f'HDR1 header, length or payload differs: {tile}')
        require(sha(hda) == row['hda_sha256'], f'Frozen HDA hash differs: {tile}')
        if changes:
            changed_ids.append(tile)
        results.append({'id': tile, 'slot': row['slot'], 'changed_hd_pixels': len(changes),
                        'changed_bbox_inclusive': bounds, 'max_rgb_channel_delta': max_delta,
                        'alpha_exact_all255': True, 'dimensions_anchor_header_exact': True,
                        'outside_roi_rgba_exact': True, 'selected_rgba_and_hda_exact': True})
    require(changed_ids == OVERRIDES, 'Exactly six changed tiles required')
    return {'status': 'PASS', 'tiles': 13, 'slots': list(range(290, 303)),
            'override_ids': OVERRIDES, 'unchanged_tiles': 7,
            'total_changed_hd_pixels': sum(r['changed_hd_pixels'] for r in results),
            'maximum_rgb_channel_delta': max(r['max_rgb_channel_delta'] for r in results),
            'all_alpha_255': True, 'finite_six_roi_only': True, 'items': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild-root', type=Path,
                        help='Defaults to checking selected outputs shipped in the package')
    args = parser.parse_args()
    package = Path(__file__).resolve().parent.parent
    print(json.dumps(verify(package, args.rebuild_root.resolve() if args.rebuild_root else package),
                     indent=2))
