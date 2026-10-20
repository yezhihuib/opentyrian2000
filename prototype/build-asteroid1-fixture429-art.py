#!/usr/bin/env python3
"""Register one authored opaque fixture to four exact SHAPESZ terrain tiles.

Geometry only: resize the complete master once, then split its four quadrants.
Original game data is read from --data and is never copied into the repository.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/hd/artwork/asteroid1-fixture429-v1'
BASES = (429, 430, 439, 440)
QUADRANTS = {429: (0, 0, 192, 224), 430: (192, 0, 384, 224),
             439: (0, 224, 192, 448), 440: (192, 224, 384, 448)}
BANK_BYTES = 318976
BANK_SHA256 = '3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248'
BANK_FNV64 = '0x14ebb02c262fc4a9'
MASTER_SHA256 = 'e05e055bb9493c6904979a69c7d25da2782077f01fa2ebd611bbe5e851b0e638'
SOURCE_PINS = {
    429: ('f4273e1453c8a749071926b809c5605e7aaaf285f80b0a8b3cd2701dfaa2e56e', '0x893197763e81f4f4'),
    430: ('02917741be6ea9dbbf016d48f3e8cfb2da0287b01c1c9ba182f8f9fba20252a1', '0xa87e4bf5a86a6912'),
    439: ('9a25abb4b1097fbdb53bce3ba6b67c91acd312f2a176a800398aae3ad9f3f70f', '0x0783ab8f573aeba9'),
    440: ('5ddef6dc5da8ee8b3118656bd1706f5bce2db3a861e8661642323f70e0e6faec', '0x5822b7fb5579332a'),
}
RGBA_PINS = {429: '0xfa971f5a0beca804', 430: '0x1098b0243ce33365',
             439: '0xd45866b7c26097d5', 440: '0x6b7a2f803d4f123a'}
SHA = lambda data: hashlib.sha256(data).hexdigest()


def fnv(raw):
    value = 0xcbf29ce484222325
    for byte in raw:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'0x{value:016x}'


def authenticate_tile(base, raw):
    """Authenticate this tile independently of every other tile and the bank."""
    assert base in SOURCE_PINS and len(raw) == 24 * 28
    sha, fingerprint = SOURCE_PINS[base]
    assert SHA(raw) == sha and fnv(raw) == fingerprint, f'Original terrain {base} mismatch'
    assert all(raw), f'Original terrain {base} is not completely opaque'
    return raw


def decode_sources(bank):
    assert len(bank) == BANK_BYTES and SHA(bank) == BANK_SHA256 and fnv(bank) == BANK_FNV64
    found = {}
    offset = 0
    # Production loads exactly 600 entries. The authenticated source also has
    # 520 trailing bytes, which are not interpreted as additional terrain.
    for base in range(1, 601):
        assert offset < len(bank)
        blank = bank[offset]
        offset += 1
        assert blank in (0, 1)
        start = offset
        if blank:
            raw = bytes(672)
        else:
            raw = bank[offset:offset + 672]
            assert len(raw) == 672
            offset += 672
        if base in BASES:
            assert not blank
            found[base] = (authenticate_tile(base, raw), start)
    assert offset == 318456 and set(found) == set(BASES)
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    sources = decode_sources((args.data / 'shapesz.dat').read_bytes())
    master = ART / 'master-v1.png'
    assert SHA(master.read_bytes()) == MASTER_SHA256
    with Image.open(master) as image:
        master_size = list(image.size)
        image = image.convert('RGBA')
        assert image.getchannel('A').getextrema() == (255, 255)
        unified = image.resize((384, 448), Image.Resampling.LANCZOS)
    args.out.mkdir(parents=True, exist_ok=True)
    inventory = {}
    for base in BASES:
        source, offset = sources[base]
        image = unified.crop(QUADRANTS[base])
        assert image.size == (192, 224) and image.getchannel('A').getextrema() == (255, 255)
        assert fnv(image.tobytes()) == RGBA_PINS[base]
        stem = f'terrain-shapesz-{base}-8'
        image.save(args.out / (stem + '.png'))
        raw = struct.pack('<4s6I', b'HDR1', 1440000 + base, 8, 24, 28, 0, 0) + image.tobytes()
        (args.out / (stem + '.hda')).write_bytes(raw)
        inventory[stem] = {
            'source_bank': 'shapesz.dat', 'logical_bank': 201, 'material_role': 144,
            'source_role': 'terrain-layer1', 'base': base, 'logical_size': [24, 28],
            'source_occupied_cells': 672, 'represented_logical_cells': 672,
            'source_tile_offset': offset, 'source_tile_sha256': SHA(source),
            'source_tile_fnv64': fnv(source), 'master': 'master-v1.png',
            'master_size': master_size, 'unified_registered_size': [384, 448],
            'quadrant_box': list(QUADRANTS[base]), 'rgba_fnv64': fnv(image.tobytes()),
            'sha256': SHA(raw),
        }
    (args.out / 'art-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print(json.dumps(inventory, indent=2))


if __name__ == '__main__':
    main()
