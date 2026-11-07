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
SOURCE = ROOT / 'experimental/level2-family/src/triple275_family_mirror.inc'
SCOPE = SOURCE.with_name('triple275_later132_scope.inc')
EXPECTED = [(150, 1224, 114), (293, 2540, 258), (294, 2540, 42), (298, 2568, 42), (299, 2568, 258), (302, 2596, 42), (303, 2596, 258), (305, 2624, 42), (306, 2624, 258), (307, 2652, 42), (308, 2652, 258), (309, 2680, 42), (310, 2680, 258), (312, 2708, 258), (313, 2708, 42), (316, 2736, 258), (317, 2736, 42), (320, 2764, 42), (321, 2764, 258), (322, 2792, 42), (323, 2792, 258), (328, 2848, 42), (329, 2848, 258), (330, 2876, 42), (331, 2876, 258), (332, 2904, 42), (333, 2904, 258), (334, 2932, 42), (335, 2932, 258), (336, 2960, 42), (337, 2960, 258), (338, 2988, 42), (339, 2988, 258), (340, 3016, 42), (341, 3016, 258), (342, 3044, 42), (343, 3044, 258), (344, 3072, 42), (345, 3072, 258), (348, 3128, 42), (352, 3128, 258), (354, 3156, 42), (355, 3156, 258), (356, 3184, 42), (357, 3184, 258), (358, 3212, 42), (359, 3212, 258), (360, 3240, 42), (361, 3240, 258), (362, 3268, 42), (363, 3268, 258), (364, 3296, 42), (365, 3296, 258), (366, 3324, 42), (367, 3324, 258), (368, 3352, 42), (369, 3352, 258), (372, 3408, 42), (373, 3408, 258), (374, 3436, 42), (375, 3436, 258), (376, 3464, 42), (377, 3464, 258), (378, 3492, 42), (379, 3492, 258), (380, 3520, 42), (381, 3520, 258), (382, 3548, 42), (383, 3548, 258), (384, 3576, 42), (385, 3576, 258), (386, 3604, 42), (387, 3604, 258), (388, 3632, 42), (389, 3632, 258), (392, 3688, 42), (393, 3688, 258), (394, 3716, 42), (395, 3716, 258), (396, 3772, 42), (397, 3772, 258), (399, 3800, 42), (400, 3800, 258), (401, 3828, 42), (402, 3828, 258), (403, 3856, 42), (404, 3856, 258), (405, 3884, 42), (406, 3884, 258), (407, 3912, 42), (408, 3912, 258), (411, 3968, 42), (412, 3968, 258), (413, 3996, 42), (414, 3996, 258), (415, 4024, 42), (416, 4024, 258), (417, 4052, 42), (418, 4052, 258), (420, 4080, 42), (421, 4080, 258), (422, 4108, 42), (423, 4108, 258), (424, 4136, 42), (425, 4136, 258), (426, 4164, 42), (427, 4164, 258), (428, 4192, 42), (429, 4192, 258), (432, 4248, 42), (433, 4248, 258), (434, 4276, 42), (435, 4276, 258), (436, 4304, 42), (437, 4304, 258), (438, 4332, 42), (439, 4332, 258), (440, 4360, 42), (441, 4360, 258), (442, 4388, 42), (443, 4388, 258), (444, 4416, 42), (445, 4416, 258), (446, 4444, 42), (447, 4444, 258), (448, 4472, 42), (449, 4472, 258), (468, 4584, 42), (469, 4584, 258), (473, 4612, 258), (474, 4612, 42), (477, 4640, 42), (478, 4640, 258)]


def function(text, name):
    start = text.index('static ', text.index(name) - 30)
    # Extract through the unindented function closing brace.
    end = text.index('\n}', start) + 2
    return text[start:end]


def harness():
    text = SOURCE.read_text()
    table = re.search(r'static const struct \{unsigned event,time;int x;\} private_triple275_origins\[133\]=\{.*?\n\};', text, re.S).group()
    funcs = '\n'.join(function(text, name) for name in ('private_triple275_origin(', 'private_triple275_mode(', 'private_triple275_origin_enabled(', 'private_triple275_event_matches('))
    begin = re.search(r'uint64_t render_mirror_triple275_event_begin\(.*?\n\}', text, re.S).group()
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
#include "triple275_later132_scope.inc"
static struct {
 unsigned mode;unsigned char consumed[133];const struct JE_EventRecType *events;
 uint64_t serial,epoch;bool exhausted;
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot;} call;
} private_triple275_life;
unsigned eventLoc,curLoc;
static unsigned private_triple275_mode(void);
static bool private_triple275_scope(void){return private_triple275_mode()==private_triple275_life.mode&&!private_triple275_life.exhausted;}
static void private_triple275_fail(void){}
static void private_triple275_log(const char *p,int s,unsigned e,unsigned b,int part,int ok){(void)p;(void)s;(void)e;(void)b;(void)part;(void)ok;}

