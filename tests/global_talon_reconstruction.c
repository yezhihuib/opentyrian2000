/* SPDX-License-Identifier: GPL-2.0-or-later
 * Current-production Talon13 observer. SDL is a bounded structural shim.
 * This test is not an integrated engine/gameplay/native-caller proof.
 * Original bytes arrive on stdin, remain in process memory and are never saved.
 */
/* SHOP owner is deliberately disabled in these battle-only shims. */
#define pregame_shop_pulse_set_directory(...) ((void)0)
#define pregame_shop_ship_set_directory(...) ((void)0)
#define shop_pulse_allocated(...) ((void)0)
#define shop_pulse_initialized(...) ((void)0)
#define pregame_shop_vulcan_set_directory(...) ((void)0)
#define shop_vulcan_allocated(...) ((void)0)
#define shop_vulcan_initialized(...) ((void)0)
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct {Uint8 r,g,b,a;} SDL_Color;
typedef struct {unsigned format;int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;SDL_Rect clip_rect;} SDL_Surface;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ENTITY_TILE,ENTITY_QUAD};
enum {SDL_PIXELFORMAT_ARGB8888=1,SDL_PIXELFORMAT_INDEX8=2};
typedef enum {MIRROR_OUTPUT_UNSUPPORTED,MIRROR_OUTPUT_ORDINARY,MIRROR_OUTPUT_NORMAL15_NIGHT,MIRROR_OUTPUT_NORMAL15_LOW_DETAIL} MirrorOutputKind;
/* This family is disabled in this isolated regression harness. */
/* Vulcan is disabled only in this isolated regression harness. */
static bool global_vulcan_frame,global_vulcan_fault,global_vulcan_cached;
static Uint8 *global_vulcan_owner,*global_vulcan_foreign;
static bool global_vulcan_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_vulcan_palette_matches(void){return true;}
static bool global_vulcan_requested(void){return false;}
static bool global_vulcan_is_index(unsigned index){return false;}
static bool global_vulcan_surface_matches(void){return true;}
static bool global_vulcan_final_surface_matches(void){return true;}
static void global_vulcan_shutdown(void){}
static void global_vulcan_reset(void){}
static void global_vulcan_root_changed(void){}
static void global_vulcan_frame_begin(void){}
static bool global_vulcan_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_vulcan_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_vulcan_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_vulcan_end(void){}
static bool global_vulcan_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_vulcan_finish_proof(void){return true;}
static bool global_vulcan_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_vulcan_check_cache(void){}
static bool global_vulcan_fade_buffer_safe(void){return true;}
static bool global_vulcan_fade_capture(void){return true;}
static bool global_vulcan_fade_step_valid(int steps){return true;}
static void global_vulcan_fade_palette(void){}
/* Small explosion disabled only in this isolated existing-family harness. */
static bool global_small_explosion_frame,global_small_explosion_fault,global_small_explosion_cached;
static Uint8 *global_small_explosion_owner,*global_small_explosion_foreign;
static bool global_small_explosion_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_small_explosion_palette_matches(void){return true;}
static bool global_small_explosion_requested(void){return false;}
static bool global_small_explosion_is_index(unsigned index){return false;}
static bool global_small_explosion_surface_matches(void){return true;}
static bool global_small_explosion_final_surface_matches(void){return true;}
static void global_small_explosion_shutdown(void){}
static void global_small_explosion_reset(void){}
static void global_small_explosion_frame_begin(void){}
static bool global_small_explosion_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_small_explosion_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_small_explosion_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_small_explosion_end(void){}
static bool global_small_explosion_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_small_explosion_finish_proof(void){return true;}
static bool global_small_explosion_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_small_explosion_check_cache(void){}
static bool global_small_explosion_fade_buffer_safe(void){return true;}
static bool global_small_explosion_fade_capture(void){return true;}
static bool global_small_explosion_fade_step_valid(int steps){return true;}
static void global_small_explosion_fade_palette(void){}
#define render_mirror_small_explosion_allocated(...) ((void)0)
#define render_mirror_small_explosion_initialized(...) ((void)0)
/* White smoke disabled only in this isolated existing-family harness. */
static bool global_smoke_frame,global_smoke_fault,global_smoke_cached;
static Uint8 *global_smoke_owner,*global_smoke_foreign;
static bool global_smoke_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_smoke_palette_matches(void){return true;}
static bool global_smoke_requested(void){return false;}
static bool global_smoke_is_index(unsigned index){return false;}
static bool global_smoke_surface_matches(void){return true;}
static bool global_smoke_final_surface_matches(void){return true;}
static void global_smoke_shutdown(void){}
static void global_smoke_reset(void){}
static void global_smoke_frame_begin(void){}
static bool global_smoke_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_smoke_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_smoke_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_smoke_end(void){}
static bool global_smoke_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_smoke_finish_proof(void){return true;}
static bool global_smoke_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_smoke_check_cache(void){}
static bool global_smoke_fade_buffer_safe(void){return true;}
static bool global_smoke_fade_capture(void){return true;}
static bool global_smoke_fade_step_valid(int steps){return true;}
static void global_smoke_fade_palette(void){}
#define render_mirror_smoke_explosion_allocated(...) ((void)0)
#define render_mirror_smoke_explosion_initialized(...) ((void)0)
static bool global_hitflare_frame,global_hitflare_fault,global_hitflare_cached;
static Uint8 *global_hitflare_owner,*global_hitflare_foreign;
static bool global_hitflare_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_hitflare_palette_matches(void){return true;}
static bool global_hitflare_requested(void){return false;}
static bool global_hitflare_is_index(unsigned index){return false;}
static bool global_hitflare_surface_matches(void){return true;}
static bool global_hitflare_final_surface_matches(void){return true;}
static void global_hitflare_shutdown(void){}
static void global_hitflare_reset(void){}
static void global_hitflare_frame_begin(void){}
static bool global_hitflare_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_hitflare_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_hitflare_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_hitflare_end(void){}
static bool global_hitflare_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_hitflare_finish_proof(void){return true;}
static bool global_hitflare_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_hitflare_check_cache(void){}
static bool global_hitflare_fade_buffer_safe(void){return true;}
static bool global_hitflare_fade_capture(void){return true;}
static bool global_hitflare_fade_step_valid(int steps){return true;}
static void global_hitflare_fade_palette(void){}
static void render_mirror_hitflare_explosion_allocated(unsigned slot){(void)slot;}
static void render_mirror_hitflare_explosion_initialized(unsigned slot,unsigned type){(void)slot;(void)type;}

/* This family is disabled in this isolated regression harness. */
static bool global_pulse_frame,global_pulse_fault,global_pulse_cached;
static Uint8 *global_pulse_owner,*global_pulse_foreign;
static bool global_pulse_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_pulse_palette_matches(void){return true;}
static bool global_pulse_requested(void){return false;}
static bool global_pulse_is_index(unsigned index){return false;}
static bool global_pulse_surface_matches(void){return true;}
static bool global_pulse_final_surface_matches(void){return true;}
static void global_pulse_shutdown(void){}
static void global_pulse_reset(void){}
static void global_pulse_frame_begin(void){}
static bool global_pulse_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_pulse_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_pulse_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_pulse_end(void){}
static bool global_pulse_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_pulse_finish_proof(void){return true;}
static bool global_pulse_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_pulse_check_cache(void){}
static bool global_pulse_fade_buffer_safe(void){return true;}
static bool global_pulse_fade_capture(void){return true;}
static bool global_pulse_fade_step_valid(int steps){return true;}
static void global_pulse_fade_palette(void){}
#define COUNTOF(x) (sizeof(x)/sizeof(*(x)))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
static unsigned checks,cases,asset_opens,asset_allocations,asset_frees;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"CHECK failed %s:%d: %s\n",__FILE__,__LINE__,#x);abort();}} while(0)
static FILE *counted_fopen(const char *p,const char *m){++asset_opens;CHECK(!strcmp(m,"rb"));return fopen(p,m);}
static void *counted_malloc(size_t n){++asset_allocations;return malloc(n);}
static void counted_free(void *p){if(p)++asset_frees;free(p);}
static SDL_Surface *canvas,*output,*game_screen,*VGAScreenSeg,*VGAScreen,*fade_saved;
static Uint32 fade_saved_palette[256];
static bool global_talon_frame;
/* This existing Talon-only observer excludes the independent Shield owner.
 * Enabled cross-family coverage lives in the Shield/native suites. */
