#!/usr/bin/env python3
"""Rebuild four frozen generated Sonic quadrants; never reads original game data."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
from PIL import Image, ImageOps, __version__ as pillow_version

SHA = lambda data: hashlib.sha256(data).hexdigest()


def reconstruct(root):
    contract = json.loads((root / 'contract.json').read_text())
    assert pillow_version == contract['reconstruction']['version'], 'Pinned Pillow version required'
    images = {}
    for master in contract['masters']:
        source = root / master['source']
        assert source.is_file() and not source.is_symlink() and root in source.resolve().parents
        assert source.stat().st_size <= 32 * 1024**2
        assert SHA(source.read_bytes()) == master['source_sha256'], 'Generated master fingerprint mismatch'
        with Image.open(source) as picture:
            assert picture.mode == 'RGBA' and list(picture.size) == master['source_size']
            assert master['crop'] == [0, 0, *picture.size], 'No source cropping or original-mask clipping'
            piece = picture.resize(master['resize'], Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', tuple(contract['reconstruction']['canvas']))
        canvas.paste(piece, tuple(master['paste']))
        images[master['id']] = canvas
        images[master['id'] + 1] = ImageOps.mirror(canvas)
    assert set(images) == {105, 106, 124, 125}
    assert ImageOps.flip(images[105]).tobytes() != images[124].tobytes()
    assert not any(images[105].tobytes()[:16*96*4][3::4])
    assert not any(images[124].tobytes()[88*96*4:][3::4])
    payloads = {}
    for entry in contract['entries']:
        index = entry['id']
        picture = images[index]
        rgba = picture.tobytes()
        hda = b'HDR1' + struct.pack('<6I', *entry['header_u32']) + rgba
        assert entry['header_u32'] == [80000 + index, 8, 12, 14, 0, 0]
        assert SHA(rgba) == entry['RGBA_sha256'] and SHA(hda) == entry['HDA_sha256']
        assert sum(0 < alpha < 255 for alpha in rgba[3::4]) == entry['fractional_alpha_samples']
        assert rgba[3::4].count(255) == entry['alpha255_samples']
        payloads[index] = (picture, hda)
    return contract, payloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing paths are refused')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = args.output.absolute()
    assert not output.exists() and not output.is_symlink(), 'Choose a new output directory'
    assert output.parent.is_dir() and not any(path.is_symlink() for path in output.parents)
    assert output != root and root not in output.parents and output not in root.parents
    contract, payloads = reconstruct(root)
    output.mkdir()
    for entry in contract['entries']:
        index = entry['id']
        picture, hda = payloads[index]
        png = output / f'bullet-{index}-8.png'
        picture.save(png)
        assert SHA(png.read_bytes()) == entry['PNG_sha256']
        (output / f'bullet-{index}-8.hda').write_bytes(hda)
    print('PASS: four exact generated RGBA/PNG/HDR1 identities; two independent masters, horizontal mirrors, original margins')


if __name__ == '__main__':
    main()
