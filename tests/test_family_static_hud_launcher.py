"""Read-only static-border opt-in, immutable resource and isolation checks."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('static_hud_launcher',ROOT/'scripts/launch_level2_family.py')
launcher=importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

class StaticHudLauncherTests(unittest.TestCase):
    def test_explicit_opt_in_only_and_profile_is_not_created(self):
        key='BUILDING313_FAMILY_HUD_ENABLE'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);binary=root/'never-execute';binary.write_text('');binary.chmod(0o700)
            def plan(flags):
                args=launcher.parser().parse_args(['--data',directory,'--binary',str(binary),'--profile',str(root/'profile')]+flags)
                return launcher.build_plan(args,{key:'1'})
            for flags in ([],['--hd'],['--hd','--public-candidates']):
                report,env=plan(flags)
                self.assertNotIn(key,env)
                self.assertFalse(report['static_hud_enabled'])
            with self.assertRaises(ValueError):plan(['--static-hud'])
            report,env=plan(['--hd','--static-hud'])
            self.assertEqual(env[key],'1')
            self.assertEqual(report['static_hud_assets_sha256_verified'],1)
            self.assertFalse(report['game_started'])
            self.assertFalse((root/'profile').exists())
            self.assertNotIn('static_hud',launcher.PUBLIC_CANDIDATE_FLAGS)

    def test_asset_hash_remains_mandatory(self):
        with tempfile.TemporaryDirectory() as directory:
            binary=Path(directory)/'never-execute';binary.write_text('');binary.chmod(0o700)
            args=launcher.parser().parse_args(['--data',directory,'--binary',str(binary),'--hd','--static-hud'])
            original=Path.read_bytes
            def changed(path):
                return b'changed' if path.name=='gameplay-hud-v1.hda' else original(path)
            with mock.patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(ValueError,'Changed static HUD asset'):
                launcher.build_plan(args,{})

if __name__=='__main__':unittest.main()
