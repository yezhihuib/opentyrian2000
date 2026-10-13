#ifndef RENDER_MIRROR_DISABLED
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Display-only ordered mirror. The engine always executes original 1x writes.
 * Unsupported effects or incomplete changed-pixel coverage reject the full frame.
 */
#include "settings_font.h"
#include "load_font.h"
#include "selector_font.h"
#include "pregame_font.h"
#include "render_mirror.h"
#include "gameplay_hud.h"
#include "gameplay_hud_components.h"
#include "gameplay_hud_meters.h"
#include "gameplay_hud_indicators.h"
#include "gameplay_hud_fixed_text.h"
#include "gameplay_hud_font.h"
#include "config.h"
#include "episodes.h"
#include "fonthand.h"
#include "player.h"
#include "plateau_cap_material.h"
#include "forest13_material.h"
#include "game_probe.h"
#include "asset_debug.h"
#include "entity_draw.h"
#include "palette.h"
#include "mtrand.h"
#include "network.h"
#include "video.h"
#include "varz.h"
#include "xmas.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
 bool initialized,valid;
 int bank,index,w,h,anchor_x,anchor_y,density;
 Uint8 *rgba;
} Asset;
enum { ASSET_NEWSH2=101, ASSET_NEWSH4=102, ASSET_NEWSHE=110, ASSET_TALON_BANK=109, ASSET_SHAPESZ=201, ASSET_EXPLOSION=106, ASSET_ENEMY_ENERGY=111, ASSET_CASH25_BODY=112, ASSET_CASH25_VALUE=113, ASSET_CASH75_BODY=114, ASSET_CASH75_VALUE=115, ASSET_CASH50_BODY=116, ASSET_CASH50_VALUE=117, ASSET_GEM100_BODY=118, ASSET_GEM100_VALUE=119 };
/* Roads220..226,235..236; installation231..234 and underlay237..240 stay unchanged. */
static Asset assets[499];
/* One draw-call lease from the original fixed explosion; never gameplay state. */
static bool cash25_fixed_value;
static bool cash75_fixed_value;
static bool cash50_fixed_value;
static bool gem100_fixed_value;
static Asset talon_frames[13];
typedef struct {
 bool valid;
 const Uint8 *bank_data;
 uint64_t last_tick;
 int base,logical_index,visual_index;
 unsigned int invulnerable;
} TalonBank;
static TalonBank talon_banks[2];
static uint64_t mirror_logic_tick;
static bool talon_banking_enabled=true;
static unsigned int banking_draw_player;
static FILE *banking_trace;
static const int original_visual_indices[5]={0,2,6,10,12};

void render_mirror_reset_banking(void)
{memset(talon_banks,0,sizeof(talon_banks));banking_draw_player=0;}
void render_mirror_set_talon_banking(bool enabled)
{talon_banking_enabled=enabled;render_mirror_reset_banking();}
static char terrain_file;
static struct {const Uint8 *data;unsigned int id;} terrain_sources[199];
static unsigned int terrain_source_count;
static bool forest_registry_ok=true;
static SDL_Surface *canvas,*output;
static SDL_Surface *fade_saved;
static Uint32 fade_saved_palette[256],last_output_palette[256];
static Uint8 last_output_indices[320*200];
static bool last_output_valid,have_fade_saved;
/* HUD1 admits only whole opaque logical blocks. These output-coordinate masks
 * therefore represent every actually replaced subpixel exactly, independently
 * of scene-space hd_owner. They are not a screen-identification heuristic. */
static Uint8 hud_output_owner[320*200],hud_saved_owner[320*200];
static Uint32 hud_output_palette[256];
static uint64_t hud_generation,hud_output_generation,hud_saved_generation;
static bool hud_gameplay,hud_suspended,hud_live,last_output_scene_hd;
/* Lease the persistent indexed surface, not merely coincident pixel values. */
static SDL_Surface *hud_source_surface;
static void *hud_source_pixels;
static SDL_PixelFormat *hud_source_format;
static int hud_source_pitch,hud_source_width,hud_source_height;
static Uint8 component_output_owner[320*200],component_saved_owner[320*200];
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
static int fade_mode;
static SDL_Texture *texture;
static Uint8 expected[320*200], selected[320*200];
static Uint8 *hd_owner;
/* Finite cloud provenance; never changes indexed gameplay writes. */
static Uint8 *cloud_owner;
static bool suppress_cloud;
/* Green-head display layer: only green smoke may pass underneath it. Every
 * unrelated pixel write bakes/invalidate it at its original command position. */
typedef struct { Asset *asset; int x,y; } GreenHead;
static GreenHead green_heads[256];
static unsigned int green_head_count;
static Uint16 *green_first;
static Uint32 *green_under;
static Uint8 *green_under_owner;
static Uint32 initial_palette[256];
static bool have_initial_palette;
static bool active,suppress,ready;
/* PIC3 grants this scene lease independently of optional HUD resources. */
static bool manual_hd_lease;
static bool manual_hd_scope(void)
{
 return manual_hd_enabled&&episodeNum==1&&lvlFileNum==9&&!isNetworkGame&&
   !twoPlayerMode&&!galagaMode&&!play_demo&&!record_demo;
}
static bool mirror_enabled(void)
{
 return game_probe_enabled||(manual_hd_lease&&manual_hd_scope());
}
bool render_mirror_owns_display(void) { return active; }
static bool suppress_green_smoke;
static const char *reject_reason;
static unsigned int draws,occlusions,mismatch;
typedef struct { SDL_Rect rect; int bank,index,style; bool live; } HdRegion;
/* Fixed presentation bookkeeping budget; gameplay pools are unchanged. */
#define HD_REGION_CAPACITY 65536
static HdRegion regions[HD_REGION_CAPACITY];
static unsigned int region_count,local_entities,local_regions,local_blocks;
static char all_rejections[512];
static Uint8 restored_mask[320*200];
static unsigned int brightness_blocks,restored_checks,restored_mismatches,expanded_regions,boundary_crossings;
static Uint32 palette_rgb(Uint8 index);
static unsigned int blend_source_index;
#include "gameplay_hud_font_mirror.inc"

/* Display grouping requires all four recognized rectangles at their exact
 * original adjacency. It never reads/modifies enemy state or death links. */
static bool complete_turret_group(unsigned int n,SDL_Rect *group)
{
 HdRegion q=regions[n];
 if(q.bank!=ASSET_NEWSH2||q.style!=MIRROR_NORMAL)return false;
 int ids[4]={77,79,115,117},ox[4]={0,24,0,24},oy[4]={0,0,28,28},part=-1;
 for(int k=0;k<4;k++)if(q.index==ids[k])part=k;
 if(part<0)return false;
 *group=(SDL_Rect){q.rect.x-ox[part],q.rect.y-oy[part],48,56};
 for(int k=0;k<4;k++) {
  bool found=false;
  for(unsigned int j=0;j<region_count;j++)if(regions[j].bank==ASSET_NEWSH2&&regions[j].style==MIRROR_NORMAL&&regions[j].index==ids[k]&&regions[j].rect.x==group->x+ox[k]&&regions[j].rect.y==group->y+oy[k])found=true;
  if(!found)return false;
 }
 return true;
}

/* Exact classic composition only inside the affected earlier HD rectangle.
 * Original logical pixels are read at this command position, not at frame end.
 * No true-color asset is quantized, and unaffected HD pixels remain untouched. */
static void restore_classic_rect(SDL_Rect r)
{
 SDL_Rect requested=r;unsigned int prior_blocks=local_blocks,groups=0;
 /* Close over overlapping complete HD regions, so a rectangle cannot cut
  * through a neighboring RGBA object. Previously restored records are inert. */
 bool changed;
 do {
  changed=false;
  for(unsigned int i=0;i<region_count;i++) if(regions[i].live) {
   SDL_Rect q=regions[i].rect;
   if(game_probe_known_blend) {
    SDL_Rect g;
    if(complete_turret_group(i,&g)&&r.x<q.x+q.w&&r.x+r.w>q.x&&r.y<q.y+q.h&&r.y+r.h>q.y) {q=g;}
   }
   if(r.x<q.x+q.w&&r.x+r.w>q.x&&r.y<q.y+q.h&&r.y+r.h>q.y) {
    int x0=MIN(r.x,q.x),y0=MIN(r.y,q.y),x1=MAX(r.x+r.w,q.x+q.w),y1=MAX(r.y+r.h,q.y+q.h);
    if(x0!=r.x||y0!=r.y||x1!=r.x+r.w||y1!=r.y+r.h) {if(q.w==48&&q.h==56&&regions[i].bank==ASSET_NEWSH2)++groups;r.x=x0;r.y=y0;r.w=x1-x0;r.h=y1-y0;changed=true;++expanded_regions;}
   }
  }
 } while(changed);
 font_before_effect(r);
 for(unsigned int i=0;i<region_count;i++) if(regions[i].live) {
  SDL_Rect q=regions[i].rect;
  if(r.x<q.x+q.w&&r.x+r.w>q.x&&r.y<q.y+q.h&&r.y+r.h>q.y) {
   if(q.x<r.x||q.y<r.y||q.x+q.w>r.x+r.w||q.y+q.h>r.y+r.h)++boundary_crossings;
   regions[i].live=false;
  }
 }
 int x0=MAX(0,r.x),y0=MAX(0,r.y),x1=MIN(320,r.x+r.w),y1=MIN(200,r.y+r.h);
 int d=game_probe_density;
 ++local_regions;
 for(int y=y0;y<y1;y++) for(int x=x0;x<x1;x++) {
  Uint32 color=palette_rgb(((Uint8 *)game_screen->pixels)[y*game_screen->pitch+x]);
  bool replaced=false;
  for(int sy=0;sy<d;sy++) {
   Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+(y*d+sy)*canvas->pitch)+x*d;
   Uint8 *owner=hd_owner+(y*d+sy)*canvas->w+x*d;
   for(int sx=0;sx<d;sx++) {replaced=replaced||owner[sx]!=0;p[sx]=color;owner[sx]=0;green_first[(y*d+sy)*canvas->w+x*d+sx]=0;cloud_owner[(y*d+sy)*canvas->w+x*d+sx]=0;}
  }
  if(replaced) ++local_blocks;
  selected[y*320+x]=0;
  restored_mask[y*320+x]=1;
 }
 game_probe_restore_region(blend_source_index,requested,r,groups,local_blocks-prior_blocks);
}

static Uint32 palette_rgb(Uint8 index) { return 0xff000000u|(rgb_palette[index]&0x00ffffffu); }
static Uint32 blend_rgba(Uint32 dst,const Uint8 *src,int alpha)
{
 Uint32 out=0xff000000u;
 for(int c=0;c<3;c++) { int shift=(2-c)*8; unsigned int d=(dst>>shift)&255; out|=((d*(255-alpha)+src[c]*alpha+127)/255)<<shift; }
 return out;
}
/* Transfer only a verified original palette-shadow change to authored cloud
 * color. Repeated shadows at the original ramp floor are exact no-ops. A zero
 * source channel has no multiplicative ratio, so retain that HD channel. */
static Uint32 cloud_shadow_rgba(Uint32 color,Uint8 before,Uint8 after)
{
 if(before==after)return color;
 Uint32 from=palette_rgb(before),to=palette_rgb(after),out=0xff000000u;
 for(int shift=0;shift<24;shift+=8) {
  unsigned int current=(color>>shift)&255,den=(from>>shift)&255,num=(to>>shift)&255;
  unsigned int next=den?(current*num+den/2)/den:current;
  out|=MIN(next,255u)<<shift;
 }
 return out;
}
static bool cloud_asset(const Asset *a)
{
 return a->bank==ASSET_SHAPESZ&&((a->index>=41&&a->index<=45)||
        (a->index>=51&&a->index<=55)||(a->index>=61&&a->index<=65));
}
static Uint32 darken_rgba(Uint32 dst,int alpha)
{
 Uint32 out=0xff000000u;
 for(int shift=0;shift<24;shift+=8) out|=((((dst>>shift)&255)*(510-alpha)+255)/510)<<shift;
 return out;
}
/* Continuous HSV-value-style mapping for true color: retain channel ratios
 * and subpixel detail, shift peak brightness by value/15, saturate 0..255.
 * Classic pixels continue to use the exact original palette-ramp result. */
static Uint32 brightness_rgba(Uint32 color,int value)
{
 unsigned int channels[3]={(color>>16)&255,(color>>8)&255,color&255};
 unsigned int peak=MAX(channels[0],MAX(channels[1],channels[2]));
 unsigned int next=(unsigned int)MAX(0,MIN(255,(int)peak+value*17));
 Uint32 out=0xff000000u;
 for(int c=0;c<3;c++)out|=(peak?(channels[c]*next+peak/2)/peak:next)<<((2-c)*8);
 return out;
}

void render_mirror_brightness_pixel(SDL_Surface *surface,Uint8 *address,int value)
{
 if(!active||surface!=game_screen)return;
 intptr_t off=(intptr_t)address-(intptr_t)surface->pixels;
 if(off<0||off>=(intptr_t)surface->pitch*surface->h) {render_mirror_unsupported("invalid-brightness-address");return;}
 int y=(int)(off/surface->pitch),x=(int)(off%surface->pitch);
 if(x>=320||y>=200)return;
 font_before_effect((SDL_Rect){x,y,1,1});
 expected[y*320+x]=*address;
 if(value<-15||value>15) {render_mirror_unsupported("brightness-outside-signed-ramp");return;}
 if(reject_reason)return;
 int d=game_probe_density;bool touched_hd=false;
 for(int sy=0;sy<d;sy++) {
  Uint32 *row=(Uint32 *)((Uint8 *)canvas->pixels+(y*d+sy)*canvas->pitch)+x*d;
  const Uint8 *owner=hd_owner+(y*d+sy)*canvas->w+x*d;
  for(int sx=0;sx<d;sx++) {
   green_first[(y*d+sy)*canvas->w+x*d+sx]=0;
   cloud_owner[(y*d+sy)*canvas->w+x*d+sx]=0;
   if(owner[sx]==2)row[sx]=palette_rgb(*address); /* Explicit original-copy diagnostic. */
   else if(owner[sx]) {row[sx]=brightness_rgba(row[sx],value);touched_hd=true;}
   else row[sx]=palette_rgb(*address);
  }
 }
 if(touched_hd)++brightness_blocks;
}
static void upscale(SDL_Surface *dst,SDL_Surface *src)
{
 int d=game_probe_density;
 for(int y=0;y<src->h;y++) for(int sy=0;sy<d;sy++) {
  Uint32 *row=(Uint32 *)((Uint8 *)dst->pixels+(y*d+sy)*dst->pitch);
  const Uint8 *in=(Uint8 *)src->pixels+y*src->pitch;
  for(int x=0;x<src->w;x++) for(int sx=0;sx<d;sx++) row[x*d+sx]=palette_rgb(in[x]);
 }
}

/* Finite logical coordinates, top21 followed by the complete mode216. */
static int indicator_cell(int x,int y)
{
 if(x>=269&&x<276&&y>=4&&y<7)return (y-4)*7+x-269;
 if(x>=285&&x<312&&y>=44&&y<52)return 21+(y-44)*27+x-285;
 return -1;
}
static void indicator_position(unsigned int cell,int *x,int *y)
{
 if(cell<21) {*x=269+(int)(cell%7);*y=4+(int)(cell/7);}
 else {cell-=21;*x=285+(int)(cell%27);*y=44+(int)(cell/27);}
}
/* Exact approved 26 rim cells plus the 7x8 center grille; no other lower
 * layer may overlap HUL1. Row-major positions double as the bounded ledger. */
static int indicator_overlap(int x,int y)
{

 if(x<285||x>=312||y<44||y>=52)return -1;
 unsigned int logical=(unsigned int)(y*320+x);
 for(unsigned int i=0;i<82;i++)if(indicator_overlap_positions[i]==logical)return (int)i;
 return -1;
}
/* HUT1 has no overlap with the three existing HUD families. */
static bool components_owned(void);
static bool indicators_owned(void);
static bool fixed_text_owned(void)
{return memchr(fixed_text_output_owner,1,sizeof(fixed_text_output_owner))!=NULL;}
static bool fixed_text_source_matches(void)
{
 return VGAScreenSeg&&VGAScreenSeg==fixed_text_source_surface&&
  VGAScreenSeg->pixels&&VGAScreenSeg->pixels==fixed_text_source_pixels&&
  VGAScreenSeg->format&&VGAScreenSeg->format==fixed_text_source_format&&
  VGAScreenSeg->w==320&&VGAScreenSeg->h==200&&VGAScreenSeg->pitch==fixed_text_source_pitch&&
  VGAScreenSeg->format->BitsPerPixel==8&&VGAScreenSeg->format->BytesPerPixel==1;
}
static bool fixed_text_cached_indices_match(void)
{
 if(!fixed_text_source_matches())return false;
 for(int y=0;y<200;y++)
  if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320))return false;
 return true;
}
static void fixed_text_clear_cached(void)
{
 if(!fixed_text_owned()&&!memchr(fixed_text_saved_owner,1,sizeof(fixed_text_saved_owner)))return;
 int d=game_probe_density;
 bool verified=(d==4||d==8)&&output&&output->w==320*d&&output->h==200*d&&
  fixed_text_output_generation==fixed_text_generation&&
  (!memchr(fixed_text_saved_owner,1,sizeof(fixed_text_saved_owner))||fixed_text_saved_generation==fixed_text_generation)&&
  fixed_text_cached_indices_match()&&memcmp(fixed_text_output_palette,rgb_palette,sizeof(fixed_text_output_palette))==0&&
  (!have_fade_saved||(fade_saved&&fade_saved->w==output->w&&fade_saved->h==output->h));
 if(!verified) {ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}
 for(unsigned i=0;i<370;i++) {
  if(!fixed_text_output_owner[i]&&!fixed_text_saved_owner[i])continue;
  int x,y;hud_fixed_text_position(i,&x,&y);Uint8 index=last_output_indices[y*320+x];
  if(verified)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   if(fixed_text_output_owner[i])((Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch))[x*d+sx]=palette_rgb(index);
   if(fixed_text_saved_owner[i]&&have_fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+(y*d+sy)*fade_saved->pitch))[x*d+sx]=0xff000000u|(fade_saved_palette[index]&0xffffffu);
  }
 }
 memset(fixed_text_output_owner,0,sizeof(fixed_text_output_owner));memset(fixed_text_saved_owner,0,sizeof(fixed_text_saved_owner));
 fixed_text_output_generation=fixed_text_saved_generation=0;
 if(verified) {
  bool retained=last_output_scene_hd||memchr(hud_output_owner,1,sizeof(hud_output_owner))||components_owned()||indicators_owned()||font_owned();
  last_output_valid=last_output_valid&&retained;if(!retained) {have_fade_saved=false;fade_mode=0;}
 }
}
static void fixed_text_reset(void)
{
 fixed_text_clear_cached();++fixed_text_generation;if(!fixed_text_generation)++fixed_text_generation;
 fixed_text_gameplay=fixed_text_suspended=false;hud_fixed_text_forget_source();
 fixed_text_source_surface=NULL;fixed_text_source_pixels=NULL;fixed_text_source_format=NULL;fixed_text_source_pitch=0;
}
static void fixed_text_check_mode(void)
{
 if(fixed_text_gameplay&&(twoPlayerMode||galagaMode||!fixed_text_source_matches()))fixed_text_reset();
}
static void fixed_text_start(SDL_Surface *source)
{
 /* Grant is pristine indexedPIC3; normalRGB palette is installed later. */
 if(hud_fixed_text_load(game_probe_assets)&&hud_fixed_text_capture(source->pixels,source->pitch)) {
  fixed_text_source_surface=source;fixed_text_source_pixels=source->pixels;
  fixed_text_source_format=source->format;fixed_text_source_pitch=source->pitch;fixed_text_gameplay=true;
 }
}
static void fixed_text_begin(void)
{
 if(!fixed_text_gameplay)return;
 fixed_text_suspended=false;
 memset(fixed_text_output_owner,0,sizeof(fixed_text_output_owner));memset(fixed_text_saved_owner,0,sizeof(fixed_text_saved_owner));
 fixed_text_output_generation=fixed_text_saved_generation=0;
}
static bool fixed_text_compose(void)
{
 if(!fixed_text_gameplay||fixed_text_suspended||!hud_fixed_text_ready()||game_probe_original_reference||
  !hud_fixed_text_palette_matches(rgb_palette))return false;
 int d=game_probe_density;
 if((d!=4&&d!=8)||!output||output->w!=320*d||output->h!=200*d)return false;
 bool groups[3],retained=false;
 for(unsigned g=0;g<3;g++)groups[g]=hud_fixed_text_group_matches(g,VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 for(unsigned i=0;i<370;i++) {
  if(!groups[i<95?0:i<245?1:2])continue;
  int x,y;hud_fixed_text_position(i,&x,&y);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   const Uint8 *rgba=hud_fixed_text_sample(i,sx,sy,d);
   ((Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch))[x*d+sx]=0xff000000u|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2];
  }
  fixed_text_output_owner[i]=1;retained=true;
 }
 if(retained)fixed_text_output_generation=fixed_text_generation;
 return retained;
}

