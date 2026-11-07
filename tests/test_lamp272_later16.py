import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'experimental/level2-family/src/lamp272_family_mirror.inc'
SCOPE = SOURCE.with_name('lamp272_later16_scope.inc')
EXPECTED = [(22,356,66),(23,356,138),(137,1168,138),(146,1196,138),(147,1196,114),(49,440,138),(50,440,66),
            (267,2176,114),(268,2176,138),(481,4668,114),(482,4668,138),(483,4668,162),(484,4668,186),
            (486,4696,114),(487,4696,138),(488,4696,162),(489,4696,186),(572,6124,162),(573,6124,138),
            (586,6152,162),(587,6152,138),(604,6208,186),(605,6208,114)]


def function(text, name):
    start = text.index('static ', text.index(name) - 30)
    # The isolated predicates have one braced function body and no nested braces.
    end = text.index('\n}', start) + 2
    return text[start:end]


def harness():
    text = SOURCE.read_text()
    table = re.search(r'static const struct \{unsigned event,time;int x;\} private_lamp272_origins\[23\]=\{.*?\n\};', text, re.S).group()
    funcs = '\n'.join(function(text, name) for name in ('private_lamp272_origin(', 'private_lamp272_mode(', 'private_lamp272_origin_enabled('))
    return r'''
#define _POSIX_C_SOURCE 200809L
#define B313_FAMILY_CANVAS_DIAGNOSTIC 1
#define COUNTOF(x) (sizeof(x)/sizeof(*(x)))
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef uint8_t Uint8;
struct JE_EventRecType {uint16_t eventtime;uint8_t eventtype;int16_t eventdat,eventdat2;int8_t eventdat3,eventdat5,eventdat6;uint8_t eventdat4;};
struct JE_EventRecType eventRec[731];
unsigned episodeNum=1,lvlFileNum=2,mainLevel=6,maxEvent=731;
char levelName[16]="ASTEROID2";
bool play_demo=false,game_probe_enabled=false,asset_debug_enabled=false;
void *demo_file=NULL;
#include "lamp272_later16_scope.inc"
static struct {unsigned mode;bool later_three,middle_pair;} private_lamp272_life;
''' + table + '\n' + funcs + r'''
int main(int argc,char **argv) {
 unsetenv("LAMP272_LATER_SIXTEEN_ENABLE");unsetenv("LAMP272_FAMILY_CANVAS_ENABLE");unsetenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 assert(!lamp272_later16_requested()&&private_lamp272_mode()==0);
 setenv("LAMP272_LATER_SIXTEEN_ENABLE","1",1);assert(lamp272_later16_requested());assert(private_lamp272_mode()==0);
 setenv("BUILDING313_FAMILY_CANVAS_ENABLE","1",1);assert(private_lamp272_mode()==4);
 setenv("LAMP272_FAMILY_CANVAS_ENABLE","1",1);assert(private_lamp272_mode()==6);
 setenv("LAMP272_LATER_SIXTEEN_ENABLE","true",1);assert(!lamp272_later16_requested()&&private_lamp272_mode()==2);
 setenv("LAMP272_LATER_SIXTEEN_ENABLE","1",1);
 lvlFileNum=1;assert(!lamp272_later16_requested());lvlFileNum=2;
 mainLevel=5;assert(!lamp272_later16_requested());mainLevel=6;
 episodeNum=2;assert(!lamp272_later16_requested());episodeNum=1;
 play_demo=true;assert(!lamp272_later16_requested());play_demo=false;
 game_probe_enabled=true;assert(!lamp272_later16_requested());game_probe_enabled=false;
 asset_debug_enabled=true;assert(!lamp272_later16_requested());asset_debug_enabled=false;
 demo_file=eventRec;assert(!lamp272_later16_requested());demo_file=NULL;
 strcpy(levelName,"ASTEROID1");assert(!lamp272_later16_requested());strcpy(levelName,"ASTEROID2");
 for(unsigned mode=0;mode<=6;mode+=2) for(unsigned flags=0;flags<4;flags++) {
  private_lamp272_life.mode=mode;private_lamp272_life.later_three=flags&1;private_lamp272_life.middle_pair=flags&2;
  assert(!private_lamp272_origin_enabled(-1)&&!private_lamp272_origin_enabled(23));
  unsigned mask=0;
  for(int i=0;i<23;i++) {
   bool expected=i>=7?(mode&4)!=0:(mode&2)&&(i<2||(i<5?(flags&1):(flags&2)));
   assert(private_lamp272_origin_enabled(i)==expected);
   assert(private_lamp272_origin(private_lamp272_origins[i].event)==i);
   unsigned bit=1u<<(unsigned)i;assert(!(mask&bit));mask|=bit;
  }
 }
 assert(!lamp272_later16_stream_matches(NULL));
 assert(!lamp272_later16_stream_matches(eventRec));
 if(argc>1) {
  FILE *f=fopen(argv[1],"rb");assert(f);uint8_t b[11];
  for(unsigned i=0;i<731;i++) {assert(fread(b,1,11,f)==11);eventRec[i]=(struct JE_EventRecType){(uint16_t)(b[0]|b[1]<<8),b[2],(int16_t)(b[3]|b[4]<<8),(int16_t)(b[5]|b[6]<<8),(int8_t)b[7],(int8_t)b[8],(int8_t)b[9],b[10]};}
  assert(fgetc(f)==EOF);fclose(f);assert(lamp272_later16_stream_matches(eventRec));
  for(unsigned i=0;i<23;i++){const struct JE_EventRecType *r=&eventRec[private_lamp272_origins[i].event];assert(r->eventtime==private_lamp272_origins[i].time&&r->eventtype==6&&r->eventdat==272&&r->eventdat2==private_lamp272_origins[i].x&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6);}
  eventRec[700].eventdat^=1;assert(!lamp272_later16_stream_matches(eventRec));eventRec[700].eventdat^=1;
  maxEvent=730;assert(!lamp272_later16_stream_matches(eventRec));maxEvent=731;
  struct JE_EventRecType copy[731];memcpy(copy,eventRec,sizeof copy);assert(!lamp272_later16_stream_matches(copy));
 }
 return 0;
}
'''


