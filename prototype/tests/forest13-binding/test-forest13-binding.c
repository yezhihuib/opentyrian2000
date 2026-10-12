/* Portable routing oracle. Production helpers are extracted unchanged by the
 * runner. Material preparation/sampling and drawing are explicit test doubles:
 * this file proves binding/fallback decisions, never pixel appearance. */
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "forest13_material.h"
#include "plateau_cap_material.h"
typedef uint8_t Uint8;
typedef Uint8 JE_byte;
typedef struct { int pitch; } SDL_Surface;
typedef struct { int x,y,w,h; } SDL_Rect;
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_EXPLOSION=106,ASSET_SHAPESZ=201};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_CAPACITY=367,TERRAIN_SOURCE_CAPACITY=193,MECHANICAL_COUNT=8};
#include "production-types.inc"
static unsigned long checks;
#define CHECK(x) do { if(!(x)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x);exit(1);} ++checks; } while(0)
static char terrain_file;
static unsigned terrain_source_count;
static bool forest_registry_ok=true;
static unsigned game_probe_scene_assets=3;
static bool active=true,suppress,game_probe_missing,game_probe_invalid,game_probe_original_reference;
static const char *reject_reason,*game_probe_assets;
static int game_probe_density=8;
static SDL_Surface screen={320},*game_screen=&screen;
static const unsigned forest_ids[]={211,212,213,215,221,222,223,224,225,231,232,233,234};
static const unsigned old_ids[]={101,37,57,49,50,321,322,331,332,99,100,106,107,109,110,118,119,120,96,97,98,108,323,324,333,334,36,39,40,46,48,56,58,38,47,111,114,113,341,342,343,351,352,353};
static const int old_slots[]={10,11,12,13,14,19,20,21,22,201,202,203,204,205,206,207,208,209,227,228,229,230,237,238,239,240,220,221,222,223,224,225,226,235,236,241,242,246,247,248,249,250,251,252};
static const unsigned grass_ids[]={66,67,69,76,78,79,80,89,90};
static const unsigned cloud_ids[]={41,42,43,44,45,51,52,53,54,55,61,62,63,64,65};
static const unsigned gray_ids[]={121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154};
static const unsigned purple_ids[]={150,156,157,158,159,160,166,168,169,170,176,177,178};
static const unsigned circuit_ids[]={181,182,184,185,192,193,194,195,201,202};
static const unsigned mechanical_ids[]={188,189,198,199,186,187,196,197};
static Uint8 pointers[700][672];
static const char *root;
static char pack[4096];
static bool member(unsigned id,const unsigned *ids,unsigned n){for(unsigned i=0;i<n;i++)if(ids[i]==id)return true;return false;}
static int forest_index(unsigned id){for(int i=0;i<13;i++)if(forest_ids[i]==id)return i;return -1;}
static bool accepted(unsigned layer,unsigned id){return (layer==1&&(member(id,old_ids,44)||member(id,grass_ids,9)||member(id,forest_ids,13)))||(layer==2&&member(id,cloud_ids,15))||(layer==3&&(member(id,purple_ids,13)||member(id,gray_ids,18)||member(id,circuit_ids,10)||member(id,mechanical_ids,MECHANICAL_COUNT)));}
/* Production preflight references the real-shaped map. Loader writes its source
 * pointers into these same 72-slot structures; no engine/SDL process is used. */
static struct {struct {Uint8 sh[672];unsigned fill;} shapes[72];Uint8 *mainmap[300][14];} megaData1,megaData2,megaData3;
static unsigned bank_resets,rejections;
static void render_mirror_reset_banking(void){++bank_resets;}
static void render_mirror_unsupported(const char *reason){++rejections;reject_reason=reason;}
/* Test-double boundary. It is deliberately visible, rather than claiming the
 * real lower/cap/forest parsers or world sampler have executed here. */
static bool lower_available=true,preflight_success=true,lower_context,cap_available=true,cap_ready;
static int row_override=-2;
static unsigned frame_resets,lower_loads,preflights,cap_loads,cap_verifications;
static G101FastContext fake_context;
static G101Record lower_record={201,99,201,0,0,0,0,0};
static PCapRecord cap_record={96,227,0};
static Uint8 lower_pixels[G101_TILE_PIXELS*4];
static bool lower_source_mismatch;
void ground101_frame_reset(void){++frame_resets;lower_context=false;}
bool ground101_bundle_load(const char *directory){CHECK(directory==game_probe_assets);++lower_loads;return lower_available;}
const G101Record *ground101_record_at(unsigned i){CHECK(i<61);return &lower_record;}
const Uint8 *ground101_base(const G101Record *record){CHECK(record==&lower_record);lower_pixels[0]=(Uint8)(99+(lower_source_mismatch?1:0));return lower_pixels;}
const G101Record *ground101_record(unsigned role,unsigned id){return lower_context&&role==201&&id==99?&lower_record:NULL;}
const G101FastContext *ground101_fast_context(void){return lower_context?&fake_context:NULL;}
bool ground101_layer1_preflight(const void *map,size_t bytes,const void *first,size_t stride,int x,int y)
{CHECK(map==megaData1.mainmap&&bytes==sizeof(megaData1.mainmap)&&first==megaData1.mainmap&&stride==sizeof(JE_byte *)&&x==0&&y==0);++preflights;lower_context=preflight_success;return lower_context;}
int ground101_layer1_row(const void *map,int x,int y){(void)map;(void)x;(void)y;return row_override!=-2?row_override:lower_context?1:0;}
bool plateau_cap_bundle_load(const char *directory){CHECK(directory==game_probe_assets);++cap_loads;return cap_available;}
bool plateau_cap_verify_sources(PCapSourceLookup lookup,void *context){++cap_verifications;cap_ready=lookup(96,227,context)!=NULL;return cap_ready;}
const PCapRecord *plateau_cap_record(unsigned id){return lower_context&&cap_ready&&id==96?&cap_record:NULL;}
enum {POLICY_ABSENT,POLICY_VALID,POLICY_INVALID};
static int policy=POLICY_VALID;
static bool policy_seen,declared,forest_payload=true,forest_ready;
static unsigned policy_checks,forest_prepares,source_lookups;
static Forest13Record forest_records[13];
bool forest13_policy_check(const char *directory){(void)directory;++policy_checks;policy_seen=true;declared=policy!=POLICY_ABSENT;return policy==POLICY_VALID;}
bool forest13_declared(void){return declared;}
bool forest13_prepare(const char *directory,Forest13SourceLookup lookup,void *context)
{
 ++forest_prepares;forest_ready=false;
 if(!forest13_policy_check(directory)||!ground101_fast_context()||!forest_payload)return false;
 bool good=true;
 for(unsigned i=0;i<13;i++){
  const Uint8 *p=lookup(forest_ids[i],336+i,context);++source_lookups;
  if(!p){good=false;continue;}
  /* Synthetic all-source success/failure signal, not canonical validation. */
  for(unsigned n=0;n<G101_TILE_PIXELS;n++)if(p[n*4]!=(Uint8)forest_ids[i]||p[n*4+1]!=(Uint8)(forest_ids[i]>>8)||p[n*4+2]!=77||p[n*4+3]!=255){good=false;break;}
 }
 forest_ready=good;return good;
}
const Forest13Record *forest13_record(unsigned id)
{int i=forest_index(id);return forest_ready&&ground101_fast_context()&&i>=0?&forest_records[i]:NULL;}
static unsigned draws,traces,forest_draws,lower_draws,cap_draws;
static unsigned draw_ids[12],draw_slots[12];
static int draw_density[12],draw_x[12],draw_y[12];
static bool draw_forest[12],draw_lower[12],draw_cap[12],draw_success=true;
static const Uint8 *draw_rgba[12];
static bool draw_asset_filtered(int x,int y,Asset *a,int style,const SDL_Rect *part,Uint8 filter,const G101Record *material,const PCapRecord *cap,const Forest13Record *forest)
{
 CHECK(draws<12&&a&&a->valid&&a->bank==201&&a->w==24&&a->h==28&&a->anchor_x==0&&a->anchor_y==0&&!part&&!filter);
 CHECK(a->density==8||a->density==4);
 if(forest){CHECK(style==MIRROR_NORMAL&&a->density==8&&forest_registry_ok&&policy_seen&&forest_ready&&lower_context);CHECK(forest->index==(unsigned)a->index&&forest->slot==(unsigned)(a-assets));++forest_draws;}
 if(material){CHECK(material==&lower_record&&a->index==99);++lower_draws;}
 if(cap){CHECK(cap==&cap_record&&a->index==96);++cap_draws;}
 draw_ids[draws]=(unsigned)a->index;draw_slots[draws]=(unsigned)(a-assets);draw_density[draws]=a->density;draw_x[draws]=x;draw_y[draws]=y;
 draw_forest[draws]=forest!=NULL;draw_lower[draws]=material!=NULL;draw_cap[draws]=cap!=NULL;draw_rgba[draws]=a->rgba;++draws;
 suppress=draw_success;return draw_success;
}
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{CHECK(role==201&&part==0&&style>=-1&&traces<12&&draws==traces+1&&draw_ids[traces]==id&&draw_x[traces]==x&&draw_y[traces]==y&&mirrored==draw_success);++traces;}
/* The production row's font-occlusion hook is a test double. Only its
 * terrain-row bounds are checked here; no font restoration pixels execute. */
