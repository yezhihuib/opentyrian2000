#!/usr/bin/env python3
"""Independent adversarial coverage for 33 semantic cash/gem authoring targets.

Synthetic solid-color PNGs are diagnostic fixtures, not edits of approved art.
"""
import copy
import json
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_current_art as b
from current_art_policy import PROFILES, profile
from test_current_vulcan_authoring import synthetic_png

# Independent expected semantic scope and legacy consumer slots, not inferred
# from the production helper being tested.
EXPECTED = {
    'cash25': ((1120007,1120008,1120009,1120010,1120011,1120012,1130185), 'coin25', (7,8,9,10,11,12,185)),
    'cash50': ((1160026,1160027,1160028,1160029,1160030,1160031,1170204), 'coin50', (26,27,28,29,30,31,204)),
    'cash75': ((1140020,1140021,1140022,1140023,1140024,1140025,1150223), 'coin75', (20,21,22,23,24,25,223)),
    'gem100': ((1180032,1180033,1180034,1180035,1180036,1190169), 'gem100', (32,33,34,35,36,169)),
    'gem250': ((1200014,1200015,1200016,1200017,1200018,1210188), 'gem250', (14,15,16,17,18,188)),
}

class CurrentCashGemAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='cash-gem-independent-')
        cls.base = Path(cls.temp.name)
        cls.root = cls.base / 'repo'
        names = set(b.BUILD_INPUTS)
        for manifest in ('packaging/runtime-assets-v1.json', 'packaging/runtime-assets-public63a89b3.json'):
            names.update(r['source_path'] for r in json.loads((ROOT / manifest).read_text())['files'])
        for folder in ('src', 'scripts', 'packaging', 'assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        for family in PROFILES:
            names.update(r['source_png'] for r in json.loads((ROOT / profile(family)['selection']).read_text())['resources'])
        cls.initial = {n: (ROOT / n).read_bytes() for n in names}
        cls.counter = 0

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        if self.root.exists():
            shutil.rmtree(self.root)
        for name, data in self.initial.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        self.__class__.counter += 1
        self.sequence = 0

    def selected(self, family):
        return json.loads((self.root / profile(family)['selection']).read_text())

    def synthetic(self, family, same=False):
        selected = self.selected(family)
        selected['version'] = 'independent-synthetic-v2'
        for index, row in enumerate(selected['resources']):
            name = f'assets/hd/authoring/independent-fixtures/{family}-{index}.png'
            raw = synthetic_png(91 if same else 10 + index)
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
            row.update(source_png=name, source_sha256=b.sha(raw))
        return selected

    def stage(self, family, selected):
        self.sequence += 1
        draft = self.base / f'draft-{self.counter}-{self.sequence}.json'
        draft.write_bytes(b.encoded(selected))
        stage = self.base / f'stage-{self.counter}-{self.sequence}'
        b.stage(self.root, draft, stage, family)
        return stage

    def apply(self, family, selected):
        stage = self.stage(family, selected)
        b.apply(self.root, stage, family)

    def registry(self):
        return json.loads((self.root / b.REGISTRY).read_text())

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): b.sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}

    def test_approved_sources_and_all_seven_checks(self):
        self.assertEqual(sum(len(e[0]) for e in EXPECTED.values()), 33)
        registry = {r['identity']: r for r in self.registry()['resources']}
        for family, (ids, _, _) in EXPECTED.items():
            self.assertEqual(PROFILES[family]['ids'], ids)
            for row in self.selected(family)['resources']:
                data, _ = b.source_blob(self.root, row)
                self.assertEqual(data, (self.root / 'assets/hd/global-assets-v1' / registry[row['identity']]['path']).read_bytes())
        for family in PROFILES:
            self.assertEqual(b.check(self.root, family)['status'], 'PASS')

    def test_all_33_targets_propagate_and_other_families_stay_current(self):
        for family, (ids, stem, slots) in EXPECTED.items():
            with self.subTest(family=family):
                old = self.registry()
                self.apply(family, self.synthetic(family))
                new = self.registry()
                self.assertEqual(old['families'], new['families'])
                self.assertEqual([r for r in old['resources'] if r['identity'] not in ids], [r for r in new['resources'] if r['identity'] not in ids])
                resources = {r['identity']: r for r in new['resources']}
                mapping = json.loads((self.root / profile(family)['mapping']).read_text())
                runtime = json.loads((self.root / b.RUNTIME).read_text())
                for index, identity in enumerate(ids):
                    role = 'value-newsh6' if index == len(ids)-1 else 'bank11'
                    name = f'{stem}-{role}-{slots[index]}-8.hda'
                    expected = b'HDR1' + struct.pack('<6I',identity,8,12,14,0,0) + bytes([10+index,0,0,255])*(96*112)
                    resource = resources[identity]
                    self.assertEqual((self.root / 'assets/hd/global-assets-v1' / resource['path']).read_bytes(), expected)
                    consumer = next(r for r in mapping['files'] if r['identity'] == identity)
                    self.assertEqual(consumer['source_path'], f'assets/hd/current-compat/{family}/{name}')
                    self.assertEqual(consumer['destination'], f'assets/gameplay/{name}')
                    self.assertEqual((self.root / consumer['source_path']).read_bytes(), expected)
                    row = next(r for r in runtime['files'] if r['destination'] == consumer['destination'])
                    self.assertEqual(row['source_path'], consumer['source_path'])
                    self.assertEqual(row['sha256'], b.sha(expected))
                    self.assertIn(f'CURRENT_{family.upper()}_{identity}_RGBA UINT64_C(0x{b.fnv(expected[28:])})', (self.root / b.LEGACY_HEADER).read_text())
                    self.assertIn(resource['payload_fnv64'], (self.root / b.HEADER).read_text())
                for other in PROFILES:
                    self.assertEqual(b.check(self.root, other)['status'], 'PASS')
        for name, data in self.initial.items():
            if name.startswith(('assets/hd/packs/', 'assets/hd/artwork/')) or name == 'packaging/runtime-assets-public63a89b3.json':
                self.assertEqual((self.root / name).read_bytes(), data)

    def test_same_pixels_do_not_merge_semantic_identities(self):
        for family in EXPECTED:
            self.apply(family, self.synthetic(family, same=True))
        rows = [r for r in self.registry()['resources'] if r['identity'] in {i for e in EXPECTED.values() for i in e[0]}]
        self.assertEqual(len({r['payload_fnv64'] for r in rows}), 1)
        self.assertEqual(len({r['path'] for r in rows}), 33)
        self.assertEqual(len({r['sha256'] for r in rows}), 33)
        for r in rows:
            data = (self.root / 'assets/hd/global-assets-v1' / r['path']).read_bytes()
            self.assertEqual(struct.unpack('<6I', data[4:28]), (r['identity'],8,12,14,0,0))
        for family in PROFILES:
            self.assertEqual(b.check(self.root, family)['status'], 'PASS')

    def test_version_only_change_preserves_pixels_and_other_families(self):
        for family in EXPECTED:
            selected = self.synthetic(family)
            self.apply(family, selected)
            old = self.registry()
            selected['version'] = 'renamed-only-v3'
            self.apply(family, selected)
            new = self.registry()
            for before, after in zip(old['resources'], new['resources']):
                for key in ('identity','path','sha256','payload_fnv64','header_u32'):
                    self.assertEqual(before[key], after[key])
            for other in PROFILES:
                self.assertEqual(b.check(self.root, other)['status'], 'PASS')

    def test_cross_family_provenance_rejected(self):
        for target in EXPECTED:
            for victim in EXPECTED:
                registry = self.registry()
                next(r for r in registry['resources'] if r['identity'] == EXPECTED[victim][0][0])['provenance'] = {'invented': 'not-approved'}
                (self.root / b.REGISTRY).write_bytes(b.encoded(registry))
                with self.subTest(target=target, victim=victim), self.assertRaises(ValueError):
                    b.derive(self.root, b.encoded(self.selected(target)), target)
                (self.root / b.REGISTRY).write_bytes(self.initial[b.REGISTRY])

    def test_cross_family_version_drift_rejected(self):
        self.apply('gem250', self.synthetic('gem250'))
        selected = self.selected('gem250')
        selected['version'] = 'installed-manifest-was-edited-without-apply'
        (self.root / profile('gem250')['selection']).write_bytes(b.encoded(selected))
        for family in EXPECTED:
            with self.subTest(family=family), self.assertRaises(ValueError):
                b.check(self.root, family)

    def test_every_family_duplicate_or_wrong_identity_rejected(self):
        for family in EXPECTED:
            for kind in ('duplicate','bool','cross-family'):
                selected = self.selected(family)
                selected['resources'][0]['identity'] = {'duplicate': selected['resources'][1]['identity'], 'bool': True, 'cross-family': 80067}[kind]
                with self.subTest(family=family, kind=kind), self.assertRaises(ValueError):
                    b.derive(self.root, b.encoded(selected), family)

    def test_every_family_bad_source_hash_and_traversal_rejected(self):
        for family in EXPECTED:
            for key, value in (('source_sha256','0'*64),('source_png','../outside.png')):
                selected = self.selected(family)
                selected['resources'][0][key] = value
                with self.subTest(family=family, key=key), self.assertRaises(ValueError):
                    b.derive(self.root, b.encoded(selected), family)

    def test_all_families_late_collision_preflights_without_partial_writes(self):
        for family in EXPECTED:
            stage = self.stage(family, self.synthetic(family))
            plan = json.loads((stage / 'plan.json').read_text())
            collision = self.root / (plan['files'][-1]['path'] + '.pulse-tmp')
            collision.parent.mkdir(parents=True, exist_ok=True)
            collision.write_bytes(b'occupied')
            before = self.snapshot()
            with self.subTest(family=family), self.assertRaises(ValueError):
                b.apply(self.root, stage, family)
            self.assertEqual(before, self.snapshot())
            collision.unlink()

    def test_stage_is_nonmutating_and_rejects_wrong_family_or_tampering(self):
        selected = self.synthetic('cash50')
        before = self.snapshot()
        stage = self.stage('cash50', selected)
        self.assertEqual(before, self.snapshot())
        with self.assertRaises(ValueError):
            b.apply(self.root, stage, 'cash75')
        p = stage / 'files' / profile('cash50')['mapping']
        p.write_bytes(p.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            b.apply(self.root, stage, 'cash50')
        self.assertEqual(before, self.snapshot())

    def test_cash_gem_stage_path_and_source_symlinks_rejected(self):
        for family in EXPECTED:
            with self.subTest(family=family), self.assertRaises(ValueError):
                b.stage(self.root, self.root / profile(family)['selection'], self.root / f'forbidden-{family}', family)
        selected = self.selected('gem100')
        p = self.root / selected['resources'][0]['source_png']
        target = self.base / 'source-symlink.png'
        target.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(target)
        with self.assertRaises(ValueError):
            b.derive(self.root, b.encoded(selected), 'gem100')

    def test_fixed_geometry_and_source_bank_authority_rejected(self):
        for family, (ids, _, _) in EXPECTED.items():
            registry = self.registry()
            next(r for r in registry['resources'] if r['identity'] == ids[0])['header_u32'][4] = 1
            (self.root / b.REGISTRY).write_bytes(b.encoded(registry))
            with self.subTest(family=family), self.assertRaises(ValueError):
                b.derive(self.root, b.encoded(self.selected(family)), family)
            (self.root / b.REGISTRY).write_bytes(self.initial[b.REGISTRY])
        registry = self.registry()
        registry['families'][2]['source_identity']['bank_bytes'] += 1
        (self.root / b.REGISTRY).write_bytes(b.encoded(registry))
        with self.assertRaises(ValueError):
            b.derive(self.root, b.encoded(self.selected('cash25')), 'cash25')

if __name__ == '__main__':
    unittest.main()
