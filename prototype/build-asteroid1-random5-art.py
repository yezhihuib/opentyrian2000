#!/usr/bin/env python3
"""Pack the one static bankD/base5 rock shared by original records135–137.

The generated continuous grey rock is globally aligned to the original24x28
support. Inward-only contour coverage never changes original indexed drawing.
Original external data is not packaged with the artwork.
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


def helpers():
    spec = importlib.util.spec_from_file_location('asteroid1_ten_art', ROOT / 'prototype/build-asteroid1-ten-art.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode, module.fnv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--master', type=Path, default=ROOT / 'assets/hd/artwork/asteroid1-random5-v1/imagegen-master.png')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    decode, fnv = helpers()
    bank = (args.data / 'newshd.shp').read_bytes()
    assert len(bank) == 42012 and fnv(bank) == '0x913975450e0fc00d', 'Foreign original bankD'
    mask = np.zeros((28, 24), np.uint8)
    for delta, x, y in ((0, 0, 0), (1, 12, 0), (19, 0, 14), (20, 12, 14)):
        _, coverage = decode(bank, 5 + delta)
        mask[y:y + 14, x:x + 12] = coverage
    support = Image.fromarray(mask)
    generated = Image.open(args.master).convert('RGBA')
    ys, xs = np.where(np.asarray(generated.getchannel('A')) >= 16)
    assert len(xs), 'Empty artwork'
    crop = generated.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    bbox, density = support.getbbox(), 8
    aligned = Image.new('RGBA', (24 * density, 28 * density))
    crop = crop.resize(((bbox[2] - bbox[0]) * density, (bbox[3] - bbox[1]) * density), Image.Resampling.LANCZOS)
    aligned.paste(crop, (bbox[0] * density, bbox[1] * density))
    high_support = support.resize(aligned.size, Image.Resampling.NEAREST)
    smooth = np.asarray(high_support.filter(ImageFilter.GaussianBlur(4.0))).astype(float)
    inward = np.minimum(np.clip((smooth - 127.5) * 2.0, 0, 255).astype(np.uint8), np.asarray(high_support))
    rgba = np.array(aligned)
    rgba[:, :, 3] = np.minimum(rgba[:, :, 3], inward)
    aligned = Image.fromarray(rgba, 'RGBA')
    stem = 'enemy-newshd-5-8'
    aligned.save(args.out / f'{stem}.png')
    payload = aligned.tobytes()
    raw = struct.pack('<4s6I', b'HDR1', 1080005, 8, 24, 28, 0, 0) + payload
    (args.out / f'{stem}.hda').write_bytes(raw)
    inventory = {stem: dict(records=[135, 136, 137], base=5, size=1, logical_size=[24, 28],
                            source_tiles=[5, 6, 24, 25], rgba_fnv64=fnv(payload), sha256=hashlib.sha256(raw).hexdigest())}
    (args.out / 'art-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print('Packed one source-bound static rock shared by three motion records')


if __name__ == '__main__':
    main()