static void font_before_effect(SDL_Rect bounds)
{CHECK(bounds.x>=0&&bounds.x+bounds.w<=game_screen->pitch&&bounds.w==12*24&&bounds.h==28);}
#include "production-helpers.inc"
static void clear_draws(void){draws=traces=forest_draws=lower_draws=cap_draws=0;suppress=false;}
static void reset(const char *label,int selected_policy)
{
 for(unsigned i=0;i<ASSET_CAPACITY;i++)free(assets[i].rgba);memset(assets,0,sizeof(assets));
 CHECK(snprintf(pack,sizeof(pack),"%s/%s",root,label)>0);CHECK(strlen(pack)<sizeof(pack)-1);game_probe_assets=pack;
 game_probe_density=8;game_probe_scene_assets=3;active=draw_success=true;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;reject_reason=NULL;
 lower_available=preflight_success=cap_available=forest_payload=true;lower_context=cap_ready=forest_ready=policy_seen=declared=false;row_override=-2;
 lower_loads=preflights=cap_loads=cap_verifications=policy_checks=forest_prepares=source_lookups=0;policy=selected_policy;clear_draws();
 render_mirror_map_begin('Z');
}
static void preflight(void){render_mirror_ground101_layer1(game_screen,megaData1.mainmap,0,0);}
static unsigned draw_pointer(Uint8 *p,int style){Uint8 *row[12]={p};clear_draws();return render_mirror_terrain_row(game_screen,0,17,row,style);}
static void bind_family(void){for(unsigned i=0;i<13;i++)render_mirror_bind_terrain(1,forest_ids[i],pointers[i]);render_mirror_bind_terrain(1,99,pointers[13]);render_mirror_bind_terrain(1,96,pointers[14]);}
static void check_family(bool forest_expected,int density)
{
 for(unsigned i=0;i<13;i++){
  CHECK(draw_pointer(pointers[i],MIRROR_NORMAL)==(unsigned)forest_expected);
  CHECK(draws==(unsigned)forest_expected&&traces==draws&&!suppress);
  if(forest_expected){CHECK(draw_ids[0]==forest_ids[i]&&draw_slots[0]==336+i&&draw_density[0]==density);CHECK(draw_forest[0]==(policy==POLICY_VALID&&forest_ready&&lower_context&&forest_registry_ok));}
 }
}
static void nonforest(bool material,bool cap)
{
 CHECK(draw_pointer(pointers[13],MIRROR_NORMAL)==1);CHECK(draws==1&&draw_slots[0]==201&&draw_lower[0]==material&&!draw_forest[0]&&!draw_cap[0]);
 CHECK(draw_pointer(pointers[14],MIRROR_NORMAL)==1);CHECK(draws==1&&draw_slots[0]==227&&draw_cap[0]==cap&&!draw_forest[0]&&!draw_lower[0]);
}
static void finite_mapping(void)
{
 CHECK(sizeof(assets)/sizeof(*assets)==ASSET_CAPACITY&&sizeof(terrain_sources)/sizeof(*terrain_sources)==TERRAIN_SOURCE_CAPACITY);
 for(unsigned id=0;id<=1000;id++){
  int expected=-1;for(unsigned i=0;i<13;i++)if(forest_ids[i]==id)expected=336+(int)i;CHECK(forest_terrain_slot(id)==expected);
 }
 CHECK(forest_terrain_slot(UINT_MAX)==-1);
 for(unsigned layer=0;layer<5;layer++)for(unsigned id=0;id<=600;id++){
  render_mirror_map_begin('Z');render_mirror_bind_terrain(layer,id,pointers[0]);CHECK(terrain_source_count==(unsigned)accepted(layer,id));CHECK(forest_registry_ok);
  if(terrain_source_count)CHECK(terrain_sources[0].id==id&&terrain_sources[0].data==pointers[0]);
 }
 render_mirror_bind_terrain(UINT_MAX,211,pointers[0]);render_mirror_bind_terrain(1,UINT_MAX,pointers[0]);CHECK(!terrain_source_count);
 for(unsigned b=0;b<256;b++)for(unsigned i=0;i<13;i++){
  render_mirror_map_begin((char)b);render_mirror_bind_terrain(1,forest_ids[i],pointers[i]);CHECK(terrain_source_count==(unsigned)(b=='Z'||b=='z'));CHECK(forest_registry_ok);
 }
 reset("canonical8",POLICY_ABSENT);
 for(unsigned i=0;i<44;i++){render_mirror_bind_terrain(1,old_ids[i],pointers[i]);CHECK(draw_pointer(pointers[i],MIRROR_NORMAL)==1);CHECK(draw_slots[0]==(unsigned)old_slots[i]);}
 render_mirror_map_begin('Z');
 for(unsigned i=0;i<9;i++){render_mirror_bind_terrain(1,grass_ids[i],pointers[i]);CHECK(draw_pointer(pointers[i],MIRROR_NORMAL)==1);CHECK(draw_slots[0]==312+i);}
 render_mirror_map_begin('Z');
 for(unsigned i=0;i<15;i++){render_mirror_bind_terrain(2,cloud_ids[i],pointers[i]);CHECK(draw_pointer(pointers[i],MIRROR_NORMAL)==1);CHECK(draw_slots[0]==186+i);}
 render_mirror_map_begin('Z');
 for(unsigned i=0;i<18;i++){render_mirror_bind_terrain(3,gray_ids[i],pointers[i]);CHECK(draw_pointer(pointers[i],MIRROR_NORMAL)==1);CHECK(draw_slots[0]==272+i);}
 render_mirror_map_begin('Z');
 for(unsigned i=0;i<13;i++){render_mirror_bind_terrain(3,purple_ids[i],pointers[i]);CHECK(draw_pointer(pointers[i],MIRROR_NORMAL)==1);CHECK(draw_slots[0]==290+i);}
 for(unsigned i=321;i<336;i++)CHECK(!assets[i].initialized);
}
static void selected_source_metadata(void)
{
 reset("canonical8",POLICY_VALID);
 for(unsigned i=0;i<13;i++){
  const Uint8 *original=plateau_cap_selected_source(forest_ids[i],336+i,NULL);CHECK(original);
  Asset saved=assets[336+i];
  for(unsigned bad=0;bad<8;bad++){
   Asset *a=&assets[336+i];*a=saved;
   if(bad==0)a->bank=106;if(bad==1)a->index++;if(bad==2)a->density=4;if(bad==3)a->w=12;
   if(bad==4)a->h=14;if(bad==5)a->anchor_x=1;if(bad==6)a->anchor_y=1;if(bad==7)a->valid=false;
   CHECK(!plateau_cap_selected_source(forest_ids[i],336+i,NULL));
  }
  assets[336+i]=saved;CHECK(plateau_cap_selected_source(forest_ids[i],336+i,NULL)==original);
 }
}
static void policies(void)
{
 /* One successful declared preparation validates all 13 sources before drawing. */
 reset("canonical8",POLICY_VALID);bind_family();preflight();CHECK(policy_seen&&declared&&forest_ready&&source_lookups==13&&lower_context&&cap_ready);check_family(true,8);nonforest(true,true);
 /* Forest payload failures have no effect on live lower/cap paths. */
 for(unsigned kind=0;kind<3;kind++){
  reset("canonical8",kind==0?POLICY_INVALID:POLICY_VALID);bind_family();forest_payload=kind==0;preflight();CHECK(declared&&!forest_ready);check_family(false,8);nonforest(true,true);
 }
 /* Absence is explicit opt-out, regardless of the sidecar availability signal. */
 const char *packs[]={"canonical8","custom8","mixed8","custom4","canonical4","custom-alpha8"};
 for(unsigned p=0;p<6;p++)for(unsigned available=0;available<2;available++){
  reset(packs[p],POLICY_ABSENT);bind_family();forest_payload=available;preflight();CHECK(!declared&&!forest_ready&&!source_lookups);check_family(true,p==3||p==4?4:8);nonforest(true,true);
  for(unsigned i=0;i<13;i++){
   CHECK(draw_pointer(pointers[i],MIRROR_NORMAL)==1);const Uint8 *rgba=draw_rgba[0];int shift=(p==1||p==3||p==5||(p==2&&i%2))?31:0;
   Uint8 expected[4]={(Uint8)(forest_ids[i]+shift),(Uint8)(forest_ids[i]>>8),(Uint8)(77+shift),(Uint8)(p==5?127:255)};
   bool identical=true;unsigned pixels=24u*28u*(unsigned)draw_density[0]*(unsigned)draw_density[0];
   for(unsigned n=0;n<pixels;n++)if(memcmp(rgba+4*n,expected,4))identical=false;
   CHECK(identical);
  }
 }
 /* Unmarked custom 4x art also survives absent lower/world context. */
 reset("custom4",POLICY_ABSENT);bind_family();lower_available=false;preflight();CHECK(policy_seen&&!declared&&!lower_context);check_family(true,4);nonforest(false,false);
 /* Every individual bad member disables every registered member together. */
 const char *classes[]={"missing","invalid","corrupt","alpha","density4"};
 for(unsigned c=0;c<5;c++)for(unsigned i=0;i<13;i++){
  char name[48];snprintf(name,sizeof(name),"%s-%u",classes[c],forest_ids[i]);reset(name,POLICY_VALID);bind_family();preflight();CHECK(declared&&!forest_ready&&source_lookups==13);check_family(false,8);nonforest(true,true);
 }
 /* Without declaration, ordinary independent missing/invalid member semantics survive. */
 for(unsigned i=0;i<13;i++){
  char name[48];snprintf(name,sizeof(name),"missing-%u",forest_ids[i]);reset(name,POLICY_ABSENT);bind_family();preflight();
  for(unsigned j=0;j<13;j++){CHECK(draw_pointer(pointers[j],MIRROR_NORMAL)==(unsigned)(i!=j));CHECK(draws==(unsigned)(i!=j));}
  nonforest(true,true);
 }
 /* Ordered mixed rows prove skipped forest does not set a replacement bit,
  * call the draw recorder, or steal a neighboring lower/cap draw. */
 for(int p=POLICY_ABSENT;p<=POLICY_INVALID;p++)for(unsigned ready=0;ready<2;ready++){
  reset("canonical8",p);bind_family();forest_payload=ready;preflight();
  Uint8 *cells[12]={pointers[0],pointers[13],pointers[12],pointers[14],pointers[1]};
  bool enabled=p==POLICY_ABSENT||(p==POLICY_VALID&&ready);clear_draws();
  CHECK(render_mirror_terrain_row(game_screen,0,21,cells,MIRROR_NORMAL)==(enabled?31u:10u));
  CHECK(draws==(enabled?5u:2u)&&traces==draws&&!suppress&&lower_draws==1&&cap_draws==1);
  CHECK(forest_draws==(p==POLICY_VALID&&ready?3u:0u));
  if(!enabled)CHECK(draw_ids[0]==99&&draw_x[0]==24&&draw_ids[1]==96&&draw_x[1]==72);
 }
 reset("canonical8",POLICY_VALID);bind_family();preflight();lower_context=false;check_family(false,8);nonforest(false,false);
 reset("canonical8",POLICY_VALID);bind_family();preflight();row_override=0;check_family(false,8);nonforest(false,false);
 reset("canonical8",POLICY_VALID);bind_family();preflight();cap_available=false;cap_ready=false;check_family(true,8);nonforest(true,false);
}
static void pointers_and_capacity(void)
{
 reset("canonical8",POLICY_VALID);bind_family();render_mirror_bind_terrain(1,211,pointers[15]);render_mirror_bind_terrain(1,211,pointers[0]);CHECK(terrain_source_count==17&&forest_registry_ok);preflight();check_family(true,8);CHECK(draw_pointer(pointers[15],MIRROR_NORMAL)==1&&draw_ids[0]==211);
 /* Equal indexed bytes are not identity: unregistered pointers stay indexed. */
 CHECK(!memcmp(pointers[0],pointers[699],672));CHECK(!draw_pointer(pointers[699],MIRROR_NORMAL)&&!draws);
 reset("canonical8",POLICY_VALID);bind_family();for(unsigned i=15;i<213;i++)render_mirror_bind_terrain(3,150,pointers[i]);CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&forest_registry_ok);preflight();check_family(true,8);nonforest(true,true);CHECK(draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL)==1);CHECK(!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY],MIRROR_NORMAL));
 /* Lost repeated-ID pointer, null attempt, and first-match ambiguity are each
  * forest-local failures. Existing insertion and first-match order is retained. */
 for(int declared_case=0;declared_case<2;declared_case++)for(unsigned failure=0;failure<4;failure++){
  reset("canonical8",declared_case?POLICY_VALID:POLICY_ABSENT);bind_family();
  if(failure==0){for(unsigned i=15;i<TERRAIN_SOURCE_CAPACITY;i++)render_mirror_bind_terrain(3,150,pointers[i]);render_mirror_bind_terrain(1,211,pointers[TERRAIN_SOURCE_CAPACITY]);CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY);CHECK(!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY],MIRROR_NORMAL));}
  if(failure==1)render_mirror_bind_terrain(1,211,NULL);
  if(failure==2){render_mirror_bind_terrain(1,212,pointers[0]);CHECK(terrain_sources[0].id==211);}
  if(failure==3){render_mirror_bind_terrain(1,211,pointers[13]);CHECK(terrain_sources[13].id==99);}
  CHECK(!forest_registry_ok);preflight();check_family(!declared_case,8);nonforest(true,true);CHECK(!draw_pointer(NULL,MIRROR_NORMAL));
 }
 /* Exact last capacity entry succeeds; the next distinct source fails. */
 reset("canonical8",POLICY_VALID);for(unsigned i=0;i<TERRAIN_SOURCE_CAPACITY-1;i++)render_mirror_bind_terrain(3,150,pointers[i]);render_mirror_bind_terrain(1,211,pointers[TERRAIN_SOURCE_CAPACITY-1]);CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&forest_registry_ok);preflight();CHECK(draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL)==1);render_mirror_bind_terrain(1,211,pointers[TERRAIN_SOURCE_CAPACITY]);CHECK(!forest_registry_ok&&!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL));
 /* Reset recovers local completeness; legitimate maps may use one ID only. */
 unsigned resets=bank_resets;render_mirror_map_begin('Z');CHECK(forest_registry_ok&&!terrain_source_count&&bank_resets==resets+1&&!lower_context);CHECK(!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL));render_mirror_bind_terrain(1,234,pointers[400]);preflight();CHECK(source_lookups==26&&draw_pointer(pointers[400],MIRROR_NORMAL)==1&&draw_ids[0]==234);CHECK(!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL));
 render_mirror_map_begin('Y');render_mirror_bind_terrain(1,234,pointers[400]);CHECK(!terrain_source_count&&forest_registry_ok&&!draw_pointer(pointers[400],MIRROR_NORMAL));
}
static void guards_and_rows(void)
{
 const int styles[]={-1,MIRROR_BLEND,MIRROR_SHADOW,3,INT_MAX};
 for(unsigned s=0;s<5;s++)for(int p=POLICY_ABSENT;p<=POLICY_INVALID;p++){
  reset("canonical8",p);bind_family();/* Intentionally no preparation: style skip must precede asset loading. */
  for(unsigned i=0;i<13;i++){CHECK(!draw_pointer(pointers[i],styles[s]));CHECK(!draws&&!traces&&!suppress&&!assets[336+i].initialized);}
 }
 /* All excluded layer registrations leave both registry and caches untouched. */
 for(unsigned layer=0;layer<5;layer++)if(layer!=1){reset("canonical8",POLICY_VALID);for(unsigned i=0;i<13;i++){render_mirror_bind_terrain(layer,forest_ids[i],pointers[i]);CHECK(!terrain_source_count&&!draw_pointer(pointers[i],MIRROR_NORMAL)&&!assets[336+i].initialized);}}
 for(unsigned flag=0;flag<8;flag++){
  reset("canonical8",POLICY_VALID);bind_family();
  if(flag==0)game_probe_missing=true;if(flag==1)game_probe_invalid=true;if(flag==2)game_probe_density=1;if(flag==3)game_probe_assets=NULL;
  if(flag==4)game_probe_scene_assets=0;if(flag==5)active=false;if(flag==6)reject_reason="test";if(flag==7)game_probe_original_reference=true;
  preflight();CHECK(policy_seen&&!forest_ready);check_family(false,8);
 }
 reset("canonical8",POLICY_VALID);bind_family();preflight();
 SDL_Surface other={320};Uint8 *row[12]={pointers[0]};clear_draws();CHECK(!render_mirror_terrain_row(&other,0,0,row,MIRROR_NORMAL)&&!draws);
 CHECK(!render_mirror_terrain_row(game_screen,-1,0,row,MIRROR_NORMAL));reject_reason=NULL;CHECK(!render_mirror_terrain_row(game_screen,33,0,row,MIRROR_NORMAL));reject_reason=NULL;
 clear_draws();CHECK(render_mirror_terrain_row(game_screen,32,-11,row,MIRROR_NORMAL)==1&&draw_x[0]==32&&draw_y[0]==-11);
 row_override=-1;clear_draws();unsigned before=rejections;CHECK(!render_mirror_terrain_row(game_screen,0,0,row,MIRROR_NORMAL)&&!draws&&rejections==before+1&&!strcmp(reject_reason,"ground101-row-context-mismatch"));
 reset("canonical8",POLICY_VALID);bind_family();preflight();draw_success=false;CHECK(!draw_pointer(pointers[0],MIRROR_NORMAL)&&draws==1&&traces==1&&!suppress);
 const unsigned masks[]={0,1,2048,0x555,0xaaa,0xfff,0xa91};
 reset("canonical8",POLICY_VALID);bind_family();preflight();
 for(unsigned start=0;start<13;start++)for(unsigned rev=0;rev<2;rev++)for(unsigned m=0;m<7;m++){
  Uint8 *cells[12];unsigned ids[12],n=0;
  for(unsigned i=0;i<12;i++){unsigned k=(start+(rev?11-i:i))%13;ids[i]=forest_ids[k];cells[i]=(masks[m]&(1u<<i))?pointers[k]:i%2?NULL:pointers[699];}
  clear_draws();CHECK(render_mirror_terrain_row(game_screen,16,-13,cells,MIRROR_NORMAL)==masks[m]);
  for(unsigned i=0;i<12;i++)if(masks[m]&(1u<<i)){CHECK(draw_ids[n]==ids[i]&&draw_x[n]==16+(int)i*24&&draw_y[n]==-13&&draw_forest[n]);++n;}
  CHECK(draws==n&&traces==n&&!suppress);
 }
}
static void circuit_tests(void);
static void mechanical_tests(void);
static void mechanical_review_additions(void);
/* Exact original engine loader loop, extracted by the runner. */
typedef bool JE_boolean;
typedef Uint8 JE_DanCShape[672];
static uint16_t mapSh[3][128];
static Uint8 *ref[3][128];
static unsigned source_index,source_attempts;
static void fread_bool_die(JE_boolean *out,FILE *file){(void)file;CHECK(source_index<600);*out=false;++source_index;}
static void fread_u8_die(Uint8 *out,size_t n,FILE *file){(void)file;CHECK(n==672&&source_index);memset(out,(int)(source_index%254+1),n);}
static void asset_debug_bind_terrain(char file,unsigned layer,unsigned id,const Uint8 *data){CHECK(file=='Z'&&layer>=1&&layer<=3&&id>=1&&id<=600&&data);++source_attempts;}
static void run_loader(void)
{
 Uint8 shape[672];int y,yy;FILE *shpFile=NULL;char char_shapeFile='Z';source_index=source_attempts=0;
 memset(ref,0,sizeof(ref));render_mirror_map_begin(char_shapeFile);
#include "production-loader.inc"
 CHECK(source_index==600&&source_attempts==213);
}
static void actual_loader(void)
{
 reset("canonical8",POLICY_VALID);for(unsigned s=0;s<128;s++){mapSh[0][s]=99;mapSh[1][s]=41;mapSh[2][s]=150;}run_loader();CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&forest_registry_ok);
 CHECK(draw_pointer(megaData1.shapes[0].sh,MIRROR_NORMAL)==1&&draw_ids[0]==99);CHECK(draw_pointer(megaData1.shapes[71].sh,MIRROR_NORMAL)==1);CHECK(!ref[1][71]&&!ref[2][70]&&!ref[2][71]);
 reset("canonical8",POLICY_VALID);for(unsigned s=0;s<128;s++){mapSh[0][s]=211;mapSh[1][s]=41;mapSh[2][s]=150;}run_loader();CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&!forest_registry_ok);preflight();
 for(unsigned s=0;s<72;s++)CHECK(!draw_pointer(megaData1.shapes[s].sh,MIRROR_NORMAL));CHECK(draw_pointer(megaData2.shapes[0].sh,MIRROR_NORMAL)==1&&draw_ids[0]==41);CHECK(draw_pointer(megaData3.shapes[0].sh,MIRROR_NORMAL)==1&&draw_ids[0]==150);
 reset("canonical8",POLICY_ABSENT);run_loader();CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&!forest_registry_ok);preflight();for(unsigned s=0;s<72;s++)CHECK(draw_pointer(megaData1.shapes[s].sh,MIRROR_NORMAL)==(unsigned)(s<52));
 /* Thirteen forest pointers are attempted after 200 earlier nonforest
  * registrations. Even absent forest IDs in the filled registry are caught. */
 reset("canonical8",POLICY_VALID);for(unsigned s=0;s<128;s++){mapSh[0][s]=s<13?forest_ids[s]:99;mapSh[1][s]=41;mapSh[2][s]=150;}run_loader();CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&!forest_registry_ok);/* 200 nonforest registrations precede forest, so this is another genuine loss. */
}
static void lower_failure(const char *mode)
{
 reset("canonical8",POLICY_VALID);bind_family();
 if(!strcmp(mode,"lower-missing"))lower_available=false;
 else if(!strcmp(mode,"preflight-failed"))preflight_success=false;
 else if(!strcmp(mode,"lower-source-failed"))lower_source_mismatch=true;
 else if(!strcmp(mode,"terrain-only"))game_probe_scene_assets=2;
 else if(!strcmp(mode,"density4"))game_probe_density=4;
 else if(!strcmp(mode,"original-reference"))game_probe_original_reference=true;
 else CHECK(false);
 preflight();CHECK(policy_seen&&declared&&!forest_ready&&!lower_context&&!forest_prepares);check_family(false,8);
 /* Lower and cap selected-art fallback is independent of forest declaration. */
 nonforest(false,false);
 if(lower_source_mismatch)CHECK(lower_loads==1&&!preflights);
 printf("PASS %s: %lu assertions; policy detected before lower exit; all 13 forest draws indexed, selected nonforest art retained.\n",mode,checks);
}
int main(int argc,char **argv)
{
 CHECK(argc==3);root=argv[1];
 for(unsigned n=0;n<G101_TILE_PIXELS;n++){lower_pixels[n*4]=99;lower_pixels[n*4+1]=0;lower_pixels[n*4+2]=77;lower_pixels[n*4+3]=255;}
 for(unsigned i=0;i<13;i++){forest_records[i].index=forest_ids[i];forest_records[i].slot=336+i;}
 if(strcmp(argv[2],"suite"))lower_failure(argv[2]);
 else {finite_mapping();circuit_tests();mechanical_tests();mechanical_review_additions();selected_source_metadata();policies();pointers_and_capacity();guards_and_rows();actual_loader();printf("PASS suite: %lu assertions; actual extracted binding/row/preflight/HDA loader and engine registration loops, all 13 forest + 10 circuit + 8 mechanical IDs, prior finite slots, 193-pointer bounds, coupled/uncoupled decisions; draw/material doubles, no pixels.\n",checks);}
 for(unsigned i=0;i<ASSET_CAPACITY;i++)free(assets[i].rgba);
 return 0;
}

