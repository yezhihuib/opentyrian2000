#!/usr/bin/env python3
"""Deterministically normalize the approved imagegen art and export sparse PMF1.

This is resource processing, not artwork generation. Pillow 12.3.0 is the
reproducibility reference. Source image and original-layout safety mask are
retained beside the result; no game data, font resources or packs are edited.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/shop-frame-v1'
SOURCE_SHA = '455e3b1b64754def2243583f9f19233eb926ea73ff546a9cc5311de1d24ab551'
MASK_SHA = 'f640be25a78f702b314aed5ffa3670a93a115df30f78169f81b715b1c94c90ac'


def fnv(data):
    result = 14695981039346656037
    for byte in data:
        result = ((result ^ byte) * 1099511628211) & 0xffffffffffffffff
    return result


def export(destination, preview=None):
    source = (ASSETS / 'source-imagegen.png').read_bytes()
    mask = (ASSETS / 'static-metal-support-320x200.bin').read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA
    assert hashlib.sha256(mask).hexdigest() == MASK_SHA
    assert len(mask) == 64000 and set(mask) == {0, 1}
    original = Image.open(ASSETS / 'source-imagegen.png').convert('RGB')
    assert original.size == (1586, 992)
    rgb = original.resize((1280, 800), Image.Resampling.LANCZOS)
    # The binary 320 mask is only a layout constraint. Reconstruct its contour
    # continuously in a narrow band; do not enlarge staircase pixels as alpha.
    # A 0.55-logical-pixel Gaussian rounds original stair corners, followed by
    # a tight level-set ramp (~one canonical sample) rather than blurry metal.
    field = Image.frombytes('L', (320, 200), bytes(v * 255 for v in mask))
    field = field.resize((1280, 800), Image.Resampling.NEAREST)
    # The old conservative list rectangle also retained its original diagonal
    # metal at the lower-left corner. Repair only that empty margin. These
    # fixed original-layout anchors follow the old edge into the new bevel;
    # they never enter item text (x185+) or the flat list interior (x171+).
    corner = [(159,136),(160,136),(161.5,140),(161.5,161),
              (163,166),(166.5,175),(168.5,180),(159,180)]
    ImageDraw.Draw(field).polygon([(round(x*4),round(y*4)) for x,y in corner], fill=255)
    field = field.filter(ImageFilter.GaussianBlur(2.2))
    alpha = field.point([max(0, min(255, (value - 112) * 8)) for value in range(256)])
    # Deep flat floors are strictly excluded. Outside the explicitly bounded
    # empty corner repair above, only the <=1 logical-pixel contour band can
    # differ from the original safety support.
    rgba = rgb.copy(); rgba.putalpha(alpha)
    raw = rgba.tobytes(); payload = bytearray(); runs = pixels = 0
    for y in range(800):
        x = 0
        while x < 1280:
            if not raw[(y * 1280 + x) * 4 + 3]:
                x += 1; continue
            start = x
            while x < 1280 and raw[(y * 1280 + x) * 4 + 3]:
                x += 1
            count = x - start
            payload += struct.pack('<II', y * 1280 + start, count)
            payload += raw[(y * 1280 + start) * 4:(y * 1280 + x) * 4]
            runs += 1; pixels += count
    fields = [1, 320, 200, 4, 1280, 800, runs, pixels, len(payload), 4, 1, 0, 0, 0, 0]
    header = b'PMF1' + struct.pack('<15I', *fields)
    header += struct.pack('<QQQ', 0x45a77a2246c174b9, 0x1c6687307999bd82, fnv(payload))
    header += bytes(40)
    assert len(header) == 128 and len(payload) < 1500000
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(header + payload)
    manifest = dict(format='PMF1 sparse row runs, straight RGBA8', version=1,
        source=dict(file='source-imagegen.png', sha256=SOURCE_SHA, size=[1586, 992],
                    provenance='Existing approved OpenAI imagegen output exec-40e633a6-95b6-48ca-b95c-6e4927a6ea0d; no redraw'),
        layout_mask=dict(file='static-metal-support-320x200.bin', sha256=MASK_SHA,
                         role='Authenticated PIC1 safety layout; continuous narrow contour plus explicit empty lower-left corner repair'),
        normalization='1586x992 -> 1280x800 Lanczos; fixed 320x200 logical mapping, not native 8x art',
        alpha='Gaussian 2.2 canonical px, tight level-set ramp 112..144; original flat floors remain transparent',
        corner_repair=dict(bounds_logical=[159,136,169,181], anchors_logical=corner,
                           purpose='Replace old diagonal metal retained by the conservative rectangle; no text/anchor changes'),
        canvas=[1280, 800], runs=runs, pixels=pixels, payload_bytes=len(payload),
        payload_fnv1a=f'0x{fnv(payload):016x}', file_bytes=len(header)+len(payload),
        file_sha256=hashlib.sha256(header+payload).hexdigest(),
        reference_pillow='12.3.0', runtime='Optional sibling of settings-font-*-v1.hda in --startup-assets directory')
    destination.with_suffix('.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    if preview:
        preview.parent.mkdir(parents=True, exist_ok=True); rgba.save(preview)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ASSETS / 'shop-frame-metal-v1.hda')
    parser.add_argument('--preview', type=Path)
    args = parser.parse_args()
    export(args.out, args.preview)
