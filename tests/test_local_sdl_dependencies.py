import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/build_local_sdl_dependencies.py'
spec = importlib.util.spec_from_file_location('local_sdl', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class LocalSdlTests(unittest.TestCase):
    def test_plan_does_not_write_or_run(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'new'
            with patch.object(mod.subprocess, 'run', side_effect=AssertionError('must not run')):
                result = mod.plan(output, 2)
            self.assertFalse(output.exists())
            self.assertEqual(result['jobs'], 2)
            self.assertTrue(all(s['url'].startswith('https://github.com/libsdl-org/') for s in result['sources']))
            self.assertTrue(all(len(s['commit']) == 40 for s in result['sources']))

    def test_existing_output_is_never_reused(self):
        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / 'keep'
            marker.write_text('unchanged')
            with self.assertRaises(FileExistsError):
                mod.build(mod.plan(temp, 1))
            self.assertEqual(marker.read_text(), 'unchanged')
            self.assertFalse((Path(temp) / 'BUILD.json').exists())

    def test_tag_mismatch_stops_before_configure(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'new'
            with patch.object(mod.subprocess, 'run') as run, patch.object(mod.subprocess, 'check_output', return_value='bad-sha\n'):
                with self.assertRaisesRegex(ValueError, 'unpinned source'):
                    mod.build(mod.plan(output, 1))
                self.assertEqual(run.call_count, 1)
            self.assertEqual(json.loads((output / 'BUILD.json').read_text())['status'], 'failed')

    def test_success_keeps_every_install_in_local_prefix(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'new'
            def fake_run(argv, **kwargs):
                if argv[:2] == ['git', 'clone']:
                    checkout = Path(argv[-1])
                    checkout.mkdir()
                    for name in ('aclocal.m4', 'configure', 'Makefile.in'):
                        (checkout / name).write_text('pinned bytes')
            with patch.object(mod.subprocess, 'run', side_effect=fake_run) as run, patch.object(mod.subprocess, 'check_output', side_effect=[x[3] for x in mod.SOURCES]):
                result = mod.build(mod.plan(output, 2))
            self.assertEqual(result['status'], 'built')
            commands = [call.args[0] for call in run.call_args_list]
            self.assertEqual(len(commands), 8)
            self.assertTrue(all('--prefix=' + str(output / 'prefix') in commands[i] for i in (1, 5)))
            self.assertEqual(commands[2], ['make', '-j2'])
            self.assertEqual(commands[3], ['make', 'install'])
            self.assertEqual((output / 'SDL_net/configure').read_text(), 'pinned bytes')

    def test_default_cli_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'new'
            result = subprocess.run(['python3', str(SCRIPT), '--output', str(output)], capture_output=True, text=True, check=True)
            self.assertFalse(output.exists())
            self.assertFalse(json.loads(result.stdout)['game_executed'])

    def test_rejects_repo_output(self):
        result = subprocess.run(['python3', str(SCRIPT), '--output', str(SCRIPT.parent / 'deps')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('outside the repository', result.stderr)


if __name__ == '__main__':
    unittest.main()
