"""Dynamic HUD remains explicit, fully pinned, read-only at plan time."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dynamic_hud_launcher', ROOT/'scripts/launch_level2_family.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

class DynamicHudLauncherTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.binary = self.root/'never-execute'
        self.binary.write_text('')
        self.binary.chmod(0o700)

    def plan(self, flags, inherited=None):
        args = launcher.parser().parse_args(['--data', str(self.root), '--binary', str(self.binary),
            '--profile', str(self.root/'profile')] + flags)
        return launcher.build_plan(args, inherited or {})

    def test_opt_in_requires_both_parent_controls(self):
        key = 'BUILDING313_FAMILY_DYNAMIC_HUD_ENABLE'
        for flags in ([], ['--hd'], ['--hd', '--static-hud'], ['--hd', '--public-candidates']):
            report, env = self.plan(flags, {key:'1'})
            self.assertFalse(report['dynamic_hud_enabled'])
            self.assertNotIn(key, env)
        for flags in (['--dynamic-hud'], ['--hd', '--dynamic-hud']):
            with self.assertRaisesRegex(ValueError, '--dynamic-hud requires'):
                self.plan(flags)
        report, env = self.plan(['--hd', '--static-hud', '--dynamic-hud'])
        self.assertEqual(env[key], '1')
        self.assertEqual(report['dynamic_hud_assets_sha256_verified'], 4)
        self.assertFalse(report['game_started'])
        self.assertFalse((self.root/'profile').exists())
        self.assertNotIn('dynamic_hud', launcher.PUBLIC_CANDIDATE_FLAGS)

    def test_every_dynamic_resource_hash_is_required(self):
        original = Path.read_bytes
        for target in launcher.DYNAMIC_HUD_PINS:
            with self.subTest(resource=target):
                def changed(path):
                    return b'changed' if path.name == target else original(path)
                with mock.patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'Changed dynamic HUD asset'):
                    self.plan(['--hd', '--static-hud', '--dynamic-hud'])

    def test_resource_set_matches_integrated_materials(self):
        self.assertEqual(set(launcher.DYNAMIC_HUD_PINS), {
            'gameplay-hud-components-v1.hda', 'gameplay-hud-meters-v2.hda',
            'gameplay-hud-indicators-v1.hda', 'gameplay-hud-fixed-text-v1.hda'})

if __name__ == '__main__':
    unittest.main()
