/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional bounded JE_loadScreen owner. Observes original indexed work.
 * Deliberately separate from settings grammar and gameplay font ownership.
 */
#include "load_font.h"
#include "selector_font.h"
#include "selector_font_output.h"
#include "settings_font.h"
#include "config.h"
#include "helptext.h"
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
#define SF_BASE UINT64_C(0x422dabf4e68d0878)
#define SF_FNV UINT64_C(14695981039346656037)
enum { SF_W=320,SF_H=200,SF_N=64000,SF_D=4,SF_OW=1280,SF_OH=800,
 SF_OUT_BYTES=4096000,SF_PAYLOAD=1097728,SF_COMMANDS=4096,SF_RUNS=40,SF_GLYPHS=187,
 SF_MASK_BYTES=60*17*20+127*6*8,SF_CAP=7*1024*1024 };
enum { C_DARK,C_BLACK,C_FACE,C_SOLID,C_SHADE };
enum { S_IDLE,S_BUILD,S_RUN,S_ARROW,S_READY,S_CURSOR,S_CURSOR_DONE };
struct SfSpec { unsigned aw,ah,cw,ch,n,eligible,plane,mode,lo,hi,mw,mh; uint64_t metrics,encoded,eligibility,payload; const char *name; };
static const struct SfSpec spec[3]={
 {1216,384,76,96,60,53,466944,1,12,15,17,20,UINT64_C(0xb0a8226af36e025a),UINT64_C(0x5c12ed2dea448227),UINT64_C(0x5529cd3792b04378),UINT64_C(0x0501f2f573e8d9a5),"large"},
 {896,384,56,64,85,76,344064,1,12,15,12,13,UINT64_C(0xf0dec0f37828f1c4),UINT64_C(0x96f0e4e668876f23),UINT64_C(0xa3861b64f710cb1f),UINT64_C(0x08f9609583417c89),"medium"},
 {512,320,32,40,127,86,163840,0,7,7,6,8,UINT64_C(0x0908ca85cbf2a1e3),UINT64_C(0x2ed2973d82ce6f3d),UINT64_C(0x68e8c2bab3c43d0d),UINT64_C(0x85cddeb8bd7ea09a),"tiny"}
};
struct SfGlyph { const Uint8 *rle; Uint16 size,mask; Uint8 w,h,ink; };
struct SfCommand { Uint16 x,y,w,h; Uint8 kind,bank,id,hue,op; Sint8 value; };
static struct {
 bool active,frame,glyph,cursor,initial_done,exiting;
 int stage,fade_remaining,fade_kind,fade_declared;
 unsigned page,selected,row,run_next,run_total;
 bool help,arrow;unsigned help_line,arrow_quad,arrow_writes;
 struct { Uint16 level;Uint8 episode;char name[15],level_name[11]; } slots[11];
 struct { char text[64];Sint16 x,y;Uint8 role,row,bank,hue;Sint8 value; } runs[SF_RUNS];
 unsigned count,next,limit,pixel,run_count,run_role;
 bool cursor_sprite;unsigned cursor_quad,cursor_events,cursor_next;int cursor_x,cursor_y;
 struct { Uint16 position;Uint8 index; } cursor_event[168];
 SDL_Surface *screen,*backup; void *pixels,*backup_pixels;
 SDL_PixelFormat *format,*backup_format,*tex_format;
 SDL_Renderer *renderer;SDL_Texture *texture;
 unsigned generation,frame_generation,present_scaler;int present_w,present_h;
 Uint8 base[SF_N],expected[SF_N],replay[SF_N],owner[SF_N],pre_cursor[SF_N],cursor_index[SF_N],cursor_mask[SF_N];
 struct SfGlyph glyphs[SF_GLYPHS];Uint8 masks[SF_MASK_BYTES];
 struct SfCommand commands[SF_COMMANDS];
 SDL_Color expected_palette[256],fade_target[256];
 Uint32 palette[256];
 Uint8 *payload[3];Uint32 *output;
} sf;
static const char *directory;
/* Retained inactive settings static storage is included at acquisition. */
enum { SF_SETTINGS_STATIC_BOUND=600000 };
typedef char sf_budget_check[(sizeof(sf)+SF_SETTINGS_STATIC_BOUND+SF_PAYLOAD+SF_OUT_BYTES+3*128+2048<=SF_CAP)?1:-1];
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
void load_font_set_directory(const char *path){load_font_end();directory=path&&*path?path:NULL;}
void load_font_release_texture(void){if(sf.active||sf.output)selector_font_output_release();if(sf.texture)SDL_DestroyTexture(sf.texture);sf.texture=NULL;sf.renderer=NULL;}
void load_font_end(void){load_font_release_texture();for(unsigned b=0;b<3;b++)free(sf.payload[b]);free(sf.output);memset(&sf,0,sizeof(sf));}
void load_font_invalidate(void){if(sf.active){++sf.generation;reject();}load_font_release_texture();}
void load_font_table_reset(unsigned table){if(table<3)load_font_end();}
static bool geometry(SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==SF_W&&s->h==SF_H&&s->pitch==SF_W&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&s->clip_rect.x==0&&s->clip_rect.y==0&&s->clip_rect.w==SF_W&&s->clip_rect.h==SF_H;}
static bool layout(void){return sf.screen==VGAScreen&&sf.screen==VGAScreenSeg&&sf.backup==VGAScreen2&&geometry(sf.screen)&&geometry(sf.backup)&&sf.screen->pixels==sf.pixels&&sf.backup->pixels==sf.backup_pixels&&sf.screen->format==sf.format&&sf.backup->format==sf.backup_format;}
static bool source(bool capture)
{
 uint64_t map=SF_FNV;unsigned offset=0;
 for(unsigned i=0;i<256;i++){uint32_t v=(uint32_t)font_ascii[i];Uint8 p[4]={(Uint8)v,(Uint8)(v>>8),(Uint8)(v>>16),(Uint8)(v>>24)};map=hash_more(map,p,4);}
 if(map!=SF_MAP)return false;
 for(unsigned b=0;b<3;b+=2){
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
void load_font_begin(SDL_Surface *screen,SDL_Surface *backup)
{
 load_font_end();settings_font_end();selector_font_end();if(settings_font_static_bytes()>SF_SETTINGS_STATIC_BOUND||!directory||!geometry(screen)||!geometry(backup)||screen!=VGAScreen||screen!=VGAScreenSeg||backup!=VGAScreen2||palette_count<=7||palette_hash(palettes[7])!=SF_PAL||palette_hash(colors)!=SF_PAL||!main_window_tex_format||main_window_tex_format->BitsPerPixel!=32||hash(backup->pixels,SF_N)!=SF_BASE||!source(true))return;
 for(unsigned b=0;b<3;b+=2)if(!load(b)){load_font_end();return;}
 sf.output=malloc(SF_OUT_BYTES);if(!sf.output){load_font_end();return;}
 sf.screen=screen;sf.backup=backup;sf.pixels=screen->pixels;sf.backup_pixels=backup->pixels;sf.format=screen->format;sf.backup_format=backup->format;memcpy(sf.base,backup->pixels,SF_N);
 for(unsigned i=0;i<256;i++)SDL_GetRGB(rgb_palette[i],main_window_tex_format,&sf.expected_palette[i].r,&sf.expected_palette[i].g,&sf.expected_palette[i].b);
 sf.active=true;sf.stage=S_IDLE;sf.generation=1;
}
static bool check(void)
{
 if(!sf.active||!sf.frame)return false;
 if(!layout()){load_font_end();return false;}
 if(sf.frame_generation!=sf.generation){reject();return false;}return true;
}
static bool exact(void){if(!check())return false;if(!source(false)||palette_count<=7||palette_hash(palettes[7])!=SF_PAL||memcmp(sf.backup_pixels,sf.base,SF_N)){load_font_end();return false;}if(memcmp(sf.pixels,sf.expected,SF_N)){reject();return false;}return true;}
static Uint8 shade(Uint8 v){return (v&240)|((v&15)/2);}
static Uint8 face(unsigned r,int value,unsigned hue,bool unsafe)
{int v=(int)r+value;if(!unsafe){if(v<0)v=0;if(v>15)v=15;}return (Uint8)((hue<<4)|v);}
bool load_font_owns_display(void){return sf.active;}
size_t load_font_static_bytes(void){return sizeof(sf);}
static bool box(int x,int y,int w,int h){return x>=0&&y>=0&&w>0&&h>0&&x<=SF_W-w&&y<=SF_H-h;}
static struct SfCommand *append(unsigned kind,int x,int y,unsigned w,unsigned h,unsigned b,unsigned id,unsigned hue,int value)
{
 if(sf.count==SF_COMMANDS||!box(x,y,w,h)){reject();return NULL;}
 struct SfCommand *c=&sf.commands[sf.count++];c->kind=kind;c->x=x;c->y=y;c->w=w;c->h=h;c->bank=b;c->id=id;c->hue=hue;c->value=value;c->op=kind==C_DARK?LOAD_DARK:kind==C_BLACK?LOAD_BLACK:b==2?LOAD_UNSAFE:LOAD_FACE;return c;
}
static const char *const headings[2]={"One Player Saved Games","Two Player Saved Games"};
static const char *const footer[2]={"~Left~ or ~right~ for 1","or 2 player game."};
static bool bounded_text(const char *s,size_t bound,bool markup)
{
 const char *end=memchr(s,0,bound);if(!end)return false;
 for(const char *p=s;p<end;p++){unsigned ch=(unsigned char)*p;if(ch==' '||(markup&&ch=='~'))continue;
  int id=font_ascii[ch];if(ch<33||ch>=127||ch=='~'||id<0||id>=86||!glyph(2,id)->ink)return false;
 }return true;
}
static size_t bounded_length(const char *s,size_t n){size_t i=0;while(i<n&&s[i])++i;return i;}
static bool static_text(const char *s,size_t n,const char *want){size_t length=strlen(want);return length<n&&!memcmp(s,want,length+1);}
static bool add_run(unsigned role,unsigned row,int x,int y,const char *text,unsigned bank,unsigned hue,int value)
{
 if(sf.run_total==SF_RUNS||!text||bounded_length(text,64)==64)return false;
 unsigned n=sf.run_total++;sf.runs[n].role=role;sf.runs[n].row=row;sf.runs[n].x=x;sf.runs[n].y=y;sf.runs[n].bank=bank;sf.runs[n].hue=hue;sf.runs[n].value=value;
 memcpy(sf.runs[n].text,text,strlen(text)+1);return true;
}
static bool snapshot(unsigned page)
{
 if(!static_text(miscText[38],sizeof(miscText[38]),headings[0])||!static_text(miscText[39],sizeof(miscText[39]),headings[1])||!static_text(miscText[2],sizeof(miscText[2]),"EMPTY SLOT")||!static_text(miscText[33],sizeof(miscText[33]),"Exit to Main Menu")||!static_text(miscTextB[2],sizeof(miscTextB[2]),"Last Level")||!static_text(miscTextB[1],sizeof(miscTextB[1]),"Episode")||!static_text(miscText[55],sizeof(miscText[55]),"~Left~ or ~right~ for 1 or 2 player game.")||helpBoxBrightness!=1||helpBoxShadeType!=FULL_SHADE||verticalHeight!=7)return false;
 sf.run_total=0;
 if(!add_run(LOAD_HEADING,0,160,5,headings[page],0,15,-3))return false;
 for(unsigned row=0;row<11;row++){
  const JE_SaveFileType *slot=&saveFiles[page*11+row];sf.slots[row].level=slot->level;sf.slots[row].episode=slot->episode;
  bool empty=slot->level==0;int v=row==sf.selected?6:empty?0:2;char text[22];
  if(!empty){
   if(!bounded_text(slot->name,sizeof(slot->name),false)||!bounded_text(slot->levelName,sizeof(slot->levelName),false))return false;
   memcpy(sf.slots[row].name,slot->name,sizeof(slot->name));memcpy(sf.slots[row].level_name,slot->levelName,sizeof(slot->levelName));
  }else{sf.slots[row].name[0]=0;sf.slots[row].level_name[0]=0;}
  if(!add_run(LOAD_NAME,row,10,30+13*row,empty?"EMPTY SLOT":sf.slots[row].name,2,13,v))return false;
  snprintf(text,sizeof(text),"%s %s","Last Level",empty?"-----":sf.slots[row].level_name);
  if(!add_run(LOAD_LEVEL,row,120,30+13*row,text,2,5,v))return false;
  if(!empty){snprintf(text,sizeof(text),"Episode %u",sf.slots[row].episode);if(!add_run(LOAD_EPISODE,row,250,30+13*row,text,2,5,v))return false;}
 }
 return add_run(LOAD_EXIT,11,10,173,"Exit to Main Menu",2,13,sf.selected==11?6:2)&&add_run(LOAD_FOOTER,0,103,182,footer[0],2,15,1)&&add_run(LOAD_FOOTER,1,103,189,footer[1],2,15,1);
}
void load_font_frame_begin(unsigned page,size_t selected)
{
 if(!sf.active)return;
 sf.frame=true;sf.frame_generation=sf.generation;if(!check())return;
 if(!source(false)||memcmp(sf.backup_pixels,sf.base,SF_N)){load_font_end();return;}
 if(page>1||selected>=12||memcmp(sf.pixels,sf.base,SF_N)||sf.exiting){reject();return;}
 sf.page=page;sf.selected=selected;if(!snapshot(page)){reject();return;}
 memcpy(sf.expected,sf.base,SF_N);memset(sf.owner,0,SF_N);memset(sf.cursor_mask,0,SF_N);
 sf.row=sf.run_next=sf.count=sf.next=sf.limit=sf.pixel=sf.run_count=0;sf.glyph=sf.cursor=sf.help=sf.arrow=false;sf.help_line=sf.arrow_quad=sf.arrow_writes=0;sf.stage=S_BUILD;
 sf.tex_format=main_window_tex_format;sf.present_scaler=scaler;sf.present_w=sf.present_h=0;
}
void load_font_run_begin(enum LoadRun role,unsigned row,SDL_Surface *surface,int x,int y,const char *text,unsigned font,int alignment,unsigned hue,int value)
{
 if(!exact())return;
 if(sf.stage!=S_BUILD||surface!=sf.screen||!text||sf.run_next>=sf.run_total||sf.run_count>=SF_RUNS){reject();return;}
 unsigned n=sf.run_next,b=sf.runs[n].bank;
 if(role!=sf.runs[n].role||row!=sf.runs[n].row||font!=b||x!=sf.runs[n].x||y!=sf.runs[n].y||hue!=sf.runs[n].hue||value!=sf.runs[n].value||alignment!=(b==0?centered:left_aligned)||bounded_length(text,64)==64||strcmp(text,sf.runs[n].text)||(role==LOAD_FOOTER&&(!sf.help||!sf.arrow))){reject();return;}
 unsigned length=0,width=0;
 for(;length<64&&text[length];length++){
  unsigned ch=(unsigned char)text[length];if(ch==' '){width+=6;continue;}if(role==LOAD_FOOTER&&ch=='~')continue;int id=font_ascii[ch];
  if(ch<33||ch>=127||ch=='~'||id<0||(unsigned)id>=spec[b].n||(b==2&&id>=86)||!glyph(b,id)->ink){reject();return;}width+=glyph(b,id)->w+1;
 }
 if(length==64||width>318){reject();return;}if(alignment==centered)x-=(int)width/2;
 sf.next=sf.count;sf.pixel=0;sf.run_role=role;
 const int dx[5]={-1,1,0,0,0},dy[5]={0,0,-1,1,0};unsigned passes=b==0?2:5;
 for(unsigned pass=0;pass<passes;pass++){
  bool face_pass=pass==passes-1;int gx=x+(b==0?(face_pass?0:2):dx[pass]),gy=y+(b==0?(face_pass?0:2):dy[pass]),bright=0;
  for(unsigned i=0;i<length;i++){
   unsigned ch=(unsigned char)text[i];if(ch==' '){gx+=6;continue;}if(ch=='~'){bright=bright?0:4;continue;}
   unsigned id=font_ascii[ch];const struct SfGlyph *g=glyph(b,id);
   if(!append(face_pass?C_FACE:b==2?C_BLACK:C_DARK,gx,gy,g->w,g->h,b,id,hue,value+bright))return;
   gx+=g->w+1;
  }
 }
 sf.limit=sf.count;sf.stage=S_RUN;++sf.run_count;
}
void load_font_run_end(void)
{
 if(!exact())return;
 if(sf.stage!=S_RUN||sf.glyph||sf.next!=sf.limit){reject();return;}
 ++sf.run_next;sf.stage=S_BUILD;
}
void load_font_help_begin(SDL_Surface *screen,int x,int y,const char *text,unsigned width)
{
 if(!exact())return;
 if(sf.stage!=S_BUILD||sf.help||!sf.arrow||sf.run_next!=sf.run_total-2||screen!=sf.screen||x!=103||y!=182||width!=25||strcmp(text,"~Left~ or ~right~ for 1 or 2 player game.")||helpBoxColor!=15||helpBoxBrightness!=1||helpBoxShadeType!=FULL_SHADE||verticalHeight!=7){reject();return;}
 sf.help=true;sf.help_line=0;
}
void load_font_help_line_begin(SDL_Surface *screen,int x,int y,const char *text,unsigned hue,int value,unsigned shade_type)
{
 if(!sf.help||!sf.frame)return;
 if(sf.help_line>=2||shade_type!=FULL_SHADE){reject();return;}
 load_font_run_begin(LOAD_FOOTER,sf.help_line,screen,x,y,text,2,left_aligned,hue,value);
}
void load_font_help_line_end(void)
{if(!sf.help||!sf.frame)return;load_font_run_end();++sf.help_line;}
void load_font_help_end(void)
{
 if(!exact())return;
 if(!sf.help||sf.help_line!=2||helpBoxColor!=12||helpBoxShadeType!=FULL_SHADE||helpBoxBrightness!=1||verticalHeight!=7){reject();return;}sf.help=false;
}
static bool unowned(const struct SfCommand *c)
{for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++)if(sf.owner[(c->y+y)*SF_W+c->x+x])return false;return true;}
static void skip_transparent(void)
{
 const struct SfCommand *c=&sf.commands[sf.next];const struct SfGlyph *g=glyph(c->bank,c->id);
 while(sf.pixel<c->w*c->h&&sf.masks[g->mask+sf.pixel]==255)++sf.pixel;
}
void load_font_glyph_begin(SDL_Surface *surface,int x,int y,unsigned font,unsigned id,enum LoadGlyph op,unsigned hue,int value)
{
 if(!check())return;
 if(sf.stage!=S_RUN||sf.glyph||sf.next>=sf.limit||surface!=sf.screen){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];
 unsigned want=c->op;
 if(c->x!=x||c->y!=y||c->bank!=font||c->id!=id||op!=want||(c->kind==C_FACE&&(hue!=c->hue||value!=c->value))||
    (c->kind==C_DARK&&!unowned(c))){reject();return;}
 sf.glyph=true;sf.pixel=0;skip_transparent();
}
void load_font_glyph_end(void)
{
 if(!check())return;
 if(sf.stage!=S_RUN||!sf.glyph||sf.next>=sf.limit){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];const struct SfGlyph *g=glyph(c->bank,c->id);const struct SfSpec *s=&spec[c->bank];
 if(sf.pixel!=c->w*c->h){reject();return;}
 unsigned ax=(c->id%16)*s->cw+4,ay=(c->id/16)*s->ch+4;
 for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
  bool owns=sf.masks[g->mask+y*c->w+x]!=255;
  for(unsigned dy=0;dy<4&&!owns;dy++)for(unsigned dx=0;dx<4;dx++)if(sf.payload[c->bank][(ay+y*4+dy)*s->aw+ax+x*4+dx]){owns=true;break;}
  if(owns)sf.owner[(c->y+y)*SF_W+c->x+x]=1;
 }
 ++sf.next;sf.pixel=0;sf.glyph=false;
}
void load_font_arrow_begin(void)
{
 if(!exact())return;
 if(sf.stage!=S_BUILD||sf.arrow||sf.run_next!=sf.run_total-2){reject();return;}
 sf.arrow_quad=sf.arrow_writes=0;sf.stage=S_ARROW;
}
void load_font_arrow_sprite_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned id)
{
 if(!check())return;
 static const int dx[4]={0,12,0,12},dy[4]={0,0,14,14};
 unsigned base=sf.page?279:281,quad=sf.arrow_quad;
 if(sf.stage!=S_ARROW||sf.glyph||quad>=4||surface!=sf.screen||data!=shopSpriteSheet.data||size!=shopSpriteSheet.size||!data||size!=29941||hash(data,size)!=UINT64_C(0x8c478c429071f043)||id!=base+(quad&1)+(quad/2)*19||x!=(sf.page?83:213)+dx[quad]||y!=179+dy[quad]){reject();return;}
 const Uint8 *bytes=data;unsigned off=bytes[(id-1)*2]|(bytes[(id-1)*2+1]<<8),xx=0,yy=0;sf.next=sf.count;sf.pixel=0;
 for(unsigned k=off;;k++){
  if(k>=size||yy>14){reject();return;}unsigned v=bytes[k];if(v==15)break;unsigned fill=v>>4;xx+=v&15;
  if(!fill){if(xx!=12){reject();return;}++yy;xx=0;continue;}
  if(xx+fill>12||yy>=14||k+fill>=size){reject();return;}
  while(fill--){Uint8 color=bytes[++k];if(y+(int)yy<200){if(!append(C_SOLID,x+xx,y+yy,1,1,0,0,0,(Sint8)color))return;}++xx;}
 }
 sf.limit=sf.count;sf.glyph=true;
}
void load_font_arrow_sprite_end(void)
{if(!exact())return;
 if(sf.stage!=S_ARROW||!sf.glyph||sf.next!=sf.limit){reject();return;}sf.glyph=false;++sf.arrow_quad;}
