/* Synthetic production code tests. No original game data or game execution. */
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "SDL.h"

static unsigned opens,reads,allocs,creates,destroys;
static int fail_open,fail_stat,fail_read,short_read,fail_close,fail_alloc,fail_sdl;
static struct {void *p;size_t bytes;} allocations[4];
static size_t live_bytes,peak_bytes;
static int checked_open(const char *p,int flags) {++opens;return fail_open?-1:open(p,flags);}
static int checked_stat(int f,struct stat *s) {return fail_stat?-1:fstat(f,s);}
static ssize_t checked_read(int f,void *p,size_t n)
{
 ++reads;if((int)reads==fail_read){errno=EINTR;return -1;}
 return read(f,p,n-((int)reads==short_read));
}
static int checked_close(int f){int result=close(f);return fail_close?-1:result;}
static void *checked_malloc(size_t n)
{
 ++allocs;if((int)allocs==fail_alloc)return NULL;
 void *p=malloc(n);if(!p)return NULL;
 for(unsigned i=0;i<4;i++)if(!allocations[i].p){allocations[i].p=p;allocations[i].bytes=n;live_bytes+=n;if(live_bytes>peak_bytes)peak_bytes=live_bytes;return p;}
 assert(!"Allocation ledger exhausted");return NULL;
}
static void checked_free(void *p)
{
 if(!p)return;
 for(unsigned i=0;i<4;i++)if(allocations[i].p==p){live_bytes-=allocations[i].bytes;allocations[i].p=NULL;free(p);return;}
 assert(!"Free did not match a production allocation");
}
static SDL_Texture *checked_create(SDL_Renderer *r,Uint32 f,int a,int w,int h)
{++creates;return fail_sdl==1?NULL:SDL_CreateTexture(r,f,a,w,h);}
static int checked_scale(SDL_Texture *t,SDL_ScaleMode m){return fail_sdl==2?-1:SDL_SetTextureScaleMode(t,m);}
static int checked_blend(SDL_Texture *t,SDL_BlendMode m){return fail_sdl==3?-1:SDL_SetTextureBlendMode(t,m);}
static int checked_update(SDL_Texture *t,const SDL_Rect *r,const void *p,int pitch){return fail_sdl==4?-1:SDL_UpdateTexture(t,r,p,pitch);}
static int checked_color(SDL_Renderer *r,Uint8 a,Uint8 b,Uint8 c,Uint8 d){return fail_sdl==5?-1:SDL_SetRenderDrawColor(r,a,b,c,d);}
static int checked_clear(SDL_Renderer *r){return fail_sdl==6?-1:SDL_RenderClear(r);}
static int checked_copy(SDL_Renderer *r,SDL_Texture *t,const SDL_Rect *s,const SDL_Rect *d){return fail_sdl==7?-1:SDL_RenderCopy(r,t,s,d);}
static void checked_destroy(SDL_Texture *t){++destroys;SDL_DestroyTexture(t);}
#define open checked_open
#define fstat checked_stat
#define read checked_read
#define close checked_close
#define malloc checked_malloc
#define free checked_free
#define SDL_CreateTexture checked_create
#define SDL_SetTextureScaleMode checked_scale
#define SDL_SetTextureBlendMode checked_blend
#define SDL_UpdateTexture checked_update
#define SDL_SetRenderDrawColor checked_color
#define SDL_RenderClear checked_clear
#define SDL_RenderCopy checked_copy
#define SDL_DestroyTexture checked_destroy
#include "startup_logos.c"
#undef open
#undef fstat
#undef read
#undef close
#undef malloc
#undef free
#undef SDL_CreateTexture
#undef SDL_SetTextureScaleMode
#undef SDL_SetTextureBlendMode
#undef SDL_UpdateTexture
#undef SDL_SetRenderDrawColor
#undef SDL_RenderClear
#undef SDL_RenderCopy
#undef SDL_DestroyTexture

SDL_Surface *VGAScreen,*VGAScreenSeg;
SDL_PixelFormat *main_window_tex_format;
Uint32 rgb_palette[256];
static SDL_Surface *display;
static SDL_Renderer *renderer;
static SDL_Rect dst={0,0,1280,800};
static Uint8 indices[2][64000],*resource[2];
static SDL_Color targets[2][256],engine_palette[256];
static const char *directory;
static char paths[2][2048];

