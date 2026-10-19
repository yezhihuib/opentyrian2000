#!/usr/bin/env python3
"""Retired-checkpoint migration tests, using only isolated synthetic image data."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('rebuild_retired_hd_pack', ROOT / 'prototype/rebuild_retired_hd_pack.py')
REBUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REBUILD)


class RetiredPackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='retired-pack-test-')
        self.base = Path(self.temp.name)
        self.repo = self.base / 'repo'
        self.source = self.repo / 'assets/hd/source/fixture.png'
        self.source.parent.mkdir(parents=True)
        self.image = Image.new('RGBA', (8, 12), (15, 45, 90, 255))
        self.image.save(self.source)
        self.header = [42, 4, 2, 3, 0xffffffff, 0]
        self.raw = b'HDR1' + struct.pack('<6I', *self.header) + self.image.tobytes()
        self.item = {'source_png': 'assets/hd/source/fixture.png', 'source_png_sha256': hashlib.sha256(self.source.read_bytes()).hexdigest(), 'header_u32': self.header, 'sha256': hashlib.sha256(self.raw).hexdigest()}
        self.manifest = {'packs': {'current': {}}, 'retired_packs': {'retired-fixture': {'count': 1, 'files': {'fixture.hda': self.item}}}}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        (self.repo / 'assets/hd/manifest.json').write_text(json.dumps(self.manifest))

    def build(self, name='retired-fixture', output=None):
        return REBUILD.build_pack(self.repo, name, output or self.base / 'out')

    def test_rebuild_is_exact_and_does_not_require_installed_old_directory(self):
        before = self.source.read_bytes()
        receipt = self.build()
        self.assertEqual((self.base / 'out/fixture.hda').read_bytes(), self.raw)
        self.assertEqual(receipt['files'], 1)
        self.assertEqual(receipt['bytes'], len(self.raw))
        self.assertEqual(before, self.source.read_bytes())
        self.assertFalse((self.repo / 'assets/hd/packs').exists())

    def test_existing_output_and_repository_output_refused(self):
        self.build()
        with self.assertRaises(ValueError): self.build()
        with self.assertRaises(ValueError): self.build(output=self.repo / 'new-pack')

    def test_unknown_active_and_unsafe_names_refused(self):
        for name in ['current', 'unknown', '../escape', '/absolute', 'a/b', r'a\b']:
            with self.subTest(name=name), self.assertRaises(ValueError): self.build(name)
        self.assertFalse((self.base / 'out').exists())

    def test_source_mutation_is_rejected_before_output(self):
        Image.new('RGBA', (8, 12), (99, 88, 77, 255)).save(self.source)
        with self.assertRaises(ValueError): self.build()
        self.assertFalse((self.base / 'out').exists())

    def test_header_payload_or_count_mutation_is_rejected(self):
        for field, value in [('sha256', '0' * 64), ('header_u32', [1] * 6), ('source_png', '../outside.png')]:
            old = self.item[field]
            self.item[field] = value
            self.save()
            with self.subTest(field=field), self.assertRaises((ValueError, FileNotFoundError)): self.build()
            self.assertFalse((self.base / 'out').exists())
            self.item[field] = old
        self.manifest['retired_packs']['retired-fixture']['count'] = 2
        self.save()
        with self.assertRaises(ValueError): self.build()

    def test_source_and_parent_symlinks_refused(self):
        real = self.base / 'real.png'
        self.source.rename(real)
        self.source.symlink_to(real)
        with self.assertRaises(ValueError): self.build()
        parent = self.base / 'linked-parent'
        parent.symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(ValueError): self.build(output=parent / 'out')

    def test_bad_later_recipe_does_not_leave_partial_output(self):
        pack = self.manifest['retired_packs']['retired-fixture']
        pack['files']['bad.hda'] = dict(self.item, sha256='0' * 64)
        pack['count'] = 2
        self.save()
        with self.assertRaises(ValueError): self.build()
        self.assertFalse((self.base / 'out').exists())

    def test_current_manifest_separates_live_and_archived_packs(self):
        manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
        self.assertEqual(set(manifest['packs']), {manifest['default_preview_pack'], manifest['default_debug_pack']})
        self.assertEqual(len(manifest['retired_packs']), 16)
        self.assertEqual(sum(x['count'] for x in manifest['retired_packs'].values()), 2236)
        self.assertTrue(set(manifest['packs']).isdisjoint(manifest['retired_packs']))
        canonical = json.dumps(manifest['retired_packs'], sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), 'adec3a11fc1d08fe2e598039547352afda3c5291c3afed7ba332b259ea54024b')
        for name in manifest['retired_packs']:
            self.assertFalse((ROOT / 'assets/hd/packs' / name).exists())
        for name in ['startup-manufacturer-v1', 'startup-title-v1', 'startup-title-menu-v1']:
            self.assertFalse((ROOT / 'assets/hd/packs' / name).exists())
        for key in ['startup_manufacturer_v1', 'startup_title_v1', 'startup_title_menu_v1', 'startup_settings_font_v1']:
            self.assertEqual(manifest[key]['pack'], 'startup-title-settings-v1')


if __name__ == '__main__':
    unittest.main()
