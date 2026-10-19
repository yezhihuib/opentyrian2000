#!/usr/bin/env python3
"""Align and pack one imagegen-authored static record545 capsule enemy.

Original game data remains external. This converter resizes the transparent
master once, clips its alpha inward to original support, and emits one HDR1.
It does not redraw, recolor, animate, or change any gameplay data.
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--master', type=Path, default=ROOT / 'assets/hd/artwork/asteroid1-capsule545-v1/imagegen-master.png')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    helper = importlib.util.spec_from_file_location('asteroid_art', ROOT / 'prototype/build-asteroid1-ten-art.py')
    art = importlib.util.module_from_spec(helper)
    helper.loader.exec_module(art)
    bank = (args.data / 'newshd.shp').read_bytes()
    assert len(bank) == 42012 and art.fnv(bank) == '0x913975450e0fc00d', 'Foreign original bankD'
    mask = np.zeros((28, 24), np.uint8)
    for delta, x, y in ((0, 0, 0), (1, 12, 0), (19, 0, 14), (20, 12, 14)):
        _, coverage = art.decode(bank, 77 + delta)
        mask[y:y + 14, x:x + 12] = coverage
    support = Image.fromarray(mask)
    bbox = support.getbbox()
    assert bbox == (6, 3, 19, 28) and np.count_nonzero(mask) == 255
    generated = Image.open(args.master).convert('RGBA')
    ys, xs = np.where(np.asarray(generated.getchannel('A')) >= 16)
    crop = generated.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    crop = crop.resize(((bbox[2] - bbox[0]) * 8, (bbox[3] - bbox[1]) * 8), Image.Resampling.LANCZOS)
    aligned = Image.new('RGBA', (192, 224))
    aligned.paste(crop, (bbox[0] * 8, bbox[1] * 8))
    support = support.resize(aligned.size, Image.Resampling.NEAREST)
    smooth = np.asarray(support.filter(ImageFilter.GaussianBlur(3.5))).astype(float)
    inward = np.minimum(np.clip((smooth - 127.5) * 2, 0, 255).astype(np.uint8), np.asarray(support))
    rgba = np.array(aligned)
    rgba[:, :, 3] = np.minimum(rgba[:, :, 3], inward)
    rgba[rgba[:, :, 3] == 0, :3] = 0
    output = Image.fromarray(rgba, 'RGBA')
    args.out.mkdir(parents=True, exist_ok=True)
    stem = 'enemy-newshd-77-8'
    output.save(args.out / (stem + '.png'))
    raw = struct.pack('<4s6I', b'HDR1', 1080077, 8, 24, 28, 0, 0) + output.tobytes()
    (args.out / (stem + '.hda')).write_bytes(raw)
    inventory = {stem: dict(record=545, base=77, size=1, logical_size=[24, 28],
                           rgba_fnv64=art.fnv(output.tobytes()), sha256=hashlib.sha256(raw).hexdigest())}
    (args.out / 'art-inventory.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print('Packed one source-bound static capsule enemy')


if __name__ == '__main__':
    main()