''' + table + '\n' + funcs + '\n' + begin + r'''
int main(int argc,char **argv) {
 unsetenv("TRIPLE275_LATER_132_ENABLE");unsetenv("TRIPLE275_FAMILY_CANVAS_ENABLE");unsetenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 assert(!triple275_later132_requested()&&private_triple275_mode()==0);
 setenv("TRIPLE275_LATER_132_ENABLE","1",1);assert(triple275_later132_requested());assert(private_triple275_mode()==0);
 setenv("BUILDING313_FAMILY_CANVAS_ENABLE","1",1);assert(private_triple275_mode()==4);
 setenv("TRIPLE275_FAMILY_CANVAS_ENABLE","1",1);assert(private_triple275_mode()==6);
 setenv("TRIPLE275_LATER_132_ENABLE","true",1);assert(!triple275_later132_requested()&&private_triple275_mode()==2);
 setenv("TRIPLE275_LATER_132_ENABLE","1",1);
 lvlFileNum=1;assert(!triple275_later132_requested());lvlFileNum=2;
 mainLevel=5;assert(!triple275_later132_requested());mainLevel=6;
 episodeNum=2;assert(!triple275_later132_requested());episodeNum=1;
 play_demo=true;assert(!triple275_later132_requested());play_demo=false;
 game_probe_enabled=true;assert(!triple275_later132_requested());game_probe_enabled=false;
 asset_debug_enabled=true;assert(!triple275_later132_requested());asset_debug_enabled=false;
 demo_file=eventRec;assert(!triple275_later132_requested());demo_file=NULL;
 strcpy(levelName,"ASTEROID1");assert(!triple275_later132_requested());strcpy(levelName,"ASTEROID2");
 for(unsigned mode=0;mode<=6;mode+=2) {
  private_triple275_life.mode=mode;
  assert(!private_triple275_origin_enabled(-1)&&!private_triple275_origin_enabled(133));
  for(int i=0;i<133;i++) {
   bool expected=(mode&(i==0?2u:4u))!=0;
   assert(private_triple275_origin_enabled(i)==expected);
   assert(private_triple275_origin(private_triple275_origins[i].event)==i);
  }
 }
 assert(private_triple275_origin(0)==-1&&private_triple275_origin(731)==-1&&private_triple275_origin(UINT32_MAX)==-1);
 private_triple275_life.events=eventRec;
 for(unsigned i=0;i<133;i++) {
  unsigned n=private_triple275_origins[i].event;
  eventRec[n]=(struct JE_EventRecType){private_triple275_origins[i].time,6,275,private_triple275_origins[i].x,0,0,0,0};
  assert(private_triple275_event_matches(n));
  eventRec[n].eventdat2++;assert(!private_triple275_event_matches(n));eventRec[n].eventdat2--;
  eventRec[n].eventdat6=1;assert(!private_triple275_event_matches(n));eventRec[n].eventdat6=0;
 }
 assert(!private_triple275_event_matches(0)&&!private_triple275_event_matches(UINT32_MAX));
 maxEvent=730;assert(!private_triple275_event_matches(150));maxEvent=731;
 private_triple275_life.events=NULL;assert(!private_triple275_event_matches(150));private_triple275_life.events=eventRec;
 /* Actual event-begin uses deterministic synthetic rows above. Scope/log/fault
  * are stubs; consumption, serial and admission body are production source. */
 private_triple275_life.mode=6;private_triple275_life.epoch=7;
 for(unsigned i=0;i<133;i++) {
  eventLoc=private_triple275_origins[i].event+1;curLoc=private_triple275_origins[i].time;
  assert(render_mirror_triple275_event_begin(eventLoc,0,25,0));
  assert(private_triple275_life.consumed[i]&&private_triple275_life.call.epoch==7);
  /* Model failed allocation: no slot or actor is allocated, end direct call. */
  private_triple275_life.call.live=false;
  assert(!render_mirror_triple275_event_begin(eventLoc,0,25,0));
 }
 assert(private_triple275_life.consumed[132]==1);
 memset(private_triple275_life.consumed,0,sizeof private_triple275_life.consumed);
 setenv("TRIPLE275_LATER_132_ENABLE","0",1);private_triple275_life.mode=2;
 eventLoc=294;curLoc=2540;assert(!render_mirror_triple275_event_begin(eventLoc,0,25,0));assert(!private_triple275_life.consumed[1]);
 /* A live mode change cannot expand the pinned mode in the scope stub. */
 setenv("TRIPLE275_LATER_132_ENABLE","1",1);assert(!render_mirror_triple275_event_begin(eventLoc,0,25,0));
 private_triple275_life.mode=4;unsetenv("TRIPLE275_FAMILY_CANVAS_ENABLE");
 eventLoc=151;curLoc=1224;assert(!render_mirror_triple275_event_begin(eventLoc,0,25,0));assert(!private_triple275_life.consumed[0]);
 eventLoc=294;curLoc=2540;assert(render_mirror_triple275_event_begin(eventLoc,0,25,0));private_triple275_life.call.live=false;
 assert(!triple275_later132_stream_matches(NULL));
 assert(!triple275_later132_stream_matches(eventRec));
 if(argc>1) {
  FILE *f=fopen(argv[1],"rb");assert(f);uint8_t b[11];
  for(unsigned i=0;i<731;i++) {assert(fread(b,1,11,f)==11);eventRec[i]=(struct JE_EventRecType){(uint16_t)(b[0]|b[1]<<8),b[2],(int16_t)(b[3]|b[4]<<8),(int16_t)(b[5]|b[6]<<8),(int8_t)b[7],(int8_t)b[8],(int8_t)b[9],b[10]};}
  assert(fgetc(f)==EOF);fclose(f);assert(triple275_later132_stream_matches(eventRec));
  for(unsigned i=0;i<133;i++){const struct JE_EventRecType *r=&eventRec[private_triple275_origins[i].event];assert(r->eventtime==private_triple275_origins[i].time&&r->eventtype==6&&r->eventdat==275&&r->eventdat2==private_triple275_origins[i].x&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6);}
  /* Last origin uses ordinal132 (not a machine-word shift), on real data. */
  assert(private_triple275_origin(478)==132);
  memset(private_triple275_life.consumed,0,sizeof private_triple275_life.consumed);
  eventLoc=479;curLoc=4640;
  assert(render_mirror_triple275_event_begin(eventLoc,0,25,0));
  assert(private_triple275_life.consumed[132]==1);private_triple275_life.call.live=false;
  assert(!render_mirror_triple275_event_begin(eventLoc,0,25,0));
  eventRec[700].eventdat^=1;assert(!triple275_later132_stream_matches(eventRec));eventRec[700].eventdat^=1;
  maxEvent=730;assert(!triple275_later132_stream_matches(eventRec));maxEvent=731;
  struct JE_EventRecType copy[731];memcpy(copy,eventRec,sizeof copy);assert(!triple275_later132_stream_matches(copy));
 }
 return 0;
}
'''


class LaterTripleTests(unittest.TestCase):
    def test_exact_append_only_origins_and_reused_assets(self):
        text = SOURCE.read_text()
        table = re.search(r'private_triple275_origins\[133\]=\{(.*?)\n\};', text, re.S).group(1)
        self.assertEqual([tuple(map(int,x)) for x in re.findall(r'\{(\d+),(\d+),(\d+)\}', table)], EXPECTED)
        self.assertEqual(len({r[0] for r in EXPECTED}), 133)
        self.assertIn('unsigned char consumed[133]', text)
        manifest = json.loads((ROOT / 'assets/hd/level2-family-v1/MANIFEST.json').read_text())
        self.assertEqual(manifest['file_count'], 52)
        for n in (153,155,157,159,161,163):
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
            args=SimpleNamespace(data=str(root),binary=str(binary),profile=str(root/'profile'),hd=False,launch=False,later_triples=True)
            with patch.object(module,'verify_assets',return_value=52):
                with self.assertRaisesRegex(ValueError,'requires --hd'):module.build_plan(args,inherited={})
                args.hd=True
                controls={'later_lamps':'LAMP272_LATER_SIXTEEN_ENABLE','later_embers':'EMBER269_LATER_FIVE_ENABLE','later_triples':'TRIPLE275_LATER_132_ENABLE'}
                for mask in range(8):
                    for i,key in enumerate(controls):setattr(args,key,bool(mask&(1<<i)))
                    plan,env=module.build_plan(args,inherited={value:'1' for value in controls.values()})
                    self.assertEqual(plan['family_environment_count'],23+mask.bit_count())
                    for key,value in controls.items():
                        self.assertEqual(plan[key+'_enabled'],getattr(args,key))
                        self.assertEqual(value in env,getattr(args,key))
                        if value in env:self.assertEqual(env[value],'1')
                    self.assertNotIn('LATE_REUSE_FAMILY_ENABLE',env)
                self.assertFalse((root/'profile').exists())

    def test_lifetime_and_stream_guards_remain_bound(self):
        text=SOURCE.read_text()
        self.assertIn('private_triple275_mode()==private_triple275_life.mode',text)
        self.assertIn('((private_triple275_life.mode&4u)&&!triple275_later132_stream_matches(events))',text)
        self.assertIn('Allocation failure also consumes origin.',text)
        self.assertIn('private_triple275_life.consumed[origin]=1;',text)
        self.assertNotIn('LATE_REUSE_FAMILY_ENABLE',text+SCOPE.read_text())


if __name__=='__main__':unittest.main()
