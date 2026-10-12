/* Isolated binding/routing oracle. Production helpers are extracted unchanged.
 * draw_asset is a recorder; this is deliberately not a pixel or gameplay test. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef uint8_t Uint8;
typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int w,h,pitch;void *pixels;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
#define MIN(a,b) ((a)<(b)?(a):(b))
#ifndef BASELINE
#define BASELINE 0
#endif
#include "production-types.inc"
static Uint8 tokens[5];
static Sprite2_array spriteSheet8={tokens,1},spriteSheet9={tokens+1,1},spriteSheet12={tokens+2,1},explosionSpriteSheet={tokens+3,1};
static SDL_Surface screen,other,*game_screen=&screen;
static bool active=true,suppress,suppress_green_smoke,suppress_cloud;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference;
static const char *reject_reason,*game_probe_assets,*full_pack,*work_path;
static int game_probe_density=8;
static Uint32 rgb_palette[256];
static unsigned int banking_draw_player;
static uint64_t mirror_logic_tick;
static TalonBank talon_banks[2];
static const int original_visual_indices[5]={0,2,6,10,12};
static unsigned long long checks,binding_cases,valid_cases,route_cases,fallback_cases,gate_cases,classic_boundary_cases;
#define CHECK(x) do {checks++;if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(3);}}while(0)
static unsigned draw_calls,classic_calls,probe_calls;
static Asset *drawn_asset;
static int drawn_x,drawn_y,drawn_style,classic_x,classic_y,classic_style,classic_layout;
static unsigned classic_index;
static bool probe_mirrored,classic_suppressed;
static const Uint8 *classic_bank;
static bool draw_asset(int x,int y,Asset *a,int style,const SDL_Rect *part);
#include "production-helpers.inc"
static bool draw_asset(int x,int y,Asset *a,int style,const SDL_Rect *part)
{CHECK(!part);draw_calls++;drawn_asset=a;drawn_x=x;drawn_y=y;drawn_style=style;suppress=true;return true;}
static void record_classic(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i,int style,int layout)
{CHECK(s==game_screen);classic_calls++;classic_x=x;classic_y=y;classic_index=i;classic_style=style;classic_layout=layout;classic_bank=b.data;classic_suppressed=suppress||suppress_green_smoke||suppress_cloud;}
#define STUB_BLIT(name,style,layout) static void name(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){record_classic(s,x,y,b,i,style,layout);}
STUB_BLIT(blit_sprite2,ENTITY_NORMAL,ENTITY_TILE)
STUB_BLIT(blit_sprite2_blend,ENTITY_BLEND,ENTITY_TILE)
STUB_BLIT(blit_sprite2_darken,ENTITY_SHADOW,ENTITY_TILE)
STUB_BLIT(blit_sprite2x2,ENTITY_NORMAL,ENTITY_QUAD)
STUB_BLIT(blit_sprite2x2_blend,ENTITY_BLEND,ENTITY_QUAD)
STUB_BLIT(blit_sprite2x2_darken,ENTITY_SHADOW,ENTITY_QUAD)
static void game_probe_draw(int role,unsigned i,int x,int y,int style,int layout,bool mirrored)
{(void)role;(void)i;(void)x;(void)y;(void)style;(void)layout;probe_calls++;probe_mirrored=mirrored;}
#include "production-entity.inc"
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 for(unsigned i=0;i<13;i++)free(talon_frames[i].rgba);
 memset(assets,0,sizeof(assets));memset(talon_frames,0,sizeof(talon_frames));
 memset(talon_banks,0,sizeof(talon_banks));banking_draw_player=0;mirror_logic_tick=0;
 active=true;reject_reason=NULL;game_probe_density=8;game_probe_assets=full_pack;
 game_probe_missing=game_probe_invalid=game_probe_original_reference=false;
 suppress=suppress_green_smoke=suppress_cloud=false;
 draw_calls=classic_calls=probe_calls=0;drawn_asset=NULL;probe_mirrored=classic_suppressed=false;
}
/* An independent enumeration of the accepted finite routes. */
static int expected_slot(int bank,unsigned id,int layout)
{
 if(bank==0&&layout==ENTITY_TILE){
  if(!BASELINE&&id>=31&&id<=33)return 333+(int)id-31;
  if(id>=252&&id<=254)return 330+(int)id-252;
  if(id==59)return 5;if(id==103)return 325;
  const unsigned pulse[]={58,60,62,165},guided[]={19,171,20,21};
  for(int i=0;i<4;i++){if(id==pulse[i])return 321+i;if(id==guided[i])return 326+i;}
  if(id>=214&&id<=217)return 182+(int)id-214;
 }
 if(bank==1&&layout==ENTITY_QUAD&&id>=229&&id<=237&&id%2==1)return ((int)id-229)/2;
 if(bank==3&&layout==ENTITY_TILE){
  const int ranges[][3]={{122,133,31},{3,14,43},{41,52,55},{22,33,67},{60,71,79},{146,152,91},{192,203,98},{154,165,110},{211,222,122},{173,184,134},{135,141,146},{78,84,175}};
  for(unsigned i=0;i<sizeof(ranges)/sizeof(*ranges);i++)if(id>=(unsigned)ranges[i][0]&&id<=(unsigned)ranges[i][1])return ranges[i][2]+(int)id-ranges[i][0];
  const unsigned shield[]={229,230,231,232,233,234,235,236,237,248,249,250,252,253,254,255,256,267,268,269,272,275};
  for(int i=0;i<22;i++)if(id==shield[i])return 153+i;
 }
 return -1;
}
static void finite_bindings(void)
{
 CHECK(sizeof(assets)/sizeof(*assets)==(BASELINE?333:336));
 Sprite2_array banks[]={spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet,{tokens+4,1},{NULL,0}};
 const int layouts[]={ENTITY_TILE,ENTITY_QUAD,-1,2};
 for(int b=0;b<6;b++)for(int l=0;l<4;l++)for(unsigned n=0;n<601;n++){
  unsigned id=n==600?UINT_MAX:n;int layout=layouts[l],expected=expected_slot(b,id,layout);
  reset();game_probe_invalid=true;CHECK(!get_asset(banks[b],id,layout));
  int initialized=0;
  for(unsigned s=0;s<sizeof(assets)/sizeof(*assets);s++)if(assets[s].initialized){
   initialized++;CHECK((int)s==expected);CHECK(!assets[s].valid);CHECK(assets[s].index==(int)id);
   CHECK(assets[s].bank==(b==0?8:b==1?9:ASSET_EXPLOSION));
   CHECK(assets[s].w==(layout==ENTITY_QUAD?24:12));CHECK(assets[s].h==(layout==ENTITY_QUAD?28:14));
   CHECK(assets[s].anchor_x==(b==1?5:b==0&&id==59?-1:0));CHECK(assets[s].anchor_y==(b==1?7:0));
  }
  CHECK(initialized==(expected>=0));binding_cases++;
 }
}
static const unsigned prior_ids[]={252,253,254,19,171,20,21,58,60,62,165,103,59,214,215,216,217};
static void check_metadata(unsigned id,int slot,int density)
{
 Asset *a=get_asset(spriteSheet8,id,ENTITY_TILE);
 CHECK(a==assets+slot);CHECK(a->initialized&&a->valid);CHECK(a->bank==8&&a->index==(int)id);
 CHECK(a->w==12&&a->h==14);CHECK(a->anchor_x==(id==59?-1:0)&&a->anchor_y==0);
 CHECK(a->density==density&&a->rgba);CHECK(get_asset(spriteSheet8,id,ENTITY_TILE)==a);valid_cases++;
}
static void metadata_and_cache(void)
{
 reset();
 for(unsigned i=0;i<sizeof(prior_ids)/sizeof(*prior_ids);i++)check_metadata(prior_ids[i],expected_slot(0,prior_ids[i],ENTITY_TILE),8);
 if(!BASELINE){for(unsigned id=31;id<=33;id++)check_metadata(id,333+(int)id-31,8);for(unsigned id=33;id>=31;id--)check_metadata(id,333+(int)id-31,8);}
 CHECK(assets[330].index==252&&assets[331].index==253&&assets[332].index==254);
 CHECK(assets[329].index==21&&assets[325].index==103&&assets[321].index==58);
 /* Overlapping explosion IDs retain their separate namespace/cache. */
 for(unsigned id=30;id<=34;id++){
  Asset *a=get_asset(explosionSpriteSheet,id,ENTITY_TILE);
  if(id<=33){CHECK(a==assets+67+id-22);CHECK(a->bank==ASSET_EXPLOSION&&a->index==(int)id);CHECK(a->w==12&&a->h==14&&a->anchor_x==0&&a->anchor_y==0);valid_cases++;}
  else CHECK(!a);
 }
}
static bool prior_shadow(unsigned id){return !(id>=252&&id<=254)&&!(id>=214&&id<=217);}
static void check_route(Sprite2_array bank,unsigned id,int style,int layout,bool expected)
{
 reset();bool got=render_mirror_entity(game_screen,7,11,bank,id,style,layout);
 CHECK(got==expected);CHECK(draw_calls==(unsigned)expected);
 CHECK(suppress==expected);CHECK(!suppress_green_smoke&&!suppress_cloud);CHECK(!reject_reason);
 if(expected){CHECK(drawn_asset);CHECK(drawn_x==7&&drawn_y==11&&drawn_style==style);}
 render_mirror_entity_end();CHECK(!suppress&&!suppress_green_smoke&&!suppress_cloud);route_cases++;
}
static void routing(void)
{
 for(unsigned id=30;id<=34;id++)for(int style=0;style<3;style++){
  bool mapped=!BASELINE&&id>=31&&id<=33;
  check_route(spriteSheet8,id,style,ENTITY_TILE,mapped&&style!=MIRROR_SHADOW);
  check_route(spriteSheet8,id,style,ENTITY_QUAD,false);
  check_route(spriteSheet9,id,style,ENTITY_TILE,false);
  check_route(spriteSheet12,id,style,ENTITY_TILE,false);
  check_route(explosionSpriteSheet,id,style,ENTITY_TILE,id<=33);
 }
 for(unsigned i=0;i<sizeof(prior_ids)/sizeof(*prior_ids);i++)for(int style=0;style<3;style++)
  check_route(spriteSheet8,prior_ids[i],style,ENTITY_TILE,style!=MIRROR_SHADOW||prior_shadow(prior_ids[i]));
 for(unsigned id=31;id<=33;id++)for(int gate=0;gate<3;gate++){
  reset();if(gate==0)active=false;if(gate==1)reject_reason="fixture-rejection";
  CHECK(!render_mirror_entity(gate==2?&other:game_screen,7,11,spriteSheet8,id,MIRROR_NORMAL,ENTITY_TILE));
  CHECK(!draw_calls&&!suppress&&!suppress_green_smoke&&!suppress_cloud);gate_cases++;
 }
}
static void original_boundary(void)
{
 for(unsigned id=31;id<=33;id++)for(int style=0;style<3;style++)for(int density=1;density<=8;density+=7){
  reset();game_probe_density=density;bool mirrored=!BASELINE&&density==8&&style!=ENTITY_SHADOW;
  draw_entity_sprite2(game_screen,7,11,spriteSheet8,id,(EntityDrawStyle)style,ENTITY_TILE);
  CHECK(classic_calls==1&&probe_calls==1);CHECK(probe_mirrored==mirrored);CHECK(draw_calls==(unsigned)mirrored);
  CHECK(classic_x==7&&classic_y==11&&classic_index==id&&classic_style==style&&classic_layout==ENTITY_TILE&&classic_bank==spriteSheet8.data);
  CHECK(classic_suppressed==mirrored);CHECK(!suppress&&!suppress_green_smoke&&!suppress_cloud);classic_boundary_cases++;
 }
 /* Previous explicit-shadow exceptions and previous HD shadows stay intact. */
 for(unsigned i=0;i<sizeof(prior_ids)/sizeof(*prior_ids);i++){
  reset();unsigned id=prior_ids[i];bool mirrored=prior_shadow(id);
  draw_entity_sprite2(game_screen,7,11,spriteSheet8,id,ENTITY_SHADOW,ENTITY_TILE);
  CHECK(classic_calls==1&&probe_calls==1&&probe_mirrored==mirrored);CHECK(classic_suppressed==mirrored);
  CHECK(classic_style==ENTITY_SHADOW&&classic_index==id&&classic_x==7&&classic_y==11);
  CHECK(!suppress&&!suppress_green_smoke&&!suppress_cloud);classic_boundary_cases++;
 }
}
static void missing_classic_invalid(void)
{
 if(BASELINE)return;
 char path[1024];
 for(unsigned id=31;id<=33;id++){
  for(int gate=0;gate<3;gate++){
   reset();if(gate==0)game_probe_density=1;if(gate==1)game_probe_missing=true;if(gate==2)game_probe_invalid=true;
   draw_entity_sprite2(game_screen,3,5,spriteSheet8,id,ENTITY_NORMAL,ENTITY_TILE);
   CHECK(classic_calls==1&&probe_calls==1&&!probe_mirrored&&!draw_calls);CHECK(!classic_suppressed&&!suppress&&!suppress_green_smoke&&!suppress_cloud);
   CHECK(assets[333+id-31].initialized==(gate==2));gate_cases++;
  }
  reset();snprintf(path,sizeof(path),"%s/missing-%u",work_path,id);game_probe_assets=path;
  for(unsigned j=31;j<=33;j++){
   Asset *a=get_asset(spriteSheet8,j,ENTITY_TILE);CHECK((a!=NULL)==(j!=id));
   if(a)CHECK(a==assets+333+j-31&&a->valid&&a->density==8);
   else CHECK(assets[333+j-31].initialized&&!assets[333+j-31].valid);
   CHECK(!reject_reason&&!game_probe_missing&&!game_probe_invalid);fallback_cases++;
  }
  reset();snprintf(path,sizeof(path),"%s/density4",work_path);game_probe_assets=path;
  check_metadata(id,333+(int)id-31,4);fallback_cases++;
  reset();snprintf(path,sizeof(path),"%s/invalid-%u",work_path,id);game_probe_assets=path;
  CHECK(!get_asset(spriteSheet8,id,ENTITY_TILE));CHECK(assets[333+id-31].initialized&&!assets[333+id-31].valid);fallback_cases++;
 }
}
int main(int argc,char **argv)
{
 CHECK(argc==3);full_pack=argv[1];work_path=argv[2];
 finite_bindings();metadata_and_cache();routing();original_boundary();missing_classic_invalid();reset();
 printf("{\"status\":\"passed\",\"baseline\":%s,\"assertions\":%llu,\"binding_cases\":%llu,\"valid_metadata_cases\":%llu,\"render_route_cases\":%llu,\"fallback_cases\":%llu,\"guard_cases\":%llu,\"original_boundary_cases\":%llu}\n",BASELINE?"true":"false",checks,binding_cases,valid_cases,route_cases,fallback_cases,gate_cases,classic_boundary_cases);
 return 0;
}
