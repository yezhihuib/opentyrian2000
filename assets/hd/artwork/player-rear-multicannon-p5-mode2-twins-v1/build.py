#!/usr/bin/env python3
"""Rebuild reviewed lower-over-upper twins from pinned generated R2 PNG/RGBA.

Python 3 standard library only. No original data, masks, palettes or captures.
Both output directories must be fresh, separate and outside the source tree.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parent
SOURCE_FAMILY = 'assets/hd/artwork/player-rear-multicannon-p1-six-v1/output'


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


def half_up(numerator, denominator):
    return (2 * numerator + denominator) // (2 * denominator)


def png_bytes(raw, width, height):
    # Same deterministic no-filter, stored-DEFLATE encoding as reviewed preview.
    scanlines = b''.join(b'\0' + raw[y * width * 4:(y + 1) * width * 4]
                         for y in range(height))
    stream = bytearray(b'\x78\x01')
    for position in range(0, len(scanlines), 65535):
        block = scanlines[position:position + 65535]
        stream += bytes([int(position + len(block) == len(scanlines))])
        stream += struct.pack('<HH', len(block), 65535 - len(block)) + block
    stream += struct.pack('>I', zlib.adler32(scanlines) & 0xffffffff)

    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))

    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>2I5B', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', bytes(stream)) + chunk(b'IEND', b''))


def compose_lower_over_upper(source, density):
    row_bytes, height = 12 * density * 4, 14 * density
    shift = row_bytes * 4 * density
    require(not any(source[-shift:]), 'Translation would clip nonzero RGBA')
    lower = bytes(shift) + source[:-shift]
    result = bytearray(len(source))
    overlaps = 0
    nonoverlaps = 0
    for offset in range(0, len(source), 4):
        back, front = source[offset:offset + 4], lower[offset:offset + 4]
        ab, af = back[3], front[3]
        if not af:
            pixel = back
        elif not ab:
            pixel = front
        else:
            overlaps += 1
            numerator = 255 * af + ab * (255 - af)
            pixel = bytes([half_up(front[c] * af * 255 + back[c] * ab * (255 - af),
                                   numerator) for c in range(3)]
                          + [half_up(numerator, 255)])
        if bool(ab) != bool(af):
            nonoverlaps += 1
            require(pixel == (back if ab else front), 'Nonoverlap sample changed')
        require(bool(pixel[3]) == bool(ab or af), 'Support union changed')
        result[offset:offset + 4] = pixel
    require(len(source) == row_bytes * height and overlaps == 5, 'Overlap geometry mismatch')
    return bytes(result), {
        'overlap_sample_count': overlaps,
        'nonoverlap_supported_samples_preserved_exact': nonoverlaps,
        'clipped_nonzero_RGBA_samples': 0,
        'output_support_equals_union': True,
        'alpha_sum': sum(result[3::4]),
        'alpha_delta_vs_two_copies': sum(result[3::4]) - 2 * sum(source[3::4]),
        'premultiplied_RGB_delta_vs_two_copies': [
            sum(result[o + c] * result[o + 3] - 2 * source[o + c] * source[o + 3]
                for o in range(0, len(source), 4)) for c in range(3)],
    }


def build(source, output, hda_output):
    require(not output.exists() and not hda_output.exists(), 'Both output directories must not exist')
    source_abs, out_abs, hda_abs = source.resolve(), output.resolve(), hda_output.resolve()
    require(out_abs != hda_abs and out_abs not in hda_abs.parents and hda_abs not in out_abs.parents,
            'Output directories must be separate')
    require(all(p != source_abs and source_abs not in p.parents for p in [out_abs, hda_abs]),
            'Output directories must be outside source directory')
    pins = json.loads((ROOT / 'inputs.json').read_text())
    require(pins['selected_order'] == 'lower_over_upper', 'Only selected layer order is supported')
    require([(r['accepted_source_id'], r['source_id'], r['density'], r['key'])
             for r in pins['resources']] == [(281, 277, 4, 1310277), (281, 277, 8, 1310277),
                                            (282, 278, 4, 1310278), (282, 278, 8, 1310278)],
            'Only reviewed 277/278 density4/8 twins are supported')
    art_files, hda_files, results = {}, {}, []
    for row in pins['resources']:
        target, accepted, density = row['source_id'], row['accepted_source_id'], row['density']
        stem = f'rear-multi-{accepted}-{density}'
        for extension in ['png', 'rgba']:
            require(row[f'source_{extension}_repo_path'] == f'{SOURCE_FAMILY}/{stem}.{extension}',
                    'Accepted source path mismatch')
        source_png = (source / (stem + '.png')).read_bytes()
        source_rgba = (source / (stem + '.rgba')).read_bytes()
        require(sha(source_png) == row['source_png_sha256'], 'Accepted PNG pin mismatch')
        require(sha(source_rgba) == row['source_rgba_sha256'], 'Accepted RGBA pin mismatch')
        require(len(source_rgba) == 12 * 14 * density * density * 4, 'Accepted RGBA size mismatch')
        require(all(source_rgba[o + 3] or not any(source_rgba[o:o + 4])
                    for o in range(0, len(source_rgba), 4)), 'Hidden zero-alpha RGB found')
        raw, checks = compose_lower_over_upper(source_rgba, density)
        png = png_bytes(raw, 12 * density, 14 * density)
        hda = struct.pack('<4s6I', b'HDR1', row['key'], density, 12, 14, 0, 0) + raw
        for kind, data in [('png', png), ('rgba', raw), ('hda', hda)]:
            require(sha(data) == row[kind + '_sha256'], f'Approved {kind} pin mismatch')
        require(fnv(raw) == row['rgba_fnv1a64'], 'Approved FNV pin mismatch')
        out_stem = f'rear-multi-{target}-{density}-lower_over_upper'
        art_files[out_stem + '.png'], art_files[out_stem + '.rgba'] = png, raw
        hda_files[f'rear-multicannon-p1-bank8-{target}-{density}.hda'] = hda
        results.append({**row, 'checks': checks})
    contract = {
        'schema': 'rear-multicannon-p5-mode2-twins-composite-v1',
        'scope': pins['scope'], 'runtime_qualification': 'DIAGNOSTIC_QUALIFICATION_RECORDED_SEPARATELY',
        'reviewed_export_sha256': pins['reviewed_export_sha256'],
        'selected_order': 'lower_over_upper', 'logical_size': [12, 14], 'anchor': [0, 0],
        'layer_order_back_to_front_logical_xy': [[0, 0], [0, 4]],
        'operation': 'Exact rational Porter-Duff source-over, encoded RGB space; half-up quantize straight RGB and alpha independently once.',
        'alpha_formula': 'N=255*Af+Ab*(255-Af); Aout=round_half_up(N/255)',
        'RGB_formula': 'Cout=round_half_up((Cf*Af*255+Cb*Ab*(255-Af))/N)',
        'constraints': {'new_generation': False, 'resampling': False, 'filtering': False,
                        'blur': False, 'recoloring': False, 'normalization': False,
                        'original_game_inputs': False, 'comparison_order_resource': False},
        'resources': results,
    }
    art_files['composite-contract.json'] = (json.dumps(contract, indent=2) + '\n').encode()
    # All input and generated-byte checks finish before either output is created.
    output.mkdir(parents=True)
    hda_output.mkdir(parents=True)
    for name, data in art_files.items():
        (output / name).write_bytes(data)
    for name, data in hda_files.items():
        (hda_output / name).write_bytes(data)
    print('PASS: four reviewed lower-over-upper PNG/RGBA/HDR1 twins, no original-game inputs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent / 'player-rear-multicannon-p1-six-v1/output')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hda-output', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output, args.hda_output)
