#!/usr/bin/env python3
"""Exact component reuse only. Reads accepted generated art, never game data.

Usage: python3 build_composites.py ACCEPTED_ART_DIRECTORY NEW_OUTPUT_DIRECTORY
The output directory must not exist. No source file is changed. Standard library
only; canonical PNG uses explicit stored DEFLATE blocks for version-independent
bytes, without renderer, color conversion, resampling, or lossy encoding.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys
import zlib

sha = lambda b: hashlib.sha256(b).hexdigest()
SPECS = [(2, 1, [(False, -2), (True, 2)]),
         (40, 39, [(True, -4), (False, 4)])]


def fnv(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'{value:016x}'


def canonical_png(data, w, h):
    rows = b''.join(b'\0' + data[y*w*4:(y+1)*w*4] for y in range(h))
    stream = bytearray(b'\x78\x01')
    for start in range(0, len(rows), 65535):
        block = rows[start:start+65535]
        stream += bytes([int(start+len(block) == len(rows))])
        stream += struct.pack('<HH', len(block), 65535-len(block)) + block
    stream += struct.pack('>I', zlib.adler32(rows) & 0xffffffff)
    def chunk(kind, body):
        return (struct.pack('>I', len(body)) + kind + body +
                struct.pack('>I', zlib.crc32(kind+body) & 0xffffffff))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', bytes(stream)) + chunk(b'IEND', b''))


def transform(data, d, flip_y, dy):
    w, h = 12*d, 14*d
    out = bytearray(len(data))
    clipped = 0
    for y in range(h):
        yy = (h-1-y if flip_y else y) + dy*d
        row = data[y*w*4:(y+1)*w*4]
        if 0 <= yy < h:
            out[yy*w*4:(yy+1)*w*4] = row
        else:
            clipped += sum(a != 0 for a in row[3::4])
    assert clipped == 0, 'Never discard an occupied source sample'
    return bytes(out)


def stats(data, d):
    w, h = 12*d, 14*d
    points = [p for p in range(w*h) if data[p*4+3]]
    alpha = data[3::4]
    bounds = [min(p % w for p in points), min(p // w for p in points),
              max(p % w for p in points)+1, max(p // w for p in points)+1]
    energy = [sum(data[p*4+c]*data[p*4+3] for p in points) for c in range(3)]
    return {'supported_samples': len(points), 'bounds_exclusive': bounds,
            'logical_bounds_exclusive': [v/d for v in bounds],
            'opaque_samples': sum(a == 255 for a in alpha),
            'fractional_alpha_samples': sum(0 < a < 255 for a in alpha),
            'alpha_sum': sum(alpha), 'premultiplied_RGB_numerators': energy,
            'premultiplied_luma_2126_7152_722_numerator':
                sum(v*c for v, c in zip(energy, [2126, 7152, 722])),
            'peak_straight_RGB': [max(data[p*4+c] for p in points) for c in range(3)],
            'peak_alpha': max(alpha)}


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    art, out = map(lambda s: Path(s).resolve(), sys.argv[1:])
    assert not out.exists(), 'Choose a fresh output directory'
    pins = json.loads(Path(__file__).with_name('accepted-component-pins.json').read_text())
    for path, expected in pins.items():
        assert sha((art/path).read_bytes()) == expected, path
    out.mkdir(parents=True)
    records = []
    for target, source, parts in SPECS:
        for d in [4, 8]:
            data = (art/f'output/rear-multi-{source}-{d}.rgba').read_bytes()
            assert len(data) == 12*14*d*d*4
            assert all(data[p:p+3] == b'\0\0\0' for p in range(0, len(data), 4)
                       if data[p+3] == 0)
            source_stats = stats(data, d)
            layers = [transform(data, d, flip, dy) for flip, dy in parts]
            result = bytearray(len(data))
            overlap = 0
            layer_records = []
            for n, (layer, (flip, dy)) in enumerate(zip(layers, parts)):
                for p in range(0, len(data), 4):
                    if layer[p+3]:
                        overlap += result[p+3] != 0
                        result[p:p+4] = layer[p:p+4]
                ls = stats(layer, d)
                for field in ['supported_samples', 'opaque_samples', 'fractional_alpha_samples',
                              'alpha_sum', 'premultiplied_RGB_numerators',
                              'premultiplied_luma_2126_7152_722_numerator',
                              'peak_straight_RGB', 'peak_alpha']:
                    assert ls[field] == source_stats[field], field
                stem = f'rear-multi-{target}-{d}-lobe-{n+1}'
                png = canonical_png(layer, 12*d, 14*d)
                (out/(stem+'.rgba')).write_bytes(layer)
                (out/(stem+'.png')).write_bytes(png)
                layer_records.append({'lobe': n+1, 'flip_y_full_canvas': flip,
                    'translation_logical_xy': [0, dy], 'translation_pixel_xy': [0, dy*d],
                    'rgba': stem+'.rgba', 'rgba_sha256': sha(layer),
                    'png': stem+'.png', 'png_sha256': sha(png),
                    'clipped_occupied_samples': 0, 'stats': ls,
                    'brightness_and_coverage_exactly_preserved_vs_component': True})
            assert overlap == 0, 'Composition requires disjoint alpha support'
            result = bytes(result)
            assert all(result[p:p+3] == b'\0\0\0' for p in range(0, len(result), 4)
                       if result[p+3] == 0)
            stem = f'rear-multi-{target}-{d}'
            png = canonical_png(result, 12*d, 14*d)
            (out/(stem+'.rgba')).write_bytes(result)
            (out/(stem+'.png')).write_bytes(png)
            gap = layer_records[1]['stats']['bounds_exclusive'][1] - layer_records[0]['stats']['bounds_exclusive'][3]
            assert gap == 2*d
            assert not any(result[(6*d*12*d)*4+3:(8*d*12*d)*4:4])
            records.append({'target_original_id': target, 'accepted_component_original_id': source,
                'density': d, 'size': [12*d, 14*d], 'logical_size': [12, 14], 'anchor': [0, 0],
                'source_rgba_sha256': sha(data), 'source_stats': source_stats,
                'rgba': stem+'.rgba', 'rgba_sha256': sha(result), 'rgba_fnv1a64': fnv(result),
                'png': stem+'.png', 'png_sha256': sha(png), 'stats': stats(result, d),
                'layers': layer_records, 'support_overlap_samples': overlap,
                'interlobe_gap_pixels': gap, 'interlobe_gap_logical': gap/d,
                'empty_central_logical_rows_half_open': [6, 8],
                'total_brightness_ratio_vs_single_component': 2,
                'per_lobe_brightness_ratio_vs_component': [1, 1]})
    contract = {'schema': 'rear-multi-p3-mode1-component-reuse-preview-v1',
        'status': 'Preview only. No production integration or publication.',
        'logical_size': [12, 14], 'anchor': [0, 0], 'densities': [4, 8],
        'accepted_component_file_pins': pins,
        'builder_sha256': sha(Path(__file__).read_bytes()),
        'source_provenance': 'Two independently authored accepted R2 lateral SVG masters; pinned RGBA is authoritative. No opposite-direction mirroring.',
        'transform_contract': 'Reflect the entire raster: y becomes 14*d-1-y; then translate by dy*d. Never crop/recenter/resample. Discarded canvas rows must be alpha zero.',
        'assembly_contract': 'Two disjoint supports. Exact copy of all four RGBA bytes at each supported sample; no color blend, coverage normalization, opacity increase, edge sharpening, halo, or new rasterization.',
        'transparent_rgb_contract': 'RGBA zero at every zero-alpha output sample.',
        'PNG_contract': 'RGBA8, filter0 each row, explicit RFC1950 stored RFC1951 blocks of up to65535 bytes; no metadata or color conversion.',
        'rebuild_inputs': 'Accepted generated artwork package only. No original source indices, masks, palettes, screenshots or game data.',
        'excluded': ['HDA IDs', 'resource bindings', 'production changes', 'runtime acceptance', 'other powers or families'],
        'outputs': records}
    (out/'transform-contract.json').write_text(json.dumps(contract, indent=2)+'\n')
    print('PASS: four exact derived RGBA/PNG proposals plus eight unchanged-coverage lobe layers.')


if __name__ == '__main__':
    main()