static bool indicators_owned(void)
{
 return memchr(indicator_output_owner,1,sizeof(indicator_output_owner))!=NULL||
   memchr(indicator_output_owner,2,sizeof(indicator_output_owner))!=NULL;
}
static bool indicators_source_matches(void)
{
 return VGAScreenSeg&&VGAScreenSeg==indicator_source_surface&&
   VGAScreenSeg->pixels&&VGAScreenSeg->pixels==indicator_source_pixels&&
   VGAScreenSeg->format&&VGAScreenSeg->format==indicator_source_format&&
   VGAScreenSeg->w==320&&VGAScreenSeg->h==200&&VGAScreenSeg->pitch==indicator_source_pitch&&
   VGAScreenSeg->format->BitsPerPixel==8&&VGAScreenSeg->format->BytesPerPixel==1;
}
static bool indicators_cached_indices_match(void)
{
 if(!indicators_source_matches())return false;
 for(int y=0;y<200;y++)
  if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)!=0)return false;
 return true;
}
static bool indicators_underlay_matches(void)
{
 if(indicator_under_density!=game_probe_density||
    (indicators_owned()&&indicator_output_generation!=indicator_generation)||
    ((memchr(indicator_saved_owner,1,sizeof(indicator_saved_owner))||memchr(indicator_saved_owner,2,sizeof(indicator_saved_owner)))&&indicator_saved_generation!=indicator_generation))return false;
 for(unsigned int i=0;i<82;i++) {
  unsigned int logical=indicator_overlap_positions[i];
  int cell=indicator_cell((int)(logical%320),(int)(logical/320));
  if(indicator_under_owner[i]&&(indicator_under_generation!=hud_generation||hud_output_generation!=hud_generation||
     !hud_output_owner[logical]||!indicator_output_owner[cell]))return false;
  if(indicator_saved_under_owner[i]&&(indicator_saved_under_generation!=hud_generation||hud_saved_generation!=hud_generation||
     !hud_saved_owner[logical]||!indicator_saved_owner[cell]))return false;
 }
 return true;
}
/* bits1=top, bits2=mode. Upper-layer removal restores the actual lower HUD1
 * RGB, including its independent fade history. Without lower ownership the
 * verified indexed/palette snapshot remains the authority. */
static void indicators_clear_cached(unsigned int bits)
{
 bool any=false;
 for(unsigned int i=0;i<237;i++)if((indicator_output_owner[i]|indicator_saved_owner[i])&bits) {any=true;break;}
 if(!any)return;
 int d=game_probe_density;
 bool verified=(d==4||d==8)&&output&&output->w==320*d&&output->h==200*d&&
   indicators_cached_indices_match()&&indicators_underlay_matches()&&
   memcmp(indicator_output_palette,rgb_palette,sizeof(indicator_output_palette))==0&&
   (!have_fade_saved||(fade_saved&&fade_saved->w==output->w&&fade_saved->h==output->h));
 if(!verified) {ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}
 for(unsigned int i=0;i<237;i++) {
  bool current=(indicator_output_owner[i]&bits)!=0,saved=(indicator_saved_owner[i]&bits)!=0;
  if(!current&&!saved)continue;
  int x,y;indicator_position(i,&x,&y);int under=indicator_overlap(x,y);Uint8 index=last_output_indices[y*320+x];
  if(verified)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   if(current)((Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch))[x*d+sx]=
     under>=0&&indicator_under_owner[under]?indicator_under[under][sy*d+sx]:palette_rgb(index);
   if(saved&&have_fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+(y*d+sy)*fade_saved->pitch))[x*d+sx]=
     under>=0&&indicator_saved_under_owner[under]?indicator_saved_under[under][sy*d+sx]:0xff000000u|(fade_saved_palette[index]&0xffffffu);
  }
  if(under>=0) {if(current)indicator_under_owner[under]=0;if(saved)indicator_saved_under_owner[under]=0;}
  indicator_output_owner[i]&=(Uint8)~bits;indicator_saved_owner[i]&=(Uint8)~bits;
 }
 if(!indicators_owned())indicator_output_generation=0;
 if(!memchr(indicator_saved_owner,1,sizeof(indicator_saved_owner))&&!memchr(indicator_saved_owner,2,sizeof(indicator_saved_owner)))indicator_saved_generation=0;
 if(verified) {
  bool retained=last_output_scene_hd||memchr(hud_output_owner,1,sizeof(hud_output_owner))||
    components_owned()||indicators_owned()||fixed_text_owned()||font_owned();
  last_output_valid=last_output_valid&&retained;
  if(!retained) {have_fade_saved=false;fade_mode=0;}
 }
}
static void indicators_reset(void)
{
 indicators_clear_cached(3);
 ++indicator_generation;if(!indicator_generation)++indicator_generation;
 indicator_gameplay=indicator_suspended=false;hud_indicators_forget_source();
 indicator_source_surface=NULL;indicator_source_pixels=NULL;indicator_source_format=NULL;indicator_source_pitch=0;
 memset(indicator_under_owner,0,sizeof(indicator_under_owner));memset(indicator_saved_under_owner,0,sizeof(indicator_saved_under_owner));
}
static bool hud_sprite_decode(unsigned int table,unsigned int index,unsigned int max_w,unsigned int max_h,Uint8 *indices,Uint8 *opaque);
static bool indicators_decode_modes(Uint8 indices[2][80],Uint8 opaque[2][80])
{
 for(unsigned int i=0;i<2;i++)
  if(!hud_sprite_decode(OPTION_SHAPES,18+i,10,8,indices[i],opaque[i])||
     sprite_table[OPTION_SHAPES].sprite[18+i].width!=10||sprite_table[OPTION_SHAPES].sprite[18+i].height!=8)return false;
 return hud_indicators_verify_modes((const Uint8 (*)[80])indices,(const Uint8 (*)[80])opaque);
}
static void indicators_check_mode(void)
{
 if(!indicator_gameplay)return;
 Uint8 indices[2][80],opaque[2][80];
 if(twoPlayerMode||galagaMode||!indicators_source_matches()||!indicators_decode_modes(indices,opaque))indicators_reset();
}
static void indicators_start(SDL_Surface *source)
{
 Uint8 indices[2][80],opaque[2][80];
 if(hud_indicators_load(game_probe_assets)&&indicators_decode_modes(indices,opaque)&&
    hud_indicators_capture(source->pixels,source->pitch,(const Uint8 (*)[80])indices,(const Uint8 (*)[80])opaque)) {
  indicator_source_surface=source;indicator_source_pixels=source->pixels;
  indicator_source_format=source->format;indicator_source_pitch=source->pitch;indicator_gameplay=true;
 }
}
static void indicators_begin(void)
{
 if(indicator_gameplay)indicator_suspended=false;
 memset(indicator_output_owner,0,sizeof(indicator_output_owner));memset(indicator_saved_owner,0,sizeof(indicator_saved_owner));
 memset(indicator_under_owner,0,sizeof(indicator_under_owner));memset(indicator_saved_under_owner,0,sizeof(indicator_saved_under_owner));
 indicator_output_generation=indicator_saved_generation=0;
 indicator_under_generation=indicator_saved_under_generation=0;indicator_under_density=game_probe_density;
}
void render_mirror_hud_mode_drawn(SDL_Surface *surface,unsigned int mode)
{
 if(!indicator_gameplay)return;
 indicators_check_mode();if(!indicator_gameplay)return;
 if(surface!=VGAScreenSeg||(mode!=1&&mode!=2)) {
  indicators_clear_cached(2);hud_indicators_mode_wiped();return;
 }
 /* Called only after both original OPTION blits completed. No game state is
  * inferred or modified; later composition verifies all 216 indexed cells. */
 hud_indicators_mode_drawn((int)mode);
}
static bool indicators_compose(void)
{
 if(!indicator_gameplay||indicator_suspended||!hud_indicators_ready()||game_probe_original_reference||
    !hud_indicators_palette_matches(rgb_palette))return false;
 int d=game_probe_density;
 if((d!=4&&d!=8)||!output||output->w!=320*d||output->h!=200*d)return false;
 bool top=hud_indicators_top_matches(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 bool mode=hud_indicators_mode_ready()&&hud_indicators_mode_matches(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 if(!mode)hud_indicators_mode_wiped();
 bool retained=false;indicator_under_density=d;
 for(unsigned int i=0;i<237;i++) {
  if(i<21?!top:!mode)continue;
  int x,y;indicator_position(i,&x,&y);int under=indicator_overlap(x,y);
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x];
  if(!hud_indicators_sample(x,y,0,0,d,index))continue;
  bool lower=under>=0&&hud_output_generation==hud_generation&&hud_output_owner[y*320+x];
  for(int sy=0;sy<d;sy++) {
   Uint32 *row=(Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch)+x*d;
   for(int sx=0;sx<d;sx++) {
    if(lower)indicator_under[under][sy*d+sx]=row[sx];
    const Uint8 *rgba=hud_indicators_sample(x,y,sx,sy,d,index);
    row[sx]=0xff000000u|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2];
   }
  }
  if(lower) {indicator_under_owner[under]=1;indicator_under_generation=hud_generation;}
  indicator_output_owner[i]=i<21?1:2;retained=true;
 }
 if(retained)indicator_output_generation=indicator_generation;
 return retained;
}
/* Hidden lower RGB follows the same rounded channel recurrence as visible
 * HUD1. Restore targets its saved underlay, never the upper indicator image. */
static void indicators_fade_underlay(int steps)
{
 for(unsigned int i=0;i<82;i++)if(indicator_under_owner[i]&&indicator_saved_under_owner[i])
  for(int sub=0;sub<game_probe_density*game_probe_density;sub++) {
   Uint32 target=fade_mode==1?0:fade_mode==2?0xffffffu:indicator_saved_under[i][sub],color=0xff000000u;
   for(int shift=0;shift<24;shift+=8) {
    int old=(indicator_under[i][sub]>>shift)&255,want=(target>>shift)&255;
    color|=(Uint32)(old+(want-old)/steps)<<shift;
   }
   indicator_under[i][sub]=color;
  }
}

/* HUC1/HUM2 ownership shares the PIC3 lease, independently of static HUD1. */
static bool components_owned(void)
{
 for(unsigned i=0;i<320*200;i++)if(component_output_owner[i]&63)return true;
 return false;
}

static bool components_source_matches(void)
{
 return VGAScreenSeg&&VGAScreenSeg==component_source_surface&&
   VGAScreenSeg->pixels&&VGAScreenSeg->pixels==component_source_pixels&&
   VGAScreenSeg->format&&VGAScreenSeg->format==component_source_format&&
   VGAScreenSeg->w==320&&VGAScreenSeg->h==200&&VGAScreenSeg->pitch==component_source_pitch&&
   VGAScreenSeg->format->BitsPerPixel==8&&VGAScreenSeg->format->BytesPerPixel==1;
}

static bool components_cached_indices_match(void)
{
 if(!components_source_matches()||(game_probe_density!=4&&game_probe_density!=8)||
    !output||output->w!=320*game_probe_density||output->h!=200*game_probe_density||
    (component_output_generation&&component_output_generation!=component_generation)||
    (component_saved_generation&&component_saved_generation!=component_generation))return false;
 bool current=false,saved=false;
 for(unsigned i=0;i<320*200;i++) {
  unsigned c=component_output_owner[i],s=component_saved_owner[i];
  if((c&~63u)||(s&~63u)||(c&&(c&(c-1)))||(s&&(s&(s-1))))return false;
  current|=c!=0;saved|=s!=0;
  if(c&&component_output_generation!=component_generation)return false;
  if(s&&component_saved_generation!=component_generation)return false;
  if(have_fade_saved&&c!=s)return false;
 }
 if(current!=(component_output_generation!=0)||saved!=(component_saved_generation!=0))return false;
 if(have_fade_saved) {
  if(component_output_generation!=component_saved_generation||!fade_saved||
     fade_saved->w!=output->w||fade_saved->h!=output->h)return false;
 } else if(saved||component_saved_generation)return false;
 for(int y=0;y<200;y++)
  if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)!=0)return false;
 return true;
}

/* bits1=labels,2=shield,4/8=front/rear,16=generator,32=armor. Each original
 * write removes only its field. Modal suspension removes all63. Never restore
 * from unverified source/layout/generation/palette or missing saved storage. */
static void components_clear_cached(unsigned int bits)
{
 unsigned int clear_bits=bits==63?255:bits;
 bool any=false;
 for(unsigned int i=0;i<320*200;i++)
  if((component_output_owner[i]|component_saved_owner[i])&clear_bits) {any=true;break;}
 if(!any) {
  if(bits==63&&(component_output_generation||component_saved_generation)) {
   ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;
   memset(component_output_owner,0,sizeof(component_output_owner));
   memset(component_saved_owner,0,sizeof(component_saved_owner));
   component_output_generation=component_saved_generation=0;
  }
  return;
 }
 bool verified=output&&output->w==320*game_probe_density&&output->h==200*game_probe_density&&
   components_cached_indices_match()&&memcmp(component_output_palette,rgb_palette,sizeof(component_output_palette))==0;
 if(!verified) {ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}
 int d=game_probe_density;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  unsigned int i=(unsigned int)(y*320+x);
  bool current=(component_output_owner[i]&clear_bits)!=0,saved=(component_saved_owner[i]&clear_bits)!=0;
  if(!current&&!saved)continue;
  if(verified)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   if(current)((Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch))[x*d+sx]=palette_rgb(last_output_indices[i]);
   if(saved&&have_fade_saved&&fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+(y*d+sy)*fade_saved->pitch))[x*d+sx]=0xff000000u|(fade_saved_palette[last_output_indices[i]]&0xffffffu);
  }
  component_output_owner[i]&=(Uint8)(bits==63?0:~bits);component_saved_owner[i]&=(Uint8)(bits==63?0:~bits);
 }
 if(!components_owned())component_output_generation=0;
 bool saved_remaining=false;
 for(unsigned i=0;i<320*200;i++)if(component_saved_owner[i]&63) {saved_remaining=true;break;}
 if(!saved_remaining)component_saved_generation=0;
 if(verified) {
  bool retained=last_output_scene_hd||memchr(hud_output_owner,1,sizeof(hud_output_owner))||components_owned()||indicators_owned()||fixed_text_owned()||font_owned();
  last_output_valid=last_output_valid&&retained;
  if(!retained) {have_fade_saved=false;fade_mode=0;}
 }
}

static void components_reset(void)
{
 components_clear_cached(63);
 ++component_generation;if(!component_generation)++component_generation;
 component_gameplay=component_suspended=false;hud_components_forget_source();hud_meters_forget_source();
 component_source_surface=NULL;component_source_pixels=NULL;component_source_format=NULL;component_source_pitch=0;
}

static void components_check_mode(void)
{
 if(component_gameplay&&(twoPlayerMode||galagaMode||!components_source_matches()))components_reset();
}

static void components_start(SDL_Surface *source)
{
 /* Caller already checked the explicit pristine PIC3 grant and 8-bit layout. */
 bool words=hud_components_load(game_probe_assets)&&hud_components_capture(source->pixels,source->pitch);
 bool meters=hud_meters_load(game_probe_assets)&&hud_meters_capture(source->pixels,source->pitch);
 if(words||meters) {
  component_source_surface=source;component_source_pixels=source->pixels;
  component_source_format=source->format;component_source_pitch=source->pitch;component_gameplay=true;
 }
}

static void components_begin(void)
{
 if(!component_gameplay)return;
 component_suspended=false;
 memset(component_output_owner,0,sizeof(component_output_owner));
 memset(component_saved_owner,0,sizeof(component_saved_owner));
 component_output_generation=component_saved_generation=0;
}

void render_mirror_hud_shield_wiped(SDL_Surface *surface)
{
 if(!component_gameplay)return;
 components_check_mode();
 if(!component_gameplay)return;
 /* Notification precedes original clears, so valid cached scene/frame/labels
  * can survive shield removal. The subsequent indexed write stays authoritative. */
 components_clear_cached(2);hud_components_shield_wiped();
 (void)surface;
}

void render_mirror_hud_shield_drawn(SDL_Surface *surface,unsigned int shield,unsigned int maximum)
{
 if(!component_gameplay)return;
 components_check_mode();
 if(!component_gameplay)return;
 if(surface!=VGAScreenSeg||shield>28||maximum>28||shield>maximum) {
  components_clear_cached(2);hud_components_shield_wiped();return;
 }
 /* This runs after the original writer, never simulates or updates game state.
  * A later finish verifies every one of the 522 indexed channel pixels. */
 hud_components_shield_drawn((int)shield,(int)maximum);
}

