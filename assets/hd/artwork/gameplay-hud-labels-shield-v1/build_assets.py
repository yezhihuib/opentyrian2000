#!/usr/bin/env python3
"""Reproduce the fixed-label/V2-shield trial art without game data or captures.

Canonical pixels: RGBA8, straight alpha, top-to-bottom row-major, opaque alpha.
Only this script's directory is written. See README.md for assembly and provenance.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import PIL

ROOT = Path(__file__).resolve().parent
DENSITY = 4
H = 32
CHANNEL = (270, 137, 279, 195)
PIC3_INDEX_FNV1A64 = 0x14c1441f3d5dc0e2  # Required source signature supplied by integrator.
NORMAL_PALETTE_RGB_FNV1A64 = 0x5e80e83992be2927
RESOURCE_NAME = 'gameplay-hud-components-v1.hda' 
LABELS = [
    ('FRONT', (285, 5, 309, 10), [('F', 0, 4), ('R', 5, 4), ('O', 10, 4), ('N', 15, 4), ('T', 20, 4)]),
    ('GUN_front', (285, 11, 299, 16), [('G', 0, 4), ('U', 5, 4), ('N', 10, 4)]),
    ('REAR', (285, 26, 303, 31), [('R', 0, 4), ('E', 5, 3), ('A', 9, 4), ('R', 14, 4)]),
    ('GUN_rear', (285, 32, 299, 37), [('G', 0, 4), ('U', 5, 4), ('N', 10, 4)]),
]
GLYPHS = {
    'F': [[(.38,4.62),(.38,.38),(3.62,.38)],[(.38,2.45),(2.9,2.45)]],
    'R': [[(.38,4.62),(.38,.38),(2.98,.38),(3.62,1.02),(3.62,1.94),(2.98,2.55),(.38,2.55)],[(2.05,2.55),(3.62,4.62)]],
    'O': [[(1.02,.38),(2.98,.38),(3.62,1.02),(3.62,3.98),(2.98,4.62),(1.02,4.62),(.38,3.98),(.38,1.02),(1.02,.38)]],
    'N': [[(.38,4.62),(.38,.38),(3.62,4.62),(3.62,.38)]],
    'T': [[(.38,.38),(3.62,.38)],[(2,.38),(2,4.62)]],
    'G': [[(3.62,1.03),(2.98,.38),(1.02,.38),(.38,1.02),(.38,3.98),(1.02,4.62),(2.98,4.62),(3.62,3.98),(3.62,2.85),(2.35,2.85)]],
    'U': [[(.38,.38),(.38,3.98),(1.02,4.62),(2.98,4.62),(3.62,3.98),(3.62,.38)]],
    'E': [[(3.62,.38),(.38,.38),(.38,4.62),(3.62,4.62)],[(.38,2.5),(3.0,2.5)]],
    'A': [[(.38,4.62),(.38,1.02),(1.02,.38),(2.98,.38),(3.62,1.02),(3.62,4.62)],[(.38,2.7),(3.62,2.7)]],
}
# Fixed authored palette-role RGB, from the read-only source audit. No PIC read.
PALETTE_RGB = {
    146: (0,0,81), 147: (0,0,109), 148: (0,0,138), 149: (0,0,170),
    150: (0,0,199), 151: (8,16,207), 152: (20,40,219), 153: (28,60,227),
    154: (40,81,235), 155: (52,105,247), 156: (73,134,243),
    157: (89,158,239), 158: (105,174,235), 159: (121,190,231),
    68: (85,28,16), 0: (0,0,0),
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def fnv1a64(data):
    """Standard FNV-1a64; unsigned 64-bit result, 16 lowercase hex digits."""
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'{value:016x}'


def word_tile(box, chars):
    width = box[2] - box[0]
    mask = Image.new('L', (width * H, 5 * H))
    draw = ImageDraw.Draw(mask)
    for char, x, glyph_width in chars:
        for line in GLYPHS[char]:
            points = [(x + px * glyph_width / 4, py) for px, py in line]
            draw.line([(round(px * H), round(py * H)) for px, py in points],
                      fill=255, width=round(.72 * H), joint='curve')
    coverage = np.asarray(mask, dtype=float) / 255
    halo = np.asarray(mask.filter(ImageFilter.GaussianBlur(.18 * H)), dtype=float) / 255
    yy = np.linspace(0, 1, 5 * H)[:, None, None]
    green = np.array([8,182,20]) * (1 - yy) + np.array([0,125,0]) * yy
    rgb = np.maximum(coverage[:, :, None] * green,
                     halo[:, :, None] * np.array([0,42,3]))
    return Image.fromarray(np.uint8(np.clip(rgb, 0, 255))).resize(
        (width * DENSITY, 5 * DENSITY), Image.Resampling.BOX).convert('RGBA')


def shield_band(palette_role):
    """The unmodified V2 scalar-luminance recipe, sampled at exact 4x pixels."""
    source = np.array(PALETTE_RGB[palette_role], dtype=float)
    x = (np.arange(9 * H) + .5) / H
    xf = np.interp(x, [0,.20,.52,.85,1.30,2.60,6.45,7.8,8.5,8.8,9],
                   [.50,.69,1.02,1.16,1.11,1.01,.97,.84,.65,.52,.48])
    y = (np.arange(2 * H) + .5) / H
    yf = np.interp(y, [0,.13,.36,1.48,1.67,1.83,2],
                   [1.15,1.11,1.02,.99,.90,.52,.44])
    peak = float(source.max())
    luminance_peak = 255 * (peak / 255) ** .70
    body = source * (luminance_peak / peak)
    factor = xf[None, :] * yf[:, None]
    factor = np.minimum(factor, 250 / body.max())
    band = body[None, None, :] * factor[:, :, None]
    return Image.fromarray(np.uint8(np.clip(band, 0, 255))).resize(
        (36, 8), Image.Resampling.BOX).convert('RGBA')


def assemble_shield(S, M, bands, track, marker, *, active=True):
    """A display event, not a simulation: inactive is distinct from active S=0.

    active=False represents a wipe-only/inactive event and returns the blank track.
    There is no inference of event activity or baseline presence from S alone.
    """
    if type(active) is not bool:
        raise ValueError('active must be a bool')
    if type(S) is not int or type(M) is not int or not 0 <= S <= M <= 28:
        raise ValueError('S and M must be integers satisfying 0 <= S <= M <= 28')
    result = track.copy()
    if not active:
        return result
    for z in range(S + 1):
        role = 146 + max(0, (z - 1) // 2)
        result.paste(bands[role], (0, (193 - 2 * z - CHANNEL[1]) * DENSITY))
    if S != M:
        result.paste(marker, (0, (193 - 2 * M - CHANNEL[1]) * DENSITY))
    return result


def write_tile(filename, image, **semantic):
    assert image.mode == 'RGBA'
    assert image.getextrema()[3] == (255, 255)
    path = ROOT / 'tiles' / filename
    image.save(path, format='PNG', compress_level=9, optimize=False)
    decoded = image.tobytes()
    encoded = path.read_bytes()
    return {
        'path': str(path.relative_to(ROOT)), 'format': 'PNG', 'mode': 'RGBA',
        'width': image.width, 'height': image.height, 'alpha_min': 255, 'alpha_max': 255,
        'decoded_bytes': len(decoded), 'file_bytes': len(encoded),
        'decoded_rgba_sha256': sha256(decoded), 'decoded_rgba_fnv1a64': fnv1a64(decoded),
        'file_sha256': sha256(encoded), 'file_fnv1a64': fnv1a64(encoded), **semantic,
    }


def main():
    # A frozen art toolchain keeps rasterization and PNG encoding reproducible.
    if (PIL.__version__, np.__version__) != ('12.3.0', '2.3.5'):
        raise SystemExit('Use Pillow==12.3.0 and numpy==2.3.5 (requirements.txt).')
    assert fnv1a64(b'') == 'cbf29ce484222325'
    assert fnv1a64(b'a') == 'af63dc4c8601ec8c'
    assert fnv1a64(b'foobar') == '85944171f73967e8'
    provenance = json.loads((ROOT / 'provenance.json').read_text())
    (ROOT / 'tiles').mkdir(exist_ok=True)
    tiles = []
    labels = {}
    checks = []
    for name, box, chars in LABELS:
        image = word_tile(box, chars)
        expected = provenance['expected_labels'][name]
        assert sha256(image.tobytes()) == expected['decoded_rgba_sha256'], name
        labels[name] = image
        tiles.append(write_tile(f'label-{name}-4x.png', image, kind='fixed_label',
                                label=name, logical_rect_half_open=list(box)))
        checks.append({'kind': 'frozen_label', 'label': name, 'source_rgba_byte_exact': True})
    bands = {}
    for role in range(146, 160):
        bands[role] = shield_band(role)
        tiles.append(write_tile(f'shield-band-role{role}-4x.png', bands[role],
                                kind='shield_band', palette_role=role,
                                palette_rgb=list(PALETTE_RGB[role]), logical_size=[9,2]))
    track = Image.new('RGBA', (36,232), (*PALETTE_RGB[0],255))
    marker = Image.new('RGBA', (36,4), (*PALETTE_RGB[68],255))
    tiles.append(write_tile('shield-track-4x.png', track, kind='shield_track',
                            palette_role=0, logical_rect_half_open=list(CHANNEL)))
    tiles.append(write_tile('shield-capacity-marker-4x.png', marker, kind='shield_capacity_marker',
                            palette_role=68, palette_rgb=list(PALETTE_RGB[68]), logical_size=[9,1]))
    # Exactly the three supplied M10 fixture crops; no capture or state sweeps.
    for fixture in provenance['expected_m10_fixtures']:
        assembled = assemble_shield(fixture['S'], fixture['M'], bands, track, marker)
        decoded = assembled.tobytes()
        assert sha256(decoded) == fixture['shield_crop_decoded_rgba_sha256'], fixture
        assert fnv1a64(decoded) == fixture['shield_crop_decoded_rgba_fnv1a64'], fixture
        checks.append({'kind': 'supplied_m10_fixture', 'S': fixture['S'], 'M': fixture['M'],
                       'source': fixture['source'], 'shield_rgba_byte_exact': True,
                       'source_labels_rgba_byte_exact': fixture['labels_rgba_byte_exact'],
                       'assembled_decoded_rgba_sha256': sha256(decoded),
                       'assembled_decoded_rgba_fnv1a64': fnv1a64(decoded)})
    # One event distinction, not an additional visual fixture or sweep.
    active_zero = assemble_shield(0, 0, bands, track, marker)
    wiped_zero = assemble_shield(0, 0, bands, track, marker, active=False)
    assert wiped_zero.tobytes() == track.tobytes()
    assert active_zero.tobytes() != wiped_zero.tobytes()
    assert active_zero.crop((0,224,36,232)).tobytes() == bands[146].tobytes()
    assert sum((b[2]-b[0])*(b[3]-b[1]) for _,b,_ in LABELS) == 350
    assert len(tiles) == 20
    label_payload = b''.join(labels[name].tobytes() for name, _, _ in LABELS)
    band_payload = b''.join(bands[role].tobytes() for role in range(146, 160))
    assert len(label_payload) == 22400 and len(band_payload) == 16128
    assert fnv1a64(label_payload) == 'c24e8ce447f9f0e8'
    assert fnv1a64(band_payload) == '20b6e884fe4a23ce'
    header = struct.pack('<4s7I4Q', b'HUC1', 1, 4, 4, 22400, 14, 36, 8,
                         PIC3_INDEX_FNV1A64, int(fnv1a64(label_payload), 16),
                         int(fnv1a64(band_payload), 16), NORMAL_PALETTE_RGB_FNV1A64)
    assert len(header) == 64
    resource = header + label_payload + band_payload
    assert len(resource) == 38592
    (ROOT / RESOURCE_NAME).write_bytes(resource)
    resource_proof = {
        'path': RESOURCE_NAME, 'magic': 'HUC1', 'version': 1, 'file_bytes': len(resource),
        'file_sha256': sha256(resource), 'file_fnv1a64': fnv1a64(resource),
        'endianness': 'little', 'header_bytes': 64, 'header_struct': '<4s7I4Q',
        'PIC3_index_fnv1a64': f'{PIC3_INDEX_FNV1A64:016x}',
        'normal_palette_RGB_fnv1a64': f'{NORMAL_PALETTE_RGB_FNV1A64:016x}',
        'label_payload': {'offset': 64, 'bytes': 22400,
                          'decoded_rgba_sha256': sha256(label_payload),
                          'decoded_rgba_fnv1a64': fnv1a64(label_payload),
                          'order': [name for name, _, _ in LABELS]},
        'band_payload': {'offset': 22464, 'bytes': 16128,
                         'decoded_rgba_sha256': sha256(band_payload),
                         'decoded_rgba_fnv1a64': fnv1a64(band_payload),
                         'role_order': list(range(146, 160))},
        'track_and_marker': 'not included; runtime retains original indexed black/marker output',
        'density8': 'exact nearest-neighbor 2x replication of each 4x pixel in both axes',
    }
    manifest = {
        'schema': 'generated-art-manifest-v1',
        'status': 'FROZEN_GENERATED_ART_FOR_EXPLICITLY_APPROVED_TRIAL',
        'resource_format_binding': 'HUC1, exact integrator-supplied 64-byte header and ordered RGBA payload',
        'resource': resource_proof,
        'density': DENSITY, 'pixel_format': 'RGBA8', 'alpha': '255 everywhere, including black',
        'decoded_hash_serialization': 'top-to-bottom, left-to-right, row-major R,G,B,A bytes; no stride padding',
        'fnv1a64': {'variant': 'FNV-1a', 'offset_basis_hex': 'cbf29ce484222325',
                    'prime_hex': '00000100000001b3', 'arithmetic': 'unsigned modulo 2^64',
                    'encoding': '16 lowercase hex digits, numeric value, not byte-swapped'},
        'toolchain': {'python': sys.version.split()[0], 'Pillow': PIL.__version__, 'numpy': np.__version__},
        'reproducer_sha256': sha256(Path(__file__).read_bytes()),
        'provenance_sha256': sha256((ROOT / 'provenance.json').read_bytes()),
        'label_scope_logical_pixels': 350,
        'label_source_audit_ink_pixels': 215, 'label_source_audit_black_pixels': 135,
        'shield_channel_half_open': list(CHANNEL),
        'shield_assembly': {
            'bounds': 'integer 0 <= S <= M <= 28; reject other values',
            'event_activity': 'explicit active draw versus wipe-only inactive; never derive from S',
            'inactive': 'blank black track, no band and no marker',
            'active': 'paste track, then z=0..S inclusive in original draw order, then marker if S!=M',
            'band_role': '146 + max(0, floor((z-1)/2))',
            'band_global_logical_rect': '[270,193-2*z,279,195-2*z)',
            'band_tile_local_4x_xy': '[0,4*(56-2*z)]',
            'marker_global_logical_rect': '[270,193-2*M,279,194-2*M)',
            'marker_tile_local_4x_xy': '[0,4*(56-2*M)]',
            'no_capacity_normalization': True,
            'active_S0_M0': 'one role146 baseline at local y224..231 inclusive, no marker',
            'active_S28_M28': '29 bands cover all 232 rows; role159 is top band; no marker',
        },
        'provenance': provenance,
        'validation': {'checks': checks, 'opaque_tiles': len(tiles), 's0_wipe_is_distinct': True,
                       'bounded_fixture_count': 3, 'test_or_capture_sweep': False},
        'tiles': tiles,
    }
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'tiles': len(tiles), 'labels_logical_pixels': 350,
                      'M10_fixture_matches': 3, 's0_wipe_distinct': True,
                      'resource_sha256': sha256(resource),
                      'manifest_sha256': sha256((ROOT / 'manifest.json').read_bytes())}, indent=2))


if __name__ == '__main__':
    main()
