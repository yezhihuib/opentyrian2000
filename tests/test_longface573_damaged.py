"""Data-free extraction of actual shape, damage assignments and sparse writer.

Source/level/witness dependencies are stubs here, not integration qualification.
No game, original-data bank or GUI is executed.
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
    start = source.index('static ', source.index(name) - 40)
    # Locate the definition's opening brace, then count nested bodies.
    opening = source.index('{', source.index(name, start))
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


class LongfaceDamagedTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'requires C compiler')
    def test_actual_damage_shape_and_sparse_writes_all_eight_assets(self):
        source = (SRC / 'longface573_family_mirror.inc').read_text()
        shape = function(source, 'private_longface573_shape(')
        pixel = function(source, 'longface573_pixel(')
        end = function(source, 'longface573_end(')
        tile = function(source, 'longface573_tile(')
        self.assertNotIn('if(enemy[slot].edamaged)return false;', tile)
        self.assertIn('!private_longface573_shape(slot,1)', tile)
        damage_source = (SRC / 'tyrian2.c').read_text()
        a = damage_source.index('enemy[temp3].enemycycle = 1;')
        b = damage_source.index('JE_integer tempX', a)
        damage = damage_source[a:b]
        fields = set(re.findall(r'e->(\w+)', shape)) - {'sprite2s', 'enemydatofs', 'egr', 'tur', 'freq', 'edgr'}
        declarations = 'int ' + ','.join(sorted(fields)) + '; unsigned edgr;'
        harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t Uint8; typedef uint32_t Uint32;
typedef struct {int unused;} Sprite2_array;
struct JE_SingleEnemyType {FIELDS unsigned egr[20]; int tur[3],freq[3]; Sprite2_array *sprite2s; void *enemydatofs;};
static struct JE_SingleEnemyType enemy[100];
static int enemyDat[600],enemyAvail[100],enemyKilled;
static unsigned enemySpriteSheetIds[4]={8,20};
static Sprite2_array enemySpriteSheets[4];
static bool private_longface573_source(Sprite2_array bank){(void)bank;return true;}
#define LP287_DAMAGE_TRANSFORM 0
#define F270_DAMAGE_TRANSFORM 0
#define render_mirror_linked_prop287288_retired(...) assert(0)
#define render_mirror_normal270_retired(...) assert(0)
#define render_mirror_late_actor_retired(...) assert(0)
static void apply_damage(unsigned temp3){ DAMAGE }
SHAPE
NATIVE
static bool longface573_native, writer_ready=true;
static unsigned longface573_image,longface573_part,longface573_pixels;
static int longface573_x,longface573_y,faults;
static uint8_t expected[64000],hd_owner[4096000],cloud_owner[4096000],green_first[4096000],longface573_owned[64000],selected[64000];
static struct {void *pixels;} storage,*canvas=&storage;
typedef struct {uint8_t *rgba;} Asset;
static struct {Asset member[8];} private_longface573_resources;
static struct {unsigned slot,next,mask[100];bool quartet;} private_longface573_frame;
static unsigned fc_frame;
#define MIRROR_NORMAL 0
#define FC_ORDER 1
static void family_fault(int cause){(void)cause;++faults;}
static bool b313_family_writer_draw_ready(unsigned frame){(void)frame;return writer_ready;}
#define lamp272_clear(x) ((void)(x))
#define gray325_clear(x) ((void)(x))
#define triple275_clear(x) ((void)(x))
#define private_ember269_clear(x) ((void)(x))
PIXEL
END
int main(int argc,char **argv){
 assert(argc==9);(void)private_longface573_palette;
 static const unsigned normal[]={165,127,155,123},damaged[]={167,129,163,125};
 for(unsigned c=0;c<4;c++){
  struct JE_SingleEnemyType *e=&enemy[75];memset(e,0,sizeof *e);
  e->enemytype=573+c;e->enemydatofs=&enemyDat[573+c];e->sprite2s=&enemySpriteSheets[c%2];
  e->size=1;e->armorleft=20;e->ani=e->enemycycle=e->animin=1;e->exrev=e->eyrev=100;
  e->explonum=12;e->edgr=damaged[c];e->edlevel=10;e->linknum=19;e->egr[0]=normal[c];
  assert(private_longface573_shape(75,1));
  apply_damage(75);assert(e->armorleft==10&&e->edamaged&&e->egr[0]==damaged[c]);
  assert(private_longface573_shape(75,1)&&private_longface573_shape(75,2));
  assert(!private_longface573_shape(75,0));
  e->egr[0]=normal[c];assert(!private_longface573_shape(75,1));e->egr[0]=damaged[c];
  e->armorleft=0;assert(!private_longface573_shape(75,1));e->armorleft=10;
  e->linknum=20;assert(!private_longface573_shape(75,1));
 }
 canvas->pixels=calloc(4096000,sizeof(Uint32));assert(canvas->pixels);
 unsigned total=0;const unsigned parts[]={0,1,19,20};
 for(unsigned k=0;k<8;k++){
  uint8_t header[28];FILE *f=fopen(argv[k+1],"rb");assert(f);
  assert(fread(header,1,28,f)==28&&!memcmp(header,"HDR1",4));
  uint8_t *rgba=malloc(172032);assert(rgba);assert(fread(rgba,1,172032,f)==172032&&fgetc(f)==EOF);fclose(f);
  private_longface573_resources.member[k].rgba=rgba;
  for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++)
   assert(rgba[(y*192+x)*4+3]==(private_longface573_indices[k][(y/8)*24+x/8]?255:0));
  memset(canvas->pixels,0,4096000*sizeof(Uint32));memset(&private_longface573_frame,0,sizeof private_longface573_frame);
  private_longface573_frame.quartet=true;
  for(unsigned q=0;q<4;q++){
   unsigned px=(q%2)*12,py=(q/2)*14;
   longface573_native=true;longface573_image=k;longface573_part=parts[q];longface573_pixels=0;
   longface573_x=24+px;longface573_y=40+py;
   for(unsigned n=0;n<168;n++){
    unsigned index=(py+n/12)*24+px+n%12;uint8_t v=private_longface573_indices[k][index];
    if(!v)continue;
    unsigned x=longface573_x+n%12,y=longface573_y+n/12;expected[y*320+x]=v;
    assert(longface573_pixel(x,y,0));++total;
   }
   longface573_end();assert(!faults&&!longface573_native);
  }
  assert(!private_longface573_frame.quartet&&private_longface573_frame.mask[0]==15);
  for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++){
   unsigned off=(y*192+x)*4;uint32_t want=rgba[off+3]?0xff000000u|((uint32_t)rgba[off]<<16)|((uint32_t)rgba[off+1]<<8)|rgba[off+2]:0;
   assert(((Uint32*)canvas->pixels)[(40*8+y)*2560+24*8+x]==want);
  }
  /* An incomplete nonempty native quadrant cannot finish successfully. */
  longface573_native=true;longface573_image=k;longface573_part=0;longface573_pixels=0;
  longface573_end();assert(faults==1);faults=0;
  free(rgba);
 }
 free(canvas->pixels);printf("PASS: 4 real damage assignments, 8 sparse materials, %u opaque native writes\n",total);
 return 0;
}
'''
        for key, value in [('FIELDS', declarations), ('DAMAGE', damage), ('SHAPE', shape),
                           ('NATIVE', (SRC / 'longface573_native.inc').read_text()),
                           ('PIXEL', pixel), ('END', end)]:
            harness = re.sub(r'\b' + key + r'\b', lambda _: value, harness)
        assets = [('newshd',165),('newshd',167),('newshp',127),('newshp',129),
                  ('newshd',155),('newshd',163),('newshp',123),('newshp',125)]
        with tempfile.TemporaryDirectory() as temp:
            c = Path(temp)/'damage.c'; binary = Path(temp)/'damage'
            c.write_text(harness)
            subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-pedantic',str(c),'-o',str(binary)],check=True)
            subprocess.run([str(binary)]+[str(ROOT/'assets/hd/level2-family-v1/longface'/f'enemy-{bank}-{base}-8.hda') for bank,base in assets],check=True)


if __name__ == '__main__':
    unittest.main()
