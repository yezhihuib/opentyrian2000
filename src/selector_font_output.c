/* SPDX-License-Identifier: GPL-2.0-or-later
 * Bounded output-space font sampling over the unchanged selected scaler.
 */
#include "selector_font_output.h"
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { TILE_W=128, TILE_H=64, CW=1280, CH=800, IW=320, IH=200 };
struct OutputGeometry {
 float sx,sy;
 SDL_Rect viewport,clip;
 double x,y,w,h;
 int width,height;
 bool software;
};
static struct {
 SDL_Renderer *renderer;
 SDL_Texture *underlay,*tile,**cursor_tiles;
 size_t cursor_capacity;
 Uint32 format;
 int width,height,tw,th;
 Uint32 pixels[TILE_W*TILE_H];
} output;

size_t selector_font_output_static_bytes(void){return sizeof(output);}
void selector_font_output_release(void)
{
 if(output.underlay)SDL_DestroyTexture(output.underlay);
 if(output.tile)SDL_DestroyTexture(output.tile);
 for(size_t i=0;i<output.cursor_capacity;i++)if(output.cursor_tiles[i])SDL_DestroyTexture(output.cursor_tiles[i]);
 free(output.cursor_tiles);
 memset(&output,0,sizeof(output));
}
static bool intersect(SDL_Rect *a,const SDL_Rect *b)
{
 int64_t x=MAX((int64_t)a->x,b->x),y=MAX((int64_t)a->y,b->y);
 int64_t r=MIN((int64_t)a->x+a->w,(int64_t)b->x+b->w);
 int64_t d=MIN((int64_t)a->y+a->h,(int64_t)b->y+b->h);
 if(r<=x||d<=y){a->x=a->y=a->w=a->h=0;return false;}
 a->x=(int)x;a->y=(int)y;a->w=(int)(r-x);a->h=(int)(d-y);return true;
}
static bool geometry(SDL_Renderer *renderer,const SDL_Rect *dst,
 const SDL_RendererInfo *info,struct OutputGeometry *g)
{
 if(SDL_GetRenderTarget(renderer)||SDL_GetRendererOutputSize(renderer,&g->width,&g->height)||g->width<=0||g->height<=0)return false;
 SDL_RenderGetScale(renderer,&g->sx,&g->sy);
 if(!isfinite(g->sx)||!isfinite(g->sy)||g->sx<=0||g->sy<=0)return false;
 /* SDL's getters divide by scale and floor. Query at scale one to obtain
  * precisely the integer viewport/scissor used by the rendering backend.
  * Do not rewrite these states: their internal fractional values are private.
  */
 if(SDL_RenderSetScale(renderer,1,1))return false;
 SDL_RenderGetViewport(renderer,&g->viewport);
 g->clip=g->viewport;
 if(SDL_RenderIsClipEnabled(renderer)){
  SDL_Rect c;SDL_RenderGetClipRect(renderer,&c);
  int64_t x=(int64_t)c.x+g->viewport.x,y=(int64_t)c.y+g->viewport.y;
  if(x<INT_MIN||x>INT_MAX||y<INT_MIN||y>INT_MAX){SDL_RenderSetScale(renderer,g->sx,g->sy);return false;}
  c.x=(int)x;c.y=(int)y;intersect(&g->clip,&c);
 }
 if(SDL_RenderSetScale(renderer,g->sx,g->sy))return false;
 SDL_Rect bounds={0,0,g->width,g->height};intersect(&g->clip,&bounds);
 /* SDL_RenderCopy converts the destination to float before applying scale. */
 float x=(float)dst->x*g->sx,y=(float)dst->y*g->sy;
 float w=(float)dst->w*g->sx,h=(float)dst->h*g->sy;
 if(!isfinite(x)||!isfinite(y)||!isfinite(w)||!isfinite(h)||w<=0||h<=0)return false;
 g->software=(info->flags&SDL_RENDERER_SOFTWARE)!=0;
 if(g->software){
  if((double)x<INT_MIN||(double)x>INT_MAX||(double)y<INT_MIN||(double)y>INT_MAX||(double)w>INT_MAX||(double)h>INT_MAX)return false;
  x=(float)(int)x;y=(float)(int)y;w=(float)(int)w;h=(float)(int)h;
  if(w<=0||h<=0)return false;
 }
 g->x=g->viewport.x+(double)x;g->y=g->viewport.y+(double)y;g->w=w;g->h=h;
 return true;
}
static SDL_Rect mapped_box(const struct OutputGeometry *g,double x,double y,double w,double h)
{
 /* Clip as doubles before converting, keeping negative origins signed. */
 double l=MAX(floor(g->x+x*g->w/CW),(double)g->clip.x);
 double t=MAX(floor(g->y+y*g->h/CH),(double)g->clip.y);
 double r=MIN(ceil(g->x+(x+w)*g->w/CW),(double)g->clip.x+g->clip.w);
 double b=MIN(ceil(g->y+(y+h)*g->h/CH),(double)g->clip.y+g->clip.h);
 SDL_Rect result={0,0,0,0};
 if(r>l&&b>t){result.x=(int)l;result.y=(int)t;result.w=(int)(r-l);result.h=(int)(b-t);}
 return result;
}
static bool resources(SDL_Renderer *r,SDL_Texture *reference,const SDL_RendererInfo *info)
{
 Uint32 format;int access,w,h;SDL_ScaleMode mode;SDL_BlendMode blend;
 Uint8 red,green,blue,alpha;
 if(SDL_QueryTexture(reference,&format,&access,&w,&h)||w<=0||h<=0||
    SDL_GetTextureScaleMode(reference,&mode)||SDL_GetTextureBlendMode(reference,&blend)||
    SDL_GetTextureColorMod(reference,&red,&green,&blue)||SDL_GetTextureAlphaMod(reference,&alpha))return false;
 /* Main RGB scaler textures have no modulation or blending. Unknown state
  * is a real unsupported state, not a resolution-dependent admission rule. */
 if(blend!=SDL_BLENDMODE_NONE||red!=255||green!=255||blue!=255||alpha!=255||
    (format!=SDL_PIXELFORMAT_RGB888&&format!=SDL_PIXELFORMAT_RGB565))return false;
 if(output.renderer!=r||output.format!=format||output.width!=w||output.height!=h)selector_font_output_release();
 if(!output.renderer){
  output.renderer=r;output.format=format;output.width=w;output.height=h;
  output.tw=info->max_texture_width>0?MIN(TILE_W,info->max_texture_width):TILE_W;
  output.th=info->max_texture_height>0?MIN(TILE_H,info->max_texture_height):TILE_H;
  if(output.tw<1||output.th<1)return false;
  output.underlay=SDL_CreateTexture(r,format,SDL_TEXTUREACCESS_STREAMING,w,h);
  output.tile=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,output.tw,output.th);
  if(!output.underlay||!output.tile||SDL_SetTextureBlendMode(output.underlay,SDL_BLENDMODE_NONE)||
     SDL_SetTextureBlendMode(output.tile,SDL_BLENDMODE_NONE)||SDL_SetTextureScaleMode(output.tile,SDL_ScaleModeNearest))return false;
 }
 if(SDL_SetTextureScaleMode(output.underlay,mode))return false;

 return true;
}
/* Reconstruct crisply on magnified axes; integrate the complete correlated
 * premultiplied layer over reduction axes. Out-of-domain coverage is zero. */
