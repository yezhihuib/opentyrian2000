#!/usr/bin/env python3
"""Rebuild only reviewed 182/183 density8 PNG/RGBA/HDR1 from accepted front PNGs.

Python 3 and Pillow are required. Reads no original-game data, masks or HDA.
Both destinations must be fresh and separate. No resampling or compositing.
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


def verify_mapping(source, output):
    width, height = 96, 112
    expected = bytearray(len(output))
    for y in range(height):
        for x in range(width):
            src = 4 * (y * width + x)
            dst = 4 * ((height - 1 - y) * width + x)
            expected[dst:dst + 4] = source[src:src + 4]
    require(bytes(expected) == output, 'Exact whole-canvas mapping differs')
    require(stats(source) == stats(output), 'Full-density energy or alpha changed')
    return {
        'full_RGBA_coordinate_mapping_equal': True,
        'mapped_source_samples': width * height,
        'clipped_source_samples': 0,
        'all_source_RGBA_samples_preserved': True,
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
    require([(r['accepted_source_id'], r['source_id'], r['density'], r['key'])
             for r in pins['resources']] == [(163, 182, 8, 1310182), (164, 183, 8, 1310183)],
            'Only accepted 163/164 to reviewed 182/183 density8 are supported')
    art_files, hda_files, results = {}, {}, []
    for row in pins['resources']:
        target, accepted = row['source_id'], row['accepted_source_id']
        source_name = f'bullet-{accepted}-8.png'
        require(row['source_png_repo_path'] ==
                'assets/hd/artwork/player-front-multi-eight-v1/output/' + source_name,
                'Accepted source path mismatch')
        source_png = (source / source_name).read_bytes()
        require(sha(source_png) == row['source_png_sha256'], 'Accepted PNG pin mismatch')
        with Image.open(io.BytesIO(source_png)) as image:
            require(image.mode == 'RGBA' and image.size == (96, 112),
                    'Accepted source format mismatch')
            source_raw = image.tobytes()
            require(sha(source_raw) == row['source_rgba_sha256'], 'Accepted RGBA pin mismatch')
            transformed = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        raw = transformed.tobytes()
        checks = verify_mapping(source_raw, raw)
        encoded = io.BytesIO()
        transformed.save(encoded, format='PNG', compress_level=9, optimize=False)
        png = encoded.getvalue()
        hda = struct.pack('<4s6I', b'HDR1', row['key'], 8, 12, 14, 0, 0) + raw
        for kind, data in [('png', png), ('rgba', raw), ('hda', hda)]:
            require(sha(data) == row[f'{kind}_sha256'], f'Approved {kind} pin mismatch')
        require(fnv(raw) == row['rgba_fnv1a64'], 'Approved FNV pin mismatch')
        stem = f'rear-multi-p4-{target}-8'
        art_files[stem + '.png'], art_files[stem + '.rgba'] = png, raw
        hda_files[f'rear-multicannon-p1-bank8-{target}-8.hda'] = hda
        results.append({**row, 'checks': checks})
    contract = {
        'schema': 'rear-multicannon-p4-mode2-down-diagonals-transform-v1',
        'scope': pins['scope'],
        'reviewed_export_sha256': pins['reviewed_export_sha256'],
        'source_family': 'player-front-multi-eight-v1/output',
        'logical_size': [12, 14], 'anchor': [0, 0],
        'transform': 'whole_canvas_flip_y', 'translation_logical_xy': [0, 0],
        'constraints': {'new_generation': False, 'new_drawing': False,
                        'normalization': False, 'resampling': False,
                        'filtering': False, 'blur': False, 'alpha_compositing': False,
                        'density4_creation': False, 'density_upward_fallback': False},
        'resources': results,
    }
    art_files['transform-contract.json'] = (json.dumps(contract, indent=2) + '\n').encode()
    output.mkdir(parents=True)
    hda_output.mkdir(parents=True)
    for name, data in art_files.items():
        (output / name).write_bytes(data)
    for name, data in hda_files.items():
        (hda_output / name).write_bytes(data)
    print('PASS: reviewed 182/183 density8 PNG/RGBA/HDR1; exact whole-canvas flip and energy preservation.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path,
                        default=ROOT.parent / 'player-front-multi-eight-v1/output')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hda-output', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output, args.hda_output)
