/* SPDX-License-Identifier: GPL-2.0-or-later
 * Current-production Shield22 observer. SDL is a bounded structural shim.
 * This test is not an integrated engine/gameplay/native-caller proof.
 * Original bytes arrive on stdin, remain in process memory and are never saved.
 */
/* SHOP owner is deliberately disabled in these battle-only shims. */
#define pregame_shop_pulse_set_directory(...) ((void)0)
#define pregame_shop_ship_set_directory(...) ((void)0)
#define shop_pulse_allocated(...) ((void)0)
#define shop_pulse_initialized(...) ((void)0)
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
static bool global_talon_frame,global_shield_frame,global_shield_fault,global_talon_shield_dependency;
static Uint8 *global_shield_owner,*global_shield_foreign;
static bool global_shield_source_matches(Sprite2_array);
static bool global_shield_palette_matches(void);
static Sprite2_array spriteSheet9,explosionSpriteSheet;
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
#include "global_shield_mirror.inc"
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
static void load_original(void)
{
 Uint32 n;read_exact(&n,4);CHECK(n==33484);spriteSheet9.size=n;spriteSheet9.data=malloc(n);CHECK(spriteSheet9.data);read_exact(spriteSheet9.data,n);
 read_exact(&n,4);CHECK(n==17810);explosionSpriteSheet.size=n;explosionSpriteSheet.data=malloc(n);CHECK(explosionSpriteSheet.data);read_exact(explosionSpriteSheet.data,n);
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
static Uint8 *source_backup;
static Uint8 *reference_frames[27];
static void load_frames(void)
{
 for(unsigned i=0;i<27;i++) {
  if(!global_shield_resource_ids[i])continue;
  const GlobalAssetResource *r=NULL;for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_shield_resource_ids[i])r=global_asset_resources+j;
  CHECK(r);char p[2048];snprintf(p,sizeof(p),"%s/%s",valid_root,r->path);FILE *f=fopen(p,"rb");CHECK(f);CHECK(!fseek(f,28,SEEK_SET));reference_frames[i]=malloc(96*112*4);CHECK(reference_frames[i]);CHECK(fread(reference_frames[i],1,96*112*4,f)==96*112*4);CHECK(fgetc(f)==EOF);fclose(f);
 }
}
static void setup(const char *root,int d)
{
 ++cases;global_shield_shutdown();global_talon_shutdown();
 free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);fade_saved=NULL;
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 game_probe_density=d;canvas=make_surface(320*d,200*d,32);output=make_surface(320*d,200*d,32);game_screen=make_surface(320,200,8);VGAScreenSeg=make_surface(320,200,8);VGAScreen=game_screen;
 size_t n=(size_t)canvas->w*canvas->h;hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,2);green_under=calloc(n,4);green_under_owner=calloc(n,1);CHECK(hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);
 memset(explosions,0,sizeof(explosions));memcpy(explosionSpriteSheet.data,source_backup,explosionSpriteSheet.size);
 game_probe_missing=game_probe_invalid=game_probe_original_reference=false;twoPlayerMode=false;shared_hud_frame=false;
 ready=last_output_valid=have_fade_saved=false;fade_mode=0;player[0].x=120;player[0].y=90;player[1].x=160;player[1].y=90;
 CHECK(render_mirror_set_global_assets(root));set_background();++mirror_logic_tick;global_talon_frame_begin();global_shield_frame_begin();CHECK(global_shield_frame);
}
static void next_frame(void)
{set_background();++mirror_logic_tick;global_talon_frame_begin();global_shield_frame_begin();CHECK(global_shield_frame);}
static void birth(unsigned slot,unsigned type,unsigned pnum)
{
 static const int dx[9]={-17,-5,7,19,-17,19,-17,-5,7},dy[9]={-12,-12,-12,-12,2,2,16,16,16};
 /* The actual original allocator chooses first free slot; reserve earlier slots. */
 for(unsigned i=0;i<slot;i++)if(!explosions[i].ttl)explosions[i].ttl=10;
 explosions[slot].ttl=0;JE_setupShieldExplosion(pnum,player[pnum-1].x+dx[type-14],player[pnum-1].y+dy[type-14],type);
 CHECK(global_shield_slots[slot].role);CHECK(explosions[slot].ttl==3);CHECK(global_shield_slots[slot].next_ttl==3);
}
static int start_draw(unsigned slot,int style)
{
 Explosion *e=explosions+slot;++e->sprite;
 return render_mirror_global_shield(game_screen,e->x,e->y,explosionSpriteSheet,e->sprite+1,style,slot);
}
static void emit(unsigned slot,int style)
{
 Explosion *e=explosions+slot;Uint8 color[168],mask[168];CHECK(reference_decode(explosionSpriteSheet,e->sprite+1,color,mask,NULL));
 for(unsigned i=0;i<168;i++)if(mask[i]) {
  int x=e->x+i%12,y=e->y+i/12;if(x<0||x>=320||y<0||y>=200)continue;
  Uint8 *at=index_at(x,y),source=color[i];
  *at=style==MIRROR_NORMAL?source:style==MIRROR_BLEND?(source&240)|(((source&15)+(*at&15))/2):(*at&240)|((*at&15)/2);
  render_mirror_pixel(game_screen,at,source,style);
 }
 global_shield_end();global_talon_end();--e->ttl;CHECK(!global_shield_fault);
}
static unsigned owner_count(void)
{unsigned n=0;for(size_t i=0;i<global_shield_capacity;i++)n+=global_shield_owner[i]!=0;return n;}
static void expected_rgba(unsigned slot,unsigned phase,int style)
{
 Explosion *e=explosions+slot;Uint8 color[168],mask[168];CHECK(reference_decode(explosionSpriteSheet,global_shield_phase_indices[phase],color,mask,NULL));
 const Uint8 *rgba=reference_frames[phase];int d=game_probe_density;
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++) {
  Uint32 want=palette_rgb(0x1b);const Uint8 *a=rgba?rgba+4*((ay*8/d)*96+ax*8/d):NULL;
  if(a&&a[3])want=reference_blend(want,a,style==MIRROR_BLEND?(a[3]+1u)/2u:a[3]);
  CHECK(*rgba_at(e->x*d+ax,e->y*d+ay)==want);
  bool support=a&&(a[3]||mask[(ay/d)*12+ax/d]);CHECK((global_shield_owner[(e->y*d+ay)*canvas->w+e->x*d+ax]!=0)==support);
 }
}
static void all_phases(void)
{
 for(int d=4;d<=8;d+=4)for(unsigned pnum=1;pnum<=2;pnum++)for(int style=0;style<2;style++)for(unsigned type=14;type<=22;type++) {
  setup(valid_root,d);twoPlayerMode=pnum==2;birth(0,type,pnum);
  for(unsigned phase=0;phase<3;phase++) {
   if(phase)next_frame();CHECK(start_draw(0,style)==1);expected_rgba(0,(type-14)*3+phase,style);emit(0,style);expected_rgba(0,(type-14)*3+phase,style);
   CHECK(global_shield_slots[0].next_ttl==2-phase);
  }
 }
}
static void invalid_births(void)
{
 for(unsigned bad=0;bad<12;bad++) {
  setup(valid_root,4);unsigned before=asset_opens;
  switch(bad) {
   case 0:JE_setupExplosion(103,78,0,14,false,true);break;
   case 1:render_mirror_shield_birth_begin(0,14,103,78,true);JE_setupExplosion(103,78,0,14,false,true);break;
   case 2:render_mirror_shield_birth_begin(3,14,103,78,true);JE_setupExplosion(103,78,0,14,false,true);break;
   case 3:render_mirror_shield_birth_begin(1,14,104,78,true);JE_setupExplosion(104,78,0,14,false,true);break;
   case 4:render_mirror_shield_birth_begin(1,14,103,79,true);JE_setupExplosion(103,79,0,14,false,true);break;
   case 5:render_mirror_shield_birth_begin(1,14,103,78,false);JE_setupExplosion(103,78,0,14,false,false);break;
   case 6:render_mirror_shield_birth_begin(1,14,103,78,true);JE_setupExplosion(103,78,1,14,false,true);break;
   case 7:render_mirror_shield_birth_begin(1,14,103,78,true);JE_setupExplosion(103,78,0,14,true,true);break;
   case 8:render_mirror_shield_birth_begin(1,14,103,78,true);JE_setupExplosion(103,78,0,15,false,true);break;
   case 9:render_mirror_shield_birth_begin(1,14,103,78,true);render_mirror_shield_birth_end();JE_setupExplosion(103,78,0,14,false,true);break;
   case 10:render_mirror_shield_birth_begin(1,13,103,78,true);JE_setupExplosion(103,78,0,14,false,true);break;
   case 11:render_mirror_shield_birth_begin(1,23,103,78,true);JE_setupExplosion(103,78,0,14,false,true);break;
  }
  CHECK(!global_shield_slots[0].role);CHECK(start_draw(0,MIRROR_NORMAL)==-1);CHECK(asset_opens==before);
 }
}
static void invalid_draws(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned bad=0;bad<20;bad++) {
  setup(valid_root,4);if(warm){birth(0,14,1);CHECK(start_draw(0,0)==1);emit(0,0);next_frame();}
  birth(0,14,1);Explosion *e=explosions;unsigned index=e->sprite+2;int x=e->x,y=e->y,style=0;Sprite2_array bank=explosionSpriteSheet;SDL_Surface *surface=game_screen;++e->sprite;
  unsigned before=asset_opens;Uint8 *copy=NULL;unsigned oldttl=global_shield_slots[0].next_ttl;
  switch(bad) {
   case 0:index++;break;case 1:e->ttl=2;break;case 2:e->fixedPosition=true;break;case 3:e->followPlayer=false;break;case 4:e->deltaY=1;break;
   case 5:x++;break;case 6:y++;break;case 7:style=MIRROR_SHADOW;break;case 8:bank.size--;break;
   case 9:copy=malloc(bank.size);CHECK(copy);memcpy(copy,bank.data,bank.size);bank.data=copy;break;
   case 10:surface=VGAScreenSeg;break;case 11:game_probe_original_reference=true;break;case 12:game_probe_missing=true;break;case 13:game_probe_invalid=true;break;
   case 14:rgb_palette[128]^=1;break;case 15:global_shield_slots[0].generation++;break;
   case 16:global_shield_slots[0].tick=mirror_logic_tick;break;case 17:global_shield_slots[0].next_ttl=1;break;
   case 18:e->sprite++;break;case 19:game_screen->pitch++;break;
  }
  CHECK(render_mirror_global_shield(surface,x,y,bank,index,style,0)==0);CHECK(asset_opens==before);free(copy);if(bad==19)game_screen->pitch--;
  (void)oldttl;
 }
}
static void phase_and_reuse(void)
{
 setup(valid_root,4);birth(0,14,1);CHECK(start_draw(0,0)==1);emit(0,0);
 CHECK(render_mirror_global_shield(game_screen,explosions[0].x,explosions[0].y,explosionSpriteSheet,229,0,0)==0);CHECK(!global_shield_slots[0].role);
 next_frame();CHECK(start_draw(0,0)==-1);
 setup(valid_root,4);birth(0,14,1);uint64_t gen=global_shield_slots[0].generation;explosions[0].ttl=0;JE_setupExplosion(103,78,0,14,false,true);CHECK(global_shield_slots[0].generation!=gen);CHECK(!global_shield_slots[0].role);CHECK(start_draw(0,0)==-1);
 setup(valid_root,4);birth(0,14,1);render_mirror_global_reset();CHECK(start_draw(0,0)==-1);
}
static void resources(void)
{
 char path[2048];const char *modes[]={"missing","corrupt","header","trailing"};
 for(unsigned mode=0;mode<4;mode++)for(unsigned n=0;n<22;n++) {
  snprintf(path,sizeof(path),"%s/%s%u",fixture_root,modes[mode],n);setup(path,4);birth(0,14,1);CHECK(start_draw(0,0)==0);CHECK(!global_shield_good);CHECK(owner_count()==0);
  unsigned before=asset_opens;next_frame();birth(0,14,1);CHECK(start_draw(0,0)==0);CHECK(asset_opens==before);
 }
 snprintf(path,sizeof(path),"%s/shield-only",fixture_root);setup(path,4);birth(0,14,1);CHECK(start_draw(0,0)==1);emit(0,0);CHECK(global_shield_good&&!global_talon_loaded);
}
static void source_mutations(void)
{
 for(unsigned warm=0;warm<2;warm++)for(unsigned t=0;t<27;t++) {
  setup(valid_root,4);if(warm){birth(0,14,1);CHECK(start_draw(0,0)==1);emit(0,0);next_frame();}
  unsigned idx=global_shield_source[t].index;size_t pos=explosionSpriteSheet.data[2*(idx-1)]+256u*explosionSpriteSheet.data[2*(idx-1)+1];Uint8 saved=explosionSpriteSheet.data[pos];explosionSpriteSheet.data[pos]^=0x10;
  birth(0,14,1);unsigned before=asset_opens;CHECK(start_draw(0,0)==0);CHECK(asset_opens==before);explosionSpriteSheet.data[pos]=saved;
 }
}
static void final_mapping(void)
{
 for(unsigned type=14;type<=22;type++) {
  setup(valid_root,4);birth(0,type,1);CHECK(start_draw(0,0)==1);emit(0,0);
  for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);
  bool keep=global_shield_compose(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(keep==(owner_count()!=0));
  memcpy(last_output_indices,VGAScreenSeg->pixels,64000);ready=last_output_valid=keep;global_shield_check_cache();CHECK(global_shield_cached==keep);
  if(keep){CHECK(global_shield_cache_source_matches());Uint8 *at=(Uint8 *)VGAScreenSeg->pixels+(explosions[0].y)*320+explosions[0].x-24;global_shield_final_pixel(VGAScreenSeg,at);CHECK(global_shield_cache_source_matches());}
 }
}
static void ordered_writes(void)
{
 for(int style=0;style<3;style++) {
  setup(valid_root,4);birth(0,15,1);CHECK(start_draw(0,0)==1);emit(0,0);CHECK(owner_count()>0);
  for(int y=0;y<14;y++)for(int x=0;x<12;x++) {
   Uint8 *p=index_at(explosions[0].x+x,explosions[0].y+y),v=*p;
   if(style==MIRROR_SHADOW)*p=(v&240)|((v&15)/2);else if(style==MIRROR_BLEND)*p=(v&240)|((v&15)/2);
   render_mirror_pixel(game_screen,p,v,style);
  }
  if(style!=MIRROR_SHADOW)CHECK(owner_count()==0);else CHECK(owner_count()>0);
 }
}
static void cache_and_leases(void)
{
 for(unsigned bad=0;bad<10;bad++) {
  setup(valid_root,4);birth(0,15,1);CHECK(start_draw(0,0)==1);emit(0,0);
  for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);
  CHECK(global_shield_compose(MIRROR_OUTPUT_ORDINARY,0,0));memcpy(last_output_indices,VGAScreenSeg->pixels,64000);ready=last_output_valid=true;
  SDL_Surface a=*canvas,b=*output,c=*game_screen,f=*VGAScreenSeg;SDL_PixelFormat fmt=*canvas->format;
  switch(bad){case 0:canvas->pitch++;break;case 1:output->pixels=NULL;break;case 2:game_screen->pitch++;break;case 3:VGAScreenSeg->pixels=NULL;break;case 4:canvas->format->BytesPerPixel=1;break;case 5:game_probe_density=8;break;case 6:rgb_palette[0]^=1;break;case 7:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;case 8:global_asset_directory[0]=0;break;case 9:explosionSpriteSheet.size--;break;}
  global_shield_check_cache();CHECK(!global_shield_cached&&!ready&&!last_output_valid);
  *canvas=a;*output=b;*game_screen=c;*VGAScreenSeg=f;*canvas->format=fmt;game_probe_density=4;if(bad==9)explosionSpriteSheet.size++;
 }
}
static void fresh_allocation(void)
{
 for(unsigned bad=0;bad<5;bad++) {
  setup(valid_root,4);unsigned opens=asset_opens;Explosion e={3,103,78,227,true,false,0};
  if(bad==0){explosions[0]=e;render_mirror_shield_birth_begin(1,14,103,78,true);render_mirror_explosion_initialized(0,14);CHECK(!global_shield_slots[0].role);}
  if(bad==1){explosions[0]=e;render_mirror_explosion_allocated(0);render_mirror_shield_birth_begin(1,14,103,78,true);render_mirror_explosion_initialized(0,14);CHECK(!global_shield_slots[0].role);}
  if(bad==2){render_mirror_explosion_allocated(0);++mirror_logic_tick;explosions[0]=e;render_mirror_shield_birth_begin(1,14,103,78,true);render_mirror_explosion_initialized(0,14);CHECK(!global_shield_slots[0].role);}
  if(bad==3){render_mirror_explosion_allocated(0);explosions[0]=e;render_mirror_explosion_initialized(0,14);render_mirror_shield_birth_begin(1,14,103,78,true);render_mirror_explosion_initialized(0,14);CHECK(!global_shield_slots[0].role);}
  if(bad==4){birth(0,14,1);CHECK(start_draw(0,0)==1);emit(0,0);unsigned next=global_shield_slots[0].next_ttl;uint64_t tick=global_shield_slots[0].tick;render_mirror_shield_birth_begin(1,14,103,78,true);render_mirror_explosion_initialized(0,14);CHECK(global_shield_slots[0].next_ttl==next&&global_shield_slots[0].tick==tick);}
  if(bad<4)CHECK(asset_opens==opens);
 }
}
static void transactions(void)
{
 for(unsigned bad=0;bad<5;bad++) {
  setup(valid_root,4);birth(0,15,1);CHECK(start_draw(0,0)==1);unsigned left=global_shield_call.left;CHECK(left>0);
  if(bad==0)global_shield_end();
  if(bad>=1&&bad<=3){Uint8 color[168],mask[168];CHECK(reference_decode(explosionSpriteSheet,232,color,mask,NULL));unsigned first=first_cell(mask);int x=explosions[0].x+first%12,y=explosions[0].y+first/12;Uint8 *at=index_at(x,y);*at=bad==1?color[first]^1:color[first];render_mirror_pixel(game_screen,at,color[first],bad==2?MIRROR_BLEND:MIRROR_NORMAL);if(bad==3)render_mirror_pixel(game_screen,at,color[first],MIRROR_NORMAL);}
  if(bad==4){Uint8 *at=index_at(0,0);render_mirror_pixel(game_screen,at,*at,MIRROR_NORMAL);}
  CHECK(global_shield_fault&&!global_shield_call.live);CHECK(owner_count()==0);
 }
}
static void emit_talon(int x,int y,unsigned index)
{
 static const unsigned parts[4]={0,1,19,20};
 for(unsigned part=0;part<4;part++){Uint8 color[168],mask[168];CHECK(reference_decode(spriteSheet9,index+parts[part],color,mask,NULL));for(unsigned i=0;i<168;i++)if(mask[i]){Uint8 *p=index_at(x+(part%2)*12+i%12,y+(part/2)*14+i/12);*p=color[i];render_mirror_pixel(game_screen,p,color[i],MIRROR_NORMAL);}}
 global_talon_end();CHECK(!global_talon_fault);
}
static void final_copy(void)
{for(int y=0;y<184;y++)memcpy((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264);upscale(output,VGAScreenSeg);}
static void cross_family(void)
{
 for(unsigned reverse=0;reverse<2;reverse++)for(unsigned invalid=0;invalid<2;invalid++) {
  setup(valid_root,4);birth(0,15,1);int tx=103,ty=78;
  if(!reverse){global_talon_pose(1,spriteSheet9,233,233,0);CHECK(render_mirror_global_player_ship(game_screen,tx,ty,spriteSheet9,233,0,1,233)==1);emit_talon(tx,ty,233);}
  CHECK(start_draw(0,0)==1);emit(0,0);
  if(reverse){global_talon_pose(1,spriteSheet9,233,233,0);CHECK(render_mirror_global_player_ship(game_screen,tx,ty,spriteSheet9,233,0,1,233)==1);emit_talon(tx,ty,233);}
  for(size_t n=0;n<global_shield_capacity;n++)CHECK(!(global_shield_owner[n]&&global_talon_owner[n]));
  CHECK(reverse?global_talon_shield_dependency:global_shield_talon_dependency);
  final_copy();Sprite2_array changed=reverse?explosionSpriteSheet:spriteSheet9;Uint8 dc[168],dm[168];size_t rawpos[168];CHECK(reference_decode(changed,229,dc,dm,rawpos));size_t pos=rawpos[first_cell(dm)];Uint8 before=changed.data[pos];
  if(invalid)changed.data[pos]^=1;
  bool talon=global_talon_compose(MIRROR_OUTPUT_ORDINARY,0,0),shield=global_shield_compose(MIRROR_OUTPUT_ORDINARY,0,0);
  if(invalid)CHECK(reverse?!talon:!shield);
  else {CHECK(talon||shield);for(int y=0;y<184*4;y++)for(int x=24*4;x<288*4;x++){size_t n=(size_t)y*canvas->w+x;if(global_shield_owner[n]||global_talon_owner[n])CHECK(((Uint32 *)output->pixels)[y*output->w+x-24*4]==*rgba_at(x,y));}}
  changed.data[pos]=before;
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
 setup(valid_root,d);birth(0,15,1);CHECK(start_draw(0,0)==1);emit(0,0);final_copy();CHECK(global_shield_compose(MIRROR_OUTPUT_ORDINARY,0,0));
 memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));ready=last_output_valid=true;
 SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(fade_saved&&fade_mode==1&&have_fade_saved&&last_output_valid&&global_shield_cached);
}
static void fade_cases(void)
{
 for(int d=4;d<=8;d+=4) {
  prepare_fade(d);size_t count=(size_t)output->w*output->h;Uint32 *before=malloc(count*4);CHECK(before);memcpy(before,output->pixels,count*4);
  for(unsigned i=0;i<256;i++){Uint32 v=rgb_palette[i],next=0;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;next|=(Uint32)(c+(0-c)/2)<<shift;}rgb_palette[i]=next;}
  render_mirror_fade_step(2);CHECK(ready&&global_shield_cached&&last_output_valid);
  for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++) {
   bool owned=x<264*d&&y<184*d&&hd_owner[(size_t)y*canvas->w+x+24*d];Uint32 want=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*320+x/d]);
   if(owned){Uint32 v=before[(size_t)y*output->w+x];want=0xff000000u;for(int shift=0;shift<24;shift+=8){int c=(v>>shift)&255;want|=(Uint32)(c+(0-c)/2)<<shift;}}
   CHECK(((Uint32 *)output->pixels)[(size_t)y*output->w+x]==want);
  }
  global_shield_check_cache();CHECK(global_shield_cached);free(before);
 }
 for(unsigned bad=0;bad<11;bad++) {
  prepare_fade(4);SDL_Surface c=*canvas,o=*output,f=*fade_saved,v=*VGAScreenSeg;SDL_PixelFormat fmt=*fade_saved->format;
  switch(bad){case 0:fade_saved->pixels=NULL;break;case 1:fade_saved->pixels=(Uint8 *)canvas->pixels+4;break;case 2:fade_saved->pitch++;break;case 3:fade_saved->w--;break;case 4:fade_saved->format->BytesPerPixel=1;break;case 5:canvas->pitch++;break;case 6:output->pixels=NULL;break;case 7:VGAScreenSeg->pitch++;break;case 8:rgb_palette[255]^=1;break;case 9:game_probe_density=8;break;case 10:((Uint8 *)VGAScreenSeg->pixels)[0]^=1;break;}
  render_mirror_fade_step(2);CHECK(!ready&&!last_output_valid&&!global_shield_cached&&!fade_mode&&!have_fade_saved);
  *canvas=c;*output=o;*fade_saved=f;*VGAScreenSeg=v;*fade_saved->format=fmt;game_probe_density=4;
 }
}
/* Model a later RGB consumer having taken every Shield owner bit. This is
 * not a HUD font simulation: native tests cover the actual underlay copy. */
