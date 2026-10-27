"""Finite37 adapters preserve every non-boundary historical oracle byte."""
import hashlib
from pathlib import Path
import unittest
from interceptor166_inherited_native_validation import PINS,adapt_scout,adapt_fighter
ROOT=Path(__file__).resolve().parents[1]
PAIRS={
 'scout164':[
 ('GLOBAL_NEWSHF_RESOURCE_COUNT==31&&COUNTOF(newshf_profiles)==18','GLOBAL_NEWSHF_RESOURCE_COUNT==37&&COUNTOF(newshf_profiles)==20'),
 ('!global_newshf_phase_bank_matches(31,b10)&&!global_newshf_phase_bank_matches(32,b10)','!global_newshf_phase_bank_matches(37,b10)&&!global_newshf_phase_bank_matches(38,b10)'),
 ('!global_newshf_group_ready(31)&&!global_newshf_group_ready(32)','!global_newshf_group_ready(37)&&!global_newshf_group_ready(38)'),
 ('mode==0?28:mode==1?18:31','mode==0?28:mode==1?18:37')],
 'fighter165':[
 ('GLOBAL_NEWSHF_RESOURCE_COUNT==34&&COUNTOF(newshf_profiles)==19','GLOBAL_NEWSHF_RESOURCE_COUNT==37&&COUNTOF(newshf_profiles)==20'),
 ('const unsigned invalid[]={34,63,64,UINT_MAX}','const unsigned invalid[]={37,63,64,UINT_MAX}')]
}
class FiniteNativeAdapterTests(unittest.TestCase):
 def test_exact_inherited_harness_and_only_declared_changes(self):
  for family,adapt in [('scout164',adapt_scout),('fighter165',adapt_fighter)]:
   p=ROOT/('tests/'+family+'_newshf_native_validation.c');before=p.read_bytes();expected=before.decode()
   for a,b in PAIRS[family]:self.assertEqual(expected.count(a),1);expected=expected.replace(a,b)
   self.assertEqual(adapt(before),expected.encode());self.assertEqual(p.read_bytes(),before)
 def test_changed_original_harness_rejected(self):
  for family,adapt in [('scout164',adapt_scout),('fighter165',adapt_fighter)]:
   b=(ROOT/('tests/'+family+'_newshf_native_validation.c')).read_bytes()
   for candidate in (b+b'\n',b.replace(b'CHECK(local>0)',b'CHECK(local>=0)')):
    with self.assertRaises(AssertionError):adapt(candidate)
 def test_all_original_native_inputs_remain_pinned(self):
  for name,h in PINS.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),h,name)
 def test_fighter_high_bits_and_resource_loops_preserved(self):
  s=adapt_fighter((ROOT/'tests/fighter165_newshf_native_validation.c').read_bytes()).decode()
  for line in ('for(unsigned phase=31;phase<34;phase++)','UINT64_C(0x380000000)','global_newshf_rgba[31+mode-12][31]^=1'):
   self.assertIn(line,s)
if __name__=='__main__':unittest.main()
