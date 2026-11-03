"""Actual-byte finite epoch tests, never derive/build/full asset validation.

TANK194_EPOCH_TEST_ROOT may point to a repository-layout current331 fixture.
Only source, metadata, existing body HDR1 and fixed public proof inputs are read.
No hash constants, source readers or authority predicates are mocked.
"""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get('TANK194_EPOCH_TEST_ROOT', Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import current_tank194_source_bridge as bridge
import current_tank194_body_registration as body
import current_tank_muzzle_source_bridge as muzzle
from verify_current_production import BUILD_INPUTS, source_inventory, source_manifest_digest


class BodyEpoch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = bridge.proof(ROOT)
        b, _ = body.authority(ROOT)
        names = set(cls.p['source_sha256']) | set(BUILD_INPUTS) | {
            bridge.PROOF, body.PROOF, bridge.BINDING, bridge.RUNTIME,
            'packaging/frontend-validation.json', 'packaging/global-validation.json'}
        names |= {r['path'] for r in b['public_sources'].values()}
        names |= {r['manual_row']['source_path'] for r in b['resources']}
        names |= {r['source_path'] for r in cls.p['body_alias_rows']}
        cls.original = {n: body.regular(ROOT, n, 4 * 1024 * 1024) for n in names}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='tank194-epoch-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, raw in self.original.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.manifest = json.loads(self.original[bridge.RUNTIME])

    def put(self, name, raw):
        (self.root / name).write_bytes(raw)

    def test_exact_current331_to_public329_raw_projection(self):
        inventory, restored = bridge.project_sources(self.root)
        self.assertEqual(inventory, self.p['public_source_sha256'])
        self.assertEqual(len(restored), 18)
        self.assertEqual(len(inventory), 329)
        for name, raw in restored.items():
            self.assertEqual(body.sha(raw), inventory[name])
            self.assertEqual(body.blob(raw), self.p['changed_sources'][name]['public_git_blob'])
        self.assertTrue(set(self.p['new_source_sha256']).isdisjoint(inventory))

    def test_real_public_warning_and_muzzle_chain_is_unchanged(self):
        inventory, restored = bridge.project_sources(self.root)
        del inventory[bridge.HEADER]
        self.assertEqual(source_manifest_digest(inventory), bridge.PUBLIC_NONHEADER_DIGEST)
        projected = muzzle.project(inventory, lambda n: restored[n] if n in restored else body.regular(self.root, n))
        self.assertEqual(len(projected), 328)
        self.assertEqual(source_manifest_digest(projected), muzzle.BASE_SOURCE_DIGEST)

    def test_each_changed_source_raw_byte_is_required(self):
        for name in self.p['changed_sources']:
            with self.subTest(name=name):
                self.put(name, self.original[name] + b'\n')
                with self.assertRaises(ValueError):
                    bridge.project_sources(self.root)
                self.put(name, self.original[name])

    def test_each_new_source_raw_byte_is_required_before_removal(self):
        for name in self.p['new_source_sha256']:
            with self.subTest(name=name):
                self.put(name, self.original[name] + b'\n')
                with self.assertRaises(ValueError):
                    bridge.project_sources(self.root)
                self.put(name, self.original[name])

    def test_missing_extra_and_mixed_sources_rejected(self):
        name = next(iter(self.p['changed_sources']))
        inventory, restored = bridge.project_sources(self.root)
        self.put(name, restored[name])
        with self.assertRaises(ValueError):
            bridge.project_sources(self.root)
        self.put(name, self.original[name])
        extra = self.root / 'src/unreviewed.txt'
        extra.write_text('unreviewed')
        with self.assertRaises(ValueError):
            bridge.project_sources(self.root)
        extra.unlink()
        (self.root / name).unlink()
        with self.assertRaises(ValueError):
            bridge.project_sources(self.root)

    def test_unchanged_source_drift_is_not_hidden_by_inverse(self):
        name = next(n for n in self.p['public_source_sha256'] if n not in self.p['changed_sources'])
        self.put(name, self.original[name] + b'\n')
        with self.assertRaises(ValueError):
            bridge.project_sources(self.root)

    def test_proof_or_native_header_comment_drift_rejected(self):
        self.put(bridge.PROOF, self.original[bridge.PROOF] + b'\n')
        with self.assertRaises(ValueError):
            bridge.project_sources(self.root)
        self.put(bridge.PROOF, self.original[bridge.PROOF])
        name = body.HEADER
        self.put(name, self.original[name].replace(b' * Source proof SHA256:', b' * Other proof SHA256:', 1))
        with self.assertRaises(ValueError):
            bridge.project_sources(self.root)

    def test_runtime1133_to1131_preserves_every_other_row(self):
        rows = bridge.project_runtime_rows(self.root, self.manifest)
        self.assertEqual(len(rows), 1131)
        self.assertEqual(rows, [r for r in self.manifest['files'] if r not in self.p['body_alias_rows']])
        self.assertEqual(len(self.manifest['files']), 1133)
        self.assertEqual((self.root / bridge.RUNTIME).read_bytes(), self.original[bridge.RUNTIME])

    def test_missing_duplicate_and_malformed_body_rows_rejected(self):
        row = self.p['body_alias_rows'][0]
        variants = []
        missing = copy.deepcopy(self.manifest)
        missing['files'].remove(row)
        variants.append(missing)
        duplicate = copy.deepcopy(self.manifest)
        duplicate['files'].append(row)
        variants.append(duplicate)
        malformed = copy.deepcopy(self.manifest)
        next(r for r in malformed['files'] if r == row)['identity'] = True
        variants.append(malformed)
        for manifest in variants:
            with self.assertRaises(ValueError):
                bridge.project_runtime_rows(self.root, manifest)

    def test_alias_bytes_are_checked_before_projection(self):
        for row in self.p['body_alias_rows']:
            name = row['source_path']
            self.put(name, self.original[name][:-1] + bytes([self.original[name][-1] ^ 1]))
            with self.assertRaises(ValueError):
                bridge.project_runtime_rows(self.root, self.manifest)
            self.put(name, self.original[name])

    def test_unrelated_runtime_row_is_never_exempted(self):
        row = next(r for r in self.manifest['files'] if r not in self.p['body_alias_rows'] and r['source_path'] != bridge.BINDING)
        row['destination'] = 'assets/unreviewed.bin'
        with self.assertRaisesRegex(ValueError, 'runtime row changed'):
            bridge.project_runtime_rows(self.root, self.manifest)

    def test_current_binding_raw_and_digest_tamper_rejected(self):
        self.manifest['source_revision']['current_production_source_manifest_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            bridge.project_runtime_rows(self.root, self.manifest)
        self.manifest = json.loads(self.original[bridge.RUNTIME])
        self.put(bridge.BINDING, self.original[bridge.BINDING] + b'\n')
        with self.assertRaises(ValueError):
            bridge.project_runtime_rows(self.root, self.manifest)

    def test_duplicate_binding_marker_rejected(self):
        target = next(r for r in self.manifest['files'] if r not in self.p['body_alias_rows'] and r['source_path'] != bridge.BINDING)
        target['group'] = 'current-production-validation'
        with self.assertRaises(ValueError):
            bridge.project_runtime_rows(self.root, self.manifest)

    def test_source_and_alias_symlinks_rejected(self):
        for name in [next(iter(self.p['new_source_sha256'])), self.p['body_alias_rows'][0]['source_path']]:
            path = self.root / name
            path.unlink()
            target = self.root / 'standin'
            target.write_bytes(self.original[name])
            path.symlink_to(target)
            with self.assertRaises(ValueError):
                if name.startswith('src/'):
                    bridge.project_sources(self.root)
                else:
                    bridge.project_runtime_rows(self.root, self.manifest)
            path.unlink()
            path.write_bytes(self.original[name])
            target.unlink()

    def test_old_and_new_source_epochs_cannot_be_mixed(self):
        actual = source_inventory(self.root)
        del actual[bridge.HEADER]
        with self.assertRaises(ValueError):
            muzzle.project(actual, lambda n: body.regular(self.root, n))
        inventory, restored = bridge.project_sources(self.root)
        for name, raw in restored.items():
            self.put(name, raw)
        for name in self.p['new_source_sha256']:
            (self.root / name).unlink()
        with self.assertRaises(ValueError):
            bridge.project_sources(self.root)

    def test_no_original_data_or_new_art_input(self):
        self.assertFalse(any(Path(n).name in {'newshp.shp', 'tyrian.hdt'} for n in self.original))
        self.assertEqual(len([n for n in self.original if n.endswith('.hda')]), 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
