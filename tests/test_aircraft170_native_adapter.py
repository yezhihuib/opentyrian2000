"""Pure-source43-resource driver checks; no native compile/fixtures/gameplay."""
import ast,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from aircraft170_newshf_native_validation import build_source
class Aircraft170NativeAdapter(unittest.TestCase):
    def test_driver_payload_order_and_complete_optional_inventory(self):
        s=build_source(ROOT);ast.parse(s)
        for marker in ("str(ROOT/'tests/aircraft170_newshf_native_validation.c')",'+raw[177105:177182]+raw[176720:176797]+raw[176797:176874]+raw[177028:177105]',"'newshf-aircraft169','newshf-aircraft170'",'[9,6,1,2,10,3,3,3,3,3]','a748cb13a7cc08411b625a622a0818b5f95b987329db627760edb28d180c66a4','test_unchanged and assets_unchanged and originals_unchanged','assert shutil.disk_usage(a.out).free>450*1024**2'):
            self.assertIn(marker,s)
    def test_candidate_identity_phases_masks_and_variant_rejection(self):
        s=(ROOT/'tests/aircraft170_newshf_native_validation.c').read_text()
        for marker in ('current_record=170','profile==21','GLOBAL_NEWSHF_RESOURCE_COUNT==43&&COUNTOF(newshf_profiles)==22','native_counts[3]={295,280,280}','for(unsigned phase=40;phase<43;phase++)','UINT64_C(0x70000000000)','const unsigned invalid[]={43,63,64,UINT_MAX}','family==4?169:302','family<5','global_newshf_rgba[40+mode-12][31]^=1','enemyDat[170].tur[1]=0','!newshf_validation_record_valid(22)'):
            self.assertIn(marker,s)
        for obsolete in ('profile==20','newshf_profiles[20]','0xe000000000','36+pose'):
            self.assertNotIn(obsolete,s)
if __name__=='__main__':unittest.main()
