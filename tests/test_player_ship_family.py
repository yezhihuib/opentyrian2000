"""Extract normal-only player-ship pose/body/writer and affine sampling functions.

Scope/request/source-bank and palette readiness, writer/display preparation,
other-family clears and load I/O are explicit harness stubs. The native bank is
synthetic; HDA payloads, native callback tables and sampled functions are real.
No gameplay, original blit/RLE, display admission or Present is executed.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from test_smallrocks_family import ROOT, SRC


def function(source, name):
    match = re.search(r'^static [^\n]+?\b' + re.escape(name) + r'\(', source, re.M)
    if match is None:
        raise AssertionError('Missing real function: ' + name)
    opening = source.index('{', match.start())
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end]


class PlayerShipTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'requires C compiler')
    def test_actual_normal_pose_affine_writer_and_retirement(self):
        source = (SRC / 'player_ship_family_mirror.inc').read_text()
        declarations = source[source.index('static struct {PlayerShipDraw'):source.index('static const char *ps_root')]
        self.assertIn('ps_sprite2_blend_pixel(', source)
        names = ('ps_fail', 'ps_reset', 'ps_art_current', 'ps_sample', 'ps_pose',
                 'ps_current', 'ps_body', 'ps_retire', 'ps_pixel', 'ps_shadow', 'ps_end', 'ps_finish')
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
#include "player_ship_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {uint8_t *data;size_t size;} Sprite2_array;
typedef struct {void *pixels;} SDL_Surface;
NATIVE
DECLARATIONS
static struct {int x,y;unsigned invulnerable_ticks;} player[1];
static Sprite2_array spriteSheet9;
static bool requested=true,scope_ok=true,source_ok=true,palette_ok=true,writer_ok=true;
static struct {bool frame_active,frame_failed;} fc;
static unsigned fc_frame=3,fc_session=5,fc_generation=7;
static bool fc_native_call,suppress;
static unsigned fc_palette[256],rgb_palette[256];
static unsigned faults;
static const char *ps_root(void){return "test-assets";}
static bool ps_requested(void){return requested;}
static bool ps_invulnerable_requested(void){return false;}
static bool ps_scope(void){return scope_ok;}
static bool ps_source(Sprite2_array bank){return source_ok&&bank.data==spriteSheet9.data&&bank.size==spriteSheet9.size;}
static bool global_talon_palette_matches(void){return palette_ok;}
static bool ps_art_current(void);
static bool ps_load(void){return ps_art_current();}
static void fg_before_actor(void){}
static bool family_geometry(bool strict){(void)strict;return true;}
static bool family_prepare_canvas(void){return true;}
static bool b313_family_writer_draw_ready(unsigned frame){(void)frame;return writer_ok;}
#define FC_SOURCE 1
#define FC_ORDER 2
#define FC_WRITER 3
#define MIRROR_NORMAL 0
#define MIRROR_BLEND 1
#define MIRROR_SHADOW 2
#define OHS_SURVIVAL_WRITE(...) ((void)0)
static void family_fault(int cause){(void)cause;++faults;}
static uint8_t expected[64000],source_pixels[64000],hd_owner[4096000],cloud_owner[4096000],green_first[4096000],green_under_owner[4096000],selected[64000];
static void *fc_source_pixels=source_pixels;
static SDL_Surface storage,screen;
static SDL_Surface *canvas=&storage,*game_screen=&screen,*VGAScreen=&screen;
#define lamp272_clear(x) ((void)(x))
#define triple275_clear(x) ((void)(x))
#define private_ember269_clear(x) ((void)(x))
#define gray325_clear(x) ((void)(x))
#define longface573_clear(x) ((void)(x))
STAMP
BLEND
FUNCTIONS
static void reset_test(void){
 ps_reset();faults=0;requested=scope_ok=source_ok=palette_ok=writer_ok=true;
 player[0].x=29;player[0].y=47;player[0].invulnerable_ticks=0;
 fc.frame_active=true;fc.frame_failed=false;screen.pixels=source_pixels;
 memset(expected,0,sizeof expected);memset(source_pixels,0,sizeof source_pixels);memset(hd_owner,0,sizeof hd_owner);
}
static const uint8_t *reference_sample(const PlayerShipSpec *spec,unsigned x,unsigned y){
 static const uint8_t empty[4]={0};
 if(spec->index==233)return ps_art.rgba[2]+(y*192+x)*4;
 int a=(int)x*100+spec->offset_x,b=(int)y*100+spec->offset_y;
 if(a<0||b<0)return empty;
 unsigned xx=(unsigned)a/(unsigned)spec->scale_x,yy=(unsigned)b/(unsigned)spec->scale_y;
 return xx>=192||yy>=224?empty:ps_art.rgba[(spec->index-229)/2]+(yy*192+xx)*4;
}
static Uint32 reference_blend(Uint32 before,const uint8_t *rgba){
 uint32_t result=0xff000000;
 for(unsigned c=0;c<3;c++){
  unsigned channel=(before>>(16-c*8))&255;
  result|=((channel*(255-rgba[3])+rgba[c]*rgba[3]+127)/255)<<(16-c*8);
 }
 return result;
}
static void start(unsigned index){
 ps_pose(1,spriteSheet9,233,(int)index,0);assert(ps.draw.pose_seen&&ps_current());
 assert(ps_body(game_screen,24,40,spriteSheet9,index,MIRROR_BLEND,1,233)==-1&&!ps.active&&ps_current());
 assert(ps_body(game_screen,24,40,spriteSheet9,index,MIRROR_SHADOW,1,233)==-1&&!ps.active&&ps_current());
 assert(ps_body(game_screen,24,40,spriteSheet9,index,MIRROR_NORMAL,1,233)==1&&ps.active);
}
int main(int argc,char **argv){
 assert(argc==6);uint8_t native_bank[1]={0};spriteSheet9=(Sprite2_array){native_bank,1};
 canvas->pixels=malloc(4096000*sizeof(Uint32));assert(canvas->pixels);
 ps_art.checked=ps_art.valid=true;strcpy(ps_art.root,ps_root());
 for(unsigned pose=0;pose<5;pose++){
  uint8_t header[28];FILE *f=fopen(argv[pose+1],"rb");assert(f);
  assert(fread(header,1,28,f)==28&&!memcmp(header,"HDR1",4));
  ps_art.rgba[pose]=malloc(172032);assert(ps_art.rgba[pose]);
  assert(fread(ps_art.rgba[pose],1,172032,f)==172032&&fgetc(f)==EOF);fclose(f);
  assert(asteroid1_stamp(ps_art.rgba[pose],172032)==ps_specs[pose].stamp);
 }
 unsigned writes=0,alpha_zero=0,partial_alpha=0,outside=0;
 for(unsigned pose=0;pose<5;pose++){
  const PlayerShipSpec *spec=&ps_specs[pose];reset_test();
  for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++){
   assert(!memcmp(ps_sample(spec,x,y),reference_sample(spec,x,y),4));
   if(spec->index==233)assert(ps_sample(spec,x,y)==ps_art.rgba[pose]+(y*192+x)*4);
   else if((int)x*100+spec->offset_x<0||(int)y*100+spec->offset_y<0)outside++;
  }
  player[0].invulnerable_ticks=1;ps_pose(1,spriteSheet9,233,(int)spec->index,1);assert(!ps.draw.pose_seen);
  player[0].invulnerable_ticks=0;assert(!ps_current()); /* real 1->0 decrement cannot create a normal pose */
  assert(ps_body(game_screen,24,40,spriteSheet9,spec->index,MIRROR_NORMAL,1,233)==0&&!ps.active);
  reset_test();assert(ps_body(game_screen,24,40,spriteSheet9,spec->index,MIRROR_BLEND,1,233)==-1&&!ps.active);
  source_ok=false;ps_pose(1,spriteSheet9,233,(int)spec->index,0);assert(!ps.draw.pose_seen);
  reset_test();ps_pose(2,spriteSheet9,233,(int)spec->index,0);assert(!ps.draw.pose_seen);
  reset_test();ps_pose(1,spriteSheet9,233,230,0);assert(!ps.draw.pose_seen);
  reset_test();for(unsigned n=0;n<4096000;n++)((Uint32*)canvas->pixels)[n]=0xff204060u;
  start(spec->index);bool touched[672]={false};
  for(unsigned n=0;n<spec->count;n++){
   const PlayerShipWrite *w=&spec->writes[n];assert(w->x<24&&w->y<28&&!touched[w->y*24+w->x]);touched[w->y*24+w->x]=true;
   unsigned x=24+w->x,y=40+w->y;expected[y*320+x]=source_pixels[y*320+x]=w->index;
   assert(ps_pixel(x,y,MIRROR_NORMAL));writes++;
   assert(ps_owned[y*320+x]&&selected[y*320+x]);
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    const uint8_t *art=reference_sample(spec,w->x*8+sx,w->y*8+sy);
    unsigned off=(y*8+sy)*2560+x*8+sx;
    assert(((Uint32*)canvas->pixels)[off]==reference_blend(0xff204060u,art)&&hd_owner[off]);
    alpha_zero+=art[3]==0;partial_alpha+=art[3]>0&&art[3]<255;
   }
  }
  ps_end();assert(!faults&&!ps.active&&ps.draw.complete&&ps.draw.part_mask==15&&ps_finish());
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(!touched[y*24+x]){
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned off=((40+y)*8+sy)*2560+(24+x)*8+sx;
    assert(((Uint32*)canvas->pixels)[off]==0xff204060u&&!hd_owner[off]);
   }
  }
  ++fc_generation;assert(!ps_finish());--fc_generation;assert(ps_finish());
  ps_art.rgba[pose][0]^=1;assert(!ps_finish());ps_art.rgba[pose][0]^=1;assert(ps_finish());
  player[0].invulnerable_ticks=1;assert(!ps_current()&&!ps_finish());
  reset_test();start(spec->index);ps_end();assert(faults&&ps.draw.failed&&!ps_finish());
  reset_test();start(spec->index);
  const PlayerShipWrite *w=spec->writes;unsigned x=24+w->x,y=40+w->y;
  expected[y*320+x]=source_pixels[y*320+x]=(uint8_t)(w->index^1);
  assert(ps_pixel(x,y,MIRROR_NORMAL)&&faults&&ps.draw.failed);
  reset_test();start(spec->index);assert(ps_pixel(999,999,MIRROR_NORMAL)&&faults&&ps.draw.failed);
  reset_test();start(spec->index);assert(ps_pixel(24,40,MIRROR_BLEND)&&faults&&ps.draw.failed);
 }
 assert(writes==1186&&alpha_zero&&outside);
 unsigned cell=40*320+24;ps_owned[cell]=1;ps_shadows[cell]=0;
 assert(ps_retire(cell,MIRROR_SHADOW)&&ps_owned[cell]);for(unsigned n=0;n<300;n++)ps_shadow(cell);assert(ps_shadows[cell]==255);
 assert(ps_retire(cell,MIRROR_BLEND)&&!ps_owned[cell]&&!ps_shadows[cell]);
 ps_owned[cell]=1;assert(ps_retire(cell,MIRROR_NORMAL)&&!ps_owned[cell]);assert(!ps_retire(64000,MIRROR_NORMAL));
 for(unsigned pose=0;pose<5;pose++)free(ps_art.rgba[pose]);
 free(canvas->pixels);
 printf("PASS: 5 normal poses, %u native writes, %u alpha0 / %u partial-alpha subpixels; affine/holes/order/invulnerability/retirement\n",writes,alpha_zero,partial_alpha);
 return 0;
}
'''
        for key, value in [('DECLARATIONS', declarations), ('NATIVE', (SRC / 'player_ship_native.inc').read_text()),
                           ('STAMP', stamp), ('BLEND', blend), ('FUNCTIONS', functions)]:
            harness = re.sub(r'\b' + key + r'\b', lambda _: value, harness)
        with tempfile.TemporaryDirectory() as temp:
            c, binary = Path(temp)/'player_ship.c', Path(temp)/'player_ship'
            c.write_text(harness)
            subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-unused-variable',
                            '-pedantic', '-I', str(SRC), str(c), '-o', str(binary)], check=True)
            subprocess.run([str(binary)]+[str(ROOT/'assets/hd/current-compat/talon'/f'ship-{index}-8.hda')
                                          for index in (229,231,233,235,237)], check=True)


if __name__ == '__main__':
    unittest.main()