static bool global_shield_frame,global_shield_fault,global_talon_shield_dependency;
static Uint8 *global_shield_owner,*global_shield_foreign;
static bool global_shield_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_shield_palette_matches(void){return true;}
static bool global_shield_is_index(unsigned i){(void)i;return false;}
static bool global_shield_surface_matches(void){return true;}
static bool global_shield_final_surface_matches(void){return true;}
static void global_shield_shutdown(void){}
static bool global_shield_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_shield_final_pixel(SDL_Surface *s,Uint8 *p){}
static bool global_shield_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_shield_cached;
static bool global_shield_finish_proof(void){return true;}
static bool global_shield_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_shield_check_cache(void){}
static bool global_shield_fade_buffer_safe(void){return true;}
static bool global_shield_fade_capture(void){return true;}
static bool global_shield_fade_step_valid(int steps){return true;}
static void global_shield_fade_palette(void){}

static Sprite2_array spriteSheet9,explosionSpriteSheet;
static Uint32 rgb_palette[256],normal_palette[256];
static Uint8 expected[64000],selected[64000],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static char global_asset_directory[1024];
static int game_probe_density,mapX2Ofs=30,shadowYDist;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_enabled;
static bool active,suppress,suppress_green_smoke,suppress_cloud,ready,last_output_valid,last_output_scene_hd;
static bool shared_hud_frame,shared_hud_lease,manual_hd_enabled,manual_hd_lease,asteroid_hd_enabled,asteroid_hd_lease;
static bool talon_banking_enabled=true;
static bool twoPlayerMode,galagaMode,twoPlayerLinked,xmas,isNetworkGame,record_demo,play_demo;
static unsigned draws,occlusions,region_count;
static bool have_fade_saved,game_probe_local_blend;
static int fade_mode;
static Uint8 last_output_indices[64000];
static const int original_visual_indices[5]={0,2,6,10,12};
typedef struct {SDL_Rect rect;bool live;} HdRegion;
static HdRegion regions[1];
static void restore_classic_rect(SDL_Rect r){CHECK(false);}
static uint64_t mirror_logic_tick;
static const char *reject_reason;
static struct {int x,y;unsigned invulnerable_ticks;} player[2];
static SDL_Surface *make_surface(int w,int h,int depth)
{
 SDL_Surface *s=calloc(1,sizeof(*s));CHECK(s);s->w=w;s->h=h;s->pitch=w*(depth/8);
 s->pixels=calloc((size_t)s->pitch,h);s->format=calloc(1,sizeof(*s->format));CHECK(s->pixels&&s->format);
 s->format->BitsPerPixel=depth;s->format->BytesPerPixel=depth/8;s->format->format=depth==8?SDL_PIXELFORMAT_INDEX8:SDL_PIXELFORMAT_ARGB8888;
 s->clip_rect=(SDL_Rect){0,0,w,h};return s;
}
static void free_surface(SDL_Surface *s){if(s){free(s->pixels);free(s->format);free(s);}}
static void font_before_effect(SDL_Rect r){(void)r;}
static void render_mirror_unsupported(const char *r){reject_reason=r;}
static void render_mirror_shadow_end(void){}
#include "primitives.inc"

/* All I/O and resource allocations below belong to the included current
 * production global stage, so wrong-source cold tests cannot hide cache warms. */
#define fopen counted_fopen
#define malloc counted_malloc
#define free counted_free
#include "global_talon_mirror.inc"
static void render_mirror_global_reset(void){global_talon_reset();}
#undef fopen
#undef malloc
#undef free
#define data_frame_pixel(...) ((void)0)
#define data_portrait_pixel(...) ((void)0)
#define storm_pixel(...) ((void)0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
#define font_final_pixel(...) ((void)0)
#define common_pause_pixel(...) ((void)0)
#define vulcan_shadow_clear(...) ((void)0)
#define vulcan_shadow_pixel(...) false
#define font_pixel(...) false
#include "pixel.inc"
#include "root.inc"

static unsigned local_blocks,blend_source_index;
static bool game_probe_known_blend;
#define asteroid1_sprite2_blend_pixel(...) CHECK(false)
#define have_supported_talon() false
#define recognized_value_effect(...) false
#define effect_ramp_monotone_to(...) false
#define recognized_contact_effect(...) false
#define effect_ramp_monotone(...) false
#define game_probe_blend_write(...) ((void)0)
static Uint32 explosion_blend_rgba(Uint32 v,Uint8 s){CHECK(false);return v;}
#include "blend.inc"
#define asset_debug_effect(...) ((void)0)
#define SDL_SwapLE16(v) (v)
#include "blitter.inc"

static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static void load_original(void)
{
 Uint32 n;read_exact(&n,sizeof(n));CHECK(n==33484);spriteSheet9.size=n;
 spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 read_exact(normal_palette,sizeof(normal_palette));CHECK(fgetc(stdin)==EOF);
}
/* Independent cursor decoder records raw offsets for source-mutation checks.
 * It does not use production's x/y parser, generated hashes, or cached state. */
static bool reference_decode(Sprite2_array bank,unsigned index,Uint8 color[168],Uint8 mask[168],size_t raw[168])
{
 memset(color,0,168);memset(mask,0,168);if(raw)memset(raw,0,168*sizeof(*raw));
 if(!bank.data||!index||(size_t)index*2>bank.size)return false;
 size_t pos=bank.data[2*(index-1)]+256u*bank.data[2*(index-1)+1];unsigned cell=0;
 for(size_t step=0;step<bank.size;step++) {
  if(pos>=bank.size)return false;unsigned code=bank.data[pos++];if(code==15)return true;
  cell+=code&15;for(unsigned n=code>>4;n;n--){if(pos>=bank.size||cell>=168)return false;color[cell]=bank.data[pos];mask[cell]=255;if(raw)raw[cell]=pos;++cell;++pos;}
 }
 return false;
}
static Uint32 reference_blend(Uint32 prior,const Uint8 *rgba,unsigned alpha)
{
 unsigned r=((prior>>16)&255)*(255-alpha)+rgba[0]*alpha;
 unsigned g=((prior>>8)&255)*(255-alpha)+rgba[1]*alpha;
 unsigned b=(prior&255)*(255-alpha)+rgba[2]*alpha;
 return UINT32_C(0xff000000)|((r+127)/255<<16)|((g+127)/255<<8)|(b+127)/255;
}
static Uint32 reference_darken(Uint32 prior,unsigned alpha)
{
 unsigned r=((prior>>16)&255)*(510-alpha),g=((prior>>8)&255)*(510-alpha),b=(prior&255)*(510-alpha);
 return UINT32_C(0xff000000)|((r+255)/510<<16)|((g+255)/510<<8)|(b+255)/510;
}
static Uint32 *rgba_at(int x,int y){return (Uint32 *)((Uint8 *)canvas->pixels+(size_t)y*canvas->pitch)+x;}
static Uint8 *index_at(int x,int y){return (Uint8 *)game_screen->pixels+(size_t)y*game_screen->pitch+x;}
static unsigned first_cell(const Uint8 mask[168]){for(unsigned i=0;i<168;i++)if(mask[i])return i;CHECK(false);return 0;}
static void set_background(void)
{
 memcpy(rgb_palette,normal_palette,sizeof(rgb_palette));
 memset(game_screen->pixels,0x1b,64000);memset(VGAScreenSeg->pixels,0x1b,64000);memset(expected,0x1b,64000);
 memset(selected,0,sizeof(selected));memset(hd_owner,0,(size_t)canvas->w*canvas->h);memset(cloud_owner,0,(size_t)canvas->w*canvas->h);
 memset(green_first,0,(size_t)canvas->w*canvas->h*sizeof(*green_first));
 upscale(canvas,game_screen);upscale(output,VGAScreenSeg);
 active=true;suppress=suppress_green_smoke=suppress_cloud=false;reject_reason=NULL;draws=occlusions=0;
}
/* Tests below use real included functions, not substitute admission or drawing.
 * Their API-specific section is maintained with the reconstruction owner. */
