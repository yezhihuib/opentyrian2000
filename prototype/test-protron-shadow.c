/* Exact extracted loader/hook/wrapper/compositor/RLE with independent RGBA,
 * physical-address and ownership oracles. Unit only: no game or capture. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int unused;} G101Record,PCapRecord,Forest13Record;
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};

#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "types.inc"
#include "shadow-types.inc"
typedef struct {Uint8 r,g,b,a;} SDL_Color;
typedef struct {int unused;} SDL_Renderer;
typedef struct {int unused;} SDL_Texture;
static bool xmas;
static bool active=true,suppress,suppress_green_smoke,suppress_cloud,game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend;
static const char *game_probe_assets,*reject_reason,*full_pack,*work;
static int game_probe_density=8;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},display,output_surface,fade_surface,*game_screen=&screen,*VGAScreen=&screen,*VGAScreenSeg=&screen,*canvas=&display,*output=&output_surface,*fade_saved=&fade_surface;
static SDL_Texture texture_value,*texture=&texture_value;
static bool ready,last_output_valid,have_fade_saved,have_initial_palette,last_output_scene_hd,manual_hd_enabled,game_probe_skip,game_probe_repeat,game_probe_coverage_fault;
static int fade_mode;static Uint32 initial_palette[256],last_output_palette[256],fade_saved_palette[256];static Uint8 last_output_indices[64000];
static unsigned mismatch,brightness_blocks,restored_checks,restored_mismatches,game_probe_tick,sdl_present_calls,probe_present_calls;
static Uint8 hud_output_owner[64000],hud_saved_owner[64000],component_output_owner[64000],component_saved_owner[64000],indicator_output_owner[237],indicator_saved_owner[237],fixed_text_output_owner[370],fixed_text_saved_owner[370],font_powner[1],font_psaved_owner[1];
static Uint32 hud_output_palette[256],component_output_palette[256],indicator_output_palette[256],fixed_text_output_palette[256],font_output_palette[256];
static uint64_t hud_generation,hud_output_generation,hud_saved_generation,component_generation,component_output_generation,component_saved_generation,indicator_generation,indicator_output_generation,indicator_saved_generation,fixed_text_generation,fixed_text_output_generation,fixed_text_saved_generation,font_generation,font_output_generation,font_saved_generation,indicator_under_generation,indicator_saved_under_generation;
static Uint32 indicator_under[82][64],indicator_saved_under[82][64];static Uint8 indicator_under_owner[82],indicator_saved_under_owner[82];
#define mirror_enabled() true
#define render_mirror_hud_reset() ((void)0)
#define hud_begin() ((void)0)
#define hud_check_mode() ((void)0)
#define ground101_frame_reset() ((void)0)
#define ground101_frame_report(...) ((void)0)
#define asset_debug_fast_forward() false
#define SDL_PIXELFORMAT_ARGB8888 0
#define SDL_TEXTUREACCESS_STREAMING 0
#define SDL_ScaleModeNearest 0
#define SDL_BLENDMODE_NONE 0
#define SDL_CreateRGBSurfaceWithFormat(...) (assert(0),(SDL_Surface*)NULL)
#define SDL_CreateTexture(...) (assert(0),(SDL_Texture*)NULL)
#define SDL_SetTextureScaleMode(...) 0
#define SDL_SetTextureBlendMode(...) 0
#define SDL_SetRenderDrawColor(r,a,b,c,d) ((void)(r),0)
#define SDL_RenderClear(...) 0
#define SDL_RenderCopy(r,t,s,d) ((void)(r),(void)(t),(void)(s),(void)(d),0)
#define SDL_UnlockTexture(...) ((void)0)
#define asset_debug_readback(...) ((void)0)
#define SDL_RenderPresent(...) ((void)sdl_present_calls++)
#define mt_state_fingerprint() UINT64_C(0x57a7192098)
#define font_cached() false
#define font_cached_indices_match() true
#define fixed_text_cached_indices_match() true
#define indicators_cached_indices_match() true
#define indicators_underlay_matches() true
#define hud_cached_indices_match() true
#define components_cached_indices_match() true
#define font_clear_cached(...) ((void)0)
#define fixed_text_clear_cached() ((void)0)
#define indicators_clear_cached(...) ((void)0)
#define hud_clear_cached() ((void)0)
#define components_clear_cached(...) ((void)0)
#define font_fade_save() ((void)0)
#define font_fade_underlay(...) ((void)0)
#define indicators_fade_underlay(...) ((void)0)
#define game_probe_fade_sample(o,s,p,m) ((void)(o),(void)(s),(void)(p),(void)(m))
#define indicator_cell(...) (-1)
#define hud_fixed_text_cell(...) (-1)
#define font_pcell(...) (-1)
#define font_prepare_finish() ((void)0)
#define game_probe_effects(...) ((void)0)
#define hud_compose() false
#define components_compose() false
#define indicators_compose() false
#define fixed_text_compose() false
#define font_finish(...) false
#define game_probe_rgb_audit(o,n) ((void)(o),(void)(n))
#define game_probe_frame(...) ((void)0)
#define game_probe_capture_tick() false
#define game_probe_export(...) ((void)0)
static void *texture_pixels;static int texture_pitch;
static int SDL_LockTexture(SDL_Texture*t,const SDL_Rect*r,void**p,int*pitch){(void)t;(void)r;*p=texture_pixels;*pitch=texture_pitch;return 0;}
static void game_probe_present(int count,uint64_t a,uint64_t b){assert(a==b);assert(count==(game_probe_repeat?2:1));probe_present_calls++;}
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static Uint8 expected[64000],selected[64000],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;static Uint32 *green_under;
typedef struct {Asset *asset;int x,y;} GreenHead;static GreenHead green_heads[256];
typedef struct {Uint16 peak[16][14];} GreenBackground;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;static HdRegion regions[256];
static unsigned green_head_count,region_count,draws,occlusions,local_entities;
static TalonBank talon_banks[2];static unsigned banking_draw_player;static uint64_t mirror_logic_tick;
static const int original_visual_indices[5]={0,2,6,10,12};
static unsigned original_calls,end_calls,scene_calls,player_calls,font_calls;
static unsigned log_id;static int log_role,log_x,log_y;static bool log_mirrored;
#define ground101_select(...) assert(0)
#define plateau_cap_select(...) assert(0)
#define forest13_select(...) assert(0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define load_font_arrow_sprite_begin(...) ((void)0)
#define load_font_arrow_sprite_end(...) ((void)0)
void render_mirror_unsupported(const char *s);
static bool font_force_reject;
static void font_before_effect(SDL_Rect r){assert(r.w>0&&r.h>0);font_calls++;if(font_force_reject)render_mirror_unsupported("fixture-font");}
static bool font_pixel(int x,int y,Uint8 p,int style){(void)x;(void)y;(void)p;(void)style;return false;}
static bool game_probe_known_blend;
static Uint8 restored_mask[64000];
static unsigned local_blocks,local_regions,expanded_regions,boundary_crossings,blend_source_index;
static void game_probe_restore_region(unsigned source,SDL_Rect requested,SDL_Rect restored,unsigned groups,unsigned blocks)
{(void)source;(void)requested;(void)restored;(void)groups;(void)blocks;}
static Uint32 palette_rgb(Uint8 index);
static char all_rejections[512];
void render_mirror_unsupported(const char *s);
static Uint16 SDL_SwapLE16(Uint16 value){Uint8 b[2];memcpy(b,&value,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}

static void game_probe_scene_draw(int,unsigned,int,int,int,int,bool);
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value;
#define cash25_surface_ready(...) (assert(0),false)
#define cash25_family_ready() (assert(0),false)
#define cash75_family_ready() (assert(0),false)
#define cash50_family_ready() (assert(0),false)
#define gem100_family_ready() (assert(0),false)
#define gem250_family_ready() (assert(0),false)
#define enemy_tank_shell_family_ready() (assert(0),false)
#define pregame_font_sprite2_begin(...) ((void)0)
#define pregame_font_sprite2_end(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)

#define render_mirror_entity_end production_end
#include "functions.inc"
#undef render_mirror_entity_end
static void render_mirror_entity_end(void){end_calls++;production_end();}
static void asset_debug_effect(SDL_Surface*s,Sprite2_array b,unsigned id,int x,int y){assert(s&&b.data&&id);(void)x;(void)y;original_calls++;}
static void observed_pixel(SDL_Surface*,Uint8*,Uint8,int);
#define render_mirror_pixel observed_pixel
#include "blitters.inc"
#undef render_mirror_pixel
#define blit_sprite2_blend(...) assert(0)
#define blit_sprite2x2(...) assert(0)
#define blit_sprite2x2_blend(...) assert(0)
#define blit_sprite2x2_darken(...) assert(0)
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored){assert(part==0&&style==ENTITY_NORMAL);scene_calls++;log_role=role;log_id=id;log_x=x;log_y=y;log_mirrored=mirrored;}
static void game_probe_draw(int role,unsigned id,int x,int y,int style,int layout,bool mirrored){assert(role==8&&layout==ENTITY_TILE);(void)style;player_calls++;log_role=role;log_id=id;log_x=x;log_y=y;log_mirrored=mirrored;}
#include "wrappers.inc"
#include "variants.inc"
#ifndef BASELINE
#define BASELINE 0
#endif
/* Bounded adaptation of the existing missile and enemy-energy unit tests. */
enum {W=320,H=200,SCREEN=W*H,PAD=16384,REF=336+43008,NID=13,NREF=31};
static const unsigned ids[NREF]={67,70,121,122,163,164,201,202,279,280,225,244,226,67,70,121,122,163,164,201,202,279,280,225,244,226,58,59,163,164,58};
static Uint8 coverage[NID][43008];
static Uint8 references[NREF][REF],index_ref[328*H],selection_ref[SCREEN],*index_storage,*owner_ref,*cloud_ref;
static Uint16 *first_ref;static Uint32 *color_ref;
static unsigned area[1024],area_count;static bool seen[SCREEN];
static unsigned cases,accepted_cases,fallback_cases,guard_cases,full_comparisons,overlap_cases,lifecycle_cases,restore_cases,present_cases;
static unsigned observed_count,write_count,write_offsets[168];static Uint8 write_values[168];static bool observing;
static uint64_t comparisons,alpha_cases;static char pack_path[2048];
static void *read_file(const char *name,size_t *len)
{FILE*f=fopen(name,"rb");assert(f&&!fseek(f,0,SEEK_END));long n=ftell(f);assert(n>0&&!fseek(f,0,SEEK_SET));Uint8*p=malloc((size_t)n);assert(p&&fread(p,1,(size_t)n,f)==(size_t)n&&!fclose(f));*len=(size_t)n;return p;}
static void clear_assets(void)
{for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(*assets));}for(unsigned i=0;i<13;i++){free(talon_frames[i].rgba);memset(talon_frames+i,0,sizeof(*talon_frames));}enemy_energy_checked=enemy_energy_valid=false;}
static void select_pack(const char *name)
{snprintf(pack_path,sizeof(pack_path),"%s/%s",work,name);game_probe_assets=pack_path;}
static Uint32 initial_color(unsigned n){return 0xff000000u|((n*2654435761u+0x594123u)&0xffffffu);}
static Uint32 *pixel(unsigned n){return (Uint32*)((Uint8*)canvas->pixels+(n/(unsigned)canvas->w)*canvas->pitch)+n%(unsigned)canvas->w;}
static void init_cell(int a)
{
 int d=game_probe_density,x=a%W,y=a/W,pa=y*screen.pitch+x;
 index_ref[pa]=expected[a]=((Uint8*)screen.pixels)[pa]=(Uint8)(a*29+23);selection_ref[a]=selected[a]=0;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
  int n=(y*d+sy)*canvas->w+x*d+sx;color_ref[n]=*pixel(n)=initial_color((unsigned)n);
  owner_ref[n]=hd_owner[n]=(Uint8)(n%3);cloud_ref[n]=cloud_owner[n]=(Uint8)(n&1);
  first_ref[n]=green_first[n]=(Uint16)(n%4);green_under[n]=initial_color((unsigned)n+19);green_under_owner[n]=(Uint8)(n%3);
 }
}
static void allocate(int d,int indexed_pitch,int rgba_padding)
{
 game_probe_density=d;screen.pitch=indexed_pitch;canvas->w=W*d;canvas->h=H*d;canvas->pitch=canvas->w*4+rgba_padding;
 output_surface=*canvas;fade_surface=*canvas;output->pixels=malloc((size_t)canvas->pitch*canvas->h);fade_saved->pixels=malloc((size_t)canvas->pitch*canvas->h);texture_pitch=canvas->pitch;texture_pixels=malloc((size_t)canvas->pitch*canvas->h);
 size_t n=(size_t)canvas->w*canvas->h;canvas->pixels=malloc((size_t)canvas->pitch*canvas->h);memset(canvas->pixels,0xa9,(size_t)canvas->pitch*canvas->h);
 color_ref=malloc(n*4);hd_owner=malloc(n);owner_ref=malloc(n);cloud_owner=malloc(n);cloud_ref=malloc(n);green_first=malloc(n*2);first_ref=malloc(n*2);green_under=malloc(n*4);green_under_owner=malloc(n);
 assert(canvas->pixels&&color_ref&&hd_owner&&owner_ref&&cloud_owner&&cloud_ref&&green_first&&first_ref&&green_under&&green_under_owner);
 memset(index_storage,0xa9,328*H+2*PAD);memset(index_ref,0xa9,sizeof(index_ref));for(int a=0;a<SCREEN;a++)init_cell(a);
}
static void release(void)
{free(output->pixels);free(fade_saved->pixels);free(texture_pixels);free(canvas->pixels);free(color_ref);free(hd_owner);free(owner_ref);free(cloud_owner);free(cloud_ref);free(green_first);free(first_ref);free(green_under);free(green_under_owner);}
static void begin_area(int x,int y,bool reset)
{
 if(reset){memset(seen,0,sizeof(seen));area_count=region_count=green_head_count=0;}
 for(int py=-1;py<15;py++)for(int px=-1;px<13;px++){
  int pa=(y+py)*screen.pitch+x+px;if(pa<0||pa>=screen.pitch*H||pa%screen.pitch>=W)continue;
  int a=(pa/screen.pitch)*W+pa%screen.pitch;if(!seen[a]){assert(area_count<1024);seen[a]=true;area[area_count++]=(unsigned)a;init_cell(a);}
 }
 production_end();
}
static void check_area(void)
{
 int d=game_probe_density;
 for(unsigned k=0;k<area_count;k++){
  int a=(int)area[k],x=a%W,y=a/W,pa=y*screen.pitch+x;assert(index_ref[pa]==((Uint8*)screen.pixels)[pa]);assert(expected[a]==index_ref[pa]);assert(selected[a]==selection_ref[a]);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
   int n=(y*d+sy)*canvas->w+x*d+sx;assert(color_ref[n]==*pixel(n));assert(owner_ref[n]==hd_owner[n]&&cloud_ref[n]==cloud_owner[n]&&first_ref[n]==green_first[n]);
   assert(green_under[n]==initial_color((unsigned)n+19)&&green_under_owner[n]==n%3);comparisons++;
  }
 }
 for(int i=0;i<PAD;i++)assert(index_storage[i]==0xa9&&index_storage[PAD+328*H+i]==0xa9);
}
static void check_all(void)
{
 assert(!memcmp(index_ref,screen.pixels,(size_t)screen.pitch*H));assert(!memcmp(selected,selection_ref,SCREEN));
 for(int y=0;y<H;y++)for(int x=0;x<W;x++)assert(expected[y*W+x]==index_ref[y*screen.pitch+x]);
 size_t n=(size_t)canvas->w*canvas->h;for(size_t p=0;p<n;p++)assert(color_ref[p]==*pixel((unsigned)p));
 assert(!memcmp(owner_ref,hd_owner,n)&&!memcmp(cloud_ref,cloud_owner,n)&&!memcmp(first_ref,green_first,n*2));
 for(int y=0;y<canvas->h;y++)for(int b=canvas->w*4;b<canvas->pitch;b++)assert(((Uint8*)canvas->pixels)[y*canvas->pitch+b]==0xa9);
 full_comparisons++;
}
static Uint32 blend_oracle(Uint32 dst,const Uint8 *src)
{Uint32 out=0xff000000u;for(int c=0;c<3;c++){unsigned shift=16-c*8,n=((dst>>shift)&255)*(255-src[3])+src[c]*src[3];out|=(n/255+(n%255>=128))<<shift;}return out;}
static Uint32 dark_oracle(Uint32 dst,unsigned alpha)
{Uint32 out=0xff000000u;for(unsigned shift=0;shift<24;shift+=8){unsigned n=((dst>>shift)&255)*(510-alpha);out|=(n/510+(n%510>=255))<<shift;}return out;}
static Uint32 cloud_shadow_oracle(Uint32 dst,Uint8 before,Uint8 after)
{if(before==after)return dst;Uint32 out=0xff000000u;for(unsigned shift=0;shift<24;shift+=8){unsigned den=(rgb_palette[before]>>shift)&255,num=((dst>>shift)&255)*((rgb_palette[after]>>shift)&255),v=den?num/den+(num%den>=(den+1)/2):((dst>>shift)&255);out|=MIN(v,255u)<<shift;}return out;}
static void oracle_asset(const Uint8 *rgba,int x,int y,bool shadow,int ad)
{
 int d=game_probe_density;
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){
  int dx=x*d+ax,dy=y*d+ay;if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;
  const Uint8*s=rgba+4*(((ay*ad/d)*8/ad)*96+(ax*ad/d)*8/ad);if(!s[3])continue;int n=dy*canvas->w+dx;
  if(shadow&&owner_ref[n]!=1){Uint8 ci=index_ref[(dy/d)*screen.pitch+dx/d];Uint32 dark=rgb_palette[(ci&0xf0)|((ci&15)/2)];Uint8 q[4]={(dark>>16)&255,(dark>>8)&255,dark&255,s[3]};color_ref[n]=blend_oracle(color_ref[n],q);}
  else color_ref[n]=shadow?dark_oracle(color_ref[n],s[3]):blend_oracle(color_ref[n],s);
  owner_ref[n]=game_probe_original_reference?2:1;cloud_ref[n]=0;first_ref[n]=0;selection_ref[(dy/d)*W+dx/d]=1;
 }
}
static void oracle_original(unsigned k,int x,int y,bool accepted,bool shadow)
{
 int d=game_probe_density;
 for(int py=0;py<14;py++)for(int px=0;px<12;px++){
  int cell=py*12+px;if(!references[k][168+cell])continue;int pa=(y+py)*screen.pitch+x+px;if(pa<0||pa>=screen.pitch*H)continue;
  Uint8 before=index_ref[pa],v=shadow?(Uint8)((before&0xf0)|((before&15)/2)):references[k][cell];index_ref[pa]=v;
  if(!active||pa%screen.pitch>=W)continue;int a=(pa/screen.pitch)*W+pa%screen.pitch;assert(seen[a]);
  if(reject_reason)continue;selection_ref[a]=(Uint8)accepted;
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
   int n=((a/W)*d+sy)*canvas->w+(a%W)*d+sx;
   if(accepted){owner_ref[n]=game_probe_original_reference?2:1;cloud_ref[n]=0;}
   else{bool cloud=shadow&&cloud_ref[n]&&owner_ref[n]==1;first_ref[n]=0;if(!cloud)cloud_ref[n]=0;color_ref[n]=cloud?cloud_shadow_oracle(color_ref[n],before,v):shadow&&owner_ref[n]==1?dark_oracle(color_ref[n],255):0xff000000u|rgb_palette[v];if(!shadow)owner_ref[n]=0;}
  }
 }
}
static void oracle_smooth(unsigned k,int x,int y)
{
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int dx=x*8+ax,dy=y*8+ay;if(dy<0||dy>=canvas->h)continue;
  unsigned alpha=coverage[k][4*(ay*96+ax)+3];if(!alpha)continue;
  int n=dy*canvas->w+dx,a=(dy/8)*W+dx/8;
  Uint8 before=index_ref[(dy/8)*screen.pitch+dx/8],after=(before&0xf0)|((before&15)/2);
  Uint32 target=owner_ref[n]==1?(cloud_ref[n]?cloud_shadow_oracle(color_ref[n],before,after):dark_oracle(color_ref[n],255)):0xff000000u|rgb_palette[after];
  Uint8 q[4]={(target>>16)&255,(target>>8)&255,target&255,(Uint8)alpha};
  Uint32 next=blend_oracle(color_ref[n],q);if(next!=color_ref[n]){owner_ref[n]=1;selection_ref[a]=1;}
  color_ref[n]=next;first_ref[n]=0;
 }
}
static void oracle_smooth_original(unsigned k,int x,int y)
{
 for(int py=0;py<14;py++)for(int px=0;px<12;px++) {
  if(!references[k][168+py*12+px])continue;
  int pa=(y+py)*screen.pitch+x+px;if(pa<0||pa>=screen.pitch*H)continue;
  Uint8 before=index_ref[pa],after=(before&0xf0)|((before&15)/2);index_ref[pa]=after;
  int a=(pa/screen.pitch)*W+pa%screen.pitch;
  if(before!=after)selection_ref[a]=1;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++) {
   int n=((a/W)*8+sy)*canvas->w+(a%W)*8+sx;
   if(before!=after)owner_ref[n]=1;first_ref[n]=0;
  }
 }
}
static void observed_pixel(SDL_Surface *s,Uint8 *p,Uint8 source,int style)
{
 if(observing){assert(s==&screen&&observed_count<write_count);assert(p==(Uint8*)screen.pixels+write_offsets[observed_count]);assert(*p==write_values[observed_count]);observed_count++;}
 render_mirror_pixel(s,p,source,style);
}
static void prepare_writes(unsigned k,int x,int y,bool shadow)
{
 observed_count=write_count=0;
 for(int cy=0;cy<14;cy++)for(int cx=0;cx<12;cx++){
  int cell=cy*12+cx;if(!references[k][168+cell])continue;
  int pa=(y+cy)*screen.pitch+x+cx;if(pa<0||pa>=screen.pitch*H)continue;
  write_offsets[write_count]=(unsigned)pa;Uint8 before=index_ref[pa];
  write_values[write_count++]=shadow?(before&0xf0)|((before&15)/2):references[k][cell];
 }
 observing=true;
}
static void execute(unsigned k,int x,int y,bool accepted,bool shadow,int mode)
{
 unsigned before=original_calls,ends=end_calls,logs=player_calls,scenes=scene_calls,old_draws=draws;
 Uint8 *allocation=spriteSheet8.data;size_t allocation_size=spriteSheet8.size;
 prepare_writes(k,x,y,shadow);
 if(mode==1){if(shadow)blit_sprite2_darken(&screen,x,y,spriteSheet8,ids[k]);else blit_sprite2(&screen,x,y,spriteSheet8,ids[k]);}
 else if(mode==2)draw_enemy_shot_sprite2(&screen,x,y,spriteSheet8,ids[k]);
 else draw_entity_sprite2(&screen,x,y,spriteSheet8,ids[k],shadow?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);
 observing=false;assert(observed_count==write_count);
 assert(original_calls==before+1&&end_calls==ends+(unsigned)(mode!=1)&&draws==old_draws+(unsigned)accepted);
 assert(!suppress&&!suppress_cloud&&!suppress_green_smoke&&!vulcan_shadow.live);
 assert(spriteSheet8.data==allocation&&spriteSheet8.size==allocation_size);
 if(mode==0)assert(player_calls==logs+1&&log_id==ids[k]&&log_x==x&&log_y==y&&log_mirrored==accepted&&log_role==8);
 if(mode==2){bool energy=enemy_energy_slot(ids[k])>=0;assert(scene_calls==scenes+(unsigned)energy&&player_calls==logs);if(energy)assert(log_role==111&&log_id==ids[k]&&log_mirrored==accepted);}
 if(accepted&&shadow&&k<NID){oracle_smooth(k,x,y);oracle_smooth_original(k,x,y);}
 else {
  if(accepted){Asset*a=mode==2?&assets[enemy_energy_slot(ids[k])]:get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert(a&&a->valid);oracle_asset(references[k]+336,x,y,shadow,a->density);}
  oracle_original(k,x,y,accepted,shadow);
 }
 check_area();cases++;accepted_cases+=accepted;fallback_cases+=!accepted;
}
static void transaction(unsigned k,int x,int y,bool accepted,bool shadow,int mode,bool reset)
{begin_area(x,y,reset);execute(k,x,y,accepted,shadow,mode);}
static void fill_area(Uint8 index,int owner,int cloud)
{
 for(unsigned i=0;i<area_count;i++){
  int a=area[i],x=a%W,y=a/W;index_ref[y*screen.pitch+x]=expected[a]=((Uint8*)screen.pixels)[y*screen.pitch+x]=index;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
   int n=(y*8+sy)*canvas->w+x*8+sx;owner_ref[n]=hd_owner[n]=(Uint8)owner;cloud_ref[n]=cloud_owner[n]=(Uint8)cloud;
   color_ref[n]=*pixel(n)=owner==1?initial_color(n):0xff000000u|rgb_palette[index];
  }
 }
}
static void check_math(void)
{
 for(unsigned k=0;k<NID;k++){
  unsigned extension=0,transparent_support=0;
  for(int y=0;y<112;y++)for(int x=0;x<96;x++){
   bool support=references[k][168+(y/8)*12+x/8]!=0;Uint8 alpha=coverage[k][4*(y*96+x)+3];
   extension+=!support&&alpha;transparent_support+=support&&!alpha;
  }
  const unsigned extras[10]={78,110,204,205,311,312,252,253,431,433};
  if(k<10)assert(extension==extras[k]&&transparent_support>0);
  else {unsigned zero=0,partial=0,opaque=0,different=0;
   for(unsigned n=0;n<96*112;n++){unsigned a=coverage[k][4*n+3];zero+=a==0;partial+=a>0&&a<255;opaque+=a==255;different+=a!=references[k][336+4*n+3];}
   const unsigned zeros[3]={9896,4514,9442},partials[3]={124,332,154},opaques[3]={732,5906,1156},added[3]={104,208,58},removed[3]={16,178,92};
   assert(zero==zeros[k-10]&&partial==partials[k-10]&&opaque==opaques[k-10]&&different);
   assert(extension==added[k-10]&&transparent_support==removed[k-10]);
  }
 }
 const Uint8 alphas[]={0,1,254,255};
 for(unsigned a=0;a<4;a++)for(unsigned src=0;src<256;src++)for(unsigned dst=0;dst<256;dst++) {
  Uint8 rgba[4]={(Uint8)src,(Uint8)(255-src),(Uint8)(src^0x69),alphas[a]};Uint32 color=0xff000000u|dst<<16|(255-dst)<<8|(dst^0x96);
  assert(blend_rgba(color,rgba,rgba[3])==blend_oracle(color,rgba));alpha_cases++;
  Uint32 half=darken_rgba(color,255);assert(half==dark_oracle(color,255));
  Uint8 q[4]={(half>>16)&255,(half>>8)&255,half&255,alphas[a]};
  assert(blend_rgba(color,q,q[3])==blend_oracle(color,q));alpha_cases++;
 }
 for(unsigned index=0;index<256;index++)for(unsigned k=0;k<NID;k++)for(int owner=0;owner<=1;owner++)for(int cloud=0;cloud<=1;cloud++) {
  begin_area(94,73,true);fill_area((Uint8)index,owner,cloud);execute(k,94,73,true,true,0);
  execute(k,94,73,true,true,0); /* Real same-ID repeated writes include every ramp floor. */
 }
 check_all();
}
static unsigned support_overlap(unsigned a,int ax,int ay,unsigned b,int bx,int by)
{
 unsigned total=0;for(int y=0;y<14;y++)for(int x=0;x<12;x++) {
  if(!references[a][168+y*12+x])continue;int rx=ax+x-bx,ry=ay+y-by;
  if(rx>=0&&rx<12&&ry>=0&&ry<14&&references[b][168+ry*12+rx])total++;
 }return total;
}
static void test_order(void)
{
 for(unsigned k=0;k<NID;k++){
  if(k<2)assert(support_overlap(k,94,83,k,94,73)==k+1);
  int hy=k<10?73:81;begin_area(94,83,true);begin_area(94,hy,false);
  execute(k,94,83,true,true,0);execute(k,94,hy,true,false,0);overlap_cases++;
 }
 for(unsigned a=0;a<NID;a++)for(unsigned b=0;b<NID;b++)for(int reverse=0;reverse<2;reverse++){
  int bx=0,by=0,best=1000,gap=a<10&&b<10?10:1,hy=83-gap;
  for(int oy=-13;oy<=13;oy++)for(int ox=-11;ox<=11;ox++) {
   int distance=abs(ox-1)+abs(oy+2);
   if(distance<best&&support_overlap(a,94,83,b,94+ox,83+oy)>0&&support_overlap(a,94,hy,b,94+ox,83+oy)>0){bx=94+ox;by=83+oy;best=distance;}
  }
  assert(best<1000);
  begin_area(94,83,true);begin_area(94,hy,false);begin_area(bx,by,false);begin_area(bx,by-gap,false);
  if(!reverse){execute(a,94,83,true,true,0);execute(a,94,hy,true,false,0);execute(b,bx,by,true,true,0);execute(b,bx,by-gap,true,false,0);}
  else {execute(b,bx,by,true,true,0);execute(b,bx,by-gap,true,false,0);execute(a,94,83,true,true,0);execute(a,94,hy,true,false,0);}
  overlap_cases++;
  execute(a,94,hy,false,false,1);execute(b,bx,by,true,true,0);
 }
 check_all();
}
static void test_fallbacks(void)
{
 for(unsigned v=0;v<sizeof(variants)/sizeof(*variants);v++){
  clear_assets();select_pack(variants[v]);
  for(unsigned k=0;k<NID;k++){
   transaction(k,94,73,variant_valid[v][k],true,0,true);
   Asset *head=get_asset(spriteSheet8,ids[k],ENTITY_TILE);int density=variant_head_density[v][k];
   assert(density?(head&&head->valid&&head->density==density):!head);
   /* Missing/broken coverage must not alter normal heads. Valid 4x heads
    * still draw through their independent fallback while shadow stays indexed. */
   if(!strncmp(variants[v],"protron-shadow-",15)||density!=8)
    transaction(k,94,73,density!=0,false,0,true);
  }
  /* A warm result cannot be relabelled as coming from a new resource root. */
  game_probe_assets=full_pack;
  for(unsigned k=0;k<NID;k++)transaction(k,94,73,false,true,0,true);
 }
 clear_assets();game_probe_assets=full_pack;
 for(unsigned k=0;k<NID;k++) {
  transaction(k,94,73,true,true,0,true);Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert(a);
  Uint8 saved=a->rgba[3];a->rgba[3]^=1;transaction(k,94,73,false,true,0,true);a->rgba[3]=saved;
  transaction(k,94,73,true,true,0,true);
 }
}
static void test_guards(void)
{
 SDL_Surface other=screen;Uint8 token;Sprite2_array banks[]={spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet,{&token,1},{NULL,0}};
 const unsigned indices[]={0,31,58,59,66,67,68,69,70,71,121,122,163,164,201,202,279,280,214,217,225,226,244,252,254,UINT_MAX};
 for(unsigned b=0;b<6;b++)for(unsigned j=0;j<sizeof(indices)/sizeof(*indices);j++)for(int layout=0;layout<2;layout++){
  unsigned index=indices[j];bool finite=b==0&&layout==ENTITY_TILE&&vulcan_shadow_member(index)>=0;
  if(finite)continue; /* Generic existing routes are outside this finite gate. */
  if(b==0&&vulcan_shadow_member(index)>=0){assert(!render_mirror_entity(&screen,94,73,banks[b],index,MIRROR_SHADOW,layout));guard_cases++;continue;}
  assert(!draw_vulcan_shadow(&screen,94,73,banks[b],index));guard_cases++;
 }
 for(unsigned k=0;k<NID;k++)for(int gate=0;gate<11;gate++){
  begin_area(94,73,true);unsigned before=draws;
  active=gate!=0;reject_reason=gate==1?"fixture":NULL;xmas=gate==2;game_probe_density=gate==3?4:8;game_probe_missing=gate==4;game_probe_invalid=gate==5;game_probe_original_reference=gate==6;
  int width=screen.w;screen.w=gate==8?319:320;SDL_Surface*old=VGAScreen;if(gate==9)VGAScreen=&other;
  int bytes=format.BytesPerPixel;if(gate==10)format.BytesPerPixel=4;
  assert(!render_mirror_entity(gate==7?&other:&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));
  assert(draws==before&&!vulcan_shadow.live&&!suppress);guard_cases++;
  active=true;reject_reason=NULL;xmas=game_probe_missing=game_probe_invalid=game_probe_original_reference=false;game_probe_density=8;screen.w=width;VGAScreen=old;format.BytesPerPixel=bytes;
 }
}
static void test_source_epochs(Sprite2_array normal,Sprite2_array christmas)
{
 for(unsigned k=0;k<NID;k++){
  spriteSheet8=normal;transaction(k,94,73,true,true,0,true);
  Asset head_before=assets[vulcan_shadow_pins[k].slot],mask_before={0};if(k>=10)mask_before=assets[vulcan_shadow_pins[k].coverage_slot];
  xmas=true;transaction(k,94,73,false,true,0,true);spriteSheet8=christmas;
  transaction(k+NID,94,73,false,true,0,true);
  assert(!memcmp(&head_before,&assets[vulcan_shadow_pins[k].slot],sizeof(Asset)));
  if(k>=10)assert(!memcmp(&mask_before,&assets[vulcan_shadow_pins[k].coverage_slot],sizeof(Asset)));xmas=false;
  bool same_source=!memcmp(references[k],references[k+NID],336);
  if(k>=10)assert(same_source==(ids[k]!=244));
  assert(render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE)==same_source);production_end();guard_cases++;
  spriteSheet8=normal;transaction(k,94,73,true,true,0,true);
  /* Change the semantic source at exactly the same allocation address. */
  size_t offset=normal.data[2*(ids[k]-1)]|((size_t)normal.data[2*(ids[k]-1)+1]<<8);
  while(!(normal.data[offset]>>4))offset++;
  Uint8 saved=normal.data[offset+1];normal.data[offset+1]^=1;
  assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));normal.data[offset+1]=saved;
  assert(!vulcan_shadow.live);guard_cases++;
  transaction(k,94,73,true,true,0,true);
  Sprite2_array changed=normal;changed.data=malloc(changed.size);assert(changed.data);memcpy(changed.data,normal.data,changed.size);spriteSheet8=changed;
  transaction(k,94,73,true,true,0,true);free(changed.data);spriteSheet8=normal;lifecycle_cases++;
 }
}
static void prime(unsigned k)
{begin_area(94,73,true);unsigned old_draws=draws;assert(render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));assert(vulcan_shadow.live&&!vulcan_shadow.entered&&draws==old_draws&&region_count==0);check_area();}
static unsigned mask_guard_cases,cold_xmas_cases,mask_swap_cases;
static void test_mask_identity(void)
{
 for(unsigned k=10;k<NID;k++){
  for(int entry=0;entry<2;entry++)for(int change=0;change<16;change++){
   if(!entry&&(change==13||change==14))continue;
   prime(k);Asset *a=&assets[vulcan_shadow_pins[k].coverage_slot],metadata=*a;
   const Uint8 *receipt=vulcan_shadow_coverage_resource[k-10].rgba;const char *root=game_probe_assets;
   char path[1024];memcpy(path,vulcan_shadow_coverage_resource[k-10].path,sizeof(path));Uint8 byte=a->rgba[3];
   if(change==0)a->rgba[3]^=1;if(change==1)a->bank=8;if(change==2)a->index++;
   if(change==3)a->w--;if(change==4)a->h--;if(change==5)a->anchor_x++;if(change==6)a->anchor_y++;
   if(change==7)a->density=4;if(change==8)a->valid=false;if(change==9)a->rgba+=4;
   if(change==10)vulcan_shadow_coverage_resource[k-10].rgba+=4;
   if(change==11)vulcan_shadow_coverage_resource[k-10].path[0]^=1;
   if(change==12)a->rgba=assets[vulcan_shadow_pins[k].slot].rgba;
   if(change==13)a->initialized=false;
   if(change==14)vulcan_shadow.shadow_rgba=assets[vulcan_shadow_pins[k].slot].rgba;
   if(change==15)select_pack("missing-all");
   if(entry)render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);
   else {production_end();assert(!draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));}
   assert(!vulcan_shadow.live&&!reject_reason);
   *a=metadata;a->rgba[3]=byte;vulcan_shadow_coverage_resource[k-10].rgba=receipt;
   memcpy(vulcan_shadow_coverage_resource[k-10].path,path,sizeof(path));game_probe_assets=root;
   check_area();mask_guard_cases++;
  }
  for(unsigned other=10;other<NID;other++)if(other!=k){
   transaction(other,94,73,true,true,0,true);prime(k);
   Asset *a=&assets[vulcan_shadow_pins[k].coverage_slot],saved=*a;
   a->rgba=assets[vulcan_shadow_pins[other].coverage_slot].rgba;
   render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);assert(!vulcan_shadow.live&&!reject_reason);*a=saved;check_area();mask_swap_cases++;
  }
 }
}
static void test_cold_xmas(Sprite2_array normal,Sprite2_array christmas)
{
 for(int alternate=0;alternate<2;alternate++)for(unsigned k=10;k<NID;k++){
  clear_assets();game_probe_assets=full_pack;spriteSheet8=alternate?christmas:normal;xmas=true;
  begin_area(94,73,true);assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));
  for(unsigned n=0;n<sizeof(assets)/sizeof(*assets);n++)assert(!assets[n].initialized);
  assert(!vulcan_shadow.live&&!reject_reason);check_area();xmas=false;spriteSheet8=normal;cold_xmas_cases++;
 }
 for(unsigned k=0;k<NID;k++)transaction(k,94,73,true,true,0,true);
}
static void test_lifecycle(void)
{
 for(unsigned k=0;k<NID;k++){
  prime(k);production_end();assert(!vulcan_shadow.live);lifecycle_cases++;
  prime(k);region_count=256;render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);assert(!vulcan_shadow.live&&!reject_reason);region_count=0;check_area();lifecycle_cases++;
  begin_area(94,73,true);region_count=256;assert(!draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));region_count=0;check_area();lifecycle_cases++;
  prime(k);active=false;assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));active=true;assert(!vulcan_shadow.live);lifecycle_cases++;
  prime(k);render_mirror_unsupported("fixture-reject");assert(!vulcan_shadow.live);reject_reason=NULL;lifecycle_cases++;
  prime(k);assert(!render_mirror_enemy_shot(&screen,94,73,spriteSheet8,67));assert(!vulcan_shadow.live);lifecycle_cases++;
  /* Check epochs at actual entry and again while consuming a live command. */
  for(int entered=0;entered<2;entered++)for(int mismatch=0;mismatch<13;mismatch++){
   prime(k);if(entered)render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);
   int cell=0;while(!references[k][168+cell])cell++;
   int x=94+cell%12,y=73+cell/12;Uint8 before=expected[y*W+x],after=(before&0xf0)|((before&15)/2);
   SDL_Surface other=screen;Sprite2_array bank=spriteSheet8;void*p=screen.pixels,*cp=canvas->pixels;SDL_PixelFormat*f=screen.format;
   int pitch=screen.pitch,cpp=canvas->pitch,cw=canvas->w,bits=format.BitsPerPixel;uint64_t tick=mirror_logic_tick;
   if(mismatch==0)mirror_logic_tick++;if(mismatch==1)screen.pixels=(Uint8*)screen.pixels+1;if(mismatch==2)screen.pitch++;
   if(mismatch==3)spriteSheet8.size--;if(mismatch==4)spriteSheet8.data++;if(mismatch==5)screen.format=NULL;if(mismatch==6)xmas=true;
   if(mismatch==9)canvas->pixels=(Uint8*)canvas->pixels+4;if(mismatch==10)canvas->pitch+=4;if(mismatch==11)canvas->w--;if(mismatch==12)format.BitsPerPixel=16;
   if(entered)assert(vulcan_shadow_pixel(mismatch==7?&other:&screen,x,y,before,after,mismatch==8?MIRROR_NORMAL:MIRROR_SHADOW)&&reject_reason);
   else {render_mirror_shadow_begin(mismatch==7?&other:&screen,94,73,spriteSheet8,mismatch==8?ids[(k+1)%NID]:ids[k]);assert(!reject_reason);}
   assert(!vulcan_shadow.live);spriteSheet8=bank;screen.pixels=p;screen.format=f;screen.pitch=pitch;mirror_logic_tick=tick;xmas=false;
   canvas->pixels=cp;canvas->pitch=cpp;canvas->w=cw;format.BitsPerPixel=bits;reject_reason=NULL;if(!entered)check_area();lifecycle_cases++;
  }
  /* The lease suppresses each classic support cell once, never twice. */
  prime(k);render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);assert(vulcan_shadow.entered);int cell=0;while(!references[k][168+cell])cell++;int x=94+cell%12,y=73+cell/12,a=y*W+x;
  Uint8 *address=(Uint8*)screen.pixels+y*screen.pitch+x,before=*address;Uint32 colors[64];
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)colors[sy*8+sx]=*pixel((y*8+sy)*canvas->w+x*8+sx);
  *address=(before&0xf0)|((before&15)/2);render_mirror_pixel(&screen,address,0,MIRROR_SHADOW);
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)assert(colors[sy*8+sx]==*pixel((y*8+sy)*canvas->w+x*8+sx));
  before=*address;*address=(before&0xf0)|((before&15)/2);render_mirror_pixel(&screen,address,0,MIRROR_SHADOW);assert(!vulcan_shadow.live&&expected[a]==*address&&reject_reason);reject_reason=NULL;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)assert(colors[sy*8+sx]==*pixel((y*8+sy)*canvas->w+x*8+sx));
  lifecycle_cases++;
 }
 /* Tests above intentionally simulate aborted calls; restore a clean oracle. */
 for(int a=0;a<SCREEN;a++)init_cell(a);region_count=0;production_end();
}

