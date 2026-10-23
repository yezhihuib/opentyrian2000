#!/usr/bin/env python3
"""Bounded NEWSHF pin checks; no original data copied into fixtures/artifacts."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import build_newshf_prototype_pins as pins


class PrototypePins(unittest.TestCase):
    def test_frozen_header_and_source(self):
        report = pins.verify()
        self.assertEqual(report['status'], 'PASS')
        self.assertFalse(report['original_bytes_verified'])
        self.assertEqual(report['scope'], 'identity-only-no-rendering')

    def test_exact_identity_and_geometry_contract(self):
        text = pins.HEADER.read_text()
        self.assertIn('{163u,167u,168u}', text)
        self.assertIn('{{125u,123u,127u},{3u,1u,5u},{55u,17u,93u}}', text)
        self.assertIn('BANK_BYTES 33543u', text)
        self.assertNotIn('GlobalAssetResource', text)
        self.assertNotIn('.hda', text)
        self.assertIn('NEWSHF_PROTOTYPE_PALETTE_FNV UINT64_C(', text)
        self.assertNotIn('newshf_prototype_palette[', text)
        self.assertNotIn('static const uint32_t', text)
        self.assertEqual(pins.IDENTITY['logical_bank'], 10)
        self.assertEqual(pins.IDENTITY['logical_size'], [24,28])
        self.assertEqual(pins.IDENTITY['logical_anchor'], [6,7])

    def test_header_change_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'pins.h'
            path.write_bytes(pins.HEADER.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError, 'header drift'):
                pins.verify(header=path)

    def test_header_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'pins.h'
            path.symlink_to(pins.HEADER)
            with self.assertRaisesRegex(ValueError, 'unsafe'):
                pins.verify(header=path)

    def test_source_extra_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'source'
            shutil.copytree(pins.DEFAULT, path)
            (path/'unrelated.png').write_bytes(b'not an allowed source')
            with self.assertRaisesRegex(ValueError, 'source-bundle'):
                pins.verify(source=path)

    def test_unpinned_source_change_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'source'
            shutil.copytree(pins.DEFAULT, path)
            png = next(path.glob('*.png'))
            png.write_bytes(png.read_bytes()+b'changed')
            with self.assertRaisesRegex(ValueError, 'art hash'):
                pins.verify(source=path)

    def test_source_identity_change_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'source'
            shutil.copytree(pins.DEFAULT, path)
            manifest = path/'manifest.json'
            manifest.write_text(manifest.read_text().replace('"logical_bank": 10', '"logical_bank": 1'))
            with self.assertRaisesRegex(ValueError, 'immutable'):
                pins.verify(source=path)

    def test_fnv_standard_vectors(self):
        self.assertEqual(pins.fnv64(b''), 0xcbf29ce484222325)
        self.assertEqual(pins.fnv64(b'a'), 0xaf63dc4c8601ec8c)

    def test_synthetic_decoder(self):
        # One index offset, one opaque pixel, then native terminator.
        decoded = pins.decode(b'\x02\x00\x10\x35\x0f', 1)
        self.assertEqual(len(decoded), 336)
        self.assertEqual(decoded[0], 0x35)
        self.assertEqual(decoded[168], 255)
        self.assertEqual(sum(decoded[1:168]), 0)
        self.assertEqual(sum(decoded[169:]), 0)
        for bank, index in [(b'',1),(b'\x02\x00',1),(b'\x02\x00\xf0',1),(b'\x02\x00\x0f',0)]:
            with self.assertRaises(ValueError):
                pins.decode(bank,index)

    def test_unverified_originals_rejected(self):
        with self.assertRaisesRegex(ValueError, 'bank pin'):
            pins.derive(b'\0'*33543, b'', b'')

    def test_cli_no_write_without_game_data(self):
        before = pins.HEADER.read_bytes()
        run = subprocess.run([sys.executable,str(ROOT/'scripts/build_newshf_prototype_pins.py'),'--write'], capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('requires --game-data', run.stderr)
        self.assertEqual(pins.HEADER.read_bytes(), before)

    @unittest.skipUnless(os.environ.get('NEWSHF_PRIVATE_GAME_DATA'), 'private originals not supplied')
    def test_private_reproduction_and_memory_only_negative_cases(self):
        p = Path(os.environ['NEWSHF_PRIVATE_GAME_DATA'])
        self.assertTrue(pins.verify(game_data=p)['original_bytes_verified'])
        data = [(p/n).read_bytes() for n in ('newshf.shp','tyrian.hdt','palette.dat')]
        for index in range(3):
            bad = list(data)
            mutated = bytearray(bad[index]); mutated[-1] ^= 1; bad[index] = bytes(mutated)
            with self.assertRaises(ValueError):
                pins.derive(*bad)
        self.assertEqual(pins.derive(*data), pins.HEADER.read_bytes())


if __name__ == '__main__':
    unittest.main()
