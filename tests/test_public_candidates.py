"""Public combination planner only. Never execute a game."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('combo_launcher',ROOT/'scripts/launch_level2_family.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)
class PublicCandidateTests(unittest.TestCase):
    def setup_args(self,temp,flags):
        b=Path(temp)/'never-run';b.write_text('');b.chmod(0o700)
        return launcher.parser().parse_args(['--data',temp,'--binary',str(b)]+flags)
    def test_explicit_hd_default_and_private_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            for flags in ([],['--hd']):
                args=self.setup_args(temp,flags);plan,env=launcher.build_plan(args,{'NORMAL270_ENABLE':'1'})
                self.assertFalse(plan['public_candidates_enabled']);self.assertFalse(plan['normal270_enabled']);self.assertNotIn('NORMAL270_ENABLE',env)
            for flags in (['--public-candidates'],['--hd','--public-candidates','--redvent-pair',temp]):
                with self.assertRaises(ValueError):launcher.build_plan(self.setup_args(temp,flags),{})
    def test_combo_all_flags_idempotent_and_no_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            args=self.setup_args(temp,['--hd','--public-candidates']);original=vars(args).copy()
            plan,env=launcher.build_plan(args,{'LATE_ACTORS_ASSET_DIR':'bad','GAME_PROBE_ENABLE':'1','NORMAL270_ASSET_DIR':'bad','UNRELATED':'kept'})
            self.assertEqual(vars(args),original);self.assertEqual(plan['status'],'CHECK_ONLY');self.assertFalse(plan['game_started']);self.assertFalse(plan['profile_created'])
            self.assertEqual(env['UNRELATED'],'kept');self.assertNotIn('GAME_PROBE_ENABLE',env)
            self.assertEqual(plan['normal270_assets_sha256_verified'],3);self.assertEqual(len(plan['public_candidate_flags']),9)
            for flag in launcher.PUBLIC_CANDIDATE_FLAGS:
                key={'linked_props':'linked_props','later_triples':'later_triples','later_embers':'later_embers','later_lamps':'later_lamps'}.get(flag,flag)+'_enabled'
                self.assertTrue(plan[key])
            self.assertFalse(plan['redvent_pair_enabled']);self.assertNotIn('BUILDING313_REDVENT_PAIR_ENABLE',env)
            flags=['--hd','--public-candidates']+['--'+x.replace('_','-') for x in launcher.PUBLIC_CANDIDATE_FLAGS if x!='normal270']
            plan2,env2=launcher.build_plan(self.setup_args(temp,flags),{})
            self.assertEqual(plan2['environment_overrides'],plan['environment_overrides'])
    def test_lamp_edges_explicit_independent_and_not_in_preset(self):
        controls = ('LAMP272_TOP_CLIP_ENABLE', 'LAMP272_BOTTOM_CLIP_ENABLE')
        with tempfile.TemporaryDirectory() as temp:
            for top, bottom in ((False, False), (True, False), (False, True), (True, True)):
                flags = ['--hd'] + (['--lamp-top-clip'] if top else []) + (['--lamp-bottom-clip'] if bottom else [])
                args = self.setup_args(temp, flags)
                plan, env = launcher.build_plan(args, dict.fromkeys(controls, '1'))
                for key, enabled in zip(controls, (top, bottom)):
                    self.assertEqual(env.get(key), '1' if enabled else None)
                self.assertEqual(plan['lamp_top_clip_enabled'], top)
                self.assertEqual(plan['lamp_bottom_clip_enabled'], bottom)
                self.assertFalse(plan['game_started'])
            for option in ('--lamp-top-clip', '--lamp-bottom-clip'):
                with self.assertRaisesRegex(ValueError, 'requires explicit --hd'):
                    launcher.build_plan(self.setup_args(temp, [option]), {})
            plan, env = launcher.build_plan(self.setup_args(temp, ['--hd', '--public-candidates']), dict.fromkeys(controls, '1'))
            for key in controls:
                self.assertNotIn(key, env)

    def test_bad_normal270_asset_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            args=self.setup_args(temp,['--hd','--public-candidates'])
            real=Path.read_bytes
            def corrupt(path):
                raw=real(path)
                return raw[:-1]+bytes([raw[-1]^1]) if path.name=='enemy-newshd-129-8.hda' else raw
            with patch.object(Path,'read_bytes',corrupt),self.assertRaisesRegex(ValueError,'Changed normal270'):
                launcher.build_plan(args,{})
if __name__=='__main__':unittest.main()
