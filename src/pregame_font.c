/* SPDX-License-Identifier: GPL-2.0-or-later
 * PIC1 pre-game root/category and bounded equipment-product leases. Original indexed work is untouched.
 * Reuses accepted SFN1 resources and the selector output-footprint sampler.
 */
#include "pregame_font.h"
#include "settings_font.h"
#include "selector_font_output.h"
#include "helptext.h"
#include "load_font.h"
#include "selector_font.h"
#include "font.h"
#include "fonthand.h"
#include "sprite.h"
#include "palette.h"
#include "video.h"
#include "video_scale.h"
#include <stdint.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define SF_OPEN(p) _open(p,_O_RDONLY|_O_BINARY|_O_NOINHERIT)
#define SF_READ _read
#define SF_CLOSE _close
#define SF_FSTAT _fstat
#define SF_STAT struct _stat
#define SF_REGULAR(m) (((m)&_S_IFMT)==_S_IFREG)
#else
#include <unistd.h>
#define SF_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define SF_READ read
#define SF_CLOSE close
#define SF_FSTAT fstat
#define SF_STAT struct stat
#define SF_REGULAR(m) S_ISREG(m)
#endif
#define SF_MAP UINT64_C(0x845b16939661b466)
#define SF_PAL UINT64_C(0x69f74bd2c5d2ad5b)
#define SF_FNV UINT64_C(14695981039346656037)
#define PF_PAL UINT64_C(0x1c6687307999bd82)
#define PF_BASE UINT64_C(0x45a77a2246c174b9)
#define PF_METAL_HASH UINT64_C(0xccdc5e34cc4f9f93)
#include "shop_talon_sprite_pins.h"
#include "shop_equipment_sprite_pins.h"
enum { SF_W=320,SF_H=200,SF_N=64000,SF_OW=1280,SF_OH=800,
 SF_OUT_BYTES=4096000,SF_PAYLOAD=1785856,SF_COMMANDS=1024,SF_GLYPHS=272,
 SF_MASK_BYTES=60*17*20+85*12*13+127*6*8,SF_EVENTS=40000,SF_CAP=11*1024*1024,
 PF_METAL_BYTES=1276820,PF_METAL_RUNS=2492,PF_METAL_PIXELS=314221,
 PF_SPRITE_W=85,PF_SPRITE_H=112,PF_SPRITE_BYTES=85*112*16*4,
 PF_FRONT_BYTES=33*34*16*4,PF_SHOP_SPRITES=2 };
