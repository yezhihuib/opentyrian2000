"""Read-only package/launcher checks. No game execution or damaged-file tests."""

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/launch_level2_family.py"
spec = importlib.util.spec_from_file_location("level2_family_launcher", SCRIPT)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)
build_spec = importlib.util.spec_from_file_location("level2_family_builder", ROOT / "scripts/build_level2_family.py")
builder = importlib.util.module_from_spec(build_spec)
build_spec.loader.exec_module(builder)


class Level2FamilyReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="level2-family-check-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.data = self.directory / "user data"
        self.data.mkdir()
        self.profile = self.directory / "profile"
        self.binary = self.directory / "never-run-game"
        # This executable is only selected by dry-run checks, never executed.
        self.binary.write_text("#!/bin/sh\nprintf 'unexpected execution' > game-was-run\nexit 91\n")
        self.binary.chmod(0o700)

    def args(self, *extra):
        return launcher.parser().parse_args([
            "--data", str(self.data), "--binary", str(self.binary),
            "--profile", str(self.profile), *extra,
        ])

    def test_exact_manifest_and_unchanged_asset_hashes(self):
        document = json.loads((ROOT / launcher.MANIFEST).read_text())
        self.assertEqual(document["file_count"], 52)
        self.assertEqual(document["new_file_count"], 11)
        self.assertEqual(document["reused_file_count"], 41)
        self.assertEqual(launcher.verify_assets(), 52)
        for entry in document["files"]:
            with self.subTest(path=entry["path"]):
                path = ROOT / entry["path"]
                self.assertEqual(path.stat().st_size, entry["bytes"])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])

    def test_default_off_clears_inherited_family_and_diagnostic_controls(self):
        inherited = dict.fromkeys(launcher.hd_environment(ROOT), "untrusted-inherited-value")
        inherited.update({
            "B313_FACTS_ENABLE": "1", "BUILDING313_V6_PAYLOAD": "elsewhere",
            "OLD_HD_SAMPLE_OBSERVER_ENABLE": "1", "NATIVE_WRITER_OBSERVER_ENABLE": "1",
            "TYRIAN_CYAN_BORROW_TRACE": "1", "ASSET_DEBUG_OUTPUT": "elsewhere",
            "GAME_PROBE_OUTPUT": "elsewhere", "DISPLAY": ":17", "UNRELATED": "retained",
        })
        cwd = Path.cwd()
        plan, environment = launcher.build_plan(self.args(), inherited)
        self.assertFalse(plan["hd_enabled"])
        self.assertEqual(plan["family_environment_count"], 0)
        self.assertFalse(any(launcher.controlled_name(key) for key in environment))
        self.assertEqual(environment["DISPLAY"], ":17")
        self.assertEqual(environment["UNRELATED"], "retained")
        self.assertEqual(environment["XDG_CONFIG_HOME"], str(self.profile / "config"))
        self.assertFalse(self.profile.exists())
        self.assertEqual(Path.cwd(), cwd)

    def test_hd_sets_exact_23_settings_and_fixed_asset_paths(self):
        poisoned = dict.fromkeys(launcher.hd_environment(ROOT), "wrong")
        plan, environment = launcher.build_plan(self.args("--hd"), poisoned)
        expected = launcher.hd_environment(ROOT)
        self.assertEqual(len(expected), 23)
        self.assertEqual(plan["family_environment_count"], 23)
        self.assertEqual({k: v for k, v in environment.items() if launcher.controlled_name(k)}, expected)
        self.assertEqual(plan["cwd"], str(ROOT))
        self.assertEqual(plan["argv"], [str(self.binary), "--data=" + str(self.data)])
        self.assertFalse(self.profile.exists())

    def test_default_binary_and_separate_repo_profile_selection(self):
        root = self.directory / "repository"
        root.mkdir()
        binary = root / "opentyrian2000-family"
        binary.write_bytes(self.binary.read_bytes())
        binary.chmod(0o700)
        args = launcher.parser().parse_args(["--data", str(self.data)])
        with mock.patch.object(launcher, "verify_assets", return_value=52):
            plan, _ = launcher.build_plan(args, {}, root)
        self.assertEqual(plan["argv"][0], str(binary))
        self.assertEqual(plan["profile"], str(root / ".level2-family-profile"))
        self.assertFalse((root / ".level2-family-profile").exists())

    def test_check_only_from_other_cwd_does_not_execute_or_create_files(self):
        before = set(self.directory.iterdir())
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", BUILDING313_FAMILY_CANVAS_ENABLE="1")
        completed = subprocess.run([
            sys.executable, str(SCRIPT), "--check-only", "--data", "user data",
            "--binary", "never-run-game", "--profile", "profile",
        ], cwd=self.directory, env=env, capture_output=True, text=True, check=True)
        plan = json.loads(completed.stdout)
        self.assertEqual(plan["status"], "CHECK_ONLY")
        self.assertFalse(plan["game_started"])
        self.assertFalse(plan["profile_created"])
        self.assertFalse(plan["hd_enabled"])
        self.assertEqual(plan["argv"][0], str(self.binary))
        self.assertEqual(plan["cwd"], str(ROOT))
        self.assertEqual(set(self.directory.iterdir()), before)
        self.assertEqual(completed.stderr, "")

    def test_dry_run_hd_never_calls_exec(self):
        with mock.patch.object(launcher.os, "execvpe", side_effect=AssertionError("must not launch")), \
             mock.patch("sys.stdout") as output:
            result = launcher.main([
                "--dry-run", "--hd", "--data", str(self.data),
                "--binary", str(self.binary), "--profile", str(self.profile),
            ])
        self.assertEqual(result, 0)
        self.assertTrue(output.write.called)
        self.assertFalse(self.profile.exists())

    def test_damaged_longface_is_manifested_as_unqualified_candidate(self):
        document = json.loads((ROOT / launcher.MANIFEST).read_text())
        longface = [f for f in document["files"] if f["provenance"] == "longface"]
        self.assertEqual(len(longface), 8)
        self.assertEqual(sum(f["runtime_use"] == "normal state" for f in longface), 4)
        self.assertEqual(sum(f["runtime_use"] == "damaged state candidate; first-group full-body/top-entry only; gameplay unverified" for f in longface), 4)

    def test_builder_check_only_snapshots_overlay_without_building(self):
        output = io.StringIO()
        def pkg_config(command, **kwargs):
            self.assertEqual(command[0], "mock-pkg-config")
            self.assertEqual(command[2:], ["sdl2", "SDL2_net", "libcrypto"])
            self.assertTrue(kwargs.get("text"))
            return "-I/example/include" if command[1] == "--cflags" else "-lSDL2 -lSDL2_net -lcrypto"
        with mock.patch.dict(os.environ, {
                "CC": "mock-cc", "PKG_CONFIG": "mock-pkg-config",
                "CPPFLAGS": "", "CFLAGS": "", "LDFLAGS": "",
            }), \
             mock.patch.object(builder.subprocess, "check_output", side_effect=pkg_config) as pkg, \
             mock.patch.object(builder.subprocess, "run", side_effect=AssertionError("must not compile or link")), \
             mock.patch.object(builder.Path, "mkdir", side_effect=AssertionError("must not create a stage")), \
             mock.patch.object(builder.Path, "write_bytes", side_effect=AssertionError("must not stage source")), \
             mock.patch.object(builder.shutil, "copyfile", side_effect=AssertionError("must not publish a binary")), \
             mock.patch("sys.stdout", output):
            result = builder.main(["--check-only"])
        self.assertEqual(result, 0)
        self.assertEqual(pkg.call_count, 2)
        plan = json.loads(output.getvalue())
        self.assertEqual(plan["translation_units"], 112)
        self.assertEqual(plan["compiler"], ["mock-cc"])
        self.assertFalse(plan["production_tree_modified"])
        self.assertFalse(plan["game_started"])
        self.assertEqual(plan["binary"], str(ROOT / "opentyrian2000-family"))
        self.assertIn("-DNEWSHF_HD_COMPOSITOR=0", plan["cppflags"])
        self.assertIn("-DB313_FAMILY_CANVAS_DIAGNOSTIC=1", plan["cppflags"])
        self.assertIn("-lcrypto", plan["libs"])
        self.assertNotIn("harness.c", plan["source_sha256"])
        self.assertNotIn("entry_shim.c", plan["source_sha256"])
        expected_headers = {
            "hd/shared-menu-runs-v1/" + name
            for name in ("reconstructed_run_specs.h", "reconstructed_numeric_specs.h",
                         "reconstructed_name_source_specs.h")
        }
        self.assertEqual(set(plan["asset_header_sha256"]), expected_headers)
        for name, digest in plan["asset_header_sha256"].items():
            self.assertEqual(digest, hashlib.sha256((ROOT / "assets" / name).read_bytes()).hexdigest())
        self.assertIn("-I" + str(Path(plan["stage"]) / "assets"), plan["cppflags"])
        self.assertNotIn("-I" + str(ROOT / "assets"), plan["cppflags"])
        expected_digest = hashlib.sha256(json.dumps({
            "source": plan["source_sha256"], "assets": plan["asset_header_sha256"],
        }, sort_keys=True).encode()).hexdigest()
        self.assertEqual(plan["build_input_digest"], expected_digest)
        for name in ("render_mirror.c", "sprite.c", "tyrian2.c"):
            overlay = ROOT / "experimental/level2-family/src" / name
            self.assertEqual(plan["source_sha256"][name], hashlib.sha256(overlay.read_bytes()).hexdigest())
        # An unused compositor is intentionally retained from the canonical tree.
        canonical = ROOT / "src/global_newshf_mirror.inc"
        self.assertEqual(plan["source_sha256"][canonical.name], hashlib.sha256(canonical.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