/* Shared PIC3 lease, independent HUC1/HUM2 readiness and per-field history. */
void render_mirror_hud_meter_begin(SDL_Surface *surface,SDL_Surface *draw_surface,unsigned int kind,unsigned int a,unsigned int b)
{
 if(!component_gameplay||!hud_meters_ready())return;
 components_check_mode();if(!component_gameplay)return;
 unsigned bits=hud_meters_event_bits(kind);if(!bits)bits=HUD_METERS_ALL;
 components_clear_cached(bits);
 if(surface!=VGAScreenSeg||draw_surface!=VGAScreenSeg) {hud_meters_revoke(bits);return;}
 hud_meters_write_begin(kind,a,b);
}
void render_mirror_hud_meter_end(SDL_Surface *surface,unsigned int kind)
{
 if(!component_gameplay||!hud_meters_ready())return;
 components_check_mode();if(!component_gameplay)return;
 unsigned bits=hud_meters_event_bits(kind);if(!bits)bits=HUD_METERS_ALL;
 if(surface!=VGAScreenSeg) {hud_meters_revoke(bits);return;}
 hud_meters_write_end(kind,VGAScreenSeg->pixels,VGAScreenSeg->pitch);
}
static bool components_compose(void)
{
 if(!component_gameplay||component_suspended||game_probe_original_reference)return false;
 bool words=hud_components_ready()&&hud_components_palette_matches(rgb_palette);
 bool meters=hud_meters_ready()&&hud_meters_palette_matches(rgb_palette);
 if(!words&&!meters)return false;
 int d=game_probe_density;
 if((d!=4&&d!=8)||!output||output->w!=320*d||output->h!=200*d)return false;
 bool shield=words&&hud_components_shield_ready()&&hud_components_shield_matches(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 if(!shield)hud_components_shield_wiped();
 unsigned meter_bits=meters?hud_meters_prepare(VGAScreenSeg->pixels,VGAScreenSeg->pitch):0;
 static const int boxes[][4]={{285,5,309,10},{285,11,299,16},{285,26,303,31},{285,32,299,37},{270,137,279,195},
  {289,17,311,20},{289,38,311,41},{269,12,277,104},{307,137,316,195}};
 bool retained=false;
 for(unsigned int box=0;box<COUNTOF(boxes);box++) {
  bool bar=box==4,meter=box>=5;unsigned kind=meter?4u<<(box-5):bar?2:1;
  if((box<4&&!words)||(bar&&!shield)||(meter&&!(meter_bits&kind)))continue;
  for(int y=boxes[box][1];y<boxes[box][3];y++)for(int x=boxes[box][0];x<boxes[box][2];x++) {
   Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x];
   const Uint8 *rgba=meter?hud_meters_sample(x,y,0,0,d,index):bar?hud_components_shield_sample(x,y,0,0,d,index):hud_components_label_sample(x,y,0,0,d,index);
   if(!rgba)continue;
   for(int sy=0;sy<d;sy++) {
    Uint32 *row=(Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch)+x*d;
    for(int sx=0;sx<d;sx++) {
     rgba=meter?hud_meters_sample(x,y,sx,sy,d,index):bar?hud_components_shield_sample(x,y,sx,sy,d,index):hud_components_label_sample(x,y,sx,sy,d,index);
     row[sx]=0xff000000u|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2];
    }
   }
   component_output_owner[y*320+x]=(Uint8)kind;retained=true;
  }
 }
 if(retained)component_output_generation=component_generation;
 return retained;
}

static bool hud_source_matches(void)
{
 /* Compare identity before dereferencing; a replaced/freed old allocation is
  * never read. True video teardown revokes before freeing the current one. */
 return VGAScreenSeg&&VGAScreenSeg==hud_source_surface&&
   VGAScreenSeg->pixels&&VGAScreenSeg->pixels==hud_source_pixels&&
   VGAScreenSeg->format&&VGAScreenSeg->format==hud_source_format&&
   VGAScreenSeg->pitch==hud_source_pitch&&VGAScreenSeg->w==hud_source_width&&
   VGAScreenSeg->h==hud_source_height&&VGAScreenSeg->format->BitsPerPixel==8&&
   VGAScreenSeg->format->BytesPerPixel==1;
}

static bool hud_cached_indices_match(void)
{
 if(!hud_source_matches())return false;
 for(int y=0;y<200;y++)
  if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)!=0)return false;
 return true;
}

/* Remove only baked HUD samples. The scene fade image survives suspension when
 * the original indexed/palette snapshot still describes this output. A stale
 * cache cannot be repaired from a different screen and is rejected instead. */
static void hud_clear_cached(void)
{
 bool owned=memchr(hud_output_owner,1,sizeof(hud_output_owner))!=NULL;
 bool saved=memchr(hud_saved_owner,1,sizeof(hud_saved_owner))!=NULL;
 if(owned||saved) {
  bool verified=output&&output->w==320*game_probe_density&&output->h==200*game_probe_density&&
    hud_cached_indices_match()&&memcmp(hud_output_palette,rgb_palette,sizeof(hud_output_palette))==0;
  if(!verified) {
   ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;
  } else {
   int d=game_probe_density;
   for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
    unsigned int i=(unsigned int)(y*320+x);Uint8 index=last_output_indices[i];
    if(!hud_output_owner[i]&&!hud_saved_owner[i])continue;
    int cell=indicator_cell(x,y),under=indicator_overlap(x,y);
    bool upper=cell>=0&&indicator_output_owner[cell],saved_upper=cell>=0&&indicator_saved_owner[cell];
    if(under>=0) {indicator_under_owner[under]=0;indicator_saved_under_owner[under]=0;}
    for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
     if(hud_output_owner[i]&&!upper)
      ((Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch))[x*d+sx]=palette_rgb(index);
     if(hud_saved_owner[i]&&!saved_upper&&have_fade_saved&&fade_saved)
      ((Uint32 *)((Uint8 *)fade_saved->pixels+(y*d+sy)*fade_saved->pitch))[x*d+sx]=0xff000000u|(fade_saved_palette[index]&0xffffffu);
    }
   }
   bool retained=last_output_scene_hd||components_owned()||indicators_owned()||fixed_text_owned()||font_owned();
   last_output_valid=last_output_valid&&retained;
   if(!retained) {have_fade_saved=false;fade_mode=0;}
  }
 }
 memset(hud_output_owner,0,sizeof(hud_output_owner));
 memset(hud_saved_owner,0,sizeof(hud_saved_owner));
 memset(indicator_under_owner,0,sizeof(indicator_under_owner));memset(indicator_saved_under_owner,0,sizeof(indicator_saved_under_owner));
 hud_output_generation=hud_saved_generation=0;
}

static void hud_frame_reset(void)
{
 hud_clear_cached();
 ++hud_generation;if(!hud_generation)++hud_generation;
 hud_gameplay=false;hud_suspended=false;hud_live=false;gameplay_hud_forget_source();
 hud_source_surface=NULL;hud_source_pixels=NULL;hud_source_format=NULL;
 hud_source_pitch=hud_source_width=hud_source_height=0;
}

void render_mirror_hud_reset(void)
{
 font_reset();fixed_text_reset();indicators_reset();components_reset();hud_frame_reset();
 if(manual_hd_enabled) {
  manual_hd_lease=false;active=false;ready=false;
  last_output_valid=false;last_output_scene_hd=false;have_fade_saved=false;fade_mode=0;
  have_initial_palette=false;render_mirror_reset_banking();
 }
}

void render_mirror_hud_shutdown(void)
{
 render_mirror_hud_reset();gameplay_hud_shutdown();hud_components_shutdown();hud_meters_shutdown();hud_indicators_shutdown();hud_fixed_text_shutdown();font_shutdown();
}

/* Validate the original bytecode as well as declared dimensions: malformed RLE
 * must not silently write past an audited font/icon/mode footprint. All bounds
 * are tiny fixed HUD limits; this is allocation-free and never paints a sprite. */
static bool hud_sprite_decode(unsigned int table,unsigned int index,unsigned int max_w,unsigned int max_h,Uint8 *indices,Uint8 *opaque)
{
 if(table>=SPRITE_TABLES_MAX||sprite_table[table].count>SPRITES_PER_TABLE_MAX||
    index>=sprite_table[table].count)return false;
 const Sprite *s=&sprite_table[table].sprite[index];
 if(!s->data||!s->width||!s->height||s->width>max_w||s->height>max_h||
    !s->size||s->size>2u*s->width*s->height+s->height)return false;
 if(indices)memset(indices,0,(size_t)s->width*s->height);
 if(opaque)memset(opaque,0,(size_t)s->width*s->height);
 unsigned int x=0,y=0;
 for(unsigned int i=0;i<s->size;i++) {
  if(y>=s->height)return false;
  Uint8 v=s->data[i];
  if(v==255) {
   if(++i>=s->size||s->data[i]>s->width-x)return false;
   x+=s->data[i];
  } else if(v==254)x=s->width;
  else if(v==253)++x;
  else {
   if(indices)indices[y*s->width+x]=v;
   if(opaque)opaque[y*s->width+x]=255;
   ++x;
  }
  if(x>=s->width) {x=0;++y;}
 }
 return true;
}

static bool hud_runtime_compatible(bool live)
{
 if(!gameplay_hud_has_expansion())return true;
 bool checked[SPRITES_PER_TABLE_MAX]={false};
 for(unsigned int c=0;c<256;c++) {
  int id=font_ascii[c];
  if(id<0)continue;
  if(id>=SPRITES_PER_TABLE_MAX)return false;
  if(!checked[id]&&!hud_sprite_decode(TINY_FONT,(unsigned int)id,6,8,NULL,NULL))return false;
  checked[id]=true;
 }
 memset(checked,0,sizeof(checked));
 for(unsigned int i=0;i<=OPTION_NUM;i++) {
  unsigned int ammo=options[i].ammo,unit=MAX(1u,ammo/10u);
  if((ammo+unit-1)/unit>10)return false;
  unsigned int icon=options[i].icongr;
  if(!icon)continue;
  --icon;
  if(icon>=SPRITES_PER_TABLE_MAX)return false;
  if(!checked[icon]&&!hud_sprite_decode(OPTION_SHAPES,icon,28,13,NULL,NULL))return false;
  checked[icon]=true;
 }
 for(unsigned int i=0;i<=SHIELD_NUM;i++)if(shields[i].mpwr>14)return false;
 if(!memchr(levelName,'\0',sizeof(levelName)))return false;
 Uint8 mode_indices[2][80],mode_opaque[2][80];
 for(unsigned int i=0;i<2;i++) {
  if(!hud_sprite_decode(OPTION_SHAPES,18+i,10,8,mode_indices[i],mode_opaque[i])||
     sprite_table[OPTION_SHAPES].sprite[18+i].width!=10||sprite_table[OPTION_SHAPES].sprite[18+i].height!=8)return false;
 }
 if(!gameplay_hud_verify_modes((const Uint8 (*)[80])mode_indices,(const Uint8 (*)[80])mode_opaque))return false;
 if(live) {
  if(power>900||lastPower>90||player[0].shield>28||player[0].shield_max>28||player[0].armor>28)return false;
  for(unsigned int i=0;i<2;i++) {
   if(player[0].items.weapon[i].power>11||player[0].items.sidekick[i]>OPTION_NUM)return false;
   int ammo=player[0].sidekick[i].ammo,maximum=player[0].sidekick[i].ammo_max;
   if(ammo<0||maximum<0||ammo>maximum||maximum>255)return false;
   unsigned int unit=MAX(1u,(unsigned int)maximum/10u);
   if(((unsigned int)maximum+unit-1)/unit>10)return false;
  }
 }
 return true;
}

static void hud_check_mode(void)
{
 font_check_mode();fixed_text_check_mode();indicators_check_mode();components_check_mode();
 if(((twoPlayerMode||galagaMode)&&(hud_gameplay||hud_suspended))||
    (hud_gameplay&&(!hud_source_matches()||!hud_runtime_compatible(hud_live))))hud_frame_reset();
}

void render_mirror_hud_start(SDL_Surface *decoded_pic3)
{
 /* This is called only at the successful gameplay PIC3 load, before options
  * and text. Generic JE_loadPic never grants gameplay ownership. */
 render_mirror_hud_reset();
 if(!decoded_pic3||decoded_pic3!=VGAScreenSeg||!decoded_pic3->pixels||decoded_pic3->w!=320||decoded_pic3->h!=200||decoded_pic3->pitch<320||
    !decoded_pic3->format||decoded_pic3->format->BitsPerPixel!=8||decoded_pic3->format->BytesPerPixel!=1)return;
 manual_hd_lease=manual_hd_scope();
 if(twoPlayerMode||galagaMode||!mirror_enabled()||game_probe_missing||game_probe_invalid||
    game_probe_original_reference||(game_probe_density!=4&&game_probe_density!=8))return;
 if(gameplay_hud_load(game_probe_assets)&&gameplay_hud_capture(decoded_pic3->pixels,decoded_pic3->pitch)) {
  if(hud_runtime_compatible(false)) {
   hud_source_surface=decoded_pic3;hud_source_pixels=decoded_pic3->pixels;hud_source_format=decoded_pic3->format;
   hud_source_pitch=decoded_pic3->pitch;hud_source_width=decoded_pic3->w;hud_source_height=decoded_pic3->h;
   hud_gameplay=true;
  }
  else gameplay_hud_forget_source();
 }
 components_start(decoded_pic3);indicators_start(decoded_pic3);fixed_text_start(decoded_pic3);font_start(decoded_pic3);
}

void render_mirror_hud_suspend(void)
{
 hud_check_mode();
 font_suspend();fixed_text_clear_cached();if(fixed_text_gameplay)fixed_text_suspended=true;
 indicators_clear_cached(3);if(indicator_gameplay)indicator_suspended=true;
 components_clear_cached(63);
 if(component_gameplay)component_suspended=true;
 hud_clear_cached();
 if(hud_gameplay)hud_suspended=true;
}

static void hud_begin(void)
{
 /* PIC capture precedes level stat initialization. Live gauge bounds become
  * meaningful at the first simulation begin, then stay checked through fades. */
 if(hud_gameplay)hud_live=true;
 hud_check_mode();
 /* Reset revokes the generation; only an intact gameplay capture may resume. */
 if(hud_gameplay&&gameplay_hud_ready())hud_suspended=false;
 memset(hud_output_owner,0,sizeof(hud_output_owner));
 memset(hud_saved_owner,0,sizeof(hud_saved_owner));
 hud_output_generation=hud_saved_generation=0;
 components_begin();indicators_begin();fixed_text_begin();font_begin();
}

static bool hud_compose(void)
{
 if(!hud_gameplay||hud_suspended||!gameplay_hud_ready()||game_probe_original_reference)return false;
 int d=game_probe_density;
 if((d!=4&&d!=8)||!output||output->w!=320*d||output->h!=200*d)return false;
 gameplay_hud_prepare_corner(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 bool retained=false;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  if(x<264&&y<184)continue;
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x];
  if(!gameplay_hud_sample(x,y,0,0,d,index))continue;
  for(int sy=0;sy<d;sy++) {
   Uint32 *row=(Uint32 *)((Uint8 *)output->pixels+(y*d+sy)*output->pitch)+x*d;
   for(int sx=0;sx<d;sx++) {
    const Uint8 *rgba=gameplay_hud_sample(x,y,sx,sy,d,index);
    row[sx]=0xff000000u|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2];
   }
  }
  hud_output_owner[y*320+x]=1;retained=true;
 }
 if(retained)hud_output_generation=hud_generation;
 return retained;
}

void render_mirror_begin(void)
{
 cash25_fixed_value=false;
 cash75_fixed_value=false;
 cash50_fixed_value=false;
 gem100_fixed_value=false;
 if(manual_hd_enabled&&!mirror_enabled()) {render_mirror_hud_reset();return;}
 hud_begin();
 /* JE_main level_loop calls begin exactly once per simulation tick. Neither
  * individual sprites, shadows nor repeated Present calls advance this clock. */
 ground101_frame_reset();
 ++mirror_logic_tick;banking_draw_player=0;
 last_output_valid=false;have_fade_saved=false;fade_mode=0;
 ready=false; active=false; suppress=false;suppress_green_smoke=false;suppress_cloud=false;
 if(!mirror_enabled()) return;
 if(!have_initial_palette) {memcpy(initial_palette,rgb_palette,sizeof(initial_palette));have_initial_palette=true;}
 if(asset_debug_fast_forward())return;
 if(!canvas) {
  int d=game_probe_density;
  canvas=SDL_CreateRGBSurfaceWithFormat(0,320*d,200*d,32,SDL_PIXELFORMAT_ARGB8888);
  output=SDL_CreateRGBSurfaceWithFormat(0,320*d,200*d,32,SDL_PIXELFORMAT_ARGB8888);
  hd_owner=calloc((size_t)320*200*d*d,1);
  cloud_owner=calloc((size_t)320*200*d*d,1);
  green_first=calloc((size_t)320*200*d*d,sizeof(*green_first));
  green_under=malloc((size_t)320*200*d*d*sizeof(*green_under));
  green_under_owner=malloc((size_t)320*200*d*d);
 }
 if(!canvas||!output||!hd_owner||!cloud_owner||!green_first||!green_under||!green_under_owner) return;
 if(!have_initial_palette) { memcpy(initial_palette,rgb_palette,sizeof(initial_palette));have_initial_palette=true; }
 for(int y=0;y<200;y++) memcpy(expected+y*320,(Uint8 *)game_screen->pixels+y*game_screen->pitch,320);
 upscale(canvas,game_screen);
 memset(selected,0,sizeof(selected)); memset(hd_owner,0,(size_t)canvas->w*canvas->h); draws=occlusions=mismatch=0; reject_reason=NULL; active=true;
 memset(cloud_owner,0,(size_t)canvas->w*canvas->h);
 green_head_count=0;memset(green_first,0,(size_t)canvas->w*canvas->h*sizeof(*green_first));
 region_count=local_entities=local_regions=local_blocks=0;all_rejections[0]='\0';
 memset(restored_mask,0,sizeof(restored_mask));brightness_blocks=restored_checks=restored_mismatches=expanded_regions=boundary_crossings=0;
}

void render_mirror_pixel(SDL_Surface *surface,Uint8 *address,Uint8 source,int style)
{
 settings_font_pixel(surface,address,style);
 load_font_pixel(surface,address,style);
 selector_font_pixel(surface,address,style);
 pregame_font_pixel(surface,address,style);
 if(!active||surface!=game_screen) return;
 intptr_t offset=(intptr_t)address-(intptr_t)surface->pixels;
 if(offset<0||offset>=(intptr_t)surface->pitch*surface->h) { render_mirror_unsupported("invalid-write-address");return; }
 int y=(int)(offset/surface->pitch),x=(int)(offset%surface->pitch);
 if(x>=320||y>=200) return;
 Uint8 before=expected[y*320+x];expected[y*320+x]=*address;
 if(reject_reason) return;
 if(font_pixel(x,y,*address,style))return;
 if(suppress) {
  /* The replacement's transparent pixels preserve the earlier RGB scene.
   * Original covered pixels still advance the indexed engine, but must not
   * reappear through that transparency when a later palette fade runs. */
  int d=game_probe_density;
  for(int sy=0;sy<d;sy++)memset(hd_owner+(y*d+sy)*canvas->w+x*d,game_probe_original_reference?2:1,(size_t)d);
  if(!suppress_cloud)for(int sy=0;sy<d;sy++)memset(cloud_owner+(y*d+sy)*canvas->w+x*d,0,(size_t)d);
  if(suppress_green_smoke)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   int n=(y*d+sy)*canvas->w+x*d+sx;
   if(green_first[n])green_under_owner[n]=1;
  }
  selected[y*320+x]=1;
  return;
 }
 if(selected[y*320+x]) { ++occlusions; selected[y*320+x]=0; }
 int d=game_probe_density;
 for(int sy=0;sy<d;sy++) {
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+(y*d+sy)*canvas->pitch)+x*d;
  Uint8 *owner=hd_owner+(y*d+sy)*canvas->w+x*d;
  for(int sx=0;sx<d;sx++) {
   int n=(y*d+sy)*canvas->w+x*d+sx;
   green_first[n]=0;
   bool cloud_shadow=cloud_owner[n]&&owner[sx]==1&&style==MIRROR_SHADOW&&
                     *address==(Uint8)((before&0xf0)|((before&15)/2));
   if(!cloud_shadow)cloud_owner[n]=0;
   if(owner[sx]&&style==MIRROR_BLEND) {
    if(!game_probe_local_blend) {render_mirror_unsupported("hd-under-palette-blend");return;}
    bool found=false;
    for(unsigned int i=0;i<region_count;i++) {
     SDL_Rect r=regions[i].rect;
     if(regions[i].live&&x>=r.x&&x<r.x+r.w&&y>=r.y&&y<r.y+r.h) {restore_classic_rect(r);found=true;}
    }
    if(!found) {render_mirror_unsupported("local-blend-owner-without-region");return;}
   }
   if(cloud_shadow)p[sx]=cloud_shadow_rgba(p[sx],before,*address);
   else if(owner[sx]==1&&style==MIRROR_SHADOW) p[sx]=darken_rgba(p[sx],255);
   else {p[sx]=palette_rgb(*address);if(style==MIRROR_NORMAL) owner[sx]=0;}
  }
 }
 (void)source;

}

