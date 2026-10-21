#define render_mirror_green_create_begin(...) (0)
#define render_mirror_green_create_end(...) ((void)0)
#define render_mirror_green_shot_allocated(...) ((void)0)
#define render_mirror_green_shot_initialized(...) ((void)0)
#define render_mirror_green_trail_begin(...) ((void)0)
#define render_mirror_green_trail_end(...) ((void)0)
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Current-production Vulcan2 observer. SDL is a bounded structural shim.
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

/* This family is disabled in this isolated regression harness. */
/* Small explosion disabled only in this isolated existing-family harness. */
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
#define render_mirror_cash25_value_allocated(...) ((void)0)
#define render_mirror_cash25_value_initialized(...) ((void)0)

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

static bool global_pulse_frame,global_pulse_fault;
static Uint8 *global_pulse_owner,*global_pulse_foreign;
static bool global_pulse_source_matches(Sprite2_array);
static bool global_pulse_palette_matches(void);

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
static bool global_talon_frame,global_shield_frame,global_shield_fault,global_talon_shield_dependency;
static Uint8 *global_shield_owner,*global_shield_foreign;
static bool global_shield_source_matches(Sprite2_array);
static bool global_shield_palette_matches(void);
static Sprite2_array spriteSheet9,explosionSpriteSheet,spriteSheet8;
#define MAX_EXPLOSIONS 200
typedef int JE_integer;typedef unsigned short JE_word;typedef unsigned char JE_byte;
typedef struct {JE_byte ttl;JE_integer x,y;JE_word sprite;bool followPlayer,fixedPosition;JE_integer deltaY;} Explosion;
static Explosion explosions[MAX_EXPLOSIONS];
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
static bool background2;
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
static struct {int x,y,delta_x_shot_move,delta_y_shot_move;unsigned invulnerable_ticks;struct {struct {unsigned id,power;} weapon[2];} items;unsigned weapon_mode;} player[2];
#define MAX_PWEAPON 81
#define PORT_NUM 42
#define WEAP_NUM 1818
#define FRONT_WEAPON 0
#define REAR_WEAPON 1
typedef signed char JE_shortint;
typedef unsigned int uint;
typedef struct {JE_word drain;JE_byte shotrepeat,multi;JE_word weapani;JE_byte max,tx,ty,aim;JE_byte attack[8],del[8];JE_shortint sx[8],sy[8],bx[8],by[8];JE_word sg[8];JE_shortint acceleration,accelerationx;JE_byte circlesize,sound,trail,shipblastfilter;} JE_WeaponType;
static JE_WeaponType weapons[WEAP_NUM+1];
static struct {char name[31];JE_byte opnum;JE_word op[2][11],cost,itemgraphic,poweruse;} weaponPort[PORT_NUM+1];
typedef struct {JE_integer shotX,shotY,shotXM,shotYM,shotXC,shotYC;bool shotComplicated;JE_integer shotDevX,shotDirX,shotDevY,shotDirY,shotCirSizeX,shotCirSizeY;JE_byte shotTrail;JE_word shotGr,shotAni,shotAniMax;Uint8 shotDmg;JE_byte shotBlastFilter,chainReaction,playerNumber,aimAtEnemy,aimDelay,aimDelayMax;} PlayerShotDataType;
static PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static JE_byte shotAvail[MAX_PWEAPON];
static bool global_vulcan_frame,global_vulcan_fault;
static Uint8 *global_vulcan_owner,*global_vulcan_foreign;
static bool global_vulcan_source_matches(Sprite2_array);
static bool global_vulcan_palette_matches(void);

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
#include "global_shield_mirror.inc"
#define render_mirror_front_port_name render_mirror_pulse_front_port_name
#define render_mirror_front_port_loaded render_mirror_pulse_front_port_loaded
#define render_mirror_front_call_begin render_mirror_pulse_front_call_begin
#define render_mirror_front_call_end render_mirror_pulse_front_call_end
#define render_mirror_front_create_begin render_mirror_pulse_front_create_begin
#define render_mirror_front_create_end render_mirror_pulse_front_create_end
#define render_mirror_front_shot_initialized render_mirror_pulse_front_shot_initialized
#define render_mirror_shot_allocated render_mirror_pulse_shot_allocated
#include "global_pulse_mirror.inc"
#undef render_mirror_front_port_name
#undef render_mirror_front_port_loaded
#undef render_mirror_front_call_begin
#undef render_mirror_front_call_end
#undef render_mirror_front_create_begin
#undef render_mirror_front_create_end
#undef render_mirror_front_shot_initialized
#undef render_mirror_shot_allocated
#include "global_vulcan_mirror.inc"
#include "front-dispatch.inc"
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

