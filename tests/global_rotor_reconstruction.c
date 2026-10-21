#define render_mirror_green_create_begin(...) (0)
#define render_mirror_green_create_end(...) ((void)0)
#define render_mirror_green_shot_allocated(...) ((void)0)
#define render_mirror_green_shot_initialized(...) ((void)0)
#define render_mirror_green_trail_begin(...) ((void)0)
#define render_mirror_green_trail_end(...) ((void)0)
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Current-production Rotor5And11Eight observer. SDL is a bounded structural shim.
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
static bool global_cash25_frame,global_cash25_fault,global_cash25_cached;
static Uint8 *global_cash25_owner,*global_cash25_foreign;
static bool global_cash25_source_matches(Sprite2_array b){(void)b;return true;}
static bool global_cash25_palette_matches(void){return true;}
static bool global_cash25_requested(void){return false;}
static bool global_cash25_is_index(unsigned index){return false;}
static bool global_cash25_surface_matches(void){return true;}
static bool global_cash25_final_surface_matches(void){return true;}
static void global_cash25_shutdown(void){}
static void global_cash25_reset(void){}
static void global_cash25_frame_begin(void){}
static bool global_cash25_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_cash25_final_pixel(SDL_Surface *s,Uint8 *p){}
static void global_cash25_final_rect(SDL_Surface *s,const SDL_Rect *r){}
static void global_cash25_end(void){}
static bool global_cash25_observe_blend(SDL_Surface *s,Uint8 *p){return false;}
static bool global_cash25_finish_proof(void){return true;}
static bool global_cash25_compose(MirrorOutputKind k,int x,int y){return false;}
static void global_cash25_check_cache(void){}
static bool global_cash25_fade_buffer_safe(void){return true;}
static bool global_cash25_fade_capture(void){return true;}
static bool global_cash25_fade_step_valid(int steps){return true;}
static void global_cash25_fade_palette(void){}

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
static bool global_talon_frame,global_rotor_frame,global_rotor_fault,global_talon_shield_dependency;
static Uint8 *global_rotor_owner,*global_rotor_foreign;
static bool global_rotor_source_matches(Sprite2_array);
static bool global_rotor_palette_matches(void);
static Sprite2_array spriteSheet9,spriteSheet11,explosionSpriteSheet,enemySpriteSheets[4];
static Uint8 enemySpriteSheetIds[4];
#define MAX_EXPLOSIONS 200
typedef int16_t JE_integer;typedef unsigned short JE_word;typedef unsigned char JE_byte;
typedef struct {JE_byte ttl;JE_integer x,y;JE_word sprite;bool followPlayer,fixedPosition;JE_integer deltaY;} Explosion;
typedef int8_t JE_shortint;typedef bool JE_boolean;
#define ENEMY_NUM 1850
#include "rotor_identity_types.h"
static JE_EnemyDatType enemyDat;
static JE_MultiEnemyType enemy;
static Uint8 enemyAvail[100],original_record[154];
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
#include "global_rotor_mirror.inc"
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

static void record_load(const Uint8 *b){record_load_one(b,5);record_load_one(b+77,11);}
static void load_original(void){Uint32 n;read_exact(&n,4);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);read_exact(&n,4);enemySpriteSheets[0].size=n;enemySpriteSheets[0].data=malloc(n);CHECK(enemySpriteSheets[0].data);read_exact(enemySpriteSheets[0].data,n);enemySpriteSheetIds[0]=1;read_exact(original_record,sizeof(original_record));record_load(original_record);read_exact(normal_palette,sizeof(normal_palette));CHECK(fgetc(stdin)==EOF);}
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
static Uint8 *source_backup,*reference_frames[8];
static void load_frames(void){for(unsigned i=0;i<8;i++){const GlobalAssetResource *r=NULL;for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_rotor_resource_ids[i])r=global_asset_resources+j;CHECK(r);char p[2048];snprintf(p,sizeof(p),"%s/%s",valid_root,r->path);FILE *f=fopen(p,"rb");CHECK(f);CHECK(!fseek(f,28,SEEK_SET));reference_frames[i]=malloc(192*224*4);CHECK(reference_frames[i]);CHECK(fread(reference_frames[i],1,192*224*4,f)==192*224*4);CHECK(fgetc(f)==EOF);fclose(f);}}
static void setup(const char *root,int d){++cases;global_rotor_shutdown();global_talon_shutdown();free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);fade_saved=NULL;free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);game_probe_density=d;canvas=make_surface(320*d,200*d,32);output=make_surface(320*d,200*d,32);game_screen=make_surface(320,200,8);VGAScreenSeg=make_surface(320,200,8);VGAScreen=game_screen;size_t n=(size_t)canvas->w*canvas->h;hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,2);green_under=calloc(n,4);green_under_owner=calloc(n,1);CHECK(hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));record_load(original_record);memcpy(enemySpriteSheets[0].data,source_backup,enemySpriteSheets[0].size);enemySpriteSheetIds[0]=1;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;twoPlayerMode=false;shared_hud_frame=false;ready=last_output_valid=have_fade_saved=false;fade_mode=0;CHECK(render_mirror_set_global_assets(root));set_background();++mirror_logic_tick;global_talon_frame_begin();global_rotor_frame_begin();CHECK(global_rotor_frame);}
static void next_frame(void){set_background();++mirror_logic_tick;global_talon_frame_begin();global_rotor_frame_begin();CHECK(global_rotor_frame);}
static void final_copy(void){for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);upscale(output,VGAScreenSeg);}
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