static Uint8 *reference_frames[13];
static Uint32 *saved_canvas;
static Uint8 *saved_owners;
static void load_reference_frames(const char *root)
{
 for(unsigned i=0;i<13;i++) {
  const GlobalAssetResource *record=NULL;
  for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_talon_resource_ids[i])record=global_asset_resources+j;
  CHECK(record);char path[2048];CHECK(snprintf(path,sizeof(path),"%s/%s",root,record->path)>0);
  FILE *file=fopen(path,"rb");CHECK(file);Uint8 header[28];CHECK(fread(header,1,28,file)==28);CHECK(!memcmp(header,"HDR1",4));
  reference_frames[i]=malloc(192u*224u*4u);CHECK(reference_frames[i]);CHECK(fread(reference_frames[i],1,192u*224u*4u,file)==192u*224u*4u);CHECK(fgetc(file)==EOF);CHECK(!fclose(file));
 }
}
static void snapshot_canvas(void)
{
 size_t bytes=(size_t)canvas->w*canvas->h*4;free(saved_canvas);saved_canvas=malloc(bytes);CHECK(saved_canvas);
 free(saved_owners);saved_owners=malloc(bytes/4);CHECK(saved_owners);memcpy(saved_owners,hd_owner,bytes/4);
 for(int y=0;y<canvas->h;y++)memcpy(saved_canvas+(size_t)y*canvas->w,(Uint8 *)canvas->pixels+(size_t)y*canvas->pitch,(size_t)canvas->w*4);
}
static void patterned_canvas(void)
{
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++)
  *rgba_at(x,y)=UINT32_C(0xff000000)|((unsigned)(x*137+y*937+0x13579b)&0xffffffu);
}
static void check_reference_draw(unsigned visual,int ox,int oy,int style)
{
 int d=game_probe_density;CHECK(visual<13);
 unsigned opaque=0,transparent=0,partial=0;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  Uint32 want=saved_canvas[(size_t)y*canvas->w+x];int rx=x-ox*d,ry=y-oy*d;
  if(rx>=0&&ry>=0&&rx<24*d&&ry<28*d) {
   const Uint8 *a=reference_frames[visual]+4u*((size_t)(ry*8/d)*192+rx*8/d);
   if(!a[3])++transparent;
   else {if(a[3]==255)++opaque;else ++partial;
    if(style==MIRROR_SHADOW) {
     if(saved_owners[(size_t)y*canvas->w+x])want=reference_darken(want,a[3]);
     else {Uint8 index=*index_at(x/d,y/d);Uint32 color=palette_rgb((index&240)|((index&15)/2));Uint8 dark[4]={color>>16,color>>8,color,255};want=reference_blend(want,dark,a[3]);}
    }
    else want=reference_blend(want,a,style==MIRROR_BLEND?(a[3]+1u)/2u:a[3]);
   }
  }
  CHECK(*rgba_at(x,y)==want);
 }
 CHECK(opaque&&transparent&&!partial);
}
static void check_source_decoder(void)
{
 ++cases;
 for(unsigned index=229;index<=257;index++) {
  if(index>238&&index<248)continue;
  Uint8 ref[168],mask[168],actual[336]={0};CHECK(reference_decode(spriteSheet9,index,ref,mask,NULL));
  CHECK(decode_tile(spriteSheet9,index,actual,actual+168,12,0,0));CHECK(!memcmp(ref,actual,168));CHECK(!memcmp(mask,actual+168,168));
 }
}
static Uint8 *source_backup;
static void restore_original_source(void)
{
 CHECK(source_backup&&spriteSheet9.size==33484);memcpy(spriteSheet9.data,source_backup,spriteSheet9.size);
}
static void initialize_surfaces(int density)
{
 free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 game_probe_density=density;canvas=make_surface(320*density,200*density,32);output=make_surface(320*density,200*density,32);
 game_screen=make_surface(320,200,8);VGAScreenSeg=make_surface(320,200,8);VGAScreen=game_screen;
 size_t count=(size_t)canvas->w*canvas->h;hd_owner=calloc(count,1);cloud_owner=calloc(count,1);green_first=calloc(count,sizeof(*green_first));
 green_under=calloc(count,sizeof(*green_under));green_under_owner=calloc(count,1);CHECK(hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);
 set_background();
}
static const char *valid_root,*fixture_root;
static void setup(const char *root,int density)
{
 ++cases;global_talon_shutdown();free_surface(fade_saved);fade_saved=NULL;initialize_surfaces(density);restore_original_source();
 game_probe_missing=game_probe_invalid=game_probe_original_reference=game_probe_enabled=false;
 shared_hud_frame=shared_hud_lease=manual_hd_enabled=manual_hd_lease=asteroid_hd_enabled=asteroid_hd_lease=false;
 twoPlayerMode=galagaMode=twoPlayerLinked=xmas=isNetworkGame=record_demo=play_demo=false;
 talon_banking_enabled=true;mirror_logic_tick=1;have_fade_saved=last_output_valid=ready=false;fade_mode=0;
 player[0].x=100;player[0].y=80;player[1].x=180;player[1].y=100;
 CHECK(render_mirror_set_global_assets(root));global_talon_frame_begin();asset_opens=asset_allocations=asset_frees=0;
}
static void pose(unsigned pnum,int index,unsigned invulnerable)
{global_talon_pose(pnum,spriteSheet9,233,index,invulnerable);}
static int draw_at(int x,int y,unsigned index,int style,unsigned pnum)
{return render_mirror_global_player_ship(game_screen,x,y,spriteSheet9,index,style,pnum,233);}
/* Simulate exactly one original indexed quad in native quadrant order. This is
 * an independent source walker, not a claim that the real native caller ran.
 * The pixel observer itself is the extracted current production callback. */
