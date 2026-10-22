#!/usr/bin/env python3
"""Finite shield-only boundary and deterministic material checks.

No projection fixtures, game loop, network or original-data redistribution.
"""
from pathlib import Path
import hashlib
import json
import struct
import unittest
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
# The combined public batch has independent history. Check the finite shield
# authoring/runtime boundary directly; publication overlay scope is checked by
# the publisher, without making the tests depend on a private development base.
REQUIRED_SHIELD_ASSETS = {
    'shop-shield-option26-v1.hda', 'shop-shield-option26-v1.json',
    'shield-alpha8-roleq4-4x.bin', 'shield-alpha-4x.png', 'shield-role-q4-4x.png',
}
OPTIONAL_REVIEW_PREVIEWS = {'reviewed-assembly-preview.png', 'reviewed-values-preview.png'}
SHIELD_INTEGRATION_PATHS = {
    'src/pregame_font.c', 'src/shop_shield_material_pins.h',
    'scripts/export_shop_shield.py', 'docs/shop-shield-material.md',
    'tests/shop_shield_test.c', 'tests/run_shop_shield_tests.sh',
    'tests/test_shop_shield_boundary.py', 'tests/test_runtime_packaging.py',
    'scripts/update_runtime_manifest.py', 'packaging/runtime-selection-v1.json',
    'packaging/runtime-assets-v1.json', 'docs/runtime-packaging.md',
}
SHIELD_SOURCE_SHA256 = {
    'scripts/export_shop_shield.py': 'd3668c4e51033be15d6347988084e592c81a007934a5e18f1109a2965a8668f7',
    'src/shop_shield_material_pins.h': 'd0429c705a0fd7c1a7259c20eeed811205e902ff204ffc74b7e2bb228585a695',
}


def fnv(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return value


class ShieldBoundary(unittest.TestCase):
    def test_finite_shield_source_and_material_inventory(self):
        directory = ROOT / 'assets/shop-shield-v1'
        leaves = {path.name for path in directory.iterdir()}
        self.assertTrue(REQUIRED_SHIELD_ASSETS <= leaves)
        self.assertFalse(leaves - REQUIRED_SHIELD_ASSETS - OPTIONAL_REVIEW_PREVIEWS)
        for name in leaves:
            self.assertTrue((directory / name).is_file(), name)
            self.assertFalse((directory / name).is_symlink(), name)
        for name in SHIELD_INTEGRATION_PATHS:
            self.assertTrue((ROOT / name).is_file(), name)
            self.assertFalse((ROOT / name).is_symlink(), name)
        for name, digest in SHIELD_SOURCE_SHA256.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        selection = json.loads((ROOT / 'packaging/runtime-selection-v1.json').read_text())
        self.assertEqual(selection['shop_runtime_extension'], '.hda')
        self.assertEqual(selection['shop_runtime_directories'].count('assets/shop-shield-v1'), 1)
        self.assertEqual({p.name for p in directory.glob('*.hda')}, {'shop-shield-option26-v1.hda'})

    def test_material_header_and_pins(self):
        data = (ROOT/'assets/shop-shield-v1/shop-shield-option26-v1.hda').read_bytes()
        self.assertEqual(len(data), 72992)
        self.assertEqual(hashlib.sha256(data).hexdigest(), 'd93bf60729fc2154c0274847e01910e15484db34935d296782d7d7b218c547a2')
        self.assertEqual(data[:4], b'PSS1')
        self.assertEqual(struct.unpack_from('<15I', data, 4), (1,5,26,99,23,4,396,92,28,23,36432,36432,15,4,0))
        self.assertEqual(struct.unpack_from('<8Q', data, 64), (0x45a77a2246c174b9,0x1c6687307999bd82,0x2b70bbc97a03a906,0xb2954b44fe9312bd,0xb3481df839c0dec8,0x12adb0f5c62fab83,0,0))
        payload = data[128:]
        self.assertEqual(fnv(payload), 0x12adb0f5c62fab83)
        self.assertEqual(fnv(payload[:36432]), 0x9c0ae0f6a65255c9)
        self.assertEqual(fnv(payload[36432:]), 0x747a5079e7a8a3ef)
        self.assertEqual(payload, (ROOT/'assets/shop-shield-v1/shield-alpha8-roleq4-4x.bin').read_bytes())
        self.assertTrue(all(r <= 240 and (a or not r) for a,r in zip(payload[:36432],payload[36432:])))
        header = (ROOT/'src/shop_shield_material_pins.h').read_text()
        self.assertIn('#define PF_SHIELD_HASH UINT64_C(0x12adb0f5c62fab83)', header)

    def test_runtime_one_hda_and_no_development_material(self):
        manifest = json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text())
        rows = [r for r in manifest['files'] if r['source_path'].startswith('assets/shop-shield-v1/')]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['source_path'], 'assets/shop-shield-v1/shop-shield-option26-v1.hda')
        self.assertEqual(rows[0]['group'], 'shop')
        self.assertEqual(rows[0]['destination'], 'assets/startup/shop-shield-option26-v1.hda')
        self.assertEqual(rows[0]['bytes'], 72992)
        # Explicit current SHOP closure, not a count that silently admits any
        # replacement set. Shared reconstructed text runs use a separate group.
        expected = {
            'shop-frame-metal-v1.hda', 'shop-front-weapon00-v1.hda',
            'shop-generator-weapon16-v1.hda', 'shop-talon-option31-v1.hda',
            'shop-shield-option26-v1.hda',
            *{f'shop-menu-run{i}-v1.hda' for i in range(7)},
            *{f'shop-static-newsh1-quad{i}-v1.hda' for i in (169, 199, 235)},
        }
        shop = [r for r in manifest['files'] if r['group'] == 'shop']
        self.assertEqual(len(shop), len(expected))
        self.assertEqual({r['destination'] for r in shop},
                         {'assets/startup/'+name for name in expected})
        self.assertEqual(manifest['closure']['shop_files'], len(expected))
        # Replace obsolete unrelated whole-package byte/count constants with
        # an exact fresh reconstruction from the finite approved inventories.
        with tempfile.TemporaryDirectory(prefix='shield-package-closure-') as temp:
            output = Path(temp)/'runtime.json'
            subprocess.run([sys.executable,
                            str(ROOT/'scripts/rebuild_recovered_runtime_manifest.py'),
                            '--root', str(ROOT), '--output', str(output)],
                           check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(output.read_text()), manifest)


if __name__ == '__main__':
    unittest.main(verbosity=2)
