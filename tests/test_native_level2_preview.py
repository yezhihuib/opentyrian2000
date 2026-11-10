"""Focused native preview option and source contract tests. No game data required."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NativePreviewContract(unittest.TestCase):
    def test_bootstrap_is_opt_in_and_has_no_playback(self):
        text = (ROOT/'src/opentyr.c').read_text()
        self.assertLess(text.index('level2_preview_parse(&argc, argv);'), text.index('game_probe_parse(&argc, argv);'))
        block = text.split('/* Normal native initialization and loader, not game_probe_start(). */', 1)[1].split('#ifdef NDEBUG', 1)[0]
        for required in ('JE_initEpisode(1);', 'JE_initPlayerData();', 'mainLevel = 6;', 'inputDevice[0] = 1;', 'play_demo = false;', 'JE_main();', 'JE_tyrianHalt(0);'):
            self.assertIn(required, block)
        for forbidden in ('mt_srand(', 'keysactive[', 'invulnerable_ticks', 'game_probe_start();', 'SDL_PushEvent', 'tick_limit'):
            self.assertNotIn(forbidden, block)

    def test_both_level_loops_stop_at_native_boundary(self):
        for name in ('src/tyrian2.c', 'experimental/level2-family/src/tyrian2.c'):
            text = (ROOT/name).read_text()
            cleanup = text.index('free_sprite2s(&enemySpriteSheets[3]);', text.index('start_level:'))
            boundary = text.index('if (level2_preview_requested)', cleanup)
            next_flow = text.index('difficultyLevel = oldDifficultyLevel;', cleanup)
            self.assertLess(cleanup, boundary)
            self.assertLess(boundary, next_flow)
            self.assertIn('return;', text[boundary:next_flow])
            self.assertIn('(episodeNum != 1 || lvlFileNum != 2 || mainLevel != 6 ||', text)

    def test_frozen_preview_remains_historical(self):
        text = (ROOT/'scripts/preview_level2_frozen.py').read_text()
        self.assertIn("SOURCE_COMMIT = '562e8fc4ad0f7916734bc40624b867a152d89b0c'", text)
        self.assertIn("'--render-ticks=600'", text)
        self.assertNotIn('--level2-preview=', text)


class NativePreviewCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = Path(os.environ.get('NATIVE_PREVIEW_BINARY', ROOT/'opentyrian2000-family')).resolve()
        if not cls.binary.is_file():
            raise unittest.SkipTest('Build the native preview binary first, or set NATIVE_PREVIEW_BINARY.')
        result = subprocess.run([str(cls.binary), '--help'], capture_output=True, text=True)
        if result.returncode or '--level2-preview=asteroid2-v1' not in result.stdout:
            raise unittest.SkipTest('Available binary predates native preview, or its runtime dependencies are unavailable.')

    def run_cli(self, *args):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, HOME=directory, XDG_CONFIG_HOME=directory+'/config')
            result = subprocess.run([str(self.binary), *args], cwd=directory, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(list(Path(directory).iterdir()), [], 'CLI checks must not touch profiles or game data.')
            return result

    def test_help_preserves_default_and_supports_exact_mode(self):
        for args in (('--help',), ('--level2-preview=asteroid2-v1', '--help')):
            self.assertEqual(self.run_cli(*args).returncode, 0)

    def test_invalid_or_duplicate_contract(self):
        for args in (('--level2-preview',), ('--level2-preview=wrong',),
                     ('--level2-preview=asteroid2-v1', '--level2-preview=asteroid2-v1')):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn('exactly one', result.stderr)

    def test_raw_diagnostic_options_are_rejected_in_either_order(self):
        for option in ('--render-test=8', '--render-ticks=600', '--asset-debug=custom',
                       '--enemy-reuse-observe-assets=/unused', '--manual-hd-assets=/unused',
                       '--asteroid-hd-assets=/unused'):
            for args in ((option, '--level2-preview=asteroid2-v1'), ('--level2-preview=asteroid2-v1', option)):
                with self.subTest(args=args):
                    result = self.run_cli(*args)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('cannot be combined', result.stderr)

    def test_native_conflicts_are_rejected_before_data_or_profile_access(self):
        for option in ('--net=localhost', '--record', '--constant', '--death', '--loot', '--xmas',
                       'RECORD', 'CONSTANT', 'DEATH', 'LOOT', 'YESXMAS'):
            with self.subTest(option=option):
                result = self.run_cli('--level2-preview=asteroid2-v1', option)
                self.assertEqual(result.returncode, 2)
                self.assertIn('local normal play only', result.stderr)


if __name__ == '__main__':
    unittest.main()
