#!/usr/bin/env python3
"""Opt-in audit catalog tests; no runtime storage changes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
import test_runtime_packaging as fixture
PACK, row = fixture.PACK, fixture.row


class CatalogTests(unittest.TestCase):
    setUp = fixture.PackagingTests.setUp
    tearDown = fixture.PackagingTests.tearDown
    save = fixture.PackagingTests.save
    run_pack = fixture.PackagingTests.run_pack
    def catalog(self, name='catalog.json', *extra):
        target = self.base / name
        code, report = self.run_pack('--content-catalog', target, *extra)
        self.assertEqual(code, 0)
        return target, json.loads(target.read_text()), report

    def add_copy(self, name='copy.hda', data=None):
        data = self.data if data is None else data
        (self.source / 'assets' / name).write_bytes(data)
        self.content['files'].append(row('assets/' + name, 'other/' + name, data))
        self.save()

    def test_catalog_groups_full_bytes_and_preserves_paths(self):
        self.add_copy()
        target, catalog, _ = self.catalog()
        summary = catalog['summary']
        self.assertEqual((summary['logical_files'], summary['unique_contents'], summary['duplicate_groups']), (2, 1, 1))
        self.assertEqual(summary['duplicate_bytes'], len(self.data))
        self.assertEqual(summary['bytes_saved_by_this_tool'], 0)
        self.assertEqual(len(catalog['files']), 2)
        self.assertNotIn(str(self.base), target.read_text())
        self.assertEqual(self.run_pack('--check-content-catalog', target)[0], 0)

    def test_catalog_order_independent_and_repeatable(self):
        self.add_copy()
        first, _, _ = self.catalog()
        self.content['files'].reverse(); self.save()
        second, _, _ = self.catalog('second.json')
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_zero_byte_content_and_different_size(self):
        self.add_copy('empty.hda', b'')
        self.add_copy('empty2.hda', b'')
        _, catalog, _ = self.catalog()
        self.assertEqual(catalog['summary']['unique_contents'], 2)
        self.assertEqual(catalog['summary']['duplicate_bytes'], 0)

    def test_same_pixels_different_header_not_equivalent(self):
        self.add_copy('header1.hda', b'HDR1\x00' + self.data)
        self.add_copy('header2.hda', b'HDR1\x01' + self.data)
        _, catalog, _ = self.catalog()
        self.assertEqual(catalog['summary']['unique_contents'], 3)

    def test_drift_rejected_before_build(self):
        target, catalog, _ = self.catalog()
        mutations = [lambda c: c.update(schema='wrong'), lambda c: c['summary'].update(bytes_saved_by_this_tool=1),
                     lambda c: c['files'][0].update(destination='../unsafe'), lambda c: c['contents'][0].update(sha256='g'*64),
                     lambda c: c['files'].append(dict(c['files'][0])), lambda c: c['files'].clear(),
                     lambda c: c['summary'].update(logical_files=1.0), lambda c: c['summary'].update(logical_files=True)]
        for mutate in mutations:
            current = json.loads(json.dumps(catalog)); mutate(current); target.write_text(json.dumps(current))
            with self.assertRaises(ValueError):
                self.run_pack('--check-content-catalog', target, '--build', '--output', self.base/'out')
            self.assertFalse((self.base/'out').exists())

    def test_changed_valid_selection_rejected(self):
        target, _, _ = self.catalog()
        self.add_copy()
        with self.assertRaises(ValueError): self.run_pack('--check-content-catalog', target)

    def test_missing_and_corrupt_refuse_partial_catalog(self):
        source = self.source/'assets/art.hda'
        source.write_bytes(b'x' * len(self.data))
        with self.assertRaises(ValueError): self.catalog()
        self.assertFalse((self.base/'catalog.json').exists())
        source.unlink()
        with self.assertRaises(ValueError): self.catalog()

    def test_symlink_sources_refuse_catalog(self):
        source = self.source/'assets/art.hda'; other = self.base/'copy'; source.rename(other); source.symlink_to(other)
        with self.assertRaises(ValueError): self.catalog()
        self.assertFalse((self.base/'catalog.json').exists())

    def test_source_map_portability(self):
        target, _, _ = self.catalog()
        source = self.source/'assets/art.hda'; mapped = self.base/'mapped'; source.rename(mapped)
        mapping = self.base/'mapping.json'; mapping.write_text(json.dumps({'assets/art.hda': str(mapped)}))
        second, _, _ = self.catalog('mapped-catalog.json', '--source-map', mapping)
        self.assertEqual(target.read_bytes(), second.read_bytes())

    def test_catalog_existing_or_source_output_rejected(self):
        target, _, _ = self.catalog()
        with self.assertRaises(ValueError): self.run_pack('--content-catalog', target)
        with self.assertRaises(ValueError): self.run_pack('--content-catalog', self.source/'catalog.json')

    def test_output_collisions_refused(self):
        for flag in ('--report', '--zip', '--output'):
            path = self.base/'same'
            extra = ['--build', '--output', self.base/'out'] if flag == '--zip' else []
            with self.assertRaises(ValueError): self.run_pack('--content-catalog', path, flag, path, *extra)
            self.assertFalse(path.exists())
        with self.assertRaises(ValueError): self.run_pack('--content-catalog', self.base/'out/catalog', '--build', '--output', self.base/'out')

    def test_input_symlink_and_duplicate_json_keys_rejected(self):
        target, _, _ = self.catalog()
        link = self.base/'link'; link.symlink_to(target)
        with self.assertRaises(ValueError): self.run_pack('--check-content-catalog', link)
        target.write_text('{"schema":"a","schema":"b"}')
        with self.assertRaises(ValueError): self.run_pack('--check-content-catalog', target)

    def test_platform_and_executable_are_identity(self):
        target, _, _ = self.catalog()
        with self.assertRaises(ValueError): self.run_pack('--check-content-catalog', target, '--platform', 'windows')
        exe = self.base/'exe'; exe.write_bytes(b'not executed')
        other, catalog, _ = self.catalog('executable-catalog.json', '--executable', exe)
        self.assertEqual(catalog['summary']['logical_files'], 2)
        self.assertEqual(catalog['files'][-1]['destination'], 'opentyrian2000')

    def test_default_report_and_package_bytes_unchanged(self):
        _, baseline_report = self.run_pack()
        target, _, catalog_report = self.catalog()
        self.assertEqual(baseline_report, catalog_report)
        first, second = self.base/'old', self.base/'new'
        self.run_pack('--build', '--output', first)
        self.run_pack('--check-content-catalog', target, '--build', '--output', second)
        digest = lambda d: {p.relative_to(d).as_posix(): (p.read_bytes(), p.stat().st_mode & 0o777) for p in d.rglob('*') if p.is_file()}
        self.assertEqual(digest(first), digest(second))

    def test_invalid_manifest_sha256_rejected_only_in_catalog_mode(self):
        for digest in ('', None, False, 'f'*63, 'G'*64):
            self.content['files'][0]['sha256'] = digest; self.save()
            with self.assertRaises(ValueError): self.catalog()
        del self.content['files'][0]['sha256']; self.save()
        self.assertEqual(self.catalog()[1]['summary']['logical_files'], 1)

    def test_nonfinite_snapshot_numbers_refused(self):
        target = self.base/'snapshot.json'
        for value in ('NaN', 'Infinity', '-Infinity'):
            target.write_text('{"value":' + value + '}')
            with self.assertRaises(ValueError): self.run_pack('--check-content-catalog', target)

    def test_real_catalog_known_duplicate_accounting(self):
        manifest = PACK.load_manifest(ROOT/'packaging/runtime-assets-v1.json')
        verified = [PACK.checked_source(PACK.contained_file(ROOT, r['source_path']), r) for r in manifest['files']]
        catalog = PACK.content_catalog(verified, 'linux')
        self.assertEqual(catalog['summary']['logical_files'], 1006)
        # Current Pulse compatibility intentionally matches its five approved global blobs.
        self.assertEqual(catalog['summary']['unique_contents'], 880)
        self.assertEqual(catalog['summary']['duplicate_groups'], 126)
        self.assertEqual(catalog['summary']['duplicate_bytes'], 12911168)


if __name__ == '__main__':
    unittest.main()
