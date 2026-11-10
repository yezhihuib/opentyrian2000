/* Real HUD1 and SDL software presentation with original PIC3/font/option input
 * on stdin. The unrelated scene admission is a controllable test witness. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "SDL.h"
#include "gameplay_hud.h"
#define B313_FAMILY_CANVAS_DIAGNOSTIC 1
#define MAX(a,b) ((a)>(b)?(a):(b))
#define SPRITE_TABLES_MAX 8
#define SPRITES_PER_TABLE_MAX 152
#define TINY_FONT 2
#define OPTION_SHAPES 5
#define OPTION_NUM 37
#define SHIELD_NUM 11
typedef struct { Uint16 width,height,size; Uint8 *data; } Sprite;
static struct {unsigned count;Sprite sprite[152];} sprite_table[8];
static int font_ascii[256];
static struct {Uint8 ammo,icongr;} options[38];
static struct {Uint8 mpwr;} shields[12];
static char levelName[11]="ASTEROID2";
static unsigned power,lastPower;
static struct {
 unsigned shield,shield_max,armor;
 struct {struct {unsigned power;} weapon[2];unsigned sidekick[2];} items;
 struct {int ammo,ammo_max;} sidekick[2];
} player[2];
typedef enum {MIRROR_OUTPUT_UNSUPPORTED,MIRROR_OUTPUT_ORDINARY} MirrorOutputKind;
static SDL_Surface *VGAScreenSeg,*output;
static Uint32 rgb_palette[256],normal_palette[256];
static Uint8 original_pic[64000];
static bool scope=true,parent_requested=true;
static unsigned readbacks,checks;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAILED line %d: %s\n",__LINE__,#x);abort();}}while(0)
static Uint32 palette_rgb(Uint8 index){return UINT32_C(0xff000000)|rgb_palette[index];}
static bool family_scope(void){return scope;}
static bool render_mirror_family_requested(void){return parent_requested;}
static void asset_debug_readback(SDL_Renderer *renderer){(void)renderer;++readbacks;}
#include "family_static_hud_helpers.inc"
#include "family_static_hud_mirror.inc"

static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static void load_original(void)
{
 read_exact(original_pic,sizeof original_pic);read_exact(normal_palette,sizeof normal_palette);
 read_exact(font_ascii,sizeof font_ascii);
 for(unsigned ti=0;ti<2;ti++){
  unsigned t=ti?OPTION_SHAPES:TINY_FONT;Uint16 n;read_exact(&n,2);CHECK(n<=152);sprite_table[t].count=n;
  for(unsigned i=0;i<n;i++){
   Sprite *s=&sprite_table[t].sprite[i];read_exact(&s->width,2);read_exact(&s->height,2);read_exact(&s->size,2);
   if(s->size){s->data=malloc(s->size);CHECK(s->data);read_exact(s->data,s->size);}
  }
 }
 CHECK(fgetc(stdin)==EOF);
}
static void reset_source(void)
{
 family_static_hud_reset();gameplay_hud_shutdown();scope=parent_requested=true;
 memcpy(VGAScreenSeg->pixels,original_pic,sizeof original_pic);
 memcpy(rgb_palette,normal_palette,sizeof normal_palette);
 memset(player,0,sizeof player);memset(options,0,sizeof options);memset(shields,0,sizeof shields);
 power=lastPower=0;family_static_hud_start(VGAScreenSeg);
}
static Uint32 sample_expected(int x,int y,int sx,int sy)
{
 Uint8 idx=((Uint8 *)VGAScreenSeg->pixels)[y*320+x];
 const Uint8 *rgba=(x>=264||y>=184)?gameplay_hud_sample(x,y,sx,sy,8,idx):NULL;
 return rgba?(UINT32_C(0xff000000)|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2]):palette_rgb(idx);
}
static void verify_border_and_scene(Uint32 scene)
{
 unsigned owned=0;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++)for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  Uint32 actual=((Uint32 *)((Uint8 *)output->pixels+(y*8+sy)*output->pitch))[x*8+sx];
  Uint32 expect=(x<264&&y<184)?scene:sample_expected(x,y,sx,sy);
  CHECK(actual==expect);
  if(actual!=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*320+x])&&(x>=264||y>=184))++owned;
 }
 CHECK(owned>10000);
}
static void verify_native_target(SDL_Surface *target,int scale)
{
 for(int y=0;y<target->h;y++)for(int x=0;x<target->w;x++){
  int sx=(x%scale)*(8/scale)+(4/scale),sy=(y%scale)*(8/scale)+(4/scale);
  Uint32 expect=sample_expected(x/scale,y/scale,sx,sy);
  Uint32 actual=((Uint32 *)((Uint8 *)target->pixels+y*target->pitch))[x];
  CHECK(actual==expect);
 }
}
int main(int argc,char **argv)
{
 /* Exercise disabled callback routing too: it must never acquire a lease. */
 fdh_mode_drawn(NULL,1);fdh_shield_wiped(NULL);fdh_shield_drawn(NULL,0,0);
 fdh_meter_begin(NULL,NULL,HUD_WRITE_FRONT,1,0);fdh_meter_end(NULL,HUD_WRITE_FRONT);
 CHECK(argc==2);load_original();CHECK(SDL_Init(SDL_INIT_VIDEO)==0);
 VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 output=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 CHECK(VGAScreenSeg&&output);
 SDL_setenv("BUILDING313_FAMILY_HUD_ENABLE","0",1);reset_source();CHECK(!family_static_hud_captured);
 SDL_FillRect(output,NULL,0x12345678);family_static_hud_finish(MIRROR_OUTPUT_ORDINARY,true);
 CHECK(((Uint32 *)output->pixels)[0]==0x12345678&&!family_static_hud_painted);
 SDL_setenv("BUILDING313_FAMILY_HUD_ENABLE","1",1);reset_source();
 if(strcmp(argv[1],"valid")){
  CHECK(!family_static_hud_captured);family_static_hud_finish(MIRROR_OUTPUT_ORDINARY,false);CHECK(!family_static_hud_frame_ready);goto cleanup;
 }
 CHECK(family_static_hud_captured&&family_static_hud_current());
 SDL_FillRect(output,NULL,0x12345678);family_static_hud_begin();family_static_hud_finish(MIRROR_OUTPUT_ORDINARY,true);
 CHECK(family_static_hud_painted);verify_border_and_scene(0x12345678);
 /* Original front/rear power, generator, armor, labels, icons and messages. */
 const int holes[][4]={{289,17,311,20},{289,38,311,41},{269,12,277,104},{307,137,316,195},{284,4,312,17},{283,63,313,99},{16,189,248,200}};
 for(unsigned i=0;i<sizeof holes/sizeof holes[0];i++)for(int y=holes[i][1];y<holes[i][3];y++)for(int x=holes[i][0];x<holes[i][2];x++)((Uint8 *)VGAScreenSeg->pixels)[y*320+x]^=3;
 family_static_hud_compose();verify_border_and_scene(0x12345678);
 /* A late write retires one static cell; any corner write retires its whole block. */
 ((Uint8 *)VGAScreenSeg->pixels)[2*320+265]^=1;
 ((Uint8 *)VGAScreenSeg->pixels)[190*320+250]^=1;
 family_static_hud_compose();verify_border_and_scene(0x12345678);
 CHECK(!gameplay_hud_sample(248,184,0,0,8,((Uint8 *)VGAScreenSeg->pixels)[184*320+248]));
 for(int scale=2;scale<=4;scale+=2){
  reset_source();CHECK(family_static_hud_current());
  /* Distinct native world proves fallback never reuses a rejected HD canvas. */
  for(int y=0;y<184;y++)for(int x=0;x<264;x++)((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=(Uint8)(x+y);
  SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,320*scale,200*scale,32,SDL_PIXELFORMAT_ARGB8888);CHECK(target);
  SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(target);CHECK(renderer);
  SDL_Rect dst={0,0,320*scale,200*scale};
  family_static_hud_begin();family_static_hud_finish(MIRROR_OUTPUT_ORDINARY,false);
  CHECK(family_static_hud_present(renderer,VGAScreenSeg,&dst));verify_native_target(target,scale);
  CHECK(!family_static_hud_present(renderer,VGAScreenSeg,&dst));
  family_static_hud_begin();family_static_hud_finish(MIRROR_OUTPUT_ORDINARY,false);
  ((Uint8 *)VGAScreenSeg->pixels)[0]^=1;
  CHECK(!family_static_hud_present(renderer,VGAScreenSeg,&dst));
  family_static_hud_invalidate_frame();
  family_static_hud_release_texture();SDL_DestroyRenderer(renderer);SDL_FreeSurface(target);
 }
 reset_source();family_static_hud_begin();family_static_hud_finish(MIRROR_OUTPUT_UNSUPPORTED,false);CHECK(!family_static_hud_frame_ready);
 family_static_hud_suspend();CHECK(!family_static_hud_current());family_static_hud_begin();CHECK(family_static_hud_current());
 rgb_palette[108]^=1;CHECK(!family_static_hud_current());rgb_palette[108]^=1;CHECK(family_static_hud_current());
 rgb_palette[255]^=1;CHECK(family_static_hud_current());rgb_palette[255]^=1;
 scope=false;CHECK(!family_static_hud_current());scope=true;
 SDL_setenv("BUILDING313_FAMILY_HUD_ENABLE","0",1);CHECK(!family_static_hud_current());
 SDL_setenv("BUILDING313_FAMILY_HUD_ENABLE","1",1);CHECK(family_static_hud_current());
 player[0].armor=29;CHECK(!family_static_hud_current());player[0].armor=0;CHECK(!family_static_hud_current());
 reset_source();CHECK(family_static_hud_current());
 void *old=VGAScreenSeg->pixels;VGAScreenSeg->pixels=malloc(64000);CHECK(VGAScreenSeg->pixels);memcpy(VGAScreenSeg->pixels,old,64000);
 CHECK(!family_static_hud_current());free(VGAScreenSeg->pixels);VGAScreenSeg->pixels=old;CHECK(!family_static_hud_current());
cleanup:
 family_static_hud_release_texture();family_static_hud_reset();gameplay_hud_shutdown();
 SDL_FreeSurface(VGAScreenSeg);SDL_FreeSurface(output);
 for(unsigned t=0;t<8;t++)for(unsigned i=0;i<sprite_table[t].count;i++)free(sprite_table[t].sprite[i].data);
 SDL_Quit();printf("PASS family static HUD %s: %u checks, %u actual SDL presents\n",argv[1],checks,readbacks);return 0;
}
