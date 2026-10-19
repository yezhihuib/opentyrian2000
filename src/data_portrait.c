/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional source-authenticated Data portrait presentation only. Native INDEX8, palettes, RNG and input stay
 * untouched. Reconstruct the true pre-face underlay before applying new alpha.
 */
#ifndef _WIN32
#define _POSIX_C_SOURCE 200809L
#endif
#include "data_portrait.h"
#include "hd_cursor.h"
#include "data_frame.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#if defined(_WIN32)
#include <io.h>
#include <fcntl.h>
#define DP_OPEN(p) _open(p,_O_RDONLY|_O_BINARY|_O_NOINHERIT)
#define DP_READ _read
#define DP_CLOSE _close
#define DP_FSTAT _fstat
#define DP_STAT struct _stat
#define DP_REGULAR(m) (((m)&_S_IFMT)==_S_IFREG)
#else
#include <fcntl.h>
#include <unistd.h>
#define DP_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define DP_READ read
#define DP_CLOSE close
#define DP_FSTAT fstat
#define DP_STAT struct stat
#define DP_REGULAR(m) S_ISREG(m)
#endif
enum {DP_COUNT=18,DP_MAX_W=70,DP_MAX_H=77,DP_N=5390,DP_CANVAS=4096000};
/* Every size, geometry and identity comes from this compiled allowlist, never
 * from a resource header. At most 18 bounded art allocations may be cached. */
