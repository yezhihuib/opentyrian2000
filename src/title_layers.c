/* SPDX-License-Identifier: GPL-2.0-or-later
 * Explicit title-only display lease. Original indexed writes, palettes, input,
 * delays, motion and RNG remain owned by the original engine.
 */
#include "title_layers.h"
#include "hd_cursor.h"
#include "font.h"
#include "selector_font_output.h"
#include "fonthand.h"
#include "palette.h"
#include "sprite.h"
#include "video.h"
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define TL_OPEN(p) _open(p,_O_RDONLY|_O_BINARY|_O_NOINHERIT)
#define TL_READ _read
#define TL_CLOSE _close
#define TL_FSTAT _fstat
#define TL_STAT struct _stat
#define TL_REGULAR(m) (((m)&_S_IFMT)==_S_IFREG)
#else
#include <unistd.h>
#define TL_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define TL_READ read
#define TL_CLOSE close
#define TL_FSTAT fstat
#define TL_STAT struct stat
#define TL_REGULAR(m) S_ISREG(m)
#endif
#ifndef TITLE_PIC4_FNV
#define TITLE_PIC4_FNV UINT64_C(0x9a3f7cb8ec37073e)
#endif
#ifndef TITLE_PAL_FNV
#define TITLE_PAL_FNV UINT64_C(0x8f64628a08533287)
#endif
#ifndef TITLE_146_INDEX_FNV
#define TITLE_146_INDEX_FNV UINT64_C(0x30f8dbf0554a03ae)
#endif
#ifndef TITLE_146_MASK_FNV
#define TITLE_146_MASK_FNV UINT64_C(0x0cb7de8084912543)
#endif
#ifndef TITLE_146_RLE_FNV
#define TITLE_146_RLE_FNV UINT64_C(0xf19983d3c8b5e3a1)
#endif
#ifndef TITLE_151_INDEX_FNV
#define TITLE_151_INDEX_FNV UINT64_C(0x4562ec954d257998)
#endif
#ifndef TITLE_151_MASK_FNV
#define TITLE_151_MASK_FNV UINT64_C(0xee71b0121c53f8df)
#endif
#ifndef TITLE_151_RLE_FNV
#define TITLE_151_RLE_FNV UINT64_C(0x9133efa73da3f836)
#endif

enum { TL_W=320, TL_H=200, TL_N=64000, TL_D=4, TL_OUT_N=1024000,
       TL_OUT_BYTES=4096000, TL_HEADER=80 };
enum Phase { PH_VERSION, PH_VERSION_DONE, PH_ART_START, PH_ART_FADE,
             PH_MOTION, PH_MENU_READY, PH_MENU_BUILD, PH_MENU_DONE,
             PH_UI_START, PH_UI_FADE, PH_LIVE, PH_OUT };
enum Stage { ST_NONE, ST_VERSION, ST_LOGO146, ST_LOGO151, ST_MENU, ST_HIGHLIGHT, ST_CURSOR };
static const struct {
 unsigned id,w,h,alpha_mode,x0,y0,x1,y1;
 uint64_t index_hash,mask_hash,rle_hash;
 const char *file;
} specs[3]={
 {4,320,200,0,0,0,1280,800,TITLE_PIC4_FNV,UINT64_C(0x9c9baa40cbccf525),0,"title-pic4-v1.hda"},
 {146,304,121,1,4,4,1216,484,TITLE_146_INDEX_FNV,TITLE_146_MASK_FNV,TITLE_146_RLE_FNV,"title-planet146-v1.hda"},
 {151,162,64,1,8,8,644,252,TITLE_151_INDEX_FNV,TITLE_151_MASK_FNV,TITLE_151_RLE_FNV,"title-planet151-v1.hda"}
};
struct Plane { Uint8 index[TL_N],coverage[TL_N]; };
static struct {
 bool active,animate,initial_done,pose_ready,checkpoint_valid,cursor_live,cursor_presented,highlight_ready;
 int phase,stage,checkpoint_kind,pending_save,pending_restore,motions_done,remaining;
 unsigned fade_first,fade_last,logo_count;
 int logo_x[2],logo_y[2],last_logo_offset;
 SDL_Surface *screen,*backup;
 void *pixels,*backup_pixels;
 SDL_PixelFormat *format,*backup_format;
 const Uint8 *rle[2]; unsigned rle_size[2],opaque_count[2];
 Uint8 pic4[TL_N],i146[304*121],m146[304*121],i151[162*64],m151[162*64];
 Uint8 expected[TL_N],checkpoint[TL_N],pre_cursor[TL_N];
 struct Plane version,menu,menu_base,cursor;
 SDL_Color expected_palette[256],target_palette[256],fade_target[256];
 Uint8 channel[256];
 Uint8 *rgba[3];
 Uint32 *output;
 SDL_Texture *texture;
} state;
static const char *asset_directory;
bool title_layers_owns_display(void) { return state.active; }
static void tm_end(void);
static bool tm_check(void);