static Uint32 sample(const Uint32 *layer,const struct OutputGeometry *g,int px,int py,Uint32 base)
{
 double xa=(px-g->x)*CW/g->w,xb=(px+1.0-g->x)*CW/g->w;
 double ya=(py-g->y)*CH/g->h,yb=(py+1.0-g->y)*CH/g->h;
 if(g->w>CW){xa=floor((xa+xb)*0.5);xb=xa+1;}
 if(g->h>CH){ya=floor((ya+yb)*0.5);yb=ya+1;}
 double area=(xb-xa)*(yb-ya),sum[4]={0,0,0,0};
 if(xb<=0||yb<=0||xa>=CW||ya>=CH)return base;
 int x0=(int)floor(MAX(xa,0.0)),y0=(int)floor(MAX(ya,0.0));
 int x1=(int)ceil(MIN(xb,(double)CW)),y1=(int)ceil(MIN(yb,(double)CH));
 for(int y=y0;y<y1;y++){
  double wy=MIN(y+1.0,yb)-MAX((double)y,ya);
  for(int x=x0;x<x1;x++){
   double weight=(MIN(x+1.0,xb)-MAX((double)x,xa))*wy;
   Uint32 c=layer[y*CW+x];
   for(unsigned ch=0;ch<4;ch++)sum[ch]+=((c>>(ch*8))&255)*weight;
  }
 }
 if(sum[3]==0)return base;
 Uint32 result=UINT32_C(0xff000000);double remain=1.0-sum[3]/(255.0*area);
 for(unsigned ch=0;ch<3;ch++){
  double value=sum[ch]/area+((base>>(ch*8))&255)*remain;
  unsigned v=(unsigned)MIN(255.0,MAX(0.0,floor(value+0.5)));result|=v<<(ch*8);
 }
 return result;
}
/* Retain only the cursor/filter neighbourhood, in reusable texture tiles.
 * Capturing the normal full-frame reference before the underlay guarantees
 * the exact backend sampling phase. Neither a cropped texture copy nor a
 * clipped full copy has that guarantee on SDL's software renderer.
 * CPU staging remains one fixed tile even for very large output dimensions.
 */