void load_font_arrow_end(void)
{if(!exact())return;
 if(sf.stage!=S_ARROW||sf.glyph||sf.arrow_quad!=4||sf.arrow_writes!=204){reject();return;}sf.arrow=true;sf.stage=S_BUILD;}
void load_font_pixel(SDL_Surface *surface,Uint8 *address,int style)
{
 if(!sf.active||!sf.frame)return;
 if(!check())return;
 if(surface!=sf.screen){reject();return;}
 uintptr_t ptr=(uintptr_t)address,base=(uintptr_t)sf.pixels;if(ptr<base||ptr-base>=SF_N){reject();return;}unsigned p=ptr-base;
 if(sf.stage==S_CURSOR){
  if(style!=0||!sf.cursor_sprite||sf.cursor_next>=sf.cursor_events||sf.cursor_event[sf.cursor_next].position!=p||sf.cursor_event[sf.cursor_next].index!=*address){reject();return;}
  ++sf.cursor_next;sf.expected[p]=*address;sf.cursor_index[p]=*address;sf.cursor_mask[p]=1;return;
 }
 if((sf.stage!=S_RUN&&sf.stage!=S_ARROW)||sf.next>=sf.limit||!sf.glyph){reject();return;}
 const struct SfCommand *c=&sf.commands[sf.next];unsigned wanted=(c->y+sf.pixel/c->w)*SF_W+c->x+sf.pixel%c->w;
 bool dark=c->kind==C_DARK||c->kind==C_SHADE;
 if(p!=wanted||style!=(dark?2:0)){reject();return;}
 if(c->kind==C_SHADE&&sf.owner[p]){reject();return;}
 Uint8 v=dark?shade(sf.expected[p]):c->kind==C_BLACK?0:c->kind==C_SOLID?(Uint8)c->value:face(sf.masks[glyph(c->bank,c->id)->mask+sf.pixel],c->value,c->hue,c->bank==2);
 if(*address!=v){reject();return;}sf.expected[p]=v;++sf.pixel;
 if(sf.stage==S_RUN)skip_transparent();else {++sf.arrow_writes;sf.owner[p]=0;if(sf.pixel==c->w*c->h){++sf.next;sf.pixel=0;}}
}
void load_font_rect(SDL_Surface *surface,const SDL_Rect *r)
{(void)surface;(void)r;if(sf.active&&sf.frame)reject();}
void load_font_frame_end(void)
{if(!exact())return;
 if(sf.stage!=S_BUILD||sf.help||!sf.arrow||sf.run_next!=sf.run_total||sf.glyph||sf.next!=sf.count){reject();return;}sf.stage=S_READY;}
