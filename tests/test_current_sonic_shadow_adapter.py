"""Selected master pins cannot weaken the original shadow structural oracle."""
import re
import subprocess
import unittest
from unittest.mock import patch
import run_sonic_quadrant_shadow_tests as s


class CurrentMasterShadowAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(s.ROOT/'src/render_mirror.c').read_text()
        cls.protron=(s.ROOT/'src'/s.PROTRON_HEADER).read_text()
        cls.sonic=(s.ROOT/'src'/s.SONIC_HEADER).read_text()

    def test_resolves_exactly_45_rows_and_rederives_selected_masters(self):
        self.assertEqual(len(s.verify_master_rows(self.source)),45)
        self.assertEqual(set(s.master_payloads('sonic')),{105,106,124,125})
        self.assertEqual(set(s.master_payloads('protron')),{225,244,226})

    def test_generated_header_missing_duplicate_unknown_or_malformed_pin_rejected(self):
        for name,header in (('protron_header',self.protron),('sonic_header',self.sonic)):
            macro=next(line for line in header.splitlines() if '_PAYLOAD_FNV ' in line)
            for bad in (header.replace(macro,'',1),header+'\n'+macro+'\n',
                        header.replace('_D8_PAYLOAD_FNV','_D4_PAYLOAD_FNV',1),
                        header.replace('UINT64_C(0x','UINT64_C(0X',1)):
                with self.subTest(header=name),self.assertRaises(AssertionError):
                    s.shadow_pin_rows(self.source,**{name:bad})
        bad=self.source.replace('CURRENT_SONIC_80105_D8_PAYLOAD_FNV','CURRENT_SONIC_89999_D8_PAYLOAD_FNV')
        with self.assertRaises(AssertionError):s.shadow_pin_rows(bad)

    def test_well_formed_but_false_generated_header_rejected_by_master_derivation(self):
        import importlib
        for family in ('sonic','protron'):
            s.master_payloads(family)  # imports the explicit selected compatibility
            compat=importlib.import_module('current_'+family+'_compatibility')
            real=compat.read
            original=real(s.ROOT,compat.HEADER)
            bad=re.sub(rb'UINT64_C\(0x[0-9a-f]{16}\)',b'UINT64_C(0x0000000000000000)',original,count=1)
            self.assertNotEqual(bad,original)
            with patch.object(compat,'read',side_effect=lambda root,name,*args:bad if name==compat.HEADER else real(root,name,*args)):
                with self.subTest(family=family),self.assertRaises(AssertionError):s.master_payloads(family)

    def test_current_source_slot_coverage_and_payload_changes_rejected(self):
        mutations=(('105,563','105,562'),('225,469','225,470'),
                   ('0x66cdc314034152a6','0x66cdc314034152a7'),
                   ('0x9115d94f761d41b6','0x9115d94f761d41b7'),
                   ('CURRENT_SONIC_80105_D8_PAYLOAD_FNV','UINT64_C(0x0000000000000000)'))
        for old,new in mutations:
            self.assertIn(old,self.source)
            with self.subTest(old=old),self.assertRaises(AssertionError):s.verify_master_rows(self.source.replace(old,new,1))

    def test_prior_structure_still_rejected_despite_current_payload_authoring(self):
        prior=subprocess.check_output(['git','-C',str(s.ROOT),'show','HEAD:src/render_mirror.c'],text=True)
        self.assertEqual(len(s.compare_previous_shadow_pins(self.source,prior,17)),45)
        for old,new in (('225,469','225,470'),('105,563','105,562'),
                        ('0x9115d94f761d41b6','0x9115d94f761d41b7')):
            with self.subTest(old=old),self.assertRaises(AssertionError):
                s.compare_previous_shadow_pins(self.source,prior.replace(old,new,1),17)


if __name__=='__main__':unittest.main()
