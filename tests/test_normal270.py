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
TEXT=(SRC/'normal270_family_mirror.inc').read_text()
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


class Normal270Tests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_three_native_images_alpha_holes_and_retirement(self):
        source=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "normal270_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
#include "normal270_native.inc"
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
#define FC_ORDER 1
#define OHS_SURVIVAL_WRITE(...) ((void)0)
static uint8_t f270_owned[64000],f270_shadows[64000],selected[64000],expected[64000],native[64000];
static uint8_t hd_owner[4096000],cloud_owner[4096000];static unsigned green_first[4096000];static uint32_t rgb[4096000];
static struct {void *pixels;} surface={rgb},*canvas=&surface;static void *fc_source_pixels=native;
static struct {bool active,pending,contributed;unsigned slot,part,pixels,image;Normal270Draw draw[100];Normal270Write writes[100][672];} f270_frame;
static uint64_t f270_blend_retirements,f270_normal_retirements,f270_shadow_writes,f270_contract_faults;
static unsigned failure,clears;
typedef struct {uint8_t *rgba;} Asset;static uint8_t rgba[172032];static struct {Asset member[15];} f270_resources;
static void f270_fail(unsigned r){failure=r;f270_frame.active=f270_frame.pending=false;}
static void family_fault(unsigned r){(void)r;}
static void enemy_filter_rgba(const Uint8 *src,Uint8 filter,Uint8 *dst){(void)filter;memcpy(dst,src,4);}
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
'''+'\n'.join(function(n) for n in ('f270_retire','f270_pixel','f270_shadow'))+r'''
int main(void){
 assert(f270_records[4].record==270);
 for(unsigned i=0;i<172032;i+=4){rgba[i]=60;rgba[i+1]=80;rgba[i+2]=120;rgba[i+3]=(i/4)%192%8==0?0:127;}
 unsigned total=0;
 for(unsigned image=12;image<15;image++){
  for(unsigned n=0;n<4096000;n++)rgb[n]=0xff204060;
  memset(f270_owned,0,sizeof f270_owned);
  memset(&f270_frame,0,sizeof f270_frame);f270_frame.slot=25;f270_frame.image=image;f270_frame.pending=true;f270_frame.contributed=true;
  f270_resources.member[image].rgba=rgba;Normal270Draw *d=f270_frame.draw+25;d->x=40;d->y=20;
  total+=f270_totals[image];
  for(unsigned k=0;k<4;k++){
   f270_frame.part=k;f270_frame.active=true;f270_frame.pixels=0;
   for(unsigned i=0;i<f270_counts[image][k];i++){
    const Normal270Write *w=f270_native[image][k]+i;
    unsigned x=d->x+f270_px[k]+w->x,y=d->y+f270_py[k]+w->y,off=y*320+x;
    native[off]=expected[off]=w->index;assert(f270_pixel(x,y,MIRROR_NORMAL)&&!failure);
    assert(f270_owned[off]==26&&selected[off]&&rgb[y*8*2560+x*8]==0xff204060);
   }
  }
  assert(d->callback_count==f270_totals[image]);
  unsigned holes=0;
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(!f270_owned[(y+20)*320+x+40]){
   assert(rgb[(y+20)*8*2560+(x+40)*8]==0xff204060);holes++;
  }
  assert(holes==672-f270_totals[image]);
  const Normal270Write *w=f270_native[image][0];
  unsigned off=(20+w->y)*320+40+w->x;assert(f270_retire(off,MIRROR_SHADOW)&&f270_owned[off]==26);f270_shadow(off);assert(f270_shadows[off]==1);
  assert(f270_retire(off,MIRROR_BLEND)&&!f270_owned[off]&&!f270_shadows[off]);
  f270_owned[off]=26;assert(f270_retire(off,MIRROR_NORMAL)&&!f270_owned[off]);
 }
 assert(clears==total*5&&f270_blend_retirements==3&&f270_normal_retirements==3&&f270_shadow_writes==3);
 f270_frame.part=0;f270_frame.pixels=0;f270_frame.active=true;assert(f270_pixel(0,0,MIRROR_NORMAL)&&failure==16);
 return 0;
}
'''
        run_c(source)

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_only_two_original_admissions_in_window(self):
        run_c(r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
struct JE_EventRecType {unsigned eventtime,eventtype;int eventdat,eventdat2,eventdat3;uint8_t eventdat4;int eventdat5,eventdat6;};
static struct JE_EventRecType eventRec[731];static unsigned maxEvent=731,eventLoc,curLoc;
static struct {bool loaded,exhausted;uint64_t epoch,serial;unsigned consumed;const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned record,event,component;int slot;} call;
} f270_life;
static struct {bool active;unsigned event;} f270_script;
static bool f270_scope(void){return f270_life.loaded&&curLoc<1960&&eventLoc<=259;}
static void f270_fail(unsigned r){(void)r;assert(0);}
'''+function('f270_event_matches')+function('render_mirror_normal270_event_begin')+r'''
int main(void){
 f270_life.loaded=true;f270_life.events=eventRec;
 eventRec[243]=(struct JE_EventRecType){1896,6,270,90,0,0,0,0};
 eventRec[244]=(struct JE_EventRecType){1896,6,270,162,0,0,0,0};
 eventRec[241]=(struct JE_EventRecType){1840,12,309,66,0,24,0,0};
 assert(!f270_event_matches(242));
 for(unsigned e=244;e<=245;e++){
  eventLoc=e;curLoc=1896;f270_script.event=e;
  assert(!render_mirror_normal270_event_begin(e,0,25,0));f270_script.active=true;
  assert(!render_mirror_normal270_event_begin(e,1,25,0));
  assert(!render_mirror_normal270_event_begin(e,0,50,0));
  assert(render_mirror_normal270_event_begin(e,0,25,0));
  f270_life.call.live=false;assert(!render_mirror_normal270_event_begin(e,0,25,0));f270_script.active=false;
 }
 assert(f270_life.consumed==3&&f270_life.serial==2);
 curLoc=1960;assert(!f270_scope());curLoc=1959;eventLoc=260;assert(!f270_scope());return 0;
}
''')

    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_dual_weapon_six_cycle_resume(self):
        run_c(r'''
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "normal270_family.h"
#define ENEMY_SHOT_MAX 60
static unsigned enemyShotAvail[60],retired;
static uint64_t fc_frame,f270_phase_observations,f270_shot_resumptions;
static struct {bool live;unsigned record,cycle,gate;uint64_t phase_tick,generation;Normal270Birth birth;} f270_slots[100];
static struct {unsigned enemycycle,aniactive;} enemy[100];
static struct {Normal270Draw draw[100];} f270_frame;
static bool f270_scope(void){return true;}static bool f270_witness(unsigned s){return f270_slots[s].live;}
static bool f270_shape(unsigned s,unsigned stage){(void)s;(void)stage;return true;}
static void render_mirror_normal270_retired(unsigned s,unsigned reason,unsigned source){(void)reason;(void)source;f270_slots[s].live=false;retired++;}
'''+function('render_mirror_normal270_enemy_animated')+function('render_mirror_normal270_shot_fired')+r'''
int main(void){
 unsigned s=25;f270_slots[s].live=true;f270_slots[s].record=270;f270_slots[s].cycle=1;f270_slots[s].gate=2;
 enemy[s].enemycycle=1;enemy[s].aniactive=2;fc_frame=1;render_mirror_normal270_enemy_animated(s);assert(!retired);
 /* No successful allocation: stay idle without a synthetic shot hook. */
 fc_frame++;render_mirror_normal270_enemy_animated(s);assert(f270_slots[s].gate==2);
 for(unsigned weapon=145;weapon<=146;weapon++){
  enemy[s].aniactive=1;render_mirror_normal270_shot_fired(s,weapon,weapon-144,0);assert(!retired);
  unsigned start=f270_slots[s].cycle==6?1:2;
  for(unsigned c=start;c<=6;c++){
   fc_frame++;enemy[s].enemycycle=c;enemy[s].aniactive=c==6?2:1;
   render_mirror_normal270_enemy_animated(s);assert(!retired&&f270_slots[s].cycle==c);
  }
 }
 assert(f270_shot_resumptions==2&&f270_slots[s].birth.shot_weapon_count[0]==1&&f270_slots[s].birth.shot_weapon_count[1]==1);
 return 0;
}
''')

    def test_scope_hooks_and_no_compound_admission(self):
        self.assertIn('r==270?4:-1',TEXT);self.assertIn('event<244||event>245',TEXT)
        self.assertIn('for(unsigned i=12;i<15;i++)',TEXT)
        self.assertIn('!f284_stream_matches(events)',TEXT);self.assertIn('f270_script.active',TEXT)
        self.assertIn('curLoc<1960',TEXT);self.assertIn('eventLoc<=259',TEXT)
        self.assertNotIn('stamp(',function('f270_write_current'))
        native=(SRC/'tyrian2.c').read_text();canvas=(SRC/'b313_family_canvas_mirror.inc').read_text()
        for phase in ('before','after'):self.assertIn(f'render_mirror_normal270_script_{phase}(facts_event_entry);',native)
        self.assertIn('render_mirror_normal270_shot_fired(i,temp3,j,b);',native)
        for name in ('f284','tp','ln','lp287','la','f270'):
            self.assertLess(canvas.index(name+'_retire((unsigned)off,style)'),canvas.index('if(f284_pixel'))
        self.assertIn('!f270_finish()',canvas);self.assertIn('!f270_guard()',canvas)

if __name__=='__main__':unittest.main()
