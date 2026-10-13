/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite PIC1 pre-game root/category lease. Original indexed work is untouched.
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
enum { SF_W=320,SF_H=200,SF_N=64000,SF_OW=1280,SF_OH=800,
 SF_OUT_BYTES=4096000,SF_PAYLOAD=1785856,SF_COMMANDS=1024,SF_GLYPHS=272,
 SF_MASK_BYTES=60*17*20+85*12*13+127*6*8,SF_EVENTS=40000,SF_CAP=9*1024*1024 };
enum { C_DARK,C_FACE,C_CLASSIC };
enum { S_IDLE,S_BUILD,S_RUN,S_PRIMITIVE,S_READY,S_CURSOR,S_CURSOR_DONE };
struct SfSpec { unsigned aw,ah,cw,ch,n,eligible,plane,mode,lo,hi,mw,mh; uint64_t metrics,encoded,eligibility,payload; const char *name; };
static const struct SfSpec spec[3]={
 {1216,384,76,96,60,53,466944,1,12,15,17,20,UINT64_C(0xb0a8226af36e025a),UINT64_C(0x5c12ed2dea448227),UINT64_C(0x5529cd3792b04378),UINT64_C(0x0501f2f573e8d9a5),"large"},
 {896,384,56,64,85,76,344064,1,12,15,12,13,UINT64_C(0xf0dec0f37828f1c4),UINT64_C(0x96f0e4e668876f23),UINT64_C(0xa3861b64f710cb1f),UINT64_C(0x08f9609583417c89),"medium"},
 {512,320,32,40,127,86,163840,0,7,7,6,8,UINT64_C(0x0908ca85cbf2a1e3),UINT64_C(0x2ed2973d82ce6f3d),UINT64_C(0x68e8c2bab3c43d0d),UINT64_C(0x85cddeb8bd7ea09a),"tiny"}
};
struct SfGlyph { const Uint8 *rle; Uint16 size,mask; Uint8 w,h,ink; };
struct SfCommand { Uint16 x,y,w,h; Uint8 kind,bank,id,hue; Sint16 value; unsigned first,events; };
struct SfEvent { Uint16 position; Uint8 index,style; };
static struct {
 bool active,frame,glyph,cursor,exiting,primitive,ship_shield;
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
 struct SfGlyph glyphs[SF_GLYPHS];Uint8 masks[SF_MASK_BYTES];
 struct SfCommand commands[SF_COMMANDS];struct SfEvent events[SF_EVENTS];
 SDL_Color expected_palette[256],fade_target[256];Uint32 palette[256];
 Uint8 *payload[3];Uint32 *output;
} sf;
static const char *directory;
size_t pregame_font_static_bytes(void){return sizeof(sf);}
bool pregame_font_owns_display(void){return sf.active;}
typedef char sf_budget_check[(sizeof(sf)+1800000+70000+SF_PAYLOAD+SF_OUT_BYTES+3*128+2048<=SF_CAP)?1:-1];
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
void pregame_font_end(void){pregame_font_release_texture();for(unsigned b=0;b<3;b++)free(sf.payload[b]);free(sf.output);memset(&sf,0,sizeof(sf));}
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
void pregame_font_begin(unsigned menu,unsigned selected,unsigned last,bool ordinary,unsigned long cash,unsigned cubes,SDL_Surface *screen,SDL_Surface *backup)
{
 pregame_font_end();
 if(menu>1||!ordinary||last!=(menu?9u:7u)||selected<2||selected>last||cubes>4||!directory)return;
 settings_font_end();load_font_end();selector_font_end();
 if(!geometry(screen)||!geometry(backup)||screen!=VGAScreen||screen!=VGAScreenSeg||backup!=VGAScreen2||palette_count<=7||palette_hash(palettes[7])!=SF_PAL||palette_hash(palettes[0])!=PF_PAL||palette_hash(colors)!=PF_PAL||!main_window_tex_format||main_window_tex_format->BitsPerPixel!=32||hash(backup->pixels,SF_N)!=PF_BASE||memcmp(screen->pixels,backup->pixels,SF_N)||!source(true)||!classic_sources())return;
 sf.menu=menu;sf.selected=selected;sf.last=last;sf.cubes=cubes;
 if(!strings(true))return;
 snprintf(sf.cash,sizeof(sf.cash),"%lu",cash);
 for(unsigned b=0;b<3;b++)if(!load(b)){pregame_font_end();return;}
 sf.output=malloc(SF_OUT_BYTES);if(!sf.output){pregame_font_end();return;}
 sf.screen=screen;sf.backup=backup;sf.pixels=screen->pixels;sf.backup_pixels=backup->pixels;sf.format=screen->format;sf.backup_format=backup->format;
 memcpy(sf.base,backup->pixels,SF_N);memcpy(sf.expected,sf.base,SF_N);
 for(unsigned i=0;i<256;i++)SDL_GetRGB(rgb_palette[i],main_window_tex_format,&sf.expected_palette[i].r,&sf.expected_palette[i].g,&sf.expected_palette[i].b);
 bool pic=true,black=true;
 for(unsigned i=0;i<256;i++){
  SDL_Color c=sf.expected_palette[i],p=palettes[0][i];
  if(c.r!=p.r||c.g!=p.g||c.b!=p.b)pic=false;
  if(c.r||c.g||c.b)black=false;
 }
 if(!pic&&!black){pregame_font_end();return;}
 sf.active=sf.frame=true;sf.stage=S_BUILD;sf.generation=sf.frame_generation=1;sf.next_role=PREGAME_HEADING;sf.row=2;
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
 if(!source(false)||!classic_sources()||!strings(false)||palette_count<=7||palette_hash(palettes[0])!=PF_PAL||palette_hash(palettes[7])!=SF_PAL||memcmp(sf.backup_pixels,sf.base,SF_N)){pregame_font_end();return false;}
 if(memcmp(sf.pixels,sf.expected,SF_N)){reject();return false;}return true;
}
static Uint8 shade(Uint8 v){return (v&240)|((v&15)/2);}
/* JE_dString and DARKEN both use unsafe OR, including negative overflow. */
static Uint8 face(unsigned r,unsigned hue,int value){return (Uint8)((hue<<4)|((int)r+value));}
static bool box(int x,int y,int w,int h){return x>=0&&y>=0&&w>0&&h>0&&x<=SF_W-w&&y<=SF_H-h;}
static struct SfCommand *append(unsigned kind,int x,int y,unsigned b,unsigned id,unsigned hue,int value)
{
 if(sf.count==SF_COMMANDS){reject();return NULL;}
 struct SfCommand *c=&sf.commands[sf.count++];memset(c,0,sizeof(*c));c->kind=kind;c->x=x;c->y=y;c->bank=b;c->id=id;c->hue=hue;c->value=value;
 if(kind!=C_CLASSIC){const struct SfGlyph *g=glyph(b,id);if(!box(x,y,g->w,g->h)){reject();return NULL;}c->w=g->w;c->h=g->h;}
 else c->first=sf.event_count;
 return c;
}
void pregame_font_run_begin(enum PregameRun role,unsigned row,SDL_Surface *surface,int x,int y,const char *text,unsigned font,unsigned hue,int value)
{
 if(!exact())return;
 if(sf.stage!=S_BUILD||sf.primitive||surface!=sf.screen||!text||role!=sf.next_role){reject();return;}
 unsigned b=role==PREGAME_HEADING?0:role==PREGAME_ROW?1:2,eh=role==PREGAME_CASH?1:role==PREGAME_FOOTER?14:15;
 int ex=role==PREGAME_HEADING?234-JE_textWidth(sf.text[0],0)/2:role==PREGAME_ROW?166:role==PREGAME_CASH?65:10;
 int ey=role==PREGAME_HEADING?10:role==PREGAME_ROW?38+(sf.row-2)*16+(!sf.menu&&sf.row==7?16:0):role==PREGAME_CASH?173:187;
 int ev=role==PREGAME_CASH?6:role==PREGAME_FOOTER?1:-3;char selected[20];const char *wanted;
 if(role==PREGAME_ROW){if(row!=sf.row){reject();return;}snprintf(selected,sizeof(selected),"%s%s",row==sf.selected?"~":"",sf.text[row-1]);wanted=selected;}
 else wanted=role==PREGAME_HEADING?sf.text[0]:role==PREGAME_CASH?sf.cash:sf.footer[sf.selected-2];
 if((role!=PREGAME_ROW&&row!=(role==PREGAME_FOOTER?sf.selected:0))||strcmp(text,wanted)||font!=b||x!=ex||y!=ey||hue!=eh||value!=ev){reject();return;}
 sf.next=sf.count;sf.pixel=0;sf.run_role=role;
 if(b==2){++x;++y;}
 int v=value;bool highlight=false;
 for(unsigned i=0;text[i];i++){
  unsigned ch=(unsigned char)text[i];if(ch==' '){x+=6;continue;}
  if(ch=='~'){highlight=!highlight;v+=highlight?(b==2?4:2):-(b==2?4:2);continue;}
  int id=font_ascii[ch];if(ch>=128||id<0||(unsigned)id>=spec[b].n||(b==2&&id>=86)||!glyph(b,id)->ink){reject();return;}
  if(!append(C_DARK,x+(b==2?1:2),y+(b==2?1:2),b,id,0,0)||!append(C_FACE,x,y,b,id,hue,v))return;
  x+=glyph(b,id)->w+1;
 }
 sf.limit=sf.count;sf.stage=S_RUN;++sf.run_count;
}
void pregame_font_run_end(void)
{
 if(!exact())return;
 if(sf.stage!=S_RUN||sf.glyph||sf.next!=sf.limit){reject();return;}
 switch(sf.run_role){
 case PREGAME_HEADING:sf.next_role=PREGAME_ROW;break;
 case PREGAME_ROW:if(++sf.row>sf.last)sf.next_role=sf.menu?PREGAME_CASH:PREGAME_CUBES;break;
 case PREGAME_CASH:sf.next_role=PREGAME_BARS;break;
 case PREGAME_FOOTER:sf.next_role=99;break;
 }
 sf.stage=S_BUILD;
}
static bool event(unsigned x,unsigned y,unsigned index,unsigned style)
{
 if(x>=SF_W||y>=SF_H||sf.event_count==SF_EVENTS){reject();return false;}
 struct SfEvent *e=&sf.events[sf.event_count++];e->position=y*SF_W+x;e->index=index;e->style=style;return true;
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
 if(!exact())return;
 if(sf.stage!=S_BUILD||sf.primitive||sf.next_role!=(unsigned)phase){reject();return;}
 sf.stage=S_PRIMITIVE;sf.phase=phase;sf.phase_count=0;sf.ship_shield=false;
 if(phase==PREGAME_BARS){
  struct SfCommand *c=append(C_CLASSIC,0,0,0,0,0,0);if(!c)return;memcpy(sf.replay,sf.expected,SF_N);
  if(!bar_events(42,3,armor)||!bar_events(104,2,shield))return;
  c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;
 }
}
void pregame_font_phase_end(void)
{
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
static bool classic_begin(SDL_Surface *surface,int x,int y,unsigned bank,unsigned id,unsigned op,unsigned hue,int value)
{
 if(!exact())return false;
 if(sf.stage!=S_PRIMITIVE||sf.primitive||surface!=sf.screen||(bank!=5&&bank!=6)||id>=sprite_table[bank].count){reject();return false;}
 if(sf.phase==PREGAME_CUBES){
  bool dark=(sf.phase_count%2)==0;unsigned cube=sf.phase_count/2+1;
  if(cube>sf.cubes||bank!=5||id!=34||op!=(dark?PREGAME_DARK:PREGAME_ORIGINAL)||x!=190+(int)cube*18+(dark?2:0)||y!=(dark?38:37)){reject();return false;}
 }else if(sf.phase==PREGAME_SHIP){
  if(sf.ship_shield||(op!=PREGAME_ORIGINAL&&op!=PREGAME_FACE)||(op==PREGAME_FACE&&(bank!=5||id!=26||hue!=15||x!=28||y!=23))||(!sf.phase_count&&(bank!=5||id<27||id>45))||(sf.phase_count==1&&(bank!=6||id<16||id>20))){reject();return false;}
  if(op==PREGAME_FACE)sf.ship_shield=true;
 }else {reject();return false;}
 const Sprite *s=sprite(bank,id);if(!s->data||!box(x,y,s->width,s->height)||(sf.phase==PREGAME_SHIP&&(x+s->width>154||y+s->height>150))){reject();return false;}
 struct SfCommand *c=append(C_CLASSIC,0,0,0,0,0,0);if(!c)return false;
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
 c->events=sf.event_count-c->first;sf.event_next=c->first;sf.event_limit=sf.event_count;sf.primitive=true;return true;
}
void pregame_font_glyph_begin(SDL_Surface *surface,int x,int y,unsigned font,unsigned id,enum PregameGlyph op,unsigned hue,int value)
{
 if(!check())return;
 if(font>=3){classic_begin(surface,x,y,font,id,op,hue,value);return;}
 if(sf.stage!=S_RUN||sf.glyph||sf.next>=sf.limit||surface!=sf.screen){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];unsigned want=c->kind==C_DARK?PREGAME_DARK:PREGAME_UNSAFE;
 if(c->x!=x||c->y!=y||c->bank!=font||c->id!=id||op!=want||(c->kind==C_FACE&&(hue!=c->hue||value!=c->value))){reject();return;}
 sf.glyph=true;sf.pixel=0;skip_transparent();
}
void pregame_font_glyph_end(void)
{
 if(!check())return;
 if(sf.stage==S_PRIMITIVE){
  if(!sf.primitive||sf.phase==PREGAME_BARS||sf.event_next!=sf.event_limit){reject();return;}
  sf.primitive=false;++sf.phase_count;return;
 }
 if(sf.stage!=S_RUN||!sf.glyph||sf.next>=sf.limit||sf.pixel!=sf.commands[sf.next].w*sf.commands[sf.next].h){reject();return;}
 ++sf.next;sf.pixel=0;sf.glyph=false;
}
void pregame_font_sprite2_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned id)
{
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
 if(!r||!box(r->x,r->y,r->w,r->h)||sf.stage!=S_PRIMITIVE||sf.phase!=PREGAME_BARS||!sf.primitive){reject();return;}
 for(int y=r->y;y<r->y+r->h&&sf.frame;y++)for(int x=r->x;x<r->x+r->w&&sf.frame;x++)pregame_font_pixel(surface,(Uint8 *)surface->pixels+y*SF_W+x,0);
}
void pregame_font_frame_end(void)
{
 if(!exact())return;
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
}
/* Same premultiplied correlated-layer contract as the approved selectors. */
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
  const struct SfCommand *c=&sf.commands[k];
  if(c->kind==C_CLASSIC){
   for(unsigned i=c->first;i<c->first+c->events;i++){
    const struct SfEvent *e=&sf.events[i];unsigned p=e->position;sf.replay[p]=sf.underlay[p]=e->index;
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
  for(unsigned y=0;y<c->h*4u;y++)for(unsigned x=0;x<c->w*4u;x++){
   unsigned at=(ay+y)*s->aw+ax+x;Uint8 alpha=sf.payload[c->bank][at];if(!alpha)continue;
   unsigned p=(c->y+y/4)*SF_W+c->x+x/4;
   Uint8 v=c->kind==C_DARK?shade(sf.replay[p]):face(c->bank==2?7:sf.payload[c->bank][s->plane+at],c->hue,c->value);
   unsigned out=(c->y*4+y)*SF_OW+c->x*4+x;sf.output[out]=over(sf.output[out],sf.palette[v],alpha);sf.owner[p]=1;
  }
  for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
   Uint8 role=sf.masks[g->mask+y*c->w+x];if(role==255)continue;unsigned p=(c->y+y)*SF_W+c->x+x;
   sf.replay[p]=c->kind==C_DARK?shade(sf.replay[p]):face(role,c->hue,c->value);sf.owner[p]=1;
  }
 }
 for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p])sf.replay[p]=sf.underlay[p]=sf.cursor_index[p];
 support.w=right-support.x;support.h=bottom-support.y;return support;
}
bool pregame_font_present(SDL_Renderer *renderer,SDL_Texture *reference,SDL_Surface *surface,const SDL_Rect *destination,bool foreign_owner)
{
 if(!exact())return false;
 if(foreign_owner){pregame_font_invalidate();return false;}
 if(sf.stage!=S_READY&&sf.stage!=S_CURSOR_DONE){reject();return false;}
 if(!renderer||surface!=sf.screen||!destination||!palette_matches()||scaler>=scalers_count||!scalers[scaler].scaler32){reject();return false;}
 SDL_Rect support=render();if(memcmp(sf.replay,sf.expected,SF_N)){reject();return false;}
 SDL_Surface underlay=*sf.screen;underlay.pixels=sf.underlay;
 unsigned radius=scaler==0||scaler==1||scaler==4||scaler==7?0:1;
 return selector_font_output_present(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,sf.cursor_mask,radius);
}
