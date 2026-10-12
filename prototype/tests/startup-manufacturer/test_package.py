#!/usr/bin/env python3
"""Source/package checks only: never compile, invoke or require the game."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'prototype'))
from startup_manufacturer_bundle import build_bundles, PACK, SOURCE, SOURCE_FILES, RUNTIME_FILES

API = runpy.run_path(str(ROOT / SOURCE / 'build_resource.py'))
HEADER = struct.Struct('<4s7I4Q')
FROZEN = {
    10: ('a885d023f89b0e214a81df1d02dbf62d6e36645820c1a15e9a0ad74a2c5e2c79',
         0x720d8ce9dda3f5f4, 0xb50ac0b9e5f1a73d, 0x46944845146f2d39),
    12: ('bd358e8006a99467e08bc8bf257e6ead51fe5f216c63c57088612ef5039c7669',
         0x98d7341da720b7ab, 0x20261a06b61711d5, 0x3d97f250a0cae51a),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def independent_fnv(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value ^= byte
        value *= 0x100000001b3
        value &= 0xffffffffffffffff
    return value


class ManufacturerPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundles = build_bundles(ROOT)
        cls.manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())

    def call(self, script, *args, cwd, success=True, optimize=False):
        result = subprocess.run(
            [sys.executable, *(['-O'] if optimize else []), str(script), *map(str, args)],
            cwd=cwd, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_exact_rgba_and_header(self):
        self.assertEqual(HEADER.size, 64)
        self.assertEqual(set(self.bundles), RUNTIME_FILES)
        for pic, (expected_sha, indices, palette, stamp) in FROZEN.items():
            with self.subTest(pic=pic):
                raw, receipt = self.bundles[f'startup-pic{pic}-v1.hda']
                self.assertEqual(len(raw), 4096064)
                self.assertEqual(digest(raw), expected_sha)
                self.assertEqual(HEADER.unpack_from(raw), (
                    b'MFG1', 1, 4, pic, pic + 10, 320, 200, 4096000,
                    indices, palette, stamp, 0,
                ))
                png = ROOT / SOURCE / f'previews/pic{pic}-candidate-native4x.png'
                with Image.open(png) as image:
                    self.assertEqual((image.mode, image.size), ('RGB', (1280, 800)))
                    self.assertEqual(raw[64:], image.convert('RGBA').tobytes())
                self.assertEqual(raw[67::4], b'\xff' * 1024000)
                self.assertEqual(independent_fnv(raw[64:]), stamp)
                self.assertEqual(receipt['sha256'], expected_sha)

    def test_fnv_convention(self):
        self.assertEqual(API['fnv'](b''), 14695981039346656037)
        self.assertEqual(API['fnv'](b'hello'), 0xa430d84680aabd0b)

    def test_malformed_headers_are_rejected(self):
        for name, (raw, _) in self.bundles.items():
            words = list(HEADER.unpack_from(raw))
            mutations = {
                'magic': (0, b'HDR1'), 'version': (1, 2), 'density': (2, 8),
                'title-not-manufacturer': (3, 4), 'palette': (4, 0),
                'width': (5, 0xffffffff), 'height': (6, 0xffffffff),
                'payload-length': (7, 0xffffffff), 'index-guard': (8, 0),
                'palette-guard': (9, 0), 'payload-fnv': (10, 0), 'reserved': (11, 1),
            }
            for label, (at, value) in mutations.items():
                with self.subTest(name=name, field=label):
                    changed = words.copy()
                    changed[at] = value
                    with self.assertRaises(ValueError):
                        API['validate_resource'](HEADER.pack(*changed) + raw[64:])
            with self.assertRaises(ValueError):
                API['validate_resource'](raw, 12 if words[3] == 10 else 10)

    def test_size_corruption_and_transparency_are_rejected(self):
        for name, (raw, _) in self.bundles.items():
            for size in (0, 1, 63, 64, 4096063):
                with self.subTest(name=name, truncated=size), self.assertRaises(ValueError):
                    API['validate_resource'](raw[:size])
            with self.assertRaises(ValueError):
                API['validate_resource'](raw + b'\x00')
            corrupt = bytearray(raw)
            corrupt[64] ^= 1
            with self.assertRaises(ValueError):
                API['validate_resource'](corrupt)
            # Even a recomputed checksum cannot authorize alpha holes.
            corrupt = bytearray(raw)
            corrupt[67] = 254
            struct.pack_into('<Q', corrupt, 48, independent_fnv(corrupt[64:]))
            with self.assertRaises(ValueError):
                API['validate_resource'](corrupt)

    def test_gameplay_manifest_unchanged(self):
        packs = self.manifest['packs']
        self.assertNotIn(PACK, packs)
        self.assertEqual(digest(json.dumps(packs, sort_keys=True, separators=(',', ':')).encode()),
                         'e21f03ac25ac166c432e8270357830aba12d1621dbdd2d8063c5823c2c2b7b4b')
        self.assertEqual(len(packs), 18)
        self.assertEqual(sum(len(pack['files']) for pack in packs.values()), 2982)
        self.assertEqual(len({item['source_png'] for pack in packs.values() for item in pack['files'].values()}), 387)
        self.assertEqual([packs[self.manifest[key]]['count'] for key in
                          ('default_preview_pack', 'default_debug_pack')], [371, 375])
        self.assertEqual(self.manifest['default_preview_pack'],
                         'packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test')
        self.assertEqual(self.manifest['default_debug_pack'],
                         'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test')

    def test_original_pixel_files_excluded_and_provenance_exact(self):
        source = ROOT / SOURCE
        imported = json.loads((source / 'import.json').read_text())
        self.assertEqual(len(imported['omitted_files']), 4)
        imported_names = {path.relative_to(source).as_posix() for path in source.rglob('*') if path.is_file()}
        self.assertEqual(imported_names, SOURCE_FILES)
        for entry in imported['omitted_files']:
            self.assertNotIn(entry['pilot_path'], imported_names)
            self.assertFalse(any(path.name == Path(entry['pilot_path']).name for path in source.rglob('*.png')))
        for entry in imported['copied_files']:
            data = (source / entry['imported_path']).read_bytes()
            self.assertEqual((len(data), digest(data)), (entry['bytes'], entry['sha256']))

    def test_fresh_standalone_and_master_only_relocation(self):
        source = ROOT / SOURCE
        before = {name: digest((source / name).read_bytes()) for name in SOURCE_FILES}
        with tempfile.TemporaryDirectory(prefix='manufacturer-source-only-') as tmp:
            root = Path(tmp)
            cwd = root / 'unrelated working directory'
            cwd.mkdir()
            canonical = root / 'canonical output with spaces'
            self.call(source / 'build_resource.py', '--output', canonical, cwd=cwd)
            # No canonical images, original game files, prior HDA files, or repo
            # modules are copied into this independently relocated source tree.
            relocated = root / 'relocated generated masters with spaces'
            relocated.mkdir()
            shutil.copytree(source / 'masters', relocated / 'masters')
            for name in ('build_resource.py', 'build_previews.py', 'requirements.txt'):
                shutil.copyfile(source / name, relocated / name)
            self.assertFalse((relocated / 'previews').exists())
            output = root / 'relocated resource output'
            self.call(relocated / 'build_resource.py', '--from-masters', '--output', output, cwd=cwd)
            for name, (raw, _) in self.bundles.items():
                self.assertEqual((canonical / name).read_bytes(), raw)
                self.assertEqual((output / name).read_bytes(), raw)
            self.call(relocated / 'build_resource.py', '--validate',
                      *(output / name for name in sorted(RUNTIME_FILES)), cwd=cwd, optimize=True)
            preview_output = root / 'fresh regenerated preview output'
            self.call(relocated / 'build_previews.py', '--output', preview_output, cwd=cwd)
            for name in SOURCE_FILES:
                if name.startswith('previews/'):
                    self.assertEqual((preview_output / Path(name).name).read_bytes(), (source / name).read_bytes())
            # Source tree and existing output cannot be used as output targets.
            for invalid in (output, relocated, relocated / 'nested output'):
                self.call(relocated / 'build_resource.py', '--from-masters', '--output', invalid,
                          cwd=cwd, success=False)
            corrupt = root / 'corrupt.hda'
            corrupt.write_bytes(next(iter(self.bundles.values()))[0][:-1])
            self.call(relocated / 'build_resource.py', '--validate', corrupt,
                      cwd=cwd, success=False, optimize=True)
        self.assertEqual(before, {name: digest((source / name).read_bytes()) for name in SOURCE_FILES})

    def test_relocated_inventory_and_corrupt_input_rejections(self):
        with tempfile.TemporaryDirectory(prefix='manufacturer-repo-check-') as tmp:
            repo = Path(tmp) / 'relocated repository with spaces'
            source = repo / SOURCE
            shutil.copytree(ROOT / SOURCE, source)
            pack = repo / 'assets/hd/packs' / PACK
            shutil.copytree(ROOT / 'assets/hd/packs' / PACK, pack)
            manifest_path = repo / 'assets/hd/manifest.json'
            manifest_path.write_text(json.dumps(self.manifest))
            self.assertEqual(build_bundles(repo), self.bundles)
            unexpected = source / 'unexpected.txt'
            unexpected.write_text('not frozen artwork')
            with self.assertRaises(ValueError):
                build_bundles(repo)
            unexpected.unlink()
            png = source / 'previews/pic10-candidate-native4x.png'
            original = png.read_bytes()
            png.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            with self.assertRaises(ValueError):
                build_bundles(repo)
            png.write_bytes(original)
            moved = repo / 'outside-image.png'
            png.rename(moved)
            png.symlink_to(moved)
            with self.assertRaises(ValueError):
                build_bundles(repo)
            png.unlink()
            moved.rename(png)
            runtime = pack / 'startup-pic10-v1.hda'
            original = runtime.read_bytes()
            changed = bytearray(original)
            changed[64] ^= 1
            # Binary-valid but unreviewed pixels must still fail package checks.
            struct.pack_into('<Q', changed, 48, independent_fnv(changed[64:]))
            API['validate_resource'](changed)
            runtime.write_bytes(changed)
            with self.assertRaises(ValueError):
                build_bundles(repo)
            runtime.write_bytes(original)
            extra_runtime = pack / 'startup-pic4-v1.hda'
            extra_runtime.write_bytes(original)
            with self.assertRaises(ValueError):
                build_bundles(repo)


if __name__ == '__main__':
    unittest.main(verbosity=2)
