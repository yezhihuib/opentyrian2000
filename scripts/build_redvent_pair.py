#!/usr/bin/env python3
"""Rebuild two PRIVATE static terrain art candidates; never install or run them."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

IDS = (339, 348)
INPUTS = {'shapesz.dat': (318976, '3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248'),
          'palette.dat': (18432, 'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0')}
RAW_PINS = {339: '506a5da8fe4b08d593936a50c2ce650703eaebafae1fdd41c3875c28d4563da5',
            348: '3bb68a1fe7ed4d7086e63a41d6dc561c5d620c154f8d115fe393fd73b3205e53'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, sha, size=None):
    path = Path(path)
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('Expected regular non-symlink input: ' + str(path))
    actual_size = path.stat().st_size
    if actual_size > 20 * 1024 * 1024 or (size is not None and actual_size != size):
        raise ValueError('Wrong input size: ' + path.name)
    data = path.read_bytes()
    if digest(data) != sha:
        raise ValueError('Wrong input hash: ' + path.name)
    return data


def decode_shapes(data):
    pos = 0
    tiles = {}
    for tile_id in range(1, 601):
        if pos >= len(data):
            raise ValueError('Truncated shape flag')
        blank = data[pos]
        pos += 1
        if blank:
            raw = bytes(672)
        else:
            if pos + 672 > len(data):
                raise ValueError('Truncated shape pixels')
            raw = data[pos:pos + 672]
            pos += 672
        if tile_id in IDS:
            if not all(raw):
                raise ValueError('This pair requires fully opaque original tiles')
            tiles[tile_id] = raw
    if pos != 318456 or len(data) - pos != 520:
        raise ValueError('Unsupported shape layout')
    return tiles


def register(raw_image, native):
    """Preserve a one-native-pixel border, feather over the next two pixels."""
    from PIL import Image, ImageStat
    generated = raw_image.convert('RGB').resize((192, 224), Image.Resampling.LANCZOS)
    original = native.convert('RGB').resize((192, 224), Image.Resampling.NEAREST)
    means_g = ImageStat.Stat(generated).mean
    means_n = ImageStat.Stat(original).mean
    gains = [max(.75, min(1.25, n / max(g, 1))) for n, g in zip(means_n, means_g)]
    result = bytearray()
    old = original.load()
    new = generated.load()
    for y in range(224):
        for x in range(192):
            distance = min(x, y, 191 - x, 223 - y)
            weight = max(0., min(1., (distance - 7) / 16))
            for channel in range(3):
                candidate = min(255, max(0, round(new[x, y][channel] * gains[channel])))
                result.append(round(old[x, y][channel] * (1 - weight) + candidate * weight))
            result.append(255)
    return Image.frombytes('RGBA', (192, 224), bytes(result)), gains


def build(data_dir, raw_dir, output):
    from PIL import Image
    import PIL
    import io
    if PIL.__version__ != '13.0.0':
        raise ValueError('Exact candidate reproduction requires Pillow 13.0.0')
    data_dir, raw_dir, output = map(Path, (data_dir, raw_dir, output))
    repo = Path(__file__).resolve().parents[1]
    if output.exists() or output.is_symlink():
        raise ValueError('Output already exists; no overwrite allowed')
    out = output.resolve()
    if out.is_relative_to(repo) or not out.parent.is_dir():
        raise ValueError('Choose a fresh external output beneath an existing parent')
    for source in (data_dir, raw_dir):
        if source.resolve().is_relative_to(out) or out.is_relative_to(source.resolve()):
            raise ValueError('Output overlaps input directory')
    inputs = {name: checked(data_dir / name, pin, size) for name, (size, pin) in INPUTS.items()}
    tiles = decode_shapes(inputs['shapesz.dat'])
    palette = bytes((v << 2) | (v >> 4) for v in inputs['palette.dat'][3840:4608])
    outputs = {}
    entries = []
    for tile_id in IDS:
        raw = checked(raw_dir / f'tile{tile_id}-raw-v{1 if tile_id == 339 else 2}.png', RAW_PINS[tile_id])
        native = Image.frombytes('P', (24, 28), tiles[tile_id])
        native.putpalette(palette)
        with Image.open(io.BytesIO(raw)) as im:
            candidate, gains = register(im, native)
        payload = candidate.tobytes()
        hda = struct.pack('<4s4I2i', b'HDR1', 2010000 + tile_id, 8, 24, 28, 0, 0) + payload
        name = f'terrain-shapesz-{tile_id}-8'
        png = io.BytesIO()
        candidate.save(png, format='PNG')
        outputs[name + '.hda'] = hda
        outputs[name + '.png'] = png.getvalue()
        entries.append({'id': tile_id, 'hda_sha256': digest(hda), 'rgba_sha256': digest(payload),
                        'png_sha256': digest(png.getvalue()), 'raw_sha256': digest(raw),
                        'native_sha256': digest(tiles[tile_id]), 'channel_gains': gains,
                        'opaque_pixels': 192 * 224, 'native_border_locked_hd_pixels': 6400})
    report = {'schema': 'redvent-pair-static-candidate-v1', 'ids': list(IDS),
              'pillow': PIL.__version__, 'runtime_integrated': False, 'gameplay_verified': False,
              'source_data_included': False, 'original_derived_border': True,
              'scope': 'Private static candidate only; preserve the existing public 24-terrain count.',
              'files': entries}
    outputs['REPORT.json'] = (json.dumps(report, indent=2) + '\n').encode()
    out.mkdir()
    for name, data in outputs.items():
        (out / name).write_bytes(data)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--raw-art', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(build(args.data, args.raw_art, args.output), indent=2))


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        sys.exit(str(error))
