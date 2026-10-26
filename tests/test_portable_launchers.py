"""Command/metadata checks only: no game launch or Windows execution claims."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
PROTOTYPE = REPO / 'prototype'
sys.path.insert(0, str(PROTOTYPE))
spec = importlib.util.spec_from_file_location('portable_debug', PROTOTYPE / 'start-asset-debug.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class PortableLaunchers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='launcher test 空间 ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.exe = self.root / 'game 空格.exe'
        self.exe.write_bytes(b'not an executable')
        self.data = self.root / 'original 数据'
        self.data.mkdir()
        (self.data / 'tyrian1.lvl').write_bytes(b'fixture')
        self.assets = self.root / 'pack 素材'
        self.assets.mkdir()
        self.index = self.root / 'index.json'
        self.index.write_text(json.dumps({'replay': {'episode': 1, 'physical_level': 9}, 'segments': [{'number': 0, 'start_tick': 232}], 'materials': {}}))
        self.paths = ['--exe', str(self.exe), '--assets', str(self.assets), '--data', str(self.data)]

    def run_script(self, name, args):
        with patch.object(sys, 'argv', [name] + args), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return runpy.run_path(str(PROTOTYPE / name), run_name='__main__')

    def test_play_routes_python_and_preserves_argv(self):
        with patch('subprocess.call', return_value=0) as call:
            with self.assertRaises(SystemExit) as result:
                self.run_script('asset-index.py', ['play', '--index', str(self.index), '--segment', '0'] + self.paths + ['--capture', '--capture-start', '232', '--capture-count', '4', '--window-only', '--headless', '--running', '--talon5', '--explosion-log'])
            self.assertEqual(result.exception.code, 0)
            cmd = call.call_args.args[0]
            self.assertEqual(cmd[0], sys.executable)
            self.assertTrue(cmd[1].endswith('start-asset-debug.py'))
            parsed = launcher.parser().parse_args(cmd[2:])
            launcher.validate(launcher.parser(), parsed)
            self.assertEqual((parsed.exe, parsed.assets, parsed.data), (str(self.exe), str(self.assets), str(self.data)))
            self.assertEqual((parsed.tick, parsed.capture_count, parsed.talon_bank), (232, 4, '5'))
            self.assertTrue(parsed.window_only and parsed.headless and parsed.running and parsed.explosion_log)

    def test_no_launch_never_builds_or_starts_process(self):
        with patch('subprocess.call') as call, patch('subprocess.run') as run:
            self.run_script('asset-index.py', ['play', '--index', str(self.index), '--segment', '0', '--no-launch'])
        call.assert_not_called()
        run.assert_not_called()

    def test_missing_path_values_rejected_all_entrypoints(self):
        for script, prefix in [('asset-index.py', ['play']), ('run-controlled.py', []), ('start-asset-debug.py', ['--tick', '232'])]:
            for flag in ['--exe', '--assets', '--data']:
                with self.subTest(script=script, flag=flag), self.assertRaises(SystemExit) as result:
                    self.run_script(script, prefix + [flag])
                self.assertEqual(result.exception.code, 2)

    def test_explicit_invalid_data_fails_before_launch(self):
        for value in [self.root / 'missing', self.exe, self.assets]:
            with self.subTest(value=value), patch('subprocess.run') as run, self.assertRaises(SystemExit) as result:
                launcher.main(['--tick', '232', '--exe', str(self.exe), '--data', str(value), '--assets', str(self.assets)])
            self.assertEqual(result.exception.code, 2)
            run.assert_not_called()

    def test_invalid_capture_and_tick_ranges(self):
        cases = [['--tick', '-1'], ['--tick', '60', '--until', '60'], ['--tick', '1', '--until', '6001'], ['--tick', '1', '--episode', '6'], ['--tick', '1', '--level', '0'], ['--tick', '1', '--capture-count', '0'], ['--tick', '1', '--window-only'], ['--tick', '1', '--capture-start', '6000', '--capture']]
        for args in cases:
            with self.subTest(args=args), patch('subprocess.run') as run, self.assertRaises(SystemExit) as result:
                launcher.main(args)
            self.assertEqual(result.exception.code, 2)
            run.assert_not_called()

    def test_command_flags(self):
        a = launcher.parser().parse_args(['--tick', '232', '--capture', '--capture-start', '232', '--capture-count', '4', '--window-only', '--running', '--explosion-log'])
        cmd = launcher.command(a, self.exe, self.data, self.assets, self.root / 'control file')
        for arg in ['--data=' + str(self.data), '--render-assets=' + str(self.assets), '--asset-debug=custom', '--asset-debug-tick=232', '--asset-debug-capture-count=4', '--asset-debug-window-only', '--asset-debug-running', '--asset-debug-explosion-log', '--render-talon-bank=13']:
            self.assertIn(arg, cmd)
        self.assertEqual(cmd[0], str(self.exe))

    def test_reload_metadata_and_isolated_process(self):
        fake_repo = self.root / 'repo'
        for name in ['asset_debug.c', 'tyrian2.c', 'game_probe.c', 'render_mirror.c']:
            path = fake_repo / 'src' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture')
        with patch.object(launcher, 'REPO', fake_repo), patch.object(launcher.subprocess, 'run', side_effect=[subprocess.CompletedProcess([], 75), subprocess.CompletedProcess([], 0)]) as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(launcher.main(['--tick', '232', '--headless'] + self.paths), 0)
        self.assertEqual(run.call_count, 2)
        dirs = [call.kwargs['cwd'] for call in run.call_args_list]
        self.assertNotEqual(*dirs)
        for out, code in zip(dirs, [75, 0]):
            metadata = json.loads((out / 'asset-debug-run.json').read_text())
            self.assertEqual(metadata['exit_code'], code)
            self.assertEqual(metadata['exe_sha256'], launcher.sha(self.exe))
            self.assertEqual(metadata['argv'][1], '--data=' + str(self.data))
            self.assertTrue((out / 'debug-control.txt').is_file())
            self.assertTrue((out / 'opentyrian.cfg').is_file())
        self.assertEqual(run.call_args.kwargs['env']['SDL_VIDEODRIVER'], 'dummy')
        self.assertNotIn('shell', run.call_args.kwargs)
        for call in run.call_args_list:
            out = call.kwargs['cwd']
            env = call.kwargs['env']
            self.assertEqual(env['HOME'], str(out / 'home'))
            self.assertEqual(env['XDG_CONFIG_HOME'], str(out / 'config'))
            self.assertEqual((out / 'config/opentyrian2000/opentyrian.cfg').read_bytes(), (out / 'opentyrian.cfg').read_bytes())

    def test_replay_limit_is_bounded(self):
        (self.root / 'run').mkdir()
        with patch.object(launcher.tempfile, 'mkdtemp', return_value=str(self.root / 'run')), patch.object(launcher.subprocess, 'run', return_value=subprocess.CompletedProcess([], 75)) as run, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(launcher.main(['--tick', '232', '--max-replays', '0'] + self.paths), 75)
        self.assertEqual(run.call_count, 1)
        self.assertIn('Replay limit exhausted', stderr.getvalue())

    def test_missing_executable_and_file_as_assets_rejected(self):
        for flag, value in [('--exe', self.assets), ('--exe', self.root / 'absent'), ('--assets', self.exe)]:
            with self.subTest(flag=flag, value=value), patch('subprocess.run') as run, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
                launcher.main(['--tick', '232'] + self.paths + [flag, str(value)])
            self.assertEqual(result.exception.code, 2)
            run.assert_not_called()

    def test_nonzero_exit_propagates(self):
        (self.root / 'run').mkdir()
        with patch.object(launcher, 'REPO', REPO), patch.object(launcher.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2)):
            # Avoid creating files beside the real repository.
            with patch.object(launcher.tempfile, 'mkdtemp', return_value=str(self.root / 'run')), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(launcher.main(['--tick', '232'] + self.paths), 2)

    def test_run_controlled_forwards_explicit_data(self):
        def stopped(cmd, **kwargs):
            self.assertEqual(cmd[0], str(self.exe))
            self.assertIn('--data=' + str(self.data), cmd)
            self.assertIn('--render-assets=' + str(self.assets), cmd)
            raise RuntimeError('mock stop before game')
        # Redirect output-directory operations without touching the real controlled-runs.
        with patch('subprocess.run', side_effect=stopped), patch.object(Path, 'mkdir'), patch.object(Path, 'open', return_value=io.StringIO()), self.assertRaisesRegex(RuntimeError, 'mock stop'):
            self.run_script('run-controlled.py', self.paths + ['--modes', 'classic'])

    def test_original_data_default_retained(self):
        for script in ['start-asset-debug.py', 'run-controlled.py', 'asset-index.py']:
            self.assertIn("runtime-data/tyrian2000", (PROTOTYPE / script).read_text())


if __name__ == '__main__':
    unittest.main()
