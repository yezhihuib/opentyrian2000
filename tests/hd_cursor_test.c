/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "hd_cursor.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef HD_CURSOR_FAULT_TEST
static int fault;
SDL_Texture *__real_SDL_CreateTexture(SDL_Renderer *,Uint32,int,int,int);
int __real_SDL_SetTextureBlendMode(SDL_Texture *,SDL_BlendMode);
int __real_SDL_SetTextureScaleMode(SDL_Texture *,SDL_ScaleMode);
int __real_SDL_UpdateTexture(SDL_Texture *,const SDL_Rect *,const void *,int);
int __real_SDL_RenderCopyF(SDL_Renderer *,SDL_Texture *,const SDL_Rect *,const SDL_FRect *);
SDL_Texture *__wrap_SDL_CreateTexture(SDL_Renderer *r,Uint32 f,int a,int w,int h)
{return fault==1?NULL:__real_SDL_CreateTexture(r,f,a,w,h);}
int __wrap_SDL_SetTextureBlendMode(SDL_Texture *t,SDL_BlendMode m)
{return fault==2?-1:__real_SDL_SetTextureBlendMode(t,m);}
int __wrap_SDL_SetTextureScaleMode(SDL_Texture *t,SDL_ScaleMode m)
{return fault==3?-1:__real_SDL_SetTextureScaleMode(t,m);}
int __wrap_SDL_UpdateTexture(SDL_Texture *t,const SDL_Rect *r,const void *p,int n)
{return fault==4?-1:__real_SDL_UpdateTexture(t,r,p,n);}
int __wrap_SDL_RenderCopyF(SDL_Renderer *r,SDL_Texture *t,const SDL_Rect *s,const SDL_FRect *d)
{return fault==5?-1:__real_SDL_RenderCopyF(r,t,s,d);}
#endif
static unsigned char sheet[29941],saved[64000];
static void draw(SDL_Surface *s,int x,int y,unsigned sprite,int filter)
{
 for(unsigned q=0;q<4;q++){
  unsigned id=sprite+(q&1)+(q/2)*19,at=sheet[(id-1)*2]|((unsigned)sheet[(id-1)*2+1]<<8);
  int xx=x+(q&1)*12,yy=y+(q/2)*14;
  while(sheet[at]!=15){unsigned code=sheet[at++],n=code>>4;xx+=code&15;
   if(!n){yy++;xx-=12;}else{
    for(unsigned i=0;i<n;i++,xx++)if(xx>=0&&xx<s->w&&yy>=0&&yy<s->h)
     ((Uint8 *)s->pixels)[yy*s->pitch+xx]=filter<0?sheet[at+i]:(Uint8)(filter|(sheet[at+i]&15));
    at+=n;
   }
  }
 }
}
static void background(SDL_Surface *s)
{for(int y=0;y<200;y++)for(int x=0;x<320;x++)((Uint8 *)s->pixels)[y*s->pitch+x]=(Uint8)(x+y);}
static void unchanged(SDL_Surface *s)
{for(int y=0;y<200;y++)assert(!memcmp(saved+y*320,(Uint8 *)s->pixels+y*s->pitch,320));}
int main(int argc,char **argv)
{
 assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f&&fread(sheet,1,sizeof(sheet),f)==sizeof(sheet)&&fgetc(f)==EOF);fclose(f);
 assert(SDL_Init(SDL_INIT_VIDEO)==0);
 SDL_Surface *s=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 SDL_Surface *canvas=SDL_CreateRGBSurfaceWithFormat(0,1400,900,32,SDL_PIXELFORMAT_ARGB8888);
 SDL_Renderer *r=SDL_CreateSoftwareRenderer(canvas);assert(s&&canvas&&r);
 Uint32 rgb[256];SDL_PixelFormat *format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);
 for(unsigned i=0;i<256;i++)rgb[i]=SDL_MapRGB(format,(Uint8)i,(Uint8)(i*.82),(Uint8)(i*.38));
 const SDL_Rect sizes[]={{0,0,640,400},{0,0,1280,800},{64,0,1152,720},{0,0,1001,633},{0,0,320,200}};
 const int positions[][2]={{135,80},{0,0},{319,199},{-5,-5},{310,192}};
 static const unsigned sprites[]={273,275,277,279,281};
 for(unsigned shape=0;shape<5;shape++)for(unsigned a=0;a<5;a++)for(unsigned b=0;b<5;b++)for(int filter=-1;filter<=240;filter+=241){
  unsigned sprite=sprites[shape];
  background(s);Uint8 before[64000];memcpy(before,s->pixels,64000);
  hd_cursor_begin(s,positions[b][0],positions[b][1],sprite,sheet,sizeof(sheet),true,filter);
  assert(!hd_cursor_active());draw(s,positions[b][0],positions[b][1],sprite,filter);hd_cursor_done();memcpy(saved,s->pixels,64000);
  hd_cursor_prepare(r,s,&sizes[a],rgb,format);assert(hd_cursor_active());
  SDL_Surface *clean=hd_cursor_underlay(s);assert(clean!=s&&!memcmp(clean->pixels,before,64000));unchanged(s);
  SDL_SetRenderDrawColor(r,12,24,36,255);SDL_RenderClear(r);
  SDL_Rect clip={sizes[a].x+1,sizes[a].y+1,sizes[a].w-2,sizes[a].h-2};SDL_RenderSetClipRect(r,&clip);
  hd_cursor_present(r,&sizes[a]);SDL_Rect restored;SDL_RenderGetClipRect(r,&restored);assert(!memcmp(&clip,&restored,sizeof(clip)));
  SDL_RenderSetClipRect(r,NULL);unchanged(s);
  hd_cursor_clear();assert(!hd_cursor_active()&&hd_cursor_underlay(s)==s);
 }
 /* Every direction must authenticate its own native draw, and switching to a
  * hidden/unsupported pointer must retire the previous display lease. */
 for(unsigned shape=0;shape<5;shape++){
  unsigned sprite=sprites[shape];background(s);
  hd_cursor_begin(s,100,70,sprite,sheet,sizeof(sheet),true,-1);
  draw(s,100,70,sprites[(shape+1)%5],-1);hd_cursor_done();
  hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
  background(s);hd_cursor_begin(s,100,70,sprite,sheet,sizeof(sheet),true,-1);
  draw(s,100,70,sprite,-1);hd_cursor_done();hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(hd_cursor_active());
  hd_cursor_begin(s,100,70,sprite,sheet,sizeof(sheet),false,-1);hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
  SDL_SetRenderDrawColor(r,12,24,36,255);SDL_RenderClear(r);assert(hd_cursor_present(r,&sizes[1]));
  Uint32 pixel;memcpy(&pixel,(Uint8 *)canvas->pixels+280*canvas->pitch+400*4,4);assert((pixel&0xffffff)==0x0c1824);
  background(s);hd_cursor_begin(s,100,70,999,sheet,sizeof(sheet),true,-1);draw(s,100,70,sprite,-1);hd_cursor_done();
  hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
 }
 background(s);hd_cursor_begin(s,135,80,273,sheet,sizeof(sheet),false,-1);hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
 hd_cursor_begin(s,135,80,273,sheet,sizeof(sheet)-1,true,-1);hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
 hd_cursor_begin(s,135,80,273,sheet,sizeof(sheet),true,-1);draw(s,135,80,273,-1);hd_cursor_done();((Uint8 *)s->pixels)[10]^=1;hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
 sheet[100]^=1;hd_cursor_begin(s,135,80,273,sheet,sizeof(sheet),true,-1);hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());sheet[100]^=1;
 hd_cursor_begin(s,135,80,273,sheet,sizeof(sheet),true,0xe0);hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
 /* Same-index cursor writes still restore the real pre-cursor underlay. */
 background(s);draw(s,135,80,273,-1);memcpy(saved,s->pixels,64000);hd_cursor_begin(s,135,80,273,sheet,sizeof(sheet),true,-1);draw(s,135,80,273,-1);hd_cursor_done();hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(hd_cursor_active());assert(!memcmp(hd_cursor_underlay(s)->pixels,saved,64000));
 /* Preserve a caller's exact physical scissor at non-unit renderer scale. */
 SDL_Rect physical={1,1,101,101},after;SDL_RenderSetClipRect(r,&physical);SDL_RenderSetScale(r,1.25f,1.25f);
 hd_cursor_prepare(r,s,&sizes[1],rgb,format);assert(!hd_cursor_active());
 SDL_RenderSetScale(r,1,1);SDL_RenderGetClipRect(r,&after);assert(!memcmp(&physical,&after,sizeof(after)));SDL_RenderSetClipRect(r,NULL);
 /* Real renderer resize/recreation and a black palette must remain bounded. */
 memset(rgb,0,sizeof(rgb));
 for(unsigned shape=0;shape<5;shape++){
  unsigned sprite=sprites[shape];hd_cursor_release();assert(!hd_cursor_active());background(s);
  hd_cursor_begin(s,135,80,sprite,sheet,sizeof(sheet),true,-1);draw(s,135,80,sprite,-1);hd_cursor_done();
  hd_cursor_prepare(r,s,&sizes[0],rgb,format);assert(hd_cursor_active());
  SDL_SetRenderDrawColor(r,0,0,0,255);SDL_RenderClear(r);assert(hd_cursor_present(r,&sizes[0]));
  for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++){Uint32 pixel;memcpy(&pixel,(Uint8 *)canvas->pixels+y*canvas->pitch+x*4,4);assert((pixel&0xffffff)==0);}
 }
 /* A distinct live renderer replaces and releases the old texture owner. */
 SDL_Surface *canvas2=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);assert(canvas2);
 SDL_Renderer *r2=SDL_CreateSoftwareRenderer(canvas2);assert(r2);
 hd_cursor_prepare(r2,s,&sizes[1],rgb,format);assert(hd_cursor_active());assert(hd_cursor_present(r2,&sizes[1]));
 hd_cursor_release();SDL_DestroyRenderer(r2);SDL_FreeSurface(canvas2);
#ifdef HD_CURSOR_FAULT_TEST
 for(unsigned shape=0;shape<5;shape++)for(fault=1;fault<=5;fault++){
  unsigned sprite=sprites[shape];
  hd_cursor_release();background(s);hd_cursor_begin(s,135,80,sprite,sheet,sizeof(sheet),true,-1);draw(s,135,80,sprite,-1);hd_cursor_done();memcpy(saved,s->pixels,64000);
  hd_cursor_prepare(r,s,&sizes[1],rgb,format);unchanged(s);
  if(fault<5)assert(!hd_cursor_active());else{assert(hd_cursor_active());assert(!hd_cursor_present(r,&sizes[1]));assert(!hd_cursor_active());}
 }
 fault=0;
#endif
 hd_cursor_release();SDL_FreeFormat(format);SDL_DestroyRenderer(r);SDL_FreeSurface(canvas);SDL_FreeSurface(s);SDL_Quit();
 puts("PASS: 250 shape/scale/clip/filter combinations; five-shape switching/hidden/mismatched draws; exact INDEX8 underlays; hidden/malformed/late-write fallbacks; fractional scissor fallback; renderer replacement; black fade; optional injected SDL failures.");return 0;
}
