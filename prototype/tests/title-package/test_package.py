#!/usr/bin/env python3
"""Finite title source/package tests. No engine, render, capture or aggregate build."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('title_layer_bundle', ROOT / 'prototype/title_layer_bundle.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
sys.modules[spec.name] = bundle

# Independent protocol pins, deliberately not imported from the producer.
EXPECTED = {
    'title-pic4-v1.hda': ('pic4', 4, 320, 200, 0, None,
        0x9a3f7cb8ec37073e, 0x9c9baa40cbccf525, 0x0abb22518a6634df,
        4096080, '0149d26dd7c860f497089f27d5650dec7af21846ad92cc8269a66b5375592c31'),
    'title-planet146-v1.hda': ('tyrian146', 146, 304, 121, 1, (4, 4, 1216, 484),
        0x30f8dbf0554a03ae, 0x0cb7de8084912543, 0x623a5b10ca52dae3,
        2354256, 'ff126712e87c052b2176365b228a8248d5ec7e04386e5d233614405e51537b05'),
    'title-planet151-v1.hda': ('year151', 151, 162, 64, 1, (8, 8, 644, 252),
        0x4562ec954d257998, 0xee71b0121c53f8df, 0x0df98d9dd374ce169,
        663632, '325c3602bce555f3b8023dd6b6167099d540fc828bf9e84c3bd21b85d0787357'),
}
SOURCE_MANIFEST = 'd7bd240f1210d01c3d0e01a81ec5511fe02be7972014d6564e333c54306bd7cc'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def independent_fnv(data):
    result = 0xcbf29ce484222325
    for byte in data:
        result ^= byte
        result = (result * 0x100000001b3) % (1 << 64)
    return result


class TitlePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ROOT / 'assets/hd/artwork/title-screen-v1'
        cls.runtime = ROOT / 'assets/hd/packs/startup-title-v1'
        cls.manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
        cls.bundles = bundle.build_bundles(ROOT)
        cls.family = cls.manifest['startup_title_v1']

    def test_exact_headers_hashes_and_canonical_payloads(self):
        self.assertEqual(struct.calcsize('<4s11I4Q'), 80)
        for filename, (asset, identity, w, h, alpha, bounds, indices, mask, payload_fnv, size, digest) in EXPECTED.items():
            with self.subTest(filename=filename):
                raw = (self.runtime / filename).read_bytes()
                fields = struct.unpack('<4s11I4Q', raw[:80])
                self.assertEqual(fields, (b'TLV1', 1, 4, identity, w, h, 8, alpha,
                                          w * h * 64, 0, 0, 0,
                                          indices, mask, 0x8f64628a08533287, payload_fnv))
                self.assertEqual(len(raw), size)
                self.assertEqual(sha(raw), digest)
                self.assertEqual(independent_fnv(raw[80:]), payload_fnv)
                with Image.open(self.source / 'canonical' / (asset + '-canonical4x.png')) as image:
                    self.assertEqual(image.mode, 'RGBA')
                    self.assertEqual(image.size, (w * 4, h * 4))
                    self.assertEqual(raw[80:], image.tobytes())
                self.assertEqual(self.family['files'][filename]['header_u32'], list(fields[1:12]))

    def test_opaque_background_straight_alpha_and_exact_support(self):
        for filename, (_, _, w, h, alpha_mode, bounds, *_) in EXPECTED.items():
            payload = (self.runtime / filename).read_bytes()[80:]
            image = Image.frombytes('RGBA', (w * 4, h * 4), payload)
            alpha = image.getchannel('A')
            if alpha_mode == 0:
                self.assertEqual(alpha.getextrema(), (255, 255))
            else:
                self.assertTrue(any(0 < value < 255 for value in alpha.tobytes()))
                self.assertEqual(alpha.getbbox(), bounds)
                for y in range(h * 4):
                    row = alpha.tobytes()[y * w * 4:(y + 1) * w * 4]
                    outside = row if y < bounds[1] or y >= bounds[3] else row[:bounds[0]] + row[bounds[2]:]
                    self.assertFalse(any(outside))
            self.assertTrue(all(payload[i:i + 3] == b'\0\0\0'
                                for i in range(0, len(payload), 4) if payload[i + 3] == 0))

    def test_frozen_source_inventory_and_generated_raster_scope(self):
        self.assertEqual(sha((self.source / 'manifest.json').read_bytes()), SOURCE_MANIFEST)
        self.assertEqual(len(self.family['source_files']), 19)
        actual = {p.relative_to(self.source).as_posix() for p in self.source.rglob('*') if p.is_file()}
        self.assertEqual(actual, set(self.family['source_files']))
        self.assertEqual({name for name in actual if name.endswith('.png')}, {
            'canonical/pic4-canonical4x.png', 'canonical/tyrian146-canonical4x.png',
            'canonical/year151-canonical4x.png', 'masters/left-clearance-master.png',
            'masters/pic4-master.png', 'masters/right-clearance-master.png',
            'masters/tyrian146-master.png', 'masters/year151-master.png',
            'proof/tyrian-alpha-correction-boundary-mask4x.png',
        })
        for name, receipt in self.family['source_files'].items():
            raw = (self.source / name).read_bytes()
            self.assertEqual(receipt, {'bytes': len(raw), 'sha256': sha(raw)})
        source_manifest = json.loads((self.source / 'manifest.json').read_text())
        self.assertEqual(len(source_manifest['files']), 17)
        self.assertEqual(source_manifest['total_bytes_excluding_manifest_and_FILES'], 8997880)
        self.assertIn('alpha only from two generated component masters', (self.source / 'README.md').read_text())
        self.assertIn('Original game image pixels', (self.source / 'README.md').read_text())
        self.assertEqual((self.source / 'requirements.txt').read_text().strip(), 'Pillow==12.3.0')

    def test_existing_manifest_fields_and_bytes_unchanged_from_baseline(self):
        baseline = subprocess.check_output(['git', 'show', 'aba8650:assets/hd/manifest.json'], cwd=ROOT)
        actual = (ROOT / 'assets/hd/manifest.json').read_bytes()
        self.assertTrue(actual.startswith(baseline[:-3] + b',\n'))
        without_title = dict(self.manifest)
        del without_title['startup_title_v1']
        self.assertEqual(without_title, json.loads(baseline))
        self.assertNotIn('startup-title-v1', self.manifest['packs'])
        self.assertEqual(self.family['count'], 5)
        self.assertEqual(self.family['title_count'], 3)
        self.assertEqual(self.family['manufacturer_compatibility_count'], 2)

    def test_original_mfg1_family_source_and_pack_are_unchanged(self):
        paths = ['assets/hd/artwork/startup-manufacturer-v1',
                 'assets/hd/packs/startup-manufacturer-v1', 'prototype/startup_manufacturer_bundle.py']
        subprocess.run(['git', 'diff', '--exit-code', '1df1d87', '--', *paths], cwd=ROOT, check=True,
                       capture_output=True)
        original = self.manifest['startup_manufacturer_v1']
        for name, receipt in original['files'].items():
            source = ROOT / 'assets/hd/packs/startup-manufacturer-v1' / name
            copy = self.runtime / name
            self.assertEqual(source.read_bytes(), copy.read_bytes())
            self.assertEqual(self.family['files'][name], receipt)
            self.assertEqual(sha(copy.read_bytes()), receipt['sha256'])
            self.assertEqual(copy.read_bytes()[:4], b'MFG1')

    def test_independent_family_receipt_and_separate_byte_accounting(self):
        bundles, receipt = bundle.build_family(ROOT)
        self.assertEqual(receipt, self.family)
        self.assertEqual(bundles, self.bundles)
        title_total = sum(len(raw) for name, (raw, _) in bundles.items() if name in EXPECTED)
        copies_total = sum(len(raw) for name, (raw, _) in bundles.items() if name not in EXPECTED)
        self.assertEqual(title_total, 7113968)
        self.assertEqual(copies_total, 8192128)
        self.assertEqual(title_total, self.family['title_resource_bytes'])
        self.assertEqual(copies_total, self.family['manufacturer_compatibility_bytes'])
        self.assertEqual(len(list(self.runtime.iterdir())), 5)

    def test_source_only_relocated_rebuild_is_exact(self):
        report = bundle.verify_source_rebuild(ROOT)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['movement_positions'], 29)
        self.assertEqual(report['output_files'], 11)
        self.assertEqual(len(report['assets']), 3)

    def test_source_builder_rejects_unsafe_output_paths_without_changes(self):
        before = bundle.source_receipts(self.source)
        with tempfile.TemporaryDirectory(prefix='title-path-guards-') as temporary:
            existing = Path(temporary) / 'exists'
            existing.mkdir()
            link = Path(temporary) / 'link'
            link.symlink_to(existing, target_is_directory=True)
            candidates = ['relative-output', str(existing), str(self.source / 'unsafe-output'),
                          str(self.source.parent), str(link / 'output'), str(Path(temporary) / 'absent' / 'output')]
            for output in candidates:
                with self.subTest(output=output):
                    result = subprocess.run([sys.executable, '-B', str(self.source / 'build.py'), '--output', output],
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('ValueError', result.stderr)
            self.assertFalse((self.source / 'unsafe-output').exists())
        self.assertEqual(before, bundle.source_receipts(self.source))

    def test_source_inventory_hash_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix='title-source-rejections-') as temporary:
            target = Path(temporary) / 'source'
            shutil.copytree(self.source, target)
            for name in ('README.md', 'build.py', 'canonical/pic4-canonical4x.png', 'FILES.sha256', 'manifest.json'):
                with self.subTest(changed=name):
                    path = target / name
                    previous = path.read_bytes()
                    path.write_bytes(previous + b'\n')
                    with self.assertRaises(ValueError):
                        bundle.source_receipts(target)
                    path.write_bytes(previous)
            sums = target / 'FILES.sha256'
            saved_sums = sums.read_bytes()
            sums.write_bytes(saved_sums.rstrip(b'\n'))
            with self.assertRaisesRegex(ValueError, 'FILES.sha256'):
                bundle.source_receipts(target)
            sums.write_bytes(saved_sums)
            extra = target / 'reference-original.png'
            extra.write_bytes(b'not permitted')
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            extra.unlink()
            empty = target / 'extra-directory'
            empty.mkdir()
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            empty.rmdir()
            path = target / 'README.md'
            saved = path.read_bytes()
            path.unlink()
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            path.symlink_to(self.source / 'README.md')
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            path.unlink()
            path.write_bytes(saved)
            symlink_root = Path(temporary) / 'source-link'
            symlink_root.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                bundle.source_receipts(symlink_root)
            self.assertEqual(bundle.source_receipts(target), self.family['source_files'])

    def test_checked_file_rejects_escape_absolute_and_nonregular(self):
        with tempfile.TemporaryDirectory(prefix='title-path-rejections-') as temporary:
            root = Path(temporary)
            for name in ('../outside', '/etc/passwd', '.'):
                with self.subTest(path=name), self.assertRaises(ValueError):
                    bundle.checked_file(root, name)
            if hasattr(os, 'mkfifo'):
                os.mkfifo(root / 'pipe')
                with self.assertRaises(ValueError):
                    bundle.checked_file(root, 'pipe')
                with self.assertRaises(ValueError):
                    bundle.require_inventory(root, {'pipe'}, 'test tree')

    def test_alpha_policy_rejects_hidden_rgb_opaque_and_support_errors(self):
        # A small straight-alpha logo keeps partial coverage and clean padding.
        pixels = bytearray(4 * 4 * 4)
        pixels[4 * 5:4 * 5 + 4] = b'\x20\x40\x60\x80'
        bundle.validate_rgba(bytes(pixels), 4, 4, 1, (1, 1, 3, 3))
        hidden = bytearray(pixels)
        hidden[0] = 1
        with self.assertRaisesRegex(ValueError, 'hidden RGB'):
            bundle.validate_rgba(bytes(hidden), 4, 4, 1, (1, 1, 3, 3))
        outside = bytearray(pixels)
        outside[3] = 1
        with self.assertRaisesRegex(ValueError, 'support bound'):
            bundle.validate_rgba(bytes(outside), 4, 4, 1, (1, 1, 3, 3))
        no_partial = bytearray(pixels)
        no_partial[4 * 5 + 3] = 255
        with self.assertRaisesRegex(ValueError, 'partial alpha'):
            bundle.validate_rgba(bytes(no_partial), 4, 4, 1, (1, 1, 3, 3))
        with self.assertRaisesRegex(ValueError, 'entirely opaque'):
            bundle.validate_rgba(bytes(pixels), 4, 4, 0, None)
        with self.assertRaisesRegex(ValueError, 'Unsupported alpha mode'):
            bundle.validate_rgba(bytes(pixels), 4, 4, 2, (1, 1, 3, 3))
        with self.assertRaisesRegex(ValueError, 'byte count'):
            bundle.validate_rgba(bytes(pixels[:-1]), 4, 4, 1, (1, 1, 3, 3))

    def test_runtime_inventory_bytes_and_manifest_receipt_fail_closed(self):
        # Isolate final on-disk checks from the already-tested expensive producer.
        with tempfile.TemporaryDirectory(prefix='title-runtime-rejections-') as temporary:
            repo = Path(temporary)
            runtime = repo / 'assets/hd/packs/startup-title-v1'
            runtime.parent.mkdir(parents=True)
            shutil.copytree(self.runtime, runtime)
            manifest_path = repo / 'assets/hd/manifest.json'
            manifest_path.write_text(json.dumps(self.manifest))
            with mock.patch.object(bundle, 'build_family', return_value=(self.bundles, self.family)):
                for name in self.bundles:
                    with self.subTest(runtime=name):
                        path = runtime / name
                        original = path.read_bytes()
                        path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
                        with self.assertRaisesRegex(ValueError, 'Runtime bytes'):
                            bundle.build_bundles(repo)
                        path.write_bytes(original)
                extra = runtime / 'extra.hda'
                extra.write_bytes(b'')
                with self.assertRaises(ValueError):
                    bundle.build_bundles(repo)
                extra.unlink()
                path = runtime / 'title-pic4-v1.hda'
                original = path.read_bytes()
                path.unlink()
                with self.assertRaises(ValueError):
                    bundle.build_bundles(repo)
                path.symlink_to(self.runtime / path.name)
                with self.assertRaises(ValueError):
                    bundle.build_bundles(repo)
                path.unlink()
                path.write_bytes(original)
                malformed = json.loads(json.dumps(self.manifest))
                malformed['startup_title_v1']['count'] = 3
                manifest_path.write_text(json.dumps(malformed))
                with self.assertRaisesRegex(ValueError, 'independent receipt'):
                    bundle.build_bundles(repo)

    def test_aggregate_title_block_verifies_and_outputs_only_five_files(self):
        # Execute only the real title-family block, never the aggregate rebuild.
        text = (ROOT / 'prototype/build-hd-assets.py').read_text()
        block = text[text.index('title_count=0\n'):text.index('type4_count=0\n')]
        with tempfile.TemporaryDirectory(prefix='title-aggregate-block-') as temporary:
            namespace = {'repo': ROOT, 'manifest': self.manifest,
                         'a': SimpleNamespace(output=True), 'output': Path(temporary)}
            exec(compile(block, 'build-hd-assets.py:title-family-only', 'exec'), namespace)
            self.assertEqual(namespace['title_count'], 3)
            self.assertEqual(namespace['title_source_count'], 19)
            self.assertEqual(namespace['title_compatibility_count'], 2)
            output = Path(temporary) / 'startup-title-v1'
            self.assertEqual({p.name for p in output.iterdir()}, set(self.bundles))
            for name, (raw, _) in self.bundles.items():
                self.assertEqual((output / name).read_bytes(), raw)
            self.assertEqual({p.name for p in Path(temporary).iterdir()}, {'startup-title-v1'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
