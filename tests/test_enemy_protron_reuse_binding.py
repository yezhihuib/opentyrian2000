#!/usr/bin/env python3
"""Exact P09 addition and finite inverses; no wildcard historical exemptions."""
import json
import subprocess
import unittest
import accepted_later_changes as a
import sys
sys.path.insert(0, str(a.ROOT / 'scripts'))
import portable_history_baselines as history
BASE='4810555b37ab12247690f383160e6bff433f41c6'
P09='assets/hd/enemy-protron-p09-v1/'
NEW_ASSETS={P09+n for n in ('identity.json','recipe.json','source227.png','enemy-protron-p09-227-8.hda')}
NEW_DEST='assets/gameplay/enemy-protron-p09-227-8.hda'

def original(name,base=BASE):
 return history.preimage(base, name, a.ROOT)

def check_additive_assets_and_runtime(base=BASE):
 proof=a.verified_protron_current()
 assert set(proof['assets'])==NEW_ASSETS
 # Include untracked files before commit as well as tracked differences after
 # commit, with exact names. Every other historical asset remains byte-identical.
 changed=history.changed(base, a.ROOT)
 changed.update(subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','assets','authoring-inputs'],cwd=a.ROOT).decode().splitlines())
 mint27_proof=a.verified_current_mint27()
 assert mint27_proof['paths']<=changed
 changed-=mint27_proof['paths']
 newshf_proof=a.verified_current_newshf()
 assert newshf_proof['paths']<=changed
 changed-=newshf_proof['paths']
 guided_proof=a.verified_current_guided()
 assert guided_proof['paths']<=changed
 changed-=guided_proof['paths']
 sonic_proof=a.verified_current_sonic()
 assert sonic_proof['paths']<=changed
 changed-=sonic_proof['paths']
 current_proof=a.verified_current_protron()
 assert current_proof['paths']<=changed
 changed-=current_proof['paths']
 assert changed==NEW_ASSETS,changed
 current=a.before_current_protron_runtime(json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'])
 previous=json.loads(original('packaging/runtime-assets-v1.json',base))['files']
 assert len(current)==1025 and len(previous)==1024
 new={x['destination']:x for x in current};old={x['destination']:x for x in previous}
 assert len(new)==len(current) and len(old)==len(previous)
 assert new.keys()-old.keys()=={NEW_DEST} and not old.keys()-new.keys()
 assert {name for name in old if new[name]!=old[name]}=={'CURRENT-PRODUCTION-VALIDATION.json'}
 entry=new[NEW_DEST]
 assert entry['source_path']==P09+'enemy-protron-p09-227-8.hda'
 assert entry['sha256']==proof['assets'][entry['source_path']]['sha256']
 return proof

class EnemyProtronReuseBinding(unittest.TestCase):
 def test_exact_four_source_inverse(self):
  ledger=a.load('enemy-protron-reuse-source.json')
  self.assertEqual(ledger['integration_base'],BASE)
  self.assertEqual(set(ledger['files']),{'src/enemy_reuse_identity.c','src/enemy_reuse_mirror.inc','src/render_mirror.c','src/tyrian2.c'})
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes()
   restored=a.project_source('enemy-protron-reuse',name,raw)
   self.assertEqual(restored,original(name))
   self.assertEqual(a.sha(restored),pin['previous_sha256'])
   with self.assertRaises(AssertionError):a.project_source('enemy-protron-reuse',name,raw+b'\n')
 def test_old_ledgers_unchanged(self):
  for path in sorted(a.FIXTURES.glob('*.json')):
   if path.name in ('normal-observer-surface-source.json','enemy-protron-reuse-source.json','enemy-proof-dedup-source.json','enemy-reuse-observe-source.json','enemy-controlled-probe-source.json'):continue
   self.assertEqual(path.read_bytes(),original(path.relative_to(a.ROOT).as_posix()))
 def test_exact_additive_assets_and_runtime(self):
  check_additive_assets_and_runtime()
 def test_source_binding_and_derived_header(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  from verify_current_production import verify
  binding=json.loads((a.ROOT/'packaging/current-production-validation.json').read_bytes())
  verify(a.ROOT,binding)
  self.assertEqual(len(a.before_current_newshf_inventory(binding['source_sha256']))-len(a.verified_enemy_probe_sources())-3,265)
  binding=dict(binding,source_sha256=a.before_controlled_probe_inventory(binding['source_sha256']))
  old=json.loads(original('packaging/current-production-validation.json'))
  self.assertEqual(set(binding['source_sha256'])-set(old['source_sha256']),{a.PROTRON_HEADER}|set(a.verified_enemy_observe_sources()))
  self.assertEqual(a.sha((a.ROOT/a.PROTRON_HEADER).read_bytes()),a.verified_protron_current()['header_sha256'])
  self.assertEqual(binding['reviewed_enemy_protron_reuse']['source_ledger_sha256'],a.PINS['enemy-protron-reuse-source.json'])
if __name__=='__main__':unittest.main()
