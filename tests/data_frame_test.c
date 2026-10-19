/* SPDX-License-Identifier: GPL-2.0-or-later */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <limits.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned allocations,fail_at;
static void *test_malloc(size_t n){if(++allocations==fail_at)return NULL;return malloc(n);}
#define malloc test_malloc
#include "../src/data_frame.c"
#undef malloc
struct SpriteSource {unsigned w,h,n;const Uint8 *rle;};
static unsigned read16(const Uint8 *p){return p[0]|(unsigned)p[1]<<8;}
static Uint8 *read_file(const char *dir,const char *name,size_t bytes)
{char path[4096];assert(snprintf(path,sizeof(path),"%s/%s",dir,name)>0);FILE *f=fopen(path,"rb");assert(f);Uint8 *p=malloc(bytes);assert(p);assert(fread(p,1,bytes,f)==bytes&&fgetc(f)==EOF);assert(!fclose(f));return p;}
static struct SpriteSource shapes[2][256];
static void load_shapes(const Uint8 *p)
{
 for(unsigned bank=4;bank<=5;++bank){unsigned off=df_u32(p+2+4*bank),count=read16(p+off);off+=2;assert(count<=256);
  for(unsigned id=0;id<count;++id){if(!p[off++])continue;unsigned w=read16(p+off),h=read16(p+off+2),n=read16(p+off+4);off+=6;shapes[bank-4][id]=(struct SpriteSource){w,h,n,p+off};off+=n;assert(off<=505983);}
 }
}
static void native_sprite(SDL_Surface *s,int ox,int oy,struct SpriteSource sp,bool observe,Uint8 *mask)
{
 unsigned x=0,y=0,k=0;while(k<sp.n){unsigned v=sp.rle[k++];if(v==255)x+=sp.rle[k++];else if(v==254)x=sp.w;else if(v==253)++x;else{assert(x<sp.w&&y<sp.h);int px=ox+(int)x,py=oy+(int)y;assert(px>=0&&px<320&&py>=0&&py<200);Uint8 *at=(Uint8 *)s->pixels+py*s->pitch+px;*at=(Uint8)v;if(observe)data_frame_pixel(s,at);if(mask)mask[py*320+px]=1;++x;}assert(x<=sp.w);if(x==sp.w){x=0;++y;}}
}
static void start(SDL_Surface *s,SDL_Surface *bg,struct SpriteSource surround,const char *assets,unsigned menu)
{
 data_frame_set_directory(assets);SDL_BlitSurface(bg,NULL,s,NULL);data_frame_begin(menu,s,bg,true);
 if(menu!=7&&menu!=8)return;assert(df.active);data_frame_surround_begin(s,surround.rle,surround.n,surround.w,surround.h);
 for(unsigned y=1;y<171;++y)memset((Uint8 *)s->pixels+y*s->pitch+1,0,145);
 native_sprite(s,1,1,surround,true,NULL);data_frame_surround_end(s);assert(data_frame_active(s));
}
static void native_render(SDL_Renderer *r,SDL_Surface *s,const SDL_Rect *dst,const Uint32 *rgb,unsigned density,const Uint8 *mask)
{
 unsigned w=320*density,h=200*density;Uint32 *pixels=malloc((size_t)w*h*4);assert(pixels);
 for(unsigned y=0;y<h;++y)for(unsigned x=0;x<w;++x){unsigned cell=(y/density)*320+x/density;pixels[y*w+x]=mask?(mask[cell]?0xffffffff:0xff000000):rgb[((Uint8 *)s->pixels)[(y/density)*s->pitch+x/density]];}
 SDL_Texture *texture=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STATIC,(int)w,(int)h);assert(texture);assert(!SDL_UpdateTexture(texture,NULL,pixels,(int)w*4));free(pixels);assert(!SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_NONE));assert(!SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest));
 SDL_SetRenderDrawColor(r,7,11,19,255);assert(!SDL_RenderClear(r));assert(!SDL_RenderCopy(r,texture,NULL,dst));SDL_DestroyTexture(texture);
}
static void write_fixture(const char *root,const char *label,const Uint8 *p,size_t n)
{
 char dir[4096],name[4096];assert(snprintf(dir,sizeof(dir),"%s/%s",root,label)<(int)sizeof(dir));assert(!mkdir(dir,0700));assert(snprintf(name,sizeof(name),"%s/data-frame-v1.hda",dir)<(int)sizeof(name));FILE *f=fopen(name,"wb");assert(f);assert(fwrite(p,1,n,f)==n);assert(!fclose(f));data_frame_set_directory(dir);load_resource();assert(!df.valid&&!df.art);
}
int main(int argc,char **argv)
{
 assert(argc==4);assert(!SDL_Init(SDL_INIT_VIDEO));
 Uint8 *shp=read_file(argv[1],"tyrian.shp",505983),*pic=read_file(argv[1],"tyrian.pic",367161),*pal=read_file(argv[1],"palette.dat",18432);
 assert(df_hash(shp,505983)==UINT64_C(0x5e490c45465ef7b0));assert(df_hash(pic,367161)==UINT64_C(0xa348ffcf393764e0));assert(df_hash(pal,18432)==UINT64_C(0x85e04ee4cd9cca88));load_shapes(shp);struct SpriteSource surround=shapes[1][20];
 SDL_Surface *s=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8),*bg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);assert(s&&bg);
 unsigned off=df_u32(pic+2),n=0;while(n<64000){unsigned v=pic[off++],run=1;if((v&192)==192){run=v&63;v=pic[off++];}while(run--){((Uint8 *)bg->pixels)[n++]=(Uint8)v;}}
 assert(df_hash(bg->pixels,64000)==UINT64_C(0x45a77a2246c174b9));
 SDL_PixelFormat *fmt=SDL_AllocFormat(SDL_PIXELFORMAT_ARGB8888);assert(fmt);Uint32 rgb[256];
 for(unsigned i=0;i<256;++i)rgb[i]=SDL_MapRGB(fmt,(pal[i*3]<<2)|(pal[i*3]>>4),(pal[i*3+1]<<2)|(pal[i*3+1]>>4),(pal[i*3+2]<<2)|(pal[i*3+2]>>4));assert(palette_ok(rgb,fmt));
 Uint8 face_mask[64000],before[64000];unsigned faces=0,rendered=0;
 const unsigned widths[]={640,1280,1280},heights[]={400,800,720};
 for(unsigned size=0;size<3;++size){unsigned width=widths[size],height=heights[size];SDL_Surface *target=SDL_CreateRGBSurfaceWithFormat(0,width,height,32,SDL_PIXELFORMAT_ARGB8888);assert(target);SDL_Renderer *r=SDL_CreateSoftwareRenderer(target);assert(r);SDL_Rect dst=size==2?(SDL_Rect){64,0,1152,720}:(SDL_Rect){0,0,(int)width,(int)height};
  Uint32 *baseline=malloc((size_t)width*height*4),*ownership=malloc((size_t)width*height*4);assert(baseline&&ownership);
  for(unsigned density=2;density<=4;density+=2)for(unsigned face=0;face<=18;++face){start(s,bg,surround,argv[2],face&1?7:8);memset(face_mask,0,sizeof(face_mask));if(face<18){struct SpriteSource sp=shapes[0][face];assert(sp.n);native_sprite(s,77-(int)sp.w/2,92-(int)sp.h/2,sp,true,face_mask);if(!size&&density==2)++faces;}
   /* Protect every native later opaque face and same-index text/cube footprint. */
   SDL_Rect fill={160,39,151,128};assert(!SDL_FillRect(s,&fill,228));data_frame_rect(s,&fill);assert(df.blocked[39*320+160]&&df.blocked[166*320+310]);
   Uint8 *at=(Uint8 *)s->pixels+180*s->pitch+77;data_frame_pixel(s,at);assert(df.blocked[180*320+77]);copy_indices(before,s);
   native_render(r,s,&dst,rgb,density,face_mask);assert(!SDL_RenderReadPixels(r,NULL,fmt->format,ownership,(int)width*4));
   native_render(r,s,&dst,rgb,density,NULL);assert(!SDL_RenderReadPixels(r,NULL,fmt->format,baseline,(int)width*4));uint64_t native_output=df_hash(baseline,(size_t)width*height*4);
   assert(data_frame_present(r,s,&dst,rgb,fmt));assert(!SDL_RenderReadPixels(r,NULL,fmt->format,target->pixels,target->pitch));assert(df_hash(target->pixels,(size_t)target->pitch*height)!=native_output);
   assert(!memcmp(before,s->pixels,64000));
   for(unsigned y=0;y<height;++y)for(unsigned x=0;x<width;++x)if(ownership[y*width+x]==0xffffffff){Uint32 c;memcpy(&c,(Uint8 *)target->pixels+y*target->pitch+x*4,4);if(c!=baseline[y*width+x]){fprintf(stderr,"face%u size%u density%u output%u,%u got%08x native%08x\n",face,size,density,x,y,c,baseline[y*width+x]);abort();}}
   /* Persist reader ownership across F6/redraw without recapturing static art. */
   unsigned blocked=df.blocked[180*320+77];data_frame_begin(8,s,bg,false);assert(data_frame_active(s)&&df.blocked[180*320+77]==blocked);
   data_frame_transition(true);uint64_t paused=df_hash(target->pixels,(size_t)target->pitch*height);assert(!data_frame_present(r,s,&dst,rgb,fmt));assert(paused==df_hash(target->pixels,(size_t)target->pitch*height));data_frame_transition(false);
   Uint32 saved=rgb[224];rgb[224]^=1;assert(!data_frame_present(r,s,&dst,rgb,fmt));rgb[224]=saved;
   data_frame_invalidate();assert(!data_frame_active(s)&&!data_frame_present(r,s,&dst,rgb,fmt));
   start(s,bg,surround,argv[2],7);assert(data_frame_present(r,s,&dst,rgb,fmt));
   /* Cursor may write same-index values, then restore without static holes. */
   unsigned cell=100*320+20;Uint8 original=((Uint8 *)s->pixels)[cell];unsigned oldblocked=df.blocked[cell];data_frame_cursor_begin(s);((Uint8 *)s->pixels)[cell]=224;data_frame_pixel(s,(Uint8 *)s->pixels+cell);data_frame_cursor_done();assert(df.cursor_mask[cell]&&df.blocked[cell]==oldblocked);assert(data_frame_present(r,s,&dst,rgb,fmt));((Uint8 *)s->pixels)[cell]=original;data_frame_cursor_restored(s);assert(data_frame_present(r,s,&dst,rgb,fmt)&&df.blocked[cell]==oldblocked);
   /* An unobserved changed write conservatively revokes this lease. */
   ((Uint8 *)s->pixels)[cell]^=1;assert(!data_frame_present(r,s,&dst,rgb,fmt)&&!df.active);++rendered;
  }
  data_frame_invalidate();free(baseline);free(ownership);SDL_DestroyRenderer(r);SDL_FreeSurface(target);
 }
 assert(faces==18&&rendered==114);
 for(unsigned menu=0;menu<17;++menu)if(menu!=7&&menu!=8){data_frame_begin(menu,s,bg,true);assert(!df.active);}
 start(s,bg,surround,argv[2],7);data_frame_surround_begin(s,surround.rle,surround.n-1,surround.w,surround.h);assert(!df.active);
 ((Uint8 *)bg->pixels)[0]^=1;data_frame_begin(7,s,bg,true);assert(!df.active);((Uint8 *)bg->pixels)[0]^=1;
 Uint8 *resource=read_file(argv[2],"data-frame-v1.hda",128+DF_BYTES);
 assert(valid_header(resource));for(unsigned field=0;field<128;++field){resource[field]^=1;assert(!valid_header(resource));resource[field]^=1;}
 write_fixture(argv[3],"short-header",resource,90);write_fixture(argv[3],"truncated",resource,127+DF_BYTES);resource[128+10]^=1;write_fixture(argv[3],"payload",resource,128+DF_BYTES);resource[128+10]^=1;
 Uint8 *extra=malloc(129+DF_BYTES);assert(extra);memcpy(extra,resource,128+DF_BYTES);extra[128+DF_BYTES]=0;write_fixture(argv[3],"extra",extra,129+DF_BYTES);free(extra);
 char path[4096],fifo[4096];assert(snprintf(path,sizeof(path),"%s/fifo",argv[3])<(int)sizeof(path));assert(!mkdir(path,0700));assert(snprintf(fifo,sizeof(fifo),"%s/data-frame-v1.hda",path)<(int)sizeof(fifo));assert(!mkfifo(fifo,0600));data_frame_set_directory(path);load_resource();assert(!df.valid);
 data_frame_set_directory("/missing");load_resource();assert(!df.valid);
 data_frame_set_directory(argv[2]);allocations=0;fail_at=1;load_resource();assert(!df.valid&&!df.art);fail_at=0;
 start(s,bg,surround,argv[2],7);free(df.output);df.output=NULL;allocations=0;fail_at=1;SDL_Surface *small=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);SDL_Renderer *r=SDL_CreateSoftwareRenderer(small);assert(!data_frame_present(r,s,&(SDL_Rect){0,0,640,400},rgb,fmt));fail_at=0;assert(data_frame_present(r,s,&(SDL_Rect){0,0,640,400},rgb,fmt));
 data_frame_set_directory("/missing");SDL_DestroyRenderer(r);SDL_FreeSurface(small);free(resource);free(shp);free(pic);free(pal);SDL_FreeFormat(fmt);SDL_FreeSurface(s);SDL_FreeSurface(bg);SDL_Quit();
 puts("PASS Data DFM1: 18 native faces + no-portrait x3 viewports; 132 corruptions; source/palette/menu/fade/cursor/same-index/unknown-write/allocation/FIFO fallback; INDEX8 unchanged");return 0;
}
