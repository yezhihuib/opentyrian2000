"""Finite40 pure-source adapters; no compilation, fixture creation or gameplay."""
import ast
import builtins
import hashlib
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from aircraft169_inherited_native_validation import (
    PINS, adapt_scout, adapt_fighter, adapt_interceptor, adapt_driver,
)
from aircraft169_newshf_native_validation import build_source

ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = {'scout164': adapt_scout, 'fighter165': adapt_fighter,
            'interceptor166': adapt_interceptor}
PAIRS = {
    'scout164': [
        ('GLOBAL_NEWSHF_RESOURCE_COUNT==31&&COUNTOF(newshf_profiles)==18',
         'GLOBAL_NEWSHF_RESOURCE_COUNT==40&&COUNTOF(newshf_profiles)==21'),
        ('!global_newshf_phase_bank_matches(31,b10)&&!global_newshf_phase_bank_matches(32,b10)',
         '!global_newshf_phase_bank_matches(40,b10)&&!global_newshf_phase_bank_matches(41,b10)'),
        ('!global_newshf_group_ready(31)&&!global_newshf_group_ready(32)',
         '!global_newshf_group_ready(40)&&!global_newshf_group_ready(41)'),
        ('mode==0?28:mode==1?18:31', 'mode==0?28:mode==1?18:40')],
    'fighter165': [
        ('GLOBAL_NEWSHF_RESOURCE_COUNT==34&&COUNTOF(newshf_profiles)==19',
         'GLOBAL_NEWSHF_RESOURCE_COUNT==40&&COUNTOF(newshf_profiles)==21'),
        ('const unsigned invalid[]={34,63,64,UINT_MAX}',
         'const unsigned invalid[]={40,63,64,UINT_MAX}')],
    'interceptor166': [
        ('GLOBAL_NEWSHF_RESOURCE_COUNT==37&&COUNTOF(newshf_profiles)==20',
         'GLOBAL_NEWSHF_RESOURCE_COUNT==40&&COUNTOF(newshf_profiles)==21'),
        ('const unsigned invalid[]={37,63,64,UINT_MAX}',
         'const unsigned invalid[]={40,63,64,UINT_MAX}'),
        ('for(unsigned p=0;p<37;p++)', 'for(unsigned p=0;p<40;p++)')],
}
FILES = ['aircraft169_newshf_native_validation.py',
         'aircraft169_inherited_native_validation.py',
         'aircraft169_aircraft_diagnostics.py', 'aircraft169_gameplay.py',
         'aircraft169_native_blend_trace.py', 'test_aircraft169_native_adapter.py']