static void put32(Uint8 *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(Uint8)(v>>(8*i));}
static void put64(Uint8 *p,uint64_t v){for(unsigned i=0;i<8;i++)p[i]=(Uint8)(v>>(8*i));}
static void reset_faults(void)
{
 fail_open=fail_stat=fail_read=short_read=fail_close=fail_alloc=fail_sdl=0;
 opens=reads=allocs=0;
}
static void write_resource(unsigned card,const void *data,size_t size)
{
 FILE *f=fopen(paths[card],"wb");assert(f);assert(fwrite(data,1,size,f)==size);assert(fclose(f)==0);
}
static void pack(unsigned card)
{
 resource[card]=malloc(MFG_FILE);assert(resource[card]);
 Uint8 *h=resource[card];memset(h,0,MFG_HEADER);memcpy(h,"MFG1",4);
 const Uint32 fields[]={1,4,10+2*card,20+2*card,320,200,MFG_PAYLOAD};
 for(unsigned i=0;i<7;i++)put32(h+4+i*4,fields[i]);
 put64(h+32,card_specs[card].indices);put64(h+40,card_specs[card].rgb);
 for(size_t i=0;i<MFG_PIXELS;i++) {
  h[64+i*4]=(Uint8)(i*7+card*9);h[65+i*4]=(Uint8)(i/13+card*11);
  h[66+i*4]=(Uint8)(i/37+card*15);h[67+i*4]=255;
 }
 put64(h+48,mfg_hash(UINT64_C(14695981039346656037),h+64,MFG_PAYLOAD));
 write_resource(card,h,MFG_FILE);
}
static void apply_engine_palette(void)
{
 for(unsigned i=0;i<256;i++)rgb_palette[i]=SDL_MapRGB(main_window_tex_format,engine_palette[i].r,engine_palette[i].g,engine_palette[i].b);
}
static void prepare(unsigned card)
{
 for(unsigned y=0;y<200;y++)memcpy((Uint8 *)VGAScreen->pixels+y*VGAScreen->pitch,indices[card]+y*320,320);
 Uint8 v=card?0:255;
 for(unsigned i=0;i<256;i++)engine_palette[i]=(SDL_Color){v,v,v,255};
 apply_engine_palette();
}
static void begin_card(unsigned card)
{
 startup_logos_begin();
 /* Missing PIC10 advances its explicit binding, never inferred from content. */
 if(card){prepare(0);startup_logos_bind(VGAScreen,10,NULL);assert(!phase);}
 prepare(card);startup_logos_bind(VGAScreen,10+card*2,targets[card]);
}
static void assert_unchanged(unsigned card,const Uint32 palette_before[256])
{
 assert(!memcmp(palette_before,rgb_palette,sizeof(rgb_palette)));
 for(unsigned y=0;y<200;y++)assert(!memcmp((Uint8 *)VGAScreen->pixels+y*VGAScreen->pitch,indices[card]+y*320,320));
}
static void check_output(unsigned card,int solid)
{
 for(size_t i=0;i<MFG_PIXELS;i++) {
  const Uint8 *p=resource[card]+64+i*4;
  Uint32 want=solid>=0?UINT32_C(0xff000000)|(Uint32)solid*UINT32_C(0x010101):
    UINT32_C(0xff000000)|((Uint32)p[0]<<16)|((Uint32)p[1]<<8)|p[2];
  assert(card_output[i]==want);
 }
}
static void fade(unsigned card,bool incoming)
{
 int steps=incoming?(card?10:25):10;SDL_Color black={0,0,0,255};
 const SDL_Color *want=incoming?targets[card]:NULL;
 Uint32 before[256];memcpy(before,rgb_palette,sizeof(before));
 startup_logos_fade_start(want,incoming?NULL:&black,0,255);
 assert(phase==(incoming?CARD_FADING_IN:CARD_FADING_OUT));assert_unchanged(card,before);
 for(int remaining=steps;remaining;--remaining) {
  for(unsigned i=0;i<256;i++) {
   SDL_Color target=incoming?targets[card][i]:black;
   engine_palette[i].r+=(int)(target.r-engine_palette[i].r)/remaining;
   engine_palette[i].g+=(int)(target.g-engine_palette[i].g)/remaining;
   engine_palette[i].b+=(int)(target.b-engine_palette[i].b)/remaining;
  }
  apply_engine_palette();memcpy(before,rgb_palette,sizeof(before));
  Uint32 old=card_output[123456],expected=UINT32_C(0xff000000);
  for(unsigned c=0;c<3;c++) {
   unsigned shift=16-c*8;int prior=(old>>shift)&255,target=incoming?resource[card][64+4*123456+c]:0;
   expected|=(Uint32)(prior+(target-prior)/remaining)<<shift;
  }
  startup_logos_fade_step(remaining,0,255);assert(phase);assert(card_output[123456]==expected);
  assert_unchanged(card,before);
 }
 assert(phase==(incoming?CARD_HOLD:CARD_BLACK));check_output(card,incoming?-1:0);
}
static void check_present(void)
{
 assert(startup_logos_present(renderer,VGAScreen,&dst));
 for(int y=0;y<800;y++)assert(!memcmp((Uint8 *)display->pixels+(size_t)y*display->pitch,card_output+(size_t)y*1280,1280*4));
 unsigned saved_allocs=allocs,saved_reads=reads,saved_opens=opens,saved_creates=creates;
 assert(startup_logos_present(renderer,VGAScreen,&dst));
 assert(allocs==saved_allocs&&reads==saved_reads&&opens==saved_opens&&creates==saved_creates);
}
static void test_native2x(void)
{
 begin_card(0);fade(0,true);check_present();
 startup_logos_release_texture();SDL_DestroyRenderer(renderer);SDL_FreeSurface(display);
 display=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);assert(display);
 renderer=SDL_CreateSoftwareRenderer(display);assert(renderer);
 SDL_Rect two={0,0,640,400};assert(startup_logos_present(renderer,VGAScreen,&two));
 for(int y=0;y<400;y++)for(int x=0;x<640;x++) {
  const Uint32 *row=(const Uint32 *)((const Uint8 *)display->pixels+(size_t)y*display->pitch);
  assert(row[x]==card_output[(size_t)(2*y+1)*1280+2*x+1]);
 }
 startup_logos_release_texture();SDL_DestroyRenderer(renderer);SDL_FreeSurface(display);
 display=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);assert(display);
 renderer=SDL_CreateSoftwareRenderer(display);assert(renderer);startup_logos_end();
}
static void test_sequence(void)
{
 begin_card(0);assert(phase==CARD_INITIAL);check_output(0,255);check_present();
 fade(0,true);check_present();
 startup_logos_release_texture();assert(!card_texture&&phase==CARD_HOLD);check_present();
 fade(0,false);check_present();
 startup_logos_reset();prepare(1);startup_logos_bind(VGAScreen,12,targets[1]);
 assert(phase==CARD_INITIAL);check_output(1,0);fade(1,true);check_present();fade(1,false);
 startup_logos_bind(VGAScreen,12,targets[1]);assert(!phase&&!card_rgba&&!card_output);
 startup_logos_bind(VGAScreen,10,targets[0]);assert(!phase&&!card_rgba&&!card_output);
 startup_logos_end();assert(!context&&!phase&&!card_rgba&&!card_output&&!card_texture);
 assert(!startup_logos_present(renderer,VGAScreen,&dst));
 startup_logos_shutdown();startup_logos_shutdown();
}
static void rejected_file(const void *data,size_t size)
{
 write_resource(0,data,size);reset_faults();begin_card(0);assert(!phase&&!card_rgba&&!card_output);startup_logos_end();
}
static void test_loader(void)
{
 Uint8 *bad=malloc(MFG_FILE+1);assert(bad);
 for(unsigned offset=0;offset<64;offset++) {
  memcpy(bad,resource[0],MFG_FILE);bad[offset]^=1;rejected_file(bad,MFG_FILE);
 }
 const size_t lengths[]={0,3,63,64,MFG_FILE-1};
 for(unsigned i=0;i<sizeof(lengths)/sizeof(*lengths);i++)rejected_file(resource[0],lengths[i]);
 memcpy(bad,resource[0],MFG_FILE);bad[MFG_FILE]=0;rejected_file(bad,MFG_FILE+1);
 memcpy(bad,resource[0],MFG_FILE);bad[MFG_FILE-4]^=1;rejected_file(bad,MFG_FILE);
 for(unsigned alpha=0;alpha<255;alpha+=17) {
  memcpy(bad,resource[0],MFG_FILE);bad[67]=(Uint8)alpha;
  put64(bad+48,mfg_hash(UINT64_C(14695981039346656037),bad+64,MFG_PAYLOAD));rejected_file(bad,MFG_FILE);
 }
 assert(unlink(paths[0])==0);reset_faults();begin_card(0);assert(!phase);
 prepare(1);startup_logos_bind(VGAScreen,12,targets[1]);assert(phase);startup_logos_end();
 assert(mkdir(paths[0],0700)==0);begin_card(0);assert(!phase);startup_logos_end();assert(rmdir(paths[0])==0);
 assert(mkfifo(paths[0],0600)==0);begin_card(0);assert(!phase);startup_logos_end();assert(unlink(paths[0])==0);
 write_resource(0,resource[0],MFG_FILE);
 for(int fault=0;fault<12;fault++) {
  reset_faults();switch(fault){case 0:fail_open=1;break;case 1:fail_stat=1;break;
   case 2:fail_read=1;break;case 3:fail_read=2;break;case 4:fail_read=3;break;
   case 5:short_read=1;break;case 6:short_read=2;break;case 7:fail_close=1;break;
   case 8:fail_alloc=1;break;case 9:fail_alloc=2;break;
   case 10:asset_directory="";break;case 11:{static char longpath[2048];memset(longpath,'x',sizeof(longpath)-1);asset_directory=longpath;break;}}
  begin_card(0);assert(!phase&&!card_rgba&&!card_output);startup_logos_end();asset_directory=directory;
 }
 reset_faults();free(bad);
 /* Second file's failure cannot revoke already completed first-card output. */
 write_resource(1,resource[1],63);begin_card(0);assert(phase);fade(0,true);fade(0,false);
 prepare(1);startup_logos_bind(VGAScreen,12,targets[1]);assert(!phase);startup_logos_end();write_resource(1,resource[1],MFG_FILE);
}
static void test_registration(void)
{
 for(unsigned fault=0;fault<12;fault++) {
  startup_logos_begin();prepare(0);reset_faults();
  void *pixels=VGAScreen->pixels;SDL_PixelFormat *format=VGAScreen->format;
  SDL_Color changed[256];memcpy(changed,targets[0],sizeof(changed));
  SDL_Surface other=*VGAScreen;SDL_Surface *source=VGAScreen;const SDL_Color *target=targets[0];
  switch(fault) {
   case 0:((Uint8 *)VGAScreen->pixels)[123]^=1;break;
   case 1:changed[23].r^=1;target=changed;break;
   case 2:rgb_palette[17]^=1;break;
   case 3:VGAScreen->w=319;break;
   case 4:VGAScreen->h=199;break;
   case 5:VGAScreen->pitch=2147483647;break;
   case 6:VGAScreen->format->BitsPerPixel=16;break;
   case 7:VGAScreen->pixels=NULL;break;
   case 8:VGAScreen->format=NULL;break;
   case 9:source=&other;break;
   case 10:source=NULL;break;
   case 11:target=NULL;break;
  }
  startup_logos_bind(source,10,target);assert(!phase&&opens==0&&allocs==0);
  VGAScreen->pixels=pixels;VGAScreen->format=format;format->BitsPerPixel=8;
  VGAScreen->w=320;VGAScreen->h=200;VGAScreen->pitch=320;startup_logos_end();
 }
}
static void test_lease(void)
{
 startup_logos_end();prepare(0);startup_logos_bind(VGAScreen,10,targets[0]);assert(!phase);
 startup_logos_begin();prepare(0);startup_logos_bind(VGAScreen,12,targets[0]);assert(!phase);startup_logos_end();
 for(unsigned mode=0;mode<10;mode++) {
  begin_card(0);assert(phase);
  switch(mode) {
   case 0:((Uint8 *)VGAScreen->pixels)[100]^=1;break;
   case 1:rgb_palette[100]^=1;break;
   case 2:VGAScreen->w=319;break;
   case 3:VGAScreen->h=199;break;
   case 4:VGAScreen->pitch++;break;
   case 5:VGAScreen->format->BitsPerPixel=16;break;
   case 6:VGAScreen->format->BytesPerPixel=2;break;
   case 7:VGAScreenSeg=NULL;break;
   case 8:{void *p=VGAScreen->pixels;VGAScreen->pixels=indices[1];assert(!startup_logos_present(renderer,VGAScreen,&dst));VGAScreen->pixels=p;break;}
   case 9:{SDL_PixelFormat *p=VGAScreen->format;VGAScreen->format=NULL;assert(!startup_logos_present(renderer,VGAScreen,&dst));VGAScreen->format=p;break;}
  }
  assert(!startup_logos_present(renderer,VGAScreen,&dst));assert(!phase);
  if(mode==2)VGAScreen->w=320;
  if(mode==3)VGAScreen->h=200;
  if(mode==4)--VGAScreen->pitch;
  if(mode==5)VGAScreen->format->BitsPerPixel=8;
  if(mode==6)VGAScreen->format->BytesPerPixel=1;
  VGAScreenSeg=VGAScreen;startup_logos_end();
 }
 begin_card(0);startup_logos_fade_start(targets[0],NULL,0,239);assert(!phase);
 begin_card(0);startup_logos_fade_start(targets[1],NULL,0,255);assert(!phase);
 begin_card(0);startup_logos_fade_start(targets[0],NULL,0,255);startup_logos_fade_step(24,0,255);assert(!phase);
 begin_card(0);startup_logos_fade_start(targets[0],NULL,0,255);startup_logos_fade_step(25,0,255);assert(!phase); /* Palette did not advance. */
 begin_card(0);assert(!startup_logos_present(renderer,NULL,&dst));assert(!phase);
 begin_card(0);assert(!startup_logos_present(NULL,VGAScreen,&dst));assert(!phase);
 for(int fault=1;fault<=7;fault++) {
  reset_faults();begin_card(0);assert(phase);fail_sdl=fault;
  assert(!startup_logos_present(renderer,VGAScreen,&dst));assert(!phase&&!card_texture&&!card_output&&!card_rgba);
 }
 reset_faults();startup_logos_end();
}
int main(int argc,char **argv)
{
 assert(argc==2);directory=argv[1];assert(SDL_Init(0)==0);
 VGAScreen=VGAScreenSeg=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);assert(VGAScreen);
 main_window_tex_format=SDL_AllocFormat(SDL_PIXELFORMAT_RGB888);assert(main_window_tex_format);
 display=SDL_CreateRGBSurfaceWithFormat(0,1280,800,32,SDL_PIXELFORMAT_ARGB8888);assert(display);
 renderer=SDL_CreateSoftwareRenderer(display);assert(renderer);
 for(unsigned card=0;card<2;card++) {
  for(unsigned i=0;i<64000;i++)indices[card][i]=(Uint8)((i*7+card*19)%253);
  for(unsigned i=0;i<256;i++)targets[card][i]=(SDL_Color){(Uint8)(i*3+card*5),(Uint8)(i*7+card*11),(Uint8)(i*13+card*17),255};
  snprintf(paths[card],sizeof(paths[card]),"%s/%s",directory,card_specs[card].filename);pack(card);
 }
 assert(!startup_logos_configured());assert(!startup_logos_set_directory(NULL));assert(!startup_logos_set_directory(""));
 startup_logos_begin();assert(!context);startup_logos_bind(VGAScreen,10,targets[0]);assert(!phase&&opens==0);
 assert(startup_logos_set_directory(directory));assert(startup_logos_configured());reset_faults();
 test_sequence();test_loader();test_registration();test_lease();test_native2x();test_sequence();startup_logos_shutdown();
 assert(live_bytes==0&&peak_bytes==2*MFG_PAYLOAD);
 assert(destroys<=creates);free(resource[0]);free(resource[1]);
 SDL_DestroyRenderer(renderer);SDL_FreeSurface(display);SDL_FreeSurface(VGAScreen);SDL_FreeFormat(main_window_tex_format);SDL_Quit();
 puts("MFG1 synthetic production loader, ownership, fade endpoints, presentation, fault and lifetime checks passed");
 return 0;
}