/* Circuit10 additions use actual extracted production helpers, synthetic HDA
 * bytes and exact routing observations. No raster draw is claimed. */
static void bind_circuit(void){for(unsigned i=0;i<10;i++)render_mirror_bind_terrain(3,circuit_ids[i],pointers[500+i]);}
static void check_circuit(unsigned omitted,int density)
{
 for(unsigned i=0;i<10;i++){
  CHECK(draw_pointer(pointers[500+i],MIRROR_NORMAL)==(unsigned)(i!=omitted));
  CHECK(draws==(unsigned)(i!=omitted)&&traces==draws&&!suppress);
  if(i!=omitted)CHECK(draw_ids[0]==circuit_ids[i]&&draw_slots[0]==349+i&&draw_density[0]==density&&!draw_lower[0]&&!draw_cap[0]&&!draw_forest[0]);
 }
}
static void circuit_tests(void)
{
 CHECK(sizeof(assets)/sizeof(*assets)==ASSET_CAPACITY);CHECK(sizeof(terrain_sources)/sizeof(*terrain_sources)==TERRAIN_SOURCE_CAPACITY);
 for(unsigned id=0;id<=1000;id++){
  int want=-1;for(unsigned i=0;i<10;i++)if(id==circuit_ids[i])want=349+(int)i;
  CHECK(layer3_circuit_slot(id)==want);
 }
 CHECK(layer3_circuit_slot(UINT_MAX)==-1&&layer3_circuit_slot(191)==-1);
 for(unsigned bank=0;bank<256;bank++)for(unsigned i=0;i<10;i++){
  render_mirror_map_begin((char)bank);render_mirror_bind_terrain(3,circuit_ids[i],pointers[500+i]);
  CHECK(terrain_source_count==(unsigned)(bank=='z'||bank=='Z')&&forest_registry_ok);
 }
 /* Wrong layer and style must not initialize art, even when art exists. */
 for(unsigned layer=0;layer<6;layer++)if(layer!=3){
  reset("canonical8",POLICY_ABSENT);
  for(unsigned i=0;i<10;i++){render_mirror_bind_terrain(layer,circuit_ids[i],pointers[500+i]);CHECK(!terrain_source_count&&!draw_pointer(pointers[500+i],MIRROR_NORMAL)&&!draws&&!traces&&!assets[349+i].initialized);}
 }
 const int styles[]={-1,MIRROR_BLEND,MIRROR_SHADOW,3,INT_MAX};
 for(unsigned s=0;s<5;s++){
  reset("canonical8",POLICY_ABSENT);bind_circuit();
  for(unsigned i=0;i<10;i++)CHECK(!draw_pointer(pointers[500+i],styles[s])&&!draws&&!traces&&!suppress&&!assets[349+i].initialized);
 }
 reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(3,191,pointers[520]);CHECK(!terrain_source_count&&!draw_pointer(pointers[520],MIRROR_NORMAL)&&!draws&&!traces);
 render_mirror_bind_terrain(3,181,NULL);CHECK(terrain_source_count==1&&forest_registry_ok&&!draw_pointer(NULL,MIRROR_NORMAL)&&!draws&&!assets[349].initialized);
 reset("canonical8",POLICY_ABSENT);bind_circuit();check_circuit(UINT_MAX,8);CHECK(forest_registry_ok);
 for(unsigned id=336;id<349;id++)CHECK(!assets[id].initialized);
 for(unsigned i=0;i<10;i++){
  /* Distinct pointer to equal source ID is a legitimate independent loader slot. */
  render_mirror_bind_terrain(3,circuit_ids[i],pointers[530+i]);CHECK(draw_pointer(pointers[530+i],MIRROR_NORMAL)==1&&draw_slots[0]==349+i);
 }
 CHECK(terrain_source_count==20&&forest_registry_ok);
 CHECK(!memcmp(pointers[500],pointers[699],672)&&!draw_pointer(pointers[699],MIRROR_NORMAL)&&!draws);
 /* First-match pointer identity is preserved rather than silently overwritten. */
 render_mirror_bind_terrain(3,202,pointers[500]);CHECK(terrain_source_count==21&&draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_ids[0]==181&&forest_registry_ok);
 reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(3,121,pointers[500]);render_mirror_bind_terrain(3,181,pointers[500]);CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_ids[0]==121&&draw_slots[0]==272);
 const char *invalid[]={"missing","invalid","wrong-id","wrong-bank","wrong-density","wrong-width","wrong-height","wrong-anchorx","wrong-anchory","truncated","trailing"};
 for(unsigned k=0;k<sizeof(invalid)/sizeof(*invalid);k++)for(unsigned i=0;i<10;i++){
  char name[96];snprintf(name,sizeof(name),"circuit-%s-%u",invalid[k],circuit_ids[i]);reset(name,POLICY_ABSENT);bind_circuit();check_circuit(i,8);
  CHECK(assets[349+i].initialized&&!assets[349+i].valid&&forest_registry_ok);
  render_mirror_bind_terrain(3,121,pointers[550]);CHECK(draw_pointer(pointers[550],MIRROR_NORMAL)==1&&draw_ids[0]==121);
 }
 for(unsigned k=0;k<2;k++)for(unsigned i=0;i<10;i++){
  char name[96];snprintf(name,sizeof(name),"circuit-%s-%u",k?"invalid8-valid4":"density4",circuit_ids[i]);reset(name,POLICY_ABSENT);bind_circuit();
  for(unsigned j=0;j<10;j++){CHECK(draw_pointer(pointers[500+j],MIRROR_NORMAL)==1&&draw_density[0]==(i==j?4:8)&&draw_slots[0]==349+j);}
 }
 for(unsigned i=0;i<10;i++){
  char name[96];snprintf(name,sizeof(name),"circuit-selected-%u",circuit_ids[i]);reset(name,POLICY_VALID);bind_circuit();CHECK(draw_pointer(pointers[500+i],MIRROR_NORMAL)==1);
  const Uint8 expected[4]={(Uint8)(circuit_ids[i]+31),(Uint8)(circuit_ids[i]>>8),108,255};
  for(unsigned n=0;n<24*28*8*8;n++)CHECK(!memcmp(draw_rgba[0]+n*4,expected,4));
 }
 reset("canonical8",POLICY_ABSENT);game_probe_density=4;bind_circuit();check_circuit(UINT_MAX,4);
 for(unsigned bad=0;bad<7;bad++){
  reset("canonical8",POLICY_ABSENT);bind_circuit();
  if(bad==0)game_probe_missing=true;if(bad==1)game_probe_invalid=true;if(bad==2)game_probe_density=1;if(bad==3)game_probe_assets=NULL;if(bad==4)game_probe_scene_assets=1;if(bad==5)active=false;if(bad==6)reject_reason="test";
  for(unsigned i=0;i<10;i++)CHECK(!draw_pointer(pointers[500+i],MIRROR_NORMAL)&&!draws&&!traces);
 }
 /* Forest policy/registry failure remains forest-local. */
 for(int pol=POLICY_ABSENT;pol<=POLICY_INVALID;pol++){
  reset("canonical8",pol);bind_circuit();bind_family();preflight();check_circuit(UINT_MAX,8);check_family(pol!=POLICY_INVALID,8);
 }
 reset("canonical8",POLICY_VALID);bind_circuit();bind_family();render_mirror_bind_terrain(1,211,NULL);CHECK(!forest_registry_ok);preflight();check_circuit(UINT_MAX,8);check_family(false,8);nonforest(true,true);
 /* Exact last registry position, overflow, duplicates, and reset recovery. */
 reset("canonical8",POLICY_ABSENT);for(unsigned n=0;n<TERRAIN_SOURCE_CAPACITY-1;n++)render_mirror_bind_terrain(3,150,pointers[n]);render_mirror_bind_terrain(3,202,pointers[TERRAIN_SOURCE_CAPACITY-1]);
 CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&forest_registry_ok&&draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL)==1&&draw_slots[0]==358);
 render_mirror_bind_terrain(3,181,pointers[TERRAIN_SOURCE_CAPACITY]);CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&forest_registry_ok&&!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY],MIRROR_NORMAL));
 render_mirror_bind_terrain(3,202,pointers[TERRAIN_SOURCE_CAPACITY-1]);CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL)==1&&draw_ids[0]==202);
 render_mirror_map_begin('Z');CHECK(!terrain_source_count&&forest_registry_ok&&!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL));bind_circuit();check_circuit(UINT_MAX,8);
 /* Exact production loader's worst213 attempts must truncate at193; forest
  * partial registrations cannot become an apparently complete coupled family. */
 reset("canonical8",POLICY_VALID);for(unsigned s=0;s<128;s++){mapSh[0][s]=211;mapSh[1][s]=41;mapSh[2][s]=181;}run_loader();CHECK(source_attempts==213&&terrain_source_count==TERRAIN_SOURCE_CAPACITY&&!forest_registry_ok);preflight();
 for(unsigned s=0;s<72;s++)CHECK(!draw_pointer(megaData1.shapes[s].sh,MIRROR_NORMAL));
 for(unsigned s=0;s<70;s++)CHECK(draw_pointer(megaData3.shapes[s].sh,MIRROR_NORMAL)==1&&draw_ids[0]==181&&draw_slots[0]==349);
 reset("canonical8",POLICY_ABSENT);run_loader();CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&!forest_registry_ok);
 /*71 cloud +70 circuit registrations precede forest => exactly52/72 forest pointers fit. */
 for(unsigned s=0;s<72;s++)CHECK(draw_pointer(megaData1.shapes[s].sh,MIRROR_NORMAL)==(unsigned)(s<52));
 /* Ordered mixed finite row preserves replacement bits and selected callbacks. */
 reset("canonical8",POLICY_ABSENT);bind_circuit();render_mirror_bind_terrain(3,121,pointers[550]);render_mirror_bind_terrain(2,41,pointers[551]);
 Uint8 *row[12]={pointers[500],NULL,pointers[550],pointers[509],pointers[551],pointers[699],pointers[504]};clear_draws();
 CHECK(render_mirror_terrain_row(game_screen,16,33,row,MIRROR_NORMAL)==93&&draws==5&&traces==5&&!suppress);
 const unsigned want[]={181,121,202,41,192};const int xs[]={16,64,88,112,160};for(unsigned i=0;i<5;i++)CHECK(draw_ids[i]==want[i]&&draw_x[i]==xs[i]);
 draw_success=false;CHECK(!draw_pointer(pointers[500],MIRROR_NORMAL)&&draws==1&&traces==1&&!suppress);
}