static bool cursor_resources(SDL_Renderer *r,const SDL_Rect *box)
{
 size_t cols=(size_t)box->w/output.tw+(box->w%output.tw!=0);
 size_t rows=(size_t)box->h/output.th+(box->h%output.th!=0);
 if(rows&&cols>SIZE_MAX/rows)return false;
 size_t count=cols*rows;
 if(count>SIZE_MAX/sizeof(*output.cursor_tiles))return false;
 if(count>output.cursor_capacity){
  SDL_Texture **tiles=realloc(output.cursor_tiles,count*sizeof(*tiles));
  if(!tiles)return false;
  output.cursor_tiles=tiles;
  for(size_t i=output.cursor_capacity;i<count;i++)tiles[i]=NULL;
  output.cursor_capacity=count;
  for(size_t i=0;i<count;i++)if(!tiles[i]){
   tiles[i]=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,output.tw,output.th);
   if(!tiles[i]||SDL_SetTextureBlendMode(tiles[i],SDL_BLENDMODE_NONE)||SDL_SetTextureScaleMode(tiles[i],SDL_ScaleModeNearest))return false;
  }
 }
 return true;
}
static bool cursor_tiles(SDL_Renderer *r,const struct OutputGeometry *g,const SDL_Rect *box,bool save)
{
 size_t i=0;
 for(int y=box->y;y<box->y+box->h;){
  int height=MIN(output.th,box->y+box->h-y);
  for(int x=box->x;x<box->x+box->w;){
   int width=MIN(output.tw,box->x+box->w-x);
   SDL_Rect source={0,0,width,height};
   if(save){
    SDL_Rect read={x,y,width,height};
    if(SDL_RenderReadPixels(r,&read,SDL_PIXELFORMAT_ARGB8888,output.pixels,TILE_W*4)||
       SDL_UpdateTexture(output.cursor_tiles[i],&source,output.pixels,TILE_W*4))return false;
   }else{
    SDL_Rect destination={x-g->viewport.x,y-g->viewport.y,width,height};
    if(SDL_RenderCopy(r,output.cursor_tiles[i],&source,&destination))return false;
   }
   i++;x+=width;
  }
  y+=height;
 }
 return true;
}

