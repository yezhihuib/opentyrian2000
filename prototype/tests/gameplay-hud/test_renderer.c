/* Synthetic oracle extracts unchanged production function bodies. No game data,
 * art, SDL runtime, input loop, or scene assets are required. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gameplay_hud.h"
#include "gameplay_hud_components.h"
#include "gameplay_hud_meters.h"
#include "gameplay_hud_indicators.h"
#include "gameplay_hud_fixed_text.h"
#include "gameplay_hud_font.h"
typedef uint8_t Uint8;
typedef int8_t Sint8;
typedef int16_t Sint16;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct { int BytesPerPixel,BitsPerPixel; } SDL_PixelFormat;
typedef struct { int x,y,w,h; } SDL_Rect;
typedef struct { int w,h,pitch; void *pixels; SDL_PixelFormat *format; SDL_Rect clip_rect; } SDL_Surface;

typedef struct { Uint8 r,g,b,a; } SDL_Color;
typedef int SDL_Renderer;
typedef int SDL_Texture;
#define SDL_PIXELFORMAT_ARGB8888 0
#define SDL_TEXTUREACCESS_STREAMING 0
#define SDL_ScaleModeNearest 0
#define SDL_BLENDMODE_NONE 0
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
static unsigned allocations;
static SDL_Surface *SDL_CreateRGBSurfaceWithFormat(unsigned flags,int w,int h,int depth,unsigned format)
{
 SDL_Surface *p=calloc(1,sizeof(*p));assert(p);p->w=w;p->h=h;p->pitch=w*(depth/8);
 p->pixels=calloc((size_t)p->pitch,h);p->format=malloc(sizeof(*p->format));assert(p->pixels&&p->format);
 p->clip_rect=(SDL_Rect){0,0,w,h};
 p->format->BytesPerPixel=depth/8;p->format->BitsPerPixel=depth;++allocations;return p;
}
static void SDL_FreeSurface(SDL_Surface *p) {if(p){free(p->pixels);free(p->format);free(p);}}
static SDL_Texture *SDL_CreateTexture(SDL_Renderer *r,unsigned f,unsigned a,int w,int h) {static int texture;return &texture;}
static void SDL_DestroyTexture(SDL_Texture *p) {}
static int SDL_SetTextureScaleMode(SDL_Texture *p,int a) {return 0;}
static int SDL_SetTextureBlendMode(SDL_Texture *p,int a) {return 0;}
static int SDL_LockTexture(SDL_Texture *p,void *a,void **b,int *c) {return -1;}
static void SDL_UnlockTexture(SDL_Texture *p) {}
static int SDL_SetRenderDrawColor(SDL_Renderer *p,int a,int b,int c,int d) {return 0;}
static int SDL_RenderClear(SDL_Renderer *p) {return 0;}
static int SDL_RenderCopy(SDL_Renderer *p,SDL_Texture *t,void *a,const SDL_Rect *b) {return 0;}
static void SDL_RenderPresent(SDL_Renderer *p) {}
static void asset_debug_readback(SDL_Renderer *p) {}
static uint64_t mt_state_fingerprint(void) {return UINT64_C(0x7654321012345678);}
static void ground101_frame_reset(void) {}
static void ground101_frame_report(unsigned tick,const char *reason) {}
static bool asset_debug_fast_forward(void) {return false;}
static unsigned sample_hd,sample_mode,audit_mismatch,frames,presents;
static void game_probe_fade_sample(SDL_Surface *p,int s,unsigned hd,int mode) {sample_hd=hd;sample_mode=mode;}
static void game_probe_effects(unsigned a,unsigned b,unsigned c,unsigned d,unsigned e) {}
static void game_probe_rgb_audit(SDL_Surface *p,unsigned mismatches) {audit_mismatch=mismatches;}
static void game_probe_frame(unsigned a,unsigned b,unsigned c,const char *d,const char *e,unsigned f,unsigned g,unsigned h) {++frames;}
static bool game_probe_capture_tick(void) {return false;}
static void game_probe_export(SDL_Surface *p,const char *name) {assert(false);}
static void game_probe_present(unsigned count,uint64_t before,uint64_t after) {assert(before==after);++presents;}
static void render_mirror_reset_banking(void) {}
static SDL_Surface *canvas,*output,*fade_saved,*game_screen,*VGAScreenSeg;
static SDL_Texture *texture;
static Uint32 rgb_palette[256],initial_palette[256],fade_saved_palette[256],last_output_palette[256];
static Uint8 last_output_indices[64000],expected[64000],selected[64000],restored_mask[64000];
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static Uint8 hud_output_owner[64000],hud_saved_owner[64000];
static Uint32 hud_output_palette[256];
static uint64_t hud_generation,hud_output_generation,hud_saved_generation,mirror_logic_tick;
static bool hud_gameplay,hud_suspended,hud_live,last_output_scene_hd;
static SDL_Surface *hud_source_surface;
static void *hud_source_pixels;
static SDL_PixelFormat *hud_source_format;
static int hud_source_pitch,hud_source_width,hud_source_height;
static Uint8 component_output_owner[64000],component_saved_owner[64000];
static Uint32 component_output_palette[256];
static uint64_t component_generation,component_output_generation,component_saved_generation;
static bool component_gameplay,component_suspended;
static SDL_Surface *component_source_surface;
static void *component_source_pixels;
static SDL_PixelFormat *component_source_format;
static int component_source_pitch;
/* HUL1 is the only overlapping HUD layer. Save the actual already-composed
 * HUD1 subpixels, never reconstruct its authored RGB from indexed pixels. */
