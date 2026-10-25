"""Finite current RearP7 integration, not additional gameplay eligibility."""
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
import current_rear_p7_compatibility as current
import package_runtime as package
from verify_current_production import source_inventory, verify
BASE = '525de2b9d5b4605dd6bf997cee644c9ac39546c1'
MANIFEST = 'packaging/runtime-assets-v1.json'
DESTINATION = 'assets/gameplay/rear-multicannon-p1-bank8-294-4.hda'
DESTINATIONS = {f'assets/gameplay/rear-multicannon-p1-bank8-{i}-{d}.hda' for i in (294,295) for d in (4,8)}

def old(name):
    return subprocess.check_output(['git', 'show', BASE+':'+name], cwd=ROOT)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

class CurrentRearP7Integration(unittest.TestCase):
    def test_exact_payload_pin_inverse_and_full_inventory(self):
        ledger = json.loads((ROOT/'tests/current_rear_p7_source_projection.json').read_bytes())
        self.assertEqual(ledger['integration_base'], BASE)
        self.assertEqual(set(ledger['files']), {'src/rear_multi_p1_mirror.inc'})
        name = 'src/rear_multi_p1_mirror.inc'; pin = ledger['files'][name]
        raw = (ROOT/name).read_bytes()
        self.assertEqual(sha(raw), pin['current_sha256'])
        self.assertEqual(sha(old(name)), pin['previous_sha256'])
        self.assertEqual(len(pin['hunks']), 1)
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
        self.assertEqual(verify(ROOT, json.loads((ROOT/'packaging/current-production-validation.json').read_bytes())), 274)

    def test_frozen_rear_p7_and_bootstrap_bytes(self):
        prefix = 'assets/hd/artwork/player-rear-multicannon-p7-mode2-twins-v1'
        names = subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--',prefix],cwd=ROOT).decode().splitlines()
        self.assertTrue(names)
        for name in names:
            self.assertEqual((ROOT/name).read_bytes(), old(name))
        previous = {r['destination']:r for r in json.loads(old(MANIFEST))['files']}
        selected = current.load(ROOT)
        self.assertEqual(set(selected), DESTINATIONS)
        for destination in DESTINATIONS:
            self.assertEqual((ROOT/selected[destination]['source_path']).read_bytes(), old(previous[destination]['source_path']))
        self.assertIn(b'#ifndef REAR_P1_RGBA_PINS', (ROOT/current.HEADER).read_bytes())
        self.assertEqual((ROOT/'src/rear_multi_p1_pins.h').read_bytes(), old('src/rear_multi_p1_pins.h'))
        self.assertEqual((ROOT/'assets/hd/global-assets-v1/registry.json').read_bytes(), old('assets/hd/global-assets-v1/registry.json'))

    def test_other_rear_and_front_transports_are_isolated(self):
        previous = json.loads(old(MANIFEST))['files']
        rear = [r for r in previous if Path(r['destination']).name.startswith('rear-multicannon-p1-bank8-')]
        self.assertEqual(len(rear),48)
        untouched = [r for r in rear if r['destination'] not in DESTINATIONS]
        self.assertEqual(len(untouched),44)
        import current_front_multi_compatibility as front
        for row in untouched:
            self.assertEqual((ROOT/row['source_path']).read_bytes(), old(row['source_path']))
        for name in front.input_paths(ROOT) | {front.MAPPING}:
            self.assertEqual((ROOT/name).read_bytes(), old(name))
        self.assertEqual((ROOT/'src/rear_multi_p11_shadow.inc').read_bytes(), old('src/rear_multi_p11_shadow.inc'))

    def test_runtime_only_four_source_revisions_and_binding_change(self):
        from accepted_later_changes import before_current_rear39_runtime
        restored = before_current_rear39_runtime(json.loads((ROOT/MANIFEST).read_bytes())['files'], ROOT)
        now = {r['destination']:r for r in restored}
        previous = {r['destination']:r for r in json.loads(old(MANIFEST))['files']}
        self.assertEqual(len(now), 1029); self.assertEqual(set(now), set(previous))
        for destination,row in now.items():
            if destination=='CURRENT-PRODUCTION-VALIDATION.json':
                continue
            if destination in DESTINATIONS:
                self.assertEqual(row['revision'],'current-single-source-rear-p7')
                row = dict(row, source_path=previous[destination]['source_path'], revision=previous[destination]['revision'])
            self.assertEqual(row, previous[destination])

    def test_current_preview_and_master_map(self):
        from build_current_craft267 import current_overlays
        from shared_asset_authoring_map import build_map
        overlays = current_overlays(ROOT)
        from accepted_later_changes import verified_current_rear39
        rear39 = verified_current_rear39(ROOT)['mapping']
        self.assertEqual(len(rear39), 6)
        from accepted_later_changes import verified_current_rear1
        rear1 = verified_current_rear1(ROOT)['mapping']
        self.assertEqual(len(rear1), 8)
        self.assertEqual(len(overlays), 204)
        historical_overlays = dict(overlays)
        for destination, selected in rear1.items():
            self.assertEqual(historical_overlays.pop(Path(destination).name),
                             (ROOT/selected['source_path']).read_bytes())
        self.assertEqual(len(historical_overlays), 196)
        for destination, selected in rear39.items():
            self.assertEqual(historical_overlays.pop(Path(destination).name),
                             (ROOT/selected['source_path']).read_bytes())
        self.assertEqual(len(historical_overlays), 190)
        rows = [r for r in build_map(ROOT)['resources'] if r['identity'] in current.IDS]
        self.assertEqual(len(rows),4)
        for row in rows:
            name = current.name(row['identity'],row['density'])
            self.assertEqual(overlays[name], (ROOT/current.ROOT/name).read_bytes())
            self.assertEqual(row['family'],'rear-p7')
            self.assertEqual(row['role'],131)
            self.assertEqual(row['editable_inputs'],['authoring-inputs/rear-p7-current/master-294.svg'])
            self.assertEqual(row['status'],'current-editable')
            self.assertEqual({r['path'] for r in row['declared_consumers']}, {'assets/gameplay/'+name, 'src/rear_multi_p1_mirror.inc', 'src/rear_multi_p11_shadow.inc'})
            self.assertNotIn(row['editable_inputs'][0],row['derived_outputs'])

    def test_other_family_dependency_closures(self):
        import importlib
        from current_sidekick_body_compatibility import independent_input_paths
        required = current.input_paths(ROOT) | {current.MAPPING}
        self.assertEqual(len(required),12)
        self.assertTrue(required<=independent_input_paths(ROOT))
        for family in ('guided','sonic','protron','plasma_projectile','front_multi','enemy_orb','newshf','mint27','missile'):
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
        for action in ('missing','all-missing','old-source','wrong-hash','extra-marker','wrong-group'):
            manifest=copy.deepcopy(original)
            if action=='all-missing':manifest['files']=[r for r in manifest['files'] if r['destination'] not in DESTINATIONS]
            elif action=='missing':manifest['files']=[r for r in manifest['files'] if r['destination']!=DESTINATION]
            else:
                row=next(r for r in manifest['files'] if r['destination']==DESTINATION)
                if action=='old-source':row['source_path']=old_row['source_path']
                elif action=='wrong-hash':row['sha256']='0'*64
                elif action=='wrong-group':row['group']='newshf-optin'
                else:
                    row=copy.deepcopy(row);row['destination']='assets/gameplay/unrelated.hda';row['source_path']='unrelated.hda';manifest['files'].append(row)
            with self.subTest(action=action),self.assertRaisesRegex(ValueError,'Rear P7'):
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
