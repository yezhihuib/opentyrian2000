"""Public-base inverse rejection and fully qualified six-resource extension."""
import unittest
from unittest.mock import patch
import linked_newshf_projection as p
class LinkedProjection(unittest.TestCase):
 def test_public_inverse(self):
  for name,pin in p.ledger()['files'].items():
   raw=(p.ROOT/name).read_bytes()
   self.assertEqual(p.sha(p.project_source(name,raw)),pin['previous_sha256'])
   for bad in (raw+b'\n',raw[:-1],p.project_source(name,raw)):
    with self.subTest(name=name),self.assertRaises(AssertionError):p.project_source(name,bad)
   for hunk in pin['hunks']:
    lines=raw.splitlines(True);a,b=hunk['after_lines'];lines[a:b]=hunk['before'].encode().splitlines(True)
    with self.assertRaises(AssertionError):p.project_source(name,b''.join(lines))
 def test_exact_six_and_old_pins_preserved(self):
  import subprocess
  with patch.object(subprocess,'Popen',side_effect=AssertionError('No Git/private object dependency')):proof=p.verified()
  self.assertEqual(len(proof['mapping']),6)
  self.assertNotIn('src/newshf_prototype_pins.h',proof['paths'])
  self.assertNotIn('src/current_newshf_hd_assets.h',proof['paths'])
 def test_every_qualified_input_rejects_mutation(self):
  from pathlib import Path
  original=Path.read_bytes
  for name in p.ledger()['qualified']:
   def read(path):
    raw=original(path);return raw+b'\n' if path==p.ROOT/name else raw
   with self.subTest(name=name),patch.object(Path,'read_bytes',read),self.assertRaises((AssertionError,ValueError,OSError)):
    p.verified()

class LinkedRuntimeProjection(unittest.TestCase):
 def test_six_exact_rows_removed_and_others_unchanged(self):
  import json,copy
  rows=json.loads((p.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
  mapping=p.verified()['mapping'];old=p.before_runtime(rows)
  self.assertEqual(old,[r for r in rows if r['destination'] not in mapping])
  self.assertEqual(len(rows)-len(old),6)
  for destination in mapping:
   for action in ('missing','duplicate','changed'):
    bad=copy.deepcopy(rows);row=next(r for r in bad if r['destination']==destination)
    if action=='missing':bad.remove(row)
    elif action=='duplicate':bad.append(row)
    else:row['revision']='unreviewed'
    with self.subTest(destination=destination,action=action),self.assertRaises(AssertionError):p.before_runtime(bad)

if __name__=='__main__':unittest.main()
