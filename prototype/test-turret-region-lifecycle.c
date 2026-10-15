/* Actual production helpers, synthetic assets, independent rectangle/pixel
 * expectations. This is a unit fixture, not a natural gameplay witness. */
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
typedef struct {int unused;} G101Record,PCapRecord,Forest13Record;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106,
      ASSET_CASH25_VALUE=113,ASSET_CASH75_VALUE=115,ASSET_CASH50_VALUE=117,
      ASSET_GEM100_VALUE=119,ASSET_GEM250_VALUE=121};
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#include "types.inc"
static SDL_Surface screen,display,*game_screen=&screen,*canvas=&display;
static bool active=true,suppress,suppress_cloud,suppress_green_smoke;
static bool game_probe_original_reference,game_probe_local_blend=true,game_probe_known_blend=true;
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value;
static int game_probe_density;
static const char *reject_reason;
static Uint32 rgb_palette[256];
static Uint8 expected[64000],selected[64000],restored_mask[64000];
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static GreenHead green_heads[256];
static HdRegion regions[32];
static unsigned region_count,green_head_count,local_entities,draws,occlusions;
static unsigned local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
static unsigned long long checks;
static bool expect_stale;
static unsigned restore_calls,last_groups,last_blocks;
static SDL_Rect last_requested,last_restored;
#define CHECK(x) do {checks++;if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(3);}}while(0)
#define ground101_select(...) assert(0)
#define plateau_cap_select(...) assert(0)
#define forest13_select(...) assert(0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
static void render_mirror_shadow_end(void) {}
static void vulcan_shadow_clear(void) {}
static bool vulcan_shadow_pixel(SDL_Surface *s,int x,int y,Uint8 b,Uint8 a,int style)
{(void)s;(void)x;(void)y;(void)b;(void)a;(void)style;return false;}
static bool font_pixel(int x,int y,Uint8 a,int style)
{(void)x;(void)y;(void)a;(void)style;return false;}
static void font_before_effect(SDL_Rect r) {CHECK(r.w>0&&r.h>0);}
static void render_mirror_unsupported(const char *reason) {reject_reason=reason;}
static void game_probe_restore_region(unsigned source,SDL_Rect requested,SDL_Rect restored,unsigned groups,unsigned blocks)
{(void)source;restore_calls++;last_requested=requested;last_restored=restored;last_groups=groups;last_blocks=blocks;}
static Uint32 palette_rgb(Uint8 index);
#include "functions.inc"

