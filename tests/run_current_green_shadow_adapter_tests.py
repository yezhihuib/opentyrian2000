#!/usr/bin/env python3
"""Independent frozen Green shadow pin adapter tests; no native build or assets."""
import re
import unittest
from pathlib import Path
from run_sonic_quadrant_shadow_tests import resolve_current_payload_pins
from run_ten_weapon_shadow_tests import PINS

ROOT = Path(__file__).resolve().parents[1]


def green_rows(source, header):
    expanded = resolve_current_payload_pins(source, header)
    rows = re.findall(r'^ \{(21[4-7]),(\d+),UINT64_C\(0x([0-9a-f]+)\),UINT64_C\(0x([0-9a-f]+)\),0,0\}', expanded, re.M)
    actual = [(int(i), int(slot), int(src,16), int(rgba,16)) for i,slot,src,rgba in rows]
    if actual != list(PINS[-4:]):
        raise AssertionError('Independent frozen Green source/slot/payload mismatch')
    return actual


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT/'src/render_mirror.c').read_text()
        self.header = (ROOT/'src/current_art_payload_pins.h').read_text()

    def test_approved_four_independent_frozen_pins(self):
        self.assertEqual(len(green_rows(self.source,self.header)),4)

    def test_unknown_macro_rejected(self):
        with self.assertRaises(AssertionError):
            resolve_current_payload_pins('CURRENT_GREEN_89999_RGBA', self.header)

    def test_tampered_payload_rejected(self):
        old = '#define CURRENT_GREEN_80214_RGBA UINT64_C(0xa1bc11025ec02c94)'
        self.assertIn(old,self.header)
        with self.assertRaises(AssertionError):
            green_rows(self.source,self.header.replace(old,old.replace('a1bc11025ec02c94','a1bc11025ec02c95')))

    def test_source_or_slot_mutation_rejected(self):
        for old,new in [('0x17da292b54af394c','0x17da292b54af394d'),('{214,182,','{214,183,')]:
            self.assertIn(old,self.source)
            with self.subTest(old=old),self.assertRaises(AssertionError):
                green_rows(self.source.replace(old,new),self.header)

if __name__=='__main__':unittest.main()
