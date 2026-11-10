"""Actual random-prop lifecycle, four-part writer and retirement extraction.

Synthetic actor/frame setup; scope, shape, source/palette/resource readiness and
other-family clears are stubs. No native constructor/RLE, RNG or game is run.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from test_smallrocks_family import function, ROOT, SRC


class RandomPropsTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'requires C compiler')
    def test_actual_birth_quartet_writer_and_retirement(self):
        source = (SRC / 'random_props_family_mirror.inc').read_text()
        declarations = source[source.index('static struct {uint64_t generation'):source.index('static const char *rp_root')]
        names = ('rp_fail', 'render_mirror_random_props_retired', 'rp_slot',
                 'render_mirror_random_props_spawn_begin', 'render_mirror_random_props_enemy_allocated',
                 'render_mirror_random_props_enemy_initialized', 'render_mirror_random_props_spawn_commit',
                 'rp_witness', 'rp_dependencies', 'rp_finish', 'rp_before_tile', 'rp_geometry', 'rp_tile',
                 'rp_retire', 'rp_pixel', 'rp_shadow', 'rp_end')
        functions = '\n'.join(function(source, name) for name in names)
        blend = function((SRC / 'render_mirror.c').read_text(), 'blend_rgba')
        harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "random_props_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {uint8_t *data;size_t size;} Sprite2_array;
typedef struct {void *pixels;} SDL_Surface;
typedef struct {uint8_t *rgba;} Asset;
static struct {Sprite2_array *sprite2s;unsigned enemytype;int ex,ey,mapoffset,eyc;} enemy[100];
static unsigned enemyAvail[100];
NATIVE
DECLARATIONS
static bool scope_ok=true,shape_ok=true,writer_ok=true,enemiesActive=true;
static bool ready,last_output_valid,last_output_scene_hd,have_fade_saved;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference;
static bool fc_native_call,suppress;static unsigned fc_palette[256],rgb_palette[256];
static struct {bool frame_active,frame_failed;} fc;
static int fade_mode,faults;
static bool rp_enabled(void){return true;}
static bool rp_scope(void){return scope_ok;}
static bool rp_shape(unsigned slot,bool birth){(void)slot;(void)birth;return shape_ok;}
static bool rp_colors(void){return true;}
static bool rp_resources_current(void){return true;}
static bool rp_ready(void){return true;}
static void fg_before_actor(void){}
static bool family_geometry(bool strict){(void)strict;return true;}
static bool family_prepare_canvas(void){return true;}
#define FC_SOURCE 1
#define FC_ORDER 2
#define FC_WRITER 3
#define MIRROR_NORMAL 0
#define MIRROR_BLEND 1
#define MIRROR_SHADOW 2
#define OHS_SURVIVAL_WRITE(...) ((void)0)
static void family_fault(int cause){(void)cause;++faults;}
static bool b313_family_writer_draw_ready(unsigned frame){(void)frame;return writer_ok;}
static unsigned fc_frame=1,curLoc=500;
static uint8_t expected[64000],source_pixels[64000],hd_owner[4096000],cloud_owner[4096000],green_first[4096000],selected[64000];
static void *fc_source_pixels=source_pixels;
static SDL_Surface storage,screen;
static SDL_Surface *canvas=&storage,*game_screen=&screen,*VGAScreen=&screen;
#define lamp272_clear(x) ((void)(x))
#define triple275_clear(x) ((void)(x))
#define private_ember269_clear(x) ((void)(x))
#define gray325_clear(x) ((void)(x))
#define longface573_clear(x) ((void)(x))
BLEND
FUNCTIONS
static void reset_test(void){
 memset(&rp_life,0,sizeof rp_life);memset(rp_slots,0,sizeof rp_slots);memset(&rp_frame,0,sizeof rp_frame);
 memset(enemy,0,sizeof enemy);for(unsigned i=0;i<100;i++)enemyAvail[i]=1;
 faults=0;rp_first_reason=0;scope_ok=shape_ok=writer_ok=enemiesActive=true;rp_life.epoch=7;
 fc.frame_active=true;fc.frame_failed=false;screen.pixels=source_pixels;
}
static uint64_t birth(unsigned record,Sprite2_array *bank){
 uint64_t token=render_mirror_random_props_spawn_begin(record,0,0);assert(token);
 render_mirror_random_props_enemy_allocated(&enemy[0],record,0);
 enemy[0].sprite2s=bank;enemy[0].enemytype=record;enemy[0].ex=30;enemy[0].ey=47;
 render_mirror_random_props_enemy_initialized(&enemy[0],record,0);
 assert(rp_slots[0].initialized);enemyAvail[0]=0;render_mirror_random_props_spawn_commit(token,1);
 assert(rp_witness(0)&&rp_slots[0].birth.token==token);return token;
}
static Uint32 reference_blend(Uint32 before,const uint8_t *rgba){
 uint32_t result=0xff000000;
 for(unsigned c=0;c<3;c++){
  unsigned channel=(before>>(16-c*8))&255;
  result|=((channel*(255-rgba[3])+rgba[c]*rgba[3]+127)/255)<<(16-c*8);
 }
 return result;
}
static void start_part(unsigned image,unsigned part,Sprite2_array *bank){
 assert(rp_before_tile(0,(int)rp_parts[part]));
 assert(rp_tile(game_screen,0,24+(int)rp_px[part],40+(int)rp_py[part],bank,rp_images[image].base,(int)rp_parts[part],0));
 assert(rp_frame.active&&rp_frame.pending);
}
static unsigned feed_part(unsigned image,unsigned part){
 for(unsigned n=0;n<rp_counts[image][part];n++){
  const RandomPropsWrite *w=&rp_native[image][part][n];
  unsigned x=24+rp_px[part]+w->x,y=40+rp_py[part]+w->y;
  source_pixels[y*320+x]=expected[y*320+x]=w->index;
  assert(rp_pixel(x,y,MIRROR_NORMAL));
 }
 rp_end();assert(!faults&&!rp_frame.active);return rp_counts[image][part];
}
int main(int argc,char **argv){
 assert(argc==5);reset_test();uint8_t bank_bytes[1]={0};Sprite2_array bank={bank_bytes,1};
 const unsigned excluded[]={137,262,264,267,317};
 for(unsigned i=0;i<sizeof excluded/sizeof excluded[0];i++)assert(!render_mirror_random_props_spawn_begin(excluded[i],0,0));
 assert(!render_mirror_random_props_spawn_begin(135,25,0));assert(!render_mirror_random_props_spawn_begin(135,0,1));
 for(unsigned r=0;r<8;r++){birth(rp_records[r].record,&bank);assert(rp_slots[0].generation==r+1);enemyAvail[0]=1;}
 assert(rp_witnessed_records==255);
 render_mirror_random_props_enemy_allocated(&enemy[0],999,0);assert(!rp_witness(0));
 uint64_t failed=render_mirror_random_props_spawn_begin(135,0,0);assert(failed);
 render_mirror_random_props_spawn_commit(failed,0);assert(!rp_life.call.live);
 uint64_t fresh=render_mirror_random_props_spawn_begin(135,0,0);assert(fresh>failed);
 render_mirror_random_props_enemy_allocated(&enemy[0],135,0);
 render_mirror_random_props_enemy_initialized(&enemy[0],135,0);enemyAvail[0]=0;
 render_mirror_random_props_spawn_commit(failed,1);assert(!rp_witness(0)&&!rp_life.call.live);
 canvas->pixels=malloc(4096000*sizeof(Uint32));assert(canvas->pixels);
 unsigned writes=0,zero_indices=0,alpha_zero=0,partial_alpha=0;
 for(unsigned image=0;image<4;image++){
  uint8_t header[28];FILE *f=fopen(argv[image+1],"rb");assert(f);
  assert(fread(header,1,28,f)==28&&!memcmp(header,"HDR1",4));
  uint8_t *rgba=malloc(172032);assert(rgba);assert(fread(rgba,1,172032,f)==172032&&fgetc(f)==EOF);fclose(f);
  rp_resources.member[image].rgba=rgba;
  reset_test();unsigned record=0;for(unsigned r=0;r<8;r++)if(rp_records[r].image==image){record=rp_records[r].record;break;}
  birth(record,&bank);
  for(unsigned n=0;n<4096000;n++)((Uint32*)canvas->pixels)[n]=0xff204060u;
  memset(hd_owner,0,sizeof hd_owner);memset(rp_owned,0,sizeof rp_owned);
  bool touched[672]={false};
  for(unsigned part=0;part<4;part++){
   start_part(image,part,&bank);writes+=feed_part(image,part);
   if(part<3)assert(rp_frame.pending&&!rp_finish());
   for(unsigned n=0;n<rp_counts[image][part];n++){
    const RandomPropsWrite *w=&rp_native[image][part][n];unsigned lx=rp_px[part]+w->x,ly=rp_py[part]+w->y;
    assert(lx<24&&ly<28&&!touched[ly*24+lx]);touched[ly*24+lx]=true;zero_indices+=w->index==0;
    unsigned x=24+lx,y=40+ly;assert(rp_owned[y*320+x]==1&&selected[y*320+x]);
    for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
     const uint8_t *art=rgba+(((ly*8+sy)*192+lx*8+sx)*4);unsigned off=(y*8+sy)*2560+x*8+sx;
     assert(((Uint32*)canvas->pixels)[off]==reference_blend(0xff204060u,art)&&hd_owner[off]);
     alpha_zero+=art[3]==0;partial_alpha+=art[3]>0&&art[3]<255;
    }
   }
  }
  assert(rp_finish()&&!rp_frame.pending&&rp_frame.draw[0].complete&&rp_frame.draw[0].mask==15);
  assert(rp_frame.draw[0].callback_count==rp_totals[image]);
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(!touched[y*24+x]){
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned off=((40+y)*8+sy)*2560+(24+x)*8+sx;
    assert(((Uint32*)canvas->pixels)[off]==0xff204060u&&!hd_owner[off]);
   }
  }
  /* Duplicate body after completion and missing first part are not admitted. */
  assert(!rp_tile(game_screen,0,24,40,&bank,rp_images[image].base,0,0)&&rp_frame.fault);
  reset_test();birth(record,&bank);
  assert(!rp_tile(game_screen,0,36,40,&bank,rp_images[image].base,1,0)&&!rp_frame.contributed);
  /* Incomplete native calls cannot commit their quadrant. */
  start_part(image,0,&bank);rp_end();assert(faults&&rp_frame.fault&&!rp_finish());
  /* Pending quartet excludes other slots and non-next native parts. */
  reset_test();birth(record,&bank);start_part(image,0,&bank);feed_part(image,0);
  assert(!rp_before_tile(1,1)&&rp_frame.fault);
  reset_test();birth(record,&bank);start_part(image,0,&bank);feed_part(image,0);
  assert(!rp_before_tile(0,19)&&rp_frame.fault);
  /* Unexpected intervening pixel is not silently attributed to the next part. */
  reset_test();birth(record,&bank);start_part(image,0,&bank);feed_part(image,0);
  assert(rp_pixel(24,40,MIRROR_NORMAL)&&rp_frame.fault);
  free(rgba);
 }
 assert(writes==1594&&alpha_zero&&partial_alpha);
 unsigned cell=40*320+24;rp_owned[cell]=1;rp_shadows[cell]=0;
 assert(rp_retire(cell,MIRROR_SHADOW)&&rp_owned[cell]);for(unsigned n=0;n<300;n++)rp_shadow(cell);assert(rp_shadows[cell]==255);
 assert(rp_retire(cell,MIRROR_BLEND)&&!rp_owned[cell]&&!rp_shadows[cell]);
 rp_owned[cell]=1;assert(rp_retire(cell,MIRROR_NORMAL)&&!rp_owned[cell]);assert(!rp_retire(64000,MIRROR_NORMAL));
 free(canvas->pixels);
 printf("PASS: 8 births, 4 four-part materials, %u writes (%u zero indices), %u alpha0 / %u partial-alpha subpixels; ordering/retirement\n",writes,zero_indices,alpha_zero,partial_alpha);
 return 0;
}
'''
        for key, value in [('DECLARATIONS', declarations), ('NATIVE', (SRC / 'random_props_native.inc').read_text()),
                           ('BLEND', blend), ('FUNCTIONS', functions)]:
            harness = re.sub(r'\b' + key + r'\b', lambda _: value, harness)
        with tempfile.TemporaryDirectory() as temp:
            c, binary = Path(temp)/'random_props.c', Path(temp)/'random_props'
            c.write_text(harness)
            subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-variable',
                            '-pedantic', '-I', str(SRC), str(c), '-o', str(binary)], check=True)
            subprocess.run([str(binary)]+[str(ROOT/'assets/hd/packs/asteroid1-ten-v1'/f'enemy-newshd-{base}-8.hda')
                                          for base in (5,43,85,123)], check=True)


if __name__ == '__main__':
    unittest.main()
