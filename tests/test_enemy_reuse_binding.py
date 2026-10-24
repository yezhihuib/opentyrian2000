#!/usr/bin/env python3
"""Exact finite inverse/allowlist checks; no broad fixture or asset copies."""
import json,tempfile,unittest
from pathlib import Path
import accepted_later_changes as a
class EnemyReuseBinding(unittest.TestCase):
 def test_six_whole_blob_inverses(self):
  ledger=a.load('enemy-reuse-source.json')
  self.assertEqual(set(ledger['files']),{'src/entity_draw.c','src/entity_draw.h','src/render_mirror.c','src/render_mirror.h','src/sprite.c','src/tyrian2.c'})
  for p,pin in ledger['files'].items():
   raw=(a.ROOT/p).read_bytes()
   self.assertEqual(a.sha(a.project_source('enemy-reuse',p,raw)),pin['previous_sha256'])
   with self.assertRaises(AssertionError):a.project_source('enemy-reuse',p,raw+b'\n')
 def test_three_new_sources_exact(self):
  expected=a.verified_enemy_reuse_sources()
  self.assertEqual(len(expected),3)
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)
   for p in expected:
    target=root/p;target.parent.mkdir(exist_ok=True);target.write_bytes((a.ROOT/p).read_bytes())
   self.assertEqual(a.verified_enemy_reuse_sources(root),expected)
   for p in expected:
    target=root/p;raw=target.read_bytes();target.write_bytes(raw+b'\n')
    with self.assertRaises(AssertionError):a.verified_enemy_reuse_sources(root)
    target.write_bytes(raw)
 def test_current_binding_count(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  from verify_current_production import verify
  binding=json.loads((a.ROOT/'packaging/current-production-validation.json').read_bytes())
  self.assertEqual(verify(a.ROOT,binding)-len(a.verified_enemy_probe_sources())-1,265)
  self.assertEqual(binding['reviewed_enemy_reuse_changes']['ledger_sha256'],a.PINS['enemy-reuse-source.json'])
if __name__=='__main__':unittest.main()
