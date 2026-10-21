#define render_mirror_green_create_begin(...) (0)
#define render_mirror_green_create_end(...) ((void)0)
#define render_mirror_green_shot_allocated(...) ((void)0)
#define render_mirror_green_shot_initialized(...) ((void)0)
#define render_mirror_green_trail_begin(...) ((void)0)
#define render_mirror_green_trail_end(...) ((void)0)
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Current-production Cash25BodyAndValue7 observer. SDL is a bounded structural shim.
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
/* Green is disabled only in this isolated prior-family harness. */
static bool global_green_frame,global_green_fault,global_green_cached;
static Uint8 *global_green_owner,*global_green_foreign;
static bool global_green_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_green_palette_matches(void){return true;}
static bool global_green_requested(void){return false;}
static bool global_green_is_index(unsigned index){return false;}
static bool global_green_surface_matches(void){return true;}
static bool global_green_final_surface_matches(void){return true;}
static void global_green_shutdown(void){}
static void global_green_reset(void){}
static void global_green_frame_begin(void){}
static bool global_green_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_green_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_green_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_green_end(void){}
static bool global_green_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_green_finish_proof(void){return true;}
static bool global_green_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_green_check_cache(void){}
static bool global_green_fade_buffer_safe(void){return true;}
static bool global_green_fade_capture(void){return true;}
static bool global_green_fade_step_valid(int steps){return true;}
static void global_green_fade_palette(void){}
#define render_mirror_green_smoke_allocated(...) ((void)0)
#define render_mirror_green_smoke_initialized(...) ((void)0)

/* White smoke disabled only in this isolated existing-family harness. */
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

static bool global_rotor_frame,global_rotor_fault,global_rotor_cached;
static Uint8 *global_rotor_owner,*global_rotor_foreign;
static bool global_rotor_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_rotor_palette_matches(void){return true;}
static bool global_rotor_requested(void){return false;}
static bool global_rotor_is_index(unsigned index){return false;}
static bool global_rotor_surface_matches(void){return true;}
static bool global_rotor_final_surface_matches(void){return true;}
static void global_rotor_shutdown(void){}
static void global_rotor_reset(void){}
static void global_rotor_frame_begin(void){}
static bool global_rotor_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_rotor_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_rotor_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_rotor_end(void){}
static bool global_rotor_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_rotor_finish_proof(void){return true;}
static bool global_rotor_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_rotor_check_cache(void){}
static bool global_rotor_fade_buffer_safe(void){return true;}
static bool global_rotor_fade_capture(void){return true;}
static bool global_rotor_fade_step_valid(int steps){return true;}
static void global_rotor_fade_palette(void){}

#define render_mirror_rotor_enemy_allocated(...) ((void)0)
#define render_mirror_rotor_enemy_initialized(...) ((void)0)
#define render_mirror_rotor_enemy_animated(...) ((void)0)

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
static void render_mirror_hitflare_explosion_allocated(unsigned slot){}
static void render_mirror_hitflare_explosion_initialized(unsigned slot,unsigned type){}
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
/* This family is disabled in this isolated regression harness. */
static bool global_shield_frame,global_shield_fault,global_shield_cached;
static Uint8 *global_shield_owner,*global_shield_foreign;
static bool global_shield_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_shield_palette_matches(void){return true;}
static bool global_shield_requested(void){return false;}
static bool global_shield_is_index(unsigned index){return false;}
static bool global_shield_surface_matches(void){return true;}
static bool global_shield_final_surface_matches(void){return true;}
static void global_shield_shutdown(void){}
static void global_shield_reset(void){}
static void global_shield_frame_begin(void){}
static bool global_shield_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_shield_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_shield_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_shield_end(void){}
static bool global_shield_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_shield_finish_proof(void){return true;}
static bool global_shield_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_shield_check_cache(void){}
static bool global_shield_fade_buffer_safe(void){return true;}
static bool global_shield_fade_capture(void){return true;}
static bool global_shield_fade_step_valid(int steps){return true;}
static void global_shield_fade_palette(void){}

