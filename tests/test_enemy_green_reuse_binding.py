#!/usr/bin/env python3
"""P05 finite inverse and unchanged approved sources, no wildcard exemptions."""
import json,unittest
import accepted_later_changes as a
class EnemyGreenReuseBinding(unittest.TestCase):
 def test_exact_five_source_inverse(self):
  ledger=a.load('enemy-green-reuse-source.json')
  self.assertEqual(set(ledger['files']),{'src/enemy_reuse_identity.c','src/enemy_reuse_identity.h','src/enemy_reuse_mirror.inc','src/tyrian2.c','src/render_mirror.c'})
  self.assertEqual(ledger['integration_base'],'47e7d062e0fc4a449a36f1d1f47e53c42f65c66d')
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes()
   self.assertEqual(a.sha(a.project_source('enemy-green-reuse',name,raw)),pin['previous_sha256'])
   with self.assertRaises(AssertionError):a.project_source('enemy-green-reuse',name,raw+b'\n')
 def test_original_modules_still_exact(self):
  original=a.load('enemy-reuse-source.json')['added_sources']
  current=a.verified_enemy_reuse_sources()
  self.assertEqual(set(original),set(current))
  for name,digest in original.items():
   self.assertEqual(a.sha(a.project_source('enemy-green-reuse',name,(a.ROOT/name).read_bytes())),digest)
 def test_binding_authority(self):
  binding=json.loads((a.ROOT/'packaging/current-production-validation.json').read_bytes())
  self.assertEqual(binding['reviewed_enemy_green_reuse']['source_ledger_sha256'],a.PINS['enemy-green-reuse-source.json'])
  self.assertEqual(len(a.before_controlled_probe_inventory(binding['source_sha256'])),265)
  self.assertEqual(len(json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']),1025)
if __name__=='__main__':unittest.main()