static unsigned original_quad(int x,int y,unsigned index,int style)
{
 unsigned calls=0;const unsigned parts[4]={0,1,19,20};
 if(style==MIRROR_BLEND) {
  Uint8 reference[64000];memcpy(reference,game_screen->pixels,sizeof(reference));
  for(unsigned q=0;q<4;q++) {Uint8 c[168],m[168];CHECK(reference_decode(spriteSheet9,index+parts[q],c,m,NULL));
   int ox=x+(q&1)*12,oy=y+(q>>1)*14;
   for(unsigned i=0;i<168;i++)if(m[i]){int px=ox+(int)(i%12),py=oy+(int)(i/12);if(py<0||py>=200)continue;CHECK(px>=0&&px<320);unsigned at=py*320+px;reference[at]=(c[i]&240)|(((c[i]&15)+(reference[at]&15))/2);++calls;}
   blit_sprite2_blend(game_screen,ox,oy,spriteSheet9,index+parts[q]);
  }
  CHECK(!memcmp(reference,game_screen->pixels,64000));CHECK(!memcmp(reference,expected,64000));return calls;
 }
 for(unsigned q=0;q<4;q++) {
  Uint8 c[168],m[168];CHECK(reference_decode(spriteSheet9,index+parts[q],c,m,NULL));
  int ox=x+(q&1)*12,oy=y+(q>>1)*14;
  for(unsigned i=0;i<168;i++)if(m[i]) {
   int px=ox+(int)(i%12),py=oy+(int)(i/12);if(py<0||py>=200)continue;
   CHECK(px>=0&&px<320);Uint8 *out=index_at(px,py),before=*out;
   *out=style==MIRROR_NORMAL?c[i]:style==MIRROR_BLEND?(Uint8)((c[i]&240)|(((c[i]&15)+(before&15))/2)):(Uint8)((before&240)|((before&15)/2));
   render_mirror_pixel(game_screen,out,c[i],style);CHECK(expected[py*320+px]==*out);++calls;
  }
 }
 return calls;
}
static void finish_draw(int x,int y,unsigned index,int style)
{CHECK(original_quad(x,y,index,style)>0);global_talon_end();CHECK(!global_talon_fault);}
static void cold_guards(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned which=0;which<30;which++) {
  setup(valid_root,8);
  if(warm){pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);CHECK(asset_opens==13);}
  unsigned opens=asset_opens;pose(1,233,which==6?10:0);CHECK(asset_opens==opens);
  SDL_Surface *surface=game_screen;Sprite2_array bank=spriteSheet9;
  unsigned pnum=1,index=233;int style=MIRROR_NORMAL,base=233,x=95,y=73,want=0;
  Uint8 *clone=NULL;Uint8 saved=0;size_t changed=0,old_size=spriteSheet9.size;
  switch(which) {
   case 0:pnum=0;break;case 1:pnum=3;break;case 2:pnum=2;break;
   case 3:style=-1;break;case 4:style=3;break;case 5:style=MIRROR_BLEND;break;
   case 6:break;case 7:surface=VGAScreenSeg;break;
   case 8:clone=malloc(bank.size);CHECK(clone);memcpy(clone,bank.data,bank.size);bank.data=clone;break;
   case 9:--bank.size;break;case 10:index=234;break;case 11:index=239;break;
   case 12:base=234;want=-1;break;case 13:rgb_palette[16]^=1;break;
   case 14:game_probe_original_reference=true;break;case 15:game_probe_missing=true;break;case 16:game_probe_invalid=true;break;
   case 17:game_probe_density=2;break;case 18:++mirror_logic_tick;break;
   case 19:CHECK(render_mirror_set_global_assets(NULL));want=-1;break;
   case 20:x=-1;break;case 21:x=297;break;case 22:y=-28;break;case 23:y=200;break;
   case 24:{Uint8 c[168],m[168];size_t raw[168];CHECK(reference_decode(bank,229,c,m,raw));changed=raw[first_cell(m)];saved=bank.data[changed];bank.data[changed]^=1;break;}
   case 25:--spriteSheet9.size;break;case 26:bank.data=NULL;break;
   case 27:game_screen->format->BitsPerPixel=32;break;
   case 28:render_mirror_global_reset();break;
   case 29:clone=malloc(bank.size);CHECK(clone);memcpy(clone,bank.data,bank.size);spriteSheet9.data=clone;break;
  }
  snapshot_canvas();CHECK(render_mirror_global_player_ship(surface,x,y,bank,index,style,pnum,base)==want);CHECK(asset_opens==opens);
  CHECK(!memcmp(saved_canvas,canvas->pixels,(size_t)canvas->w*canvas->h*4));
  if(which==24)bank.data[changed]=saved;if(which==29)spriteSheet9.data=bank.data;spriteSheet9.size=old_size;free(clone);
 }
}
static void resource_failures(void)
{
 const char *modes[]={"missing","corrupt","header","trailing"};
 for(unsigned mode=0;mode<COUNTOF(modes);mode++)for(unsigned visual=0;visual<13;visual++) {
  char path[2048];CHECK(snprintf(path,sizeof(path),"%s/%s%u",fixture_root,modes[mode],visual)>0);setup(path,8);pose(1,233,0);
  snapshot_canvas();CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);CHECK(asset_opens==13);CHECK(!global_talon_good);
  CHECK(!memcmp(saved_canvas,canvas->pixels,(size_t)canvas->w*canvas->h*4));
  for(unsigned j=0;j<13;j++)CHECK(!global_talon_rgba[j]);
  CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);CHECK(asset_opens==13);
  CHECK(render_mirror_set_global_assets(valid_root));global_talon_frame_begin();pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);
 }
 char path[2048];CHECK(snprintf(path,sizeof(path),"%s/talon-only",fixture_root)>0);setup(path,8);pose(1,233,0);
 CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);CHECK(asset_opens==13);
 /* All non-Talon resources are absent, yet Talon remains independently usable. */
}
static void select_visual(unsigned visual,unsigned invulnerable)
{
 unsigned target=visual<6?229:237;pose(1,(int)target,invulnerable);CHECK(global_talon_poses[0].visual==6);
 for(unsigned step=0;step<(visual<6?6-visual:visual-6);step++){++mirror_logic_tick;global_talon_frame_begin();pose(1,(int)target,invulnerable);}
 CHECK(global_talon_poses[0].visual==(int)visual);CHECK(!asset_opens);
}
static void mixed_background(void)
{
 int d=game_probe_density;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;hd_owner[n]=(x+3*y)%3==1;
  *rgba_at(x,y)=hd_owner[n]?(UINT32_C(0xff000000)|((unsigned)(x*137+y*937+0x13579b)&0xffffffu)):palette_rgb(*index_at(x/d,y/d));
 }
}
static unsigned owned_cell(void)
{
 int d=game_probe_density;
 for(unsigned y=73;y<101;y++)for(unsigned x=95;x<119;x++)if(global_talon_owner[(size_t)(y*d)*canvas->w+x*d])return y*320+x;
 CHECK(false);return 0;
}
static void alpha_and_writes(void)
{
 for(int d=4;d<=8;d+=4)for(unsigned visual=0;visual<13;visual++)for(int style=MIRROR_NORMAL;style<=MIRROR_SHADOW;style++) {
  setup(valid_root,d);select_visual(visual,style==MIRROR_BLEND?10:0);mixed_background();snapshot_canvas();
  unsigned index=visual<6?229:237;CHECK(draw_at(95,73,index,style,1)==1);CHECK(asset_opens==13);check_reference_draw(visual,95,73,style);
  finish_draw(95,73,index,style);CHECK(!reject_reason);
  unsigned cell=owned_cell(),x=cell%320,y=cell/320;Uint8 *at=index_at(x,y),before=*at;
  render_mirror_pixel(game_screen,at,*at,MIRROR_NORMAL);CHECK(*at==before&&expected[cell]==before);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;CHECK(!global_talon_owner[n]);CHECK(!hd_owner[n]);CHECK(*rgba_at(x*d+sx,y*d+sy)==palette_rgb(before));}
  CHECK(!global_talon_fault);
 }
 /* Successive authored operators see the already-composed RGB, not a replay of
  * a prior index image. Native writes after each accepted operator occur once. */
 for(int d=4;d<=8;d+=4) {
  setup(valid_root,d);pose(1,233,0);mixed_background();
  const int sequence[]={MIRROR_SHADOW,MIRROR_SHADOW,MIRROR_NORMAL,MIRROR_SHADOW};
  for(unsigned i=0;i<COUNTOF(sequence);i++) {snapshot_canvas();CHECK(draw_at(95,73,233,sequence[i],1)==1);check_reference_draw(6,95,73,sequence[i]);finish_draw(95,73,233,sequence[i]);}
 }
}
static void source_and_lifecycle(void)
{
 setup(valid_root,8);pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);
 unsigned tested=0;
 for(unsigned t=0;t<COUNTOF(global_talon_source);t++) {
  Uint8 c[168],m[168];size_t raw[168];CHECK(reference_decode(spriteSheet9,global_talon_source[t].index,c,m,raw));
  for(unsigned cell=0;cell<168;cell++)if(m[cell]) {
   Uint8 prior=spriteSheet9.data[raw[cell]];spriteSheet9.data[raw[cell]]^=1;
   CHECK(!global_talon_source_matches(spriteSheet9));CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);CHECK(asset_opens==13);
   spriteSheet9.data[raw[cell]]=prior;CHECK(global_talon_source_matches(spriteSheet9));++tested;
  }
  unsigned start=spriteSheet9.data[2*(global_talon_source[t].index-1)]+256u*spriteSheet9.data[2*(global_talon_source[t].index-1)+1];
  Uint8 saved=spriteSheet9.data[start];spriteSheet9.data[start]=15;CHECK(!global_talon_source_matches(spriteSheet9));CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);spriteSheet9.data[start]=saved;
 }
 CHECK(tested>1000);
 /* Unrelated palette entries cannot gate Talon. Relevant entries are checked
  * every call, including after the family has been loaded successfully. */
 for(unsigned index=0;index<256;index++) {
  rgb_palette[index]^=1;CHECK(global_talon_palette_matches()==(index<16||index>31));
  if(index>=16&&index<=31)CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);
  rgb_palette[index]^=1;
 }
 CHECK(asset_opens==13);
 Uint8 *old=spriteSheet9.data,*replacement=malloc(spriteSheet9.size);CHECK(replacement);memcpy(replacement,old,spriteSheet9.size);
 Sprite2_array stale=spriteSheet9;spriteSheet9.data=replacement;CHECK(!global_talon_source_matches(stale));CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);
 render_mirror_global_reset();CHECK(!global_talon_frame&&!global_talon_cached);CHECK(!global_talon_poses[0].valid);CHECK(!memchr(global_talon_owner,1,global_talon_capacity));
 global_talon_frame_begin();pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);
 spriteSheet9.data=old;free(replacement);render_mirror_global_reset();
 CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);global_talon_frame_begin();pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);
 unsigned loaded=asset_opens;CHECK(render_mirror_set_global_assets(valid_root));CHECK(asset_opens==loaded);
 char too_long[1025];memset(too_long,'x',sizeof(too_long)-1);too_long[sizeof(too_long)-1]=0;
 CHECK(!render_mirror_set_global_assets(too_long));CHECK(!global_asset_directory[0]);CHECK(!global_talon_loaded);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==-1);
}
static void pose_lifecycle(void)
{
 setup(valid_root,4);pose(1,229,0);CHECK(global_talon_poses[0].visual==6);pose(1,229,0);CHECK(global_talon_poses[0].visual==6);
 for(int want=5;want>=0;want--){++mirror_logic_tick;global_talon_frame_begin();pose(1,229,0);CHECK(global_talon_poses[0].visual==want);pose(1,229,0);CHECK(global_talon_poses[0].visual==want);}
 ++mirror_logic_tick;global_talon_frame_begin();pose(1,237,0);CHECK(global_talon_poses[0].visual==1);
 pose(2,237,0);CHECK(global_talon_poses[1].visual==6);CHECK(global_talon_poses[0].visual==1);
 ++mirror_logic_tick;global_talon_frame_begin();pose(1,237,10);CHECK(global_talon_poses[0].visual==6);pose(2,237,0);CHECK(global_talon_poses[1].visual==7);
 mirror_logic_tick+=2;global_talon_frame_begin();pose(1,229,9);CHECK(global_talon_poses[0].visual==6);
 talon_banking_enabled=false;for(unsigned p=0;p<5;p++){pose(1,229+2*p,0);CHECK(global_talon_poses[0].visual==original_visual_indices[p]);}
 CHECK(!asset_opens);
}
static void map_final_indices(void)
{
 for(unsigned y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,(Uint8 *)game_screen->pixels+y*320+24,264);
 upscale(output,VGAScreenSeg);
}
static void check_output_mapping(bool accepted)
{
 int d=game_probe_density;unsigned retained=0;
 for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
  Uint32 want=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*VGAScreenSeg->pitch+x/d]);
  if(accepted&&x<264*d&&y<184*d) {
   size_t n=(size_t)y*canvas->w+x+24*d;
   if(global_talon_owner[n]){want=*rgba_at(x+24*d,y);++retained;}
  }
  CHECK(((Uint32 *)((Uint8 *)output->pixels+y*output->pitch))[x]==want);
 }
 if(accepted)CHECK(retained>0);
}
static void prepare_composition(int d,int style,bool mixed)
{
 setup(valid_root,d);active=false;pose(1,233,style==MIRROR_BLEND?10:0);if(mixed)mixed_background();
 CHECK(draw_at(95,73,233,style,1)==1);finish_draw(95,73,233,style);map_final_indices();
}
static void output_and_final_writes(void)
{
 for(int d=4;d<=8;d+=4)for(unsigned kind=0;kind<4;kind++) {
  prepare_composition(d,MIRROR_NORMAL,false);bool accepted=kind==MIRROR_OUTPUT_ORDINARY||kind==MIRROR_OUTPUT_NORMAL15_LOW_DETAIL;
  CHECK(global_talon_compose((MirrorOutputKind)kind,0,0)==accepted);CHECK(global_talon_cached==accepted);check_output_mapping(accepted);
 }
 for(int d=4;d<=8;d+=4)for(unsigned when=0;when<2;when++) {
  prepare_composition(d,MIRROR_NORMAL,false);unsigned cell=owned_cell(),sx=cell%320,y=cell/320,x=sx-24;
  if(when){CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));memcpy(last_output_indices,VGAScreenSeg->pixels,64000);}
  Uint8 *at=(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch+x,before=*at;
  render_mirror_pixel(VGAScreenSeg,at,*at,MIRROR_NORMAL);CHECK(*at==before);
  for(int yy=0;yy<d;yy++)for(int xx=0;xx<d;xx++){size_t n=(size_t)(y*d+yy)*canvas->w+sx*d+xx;CHECK(!global_talon_owner[n]);CHECK(!hd_owner[n]);CHECK(*rgba_at(sx*d+xx,y*d+yy)==palette_rgb(before));}
  if(!when)CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));check_output_mapping(true);
  SDL_Rect rect={71,73,24,28};global_talon_final_rect(VGAScreenSeg,&rect);
  CHECK(!memchr(global_talon_owner,1,global_talon_capacity));check_output_mapping(false);
 }
 /* A final indexed mismatch revokes its exact cell, even if bytes happen to
  * match elsewhere. An uncovered source write rejects the full family. */
 prepare_composition(8,MIRROR_NORMAL,false);unsigned cell=owned_cell(),x=cell%320,y=cell/320;
 ((Uint8 *)VGAScreenSeg->pixels)[y*320+x-24]^=1;upscale(output,VGAScreenSeg);CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));
 for(int yy=0;yy<8;yy++)for(int xx=0;xx<8;xx++)CHECK(!global_talon_owner[(size_t)(y*8+yy)*canvas->w+x*8+xx]);check_output_mapping(true);
 prepare_composition(8,MIRROR_NORMAL,false);((Uint8 *)game_screen->pixels)[0]^=1;CHECK(!global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));check_output_mapping(false);
 prepare_composition(8,MIRROR_NORMAL,false);game_probe_original_reference=true;CHECK(!global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));check_output_mapping(false);
 /* Unrelated scene rejection must not destroy opaque Talon output, while an
  * invulnerability blend over foreign HD cannot survive that rejection. */
 for(int style=MIRROR_NORMAL;style<=MIRROR_BLEND;style++) {
  prepare_composition(8,style,true);reject_reason="unrelated-family-rejected";CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));check_output_mapping(true);
  unsigned foreign_left=0;for(size_t i=0;i<global_talon_capacity;i++)if(global_talon_owner[i]&&global_talon_foreign[i])++foreign_left;CHECK(!foreign_left);
 }
}
/* Independent descending-counter native cone, without calling production
 * normal15 helpers. Authored RGB residuals are compared after exactly one
 * palette-anchored attenuation; original INDEX8 memory remains unchanged. */
