#!/usr/bin/env python3
"""Routing/inventory regressions for the sole installed startup pack.

Use actual repository pack bytes, while isolating the expensive canonical source
producer. The dedicated artwork/package suites remain the source rebuild gates.
"""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'prototype'))
import startup_manufacturer_bundle as manufacturer
import title_layer_bundle as title
import title_menu_font_bundle as menu
import settings_font_bundle as settings

PACK = 'startup-title-settings-v1'
RETIRED = ('startup-manufacturer-v1', 'startup-title-v1', 'startup-title-menu-v1')


class StartupRebuildChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
        cls.pack = ROOT / 'assets/hd/packs' / PACK
        cls.raw = {name: (cls.pack / name).read_bytes()
                   for name in manufacturer.CURRENT_RUNTIME_FILES}

    def fixture(self, root):
        pack = root / 'assets/hd/packs' / PACK
        pack.parent.mkdir(parents=True)
        shutil.copytree(self.pack, pack)
        (root / 'assets/hd/manifest.json').write_text(json.dumps(self.manifest))
        return pack

    def bundles(self, family):
        return {name: (self.raw[name], receipt)
                for name, receipt in self.manifest[family]['files'].items()}

    def test_only_current_pack_is_required_and_constants_are_explicit(self):
        for module in (manufacturer, title, menu, settings):
            self.assertEqual(module.PACK, PACK)
        self.assertEqual(manufacturer.SOURCE,
                         'assets/hd/artwork/startup-manufacturer-v1')
        self.assertEqual({p.name for p in self.pack.iterdir()},
                         manufacturer.CURRENT_RUNTIME_FILES)
        self.assertEqual(len(manufacturer.CURRENT_RUNTIME_FILES), 9)
        for name in RETIRED:
            self.assertFalse((ROOT / 'assets/hd/packs' / name).exists())

    def test_manifest_routes_and_all_current_bytes_match_exact_receipts(self):
        for family in ('startup_manufacturer_v1', 'startup_title_v1',
                       'startup_title_menu_v1', 'startup_settings_font_v1'):
            self.assertEqual(self.manifest[family]['pack'], PACK)
            for name, receipt in self.manifest[family]['files'].items():
                raw = self.raw[name]
                self.assertEqual(len(raw), receipt['bytes'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt['sha256'])
        self.assertEqual(self.manifest['startup_title_v1']['manufacturer_compatibility_source_pack'], PACK)
        self.assertEqual(self.manifest['startup_title_menu_v1']['compatibility_source_pack'], PACK)
        self.assertEqual(self.manifest['startup_settings_font_v1']['compatibility_source_pack'], PACK)

    def check_subset_verifier(self, module, family):
        bundles = self.bundles(family)
        receipt = self.manifest[family]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = self.fixture(root)
            with mock.patch.object(module, 'build_family', return_value=(bundles, receipt)):
                self.assertEqual(module.build_bundles(root), bundles)
                for name in bundles:
                    path = pack / name
                    raw = path.read_bytes()
                    path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
                    with self.assertRaises(ValueError):
                        module.build_bundles(root)
                    path.write_bytes(raw)
                for name in sorted(manufacturer.CURRENT_RUNTIME_FILES):
                    path = pack / name
                    raw = path.read_bytes()
                    path.unlink()
                    with self.assertRaises(ValueError):
                        module.build_bundles(root)
                    path.symlink_to(self.pack / name)
                    with self.assertRaises(ValueError):
                        module.build_bundles(root)
                    path.unlink()
                    path.write_bytes(raw)
                extra = pack / 'unreviewed.hda'
                extra.write_bytes(b'extra')
                with self.assertRaises(ValueError):
                    module.build_bundles(root)
                extra.unlink()
                changed = copy.deepcopy(self.manifest)
                changed[family]['count'] += 1
                (root / 'assets/hd/manifest.json').write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    module.build_bundles(root)

    def test_title_subset_current_inventory_corruption_and_receipt_rejections(self):
        self.check_subset_verifier(title, 'startup_title_v1')

    def test_menu_subset_current_inventory_corruption_and_receipt_rejections(self):
        self.check_subset_verifier(menu, 'startup_title_menu_v1')

    def test_title_manufacturer_is_built_from_canonical_source_helper(self):
        title_only = {name: item for name, item in self.bundles('startup_title_v1').items()
                      if name in title.TITLE_FILES}
        mfg = self.bundles('startup_manufacturer_v1')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            with mock.patch.object(title, 'source_receipts', return_value=self.manifest['startup_title_v1']['source_files']), \
                 mock.patch.object(title, 'build_resources', return_value=title_only), \
                 mock.patch.object(title, 'manufacturer_bundles', return_value=mfg) as producer:
                bundles, family = title.build_family(root)
                producer.assert_called_once_with(root.resolve())
                self.assertEqual(bundles, self.bundles('startup_title_v1'))
                self.assertEqual(family, self.manifest['startup_title_v1'])
                changed = dict(mfg)
                raw, receipt = changed['startup-pic10-v1.hda']
                changed['startup-pic10-v1.hda'] = (raw[:-1] + bytes([raw[-1] ^ 1]), receipt)
                producer.return_value = changed
                with self.assertRaises(ValueError):
                    title.build_family(root)

    def test_menu_builds_title_source_chain_without_legacy_pack(self):
        previous = self.bundles('startup_title_v1')
        raw = self.raw[menu.FILENAME]
        stamp = self.manifest['startup_title_menu_v1']['files'][menu.FILENAME]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            with mock.patch.object(menu, 'title_bundles', return_value=previous) as producer, \
                 mock.patch.object(menu, 'build_resource', return_value=(raw, stamp)), \
                 mock.patch.object(menu, 'source_receipts', return_value=self.manifest['startup_title_menu_v1']['source_files']):
                bundles, family = menu.build_family(root)
                producer.assert_called_once_with(root)
                self.assertEqual(bundles, self.bundles('startup_title_menu_v1'))
                self.assertEqual(family, self.manifest['startup_title_menu_v1'])

    def test_manufacturer_source_receipts_and_current_subset_fail_closed(self):
        # Synthetic frozen input inventory isolates routing. The real dedicated
        # manufacturer suite continues to decode/rebuild the canonical artwork.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = self.fixture(root)
            source = root / manufacturer.SOURCE
            for name in manufacturer.SOURCE_FILES:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(('fixture: ' + name).encode())
            (source / 'FILES.txt').write_text('\n'.join(sorted(manufacturer.SOURCE_FILES)) + '\n')
            sums = [hashlib.sha256((source / name).read_bytes()).hexdigest() + '  ' + name
                    for name in sorted(manufacturer.SOURCE_FILES - {'SHA256SUMS'})]
            (source / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
            manifest = copy.deepcopy(self.manifest)
            manifest['startup_manufacturer_v1']['source_files'] = {
                name: {'bytes': len((source / name).read_bytes()),
                       'sha256': hashlib.sha256((source / name).read_bytes()).hexdigest()}
                for name in manufacturer.SOURCE_FILES
            }
            (root / 'assets/hd/manifest.json').write_text(json.dumps(manifest))
            bundles = self.bundles('startup_manufacturer_v1')
            producer = mock.Mock(return_value=bundles)
            with mock.patch.object(manufacturer.runpy, 'run_path', return_value={'build_resources': producer}):
                self.assertEqual(manufacturer.build_bundles(root), bundles)
                producer.assert_called_once_with(source)
                path = source / 'prompts.json'
                original = path.read_bytes()
                path.write_bytes(original + b'changed')
                producer.reset_mock()
                with self.assertRaises(ValueError):
                    manufacturer.build_bundles(root)
                producer.assert_not_called()
                path.write_bytes(original)
                for name in manufacturer.RUNTIME_FILES:
                    path = pack / name
                    original = path.read_bytes()
                    path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
                    with self.assertRaises(ValueError):
                        manufacturer.build_bundles(root)
                    path.write_bytes(original)
                for name in manufacturer.CURRENT_RUNTIME_FILES:
                    path = pack / name
                    original = path.read_bytes()
                    path.unlink()
                    with self.assertRaises(ValueError):
                        manufacturer.build_bundles(root)
                    path.symlink_to(self.pack / name)
                    with self.assertRaises(ValueError):
                        manufacturer.build_bundles(root)
                    path.unlink()
                    path.write_bytes(original)
                (pack / 'extra.hda').write_bytes(b'')
                with self.assertRaises(ValueError):
                    manufacturer.build_bundles(root)

    def test_historical_view_projects_only_the_finite_pinned_retirement(self):
        manifest = copy.deepcopy(self.manifest)
        manifest.pop('startup_settings_font_v1')
        manufacturer.project_retired_resources_for_historical_checks(manifest)
        self.assertNotIn('retired_packs', manifest)
        self.assertEqual(tuple(manifest['packs']),
                         manufacturer.RETIRED_GAMEPLAY_PACKS + manufacturer.ACTIVE_GAMEPLAY_PACKS)
        self.assertEqual(manifest['startup_manufacturer_v1']['pack'], RETIRED[0])
        self.assertEqual(manifest['startup_title_v1']['pack'], RETIRED[1])
        self.assertEqual(manifest['startup_title_menu_v1']['pack'], RETIRED[2])
        self.assertEqual(self.manifest['startup_manufacturer_v1']['pack'], PACK)
        complete = copy.deepcopy(self.manifest)
        manufacturer.project_retired_resources_for_historical_checks(complete)
        self.assertEqual(complete['startup_settings_font_v1']['compatibility_source_pack'], RETIRED[2])

    def test_historical_view_rejects_changed_archive_default_and_startup_routes(self):
        for mutation in ('missing-archive', 'changed-archive', 'extra-archive',
                         'extra-active-pack', 'changed-default', 'changed-startup-route'):
            with self.subTest(mutation=mutation):
                manifest = copy.deepcopy(self.manifest)
                manifest.pop('startup_settings_font_v1')
                name = manufacturer.RETIRED_GAMEPLAY_PACKS[0]
                if mutation == 'missing-archive':
                    del manifest['retired_packs'][name]
                elif mutation == 'changed-archive':
                    manifest['retired_packs'][name]['count'] += 1
                elif mutation == 'extra-archive':
                    manifest['retired_packs']['unreviewed'] = manifest['retired_packs'][name]
                elif mutation == 'extra-active-pack':
                    manifest['packs']['unreviewed'] = {}
                elif mutation == 'changed-default':
                    manifest['default_preview_pack'] = name
                else:
                    manifest['startup_title_v1']['pack'] = RETIRED[1]
                with self.assertRaises(ValueError):
                    manufacturer.project_retired_resources_for_historical_checks(manifest)


if __name__ == '__main__':
    unittest.main(verbosity=2)
