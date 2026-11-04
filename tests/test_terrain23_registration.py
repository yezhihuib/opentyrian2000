"""Finite terrain23 registration tests; never a complete package/runtime PASS.

Every mutation uses a fresh independently copied temporary root, never hardlinks.
Only the private inverse helper is exercised with forged *in-memory* proof data.
Default CLI probes are dry packaging/manifest operations: no compiler/game runs,
no stub imports, no generated old payloads, and no writes to any original tree.

Run with Python -B. Optional TERRAIN23_REPORT_DIR saves a structured result and
exact subprocess diagnostics separately from the source under test.
"""
import contextlib
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
ROOT = Path(os.environ.get('TERRAIN23_TEST_SOURCE_ROOT', Path(__file__).resolve().parents[1])).resolve()
OLD_ROOT = Path(os.environ.get('TERRAIN23_OLD_SOURCE_ROOT', ROOT.parents[1] /
    'recovery-pose13-topclip/tank194-topclip-registration-result-final/registration-candidate')).resolve()
sys.path.insert(0, str(ROOT / 'scripts'))
import current_tank194_body_registration as checked
import current_tank194_source_bridge as old_bridge
import current_terrain23_registration as terrain
import current_terrain23_source_bridge as bridge
from verify_current_production import source_inventory, source_manifest_digest, verify

MANIFEST = 'packaging/runtime-assets-v1.json'
LOADED_CODE_SHA256 = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),
    ROOT / 'scripts/current_terrain23_source_bridge.py', ROOT / 'scripts/current_terrain23_registration.py']}
REPORT = {'scope': 'Targeted Python registration tests only; no compilation or game runs',
          'full_package_acceptance': False, 'cases': [], 'cli_probes': []}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def snapshot(root):
    """Bounded immutable inputs, excluding scripts concurrently integrated by parent."""
    names = set(source_inventory(root))
    proof = terrain.authority(root)
    names.update(proof['source_build_input_sha256'])
    names.update(proof['historical_validation_sha256'])
    names.update((terrain.PROOF, bridge.BINDING, MANIFEST))
    names.update(row['source_path'] for row in proof['rows'])
    return {name: digest((root / name).read_bytes()) for name in sorted(names)}


