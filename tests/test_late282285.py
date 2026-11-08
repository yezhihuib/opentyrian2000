"""Independent linked props only. Isolated native-observer tests; no game execution."""
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
TEXT=(SRC/'late_actor_family_mirror.inc').read_text()
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


class Late282285Tests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_six_native_images_alpha_holes_and_retirement(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "late_actor_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
#include "late_actor_pins.inc"
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
#define FC_ORDER 1
#define OHS_SURVIVAL_WRITE(...) ((void)0)
static uint8_t la_owned[64000],la_shadows[64000],selected[64000],expected[64000],native[64000];
static uint8_t hd_owner[4096000],cloud_owner[4096000];static unsigned green_first[4096000];static uint32_t rgb[4096000];
static struct {void *pixels;} surface={rgb},*canvas=&surface;static void *fc_source_pixels=native;
static struct {bool active,pending,contributed;unsigned slot,part,pixels,image;LateActorDraw draw[100];LateActorWrite writes[100][672];} la_frame;
static uint64_t la_blend_retirements,la_normal_retirements,la_shadow_writes,la_contract_faults;
static unsigned failure,clears;
typedef struct {uint8_t *rgba;} Asset;static uint8_t rgba[172032];static struct {Asset member[7];} la_resources;
static void la_fail(unsigned r){failure=r;la_frame.active=la_frame.pending=false;}
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
'''+'\n'.join(function(n) for n in ('la_retire','la_pixel','la_shadow'))+r'''
int main(void){
 assert(la_records[0].record==282&&la_records[2].record==285);
 for(unsigned i=0;i<172032;i+=4){rgba[i]=60;rgba[i+1]=80;rgba[i+2]=120;rgba[i+3]=(i/4)%192%8==0?0:127;}
 unsigned total=0;
 for(unsigned image=0;image<7;image++){
  if(image==3)continue;
  for(unsigned n=0;n<4096000;n++)rgb[n]=0xff204060;
  memset(la_owned,0,sizeof la_owned);
  memset(&la_frame,0,sizeof la_frame);la_frame.slot=25;la_frame.image=image;la_frame.pending=true;la_frame.contributed=true;
  la_resources.member[image].rgba=rgba;LateActorDraw *d=la_frame.draw+25;d->x=40;d->y=20;
  total+=la_totals[image];
  for(unsigned k=0;k<4;k++){
   la_frame.part=k;la_frame.active=true;la_frame.pixels=0;
   for(unsigned i=0;i<la_counts[image][k];i++){
    const LateActorWrite *w=la_native[image][k]+i;
    unsigned x=d->x+la_px[k]+w->x,y=d->y+la_py[k]+w->y,off=y*320+x;
    native[off]=expected[off]=w->index;assert(la_pixel(x,y,MIRROR_NORMAL)&&!failure);
    assert(la_owned[off]==26&&selected[off]&&rgb[y*8*2560+x*8]==0xff204060);
   }
  }
  assert(d->callback_count==la_totals[image]);
  unsigned holes=0;
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(!la_owned[(y+20)*320+x+40]){
   assert(rgb[(y+20)*8*2560+(x+40)*8]==0xff204060);holes++;
  }
  assert(holes==672-la_totals[image]);
  const LateActorWrite *w=la_native[image][0];
  unsigned off=(20+w->y)*320+40+w->x;assert(la_retire(off,MIRROR_SHADOW)&&la_owned[off]==26);la_shadow(off);assert(la_shadows[off]==1);
  assert(la_retire(off,MIRROR_BLEND)&&!la_owned[off]&&!la_shadows[off]);
  la_owned[off]=26;assert(la_retire(off,MIRROR_NORMAL)&&!la_owned[off]);
 }
 assert(clears==total*5&&la_blend_retirements==6&&la_normal_retirements==6&&la_shadow_writes==6);
 la_frame.part=0;la_frame.pixels=0;la_frame.active=true;assert(la_pixel(0,0,MIRROR_NORMAL)&&failure==16);
 return 0;
}
'''
        run_c(source)

    def test_launcher_default_off_and_six_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);b=p/'never-run';b.write_text('');b.chmod(0o700)
            args=['--data',temp,'--binary',str(b)]
            for flags in ([],['--hd']):
                plan,env=launcher.build_plan(launcher.parser().parse_args(args+flags),{'LATE_ACTORS_ENABLE':'1'})
                self.assertFalse(plan['late282285_enabled']);self.assertNotIn('LATE_ACTORS_ENABLE',env)
            with self.assertRaisesRegex(ValueError,'requires --hd'):
                launcher.build_plan(launcher.parser().parse_args(args+['--late282285']),{})
            plan,env=launcher.build_plan(launcher.parser().parse_args(args+['--hd','--late282285','--linked-props','--fork284']),{})
            self.assertEqual(plan['late282285_assets_sha256_verified'],6);self.assertFalse(plan['game_started'])
            self.assertEqual(env['LATE_ACTORS_ENABLE'],'1')
            self.assertEqual(set(launcher.LATE282285_SHA256),{f'enemy-newshd-{x}-8.hda' for x in (79,81,83,157,159,161)})
            d=p/launcher.REUSED_ROOT;d.mkdir(parents=True)
            for name in launcher.LATE282285_SHA256:(d/name).write_bytes((ROOT/launcher.REUSED_ROOT/name).read_bytes())
            f=d/'enemy-newshd-159-8.hda';raw=f.read_bytes();f.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
            with patch.object(launcher,'verify_assets',return_value=52),self.assertRaises(ValueError):
                launcher.build_plan(launcher.parser().parse_args(args+['--hd','--late282285']),{},p)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_eight_admissions_pools_and_no283(self):
        helpers=TEXT[TEXT.index('static int la_record_index'):TEXT.index('static bool la_scope')]
        # Exclude script state/helper; it is separately checked with real script hook tests.
        helpers=helpers[:helpers.index('static struct {bool active,failed;')]
        run_c(r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "late_actor_family.h"
typedef uint32_t Uint32;
#include "late_actor_pins.inc"
struct JE_EventRecType {unsigned eventtime,eventtype;int eventdat,eventdat2,eventdat3;uint8_t eventdat4;int eventdat5,eventdat6;};
static struct JE_EventRecType eventRec[731];static unsigned maxEvent=731,eventLoc,curLoc;
static struct {bool active;unsigned event;} la_script;
static int mapX=1,mapX3=1;static bool background3x1=true,background3x1b=false;
static struct {bool loaded,exhausted;uint64_t epoch,serial;unsigned consumed;const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned event,ei,record,pool;int slot,x,y;bool bg3x1,bg3x1b;int map1,map3;} call;
} la_life;
static bool la_scope(void){return la_life.loaded&&!la_life.exhausted;}
static void la_fail(unsigned r){(void)r;assert(0);}
'''+helpers+function('render_mirror_late_actor_event_begin')+r'''
int main(void){
 la_life.loaded=true;la_life.events=eventRec;
 assert(la_record_index(283)==-1&&!la_pool(0,283)&&la_event_index(262)==-1&&la_image(115)==-1);
 for(unsigned i=4;i<12;i++){
  eventLoc=la_events[i].event;curLoc=la_events[i].time;
  eventRec[eventLoc-1]=(struct JE_EventRecType){curLoc,la_events[i].type,(int)la_events[i].record,la_events[i].x,la_events[i].dy,(unsigned)la_events[i].link,0,0};
 }
 assert(la_events_current());
 for(unsigned i=4;i<12;i++){
  eventLoc=la_events[i].event;curLoc=la_events[i].time;
  assert(!render_mirror_late_actor_event_begin(eventLoc,0,la_events[i].pool,0));
  la_script.active=true;la_script.event=eventLoc+1;
  assert(!render_mirror_late_actor_event_begin(eventLoc,0,la_events[i].pool,0));
  la_script.event=eventLoc;
  assert(!render_mirror_late_actor_event_begin(eventLoc,0,25,0));
  assert(!render_mirror_late_actor_event_begin(eventLoc,1,la_events[i].pool,0));
  assert(!render_mirror_late_actor_event_begin(eventLoc,0,la_events[i].pool,1));
  assert(render_mirror_late_actor_event_begin(eventLoc,0,la_events[i].pool,0));
  assert(la_life.call.x==la_events[i].x-(i>=8?12:0)&&la_life.call.y==-28);
  /* Failed original allocation consumes only this event, never a partner. */
  la_life.call.live=false;assert(!render_mirror_late_actor_event_begin(eventLoc,0,la_events[i].pool,0));la_script.active=false;
 }
 assert(la_life.consumed==4080&&la_life.serial==8);return 0;
}
''')

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_both_firing_cycles_and_successful_resumption(self):
        run_c(r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "late_actor_family.h"
typedef uint32_t Uint32;
#include "late_actor_pins.inc"
#define ENEMY_SHOT_MAX 60
static unsigned enemyShotAvail[60];
static struct {bool live;unsigned record,cycle,gate;uint64_t phase_tick,generation;LateActorBirth birth;} la_slots[100];
static struct {unsigned enemycycle,aniactive;} enemy[100];
static struct {LateActorDraw draw[100];} la_frame;
static uint64_t fc_frame,la_phase_observations,la_shot_resumptions;static unsigned retired;
static bool la_scope(void){return true;}static bool la_witness(unsigned s){return la_slots[s].live;}
static bool la_shape(unsigned s,unsigned stage){(void)s;(void)stage;return true;}
static int la_record_index(unsigned r){return r==282?0:r==285?2:-1;}
static void render_mirror_late_actor_retired(unsigned s){la_slots[s].live=false;retired++;}
'''+function('render_mirror_late_actor_enemy_animated')+function('render_mirror_late_actor_shot_fired')+r'''
int main(void){
 for(unsigned s=0;s<2;s++){
  unsigned slot=s?50:0,record=s?282:285,ani=s?6:8,weapon=s?59:24;
  la_slots[slot].live=true;la_slots[slot].record=record;la_slots[slot].cycle=1;la_slots[slot].gate=2;
  enemy[slot].enemycycle=1;enemy[slot].aniactive=2;
  fc_frame++;render_mirror_late_actor_enemy_animated(slot);assert(!retired);
  /* Full shot pool: no observer is called and idle state remains unchanged. */
  fc_frame++;render_mirror_late_actor_enemy_animated(slot);assert(la_slots[slot].gate==2);
  enemy[slot].aniactive=1;render_mirror_late_actor_shot_fired(slot,weapon,1,0);assert(!retired&&la_slots[slot].gate==1);
  for(unsigned c=2;c<=ani;c++){
   fc_frame++;enemy[slot].enemycycle=c;enemy[slot].aniactive=c==ani?2:1;
   render_mirror_late_actor_enemy_animated(slot);assert(!retired&&la_slots[slot].cycle==c);
  }
  enemy[slot].aniactive=1;render_mirror_late_actor_shot_fired(slot,weapon,1,0);
  fc_frame++;enemy[slot].enemycycle=1;render_mirror_late_actor_enemy_animated(slot);assert(!retired&&la_slots[slot].cycle==1);
 }
 assert(la_shot_resumptions==4);return 0;
}
''')

    def test_independent_hooks_and_fail_closed_scope(self):
        native=(SRC/'tyrian2.c').read_text();canvas=(SRC/'b313_family_canvas_mirror.inc').read_text()
        self.assertIn('!f284_stream_matches(events)',TEXT);self.assertIn('la_script.next=1',TEXT)
        self.assertNotIn('la_extra_owner',TEXT);self.assertNotIn('la_extra_cell',TEXT)
        self.assertIn('if(image==3)continue',TEXT);self.assertIn('i!=3&&!la_load(i)',TEXT)
        self.assertNotIn('la_scope()',function('la_write_current'))
        for name in ('f284','tp','ln','lp287','la'):
            self.assertLess(canvas.index(name+'_retire((unsigned)off,style)'),canvas.index('if(f284_pixel'))
        self.assertIn('render_mirror_late_actor_event_begin(eventLoc,0,50,0)',native)
        self.assertIn('render_mirror_late_actor_event_begin(eventLoc,0,0,0)',native)
        self.assertIn('render_mirror_late_actor_retired(x); enemyAvail[x] = 1;',native)
        before=native.index('render_mirror_late_actor_script_before(facts_event_entry);')
        after=native.index('render_mirror_late_actor_script_after(facts_event_entry);')
        self.assertLess(before,after);self.assertLess(after,native.index('eventLoc++;',after))
        shot=native.index('render_mirror_late_actor_shot_fired(i,temp3,j,b);')
        self.assertLess(native.rindex('if (enemy[i].aniactive == 2)',0,shot),shot)
        self.assertLess(native.rindex('enemyShotAvail[b] = !enemyShotAvail[b];',0,shot),shot)

if __name__=='__main__':unittest.main()
