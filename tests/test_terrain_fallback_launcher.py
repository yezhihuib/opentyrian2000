"""Plan-only independent terrain opt-in tests. No game is executed."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('terrain_launcher', ROOT/'scripts/launch_level2_family.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

class TerrainLauncherTests(unittest.TestCase):
    def test_opt_in_is_independent_and_default_off(self):
        key = 'BUILDING313_TERRAIN_FALLBACK_ENABLE'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root/'never-execute'
            binary.write_text('')
            binary.chmod(0o700)
            def plan(flags):
                args = launcher.parser().parse_args(['--data',directory,'--binary',str(binary),'--profile',str(root/'profile'),*flags])
                return launcher.build_plan(args,{key:'1'})
            for flags in ([], ['--hd'], ['--hd','--public-candidates'], ['--hd','--static-hud']):
                report, env = plan(flags)
                self.assertFalse(report['terrain_fallback_enabled'])
                self.assertNotIn(key, env)
            with self.assertRaisesRegex(ValueError, 'requires --hd'):
                plan(['--terrain-fallback'])
            report, env = plan(['--hd','--terrain-fallback'])
            self.assertTrue(report['terrain_fallback_enabled'])
            self.assertEqual(env[key], '1')
            self.assertNotIn('BUILDING313_FAMILY_HUD_ENABLE', env)
            self.assertFalse(report['game_started'])
            self.assertFalse((root/'profile').exists())
            with self.assertRaisesRegex(ValueError, 'red-vent'):
                plan(['--hd','--terrain-fallback','--redvent-pair',str(root)])
            self.assertNotIn('terrain_fallback', launcher.PUBLIC_CANDIDATE_FLAGS)

if __name__ == '__main__':
    unittest.main()
