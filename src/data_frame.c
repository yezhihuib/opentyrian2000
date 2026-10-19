/* SPDX-License-Identifier: GPL-2.0-or-later
 * Independently authenticated Data7/8 static presentation. All indexed writes,
 * portrait palettes, menu/input state, and RNG remain owned by the native game.
 */
#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include "data_frame.h"
#include "hd_cursor.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#if defined(_WIN32)
#include <io.h>
#include <fcntl.h>
#define DF_OPEN(p) _open(p,_O_RDONLY|_O_BINARY|_O_NOINHERIT)
#define DF_READ _read
#define DF_CLOSE _close
#define DF_FSTAT _fstat
#define DF_STAT struct _stat
#define DF_REGULAR(m) (((m)&_S_IFMT)==_S_IFREG)
#else
#include <fcntl.h>
#include <unistd.h>
#define DF_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define DF_READ read
#define DF_CLOSE close
#define DF_FSTAT fstat
#define DF_STAT struct stat
#define DF_REGULAR(m) S_ISREG(m)
#endif
#include "data_frame_pins.inc"
enum { DF_W=320,DF_H=200,DF_N=64000,DF_OW=1280,DF_OH=800,DF_BYTES=4096000 };
static struct {
 bool attempted,valid,active,ready,surround,cursor;
 unsigned transition;
 SDL_Surface *screen;void *pixels;SDL_PixelFormat *format;int pitch;
 Uint8 underlay[DF_N],expected[DF_N],blocked[DF_N],cursor_mask[DF_N];
 Uint8 *art;Uint32 *output;SDL_Texture *texture;SDL_Renderer *renderer;
} df;
static char directory[1024]="assets/data-frame-v1";
static uint32_t df_u32(const Uint8 *p)
{return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint64_t df_u64(const Uint8 *p){return df_u32(p)|((uint64_t)df_u32(p+4)<<32);}
static uint64_t df_more(uint64_t h,const Uint8 *p,size_t n)
{while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint64_t df_hash(const void *p,size_t n)
{return df_more(UINT64_C(14695981039346656037),p,n);}
static bool surface_ok(SDL_Surface *s)
{return s&&s->pixels&&s->format&&s->format->BitsPerPixel==8&&s->w==DF_W&&s->h==DF_H&&s->pitch>=DF_W;}
static bool layout_ok(SDL_Surface *s)
{return df.active&&surface_ok(s)&&s==df.screen&&s->pixels==df.pixels&&s->format==df.format&&s->pitch==df.pitch;}
static bool option_support(unsigned x,unsigned y)
{
 if(x<1||y<1||x>=170||y>=187)return false;
 unsigned p=(y-1)*169+x-1;
 return (data_frame_option_support[p>>3]>>(p&7))&1;
}
static void copy_indices(Uint8 *p,SDL_Surface *s)
{for(unsigned y=0;y<DF_H;++y)memcpy(p+y*DF_W,(Uint8 *)s->pixels+y*s->pitch,DF_W);}
static bool valid_header(const Uint8 *header)
{
 static const unsigned fields[15]={1,320,200,4,1280,800,DF_BYTES,169,186,1,1,2,0,0,0};
 if(memcmp(header,"DFM1",4))return false;
 for(unsigned i=0;i<15;++i)if(df_u32(header+4+i*4)!=fields[i])return false;
 if(df_u64(header+64)!=UINT64_C(0x45a77a2246c174b9)||df_u64(header+72)!=UINT64_C(0x3c232016c519ed17)||
    df_u64(header+80)!=UINT64_C(0x03a1b83be967efe2)||df_u64(header+88)!=UINT64_C(0x2f1faa16b55f7cfc)||
    df_u64(header+96)!=DATA_FRAME_PALETTE_FNV||df_u64(header+104)!=DATA_FRAME_PAYLOAD_FNV)return false;
 for(unsigned i=112;i<128;++i)if(header[i])return false;
 return true;
}
static void load_resource(void)
{
 if(df.attempted)return;df.attempted=true;
 if(!directory[0])return;
 char path[4096];Uint8 header[128],extra;DF_STAT st;Uint8 *data=NULL;bool good=false;
 int count=snprintf(path,sizeof(path),"%s/data-frame-v1.hda",directory);
 if(count<0||(size_t)count>=sizeof(path))return;
 int fd=DF_OPEN(path);if(fd<0)return;
 if(DF_FSTAT(fd,&st)||!DF_REGULAR(st.st_mode)||st.st_size!=128+DF_BYTES||DF_READ(fd,header,128)!=128||!valid_header(header))goto done;
 data=malloc(DF_BYTES);if(!data||DF_READ(fd,data,DF_BYTES)!=DF_BYTES||DF_READ(fd,&extra,1)!=0||df_hash(data,DF_BYTES)!=DATA_FRAME_PAYLOAD_FNV)goto done;
 if(df_more(df_hash(header,128),data,DF_BYTES)!=DATA_FRAME_FILE_FNV)goto done;
 good=true;
 done:if(DF_CLOSE(fd))good=false;
 if(good){df.art=data;df.valid=true;}else free(data);
}
static void release_texture(void)
{if(df.texture)SDL_DestroyTexture(df.texture);df.texture=NULL;df.renderer=NULL;}
void data_frame_invalidate(void)
{release_texture();data_frame_end();}
void data_frame_end(void)
{df.active=df.ready=df.surround=df.cursor=false;df.screen=NULL;memset(df.cursor_mask,0,sizeof(df.cursor_mask));}
void data_frame_set_directory(const char *root)
{
 data_frame_end();data_frame_invalidate();free(df.art);free(df.output);df.art=NULL;df.output=NULL;df.attempted=df.valid=false;
 directory[0]=0;
 if(root&&strlen(root)<sizeof(directory))strcpy(directory,root);
}
bool data_frame_active(SDL_Surface *screen){return layout_ok(screen)&&df.ready;}
void data_frame_transition(bool begin)
{if(begin)++df.transition;else if(df.transition)--df.transition;}
void data_frame_begin(unsigned menu,SDL_Surface *screen,SDL_Surface *background,bool rebuilt)
{
 if(menu!=7&&menu!=8){data_frame_end();return;}
 if(!rebuilt&&layout_ok(screen)&&df.ready)return;
 data_frame_end();load_resource();
 if(!df.valid||!surface_ok(screen)||!surface_ok(background)||screen==background)return;
 uint64_t hash=UINT64_C(14695981039346656037);
 for(unsigned y=0;y<DF_H;++y)hash=df_more(hash,(Uint8 *)background->pixels+y*background->pitch,DF_W);
 if(hash!=UINT64_C(0x45a77a2246c174b9))return;
 df.screen=screen;df.pixels=screen->pixels;df.format=screen->format;df.pitch=screen->pitch;df.active=true;
 copy_indices(df.underlay,background);copy_indices(df.expected,screen);
 for(unsigned y=1;y<171;++y)memset(df.underlay+y*DF_W+1,0,145);
 memset(df.blocked,0,sizeof(df.blocked));memset(df.cursor_mask,0,sizeof(df.cursor_mask));
}
void data_frame_surround_begin(SDL_Surface *screen,const void *rle,size_t bytes,unsigned w,unsigned h)
{
 if(!layout_ok(screen))return;
 if(!rle||bytes!=24704||w!=169||h!=186||df_hash(rle,bytes)!=UINT64_C(0x3c232016c519ed17)){data_frame_end();return;}
 df.surround=true;df.ready=false;
 for(unsigned y=0;y<DF_H;++y)for(unsigned x=0;x<DF_W;++x)
  if((x>=1&&x<146&&y>=1&&y<171)||option_support(x,y))df.blocked[y*DF_W+x]=0;
}
void data_frame_surround_end(SDL_Surface *screen)
{if(layout_ok(screen)&&df.surround){copy_indices(df.expected,screen);df.surround=false;df.ready=true;}}
void data_frame_pixel(SDL_Surface *screen,const Uint8 *address)
{
 if(!layout_ok(screen)||df.surround)return;
 uintptr_t base=(uintptr_t)screen->pixels,p=(uintptr_t)address;
 if(p<base||p-base>=(size_t)screen->pitch*DF_H){data_frame_end();return;}
 size_t offset=p-base;unsigned x=(unsigned)(offset%(unsigned)screen->pitch),y=(unsigned)(offset/(unsigned)screen->pitch);
 if(x>=DF_W)return;
 unsigned n=y*DF_W+x;df.expected[n]=*address;
 /* A same-index opaque write still owns its complete logical footprint. */
 if(df.cursor)df.cursor_mask[n]=1;else df.blocked[n]=1;
}
/* SDL_FillRect does not issue per-pixel engine callbacks. Its actual clipped
 * write region still owns every cell, including writes equal to the underlay. */
void data_frame_rect(SDL_Surface *screen,const SDL_Rect *rect)
{
 if(!layout_ok(screen)||df.surround)return;
 SDL_Rect bounds={0,0,DF_W,DF_H},clipped,actual;
 if(!SDL_IntersectRect(&bounds,&screen->clip_rect,&clipped))return;
 if(rect){if(!SDL_IntersectRect(&clipped,rect,&actual))return;}else actual=clipped;
 for(int y=actual.y;y<actual.y+actual.h;++y)for(int x=actual.x;x<actual.x+actual.w;++x)
  data_frame_pixel(screen,(Uint8 *)screen->pixels+y*screen->pitch+x);
}
void data_frame_cursor_begin(SDL_Surface *screen)
{if(layout_ok(screen)){memset(df.cursor_mask,0,sizeof(df.cursor_mask));df.cursor=true;}}
void data_frame_cursor_done(void){df.cursor=false;}
void data_frame_cursor_restored(SDL_Surface *screen)
{
 if(!layout_ok(screen))return;
 for(unsigned y=0;y<DF_H;++y)for(unsigned x=0;x<DF_W;++x)if(df.cursor_mask[y*DF_W+x])
  df.expected[y*DF_W+x]=((Uint8 *)screen->pixels)[y*screen->pitch+x];
 memset(df.cursor_mask,0,sizeof(df.cursor_mask));
}
static bool palette_ok(const Uint32 *rgb,const SDL_PixelFormat *format)
{
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned i=208;i<256;++i){Uint8 c[3];SDL_GetRGB(rgb[i],format,c,c+1,c+2);h=df_more(h,c,3);}
 return h==DATA_FRAME_PALETTE_FNV;
}
bool data_frame_present(SDL_Renderer *renderer,SDL_Surface *screen,const SDL_Rect *dst,const Uint32 *rgb,const SDL_PixelFormat *format)
{
 if(!renderer||!dst||dst->w<=0||dst->h<=0||!data_frame_active(screen)||df.transition||!rgb||!format||!palette_ok(rgb,format))return false;
 for(unsigned y=0;y<DF_H;++y)if(memcmp(df.expected+y*DF_W,(Uint8 *)screen->pixels+y*screen->pitch,DF_W)){data_frame_end();return false;}
 if(!df.output){df.output=malloc(DF_BYTES);if(!df.output)return false;}
 if(df.renderer!=renderer)release_texture();
 if(!df.texture){
  df.texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,DF_OW,DF_OH);
  if(!df.texture)return false;df.renderer=renderer;
  if(SDL_SetTextureBlendMode(df.texture,SDL_BLENDMODE_BLEND)){release_texture();return false;}
#if SDL_VERSION_ATLEAST(2,0,12)
  /* Exact logical dynamic masks must not interpolate static metal over faces. */
  if(SDL_SetTextureScaleMode(df.texture,SDL_ScaleModeNearest)){release_texture();return false;}
#endif
 }
 for(unsigned y=0;y<DF_OH;++y)for(unsigned x=0;x<DF_OW;++x){
  unsigned n=y*DF_OW+x,cell=(y/4)*DF_W+x/4;const Uint8 *p=df.art+n*4;
  if(df.blocked[cell]||(!hd_cursor_active()&&df.cursor_mask[cell])){df.output[n]=0;continue;}
  unsigned a=p[3],r=p[0],g=p[1],b=p[2];
  if(option_support(x/4,y/4)){
   Uint8 ur,ug,ub;SDL_GetRGB(rgb[df.underlay[cell]],format,&ur,&ug,&ub);
   r=(r*a+ur*(255-a)+127)/255;g=(g*a+ug*(255-a)+127)/255;b=(b*a+ub*(255-a)+127)/255;a=255;
  }
  df.output[n]=a<<24|r<<16|g<<8|b;
 }
 if(SDL_UpdateTexture(df.texture,NULL,df.output,DF_OW*4))return false;
 SDL_Rect old_clip;bool clipped=SDL_RenderIsClipEnabled(renderer)==SDL_TRUE;SDL_RenderGetClipRect(renderer,&old_clip);
 SDL_RenderSetClipRect(renderer,dst);bool good=SDL_RenderCopy(renderer,df.texture,NULL,dst)==0;
 SDL_RenderSetClipRect(renderer,clipped?&old_clip:NULL);return good;
}