enum { C_DARK,C_FACE,C_CLASSIC,C_SPRITE };
enum { S_IDLE,S_BUILD,S_RUN,S_PRIMITIVE,S_READY,S_CURSOR,S_CURSOR_DONE };
struct SfSpec { unsigned aw,ah,cw,ch,n,eligible,plane,mode,lo,hi,mw,mh; uint64_t metrics,encoded,eligibility,payload; const char *name; };
static const struct SfSpec spec[3]={
 {1216,384,76,96,60,53,466944,1,12,15,17,20,UINT64_C(0xb0a8226af36e025a),UINT64_C(0x5c12ed2dea448227),UINT64_C(0x5529cd3792b04378),UINT64_C(0x0501f2f573e8d9a5),"large"},
 {896,384,56,64,85,76,344064,1,12,15,12,13,UINT64_C(0xf0dec0f37828f1c4),UINT64_C(0x96f0e4e668876f23),UINT64_C(0xa3861b64f710cb1f),UINT64_C(0x08f9609583417c89),"medium"},
 {512,320,32,40,127,86,163840,0,7,7,6,8,UINT64_C(0x0908ca85cbf2a1e3),UINT64_C(0x2ed2973d82ce6f3d),UINT64_C(0x68e8c2bab3c43d0d),UINT64_C(0x85cddeb8bd7ea09a),"tiny"}
};
/* Exactly two fixed identities; PSP1 never supplies allocation geometry. */
struct ShopSpriteSpec { unsigned bank,id,w,h,x,y,bytes,rle_bytes;uint64_t rle,index,mask,payload;const char *name; };
static const struct ShopSpriteSpec shop_spec[PF_SHOP_SPRITES]={
 {5,31,85,112,35,33,PF_SPRITE_BYTES,5578,PF_SPRITE_RLE,PF_SPRITE_INDEX,PF_SPRITE_MASK,PF_SPRITE_HASH,"shop-talon-option31-v1.hda"},
 {6,0,33,34,61,48,PF_FRONT_BYTES,897,UINT64_C(0x1a232f9fc3e904b2),UINT64_C(0xdb89c876a399ba93),UINT64_C(0x1ea87c3f611af9a4),PF_FRONT_HASH,"shop-front-weapon00-v1.hda"}
};
struct SfGlyph { const Uint8 *rle; Uint16 size,mask; Uint8 w,h,ink; };
/* Whole-run typography is deliberately independent of shared SFN1 metrics. */
struct PfMenuSpec { const char *text; unsigned x,y,w,h; uint64_t text_hash,payload_hash; };
#include "shop_menu_font_pins.h"
struct SfCommand { Uint16 x,y,w,h; Uint8 kind,bank,id,hue,cash,menu_run; Sint16 value; unsigned first,events; };
struct SfEvent { Uint16 position; Uint8 index,style; };
static struct {
 bool active,frame,glyph,cursor,exiting,primitive,ship_shield,product,updating;
 unsigned category,names,costs,static_count,static_events,cash_first,cash_limit,illustration;
 bool heading,product_footer,cash_seen,sprite_drawn;
 int stage,fade_remaining,fade_declared;
 unsigned menu,selected,last,row,next_role,cubes,phase,phase_count;
 unsigned count,next,limit,pixel,run_count,run_role,event_count,event_next,event_limit;
 char text[9][18],footer[8][66],cash[32];
 bool cursor_sprite;unsigned cursor_quad,cursor_events,cursor_next;int cursor_x,cursor_y;
 struct { Uint16 position;Uint8 index; } cursor_event[168];
 SDL_Surface *screen,*backup; void *pixels,*backup_pixels;
 SDL_PixelFormat *format,*backup_format;
 unsigned generation,frame_generation;
 Uint8 underlay[SF_N],base[SF_N],expected[SF_N],replay[SF_N],owner[SF_N],pre_cursor[SF_N],cursor_index[SF_N],cursor_mask[SF_N];
 Uint8 metal_blocked[SF_N];
 struct SfGlyph glyphs[SF_GLYPHS];Uint8 masks[SF_MASK_BYTES];
 struct SfCommand commands[SF_COMMANDS];struct SfEvent events[SF_EVENTS];
 SDL_Color expected_palette[256],fade_target[256];Uint32 palette[256];
 Uint8 *payload[3],*metal,*shop_sprite,*shop_front,*menu_run[7];unsigned metal_gain,metal_target;Uint32 *output;
} sf;
static const char *directory;
size_t pregame_font_static_bytes(void){return sizeof(sf);}
bool pregame_font_owns_display(void){return sf.active;}
typedef char sf_budget_check[(sizeof(sf)+1800000+70000+SF_PAYLOAD+SF_OUT_BYTES+PF_METAL_BYTES+PF_SPRITE_BYTES+PF_FRONT_BYTES+PF_MENU_BYTES+5*128+2048<=SF_CAP)?1:-1];
typedef char sf_command_check[(sizeof(struct SfCommand)<=24)?1:-1];
static uint64_t hash_more(uint64_t h,const Uint8 *p,size_t n)
{while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint64_t hash(const void *p,size_t n){return hash_more(SF_FNV,p,n);}
static uint64_t hash16(uint64_t h,unsigned v){Uint8 p[2]={(Uint8)v,(Uint8)(v>>8)};return hash_more(h,p,2);}
static uint32_t u32(const Uint8 *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const Uint8 *p){return u32(p)|((uint64_t)u32(p+4)<<32);}
static uint64_t palette_hash(const SDL_Color *p){uint64_t h=SF_FNV;for(unsigned i=0;i<256;i++){Uint8 b[3]={p[i].r,p[i].g,p[i].b};h=hash_more(h,b,3);}return h;}
static struct SfGlyph *glyph(unsigned bank,unsigned id){return &sf.glyphs[(bank==0?0:bank==1?60:145)+id];}
static void reject(void){sf.frame=false;sf.glyph=false;sf.stage=S_IDLE;}
void pregame_font_set_directory(const char *path){pregame_font_end();directory=path&&*path?path:NULL;}
void pregame_font_release_texture(void){if(sf.active||sf.output)selector_font_output_release();}
void pregame_font_end(void){pregame_font_release_texture();for(unsigned b=0;b<3;b++)free(sf.payload[b]);for(unsigned r=0;r<7;r++)free(sf.menu_run[r]);free(sf.metal);free(sf.shop_sprite);free(sf.shop_front);free(sf.output);memset(&sf,0,sizeof(sf));}
void pregame_font_invalidate(void){if(sf.active){++sf.generation;reject();}pregame_font_release_texture();}
void pregame_font_table_reset(unsigned table){if(table<3||table==5||table==6)pregame_font_end();}
static bool geometry(SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==SF_W&&s->h==SF_H&&s->pitch==SF_W&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&s->clip_rect.x==0&&s->clip_rect.y==0&&s->clip_rect.w==SF_W&&s->clip_rect.h==SF_H;}
static bool layout(void){return sf.screen==VGAScreen&&sf.screen==VGAScreenSeg&&sf.backup==VGAScreen2&&geometry(sf.screen)&&geometry(sf.backup)&&sf.screen->pixels==sf.pixels&&sf.backup->pixels==sf.backup_pixels&&sf.screen->format==sf.format&&sf.backup->format==sf.backup_format;}
static bool source(bool capture)
{
 uint64_t map=SF_FNV;unsigned offset=0;
 for(unsigned i=0;i<256;i++){uint32_t v=(uint32_t)font_ascii[i];Uint8 p[4]={(Uint8)v,(Uint8)(v>>8),(Uint8)(v>>16),(Uint8)(v>>24)};map=hash_more(map,p,4);}
 if(map!=SF_MAP)return false;
 for(unsigned b=0;b<3;b++){
  const struct SfSpec *s=&spec[b];uint64_t metrics=SF_FNV,encoded=SF_FNV,eligible=SF_FNV;
  if(sprite_table[b].count!=s->n)return false;
  if(b==2){const Uint8 count[4]={127,0,0,0};encoded=hash_more(encoded,count,4);}
  for(unsigned id=0;id<s->n;id++){
   const Sprite *sp=sprite(b,id);struct SfGlyph *g=glyph(b,id);
   if(!sp->data||!sp->width||!sp->height||sp->width>s->mw||sp->height>s->mh||!sp->size||sp->size>2*s->mw*s->mh+s->mh)return false;
   if(!capture&&(g->rle!=sp->data||g->size!=sp->size||g->w!=sp->width||g->h!=sp->height))return false;
   metrics=hash16(hash16(hash16(metrics,sp->width),sp->height),sp->width+1);
   encoded=hash16(hash16(hash16(encoded,sp->width),sp->height),sp->size);encoded=hash_more(encoded,sp->data,sp->size);
   if(capture){
    if(offset+sp->width*sp->height>sizeof(sf.masks))return false;
    g->rle=sp->data;g->size=sp->size;g->w=sp->width;g->h=sp->height;g->mask=offset;g->ink=0;
    memset(sf.masks+offset,255,g->w*g->h);unsigned x=0,y=0;
    for(unsigned k=0;k<sp->size;k++){
     Uint8 v=sp->data[k];if(y>=g->h)return false;
     if(v==255){if(++k>=sp->size)return false;x+=sp->data[k];}
     else if(v==254)x=g->w;else if(v==253)++x;
     else{if(x>=g->w)return false;sf.masks[offset+y*g->w+x]=v&15;g->ink=1;++x;}
     if(x>g->w)return false;
    if(x==g->w){x=0;++y;}
    }
    if(x||y>g->h)return false;
    offset+=g->w*g->h;
   }
   Uint8 e=(b==2?id<86:g->ink)?255:0;eligible=hash_more(eligible,&e,1);
  }
  if(metrics!=s->metrics||encoded!=s->encoded||eligible!=s->eligibility)return false;
 }
 return true;
}
static bool padding(unsigned b,const Uint8 *data)
{
 const struct SfSpec *s=&spec[b];unsigned inked=0;
 for(unsigned id=0;id<(s->aw/s->cw)*(s->ah/s->ch);id++){
  const struct SfGlyph *g=id<s->n?glyph(b,id):NULL;bool ink=false;
  for(unsigned y=0;y<s->ch;y++)for(unsigned x=0;x<s->cw;x++){
   unsigned p=((id/16)*s->ch+y)*s->aw+(id%16)*s->cw+x;Uint8 a=data[p],r=s->mode?data[s->plane+p]:0;
   bool allowed=g&&g->ink&&x>=4&&y>=4&&x<4+g->w*4u&&y<4+g->h*4u;
   if((!allowed&&(a||r))||(!a&&r)||(a&&s->mode&&(r<s->lo||r>s->hi)))return false;
   if(a)ink=true;
  }
  if(g&&ink!=(bool)g->ink)return false;
  inked+=ink;
 }
 return inked==(b==2?127:s->eligible);
}
static bool load(unsigned b)
{
 const struct SfSpec *s=&spec[b];char path[1024];Uint8 h[128],extra;SF_STAT st;
 int n=snprintf(path,sizeof(path),"%s/settings-font-%s-v1.hda",directory,s->name);if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=SF_OPEN(path);if(fd<0)return false;Uint8 *data=NULL;bool valid=false;
 unsigned size=s->plane*(s->mode?2:1);unsigned fields[15]={1,b,4,s->aw,s->ah,s->cw,s->ch,4,s->n,s->eligible,s->plane,s->mode?s->plane:0,s->mode,s->lo,s->hi};
 if(SF_FSTAT(fd,&st)||!SF_REGULAR(st.st_mode)||st.st_size!=128+size||SF_READ(fd,h,128)!=128||memcmp(h,"SFN1",4))goto done;
 for(unsigned i=0;i<15;i++)if(u32(h+4+4*i)!=fields[i])goto done;
 if(u64(h+64)!=SF_MAP||u64(h+72)!=s->metrics||u64(h+80)!=s->encoded||u64(h+88)!=s->eligibility||u64(h+96)!=SF_PAL||u64(h+104)!=s->payload||u64(h+112)||u64(h+120))goto done;
 data=malloc(size);if(!data||SF_READ(fd,data,size)!=(long)size||SF_READ(fd,&extra,1)!=0||hash(data,size)!=s->payload||!padding(b,data))goto done;valid=true;
 done:if(SF_CLOSE(fd))valid=false;if(valid)sf.payload[b]=data;else free(data);return valid;
}
/* Each immutable English label is optional on its own. Reject malformed or
 * unrecognized resources without dropping the underlying SFN1 lease. Bounds,
 * anchors, source provenance, text, role range and payload are all pinned. */
static void load_menu_run(unsigned r)
{
 const struct PfMenuSpec *s=&menu_spec[r];char path[1024];Uint8 h[128],extra;SF_STAT st;
 unsigned plane=s->w*s->h,size=plane*2;
 int n=snprintf(path,sizeof(path),"%s/shop-menu-run%u-v1.hda",directory,r);
 if(n<0||(size_t)n>=sizeof(path)||!s->w||!s->h||s->x+s->w+8>SF_OW||s->y+s->h+8>SF_OH||size>PF_MENU_BYTES)return;
 int fd=SF_OPEN(path);if(fd<0)return;Uint8 *data=NULL;bool valid=false;
 unsigned fields[15]={1,r,4,s->x,s->y,s->w,s->h,plane,plane,12,15,8,8,r?r+1:0,(unsigned)strlen(s->text)};
 if(SF_FSTAT(fd,&st)||!SF_REGULAR(st.st_mode)||st.st_size!=128+size||SF_READ(fd,h,128)!=128||memcmp(h,"SMR1",4))goto done;
 for(unsigned i=0;i<15;i++)if(u32(h+4+4*i)!=fields[i])goto done;
 if(u64(h+64)!=s->text_hash||u64(h+72)!=SF_MAP||u64(h+80)!=PF_BASE||u64(h+88)!=PF_PAL||u64(h+96)!=s->payload_hash||u64(h+104)||u64(h+112)||u64(h+120))goto done;
 data=malloc(size);if(!data||SF_READ(fd,data,size)!=(long)size||SF_READ(fd,&extra,1)!=0||hash(data,size)!=s->payload_hash)goto done;
 for(unsigned i=0;i<plane;i++)if(data[i]?(data[plane+i]<12||data[plane+i]>15):data[plane+i]!=0)goto done;
 valid=true;
 done:if(SF_CLOSE(fd))valid=false;if(valid)sf.menu_run[r]=data;else free(data);
}
/* A separately installed, optional skin. Failure affects only the metal, never
 * the accepted SFN1 font lease. Parse once, with exact provenance and bounds. */
static void load_metal(void)
{
 char path[1024];Uint8 h[128],extra,*data=NULL;SF_STAT st;bool valid=false;
 int n=snprintf(path,sizeof(path),"%s/shop-frame-metal-v1.hda",directory);
 if(n<0||(size_t)n>=sizeof(path))return;
 int fd=SF_OPEN(path);if(fd<0)return;
 const unsigned fields[15]={1,SF_W,SF_H,4,SF_OW,SF_OH,PF_METAL_RUNS,PF_METAL_PIXELS,PF_METAL_BYTES,4,1,0,0,0,0};
 if(SF_FSTAT(fd,&st)||!SF_REGULAR(st.st_mode)||st.st_size!=128+PF_METAL_BYTES||SF_READ(fd,h,128)!=128||memcmp(h,"PMF1",4))goto done;
 for(unsigned i=0;i<15;i++)if(u32(h+4+4*i)!=fields[i])goto done;
 if(u64(h+64)!=PF_BASE||u64(h+72)!=PF_PAL||u64(h+80)!=PF_METAL_HASH)goto done;
 for(unsigned i=88;i<128;i++)if(h[i])goto done;
 data=malloc(PF_METAL_BYTES);
 if(!data||SF_READ(fd,data,PF_METAL_BYTES)!=PF_METAL_BYTES||SF_READ(fd,&extra,1)!=0||hash(data,PF_METAL_BYTES)!=PF_METAL_HASH)goto done;
 unsigned offset=0,end=0,pixels=0;
 for(unsigned run=0;run<PF_METAL_RUNS;run++){
  if(offset>PF_METAL_BYTES-8)goto done;
  unsigned start=u32(data+offset),count=u32(data+offset+4);offset+=8;
  if(!count||start<end||start>=SF_OW*SF_OH||count>SF_OW-start%SF_OW||count>(PF_METAL_BYTES-offset)/4)goto done;
  for(unsigned i=0;i<count;i++)if(!data[offset+i*4+3])goto done;
  end=start+count;pixels+=count;offset+=count*4;
 }
 if(offset!=PF_METAL_BYTES||pixels!=PF_METAL_PIXELS)goto done;
 valid=true;
 done:if(SF_CLOSE(fd))valid=false;if(valid)sf.metal=data;else free(data);
}
/* Independently installed finite PSP1 siblings. All source identities and
 * dimensions are compile-time pins, including each one-cell contour bound. */
static Uint8 *shop_sprite_payload(unsigned slot)
{return slot?sf.shop_front:sf.shop_sprite;}
static int shop_sprite_slot(unsigned bank,unsigned id)
{for(unsigned i=0;i<PF_SHOP_SPRITES;i++)if(shop_spec[i].bank==bank&&shop_spec[i].id==id)return (int)i;return -1;}
static bool shop_sprite_source_item(unsigned slot,Uint8 *mask)
{
 const struct ShopSpriteSpec *sp=&shop_spec[slot];const Sprite *s=sprite(sp->bank,sp->id);Uint8 indices[PF_SPRITE_W*PF_SPRITE_H];unsigned cells=sp->w*sp->h;
 if(!s->data||s->width!=sp->w||s->height!=sp->h||s->size!=sp->rle_bytes||hash(s->data,s->size)!=sp->rle)return false;
 memset(indices,0,cells);memset(mask,0,cells);unsigned x=0,y=0;
 for(unsigned k=0;k<s->size;k++){
  unsigned v=s->data[k];if(y>=sp->h)return false;
  if(v==255){if(++k>=s->size)return false;x+=s->data[k];}
  else if(v==254)x=sp->w;else if(v==253)++x;
  else {if(x>=sp->w)return false;indices[y*sp->w+x]=v;mask[y*sp->w+x]=255;++x;}
  if(x>sp->w)return false;
  if(x==sp->w){x=0;++y;}
 }
 return !x&&y<=sp->h&&hash(indices,cells)==sp->index&&hash(mask,cells)==sp->mask;
}
static void load_shop_sprite_item(unsigned slot)
{
 const struct ShopSpriteSpec *sp=&shop_spec[slot];char path[1024];Uint8 h[128],extra,*data=NULL,mask[PF_SPRITE_W*PF_SPRITE_H];SF_STAT st;bool valid=false;
 int n=snprintf(path,sizeof(path),"%s/%s",directory,sp->name);
 if(n<0||(size_t)n>=sizeof(path))return;
 int fd=SF_OPEN(path);if(fd<0)return;
 const unsigned fields[15]={1,sp->bank,sp->id,sp->w,sp->h,4,sp->w*4,sp->h*4,sp->x,sp->y,sp->bytes,4,1,1,0};
 if(SF_FSTAT(fd,&st)||!SF_REGULAR(st.st_mode)||st.st_size!=128+sp->bytes||SF_READ(fd,h,128)!=128||memcmp(h,"PSP1",4))goto done;
 for(unsigned i=0;i<15;i++)if(u32(h+4+4*i)!=fields[i])goto done;
 if(u64(h+64)!=PF_BASE||u64(h+72)!=PF_PAL||u64(h+80)!=sp->rle||u64(h+88)!=sp->index||u64(h+96)!=sp->mask||u64(h+104)!=sp->payload||u64(h+112)||u64(h+120)||!shop_sprite_source_item(slot,mask))goto done;
 data=malloc(sp->bytes);
 if(!data||SF_READ(fd,data,sp->bytes)!=(long)sp->bytes||SF_READ(fd,&extra,1)!=0||hash(data,sp->bytes)!=sp->payload)goto done;
 for(unsigned p=0;p<sp->w*sp->h*16;p++){
  const Uint8 *v=data+p*4;if(!v[3]){if(v[0]||v[1]||v[2])goto done;continue;}
  int x=(int)(p%(sp->w*4))/4,y=(int)(p/(sp->w*4))/4;bool supported=false;
  for(int yy=MAX(0,y-1);yy<=MIN((int)sp->h-1,y+1);yy++)for(int xx=MAX(0,x-1);xx<=MIN((int)sp->w-1,x+1);xx++)if(mask[yy*sp->w+xx])supported=true;
  if(!supported)goto done;
 }
 valid=true;
 done:if(SF_CLOSE(fd))valid=false;if(valid){if(slot)sf.shop_front=data;else sf.shop_sprite=data;}else free(data);
}
static void load_shop_sprite(void){for(unsigned i=0;i<PF_SHOP_SPRITES;i++)load_shop_sprite_item(i);}
/* Shield is category 5. Trial pages deliberately retain their old OPTION[12]
 * left frame and the original PIC1 skin; no partial-coverage claim is made. */
static bool metal_visible(void){return sf.metal&&(!sf.product||sf.category==2||sf.category==5);}
static bool palette_matches(void)
{
 if(!main_window_tex_format||main_window_tex_format->BitsPerPixel!=32)return false;
 for(unsigned i=0;i<256;i++){SDL_Color c=sf.expected_palette[i];if(rgb_palette[i]!=SDL_MapRGB(main_window_tex_format,c.r,c.g,c.b))return false;}
 return true;
}
/* Original non-font banks remain independently authenticated. SFN1's palette7
 * header is provenance only; this lease's background and palette are PIC1/0. */
static bool classic_sources(void)
{
 static const unsigned counts[2]={47,22};
 static const uint64_t hashes[2]={UINT64_C(0xe68741eb7140c8fe),UINT64_C(0x4840d56707ef804a)};
 for(unsigned bank=5;bank<=6;bank++){
  if(sprite_table[bank].count!=counts[bank-5])return false;
  uint64_t h=SF_FNV;
  for(unsigned id=0;id<counts[bank-5];id++){
   const Sprite *s=sprite(bank,id);Uint8 exists=s->data!=NULL;h=hash_more(h,&exists,1);
   if(exists){h=hash16(hash16(hash16(h,s->width),s->height),s->size);h=hash_more(h,s->data,s->size);}
  }
  if(h!=hashes[bank-5])return false;
 }
 return shopSpriteSheet.data&&shopSpriteSheet.size==29941&&hash(shopSpriteSheet.data,shopSpriteSheet.size)==UINT64_C(0x8c478c429071f043);
}
static bool copy_text(char *dst,size_t size,const char *src,size_t capacity,bool capture)
{
 size_t n=0;while(n<capacity&&src[n])n++;
 if(!n||n==capacity||n>=size)return false;
 if(capture)memcpy(dst,src,n+1);else if(strcmp(dst,src))return false;return true;
}
static bool strings(bool capture)
{
 static const Uint8 help[2][8]={{1,34,2,3,4,5,0,0},{6,7,8,9,10,11,11,12}};
 for(unsigned row=0;row<sf.last;row++)if(!copy_text(sf.text[row],sizeof(sf.text[row]),menuInt[sf.menu+1][row],sizeof(menuInt[0][0]),capture))return false;
 for(unsigned row=0;row<sf.last-1;row++){
  if(menuHelp[sf.menu][row]!=help[sf.menu][row])return false;
  if(!copy_text(sf.footer[row],sizeof(sf.footer[row]),mainMenuHelp[help[sf.menu][row]-1],sizeof(mainMenuHelp[0]),capture))return false;
 }
 return true;
}
static bool acquire_surfaces(SDL_Surface *screen,SDL_Surface *backup)
{
 settings_font_end();load_font_end();selector_font_end();
 if(!geometry(screen)||!geometry(backup)||screen!=VGAScreen||screen!=VGAScreenSeg||backup!=VGAScreen2||palette_count<=7||palette_hash(palettes[7])!=SF_PAL||palette_hash(palettes[0])!=PF_PAL||palette_hash(colors)!=PF_PAL||!main_window_tex_format||main_window_tex_format->BitsPerPixel!=32||hash(backup->pixels,SF_N)!=PF_BASE||memcmp(screen->pixels,backup->pixels,SF_N)||!source(true)||!classic_sources())return false;
 for(unsigned b=0;b<3;b++)if(!load(b)){pregame_font_end();return false;}
 sf.output=malloc(SF_OUT_BYTES);if(!sf.output){pregame_font_end();return false;}
 sf.screen=screen;sf.backup=backup;sf.pixels=screen->pixels;sf.backup_pixels=backup->pixels;sf.format=screen->format;sf.backup_format=backup->format;
 memcpy(sf.base,backup->pixels,SF_N);memcpy(sf.expected,sf.base,SF_N);
 for(unsigned i=0;i<256;i++)SDL_GetRGB(rgb_palette[i],main_window_tex_format,&sf.expected_palette[i].r,&sf.expected_palette[i].g,&sf.expected_palette[i].b);
 bool pic=true,black=true;
 for(unsigned i=0;i<256;i++){
  SDL_Color c=sf.expected_palette[i],p=palettes[0][i];
  if(c.r!=p.r||c.g!=p.g||c.b!=p.b)pic=false;
  if(c.r||c.g||c.b)black=false;
 }
 if(!pic&&!black){pregame_font_end();return false;}
 sf.metal_gain=pic?255:0;load_metal();load_shop_sprite();
 sf.active=sf.frame=true;sf.stage=S_BUILD;sf.generation=sf.frame_generation=1;
 return true;
}
void pregame_font_begin(unsigned menu,unsigned selected,unsigned last,bool ordinary,unsigned long cash,unsigned cubes,SDL_Surface *screen,SDL_Surface *backup)
{
 pregame_font_end();
 if(menu>1||!ordinary||last!=(menu?9u:7u)||selected<2||selected>last||cubes>4||!directory)return;
 if(!acquire_surfaces(screen,backup))return;
 sf.menu=menu;sf.selected=selected;sf.last=last;sf.cubes=cubes;
 if(!strings(true)){pregame_font_end();return;}
 if(!menu)for(unsigned r=0;r<7;r++)load_menu_run(r);
 snprintf(sf.cash,sizeof(sf.cash),"%lu",cash);
 sf.next_role=PREGAME_HEADING;sf.row=2;
}
void pregame_font_product_begin(unsigned category,unsigned selected,unsigned last,bool ordinary,SDL_Surface *screen,SDL_Surface *backup)
{
 pregame_font_end();
 /* At most five item rows plus Done fit above the original footer. */
 if(!ordinary||category<2||category>8||last<3||last>7||selected<2||selected>last||!directory)return;
 if(!acquire_surfaces(screen,backup))return;
 sf.product=true;sf.menu=4;sf.category=category;sf.selected=selected;sf.last=last;
}
static bool check(void)
{
 if(!sf.active||!sf.frame)return false;
 if(!layout()){pregame_font_end();return false;}
 if(sf.frame_generation!=sf.generation){reject();return false;}return true;
}
static bool exact(void)
{
 if(!check())return false;
 if(!source(false)||!classic_sources()||(!sf.product&&!strings(false))||palette_count<=7||palette_hash(palettes[0])!=PF_PAL||palette_hash(palettes[7])!=SF_PAL||memcmp(sf.backup_pixels,sf.base,SF_N)){pregame_font_end();return false;}
 if(memcmp(sf.pixels,sf.expected,SF_N)){reject();return false;}return true;
}
static Uint8 shade(Uint8 v){return (v&240)|((v&15)/2);}
/* JE_dString and DARKEN both use unsafe OR, including negative overflow. */
static Uint8 face(unsigned r,unsigned hue,int value){return (Uint8)((hue<<4)|((int)r+value));}
static bool box(int x,int y,int w,int h){return x>=0&&y>=0&&w>0&&h>0&&x<=SF_W-w&&y<=SF_H-h;}
static struct SfCommand *append(unsigned kind,int x,int y,unsigned b,unsigned id,unsigned hue,int value)
{
 if(sf.count==SF_COMMANDS){reject();return NULL;}
 struct SfCommand *c=&sf.commands[sf.count++];memset(c,0,sizeof(*c));c->kind=kind;c->x=x;c->y=y;c->bank=b;c->id=id;c->hue=hue;c->value=value;c->cash=(kind==C_DARK||kind==C_FACE)&&sf.product&&sf.run_role==PREGAME_CASH;
 if(kind==C_DARK||kind==C_FACE){const struct SfGlyph *g=glyph(b,id);if(!box(x,y,g->w,g->h)){reject();return NULL;}c->w=g->w;c->h=g->h;}
 else {c->first=sf.event_count;if(kind==C_SPRITE){int slot=shop_sprite_slot(b,id);if(slot<0){reject();return NULL;}c->w=shop_spec[slot].w;c->h=shop_spec[slot].h;}}
 return c;
}
/* Product data is supplied by the original draws. Geometry, draw mode and
 * every glyph/write are checked; names and live amounts are not frozen. */
static bool digits(const char *text,bool sign)
{
 if(sign&&*text=='-')++text;
 if(!*text)return false;
 for(;*text;text++)if(*text<'0'||*text>'9')return false;
 return true;
}
static bool product_run(enum PregameRun role,unsigned row,int x,int y,const char *text,unsigned font,unsigned hue,int value)
{
 if(sf.stage!=S_BUILD||sf.glyph||!text)return false;
 size_t length=0;while(length<66&&text[length])++length;
 if(!length||length==66)return false;
 bool selected=row+1==sf.selected;
 switch(role){
 case PREGAME_HEADING:
  if(sf.updating||sf.heading||row||font!=0||hue!=15||value!=-3||y!=10||x!=234-JE_textWidth(text,0)/2||strcmp(text,menuInt[2][sf.category-1]))return false;
  sf.heading=true;break;
 case PREGAME_PRODUCT_NAME:
 case PREGAME_PRODUCT_COST:
  if(sf.updating||!sf.heading||row<1||row>=sf.last||font!=2||y!=40+(int)(row-1)*26+(role==PREGAME_PRODUCT_COST?10:0)||x!=(role==PREGAME_PRODUCT_COST?187:185)||hue!=(selected?0u:1u)||(value!=(selected?7:4)&&value!=(selected?3:0)))return false;
  if(role==PREGAME_PRODUCT_NAME){if(sf.names&(1u<<row))return false;sf.names|=1u<<row;}
  else {if(row==sf.last-1||(sf.costs&(1u<<row))||strncmp(text,"Cost: ",6)||!digits(text+6,false))return false;sf.costs|=1u<<row;}
  break;
 case PREGAME_CASH:
  if(row||font!=2||x!=65||y!=173||hue!=1||value!=6||length>=sizeof(sf.cash)||!digits(text,true)||sf.cash_seen)return false;
  sf.cash_seen=true;sf.cash_first=sf.count;break;
 case PREGAME_FOOTER:
  if(sf.updating||sf.product_footer||row!=sf.selected||font!=2||x!=10||y!=187||hue!=14||value!=1||(strcmp(text,mainMenuHelp[23])&&strcmp(text,mainMenuHelp[11])&&strcmp(text,mainMenuHelp[18])))return false;
  sf.product_footer=true;break;
 case PREGAME_POWER:
  if(!sf.updating||font!=2||y!=137||value!=4||row>3)return false;
  if(row==0){if(x!=26||hue!=1||!digits(text,false))return false;}
  else if(row==1){if(x!=108||(hue!=1&&hue!=7)||!digits(text,false))return false;}
  else if(row==2){size_t n=strlen(miscTextB[5]);if(x!=58||hue!=15||strncmp(text,miscTextB[5],n)||text[n]!=' '||!digits(text+n+1,false))return false;}
  else if(sf.category!=4||x!=28||hue!=1||strcmp(text,miscText[70]))return false;
  break;
 default:return false;
 }
 return true;
}
void pregame_font_run_begin(enum PregameRun role,unsigned row,SDL_Surface *surface,int x,int y,const char *text,unsigned font,unsigned hue,int value)
{
 if(!exact())return;
 if(sf.product){
  if(surface!=sf.screen||!product_run(role,row,x,y,text,font,hue,value)){reject();return;}
 }else {
 if(sf.stage!=S_BUILD||sf.primitive||surface!=sf.screen||!text||role!=sf.next_role){reject();return;}
 unsigned b=role==PREGAME_HEADING?0:role==PREGAME_ROW?1:2,eh=role==PREGAME_CASH?1:role==PREGAME_FOOTER?14:15;
 int ex=role==PREGAME_HEADING?234-JE_textWidth(sf.text[0],0)/2:role==PREGAME_ROW?166:role==PREGAME_CASH?65:10;
 int ey=role==PREGAME_HEADING?10:role==PREGAME_ROW?38+(sf.row-2)*16+(!sf.menu&&sf.row==7?16:0):role==PREGAME_CASH?173:187;
 int ev=role==PREGAME_CASH?6:role==PREGAME_FOOTER?1:-3;char selected[20];const char *wanted;
 if(role==PREGAME_ROW){if(row!=sf.row){reject();return;}snprintf(selected,sizeof(selected),"%s%s",row==sf.selected?"~":"",sf.text[row-1]);wanted=selected;}
 else wanted=role==PREGAME_HEADING?sf.text[0]:role==PREGAME_CASH?sf.cash:sf.footer[sf.selected-2];
 if((role!=PREGAME_ROW&&row!=(role==PREGAME_FOOTER?sf.selected:0))||strcmp(text,wanted)||font!=b||x!=ex||y!=ey||hue!=eh||value!=ev){reject();return;}
 }
 unsigned b=sf.product?font:role==PREGAME_HEADING?0:role==PREGAME_ROW?1:2;
 sf.next=sf.count;sf.pixel=0;sf.run_role=role;
 bool shadow=role!=PREGAME_POWER;
 if(b==2&&shadow){++x;++y;}
 int v=value;bool highlight=false;
 for(unsigned i=0;text[i];i++){
  unsigned ch=(unsigned char)text[i];if(ch==' '){x+=6;continue;}
  if(ch=='~'){highlight=!highlight;v+=highlight?(b==2?4:2):-(b==2?4:2);continue;}
  int id=font_ascii[ch];if(ch>=128||id<0||(unsigned)id>=spec[b].n||(b==2&&id>=86)||!glyph(b,id)->ink){reject();return;}
  if((shadow&&!append(C_DARK,x+(b==2?1:2),y+(b==2?1:2),b,id,0,0))||!append(C_FACE,x,y,b,id,hue,v))return;
  x+=glyph(b,id)->w+1;
 }
 sf.limit=sf.count;sf.stage=S_RUN;++sf.run_count;
 /* The original commands above remain the sole indexed proof. Only these
  * exact root labels may suppress their old HD glyphs; '~' is selection. */
 if(!sf.product&&!sf.menu&&(role==PREGAME_HEADING||role==PREGAME_ROW)){
  unsigned r=role==PREGAME_HEADING?0:row-1;const char *plain=*text=='~'?text+1:text;
  if(r<7&&sf.menu_run[r]&&!strcmp(plain,menu_spec[r].text))
   for(unsigned k=sf.next;k<sf.limit;k++)sf.commands[k].menu_run=r+1;
 }
}
void pregame_font_run_end(void)
{
 if(!exact())return;
 if(sf.stage!=S_RUN||sf.glyph||sf.next!=sf.limit){reject();return;}
 if(sf.product){if(sf.run_role==PREGAME_CASH)sf.cash_limit=sf.count;sf.stage=S_BUILD;return;}
 switch(sf.run_role){
 case PREGAME_HEADING:sf.next_role=PREGAME_ROW;break;
 case PREGAME_ROW:if(++sf.row>sf.last)sf.next_role=sf.menu?PREGAME_CASH:PREGAME_CUBES;break;
 case PREGAME_CASH:sf.next_role=PREGAME_BARS;break;
 case PREGAME_FOOTER:sf.next_role=99;break;
 default:reject();return;
 }
 sf.stage=S_BUILD;
}
static bool event(unsigned x,unsigned y,unsigned index,unsigned style)
{
 if(x>=SF_W||y>=SF_H||sf.event_count==SF_EVENTS){reject();return false;}
 struct SfEvent *e=&sf.events[sf.event_count++];e->position=y*SF_W+x;e->index=index;e->style=style;return true;
}
static void product_pixel(unsigned p,unsigned index,unsigned style)
{
 if(sf.stage!=S_BUILD||(sf.updating&&(p%SF_W>=154||p/SF_W>=185))||(style!=0&&style!=2)){reject();return;}
 struct SfCommand *c;
 if(sf.count&&(!sf.updating||sf.count>sf.static_count)&&sf.commands[sf.count-1].kind==C_CLASSIC)c=&sf.commands[sf.count-1];
 else {
  c=append(C_CLASSIC,0,0,0,0,0,0);if(!c)return;
  /* No fonts intervene in a classic command, so only its last write at each
   * pixel matters. Reuse render scratch for a 16-bit relative event index. */
  memset(sf.owner,0,SF_N);memset(sf.replay,0,SF_N);
 }
 unsigned n=sf.owner[p]|((unsigned)sf.replay[p]<<8);
 if(n){struct SfEvent *e=&sf.events[c->first+n-1];e->index=index;e->style=style;}
 else {
  if(!event(p%SF_W,p/SF_W,index,style))return;
  n=++c->events;sf.owner[p]=n;sf.replay[p]=n>>8;
 }
 sf.expected[p]=index;sf.next=sf.limit=sf.count;
}
void pregame_font_product_update_begin(void)
{
 if(!sf.product||!exact())return;
 if(sf.stage!=S_READY||sf.cursor||sf.updating){reject();return;}
 sf.count=sf.static_count;sf.event_count=sf.static_events;
 sf.next=sf.limit=sf.count;sf.cash_seen=false;sf.updating=true;sf.stage=S_BUILD;
}
void pregame_font_product_update_end(void)
{
 if(!sf.product||!exact())return;
 if(!sf.updating||sf.stage!=S_BUILD||!sf.cash_seen||sf.glyph){reject();return;}
 sf.updating=false;sf.stage=S_READY;
}
static bool rect_events(unsigned x,unsigned y,unsigned w,unsigned h,int index)
{
 if(!box(x,y,w,h)){reject();return false;}
 for(unsigned yy=y;yy<y+h;yy++)for(unsigned xx=x;xx<x+w;xx++){
  /* Prior predicted writes within the same bars bracket are replayed locally. */
  unsigned p=yy*SF_W+xx;Uint8 v=index<0?shade(sf.replay[p]):(Uint8)index;
  if(!event(xx,yy,v,index<0?2:0))return false;
  sf.replay[p]=v;
 }return true;
}
static bool bar_events(unsigned x,unsigned res,unsigned amount)
{
 if(amount>255){reject();return false;}
 for(unsigned z=0;z<amount/res;z++,x+=3)
  if(!rect_events(x+2,154,2,13,-1)||!rect_events(x,152,2,13,26)||!rect_events(x,152,2,1,27)||!rect_events(x,152,1,1,29)||!rect_events(x,164,2,1,25))return false;
 if(amount%res)if(!rect_events(x+2,154,2,13,-1)||!rect_events(x,152,2,13,14+(12/res)*(amount%res)))return false;
 return true;
}
void pregame_font_phase_begin(enum PregamePhase phase,unsigned armor,unsigned shield)
{
 if(sf.product)return;
 if(!exact())return;
 if(sf.stage!=S_BUILD||sf.primitive||sf.next_role!=(unsigned)phase){reject();return;}
 sf.stage=S_PRIMITIVE;sf.phase=phase;sf.phase_count=0;sf.ship_shield=false;if(phase==PREGAME_SHIP)sf.illustration=0;
 if(phase==PREGAME_BARS){
  struct SfCommand *c=append(C_CLASSIC,0,0,0,0,0,0);if(!c)return;memcpy(sf.replay,sf.expected,SF_N);
  if(!bar_events(42,3,armor)||!bar_events(104,2,shield))return;
  c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;
 }
}
void pregame_font_phase_end(void)
{
 if(sf.product)return;
 if(!exact())return;
 if(sf.stage!=S_PRIMITIVE||sf.glyph||sf.event_next!=sf.event_limit||(sf.phase==PREGAME_BARS?!sf.primitive:sf.primitive)||
    (sf.phase==PREGAME_CUBES&&sf.phase_count!=2*sf.cubes)||(sf.phase==PREGAME_SHIP&&(!sf.ship_shield||sf.phase_count<3))){reject();return;}
 sf.primitive=false;sf.next=sf.limit=sf.count;sf.next_role=sf.phase==PREGAME_CUBES?PREGAME_CASH:sf.phase==PREGAME_BARS?PREGAME_SHIP:PREGAME_FOOTER;sf.stage=S_BUILD;
}
static void skip_transparent(void)
{
 const struct SfCommand *c=&sf.commands[sf.next];const struct SfGlyph *g=glyph(c->bank,c->id);
 while(sf.pixel<c->w*c->h&&sf.masks[g->mask+sf.pixel]==255)++sf.pixel;
}
static bool shop_illustration_scope(SDL_Surface *surface)
{return surface==sf.screen&&(!sf.product?(sf.stage==S_PRIMITIVE&&sf.phase==PREGAME_SHIP):(!sf.updating&&(sf.stage==S_BUILD||sf.stage==S_PRIMITIVE)&&(sf.category==2||sf.category==5)));}
static bool shop_sprite_match(int x,int y,unsigned bank,unsigned id,unsigned op)
{
 int slot=shop_sprite_slot(bank,id);if(slot<0||!shop_sprite_payload(slot)||op!=PREGAME_ORIGINAL)return false;
 const struct ShopSpriteSpec *sp=&shop_spec[slot];
 if(x!=(int)sp->x||y!=(int)sp->y||!shop_illustration_scope(sf.screen))return false;
 return slot==0||sf.illustration==2;
}
/* Read only the original ordered blit calls, independently of installed art.
 * Before the known Talon hull, no assembly identity is assumed. A generator
 * of any supported original type advances to the first weapon call; rear
 * reuse of a front shape is therefore never selected by index alone. */
static void shop_illustration_observe(SDL_Surface *surface,int x,int y,unsigned bank,unsigned id,unsigned op)
{
 if(!shop_illustration_scope(surface)||op!=PREGAME_ORIGINAL)return;
 if(bank==5&&id>=27&&id<=45)sf.illustration=id==31&&x==35&&y==33?1:0;
 else if(bank==6&&sf.illustration==1){
  static const int gx[5]={62,64,67,66,63},gy[5]={84,85,86,84,97};
  sf.illustration=id>=16&&id<=20&&x==gx[id-16]&&y==gy[id-16]?2:0;
 }
 else if(bank==6&&sf.illustration==2)sf.illustration=3;
}
static bool classic_begin(SDL_Surface *surface,int x,int y,unsigned bank,unsigned id,unsigned op,unsigned hue,int value)
{
 if(!exact())return false;
 bool replacement=shop_sprite_match(x,y,bank,id,op);
 if(sf.primitive||surface!=sf.screen||(bank!=5&&bank!=6)||id>=sprite_table[bank].count){reject();return false;}
 if(sf.product){if(sf.stage!=S_BUILD||!replacement){reject();return false;}}
 else if(sf.stage!=S_PRIMITIVE){reject();return false;}
 else if(sf.phase==PREGAME_CUBES){
  bool dark=(sf.phase_count%2)==0;unsigned cube=sf.phase_count/2+1;
  if(cube>sf.cubes||bank!=5||id!=34||op!=(dark?PREGAME_DARK:PREGAME_ORIGINAL)||x!=190+(int)cube*18+(dark?2:0)||y!=(dark?38:37)){reject();return false;}
 }else if(sf.phase==PREGAME_SHIP){
  if(sf.ship_shield||(op!=PREGAME_ORIGINAL&&op!=PREGAME_FACE)||(op==PREGAME_FACE&&(bank!=5||id!=26||hue!=15||x!=28||y!=23))||(!sf.phase_count&&(bank!=5||id<27||id>45))||(sf.phase_count==1&&(bank!=6||id<16||id>20))){reject();return false;}
  if(op==PREGAME_FACE)sf.ship_shield=true;
 }else {reject();return false;}
 const Sprite *s=sprite(bank,id);if(!s->data||!box(x,y,s->width,s->height)||((sf.product||sf.phase==PREGAME_SHIP)&&(x+s->width>154||y+s->height>150))){reject();return false;}
 struct SfCommand *c=append(replacement?C_SPRITE:C_CLASSIC,x,y,bank,id,0,0);if(!c)return false;
 unsigned xx=0,yy=0;
 for(unsigned k=0;k<s->size;k++){
  unsigned v=s->data[k];if(yy>=s->height){reject();return false;}
  if(v==255){if(++k>=s->size){reject();return false;}xx+=s->data[k];}
  else if(v==254)xx=s->width;else if(v==253)++xx;
  else{
   if(xx>=s->width){reject();return false;}
   Uint8 index=v;
   if(op==PREGAME_DARK)index=shade(sf.expected[(y+yy)*SF_W+x+xx]);
   else if(op==PREGAME_FACE){Uint8 tone=(v&15)+value;if(tone>15)tone=tone>=31?0:15;index=(hue<<4)|tone;}
   if(!event(x+xx,y+yy,index,op==PREGAME_DARK?2:0))return false;
   ++xx;
  }
  if(xx>s->width){reject();return false;}if(xx==s->width){xx=0;++yy;}
 }
 if(xx||yy>s->height){reject();return false;}
 c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;sf.stage=S_PRIMITIVE;return true;
}
void pregame_font_glyph_begin(SDL_Surface *surface,int x,int y,unsigned font,unsigned id,enum PregameGlyph op,unsigned hue,int value)
{
 if(!check())return;
 if(sf.product&&font>=3){if(shop_sprite_match(x,y,font,id,op))classic_begin(surface,x,y,font,id,op,hue,value);if(sf.frame)shop_illustration_observe(surface,x,y,font,id,op);return;}
 if(font>=3){classic_begin(surface,x,y,font,id,op,hue,value);if(sf.frame)shop_illustration_observe(surface,x,y,font,id,op);return;}
 if(sf.stage!=S_RUN||sf.glyph||sf.next>=sf.limit||surface!=sf.screen){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];unsigned want=c->kind==C_DARK?PREGAME_DARK:PREGAME_UNSAFE;
 if(c->x!=x||c->y!=y||c->bank!=font||c->id!=id||op!=want||(c->kind==C_FACE&&(hue!=c->hue||value!=c->value))){reject();return;}
 sf.glyph=true;sf.pixel=0;skip_transparent();
}
void pregame_font_glyph_end(void)
{
 if(!check())return;
 if(sf.product&&sf.stage==S_BUILD)return;
 if(sf.stage==S_PRIMITIVE){
  if(!sf.primitive||sf.phase==PREGAME_BARS||sf.event_next!=sf.event_limit){reject();return;}
  sf.primitive=false;if(sf.product){sf.stage=S_BUILD;sf.next=sf.limit=sf.count;}else ++sf.phase_count;return;
 }
 if(sf.stage!=S_RUN||!sf.glyph||sf.next>=sf.limit||sf.pixel!=sf.commands[sf.next].w*sf.commands[sf.next].h){reject();return;}
 ++sf.next;sf.pixel=0;sf.glyph=false;
}
void pregame_font_sprite2_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned id)
{
 if(sf.product)return;
 if(!exact())return;
 if(sf.stage!=S_PRIMITIVE||sf.phase!=PREGAME_SHIP||sf.primitive||sf.ship_shield||sf.phase_count<2||surface!=sf.screen||data!=shopSpriteSheet.data||size!=shopSpriteSheet.size||id<1||id>304||!box(x,y,12,14)||x+12>153||y+14>112){reject();return;}
 const Uint8 *bytes=data;unsigned off=bytes[(id-1)*2]|(bytes[(id-1)*2+1]<<8),xx=0,yy=0;
 struct SfCommand *c=append(C_CLASSIC,0,0,0,0,0,0);if(!c)return;
 for(unsigned k=off;;k++){
  if(k>=size||yy>14){reject();return;}unsigned v=bytes[k];if(v==15)break;
  unsigned fill=v>>4;xx+=v&15;
  if(!fill){if(xx!=12){reject();return;}++yy;xx=0;continue;}
  if(xx+fill>12||yy>=14||k+fill>=size){reject();return;}
  while(fill--){if(!event(x+xx,y+yy,bytes[++k],0))return;++xx;}
 }
 c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;
}
void pregame_font_sprite2_end(void){pregame_font_glyph_end();}
void pregame_font_pixel(SDL_Surface *surface,Uint8 *address,int style)
{
 if(!check())return;
 if(surface!=sf.screen){reject();return;}
 uintptr_t ptr=(uintptr_t)address,base=(uintptr_t)sf.pixels;if(ptr<base||ptr-base>=SF_N){reject();return;}unsigned p=ptr-base;
 if(sf.stage==S_CURSOR){
  if(style!=0||!sf.cursor_sprite||sf.cursor_next>=sf.cursor_events||sf.cursor_event[sf.cursor_next].position!=p||sf.cursor_event[sf.cursor_next].index!=*address){reject();return;}
  ++sf.cursor_next;sf.expected[p]=*address;sf.cursor_index[p]=*address;sf.cursor_mask[p]=1;return;
 }
 if(sf.product&&sf.stage==S_BUILD){product_pixel(p,*address,style);return;}
 if(sf.stage==S_PRIMITIVE){
  if(!sf.primitive||sf.event_next>=sf.event_limit){reject();return;}
  const struct SfEvent *e=&sf.events[sf.event_next];if(p!=e->position||style!=e->style||*address!=e->index){reject();return;}++sf.event_next;sf.expected[p]=*address;return;
 }
 if(sf.stage!=S_RUN||sf.next>=sf.limit||!sf.glyph){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];unsigned wanted=(c->y+sf.pixel/c->w)*SF_W+c->x+sf.pixel%c->w;
 bool dark=c->kind==C_DARK;if(p!=wanted||style!=(dark?2:0)){reject();return;}
 Uint8 v=dark?shade(sf.expected[p]):face(sf.masks[glyph(c->bank,c->id)->mask+sf.pixel],c->hue,c->value);
 if(*address!=v){reject();return;}sf.expected[p]=v;++sf.pixel;skip_transparent();
}
void pregame_font_rect(SDL_Surface *surface,const SDL_Rect *r)
{
 if(!check())return;
 if(sf.product){
  if(surface!=sf.screen||!r||!box(r->x,r->y,r->w,r->h)||sf.stage!=S_BUILD){reject();return;}
  for(int y=r->y;y<r->y+r->h&&sf.frame;y++)for(int x=r->x;x<r->x+r->w&&sf.frame;x++)product_pixel(y*SF_W+x,((Uint8 *)surface->pixels)[y*SF_W+x],0);
  return;
 }
 if(!r||!box(r->x,r->y,r->w,r->h)||sf.stage!=S_PRIMITIVE||sf.phase!=PREGAME_BARS||!sf.primitive){reject();return;}
 for(int y=r->y;y<r->y+r->h&&sf.frame;y++)for(int x=r->x;x<r->x+r->w&&sf.frame;x++)pregame_font_pixel(surface,(Uint8 *)surface->pixels+y*SF_W+x,0);
}
void pregame_font_frame_end(void)
{
 if(!exact())return;
 if(sf.product){
  unsigned rows=(1u<<sf.last)-2u;
  if(sf.stage!=S_BUILD||!sf.heading||!sf.product_footer||!sf.cash_seen||sf.names!=rows||sf.costs!=(rows&~(1u<<(sf.last-1)))||sf.glyph||sf.cash_limit<sf.cash_first||sf.cash_limit-sf.cash_first>64){reject();return;}
  /* Keep the cash run after the immutable page commands. Each simulation or
   * idle refresh replaces only this dynamic tail, avoiding stale long values. */
  struct SfCommand cash[64];unsigned n=sf.cash_limit-sf.cash_first;
  memcpy(cash,sf.commands+sf.cash_first,n*sizeof(*cash));
  memmove(sf.commands+sf.cash_first,sf.commands+sf.cash_limit,(sf.count-sf.cash_limit)*sizeof(*cash));
  memcpy(sf.commands+sf.count-n,cash,n*sizeof(*cash));
  sf.static_count=sf.count-n;sf.static_events=sf.event_count;sf.stage=S_READY;return;
 }
 if(sf.stage!=S_BUILD||sf.next_role!=99||sf.row!=sf.last+1||sf.run_count!=sf.last+2||sf.glyph||sf.primitive||sf.next!=sf.count){reject();return;}sf.stage=S_READY;
}
void pregame_font_cursor_begin(void)
{if(!exact())return;
 if(sf.stage!=S_READY||sf.cursor||sf.fade_remaining){reject();return;}memcpy(sf.pre_cursor,sf.expected,SF_N);memset(sf.cursor_mask,0,SF_N);sf.cursor=true;sf.cursor_quad=0;sf.cursor_sprite=false;sf.stage=S_CURSOR;}
