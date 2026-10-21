#!/usr/bin/env python3
"""Verify cash25/50/75/gem100/gem250 source pins from user-supplied original files; never copy game data."""
import argparse
import hashlib
import json
import struct
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fnv(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return f'{value:016x}'

def decode(raw, index):
    pos = struct.unpack_from('<H', raw, (index - 1) * 2)[0]
    values, mask = bytearray(168), bytearray(168)
    cell = 0
    while raw[pos] != 15:
        code = raw[pos]
        pos += 1
        cell += code & 15
        for _ in range(code >> 4):
            if not 0 <= cell < 168:
                raise ValueError('Source tile overrun')
            values[cell], mask[cell] = raw[pos], 255
            pos, cell = pos + 1, cell + 1
    return values, mask

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text())
    for family in registry['families'][7:12]:
        source = family['source_identity']
        raw = (args.data/'tyrian.shp').read_bytes()
        assert sha(raw) == source['physical_source_sha256']
        count = struct.unpack_from('<H', raw)[0]
        offsets = list(struct.unpack_from('<'+str(count)+'I', raw, 2)) + [len(raw)]
        bank = raw[offsets[10]:offsets[11]]
        assert len(bank) == source['bank_bytes'] and sha(bank) == source['bank_sha256']
        value = (args.data/'newsh6.shp').read_bytes()
        assert len(value) == source['value_source']['bank_bytes']
        assert sha(value) == source['value_source']['physical_source_sha256']
        colors = set()
        for data, rows in [(bank, source['tiles']), (value, source['value_source']['tiles'])]:
            for tile in rows:
                indices, coverage = decode(data, tile['index'])
                assert fnv(indices+coverage) == tile['source_fnv64']
                assert sum(bool(x) for x in coverage) == tile['covered_cells']
                colors.update(index for index, mask in zip(indices, coverage) if mask)
        palette = source['palette']
        assert sorted(colors) == palette['indices']
        pal = (args.data/'palette.dat').read_bytes()
        # Source artwork uses gameplay palette 0. Runtime matches only the covered
        # colors, not this physical palette number or a level identifier.
        rgb = bytes((x << 2) | (x >> 4) for i in sorted(colors) for x in pal[3*i:3*i+3])
        assert sha(rgb) == palette['rgb_sha256'] and rgb.hex() == ''.join(palette['rgb_hex'])
        records = source['enemy_identity']
        for variant in records['variants']:
            data = (args.data/variant['physical_source']).read_bytes()
            assert sha(data) == variant['source_sha256']
            if variant['physical_source'].endswith('.hdt'):
                item_start = struct.unpack_from('<i', data)[0]
            else:
                count = struct.unpack_from('<H', data)[0]
                item_start = struct.unpack_from('<'+str(count)+'i', data, 2)[-1]
            # Exact disk widths from JE_loadItemDat, not sizeof(C structs).
            enemy_start = item_start+14+1638*80+61*82+55*37+7*37+19*41+38*86+12*37
            offset = enemy_start + records['record_index']*77
            assert offset == variant['offset']
            record = data[offset:offset+77]
            assert len(record) == records['record_bytes']
            assert sha(record) == variant['record_sha256'] and fnv(record) == variant['record_fnv64']
            assert fnv(record) in records['record_fnv64_variants']
            contract = family['draw_semantics']['body_contract']
            if 'animation_sequence' in contract:
                assert record[0] == contract['animation_length']
                assert list(struct.unpack_from('<20H', record, 21))[:record[0]] == contract['animation_sequence']
    print('PASS cash25/50/75/gem100/gem250: 28 body tiles, five value tiles, exact palettes and fifteen complete 77-byte record variants')

if __name__ == '__main__':
    main()