static void birth(unsigned slot,unsigned type,int x,int y,unsigned filter){
 struct JE_SingleEnemyType *e=enemy+slot;enemyAvail[slot]=1;render_mirror_rotor_enemy_allocated(e,type,0);memset(e,0,sizeof(*e));e->enemytype=type;e->enemydatofs=enemyDat+type;e->sprite2s=enemySpriteSheets;e->size=1;e->ani=8;e->animin=1;e->aniactive=1;e->armorleft=enemyDat[type].armor;e->evalue=enemyDat[type].value;e->ex=x;e->ey=y;e->filter=filter;e->edani=enemyDat[type].dani;e->edgr=enemyDat[type].dgr;e->edlevel=enemyDat[type].dlevel;memcpy(e->egr,enemyDat[type].egraphic,sizeof(e->egr));render_mirror_rotor_enemy_initialized(e,type,0);enemyAvail[slot]=0;CHECK(global_rotor_body_slots[slot].role);}
static void animate(unsigned slot){struct JE_SingleEnemyType *e=enemy+slot;e->enemycycle=e->enemycycle==8?1:e->enemycycle+1;render_mirror_rotor_enemy_animated(slot);CHECK(global_rotor_body_slots[slot].role);}
static G101EnemyContext context(unsigned slot){return (G101EnemyContext){enemy[slot].enemytype,slot,enemyAvail[slot],1,false,false,false,false};}
static int draw(unsigned slot,unsigned part){G101EnemyContext c=context(slot);struct JE_SingleEnemyType *e=enemy+slot;return render_mirror_global_rotor_body(game_screen,e->ex+(part==1||part==20?6:-6),e->ey+(part>=19?7:-7),*e->sprite2s,e->egr[e->enemycycle-1],part,e->filter,&c);}
static void emit(unsigned slot,unsigned part){struct JE_SingleEnemyType *e=enemy+slot;int x=e->ex+(part==1||part==20?6:-6),y=e->ey+(part>=19?7:-7);Uint8 c[168],m[168];CHECK(reference_decode(*e->sprite2s,e->egr[e->enemycycle-1]+part,c,m,NULL));for(unsigned i=0;i<168;i++)if(m[i]){int xx=x+i%12,yy=y+i/12;int offset=yy*320+xx;if(offset<0||offset>=64000)continue;Uint8 *p=(Uint8 *)game_screen->pixels+offset,v=e->filter?(e->filter|(c[i]&15)):c[i];*p=v;render_mirror_pixel(game_screen,p,v,MIRROR_NORMAL);}global_rotor_end();global_talon_end();}
static void quartet(unsigned slot){static const unsigned parts[]={0,1,19,20};for(unsigned q=0;q<4;q++){if(q<2?enemy[slot].ey<=-13:enemy[slot].ey<=-26||enemy[slot].ey>=182)continue;int expect=enemy[slot].ey+(q>=2?7:-7)>=-13;int accepted=draw(slot,parts[q]);if(accepted!=expect)fprintf(stderr,"draw fail case%u type%u phase%u q%u filter%u role%d remain%u fault%d source%d pal%d frame%d\n",cases,enemy[slot].enemytype,enemy[slot].enemycycle,q,enemy[slot].filter,global_rotor_body_slots[slot].role,global_rotor_body_slots[slot].remaining,global_rotor_fault,global_rotor_source_matches(global_rotor_bank()),global_rotor_palette_matches(),global_rotor_frame);CHECK(accepted==expect);emit(slot,parts[q]);CHECK(!global_rotor_fault);}CHECK(global_rotor_body_slots[slot].remaining==0);}
static void oracle(unsigned slot){struct JE_SingleEnemyType *e=enemy+slot;unsigned phase=(e->egr[e->enemycycle-1]-229)/2;int d=game_probe_density,x=e->ex-6,y=e->ey-7;const Uint8 *rgba=reference_frames[phase];for(int ay=0;ay<28*d;ay++)for(int ax=0;ax<24*d;ax++){int dx=x*d+ax,dy=y*d+ay;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;if((ay/d<14&&e->ey<=-13)||(ay/d>=14&&(e->ey<=-26||e->ey>=182)))continue;const Uint8 *a=rgba+4*((ay*8/d)*192+ax*8/d);Uint8 f[4];memcpy(f,a,4);if(e->filter){unsigned peak=a[0]>a[1]?a[0]:a[1];if(a[2]>peak)peak=a[2];unsigned v=(peak*15*256+127)/255,lo=v/256,hi=lo<15?lo+1:15,frac=v%256;Uint32 l=rgb_palette[(Uint8)(e->filter|lo)],h=rgb_palette[(Uint8)(e->filter|hi)];for(int c=0;c<3;c++){unsigned sh=16-c*8;f[c]=(((l>>sh)&255)*(256-frac)+((h>>sh)&255)*frac+128)/256;}}Uint32 want=reference_blend(palette_rgb(0x1b),f,f[3]);CHECK(*rgba_at(dx,dy)==want);}}
static void phases(void){unsigned filters[]={0,0x70,0x80,9};for(int d=4;d<=8;d+=4)for(unsigned t=0;t<2;t++)for(unsigned f=0;f<4;f++){setup(valid_root,d);birth(0,t?11:5,110,80,filters[f]);for(unsigned p=0;p<16;p++){if(p)next_frame();enemy[0].filter=filters[f];animate(0);quartet(0);oracle(0);final_copy();CHECK(global_rotor_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(global_rotor_finish_proof());}}}
static void clipping(void){int ys[]={-25,-20,-13,-12,-6,0,181,182,195};for(unsigned k=0;k<COUNTOF(ys);k++){setup(valid_root,4);birth(0,5,110,ys[k],0);animate(0);quartet(0);oracle(0);}}
static void clipped_after_contribution(void){
 for(unsigned k=0;k<2;k++){
  setup(valid_root,4);birth(0,5,110,80,0);animate(0);quartet(0);
  birth(1,11,k?0:180,k?80:-12,0);animate(1);
  const unsigned parts[]={0,1,19,20};for(unsigned q=0;q<4;q++){
   int x=enemy[1].ex+(q%2?6:-6),y=enemy[1].ey+(q>=2?7:-7);
   CHECK(draw(1,parts[q])==(x>=0&&x<=308&&y>=-13&&y<200));emit(1,parts[q]);CHECK(!global_rotor_fault);
  }
  CHECK(global_rotor_body_slots[1].remaining==0);oracle(0);CHECK(global_rotor_finish_proof());
 }
 setup(valid_root,4);birth(0,5,110,80,0);animate(0);CHECK(draw(0,0));emit(0,0);CHECK(!global_rotor_finish_proof());
}
static void invalid(void){for(unsigned k=0;k<19;k++){setup(valid_root,4);birth(0,5,110,80,0);animate(0);G101EnemyContext c=context(0);Sprite2_array bank=enemySpriteSheets[0];unsigned base=229;int part=0,filter=0,x=104,y=73;switch(k){case 0:c.type=11;break;case 1:c.pool_slot=1;break;case 2:c.availability=2;break;case 3:c.size=0;break;case 4:c.score_item=true;break;case 5:c.damaged=true;break;case 6:part=1;x+=12;break;case 7:part=2;break;case 8:filter=0x70;break;case 9:x++;break;case 10:y++;break;case 11:base+=2;break;case 12:bank.size--;break;case 13:bank.data=spriteSheet9.data;break;case 14:enemy[0].evalue++;break;case 15:enemy[0].sprite2s=&enemySpriteSheets[1];break;case 16:enemy[0].enemytype=11;break;case 17:enemy[0].enemycycle=2;break;case 18:enemyAvail[0]=1;break;}unsigned opens=asset_opens;CHECK(render_mirror_global_rotor_body(game_screen,x,y,bank,base,part,filter,&c)==0);CHECK(asset_opens==opens);}}
static void resources(void){for(unsigned i=0;i<8;i++)for(unsigned k=0;k<4;k++){const char *modes[]={"missing","corrupt","header","trailing"};char p[2048];snprintf(p,sizeof(p),"%s/%s%u",fixture_root,modes[k],i);setup(p,4);birth(0,5,110,80,0);animate(0);CHECK(draw(0,0)==0);CHECK(!global_rotor_good);}}
static void sticky(void){for(unsigned k=0;k<4;k++){setup(valid_root,4);birth(0,5,110,80,0);animate(0);quartet(0);CHECK(global_rotor_contributed);for(size_t n=0;n<global_rotor_capacity;n++)global_rotor_owner[n]=0;Uint8 saved=enemySpriteSheets[0].data[100];if(k==0)game_probe_missing=true;if(k==1)game_probe_invalid=true;if(k==2)game_probe_original_reference=true;if(k==3)enemySpriteSheets[0].size--;global_rotor_observed_preflight();game_probe_missing=game_probe_invalid=game_probe_original_reference=false;if(k==3)enemySpriteSheets[0].size++;enemySpriteSheets[0].data[100]=saved;CHECK(global_rotor_fault&&!global_rotor_finish_proof());}}
static void lifecycle(void){setup(valid_root,4);birth(0,5,110,80,0);animate(0);quartet(0);enemyAvail[0]=1;next_frame();enemyAvail[0]=0;CHECK(!global_rotor_body_slots[0].role);birth(0,11,110,80,0);animate(0);quartet(0);CHECK(!global_rotor_fault);setup(valid_root,4);birth(0,5,110,-30,0);animate(0);CHECK(global_rotor_body_slots[0].remaining==0);next_frame();enemy[0].ey=80;animate(0);CHECK(enemy[0].enemycycle==2);quartet(0);}
static void cache_tests(void){for(unsigned k=0;k<8;k++){setup(valid_root,4);birth(0,5,110,80,0);animate(0);quartet(0);final_copy();CHECK(global_rotor_compose(MIRROR_OUTPUT_ORDINARY,0,0));memcpy(last_output_indices,VGAScreenSeg->pixels,64000);ready=last_output_valid=true;SDL_Surface c=*canvas,o=*output,g=*game_screen,v=*VGAScreenSeg;switch(k){case 0:canvas->pitch++;break;case 1:output->pixels=NULL;break;case 2:game_screen->pitch++;break;case 3:VGAScreenSeg->pixels=NULL;break;case 4:game_probe_density=8;break;case 5:rgb_palette[0]^=1;break;case 6:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;case 7:enemySpriteSheets[0].size--;break;}global_rotor_check_cache();CHECK(!global_rotor_cached&&!ready&&!last_output_valid);*canvas=c;*output=o;*game_screen=g;*VGAScreenSeg=v;game_probe_density=4;if(k==7)enemySpriteSheets[0].size++;}}
static void prepare_fade(int d)
{
 setup(valid_root,d);birth(0,5,110,80,0);animate(0);quartet(0);final_copy();CHECK(global_rotor_compose(MIRROR_OUTPUT_ORDINARY,0,0));
 memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));ready=last_output_valid=true;
 SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(fade_saved&&fade_mode==1&&have_fade_saved&&last_output_valid&&global_rotor_cached);
}
static void fade_cases(void)
{
 for(int d=4;d<=8;d+=4) {
  prepare_fade(d);size_t count=(size_t)output->w*output->h;Uint32 *before=malloc(count*4);CHECK(before);memcpy(before,output->pixels,count*4);
  for(unsigned i=0;i<256;i++){Uint32 v=rgb_palette[i],next=0;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;next|=(Uint32)(c+(0-c)/2)<<shift;}rgb_palette[i]=next;}
  render_mirror_fade_step(2);CHECK(ready&&global_rotor_cached&&last_output_valid);
  for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
   bool owned=x<264*d&&y<184*d&&hd_owner[(size_t)y*canvas->w+x+24*d];Uint32 want=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d]);
   if(owned){Uint32 v=before[(size_t)y*output->w+x];want=0xff000000u;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;want|=(Uint32)(c+(0-c)/2)<<shift;}}
   CHECK(((Uint32 *)output->pixels)[(size_t)y*output->w+x]==want);
  }
  global_rotor_check_cache();CHECK(global_rotor_cached);free(before);
 }
 for(unsigned bad=0;bad<11;bad++) {
  prepare_fade(4);SDL_Surface c=*canvas,o=*output,f=*fade_saved,v=*VGAScreenSeg;SDL_PixelFormat fmt=*fade_saved->format;
  switch(bad){case 0:fade_saved->pixels=NULL;break;case 1:fade_saved->pixels=(Uint8 *)canvas->pixels+4;break;case 2:fade_saved->pitch++;break;case 3:fade_saved->w--;break;case 4:fade_saved->format->BytesPerPixel=1;break;case 5:canvas->pitch++;break;case 6:output->pixels=NULL;break;case 7:VGAScreenSeg->pitch++;break;case 8:rgb_palette[255]^=1;break;case 9:game_probe_density=8;break;case 10:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;}
  render_mirror_fade_step(2);CHECK(!ready&&!last_output_valid&&!global_rotor_cached&&!fade_mode&&!have_fade_saved);
  *canvas=c;*output=o;*fade_saved=f;*VGAScreenSeg=v;*fade_saved->format=fmt;game_probe_density=4;
 }
}
static void source_cases(void){for(unsigned k=0;k<7;k++){setup(valid_root,4);birth(0,5,110,80,0);animate(0);unsigned opens=asset_opens;Uint8 colors[168],mask[168];size_t offsets[168];CHECK(reference_decode(enemySpriteSheets[0],229,colors,mask,offsets));unsigned n=first_cell(mask);Uint8 saved=enemySpriteSheets[0].data[offsets[n]];switch(k){case 0:enemySpriteSheets[0].data[offsets[n]]^=1;break;case 1:enemySpriteSheets[0].size--;break;case 2:enemySpriteSheetIds[0]=2;break;case 3:enemyDat[5].value++;break;case 4:enemyDat[11].value++;break;case 5:rgb_palette[0]^=1;break;case 6:enemySpriteSheetIds[1]=1;enemySpriteSheets[1]=enemySpriteSheets[0];break;}CHECK(draw(0,0)==0);CHECK(asset_opens==opens);enemySpriteSheets[0].data[offsets[n]]=saved;if(k==1)enemySpriteSheets[0].size++;enemySpriteSheetIds[1]=0;memset(enemySpriteSheets+1,0,sizeof(enemySpriteSheets[1]));}}
static void geometry_cases(void){for(unsigned k=0;k<7;k++){setup(valid_root,4);global_rotor_reset();SDL_Surface c=*canvas,o=*output,g=*game_screen,v=*VGAScreenSeg;switch(k){case 0:canvas->pixels=(Uint8 *)canvas->pixels+1;break;case 1:output->pixels=(Uint8 *)canvas->pixels+4;break;case 2:game_screen->pixels=VGAScreenSeg->pixels;break;case 3:canvas->pitch++;break;case 4:VGAScreenSeg->pixels=canvas->pixels;break;case 5:output->pitch=1;break;case 6:game_screen->w--;break;}global_rotor_frame_begin();CHECK(!global_rotor_frame);*canvas=c;*output=o;*game_screen=g;*VGAScreenSeg=v;}}

int main(int argc,char **argv){CHECK(argc==3);valid_root=argv[1];fixture_root=argv[2];load_original();source_backup=malloc(enemySpriteSheets[0].size);memcpy(source_backup,enemySpriteSheets[0].data,enemySpriteSheets[0].size);load_frames();phases();clipping();clipped_after_contribution();invalid();resources();sticky();lifecycle();cache_tests();source_cases();geometry_cases();fade_cases();global_rotor_shutdown();global_talon_shutdown();free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(spriteSheet9.data);free(enemySpriteSheets[0].data);free(source_backup);for(unsigned i=0;i<8;i++)free(reference_frames[i]);printf("PASS: %u cases, %u assertions; extracted production rotor observer, not native engine proof\n",cases,checks);return 0;}
