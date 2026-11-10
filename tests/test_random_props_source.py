"""Independent original-data audit for ASTEROID2 random props.

Set ORIGINAL_GAME_DATA to a private Tyrian 2000 directory. No data is copied.
The ordinary artifact checks run without it. This is not gameplay validation.
"""
from pathlib import Path
import ast
import os
import re
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'experimental/level2-family/src'
BASES = (5, 43, 85, 123)
RECORDS = (135, 136, 260, 261, 263, 265, 266, 268)


def fnv(raw):
    h = 0xcbf29ce484222325
    for byte in raw:
        h = ((h ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return h


def array(source, name):
    raw = re.search(r'\b' + name + r'(?:\[\d+\])+=\s*(\{.*?\});', source, re.S)[1]
    return ast.literal_eval(raw.replace('{', '[').replace('}', ']'))


def decode(bank, index):
    """Decode the actual ordered RLE stores, including color zero stores."""
    pos = struct.unpack_from('<H', bank, (index - 1) * 2)[0]
    x = y = 0
    result = []
    for _ in range(len(bank)):
        code = bank[pos]
        pos += 1
        if code == 15:
            return result
        x += code & 15
        if not code >> 4:
            y += 1
            x -= 12
        else:
            for _ in range(code >> 4):
                assert 0 <= x < 12 and 0 <= y < 14
                result.append([x, y, bank[pos]])
                pos += 1
                x += 1
    raise AssertionError('unterminated RLE')


class RandomPropsSourceTests(unittest.TestCase):
    def test_all_four_materials_are_inward_and_pinned(self):
        source = (SRC / 'random_props_native.inc').read_text()
        native = array(source, 'rp_native')
        images = re.findall(r'\{(\d+),UINT64_C\(0x([0-9a-f]+)\)\}', source.split('rp_images[4]=')[1].split(';')[0])
        self.assertEqual(tuple(int(b) for b, _ in images), BASES)
        for i, (base, pin) in enumerate(images):
            raw = (ROOT / f'assets/hd/packs/asteroid1-ten-v1/enemy-newshd-{base}-8.hda').read_bytes()
            self.assertEqual(struct.unpack_from('<4s6I', raw), (b'HDR1', 1080000+int(base), 8, 24, 28, 0, 0))
            self.assertEqual(len(raw), 172060)
            self.assertEqual(fnv(raw[28:]), int(pin, 16))
            cells = {(x+dx, y+dy) for rows, (dx, dy) in zip(native[i], ((0,0),(12,0),(0,14),(12,14))) for x,y,_ in rows}
            for y in range(224):
                for x in range(192):
                    if (x//8,y//8) not in cells:
                        self.assertEqual(raw[28+(y*192+x)*4+3], 0)

    @unittest.skipUnless(os.environ.get('ORIGINAL_GAME_DATA'), 'requires private original data')
    def test_original_table_records_ordered_stores_and_palette(self):
        data = Path(os.environ['ORIGINAL_GAME_DATA'])
        source = (SRC / 'random_props_native.inc').read_text()
        mirror = (SRC / 'random_props_family_mirror.inc').read_text()
        bank = (data / 'newshd.shp').read_bytes()
        self.assertEqual((len(bank), fnv(bank)), (42012, 0x913975450e0fc00d))
        lvl = (data / 'tyrian1.lvl').read_bytes()
        offset = struct.unpack_from('<i', lvl, 2+2*4)[0]
        self.assertEqual(lvl[offset:offset+2], b'DZ')
        count = struct.unpack_from('<H', lvl, offset+8)[0]
        actual = list(struct.unpack_from(f'<{count}H', lvl, offset+10))
        self.assertEqual(actual, array(mirror, 'rp_table'))
        self.assertTrue(set(RECORDS).issubset(actual))
        self.assertTrue(set((137,262,264,267)).isdisjoint(actual))
        hdt = (data / 'tyrian.hdt').read_bytes()
        start = struct.unpack_from('<i', hdt)[0]+14+1638*80+61*82+55*37+7*37+19*41+38*86+12*37
        pins = re.findall(r'\{(\d+),(\d+),(\d+),UINT64_C\(0x([0-9a-f]+)\)\}', source.split('rp_records[8]=')[1])
        self.assertEqual(tuple(int(p[0]) for p in pins), RECORDS)
        for record, image, speed, pin in pins:
            raw = hdt[start+int(record)*77:start+(int(record)+1)*77]
            self.assertEqual(fnv(raw), int(pin,16))
            self.assertEqual(raw[8], int(speed))
            self.assertEqual(struct.unpack_from('<20H',raw,21), (BASES[int(image)],)+(0,)*19)
        stores = [[decode(bank,b+p) for p in (0,1,19,20)] for b in BASES]
        self.assertEqual(stores, array(source,'rp_native'))
        self.assertEqual([[len(p) for p in row] for row in stores],array(source,'rp_counts'))
        self.assertEqual([sum(map(len,row)) for row in stores],array(source,'rp_totals'))
        palette = {int(i):int(rgb,16) for i,rgb in re.findall(r'\{(\d+),0x([0-9a-f]+)\}', source.split('rp_palette[]')[1].split(';')[0])}
        self.assertTrue({index for row in stores for part in row for _,_,index in part}.issubset(palette))
