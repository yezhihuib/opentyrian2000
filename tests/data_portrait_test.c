/* SPDX-License-Identifier: GPL-2.0-or-later */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
static unsigned allocations,fail_at;
static void *test_malloc(size_t n){if(++allocations==fail_at)return NULL;return malloc(n);}
#define malloc test_malloc
#include "../src/data_portrait.c"
#undef malloc
struct Source{unsigned w,h,n;const Uint8 *rle;};
static struct Source shapes[2][256];
static unsigned u16(const Uint8 *p){return p[0]|(unsigned)p[1]<<8;}
static Uint8 *read_file(const char *dir,const char *name,size_t n){char path[4096];assert(snprintf(path,sizeof(path),"%s/%s",dir,name)>0);FILE *f=fopen(path,"rb");assert(f);Uint8 *p=malloc(n);assert(p);assert(fread(p,1,n,f)==n&&fgetc(f)==EOF);assert(!fclose(f));return p;}
static void load_shapes(const Uint8 *p){for(unsigned b=4;b<=5;++b){unsigned k=dp_u32(p+2+4*b),count=u16(p+k);k+=2;assert(count<=256);for(unsigned id=0;id<count;++id){if(!p[k++])continue;unsigned w=u16(p+k),h=u16(p+k+2),n=u16(p+k+4);k+=6;shapes[b-4][id]=(struct Source){w,h,n,p+k};k+=n;assert(k<=505983);}}}
static void sprite(SDL_Surface *s,int ox,int oy,struct Source sp){unsigned x=0,y=0,k=0;while(k<sp.n){unsigned v=sp.rle[k++];if(v==255)x+=sp.rle[k++];else if(v==254)x=sp.w;else if(v==253)++x;else{assert(x<sp.w&&y<sp.h);Uint8 *at=(Uint8 *)s->pixels+(oy+(int)y)*s->pitch+ox+(int)x;*at=(Uint8)v;data_frame_pixel(s,at);data_portrait_pixel(s,at);++x;}assert(x<=sp.w);if(x==sp.w){x=0;++y;}}}
static void base_render(SDL_Renderer *r,SDL_Surface *s,const SDL_Rect *dst,const Uint32 *rgb){Uint32 *pixels=malloc(4096000);assert(pixels);for(unsigned y=0;y<800;++y)for(unsigned x=0;x<1280;++x)pixels[y*1280+x]=rgb[((Uint8 *)s->pixels)[(y/4)*s->pitch+x/4]];SDL_Texture *t=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STATIC,1280,800);assert(t);assert(!SDL_UpdateTexture(t,NULL,pixels,1280*4));free(pixels);assert(!SDL_SetTextureBlendMode(t,SDL_BLENDMODE_NONE));assert(!SDL_SetTextureScaleMode(t,SDL_ScaleModeNearest));SDL_SetRenderDrawColor(r,7,11,19,255);assert(!SDL_RenderClear(r));assert(!SDL_RenderCopy(r,t,NULL,dst));SDL_DestroyTexture(t);}
static void start(SDL_Surface *s,SDL_Surface *bg,const char *art,const char *frame){data_portrait_set_directory(art);data_frame_set_directory(frame);SDL_BlitSurface(bg,NULL,s,NULL);data_frame_begin(7,s,bg,true);data_portrait_begin(7,s,true);struct Source sp=shapes[1][20];data_frame_surround_begin(s,sp.rle,sp.n,sp.w,sp.h);for(unsigned y=1;y<171;++y)memset((Uint8 *)s->pixels+y*s->pitch+1,0,145);sprite(s,1,1,sp);data_frame_surround_end(s);}
static void face(SDL_Surface *s,unsigned id){struct Source sp=shapes[0][id];int x=77-(int)sp.w/2,y=92-(int)sp.h/2;data_portrait_capture(s,id,dp_pins[id].palette,x,y,sp.rle,sp.n,sp.w,sp.h);sprite(s,x,y,sp);data_portrait_face_done(s);}
static void set_palette(Uint32 *rgb,const Uint8 *pal,const SDL_PixelFormat *fmt,unsigned face)
{
 unsigned which=face<DP_COUNT?dp_pins[face].palette:0;
 for(unsigned i=0;i<256;++i){unsigned b=(i>=1&&i<=207)?which*768:0;rgb[i]=SDL_MapRGB(fmt,(pal[b+i*3]<<2)|(pal[b+i*3]>>4),(pal[b+i*3+1]<<2)|(pal[b+i*3+1]>>4),(pal[b+i*3+2]<<2)|(pal[b+i*3+2]>>4));}
}
/* Link only unaffected resources read-only. Each bad target has separate storage,
 * so fixture mutations can never alter the approved pack. */
