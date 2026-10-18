/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite offline fixture. It runs actual extracted production fixed-effect admission,
 * compositor, pixel ledger, indexed blitters and entity wrapper. No game loop,
 * pickup injection, event scheduler or RNG is present. Original data stays local.
 */
#include <SDL.h>
#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "data_pickup_glyph.h"
#include "fixed_pickup_flash.h"
/* Shared fixed-effect adapter: the flash runner selects this bounded profile. */
#ifdef FIXED_FLASH145
#define EFFECT_NAME "fixed flash145"
#define EFFECT_ID 145
#define EFFECT_SPRITE 144
#define EFFECT_TTL 7
#define EFFECT_TABLE 288
#define effect_rgba fixed_pickup_flash_rgba
#define effect_begin render_mirror_fixed_pickup_flash_begin
#define effect_source_matches fixed_pickup_flash_source_matches
#define effect_lease fixed_pickup_flash
#define OCCLUDE_X 150
#define OCCLUDE_Y 90
#else
#define EFFECT_NAME "DATA"
#define EFFECT_ID 266
#define EFFECT_SPRITE 265
#define EFFECT_TTL 14
#define EFFECT_TABLE 530
#define effect_rgba data_pickup_glyph_rgba
#define effect_begin render_mirror_data_value_begin
#define effect_source_matches data_value_source_matches
#define effect_lease data_fixed_value
#define OCCLUDE_X 148
#define OCCLUDE_Y 86
#endif
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned long checks;static unsigned cases,mirrored_calls,classic_calls,indexed_blits;
#include "actual_types.inc"
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
typedef struct {int unused;} G101Record,PCapRecord,Forest13Record;
typedef int EntityDrawStyle;typedef int EntityDrawLayout;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW,ENTITY_TILE,ENTITY_QUAD};
static SDL_Surface *canvas,*game_screen,*VGAScreen;
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;static Uint32 *green_under,*oracle;
static Uint8 selected[64000],expected[64000],restored_mask[64000];static Uint32 rgb_palette[256];
static bool active=true,suppress,suppress_green_smoke,suppress_cloud,scope=true;
static bool game_probe_known_blend=true,game_probe_local_blend=true,game_probe_original_reference,game_probe_missing,game_probe_invalid,xmas;
static int game_probe_density=8;static const char *game_probe_assets="fixture",*reject_reason;
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value,data_fixed_value,fixed_pickup_flash;
static unsigned draws,occlusions,local_entities,local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[128];static unsigned region_count;
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[8];static unsigned green_head_count;
typedef struct {Uint16 peak[16][14];} GreenBackground;
static Sprite2_array explosionSpriteSheet,spriteSheet9,spriteSheet8,spriteSheet12;
static void font_before_effect(SDL_Rect r){(void)r;}
static void render_mirror_shadow_end(void){}
static bool mirror_enabled(void){return scope;}
static void render_mirror_unsupported(const char *s){reject_reason=s;}
static void game_probe_restore_region(unsigned b,SDL_Rect req,SDL_Rect r,unsigned g,unsigned n){(void)b;(void)req;(void)r;(void)g;(void)n;}
#define ground101_select(...) abort()
#define plateau_cap_select(...) abort()
#define forest13_select(...) abort()
static Uint32 palette_rgb(Uint8 index);
static int explosion_asset_slot(unsigned index);
#include "actual_compositor.inc"
#include "actual_adapter.inc"
#define game_probe_scene_draw(...) ((void)0)
#include "actual_entity.inc"
#define storm_pixel(...) ((void)0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
#define font_pixel(...) false
#define vulcan_shadow_clear(...) ((void)0)
#define vulcan_shadow_pixel(...) false
#include "actual_pixel.inc"
static void game_probe_blend_write(bool known,unsigned index,int ox,int oy,int x,int y,Uint8 before,Uint8 src,Uint8 after,unsigned sub,unsigned blocks,bool rgba){(void)known;(void)index;(void)ox;(void)oy;(void)x;(void)y;(void)before;(void)src;(void)after;(void)sub;(void)blocks;(void)rgba;}
#include "actual_blend.inc"
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define asset_debug_effect(...) ((void)0)
#define load_font_arrow_sprite_end(...) ((void)0)
#define pregame_font_sprite2_end(...) ((void)0)
#define blit_sprite2 indexed_sprite2
#define blit_sprite2_blend indexed_sprite2_blend
#include "actual_blit.inc"
#undef blit_sprite2
#undef blit_sprite2_blend
static void blit_sprite2(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){indexed_blits++;indexed_sprite2(s,x,y,b,i);}
static void blit_sprite2_blend(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){indexed_blits++;indexed_sprite2_blend(s,x,y,b,i);}
#include "actual_end.inc"
#define game_probe_draw(role,index,x,y,style,layout,mirrored) do{(void)(role);if(mirrored)mirrored_calls++;else classic_calls++;}while(0)
#define blit_sprite2x2(...) abort()
#define blit_sprite2x2_blend(...) abort()
#define blit_sprite2x2_darken(...) abort()
#define blit_sprite2_darken(...) abort()
#include "actual_wrapper.inc"
static Uint8 source[168],coverage[168],bank[17810];
static Uint32 rgba_at(unsigned x,unsigned y){return ((Uint32*)((Uint8*)canvas->pixels+y*canvas->pitch))[x];}
static void reset(void)
{
 active=scope=true;reject_reason=NULL;game_probe_density=8;game_probe_assets="fixture";
 game_probe_missing=game_probe_invalid=game_probe_original_reference=xmas=false;
 suppress=suppress_green_smoke=suppress_cloud=false;data_fixed_value=fixed_pickup_flash=false;
 region_count=green_head_count=draws=occlusions=local_entities=local_regions=local_blocks=expanded_regions=boundary_crossings=0;
 memset(hd_owner,0,320*200*64);memset(cloud_owner,0,320*200*64);memset(green_first,0,320*200*64*2);memset(selected,0,sizeof(selected));
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  Uint8 q=(Uint8)(0x30+(x/11+y/9)%16);((Uint8*)game_screen->pixels)[y*320+x]=expected[y*320+x]=q;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)((Uint32*)((Uint8*)canvas->pixels+(y*8+sy)*canvas->pitch))[x*8+sx]=palette_rgb(q);
 }
}
/* Independent reference for RGBA color and coverage, not production helper calls. */
static Uint32 over(Uint32 under,const Uint8 *p,bool blend)
{
 unsigned color[3]={p[0],p[1],p[2]};
 if(blend) {
  unsigned peak=MAX(color[0],MAX(color[1],color[2]));
  unsigned back=MAX((under>>16)&255,MAX((under>>8)&255,under&255));
  unsigned value=(peak+back+1)/2;
  for(int c=0;c<3;c++)color[c]=peak?(color[c]*value+peak/2)/peak:0;
 }
 Uint32 out=0xff000000u;
 for(int c=0;c<3;c++){unsigned shift=16-c*8;out|=((((under>>shift)&255)*(255-p[3])+color[c]*p[3]+127)/255)<<shift;}
 return out;
}
static void before_draw(int x,int y,int style,Uint8 index_after[64000])
{
 memcpy(index_after,game_screen->pixels,64000);
 for(int ay=0;ay<14;ay++)for(int ax=0;ax<12;ax++)if(coverage[ay*12+ax]&&y+ay>=0&&y+ay<200) {
  unsigned n=(unsigned)((y+ay)*320+x+ax);Uint8 v=source[ay*12+ax];
  index_after[n]=style==ENTITY_BLEND?(Uint8)((v&240)|(((v&15)+(index_after[n]&15))/2)):v;
 }
 memcpy(oracle,canvas->pixels,320*200*64*4);
 const Uint8 *p=effect_rgba(rgb_palette);
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int dx=x*8+ax,dy=y*8+ay;if(dx<0||dy<0||dx>=2560||dy>=1600)continue;
  unsigned n=(unsigned)(dy*2560+dx);const Uint8 *q=p+4*(ay*96+ax);if(q[3])oracle[n]=over(oracle[n],q,style==ENTITY_BLEND);
 }
}
static void compare_index(const Uint8 *after)
{
 CHECK(!memcmp(game_screen->pixels,after,64000));CHECK(!memcmp(expected,after,64000));
}
static void compare_rgba(void)
{
 CHECK(!reject_reason);CHECK(!memcmp(canvas->pixels,oracle,320*200*64*4));
}
static void native_capture(const char *out,const char *name)
{
 SDL_Surface *native=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);CHECK(native);
 SDL_Renderer *r=SDL_CreateSoftwareRenderer(native);CHECK(r);
 SDL_Texture *t=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,2560,1600);CHECK(t);
 CHECK(!SDL_SetTextureScaleMode(t,SDL_ScaleModeNearest));CHECK(!SDL_SetTextureBlendMode(t,SDL_BLENDMODE_NONE));
 CHECK(!SDL_UpdateTexture(t,NULL,canvas->pixels,canvas->pitch));CHECK(!SDL_RenderCopy(r,t,NULL,NULL));SDL_RenderPresent(r);
 char path[2048];CHECK(snprintf(path,sizeof(path),"%s/%s.bmp",out,name)<(int)sizeof(path));CHECK(!SDL_SaveBMP(native,path));
 SDL_DestroyTexture(t);SDL_DestroyRenderer(r);SDL_FreeSurface(native);
}
static void positive(int x,int y,int style,unsigned ttl,bool overlapping)
{
 reset();Uint8 after[64000];
 if(overlapping) {
  /* Authored prior HD detail and cloud/green ownership behind the entire tile. */
  for(int ay=MAX(0,y*8);ay<MIN(1600,(y+14)*8);ay++)for(int ax=x*8;ax<(x+12)*8;ax++) {
   unsigned n=(unsigned)(ay*2560+ax);((Uint32*)canvas->pixels)[n]=0xff000000u|((ax*13u+ay*7u)&0xffffffu);hd_owner[n]=cloud_owner[n]=1;green_first[n]=0;
  }
 }
 before_draw(x,y,style,after);unsigned prev=mirrored_calls,blits=indexed_blits;
 effect_begin(true,false,0,EFFECT_SPRITE,ttl);
 draw_entity_sprite2(game_screen,x,y,explosionSpriteSheet,EFFECT_ID,style,ENTITY_TILE);
 CHECK(mirrored_calls==prev+1);CHECK(indexed_blits==blits+1);CHECK(!effect_lease&&!suppress);compare_index(after);compare_rgba();
 const Uint8 *art=effect_rgba(rgb_palette);
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int dx=x*8+ax,dy=y*8+ay;if(dx<0||dy<0||dx>=2560||dy>=1600)continue;
  bool painted=art[4*(ay*96+ax)+3]||coverage[(ay/8)*12+ax/8];
  CHECK(cloud_owner[dy*2560+dx]==(overlapping&&!painted));
 }

 for(int ay=0;ay<14;ay++)for(int ax=0;ax<12;ax++)if(coverage[ay*12+ax]&&y+ay>=0&&y+ay<200) {
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)CHECK(hd_owner[((y+ay)*8+sy)*2560+(x+ax)*8+sx]==1);
 }
 ++cases;
}
static void fallback(int kind,int style)
{
 reset();Uint8 after[64000];before_draw(144,83,style,after);
 bool fixed=true,follow=false;int dy=0;unsigned ttl=EFFECT_TTL;
 switch(kind) {
  case 0:fixed=false;break;case 1:follow=true;break;case 2:dy=1;break;
  case 3:ttl=0;break;case 4:ttl=EFFECT_TTL+1;break;case 5:game_probe_missing=true;break;
  case 6:game_probe_invalid=true;break;case 7:game_probe_original_reference=true;break;
  default:scope=false;break;
 }
 unsigned hd=mirrored_calls,classic=classic_calls,blits=indexed_blits;
 effect_begin(fixed,follow,dy,EFFECT_SPRITE,ttl);
 draw_entity_sprite2(game_screen,144,83,explosionSpriteSheet,EFFECT_ID,style,ENTITY_TILE);
 CHECK(mirrored_calls==hd&&classic_calls==classic+1);CHECK(indexed_blits==blits+1);CHECK(!effect_lease&&!suppress);compare_index(after);
 for(int ay=83*8;ay<97*8;ay++)for(int ax=144*8;ax<156*8;ax++) {
  CHECK(rgba_at((unsigned)ax,(unsigned)ay)==palette_rgb(after[(ay/8)*320+ax/8]));
  CHECK(!hd_owner[ay*2560+ax]);
 }
 ++cases;
}