static Uint8 indicator_output_owner[237],indicator_saved_owner[237];
static Uint32 indicator_output_palette[256];
static uint64_t indicator_generation,indicator_output_generation,indicator_saved_generation;
static bool indicator_gameplay,indicator_suspended;
static SDL_Surface *indicator_source_surface;
static void *indicator_source_pixels;
static SDL_PixelFormat *indicator_source_format;
static int indicator_source_pitch,indicator_under_density;
static Uint32 indicator_under[82][64],indicator_saved_under[82][64];
static Uint8 indicator_under_owner[82],indicator_saved_under_owner[82];
static uint64_t indicator_under_generation,indicator_saved_under_generation;
static const Uint16 indicator_overlap_positions[82]={14365,14366,14369,14372,14373,14374,14375,14376,14377,14378,14379,14380,14381,14382,14383,14386,14389,14390,14391,14693,14695,14696,14697,14698,14699,14700,14701,14710,15015,15016,15017,15018,15019,15020,15021,15335,15336,15337,15338,15339,15340,15341,15655,15656,15657,15658,15659,15660,15661,15975,15976,15977,15978,15979,15980,15981,15982,16292,16293,16295,16296,16297,16298,16299,16300,16301,16303,16309,16310,16606,16613,16614,16615,16616,16617,16618,16619,16620,16621,16622,16623,16630};
/* Disjoint HUT1 fixed-label ownership, compact370-cell ledger. */
static Uint8 fixed_text_output_owner[370],fixed_text_saved_owner[370];
static Uint32 fixed_text_output_palette[256];
static uint64_t fixed_text_generation,fixed_text_output_generation,fixed_text_saved_generation;
static bool fixed_text_gameplay,fixed_text_suspended;
static SDL_Surface *fixed_text_source_surface;
static void *fixed_text_source_pixels;
static SDL_PixelFormat *fixed_text_source_format;
static int fixed_text_source_pitch;
static bool active,suppress,ready,suppress_green_smoke,suppress_cloud,have_initial_palette,last_output_valid,have_fade_saved;
static int fade_mode;
static const char *reject_reason;
static unsigned draws,occlusions,mismatch,banking_draw_player,green_head_count,region_count,local_entities,local_regions,local_blocks;
static unsigned brightness_blocks,restored_checks,restored_mismatches,expanded_regions,boundary_crossings;
static char all_rejections[512];
static bool game_probe_enabled,game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_coverage_fault,game_probe_skip,game_probe_repeat;
static bool twoPlayerMode,galagaMode;
static const char *game_probe_assets;
static int game_probe_density;
static unsigned game_probe_tick;
#define SPRITE_TABLES_MAX 8
#define SPRITES_PER_TABLE_MAX 152
#define TINY_FONT 2
#define OPTION_SHAPES 5
#define OPTION_NUM 37
#define SHIELD_NUM 11
#define COUNTOF(x) (sizeof(x)/sizeof((x)[0]))
typedef struct { Uint16 width,height,size; Uint8 *data; } Sprite;
static struct {unsigned int count;Sprite sprite[152];} sprite_table[8];
static int font_ascii[256];
static struct {Uint8 ammo,icongr;} options[38];
static struct {Uint8 mpwr;} shields[12];
static char levelName[11];
static unsigned int power,lastPower;
static struct {
 unsigned int shield,shield_max,armor;
 struct {struct {unsigned int power;} weapon[2];unsigned int sidekick[2];} items;
 struct {int ammo,ammo_max;} sidekick[2];
} player[2];
static bool components_owned(void);
static bool indicators_owned(void);
static Uint32 palette_rgb(Uint8 index);
void render_mirror_unsupported(const char *reason);
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#ifndef BASELINE_RENDERER
#ifdef FONT_ALLOCATION_ORACLE
static size_t font_alloc_calls,font_alloc_bytes,font_free_calls,font_alloc_failed;
static bool font_alloc_fail;
static void *font_test_calloc(size_t n,size_t bytes)
{++font_alloc_calls;if(font_alloc_fail){++font_alloc_failed;return NULL;}void *p=calloc(n,bytes);if(p)font_alloc_bytes+=n*bytes;return p;}
static void font_test_free(void *p){if(p)++font_free_calls;free(p);}
#define calloc font_test_calloc
#define free font_test_free
#endif
#include "gameplay_hud_font_mirror.inc"
#ifdef FONT_ALLOCATION_ORACLE
#undef calloc
#undef free
#endif
#else
#define font_shutdown() hud_font_shutdown()
#endif
#include "production.inc"

