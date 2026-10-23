#!/usr/bin/env python3
"""Independent adversarial coverage for 26 semantic effect authoring targets.

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
    'hitflare': ((1060146,1060147,1060148,1060149,1060150,1060151,1060152), 'explosion-newsh6', (146,147,148,149,150,151,152)),
    'white_smoke': ((1060135,1060136,1060137,1060138,1060139,1060140,1060141), 'explosion-newsh6', (135,136,137,138,139,140,141)),
    'small_explosion': ((1060122,1060123,1060124,1060125,1060126,1060127,1060128,1060129,1060130,1060131,1060132,1060133), 'explosion-newsh6', (122,123,124,125,126,127,128,129,130,131,132,133)),
}

class CurrentEffectsAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='effects-independent-')
        cls.base = Path(cls.temp.name)
        cls.root = cls.base / 'repo'
        names = set(b.BUILD_INPUTS)
        from current_sidekick_body_compatibility import independent_input_paths
        names.update(independent_input_paths(ROOT))
        for manifest in ('packaging/runtime-assets-v1.json', 'packaging/runtime-assets-public63a89b3.json'):
            names.update(r['source_path'] for r in json.loads((ROOT / manifest).read_text())['files'])
        for folder in ('src', 'scripts', 'packaging', 'assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
        for family in PROFILES:
            names.update(r['source_png'] for r in json.loads((ROOT / profile(family)['selection']).read_text())['resources'])
        import current_hud_recipe
        hud_selected = json.loads((ROOT / 'assets/hd/authoring/hud/current.json').read_text())
        names.update(r['path'] for rows in hud_selected['resources'].values() for r in rows)
        names.update(r['path'] for r in current_hud_recipe.FIXED_INPUTS.values())
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

    def test_approved_sources_and_all_current_checks(self):
        self.assertEqual(sum(len(e[0]) for e in EXPECTED.values()), 26)
        registry = {r['identity']: r for r in self.registry()['resources']}
        for family, (ids, _, _) in EXPECTED.items():
            self.assertEqual(PROFILES[family]['ids'], ids)
            for row in self.selected(family)['resources']:
                data, _ = b.source_blob(self.root, row)
                self.assertEqual(data, (self.root / 'assets/hd/global-assets-v1' / registry[row['identity']]['path']).read_bytes())
        for family in PROFILES:
            self.assertEqual(b.check(self.root, family)['status'], 'PASS')

    def test_all_26_targets_propagate_and_other_families_stay_current(self):
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
                    name = f'{stem}-{slots[index]}-8.hda'
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
                    global_row = next(r for r in runtime['files'] if r['destination'] == 'assets/global/' + resource['path'])
                    self.assertEqual(global_row['source_path'], 'assets/hd/global-assets-v1/' + resource['path'])
                    self.assertEqual(global_row['sha256'], b.sha(expected))
                    self.assertEqual((self.root / b.LEGACY_HEADER).read_bytes(), self.initial[b.LEGACY_HEADER])
                    self.assertIn(resource['payload_fnv64'], (self.root / b.HEADER).read_text())
                for other in PROFILES:
                    self.assertEqual(b.check(self.root, other)['status'], 'PASS')
        import build_current_hud
        self.assertEqual(build_current_hud.check(self.root)['status'], 'PASS')
        for name, data in self.initial.items():
            if name.startswith(('assets/hd/packs/', 'assets/hd/artwork/')) or name == 'packaging/runtime-assets-public63a89b3.json':
                self.assertEqual((self.root / name).read_bytes(), data)

    def test_same_pixels_do_not_merge_semantic_identities(self):
        for family in EXPECTED:
            self.apply(family, self.synthetic(family, same=True))
        rows = [r for r in self.registry()['resources'] if r['identity'] in {i for e in EXPECTED.values() for i in e[0]}]
        self.assertEqual(len({r['payload_fnv64'] for r in rows}), 1)
        self.assertEqual(len({r['path'] for r in rows}), 26)
        self.assertEqual(len({r['sha256'] for r in rows}), 26)
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
        self.apply('small_explosion', self.synthetic('small_explosion'))
        selected = self.selected('small_explosion')
        selected['version'] = 'installed-manifest-was-edited-without-apply'
        (self.root / profile('small_explosion')['selection']).write_bytes(b.encoded(selected))
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
        selected = self.synthetic('hitflare')
        before = self.snapshot()
        stage = self.stage('hitflare', selected)
        self.assertEqual(before, self.snapshot())
        with self.assertRaises(ValueError):
            b.apply(self.root, stage, 'white_smoke')
        p = stage / 'files' / profile('hitflare')['mapping']
        p.write_bytes(p.read_bytes() + b' ')
        with self.assertRaises(ValueError):
            b.apply(self.root, stage, 'hitflare')
        self.assertEqual(before, self.snapshot())

    def test_effects_stage_path_and_source_symlinks_rejected(self):
        for family in EXPECTED:
            with self.subTest(family=family), self.assertRaises(ValueError):
                b.stage(self.root, self.root / profile(family)['selection'], self.root / f'forbidden-{family}', family)
        selected = self.selected('white_smoke')
        p = self.root / selected['resources'][0]['source_png']
        target = self.base / 'source-symlink.png'
        target.write_bytes(p.read_bytes())
        p.unlink()
        p.symlink_to(target)
        with self.assertRaises(ValueError):
            b.derive(self.root, b.encoded(selected), 'white_smoke')

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
            b.derive(self.root, b.encoded(self.selected('hitflare')), 'hitflare')

if __name__ == '__main__':
    unittest.main()
