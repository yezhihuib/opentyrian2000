#!/usr/bin/env python3
"""Package/static and isolated switch checks. No game or resource decoder runs."""
from pathlib import Path
import collections
import hashlib
import importlib.util
import json
import os
import re
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / 'SOURCE.json').read_text())


def source(name):
    paths = [ROOT / path for path in MANIFEST['source_sha256'] if Path(path).name == name]
    if len(paths) != 1:
        raise AssertionError('Expected exactly one source variant: ' + name)
    return paths[0].read_text()


class ReleaseTests(unittest.TestCase):
    def test_source_integrity(self):
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'sources').rglob('*') if p.is_file()}
        self.assertEqual(actual, set(MANIFEST['source_sha256']))
        self.assertEqual(len(actual), 475)
        for name, expected in MANIFEST['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)

    def test_complete_production_units(self):
        units = MANIFEST['translation_units']
        self.assertEqual(len(units), 112)
        self.assertNotIn('entry-shim', units)
        self.assertEqual(sum(path.endswith('.c') for path in MANIFEST['source_sha256']), 112)
        for unit in units.values():
            self.assertIn(unit['source'], MANIFEST['source_sha256'])
            self.assertFalse(any(value.startswith('main=') for value in unit['defines']))
            for dependency in unit['local_dependencies']:
                self.assertIn(dependency, MANIFEST['source_sha256'])
        self.assertRegex((ROOT / units['opentyr']['source']).read_text(), r'\bmain\s*\(')

    def test_header_versions_not_flattened(self):
        versions = collections.defaultdict(set)
        paths = collections.defaultdict(set)
        for path, value in MANIFEST['source_sha256'].items():
            if path.endswith('.h'):
                versions[Path(path).name].add(value)
                paths[Path(path).name].add(path)
        conflicting = {name: values for name, values in versions.items() if len(values) > 1}
        self.assertEqual(len(conflicting), 3)
        self.assertEqual(sum(map(len, conflicting.values())), 9)
        for name, values in conflicting.items():
            self.assertGreaterEqual(len(paths[name]), len(values))

    def test_source_only_scope(self):
        self.assertFalse(MANIFEST['runtime_art_included'])
        self.assertFalse(MANIFEST['activation_launcher_included'])
        self.assertFalse(MANIFEST['gameplay_validation'])
        for name in MANIFEST['source_sha256']:
            self.assertIn(Path(name).suffix, ('.c', '.h', '.inc'))
            self.assertNotIn('sysroot', name)
            self.assertFalse((ROOT / name).is_symlink())
        self.assertFalse(any(ROOT.glob('*launch*')))

    def test_no_machine_paths(self):
        forbidden = ('/work' + 'space/', '/ho' + 'me/agent/', '/Us' + 'ers/')
        for name in list(MANIFEST['source_sha256']) + ['SOURCE.json', 'build.py']:
            text = (ROOT / name).read_text()
            for value in forbidden:
                self.assertNotIn(value, text, name)
        terrain = source('b313_family_ground_mirror.inc')
        self.assertIn('#define FG_ROOT "assets/hd/current-terrain23"', terrain)

    def test_damaged_longface_is_rejected_before_canvas(self):
        text = source('longface573_family_mirror.inc')
        begin = text.index('static bool longface573_tile(')
        body = text[begin:text.index('\n}', begin)]
        reject = body.index('if(enemy[slot].edamaged)return false;')
        self.assertLess(reject, body.index('family_prepare_canvas()'))
        self.assertLess(reject, body.index('private_longface573_frame.cycles[slot]='))
        self.assertLess(body.index('slot>=100'), reject)

    def test_builder_never_activates_or_runs_game(self):
        spec = importlib.util.spec_from_file_location('late_level_builder', ROOT / 'build.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(len(module.inspect_sources()['translation_units']), 112)
        text = (ROOT / 'build.py').read_text()
        self.assertNotIn('setenv', text)
        self.assertNotIn('os.environ[', text)
        self.assertIn("'cached_objects_reused': 0", text)
        self.assertIn('if build.exists():', text)
        self.assertIn('local != set(unit[', text)

    def test_git_byte_preservation_and_ignored_outputs(self):
        attrs = (ROOT / '.gitattributes').read_text()
        self.assertIn('* -text', attrs)
        self.assertIn('**/* -text', attrs)
        ignored = (ROOT / '.gitignore').read_text()
        self.assertIn('/build/', ignored)
        self.assertIn('/.test-build/', ignored)

    def test_compiled_default_off_switch_predicates(self):
        # Compile only extracted side-effect-free predicates. No game objects,
        # SDL, gameplay fixtures, real environment or asset readers are used.
        names = {
            'lpf_enabled': ('launcher271_family_mirror.inc', 1),
            'ln_enabled': ('linked338_normal_family_mirror.inc', 1),
            'tp_enabled': ('turret273_family_mirror.inc', 1),
            'ts_enabled': ('tall_structure_family_mirror.inc', 1),
            'la_enabled': ('late_actor_family_mirror.inc', 1),
            't194_enabled': ('tank194_family_mirror.inc', 1),
            't194_repeat8_requested': ('tank194_family_mirror.inc', 1),
            't194_next7_requested': ('tank194_family_mirror.inc', 1),
            'fr462_enabled': ('firing_rock462_family_mirror.inc', 1),
            'rp_enabled': ('random_props_family_mirror.inc', 1),
            'sr_enabled': ('smallrocks_family_mirror.inc', 1),
            'f284_enabled': ('fork284_family_mirror.inc', 1),
            'c309_enabled': ('compound309270_family_mirror.inc', 1),
            'private_longface573_mode': ('longface573_family_mirror.inc', 2),
            'private_longface573_later_requested': ('longface573_family_mirror.inc', 1),
            'private_lamp272_later_requested': ('lamp272_family_mirror.inc', 1),
            'private_lamp272_middle_requested': ('lamp272_family_mirror.inc', 1),
            'l271_requested': ('launcher271_lineage.inc', 1),
        }
        bodies, checks = [], []
        for name, (file, enabled) in names.items():
            match = re.search(r'static (?:bool|unsigned) ' + name + r'\(void\)\s*\{[^{}]*\}', source(file))
            self.assertIsNotNone(match, name)
            bodies.append(match[0])
            envs = re.findall(r'getenv\("([A-Z0-9_]+)"\)', match[0])
            checks.append('selected = NULL; missing = NULL; if (' + name + '()) return __LINE__;')
            for value in ('', '0', '01', 'true', ' 1', '1 '):
                checks.append('selected = ' + json.dumps(value) + '; if (' + name + '()) return __LINE__;')
            checks.append('selected = "1"; if (' + name + '() != ' + str(enabled) + ') return __LINE__;')
            for env in envs:
                checks.append('missing = ' + json.dumps(env) + '; if (' + name + '()) return __LINE__;')
            checks.append('missing = NULL;')
        harness = ('#include <stdbool.h>\n#include <stddef.h>\n#include <string.h>\n'
                   '#define B313_FAMILY_CANVAS_DIAGNOSTIC 1\n'
                   'static const char *selected, *missing;\n'
                   'static const char *mock_getenv(const char *key) { return missing && !strcmp(missing,key) ? NULL : selected; }\n'
                   '#define getenv mock_getenv\n' + '\n'.join(bodies) +
                   '\nint main(void) {\n' + '\n'.join(checks) + '\nreturn 0;\n}\n')
        base = Path(os.environ.get('LATE_LEVEL_TEST_OUTPUT', str(ROOT / '.test-build')))
        base.mkdir(parents=True, exist_ok=True)
        output = Path(tempfile.mkdtemp(prefix='switches-', dir=base))
        cfile = output / 'switches.c'
        cfile.write_text(harness)
        binary = output / 'switches'
        subprocess.run(shlex.split(os.environ.get('CC', 'cc')) +
                       ['-std=c99', '-Wall', '-Wextra', '-Werror', str(cfile), '-o', str(binary)], check=True)
        subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    unittest.main()
