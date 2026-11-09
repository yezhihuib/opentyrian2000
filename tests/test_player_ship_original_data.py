"""Checker safety/error tests; no original game data required."""
from contextlib import redirect_stdout
import io
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('original_ship_checker', Path(__file__).with_name('check_player_ship_original_data.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class OriginalShipCheckerTests(unittest.TestCase):
    def test_missing_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, 'missing original input'):
                checker.load_bank(Path(temporary))

    def test_rejects_wrong_fingerprint_before_rle(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            # Structurally valid header and bank size, deliberately invalid data.
            positions = [54] * 9 + [54 + 33484] * 4
            (path/'tyrian.shp').write_bytes(struct.pack('<H13I', 13, *positions) + bytes(33484))
            with self.assertRaisesRegex(ValueError, 'fingerprint mismatch'):
                checker.load_bank(path)

    def test_rejects_truncated_and_invalid_offsets(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path/'tyrian.shp').write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError, 'offset header'):
                checker.load_bank(path)
            (path/'tyrian.shp').write_bytes(struct.pack('<H13I', 13, *([1000] * 13)))
            with self.assertRaisesRegex(ValueError, 'offset ranges'):
                checker.load_bank(path)

    def test_rejects_checkout_output(self):
        for path in (checker.ROOT, checker.ROOT/'private-original-test-output'):
            with self.assertRaisesRegex(ValueError, 'outside the repository'):
                checker.validate_output(path)

    def test_resolves_symlink_before_checkout_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            link = Path(temporary)/'checkout'
            link.symlink_to(checker.ROOT, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'outside the repository'):
                checker.validate_output(link/'fresh-result')

    def test_requires_fresh_output_with_existing_parent(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            with self.assertRaisesRegex(ValueError, 'fresh'):
                checker.validate_output(path)
            with self.assertRaisesRegex(ValueError, 'parent'):
                checker.validate_output(path/'missing-parent'/'fresh')
            self.assertEqual(checker.validate_output(path/'fresh'), path.resolve()/'fresh')

    def test_missing_data_writes_failure_report_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            out = path/'result'
            with redirect_stdout(io.StringIO()):
                self.assertEqual(checker.main(['--data', str(path/'missing'), '--out', str(out)]), 1)
            report = json.loads((out/'report.json').read_text())
            self.assertEqual(report['status'], 'failed')
            self.assertIn('missing original input', report['error'])
            self.assertTrue(report['limits'])
            self.assertEqual(sorted(p.name for p in out.iterdir()), ['report.json'])
            self.assertEqual(out.stat().st_mode & 0o777, 0o700)


if __name__ == '__main__':
    unittest.main()
