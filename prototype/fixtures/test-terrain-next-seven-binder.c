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
#include "original-masks.inc"
static unsigned int terrain_source_count,game_probe_scene_assets=2;
static char terrain_file;
static bool active=true,suppress,game_probe_missing,game_probe_invalid;
static const char *reject_reason,*game_probe_assets=".";
static int game_probe_density=8;
static SDL_Surface screen={320},*game_screen=&screen;
static unsigned int draws,traces,last_index,checks;
static unsigned int draw_ids[64],trace_ids[64];
static int draw_x[64],trace_x[64],draw_y[64],trace_y[64];
static unsigned int rejected_layouts;
static int last_style;
static bool actual_mode,actual_all_mode;
static Uint8 actual_all_rgba[59][192*224*4];
static unsigned int actual_all_ids[59];
static unsigned actual_all_index(unsigned id){for(unsigned i=0;i<59;i++)if(actual_all_ids[i]==id)return i;assert(!"unknown actual terrain");return 0;}
#define CHECK(x) do { assert(x); checks++; } while(0)

static Uint8 actual_rgba[9][192*224*4];
static void load_actual(void)
{
 for(int i=0;i<9;i++){
  char name[40];snprintf(name,sizeof(name),"actual-%d.rgba",(int[]){111,114,113,341,342,343,351,352,353}[i]);
  FILE *f=fopen(name,"rb");assert(f);CHECK(fread(actual_rgba[i],1,sizeof(actual_rgba[i]),f)==sizeof(actual_rgba[i]));CHECK(fgetc(f)==EOF);CHECK(!fclose(f));
 }
}

