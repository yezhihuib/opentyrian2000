"""Exact bounded inherited-oracle adaptations; no native execution or fixtures."""
import ast
import hashlib
import unittest
from pathlib import Path
import shared170_inherited_native_validation as adapter
ROOT=Path(__file__).resolve().parents[1]

class Shared170InheritedAdapter(unittest.TestCase):
    def test_historical_inputs_remain_exact(self):
        for name,digest in adapter.PINS.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
    def test_all_harness_changes_are_only_finite_registry_bounds(self):
        cases={
            'scout164':(adapter.adapt_scout,[('==31&&COUNTOF(newshf_profiles)==18','==43&&COUNTOF(newshf_profiles)==22'),('phase_bank_matches(31,b10)&&!global_newshf_phase_bank_matches(32,b10)','phase_bank_matches(43,b10)&&!global_newshf_phase_bank_matches(44,b10)'),('group_ready(31)&&!global_newshf_group_ready(32)','group_ready(43)&&!global_newshf_group_ready(44)'),('mode==0?28:mode==1?18:31','mode==0?28:mode==1?18:43')]),
            'fighter165':(adapter.adapt_fighter,[('==34&&COUNTOF(newshf_profiles)==19','==43&&COUNTOF(newshf_profiles)==22'),('invalid[]={34,63,64,UINT_MAX}','invalid[]={43,63,64,UINT_MAX}')]),
            'interceptor166':(adapter.adapt_interceptor,[('==37&&COUNTOF(newshf_profiles)==20','==43&&COUNTOF(newshf_profiles)==22'),('invalid[]={37,63,64,UINT_MAX}','invalid[]={43,63,64,UINT_MAX}'),('for(unsigned p=0;p<37;p++)','for(unsigned p=0;p<43;p++)')]),
            'aircraft169':(adapter.adapt_aircraft,[('==40&&COUNTOF(newshf_profiles)==21','==43&&COUNTOF(newshf_profiles)==22'),('invalid[]={40,63,64,UINT_MAX}','invalid[]={43,63,64,UINT_MAX}'),('for(unsigned p=0;p<40;p++)','for(unsigned p=0;p<43;p++)')]),
        }
        for name,(adapt,pairs) in cases.items():
            raw=(ROOT/f'tests/{name}_newshf_native_validation.c').read_bytes();changed=adapt(raw).decode()
            for old,new in pairs:
                self.assertIn(new,changed,name);changed=changed.replace(new,old)
            self.assertEqual(changed.encode(),raw,name)
    def test_harness_drift_rejected_before_adaptation(self):
        for name,adapt in [('scout164',adapter.adapt_scout),('fighter165',adapter.adapt_fighter),('interceptor166',adapter.adapt_interceptor),('aircraft169',adapter.adapt_aircraft)]:
            with self.assertRaises(AssertionError):adapt((ROOT/f'tests/{name}_newshf_native_validation.c').read_bytes()+b'\n')
    def test_drivers_keep_original_oracles_and_complete_terminal_inventory(self):
        for name in ('scout164','fighter165','interceptor166','aircraft169','old361'):
            suite='large_newshi' if name=='old361' else name+'_newshf'
            raw=(ROOT/f'tests/{suite}_native_validation.py').read_text()
            changed=adapter.adapt_driver(raw,suite,Path('/not-executed/oracle.c'))
            ast.parse(changed)
            self.assertIn('assert shutil.disk_usage(a.out).free>INHERITED_REQUIRED_FREE',changed)
            if name in ('interceptor166','aircraft169'):
                self.assertIn("'newshf-aircraft169','newshf-aircraft170')",changed)
                self.assertIn('[9,6,1,2,10,3,3,3,3,3]',changed)
            if name!='old361':self.assertIn('/not-executed/oracle.c',changed)
    def test_complete_fresh_source_and_budget_are_required(self):
        text=Path(adapter.__file__).read_text()
        for marker in ("tree(root/'src').items()}==proof['source_sha256']", "tree(fresh/'hd-on-build/src').items()}==proof['source_sha256']", 'assert free>peak+RESERVE_BYTES', 'objects_unchanged=', 'configs_unchanged='):
            self.assertIn(marker,text)
        self.assertEqual(adapter.RESERVE_BYTES,250*1024**2)
        self.assertEqual(set(adapter.PEAK_BYTES),{'aircraft169','interceptor166','fighter165','scout164','old361'})

if __name__=='__main__':unittest.main()
