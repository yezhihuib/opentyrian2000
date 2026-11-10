#include <assert.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "b313_family_plan.h"
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef struct {int BitsPerPixel;} Format;
typedef struct {void *pixels; int pitch,h; Format *format;} SDL_Surface;
typedef struct {Uint8 *data; size_t size;} Sprite2_array;
static SDL_Surface *VGAScreen;
#define SDL_SwapLE16(x) (x)
#define MIRROR_NORMAL 0
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define asset_debug_effect(...) ((void)0)
#define load_font_arrow_sprite_end(...) ((void)0)
#define pregame_font_sprite2_end(...) ((void)0)
static B313FamilyPlan plan;
static unsigned writes;
typedef struct {int x,y,w,h;} SDL_Rect;
static SDL_Rect fc_call_rect;
static uint64_t fc_call_pixels;
static bool fc_native_call=true,suppress=true,fault;
#define FC_ORDER 1
#define family_fault(...) (fault=true)
#define lamp272_clear(...) ((void)0)
#define triple275_clear(...) ((void)0)
#define private_ember269_clear(...) ((void)0)
#define gray325_clear(...) ((void)0)
#define longface573_clear(...) ((void)0)
static void check_native_guard(unsigned x,unsigned y,int style)
{
#include "b313_native_guard.inc"
}
static void guard_negative_cases(void)
{
 fc_call_rect=(SDL_Rect){24,0,12,1};fc_call_pixels=0;fault=false;
 check_native_guard(25,0,0);assert(fault&&fc_call_pixels==0); /* skipped column */
 fault=false;check_native_guard(24,1,0);assert(fault); /* wrong row */
 fault=false;check_native_guard(24,0,1);assert(fault); /* wrong effect */
 fault=false;suppress=false;check_native_guard(24,0,0);assert(fault);suppress=true;
 fault=false;check_native_guard(24,0,0);assert(!fault&&fc_call_pixels==1);
 check_native_guard(24,0,0);assert(fault); /* duplicate */
 fault=false;fc_call_pixels=12;check_native_guard(24,1,0);assert(fault); /* extra */
 fault=false;fc_call_pixels=0;fc_call_rect.h=0;check_native_guard(24,0,0);assert(fault);
}
static void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style)
{
 check_native_guard((unsigned)(p-(Uint8 *)s->pixels)%320,(unsigned)(p-(Uint8 *)s->pixels)/320,style);
 assert(!fault);
 assert(style==MIRROR_NORMAL && writes<plan.visible_pixels);
 unsigned row=plan.first_visible_row+writes/12,col=writes%12;
 assert(p==(Uint8 *)s->pixels+(plan.visible_y+(int)(writes/12))*320+plan.destination_x+(int)col);
 assert(v==(Uint8)(row*12+col+1));
 ++writes;
}
/* Extracted unchanged from the actual engine by the Python runner. */
#include "b313_native_blit.inc"
int main(void)
{
 guard_negative_cases();
 static const unsigned bases[4][3]={{191,195,199},{193,197,201},{153,157,161},{155,159,163}};
 static const unsigned phase[20]={0,0,0,0,1,1,2,2,1,1,0,0,0,0,0,0,0,0,0,0};
 static const unsigned parts[4]={0,1,19,20};
 static Uint8 pixels[320*264],rle[2+14*14+1];
 rle[0]=2;rle[1]=0;unsigned pos=2;
 for(unsigned row=0;row<14;row++){rle[pos++]=0xc0;for(unsigned col=0;col<12;col++)rle[pos++]=(Uint8)(row*12+col+1);rle[pos++]=0;}
 rle[pos++]=0x0f;
 Format fmt={8};SDL_Surface surface={pixels+320*32,320,200,&fmt};VGAScreen=&surface;
 Sprite2_array sprite={rle,pos};unsigned cases=0;
 for(unsigned component=0;component<4;component++)for(unsigned cycle=1;cycle<=20;cycle++)for(unsigned q=0;q<4;q++){
  B313FamilyCall call={.actor={.type=313+component,.record=313+component,.record_verified=true,.graphics_verified=true,.slot=1,.pool=0,.bank=20,.sheet_identity=1,.data_identity=2,.size=1,.cycle=cycle,.base=bases[component][phase[cycle-1]]},.part=parts[q],.density=8,.x=24,.surface_width=320,.surface_height=200,.surface_pitch=320};
  for(int y=-14;y<=214;y++){
   call.y=y;assert(b313_family_plan(&call,&plan));assert(plan.phase==phase[cycle-1]);
   unsigned expected=0;for(int row=0;row<14;row++)if(y+row>=0&&y+row<200)expected+=12;
   assert(plan.visible_pixels==expected&&plan.visible_rows*12==expected);
   memset(pixels,0xaa,sizeof pixels);writes=0;
   fc_call_rect=(SDL_Rect){call.x,plan.visible_y,12,(int)plan.visible_rows};fc_call_pixels=0;fault=false;
   blit_sprite2(&surface,call.x,y,sprite,1);
   assert(writes==expected && fc_call_pixels==(unsigned)(12*fc_call_rect.h));
   /* Verify all native stores and all untouched bytes, not only callbacks. */
   for(int yy=0;yy<200;yy++)for(int xx=0;xx<320;xx++){
    Uint8 v=0xaa;
    if(yy>=y&&yy<y+14&&xx>=24&&xx<36)v=(Uint8)((yy-y)*12+xx-24+1);
    assert(((Uint8 *)surface.pixels)[yy*320+xx]==v);
   }
   ++cases;
  }
  int bad[]={INT_MIN,INT_MAX};for(unsigned n=0;n<2;n++){call.y=bad[n];assert(!b313_family_plan(&call,&plan)&&plan.reasons==B313FP_GEOMETRY);}
  call.y=INT_MIN/320+14;assert(b313_family_plan(&call,&plan)&&plan.visible_pixels==0);
  call.y=INT_MAX/320-14;assert(b313_family_plan(&call,&plan)&&plan.visible_pixels==0);
  call.y=0;call.actor.damaged=true;assert(!b313_family_plan(&call,&plan));call.actor.damaged=false;
  call.actor.filter=1;assert(!b313_family_plan(&call,&plan));call.actor.filter=0;
  call.actor.base++;assert(!b313_family_plan(&call,&plan)&&plan.reasons==B313FP_PHASE);call.actor.base--;
  call.y=0;int badx[]={INT_MIN,-1,309,INT_MAX};for(unsigned n=0;n<4;n++){call.x=badx[n];assert(!b313_family_plan(&call,&plan)&&plan.reasons==B313FP_GEOMETRY);}
 }
 printf("PASS: %u phase/part/vertical cases, exact native byte order and untouched pixels; extreme/horizontal guards\n",cases);
}
