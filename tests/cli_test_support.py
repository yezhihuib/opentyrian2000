"""Counted adapters for CLI-only oracles. Missing required inputs are errors.

No auto-downloads, implicit workspace paths, suppressed checks or success skips.
"""
from pathlib import Path
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest

REGISTRY = {
    'test_pregame_coexistence.py': 'receipt',
    'test_pregame_font_integration.py': 'receipt',
    'test_settings_integration.py': 'receipt',
    'test_rear_multi_p10_mode1_inputs.py': 'data',
    'test_rear_multi_p10_mode2_inputs.py': 'data',
    'test_rear_multi_p11_mode1_inputs.py': 'data',
    'test_rear_multi_p11_mode2_inputs.py': 'data',
    'test_reconstructed_menu_runs.py': 'directory',
}


def original_data_directory(environ=None):
    environ = os.environ if environ is None else environ
    value = environ.get('TYRIAN_TEST_DATA')
    if not value:
        raise RuntimeError('Authentic-input oracle requires TYRIAN_TEST_DATA=/path/to/tyrian2000; no test was skipped.')
    path = Path(value).expanduser().resolve()
    for name in ('tyrian.hdt', 'tyrian.shp'):
        if not (path / name).is_file():
            raise RuntimeError(f'TYRIAN_TEST_DATA is missing required original data: {name}')
    return path


def sdl2_cflags(environ=None):
    """Use standard pkg-config env, optionally an explicit relocated sysroot."""
    env = dict(os.environ if environ is None else environ)
    root = env.get('TYRIAN_TEST_SDL2_SYSROOT')
    if root:
        root = Path(root).expanduser().resolve()
        candidates = [root/'usr/lib/pkgconfig', root/'usr/share/pkgconfig',
                      *sorted((root/'usr/lib').glob('*/pkgconfig'))]
        candidates = [p for p in candidates if (p/'sdl2.pc').is_file()]
        if len(candidates) != 1:
            raise RuntimeError('TYRIAN_TEST_SDL2_SYSROOT must contain exactly one usr/lib[/<triplet>]/pkgconfig/sdl2.pc')
        env['PKG_CONFIG_LIBDIR'] = str(candidates[0])
        env['PKG_CONFIG_SYSROOT_DIR'] = str(root)
    try:
        p = subprocess.run(['pkg-config', '--cflags', 'sdl2'], env=env,
                           text=True, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, 'stderr', '') or str(exc)
        raise RuntimeError('SDL2 development headers required. Configure standard PKG_CONFIG_PATH / PKG_CONFIG_SYSROOT_DIR or TYRIAN_TEST_SDL2_SYSROOT. No test was skipped.\n'+detail) from exc
    flags = shlex.split(p.stdout)
    if not flags:
        raise RuntimeError('pkg-config returned no SDL2 include flags')
    if root:
        # Debian-style sysroots split SDL_config into a multiarch directory;
        # normal system compilation finds this implicitly, relocated roots do not.
        multiarch = sorted(root.glob('usr/include/*/SDL2/_real_SDL_config.h'))
        if len(multiarch) > 1:
            raise RuntimeError('Ambiguous SDL2 multiarch config in test sysroot')
        if multiarch:
            flags.append('-I'+str(multiarch[0].parent.parent))
    return flags


class CliOracle(unittest.TestCase):
    def __init__(self, script):
        super().__init__('runTest')
        self.script = Path(script).resolve()
        if self.script.name not in REGISTRY:
            raise ValueError('Unregistered CLI oracle: '+self.script.name)

    def id(self):
        return self.script.stem+'.CliOracle.test_cli_oracle'

    def runTest(self):
        kind = REGISTRY[self.script.name]
        with tempfile.TemporaryDirectory(prefix=self.script.stem+'-') as tmp:
            directory = Path(tmp)
            receipt = directory/'receipt.json'
            if kind == 'data':
                args = [str(original_data_directory())]
            elif kind == 'receipt':
                args = ['--out', str(receipt)]
            else:
                args = [str(directory)]
            completed = subprocess.run([sys.executable, str(self.script), *args],
                                       text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0,
                             completed.stdout+'\n'+completed.stderr)
            self.assertTrue(completed.stdout.strip(), 'Oracle produced no evidence')
            if kind == 'data':
                self.assertIn('authentic-input PASS:', completed.stdout)
            else:
                self.assertTrue(receipt.is_file(), 'Oracle did not write its receipt')
                result = json.loads(receipt.read_text())
                self.assertEqual(result.get('result', result.get('status')), 'PASS')
                fields = {
                    'test_pregame_coexistence.py': ('production_files', 'production_mutation_rejections', 'whole_parent_files'),
                    'test_pregame_font_integration.py': ('unchanged_prior_files', 'mutation_rejections'),
                    'test_settings_integration.py': ('previous_files_checked', 'projection_mutation_rejections'),
                    'test_reconstructed_menu_runs.py': ('whole_string_raqm_cases', 'independent_alpha_pixels', 'resource_mutation_negatives'),
                }[self.script.name]
                for field in fields:
                    self.assertIs(type(result.get(field)), int, field)
                    self.assertGreater(result[field], 0, field)



def cli_suite(script):
    return unittest.TestSuite([CliOracle(script)])
