#!/usr/bin/env python3
"""Keep historical exports explicit and separate from the current runtime.

Legacy CLI tests use an isolated checkout and synthetic tree metadata, never
write a real checkout's manifest, and do not require Git history or network.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_REVISION = 'fedc541cc6b6e93f7748a85e6c40318b6ca9f5a8'
CURRENT = Path('packaging/runtime-assets-v1.json')


class RuntimeManifestRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='runtime-refresh-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.script = self.source / 'scripts/update_runtime_manifest.py'
        self.script.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / 'scripts/update_runtime_manifest.py', self.script)
        self.current_bytes = (ROOT / CURRENT).read_bytes()
        self.write(CURRENT, self.current_bytes)
        self.selection = {
            'gameplay_pack': 'historical/gameplay',
            'gameplay_destination': 'assets/gameplay',
            'startup_pack': 'historical/startup',
            'startup_destination': 'assets/startup',
            'shop_runtime_directories': ['assets/shop'],
            'preserve_in_development_only': ['fixture-artwork'],
        }
        self.write('packaging/runtime-selection-v1.json', json.dumps(self.selection).encode())
        self.tree_content = {'sha': PUBLIC_REVISION, 'truncated': False, 'tree': []}
        # Deliberately synthetic metadata exercises the legacy selection itself,
        # not current authoring mappings or the current manifest as a base.
        for kind, count in [('gameplay', 637), ('startup', 9)]:
            for number in range(count):
                self.tree_content['tree'].append({
                    'path': f'historical/{kind}/{number}.hda', 'type': 'blob',
                    'size': 1, 'sha': hashlib.sha1(b'blob 1\0x').hexdigest(),
                })
        for number in range(15):
            self.write(f'assets/shop/shop{number}.hda', b'historical fixture')
        for name in ['COPYING', 'assets/shop-menu-font-v1/LICENSE-DejaVu.txt',
                     'assets/shop-menu-font-v1/FONT-PROVENANCE.txt',
                     'src/third_party/dr_mp3-LICENSE',
                     'src/third_party/dr_mp3-PROVENANCE.md',
                     'packaging/start-hd.sh', 'packaging/start-hd.ps1',
                     'packaging/runtime-README.txt']:
            self.write(name, b'historical fixture')
        self.write('assets/data-text-zh-CN-v1/data-text-zh-CN-v1-font-manifest.json',
                   b'{"glyph_count": 1}')
        self.tree = self.base / 'historical-tree.json'
        self.tree.write_text(json.dumps(self.tree_content))

    def write(self, relative, data):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def run_legacy(self, *args):
        return subprocess.run([sys.executable, '-B', str(self.script), *map(str, args)],
                              cwd=self.source, capture_output=True, text=True)

    def assert_refused(self, result, reason):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(reason, result.stderr)
        self.assertIn('rebuild_recovered_runtime_manifest.py', result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual((self.source / CURRENT).read_bytes(), self.current_bytes)

    def test_no_arguments_or_old_documented_command_refuse_without_writing(self):
        for args in [(), ('--public-tree', self.tree)]:
            with self.subTest(args=args):
                self.assert_refused(self.run_legacy(*args), 'explicit --output')

    def test_default_output_protection_precedes_selection_and_tree_reads(self):
        (self.source / 'packaging/runtime-selection-v1.json').unlink()
        self.assert_refused(self.run_legacy('--public-tree', self.base / 'missing.json'),
                            'explicit --output')

    def test_explicit_current_paths_refuse_before_input_reads(self):
        (self.source / 'packaging/runtime-selection-v1.json').unlink()
        for output in [CURRENT, self.source / CURRENT,
                       self.source / 'packaging/../packaging/runtime-assets-v1.json']:
            with self.subTest(output=output):
                self.assert_refused(self.run_legacy('--public-tree', self.base / 'missing.json',
                                                    '--output', output),
                                    'must not overwrite the current runtime manifest')

    def test_source_root_override_cannot_overwrite_either_current_manifest(self):
        other = self.base / 'other-source'
        (other / 'packaging').mkdir(parents=True)
        (other / CURRENT).write_bytes(self.current_bytes)
        for output in [other / CURRENT, self.source / CURRENT]:
            with self.subTest(output=output):
                self.assert_refused(self.run_legacy('--source-root', other,
                                                    '--public-tree', self.tree, '--output', output),
                                    'must not overwrite the current runtime manifest')
                self.assertEqual((other / CURRENT).read_bytes(), self.current_bytes)

    def test_missing_current_target_is_also_protected(self):
        current = self.source / CURRENT
        current.unlink()
        result = self.run_legacy('--public-tree', self.tree, '--output', current)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('must not overwrite the current runtime manifest', result.stderr)
        self.assertFalse(current.exists())

    def test_symlink_file_and_parent_aliases_are_refused(self):
        file_alias = self.base / 'alias.json'
        directory_alias = self.base / 'alias-directory'
        file_alias.symlink_to(self.source / CURRENT)
        directory_alias.symlink_to(self.source / 'packaging', target_is_directory=True)
        for output in [file_alias, directory_alias / CURRENT.name]:
            with self.subTest(output=output):
                self.assert_refused(self.run_legacy('--public-tree', self.tree, '--output', output),
                                    'must not overwrite the current runtime manifest')

    def test_hardlink_alias_is_refused(self):
        alias = self.base / 'hardlink.json'
        os.link(self.source / CURRENT, alias)
        self.assert_refused(self.run_legacy('--public-tree', self.tree, '--output', alias),
                            'must not overwrite the current runtime manifest')
        self.assertEqual(alias.read_bytes(), self.current_bytes)

    def test_explicit_historical_export_retains_legacy_semantics(self):
        # A separate export may keep this filename; protection is path/identity
        # based rather than banning a filename or all historical invocations.
        output = self.base / CURRENT.name
        previous = None
        for _ in range(2):
            result = self.run_legacy('--public-tree', self.tree, '--output', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(output.read_text())
            self.assertEqual(json.loads(result.stdout)['files'], 669)
            self.assertEqual(len(manifest['files']), 669)
            historical = [r for r in manifest['files'] if r['group'] in ('gameplay', 'startup')]
            self.assertEqual(len(historical), 646)
            self.assertTrue(all(r['source_path'].startswith('historical/') for r in historical))
            self.assertTrue(all(r['revision'] == PUBLIC_REVISION for r in historical))
            self.assertNotIn('global_hda_files', manifest['closure'])
            self.assertEqual((self.source / CURRENT).read_bytes(), self.current_bytes)
            if previous is not None:
                self.assertEqual(output.read_bytes(), previous)
            previous = output.read_bytes()

    def test_historical_tree_is_still_required_and_validated(self):
        output = self.base / 'historical.json'
        result = self.run_legacy('--output', output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('historical export requires --public-tree', result.stderr)
        self.assertFalse(output.exists())
        for change in [{'truncated': True}, {'sha': 'wrong-revision'}]:
            with self.subTest(change=change):
                self.tree.write_text(json.dumps(dict(self.tree_content, **change)))
                result = self.run_legacy('--public-tree', self.tree, '--output', output)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Expected complete recursive tree', result.stderr)
                self.assertFalse(output.exists())

    def test_current_builder_preserves_all_1006_rows_byte_for_byte(self):
        output = self.base / 'current.json'
        result = subprocess.run([sys.executable, '-B',
                                 str(ROOT / 'scripts/rebuild_recovered_runtime_manifest.py'),
                                 '--root', str(ROOT), '--output', str(output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['files'], 1006)
        self.assertEqual(output.read_bytes(), self.current_bytes)


if __name__ == '__main__':
    unittest.main(verbosity=2)
