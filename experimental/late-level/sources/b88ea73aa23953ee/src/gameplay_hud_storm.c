/* SPDX-License-Identifier: GPL-2.0-or-later
 * HSI1: authored STORM heading only. Original sprite data stays runtime-only. */
#include "gameplay_hud_storm.h"
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#if defined(TARGET_WIN32) || defined(_WIN32)
#include <io.h>
#define HSI_OPEN(p) _open(p, _O_RDONLY | _O_BINARY | _O_NOINHERIT)
#define HSI_READ _read
#define HSI_CLOSE _close
#define HSI_FSTAT _fstat
#define HSI_STAT struct _stat
#define HSI_REGULAR(m) (((m) & _S_IFMT) == _S_IFREG)
#else
#include <unistd.h>
#define HSI_OPEN(p) open(p, O_RDONLY | O_NONBLOCK)
#define HSI_READ read
#define HSI_CLOSE close
#define HSI_FSTAT fstat
#define HSI_STAT struct stat
#define HSI_REGULAR(m) S_ISREG(m)
#endif
#ifndef HUD_STORM_SOURCE_BYTES
#define HUD_STORM_SOURCE_BYTES 230u
#endif
#ifndef HUD_STORM_RAW_FNV
#define HUD_STORM_RAW_FNV UINT64_C(0xe31bdc2ac030d21e)
#endif
#ifndef HUD_STORM_INDICES_FNV
#define HUD_STORM_INDICES_FNV UINT64_C(0x72f4faf812d18989)
#endif
#ifndef HUD_STORM_COVERAGE_FNV
#define HUD_STORM_COVERAGE_FNV UINT64_C(0xd6c645d37088c678)
#endif
#ifndef HUD_STORM_PIC3_FNV
#define HUD_STORM_PIC3_FNV UINT64_C(0x14c1441f3d5dc0e2)
#endif
#ifndef HUD_STORM_PALETTE_FNV
#define HUD_STORM_PALETTE_FNV UINT64_C(0x5e80e83992be2927)
#endif
#ifndef HUD_STORM_ART_FNV
#define HUD_STORM_ART_FNV UINT64_C(0x9ec4cfb118ff6182)
#endif

enum { W=25, H=13, LABEL_H=5, CELLS=W*H, X=284, Y=82,
       HEADER=96, PAYLOAD=20000, FILE_BYTES=HEADER+PAYLOAD };
static struct {
 bool live, suspended, pending, cleared, recorded, loaded, fade_palette_live;
 uint64_t generation, pending_generation, recorded_generation;
 HudStormView view;
 const uint8_t *source;
 uint8_t indices[CELLS], coverage[CELLS], touched[CELLS], art[PAYLOAD];
 uint32_t fade_palette[256];
} state;

static uint64_t update(uint64_t h,const uint8_t *p,size_t n)
{for(size_t i=0;i<n;i++)h=(h^p[i])*UINT64_C(1099511628211);return h;}
static uint64_t stamp(const uint8_t *p,size_t n)
{return update(UINT64_C(14695981039346656037),p,n);}
static uint32_t u32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const uint8_t *p)
{return (uint64_t)u32(p)|((uint64_t)u32(p+4)<<32);}
static bool valid_view(const HudStormView *v)
{return v&&v->surface&&v->format&&v->pixels&&v->width==320&&v->height==200&&
 v->bits==8&&v->bytes==1&&v->pitch>=320&&
 (size_t)v->pitch<=(SIZE_MAX-320)/199;}
static bool same_view(const HudStormView *v)
{return valid_view(v)&&v->surface==state.view.surface&&v->format==state.view.format&&
 v->pixels==state.view.pixels&&v->pitch==state.view.pitch;}