void load_font_cursor_begin(void)
{if(!exact())return;
 if(sf.stage!=S_READY||sf.cursor||sf.fade_remaining){reject();return;}memcpy(sf.pre_cursor,sf.expected,SF_N);memset(sf.cursor_mask,0,SF_N);sf.cursor=true;sf.cursor_quad=0;sf.cursor_sprite=false;sf.stage=S_CURSOR;}
/* Verify the exact four normal-pointer source tiles before observing writes.
 * This also rejects unrelated same-index writers during the cursor bracket. */
void load_font_cursor_sprite_begin(SDL_Surface *surface,int x,int y,const void *data,size_t size,unsigned id)
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
void load_font_cursor_sprite_end(void)
{
 if(!check())return;
 if(sf.stage!=S_CURSOR||!sf.cursor_sprite||sf.cursor_next!=sf.cursor_events){reject();return;}
 sf.cursor_sprite=false;++sf.cursor_quad;
}
void load_font_cursor_done(void)
{if(!exact())return;
 if(sf.stage!=S_CURSOR||sf.cursor_sprite||(sf.cursor_quad!=0&&sf.cursor_quad!=4)){reject();return;}sf.stage=S_CURSOR_DONE;}
void load_font_cursor_erased(void)
{
 if(!check())return;
 if(sf.stage!=S_CURSOR_DONE||!sf.cursor||memcmp(sf.pixels,sf.pre_cursor,SF_N)){reject();return;}
 memcpy(sf.expected,sf.pre_cursor,SF_N);memset(sf.cursor_mask,0,SF_N);sf.cursor=false;sf.stage=S_READY;
}
void load_font_fade_declare(int steps)
{
 if(!sf.active)return;
 if(sf.fade_declared||sf.fade_remaining||steps!=(sf.initial_done?15:10)){load_font_end();return;}
 sf.fade_declared=steps;
}
void load_font_fade_start(const SDL_Color *target,const SDL_Color *solid,unsigned first,unsigned last)
{
 if(!sf.active)return;
 if(sf.fade_declared!=(sf.initial_done?15:10)||first||last!=255||sf.cursor||sf.fade_remaining||(!target&&!solid)||(!sf.initial_done&&(!target||palette_hash(target)!=SF_PAL))||(sf.initial_done&&(!solid||solid->r||solid->g||solid->b))){load_font_end();return;}
 sf.fade_kind=sf.initial_done?2:1;sf.fade_remaining=sf.fade_declared;sf.fade_declared=0;
 for(unsigned i=0;i<256;i++)sf.fade_target[i]=target?target[i]:*solid;
 if(sf.initial_done)sf.exiting=true;
}
void load_font_fade_step(int remaining,unsigned first,unsigned last)
{
 if(!sf.active)return;
 if(first||last!=255||remaining!=sf.fade_remaining||remaining<1||remaining>(sf.fade_kind==1?10:15)){load_font_end();return;}
 for(unsigned i=0;i<256;i++){
  sf.expected_palette[i].r+=(int)(sf.fade_target[i].r-sf.expected_palette[i].r)/remaining;
  sf.expected_palette[i].g+=(int)(sf.fade_target[i].g-sf.expected_palette[i].g)/remaining;
  sf.expected_palette[i].b+=(int)(sf.fade_target[i].b-sf.expected_palette[i].b)/remaining;
 }
 if(!palette_matches()){load_font_end();return;}
 if(!--sf.fade_remaining)sf.initial_done=true;
}
static Uint32 mix(Uint32 dst,Uint32 src,unsigned alpha)
{
 Uint32 result=UINT32_C(0xff000000);
 for(unsigned shift=0;shift<=16;shift+=8)result|=((((src>>shift)&255)*alpha+((dst>>shift)&255)*(255-alpha)+127)/255)<<shift;
 return result;
}
static void paint_original(unsigned p,Uint8 index)
{
 unsigned x=(p%SF_W)*4,y=(p/SF_W)*4;Uint32 color=sf.palette[index];
 for(unsigned dy=0;dy<4;dy++)for(unsigned dx=0;dx<4;dx++)sf.output[(y+dy)*SF_OW+x+dx]=color;
}
/* Build complete correlated samples before reducing. Original source coverage
 * changes replay indices only; it must never leak through authored alpha gaps. */
