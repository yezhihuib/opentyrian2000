#!/usr/bin/env python3
"""Reviewed authored smoke resources and reproducible registry pins; no game data."""
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fnv64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return value


class SmokeRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / 'assets/hd/global-assets-v1/registry.json').read_text())
        self.family = self.registry['families'][5]

    def test_exact_phase_and_role_scope(self):
        f = self.family
        self.assertEqual(f['name'], 'moving-white-smoke')
        self.assertEqual([p['index'] for p in f['phases']], list(range(135, 142)))
        self.assertEqual([p['ttl'] for p in f['phases']], list(range(7, 0, -1)))
        self.assertEqual([p['resource_identity'] for p in f['phases']], list(range(1060135, 1060142)))
        self.assertEqual(f['draw_semantics']['slot_contract']['input_types'], [6, 98, 198])
        self.assertFalse(f['draw_semantics']['slot_contract']['fixedPosition'])
        self.assertFalse(f['draw_semantics']['slot_contract']['followPlayer'])
        self.assertEqual(f['source_identity']['bank_bytes'], 17810)
        self.assertEqual([t['index'] for t in f['source_identity']['tiles']], list(range(135, 142)))
        pal = f['source_identity']['palette']
        self.assertEqual((pal['first_index'], pal['count']), (9, 7))
        self.assertEqual(hashlib.sha256(bytes.fromhex(''.join(pal['rgb_hex']))).hexdigest(), pal['rgb21_sha256'])

    def test_seven_resources_are_exact_existing_approved_bytes(self):
        resources = self.registry['resources'][49:56]
        manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
        self.assertEqual(len(resources), 7)
        for n, r in enumerate(resources):
            p = ROOT / 'assets/hd/global-assets-v1' / r['path']
            self.assertFalse(p.is_symlink())
            b = p.read_bytes()
            self.assertEqual(len(b), 43036)
            self.assertEqual(hashlib.sha256(b).hexdigest(), r['sha256'])
            self.assertEqual(r['path'], 'content/' + r['sha256'] + '.hda')
            self.assertEqual(b[:4], b'HDR1')
            self.assertEqual(list(struct.unpack('<6I', b[4:28])), [1060135+n, 8, 12, 14, 0, 0])
            self.assertEqual(f'{fnv64(b[28:]):016x}', r['payload_fnv64'])
            provenance = r['provenance']
            old = ROOT / 'assets/hd/packs' / provenance['pack'] / provenance['file']
            self.assertEqual(b, old.read_bytes())
            approval = manifest['packs'][provenance['pack']]['files'][provenance['file']]
            self.assertEqual(approval['sha256'], r['sha256'])
            self.assertEqual(hashlib.sha256((ROOT / provenance['source_png']).read_bytes()).hexdigest(), approval['source_png_sha256'])

    def test_generator_reproduces_checked_in_header(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'pins.h'
            subprocess.run([sys.executable, str(ROOT / 'scripts/build_global_registry_header.py'),
                            '--registry', str(ROOT / 'assets/hd/global-assets-v1/registry.json'),
                            '--output', str(output)], check=True, capture_output=True)
            self.assertEqual(output.read_bytes(), (ROOT / 'src/global_asset_registry.h').read_bytes())


if __name__ == '__main__':
    unittest.main()
