import os
import importlib.util
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ROOT / 'experimental/level2-family/src/b313_redvent_pair.inc'
HARNESS = r'''
#define _POSIX_C_SOURCE 200809L
#define B313_FAMILY_CANVAS_DIAGNOSTIC 1
#include "b313_redvent_pair.inc"
#include <assert.h>
int main(int argc,char **argv) {
 unsetenv("BUILDING313_REDVENT_PAIR_ENABLE");
 unsetenv("BUILDING313_REDVENT_PAIR_ASSET_DIR");
 assert(rp_member(339)==0&&rp_member(348)==1&&rp_member(340)==-1);
 assert(rp_begin(true,true)&&!rp.enabled&&rp_current());
 setenv("BUILDING313_REDVENT_PAIR_ENABLE","true",1);
 assert(!rp_begin(true,true));
 setenv("BUILDING313_REDVENT_PAIR_ENABLE","1",1);
 assert(!rp_begin(true,false));
 assert(!rp_begin(true,true)); /* No directory. */
 assert(rp_begin(false,true)&&!rp.enabled); /* Parent cannot be enabled here. */
 if(argc>1) {
  setenv("BUILDING313_REDVENT_PAIR_ASSET_DIR",argv[1],1);
  bool expected=argc>2&&!strcmp(argv[2],"valid");
  if(argc>4) {
   uint8_t source[672];
   for(unsigned i=0;i<2;i++) {
    FILE *f=fopen(argv[3+i],"rb");assert(f);
    assert(fread(source,1,672,f)==672&&fgetc(f)==EOF);fclose(f);rp_bind(rp_ids[i],source);
   }
  }
  assert(rp_begin(true,true)==expected);
  if(!expected&&rp.failed)assert(!rp.enabled&&!rp.ready&&!rp.rgba[0]&&!rp.rgba[1]);
  if(expected) {
   assert(rp.enabled&&rp.ready&&rp_current()&&rp.rgba[0]&&rp.rgba[1]);
   setenv("BUILDING313_REDVENT_PAIR_ASSET_DIR","changed-mid-frame",1);
   assert(!rp_current());
   setenv("BUILDING313_REDVENT_PAIR_ASSET_DIR",argv[1],1);
   assert(rp_current());
   setenv("BUILDING313_REDVENT_PAIR_ENABLE","0",1);assert(!rp_current());
   assert(rp_begin(true,true)&&!rp.enabled&&!rp.ready&&!rp.rgba[0]&&!rp.rgba[1]);
   uint8_t bad[672]={0};rp_bind(339,bad);
   setenv("BUILDING313_REDVENT_PAIR_ENABLE","1",1);assert(!rp_begin(true,true));
   rp_map_begin();assert(!rp.source_fault);
  }
 }
 rp_free();return 0;
}
'''


@unittest.skipUnless(shutil.which('cc'), 'C compiler required')
class RedventLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        source = cls.root / 'test.c'
        source.write_text(HARNESS)
        cls.binary = cls.root / 'test'
        subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-I' + str(INCLUDE.parent), str(source), '-o', str(cls.binary)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_harness(self, *args):
        subprocess.run([str(self.binary), *map(str, args)], check=True, capture_output=True)

    def test_default_off_exact_toggle_and_parent(self):
        self.run_harness()

    def test_missing_assets_rejected(self):
        self.run_harness(self.root / 'missing', 'invalid')

    def test_malformed_assets_rejected(self):
        d = self.root / 'bad'
        d.mkdir(exist_ok=True)
        (d / 'terrain-shapesz-339-8.hda').write_bytes(b'HDR1' + bytes(24))
        self.run_harness(d, 'invalid')

    def test_compile_disabled_ignores_enable_variable(self):
        source = self.root / 'disabled.c'
        source.write_text('#define _POSIX_C_SOURCE 200809L\n#define B313_FAMILY_CANVAS_DIAGNOSTIC 0\n#include "b313_redvent_pair.inc"\n#include <assert.h>\nint main(void){setenv("BUILDING313_REDVENT_PAIR_ENABLE","1",1);assert(rp_setting()==0);assert(rp_begin(true,true)&&!rp.enabled);rp_free();return 0;}\n')
        binary = self.root / 'disabled'
        subprocess.run(['cc', '-std=c99', '-I' + str(INCLUDE.parent), str(source), '-o', str(binary)], check=True, capture_output=True)
        subprocess.run([str(binary)], check=True)

    def test_launcher_requires_hd_and_explicit_pair(self):
        spec = importlib.util.spec_from_file_location('family_launcher', ROOT / 'scripts/launch_level2_family.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = SimpleNamespace(data=str(self.root), binary=str(self.binary), profile=str(self.root / 'profile'), hd=False, launch=False, redvent_pair=str(self.root / 'pair'))
        with patch.object(module, 'verify_assets', return_value=52), patch.object(module, 'verify_redvent_pair', return_value=self.root / 'pair'):
            with self.assertRaisesRegex(ValueError, 'requires --hd'):
                module.build_plan(args, inherited={})
            args.hd = True
            plan, environment = module.build_plan(args, inherited={})
            self.assertTrue(plan['redvent_pair_enabled'])
            self.assertEqual(plan['redvent_assets_sha256_verified'], 2)
            self.assertEqual(environment['BUILDING313_REDVENT_PAIR_ENABLE'], '1')
            self.assertFalse((self.root / 'profile').exists())
            args.redvent_pair = None
            plan, environment = module.build_plan(args, inherited={'BUILDING313_REDVENT_PAIR_ENABLE': '1', 'BUILDING313_REDVENT_PAIR_ASSET_DIR': 'stray'})
            self.assertFalse(plan['redvent_pair_enabled'])
            self.assertNotIn('BUILDING313_REDVENT_PAIR_ENABLE', environment)

    def test_pixel_callback_and_snapshot_have_config_guards(self):
        source = (INCLUDE.parent / 'b313_family_ground_mirror.inc').read_text()
        self.assertIn('if(!rp_current()||!fg.row||', source)
        self.assertIn('return rp_current()&&fg.enabled', source)
        self.assertIn('member<10?fg.rgba[member]:rp.rgba[member-10]', source)
        self.assertIn('rp_bind(id,data);', source)
        self.assertIn('{if(!fg_config_current())return false;if(fg.enabled&&fg.pass', source)
        self.assertIn('if(!rp_current()||off>=64000||!fg.enabled||!fg.done', source)
        for name, state in [('fg_cliff_support_current', 'fl'), ('fg_corner_support_current', 'fk'), ('fg_static340_support_current', 'fs340')]:
            start = source.index('static bool ' + name + '(void)')
            body = source[start:source.index('\n}', start)]
            self.assertIn('return rp_current()&&' + state + '.support_ready&&', body)


if __name__ == '__main__':
    unittest.main()