/* Actual production allocator, with diagnostics and unrelated adapters inert. */
static int power=10000,x,y;
static Uint8 soundQueue[8],shotMultiPos[16],shotRepeat[16],enemyAvail[100];
static struct {bool scoreitem;int ex,ey;} enemy[100];
#define game_probe_shot_begin(...) 0u
#define game_probe_shot_result(...) ((void)0)
#define game_probe_shot_emit(...) ((void)0)
#define render_mirror_rear_p1_create_begin(...) UINT64_C(0)
#define render_mirror_rear_p1_create_end(...) ((void)0)
#define render_mirror_plasma_art_emit(...) ((void)0)
#define render_mirror_rear_p1_emit(...) ((void)0)
#include "allocator.inc"
static Uint8 raw_records[3][11][80],raw_ports[3][82];
static unsigned variant;
static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static unsigned get16(const Uint8 **p){unsigned n=(*p)[0]+256u*(*p)[1];*p+=2;return n;}
static void load_tables(unsigned v)
{
 variant=v;
 for(unsigned k=0;k<11;k++) {
  const Uint8 *p=raw_records[v][k];JE_WeaponType *w=&weapons[221+k];memset(w,0,sizeof(*w));
  w->drain=get16(&p);w->shotrepeat=*p++;w->multi=*p++;w->weapani=get16(&p);w->max=*p++;w->tx=*p++;w->ty=*p++;w->aim=*p++;
  memcpy(w->attack,p,8);p+=8;memcpy(w->del,p,8);p+=8;memcpy(w->sx,p,8);p+=8;memcpy(w->sy,p,8);p+=8;memcpy(w->bx,p,8);p+=8;memcpy(w->by,p,8);p+=8;
  for(unsigned j=0;j<8;j++)w->sg[j]=get16(&p);
  w->acceleration=(int8_t)*p++;w->accelerationx=(int8_t)*p++;w->circlesize=*p++;w->sound=*p++;w->trail=*p++;w->shipblastfilter=*p++;CHECK(p==raw_records[v][k]+80);
 }
 const Uint8 *p=raw_ports[v];unsigned length=*p++;memcpy(weaponPort[7].name,p,30);render_mirror_front_port_name(7,length,weaponPort[7].name);weaponPort[7].name[MIN(length,30)]=0;p+=30;weaponPort[7].opnum=*p++;
 for(unsigned j=0;j<2;j++)for(unsigned i=0;i<11;i++)weaponPort[7].op[j][i]=get16(&p);
 weaponPort[7].cost=get16(&p);weaponPort[7].itemgraphic=get16(&p);weaponPort[7].poweruse=get16(&p);CHECK(p==raw_ports[v]+82);render_mirror_front_port_loaded(7);
}
static void load_original(void)
{
 Sprite2_array *banks[]={&spriteSheet9,&explosionSpriteSheet,&spriteSheet8};unsigned sizes[]={33484,17810,32060};
 for(unsigned i=0;i<3;i++){Uint32 n;read_exact(&n,4);CHECK(n==sizes[i]);banks[i]->size=n;banks[i]->data=malloc(n);CHECK(banks[i]->data);read_exact(banks[i]->data,n);}
 read_exact(normal_palette,sizeof(normal_palette));
 for(unsigned v=0;v<3;v++){read_exact(raw_records[v],sizeof(raw_records[v]));read_exact(raw_ports[v],82);}CHECK(fgetc(stdin)==EOF);load_tables(0);
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
static Uint8 *source_backup;
static Uint8 *reference_frames[2];
static void load_frames(void)
{
 for(unsigned i=0;i<2;i++) {
  if(!global_vulcan_resource_ids[i])continue;
  const GlobalAssetResource *r=NULL;for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_vulcan_resource_ids[i])r=global_asset_resources+j;
  CHECK(r);char p[2048];snprintf(p,sizeof(p),"%s/%s",valid_root,r->path);FILE *f=fopen(p,"rb");CHECK(f);CHECK(!fseek(f,28,SEEK_SET));reference_frames[i]=malloc(96*112*4);CHECK(reference_frames[i]);CHECK(fread(reference_frames[i],1,96*112*4,f)==96*112*4);CHECK(fgetc(f)==EOF);fclose(f);
 }
}
static void setup(const char *root,int d)
{
 ++cases;global_vulcan_shutdown();global_shield_shutdown();global_talon_shutdown();
 free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);fade_saved=NULL;
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 game_probe_density=d;canvas=make_surface(320*d,200*d,32);output=make_surface(320*d,200*d,32);game_screen=make_surface(320,200,8);VGAScreenSeg=make_surface(320,200,8);VGAScreen=game_screen;
 size_t n=(size_t)canvas->w*canvas->h;hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,2);green_under=calloc(n,4);green_under_owner=calloc(n,1);CHECK(hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);
 memset(playerShotData,0,sizeof(playerShotData));memset(shotAvail,0,sizeof(shotAvail));load_tables(0);memcpy(spriteSheet8.data,source_backup,spriteSheet8.size);
 game_probe_missing=game_probe_invalid=game_probe_original_reference=false;twoPlayerMode=false;shared_hud_frame=false;
 ready=last_output_valid=have_fade_saved=false;fade_mode=0;player[0].x=120;player[0].y=90;player[1].x=226;player[1].y=90;
 CHECK(render_mirror_set_global_assets(root));set_background();++mirror_logic_tick;global_talon_frame_begin();global_shield_frame_begin();global_vulcan_frame_begin();CHECK(global_vulcan_frame);
}
static void next_frame(void)
{set_background();++mirror_logic_tick;global_talon_frame_begin();global_shield_frame_begin();global_vulcan_frame_begin();CHECK(global_vulcan_frame);}
/* A bounded faithful snapshot of the native allocator's normal Vulcan fields.
 * Integration tests separately execute actual player_shot_create and movement. */
