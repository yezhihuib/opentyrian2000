"""Plan-only normal-player fallback opt-in tests. No game is executed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('player_fallback_launcher', ROOT/'scripts/launch_level2_family.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class PlayerFallbackLauncherTests(unittest.TestCase):
    def test_explicit_dependencies_and_default_off(self):
        key = 'BUILDING313_PLAYER_FALLBACK_ENABLE'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root/'never-execute'
            binary.write_text('')
            binary.chmod(0o700)

            def plan(flags):
                args = launcher.parser().parse_args(['--data', directory, '--binary', str(binary),
                    '--profile', str(root/'profile'), *flags])
                return launcher.build_plan(args, {key: '1'})

            for flags in ([], ['--hd'], ['--hd', '--public-candidates'],
                          ['--hd', '--terrain-fallback'],
                          ['--hd', '--public-candidates', '--terrain-fallback', '--static-hud']):
                report, env = plan(flags)
                self.assertFalse(report['player_fallback_enabled'])
                self.assertNotIn(key, env)
            for flags in (['--player-fallback'], ['--hd', '--player-fallback'],
                          ['--hd', '--public-candidates', '--player-fallback'],
                          ['--hd', '--terrain-fallback', '--player-fallback']):
                with self.assertRaisesRegex(ValueError, 'requires --hd --public-candidates --terrain-fallback'):
                    plan(flags)
            report, env = plan(['--hd', '--public-candidates', '--terrain-fallback', '--player-fallback'])
            self.assertTrue(report['player_fallback_enabled'])
            self.assertEqual(env[key], '1')
            self.assertEqual(env['PLAYER_SHIP_FAMILY_ENABLE'], '1')
            self.assertEqual(env['BUILDING313_TERRAIN_FALLBACK_ENABLE'], '1')
            self.assertNotIn('PLAYER_SHIP_FAMILY_INVULNERABLE_ENABLE', env)
            self.assertNotIn('BUILDING313_FAMILY_HUD_ENABLE', env)
            self.assertFalse(report['game_started'])
            self.assertFalse((root/'profile').exists())
            self.assertNotIn('player_fallback', launcher.PUBLIC_CANDIDATE_FLAGS)


if __name__ == '__main__':
    unittest.main()
