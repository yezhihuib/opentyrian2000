"""Production central dispatch + retirement regression; no SDL/game execution.
Pixel adapters deliberately model ownership acquisition only. Actual family
alpha/native-hole codecs remain covered by their separate production tests.
Run: python central_writer_test.py /path/to/repository
"""
from pathlib import Path
import re, subprocess, tempfile, sys
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
SRC=ROOT/'experimental/level2-family/src'
def extract(file,name):
 text=(SRC/file).read_text()
 return re.search(r'static (?:bool|void) '+name+r'\([^\n]*\)\n\{.*?\n\}',text,re.S).group()
prefixes=['rp','sr','f284','tp','ln','lp287','la']
files=['random_props','smallrocks','fork284','turret273','linked338_normal','linked_prop287288','late_actor']
if (SRC/'normal270_family_mirror.inc').exists():
 prefixes.insert(4,'f270');files.insert(4,'normal270')
c=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {void *pixels;} SDL_Surface;
#define MIRROR_NORMAL 0
#define MIRROR_BLEND 1
#define MIRROR_SHADOW 2
#define FC_SOURCE 1
#define FC_CONFIG 2
#define FC_EFFECT 3
#define FC_GROUND 4
#define FC_WRITER 5
#define FC_ORDER 6
#define FC_CONTEXT 7
static struct {bool frame_active,frame_failed;unsigned native_pixels,occlusions,blend_fallbacks,shadow_pixels;} fc;
static struct {bool requested;} fct;
static struct {bool frame_enabled;unsigned frame_eligible,total_eligible,frame_retired,total_retired;int first_x,first_y;} fbr;
static bool fc_canvas_ready=true,fc_native_call,suppress;
static struct {int x,y;} fc_call_rect;static unsigned fc_call_pixels;
static uint8_t native[64000],expected[64000],selected[64000],fbr_retired[64000];
static uint8_t hd_owner[4096000],cloud_owner[4096000],green_first[4096000];
static Uint32 rgb[4096000];static SDL_Surface source={native},cv={rgb},*canvas=&cv,*fc_source=&source;
static void *fc_source_pixels=native;
static unsigned faults;static int active=-1;
static void family_fault(unsigned reason){faults=reason;fc.frame_failed=true;}
#define family_terrain_blend_config_current() true
#define fg_writer_entry() true
#define b313_family_writer_pixel(s,a) true
#define family_geometry(x) true
#define fg_terrain_cell_survives(off) false
#define fg_native_written(off,style) ((void)0)
static Uint32 palette_rgb(Uint8 i){return 0xff000000u|i;}
static Uint32 darken_rgba(Uint32 rgb,unsigned alpha){(void)alpha;return 0xff000000u|((rgb&0xfefefeu)>>1);}
'''
for p,f in zip(prefixes,files):
 c+=f'''static uint8_t {p}_owned[64000],{p}_shadows[64000];
static uint64_t {p}_blend_retirements,{p}_normal_retirements;
#define {p}_write_current() true
#define {p}_fail(x) ((void)0)
#define {p}_shadow(off) (++{p}_shadows[off])
'''
 if p in ['tp','ln','la']:c+=f'static struct {{bool contributed;}} {p}_frame={{true}};\n'
 c+=extract(f+'_family_mirror.inc','smallrocks_retire' if p=='sr' else p+'_retire')+'\n'
c+=f'#define N_FAMILIES {len(prefixes)}\n'
c+='static uint8_t *owners[]={'+','.join(p+'_owned' for p in prefixes)+'};\n'
c+='static uint8_t *shadows[]={'+','.join(p+'_shadows' for p in prefixes)+'};\n'
c+=r'''
static bool acquire(unsigned who,unsigned x,unsigned y,int style){
 if(active!=(int)who)return false;
 assert(style==MIRROR_NORMAL);
 unsigned off=y*320+x;
 /* Every family must already be retired when even the first writer returns. */
 for(unsigned j=0;j<N_FAMILIES;j++)assert(owners[j][off]==0);
 owners[who][off]=1;selected[off]=1;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  unsigned n=(y*8+sy)*2560+x*8+sx;hd_owner[n]=1;rgb[n]=0xff808080;
 }
 return true;
}
'''
for i,p in enumerate(prefixes):c+=f'#define {p}_pixel(x,y,s) acquire({i},x,y,s)\n'
c+='#define smallrocks_pixel(x,y,s) sr_pixel(x,y,s)\n#define smallrocks_shadow(off) sr_shadow(off)\n'
for p in ['lamp272','triple275','private_ember269','gray325','longface573']:
 c+=f'#define {p}_pixel(x,y,s) false\n#define {p}_clear(off) ((void)0)\n#define {p}_cell(off) false\n#define {p}_blend_retired() ((void)0)\n'
c+=extract('b313_family_canvas_mirror.inc','family_pixel')
c+=r'''
static void reset(void){
 memset(&fc,0,sizeof fc);fc.frame_active=true;faults=0;active=-1;
 memset(native,0,sizeof native);memset(expected,0,sizeof expected);
 memset(hd_owner,0,sizeof hd_owner);memset(rgb,0,sizeof rgb);
 for(unsigned i=0;i<N_FAMILIES;i++){memset(owners[i],0,64000);memset(shadows[i],0,64000);}
}
int main(void){
 const unsigned x=40,y=20,off=y*320+x,n=y*8*2560+x*8;
 for(unsigned old=0;old<N_FAMILIES;old++)for(unsigned next=0;next<N_FAMILIES;next++){
  reset();owners[old][off]=9;active=next;native[off]=31;
  family_pixel(&source,native+off,MIRROR_NORMAL);assert(!faults);
  for(unsigned j=0;j<N_FAMILIES;j++)assert(owners[j][off]==(j==next));
  /* A native hole has no callback: adjacent underlay and owners stay untouched. */
  assert(!owners[next][off+1]&&rgb[n+8]==0&&expected[off+1]==0);
  active=-1;native[off]=23; /* 31 -> shadow luminance 15/2 */
  family_pixel(&source,native+off,MIRROR_SHADOW);assert(!faults);
  assert(owners[next][off]==1&&shadows[next][off]==1&&rgb[n]==0xff404040&&hd_owner[n]);
  native[off]=8;family_pixel(&source,native+off,MIRROR_BLEND);assert(!faults);
  for(unsigned j=0;j<N_FAMILIES;j++)assert(!owners[j][off]);
  assert(!hd_owner[n]&&rgb[n]==palette_rgb(8));
 }
 for(unsigned old=0;old<N_FAMILIES;old++){
  reset();owners[old][off]=1;hd_owner[n]=1;rgb[n]=0xff808080;native[off]=4;
  family_pixel(&source,native+off,MIRROR_NORMAL);assert(!faults&&!owners[old][off]&&!hd_owner[n]);
  assert(rgb[n]==palette_rgb(4));
 }
 /* Invalid native shadow must fail closed, not claim a successful receipt. */
 reset();owners[0][off]=1;hd_owner[n]=1;expected[off]=31;native[off]=99;
 family_pixel(&source,native+off,MIRROR_SHADOW);assert(faults==FC_EFFECT&&!shadows[0][off]);
 return 0;
}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td);(p/'test.c').write_text(c)
 subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print(f'central dispatch: {len(prefixes)**2} pairwise transitions, normal/blend/shadow/hole checks passed')