static uint64_t synthetic_create_begin(unsigned port,unsigned bay,unsigned record,unsigned pnum)
{
 uint64_t token=render_mirror_front_create_begin(port,bay,record,pnum);
 render_mirror_front_create_geometry(token,120,90,120,90);return token;
}
static uint64_t begin_birth(unsigned record,unsigned pnum)
{
 unsigned power_index=record-221;player[pnum-1].items.weapon[0].id=7;player[pnum-1].items.weapon[0].power=power_index+1;player[pnum-1].weapon_mode=1;
 render_mirror_front_call_begin(7,0,power_index,0,pnum,record);
 return synthetic_create_begin(7,0,record,pnum);
}
static unsigned initializer_mutation;
static void initialize(unsigned slot,unsigned record,unsigned pnum,unsigned multipos,uint64_t token)
{
 JE_WeaponType *w=&weapons[record];unsigned k=multipos-1;PlayerShotDataType *s=playerShotData+slot;memset(s,0,sizeof(*s));
 s->shotX=120+w->bx[k];s->shotY=90+w->by[k];s->shotYC=-w->acceleration;s->shotXC=w->accelerationx;s->shotXM=w->sx[k];s->shotYM=-w->sy[k];
 s->shotGr=w->sg[k];s->shotAni=0;s->shotAniMax=w->weapani+1;s->shotTrail=w->trail;s->shotBlastFilter=w->shipblastfilter;s->playerNumber=pnum;
 s->shotDmg=w->attack[k];if(w->attack[k]>99&&w->attack[k]<250){s->chainReaction=w->attack[k]-100;s->shotDmg=1;}
 shotAvail[slot]=s->shotGr?w->del[k]:0;
 if(initializer_mutation==1)s->shotGr=70;
 if(initializer_mutation==2)s->aimAtEnemy=1;
 if(initializer_mutation==3)s->shotXM++;
 render_mirror_front_shot_initialized(token,slot,7,0,record,pnum,multipos);
}
static void birth(unsigned slot,unsigned record,unsigned pnum,unsigned multipos)
{
 shotAvail[slot]=0;uint64_t token=begin_birth(record,pnum);render_mirror_shot_allocated(slot);initialize(slot,record,pnum,multipos,token);
 render_mirror_front_create_end(token);render_mirror_front_call_end();
}
static unsigned raw_for(unsigned slot)
{PlayerShotDataType *s=playerShotData+slot;unsigned raw=s->shotGr+s->shotAni;if(++s->shotAni==s->shotAniMax)s->shotAni=0;return raw;}
static int start_draw(unsigned slot,int style,unsigned raw)
{PlayerShotDataType *s=playerShotData+slot;return render_mirror_global_vulcan(game_screen,s->shotX+1,s->shotY+(style==MIRROR_SHADOW?shadowYDist:0),spriteSheet8,raw,style,slot,raw);}
static void emit(unsigned slot,int style,unsigned raw)
{
 PlayerShotDataType *s=playerShotData+slot;Uint8 color[168],mask[168];CHECK(reference_decode(spriteSheet8,raw,color,mask,NULL));
 for(unsigned i=0;i<168;i++)if(mask[i]){int x=s->shotX+1+i%12,y=s->shotY+(style==MIRROR_SHADOW?shadowYDist:0)+i/12;if(x<0||x>=320||y<0||y>=200)continue;
 Uint8 *at=index_at(x,y),source=color[i];*at=style==MIRROR_NORMAL?source:style==MIRROR_BLEND?(source&240)|(((source&15)+(*at&15))/2):(*at&240)|((*at&15)/2);render_mirror_pixel(game_screen,at,source,style);}
 global_vulcan_end();global_shield_end();global_talon_end();CHECK(!global_vulcan_fault);
}
static unsigned owner_count(void){unsigned n=0;for(size_t i=0;i<global_vulcan_capacity;i++)n+=global_vulcan_owner[i]!=0;return n;}
static void final_copy(void){for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);upscale(output,VGAScreenSeg);}
static void all_births(void)
{
 for(unsigned v=0;v<3;v++)for(int d=4;d<=8;d+=4)for(unsigned pnum=1;pnum<=2;pnum++)for(unsigned rec=221;rec<=231;rec++) {
 setup(valid_root,d);load_tables(v);twoPlayerMode=pnum==2;
 for(unsigned m=1;m<=weapons[rec].max;m++){if(m>1)next_frame();birth(0,rec,pnum,m);unsigned raw=raw_for(0);CHECK(start_draw(0,MIRROR_NORMAL,raw)==1);emit(0,MIRROR_NORMAL,raw);CHECK(owner_count()>0);final_copy();CHECK(global_vulcan_finish_proof());CHECK(global_vulcan_compose(MIRROR_OUTPUT_ORDINARY,0,0));}
 }
}
static void resources(void)
{
 char path[2048];const char *modes[]={"missing","corrupt","header","trailing"};
 for(unsigned mode=0;mode<4;mode++)for(unsigned n=0;n<2;n++){snprintf(path,sizeof(path),"%s/%s%u",fixture_root,modes[mode],n);setup(path,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==0);CHECK(!global_vulcan_good);CHECK(owner_count()==0);unsigned before=asset_opens;next_frame();birth(0,221,1,1);raw=raw_for(0);CHECK(start_draw(0,0,raw)==0);CHECK(asset_opens==before);}
 snprintf(path,sizeof(path),"%s/vulcan-only",fixture_root);setup(path,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);CHECK(global_vulcan_good&&!global_talon_loaded&&!global_shield_loaded);
}
static void invalid_draws(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned bad=0;bad<15;bad++){
 setup(valid_root,4);if(warm){birth(0,221,1,1);unsigned r=raw_for(0);CHECK(start_draw(0,0,r)==1);emit(0,0,r);next_frame();}
 birth(0,221,1,1);unsigned raw=raw_for(0),index=raw;PlayerShotDataType *s=playerShotData;int x=s->shotX+1,y=s->shotY,style=0;Sprite2_array bank=spriteSheet8;SDL_Surface *surface=game_screen;unsigned opens=asset_opens;Uint8 *copy=NULL;
 switch(bad){case 0:index++;break;case 1:raw++;break;case 2:x++;break;case 3:y++;break;case 4:style=MIRROR_BLEND;break;case 5:bank.size--;break;case 6:copy=malloc(bank.size);memcpy(copy,bank.data,bank.size);bank.data=copy;break;case 7:surface=VGAScreenSeg;break;case 8:game_probe_original_reference=true;break;case 9:game_probe_missing=true;break;case 10:game_probe_invalid=true;break;case 11:rgb_palette[113]^=1;break;case 12:s->playerNumber=2;break;case 13:s->shotGr++;break;case 14:game_screen->pitch++;break;}
 CHECK(render_mirror_global_vulcan(surface,x,y,bank,index,style,0,raw)==0);CHECK(asset_opens==opens);free(copy);if(bad==14)game_screen->pitch--;
 }
}
static void source_mutations(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned t=0;t<2;t++){
 setup(valid_root,4);if(warm){birth(0,221,1,1);unsigned r=raw_for(0);CHECK(start_draw(0,0,r)==1);emit(0,0,r);next_frame();}
 Uint8 color[168],mask[168];size_t rawpos[168];CHECK(reference_decode(spriteSheet8,global_vulcan_source[t].index,color,mask,rawpos));size_t pos=rawpos[first_cell(mask)];Uint8 saved=spriteSheet8.data[pos];spriteSheet8.data[pos]^=1;
 birth(0,221,1,1);unsigned opens=asset_opens,r=raw_for(0);CHECK(start_draw(0,0,r)==0);CHECK(asset_opens==opens);spriteSheet8.data[pos]=saved;
 }
}
static void invalid_births(void)
{
 for(unsigned bad=0;bad<13;bad++){
 setup(valid_root,4);unsigned opens=asset_opens;player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=1;player[0].weapon_mode=1;
 unsigned port=7,bay=0,power_index=0,mode=0,pnum=1,record=221;
 switch(bad){case 1:port=2;break;case 2:bay=1;break;case 3:power_index=1;break;case 4:mode=1;break;case 5:pnum=0;break;case 6:record=222;break;case 7:weaponPort[7].cost++;break;case 8:weapons[221].sound++;break;case 9:weaponPort[7].name[0]^=1;break;case 10:weapons[221].by[7]^=1;break;case 12:weaponPort[7].name[30]=1;break;}
 if(bad)render_mirror_front_call_begin(port,bay,power_index,mode,pnum,record);
 if(bad==11)render_mirror_front_call_end();
 uint64_t token=synthetic_create_begin(7,0,221,1);render_mirror_shot_allocated(0);initialize(0,221,1,1,token);render_mirror_front_create_end(token);render_mirror_front_call_end();unsigned raw=raw_for(0);
 CHECK(start_draw(0,0,raw)!=1);CHECK(asset_opens==opens);
 }
}
static void allocation_reuse(void)
{
 setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);next_frame();
 shotAvail[0]=0;render_mirror_shot_allocated(0);initialize(0,221,1,1,0);raw=raw_for(0);CHECK(start_draw(0,0,raw)!=1);
 setup(valid_root,4);birth(0,221,1,1);render_mirror_global_reset();raw=raw_for(0);CHECK(start_draw(0,0,raw)!=1);
 for(unsigned bad=0;bad<5;bad++){
 setup(valid_root,4);uint64_t token=begin_birth(221,1);if(bad!=0)render_mirror_shot_allocated(0);
 if(bad==1)++mirror_logic_tick;if(bad==2)render_mirror_front_create_end(token);if(bad==3)render_mirror_front_call_end();
 initialize(0,221,1,1,bad==4?token+1:token);render_mirror_front_create_end(token);render_mirror_front_call_end();raw=raw_for(0);CHECK(start_draw(0,0,raw)!=1);
 }
}
static void cache_and_leases(void)
{
 for(unsigned bad=0;bad<10;bad++) {
  setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);
  for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);
  CHECK(global_vulcan_compose(MIRROR_OUTPUT_ORDINARY,0,0));memcpy(last_output_indices,VGAScreenSeg->pixels,64000);ready=last_output_valid=true;
  SDL_Surface a=*canvas,b=*output,c=*game_screen,f=*VGAScreenSeg;SDL_PixelFormat fmt=*canvas->format;
  switch(bad){case 0:canvas->pitch++;break;case 1:output->pixels=NULL;break;case 2:game_screen->pitch++;break;case 3:VGAScreenSeg->pixels=NULL;break;case 4:canvas->format->BytesPerPixel=1;break;case 5:game_probe_density=8;break;case 6:rgb_palette[0]^=1;break;case 7:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;case 8:global_asset_directory[0]=0;break;case 9:spriteSheet8.size--;break;}
  global_vulcan_check_cache();CHECK(!global_vulcan_cached&&!ready&&!last_output_valid);
  *canvas=a;*output=b;*game_screen=c;*VGAScreenSeg=f;*canvas->format=fmt;game_probe_density=4;if(bad==9)spriteSheet8.size++;
 }
}
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
 setup(valid_root,d);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);final_copy();CHECK(global_vulcan_compose(MIRROR_OUTPUT_ORDINARY,0,0));
 memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));ready=last_output_valid=true;
 SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(fade_saved&&fade_mode==1&&have_fade_saved&&last_output_valid&&global_vulcan_cached);
}
static void fade_cases(void)
{
 for(int d=4;d<=8;d+=4) {
  prepare_fade(d);size_t count=(size_t)output->w*output->h;Uint32 *before=malloc(count*4);CHECK(before);memcpy(before,output->pixels,count*4);
  for(unsigned i=0;i<256;i++){Uint32 v=rgb_palette[i],next=0;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;next|=(Uint32)(c+(0-c)/2)<<shift;}rgb_palette[i]=next;}
  render_mirror_fade_step(2);CHECK(ready&&global_vulcan_cached&&last_output_valid);
  for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
   bool owned=x<264*d&&y<184*d&&hd_owner[(size_t)y*canvas->w+x+24*d];Uint32 want=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d]);
   if(owned){Uint32 v=before[(size_t)y*output->w+x];want=0xff000000u;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;want|=(Uint32)(c+(0-c)/2)<<shift;}}
   CHECK(((Uint32 *)output->pixels)[(size_t)y*output->w+x]==want);
  }
  global_vulcan_check_cache();CHECK(global_vulcan_cached);free(before);
 }
 for(unsigned bad=0;bad<11;bad++) {
  prepare_fade(4);SDL_Surface c=*canvas,o=*output,f=*fade_saved,v=*VGAScreenSeg;SDL_PixelFormat fmt=*fade_saved->format;
  switch(bad){case 0:fade_saved->pixels=NULL;break;case 1:fade_saved->pixels=(Uint8 *)canvas->pixels+4;break;case 2:fade_saved->pitch++;break;case 3:fade_saved->w--;break;case 4:fade_saved->format->BytesPerPixel=1;break;case 5:canvas->pitch++;break;case 6:output->pixels=NULL;break;case 7:VGAScreenSeg->pitch++;break;case 8:rgb_palette[255]^=1;break;case 9:game_probe_density=8;break;case 10:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;}
  render_mirror_fade_step(2);CHECK(!ready&&!last_output_valid&&!global_vulcan_cached&&!fade_mode&&!have_fade_saved);
  *canvas=c;*output=o;*fade_saved=f;*VGAScreenSeg=v;*fade_saved->format=fmt;game_probe_density=4;
 }
}
/* Model a later RGB consumer having taken every Shield owner bit. This is
 * not a HUD font simulation: native tests cover the actual underlay copy. */
