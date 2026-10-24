"""One exact RearP7 source hunk; original source ledgers remain frozen."""
import copy
import unittest
from unittest.mock import patch
import accepted_later_changes as a

NAME='src/rear_multi_p1_mirror.inc'
class CurrentRearP7SourceProjection(unittest.TestCase):
 def test_exact_inverse_rejects_partial_or_altered_current_bytes(self):
  ledger=a.current_rear_p7_ledger();self.assertEqual(set(ledger['files']),{NAME})
  raw=(a.ROOT/NAME).read_bytes();pin=ledger['files'][NAME]
  self.assertEqual(pin['hunks'],[{'after':'#include \"current_rear_multi_payload_pins.h\"\n','after_lines':[2,3],'before':''}])
  previous=a.project_current_rear_p7_source(NAME,raw)
  self.assertEqual(a.sha(previous),pin['previous_sha256'])
  for invalid in (previous,raw+b'\n',raw[:-1]):
   with self.assertRaises(AssertionError):a.project_current_rear_p7_source(NAME,invalid)
  for key in ('before','after'):
   modified=copy.deepcopy(ledger);modified['files'][NAME]['hunks'][0][key]+='\n'
   with patch.object(a,'current_rear_p7_ledger',return_value=modified),self.assertRaises(AssertionError):
    a.project_current_rear_p7_source(NAME,raw)

 def test_header_proof_precedes_exclusion(self):
  from verify_current_production import source_inventory
  actual=source_inventory(a.ROOT)
  projected=a.before_current_rear_p7_inventory(actual)
  self.assertEqual(len(actual),274)
  self.assertEqual(len(projected),273)
  self.assertEqual({n:h for n,h in actual.items() if n not in (NAME,a.CURRENT_REAR_P7_HEADER)},{n:h for n,h in projected.items() if n!=NAME})
  self.assertNotIn(a.CURRENT_REAR_P7_HEADER,projected)
  self.assertEqual(projected[NAME],a.current_rear_p7_ledger()['files'][NAME]['previous_sha256'])
  for key in (NAME,a.CURRENT_REAR_P7_HEADER):
   for action in ('missing','changed'):
    invalid=dict(actual)
    if action=='missing':invalid.pop(key)
    else:invalid[key]='0'*64
    with self.subTest(key=key,action=action),self.assertRaises((AssertionError,KeyError)):
     a.before_current_rear_p7_inventory(invalid)

 def test_same_call_rechecks_header_bytes(self):
  import current_rear_p7_compatibility as c
  actual=c.read
  with patch.object(c,'read',side_effect=lambda root,name,*args:actual(root,name,*args)+b'\n' if name==c.HEADER else actual(root,name,*args)):
   with self.assertRaisesRegex(ValueError,'payload pins'):a.verified_current_rear_p7()
  self.assertEqual(len(a.verified_current_rear_p7()['assets']),5)

 def test_actual_source_rechecked_after_missing_changed_and_restore(self):
  import current_rear_p7_compatibility as c
  import tempfile
  from pathlib import Path
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   names=a.rear_p7_runtime_input_paths()
   for name in names:
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes((a.ROOT/name).read_bytes())
   expected=a.verified_current_rear_p7(root)
   source=root/NAME;raw=source.read_bytes()
   source.unlink()
   with self.assertRaises((ValueError,AssertionError)):a.verified_current_rear_p7(root)
   source.write_bytes(raw+b'\n')
   with self.assertRaises(AssertionError):a.verified_current_rear_p7(root)
   source.write_bytes(raw)
   self.assertEqual(a.verified_current_rear_p7(root),expected)

 def test_runtime_exact_current_rows_and_frozen_preimages(self):
  import json
  rows=json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
  before=a.before_current_rear_p7_runtime(rows)
  expected={r['destination']:r for r in a.current_rear_p7_ledger()['runtime_before']}
  self.assertEqual({r['destination']:r for r in before if r['destination'] in expected},expected)
  self.assertEqual(len(before),1029)
  self.assertEqual([r for r in a.before_current_rear39_runtime(rows) if r['destination'] not in expected],[r for r in before if r['destination'] not in expected])
  for action in ('missing','old','tampered'):
   invalid=copy.deepcopy(rows);target=next(r for r in invalid if r['destination'] in expected and r['source_path'].startswith('assets/hd/current-compat/rear-p7/'))
   if action=='missing':invalid.remove(target)
   elif action=='old':target.update(expected[target['destination']])
   else:target['sha256']='0'*64
   with self.subTest(action=action),self.assertRaises(AssertionError):a.before_current_rear_p7_runtime(invalid)

if __name__=='__main__':unittest.main()