/* Verify the exact four normal-pointer source tiles before observing writes.
 * This also rejects unrelated same-index writers during the cursor bracket. */
void pregame_font_cursor_sprite_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned id)
{
 if(!check())return;
 static const unsigned ids[4]={273,274,292,293};
 static const int dx[4]={0,12,0,12},dy[4]={0,0,14,14};
 if(sf.stage!=S_CURSOR||surface!=sf.screen||sf.cursor_sprite||sf.cursor_quad>=4||data!=shopSpriteSheet.data||size!=shopSpriteSheet.size||!data||size!=29941||hash(data,size)!=UINT64_C(0x8c478c429071f043)||id!=ids[sf.cursor_quad]){reject();return;}
 if(!sf.cursor_quad){if(x < -24||x>=320||y < -28||y>=200){reject();return;}sf.cursor_x=x;sf.cursor_y=y;}
 if(x!=sf.cursor_x+dx[sf.cursor_quad]||y!=sf.cursor_y+dy[sf.cursor_quad]){reject();return;}
 const Uint8 *bytes=data;unsigned off=bytes[(id-1)*2]|(bytes[(id-1)*2+1]<<8),xx=0,yy=0;
 sf.cursor_events=sf.cursor_next=0;
 for(unsigned k=off;;k++){
  if(k>=size||yy>14){reject();return;}unsigned v=bytes[k];if(v==15)break;
  unsigned fill=v>>4;xx+=v&15;
  if(!fill){if(xx!=12){reject();return;}++yy;xx=0;continue;}
  if(xx+fill>12||yy>=14||k+fill>=size){reject();return;}
  while(fill--){Uint8 color=bytes[++k];if(x+(int)xx>=0&&x+(int)xx<320&&y+(int)yy>=0&&y+(int)yy<200){
   if(sf.cursor_events==168){reject();return;}sf.cursor_event[sf.cursor_events].position=(y+yy)*320+x+xx;sf.cursor_event[sf.cursor_events++].index=color;
  }++xx;}
 }
 sf.cursor_sprite=true;
}
void pregame_font_cursor_sprite_end(void)
{
 if(!check())return;
 if(sf.stage!=S_CURSOR||!sf.cursor_sprite||sf.cursor_next!=sf.cursor_events){reject();return;}
 sf.cursor_sprite=false;++sf.cursor_quad;
}
void pregame_font_cursor_done(void)
{if(!exact())return;
 if(sf.stage!=S_CURSOR||sf.cursor_sprite||(sf.cursor_quad!=0&&sf.cursor_quad!=4)){reject();return;}sf.stage=S_CURSOR_DONE;}
