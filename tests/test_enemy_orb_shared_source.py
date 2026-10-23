#!/usr/bin/env python3
"""Fixed approved orb input binding, without private data or original-RLE proof."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('orb_shared_source', ROOT / 'prototype/build-asteroid1-orb112113-art.py')
ORB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORB)
ART = Path('assets/hd/artwork/asteroid1-orb112113-v1')
PACK = ROOT / 'assets/hd/packs/asteroid1-ten-v1'
PINS = {
    112: 'c28da6740c5827bab6e2ab44faf0e5218fb8f033af7c6bc500d80167cf47405b',
    113: '49a4ef3fe0c25cb5cabe153a83d4cf72fc204c45872af83178521d33a902d412',
}


def approved_output(selector):
    with Image.open(ROOT / ART / f'enemy-orb112113-{selector}-8.png') as image:
        return np.array(image)


def public_mask(selector):
    # This oracle proves equivalence to approved public output, not original RLE.
    rgba = approved_output(selector)
    return (rgba[:, :, 3] > 0).reshape(14, 8, 12, 8).any(axis=(1, 3))


class SharedSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='orb-shared-source-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'
        self.records = json.loads((ROOT / ORB.SELECTED).read_bytes())
        self.manifest = self.root / ORB.SELECTED
        self.manifest.parent.mkdir(parents=True)
        self.save(self.records)
        for row in self.records:
            self.write(row['source_png'], (ROOT / row['source_png']).read_bytes())
        for selector in PINS:
            path = ART / f'retained-source-{selector}.png'
            self.write(path, (ROOT / path).read_bytes())

    def write(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def save(self, records):
        self.manifest.write_text(json.dumps(records), encoding='utf-8')

    def reject_before_output(self):
        output = self.base / 'must-not-exist'
        with mock.patch.object(ORB, 'ROOT', self.root), mock.patch.object(ORB, 'decode') as decode:
            with self.assertRaises(ValueError):
                ORB.main(['--data', str(self.base / 'no-private-data'), '--out', str(output)])
            decode.assert_not_called()
        self.assertFalse(output.exists())

    def test_fixed_approved_sources_and_binding(self):
        self.assertEqual(ORB.PINS, PINS)
        sources, binding = ORB.load_approved_sources(self.root)
        self.assertEqual(set(sources), {112, 113})
        self.assertEqual(binding['selected_manifest'], ORB.SELECTED)
        self.assertEqual(binding['selected_manifest_sha256'], hashlib.sha256(self.manifest.read_bytes()).hexdigest())
        self.assertFalse(binding['retained_sources_used'])
        for row in binding['sources']:
            self.assertEqual(row['source_png_sha256'], PINS[row['selector']])
            with Image.open(self.root / row['source_png']) as image:
                np.testing.assert_array_equal(sources[row['selector']], np.array(image))

    def test_missing_or_corrupt_sources_never_fall_back_to_retained(self):
        for row in self.records:
            path = self.root / row['source_png']
            original = path.read_bytes()
            for replacement in (None, original + b'corrupt'):
                with self.subTest(selector=row['id'], missing=replacement is None):
                    self.assertEqual(hashlib.sha256((self.root / ART / f"retained-source-{row['id']}.png").read_bytes()).hexdigest(), PINS[row['id']])
                    if replacement is None:
                        path.unlink()
                    else:
                        path.write_bytes(replacement)
                    self.reject_before_output()
                    path.write_bytes(original)

    def test_retained_files_are_not_current_input_dependencies(self):
        expected, _ = ORB.load_approved_sources(self.root)
        for selector in PINS:
            (self.root / ART / f'retained-source-{selector}.png').unlink()
        actual, _ = ORB.load_approved_sources(self.root)
        for selector in PINS:
            np.testing.assert_array_equal(actual[selector], expected[selector])
            self.write(ART / f'retained-source-{selector}.png', b'not a PNG')
        actual, _ = ORB.load_approved_sources(self.root)
        for selector in PINS:
            np.testing.assert_array_equal(actual[selector], expected[selector])

    def test_missing_or_malformed_manifest_rejected(self):
        self.manifest.unlink()
        self.reject_before_output()
        for raw in ('{', '{}', 'null', '[null, null]', '[{"id":112,"id":113},{}]'):
            with self.subTest(raw=raw):
                self.manifest.write_text(raw)
                self.reject_before_output()

    def test_exact_unique_integer_selectors_required(self):
        for records in ([], self.records[:1], self.records + self.records[:1],
                        [self.records[0], self.records[0]]):
            self.save(records)
            self.reject_before_output()
        for bad in (114, 112.0, '112', True, None):
            records = copy.deepcopy(self.records)
            records[0]['id'] = bad
            self.save(records)
            self.reject_before_output()
        self.save(list(reversed(self.records)))
        self.assertEqual(set(ORB.load_approved_sources(self.root)[0]), {112, 113})

    def test_all_geometry_fields_and_integer_types_are_fixed(self):
        for index in range(6):
            records = copy.deepcopy(self.records)
            records[1]['header_u32'][index] += 1
            self.save(records)
            self.reject_before_output()
        for header in (None, [], [80112, 8, 12, 14, 0, 0, 0],
                       [80112, 8.0, 12, 14, 0, 0], [80112, 8, 12, 14, False, 0]):
            records = copy.deepcopy(self.records)
            records[0]['header_u32'] = header
            self.save(records)
            self.reject_before_output()

    def test_changed_source_and_recomputed_manifest_hash_are_not_approval(self):
        row = copy.deepcopy(self.records[0])
        raw = (self.root / row['source_png']).read_bytes() + b'new revision'
        self.write(row['source_png'], raw)
        row['source_png_sha256'] = hashlib.sha256(raw).hexdigest()
        self.save([row, self.records[1]])
        self.reject_before_output()

    def test_source_pin_must_match_the_fixed_approved_revision(self):
        for bad in (None, '', '0' * 64, PINS[113]):
            records = copy.deepcopy(self.records)
            records[0]['source_png_sha256'] = bad
            self.save(records)
            self.reject_before_output()

    def test_unsafe_or_noncanonical_paths_rejected(self):
        for path in ('/tmp/source.png', '../source.png', r'assets\hd\source\frame.png',
                     'C:/source.png', 'assets/hd/source/../frame.png',
                     'assets//hd/source/frame.png', 'assets/hd/source/./frame.png',
                     'assets/hd/source/nested/frame.png', 'assets/hd/source/frame.png:stream',
                     str(ART / 'retained-source-112.png'), None):
            records = copy.deepcopy(self.records)
            records[0]['source_png'] = path
            self.save(records)
            self.reject_before_output()

    def test_link_components_rejected_without_creating_os_links(self):
        original = Path.is_symlink
        for relative in ('assets', ORB.SELECTED, 'assets/hd/source', self.records[0]['source_png']):
            blocked = self.root / relative
            with mock.patch.object(Path, 'is_symlink', lambda path: path == blocked or original(path)):
                self.reject_before_output()

    def test_png_geometry_mode_and_frames_are_checked(self):
        for field, value in (('size', (96, 111)), ('mode', 'RGB'), ('n_frames', 2), ('format', 'JPEG')):
            image = mock.MagicMock(format='PNG', mode='RGBA', size=(96, 112), n_frames=1)
            setattr(image, field, value)
            image.__enter__.return_value = image
            with mock.patch.object(ORB.Image, 'open', return_value=image):
                self.reject_before_output()

    def test_public_mask_derivation_preserves_both_output_contracts(self):
        sources, _ = ORB.load_approved_sources()
        manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_bytes())
        inventory = json.loads((ROOT / ART / 'art-inventory.json').read_bytes())
        for row in self.records:
            selector = row['id']
            source = sources[selector]
            before = source.copy()
            normal = struct.pack('<4s6I', b'HDR1', 80000 + selector, 8, 12, 14, 0, 0) + source.tobytes()
            self.assertEqual(hashlib.sha256(normal).hexdigest(), row['sha256'])
            for pack in manifest['packs']:
                self.assertEqual(normal, (ROOT / 'assets/hd/packs' / pack / f'bullet-{selector}-8.hda').read_bytes())
            mask = public_mask(selector)
            self.assertEqual(int(mask.sum()), 45)
            support = np.repeat(np.repeat(mask, 8, axis=0), 8, axis=1)
            derived = ORB.register_rgba(source, mask)
            np.testing.assert_array_equal(source, before)
            np.testing.assert_array_equal(derived, approved_output(selector))
            np.testing.assert_array_equal(derived[support], source[support])
            self.assertFalse(derived[~support].any())
            self.assertTrue(source[~support].any())  # The two contracts are intentionally different.
            optional = struct.pack('<4s6I', b'HDR1', 1420000 + selector, 8, 12, 14, 0, 0) + derived.tobytes()
            self.assertEqual(optional, (PACK / f'enemy-orb112113-{selector}-8.hda').read_bytes())
            self.assertEqual(hashlib.sha256(optional).hexdigest(), inventory[str(selector)]['hda_sha256'])
            png = io.BytesIO()
            Image.fromarray(derived).save(png, format='PNG')
            self.assertEqual(png.getvalue(), (ROOT / ART / f'enemy-orb112113-{selector}-8.png').read_bytes())

    def test_registration_rejects_wrong_geometry_and_uncovered_mask(self):
        source = ORB.load_approved_sources()[0][112]
        mask = public_mask(112)
        for wrong_source, wrong_mask in ((source[:-1], mask), (source.astype(float), mask),
                                         (source, mask[:-1]), (source, mask.astype(np.uint8)),
                                         (source, np.zeros((14, 12), bool)),
                                         (np.zeros_like(source), mask)):
            with self.assertRaises(ValueError):
                ORB.register_rgba(wrong_source, wrong_mask)

    def run_synthetic_build(self, output):
        # Exercising CLI output only: this stub is explicitly NOT original-bank proof.
        def synthetic_decode(data, selector):
            return b'synthetic public-mask test only', public_mask(selector), None
        with mock.patch.object(ORB, 'ROOT', self.root), mock.patch.object(ORB, 'decode', side_effect=synthetic_decode), contextlib.redirect_stdout(io.StringIO()):
            ORB.main(['--data', str(self.base / 'unused'), '--out', str(output)])

    def test_new_output_binding_and_legacy_inventory_schema(self):
        output = self.base / 'synthetic-build'
        self.run_synthetic_build(output)
        binding = json.loads((output / 'source-binding.json').read_bytes())
        self.assertEqual(binding, ORB.load_approved_sources(self.root)[1])
        current = json.loads((output / 'art-inventory.json').read_bytes())
        historical = json.loads((ROOT / ART / 'art-inventory.json').read_bytes())
        for selector in PINS:
            self.assertEqual(set(current[str(selector)]), set(historical[str(selector)]))
            for key in historical[str(selector)]:
                if key not in ('source_bank_bytes', 'source_bank_fnv64'):
                    self.assertEqual(current[str(selector)][key], historical[str(selector)][key])
            self.assertEqual((output / f'enemy-orb112113-{selector}-8.hda').read_bytes(), (PACK / f'enemy-orb112113-{selector}-8.hda').read_bytes())

    def test_existing_empty_external_output_is_supported(self):
        output = self.base / 'existing-empty'
        output.mkdir()
        self.run_synthetic_build(output)
        self.assertTrue((output / 'source-binding.json').is_file())
        for selector in PINS:
            self.assertEqual((output / f'enemy-orb112113-{selector}-8.hda').read_bytes(), (PACK / f'enemy-orb112113-{selector}-8.hda').read_bytes())

    def test_existing_nonempty_external_output_rebuild_preserves_unrelated_files(self):
        output = self.base / 'existing-nonempty'
        self.run_synthetic_build(output)
        expected = {p.name: p.read_bytes() for p in output.iterdir()}
        (output / 'unrelated-sentinel.txt').write_bytes(b'preserve unrelated file')
        (output / 'enemy-orb112113-112-8.hda').write_bytes(b'old generated output')
        self.run_synthetic_build(output)
        self.assertEqual((output / 'unrelated-sentinel.txt').read_bytes(), b'preserve unrelated file')
        for name, raw in expected.items():
            self.assertEqual((output / name).read_bytes(), raw)

    def test_bad_source_leaves_existing_output_bytes_unchanged(self):
        output = self.base / 'existing-output'
        self.run_synthetic_build(output)
        (output / 'unrelated-sentinel.txt').write_bytes(b'preserve unrelated file')
        expected = {p.name: p.read_bytes() for p in output.iterdir()}
        for row in self.records:
            source = self.root / row['source_png']
            original = source.read_bytes()
            for replacement in (None, original + b'corrupt'):
                if replacement is None:
                    source.unlink()
                else:
                    source.write_bytes(replacement)
                with mock.patch.object(ORB, 'ROOT', self.root), mock.patch.object(ORB, 'decode') as decode:
                    with self.assertRaises(ValueError):
                        ORB.main(['--data', str(self.base / 'unused'), '--out', str(output)])
                    decode.assert_not_called()
                self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, expected)
                source.write_bytes(original)

    def test_repository_outputs_are_not_overwritten(self):
        for output in (self.root, self.root / 'new-output'):
            with mock.patch.object(ORB, 'ROOT', self.root), mock.patch.object(ORB, 'decode') as decode:
                with self.assertRaises(ValueError):
                    ORB.main(['--data', str(self.base / 'unused'), '--out', str(output)])
                decode.assert_not_called()
        self.assertFalse((self.root / 'new-output').exists())


if __name__ == '__main__':
    unittest.main()
