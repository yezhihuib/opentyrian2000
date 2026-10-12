#include "plateau_cap_material.h"
#include "ground101_bundle_index.h"
#include "plateau_cap_bundle_index.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;typedef Uint8 JE_byte;
typedef struct {int pitch;} SDL_Surface;
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
enum {ASSET_SHAPESZ=201,MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
static bool active=true,suppress,game_probe_missing,game_probe_invalid,game_probe_original_reference;
static unsigned game_probe_scene_assets=3;static int game_probe_density=8;
static const char *reject_reason,*game_probe_assets="selected";
static char terrain_file='z';static SDL_Surface screen={320},other={320},*game_screen=&screen;
static struct {Uint8 *mainmap[300][14];} megaData1;
static struct {const Uint8 *data;unsigned id;} terrain_sources[162];static unsigned terrain_source_count;
static Uint8 base[G101_TILE_PIXELS*4],badbase[G101_TILE_PIXELS*4],bank[700];
static bool lower_present=true,lower_mismatch,preflight_ok=true,cap_present=true,cap_mismatch,cap_enabled,lower_active;
static unsigned scene_calls,lower_loads,cap_loads,preflights,cap_checks,lower_draws,cap_draws,draws,rejections;
static int material_row=1,shape_error;
static Asset asset;
void ground101_frame_reset(void){lower_active=false;}
bool ground101_bundle_load(const char *path){assert(!strcmp(path,"selected"));lower_loads++;return lower_present;}
const G101Record *ground101_record_at(unsigned i){assert(i<61);return &g101_records[i];}
const G101Record *ground101_record(unsigned role,unsigned id)
{for(unsigned i=0;i<61;i++)if(g101_records[i].role==role&&g101_records[i].index==id)return &g101_records[i];return NULL;}
const uint8_t *ground101_base(const G101Record *r){assert(r);return base;}
bool ground101_layer1_preflight(const void *map,size_t bytes,const void *first,size_t stride,int x,int y)
{assert(map==megaData1.mainmap&&bytes==sizeof(megaData1.mainmap)&&first==&megaData1.mainmap[20][2]&&stride==sizeof(JE_byte *)&&x==13&&y==-17);preflights++;lower_active=preflight_ok;return preflight_ok;}
int ground101_layer1_row(const void *p,int x,int y){(void)p;(void)x;(void)y;return lower_active?material_row:0;}
bool plateau_cap_bundle_load(const char *path){assert(lower_active&&scene_calls==61&&!strcmp(path,"selected"));cap_loads++;return cap_present;}
bool plateau_cap_verify_sources(PCapSourceLookup lookup,void *context)
{
 assert(cap_present&&lower_active);cap_checks++;
 for(unsigned i=0;i<13;i++) {const uint8_t *p=lookup(pcap_records[i].index,pcap_records[i].slot,context);if(!p||memcmp(p,base,sizeof(base)))return false;}
 cap_enabled=true;return true;
}
const PCapRecord *plateau_cap_record(unsigned id)
{if(!cap_enabled||!lower_active)return NULL;for(unsigned i=0;i<13;i++)if(pcap_records[i].index==id&&pcap_records[i].mask_offset)return &pcap_records[i];return NULL;}
static Asset *scene_asset(int slot,int role,int id,int ax,int ay)
{
 assert(slot>=0&&slot<330);scene_calls++;
 asset=(Asset){true,true,role,id,24,28,ax,ay,8,base};
 if(!lower_active&&lower_mismatch&&role==201&&id==96)asset.rgba=badbase;
 if(lower_active&&cap_mismatch&&id==109)asset.rgba=badbase;
 if(shape_error==1)asset.density=4;
 if(shape_error==2)asset.w=23;
 if(shape_error==3)asset.h=27;
 if(shape_error==4)asset.anchor_x=1;
 if(shape_error==5)asset.anchor_y=1;
 if(shape_error==7)asset.bank=101;
 if(shape_error==8)asset.index=110;
 return shape_error==6?NULL:&asset;
}
static void render_mirror_unsupported(const char *why){assert(why);rejections++;}
static bool draw_asset_filtered(int x,int y,Asset *a,int style,const void *part,Uint8 filter,const G101Record *lower,const PCapRecord *cap)
{(void)x;(void)y;(void)style;(void)part;assert(a&&filter==0);draws++;if(lower)lower_draws++;if(cap)cap_draws++;suppress=true;return true;}
static void game_probe_scene_draw(unsigned role,unsigned id,int x,int y,int part,int style,bool mirrored)
{(void)id;(void)x;(void)y;(void)part;(void)style;assert(role==201&&mirrored);}
#include "wiring.inc"
static void check_rows(bool expect_lower,bool expect_cap)
{
 for(unsigned j=0;j<13;j++) {
  unsigned id=pcap_records[j].index;terrain_source_count=0;render_mirror_bind_terrain(1,id,bank+id);assert(terrain_source_count==1);
  Uint8 *map[12]={bank+id};
  for(int style=MIRROR_NORMAL;style<=MIRROR_SHADOW;style++) {
   unsigned ld=lower_draws,cd=cap_draws;assert(render_mirror_terrain_row(game_screen,0,0,map,style)==1&&!suppress);
   assert(lower_draws-ld==(unsigned)(expect_lower&&style==MIRROR_NORMAL&&id!=109));
   assert(cap_draws-cd==(unsigned)(expect_cap&&style==MIRROR_NORMAL&&pcap_records[j].mask_offset));
  }
  material_row=0;unsigned ld=lower_draws,cd=cap_draws;assert(render_mirror_terrain_row(game_screen,0,0,map,MIRROR_NORMAL)==1);assert(ld==lower_draws&&cd==cap_draws);material_row=1;
 }
 Uint8 *map[12]={bank+109};unsigned old=draws;assert(render_mirror_terrain_row(&other,0,0,map,MIRROR_NORMAL)==0&&draws==old);
 if(expect_lower){material_row=-1;assert(!render_mirror_terrain_row(game_screen,0,0,map,MIRROR_NORMAL)&&rejections==1);material_row=1;}
}
int main(int argc,char **argv)
{
 assert(argc==2);const char *name=argv[1];bool blocked=false;badbase[0]=1;
 SDL_Surface *surface=game_screen;
 if(!strcmp(name,"lower-missing"))lower_present=false;
 else if(!strcmp(name,"lower-mismatch"))lower_mismatch=true;
 else if(!strcmp(name,"preflight-failure"))preflight_ok=false;
 else if(!strcmp(name,"cap-missing"))cap_present=false;
 else if(!strcmp(name,"cap-mismatch"))cap_mismatch=true;
 else if(!strcmp(name,"density4")){game_probe_density=4;blocked=true;}
 else if(!strcmp(name,"wrong-surface")){surface=&other;blocked=true;}
 else if(!strcmp(name,"inactive")){active=false;blocked=true;}
 else if(!strcmp(name,"wrong-map")){terrain_file='x';blocked=true;}
 else if(!strcmp(name,"missing-assets")){game_probe_missing=true;blocked=true;}
 else if(!strcmp(name,"invalid-assets")){game_probe_invalid=true;blocked=true;}
 else if(!strcmp(name,"original-reference")){game_probe_original_reference=true;blocked=true;}
 else if(!strcmp(name,"no-assets")){game_probe_assets=NULL;blocked=true;}
 else if(!strcmp(name,"wrong-scene-bits")){game_probe_scene_assets=2;blocked=true;}
 else if(!strcmp(name,"already-rejected")){reject_reason="old";blocked=true;}
 else assert(!strcmp(name,"valid"));
 render_mirror_ground101_layer1(surface,&megaData1.mainmap[20][2],13,-17);
 bool expect_lower=!blocked&&lower_present&&!lower_mismatch&&preflight_ok;
 bool expect_cap=expect_lower&&cap_present&&!cap_mismatch;
 assert(lower_active==expect_lower&&cap_enabled==expect_cap);
 assert(cap_loads==(unsigned)expect_lower);
 assert(cap_checks==(unsigned)(expect_lower&&cap_present));
 if(blocked)assert(!lower_loads&&!scene_calls&&!preflights&&!cap_loads&&!cap_checks);
 if(!blocked) {
  assert(lower_loads==1);
  if(!lower_present)assert(!scene_calls&&!preflights);
  if(lower_present&&!lower_mismatch)assert(preflights==1);
  check_rows(expect_lower,expect_cap);
 }
 if(!strcmp(name,"valid"))for(shape_error=0;shape_error<=8;shape_error++)assert((plateau_cap_selected_source(109,205,NULL)!=NULL)==(shape_error==0));
 printf("PASS %s lower=%d cap=%d lower-first gate and selected-source validation\n",name,expect_lower,expect_cap);return 0;
}
