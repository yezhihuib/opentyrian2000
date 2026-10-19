#!/usr/bin/env python3
"""Export the fixed optional shop front-weapon PSP1 resources.

Original art is read from external game data. No binary-mask clipping is used.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
from PIL import Image, ImageChops, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PARTS = {
    'front': dict(bank=6, index=0, size=(33,34), anchor=(61,48), rle_bytes=897,
        rle=0x1a232f9fc3e904b2, index_hash=0xdb89c876a399ba93, mask=0x1ea87c3f611af9a4,
        directory='shop-front-v1', name='shop-front-weapon00-v1.hda',
        source_sha='a8ffaf746ee2a81a62aaadcbd0f6c3b720165392c8a2d94d6279f4ed03692365',
        source_size=(1236,1273), crop=(27,33,1209,1233),
        provenance='OpenAI imagegen exec-af83d411-da96-4062-9f42-61d53c38f630')
}


def fnv(raw):
    value = 14695981039346656037
    for byte in raw:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return value


def support(data, sp):
    raw = (data/'tyrian.shp').read_bytes()
    offset = struct.unpack_from('<I', raw, 2+sp['bank']*4)[0]
    count = struct.unpack_from('<H', raw, offset)[0]
    offset += 2
    for sid in range(count):
        present = raw[offset]
        offset += 1
        if not present:
            continue
        w,h,size = struct.unpack_from('<HHH',raw,offset)
        offset += 6
        rle = raw[offset:offset+size]
        offset += size
        if sid != sp['index']:
            continue
        assert (w,h) == sp['size'] and size == sp['rle_bytes'] and fnv(rle) == sp['rle']
        indices, mask = bytearray(w*h), bytearray(w*h)
        x = y = k = 0
        while k < size:
            v = rle[k]
            k += 1
            assert y < h
            if v == 255:
                x += rle[k]
                k += 1
            elif v == 254:
                x = w
            elif v == 253:
                x += 1
            else:
                assert x < w
                indices[y*w+x], mask[y*w+x] = v,255
                x += 1
            assert x <= w
            if x == w:
                x,y = 0,y+1
        assert x == 0 and y <= h
        assert fnv(indices) == sp['index_hash'] and fnv(mask) == sp['mask']
        return Image.frombytes('L',(w,h),bytes(mask))
    raise ValueError('Missing fixed WEAPON sprite')


def export(data, part):
    sp = PARTS[part]
    assert sp['source_sha'], f'{part} artwork has not been reviewed'
    asset = ROOT/'assets'/sp['directory']
    source = asset/'source-imagegen.png'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == sp['source_sha']
    original = Image.open(source).convert('RGBA')
    assert original.size == sp['source_size']
    raster = tuple(v*4 for v in sp['size'])
    rgba = original.crop(sp['crop']).resize(raster,Image.Resampling.LANCZOS)
    raw = bytearray(rgba.tobytes())
    removed = sum(0 < raw[p+3] < 8 for p in range(0,len(raw),4))
    for p in range(0,len(raw),4):
        if raw[p+3] < 8:
            raw[p:p+4] = bytes(4)
    rgba = Image.frombytes('RGBA',raster,bytes(raw))
    # Match the runtime's three-by-three logical-cell Chebyshev support guard.
    # This is a validation assertion, never a clipping or silhouette operation.
    allowed = support(data,sp).filter(ImageFilter.MaxFilter(3)).resize(raster,Image.Resampling.NEAREST)
    excess = ImageChops.subtract(rgba.getchannel('A').point(lambda a:255 if a else 0),allowed)
    outside = sum(bool(v) for v in excess.tobytes())
    assert outside == 0, f'{outside} samples exceed the existing runtime support guard'
    fields = [1,sp['bank'],sp['index'],*sp['size'],4,*raster,*sp['anchor'],len(raw),4,1,1,0]
    payload_hash = fnv(raw)
    header = b'PSP1'+struct.pack('<15I',*fields)+struct.pack('<8Q',
        0x45a77a2246c174b9,0x1c6687307999bd82,sp['rle'],sp['index_hash'],sp['mask'],payload_hash,0,0)
    assert len(header) == 128 and len(raw) == sp['size'][0]*sp['size'][1]*64
    destination = asset/sp['name']
    destination.write_bytes(header+raw)
    rgba.save(destination.with_suffix('.png'))
    manifest = dict(format='PSP1',header_bytes=128,part=part,
        source=dict(file='source-imagegen.png',sha256=sp['source_sha'],size=sp['source_size'],crop_xyxy=sp['crop'],provenance=sp['provenance']),
        normalization='Original RGBA crop -> 4x Lanczos; alpha<8 zeroed with RGB; no original-mask clipping',
        alpha_below_8_zeroed_samples=removed,outside_runtime_one_logical_cell_samples=outside,
        bank=sp['bank'],index=sp['index'],logical_size=sp['size'],density=4,anchor=sp['anchor'],
        rgba='straight RGBA8; transparent RGB zero',payload_bytes=len(raw),payload_fnv1a=f'0x{payload_hash:016x}',
        file_sha256=hashlib.sha256(header+raw).hexdigest(),pillow=Image.__version__,
        original_rle_fnv1a=f'0x{sp["rle"]:016x}',original_index_fnv1a=f'0x{sp["index_hash"]:016x}',original_mask_fnv1a=f'0x{sp["mask"]:016x}',
        runtime='Independent optional SFN1 sibling; only known Talon full illustration; fixed front anchor excludes rear')
    destination.with_suffix('.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'src/shop_equipment_sprite_pins.h').write_text(
        '/* SPDX-License-Identifier: GPL-2.0-or-later */\n'
        '/* Generated by scripts/export_shop_equipment.py for the reviewed front-only batch. */\n'
        f'#define PF_FRONT_HASH UINT64_C(0x{payload_hash:016x})\n')
    print(json.dumps(manifest,indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--part',choices=tuple(PARTS),required=True)
    args = parser.parse_args()
    export(args.data,args.part)
