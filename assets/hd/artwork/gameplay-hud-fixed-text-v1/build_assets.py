#!/usr/bin/env python3
"""Reproduce the accepted 370-cell fixed green-label art without game assets.

Inputs are only the two adjacent JSON files. Outputs are generated PNGs, an
ownership mask, the HUT1 resource, and a deterministic manifest. Existing files
are never changed unless their bytes already equal the newly generated result.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import zlib

import numpy as np
import PIL
from PIL import Image, ImageChops, ImageDraw


HERE = Path(__file__).resolve().parent
HEADER = struct.Struct('<4s7I4Q')
RESOURCE_NAME = 'gameplay-hud-fixed-text-v1.hda'
DENSITY = 4
PIC3_FNV = 0x14C1441F3D5DC0E2
PALETTE_FNV = 0x5E80E83992BE2927
SOURCE_370_FNV = 0xB110512DD1FC63F4
SOURCE_370_SHA256 = '272f2995359bd118dd62cb3b597ad937034527a25180115b399f8978777c59f6'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fnv1a64(data: bytes) -> int:
    value = 0xCBF29CE484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def known_answer_tests() -> None:
    assert fnv1a64(b'') == 0xCBF29CE484222325
    assert fnv1a64(b'a') == 0xAF63DC4C8601EC8C
    assert fnv1a64(b'foobar') == 0x85944171F73967E8
    assert HEADER.size == 64


def specs() -> list[tuple[str, tuple[int, ...], list[tuple[str, int, int]]]]:
    result = [('MODE', (284, 54, 303, 59),
               [('M', 0, 5), ('O', 6, 4), ('D', 11, 4), ('E', 16, 3)])]
    for word, x in [('SHIELD', 285), ('ARMOR', 296)]:
        for index, char in enumerate(word):
            y = 138 + 6 * index
            result.append((f'{word}_{char}{index}', (x, y, x + 5, y + 5),
                           [(char, 0, 5)]))
    return result


def translated(lines: list, width: int) -> list:
    # This operation order is frozen from the accepted pilot. All cells are 5
    # logical units high; the pilot's .36 inset and .72 stroke are unchanged.
    return [[(.36 + (x - .38) / 3.24 * max(0, width - .72),
              .36 + (y - .38) / 4.24 * max(0, 5 - .72))
             for x, y in line] for line in lines]


def coverage(paths: list, width: int) -> Image.Image:
    supersampling = 32
    mask = Image.new('L', (width * supersampling, 5 * supersampling))
    draw = ImageDraw.Draw(mask)
    for line in paths:
        points = [(round(x * supersampling), round(y * supersampling))
                  for x, y in line]
        if len(points) == 1:
            x, y = points[0]
            radius = .36 * supersampling
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
        else:
            draw.line(points, fill=255, width=round(.72 * supersampling),
                      joint='curve')
    clip = Image.new('L', mask.size)
    ImageDraw.Draw(clip).rectangle((0, 0, width * supersampling - 1,
                                   5 * supersampling - 1), fill=255)
    mask = ImageChops.multiply(mask, clip)
    return mask.resize((width * DENSITY, 20), Image.Resampling.BOX)


def fixed_tile(spec: tuple, glyphs: dict) -> Image.Image:
    _, box, letters = spec
    width = box[2] - box[0]
    mask = Image.new('L', (width * DENSITY, 20))
    for char, x, letter_width in letters:
        mask.paste(coverage(translated(glyphs[char], letter_width), letter_width),
                   (x * DENSITY, 0))
    # Authored colors, not copied palette arrays. Preserve the exact pilot
    # floating-point operation order and truncation to unsigned eight-bit RGB.
    yy = np.linspace(0, 1, 20)[:, None, None]
    colors = np.array([8, 182, 20]) * (1 - yy) + np.array([0, 125, 0]) * yy
    color = np.broadcast_to(colors, (20, width * DENSITY, 3))
    alpha = np.array(mask, dtype=float) / 255
    rgb = np.uint8(color * alpha[:, :, None])
    # Coverage is baked into RGB over black. Stored alpha is 255 even in black.
    return Image.fromarray(rgb, 'RGB').convert('RGBA')


def png_bytes(image: Image.Image) -> bytes:
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


def retain_or_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f'Refusing to overwrite different existing bytes: {path}')
    else:
        path.write_bytes(data)


def build(output: Path) -> dict:
    known_answer_tests()
    provenance_bytes = (HERE / 'provenance.json').read_bytes()
    vector_bytes = (HERE / 'selected-glyph-paths.json').read_bytes()
    provenance = json.loads(provenance_bytes)
    vectors = json.loads(vector_bytes)
    expected_dependencies = provenance['build_dependencies']
    actual_dependencies = {'Pillow': PIL.__version__, 'numpy': np.__version__,
                           'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION}
    if actual_dependencies != expected_dependencies:
        raise RuntimeError(f'Exact reproduction requires {expected_dependencies}; '
                           f'found {actual_dependencies}')
    assert vectors['stroke_width_logical'] == .72
    assert set(vectors['glyphs']) == set('MODESHIELDARMOR')
    assert provenance['source_370']['sha256'] == SOURCE_370_SHA256
    assert int(provenance['source_370']['fnv1a64'], 16) == SOURCE_370_FNV
    assert int(provenance['source_pic3']['fnv1a64'], 16) == PIC3_FNV
    assert int(provenance['palette']['palette5_rgb_fnv1a64'], 16) == PALETTE_FNV

    records = []
    payload_parts = []
    ownership = np.zeros((200, 320), dtype=np.uint8)
    outputs = {}
    offset = 64
    tile_specs = specs()
    assert len(tile_specs) == len(provenance['tiles']) == 12
    for spec, reference in zip(tile_specs, provenance['tiles'], strict=True):
        name, box, letters = spec
        assert name == reference['name']
        assert list(box) == reference['logical_box_half_open']
        tile = fixed_tile(spec, vectors['glyphs'])
        rgba = tile.tobytes()
        png = png_bytes(tile)
        assert tile.mode == 'RGBA'
        assert list(tile.size) == reference['pixel_size']
        assert set(rgba[3::4]) == {255}
        assert sha256(rgba) == reference['decoded_rgba_sha256']
        assert f'{fnv1a64(rgba):016x}' == reference['decoded_rgba_fnv1a64']
        assert sha256(png) == reference['png_sha256']
        assert len(png) == reference['png_bytes']
        x0, y0, x1, y1 = box
        assert not ownership[y0:y1, x0:x1].any()
        ownership[y0:y1, x0:x1] = 255
        record = dict(reference)
        record.update({'tile_index': len(records), 'alpha_min': 255,
                       'alpha_max': 255, 'logical_cells': (x1 - x0) * (y1 - y0),
                       'letters': [{'character': ch, 'local_x': x, 'width': w,
                                    'height': 5} for ch, x, w in letters],
                       'payload_offset': offset - 64, 'resource_offset': offset,
                       'rgba_bytes': len(rgba)})
        records.append(record)
        payload_parts.append(rgba)
        outputs[reference['png_path']] = png
        offset += len(rgba)

    mask_bytes = ownership.tobytes()
    mask_png = png_bytes(Image.fromarray(ownership))
    assert int(np.count_nonzero(ownership)) == 370
    assert sha256(mask_bytes) == provenance['mask']['bin_sha256']
    assert sha256(mask_png) == provenance['mask']['png_sha256']
    # Each vertical inter-letter row is intentionally outside ownership.
    for word, x in [('SHIELD', 285), ('ARMOR', 296)]:
        for i in range(len(word) - 1):
            assert not ownership[143 + 6 * i, x:x + 5].any()
    outputs['fixed-label-mask-370.bin'] = mask_bytes
    outputs['fixed-label-mask-370.png'] = mask_png

    payload = b''.join(payload_parts)
    assert len(payload) == 23680 == 370 * DENSITY * DENSITY * 4
    header_values = (b'HUT1', 1, DENSITY, 12, 370, 23680, 1, 0,
                     PIC3_FNV, PALETTE_FNV, SOURCE_370_FNV, fnv1a64(payload))
    resource = HEADER.pack(*header_values) + payload
    assert len(resource) == 23744
    assert HEADER.unpack(resource[:64]) == header_values
    outputs[RESOURCE_NAME] = resource
    artifact_records = [{'path': name, 'bytes': len(data), 'sha256': sha256(data)}
                        for name, data in sorted(outputs.items())]
    manifest = {
        'schema': 'gameplay-hud-fixed-text-manifest-v1',
        'status': 'FROZEN_GENERATED_ONLY_TRIAL_ART_NOT_RUNTIME_INTEGRATED',
        'density': DENSITY, 'layout_id': 1, 'tile_count': 12, 'logical_cells': 370,
        'scope': provenance['source_scope'],
        'ownership': {'canvas_logical': [320, 200], 'mask_format': 'uint8 row-major 0/255',
                      'mask_sha256': sha256(mask_bytes),
                      'whole_tile_owned_including_black': True,
                      'vertical_gap_cells_owned': 0},
        'source_370': provenance['source_370'],
        'resource': {
            'path': RESOURCE_NAME, 'magic': 'HUT1', 'version': 1,
            'header_struct': '<4s7I4Q', 'header_bytes': 64, 'density': 4,
            'tile_count': 12, 'logical_cells': 370, 'payload_bytes': len(payload),
            'layout_id': 1, 'reserved': 0, 'total_bytes': len(resource),
            'pic3_fnv1a64': f'{PIC3_FNV:016x}',
            'palette_fnv1a64': f'{PALETTE_FNV:016x}',
            'source_370_fnv1a64': f'{SOURCE_370_FNV:016x}',
            'payload_fnv1a64': f'{fnv1a64(payload):016x}',
            'payload_sha256': sha256(payload), 'sha256': sha256(resource),
            'payload_order': 'MODE, SHIELD top-down, ARMOR top-down',
            'pixel_order': 'top-to-bottom, left-to-right, RGBA8, no stride padding',
            'alpha': '255 throughout every tile, including black'},
        'source_input_sha256': {'provenance.json': sha256(provenance_bytes),
                                'selected-glyph-paths.json': sha256(vector_bytes)},
        'dependencies': actual_dependencies,
        'fnv1a64': {'offset_basis_hex': 'cbf29ce484222325',
                    'prime_hex': '00000100000001b3', 'modulus': '2^64',
                    'hex_representation': 'numeric value, not serialized byte order'},
        'tiles': records, 'artifacts': artifact_records,
        'checks': {'all_tile_png_files_equal_pilot': True,
                   'all_tile_decoded_rgba_equal_pilot': True,
                   'all_tile_alpha_255': True, 'mask_equal_pilot': True,
                   'vertical_gaps_excluded': True, 'overlapping_tiles': 0,
                   'header_and_payload_verified': True,
                   'original_source_files_required_to_rebuild': False},
        'limits': 'No runtime, capture, repository, HUD1, HUC1, HUL1, or dynamic '
                  '127-glyph atlas changes. This package proves art reproduction only.'}
    outputs['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    # All identities are validated before writing any output.
    for name, data in sorted(outputs.items()):
        retain_or_write(output / name, data)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE,
                        help='Output directory; default is this package directory.')
    args = parser.parse_args()
    manifest = build(args.output.resolve())
    print(json.dumps({'status': 'PASS', 'tile_count': 12, 'logical_cells': 370,
                      'resource_bytes': 23744,
                      'resource_sha256': manifest['resource']['sha256'],
                      'payload_fnv1a64': manifest['resource']['payload_fnv1a64']},
                     indent=2))


if __name__ == '__main__':
    main()
