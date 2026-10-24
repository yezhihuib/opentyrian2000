#!/usr/bin/env python3
"""Exact session/output fix inverse, without assets or historical oracle rebases."""
import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import accepted_later_changes as a
BASE='19c96ae931fa1a23b05d75cb9b4387330cc8db54'
NAME='normal-observer-surface-source.json'
FILES={'src/enemy_reuse_observe.h','src/enemy_reuse_observe.inc','src/enemy_reuse_mirror.inc'}
def original(name):return subprocess.check_output(['git','show',BASE+':'+name],cwd=a.ROOT)
class NormalObserverSurfaceBinding(unittest.TestCase):
 def test_exact_inverse_and_partial_revert_rejection(self):
  ledger=a.load(NAME)
  self.assertEqual(ledger['integration_base'],BASE)
  self.assertEqual(set(ledger['files']),FILES)
  self.assertEqual(ledger['added_sources'],{})
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes();old=original(name)
   self.assertEqual(a.project_normal_observer_source(name,raw),old)
   self.assertEqual(a.sha(old),pin['previous_sha256'])
   for bad in (old,raw+b'\n',raw[:-1]):
    with self.assertRaises(AssertionError):a.project_normal_observer_source(name,bad)
   for edit in pin['hunks']:
    lines=raw.splitlines(keepends=True);i,j=edit['after_lines'];lines[i:j]=edit['before'].encode().splitlines(keepends=True)
    with self.assertRaises(AssertionError):a.project_normal_observer_source(name,b''.join(lines))
 def test_hunks_and_result_independent_of_whole_input_digest(self):
  ledger=a.load(NAME);load=a.load
  for name in FILES:
   for field in ('after','before'):
    mutant=copy.deepcopy(ledger);mutant['files'][name]['hunks'][0][field]+='\n'
    with patch.object(a,'load',side_effect=lambda n:mutant if n==NAME else load(n)):
     with self.assertRaises(AssertionError):a.project_normal_observer_source(name,(a.ROOT/name).read_bytes())
 def test_all_historical_ledgers_and_art_unchanged(self):
  names=set(subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--','tests/fixtures/accepted-later-changes-v1'],cwd=a.ROOT).decode().splitlines())
  actual={p.relative_to(a.ROOT).as_posix() for p in a.FIXTURES.iterdir() if p.is_file()}
  self.assertEqual(actual-names,{'tests/fixtures/accepted-later-changes-v1/'+NAME});self.assertFalse(names-actual)
  for name in names:self.assertEqual((a.ROOT/name).read_bytes(),original(name))
  changed=set()
  for args in [('diff','--name-only',BASE,'--'),('ls-files','--others','--exclude-standard','--')]:
   changed.update(subprocess.check_output(['git',*args,'assets','authoring-inputs'],cwd=a.ROOT).decode().splitlines())
  self.assertEqual(changed,a.verified_current_sonic()['paths'] | a.verified_current_guided()['paths'])
 def test_exact_binding_and_runtime_delta(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  import build_current_art as b
  from verify_current_production import verify,source_inventory
  binding=json.loads((a.ROOT/b.BINDING).read_bytes());old=json.loads(original(b.BINDING))
  self.assertEqual(verify(a.ROOT,binding),270)
  self.assertEqual(binding['reviewed_normal_observer_surface']['source_ledger_sha256'],a.PINS[NAME])
  self.assertEqual(a.before_normal_observer_inventory(binding['source_sha256']),old['source_sha256'])
  for name in FILES:
   for action in ('missing','changed'):
    inventory=source_inventory(a.ROOT)
    if action=='missing':del inventory[name]
    else:inventory[name]='0'*64
    with self.assertRaises(AssertionError):a.before_normal_observer_inventory(inventory)
  previous=json.loads(original(b.RUNTIME))['files'];current=a.before_sonic_runtime(json.loads((a.ROOT/b.RUNTIME).read_bytes())['files'])
  p={r['destination']:r for r in previous};c={r['destination']:r for r in current}
  self.assertEqual(len(previous),len(current));self.assertEqual(set(p),set(c))
  self.assertEqual({n for n in p if p[n]!=c[n]},{'CURRENT-PRODUCTION-VALIDATION.json'})
 def test_current_authority_rejects_missing_or_mutated_source(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  import build_current_art as b
  registry=json.loads((a.ROOT/b.REGISTRY).read_bytes());b.verify_authority(a.ROOT,registry)
  sources=b.source_inventory(a.ROOT)
  for name in FILES:
   for action in ('missing','changed'):
    mutant=dict(sources)
    if action=='missing':del mutant[name]
    else:mutant[name]='0'*64
    with patch.object(b,'source_inventory',return_value=mutant):
     with self.assertRaisesRegex(ValueError,'Unrelated gameplay source changed'):b.verify_authority(a.ROOT,registry)
if __name__=='__main__':unittest.main()
