"""Finite current Mint27 integration, not additional gameplay eligibility."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import current_mint27_compatibility as current
import package_runtime as package
from verify_current_production import source_inventory, verify
BASE = '4f7e60b5c9b64356719b207ff66a14ad081bcef6'
MANIFEST = 'packaging/runtime-assets-v1.json'
DESTINATION = 'assets/gameplay/bullet-27-8.hda'

def old(name):
    return subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

class CurrentMint27Integration(unittest.TestCase):
    def test_exact_payload_pin_inverse_and_full_inventory(self):
        ledger = json.loads((ROOT/'tests/current_mint27_source_projection.json').read_bytes())
        self.assertEqual(ledger['integration_base'], BASE)
        self.assertEqual(set(ledger['files']), {'src/render_mirror.c'})
        name = 'src/render_mirror.c'; pin = ledger['files'][name]
        raw = (ROOT/name).read_bytes()
        self.assertEqual(sha(raw), pin['current_sha256'])
        self.assertEqual(sha(old(name)), pin['previous_sha256'])
        self.assertEqual(len(pin['hunks']), 2)
        for hunk in reversed(pin['hunks']):
            after, before = hunk['after'].encode(), hunk['before'].encode()
            self.assertEqual(raw.count(after), 1)
            raw = raw.replace(after, before)
        self.assertEqual(raw, old(name))
        actual = source_inventory(ROOT)
        expected = json.loads(old('packaging/current-production-validation.json'))['source_sha256']
        self.assertEqual(set(actual)-set(expected), {current.HEADER})
        self.assertEqual(set(expected)-set(actual), set())
        actual.pop(current.HEADER); actual[name] = sha(raw)
        self.assertEqual(actual, expected)
        self.assertEqual(verify(ROOT, json.loads((ROOT/'packaging/current-production-validation.json').read_bytes())), 272)

    def test_frozen_mint27_and_bootstrap_bytes(self):
        prefix = 'assets/hd/artwork/player-mint27-one-v1'
        names = subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--',prefix],cwd=ROOT).decode().splitlines()
        self.assertTrue(names)
        for name in names:
            self.assertEqual((ROOT/name).read_bytes(), old(name))
        previous = next(r for r in json.loads(old(MANIFEST))['files'] if r['destination']==DESTINATION)
        selected = current.load(ROOT)
        self.assertEqual(set(selected), {DESTINATION})
        self.assertEqual((ROOT/selected[DESTINATION]['source_path']).read_bytes(), old(previous['source_path']))
        self.assertIn(b'UINT64_C(0xe75bfc31a0616e75)', (ROOT/current.HEADER).read_bytes())
        self.assertEqual((ROOT/'assets/hd/global-assets-v1/registry.json').read_bytes(), old('assets/hd/global-assets-v1/registry.json'))

    def test_runtime_only_one_source_revision_and_binding_change(self):
        now = {r['destination']:r for r in json.loads((ROOT/MANIFEST).read_bytes())['files']}
        previous = {r['destination']:r for r in json.loads(old(MANIFEST))['files']}
        self.assertEqual(len(now), 1029); self.assertEqual(set(now), set(previous))
        for destination,row in now.items():
            if destination=='CURRENT-PRODUCTION-VALIDATION.json':
                continue
            if destination==DESTINATION:
                self.assertEqual(row['revision'],'current-single-source-mint27')
                row = dict(row, source_path=previous[destination]['source_path'], revision=previous[destination]['revision'])
            self.assertEqual(row, previous[destination])

    def test_current_preview_and_master_map(self):
        from build_current_craft267 import current_overlays
        from shared_asset_authoring_map import build_map
        overlays = current_overlays(ROOT)
        self.assertEqual(len(overlays), 183)
        self.assertEqual(overlays['bullet-27-8.hda'], (ROOT/current.ROOT/'bullet-27-8.hda').read_bytes())
        rows = [r for r in build_map(ROOT)['resources'] if r['identity']==80027]
        self.assertEqual(len(rows),1)
        row = rows[0]
        self.assertEqual(row['family'],'mint27')
        self.assertEqual(row['editable_inputs'],['authoring-inputs/mint27-current/master-27.png'])
        self.assertEqual(row['status'],'current-editable')
        self.assertEqual({r['path'] for r in row['declared_consumers']}, {DESTINATION, 'src/render_mirror.c'})
        self.assertNotIn(row['editable_inputs'][0],row['derived_outputs'])

    def test_other_family_dependency_closures(self):
        import importlib
        from current_sidekick_body_compatibility import independent_input_paths
        required = current.input_paths(ROOT) | {current.MAPPING}
        self.assertEqual(len(required),6)
        self.assertTrue(required<=independent_input_paths(ROOT))
        for family in ('guided','sonic','protron','plasma_projectile','front_multi','enemy_orb','newshf'):
            builder = importlib.import_module('build_current_'+family)
            compat = importlib.import_module('current_'+family+'_compatibility')
            selected = json.loads((ROOT/compat.SELECTION).read_bytes())
            self.assertTrue(required<=builder.dependencies(ROOT,selected),family)

    def run_package(self, manifest):
        with patch.object(package,'load_manifest',return_value=manifest),contextlib.redirect_stdout(io.StringIO()):
            return package.main(['--source-root',str(ROOT)])

    def test_package_missing_old_source_stale_extra_and_group_rejected(self):
        original=json.loads((ROOT/MANIFEST).read_bytes())
        old_row=next(r for r in json.loads(old(MANIFEST))['files'] if r['destination']==DESTINATION)
        for action in ('missing','old-source','wrong-hash','extra-marker','wrong-group'):
            manifest=copy.deepcopy(original)
            if action=='missing':manifest['files']=[r for r in manifest['files'] if r['destination']!=DESTINATION]
            else:
                row=next(r for r in manifest['files'] if r['destination']==DESTINATION)
                if action=='old-source':row['source_path']=old_row['source_path']
                elif action=='wrong-hash':row['sha256']='0'*64
                elif action=='wrong-group':row['group']='newshf-optin'
                else:
                    row=copy.deepcopy(row);row['destination']='assets/gameplay/unrelated.hda';row['source_path']='unrelated.hda';manifest['files'].append(row)
            with self.subTest(action=action),self.assertRaisesRegex(ValueError,'Mint27'):
                self.run_package(manifest)

    def test_external_historical_manifest_does_not_require_current_contract(self):
        previous=json.loads(old(MANIFEST));previous['files']=[r for r in previous['files'] if r['destination']==DESTINATION]
        with patch.object(package,'load_manifest',return_value=previous), \
             patch.object(current,'load',side_effect=AssertionError('No current contract for historical export')), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(package.main(['--source-root',str(ROOT),'--manifest',str(ROOT/'external-historical.json')]),0)

    def test_package_baseline_passes(self):
        self.assertEqual(self.run_package(json.loads((ROOT/MANIFEST).read_bytes())),0)

if __name__=='__main__':unittest.main()