/* Bounded right-plus-left eight-member extension; all draw calls below are test doubles. */
static void mechanical_tests(void)
{
 for(unsigned id=0;id<=1000;id++) {
  int expected=-1;for(unsigned i=0;i<MECHANICAL_COUNT;i++)if(id==mechanical_ids[i])expected=359+(int)i;
  CHECK(layer3_mechanical_slot(id)==expected);
 }
 CHECK(layer3_mechanical_slot(UINT_MAX)==-1&&layer3_mechanical_slot(190)==-1&&layer3_mechanical_slot(200)==-1);
 for(unsigned i=0;i<MECHANICAL_COUNT;i++) {
  unsigned id=mechanical_ids[i];
  for(unsigned layer=0;layer<6;layer++) {
   reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(layer,id,pointers[500]);
   CHECK(terrain_source_count==(unsigned)(layer==3));
   CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==(unsigned)(layer==3));
   if(layer==3)CHECK(draw_slots[0]==359+i&&draw_ids[0]==id);
  }
  const int styles[]={-1,MIRROR_BLEND,MIRROR_SHADOW,3,INT_MAX};
  for(unsigned k=0;k<5;k++) {
   reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(3,id,pointers[500]);
   CHECK(!draw_pointer(pointers[500],styles[k])&&!assets[359+i].initialized&&!draws&&!traces);
  }
  const char *reasons[]={"missing","invalid","wrong-id","wrong-bank","wrong-density","wrong-width","wrong-height","wrong-anchorx","wrong-anchory","truncated","trailing"};
  for(unsigned k=0;k<11;k++) {
   char name[96];snprintf(name,sizeof(name),"circuit-%s-%u",reasons[k],id);reset(name,POLICY_ABSENT);
   for(unsigned j=0;j<MECHANICAL_COUNT;j++)render_mirror_bind_terrain(3,mechanical_ids[j],pointers[500+j]);
   for(unsigned j=0;j<MECHANICAL_COUNT;j++) {
    CHECK(draw_pointer(pointers[500+j],MIRROR_NORMAL)==(unsigned)(j!=i));
    CHECK(draws==(unsigned)(j!=i)&&traces==draws&&!suppress);
    if(j!=i)CHECK(draw_ids[0]==mechanical_ids[j]&&draw_slots[0]==359+j&&draw_density[0]==8&&!draw_lower[0]&&!draw_cap[0]&&!draw_forest[0]);
   }
   CHECK(assets[359+i].initialized&&!assets[359+i].valid&&forest_registry_ok);
   render_mirror_bind_terrain(3,121,pointers[550]);CHECK(draw_pointer(pointers[550],MIRROR_NORMAL)==1&&draw_ids[0]==121);
  }
  for(unsigned k=0;k<2;k++) {
   char name[96];snprintf(name,sizeof(name),"circuit-%s-%u",k?"invalid8-valid4":"density4",id);reset(name,POLICY_ABSENT);
   render_mirror_bind_terrain(3,id,pointers[500]);CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_density[0]==4);
  }
  reset("canonical8",POLICY_ABSENT);for(unsigned n=0;n<TERRAIN_SOURCE_CAPACITY-1;n++)render_mirror_bind_terrain(3,150,pointers[n]);
  render_mirror_bind_terrain(3,id,pointers[TERRAIN_SOURCE_CAPACITY-1]);CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY-1],MIRROR_NORMAL)==1&&draw_slots[0]==359+i);
  render_mirror_bind_terrain(3,id,pointers[TERRAIN_SOURCE_CAPACITY]);CHECK(terrain_source_count==TERRAIN_SOURCE_CAPACITY&&!draw_pointer(pointers[TERRAIN_SOURCE_CAPACITY],MIRROR_NORMAL));
 }
 /* Valid synthetic 190 and 200 assets are present: exclusion is finite routing. */
 const unsigned excluded[]={190,200};
 for(unsigned i=0;i<2;i++)for(unsigned layer=0;layer<6;layer++) {
  reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(layer,excluded[i],pointers[500]);
  CHECK(!terrain_source_count&&forest_registry_ok&&!draw_pointer(pointers[500],MIRROR_NORMAL)&&!draws&&!traces&&!suppress);
  for(unsigned slot=359;slot<ASSET_CAPACITY;slot++)CHECK(!assets[slot].initialized);
 }
}