void pregame_font_cursor_erased(void)
{
 if(!check())return;
 if(sf.stage!=S_CURSOR_DONE||!sf.cursor||memcmp(sf.pixels,sf.pre_cursor,SF_N)){reject();return;}
 memcpy(sf.expected,sf.pre_cursor,SF_N);memset(sf.cursor_mask,0,SF_N);sf.cursor=false;sf.stage=S_READY;
}
void pregame_font_fade_declare(int steps)
{
 if(!sf.active)return;
 if(steps!=10||sf.fade_declared||sf.fade_remaining||sf.cursor||!exact()||sf.stage!=S_READY){pregame_font_end();return;}
 sf.fade_declared=steps;
}
void pregame_font_fade_start(const SDL_Color *target,const SDL_Color *solid,unsigned first,unsigned last)
{
 if(!sf.active)return;
 bool incoming=target&&palette_hash(target)==PF_PAL;
 bool outgoing=solid&&!solid->r&&!solid->g&&!solid->b;
 if(sf.fade_declared!=10||first||last!=255||sf.cursor||sf.fade_remaining||(!incoming&&!outgoing)){pregame_font_end();return;}
 sf.fade_remaining=10;sf.fade_declared=0;sf.exiting=outgoing;
 sf.metal_target=incoming?255:0;
 for(unsigned i=0;i<256;i++)sf.fade_target[i]=incoming?target[i]:*solid;
}
void pregame_font_fade_step(int remaining,unsigned first,unsigned last)
{
 if(!sf.active)return;
 if(first||last!=255||remaining!=sf.fade_remaining||remaining<1||remaining>10){pregame_font_end();return;}
 for(unsigned i=0;i<256;i++){
  sf.expected_palette[i].r+=(int)(sf.fade_target[i].r-sf.expected_palette[i].r)/remaining;
  sf.expected_palette[i].g+=(int)(sf.fade_target[i].g-sf.expected_palette[i].g)/remaining;
  sf.expected_palette[i].b+=(int)(sf.fade_target[i].b-sf.expected_palette[i].b)/remaining;
 }
 if(!palette_matches()){pregame_font_end();return;}--sf.fade_remaining;
 sf.metal_gain=(unsigned)((int)sf.metal_gain+((int)sf.metal_target-(int)sf.metal_gain)/remaining);
}
/* Same premultiplied correlated-layer contract as the approved selectors. */
static Uint32 over(Uint32 dst,Uint32 color,unsigned alpha)
{
 unsigned inv=255-alpha,a=alpha+(((dst>>24)*inv+127)/255);Uint32 result=a<<24;
 for(unsigned shift=0;shift<=16;shift+=8){unsigned v=(((color>>shift)&255)*alpha+((dst>>shift)&255)*inv+127)/255;result|=v<<shift;}
 return result;
}
static void render_menu_run(unsigned r,bool shadow,SDL_Rect *support,int *right,int *bottom)
{
 const struct PfMenuSpec *s=&menu_spec[r];const Uint8 *data=sf.menu_run[r];
 unsigned x0=s->x+(shadow?8:0),y0=s->y+(shadow?8:0),plane=s->w*s->h;
 int value=-3+(r&&sf.selected==r+1?2:0);
 for(unsigned y=0;y<s->h;y++)for(unsigned x=0;x<s->w;x++){
  unsigned at=y*s->w+x,alpha=data[at];if(!alpha)continue;
  unsigned p=((y0+y)/4)*SF_W+(x0+x)/4;
  Uint8 v=shadow?shade(sf.replay[p]):face(data[plane+at],15,value);
  unsigned out=(y0+y)*SF_OW+x0+x;
  sf.output[out]=over(sf.output[out],sf.palette[v],alpha);sf.owner[p]=1;
 }
 if((int)x0<support->x)support->x=x0;
 if((int)y0<support->y)support->y=y0;
 if((int)(x0+s->w)>*right)*right=x0+s->w;
 if((int)(y0+s->h)>*bottom)*bottom=y0+s->h;
}
static SDL_Rect render(void)
{
 SDL_Rect support={SF_OW,SF_OH,0,0};int right=0,bottom=0;
 for(unsigned i=0;i<256;i++){SDL_Color p=sf.expected_palette[i];sf.palette[i]=((Uint32)p.r<<16)|((Uint32)p.g<<8)|p.b;}
 memcpy(sf.replay,sf.base,SF_N);memcpy(sf.underlay,sf.base,SF_N);memset(sf.output,0,SF_OUT_BYTES);memset(sf.owner,0,SF_N);memset(sf.metal_blocked,0,SF_N);sf.sprite_drawn=false;
 if(metal_visible()){
  unsigned offset=0;
  for(unsigned run=0;run<PF_METAL_RUNS;run++){
   unsigned start=u32(sf.metal+offset),count=u32(sf.metal+offset+4);offset+=8;
   for(unsigned i=0;i<count;i++,offset+=4){
    const Uint8 *v=sf.metal+offset;unsigned a=v[3];Uint32 color=0;
    for(unsigned c=0;c<3;c++)color|=((v[c]*sf.metal_gain+127)/255)<<(16-c*8);
    sf.output[start+i]=over(0,color,a);
   }
  }
  support.x=support.y=0;right=SF_OW;bottom=SF_OH;
 }
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];
  /* Shadow samples the true pre-run indexed scene. Face lands at the end of
   * that same run, before any later cube/classic writes can occlude it. */
  if(c->menu_run&&(!k||sf.commands[k-1].menu_run!=c->menu_run))render_menu_run(c->menu_run-1,true,&support,&right,&bottom);
  if(c->kind==C_SPRITE){
   int slot=shop_sprite_slot(c->bank,c->id);const Uint8 *data=shop_sprite_payload(slot);
   /* Replay the real indexed hull for verification and all later classic
    * arithmetic, but leave its actual pre-draw underlay untouched. In
    * particular, transparent authored samples never reveal the old hull. */
   for(unsigned i=c->first;i<c->first+c->events;i++){unsigned p=sf.events[i].position;sf.replay[p]=sf.events[i].index;sf.owner[p]=1;}
   for(unsigned y=0;y<c->h*4u;y++)for(unsigned x=0;x<c->w*4u;x++){
    const Uint8 *v=data+(y*c->w*4+x)*4;unsigned a=v[3];if(!a)continue;Uint32 color=0;
    for(unsigned ch=0;ch<3;ch++)color|=((v[ch]*sf.metal_gain+127)/255)<<(16-ch*8);
    unsigned out=(c->y*4+y)*SF_OW+c->x*4+x;sf.output[out]=over(sf.output[out],color,a);sf.owner[(c->y+y/4)*SF_W+c->x+x/4]=1;
   }
   if(c->x*4<support.x)support.x=c->x*4;
   if(c->y*4<support.y)support.y=c->y*4;
   if((c->x+c->w)*4>right)right=(c->x+c->w)*4;
   if((c->y+c->h)*4>bottom)bottom=(c->y+c->h)*4;
   sf.sprite_drawn=true;continue;
  }
  if(c->kind==C_CLASSIC){
   for(unsigned i=c->first;i<c->first+c->events;i++){
    const struct SfEvent *e=&sf.events[i];unsigned p=e->position;sf.replay[p]=sf.underlay[p]=e->index;
    sf.metal_blocked[p]=1;
    /* Original writes, including same-index writes, occlude authored support. */
    for(unsigned yy=0;yy<4;yy++)for(unsigned xx=0;xx<4;xx++)sf.output[((p/SF_W)*4+yy)*SF_OW+(p%SF_W)*4+xx]=0;
   }continue;
  }
  const struct SfSpec *s=&spec[c->bank];const struct SfGlyph *g=glyph(c->bank,c->id);
  unsigned ax=(c->id%16)*s->cw+4,ay=(c->id/16)*s->ch+4;
  if(c->x*4<support.x)support.x=c->x*4;
  if(c->y*4<support.y)support.y=c->y*4;
  if((c->x+c->w)*4>right)right=(c->x+c->w)*4;
  if((c->y+c->h)*4>bottom)bottom=(c->y+c->h)*4;
  if(!c->menu_run)for(unsigned y=0;y<c->h*4u;y++)for(unsigned x=0;x<c->w*4u;x++){
   unsigned at=(ay+y)*s->aw+ax+x;Uint8 alpha=sf.payload[c->bank][at];if(!alpha)continue;
   unsigned p=(c->y+y/4)*SF_W+c->x+x/4;
   Uint8 v=c->kind==C_DARK?shade(sf.replay[p]):face(c->bank==2?7:sf.payload[c->bank][s->plane+at],c->hue,c->value);
   unsigned out=(c->y*4+y)*SF_OW+c->x*4+x;sf.output[out]=over(sf.output[out],sf.palette[v],alpha);sf.owner[p]=1;
  }
  for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
   Uint8 role=sf.masks[g->mask+y*c->w+x];if(role==255)continue;unsigned p=(c->y+y)*SF_W+c->x+x;
   sf.replay[p]=c->kind==C_DARK?shade(sf.replay[p]):face(role,c->hue,c->value);sf.owner[p]=1;
  }
  if(c->menu_run&&(k+1==sf.count||sf.commands[k+1].menu_run!=c->menu_run))render_menu_run(c->menu_run-1,false,&support,&right,&bottom);
 }
 for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p])sf.replay[p]=sf.underlay[p]=sf.cursor_index[p];
 support.w=right-support.x;support.h=bottom-support.y;return support;
}
static bool replay_matches(void)
{
 for(unsigned p=0;p<SF_N;p++)if(sf.replay[p]!=sf.expected[p]){
  if(!sf.product)return false;
  /* JE_drawScore repeats DARKEN without erasing its old indexed shadow.
   * Admit that difference only at a current Cash glyph's original ink. */
  bool cash=false;unsigned x=p%SF_W,y=p/SF_W;
  for(unsigned k=0;k<sf.count&&!cash;k++){
   const struct SfCommand *c=&sf.commands[k];
   if(c->kind==C_CLASSIC||!c->cash||x<c->x||y<c->y||x>=c->x+c->w||y>=c->y+c->h)continue;
   cash=sf.masks[glyph(c->bank,c->id)->mask+(y-c->y)*c->w+x-c->x]!=255;
  }
  if(!cash)return false;
 }
 return true;
}
bool pregame_font_present(SDL_Renderer *renderer,SDL_Texture *reference,SDL_Surface *surface,const SDL_Rect *destination,bool foreign_owner)
{
 if(!exact())return false;
 if(foreign_owner){pregame_font_invalidate();return false;}
 if(sf.stage!=S_READY&&sf.stage!=S_CURSOR_DONE){reject();return false;}
 if(!renderer||surface!=sf.screen||!destination||!palette_matches()||scaler>=scalers_count||!scalers[scaler].scaler32){reject();return false;}
 SDL_Rect support=render();if(!replay_matches()){reject();return false;}
 SDL_Surface underlay=*sf.screen;underlay.pixels=sf.underlay;
 unsigned radius=scaler==0||scaler==1||scaler==4||scaler==7?0:1;
 if(metal_visible()||sf.sprite_drawn)return selector_font_output_present_smooth_guarded(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,sf.cursor_mask,radius,sf.metal_blocked);
 return selector_font_output_present(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,sf.cursor_mask,radius);
}