static int reference_night_branch(int u,int v,int lx,int ly)
{
 int64_t row=184-(int64_t)v,dist=(int64_t)lx-(264-(int64_t)u);
 if(ly>row)return 6;if(dist<0)dist=-dist;dist+=(int64_t)ly-row;
 return dist<0?-1:dist<=5?(int)dist:6;
}
static Uint8 reference_night_index(Uint8 v,int branch)
{return branch<0?v:(Uint8)((v&240)|(branch==6?(v&15)/4:((v&15)+15-3*branch)/4));}
static Uint32 reference_night_rgb(Uint32 color,Uint8 before,Uint8 after,int branch)
{
 if(branch<0)return color;Uint32 result=0xff000000u;
 for(unsigned shift=0;shift<24;shift+=8){unsigned h=(color>>shift)&255,b=(normal_palette[before]>>shift)&255,a=(normal_palette[after]>>shift)&255,value=a;
  if(h<b){unsigned delta=b-h;value-=4*a<b?(delta*a+b/2)/b:(delta+2)/4;}
  if(h>b){unsigned delta=h-b;value+=4*(255-a)<255-b?(delta*(255-a)+(255-b)/2)/(255-b):(delta+2)/4;}
  result|=value<<shift;
 }return result;
}
static void map_night_indices(int lx,int ly)
{
 for(int y=0;y<184;y++)for(int x=0;x<264;x++)((Uint8 *)VGAScreenSeg->pixels)[y*320+x]=reference_night_index(*index_at(x+24,y),reference_night_branch(x,y,lx,ly));
 upscale(output,VGAScreenSeg);
}
static void night_mapping(void)
{
 static const int lights[][2]={{181,100},{181,110},{181,0},{0,184},{INT_MIN,INT_MAX},{INT_MAX,INT_MIN}};
 for(int d=4;d<=8;d+=4)for(unsigned light=0;light<COUNTOF(lights);light++)for(int style=MIRROR_NORMAL;style<=MIRROR_SHADOW;style++) {
  prepare_composition(d,style,false);int lx=lights[light][0],ly=lights[light][1];map_night_indices(lx,ly);snapshot_canvas();
  CHECK(global_talon_compose(MIRROR_OUTPUT_NORMAL15_NIGHT,lx,ly));CHECK(global_talon_cached);
  CHECK(!memcmp(saved_canvas,canvas->pixels,(size_t)canvas->w*canvas->h*4));
  unsigned retained=0;
  for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
   Uint8 after=((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d];Uint32 want=palette_rgb(after);
   if(x<264*d&&y<184*d){size_t n=(size_t)y*canvas->w+x+24*d;if(global_talon_owner[n]){want=reference_night_rgb(*rgba_at(x+24*d,y),*index_at(x/d+24,y/d),after,reference_night_branch(x/d,y/d,lx,ly));++retained;}}
   CHECK(((Uint32 *)output->pixels)[(size_t)y*output->w+x]==want);
  }
  CHECK(retained);memcpy(last_output_indices,VGAScreenSeg->pixels,64000);global_talon_check_cache();CHECK(global_talon_cached);
 }
 for(unsigned bad=0;bad<5;bad++){
  prepare_composition(4,MIRROR_NORMAL,false);map_night_indices(181,100);
  if(bad==0)((Uint8 *)VGAScreenSeg->pixels)[0]^=1;
  if(bad==1)rgb_palette[255]^=1;
  if(bad==2)VGAScreenSeg->pitch=321;
  CHECK(!global_talon_compose(bad==4?MIRROR_OUTPUT_UNSUPPORTED:MIRROR_OUTPUT_NORMAL15_NIGHT,bad==3?0:181,100));CHECK(!global_talon_cached);
  VGAScreenSeg->pitch=320;
 }
 /* Every indexed ramp level and all eight cone branches. */
 for(unsigned v=0;v<256;v++)for(int branch=-1;branch<=6;branch++){
  int lx=264,ly=branch<0?100:184+branch;
  if(branch>=0&&branch<=5){lx=264+branch;ly=184;}
  CHECK(normal15_index(v,0,0,lx,ly)==reference_night_index(v,branch));
 }
}

