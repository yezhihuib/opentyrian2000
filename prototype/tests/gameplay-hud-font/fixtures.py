"""Synthetic HUF1 inputs. No original image or encoded font bytes are used."""
from pathlib import Path
import re
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HEADER = struct.Struct('<4s11I8Q')
PAYLOAD = 163840
FILENAME = 'gameplay-hud-font-v1.hda'
GUARDS = {
    'PIC3': 0x14c1441f3d5dc0e2,
    'PALETTE': 0x5e80e83992be2927,
    'MAP': 0x845b16939661b466,
    'METRICS': 0x0908ca85cbf2a1e3,
    'ENCODED': 0x2ed2973d82ce6f3d,
    'ELIGIBLE': 0x68e8c2bab3c43d0d,
}


def fnv(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return value


def dimensions(glyph_id):
    width = 6 if glyph_id == 0 else 3 if glyph_id == 70 else 4
    height = 8 if glyph_id in (0, 40, 43, 49, 50, 58) else 6
    return width, height


def font_map():
    source = (ROOT / 'src/fonthand.c').read_text()
    body = re.search(r'const int font_ascii\[256\]\s*=\s*\{(.*?)\};',
                     source, re.S).group(1)
    values = [int(value) for value in re.findall(r'-?\d+', re.sub(r'//[^\n]*', '', body))]
    assert len(values) == 256
    return values


def fixture(directory, glyph_overrides=None):
    """Write deterministic synthetic inputs and return (guard dict, HUF1 bytes).

    Overrides are ID -> (width, height, encoded bytes), solely for bounded-source
    parser tests with independently recomputed source pins.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    source = bytes([7]) * 64000
    palette = bytes(value for i in range(256)
                    for value in (i * 5 % 256, i * 11 % 256, i * 17 % 256))
    mapping = struct.pack('<256i', *font_map())
    glyphs = bytearray()
    metrics = bytearray()
    alpha = bytearray(PAYLOAD)
    for glyph_id in range(127):
        width, height = dimensions(glyph_id)
        data = bytes(253 if (x + y + glyph_id) % 4 == 0 else
                     3 if (x + y) % 3 == 0 else 7
                     for y in range(height) for x in range(width))
        for y in range(height * 4):
            for x in range(width * 4):
                coverage = (0 if (x // 4 + y // 4 + glyph_id) % 3 == 0 else
                            ((x * 29 + y * 11 + glyph_id * 13) % 255) + 1)
                ax = (glyph_id % 16) * 32 + 4 + x
                ay = (glyph_id // 16) * 40 + 4 + y
                alpha[ay * 512 + ax] = coverage
        if glyph_overrides and glyph_id in glyph_overrides:
            width, height, data = glyph_overrides[glyph_id]
        metrics.extend(struct.pack('<3H', width, height, width + 1))
        glyphs.extend(struct.pack('<3H', width, height, len(data)))
        glyphs.extend(data)
    guards = {
        'PIC3': fnv(source), 'PALETTE': fnv(palette), 'MAP': fnv(mapping),
        'METRICS': fnv(metrics), 'ENCODED': fnv(struct.pack('<I', 127) + glyphs),
        'ELIGIBLE': fnv(bytes([255]) * 86 + bytes(41)),
    }
    raw = HEADER.pack(b'HUF1', 1, 4, 512, 320, 127, 86, 32, 40, 4, PAYLOAD, 7,
                      guards['PIC3'], guards['PALETTE'], guards['MAP'],
                      guards['METRICS'], guards['ENCODED'], fnv(alpha),
                      guards['ELIGIBLE'], 0) + alpha
    for name, data in (('source.bin', source), ('map.bin', mapping),
                       ('glyphs.bin', glyphs), ('alpha.bin', alpha), (FILENAME, raw)):
        (directory / name).write_bytes(data)
    return guards, raw


def compiler_flags(guards):
    return ['-DHUD_FONT_' + name + '_FNV=UINT64_C(0x%016x)' % value
            for name, value in guards.items()]


def rechecksum(raw):
    raw = bytearray(raw)
    struct.pack_into('<Q', raw, 88, fnv(raw[HEADER.size:]))
    return raw


# Compatibility names for the renderer's independently recovered test harness.
make = fixture
flags = compiler_flags
