#!/usr/bin/env python3
"""Independent Shield22 authoring checks; synthetic pixels are diagnostic only."""
import copy
import json
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_current_art as b
from current_art_policy import PROFILES, profile

# Spell out consumer identities independently of production policy and registry.
SLOTS = (229,230,231,232,233,234,235,236,237,248,249,250,252,253,254,255,256,267,268,269,272,275)
IDS = (1060229,1060230,1060231,1060232,1060233,1060234,1060235,1060236,1060237,
       1060248,1060249,1060250,1060252,1060253,1060254,1060255,1060256,
       1060267,1060268,1060269,1060272,1060275)
EMPTY = (1060251,1060270,1060271,1060273,1060274)


def png(value, alpha=255):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    rows = (b'\0' + bytes((value,0,0,alpha))*96)*112
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB',96,112,8,6,0,0,0))
            + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))


class CurrentShieldAuthoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='shield-independent-')
        cls.base = Path(cls.temp.name)
        cls.root = cls.base / 'repo'
        names = set(b.BUILD_INPUTS)
        for manifest in ('packaging/runtime-assets-v1.json', 'packaging/runtime-assets-public63a89b3.json'):
            names.update(r['source_path'] for r in json.loads((ROOT / manifest).read_text())['files'])
        for folder in ('src','scripts','packaging','assets/hd/authoring'):
            names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / folder).rglob('*')
                         if p.is_file() and '__pycache__' not in p.parts)
        for family in PROFILES:
            names.update(r['source_png'] for r in json.loads((ROOT / profile(family)['selection']).read_text())['resources'])
        import current_hud_recipe
        hud = json.loads((ROOT / 'assets/hd/authoring/hud/current.json').read_text())
        names.update(r['path'] for rows in hud['resources'].values() for r in rows)
        names.update(r['path'] for r in current_hud_recipe.FIXED_INPUTS.values())
        cls.initial = {name: (ROOT / name).read_bytes() for name in names}
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

    def selected(self):
        return json.loads((self.root / profile('shield')['selection']).read_text())

    def registry(self):
        return json.loads((self.root / b.REGISTRY).read_text())

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): b.sha(p.read_bytes())
                for p in self.root.rglob('*') if p.is_file()}

    def synthetic(self, same=False):
        selected = self.selected()
        selected['version'] = 'independent-shield-v2'
        for index, row in enumerate(selected['resources']):
            name = f'assets/hd/authoring/independent-fixtures/shield-{index}.png'
            raw = png(91 if same else 10+index, 0 if same or row['identity']==1060268 else 255)
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
            row.update(source_png=name, source_sha256=b.sha(raw))
        return selected

    def stage(self, selected):
        self.sequence += 1
        draft = self.base / f'draft-{self.counter}-{self.sequence}.json'
        draft.write_bytes(b.encoded(selected))
        stage = self.base / f'stage-{self.counter}-{self.sequence}'
        b.stage(self.root, draft, stage, 'shield')
        return stage

    def apply(self, selected):
        b.apply(self.root, self.stage(selected), 'shield')

    def test_exact_approved_scope_transparency_and_current_checks(self):
        self.assertEqual(PROFILES['shield']['ids'], IDS)
        selected = self.selected()
        self.assertEqual(tuple(r['identity'] for r in selected['resources']), IDS)
        registry = {r['identity']: r for r in self.registry()['resources']}
        self.assertTrue(set(EMPTY).isdisjoint(registry))
        payloads = {}
        for row in selected['resources']:
            data, payload = b.source_blob(self.root, row)
            payloads[row['identity']] = payload
            self.assertEqual(data, (self.root / 'assets/hd/global-assets-v1' / registry[row['identity']]['path']).read_bytes())
            self.assertEqual(struct.unpack('<6I', data[4:28]), (row['identity'],8,12,14,0,0))
        self.assertFalse(any(payloads[1060268][3::4]))
        self.assertTrue(any(payloads[1060267][3::4]))
        self.assertTrue(any(payloads[1060269][3::4]))
        for family in PROFILES:
            self.assertEqual(b.check(self.root, family)['status'], 'PASS')

    def test_all_22_propagate_preserving_authority_history_and_other_profiles(self):
        before = self.registry()
        self.apply(self.synthetic())
        after = self.registry()
        self.assertEqual(before['families'], after['families'])
        self.assertEqual([r for r in before['resources'] if r['identity'] not in IDS],
                         [r for r in after['resources'] if r['identity'] not in IDS])
        resources = {r['identity']: r for r in after['resources']}
        mapping = json.loads((self.root / profile('shield')['mapping']).read_text())
        self.assertEqual(tuple(r['identity'] for r in mapping['files']), IDS)
        runtime = json.loads((self.root / b.RUNTIME).read_text())['files']
        for index, (identity, slot) in enumerate(zip(IDS, SLOTS)):
            alpha = 0 if identity == 1060268 else 255
            expected = b'HDR1' + struct.pack('<6I',identity,8,12,14,0,0) + bytes((10+index,0,0,alpha))*(96*112)
            resource = resources[identity]
            self.assertEqual((self.root / 'assets/hd/global-assets-v1' / resource['path']).read_bytes(), expected)
            consumer = mapping['files'][index]
            name = f'explosion-newsh6-{slot}-8.hda'
            self.assertEqual(consumer['source_path'], f'assets/hd/current-compat/shield/{name}')
            self.assertEqual(consumer['destination'], f'assets/gameplay/{name}')
            self.assertEqual((self.root / consumer['source_path']).read_bytes(), expected)
            legacy = [r for r in runtime if r['destination'] == consumer['destination']]
            self.assertEqual(len(legacy), 1)
            self.assertEqual(legacy[0]['source_path'], consumer['source_path'])
            self.assertEqual(legacy[0]['sha256'], b.sha(expected))
            global_rows = [r for r in runtime if r['destination'] == 'assets/global/' + resource['path']]
            self.assertEqual(len(global_rows), 1)
            self.assertEqual(global_rows[0]['sha256'], b.sha(expected))
            self.assertIn(resource['payload_fnv64'], (self.root / b.HEADER).read_text())
        self.assertEqual((self.root / b.LEGACY_HEADER).read_bytes(), self.initial[b.LEGACY_HEADER])
        for family in PROFILES:
            self.assertEqual(b.check(self.root, family)['status'], 'PASS')
        import build_current_hud
        self.assertEqual(build_current_hud.check(self.root)['status'], 'PASS')
        for name, data in self.initial.items():
            if name.startswith(('assets/hd/packs/','assets/hd/artwork/')) or name == 'packaging/runtime-assets-public63a89b3.json':
                self.assertEqual((self.root / name).read_bytes(), data)

    def test_same_transparent_pixels_keep_all_semantic_identities(self):
        self.apply(self.synthetic(same=True))
        rows = [r for r in self.registry()['resources'] if r['identity'] in IDS]
        self.assertEqual(len({r['payload_fnv64'] for r in rows}), 1)
        self.assertEqual(len({r['path'] for r in rows}), 22)
        self.assertEqual(len({r['sha256'] for r in rows}), 22)
        for r in rows:
            data = (self.root / 'assets/hd/global-assets-v1' / r['path']).read_bytes()
            self.assertEqual(struct.unpack('<6I', data[4:28]), (r['identity'],8,12,14,0,0))
        self.assertEqual(b.check(self.root, 'shield')['status'], 'PASS')

    def test_opaque_268_rejected_without_writes_even_with_valid_hash(self):
        selected = self.synthetic()
        row = next(r for r in selected['resources'] if r['identity']==1060268)
        for alpha in (1,255):
            raw = png(80, alpha)
            (self.root / row['source_png']).write_bytes(raw)
            row['source_sha256'] = b.sha(raw)
            before = self.snapshot()
            with self.subTest(alpha=alpha), self.assertRaises(ValueError):
                b.derive(self.root, b.encoded(selected), 'shield')
            self.assertEqual(self.snapshot(), before)

    def test_scope_mutations_and_native_empty_phases_rejected(self):
        for kind in ('missing','reordered','duplicate','bool','extra',*EMPTY):
            selected = self.selected()
            rows = selected['resources']
            if kind == 'missing': rows.pop()
            elif kind == 'reordered': rows[0], rows[1] = rows[1], rows[0]
            elif kind == 'duplicate': rows[0]['identity'] = rows[1]['identity']
            elif kind == 'bool': rows[0]['identity'] = True
            elif kind == 'extra': rows.append(copy.deepcopy(rows[-1]))
            else: rows[0]['identity'] = kind
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                b.derive(self.root, b.encoded(selected), 'shield')

    def test_authority_and_cross_family_provenance_rejected(self):
        for kind in ('geometry','role','empty','transparent','provenance'):
            registry = self.registry()
            family = next(f for f in registry['families'] if f['name']=='player-shield-hit')
            if kind == 'geometry': next(r for r in registry['resources'] if r['identity']==IDS[0])['header_u32'][4] = 1
            elif kind == 'role': family['draw_semantics']['role'] = 'other'
            elif kind == 'empty': family['draw_semantics']['empty_original_indices'].remove(251)
            elif kind == 'transparent': family['draw_semantics']['authored_transparent_indices'] = []
            else: next(r for r in registry['resources'] if r['identity']==80067)['provenance'] = {'invented':'not-approved'}
            (self.root / b.REGISTRY).write_bytes(b.encoded(registry))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                b.derive(self.root, b.encoded(self.selected()), 'shield')
            (self.root / b.REGISTRY).write_bytes(self.initial[b.REGISTRY])

    def test_bad_source_hash_and_path_rejected(self):
        for key, value in (('source_sha256','0'*64),('source_png','../outside.png')):
            selected = self.selected()
            selected['resources'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                b.derive(self.root, b.encoded(selected), 'shield')
        with self.assertRaises(ValueError):
            b.stage(self.root, self.root / profile('shield')['selection'], self.root / 'forbidden', 'shield')

    def test_stage_tampering_stale_source_and_late_collision_no_partial_writes(self):
        selected = self.synthetic()
        before = self.snapshot()
        stage = self.stage(selected)
        self.assertEqual(self.snapshot(), before)
        with self.assertRaises(ValueError): b.apply(self.root, stage, 'hitflare')
        mapping = stage / 'files' / profile('shield')['mapping']
        saved = mapping.read_bytes()
        mapping.write_bytes(saved + b' ')
        with self.assertRaises(ValueError): b.apply(self.root, stage, 'shield')
        self.assertEqual(self.snapshot(), before)
        mapping.write_bytes(saved)
        source = self.root / selected['resources'][0]['source_png']
        saved_source = source.read_bytes()
        source.write_bytes(png(99))
        stale = self.snapshot()
        with self.assertRaises(ValueError): b.apply(self.root, stage, 'shield')
        self.assertEqual(self.snapshot(), stale)
        source.write_bytes(saved_source)
        plan = json.loads((stage / 'plan.json').read_text())
        collision = self.root / (plan['files'][-1]['path'] + '.pulse-tmp')
        collision.parent.mkdir(parents=True, exist_ok=True)
        collision.write_bytes(b'occupied')
        occupied = self.snapshot()
        with self.assertRaises(ValueError): b.apply(self.root, stage, 'shield')
        self.assertEqual(self.snapshot(), occupied)

    def test_version_only_change_and_cross_profile_drift_detection(self):
        selected = self.synthetic()
        self.apply(selected)
        before = self.registry()
        selected['version'] = 'shield-version-only-v3'
        self.apply(selected)
        after = self.registry()
        for old, new in zip(before['resources'], after['resources']):
            for key in ('identity','path','sha256','payload_fnv64','header_u32'):
                self.assertEqual(old[key], new[key])
        installed = self.root / profile('shield')['selection']
        selected['version'] = 'unapplied-drift'
        installed.write_bytes(b.encoded(selected))
        for family in PROFILES:
            with self.subTest(family=family), self.assertRaises(ValueError):
                b.check(self.root, family)


if __name__ == '__main__':
    unittest.main()