static void fixture(const char *root,const char *assets,const char *label,unsigned bad,const Uint8 *raw,size_t n,int fifo)
{
 char dir[4096],path[4096],source[4096];
 assert(snprintf(dir,sizeof(dir),"%s/%s-%02u",root,label,bad)<(int)sizeof(dir));assert(!mkdir(dir,0700));
 for(unsigned id=0;id<DP_COUNT;++id){assert(snprintf(path,sizeof(path),"%s/face%02u-v1.hda",dir,id)<(int)sizeof(path));
  if(id!=bad){assert(snprintf(source,sizeof(source),"%s/face%02u-v1.hda",assets,id)<(int)sizeof(source));assert(!symlink(source,path));}
  else if(fifo)assert(!mkfifo(path,0600));
  else if(raw){FILE *f=fopen(path,"wb");assert(f&&fwrite(raw,1,n,f)==n&&!fclose(f));}
 }
 data_portrait_set_directory(dir);
 for(unsigned id=0;id<DP_COUNT;++id){load_resource(id);assert(resources[id].valid==(id!=bad));assert((resources[id].art!=NULL)==(id!=bad));}
}
int main(int argc,char **argv)
{
 assert(argc==5);assert(!SDL_Init(SDL_INIT_VIDEO));
 Uint8 *shp=read_file(argv[1],"tyrian.shp",505983),*pic=read_file(argv[1],"tyrian.pic",367161),*pal=read_file(argv[1],"palette.dat",18432);load_shapes(shp);
 for(unsigned f=0;f<DP_COUNT;++f){assert(dp_pins[f].w<=DP_MAX_W&&dp_pins[f].h<=DP_MAX_H);assert(source_ok(&dp_pins[f],shapes[0][f].rle,shapes[0][f].n));}
 SDL_Surface *s=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8),*bg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);assert(s&&bg);
 unsigned off=dp_u32(pic+2),n=0;while(n<64000){unsigned v=pic[off++],run=1;if((v&192)==192){run=v&63;v=pic[off++];}while(run--)((Uint8 *)bg->pixels)[n++]=(Uint8)v;}
 SDL_PixelFormat *fmt=SDL_AllocFormat(SDL_PIXELFORMAT_ARGB8888);assert(fmt);Uint32 rgb[256];unsigned cases=0;Uint8 before[64000];
 const unsigned widths[]={1280,640,1280},heights[]={800,400,720};
 for(unsigned size=0;size<3;++size){
  unsigned w=widths[size],h=heights[size];SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_ARGB8888);assert(target);SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);assert(r);
  SDL_Rect dst=size==2?(SDL_Rect){64,0,1152,720}:(SDL_Rect){0,0,(int)w,(int)h};Uint32 *under=malloc((size_t)w*h*4),*baseline=malloc((size_t)w*h*4);assert(under&&baseline);
  for(unsigned f=0;f<=DP_COUNT;++f){
   set_palette(rgb,pal,fmt,f);start(s,bg,argv[2],argv[3]);base_render(r,s,&dst,rgb);assert(data_frame_present(r,s,&dst,rgb,fmt));assert(!SDL_RenderReadPixels(r,NULL,fmt->format,under,(int)w*4));
   if(f<DP_COUNT)face(s,f);assert(data_portrait_active(s)==(f<DP_COUNT));memcpy(before,s->pixels,64000);
   base_render(r,s,&dst,rgb);assert(data_frame_present(r,s,&dst,rgb,fmt));assert(!SDL_RenderReadPixels(r,NULL,fmt->format,baseline,(int)w*4));uint64_t native=dp_hash(baseline,(size_t)w*h*4);
   bool shown=data_portrait_present(r,s,&dst,rgb,fmt);assert(shown==(f<DP_COUNT));assert(!memcmp(before,s->pixels,64000));assert(!SDL_RenderReadPixels(r,NULL,fmt->format,target->pixels,target->pitch));assert((dp_hash(target->pixels,(size_t)target->pitch*h)!=native)==(f<DP_COUNT));
   if(f<DP_COUNT){
    const struct DPPin *pin=&dp_pins[f];assert(palette_ok(pin,rgb,fmt));assert(data_frame_underlay_ready(s,rgb,fmt));Uint32 high=rgb[224];rgb[224]^=1;assert(!data_frame_underlay_ready(s,rgb,fmt));rgb[224]=high;
    /* Independently compose EVERY art sample over the actual rendered pre-face
     * underlay. This includes transparent margins and FACE15's rim overlap. */
    if(!size)for(unsigned y=0;y<800;++y)for(unsigned x=0;x<1280;++x){
     Uint32 got=((Uint32 *)target->pixels)[y*1280+x];
     if(x<pin->x*4||x>=(pin->x+pin->w)*4||y<pin->y*4||y>=(pin->y+pin->h)*4){assert(got==baseline[y*1280+x]);continue;}
     const Uint8 *p=dp.art+((y-pin->y*4)*pin->w*4+x-pin->x*4)*4;Uint8 ur,ug,ub;SDL_GetRGB(under[y*1280+x],fmt,&ur,&ug,&ub);unsigned a=p[3];
     Uint32 expected=0xff000000|((p[0]*a+ur*(255-a)+127)/255)<<16|((p[1]*a+ug*(255-a)+127)/255)<<8|((p[2]*a+ub*(255-a)+127)/255);
     for(unsigned shift=0;shift<24;shift+=8)assert(abs((int)((got>>shift)&255)-(int)((expected>>shift)&255))<=2);
    }
    data_portrait_begin(8,s,false);assert(data_portrait_active(s));data_portrait_transition(true);assert(!data_portrait_present(r,s,&dst,rgb,fmt));data_portrait_transition(false);assert(data_portrait_present(r,s,&dst,rgb,fmt));
    Uint32 c=rgb[75];rgb[75]^=1;assert(!data_portrait_present(r,s,&dst,rgb,fmt));rgb[75]=c;
    /* Later same-index opaque writes, fills and cursor own complete cells. */
    Uint8 *at=(Uint8 *)s->pixels+80*s->pitch+77;unsigned cell=(80-pin->y)*pin->w+77-pin->x;data_portrait_pixel(s,at);assert(dp.blocked[cell]);
    SDL_Rect fill={(int)pin->x+2,(int)pin->y+2,4,3};assert(!SDL_FillRect(s,&fill,0));data_portrait_rect(s,&fill);assert(dp.blocked[2*pin->w+2]);
    data_portrait_cursor_begin(s);Uint8 *outside=(Uint8 *)s->pixels+150*s->pitch+250;Uint8 old=*outside;*outside^=1;data_portrait_pixel(s,outside);Uint8 *inside=(Uint8 *)s->pixels+95*s->pitch+90;Uint8 oldin=*inside;*inside=224;data_portrait_pixel(s,inside);data_portrait_cursor_done();assert(data_portrait_present(r,s,&dst,rgb,fmt));
    *outside=old;*inside=oldin;data_portrait_cursor_restored(s);assert(data_portrait_present(r,s,&dst,rgb,fmt));*outside^=1;assert(!data_portrait_present(r,s,&dst,rgb,fmt)&&!dp.active);*outside=old;
   }
   ++cases;
  }
  data_portrait_invalidate();data_frame_invalidate();free(under);free(baseline);SDL_DestroyRenderer(r);SDL_FreeSurface(target);
 }
 assert(cases==57);
 for(unsigned f=0;f<DP_COUNT;++f){
  const struct DPPin *pin=&dp_pins[f];struct Source sp=shapes[0][f];
  start(s,bg,argv[2],argv[3]);data_portrait_capture(s,f,pin->palette,pin->x,pin->y,sp.rle,sp.n-1,pin->w,pin->h);assert(!dp.active);
  start(s,bg,argv[2],argv[3]);data_portrait_capture(s,f,pin->palette,pin->x-1,pin->y,sp.rle,sp.n,pin->w,pin->h);assert(!dp.active);
  start(s,bg,argv[2],argv[3]);data_portrait_capture(s,f,pin->palette+1,pin->x,pin->y,sp.rle,sp.n,pin->w,pin->h);assert(!dp.active);
  Uint8 *changed=malloc(sp.n);assert(changed);memcpy(changed,sp.rle,sp.n);changed[sp.n/2]^=1;assert(!source_ok(pin,changed,sp.n));free(changed);
  start(s,bg,argv[2],argv[3]);face(s,f);data_portrait_invalidate();assert(!data_portrait_active(s));
  char name[64];assert(snprintf(name,sizeof(name),"face%02u-v1.hda",f)>0);Uint8 *raw=read_file(argv[2],name,128+pin->bytes);assert(valid_header(raw,f,pin));
  for(unsigned i=0;i<128;++i){raw[i]^=1;assert(!valid_header(raw,f,pin));raw[i]^=1;}
  fixture(argv[4],argv[2],"missing",f,NULL,0,0);fixture(argv[4],argv[2],"header",f,raw,90,0);fixture(argv[4],argv[2],"truncated",f,raw,127+pin->bytes,0);
  raw[140]^=1;fixture(argv[4],argv[2],"payload",f,raw,128+pin->bytes,0);raw[140]^=1;
  raw[64]^=1;fixture(argv[4],argv[2],"source-header",f,raw,128+pin->bytes,0);raw[64]^=1;
  Uint8 *extra=malloc(129+pin->bytes);assert(extra);memcpy(extra,raw,128+pin->bytes);extra[128+pin->bytes]=0;fixture(argv[4],argv[2],"extra",f,extra,129+pin->bytes,0);free(extra);
  fixture(argv[4],argv[2],"fifo",f,NULL,0,1);free(raw);
  data_portrait_set_directory(argv[2]);allocations=0;fail_at=1;load_resource(f);assert(!resources[f].valid&&!resources[f].art);fail_at=0;load_resource((f+1)%DP_COUNT);assert(resources[(f+1)%DP_COUNT].valid);
 }
 data_portrait_set_directory("/missing");for(unsigned f=0;f<DP_COUNT;++f){load_resource(f);assert(!resources[f].valid);}
 start(s,bg,argv[2],argv[3]);data_portrait_capture(s,DP_COUNT,0,0,0,NULL,0,0,0);assert(!dp.active);
 start(s,bg,argv[2],argv[3]);face(s,7);set_palette(rgb,pal,fmt,7);free(dp.output);dp.output=NULL;allocations=0;fail_at=1;
 SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);assert(!data_portrait_present(r,s,&(SDL_Rect){0,0,640,400},rgb,fmt));fail_at=0;assert(data_portrait_present(r,s,&(SDL_Rect){0,0,640,400},rgb,fmt));
 dp.cursor_expected[0]=1;data_portrait_end();assert(!dp.cursor_expected[0]);
 data_portrait_set_directory("/missing");data_frame_invalidate();SDL_DestroyRenderer(r);SDL_FreeSurface(target);free(shp);free(pic);free(pal);SDL_FreeFormat(fmt);SDL_FreeSurface(s);SDL_FreeSurface(bg);SDL_Quit();
 puts("PASS DPR1 all18 HD + noPortrait x3 viewports; every underlay/alpha sample within SDL rounding2; variable geometry including FACE15 rim; independent per-face source/header/payload/length/missing/FIFO/allocation fallback; later same-index ownership, cursor, F6, fade, palette, unknown-write; native INDEX8 exact");return 0;
}
