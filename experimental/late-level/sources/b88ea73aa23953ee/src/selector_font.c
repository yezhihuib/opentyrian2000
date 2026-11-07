/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite startup-selector lease. Observes original indexed writes; never changes
 * menu state, source pixels, font metrics, or the normal presentation transform.
 */
#include "selector_font.h"
#include "hd_cursor.h"
#include "selector_font_output.h"
#include "settings_font.h"
#include "menus.h"
#include "episodes.h"
#include "load_font.h"
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
#define SF_BASE UINT64_C(0xed50daf064c720e4)
#define SF_FNV UINT64_C(14695981039346656037)
enum { SF_W=320,SF_H=200,SF_N=64000,SF_D=4,SF_OW=1280,SF_OH=800,
 SF_OUT_BYTES=4096000,SF_PAYLOAD=1622016,SF_COMMANDS=512,SF_GLYPHS=145,
 SF_MASK_BYTES=60*17*20+85*12*13,SF_CAP=8*1024*1024 };
enum { C_DARK,C_FACE };
enum { S_IDLE,S_BUILD,S_RUN,S_READY,S_CURSOR,S_CURSOR_DONE };
struct SfSpec { unsigned aw,ah,cw,ch,n,eligible,plane,mode,lo,hi,mw,mh; uint64_t metrics,encoded,eligibility,payload; const char *name; };
static const struct SfSpec spec[2]={
 {1216,384,76,96,60,53,466944,1,12,15,17,20,UINT64_C(0xb0a8226af36e025a),UINT64_C(0x5c12ed2dea448227),UINT64_C(0x5529cd3792b04378),UINT64_C(0x0501f2f573e8d9a5),"large"},
 {896,384,56,64,85,76,344064,1,12,15,12,13,UINT64_C(0xf0dec0f37828f1c4),UINT64_C(0x96f0e4e668876f23),UINT64_C(0xa3861b64f710cb1f),UINT64_C(0x08f9609583417c89),"medium"},
};
struct SfGlyph { const Uint8 *rle; Uint16 size,mask; Uint8 w,h,ink; };
struct SfCommand { Uint16 x,y,w,h; Uint8 kind,bank,id; Sint8 value; };
static struct {
 bool active,frame,glyph,cursor,initial_done,exiting,header_done;
 int stage,fade_remaining,fade_kind,fade_declared;
 unsigned context,selected,visible,disabled,row,header_count;
 unsigned count,next,limit,pixel,run_count,run_role;
 char text[7][31];
 bool cursor_sprite;unsigned cursor_quad,cursor_events,cursor_next;int cursor_x,cursor_y;
 struct { Uint16 position;Uint8 index; } cursor_event[168];
 SDL_Surface *screen,*backup; void *pixels,*backup_pixels;
 SDL_PixelFormat *format,*backup_format;
 unsigned generation,frame_generation;
 Uint8 underlay[SF_N],base[SF_N],cached_header[SF_N],expected[SF_N],replay[SF_N],owner[SF_N],pre_cursor[SF_N],cursor_index[SF_N],cursor_mask[SF_N];
 struct SfGlyph glyphs[SF_GLYPHS];Uint8 masks[SF_MASK_BYTES];
 struct SfCommand commands[SF_COMMANDS];
 SDL_Color expected_palette[256],fade_target[256];
 Uint32 palette[256];
 Uint8 *payload[2];Uint32 *output;
} sf;
static const char *directory;
size_t selector_font_static_bytes(void){return sizeof(sf);}
bool selector_font_owns_display(void){return sf.active;}
typedef char sf_budget_check[(sizeof(sf)+1200000+70000+SF_PAYLOAD+SF_OUT_BYTES+2*128+2048<=SF_CAP)?1:-1];
typedef char sf_command_check[(sizeof(struct SfCommand)<=16)?1:-1];
static uint64_t hash_more(uint64_t h,const Uint8 *p,size_t n)
{while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint64_t hash(const void *p,size_t n){return hash_more(SF_FNV,p,n);}
static uint64_t hash16(uint64_t h,unsigned v){Uint8 p[2]={(Uint8)v,(Uint8)(v>>8)};return hash_more(h,p,2);}
static uint32_t u32(const Uint8 *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const Uint8 *p){return u32(p)|((uint64_t)u32(p+4)<<32);}
static uint64_t palette_hash(const SDL_Color *p){uint64_t h=SF_FNV;for(unsigned i=0;i<256;i++){Uint8 b[3]={p[i].r,p[i].g,p[i].b};h=hash_more(h,b,3);}return h;}
static struct SfGlyph *glyph(unsigned bank,unsigned id){return &sf.glyphs[(bank==0?0:60)+id];}
static void reject(void){sf.frame=false;sf.glyph=false;sf.stage=S_IDLE;}
void selector_font_set_directory(const char *path){selector_font_end();directory=path&&*path?path:NULL;}
void selector_font_release_texture(void){selector_font_output_release();}
void selector_font_end(void){selector_font_release_texture();for(unsigned b=0;b<2;b++)free(sf.payload[b]);free(sf.output);memset(&sf,0,sizeof(sf));}
void selector_font_invalidate(void){if(sf.active){++sf.generation;reject();}selector_font_release_texture();}
void selector_font_table_reset(unsigned table){if(table<2)selector_font_end();}
static bool geometry(SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==SF_W&&s->h==SF_H&&s->pitch==SF_W&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&s->clip_rect.x==0&&s->clip_rect.y==0&&s->clip_rect.w==SF_W&&s->clip_rect.h==SF_H;}
static bool layout(void){return sf.screen==VGAScreen&&sf.screen==VGAScreenSeg&&sf.backup==VGAScreen2&&geometry(sf.screen)&&geometry(sf.backup)&&sf.screen->pixels==sf.pixels&&sf.backup->pixels==sf.backup_pixels&&sf.screen->format==sf.format&&sf.backup->format==sf.backup_format;}
static bool source(bool capture)
{
 uint64_t map=SF_FNV;unsigned offset=0;
 for(unsigned i=0;i<256;i++){uint32_t v=(uint32_t)font_ascii[i];Uint8 p[4]={(Uint8)v,(Uint8)(v>>8),(Uint8)(v>>16),(Uint8)(v>>24)};map=hash_more(map,p,4);}
 if(map!=SF_MAP)return false;
 for(unsigned b=0;b<2;b++){
  const struct SfSpec *s=&spec[b];uint64_t metrics=SF_FNV,encoded=SF_FNV,eligible=SF_FNV;
  if(sprite_table[b].count!=s->n)return false;

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
   Uint8 e=g->ink?255:0;eligible=hash_more(eligible,&e,1);
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
 return inked==s->eligible;
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
static bool palette_matches(void)
{
 if(!main_window_tex_format||main_window_tex_format->BitsPerPixel!=32)return false;
 for(unsigned i=0;i<256;i++){SDL_Color c=sf.expected_palette[i];if(rgb_palette[i]!=SDL_MapRGB(main_window_tex_format,c.r,c.g,c.b))return false;}
 return true;
}
static unsigned row_count(void){return sf.context==SELECTOR_DIFFICULTY?6:sf.context==SELECTOR_TIMED?3:5;}
static const char *source_text(unsigned row,size_t *capacity)
{
 switch(sf.context){
 case SELECTOR_GAMEPLAY:*capacity=sizeof(gameplay_name[0]);return gameplay_name[row];
 case SELECTOR_EPISODE:*capacity=sizeof(episode_name[0]);return episode_name[row];
 case SELECTOR_DIFFICULTY:*capacity=sizeof(difficulty_name[0]);return difficulty_name[row];
 case SELECTOR_TIMED:*capacity=sizeof(timed_battle_name[0]);return timed_battle_name[row];
 default:*capacity=0;return NULL;
 }
}
static bool strings(bool capture)
{
 for(unsigned row=0;row<=row_count();row++){
  size_t cap;const char *s=source_text(row,&cap);size_t n=0;
  if(!s)return false;
  while(n<cap&&s[n])n++;
  if(!n||n==cap||n>=sizeof(sf.text[0]))return false;
  if(capture)memcpy(sf.text[row],s,n+1);else if(strcmp(sf.text[row],s))return false;
 }
 return true;
}
void selector_font_begin(enum SelectorContext context,SDL_Surface *screen,SDL_Surface *backup)
{
 selector_font_end();settings_font_end();load_font_end();
 if(context>SELECTOR_TIMED||!directory||!geometry(screen)||!geometry(backup)||screen!=VGAScreen||screen!=VGAScreenSeg||backup!=VGAScreen2||palette_count<=7||palette_hash(palettes[7])!=SF_PAL||palette_hash(colors)!=SF_PAL||!main_window_tex_format||main_window_tex_format->BitsPerPixel!=32||hash(backup->pixels,SF_N)!=SF_BASE||!source(true))return;
 sf.context=context;if(!strings(true))return;
 for(unsigned b=0;b<2;b++)if(!load(b)){selector_font_end();return;}
 sf.output=malloc(SF_OUT_BYTES);if(!sf.output){selector_font_end();return;}
 sf.screen=screen;sf.backup=backup;sf.pixels=screen->pixels;sf.backup_pixels=backup->pixels;sf.format=screen->format;sf.backup_format=backup->format;
 memcpy(sf.base,backup->pixels,SF_N);memcpy(sf.expected,sf.base,SF_N);
 for(unsigned i=0;i<256;i++)SDL_GetRGB(rgb_palette[i],main_window_tex_format,&sf.expected_palette[i].r,&sf.expected_palette[i].g,&sf.expected_palette[i].b);
 sf.active=sf.frame=true;sf.stage=S_BUILD;sf.generation=sf.frame_generation=1;
}
static bool check(void)
{
 if(!sf.active||!sf.frame)return false;
 if(!layout()){selector_font_end();return false;}
 if(sf.frame_generation!=sf.generation){reject();return false;}return true;
}
static SDL_Surface *target(void){return sf.header_done?sf.screen:sf.backup;}
static bool exact(void)
{
 if(!check())return false;
 if(!source(false)||!strings(false)||palette_count<=7||palette_hash(palettes[7])!=SF_PAL||(sf.header_done&&memcmp(sf.backup_pixels,sf.cached_header,SF_N))){selector_font_end();return false;}
 if(memcmp(target()->pixels,sf.expected,SF_N)){reject();return false;}return true;
}
static Uint8 shade(Uint8 v){return (v&240)|((v&15)/2);}
static Uint8 face(unsigned r,int value){int v=(int)r+value;if(v<0)v=0;if(v>15)v=15;return 240|v;}
static bool box(int x,int y,int w,int h){return x>=0&&y>=0&&w>0&&h>0&&x<=SF_W-w&&y<=SF_H-h;}
static bool append(unsigned kind,int x,int y,unsigned b,unsigned id,int value)
{
 const struct SfGlyph *g=glyph(b,id);
 if(sf.count==SF_COMMANDS||!box(x,y,g->w,g->h)){reject();return false;}
 struct SfCommand *c=&sf.commands[sf.count++];c->kind=kind;c->x=x;c->y=y;c->w=g->w;c->h=g->h;c->bank=b;c->id=id;c->value=value;return true;
}
void selector_font_frame_begin(size_t selected,size_t visible)
{
 if(!sf.active||!sf.header_done)return;
 sf.frame=true;sf.frame_generation=sf.generation;
 if(!check())return;
 if(!source(false)||!strings(false)||memcmp(sf.backup_pixels,sf.cached_header,SF_N)){selector_font_end();return;}
 if(selected>=visible||visible>row_count()||(sf.context==SELECTOR_DIFFICULTY?visible<3:visible!=row_count())||sf.exiting||memcmp(sf.pixels,sf.cached_header,SF_N)){reject();return;}
 sf.selected=selected;sf.visible=visible;sf.disabled=sf.context==SELECTOR_GAMEPLAY?1u<<4:0;
 if(sf.context==SELECTOR_EPISODE)for(unsigned i=0;i<5;i++)if(!episodeAvail[i])sf.disabled|=1u<<i;
 memcpy(sf.expected,sf.cached_header,SF_N);memset(sf.owner,0,SF_N);memset(sf.cursor_mask,0,SF_N);
 sf.row=sf.run_count=0;sf.count=sf.next=sf.limit=sf.header_count;sf.pixel=0;sf.glyph=sf.cursor=false;sf.stage=S_BUILD;
}
void selector_font_run_begin(enum SelectorRun role,unsigned row,SDL_Surface *surface,int x,int y,const char *text,unsigned font,int alignment,unsigned hue,int value)
{
 if(!exact())return;
 if(sf.stage!=S_BUILD||surface!=target()||!text||role>(unsigned)SELECTOR_ROW||role!=(sf.header_done?SELECTOR_ROW:SELECTOR_HEADING)){reject();return;}
 bool heading=role==SELECTOR_HEADING;unsigned b=heading?0:1;
 if(heading?row!=0:row>=sf.visible||row!=sf.row){reject();return;}
 int ex=heading?160:sf.context==SELECTOR_EPISODE?20:160-JE_textWidth(sf.text[row+1],normal_font)/2;
 int ey=heading?20:sf.context==SELECTOR_EPISODE?50+30*(int)row:54+24*(int)row;
 int ev=heading?-3:-4+(row==sf.selected?2:0)-((sf.disabled&(1u<<row))?4:0);
 if((heading?row!=0:row!=sf.row||row>=sf.visible)||font!=b||alignment!=(heading?centered:left_aligned)||hue!=15||x!=ex||y!=ey||value!=ev||strcmp(text,sf.text[heading?0:row+1])){reject();return;}
 unsigned width=0,length=0;
 for(;text[length];length++){
  unsigned ch=(unsigned char)text[length];if(ch=='~')continue;if(ch==' '){width+=6;continue;}
  int id=font_ascii[ch];if(ch>=128||id<0||(unsigned)id>=spec[b].n||!glyph(b,id)->ink){reject();return;}width+=glyph(b,id)->w+1;
 }
 if(width>318){reject();return;}if(heading)x-=(int)width/2;
 sf.next=sf.count;sf.pixel=0;sf.run_role=role;
 for(unsigned pass=0;pass<2;pass++){
  int gx=x+(pass?0:2),gy=y+(pass?0:2),v=value;bool highlight=false;
  for(unsigned i=0;i<length;i++){
   unsigned ch=(unsigned char)text[i];if(ch==' '){gx+=6;continue;}
   if(ch=='~'){highlight=!highlight;v+=highlight?4:-4;continue;}
   unsigned id=font_ascii[ch];const struct SfGlyph *g=glyph(b,id);
   if(!append(pass?C_FACE:C_DARK,gx,gy,b,id,pass?v:0))return;
   gx+=g->w+1;
  }
 }
 sf.limit=sf.count;sf.stage=S_RUN;++sf.run_count;
}
void selector_font_run_end(void)
{
 if(!exact())return;
 if(sf.stage!=S_RUN||sf.glyph||sf.next!=sf.limit){reject();return;}
 if(sf.run_role==SELECTOR_HEADING){memcpy(sf.cached_header,sf.expected,SF_N);sf.header_count=sf.count;sf.header_done=true;sf.frame=false;}
 else ++sf.row;
 sf.stage=S_BUILD;
}
static void skip_transparent(void)
{
 const struct SfCommand *c=&sf.commands[sf.next];const struct SfGlyph *g=glyph(c->bank,c->id);
 while(sf.pixel<c->w*c->h&&sf.masks[g->mask+sf.pixel]==255)++sf.pixel;
}
void selector_font_glyph_begin(SDL_Surface *surface,int x,int y,unsigned font,unsigned id,enum SelectorGlyph op,unsigned hue,int value)
{
 if(!check())return;
 if(sf.stage!=S_RUN||sf.glyph||sf.next>=sf.limit||surface!=target()){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];
 unsigned want=c->kind==C_DARK?SELECTOR_DARK:SELECTOR_FACE;
 if(c->x!=x||c->y!=y||c->bank!=font||c->id!=id||op!=want||(c->kind==C_FACE&&(hue!=15||value!=c->value))){reject();return;}
 sf.glyph=true;sf.pixel=0;skip_transparent();
}
void selector_font_glyph_end(void)
{
 if(!check())return;
 if(sf.stage!=S_RUN||!sf.glyph||sf.next>=sf.limit){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];
 if(sf.pixel!=c->w*c->h){reject();return;}
 ++sf.next;sf.pixel=0;sf.glyph=false;
}
void selector_font_pixel(SDL_Surface *surface,Uint8 *address,int style)
{
 if(!sf.active||!sf.frame)return;
 if(!check())return;
 if(surface!=target()){reject();return;}
 uintptr_t ptr=(uintptr_t)address,base=(uintptr_t)target()->pixels;if(ptr<base||ptr-base>=SF_N){reject();return;}unsigned p=ptr-base;
 if(sf.stage==S_CURSOR){
  if(style!=0||!sf.cursor_sprite||sf.cursor_next>=sf.cursor_events||sf.cursor_event[sf.cursor_next].position!=p||sf.cursor_event[sf.cursor_next].index!=*address){reject();return;}
  ++sf.cursor_next;sf.expected[p]=*address;sf.cursor_index[p]=*address;sf.cursor_mask[p]=1;return;
 }
 if(sf.stage!=S_RUN||sf.next>=sf.limit||!sf.glyph){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];unsigned wanted=(c->y+sf.pixel/c->w)*SF_W+c->x+sf.pixel%c->w;
 bool dark=c->kind==C_DARK;if(p!=wanted||style!=(dark?2:0)){reject();return;}
 Uint8 v=dark?shade(sf.expected[p]):face(sf.masks[glyph(c->bank,c->id)->mask+sf.pixel],c->value);
 if(*address!=v){reject();return;}sf.expected[p]=v;++sf.pixel;skip_transparent();
}
void selector_font_rect(SDL_Surface *surface,const SDL_Rect *r)
{(void)surface;(void)r;if(sf.active&&sf.frame)reject();}
void selector_font_frame_end(void)
{
 if(!exact())return;
 if(sf.stage!=S_BUILD||sf.row!=sf.visible||sf.run_count!=sf.visible||sf.glyph||sf.next!=sf.count){reject();return;}sf.stage=S_READY;
}
void selector_font_cursor_begin(void)
{if(!exact())return;
 if(sf.stage!=S_READY||sf.cursor||sf.fade_remaining){reject();return;}memcpy(sf.pre_cursor,sf.expected,SF_N);memset(sf.cursor_mask,0,SF_N);sf.cursor=true;sf.cursor_quad=0;sf.cursor_sprite=false;sf.stage=S_CURSOR;}
/* Verify the exact four normal-pointer source tiles before observing writes.
 * This also rejects unrelated same-index writers during the cursor bracket. */
void selector_font_cursor_sprite_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned id)
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
void selector_font_cursor_sprite_end(void)
{
 if(!check())return;
 if(sf.stage!=S_CURSOR||!sf.cursor_sprite||sf.cursor_next!=sf.cursor_events){reject();return;}
 sf.cursor_sprite=false;++sf.cursor_quad;
}
void selector_font_cursor_done(void)
{if(!exact())return;
 if(sf.stage!=S_CURSOR||sf.cursor_sprite||(sf.cursor_quad!=0&&sf.cursor_quad!=4)){reject();return;}sf.stage=S_CURSOR_DONE;}
void selector_font_cursor_erased(void)
{
 if(!check())return;
 if(sf.stage!=S_CURSOR_DONE||!sf.cursor||memcmp(sf.pixels,sf.pre_cursor,SF_N)){reject();return;}
 memcpy(sf.expected,sf.pre_cursor,SF_N);memset(sf.cursor_mask,0,SF_N);sf.cursor=false;sf.stage=S_READY;
}
void selector_font_fade_declare(int steps)
{
 if(!sf.active)return;
 if(sf.fade_declared||sf.fade_remaining||(!sf.initial_done?steps!=10:(steps!=10&&steps!=15))){selector_font_end();return;}
 sf.fade_declared=steps;
}
void selector_font_fade_start(const SDL_Color *target,const SDL_Color *solid,unsigned first,unsigned last)
{
 if(!sf.active)return;
 if((!sf.initial_done?sf.fade_declared!=10:(sf.fade_declared!=10&&sf.fade_declared!=15))||first||last!=255||sf.cursor||sf.fade_remaining||(!target&&!solid)||(!sf.initial_done&&(!target||palette_hash(target)!=SF_PAL))||(sf.initial_done&&(!solid||solid->r||solid->g||solid->b))){selector_font_end();return;}
 sf.fade_kind=sf.initial_done?2:1;sf.fade_remaining=sf.fade_declared;sf.fade_declared=0;
 for(unsigned i=0;i<256;i++)sf.fade_target[i]=target?target[i]:*solid;
 if(sf.initial_done)sf.exiting=true;
}
void selector_font_fade_step(int remaining,unsigned first,unsigned last)
{
 if(!sf.active)return;
 if(first||last!=255||remaining!=sf.fade_remaining||remaining<1||remaining>(sf.fade_kind==1?10:15)){selector_font_end();return;}
 for(unsigned i=0;i<256;i++){
  sf.expected_palette[i].r+=(int)(sf.fade_target[i].r-sf.expected_palette[i].r)/remaining;
  sf.expected_palette[i].g+=(int)(sf.fade_target[i].g-sf.expected_palette[i].g)/remaining;
  sf.expected_palette[i].b+=(int)(sf.fade_target[i].b-sf.expected_palette[i].b)/remaining;
 }
 if(!palette_matches()){selector_font_end();return;}
 if(!--sf.fade_remaining)sf.initial_done=true;
}
/* The layer is premultiplied and transparent. All ordered operations are
 * composited at correlated canonical samples before output-footprint sampling.
 * Indexed replay supplies H(i); RGB and palette role indices are never mixed. */
static Uint32 over(Uint32 dst,Uint32 color,unsigned alpha)
{
 unsigned inv=255-alpha,a=alpha+(((dst>>24)*inv+127)/255);Uint32 result=a<<24;
 for(unsigned shift=0;shift<=16;shift+=8){unsigned v=(((color>>shift)&255)*alpha+((dst>>shift)&255)*inv+127)/255;result|=v<<shift;}
 return result;
}
static SDL_Rect render(void)
{
 SDL_Rect support={SF_OW,SF_OH,0,0};int right=0,bottom=0;
 for(unsigned i=0;i<256;i++){SDL_Color p=sf.expected_palette[i];sf.palette[i]=((Uint32)p.r<<16)|((Uint32)p.g<<8)|p.b;}
 memcpy(sf.replay,sf.base,SF_N);memcpy(sf.underlay,sf.base,SF_N);memset(sf.output,0,SF_OUT_BYTES);memset(sf.owner,0,SF_N);
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];const struct SfSpec *s=&spec[c->bank];const struct SfGlyph *g=glyph(c->bank,c->id);
  unsigned ax=(c->id%16)*s->cw+4,ay=(c->id/16)*s->ch+4;
  if(c->x*4<support.x)support.x=c->x*4;
  if(c->y*4<support.y)support.y=c->y*4;
  if((c->x+c->w)*4>right)right=(c->x+c->w)*4;
  if((c->y+c->h)*4>bottom)bottom=(c->y+c->h)*4;
  for(unsigned y=0;y<c->h*4u;y++)for(unsigned x=0;x<c->w*4u;x++){
   unsigned at=(ay+y)*s->aw+ax+x;Uint8 alpha=sf.payload[c->bank][at];if(!alpha)continue;
   unsigned p=(c->y+y/4)*SF_W+c->x+x/4;
   Uint8 v=c->kind==C_DARK?shade(sf.replay[p]):face(sf.payload[c->bank][s->plane+at],c->value);
   unsigned out=(c->y*4+y)*SF_OW+c->x*4+x;sf.output[out]=over(sf.output[out],sf.palette[v],alpha);sf.owner[p]=1;
  }
  for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
   Uint8 role=sf.masks[g->mask+y*c->w+x];if(role==255)continue;unsigned p=(c->y+y)*SF_W+c->x+x;
   sf.replay[p]=c->kind==C_DARK?shade(sf.replay[p]):face(role,c->value);sf.owner[p]=1;
  }
 }
 for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p]){sf.replay[p]=sf.cursor_index[p];if(!hd_cursor_active())sf.underlay[p]=sf.cursor_index[p];}
 support.w=right-support.x;support.h=bottom-support.y;return support;
}
bool selector_font_present(SDL_Renderer *renderer,SDL_Texture *reference,SDL_Surface *surface,const SDL_Rect *destination,bool foreign_owner)
{
 if(!exact())return false;
 if(foreign_owner){selector_font_invalidate();return false;}
 if(sf.stage!=S_READY&&sf.stage!=S_CURSOR_DONE){reject();return false;}
 if(!renderer||surface!=sf.screen||!destination||!palette_matches()||scaler>=scalers_count||!scalers[scaler].scaler32){reject();return false;}
 SDL_Rect support=render();if(memcmp(sf.replay,sf.expected,SF_N)){reject();return false;}
 SDL_Surface underlay=*sf.screen;underlay.pixels=sf.underlay;
 unsigned radius=scaler==0||scaler==1||scaler==4||scaler==7?0:1;
 return selector_font_output_present(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,hd_cursor_active()?NULL:sf.cursor_mask,radius);
}
