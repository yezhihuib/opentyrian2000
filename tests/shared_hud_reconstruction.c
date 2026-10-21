/* Fresh shared-stage reconstruction oracle: current extracted production bodies.
 * Original game bytes arrive on stdin and are retained only in process memory. */
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
typedef struct { int BytesPerPixel,BitsPerPixel;unsigned format; } SDL_PixelFormat;
typedef struct { int x,y,w,h; } SDL_Rect;
typedef struct { int w,h,pitch; void *pixels; SDL_PixelFormat *format; SDL_Rect clip_rect; } SDL_Surface;

typedef struct { Uint8 r,g,b,a; } SDL_Color;
typedef int SDL_Renderer;
typedef int SDL_Texture;
#define SDL_PIXELFORMAT_ARGB8888 0
#define SDL_PIXELFORMAT_INDEX8 1
#define SDL_PIXELFORMAT_RGB332 2
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
 p->format->format=depth==8?SDL_PIXELFORMAT_INDEX8:SDL_PIXELFORMAT_ARGB8888;p->format->BytesPerPixel=depth/8;p->format->BitsPerPixel=depth;++allocations;return p;
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

/* Unrelated scene/menu adapters are deliberately inert. HUD and font paths below
 * are production bodies; all six production loaders retain their real pins. */
static bool shared_hud_lease,shared_hud_frame,manual_hd_lease,asteroid_hd_lease;
static char shared_hud_assets[1024],global_asset_directory[1024];
#include "shared_root.inc"
static bool manual_hd_enabled,asteroid_hd_enabled,xmas,isNetworkGame,twoPlayerLinked,record_demo,onePlayerAction,superTyrian,timedBattleMode,bonusLevel,normalBonusLevelCurrent,bonusLevelCurrent,play_demo;
static int episodeNum=1,lvlFileNum=2,initialDifficulty=2,superArcadeMode;
static char terrain_file='a';
#define SA_NONE 0
#define DIFFICULTY_NORMAL 2
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value,data_fixed_value,fixed_pickup_flash;
static bool game_probe_local_blend;
typedef struct {SDL_Rect rect;bool live;} HdRegion;
static HdRegion regions[1];
static void restore_classic_rect(SDL_Rect r){assert(false);}
static bool vulcan_shadow_pixel(SDL_Surface *s,int x,int y,Uint8 a,Uint8 b,int style){return false;}
#define NOOP(name) static void name(void){}
NOOP(rear_p1_frame) NOOP(vulcan_shadow_clear) NOOP(asteroid1_talon_blend_reset)
NOOP(render_mirror_shadow_end) NOOP(hud_storm_reset) NOOP(hud_storm_shutdown) NOOP(hud_storm_suspend) NOOP(storm_resume)
NOOP(rear_p1_shutdown) NOOP(asteroid1_shutdown) NOOP(asteroid4_shutdown) NOOP(asteroid_common4_shutdown)
NOOP(asteroid_random5_shutdown) NOOP(asteroid_random43_shutdown) NOOP(asteroid_random85_shutdown) NOOP(asteroid_random123_shutdown) NOOP(asteroid_random95_shutdown) NOOP(asteroid_random114_shutdown) NOOP(asteroid_random133_shutdown) NOOP(asteroid_random152_shutdown) NOOP(goldwing_shutdown) NOOP(asteroid_random286_shutdown) NOOP(fork284_shutdown) NOOP(capsule545_shutdown) NOOP(paired287_288_shutdown) NOOP(firing325_shutdown) NOOP(ember269_shutdown) NOOP(linked338_shutdown) NOOP(pulsing272_shutdown) NOOP(triple275_shutdown) NOOP(columns276_shutdown) NOOP(turret273_shutdown) NOOP(projectile304_shutdown) NOOP(firing270_shutdown) NOOP(firing285_shutdown) NOOP(enemy_orb112113_shutdown) NOOP(terrain144_shutdown)
static void storm_start(SDL_Surface *s){}
static void hud_storm_fade_palette(const Uint32 *p){}
static void storm_present(void *p,int pitch){}
/* Pause seam is independently tested; HUD oracle keeps the menu owner off. */
/* Global family internals have a separate real-source oracle. This suite
 * exercises the shared HUD with that independent owner inactive. */
