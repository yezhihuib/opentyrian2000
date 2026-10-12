#ifndef RENDER_MIRROR_DISABLED
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Display-only ordered mirror. The engine always executes original 1x writes.
 * Unsupported effects or incomplete changed-pixel coverage reject the full frame.
 */
#include "render_mirror.h"
#include "game_probe.h"
#include "asset_debug.h"
#include "entity_draw.h"
#include "palette.h"
#include "mtrand.h"
#include "video.h"
#include "varz.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
 bool initialized,valid;
 int bank,index,w,h,anchor_x,anchor_y,density;
 Uint8 *rgba;
} Asset;
enum { ASSET_NEWSH2=101, ASSET_NEWSHE=110, ASSET_TALON_BANK=109, ASSET_SHAPESZ=201, ASSET_EXPLOSION=106 };
/* Roads220..226,235..236; installation231..234 and underlay237..240 stay unchanged. */
static Asset assets[330];
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
static struct {const Uint8 *data;unsigned int id;} terrain_sources[162];
static unsigned int terrain_source_count;
static SDL_Surface *canvas,*output;
static SDL_Surface *fade_saved;
static Uint32 fade_saved_palette[256],last_output_palette[256];
static Uint8 last_output_indices[320*200];
static bool last_output_valid,have_fade_saved;
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

