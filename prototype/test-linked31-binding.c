/* Extracted production loader and both routes. Recorder, not a game capture. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef uint8_t Uint8;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int pitch;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int unused;} G101EnemyContext;
typedef struct {int unused;} G101Record;
typedef struct {int unused;} PCapRecord;
typedef struct {int unused;} Forest13Record;
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
enum {MIRROR_NORMAL=0,MIRROR_BLEND=1,MIRROR_SHADOW=2};
#include "production-types.inc"
static bool active=true,game_probe_missing,game_probe_invalid,suppress,forest_registry_ok=true;
static int game_probe_density=8,game_probe_scene_assets=3;
static const char *game_probe_assets,*reject_reason;
static SDL_Surface surface_storage={320},*game_screen=&surface_storage;
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
 if(recorded.slot>=374)for(int i=374;i<382;i++)assert(assets[i].initialized&&assets[i].valid&&assets[i].density==8);
 return true;
}
static unsigned allocation_calls;
static int fail_allocation=-1;
static void *test_malloc(size_t n){unsigned call=allocation_calls++;return (int)call==fail_allocation?NULL:malloc(n);}
#define malloc test_malloc
#include "production-helpers.inc"
#undef malloc
static const unsigned terrain_ids[4]={161,162,171,172},actor_ids[4]={15,17,53,55};
static Uint8 terrain_data[601][2];
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));memset(&recorded,0,sizeof(recorded));
#if !BASELINE
 linked31_checked=linked31_valid=false;
#endif
 allocation_calls=0;fail_allocation=-1;game_probe_density=8;game_probe_missing=game_probe_invalid=false;active=true;game_probe_scene_assets=3;reject_reason=NULL;render_mirror_map_begin('Z');
}
static bool actor(unsigned id,int part,int filter){int px=part==1||part==20?12:0,py=part==19||part==20?14:0;return render_mirror_enemy_tile(game_screen,94+px,73+py,enemySpriteSheets[0],id,part,filter,NULL);}
static unsigned terrain(unsigned id,int style){Uint8*row[12]={terrain_data[id]};return render_mirror_terrain_row(game_screen,0,37,row,style);}
static void register_family(void){for(int k=0;k<4;k++)render_mirror_bind_terrain(3,terrain_ids[k],terrain_data[terrain_ids[k]]);}
int main(int argc,char**argv)
{
 assert(argc==4);game_probe_assets=argv[1];Uint8 data[4][2]={{0}};unsigned bank_ids[4]={1,9,3,0};
 for(int i=0;i<4;i++){enemySpriteSheets[i]=(Sprite2_array){data[i],2};enemySpriteSheetIds[i]=bank_ids[i];}
 if(!strcmp(argv[2],"trace")){
  for(int b=0;b<4;b++)for(unsigned id=0;id<=700;id++)if(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[b],id,0,0,NULL))printf("a %u %u %d\n",bank_ids[b],id,recorded.slot);
  for(unsigned layer=1;layer<=3;layer++)for(unsigned id=1;id<=600;id++){
   render_mirror_map_begin('Z');render_mirror_bind_terrain(layer,id,terrain_data[id]);
   if(terrain(id,MIRROR_NORMAL))printf("t %u %u %d\n",layer,id,recorded.slot);
  }
  reset();return 0;
 }
 assert(!BASELINE);bool present=!!atoi(argv[3]);const int parts[4]={0,1,19,20},xs[4]={0,12,0,12},ys[4]={0,0,14,14};
 /* Disabled families do not allocate or poison the later valid preflight. */
 for(unsigned bits=0;bits<3;bits++){
  reset();register_family();game_probe_scene_assets=(int)bits;
  assert(!actor(15,0,0)&&!terrain(161,MIRROR_NORMAL)&&allocation_calls==0);
  game_probe_scene_assets=3;assert(actor(15,0,0)==present);unsigned loaded=allocation_calls;assert(loaded<=8&&(!present||loaded==8));
  for(int n=0;n<32;n++)assert(terrain(161,MIRROR_NORMAL)==(unsigned)present);
  assert(allocation_calls==loaded);
 }
 if(present)for(int failed=0;failed<8;failed++){
  reset();register_family();fail_allocation=failed;
  assert(!actor(15,0,0)&&allocation_calls==8&&!recorded.calls);
  fail_allocation=-1;
  for(int k=0;k<4;k++)assert(!actor(actor_ids[k],0,0)&&!terrain(terrain_ids[k],MIRROR_NORMAL));
  assert(allocation_calls==8); /* Failure is cached, no per-frame retry. */
  assert(actor(153,0,0)&&allocation_calls==9); /* Existing neighbor unaffected. */
  reset();register_family();assert(terrain(161,MIRROR_NORMAL)&&actor(15,0,0));
  assert(allocation_calls==8); /* Fresh process/cache can load successfully. */
 }
 for(int first=0;first<2;first++){
  reset();register_family();
  if(first)assert(actor(15,0,0)==present);else assert(terrain(161,MIRROR_NORMAL)==(unsigned)present);
  for(int k=0;k<4;k++){
   unsigned n=recorded.calls;assert(terrain(terrain_ids[k],MIRROR_NORMAL)==(unsigned)present);
   if(present){assert(recorded.calls==n+1&&recorded.slot==374+k&&recorded.x==0&&recorded.y==37&&!recorded.part_present);Asset*a=&assets[374+k];assert(a->bank==201&&a->index==(int)terrain_ids[k]&&a->w==24&&a->h==28&&!a->anchor_x&&!a->anchor_y);}
   else assert(recorded.calls==n);
   for(int q=0;q<4;q++)for(int f=0;f<256;f++){
    n=recorded.calls;assert(actor(actor_ids[k],parts[q],f)==present);
    if(present){Asset*a=&assets[378+k];assert(recorded.calls==n+1&&recorded.slot==378+k&&recorded.x==94&&recorded.y==73&&recorded.style==MIRROR_NORMAL&&recorded.filter==f);assert(recorded.part.x==xs[q]&&recorded.part.y==ys[q]&&recorded.part.w==12&&recorded.part.h==14);assert(a->bank==101&&a->index==(int)actor_ids[k]&&a->w==24&&a->h==28&&a->anchor_x==6&&a->anchor_y==7);}
    else assert(recorded.calls==n);
   }
  }
  /* Cached success/failure still honors explicit runtime guards. */
  for(int mode=0;mode<9;mode++){
   int old_bits=game_probe_scene_assets;const char*old_assets=game_probe_assets;
   if(mode==0)game_probe_missing=true;if(mode==1)game_probe_invalid=true;if(mode==2)game_probe_density=4;if(mode==3)game_probe_density=1;if(mode==4)game_probe_scene_assets=1;if(mode==5)game_probe_scene_assets=2;if(mode==6)active=false;if(mode==7)game_probe_assets=NULL;if(mode==8)reject_reason="test";
   for(int k=0;k<4;k++)assert(!actor(actor_ids[k],0,0)&&!terrain(terrain_ids[k],MIRROR_NORMAL));
   game_probe_scene_assets=old_bits;game_probe_assets=old_assets;game_probe_missing=game_probe_invalid=false;game_probe_density=8;active=true;reject_reason=NULL;
  }
  for(int k=0;k<4;k++){
   assert(!actor(actor_ids[k],2,0)&&!actor(actor_ids[k],-1,0)&&!actor(actor_ids[k],21,0));
   assert(!terrain(terrain_ids[k],MIRROR_BLEND)&&!terrain(terrain_ids[k],MIRROR_SHADOW));
   for(int b=1;b<4;b++)assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[b],actor_ids[k],0,0,NULL));
  }
  /* Neighboring preexisting actors and terrain remain independent. */
  assert(actor(153,0,0)&&recorded.slot==269);render_mirror_bind_terrain(3,132,terrain_data[132]);assert(terrain(132,MIRROR_NORMAL)&&recorded.slot==278);
 }
 for(int k=0;k<4;k++)for(unsigned layer=1;layer<=3;layer++){
  reset();render_mirror_bind_terrain(layer,terrain_ids[k],terrain_data[terrain_ids[k]]);assert(terrain_source_count==(unsigned)(layer==3));
 }
 reset();render_mirror_map_begin('x');register_family();assert(!terrain_source_count);
 reset();register_family();Uint8 foreign[2]={0};Uint8*row[12]={foreign};assert(!render_mirror_terrain_row(game_screen,0,0,row,MIRROR_NORMAL));
 /* Boundary capacity remains checked, with all199 registered source pointers. */
 reset();for(unsigned i=0;i<199;i++)render_mirror_bind_terrain(3,161,terrain_data[i]);assert(terrain_source_count==199);render_mirror_bind_terrain(3,162,terrain_data[200]);assert(terrain_source_count==199);
 for(unsigned i=0;i<256;i++)rgb_palette[i]=(i<<16)|(i<<8)|i;
 for(unsigned f=0;f<256;f++)for(unsigned peak=0;peak<256;peak++){Uint8 src[4]={(Uint8)peak,(Uint8)(peak/2),0,173},out[4];enemy_filter_rgba(src,(Uint8)f,out);unsigned v=(peak*15*256+127)/255,lo=v/256,hi=MIN(15,lo+1),frac=v%256,expected=((f|lo)*(256-frac)+(f|hi)*frac+128)/256;assert(out[0]==expected&&out[1]==expected&&out[2]==expected&&out[3]==173);}
 reset();puts("PASS both routes, preflight-before-first-draw, cached coherence, four quadrants/all filters, source identities and unrelated neighbors");return 0;
}