static uint64_t aggregate=UINT64_C(14695981039346656037);
static void digest(const void *p,size_t n) {const Uint8 *b=p;for(size_t i=0;i<n;i++)aggregate=(aggregate^b[i])*UINT64_C(1099511628211);}
static Uint32 *pixel(SDL_Surface *p,int x,int y) {return (Uint32 *)((Uint8 *)p->pixels+y*p->pitch)+x;}
static void cleanup(void)
{
 font_shutdown();
 SDL_FreeSurface(canvas);SDL_FreeSurface(output);SDL_FreeSurface(fade_saved);SDL_FreeSurface(game_screen);SDL_FreeSurface(VGAScreenSeg);
 canvas=output=fade_saved=game_screen=VGAScreenSeg=NULL;
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 hd_owner=cloud_owner=green_under_owner=NULL;green_first=NULL;green_under=NULL;
 gameplay_hud_shutdown();hud_components_shutdown();hud_meters_shutdown();hud_indicators_shutdown();hud_fixed_text_shutdown();
}
static void setup(int d,const char *directory)
{
 cleanup();game_probe_density=d;game_probe_assets=directory;
 game_probe_enabled=true;game_probe_missing=game_probe_invalid=game_probe_original_reference=game_probe_coverage_fault=false;
 game_probe_skip=true;game_probe_repeat=false;twoPlayerMode=galagaMode=false;
 last_output_valid=have_fade_saved=have_initial_palette=ready=active=false;fade_mode=0;texture=NULL;
 hud_source_surface=NULL;hud_source_pixels=NULL;hud_source_format=NULL;
 fixed_text_gameplay=fixed_text_suspended=false;fixed_text_source_surface=NULL;fixed_text_source_pixels=NULL;fixed_text_source_format=NULL;
 fixed_text_output_generation=fixed_text_saved_generation=0;
 memset(fixed_text_output_owner,0,sizeof(fixed_text_output_owner));memset(fixed_text_saved_owner,0,sizeof(fixed_text_saved_owner));
 indicator_gameplay=indicator_suspended=false;indicator_source_surface=NULL;indicator_source_pixels=NULL;indicator_source_format=NULL;
 indicator_output_generation=indicator_saved_generation=0;
 memset(indicator_output_owner,0,sizeof(indicator_output_owner));memset(indicator_saved_owner,0,sizeof(indicator_saved_owner));
 memset(indicator_under_owner,0,sizeof(indicator_under_owner));memset(indicator_saved_under_owner,0,sizeof(indicator_saved_under_owner));
 component_gameplay=component_suspended=false;component_source_surface=NULL;component_source_pixels=NULL;component_source_format=NULL;
 component_output_generation=component_saved_generation=0;
 memset(component_output_owner,0,sizeof(component_output_owner));memset(component_saved_owner,0,sizeof(component_saved_owner));
 hud_gameplay=hud_suspended=hud_live=false;hud_output_generation=hud_saved_generation=0;last_output_scene_hd=false;
 memset(hud_output_owner,0,sizeof(hud_output_owner));memset(hud_saved_owner,0,sizeof(hud_saved_owner));
 game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);
 memset(game_screen->pixels,7,64000);memset(VGAScreenSeg->pixels,7,64000);
 for(unsigned i=0;i<256;i++)rgb_palette[i]=((i*5%256)<<16)|((i*11%256)<<8)|(i*17%256);
}
static void scene_pixel(void)
{
 int d=game_probe_density;
 *pixel(canvas,54*d,20*d)=0xffdc51a3u;hd_owner[20*d*canvas->w+54*d]=1;
}
static void frame(bool scene,bool ordinary)
{
 uint64_t before=gameplay_hud_fnv64(VGAScreenSeg->pixels,64000),game_before=gameplay_hud_fnv64(game_screen->pixels,64000);
 render_mirror_begin();if(scene)scene_pixel();render_mirror_finish(ordinary);
 assert(before==gameplay_hud_fnv64(VGAScreenSeg->pixels,64000));
 assert(game_before==gameplay_hud_fnv64(game_screen->pixels,64000));
}
static void palette_step(unsigned solid,int steps,const Uint32 *target)
{
 for(int i=0;i<256;i++) {
  Uint32 value=0;
  for(int s=0;s<24;s+=8) {
   int old=(rgb_palette[i]>>s)&255,want=target?(int)((target[i]>>s)&255):(int)solid;
   value|=(Uint32)(old+(want-old)/steps)<<s;
  }
  rgb_palette[i]=value;
 }
}
static Uint32 channel_step(Uint32 before,Uint32 target,int steps)
{
 Uint32 result=0xff000000u;
 for(int shift=0;shift<24;shift+=8) {
  int old=(before>>shift)&255,want=(target>>shift)&255;
  result|=(Uint32)(old+(want-old)/steps)<<shift;
 }
 return result;
}
static void baseline_suite(void)
{
 for(int d=1;d<=8;d=d==1?4:8) {
  for(int mode=0;mode<5;mode++) {
   setup(d,NULL);
#ifndef BASELINE_RENDERER
   render_mirror_hud_start(VGAScreenSeg);assert(!hud_gameplay);
#endif
   if(mode==3)game_probe_original_reference=true;
   render_mirror_begin();if(mode!=0)scene_pixel();
   if(mode==4)rgb_palette[0]^=1;
   render_mirror_finish(mode!=2);
   digest(output->pixels,(size_t)output->pitch*output->h);
   digest(&last_output_valid,sizeof(last_output_valid));digest(&ready,sizeof(ready));
   SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
   for(int step=3;step;step--) {
    palette_step(0,step,NULL);render_mirror_fade_step(step);
    digest(output->pixels,(size_t)output->pitch*output->h);digest(&fade_mode,sizeof(fade_mode));
   }
   bool first=render_mirror_present(NULL,VGAScreenSeg,NULL),second=render_mirror_present(NULL,VGAScreenSeg,NULL);
   digest(&first,sizeof(first));digest(&second,sizeof(second));assert(!second);
  }
  if(d==8)break;
 }
 printf("BASELINE %016llx\n",(unsigned long long)aggregate);
}
#ifndef BASELINE_RENDERER
static Uint8 expansion_mask[64000];
static bool expanded_test;
static const int points[4][2]={{264,0},{319,0},{280,109},{0,184}};
static Uint32 authored(int x,int y,int sx,int sy,int d)
{
 sx/=d/4;sy/=d/4;
 return 0xff000000u|((Uint32)((x*13+sx*3)%256)<<16)|((Uint32)((y*7+sy*5)%256)<<8)|(unsigned)((sx+sy*4)*9);
}
static bool point(int x,int y)
{if(expanded_test)return expansion_mask[y*320+x]!=0;for(int i=0;i<4;i++)if(x==points[i][0]&&y==points[i][1])return true;return false;}
static void check_frame(bool hud,bool scene)
{
 int d=game_probe_density;
 for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d];
  Uint32 want=palette_rgb(index);
  if(!reject_reason&&x<264*d&&y<184*d)want=palette_rgb(((Uint8 *)game_screen->pixels)[(y/d)*320+x/d+24]);
  bool owned=hud&&point(x/d,y/d)&&index==7;
  if(owned)want=authored(x/d,y/d,x%d,y%d,d);
  if(scene&&x==30*d&&y==20*d)want=0xffdc51a3u;
  if(*pixel(output,x,y)!=want) {fprintf(stderr,"check_frame failure frame=%u density=%d hud=%d scene=%d at%d,%d actual=%08x want=%08x gen=%llu suspended=%d reason=%s\n",frames,d,hud,scene,x,y,*pixel(output,x,y),want,(unsigned long long)hud_generation,hud_suspended,reject_reason?reject_reason:"none");abort();}
  assert(hud_output_owner[(y/d)*320+x/d]==owned);
 }
}
static void activate(const char *directory,int d)
{expanded_test=false;setup(d,directory);render_mirror_hud_start(VGAScreenSeg);assert(hud_gameplay&&gameplay_hud_ready());}
static void fade_suite(const char *directory,int d,unsigned solid)
{
 activate(directory,d);frame(true,true);check_frame(true,true);
 Uint32 palette[256];memcpy(palette,rgb_palette,sizeof(palette));
 SDL_Color target={solid,solid,solid,255};render_mirror_fade_start(NULL,&target,0,255);
 assert(fade_mode==(solid?2:1)&&have_fade_saved);
 assert(hud_saved_generation==hud_generation&&memcmp(hud_saved_owner,hud_output_owner,64000)==0);
 for(int step=5;step;step--) {
  Uint32 prior=*pixel(output,264*d+1,1),scene=*pixel(output,30*d,20*d);
  palette_step(solid,step,NULL);render_mirror_fade_step(step);
  Uint32 want=solid?0xffffffffu:0xff000000u;
  assert(*pixel(output,264*d+1,1)==channel_step(prior,want,step));
  assert(*pixel(output,30*d,20*d)==channel_step(scene,want,step));
  assert(*pixel(output,265*d,0)==palette_rgb(7));assert(sample_hd==4u*d*d+1);
  assert(render_mirror_present(NULL,VGAScreenSeg,NULL));assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 }
 SDL_Color restore[256];for(int i=0;i<256;i++)restore[i]=(SDL_Color){palette[i]>>16,palette[i]>>8,palette[i],255};
 render_mirror_fade_start(restore,NULL,0,255);assert(fade_mode==3);
 for(int step=4;step;step--) {palette_step(0,step,palette);render_mirror_fade_step(step);}
 check_frame(true,true);
 /* Mid-fade suspension restores ONLY HUD-owned current/saved pixels. */
 frame(true,true);render_mirror_fade_start(NULL,&target,0,255);palette_step(solid,3,NULL);render_mirror_fade_step(3);
 Uint32 current_scene=*pixel(output,30*d,20*d),saved_scene=*pixel(fade_saved,30*d,20*d);
 unsigned old_mode=fade_mode;uint64_t generation=hud_generation;
 render_mirror_hud_suspend();render_mirror_hud_suspend();
 assert(hud_suspended&&hud_generation==generation&&fade_mode==(int)old_mode&&have_fade_saved&&last_output_valid);
 assert(*pixel(output,30*d,20*d)==current_scene&&*pixel(fade_saved,30*d,20*d)==saved_scene);
 for(int i=0;i<4;i++) {
  assert(*pixel(output,points[i][0]*d,points[i][1]*d)==palette_rgb(7));
  assert(*pixel(fade_saved,points[i][0]*d,points[i][1]*d)==(0xff000000u|palette[7]));
 }
 assert(!memchr(hud_output_owner,1,64000)&&!memchr(hud_saved_owner,1,64000));
 palette_step(solid,2,NULL);render_mirror_fade_step(2);assert(sample_hd==1);
 /* Restore palette before another ordinary frame; otherwise gamma guard wins. */
 memcpy(rgb_palette,palette,sizeof(palette));frame(true,true);assert(!hud_suspended);check_frame(true,true);
 render_mirror_fade_start(NULL,&target,0,255);palette_step(solid,3,NULL);render_mirror_fade_step(3);
 current_scene=*pixel(output,30*d,20*d);saved_scene=*pixel(fade_saved,30*d,20*d);
 render_mirror_hud_reset();assert(!hud_gameplay&&!gameplay_hud_ready());
 assert(*pixel(output,30*d,20*d)==current_scene&&*pixel(fade_saved,30*d,20*d)==saved_scene);
 assert(have_fade_saved&&last_output_valid);palette_step(solid,2,NULL);render_mirror_fade_step(2);assert(sample_hd==1);
}
static void lifecycle_suite(const char *directory,int d)
{
 activate(directory,d);assert(!ready);assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 frame(true,true);check_frame(true,true);
 unsigned allocation_count=allocations;frame(true,true);assert(allocations==allocation_count);
 /* Equality is only an occlusion check: a generic replacement with identical
  * indices must not re-authorize the lease. PIC6 and new-level entry use reset. */
 uint64_t generation=hud_generation;render_mirror_hud_reset();assert(hud_generation!=generation);
 check_frame(false,true);frame(true,true);check_frame(false,true);assert(!gameplay_hud_ready());
 render_mirror_hud_start(VGAScreenSeg);frame(true,true);check_frame(true,true);
 for(int mode=0;mode<2;mode++) {
  if(mode)galagaMode=true;else twoPlayerMode=true;
  assert(render_mirror_present(NULL,VGAScreenSeg,NULL));assert(!hud_gameplay);check_frame(false,true);
  galagaMode=twoPlayerMode=false;frame(true,true);check_frame(false,true);
  render_mirror_hud_start(VGAScreenSeg);frame(true,true);check_frame(true,true);
 }
 /* Each modal entry suspends immediately; an interrupted finish remains classic. */
 for(int modal=0;modal<3;modal++) {
  render_mirror_begin();scene_pixel();render_mirror_hud_suspend();render_mirror_finish(true);
  check_frame(false,true);assert(hud_suspended);
  frame(true,true);check_frame(true,true);assert(!hud_suspended);
 }
 /* Occluding original writes remain untouched. Never infer a new screen. */
 ((Uint8 *)VGAScreenSeg->pixels)[264]=9;((Uint8 *)game_screen->pixels)[264]=9;
 frame(true,true);check_frame(true,true);assert(!hud_output_owner[264]);
 ((Uint8 *)VGAScreenSeg->pixels)[264]=7;((Uint8 *)game_screen->pixels)[264]=7;
 frame(true,false);check_frame(false,false);assert(reject_reason&&!last_output_valid);
 frame(true,true);check_frame(true,true);
 rgb_palette[0]^=1;frame(true,true);check_frame(false,false);assert(reject_reason&&!last_output_valid);rgb_palette[0]^=1;
 frame(true,true);check_frame(true,true);
 /* A stale index or palette must reject cached output, including scene cache. */
 ((Uint8 *)VGAScreenSeg->pixels)[0]=8;render_mirror_hud_suspend();assert(!ready&&!last_output_valid&&!have_fade_saved);
 ((Uint8 *)VGAScreenSeg->pixels)[0]=7;frame(true,true);check_frame(true,true);
 rgb_palette[0]^=1;render_mirror_hud_reset();assert(!ready&&!last_output_valid);rgb_palette[0]^=1;
 render_mirror_hud_start(VGAScreenSeg);frame(true,true);check_frame(true,true);
 /* Benign renderer recreation suspends; true video teardown revokes. */
 generation=hud_generation;render_mirror_release_texture();assert(hud_gameplay&&hud_suspended&&generation==hud_generation&&!ready);
 frame(true,true);check_frame(true,true);
 render_mirror_hud_shutdown();assert(!hud_gameplay&&!gameplay_hud_ready());frame(true,true);check_frame(false,true);
 /* Mode changes are rechecked after begin and at fade entry/step, too. */
 activate(directory,d);render_mirror_begin();scene_pixel();twoPlayerMode=true;render_mirror_finish(true);
 assert(!hud_gameplay);check_frame(false,true);twoPlayerMode=false;frame(true,true);check_frame(false,true);
 render_mirror_hud_start(VGAScreenSeg);frame(true,true);
 SDL_Color black={0,0,0,255};galagaMode=true;render_mirror_fade_start(NULL,&black,0,255);
 assert(!hud_gameplay&&fade_mode==1);assert(!memchr(hud_saved_owner,1,64000));
 palette_step(0,1,NULL);render_mirror_fade_step(1);assert(sample_hd==1);
 activate(directory,d);frame(true,true);render_mirror_fade_start(NULL,&black,0,255);
 twoPlayerMode=true;render_mirror_fade_step(2);assert(!hud_gameplay&&sample_hd==1);
 /* A mode change coincident with a palette update fails closed if the HUD's
  * previous output palette can no longer be verified. */
 activate(directory,d);frame(true,true);render_mirror_fade_start(NULL,&black,0,255);
 twoPlayerMode=true;palette_step(0,2,NULL);render_mirror_fade_step(2);
 assert(!hud_gameplay&&!ready&&!last_output_valid&&!have_fade_saved);
 /* Unsupported partial fades do not manufacture a pending HUD presentation. */
 activate(directory,d);frame(true,true);render_mirror_fade_start(NULL,&black,1,255);
 assert(!fade_mode&&!ready&&!last_output_valid);assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 frame(true,true);check_frame(true,true);
 /* HUD-only reset clears fade validity, while a valid all-classic pending
  * output may still be consumed once. */
 activate(directory,d);frame(false,true);render_mirror_hud_reset();check_frame(false,false);
 assert(!last_output_valid);assert(render_mirror_present(NULL,VGAScreenSeg,NULL));
 assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 activate(directory,d);frame(true,true);render_mirror_hud_suspend();render_mirror_hud_reset();
 frame(true,true);assert(!hud_gameplay&&!hud_suspended);check_frame(false,true);
 /* Missing, disabled, PIC6/Galaga modes and original-copy diagnostics never arm. */
 for(int flag=0;flag<7;flag++) {
  setup(d,directory);
  if(flag==0)game_probe_enabled=false;
  if(flag==1)game_probe_missing=true;
  if(flag==2)game_probe_invalid=true;
  if(flag==3)game_probe_original_reference=true;
  if(flag==4)twoPlayerMode=true;
  if(flag==5)galagaMode=true;
  if(flag==6)VGAScreenSeg->format->BytesPerPixel=4;
  render_mirror_hud_start(VGAScreenSeg);assert(!hud_gameplay&&!gameplay_hud_ready());
 }
}