static void transferred_contributor_cases(void)
{
 for(unsigned stage=0;stage<3;stage++)for(unsigned bad=0;bad<9;bad++) {
  setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);final_copy();
  CHECK(global_vulcan_contributed);memset(global_vulcan_owner,0,(size_t)canvas->w*canvas->h);
  CHECK(global_vulcan_finish_proof());
  SDL_Surface c=*canvas,o=*output,g=*game_screen,v=*VGAScreenSeg;
  Uint8 color[168],mask[168];size_t rawpos[168];CHECK(reference_decode(spriteSheet8,67,color,mask,rawpos));size_t pos=rawpos[first_cell(mask)];
  if(stage) {
   CHECK(!global_vulcan_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(global_vulcan_cached);
   memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));ready=last_output_valid=true;
   global_vulcan_check_cache();global_vulcan_check_cache();CHECK(ready&&last_output_valid&&global_vulcan_cached);
   if(stage==2){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(last_output_valid&&global_vulcan_cached&&have_fade_saved);
    for(unsigned i=0;i<256;i++){Uint32 v=rgb_palette[i],next=0;for(int shift=0;shift<24;shift+=8){int ch=(v>>shift)&255;next|=(Uint32)(ch+(0-ch)/2)<<shift;}rgb_palette[i]=next;}
    CHECK(global_vulcan_fade_step_valid(2));}
  }
  switch(bad) {
   case 0:spriteSheet8.data[pos]^=1;break;
   case 1:rgb_palette[113]^=1;break;
   case 2:global_vulcan_fault=true;break;
   case 3:canvas->pitch+=4;break;
   case 4:output->pitch+=4;break;
   case 5:game_screen->pixels=(Uint8 *)game_screen->pixels+1;break;
   case 6:VGAScreenSeg->pitch++;break;
   case 7:CHECK(render_mirror_set_global_assets(NULL));break;
  }
  if(!stage) {
   if(bad==8)CHECK(global_vulcan_finish_proof());
   else if(bad==7)CHECK(!active&&!shared_hud_frame&&!ready&&!last_output_valid);
   else CHECK(!global_vulcan_finish_proof());
  } else {
   if(stage==1)global_vulcan_check_cache();else render_mirror_fade_step(2);
   if(bad==8)CHECK(ready&&last_output_valid&&global_vulcan_cached);
   else CHECK(!ready&&!last_output_valid&&!global_vulcan_cached&&!have_fade_saved&&!fade_mode);
  }
  *canvas=c;*output=o;*game_screen=g;*VGAScreenSeg=v;memcpy(spriteSheet8.data,source_backup,spriteSheet8.size);
  CHECK(render_mirror_set_global_assets(valid_root));next_frame();CHECK(!global_vulcan_contributed&&!global_vulcan_fault);
  birth(0,221,1,1);raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);final_copy();CHECK(global_vulcan_finish_proof());CHECK(global_vulcan_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(global_vulcan_cached);
 }
}
static void geometry_cases(void)
{
 for(unsigned bad=0;bad<8;bad++) {
  setup(valid_root,4);global_vulcan_reset();SDL_Surface c=*canvas,o=*output,g=*game_screen,v=*VGAScreenSeg;
  switch(bad){case 0:canvas->pixels=(Uint8 *)canvas->pixels+1;break;case 1:output->pixels=(Uint8 *)canvas->pixels+4;break;case 2:game_screen->pixels=VGAScreenSeg->pixels;break;case 3:canvas->pitch++;break;case 4:VGAScreenSeg->pixels=canvas->pixels;break;case 5:output->pitch=1;break;case 6:game_screen->w--;break;case 7:game_probe_density=2;break;}
  global_vulcan_frame_begin();CHECK(!global_vulcan_frame);unsigned opens=asset_opens;birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==0);CHECK(asset_opens==opens);
  *canvas=c;*output=o;*game_screen=g;*VGAScreenSeg=v;game_probe_density=4;
 }
}


