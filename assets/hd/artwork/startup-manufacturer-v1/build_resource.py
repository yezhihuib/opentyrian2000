"""Build or validate the two frozen MFG1 startup resources, without game data.

FNV-1a stamps are compatibility/corruption checks, not security primitives.
Every output is 64 little-endian header bytes followed by opaque RGBA pixels.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct

from PIL import Image

ROOT = Path(__file__).resolve().parent
HEADER = struct.Struct('<4s7I4Q')
PACK = 'startup-manufacturer-v1'
DENSITY = 4
WIDTH, HEIGHT = 320, 200
PIXEL_SIZE = (WIDTH * DENSITY, HEIGHT * DENSITY)
PAYLOAD_BYTES = PIXEL_SIZE[0] * PIXEL_SIZE[1] * 4
FNV_OFFSET = 14695981039346656037
FNV_PRIME = 1099511628211
CARDS = {
    10: {
        'palette': 20,
        'indices_fnv64': 0x720d8ce9dda3f5f4,
        'palette_fnv64': 0xb50ac0b9e5f1a73d,
        'master': 'masters/pic10-xsiv-generated-master.png',
        'master_sha256': '8cb1be9d12efd38f129447116ce37bd5bd8347d24ff5e331b0e5cf29bb217ad9',
        'png': 'previews/pic10-candidate-native4x.png',
        'png_sha256': '00fd3fa8dccd72edc7621fe1b94e0f7ab60ca011e15ea886bfac2dcef63688bd',
        'rgb_sha256': 'af1361363f0d4405008ecf3458d5fcaae1ffc39159572dad0448c8d92fe9765e',
    },
    12: {
        'palette': 22,
        'indices_fnv64': 0x98d7341da720b7ab,
        'palette_fnv64': 0x20261a06b61711d5,
        'master': 'masters/pic12-eclipse-generated-master.png',
        'master_sha256': '264220752c724600b5912c1de61906bb934c36e7684179d747e3aa5837b91a74',
        'png': 'previews/pic12-candidate-native4x.png',
        'png_sha256': '1e84bae41415ea278257c81ab29397f97e586c87af0169e0fa497a2c87effa34',
        'rgb_sha256': '60ebe4edccdd61588a707bd28c5d6fcd50f2aa2460060ee93812469b8e6a92c9',
    },
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fnv(data):
    value = FNV_OFFSET
    for byte in data:
        value = ((value ^ byte) * FNV_PRIME) & 0xffffffffffffffff
    return value


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_file(root, name):
    """Accept only an ordinary, relative file wholly within this source root."""
    root = Path(root).resolve()
    relative = Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts,
            'Source path must be relative and contained')
    path = root / relative
    require(not any(p.is_symlink() for p in (path, *path.parents) if p != root),
            'Symlink source is not supported')
    require(path.is_file() and root in path.resolve().parents,
            'Missing or escaped source: ' + name)
    return path


def canonical_image(source, pic, from_masters=False):
    require(pic in CARDS, 'Only PIC10/PIC12 are supported')
    spec = CARDS[pic]
    key = 'master' if from_masters else 'png'
    path = checked_file(source, spec[key])
    require(sha(path.read_bytes()) == spec[key + '_sha256'], 'Frozen input hash mismatch')
    with Image.open(path) as image:
        require(image.mode == 'RGB', 'Frozen source must be RGB')
        if from_masters:
            require(image.size == (1586, 992), 'Unexpected master dimensions')
            canonical = image.resize(PIXEL_SIZE, Image.Resampling.LANCZOS)
        else:
            require(image.size == PIXEL_SIZE, 'Canonical dimensions must be 1280x800')
            canonical = image.copy()
    require(sha(canonical.tobytes()) == spec['rgb_sha256'], 'Canonical RGB hash mismatch')
    return canonical


def validate_resource(raw, expected_pic=None):
    """Reject malformed/corrupt MFG1 data; return the checked header values.

This validates the binary contract. The repository validator additionally pins
the complete resource SHA-256 to the reviewed artwork, not just its FNV stamp.
"""
    require(len(raw) == HEADER.size + PAYLOAD_BYTES, 'MFG1 must be exactly 4096064 bytes')
    words = HEADER.unpack_from(raw)
    magic, version, density, pic, palette, width, height, size, indices, colors, stamp, reserved = words
    require(magic == b'MFG1', 'Invalid MFG1 magic')
    require(version == 1 and density == DENSITY, 'Unsupported version or density')
    require(pic in CARDS and (expected_pic is None or pic == expected_pic), 'Unexpected PIC identity')
    spec = CARDS[pic]
    require(palette == spec['palette'], 'Unexpected palette identity')
    require((width, height, size) == (WIDTH, HEIGHT, PAYLOAD_BYTES), 'Invalid geometry or payload size')
    require(indices == spec['indices_fnv64'] and colors == spec['palette_fnv64'],
            'Incompatible original source signatures')
    require(reserved == 0, 'Reserved field must be zero')
    payload = raw[HEADER.size:]
    require(payload[3::4] == b'\xff' * (PIXEL_SIZE[0] * PIXEL_SIZE[1]), 'Payload must be fully opaque')
    require(fnv(payload) == stamp, 'Corrupt RGBA payload')
    return words


def build_resources(source=ROOT, from_masters=False):
    bundles = {}
    for pic, spec in CARDS.items():
        rgba = canonical_image(source, pic, from_masters).convert('RGBA').tobytes()
        stamp = fnv(rgba)
        raw = HEADER.pack(b'MFG1', 1, DENSITY, pic, spec['palette'], WIDTH, HEIGHT,
                          PAYLOAD_BYTES, spec['indices_fnv64'], spec['palette_fnv64'], stamp, 0) + rgba
        validate_resource(raw, pic)
        bundles[f'startup-pic{pic}-v1.hda'] = (raw, {
            'bytes': len(raw), 'sha256': sha(raw), 'pic_id': pic,
            'palette_zero_based': spec['palette'], 'density': DENSITY,
            'logical_dimensions': [WIDTH, HEIGHT], 'pixel_dimensions': list(PIXEL_SIZE),
            'payload_bytes': PAYLOAD_BYTES, 'header_bytes': HEADER.size,
            'decoded_indices_fnv64': f'{spec["indices_fnv64"]:016x}',
            'palette_rgb_fnv64': f'{spec["palette_fnv64"]:016x}',
            'payload_fnv64': f'{stamp:016x}', 'reserved': 0,
            'source_png': spec['png'], 'source_png_sha256': spec['png_sha256'],
            'canonical_rgb_sha256': spec['rgb_sha256'],
        })
    return bundles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--output', type=Path, help='New external directory for the two MFG1 files')
    action.add_argument('--validate', type=Path, nargs='+', help='Validate existing MFG1 resources')
    parser.add_argument('--from-masters', action='store_true', help='Rebuild from frozen generated masters only')
    args = parser.parse_args()
    try:
        if args.validate:
            require(not args.from_masters, '--from-masters requires --output')
            for path in args.validate:
                validate_resource(path.read_bytes())
            print(json.dumps({'validated': len(args.validate)}))
            return
        output = args.output.resolve()
        require(not output.exists() and output != ROOT and ROOT not in output.parents,
                'Choose a new external output directory; existing files are never overwritten')
        bundles = build_resources(from_masters=args.from_masters)
        output.mkdir(parents=True, exist_ok=False)
        for name, (raw, _) in bundles.items():
            (output / name).write_bytes(raw)
        print(json.dumps({name: receipt for name, (_, receipt) in bundles.items()}, indent=2))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
