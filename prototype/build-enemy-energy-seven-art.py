#!/usr/bin/env python3
"""Validate/rebuild the frozen seven-ID enemy-role energy family. No game run."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
from PIL import Image

IDS = [77, 58, 182, 163, 1, 183, 164]
SOURCE = 'assets/hd/artwork/enemy-energy-seven-v1'
INVENTORY_SHA = '3eb212ba59bc52f2d75e86582e308518e2322c8e2ad09be46567a29c19810e1c'
FAMILY = 'enemy_energy_seven_v1'
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def read(path):
    assert path.is_file() and not path.is_symlink(), ('regular file required', str(path))
    return path.read_bytes()


def fnv(raw):
    value = 0xcbf29ce484222325
    for byte in raw:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'{value:016x}'


def validate(repo):
    repo = Path(repo)
    source = repo / SOURCE
    raw_inventory = read(source / 'inventory.json')
    assert sha(raw_inventory) == INVENTORY_SHA, 'frozen inventory changed'
    inventory = json.loads(raw_inventory)
    assert [row['id'] for row in inventory['outputs']] == IDS
    for name, digest in inventory['inputs'].items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(read(source / name)) == digest, ('frozen input changed', name)
    contract = json.loads(read(source / 'proof/source-contract.json'))
    original = {row['id']: row for row in contract['sprites']}
    manifest = json.loads(read(repo / 'assets/hd/manifest.json'))
    defaults = [manifest['default_preview_pack'], manifest['default_debug_pack']]
    assert len(set(defaults)) == 2
    expected_entries, canonical_paths, names, hashes, rgba_hashes = [], set(), set(), set(), set()
    fractional = 0
    for slot, row in enumerate(inventory['outputs'], 462):
        index = row['id']
        stem = f'enemy-energy-{index}-8'
        raw = read(source / 'output' / (stem + '.hda'))
        header = [1110000 + index, 8, 12, 14, 0, 0]
        assert len(raw) == 43036 and raw[:28] == b'HDR1' + struct.pack('<6I', *header)
        assert sha(raw) == row['HDA_SHA256'] and sha(raw[28:]) == row['RGBA_SHA256']
        png = read(source / 'output' / (stem + '.png'))
        assert sha(png) == row['PNG_SHA256']
        with Image.open(source / 'output' / (stem + '.png')) as image:
            assert image.mode == 'RGBA' and image.size == (96, 112) and image.tobytes() == raw[28:]
        with Image.open(source / f'masks/mask-bank8-{index}.png') as mask:
            assert mask.mode == 'L' and mask.size == (12, 14)
            logical = mask.tobytes()
            assert set(logical) <= {0, 255} and sha(logical) == original[index]['mask_sha256']
            assert logical.count(255) == original[index]['opaque_pixels']
            support = mask.resize((96, 112), Image.Resampling.NEAREST).tobytes()
        alpha = raw[31::4]
        assert all(not a or s for a, s in zip(alpha, support)), 'alpha outside original support'
        partial = sum(0 < a < 255 for a in alpha)
        assert partial == row['fractional_alpha_samples'] and partial > 0 and any(alpha)
        fractional += partial
        digest = sha(raw)
        canonical = f'assets/hd/source/{stem}-{digest[:12]}.png'
        assert read(repo / canonical) == png
        assert manifest['source_pngs'][digest] == {'path': canonical, 'sha256': sha(png), 'RGBA_sha256': sha(raw[28:])}
        for pack in defaults:
            item = manifest['packs'][pack]['files'][stem + '.hda']
            assert item == {'header_u32': header, 'sha256': digest, 'source_png': canonical, 'source_png_sha256': sha(png)}
            assert read(repo / 'assets/hd/packs' / pack / (stem + '.hda')) == raw
        expected_entries.append({'id': index, 'slot': slot, 'HDA_sha256': digest, 'RGBA_FNV1a64': fnv(raw[28:])})
        canonical_paths.add(canonical); names.add(stem + '.hda'); hashes.add(digest); rgba_hashes.add(sha(raw[28:]))
    assert manifest[FAMILY] == {
        'source': SOURCE, 'inventory_sha256': INVENTORY_SHA, 'role': 111, 'density': 8,
        'logical_size': [12, 14], 'anchor': [0, 0], 'ids': IDS,
        'scope': 'enemy-role including declared shared58; all player paths unchanged',
        'fallback': 'all-seven-or-classic; density8 only; startup-selected cache', 'entries': expected_entries}
    for pack, content in manifest['packs'].items():
        assert content['count'] == len(content['files'])
        relevant = {name for name, entry in content['files'].items()
                    if name.startswith('enemy-energy-') or entry['header_u32'][0] // 10000 == 111 or entry['sha256'] in hashes}
        assert relevant == (names if pack in defaults else set()), 'unexpected energy pack binding'
    indexed = {entry['path'] for digest, entry in manifest['source_pngs'].items()
               if digest in hashes or entry['RGBA_sha256'] in rgba_hashes or Path(entry['path']).name.startswith('enemy-energy-')}
    assert indexed == canonical_paths, 'unexpected energy canonical index'
    actual = set()
    for path in (repo / 'assets/hd/packs').rglob('*'):
        assert not path.is_symlink()
        if not path.is_file():
            continue
        with path.open('rb') as stream:
            header = stream.read(8)
        role = struct.unpack('<I', header[4:])[0] // 10000 if len(header) == 8 and header[:4] == b'HDR1' else 0
        if path.name.startswith('enemy-energy-') or role == 111:
            actual.add(path.relative_to(repo / 'assets/hd/packs').as_posix())
    assert actual == {f'{pack}/{name}' for pack in defaults for name in names}, 'unexpected on-disk energy binding'
    assert {p.relative_to(repo).as_posix() for p in (repo / 'assets/hd/source').glob('enemy-energy-*')} == canonical_paths
    return {'status': 'PASS', 'members': 7, 'bindings': 14, 'fractional_alpha_samples': fractional,
            'inventory_sha256': INVENTORY_SHA, 'entries': expected_entries, 'game_runs': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    result = validate(repo)
    if args.output:
        destination = args.output.absolute()
        assert not destination.exists() and not any(p.is_symlink() for p in [destination, *destination.parents])
        assert repo != destination and repo not in destination.parents and destination not in repo.parents
        subprocess.run([sys.executable, str(repo / SOURCE / 'rebuild.py'), str(destination)], check=True)
    else:
        with tempfile.TemporaryDirectory(prefix='enemy-energy-rebuild-') as temporary:
            subprocess.run([sys.executable, str(repo / SOURCE / 'rebuild.py'), str(Path(temporary) / 'output')], check=True)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