static void direct_shadow(Sprite2_array bank,unsigned k,int x,int y)
{
 unsigned before=original_calls,old_draws=draws;prepare_writes(k,x,y,true);
 blit_sprite2_darken(&screen,x,y,bank,ids[k]);observing=false;
 assert(observed_count==write_count&&original_calls==before+1&&draws==old_draws&&!vulcan_shadow.live&&!reject_reason);
 oracle_original(k,x,y,false,true);check_area();cases++;fallback_cases++;
}
static void test_command_identity(void)
{
 for(unsigned k=0;k<NID;k++){
  prime(k);direct_shadow(spriteSheet8,(k+1)%NID,94,73);lifecycle_cases++;
  begin_area(94,73,true);begin_area(95,74,false);unsigned old=draws;
  assert(render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));check_area();assert(draws==old);
  direct_shadow(spriteSheet8,k,95,74);lifecycle_cases++;
  Sprite2_array other=spriteSheet8;other.data=malloc(other.size);assert(other.data);memcpy(other.data,spriteSheet8.data,other.size);
  prime(k);direct_shadow(other,k,94,73);free(other.data);lifecycle_cases++;
  prime(k);execute((k+1)%NID,94,73,false,false,1);lifecycle_cases++;
  prime(k);font_force_reject=true;render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);font_force_reject=false;assert(!vulcan_shadow.live&&reject_reason&&!region_count);reject_reason=NULL;check_area();lifecycle_cases++;
  /* Reject every unfinished entered command at an ordinary command boundary. */
  for(int boundary=0;boundary<4;boundary++){
   prime(k);render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);assert(vulcan_shadow.entered);
   if(boundary==0)production_end();
   if(boundary==1)assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_NORMAL,ENTITY_TILE));
   if(boundary==2)render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[(k+1)%NID]);
   if(boundary==3)render_mirror_finish(true);
   assert(!vulcan_shadow.live&&reject_reason);reject_reason=NULL;active=true;lifecycle_cases++;
  }
  prime(k);render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);int cell=0;while(!references[k][168+cell])cell++;
  int x=94+cell%12,y=73+cell/12;Uint8*p=(Uint8*)screen.pixels+y*screen.pitch+x;*p=(*p&0xf0)|((*p&15)/2);render_mirror_pixel(&screen,p,0,MIRROR_SHADOW);
  render_mirror_shadow_end();assert(!vulcan_shadow.live&&reject_reason&&!strcmp(reject_reason,"incomplete-vulcan-shadow-command"));reject_reason=NULL;lifecycle_cases++;
  /* Source, pack-root, payload, expected-ledger changes cancel before RGBA writes. */
  for(int change=0;change<13;change++){
   prime(k);Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);Asset metadata=*a;Uint8 byte=a->rgba[3];const char*root=game_probe_assets;
   size_t off=spriteSheet8.data[2*(ids[k]-1)]|((size_t)spriteSheet8.data[2*(ids[k]-1)+1]<<8);while(!(spriteSheet8.data[off]>>4))off++;Uint8 source=spriteSheet8.data[off+1];
   if(change==0)a->rgba[3]^=1;if(change==1)select_pack("missing-all");if(change==2)spriteSheet8.data[off+1]^=1;if(change==3)expected[73*W+94]^=1;
   if(change==4)a->bank=111;if(change==5)a->index++;if(change==6)a->w--;if(change==7)a->h--;if(change==8)a->anchor_x++;if(change==9)a->anchor_y++;if(change==10)a->density=4;if(change==11)a->valid=false;if(change==12)a->rgba+=4;
   render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);assert(!vulcan_shadow.live&&!reject_reason);
   *a=metadata;a->rgba[3]=byte;game_probe_assets=root;spriteSheet8.data[off+1]=source;if(change==3)expected[73*W+94]^=1;check_area();lifecycle_cases++;
  }
 }
 for(int a=0;a<SCREEN;a++)init_cell(a);region_count=0;production_end();
}
static void test_restore(void)
{
 for(unsigned k=0;k<NID;k++){
  transaction(k,94,73,true,true,0,true);restore_classic_rect((SDL_Rect){95,74,1,1});
  for(int y=73;y<87;y++)for(int x=94;x<106;x++){
   int a=y*W+x;selection_ref[a]=0;
   for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
    int n=(y*8+sy)*canvas->w+x*8+sx;color_ref[n]=0xff000000u|rgb_palette[index_ref[y*screen.pitch+x]];owner_ref[n]=cloud_ref[n]=0;first_ref[n]=0;
   }
  }
  check_area();check_all();restore_cases++;
 }
}

