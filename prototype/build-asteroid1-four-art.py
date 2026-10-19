#!/usr/bin/env python3
"""Pack one imagegen rock into the four original event12 actor positions.

The original 48x56 assembly is one continuous artwork. Its inward-only contour
coverage is applied globally before exact 24x28 slicing; interior boundaries
are never independently feathered. External original data stays external.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PLACEMENTS = ((440, 45, 0, 28), (441, 47, 24, 28),
              (442, 7, 0, 0), (443, 9, 24, 0))


def helpers():
    path = ROOT / 'prototype/build-asteroid1-ten-art.py'
    spec = importlib.util.spec_from_file_location('asteroid1_ten_art', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode, module.fnv


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--master', type=Path, default=ROOT / 'assets/hd/artwork/asteroid1-four-v1/imagegen-master.png')
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    decode, fnv = helpers()
    bank = (args.data / 'newshd.shp').read_bytes()
    assert len(bank) == 42012 and fnv(bank) == '0x913975450e0fc00d', 'Foreign original bankD'
    support = Image.new('L', (48, 56))
    pieces = []
    for record, base, x, y in PLACEMENTS:
        mask = np.zeros((28, 24), np.uint8)
        for di, dx, dy in ((0, 0, 0), (1, 12, 0), (19, 0, 14), (20, 12, 14)):
            _, coverage = decode(bank, base + di)
            mask[dy:dy + 14, dx:dx + 12] = coverage
        support.paste(Image.fromarray(mask), (x, y))
        pieces.append((record, base, x, y, mask))
    generated = Image.open(args.master).convert('RGBA')
    ys, xs = np.where(np.asarray(generated.getchannel('A')) >= 16)
    assert len(xs), 'Empty artwork'
    crop = generated.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    bbox, density = support.getbbox(), 8
    aligned = Image.new('RGBA', (48 * density, 56 * density))
    crop = crop.resize(((bbox[2] - bbox[0]) * density, (bbox[3] - bbox[1]) * density), Image.Resampling.LANCZOS)
    aligned.paste(crop, (bbox[0] * density, bbox[1] * density))
    high_support = support.resize(aligned.size, Image.Resampling.NEAREST)
    smooth = np.asarray(high_support.filter(ImageFilter.GaussianBlur(4.0))).astype(float)
    inward = np.minimum(np.clip((smooth - 127.5) * 2.0, 0, 255).astype(np.uint8), np.asarray(high_support))
    rgba = np.array(aligned)
    rgba[:, :, 3] = np.minimum(rgba[:, :, 3], inward)
    aligned = Image.fromarray(rgba, 'RGBA')
    inventory = {}
    for record, base, x, y, mask in pieces:
        tile = aligned.crop((x * density, y * density, (x + 24) * density, (y + 28) * density))
        rgba = np.array(tile)
        piece_support = Image.fromarray(mask).resize(tile.size, Image.Resampling.NEAREST)
        rgba[:, :, 3] = np.minimum(rgba[:, :, 3], np.asarray(piece_support))
        tile = Image.fromarray(rgba, 'RGBA')
        stem = f'enemy-newshd-{base}-8'
        tile.save(args.out / f'{stem}.png')
        payload = tile.tobytes()
        raw = struct.pack('<4s6I', b'HDR1', 1080000 + base, 8, 24, 28, 0, 0) + payload
        (args.out / f'{stem}.hda').write_bytes(raw)
        inventory[stem] = dict(record=record, base=base, size=1, logical_size=[24, 28],
                               rgba_fnv64=fnv(payload), sha256=hashlib.sha256(raw).hexdigest())
    aligned.save(args.out / 'assembled-rock-8x.png')
    (args.out / 'art-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print(f'Packed {len(inventory)} source-bound asteroid pieces')


if __name__ == '__main__':
    main()