void render_mirror_rect(SDL_Surface *s,const SDL_Rect *rect)
{
 settings_font_rect(s,rect);
 load_font_rect(s,rect);
 selector_font_rect(s,rect);
 pregame_font_rect(s,rect);
 if(!active||s!=game_screen) return;
 int x0=rect?rect->x:0,y0=rect?rect->y:0;
 int x1=rect?rect->x+rect->w:s->w,y1=rect?rect->y+rect->h:s->h;
 x0=MAX(x0,s->clip_rect.x);y0=MAX(y0,s->clip_rect.y);
 x1=MIN(x1,s->clip_rect.x+s->clip_rect.w);y1=MIN(y1,s->clip_rect.y+s->clip_rect.h);
 for(int y=y0;y<y1;y++) for(int x=x0;x<x1;x++) {
  Uint8 *p=(Uint8 *)s->pixels+y*s->pitch+x;render_mirror_pixel(s,p,*p,MIRROR_NORMAL);
 }
}

void render_mirror_unsupported(const char *reason)
{
 if(!active)return;
 if(!reject_reason) reject_reason=reason;
 if(!strstr(all_rejections,reason)) {
  size_t used=strlen(all_rejections),needed=strlen(reason)+(used?1:0);
  if(used+needed<sizeof(all_rejections)) {
   if(used)all_rejections[used++]='|';
   memcpy(all_rejections+used,reason,strlen(reason)+1);
  }
 }
}

static bool decode_tile(Sprite2_array bank,unsigned int index,Uint8 *indices,Uint8 *coverage,int w,int ox,int oy)
{
 if(!index||bank.size<2||2*(size_t)index>bank.size) return false;
 size_t pos=bank.data[2*(index-1)]|((size_t)bank.data[2*(index-1)+1]<<8);
 int x=0,y=0;
 for(size_t guard=0;guard<bank.size&&pos<bank.size;guard++) {
  unsigned int code=bank.data[pos++];if(code==15) return true;
  x+=code&15;unsigned int n=code>>4;
  if(!n) { ++y;x-=12; }
  else for(unsigned int j=0;j<n;j++) {
   if(pos>=bank.size||x<0||x>=12||y<0||y>=14) return false;
   indices[(oy+y)*w+ox+x]=bank.data[pos++];coverage[(oy+y)*w+ox+x]=255;++x;
  }
 }
 return false;
}

static bool read_asset(Asset *a,int wanted)
{
 char name[1024];
 const char *prefix=a->bank==ASSET_GEM100_BODY?"gem100-bank11":a->bank==ASSET_GEM100_VALUE?"gem100-value-newsh6":a->bank==ASSET_CASH50_BODY?"coin50-bank11":a->bank==ASSET_CASH50_VALUE?"coin50-value-newsh6":a->bank==ASSET_CASH75_BODY?"coin75-bank11":a->bank==ASSET_CASH75_VALUE?"coin75-value-newsh6":a->bank==ASSET_CASH25_BODY?"coin25-bank11":a->bank==ASSET_CASH25_VALUE?"coin25-value-newsh6":a->bank==9?"ship":a->bank==8?"bullet":a->bank==ASSET_ENEMY_ENERGY?"enemy-energy":a->bank==ASSET_NEWSH2?"enemy-newsh2":a->bank==ASSET_NEWSH4?"enemy-newsh4":a->bank==ASSET_NEWSHE?"enemy-newshe":a->bank==ASSET_TALON_BANK?"talon-bank":a->bank==ASSET_EXPLOSION?"explosion-newsh6":"terrain-shapesz";
 if(!game_probe_assets||snprintf(name,sizeof(name),"%s/%s-%d-%d.hda",game_probe_assets,prefix,a->index,wanted)>=(int)sizeof(name)) return false;
 FILE *f=fopen(name,"rb");if(!f)return false;
 Uint8 h[28]={0};bool ok=fread(h,1,sizeof(h),f)==sizeof(h)&&memcmp(h,"HDR1",4)==0;
 uint32_t values[6]={0};
 for(int i=0;i<6;i++) for(int b=0;b<4;b++) values[i]|=(uint32_t)h[4+i*4+b]<<(8*b);
 ok=ok&&values[0]==(uint32_t)(a->bank*10000+a->index)&&values[1]==(uint32_t)wanted&&values[2]==(uint32_t)a->w&&values[3]==(uint32_t)a->h&&
  (int32_t)values[4]==a->anchor_x&&(int32_t)values[5]==a->anchor_y;
 size_t size=(size_t)a->w*a->h*wanted*wanted*4;
 Uint8 *pixels=malloc(size);
 ok=ok&&pixels;
 if(ok) ok=fread(pixels,1,size,f)==size&&fgetc(f)==EOF;
 fclose(f);
 if(!ok) { free(pixels);return false; }
 a->density=wanted;a->rgba=pixels;return true;
}

/* Seven inseparable 8x resources, locked to the frozen generated inventory.
 * Failed preflight keeps both physical coins and their fixed value classic. */
static bool cash25_checked,cash25_valid;
static bool cash25_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||
    game_probe_original_reference||!game_probe_assets)return false;
 if(cash25_checked)return cash25_valid;
 cash25_checked=true;cash25_valid=true;
 static const unsigned int ids[7]={7,8,9,10,11,12,185};
 static const uint64_t rgba_stamps[7]={UINT64_C(0xe952934bb0c309c4),UINT64_C(0x26d922fce156243e),UINT64_C(0x5a804e039a96052b),UINT64_C(0x4ba2888114d88f61),UINT64_C(0x751bda162b36b9a4),UINT64_C(0x999334a6fd5ac8ab),UINT64_C(0xa840af8b65d8ca4d)};
 for(int i=0;i<7;i++) {
  Asset *a=&assets[472+i];
  a->initialized=true;a->bank=i<6?ASSET_CASH25_BODY:ASSET_CASH25_VALUE;a->index=(int)ids[i];
  a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)12*14*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)cash25_valid=false;
 }
 return cash25_valid;
}

/* Independent silver family: a failure never changes the bronze decision. */
static bool cash75_checked,cash75_valid;
static bool cash75_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||
    game_probe_original_reference||!game_probe_assets)return false;
 if(cash75_checked)return cash75_valid;
 cash75_checked=true;cash75_valid=true;
 static const unsigned int ids[7]={20,21,22,23,24,25,223};
 static const uint64_t rgba_stamps[7]={UINT64_C(0xa1726c63d4e7cc68),UINT64_C(0xd828f299359e35b5),UINT64_C(0x718306fc654bdf56),UINT64_C(0x2bf9c217827874ef),UINT64_C(0x419236f6294dd493),UINT64_C(0xc78b7f8d2dc8abd7),UINT64_C(0xb4d84008d761c5b0)};
 for(int i=0;i<7;i++) {
  Asset *a=&assets[479+i];
  a->initialized=true;a->bank=i<6?ASSET_CASH75_BODY:ASSET_CASH75_VALUE;a->index=(int)ids[i];
  a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)12*14*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)cash75_valid=false;
 }
 return cash75_valid;
}

/* Independent copper family: a failure never changes the 25/75 decisions. */
static bool cash50_checked,cash50_valid;
static bool cash50_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||
    game_probe_original_reference||!game_probe_assets)return false;
 if(cash50_checked)return cash50_valid;
 cash50_checked=true;cash50_valid=true;
 static const unsigned int ids[7]={26,27,28,29,30,31,204};
 static const uint64_t rgba_stamps[7]={UINT64_C(0x7c4e0590d0f393cb),UINT64_C(0xe6ef27afa8cd5246),UINT64_C(0x86a0b1489c3c8805),UINT64_C(0xf60da1b7c4a748c6),UINT64_C(0x497abec68554008a),UINT64_C(0xe8421af53de17a52),UINT64_C(0x5d4b2544af04d8a0)};
 for(int i=0;i<7;i++) {
  Asset *a=&assets[486+i];
  a->initialized=true;a->bank=i<6?ASSET_CASH50_BODY:ASSET_CASH50_VALUE;a->index=(int)ids[i];
  a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)12*14*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)cash50_valid=false;
 }
 return cash50_valid;
}

/* Independent five-state gem plus shared fixed100; never replaces moving169. */
static bool gem100_checked,gem100_valid;
static bool gem100_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||
    game_probe_original_reference||!game_probe_assets)return false;
 if(gem100_checked)return gem100_valid;
 gem100_checked=true;gem100_valid=true;
 static const unsigned int ids[6]={32,33,34,35,36,169};
 static const uint64_t rgba_stamps[6]={UINT64_C(0xed343349769eaf60),UINT64_C(0xb875aedd515d1eed),UINT64_C(0x39d72c1f99c01ff5),UINT64_C(0x74620d4bdbd8c517),UINT64_C(0x2cdddc095a32052b),UINT64_C(0x57749151cd61da91)};
 for(int i=0;i<6;i++) {
  Asset *a=&assets[493+i];
  a->initialized=true;a->bank=i<5?ASSET_GEM100_BODY:ASSET_GEM100_VALUE;a->index=(int)ids[i];
  a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)12*14*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)gem100_valid=false;
 }
 return gem100_valid;
}

static bool cash25_surface_ready(SDL_Surface *surface,int x,int y)
{
 return active&&surface&&surface==game_screen&&surface==VGAScreen&&!reject_reason&&
  surface->w==320&&surface->h==200&&surface->pitch==320&&surface->format&&
  surface->format->BitsPerPixel==8&&surface->format->BytesPerPixel==1&&
  x>=0&&x<=308&&y>=-13&&y<=199;
}

void render_mirror_coin25_value_begin(bool fixed)
{cash25_fixed_value=fixed;}

void render_mirror_coin75_value_begin(bool fixed)
{cash75_fixed_value=fixed;}

void render_mirror_coin50_value_begin(bool fixed)
{cash50_fixed_value=fixed;}

void render_mirror_gem100_value_begin(bool fixed)
{gem100_fixed_value=fixed;}

/* Finite accepted newsh6 families only; each quadrant retains its original
 * one-based ID and 12x14 tile call. No shield, smoke or cash bind. */
static int explosion_asset_slot(unsigned int index)
{
 if(index>=122&&index<=133)return 31+(int)index-122;
 if(index>=3&&index<=14)return 43+(int)index-3;
 if(index>=41&&index<=52)return 55+(int)index-41;
 if(index>=22&&index<=33)return 67+(int)index-22;
 if(index>=60&&index<=71)return 79+(int)index-60;
 if(index>=146&&index<=152)return 91+(int)index-146;
 if(index>=192&&index<=203)return 98+(int)index-192;
 if(index>=154&&index<=165)return 110+(int)index-154;
 if(index>=211&&index<=222)return 122+(int)index-211;
 if(index>=173&&index<=184)return 134+(int)index-173;
 if(index>=135&&index<=141)return 146+(int)index-135;
 static const unsigned int shield_ids[22]={229,230,231,232,233,234,235,236,237,248,249,250,252,253,254,255,256,267,268,269,272,275};
 for(int k=0;k<22;k++)if(index==shield_ids[k])return 153+k;
 if(index>=78&&index<=84)return 175+(int)index-78;
 return -1;
}

static Asset *get_asset(Sprite2_array bank,unsigned int index,int layout)
{
 int slot=-1,role=0;
 if(bank.data==spriteSheet9.data&&layout==ENTITY_QUAD&&index>=229&&index<=237&&index%2==1) {slot=(int)(index-229)/2;role=9;}
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==59) {slot=5;role=8;}
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE) {
  static const unsigned int pulse_ids[4]={58,60,62,165};
  for(int i=0;i<4;i++)if(index==pulse_ids[i]){slot=321+i;role=8;break;}
 }
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==103) {slot=325;role=8;}
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE) {
  static const unsigned int guided_ids[4]={19,171,20,21};
  for(int i=0;i<4;i++)if(index==guided_ids[i]){slot=326+i;role=8;break;}
 }
 /* Normal Protron: three static player heads; alternate Christmas art stays original. */
 if(!xmas&&bank.data==spriteSheet8.data&&layout==ENTITY_TILE) {
  static const unsigned int protron_ids[3]={225,244,226};
  for(int i=0;i<3;i++)if(index==protron_ids[i]){slot=469+i;role=8;break;}
 }
 /* Regular Missile Launcher: three static physical player heads. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index>=31&&index<=33) {slot=333+(int)index-31;role=8;}
 /* Charge Cannon static heads only; original bank9 launcher bodies stay separate. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index>=252&&index<=254) {slot=330+(int)index-252;role=8;}
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index>=214&&index<=217) {slot=182+(int)index-214;role=8;}
 if(bank.data==explosionSpriteSheet.data&&layout==ENTITY_TILE) {int explosion_slot=explosion_asset_slot(index);if(explosion_slot>=0){slot=explosion_slot;role=ASSET_EXPLOSION;}}
 if(slot<0||game_probe_density==1||game_probe_missing||(role==ASSET_EXPLOSION&&(!game_probe_assets||game_probe_original_reference))) return NULL;
 Asset *a=&assets[slot];
 if(a->initialized) return a->valid?a:NULL;
 a->initialized=true; a->bank=role;a->index=(int)index;a->w=layout==ENTITY_QUAD?24:12;a->h=layout==ENTITY_QUAD?28:14;
 a->anchor_x=role==9?5:role==8&&index==59?-1:0;a->anchor_y=role==9?7:0;
 if(game_probe_invalid) return NULL;
 if(game_probe_assets) {
  a->valid=read_asset(a,game_probe_density);
  if(!a->valid&&game_probe_density==8) a->valid=read_asset(a,4);
  return a->valid?a:NULL;
 }
 /* Explicit diagnostic fixture: source coverage with deterministic RGB
  * subpixel ramps. Not authored HD art; never quantized to palette indices. */
 Uint8 original[24*28]={0},mask[24*28]={0};
 bool ok=decode_tile(bank,index,original,mask,a->w,0,0);
 if(layout==ENTITY_QUAD) ok=ok&&decode_tile(bank,index+1,original,mask,a->w,12,0)&&decode_tile(bank,index+19,original,mask,a->w,0,14)&&decode_tile(bank,index+20,original,mask,a->w,12,14);
 if(!ok)return NULL;
 a->density=game_probe_density;
 size_t size=(size_t)a->w*a->h*a->density*a->density;
 a->rgba=malloc(size*4);if(!a->rgba)return NULL;
 int d=a->density,pw=a->w*d;
 for(int y=0;y<a->h*d;y++) for(int x=0;x<pw;x++) {
  int n=(y/d)*a->w+x/d;Uint32 color=rgb_palette[original[n]];Uint8 *p=a->rgba+4*(y*pw+x);
  p[0]=(Uint8)MIN(255,((color>>16)&255)+(x%d));
  p[1]=(Uint8)MIN(255,((color>>8)&255)+(y%d));
  p[2]=(Uint8)MIN(255,(color&255)+((x+3*y)%d));p[3]=mask[n];
 }

 a->valid=true;return a;
}

/* Original five frames keep their original HDA/IDs. Only the eight intermediate
 * display frames use the independent ASSET_TALON_BANK namespace. A partial set
 * disables smoothing as a unit, preserving the established five-frame path. */
static Asset *talon_frame(unsigned int visual_index)
{
 for(int i=0;i<5;i++)if(visual_index==(unsigned int)original_visual_indices[i])
  return get_asset(spriteSheet9,229+2*i,ENTITY_QUAD);
 if(visual_index>=13)return NULL;
 Asset *a=&talon_frames[visual_index];
 if(!a->initialized) {
  a->initialized=true;a->bank=ASSET_TALON_BANK;a->index=(int)visual_index;
  a->w=24;a->h=28;a->anchor_x=5;a->anchor_y=7;
  a->valid=read_asset(a,8);
 }
 return a->valid?a:NULL;
}
static bool talon_frames_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||game_probe_original_reference)return false;
 for(unsigned int i=0;i<13;i++) {Asset *a=talon_frame(i);if(!a||a->density!=8)return false;}
 return true;
}

void render_mirror_player_pose(unsigned int pnum,Sprite2_array bank,int base,int index,unsigned int invulnerable)
{
 if(manual_hd_enabled&&!mirror_enabled())return;
 if(pnum<1||pnum>2)return;
 TalonBank *s=&talon_banks[pnum-1];
 bool supported=bank.data==spriteSheet9.data&&base==233&&index>=229&&index<=237&&index%2==1;
 bool available=talon_banking_enabled&&supported&&talon_frames_ready();
 int target=supported?original_visual_indices[(index-229)/2]:-1;
 int reset=0,advanced=0;
 banking_draw_player=0;
 if(!available) {s->valid=false;}
 else {
  if(!s->valid)reset|=1;
  else if(s->last_tick!=mirror_logic_tick&&s->last_tick+1!=mirror_logic_tick)reset|=2;
  if(s->valid&&(s->bank_data!=bank.data||s->base!=base))reset|=4;
  if(s->valid&&invulnerable>s->invulnerable)reset|=8;
  if(reset) {s->visual_index=6;s->valid=true;}
  else if(s->last_tick!=mirror_logic_tick) {
   if(s->visual_index<target)++s->visual_index;
   else if(s->visual_index>target)--s->visual_index;
   advanced=1;
  }
  s->last_tick=mirror_logic_tick;s->bank_data=bank.data;s->base=base;
  s->logical_index=index;s->invulnerable=invulnerable;banking_draw_player=pnum;
 }
 if(game_probe_enabled) {
  if(!banking_trace) {
   banking_trace=fopen("talon-bank-visual.tsv","w");
   if(!banking_trace) {fprintf(stderr,"Unable to create banking display trace\n");exit(2);}
   fprintf(banking_trace,"tick\tlogic_serial\tplayer\tlogical_index\ttarget_visual_index\tvisual_index\treset\tadvanced\tenabled\tavailable\tinvulnerable\n");
  }
  fprintf(banking_trace,"%u\t%llu\t%u\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%u\n",game_probe_tick,(unsigned long long)mirror_logic_tick,pnum,index,target,available?s->visual_index:-1,reset,advanced,talon_banking_enabled,available,invulnerable);
 }
}

/* Original enemy filters use filter | (source_index & 15). Apply that
 * palette ramp to source brightness before compositing, retaining continuous
 * detail and alpha. The original indexed renderer still performs its exact OR
 * writes; filter timing and invulnerability remain entirely engine-controlled. */
static void enemy_filter_rgba(const Uint8 *src,Uint8 filter,Uint8 *rgba)
{
 unsigned int peak=MAX(src[0],MAX(src[1],src[2]));
 unsigned int value=(peak*15*256+127)/255;
 unsigned int lo=value/256,hi=MIN(15,lo+1),fraction=value%256;
 Uint32 a=palette_rgb((Uint8)(filter|lo)),b=palette_rgb((Uint8)(filter|hi));
 for(int c=0;c<3;c++) {
  unsigned int shift=(2-c)*8;
  rgba[c]=((((a>>shift)&255)*(256-fraction)+((b>>shift)&255)*fraction+128)/256);
 }
 rgba[3]=src[3];
}

/* Accepted explosion RGBA keeps the established continuous hue-overwrite/value-average
 * interpretation of the indexed explosion operator. Average HSV value only;
 * keep source channel ratios and use authored alpha solely for coverage. This
 * is not RGB half-opacity. Original indexed writes execute unchanged below. */
static void explosion_asset_blend_rgba(Uint32 dst,const Uint8 *src,Uint8 *rgba)
{
 unsigned int source_peak=MAX(src[0],MAX(src[1],src[2]));
 unsigned int destination_peak=MAX((dst>>16)&255,MAX((dst>>8)&255,dst&255));
 unsigned int next=(source_peak+destination_peak+1)/2;
 for(int c=0;c<3;c++)rgba[c]=source_peak?(src[c]*next+source_peak/2)/source_peak:0;
 rgba[3]=src[3];
}

