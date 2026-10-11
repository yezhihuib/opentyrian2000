#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
/* Test-only no-delete retention: rename generated fixture files out of the load path. */
static int retain_removed_fixture(const char *path) {
 static unsigned serial;
 char saved[4096];
 if (snprintf(saved, sizeof(saved), "%s.retained-%u", path, ++serial) >= (int)sizeof(saved)) return -1;
 return rename(path, saved);
}
#define remove retain_removed_fixture
#define unlink retain_removed_fixture
typedef uint8_t Uint8;
typedef struct {int pitch;} SDL_Surface;
enum {ASSET_NEWSH2=101,ASSET_TALON_BANK=109,ASSET_NEWSHE=110,ASSET_EXPLOSION=106,ASSET_SHAPESZ=201};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#include "production-types.inc"
static unsigned int terrain_source_count,game_probe_scene_assets=2;
static char terrain_file;
static bool active=true,suppress,game_probe_missing,game_probe_invalid;
static const char *reject_reason,*game_probe_assets=".";
static int game_probe_density=8;
static SDL_Surface screen={320},*game_screen=&screen;
static unsigned int draws,traces,last_index,checks;
static int last_style;
#define CHECK(x) do { assert(x); checks++; } while(0)
static void render_mirror_reset_banking(void){}
static void render_mirror_unsupported(const char *why){fprintf(stderr,"Unexpected: %s\n",why);abort();}
static bool draw_asset(int x,int y,Asset*a,int style,void*part)
{(void)x;(void)y;(void)part;CHECK(a->valid);CHECK(a->w==24&&a->h==28&&a->anchor_x==0&&a->anchor_y==0&&a->density==8);draws++;last_index=a->index;last_style=style;suppress=true;return true;}
static void game_probe_scene_draw(int role,unsigned int id,int x,int y,int part,int style,bool mirrored)
{(void)x;(void)y;(void)part;(void)style;(void)mirrored;CHECK(role==201);traces++;last_index=id;}
#include "production-helpers.inc"
static const unsigned int ids[]={323,324,333,334};
static const unsigned int ground_ids[]={99,100,106,107,109,110,118,119,120};
static const unsigned int road_ids[]={36,39,40,46,48,56,58,38,47};
static const unsigned int old_ids[]={101,37,57,49,50,321,322,331,332};
static const int old_slots[]={10,11,12,13,14,19,20,21,22};
static const unsigned int purple_ids[]={150,156,157,158,159,160,166,168,169,170,176,177,178};
static const unsigned int gray_ids[]={121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154};
static Uint8 bank[600];
static void reset(void)
{for(unsigned int i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);memset(assets,0,sizeof(assets));draws=traces=0;active=true;game_probe_missing=game_probe_invalid=false;game_probe_assets=".";game_probe_density=8;game_probe_scene_assets=2;reject_reason=NULL;suppress=false;render_mirror_map_begin('Z');}
static bool member(unsigned int id,const unsigned int *set,size_t n)
{for(size_t i=0;i<n;i++)if(id==set[i])return true;return false;}
static void write_hda(unsigned int id,int bad)
{char filename[80];snprintf(filename,sizeof(filename),"terrain-shapesz-%u-8.hda",id);FILE*f=fopen(filename,"wb");assert(f);assert(fwrite(bad==7?"BAD1":"HDR1",1,4,f)==4);uint32_t words[]={2010000+id,8,24,28,0,0};if(bad>=0&&bad<6)words[bad]++;for(int i=0;i<6;i++)for(int b=0;b<4;b++)assert(fputc((words[i]>>(8*b))&255,f)!=EOF);int count=bad==8?0:bad==9?192*224-1:192*224;for(int i=0;i<count;i++){assert(fputc(id&255,f)!=EOF);assert(fputc(47,f)!=EOF);assert(fputc(19,f)!=EOF);assert(fputc(255,f)!=EOF);}if(bad==6)assert(fputc(0,f)!=EOF);assert(!fclose(f));}
static void remove_hda(unsigned int id)
{char filename[80];snprintf(filename,sizeof(filename),"terrain-shapesz-%u-8.hda",id);assert(!unlink(filename));}
static unsigned int draw_one(unsigned int id,int style)
{Uint8*map[12]={bank+id};draws=traces=0;return render_mirror_terrain_row(game_screen,0,0,map,style);}
static bool cloud(unsigned int id)
{return (id>=41&&id<=45)||(id>=51&&id<=55)||(id>=61&&id<=65);}
static void nonterrain_untouched(void)
{CHECK(!assets[218].initialized&&!assets[219].initialized);for(int i=231;i<=234;i++)CHECK(!assets[i].initialized);}
int main(void)
{
 CHECK(sizeof(assets)/sizeof(*assets)==312);CHECK(sizeof(terrain_sources)/sizeof(*terrain_sources)==153);
 for(unsigned int id=0;id<600;id++){int expected=-1;for(int j=0;j<4;j++)if(id==ids[j])expected=237+j;CHECK(underlay_terrain_slot(id)==expected);}
 for(unsigned int id=0;id<600;id++){int expected=-1;for(int j=0;j<9;j++)if(id==ground_ids[j])expected=201+j;CHECK(ground_terrain_slot(id)==expected);}
 for(unsigned int layer=0;layer<5;layer++)for(unsigned int id=0;id<600;id++){
  reset();render_mirror_bind_terrain(layer,id,bank+id);bool accepted=(layer==1&&(id==111||id==114||id==113||id==341||id==342||id==343||id==351||id==352||id==353||member(id,road_ids,9)||member(id,ids,4)||member(id,ground_ids,9)||member(id,old_ids,9)||id==96||id==97||id==98||id==108))||(layer==2&&cloud(id))||(layer==3&&(member(id,gray_ids,18)||member(id,purple_ids,13)));CHECK(terrain_source_count==(unsigned int)accepted);nonterrain_untouched();
 }
 for(int b=0;b<256;b++)if(b!='z'&&b!='Z')for(unsigned int j=0;j<4;j++){reset();render_mirror_map_begin((char)b);render_mirror_bind_terrain(1,ids[j],bank+ids[j]);CHECK(!terrain_source_count);}
 /* Missing resources preserve original path and original scene-draw log. */
 reset();for(int j=0;j<4;j++)render_mirror_bind_terrain(1,ids[j],bank+ids[j]);
 for(int j=0;j<4;j++){CHECK(!draw_one(ids[j],MIRROR_NORMAL));CHECK(!draws&&!traces);CHECK(assets[237+j].initialized&&!assets[237+j].valid);nonterrain_untouched();}
 /* All header words, magic, empty/truncated and trailing payload reject. */
 for(int bad=0;bad<10;bad++)for(int j=0;j<4;j++){reset();write_hda(ids[j],bad);render_mirror_bind_terrain(1,ids[j],bank+ids[j]);CHECK(!draw_one(ids[j],MIRROR_NORMAL));CHECK(!draws&&!traces);CHECK(assets[237+j].initialized&&!assets[237+j].valid);nonterrain_untouched();remove_hda(ids[j]);}
 for(int j=0;j<4;j++)write_hda(ids[j],-1);
 for(int j=0;j<4;j++)for(int style=0;style<3;style++){reset();render_mirror_bind_terrain(1,ids[j],bank+ids[j]);CHECK(draw_one(ids[j],style)==1);CHECK(draws==1&&traces==1&&last_index==ids[j]&&last_style==style);CHECK(assets[237+j].valid&&!suppress);nonterrain_untouched();}
 /* Each absent member falls back independently while three remaining members work. */
 for(int missing=0;missing<4;missing++){remove_hda(ids[missing]);reset();for(int j=0;j<4;j++)render_mirror_bind_terrain(1,ids[j],bank+ids[j]);for(int j=0;j<4;j++){CHECK(draw_one(ids[j],MIRROR_NORMAL)==(unsigned int)(j!=missing));CHECK(draws==(unsigned int)(j!=missing)&&traces==(unsigned int)(j!=missing));nonterrain_untouched();}write_hda(ids[missing],-1);}
 /* The inherited loader/renderer disable guards do not leak traces. */
 for(int flag=0;flag<7;flag++)for(int j=0;j<4;j++){
  reset();render_mirror_bind_terrain(1,ids[j],bank+ids[j]);
  if(flag==0)game_probe_missing=true;
  if(flag==1)game_probe_invalid=true;
  if(flag==2)game_probe_density=1;
  if(flag==3)game_probe_assets=NULL;
  if(flag==4)game_probe_scene_assets=0;
  if(flag==5)active=false;
  if(flag==6)reject_reason="test";
  CHECK(!draw_one(ids[j],MIRROR_NORMAL));CHECK(!draws&&!traces);nonterrain_untouched();
 }
 for(int j=0;j<4;j++)remove_hda(ids[j]);
 /* Existing ground, plateau and fifteen cloud IDs preserve exact accepted slots. */
 for(int j=0;j<9;j++){reset();write_hda(old_ids[j],-1);render_mirror_bind_terrain(1,old_ids[j],bank+old_ids[j]);CHECK(draw_one(old_ids[j],MIRROR_NORMAL)==1);CHECK(assets[old_slots[j]].valid);nonterrain_untouched();remove_hda(old_ids[j]);}
 for(int j=0;j<9;j++){reset();write_hda(ground_ids[j],-1);render_mirror_bind_terrain(1,ground_ids[j],bank+ground_ids[j]);CHECK(draw_one(ground_ids[j],MIRROR_NORMAL)==1);CHECK(assets[201+j].valid);nonterrain_untouched();remove_hda(ground_ids[j]);}
 for(unsigned int id=41;id<=65;id++)if(cloud(id)){reset();write_hda(id,-1);int expected=id<=45?186+(int)id-41:id<=55?191+(int)id-51:196+(int)id-61;CHECK(cloud_terrain_slot(id)==expected);render_mirror_bind_terrain(2,id,bank+id);CHECK(!draw_one(id,MIRROR_BLEND));CHECK(!draws&&!traces);CHECK(draw_one(id,MIRROR_NORMAL)==1);CHECK(assets[expected].valid);nonterrain_untouched();remove_hda(id);}
 /* Explicit new-family membership must not turn into a broad numeric range. */
 for(int j=0;j<18;j++){
  unsigned id=gray_ids[j];reset();write_hda(id,-1);render_mirror_bind_terrain(3,id,bank+id);
  CHECK(draw_one(id,MIRROR_NORMAL)==1);CHECK(assets[272+j].valid&&assets[272+j].bank==201&&assets[272+j].index==(int)id);
  CHECK(!draw_one(id,MIRROR_BLEND)&&!draws&&!traces);CHECK(!draw_one(id,MIRROR_SHADOW)&&!draws&&!traces);
  nonterrain_untouched();for(int slot=269;slot<=271;slot++)CHECK(!assets[slot].initialized);remove_hda(id);
 }
 /* Every unrecognized ID must not alias the old implicit ID332 fallback. */
 for(unsigned int id=0;id<600;id++)if(!member(id,gray_ids,18)&&id!=111&&id!=114&&id!=113&&id!=341&&id!=342&&id!=343&&id!=351&&id!=352&&id!=353&&!member(id,road_ids,9)&&!member(id,ids,4)&&!member(id,ground_ids,9)&&!member(id,old_ids,9)&&!cloud(id)&&id!=96&&id!=97&&id!=98&&id!=108){
  reset();terrain_sources[0].data=bank+id;terrain_sources[0].id=id;terrain_source_count=1;CHECK(!draw_one(id,MIRROR_NORMAL));CHECK(!draws&&!traces&&!assets[22].initialized);nonterrain_untouched();
 }
 reset();for(int i=0;i<600;i++)render_mirror_bind_terrain(1,96,bank+i);CHECK(terrain_source_count==153);nonterrain_untouched();
 reset();printf("PASS: %u checks; four exact physical underlay IDs/layers/banks; slots237–240 and untouched orb218–219/installation231–234; six header words/magic/payload rejection; missing-all/each; existing plateau/ground/cloud unchanged; exhaustive unknown ID332 rejection; registry153.\n",checks);return 0;
}