static bool global_talon_frame;
static bool global_talon_requested(void){return false;}
static bool global_talon_surface_matches(void){return true;}
static bool global_talon_final_surface_matches(void){return true;}
static bool global_talon_fade_buffer_safe(void){return true;}
static bool global_talon_fade_capture(void){return true;}
static bool global_talon_fade_step_valid(int steps){(void)steps;return true;}
void render_mirror_global_reset(void){}
static void global_talon_fail(void){}
static void global_talon_shutdown(void){}
static void global_talon_frame_begin(void){global_talon_frame=false;}
static bool global_talon_pixel(int x,int y,Uint8 before,Uint8 after,int style){return false;}
static void global_talon_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_talon_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_talon_end(void){}
static bool global_talon_compose(int kind,int lightx,int lighty){return false;}
static void global_talon_check_cache(void){}
static void global_talon_fade_palette(void){}
/* Independent Shield disabled in this focused HUD observer. */
/* This family is disabled in this isolated regression harness. */
/* Vulcan is disabled only in this isolated regression harness. */
static bool global_vulcan_frame,global_vulcan_fault,global_vulcan_cached;
static Uint8 *global_vulcan_owner,*global_vulcan_foreign;
#define global_vulcan_source_matches(...) true
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
#define global_vulcan_compose(...) false
static void global_vulcan_check_cache(void){}
static bool global_vulcan_fade_buffer_safe(void){return true;}
static bool global_vulcan_fade_capture(void){return true;}
static bool global_vulcan_fade_step_valid(int steps){return true;}
static void global_vulcan_fade_palette(void){}
static bool global_hitflare_frame,global_hitflare_fault,global_hitflare_cached;
static Uint8 *global_hitflare_owner,*global_hitflare_foreign;
#define global_hitflare_source_matches(...) true
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
#define global_hitflare_compose(...) false
static void global_hitflare_check_cache(void){}
static bool global_hitflare_fade_buffer_safe(void){return true;}
static bool global_hitflare_fade_capture(void){return true;}
static bool global_hitflare_fade_step_valid(int steps){return true;}
static void global_hitflare_fade_palette(void){}
/* This family is disabled in this isolated regression harness. */
static bool global_pulse_frame,global_pulse_fault,global_pulse_cached;
static Uint8 *global_pulse_owner,*global_pulse_foreign;
#define global_pulse_source_matches(...) true
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
#define global_pulse_compose(...) false
static void global_pulse_check_cache(void){}
static bool global_pulse_fade_buffer_safe(void){return true;}
static bool global_pulse_fade_capture(void){return true;}
static bool global_pulse_fade_step_valid(int steps){return true;}
static void global_pulse_fade_palette(void){}
static bool global_shield_frame;
static bool global_shield_requested(void){return false;}
static bool global_shield_surface_matches(void){return true;}
static bool global_shield_final_surface_matches(void){return true;}
static bool global_shield_fade_buffer_safe(void){return true;}
static bool global_shield_fade_capture(void){return true;}
static bool global_shield_fade_step_valid(int steps){(void)steps;return true;}
static void global_shield_fail(void){}
static void global_shield_shutdown(void){}
static void global_shield_frame_begin(void){global_shield_frame=false;}
static bool global_shield_pixel(int x,int y,Uint8 before,Uint8 after,int style){return false;}
static void global_shield_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_shield_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_shield_end(void){}
static bool global_shield_cached;
static bool global_shield_finish_proof(void){return true;}
static bool global_shield_compose(int kind,int lightx,int lighty){return false;}
static void global_shield_check_cache(void){}
static void global_shield_fade_palette(void){}
static bool common_menu_configured(void){return false;}
static void common_pause_snapshot_stage(SDL_Surface *s,const void *p,int pitch,int w,int h,unsigned d){}
static void common_pause_snapshot_commit(void){}
static void common_pause_snapshot_discard_candidate(void){}
#define PIXEL2(n) static void n(SDL_Surface *s,Uint8 *p){}
#define PIXEL3(n) static void n(SDL_Surface *s,Uint8 *p,int style){}
#define RECT(n) static void n(SDL_Surface *s,const SDL_Rect *r){}
PIXEL2(data_frame_pixel) PIXEL2(data_portrait_pixel) PIXEL2(storm_pixel)
PIXEL3(common_pause_pixel)
RECT(common_pause_rect)
PIXEL3(settings_font_pixel) PIXEL3(load_font_pixel) PIXEL3(selector_font_pixel) PIXEL3(pregame_font_pixel)
RECT(data_frame_rect) RECT(data_portrait_rect) RECT(storm_rect) RECT(settings_font_rect) RECT(load_font_rect) RECT(selector_font_rect) RECT(pregame_font_rect)
typedef enum {MIRROR_OUTPUT_UNKNOWN,MIRROR_OUTPUT_ORDINARY,MIRROR_OUTPUT_NORMAL15_NIGHT,MIRROR_OUTPUT_NORMAL15_LOW_DETAIL} MirrorOutputKind;
#include "gameplay_hud_font_mirror.inc"
#include "production.inc"
static Uint8 original_pic[64000];
static Uint32 normal_palette[256];
static unsigned checks;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"CHECK failed at %s:%d: %s\n",__FILE__,__LINE__,#x);abort();}} while(0)
static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static void load_original(void)
{
 read_exact(original_pic,sizeof(original_pic));read_exact(normal_palette,sizeof(normal_palette));read_exact(font_ascii,sizeof(font_ascii));
 for(unsigned ti=0;ti<2;ti++) {
  unsigned table=ti?OPTION_SHAPES:TINY_FONT;Uint16 count;read_exact(&count,2);CHECK(count<=152);sprite_table[table].count=count;
  for(unsigned i=0;i<count;i++) {Sprite *s=&sprite_table[table].sprite[i];read_exact(&s->width,2);read_exact(&s->height,2);read_exact(&s->size,2);if(s->size){s->data=malloc(s->size);CHECK(s->data);read_exact(s->data,s->size);}}
 }
 CHECK(fgetc(stdin)==EOF);
}
static void cleanup(void)
{
 render_mirror_hud_shutdown();
 SDL_FreeSurface(canvas);SDL_FreeSurface(output);SDL_FreeSurface(fade_saved);SDL_FreeSurface(game_screen);SDL_FreeSurface(VGAScreenSeg);
 canvas=output=fade_saved=game_screen=VGAScreenSeg=NULL;
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 hd_owner=cloud_owner=green_under_owner=NULL;green_first=NULL;green_under=NULL;
 shared_hud_assets[0]=global_asset_directory[0]=0;shared_hud_lease=shared_hud_frame=false;
}
static void setup(const char *root,int d)
{
 cleanup();
 game_probe_enabled=game_probe_missing=game_probe_invalid=game_probe_original_reference=game_probe_coverage_fault=false;
 manual_hd_enabled=asteroid_hd_enabled=manual_hd_lease=asteroid_hd_lease=false;
 xmas=isNetworkGame=twoPlayerMode=galagaMode=twoPlayerLinked=record_demo=onePlayerAction=superTyrian=timedBattleMode=bonusLevel=normalBonusLevelCurrent=bonusLevelCurrent=play_demo=false;
 episodeNum=1;lvlFileNum=2;initialDifficulty=DIFFICULTY_NORMAL;superArcadeMode=SA_NONE;
 game_probe_assets="/no-legacy-scene-pack";game_probe_density=d;game_probe_skip=true;game_probe_repeat=false;
 last_output_valid=have_fade_saved=have_initial_palette=ready=active=false;fade_mode=0;reject_reason=NULL;texture=NULL;
 game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 memcpy(VGAScreenSeg->pixels,original_pic,64000);memset(game_screen->pixels,7,64000);memcpy(rgb_palette,normal_palette,sizeof(rgb_palette));
 memset(options,0,sizeof(options));memset(shields,0,sizeof(shields));memset(player,0,sizeof(player));power=lastPower=0;strcpy(levelName,"TEST");
 CHECK(render_mirror_set_hud_assets(root));
}
static void grant(void){render_mirror_hud_start(VGAScreenSeg);}
static void all_ready(void)
{CHECK(gameplay_hud_ready());CHECK(hud_components_ready());CHECK(hud_meters_ready());CHECK(hud_indicators_ready());CHECK(hud_fixed_text_ready());CHECK(hud_font_ready());}
static void none_ready(void)
{CHECK(!gameplay_hud_ready());CHECK(!hud_components_ready());CHECK(!hud_meters_ready());CHECK(!hud_indicators_ready());CHECK(!hud_fixed_text_ready());CHECK(!hud_font_ready());}
static Uint32 *pixel(SDL_Surface *s,int x,int y){return (Uint32 *)((Uint8 *)s->pixels+y*s->pitch)+x;}
static void frame(MirrorOutputKind kind)
{
 uint64_t before=gameplay_hud_fnv64(VGAScreenSeg->pixels,64000),scene=gameplay_hud_fnv64(game_screen->pixels,64000);
 render_mirror_begin();render_mirror_finish(kind,0,0);
 CHECK(before==gameplay_hud_fnv64(VGAScreenSeg->pixels,64000));CHECK(scene==gameplay_hud_fnv64(game_screen->pixels,64000));
}
static void static_owners(void)
{CHECK(hud_output_generation);CHECK(component_output_generation);CHECK(indicator_output_generation);CHECK(fixed_text_output_generation);CHECK(ready&&last_output_valid);}
static void verify_actual_world(void)
{
 int d=game_probe_density;
 for(int y=0;y<184*d;y++)for(int x=0;x<264*d;x++)CHECK(*pixel(output,x,y)==palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d]));
}
static void draw_scene_text(unsigned kind);
static void verify_static_samples(void)
{
 int d=game_probe_density;unsigned samples=0;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  unsigned logical=y*320+x;int indicator=indicator_cell(x,y),fixed=hud_fixed_text_cell(x,y);
  bool own=hud_output_owner[logical]||component_output_owner[logical]||(indicator>=0&&indicator_output_owner[indicator])||(fixed>=0&&fixed_text_output_owner[fixed]);
  if(!own)continue;
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[logical];
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   const Uint8 *rgba=NULL;
   if(hud_output_owner[logical])rgba=gameplay_hud_sample(x,y,sx,sy,d,index);
   if(component_output_owner[logical]) {const Uint8 *p=hud_components_label_sample(x,y,sx,sy,d,index);if(p)rgba=p;}
   if(indicator>=0&&indicator_output_owner[indicator])rgba=hud_indicators_sample(x,y,sx,sy,d,index);
   if(fixed>=0&&fixed_text_output_owner[fixed])rgba=hud_fixed_text_sample((unsigned)fixed,sx,sy,d);
   CHECK(rgba);CHECK(*pixel(output,x*d+sx,y*d+sy)==(0xff000000u|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2]));++samples;
  }
 }
 CHECK(samples>1000);
}
static void coexistence_suite(const char *root)
{
 for(unsigned mode=0;mode<3;mode++) {
  setup(root,4);manual_hd_enabled=true;asteroid_hd_enabled=mode==1;lvlFileNum=mode==2?9:2;grant();all_ready();
  CHECK(shared_hud_lease);CHECK(mirror_enabled()==(mode==2));render_mirror_begin();CHECK(active==(mode==2));
  if(mode==2){draw_scene_text(1);hd_owner[20*4*canvas->w+50*4]=1;*pixel(canvas,50*4,20*4)=0xffab12cdu;render_mirror_unsupported("legacy-world-rejected");}
  render_mirror_finish(MIRROR_OUTPUT_UNKNOWN,0,0);static_owners();verify_actual_world();verify_static_samples();
  CHECK(!font_scenes[1].output_live);if(mode==2)CHECK(!memchr(hd_owner,1,(size_t)canvas->w*canvas->h));
 }
 puts("PASS shared HUD with inactive legacy flags and rejected active legacy scene");
 for(int d=4;d<=8;d+=4) {
  setup(root,d);manual_hd_enabled=true;lvlFileNum=9;grant();all_ready();CHECK(shared_hud_lease&&manual_hd_lease&&mirror_enabled());
  render_mirror_begin();CHECK(active&&shared_hud_frame&&!game_probe_enabled);draw_scene_text(1);
  hd_owner[20*d*canvas->w+50*d]=1;*pixel(canvas,50*d,20*d)=0xffab12cdu;
  render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!reject_reason);static_owners();verify_static_samples();
  CHECK(font_scenes[1].output_live&&last_output_scene_hd);CHECK(*pixel(output,26*d,20*d)==0xffab12cdu);
  for(int y=0;y<184*d;y++)for(int x=0;x<264*d;x++)CHECK(*pixel(output,x,y)==*pixel(canvas,x+24*d,y));
  CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 }
 puts("PASS genuinely accepted ORDINARY legacy scene plus shared static HUD and scene-font at 4x/8x");
}
static void stage_suite(const char *root)
{
 for(int d=4;d<=8;d+=4)for(unsigned level=1;level<=18;level++) {
  setup(root,d);lvlFileNum=(int)level;grant();all_ready();CHECK(shared_hud_lease);CHECK(!manual_hd_lease&&!asteroid_hd_lease&&!mirror_enabled()&&!active);
  frame(MIRROR_OUTPUT_UNKNOWN);static_owners();CHECK(!active&&!render_mirror_owns_display()&&!game_probe_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled);verify_actual_world();verify_static_samples();
  CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 }
 setup(NULL,4);grant();none_ready();CHECK(!shared_hud_lease);render_mirror_begin();CHECK(!active&&!shared_hud_frame);
 setup(root,4);CHECK(render_mirror_set_global_assets("/configured-but-unadmitted"));CHECK(!mirror_enabled());grant();all_ready();CHECK(!mirror_enabled());
 for(unsigned flag=0;flag<7;flag++) {
  setup(root,4);if(flag==0)twoPlayerMode=true;if(flag==1)galagaMode=true;if(flag==2)game_probe_missing=true;if(flag==3)game_probe_invalid=true;if(flag==4)game_probe_original_reference=true;if(flag==5)game_probe_density=1;if(flag==6)game_probe_density=3;
  grant();none_ready();CHECK(!shared_hud_lease);
 }
 puts("PASS independent root, 18 level scopes at 4x/8x, no scene/manual/probe admission, static HUD actual-final-surface");
}
static void draw_scene_text(unsigned kind)
{
 render_mirror_text_begin(game_screen,kind,kind?28:30,kind?8:175,kind?"TEST":"123",2,kind?6:4);
 CHECK(font_context==(int)kind);unsigned count=font_command_count;
 for(unsigned i=0;i<count;i++) {
  FontCommand c=font_commands[i];Sprite *s=&sprite_table[TINY_FONT].sprite[c.id];Uint8 indices[48]={0},opaque[48]={0};
  CHECK(hud_sprite_decode(TINY_FONT,c.id,6,8,indices,opaque));
  render_mirror_text_glyph_begin(game_screen,c.x,c.y,TINY_FONT,c.id,c.black,c.hue,c.value);
  CHECK(font_glyph_active);
  for(unsigned y=0;y<s->height;y++)for(unsigned x=0;x<s->width;x++)if(opaque[y*s->width+x]) {
   Uint8 *p=(Uint8 *)game_screen->pixels+(c.y+y)*game_screen->pitch+c.x+x;
   *p=c.black?0:((c.hue<<4)|((indices[y*s->width+x]&15)+c.value));render_mirror_pixel(game_screen,p,*p,MIRROR_NORMAL);
  }
  render_mirror_text_glyph_end();
 }
 render_mirror_text_end();CHECK(font_scenes[kind].canvas_live);
 for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);
}
static void scene_suite(const char *root)
{
 for(int d=4;d<=8;d+=4)for(unsigned textkind=0;textkind<2;textkind++)for(int mode=0;mode<9;mode++) {
  setup(root,d);grant();render_mirror_begin();draw_scene_text(textkind);
  MirrorOutputKind kind=mode==0?MIRROR_OUTPUT_ORDINARY:mode==1?MIRROR_OUTPUT_NORMAL15_LOW_DETAIL:mode==2?MIRROR_OUTPUT_UNKNOWN:mode==3?MIRROR_OUTPUT_NORMAL15_NIGHT:MIRROR_OUTPUT_ORDINARY;
  FontScene *r=font_scenes+textkind;int sample=-1;
  for(unsigned i=0;i<r->used;i++)if(font_owner[r->offset+i]){sample=(int)i;break;}CHECK(sample>=0);
  int logical=sample/(d*d),sx=sample%d,sy=(sample/d)%d,x=r->rect.x+logical%r->rect.w,y=r->rect.y+logical/r->rect.w;
  Uint32 want=*pixel(canvas,x*d+sx,y*d+sy);
  if(mode==4)((Uint8 *)VGAScreenSeg->pixels)[r->rect.y*320+r->rect.x-24]^=1;
  if(mode==5)((Uint8 *)game_screen->pixels)[0]^=1;
  if(mode==6){game_screen->format->BitsPerPixel=16;game_screen->format->BytesPerPixel=2;}
  if(mode==7)render_mirror_unsupported("unrelated-scene-rejection");
  if(mode==8)game_screen->format->format=SDL_PIXELFORMAT_RGB332;
  render_mirror_finish(kind,0,0);static_owners();
  if(mode<2){CHECK(r->output_live&&last_output_scene_hd);CHECK(*pixel(output,(x-24)*d+sx,y*d+sy)==want);}
  else {CHECK(!r->output_live&&!last_output_scene_hd);verify_actual_world();}
  if(mode==6){game_screen->format->BitsPerPixel=8;game_screen->format->BytesPerPixel=1;}
  if(mode==8)game_screen->format->format=SDL_PIXELFORMAT_INDEX8;
 }
 puts("PASS exact ordinary/low-detail scene-font output witness; unknown/night/index-mismatch/source-format/rejection strip only scene fonts");
}
static void same_index_suite(const char *root)
{
 setup(root,4);grant();render_mirror_begin();draw_scene_text(1);FontScene *r=font_scenes+1;
 int x=-1,y=-1;for(unsigned k=0;k<r->used;k++)if(font_owner[r->offset+k]){unsigned n=k/16;x=r->rect.x+n%r->rect.w;y=r->rect.y+n/r->rect.w;break;}
 CHECK(x>=0);Uint8 *p=(Uint8 *)game_screen->pixels+y*320+x;Uint8 same=*p;render_mirror_pixel(game_screen,p,same,MIRROR_NORMAL);
 unsigned base=r->offset+((y-r->rect.y)*r->rect.w+x-r->rect.x)*16;CHECK(!memchr(font_owner+base,1,16));
 render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);for(int sy=0;sy<4;sy++)for(int sx=0;sx<4;sx++)CHECK(*pixel(output,(x-24)*4+sx,y*4+sy)==palette_rgb(same));
 puts("PASS same-index witnessed scene writes remove HD ownership");
}
static void lifecycle_suite(const char *root,const char *temp)
{
 setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);uint64_t generation=hud_generation;unsigned alloc=allocations;
 CHECK(render_mirror_set_hud_assets(root));CHECK(hud_generation==generation);frame(MIRROR_OUTPUT_UNKNOWN);CHECK(alloc==allocations);
 render_mirror_hud_suspend();CHECK(hud_suspended&&font_suspended);frame(MIRROR_OUTPUT_UNKNOWN);static_owners();
 render_mirror_hud_reset();none_ready();CHECK(!shared_hud_lease&&!shared_hud_frame&&!ready&&!last_output_valid);render_mirror_begin();CHECK(!shared_hud_frame);
 grant();all_ready();frame(MIRROR_OUTPUT_UNKNOWN);CHECK(render_mirror_set_hud_assets(NULL));none_ready();CHECK(!ready&&!shared_hud_lease&&!shared_hud_assets[0]);
 CHECK(render_mirror_set_hud_assets(root));grant();all_ready();char path[2048];snprintf(path,sizeof(path),"%s/empty",temp);CHECK(render_mirror_set_hud_assets(path));grant();none_ready();
 CHECK(render_mirror_set_hud_assets(root));grant();all_ready();memset(path,'x',sizeof(path)-1);path[sizeof(path)-1]=0;CHECK(!render_mirror_set_hud_assets(path));none_ready();CHECK(!shared_hud_assets[0]&&!shared_hud_lease);
 for(unsigned flag=0;flag<5;flag++) {
  setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);if(flag==0)game_probe_original_reference=true;if(flag==1)game_probe_missing=true;if(flag==2)game_probe_invalid=true;if(flag==3)twoPlayerMode=true;if(flag==4)galagaMode=true;
  render_mirror_begin();render_mirror_finish(MIRROR_OUTPUT_UNKNOWN,0,0);none_ready();CHECK(!last_output_valid);
 }
 puts("PASS lifecycle suspend/resume/reset, root idempotence/replacement/disable/overlong, live diagnostics/mode revocation");
}
static void feature_off_suite(const char *root)
{
 setup(NULL,4);ready=true;render_mirror_finish(MIRROR_OUTPUT_UNKNOWN,0,0);CHECK(ready&&!shared_hud_frame);
 setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);CHECK(ready&&!shared_hud_frame);render_mirror_finish(MIRROR_OUTPUT_UNKNOWN,0,0);CHECK(ready);
 CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 setup(root,4);VGAScreenSeg->format->format=SDL_PIXELFORMAT_RGB332;grant();none_ready();CHECK(!shared_hud_lease);
 setup(root,4);grant();render_mirror_begin();VGAScreenSeg->format->format=SDL_PIXELFORMAT_RGB332;render_mirror_finish(MIRROR_OUTPUT_UNKNOWN,0,0);CHECK(!ready);none_ready();
 puts("PASS inactive finish preserves ready, repeated finish does not consume Present, exact INDEX8 source tag");
}
static void isolation_suite(const char *root,const char *temp)
{
 for(unsigned mode=0;mode<2;mode++)for(unsigned missing=0;missing<6;missing++) {
  char path[2048];snprintf(path,sizeof(path),"%s/%s%u",temp,mode?"corrupt":"missing",missing);setup(path,4);grant();
  bool statuses[]={gameplay_hud_ready(),hud_components_ready(),hud_meters_ready(),hud_indicators_ready(),hud_fixed_text_ready(),hud_font_ready()};
  for(unsigned j=0;j<6;j++)CHECK(statuses[j]==(j!=missing));frame(MIRROR_OUTPUT_UNKNOWN);CHECK(last_output_valid&&ready);verify_actual_world();
 }
 puts("PASS missing/corrupt resource family isolation for all six actual loaders");
}
static void mutation_suite(const char *root)
{
 for(unsigned mutation=0;mutation<8;mutation++) {
  setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);
  SDL_Surface *old=VGAScreenSeg;void *pixels=old->pixels;SDL_PixelFormat *format=old->format;
  if(mutation==0){VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,0);memcpy(VGAScreenSeg->pixels,pixels,64000);}
  if(mutation==1){old->pixels=malloc(64000);memcpy(old->pixels,pixels,64000);}
  if(mutation==2){old->format=malloc(sizeof(*format));*old->format=*format;}
  if(mutation==3)old->w=319;
  if(mutation==4)old->h=199;
  if(mutation==5)old->pitch=321;
  if(mutation==6)old->format->BitsPerPixel=16;
  if(mutation==7)old->format->BytesPerPixel=2;
  render_mirror_hud_suspend();none_ready();CHECK(!ready&&!last_output_valid);
  if(mutation==0){SDL_FreeSurface(VGAScreenSeg);VGAScreenSeg=old;}
  if(mutation==1){free(old->pixels);old->pixels=pixels;}
  if(mutation==2){free(old->format);old->format=format;}
  old->w=320;old->h=200;old->pitch=320;old->format->BitsPerPixel=8;old->format->BytesPerPixel=1;
 }
 setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);rgb_palette[0]^=1;CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!ready&&!last_output_valid);
 setup(root,4);grant();sprite_table[TINY_FONT].sprite[0].data[0]^=1;render_mirror_begin();CHECK(!hud_font_ready());CHECK(hud_components_ready()&&hud_fixed_text_ready());sprite_table[TINY_FONT].sprite[0].data[0]^=1;
 setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);game_probe_density=8;render_mirror_begin();CHECK(!active&&!shared_hud_frame&&!ready);render_mirror_finish(MIRROR_OUTPUT_UNKNOWN,0,0);CHECK(!ready);
 for(unsigned mutation=0;mutation<8;mutation++) {
  setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);
  void *oldpixels=game_screen->pixels;SDL_PixelFormat *oldformat=game_screen->format;
  if(mutation==0)game_screen->pixels=NULL;if(mutation==1)game_screen->format=NULL;
  if(mutation==2)game_screen->w=319;if(mutation==3)game_screen->h=199;if(mutation==4)game_screen->pitch=319;
  if(mutation==5)game_screen->format->BitsPerPixel=16;if(mutation==6)game_screen->format->BytesPerPixel=2;if(mutation==7)game_screen->format->format=SDL_PIXELFORMAT_RGB332;
  render_mirror_begin();CHECK(!active&&!shared_hud_frame&&!ready);
  game_screen->pixels=oldpixels;game_screen->format=oldformat;game_screen->w=320;game_screen->h=200;game_screen->pitch=320;game_screen->format->BitsPerPixel=8;game_screen->format->BytesPerPixel=1;game_screen->format->format=SDL_PIXELFORMAT_INDEX8;
 }
 puts("PASS source identity/layout, font-source/palette mutation, stale-density fail-closed");
}
static Uint32 channel_step(Uint32 before,Uint32 target,int steps)
{Uint32 out=0xff000000u;for(int s=0;s<24;s+=8){int old=(before>>s)&255,want=(target>>s)&255;out|=(Uint32)(old+(want-old)/steps)<<s;}return out;}
static void scene_cache_suite(const char *root)
{
 for(int d=4;d<=8;d+=4) {
  setup(root,d);grant();render_mirror_begin();draw_scene_text(1);FontScene *r=font_scenes+1;unsigned k=0;while(k<r->used&&!font_owner[r->offset+k])++k;CHECK(k<r->used);
  unsigned cell=k/(d*d);int x=(r->rect.x+(int)(cell%r->rect.w)-24)*d+(int)(k%d),y=(r->rect.y+(int)(cell/r->rect.w))*d+(int)((k/d)%d);
  render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);Uint32 original=*pixel(output,x,y);CHECK(r->output_live&&font_cached_indices_match());
  unsigned count=allocations;CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(allocations==count);
  SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(fade_mode==1&&font_saved_generation==font_generation);
  for(int step=3;step;step--){Uint32 prior=*pixel(output,x,y);for(unsigned i=0;i<256;i++)rgb_palette[i]=channel_step(rgb_palette[i],0,step)&0xffffffu;render_mirror_fade_step(step);CHECK(*pixel(output,x,y)==channel_step(prior,0,step));CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));}
  SDL_Color target[256];for(unsigned i=0;i<256;i++)target[i]=(SDL_Color){normal_palette[i]>>16,normal_palette[i]>>8,normal_palette[i],255};render_mirror_fade_start(target,NULL,0,255);CHECK(fade_mode==3);
  for(int step=3;step;step--){for(unsigned i=0;i<256;i++)rgb_palette[i]=channel_step(rgb_palette[i],normal_palette[i],step)&0xffffffu;render_mirror_fade_step(step);}CHECK(*pixel(output,x,y)==original);
  ((Uint8 *)VGAScreenSeg->pixels)[0]^=1;CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!ready&&!last_output_valid&&!have_fade_saved);
 }
 puts("PASS shared scene-font cache, 4x/8x fade/restore, repeated Present, final-index mutation rejection");
}
static void fade_suite(const char *root)
{
 for(unsigned solid=0;solid<=255;solid+=255) {
  setup(root,4);grant();frame(MIRROR_OUTPUT_UNKNOWN);unsigned cell=0;while(cell<64000&&!hud_output_owner[cell])++cell;CHECK(cell<64000);
  int x=(cell%320)*4,y=(cell/320)*4;Uint32 original=*pixel(output,x,y);SDL_Color color={solid,solid,solid,255};render_mirror_fade_start(NULL,&color,0,255);CHECK(fade_mode==(solid?2:1)&&have_fade_saved);
  for(int steps=3;steps;steps--){Uint32 prior=*pixel(output,x,y);for(unsigned i=0;i<256;i++)rgb_palette[i]=channel_step(rgb_palette[i],solid?0xffffffu:0,steps)&0xffffffu;render_mirror_fade_step(steps);CHECK(*pixel(output,x,y)==channel_step(prior,solid?0xffffffu:0,steps));CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));}
  SDL_Color colors[256];for(unsigned i=0;i<256;i++)colors[i]=(SDL_Color){normal_palette[i]>>16,normal_palette[i]>>8,normal_palette[i],255};render_mirror_fade_start(colors,NULL,0,255);CHECK(fade_mode==3);
  for(int steps=3;steps;steps--){for(unsigned i=0;i<256;i++)rgb_palette[i]=channel_step(rgb_palette[i],normal_palette[i],steps)&0xffffffu;render_mirror_fade_step(steps);}CHECK(*pixel(output,x,y)==original);
 }
 puts("PASS cached static HUD black/white fades, exact restoration, repeated Present non-replay");
}
static void selected_font_pixel_with_lower(int *x,int *y,int *sx,int *sy,unsigned *base,bool require_lower)
{
 FontScene *r=font_scenes+1;int d=game_probe_density;
 for(unsigned k=0;k<r->used;k++)if(font_owner[r->offset+k]&&(!require_lower||font_lower_owner[r->offset+k])) {
  unsigned cell=k/(d*d);int px=r->rect.x+(int)(cell%r->rect.w),py=r->rect.y+(int)(cell/r->rect.w);
  int subx=(int)(k%d),suby=(int)((k/d)%d);Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[py*320+px-24];
  if(*pixel(canvas,px*d+subx,py*d+suby)!=palette_rgb(index)) {*x=px;*y=py;*sx=subx;*sy=suby;*base=r->offset+cell*d*d;return;}
 }
 CHECK(false);
}
static void selected_font_pixel(int *x,int *y,int *sx,int *sy,unsigned *base)
{selected_font_pixel_with_lower(x,y,sx,sy,base,false);}
static void final_same_index_suite(const char *root)
{
 for(int d=4;d<=8;d+=4)for(unsigned legacy=0;legacy<2;legacy++)for(unsigned after=0;after<4;after++)for(unsigned rect=0;rect<2;rect++) {
  setup(root,d);if(legacy){manual_hd_enabled=true;lvlFileNum=9;}grant();render_mirror_begin();
  if(legacy)for(int y=6*d;y<19*d;y++)for(int x=26*d;x<100*d;x++){*pixel(canvas,x,y)=0xffab12cdu;hd_owner[y*canvas->w+x]=1;}
  draw_scene_text(1);
  int x,y,sx,sy;unsigned base;selected_font_pixel_with_lower(&x,&y,&sx,&sy,&base,legacy&&after>=2);
  Uint8 *address=(Uint8 *)VGAScreenSeg->pixels+y*320+x-24;Uint8 unchanged=*address;
  if(after){render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(font_scenes[1].output_live);CHECK(*pixel(output,(x-24)*d+sx,y*d+sy)!=palette_rgb(unchanged));}
  SDL_Color black={0,0,0,255};
  if(after==2){render_mirror_fade_start(NULL,&black,0,255);CHECK(have_fade_saved&&fade_mode==1);for(unsigned i=0;i<256;i++)rgb_palette[i]=channel_step(rgb_palette[i],0,2)&0xffffffu;render_mirror_fade_step(2);}
  if(after==3){CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!ready&&last_output_valid);}
  SDL_Rect touched=rect?(SDL_Rect){font_scenes[1].rect.x-24,font_scenes[1].rect.y,font_scenes[1].rect.w,font_scenes[1].rect.h}:(SDL_Rect){x-24,y,1,1};
  if(rect)render_mirror_rect(VGAScreenSeg,&touched);
  else render_mirror_pixel(VGAScreenSeg,address,unchanged,MIRROR_NORMAL);
  CHECK(*address==unchanged);
  if(!after)render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
  CHECK(!font_scenes[1].output_live||!memchr(font_owner+base,1,(size_t)d*d));
  CHECK(hud_output_generation&&memchr(hud_output_owner,1,sizeof(hud_output_owner)));
  CHECK(!last_output_valid||*pixel(output,(x-24)*d+sx,y*d+sy)==palette_rgb(unchanged));
  if(rect)for(int cy=touched.y;cy<touched.y+touched.h;cy++)for(int cx=touched.x;cx<touched.x+touched.w;cx++)for(int yy=0;yy<d;yy++)for(int xx=0;xx<d;xx++) {
   Uint8 value=((Uint8 *)VGAScreenSeg->pixels)[cy*320+cx];CHECK(*pixel(output,cx*d+xx,cy*d+yy)==palette_rgb(value));CHECK(!hd_owner[(cy*d+yy)*canvas->w+(cx+24)*d+xx]);
   if(after==2){CHECK(have_fade_saved);CHECK(*pixel(fade_saved,cx*d+xx,cy*d+yy)==(0xff000000u|normal_palette[value]));}
  }
  if(after==2){CHECK(have_fade_saved);CHECK(*pixel(fade_saved,(x-24)*d+sx,y*d+sy)==(0xff000000u|normal_palette[unchanged]));}
  if(after==3){render_mirror_fade_start(NULL,&black,0,255);CHECK(have_fade_saved&&fade_mode==1);for(unsigned i=0;i<256;i++)rgb_palette[i]=channel_step(rgb_palette[i],0,2)&0xffffffu;render_mirror_fade_step(2);CHECK(*pixel(output,(x-24)*d+sx,y*d+sy)==palette_rgb(unchanged));}
  if(after>=2){SDL_Color target[256];for(unsigned i=0;i<256;i++)target[i]=(SDL_Color){normal_palette[i]>>16,normal_palette[i]>>8,normal_palette[i],255};render_mirror_fade_start(target,NULL,0,255);CHECK(fade_mode==3);memcpy(rgb_palette,normal_palette,sizeof(rgb_palette));render_mirror_fade_step(1);CHECK(*pixel(output,(x-24)*d+sx,y*d+sy)==palette_rgb(unchanged));}
  if(ready){CHECK(render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));}
 }
 puts("PASS final-surface same-index pixel/rect writes before/after finish, mid-fade, and after consumed Present; current/saved cache stays classic with authored legacy underlay at 4x/8x");
}
static void active_mapping_suite(const char *root)
{
 for(int d=4;d<=8;d+=4)for(unsigned legacy=0;legacy<2;legacy++) {
  setup(root,d);if(legacy){manual_hd_enabled=true;lvlFileNum=9;}grant();render_mirror_begin();draw_scene_text(1);
  int x,y,sx,sy;unsigned base;selected_font_pixel(&x,&y,&sx,&sy,&base);
  Uint8 *address=(Uint8 *)VGAScreenSeg->pixels+y*320+x-24;*address^=1;
  render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);static_owners();CHECK(!font_scenes[1].output_live);
  CHECK(*pixel(output,(x-24)*d+sx,y*d+sy)==palette_rgb(*address));
 }
 puts("PASS identical final-index font witness independent of inactive/active legacy scene admission at 4x/8x");
}
static void hud_palette_boundary_suite(const char *root)
{
 for(int d=4;d<=8;d+=4)for(unsigned between=0;between<2;between++)for(unsigned unrelated=0;unrelated<2;unrelated++) {
  setup(root,d);grant();if(between)render_mirror_begin();rgb_palette[unrelated?255:108]^=1;if(!between)render_mirror_begin();
  render_mirror_finish(MIRROR_OUTPUT_UNKNOWN,0,0);
  if(unrelated){CHECK(hud_output_generation&&memchr(hud_output_owner,1,sizeof(hud_output_owner)));CHECK(ready&&last_output_valid);verify_static_samples();}
  else {CHECK(!hud_output_generation&&!memchr(hud_output_owner,1,sizeof(hud_output_owner)));for(unsigned y=0;y<200;y++)for(unsigned x=0;x<320;x++)if((x>=264||y>=184)&&((Uint8 *)VGAScreenSeg->pixels)[y*320+x]==108)CHECK(*pixel(output,x*d,y*d)==palette_rgb(108));}
 }
 puts("PASS HUD1 source-used index108 palette changes reject before/between begin-finish; unrelated index255 preserves HUD1 at 4x/8x");
}
int main(int argc,char **argv)
{
 setvbuf(stdout,NULL,_IOLBF,0);CHECK(argc==4);load_original();
 if(!strcmp(argv[3],"all")){stage_suite(argv[1]);coexistence_suite(argv[1]);scene_suite(argv[1]);same_index_suite(argv[1]);lifecycle_suite(argv[1],argv[2]);feature_off_suite(argv[1]);isolation_suite(argv[1],argv[2]);mutation_suite(argv[1]);fade_suite(argv[1]);scene_cache_suite(argv[1]);final_same_index_suite(argv[1]);active_mapping_suite(argv[1]);hud_palette_boundary_suite(argv[1]);}
 else if(!strcmp(argv[3],"palette-boundary"))hud_palette_boundary_suite(argv[1]);
 else if(!strcmp(argv[3],"final-writes"))final_same_index_suite(argv[1]);
 else if(!strcmp(argv[3],"active-map"))active_mapping_suite(argv[1]);
 else if(!strcmp(argv[3],"density")){setup(argv[1],4);grant();frame(MIRROR_OUTPUT_UNKNOWN);game_probe_density=8;render_mirror_begin();CHECK(!shared_hud_frame&&!ready);}
 else CHECK(false);
 cleanup();for(unsigned t=0;t<8;t++)for(unsigned i=0;i<sprite_table[t].count;i++)free(sprite_table[t].sprite[i].data);
 printf("PASS shared-HUD reconstruction: %u checks; original bytes were never persisted\n",checks);return 0;
}