/* Green smoke alone interpolates the original scenery's brightness term.
 * Snapshot the 12x14 tile plus one logical-pixel halo BEFORE drawing: sampling
 * a live canvas would depend on scan order as this sprite claims HD ownership.
 * 256 marks an HD-owned or outside tap; use the current destination there so
 * an adjacent HD entity is never blurred into the indexed scenery. Authored
 * hue/alpha, prior HD overlaps, and every other effect keep their old operator. */
typedef struct { Uint16 peak[16][14]; } GreenBackground;

static void green_background_snapshot(GreenBackground *background,int x,int y)
{
 int d=game_probe_density;
 for(int iy=0;iy<16;iy++)for(int ix=0;ix<14;ix++) {
  int tx=(x+ix-1)*d+d/2,ty=(y+iy-1)*d+d/2;
  unsigned int peak=256;
  if(tx>=0&&ty>=0&&tx<canvas->w&&ty<canvas->h) {
   int n=ty*canvas->w+tx;
   Uint8 owner=green_first[n]?green_under_owner[n]:hd_owner[n];
   Uint32 color=green_first[n]?green_under[n]:*((Uint32 *)((Uint8 *)canvas->pixels+ty*canvas->pitch)+tx);
   if(owner==0)
   peak=MAX((color>>16)&255,MAX((color>>8)&255,color&255));
  }
  background->peak[iy][ix]=(Uint16)peak;
 }
}

static unsigned int green_background_peak(const GreenBackground *background,int ax,int ay,Uint32 dst)
{
 int d=game_probe_density,den=2*d;
 int wx=2*(ax%d)+1-d,wy=2*(ay%d)+1-d;
 int bx=ax/d+1,by=ay/d+1;
 if(wx<0){--bx;wx+=den;}if(wy<0){--by;wy+=den;}
 unsigned int current=MAX((dst>>16)&255,MAX((dst>>8)&255,dst&255)),sum=0;
 for(int iy=0;iy<2;iy++)for(int ix=0;ix<2;ix++) {
  unsigned int peak=background->peak[by+iy][bx+ix];
  if(peak==256)peak=current;
  sum+=peak*(unsigned int)(ix?wx:den-wx)*(unsigned int)(iy?wy:den-wy);
 }
 return (sum+(unsigned int)(den*den/2))/(unsigned int)(den*den);
}

/* Rebuild from the head-free underlay, never from a previously composited
 * head. Ordered replay preserves exact integer alpha for overlapping heads. */
static Uint32 green_head_composite(int dx,int dy,unsigned int first,Uint32 color)
{
 int d=game_probe_density;
 for(unsigned int i=first-1;i<green_head_count;i++) {
  const GreenHead *h=&green_heads[i];const Asset *a=h->asset;
  int ax=dx-h->x*d,ay=dy-h->y*d;
  if(ax<0||ay<0||ax>=a->w*d||ay>=a->h*d)continue;
  const Uint8 *src=a->rgba+4*((ay*a->density/d)*(a->w*a->density)+ax*a->density/d);
  if(src[3])color=blend_rgba(color,src,src[3]);
 }
 return color;
}

static bool draw_asset_filtered(int x,int y,Asset *a,int style,const SDL_Rect *part,Uint8 filter,const G101Record *material,const PCapRecord *cap,const Forest13Record *forest)
{
 /* Original Talon invulnerability uses half-opacity, not a different sprite.
  * Preserve that effect over the ordered RGBA scene and keep the engine's
  * original indexed blend writes for gameplay/coverage. Other sources and
  * the explicit original-copy diagnostic keep their established fallback. */
 font_before_effect((SDL_Rect){x,y,a->w,a->h});
 if(a->bank==ASSET_EXPLOSION&&a->index>=78&&a->index<=84&&style==MIRROR_BLEND)
  font_before_effect((SDL_Rect){x-1,y-1,14,16});
 bool talon_blend=style==MIRROR_BLEND&&a->bank==9&&a->index>=229&&a->index<=237&&a->index%2==1&&!game_probe_original_reference;
 /* Fixed 25 uses the same continuous hue/value analogue; the exact 0x90
  * indexed shades are retained only by the always-executed original blitter. */
 bool coin25_value_blend=style==MIRROR_BLEND&&a->bank==ASSET_CASH25_VALUE&&a->index==185&&!game_probe_original_reference;
 bool coin75_value_blend=style==MIRROR_BLEND&&a->bank==ASSET_CASH75_VALUE&&a->index==223&&!game_probe_original_reference;
 bool coin50_value_blend=style==MIRROR_BLEND&&a->bank==ASSET_CASH50_VALUE&&a->index==204&&!game_probe_original_reference;
 bool gem100_value_blend=style==MIRROR_BLEND&&a->bank==ASSET_GEM100_VALUE&&a->index==169&&!game_probe_original_reference;
 bool explosion_blend=style==MIRROR_BLEND&&a->bank==ASSET_EXPLOSION&&explosion_asset_slot((unsigned int)a->index)>=0&&!game_probe_original_reference;
 if(style==MIRROR_BLEND&&!talon_blend&&!explosion_blend&&!coin25_value_blend&&!coin75_value_blend&&!coin50_value_blend&&!gem100_value_blend) {
  if(!game_probe_local_blend) {render_mirror_unsupported("hd-invulnerability-palette-blend");return false;}
  /* Preserve the original indexed invulnerability blend, including earlier
   * shadows of this asset. Its own RGBA version is not drawn this frame. */
  for(unsigned int i=0;i<region_count;i++)
   if(regions[i].live&&regions[i].bank==a->bank&&regions[i].index==a->index&&regions[i].style==MIRROR_SHADOW) restore_classic_rect(regions[i].rect);
  SDL_Rect r={x,y,a->w,a->h};restore_classic_rect(r);++local_entities;
  return false;
 }
 bool region_present=false;
 for(unsigned int i=0;i<region_count;i++)if(regions[i].live&&regions[i].bank==a->bank&&regions[i].index==a->index&&regions[i].style==style&&regions[i].rect.x==x&&regions[i].rect.y==y)region_present=true;
 if(!region_present) {
  if(region_count>=sizeof(regions)/sizeof(regions[0])) {render_mirror_unsupported("hd-region-capacity");return false;}
  HdRegion region={{x,y,a->w,a->h},a->bank,a->index,style,true};regions[region_count++]=region;
 }
 bool cloud=cloud_asset(a)&&style==MIRROR_NORMAL&&!filter&&!game_probe_original_reference;
 bool green_blend=explosion_blend&&a->index>=78&&a->index<=84;
 bool green_smoke=a->bank==ASSET_EXPLOSION&&a->index>=78&&a->index<=84&&style!=MIRROR_SHADOW&&!game_probe_original_reference;
 bool green_head=a->bank==8&&a->index>=214&&a->index<=217&&style==MIRROR_NORMAL&&!game_probe_original_reference&&!part&&!filter;
 if(green_head) {
  if(green_head_count>=sizeof(green_heads)/sizeof(green_heads[0])) {render_mirror_unsupported("green-head-layer-capacity");return false;}
  green_heads[green_head_count++]=(GreenHead){a,x,y};
 }
 GreenBackground green_background;
 if(green_blend)green_background_snapshot(&green_background,x,y);
 int d=game_probe_density,ad=a->density,pw=a->w*ad;
 int x0=part?part->x*d:0,y0=part?part->y*d:0,x1=part?(part->x+part->w)*d:a->w*d,y1=part?(part->y+part->h)*d:a->h*d;
 for(int ay=y0;ay<y1;ay++) for(int ax=x0;ax<x1;ax++) {
  int dx=x*d+ax,dy=y*d+ay;if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;
  int n=(ay*ad/d)*pw+(ax*ad/d);const Uint8 *src=a->rgba+n*4;if(!src[3])continue;
  Uint8 world_material[4];if(material){ground101_select(material,src,(unsigned)n,dx,dy,world_material);src=world_material;}
  Uint8 cap_material[4];if(cap){plateau_cap_select(cap,src,(unsigned)n,dx,dy,cap_material);src=cap_material;}
  Uint8 forest_material[4];if(forest){forest13_select(forest,src,(unsigned)n,dx,dy,forest_material);src=forest_material;}
  Uint8 filtered[4];if(filter){enemy_filter_rgba(src,filter,filtered);src=filtered;}
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx;
  int owner_index=dy*canvas->w+dx;
  cloud_owner[owner_index]=cloud?1:0;
  if(green_head&&!green_first[owner_index]) {
   green_first[owner_index]=(Uint16)green_head_count;
   green_under[owner_index]=*p;green_under_owner[owner_index]=hd_owner[owner_index];
  } else if(!green_head&&!green_smoke)green_first[owner_index]=0;
  bool under_head=green_smoke&&green_first[owner_index];
  Uint8 destination_owner=under_head?green_under_owner[owner_index]:hd_owner[owner_index];
  if(under_head)*p=green_under[owner_index];
  if(style==MIRROR_SHADOW) {
   if(hd_owner[owner_index]==1) *p=darken_rgba(*p,src[3]);
   else {
    Uint8 classic_index=((Uint8 *)game_screen->pixels)[(dy/d)*game_screen->pitch+dx/d];
    Uint32 dark=palette_rgb((classic_index&0xf0)|((classic_index&15)/2));
    Uint8 rgba[4]={(dark>>16)&255,(dark>>8)&255,dark&255,255};*p=blend_rgba(*p,rgba,src[3]);
   }
  } else if(explosion_blend||coin25_value_blend||coin75_value_blend||coin50_value_blend||gem100_value_blend) {
   Uint32 background=*p;
   if(green_blend&&destination_owner==0) {
    unsigned int peak=green_background_peak(&green_background,ax,ay,*p);
    background=0xff000000u|peak*0x010101u;
   }
   Uint8 rgba[4];explosion_asset_blend_rgba(background,src,rgba);*p=blend_rgba(*p,rgba,src[3]);
  } else *p=blend_rgba(*p,src,talon_blend?(src[3]+1)/2:src[3]);
  if(under_head) {
   green_under[owner_index]=*p;green_under_owner[owner_index]=1;
   *p=green_head_composite(dx,dy,green_first[owner_index],*p);
  }
  hd_owner[owner_index]=game_probe_original_reference?2:1;selected[(dy/d)*320+dx/d]=1;
 }

 ++draws;suppress=true;suppress_green_smoke=green_smoke;suppress_cloud=cloud;return true;
}

static bool draw_asset(int x,int y,Asset *a,int style,const SDL_Rect *part)
{return draw_asset_filtered(x,y,a,style,part,0,NULL,NULL,NULL);}

/* Only record391's original global bank11 small tile can enter this family. */
static bool cash25_pickup(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int base,int part,int filter,const G101EnemyContext *context)
{
 if(!cash25_surface_ready(surface,x,y)||!bank.data||bank.data!=spriteSheet11.data||
    base<7||base>12||part!=0||!context||context->type!=391||
    context->size!=0||!cash25_family_ready())return false;
 return draw_asset_filtered(x,y,&assets[472+(int)base-7],MIRROR_NORMAL,NULL,(Uint8)filter,NULL,NULL,NULL);
}

/* Only record393's original global bank11 small tile can enter this family. */
static bool cash75_pickup(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int base,int part,int filter,const G101EnemyContext *context)
{
 if(!cash25_surface_ready(surface,x,y)||!bank.data||bank.data!=spriteSheet11.data||
    base<20||base>25||part!=0||!context||context->type!=393||
    context->size!=0||!cash75_family_ready())return false;
 return draw_asset_filtered(x,y,&assets[479+(int)base-20],MIRROR_NORMAL,NULL,(Uint8)filter,NULL,NULL,NULL);
}

/* Only record392's original global bank11 small tile can enter this family. */
static bool cash50_pickup(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int base,int part,int filter,const G101EnemyContext *context)
{
 if(!cash25_surface_ready(surface,x,y)||!bank.data||bank.data!=spriteSheet11.data||
    base<26||base>31||part!=0||!context||context->type!=392||
    context->size!=0||!cash50_family_ready())return false;
 return draw_asset_filtered(x,y,&assets[486+(int)base-26],MIRROR_NORMAL,NULL,(Uint8)filter,NULL,NULL,NULL);
}

/* Only record394's original global bank11 small tile can enter this family. */
static bool gem100_pickup(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int base,int part,int filter,const G101EnemyContext *context)
{
 if(!cash25_surface_ready(surface,x,y)||!bank.data||bank.data!=spriteSheet11.data||
    base<32||base>36||part!=0||!context||context->type!=394||
    context->size!=0||!gem100_family_ready())return false;
 return draw_asset_filtered(x,y,&assets[493+(int)base-32],MIRROR_NORMAL,NULL,(Uint8)filter,NULL,NULL,NULL);
}

bool render_mirror_entity(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int index,int style,int layout)
{
 /* Consume the lease before every early return, including inactive/rejected draws. */
 bool fixed_value=cash25_fixed_value;cash25_fixed_value=false;
 bool fixed_value75=cash75_fixed_value;cash75_fixed_value=false;
 bool fixed_value50=cash50_fixed_value;cash50_fixed_value=false;
 bool fixed_value100=gem100_fixed_value;gem100_fixed_value=false;
 if(fixed_value&&bank.data&&bank.data==explosionSpriteSheet.data&&index==185&&
    layout==ENTITY_TILE&&(style==MIRROR_NORMAL||style==MIRROR_BLEND)) {
  bool mirrored=cash25_surface_ready(surface,x,y)&&cash25_family_ready()&&
   draw_asset(x,y,&assets[478],style,NULL);
  game_probe_scene_draw(ASSET_CASH25_VALUE,index,x,y,0,style,mirrored);
  return mirrored;
 }
 if(fixed_value75&&bank.data&&bank.data==explosionSpriteSheet.data&&index==223&&
    layout==ENTITY_TILE&&(style==MIRROR_NORMAL||style==MIRROR_BLEND)) {
  bool mirrored=cash25_surface_ready(surface,x,y)&&cash75_family_ready()&&
   draw_asset(x,y,&assets[485],style,NULL);
  game_probe_scene_draw(ASSET_CASH75_VALUE,index,x,y,0,style,mirrored);
  return mirrored;
 }
 if(fixed_value50&&bank.data&&bank.data==explosionSpriteSheet.data&&index==204&&
    layout==ENTITY_TILE&&(style==MIRROR_NORMAL||style==MIRROR_BLEND)) {
  bool mirrored=cash25_surface_ready(surface,x,y)&&cash50_family_ready()&&
   draw_asset(x,y,&assets[492],style,NULL);
  game_probe_scene_draw(ASSET_CASH50_VALUE,index,x,y,0,style,mirrored);
  return mirrored;
 }
 if(fixed_value100&&bank.data&&bank.data==explosionSpriteSheet.data&&index==169&&
    layout==ENTITY_TILE&&(style==MIRROR_NORMAL||style==MIRROR_BLEND)) {
  bool mirrored=cash25_surface_ready(surface,x,y)&&gem100_family_ready()&&
   draw_asset(x,y,&assets[498],style,NULL);
  game_probe_scene_draw(ASSET_GEM100_VALUE,index,x,y,0,style,mirrored);
  return mirrored;
 }
 if(!active||surface!=game_screen||reject_reason)return false;
 /* Protron shadows retain their original indexed silhouettes and origin. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&(index==225||index==244||index==226)&&style==MIRROR_SHADOW)return false;
 /* Regular Missile Launcher shadows retain their original indexed silhouettes and origin. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index>=31&&index<=33&&style==MIRROR_SHADOW)return false;
 /* Charge Cannon shadows retain their original indexed silhouettes and origin. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index>=252&&index<=254&&style==MIRROR_SHADOW)return false;
 /* Keep the green214..217 shadows on their original indexed path and origin. */
 if(bank.data==spriteSheet8.data&&index>=214&&index<=217&&style==MIRROR_SHADOW)return false;
 Asset *a=get_asset(bank,index,layout);
 if(a&&a->bank==9&&banking_draw_player) {
  TalonBank *s=&talon_banks[banking_draw_player-1];
  if(s->valid&&s->last_tick==mirror_logic_tick&&s->logical_index==(int)index) {
   Asset *frame=talon_frame((unsigned int)s->visual_index);
   if(frame) {Asset display=*a;display.rgba=frame->rgba;display.density=frame->density;return draw_asset(x,y,&display,style,NULL);}
  }
 }
 return a?draw_asset(x,y,a,style,NULL):false;
}

/* Seven original static directions, including shared enemy58 uses. This
 * resource role is separate from player pulse58 and the older enemy orbs.
 * Frozen inward alpha is composited by the existing ordered normal operator. */
static int enemy_energy_slot(unsigned int index)
{
 static const unsigned int ids[7]={77,58,182,163,1,183,164};
 for(int i=0;i<7;i++)if(index==ids[i])return 462+i;
 return -1;
}

static bool enemy_energy_checked,enemy_energy_valid;
static bool enemy_energy_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||
    game_probe_original_reference||!game_probe_assets)return false;
 if(enemy_energy_checked)return enemy_energy_valid;
 enemy_energy_checked=true;enemy_energy_valid=true;
 static const unsigned int ids[7]={77,58,182,163,1,183,164};
 static const uint64_t rgba_stamps[7]={UINT64_C(0xe7ad74098293fa74),UINT64_C(0x6bde72d8a3fb5321),UINT64_C(0xdad683e2104c364c),UINT64_C(0xda40a3f50079bbb7),UINT64_C(0x17a96f454b155ee6),UINT64_C(0x46a1a574bc4971cf),UINT64_C(0x03388802eea7f5a4)};
 for(int i=0;i<7;i++) {
  Asset *a=&assets[462+i];
  a->initialized=true;a->bank=ASSET_ENEMY_ENERGY;a->index=(int)ids[i];
  a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)12*14*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)enemy_energy_valid=false;
 }
 return enemy_energy_valid;
}

/* Enemy-only bindings: the indexed original still executes in the wrapper. */
bool render_mirror_enemy_shot(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int index)
{
 int energy_slot=enemy_energy_slot(index);
 if(energy_slot>=0) {
  if(!active||!surface||surface!=game_screen||surface!=VGAScreen||reject_reason||
     !bank.data||bank.data!=spriteSheet8.data||
     surface->w!=320||surface->h!=200||surface->pitch!=320||!surface->format||
     surface->format->BitsPerPixel!=8||surface->format->BytesPerPixel!=1||
     x<0||x>308||y<-13||y>199)return false;
  /* Original RLE clips linear addresses. Decline physical-row wrapping,
   * retain partial vertical clips, and never rotate art to shot velocity. */
  if(!enemy_energy_family_ready())return false;
  return draw_asset(x,y,&assets[energy_slot],MIRROR_NORMAL,NULL);
 }
 if(!active||surface!=game_screen||reject_reason||bank.data!=spriteSheet8.data||(index!=112&&index!=113)||game_probe_density==1||game_probe_missing||game_probe_invalid||!game_probe_assets)return false;
 Asset *a=&assets[218+(int)index-112];
 if(!a->initialized) {
  a->initialized=true;a->bank=8;a->index=(int)index;a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;
  a->valid=read_asset(a,game_probe_density);
  if(!a->valid&&game_probe_density==8)a->valid=read_asset(a,4);
 }
 return a->valid?draw_asset(x,y,a,MIRROR_NORMAL,NULL):false;
}

