"""Extract the eighteen-origin tank birth selector and actual sparse writer/finish guards.

Event steps, actor/lifetime receipts and draw setup are synthetic. Scope,
witness/shape, source/palette/resource readiness and other-owner clears are
stubs. No constructor, event execution, native RLE, RNG, or game is run.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from test_smallrocks_family import function, ROOT, SRC


class Tank194Tests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'requires C compiler')
    def test_actual_minimal_birth_selector_and_eight_pose_writers(self):
        source = (SRC / 'tank194_family_mirror.inc').read_text()
        declarations = source[source.index('typedef struct {'):source.index('static const char *t194_root')]
        self.assertIn('(event>258u)', source)
        self.assertNotIn('TANK194_REPEAT8_ENABLE', source)
        names = ('t194_birth_index', 't194_event_matches', 't194_events_current', 't194_fail',
                 'render_mirror_tank194_family_event_before', 'render_mirror_tank194_family_event_after',
                 'render_mirror_tank194_family_event_begin', 't194_dependencies', 't194_finish',
                 't194_retire', 't194_pixel', 't194_shadow', 't194_end')
        functions = '\n'.join(function(source, name) for name in names)
        blend = function((SRC / 'render_mirror.c').read_text(), 'blend_rgba')
        stamp = function((ROOT / 'src/asteroid1_ten_mirror.inc').read_text(), 'asteroid1_stamp')
        harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "tank194_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {uint8_t *data;size_t size;} Sprite2_array;
typedef struct {uint8_t *rgba;} Asset;
static struct {Sprite2_array *sprite2s;unsigned enemycycle,eshotwait[3];} enemy[100];
struct JE_EventRecType {unsigned eventtime,eventtype;int eventdat,eventdat2,eventdat3,eventdat4,eventdat5,eventdat6;};
NATIVE
DECLARATIONS
static bool scope_ok=true,writer_ok=true;
static bool ready,last_output_valid,last_output_scene_hd,have_fade_saved;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference;
static unsigned eventLoc,curLoc,maxEvent=731;static int mapX=1;
static int fade_mode,faults;
static bool t194_events_current(void);
static bool t194_scope(void){return scope_ok&&!t194_life.stream_broken&&t194_events_current();}
static bool t194_shape(unsigned slot,unsigned stage){(void)slot;(void)stage;return true;}
static bool t194_witness(unsigned slot){return slot==75;}
static bool t194_colors(void){return true;}
static bool t194_resources_current(void){return true;}
static bool t194_targets(unsigned type,const int *data,unsigned slot){(void)type;(void)data;(void)slot;return false;}
static T194Script t194_script(unsigned slot){(void)slot;return (T194Script){0};}
static bool t194_script_equal(T194Script a,T194Script b){return !memcmp(&a,&b,sizeof a);}
static void render_mirror_tank194_family_retired(unsigned slot){t194_slots[slot].live=false;}
#define FC_SOURCE 1
#define FC_ORDER 2
#define MIRROR_NORMAL 0
#define MIRROR_BLEND 1
#define MIRROR_SHADOW 2
static void family_fault(int cause){(void)cause;++faults;}
static bool b313_family_writer_draw_ready(unsigned frame){(void)frame;return writer_ok;}
static unsigned fc_frame=1;
static uint8_t expected[64000],source_pixels[64000],hd_owner[4096000],cloud_owner[4096000],green_first[4096000],selected[64000];
static void *fc_source_pixels=source_pixels;
static struct {void *pixels;} storage,*canvas=&storage;
#define lamp272_clear(x) ((void)(x))
#define triple275_clear(x) ((void)(x))
#define private_ember269_clear(x) ((void)(x))
#define gray325_clear(x) ((void)(x))
#define longface573_clear(x) ((void)(x))
STAMP
BLEND
FUNCTIONS
static void reset_draw(unsigned pose,Sprite2_array *bank){
 memset(&t194_frame,0,sizeof t194_frame);faults=0;t194_first_reason=0;
 t194_life.epoch=7;enemy[75].sprite2s=bank;enemy[75].enemycycle=pose+1;
 t194_slots[75].generation=1;t194_slots[75].script_serial=1;t194_slots[75].script_event=6;
 t194_slots[75].birth.token=1;t194_slots[75].birth.event=6;
 t194_frame.slot=75;t194_frame.pending=t194_frame.contributed=true;
 t194_frame.draw[0]=(Tank194Draw){.frame=fc_frame,.epoch=7,.token=1,.generation=1,.script_serial=1,
 .script_event=6,.slot=75,.event=6,.record=194,.base=t194_bases[pose],.pose=pose,
 .bank_object=(uintptr_t)bank,.bank_data=(uintptr_t)bank->data,.x=24,.y=40};
}
static Uint32 reference_blend(Uint32 before,const uint8_t *rgba){
 uint32_t result=0xff000000;
 for(unsigned c=0;c<3;c++){
  unsigned channel=(before>>(16-c*8))&255;
  result|=((channel*(255-rgba[3])+rgba[c]*rgba[3]+127)/255)<<(16-c*8);
 }
 return result;
}
static struct JE_EventRecType rows[258];
static void prepare_events(void){
 memset(&t194_life,0,sizeof t194_life);memset(t194_slots,0,sizeof t194_slots);
 t194_life.epoch=7;t194_life.loaded=true;t194_life.events=rows;
 for(unsigned n=0;n<258;n++){
  const int *d=t194_events[n].d;
  rows[n]=(struct JE_EventRecType){t194_events[n].time,t194_events[n].type,d[0],d[1],d[2],d[3],d[4],d[5]};
 }
 eventLoc=t194_life.next_event=106;curLoc=t194_events[105].time;
}
int main(int argc,char **argv){
 assert(argc==9);assert(sizeof t194_events/sizeof t194_events[0]==258);
 prepare_events();
 render_mirror_tank194_family_event_before(106);assert(t194_life.step.live&&t194_life.step.d[5]==4);
 rows[105].eventdat6=0;render_mirror_tank194_family_event_after(106);
 assert(!t194_life.stream_broken&&t194_life.next_event==107&&t194_life.mutated106_epoch==7);
 assert(t194_event_matches(106,false)&&!t194_event_matches(106,true));
 ++t194_life.epoch;assert(!t194_event_matches(106,false));
 prepare_events();rows[105].eventdat6=0;
 render_mirror_tank194_family_event_before(106);assert(t194_life.stream_broken&&!t194_life.step.live&&!t194_life.mutated106_epoch);
 /* A receipt may change only dat6, in the same epoch/time and type12. */
 for(unsigned bad=0;bad<9;bad++){
  prepare_events();render_mirror_tank194_family_event_before(106);assert(t194_life.step.live);
  rows[105].eventdat6=0;
  if(bad==0)++t194_life.step.epoch;
  else if(bad==1)++curLoc;
  else if(bad==2)++rows[105].eventtime;
  else if(bad==3)++rows[105].eventtype;
  else if(bad==4)++rows[105].eventdat;
  else if(bad==5)++rows[105].eventdat2;
  else if(bad==6)++rows[105].eventdat3;
  else if(bad==7)++rows[105].eventdat4;
  else ++rows[105].eventdat5;
  render_mirror_tank194_family_event_after(106);
  assert(t194_life.stream_broken&&!t194_life.mutated106_epoch);
 }
 /* Each later type12 row needs its own actual same-epoch receipt. */
 const unsigned receipt_rows[2]={230,240};
 for(unsigned k=0;k<2;k++){
  unsigned event=receipt_rows[k],other=receipt_rows[1-k];
  prepare_events();eventLoc=t194_life.next_event=event;curLoc=t194_events[event-1].time;
  render_mirror_tank194_family_event_before(event);assert(t194_life.step.live&&t194_life.step.d[5]==4);
  rows[event-1].eventdat6=0;render_mirror_tank194_family_event_after(event);
  assert(!t194_life.stream_broken&&t194_life.next_event==event+1&&t194_life.mutated_next7_epoch[k]==7);
  assert(!t194_life.mutated_next7_epoch[1-k]);
  assert(t194_event_matches(event,false)&&!t194_event_matches(event,true));
  rows[other-1].eventdat6=0;assert(!t194_event_matches(other,false));rows[other-1].eventdat6=4;
  ++t194_life.epoch;assert(!t194_event_matches(event,false));
  prepare_events();eventLoc=t194_life.next_event=event;curLoc=t194_events[event-1].time;
  rows[event-1].eventdat6=0;render_mirror_tank194_family_event_before(event);
  assert(t194_life.stream_broken&&!t194_life.step.live&&!t194_life.mutated_next7_epoch[k]);
  for(unsigned bad=0;bad<9;bad++){
   prepare_events();eventLoc=t194_life.next_event=event;curLoc=t194_events[event-1].time;
   render_mirror_tank194_family_event_before(event);assert(t194_life.step.live);
   struct JE_EventRecType *r=&rows[event-1];r->eventdat6=0;
   if(bad==0)++t194_life.step.epoch;
   else if(bad==1)++curLoc;
   else if(bad==2)++r->eventtime;
   else if(bad==3)++r->eventtype;
   else if(bad==4)++r->eventdat;
   else if(bad==5)++r->eventdat2;
   else if(bad==6)++r->eventdat3;
   else if(bad==7)++r->eventdat4;
   else ++r->eventdat5;
   render_mirror_tank194_family_event_after(event);
   assert(t194_life.stream_broken&&!t194_life.mutated_next7_epoch[k]);
  }
 }
 prepare_events();eventLoc=t194_life.next_event=259;
 render_mirror_tank194_family_event_before(259);assert(t194_life.stream_broken&&!t194_life.step.live);
 prepare_events();
 for(unsigned event=0;event<=259;event++){
  const unsigned allowed[]={6,25,26,36,37,76,77,78,89,90,91,177,208,209,210,211,246,247};
  int wanted=-1;for(unsigned n=0;n<18;n++)if(event==allowed[n])wanted=(int)n;
  assert(t194_birth_index(event)==wanted);
 }
 const unsigned births[18]={6,25,26,36,37,76,77,78,89,90,91,177,208,209,210,211,246,247};
 for(unsigned i=0;i<18;i++){
  unsigned event=births[i];eventLoc=event;curLoc=t194_events[event-1].time;
  t194_life.step.live=true;t194_life.step.event=event;
  assert(!render_mirror_tank194_family_event_begin(event,1,75,0));
  assert(!render_mirror_tank194_family_event_begin(event,0,0,0));
  assert(!render_mirror_tank194_family_event_begin(event,0,75,1));
  uint64_t token=render_mirror_tank194_family_event_begin(event,0,75,0);assert(token);
  assert(t194_life.call.event==event&&t194_life.call.slot==-1);
  /* Simulate the outside allocation attempt closing; do not model its constructor. */
  t194_life.call.live=false;
  assert(!render_mirror_tank194_family_event_begin(event,0,75,0));
 }
 assert(t194_life.consumed==262143);
 eventLoc=248;t194_life.step.event=248;
 assert(!render_mirror_tank194_family_event_begin(248,0,75,0));
 uint8_t bank_bytes[1]={0};Sprite2_array bank={bank_bytes,1};
 canvas->pixels=malloc(4096000*sizeof(Uint32));assert(canvas->pixels);
 unsigned writes=0,alpha_zero=0,partial_alpha=0;
 for(unsigned pose=0;pose<8;pose++){
  uint8_t header[28];FILE *f=fopen(argv[pose+1],"rb");assert(f);
  assert(fread(header,1,28,f)==28&&!memcmp(header,"HDR1",4));
  uint32_t values[6]={0};for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)values[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
  assert(values[0]==1010000+t194_art[pose]&&values[1]==8&&values[2]==24&&values[3]==28&&values[4]==6&&values[5]==7);
  uint8_t *rgba=malloc(172032);assert(rgba);assert(fread(rgba,1,172032,f)==172032&&fgetc(f)==EOF);fclose(f);
  assert(asteroid1_stamp(rgba,172032)==t194_art_stamp[pose]);t194_resources.member[pose].rgba=rgba;
  reset_draw(pose,&bank);
  for(unsigned n=0;n<4096000;n++)((Uint32*)canvas->pixels)[n]=0xff204060u;
  memset(hd_owner,0,sizeof hd_owner);memset(t194_owned,0,sizeof t194_owned);
  bool touched[672]={false};
  for(unsigned part=0;part<4;part++){
   t194_frame.active=true;t194_frame.part=part;t194_frame.pixels=0;
   for(unsigned n=0;n<t194_counts[pose][part];n++){
    const Tank194Write *w=&t194_native[pose][part][n];
    unsigned lx=t194_px[part]+w->x,ly=t194_py[part]+w->y;assert(lx<24&&ly<28&&!touched[ly*24+lx]);touched[ly*24+lx]=true;
    unsigned x=24+lx,y=40+ly;source_pixels[y*320+x]=expected[y*320+x]=w->index;
    assert(t194_pixel(x,y,MIRROR_NORMAL));writes++;
    assert(t194_owned[y*320+x]==76&&selected[y*320+x]);
    for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
     const uint8_t *art=rgba+(((ly*8+sy)*192+lx*8+sx)*4);unsigned off=(y*8+sy)*2560+x*8+sx;
     assert(((Uint32*)canvas->pixels)[off]==reference_blend(0xff204060u,art)&&hd_owner[off]);
     alpha_zero+=art[3]==0;partial_alpha+=art[3]>0&&art[3]<255;
    }
   }
   t194_end();assert(!faults&&!t194_frame.active);
   if(part<3)assert(!t194_finish()&&t194_frame.pending);
  }
  assert(t194_finish()&&t194_frame.draw[0].complete&&t194_frame.draw[0].mask==15&&!t194_frame.pending);
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(!touched[y*24+x]){
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned off=((40+y)*8+sy)*2560+(24+x)*8+sx;
    assert(((Uint32*)canvas->pixels)[off]==0xff204060u&&!hd_owner[off]);
   }
  }
  ++t194_slots[75].script_serial;assert(!t194_finish());--t194_slots[75].script_serial;assert(t194_finish());
  reset_draw(pose,&bank);t194_frame.active=true;t194_end();assert(faults&&t194_frame.fault&&!t194_finish());
  reset_draw(pose,&bank);t194_frame.active=true;assert(t194_pixel(999,999,MIRROR_NORMAL)&&faults&&t194_frame.fault);
  reset_draw(pose,&bank);t194_frame.active=true;assert(t194_pixel(24,40,MIRROR_BLEND)&&faults&&t194_frame.fault);
  reset_draw(pose,&bank);assert(t194_pixel(24,40,MIRROR_NORMAL)&&t194_frame.fault);
  free(rgba);
 }
 assert(writes==1196&&alpha_zero);
 unsigned cell=40*320+24;t194_owned[cell]=76;t194_shadows[cell]=0;
 assert(t194_retire(cell,MIRROR_SHADOW)&&t194_owned[cell]);for(unsigned n=0;n<300;n++)t194_shadow(cell);assert(t194_shadows[cell]==255);
 assert(t194_retire(cell,MIRROR_BLEND)&&!t194_owned[cell]&&!t194_shadows[cell]);
 t194_owned[cell]=76;assert(t194_retire(cell,MIRROR_NORMAL)&&!t194_owned[cell]);assert(!t194_retire(64000,MIRROR_NORMAL));
 free(canvas->pixels);
 printf("PASS: 18 pinned births / event106+230+240 receipts / stop259, 8 pose materials, %u writes, %u alpha0 / %u partial-alpha subpixels; order/retirement\n",writes,alpha_zero,partial_alpha);
 return 0;
}
'''
        for key, value in [('DECLARATIONS', declarations), ('NATIVE', (SRC / 'tank194_native.inc').read_text()),
                           ('STAMP', stamp), ('BLEND', blend), ('FUNCTIONS', functions)]:
            harness = re.sub(r'\b' + key + r'\b', lambda _: value, harness)
        # Runtime uses the existing public eight-heading artwork; no image copies.
        asset_root = ROOT / 'assets/hd/artwork/type15-eightheading-smooth-contour-v2/output'
        with tempfile.TemporaryDirectory() as temp:
            c, binary = Path(temp)/'tank194.c', Path(temp)/'tank194'
            c.write_text(harness)
            subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-variable',
                            '-pedantic', '-I', str(SRC), str(c), '-o', str(binary)], check=True)
            subprocess.run([str(binary)]+[str(asset_root/f'enemy-newsh2-{index}-8.hda')
                                          for index in (91,45,93,39,43,129,41,131)], check=True)


if __name__ == '__main__':
    unittest.main()
