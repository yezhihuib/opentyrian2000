#!/usr/bin/env python3
"""Derive frozen grass9 pure-backing masks only; verify by default. Never alters art."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def green(a):
    a = a.astype(np.int16)
    return a[..., 1] - np.maximum(a[..., 0], a[..., 2])

def local_filter(a, offsets, op):
    pad = max(max(abs(y), abs(x)) for y, x in offsets)
    p = np.pad(a, pad, mode='edge')
    h, w = a.shape
    parts = [p[pad+y:pad+y+h, pad+x:pad+x+w] for y, x in offsets]
    if op == 'max':
        return np.maximum.reduce(parts)
    if op == 'min':
        return np.minimum.reduce(parts)
    return np.sum(parts, axis=0, dtype=np.int16)

def rle(mask):
    d = np.diff(np.pad(mask.ravel().astype(np.int8), (1, 1)))
    s, e = np.where(d == 1)[0], np.where(d == -1)[0]
    return [[int(a), int(b-a)] for a, b in zip(s, e)]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir', type=Path, help='Optional new/empty directory for derived mask JSON only')
    args = ap.parse_args()
    contract = json.loads((ROOT / 'contract.json').read_text())
    expected = json.loads((ROOT / contract['mask_file']).read_text())
    assert sha((ROOT / contract['mask_file']).read_bytes()) == contract['mask_file_sha256'], 'Mask export hash mismatch'
    images = {}
    for key, item in contract['inputs'].items():
        path = (ROOT / item['relative_path']).resolve()
        assert sha(path.read_bytes()) == item['file_sha256'], f'Input file hash mismatch: {key}'
        if 'rgba_sha256' in item:
            with Image.open(path) as im:
                a = np.array(im.convert('RGBA'))
            assert [a.shape[1], a.shape[0]] == item['size'], f'Input size mismatch: {key}'
            assert sha(a.tobytes()) == item['rgba_sha256'], f'Input RGBA mismatch: {key}'
            images[key] = a
    disk = [(y,x) for y in range(-2,3) for x in range(-2,3) if y*y+x*x <= 4]
    box = [(y,x) for y in range(-1,2) for x in range(-1,2)]
    yy, xx = np.indices((224,192))
    edge = np.minimum.reduce([xx,191-xx,yy,223-yy])
    origins = {i:(x*192,y*224) for y,row in enumerate(contract['fringe_layout']) for x,i in enumerate(row)}
    result = {k:v for k,v in expected.items() if k != 'tiles'}
    result['tiles'] = {}
    checks = []
    for i in contract['ids']:
        x,y = contract['source_crop_origins'][str(i)]
        m = green(images['family_v1'][y:y+224,x:x+192]) >= 3
        closed = local_filter(local_filter(m,disk,'max'),disk,'min')
        w1_num = local_filter(closed,box,'sum')
        if i == 69:
            w1_num[:] = 9
        w3_positive = np.zeros((224,192), dtype=bool)
        if i in origins:
            fx,fy = origins[i]
            fringe = images['fringe_v3'][fy:fy+224,fx:fx+192]
            w3_positive = (green(images[f'accepted_v2_{i}']) < 3) & (green(fringe) > 2) & (edge > 3)
        mask = (w1_num == 0) & ~w3_positive
        actual = {'sha256_u8':sha(mask.astype(np.uint8).tobytes()),'count':int(mask.sum()),'runs':rle(mask)}
        assert actual == expected['tiles'][str(i)], f'Derived mask mismatch: {i}'
        accepted = images[f'accepted_v3_{i}']
        assert np.all(accepted[mask] == images['old47'][mask]), f'Not pure frozen backing: {i}'
        assert not np.any(mask & (green(accepted) >= 3)), f'Accepted green is writable: {i}'
        assert np.all(accepted[...,3] == 255), f'Unexpected source occupancy: {i}'
        if i == 69:
            assert not mask.any(), '69 guard changed'
        result['tiles'][str(i)] = actual
        checks.append({'id':i,'pure_backing_pixels':int(mask.sum()),'mask_sha256_u8':actual['sha256_u8'],'exact':True})
    if args.output_dir:
        out = args.output_dir.expanduser().resolve()
        assert not out.exists() or (out.is_dir() and not any(out.iterdir())), 'Output must be new or empty'
        assert out != ROOT and not out.is_relative_to(ROOT) and not ROOT.is_relative_to(out), 'Output must be separate from mask contract'
        out.mkdir(parents=True, exist_ok=True)
        (out/'pure-sand-masks.rle.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(json.dumps({'all_input_hashes_valid':True,'all_masks_exact':True,'art_outputs_written':False,'pure_backing_pixels':sum(x['pure_backing_pixels'] for x in checks),'tiles':checks},indent=2))
if __name__ == '__main__':
    main()