static Asset *scene_asset(int slot,int role,int index,int anchor_x,int anchor_y)
{
 if(game_probe_density==1||game_probe_missing||!game_probe_assets)return NULL;
 Asset *a=&assets[slot];
 if(a->initialized)return a->valid?a:NULL;
 a->initialized=true;a->bank=role;a->index=index;a->w=24;a->h=28;a->anchor_x=anchor_x;a->anchor_y=anchor_y;
 if(!game_probe_invalid) {
  a->valid=read_asset(a,game_probe_density);
  if(!a->valid&&game_probe_density==8)a->valid=read_asset(a,4);
 }
 return a->valid?a:NULL;
}

/* One coordinated selected-pack family. Preflight is shared by both routes,
 * completed before any member draw, and cached for the existing Asset lifetime.
 * Missing/corrupt/nonopaque members disable all eight, never unrelated art.
 * This family is authored only at8x: no mixed-density or partial-scene fallback. */
static bool linked31_checked,linked31_valid;
static bool linked31_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    (game_probe_scene_assets&3)!=3)return false;
 if(linked31_checked)return linked31_valid;
 linked31_checked=true;linked31_valid=true;
 static const unsigned int ids[8]={161,162,171,172,15,17,53,55};
 for(int i=0;i<8;i++) {
  Asset *a=&assets[374+i];
  a->initialized=true;a->bank=i<4?ASSET_SHAPESZ:ASSET_NEWSH2;a->index=(int)ids[i];
  a->w=24;a->h=28;a->anchor_x=i<4?0:6;a->anchor_y=i<4?0:7;
  a->valid=read_asset(a,8);
  if(a->valid)for(size_t p=3;p<(size_t)24*28*8*8*4;p+=4)if(a->rgba[p]!=255){a->valid=false;break;}
  if(!a->valid)linked31_valid=false;
 }
 return linked31_valid;
}

/* Approved newsh4 long-seven family, selected-pack and 8x only.
 * Preflight every member before the first replacement. The complete RGBA
 * integrity stamps also pin the exact original alpha support. Failure stays
 * coherent for this Asset-cache lifetime; unrelated namespaces are untouched. */
static bool newsh4_long7_checked,newsh4_long7_valid;
static bool newsh4_long7_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    !(game_probe_scene_assets&1))return false;
 if(newsh4_long7_checked)return newsh4_long7_valid;
 newsh4_long7_checked=true;newsh4_long7_valid=true;
 static const unsigned int ids[7]={153,155,157,159,191,193,195};
 static const uint64_t rgba_stamps[7]={UINT64_C(0x467dfe0e38d4d6af),UINT64_C(0xc94f12efbf56fa95),UINT64_C(0xe029beb9289c7f9f),UINT64_C(0x027743ab3ea4c742),UINT64_C(0xa9ff3f5e5ff49200),UINT64_C(0x5cd069e1cf31bb95),UINT64_C(0x568006eacc4be79e)};
 for(int i=0;i<7;i++) {
  Asset *a=&assets[382+i];
  a->initialized=true;a->bank=ASSET_NEWSH4;a->index=(int)ids[i];
  a->w=24;a->h=28;a->anchor_x=6;a->anchor_y=7;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)24*28*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)newsh4_long7_valid=false;
 }
 return newsh4_long7_valid;
}

/* Approved opposite newsh4 seven-part family, selected-pack and 8x only.
 * Preflight every member before the first replacement. The complete RGBA
 * integrity stamps also pin the exact original alpha support. Failure stays
 * coherent for this Asset-cache lifetime; unrelated namespaces are untouched. */
static bool newsh4_opposite7_checked,newsh4_opposite7_valid;
static bool newsh4_opposite7_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    !(game_probe_scene_assets&1))return false;
 if(newsh4_opposite7_checked)return newsh4_opposite7_valid;
 newsh4_opposite7_checked=true;newsh4_opposite7_valid=true;
 static const unsigned int ids[7]={231,233,235,267,269,271,273};
 static const uint64_t rgba_stamps[7]={UINT64_C(0x7772ad387ba647e1),UINT64_C(0x46ec9cc03cb2a64d),UINT64_C(0x6cf67a53c0c3c617),UINT64_C(0x3b6f6b5a0675dfab),UINT64_C(0x4e35f12d37d40aa1),UINT64_C(0x4fb033fc9820579f),UINT64_C(0x638ffb21f4fcc1dc)};
 for(int i=0;i<7;i++) {
  Asset *a=&assets[389+i];
  a->initialized=true;a->bank=ASSET_NEWSH4;a->index=(int)ids[i];
  a->w=24;a->h=28;a->anchor_x=6;a->anchor_y=7;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)24*28*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)newsh4_opposite7_valid=false;
 }
 return newsh4_opposite7_valid;
}

/* Approved type15 eight-heading bank1 family, selected-pack and 8x only.
 * Preflight every member before the first replacement. The complete RGBA
 * integrity stamps pin approved fractional contours and apertures. Failure stays
 * coherent for this Asset-cache lifetime; unrelated namespaces are untouched. */
static bool type15_eightheading_checked,type15_eightheading_valid;
static bool type15_eightheading_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    !(game_probe_scene_assets&1))return false;
 if(type15_eightheading_checked)return type15_eightheading_valid;
 type15_eightheading_checked=true;type15_eightheading_valid=true;
 static const unsigned int ids[8]={39,41,43,45,91,93,129,131};
 static const uint64_t rgba_stamps[8]={UINT64_C(0xcc3d8be70ed2e620),UINT64_C(0x80d5e7bb507fe084),UINT64_C(0x3228caecc8f7abe8),UINT64_C(0x33f828b2c95baa5a),UINT64_C(0x452516abee3a1d95),UINT64_C(0xc8296a713b1af965),UINT64_C(0x1f937a94539eb9cb),UINT64_C(0xb01b2fcfaa46aaf0)};
 for(int i=0;i<8;i++) {
  Asset *a=&assets[396+i];
  a->initialized=true;a->bank=ASSET_NEWSH2;a->index=(int)ids[i];
  a->w=24;a->h=28;a->anchor_x=6;a->anchor_y=7;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)24*28*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)type15_eightheading_valid=false;
 }
 return type15_eightheading_valid;
}

/* Approved late spike six-member bank1 family, selected-pack and 8x only.
 * Preflight every member before the first replacement. The complete RGBA
 * integrity stamps also pin the exact original alpha support. Failure stays
 * coherent for this Asset-cache lifetime; unrelated namespaces are untouched. */
static bool late_spike_checked,late_spike_valid;
static bool late_spike_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    !(game_probe_scene_assets&1))return false;
 if(late_spike_checked)return late_spike_valid;
 late_spike_checked=true;late_spike_valid=true;
 static const unsigned int ids[6]={1,3,5,7,9,11};
 static const uint64_t rgba_stamps[6]={UINT64_C(0xa200c71744dfb67d),UINT64_C(0x16563f2a13fd9d20),UINT64_C(0xa61fd6d4144d8607),UINT64_C(0x41e6f49abb0f073e),UINT64_C(0x7431a5a306d38062),UINT64_C(0x57fb1ddb756b7bd3)};
 for(int i=0;i<6;i++) {
  Asset *a=&assets[404+i];
  a->initialized=true;a->bank=ASSET_NEWSH2;a->index=(int)ids[i];
  a->w=24;a->h=28;a->anchor_x=6;a->anchor_y=7;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)24*28*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)late_spike_valid=false;
 }
 return late_spike_valid;
}

/* Approved newsh4 entry six-member bank2 family, selected-pack and 8x only.
 * Preflight every member before the first replacement. The complete RGBA
 * integrity stamps also pin the exact original alpha support. Failure stays
 * coherent for this Asset-cache lifetime; unrelated namespaces are untouched. */
static bool newsh4_entry6_checked,newsh4_entry6_valid;
static bool newsh4_entry6_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    !(game_probe_scene_assets&1))return false;
 if(newsh4_entry6_checked)return newsh4_entry6_valid;
 newsh4_entry6_checked=true;newsh4_entry6_valid=true;
 static const unsigned int ids[6]={81,83,85,119,121,123};
 static const uint64_t rgba_stamps[6]={UINT64_C(0xd568531aec92422c),UINT64_C(0xbf0fa10dfdd98241),UINT64_C(0x095506cac33b7e8e),UINT64_C(0x568183ac9f82133c),UINT64_C(0xbd0f65394c14826d),UINT64_C(0xd3f58ab88accaf9d)};
 for(int i=0;i<6;i++) {
  Asset *a=&assets[410+i];
  a->initialized=true;a->bank=ASSET_NEWSH4;a->index=(int)ids[i];
  a->w=24;a->h=28;a->anchor_x=6;a->anchor_y=7;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)24*28*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)newsh4_entry6_valid=false;
 }
 return newsh4_entry6_valid;
}

/* Approved type3 six-member small bank1 family, selected-pack and 8x only.
 * All six exact 12x14 resources are validated before the first replacement.
 * Cache/failure lifetime matches the existing startup-selected Asset cache;
 * full RGBA stamps pin the frozen art and each original binary alpha mask. */
static bool type3_small_checked,type3_small_valid;
static bool type3_small_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    !(game_probe_scene_assets&1))return false;
 if(type3_small_checked)return type3_small_valid;
 type3_small_checked=true;type3_small_valid=true;
 static const unsigned int ids[6]={171,190,209,228,247,266};
 static const uint64_t rgba_stamps[6]={UINT64_C(0xe50b6977b5066df5),UINT64_C(0xb9a24984f9b4c702),UINT64_C(0xf68843a48851eb04),UINT64_C(0x218f933c0d4477ac),UINT64_C(0xc321dd3cedba226d),UINT64_C(0x890da522ac93848e)};
 for(int i=0;i<6;i++) {
  Asset *a=&assets[416+i];
  a->initialized=true;a->bank=ASSET_NEWSH2;a->index=(int)ids[i];
  a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)12*14*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)type3_small_valid=false;
 }
 return type3_small_valid;
}

/* Approved whole-boss bank2 family: forty nonempty complete24x28 images.
 * Empty aftermath bases238/278/282 stay original no-ops, never missing art.
 * The V2 stamps pin inward-only authored alpha and byte-exact V1 RGB.
 * Preflight all forty before any body replacement; failure stays local to this
 * selected-pack Asset lifetime. No mixed-density or partial-family fallback. */
static bool boss_whole_checked,boss_whole_valid;
static bool boss_whole_family_ready(void)
{
 if(game_probe_density!=8||game_probe_missing||game_probe_invalid||!game_probe_assets||
    !(game_probe_scene_assets&1))return false;
 if(boss_whole_checked)return boss_whole_valid;
 boss_whole_checked=true;boss_whole_valid=true;
 static const unsigned int ids[40]={1,3,5,7,10,12,14,16,18,39,41,43,45,48,50,54,56,86,88,90,92,94,124,126,128,130,132,162,164,168,170,200,202,206,208,240,242,244,246,280};
 static const uint64_t rgba_stamps[40]={UINT64_C(0x79d01a5867512fb7),UINT64_C(0x451ea77629c45e55),UINT64_C(0x74dcbe3f4e30da68),UINT64_C(0x7f796d2a95aedc49),UINT64_C(0xc7bea79e9d18e340),UINT64_C(0x3c44af08fe16b732),UINT64_C(0x94cf458d1232f3f6),UINT64_C(0xc19d47efd48d3faa),UINT64_C(0x318712cca2a454d3),UINT64_C(0xadf0fba4f703b1e8),UINT64_C(0x657f79c4e078c171),UINT64_C(0x4a8179a13feefaec),UINT64_C(0x1c8b5aae9167fd54),UINT64_C(0x9defb5b84aaafb50),UINT64_C(0x22f3a2dc3d3f22c6),UINT64_C(0x30de8d9f19b77745),UINT64_C(0xc9d44987407e7795),UINT64_C(0xf68095e34e94f11d),UINT64_C(0x966df86cc6ad9a4e),UINT64_C(0x54661ebe8181d394),UINT64_C(0xecb6106aa424eed9),UINT64_C(0x233840a2896f6aec),UINT64_C(0xee73d5b71b292076),UINT64_C(0xc7e3b17d9b721a67),UINT64_C(0x1b322f4cc4116f5f),UINT64_C(0x441025d8061eb1e1),UINT64_C(0xd828fffbc7efb661),UINT64_C(0xe11733af132999f8),UINT64_C(0x4600faa86b29a5a1),UINT64_C(0x46c6ce3f51e09c09),UINT64_C(0x636a1907c56f7cc4),UINT64_C(0x512ff03eed10ff0e),UINT64_C(0x860de7c816f3f638),UINT64_C(0x49b4a1fb8f930ef0),UINT64_C(0x0a7b91629f0ac91c),UINT64_C(0x0db71a0453fa65ed),UINT64_C(0x23c219a3afe96982),UINT64_C(0x2a4b2ec5dfc96562),UINT64_C(0xd9dafd092794900a),UINT64_C(0x1b322f4cc4116f5f)};
 for(int i=0;i<40;i++) {
  Asset *a=&assets[422+i];
  a->initialized=true;a->bank=ASSET_NEWSH4;a->index=(int)ids[i];
  a->w=24;a->h=28;a->anchor_x=6;a->anchor_y=7;
  a->valid=read_asset(a,8);
  if(a->valid) {
   uint64_t stamp=UINT64_C(0xcbf29ce484222325);
   for(size_t p=0;p<(size_t)24*28*8*8*4;p++){stamp^=a->rgba[p];stamp*=UINT64_C(0x100000001b3);}
   if(stamp!=rgba_stamps[i])a->valid=false;
  }
  if(!a->valid)boss_whole_valid=false;
 }
 return boss_whole_valid;
}

/* Record1 shares center source tiles. Scope the new body by original record
 * and its finite visible bases, not raw tile identity, scoreitem or damage.
 * Independent movement, initial negative-dani and avail2 wrecks stay eligible. */
static bool boss_whole_base_allowed(const G101EnemyContext *context,unsigned int base)
{
 if(!context||context->size!=1)return false;
 switch(context->type) {
  case 46:return base==10||base==162;
  case 47:return base==12||base==164;
  case 48:return base==14;
  case 49:return base==16||base==168;
  case 50:return base==18||base==170;
  case 51:return base==48||base==200;
  case 52:return base==50||base==202;
  case 53:return base==1||base==3||base==5||base==7||base==39||base==41||base==43||base==45;
  case 54:return base==54||base==206;
  case 55:return base==56||base==208;
  case 56:return base==86;
  case 57:return base==88||base==240;
  case 58:return base==90||base==242;
  case 59:return base==92||base==244;
  case 60:return base==94||base==246;
  case 61:return base==124;
  case 62:return base==126;
  case 63:return base==128||base==280;
  case 64:return base==130;
  case 65:return base==132;
  default:return false;
 }
}

