"""Extract the minimal tank birth selector and actual sparse writer/finish guards.

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
        self.assertIn('(event>75u)', source)
        self.assertNotIn('TANK194_REPEAT8_ENABLE', source)
        names = ('t194_birth_index', 't194_fail',
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
static struct {Sprite2_array *sprite2s;unsigned enemycycle;} enemy[100];
NATIVE
DECLARATIONS
static bool scope_ok=true,writer_ok=true;
static bool ready,last_output_valid,last_output_scene_hd,have_fade_saved;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference;
static unsigned eventLoc,curLoc;static int mapX=1;
static int fade_mode,faults;
static bool t194_scope(void){return scope_ok;}
static bool t194_shape(unsigned slot,unsigned stage){(void)slot;(void)stage;return true;}
static bool t194_witness(unsigned slot){return slot==75;}
static bool t194_colors(void){return true;}
static bool t194_resources_current(void){return true;}
static bool t194_event_matches(unsigned event,bool original){(void)event;(void)original;return true;}
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
int main(int argc,char **argv){
 assert(argc==9);assert(sizeof t194_events/sizeof t194_events[0]==75);
 for(unsigned event=0;event<=259;event++){
  int wanted=event==6?0:event==25?1:event==26?2:-1;
  assert(t194_birth_index(event)==wanted);
 }
 const unsigned births[3]={6,25,26};
 for(unsigned i=0;i<3;i++){
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
 assert(t194_life.consumed==7);
 eventLoc=36;curLoc=t194_events[35].time;t194_life.step.event=36;
 assert(!render_mirror_tank194_family_event_begin(36,0,75,0));
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
 printf("PASS: births6/25/26 only, 8 pose materials, %u writes, %u alpha0 / %u partial-alpha subpixels; order/retirement\n",writes,alpha_zero,partial_alpha);
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
