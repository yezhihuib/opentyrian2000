"""Read-only authoring navigation; synthetic negatives never edit real inputs."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import shared_asset_authoring_map as authoring
import current_enemy_orb_compatibility as orb


class AuthoringMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = authoring.build_map(ROOT)
        cls.rows = cls.result['resources']

    def rows_for(self, ids):
        return [r for r in self.rows if r['identity'] in ids]

    def test_charge_one_master_nine_outputs_not_nine_inputs(self):
        rows = self.rows_for({1450000 + i for i in (258,259,260,277,278,279,296,297,298)})
        self.assertEqual(len(rows), 9)
        inputs = {p for r in rows for p in r['editable_inputs']}
        self.assertEqual(inputs, {'authoring-inputs/charge-body-current/master.png'})
        self.assertTrue(all(r['recipe'] for r in rows))
        self.assertTrue(all('/derived/' not in p for p in inputs))

    def test_plasma_one_master_three_roles_two_densities(self):
        rows = [r for r in self.rows if r['family'] == 'plasma-projectile']
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({r['identity'] for r in rows}), 3)
        self.assertEqual({r['density'] for r in rows}, {4, 8})
        self.assertEqual(len({p for r in rows for p in r['editable_inputs']}), 1)
        self.assertEqual(len({(r['identity'], r['density']) for r in rows}), 6)

    def test_orb_two_independent_masters_four_contracts(self):
        rows = self.rows_for({80112,80113,1420112,1420113})
        self.assertEqual(len(rows), 4)
        by_id = {r['identity']: r for r in rows}
        self.assertEqual(by_id[80112]['editable_inputs'], by_id[1420112]['editable_inputs'])
        self.assertEqual(by_id[80113]['editable_inputs'], by_id[1420113]['editable_inputs'])
        self.assertNotEqual(by_id[80112]['editable_inputs'], by_id[80113]['editable_inputs'])
        self.assertNotEqual(by_id[80112]['role'], by_id[1420112]['role'])
        self.assertTrue(all(r['declared_consumers'] for r in rows))

    def test_front_eight_independent_current_pngs(self):
        rows = self.rows_for({80121,80122,80163,80164,80201,80202,80279,80280})
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({p for r in rows for p in r['editable_inputs']}), 8)
        self.assertTrue(all(r['status'] == 'current-editable' for r in rows))
        self.assertFalse(any(r['identity'] in (1310182,1310183) and r['status'] == 'current-editable' for r in self.rows))

    def test_newshf_nine_normalized_inputs_not_three_raw_masters(self):
        rows = self.rows_for(set(range(2100000,2100009)))
        self.assertEqual(len(rows), 9)
        inputs = {p for r in rows for p in r['source_inputs']}
        self.assertEqual(len(inputs), 9)
        frozen = [r for r in rows if r['status'] == 'frozen-reproducer']
        editable = [r for r in rows if r['editable_inputs']]
        self.assertEqual(len(frozen), 3)
        self.assertTrue(all(not r['editable_inputs'] for r in frozen))
        self.assertEqual(len(editable), 6)
        self.assertEqual(len({p for r in editable for p in r['editable_inputs']}), 6)
        self.assertTrue(all(p.startswith('authoring-inputs/enemies/newshf-phase-a/') and p.endswith('.png') for p in inputs))

    def test_protron_one_current_master_four_distinct_contracts(self):
        rows = self.rows_for({80225,80226,80244,1470227})
        self.assertEqual(len(rows), 4)
        master = 'authoring-inputs/protron-current/master.png'
        self.assertTrue(all(r['status'] == 'current-editable' for r in rows))
        self.assertTrue(all(r['editable_inputs'] == [master] and r['source_inputs'] == [master] for r in rows))
        self.assertEqual({r['role'] for r in rows}, {8,147})
        self.assertTrue(all(r['density'] == 8 for r in rows))
        self.assertTrue(all('authoring-inputs/protron-current/recipe.json' in r['recipe'] for r in rows))
        self.assertEqual(len({p for r in rows for p in r['derived_outputs'] if p.endswith('.hda')}), 4)
        frozen = 'assets/hd/artwork/player-protron-three-v1/'
        self.assertFalse(any(p.startswith(frozen) for r in self.rows for p in r['editable_inputs']))
        by_id = {r['identity']: r for r in rows}
        self.assertNotEqual(by_id[80244]['role'], by_id[1470227]['role'])
        for identity in (80226,80244,1470227):
            self.assertTrue(any(c['role'] == 146 and c['material_identity'] == identity
                                and c['evidence'] == 'src/enemy_reuse_mirror.inc'
                                for c in by_id[identity]['declared_consumers']))

    def test_sonic_two_current_masters_four_mirror_contracts(self):
        rows = self.rows_for({80105,80106,80124,80125})
        self.assertEqual(len(rows),4)
        by_id = {r['identity']:r for r in rows}
        for first, mirrored in ((80105,80106),(80124,80125)):
            self.assertEqual(by_id[first]['editable_inputs'],by_id[mirrored]['editable_inputs'])
            self.assertEqual(by_id[first]['editable_inputs'],[f'authoring-inputs/sonic-current/master-{first-80000}.png'])
        self.assertNotEqual(by_id[80105]['editable_inputs'],by_id[80124]['editable_inputs'])
        for row in rows:
            self.assertEqual(row['status'],'current-editable')
            self.assertEqual(row['role'],8)
            self.assertTrue(any(c['role']==146 for c in row['declared_consumers']))
            runtime = [c for c in row['declared_consumers']
                       if c['evidence']=='packaging/runtime-assets-v1.json']
            self.assertEqual(len(runtime), 1)
            self.assertEqual(runtime[0]['path'], f"assets/gameplay/bullet-{row['identity']-80000}-8.hda")
            self.assertFalse(any(c['evidence']=='assets/hd/global-assets-v1/registry.json'
                                 for c in row['declared_consumers']))
            self.assertTrue(any('formal runtime package include this quartet' in n for n in row['notes']))
            self.assertTrue(any('does not enable the default-off enemy renderer' in n for n in row['notes']))

    def test_guided_four_independent_static_contracts(self):
        rows = self.rows_for({80019,80171,80020,80021})
        self.assertEqual(len(rows),4)
        self.assertEqual(len({p for r in rows for p in r['editable_inputs']}),4)
        for row in rows:
            identity=row['identity']
            self.assertEqual(row['editable_inputs'],[f'authoring-inputs/guided-current/master-{identity % 10000}.png'])
            self.assertEqual(row['family'],'guided')
            self.assertEqual(row['role'],8)
            self.assertEqual(any(c['role']==146 for c in row['declared_consumers']),identity in (80020,80021))
            self.assertEqual(len([c for c in row['declared_consumers'] if c['evidence']=='packaging/runtime-assets-v1.json']),1)
            self.assertFalse(any('global-assets' in p for p in row['derived_outputs']))
            self.assertTrue(any('not animation frames' in n for n in row['notes']))

    def test_p05_reuses_current_green_with_distinct_draw_role(self):
        rows = self.rows_for({80214,80215,80216})
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row['role'], 8)
            consumers = row['declared_consumers']
            self.assertTrue(any(c['role'] == 8 for c in consumers))
            self.assertTrue(any(c['role'] == 146 and c['evidence'] == 'src/enemy_reuse_mirror.inc' for c in consumers))
            self.assertEqual(len(row['editable_inputs']), 1)

    def test_green_global_consumer_is_identity_joined(self):
        row = self.rows_for({80214})[0]
        registry = json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_bytes())
        selected = next(r for r in registry['resources'] if r['identity'] == 80214)
        source = 'assets/hd/global-assets-v1/' + selected['path']
        self.assertIn(source, row['derived_outputs'])
        runtime = json.loads((ROOT/'packaging/runtime-assets-v1.json').read_bytes())
        members = runtime['files']
        expected = {r['destination'] for r in members if r['source_path'] == source}
        self.assertTrue(expected)
        self.assertTrue(expected <= {r['path'] for r in row['declared_consumers']})

    def test_shared_input_index_preserves_all_roles_and_recipes(self):
        paths = [r['path'] for r in self.result['inputs']]
        self.assertEqual(len(paths), len(set(paths)))
        master = 'authoring-inputs/protron-current/master.png'
        entry = next(r for r in self.result['inputs'] if r['path'] == master)
        contracts = [r for r in entry['contracts'] if r['identity'] in (80225,80226,80244,1470227)]
        self.assertEqual(len(contracts), 4)
        self.assertEqual(len({r['role'] for r in contracts}), 2)
        self.assertTrue(all('authoring-inputs/protron-current/recipe.json' in r['recipe'] for r in contracts))
        orb_source = self.rows_for({80112})[0]['source_inputs'][0]
        orb_entry = next(r for r in self.result['inputs'] if r['path'] == orb_source)
        self.assertEqual({r['identity'] for r in orb_entry['contracts']}, {80112,1420112})

    def test_no_duplicate_contracts_or_derived_editable_inputs(self):
        keys = [(r['identity'], r['density'], r['role']) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))
        outputs = {p for r in self.rows for p in r['derived_outputs']}
        editable = {p for r in self.rows for p in r['editable_inputs']}
        self.assertFalse(outputs & editable)
        authoring.validate_records(self.rows)

    def test_all_advertised_file_paths_exist(self):
        for row in self.rows:
            for field in ('editable_inputs', 'source_inputs', 'recipe', 'derived_outputs'):
                for relative in row[field]:
                    with self.subTest(identity=row['identity'], field=field, path=relative):
                        self.assertTrue((ROOT/relative).is_file())

    def test_duplicate_contract_rejected(self):
        row = copy.deepcopy(self.rows[0])
        with self.assertRaises(ValueError):
            authoring.validate_records([row, copy.deepcopy(row)])

    def test_derived_output_cannot_be_relabelled_input(self):
        row = copy.deepcopy(next(r for r in self.rows if r['derived_outputs']))
        row['editable_inputs'] = [row['derived_outputs'][0]]
        with self.assertRaises(ValueError):
            authoring.validate_records([row])

    def test_cli_is_deterministic_stdout_and_no_worktree_writes(self):
        command = [sys.executable, '-B', str(ROOT/'scripts/shared_asset_authoring_map.py'), '--id', '80112', '--format', 'json']
        before = subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'], cwd=ROOT)
        first = subprocess.check_output(command, cwd=ROOT)
        second = subprocess.check_output(command, cwd=ROOT)
        self.assertEqual(first, second)
        parsed = json.loads(first)
        self.assertEqual({r['identity'] for r in parsed['resources']}, {80112})
        after = subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'], cwd=ROOT)
        self.assertEqual(before, after)


class StrictLoaderNegativeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='authoring-map-orb-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        paths = orb.input_paths(ROOT)
        for relative in paths:
            target = self.root/relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/relative, target)

    def test_missing_master_is_rejected(self):
        selected = json.loads((self.root/orb.SELECTION).read_bytes())
        (self.root/selected['masters'][0]['source_png']).unlink()
        with self.assertRaises((ValueError, FileNotFoundError)):
            orb.selection(self.root, (self.root/orb.SELECTION).read_bytes())

    def test_wrong_master_hash_is_rejected(self):
        selected = json.loads((self.root/orb.SELECTION).read_bytes())
        target = self.root/selected['masters'][0]['source_png']
        target.write_bytes(target.read_bytes() + b'wrong-hash')
        with self.assertRaises(ValueError):
            orb.selection(self.root, (self.root/orb.SELECTION).read_bytes())

    def test_missing_masked_contract_is_rejected(self):
        mapping = json.loads((self.root/orb.MAPPING).read_bytes())
        mapping['files'].pop()
        (self.root/orb.MAPPING).write_text(json.dumps(mapping))
        with self.assertRaises(ValueError):
            orb.load(self.root)


if __name__ == '__main__':
    unittest.main()