static void cache_and_layout(void)
{
 for(unsigned which=0;which<10;which++) {
  prepare_composition(4,MIRROR_NORMAL,false);SDL_Surface saved_output=*output,saved_canvas_surface=*canvas,saved_final=*VGAScreenSeg,saved_source=*game_screen;
  SDL_PixelFormat out_format=*output->format,source_format=*game_screen->format,final_format=*VGAScreenSeg->format;
  void *replacement=NULL;
  switch(which){
   case 0:output->pitch--;break;case 1:output->w--;break;case 2:output->format->BitsPerPixel=8;break;
   case 3:output->pixels=NULL;break;case 4:canvas->pixels=NULL;break;case 5:VGAScreenSeg->pitch=319;break;
   case 6:game_screen->format->BitsPerPixel=32;break;case 7:replacement=malloc(64000);CHECK(replacement);memcpy(replacement,VGAScreenSeg->pixels,64000);VGAScreenSeg->pixels=replacement;break;
   case 8:VGAScreenSeg->format->BytesPerPixel=4;break;case 9:game_screen->pitch=319;break;
  }
  CHECK(!global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(!global_talon_cached);
  *output=saved_output;*canvas=saved_canvas_surface;*VGAScreenSeg=saved_final;*game_screen=saved_source;*output->format=out_format;*game_screen->format=source_format;*VGAScreenSeg->format=final_format;free(replacement);
 }
 for(unsigned which=0;which<6;which++) {
  prepare_composition(4,MIRROR_NORMAL,false);CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));memcpy(last_output_indices,VGAScreenSeg->pixels,64000);
  ready=last_output_valid=have_fade_saved=true;fade_mode=1;global_talon_check_cache();CHECK(global_talon_cached&&ready&&last_output_valid);
  Uint8 saved=0;size_t at=0;
  switch(which){
   case 0:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;
   case 1:rgb_palette[7]^=1;break;
   case 2:{Uint8 c[168],m[168];size_t raw[168];CHECK(reference_decode(spriteSheet9,229,c,m,raw));at=raw[first_cell(m)];saved=spriteSheet9.data[at];spriteSheet9.data[at]^=1;break;}
   case 3:game_probe_original_reference=true;break;
   case 4:global_talon_source_lease.pixels=NULL;break;
   case 5:render_mirror_global_reset();break;
  }
  global_talon_check_cache();CHECK(!global_talon_cached&&!ready&&!last_output_valid&&!have_fade_saved&&!fade_mode);if(which==2)spriteSheet9.data[at]=saved;
 }
}
static void underlay_palette(void)
{
 for(int style=MIRROR_NORMAL;style<=MIRROR_SHADOW;style++)for(unsigned change=0;change<3;change++) {
  setup(valid_root,4);memset(game_screen->pixels,0x6b,64000);memset(expected,0x6b,64000);upscale(canvas,game_screen);
  pose(1,233,style==MIRROR_BLEND?10:0);CHECK(draw_at(95,73,233,style,1)==1);finish_draw(95,73,233,style);map_final_indices();
  unsigned color=change==0?0x6b:change==1?0x65:0x01;bool invalid=change==0||(change==1&&style==MIRROR_SHADOW);
  rgb_palette[color]^=1;upscale(output,VGAScreenSeg);CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0)==!invalid);check_output_mapping(!invalid);
 }
 /* A palette change before drawing refreshes a classic-owned underlay. */
 setup(valid_root,4);memset(game_screen->pixels,0x6b,64000);memset(expected,0x6b,64000);upscale(canvas,game_screen);rgb_palette[0x6b]^=0x010101;
 pose(1,233,10);CHECK(draw_at(95,73,233,MIRROR_BLEND,1)==1);finish_draw(95,73,233,MIRROR_BLEND);map_final_indices();CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));check_output_mapping(true);
}
static void transaction_faults(void)
{
 for(unsigned which=0;which<6;which++) {
  setup(valid_root,4);pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);
  Uint8 c[168],m[168];CHECK(reference_decode(spriteSheet9,233,c,m,NULL));unsigned cell=first_cell(m),x=95+cell%12,y=73+cell/12;
  Uint8 *at=index_at(x,y);
  switch(which) {
   case 0:global_talon_end();break;
   case 1:*at=c[cell];render_mirror_pixel(game_screen,at,c[cell],MIRROR_NORMAL);render_mirror_pixel(game_screen,at,c[cell],MIRROR_NORMAL);break;
   case 2:*at=c[cell]^1;render_mirror_pixel(game_screen,at,c[cell],MIRROR_NORMAL);break;
   case 3:*at=c[cell];render_mirror_pixel(game_screen,at,c[cell],MIRROR_BLEND);break;
   case 4:CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);break;
   case 5:render_mirror_pixel(game_screen,index_at(0,0),*index_at(0,0),MIRROR_NORMAL);break;
  }
  CHECK(global_talon_fault);CHECK(!global_talon_call.live);CHECK(!memchr(global_talon_owner,1,global_talon_capacity));
  map_final_indices();CHECK(!global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));check_output_mapping(false);
 }
 for(unsigned pixel=0;pixel<2;pixel++) {
  prepare_composition(4,MIRROR_NORMAL,false);snapshot_canvas();game_probe_density=8;
  if(pixel){render_mirror_pixel(game_screen,index_at(100,80),*index_at(100,80),MIRROR_NORMAL);CHECK(reject_reason&&global_talon_fault);}
  CHECK(!global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(!memcmp(saved_canvas,canvas->pixels,(size_t)canvas->w*canvas->h*4));game_probe_density=4;
 }
}
/* Exact production finish body, but unrelated family hooks are inert. The
 * sentinel upscale is intentionally fatal: invalid layout must return before
 * the real upscaler could touch an invalid destination. This proves only the
 * current finish early-return guard, not an integrated rendering session. */
