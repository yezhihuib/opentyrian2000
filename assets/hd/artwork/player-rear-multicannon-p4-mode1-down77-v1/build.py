#!/usr/bin/env python3
"""Rebuild only approved down77 PNG/RGBA/HDR1 bytes from accepted R2 ID1.

Python 3 and Pillow are required. No original-game data is read. Both output
locations must be fresh directories. No resampling or alpha compositing occurs.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fnv(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return f'0x{value:016x}'


def stats(raw):
    return {
        'alpha_sum': sum(raw[3::4]),
        'alpha_nonzero_samples': sum(a > 0 for a in raw[3::4]),
        'fractional_alpha_samples': sum(0 < a < 255 for a in raw[3::4]),
        'premultiplied_RGB_numerators': [
            sum(raw[p + c] * raw[p + 3] for p in range(0, len(raw), 4))
            for c in range(3)],
    }


def verify_mapping(source, output, density):
    w, h = 12 * density, 14 * density
    expected = bytearray(len(output))
    clipped = mapped = 0
    for y in range(h):
        for x in range(w):
            pixel = source[4 * (y * w + x):4 * (y * w + x + 1)]
            xx, yy = h - 1 - y - 2 * density, x + 2 * density
            if 0 <= xx < w and 0 <= yy < h:
                start = 4 * (yy * w + xx)
                expected[start:start + 4] = pixel
                mapped += 1
            else:
                require(pixel == b'\0\0\0\0', 'Nonzero RGBA would be clipped')
                clipped += 1
    require(bytes(expected) == output, 'Exact coordinate mapping differs')
    require(stats(source) == stats(output), 'Full-density energy or alpha changed')
    return {
        'full_RGBA_coordinate_mapping_equal': True,
        'mapped_source_samples': mapped,
        'clipped_transparent_black_samples': clipped,
        'clipped_nonzero_RGBA_samples': 0,
        'all_supported_source_RGBA_samples_preserved': True,
        'full_density_alpha_RGB_energy_exact': True,
        'preserved_stats': stats(output),
    }


def build(source, output, hda_output):
    require(not output.exists() and not hda_output.exists(),
            'Both output directories must not exist')
    out_abs, hda_abs = output.resolve(), hda_output.resolve()
    require(out_abs != hda_abs and out_abs not in hda_abs.parents
            and hda_abs not in out_abs.parents, 'Output directories must be separate')
    pins = json.loads((ROOT / 'inputs.json').read_text())
    require([row['density'] for row in pins['resources']] == [4, 8],
            'Only independently pinned density4 and density8 are supported')
    art_files, hda_files, results = {}, {}, []
    for row in pins['resources']:
        d = row['density']
        require(row['accepted_source_id'] == 1 and row['source_id'] == 77
                and row['key'] == 1310077, 'Only accepted ID1 to down77 is supported')
        png_name, rgba_name = f'rear-multi-1-{d}.png', f'rear-multi-1-{d}.rgba'
        source_png = (source / png_name).read_bytes()
        source_raw = (source / rgba_name).read_bytes()
        require(sha(source_png) == row['source_png_sha256'], 'Accepted PNG pin mismatch')
        require(sha(source_raw) == row['source_rgba_sha256'], 'Accepted RGBA pin mismatch')
        with Image.open(io.BytesIO(source_png)) as image:
            require(image.mode == 'RGBA' and image.size == (12 * d, 14 * d),
                    'Accepted source format mismatch')
            require(image.tobytes() == source_raw, 'Accepted PNG/RGBA mismatch')
            rotated = image.transpose(Image.Transpose.ROTATE_270)
        transformed = Image.new('RGBA', (12 * d, 14 * d), (0, 0, 0, 0))
        # No mask: copies exact straight RGBA, never alpha-composites.
        transformed.paste(rotated, (-2 * d, 2 * d))
        raw = transformed.tobytes()
        checks = verify_mapping(source_raw, raw, d)
        encoded = io.BytesIO()
        transformed.save(encoded, format='PNG', compress_level=9, optimize=False)
        png = encoded.getvalue()
        hda = struct.pack('<4s6I', b'HDR1', 1310077, d, 12, 14, 0, 0) + raw
        for kind, data in [('png', png), ('rgba', raw), ('hda', hda)]:
            require(sha(data) == row[f'{kind}_sha256'], f'Approved {kind} pin mismatch')
        require(fnv(raw) == row['rgba_fnv1a64'], 'Approved FNV pin mismatch')
        stem = f'rear-multi-p4-77-{d}'
        art_files[stem + '.png'], art_files[stem + '.rgba'] = png, raw
        hda_files[f'rear-multicannon-p1-bank8-77-{d}.hda'] = hda
        results.append({'density': d, 'checks': checks, **row})
    contract = {
        'schema': 'rear-multicannon-p4-mode1-down77-transform-v1',
        'scope': pins['scope'],
        'reviewed_export_sha256': pins['reviewed_export_sha256'],
        'source_family': 'player-rear-multicannon-p1-six-v1/output',
        'logical_size': [12, 14], 'anchor': [0, 0],
        'transform': 'clockwise90 then translate logical (-2,+2)',
        'constraints': {'new_generation': False, 'new_drawing': False,
                        'normalization': False, 'resampling': False,
                        'filtering': False, 'blur': False, 'alpha_compositing': False},
        'resources': results,
    }
    art_files['transform-contract.json'] = (json.dumps(contract, indent=2) + '\n').encode()
    output.mkdir(parents=True)
    hda_output.mkdir(parents=True)
    for name, data in art_files.items():
        (output / name).write_bytes(data)
    for name, data in hda_files.items():
        (hda_output / name).write_bytes(data)
    print('PASS: two pinned down77 PNG/RGBA/HDR1 resources; exact mapping and no covered clipping.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path,
                        default=ROOT.parent / 'player-rear-multicannon-p1-six-v1/output')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hda-output', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output, args.hda_output)