static uint32_t tl_u32(const Uint8 *p)
{ return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24); }
static uint64_t tl_u64(const Uint8 *p) { return (uint64_t)tl_u32(p)|((uint64_t)tl_u32(p+4)<<32); }
static uint64_t tl_hash(const Uint8 *p,size_t n)
{ uint64_t h=UINT64_C(14695981039346656037);while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h; }
static uint64_t tl_palette_hash(const SDL_Color *p)
{
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned i=0;i<256;i++) {
  const Uint8 rgb[3]={p[i].r,p[i].g,p[i].b};
  for(unsigned c=0;c<3;c++)h=(h^rgb[c])*UINT64_C(1099511628211);
 }
 return h;
}
static Uint8 *tl_indices(unsigned i) { return i==0?state.pic4:i==1?state.i146:state.i151; }
static Uint8 *tl_mask(unsigned i) { return i==1?state.m146:state.m151; }
void title_layers_set_directory(const char *directory) { asset_directory=directory&&*directory?directory:NULL; }
void title_layers_release_texture(void)
{ if(state.texture)SDL_DestroyTexture(state.texture);state.texture=NULL;
  if(state.active||state.output)selector_font_output_release(); }
void title_layers_end(void)
{
 tm_end();
 title_layers_release_texture();
 for(unsigned i=0;i<3;i++){free(state.rgba[i]);state.rgba[i]=NULL;}
 free(state.output);state.output=NULL;state.active=false;state.stage=ST_NONE;
}
void title_layers_sprite_table_reset(unsigned int table)
{ if(table==PLANET_SHAPES)title_layers_end();else if(table==SMALL_FONT_SHAPES)tm_end(); }
static bool tl_geometry(SDL_Surface *s)
{ return s&&s->pixels&&s->format&&s->w==TL_W&&s->h==TL_H&&s->pitch==TL_W&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1; }
static bool tl_layout(void)
{
 return state.screen==VGAScreen&&state.screen==VGAScreenSeg&&state.backup==VGAScreen2&&
        tl_geometry(state.screen)&&tl_geometry(state.backup)&&state.screen->pixels==state.pixels&&
        state.backup->pixels==state.backup_pixels&&state.screen->format==state.format&&state.backup->format==state.backup_format;
}
static bool tl_sprites(void)
{
 if(sprite_table[PLANET_SHAPES].count<=151)return false;
 for(unsigned i=1;i<3;i++) {
  const Sprite *s=sprite(PLANET_SHAPES,specs[i].id);
  if(s->data!=state.rle[i-1]||s->size!=state.rle_size[i-1]||s->width!=specs[i].w||s->height!=specs[i].h||
     tl_hash(s->data,s->size)!=specs[i].rle_hash)return false;
 }
 return true;
}
static bool tl_palette_matches(void)
{
 if(!main_window_tex_format)return false;
 for(unsigned i=0;i<256;i++) {
  SDL_Color p=state.expected_palette[i];
  if(rgb_palette[i]!=SDL_MapRGB(main_window_tex_format,p.r,p.g,p.b))return false;
 }
 return true;
}
static bool tl_source_matches(void)
{
 return tl_layout()&&tl_sprites()&&!memcmp(state.pixels,state.expected,TL_N)&&
        (!state.checkpoint_valid||!memcmp(state.backup_pixels,state.checkpoint,TL_N));
}
static bool tl_check(void)
{
 if(!state.active)return false;
 if(!tl_source_matches()||!tl_palette_matches()){title_layers_end();return false;}
 (void)tm_check();
 return true;
}
static bool tl_decode(unsigned i)
{
 const Sprite *s=sprite(PLANET_SHAPES,specs[i].id);
 if(!s->data||!s->size||s->width!=specs[i].w||s->height!=specs[i].h||tl_hash(s->data,s->size)!=specs[i].rle_hash)return false;
 Uint8 *indices=tl_indices(i),*mask=tl_mask(i);
 unsigned x=0,y=0,count=0;
 for(unsigned k=0;k<s->size;k++) {
  Uint8 v=s->data[k];
  if(v==255){if(++k>=s->size)return false;x+=s->data[k];}
  else if(v==254)x=s->width;
  else if(v==253)++x;
  else {
   if(x>=s->width||y>=s->height||v>=240)return false;
   indices[y*s->width+x]=v;mask[y*s->width+x]=255;++count;++x;
  }
  if(x>s->width)return false;
  if(x==s->width){++y;x=0;}
  if(y>s->height)return false;
 }
 if(tl_hash(indices,(size_t)s->width*s->height)!=specs[i].index_hash||
    tl_hash(mask,(size_t)s->width*s->height)!=specs[i].mask_hash)return false;
 state.rle[i-1]=s->data;state.rle_size[i-1]=s->size;state.opaque_count[i-1]=count;
 return true;
}
static bool tl_read(int fd,Uint8 *out,unsigned n) {return TL_READ(fd,out,n)==(long)n;}
static Uint8 *tl_load(unsigned i,bool *allocation_failed)
{
 char path[1024];Uint8 header[TL_HEADER],extra,*rgba=NULL;TL_STAT st;bool ok=false;
 unsigned bytes=specs[i].w*specs[i].h*TL_D*TL_D*4;
 int n=snprintf(path,sizeof(path),"%s/%s",asset_directory,specs[i].file);
 if(n<0||(size_t)n>=sizeof(path))return NULL;
 int fd=TL_OPEN(path);if(fd<0)return NULL;
 if(TL_FSTAT(fd,&st)||!TL_REGULAR(st.st_mode)||st.st_size!=(long)(TL_HEADER+bytes)||!tl_read(fd,header,TL_HEADER))goto done;
 if(memcmp(header,"TLV1",4)||tl_u32(header+4)!=1||tl_u32(header+8)!=TL_D||tl_u32(header+12)!=specs[i].id||
    tl_u32(header+16)!=specs[i].w||tl_u32(header+20)!=specs[i].h||tl_u32(header+24)!=8||
    tl_u32(header+28)!=specs[i].alpha_mode||tl_u32(header+32)!=bytes||
    tl_u32(header+36)||tl_u32(header+40)||tl_u32(header+44)||tl_u64(header+48)!=specs[i].index_hash||
    tl_u64(header+56)!=specs[i].mask_hash||tl_u64(header+64)!=TITLE_PAL_FNV)goto done;
 rgba=malloc(bytes);
 if(!rgba){*allocation_failed=true;goto done;}
 if(!tl_read(fd,rgba,bytes)||TL_READ(fd,&extra,1)!=0||tl_hash(rgba,bytes)!=tl_u64(header+72))goto done;
 for(unsigned p=0;p<bytes/4;p++) {
  const Uint8 *v=rgba+4*p;unsigned x=p%(specs[i].w*TL_D),y=p/(specs[i].w*TL_D);
  if(!i) {if(v[3]!=255)goto done;}
  else if((!v[3]&&(v[0]||v[1]||v[2]))||
          ((x<specs[i].x0||x>=specs[i].x1||y<specs[i].y0||y>=specs[i].y1)&&v[3]))goto done;
 }
 ok=true;
done:
 if(TL_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return NULL;}return rgba;
}
#include "title_menu_font.inc"

