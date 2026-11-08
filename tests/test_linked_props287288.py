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
TEXT=(SRC/'linked_prop287288_family_mirror.inc').read_text()
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


class LinkedPropsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_three_native_images_alpha_holes_and_retirement(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "linked_prop287288_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
#include "linked_prop287288_native.inc"
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
#define FC_ORDER 1
#define OHS_SURVIVAL_WRITE(...) ((void)0)
static uint8_t lp287_owned[64000],lp287_shadows[64000],selected[64000],expected[64000],native[64000];
static uint8_t hd_owner[4096000],cloud_owner[4096000];static unsigned green_first[4096000];static uint32_t rgb[4096000];
static struct {void *pixels;} surface={rgb},*canvas=&surface;static void *fc_source_pixels=native;
static struct {bool active,pending,contributed;unsigned slot,part,pixels,image;LinkedProp287288Draw draw[100];LinkedProp287288Write writes[100][672];} lp287_frame;
static uint64_t lp287_blend_retirements,lp287_normal_retirements,lp287_shadow_writes,lp287_contract_faults;
static unsigned failure,clears;
typedef struct {uint8_t *rgba;} Asset;static uint8_t rgba[172032];static struct {Asset member[3];} lp287_resources;
static void lp287_fail(unsigned r){failure=r;lp287_frame.active=lp287_frame.pending=false;}
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
'''+'\n'.join(function(n) for n in ('lp287_retire','lp287_pixel','lp287_shadow'))+r'''
int main(void){
 assert(lp287_records[0].record==287&&lp287_records[1].record==288);
 for(unsigned i=0;i<172032;i+=4){rgba[i]=60;rgba[i+1]=80;rgba[i+2]=120;rgba[i+3]=(i/4)%192%8==0?0:127;}
 unsigned total=0;
 for(unsigned image=0;image<3;image++){
  for(unsigned n=0;n<4096000;n++)rgb[n]=0xff204060;
  memset(lp287_owned,0,sizeof lp287_owned);
  memset(&lp287_frame,0,sizeof lp287_frame);lp287_frame.slot=25;lp287_frame.image=image;lp287_frame.pending=true;lp287_frame.contributed=true;
  lp287_resources.member[image].rgba=rgba;LinkedProp287288Draw *d=lp287_frame.draw+25;d->x=40;d->y=20;
  total+=lp287_totals[image];
  for(unsigned k=0;k<4;k++){
   lp287_frame.part=k;lp287_frame.active=true;lp287_frame.pixels=0;
   for(unsigned i=0;i<lp287_counts[image][k];i++){
    const LinkedProp287288Write *w=lp287_native[image][k]+i;
    unsigned x=d->x+lp287_px[k]+w->x,y=d->y+lp287_py[k]+w->y,off=y*320+x;
    native[off]=expected[off]=w->index;assert(lp287_pixel(x,y,MIRROR_NORMAL)&&!failure);
    assert(lp287_owned[off]==26&&selected[off]&&rgb[y*8*2560+x*8]==0xff204060);
   }
  }
  assert(d->callback_count==lp287_totals[image]);
  unsigned holes=0;
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(!lp287_owned[(y+20)*320+x+40]){
   assert(rgb[(y+20)*8*2560+(x+40)*8]==0xff204060);holes++;
  }
  assert(holes==672-lp287_totals[image]);
  const LinkedProp287288Write *w=lp287_native[image][0];
  unsigned off=(20+w->y)*320+40+w->x;assert(lp287_retire(off,MIRROR_SHADOW)&&lp287_owned[off]==26);lp287_shadow(off);assert(lp287_shadows[off]==1);
  assert(lp287_retire(off,MIRROR_BLEND)&&!lp287_owned[off]&&!lp287_shadows[off]);
  lp287_owned[off]=26;assert(lp287_retire(off,MIRROR_NORMAL)&&!lp287_owned[off]);
 }
 assert(clears==total*5&&lp287_blend_retirements==3&&lp287_normal_retirements==3&&lp287_shadow_writes==3);
 lp287_frame.part=0;lp287_frame.pixels=0;lp287_frame.active=true;assert(lp287_pixel(0,0,MIRROR_NORMAL)&&failure==16);
 return 0;
}
'''
        run_c(source)

    def test_launcher_narrow_opt_in_and_asset_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);b=p/'never-run';b.write_text('');b.chmod(0o700)
            args=['--data',temp,'--binary',str(b)]
            inherited={'LINKED_PROP287288_ENABLE':'1','LINKED_PROP287288_ASSET_DIR':'wrong'}
            for flags in ([],['--hd']):
                plan,env=launcher.build_plan(launcher.parser().parse_args(args+flags),inherited)
                self.assertFalse(plan['linked_props_enabled'])
                self.assertFalse(any(k.startswith('LINKED_PROP287288_') for k in env))
            with self.assertRaisesRegex(ValueError,'requires --hd'):
                launcher.build_plan(launcher.parser().parse_args(args+['--linked-props']),{})
            plan,env=launcher.build_plan(launcher.parser().parse_args(args+['--hd','--linked-props','--fork284','--turret273','--linked338']),{})
            self.assertEqual(plan['linked_props_assets_sha256_verified'],3)
            self.assertEqual(env['LINKED_PROP287288_ENABLE'],'1');self.assertFalse(plan['game_started'])
            self.assertEqual(set(launcher.LINKED_PROPS_SHA256),{245,281,283})
            directory=p/launcher.REUSED_ROOT;directory.mkdir(parents=True)
            for base in launcher.LINKED_PROPS_SHA256:
                name=f'enemy-newshd-{base}-8.hda';raw=(ROOT/launcher.REUSED_ROOT/name).read_bytes()
                self.assertEqual(len(raw),172060);(directory/name).write_bytes(raw)
            f=directory/'enemy-newshd-283-8.hda';raw=f.read_bytes();f.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
            with patch.object(launcher,'verify_assets',return_value=52),self.assertRaises(ValueError):
                launcher.build_plan(launcher.parser().parse_args(args+['--hd','--linked-props']),{},p)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_six_independent_origins_and_failed_allocations(self):
        origins=TEXT[TEXT.index('static const struct {unsigned event,time,record;'):TEXT.index('static bool lp287_scope')]
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#define COUNTOF(a) (sizeof(a)/sizeof((a)[0]))
struct JE_EventRecType {unsigned eventtime,eventtype;int eventdat,eventdat2,eventdat3;unsigned eventdat4;int eventdat5,eventdat6;};
static struct JE_EventRecType eventRec[731];
static unsigned maxEvent=731,eventLoc,curLoc,failures;
static struct {bool loaded,exhausted;unsigned mode,consumed;uint64_t serial,epoch;const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned record,event;int slot;} call;
} lp287_life;
static bool lp287_scope(void){return lp287_life.loaded&&!lp287_life.exhausted;}
static void lp287_fail(unsigned r){(void)r;failures++;}
'''+origins+function('render_mirror_linked_prop287288_event_begin')+r'''
int main(void){
 lp287_life.loaded=true;lp287_life.mode=6;lp287_life.events=eventRec;
 for(unsigned i=0;i<6;i++){
  eventLoc=lp287_origins[i].event;curLoc=lp287_origins[i].time;
  struct JE_EventRecType *r=eventRec+eventLoc-1;
  *r=(struct JE_EventRecType){curLoc,6,(int)lp287_origins[i].record,lp287_origins[i].x,0,(int)lp287_origins[i].link,lp287_origins[i].y,0};
  assert(lp287_event_matches(eventLoc));r->eventdat4++;assert(!lp287_event_matches(eventLoc));r->eventdat4--;
  assert(!render_mirror_linked_prop287288_event_begin(eventLoc,1,25,0));
  assert(!render_mirror_linked_prop287288_event_begin(eventLoc,0,50,0));
  assert(!render_mirror_linked_prop287288_event_begin(eventLoc,0,25,1));
  assert(render_mirror_linked_prop287288_event_begin(eventLoc,0,25,0));
  assert(lp287_life.call.record==lp287_origins[i].record);
  /* Simulate failed allocation: no partner is ever created. */
  lp287_life.call.live=false;
  assert(!render_mirror_linked_prop287288_event_begin(eventLoc,0,25,0));
 }
 assert(lp287_life.consumed==63&&lp287_life.serial==6&&!failures);
 lp287_life.events=0;assert(!lp287_event_matches(183));return 0;
}
'''
        run_c(source)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_animation_and_hit_receipts_do_not_mutate_gameplay(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "linked_prop287288_family.h"
static struct {bool live;unsigned record,cycle;uint64_t phase_tick;LinkedProp287288Birth birth;} lp287_slots[100];
static struct {unsigned enemycycle,linknum,armorleft;} enemy[100];static unsigned enemyAvail[100];
static struct {uint64_t hit_serial;struct {bool live;uint64_t token;unsigned slot,link,damage,armor,shot;} hit;} lp287_life;
static uint64_t fc_frame,lp287_phase_observations,lp287_hit_count;static unsigned retired;
static bool lp287_scope(void){return true;}
static bool lp287_witness(unsigned s){return lp287_slots[s].live;}
static bool lp287_shape(unsigned s,unsigned stage){(void)s;(void)stage;return true;}
static void render_mirror_linked_prop287288_retired(unsigned s,unsigned reason,unsigned source){(void)reason;(void)source;retired++;lp287_slots[s].live=false;}
'''+''.join(function(n) for n in ('render_mirror_linked_prop287288_enemy_animated','render_mirror_linked_prop287288_hit_begin','render_mirror_linked_prop287288_hit_end'))+r'''
int main(void){
 lp287_slots[25].live=lp287_slots[26].live=true;
 lp287_slots[25].record=287;lp287_slots[25].cycle=1;lp287_slots[26].record=288;
 for(unsigned tick=1;tick<=40;tick++){
  fc_frame=tick;enemy[25].enemycycle=1;enemy[26].enemycycle=(tick-1)%20+1;
  render_mirror_linked_prop287288_enemy_animated(25);render_mirror_linked_prop287288_enemy_animated(26);
  assert(!retired&&lp287_slots[26].cycle==enemy[26].enemycycle);
 }
 assert(lp287_phase_observations==80);
 enemy[25].linknum=22;enemy[25].armorleft=10;lp287_slots[25].birth.link=22;
 render_mirror_linked_prop287288_hit_begin(25,4,7);
 assert(lp287_life.hit.live&&lp287_life.hit.damage==4&&enemy[25].armorleft==10);
 enemy[25].armorleft=6;render_mirror_linked_prop287288_hit_end();
 assert(!lp287_life.hit.live&&lp287_slots[25].birth.hit_armor_after==6);
 /* Native linked source can be outside this rendered family. */
 enemy[50].linknum=22;enemy[50].armorleft=2;render_mirror_linked_prop287288_hit_begin(50,4,8);
 assert(lp287_life.hit.live&&lp287_life.hit.slot==50&&enemy[50].armorleft==2);
 render_mirror_linked_prop287288_hit_end();assert(lp287_hit_count==2);
 render_mirror_linked_prop287288_enemy_animated(25);assert(retired==1);
 return 0;
}
'''
        run_c(source)

    def test_hooks_and_fail_closed_boundaries(self):
        native=(SRC/'tyrian2.c').read_text();canvas=(SRC/'b313_family_canvas_mirror.inc').read_text()
        self.assertNotIn('late_reuse_',TEXT)
        self.assertIn('!f284_stream_matches(events)',TEXT)
        self.assertIn('lp287_write_current()',canvas)
        self.assertNotIn('dependencies',function('lp287_write_current'))
        for name in ('f284','tp','ln','lp287'):
            self.assertLess(canvas.index(name+'_retire((unsigned)off,style)'),canvas.index('if(f284_pixel'))
        begin=native.index('render_mirror_linked_prop287288_hit_begin(b,damage,z);')
        self.assertLess(native.index('int armorleft = enemy[b].armorleft;'),begin)
        end=native.index('render_mirror_linked_prop287288_hit_end();',begin)
        for reason in ('LP287_DAMAGE_TRANSFORM','LP287_DIRECT_LETHAL','LP287_LINKED_LETHAL'):
            self.assertLess(begin,native.index(reason));self.assertLess(native.index(reason),end)
        for reason in ('LP287_OFFSCREEN','LP287_EVENT_RETIRE'):
            self.assertIn(reason,native)
        self.assertIn('!lp287_finish()',canvas);self.assertIn('!lp287_guard()',canvas)

if __name__=='__main__':unittest.main()
