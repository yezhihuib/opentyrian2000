/* Extracted production loader and both routes. Recorder, not a game capture. */
#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int pitch,w,h;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int unused;} G101EnemyContext;
typedef struct {int unused;} G101Record;
typedef struct {int unused;} PCapRecord;
typedef struct {int unused;} Forest13Record;
enum {ASSET_NEWSH2=101,ASSET_NEWSH4=102,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
enum {MIRROR_NORMAL=0,MIRROR_BLEND=1,MIRROR_SHADOW=2};
#include "production-types.inc"
static bool active=true,game_probe_missing,game_probe_invalid,suppress,forest_registry_ok=true;
static int game_probe_density=8,game_probe_scene_assets=3;
static const char *game_probe_assets,*reject_reason;
static SDL_PixelFormat pixel_format={8,1};
static SDL_Surface surface_storage={320,320,200,&pixel_format},*game_screen=&surface_storage;
static Sprite2_array enemySpriteSheets[4];static unsigned enemySpriteSheetIds[4];
static Uint32 rgb_palette[256];static unsigned terrain_source_count;static char terrain_file;
static struct {unsigned calls;int slot,x,y,style,filter;bool part_present;SDL_Rect part;} recorded;
static bool ground101_enemy_eligible(const G101EnemyContext*c,unsigned r,unsigned b){(void)c;(void)r;(void)b;return false;}
static const G101Record *ground101_record(unsigned r,unsigned b){(void)r;(void)b;return NULL;}
static const PCapRecord *plateau_cap_record(unsigned b){(void)b;return NULL;}
static const Forest13Record *forest13_record(unsigned b){(void)b;return NULL;}
static bool forest13_declared(void){return false;}
static int ground101_layer1_row(Uint8 **m,int x,int y){(void)m;(void)x;(void)y;return 0;}
#define ground101_actor_trace(...) ((void)0)
#define ground101_note_draw(...) ((void)0)
#define ground101_frame_reset(...) ((void)0)
#define render_mirror_reset_banking(...) ((void)0)
#define game_probe_scene_draw(...) ((void)0)
#define font_before_effect(...) ((void)0)
#define render_mirror_unsupported(...) ((void)0)
static bool draw_asset_filtered(int x,int y,Asset*a,int style,const SDL_Rect*part,Uint8 filter,const G101Record*m,const PCapRecord*c,const Forest13Record*f)
{
 assert(a&&a->valid&&!m&&!c&&!f);recorded.calls++;recorded.slot=(int)(a-assets);recorded.x=x;recorded.y=y;recorded.style=style;recorded.filter=filter;recorded.part_present=!!part;if(part)recorded.part=*part;
 /* Every member has been loaded before the very first route draws anything. */
 if(recorded.slot>=404)for(int i=404;i<410;i++)assert(assets[i].initialized&&assets[i].valid&&assets[i].density==8);
 return true;
}
static unsigned allocation_calls;
static int fail_allocation=-1;
static void *test_malloc(size_t n){unsigned call=allocation_calls++;return (int)call==fail_allocation?NULL:malloc(n);}
#define malloc test_malloc
#include "production-helpers.inc"
#undef malloc
static const unsigned actor_ids[6]={1,3,5,7,9,11};
static Uint8 terrain_data[601][2];
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));memset(&recorded,0,sizeof(recorded));
 linked31_checked=linked31_valid=false;newsh4_long7_checked=newsh4_long7_valid=false;newsh4_opposite7_checked=newsh4_opposite7_valid=false;
type15_eightheading_checked=type15_eightheading_valid=false;
#if !BASELINE
 late_spike_checked=late_spike_valid=false;
