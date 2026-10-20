#!/usr/bin/env python3
"""Portable exact four-tile fixture art and independent original-source checks."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/hd/artwork/asteroid1-fixture429-v1'
PACK = ROOT / 'assets/hd/packs/asteroid1-ten-v1'
SHA = lambda data: hashlib.sha256(data).hexdigest()


def rejects(action):
    try:
        action()
    except AssertionError:
        return
    raise AssertionError('Mutated source unexpectedly authenticated')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists() and not args.out.is_symlink()
    args.out.mkdir(parents=True)
    script = ROOT / 'prototype/build-asteroid1-fixture429-art.py'
    spec = importlib.util.spec_from_file_location('fixture_art', script)
    compiler = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(compiler)
    provenance = json.loads((ART / 'provenance.json').read_text())
    inventory = json.loads((ART / 'art-inventory.json').read_text())
    bank = (args.data / 'shapesz.dat').read_bytes()
    sources = compiler.decode_sources(bank)
    assert provenance['masters'] == {'master-v1.png': compiler.MASTER_SHA256}
    assert (ART / provenance['generation_prompt_file']).is_file()
    assert SHA((ART / 'master-v1.png').read_bytes()) == compiler.MASTER_SHA256
    with Image.open(ART / 'master-v1.png') as master:
        assert master.size == (1161, 1355)
        unified = master.convert('RGBA').resize((384, 448), Image.Resampling.LANCZOS)
    subprocess.run([sys.executable, str(script), '--data', str(args.data), '--out', str(args.out / 'rebuilt')],
                   check=True, capture_output=True, text=True)
    stitched = Image.new('RGBA', (384, 448))
    rows = []
    source_mutations = 0
    source_swaps = 0
    for base in compiler.BASES:
        source, offset = sources[base]
        assert len(source) == 672 and all(source)
        assert bank[offset:offset + 672] == source
        # This rejection path has no bank fingerprint: every byte of every tile
        # is protected by that tile's own identity, not an incidental neighbor.
        for index in range(672):
            damaged = bytearray(source)
            damaged[index] ^= 1
            rejects(lambda: compiler.authenticate_tile(base, damaged))
            source_mutations += 1
        for other in compiler.BASES:
            if other != base:
                rejects(lambda: compiler.authenticate_tile(base, sources[other][0]))
                source_swaps += 1
        rejects(lambda: compiler.authenticate_tile(base, source[:-1]))
        rejects(lambda: compiler.authenticate_tile(base, source + b'\0'))
        stem = f'terrain-shapesz-{base}-8'
        raw = (PACK / (stem + '.hda')).read_bytes()
        with Image.open(ART / (stem + '.png')) as image:
            assert image.mode == 'RGBA' and image.size == (192, 224)
            assert image.getchannel('A').getextrema() == (255, 255)
            assert struct.unpack('<4s6I', raw[:28]) == (b'HDR1', 1440000 + base, 8, 24, 28, 0, 0)
            assert raw[28:] == image.tobytes()
            assert SHA(raw) == inventory[stem]['sha256']
            assert compiler.fnv(image.tobytes()) == compiler.RGBA_PINS[base] == inventory[stem]['rgba_fnv64']
            assert image.tobytes() == unified.crop(compiler.QUADRANTS[base]).tobytes()
            stitched.paste(image, compiler.QUADRANTS[base][:2])
        assert raw == (args.out / 'rebuilt' / (stem + '.hda')).read_bytes()
        assert (ART / (stem + '.png')).read_bytes() == (args.out / 'rebuilt' / (stem + '.png')).read_bytes()
        rows.append({'base': base, 'source_cells': 672, 'source_tile_sha256': SHA(source),
                     'source_tile_fnv64': compiler.fnv(source), 'rgba_fnv64': compiler.RGBA_PINS[base],
                     'hda_sha256': SHA(raw)})
    assert len(set(row['rgba_fnv64'] for row in rows)) == 4
    assert stitched.tobytes() == unified.tobytes()
    assert (ART / 'art-inventory.json').read_bytes() == (args.out / 'rebuilt/art-inventory.json').read_bytes()
    stitched.save(args.out / 'registered-unified.png')
    report = {
        'status': 'PASS', 'images': rows, 'material_role': 144, 'logical_bank': 201,
        'source_bank_bytes': len(bank), 'source_bank_sha256': SHA(bank),
        'independent_source_byte_mutations_rejected': source_mutations,
        'independent_source_tile_swaps_rejected': source_swaps,
        'all_2688_original_cells_represented_and_fully_opaque': True,
        'whole_master_single_resize_and_exact_quadrants': True,
        'reassembled_tiles_equal_whole_registered_master': True,
        'rebuild_HDA_PNG_inventory_exact': True, 'master_matches_provenance': True,
        'scope': 'Finite geometry-only art conversion; production admission, original indexed blits and normal-engine acceptance are tested separately.',
    }
    (args.out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