bool render_mirror_enemy_tile(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int base,int part,int filter,const G101EnemyContext *material_context)
{
 if(!active||surface!=game_screen||reject_reason||!(game_probe_scene_assets&1))return false;
 if(bank.data&&bank.data==spriteSheet11.data) {
  if(base>=20&&base<=25) {
   bool mirrored=cash75_pickup(surface,x,y,bank,base,part,filter,material_context);
   game_probe_scene_draw(ASSET_CASH75_BODY,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
   return mirrored;
  }
  if(base>=26&&base<=31) {
   bool mirrored=cash50_pickup(surface,x,y,bank,base,part,filter,material_context);
   game_probe_scene_draw(ASSET_CASH50_BODY,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
   return mirrored;
  }
  if(base>=32&&base<=36) {
   bool mirrored=gem100_pickup(surface,x,y,bank,base,part,filter,material_context);
   game_probe_scene_draw(ASSET_GEM100_BODY,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
   return mirrored;
  }
  bool mirrored=cash25_pickup(surface,x,y,bank,base,part,filter,material_context);
  if(base>=7&&base<=12)game_probe_scene_draw(ASSET_CASH25_BODY,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);
  return mirrored;
 }
 int role=0;
 for(int i=0;i<4;i++)if(bank.data&&bank.data==enemySpriteSheets[i].data) {
  if(enemySpriteSheetIds[i]==1)role=ASSET_NEWSH2;
  else if(enemySpriteSheetIds[i]==9)role=ASSET_NEWSHE;
  else if(enemySpriteSheetIds[i]==2)role=ASSET_NEWSH4;
 }
 /* Type3/type16 use one small tile at the original top-left, not a composite.
  * The original caller owns the held-twice cycle, filter and indexed blit. */
 if(role==ASSET_NEWSH2) {
  static const unsigned int type3_small_ids[6]={171,190,209,228,247,266};
  for(int i=0;i<6;i++)if(base==type3_small_ids[i]) {
   if(part!=0||!material_context||material_context->size!=0)return false;
   /* Preserve physical-row RLE wrapping as classic. The original target is
    * VGAScreen=game_screen; normal playfield-edge and partial vertical clips
    * remain supported. Direct bounds checks avoid coordinate overflow. */
   if(!surface||surface->w!=320||surface->h!=200||surface->pitch!=320||
      !surface->format||surface->format->BitsPerPixel!=8||
      surface->format->BytesPerPixel!=1||x<0||x>308||y<-13||y>199)return false;
   if(!type3_small_family_ready())return false;
   bool mirrored=draw_asset_filtered(x,y,&assets[416+i],MIRROR_NORMAL,NULL,(Uint8)filter,NULL,NULL,NULL);
   game_probe_scene_draw(role,base,x,y,0,filter?3:MIRROR_NORMAL,mirrored);
   return mirrored;
  }
 }
 /* Existing ground201..209 and rotor210..217 remain unchanged. */
 int slot=base==169?303:base==207?304:base==245?305:base==273?306:base==275?307:base==277?308:base==279?309:base==281?310:base==283?311:base==153?269:base==155?270:base==157?271:base==49?265:base==51?266:base==89?267:base==127?268:base==267?243:base==269?244:base==271?245:base==81?231:base==83?232:base==119?233:base==121?234:(base>=229&&base<=243&&base%2==1)?210+(int)(base-229)/2:base==77?6:base==79?7:base==115?8:base==117?9:base==85?15:base==87?16:base==123?17:base==125?18:(base>=191&&base<=205&&base%2==1)?23+(int)(base-191)/2:-1;
 /* Type4: five complete24x28 newsh2 composites, never individual cells.
  * Keep the original four ordered quadrant calls, cycle, filters and death. */
 if(role==ASSET_NEWSH2) {
  static const unsigned int type4_ids[5]={159,161,163,165,167};
  for(int i=0;i<5;i++)if(base==type4_ids[i]){slot=369+i;break;}
 }
 /* Type15 eight event-selected complete composites, never a rotation cycle.
  * Retain each original quadrant call, anchor, clipping, filter and lifecycle. */
 if(role==ASSET_NEWSH2) {
  static const unsigned int type15_ids[8]={39,41,43,45,91,93,129,131};
  for(int i=0;i<8;i++)if(base==type15_ids[i]) {
   if(!type15_eightheading_family_ready())return false;
   slot=396+i;break;
  }
 }
 /* Late spike six complete composites form four independent moving rows.
  * Preserve each original quadrant, alpha, filter, anchor and update order. */
 if(role==ASSET_NEWSH2) {
  static const unsigned int late_spike_ids[6]={1,3,5,7,9,11};
  for(int i=0;i<6;i++)if(base==late_spike_ids[i]) {
   if(!late_spike_family_ready())return false;
   /* The original 12px RLE call clips linear addresses, so crossing a
    * physical row can wrap writes onto another scanline. Keep that entire
    * quadrant classic; an adjacent in-row quadrant may still use HD.
    * The mirror uses a fixed indexed 320x200 layout. Fail closed for other
    * layouts and compare x directly, without overflowing x+12 arithmetic. */
   if(surface->w!=320||surface->h!=200||surface->pitch!=320||
      !surface->format||surface->format->BitsPerPixel!=8||
      surface->format->BytesPerPixel!=1||x<0||x>308)return false;
   slot=404+i;break;
  }
 }
 /* Linked31 four complete newsh2 composites; original coordinates already
  * include the one-logical-pixel actor/terrain offset. Never add an offset. */
 if(role==ASSET_NEWSH2) {
  static const unsigned int linked31_ids[4]={15,17,53,55};
  for(int i=0;i<4;i++)if(base==linked31_ids[i]) {
   if(!linked31_family_ready())return false;
   slot=378+i;break;
  }
 }
 /* Explicit bank2 left-family allowlist; matching numbers never borrow
  * newsh2 slots. The distinct opposite family is handled separately below. */
 if(role==ASSET_NEWSH4) {
  static const unsigned int newsh4_long7_ids[7]={153,155,157,159,191,193,195};
  slot=-1;
  for(int i=0;i<7;i++)if(base==newsh4_long7_ids[i]) {
   if(!newsh4_long7_family_ready())return false;
   slot=382+i;break;
  }
  /* Distinct opposite/link2 composites have their own coherent fallback.
   * Base231 remains a full composite even though its first quadrant is empty. */
  static const unsigned int newsh4_opposite7_ids[7]={231,233,235,267,269,271,273};
  for(int i=0;i<7;i++)if(base==newsh4_opposite7_ids[i]) {
   if(!newsh4_opposite7_family_ready())return false;
   slot=389+i;break;
  }
  /* Whole boss remains twenty original actors with four ordered calls each.
   * The three empty aftermath bases deliberately fall through to classic. */
  static const unsigned int boss_whole_ids[40]={1,3,5,7,10,12,14,16,18,39,41,43,45,48,50,54,56,86,88,90,92,94,124,126,128,130,132,162,164,168,170,200,202,206,208,240,242,244,246,280};
  for(int i=0;i<40;i++)if(base==boss_whole_ids[i]) {
   if(!boss_whole_base_allowed(material_context,base))return false;
   /* Preserve original linear-address RLE physical-row wrapping. Partial
    * vertical clips keep their original calls; unsupported geometry declines
    * before any coordinate subtraction, scaling or resource access. */
   if(!surface||surface->w!=320||surface->h!=200||surface->pitch!=320||
      !surface->format||surface->format->BitsPerPixel!=8||
      surface->format->BytesPerPixel!=1||x<0||x>308||y<-13||y>199)return false;
   if(part!=0&&part!=1&&part!=19&&part!=20)return false;
   if(!boss_whole_family_ready())return false;
   slot=422+i;break;
  }
  /* Entry craft remains six independent source actors with ordered overlap.
   * Only these full composites are bound; raw cells and boss86/124 stay classic. */
  static const unsigned int newsh4_entry6_ids[6]={81,83,85,119,121,123};
  for(int i=0;i<6;i++)if(base==newsh4_entry6_ids[i]) {
   if(!newsh4_entry6_family_ready())return false;
   /* Preserve original linear-address RLE row wrapping by declining HD for
    * any quadrant crossing a physical row or an unsupported indexed layout.
    * Wholly offscreen y calls also stay classic before subtraction/scaling;
    * the accepted -13..199 range retains every partial 14px vertical clip. */
   if(surface->w!=320||surface->h!=200||surface->pitch!=320||
      !surface->format||surface->format->BitsPerPixel!=8||
      surface->format->BytesPerPixel!=1||x<0||x>308||y<-13||y>199)return false;
   slot=410+i;break;
  }
 }
 if(role==ASSET_NEWSHE) {
  const unsigned int ids[12]={1,3,5,39,41,43,7,9,11,45,47,49};
  slot=-1;for(int i=0;i<12;i++)if(base==ids[i])slot=253+i;
 }
 if(!role||slot<0)return false;
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 if(part!=0&&part!=1&&part!=19&&part!=20)return false;
 Asset *a=scene_asset(slot,role,(int)base,6,7);bool mirrored=false;
 if(a) {
  SDL_Rect quadrant={px,py,12,14};
  const G101Record *material=a->density==8&&ground101_enemy_eligible(material_context,(unsigned)role,base)?ground101_record((unsigned)role,base):NULL;
  ground101_actor_trace(game_probe_tick,material_context,(unsigned)role,base,part,filter,x,y,material!=NULL);
  ground101_note_draw(material,true);
  mirrored=draw_asset_filtered(x-px,y-py,a,MIRROR_NORMAL,&quadrant,(Uint8)filter,material,NULL,NULL);
 }
 game_probe_scene_draw(role,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);return mirrored;
}

void render_mirror_map_begin(char shape_file)
{ground101_frame_reset();terrain_file=shape_file=='Z'?'z':shape_file;terrain_source_count=0;forest_registry_ok=true;render_mirror_reset_banking();}
/* Only shapesZ layer2 cloud IDs; no renderer/filter or game-state changes. */
static int cloud_terrain_slot(unsigned int id)
{
 if(id>=41&&id<=45)return 186+(int)id-41;
 if(id>=51&&id<=55)return 191+(int)id-51;
 if(id>=61&&id<=65)return 196+(int)id-61;
 return -1;
}
/* Only the nine reviewed shapesZ layer1 ground IDs; no implicit ranges. */
static int ground_terrain_slot(unsigned int id)
{
 static const unsigned int ids[9]={99,100,106,107,109,110,118,119,120};
 for(int i=0;i<9;i++)if(id==ids[i])return 201+i;
 return -1;
}
/* Only the four reviewed shapesZ layer1 plateau tiles; no implicit ranges. */
static int plateau_terrain_slot(unsigned int id)
{
 static const unsigned int ids[4]={96,97,98,108};
 for(int i=0;i<4;i++)if(id==ids[i])return 227+i;
 return -1;
}
/* Static physical terrain underlay, distinct from the enemy overlay. */
static int underlay_terrain_slot(unsigned int id)
{
 static const unsigned int ids[4]={323,324,333,334};
 for(int i=0;i<4;i++)if(id==ids[i])return 237+i;
 return -1;
}
/* Nine new roads complete the family; four accepted road IDs stay unchanged. */
static int road_terrain_slot(unsigned int id)
{
 static const unsigned int ids[9]={36,39,40,46,48,56,58,38,47};
 static const int slots[9]={220,221,222,223,224,225,226,235,236};
 for(int i=0;i<9;i++)if(id==ids[i])return slots[i];
 return -1;
}
/* Only the two reviewed shapesZ layer1 tiles with original interior holes. */
static int terrain_holes_slot(unsigned int id)
{
 static const unsigned int ids[3]={111,114,113};
 static const int slots[3]={241,242,246};
 for(int i=0;i<3;i++)if(id==ids[i])return slots[i];
 return -1;
}
/* Complete reviewed stone foundation; separate from original newshE objects. */
static int stone_foundation_slot(unsigned int id)
{
 static const unsigned int ids[6]={341,342,343,351,352,353};
 for(int i=0;i<6;i++)if(id==ids[i])return 247+i;
 return -1;
}
/* Only the reviewed shapesZ layer3 gray island family. Slots269-271
 * remain reserved for the separate three-design type40 enemy family. */
static int layer3_gray_slot(unsigned int id)
{
 static const unsigned int ids[18]={121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154};
 for(int i=0;i<18;i++)if(id==ids[i])return 272+i;
 return -1;
}
/* Finite purple foundation family, distinct from its independent enemy overlay. */
static int layer3_purple_slot(unsigned int id)
{
 static const unsigned int ids[13]={150,156,157,158,159,160,166,168,169,170,176,177,178};
 for(int i=0;i<13;i++)if(id==ids[i])return 290+i;
 return -1;
}
/* Finite low-grass/sand Layer1 family. */
static int grass_sand_slot(unsigned int id)
{
 static const unsigned int ids[9]={66,67,69,76,78,79,80,89,90};
 for(int i=0;i<9;i++)if(id==ids[i])return 312+i;
 return -1;
}
/* Exactly the reviewed forest family; no implicit bank-wide replacement. */
static int forest_terrain_slot(unsigned int id)
{
 static const unsigned int ids[13]={211,212,213,215,221,222,223,224,225,231,232,233,234};
 for(int i=0;i<13;i++)if(id==ids[i])return 336+i;
 return -1;
}
/* Exactly ten reviewed Layer3 circuit/deck designs; source191 stays original. */
static int layer3_circuit_slot(unsigned int id)
{
 static const unsigned int ids[10]={181,182,184,185,192,193,194,195,201,202};
 for(int i=0;i<10;i++)if(id==ids[i])return 349+i;
 return -1;
}
/* Finite right/left mechanical assemblies and two static round inserts. */
static int layer3_mechanical_slot(unsigned int id)
{
 static const unsigned int ids[10]={188,189,198,199,186,187,196,197,190,200};
 for(int i=0;i<10;i++)if(id==ids[i])return 359+i;
 return -1;
}
/* Static linked31 remnants, strictly shapesZ Layer3 pointer registration. */
static int layer3_linked31_slot(unsigned int id)
{
 static const unsigned int ids[4]={161,162,171,172};
 for(int i=0;i<4;i++)if(id==ids[i])return 374+i;
 return -1;
}
void render_mirror_bind_terrain(unsigned int layer,unsigned int id,const Uint8 *data)
{
 if(terrain_file=='z'&&((layer==1&&(forest_terrain_slot(id)>=0||grass_sand_slot(id)>=0||stone_foundation_slot(id)>=0||terrain_holes_slot(id)>=0||road_terrain_slot(id)>=0||underlay_terrain_slot(id)>=0||plateau_terrain_slot(id)>=0||ground_terrain_slot(id)>=0||id==101||id==37||id==57||id==49||id==50||id==321||id==322||id==331||id==332))||(layer==2&&cloud_terrain_slot(id)>=0)||(layer==3&&(layer3_gray_slot(id)>=0||layer3_purple_slot(id)>=0||layer3_circuit_slot(id)>=0||layer3_mechanical_slot(id)>=0||layer3_linked31_slot(id)>=0)))&&terrain_source_count<199) {
  terrain_sources[terrain_source_count].data=data;
  terrain_sources[terrain_source_count++].id=id;
 }
 /* Validate each actually attempted forest pointer, including duplicate-ID
  * loader slots. Other maps need not contain all thirteen numeric IDs. */
 if(terrain_file=='z'&&layer==1&&forest_terrain_slot(id)>=0) {
  bool found=false;
  for(unsigned k=0;k<terrain_source_count;k++)if(terrain_sources[k].data==data) {
   found=data&&terrain_sources[k].id==id;break;
  }
  if(!found)forest_registry_ok=false;
 }
}
/* Selected-pack lookup retains the existing HDA validation and density gate. */
static const uint8_t *plateau_cap_selected_source(unsigned index,unsigned slot,void *context)
{
 (void)context;
 Asset *a=scene_asset((int)slot,ASSET_SHAPESZ,(int)index,0,0);
 return a&&a->bank==ASSET_SHAPESZ&&a->index==(int)index&&a->density==8&&a->w==24&&a->h==28&&a->anchor_x==0&&a->anchor_y==0?a->rgba:NULL;
}
/* Optional finite bundle: the selected pack remains the unchanged fallback.
 * Validate all 61 source assets and the entire pass before changing a pixel. */
void render_mirror_ground101_layer1(SDL_Surface *surface,const void *first,int x,int y)
{
 ground101_frame_reset();
 if(manual_hd_enabled&&!mirror_enabled())return;
 /* Declaration is independent of lower/context validation and its early exits. */
 forest13_policy_check(game_probe_assets);
 if(!active||surface!=game_screen||reject_reason||terrain_file!='z'||game_probe_density!=8||
    game_probe_missing||game_probe_invalid||game_probe_original_reference||!game_probe_assets||
    (game_probe_scene_assets&3)!=3||!ground101_bundle_load(game_probe_assets))return;
 static bool source_checked,source_valid;
 if(!source_checked) {
  source_checked=true;source_valid=true;
  for(unsigned i=0;i<61;i++) {
   const G101Record *r=ground101_record_at(i);
   Asset *a=scene_asset((int)r->slot,(int)r->role,(int)r->index,r->role==201?0:6,r->role==201?0:7);
   if(!a||a->density!=8||memcmp(a->rgba,ground101_base(r),G101_TILE_PIXELS*4)!=0){source_valid=false;break;}
  }
#ifdef GROUND101_MATERIAL_TRACE
  if(!source_valid)fprintf(stderr,"ground101 optional bundle: source mismatch; selected pack unchanged\n");
#endif
 }
 if(source_valid&&ground101_layer1_preflight(megaData1.mainmap,sizeof(megaData1.mainmap),first,sizeof(JE_byte *),x,y)) {
  /* Optional cap failure leaves the successfully verified lower family live. */
  if(plateau_cap_bundle_load(game_probe_assets))plateau_cap_verify_sources(plateau_cap_selected_source,NULL);
  forest13_prepare(game_probe_assets,plateau_cap_selected_source,NULL);
 }
}
unsigned int render_mirror_terrain_row(SDL_Surface *surface,int x,int y,Uint8 **map,int style)
{
 if(!active||surface!=game_screen||reject_reason||!(game_probe_scene_assets&2))return 0;
 if(x<0||x+12*24>surface->pitch) {render_mirror_unsupported("terrain-row-outside-linear-layout");return 0;}
 font_before_effect((SDL_Rect){x,y,12*24,28});
 int material_row=ground101_layer1_row(map,x,y);
 if(material_row<0){render_mirror_unsupported("ground101-row-context-mismatch");return 0;}
 unsigned int replaced=0;
 for(int tile=0;tile<12;tile++) {
  unsigned int id=0;
  for(unsigned int k=0;k<terrain_source_count;k++)if(map[tile]&&map[tile]==terrain_sources[k].data) {id=terrain_sources[k].id;break;}
  if(!id)continue;
  int slot=cloud_terrain_slot(id);
  if(slot>=0&&style==MIRROR_BLEND)continue; /* Preserve original palette-blended clouds. */
  int ground_slot=ground_terrain_slot(id);
  int plateau_slot=plateau_terrain_slot(id);
  int underlay_slot=underlay_terrain_slot(id);
  int road_slot=road_terrain_slot(id);
  int holes_slot=terrain_holes_slot(id);
  int stone_slot=stone_foundation_slot(id);
  int gray_slot=layer3_gray_slot(id);
  int purple_slot=layer3_purple_slot(id);
  int circuit_slot=layer3_circuit_slot(id);
  int mechanical_slot=layer3_mechanical_slot(id);
  int linked31_slot=layer3_linked31_slot(id);
  int grass_slot=grass_sand_slot(id);
  int forest_slot=forest_terrain_slot(id);
  if(forest_slot>=0&&style!=MIRROR_NORMAL)continue;
  if((gray_slot>=0||purple_slot>=0||circuit_slot>=0||mechanical_slot>=0||linked31_slot>=0)&&style!=MIRROR_NORMAL)continue;
  if(slot<0)slot=ground_slot;
  if(slot<0)slot=plateau_slot;
  if(slot<0)slot=underlay_slot;
  if(slot<0)slot=road_slot;
  if(slot<0)slot=holes_slot;
  if(slot<0)slot=stone_slot;
  if(slot<0)slot=gray_slot;
  if(slot<0)slot=purple_slot;
  if(slot<0)slot=circuit_slot;
  if(slot<0)slot=mechanical_slot;
  if(slot<0)slot=linked31_slot;
  if(slot<0)slot=grass_slot;
  if(slot<0)slot=forest_slot;
  if(slot<0)slot=id==101?10:id==37?11:id==57?12:id==49?13:id==50?14:id==321?19:id==322?20:id==331?21:id==332?22:-1;
  if(slot<0)continue;
  if(linked31_slot>=0&&!linked31_family_ready())continue;
  Asset *a=scene_asset(slot,ASSET_SHAPESZ,(int)id,0,0);
  /* Missing/invalid new art retains the exact previous fallback and trace. */
  if((ground_slot>=0||plateau_slot>=0||underlay_slot>=0||road_slot>=0||holes_slot>=0||stone_slot>=0||gray_slot>=0||purple_slot>=0||circuit_slot>=0||mechanical_slot>=0||linked31_slot>=0||grass_slot>=0||forest_slot>=0)&&!a)continue;
  const G101Record *material=a&&a->density==8&&material_row==1&&style==MIRROR_NORMAL?ground101_record(ASSET_SHAPESZ,id):NULL;
  ground101_note_draw(material,false);
  const PCapRecord *cap=a&&a->density==8&&material_row==1&&style==MIRROR_NORMAL?plateau_cap_record(id):NULL;
  const Forest13Record *forest=a&&a->density==8&&material_row==1&&forest_registry_ok&&style==MIRROR_NORMAL?forest13_record(id):NULL;
  /* A declared coupled family cannot expose rejected fixed canopy repeats.
   * Unmarked custom packs retain their ordinary selected-art behavior. */
  if(forest_slot>=0&&forest13_declared()&&!forest)continue;
  bool mirrored=a?draw_asset_filtered(x+tile*24,y,a,style,NULL,0,material,cap,forest):false;
  suppress=false;
  if(mirrored)replaced|=1u<<tile;
  game_probe_scene_draw(ASSET_SHAPESZ,id,x+tile*24,y,0,style,mirrored);
 }
 return replaced;
}
void render_mirror_terrain_pixel(SDL_Surface *surface,Uint8 *address,Uint8 source,int style,bool replaced)
{
 /* Terrain rows render all RGBA tiles before original indexed callbacks.
  * Their actual non-cloud RGBA writes already invalidated cloud provenance. */
 bool previous=suppress,previous_cloud=suppress_cloud;suppress=replaced;suppress_cloud=replaced;
 render_mirror_pixel(surface,address,source,style);suppress=previous;suppress_cloud=previous_cloud;
}

void render_mirror_entity_end(void) { cash25_fixed_value=false;cash75_fixed_value=false;cash50_fixed_value=false;gem100_fixed_value=false;suppress=false;suppress_green_smoke=false;suppress_cloud=false; }

/* Recognized original warm/contact explosions and nine shield-hit pieces.
 * Original hue overwrite + averaged ramp value is approximated continuously
 * over true-color HSV value. No target is quantized; interpolate the same
 * source hue ramp. Exact classic/copy pixels retain the original index result.
 * Other sprite sources, ramps and animation families keep the old guard. */
static Uint32 explosion_blend_rgba(Uint32 color,Uint8 source)
{
 unsigned int peak=MAX((color>>16)&255,MAX((color>>8)&255,color&255));
 unsigned int value=((peak*15*256+127)/255+(source&15)*256)/2;
 unsigned int lo=value/256,hi=MIN(15,lo+1),fraction=value%256,hue=source&240;
 Uint32 out=0xff000000u;
 for(int shift=0;shift<24;shift+=8) {
  unsigned int a=(rgb_palette[hue+lo]>>shift)&255,b=(rgb_palette[hue+hi]>>shift)&255;
  out|=((a*(256-fraction)+b*fraction+128)/256)<<shift;
 }
 return out;
}

static bool effect_ramp_monotone_to(unsigned int hue,int last)
{
 for(int i=0;i<last;i++)for(int shift=0;shift<24;shift+=8)
  if(((rgb_palette[hue+i]>>shift)&255)>((rgb_palette[hue+i+1]>>shift)&255))return false;
 return true;
}
static bool effect_ramp_monotone(unsigned int hue)
{return effect_ramp_monotone_to(hue,15);}

static bool recognized_value_effect(unsigned int index)
{
 return index==166||index==185||index==204||index==223||index==169||index==188||index==207||index==226||
        index==170||index==189||index==208||index==227||index==171||index==190||index==209||index==247||index==228||index==266;
}

static bool recognized_contact_effect(unsigned int index,unsigned int hue)
{
 /* JE_setupExplosion's four small warm pieces have ttl12, not8. The draw
  * loop increments sprite and then uses sprite+1:152 ->154..165,171 ->
  *173..184,190 ->192..203,209 ->211..222. Large warm pieces similarly use
  * the full12-frame ranges3..14/22..33/41..52/60..71. Never let a late frame
  * restore the already drawn Talon and its overlapping HD background. */
 /* Fixed-position pickups may use explosion_data[0]={144,7}; unlike the
  * moving flare, its original sprite does not increment, so all7 draws use145.
  * Admit only this explicit ID under the existing known-sheet/Talon/ramp guards. */
 bool warm=(index>=3&&index<=14)||(index>=22&&index<=33)||(index>=41&&index<=52)||(index>=60&&index<=71)||
           (index>=122&&index<=133)||index==145||(index>=146&&index<=152)||(index>=154&&index<=165)||
           (index>=173&&index<=184)||(index>=192&&index<=203)||(index>=211&&index<=222);
 bool shield=(index>=229&&index<=237)||(index>=248&&index<=256)||(index>=267&&index<=275);
 bool green=index>=78&&index<=84; /* Original green ramp, including a missing HD frame. */
 bool smoke=index>=135&&index<=141; /* Exact original gray smoke ramp, including one missing HD frame. */
 /* Original fixed-position value graphics: explosion_data[35..52].sprite+1.
  * Their two observed blue/gray ramps use the same checked blend arithmetic;
  * keep the glyph indexed while modulating only the true-color background. */
 bool value=recognized_value_effect(index);
 /* The original Data pickup is fixed sprite266 with a warm0x70 glyph,
  * unlike the blue/gray cash values. Keep it under the same source/Talon/
  * monotone-ramp checks instead of restoring the connected HD scene. */
 bool data=index==266&&hue==0x70;
 return (warm&&(hue==0x70||hue==0x40))||(shield&&hue==0x80)||(smoke&&hue==0)||(green&&hue==0x20)||(value&&(hue==0x80||hue==0x90))||data;
}

static bool have_supported_talon(void)
{
 for(unsigned int i=0;i<region_count;i++)
  if(regions[i].live&&regions[i].bank==9&&regions[i].index>=229&&regions[i].index<=237&&regions[i].index%2==1)return true;
 return false;
}

void render_mirror_sprite2_blend_pixel(SDL_Surface *surface,Uint8 *address,Uint8 source,Sprite2_array bank,unsigned int index,int origin_x,int origin_y)
{
 if(!active||surface!=game_screen)return;
 intptr_t off=(intptr_t)address-(intptr_t)surface->pixels;
 if(off<0||off>=(intptr_t)surface->pitch*surface->h) {render_mirror_pixel(surface,address,source,MIRROR_BLEND);return;}
 int y=(int)(off/surface->pitch),x=(int)(off%surface->pitch);
 if(x>=320||y>=200)return;
 font_before_effect((SDL_Rect){x,y,1,1});
 bool known=bank.data&&bank.data==explosionSpriteSheet.data&&index&&2*(size_t)index<=bank.size;
 Uint8 before=expected[y*320+x];unsigned int subpixels=0,old_blocks=local_blocks;
 int d=game_probe_density;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)if(hd_owner[(y*d+sy)*canvas->w+x*d+sx]==1)++subpixels;
 bool old_family=((index>=122&&index<=133)||(index>=146&&index<=152))&&(source&240)==0x70;
 /* Expanded contact/shield compatibility requires a loaded supported Talon.
  * Other ships and missing Talon assets keep the previous effect guard. */
 bool talon=have_supported_talon();
 /* The fixed value glyph's source0x90 has value0. Averaging with any HD
  * value0..15 can reach at most7.5, so interpolation only reads ramp0..8.
  * The original blue ramp declines at12..15; those entries are unreachable
  * here. Check the entire reachable prefix instead of disabling the glyph
  * and restoring the Talon. Other nonmonotone sources keep the old guard. */
 bool low_value_glyph=talon&&recognized_value_effect(index)&&source==0x90&&effect_ramp_monotone_to(0x90,8);
 bool eligible=known&&(old_family||(talon&&recognized_contact_effect(index,source&240)))&&(effect_ramp_monotone(source&240)||low_value_glyph);
 bool rgba=game_probe_known_blend&&eligible&&!suppress&&!reject_reason&&*address==((source&240)|(((before&15)+(source&15))/2));
 if(rgba) {
  expected[y*320+x]=*address;
  if(selected[y*320+x]) {++occlusions;selected[y*320+x]=0;}
  for(int sy=0;sy<d;sy++) {
   Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+(y*d+sy)*canvas->pitch)+x*d;
   const Uint8 *owner=hd_owner+(y*d+sy)*canvas->w+x*d;
   for(int sx=0;sx<d;sx++) {green_first[(y*d+sy)*canvas->w+x*d+sx]=0;cloud_owner[(y*d+sy)*canvas->w+x*d+sx]=0;p[sx]=owner[sx]==1?explosion_blend_rgba(p[sx],source):palette_rgb(*address);}
  }
 } else {blend_source_index=index;render_mirror_pixel(surface,address,source,MIRROR_BLEND);blend_source_index=0;}
 game_probe_blend_write(known,index,origin_x,origin_y,x,y,before,source,*address,subpixels,local_blocks-old_blocks,rgba);
}

void render_mirror_finish(bool ordinary_crop)
{
 hud_check_mode();
 if(!active)return;
 font_prepare_finish();
 if(!ordinary_crop) render_mirror_unsupported("special-output-composition");
 if(memcmp(initial_palette,rgb_palette,sizeof(initial_palette))!=0) render_mirror_unsupported("hd-palette-change");
 /* Negative test corrupts only the display coverage ledger, never game pixels. */
 if(game_probe_coverage_fault) expected[0]^=1;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++)
  if(expected[y*320+x]!=((Uint8 *)game_screen->pixels)[y*game_screen->pitch+x]) ++mismatch;
 if(mismatch)render_mirror_unsupported("uncovered-pixel-writes");
 if(boundary_crossings)render_mirror_unsupported("local-region-boundary-crossing");
 if(!reject_reason) for(int y=0;y<200;y++)for(int x=0;x<320;x++) if(restored_mask[y*320+x]) {
  int d=game_probe_density;bool any_hd=false;
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) if(hd_owner[(y*d+sy)*canvas->w+x*d+sx])any_hd=true;
  if(any_hd)continue;
  ++restored_checks;Uint32 classic=palette_rgb(((Uint8 *)game_screen->pixels)[y*game_screen->pitch+x]);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)
   if(((Uint32 *)((Uint8 *)canvas->pixels+(y*d+sy)*canvas->pitch))[x*d+sx]!=classic)++restored_mismatches;
 }
 if(restored_mismatches)render_mirror_unsupported("local-region-residue");
 game_probe_effects(brightness_blocks,restored_checks,restored_mismatches,expanded_regions,boundary_crossings);
 upscale(output,VGAScreenSeg);
 if(!reject_reason) {
  int d=game_probe_density;
  for(int y=0;y<184*d;y++) memcpy((Uint8 *)output->pixels+y*output->pitch,(Uint8 *)canvas->pixels+y*canvas->pitch+24*d*4,(size_t)264*d*4);
 }
 bool retained_hud=!reject_reason&&ordinary_crop&&hud_compose();
 bool retained_components=!reject_reason&&ordinary_crop&&components_compose();
 bool retained_indicators=!reject_reason&&ordinary_crop&&indicators_compose();
 bool retained_fixed_text=!reject_reason&&ordinary_crop&&fixed_text_compose();
 bool retained_font=font_finish(!reject_reason&&ordinary_crop);
 bool retained_scene_hd=memchr(hd_owner,1,(size_t)canvas->w*canvas->h)!=NULL||memchr(hd_owner,2,(size_t)canvas->w*canvas->h)!=NULL;
 bool retained_hd=retained_scene_hd||retained_hud||retained_components||retained_indicators||retained_fixed_text||retained_font;
 unsigned int classic_mismatches=0;
 if(game_probe_original_reference)for(int y=0;y<output->h;y++) {
  const Uint32 *row=(const Uint32 *)((Uint8 *)output->pixels+y*output->pitch);
  const Uint8 *classic=(Uint8 *)VGAScreenSeg->pixels+(y/game_probe_density)*VGAScreenSeg->pitch;
  for(int x=0;x<output->w;x++)if(row[x]!=palette_rgb(classic[x/game_probe_density]))++classic_mismatches;
 }
 game_probe_rgb_audit(output,classic_mismatches);
 last_output_scene_hd=!reject_reason&&retained_scene_hd;
 last_output_valid=!reject_reason&&retained_hd;
 memcpy(last_output_palette,rgb_palette,sizeof(last_output_palette));
 if(retained_hud)memcpy(hud_output_palette,rgb_palette,sizeof(hud_output_palette));
 if(retained_components)memcpy(component_output_palette,rgb_palette,sizeof(component_output_palette));
 if(retained_indicators)memcpy(indicator_output_palette,rgb_palette,sizeof(indicator_output_palette));
 if(retained_fixed_text)memcpy(fixed_text_output_palette,rgb_palette,sizeof(fixed_text_output_palette));
 for(int y=0;y<200;y++)memcpy(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320);
 ground101_frame_report(game_probe_tick,reject_reason);
 game_probe_frame(draws,occlusions,mismatch,reject_reason?reject_reason:retained_hd?"hd-ordered":"classic-assets",all_rejections,local_entities,local_regions,local_blocks);
 if(game_probe_capture_tick()) {
  char name[64];snprintf(name,sizeof(name),"display-%04u.bmp",game_probe_tick);game_probe_export(output,name);
 }
 active=false;ready=game_probe_density>1;
}

