"""Finite extraction of actual tank-shell pixel, extra ownership and live guards.

Synthetic draw/birth receipts and stubbed scope/source/palette/ready gates.
No constructor, engine motion, native RLE or game is executed.
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from test_smallrocks_family import function, ROOT, SRC


class TankShellTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'requires C compiler')
    def test_native_alpha_extra_retirement_and_independent_lifetime(self):
        source = (SRC/'enemy_shot_family_mirror.inc').read_text()
        declarations = source[source.index('static struct {unsigned checked'):source.index('static const char *es_root')]
        names = ('es_fail','es_live','es_retire','es_extra','es_store','es_pixel','es_end')
        functions = '\n'.join(function(source, name) for name in names)
        blend = function((SRC/'render_mirror.c').read_text(), 'blend_rgba')
        stamp = function((ROOT/'src/asteroid1_ten_mirror.inc').read_text(), 'asteroid1_stamp')
        birth_index = function((SRC/'tank194_family_mirror.inc').read_text(), 't194_birth_index')
        harness = r"""
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "enemy_shot_family.h"
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {uint8_t *data;size_t size;} Sprite2_array;
#define COUNTOF(x) (sizeof(x)/sizeof((x)[0]))
NATIVE
DECLARATIONS
static bool requested=true,draw_current=true;
static unsigned enemyShotAvail[60];
static unsigned fc_frame=1,faults;
static struct {bool frame_failed;} fc;
static Sprite2_array spriteSheet8;
static uint32_t fc_palette[256],rgb_palette[256];
static uint8_t expected[64000],source_pixels[64000],hd_owner[4096000],cloud_owner[4096000],green_first[4096000],green_under_owner[4096000],selected[64000];
static void *fc_source_pixels=source_pixels;
static struct {void *pixels;} storage,*canvas=&storage;
#define FC_SOURCE 1
#define FC_ORDER 2
#define MIRROR_NORMAL 0
#define MIRROR_BLEND 1
#define MIRROR_SHADOW 2
static void family_fault(int reason){(void)reason;++faults;}
static bool es_scope(void){return true;}
static bool es_art_current(void){return true;}
static bool es_colors(void){return true;}
static bool es_bank(Sprite2_array bank){(void)bank;return true;}
static bool es_draw_current(const EnemyShotDraw *d){(void)d;return draw_current;}
static bool b313_family_writer_draw_ready(unsigned frame){(void)frame;return true;}
static bool family_geometry(bool rgb){(void)rgb;return true;}
static uint64_t es_weapon(unsigned weapon){for(unsigned i=0;requested&&i<COUNTOF(es_weapons);i++)if(es_weapons[i].weapon==weapon)return es_weapons[i].stamp;return 0;}
#define lamp272_clear(x) ((void)(x))
#define triple275_clear(x) ((void)(x))
#define private_ember269_clear(x) ((void)(x))
#define gray325_clear(x) ((void)(x))
#define longface573_clear(x) ((void)(x))
#define OHS_SURVIVAL_WRITE(a,b,c) ((void)(a),(void)(b),(void)(c))
STAMP
BLEND
BIRTH_INDEX
FUNCTIONS
static Uint32 reference_blend(Uint32 before,const Uint8 *rgba) {
 uint32_t out=0xff000000u;
 for(unsigned c=0;c<3;c++){unsigned shift=(2-c)*8;unsigned old=(before>>shift)&255u;
  out|=((rgba[c]*rgba[3]+old*(255-rgba[3])+127)/255)<<shift;
 }
 return out;
}
static void reset(unsigned spec) {
 memset(&es,0,sizeof es);memset(es_native_owner,0,sizeof es_native_owner);
 memset(es_extra_cell,0,sizeof es_extra_cell);memset(es_extra_owner,0,sizeof es_extra_owner);
 memset(hd_owner,0,sizeof hd_owner);memset(selected,0,sizeof selected);
 memset(expected,0,sizeof expected);memset(source_pixels,0,sizeof source_pixels);
 memset(&fc,0,sizeof fc);faults=0;draw_current=true;
 Uint32 *p=canvas->pixels;for(unsigned n=0;n<4096000;n++)p[n]=0xff182838u;
 es.spec=spec;es.active=true;es.draws[0]=(EnemyShotDraw){.slot=3,.x=24,.y=40};
}
static void native_writes(unsigned spec,unsigned count) {
 for(unsigned i=0;i<count;i++){
  const EnemyShotWrite *w=&es_specs[spec].writes[i];unsigned x=24+w->x,y=40+w->y;
  expected[y*320+x]=source_pixels[y*320+x]=w->index;
  assert(es_pixel(x,y,MIRROR_NORMAL));
 }
}
int main(int argc,char **argv) {
 assert(argc==3);canvas->pixels=malloc(4096000*sizeof(Uint32));assert(canvas->pixels);
 unsigned alpha0=0,total_extra=0,total_native=0;
 for(unsigned k=0;k<2;k++){
  FILE *f=fopen(argv[k+1],"rb");assert(f);Uint8 h[28];assert(fread(h,1,28,f)==28);
  assert(!memcmp(h,"HDR1",4));Uint8 *rgba=malloc(43008);assert(rgba);
  assert(fread(rgba,1,43008,f)==43008&&fgetc(f)==EOF);fclose(f);
  assert(asteroid1_stamp(rgba,43008)==es_specs[k].payload);es_art.rgba[k]=rgba;
  assert(es_specs[k].count==39&&es_specs[k].extra==(k?11:80));
  reset(k);native_writes(k,39);assert(es.pixels==39);es_end();
  assert(!faults&&!es.failed&&!es.active&&es.count==1&&es.draws[0].complete);
  assert(es.draws[0].callbacks==39&&es.draws[0].core_stores==39*64);
  assert(es.draws[0].extra_stores==es_specs[k].extra);
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
   unsigned off=(40+y)*320+24+x;bool native=es_specs[k].mask[y*12+x]!=0;
   assert((es_native_owner[off]!=0)==native);assert((selected[off]!=0)==native);
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned ax=x*8+sx,ay=y*8+sy;size_t n=((40+y)*8+sy)*2560+(24+x)*8+sx;
    const Uint8 *a=rgba+(ay*96+ax)*4;bool extra=!native&&a[3];
    Uint32 want=(native||extra)?reference_blend(0xff182838u,a):0xff182838u;
    assert(((Uint32 *)canvas->pixels)[n]==want);
    assert((hd_owner[n]!=0)==native);assert(es_extra(n)==extra);
    if(native){++total_native;if(!a[3]){++alpha0;assert(hd_owner[n]);}}
    if(extra)++total_extra;
   }
  }
  assert(!es_extra(4096000));
  /* Shadows retain both categories; ordinary/blend writes retire their cell. */
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
   unsigned off=(40+y)*320+24+x;bool native=es_native_owner[off]!=0;
   unsigned extras=0;for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)extras+=es_extra(((40+y)*8+sy)*2560+(24+x)*8+sx);
   assert(es_retire(off,MIRROR_SHADOW)==native);assert((es_native_owner[off]!=0)==native);
   unsigned retained=0;for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)retained+=es_extra(((40+y)*8+sy)*2560+(24+x)*8+sx);
   assert(retained==extras);
   assert(es_retire(off,(x+y)%2?MIRROR_BLEND:MIRROR_NORMAL)==native);
   assert(!es_native_owner[off]&&!es_extra_cell[off]);
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)assert(!es_extra(((40+y)*8+sy)*2560+(24+x)*8+sx));
  }
  assert(!es_retire(64000,MIRROR_NORMAL));
  reset(k);native_writes(k,38);es_end();assert(faults&&es.failed&&!es.draws[0].complete);
  reset(k);assert(es_pixel(24,40,MIRROR_NORMAL));assert(faults&&es.failed);
  reset(k);native_writes(k,39);draw_current=false;es_end();assert(faults&&es.failed);
  free(rgba);
 }
 assert(total_native==4992&&total_extra==91&&alpha0>0);
 /* Actual live guard uses captured parent provenance, never current emitter. */
 es_epoch=7;es_life[3].generation=9;es_life[3].emitter_token=11;es_life[3].emitter_event=6;
 es_life[3].birth=(EnemyShotBirth){.epoch=7,.generation=9,.witnessed=true,.live=true,.emitter_slot=75,.emitter_record=194,.weapon=2,.weapon_stamp=es_weapons[0].stamp};
 assert(es_live(3));es_actor_generation[75]=999;assert(es_live(3));
 es_life[3].emitter_token=0;assert(!es_live(3));es_life[3].emitter_token=11;
 es_life[3].emitter_event=999;assert(!es_live(3));es_life[3].emitter_event=6;
 es_life[3].birth.emitter_record=195;assert(!es_live(3));es_life[3].birth.emitter_record=194;
 enemyShotAvail[3]=1;assert(!es_live(3));enemyShotAvail[3]=0;
 es_life[3].generation++;assert(!es_live(3));es_life[3].generation--;
 requested=false;assert(!es_live(3));requested=true;assert(es_live(3));assert(!es_live(60));
 printf("PASS: 2 shells,78 callbacks,4992 native subpixels,%u alpha0,91 extra; retirement/live guard\n",alpha0);
 free(canvas->pixels);return 0;
}
"""
        replacements = [('NATIVE',(SRC/'enemy_shot_native.inc').read_text()),('DECLARATIONS',declarations),
                        ('STAMP',stamp),('BLEND',blend),('BIRTH_INDEX',birth_index),('FUNCTIONS',functions)]
        for key,value in replacements:
            harness=harness.replace(chr(10)+key+chr(10),chr(10)+value+chr(10))
        with tempfile.TemporaryDirectory() as temp:
            c,binary=Path(temp)/'shell.c',Path(temp)/'shell'
            c.write_text(harness)
            subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-unused-variable',
                            '-pedantic','-I',str(SRC),str(c),'-o',str(binary)],check=True)
            assets=ROOT/'assets/hd/current-compat/tank-shell'
            subprocess.run([str(binary)]+[str(assets/f'enemy-tank-shell-{i}-8.hda') for i in (146,147)],check=True)


if __name__=='__main__':
    unittest.main()
