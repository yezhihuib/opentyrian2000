"""The font feature never changes the independent dynamic HUD preset."""
from pathlib import Path
import unittest
from unittest import mock
from test_family_dynamic_hud_launcher import DynamicHudLauncherTests, launcher


class FontLauncherTests(DynamicHudLauncherTests):
    def test_font_is_separate_and_explicit(self):
        key = 'BUILDING313_FAMILY_FONT_ENABLE'
        for flags in ([], ['--hd'], ['--hd', '--static-hud'],
                      ['--hd', '--static-hud', '--dynamic-hud']):
            report, env = self.plan(flags, {key: '1'})
            self.assertFalse(report['hud_font_enabled'])
            self.assertNotIn(key, env)
        for flags in (['--hud-font'], ['--hd', '--hud-font']):
            with self.assertRaisesRegex(ValueError, '--hud-font requires'):
                self.plan(flags)
        report, env = self.plan(['--hd', '--static-hud', '--hud-font'])
        self.assertEqual(env[key], '1')
        self.assertEqual(report['hud_font_assets_sha256_verified'], 1)
        self.assertFalse(report['dynamic_hud_enabled'])
        self.assertFalse(report['game_started'])
        self.assertFalse((self.root/'profile').exists())
        self.assertNotIn('hud_font', launcher.PUBLIC_CANDIDATE_FLAGS)

    def test_font_hash_is_required(self):
        original = Path.read_bytes
        def changed(path):
            return b'changed' if path.name == 'gameplay-hud-font-v1.hda' else original(path)
        with mock.patch.object(Path, 'read_bytes', changed), self.assertRaisesRegex(ValueError, 'Changed HUD font asset'):
            self.plan(['--hd', '--static-hud', '--hud-font'])


if __name__ == '__main__':
    unittest.main()
