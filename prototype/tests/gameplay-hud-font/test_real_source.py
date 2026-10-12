#!/usr/bin/env python3
"""Read-only production HUF1/source acceptance; never persist original pixels.

The supplied original game files are decoded only in memory. The temporary
directory contains a compiled loader library, never image/font/palette inputs.
An optional receipt records only hashes, dimensions, counts and pass status.
"""
from pathlib import Path
import argparse
import ctypes
import hashlib
import json
import os
import struct
import subprocess
import tempfile

from fixtures import GUARDS, HEADER, ROOT, fnv, font_map

RESOURCE_SHA256 = '3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e'
PIC3_SHA256 = '83c5979f54de07f79e0c13970f242ae6f7435d4d396a168b340458c955c0e0f4'


def decode_pic3(data):
    assert len(data) >= 58
    offsets = struct.unpack_from('<14I', data, 2)
    start, end = offsets[2], offsets[3]
    assert 58 <= start < end <= len(data)
    pixels = bytearray()
    cursor = start
    while len(pixels) < 64000:
        assert cursor < end, 'Truncated PIC3 stream'
        value = data[cursor]
        cursor += 1
        if value & 192 == 192:
            count = value & 63
            assert cursor < end, 'Truncated PIC3 repeat'
            value = data[cursor]
            cursor += 1
        else:
            count = 1
        assert len(pixels) + count <= 64000, 'PIC3 exceeds its fixed rectangle'
        pixels.extend(bytes([value]) * count)
    assert hashlib.sha256(pixels).hexdigest() == PIC3_SHA256
    return pixels


def decode_tiny(data):
    assert len(data) >= 2
    tables, = struct.unpack_from('<H', data)
    assert 3 < tables < 256 and len(data) >= 2 + 4 * tables
    offsets = struct.unpack_from('<%di' % tables, data, 2)
    cursor, end = offsets[2], offsets[3]
    assert 2 + 4 * tables <= cursor < end <= len(data)
    count, = struct.unpack_from('<H', data, cursor)
    cursor += 2
    assert count == 127
    glyphs = []
    for _ in range(count):
        assert cursor < end and data[cursor] == 1, 'Missing tiny-font record'
        cursor += 1
        assert cursor + 6 <= end
        width, height, size = struct.unpack_from('<3H', data, cursor)
        cursor += 6
        assert 1 <= width <= 6 and 1 <= height <= 8
        assert 0 < size <= 2 * width * height + height and cursor + size <= end
        glyphs.append((width, height, data[cursor:cursor + size]))
        cursor += size
    assert cursor <= end
    return glyphs


class Glyph(ctypes.Structure):
    _fields_ = [('width', ctypes.c_uint16), ('height', ctypes.c_uint16),
                ('size', ctypes.c_uint16), ('data', ctypes.POINTER(ctypes.c_uint8))]