static void actual_allocator(void)
{
 for(unsigned v=0;v<3;v++)for(unsigned rec=221;rec<=231;rec++)for(unsigned pnum=1;pnum<=2;pnum++) {
  setup(valid_root,4);load_tables(v);memset(shotMultiPos,0,sizeof(shotMultiPos));power=10000;player[pnum-1].items.weapon[0].id=7;player[pnum-1].items.weapon[0].power=rec-220;
  render_mirror_front_call_begin(7,0,rec-221,0,pnum,rec);int last=player_shot_create(7,0,120,90,120,90,rec,pnum);render_mirror_front_call_end();CHECK(last==(int)weapons[rec].multi-1);
  for(unsigned slot=0;slot<weapons[rec].multi;slot++) {unsigned raw=raw_for(slot);CHECK(start_draw(slot,0,raw)==1);emit(slot,0,raw);}
 }
 for(unsigned bad=0;bad<3;bad++) {
  setup(valid_root,4);memset(shotMultiPos,0,sizeof(shotMultiPos));power=bad==0?0:10000;if(bad==1)memset(shotAvail,1,sizeof(shotAvail));
  player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=1;render_mirror_front_call_begin(7,0,0,0,1,221);
  CHECK(player_shot_create(7,0,120,90,120,90,bad==2?0:221,1)==MAX_PWEAPON);CHECK(!global_vulcan_front_call.live);render_mirror_front_call_end();
 }
}
/* del 98 retains real player horizontal movement, including the +/-5 clamp.
 * Every used lane is obtained from the allocator, not a synthetic initializer. */
