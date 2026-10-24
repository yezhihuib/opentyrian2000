#!/usr/bin/env python3
"""Exact newest three-file inverse, with immutable old ledgers and assets."""
import copy,json,subprocess,unittest
from unittest.mock import patch
import accepted_later_changes as a
BASE='5109ebbd3f8a5c58075d6358e82e2e4459ac5460'
NAME='enemy-proof-dedup-source.json'
FILES={'src/enemy_reuse_identity.c','src/enemy_reuse_identity.h','src/enemy_reuse_mirror.inc'}
def original(name):return subprocess.check_output(['git','show',BASE+':'+name],cwd=a.ROOT)
class EnemyProofDedupBinding(unittest.TestCase):
 def test_exact_inverse_and_reject_changed_or_partially_reverted_source(self):
  ledger=a.load(NAME)
  self.assertEqual(ledger['integration_base'],BASE)
  self.assertEqual(set(ledger['files']),FILES)
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes();old=original(name)
   self.assertEqual(a.project_source('enemy-proof-dedup',name,raw),old)
   self.assertEqual(a.sha(old),pin['previous_sha256'])
   for bad in (old,raw+b'\n'):
    with self.assertRaises(AssertionError):a.project_source('enemy-proof-dedup',name,bad)
   edit=pin['hunks'][0];lines=raw.splitlines(keepends=True);i,j=edit['after_lines'];lines[i:j]=edit['before'].encode().splitlines(keepends=True)
   with self.assertRaises(AssertionError):a.project_source('enemy-proof-dedup',name,b''.join(lines))
 def test_hunks_and_whole_result_are_required_even_after_input_pin(self):
  ledger=a.load(NAME);load=a.load
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes()
   for field in ('after','before'):
    mutant=copy.deepcopy(ledger);mutant['files'][name]['hunks'][0][field]+='\n'
    with patch.object(a,'load',side_effect=lambda n:mutant if n==NAME else load(n)):
     with self.assertRaises(AssertionError):a.project_source('enemy-proof-dedup',name,raw)
 def test_every_older_ledger_and_all_asset_bytes_are_unchanged(self):
  old_names=set(subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--','tests/fixtures/accepted-later-changes-v1'],cwd=a.ROOT).decode().splitlines())
  actual={p.relative_to(a.ROOT).as_posix() for p in a.FIXTURES.iterdir() if p.is_file()}
  actual.remove('tests/fixtures/accepted-later-changes-v1/enemy-controlled-probe-source.json');a.load('enemy-controlled-probe-source.json')
  actual.remove('tests/fixtures/accepted-later-changes-v1/normal-observer-surface-source.json');a.load('normal-observer-surface-source.json')
  self.assertEqual(actual-old_names,{'tests/fixtures/accepted-later-changes-v1/'+NAME,'tests/fixtures/accepted-later-changes-v1/enemy-reuse-observe-source.json'})
  self.assertFalse(old_names-actual)
  for name in old_names:self.assertEqual((a.ROOT/name).read_bytes(),original(name))
  # Verify exactly the new current inputs/outputs; no old asset is exempt.
  proof=a.verified_current_protron()
  changed=set()
  for args in [('diff','--name-only',BASE,'--'),('ls-files','--others','--exclude-standard','--')]:
   changed.update(subprocess.check_output(['git',*args,'assets','authoring-inputs'],cwd=a.ROOT).decode().splitlines())
  self.assertEqual(changed,proof['paths']|a.verified_current_sonic()['paths'])
 def test_current_binding_runtime_and_original_semantics_inventory(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  from verify_current_production import verify
  binding=json.loads((a.ROOT/'packaging/current-production-validation.json').read_bytes());old=json.loads(original('packaging/current-production-validation.json'))
  self.assertEqual(verify(a.ROOT,binding)-len(a.verified_enemy_probe_sources())-2,265)
  binding=dict(binding,source_sha256=a.before_controlled_probe_inventory(binding['source_sha256']))
  self.assertEqual(set(binding['source_sha256'])-set(a.verified_enemy_observe_sources()),set(old['source_sha256']))
  self.assertEqual({n for n in old['source_sha256'] if old['source_sha256'][n]!=binding['source_sha256'][n]},FILES|set(a.load('enemy-reuse-observe-source.json')['files']))
  self.assertEqual(binding['reviewed_enemy_proof_dedup']['source_ledger_sha256'],a.PINS[NAME])
  previous=json.loads(original('packaging/runtime-assets-v1.json'))['files'];current=a.before_current_protron_runtime(json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'])
  self.assertEqual(len(previous),len(current));p={x['destination']:x for x in previous};c={x['destination']:x for x in current}
  self.assertEqual(set(p),set(c));self.assertEqual({n for n in p if p[n]!=c[n]},{'CURRENT-PRODUCTION-VALIDATION.json'})
  self.assertEqual(set(a.verified_enemy_reuse_sources()),FILES)
if __name__=='__main__':unittest.main()
