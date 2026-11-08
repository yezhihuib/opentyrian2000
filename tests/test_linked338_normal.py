"""Normal linked group only. Isolated native-observer tests; no game execution."""
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'experimental/level2-family/src'
TEXT=(SRC/'linked338_normal_family_mirror.inc').read_text()
spec=importlib.util.spec_from_file_location('linked_launcher',ROOT/'scripts/launch_level2_family.py')
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)


def function(name):
    return re.search(r'(?:static )?(?:bool|void|uint64_t|int) '+name+r'\([^\n]*\)\n\{.*?\n\}',TEXT,re.S).group()


def run_c(source):
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp);(p/'test.c').write_text(source)
        result=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-unused-const-variable','-I',str(SRC),str(p/'test.c'),'-o',str(p/'test')],capture_output=True,text=True)
        if result.returncode:raise AssertionError(result.stderr)
        subprocess.run([str(p/'test')],check=True,capture_output=True,text=True)


class Linked338Tests(unittest.TestCase):
    def test_launcher_off_and_explicit_combination(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);b=p/'never-run';b.write_text('');b.chmod(0o700)
            args=['--data',temp,'--binary',str(b)]
            inherited={'LINKED338_NORMAL_ENABLE':'1','LINKED338_NORMAL_ASSET_DIR':'wrong','LINKED338_OTHER':'1','FORK284_ENABLE':'1'}
            for flags in ([],['--hd']):
                plan,env=launcher.build_plan(launcher.parser().parse_args(args+flags),inherited)
                self.assertFalse(plan['linked338_enabled']);self.assertFalse(any(k.startswith('LINKED338_') for k in env))
            with self.assertRaisesRegex(ValueError,'requires --hd'):
                launcher.build_plan(launcher.parser().parse_args(args+['--linked338']),{})
            plan,env=launcher.build_plan(launcher.parser().parse_args(args+['--hd','--linked338','--fork284']),{})
            self.assertEqual(plan['assets_sha256_verified'],52);self.assertEqual(plan['linked338_assets_sha256_verified'],7)
            self.assertTrue(plan['linked338_enabled'] and plan['fork284_enabled']);self.assertFalse(plan['game_started'])
            self.assertNotIn('PROJECTILE304_ENABLE',env)

    def test_all_seven_assets_and_damage_rejection(self):
        self.assertEqual(set(launcher.LINKED338_SHA256),{115,117,119,229,231,267,269})
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);b=p/'never-run';b.write_text('');b.chmod(0o700)
            directory=p/launcher.REUSED_ROOT;directory.mkdir(parents=True)
            for base in launcher.LINKED338_SHA256:
                name=f'enemy-newshp-{base}-8.hda';raw=(ROOT/launcher.REUSED_ROOT/name).read_bytes()
                self.assertEqual(len(raw),172060);(directory/name).write_bytes(raw)
            name='enemy-newshp-269-8.hda';raw=(directory/name).read_bytes();(directory/name).write_bytes(raw[:-1]+bytes([raw[-1]^1]))
            args=launcher.parser().parse_args(['--data',temp,'--binary',str(b),'--hd','--linked338'])
            with patch.object(launcher,'verify_assets',return_value=52),self.assertRaisesRegex(ValueError,'Changed Linked338'):
                launcher.build_plan(args,{},p)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_ten_independent_attempts_and_script_mutations(self):
        # Exact admission and native-script observer bodies, other state explicit stubs.
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "linked338_normal_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
#include "linked338_normal_pins.inc"
struct JE_EventRecType {uint16_t eventtime;uint8_t eventtype;int16_t eventdat,eventdat2;int8_t eventdat3,eventdat5,eventdat6;uint8_t eventdat4;};
struct JE_EventRecType eventRec[731];
static unsigned maxEvent=731,eventLoc,curLoc,failures;static int mapX=1;
static struct {bool loaded,exhausted;const struct JE_EventRecType *events;unsigned consumed;uint64_t serial,epoch;
 struct {bool live;uint64_t token,epoch,generation;unsigned event,ei,record,pool,component;int slot,x,y,map1;} call;
} ln_life;
static struct {bool active,failed;unsigned event,next;uint64_t observations,mutations;struct JE_EventRecType before,expected[731];} ln_script;
static bool ln_scope(void){return ln_life.loaded&&!ln_life.exhausted&&!ln_script.failed;}
static void ln_fail(unsigned r){(void)r;failures++;}
static int ln_event_index(unsigned e){for(unsigned i=0;i<4;i++)if(ln_events[i].event==e)return (int)i;return -1;}
'''+'\n'.join(function(n) for n in ('ln_event_matches','ln_events_current','ln_row_equal','render_mirror_linked338_normal_script_before','render_mirror_linked338_normal_script_after','render_mirror_linked338_normal_event_begin'))+r'''
int main(void){
 ln_life.loaded=true;ln_life.events=eventRec;ln_life.epoch=4;ln_script.next=1;
 for(unsigned i=0;i<4;i++){
  const unsigned e=ln_events[i].event;struct JE_EventRecType *r=eventRec+e-1;
  *r=(struct JE_EventRecType){ln_events[i].time,ln_events[i].type,ln_events[i].record,ln_events[i].x,0,ln_events[i].y,0,ln_events[i].link};
  assert(ln_event_matches(e));r->eventdat4++;assert(!ln_event_matches(e));r->eventdat4--;
 }
 eventRec[0]=(struct JE_EventRecType){0,12,400,1,0,0,1,0};
 eventRec[1]=(struct JE_EventRecType){0,33,533,0,0,0,0,0};
 memcpy(ln_script.expected,eventRec,sizeof eventRec);
 unsigned attempts=0;
 for(eventLoc=1;eventLoc<=354;eventLoc++){
  curLoc=eventRec[eventLoc-1].eventtime;render_mirror_linked338_normal_script_before(eventLoc);assert(!failures);
  if(eventLoc==1)eventRec[0].eventdat6=0;
  if(eventLoc==2)eventRec[1].eventdat=832; /* documented native random choice, no RNG used by observer */
  int ei=ln_event_index(eventLoc);
  if(ei>=0){
   unsigned parts=ln_events[ei].type==6?1:4;
   assert(!render_mirror_linked338_normal_event_begin(eventLoc,4,25,0));
   assert(!render_mirror_linked338_normal_event_begin(eventLoc,0,50,0));
   assert(!render_mirror_linked338_normal_event_begin(eventLoc,0,25,1));
   for(unsigned part=0;part<parts;part++){
    assert(render_mirror_linked338_normal_event_begin(eventLoc,part,25,0));attempts++;
    assert(ln_life.call.record==ln_events[ei].record+part);
    assert(ln_life.call.x==ln_events[ei].x-12+(part%2?24:0));
    assert(ln_life.call.y==-28+ln_events[ei].y-(part>=2?28:0));
    /* Each failed allocation still consumes this component, not its siblings. */
    ln_life.call.live=false;assert(!render_mirror_linked338_normal_event_begin(eventLoc,part,25,0));
   }
  }
  render_mirror_linked338_normal_script_after(eventLoc);assert(!failures);
 }
 assert(attempts==10&&ln_life.consumed==1023&&ln_script.observations==354&&ln_script.mutations==2);
 eventLoc=355;curLoc=0;render_mirror_linked338_normal_script_before(eventLoc);eventRec[354].eventdat=42;
 render_mirror_linked338_normal_script_after(eventLoc);assert(ln_script.failed&&failures==1);
 return 0;
}
'''
        run_c(source)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_cap_animation_and_static_components(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "linked338_normal_family.h"
static struct {bool live;unsigned record,cycle,gate;uint64_t phase_tick;Linked338NormalBirth birth;} ln_slots[100];
static struct {int ex;unsigned enemycycle,aniactive;} enemy[100];
static uint64_t fc_frame,ln_phase_observations;static int tempMapXOfs;static unsigned retired;
static bool ln_scope(void){return true;}
static bool ln_witness(unsigned s){(void)s;return true;}
static bool ln_shape(unsigned s,unsigned stage){(void)s;(void)stage;return true;}
static void render_mirror_linked338_normal_retired(unsigned s){retired++;ln_slots[s].live=false;}
'''+function('render_mirror_linked338_normal_enemy_animated')+r'''
int main(void){
 for(unsigned s=25;s<30;s++){ln_slots[s].live=true;ln_slots[s].record=338+s-25;ln_slots[s].phase_tick=UINT64_MAX;enemy[s].ex=50;}
 for(unsigned tick=1;tick<=36;tick++){
  fc_frame=tick;
  for(unsigned s=25;s<30;s++){
   enemy[s].enemycycle=s==25?(tick-1)%12+1:1;enemy[s].aniactive=s==25?1:0;
   render_mirror_linked338_normal_enemy_animated(s);assert(!retired&&ln_slots[s].cycle==enemy[s].enemycycle&&ln_slots[s].gate==enemy[s].aniactive);
  }
 }
 assert(ln_phase_observations==180);
 render_mirror_linked338_normal_enemy_animated(25);assert(retired==1);
 fc_frame++;enemy[26].enemycycle=2;render_mirror_linked338_normal_enemy_animated(26);assert(retired==2);
 enemy[27].aniactive=1;render_mirror_linked338_normal_enemy_animated(27);assert(retired==3);
 return 0;
}
'''
        run_c(source)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_seven_native_images_alpha_holes_and_retirement(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "linked338_normal_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
#include "linked338_normal_pins.inc"
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
#define FC_ORDER 1
static uint8_t ln_owned[64000],ln_shadows[64000],selected[64000],expected[64000],native[64000];
static uint8_t hd_owner[4096000],cloud_owner[4096000];static unsigned green_first[4096000];static uint32_t rgb[4096000];
static struct {void *pixels;} surface={rgb},*canvas=&surface;static void *fc_source_pixels=native;
static struct {bool active,pending,contributed;unsigned slot,part,pixels,image;Linked338NormalDraw draw[100];Linked338NormalWrite writes[100][672];} ln_frame;
static uint64_t ln_blend_retirements,ln_normal_retirements,ln_shadow_writes,ln_contract_faults;
static unsigned failure,clears;
typedef struct {uint8_t *rgba;} Asset;static uint8_t rgba[172032];static struct {Asset member[7];} ln_resources;
static void ln_fail(unsigned r){failure=r;ln_frame.active=ln_frame.pending=false;}
static void family_fault(unsigned r){(void)r;}
static void lamp272_clear(unsigned x){(void)x;clears++;}
#define triple275_clear lamp272_clear
#define private_ember269_clear lamp272_clear
#define gray325_clear lamp272_clear
#define longface573_clear lamp272_clear
static uint32_t blend_rgba(uint32_t dst,const uint8_t *art,unsigned a){
 unsigned r=(((dst>>16)&255)*(255-a)+art[0]*a)/255;
 unsigned g=(((dst>>8)&255)*(255-a)+art[1]*a)/255;
 unsigned b=((dst&255)*(255-a)+art[2]*a)/255;
 return 0xff000000u|(r<<16)|(g<<8)|b;
}
'''+'\n'.join(function(n) for n in ('ln_retire','ln_pixel','ln_shadow'))+r'''
int main(void){
 assert(ln_records[0].record==338&&ln_events[0].event==288&&ln_events[1].event==289);
 for(unsigned i=0;i<172032;i+=4){rgba[i]=60;rgba[i+1]=80;rgba[i+2]=120;rgba[i+3]=(i/4)%192%8==0?0:127;}
 unsigned total=0;
 for(unsigned image=0;image<7;image++){
  for(unsigned n=0;n<4096000;n++)rgb[n]=0xff204060;
  memset(ln_owned,0,sizeof ln_owned);
  memset(&ln_frame,0,sizeof ln_frame);ln_frame.slot=25;ln_frame.image=image;ln_frame.pending=true;ln_frame.contributed=true;
  ln_resources.member[image].rgba=rgba;Linked338NormalDraw *d=ln_frame.draw+25;d->x=40;d->y=20;
  assert(ln_images[image].extra==0);total+=ln_totals[image];
  for(unsigned k=0;k<4;k++){
   ln_frame.part=k;ln_frame.active=true;ln_frame.pixels=0;
   for(unsigned i=0;i<ln_counts[image][k];i++){
    const Linked338NormalWrite *w=ln_native[image][k]+i;
    unsigned x=d->x+ln_px[k]+w->x,y=d->y+ln_py[k]+w->y,off=y*320+x;
    native[off]=expected[off]=w->index;assert(ln_pixel(x,y,MIRROR_NORMAL)&&!failure);
    assert(ln_owned[off]==26&&selected[off]&&rgb[y*8*2560+x*8]==0xff204060);
   }
  }
  assert(d->callback_count==ln_totals[image]);
  unsigned holes=0;
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(!ln_owned[(y+20)*320+x+40]){
   assert(rgb[(y+20)*8*2560+(x+40)*8]==0xff204060);holes++;
  }
  assert(holes==672-ln_totals[image]);
  const Linked338NormalWrite *w=ln_native[image][0];
  unsigned off=(20+w->y)*320+40+w->x;assert(ln_retire(off,MIRROR_SHADOW)&&ln_owned[off]==26);ln_shadow(off);assert(ln_shadows[off]==1);
  assert(ln_retire(off,MIRROR_BLEND)&&!ln_owned[off]&&!ln_shadows[off]);
  ln_owned[off]=26;assert(ln_retire(off,MIRROR_NORMAL)&&!ln_owned[off]);
 }
 assert(clears==total*5&&ln_blend_retirements==7&&ln_normal_retirements==7&&ln_shadow_writes==7);
 ln_frame.part=0;ln_frame.pixels=0;ln_frame.active=true;assert(ln_pixel(0,0,MIRROR_NORMAL)&&failure==16);
 return 0;
}
'''
        run_c(source)

    def test_hook_order_and_no_damage_loader(self):
        canvas=(SRC/'b313_family_canvas_mirror.inc').read_text();native=(SRC/'tyrian2.c').read_text()
        for name in ('f284','tp','ln'):
            self.assertLess(canvas.index(name+'_retire((unsigned)off,style)'),canvas.index('if(f284_pixel'))
            self.assertIn(name+'_before_tile(slot,part)',canvas)
        self.assertIn('!linked_owned&&!linked_prop_owned&&!terrain_retire',canvas)
        self.assertIn('ln_write_current()',canvas);self.assertIn('!ln_finish()',canvas);self.assertIn('!ln_guard()',canvas)
        self.assertIn('!f284_stream_matches(events)',TEXT)
        before=native.index('render_mirror_linked338_normal_script_before(facts_event_entry);')
        after=native.index('render_mirror_linked338_normal_script_after(facts_event_entry);')
        self.assertLess(before,native.index('case 6: /* Ground Enemy */',before))
        self.assertLess(after,native.index('eventLoc++;',after))
        for k in range(4):
            begin=native.index(f'const uint64_t linked338_call{k}=')
            commit=native.index(f'render_mirror_linked338_normal_event_commit(linked338_call{k},b313_slot{k});')
            self.assertLess(begin,native.index(f'JE_createNewEventEnemy({k}, temp, 0);',begin))
            if k in (1,3):self.assertLess(native.index('enemy[b-1].ex += 24;',begin),commit)
            if k in (2,3):self.assertLess(native.index('enemy[b-1].ey -= 28;',begin),commit)
        self.assertEqual(set(launcher.LINKED338_SHA256),{115,117,119,229,231,267,269})
        self.assertNotIn(121,launcher.LINKED338_SHA256)
        self.assertIn('e->edamaged',TEXT)

if __name__=='__main__':unittest.main()