static void render(void)
{
 for(unsigned i=0;i<256;i++){SDL_Color p=sf.expected_palette[i];sf.palette[i]=UINT32_C(0xff000000)|((Uint32)p.r<<16)|((Uint32)p.g<<8)|p.b;}
 memcpy(sf.replay,sf.base,SF_N);
 for(unsigned p=0;p<SF_N;p++)paint_original(p,sf.base[p]);
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];
  if(c->kind==C_SOLID||c->kind==C_SHADE){
   for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
    unsigned p=(c->y+y)*SF_W+c->x+x;Uint8 v=c->kind==C_SOLID?(Uint8)c->value:shade(sf.replay[p]);sf.replay[p]=v;paint_original(p,v);
   }
  }else{
   const struct SfSpec *s=&spec[c->bank];const struct SfGlyph *g=glyph(c->bank,c->id);
   unsigned ax=(c->id%16)*s->cw+4,ay=(c->id/16)*s->ch+4;
   for(unsigned y=0;y<c->h*4u;y++)for(unsigned x=0;x<c->w*4u;x++){
    unsigned a=(ay+y)*s->aw+ax+x;Uint8 alpha=sf.payload[c->bank][a];if(!alpha)continue;
    unsigned p=(c->y+y/4)*SF_W+c->x+x/4;Uint8 v=c->kind==C_DARK?shade(sf.replay[p]):c->kind==C_BLACK?0:face(c->bank==2?7:sf.payload[c->bank][s->plane+a],c->value,c->hue,c->bank==2);
    unsigned out=(c->y*4+y)*SF_OW+c->x*4+x;sf.output[out]=mix(sf.output[out],sf.palette[v],alpha);
   }
   for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
    Uint8 role=sf.masks[g->mask+y*c->w+x];if(role==255)continue;unsigned p=(c->y+y)*SF_W+c->x+x;
    sf.replay[p]=c->kind==C_DARK?shade(sf.replay[p]):c->kind==C_BLACK?0:face(role,c->value,c->hue,c->bank==2);
   }
  }
 }
 for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p]){sf.replay[p]=sf.cursor_index[p];paint_original(p,sf.cursor_index[p]);}
}
/* Portable output keeps authored glyphs as an ordered premultiplied layer.
 * sf.replay first proves the complete original indexed command stream. Only
 * after that proof may the same storage become the font-free underlay. */