static void render_mirror_explosion_allocated(unsigned slot){}
static void render_mirror_explosion_initialized(unsigned slot,unsigned type){}
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
static bool global_talon_frame,global_cash25_frame,global_cash25_fault,global_talon_shield_dependency;
static Uint8 *global_cash25_owner,*global_cash25_foreign;
static bool global_cash25_source_matches(Sprite2_array);
static bool global_cash25_palette_matches(void);
static Sprite2_array spriteSheet9,spriteSheet11,explosionSpriteSheet;
#define MAX_EXPLOSIONS 200
typedef int16_t JE_integer;typedef unsigned short JE_word;typedef unsigned char JE_byte;
typedef struct {JE_byte ttl;JE_integer x,y;JE_word sprite;bool followPlayer,fixedPosition;JE_integer deltaY;} Explosion;
typedef int8_t JE_shortint;typedef bool JE_boolean;
#define ENEMY_NUM 1850
#include "cash25_identity_types.h"
static JE_EnemyDatType enemyDat;
static JE_MultiEnemyType enemy;
static Uint8 enemyAvail[100],original_record[385];
static JE_word tempMapXOfs;
static Explosion explosions[MAX_EXPLOSIONS];
static JE_word explodeMove;
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
#include "global_cash25_mirror.inc"
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
#include "allocation.inc"
static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static void record_load_one(const Uint8 *b,unsigned record)
{
 size_t n=0;
#define RBYTE(v) do {(v)=b[n++];} while(0)
#define RWORD(v) do {(v)=(unsigned)b[n]|((unsigned)b[n+1]<<8);n+=2;} while(0)
 RBYTE(enemyDat[record].ani);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[record].tur[i]);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[record].freq[i]);
 RBYTE(enemyDat[record].xmove);RBYTE(enemyDat[record].ymove);RBYTE(enemyDat[record].xaccel);RBYTE(enemyDat[record].yaccel);
 RBYTE(enemyDat[record].xcaccel);RBYTE(enemyDat[record].ycaccel);RWORD(enemyDat[record].startx);RWORD(enemyDat[record].starty);
 RBYTE(enemyDat[record].startxc);RBYTE(enemyDat[record].startyc);RBYTE(enemyDat[record].armor);RBYTE(enemyDat[record].esize);
 for(unsigned i=0;i<20;i++)RWORD(enemyDat[record].egraphic[i]);
 RBYTE(enemyDat[record].explosiontype);RBYTE(enemyDat[record].animate);RBYTE(enemyDat[record].shapebank);
 RBYTE(enemyDat[record].xrev);RBYTE(enemyDat[record].yrev);RWORD(enemyDat[record].dgr);RBYTE(enemyDat[record].dlevel);
 RBYTE(enemyDat[record].dani);RBYTE(enemyDat[record].elaunchfreq);RWORD(enemyDat[record].elaunchtype);
 RWORD(enemyDat[record].value);RWORD(enemyDat[record].eenemydie);
#undef RBYTE
#undef RWORD
 CHECK(n==77);
}

static void record_load(const Uint8 *b)
{for(unsigned p=0;p<5;p++)record_load_one(b+p*77,391+p);}
static unsigned test_profile;
static const unsigned test_body_first[5]={7,26,20,32,14};
static const unsigned test_popup_index[5]={185,204,223,169,188};
static const unsigned test_body_count[5]={6,6,6,5,5};
static const unsigned test_resource_offset[5]={0,7,14,21,27};

