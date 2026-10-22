"""Historical anchors fail closed; immutable metadata works without Git or network."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from historical_global_fixtures import (
    FIXTURES, REGISTRY_ANCHORS, RECEIPT_ANCHORS, PULSE_BASELINE,
    registry_at, verify_original_bytes, verify_historical_receipt,
)


class HistoricalGlobalFixturesTests(unittest.TestCase):
    def test_all_original_blobs_work_without_git(self):
        with patch('subprocess.check_output', side_effect=AssertionError('Git must not be needed')):
            for commit in REGISTRY_ANCHORS:
                value = registry_at(commit)
                self.assertIsInstance(value['resources'], list)
                self.assertIsInstance(value['families'], list)

    def test_fixture_corruption_and_valid_json_rewrite_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for commit in REGISTRY_ANCHORS:
                original = (FIXTURES / (commit + '.json')).read_bytes()
                destination = Path(tmp) / (commit + '.json')
                for damaged in (original[:-1], original + b' ', json.dumps({'resources': []}).encode()):
                    destination.write_bytes(damaged)
                    with self.subTest(commit=commit, size=len(damaged)):
                        with self.assertRaises(ValueError):
                            registry_at(commit, tmp)

    def test_missing_and_unknown_fixture_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                registry_at(PULSE_BASELINE, tmp)
            with self.assertRaises(KeyError):
                registry_at('0' * 40, tmp)

    def test_each_independent_anchor_field_enforced(self):
        data = (FIXTURES / (PULSE_BASELINE + '.json')).read_bytes()
        for field in ('git_blob', 'sha256', 'bytes'):
            altered = dict(REGISTRY_ANCHORS[PULSE_BASELINE])
            altered[field] = 0 if field == 'bytes' else '0' * len(altered[field])
            with self.assertRaises(ValueError):
                verify_original_bytes(data, altered)

    def test_original_receipts_and_tamper_detection(self):
        root = Path(__file__).resolve().parents[1]
        for name in RECEIPT_ANCHORS:
            original = (root / name).read_bytes()
            verify_historical_receipt(PULSE_BASELINE, name, original)
            with self.assertRaises(ValueError):
                verify_historical_receipt(PULSE_BASELINE, name, original + b' ')
            with self.assertRaises(ValueError):
                verify_historical_receipt('0' * 40, name, original)


if __name__ == '__main__':
    unittest.main()