#endif
 surface_storage=(SDL_Surface){320,320,200,&pixel_format};pixel_format=(SDL_PixelFormat){8,1};
 allocation_calls=0;fail_allocation=-1;game_probe_density=8;game_probe_missing=game_probe_invalid=false;active=true;game_probe_scene_assets=3;reject_reason=NULL;render_mirror_map_begin('Z');
}
static bool actor(unsigned id,int part,int filter){int px=part==1||part==20?12:0,py=part==19||part==20?14:0;return render_mirror_enemy_tile(game_screen,94+px,73+py,enemySpriteSheets[0],id,part,filter,NULL);}
static bool neighbor(void){return render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],153,0,0,NULL);}
static unsigned terrain(unsigned id,int style){Uint8*row[12]={terrain_data[id]};return render_mirror_terrain_row(game_screen,0,37,row,style);}
int main(int argc,char**argv)
{
 assert(argc==4);game_probe_assets=argv[1];Uint8 data[4][2]={{0}};unsigned bank_ids[4]={1,2,9,0};
 for(int i=0;i<4;i++){enemySpriteSheets[i]=(Sprite2_array){data[i],2};enemySpriteSheetIds[i]=bank_ids[i];}
 if(!strcmp(argv[2],"trace")){
  /* All sheet identities, not just the new bank; bank3 is also checked. */
  for(unsigned bank_id=0;bank_id<=36;bank_id++) {
   enemySpriteSheetIds[3]=bank_id;
   for(unsigned id=0;id<=700;id++)if(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[3],id,0,0,NULL))printf("a %u %u %d\n",bank_id,id,recorded.slot);
  }
  for(unsigned layer=1;layer<=3;layer++)for(unsigned id=1;id<=600;id++){
   render_mirror_map_begin('Z');render_mirror_bind_terrain(layer,id,terrain_data[id]);
   if(terrain(id,MIRROR_NORMAL))printf("t %u %u %d\n",layer,id,recorded.slot);
  }
  reset();return 0;
 }
 if(!strcmp(argv[2],"independent")){
  assert(!BASELINE);reset();
  const unsigned older[13]={39,41,43,45,91,93,129,131,15,17,53,55,153};
  for(int k=0;k<13;k++)render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],older[k],0,0,NULL);
  const unsigned bank2[14]={153,155,157,159,191,193,195,231,233,235,267,269,271,273};
  for(int k=0;k<14;k++)render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],bank2[k],0,0,NULL);
  for(int k=0;k<6;k++)assert(actor(actor_ids[k],0,0)&&recorded.slot==404+k);
  reset();puts("PASS neighboring missing/corrupt resources do not disable late six");return 0;
 }
 assert(!BASELINE);bool present=!!atoi(argv[3]);const int parts[4]={0,1,19,20},xs[4]={0,12,0,12},ys[4]={0,0,14,14};
 for(unsigned bits=0;bits<4;bits++){
  reset();game_probe_scene_assets=(int)bits;
  assert(actor(1,0,0)==(present&&(bits&1)));
  if(!(bits&1))assert(allocation_calls==0);
  game_probe_scene_assets=1;assert(actor(1,0,0)==present);unsigned loaded=allocation_calls;assert(loaded<=6&&(!present||loaded==6));
  for(int n=0;n<32;n++)assert(actor(11,0,0)==present);
  assert(allocation_calls==loaded);
 }
 if(present)for(int failed=0;failed<6;failed++){
  reset();fail_allocation=failed;assert(!actor(1,0,0)&&allocation_calls==6&&!recorded.calls);fail_allocation=-1;
  for(int k=0;k<6;k++)assert(!actor(actor_ids[k],0,0));
  assert(allocation_calls==6);assert(neighbor()&&allocation_calls==7&&recorded.slot==269);
  reset();assert(actor(11,0,0)&&allocation_calls==6);
 }
 /* Every possible first member must preflight the whole family. */
 for(int first=0;first<6;first++){
  reset();assert(actor(actor_ids[first],0,0)==present);
  for(int k=0;k<6;k++)for(int q=0;q<4;q++)for(int f=0;f<256;f++){
   unsigned n=recorded.calls;assert(actor(actor_ids[k],parts[q],f)==present);
   if(present){Asset*a=&assets[404+k];assert(recorded.calls==n+1&&recorded.slot==404+k&&recorded.x==94&&recorded.y==73&&recorded.style==MIRROR_NORMAL&&recorded.filter==f);assert(recorded.part.x==xs[q]&&recorded.part.y==ys[q]&&recorded.part.w==12&&recorded.part.h==14);assert(a->bank==101&&a->index==(int)actor_ids[k]&&a->w==24&&a->h==28&&a->anchor_x==6&&a->anchor_y==7);}
   else assert(recorded.calls==n);
  }
  for(int mode=0;mode<9;mode++){
   int old_bits=game_probe_scene_assets;const char*old_assets=game_probe_assets;
   if(mode==0)game_probe_missing=true;if(mode==1)game_probe_invalid=true;if(mode==2)game_probe_density=4;if(mode==3)game_probe_density=1;if(mode==4)game_probe_scene_assets=0;if(mode==5)game_probe_scene_assets=2;if(mode==6)active=false;if(mode==7)game_probe_assets=NULL;if(mode==8)reject_reason="test";
   for(int k=0;k<6;k++)assert(!actor(actor_ids[k],0,0));
   game_probe_scene_assets=old_bits;game_probe_assets=old_assets;game_probe_missing=game_probe_invalid=false;game_probe_density=8;active=true;reject_reason=NULL;
  }
  for(int k=0;k<6;k++)assert(!actor(actor_ids[k],2,0)&&!actor(actor_ids[k],-1,0)&&!actor(actor_ids[k],21,0));
  assert(neighbor()&&recorded.slot==269);
  /* Existing numeric aliases and both bank2 families remain independently live. */
  for(int k=0;k<6;k++)assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[2],actor_ids[k],0,0,NULL)&&recorded.slot==(k<3?253+k:256+k));
  const unsigned prior15[8]={39,41,43,45,91,93,129,131};
  for(int k=0;k<8;k++)assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],prior15[k],0,0,NULL)&&recorded.slot==396+k);
  const unsigned linked[4]={15,17,53,55};
  for(int k=0;k<4;k++)assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],linked[k],0,0,NULL)&&recorded.slot==378+k);
  const unsigned bank2[14]={153,155,157,159,191,193,195,231,233,235,267,269,271,273};
  for(int k=0;k<14;k++)assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],bank2[k],0,0,NULL)&&recorded.slot==382+k);
  for(int k=0;k<6;k++)assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],actor_ids[k],0,0,NULL));
  Sprite2_array foreign={data[0]+1,1};assert(!render_mirror_enemy_tile(game_screen,94,73,foreign,1,0,0,NULL));
  SDL_Surface wrong={320,320,200,&pixel_format};assert(!render_mirror_enemy_tile(&wrong,94,73,enemySpriteSheets[0],1,0,0,NULL));
 }
 /* Physical-row geometry fallback is per call, distinct from the all-six
  * asset gate. Never wrap HD art or suppress the original wrapped RLE write. */
 if(present) {
  const int pitches[]={INT_MIN,-1,0,11,12,319,320,321,INT_MAX};
  const int boundary_ys[]={-214,-28,-14,-1,0,1,185,199,200,214};
  for(unsigned p=0;p<sizeof(pitches)/sizeof(*pitches);p++) {
   reset();game_screen->pitch=pitches[p];
   const int boundary_xs[]={INT_MIN,-321,-34,-33,-13,-12,-1,0,1,11,12,24,286,287,288,307,308,309,319,320,321,INT_MAX};
   for(int k=0;k<6;k++)for(int q=0;q<4;q++)for(int f=0;f<256;f++)
    for(unsigned xi=0;xi<sizeof(boundary_xs)/sizeof(*boundary_xs);xi++)for(unsigned yi=0;yi<sizeof(boundary_ys)/sizeof(*boundary_ys);yi++) {
     int x=boundary_xs[xi],y=boundary_ys[yi];unsigned before=recorded.calls;
     bool safe=pitches[p]==320&&x>=0&&x<=308;
     bool result=render_mirror_enemy_tile(game_screen,x,y,enemySpriteSheets[0],actor_ids[k],parts[q],f,NULL);
     assert(result==safe&&recorded.calls==before+(unsigned)safe);
     if(safe)assert(recorded.slot==404+k&&recorded.x==x-xs[q]&&recorded.y==y-ys[q]&&recorded.filter==f);
    }
   /* A geometric miss must never poison valid six-member resources. */
   game_screen->pitch=320;assert(actor(7,0,0)&&recorded.slot==407);
  }
  /* Unsupported indexed layout fails closed only for this six-ID family. */
  for(int mode=0;mode<9;mode++) {
   reset();
   if(mode==0)game_screen->w=319;if(mode==1)game_screen->w=321;
   if(mode==2)game_screen->h=199;if(mode==3)game_screen->h=201;
   if(mode==4)pixel_format.BitsPerPixel=0;if(mode==5)pixel_format.BitsPerPixel=32;
   if(mode==6)game_screen->format=NULL;if(mode==7)pixel_format.BytesPerPixel=0;if(mode==8)pixel_format.BytesPerPixel=4;
   for(int k=0;k<6;k++)for(int q=0;q<4;q++)for(int f=0;f<256;f++) {
    unsigned before=recorded.calls;assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],actor_ids[k],parts[q],f,NULL)&&recorded.calls==before);
   }
   assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],39,0,0,NULL)&&recorded.slot==396);
  }
  reset();
  /* Extreme x must return before x-part/y-part arithmetic, including corners. */
  for(int k=0;k<6;k++)for(int q=0;q<4;q++)for(int f=0;f<256;f++) {
   assert(!render_mirror_enemy_tile(game_screen,INT_MIN,INT_MIN,enemySpriteSheets[0],actor_ids[k],parts[q],f,NULL));
   assert(!render_mirror_enemy_tile(game_screen,INT_MAX,INT_MAX,enemySpriteSheets[0],actor_ids[k],parts[q],f,NULL));
  }
  /* Safe neighbor quadrants remain HD even when one quadrant is classic. */
  assert(!render_mirror_enemy_tile(game_screen,-1,50,enemySpriteSheets[0],1,0,0,NULL));
  assert(render_mirror_enemy_tile(game_screen,11,50,enemySpriteSheets[0],1,1,0,NULL));
  assert(render_mirror_enemy_tile(game_screen,308,50,enemySpriteSheets[0],1,0,0,NULL));
  assert(!render_mirror_enemy_tile(game_screen,320,50,enemySpriteSheets[0],1,1,0,NULL));
  const int edge_xs[]={-34,-1,0,308,309,320};
  for(unsigned q=0;q<sizeof(edge_xs)/sizeof(*edge_xs);q++) {
   int x=edge_xs[q];
   assert(render_mirror_enemy_tile(game_screen,x,50,enemySpriteSheets[0],39,0,0,NULL)&&recorded.slot==396);
   assert(render_mirror_enemy_tile(game_screen,x,50,enemySpriteSheets[0],15,0,0,NULL)&&recorded.slot==378);
   assert(render_mirror_enemy_tile(game_screen,x,50,enemySpriteSheets[1],231,0,0,NULL)&&recorded.slot==389);
   assert(render_mirror_enemy_tile(game_screen,x,50,enemySpriteSheets[2],1,0,0,NULL)&&recorded.slot==253);
  }
 }
 /* Existing registry capacity is unchanged, no new terrain entries. */
 reset();for(unsigned i=0;i<199;i++)render_mirror_bind_terrain(3,161,terrain_data[i]);assert(terrain_source_count==199);render_mirror_bind_terrain(3,162,terrain_data[200]);assert(terrain_source_count==199);
 for(unsigned i=0;i<256;i++)rgb_palette[i]=(i<<16)|(i<<8)|i;
 for(unsigned f=0;f<256;f++)for(unsigned peak=0;peak<256;peak++){Uint8 src[4]={(Uint8)peak,(Uint8)(peak/2),0,173},out[4];enemy_filter_rgba(src,(Uint8)f,out);unsigned v=(peak*15*256+127)/255,lo=v/256,hi=MIN(15,lo+1),frac=v%256,expected=((f|lo)*(256-frac)+(f|hi)*frac+128)/256;assert(out[0]==expected&&out[1]==expected&&out[2]==expected&&out[3]==173);}
 reset();puts("PASS six-member preflight including naturally hidden caps, cached coherence, four quadrants/all filters, exact identities, aliases, terrain capacity and prior type15, linked31 and both bank2 families");return 0;
}
