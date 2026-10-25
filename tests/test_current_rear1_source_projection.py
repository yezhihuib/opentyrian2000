"""Rear1 exact eight-row inverse and fresh joint shared-header proof; old ledgers fixed."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import accepted_later_changes as a
import current_rear1_compatibility as c

class CurrentRear1SourceProjection(unittest.TestCase):
 def test_no_new_c_source_and_joint_header_proof(self):
  from verify_current_production import source_inventory
  self.assertEqual(a.current_rear1_ledger()['files'],{})
  actual=source_inventory(a.ROOT)
  self.assertEqual(len(actual),274)
  proof=a.verified_current_rear1()
  self.assertEqual(proof['header_sha256'],actual[c.HEADER])
  self.assertEqual(proof['header_sha256'],a.verified_current_rear_p7()['header_sha256'])
  projected=a.before_current_rear_p7_inventory(actual)
  self.assertEqual(len(projected),273)
  self.assertEqual(len(proof['assets']),9)
  self.assertEqual(len(proof['mapping']),8)

 def test_fresh_missing_tamper_restore_of_all_three_family_closures(self):
  import current_rear_p7_compatibility as p7
  import current_rear39_compatibility as rear39
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   for name in a.rear39_runtime_input_paths():
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes((a.ROOT/name).read_bytes())
   expected=a.verified_current_rear1(root)
   # Same process, exact real filesystem loss/tamper/restore: never a cached proof.
   names=(c.SELECTION,c.MAPPING,c.HEADER,c.INPUT_ROOT+'/master-1.json',
          c.ROOT+'/'+c.name(1310001,4),p7.MAPPING,p7.ROOT+'/'+p7.name(1310294,4),rear39.MAPPING,rear39.ROOT+'/'+rear39.name(1310039,4))
   for name in names:
    target=root/name;raw=target.read_bytes()
    for action in ('missing','tampered'):
     if action=='missing':target.unlink()
     else:target.write_bytes(b'!' + raw[1:])
     with self.subTest(name=name,action=action),self.assertRaises((ValueError,AssertionError)):
      a.verified_current_rear1(root)
     target.write_bytes(raw)
     self.assertEqual(a.verified_current_rear1(root),expected)

 def test_exact_nine_assets_reject_missing_hash_and_mode(self):
  proof=a.verified_current_rear1()['assets']
  preceding=a.verified_current_rear39()['assets']
  for name in proof:
   for action in ('missing','hash','mode'):
    invalid=copy.deepcopy(preceding);invalid.update(copy.deepcopy(proof))
    if action=='missing':del invalid[name]
    elif action=='hash':invalid[name]['sha256']='0'*64
    else:invalid[name]['mode']='100755'
    # Own-family failure must happen before any older-family exclusion.
    with self.subTest(name=name,action=action),self.assertRaisesRegex(AssertionError,'unverified current Rear1 output'):
     a.project_p9_inventory(invalid)

 def test_runtime_eight_exact_preimages_and_p7_coexistence(self):
  rows=json.loads((a.ROOT/'packaging/runtime-assets-v1.json').read_bytes())['files']
  old={r['destination']:r for r in a.current_rear1_ledger()['runtime_before']}
  before=a.before_current_rear1_runtime(rows)
  self.assertEqual({r['destination']:r for r in before if r['destination'] in old},old)
  self.assertEqual([r for r in rows if r['destination'] not in old],[r for r in before if r['destination'] not in old])
  p7old={r['destination']:r for r in a.current_rear_p7_ledger()['runtime_before']}
  both=a.before_current_rear_p7_runtime(rows)
  self.assertEqual({r['destination']:r for r in both if r['destination'] in p7old},p7old)
  self.assertEqual({r['destination']:r for r in both if r['destination'] in old},old)
  for action in ('missing','old','tampered','duplicate'):
   invalid=copy.deepcopy(rows);target=next(r for r in invalid if r['destination'] in old)
   if action=='missing':invalid.remove(target)
   elif action=='old':target.update(old[target['destination']])
   elif action=='duplicate':invalid.append(copy.deepcopy(target))
   else:target['sha256']='0'*64
   with self.subTest(action=action),self.assertRaises(AssertionError):a.before_current_rear1_runtime(invalid)

if __name__=='__main__':unittest.main()