def configure(library):
    byte_pointer = ctypes.POINTER(ctypes.c_uint8)
    map_pointer = ctypes.POINTER(ctypes.c_int)
    glyph_pointer = ctypes.POINTER(Glyph)
    library.hud_font_load.argtypes = [ctypes.c_char_p]
    library.hud_font_load.restype = ctypes.c_bool
    library.hud_font_capture.argtypes = [byte_pointer, ctypes.c_int, map_pointer, glyph_pointer]
    library.hud_font_capture.restype = ctypes.c_bool
    library.hud_font_source_matches.argtypes = [map_pointer, glyph_pointer]
    library.hud_font_source_matches.restype = ctypes.c_bool
    library.hud_font_palette_matches.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
    library.hud_font_palette_matches.restype = ctypes.c_bool
    library.hud_font_ready.argtypes = []
    library.hud_font_ready.restype = ctypes.c_bool
    library.hud_font_forget_source.argtypes = []
    library.hud_font_forget_source.restype = None
    library.hud_font_shutdown.argtypes = []
    library.hud_font_shutdown.restype = None
    for name in ('hud_font_width', 'hud_font_height'):
        function = getattr(library, name)
        function.argtypes = [ctypes.c_uint]
        function.restype = ctypes.c_int
    library.hud_font_alpha.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    library.hud_font_alpha.restype = ctypes.c_uint8


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Original game data directory (read only)')
    parser.add_argument('--resource', type=Path, required=True, help='Frozen gameplay-hud-font-v1.hda (read only)')
    parser.add_argument('--receipt', type=Path, help='Optional hash-only JSON receipt, outside the repository')
    args = parser.parse_args()
    resource = args.resource.resolve()
    assert resource.name == 'gameplay-hud-font-v1.hda'
    if args.receipt:
        receipt_path = args.receipt.resolve()
        assert ROOT.resolve() not in receipt_path.parents, 'Receipt must remain outside the repository'
        assert receipt_path not in (resource, args.data.resolve()), 'Receipt cannot replace an input'
        assert args.data.resolve() not in receipt_path.parents, 'Receipt cannot modify original game data'
    raw = resource.read_bytes()
    assert len(raw) == 163952 and hashlib.sha256(raw).hexdigest() == RESOURCE_SHA256
    original_pic = decode_pic3((args.data / 'tyrian.pic').read_bytes())
    original_glyphs = decode_tiny((args.data / 'tyrian.shp').read_bytes())
    palette_data = (args.data / 'palette.dat').read_bytes()
    assert len(palette_data) >= 6 * 768
    bank = palette_data[5 * 768:6 * 768]
    assert all(value < 64 for value in bank)
    rgb = bytes((value << 2) | (value >> 4) for value in bank)
    map_values = font_map()
    mapping_bytes = struct.pack('<256i', *map_values)
    metrics = b''.join(struct.pack('<3H', width, height, width + 1)
                       for width, height, _ in original_glyphs)
    encoded = struct.pack('<I', 127) + b''.join(
        struct.pack('<3H', width, height, len(data)) + data
        for width, height, data in original_glyphs)
    source_hashes = {
        'PIC3': fnv(original_pic), 'PALETTE': fnv(rgb), 'MAP': fnv(mapping_bytes),
        'METRICS': fnv(metrics), 'ENCODED': fnv(encoded),
        'ELIGIBLE': fnv(bytes([255]) * 86 + bytes(41)),
    }
    assert source_hashes == GUARDS, 'Recovered original source does not match the fixed contract'
    assert len(metrics) == 762 and len(encoded) == 3221

    indices = (ctypes.c_uint8 * 64000).from_buffer_copy(original_pic)
    mapping = (ctypes.c_int * 256)(*map_values)
    backing = [(ctypes.c_uint8 * len(data)).from_buffer_copy(data)
               for _, _, data in original_glyphs]
    glyphs = (Glyph * 127)(*(Glyph(width, height, len(data), backing[index])
                           for index, (width, height, data) in enumerate(original_glyphs)))
    palette = (ctypes.c_uint32 * 256)(*((rgb[i * 3] << 16) |
                                       (rgb[i * 3 + 1] << 8) | rgb[i * 3 + 2]
                                      for i in range(256)))
    with tempfile.TemporaryDirectory(prefix='huf-real-loader-') as tmp:
        shared_library = Path(tmp) / 'libhudfont.so'
        command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall',
                   '-Wextra', '-Werror', '-pedantic', '-shared', '-fPIC',
                   '-I' + str(ROOT / 'src'), str(ROOT / 'src/gameplay_hud_font.c'),
                   '-o', str(shared_library)]
        subprocess.run(command, check=True, timeout=45)
        library = ctypes.CDLL(str(shared_library))
        configure(library)
        try:
            assert library.hud_font_load(os.fsencode(resource.parent))
            assert not library.hud_font_ready()
            assert library.hud_font_source_matches(mapping, glyphs)
            # Capture is deliberately tested before any palette guard call.
            assert library.hud_font_capture(indices, 320, mapping, glyphs)
            assert library.hud_font_ready()
            assert library.hud_font_palette_matches(palette)
            samples = 0
            for glyph_id, (width, height, _) in enumerate(original_glyphs):
                assert library.hud_font_width(glyph_id) == (width if glyph_id < 86 else 0)
                assert library.hud_font_height(glyph_id) == (height if glyph_id < 86 else 0)
                if glyph_id >= 86:
                    assert library.hud_font_alpha(glyph_id, 0, 0, 4) == 0
                    continue
                for density in (4, 8):
                    repeat = density // 4
                    for y in range(height * density):
                        for x in range(width * density):
                            offset = (HEADER.size + ((glyph_id // 16) * 40 + 4 + y // repeat) * 512 +
                                      (glyph_id % 16) * 32 + 4 + x // repeat)
                            assert library.hud_font_alpha(glyph_id, x, y, density) == raw[offset]
                            samples += 1
                    assert library.hud_font_alpha(glyph_id, width * density, 0, density) == 0
                    assert library.hud_font_alpha(glyph_id, 0, height * density, density) == 0
            assert samples == 150800
            palette[0] ^= 1
            assert not library.hud_font_palette_matches(palette)
            palette[0] ^= 1
            assert library.hud_font_palette_matches(palette)
            indices[0] ^= 1
            assert not library.hud_font_capture(indices, 320, mapping, glyphs)
            assert not library.hud_font_ready()
            indices[0] ^= 1
            assert library.hud_font_capture(indices, 320, mapping, glyphs)
            library.hud_font_forget_source()
            assert not library.hud_font_ready()
            assert library.hud_font_alpha(0, 0, 0, 4) == 0
        finally:
            library.hud_font_shutdown()

    receipt = {
        'status': 'PASS', 'candidate': 'new recovered implementation',
        'resource_sha256': RESOURCE_SHA256, 'pic3_sha256': PIC3_SHA256,
        'source_fnv1a64': {name: '%016x' % value for name, value in source_hashes.items()},
        'production_constants': True, 'glyph_records_verified': 127,
        'eligible_glyphs_sampled': 86, 'exact_density_4_8_samples': samples,
        'metrics_bytes': len(metrics), 'encoded_serialization_bytes': len(encoded),
        'normal_palette_guard': 'PASS', 'actual_metric_padding_at_capture': 'PASS',
        'source_and_palette_mutations': 'PASS', 'original_data_persisted': False,
        'sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                   for path in (ROOT / 'src/gameplay_hud_font.c', ROOT / 'src/gameplay_hud_font.h',
                                Path(__file__).resolve())},
    }
    if args.receipt:
        args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print('HUF1 real-source PASS: production guards, 127 original glyph records, '
          'PIC3 capture before palette, normal palette, %d exact 4x/8x samples; '
          'no original bytes persisted.' % samples)


if __name__ == '__main__':
    main()
