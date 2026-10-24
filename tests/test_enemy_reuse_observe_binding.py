#!/usr/bin/env python3
"""Exact observer source delta; historical gameplay/assets are not rebased."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import accepted_later_changes as a

BASE='6488220464055166c69267abee7b3a11b41fe16b'
NAME='enemy-reuse-observe-source.json'
FILES={'src/config.c','src/enemy_reuse_identity.c','src/enemy_reuse_mirror.inc',
       'src/game_probe.c','src/opentyr.c','src/render_mirror.c'}
ADDED={'src/enemy_reuse_observe.h','src/enemy_reuse_observe.inc'}
def original(name):
 return subprocess.check_output(['git','show',BASE+':'+name],cwd=a.ROOT)

class EnemyReuseObserveBinding(unittest.TestCase):
 def test_exact_six_file_inverse_and_whole_blob_rejection(self):
  ledger=a.load(NAME)
  self.assertEqual(ledger['integration_base'],BASE)
  self.assertEqual(set(ledger['files']),FILES)
  self.assertEqual(set(ledger['added_sources']),ADDED)
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes();old=original(name)
   self.assertEqual(a.project_source('enemy-reuse-observe',name,raw),old)
   self.assertEqual(a.sha(old),pin['previous_sha256'])
   for bad in (old,raw+b'\n'):
    with self.assertRaises(AssertionError):a.project_source('enemy-reuse-observe',name,bad)
   for edit in pin['hunks']:
    lines=raw.splitlines(keepends=True);i,j=edit['after_lines']
    lines[i:j]=edit['before'].encode().splitlines(keepends=True)
    with self.assertRaises(AssertionError):a.project_source('enemy-reuse-observe',name,b''.join(lines))
 def test_input_digest_does_not_replace_hunk_and_result_checks(self):
  ledger=a.load(NAME);load=a.load
  for name in FILES:
   raw=(a.ROOT/name).read_bytes()
   for field in ('after','before'):
    mutant=copy.deepcopy(ledger);mutant['files'][name]['hunks'][0][field]+='\n'
    with patch.object(a,'load',side_effect=lambda n:mutant if n==NAME else load(n)):
     with self.assertRaises(AssertionError):a.project_source('enemy-reuse-observe',name,raw)
 def test_exact_two_added_modules_and_mutation_rejection(self):
  expected=a.verified_enemy_observe_sources();self.assertEqual(set(expected),ADDED)
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory);(root/'src').mkdir()
   for name in ADDED:(root/name).write_bytes((a.ROOT/name).read_bytes())
   self.assertEqual(a.verified_enemy_observe_sources(root),expected)
   for name in ADDED:
    path=root/name;raw=path.read_bytes();path.write_bytes(raw+b'\n')
    with self.assertRaises(AssertionError):a.verified_enemy_observe_sources(root)
    path.write_bytes(raw)
 def test_all_older_ledgers_and_assets_unchanged(self):
  names=set(subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--','tests/fixtures/accepted-later-changes-v1'],cwd=a.ROOT).decode().splitlines())
  actual={p.relative_to(a.ROOT).as_posix() for p in a.FIXTURES.iterdir() if p.is_file()}
  actual.remove('tests/fixtures/accepted-later-changes-v1/enemy-controlled-probe-source.json');a.load('enemy-controlled-probe-source.json')
  actual.remove('tests/fixtures/accepted-later-changes-v1/normal-observer-surface-source.json');a.load('normal-observer-surface-source.json')
  self.assertEqual(actual-names,{'tests/fixtures/accepted-later-changes-v1/'+NAME})
  self.assertFalse(names-actual)
  for name in names:self.assertEqual((a.ROOT/name).read_bytes(),original(name))
  # Verify exactly the new current inputs/outputs; no old asset is exempt.
  proof=a.verified_current_protron()
  changed=set()
  for args in [('diff','--name-only',BASE,'--'),('ls-files','--others','--exclude-standard','--')]:
   changed.update(subprocess.check_output(['git',*args,'assets','authoring-inputs'],cwd=a.ROOT).decode().splitlines())
  self.assertEqual(changed,proof['paths']|a.verified_current_sonic()['paths']|a.verified_current_guided()['paths'])
 def test_art_authority_cannot_rebind_observer_modules(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  import build_current_art as builder
  registry=json.loads((a.ROOT/builder.REGISTRY).read_bytes())
  sources=builder.source_inventory(a.ROOT)
  historical=a.before_controlled_probe_inventory(sources)
  for name in (builder.HEADER,builder.LEGACY_HEADER,'src/current_hud_payload_pins.h','src/current_tank_shell_payload_pins.h','src/current_enemy_energy_payload_pins.h','src/current_sidekick_body_payload_pins.h','src/current_plasma_projectile_payload_pins.h','src/hd_front_multi_current.h','src/current_enemy_orb_payload_pins.h','src/newshf_hd_assets.h','src/current_enemy_protron_payload_pins.h'):historical.pop(name,None)
  builder.verify_authority(a.ROOT,registry)
  self.assertEqual(builder.source_manifest_digest(historical),'e2651e92494f25a0070b9b28e46806aad542bc4d1cc59a0230f913d8658c382d')
  for name in ADDED:
   for action in ('missing','changed'):
    mutant=dict(sources)
    if action=='missing':del mutant[name]
    else:mutant[name]='0'*64
    with patch.object(builder,'source_inventory',return_value=mutant):
     with self.assertRaisesRegex(ValueError,'Unrelated gameplay source changed'):
      builder.verify_authority(a.ROOT,registry)
 def test_binding_inventory_and_runtime_change_are_exact(self):
  import sys
  sys.path.insert(0,str(a.ROOT/'scripts'))
  from verify_current_production import verify
  binding=json.loads((a.ROOT/'packaging/current-production-validation.json').read_bytes())
  old=json.loads(original('packaging/current-production-validation.json'))
  self.assertEqual(verify(a.ROOT,binding)-len(a.verified_enemy_probe_sources())-3,265)
  binding=dict(binding,source_sha256=a.before_controlled_probe_inventory(binding['source_sha256']))
  self.assertEqual(set(binding['source_sha256'])-set(old['source_sha256']),ADDED)
  self.assertFalse(set(old['source_sha256'])-set(binding['source_sha256']))
  self.assertEqual({n for n in old['source_sha256'] if old['source_sha256'][n]!=binding['source_sha256'][n]},FILES)
  self.assertEqual(binding['reviewed_enemy_reuse_observe']['source_ledger_sha256'],a.PINS[NAME])
  previous=json.loads(original('packaging/runtime-assets-v1.json'))['files']
  current=a.before_current_protron_runtime(json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files'])
  p={x['destination']:x for x in previous};c={x['destination']:x for x in current}
  self.assertEqual(len(previous),len(current));self.assertEqual(set(p),set(c))
  self.assertEqual({n for n in p if p[n]!=c[n]},{'CURRENT-PRODUCTION-VALIDATION.json'})

if __name__=='__main__':unittest.main()