class LaterLampTests(unittest.TestCase):
    def test_exact_append_only_origins_and_reused_assets(self):
        text = SOURCE.read_text()
        table = re.search(r'private_lamp272_origins\[23\]=\{(.*?)\n\};', text, re.S).group(1)
        self.assertEqual([tuple(map(int,x)) for x in re.findall(r'\{(\d+),(\d+),(\d+)\}', table)], EXPECTED)
        self.assertEqual(len({r[0] for r in EXPECTED}), 23)
        self.assertIn('1u<<(unsigned)origin', text)
        manifest = json.loads((ROOT / 'assets/hd/level2-family-v1/MANIFEST.json').read_text())
        self.assertEqual(manifest['file_count'], 52)
        for n in (229,231,233,235):
            self.assertTrue((ROOT / f'assets/hd/packs/asteroid1-ten-v1/enemy-newshs-{n}-8.hda').is_file())

    @unittest.skipUnless(shutil.which('cc'), 'C compiler required')
    def test_compiled_origin_modes_scope_and_bad_stream(self):
        with tempfile.TemporaryDirectory() as temp:
            c = Path(temp)/'test.c';c.write_text(harness());binary=Path(temp)/'test'
            subprocess.run(['cc','-std=c99','-Wall','-Wextra','-I'+str(SCOPE.parent),str(c),'-o',str(binary)],check=True,capture_output=True)
            subprocess.run([str(binary)],check=True,capture_output=True)

    def test_launcher_explicit_and_default_off(self):
        spec=importlib.util.spec_from_file_location('launcher',ROOT/'scripts/launch_level2_family.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);binary=root/'game';binary.write_text('not executed');binary.chmod(0o700)
            args=SimpleNamespace(data=str(root),binary=str(binary),profile=str(root/'profile'),hd=False,launch=False,later_lamps=True)
            with patch.object(module,'verify_assets',return_value=52):
                with self.assertRaisesRegex(ValueError,'requires --hd'):module.build_plan(args,inherited={})
                args.hd=True;plan,env=module.build_plan(args,inherited={});self.assertTrue(plan['later_lamps_enabled']);self.assertEqual(env['LAMP272_LATER_SIXTEEN_ENABLE'],'1');self.assertEqual(plan['family_environment_count'],24)
                args.later_lamps=False;plan,env=module.build_plan(args,inherited={'LAMP272_LATER_SIXTEEN_ENABLE':'1'});self.assertFalse(plan['later_lamps_enabled']);self.assertNotIn('LAMP272_LATER_SIXTEEN_ENABLE',env)
                self.assertFalse((root/'profile').exists())

    def test_lifetime_and_stream_guards_remain_bound(self):
        text=SOURCE.read_text()
        self.assertIn('private_lamp272_mode()==private_lamp272_life.mode',text)
        self.assertIn('((private_lamp272_life.mode&4u)&&!lamp272_later16_stream_matches(events))',text)
        self.assertIn('Allocation failure also consumes origin.',text)
        self.assertIn('private_lamp272_life.consumed|=bit;',text)
        self.assertNotIn('LATE_REUSE_FAMILY_ENABLE',text+SCOPE.read_text())


if __name__=='__main__':unittest.main()
