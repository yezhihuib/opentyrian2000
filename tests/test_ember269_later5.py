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
SOURCE = ROOT / 'experimental/level2-family/src/ember269_family_mirror.inc'
SCOPE = SOURCE.with_name('ember269_later5_scope.inc')
EXPECTED = [(157,1252,114),(349,3128,114),(351,3128,186),(479,4668,42),(480,4668,66),(485,4668,258)]


def function(text, name):
    start = text.index('static ', text.index(name) - 30)
    # Extract through the unindented function closing brace.
    end = text.index('\n}', start) + 2
    return text[start:end]


def harness():
    text = SOURCE.read_text()
    table = re.search(r'static const struct \{unsigned event,time;int x;\} private_ember269_origins\[6\]=\{.*?\n\};', text, re.S).group()
    funcs = '\n'.join(function(text, name) for name in ('private_ember269_origin(', 'private_ember269_mode(', 'private_ember269_origin_enabled(', 'private_ember269_event_matches('))
    begin = re.search(r'uint64_t render_mirror_ember269_event_begin\(.*?\n\}', text, re.S).group()
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
#include "ember269_later5_scope.inc"
static struct {
 unsigned mode;unsigned char consumed[6];const struct JE_EventRecType *events;
 uint64_t serial,epoch;bool exhausted;
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot;} call;
} private_ember269_life;
unsigned eventLoc,curLoc;
static unsigned private_ember269_mode(void);
static bool private_ember269_scope(void){return private_ember269_mode()==private_ember269_life.mode&&!private_ember269_life.exhausted;}
static void private_ember269_fail(void){}
static void private_ember269_log(const char *p,int s,unsigned e,unsigned b,int part,int ok){(void)p;(void)s;(void)e;(void)b;(void)part;(void)ok;}