/* Read-only static presentation sampling for a separately authenticated portrait.
 * The caller snapshots ownership before the native face writes, and excludes
 * every later opaque write itself. No indexed pixels or frame leases change. */
bool data_frame_underlay_owned(SDL_Surface *screen,unsigned x,unsigned y)
{return x<DF_W&&y<DF_H&&data_frame_active(screen)&&!df.blocked[y*DF_W+x];}
bool data_frame_underlay_ready(SDL_Surface *screen,const Uint32 *rgb,const SDL_PixelFormat *format)
{return rgb&&format&&data_frame_active(screen)&&!df.transition&&palette_ok(rgb,format);}
/* The caller validates the palette once with underlay_ready in this synchronous
 * present call. Sampling never pumps events or changes the palette/lease. */
bool data_frame_underlay_sample(SDL_Surface *screen,unsigned x,unsigned y,const Uint32 *rgb,const SDL_PixelFormat *format,Uint32 *color)
{
 if(x>=DF_OW||y>=DF_OH||!color||!rgb||!format||!data_frame_active(screen)||df.transition)return false;
 unsigned cell=(y/4)*DF_W+x/4;const Uint8 *p=df.art+(y*DF_OW+x)*4;
 Uint8 ur,ug,ub;
 if(option_support(x/4,y/4))SDL_GetRGB(rgb[df.underlay[cell]],format,&ur,&ug,&ub);
 else SDL_GetRGB(*color,format,&ur,&ug,&ub);
 unsigned a=p[3];
 *color=SDL_MapRGB(format,(Uint8)((p[0]*a+ur*(255-a)+127)/255),(Uint8)((p[1]*a+ug*(255-a)+127)/255),(Uint8)((p[2]*a+ub*(255-a)+127)/255));
 return true;
}
