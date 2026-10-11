"""Run isolated fixture-preparation regression tests with the standard library."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest


PREPARE = Path(__file__).with_name('prepare-effects.py')
BASE = b'int x = 1;\nint y = 2;\n'
OVERRIDE = b'/* exact archived override */\r\n'


class PrepareEffectsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='prepare-effects-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.script = self.repo / 'prototype/fixtures/prepare-effects.py'
        self.script.parent.mkdir(parents=True)
        shutil.copy2(PREPARE, self.script)
        (self.repo / 'src').mkdir()
        (self.repo / 'visualc').mkdir()
        (self.repo / 'Makefile').write_bytes(b'# test build file\n')
        (self.repo / 'prototype/build-game.ps1').write_bytes(b'# test build file\n')
        self.fixture = self.script.parent / 'effects/green-trail'
        (self.fixture / 'overrides/src').mkdir(parents=True)
        self.configure()

    def configure(self, production=BASE, expected=None, override=OVERRIDE):
        if expected is None:
            expected = BASE.replace(b'\n', b'\r\n')
        (self.repo / 'src/base.c').write_bytes(production)
        (self.fixture / 'overrides/src/override.c').write_bytes(override)
        manifest = {
            'same_other_production_src_sha256': {
                'src/base.c': hashlib.sha256(expected).hexdigest(),
            },
            'tested_exact_source_overrides': {
                'src/override.c': hashlib.sha256(OVERRIDE).hexdigest(),
            },
            'test_resource_pack': 'test-pack',
        }
        (self.fixture / 'manifest.json').write_text(json.dumps(manifest))

    def prepare(self, output=None):
        if output is None:
            output = self.root / 'output'
        return subprocess.run(
            [sys.executable, str(self.script), '--family', 'green-trail',
             '--output', str(output)],
            capture_output=True, text=True,
        )

    def assert_prepares_unchanged(self, production, expected):
        self.configure(production=production, expected=expected)
        output = self.root / hashlib.sha256(production + expected).hexdigest()
        result = self.prepare(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((output / 'src/base.c').read_bytes(), production)
        self.assertEqual((output / 'src/override.c').read_bytes(), OVERRIDE)

    def test_raw_lf_hash(self):
        self.assert_prepares_unchanged(BASE, BASE)

    def test_raw_crlf_hash(self):
        crlf = BASE.replace(b'\n', b'\r\n')
        self.assert_prepares_unchanged(crlf, crlf)

    def test_lf_checkout_against_windows_manifest(self):
        self.assert_prepares_unchanged(BASE, BASE.replace(b'\n', b'\r\n'))

    def test_mixed_line_endings_against_windows_manifest(self):
        mixed = BASE.replace(b'\n', b'\r\n', 1)
        self.assert_prepares_unchanged(mixed, BASE.replace(b'\n', b'\r\n'))

    def test_content_changes_are_rejected_before_creating_output(self):
        changes = {
            'value': BASE.replace(b'1', b'3'),
            'whitespace': BASE.replace(b'int x', b'int  x'),
            'trailing_space': BASE.replace(b';\n', b'; \n'),
            'missing_final_newline': BASE.rstrip(b'\n'),
            'bom': b'\xef\xbb\xbf' + BASE,
            'bare_cr': BASE.replace(b'\n', b'\r'),
            'extra_cr': BASE.replace(b'\n', b'\r\r\n'),
        }
        for label, production in changes.items():
            with self.subTest(change=label):
                self.configure(production=production)
                output = self.root / label
                result = self.prepare(output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Production base changed', result.stderr)
                self.assertFalse(output.exists())

    def test_override_hashes_stay_byte_exact(self):
        for label, override in {
            'line_endings': OVERRIDE.replace(b'\r\n', b'\n'),
            'content': OVERRIDE.replace(b'exact', b'changed'),
        }.items():
            with self.subTest(change=label):
                self.configure(override=override)
                result = self.prepare(self.root / label)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('AssertionError', result.stderr)

    def test_existing_output_is_rejected(self):
        output = self.root / 'existing'
        output.mkdir()
        result = self.prepare(output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Choose a new fixture output directory', result.stderr)

    def test_output_inside_checkout_is_rejected(self):
        output = self.repo / 'fixture-output'
        result = self.prepare(output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Keep fixture output outside', result.stderr)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