/* Independent mechanical coverage: source-bank identity, nulls, selected bytes,
 * duplicate pointer order, global gates, local policy failure and loader bound. */
static void mechanical_review_additions(void)
{
 for(unsigned i=0;i<MECHANICAL_COUNT;i++) {
  unsigned id=mechanical_ids[i];
  for(unsigned bank=0;bank<256;bank++) {
   reset("canonical8",POLICY_ABSENT);render_mirror_map_begin((char)bank);
   render_mirror_bind_terrain(3,id,pointers[500]);
   bool allowed=bank=='z'||bank=='Z';
   CHECK(terrain_source_count==(unsigned)allowed&&forest_registry_ok);
   CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==(unsigned)allowed);
   CHECK(assets[359+i].initialized==allowed);
  }
  reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(3,id,NULL);
  CHECK(terrain_source_count==1&&forest_registry_ok&&!draw_pointer(NULL,MIRROR_NORMAL)&&!draws&&!traces&&!assets[359+i].initialized);
  render_mirror_bind_terrain(3,id,pointers[500]);render_mirror_bind_terrain(3,id,pointers[501]);
  CHECK(terrain_source_count==3&&draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_slots[0]==359+i);
  CHECK(draw_pointer(pointers[501],MIRROR_NORMAL)==1&&draw_slots[0]==359+i);
  CHECK(!memcmp(pointers[500],pointers[699],672)&&!draw_pointer(pointers[699],MIRROR_NORMAL));
  render_mirror_bind_terrain(3,mechanical_ids[(i+1)%MECHANICAL_COUNT],pointers[500]);
  CHECK(terrain_source_count==4&&draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_ids[0]==id);
  reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(3,121,pointers[500]);render_mirror_bind_terrain(3,id,pointers[500]);
  CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_ids[0]==121&&draw_slots[0]==272&&!assets[359+i].initialized);
  for(unsigned d=0;d<2;d++) {
   char name[96];snprintf(name,sizeof(name),d?"mechanical-selected4-%u":"circuit-selected-%u",id);reset(name,POLICY_ABSENT);
   render_mirror_bind_terrain(3,id,pointers[500]);CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_density[0]==(d?4:8)&&draw_slots[0]==359+i);
   Uint8 expected[4]={(Uint8)(id+(d?47:31)),(Uint8)(id>>8),(Uint8)(d?124:108),255};
   for(unsigned n=0;n<24*28*(d?16:64);n++)CHECK(!memcmp(draw_rgba[0]+n*4,expected,4));
  }
  reset("canonical8",POLICY_ABSENT);game_probe_density=4;render_mirror_bind_terrain(3,id,pointers[500]);
  CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_density[0]==4&&draw_slots[0]==359+i);
  for(unsigned bad=0;bad<7;bad++) {
   reset("canonical8",POLICY_ABSENT);render_mirror_bind_terrain(3,id,pointers[500]);
   if(bad==0)game_probe_missing=true;if(bad==1)game_probe_invalid=true;if(bad==2)game_probe_density=1;if(bad==3)game_probe_assets=NULL;
   if(bad==4)game_probe_scene_assets=1;if(bad==5)active=false;if(bad==6)reject_reason="test";
   CHECK(!draw_pointer(pointers[500],MIRROR_NORMAL)&&!draws&&!traces&&!suppress);
  }
  for(int policy_case=POLICY_ABSENT;policy_case<=POLICY_INVALID;policy_case++) {
   reset("canonical8",policy_case);bind_family();render_mirror_bind_terrain(3,id,pointers[500]);preflight();
   CHECK(draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_slots[0]==359+i&&!draw_forest[0]&&!draw_cap[0]&&!draw_lower[0]);
   check_family(policy_case!=POLICY_INVALID,8);
  }
  reset("canonical8",POLICY_VALID);bind_family();render_mirror_bind_terrain(3,id,pointers[500]);render_mirror_bind_terrain(1,211,NULL);preflight();
  CHECK(!forest_registry_ok&&draw_pointer(pointers[500],MIRROR_NORMAL)==1&&draw_slots[0]==359+i);check_family(false,8);
  draw_success=false;CHECK(!draw_pointer(pointers[500],MIRROR_NORMAL)&&draws==1&&traces==1&&!suppress);
 }
 reset("canonical8",POLICY_ABSENT);for(unsigned i=0;i<MECHANICAL_COUNT;i++)render_mirror_bind_terrain(3,mechanical_ids[i],pointers[500+i]);
 render_mirror_bind_terrain(3,200,pointers[550]);render_mirror_bind_terrain(3,181,pointers[551]);render_mirror_bind_terrain(3,121,pointers[552]);
 Uint8 *row[12]={pointers[500],pointers[550],pointers[501],NULL,pointers[502],pointers[551],pointers[503],pointers[552]};clear_draws();
 CHECK(render_mirror_terrain_row(game_screen,16,33,row,MIRROR_NORMAL)==245&&draws==6&&traces==6&&!suppress);
 const unsigned ids[]={188,189,198,181,199,121};const int xs[]={16,64,112,136,160,184};
 for(unsigned i=0;i<6;i++)CHECK(draw_ids[i]==ids[i]&&draw_x[i]==xs[i]);
 /* All eight, both explicit exclusions, and unrelated circuit/gray neighbors. */
 render_mirror_bind_terrain(3,190,pointers[553]);
 Uint8 *all_row[12]={pointers[500],pointers[553],pointers[504],pointers[501],pointers[505],pointers[550],pointers[502],pointers[506],pointers[551],pointers[503],pointers[507],pointers[552]};clear_draws();
 CHECK(render_mirror_terrain_row(game_screen,16,33,all_row,MIRROR_NORMAL)==4061&&draws==10&&traces==10&&!suppress);
 const unsigned all_ids[]={188,186,189,187,198,196,181,199,197,121};
 const unsigned all_slots[]={359,363,360,364,361,365,349,362,366,272};
 const int all_xs[]={16,64,88,112,160,184,208,232,256,280};
 for(unsigned i=0;i<10;i++)CHECK(draw_ids[i]==all_ids[i]&&draw_slots[i]==all_slots[i]&&draw_x[i]==all_xs[i]&&draw_y[i]==33&&!draw_lower[i]&&!draw_cap[i]&&!draw_forest[i]);
 for(int policy_case=POLICY_ABSENT;policy_case<=POLICY_VALID;policy_case++) {
  reset("canonical8",policy_case);for(unsigned s=0;s<128;s++){mapSh[0][s]=211;mapSh[1][s]=41;mapSh[2][s]=mechanical_ids[s%MECHANICAL_COUNT];}run_loader();
  CHECK(source_attempts==213&&terrain_source_count==TERRAIN_SOURCE_CAPACITY&&!forest_registry_ok);preflight();
  for(unsigned s=0;s<70;s++)CHECK(draw_pointer(megaData3.shapes[s].sh,MIRROR_NORMAL)==1&&draw_ids[0]==mechanical_ids[s%MECHANICAL_COUNT]);
  for(unsigned s=0;s<72;s++)CHECK(draw_pointer(megaData1.shapes[s].sh,MIRROR_NORMAL)==(unsigned)(policy_case==POLICY_ABSENT&&s<52));
 }
}
