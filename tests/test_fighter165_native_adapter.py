"""The finite inherited harness adapter never rewrites historical files."""
import hashlib
from pathlib import Path
import unittest
from fighter165_inherited_native_validation import PINS,adapt_scout
ROOT=Path(__file__).resolve().parents[1]
class FiniteNativeAdapterTests(unittest.TestCase):
 def test_exact_inherited_harness_and_only_four_changes(self):
  p=ROOT/'tests/scout164_newshf_native_validation.c';before=p.read_bytes();after=adapt_scout(before)
  expected=before.decode()
  pairs=[('GLOBAL_NEWSHF_RESOURCE_COUNT==31&&COUNTOF(newshf_profiles)==18','GLOBAL_NEWSHF_RESOURCE_COUNT==34&&COUNTOF(newshf_profiles)==19'),('!global_newshf_phase_bank_matches(31,b10)&&!global_newshf_phase_bank_matches(32,b10)','!global_newshf_phase_bank_matches(34,b10)&&!global_newshf_phase_bank_matches(35,b10)'),('!global_newshf_group_ready(31)&&!global_newshf_group_ready(32)','!global_newshf_group_ready(34)&&!global_newshf_group_ready(35)'),('mode==0?28:mode==1?18:31','mode==0?28:mode==1?18:34')]
  for a,b in pairs:self.assertEqual(expected.count(a),1);expected=expected.replace(a,b)
  self.assertEqual(after,expected.encode());self.assertEqual(p.read_bytes(),before)
 def test_changed_original_harness_rejected(self):
  b=(ROOT/'tests/scout164_newshf_native_validation.c').read_bytes()
  for candidate in (b+b'\n',b.replace(b'CHECK(local>0)',b'CHECK(local>=0)')):
   with self.assertRaises(AssertionError):adapt_scout(candidate)
 def test_all_original_native_inputs_remain_pinned(self):
  for name,h in PINS.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),h,name)
if __name__=='__main__':unittest.main()