/* Full-range solid black/white fades and restoration of the saved palette.
 * Each true-color channel follows the original integer diff/remaining-steps
 * schedule. Classic pixels use the original newly updated palette directly. */
void render_mirror_fade_start(const SDL_Color *target,const SDL_Color *solid,unsigned int first,unsigned int last)
{
 if(manual_hd_enabled&&!mirror_enabled()) {render_mirror_hud_reset();return;}
 hud_check_mode();
 if(font_cached()&&!font_cached_indices_match())font_clear_cached(15);
 bool cached=last_output_valid;last_output_valid=false;fade_mode=0;ready=false;
 if(!mirror_enabled()||game_probe_density<2||!output||!cached||first!=0||last!=255)return;
 bool component_cached=component_output_generation||component_saved_generation;
 for(unsigned i=0;i<320*200&&!component_cached;i++)component_cached=(component_output_owner[i]|component_saved_owner[i])!=0;
 if(component_cached&&!components_cached_indices_match()) {components_clear_cached(63);return;}
 for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)!=0)return;
 if(solid&&solid->r==solid->g&&solid->g==solid->b&&(solid->r==0||solid->r==255)) {
  if(memcmp(last_output_palette,rgb_palette,sizeof(last_output_palette))!=0)return;
  if(!fade_saved)fade_saved=SDL_CreateRGBSurfaceWithFormat(0,output->w,output->h,32,SDL_PIXELFORMAT_ARGB8888);
  if(!fade_saved)return;
  for(int y=0;y<output->h;y++)memcpy((Uint8 *)fade_saved->pixels+y*fade_saved->pitch,(Uint8 *)output->pixels+y*output->pitch,(size_t)output->w*4);
  memcpy(fade_saved_palette,rgb_palette,sizeof(fade_saved_palette));
  memcpy(hud_saved_owner,hud_output_owner,sizeof(hud_saved_owner));hud_saved_generation=hud_output_generation;
  memcpy(fixed_text_saved_owner,fixed_text_output_owner,sizeof(fixed_text_saved_owner));fixed_text_saved_generation=fixed_text_output_generation;
  memcpy(component_saved_owner,component_output_owner,sizeof(component_saved_owner));component_saved_generation=component_output_generation;
  memcpy(indicator_saved_owner,indicator_output_owner,sizeof(indicator_saved_owner));indicator_saved_generation=indicator_output_generation;
  memcpy(indicator_saved_under,indicator_under,sizeof(indicator_saved_under));
  memcpy(indicator_saved_under_owner,indicator_under_owner,sizeof(indicator_saved_under_owner));indicator_saved_under_generation=indicator_under_generation;
  font_fade_save();have_fade_saved=true;fade_mode=solid->r==0?1:2;
 } else if(target&&have_fade_saved) {
  for(int i=0;i<256;i++)if((fade_saved_palette[i]&0xffffffu)!=(((Uint32)target[i].r<<16)|((Uint32)target[i].g<<8)|target[i].b))return;
  fade_mode=3;
 }
 if(fade_mode)last_output_valid=true;
}

void render_mirror_fade_step(int steps)
{
 if(manual_hd_enabled&&!mirror_enabled()) {render_mirror_hud_reset();return;}
 hud_check_mode();
 if(!fade_mode||steps<=0)return;
 if(font_cached()&&!font_cached_indices_match()){font_clear_cached(15);return;}
 if(fixed_text_output_generation&&!fixed_text_cached_indices_match()) {fixed_text_clear_cached();return;}
 if(indicator_output_generation&&(!indicators_cached_indices_match()||!indicators_underlay_matches())) {indicators_clear_cached(3);return;}
 if(hud_output_generation&&!hud_cached_indices_match()) {hud_clear_cached();return;}
 bool component_cached=component_output_generation||component_saved_generation;
 for(unsigned i=0;i<320*200&&!component_cached;i++)component_cached=(component_output_owner[i]|component_saved_owner[i])!=0;
 if(component_cached&&!components_cached_indices_match()) {components_clear_cached(63);return;}
 int d=game_probe_density;unsigned int hd_pixels=0;
 for(int y=0;y<output->h;y++) {
  Uint32 *row=(Uint32 *)((Uint8 *)output->pixels+y*output->pitch);
  const Uint32 *saved=(Uint32 *)((Uint8 *)fade_saved->pixels+y*fade_saved->pitch);
  for(int x=0;x<output->w;x++) {
   unsigned int logical=(unsigned int)((y/d)*320+x/d);
   bool hud=hud_output_generation==hud_generation&&hud_saved_generation==hud_generation&&
     hud_output_owner[logical]&&hud_saved_owner[logical];
   bool component=component_output_generation==component_generation&&component_saved_generation==component_generation&&
     component_output_owner[logical]&&component_saved_owner[logical];
   int cell=indicator_output_generation?indicator_cell(x/d,y/d):-1;
   bool indicator=cell>=0&&indicator_output_generation==indicator_generation&&indicator_saved_generation==indicator_generation&&
     indicator_output_owner[cell]&&indicator_saved_owner[cell];
   int fixed_cell=fixed_text_output_generation?hud_fixed_text_cell(x/d,y/d):-1;
   bool fixed=fixed_cell>=0&&fixed_text_output_generation==fixed_text_generation&&fixed_text_saved_generation==fixed_text_generation&&
    fixed_text_output_owner[fixed_cell]&&fixed_text_saved_owner[fixed_cell];
   int font_cell=font_output_generation?font_pcell(x/d,y/d):-1;
   bool text=font_cell>=0&&font_output_generation==font_generation&&font_saved_generation==font_generation&&font_powner[font_cell]&&font_psaved_owner[font_cell];
   bool hd=(x<264*d&&y<184*d&&hd_owner[y*canvas->w+x+24*d]!=0)||hud||component||indicator||fixed||text;
   if(hd) {
    Uint32 target=fade_mode==1?0:fade_mode==2?0xffffffu:saved[x];
    Uint32 color=0xff000000u;
    for(int shift=0;shift<24;shift+=8) {
     int old=(row[x]>>shift)&255,want=(target>>shift)&255;
     color|=(Uint32)(old+(want-old)/steps)<<shift;
    }
    row[x]=color;++hd_pixels;
   } else row[x]=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[(y/d)*VGAScreenSeg->pitch+x/d]);
  }
 }
 indicators_fade_underlay(steps);font_fade_underlay(steps);
 if(indicator_output_generation)memcpy(indicator_output_palette,rgb_palette,sizeof(indicator_output_palette));
 if(hud_output_generation)memcpy(hud_output_palette,rgb_palette,sizeof(hud_output_palette));
 if(component_output_generation)memcpy(component_output_palette,rgb_palette,sizeof(component_output_palette));
 if(fixed_text_output_generation)memcpy(fixed_text_output_palette,rgb_palette,sizeof(fixed_text_output_palette));
 ready=true;game_probe_fade_sample(output,steps,hd_pixels,fade_mode);
 if(steps==1)fade_mode=0;
}

bool render_mirror_present(SDL_Renderer *renderer,SDL_Surface *src,const SDL_Rect *dst)
{
 if(manual_hd_enabled&&!mirror_enabled()) {render_mirror_hud_reset();return false;}
 hud_check_mode();
 if(font_cached()&&(!font_cached_indices_match()||memcmp(font_output_palette,rgb_palette,sizeof(font_output_palette))))font_clear_cached(15);
 if(fixed_text_output_generation&&(!fixed_text_cached_indices_match()||memcmp(fixed_text_output_palette,rgb_palette,sizeof(fixed_text_output_palette))!=0))fixed_text_clear_cached();
 if(indicator_output_generation&&(!indicators_cached_indices_match()||!indicators_underlay_matches()||memcmp(indicator_output_palette,rgb_palette,sizeof(indicator_output_palette))!=0))indicators_clear_cached(3);
 if(hud_output_generation&&(!hud_cached_indices_match()||memcmp(hud_output_palette,rgb_palette,sizeof(hud_output_palette))!=0))hud_clear_cached();
 bool component_cached=component_output_generation||component_saved_generation;
 for(unsigned i=0;i<320*200&&!component_cached;i++)component_cached=(component_output_owner[i]|component_saved_owner[i])!=0;
 if(component_cached&&(!components_cached_indices_match()||memcmp(component_output_palette,rgb_palette,sizeof(component_output_palette))!=0))components_clear_cached(63);
 if(!ready||src!=VGAScreenSeg)return false;ready=false;
 if(game_probe_skip) { uint64_t rng=mt_state_fingerprint();game_probe_present(0,rng,rng);return true; }
 if(!texture) texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,output->w,output->h);
 if(!texture)return false;
 if(SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)!=0||SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_NONE)!=0)return false;
 void *pixels=NULL;int pitch=0;
 if(SDL_LockTexture(texture,NULL,&pixels,&pitch)!=0)return false;
 for(int y=0;y<output->h;y++) memcpy((Uint8 *)pixels+y*pitch,(Uint8 *)output->pixels+y*output->pitch,(size_t)output->w*4);
 SDL_UnlockTexture(texture);
 uint64_t rng_before=mt_state_fingerprint();
 for(int i=0;i<(game_probe_repeat?2:1);i++) {
  if(SDL_SetRenderDrawColor(renderer,0,0,0,255)!=0||SDL_RenderClear(renderer)!=0||SDL_RenderCopy(renderer,texture,NULL,dst)!=0) return false;
  asset_debug_readback(renderer);
  SDL_RenderPresent(renderer);
 }
 if(rng_before!=mt_state_fingerprint()) {fprintf(stderr,"Display advanced RNG\n");exit(2);}
 game_probe_present(game_probe_repeat?2:1,rng_before,mt_state_fingerprint());
 return true;
}

void render_mirror_release_texture(void)
{
 /* Renderer recreation keeps the gameplay lease, but discards pending HUD.
  * True video teardown separately revokes it before freeing indexed surfaces. */
 render_mirror_hud_suspend();
 if(texture) {SDL_DestroyTexture(texture);texture=NULL;}
 ready=false;
 render_mirror_reset_banking();
}

#else
typedef int render_mirror_disabled_translation_unit;
#endif
