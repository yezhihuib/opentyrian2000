#!/usr/bin/env python3
"""Finite four-row Guided inverse preserves Sonic quartet and historical paths."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import accepted_later_changes as a

BASE='e5fac6ce2a739ad2e0d6e8f99edaec56411e6e7a'
class GuidedRuntimeProjectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.baseline={p:(a.ROOT/p).read_bytes() for p in a.guided_runtime_input_paths()}
  cls.current=json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
  cls.previous=json.loads(subprocess.check_output(['git','show',BASE+':packaging/runtime-assets-v1.json'],cwd=a.ROOT))['files']
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='guided-runtime-inverse-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  for name,raw in self.baseline.items():
   p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 def test_exact_four_rows_preserve_sonic_and_other_destinations(self):
  current=copy.deepcopy(self.current);result=a.before_current_guided_runtime(current,self.root)
  self.assertEqual(current,self.current);self.assertEqual(len(result),1029)
  old={r['destination']:r for r in self.previous};now={r['destination']:r for r in result}
  self.assertEqual(set(old),set(now))
  self.assertEqual({n for n in now if now[n]!=old[n]},{'CURRENT-PRODUCTION-VALIDATION.json'})
  for n in a.SONIC_RUNTIME_DESTINATIONS:self.assertEqual(now[n],old[n])
  for n in old:
   if n=='CURRENT-PRODUCTION-VALIDATION.json':
    for k in set(old[n])-{'sha256','bytes','git_blob'}:self.assertEqual(now[n][k],old[n][k])
 def test_all_four_rows_required_and_every_field_strict(self):
  destinations={r['destination'] for r in a.current_guided_ledger()['runtime_before']}
  for destination in destinations:
   for field,value in dict(source_path='wrong',destination='wrong',group='wrong',revision='wrong',bytes=0,git_blob='0'*40,sha256='0'*64,extra=True).items():
    rows=copy.deepcopy(self.current);next(r for r in rows if r['destination']==destination)[field]=value
    with self.subTest(destination=destination,field=field),self.assertRaises(AssertionError):a.before_current_guided_runtime(rows,self.root)
  row=next(r for r in self.current if r['destination'] in destinations)
  duplicate=copy.deepcopy(self.current);duplicate[-1]=copy.deepcopy(duplicate[-2])
  replacement=copy.deepcopy(self.current);replacement[-1]['destination']='unknown-runtime-member'
  for rows in (self.current[:-1],self.current+[row],duplicate,replacement,[r for r in self.current if r['destination'] not in destinations]):
   with self.assertRaises(AssertionError):a.before_current_guided_runtime(rows,self.root)
 def test_every_proof_input_missing_or_tampered_rejected(self):
  for name,raw in self.baseline.items():
   p=self.root/name
   for action in ('missing','changed'):
    try:
     if action=='missing':p.unlink()
     else:p.write_bytes(raw+b'broken')
     with self.subTest(name=name,action=action),self.assertRaises((AssertionError,ValueError,OSError)):a.before_current_guided_runtime(self.current,self.root)
    finally:p.write_bytes(raw)
if __name__=='__main__':unittest.main()
