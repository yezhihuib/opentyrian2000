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
typedef struct {int w,h,pitch;void *pixels;} SDL_Surface;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_EXPLOSION=106,ASSET_SHAPESZ=201};
#include "production-asset.inc"
#include "original-masks.inc"
static SDL_Surface storage,screen,*canvas=&storage,*game_screen=&screen;
static int game_probe_density;
static bool game_probe_original_reference,game_probe_local_blend;
static bool suppress,suppress_green_smoke,suppress_cloud;
static unsigned int draws,local_entities,region_count,green_head_count,checks;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[256];
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[256];
typedef struct {Uint16 peak[16][14];} GreenBackground;
static Uint8 *cloud_owner,*hd_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static Uint8 selected[320*200];
#define CHECK(x) do { assert(x); checks++; } while(0)

static Uint8 actual_rgba[2][192*224*4];
static void load_actual(void)
{
 for(int i=0;i<2;i++){
  char name[40];snprintf(name,sizeof(name),"actual-%d.rgba",i?114:111);
  FILE *f=fopen(name,"rb");assert(f);CHECK(fread(actual_rgba[i],1,sizeof(actual_rgba[i]),f)==sizeof(actual_rgba[i]));CHECK(fgetc(f)==EOF);CHECK(!fclose(f));
 }
}

static void unreachable(void){assert(!"unrelated effect branch entered");abort();}
static int explosion_asset_slot(unsigned int i){(void)i;unreachable();return -1;}
static void restore_classic_rect(SDL_Rect r){(void)r;unreachable();}
static void render_mirror_unsupported(const char *s){(void)s;unreachable();}
static void green_background_snapshot(GreenBackground *b,int x,int y){(void)b;(void)x;(void)y;unreachable();}
static void enemy_filter_rgba(const Uint8 *s,Uint8 f,Uint8 *d){(void)s;(void)f;(void)d;unreachable();}
static Uint32 palette_rgb(Uint8 i){(void)i;unreachable();return 0;}
static unsigned int green_background_peak(const GreenBackground*b,int x,int y,Uint32 dst){(void)b;(void)x;(void)y;(void)dst;unreachable();return 0;}
static void explosion_asset_blend_rgba(Uint32 p,const Uint8 *s,Uint8 *d){(void)p;(void)s;(void)d;unreachable();}
static Uint32 green_head_composite(int x,int y,unsigned int f,Uint32 p){(void)x;(void)y;(void)f;(void)p;unreachable();return 0;}
#include "production-alpha.inc"
static Uint32 background(int n){return 0xff203040u+(Uint32)(n%71)*0x00010101u;}
static Uint32 expected_color(Uint32 dest,const Uint8*src,int style)
{
 Uint32 result=0xff000000u;
 for(int c=0;c<3;c++){
  int shift=(2-c)*8;unsigned int old=(dest>>shift)&255,alpha=src[3];
  unsigned int v=style==MIRROR_SHADOW?(old*(510-alpha)+255)/510:(old*(255-alpha)+src[c]*alpha+127)/255;
  result|=v<<shift;
 }
 return result;
}
int main(void)
{
 load_actual();
 Uint8 rgba[192*224*4];
 for(int density_i=0;density_i<2;density_i++) {
  int d=density_i?8:2;game_probe_density=d;canvas->w=32*d;canvas->h=36*d;canvas->pitch=canvas->w*4;
  size_t n=(size_t)canvas->w*canvas->h;
  canvas->pixels=malloc(n*4);cloud_owner=malloc(n);hd_owner=malloc(n);green_under_owner=malloc(n);green_first=malloc(n*2);green_under=malloc(n*4);
  CHECK(canvas->pixels&&cloud_owner&&hd_owner&&green_under_owner&&green_first&&green_under);
  for(int tile=0;tile<2;tile++)for(int fractional=0;fractional<3;fractional++)for(int style_i=0;style_i<2;style_i++)for(int placement=0;placement<3;placement++) {
   int style=style_i?MIRROR_SHADOW:MIRROR_NORMAL;int x=placement==1?-1:placement==2?27:1,y=placement==1?-1:placement==2?32:1;
   for(int ay=0;ay<224;ay++)for(int ax=0;ax<192;ax++){
    int pos=ay*192+ax;bool occupied=original_masks[tile][(ay/8)*24+ax/8]!=0;
    rgba[pos*4]=occupied?137:0;rgba[pos*4+1]=occupied?91:0;rgba[pos*4+2]=occupied?44:0;
    rgba[pos*4+3]=occupied?(fractional&&ax>7&&ax<184&&ay>7&&ay<216&&((ax+ay)%3==0)?128:255):0;
   }
   if(fractional==2)memcpy(rgba,actual_rgba[tile],sizeof(rgba));
   for(size_t k=0;k<n;k++){((Uint32*)canvas->pixels)[k]=background((int)k);cloud_owner[k]=1;hd_owner[k]=1;green_first[k]=7;green_under[k]=0xabcdef01;green_under_owner[k]=2;}
   memset(selected,0,sizeof(selected));region_count=green_head_count=draws=local_entities=0;suppress=false;suppress_cloud=suppress_green_smoke=true;
   Asset asset={true,true,ASSET_SHAPESZ,tile?114:111,24,28,0,0,8,rgba};
   CHECK(draw_asset(x,y,&asset,style,NULL));CHECK(draws==1&&region_count==1&&suppress&&!suppress_cloud&&!suppress_green_smoke);CHECK(!green_head_count&&!local_entities);
   for(int cy=0;cy<canvas->h;cy++)for(int cx=0;cx<canvas->w;cx++){
    int k=cy*canvas->w+cx,ax=cx-x*d,ay=cy-y*d;
    bool inside=ax>=0&&ay>=0&&ax<24*d&&ay<28*d;
    const Uint8 *src=inside?rgba+4*((ay*8/d)*192+ax*8/d):NULL;
    bool covered=src&&src[3];Uint32 want=covered?expected_color(background(k),src,style):background(k);
    CHECK(((Uint32*)canvas->pixels)[k]==want);CHECK(cloud_owner[k]==(covered?0:1));CHECK(green_first[k]==(covered?0:7));CHECK(hd_owner[k]==1);CHECK(green_under[k]==0xabcdef01);CHECK(green_under_owner[k]==2);
   }
  }
  free(canvas->pixels);free(cloud_owner);free(hd_owner);free(green_under_owner);free(green_first);free(green_under);
 }
 printf("PASS: %u assertions; real unchanged production compositor preserves underlying RGBA and owner metadata through exact111/114 holes at2x/8x; normal/shadow and clipped draws; synthetic and actual selected opaque/fractional occupied RGBA blend exactly.\n",checks);return 0;
}