static bool admit(SDL_Surface *surface,int x,int y,Sprite2_array b,unsigned index,int style,int layout)
{
 effect_begin(true,false,0,EFFECT_SPRITE,EFFECT_TTL);
 bool ok=render_mirror_entity(surface,x,y,b,index,style,layout);CHECK(!effect_lease);render_mirror_entity_end();++cases;return ok;
}
static void negatives(void)
{
 reset();effect_begin(true,false,0,EFFECT_SPRITE,EFFECT_TTL);render_mirror_entity_end();CHECK(!effect_lease);
 CHECK(explosion_asset_slot(266)<0);CHECK(explosion_asset_slot(145)<0);
 for(unsigned i=146;i<=152;i++)CHECK(explosion_asset_slot(i)==91+(int)i-146);
 CHECK(!render_mirror_entity(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 for(unsigned ttl=0;ttl<=EFFECT_TTL+1;ttl++)if(ttl==0||ttl==EFFECT_TTL+1) {
  effect_begin(true,false,0,EFFECT_SPRITE,ttl);CHECK(!render_mirror_entity(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 }
 CHECK(!admit(game_screen,-1,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 CHECK(!admit(game_screen,309,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 CHECK(!admit(game_screen,30,-14,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 CHECK(!admit(game_screen,30,200,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_SHADOW,ENTITY_TILE));
 CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_QUAD));
 CHECK(!admit(game_screen,30,40,spriteSheet8,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 CHECK(!admit(game_screen,30,40,(Sprite2_array){0,NULL},EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_SPRITE,ENTITY_NORMAL,ENTITY_TILE));
 SDL_Surface other=*game_screen;CHECK(!admit(&other,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 int old=game_screen->pitch;game_screen->pitch=324;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));game_screen->pitch=old;
 old=game_screen->format->BitsPerPixel;game_screen->format->BitsPerPixel=32;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));game_screen->format->BitsPerPixel=(Uint8)old;
#ifdef FIXED_FLASH145
 void *pixels=game_screen->pixels;game_screen->pixels=NULL;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));game_screen->pixels=pixels;
 Uint32 format=game_screen->format->format;game_screen->format->format=SDL_PIXELFORMAT_RGB332;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));game_screen->format->format=format;
 SDL_Surface *saved_canvas=canvas;canvas=NULL;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));canvas=saved_canvas;
 pixels=canvas->pixels;canvas->pixels=NULL;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));canvas->pixels=(Uint8*)pixels+1;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));canvas->pixels=pixels;
 old=canvas->pitch;canvas->pitch=INT_MAX&~3;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));canvas->pitch=old;
 pixels=canvas->pixels;canvas->pixels=game_screen->pixels;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));canvas->pixels=pixels;
 format=canvas->format->format;canvas->format->format=SDL_PIXELFORMAT_RGBA8888;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));canvas->format->format=format;
 int *dimensions[]={&canvas->w,&canvas->h,&canvas->pitch};for(unsigned i=0;i<3;i++){old=*dimensions[i];--*dimensions[i];CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));*dimensions[i]=old;}
 Uint8 **owners[]={&hd_owner,&cloud_owner,&green_under_owner};for(unsigned i=0;i<3;i++){Uint8 *saved=*owners[i];*owners[i]=NULL;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));*owners[i]=saved;}
 Uint16 *first=green_first;green_first=NULL;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));green_first=first;
 Uint16 *aligned=green_first;green_first=(Uint16*)((Uint8*)aligned+1);CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));green_first=aligned;
 Uint32 *aligned_under=green_under;green_under=(Uint32*)((Uint8*)aligned_under+1);CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));green_under=aligned_under;
 Uint32 *under=green_under;green_under=NULL;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));green_under=under;
