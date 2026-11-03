"""Small synthetic metadata fixtures: no artwork, licensed data, or native build."""
import builtins
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import check_runtime_source_binding as CHECK
import package_runtime as PACK


class BindingPreflight(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'packaging').mkdir()
        self.path = self.root / 'packaging/runtime-assets-v1.json'
        self.receipt_path = self.root / CHECK.SOURCE
        self.receipt = {'schema': 'opentyrian-current-production-binding-v1', 'source_sha256': {'src/a.c': '1' * 64}}
        self.receipt['production_source_manifest_sha256'] = CHECK.source_manifest_digest(self.receipt['source_sha256'])
        raw = (json.dumps(self.receipt, sort_keys=True) + '\n').encode()
        self.receipt_path.write_bytes(raw)
        self.row = {'source_path': CHECK.SOURCE, 'destination': CHECK.DESTINATION, 'group': 'current-production-validation', 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'git_blob': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()}
        self.manifest = {'schema': 'opentyrian-runtime-package-v1', 'source_revision': {CHECK.DIGEST: self.receipt['production_source_manifest_sha256']}, 'external_dependencies': {}, 'files': [self.row]}
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.manifest))

    def rejects(self):
        self.save()
        with self.assertRaisesRegex(ValueError, 'rebuild the runtime manifest'):
            CHECK.check(self.root, self.path)

    def test_current_valid_metadata_only(self):
        self.assertFalse((self.root / 'src').exists())
        self.assertEqual(CHECK.check(self.root, self.path)['declared_source_files'], 1)

    def test_stale_top_digest(self):
        self.manifest['source_revision'][CHECK.DIGEST] = '2' * 64
        self.rejects()

    def test_missing_top_digest(self):
        self.manifest['source_revision'].clear()
        self.rejects()

    def test_missing_binding_row(self):
        self.manifest['files'].clear()
        self.rejects()

    def test_duplicate_binding_row(self):
        self.manifest['files'].append(copy.deepcopy(self.row))
        self.rejects()

    def test_receipt_inventory_mutation(self):
        self.receipt['source_sha256']['src/a.c'] = '3' * 64
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.rejects()

    def test_receipt_internal_digest_mutation(self):
        self.receipt['production_source_manifest_sha256'] = '4' * 64
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.rejects()

    def test_row_fingerprints_and_boolean_size(self):
        for key, value in [('bytes', True), ('bytes', 0), ('sha256', '0' * 64), ('git_blob', '0' * 40)]:
            with self.subTest(key=key, value=value):
                original = self.row[key]
                self.row[key] = value
                self.rejects()
                self.row[key] = original

    def test_receipt_missing_or_symlink(self):
        original = self.receipt_path.read_bytes()
        self.receipt_path.unlink()
        self.rejects()
        target = self.root / 'other.json'
        target.write_bytes(original)
        self.receipt_path.symlink_to(target)
        self.rejects()

    def test_duplicate_json_keys(self):
        self.path.write_text(self.path.read_text().replace('"source_revision":', '"source_revision": {}, "source_revision":'))
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            CHECK.check(self.root, self.path)

    def test_duplicate_receipt_keys(self):
        self.receipt_path.write_text(self.receipt_path.read_text().replace('"source_sha256":', '"source_sha256": {}, "source_sha256":'))
        self.rejects()

    def test_renamed_current_still_checked(self):
        self.manifest['source_revision'][CHECK.DIGEST] = '0' * 64
        self.path = self.root / 'renamed.json'
        self.rejects()

    def test_each_content_marker_requires_current_contract(self):
        for keep in ('source_path', 'destination', 'group'):
            with self.subTest(marker=keep):
                row = dict(self.row)
                for key in ('source_path', 'destination', 'group'):
                    if key != keep:
                        row[key] = 'other'
                self.manifest['files'] = [row]
                self.manifest['source_revision'] = {}
                self.path = self.root / 'custom.json'
                self.rejects()

    def test_legacy_custom_without_markers_compatible(self):
        self.path = self.root / 'legacy.json'
        self.manifest['files'] = []
        self.manifest['source_revision'] = {'historical': 'unchanged'}
        self.save()
        self.assertEqual(CHECK.check(self.root, self.path)['status'], 'NOT_APPLICABLE')

    def test_nonempty_legacy_without_revision_reaches_old_downstream(self):
        self.path = self.root / 'custom-without-revision.json'
        del self.manifest['source_revision']
        self.manifest['files'] = [dict(self.row, source_path='assets/example.hda', destination='assets/example.hda', group='fixture')]
        self.save()
        self.assertEqual(CHECK.check(self.root, self.path)['status'], 'NOT_APPLICABLE')
        actual_import = builtins.__import__
        class ReachedDownstream(Exception):
            pass
        def monitored(name, *args, **kwargs):
            if name == 'current_projectile145_compatibility':
                raise ReachedDownstream
            return actual_import(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=monitored):
            with self.assertRaises(ReachedDownstream):
                PACK.main(['--source-root', str(self.root), '--manifest', str(self.path)])

    def test_default_cannot_drop_all_markers(self):
        self.manifest['files'] = []
        self.manifest['source_revision'] = {}
        self.rejects()

    def test_invalid_digest_types_and_nonfinite(self):
        for value in (None, True, 7, 'F' * 64, '0' * 63):
            with self.subTest(value=value):
                self.manifest['source_revision'][CHECK.DIGEST] = value
                self.rejects()
        self.path.write_text('{"files": [], "source_revision": {"x": NaN}}')
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            CHECK.check(self.root, self.path)

    def test_cli_read_only_success_and_actionable_failure(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        command = [sys.executable, '-B', str(SCRIPTS / 'check_runtime_source_binding.py'), '--root', str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'PASS')
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.manifest['source_revision'][CHECK.DIGEST] = '0' * 64
        self.save()
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('do not edit hashes by hand', result.stderr)

    def test_package_default_explicit_and_renamed_fail_before_producer_or_output(self):
        self.manifest['source_revision'][CHECK.DIGEST] = '0' * 64
        self.save()
        renamed = self.root / 'renamed.json'
        renamed.write_bytes(self.path.read_bytes())
        actual_import = builtins.__import__
        entered = []
        def monitored(name, *args, **kwargs):
            if name.startswith('current_'):
                entered.append(name)
                raise AssertionError('producer reached')
            return actual_import(name, *args, **kwargs)
        for extra in ([], ['--manifest', str(self.path)], ['--manifest', str(renamed)]):
            with self.subTest(extra=extra), patch('builtins.__import__', side_effect=monitored):
                with self.assertRaisesRegex(ValueError, 'top-level'):
                    PACK.main(['--source-root', str(self.root), '--build', '--output', str(self.root / 'output')] + extra)
                self.assertEqual(entered, [])
                self.assertFalse((self.root / 'output').exists())

    def test_valid_package_reaches_current_body_validation_before_legacy(self):
        actual_import = builtins.__import__
        class ReachedDownstream(Exception):
            pass
        def monitored(name, *args, **kwargs):
            if name == 'current_tank194_body_registration':
                raise ReachedDownstream
            return actual_import(name, *args, **kwargs)
        for extra in ([], ['--manifest', str(self.path)]):
            with patch('builtins.__import__', side_effect=monitored):
                with self.assertRaises(ReachedDownstream):
                    PACK.main(['--source-root', str(self.root)] + extra)


if __name__ == '__main__':
    unittest.main()