void title_layers_begin(SDL_Surface *source,const SDL_Color *target,bool animate)
{
 title_layers_end();
 if(!asset_directory||source!=VGAScreen||source!=VGAScreenSeg||!tl_geometry(source)||!tl_geometry(VGAScreen2)||
    source->pixels==VGAScreen2->pixels||!target||!main_window_tex_format||sprite_table[PLANET_SHAPES].count<=151)return;
 if(tl_hash(source->pixels,TL_N)!=TITLE_PIC4_FNV||tl_palette_hash(target)!=TITLE_PAL_FNV)return;
 for(unsigned i=0;i<240;i++)if(rgb_palette[i]!=SDL_MapRGB(main_window_tex_format,0,0,0))return;
 memset(&state,0,sizeof(state));
 state.screen=source;state.backup=VGAScreen2;state.pixels=source->pixels;state.backup_pixels=VGAScreen2->pixels;
 state.format=source->format;state.backup_format=VGAScreen2->format;state.animate=animate;
 state.pending_save=state.pending_restore=-1;state.checkpoint_kind=-1;
 memcpy(state.pic4,source->pixels,TL_N);memcpy(state.expected,source->pixels,TL_N);
 for(unsigned i=0;i<256;i++){SDL_Color *p=&state.expected_palette[i];SDL_GetRGB(rgb_palette[i],main_window_tex_format,&p->r,&p->g,&p->b);p->a=255;}
 memcpy(state.target_palette,target,sizeof(state.target_palette));
 if(!tl_decode(1)||!tl_decode(2)||!tl_palette_matches())return;
 bool allocation_failed=false;
 for(unsigned i=0;i<3;i++){state.rgba[i]=tl_load(i,&allocation_failed);if(allocation_failed){title_layers_end();return;}}
 if(!state.rgba[0]&&!state.rgba[1]&&!state.rgba[2])return;
 state.output=malloc(TL_OUT_BYTES);if(!state.output){title_layers_end();return;}
 state.active=true;state.phase=PH_VERSION;state.stage=ST_VERSION;
 tm_load(asset_directory);
}
void title_layers_version_done(void)
{
 if(!tl_check())return;
 if(state.phase!=PH_VERSION||state.stage!=ST_VERSION){title_layers_end();return;}
 state.stage=ST_NONE;state.phase=PH_VERSION_DONE;
}
void title_layers_save_before(enum TitleCheckpoint kind)
{
 if(!tl_check())return;
 if(kind!=TITLE_BACKGROUND&&kind!=TITLE_MENU){title_layers_end();return;}
 if(state.stage!=ST_NONE||state.pending_save!=-1||state.pending_restore!=-1||
    !((kind==TITLE_BACKGROUND&&state.phase==PH_VERSION_DONE&&state.animate&&!state.initial_done)||
      (kind==TITLE_MENU&&state.phase==PH_MENU_DONE))){title_layers_end();return;}
 state.pending_save=kind;
}
void title_layers_save_after(enum TitleCheckpoint kind)
{
 if(!state.active)return;
 if((kind!=TITLE_BACKGROUND&&kind!=TITLE_MENU)||state.pending_save<0){title_layers_end();return;}
 /* The original copy just changed backup pixels, so check against the known
  * source expectation before committing the new checkpoint. */
 if(!tl_layout()||!tl_sprites()||!tl_palette_matches()||state.pending_save!=(int)kind||
    memcmp(state.pixels,state.expected,TL_N)||memcmp(state.backup_pixels,state.expected,TL_N)) {title_layers_end();return;}
 memcpy(state.checkpoint,state.expected,TL_N);state.checkpoint_valid=true;state.checkpoint_kind=kind;state.pending_save=-1;
 if(kind==TITLE_MENU){state.menu_base=state.menu;tm_save();state.phase=PH_UI_START;}
}
void title_layers_restore_before(enum TitleCheckpoint kind)
{
 if(!tl_check())return;
 if(kind!=TITLE_BACKGROUND&&kind!=TITLE_MENU){title_layers_end();return;}
 if(state.stage!=ST_NONE||state.pending_save!=-1||state.pending_restore!=-1||!state.checkpoint_valid||state.checkpoint_kind!=(int)kind||
    !((kind==TITLE_BACKGROUND&&state.phase==PH_MOTION&&state.motions_done<29)||
      (kind==TITLE_MENU&&state.phase==PH_LIVE&&!state.cursor_live))){title_layers_end();return;}
 state.pending_restore=kind;
}
void title_layers_restore_after(enum TitleCheckpoint kind)
{
 if(!state.active)return;
 if((kind!=TITLE_BACKGROUND&&kind!=TITLE_MENU)||state.pending_restore<0){title_layers_end();return;}
 if(!tl_layout()||!tl_sprites()||!tl_palette_matches()||state.pending_restore!=(int)kind||
    memcmp(state.backup_pixels,state.checkpoint,TL_N)||memcmp(state.pixels,state.checkpoint,TL_N)){title_layers_end();return;}
 memcpy(state.expected,state.checkpoint,TL_N);state.pending_restore=-1;
 if(kind==TITLE_BACKGROUND)state.pose_ready=true;
 else {state.menu=state.menu_base;tm_restore();state.stage=ST_HIGHLIGHT;state.highlight_ready=false;memset(state.cursor.coverage,0,TL_N);}
}
static bool tl_logo_done(unsigned i)
{ return state.logo_count==state.opaque_count[i-1]; }
void title_layers_logo(unsigned id,int x,int y)
{
 if(!tl_check())return;
 unsigned i=id==146?1:id==151?2:0;
 if(!i){title_layers_end();return;}
 int expected_y=state.initial_done?(i==1?60-2*state.motions_done:45+state.motions_done):
                                    (state.animate?(i==1?62:41):(i==1?4:73));
 bool ordered=i==1?(state.stage==ST_NONE&&((state.phase==PH_VERSION_DONE&&(!state.animate||state.checkpoint_kind==TITLE_BACKGROUND))||
                                        (state.phase==PH_MOTION&&state.pose_ready))):
                    (state.stage==ST_LOGO146&&tl_logo_done(1));
 if(!ordered||x!=(i==1?11:155)||y!=expected_y){title_layers_end();return;}
 state.logo_x[i-1]=x;state.logo_y[i-1]=y;state.logo_count=0;state.last_logo_offset=-1;state.stage=i==1?ST_LOGO146:ST_LOGO151;
}
void title_layers_art_ready(void)
{
 if(!tl_check())return;
 if(state.stage!=ST_LOGO151||!tl_logo_done(2)){title_layers_end();return;}
 state.stage=ST_NONE;state.pose_ready=false;
 if(!state.initial_done){state.initial_done=true;state.phase=PH_ART_START;}
 else {++state.motions_done;state.phase=state.motions_done==29?PH_MENU_READY:PH_MOTION;}
}
void title_layers_menu_begin(void)
{
 if(!tl_check())return;
 if(state.phase!=PH_MENU_READY||state.stage!=ST_NONE){title_layers_end();return;}
 state.stage=ST_MENU;state.phase=PH_MENU_BUILD;tm_base_begin();
}
void title_layers_menu_done(void)
{
 if(!tl_check())return;
 if(state.phase!=PH_MENU_BUILD||state.stage!=ST_MENU){title_layers_end();return;}
 tm_base_done();state.stage=ST_NONE;state.phase=PH_MENU_DONE;
}
void title_layers_highlight_done(void)
{
 if(!tl_check())return;
 if(state.phase!=PH_LIVE||state.stage!=ST_HIGHLIGHT){title_layers_end();return;}
 tm_highlight_done();state.stage=ST_NONE;state.highlight_ready=true;
}
void title_layers_cursor_begin(void)
{
 if(!tl_check())return;
 if(state.phase!=PH_LIVE||state.stage!=ST_NONE||!state.highlight_ready||state.cursor_live){title_layers_end();return;}
 memcpy(state.pre_cursor,state.expected,TL_N);memset(state.cursor.coverage,0,TL_N);
 state.stage=ST_CURSOR;state.cursor_live=true;state.cursor_presented=false;
}
void title_layers_cursor_done(void)
{
 if(!tl_check())return;
 if(state.phase!=PH_LIVE||state.stage!=ST_CURSOR||!state.cursor_live){title_layers_end();return;}
 state.stage=ST_NONE;
}
void title_layers_cursor_erased(void)
{
 if(!state.active)return;
 if(!tl_layout()||!tl_sprites()||!tl_palette_matches()||state.phase!=PH_LIVE||state.stage!=ST_NONE||
    !state.cursor_live||!state.cursor_presented||memcmp(state.pixels,state.pre_cursor,TL_N)||
    !state.checkpoint_valid||memcmp(state.backup_pixels,state.checkpoint,TL_N)){title_layers_end();return;}
 memcpy(state.expected,state.pre_cursor,TL_N);memset(state.cursor.coverage,0,TL_N);state.cursor_live=false;
}
void title_layers_pixel(SDL_Surface *surface,Uint8 *address,enum TitleWriter writer)
{
 if(!state.active)return;
 if(surface!=state.screen||!tl_layout()){title_layers_end();return;}
 uintptr_t base=(uintptr_t)state.pixels,position=(uintptr_t)address;
 if(position<base||position-base>=TL_N){title_layers_end();return;}
 int offset=(int)(position-base);
 struct Plane *plane=NULL;
 if(state.stage==ST_VERSION&&(writer==TITLE_WRITE_FONT||writer==TITLE_WRITE_SHADOW))plane=&state.version;
 else if((state.stage==ST_MENU||state.stage==ST_HIGHLIGHT)&&writer==TITLE_WRITE_FONT)plane=&state.menu;
 else if(state.stage==ST_CURSOR&&writer==TITLE_WRITE_CURSOR)plane=&state.cursor;
 else if((state.stage==ST_LOGO146||state.stage==ST_LOGO151)&&writer==TITLE_WRITE_LOGO) {
  unsigned i=state.stage==ST_LOGO146?1:2;
  int x=(int)(offset%TL_W)-state.logo_x[i-1],y=(int)(offset/TL_W)-state.logo_y[i-1];
  if(x<0||y<0||x>=(int)specs[i].w||y>=(int)specs[i].h||offset<=state.last_logo_offset||
     !tl_mask(i)[y*specs[i].w+x]||*address!=tl_indices(i)[y*specs[i].w+x]){title_layers_end();return;}
  state.last_logo_offset=(int)offset;++state.logo_count;
 } else {title_layers_end();return;}
 state.expected[offset]=*address;
 if(plane){plane->coverage[offset]=1;plane->index[offset]=*address;}
 if(plane==&state.menu)tm_pixel((unsigned)offset,*address);
}
void title_layers_fade_start(const SDL_Color *target,const SDL_Color *solid,unsigned first,unsigned last)
{
 if(!tl_check())return;
 if(state.stage!=ST_NONE||state.pending_save!=-1||state.pending_restore!=-1||state.cursor_live){title_layers_end();return;}
 if(target&&!solid&&tl_palette_hash(target)==TITLE_PAL_FNV&&first==0&&last==239&&state.phase==PH_ART_START) {
  state.phase=PH_ART_FADE;state.remaining=10;memcpy(state.fade_target,target,sizeof(state.fade_target));
 } else if(target&&!solid&&tl_palette_hash(target)==TITLE_PAL_FNV&&first==240&&last==255&&state.phase==PH_UI_START) {
  state.phase=PH_UI_FADE;state.remaining=20;memcpy(state.fade_target,target,sizeof(state.fade_target));
 } else if(!target&&solid&&!solid->r&&!solid->g&&!solid->b&&first==0&&last==255&&state.phase==PH_LIVE) {
  state.phase=PH_OUT;state.remaining=-1;memset(state.fade_target,0,sizeof(state.fade_target));
 } else {title_layers_end();return;}
 state.fade_first=first;state.fade_last=last;
}
void title_layers_fade_step(int remaining,unsigned first,unsigned last)
{
 if(!state.active)return;
 if(state.phase==PH_OUT&&state.remaining==-1&&(remaining==10||remaining==15))state.remaining=remaining;
 if(!tl_source_matches()||state.stage!=ST_NONE||first!=state.fade_first||last!=state.fade_last||remaining<=0||remaining!=state.remaining||
    (state.phase!=PH_ART_FADE&&state.phase!=PH_UI_FADE&&state.phase!=PH_OUT)){title_layers_end();return;}
 for(unsigned i=first;i<=last;i++) {
  state.expected_palette[i].r+=(int)(state.fade_target[i].r-state.expected_palette[i].r)/remaining;
  state.expected_palette[i].g+=(int)(state.fade_target[i].g-state.expected_palette[i].g)/remaining;
  state.expected_palette[i].b+=(int)(state.fade_target[i].b-state.expected_palette[i].b)/remaining;
 }
 if(!tl_palette_matches()){title_layers_end();return;}
 if(state.phase!=PH_UI_FADE)for(unsigned v=0;v<256;v++) {
  int target=state.phase==PH_ART_FADE?(int)v:0;
  state.channel[v]+=(target-state.channel[v])/remaining;
 }
 if(--state.remaining==0) {
  if(state.phase==PH_ART_FADE)state.phase=state.animate?PH_MOTION:PH_MENU_READY;
  else if(state.phase==PH_UI_FADE)state.phase=PH_LIVE;
  else title_layers_end(); /* final original black presentation remains exact */
 }
}
static Uint32 tl_classic(Uint8 index)
{ SDL_Color p=state.expected_palette[index];return UINT32_C(0xff000000)|((Uint32)p.r<<16)|((Uint32)p.g<<8)|p.b; }
static Uint32 tl_art(const Uint8 *rgba)
{ return UINT32_C(0xff000000)|((Uint32)state.channel[rgba[0]]<<16)|((Uint32)state.channel[rgba[1]]<<8)|state.channel[rgba[2]]; }
static void tl_plane(const struct Plane *plane)
{
 for(unsigned p=0;p<TL_N;p++)if(plane->coverage[p]) {
  Uint32 color=tl_classic(plane->index[p]);unsigned x=(p%TL_W)*TL_D,y=(p/TL_W)*TL_D;
  for(unsigned dy=0;dy<TL_D;dy++)for(unsigned dx=0;dx<TL_D;dx++)state.output[(y+dy)*(TL_W*TL_D)+x+dx]=color;
 }
}
static void tl_logo(unsigned i)
{
 unsigned w=specs[i].w*TL_D,h=specs[i].h*TL_D;
 unsigned ox=(unsigned)state.logo_x[i-1]*TL_D,oy=(unsigned)state.logo_y[i-1]*TL_D;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++) {
  unsigned index=(y/TL_D)*specs[i].w+x/TL_D;
  Uint32 *out=&state.output[(oy+y)*(TL_W*TL_D)+ox+x];
  if(!state.rgba[i]) {if(tl_mask(i)[index])*out=tl_classic(tl_indices(i)[index]);continue;}
  const Uint8 *rgba=state.rgba[i]+4*(y*w+x);unsigned a=rgba[3];if(!a)continue;
  Uint32 src=tl_art(rgba),dst=*out,value=UINT32_C(0xff000000);
  for(unsigned shift=0;shift<=16;shift+=8)value|=((((src>>shift)&255)*a+((dst>>shift)&255)*(255-a)+127)/255)<<shift;
  *out=value;
 }
}
bool title_layers_present(SDL_Renderer *renderer,SDL_Surface *source,const SDL_Rect *destination)
{
 if(!tl_check())return false;
 bool phase_ok=state.phase==PH_ART_FADE||state.phase==PH_MOTION||state.phase==PH_MENU_READY||state.phase==PH_UI_FADE||
               (state.phase==PH_LIVE&&(state.cursor_live||state.remaining==0))||state.phase==PH_OUT;
 if(!renderer||!destination||source!=state.screen||state.stage!=ST_NONE||!phase_ok||state.pending_save!=-1||state.pending_restore!=-1||state.pose_ready){title_layers_end();return false;}
 for(unsigned p=0;p<TL_OUT_N;p++)state.output[p]=state.rgba[0]?tl_art(state.rgba[0]+4*p):tl_classic(state.pic4[(p/(TL_W*TL_D)/TL_D)*TL_W+(p%(TL_W*TL_D))/TL_D]);
 tl_plane(&state.version);tl_logo(1);tl_logo(2);
 float sx,sy;SDL_RenderGetScale(renderer,&sx,&sy);
 bool native_font=sx==1.0f&&sy==1.0f&&tm_render(destination);
 bool portable_font=!native_font&&tm_render_portable();
 if(!native_font&&!portable_font)tl_plane(&state.menu);
 if(!hd_cursor_active())tl_plane(&state.cursor);
 if(!state.texture) {
  state.texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,TL_W*TL_D,TL_H*TL_D);
  if(!state.texture||SDL_SetTextureScaleMode(state.texture,SDL_ScaleModeNearest)||SDL_SetTextureBlendMode(state.texture,SDL_BLENDMODE_NONE))goto failed;
 }
 if(SDL_UpdateTexture(state.texture,NULL,state.output,TL_W*TL_D*4)||SDL_SetRenderDrawColor(renderer,0,0,0,255)||
    SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,state.texture,NULL,destination))goto failed;
 if(portable_font) {
  SDL_Rect support={0,TM_SAMPLE_Y,TM_SAMPLE_W,TM_SAMPLE_H};
  if(!selector_font_output_overlay(renderer,destination,menu_font.samples,&support)) {
   /* Real renderer/resource failure falls back only the optional menu. */
   tl_plane(&state.menu);if(!hd_cursor_active())tl_plane(&state.cursor);
   if(SDL_UpdateTexture(state.texture,NULL,state.output,TL_W*TL_D*4)||SDL_RenderClear(renderer)||
      SDL_RenderCopy(renderer,state.texture,NULL,destination))goto failed;
  } else if(state.cursor_live) {
   /* Reuse the title texture for a transparent cursor-only nearest copy.
    * SDL applies precisely the original title sampling phase at every size. */
   memset(state.output,0,TL_OUT_BYTES);if(!hd_cursor_active())tl_plane(&state.cursor);
   if(SDL_UpdateTexture(state.texture,NULL,state.output,TL_W*TL_D*4)||
      SDL_SetTextureBlendMode(state.texture,SDL_BLENDMODE_BLEND)||
      SDL_RenderCopy(renderer,state.texture,NULL,destination)||
      SDL_SetTextureBlendMode(state.texture,SDL_BLENDMODE_NONE))goto failed;
  }
 }
 if(!hd_cursor_present(renderer,destination))goto failed;
 SDL_RenderPresent(renderer);if(state.cursor_live)state.cursor_presented=true;return true;
failed:
 title_layers_end();return false;
}