struct DPPin {
 unsigned w,h,x,y,palette,rle_bytes,bytes;
 uint64_t rle_fnv,index_fnv,mask_fnv,palette_fnv,payload_fnv,file_fnv;
};
#include "data_portrait_pins.inc"
static struct {bool attempted,valid;Uint8 *art;} resources[DP_COUNT];
static struct {
 bool active,ready,capturing,cursor;
 unsigned transition;
 SDL_Surface *screen;void *pixels;SDL_PixelFormat *format;int pitch;
 Uint8 underlay[DP_N],expected[64000],blocked[DP_N],cursor_mask[DP_N],cursor_expected[64000],frame_owned[DP_N];
 const struct DPPin *pin;const Uint8 *art;Uint32 *output;SDL_Texture *texture;SDL_Renderer *renderer;
} dp;
static char directory[1024]="assets/data-portrait-v1";
static uint32_t dp_u32(const Uint8 *p){return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static uint64_t dp_u64(const Uint8 *p){return dp_u32(p)|((uint64_t)dp_u32(p+4)<<32);}
static uint64_t dp_more(uint64_t h,const Uint8 *p,size_t n){while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint64_t dp_hash(const void *p,size_t n){return dp_more(UINT64_C(14695981039346656037),p,n);}
static bool surface_ok(SDL_Surface *s){return s&&s->pixels&&s->format&&s->format->BitsPerPixel==8&&s->w==320&&s->h==200&&s->pitch>=320;}
static bool layout_ok(SDL_Surface *s){return dp.active&&surface_ok(s)&&s==dp.screen&&s->pixels==dp.pixels&&s->format==dp.format&&s->pitch==dp.pitch;}
static void copy_expected(SDL_Surface *s){for(unsigned y=0;y<200;++y)memcpy(dp.expected+y*320,(Uint8 *)s->pixels+y*s->pitch,320);}
static bool valid_header(const Uint8 *p,unsigned face,const struct DPPin *pin)
{
 const unsigned fields[15]={1,320,200,4,pin->w,pin->h,pin->w*4,pin->h*4,pin->x,pin->y,face,face+1,pin->palette,pin->bytes,0};
 if(memcmp(p,"DPR1",4))return false;
 for(unsigned i=0;i<15;++i)if(dp_u32(p+4+i*4)!=fields[i])return false;
 const uint64_t hashes[5]={pin->rle_fnv,pin->index_fnv,pin->mask_fnv,pin->palette_fnv,pin->payload_fnv};
 for(unsigned i=0;i<5;++i)if(dp_u64(p+64+i*8)!=hashes[i])return false;
 for(unsigned i=104;i<128;++i)if(p[i])return false;
 return true;
}
static void load_resource(unsigned face)
{
 if(face>=DP_COUNT||resources[face].attempted)return;
 resources[face].attempted=true;if(!directory[0])return;
 const struct DPPin *pin=&dp_pins[face];
 char path[4096];Uint8 header[128],extra,*data=NULL;DP_STAT st;bool good=false;
 int n=snprintf(path,sizeof(path),"%s/face%02u-v1.hda",directory,face);if(n<0||(size_t)n>=sizeof(path))return;
 int fd=DP_OPEN(path);if(fd<0)return;
 if(DP_FSTAT(fd,&st)||!DP_REGULAR(st.st_mode)||st.st_size!=128+pin->bytes||DP_READ(fd,header,128)!=128||!valid_header(header,face,pin))goto done;
 data=malloc(pin->bytes);
 if(!data||DP_READ(fd,data,pin->bytes)!=(int)pin->bytes||DP_READ(fd,&extra,1)!=0||dp_hash(data,pin->bytes)!=pin->payload_fnv||dp_more(dp_hash(header,128),data,pin->bytes)!=pin->file_fnv)goto done;
 good=true;
 done:if(DP_CLOSE(fd))good=false;
 if(good){resources[face].art=data;resources[face].valid=true;}else free(data);
}
static void release_texture(void){if(dp.texture)SDL_DestroyTexture(dp.texture);dp.texture=NULL;dp.renderer=NULL;}
void data_portrait_end(void){dp.active=dp.ready=dp.capturing=dp.cursor=false;dp.screen=NULL;dp.pin=NULL;dp.art=NULL;memset(dp.cursor_mask,0,sizeof(dp.cursor_mask));memset(dp.cursor_expected,0,sizeof(dp.cursor_expected));}
void data_portrait_invalidate(void){release_texture();data_portrait_end();}
void data_portrait_set_directory(const char *root)
{
 data_portrait_invalidate();for(unsigned face=0;face<DP_COUNT;++face)free(resources[face].art);memset(resources,0,sizeof(resources));free(dp.output);dp.output=NULL;directory[0]=0;
 if(root&&strlen(root)<sizeof(directory))strcpy(directory,root);
}
void data_portrait_begin(unsigned menu,SDL_Surface *s,bool rebuilt)
{
 if(menu!=7&&menu!=8){data_portrait_end();return;}
 if(!rebuilt&&layout_ok(s)&&dp.ready)return;
 data_portrait_end();if(!surface_ok(s))return;
 dp.active=true;dp.screen=s;dp.pixels=s->pixels;dp.format=s->format;dp.pitch=s->pitch;
}
/* Bounded independent RLE/index/mask authentication, including transparent
 * cells and native same-index opaque writes. No source data is retained. */
static bool source_ok(const struct DPPin *pin,const Uint8 *rle,size_t bytes)
{
 if(!pin||!rle||bytes!=pin->rle_bytes||dp_hash(rle,bytes)!=pin->rle_fnv)return false;
 Uint8 indices[DP_N]={0},mask[DP_N]={0};unsigned x=0,y=0;
 for(size_t k=0;k<bytes;){unsigned v=rle[k++];if(y>=pin->h)return false;
  if(v==255){if(k>=bytes)return false;x+=rle[k++];}
  else if(v==254)x=pin->w;
  else if(v==253)++x;
  else{if(x>=pin->w)return false;indices[y*pin->w+x]=(Uint8)v;mask[y*pin->w+x]=255;++x;}
  if(x>pin->w)return false;if(x==pin->w){x=0;++y;}
 }
 return y==pin->h&&x==0&&dp_hash(indices,pin->w*pin->h)==pin->index_fnv&&dp_hash(mask,pin->w*pin->h)==pin->mask_fnv;
}
void data_portrait_capture(SDL_Surface *s,unsigned face,unsigned palette,int x,int y,const void *rle,size_t bytes,unsigned w,unsigned h)
{
 if(!layout_ok(s))return;dp.ready=false;
 if(face>=DP_COUNT){data_portrait_end();return;}
 const struct DPPin *pin=&dp_pins[face];
 if(palette!=pin->palette||x!=(int)pin->x||y!=(int)pin->y||w!=pin->w||h!=pin->h||!source_ok(pin,rle,bytes)){data_portrait_end();return;}
 load_resource(face);if(!resources[face].valid){data_portrait_end();return;}
 dp.pin=pin;dp.art=resources[face].art;
 memset(dp.blocked,0,sizeof(dp.blocked));memset(dp.cursor_mask,0,sizeof(dp.cursor_mask));
 for(unsigned py=0;py<pin->h;++py)for(unsigned px=0;px<pin->w;++px){unsigned n=py*pin->w+px;
  dp.underlay[n]=((Uint8 *)s->pixels)[(py+pin->y)*s->pitch+px+pin->x];
  dp.frame_owned[n]=data_frame_underlay_owned(s,px+pin->x,py+pin->y);
 }
 dp.capturing=true;
}
void data_portrait_face_done(SDL_Surface *s){if(layout_ok(s)&&dp.capturing){copy_expected(s);dp.capturing=false;dp.ready=true;}}
bool data_portrait_active(SDL_Surface *s){return layout_ok(s)&&dp.ready;}
void data_portrait_pixel(SDL_Surface *s,const Uint8 *address)
{
 if(!layout_ok(s)||!dp.ready||dp.capturing)return;
 uintptr_t base=(uintptr_t)s->pixels,p=(uintptr_t)address;
 if(p<base||p-base>=(size_t)s->pitch*200){data_portrait_end();return;}
 const struct DPPin *pin=dp.pin;
 size_t off=p-base;unsigned x=(unsigned)(off%(unsigned)s->pitch),y=(unsigned)(off/(unsigned)s->pitch);if(x>=320)return;
 dp.expected[y*320+x]=*address;
 if(dp.cursor)dp.cursor_expected[y*320+x]=1;
 if(x>=pin->x&&x<pin->x+pin->w&&y>=pin->y&&y<pin->y+pin->h){unsigned n=(y-pin->y)*pin->w+x-pin->x;if(dp.cursor)dp.cursor_mask[n]=1;else dp.blocked[n]=1;}
}
void data_portrait_rect(SDL_Surface *s,const SDL_Rect *rect)
{
 if(!layout_ok(s)||!dp.ready)return;SDL_Rect bounds={0,0,320,200},clipped,actual;
 if(!SDL_IntersectRect(&bounds,&s->clip_rect,&clipped))return;if(rect){if(!SDL_IntersectRect(&clipped,rect,&actual))return;}else actual=clipped;
 for(int y=actual.y;y<actual.y+actual.h;++y)for(int x=actual.x;x<actual.x+actual.w;++x)data_portrait_pixel(s,(Uint8 *)s->pixels+y*s->pitch+x);
}
void data_portrait_cursor_begin(SDL_Surface *s){if(layout_ok(s)){memset(dp.cursor_mask,0,sizeof(dp.cursor_mask));memset(dp.cursor_expected,0,sizeof(dp.cursor_expected));dp.cursor=true;}}
void data_portrait_cursor_done(void){dp.cursor=false;}
void data_portrait_cursor_restored(SDL_Surface *s)
{
 if(!layout_ok(s))return;
 /* Restore only observed opaque cursor cells; never bless unrelated writes. */
 if(dp.ready)for(unsigned y=0;y<200;++y)for(unsigned x=0;x<320;++x)if(dp.cursor_expected[y*320+x])
  dp.expected[y*320+x]=((Uint8 *)s->pixels)[y*s->pitch+x];
 memset(dp.cursor_expected,0,sizeof(dp.cursor_expected));
 memset(dp.cursor_mask,0,sizeof(dp.cursor_mask));
}
void data_portrait_transition(bool begin){if(begin)++dp.transition;else if(dp.transition)--dp.transition;}
static bool palette_ok(const struct DPPin *pin,const Uint32 *rgb,const SDL_PixelFormat *format)
{
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned i=0;i<256;++i){Uint8 c[3];SDL_GetRGB(rgb[i],format,c,c+1,c+2);h=dp_more(h,c,3);}
 return pin&&h==pin->palette_fnv;
}
bool data_portrait_present(SDL_Renderer *r,SDL_Surface *s,const SDL_Rect *dst,const Uint32 *rgb,const SDL_PixelFormat *format)
{
 if(!r||!dst||dst->w<=0||dst->h<=0||!data_portrait_active(s)||dp.transition||!rgb||!format||!palette_ok(dp.pin,rgb,format))return false;
 for(unsigned y=0;y<200;++y)if(memcmp(dp.expected+y*320,(Uint8 *)s->pixels+y*s->pitch,320)){data_portrait_end();return false;}
 if(!dp.output){dp.output=malloc(DP_CANVAS);if(!dp.output)return false;}
 if(dp.renderer!=r)release_texture();
 if(!dp.texture){dp.texture=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,1280,800);if(!dp.texture)return false;dp.renderer=r;
  if(SDL_SetTextureBlendMode(dp.texture,SDL_BLENDMODE_BLEND)){release_texture();return false;}
#if SDL_VERSION_ATLEAST(2,0,12)
  if(SDL_SetTextureScaleMode(dp.texture,SDL_ScaleModeNearest)){release_texture();return false;}
#endif
 }
 const struct DPPin *pin=dp.pin;
 memset(dp.output,0,DP_CANVAS);
 bool frame_ready=data_frame_underlay_ready(s,rgb,format);
 for(unsigned y=0;y<(pin->h*4);++y)for(unsigned x=0;x<(pin->w*4);++x){unsigned cell=(y/4)*pin->w+x/4;if(dp.blocked[cell]||(!hd_cursor_active()&&dp.cursor_mask[cell]))continue;
  Uint8 ur,ug,ub;Uint32 color=rgb[dp.underlay[cell]];unsigned cx=pin->x*4+x,cy=pin->y*4+y;
  if(frame_ready&&dp.frame_owned[cell])data_frame_underlay_sample(s,cx,cy,rgb,format,&color);
  SDL_GetRGB(color,format,&ur,&ug,&ub);const Uint8 *p=dp.art+(y*(pin->w*4)+x)*4;unsigned a=p[3];
  unsigned rr=(p[0]*a+ur*(255-a)+127)/255,gg=(p[1]*a+ug*(255-a)+127)/255,bb=(p[2]*a+ub*(255-a)+127)/255;
  dp.output[cy*1280+cx]=UINT32_C(0xff000000)|rr<<16|gg<<8|bb;
 }
 if(SDL_UpdateTexture(dp.texture,NULL,dp.output,1280*4))return false;
 SDL_Rect clip;bool clipped=SDL_RenderIsClipEnabled(r)==SDL_TRUE;SDL_RenderGetClipRect(r,&clip);SDL_RenderSetClipRect(r,dst);
 bool good=SDL_RenderCopy(r,dp.texture,NULL,dst)==0;SDL_RenderSetClipRect(r,clipped?&clip:NULL);return good;
}