static int lvlFileNum=2;static char terrain_file='a';
static bool font_history,game_probe_coverage_fault;static unsigned char *font_owner;
static struct {bool canvas_live,output_live;} font_scenes[2];
static Uint32 initial_palette[256],last_output_palette[256],hud_output_palette[256],component_output_palette[256],indicator_output_palette[256],fixed_text_output_palette[256];
static Uint8 restored_mask[64000];
static unsigned mismatch,boundary_crossings,restored_checks,restored_mismatches,brightness_blocks,expanded_regions,game_probe_tick,local_entities,local_regions;
static char all_rejections[512];
#define mirror_enabled() false
#define render_mirror_hud_reset() CHECK(false)
#define hud_check_mode() ((void)0)
#define shared_hud_finish(...) CHECK(false)
#define normal15_layout() false
#define normal15_scope() false
#define normal15_compose(...) CHECK(false)
#define font_prepare_finish() ((void)0)
#define font_scene_owned(...) false
#define font_validate_shared_scene(...) ((void)0)
#define font_restore_shared_rejected() ((void)0)
#define shared_hud_requested() false
#define font_compose_shared_scene(...) false
#define hud_compose() false
#define components_compose() false
#define indicators_compose() false
#define fixed_text_compose() false
#define font_finish(...) false
#define game_probe_rgb_audit(...) ((void)0)
#define game_probe_effects(...) ((void)0)
#define ground101_frame_report(...) ((void)0)
#define game_probe_frame(...) ((void)0)
#define game_probe_capture_tick() false
#define game_probe_export(...) CHECK(false)
static bool finish_allow_upscale;
static void forbidden_upscale(SDL_Surface *out,SDL_Surface *in){CHECK(finish_allow_upscale);upscale(out,in);}
#define upscale forbidden_upscale
#include "finish.inc"
#undef upscale
static void finish_layout_guard(void)
{
 finish_allow_upscale=false;
 for(unsigned which=0;which<9;which++) {
  prepare_composition(4,MIRROR_NORMAL,false);active=true;ready=last_output_valid=have_fade_saved=true;
  SDL_Surface saved=*output,final_saved=*VGAScreenSeg;SDL_PixelFormat format=*output->format,final_format=*VGAScreenSeg->format;void *replacement=NULL;
  switch(which){case 0:game_probe_density=8;break;case 1:output->pixels=NULL;break;case 2:output->pitch=1;break;case 3:output->format->BitsPerPixel=8;break;case 4:output->w=1;break;case 5:VGAScreenSeg->pixels=NULL;break;case 6:VGAScreenSeg->pitch=319;break;case 7:VGAScreenSeg->format->BytesPerPixel=4;break;case 8:replacement=malloc(64000);CHECK(replacement);memcpy(replacement,VGAScreenSeg->pixels,64000);VGAScreenSeg->pixels=replacement;break;}
  render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid&&!have_fade_saved);
  game_probe_density=4;*output=saved;*output->format=format;*VGAScreenSeg=final_saved;*VGAScreenSeg->format=final_format;free(replacement);
 }
}
/* Compile the whole generic dispatch, trapping every legacy entry. Migrated
 * bank9 quads must reject here before a warm legacy cache can authorize them. */
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value,data_fixed_value,fixed_pickup_flash;
static Asset assets[567];static Sprite2_array spriteSheet8;
static unsigned banking_draw_player;
typedef struct {bool valid;uint64_t last_tick;int logical_index,visual_index;} TalonBank;
static TalonBank talon_banks[2];
enum {ASSET_FIXED_PICKUP_FLASH,ASSET_DATA_VALUE,ASSET_CASH25_VALUE,ASSET_CASH75_VALUE,ASSET_CASH50_VALUE,ASSET_GEM100_VALUE,ASSET_GEM250_VALUE};
#define asteroid1_talon_blend_begin(...) CHECK(false)
#define fixed_pickup_flash_draw(...) false
#define data_value_draw(...) false
#define game_probe_scene_draw(...) ((void)0)
#define cash25_surface_ready(...) false
#define cash25_family_ready() false
#define cash75_family_ready() false
#define cash50_family_ready() false
#define gem100_family_ready() false
#define gem250_family_ready() false
#define draw_asset(x,y,a,s,p) ((void)(a),false)
#define sonic_quadrant_member(...) (-1)
#define vulcan_shadow_member(...) (-1)
#define draw_vulcan_shadow(...) false
static Asset *forbidden_asset(void){CHECK(false);return NULL;}
#define get_asset(...) forbidden_asset()
#define talon_frame(...) forbidden_asset()
#include "generic.inc"
static void generic_role_guards(void)
{
 for(unsigned warm=0;warm<2;warm++) {
  setup(valid_root,8);if(warm){pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);}
  unsigned before=asset_opens;snapshot_canvas();
  for(unsigned index=229;index<=237;index+=2)for(int style=MIRROR_NORMAL;style<=MIRROR_SHADOW;style++)
   CHECK(!render_mirror_entity(game_screen,95,73,spriteSheet9,index,style,ENTITY_QUAD));
  CHECK(asset_opens==before);CHECK(!memcmp(saved_canvas,canvas->pixels,(size_t)canvas->w*canvas->h*4));
 }
}
/* The native generic draw alias changes before/after gameplay, but the leased
 * source stays game_screen. Actual draw destination identity remains required. */
static void shared_hud_blend_ledger(void)
{
 setup(valid_root,4);render_mirror_global_reset();shared_hud_frame=true;active=false;
 Uint8 *at=index_at(2,3),before=*at,source=0x74;*at=(source&240)|(((source&15)+(before&15))/2);
 render_mirror_sprite2_blend_pixel(game_screen,at,source,spriteSheet9,233,2,3);
 CHECK(expected[3*320+2]==*at);CHECK(!global_talon_frame&&!global_talon_cached&&!asset_opens);
 shared_hud_frame=false;
}
static void native_alias_lifecycle(void)
{
 for(int d=4;d<=8;d+=4)for(int style=MIRROR_NORMAL;style<=MIRROR_SHADOW;style++) {
  setup(valid_root,d);render_mirror_global_reset();VGAScreen=VGAScreenSeg;
  global_talon_frame_begin();CHECK(global_talon_frame);
  VGAScreen=game_screen;pose(1,233,style==MIRROR_BLEND?10:0);
  unsigned opens=asset_opens;
  CHECK(render_mirror_global_player_ship(VGAScreenSeg,95,73,spriteSheet9,233,style,1,233)==0);
  CHECK(asset_opens==opens);CHECK(draw_at(95,73,233,style,1)==1);finish_draw(95,73,233,style);
  VGAScreen=VGAScreenSeg;map_final_indices();CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));check_output_mapping(true);
  memcpy(last_output_indices,VGAScreenSeg->pixels,64000);ready=last_output_valid=true;
  global_talon_check_cache();CHECK(global_talon_cached&&ready&&last_output_valid);
 }
}
/* Reset/disable is tested inside an accepted active legacy frame, with no
 * restart/begin that could erase the stale RGB and accidentally hide a ghost. */
static void reset_live_legacy_frame(void)
{
 for(unsigned disable=0;disable<2;disable++)for(int d=4;d<=8;d+=4) {
  setup(valid_root,d);active=true;memcpy(initial_palette,rgb_palette,sizeof(initial_palette));
  pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);map_final_indices();
  unsigned visible=0;for(int y=73*d;y<101*d;y++)for(int x=95*d;x<119*d;x++)if(*rgba_at(x,y)!=palette_rgb(*index_at(x/d,y/d)))++visible;CHECK(visible>0);
  size_t sentinel=(size_t)5*d*canvas->w+30*d;Uint32 other=0xff12abcd;((Uint32 *)canvas->pixels)[sentinel]=other;hd_owner[sentinel]=1;
  if(disable)CHECK(render_mirror_set_global_assets(NULL));else render_mirror_global_reset();
  CHECK(active);CHECK(!global_talon_frame&&!global_talon_cached);CHECK(!reject_reason);
  finish_allow_upscale=true;render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);finish_allow_upscale=false;
  CHECK(!reject_reason);CHECK(((Uint32 *)output->pixels)[(size_t)5*d*output->w+6*d]==other);CHECK(hd_owner[sentinel]==1);
  ((Uint32 *)output->pixels)[(size_t)5*d*output->w+6*d]=palette_rgb(*index_at(30,5));hd_owner[sentinel]=0;
  check_output_mapping(false);CHECK(!memchr(hd_owner,1,(size_t)canvas->w*canvas->h));
 }
}
/* Real fade entrypoints with independent HUD/font state held empty. The actual
 * source/canvas/output/final and saved surfaces remain observable and mutable. */
