#!/usr/bin/env python3
"""Rebuild only cloud64 from two bundled authored PNGs; no game files are read."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parent
SIZE = (192, 224)
STEM = 'terrain-shapesz-64-8'
HEADER = [2010064, 8, 24, 28, 0, 0]
INPUTS = {
    'source/prior-generated64-v2.png': (
        '1b1cf5216ef9fdc87c860015cc4b7e0c245b4e8566e9b4ffca8ab58a7659350d',
        '79c8d4aeaebea142340801c160bcccb3eaa34f53af8c5610fefaebe068de1aee'),
    'source/generated64-bottom-reference.png': (
        '29362a2acb6d6a709ca91f0b165fad3a02ee865241da37e62b8f69d3586a7062',
        'e603b139baaa6d853a5aa9dbae721904936de2ae7906734c60799baee6e29fc4'),
}
HELPER_SHA = 'e4ec5c68ba9ca9efcd0fbbcdf843b21b4cc1ec588ffea6c5e761bc092a8862bd'
RGBA_SHA = 'fc88d9e42885e523c54111ab8e9a833a887256b222e97549d9d972bec988480f'
HDA_SHA = '1f9378615e16157f59113a47066dd28a52433c28e5a36d8845491b355e64a3b8'
SELECTED_PNG_SHA = '5a7b79fac3399d87cde0fb2d855e92e2121ed127a5112f7afcb5216e70deead3'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_inputs():
    images = []
    for relative, (file_hash, rgba_hash) in INPUTS.items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise ValueError('Canonical input must be a regular, package-owned file: ' + relative)
        if sha(path.read_bytes()) != file_hash:
            raise ValueError('Canonical input file SHA-256 mismatch: ' + relative)
        with Image.open(path) as im:
            if im.mode != 'RGBA' or im.size != SIZE:
                raise ValueError('Expected a 192x224 RGBA source: ' + relative)
            raw = im.tobytes()
        if sha(raw) != rgba_hash:
            raise ValueError('Canonical input decoded RGBA SHA-256 mismatch: ' + relative)
        images.append(raw)
    helper = ROOT / 'source/register_bottom64.cpp'
    if helper.is_symlink() or not helper.resolve().is_relative_to(ROOT) or sha(helper.read_bytes()) != HELPER_SHA:
        raise ValueError('Canonical C++ helper mismatch')
    return images, helper


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='An empty or new build directory, separate from this package')
    parser.add_argument('--cxx', default=os.environ.get('CXX', 'c++'),
                        help='C++17 compiler executable (one executable path, no shell flags)')
    args = parser.parse_args()
    images, helper = read_inputs()
    out = args.output_dir.expanduser().resolve()
    if out == ROOT or ROOT.is_relative_to(out) or (out.exists() and any(out.iterdir())):
        raise ValueError('Output directory must be empty and must not be a package ancestor')
    compiler = shutil.which(args.cxx)
    if compiler is None:
        raise ValueError('C++17 compiler not found: ' + args.cxx)
    with tempfile.TemporaryDirectory(prefix='cloud64 build ') as temp:
        work = Path(temp)
        for name, raw in zip(('prior.rgba', 'generated.rgba'), images):
            (work / name).write_bytes(raw)
        executable = work / 'register_bottom64'
        subprocess.run([compiler, '-std=c++17', '-O2', str(helper), '-o', str(executable)], check=True)
        subprocess.run([str(executable), str(work / 'prior.rgba'), str(work / 'generated.rgba'),
                        str(work / 'selected.rgba')], check=True)
        rgba = (work / 'selected.rgba').read_bytes()
    if len(rgba) != 192 * 224 * 4 or sha(rgba) != RGBA_SHA:
        raise ValueError('Rebuilt RGBA does not match the selected correction')
    hda = b'HDR1' + struct.pack('<6I', *HEADER) + rgba
    if sha(hda) != HDA_SHA:
        raise ValueError('Rebuilt HDA does not match the selected correction')
    (out / 'output').mkdir(parents=True)
    (out / 'runtime-overlay').mkdir()
    png = out / 'output' / (STEM + '.png')
    Image.frombytes('RGBA', SIZE, rgba).save(png, format='PNG', optimize=False, compress_level=9)
    (out / 'runtime-overlay' / (STEM + '.hda')).write_bytes(hda)
    report = {
        'schema': 'cloud64-v3-rebuild-v1', 'id': 64, 'layer': 2, 'slot': 199,
        'header_u32': HEADER, 'canonical_authored_input_count': 2,
        'original_game_data_required': False, 'generative_rerun': False,
        'rgba_sha256': sha(rgba), 'hda_sha256': sha(hda),
        'rebuilt_png_sha256': sha(png.read_bytes()),
        'selected_committed_png_sha256': SELECTED_PNG_SHA,
        'png_encoding_may_differ': True, 'compiler': compiler,
    }
    (out / 'rebuild-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