static void actual_moving_allocator(void)
{
 static const int offsets[]={-17,-5,-2,0,2,5,17};
 for(unsigned v=0;v<3;v++)for(unsigned rec=221;rec<=231;rec++)for(unsigned pnum=1;pnum<=2;pnum++)for(unsigned d=0;d<COUNTOF(offsets);d++) {
  setup(valid_root,4);load_tables(v);twoPlayerMode=pnum==2;power=10000;
  player[pnum-1].items.weapon[0].id=7;player[pnum-1].items.weapon[0].power=rec-220;
  for(unsigned k=0;k<weapons[rec].max;k++) {
   memset(shotAvail,0,sizeof(shotAvail));memset(shotMultiPos,0,sizeof(shotMultiPos));shotMultiPos[0]=k;
   render_mirror_front_call_begin(7,0,rec-221,0,pnum,rec);
   CHECK(player_shot_create(7,0,120,90,120-offsets[d],90,rec,pnum)==0);
   render_mirror_front_call_end();CHECK(shotMultiPos[0]==k+1);
   int adjusted=offsets[d]<-5?-5:offsets[d]>5?5:offsets[d];
   CHECK(weapons[rec].del[k]==98);CHECK(playerShotData[0].shotXM==weapons[rec].sx[k]+adjusted);
   CHECK(global_vulcan_slots[0].claimed&&global_vulcan_slots[0].role);
   unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);next_frame();
  }
 }
 /* Incorrect XM cannot be justified merely because it lies inside the clamp. */
 setup(valid_root,4);initializer_mutation=3;birth(0,221,1,1);initializer_mutation=0;
 CHECK(global_vulcan_slots[0].claimed&&!global_vulcan_slots[0].role);
 CHECK(start_draw(0,0,raw_for(0))==0);
}
static void actual_zero_graphic_reuse(void)
{
 setup(valid_root,4);memset(shotMultiPos,0,sizeof(shotMultiPos));power=10000;
 player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=1;render_mirror_front_call_begin(7,0,0,0,1,221);
 CHECK(player_shot_create(7,0,120,90,120,90,221,1)==0);render_mirror_front_call_end();CHECK(global_vulcan_slots[0].role);uint64_t generation=global_vulcan_slots[0].generation;
 shotAvail[0]=0;weapons[1]=weapons[221];weapons[1].sg[0]=0;memset(shotMultiPos,0,sizeof(shotMultiPos));CHECK(player_shot_create(7,0,120,90,120,90,1,1)==0);
 CHECK(!shotAvail[0]&&!global_vulcan_slots[0].role&&global_vulcan_slots[0].generation!=generation);
}
static void birth_and_draw_boundaries(void)
{
 for(unsigned bad=0;bad<7;bad++){
  setup(valid_root,4);player[0].items.weapon[0].id=bad==0?2:7;player[0].items.weapon[0].power=bad==1?2:1;
  if(bad==2)game_probe_missing=true;if(bad==3)game_probe_original_reference=true;if(bad==4)game_probe_invalid=true;
  render_mirror_front_call_begin(7,0,0,0,1,221);uint64_t token=synthetic_create_begin(7,0,221,1);render_mirror_shot_allocated(0);initialize(0,221,1,1,token);render_mirror_front_create_end(token);render_mirror_front_call_end();
  game_probe_missing=game_probe_original_reference=game_probe_invalid=false;
  if(bad==5){player[0].items.weapon[0].id=2;player[0].items.weapon[0].power=11;}
  if(bad==6){weapons[221].by[7]^=1;}
  unsigned raw=raw_for(0);int result=start_draw(0,0,raw);if(bad==5){CHECK(result==1);emit(0,0,raw);}else CHECK(result!=1);
 }
}

