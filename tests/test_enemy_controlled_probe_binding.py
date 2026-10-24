#!/usr/bin/env python3
"""Exact controlled-probe inverse; immutable earlier ledgers and artwork."""
import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import accepted_later_changes as a
import sys
sys.path.insert(0, str(a.ROOT / 'scripts'))
import portable_history_baselines as history
BASE='4d8981d875f3112a96c1e71644642fefc419a7f6'
NAME='enemy-controlled-probe-source.json'
FILES={'src/game_probe.c','src/asset_debug.c','src/render_mirror.c','src/enemy_reuse_mirror.inc'}
ADDED={'src/enemy_reuse_probe.h','src/enemy_reuse_probe.inc'}
def original(name):return history.preimage(BASE, name, a.ROOT)
class ControlledProbeBinding(unittest.TestCase):
 def test_exact_inverse_and_each_hunk_rejects_partial_revert(self):
  ledger=a.load(NAME)
  self.assertEqual(ledger['integration_base'],BASE)
  self.assertEqual(set(ledger['files']),FILES)
  self.assertEqual(set(ledger['added_sources']),ADDED)
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes();old=original(name)
   self.assertEqual(a.project_source('enemy-controlled-probe',name,raw),old)
   self.assertEqual(a.sha(old),pin['previous_sha256'])
   for bad in (old,raw+b'\n'):
    with self.assertRaises(AssertionError):a.project_source('enemy-controlled-probe',name,bad)
   for edit in pin['hunks']:
    lines=raw.splitlines(keepends=True);i,j=edit['after_lines'];lines[i:j]=edit['before'].encode().splitlines(keepends=True)
    with self.assertRaises(AssertionError):a.project_source('enemy-controlled-probe',name,b''.join(lines))
 def test_hunks_and_result_remain_independent_of_input_pin(self):
  ledger=a.load(NAME);load=a.load
  for name in FILES:
   for field in ('after','before'):
    mutant=copy.deepcopy(ledger);mutant['files'][name]['hunks'][0][field]+='\n'
    with patch.object(a,'load',side_effect=lambda n:mutant if n==NAME else load(n)):
     with self.assertRaises(AssertionError):a.project_source('enemy-controlled-probe',name,(a.ROOT/name).read_bytes())
 def test_exact_added_modules_reject_missing_and_modified(self):
  expected=a.verified_enemy_probe_sources();self.assertEqual(set(expected),ADDED)
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'src').mkdir()
   for name in ADDED:(root/name).write_bytes((a.ROOT/name).read_bytes())
   for name in ADDED:
    path=root/name;raw=path.read_bytes();path.write_bytes(raw+b'\n')
    with self.assertRaises(AssertionError):a.verified_enemy_probe_sources(root)
    path.unlink()
    with self.assertRaises(AssertionError):a.verified_enemy_probe_sources(root)
    path.write_bytes(raw)
   self.assertEqual(a.verified_enemy_probe_sources(root),expected)
 def test_old_ledgers_assets_and_inputs_are_unchanged(self):
  names=history.names(BASE, 'tests/fixtures/accepted-later-changes-v1', a.ROOT)
  actual={p.relative_to(a.ROOT).as_posix() for p in a.FIXTURES.iterdir() if p.is_file()}
  actual.remove('tests/fixtures/accepted-later-changes-v1/normal-observer-surface-source.json');a.load('normal-observer-surface-source.json')
  self.assertEqual(actual-names,{'tests/fixtures/accepted-later-changes-v1/'+NAME});self.assertFalse(names-actual)
  for name in names:self.assertEqual((a.ROOT/name).read_bytes(),original(name))
  # Verify exactly the new current inputs/outputs; no old asset is exempt.
  proof=a.verified_current_protron()
  changed=history.changed(BASE, a.ROOT)
  changed.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','assets','authoring-inputs'],cwd=a.ROOT).decode().splitlines())
  self.assertEqual(changed,proof['paths']|a.verified_current_sonic()['paths']|a.verified_current_guided()['paths'])
 def test_exact_historical_runtime_projection(self):
  previous=json.loads(original('packaging/runtime-assets-v1.json'))['files']
  current=a.before_current_protron_runtime(json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'])
  p={row['destination']:row for row in previous};c={row['destination']:row for row in current}
  self.assertEqual(len(previous),len(current));self.assertEqual(len(c),len(current))
  self.assertEqual(set(p),set(c))
  self.assertEqual({name for name in p if p[name]!=c[name]},{'CURRENT-PRODUCTION-VALIDATION.json'})
 def test_current_authority_and_exact_historical_binding_projection(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  import build_current_art as b
  from verify_current_production import verify
  binding=json.loads((a.ROOT/b.BINDING).read_bytes());old=json.loads(original(b.BINDING))
  self.assertEqual(verify(a.ROOT,binding)-3,267)
  self.assertEqual(binding['reviewed_enemy_controlled_probe']['source_ledger_sha256'],a.PINS[NAME])
  self.assertEqual(a.before_controlled_probe_inventory(binding['source_sha256']),old['source_sha256'])
  registry=json.loads((a.ROOT/b.REGISTRY).read_bytes());b.verify_authority(a.ROOT,registry)
  sources=b.source_inventory(a.ROOT)
  for name in FILES|ADDED:
   for action in ('missing','changed'):
    mutant=dict(sources)
    if action=='missing':del mutant[name]
    else:mutant[name]='0'*64
    with patch.object(b,'source_inventory',return_value=mutant):
     with self.assertRaisesRegex(ValueError,'Unrelated gameplay source changed'):b.verify_authority(a.ROOT,registry)
if __name__=='__main__':unittest.main()