static Uint32 surface_pixel(SDL_Surface*s,int x,int y)
{return ((Uint32*)((Uint8*)s->pixels+y*s->pitch))[x];}
static void reset_begin_oracle(void)
{
 for(int a=0;a<SCREEN;a++){
  int x=a%W,y=a/W;index_ref[y*screen.pitch+x]=((Uint8*)screen.pixels)[y*screen.pitch+x];selection_ref[a]=0;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
   int n=(y*8+sy)*canvas->w+x*8+sx;color_ref[n]=0xff000000u|rgb_palette[index_ref[y*screen.pitch+x]];owner_ref[n]=cloud_ref[n]=0;first_ref[n]=0;
  }
 }
}
static void test_presentation(unsigned k)
{
 prime(k);uint64_t tick=mirror_logic_tick;render_mirror_begin();assert(!vulcan_shadow.live&&mirror_logic_tick==tick+1&&active&&!ready);reset_begin_oracle();check_all();lifecycle_cases++;
 begin_area(94,83,true);begin_area(94,73,false);execute(k,94,83,true,true,0);execute(k,94,73,true,false,0);
 begin_area(95,81,false);execute((k+1)%NID,95,81,true,true,0);check_all();
 render_mirror_finish(true);assert(!active&&ready&&!vulcan_shadow.live&&!reject_reason&&last_output_valid&&last_output_scene_hd);
 for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++){
  Uint32 q=x<264*8&&y<184*8?color_ref[y*canvas->w+x+24*8]:0xff000000u|rgb_palette[index_ref[(y/8)*screen.pitch+x/8]];
  assert(surface_pixel(output,x,y)==q);
 }
 game_probe_repeat=true;SDL_Renderer renderer={0};SDL_Rect rect={0,0,640,400};unsigned calls=sdl_present_calls;tick=mirror_logic_tick;
 assert(render_mirror_present(&renderer,VGAScreenSeg,&rect));assert(sdl_present_calls==calls+2&&!ready&&mirror_logic_tick==tick);check_all();
 for(int y=0;y<output->h;y++)assert(!memcmp((Uint8*)texture_pixels+y*texture_pitch,(Uint8*)output->pixels+y*output->pitch,(size_t)output->w*4));
 assert(!render_mirror_present(&renderer,VGAScreenSeg,&rect));assert(sdl_present_calls==calls+2&&mirror_logic_tick==tick);present_cases+=2;
 SDL_Color black={0,0,0,255},white={255,255,255,255},target[256];
 for(int i=0;i<256;i++)target[i]=(SDL_Color){(rgb_palette[i]>>16)&255,(rgb_palette[i]>>8)&255,rgb_palette[i]&255,255};
 render_mirror_fade_start(NULL,&black,0,255);assert(fade_mode==1&&!vulcan_shadow.live&&have_fade_saved);
 render_mirror_fade_step(2);assert(ready);
 for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++){
  bool hd=x<264*8&&y<184*8&&hd_owner[y*canvas->w+x+24*8]!=0;
  Uint32 q=0xff000000u;if(hd){Uint32 saved=surface_pixel(fade_saved,x,y);for(int shift=0;shift<24;shift+=8){int old=(saved>>shift)&255;q|=(Uint32)(old-old/2)<<shift;}}
  else q|=rgb_palette[index_ref[(y/8)*screen.pitch+x/8]];
  assert(surface_pixel(output,x,y)==q);
 }
 render_mirror_fade_step(1);assert(!fade_mode);
 for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++){
  bool hd=x<264*8&&y<184*8&&hd_owner[y*canvas->w+x+24*8]!=0;
  assert(surface_pixel(output,x,y)==(hd?0xff000000u:0xff000000u|rgb_palette[index_ref[(y/8)*screen.pitch+x/8]]));
 }
 render_mirror_fade_start(target,NULL,0,255);assert(fade_mode==3);render_mirror_fade_step(1);
 for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++){
  bool hd=x<264*8&&y<184*8&&hd_owner[y*canvas->w+x+24*8]!=0;
  Uint32 q=hd?surface_pixel(fade_saved,x,y):0xff000000u|rgb_palette[index_ref[(y/8)*screen.pitch+x/8]];assert(surface_pixel(output,x,y)==q);
 }
 render_mirror_fade_start(NULL,&white,0,255);assert(fade_mode==2);render_mirror_fade_step(1);
 for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++){
  bool hd=x<264*8&&y<184*8&&hd_owner[y*canvas->w+x+24*8]!=0;
  assert(surface_pixel(output,x,y)==(hd?0xffffffffu:0xff000000u|rgb_palette[index_ref[(y/8)*screen.pitch+x/8]]));
 }
 check_all();present_cases+=4;game_probe_repeat=false;active=true;
}
static unsigned contour_clear_samples,contour_extra_samples,control_cases;
static void test_contour_and_controls(void)
{
 for(unsigned k=0;k<NID;k++) {
  begin_area(94,73,true);fill_area(0x7f,1,0);execute(k,94,73,true,true,0);
  for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
   unsigned alpha=coverage[k][4*(ay*96+ax)+3];bool support=references[k][168+(ay/8)*12+ax/8]!=0;
   unsigned n=(73*8+ay)*canvas->w+94*8+ax;Uint32 initial=initial_color(n);
   if(support&&!alpha){assert(*pixel(n)==initial);contour_clear_samples++;}
   if(!support&&alpha){Uint32 half=dark_oracle(initial,255);Uint8 q[4]={(half>>16)&255,(half>>8)&255,half&255,(Uint8)alpha};assert(*pixel(n)==blend_oracle(initial,q));contour_extra_samples++;}
  }
 }
 for(unsigned k=26;k<28;k++) {
  assert(!draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));
  transaction(k,94,73,true,false,0,true);transaction(k,94,73,true,true,0,true);control_cases++;
 }
 for(unsigned k=28;k<31;k++) {
  unsigned player=k==28?4:k==29?5:26;
  for(int reverse=0;reverse<2;reverse++) {
   begin_area(94,73,true);begin_area(96,75,false);
   if(reverse){execute(player,94,73,true,true,0);execute(k,96,75,screen.pitch==320,false,2);}
   else {execute(k,96,75,screen.pitch==320,false,2);execute(player,94,73,true,true,0);}
   Asset*p=get_asset(spriteSheet8,ids[player],ENTITY_TILE);assert(p&&p->bank==8);
   if(screen.pitch==320){Asset*e=&assets[enemy_energy_slot(ids[k])];assert(e->bank==111&&e->rgba!=p->rgba);}
   control_cases++;
  }
 }
 check_all();
}