static void transferred_contributor_cases(void)
{
 for(unsigned stage=0;stage<3;stage++)for(unsigned bad=0;bad<9;bad++) {
  setup(valid_root,4);birth(0,15,1);CHECK(start_draw(0,0)==1);emit(0,0);final_copy();
  CHECK(global_shield_contributed);memset(global_shield_owner,0,(size_t)canvas->w*canvas->h);
  CHECK(global_shield_finish_proof());
  SDL_Surface c=*canvas,o=*output,g=*game_screen,v=*VGAScreenSeg;
  Uint8 color[168],mask[168];size_t raw[168];CHECK(reference_decode(explosionSpriteSheet,229,color,mask,raw));size_t pos=raw[first_cell(mask)];
  if(stage) {
   CHECK(!global_shield_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(global_shield_cached);
   memcpy(last_output_indices,VGAScreenSeg->pixels,64000);memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));ready=last_output_valid=true;
   global_shield_check_cache();global_shield_check_cache();CHECK(ready&&last_output_valid&&global_shield_cached);
   if(stage==2){SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);CHECK(last_output_valid&&global_shield_cached&&have_fade_saved);
    for(unsigned i=0;i<256;i++){Uint32 v=rgb_palette[i],next=0;for(int shift=0;shift<24;shift+=8){int ch=(v>>shift)&255;next|=(Uint32)(ch+(0-ch)/2)<<shift;}rgb_palette[i]=next;}
    CHECK(global_shield_fade_step_valid(2));}
  }
  switch(bad) {
   case 0:explosionSpriteSheet.data[pos]^=1;break;
   case 1:rgb_palette[128]^=1;break;
   case 2:global_shield_fault=true;break;
   case 3:canvas->pitch+=4;break;
   case 4:output->pitch+=4;break;
   case 5:game_screen->pixels=(Uint8 *)game_screen->pixels+1;break;
   case 6:VGAScreenSeg->pitch++;break;
   case 7:CHECK(render_mirror_set_global_assets(NULL));break;
  }
  if(!stage) {
   if(bad==8)CHECK(global_shield_finish_proof());
   else if(bad==7)CHECK(!active&&!shared_hud_frame&&!ready&&!last_output_valid);
   else CHECK(!global_shield_finish_proof());
  } else {
   if(stage==1)global_shield_check_cache();else render_mirror_fade_step(2);
   if(bad==8)CHECK(ready&&last_output_valid&&global_shield_cached);
   else CHECK(!ready&&!last_output_valid&&!global_shield_cached&&!have_fade_saved&&!fade_mode);
  }
  *canvas=c;*output=o;*game_screen=g;*VGAScreenSeg=v;memcpy(explosionSpriteSheet.data,source_backup,explosionSpriteSheet.size);
  CHECK(render_mirror_set_global_assets(valid_root));next_frame();CHECK(!global_shield_contributed&&!global_shield_fault);
  birth(0,15,1);CHECK(start_draw(0,0)==1);emit(0,0);final_copy();CHECK(global_shield_finish_proof());CHECK(global_shield_compose(MIRROR_OUTPUT_ORDINARY,0,0));CHECK(global_shield_cached);
 }
}
static void geometry_cases(void)
{
 for(unsigned bad=0;bad<8;bad++) {
  setup(valid_root,4);global_shield_reset();SDL_Surface c=*canvas,o=*output,g=*game_screen,v=*VGAScreenSeg;
  switch(bad){case 0:canvas->pixels=(Uint8 *)canvas->pixels+1;break;case 1:output->pixels=(Uint8 *)canvas->pixels+4;break;case 2:game_screen->pixels=VGAScreenSeg->pixels;break;case 3:canvas->pitch++;break;case 4:VGAScreenSeg->pixels=canvas->pixels;break;case 5:output->pitch=1;break;case 6:game_screen->w--;break;case 7:game_probe_density=2;break;}
  global_shield_frame_begin();CHECK(!global_shield_frame);unsigned opens=asset_opens;birth(0,14,1);CHECK(start_draw(0,0)==0);CHECK(asset_opens==opens);
  *canvas=c;*output=o;*game_screen=g;*VGAScreenSeg=v;game_probe_density=4;
 }
}

int main(int argc,char **argv)
{
 CHECK(argc==3);valid_root=argv[1];fixture_root=argv[2];load_original();source_backup=malloc(explosionSpriteSheet.size);CHECK(source_backup);memcpy(source_backup,explosionSpriteSheet.data,explosionSpriteSheet.size);load_frames();
 all_phases();invalid_births();invalid_draws();phase_and_reuse();resources();source_mutations();final_mapping();ordered_writes();cache_and_leases();fresh_allocation();transactions();cross_family();fade_cases();geometry_cases();transferred_contributor_cases();
 global_shield_shutdown();global_talon_shutdown();free_surface(canvas);free_surface(output);free_surface(game_screen);free_surface(VGAScreenSeg);free_surface(fade_saved);
 free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(spriteSheet9.data);free(explosionSpriteSheet.data);free(source_backup);for(unsigned i=0;i<27;i++)free(reference_frames[i]);
 printf("PASS: %u cases, %u assertions; production Shield22 observer, not native engine proof\n",cases,checks);return 0;
}
