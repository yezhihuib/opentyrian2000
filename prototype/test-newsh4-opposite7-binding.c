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
enum {ASSET_NEWSH2=101,ASSET_NEWSH4=102,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
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
 if(recorded.slot>=389)for(int i=389;i<396;i++)assert(assets[i].initialized&&assets[i].valid&&assets[i].density==8);
 return true;
}
static unsigned allocation_calls;
static int fail_allocation=-1;
static void *test_malloc(size_t n){unsigned call=allocation_calls++;return (int)call==fail_allocation?NULL:malloc(n);}
#define malloc test_malloc
#include "production-helpers.inc"
#undef malloc
static const unsigned actor_ids[7]={231,233,235,267,269,271,273};
static const unsigned left_ids[7]={153,155,157,159,191,193,195};
static Uint8 terrain_data[601][2];
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));memset(&recorded,0,sizeof(recorded));
 linked31_checked=linked31_valid=false;newsh4_long7_checked=newsh4_long7_valid=false;
#if !BASELINE
 newsh4_opposite7_checked=newsh4_opposite7_valid=false;
#endif
 allocation_calls=0;fail_allocation=-1;game_probe_density=8;game_probe_missing=game_probe_invalid=false;active=true;game_probe_scene_assets=3;reject_reason=NULL;render_mirror_map_begin('Z');
}
static bool actor(unsigned id,int part,int filter){int px=part==1||part==20?12:0,py=part==19||part==20?14:0;return render_mirror_enemy_tile(game_screen,94+px,73+py,enemySpriteSheets[0],id,part,filter,NULL);}
static bool left_member(void){return actor(153,0,0);}
static bool neighbor(void){return render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],153,0,0,NULL);}
static unsigned terrain(unsigned id,int style){Uint8*row[12]={terrain_data[id]};return render_mirror_terrain_row(game_screen,0,37,row,style);}
int main(int argc,char**argv)
{
 assert(argc==4);game_probe_assets=argv[1];Uint8 data[4][2]={{0}};unsigned bank_ids[4]={2,1,9,0};
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
 assert(!BASELINE);
 if(!strcmp(argv[2],"independent")){
  bool right=!!atoi(argv[3]);reset();
  if(right){assert(!left_member());for(int i=0;i<7;i++)assert(actor(actor_ids[i],0,0));}
  else{assert(!actor(231,0,0));for(int i=0;i<7;i++)assert(actor(left_ids[i],0,0));}
  assert(neighbor());reset();puts("PASS independent left/right family fallback");return 0;
 }
 bool present=!!atoi(argv[3]);const int parts[4]={0,1,19,20},xs[4]={0,12,0,12},ys[4]={0,0,14,14};
 for(unsigned bits=0;bits<4;bits++){
  reset();game_probe_scene_assets=(int)bits;
  assert(actor(231,0,0)==(present&&(bits&1)));
  if(!(bits&1))assert(allocation_calls==0);
  game_probe_scene_assets=1;assert(actor(231,0,0)==present);unsigned loaded=allocation_calls;assert(loaded<=7&&(!present||loaded==7));
  for(int n=0;n<32;n++)assert(actor(273,0,0)==present);
  assert(allocation_calls==loaded);
 }
 if(present)for(int failed=0;failed<7;failed++){
  reset();fail_allocation=failed;assert(!actor(231,0,0)&&allocation_calls==7&&!recorded.calls);fail_allocation=-1;
  for(int k=0;k<7;k++)assert(!actor(actor_ids[k],0,0));
  assert(allocation_calls==7);assert(neighbor()&&allocation_calls==8&&recorded.slot==269);assert(left_member()&&allocation_calls==15&&recorded.slot==382);
  reset();assert(actor(273,0,0)&&allocation_calls==7);
 }
 /* Every possible first member must preflight the whole family. */
 for(int first=0;first<7;first++){
  reset();assert(actor(actor_ids[first],0,0)==present);
  for(int k=0;k<7;k++)for(int q=0;q<4;q++)for(int f=0;f<256;f++){
   unsigned n=recorded.calls;assert(actor(actor_ids[k],parts[q],f)==present);
   if(present){Asset*a=&assets[389+k];assert(recorded.calls==n+1&&recorded.slot==389+k&&recorded.x==94&&recorded.y==73&&recorded.style==MIRROR_NORMAL&&recorded.filter==f);assert(recorded.part.x==xs[q]&&recorded.part.y==ys[q]&&recorded.part.w==12&&recorded.part.h==14);assert(a->bank==102&&a->index==(int)actor_ids[k]&&a->w==24&&a->h==28&&a->anchor_x==6&&a->anchor_y==7);}
   else assert(recorded.calls==n);
  }
  for(int mode=0;mode<9;mode++){
   int old_bits=game_probe_scene_assets;const char*old_assets=game_probe_assets;
   if(mode==0)game_probe_missing=true;if(mode==1)game_probe_invalid=true;if(mode==2)game_probe_density=4;if(mode==3)game_probe_density=1;if(mode==4)game_probe_scene_assets=0;if(mode==5)game_probe_scene_assets=2;if(mode==6)active=false;if(mode==7)game_probe_assets=NULL;if(mode==8)reject_reason="test";
   for(int k=0;k<7;k++)assert(!actor(actor_ids[k],0,0));
   game_probe_scene_assets=old_bits;game_probe_assets=old_assets;game_probe_missing=game_probe_invalid=false;game_probe_density=8;active=true;reject_reason=NULL;
  }
  for(int k=0;k<7;k++)assert(!actor(actor_ids[k],2,0)&&!actor(actor_ids[k],-1,0)&&!actor(actor_ids[k],21,0));
  assert(neighbor()&&recorded.slot==269);
  for(unsigned id=0;id<=700;id++){
   bool allowed=false;for(int k=0;k<7;k++)allowed|=id==actor_ids[k];if(!allowed){bool left=false;for(int k=0;k<7;k++)left|=id==left_ids[k];assert(actor(id,0,0)==left);}
  }
  Sprite2_array foreign={data[0]+1,1};assert(!render_mirror_enemy_tile(game_screen,94,73,foreign,231,0,0,NULL));
  SDL_Surface wrong={320};assert(!render_mirror_enemy_tile(&wrong,94,73,enemySpriteSheets[0],231,0,0,NULL));
 }
 if(present){
  reset();assert(actor(231,0,0));Asset*a=&assets[389];unsigned top_left=0,top_right=0,total=0;
  for(int y=0;y<224;y++)for(int x=0;x<192;x++){unsigned opaque=a->rgba[4*(y*192+x)+3]==255;total+=opaque;if(y<112){if(x<96)top_left+=opaque;else top_right+=opaque;}}
  assert(top_left==0&&top_right==2*64&&total==110*64);
  for(int q=0;q<4;q++)assert(actor(231,parts[q],0));
 }
 /* Existing registry capacity is unchanged, no new terrain entries. */
 reset();for(unsigned i=0;i<199;i++)render_mirror_bind_terrain(3,161,terrain_data[i]);assert(terrain_source_count==199);render_mirror_bind_terrain(3,162,terrain_data[200]);assert(terrain_source_count==199);
 for(unsigned i=0;i<256;i++)rgb_palette[i]=(i<<16)|(i<<8)|i;
 for(unsigned f=0;f<256;f++)for(unsigned peak=0;peak<256;peak++){Uint8 src[4]={(Uint8)peak,(Uint8)(peak/2),0,173},out[4];enemy_filter_rgba(src,(Uint8)f,out);unsigned v=(peak*15*256+127)/255,lo=v/256,hi=MIN(15,lo+1),frac=v%256,expected=((f|lo)*(256-frac)+(f|hi)*frac+128)/256;assert(out[0]==expected&&out[1]==expected&&out[2]==expected&&out[3]==173);}
 reset();puts("PASS opposite seven-member preflight, independent left fallback, empty first quadrant, cached coherence, four quadrants/all filters, exact identities, aliases, terrain capacity and unrelated neighbors");return 0;
}
