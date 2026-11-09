"""Extract actual smallrock token lifecycle and sparse writer/retirement code.

The harness supplies synthetic slots/frame/canvas; scope, shape, writer readiness
and other-family ownership clears are stubs. It does not run RNG, native RLE,
allocation constructors, display admission, Present or the game.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'experimental/level2-family/src'


def function(source, name):
    match = re.search(r'^(?:static )?(?:bool|void|uint64_t|unsigned|int|Uint32) ' + re.escape(name) + r'\(', source, re.M)
    if match is None:
        raise AssertionError('Missing real function: ' + name)
    opening = source.index('{', match.start())
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end]


class SmallrocksTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'requires C compiler')
    def test_actual_birth_sparse_writer_and_retirement(self):
        source = (SRC / 'smallrocks_family_mirror.inc').read_text()
        declarations = source[source.index('static struct {uint64_t generation'):source.index('static const char *sr_root')]
        names = ('sr_fail', 'render_mirror_smallrocks_retired', 'sr_slot',
                 'render_mirror_smallrocks_spawn_begin', 'render_mirror_smallrocks_enemy_allocated',
                 'render_mirror_smallrocks_enemy_initialized', 'render_mirror_smallrocks_spawn_commit',
                 'sr_witness', 'smallrocks_retire', 'smallrocks_pixel', 'smallrocks_shadow', 'smallrocks_end')
        functions = '\n'.join(function(source, name) for name in names)
        blend = function((SRC / 'render_mirror.c').read_text(), 'blend_rgba')
        harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "smallrocks_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {uint8_t *data;size_t size;} Sprite2_array;
typedef struct {uint8_t *rgba;} Asset;
static struct {Sprite2_array *sprite2s;} enemy[100];
static unsigned enemyAvail[100];
DECLARATIONS
NATIVE
static bool scope_ok=true,shape_ok=true,writer_ok=true,enemiesActive=true;
static bool ready,last_output_valid,last_output_scene_hd,have_fade_saved;
static int fade_mode,faults;
static bool sr_scope(void){return scope_ok;}
static bool sr_shape(unsigned slot,bool birth){(void)slot;(void)birth;return shape_ok;}
#define FC_SOURCE 1
#define FC_ORDER 2
#define MIRROR_NORMAL 0
#define MIRROR_BLEND 1
#define MIRROR_SHADOW 2
static void family_fault(int cause){(void)cause;++faults;}
static bool b313_family_writer_draw_ready(unsigned frame){(void)frame;return writer_ok;}
static unsigned fc_frame;
static uint8_t expected[64000],source_pixels[64000],hd_owner[4096000],cloud_owner[4096000],green_first[4096000],selected[64000];
static void *fc_source_pixels=source_pixels;
static struct {void *pixels;} storage,*canvas=&storage;
#define lamp272_clear(x) ((void)(x))
#define triple275_clear(x) ((void)(x))
#define private_ember269_clear(x) ((void)(x))
#define gray325_clear(x) ((void)(x))
#define longface573_clear(x) ((void)(x))
BLEND
FUNCTIONS
static void reset_test(void){
 memset(&sr_life,0,sizeof sr_life);memset(sr_slots,0,sizeof sr_slots);memset(&sr_frame,0,sizeof sr_frame);
 memset(enemy,0,sizeof enemy);
 for(unsigned i=0;i<100;i++)enemyAvail[i]=1;
 faults=0;sr_first_reason=0;scope_ok=shape_ok=writer_ok=enemiesActive=true;sr_life.epoch=7;
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
 assert(argc==5);reset_test();uint8_t bank_bytes[1]={0};Sprite2_array bank={bank_bytes,1};
 assert(!render_mirror_smallrocks_spawn_begin(316,0,0));
 assert(!render_mirror_smallrocks_spawn_begin(317,25,0));
 assert(!render_mirror_smallrocks_spawn_begin(317,0,1));
 scope_ok=false;assert(!render_mirror_smallrocks_spawn_begin(317,0,0));scope_ok=true;
 for(unsigned record=317;record<=324;record++){
  uint64_t token=render_mirror_smallrocks_spawn_begin(record,0,0);assert(token);
  render_mirror_smallrocks_enemy_allocated(&enemy[0],record,0);
  enemy[0].sprite2s=&bank;
  render_mirror_smallrocks_enemy_initialized(&enemy[0],record,0);
  assert(sr_slots[0].pending&&sr_slots[0].initialized&&!sr_slots[0].live);
  enemyAvail[0]=0;render_mirror_smallrocks_spawn_commit(token,1);
  assert(!sr_life.call.live&&sr_witness(0)&&sr_slots[0].token==token&&sr_slots[0].record==record);
  assert(sr_slots[0].generation==record-316);
  enemyAvail[0]=1;
 }
 /* Unrelated slot reuse invalidates the witness and advances generation. */
 uint64_t old_generation=sr_slots[0].generation;
 render_mirror_smallrocks_enemy_allocated(&enemy[0],999,0);
 assert(!sr_witness(0)&&sr_slots[0].generation==old_generation+1);
 uint64_t failed=render_mirror_smallrocks_spawn_begin(317,0,0);assert(failed);
 render_mirror_smallrocks_spawn_commit(failed,0);assert(!sr_life.call.live);
 uint64_t fresh=render_mirror_smallrocks_spawn_begin(317,0,0);assert(fresh>failed);
 render_mirror_smallrocks_enemy_allocated(&enemy[0],317,0);
 render_mirror_smallrocks_enemy_initialized(&enemy[0],317,0);
 enemyAvail[0]=0;render_mirror_smallrocks_spawn_commit(failed,1);
 assert(!sr_life.call.live&&!sr_witness(0));
 reset_test();
 fresh=render_mirror_smallrocks_spawn_begin(317,0,0);assert(fresh);
 render_mirror_smallrocks_enemy_allocated(&enemy[0],317,0);enemy[0].sprite2s=&bank;
 shape_ok=false;render_mirror_smallrocks_enemy_initialized(&enemy[0],317,0);
 assert(!sr_slots[0].initialized);enemyAvail[0]=0;
 render_mirror_smallrocks_spawn_commit(fresh,1);assert(!sr_witness(0));
 reset_test();sr_life.serial=UINT64_MAX;
 assert(!render_mirror_smallrocks_spawn_begin(317,0,0)&&sr_life.exhausted);
 reset_test();
 canvas->pixels=malloc(4096000*sizeof(Uint32));assert(canvas->pixels);
 unsigned writes=0,zero_indices=0,alpha_zero=0,partial_alpha=0;
 for(unsigned k=0;k<4;k++){
  uint8_t header[28];FILE *f=fopen(argv[k+1],"rb");assert(f);
  assert(fread(header,1,28,f)==28&&!memcmp(header,"HDR1",4));
  uint8_t *rgba=malloc(43008);assert(rgba);assert(fread(rgba,1,43008,f)==43008&&fgetc(f)==EOF);fclose(f);
  sr_resources.member[k].rgba=rgba;
  for(unsigned n=0;n<4096000;n++)((Uint32*)canvas->pixels)[n]=0xff204060u;
  memset(hd_owner,0,sizeof hd_owner);memset(sr_owned,0,sizeof sr_owned);memset(&sr_frame,0,sizeof sr_frame);
  sr_frame.active=true;sr_frame.slot=3;sr_frame.image=k;sr_frame.draw[3].x=24;sr_frame.draw[3].y=40;
  bool touched[168]={false};
  for(unsigned n=0;n<sr_counts[k];n++){
   const SmallRocksWrite *w=&sr_native[k][n];assert(w->x<12&&w->y<14);assert(!touched[w->y*12+w->x]);touched[w->y*12+w->x]=true;
   unsigned x=24+w->x,y=40+w->y;expected[y*320+x]=source_pixels[y*320+x]=w->index;
   assert(smallrocks_pixel(x,y,MIRROR_NORMAL));writes++;zero_indices+=w->index==0;
   assert(sr_owned[y*320+x]==4&&selected[y*320+x]);
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    const uint8_t *art=rgba+(((w->y*8+sy)*96+w->x*8+sx)*4);
    unsigned off=(y*8+sy)*2560+x*8+sx;
    assert(((Uint32*)canvas->pixels)[off]==reference_blend(0xff204060u,art)&&hd_owner[off]);
    alpha_zero+=art[3]==0;partial_alpha+=art[3]>0&&art[3]<255;
   }
  }
  smallrocks_end();assert(!faults&&!sr_frame.active&&sr_frame.draw[3].complete&&sr_frame.draw[3].callback_count==sr_counts[k]);
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++)if(!touched[y*12+x]){
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned off=((40+y)*8+sy)*2560+(24+x)*8+sx;
    assert(((Uint32*)canvas->pixels)[off]==0xff204060u&&!hd_owner[off]);
   }
  }
  /* Missing callback, unexpected coordinate and non-normal style fail closed. */
  memset(&sr_frame,0,sizeof sr_frame);sr_frame.active=true;sr_frame.image=k;
  smallrocks_end();assert(faults&&sr_frame.fault&&!sr_frame.active);faults=0;
  memset(&sr_frame,0,sizeof sr_frame);sr_frame.active=true;sr_frame.image=k;
  assert(smallrocks_pixel(999,999,MIRROR_NORMAL));assert(faults&&sr_frame.fault);faults=0;
  memset(&sr_frame,0,sizeof sr_frame);sr_frame.active=true;sr_frame.image=k;
  assert(smallrocks_pixel(0,0,MIRROR_BLEND));assert(faults&&sr_frame.fault);faults=0;
  free(rgba);
 }
 assert(writes==548&&alpha_zero&&partial_alpha);
 unsigned cell=40*320+24;sr_owned[cell]=4;sr_shadows[cell]=0;
 assert(smallrocks_retire(cell,MIRROR_SHADOW)&&sr_owned[cell]==4);
 for(unsigned n=0;n<300;n++)smallrocks_shadow(cell);
 assert(sr_shadows[cell]==255);
 assert(smallrocks_retire(cell,MIRROR_BLEND)&&!sr_owned[cell]&&!sr_shadows[cell]);
 assert(!smallrocks_retire(cell,MIRROR_NORMAL));
 sr_owned[cell]=4;assert(smallrocks_retire(cell,MIRROR_NORMAL)&&!sr_owned[cell]);
 assert(!smallrocks_retire(64000,MIRROR_NORMAL));
 free(canvas->pixels);
 printf("PASS: 8 births, 4 sparse materials, %u writes (%u zero indices), %u alpha0 / %u partial-alpha subpixels; retirement\n",writes,zero_indices,alpha_zero,partial_alpha);
 return 0;
}
'''
        for key, value in [('DECLARATIONS', declarations), ('NATIVE', (SRC / 'smallrocks_native.inc').read_text()),
                           ('BLEND', blend), ('FUNCTIONS', functions)]:
            harness = re.sub(r'\b' + key + r'\b', lambda _: value, harness)
        with tempfile.TemporaryDirectory() as temp:
            c, binary = Path(temp)/'smallrocks.c', Path(temp)/'smallrocks'
            c.write_text(harness)
            subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-variable',
                            '-pedantic', '-I', str(SRC), str(c), '-o', str(binary)], check=True)
            subprocess.run([str(binary)]+[str(ROOT/'assets/hd/packs/asteroid1-ten-v1'/f'enemy-newshd-{base}-8.hda')
                                          for base in (95,114,133,152)], check=True)


if __name__ == '__main__':
    unittest.main()