void render_mirror_begin(void)
{
 /* JE_main level_loop calls begin exactly once per simulation tick. Neither
  * individual sprites, shadows nor repeated Present calls advance this clock. */
 ground101_frame_reset();
 ++mirror_logic_tick;banking_draw_player=0;
 last_output_valid=false;have_fade_saved=false;fade_mode=0;
 ready=false; active=false; suppress=false;suppress_green_smoke=false;suppress_cloud=false;
 if(!game_probe_enabled) return;
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
 if(!active||surface!=game_screen) return;
 intptr_t offset=(intptr_t)address-(intptr_t)surface->pixels;
 if(offset<0||offset>=(intptr_t)surface->pitch*surface->h) { render_mirror_unsupported("invalid-write-address");return; }
 int y=(int)(offset/surface->pitch),x=(int)(offset%surface->pitch);
 if(x>=320||y>=200) return;
 Uint8 before=expected[y*320+x];expected[y*320+x]=*address;
 if(reject_reason) return;
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
 const char *prefix=a->bank==9?"ship":a->bank==8?"bullet":a->bank==ASSET_NEWSH2?"enemy-newsh2":a->bank==ASSET_NEWSHE?"enemy-newshe":a->bank==ASSET_TALON_BANK?"talon-bank":a->bank==ASSET_EXPLOSION?"explosion-newsh6":"terrain-shapesz";
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

static bool draw_asset_filtered(int x,int y,Asset *a,int style,const SDL_Rect *part,Uint8 filter,const G101Record *material)
{
 /* Original Talon invulnerability uses half-opacity, not a different sprite.
  * Preserve that effect over the ordered RGBA scene and keep the engine's
  * original indexed blend writes for gameplay/coverage. Other sources and
  * the explicit original-copy diagnostic keep their established fallback. */
 bool talon_blend=style==MIRROR_BLEND&&a->bank==9&&a->index>=229&&a->index<=237&&a->index%2==1&&!game_probe_original_reference;
 bool explosion_blend=style==MIRROR_BLEND&&a->bank==ASSET_EXPLOSION&&explosion_asset_slot((unsigned int)a->index)>=0&&!game_probe_original_reference;
 if(style==MIRROR_BLEND&&!talon_blend&&!explosion_blend) {
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
  } else if(explosion_blend) {
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
{return draw_asset_filtered(x,y,a,style,part,0,NULL);}

bool render_mirror_entity(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int index,int style,int layout)
{
 if(!active||surface!=game_screen||reject_reason)return false;
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

/* Enemy-only energy orb binding: shared numeric player IDs are not mapped. */
bool render_mirror_enemy_shot(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int index)
{
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

bool render_mirror_enemy_tile(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned int base,int part,int filter,const G101EnemyContext *material_context)
{
 if(!active||surface!=game_screen||reject_reason||!(game_probe_scene_assets&1))return false;
 int role=0;
 for(int i=0;i<4;i++)if(bank.data&&bank.data==enemySpriteSheets[i].data) {
  if(enemySpriteSheetIds[i]==1)role=ASSET_NEWSH2;
  else if(enemySpriteSheetIds[i]==9)role=ASSET_NEWSHE;
 }
 /* Existing ground201..209 and rotor210..217 remain unchanged. */
 int slot=base==169?303:base==207?304:base==245?305:base==273?306:base==275?307:base==277?308:base==279?309:base==281?310:base==283?311:base==153?269:base==155?270:base==157?271:base==49?265:base==51?266:base==89?267:base==127?268:base==267?243:base==269?244:base==271?245:base==81?231:base==83?232:base==119?233:base==121?234:(base>=229&&base<=243&&base%2==1)?210+(int)(base-229)/2:base==77?6:base==79?7:base==115?8:base==117?9:base==85?15:base==87?16:base==123?17:base==125?18:(base>=191&&base<=205&&base%2==1)?23+(int)(base-191)/2:-1;
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
  mirrored=draw_asset_filtered(x-px,y-py,a,MIRROR_NORMAL,&quadrant,(Uint8)filter,material);
 }
 game_probe_scene_draw(role,base,x,y,part,filter?3:MIRROR_NORMAL,mirrored);return mirrored;
}

void render_mirror_map_begin(char shape_file)
{ground101_frame_reset();terrain_file=shape_file=='Z'?'z':shape_file;terrain_source_count=0;render_mirror_reset_banking();}
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
/* Finite low-grass/sand Layer1 family; neighboring forest remains original. */
static int grass_sand_slot(unsigned int id)
{
 static const unsigned int ids[9]={66,67,69,76,78,79,80,89,90};
 for(int i=0;i<9;i++)if(id==ids[i])return 312+i;
 return -1;
}
void render_mirror_bind_terrain(unsigned int layer,unsigned int id,const Uint8 *data)
{
 if(terrain_file=='z'&&((layer==1&&(grass_sand_slot(id)>=0||stone_foundation_slot(id)>=0||terrain_holes_slot(id)>=0||road_terrain_slot(id)>=0||underlay_terrain_slot(id)>=0||plateau_terrain_slot(id)>=0||ground_terrain_slot(id)>=0||id==101||id==37||id==57||id==49||id==50||id==321||id==322||id==331||id==332))||(layer==2&&cloud_terrain_slot(id)>=0)||(layer==3&&(layer3_gray_slot(id)>=0||layer3_purple_slot(id)>=0)))&&terrain_source_count<162) {
  terrain_sources[terrain_source_count].data=data;
  terrain_sources[terrain_source_count++].id=id;
 }
}
/* Optional finite bundle: the selected pack remains the unchanged fallback.
 * Validate all 61 source assets and the entire pass before changing a pixel. */
void render_mirror_ground101_layer1(SDL_Surface *surface,const void *first,int x,int y)
{
 ground101_frame_reset();
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
 if(source_valid)ground101_layer1_preflight(megaData1.mainmap,sizeof(megaData1.mainmap),first,sizeof(JE_byte *),x,y);
}
unsigned int render_mirror_terrain_row(SDL_Surface *surface,int x,int y,Uint8 **map,int style)
{
 if(!active||surface!=game_screen||reject_reason||!(game_probe_scene_assets&2))return 0;
 if(x<0||x+12*24>surface->pitch) {render_mirror_unsupported("terrain-row-outside-linear-layout");return 0;}
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
  int grass_slot=grass_sand_slot(id);
  if((gray_slot>=0||purple_slot>=0)&&style!=MIRROR_NORMAL)continue;
  if(slot<0)slot=ground_slot;
  if(slot<0)slot=plateau_slot;
  if(slot<0)slot=underlay_slot;
  if(slot<0)slot=road_slot;
  if(slot<0)slot=holes_slot;
  if(slot<0)slot=stone_slot;
  if(slot<0)slot=gray_slot;
  if(slot<0)slot=purple_slot;
  if(slot<0)slot=grass_slot;
  if(slot<0)slot=id==101?10:id==37?11:id==57?12:id==49?13:id==50?14:id==321?19:id==322?20:id==331?21:id==332?22:-1;
  if(slot<0)continue;
  Asset *a=scene_asset(slot,ASSET_SHAPESZ,(int)id,0,0);
  /* Missing/invalid new art retains the exact previous fallback and trace. */
  if((ground_slot>=0||plateau_slot>=0||underlay_slot>=0||road_slot>=0||holes_slot>=0||stone_slot>=0||gray_slot>=0||purple_slot>=0||grass_slot>=0)&&!a)continue;
  const G101Record *material=a&&a->density==8&&material_row==1&&style==MIRROR_NORMAL?ground101_record(ASSET_SHAPESZ,id):NULL;
  ground101_note_draw(material,false);
  bool mirrored=a?draw_asset_filtered(x+tile*24,y,a,style,NULL,0,material):false;
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

void render_mirror_entity_end(void) { suppress=false;suppress_green_smoke=false;suppress_cloud=false; }

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
 return (warm&&(hue==0x70||hue==0x40))||(shield&&hue==0x80)||(smoke&&hue==0)||(green&&hue==0x20)||(value&&(hue==0x80||hue==0x90));
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
 if(!active)return;
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
 bool retained_hd=memchr(hd_owner,1,(size_t)canvas->w*canvas->h)!=NULL||memchr(hd_owner,2,(size_t)canvas->w*canvas->h)!=NULL;
 unsigned int classic_mismatches=0;
 if(game_probe_original_reference)for(int y=0;y<output->h;y++) {
  const Uint32 *row=(const Uint32 *)((Uint8 *)output->pixels+y*output->pitch);
  const Uint8 *classic=(Uint8 *)VGAScreenSeg->pixels+(y/game_probe_density)*VGAScreenSeg->pitch;
  for(int x=0;x<output->w;x++)if(row[x]!=palette_rgb(classic[x/game_probe_density]))++classic_mismatches;
 }
 game_probe_rgb_audit(output,classic_mismatches);
 last_output_valid=!reject_reason&&retained_hd;
 memcpy(last_output_palette,rgb_palette,sizeof(last_output_palette));
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
 bool cached=last_output_valid;last_output_valid=false;fade_mode=0;ready=false;
 if(!game_probe_enabled||game_probe_density<2||!output||!cached||first!=0||last!=255)return;
 for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)!=0)return;
 if(solid&&solid->r==solid->g&&solid->g==solid->b&&(solid->r==0||solid->r==255)) {
  if(memcmp(last_output_palette,rgb_palette,sizeof(last_output_palette))!=0)return;
  if(!fade_saved)fade_saved=SDL_CreateRGBSurfaceWithFormat(0,output->w,output->h,32,SDL_PIXELFORMAT_ARGB8888);
  if(!fade_saved)return;
  for(int y=0;y<output->h;y++)memcpy((Uint8 *)fade_saved->pixels+y*fade_saved->pitch,(Uint8 *)output->pixels+y*output->pitch,(size_t)output->w*4);
  memcpy(fade_saved_palette,rgb_palette,sizeof(fade_saved_palette));have_fade_saved=true;fade_mode=solid->r==0?1:2;
 } else if(target&&have_fade_saved) {
  for(int i=0;i<256;i++)if((fade_saved_palette[i]&0xffffffu)!=(((Uint32)target[i].r<<16)|((Uint32)target[i].g<<8)|target[i].b))return;
  fade_mode=3;
 }
 if(fade_mode)last_output_valid=true;
}

void render_mirror_fade_step(int steps)
{
 if(!fade_mode||steps<=0)return;
 int d=game_probe_density;unsigned int hd_pixels=0;
 for(int y=0;y<output->h;y++) {
  Uint32 *row=(Uint32 *)((Uint8 *)output->pixels+y*output->pitch);
  const Uint32 *saved=(Uint32 *)((Uint8 *)fade_saved->pixels+y*fade_saved->pitch);
  for(int x=0;x<output->w;x++) {
   bool hd=x<264*d&&y<184*d&&hd_owner[y*canvas->w+x+24*d]!=0;
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
 ready=true;game_probe_fade_sample(output,steps,hd_pixels,fade_mode);
 if(steps==1)fade_mode=0;
}

bool render_mirror_present(SDL_Renderer *renderer,SDL_Surface *src,const SDL_Rect *dst)
{
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
 if(texture) {SDL_DestroyTexture(texture);texture=NULL;}
 ready=false;
 render_mirror_reset_banking();
}

#else
typedef int render_mirror_disabled_translation_unit;
#endif