static void render_mirror_reset_banking(void){}
static void render_mirror_unsupported(const char *why){CHECK(!strcmp(why,"terrain-row-outside-linear-layout"));rejected_layouts++;}
static int actual_index(unsigned int id){const unsigned int ids[]={111,114,113,341,342,343,351,352,353};for(int j=0;j<9;j++)if(id==ids[j])return j;return -1;}
static unsigned char expected_alpha(unsigned int id,int i) {
 int j=actual_index(id);if(j<0)return 255;
 if(actual_mode)return actual_rgba[j][4*i+3];
 int x=i%192,y=i/192;
 if(!original_masks[j][(y/8)*24+x/8])return 0;
 return x>7&&x<184&&y>7&&y<216&&((x+y)%3==0)?128:255;
}
static bool draw_asset(int x,int y,Asset*a,int style,void*part)
{
 (void)x;(void)y;(void)part;CHECK(a->valid);
 CHECK(a->w==24&&a->h==28&&a->anchor_x==0&&a->anchor_y==0&&a->density==8);
 if(actual_all_mode){CHECK(memcmp(a->rgba,actual_all_rgba[actual_all_index((unsigned)a->index)],192*224*4)==0);}
 else for(int i=0;i<192*224;i++) {
  unsigned char alpha=expected_alpha((unsigned int)a->index,i);
  CHECK(a->rgba[4*i+3]==alpha);
  if(actual_mode) { for(int c=0;c<4;c++)CHECK(a->rgba[4*i+c]==actual_rgba[actual_index((unsigned)a->index)][4*i+c]); continue; }
  CHECK(a->rgba[4*i]==(alpha?(a->index&255):0));
  CHECK(a->rgba[4*i+1]==(alpha?47:0));CHECK(a->rgba[4*i+2]==(alpha?19:0));
 }
 CHECK(draws<64);draw_ids[draws]=(unsigned)a->index;draw_x[draws]=x;draw_y[draws]=y;draws++;last_index=a->index;last_style=style;suppress=true;return true;
}
static void game_probe_scene_draw(int role,unsigned int id,int x,int y,int part,int style,bool mirrored)
{(void)x;(void)y;(void)part;(void)style;(void)mirrored;CHECK(role==201);CHECK(traces<64);trace_ids[traces]=id;trace_x[traces]=x;trace_y[traces]=y;CHECK(part==0&&mirrored);traces++;last_index=id;}
#include "production-helpers.inc"
static const unsigned int ids[]={111,114,113,341,342,343,351,352,353};
static const int slots[]={241,242,246,247,248,249,250,251,252};
static const unsigned int road_ids[]={36,39,40,46,48,56,58,38,47};
static const int road_slots[]={220,221,222,223,224,225,226,235,236};
static const unsigned int underlay_ids[]={323,324,333,334};
static const unsigned int plateau_ids[]={96,97,98,108};
static const unsigned int ground_ids[]={99,100,106,107,109,110,118,119,120};
static const unsigned int old_ids[]={101,37,57,49,50,321,322,331,332};
static const int old_slots[]={10,11,12,13,14,19,20,21,22};
static Uint8 bank[600];
static void reset(void)
{for(unsigned int i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);memset(assets,0,sizeof(assets));draws=traces=0;active=true;game_probe_missing=game_probe_invalid=false;game_probe_assets=".";game_probe_density=8;game_probe_scene_assets=2;reject_reason=NULL;suppress=false;render_mirror_map_begin('Z');}
static bool member(unsigned int id,const unsigned int *set,size_t n)
{for(size_t i=0;i<n;i++)if(id==set[i])return true;return false;}
static void write_hda(unsigned int id,int bad)
{
 char filename[80];snprintf(filename,sizeof(filename),"terrain-shapesz-%u-8.hda",id);FILE*f=fopen(filename,"wb");assert(f);
 if(bad>=10){unsigned char header[28]={'H','D','R','1'};uint32_t values[]={2010000+id,8,24,28,0,0};for(int h=0;h<6;h++)for(int b=0;b<4;b++)header[4+h*4+b]=(values[h]>>(8*b))&255;CHECK(fwrite(header,1,(size_t)(bad-10),f)==(size_t)(bad-10));CHECK(!fclose(f));return;}
 assert(fwrite(bad==7?"BAD1":"HDR1",1,4,f)==4);uint32_t words[]={2010000+id,8,24,28,0,0};if(bad>=0&&bad<6)words[bad]++;
 for(int i=0;i<6;i++)for(int b=0;b<4;b++)assert(fputc((words[i]>>(8*b))&255,f)!=EOF);
 int count=bad==8?0:bad==9?192*224-1:192*224;
 for(int i=0;i<count;i++){unsigned char alpha=expected_alpha(id,i);assert(fputc(alpha?(id&255):0,f)!=EOF);assert(fputc(alpha?47:0,f)!=EOF);assert(fputc(alpha?19:0,f)!=EOF);assert(fputc(alpha,f)!=EOF);}
 if(bad==6)assert(fputc(0,f)!=EOF);
 assert(!fclose(f));
}
static void remove_hda(unsigned int id)
{char filename[80];snprintf(filename,sizeof(filename),"terrain-shapesz-%u-8.hda",id);assert(!unlink(filename));}
static unsigned int draw_one(unsigned int id,int style)
{Uint8*map[12]={bank+id};draws=traces=0;return render_mirror_terrain_row(game_screen,0,0,map,style);}
static bool cloud(unsigned int id)
{return (id>=41&&id<=45)||(id>=51&&id<=55)||(id>=61&&id<=65);}
static void nonterrain_untouched(void)
{CHECK(!assets[218].initialized&&!assets[219].initialized);for(int i=231;i<=234;i++)CHECK(!assets[i].initialized);for(int i=243;i<=245;i++)CHECK(!assets[i].initialized);}
int main(void)
{
 load_actual();
 CHECK(sizeof(assets)/sizeof(*assets)==253);CHECK(sizeof(terrain_sources)/sizeof(*terrain_sources)==122);
 for(unsigned int id=0;id<600;id++) {
  int e=-1;for(int j=0;j<3;j++)if(id==ids[j])e=slots[j];CHECK(terrain_holes_slot(id)==e);
  e=-1;for(int j=3;j<9;j++)if(id==ids[j])e=slots[j];CHECK(stone_foundation_slot(id)==e);
  e=-1;for(int j=0;j<9;j++)if(id==road_ids[j])e=road_slots[j];CHECK(road_terrain_slot(id)==e);
  e=-1;for(int j=0;j<4;j++)if(id==underlay_ids[j])e=237+j;CHECK(underlay_terrain_slot(id)==e);
  e=-1;for(int j=0;j<9;j++)if(id==ground_ids[j])e=201+j;CHECK(ground_terrain_slot(id)==e);
 }
 for(unsigned int layer=0;layer<5;layer++)for(unsigned int id=0;id<600;id++){
  reset();render_mirror_bind_terrain(layer,id,bank+id);
  bool accepted=(layer==1&&(id==113||id==341||id==342||id==343||id==351||id==352||id==353||member(id,ids,9)||member(id,road_ids,9)||member(id,underlay_ids,4)||member(id,plateau_ids,4)||member(id,ground_ids,9)||member(id,old_ids,9)))||(layer==2&&cloud(id));
  CHECK(terrain_source_count==(unsigned int)accepted);nonterrain_untouched();
 }
 for(int b=0;b<256;b++)if(b!='z'&&b!='Z')for(unsigned int j=0;j<9;j++){reset();render_mirror_map_begin((char)b);render_mirror_bind_terrain(1,ids[j],bank+ids[j]);CHECK(!terrain_source_count);}
 reset();for(int j=0;j<9;j++)render_mirror_bind_terrain(1,ids[j],bank+ids[j]);
 for(int j=0;j<9;j++){CHECK(!draw_one(ids[j],MIRROR_NORMAL));CHECK(!draws&&!traces);CHECK(assets[slots[j]].initialized&&!assets[slots[j]].valid);nonterrain_untouched();}
 for(int bad=0;bad<38;bad++)for(int j=0;j<9;j++){reset();write_hda(ids[j],bad);render_mirror_bind_terrain(1,ids[j],bank+ids[j]);CHECK(!draw_one(ids[j],MIRROR_NORMAL));CHECK(!draws&&!traces);CHECK(assets[slots[j]].initialized&&!assets[slots[j]].valid);nonterrain_untouched();remove_hda(ids[j]);}
 for(int j=0;j<9;j++)write_hda(ids[j],-1);
 for(int j=0;j<9;j++)for(int style=0;style<3;style++){reset();render_mirror_bind_terrain(1,ids[j],bank+ids[j]);CHECK(draw_one(ids[j],style)==1);CHECK(draws==1&&traces==1&&last_index==ids[j]&&last_style==style);CHECK(assets[slots[j]].valid&&!suppress);nonterrain_untouched();}
 for(int missing=0;missing<9;missing++){remove_hda(ids[missing]);reset();for(int j=0;j<9;j++)render_mirror_bind_terrain(1,ids[j],bank+ids[j]);for(int j=0;j<9;j++){CHECK(draw_one(ids[j],MIRROR_NORMAL)==(unsigned int)(j!=missing));CHECK(draws==(unsigned int)(j!=missing)&&traces==(unsigned int)(j!=missing));nonterrain_untouched();}write_hda(ids[missing],-1);}
 for(int flag=0;flag<7;flag++)for(int j=0;j<9;j++){
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
 for(int j=0;j<9;j++)remove_hda(ids[j]);
 for(int j=0;j<9;j++){reset();write_hda(old_ids[j],-1);render_mirror_bind_terrain(1,old_ids[j],bank+old_ids[j]);CHECK(draw_one(old_ids[j],MIRROR_NORMAL)==1);CHECK(assets[old_slots[j]].valid);nonterrain_untouched();remove_hda(old_ids[j]);}
 for(int j=0;j<9;j++){reset();write_hda(ground_ids[j],-1);render_mirror_bind_terrain(1,ground_ids[j],bank+ground_ids[j]);CHECK(draw_one(ground_ids[j],MIRROR_NORMAL)==1);CHECK(assets[201+j].valid);nonterrain_untouched();remove_hda(ground_ids[j]);}
 for(int j=0;j<4;j++){reset();write_hda(plateau_ids[j],-1);render_mirror_bind_terrain(1,plateau_ids[j],bank+plateau_ids[j]);CHECK(draw_one(plateau_ids[j],MIRROR_NORMAL)==1);CHECK(assets[227+j].valid);nonterrain_untouched();remove_hda(plateau_ids[j]);}
 for(int j=0;j<4;j++){reset();write_hda(underlay_ids[j],-1);render_mirror_bind_terrain(1,underlay_ids[j],bank+underlay_ids[j]);CHECK(draw_one(underlay_ids[j],MIRROR_NORMAL)==1);CHECK(assets[237+j].valid);nonterrain_untouched();remove_hda(underlay_ids[j]);}
 for(int j=0;j<9;j++){reset();write_hda(road_ids[j],-1);render_mirror_bind_terrain(1,road_ids[j],bank+road_ids[j]);CHECK(draw_one(road_ids[j],MIRROR_NORMAL)==1);CHECK(assets[road_slots[j]].valid);nonterrain_untouched();remove_hda(road_ids[j]);}
 for(unsigned int id=41;id<=65;id++)if(cloud(id)){reset();write_hda(id,-1);int expected=id<=45?186+(int)id-41:id<=55?191+(int)id-51:196+(int)id-61;CHECK(cloud_terrain_slot(id)==expected);render_mirror_bind_terrain(2,id,bank+id);CHECK(!draw_one(id,MIRROR_BLEND));CHECK(!draws&&!traces);CHECK(draw_one(id,MIRROR_NORMAL)==1);CHECK(assets[expected].valid);nonterrain_untouched();remove_hda(id);}
 for(unsigned int id=0;id<600;id++)if(id!=113&&id!=341&&id!=342&&id!=343&&id!=351&&id!=352&&id!=353&&!member(id,ids,9)&&!member(id,road_ids,9)&&!member(id,underlay_ids,4)&&!member(id,plateau_ids,4)&&!member(id,ground_ids,9)&&!member(id,old_ids,9)&&!cloud(id)){
  reset();terrain_sources[0].data=bank+id;terrain_sources[0].id=id;terrain_source_count=1;CHECK(!draw_one(id,MIRROR_NORMAL));CHECK(!draws&&!traces&&!assets[22].initialized);nonterrain_untouched();
 }
 reset();for(int i=0;i<600;i++)render_mirror_bind_terrain(1,111,bank+i);CHECK(terrain_source_count==122);nonterrain_untouched();

 /* A rejected member cannot suppress or alias any of the other eight tiles. */
 for(int j=0;j<9;j++)write_hda(ids[j],-1);
 for(int bad=0;bad<10;bad++)for(int broken=2;broken<9;broken++) {
  write_hda(ids[broken],bad);reset();
  for(int j=0;j<9;j++)render_mirror_bind_terrain(1,ids[j],bank+ids[j]);
  Uint8 *row[12]={0};for(int j=0;j<9;j++)row[j]=bank+ids[j];draws=traces=0;
  CHECK(render_mirror_terrain_row(game_screen,0,17,row,MIRROR_NORMAL)==(511u^(1u<<broken)));CHECK(draws==8&&traces==8&&!suppress);
  for(int j=0,k=0;j<9;j++)if(j!=broken){CHECK(draw_ids[k]==ids[j]&&trace_ids[k]==ids[j]);CHECK(draw_x[k]==24*j&&trace_x[k]==24*j&&draw_y[k]==17&&trace_y[k]==17);k++;}
  CHECK(assets[slots[broken]].initialized&&!assets[slots[broken]].valid);nonterrain_untouched();write_hda(ids[broken],-1);
 }
 for(int j=0;j<9;j++)remove_hda(ids[j]);
 /* Every accepted terrain asset resides simultaneously, with no cross-family aliases. */
 reset();
 const unsigned int combined_ids[]={101,37,57,49,50,321,322,331,332,99,100,106,107,109,110,118,119,120,96,97,98,108,323,324,333,334,36,39,40,46,48,56,58,38,47,41,42,43,44,45,51,52,53,54,55,61,62,63,64,65,111,114,113,341,342,343,351,352,353};
 const int combined_slots[]={10,11,12,13,14,19,20,21,22,201,202,203,204,205,206,207,208,209,227,228,229,230,237,238,239,240,220,221,222,223,224,225,226,235,236,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,241,242,246,247,248,249,250,251,252};
 CHECK(sizeof(combined_ids)/sizeof(*combined_ids)==59);
 for(unsigned j=0;j<59;j++){
  for(unsigned k=0;k<j;k++)CHECK(combined_slots[j]!=combined_slots[k]);
  write_hda(combined_ids[j],-1);render_mirror_bind_terrain(cloud(combined_ids[j])?2:1,combined_ids[j],bank+combined_ids[j]);
 }
 CHECK(terrain_source_count==59);
 for(unsigned j=0;j<59;j++)CHECK(draw_one(combined_ids[j],MIRROR_NORMAL)==1);
 for(unsigned j=0;j<59;j++){Asset *a=&assets[combined_slots[j]];CHECK(a->initialized&&a->valid&&a->bank==201&&a->index==(int)combined_ids[j]);}
 for(unsigned slot=0;slot<253;slot++){bool terrain=false;for(unsigned j=0;j<59;j++)if(slot==(unsigned)combined_slots[j])terrain=true;CHECK(assets[slot].initialized==terrain);}
 /* Rotated, reversed full/partial12-tile rows cover every accepted ID and every bit position. */
 const unsigned masks[]={4095,0,1,2048,0x555,0xaaa,3547,0x1ff};
 for(unsigned start=0;start<59;start++)for(int reverse=0;reverse<2;reverse++)for(int style=0;style<3;style++){
  unsigned selected_mask=masks[start%8],wanted=0,count=0;Uint8 *row[12];unsigned row_ids[12];
  for(int j=0;j<12;j++){row_ids[j]=combined_ids[(start+(reverse?11-j:j))%59];row[j]=(selected_mask&(1u<<j))?bank+row_ids[j]:(j%2?NULL:bank+112);if(row[j]&&(selected_mask&(1u<<j))&&!(cloud(row_ids[j])&&style==MIRROR_BLEND)){wanted|=1u<<j;count++;}}
  draws=traces=0;CHECK(render_mirror_terrain_row(game_screen,16,-13,row,style)==wanted);CHECK(draws==count&&traces==count&&!suppress);nonterrain_untouched();
  for(int j=0,k=0;j<12;j++)if(wanted&(1u<<j)){CHECK(draw_ids[k]==row_ids[j]&&trace_ids[k]==row_ids[j]);CHECK(draw_x[k]==16+24*j&&trace_x[k]==16+24*j&&draw_y[k]==-13&&trace_y[k]==-13);k++;}
 }
 /* Wrong surfaces and invalid linear row boundaries are fail-closed. */
 Uint8 *row[12]={bank+113};SDL_Surface other={320};draws=traces=0;
 CHECK(!render_mirror_terrain_row(&other,0,0,row,MIRROR_NORMAL));CHECK(!draws&&!traces);
 for(int x=-1;x<=33;x+=34){CHECK(!render_mirror_terrain_row(game_screen,x,0,row,MIRROR_NORMAL));CHECK(!draws&&!traces);}CHECK(rejected_layouts==2);
 for(unsigned j=0;j<59;j++)remove_hda(combined_ids[j]);
 reset();

 /* Repeat simultaneous residency with every real accepted terrain payload. */
 reset();actual_all_mode=true;
 for(unsigned j=0;j<59;j++){
  actual_all_ids[j]=combined_ids[j];char src[80],dst[80];snprintf(src,sizeof(src),"actual-all-%u.rgba",combined_ids[j]);FILE *f=fopen(src,"rb");CHECK(f);CHECK(fread(actual_all_rgba[j],1,sizeof(actual_all_rgba[j]),f)==sizeof(actual_all_rgba[j]));CHECK(fgetc(f)==EOF);CHECK(!fclose(f));
  snprintf(src,sizeof(src),"actual-all-%u.hda",combined_ids[j]);snprintf(dst,sizeof(dst),"terrain-shapesz-%u-8.hda",combined_ids[j]);FILE *in=fopen(src,"rb"),*out=fopen(dst,"wb");CHECK(in&&out);int byte;while((byte=fgetc(in))!=EOF)CHECK(fputc(byte,out)!=EOF);CHECK(!fclose(in));CHECK(!fclose(out));
  render_mirror_bind_terrain(cloud(combined_ids[j])?2:1,combined_ids[j],bank+combined_ids[j]);
 }
 CHECK(terrain_source_count==59);
 for(unsigned j=0;j<59;j++)CHECK(draw_one(combined_ids[j],MIRROR_NORMAL)==1);
 for(unsigned slot=0;slot<253;slot++){bool terrain=false;for(unsigned j=0;j<59;j++)if(slot==(unsigned)combined_slots[j])terrain=true;CHECK(assets[slot].initialized==terrain);}
 for(unsigned start=0;start<59;start++)for(int style=0;style<3;style++){
  unsigned wanted=0,count=0,mask=masks[start%8];Uint8 *row[12];unsigned row_ids[12];
  for(int j=0;j<12;j++){row_ids[j]=combined_ids[(start+j)%59];row[j]=(mask&(1u<<j))?bank+row_ids[j]:NULL;if(row[j]&&!(cloud(row_ids[j])&&style==MIRROR_BLEND)){wanted|=1u<<j;count++;}}
  draws=traces=0;CHECK(render_mirror_terrain_row(game_screen,32,23,row,style)==wanted);CHECK(draws==count&&traces==count&&!suppress);nonterrain_untouched();
  for(int j=0,k=0;j<12;j++)if(wanted&(1u<<j)){CHECK(draw_ids[k]==row_ids[j]&&trace_ids[k]==row_ids[j]);CHECK(draw_x[k]==32+24*j&&trace_x[k]==32+24*j&&draw_y[k]==23&&trace_y[k]==23);k++;}
 }
 for(unsigned j=0;j<59;j++)remove_hda(combined_ids[j]);
 actual_all_mode=false;reset();
 /* The existing8x→4x fallback loads the same finite headers without aliasing. */
 for(int j=2;j<9;j++){
  char name[80];snprintf(name,sizeof(name),"terrain-shapesz-%u-4.hda",ids[j]);FILE *f=fopen(name,"wb");CHECK(f);CHECK(fwrite("HDR1",1,4,f)==4);uint32_t words[]={2010000+ids[j],4,24,28,0,0};for(int h=0;h<6;h++)for(int b=0;b<4;b++)CHECK(fputc((words[h]>>(8*b))&255,f)!=EOF);for(int k=0;k<96*112;k++)for(int c=0;c<4;c++)CHECK(fputc(c==3?255:(int)(ids[j]&255),f)!=EOF);CHECK(!fclose(f));
  Asset *a=scene_asset(slots[j],ASSET_SHAPESZ,(int)ids[j],0,0);CHECK(a&&a->valid&&a->density==4&&a->bank==201&&a->index==(int)ids[j]);CHECK(a->rgba[0]==(ids[j]&255));CHECK(!unlink(name));
 }
 reset();


 /* Transport every actual selected RGBA byte through the real loader. */
 for(int j=0;j<9;j++){
  reset();actual_mode=true;char src[40],dst[80];snprintf(src,sizeof(src),"actual-%u.hda",ids[j]);snprintf(dst,sizeof(dst),"terrain-shapesz-%u-8.hda",ids[j]);
  FILE *in=fopen(src,"rb"),*out=fopen(dst,"wb");CHECK(in&&out);int byte;while((byte=fgetc(in))!=EOF)CHECK(fputc(byte,out)!=EOF);CHECK(!fclose(in));CHECK(!fclose(out));
  render_mirror_bind_terrain(1,ids[j],bank+ids[j]);CHECK(draw_one(ids[j],MIRROR_NORMAL)==1);CHECK(assets[slots[j]].valid);remove_hda(ids[j]);actual_mode=false;
 }
 reset();printf("PASS: %u assertions; finite111/114/113 and stone341/342/343/351/352/353 IDs slots241/242/246..252; exact banks/layers; registry122; binary holes, synthetic fractional alpha and actual selected RGBA transported unchanged; missing-all/each, malformed magic/header/payload and inherited disable guards; accepted road/underlay/ground/plateau/cloud slots unchanged; exhaustive unknown-ID rejection; all28 short-header lengths; malformed-member isolation;59 simultaneous terrain assets;354 full/partial row cases with exact ordering/bitmasks/coordinates; actual59-terrain byte-exact simultaneous residency and177 additional full/partial rows;7 inherited4x fallback cases; wrong surface and boundary guards; craft slots243..245 untouched.\n",checks);return 0;
}