int main(int argc,char **argv)
{
 assert(argc==3);full_pack=game_probe_assets=argv[1];work=argv[2];char path[2048];size_t bytes;
 snprintf(path,sizeof(path),"%s/bank.bin",work);spriteSheet8.data=read_file(path,&bytes);spriteSheet8.size=bytes;Sprite2_array normal=spriteSheet8;
 snprintf(path,sizeof(path),"%s/xmas-bank.bin",work);Sprite2_array christmas={0};christmas.data=read_file(path,&bytes);christmas.size=bytes;
 snprintf(path,sizeof(path),"%s/reference.bin",work);void*ref=read_file(path,&bytes);assert(bytes==sizeof(references));memcpy(references,ref,bytes);free(ref);
 snprintf(path,sizeof(path),"%s/coverage.bin",work);ref=read_file(path,&bytes);assert(bytes==sizeof(coverage));memcpy(coverage,ref,bytes);free(ref);
 Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){tokens,1};spriteSheet12=(Sprite2_array){tokens+1,1};explosionSpriteSheet=(Sprite2_array){tokens+2,1};
 index_storage=malloc(328*H+2*PAD);assert(index_storage);screen.pixels=index_storage+PAD;
 for(unsigned i=0;i<256;i++)rgb_palette[i]=((i*71)%256)<<16|((i*31)%256)<<8|((i*13)%256);
 for(int layout=0;layout<2;layout++){
  allocate(8,layout?328:320,layout?28:0);game_probe_assets=full_pack;
#ifdef PROTRON_PRESENTATION_ONLY
  test_contour_and_controls();for(unsigned k=0;k<NID;k++)test_presentation(k);check_all();clear_assets();release();continue;
#endif
  test_guards();
  const int xy[][2]={{94,73},{0,0},{308,0},{0,-13},{308,-1},{94,187},{0,199},{308,199},{-3,73},{315,73},{94,-14},{94,200}};
  for(unsigned k=0;k<NID;k++)for(unsigned p=0;p<sizeof(xy)/sizeof(*xy);p++){
   int x=xy[p][0],y=xy[p][1];bool ok=x>=0&&x<=308&&y>=-13&&y<=199;
   transaction(k,x,y,ok,true,0,true);transaction(k,x,y,true,false,0,true);
  }
  for(unsigned k=0;k<NID;k++){transaction(k,94,73,false,true,1,true);if(ids[k]!=163&&ids[k]!=164)transaction(k,94,73,false,false,2,true);}
  if(!layout)check_math();test_contour_and_controls();test_order();test_fallbacks();test_source_epochs(normal,christmas);test_cold_xmas(normal,christmas);test_mask_identity();test_lifecycle();test_command_identity();test_restore();test_presentation(0);check_all();clear_assets();release();
 }
 assert(contour_clear_samples&&contour_extra_samples&&control_cases);
 free(index_storage);free(normal.data);free(christmas.data);
 printf("{\"status\":\"PASS\",\"mask_identity_cases\":%u,\"cold_xmas_cases\":%u,\"warm_mask_swaps\":%u,\"old_block_clear_samples\":%u,\"coverage_expansion_samples\":%u,\"control_cases\":%u,\"transactions\":%u,\"accepted\":%u,\"fallback\":%u,\"guard_cases\":%u,\"ordering_cases\":%u,\"lifecycle_cases\":%u,\"local_restore_cases\":%u,\"present_cases\":%u,\"pixel_comparisons\":%llu,\"full_frame_checks\":%u,\"exact_alpha_cases\":%llu}\n",mask_guard_cases,cold_xmas_cases,mask_swap_cases,contour_clear_samples,contour_extra_samples,control_cases,cases,accepted_cases,fallback_cases,guard_cases,overlap_cases,lifecycle_cases,restore_cases,present_cases,(unsigned long long)comparisons,full_comparisons,(unsigned long long)alpha_cases);
 return 0;
}