static void lease_suite(const char *directory)
{
 /* Grant only the decoded persistent surface, even for identical bytes. */
 setup(4,directory);render_mirror_hud_start(game_screen);assert(!hud_gameplay);
 void *pixels=VGAScreenSeg->pixels;VGAScreenSeg->pixels=NULL;
 render_mirror_hud_start(VGAScreenSeg);assert(!hud_gameplay);VGAScreenSeg->pixels=pixels;
 for(int field=0;field<9;field++) {
  activate(directory,4);frame(true,true);
  SDL_Surface *original=VGAScreenSeg;SDL_PixelFormat *format=original->format;pixels=original->pixels;
  int pitch=original->pitch,w=original->w,h=original->h;
  if(field==0) {VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);memset(VGAScreenSeg->pixels,7,64000);SDL_FreeSurface(original);}
  if(field==1) {original->pixels=malloc(64000);assert(original->pixels);memset(original->pixels,7,64000);free(pixels);}
  if(field==2) {original->format=malloc(sizeof(*format));assert(original->format);*original->format=*format;free(format);}
  if(field==3)original->pitch++;
  if(field==4)original->w--;
  if(field==5)original->h--;
  if(field==6)original->format->BitsPerPixel=4;
  if(field==7)original->format->BytesPerPixel=4;
  if(field==8)VGAScreenSeg=NULL;
  /* Suspension must reject before reading old/freed pixels or format. */
  render_mirror_hud_suspend();assert(!hud_gameplay&&!hud_suspended&&!ready&&!last_output_valid);
  assert(!hud_source_surface&&!hud_source_pixels&&!hud_source_format);
  if(field>=3&&field<=7) {original->pitch=pitch;original->w=w;original->h=h;original->format->BitsPerPixel=8;original->format->BytesPerPixel=1;}
  if(field==8)VGAScreenSeg=original;
  frame(true,true);check_frame(false,true);render_mirror_hud_start(VGAScreenSeg);assert(hud_gameplay);
 }
}
static Uint8 font_data[48],icon_data[364],mode_data[2][80];
static void valid_bindings(void)
{
 memset(sprite_table,0,sizeof(sprite_table));memset(options,0,sizeof(options));memset(shields,0,sizeof(shields));
 memset(player,0,sizeof(player));power=900;lastPower=90;
 player[0].shield=player[0].shield_max=player[0].armor=28;
 for(int i=0;i<2;i++) {player[0].items.weapon[i].power=11;player[0].sidekick[i].ammo=player[0].sidekick[i].ammo_max=100;}
 for(int i=0;i<256;i++)font_ascii[i]=-1;font_ascii['A']=0;
 memset(font_data,7,sizeof(font_data));memset(icon_data,7,sizeof(icon_data));memset(mode_data,7,sizeof(mode_data));
 sprite_table[TINY_FONT].count=1;sprite_table[TINY_FONT].sprite[0]=(Sprite){6,8,sizeof(font_data),font_data};
 sprite_table[OPTION_SHAPES].count=20;sprite_table[OPTION_SHAPES].sprite[0]=(Sprite){28,13,sizeof(icon_data),icon_data};
 for(int i=0;i<2;i++)sprite_table[OPTION_SHAPES].sprite[18+i]=(Sprite){10,8,80,mode_data[i]};
 for(int i=0;i<=OPTION_NUM;i++){options[i].icongr=1;options[i].ammo=100;}
 for(int i=0;i<=SHIELD_NUM;i++)shields[i].mpwr=14;
 strcpy(levelName,"AAAAAAAAAA");
}
static void read_fixture(const char *dir,const char *name,void *data,size_t size)
{
 char path[1024];assert(snprintf(path,sizeof(path),"%s/%s",dir,name)<(int)sizeof(path));
 FILE *f=fopen(path,"rb");assert(f);assert(fread(data,1,size,f)==size);assert(fgetc(f)==EOF);fclose(f);
}
static void expanded_setup(const char *directory,int d)
{
 setup(d,directory);expanded_test=true;valid_bindings();
 read_fixture(directory,"source.indices",VGAScreenSeg->pixels,64000);
 read_fixture(directory,"synthetic.mask",expansion_mask,64000);
}
static void mutate_binding(unsigned which)
{
 switch(which) {
 case 0:font_ascii['A']=152;break;
 case 1:sprite_table[TINY_FONT].sprite[0].width=7;break;
 case 2:sprite_table[TINY_FONT].sprite[0].height=9;break;
 case 3:sprite_table[TINY_FONT].sprite[0].data=NULL;break;
 case 4:font_data[0]=255;font_data[1]=7;break; /* row-crossing RLE */
 case 5:font_data[47]=255;break; /* truncated skip */
 case 6:font_data[0]=254;font_data[1]=254;break; /* too many rows */
 case 7:sprite_table[TINY_FONT].count=153;break;
 case 8:options[37].ammo=19;break; /* would draw 19 segments */
 case 9:options[37].icongr=153;break;
 case 10:sprite_table[OPTION_SHAPES].sprite[0].width=29;break;
 case 11:sprite_table[OPTION_SHAPES].sprite[0].height=14;break;
 case 12:shields[11].mpwr=15;break;
 case 13:memset(levelName,'A',sizeof(levelName));break;
 case 14:sprite_table[OPTION_SHAPES].sprite[18].width=9;break;
 case 15:memset(mode_data[1],8,80);break;
 case 16:memset(mode_data[0],253,80);break;
 case 17:power=901;break;
 case 18:lastPower=91;break;
 case 19:player[0].shield=29;break;
 case 20:player[0].shield_max=29;break;
 case 21:player[0].armor=29;break;
 case 22:player[0].items.weapon[1].power=12;break;
 case 23:player[0].items.sidekick[1]=38;break;
 case 24:player[0].sidekick[1].ammo=-1;break;
 case 25:player[0].sidekick[1].ammo_max=-1;break;
 case 26:player[0].sidekick[1].ammo=101;break;
 case 27:player[0].sidekick[1].ammo_max=256;break;
 case 28:player[0].sidekick[1].ammo=19;player[0].sidekick[1].ammo_max=19;break;
 default:assert(false);
 }
}
static void expanded_suite(const char *directory,int d)
{
 expanded_setup(directory,d);render_mirror_hud_start(VGAScreenSeg);assert(hud_gameplay);
 frame(true,true);check_frame(true,true);
 unsigned owners=0;for(unsigned i=0;i<64000;i++)owners+=hud_output_owner[i];assert(owners==310);
 unsigned old_allocations=allocations;frame(true,true);assert(allocations==old_allocations);
 SDL_Color black={0,0,0,255};Uint32 palette[256];memcpy(palette,rgb_palette,sizeof(palette));
 for(unsigned solid=0;solid<=255;solid+=255) {
  SDL_Color target={solid,solid,solid,255};render_mirror_fade_start(NULL,&target,0,255);
  for(int step=3;step;step--) {palette_step(solid,step,NULL);render_mirror_fade_step(step);assert(sample_hd==310u*d*d+1);}
  SDL_Color restore[256];for(int i=0;i<256;i++)restore[i]=(SDL_Color){palette[i]>>16,palette[i]>>8,palette[i],255};
  render_mirror_fade_start(restore,NULL,0,255);
  for(int step=3;step;step--){palette_step(0,step,palette);render_mirror_fade_step(step);}
  check_frame(true,true);if(solid==255)break;
 }
 uint64_t generation=hud_generation;render_mirror_release_texture();assert(hud_suspended&&hud_gameplay&&generation==hud_generation);
 frame(true,true);check_frame(true,true);
 if(d==8)return;
 for(unsigned mutation=0;mutation<29;mutation++) {
  expanded_setup(directory,d);mutate_binding(mutation);render_mirror_hud_start(VGAScreenSeg);
  if(mutation<17)assert(!hud_gameplay);
  else {assert(hud_gameplay&&!hud_live);hud_begin();assert(!hud_gameplay);}
  valid_bindings();render_mirror_hud_start(VGAScreenSeg);assert(hud_gameplay);frame(true,true);
  render_mirror_fade_start(NULL,&black,0,255);
  Uint32 scene=*pixel(output,30*d,20*d),saved=*pixel(fade_saved,30*d,20*d);
  mutate_binding(mutation);hud_check_mode();assert(!hud_gameplay&&!gameplay_hud_ready());
  assert(*pixel(output,30*d,20*d)==scene&&*pixel(fade_saved,30*d,20*d)==saved&&have_fade_saved);
  assert(!memchr(hud_output_owner,1,64000)&&!memchr(hud_saved_owner,1,64000));
  valid_bindings();hud_begin();assert(!hud_gameplay); /* no implicit regrant */
 }
 /* Mutations after begin and at each cache boundary revoke immediately. */
 for(int boundary=0;boundary<4;boundary++) {
  expanded_setup(directory,d);render_mirror_hud_start(VGAScreenSeg);frame(true,true);
  if(boundary==0)render_mirror_begin();
  if(boundary==2)render_mirror_fade_start(NULL,&black,0,255);
  shields[0].mpwr=15;
  if(boundary==0)render_mirror_finish(true);
  if(boundary==1)render_mirror_fade_start(NULL,&black,0,255);
  if(boundary==2)render_mirror_fade_step(2);
  if(boundary==3)render_mirror_present(NULL,VGAScreenSeg,NULL);
  assert(!hud_gameplay&&!memchr(hud_output_owner,1,64000));
 }
}

#endif
int main(int argc,char **argv)
{
 assert(argc==2);baseline_suite();
#ifndef BASELINE_RENDERER
 for(int d=4;d<=8;d+=4) {lifecycle_suite(argv[1],d);fade_suite(argv[1],d,0);fade_suite(argv[1],d,255);}
 lease_suite(argv[1]);
 char expanded[1024];assert(snprintf(expanded,sizeof(expanded),"%s/expanded",argv[1])<(int)sizeof(expanded));
 for(int d=4;d<=8;d+=4)expanded_suite(expanded,d);
 printf("Expanded exact310 runtime data/font/mode/live-bound mutations and persistent source lease tests passed.\n");
 printf("Synthetic lifecycle, ordinary/special/gamma, occlusion, density, cache-reset, renderer recreation and black/white+restore fade oracles passed.\n");
#endif
 cleanup();return 0;
}
