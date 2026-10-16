#!/usr/bin/env python3
"""Verify or rebuild the generated-only, three-piece Plasma Storm artwork."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = 'assets/hd/artwork/option-plasma-projectile-art-v1'
CONTRACT = '1bb4ed9bb6757050928d7c48b50c64bbe9fd0cc117c8991e4968918fea526f9d'
BINDING = '95c493c07c270efaa996db27a39c67a94cd713a9e2f36dca3b30eca62279f426'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fnv(raw):
    value = 14695981039346656037
    for byte in raw:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return f'{value:016x}'


def verify_rebuild(art, output, entries):
    subprocess.run([sys.executable, str(art / 'rebuild.py'), '--output', str(output),
                    '--resource-ids', '1300022', '1300023', '1300024'],
                   check=True, capture_output=True, text=True)
    for entry in entries:
        for key in ('output_png', 'output_hda'):
            assert (output / Path(entry[key]).name).read_bytes() == (art / entry[key]).read_bytes()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New output directory; never overwrite existing files')
    args = parser.parse_args()
    art = ROOT / ART
    assert sha((art / 'contract.json').read_bytes()) == CONTRACT
    assert sha((art / 'binding.json').read_bytes()) == BINDING
    contract = json.loads((art / 'contract.json').read_text())
    binding = json.loads((art / 'binding.json').read_text())
    assert binding['art_contract_sha256'] == CONTRACT
    assert binding['role'] == 130 and binding['indices'] == [22, 23, 24]
    assert binding['densities'] == [4, 8]
    assert sha((art / contract['master']['path']).read_bytes()) == contract['master']['sha256']
    manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    assert len(defaults) == 2
    expected_pairs = {(index, density) for index in (22, 23, 24) for density in (4, 8)}
    assert {(entry['index'], entry['density']) for entry in binding['entries']} == expected_pairs
    assert len(binding['entries']) == 6
    for entry in binding['entries']:
        index, density = entry['index'], entry['density']
        size = {22: [62, 24], 23: [65, 28], 24: [62, 23]}[index]
        header = [1300000 + index, density, *size, 0, 0]
        assert entry['header_u32'] == header and entry['logical_size'] == size
        assert entry['anchor'] == [0, 0] and entry['resource_id'] == 1300000 + index
        raw = (art / entry['output_hda']).read_bytes()
        png = (art / entry['output_png']).read_bytes()
        assert raw[:28] == struct.pack('<4s6I', b'HDR1', *header)
        assert len(raw) == 28 + size[0] * size[1] * density * density * 4 == entry['HDA_bytes']
        assert sha(raw) == entry['HDA_sha256'] and sha(png) == entry['PNG_sha256']
        assert sha(raw[28:]) == entry['RGBA_sha256'] and fnv(raw[28:]) == entry['RGBA_fnv1a64']
        with Image.open(art / entry['output_png']) as image:
            assert image.mode == 'RGBA' and image.size == (size[0] * density, size[1] * density)
            assert image.tobytes() == raw[28:]
        assert sum(value > 0 for value in raw[31::4]) == entry['alpha_nonzero_samples']
        assert sum(0 < value < 255 for value in raw[31::4]) == entry['alpha_fractional_samples']
        source = entry['source_png']
        assert (ROOT / source).read_bytes() == png
        assert manifest['source_pngs'][entry['HDA_sha256']] == {
            'path': source, 'sha256': entry['PNG_sha256'], 'RGBA_sha256': entry['RGBA_sha256']}
        expected = {'sha256': entry['HDA_sha256'], 'header_u32': header,
                    'source_png': source, 'source_png_sha256': entry['PNG_sha256']}
        for name, pack in manifest['packs'].items():
            assert pack['count'] == len(pack['files'])
            if name in defaults:
                assert pack['files'][entry['resource_name']] == expected
                assert (ROOT / 'assets/hd/packs' / name / entry['resource_name']).read_bytes() == raw
            else:
                assert entry['resource_name'] not in pack['files']
                assert not (ROOT / 'assets/hd/packs' / name / entry['resource_name']).exists()
    family = manifest['option_plasma_projectile_art_v1']
    assert family['source'] == ART and family['contract_sha256'] == CONTRACT
    assert family['binding_sha256'] == BINDING and family['role'] == 130
    assert family['indices'] == [22, 23, 24] and family['densities'] == [4, 8]
    assert family['entries'] == [{'index': e['index'], 'density': e['density'],
                                 'HDA_sha256': e['HDA_sha256']} for e in binding['entries']]
    if args.output:
        verify_rebuild(art, args.output.resolve(), binding['entries'])
    else:
        with tempfile.TemporaryDirectory(prefix='plasma-art-rebuild-') as temporary:
            verify_rebuild(art, Path(temporary) / 'rebuilt', binding['entries'])
    print('PASS: six generated-only Plasma Storm PNG/HDA resources, exact source/payload/header, '
          'canonical copies, both default packs, rollback exclusions and reproducible master fit.')


if __name__ == '__main__':
    main()