/* Continuous reconstruction belongs only to the title-font overlay. Enlarge
 * the completed correlated premultiplied layer, not individual glyph passes.
 * Fully covered flat interiors stay exact; artwork never enters this filter. */
static Uint32 sample_overlay(const Uint32 *layer,const struct OutputGeometry *g,int px,int py,Uint32 base)
{
 if(g->w<=CW&&g->h<=CH)return sample(layer,g,px,py,base);
 double xa=(px-g->x)*CW/g->w,xb=(px+1.0-g->x)*CW/g->w;
 double ya=(py-g->y)*CH/g->h,yb=(py+1.0-g->y)*CH/g->h;
 bool mx=g->w>CW,my=g->h>CH;double fx=0,fy=0;
 if(mx){double c=(xa+xb)*0.5-0.5;xa=floor(c);fx=c-xa;xb=xa+2;}
 if(my){double c=(ya+yb)*0.5-0.5;ya=floor(c);fy=c-ya;yb=ya+2;}
 double area=(mx?1:xb-xa)*(my?1:yb-ya),sum[4]={0,0,0,0};
 if(xb<=0||yb<=0||xa>=CW||ya>=CH)return base;
 int x0=(int)floor(MAX(xa,0.0)),y0=(int)floor(MAX(ya,0.0));
 int x1=(int)ceil(MIN(xb,(double)CW)),y1=(int)ceil(MIN(yb,(double)CH));
 for(int y=y0;y<y1;y++){
  double wy=my?(y==ya?1-fy:fy):MIN(y+1.0,yb)-MAX((double)y,ya);
  for(int x=x0;x<x1;x++){
   double wx=mx?(x==xa?1-fx:fx):MIN(x+1.0,xb)-MAX((double)x,xa);
   Uint32 c=layer[y*CW+x];for(unsigned ch=0;ch<4;ch++)sum[ch]+=((c>>(ch*8))&255)*wx*wy;
  }
 }
 if(sum[3]==0)return base;
 Uint32 result=UINT32_C(0xff000000);double remain=1.0-sum[3]/(255.0*area);
 for(unsigned ch=0;ch<3;ch++){
  double v=sum[ch]/area+((base>>(ch*8))&255)*remain;
  result|=(unsigned)MIN(255.0,MAX(0.0,floor(v+0.5)))<<(ch*8);
 }
 return result;
}