''' + table + '\n' + funcs + '\n' + begin + r'''
int main(int argc,char **argv) {
 unsetenv("EMBER269_LATER_FIVE_ENABLE");unsetenv("EMBER269_FAMILY_CANVAS_ENABLE");unsetenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 assert(!ember269_later5_requested()&&private_ember269_mode()==0);
 setenv("EMBER269_LATER_FIVE_ENABLE","1",1);assert(ember269_later5_requested());assert(private_ember269_mode()==0);
 setenv("BUILDING313_FAMILY_CANVAS_ENABLE","1",1);assert(private_ember269_mode()==4);
 setenv("EMBER269_FAMILY_CANVAS_ENABLE","1",1);assert(private_ember269_mode()==6);
 setenv("EMBER269_LATER_FIVE_ENABLE","true",1);assert(!ember269_later5_requested()&&private_ember269_mode()==2);
 setenv("EMBER269_LATER_FIVE_ENABLE","1",1);
 lvlFileNum=1;assert(!ember269_later5_requested());lvlFileNum=2;
 mainLevel=5;assert(!ember269_later5_requested());mainLevel=6;
 episodeNum=2;assert(!ember269_later5_requested());episodeNum=1;
 play_demo=true;assert(!ember269_later5_requested());play_demo=false;
 game_probe_enabled=true;assert(!ember269_later5_requested());game_probe_enabled=false;
 asset_debug_enabled=true;assert(!ember269_later5_requested());asset_debug_enabled=false;
 demo_file=eventRec;assert(!ember269_later5_requested());demo_file=NULL;
 strcpy(levelName,"ASTEROID1");assert(!ember269_later5_requested());strcpy(levelName,"ASTEROID2");
 for(unsigned mode=0;mode<=6;mode+=2) {
  private_ember269_life.mode=mode;
  assert(!private_ember269_origin_enabled(-1)&&!private_ember269_origin_enabled(6));
  for(int i=0;i<6;i++) {
   bool expected=(mode&(i==0?2u:4u))!=0;
   assert(private_ember269_origin_enabled(i)==expected);
   assert(private_ember269_origin(private_ember269_origins[i].event)==i);
  }
 }
 assert(private_ember269_origin(0)==-1&&private_ember269_origin(731)==-1&&private_ember269_origin(UINT32_MAX)==-1);
 private_ember269_life.events=eventRec;
 for(unsigned i=0;i<6;i++) {
  unsigned n=private_ember269_origins[i].event;
  eventRec[n]=(struct JE_EventRecType){private_ember269_origins[i].time,6,269,private_ember269_origins[i].x,0,0,0,0};
  assert(private_ember269_event_matches(n));
  eventRec[n].eventdat2++;assert(!private_ember269_event_matches(n));eventRec[n].eventdat2--;
  eventRec[n].eventdat6=1;assert(!private_ember269_event_matches(n));eventRec[n].eventdat6=0;
 }
 assert(!private_ember269_event_matches(0)&&!private_ember269_event_matches(UINT32_MAX));
 maxEvent=730;assert(!private_ember269_event_matches(157));maxEvent=731;
 private_ember269_life.events=NULL;assert(!private_ember269_event_matches(157));private_ember269_life.events=eventRec;
 /* Actual event-begin uses deterministic synthetic rows above. Scope/log/fault
  * are stubs; consumption, serial and admission body are production source. */
 private_ember269_life.mode=6;private_ember269_life.epoch=7;
 for(unsigned i=0;i<6;i++) {
  eventLoc=private_ember269_origins[i].event+1;curLoc=private_ember269_origins[i].time;
  assert(render_mirror_ember269_event_begin(eventLoc,0,25,0));
  assert(private_ember269_life.consumed[i]&&private_ember269_life.call.epoch==7);
  /* Model failed allocation: no slot or actor is allocated, end direct call. */
  private_ember269_life.call.live=false;
  assert(!render_mirror_ember269_event_begin(eventLoc,0,25,0));
 }
 memset(private_ember269_life.consumed,0,sizeof private_ember269_life.consumed);
 setenv("EMBER269_LATER_FIVE_ENABLE","0",1);private_ember269_life.mode=2;
 eventLoc=350;curLoc=3128;assert(!render_mirror_ember269_event_begin(eventLoc,0,25,0));assert(!private_ember269_life.consumed[1]);
 /* A live mode change cannot expand the pinned mode in the scope stub. */
 setenv("EMBER269_LATER_FIVE_ENABLE","1",1);assert(!render_mirror_ember269_event_begin(eventLoc,0,25,0));
 private_ember269_life.mode=4;unsetenv("EMBER269_FAMILY_CANVAS_ENABLE");
 eventLoc=158;curLoc=1252;assert(!render_mirror_ember269_event_begin(eventLoc,0,25,0));assert(!private_ember269_life.consumed[0]);
 eventLoc=350;curLoc=3128;assert(render_mirror_ember269_event_begin(eventLoc,0,25,0));private_ember269_life.call.live=false;
 assert(!ember269_later5_stream_matches(NULL));
 assert(!ember269_later5_stream_matches(eventRec));
 if(argc>1) {
  FILE *f=fopen(argv[1],"rb");assert(f);uint8_t b[11];
  for(unsigned i=0;i<731;i++) {assert(fread(b,1,11,f)==11);eventRec[i]=(struct JE_EventRecType){(uint16_t)(b[0]|b[1]<<8),b[2],(int16_t)(b[3]|b[4]<<8),(int16_t)(b[5]|b[6]<<8),(int8_t)b[7],(int8_t)b[8],(int8_t)b[9],b[10]};}
  assert(fgetc(f)==EOF);fclose(f);assert(ember269_later5_stream_matches(eventRec));
  for(unsigned i=0;i<6;i++){const struct JE_EventRecType *r=&eventRec[private_ember269_origins[i].event];assert(r->eventtime==private_ember269_origins[i].time&&r->eventtype==6&&r->eventdat==269&&r->eventdat2==private_ember269_origins[i].x&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6);}
  eventRec[700].eventdat^=1;assert(!ember269_later5_stream_matches(eventRec));eventRec[700].eventdat^=1;
  maxEvent=730;assert(!ember269_later5_stream_matches(eventRec));maxEvent=731;
  struct JE_EventRecType copy[731];memcpy(copy,eventRec,sizeof copy);assert(!ember269_later5_stream_matches(copy));
 }
 return 0;
}
'''


class LaterEmberTests(unittest.TestCase):
    def test_exact_append_only_origins_and_reused_assets(self):
        text = SOURCE.read_text()
        table = re.search(r'private_ember269_origins\[6\]=\{(.*?)\n\};', text, re.S).group(1)
        self.assertEqual([tuple(map(int,x)) for x in re.findall(r'\{(\d+),(\d+),(\d+)\}', table)], EXPECTED)
        self.assertEqual(len({r[0] for r in EXPECTED}), 6)
        self.assertIn('unsigned char consumed[6]', text)
        manifest = json.loads((ROOT / 'assets/hd/level2-family-v1/MANIFEST.json').read_text())
        self.assertEqual(manifest['file_count'], 52)
        for n in (267,269,271,273):
            self.assertTrue((ROOT / f'assets/hd/packs/asteroid1-ten-v1/enemy-newshd-{n}-8.hda').is_file())

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
            args=SimpleNamespace(data=str(root),binary=str(binary),profile=str(root/'profile'),hd=False,launch=False,later_embers=True)
            with patch.object(module,'verify_assets',return_value=52):
                with self.assertRaisesRegex(ValueError,'requires --hd'):module.build_plan(args,inherited={})
                args.hd=True;plan,env=module.build_plan(args,inherited={});self.assertTrue(plan['later_embers_enabled']);self.assertEqual(env['EMBER269_LATER_FIVE_ENABLE'],'1');self.assertEqual(plan['family_environment_count'],24);self.assertNotIn('LAMP272_LATER_SIXTEEN_ENABLE',env);self.assertNotIn('LATE_REUSE_FAMILY_ENABLE',env)
                args.later_embers=False;plan,env=module.build_plan(args,inherited={'EMBER269_LATER_FIVE_ENABLE':'1'});self.assertFalse(plan['later_embers_enabled']);self.assertNotIn('EMBER269_LATER_FIVE_ENABLE',env)
                args.later_embers=True;args.later_lamps=True;plan,env=module.build_plan(args,inherited={});self.assertEqual(plan['family_environment_count'],25);self.assertEqual(env['LAMP272_LATER_SIXTEEN_ENABLE'],'1');self.assertEqual(env['EMBER269_LATER_FIVE_ENABLE'],'1')
                args.later_embers=False;plan,env=module.build_plan(args,inherited={});self.assertNotIn('EMBER269_LATER_FIVE_ENABLE',env);self.assertEqual(env['LAMP272_LATER_SIXTEEN_ENABLE'],'1');self.assertEqual(plan['family_environment_count'],24)
                self.assertFalse((root/'profile').exists())

    def test_lifetime_and_stream_guards_remain_bound(self):
        text=SOURCE.read_text()
        self.assertIn('private_ember269_mode()==private_ember269_life.mode',text)
        self.assertIn('((private_ember269_life.mode&4u)&&!ember269_later5_stream_matches(events))',text)
        self.assertIn('Allocation failure also consumes origin.',text)
        self.assertIn('private_ember269_life.consumed[origin]=1;',text)
        self.assertNotIn('LATE_REUSE_FAMILY_ENABLE',text+SCOPE.read_text())


if __name__=='__main__':unittest.main()
