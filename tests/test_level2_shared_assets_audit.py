"""The inventory must never confuse existing art with family integration."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_level2_shared_assets as inventory


class SharedInventoryTests(unittest.TestCase):
    def test_report_is_not_completion(self):
        report = inventory.audit()
        self.assertFalse(report["complete"])
        self.assertTrue(report["classification_current"])
        entries = report["entries"]
        self.assertEqual(5, sum(e["family_integration"] == "guarded-five-pose-adapter" for e in entries))
        self.assertEqual(2, sum(e["family_integration"] == "guarded-tank194-weapons2-and3" for e in entries))
        self.assertTrue(any(e["category"] == "effects" and e["family_integration"] == "not-wired" for e in entries))
        self.assertFalse(any(e["resource"] != "hash-verified" for e in entries if e["category"] != "hud"))

    def test_resource_states_are_distinct(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "asset.hda"
            self.assertEqual("missing", inventory.inspect_file(path))
            path.write_bytes(b"version https://git-lfs.github.com/spec/v1\n")
            self.assertEqual("lfs-pointer", inventory.inspect_file(path))
            path.write_bytes(b"wrong")
            self.assertEqual("hash-mismatch", inventory.inspect_file(path, "0" * 64))
            self.assertEqual("present-unverified", inventory.inspect_file(path))


if __name__ == "__main__":
    unittest.main()
