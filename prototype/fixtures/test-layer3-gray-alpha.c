#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_EXPLOSION=106,ASSET_SHAPESZ=201};
#include "production-types.inc"
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x);abort();}++checks;}while(0)
static unsigned long checks;
static SDL_Surface storage,screen,*canvas=&storage,*game_screen=&screen;
static int game_probe_density;
static bool game_probe_original_reference,game_probe_local_blend,game_probe_missing,game_probe_invalid;
static const char *game_probe_assets="/nonexistent-layer3-gray-fixture",*reject_reason;
static bool suppress,suppress_green_smoke,suppress_cloud,active=true;
static unsigned draws,local_entities,region_count,green_head_count,traces,occlusions,terrain_source_count,game_probe_scene_assets=2;
static char terrain_file;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[256];
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[256];
typedef struct {Uint16 peak[16][14];} GreenBackground;
static Uint8 *cloud_owner,*hd_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static Uint8 selected[320*200],expected[320*200];
static unsigned ids[]={121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154};
static Uint8 rgba[18][192*224*4],original[18][672],indexed[320*36];
static void unreachable(void){CHECK(!"unrelated effect or restore path executed");}
static int explosion_asset_slot(unsigned i){(void)i;unreachable();return -1;}
static void restore_classic_rect(SDL_Rect r){(void)r;unreachable();}
static void render_mirror_unsupported(const char *why){fprintf(stderr,"unexpected: %s\n",why);unreachable();}
static void green_background_snapshot(GreenBackground *b,int x,int y){(void)b;(void)x;(void)y;unreachable();}
static void enemy_filter_rgba(const Uint8 *s,Uint8 f,Uint8 *d){(void)s;(void)f;(void)d;unreachable();}
static Uint32 palette_rgb(Uint8 i){return 0xff000000u|((unsigned)i*71%256)<<16|((unsigned)i*37%256)<<8|((unsigned)i*19%256);}
static unsigned green_background_peak(const GreenBackground *b,int x,int y,Uint32 p){(void)b;(void)x;(void)y;(void)p;unreachable();return 0;}
static void explosion_asset_blend_rgba(Uint32 p,const Uint8 *s,Uint8 *d){(void)p;(void)s;(void)d;unreachable();}
static Uint32 green_head_composite(int x,int y,unsigned f,Uint32 p){(void)x;(void)y;(void)f;(void)p;unreachable();return 0;}
static Uint32 cloud_shadow_rgba(Uint32 p,Uint8 a,Uint8 b){(void)p;(void)a;(void)b;unreachable();return 0;}
static void render_mirror_reset_banking(void){}
static void asset_debug_terrain_row(int x,int y,Uint8 **map){(void)x;(void)y;CHECK(map);}
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{(void)x;(void)y;bool found=false;for(unsigned j=0;j<18;j++)found|=ids[j]==id;CHECK(role==201&&found&&part==0&&style==MIRROR_NORMAL&&mirrored);traces++;}
#include "production-helpers.inc"
static Uint32 background(unsigned n){return 0xff203040u+(n%71)*0x00010101u;}
static Uint8 initial_owner(unsigned n){return (Uint8)(n%3);}
static Uint32 normal_color(Uint32 old,const Uint8 *p)
{
 Uint32 out=0xff000000u;for(int c=0;c<3;c++){unsigned shift=(unsigned)(2-c)*8;out|=((((old>>shift)&255)*(255-p[3])+p[c]*p[3]+127)/255)<<shift;}return out;
}
static void setup(unsigned j,int fractional,int missing)
{
 memset(assets,0,sizeof(assets));render_mirror_map_begin('Z');render_mirror_bind_terrain(3,ids[j],original[j]);
 for(unsigned k=0;k<672;k++)original[j][k]=(k%24+k/24+ids[j])%4?((Uint8)(ids[j]+k)%254+1):0;
 const unsigned alpha[]={1,127,128,254,255};
 for(unsigned ay=0;ay<224;ay++)for(unsigned ax=0;ax<192;ax++){
  unsigned k=ay*192+ax;bool occupied=original[j][(ay/8)*24+ax/8]!=0;
  rgba[j][4*k]=(Uint8)(ids[j]+ax*3+ay);rgba[j][4*k+1]=(Uint8)(ids[j]*3+ax+ay*5);rgba[j][4*k+2]=(Uint8)(ids[j]*7+ax*11+ay);
  rgba[j][4*k+3]=occupied?(fractional?alpha[(ax+2*ay)%5]:255):0;
 }
 if(missing!=1)assets[272+j]=(Asset){true,missing==0,201,(int)ids[j],24,28,0,0,8,rgba[j]};
 size_t n=(size_t)canvas->w*canvas->h;
 for(size_t k=0;k<n;k++){((Uint32*)canvas->pixels)[k]=background((unsigned)k);cloud_owner[k]=1;hd_owner[k]=initial_owner((unsigned)k);green_first[k]=7;green_under[k]=0xabcdef01;green_under_owner[k]=2;}
 memset(indexed,17,sizeof(indexed));memset(expected,17,sizeof(expected));memset(selected,0,sizeof(selected));region_count=green_head_count=draws=local_entities=traces=occlusions=0;
 suppress=suppress_cloud=suppress_green_smoke=false;
}
static void assert_pixels(unsigned j,int x,int y,int missing,bool indexed_draw)
{
 int d=game_probe_density;
 for(int cy=0;cy<canvas->h;cy++)for(int cx=0;cx<canvas->w;cx++){
  unsigned k=(unsigned)(cy*canvas->w+cx);int ax=cx-x*d,ay=cy-y*d;
  bool inside=ax>=0&&ay>=0&&ax<24*d&&ay<28*d;
  const Uint8 *p=inside?rgba[j]+4*((ay*8/d)*192+ax*8/d):NULL;
  bool covered=p&&p[3];Uint8 classic=inside?original[j][(ay/d)*24+ax/d]:0;
  Uint32 wanted=covered&&!missing?normal_color(background(k),p):inside&&classic&&missing&&indexed_draw?palette_rgb(classic):background(k);
  CHECK(((Uint32*)canvas->pixels)[k]==wanted);
  bool overwritten=(covered&&!missing)||(inside&&classic&&missing&&indexed_draw);
  CHECK(cloud_owner[k]==(overwritten?0:1));CHECK(green_first[k]==(overwritten?0:7));
  Uint8 owner=covered&&!missing?1:inside&&classic&&missing&&indexed_draw?0:initial_owner(k);
  CHECK(hd_owner[k]==owner);CHECK(green_under[k]==0xabcdef01);CHECK(green_under_owner[k]==2);
 }
 for(int cy=0;cy<36;cy++)for(int cx=0;cx<320;cx++){
  int ax=cx-x,ay=cy-y;bool inside=ax>=0&&ay>=0&&ax<24&&ay<28;
  Uint8 value=inside?original[j][ay*24+ax]:0;
  CHECK(indexed[cy*320+cx]==(indexed_draw&&value?value:17));CHECK(expected[cy*320+cx]==(indexed_draw&&value?value:17));
 }
}
int main(void)
{
 SDL_PixelFormat format={8};screen=(SDL_Surface){320,36,320,indexed,&format};
 for(int d=2;d<=8;d*=2){
  game_probe_density=d;canvas->w=64*d;canvas->h=36*d;canvas->pitch=canvas->w*4;
  size_t n=(size_t)canvas->w*canvas->h;canvas->pixels=malloc(n*4);cloud_owner=malloc(n);hd_owner=malloc(n);green_under_owner=malloc(n);green_first=malloc(n*2);green_under=malloc(n*4);
  CHECK(canvas->pixels&&cloud_owner&&hd_owner&&green_under_owner&&green_first&&green_under);
  for(unsigned j=0;j<18;j++)for(int fractional=0;fractional<2;fractional++)for(int placement=0;placement<3;placement++){
   int x=placement==2?32:0,y=placement==0?1:placement==1?-3:30;Uint8 *row[12]={original[j]};
   setup(j,fractional,0);CHECK(render_mirror_terrain_row(game_screen,x,y,row,MIRROR_NORMAL)==1);CHECK(draws==1&&traces==1&&!suppress&&!suppress_cloud&&!suppress_green_smoke);assert_pixels(j,x,y,0,false);
   if(y>=0){setup(j,fractional,0);blit_background_row(game_screen,x,y,row);CHECK(draws==1&&traces==1&&!suppress);assert_pixels(j,x,y,0,true);}
  }
  /* Real original writes remain identical with missing, invalid or null assets. */
  for(unsigned j=0;j<18;j++)for(int missing=1;missing<=2;missing++){
   setup(j,1,missing);Uint8 *row[12]={original[j]};blit_background_row(game_screen,0,1,row);CHECK(!draws&&!traces&&!region_count&&!local_entities);assert_pixels(j,0,1,missing,true);
  }
  /* Both non-NORMAL styles return before loading/drawing/restoring anything. */
  for(unsigned j=0;j<18;j++)for(int style=1;style<=3;style++){
   setup(j,1,0);Uint8 *row[12]={original[j]};CHECK(!render_mirror_terrain_row(game_screen,0,1,row,style));CHECK(!draws&&!traces&&!region_count&&!local_entities&&!suppress);
   for(size_t k=0;k<n;k++){CHECK(((Uint32*)canvas->pixels)[k]==background((unsigned)k));CHECK(cloud_owner[k]==1&&green_first[k]==7&&hd_owner[k]==initial_owner((unsigned)k));}
  }
  setup(0,1,0);Uint8 *empty[12]={0};blit_background_row(game_screen,0,1,empty);CHECK(!draws&&!traces);assert_pixels(0,0,1,1,false);
  free(canvas->pixels);free(cloud_owner);free(hd_owner);free(green_under_owner);free(green_first);free(green_under);
 }
 printf("PASS: %lu assertions; actual NORMAL row/compositor/original indexed blitter and pixel callback, all18 gray IDs,2x/4x/8x, binary/fractional alpha, clipping, missing/invalid/null fallback, exact RGBA/owner metadata/indexed writes; non-NORMAL styles do not draw or restore.\n",checks);return 0;
}