static bool present(SDL_Renderer *renderer,SDL_Texture *reference,
 SDL_Surface *underlay,ScalerFunction scale,const SDL_Rect *dst,
 const Uint32 *layer,const SDL_Rect *support,const Uint8 *cursor,unsigned radius,bool smooth)
{
 struct OutputGeometry g;SDL_RendererInfo info;SDL_Rect canonical={0,0,CW,CH};
 SDL_Rect ink,cursor_box={0,0,0,0};Uint8 old_r,old_g,old_b,old_a;bool ok=false,changed_scale=false;
 if(!renderer||!reference||!underlay||!underlay->pixels||!underlay->format||
    underlay->w!=IW||underlay->h!=IH||underlay->pitch<IW||underlay->format->BytesPerPixel!=1||
    !scale||!dst||dst->w<=0||dst->h<=0||!layer||!support||radius>1||
    support->w<0||support->h<0||SDL_GetRendererInfo(renderer,&info)||!geometry(renderer,dst,&info,&g))return false;
 ink=*support;intersect(&ink,&canonical);
 /* Check the API's premultiplication contract before touching the frame. */
 for(int y=ink.y;y<ink.y+ink.h;y++)for(int x=ink.x;x<ink.x+ink.w;x++){
  Uint32 c=layer[y*CW+x];unsigned a=c>>24;
  if((c&255)>a||((c>>8)&255)>a||((c>>16)&255)>a)return false;
 }
 SDL_ScaleMode mode;if(SDL_GetTextureScaleMode(reference,&mode))return false;
 int pad=(int)radius+(mode==SDL_ScaleModeNearest?0:1);
 int px=pad*4+(smooth&&g.w>CW?1:0),py=pad*4+(smooth&&g.h>CH?1:0);
 SDL_Rect changed=mapped_box(&g,MAX(0,ink.x-px),MAX(0,ink.y-py),
  MIN(CW,ink.x+ink.w+px)-MAX(0,ink.x-px),MIN(CH,ink.y+ink.h+py)-MAX(0,ink.y-py));
 if(cursor){
  int l=IW,t=IH,r=0,b=0;
  for(int y=0;y<IH;y++)for(int x=0;x<IW;x++)if(cursor[y*IW+x]){l=MIN(l,x);t=MIN(t,y);r=MAX(r,x+1);b=MAX(b,y+1);}
  if(l<r&&t<b){
   l=MAX(0,l-pad);t=MAX(0,t-pad);r=MIN(IW,r+pad);b=MIN(IH,b+pad);
   cursor_box=mapped_box(&g,l*4,t*4,(r-l)*4,(b-t)*4);
   intersect(&cursor_box,&changed);
  }
 }
 bool has_cursor=cursor_box.w>0&&cursor_box.h>0;
 if(!resources(renderer,reference,&info)||(has_cursor&&!cursor_resources(renderer,&cursor_box))){selector_font_output_release();return false;}
 if(SDL_GetRenderDrawColor(renderer,&old_r,&old_g,&old_b,&old_a))return false;
 if(has_cursor){
  if(SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||
     SDL_RenderCopy(renderer,reference,NULL,dst)||!cursor_tiles(renderer,&g,&cursor_box,true))goto finish;
 }
 scale(underlay,output.underlay);
 if(SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,output.underlay,NULL,dst))goto finish;
 if(SDL_RenderSetScale(renderer,1,1))goto finish;
 changed_scale=true;
 for(int ty=changed.y;ty<changed.y+changed.h;){
  int height=MIN(output.th,changed.y+changed.h-ty);
  for(int tx=changed.x;tx<changed.x+changed.w;){
   int width=MIN(output.tw,changed.x+changed.w-tx);
   SDL_Rect tile={tx,ty,width,height};
   if(SDL_RenderReadPixels(renderer,&tile,SDL_PIXELFORMAT_ARGB8888,output.pixels,TILE_W*4))goto finish;
   for(int y=0;y<height;y++)for(int x=0;x<width;x++){
    unsigned p=y*TILE_W+x;int ox=tx+x,oy=ty+y;
    output.pixels[p]=smooth?sample_overlay(layer,&g,ox,oy,output.pixels[p]):sample(layer,&g,ox,oy,output.pixels[p]);
   }
   SDL_Rect source={0,0,width,height},destination={tx-g.viewport.x,ty-g.viewport.y,width,height};
   if(SDL_UpdateTexture(output.tile,&source,output.pixels,TILE_W*4)||SDL_RenderCopy(renderer,output.tile,&source,&destination))goto finish;
   tx+=width;
  }
  ty+=height;
 }
 if(has_cursor&&!cursor_tiles(renderer,&g,&cursor_box,false))goto finish;
 ok=true;
 finish:
 /* A genuine state/resource error leaves presentation to the classic caller. */
 if(changed_scale&&SDL_RenderSetScale(renderer,g.sx,g.sy))ok=false;
 if(SDL_SetRenderDrawColor(renderer,old_r,old_g,old_b,old_a))ok=false;
 if(ok)SDL_RenderPresent(renderer);else selector_font_output_release();
 return ok;
}

bool selector_font_output_present(SDL_Renderer *r,SDL_Texture *reference,
 SDL_Surface *underlay,ScalerFunction scale,const SDL_Rect *dst,
 const Uint32 *layer,const SDL_Rect *support,const Uint8 *cursor,unsigned radius)
{return present(r,reference,underlay,scale,dst,layer,support,cursor,radius,false);}