static const int ids[4]={77,79,115,117};
static const int ox[4]={0,24,0,24},oy[4]={0,0,28,28};
static Uint8 rgba[24*28*4],other_rgba[4*4*4];
static Asset parts[4],other;
static bool same_rect(SDL_Rect a,SDL_Rect b)
{return a.x==b.x&&a.y==b.y&&a.w==b.w&&a.h==b.h;}
static Uint32 pixel(int x,int y)
{return *((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x);}
static unsigned owner(int x,int y)
{return hd_owner[(size_t)y*canvas->w+x];}
static void reset(void)
{
 region_count=green_head_count=local_entities=draws=occlusions=0;
 local_regions=local_blocks=expanded_regions=boundary_crossings=restore_calls=0;
 reject_reason=NULL;render_mirror_entity_end();game_probe_known_blend=true;
 memset(selected,0,sizeof(selected));memset(restored_mask,0,sizeof(restored_mask));
 memset(screen.pixels,52,(size_t)screen.pitch*screen.h);memset(expected,52,sizeof(expected));
 memset(canvas->pixels,0xcd,(size_t)canvas->pitch*canvas->h);
 size_t n=(size_t)canvas->w*canvas->h;
 memset(hd_owner,0,n);memset(cloud_owner,0,n);memset(green_first,0,n*sizeof(*green_first));
 memset(green_under_owner,0,n);memset(green_under,0,n*sizeof(*green_under));
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++)
  *((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x)=palette_rgb(52);
}
static void draw(int x,int y,Asset *a)
{
 CHECK(draw_asset(x,y,a,MIRROR_NORMAL,NULL));
 /* Stand in for an opaque indexed blit, preserving the production callback's
  * real suppression and command-end behavior. No RLE/gameplay is exercised. */
 for(int yy=y;yy<y+a->h;yy++)for(int xx=x;xx<x+a->w;xx++) {
  Uint8 *p=(Uint8 *)screen.pixels+yy*screen.pitch+xx;
  *p=(Uint8)a->index;render_mirror_pixel(&screen,p,*p,MIRROR_NORMAL);
 }
 render_mirror_entity_end();CHECK(!reject_reason);
}
static void group_draw(unsigned mask)
{for(int k=0;k<4;k++)if(mask&(1u<<k))draw(40+ox[k],30+oy[k],parts+k);}
static void blend(int x,int y)
{
 Uint8 *p=(Uint8 *)screen.pixels+y*screen.pitch+x;
 *p=99;render_mirror_pixel(&screen,p,99,MIRROR_BLEND);CHECK(!reject_reason);
}
static void assert_classic(SDL_Rect r)
{
 int d=game_probe_density;
 for(int y=r.y;y<r.y+r.h;y++)for(int x=r.x;x<r.x+r.w;x++) {
  Uint8 index=((Uint8 *)screen.pixels)[y*screen.pitch+x];
  Uint32 color=UINT32_C(0xff000000)|(rgb_palette[index]&UINT32_C(0x00ffffff));
  CHECK(restored_mask[y*320+x]&&!selected[y*320+x]);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
   CHECK(pixel(x*d+sx,y*d+sy)==color);
   CHECK(!hd_owner[n]&&!cloud_owner[n]&&!green_first[n]);
  }
 }
}
static void all_live(void)
{
 reset();group_draw(15);CHECK(region_count==4);
 for(int k=0;k<4;k++) {SDL_Rect r;CHECK(complete_turret_group(k,&r));CHECK(same_rect(r,(SDL_Rect){40,30,48,56}));}
 blend(41,31);CHECK(restore_calls==1&&last_groups==1&&last_blocks==48*56);
 CHECK(same_rect(last_requested,(SDL_Rect){40,30,24,28}));
 CHECK(same_rect(last_restored,(SDL_Rect){40,30,48,56}));
 for(int k=0;k<4;k++)CHECK(!regions[k].live);
 assert_classic((SDL_Rect){40,30,48,56});
 printf("all-live d=%d restore=40,30,48,56 groups=1 blocks=2688\n",game_probe_density);
 /* All-dead records cannot start another region closure, even on a blend. */
 unsigned previous=restore_calls;blend(65,59);CHECK(restore_calls==previous);
 restore_classic_rect((SDL_Rect){42,32,1,1});
 CHECK(same_rect(last_restored,(SDL_Rect){42,32,1,1})&&last_groups==0&&last_blocks==0);
 printf("all-dead d=%d restore=42,32,1,1 groups=0 blocks=0\n",game_probe_density);
}
static void partial_redraw(unsigned mask)
{
 reset();group_draw(15);blend(41,31);
 for(int k=0;k<4;k++)CHECK(!regions[k].live);
 memset(restored_mask,0,sizeof(restored_mask));restore_calls=local_blocks=expanded_regions=0;
 int anchor=0,missing=3;
 while(!(mask&(1u<<anchor)))anchor++;
 if(mask!=15){missing=0;while(mask&(1u<<missing))missing++;}
 int other_x=44+ox[missing],other_y=34+oy[missing];
 /* A separate HD object lies in a missing old member, away from every live
  * redraw. Stale grouping must not erase it. Full redraw covers it normally. */
 draw(other_x,other_y,&other);group_draw(mask);
 unsigned previous_count=region_count;
 blend(41+ox[anchor],31+oy[anchor]);CHECK(region_count==previous_count&&restore_calls==1);
 SDL_Rect want=expect_stale||mask==15?(SDL_Rect){40,30,48,56}:
   (SDL_Rect){40+ox[anchor],30+oy[anchor],24,28};
 /* Mere edge/corner touching does not close over other live members. */
 CHECK(same_rect(last_restored,want));
 CHECK(last_groups==(unsigned)(expect_stale||mask==15));
 if(expect_stale||mask==15) {
  CHECK(!regions[4].live&&owner(other_x*game_probe_density,other_y*game_probe_density)==0);
  assert_classic(want);
 } else {
  CHECK(last_blocks==24*28);
  CHECK(regions[4].live&&owner(other_x*game_probe_density,other_y*game_probe_density)==1);
  CHECK(pixel(other_x*game_probe_density,other_y*game_probe_density)==UINT32_C(0xff11cc88));
  CHECK(!restored_mask[other_y*320+other_x]);assert_classic(want);
  for(int k=0;k<4;k++)if(k!=anchor&&(mask&(1u<<k)))
   CHECK(owner((41+ox[k])*game_probe_density,(31+oy[k])*game_probe_density)==1);
 }
 printf("redraw-mask%u d=%d restore=%d,%d,%d,%d groups=%u blocks=%u unrelated-live=%d\n",
  mask,game_probe_density,want.x,want.y,want.w,want.h,last_groups,last_blocks,regions[4].live);
}
static void predicate_controls(void)
{
 for(unsigned mask=1;mask<16;mask++) {
  reset();group_draw(15);
  for(int k=0;k<4;k++)regions[k].live=(mask&(1u<<k))!=0;
  for(unsigned k=0;k<4;k++)if(regions[k].live) {
   SDL_Rect r;CHECK(complete_turret_group(k,&r)==(expect_stale||mask==15));
  }
 }
 for(int k=0;k<4;k++)for(int property=0;property<5;property++) {
  reset();group_draw(15);
  if(property==0)regions[k].bank++;
  if(property==1)regions[k].style=MIRROR_SHADOW;
  if(property==2)regions[k].index++;
  if(property==3)regions[k].rect.x++;
  if(property==4)regions[k].rect.y++;
  for(unsigned j=0;j<4;j++){SDL_Rect r;CHECK(!complete_turret_group(j,&r));}
 }
 /* Record order, dead duplicates and live replacements must not hide a new
  * complete group. Requiring all matching records live would be too strict. */
 reset();group_draw(15);blend(41,31);
 for(int k=3;k>=0;k--)draw(40+ox[k],30+oy[k],parts+k);
 CHECK(region_count==8);
 for(unsigned k=4;k<8;k++){SDL_Rect r;CHECK(complete_turret_group(k,&r));}
 blend(41,31);CHECK(same_rect(last_restored,(SDL_Rect){40,30,48,56}));
 /* The known-blend option remains the only group-closure gate. */
 reset();group_draw(15);game_probe_known_blend=false;blend(41,31);
 CHECK(same_rect(last_restored,(SDL_Rect){40,30,24,28})&&last_groups==0);
 CHECK(!regions[0].live&&regions[1].live&&regions[2].live&&regions[3].live);
 printf("predicate-controls d=%d live-masks=15 wrong-properties=20 reversed-redraw=pass known-blend-off=pass\n",game_probe_density);
}
static void padding(void)
{
 for(int y=0;y<screen.h;y++)for(int x=320;x<screen.pitch;x++)CHECK(((Uint8 *)screen.pixels)[y*screen.pitch+x]==52);
 for(int y=0;y<canvas->h;y++)for(int x=canvas->w*4;x<canvas->pitch;x++)CHECK(((Uint8 *)canvas->pixels)[y*canvas->pitch+x]==0xcd);
}
int main(int argc,char **argv)
{
 CHECK(argc==2);expect_stale=atoi(argv[1])!=0;
 for(unsigned i=0;i<256;i++)rgb_palette[i]=(i<<16)|((i*3%256)<<8)|(i*7%256);
 for(unsigned i=0;i<24*28;i++){rgba[4*i]=180;rgba[4*i+1]=80;rgba[4*i+2]=35;rgba[4*i+3]=255;}
 for(unsigned i=0;i<4*4;i++){other_rgba[4*i]=17;other_rgba[4*i+1]=204;other_rgba[4*i+2]=136;other_rgba[4*i+3]=255;}
 for(int k=0;k<4;k++)parts[k]=(Asset){true,true,ASSET_NEWSH2,ids[k],24,28,0,0,1,rgba};
 other=(Asset){true,true,8,999,4,4,0,0,1,other_rgba};
 screen=(SDL_Surface){320,200,328,NULL};screen.pixels=malloc((size_t)screen.pitch*screen.h);CHECK(screen.pixels);
 for(int d=2;d<=8;d*=2) {
  game_probe_density=d;display=(SDL_Surface){320*d,200*d,320*d*4+20,NULL};
  size_t n=(size_t)display.w*display.h;display.pixels=malloc((size_t)display.pitch*display.h);
  hd_owner=malloc(n);cloud_owner=malloc(n);green_first=malloc(n*sizeof(*green_first));
  green_under=malloc(n*sizeof(*green_under));green_under_owner=malloc(n);
  CHECK(display.pixels&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);
  all_live();for(unsigned mask=1;mask<16;mask++)partial_redraw(mask);predicate_controls();padding();
  free(display.pixels);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 }
 free(screen.pixels);
 printf("PASS turret lifecycle: %llu checks; expected-stale=%d; synthetic units only.\n",checks,expect_stale);
 return 0;
}