@contextlib.contextmanager
def fresh_root(original=ROOT):
    with tempfile.TemporaryDirectory(prefix='terrain23-registration-') as tmp:
        root = Path(tmp) / 'source'
        shutil.copytree(original, root, copy_function=shutil.copyfile,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
        # A source fixture must be physically independent, not merely a new path.
        for name in ('src/render_mirror.c', bridge.BINDING):
            if (original / name).exists():
                assert (original / name).stat().st_ino != (root / name).stat().st_ino
                assert (root / name).stat().st_nlink == 1
        yield root


def read_json(root, name=MANIFEST):
    return checked.object_bytes((root / name).read_bytes())


def mutate_byte(path, offset=-1):
    raw = bytearray(path.read_bytes())
    raw[offset] ^= 1
    path.write_bytes(raw)


def source_raw(root):
    return {name: (root / name).read_bytes() for name in source_inventory(root)}


class Terrain23FiniteRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = snapshot(ROOT)
        cls.proof = terrain.authority(ROOT)
        cls.old_manifest = read_json(OLD_ROOT)
        cls.old_receipt = (OLD_ROOT / bridge.BINDING).read_bytes()
        cls.expected_rows = terrain.rows_for(ROOT)
        cls.aliases = [row for row in cls.old_manifest['files']
                       if row.get('group') == 'global-source-identity' and
                       str(row.get('revision', '')).startswith('canonical-tank194-')]
        if len(cls.aliases) != 8:
            raise AssertionError('Expected eight genuine old tank aliases, found %s' % len(cls.aliases))

    @classmethod
    def tearDownClass(cls):
        if snapshot(ROOT) != cls.original:
            raise AssertionError('Original approved source/proof/receipt/manifest/payload inputs changed')
        REPORT['original_frozen_inputs_unchanged'] = True
        REPORT['frozen_input_count'] = len(cls.original)

    def reject_source(self, root, pattern=None):
        if pattern:
            with self.assertRaisesRegex((ValueError, OSError), pattern):
                bridge.verify_source_epoch(root)
        else:
            with self.assertRaises((ValueError, OSError)):
                bridge.verify_source_epoch(root)

    def reject_manifest(self, root, manifest):
        with self.assertRaises((ValueError, OSError)):
            bridge.validate_runtime_rows(root, manifest, required=True)

    def test_exact338_projection_preserves_actual_binding_and_bytes(self):
        with fresh_root() as root:
            before = snapshot(root)
            result = bridge.verify_source_epoch(root)
            self.assertEqual(result['source_files'], 338)
            self.assertEqual(result['actual_source_manifest_sha256'], bridge.CURRENT_DIGEST)
            self.assertEqual(result['projected_body_policy_epoch'], bridge.TOPCLIP_DIGEST)
            self.assertIs(result['full_package_acceptance'], False)
            projected = bridge._project_sources(self.proof, source_raw(root))
            self.assertEqual(len(projected), 335)
            self.assertEqual(projected, source_inventory(OLD_ROOT))
            self.assertEqual(source_manifest_digest(projected), bridge.TOPCLIP_DIGEST)
            self.assertEqual(read_json(root, bridge.BINDING)['production_source_manifest_sha256'], bridge.CURRENT_DIGEST)
            self.assertEqual(snapshot(root), before)
            self.assertNotIn('private_ground_capture', (root / 'src/render_mirror.c').read_text())
            self.assertFalse((root / 'src/private_ground_capture.inc').exists())
            REPORT['finite_source_result'] = result

    def test_exact1162_preserves1138_rows_eight_aliases_and141_closure(self):
        with fresh_root() as root:
            manifest = read_json(root)
            original = copy.deepcopy(manifest)
            result = bridge.validate_runtime_rows(root, manifest, required=True)
            self.assertEqual(result['runtime_rows'], 1162)
            self.assertEqual(result['old_nonbinding_rows'], 1138)
            self.assertEqual(result['terrain_payloads'], 23)
            self.assertIs(result['old_payloads_revalidated'], False)
            self.assertIs(result['full_package_acceptance'], False)
            base = [r for r in self.old_manifest['files'] if r['source_path'] != bridge.BINDING]
            present = [r for r in manifest['files'] if r['source_path'] != bridge.BINDING
                       and r not in self.expected_rows]
            self.assertEqual(sorted(present, key=lambda r: r['destination']), sorted(base, key=lambda r: r['destination']))
            self.assertTrue(all(r in present for r in self.aliases))
            self.assertEqual(manifest['closure']['global_tank194_body_alias_files'], 8)
            self.assertEqual(manifest['closure']['global_content_hda_files'], 141)
            self.assertEqual(manifest, original)
            REPORT['finite_metadata_and23_result'] = result

    def test_all23_exact_headers_payload_fnv_and_independent_alpha_masks(self):
        with fresh_root() as root:
            actual = terrain.load(root)
            self.assertEqual(len(actual), 23)
            text = (root / 'src/private_cliff_family.inc').read_text()
            mask_text = re.search(r'private_cliff_masks\[12\]\[84\]=(\{.*?\});', text).group(1)
            mask_bytes = bytes(map(int, re.findall(r'\d+', mask_text)))
            self.assertEqual(len(mask_bytes), 1008)
            masks = {tile: mask_bytes[i * 84:(i + 1) * 84]
                     for i, tile in enumerate(self.proof['runtime_groups']['cliff12'])}
            total = 0
            for resource in self.proof['resources']:
                with self.subTest(tile=resource['id']):
                    row = resource['row']; raw = (root / row['source_path']).read_bytes(); payload = raw[28:]
                    self.assertEqual(len(raw), 172060)
                    self.assertEqual(struct.unpack('<4s4I2i', raw[:28]), (b'HDR1', 2010000 + resource['id'], 8, 24, 28, 0, 0))
                    self.assertEqual(digest(raw), row['sha256'])
                    self.assertEqual(digest(payload), resource['payload_sha256'])
                    self.assertEqual(checked.fnv(payload), resource['payload_fnv64'])
                    mask = masks.get(resource['id'])
                    expected_alpha = bytes(255 if mask is None or mask[((y // 8) * 24 + x // 8) // 8] &
                        (1 << (((y // 8) * 24 + x // 8) % 8)) else 0
                        for y in range(224) for x in range(192))
                    self.assertEqual(payload[3::4], expected_alpha)
                    self.assertEqual(expected_alpha.count(255), resource['native_nonzero_cells'] * 64)
                    self.assertTrue(all(payload[i:i + 4] == b'\0\0\0\0'
                                        for i in range(0, len(payload), 4) if payload[i + 3] == 0))
                    total += len(raw)
            self.assertEqual(total, 3957380)
            REPORT['payload_positive'] = {'files': 23, 'bytes': total, 'exact_headers': True,
                                          'payload_fnv': True, 'independent_alpha_masks': True}

    def test_finite_builder_exact_deterministic1162_without_package_claim(self):
        import build_terrain23_registration as builder
        with fresh_root() as root:
            base = root.parent / 'genuine-old1139.json'
            base.write_bytes((OLD_ROOT / MANIFEST).read_bytes())
            before = snapshot(root)
            first, report = builder.build(root, base)
            second, report2 = builder.build(root, base)
            self.assertEqual(first, second)
            self.assertEqual(report, report2)
            self.assertEqual((json.dumps(first, indent=2, sort_keys=True) + '\n').encode(), (root / MANIFEST).read_bytes())
            self.assertIs(report['full_package_acceptance'], False)
            self.assertIs(report['old_payloads_revalidated'], False)
            self.assertEqual(len(first['files']), 1162)
            self.assertEqual(snapshot(root), before)
            base.write_bytes(base.read_bytes() + b'\n')
            with self.assertRaisesRegex(ValueError, 'exact public TOPCLIP1139'):
                builder.build(root, base)

    def test_rows_are_deterministic_and_return_independent_copies(self):
        with fresh_root() as root:
            first = terrain.rows_for(root)
            encoded = json.dumps(first, sort_keys=True, separators=(',', ':'))
            self.assertEqual(encoded, json.dumps(terrain.rows_for(root), sort_keys=True, separators=(',', ':')))
            first[0]['sha256'] = '0' * 64
            self.assertNotEqual(first, terrain.rows_for(root))
            terrain.validate_runtime_rows(root, {'files': self.expected_rows}, required=True)

    def test_mutation_each_new_include_rejected(self):
        for name in terrain.INCLUDES:
            with self.subTest(path=name), fresh_root() as root:
                mutate_byte(root / name)
                self.reject_source(root)

    def test_unrelated_source_and_renderer_changes_rejected(self):
        unrelated = next(name for name in self.proof['source_sha256'] if name not in terrain.INCLUDES
                         and name != 'src/render_mirror.c')
        for name in (unrelated, 'src/render_mirror.c'):
            with self.subTest(path=name), fresh_root() as root:
                mutate_byte(root / name)
                self.reject_source(root)

    def test_deleted_renamed_extra_hidden_capture_sources_rejected(self):
        for kind in ('delete', 'rename', 'extra', 'hidden', 'capture'):
            with self.subTest(kind=kind), fresh_root() as root:
                p = root / terrain.INCLUDES[0]
                if kind == 'delete': p.unlink()
                elif kind == 'rename': p.rename(p.with_suffix('.renamed'))
                else:
                    name = {'extra': 'extra.txt', 'hidden': '.hidden-input', 'capture': 'private_ground_capture.inc'}[kind]
                    (root / 'src' / name).write_bytes(b'/* unauthorized source */\n')
                self.reject_source(root)

    def test_source_symlink_broken_symlink_fifo_and_directory_rejected(self):
        for kind in ('symlink', 'broken-symlink', 'fifo', 'directory', 'source-root-symlink'):
            with self.subTest(kind=kind), fresh_root() as root:
                p = root / terrain.INCLUDES[0]
                if kind == 'source-root-symlink':
                    (root / 'src').rename(root / 'saved-src')
                    (root / 'src').symlink_to(root / 'saved-src', target_is_directory=True)
                else:
                    raw = p.read_bytes(); p.unlink()
                    if kind == 'symlink':
                        target = root / 'same-bytes.inc'; target.write_bytes(raw); p.symlink_to(target)
                    elif kind == 'broken-symlink': p.symlink_to(root / 'absent.inc')
                    elif kind == 'fifo': os.mkfifo(p)
                    else: p.mkdir()
                self.reject_source(root)

    def test_each_build_input_and_historical_receipt_change_rejected(self):
        for name in (*self.proof['source_build_input_sha256'], *self.proof['historical_validation_sha256']):
            with self.subTest(path=name), fresh_root() as root:
                mutate_byte(root / name)
                self.reject_source(root)

    def test_current_receipt_missing_changed_stale_and_newdigest_disagreement_rejected(self):
        for kind in ('missing', 'append', 'old335', 'wrong-digest', 'wrong-production-commit'):
            with self.subTest(kind=kind), fresh_root() as root:
                p = root / bridge.BINDING
                if kind == 'missing': p.unlink()
                elif kind == 'append': p.write_bytes(p.read_bytes() + b'\n')
                elif kind == 'old335': p.write_bytes(self.old_receipt)
                else:
                    receipt = read_json(root, bridge.BINDING)
                    receipt['production_source_manifest_sha256' if kind == 'wrong-digest' else 'production_commit'] = '0' * 64
                    p.write_text(json.dumps(receipt))
                self.reject_source(root)

    def test_proof_missing_changed_and_duplicate_json_rejected(self):
        for kind in ('missing', 'append', 'duplicate-json-key'):
            with self.subTest(kind=kind), fresh_root() as root:
                p = root / terrain.PROOF
                if kind == 'missing': p.unlink()
                elif kind == 'append': p.write_bytes(p.read_bytes() + b'\n')
                else: p.write_bytes(b'{"schema":"x",' + p.read_bytes()[1:])
                self.reject_source(root)

    def test_proof_receipt_build_and_historical_symlinks_rejected(self):
        for name in (terrain.PROOF, bridge.BINDING, *self.proof['source_build_input_sha256'],
                     *self.proof['historical_validation_sha256']):
            with self.subTest(path=name), fresh_root() as root:
                p = root / name; raw = p.read_bytes(); p.unlink()
                target = root / 'same-bytes-target'; target.write_bytes(raw); p.symlink_to(target)
                self.reject_source(root)

    def test_genuine_old335_source_gate_unchanged_and_optional_terrain_absent(self):
        with fresh_root(OLD_ROOT) as root:
            receipt = read_json(root, bridge.BINDING); manifest = read_json(root)
            before = source_inventory(root)
            self.assertEqual(len(before), 335)
            self.assertEqual(source_manifest_digest(before), bridge.TOPCLIP_DIGEST)
            self.assertEqual(verify(root, receipt), 335)
            self.assertFalse(bridge.requires_terrain(root, manifest, receipt))
            self.assertIsNone(bridge.validate_runtime_rows(root, manifest, required=False))
            projected, restored = old_bridge.project_topclip_sources(root)
            self.assertEqual(len(projected), 329); self.assertEqual(len(restored), 18)
            self.assertEqual(source_inventory(root), before)
            REPORT['genuine_old335_gate'] = 'PASS: unchanged original topclip source projection; not old payload acceptance'

    def test_old_topclip_mode_rejects_new338(self):
        with fresh_root() as root:
            with self.assertRaisesRegex(ValueError, 'Unreviewed topclip production epoch'):
                old_bridge.project_topclip_sources(root)

    def test_each_broken_root_marker_forces_terrain(self):
        for name in bridge.ROOT_MARKERS:
            with self.subTest(marker=name), fresh_root(OLD_ROOT) as root:
                (root / name).symlink_to(root / 'absent-marker-target')
                self.assertTrue(bridge.requires_terrain(root, read_json(root), read_json(root, bridge.BINDING)))
                self.reject_manifest(root, read_json(root))

    def test_critical_new338_old335receipt_old1139manifest_downgrade_rejected(self):
        for keep_proof in (True, False):
            with self.subTest(proof_present=keep_proof), fresh_root() as root:
                (root / bridge.BINDING).write_bytes(self.old_receipt)
                (root / MANIFEST).write_bytes((OLD_ROOT / MANIFEST).read_bytes())
                if not keep_proof: (root / terrain.PROOF).unlink()
                manifest = read_json(root); receipt = read_json(root, bridge.BINDING)
                self.assertEqual(len(manifest['files']), 1139)
                self.assertFalse(terrain.marked_rows(manifest))
                self.assertTrue(bridge.requires_terrain(root, manifest, receipt))
                self.reject_manifest(root, manifest)

    def test_unknown_digest_terrain_markers_never_authorize_fallback(self):
        for origin in ('source-revision', 'closure', 'row-revision', 'row-id', 'row-source', 'row-destination', 'current'):
            with self.subTest(marker=origin), fresh_root(OLD_ROOT) as root:
                manifest = copy.deepcopy(self.old_manifest); receipt = read_json(root, bridge.BINDING)
                if origin == 'source-revision': manifest['source_revision']['terrain23_epoch'] = 'unknown'
                elif origin == 'closure': manifest['closure']['terrain23_fake'] = 0
                elif origin == 'row-revision': manifest['files'][0]['revision'] = terrain.MODE
                elif origin == 'row-id': manifest['files'][0]['identity'] = 2010361
                elif origin == 'row-source': manifest['files'][0]['source_path'] = self.expected_rows[0]['source_path']
                elif origin == 'row-destination': manifest['files'][0]['destination'] = self.expected_rows[0]['destination']
                else: receipt['terrain23_binding'] = {}
                self.assertTrue(bridge.requires_terrain(root, manifest, receipt))
                self.reject_manifest(root, manifest)

    def test_old_nonbinding_row_fields_changed_removed_duplicated_rejected(self):
        sample = next(r for r in self.old_manifest['files'] if r['source_path'] != bridge.BINDING)
        for key in (*sample, 'remove-row', 'duplicate-row', 'injected-extra-field'):
            with self.subTest(field=key), fresh_root() as root:
                manifest = read_json(root); row = next(r for r in manifest['files'] if r == sample)
                if key == 'remove-row': manifest['files'].remove(row)
                elif key == 'duplicate-row': manifest['files'].append(copy.deepcopy(row))
                elif key == 'injected-extra-field': row['unexpected'] = 'changed'
                elif key == 'bytes': row[key] += 1
                elif key in ('source_path', 'destination'): row[key] = 'safe-but-wrong/name.bin'
                else: row[key] = 'altered'
                self.reject_manifest(root, manifest)

    def test_each_of_eight_old_aliases_cannot_be_dropped_or_disguised(self):
        for alias in self.aliases:
            for kind in ('remove', 'disguise-preserve-count'):
                with self.subTest(identity=alias['identity'], kind=kind), fresh_root() as root:
                    manifest = read_json(root); row = next(r for r in manifest['files'] if r == alias)
                    if kind == 'remove': manifest['files'].remove(row)
                    else: row.update(revision='concealed-old-alias', identity=0)
                    self.reject_manifest(root, manifest)

    def test_eight141_and_terrain_closures_cannot_change(self):
        for key, value in (('global_tank194_body_alias_files', 2), ('global_tank194_body_alias_files', True),
                           ('global_content_hda_files', 140), ('terrain23_files', 22),
                           ('terrain23_atomic_groups', {'ground10': 9, 'cliff12': 12, 'corner366': 1})):
            with self.subTest(key=key, value=value), fresh_root() as root:
                manifest = read_json(root); manifest['closure'][key] = value
                self.reject_manifest(root, manifest)

    def test_metadata_integer_types_are_exact_not_python_numeric_equality(self):
        cases = [('terrain23_atomic_groups.corner366', True), ('data_frame_files', True),
                 ('data_frame_files', 1.0), ('global_tank194_body_alias_files', 8.0),
                 ('global_content_hda_files', 141.0), ('terrain23_files', 23.0),
                 ('terrain23_atomic_groups.ground10', 10.0)]
        for key, value in cases:
            with self.subTest(key=key, value=value, type=type(value).__name__), fresh_root() as root:
                manifest = read_json(root)
                if '.' in key:
                    first, second = key.split('.')
                    manifest['closure'][first][second] = value
                else:
                    manifest['closure'][key] = value
                self.reject_manifest(root, manifest)

    def test_binding_row_and_top_level_digest_disagreement_rejected(self):
        for kind in ('old-digest', 'unknown-digest', 'old-binding-row', 'binding-sha', 'binding-path', 'duplicate-binding', 'binding-bytes-bool'):
            with self.subTest(kind=kind), fresh_root() as root:
                manifest = read_json(root); row = next(r for r in manifest['files'] if r['source_path'] == bridge.BINDING)
                if kind.endswith('digest'):
                    manifest['source_revision']['current_production_source_manifest_sha256'] = bridge.TOPCLIP_DIGEST if kind == 'old-digest' else '0' * 64
                elif kind == 'old-binding-row': row.update(next(r for r in self.old_manifest['files'] if r['source_path'] == bridge.BINDING))
                elif kind == 'binding-sha': row['sha256'] = '0' * 64
                elif kind == 'binding-path': row['source_path'] = 'packaging/stale-current.json'
                elif kind == 'duplicate-binding': manifest['files'].append(copy.deepcopy(row))
                else: row['bytes'] = True
                self.reject_manifest(root, manifest)

    def test_each23_row_identity_path_hash_revision_change_rejected(self):
        for expected in self.expected_rows:
            for kind in ('identity', 'source_path', 'destination', 'sha256', 'revision'):
                with self.subTest(resource=expected['destination'], field=kind), fresh_root() as root:
                    manifest = read_json(root); row = next(r for r in manifest['files'] if r == expected)
                    row[kind] = {'identity': 2019999, 'source_path': 'assets/hd/wrong.hda',
                                 'destination': 'assets/gameplay/wrong.hda', 'sha256': '0' * 64,
                                 'revision': 'unknown-terrain'}[kind]
                    self.reject_manifest(root, manifest)

    def test_terrain_omitted_duplicate_extra_and_unsafe_rows_rejected(self):
        for kind in ('missing', 'duplicate', 'extra', 'traversal', 'absolute', 'backslash', 'bool-size', 'not-row'):
            with self.subTest(kind=kind), fresh_root() as root:
                manifest = read_json(root); row = next(r for r in manifest['files'] if r in self.expected_rows)
                if kind == 'missing': manifest['files'].remove(row)
                elif kind == 'duplicate': manifest['files'].append(copy.deepcopy(row))
                elif kind == 'extra': manifest['files'].append(dict(row, destination='assets/gameplay/extra.hda'))
                elif kind == 'bool-size': row['bytes'] = True
                elif kind == 'not-row': manifest['files'][0] = None
                else: row['source_path'] = {'traversal': '../outside.hda', 'absolute': '/tmp/outside.hda', 'backslash': 'assets\\wrong.hda'}[kind]
                self.reject_manifest(root, manifest)

    def test_all23_missing_truncated_header_payload_nonregular_rejected(self):
        for row in self.expected_rows:
            for kind in ('missing', 'truncated', 'header', 'payload', 'directory', 'symlink', 'broken-symlink'):
                with self.subTest(resource=row['destination'], corruption=kind), fresh_root() as root:
                    p = root / row['source_path']
                    if kind in ('missing', 'directory', 'symlink', 'broken-symlink'):
                        raw = p.read_bytes(); p.unlink()
                        if kind == 'directory': p.mkdir()
                        elif kind == 'symlink':
                            target = root / 'same-payload.hda'; target.write_bytes(raw); p.symlink_to(target)
                        elif kind == 'broken-symlink': p.symlink_to(root / 'absent-payload.hda')
                    elif kind == 'truncated': p.write_bytes(p.read_bytes()[:-1])
                    else: mutate_byte(p, 4 if kind == 'header' else 28)
                    with self.assertRaises((ValueError, OSError)):
                        terrain.validate_runtime_rows(root, {'files': self.expected_rows}, required=True)

    def test_inverse_helper_memory_only_wrong_missing_duplicate_hunks_rejected(self):
        # Public entrypoints always authenticate the immutable proof. These forged
        # dictionaries never touch disk and test defense of the private helper.
        with fresh_root() as root:
            raw = source_raw(root)
            for kind in ('missing-hunk', 'duplicate-hunk', 'duplicate-preserve-eight', 'unordered-preserve-eight',
                         'overlap-preserve-eight', 'wrong-candidate', 'wrong-position',
                         'wrong-context', 'blank-wrong-position', 'wrong-public', 'wrong-projected335', 'wrong-include-hash'):
                with self.subTest(kind=kind):
                    proof = copy.deepcopy(self.proof); edits = proof['inverse']['inverse_hunks']
                    if kind == 'missing-hunk': edits.pop(0)
                    elif kind == 'duplicate-hunk': edits.insert(1, copy.deepcopy(edits[0]))
                    elif kind == 'duplicate-preserve-eight': edits[1] = copy.deepcopy(edits[0])
                    elif kind == 'unordered-preserve-eight': edits[0], edits[1] = edits[1], edits[0]
                    elif kind == 'overlap-preserve-eight': edits[1]['start_line_zero_based'] = edits[0]['start_line_zero_based']
                    elif kind == 'wrong-candidate': edits[0]['candidate'] = 'wrong source\n'
                    elif kind == 'wrong-position': edits[0]['start_line_zero_based'] += 1
                    elif kind == 'wrong-context': edits[0]['context_before'] = 'wrong context\n'
                    elif kind == 'blank-wrong-position': edits[-1]['start_line_zero_based'] += 1
                    elif kind == 'wrong-public': edits[0]['public'] = 'wrong public\n'
                    elif kind == 'wrong-projected335': proof['projected_source_sha256']['src/render_mirror.c'] = '0' * 64
                    else: proof['include_sha256'][terrain.INCLUDES[0]] = '0' * 64
                    with self.assertRaises(ValueError): bridge._project_sources(proof, raw)
            self.assertEqual(terrain.authority(root), self.proof)

    def test_inverse_helper_memory_only_duplicate_candidate_and_unrelated_change_rejected(self):
        with fresh_root() as root:
            original = source_raw(root)
            for kind in ('duplicate-candidate', 'extra-renderer', 'changed-include', 'missing-include', 'extra-source'):
                with self.subTest(kind=kind):
                    raw = dict(original); proof = copy.deepcopy(self.proof)
                    if kind == 'duplicate-candidate':
                        raw['src/render_mirror.c'] += proof['inverse']['inverse_hunks'][0]['candidate'].encode()
                    elif kind == 'extra-renderer': raw['src/render_mirror.c'] += b'/* unrelated */\n'
                    elif kind == 'changed-include': raw[terrain.INCLUDES[0]] += b'\n'
                    elif kind == 'missing-include': del raw[terrain.INCLUDES[0]]
                    else: raw['src/extra.txt'] = b'extra'
                    proof['inverse']['planned_renderer_sha256'] = digest(raw['src/render_mirror.c'])
                    with self.assertRaises(ValueError): bridge._project_sources(proof, raw)


class Terrain23DefaultPipeline(unittest.TestCase):
    """Honest expected missing-material failure, separate from finite success."""
    def probe(self, script, args, kind, root):
        result = subprocess.run([sys.executable, '-B', str(root / 'scripts' / script), *map(str, args)],
            cwd=root, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, text=True, timeout=90)
        record = {'kind': kind, 'script': script, 'returncode': result.returncode,
                  'stdout': result.stdout, 'stderr': result.stderr, 'full_package_acceptance': False,
                  'copied_script_sha256': digest((root / 'scripts' / script).read_bytes())}
        REPORT['cli_probes'].append(record)
        self.assertNotEqual(result.returncode, 0, 'Sparse private root cannot truthfully fully package')
        text = result.stdout + result.stderr
        missing_import = 'ModuleNotFoundError' in text
        self.assertFalse(missing_import, 'Missing Python dependency is honest blocking, but does not establish the required final old-input/payload failure')
        self.assertNotIn('Unreviewed topclip production epoch', text)
        self.assertNotIn('Unreviewed terrain23', text)
        self.assertTrue(any(word in text for word in ('No such file or directory', 'Missing', 'missing', 'Expected regular selected file', 'ModuleNotFoundError')),
                        'Expected an explicit missing old-material error, got: ' + text[-2000:])
        record['expected_blocked_failure'] = True
        record['blocker_class'] = 'MISSING_PYTHON_DEPENDENCY' if missing_import else 'MISSING_OLD_INPUT_OR_PAYLOAD'
        record['full_old_payload_validation_completed'] = False
        return result

    def test_default_packager_fails_honestly_on_missing_old_material(self):
        with fresh_root() as root:
            self.probe('package_runtime.py', ['--source-root', root], 'default-packager-dry-run', root)

    def test_renamed_manifest_terrain_validation_cannot_be_bypassed(self):
        with fresh_root() as root:
            manifest = read_json(root)
            row = next(r for r in manifest['files'] if r.get('revision') == terrain.MODE)
            row['sha256'] = '0' * 64
            path = root.parent / 'innocent-renamed-manifest.json'; path.write_text(json.dumps(manifest))
            result = subprocess.run([sys.executable, '-B', str(root / 'scripts/package_runtime.py'),
                '--source-root', str(root), '--manifest', str(path)], cwd=root,
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, text=True, timeout=90)
            REPORT['cli_probes'].append({'kind': 'renamed-manifest-bad-terrain-row', 'returncode': result.returncode,
                                        'stdout': result.stdout, 'stderr': result.stderr})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Missing, duplicate or changed terrain23 row', result.stdout + result.stderr)

    def test_default_packager_renamed_old1139manifest_old335receipt_cannot_downgrade338(self):
        with fresh_root() as root:
            (root / bridge.BINDING).write_bytes((OLD_ROOT / bridge.BINDING).read_bytes())
            path = root.parent / 'ordinary-old1139.json'
            path.write_bytes((OLD_ROOT / MANIFEST).read_bytes())
            self.assertFalse(terrain.marked_rows(read_json(OLD_ROOT)))
            result = subprocess.run([sys.executable, '-B', str(root / 'scripts/package_runtime.py'),
                '--source-root', str(root), '--manifest', str(path)], cwd=root,
                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, text=True, timeout=90)
            REPORT['cli_probes'].append({'kind': 'renamed-old1139-downgrade-actual338',
                'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Changed terrain23 actual current receipt', result.stdout + result.stderr)

    def test_default_rebuild_fails_honestly_and_writes_no_candidate(self):
        with fresh_root() as root:
            output = root.parent / 'should-not-exist.json'
            self.probe('rebuild_recovered_runtime_manifest.py', ['--root', root, '--output', output],
                       'default-rebuild', root)
            self.assertFalse(output.exists(), 'Failed rebuild must not leave a candidate manifest')


class RecordingResult(unittest.TextTestResult):
    def addSuccess(self, test):
        REPORT['cases'].append({'test': test.id(), 'status': 'PASS'})
        super().addSuccess(test)
    def addFailure(self, test, err):
        REPORT['cases'].append({'test': test.id(), 'status': 'FAIL', 'detail': self._exc_info_to_string(err, test)})
        super().addFailure(test, err)
    def addError(self, test, err):
        REPORT['cases'].append({'test': test.id(), 'status': 'ERROR', 'detail': self._exc_info_to_string(err, test)})
        super().addError(test, err)
    def addSubTest(self, test, subtest, err):
        REPORT['cases'].append({'test': subtest.id(), 'status': 'PASS' if err is None else 'FAIL',
                                **({'detail': self._exc_info_to_string(err, test)} if err else {})})
        super().addSubTest(test, subtest, err)


if __name__ == '__main__':
    started = time.monotonic()
    program = unittest.main(verbosity=2, exit=False,
        testRunner=unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult))
    result = program.result
    REPORT.update(tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                  elapsed_seconds=round(time.monotonic() - started, 3),
                  targeted_tests_passed=result.wasSuccessful(),
                  source_root=str(ROOT), old_source_root=str(OLD_ROOT),
                  proof_sha256=terrain.PROOF_SHA256, loaded_code_sha256=LOADED_CODE_SHA256,
                  python_version=sys.version,
                  code_sha256={p.name: digest(p.read_bytes()) for p in [Path(__file__),
                      ROOT / 'scripts/current_terrain23_source_bridge.py',
                      ROOT / 'scripts/current_terrain23_registration.py',
                      ROOT / 'scripts/package_runtime.py',
                      ROOT / 'scripts/rebuild_recovered_runtime_manifest.py']})
    if os.environ.get('TERRAIN23_REPORT_DIR'):
        directory = Path(os.environ['TERRAIN23_REPORT_DIR']); directory.mkdir(parents=True, exist_ok=True)
        (directory / 'registration-test-results.json').write_text(json.dumps(REPORT, indent=2, sort_keys=True) + '\n')
    sys.exit(0 if result.wasSuccessful() else 1)
