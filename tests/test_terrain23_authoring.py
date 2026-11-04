"""Terrain23 producer checks. No game, compiler, network or original-data fixture.

Set TERRAIN23_TEST_SHAPESZ and TERRAIN23_TEST_PALETTE to the user's matching,
legally obtained files to enable positive reproduction and data-dependent tests.
Without both, those tests are explicitly skipped, not reported as passed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build_current_terrain23.py"
spec = importlib.util.spec_from_file_location("terrain23_authoring", SCRIPT)
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


def invoke(shapesz, palette, output, *, timeout=30):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), "--shapesz", str(shapesz),
         "--palette", str(palette), "--output", str(output)],
        capture_output=True, text=True, env=env, check=False, timeout=timeout,
    )


class Terrain23FailClosedTests(unittest.TestCase):
    def test_missing_inputs_do_not_create_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = invoke(root / "missing-shapesz.dat", root / "missing-palette.dat", root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Cannot read required input", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_wrong_same_length_shapesz_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shape = root / "shapesz.dat"
            shape.write_bytes(bytes(318976))
            result = invoke(shape, root / "palette.dat", root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("SHA256 mismatch", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_wrong_length_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shape = root / "shapesz.dat"
            shape.write_bytes(b"not original data")
            result = invoke(shape, root / "palette.dat", root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Input size mismatch", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_existing_output_is_not_touched(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "existing"
            output.mkdir()
            sentinel = output / "sentinel.txt"
            sentinel.write_bytes(b"preserve me")
            result = invoke(root / "shapesz.dat", root / "palette.dat", output)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Output already exists", result.stderr)
            self.assertEqual(sentinel.read_bytes(), b"preserve me")
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_existing_empty_output_is_also_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "existing"
            output.mkdir()
            with self.assertRaisesRegex(producer.AuthoringError, "already exists"):
                producer.validate_paths(Path("absent-shapes"), Path("absent-palette"), output)
            self.assertEqual(list(output.iterdir()), [])

    def test_output_in_source_tree_is_rejected(self):
        output = producer.SOURCE_ROOT / ".terrain23-authoring-test-must-not-create"
        with self.assertRaisesRegex(producer.AuthoringError, "outside the source"):
            producer.validate_paths(Path("absent-shapes"), Path("absent-palette"), output)
        self.assertFalse(output.exists())

    def test_output_ancestor_of_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "new"
            with self.assertRaisesRegex(producer.AuthoringError, "overlaps"):
                producer.validate_paths(output / "shapesz.dat", Path(td) / "palette.dat", output)
            self.assertFalse(output.exists())

    def test_dangling_output_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output = root / "symlink"
            try:
                output.symlink_to(root / "absent-target", target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable")
            with self.assertRaisesRegex(producer.AuthoringError, "already exists"):
                producer.validate_paths(root / "shapesz.dat", root / "palette.dat", output)
            self.assertTrue(output.is_symlink())
            self.assertFalse((root / "absent-target").exists())

    def test_missing_output_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(producer.AuthoringError, "parent must already exist"):
                producer.validate_paths(root / "shapesz.dat", root / "palette.dat", root / "absent" / "new")
            self.assertFalse((root / "absent").exists())

    def test_truncated_shapes_parser_is_bounded(self):
        with self.assertRaisesRegex(producer.AuthoringError, "Truncated"):
            producer.decode_shapes(b"\0" * 10)

    def test_fifo_input_is_rejected_without_waiting_for_a_writer(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO creation unavailable")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fifo = root / "shapesz.dat"
            os.mkfifo(fifo, 0o600)
            result = invoke(fifo, root / "palette.dat", root / "new", timeout=2)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Regular file required", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_directory_input_is_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = invoke(root, root / "palette.dat", root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Regular file required", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_device_input_is_rejected_before_open(self):
        device = Path("/dev/null")
        if not device.exists() or not stat.S_ISCHR(device.lstat().st_mode):
            self.skipTest("Safe character-device fixture unavailable")
        with mock.patch.object(producer.os, "open", side_effect=AssertionError("Device must not be opened")):
            with self.assertRaisesRegex(producer.AuthoringError, "Regular file required"):
                producer.read_checked(device, "0" * 64, size=318976)

    def test_oversize_raw_is_rejected_before_open(self):
        with tempfile.TemporaryDirectory() as td:
            raw = Path(td) / "raw.png"
            size = producer.RAW_BYTES["ground10"]
            with raw.open("wb") as stream:
                stream.truncate(size + 1)
            with mock.patch.object(producer.os, "open", side_effect=AssertionError("Oversize raw must not be opened")):
                with self.assertRaisesRegex(producer.AuthoringError, "Input size mismatch"):
                    producer.read_checked(raw, "0" * 64, size=size)

    def test_oversize_metadata_is_rejected_before_open(self):
        with tempfile.TemporaryDirectory() as td:
            metadata = Path(td) / "pins.json"
            with metadata.open("wb") as stream:
                stream.truncate(producer.MAX_METADATA_BYTES + 1)
            with mock.patch.object(producer.os, "open", side_effect=AssertionError("Oversize metadata must not be opened")):
                with self.assertRaisesRegex(producer.AuthoringError, "exceeds maximum read size"):
                    producer.read_regular(metadata, max_size=producer.MAX_METADATA_BYTES)

    def test_input_file_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "real.dat"
            target.write_bytes(bytes(318976))
            link = root / "shapesz.dat"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable")
            result = invoke(link, root / "palette.dat", root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Input symlink is not permitted", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_input_parent_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "real-dir"
            target.mkdir()
            (target / "shapesz.dat").write_bytes(bytes(318976))
            link = root / "linked-dir"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation unavailable")
            result = invoke(link / "shapesz.dat", root / "palette.dat", root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Input symlink is not permitted", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_exact_selected_scope_and_frozen_raws(self):
        pins = producer.load_pins()
        self.assertEqual(len(pins), 23)
        self.assertEqual(set(pins), set(producer.IDS))
        self.assertNotIn(319, pins)
        self.assertEqual(sum(x["source_color_lock_pixels"] for x in pins.values()), 36781)
        for family, _, _, _, name, digest in producer.GROUPS:
            data = producer.read_checked(producer.ART_ROOT / family / name, digest, size=producer.RAW_BYTES[family])
            self.assertIn(b"caBX", data)
            self.assertIn(b"c2pa", data)  # Presence only, never a signature verification.


class Terrain23OriginalDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        shape = os.environ.get("TERRAIN23_TEST_SHAPESZ")
        palette = os.environ.get("TERRAIN23_TEST_PALETTE")
        if not shape or not palette:
            raise unittest.SkipTest("Legal original-data paths not supplied; reproduction tests not run")
        cls.shape = Path(shape)
        cls.palette = Path(palette)
        # Reject a bad explicit test fixture rather than skip a requested check.
        producer.read_checked(cls.shape, producer.SHAPES_SHA, size=318976)
        producer.read_checked(cls.palette, producer.PALETTE_SHA, size=18432)

    def test_all_23_hda_exact_headers_hashes_and_scope(self):
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "generated"
            result = invoke(self.shape, self.palette, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            pins = producer.load_pins()
            expected_files = {f"terrain-shapesz-{tile_id}-8.hda" for tile_id in producer.IDS}
            self.assertEqual({p.name for p in output.iterdir()}, expected_files | {"authoring-report.json"})
            for tile_id in producer.IDS:
                data = (output / f"terrain-shapesz-{tile_id}-8.hda").read_bytes()
                self.assertEqual(len(data), 172060)
                self.assertEqual(struct.unpack("<4s6I", data[:28]),
                                 (b"HDR1", 2010000 + tile_id, 8, 24, 28, 0, 0))
                self.assertEqual(hashlib.sha256(data).hexdigest(), pins[tile_id]["hda_sha256"])
                self.assertEqual(set(data[31::4]), {255} if tile_id not in producer.GROUPS[1][1] else {0, 255})
            report = json.loads((output / "authoring-report.json").read_text())
            self.assertEqual(report["status"], "23_BYTE_EXACT_HDA_REPRODUCED")
            self.assertEqual(report["mandatory_original_rgb_lock_hd_pixels"], 36781)
            # A second invocation may not silently replace even identical outputs.
            before = {p.name: p.read_bytes() for p in output.iterdir()}
            retry = invoke(self.shape, self.palette, output)
            self.assertEqual(retry.returncode, 2, retry.stderr)
            self.assertEqual(before, {p.name: p.read_bytes() for p in output.iterdir()})

    def test_missing_palette_after_valid_shapes_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = invoke(self.shape, root / "missing-palette.dat", root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("Cannot read required input", result.stderr)
            self.assertFalse((root / "new").exists())

    def test_same_length_wrong_palette_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            wrong = bytearray(self.palette.read_bytes())
            wrong[0] ^= 1
            bad_palette = root / "palette.dat"
            bad_palette.write_bytes(wrong)
            result = invoke(self.shape, bad_palette, root / "new")
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("SHA256 mismatch", result.stderr)
            self.assertFalse((root / "new").exists())


if __name__ == "__main__":
    unittest.main()