bool selector_font_output_present_smooth(SDL_Renderer *r,SDL_Texture *reference,
 SDL_Surface *underlay,ScalerFunction scale,const SDL_Rect *dst,
 const Uint32 *layer,const SDL_Rect *support,const Uint8 *cursor,unsigned radius)
{return present(r,reference,underlay,scale,dst,layer,support,cursor,radius,true);}

/* Title artwork has its own authenticated RGBA compositor, so it supplies the
 * unchanged rendered underlay rather than an indexed scaler source. Reuse the
 * exact same output-footprint arithmetic, geometry and bounded tile. */
bool selector_font_output_overlay(SDL_Renderer *renderer,const SDL_Rect *dst,
 const Uint32 *layer,const SDL_Rect *support)
{
 struct OutputGeometry g;SDL_RendererInfo info;SDL_Rect canonical={0,0,CW,CH};
 if(!renderer||!dst||dst->w<=0||dst->h<=0||!layer||!support||support->w<0||support->h<0||
    SDL_GetRendererInfo(renderer,&info)||!geometry(renderer,dst,&info,&g))return false;
 SDL_Rect ink=*support;intersect(&ink,&canonical);
 for(int y=ink.y;y<ink.y+ink.h;y++)for(int x=ink.x;x<ink.x+ink.w;x++){
  Uint32 c=layer[y*CW+x];unsigned a=c>>24;
  if((c&255)>a||((c>>8)&255)>a||((c>>16)&255)>a)return false;
 }
 if(output.renderer&&output.renderer!=renderer)selector_font_output_release();
 if(!output.tile){
  output.renderer=renderer;
  output.tw=info.max_texture_width>0?MIN(TILE_W,info.max_texture_width):TILE_W;
  output.th=info.max_texture_height>0?MIN(TILE_H,info.max_texture_height):TILE_H;
  if(output.tw<1||output.th<1)return false;
  output.tile=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,output.tw,output.th);
  if(!output.tile||SDL_SetTextureBlendMode(output.tile,SDL_BLENDMODE_NONE)||
     SDL_SetTextureScaleMode(output.tile,SDL_ScaleModeNearest)){
   selector_font_output_release();return false;
  }
 }
 int px=g.w>CW?1:0,py=g.h>CH?1:0;
 SDL_Rect changed=mapped_box(&g,ink.x-px,ink.y-py,ink.w+2*px,ink.h+2*py);
 if(SDL_RenderSetScale(renderer,1,1))return false;
 bool ok=false;
 for(int ty=changed.y;ty<changed.y+changed.h;){
  int height=MIN(output.th,changed.y+changed.h-ty);
  for(int tx=changed.x;tx<changed.x+changed.w;){
   int width=MIN(output.tw,changed.x+changed.w-tx);
   SDL_Rect tile={tx,ty,width,height};
   if(SDL_RenderReadPixels(renderer,&tile,SDL_PIXELFORMAT_ARGB8888,output.pixels,TILE_W*4))goto finish;
   for(int y=0;y<height;y++)for(int x=0;x<width;x++){
    unsigned p=y*TILE_W+x;output.pixels[p]=sample_overlay(layer,&g,tx+x,ty+y,output.pixels[p]);
   }
   SDL_Rect source={0,0,width,height},destination={tx-g.viewport.x,ty-g.viewport.y,width,height};
   if(SDL_UpdateTexture(output.tile,&source,output.pixels,TILE_W*4)||SDL_RenderCopy(renderer,output.tile,&source,&destination))goto finish;
   tx+=width;
  }
  ty+=height;
 }
 ok=true;
 finish:
 if(SDL_RenderSetScale(renderer,g.sx,g.sy))ok=false;
 if(!ok)selector_font_output_release();
 return ok;
}
