"""The discovery adapter must execute oracles, not turn them into zero tests."""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import cli_test_support as support

class CliSupportTests(unittest.TestCase):
    def test_registry_each_module_exposes_exact_counted_cases_without_execution(self):
        paired = {
            'test_pregame_coexistence.py',
            'test_pregame_font_integration.py',
            'test_settings_integration.py',
        }
        for name in support.REGISTRY:
            spec = importlib.util.spec_from_file_location('probe_'+name[:-3], Path(__file__).with_name(name))
            module = importlib.util.module_from_spec(spec)
            with patch.object(subprocess, 'run', side_effect=AssertionError('import executed subprocess')):
                spec.loader.exec_module(module)
                suite = module.load_tests(None, None, None)
            expected_ids = [name[:-3]+'.CliOracle.test_cli_oracle']
            if name in paired:
                expected_ids.append(name[:-3]+'.CurrentProductionOracle.test_exact_published_production')
            self.assertEqual(suite.countTestCases(), len(expected_ids), name)
            self.assertEqual([case.id() for case in suite], expected_ids, name)

    def test_missing_or_incomplete_authentic_inputs_fail_not_skip(self):
        with self.assertRaisesRegex(RuntimeError, 'TYRIAN_TEST_DATA'):
            support.original_data_directory({})
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, 'tyrian.hdt'):
                support.original_data_directory({'TYRIAN_TEST_DATA': tmp})
            (Path(tmp)/'tyrian.hdt').write_bytes(b'x')
            with self.assertRaisesRegex(RuntimeError, 'tyrian.shp'):
                support.original_data_directory({'TYRIAN_TEST_DATA': tmp})

    def test_unknown_script_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unregistered'):
            support.cli_suite('unknown.py')

    def test_oracle_failure_or_empty_success_never_passes(self):
        oracle = support.CliOracle(Path(__file__).with_name('test_rear_multi_p10_mode1_inputs.py'))
        with patch.object(support, 'original_data_directory', return_value=Path('/unused')):
            for result in (subprocess.CompletedProcess([], 9, 'authentic-input PASS:', 'failure'),
                           subprocess.CompletedProcess([], 0, '', '')):
                with patch.object(subprocess, 'run', return_value=result):
                    with self.assertRaises(AssertionError):
                        oracle.runTest()

    def test_receipt_success_requires_real_receipt(self):
        oracle = support.CliOracle(Path(__file__).with_name('test_settings_integration.py'))
        with patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'PASS', '')):
            with self.assertRaisesRegex(AssertionError, 'receipt'):
                oracle.runTest()

    def test_empty_pass_receipt_is_not_evidence(self):
        oracle = support.CliOracle(Path(__file__).with_name('test_settings_integration.py'))
        def forged(command, **kwargs):
            Path(command[command.index('--out')+1]).write_text(json.dumps({'result':'PASS'}))
            return subprocess.CompletedProcess(command, 0, 'PASS', '')
        with patch.object(subprocess, 'run', side_effect=forged):
            with self.assertRaises(AssertionError):
                oracle.runTest()

    def test_explicit_sdl_sysroot_multiarch_and_ambiguity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pc = root/'usr/lib/test-triplet/pkgconfig/sdl2.pc'
            pc.parent.mkdir(parents=True)
            pc.touch()
            config = root/'usr/include/test-triplet/SDL2/_real_SDL_config.h'
            config.parent.mkdir(parents=True)
            config.touch()
            completed = subprocess.CompletedProcess([], 0, '-I"/path with space/SDL2" -D_REENTRANT', '')
            with patch.object(subprocess, 'run', return_value=completed) as run:
                flags = support.sdl2_cflags({'TYRIAN_TEST_SDL2_SYSROOT': tmp})
                self.assertEqual(flags, ['-I/path with space/SDL2', '-D_REENTRANT', '-I'+str(config.parent.parent)])
                env = run.call_args.kwargs['env']
                self.assertEqual(env['PKG_CONFIG_SYSROOT_DIR'], tmp)
                self.assertEqual(env['PKG_CONFIG_LIBDIR'], str(pc.parent))
                other = root/'usr/include/other-triplet/SDL2/_real_SDL_config.h'
                other.parent.mkdir(parents=True)
                other.touch()
                with self.assertRaisesRegex(RuntimeError, 'Ambiguous'):
                    support.sdl2_cflags({'TYRIAN_TEST_SDL2_SYSROOT': tmp})

    def test_sdl_missing_configuration_is_explicit_error(self):
        failure = subprocess.CalledProcessError(1, ['pkg-config'], stderr='not found')
        with patch.object(subprocess, 'run', side_effect=failure):
            with self.assertRaisesRegex(RuntimeError, 'No test was skipped'):
                support.sdl2_cflags({})
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, 'exactly one'):
                support.sdl2_cflags({'TYRIAN_TEST_SDL2_SYSROOT':tmp})

if __name__ == '__main__':
    unittest.main()