static void load_original(void)
{
 Uint32 n;read_exact(&n,4);CHECK(n==33484);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 read_exact(&n,4);CHECK(n==17810);explosionSpriteSheet.size=n;explosionSpriteSheet.data=malloc(n);CHECK(explosionSpriteSheet.data);read_exact(explosionSpriteSheet.data,n);
 read_exact(&n,4);CHECK(n==29032);spriteSheet11.size=n;spriteSheet11.data=malloc(n);CHECK(spriteSheet11.data);read_exact(spriteSheet11.data,n);
 read_exact(original_record,sizeof(original_record));record_load(original_record);
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
static const char *valid_root,*fixture_root;
static Uint8 *source_backup,*body_backup;
static Uint8 *reference_frames[33];
static void load_frames(void)
{
 for(unsigned i=0;i<33;i++) {
  if(!global_cash_resource_id(i))continue;
  const GlobalAssetResource *r=NULL;for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_cash_resource_id(i))r=global_asset_resources+j;
  CHECK(r);char p[2048];snprintf(p,sizeof(p),"%s/%s",valid_root,r->path);FILE *f=fopen(p,"rb");CHECK(f);CHECK(!fseek(f,28,SEEK_SET));reference_frames[i]=malloc(96*112*4);CHECK(reference_frames[i]);CHECK(fread(reference_frames[i],1,96*112*4,f)==96*112*4);CHECK(fgetc(f)==EOF);fclose(f);
 }
}
static void setup(const char *root,int d)
{
 ++cases;global_cash25_shutdown();global_talon_shutdown();
 free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);fade_saved=NULL;
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 game_probe_density=d;canvas=make_surface(320*d,200*d,32);output=make_surface(320*d,200*d,32);game_screen=make_surface(320,200,8);VGAScreenSeg=make_surface(320,200,8);VGAScreen=game_screen;
 size_t n=(size_t)canvas->w*canvas->h;hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,2);green_under=calloc(n,4);green_under_owner=calloc(n,1);CHECK(hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));record_load(original_record);memcpy(spriteSheet11.data,body_backup,spriteSheet11.size);memset(explosions,0,sizeof(explosions));memcpy(explosionSpriteSheet.data,source_backup,explosionSpriteSheet.size);
 game_probe_missing=game_probe_invalid=game_probe_original_reference=false;twoPlayerMode=false;shared_hud_frame=false;
 ready=last_output_valid=have_fade_saved=false;fade_mode=0;explodeMove=0;player[0].x=120;player[0].y=90;player[1].x=160;player[1].y=90;
 CHECK(render_mirror_set_global_assets(root));set_background();++mirror_logic_tick;global_talon_frame_begin();global_cash25_frame_begin();CHECK(global_cash25_frame);
}
static void next_frame(void)
{set_background();++mirror_logic_tick;global_talon_frame_begin();global_cash25_frame_begin();CHECK(global_cash25_frame);}
/* Every accepted popup birth uses the actual allocator with fixed types36–40. */
static void birth(unsigned slot,unsigned role)
{
 for(unsigned i=0;i<slot;i++)if(!explosions[i].ttl)explosions[i].ttl=10;
 explosions[slot].ttl=0;JE_setupExplosion(103,78,0,36+test_profile,true,false);(void)role;
 CHECK(global_cash25_slots[slot].role);CHECK(explosions[slot].ttl==8);CHECK(global_cash25_slots[slot].next_ttl==8);
}
static int start_draw(unsigned slot,int style)
{Explosion *e=explosions+slot;return render_mirror_global_cash25_value(game_screen,e->x,e->y,explosionSpriteSheet,test_popup_index[test_profile],style,slot);}
static void emit(unsigned slot,int style)
{
 Explosion *e=explosions+slot;Uint8 color[168],mask[168];CHECK(reference_decode(explosionSpriteSheet,e->sprite+1,color,mask,NULL));
 for(unsigned i=0;i<168;i++)if(mask[i]) {
  int x=e->x+i%12,y=e->y+i/12;if(x<0||x>=320||y<0||y>=200)continue;
  Uint8 *at=index_at(x,y),source=color[i];
  *at=style==MIRROR_NORMAL?source:style==MIRROR_BLEND?(source&240)|(((source&15)+(*at&15))/2):(*at&240)|((*at&15)/2);
  render_mirror_pixel(game_screen,at,source,style);
 }
 global_cash25_end();global_talon_end();--e->ttl;CHECK(!global_cash25_fault);
}
static unsigned owner_count(void)
{unsigned n=0;for(size_t i=0;i<global_cash25_capacity;i++)n+=global_cash25_owner[i]!=0;return n;}

