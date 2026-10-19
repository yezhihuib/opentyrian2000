#!/usr/bin/env python3
"""Pack the source-aligned imagegen asteroid into its ten original actor roles.

Original game data is external and is never copied into the repository.
The imagegen master is authored artwork, not a procedural source upscale.
Only global alignment, inward contour coverage and original-coordinate slicing
are applied here. Interior piece boundaries are never independently feathered.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PLACEMENTS = ((444, 31, 0, 114, -49), (445, 13, 1, 132, -56),
              (446, 15, 0, 150, -63), (447, 34, 0, 150, -49),
              (448, 49, 1, 108, -28), (449, 51, 1, 132, -28),
              (450, 53, 1, 156, -28), (451, 88, 0, 114, -7),
              (452, 89, 1, 132, 0), (453, 91, 1, 156, 0))


def decode(bank, index):
    pos = struct.unpack_from('<H', bank, 2 * (index - 1))[0]
    colors = np.zeros((14, 12), np.uint8)
    coverage = colors.copy()
    x = y = 0
    for _ in range(len(bank)):
        code = bank[pos]
        pos += 1
        if code == 15:
            return colors, coverage
        x += code & 15
        count = code >> 4
        if not count:
            y += 1
            x -= 12
        else:
            for _ in range(count):
                assert 0 <= x < 12 and 0 <= y < 14
                colors[y, x], coverage[y, x] = bank[pos], 255
                pos += 1
                x += 1
    raise ValueError('Unterminated original tile')


def fnv(raw):
    value = 0xcbf29ce484222325
    for byte in raw:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'0x{value:016x}'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--master', type=Path, default=ROOT / 'assets/hd/artwork/asteroid1-ten-v1/imagegen-master.png')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    bank = (args.data / 'newshd.shp').read_bytes()
    assert len(bank) == 42012 and fnv(bank) == '0x913975450e0fc00d', 'Foreign original bankD'
    pieces = []
    original = Image.new('L', (96, 112))
    for record, base, size, x, y in PLACEMENTS:
        w, h = (24, 28) if size else (12, 14)
        mask = np.zeros((h, w), np.uint8)
        for di, dx, dy in ((0, 0, 0), (1, 12, 0), (19, 0, 14), (20, 12, 14)) if size else ((0, 0, 0),):
            _, coverage = decode(bank, base + di)
            mask[dy:dy + 14, dx:dx + 12] = coverage
        xx, yy = x - 96 - (6 if size else 0), y + 77 - (7 if size else 0)
        original.paste(Image.fromarray(mask), (xx, yy), Image.fromarray(mask))
        pieces.append((record, base, size, xx, yy, mask))
    generated = Image.open(args.master).convert('RGBA')
    ys, xs = np.where(np.asarray(generated.getchannel('A')) >= 16)
    crop = generated.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    bbox, density = original.getbbox(), 8
    aligned = Image.new('RGBA', (96 * density, 112 * density))
    crop = crop.resize(((bbox[2] - bbox[0]) * density, (bbox[3] - bbox[1]) * density), Image.Resampling.LANCZOS)
    aligned.paste(crop, (bbox[0] * density, bbox[1] * density))
    support = original.resize(aligned.size, Image.Resampling.NEAREST)
    smooth = np.asarray(support.filter(ImageFilter.GaussianBlur(4.0))).astype(float)
    inward = np.minimum(np.clip((smooth - 127.5) * 2.0, 0, 255).astype(np.uint8), np.asarray(support))
    rgba = np.array(aligned)
    rgba[:, :, 3] = np.minimum(rgba[:, :, 3], inward)
    aligned = Image.fromarray(rgba, 'RGBA')
    result = {}
    for record, base, size, x, y, mask in pieces:
        h, w = mask.shape
        tile = aligned.crop((x * density, y * density, (x + w) * density, (y + h) * density))
        rgba = np.array(tile)
        support = Image.fromarray(mask).resize(tile.size, Image.Resampling.NEAREST)
        rgba[:, :, 3] = np.minimum(rgba[:, :, 3], np.asarray(support))
        tile = Image.fromarray(rgba, 'RGBA')
        stem = f'enemy-newshd-{base}-8'
        tile.save(args.out / f'{stem}.png')
        payload = tile.tobytes()
        raw = struct.pack('<4s6I', b'HDR1', 1080000 + base, 8, w, h, 0, 0) + payload
        (args.out / f'{stem}.hda').write_bytes(raw)
        result[stem] = dict(record=record, base=base, size=size,
                            logical_size=[w, h], rgba_fnv64=fnv(payload),
                            sha256=hashlib.sha256(raw).hexdigest())
    (args.out / 'art-inventory.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f'Packed {len(result)} source-bound asteroid pieces')


if __name__ == '__main__':
    main()