#endif
 bool *gates[]={&active,&scope,&game_probe_missing,&game_probe_invalid,&game_probe_original_reference,&xmas};
 for(unsigned i=0;i<sizeof(gates)/sizeof(gates[0]);i++) {
  bool prev=*gates[i];*gates[i]=!prev;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));*gates[i]=prev;
 }
 reject_reason="prior";CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));reject_reason=NULL;
 game_probe_density=4;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));game_probe_density=8;
 game_probe_assets=NULL;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));game_probe_assets="fixture";
 size_t size=explosionSpriteSheet.size;explosionSpriteSheet.size=EFFECT_TABLE+1;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));explosionSpriteSheet.size=size;
 Uint8 alternate[17810];memcpy(alternate,bank,sizeof(bank));Sprite2_array b={sizeof(bank),alternate};CHECK(!admit(game_screen,30,40,b,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 /* Same-address source changes must revoke warm admission immediately. */
 size_t start=bank[EFFECT_TABLE]|((size_t)bank[EFFECT_TABLE+1]<<8);Uint8 save=bank[start+1];bank[start+1]^=1;
 CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));bank[start+1]=save;
 save=bank[start];bank[start]=15;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));bank[start]=save;
 save=bank[EFFECT_TABLE];bank[EFFECT_TABLE]=255;CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));bank[EFFECT_TABLE]=save;
 /* Mutate one actual covered palette index, independently of RLE coverage. */
 size_t raw=start;while(bank[raw]!=15&&!(bank[raw]>>4))raw++;
 CHECK(bank[raw]!=15);++raw;save=bank[raw];bank[raw]^=1;
 CHECK(!admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));bank[raw]=save;
 CHECK(admit(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
 /* Wrong ID consumes the lease; the next valid draw does not inherit it. */
 effect_begin(true,false,0,EFFECT_SPRITE,EFFECT_TTL);
 CHECK(!render_mirror_entity(game_screen,30,40,explosionSpriteSheet,EFFECT_ID+1,ENTITY_NORMAL,ENTITY_TILE));
 CHECK(!effect_lease);
 CHECK(!render_mirror_entity(game_screen,30,40,explosionSpriteSheet,EFFECT_ID,ENTITY_NORMAL,ENTITY_TILE));
}
int main(int argc,char **argv)
{
 CHECK(argc==4);CHECK(SDL_Init(SDL_INIT_VIDEO)==0);char path[2048];FILE *f;
 CHECK(snprintf(path,sizeof(path),"%s/newsh6.shp",argv[1])<(int)sizeof(path));f=fopen(path,"rb");CHECK(f&&fread(bank,1,sizeof(bank),f)==sizeof(bank)&&fgetc(f)==EOF);fclose(f);
 explosionSpriteSheet=(Sprite2_array){sizeof(bank),bank};spriteSheet8=(Sprite2_array){sizeof(bank),bank+1};
 CHECK(snprintf(path,sizeof(path),"%s/palette.dat",argv[1])<(int)sizeof(path));f=fopen(path,"rb");CHECK(f);for(int i=0;i<256;i++){Uint8 p[3];CHECK(fread(p,1,3,f)==3);rgb_palette[i]=0;for(int c=0;c<3;c++)rgb_palette[i]|=(Uint32)((p[c]<<2)|(p[c]>>4))<<(16-c*8);}fclose(f);
 CHECK(decode_tile(explosionSpriteSheet,EFFECT_ID,source,coverage,12,0,0));CHECK(effect_source_matches(explosionSpriteSheet));
 game_screen=VGAScreen=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);CHECK(game_screen);
 canvas=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);CHECK(canvas);
 hd_owner=calloc(320*200*64,1);cloud_owner=calloc(320*200*64,1);green_under_owner=calloc(320*200*64,1);green_first=calloc(320*200*64,2);green_under=calloc(320*200*64,4);oracle=malloc(320*200*64*4);CHECK(hd_owner&&cloud_owner&&green_under_owner&&green_first&&green_under&&oracle);
 for(int style=0;style<=1;style++)for(unsigned ttl=EFFECT_TTL;ttl>0;ttl--)positive(144,83,style,ttl,ttl%2==0);
 positive(0,-13,ENTITY_NORMAL,EFFECT_TTL,false);positive(308,199,ENTITY_BLEND,1,false);positive(308,186,ENTITY_NORMAL,EFFECT_TTL,false);
 for(int style=0;style<=1;style++)for(int kind=0;kind<9;kind++)fallback(kind,style);
 negatives();
 /* Back-to-back original hooks cannot cross-bind DATA266 and fixed145. */
 reset();render_mirror_data_value_begin(true,false,0,144,7);render_mirror_fixed_pickup_flash_begin(true,false,0,144,7);
 CHECK(!data_fixed_value&&fixed_pickup_flash);CHECK(render_mirror_entity(game_screen,30,40,explosionSpriteSheet,145,ENTITY_NORMAL,ENTITY_TILE));render_mirror_entity_end();
 render_mirror_data_value_begin(true,false,0,265,14);render_mirror_fixed_pickup_flash_begin(true,false,0,265,14);
 CHECK(data_fixed_value&&!fixed_pickup_flash);CHECK(render_mirror_entity(game_screen,50,40,explosionSpriteSheet,266,ENTITY_NORMAL,ENTITY_TILE));render_mirror_entity_end();
 CHECK(!data_fixed_value&&!fixed_pickup_flash);cases+=2;
 /* Repeated draw/restore and post-effect normal occlusion use actual ledgers. */
 positive(144,83,ENTITY_BLEND,EFFECT_TTL,true);restore_classic_rect((SDL_Rect){OCCLUDE_X,OCCLUDE_Y,1,1});CHECK(!boundary_crossings&&local_regions==1);
 for(int y=83*8;y<97*8;y++)for(int x=144*8;x<156*8;x++){CHECK(rgba_at((unsigned)x,(unsigned)y)==palette_rgb(((Uint8*)game_screen->pixels)[(y/8)*320+x/8]));CHECK(!hd_owner[y*2560+x]);}
 positive(144,83,ENTITY_NORMAL,EFFECT_TTL,true);Uint8 *at=(Uint8*)game_screen->pixels+OCCLUDE_Y*320+OCCLUDE_X;*at=0x7d;render_mirror_pixel(game_screen,at,*at,MIRROR_NORMAL);CHECK(!selected[OCCLUDE_Y*320+OCCLUDE_X]);CHECK(!hd_owner[(OCCLUDE_Y*8)*2560+OCCLUDE_X*8]);
 /* Preview from the real nearest SDL software presenter, at native 640x400.
  * Both use synthetic scenery; filenames explicitly describe fixture evidence. */
 reset();blit_sprite2(game_screen,144,83,explosionSpriteSheet,EFFECT_ID);native_capture(argv[2],"fixture-before-native640");
 positive(144,83,ENTITY_NORMAL,EFFECT_TTL,false);native_capture(argv[2],"fixture-after-native640");
 CHECK(snprintf(path,sizeof(path),"%s/adapter-%s-receipt.json",argv[2],argv[3])<(int)sizeof(path));f=fopen(path,"w");CHECK(f);fprintf(f,"{\"cases\":%u,\"checks\":%lu,\"mirrored_draws\":%u,\"classic_draws\":%u,\"ttl_each_style\":%u,\"native\":\"SDL nearest software, synthetic scenery, no gameplay loop\"}\n",cases,checks,mirrored_calls,classic_calls,EFFECT_TTL);fclose(f);
 printf("%s actual blitter/compositor: %u cases, %lu checks; exact INDEX8 + RGBA, native SDL preview passed (%s)\n",EFFECT_NAME,cases,checks,argv[3]);
 free(oracle);free(green_under);free(green_first);free(green_under_owner);free(cloud_owner);free(hd_owner);SDL_FreeSurface(canvas);SDL_FreeSurface(game_screen);SDL_Quit();return 0;
}