static bool observed_view(const HudStormView *v)
{
 if(same_view(v))return true;
 if(v&&(v->surface==state.view.surface||v->pixels==state.view.pixels))hud_storm_reset();
 return false;
}
static bool source(const HudStormSource *s,uint8_t values[CELLS],uint8_t coverage[CELLS])
{
 if(!s||!s->data||s->count<38||s->count>152||s->width!=W||s->height!=H||
    s->size!=HUD_STORM_SOURCE_BYTES||stamp(s->data,s->size)!=HUD_STORM_RAW_FNV)return false;
 memset(values,0,CELLS);memset(coverage,0,CELLS);
 unsigned x=0,y=0;
 for(unsigned i=0;i<s->size;i++) {
  if(y>=H||x>=W)return false;
  uint8_t c=s->data[i];
  if(c==255) {if(++i>=s->size||s->data[i]>W-x)return false;x+=s->data[i];}
  else if(c==254)x=W;
  else if(c==253)x++;
  else {values[y*W+x]=c;coverage[y*W+x]=255;x++;}
  if(x==W){x=0;y++;}
 }
 return x==0&&y==H&&stamp(values,CELLS)==HUD_STORM_INDICES_FNV&&
  stamp(coverage,CELLS)==HUD_STORM_COVERAGE_FNV;
}
static bool same_source(const HudStormSource *s)
{
 uint8_t v[CELLS],c[CELLS];
 return s&&s->data==state.source&&source(s,v,c)&&
  !memcmp(v,state.indices,CELLS)&&!memcmp(c,state.coverage,CELLS);
}
static bool header_ok(const uint8_t *h)
{
 return !memcmp(h,"HSI1",4)&&u32(h+4)==1&&u32(h+8)==W&&u32(h+12)==LABEL_H&&
  u32(h+16)==2&&u32(h+20)==PAYLOAD&&u32(h+24)==W&&u32(h+28)==H&&
  u32(h+32)==HUD_STORM_SOURCE_BYTES&&!u32(h+36)&&u64(h+40)==HUD_STORM_RAW_FNV&&
  u64(h+48)==HUD_STORM_INDICES_FNV&&u64(h+56)==HUD_STORM_COVERAGE_FNV&&
  u64(h+64)==HUD_STORM_PIC3_FNV&&u64(h+72)==HUD_STORM_ART_FNV&&
  u64(h+80)==HUD_STORM_PALETTE_FNV&&!u64(h+88);
}
static bool art_ok(void)
{
 if(stamp(state.art,PAYLOAD)!=HUD_STORM_ART_FNV)return false;
 for(unsigned part=0;part<2;part++) {
  unsigned n=part?8000:2000,offset=part?4000:0;
  for(unsigned i=0;i<n;i++) {
   unsigned value=state.art[offset+i],a=state.art[offset+n+i];
   if(a?(value<192||value>207):value!=0)return false;
  }
 }
 return true;
}
static bool load(const char *directory)
{
 char path[1024];uint8_t h[HEADER],extra;HSI_STAT st;
 if(!directory||!*directory)return false;
 int n=snprintf(path,sizeof(path),"%s/gameplay-hud-storm-label-v1.hda",directory);
 if(n<0||(size_t)n>=sizeof(path))return false;
 int fd=HSI_OPEN(path);if(fd<0)return false;
 bool ok=!HSI_FSTAT(fd,&st)&&HSI_REGULAR(st.st_mode)&&st.st_size==FILE_BYTES&&
  HSI_READ(fd,h,HEADER)==HEADER&&header_ok(h)&&
  HSI_READ(fd,state.art,PAYLOAD)==PAYLOAD&&HSI_READ(fd,&extra,1)==0&&art_ok();
 if(HSI_CLOSE(fd))ok=false;
 if(!ok)memset(state.art,0,sizeof(state.art));
 return ok;
}
void hud_storm_reset(void)
{
 uint64_t generation=state.generation+1;if(!generation)generation=1;
 memset(&state,0,sizeof(state));state.generation=generation;
}
void hud_storm_shutdown(void){hud_storm_reset();}
bool hud_storm_start(const char *directory,const HudStormView *v,const HudStormSource *s)
{
 hud_storm_reset();
 /* Authenticate all original input before consulting any optional art cache. */
 if(!valid_view(v)||!source(s,state.indices,state.coverage))return false;
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned y=0;y<200;y++)h=update(h,v->pixels+(size_t)y*v->pitch,320);
 if(h!=HUD_STORM_PIC3_FNV)return false;
 state.view=*v;state.source=s->data;state.live=true;
 state.loaded=load(directory);return state.loaded;
}
void hud_storm_suspend(void)
{state.suspended=true;state.pending=false;state.cleared=false;state.recorded=false;state.fade_palette_live=false;}
void hud_storm_resume(const HudStormView *v,bool scope)
{
 if(!state.live)return;
 if(!scope||!same_view(v)){hud_storm_reset();return;}
 state.suspended=false;state.fade_palette_live=false;
 /* A begin without its matching end never becomes a retained draw. */
 state.pending=false;state.cleared=false;
}
void hud_storm_begin(const HudStormView *v,const HudStormSource *s,unsigned slot,
 unsigned option,unsigned icon,int x,int y,bool scope)
{
 if(state.pending){state.pending=false;state.recorded=false;return;}
 if(!scope){state.recorded=false;return;}
 if(slot!=1)return;
 state.fade_palette_live=false;
 state.recorded=false;state.cleared=false;
 if(!state.live||state.suspended||!same_view(v)||!same_source(s)||!scope||
  option!=9||icon!=38||x!=X||y!=Y)return;
 state.pending=true;state.pending_generation=state.generation;
 memset(state.touched,0,sizeof(state.touched));
}
static bool overlaps(int x,int y,int w,int h)
{return w>0&&h>0&&(int64_t)x+w>X&&x<X+W&&(int64_t)y+h>Y&&y<Y+H;}
void hud_storm_rect(const HudStormView *v,int x,int y,int w,int h)
{
 if(!state.live||!observed_view(v)||!overlaps(x,y,w,h))return;
 state.recorded=false;
 if(!state.pending)return;
 if(state.cleared||x!=X||y!=Y||w!=29||h!=16){state.pending=false;return;}
 for(int yy=0;yy<16;yy++)for(int xx=0;xx<29;xx++)
  if(v->pixels[(size_t)(Y+yy)*v->pitch+X+xx]){state.pending=false;return;}
 state.cleared=true;
}
void hud_storm_pixel(const HudStormView *v,const uint8_t *address)
{
 if(!state.live||!observed_view(v)||!address)return;
 uintptr_t base=(uintptr_t)v->pixels,p=(uintptr_t)address;
 if(p<base||p-base>=(size_t)v->pitch*199+320)return;
 int y=(int)((p-base)/(unsigned)v->pitch),x=(int)((p-base)%(unsigned)v->pitch);
 if(x<X||x>=X+W||y<Y||y>=Y+H)return;
 state.recorded=false;
 if(!state.pending)return;
 unsigned i=(unsigned)((y-Y)*W+x-X);
 if(!state.cleared||!state.coverage[i]||state.touched[i]||*address!=state.indices[i])
  {state.pending=false;return;}
 state.touched[i]=255;
}
static bool footprint(const HudStormView *v)
{
 for(unsigned y=0;y<H;y++)
  if(memcmp(v->pixels+(size_t)(Y+y)*v->pitch+X,state.indices+y*W,W))return false;
 return true;
}
void hud_storm_end(const HudStormView *v,const HudStormSource *s,unsigned slot,bool scope)
{
 if(!scope)state.recorded=false;
 if(slot!=1)return;
 bool ok=state.pending&&state.cleared&&state.pending_generation==state.generation&&
  !state.suspended&&same_view(v)&&same_source(s)&&scope&&footprint(v)&&
  !memcmp(state.touched,state.coverage,CELLS);
 state.pending=false;state.cleared=false;state.recorded=ok;
 state.recorded_generation=ok?state.generation:0;
}
static uint64_t palette_stamp(const uint32_t palette[256])
{
 uint64_t h=UINT64_C(14695981039346656037);
 for(unsigned i=0;i<256;i++) {
  uint8_t p[3]={(uint8_t)(palette[i]>>16),(uint8_t)(palette[i]>>8),(uint8_t)palette[i]};
  h=update(h,p,3);
 }
 return h;
}
void hud_storm_fade_palette(const uint32_t palette[256])
{
 if(state.live&&palette){memcpy(state.fade_palette,palette,sizeof(state.fade_palette));state.fade_palette_live=true;}
}
static uint32_t color(uint32_t value){return UINT32_C(0xff000000)|(value&UINT32_C(0xffffff));}
static uint32_t blend(uint32_t foreground,uint32_t background,unsigned alpha)
{
 uint32_t result=UINT32_C(0xff000000);
 for(unsigned shift=0;shift<24;shift+=8) {
  unsigned f=(foreground>>shift)&255,b=(background>>shift)&255;
  result|=((f*alpha+b*(255-alpha)+127)/255)<<shift;
 }
 return result;
}
bool hud_storm_present(const HudStormView *v,const HudStormSource *s,bool scope,
 const uint32_t palette[256],const uint8_t *rgb,int rgb_pitch,
 uint8_t *texture,int texture_pitch,int width,int height,int density)
{
 if(!state.live||state.suspended||!state.recorded||state.pending||
  state.recorded_generation!=state.generation||!same_view(v)||!scope||!same_source(s)||
  !footprint(v)) {state.recorded=false;return false;}
 /* Recheck source and current footprint BEFORE the optional cached payload. */
 if(!state.loaded||!art_ok()||!palette||!rgb||!texture||(density!=4&&density!=8)||
  width!=320*density||height!=200*density||rgb_pitch<width*4||texture_pitch<width*4||
  (size_t)rgb_pitch>(SIZE_MAX-(size_t)width*4)/(height-1)||
  (size_t)texture_pitch>(SIZE_MAX-(size_t)width*4)/(height-1))
  {state.recorded=false;return false;}
 if(palette_stamp(palette)!=HUD_STORM_PALETTE_FNV&&
  (!state.fade_palette_live||memcmp(state.fade_palette,palette,sizeof(state.fade_palette))))
  {state.recorded=false;return false;}
 /* No overlay may replace another HD contributor, even if its INDEX8 is equal.
  * The entire icon, not just the heading, must still be the original nearest RGB. */
 for(int y=0;y<H*density;y++)for(int x=0;x<W*density;x++) {
  uint32_t pixel;memcpy(&pixel,rgb+(size_t)(Y*density+y)*rgb_pitch+(X*density+x)*4,4);
  if(pixel!=color(palette[state.indices[(y/density)*W+x/density]]))
   {state.recorded=false;return false;}
 }
 unsigned n=(unsigned)(W*LABEL_H*density*density),offset=density==8?4000:0;
 for(int y=0;y<LABEL_H*density;y++)for(int x=0;x<W*density;x++) {
  unsigned i=(unsigned)(y*W*density+x);
  uint32_t pixel=blend(palette[state.art[offset+i]],palette[0],state.art[offset+n+i]);
  memcpy(texture+(size_t)(Y*density+y)*texture_pitch+(X*density+x)*4,&pixel,4);
 }
 return true;
}