static uint64_t hud_generation,hud_output_generation,hud_saved_generation,component_generation,component_output_generation,component_saved_generation;
static uint64_t indicator_generation,indicator_output_generation,indicator_saved_generation,fixed_text_generation,fixed_text_output_generation,fixed_text_saved_generation;
static uint64_t font_generation,font_output_generation,font_saved_generation,indicator_under_generation,indicator_saved_under_generation;
static Uint8 hud_output_owner[64000],hud_saved_owner[64000],component_output_owner[64000],component_saved_owner[64000];
static Uint8 fixed_text_output_owner[370],fixed_text_saved_owner[370],indicator_output_owner[237],indicator_saved_owner[237];
static Uint8 font_powner[1024],font_psaved_owner[1024],indicator_under_owner[82],indicator_saved_under_owner[82];
static Uint32 indicator_under[82][64],indicator_saved_under[82][64];
#define font_cached() false
#define font_cached_indices_match() true
#define font_clear_cached(...) ((void)0)
#define components_cached_indices_match() true
#define components_clear_cached(...) ((void)0)
#define fixed_text_cached_indices_match() true
#define fixed_text_clear_cached() ((void)0)
#define indicators_cached_indices_match() true
#define indicators_underlay_matches() true
#define indicators_clear_cached(...) ((void)0)
#define hud_cached_indices_match() true
#define hud_clear_cached() ((void)0)
#define font_fade_save() ((void)0)
#define indicator_cell(...) (-1)
#define hud_fixed_text_cell(...) (-1)
#define font_pcell(...) (-1)
#define indicators_fade_underlay(...) ((void)0)
#define font_fade_underlay(...) ((void)0)
#define hud_storm_fade_palette(...) ((void)0)
#define game_probe_fade_sample(...) ((void)0)
#define SDL_CreateRGBSurfaceWithFormat(flags,w,h,depth,format) make_surface(w,h,depth)
#include "fade.inc"
static void prepare_fade(int d)
{
 prepare_composition(d,MIRROR_NORMAL,false);CHECK(global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0));
 memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(last_output_palette));
 ready=last_output_valid=true;SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
 CHECK(fade_saved&&fade_mode==1&&have_fade_saved&&last_output_valid&&!ready&&global_talon_cached);
}
static void fade_valid_progress(void)
{
 for(int d=4;d<=8;d+=4) {
  prepare_fade(d);size_t count=(size_t)output->w*output->h;Uint32 *before=malloc(count*4);CHECK(before);memcpy(before,output->pixels,count*4);
  /* This is the palette update the real engine performs before each fade
   * callback. It must not be compared to the old pre-fade palette as a lease. */
  for(unsigned i=0;i<256;i++){Uint32 v=rgb_palette[i],next=0;for(int shift=0;shift<24;shift+=8){int channel=(v>>shift)&255;next|=(Uint32)(channel+(0-channel)/2)<<shift;}rgb_palette[i]=next;}
  render_mirror_fade_step(2);CHECK(ready&&last_output_valid&&have_fade_saved&&global_talon_cached&&fade_mode==1);
  for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
   bool owned=x<264*d&&y<184*d&&hd_owner[(size_t)y*canvas->w+x+24*d];Uint32 want=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d]);
   if(owned){Uint32 v=before[(size_t)y*output->w+x];want=0xff000000u;for(int shift=0;shift<24;shift+=8){int channel=(v>>shift)&255;want|=(Uint32)(channel+(0-channel)/2)<<shift;}}
   CHECK(((Uint32 *)output->pixels)[(size_t)y*output->w+x]==want);
  }
  global_talon_check_cache();CHECK(global_talon_cached&&last_output_valid);
  memset(rgb_palette,0,sizeof(rgb_palette));render_mirror_fade_step(1);CHECK(ready&&last_output_valid&&global_talon_cached&&!fade_mode);
  global_talon_check_cache();CHECK(global_talon_cached&&last_output_valid);free(before);
 }
}
static void fade_invalid_leases(void)
{
 for(unsigned which=0;which<23;which++) {
  prepare_fade(4);SDL_Surface saved_output=*output,saved_canvas_surface=*canvas,saved_final=*VGAScreenSeg,saved_source=*game_screen,saved_fade=*fade_saved;
  SDL_PixelFormat out_format=*output->format,canvas_format=*canvas->format,final_format=*VGAScreenSeg->format,source_format=*game_screen->format,fade_format=*fade_saved->format;
  void *replacement=NULL;
  switch(which) {
   case 0:game_probe_density=8;break;
   case 1:output->pixels=NULL;break;case 2:output->pitch=1;break;case 3:output->w=1;break;case 4:output->format->BitsPerPixel=8;break;
   case 5:canvas->pixels=NULL;break;case 6:canvas->pitch=1;break;case 7:canvas->w=1;break;
   case 8:VGAScreenSeg->pixels=NULL;break;case 9:VGAScreenSeg->pitch=1;break;case 10:VGAScreenSeg->format->BytesPerPixel=4;break;
   case 11:game_screen->pixels=NULL;break;case 12:game_screen->pitch=1;break;
   case 13:fade_saved->pixels=NULL;break;case 14:fade_saved->pitch=1;break;case 15:fade_saved->w=1;break;
   case 16:replacement=malloc((size_t)fade_saved->pitch*fade_saved->h);CHECK(replacement);memcpy(replacement,fade_saved->pixels,(size_t)fade_saved->pitch*fade_saved->h);fade_saved->pixels=replacement;break;
   case 17:fade_saved->pitch++;break;case 18:fade_saved->pixels=(Uint8 *)fade_saved->pixels+1;break;
   case 19:fade_saved->pixels=(Uint8 *)canvas->pixels+4;break;case 20:canvas->pixels=(Uint8 *)canvas->pixels+1;break;
   case 21:output->pixels=(Uint8 *)canvas->pixels+4;break;case 22:rgb_palette[255]^=1;break;
  }
  render_mirror_fade_step(2);CHECK(!ready&&!last_output_valid&&!have_fade_saved&&!fade_mode&&!global_talon_cached);
  game_probe_density=4;*output=saved_output;*canvas=saved_canvas_surface;*VGAScreenSeg=saved_final;*game_screen=saved_source;*fade_saved=saved_fade;
  *output->format=out_format;*canvas->format=canvas_format;*VGAScreenSeg->format=final_format;*game_screen->format=source_format;*fade_saved->format=fade_format;free(replacement);
 }
}
static void fade_later_write_layout(void)
{
 for(unsigned which=0;which<5;which++){
  prepare_fade(4);SDL_Surface saved=*fade_saved;SDL_PixelFormat format=*fade_saved->format;
  switch(which){case 0:fade_saved->pixels=NULL;break;case 1:fade_saved->pitch=1;break;case 2:fade_saved->w=1;break;case 3:fade_saved->pixels=(Uint8 *)canvas->pixels+4;break;case 4:fade_saved->format->BytesPerPixel=1;break;}
  unsigned cell=owned_cell();int x=(int)(cell%320)-24,y=(int)(cell/320);Uint8 *at=(Uint8 *)VGAScreenSeg->pixels+y*320+x;
  global_talon_final_pixel(VGAScreenSeg,at);
  CHECK(!global_talon_cached&&!ready&&!last_output_valid&&!have_fade_saved&&!fade_mode);
  *fade_saved=saved;*fade_saved->format=format;
 }
}
static void fade_presave_layout(void)
{
 for(unsigned which=0;which<7;which++) {
  prepare_fade(4);SDL_Surface saved=*fade_saved;SDL_PixelFormat format=*fade_saved->format;
  switch(which){case 0:fade_saved->pixels=NULL;break;case 1:fade_saved->pitch=1;break;case 2:fade_saved->pitch++;break;
   case 3:fade_saved->pixels=(Uint8 *)fade_saved->pixels+1;break;case 4:fade_saved->pixels=(Uint8 *)canvas->pixels+4;break;
   case 5:fade_saved->format->BytesPerPixel=1;break;case 6:fade_saved->w=1;break;}
  SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);
  CHECK(!ready&&!last_output_valid&&!have_fade_saved&&!fade_mode&&!global_talon_cached);
  *fade_saved=saved;*fade_saved->format=format;
 }
}
static void aligned_disjoint_geometry(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned which=0;which<9;which++) {
  setup(valid_root,4);if(warm){pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==1);finish_draw(95,73,233,MIRROR_NORMAL);}
  render_mirror_global_reset();unsigned opens=asset_opens;
  SDL_Surface a=*game_screen,b=*VGAScreenSeg,c=*canvas,o=*output;
  switch(which){case 0:canvas->pitch++;break;case 1:canvas->pixels=(Uint8 *)canvas->pixels+1;break;case 2:output->pixels=(Uint8 *)output->pixels+1;break;
   case 3:canvas->pixels=game_screen->pixels;break;case 4:output->pixels=(Uint8 *)canvas->pixels+4;break;
   case 5:VGAScreenSeg->pixels=(Uint8 *)game_screen->pixels+1;break;case 6:game_screen->pixels=(Uint8 *)output->pixels+4;break;
   case 7:VGAScreenSeg->pixels=(Uint8 *)canvas->pixels+4;break;case 8:canvas->pixels=(Uint8 *)VGAScreenSeg->pixels+4;break;}
  global_talon_frame_begin();CHECK(!global_talon_frame);pose(1,233,0);CHECK(draw_at(95,73,233,MIRROR_NORMAL,1)==0);CHECK(asset_opens==opens);
  *game_screen=a;*VGAScreenSeg=b;*canvas=c;*output=o;
 }
}
int main(int argc,char **argv)
{
 CHECK(argc==4);valid_root=argv[1];fixture_root=argv[2];load_original();source_backup=malloc(spriteSheet9.size);CHECK(source_backup);memcpy(source_backup,spriteSheet9.data,spriteSheet9.size);
 load_reference_frames(valid_root);check_source_decoder();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"guards"))cold_guards();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"resources"))resource_failures();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"alpha"))alpha_and_writes();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"source"))source_and_lifecycle();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"pose"))pose_lifecycle();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"output"))output_and_final_writes();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"night"))night_mapping();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"cache"))cache_and_layout();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"underlay"))underlay_palette();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"transactions"))transaction_faults();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"finish"))finish_layout_guard();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"role"))generic_role_guards();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"alias"))native_alias_lifecycle();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"alias"))shared_hud_blend_ledger();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"reset"))reset_live_legacy_frame();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"fade"))fade_valid_progress();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"fade_bad"))fade_invalid_leases();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"fade_presave"))fade_presave_layout();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"fade_presave"))fade_later_write_layout();
 if(!strcmp(argv[3],"all")||!strcmp(argv[3],"geometry"))aligned_disjoint_geometry();
 global_talon_shutdown();free_surface(fade_saved);free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(spriteSheet9.data);free(source_backup);free(saved_canvas);free(saved_owners);
 for(unsigned i=0;i<13;i++)free(reference_frames[i]);
 printf("PASS: %u cases, %u assertions; extracted Talon13 observer only, not integrated engine proof\n",cases,checks);return 0;
}
