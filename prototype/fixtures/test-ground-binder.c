#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
typedef uint8_t Uint8;
typedef struct {int pitch;} SDL_Surface;
enum {ASSET_NEWSH2=101,ASSET_TALON_BANK=109,ASSET_EXPLOSION=106,ASSET_SHAPESZ=201};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#include "production-types.inc"
static unsigned int terrain_source_count,game_probe_scene_assets=2;
static char terrain_file;
static bool active=true,suppress,game_probe_missing,game_probe_invalid;
static const char *reject_reason,*game_probe_assets=".";
static int game_probe_density=8;
static SDL_Surface screen={320},*game_screen=&screen;
static unsigned int draws,traces,last_index;
static void render_mirror_reset_banking(void){}
static void render_mirror_unsupported(const char *why){fprintf(stderr,"Unexpected: %s\n",why);abort();}
static bool draw_asset(int x,int y,Asset*a,int style,void*part)
{(void)x;(void)y;(void)style;(void)part;assert(a->valid);assert(a->w==24&&a->h==28&&a->anchor_x==0&&a->anchor_y==0&&a->density==8);draws++;last_index=a->index;suppress=true;return true;}
static void game_probe_scene_draw(int role,unsigned int id,int x,int y,int part,int style,bool mirrored)
{(void)x;(void)y;(void)part;(void)style;(void)mirrored;assert(role==201);traces++;last_index=id;}
#include "production-helpers.inc"
static const unsigned int ids[]={99,100,106,107,109,110,118,119,120};
static const unsigned int old_ids[]={101,37,57,49,50,321,322,331,332};
static const int old_slots[]={10,11,12,13,14,19,20,21,22};
static unsigned int checks;
static Uint8 bank[600];
static void reset(void)
{for(unsigned int i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);}memset(assets,0,sizeof(assets));draws=traces=0;active=true;game_probe_missing=game_probe_invalid=false;game_probe_assets=".";game_probe_density=8;game_probe_scene_assets=2;reject_reason=NULL;suppress=false;render_mirror_map_begin('Z');}
static bool member(unsigned int id,const unsigned int *set,size_t n)
{for(size_t i=0;i<n;i++)if(id==set[i])return true;return false;}
static void write_hda(unsigned int id,int bad)
{char filename[80];snprintf(filename,sizeof(filename),"terrain-shapesz-%u-8.hda",id);FILE*f=fopen(filename,"wb");assert(f);assert(fwrite("HDR1",1,4,f)==4);uint32_t words[]={2010000+id,8,24,28,0,0};if(bad>=0&&bad<6)words[bad]++;for(int i=0;i<6;i++)for(int b=0;b<4;b++)assert(fputc((words[i]>>(8*b))&255,f)!=EOF);for(int i=0;i<192*224;i++){assert(fputc(id&255,f)!=EOF);assert(fputc(47,f)!=EOF);assert(fputc(19,f)!=EOF);assert(fputc(255,f)!=EOF);}if(bad==6)assert(fputc(0,f)!=EOF);assert(!fclose(f));}
static void remove_hda(unsigned int id)
{char filename[80];snprintf(filename,sizeof(filename),"terrain-shapesz-%u-8.hda",id);assert(!unlink(filename));}
static unsigned int draw_one(unsigned int id,int style)
{Uint8*map[12]={bank+id};draws=traces=0;unsigned int result=render_mirror_terrain_row(game_screen,0,0,map,style);checks++;return result;}
int main(void)
{
 assert(sizeof(assets)/sizeof(*assets)==235);assert(sizeof(terrain_sources)/sizeof(*terrain_sources)==100);
 for(unsigned int id=0;id<600;id++) {int expected=-1;for(int j=0;j<9;j++)if(id==ids[j])expected=201+j;assert(ground_terrain_slot(id)==expected);checks++;}
 for(unsigned int layer=0;layer<5;layer++)for(unsigned int id=0;id<600;id++) {
  reset();render_mirror_bind_terrain(layer,id,bank+id);bool accepted=(layer==1&&(plateau_terrain_slot(id)>=0||member(id,ids,9)||member(id,old_ids,9)))||(layer==2&&((id>=41&&id<=45)||(id>=51&&id<=55)||(id>=61&&id<=65)));assert(terrain_source_count==(unsigned int)accepted);checks++;
 }
 for(int b=0;b<256;b++)if(b!='z'&&b!='Z')for(unsigned int j=0;j<9;j++) {reset();render_mirror_map_begin((char)b);render_mirror_bind_terrain(1,ids[j],bank+ids[j]);assert(!terrain_source_count);checks++;}
 /* Missing assets neither replace the tile nor add draw traces. */
 for(int j=0;j<9;j++){reset();render_mirror_bind_terrain(1,ids[j],bank+ids[j]);assert(!draw_one(ids[j],MIRROR_NORMAL));assert(!draws&&!traces);assert(assets[201+j].initialized&&!assets[201+j].valid);}
 /* All contract words and trailing bytes reject, independently for all nine. */
 for(int bad=0;bad<7;bad++)for(int j=0;j<9;j++) {reset();write_hda(ids[j],bad);render_mirror_bind_terrain(1,ids[j],bank+ids[j]);assert(!draw_one(ids[j],MIRROR_NORMAL));assert(!draws&&!traces);remove_hda(ids[j]);}
 /* Valid authored contract takes the existing renderer route at original style. */
 for(int j=0;j<9;j++)write_hda(ids[j],-1);
 for(int j=0;j<9;j++)for(int style=0;style<3;style++){reset();render_mirror_bind_terrain(1,ids[j],bank+ids[j]);assert(draw_one(ids[j],style)==1);assert(draws==1&&traces==1&&last_index==ids[j]);assert(assets[201+j].valid&&!suppress);}
 /* Each missing member falls back independently; the remaining eight work. */
 for(int missing=0;missing<9;missing++){remove_hda(ids[missing]);reset();for(int j=0;j<9;j++)render_mirror_bind_terrain(1,ids[j],bank+ids[j]);for(int j=0;j<9;j++){assert(draw_one(ids[j],MIRROR_NORMAL)==(unsigned int)(j!=missing));assert(draws==(unsigned int)(j!=missing)&&traces==(unsigned int)(j!=missing));}write_hda(ids[missing],-1);}
 for(int j=0;j<9;j++)remove_hda(ids[j]);
 /* Existing nine ground and fifteen cloud slots remain exactly where they were. */
 for(int j=0;j<9;j++){reset();write_hda(old_ids[j],-1);render_mirror_bind_terrain(1,old_ids[j],bank+old_ids[j]);assert(draw_one(old_ids[j],MIRROR_NORMAL)==1);assert(assets[old_slots[j]].valid);remove_hda(old_ids[j]);}
 for(unsigned int id=41;id<=65;id++)if(id%10>=1&&id%10<=5){reset();write_hda(id,-1);int expected=id<=45?186+(int)id-41:id<=55?191+(int)id-51:196+(int)id-61;assert(cloud_terrain_slot(id)==expected);render_mirror_bind_terrain(2,id,bank+id);assert(!draw_one(id,MIRROR_BLEND));assert(!draws&&!traces);assert(draw_one(id,MIRROR_NORMAL)==1);assert(assets[expected].valid);remove_hda(id);}
 /* Defensive lookup must not alias unknown IDs onto the existing ID332 slot. */
 reset();terrain_sources[0].data=bank+98;terrain_sources[0].id=98;terrain_source_count=1;assert(!draw_one(98,MIRROR_NORMAL));assert(!draws&&!traces&&!assets[22].initialized);
 /* Both exact registry capacity and over-capacity writes stay bounded. */
 reset();for(int i=0;i<600;i++)render_mirror_bind_terrain(1,99,bank+i);assert(terrain_source_count==100);checks++;
 reset();printf("PASS: %u checks; finite IDs/layers/banks; exact slots and capacity; all-six-header-word/trailing-byte rejection; missing-all/each; existing ground/cloud unchanged.\n",checks);return 0;
}
