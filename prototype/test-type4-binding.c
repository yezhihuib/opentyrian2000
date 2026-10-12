/* Private production-function oracle. Never launches the game or a capture. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef uint8_t Uint8;
typedef uint32_t Uint32;
typedef struct { int x,y,w,h; } SDL_Rect;
typedef struct { int unused; } SDL_Surface;
typedef struct { Uint8 *data; size_t size; } Sprite2_array;
typedef struct { int unused; } G101EnemyContext;
typedef struct { int unused; } G101Record;
typedef struct { int unused; } PCapRecord;
typedef struct { int unused; } Forest13Record;
enum { ASSET_NEWSH2=101, ASSET_NEWSHE=110, ASSET_TALON_BANK=109, ASSET_SHAPESZ=201, ASSET_EXPLOSION=106 };
enum { MIRROR_NORMAL=0, MIRROR_BLEND=1, MIRROR_SHADOW=2 };
#include "production-types.inc"
static bool active=true,game_probe_missing,game_probe_invalid;
static int game_probe_density=8,game_probe_scene_assets=1;
static const char *game_probe_assets,*reject_reason;
static SDL_Surface surface_storage,*game_screen=&surface_storage;
static Sprite2_array enemySpriteSheets[4];
static unsigned int enemySpriteSheetIds[4];
static Uint32 rgb_palette[256];
static struct { unsigned calls; int slot,x,y,style,filter; SDL_Rect part; } recorded;
static bool ground101_enemy_eligible(const G101EnemyContext *c,unsigned r,unsigned b)
{ (void)c;(void)r;(void)b;return false; }
static const G101Record *ground101_record(unsigned r,unsigned b)
{ (void)r;(void)b;assert(false);return NULL; }
#define ground101_actor_trace(...) ((void)0)
#define ground101_note_draw(...) ((void)0)
#define game_probe_scene_draw(...) ((void)0)
static bool draw_asset_filtered(int x,int y,Asset *a,int style,const SDL_Rect *part,Uint8 filter,const G101Record *m,const PCapRecord *c,const Forest13Record *f)
{
 assert(a&&a->valid&&part&&!m&&!c&&!f);
 recorded.calls++;recorded.slot=(int)(a-assets);recorded.x=x;recorded.y=y;
 recorded.style=style;recorded.filter=filter;recorded.part=*part;return true;
}
#include "production-helpers.inc"
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));memset(&recorded,0,sizeof(recorded));
 game_probe_density=8;game_probe_missing=false;game_probe_invalid=false;
 active=true;game_probe_scene_assets=1;reject_reason=NULL;
}
static bool draw(unsigned base,int part,int filter)
{
 int px=part==1||part==20?12:0,py=part==19||part==20?14:0;
 return render_mirror_enemy_tile(game_screen,94+px,73+py,enemySpriteSheets[0],base,part,filter,NULL);
}
int main(int argc,char **argv)
{
 assert(argc==4);game_probe_assets=argv[1];
 Uint8 data[4][2]={{0}};unsigned bank_ids[4]={1,9,3,0};
 for(int i=0;i<4;i++){enemySpriteSheets[i]=(Sprite2_array){data[i],2};enemySpriteSheetIds[i]=bank_ids[i];}
 if(!strcmp(argv[2],"trace")) {
  for(int b=0;b<4;b++)for(unsigned id=0;id<=700;id++) {
   recorded.calls=0;
   bool ok=render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[b],id,0,0,NULL);
   if(ok)printf("%u %u %d\n",bank_ids[b],id,recorded.slot);
  }
  reset();return 0;
 }
 assert(!BASELINE);
 unsigned mask=(unsigned)strtoul(argv[3],NULL,0);
 const unsigned ids[5]={159,161,163,165,167};
 const unsigned order[20]={159,159,161,161,163,163,165,165,167,167,165,165,163,163,161,161,159,159,159,159};
 const int parts[4]={0,1,19,20},xs[4]={0,12,0,12},ys[4]={0,0,14,14};
 const int filters[3]={0,9,0x30};
 for(int t=0;t<20;t++)for(int q=0;q<4;q++)for(int f=0;f<3;f++) {
  unsigned k=(order[t]-159)/2,before=recorded.calls;
  bool ok=draw(order[t],parts[q],filters[f]);
  assert(ok==!!(mask&(1u<<k)));
  if(ok) {
   Asset *a=&assets[369+k];
   assert(recorded.calls==before+1&&recorded.slot==(int)(369+k));
   assert(a->bank==101&&a->index==(int)order[t]&&a->w==24&&a->h==28);
   assert(a->anchor_x==6&&a->anchor_y==7&&a->density==8);
   assert(recorded.x==94&&recorded.y==73&&recorded.style==MIRROR_NORMAL);
   assert(recorded.filter==filters[f]);
   assert(recorded.part.x==xs[q]&&recorded.part.y==ys[q]&&recorded.part.w==12&&recorded.part.h==14);
  }else assert(recorded.calls==before);
 }
 for(int k=0;k<5;k++) {
  assert(!draw(ids[k],-1,0)&&!draw(ids[k],2,0)&&!draw(ids[k],21,0));
  for(int b=1;b<4;b++)assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[b],ids[k],0,0,NULL));
 }
 Uint8 foreign[2]={0};Sprite2_array other={foreign,2};
 assert(!render_mirror_enemy_tile(game_screen,94,73,other,159,0,0,NULL));
 assert(!render_mirror_enemy_tile(NULL,94,73,enemySpriteSheets[0],159,0,0,NULL));
 for(unsigned id=158;id<=168;id+=2)assert(!draw(id,0,0));
 /* A missing/corrupt target cannot disable a valid old neighbor. */
 assert(draw(153,0,0)&&recorded.slot==269);
 for(int mode=0;mode<6;mode++) {
  reset();
  if(mode==0)game_probe_missing=true;
  if(mode==1)game_probe_invalid=true;
  if(mode==2)game_probe_density=4; /* No invented4x artwork/fallback. */
  if(mode==3)game_probe_density=1;
  if(mode==4)game_probe_scene_assets=0;
  if(mode==5)active=false;
  for(int k=0;k<5;k++)assert(!draw(ids[k],0,0));
 }
 /* Test the unchanged production palette-filter helper for all byte filters. */
 for(unsigned i=0;i<256;i++)rgb_palette[i]=(i<<16)|(i<<8)|i;
 for(unsigned filter=0;filter<256;filter++)for(unsigned peak=0;peak<256;peak++) {
  Uint8 source[4]={(Uint8)peak,(Uint8)(peak/2),0,173},actual[4];
  enemy_filter_rgba(source,(Uint8)filter,actual);
  unsigned value=(peak*15*256+127)/255,lo=value/256,hi=MIN(15,lo+1),fraction=value%256;
  unsigned expected=((filter|lo)*(256-fraction)+(filter|hi)*fraction+128)/256;
  assert(actual[0]==expected&&actual[1]==expected&&actual[2]==expected&&actual[3]==173);
 }
 reset();puts("PASS five identities,20-step order,four quadrants,anchor,normal/filter path,namespace and independent fallback");
 return 0;
}
