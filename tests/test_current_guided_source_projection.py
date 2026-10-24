#!/usr/bin/env python3
"""Exact two-source Guided payload extraction; frozen historical oracles remain."""
import copy
import subprocess
import unittest
from unittest.mock import patch
import accepted_later_changes as a

BASE='e5fac6ce2a739ad2e0d6e8f99edaec56411e6e7a'
FILES={'src/render_mirror.c','src/enemy_reuse_mirror.inc'}

class CurrentGuidedProjectionTests(unittest.TestCase):
 def test_exact_inverse_and_partial_reverts_rejected(self):
  ledger=a.current_guided_ledger()
  self.assertEqual(ledger['integration_base'],BASE)
  self.assertEqual(set(ledger['files']),FILES)
  for name,pin in ledger['files'].items():
   raw=(a.ROOT/name).read_bytes()
   old=subprocess.check_output(['git','show',BASE+':'+name],cwd=a.ROOT)
   self.assertEqual(a.project_current_guided_source(name,raw),old)
   self.assertEqual(a.sha(old),pin['previous_sha256'])
   for bad in (old,raw+b'\n',raw[:-1]):
    with self.assertRaises(AssertionError):a.project_current_guided_source(name,bad)
   for hunk in pin['hunks']:
    lines=raw.splitlines(keepends=True);i,j=hunk['after_lines']
    lines[i:j]=hunk['before'].encode().splitlines(keepends=True)
    with self.assertRaises(AssertionError):a.project_current_guided_source(name,b''.join(lines))

 def test_hunks_and_result_have_independent_checks(self):
  ledger=a.current_guided_ledger()
  for name in FILES:
   raw=(a.ROOT/name).read_bytes()
   for field in ('before','after'):
    bad=copy.deepcopy(ledger);bad['files'][name]['hunks'][0][field]+='\n'
    with patch.object(a,'current_guided_ledger',return_value=bad):
     with self.assertRaises(AssertionError):a.project_current_guided_source(name,raw)

 def test_older_chain_and_ledgers_unchanged(self):
  for name in FILES:
   raw=(a.ROOT/name).read_bytes()
   for label in ('normal-observer-surface','enemy-controlled-probe','enemy-proof-dedup','enemy-protron-reuse','render-boundaries'):
    pin=a.load(label+'-source.json')['files'].get(name)
    if pin is not None:self.assertEqual(a.sha(a.project_source(label,name,raw)),pin['previous_sha256'])
  names=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'--','tests/fixtures/accepted-later-changes-v1','tests/current_protron_source_projection.json','tests/current_sonic_source_projection.json'],cwd=a.ROOT).decode().splitlines()
  for name in names:
   self.assertEqual((a.ROOT/name).read_bytes(),subprocess.check_output(['git','show',BASE+':'+name],cwd=a.ROOT))

 def test_exact_current_source_inventory_projection(self):
  import sys,json
  sys.path.insert(0,str(a.ROOT/'scripts'))
  from verify_current_production import source_inventory
  actual=source_inventory(a.ROOT)
  original=json.loads(subprocess.check_output(['git','show',BASE+':packaging/current-production-validation.json'],cwd=a.ROOT))['source_sha256']
  self.assertEqual(len(a.before_current_newshf_inventory(actual)),270)
  self.assertEqual(len(original),269)
  self.assertEqual(a.before_current_guided_inventory(actual),original)
  for name in FILES|{a.CURRENT_GUIDED_HEADER}:
   for action in ('missing','changed'):
    bad=dict(actual)
    if action=='missing':bad.pop(name)
    else:bad[name]='0'*64
    with self.assertRaises((AssertionError,KeyError)):a.before_current_guided_inventory(bad)

 def test_other_family_authority_rejects_stale_guided_header(self):
  import sys,json
  sys.path.insert(0,str(a.ROOT/'scripts'))
  import build_current_art as b
  import current_guided_compatibility as c
  registry=json.loads((a.ROOT/b.REGISTRY).read_bytes())
  read=c.read
  with patch.object(c,'read',side_effect=lambda root,name,*args,**kwargs: read(root,name,*args,**kwargs)+b'\n' if name==c.HEADER else read(root,name,*args,**kwargs)):
   with self.assertRaisesRegex(ValueError,'Stale Guided payload pins'):
    b.verify_authority(a.ROOT,registry)

if __name__=='__main__':unittest.main()