class FiniteNativeAdapterTests(unittest.TestCase):
    def test_exact_inherited_harness_and_only_declared_changes(self):
        for family, adapt in ADAPTERS.items():
            p = ROOT / ('tests/' + family + '_newshf_native_validation.c')
            before = p.read_bytes()
            expected = before.decode()
            for a, b in PAIRS[family]:
                self.assertEqual(expected.count(a), 2 if a == 'for(unsigned p=0;p<37;p++)' else 1)
                expected = expected.replace(a, b)
            self.assertEqual(adapt(before), expected.encode())
            self.assertEqual(p.read_bytes(), before)

    def test_changed_original_harness_rejected(self):
        for family, adapt in ADAPTERS.items():
            b = (ROOT / ('tests/' + family + '_newshf_native_validation.c')).read_bytes()
            self.assertIn(b'CHECK(local>0)', b)
            for candidate in (b + b'\n', b.replace(b'CHECK(local>0)', b'CHECK(local>=0)')):
                with self.assertRaises(AssertionError):
                    adapt(candidate)

    def test_all_original_native_inputs_remain_pinned(self):
        for name, h in PINS.items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), h, name)

    def test_prior_high_bits_and_resource_loops_preserved(self):
        cases = {
            'fighter165': ('for(unsigned phase=31;phase<34;phase++)',
                           'UINT64_C(0x380000000)', 'global_newshf_rgba[31+mode-12][31]^=1'),
            'interceptor166': ('for(unsigned phase=34;phase<37;phase++)',
                              'UINT64_C(0x1c00000000)', 'global_newshf_rgba[34+mode-12][31]^=1'),
        }
        for family, markers in cases.items():
            s = ADAPTERS[family]((ROOT / ('tests/' + family + '_newshf_native_validation.c')).read_bytes()).decode()
            for marker in markers:
                self.assertIn(marker, s)

    def test_native_driver_generated_source_and_private_payload_order(self):
        s = build_source(ROOT)
        ast.parse(s)
        self.assertIn("str(ROOT/'tests/aircraft169_newshf_native_validation.c')", s)
        self.assertIn("+raw[177028:177105]+raw[176720:176797]+raw[176797:176874]+(a.original_data/'newshi.shp').read_bytes()+raw[187269:187346]", s)
        self.assertIn('1e189a8f99ab90040bb5967779232f54db4bf8bf1bb732cbfb94a21ad845be43', s)
        self.assertIn('[9,6,1,2,10,3,3,3,3]', s)
        self.assertIn("'newshf-interceptor166','newshf-aircraft169'", s)
        self.assertIn("if mode=='no-interceptor166' and group=='newshf-interceptor166':continue", s)
        self.assertIn('assert shutil.disk_usage(a.out).free>512*1024**2', s)
        self.assertIn('test_unchanged and assets_unchanged and originals_unchanged', s)

    def test_inherited_drivers_generate_without_native_execution(self):
        for family in ADAPTERS:
            suite = family + '_newshf'
            path = ROOT / ('tests/' + suite + '_native_validation.py')
            adapted = Path('/not-executed') / (family + '-native-adapted.c')
            raw = adapt_driver(path.read_text(), suite, adapted)
            ast.parse(raw)
            captured = []
            # The original driver may generate Python source, but that generated
            # main is intercepted: no output directory, compile or run occurs.
            ns = {'__name__': 'adapter_source_test', '__file__': str(path),
                  'compile': lambda source, *args: source,
                  'exec': lambda source, *args: captured.append(source)}
            builtins.exec(raw, ns)
            with patch.object(sys, 'argv', [str(path), '--source-root', str(ROOT), '--skip-build']):
                ns['main']()
            self.assertEqual(len(captured), 1)
            generated = captured[0]
            ast.parse(generated)
            self.assertIn(str(adapted), generated)
            if family == 'interceptor166':
                self.assertIn('[9,6,1,2,10,3,3,3,3]', generated)
                self.assertIn("'newshf-interceptor166','newshf-aircraft169'", generated)
                self.assertIn('+raw[176797:176874]+raw[176720:176797]', generated)

    def test_candidate_native_phase_identity_and_old_family_isolation(self):
        s = (ROOT / 'tests/aircraft169_newshf_native_validation.c').read_text()
        for marker in ('current_record=169', 'profile==20',
                       'GLOBAL_NEWSHF_RESOURCE_COUNT==40&&COUNTOF(newshf_profiles)==21',
                       'native_counts[3]={260,238,238}', 'for(unsigned phase=37;phase<40;phase++)',
                       'UINT64_C(0xe000000000)', 'const unsigned invalid[]={40,63,64,UINT_MAX}',
                       'family==2?165:family==3?166:302', 'family<4',
                       '"no-interceptor166"', 'global_newshf_rgba[37+mode-12][31]^=1'):
            self.assertIn(marker, s)
        for obsolete in ('profile==19', 'newshf_profiles[19]', '0x1c00000000', '33+pose'):
            self.assertNotIn(obsolete, s)

    def test_python_sources_parse_and_gameplay_scope_is_explicit_e1_to_e3(self):
        for name in FILES:
            ast.parse((ROOT / 'tests' / name).read_text(), filename=name)
        for name in ('aircraft169_aircraft_diagnostics.py', 'aircraft169_gameplay.py',
                     'aircraft169_native_blend_trace.py'):
            s = (ROOT / 'tests' / name).read_text()
            self.assertIn("p.add_argument('--episode',type=int,choices=(1,2,3),required=True)", s)
            self.assertIn("p.add_argument('--level',type=int,required=True)", s)
            self.assertIn("p.add_argument('--start',type=int,required=True)", s)
            self.assertNotIn('E5', s)

    def test_gameplay_keeps_all_37_prior_resources_and_native_oracles(self):
        s = (ROOT / 'tests/aircraft169_gameplay.py').read_text()
        for marker in ("'fighter165_newshf','interceptor166_newshf'", 'assert len(prior)==37',
                       'bases=(79,77,115)', 'all(native.values())', 'classic_equal',
                       'state/RNG', 'owner_dependent_blend_log_equal'):
            self.assertIn(marker, s)
        trace = (ROOT / 'tests/aircraft169_native_blend_trace.py').read_text()
        self.assertIn("'native-blend-writes.tsv','state.tsv'", trace)
        self.assertIn('all(equal.values()) and count>0', trace)

    def test_diagnostics_high_bit_mutations_do_not_target_old_resources(self):
        s = (ROOT / 'tests/aircraft169_aircraft_diagnostics.py').read_text()
        for marker in ('phase>=37&&phase<=39', 'profile==20', 'enemytype==169',
                       "['aircraft37','aircraft38','aircraft39'", 'phase in (37,38,39)',
                       '"aircraft",8', 'atoi(which+8)', "'natural_state_equality_claimed':False"):
            self.assertIn(marker, s)
        for obsolete in ('profile==19', 'phase>=34', 'E5', 'enemytype==166'):
            self.assertNotIn(obsolete, s)


if __name__ == '__main__':
    unittest.main()