static void transactions_and_writes(void)
{
 for(unsigned bad=0;bad<5;bad++) {
  setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);CHECK(global_vulcan_call.left>0);
  if(bad==0)global_vulcan_end();
  else {Uint8 color[168],mask[168];CHECK(reference_decode(spriteSheet8,raw,color,mask,NULL));unsigned k=first_cell(mask);int x=playerShotData[0].shotX+1+k%12,y=playerShotData[0].shotY+k/12;Uint8 *at=index_at(x,y);
   if(bad==4)at=index_at(0,0);*at=bad==1?color[k]^1:color[k];render_mirror_pixel(game_screen,at,color[k],bad==2?MIRROR_BLEND:MIRROR_NORMAL);if(bad==3)render_mirror_pixel(game_screen,at,color[k],MIRROR_NORMAL);}
  CHECK(global_vulcan_fault&&!global_vulcan_call.live);CHECK(owner_count()==0);
 }
 for(int style=0;style<3;style++){
  setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);CHECK(owner_count()>0);
  for(int y=0;y<14;y++)for(int x=0;x<12;x++){Uint8 *p=index_at(playerShotData[0].shotX+1+x,playerShotData[0].shotY+y),v=*p;if(style!=MIRROR_NORMAL)*p=(v&240)|((v&15)/2);render_mirror_pixel(game_screen,p,v,style);}
  CHECK(style==MIRROR_SHADOW?owner_count()>0:owner_count()==0);
 }
}
static void emit_talon(int x,int y)
{
 static const unsigned parts[]={0,1,19,20};for(unsigned part=0;part<4;part++){Uint8 color[168],mask[168];CHECK(reference_decode(spriteSheet9,233+parts[part],color,mask,NULL));for(unsigned i=0;i<168;i++)if(mask[i]){Uint8 *p=index_at(x+(part%2)*12+i%12,y+(part/2)*14+i/12);*p=color[i];render_mirror_pixel(game_screen,p,color[i],0);}}global_talon_end();CHECK(!global_talon_fault);
}
static void cross_family(void)
{
 for(unsigned reverse=0;reverse<2;reverse++)for(unsigned mutate=0;mutate<2;mutate++){
  setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);int x=playerShotData[0].shotX+1,y=playerShotData[0].shotY;
  if(!reverse){global_talon_pose(1,spriteSheet9,233,233,0);CHECK(render_mirror_global_player_ship(game_screen,x-6,y-7,spriteSheet9,233,0,1,233)==1);emit_talon(x-6,y-7);}
  CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);
  if(reverse){global_talon_pose(1,spriteSheet9,233,233,0);CHECK(render_mirror_global_player_ship(game_screen,x-6,y-7,spriteSheet9,233,0,1,233)==1);emit_talon(x-6,y-7);}
  for(size_t n=0;n<global_vulcan_capacity;n++)CHECK(!(global_vulcan_owner[n]&&global_talon_owner[n]));
  final_copy();Uint8 c[168],m[168];size_t rp[168];Sprite2_array bank=reverse?spriteSheet8:spriteSheet9;CHECK(reference_decode(bank,reverse?67:233,c,m,rp));size_t pos=rp[first_cell(m)];Uint8 saved=bank.data[pos];if(mutate)bank.data[pos]^=1;
  if(global_vulcan_finish_proof()!=!mutate)fprintf(stderr,"cross reverse=%u mutate=%u dependency=%d contributed=%d\n",reverse,mutate,global_vulcan_talon_dependency,global_vulcan_contributed);CHECK(global_vulcan_finish_proof()==!mutate);bank.data[pos]=saved;
 }
}
static void alpha_and_shadow(void)
{
 const unsigned recs[2]={221,227},mpos[2]={1,1};
 for(int d=4;d<=8;d+=4)for(unsigned phase=0;phase<2;phase++)for(unsigned sh=0;sh<2;sh++) {
  setup(valid_root,d);background2=true;shadowYDist=20;birth(0,recs[phase],1,mpos[phase]);unsigned raw=raw_for(0);CHECK(raw==global_vulcan_source[phase].index);
  int style=sh?MIRROR_SHADOW:MIRROR_NORMAL,x=playerShotData[0].shotX+1,y=playerShotData[0].shotY+(sh?shadowYDist:0),anchor=0;
  CHECK(start_draw(0,style,raw)==1);Uint8 color[168],mask[168];CHECK(reference_decode(spriteSheet8,raw,color,mask,NULL));
  for(int yy=0;yy<14*d;yy++)for(int xx=-d;xx<14*d;xx++) {
   int artx=xx+anchor*d;static const Uint8 zero[4]={0};const Uint8 *a=artx>=0&&artx<12*d?reference_frames[phase]+4*((yy*8/d)*96+artx*8/d):zero;
   bool native=xx>=0&&xx<12*d&&mask[(yy/d)*12+xx/d];Uint32 prior=palette_rgb(0x1b),want=prior;
   if(a[3]) {if(sh){Uint32 dark=palette_rgb((0x1b&240)|((0x1b&15)/2));Uint8 dark_rgba[4]={dark>>16,dark>>8,dark,255};want=reference_blend(prior,dark_rgba,a[3]);}else want=reference_blend(prior,a,a[3]);}
   CHECK(*rgba_at(x*d+xx,y*d+yy)==want);CHECK((global_vulcan_owner[(y*d+yy)*canvas->w+x*d+xx]!=0)==(a[3]||native));
  }
  emit(0,style,raw);CHECK(global_vulcan_finish_proof());
  if(sh){CHECK(start_draw(0,MIRROR_NORMAL,raw)==1);emit(0,MIRROR_NORMAL,raw);}
  CHECK(start_draw(0,style,raw)==0); /* Same native operator cannot replay. */
 }
}
static void every_record_byte(void)
{
 /* Change all 80 semantic bytes, including nonzero unused tails, via the
  * independent decoder. No production stamp is used to choose mutation. */
 for(unsigned i=0;i<80;i++){
  setup(valid_root,4);Uint8 saved=raw_records[0][0][i];raw_records[0][0][i]^=1;load_tables(0);raw_records[0][0][i]=saved;
  unsigned opens=asset_opens;uint64_t token=begin_birth(221,1);render_mirror_shot_allocated(0);initialize(0,221,1,1,token);render_mirror_front_create_end(token);CHECK(!global_vulcan_slots[0].role);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)!=1);CHECK(asset_opens==opens);
 }
 for(unsigned i=0;i<82;i++){
  setup(valid_root,4);Uint8 saved=raw_ports[0][i];raw_ports[0][i]^=1;load_tables(0);raw_ports[0][i]=saved;
  unsigned opens=asset_opens;uint64_t token=begin_birth(221,1);render_mirror_shot_allocated(0);initialize(0,221,1,1,token);render_mirror_front_create_end(token);CHECK(!global_vulcan_slots[0].role);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)!=1);CHECK(asset_opens==opens);
 }
}
static void retained_table_proof(void)
{
 for(unsigned stage=0;stage<3;stage++)for(unsigned bad=0;bad<3;bad++){
  setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(start_draw(0,0,raw)==1);emit(0,0,raw);final_copy();
  memset(global_vulcan_owner,0,(size_t)canvas->w*canvas->h);CHECK(global_vulcan_finish_proof());
  if(stage){CHECK(!global_vulcan_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(global_vulcan_cached);memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));ready=last_output_valid=true;}
  if(stage==2){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(have_fade_saved);}
  if(bad==0)weapons[221].by[7]^=1;else if(bad==1)weaponPort[7].cost++;else global_vulcan_front_port_valid=false;
  if(!stage)CHECK(!global_vulcan_finish_proof());else {global_vulcan_check_cache();CHECK(!ready&&!last_output_valid&&!global_vulcan_cached);}
 }
}

