"""Current finite identity adapter and extracted entry-prefix checks.

Native prefix stubs deliberately do not model downstream rendering/session code.
"""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
import current_newshf_identity_validation as adapter
from global_talon_reconstruction import extract
ROOT = Path(__file__).resolve().parents[1]

SUPPORT = r'''
#include <stdio.h>
static int requested, active, reset_calls, frame_calls, next_calls, sequence;
static int enemy_reuse_observe_requested(void) { return requested; }
static int enemy_reuse_observe_active(void) { return active; }
static void render_mirror_hud_reset(void) { reset_calls++; sequence=sequence*10+1; }
static void render_mirror_newshf_validation_frame(void) { frame_calls++; sequence=sequence*10+2; }
static void global_newshf_tick_begin(void) { next_calls++; sequence=sequence*10+3; }
'''
MAIN = r'''
#define REQUIRE(x) do { if(!(x)) {fprintf(stderr,"LIFECYCLE CHECK: %s\n",#x); return 9;} } while(0)
int main(void) {
 for(requested=0;requested<=1;requested++) for(active=0;active<=1;active++) {
  reset_calls=frame_calls=next_calls=sequence=0;
  render_mirror_begin();
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
  if(requested&&!active) {REQUIRE(reset_calls==1); REQUIRE(frame_calls==0); REQUIRE(next_calls==0); REQUIRE(sequence==1);}
  else
#endif
  {REQUIRE(reset_calls==0); REQUIRE(frame_calls==1); REQUIRE(next_calls==1); REQUIRE(sequence==23);}
 }
 puts("PASS extracted begin prefix: 4 requested/active states"); return 0;
}
'''

def native(prefix, flags=(), tail=' global_newshf_tick_begin();\n'):
    with tempfile.TemporaryDirectory(prefix='current-identity-prefix-') as tmp:
        tmp = Path(tmp)
        source = tmp/'prefix.c'
        source.write_text(SUPPORT + prefix + tail + '}\n' + MAIN)
        exe = tmp/'prefix'
        command = ['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-unused-function',*flags,str(source),'-o',str(exe)]
        subprocess.run(command,check=True,capture_output=True)
        return subprocess.run([str(exe)],capture_output=True,text=True)

class CurrentIdentityAdapterTests(unittest.TestCase):
    def setUp(self):
        self.begin = extract((ROOT/'src/render_mirror.c').read_text(),'render_mirror_begin')
        self.raw = (ROOT/'tests/newshf_identity_validation.py').read_bytes()

    def test_exact_current_contract_and_unique_frame(self):
        self.assertEqual(adapter.validate_begin(self.begin),adapter.PREFIX)
        self.assertEqual(self.begin.count('render_mirror_newshf_validation_frame();'),1)

    def test_adapter_changes_only_root_and_stale_assertion(self):
        current = adapter.transformed(ROOT,self.raw)
        original = self.raw.decode()
        expected = original.replace('ROOT = Path(__file__).resolve().parents[1]',f'ROOT = Path({str(ROOT)!r})')
        expected = expected.replace("assert begin.split('{',1)[1].lstrip().startswith('render_mirror_newshf_validation_frame();')",'_validate_current_begin(begin)')
        self.assertEqual(current,expected)
        self.assertEqual(hashlib.sha256((ROOT/'tests/newshf_identity_validation.c').read_bytes()).hexdigest(),adapter.HARNESS_SHA)

    def test_changed_historical_driver_rejected(self):
        with self.assertRaises(AssertionError): adapter.transformed(ROOT,self.raw+b'\n')

    def test_invalid_current_preludes_rejected_and_fresh_restoration(self):
        hook=' render_mirror_newshf_validation_frame();\n'
        mutants = [self.begin.replace(hook,''), self.begin.replace(hook,hook*2),
                   self.begin.replace('render_mirror_hud_reset();return;','render_mirror_hud_reset();'),
                   self.begin.replace('!enemy_reuse_observe_active()','enemy_reuse_observe_active()'),
                   self.begin.replace(' global_newshf_tick_begin();', ' global_newshf_tick_begin();\n'+hook).replace(hook,'',1)]
        for mutant in mutants:
            with self.subTest(mutant=hashlib.sha256(mutant.encode()).hexdigest()):
                with self.assertRaises(AssertionError): adapter.validate_begin(mutant)
                self.assertEqual(adapter.validate_begin(self.begin),adapter.PREFIX)

    def test_native_prefix_three_compile_modes(self):
        prefix=adapter.validate_begin(self.begin)
        for flags in [(),('-DENEMY_REUSE_HD_PROTOTYPE=0',),('-DENEMY_REUSE_HD_PROTOTYPE=1',)]:
            with self.subTest(flags=flags):
                result=native(prefix,flags)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn('PASS extracted begin prefix',result.stdout)

    def test_native_mutation_sensitivity(self):
        prefix=adapter.validate_begin(self.begin)
        hook=' render_mirror_newshf_validation_frame();\n'
        mutants={
          'no_frame':(prefix.replace(hook,''),' global_newshf_tick_begin();\n'),
          'frame_after_next':(prefix.replace(hook,' global_newshf_tick_begin();\n'+hook),''),
          'no_rejection':(prefix.replace('render_mirror_hud_reset();return;','render_mirror_hud_reset();'),' global_newshf_tick_begin();\n'),
          'frame_before_rejection':(prefix.replace('{\n','{\n'+hook,1).rsplit(hook,1)[0],' global_newshf_tick_begin();\n'),
        }
        for name,(mutant,tail) in mutants.items():
            with self.subTest(name=name):
                result=native(mutant,('-DENEMY_REUSE_HD_PROTOTYPE=1',),tail)
                self.assertEqual(result.returncode,9,result.stderr)
                self.assertIn('LIFECYCLE CHECK:',result.stderr)

if __name__=='__main__': unittest.main()