static void final_copy(void)
{for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);upscale(output,VGAScreenSeg);}
static Uint32 last_output_palette[256],hud_output_palette[256],component_output_palette[256],indicator_output_palette[256],fixed_text_output_palette[256];
#define mirror_enabled() false
#define render_mirror_hud_reset() ((void)0)
#define hud_check_mode() ((void)0)
#define shared_hud_requested() false
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
 setup(valid_root,d);birth(0,1);CHECK(start_draw(0,0)==1);emit(0,0);final_copy();CHECK(global_cash25_compose(MIRROR_OUTPUT_ORDINARY,0,0));
 memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));ready=last_output_valid=true;
 SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(fade_saved&&fade_mode==1&&have_fade_saved&&last_output_valid&&global_cash25_cached);
}
static void fade_cases(void)
{
 for(int d=4;d<=8;d+=4) {
  prepare_fade(d);size_t count=(size_t)output->w*output->h;Uint32 *before=malloc(count*4);CHECK(before);memcpy(before,output->pixels,count*4);
  for(unsigned i=0;i<256;i++){Uint32 v=rgb_palette[i],next=0;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;next|=(Uint32)(c+(0-c)/2)<<shift;}rgb_palette[i]=next;}
  render_mirror_fade_step(2);CHECK(ready&&global_cash25_cached&&last_output_valid);
  for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
   bool owned=x<264*d&&y<184*d&&hd_owner[(size_t)y*canvas->w+x+24*d];Uint32 want=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d]);
   if(owned){Uint32 v=before[(size_t)y*output->w+x];want=0xff000000u;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;want|=(Uint32)(c+(0-c)/2)<<shift;}}
   CHECK(((Uint32 *)output->pixels)[(size_t)y*output->w+x]==want);
  }
  global_cash25_check_cache();CHECK(global_cash25_cached);free(before);
 }
 for(unsigned bad=0;bad<11;bad++) {
  prepare_fade(4);SDL_Surface c=*canvas,o=*output,f=*fade_saved,v=*VGAScreenSeg;SDL_PixelFormat fmt=*fade_saved->format;
  switch(bad){case 0:fade_saved->pixels=NULL;break;case 1:fade_saved->pixels=(Uint8 *)canvas->pixels+4;break;case 2:fade_saved->pitch++;break;case 3:fade_saved->w--;break;case 4:fade_saved->format->BytesPerPixel=1;break;case 5:canvas->pitch++;break;case 6:output->pixels=NULL;break;case 7:VGAScreenSeg->pitch++;break;case 8:rgb_palette[255]^=1;break;case 9:game_probe_density=8;break;case 10:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;}
  render_mirror_fade_step(2);CHECK(!ready&&!last_output_valid&&!global_cash25_cached&&!fade_mode&&!have_fade_saved);
  *canvas=c;*output=o;*fade_saved=f;*VGAScreenSeg=v;*fade_saved->format=fmt;game_probe_density=4;
 }
}
static void cache_and_leases(void)
{
 for(unsigned bad=0;bad<10;bad++) {
  setup(valid_root,4);birth(0,1);CHECK(start_draw(0,0)==1);emit(0,0);
  for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);
  CHECK(global_cash25_compose(MIRROR_OUTPUT_ORDINARY,0,0));memcpy(last_output_indices,VGAScreenSeg->pixels,64000);ready=last_output_valid=true;
  SDL_Surface a=*canvas,b=*output,c=*game_screen,f=*VGAScreenSeg;SDL_PixelFormat fmt=*canvas->format;
  switch(bad){case 0:canvas->pitch++;break;case 1:output->pixels=NULL;break;case 2:game_screen->pitch++;break;case 3:VGAScreenSeg->pixels=NULL;break;case 4:canvas->format->BytesPerPixel=1;break;case 5:game_probe_density=8;break;case 6:rgb_palette[0]^=1;break;case 7:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;case 8:global_asset_directory[0]=0;break;case 9:explosionSpriteSheet.size--;break;}
  global_cash25_check_cache();CHECK(!global_cash25_cached&&!ready&&!last_output_valid);
  *canvas=a;*output=b;*game_screen=c;*VGAScreenSeg=f;*canvas->format=fmt;game_probe_density=4;if(bad==9)explosionSpriteSheet.size++;
 }
}
static void geometry_cases(void)
{
 for(unsigned bad=0;bad<8;bad++) {
  setup(valid_root,4);global_cash25_reset();SDL_Surface c=*canvas,o=*output,g=*game_screen,v=*VGAScreenSeg;
  switch(bad){case 0:canvas->pixels=(Uint8 *)canvas->pixels+1;break;case 1:output->pixels=(Uint8 *)canvas->pixels+4;break;case 2:game_screen->pixels=VGAScreenSeg->pixels;break;case 3:canvas->pitch++;break;case 4:VGAScreenSeg->pixels=canvas->pixels;break;case 5:output->pitch=1;break;case 6:game_screen->w--;break;case 7:game_probe_density=2;break;}
  global_cash25_frame_begin();CHECK(!global_cash25_frame);unsigned opens=asset_opens;birth(0,1);CHECK(start_draw(0,0)==0);CHECK(asset_opens==opens);
  *canvas=c;*output=o;*game_screen=g;*VGAScreenSeg=v;game_probe_density=4;
 }
}
static void emit_bank(Sprite2_array bank,unsigned index,int x,int y,int style)
{
 Uint8 color[168],mask[168];CHECK(reference_decode(bank,index,color,mask,NULL));
 for(unsigned i=0;i<168;i++)if(mask[i]){
  int xx=x+i%12,yy=y+i/12;if(xx<0||xx>=320||yy<0||yy>=200)continue;
  Uint8 *p=index_at(xx,yy),source=color[i];
  *p=style==MIRROR_NORMAL?source:(source&240)|(((source&15)+(*p&15))/2);
  render_mirror_pixel(game_screen,p,source,style);
 }
 global_cash25_end();CHECK(!global_cash25_fault);
}
static void body_birth(unsigned slot)
{
 enemyAvail[slot]=1;render_mirror_cash25_enemy_allocated(enemy+slot,(391+test_profile),0);
 struct JE_SingleEnemyType *e=enemy+slot;memset(e,0,sizeof(*e));
 e->enemytype=(391+test_profile);e->enemydatofs=&enemyDat[(391+test_profile)];e->sprite2s=&spriteSheet11;e->scoreitem=true;
 e->armorleft=255;e->ani=enemyDat[391+test_profile].ani;e->animin=1;e->aniactive=1;e->evalue=enemyDat[391+test_profile].value;
 memcpy(e->egr,enemyDat[(391+test_profile)].egraphic,sizeof(e->egr));e->ex=103;e->ey=78;
 render_mirror_cash25_enemy_initialized(e,(391+test_profile),2);enemyAvail[slot]=2;
 CHECK(global_cash25_body_slots[slot].role);
}
static G101EnemyContext body_context(unsigned slot)
{return (G101EnemyContext){(391+test_profile),slot,enemyAvail[slot],enemy[slot].size,enemy[slot].scoreitem,enemy[slot].edamaged,true,false};}
static int body_draw(unsigned slot,unsigned phase)
{
 enemy[slot].enemycycle=phase+1;render_mirror_cash25_enemy_animated(slot);G101EnemyContext c=body_context(slot);
 return render_mirror_global_cash25_body(game_screen,enemy[slot].ex+tempMapXOfs,enemy[slot].ey,spriteSheet11,enemyDat[391+test_profile].egraphic[phase],0,0,&c);
}
/* Independent scalar HSV value arithmetic, alpha only covers authored support. */
static Uint32 oracle_value(Uint32 prior,const Uint8 *a)
{
 unsigned peak=0,dest=0;for(unsigned c=0;c<3;c++){if(a[c]>peak)peak=a[c];unsigned v=(prior>>(16-8*c))&255;if(v>dest)dest=v;}
 unsigned next=(peak+dest+1)/2;Uint8 b[4];for(unsigned c=0;c<3;c++)b[c]=peak?(a[c]*next+peak/2)/peak:0;b[3]=a[3];
 return reference_blend(prior,b,a[3]);
}
static void pixels(unsigned phase,int style,int x,int y)
{
 int d=game_probe_density;Uint8 col[168],mask[168];CHECK(reference_decode(phase==test_body_count[test_profile]?explosionSpriteSheet:spriteSheet11,phase==test_body_count[test_profile]?test_popup_index[test_profile]:phase+test_body_first[test_profile],col,mask,NULL));
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){
  int yy=y*d+ay;if(yy<0||yy>=canvas->h)continue;
  const Uint8 *a=reference_frames[test_resource_offset[test_profile]+phase]+4*((ay*8/d)*96+ax*8/d);Uint32 want=palette_rgb(0x1b);
  if(a[3])want=style==MIRROR_BLEND?oracle_value(want,a):reference_blend(want,a,a[3]);
  CHECK(*rgba_at(x*d+ax,yy)==want);
  CHECK((global_cash25_owner[(size_t)yy*canvas->w+x*d+ax]!=0)==(a[3]||mask[(ay/d)*12+ax/d]));
 }
}
static void all_phases(void)
{
 for(test_profile=0;test_profile<5;test_profile++)for(int d=4;d<=8;d+=4){
  setup(valid_root,d);body_birth(0);
  for(unsigned n=0;n<3*enemyDat[391+test_profile].ani;n++){
   if(n)next_frame();unsigned phase=n%enemyDat[391+test_profile].ani;unsigned index=enemyDat[391+test_profile].egraphic[phase];unsigned resource=index-test_body_first[test_profile];CHECK(body_draw(0,phase)==1);pixels(resource,0,103,78);
   emit_bank(spriteSheet11,index,103,78,0);pixels(resource,0,103,78);CHECK(global_cash25_finish_proof());
  }
  for(int style=0;style<2;style++){
   setup(valid_root,d);birth(0,0);
   for(unsigned ttl=8;ttl;ttl--){if(ttl!=8)next_frame();CHECK(explosions[0].ttl==ttl);CHECK(start_draw(0,style)==1);pixels(test_body_count[test_profile],style,103,78);emit(0,style);pixels(test_body_count[test_profile],style,103,78);CHECK(global_cash25_finish_proof());}
  }
 }
 test_profile=0;
}
static void invalid_cases(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned bad=0;bad<22;bad++){
  setup(valid_root,4);if(warm){birth(0,0);CHECK(start_draw(0,0)==1);emit(0,0);next_frame();}
  birth(0,0);Explosion *e=explosions;int x=e->x,y=e->y,style=0;unsigned idx=185,slot=0;Sprite2_array bank=explosionSpriteSheet;SDL_Surface *surface=game_screen;
  switch(bad){case 0:e->ttl=7;break;case 1:e->sprite++;break;case 2:e->fixedPosition=false;break;case 3:e->followPlayer=true;break;case 4:e->deltaY++;break;
   case 5:x++;break;case 6:y++;break;case 7:idx++;break;case 8:style=2;break;case 9:bank.size--;break;case 10:bank.data=spriteSheet11.data;break;
   case 11:surface=VGAScreenSeg;break;case 12:game_probe_missing=true;break;case 13:game_probe_invalid=true;break;case 14:game_probe_original_reference=true;break;
   case 15:rgb_palette[global_cash25_palette[0].index]^=1;break;case 16:enemyDat[391].value++;break;case 17:global_cash25_slots[0].generation++;break;
   case 18:global_cash25_slots[0].tick=mirror_logic_tick;break;case 19:slot=MAX_EXPLOSIONS;break;case 20:game_screen->pitch++;break;case 21:global_cash25_slots[0].next_ttl--;break;}
  unsigned opens=asset_opens;CHECK(render_mirror_global_cash25_value(surface,x,y,bank,idx,style,slot)==(bad==19?-1:0));CHECK(asset_opens==opens);if(bad==20)game_screen->pitch--;
 }
 for(unsigned bad=0;bad<14;bad++){
  setup(valid_root,4);body_birth(0);enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);G101EnemyContext c=body_context(0);unsigned base=7;int part=0,filter=0,x=103,y=78;Sprite2_array bank=spriteSheet11;
  switch(bad){case 0:enemy[0].evalue++;break;case 1:c.type++;break;case 2:c.availability=1;break;case 3:c.damaged=true;break;case 4:c.score_item=false;break;case 5:c.size=1;break;
   case 6:base++;break;case 7:part=1;break;case 8:filter=0x20;break;case 9:bank.data=explosionSpriteSheet.data;break;case 10:x++;break;case 11:y++;break;case 12:enemyDat[391].value++;break;case 13:global_cash25_body_slots[0].generation++;break;}
  unsigned opens=asset_opens;CHECK(render_mirror_global_cash25_body(game_screen,x,y,bank,base,part,filter,&c)==0);CHECK(asset_opens==opens);
 }
 for(unsigned flags=0;flags<4;flags++)for(unsigned delta=0;delta<2;delta++){
  setup(valid_root,4);JE_setupExplosion(103,78,delta,36,flags&1,flags&2);CHECK(global_cash25_slots[0].role==(flags==1&&delta==0));
 }
 const unsigned types[]={0,1,6,35,41,42,98};for(unsigned n=0;n<COUNTOF(types);n++){setup(valid_root,4);JE_setupExplosion(103,78,0,types[n],true,false);CHECK(!global_cash25_slots[0].role);}
}
static void resources(void)
{
 const char *modes[]={"missing","corrupt","header","trailing"};char path[2048];
 for(unsigned mode=0;mode<4;mode++)for(unsigned n=0;n<33;n++)for(unsigned body=0;body<2;body++){
  snprintf(path,sizeof(path),"%s/%s%u",fixture_root,modes[mode],n);setup(path,4);
  if(body){body_birth(0);CHECK(body_draw(0,0)==0);}else{birth(0,0);CHECK(start_draw(0,0)==0);}
  CHECK(!global_cash25_good&&owner_count()==0);unsigned opens=asset_opens;next_frame();birth(0,0);CHECK(start_draw(0,0)==0&&asset_opens==opens);
 }
}
static void source_mutations(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned n=0;n<33;n++){
  setup(valid_root,4);if(warm){birth(0,0);CHECK(start_draw(0,0)==1);emit(0,0);next_frame();}
  unsigned p=0;while(p<4&&n>=test_resource_offset[p+1])p++;unsigned q=n-test_resource_offset[p];Sprite2_array b=q<test_body_count[p]?spriteSheet11:explosionSpriteSheet;unsigned index=q<test_body_count[p]?test_body_first[p]+q:test_popup_index[p];
  Uint8 col[168],mask[168];size_t raw[168];CHECK(reference_decode(b,index,col,mask,raw));size_t pos=raw[first_cell(mask)];Uint8 save=b.data[pos];b.data[pos]^=1;
  birth(0,0);unsigned opens=asset_opens;CHECK(start_draw(0,0)==0&&asset_opens==opens);b.data[pos]=save;
 }
}
static void transactions(void)
{
 for(unsigned bad=0;bad<5;bad++){
  setup(valid_root,4);birth(0,0);CHECK(start_draw(0,0)==1);CHECK(global_cash25_call.left);
  if(!bad)global_cash25_end();else{
   Uint8 color[168],mask[168];CHECK(reference_decode(explosionSpriteSheet,185,color,mask,NULL));unsigned n=first_cell(mask);int x=103+n%12,y=78+n/12;Uint8 *p=index_at(x,y);
   if(bad==4)p=index_at(0,0);*p=bad==1?color[n]^1:color[n];render_mirror_pixel(game_screen,p,color[n],bad==2?MIRROR_BLEND:0);if(bad==3)render_mirror_pixel(game_screen,p,color[n],0);
  }
  CHECK(global_cash25_fault&&!global_cash25_call.live&&owner_count()==0);
 }
}
static void observed_revoke_then_restore(void)
{
 for(unsigned transfer=0;transfer<2;transfer++)for(unsigned bad=0;bad<9;bad++){
  setup(valid_root,4);birth(0,0);CHECK(start_draw(0,0)==1);emit(0,0);final_copy();if(transfer)memset(global_cash25_owner,0,global_cash25_capacity);CHECK(global_cash25_finish_proof());
  SDL_Surface c=*canvas,v=*VGAScreenSeg;Uint8 color[168],mask[168];size_t raw[168];CHECK(reference_decode(explosionSpriteSheet,185,color,mask,raw));size_t pos=raw[first_cell(mask)];Uint8 save=explosionSpriteSheet.data[pos];
  Uint32 pal=rgb_palette[global_cash25_palette[0].index];
  switch(bad){case 0:explosionSpriteSheet.data[pos]^=1;break;case 1:rgb_palette[global_cash25_palette[0].index]^=1;break;case 2:game_probe_missing=true;break;case 3:game_probe_invalid=true;break;case 4:game_probe_original_reference=true;break;case 5:canvas->pitch+=4;break;case 6:VGAScreenSeg->pitch++;break;case 7:enemyDat[391].value++;break;case 8:spriteSheet11.size--;break;}
  CHECK(render_mirror_global_cash25_value(game_screen,0,0,explosionSpriteSheet,185,0,MAX_EXPLOSIONS)==-1);
  *canvas=c;*VGAScreenSeg=v;explosionSpriteSheet.data[pos]=save;rgb_palette[global_cash25_palette[0].index]=pal;record_load(original_record);if(bad==8)spriteSheet11.size++;
  game_probe_missing=game_probe_invalid=game_probe_original_reference=false;
  CHECK(global_cash25_fault&&!global_cash25_finish_proof());
  next_frame();birth(0,0);CHECK(start_draw(0,0)==1);emit(0,0);CHECK(global_cash25_finish_proof());
 }
}
static void observed_dead_value(void)
{
 for(unsigned bad=0;bad<6;bad++) {
  setup(valid_root,4);birth(0,0);CHECK(start_draw(0,0)==1);emit(0,0);
  Explosion saved=explosions[0];
  if(bad==0)explosions[0].ttl=0;
  if(bad==1)explosions[0].sprite=185;
  if(bad==2)explosions[0].fixedPosition=false;
  if(bad==3)explosions[0].followPlayer=true;
  if(bad==4)explosions[0].deltaY=1;
  if(bad==5)explosions[0].ttl=8;
  next_frame();explosions[0]=saved;
  CHECK(!global_cash25_slots[0].role);CHECK(start_draw(0,0)==-1);
 }
}
static void lifecycle(void)
{
 setup(valid_root,4);birth(0,0);CHECK(start_draw(0,0)==1);emit(0,0);CHECK(start_draw(0,0)==0);next_frame();CHECK(start_draw(0,0)==-1);
 setup(valid_root,4);birth(0,0);explosions[0].ttl=0;JE_setupExplosion(103,78,0,1,false,false);CHECK(!global_cash25_slots[0].role);
 setup(valid_root,4);for(unsigned i=0;i<MAX_EXPLOSIONS;i++)explosions[i].ttl=1;JE_setupExplosion(103,78,0,36,true,false);for(unsigned i=0;i<MAX_EXPLOSIONS;i++)CHECK(!global_cash25_slots[i].role);
 setup(valid_root,4);body_birth(0);CHECK(body_draw(0,0)==1);emit_bank(spriteSheet11,7,103,78,0);CHECK(body_draw(0,0)==0);next_frame();CHECK(body_draw(0,1)==0);
}
static void profile_separation(void)
{
 for(unsigned p=0;p<5;p++)for(unsigned q=0;q<5;q++)if(p!=q){
  test_profile=p;setup(valid_root,4);birth(0,0);
  CHECK(render_mirror_global_cash25_value(game_screen,103,78,explosionSpriteSheet,test_popup_index[q],0,0)==0);
  CHECK(!global_cash25_slots[0].role);
  setup(valid_root,4);body_birth(0);enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);
  G101EnemyContext c=body_context(0);c.type=391+q;
  CHECK(render_mirror_global_cash25_body(game_screen,103,78,spriteSheet11,test_body_first[q],0,0,&c)==0);
  CHECK(!global_cash25_body_slots[0].role);
  setup(valid_root,4);birth(0,0);enemyDat[391+q].value++;
  CHECK(start_draw(0,0)==0); /* No profile can borrow a mutated sibling source. */
 }
 test_profile=0;
}
/* Record509 may call the canonical fixed100 popup but cannot borrow gem body. */
static void gem_phase_and_alias_cases(void)
{
 for(test_profile=3;test_profile<5;test_profile++){
  setup(valid_root,4);body_birth(0);CHECK(body_draw(0,0)==1);
  emit_bank(spriteSheet11,test_body_first[test_profile],103,78,0);next_frame();
  CHECK(body_draw(0,2)==0);CHECK(!global_cash25_body_slots[0].role);
  setup(valid_root,4);body_birth(0);
  for(unsigned phase=0;phase<16;phase++){
   if(phase)next_frame();CHECK(body_draw(0,phase)==1);
   emit_bank(spriteSheet11,enemyDat[391+test_profile].egraphic[phase],103,78,0);
  }
  next_frame();enemy[0].enemycycle=17;render_mirror_cash25_enemy_animated(0);CHECK(!global_cash25_body_slots[0].role);
  setup(valid_root,4);body_birth(0);enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);
  G101EnemyContext c=body_context(0);c.type=509;
  CHECK(render_mirror_global_cash25_body(game_screen,103,78,spriteSheet11,test_body_first[test_profile],0,0,&c)==0);
  CHECK(!global_cash25_body_slots[0].role);
 }
 test_profile=3;setup(valid_root,4); /* No gem body allocation is needed for native fixed100. */
 CHECK(!global_cash25_body_slots[0].role);birth(0,0);CHECK(start_draw(0,MIRROR_BLEND)==1);emit(0,MIRROR_BLEND);CHECK(global_cash25_finish_proof());
 test_profile=0;
}
int main(int argc,char **argv)
{
 CHECK(argc==3);valid_root=argv[1];fixture_root=argv[2];load_original();source_backup=malloc(explosionSpriteSheet.size);body_backup=malloc(spriteSheet11.size);CHECK(source_backup&&body_backup);memcpy(source_backup,explosionSpriteSheet.data,explosionSpriteSheet.size);memcpy(body_backup,spriteSheet11.data,spriteSheet11.size);load_frames();
 gem_phase_and_alias_cases();profile_separation();observed_dead_value();all_phases();invalid_cases();resources();source_mutations();transactions();observed_revoke_then_restore();lifecycle();cache_and_leases();geometry_cases();fade_cases();
 global_cash25_shutdown();global_talon_shutdown();free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(spriteSheet9.data);free(explosionSpriteSheet.data);free(spriteSheet11.data);free(source_backup);free(body_backup);for(unsigned i=0;i<33;i++)free(reference_frames[i]);
 printf("PASS: %u cases, %u assertions; production Cash25 observer with structural SDL shim, not native engine proof\n",cases,checks);return 0;
}
