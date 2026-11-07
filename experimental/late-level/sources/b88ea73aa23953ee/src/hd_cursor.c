/* SPDX-License-Identifier: GPL-2.0-or-later
 * Smooth gold geometry derived from the five original native pointer shapes.
 * This is a final display layer. Native drawing, restoration, hit testing,
 * palette changes and INDEX8 ownership remain completely unmodified.
 */
#include "hd_cursor.h"
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
enum { W=320,H=200,N=W*H,MAX_EDGE=1024 };
static struct {
 SDL_Surface *screen,clean;void *pixels;SDL_PixelFormat *format;int pitch,x,y,filter;unsigned shape;
 bool candidate,ready;Uint8 before[N],expected[N];
 SDL_Renderer *renderer;SDL_Texture *texture;int tw,th;Uint32 *rgba;
 SDL_FRect destination;
} hc;
static bool layout(SDL_Surface *s)
{return s&&s->pixels&&s->format&&s->format->BitsPerPixel==8&&s->w==W&&s->h==H&&s->pitch>=W;}
static bool matches(SDL_Surface *s,const Uint8 *p)
{
 if(!layout(s)||s!=hc.screen||s->pixels!=hc.pixels||s->format!=hc.format||s->pitch!=hc.pitch)return false;
 for(unsigned y=0;y<H;y++)if(memcmp((Uint8 *)s->pixels+y*s->pitch,p+y*W,W))return false;
 return true;
}
void hd_cursor_clear(void){hc.candidate=hc.ready=false;hc.screen=NULL;}
void hd_cursor_release(void)
{
 hd_cursor_clear();if(hc.texture)SDL_DestroyTexture(hc.texture);
 hc.texture=NULL;hc.renderer=NULL;free(hc.rgba);hc.rgba=NULL;hc.tw=hc.th=0;
}
static uint64_t hash(const Uint8 *p,size_t n)
{uint64_t h=UINT64_C(14695981039346656037);while(n--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
/* Decode the authenticated four quadrants independently, including same-index
 * opaque writes. Never infer cursor coverage by comparing before/after colors. */
static bool quadrant(const Uint8 *data,size_t bytes,unsigned id,int ox,int oy)
{
 size_t at=(id-1)*2;if(at+2>bytes)return false;
 at=data[at]|((size_t)data[at+1]<<8);int x=ox,y=oy;
 while(at<bytes&&data[at]!=15){
  unsigned code=data[at++],count=code>>4;x+=code&15;
  if(!count){++y;x-=12;continue;}
  if(count>bytes-at)return false;
  for(unsigned i=0;i<count;i++,x++)if(x>=0&&x<W&&y>=0&&y<H)
   hc.expected[y*W+x]=hc.filter<0?data[at+i]:(Uint8)(hc.filter|(data[at+i]&15));
  at+=count;
 }
 return at<bytes;
}
/* Sprite-space offsets are separate from the logical hotspot. In particular,
 * the right arrow occupies columns 8..23 of its original 24x28 sprite block. */
static const struct {unsigned sprite;int ox,w,h;} shapes[]={
 {273,0,11,16},{275,0,21,16},{277,0,21,16},{279,0,16,21},{281,8,16,21}
};
void hd_cursor_begin(SDL_Surface *s,int x,int y,unsigned sprite,const void *sheet,size_t bytes,bool visible,int filter)
{
 hd_cursor_clear();
 unsigned shape=0;while(shape<5&&shapes[shape].sprite!=sprite)++shape;
 if(shape==5||!visible||!layout(s)||!sheet||bytes!=29941||hash(sheet,bytes)!=UINT64_C(0x8c478c429071f043)||
    x < -24||x>=W||y < -28||y>=H||(filter!=-1&&filter!=0xf0))return;
 hc.screen=s;hc.pixels=s->pixels;hc.format=s->format;hc.pitch=s->pitch;hc.x=x;hc.y=y;hc.filter=filter;hc.shape=shape;
 for(unsigned row=0;row<H;row++)memcpy(hc.before+row*W,(Uint8 *)s->pixels+row*s->pitch,W);
 memcpy(hc.expected,hc.before,N);
 hc.candidate=quadrant(sheet,bytes,sprite,x,y)&&quadrant(sheet,bytes,sprite+1,x+12,y)&&
              quadrant(sheet,bytes,sprite+19,x,y+14)&&quadrant(sheet,bytes,sprite+20,x+12,y+14);
}
void hd_cursor_done(void){if(hc.candidate&&!matches(hc.screen,hc.expected))hd_cursor_clear();}
bool hd_cursor_active(void){return hc.ready;}
SDL_Surface *hd_cursor_underlay(SDL_Surface *s)
{
 if(!hc.ready||s!=hc.screen)return s;
 hc.clean=*s;hc.clean.pixels=hc.before;hc.clean.pitch=W;return &hc.clean;
}
struct Point {double x,y;};
/* A single original-shaped NW arrow, with the original upper-left hotspot.
 * Straight vector edges replace the old logical-pixel staircase. */
static const struct Point arrow[]={
 {.18,.12},{.18,14.45},{3.30,11.52},{5.46,15.22},{7.92,13.82},{5.79,10.15},{10.55,9.96}
};
/* The broad directional arrow keeps the native triangular head, inset stem
 * and 21x16 bounds. Other directions rotate this geometry, not the NW arrow. */
static const struct Point paging[]={
 {10.5,.12},{20.85,10.5},{20.85,13.8},{15.0,13.8},{15.0,15.8},
 {6.0,15.8},{5.3,13.8},{.15,13.8},{.15,10.5}
};
static bool inside(double x,double y,const struct Point *polygon,unsigned count)
{
 bool in=false;for(unsigned i=0,j=count-1;i<count;j=i++){
  const struct Point a=polygon[i],b=polygon[j];
  if((a.y>y)!=(b.y>y)&&x<(b.x-a.x)*(y-a.y)/(b.y-a.y)+a.x)in=!in;
 }return in;
}
static double edge_distance(double x,double y,unsigned *edge,const struct Point *polygon,unsigned count)
{
 double best=1e6;for(unsigned i=0;i<count;i++){
  const struct Point a=polygon[i],b=polygon[(i+1)%count];double dx=b.x-a.x,dy=b.y-a.y;
  double t=((x-a.x)*dx+(y-a.y)*dy)/(dx*dx+dy*dy);t=fmax(0,fmin(1,t));
  double distance=hypot(x-a.x-t*dx,y-a.y-t*dy);
  if(distance<best){best=distance;*edge=i;}
 }return best;
}
static double clamp(double x){return fmax(0,fmin(1,x));}
static void sample(double x,double y,const Uint8 *color,double result[4])
{
 result[0]=result[1]=result[2]=result[3]=0;
 /* A tight soft lower-right shadow fits the original 11x16 footprint. */
 if(inside(x-.32,y-.42,arrow,7)){result[3]=.48;for(unsigned c=0;c<3;c++)result[c]=color[c]*.48;}
 if(!inside(x,y,arrow,7))return;
 unsigned edge=0;double d=edge_distance(x,y,&edge,arrow,7),gold;
 if(d<.22)gold=.08+.35*d/.22;
 else if(d<.87){
  double bright=(edge==0||edge==1||edge==6)?1.0:.39;
  gold=.40+(bright-.40)*sin((d-.22)/.65*1.5707963267948966);
 }else{
  /* Broad two-dimensional metal facets, with a restrained diagonal highlight. */
  gold=.67+.13*(1-clamp(x/10))+.10*exp(-pow((x-.56*y-.7)/1.35,2))-.11*clamp((y-9)/6);
 }
 double slot=clamp(gold)*5;unsigned lo=(unsigned)slot,hi=lo<5?lo+1:5;double t=slot-lo;
 result[3]=1;for(unsigned c=0;c<3;c++)result[c]=color[lo*3+c]*(1-t)+color[hi*3+c]*t;
}
/* Map local ink coordinates back into the authored up-arrow plane. The
 * shadow is displaced in output space so its direction does not rotate. */
static void paging_coordinates(double *x,double *y)
{
 double u=*x,v=*y;
 if(hc.shape==2){*x=21-u;*y=16-v;}
 else if(hc.shape==3){*x=21-v;*y=u;}
 else if(hc.shape==4){*x=v;*y=16-u;}
}
static void paging_sample(double x,double y,const Uint8 *color,double result[4])
{
 result[0]=result[1]=result[2]=result[3]=0;
 double u=x-.24,v=y-.30;paging_coordinates(&u,&v);
 if(inside(u,v,paging,9)){result[3]=.48;for(unsigned c=0;c<3;c++)result[c]=color[c]*.48;}
 paging_coordinates(&x,&y);
 if(!inside(x,y,paging,9))return;
 unsigned edge=0;double d=edge_distance(x,y,&edge,paging,9),gold;
 if(d<.22)gold=.08+.35*d/.22;
 else if(d<.95){
  double bright=(edge==8||edge==0||edge==6)?1.0:.39;
  gold=.40+(bright-.40)*sin((d-.22)/.73*1.5707963267948966);
 }else{
  /* Broad triangular facets meet at the original central metal ridge. */
  gold=.62+.20*(1-clamp(x/21))+.16*exp(-pow((x-10.5)/1.10,2))-.09*clamp((y-10)/6);
  if(y>10.3&&x>6.2&&x<14.8)
   gold=.57+.23*exp(-pow((x-10.5)/2.8,2))-.09*clamp((y-11)/5);
 }
 double slot=clamp(gold)*5;unsigned lo=(unsigned)slot,hi=lo<5?lo+1:5;double t=slot-lo;
 result[3]=1;for(unsigned c=0;c<3;c++)result[c]=color[lo*3+c]*(1-t)+color[hi*3+c]*t;
}
void hd_cursor_prepare(SDL_Renderer *r,SDL_Surface *s,const SDL_Rect *dst,const Uint32 *palette,const SDL_PixelFormat *format)
{
 hc.ready=false;
 if(!hc.candidate||!r||!dst||dst->w<=0||dst->h<=0||!palette||!format||!matches(s,hc.expected))return;
 float sx,sy;SDL_RenderGetScale(r,&sx,&sy);
 if(!isfinite(sx)||!isfinite(sy)||sx<=0||sy<=0)return;
 /* SDL floors scaled clip getters. Decline this uncommon combination before
  * removing native ink, so a caller's fractional scissor is never rewritten.
  * Fractional window fitting uses scale one and remains fully supported. */
 if(SDL_RenderIsClipEnabled(r)&&(sx!=1.0f||sy!=1.0f))return;
 int width=shapes[hc.shape].w,height=shapes[hc.shape].h;
 double dw=(double)width*dst->w/W,dh=(double)height*dst->h/H;
 double pw=ceil(dw*sx),ph=ceil(dh*sy);
 if(pw<1||ph<1||pw>MAX_EDGE||ph>MAX_EDGE)return;
 int tw=(int)pw,th=(int)ph;
 if(hc.renderer!=r||hc.tw!=tw||hc.th!=th){
  if(hc.texture)SDL_DestroyTexture(hc.texture);
  hc.texture=NULL;hc.renderer=NULL;
  free(hc.rgba);hc.rgba=malloc((size_t)tw*th*sizeof(*hc.rgba));hc.tw=hc.th=0;
  if(!hc.rgba)return;
  hc.texture=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,tw,th);
  if(!hc.texture||SDL_SetTextureBlendMode(hc.texture,SDL_BLENDMODE_BLEND)||
     SDL_SetTextureScaleMode(hc.texture,SDL_ScaleModeLinear)){hd_cursor_release();return;}
  hc.renderer=r;hc.tw=tw;hc.th=th;
 }
 Uint8 colors[18];for(unsigned i=0;i<6;i++)SDL_GetRGB(palette[248+i],format,colors+i*3,colors+i*3+1,colors+i*3+2);
 /* Coverage is integrated from the vector at physical-output density. This is
  * authored geometry, never a resize or filter of native cursor pixels. */
 for(int y=0;y<th;y++)for(int x=0;x<tw;x++){
  double sum[4]={0,0,0,0};
  for(unsigned yy=0;yy<4;yy++)for(unsigned xx=0;xx<4;xx++){
   double v[4],u=(x+(xx+.5)/4)*width/tw,w=(y+(yy+.5)/4)*height/th;
   if(hc.shape)paging_sample(u,w,colors,v);else sample(u,w,colors,v);
   for(unsigned c=0;c<4;c++)sum[c]+=v[c];
  }
  unsigned a=(unsigned)floor(sum[3]*255/16+.5);Uint32 p=a<<24;
  if(sum[3]>0)for(unsigned c=0;c<3;c++)p|=(Uint32)floor(sum[c]/sum[3]+.5)<<(16-c*8);
  hc.rgba[y*tw+x]=p;
 }
 if(SDL_UpdateTexture(hc.texture,NULL,hc.rgba,tw*4))return;
 hc.destination=(SDL_FRect){dst->x+(float)(hc.x+shapes[hc.shape].ox)*dst->w/W,dst->y+(float)hc.y*dst->h/H,(float)dw,(float)dh};
 hc.ready=true;
}
bool hd_cursor_present(SDL_Renderer *r,const SDL_Rect *dst)
{
 if(!hc.ready)return true;
 if(r!=hc.renderer||!dst){hd_cursor_clear();return false;}
 SDL_Rect old,clip=*dst;bool clipped=SDL_RenderIsClipEnabled(r)==SDL_TRUE;SDL_RenderGetClipRect(r,&old);
 if(clipped&&!SDL_IntersectRect(&old,dst,&clip))return true;
 bool good=SDL_RenderSetClipRect(r,&clip)==0;
 if(good)good=SDL_RenderCopyF(r,hc.texture,NULL,&hc.destination)==0;
 if(SDL_RenderSetClipRect(r,clipped?&old:NULL))good=false;
 /* Let the caller redraw its complete native-backed scene on a late error. */
 if(!good)hd_cursor_clear();
 return good;
}
