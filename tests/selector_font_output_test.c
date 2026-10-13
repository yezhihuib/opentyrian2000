/* Renderer-only tests: synthetic pixels, no game, original data or artwork. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "SDL.h"
#include <stdbool.h>

enum FaultKind { F_NONE,F_CREATE,F_REALLOC,F_READ,F_UPDATE,F_COPY };
static enum FaultKind fault_kind;
static unsigned fault_after,fault_count,module_creates,module_textures,module_presents;
static bool fail(enum FaultKind kind){return kind==fault_kind&&fault_count++==fault_after;}
static SDL_Texture *checked_create(SDL_Renderer *r,Uint32 f,int a,int w,int h)
{module_creates++;if(fail(F_CREATE))return NULL;SDL_Texture *t=SDL_CreateTexture(r,f,a,w,h);if(t)module_textures++;return t;}
static void checked_destroy(SDL_Texture *t){if(t)module_textures--;SDL_DestroyTexture(t);}
static void *checked_realloc(void *p,size_t n){return fail(F_REALLOC)?NULL:realloc(p,n);}
static int checked_read(SDL_Renderer *r,const SDL_Rect *rect,Uint32 f,void *p,int pitch)
{return fail(F_READ)?-1:SDL_RenderReadPixels(r,rect,f,p,pitch);}
static int checked_update(SDL_Texture *t,const SDL_Rect *rect,const void *p,int pitch)
{return fail(F_UPDATE)?-1:SDL_UpdateTexture(t,rect,p,pitch);}
static int checked_copy(SDL_Renderer *r,SDL_Texture *t,const SDL_Rect *s,const SDL_Rect *d)
{return fail(F_COPY)?-1:SDL_RenderCopy(r,t,s,d);}
static void checked_present(SDL_Renderer *r){module_presents++;SDL_RenderPresent(r);}
#define SDL_CreateTexture checked_create
#define SDL_DestroyTexture checked_destroy
#define SDL_RenderReadPixels checked_read
#define SDL_UpdateTexture checked_update
#define SDL_RenderCopy checked_copy
#define SDL_RenderPresent checked_present
#define realloc checked_realloc
#include "../src/selector_font_output.c"
#undef SDL_CreateTexture
#undef SDL_DestroyTexture
#undef SDL_RenderReadPixels
#undef SDL_UpdateTexture
#undef SDL_RenderCopy
#undef SDL_RenderPresent
#undef realloc
#include "../src/palette.h"

Uint32 rgb_palette[256],yuv_palette[256];
static unsigned checks,cases;
#define REQUIRE(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL %s:%d: %s (%s)\n",__FILE__,__LINE__,#x,SDL_GetError());exit(1);}}while(0)
static int font_left=140,font_top=80;
static Uint32 layer[CW*CH];
static Uint8 cursor[IW*IH],base_index[IW*IH],classic_index[IW*IH];
static Uint32 premul(unsigned a,unsigned r,unsigned g,unsigned b)
{return (a<<24)|(((r*a+127)/255)<<16)|(((g*a+127)/255)<<8)|((b*a+127)/255);}
static void fill_layer(void)
{
 memset(layer,0,sizeof(layer));
 for(int y=font_top*4;y<(font_top+24)*4;y++)for(int x=font_left*4;x<(font_left+30)*4;x++){
  unsigned a=(x*17+y*29)%256;
  if((x+y)%7==0)a=0;else if((x+y)%11==0)a=255;
  layer[y*CW+x]=premul(a,245,181,29);
 }
}
static Uint32 oracle(const struct OutputGeometry *g,int px,int py,Uint32 bg)
{
 long double l=(px-g->x)*CW/g->w,r=(px+1.0-g->x)*CW/g->w;
 long double t=(py-g->y)*CH/g->h,b=(py+1.0-g->y)*CH/g->h;
 if(g->w>CW){l=floorl((l+r)/2);r=l+1;}
 if(g->h>CH){t=floorl((t+b)/2);b=t+1;}
 long double area=(r-l)*(b-t),v[4]={0,0,0,0};
 for(int y=MAX(0,(int)floorl(t));y<MIN(CH,(int)ceill(b));y++){
  for(int x=MAX(0,(int)floorl(l));x<MIN(CW,(int)ceill(r));x++){
   long double weight=(fminl(r,x+1)-fmaxl(l,x))*(fminl(b,y+1)-fmaxl(t,y));
   Uint32 p=layer[y*CW+x];for(unsigned ch=0;ch<4;ch++)v[ch]+=weight*((p>>(ch*8))&255);
  }
 }
 Uint32 result=0xff000000;
 for(unsigned ch=0;ch<3;ch++){
  long double c=v[ch]/area+((bg>>(ch*8))&255)*(1-v[3]/(255*area));
  result|=(Uint32)fminl(255,fmaxl(0,floorl(c+0.5L)))<<(ch*8);
 }
 return result;
}
static bool near(Uint32 a,Uint32 b,unsigned tolerance)
{
 for(unsigned ch=0;ch<3;ch++){int d=(int)((a>>(ch*8))&255)-(int)((b>>(ch*8))&255);if(abs(d)>(int)tolerance)return false;}return true;
}
static void sampler_checks(void)
{
 struct OutputGeometry g={0};g.w=640;g.h=400;
 memset(layer,0,sizeof(layer));
 layer[0]=premul(255,255,0,0);layer[1]=premul(255,0,255,0);
 layer[CW]=premul(255,0,0,255);layer[CW+1]=premul(255,255,255,255);
 REQUIRE(sample(layer,&g,0,0,0xff172839)==0xff808080);
 REQUIRE(sample(layer,&g,1,0,0xff172839)==0xff172839);
 g.w=1280;g.h=800;REQUIRE(sample(layer,&g,0,0,0xff000000)==layer[0]);
 g.w=2560;g.h=1600;REQUIRE(sample(layer,&g,0,0,0xff000000)==layer[0]);REQUIRE(sample(layer,&g,1,1,0xff000000)==layer[0]);
 fill_layer();
 const double widths[]={320,640,800,960,1280,1365,2560};
 for(unsigned i=0;i<COUNTOF(widths);i++){
  g.x=-3.25;g.y=7.5;g.w=widths[i];g.h=widths[i]*0.73;
  for(unsigned j=0;j<120;j++){
   int x=(int)(g.x+(560+j%120)*g.w/CW),y=(int)(g.y+(320+j%96)*g.h/CH);
   REQUIRE(near(sample(layer,&g,x,y,0xff596877),oracle(&g,x,y,0xff596877),1));
  }
 }
 /* Ordered overlap must be resolved before reduction: two disjoint opaque
  * samples remain fully covered when reduced, rather than alpha=3/4. */
 memset(layer,0,sizeof(layer));layer[0]=0xffff0000;layer[1]=0xff0000ff;
 g.x=g.y=0;g.w=640;g.h=800;REQUIRE(sample(layer,&g,0,0,0xff00ff00)==0xff800080);
}
static void copy_screen(SDL_Renderer *r,SDL_Surface *surface,Uint32 *save)
{
 REQUIRE(SDL_RenderFlush(r)==0);
 for(int y=0;y<surface->h;y++)memcpy(save+y*surface->w,(Uint8 *)surface->pixels+y*surface->pitch,surface->w*4);
}
static void draw(SDL_Renderer *r,SDL_Texture *tex,SDL_Surface *source,ScalerFunction scale,SDL_Rect *dst)
{
 scale(source,tex);REQUIRE(SDL_SetRenderDrawColor(r,0,0,0,255)==0);REQUIRE(SDL_RenderClear(r)==0);REQUIRE(SDL_RenderCopy(r,tex,NULL,dst)==0);
}
static void renderer_case(unsigned scaler_id,int width,int height,int kind,SDL_ScaleMode mode)
{
 SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,width,height,32,SDL_PIXELFORMAT_ARGB8888);
 REQUIRE(screen);SDL_Renderer *r=SDL_CreateSoftwareRenderer(screen);REQUIRE(r);
 SDL_Surface *base=SDL_CreateRGBSurfaceWithFormatFrom(base_index,IW,IH,8,IW,SDL_PIXELFORMAT_INDEX8);
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormatFrom(classic_index,IW,IH,8,IW,SDL_PIXELFORMAT_INDEX8);
 REQUIRE(base&&classic);
 SDL_Texture *reference=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,scalers[scaler_id].width,scalers[scaler_id].height);REQUIRE(reference);
 REQUIRE(SDL_SetTextureScaleMode(reference,mode)==0);
 SDL_Rect dst={7,11,width-17,height-23};
 if(kind==1){dst.x=-47;dst.y=-31;dst.w=width+93;dst.h=height+79;}
 if(kind==2){
  REQUIRE(SDL_RenderSetScale(r,1.25f,1.5f)==0);
  SDL_Rect viewport={3,5,width/2,height/2};REQUIRE(SDL_RenderSetViewport(r,&viewport)==0);
  SDL_Rect clip={9,7,width/3,height/3};REQUIRE(SDL_RenderSetClipRect(r,&clip)==0);
  REQUIRE(SDL_RenderSetScale(r,0.8f,0.875f)==0);
  dst=(SDL_Rect){-11,-13,width/2,height/2};
 }
 if(kind==3){REQUIRE(SDL_RenderSetLogicalSize(r,640,400)==0);dst=(SDL_Rect){0,0,640,400};}
 SDL_Rect saved_v,saved_c;float saved_x,saved_y;int saved_lw,saved_lh;
 SDL_RenderGetViewport(r,&saved_v);SDL_RenderGetClipRect(r,&saved_c);SDL_RenderGetScale(r,&saved_x,&saved_y);SDL_RenderGetLogicalSize(r,&saved_lw,&saved_lh);
 SDL_RendererInfo info;REQUIRE(SDL_GetRendererInfo(r,&info)==0);struct OutputGeometry g;REQUIRE(geometry(r,&dst,&info,&g));
 Uint32 *base_pixels=malloc((size_t)width*height*4),*original=malloc((size_t)width*height*4),*actual=malloc((size_t)width*height*4);REQUIRE(base_pixels&&original&&actual);
 draw(r,reference,base,scalers[scaler_id].scaler32,&dst);copy_screen(r,screen,base_pixels);
 draw(r,reference,classic,scalers[scaler_id].scaler32,&dst);copy_screen(r,screen,original);
 fill_layer();SDL_Rect support={font_left*4,font_top*4,120,96};
 unsigned radius=(scaler_id==0||scaler_id==1||scaler_id==4||scaler_id==7)?0:1;
 REQUIRE(SDL_SetRenderDrawColor(r,41,42,43,44)==0);
 REQUIRE(selector_font_output_present(r,reference,base,scalers[scaler_id].scaler32,&dst,layer,&support,cursor,radius));
 copy_screen(r,screen,actual);
 unsigned allocated_before=module_creates;
 REQUIRE(selector_font_output_present(r,reference,base,scalers[scaler_id].scaler32,&dst,layer,&support,cursor,radius));
 REQUIRE(module_creates==allocated_before);
 SDL_Rect after_v,after_c;float after_x,after_y;int after_lw,after_lh;Uint8 dr,dg,db,da;
 SDL_RenderGetViewport(r,&after_v);SDL_RenderGetClipRect(r,&after_c);SDL_RenderGetScale(r,&after_x,&after_y);SDL_RenderGetLogicalSize(r,&after_lw,&after_lh);
 REQUIRE(!memcmp(&saved_v,&after_v,sizeof(saved_v))&&!memcmp(&saved_c,&after_c,sizeof(saved_c))&&saved_x==after_x&&saved_y==after_y&&saved_lw==after_lw&&saved_lh==after_lh);
 REQUIRE(SDL_GetRenderDrawColor(r,&dr,&dg,&db,&da)==0&&dr==41&&dg==42&&db==43&&da==44);REQUIRE(!SDL_GetRenderTarget(r));
 int pad=(int)radius+(mode==SDL_ScaleModeNearest?0:1);
 int cl=IW,ct=IH,cr=0,cb=0;
 for(int cy=0;cy<IH;cy++)for(int cx=0;cx<IW;cx++)if(cursor[cy*IW+cx]){cl=MIN(cl,cx);ct=MIN(ct,cy);cr=MAX(cr,cx+1);cb=MAX(cb,cy+1);}
 cl=MAX(0,cl-pad);ct=MAX(0,ct-pad);cr=MIN(IW,cr+pad);cb=MIN(IH,cb+pad);
 SDL_Rect cursor_area=mapped_box(&g,cl*4,ct*4,(cr-cl)*4,(cb-ct)*4);
 int left=MAX(0,font_left*4-pad*4),top=MAX(0,font_top*4-pad*4);
 SDL_Rect changed=mapped_box(&g,left,top,MIN(CW,(font_left+30)*4+pad*4)-left,MIN(CH,(font_top+24)*4+pad*4)-top);
 for(int y=0;y<height;y++)for(int x=0;x<width;x++){
  unsigned p=y*width+x;
  bool in=x>=changed.x&&x<changed.x+changed.w&&y>=changed.y&&y<changed.y+changed.h;
  if(!in){REQUIRE((actual[p]&0xffffff)==(base_pixels[p]&0xffffff));continue;}
  bool cur=x>=cursor_area.x&&x<cursor_area.x+cursor_area.w&&y>=cursor_area.y&&y<cursor_area.y+cursor_area.h;
  Uint32 expected=cur?original[p]:sample(layer,&g,x,y,base_pixels[p]);
  if((actual[p]&0xffffff)!=(expected&0xffffff)){
   fprintf(stderr,"case scaler=%u size=%dx%d kind=%d filter=%d at %d,%d cursor=%d got=%08x expected=%08x\n",scaler_id,width,height,kind,mode,x,y,cur,actual[p],expected);REQUIRE(false);
  }
  checks++;
 }
 /* Invalid premultiplication and render-target state must decline without
  * changing any indexed source or presenting a half-built enhanced frame. */
 layer[font_top*4*CW+font_left*4]=0x01020000;
 REQUIRE(!selector_font_output_present(r,reference,base,scalers[scaler_id].scaler32,&dst,layer,&support,cursor,radius));
 REQUIRE(!SDL_GetRenderTarget(r));
 selector_font_output_release();REQUIRE(module_textures==0);REQUIRE(!output.renderer&&!output.underlay&&!output.tile&&!output.cursor_tiles);
 free(base_pixels);free(original);free(actual);SDL_DestroyTexture(reference);SDL_DestroyRenderer(r);SDL_FreeSurface(base);SDL_FreeSurface(classic);SDL_FreeSurface(screen);cases++;
}
static void failure_checks(void)
{
 SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);
 REQUIRE(screen);SDL_Renderer *r=SDL_CreateSoftwareRenderer(screen);REQUIRE(r);
 SDL_Surface *base=SDL_CreateRGBSurfaceWithFormatFrom(base_index,IW,IH,8,IW,SDL_PIXELFORMAT_INDEX8);
 SDL_Surface *classic=SDL_CreateRGBSurfaceWithFormatFrom(classic_index,IW,IH,8,IW,SDL_PIXELFORMAT_INDEX8);REQUIRE(base&&classic);
 SDL_Texture *reference=SDL_CreateTexture(r,SDL_PIXELFORMAT_RGB888,SDL_TEXTUREACCESS_STREAMING,640,400);REQUIRE(reference);
 SDL_Rect dst={0,0,640,400},support={560,320,120,96};
 draw(r,reference,classic,scalers[1].scaler32,&dst);fill_layer();
 const struct {enum FaultKind kind;unsigned after;} faults[]={
  {F_CREATE,0},{F_CREATE,1},{F_CREATE,2},{F_REALLOC,0},
  {F_READ,0},{F_READ,1},{F_UPDATE,0},{F_UPDATE,1},{F_COPY,0},{F_COPY,1},{F_COPY,2},{F_COPY,3}
 };
 for(unsigned i=0;i<COUNTOF(faults);i++){
  selector_font_output_release();fault_kind=faults[i].kind;fault_after=faults[i].after;fault_count=0;
  unsigned presented_before=module_presents;
  REQUIRE(SDL_SetRenderDrawColor(r,71,72,73,74)==0);
  REQUIRE(!selector_font_output_present(r,reference,base,scalers[1].scaler32,&dst,layer,&support,cursor,0));
  REQUIRE(module_presents==presented_before&&module_textures==0);
  float sx,sy;SDL_RenderGetScale(r,&sx,&sy);REQUIRE(sx==1&&sy==1&&!SDL_GetRenderTarget(r));
  Uint8 cr,cg,cb,ca;SDL_GetRenderDrawColor(r,&cr,&cg,&cb,&ca);REQUIRE(cr==71&&cg==72&&cb==73&&ca==74);
  fault_kind=F_NONE;
  REQUIRE(selector_font_output_present(r,reference,base,scalers[1].scaler32,&dst,layer,&support,cursor,0));
 }
 selector_font_output_release();REQUIRE(module_textures==0);
 SDL_DestroyTexture(reference);SDL_DestroyRenderer(r);SDL_FreeSurface(base);SDL_FreeSurface(classic);SDL_FreeSurface(screen);
}
static void fixture(int fx,int fy,int cx,int cy)
{
 font_left=fx;font_top=fy;memset(cursor,0,sizeof(cursor));
 for(int y=0;y<IH;y++)for(int x=0;x<IW;x++)base_index[y*IW+x]=(Uint8)((x/3+y/5+(x*y)%11)%192);
 memcpy(classic_index,base_index,sizeof(base_index));
 for(int y=fy;y<fy+24;y++)for(int x=fx;x<fx+30;x++)if((x+y)%3)classic_index[y*IW+x]=240+(x+y)%16;
 for(int y=MAX(0,cy);y<MIN(IH,cy+12);y++)for(int x=MAX(0,cx);x<MIN(IW,cx+10);x++)if(x==cx||y==cy+11||x-cx<=y-cy){cursor[y*IW+x]=1;base_index[y*IW+x]=classic_index[y*IW+x]=233;}
}
int main(void)
{
 REQUIRE(SDL_Init(0)==0);
 for(unsigned i=0;i<256;i++){rgb_palette[i]=((i*17%256)<<16)|((i*43%256)<<8)|(i*79%256);yuv_palette[i]=rgb_palette[i];}
 fixture(140,80,151,88);
 sampler_checks();
 for(unsigned sc=0;sc<scalers_count;sc++)for(unsigned mode=0;mode<2;mode++)renderer_case(sc,801,503,0,(SDL_ScaleMode)mode);
 for(int kind=1;kind<=3;kind++)renderer_case(2,1024,768,kind,SDL_ScaleModeLinear);
 const int sizes[][2]={{320,200},{640,400},{960,600},{1280,800},{1365,767},{1920,1080},{2560,1440},{3840,2160}};
 for(unsigned i=0;i<COUNTOF(sizes);i++)renderer_case(1,sizes[i][0],sizes[i][1],0,SDL_ScaleModeNearest);
 const int edges[][4]={{0,0,-4,-5},{290,0,316,-4},{0,176,-4,195},{290,176,316,195}};
 for(unsigned i=0;i<COUNTOF(edges);i++){fixture(edges[i][0],edges[i][1],edges[i][2],edges[i][3]);renderer_case(2,801,503,0,SDL_ScaleModeLinear);}
 fixture(140,80,151,88);failure_checks();
 REQUIRE(selector_font_output_static_bytes()<35000);
 SDL_Quit();printf("selector output: %u cases, %u checks passed\n",cases,checks);return 0;
}
