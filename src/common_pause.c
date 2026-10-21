/* SPDX-License-Identifier: GPL-2.0-or-later
 * Fresh reconstruction, 2026-10-20. Native draw calls remain mandatory witnesses.
 * This module has no gameplay admission allowlist and never writes INDEX8. */
#include "common_pause.h"
#include "common_menu_fonts.h"
#include "selector_font_output.h"
#include "font.h"
#include "fonthand.h"
#include "helptext.h"
#include "palette.h"
#include "sprite.h"
#include "video.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { W=320,H=200,N=64000,CW=1280,CH=800,LAYER_BYTES=CW*CH*4,MAX_COMMANDS=256,MAX_EVENTS=30000,MAX_CURSOR=24*28 };
enum Stage { IDLE, INITIAL, BOX, SAVE_PENDING, SAVED, RESTORE_PENDING, FRAME_WAIT, FRAME, RUN, BAR, READY, CURSOR, CURSOR_DONE };
struct Identity {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;SDL_Palette *palette;SDL_Color *palette_colors;SDL_PixelFormat *rgb_format;Uint32 rgb_format_code,rgb_masks[4];SDL_Color indexed_palette[256];Uint32 rgb[256];};
struct Command {int x,y,value;unsigned bank,id,op,hue;};
struct Event {Uint16 position;Uint8 index,style;};
static const char *const esc_text[16]={"Music Volume","Sound Volume","Detail Level","Game Speed","Return to Game","Quit Level","Low","Normal","High","Pentium","Laptop VGA","Wild","Slug Mode","Slower","Slow","Turbo"};
static const unsigned detail_run[6]={6,7,8,9,10,11},speed_run[5]={12,13,14,7,15};
static const unsigned help_index[6]={14,14,27,28,25,26};
static const char *const help_text[6]={"Change volume with the left/right arrow keys.","Change volume with the left/right arrow keys.","Change detail level with the left/right arrow keys.","Change game speed with the left/right arrow keys.","Continue playing the level.","Quit playing the level."};
static const SDL_Rect boxes[4]={{3,13,215,125},{5,15,211,121},{3,143,255,15},{5,145,251,11}};
static struct {
 struct Identity identity;Uint32 *rgba;size_t bytes;unsigned density,epoch,captured_epoch;
 bool valid,pending;Uint8 expected[N],dirty[N];
} snap;
static struct {
 bool active,glyph,enhance,provider_acquired,cursor_sprite,cursor_presented;
 enum CommonPauseKind kind;enum Stage stage;SDL_Surface *screen,*backup;void *backup_pixels;SDL_PixelFormat *backup_format;
 Uint32 *work,*layer;SDL_Texture *texture;SDL_Renderer *renderer;unsigned density,width,height,source_banks,box_count,step,selected,detail,speed,volume[2];bool disabled[2];
 Uint8 base[N],saved[N],expected[N],replay[N],pre_cursor[N],cursor_mask[N];Uint32 palette[256];
 struct Command command[MAX_COMMANDS];unsigned commands,next,pixel,role,run_id;int run_x,run_y,run_value;unsigned run_hue;
 struct Event event[MAX_EVENTS];unsigned events,event_next;
 unsigned cursor_quad,cursor_events,cursor_next,cursor_saved_count;int cursor_x,cursor_y;
 struct Event cursor_event[168];Uint16 cursor_saved_pos[MAX_CURSOR];Uint32 cursor_under[MAX_CURSOR*8*8],cursor_layer[MAX_CURSOR*16];
} cp;
static CommonPauseEscProvider provider;
static char directory[1024];
static unsigned epoch=1;
static uint64_t hash(const void *p_,size_t n){const Uint8 *p=p_;uint64_t h=UINT64_C(14695981039346656037);while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static bool geometry(const SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==W&&s->h==H&&s->pitch==W&&s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&s->clip_rect.x==0&&s->clip_rect.y==0&&s->clip_rect.w==W&&s->clip_rect.h==H;}
static bool identity(void)
{
 const struct Identity *v=&snap.identity;SDL_Surface *s=v->surface;
 return s==VGAScreenSeg&&geometry(s)&&s->pixels==v->pixels&&s->format==v->format&&s->format->palette==v->palette&&
  (!v->palette||(v->palette->ncolors==256&&v->palette->colors==v->palette_colors&&!memcmp(v->indexed_palette,v->palette->colors,sizeof(v->indexed_palette))))&&main_window_tex_format==v->rgb_format&&
  main_window_tex_format&&main_window_tex_format->BitsPerPixel==32&&main_window_tex_format->BytesPerPixel==4&&
  main_window_tex_format->format==v->rgb_format_code&&main_window_tex_format->Rmask==v->rgb_masks[0]&&main_window_tex_format->Gmask==v->rgb_masks[1]&&main_window_tex_format->Bmask==v->rgb_masks[2]&&main_window_tex_format->Amask==v->rgb_masks[3]&&!memcmp(v->rgb,rgb_palette,sizeof(v->rgb))&&snap.captured_epoch==epoch;
}
static void reject(void){cp.active=false;cp.glyph=false;cp.stage=IDLE;}
static bool exact(void)
{
 if(!cp.active)return false;
 if(!identity()||cp.screen!=snap.identity.surface||!geometry(cp.screen)||memcmp(cp.screen->pixels,cp.expected,N)||
  (cp.kind==COMMON_PAUSE_ESC&&(!geometry(cp.backup)||cp.backup!=VGAScreen2||cp.backup->pixels!=cp.backup_pixels||cp.backup->format!=cp.backup_format))){reject();return false;}
 return true;
}
static Uint8 shade(Uint8 v){return (v&240)|((v&15)/2);}
static Uint8 tone(unsigned role,int value){Uint8 v=(Uint8)((int)role+value);if(v>15)v=v>=31?0:15;return v;}
static Uint8 face(unsigned role,unsigned hue,int value,unsigned op){return op==COMMON_PAUSE_UNSAFE?(Uint8)((hue<<4)|((int)role+value)):(Uint8)((hue<<4)|tone(role,value));}
static Uint32 darken(Uint32 c){Uint32 o=UINT32_C(0xff000000);for(unsigned s=0;s<24;s+=8)o|=((((c>>s)&255)*255+255)/510)<<s;return o;}
static Uint32 over(Uint32 dst,Uint32 color,unsigned a){Uint32 o=(a+(((dst>>24)*(255-a)+127)/255))<<24;for(unsigned s=0;s<24;s+=8)o|=((((color>>s)&255)*a+((dst>>s)&255)*(255-a)+127)/255)<<s;return o;}
static void classic_cell(unsigned p,Uint8 index,unsigned style)
{
 unsigned d=cp.density,x=p%W,y=p/W;
 for(unsigned sy=0;sy<d;sy++)for(unsigned sx=0;sx<d;sx++){Uint32 *v=&cp.work[(y*d+sy)*cp.width+x*d+sx];*v=style==2?darken(*v):cp.palette[index];}
 for(unsigned sy=0;sy<4;sy++)memset(cp.layer+(y*4+sy)*CW+x*4,0,4*sizeof(Uint32));
}
void common_pause_release_texture(void){if(cp.texture)SDL_DestroyTexture(cp.texture);cp.texture=NULL;cp.renderer=NULL;if(cp.layer)selector_font_output_release();}
void common_pause_end(void)
{
 common_pause_release_texture();if(cp.provider_acquired&&provider.release)provider.release(provider.context);
 free(cp.work);free(cp.layer);memset(&cp,0,sizeof(cp));snap.valid=snap.pending=false;
}
void common_pause_snapshot_reset(void){common_pause_end();free(snap.rgba);memset(&snap,0,sizeof(snap));if(++epoch==0)++epoch;}
void common_pause_invalidate(void){common_pause_snapshot_reset();}
void common_pause_table_reset(unsigned b){common_menu_fonts_table_reset(b);if(b<3&&cp.active&&(cp.source_banks&(1u<<b)))common_pause_end();}
void common_pause_set_directory(const char *p){common_pause_end();common_menu_fonts_shutdown();directory[0]=0;if(p&&strlen(p)<sizeof(directory))strcpy(directory,p);}
const char *common_pause_esc_text(unsigned n){return n<16?esc_text[n]:NULL;}
void common_pause_set_esc_provider(const CommonPauseEscProvider *p){if(cp.kind==COMMON_PAUSE_ESC)common_pause_end();memset(&provider,0,sizeof(provider));if(p)provider=*p;}
bool common_pause_owns_display(void){return cp.active;}
void common_pause_snapshot_stage(SDL_Surface *s,const void *rgba,int pitch,int width,int height,unsigned d)
{
 if(cp.active)return;
 /* A new attempt reuses the sole framebuffer and retires its predecessor.
  * If staging or submission fails, classic fallback is safer than claiming
  * the overwritten bytes still represent the previous submitted frame. */
 snap.pending=snap.valid=false;
 if(s!=VGAScreenSeg||!geometry(s)||!rgba||(d!=4&&d!=8)||width!=(int)(W*d)||height!=(int)(H*d)||pitch<width*4||!main_window_tex_format||main_window_tex_format->BitsPerPixel!=32||main_window_tex_format->BytesPerPixel!=4)return;
 size_t bytes=(size_t)width*height*4;
 if(snap.bytes!=bytes){Uint32 *p=malloc(bytes);if(!p)return;free(snap.rgba);snap.rgba=p;snap.bytes=bytes;}
 for(int y=0;y<height;y++){
  const Uint32 *row=(const Uint32 *)((const Uint8 *)rgba+(size_t)y*pitch);
  for(int x=0;x<width;x++)if((row[x]>>24)!=255)return;
  memcpy(snap.rgba+(size_t)y*width,row,(size_t)width*4);
 }
 snap.identity.surface=s;snap.identity.pixels=s->pixels;snap.identity.format=s->format;snap.identity.palette=s->format->palette;
 snap.identity.palette_colors=s->format->palette?s->format->palette->colors:NULL;snap.identity.rgb_format=main_window_tex_format;
 if(s->format->palette){if(s->format->palette->ncolors!=256||!s->format->palette->colors)return;memcpy(snap.identity.indexed_palette,s->format->palette->colors,sizeof(snap.identity.indexed_palette));}
 snap.identity.rgb_format_code=main_window_tex_format->format;snap.identity.rgb_masks[0]=main_window_tex_format->Rmask;snap.identity.rgb_masks[1]=main_window_tex_format->Gmask;snap.identity.rgb_masks[2]=main_window_tex_format->Bmask;snap.identity.rgb_masks[3]=main_window_tex_format->Amask;
 memcpy(snap.identity.rgb,rgb_palette,sizeof(snap.identity.rgb));memcpy(snap.expected,s->pixels,N);memset(snap.dirty,0,N);
 snap.density=d;snap.captured_epoch=epoch;snap.pending=true;
}
void common_pause_snapshot_commit(void)
{
 if(!snap.pending)return;snap.pending=false;
 snap.valid=identity()&&!memcmp(snap.identity.surface->pixels,snap.expected,N);
}
void common_pause_snapshot_discard_candidate(void){if(snap.pending){snap.pending=false;snap.valid=false;}}
static bool literal(const char *text,const char *wanted){return !memcmp(text,wanted,strlen(wanted)+1);}
static bool strings(void)
{
 if(cp.kind==COMMON_PAUSE_P)return literal(miscText[22],"PAUSED");
 for(unsigned i=0;i<6;i++)if(!literal(inGameText[i],esc_text[i])||!literal(detailLevel[i],esc_text[detail_run[i]])||!literal(mainMenuHelp[help_index[i]],help_text[i]))return false;
 for(unsigned i=0;i<5;i++)if(!literal(gameSpeedText[i],esc_text[speed_run[i]]))return false;
 return true;
}
static bool run_view(unsigned id,CommonPauseNaturalRun *v)
{
 if(id>=16||!provider.get||!provider.get(provider.context,id,v)||!v->alpha||!v->roles||!v->width||!v->height||v->width>900||v->height>96||v->pitch<v->width||v->pitch>1024||v->x < -64||v->x>64||v->y < -64||v->y>64)return false;
 for(unsigned y=0;y<v->height;y++)for(unsigned x=0;x<v->width;x++){unsigned n=y*v->pitch+x,a=v->alpha[n],r=v->roles[n];if(a?(r<12||r>15):r!=0)return false;}
 return true;
}
static void base_work(void)
{
 memcpy(cp.work,snap.rgba,snap.bytes);memset(cp.layer,0,LAYER_BYTES);
 for(unsigned p=0;p<N;p++)if(snap.dirty[p])classic_cell(p,cp.base[p],0);
}
bool common_pause_begin(enum CommonPauseKind kind,SDL_Surface *s,SDL_Surface *backup)
{
 if(cp.active||cp.work||cp.layer){common_pause_end();return false;}
 if((kind!=COMMON_PAUSE_P&&kind!=COMMON_PAUSE_ESC)||!snap.valid||!identity()||s!=snap.identity.surface||memcmp(s->pixels,snap.expected,N)||
  (kind==COMMON_PAUSE_ESC&&(backup!=VGAScreen2||!geometry(backup))))return false;
 cp.kind=kind;cp.source_banks=kind==COMMON_PAUSE_P?1:6;
 if(!strings()||!common_menu_fonts_acquire(directory,cp.source_banks,kind==COMMON_PAUSE_P?1:0))return false;
 if(kind==COMMON_PAUSE_ESC){
  if(!provider.acquire||!provider.validate||!provider.get||!provider.release||!provider.acquire(provider.context))return false;cp.provider_acquired=true;
  if(!provider.validate(provider.context)){common_pause_end();return false;}
  for(unsigned i=0;i<16;i++){CommonPauseNaturalRun v;if(!run_view(i,&v)){common_pause_end();return false;}}
 }
 cp.work=malloc(snap.bytes);cp.layer=malloc(LAYER_BYTES);if(!cp.work||!cp.layer){common_pause_end();return false;}
 cp.screen=s;cp.backup=backup;cp.backup_pixels=backup?backup->pixels:NULL;cp.backup_format=backup?backup->format:NULL;
 cp.density=snap.density;cp.width=W*cp.density;cp.height=H*cp.density;memcpy(cp.base,snap.expected,N);memcpy(cp.expected,snap.expected,N);
 for(unsigned i=0;i<256;i++){Uint8 r,g,b;SDL_GetRGB(snap.identity.rgb[i],snap.identity.rgb_format,&r,&g,&b);cp.palette[i]=UINT32_C(0xff000000)|((Uint32)r<<16)|((Uint32)g<<8)|b;}
 cp.active=true;cp.stage=INITIAL;base_work();return true;
}
static bool add_event(unsigned p,unsigned style,Uint8 index)
{
 if(p>=N||cp.events==MAX_EVENTS){reject();return false;}
 cp.event[cp.events++]=(struct Event){(Uint16)p,index,(Uint8)style};cp.replay[p]=index;return true;
}
static bool rect_event(int x,int y,int w,int h,int index)
{
 if(x<0||y<0||w<=0||h<=0||x>W-w||y>H-h){reject();return false;}
 for(int yy=y;yy<y+h;yy++)for(int xx=x;xx<x+w;xx++){unsigned p=yy*W+xx;if(!add_event(p,index<0?2:0,index<0?shade(cp.replay[p]):(Uint8)index))return false;}return true;
}
void common_pause_box_begin(unsigned n)
{
 if(!exact())return;if(cp.kind!=COMMON_PAUSE_ESC||cp.stage!=INITIAL||n!=cp.box_count||n>=4){reject();return;}
 cp.events=cp.event_next=0;memcpy(cp.replay,cp.expected,N);SDL_Rect r=boxes[n];if(!rect_event(r.x,r.y,r.w,r.h,-1))return;cp.stage=BOX;
}
void common_pause_primitive_end(void)
{
 if(!exact())return;if((cp.stage!=BOX&&cp.stage!=BAR)||cp.event_next!=cp.events){reject();return;}
 if(cp.stage==BOX){++cp.box_count;cp.stage=INITIAL;}else{++cp.step;cp.stage=FRAME;}
}
void common_pause_save_before(void){if(!exact())return;if(cp.kind!=COMMON_PAUSE_ESC||cp.stage!=INITIAL||cp.box_count!=4){reject();return;}cp.stage=SAVE_PENDING;}
void common_pause_save_after(void)
{
 if(!exact())return;if(cp.stage!=SAVE_PENDING||memcmp(cp.backup->pixels,cp.expected,N)){reject();return;}
 memcpy(cp.saved,cp.expected,N);cp.stage=SAVED;
}
void common_pause_restore_before(void)
{
 if(!exact())return;if(cp.kind!=COMMON_PAUSE_ESC||(cp.stage!=SAVED&&cp.stage!=READY)||memcmp(cp.backup->pixels,cp.saved,N)){reject();return;}cp.stage=RESTORE_PENDING;
}
void common_pause_restore_after(void)
{
 if(!cp.active)return;if(cp.stage!=RESTORE_PENDING||!identity()||!geometry(cp.backup)||cp.backup->pixels!=cp.backup_pixels||memcmp(cp.screen->pixels,cp.saved,N)||memcmp(cp.backup->pixels,cp.saved,N)){reject();return;}
 memcpy(cp.expected,cp.saved,N);base_work();
 for(unsigned i=0;i<4;i++){SDL_Rect r=boxes[i];for(int y=r.y;y<r.y+r.h;y++)for(int x=r.x;x<r.x+r.w;x++)classic_cell(y*W+x,0,2);}
 cp.stage=FRAME_WAIT;
}
void common_pause_frame_begin(unsigned selected,unsigned detail,unsigned speed,unsigned mv,unsigned fv,bool md,bool fd)
{
 if(!exact())return;if(cp.kind!=COMMON_PAUSE_ESC||cp.stage!=FRAME_WAIT||selected>=6||detail>=6||speed>=5||mv>255||fv>255||!strings()||!provider.validate(provider.context)){reject();return;}
 cp.selected=selected;cp.detail=detail;cp.speed=speed;cp.volume[0]=mv;cp.volume[1]=fv;cp.disabled[0]=md;cp.disabled[1]=fd;cp.step=0;cp.stage=FRAME;
}
void common_pause_bar_begin(unsigned row)
{
 if(!exact())return;if(cp.stage!=FRAME||row>1||cp.step!=(row?3u:1u)){reject();return;}
 cp.events=cp.event_next=0;memcpy(cp.replay,cp.expected,N);unsigned amount=(cp.volume[row]+6)/12,col=cp.disabled[row]?12:16;int y=20+20*row;
 for(unsigned i=0;i<amount;i++){int x=120+4*i;if(!rect_event(x+2,y+2,3,13,-1)||!rect_event(x,y,3,13,col+12)||!rect_event(x,y,3,1,col+13)||!rect_event(x,y,1,1,col+15)||!rect_event(x,y+12,3,1,col+11))return;}
 cp.stage=BAR;
}
static bool command(int x,int y,unsigned bank,unsigned id,unsigned op,unsigned hue,int value)
{
 CommonMenuGlyph g;if(cp.commands==MAX_COMMANDS||!common_menu_fonts_glyph(bank,id,&g)||x<0||y<0||x>W-(int)g.width||y>H-(int)g.height){reject();return false;}
 cp.command[cp.commands++]=(struct Command){x,y,value,bank,id,op,hue};return true;
}
static bool build_commands(const char *text,unsigned bank,int x,int y,unsigned hue,int value,bool interleaved,bool unsafe)
{
 cp.commands=cp.next=0;
 if(!interleaved){
  int pen=x;for(unsigned i=0;text[i];i++){unsigned ch=(unsigned char)text[i];if(ch==' '){pen+=6;continue;}int id=font_ascii[ch];CommonMenuGlyph g;if(ch>=128||id<0||!common_menu_fonts_glyph(bank,(unsigned)id,&g)||!command(pen+2,y+2,bank,(unsigned)id,COMMON_PAUSE_DARK,0,0))return false;pen+=g.advance;}
 }
 for(unsigned i=0;text[i];i++){
  unsigned ch=(unsigned char)text[i];if(ch==' '){x+=6;continue;}
  int id=font_ascii[ch];CommonMenuGlyph g;if(ch>=128||id<0||!common_menu_fonts_glyph(bank,(unsigned)id,&g)){reject();return false;}
  if(interleaved&&!command(x+2,y+2,bank,(unsigned)id,COMMON_PAUSE_DARK,0,0))return false;
  if(!command(x,y,bank,(unsigned)id,unsafe?COMMON_PAUSE_UNSAFE:COMMON_PAUSE_FACE,hue,value))return false;x+=g.advance;
 }
 return cp.commands!=0;
}
void common_pause_run_begin(enum CommonPauseRun role,unsigned row,SDL_Surface *surface,int x,int y,const char *text,unsigned font,unsigned alignment,unsigned hue,int value)
{
 if(!exact())return;
 size_t length=0;if(text)while(length<66&&text[length])++length;
 if(surface!=cp.screen||!text||!length||length==66||alignment!=left_aligned||cp.glyph||!strings()||!common_menu_fonts_validate(cp.source_banks)){reject();return;}
 bool interleaved=false,unsafe=false;cp.enhance=true;
 if(cp.kind==COMMON_PAUSE_P){
  if(cp.stage!=INITIAL||role!=COMMON_PAUSE_LABEL||row||x!=120||y!=90||font!=0||hue!=15||value!=-3||strcmp(text,"PAUSED")){reject();return;}interleaved=unsafe=true;
 }else{
  if(cp.stage!=FRAME){reject();return;}
  unsigned want_step=0;int ex=10,ey=0,ev=-4+(row==cp.selected?2:0);unsigned ef=1,eh=15;const char *wanted=NULL;
  if(role==COMMON_PAUSE_NAME&&row<6){static const unsigned step[6]={0,2,4,6,8,9};want_step=step[row];ey=20+20*row;wanted=esc_text[row];cp.run_id=row;}
  else if(role==COMMON_PAUSE_DETAIL&&row==2){want_step=5;ex=120;ey=60;wanted=esc_text[detail_run[cp.detail]];cp.run_id=detail_run[cp.detail];}
  else if(role==COMMON_PAUSE_SPEED&&row==3){want_step=7;ex=120;ey=80;wanted=esc_text[speed_run[cp.speed]];cp.run_id=speed_run[cp.speed];}
  else if(role==COMMON_PAUSE_HELP&&row==cp.selected){want_step=10;ex=10;ey=147;ef=2;eh=14;ev=6;wanted=help_text[cp.selected];interleaved=true;cp.enhance=false;}
  if(!wanted||cp.step!=want_step||x!=ex||y!=ey||font!=ef||hue!=eh||value!=ev||strcmp(text,wanted)){reject();return;}
 }
 memcpy(cp.replay,cp.expected,N);cp.run_x=x;cp.run_y=y;cp.run_hue=hue;cp.run_value=value;cp.role=role;
 if(!build_commands(text,font,x,y,hue,value,interleaved,unsafe))return;cp.stage=RUN;
}
static void skip_transparent(void)
{
 if(cp.next>=cp.commands)return;struct Command *c=&cp.command[cp.next];CommonMenuGlyph g;if(!common_menu_fonts_glyph(c->bank,c->id,&g)){reject();return;}
 while(cp.pixel<g.width*g.height&&g.source[cp.pixel]==255)++cp.pixel;
}
void common_pause_glyph_begin(SDL_Surface *surface,int x,int y,unsigned bank,unsigned id,enum CommonPauseGlyph op,unsigned hue,int value)
{
 if(!cp.active)return;if(!exact())return;
 if(cp.stage!=RUN||cp.glyph||cp.next>=cp.commands){reject();return;}struct Command *c=&cp.command[cp.next];
 if(surface!=cp.screen||x!=c->x||y!=c->y||bank!=c->bank||id!=c->id||op!=c->op||hue!=c->hue||value!=c->value){reject();return;}
 cp.glyph=true;cp.pixel=0;skip_transparent();
}
void common_pause_glyph_end(void)
{
 if(!cp.active)return;if(!exact())return;CommonMenuGlyph g;
 if(cp.stage!=RUN||!cp.glyph||cp.next>=cp.commands||!common_menu_fonts_glyph(cp.command[cp.next].bank,cp.command[cp.next].id,&g)||cp.pixel!=g.width*g.height){reject();return;}
 cp.glyph=false;++cp.next;
}
static void render_p(void)
{
 for(unsigned i=0;i<cp.commands;i++){
  struct Command *c=&cp.command[i];CommonMenuGlyph g;if(!common_menu_fonts_glyph(c->bank,c->id,&g)||!g.alpha||!g.roles){reject();return;}
  for(unsigned y=0;y<g.height*4;y++)for(unsigned x=0;x<g.width*4;x++){
   unsigned n=y*g.atlas_pitch+x,a=g.alpha[n];if(!a)continue;unsigned p=(c->y+y/4)*W+c->x+x/4;
   Uint8 index=c->op==COMMON_PAUSE_DARK?shade(cp.replay[p]):face(g.roles[n],c->hue,c->value,c->op);
   unsigned at=(c->y*4+y)*CW+c->x*4+x;cp.layer[at]=over(cp.layer[at],cp.palette[index],a);
  }
  for(unsigned y=0;y<g.height;y++)for(unsigned x=0;x<g.width;x++){unsigned r=g.source[y*g.width+x];if(r==255)continue;unsigned p=(c->y+y)*W+c->x+x;cp.replay[p]=c->op==COMMON_PAUSE_DARK?shade(cp.replay[p]):face(r,c->hue,c->value,c->op);}
 }
}
static void render_esc(void)
{
 CommonPauseNaturalRun v;if(!provider.validate(provider.context)||!run_view(cp.run_id,&v)){reject();return;}
 int x0=cp.run_x*4+v.x,y0=cp.run_y*4+v.y;
 if(x0<0||y0<0||x0+(int)v.width+8>CW||y0+(int)v.height+8>CH){reject();return;}
 for(unsigned pass=0;pass<2;pass++)for(unsigned y=0;y<v.height;y++)for(unsigned x=0;x<v.width;x++){
  unsigned n=y*v.pitch+x,a=v.alpha[n];if(!a)continue;unsigned xx=x0+x+(pass?0:8),yy=y0+y+(pass?0:8),p=(yy/4)*W+xx/4;
  Uint8 index=pass?face(v.roles[n],cp.run_hue,cp.run_value,COMMON_PAUSE_FACE):shade(cp.replay[p]);unsigned at=yy*CW+xx;cp.layer[at]=over(cp.layer[at],cp.palette[index],a);
 }
}
void common_pause_run_end(void)
{
 if(!exact())return;if(cp.stage!=RUN||cp.glyph||cp.next!=cp.commands){reject();return;}
 if(cp.enhance){if(cp.kind==COMMON_PAUSE_P)render_p();else render_esc();if(!cp.active)return;}
 if(cp.kind==COMMON_PAUSE_P)cp.stage=READY;else{++cp.step;cp.stage=FRAME;}
}
void common_pause_frame_end(void){if(!exact())return;if(cp.kind!=COMMON_PAUSE_ESC||cp.stage!=FRAME||cp.step!=11||cp.glyph){reject();return;}cp.stage=READY;}
void common_pause_cursor_begin(void)
{
 if(!exact())return;if(cp.kind!=COMMON_PAUSE_ESC||cp.stage!=READY){reject();return;}
 memcpy(cp.pre_cursor,cp.expected,N);memset(cp.cursor_mask,0,N);cp.cursor_saved_count=0;cp.cursor_quad=0;cp.cursor_sprite=false;cp.cursor_presented=false;cp.stage=CURSOR;
}
void common_pause_cursor_sprite_begin(SDL_Surface *s,int x,int y,const void *data,size_t size,unsigned id)
{
 if(!cp.active)return;if(!exact())return;
 static const unsigned ids[4]={273,274,292,293};static const int dx[4]={0,12,0,12},dy[4]={0,0,14,14};
 if(cp.stage!=CURSOR||cp.cursor_sprite||cp.cursor_quad>=4||s!=cp.screen||!data||data!=shopSpriteSheet.data||size!=shopSpriteSheet.size||size!=29941||hash(data,size)!=UINT64_C(0x8c478c429071f043)||id!=ids[cp.cursor_quad]){reject();return;}
 if(!cp.cursor_quad){if(x < -24||x>=W||y < -28||y>=H){reject();return;}cp.cursor_x=x;cp.cursor_y=y;}
 if(x!=cp.cursor_x+dx[cp.cursor_quad]||y!=cp.cursor_y+dy[cp.cursor_quad]){reject();return;}
 const Uint8 *p=data;unsigned off=p[(id-1)*2]|((unsigned)p[(id-1)*2+1]<<8),xx=0,yy=0;
 cp.cursor_events=cp.cursor_next=0;
 for(unsigned k=off;;k++){
  if(k>=size||yy>14){reject();return;}unsigned v=p[k];if(v==15)break;
  unsigned count=v>>4;xx+=v&15;
  if(!count){if(xx!=12){reject();return;}++yy;xx=0;continue;}
  if(xx+count>12||yy>=14||k+count>=size){reject();return;}
  while(count--){Uint8 index=p[++k];if(x+(int)xx>=0&&x+(int)xx<W&&y+(int)yy>=0&&y+(int)yy<H){
   if(cp.cursor_events==168){reject();return;}cp.cursor_event[cp.cursor_events++]=(struct Event){(Uint16)((y+yy)*W+x+xx),index,0};
  }++xx;}
 }
 cp.cursor_sprite=true;
}
void common_pause_cursor_sprite_end(void)
{
 if(!cp.active)return;if(!exact())return;
 if(cp.stage!=CURSOR||!cp.cursor_sprite||cp.cursor_next!=cp.cursor_events){reject();return;}cp.cursor_sprite=false;++cp.cursor_quad;
}
void common_pause_cursor_done(void)
{
 if(!exact())return;if(cp.stage!=CURSOR||cp.cursor_sprite||(cp.cursor_quad&&cp.cursor_quad!=4)){reject();return;}cp.stage=CURSOR_DONE;
}
void common_pause_cursor_erased(void)
{
 if(!cp.active)return;
 if(cp.stage!=CURSOR_DONE||!identity()||memcmp(cp.screen->pixels,cp.pre_cursor,N)){reject();return;}
 memcpy(cp.expected,cp.pre_cursor,N);unsigned d=cp.density;
 for(unsigned i=0;i<cp.cursor_saved_count;i++){
  unsigned p=cp.cursor_saved_pos[i],x=p%W,y=p/W;
  for(unsigned sy=0;sy<d;sy++)memcpy(cp.work+(y*d+sy)*cp.width+x*d,cp.cursor_under+i*64+sy*d,d*4);
  for(unsigned sy=0;sy<4;sy++)memcpy(cp.layer+(y*4+sy)*CW+x*4,cp.cursor_layer+i*16+sy*4,16);
 }
 memset(cp.cursor_mask,0,N);cp.stage=READY;
}
static bool cursor_save(unsigned p)
{
 if(cp.cursor_mask[p])return true;if(cp.cursor_saved_count==MAX_CURSOR){reject();return false;}
 unsigned i=cp.cursor_saved_count++,x=p%W,y=p/W,d=cp.density;cp.cursor_saved_pos[i]=(Uint16)p;
 for(unsigned sy=0;sy<d;sy++)memcpy(cp.cursor_under+i*64+sy*d,cp.work+(y*d+sy)*cp.width+x*d,d*4);
 for(unsigned sy=0;sy<4;sy++)memcpy(cp.cursor_layer+i*16+sy*4,cp.layer+(y*4+sy)*CW+x*4,16);
 cp.cursor_mask[p]=1;return true;
}
void common_pause_pixel(SDL_Surface *s,Uint8 *address,int style)
{
 /* Ledger is observation-based: equality of indices does not imply no write. */
 if(!cp.active){
  /* No native writes belong between the locked-texture snapshot and its
   * submission. Even an equal-index write cancels that uncommitted proof. */
  if(snap.pending&&s==snap.identity.surface){snap.pending=snap.valid=false;return;}
  if(!snap.valid||s!=snap.identity.surface)return;
  if(!identity()){snap.valid=false;return;}
  uintptr_t p=(uintptr_t)address,b=(uintptr_t)snap.identity.pixels;
  if(p<b||p-b>=N||(style!=0&&style!=2)){snap.valid=false;return;}
  snap.expected[p-b]=*address;snap.dirty[p-b]=1;return;
 }
 if(s!=cp.screen||!identity()){reject();return;}
 uintptr_t a=(uintptr_t)address,b=(uintptr_t)snap.identity.pixels;if(a<b||a-b>=N){reject();return;}unsigned p=(unsigned)(a-b);
 if(cp.stage==CURSOR){
  if(style!=0||!cp.cursor_sprite||cp.cursor_next>=cp.cursor_events||cp.cursor_event[cp.cursor_next].position!=p||cp.cursor_event[cp.cursor_next].index!=*address||!cursor_save(p)){reject();return;}
  ++cp.cursor_next;cp.expected[p]=*address;classic_cell(p,*address,0);return;
 }
 if(cp.stage==BOX||cp.stage==BAR){
  if(cp.event_next>=cp.events){reject();return;}const struct Event *e=&cp.event[cp.event_next];
  if(e->position!=p||e->index!=*address||e->style!=style){reject();return;}++cp.event_next;cp.expected[p]=*address;classic_cell(p,*address,(unsigned)style);return;
 }
 if(cp.stage!=RUN||!cp.glyph||cp.next>=cp.commands){reject();return;}
 const struct Command *c=&cp.command[cp.next];CommonMenuGlyph g;if(!common_menu_fonts_glyph(c->bank,c->id,&g)||cp.pixel>=g.width*g.height){reject();return;}
 unsigned wanted=(c->y+cp.pixel/g.width)*W+c->x+cp.pixel%g.width;bool shadow=c->op==COMMON_PAUSE_DARK;
 Uint8 index=shadow?shade(cp.expected[p]):face(g.source[cp.pixel],c->hue,c->value,c->op);
 if(p!=wanted||style!=(shadow?2:0)||*address!=index){reject();return;}
 cp.expected[p]=index;if(!cp.enhance)classic_cell(p,index,(unsigned)style);++cp.pixel;skip_transparent();
}
void common_pause_rect(SDL_Surface *s,const SDL_Rect *rect)
{
 if((!cp.active&&!snap.valid&&!snap.pending)||s!=snap.identity.surface)return;
 if(!geometry(s)){if(cp.active)reject();snap.pending=snap.valid=false;return;}
 int64_t x=rect?rect->x:0,y=rect?rect->y:0,w=rect?rect->w:W,h=rect?rect->h:H;
 if(w<=0||h<=0)return;int64_t right=x+w,bottom=y+h;if(x<0)x=0;if(y<0)y=0;if(right>W)right=W;if(bottom>H)bottom=H;
 for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)common_pause_pixel(s,(Uint8 *)s->pixels+yy*W+xx,0);
}
bool common_pause_present(SDL_Renderer *renderer,SDL_Texture *reference,SDL_Surface *s,const SDL_Rect *dst,bool foreign_owner)
{
 (void)reference;
 if(!exact())return false;
 if(foreign_owner||!renderer||s!=cp.screen||!dst||dst->w<=0||dst->h<=0||(cp.stage!=READY&&cp.stage!=CURSOR_DONE)||!strings()||!common_menu_fonts_validate(cp.source_banks)||
  (cp.kind==COMMON_PAUSE_ESC&&(!provider.validate(provider.context)||memcmp(cp.backup->pixels,cp.saved,N)))){reject();return false;}
 if(cp.renderer!=renderer)common_pause_release_texture();
 if(!cp.texture){cp.texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,cp.width,cp.height);cp.renderer=renderer;}
 if(!cp.texture||SDL_SetTextureBlendMode(cp.texture,SDL_BLENDMODE_NONE)||SDL_SetTextureScaleMode(cp.texture,SDL_ScaleModeNearest)||SDL_UpdateTexture(cp.texture,NULL,cp.work,cp.width*4)||
  SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,cp.texture,NULL,dst)){reject();return false;}
 SDL_Rect support={0,0,CW,CH};if(!selector_font_output_overlay(renderer,dst,cp.layer,&support)){reject();return false;}
 SDL_RenderPresent(renderer);if(cp.stage==CURSOR_DONE)cp.cursor_presented=true;return true;
}
size_t common_pause_retained_bytes(void)
{
 return sizeof(snap)+sizeof(cp)+snap.bytes+(cp.work?snap.bytes:0)+(cp.layer?LAYER_BYTES:0)+common_menu_fonts_retained_bytes();
}
