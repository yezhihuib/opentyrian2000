"""Bounded current aircraft integration; no new gameplay or platform acceptance."""
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
import current_newshf_compatibility as current
import build_newshf_hd as legacy
import package_runtime as package
from verify_current_production import source_inventory, verify

BASE='fca48c7ace7050d52a554900f8aac47157e8e4db'
MANIFEST='packaging/runtime-assets-v1.json'

def old(name):
    return subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)

def sha(raw):return hashlib.sha256(raw).hexdigest()

class CurrentNewshfIntegration(unittest.TestCase):
    def test_exact_include_inverse_and_full_inventory(self):
        ledger=json.loads((ROOT/'tests/current_newshf_source_projection.json').read_bytes())
        self.assertEqual(ledger['integration_base'],BASE)
        self.assertEqual(set(ledger['files']),{'src/global_newshf_mirror.inc'})
        name='src/global_newshf_mirror.inc';pin=ledger['files'][name];raw=(ROOT/name).read_bytes()
        self.assertEqual(sha(raw),pin['current_sha256'])
        self.assertEqual(sha(old(name)),pin['previous_sha256'])
        hunk,=pin['hunks'];before=hunk['before'].encode();after=hunk['after'].encode()
        self.assertEqual(raw.count(after),1)
        self.assertEqual(raw.replace(after,before),old(name))
        actual=source_inventory(ROOT)
        expected=json.loads(old('packaging/current-production-validation.json'))['source_sha256']
        self.assertEqual(set(actual)-set(expected),{current.HEADER})
        self.assertEqual(set(expected)-set(actual),set())
        actual.pop(current.HEADER);actual[name]=sha(old(name))
        self.assertEqual(actual,expected)
        self.assertEqual(verify(ROOT,json.loads((ROOT/'packaging/current-production-validation.json').read_bytes())),271)

    def test_frozen_authority_and_bootstrap_bytes(self):
        for prefix in ('authoring-inputs/enemies/newshf-phase-a','assets/hd/newshf-v1'):
            names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--',prefix],cwd=ROOT).decode().splitlines()
            self.assertTrue(names)
            for name in names:self.assertEqual((ROOT/name).read_bytes(),old(name))
        for name in ('src/newshf_hd_assets.h','scripts/build_newshf_hd.py','scripts/check_newshf_phase_a.py'):
            self.assertEqual((ROOT/name).read_bytes(),old(name))
        frozen=legacy.load(ROOT);now=current.load(ROOT)
        self.assertEqual(set(now),set(frozen))
        for dest,row in now.items():
            self.assertEqual((ROOT/row['source_path']).read_bytes(),(ROOT/frozen[dest]['source_path']).read_bytes())
        # Generated header selects exactly the same C resource initializers.
        new=(ROOT/current.HEADER).read_text().split('static const GlobalAssetResource',1)[1]
        previous=(ROOT/legacy.HEADER).read_text().split('static const GlobalAssetResource',1)[1]
        self.assertEqual(new,previous)

    def test_runtime_only_six_source_paths_and_binding_change(self):
        current_rows={r['destination']:r for r in json.loads((ROOT/MANIFEST).read_bytes())['files']}
        previous={r['destination']:r for r in json.loads(old(MANIFEST))['files']}
        self.assertEqual(len(current_rows),1029);self.assertEqual(set(current_rows),set(previous))
        six={'assets/global/newshf/'+current.name(i) for i in current.EDIT_IDS}
        for destination,row in current_rows.items():
            if destination=='CURRENT-PRODUCTION-VALIDATION.json':continue
            if destination in six:
                restored=dict(row,source_path=previous[destination]['source_path'])
                self.assertEqual(restored,previous[destination])
            else:self.assertEqual(row,previous[destination])

    def test_canonical_master_map_and_frozen_168(self):
        from shared_asset_special_sources import records
        rows=records(ROOT);self.assertEqual(len(rows),9)
        for row in rows:
            identity=row['identity']
            if identity in current.EDIT_IDS:
                record=163 if identity<2100003 else 167
                self.assertEqual(row['editable_inputs'],[f'authoring-inputs/newshf-current/master-{record}.png'])
                self.assertEqual(row['status'],'current-editable')
                self.assertNotIn(row['editable_inputs'][0],row['derived_outputs'])
            else:
                self.assertEqual(row['editable_inputs'],[])
                self.assertEqual(row['status'],'frozen-reproducer')

    def test_other_family_input_closures_include_current_and_legacy(self):
        from current_sidekick_body_compatibility import independent_input_paths
        import importlib
        required=current.input_paths(ROOT)
        self.assertTrue(legacy.input_paths(ROOT)<=required)
        self.assertTrue(required<=independent_input_paths(ROOT))
        for family in ('guided','sonic','protron','plasma_projectile','front_multi','enemy_orb'):
            builder=importlib.import_module('build_current_'+family)
            compat=importlib.import_module('current_'+family+'_compatibility')
            selected=json.loads((ROOT/compat.SELECTION).read_bytes())
            self.assertTrue(required<=builder.dependencies(ROOT,selected),family)

    def run_package(self, manifest):
        with patch.object(package,'load_manifest',return_value=manifest),contextlib.redirect_stdout(io.StringIO()):
            return package.main(['--source-root',str(ROOT)])

    def test_package_current_missing_alias_stale_and_extra_rejected(self):
        original=json.loads((ROOT/MANIFEST).read_bytes())
        target='assets/global/newshf/'+current.name(2100000)
        for action in ('missing-one','missing-all','old-source','wrong-hash','extra-marker','wrong-group'):
            manifest=copy.deepcopy(original)
            if action=='missing-one':manifest['files']=[r for r in manifest['files'] if r['destination']!=target]
            elif action=='missing-all':manifest['files']=[r for r in manifest['files'] if r['group']!='newshf-optin']
            else:
                row=next(r for r in manifest['files'] if r['destination']==target)
                if action=='old-source':row['source_path']='assets/hd/newshf-v1/'+current.name(2100000)
                elif action=='wrong-hash':row['sha256']='0'*64
                elif action=='wrong-group':row['group']='gameplay'
                else:
                    row=copy.deepcopy(row);row['destination']='assets/global/other.hda';row['source_path']='unrelated.hda';manifest['files'].append(row)
            with self.subTest(action=action),self.assertRaisesRegex(ValueError,'NEWSHF'):
                self.run_package(manifest)

    def test_historical_external_manifest_does_not_import_current_contract(self):
        previous=json.loads(old(MANIFEST))
        previous['files']=[r for r in previous['files'] if r['group']=='newshf-optin']
        self.assertEqual(len(previous['files']),9)
        with patch.object(package,'load_manifest',return_value=previous), \
             patch.object(current,'load',side_effect=AssertionError('current contract must not run')), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(package.main(['--source-root',str(ROOT),'--manifest',str(ROOT/'external-historical.json')]),0)

    def test_package_baseline_passes(self):
        self.assertEqual(self.run_package(json.loads((ROOT/MANIFEST).read_bytes())),0)

if __name__=='__main__':unittest.main()