static void born_on_off_root_cases(void)
{
 for(unsigned on=0;on<2;on++)for(unsigned shadow=0;shadow<2;shadow++) {
  setup(valid_root,4);background2=true;shadowYDist=20;
  if(!on)CHECK(render_mirror_set_global_assets(NULL));
  birth(0,221,1,1);CHECK(global_vulcan_slots[0].role&&global_vulcan_slots[0].on==(on!=0));
  unsigned raw=raw_for(0),style=shadow?MIRROR_SHADOW:MIRROR_NORMAL;
  CHECK(render_mirror_set_global_assets(NULL));++mirror_logic_tick;
  CHECK(global_vulcan_slots[0].role&&global_vulcan_slots[0].on==(on!=0));
  CHECK(start_draw(0,style,raw)==(on?0:-1));
  CHECK(render_mirror_set_global_assets(valid_root));next_frame();
  CHECK(global_vulcan_slots[0].role&&global_vulcan_slots[0].on==(on!=0));
  CHECK(start_draw(0,style,raw)==(on?1:0));if(on)emit(0,style,raw);
  /* Genuine allocation revokes both classifications, not root changes. */
  shotAvail[0]=0;render_mirror_shot_allocated(0);CHECK(!global_vulcan_slots[0].role);
 }
 /* Born-on table failure is classic-only even if no resource root remains. */
 setup(valid_root,4);birth(0,221,1,1);unsigned raw=raw_for(0);CHECK(render_mirror_set_global_assets(NULL));
 weapons[221].by[7]^=1;++mirror_logic_tick;CHECK(start_draw(0,0,raw)==0);
}

static void rejected_birth_tombstones(void)
{
 for(unsigned on=0;on<2;on++)for(unsigned bad=0;bad<5;bad++) {
  setup(valid_root,4);if(!on)CHECK(render_mirror_set_global_assets(NULL));
  if(bad==0)weapons[221].sound^=1;
  uint64_t token=begin_birth(221,1);CHECK(token);render_mirror_shot_allocated(0);
  if(bad==1)weapons[221].shotrepeat^=1;
  initializer_mutation=bad==3?1:bad==4?2:0;
  initialize(0,221,1,1,bad==2?token+1:token);initializer_mutation=0;
  render_mirror_front_create_end(token);render_mirror_front_call_end();
  CHECK(global_vulcan_slots[0].claimed&&!global_vulcan_slots[0].role);
  unsigned raw=raw_for(0);CHECK(render_mirror_set_global_assets(NULL));++mirror_logic_tick;
  CHECK(start_draw(0,0,raw)==(on?0:-1));
  CHECK(render_mirror_set_global_assets(valid_root));next_frame();CHECK(start_draw(0,0,raw)==0);
  render_mirror_global_reset();CHECK(!global_vulcan_slots[0].claimed);CHECK(start_draw(0,0,raw)==-1);
 }
}

static void geometry_birth_rejection(void)
{
 for(unsigned bad=0;bad<5;bad++) {
  setup(valid_root,4);player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=1;
  render_mirror_front_call_begin(7,0,0,0,1,221);
  uint64_t token=render_mirror_front_create_begin(7,0,221,1);CHECK(token);
  if(bad)render_mirror_front_create_geometry(bad==1?token+1:token,bad==2?121:120,bad==3?91:90,bad==4?119:120,90);
  render_mirror_shot_allocated(0);initialize(0,221,1,1,token);
  render_mirror_front_create_end(token);render_mirror_front_call_end();
  CHECK(global_vulcan_slots[0].claimed&&!global_vulcan_slots[0].role);
  CHECK(start_draw(0,0,raw_for(0))==0);
 }
}

static void shared_dispatch_rejection(void)
{
 for(unsigned bad=0;bad<4;bad++) {
  setup(valid_root,4);player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=1;
  render_mirror_front_call_begin(7,0,0,0,1,221);
  CHECK(!synthetic_create_begin(bad==0?1:7,bad==1?1:0,bad==2?222:221,bad==3?2:1));
  CHECK(!global_vulcan_front_call.live);CHECK(!global_front_call.live);
  CHECK(!synthetic_create_begin(7,0,221,1));
  render_mirror_shot_allocated(0);initialize(0,221,1,1,0);CHECK(!global_vulcan_slots[0].claimed&&!global_vulcan_slots[0].role);
 }
}

int main(int argc,char **argv)
{
 CHECK(argc==3);valid_root=argv[1];fixture_root=argv[2];load_original();source_backup=malloc(spriteSheet8.size);CHECK(source_backup);memcpy(source_backup,spriteSheet8.data,spriteSheet8.size);load_frames();
 geometry_birth_rejection();shared_dispatch_rejection();rejected_birth_tombstones();born_on_off_root_cases();all_births();transactions_and_writes();cross_family();actual_allocator();actual_moving_allocator();actual_zero_graphic_reuse();birth_and_draw_boundaries();alpha_and_shadow();every_record_byte();retained_table_proof();invalid_births();invalid_draws();allocation_reuse();resources();source_mutations();cache_and_leases();fade_cases();geometry_cases();transferred_contributor_cases();
 global_vulcan_shutdown();global_shield_shutdown();global_talon_shutdown();free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(spriteSheet9.data);free(explosionSpriteSheet.data);free(spriteSheet8.data);free(source_backup);for(unsigned i=0;i<2;i++)free(reference_frames[i]);
 printf("PASS: %u cases, %u assertions; production Vulcan2 observer, not native engine proof\n",cases,checks);return 0;
}