static Uint32 mix_premul(Uint32 dst,Uint32 src,unsigned alpha)
{
 Uint32 result=(alpha+(((dst>>24)*(255-alpha)+127)/255))<<24;
 for(unsigned shift=0;shift<=16;shift+=8)result|=((((src>>shift)&255)*alpha+((dst>>shift)&255)*(255-alpha)+127)/255)<<shift;
 return result;
}
static void clear_layer(unsigned p)
{
 unsigned x=(p%SF_W)*4,y=(p/SF_W)*4;
 for(unsigned dy=0;dy<4;dy++)for(unsigned dx=0;dx<4;dx++)sf.output[(y+dy)*SF_OW+x+dx]=0;
}
static bool render_portable(SDL_Rect *support)
{
 for(unsigned i=0;i<256;i++){SDL_Color p=sf.expected_palette[i];sf.palette[i]=UINT32_C(0xff000000)|((Uint32)p.r<<16)|((Uint32)p.g<<8)|p.b;}
 memcpy(sf.replay,sf.base,SF_N);memset(sf.output,0,SF_OUT_BYTES);
 int left=SF_OW,top=SF_OH,right=0,bottom=0;
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];
  if(c->kind==C_SOLID||c->kind==C_SHADE){
   for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
    unsigned p=(c->y+y)*SF_W+c->x+x;
    sf.replay[p]=c->kind==C_SOLID?(Uint8)c->value:shade(sf.replay[p]);
    clear_layer(p); /* Even a same-index primitive occludes earlier glyphs. */
   }
  }else{
   const struct SfSpec *s=&spec[c->bank];const struct SfGlyph *g=glyph(c->bank,c->id);
   unsigned ax=(c->id%16)*s->cw+4,ay=(c->id/16)*s->ch+4;
   left=MIN(left,c->x*4);top=MIN(top,c->y*4);right=MAX(right,(c->x+c->w)*4);bottom=MAX(bottom,(c->y+c->h)*4);
   for(unsigned y=0;y<c->h*4u;y++)for(unsigned x=0;x<c->w*4u;x++){
    unsigned a=(ay+y)*s->aw+ax+x;Uint8 alpha=sf.payload[c->bank][a];if(!alpha)continue;
    unsigned p=(c->y+y/4)*SF_W+c->x+x/4;Uint8 v=c->kind==C_DARK?shade(sf.replay[p]):c->kind==C_BLACK?0:face(c->bank==2?7:sf.payload[c->bank][s->plane+a],c->value,c->hue,c->bank==2);
    unsigned out=(c->y*4+y)*SF_OW+c->x*4+x;sf.output[out]=mix_premul(sf.output[out],sf.palette[v],alpha);
   }
   for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
    Uint8 role=sf.masks[g->mask+y*c->w+x];if(role==255)continue;unsigned p=(c->y+y)*SF_W+c->x+x;
    sf.replay[p]=c->kind==C_DARK?shade(sf.replay[p]):c->kind==C_BLACK?0:face(role,c->value,c->hue,c->bank==2);
   }
  }
 }
 for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p])sf.replay[p]=sf.cursor_index[p];
 if(memcmp(sf.replay,sf.expected,SF_N))return false;
 /* C_SHADE is admitted only over cells with no prior glyph ownership.
  * Consequently its input is identical when glyph commands are omitted. */
 memcpy(sf.replay,sf.base,SF_N);
 for(unsigned k=0;k<sf.count;k++){
  const struct SfCommand *c=&sf.commands[k];if(c->kind!=C_SOLID&&c->kind!=C_SHADE)continue;
  for(unsigned y=0;y<c->h;y++)for(unsigned x=0;x<c->w;x++){
   unsigned p=(c->y+y)*SF_W+c->x+x;sf.replay[p]=c->kind==C_SOLID?(Uint8)c->value:shade(sf.replay[p]);
  }
 }
 for(unsigned p=0;p<SF_N;p++)if(sf.cursor_mask[p])sf.replay[p]=sf.cursor_index[p];
 *support=left<right&&top<bottom?(SDL_Rect){left,top,right-left,bottom-top}:(SDL_Rect){0,0,0,0};
 return true;
}
static void reduce2(void)
{
 for(unsigned y=0;y<400;y++)for(unsigned x=0;x<640;x++){
  unsigned p=y*2*SF_OW+x*2;Uint32 v=UINT32_C(0xff000000);
  for(unsigned shift=0;shift<=16;shift+=8){unsigned sum=((sf.output[p]>>shift)&255)+((sf.output[p+1]>>shift)&255)+((sf.output[p+SF_OW]>>shift)&255)+((sf.output[p+SF_OW+1]>>shift)&255);v|=((sum+2)/4)<<shift;}
  sf.output[y*640+x]=v;
 }
}
bool load_font_present(SDL_Renderer *renderer,SDL_Texture *reference,SDL_Surface *surface,const SDL_Rect *destination,bool foreign_owner)
{
 if(!exact())return false;
 if(foreign_owner){load_font_invalidate();return false;}
 if(sf.stage!=S_READY&&sf.stage!=S_CURSOR_DONE){reject();return false;}
 if(!renderer||surface!=sf.screen||!destination||!main_window_tex_format||main_window_tex_format->format!=SDL_PIXELFORMAT_RGB888||!palette_matches()){reject();return false;}
 if(scaler>=scalers_count||!scalers[scaler].scaler32||sf.tex_format!=main_window_tex_format||sf.present_scaler!=scaler||(sf.present_w&&(sf.present_w!=destination->w||sf.present_h!=destination->h))||(sf.renderer&&sf.renderer!=renderer)){load_font_invalidate();return false;}
 sf.present_w=destination->w;sf.present_h=destination->h;
 int rw=0,rh=0,lw=0,lh=0,ww=0,wh=0;float sx=0,sy=0;SDL_Rect viewport;
 SDL_RenderGetLogicalSize(renderer,&lw,&lh);SDL_RenderGetScale(renderer,&sx,&sy);SDL_RenderGetViewport(renderer,&viewport);
 if(main_window)SDL_GetWindowSize(main_window,&ww,&wh);
 bool two=scaler==1&&destination->w==640&&destination->h==400;
 bool four=scaler==7&&destination->w==1280&&destination->h==800;
 bool legacy=(two||four)&&scaling_mode!=SCALE_ASPECT_4_3&&scaling_mode!=SCALE_ASPECT_8_5&&
  !SDL_GetRenderTarget(renderer)&&!SDL_GetRendererOutputSize(renderer,&rw,&rh)&&!lw&&!lh&&sx==1.0f&&sy==1.0f&&!SDL_RenderIsClipEnabled(renderer)&&
  !viewport.x&&!viewport.y&&viewport.w==rw&&viewport.h==rh&&!destination->x&&!destination->y&&destination->w==rw&&destination->h==rh&&(!main_window||(ww==rw&&wh==rh));
 if(!legacy){
  SDL_Rect support;if(!render_portable(&support)){reject();return false;}
  SDL_Surface underlay=*surface;underlay.pixels=sf.replay;
  unsigned radius=scaler==0||scaler==1||scaler==4||scaler==7?0:1;
  if(!selector_font_output_present_smooth(renderer,reference,&underlay,scalers[scaler].scaler32,destination,sf.output,&support,sf.cursor_mask,radius)){load_font_invalidate();return false;}
  sf.renderer=renderer;return true;
 }
 render();if(memcmp(sf.replay,sf.expected,SF_N)){reject();return false;}
 if(two)reduce2();
 if(!sf.texture){sf.texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,SF_OW,SF_OH);if(!sf.texture||SDL_SetTextureScaleMode(sf.texture,SDL_ScaleModeNearest)||SDL_SetTextureBlendMode(sf.texture,SDL_BLENDMODE_NONE)){load_font_invalidate();return false;}sf.renderer=renderer;}
 SDL_Rect source_rect={0,0,destination->w,destination->h};
 if(SDL_UpdateTexture(sf.texture,&source_rect,sf.output,destination->w*4)||SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,sf.texture,&source_rect,destination)){load_font_invalidate();return false;}
 SDL_RenderPresent(renderer);return true;
}
