#!/usr/bin/env python3
"""Reflect only pinned, accepted 277/278 composited RGBA into 296/297.

Python 3 standard library only. PNG/RGBA generated art is the entire input
allowlist. No original game data, palettes, masks, captures or components.
The output must be a fresh directory outside the source directory.
"""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parent
SIGNATURE = b'\x89PNG\r\n\x1a\n'


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


def png_bytes(raw, width, height):
    """Fixed no-filter, stored-DEFLATE encoding, independent of zlib version."""
    require(len(raw) == width * height * 4, 'RGBA dimensions mismatch')
    scan = b''.join(b'\0' + raw[y*width*4:(y+1)*width*4] for y in range(height))
    stream = bytearray(b'\x78\x01')
    for pos in range(0, len(scan), 65535):
        block = scan[pos:pos+65535]
        stream += bytes([int(pos+len(block) == len(scan))])
        stream += struct.pack('<HH', len(block), 65535-len(block)) + block
    stream += struct.pack('>I', zlib.adler32(scan) & 0xffffffff)
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff))
    return (SIGNATURE + chunk(b'IHDR', struct.pack('>2I5B', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', bytes(stream)) + chunk(b'IEND', b''))


def decode_png(data):
    """Strict decoder for the pinned no-filter 8-bit RGBA PNG input format."""
    require(data.startswith(SIGNATURE), 'PNG signature mismatch')
    pos, kinds, idat, size = 8, [], bytearray(), None
    while pos < len(data):
        require(pos+12 <= len(data), 'PNG truncated chunk')
        count = struct.unpack_from('>I', data, pos)[0]
        require(pos+12+count <= len(data), 'PNG truncated payload')
        kind = data[pos+4:pos+8]
        body = data[pos+8:pos+8+count]
        crc = struct.unpack_from('>I', data, pos+8+count)[0]
        require(zlib.crc32(kind+body) & 0xffffffff == crc, 'PNG CRC mismatch')
        kinds.append(kind)
        if kind == b'IHDR':
            require(len(kinds) == 1 and len(body) == 13, 'PNG invalid IHDR')
            width, height, depth, color, comp, filt, interlace = struct.unpack('>2I5B', body)
            require((depth, color, comp, filt, interlace) == (8, 6, 0, 0, 0), 'PNG format mismatch')
            size = width, height
        elif kind == b'IDAT':
            require(size is not None, 'PNG IDAT before IHDR')
            idat.extend(body)
        elif kind == b'IEND':
            require(not body and pos+12 == len(data), 'PNG trailing data')
        else:
            raise ValueError('Unexpected PNG chunk')
        pos += 12+count
    require(kinds == [b'IHDR', b'IDAT', b'IEND'], 'Unexpected PNG chunk sequence')
    dec = zlib.decompressobj()
    scan = dec.decompress(bytes(idat)) + dec.flush()
    require(dec.eof and not dec.unused_data and not dec.unconsumed_tail, 'PNG invalid DEFLATE stream')
    width, height = size
    stride = width*4+1
    require(len(scan) == stride*height, 'PNG decoded size mismatch')
    require(all(scan[y*stride] == 0 for y in range(height)), 'PNG nonzero filter')
    return width, height, b''.join(scan[y*stride+1:(y+1)*stride] for y in range(height))


def flip_y(raw, width, height):
    stride = width*4
    require(len(raw) == stride*height, 'Reflection dimensions mismatch')
    return b''.join(raw[y*stride:(y+1)*stride] for y in range(height-1, -1, -1))


def pixels(raw):
    return [tuple(raw[o:o+4]) for o in range(0, len(raw), 4)]


def metrics(raw, width, height):
    ps = pixels(raw)
    nonzero = [(i % width, i // width, p) for i, p in enumerate(ps) if p[3]]
    rgba_sums = [sum(p[c] for p in ps) for c in range(4)]
    premul = [sum(p[c]*p[3] for p in ps) for c in range(3)]
    return {
        'canvas_pixels': width*height,
        'nonzero_alpha_samples': len(nonzero),
        'zero_alpha_samples': width*height-len(nonzero),
        'zero_alpha_nonzero_rgb_samples': sum(not p[3] and any(p[:3]) for p in ps),
        'rgba_channel_sums': rgba_sums,
        'alpha_sum': rgba_sums[3],
        'premultiplied_RGB_C_times_A': premul,
        'weighted_luma_C_times_A_2126_7152_722': sum(a*b for a, b in zip(premul, [2126, 7152, 722])),
        'maximum_alpha': max(p[3] for p in ps),
        'nonzero_bounds_exclusive': [min(x for x, y, p in nonzero), min(y for x, y, p in nonzero),
                                      max(x for x, y, p in nonzero)+1, max(y for x, y, p in nonzero)+1],
    }


def native_sample(raw, density, scale):
    """Direct center-nearest authored -> native; no 1x intermediary."""
    width = 12*density
    return bytes(c for y in range(14*scale) for x in range(12*scale)
                 for c in raw[4*(((2*y+1)*density//(2*scale))*width+(2*x+1)*density//(2*scale)):
                              4*(((2*y+1)*density//(2*scale))*width+(2*x+1)*density//(2*scale))+4])


def build(source, output, hda_output):
    source, output, hda_output = source.resolve(), output.resolve(), hda_output.resolve()
    require(source.is_dir(), 'Source directory missing')
    require(not output.exists(), 'Output directory must be fresh')
    require(not hda_output.exists(), 'HDA output directory must be fresh')
    paths = [source, output, hda_output]
    require(all(a != b and a not in b.parents and b not in a.parents
                for i, a in enumerate(paths) for b in paths[i+1:]),
            'Source, output and HDA output directories must not overlap')
    spec = json.loads((ROOT/'inputs.json').read_text())
    require(spec['logical_size'] == [12, 14] and spec['anchor'] == [0, 0], 'Geometry changed')
    require([(r['accepted_id'], r['target_id'], r['density']) for r in spec['resources']]
            == [(277, 296, 4), (277, 296, 8), (278, 297, 4), (278, 297, 8)], 'Scope changed')
    output_pins = json.loads((ROOT/'outputs.json').read_text())
    require(set(output_pins) == {'296-4', '296-8', '297-4', '297-8'}, 'Output pin scope changed')
    pending, hda_pending, receipts = {}, {}, []
    for row in spec['resources']:
        accepted, target, density = row['accepted_id'], row['target_id'], row['density']
        stem = f'rear-multi-{accepted}-{density}-lower_over_upper'
        require(row['png_name'] == stem+'.png' and row['rgba_name'] == stem+'.rgba', 'Input name changed')
        source_png = (source/row['png_name']).read_bytes()
        raw = (source/row['rgba_name']).read_bytes()
        require(sha(source_png) == row['png_sha256'] and sha(raw) == row['rgba_sha256'], 'Input SHA256 mismatch')
        width, height, decoded = decode_png(source_png)
        require((width, height) == (12*density, 14*density) and decoded == raw, 'PNG/RGBA correspondence mismatch')
        reflected = flip_y(raw, width, height)
        require(flip_y(reflected, width, height) == raw, 'Reflection inverse mismatch')
        require(Counter(pixels(raw)) == Counter(pixels(reflected)), 'RGBA sample multiset changed')
        before, after = metrics(raw, width, height), metrics(reflected, width, height)
        invariant_keys = [key for key in before if key != 'nonzero_bounds_exclusive']
        require(all(before[key] == after[key] for key in invariant_keys), 'Preservation metric changed')
        target_bounds = ([0, 4*density, 11*density, 14*density] if target == 296
                         else [density, 4*density, 12*density, 14*density])
        require(after['nonzero_bounds_exclusive'] == target_bounds, 'Reflected bounds mismatch')
        png = png_bytes(reflected, width, height)
        require(decode_png(png) == (width, height, reflected), 'Generated PNG roundtrip mismatch')
        out_stem = f'rear-multi-{target}-{density}-flipY'
        hda = struct.pack('<4s6I', b'HDR1', 1310000+target, density, 12, 14, 0, 0) + reflected
        require(output_pins[f'{target}-{density}'] == {
            'png_sha256': sha(png), 'rgba_sha256': sha(reflected), 'rgba_fnv1a64': fnv(reflected),
            'hda_sha256': sha(hda)}, 'Expected output pin mismatch')
        pending[out_stem+'.png'], pending[out_stem+'.rgba'] = png, reflected
        hda_name = f'rear-multicannon-p1-bank8-{target}-{density}.hda'
        hda_pending[hda_name] = hda
        native = []
        for scale in (2, 4):
            a, b = native_sample(raw, density, scale), native_sample(reflected, density, scale)
            ma, mb = metrics(a, 12*scale, 14*scale), metrics(b, 12*scale, 14*scale)
            reflected_native = flip_y(a, 12*scale, 14*scale)
            native.append({
                'scale': scale, 'dimensions': [12*scale, 14*scale],
                'source_coordinates_x': [(2*x+1)*density//(2*scale) for x in range(12*scale)],
                'source_coordinates_y': [(2*y+1)*density//(2*scale) for y in range(14*scale)],
                'accepted_rgba_sha256': sha(a), 'target_rgba_sha256': sha(b),
                'accepted': ma, 'target': mb,
                'target_minus_accepted_alpha_sum': mb['alpha_sum']-ma['alpha_sum'],
                'target_minus_accepted_premultiplied_RGB_C_times_A': [b-a for a, b in zip(ma['premultiplied_RGB_C_times_A'], mb['premultiplied_RGB_C_times_A'])],
                'target_equals_flip_of_native_accepted': b == reflected_native,
                'RGBA_samples_different_vs_flip_of_native_accepted': sum(x != y for x, y in zip(pixels(b), pixels(reflected_native))),
            })
        receipts.append({**row, 'output_png': out_stem+'.png', 'output_rgba': out_stem+'.rgba',
                         'output_png_sha256': sha(png), 'output_rgba_sha256': sha(reflected),
                         'output_rgba_fnv1a64': fnv(reflected), 'canvas': [12, 14], 'anchor': [0, 0],
                         'hda_name': hda_name, 'hda_sha256': sha(hda), 'hda_bytes': len(hda),
                         'hda_header': {'magic': 'HDR1', 'role': 131, 'key': 1310000+target,
                                        'density': density, 'logical_size': [12, 14], 'anchor': [0, 0]},
                         'source_metrics': before, 'target_metrics': after,
                         'checks': {'PNG_matches_RGBA': True, 'every_RGBA_sample_preserved': True,
                                    'inverse_flip_recovers_exact_accepted_RGBA': True,
                                    'whole_canvas_sample_multiset_equal': True,
                                    'clipped_or_discarded_samples': 0, 'resampled_or_recolored_samples': 0,
                                    'full_density_alpha_sum_delta': 0,
                                    'full_density_premultiplied_RGB_delta': [0, 0, 0],
                                    'accepted_internal_composition_order_preserved': True}, 'native': native})
    receipt = {
        'schema': 'rear-multicannon-p7-mode1-reflection-preservation-v1',
        'status': 'OFFLINE_ART_REVIEW_ACCEPTED_RUNTIME_UNQUALIFIED',
        'operation': 'For all x,y: target(x,y)=accepted_composited(x,height-1-y).',
        'input_contract': 'Only the eight pinned accepted composited PNG/RGBA files.',
        'source_layer_semantics': 'The accepted lower_over_upper composite is reflected as one image. Its component overlap colors are preserved, not recomputed or reordered.',
        'logical_size': [12, 14], 'anchor': [0, 0],
        'nearest_sampling': 'floor((2*display_coordinate+1)*source_density/(2*display_scale))',
        'native_warning': 'Reflection swaps sampled Y residue classes when downsampling; full-density energy preservation does not promise identical native brightness. No compensation applied.',
        'production_modified': False, 'games_launched': False, 'original_data_read': False,
        'captures_read': False, 'HDA_resources_generated': True,
        'production_HDA_resources_bound': False,
        'resources': receipts,
    }
    pending['preservation-receipt.json'] = (json.dumps(receipt, indent=2)+'\n').encode()
    # Validate every input and every generated asset before creating the output.
    output.mkdir(parents=True)
    hda_output.mkdir(parents=True)
    for name, data in pending.items():
        (output/name).write_bytes(data)
    for name, data in hda_pending.items():
        (hda_output/name).write_bytes(data)
    print('PASS: four exact reflected PNG/RGBA/HDR1 variants; all full-density preservation checks pass.')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent/'player-rear-multicannon-p5-mode2-twins-v1/output')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hda-output', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output, args.hda_output)
