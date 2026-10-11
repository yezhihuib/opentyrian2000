#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef struct { int pitch; } SDL_Surface;
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_EXPLOSION=106,ASSET_SHAPESZ=201};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#include "production-types.inc"
#include "original-map.inc"
#define CHECK(x) do { if(!(x)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x);abort();} ++checks; } while(0)
static unsigned long checks;
static unsigned terrain_source_count,game_probe_scene_assets=2;
static char terrain_file;
static bool active=true,suppress,game_probe_missing,game_probe_invalid,draw_success=true;
static const char *reject_reason,*game_probe_assets;
static int game_probe_density=8;
static SDL_Surface screen={320},*game_screen=&screen;
static unsigned draws,traces,rejected_layouts,bank_resets;
static unsigned draw_ids[12],trace_ids[12];
static int draw_x[12],draw_y[12],trace_style[12];
static bool trace_mirrored[12];
static char pack[4096];
static const char *root;
static const unsigned grass[]={66,67,69,76,78,79,80,89,90};
static const unsigned purple[]={150,156,157,158,159,160,166,168,169,170,176,177,178};
static const unsigned gray[]={121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154};
static const unsigned old[]={101,37,57,49,50,321,322,331,332,99,100,106,107,109,110,118,119,120,96,97,98,108,323,324,333,334,36,39,40,46,48,56,58,38,47,111,114,113,341,342,343,351,352,353};
static const int old_slots[]={10,11,12,13,14,19,20,21,22,201,202,203,204,205,206,207,208,209,227,228,229,230,237,238,239,240,220,221,222,223,224,225,226,235,236,241,242,246,247,248,249,250,251,252};
static const unsigned clouds[]={41,42,43,44,45,51,52,53,54,55,61,62,63,64,65};
static Uint8 bank[5][601][672];
static bool member(unsigned id,const unsigned *ids,unsigned n){for(unsigned i=0;i<n;i++)if(ids[i]==id)return true;return false;}
static bool accepted(unsigned layer,unsigned id){return (layer==1&&(member(id,old,44)||member(id,grass,9)))||(layer==2&&member(id,clouds,15))||(layer==3&&(member(id,gray,18)||member(id,purple,13)));}
static void render_mirror_reset_banking(void){bank_resets++;}
static void render_mirror_unsupported(const char *why){CHECK(!strcmp(why,"terrain-row-outside-linear-layout"));rejected_layouts++;}
static bool draw_asset(int x,int y,Asset *a,int style,void *part)
{
 CHECK(!part&&a->valid&&a->bank==201&&a->w==24&&a->h==28&&a->anchor_x==0&&a->anchor_y==0);
 CHECK(a->density==8||a->density==4);
 if(member((unsigned)a->index,gray,18))CHECK(style==MIRROR_NORMAL);
 const unsigned alpha[]={0,1,127,128,254,255};
 for(int ay=0;ay<28*a->density;ay++)for(int ax=0;ax<24*a->density;ax++){
  Uint8 *p=a->rgba+4*(ay*24*a->density+ax);
  CHECK(p[0]==(Uint8)(a->index+ax*3+ay));CHECK(p[1]==(Uint8)(a->index*3+ax+ay*5));
  CHECK(p[2]==(Uint8)(a->index*7+ax*11+ay));CHECK(p[3]==alpha[(ax+2*ay+a->index)%6]);
 }
 CHECK(draws<12);draw_ids[draws]=(unsigned)a->index;draw_x[draws]=x;draw_y[draws]=y;draws++;
 suppress=draw_success;return draw_success;
}
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{
 CHECK(role==201&&part==0&&traces<12);CHECK(draws==traces+1&&draw_ids[traces]==id&&draw_x[traces]==x&&draw_y[traces]==y);
 trace_ids[traces]=id;trace_style[traces]=style;trace_mirrored[traces]=mirrored;traces++;
}
#include "production-helpers.inc"
/* These exact loader loops are extracted from tyrian2.c, not reimplemented. */
typedef bool JE_boolean;
typedef Uint8 JE_DanCShape[672];
static uint16_t mapSh[3][128];
static struct {struct {Uint8 sh[672];unsigned fill;} shapes[72];} megaData1,megaData2,megaData3;
static Uint8 *ref[3][128];
static bool source_blank[600];
static unsigned source_index;
static void fread_bool_die(JE_boolean *out,FILE *file){(void)file;CHECK(source_index<600);*out=source_blank[source_index++];}
static void fread_u8_die(Uint8 *out,size_t n,FILE *file){(void)file;CHECK(n==672&&source_index>0);memset(out,(int)(source_index%254+1),n);}
static void asset_debug_bind_terrain(char file,unsigned layer,unsigned id,const Uint8 *data){CHECK(file=='Z'&&layer>=1&&layer<=3&&id>=1&&id<=600&&data);}
static void run_loader(void)
{
 Uint8 shape[672];int y,yy;FILE *shpFile=NULL;char char_shapeFile='Z';source_index=0;
 memset(ref,0,sizeof(ref));render_mirror_map_begin(char_shapeFile);
#include "production-loader.inc"
 CHECK(source_index==600);
}
static void reserved_untouched(void){for(unsigned i=269;i<=271;i++)CHECK(!assets[i].initialized);}
static void choose(const char *label){CHECK(snprintf(pack,sizeof(pack),"%s/%s",root,label)<(int)sizeof(pack));game_probe_assets=pack;}
static void clear_draws(void){draws=traces=0;suppress=false;}
static void reset(const char *label)
{
 for(unsigned i=0;i<321;i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));
 clear_draws();active=draw_success=true;game_probe_missing=game_probe_invalid=false;game_probe_density=8;game_probe_scene_assets=2;reject_reason=NULL;
 choose(label);render_mirror_map_begin('Z');
}
static unsigned draw_pointer(Uint8 *ptr,int style){Uint8 *row[12]={ptr};clear_draws();return render_mirror_terrain_row(game_screen,0,17,row,style);}
static void whitelist(void)
{
 CHECK(sizeof(assets)/sizeof(*assets)==321);CHECK(sizeof(terrain_sources)/sizeof(*terrain_sources)==162);
 for(unsigned id=0;id<=1000;id++){
  int expected=-1;for(unsigned j=0;j<18;j++)if(id==gray[j])expected=272+(int)j;
  CHECK(layer3_gray_slot(id)==expected);
 }
 CHECK(layer3_gray_slot(UINT_MAX)==-1);
 for(unsigned layer=0;layer<5;layer++)for(unsigned id=0;id<=600;id++){
  reset("full8");render_mirror_bind_terrain(layer,id,bank[layer][id]);
  CHECK(terrain_source_count==(unsigned)accepted(layer,id));
  if(terrain_source_count)CHECK(terrain_sources[0].id==id&&terrain_sources[0].data==bank[layer][id]);
  for(unsigned slot=0;slot<321;slot++)CHECK(!assets[slot].initialized);
 }
 for(unsigned byte=0;byte<256;byte++)for(unsigned j=0;j<18;j++){
  reset("full8");render_mirror_map_begin((char)byte);render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);
  CHECK(terrain_source_count==(unsigned)(byte=='Z'||byte=='z'));
 }
 /* Identical bytes or shared numeric IDs never replace a distinct source pointer. */
 reset("full8");for(unsigned j=0;j<18;j++)render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);
 for(unsigned layer=0;layer<5;layer++)if(layer!=3)for(unsigned j=0;j<18;j++){
  CHECK(!draw_pointer(bank[layer][gray[j]],MIRROR_NORMAL));CHECK(!draws&&!traces);
 }
 for(unsigned j=0;j<18;j++){CHECK(draw_pointer(bank[3][gray[j]],MIRROR_NORMAL)==1);CHECK(draws==1&&traces==1);reserved_untouched();}
 /* Null sources cannot match null map cells. */
 reset("full8");render_mirror_bind_terrain(3,121,NULL);CHECK(!draw_pointer(NULL,MIRROR_NORMAL));CHECK(!draws&&!traces);
}
static void guards(void)
{
 for(unsigned j=0;j<18;j++)for(int flag=0;flag<7;flag++){
  reset("full8");render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);
  if(flag==0)game_probe_missing=true;
  if(flag==1)game_probe_invalid=true;
  if(flag==2)game_probe_density=1;
  if(flag==3)game_probe_assets=NULL;
  if(flag==4)game_probe_scene_assets=0;
  if(flag==5)active=false;
  if(flag==6)reject_reason="test";
  CHECK(!draw_pointer(bank[3][gray[j]],MIRROR_NORMAL));CHECK(!draws&&!traces&&!suppress);reserved_untouched();
 }
 const int styles[]={-1,MIRROR_BLEND,MIRROR_SHADOW,3,INT_MAX};
 for(unsigned j=0;j<18;j++)for(unsigned s=0;s<sizeof(styles)/sizeof(*styles);s++){
  reset("full8");render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);
  CHECK(!draw_pointer(bank[3][gray[j]],styles[s]));CHECK(!draws&&!traces&&!suppress&&!assets[272+j].initialized);
 }
 reset("full8");render_mirror_bind_terrain(3,121,bank[3][121]);CHECK(draw_pointer(bank[3][121],MIRROR_NORMAL)==1);
 unsigned before=bank_resets;render_mirror_map_begin('Z');CHECK(bank_resets==before+1&&terrain_source_count==0);
 CHECK(!draw_pointer(bank[3][121],MIRROR_NORMAL));render_mirror_bind_terrain(3,122,bank[3][122]);
 CHECK(!draw_pointer(bank[3][121],MIRROR_NORMAL));CHECK(draw_pointer(bank[3][122],MIRROR_NORMAL)==1);
 render_mirror_map_begin('Y');CHECK(!draw_pointer(bank[3][122],MIRROR_NORMAL));
 reset("full8");render_mirror_bind_terrain(3,121,bank[3][121]);Uint8 *row[12]={bank[3][121]};SDL_Surface other={320};
 CHECK(!render_mirror_terrain_row(&other,0,0,row,MIRROR_NORMAL));CHECK(!draws&&!traces);
 unsigned n=rejected_layouts;CHECK(!render_mirror_terrain_row(game_screen,-1,0,row,MIRROR_NORMAL));CHECK(!render_mirror_terrain_row(game_screen,33,0,row,MIRROR_NORMAL));CHECK(rejected_layouts==n+2);
 CHECK(render_mirror_terrain_row(game_screen,32,-11,row,MIRROR_NORMAL)==1);CHECK(draw_x[0]==32&&draw_y[0]==-11);
 reset("full8");render_mirror_bind_terrain(3,121,bank[3][121]);draw_success=false;
 CHECK(!draw_pointer(bank[3][121],MIRROR_NORMAL));CHECK(draws==1&&traces==1&&!trace_mirrored[0]&&!suppress);
}
static void missing_invalid(void)
{
 reset("empty");for(unsigned j=0;j<18;j++)render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);
 for(unsigned j=0;j<18;j++){CHECK(!draw_pointer(bank[3][gray[j]],MIRROR_NORMAL));CHECK(!draws&&!traces&&!suppress);CHECK(assets[272+j].initialized&&!assets[272+j].valid);}
 for(int bad=0;bad<38;bad++){
  char label[30];snprintf(label,sizeof(label),"bad%d",bad);reset(label);render_mirror_bind_terrain(3,121,bank[3][121]);
  CHECK(!draw_pointer(bank[3][121],MIRROR_NORMAL));CHECK(!draws&&!traces&&!suppress);CHECK(assets[272].initialized&&!assets[272].valid);reserved_untouched();
  /* A bad member does not poison a separately cached valid family member. */
  choose("full8");render_mirror_bind_terrain(3,122,bank[3][122]);
  CHECK(draw_pointer(bank[3][122],MIRROR_NORMAL)==1);CHECK(assets[273].valid);
  choose(label);Uint8 *mixed[12]={bank[3][121],bank[3][122]};clear_draws();
  CHECK(render_mirror_terrain_row(game_screen,0,3,mixed,MIRROR_NORMAL)==2);
  CHECK(draws==1&&traces==1&&draw_ids[0]==122&&draw_x[0]==24&&!suppress);
 }
 for(unsigned missing=0;missing<18;missing++){
  char label[30];snprintf(label,sizeof(label),"missing%u",gray[missing]);reset(label);
  for(unsigned j=0;j<18;j++)render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);
  for(unsigned j=0;j<18;j++){CHECK(draw_pointer(bank[3][gray[j]],MIRROR_NORMAL)==(unsigned)(j!=missing));CHECK(draws==(unsigned)(j!=missing)&&traces==draws&&!suppress);}
 }
 reset("full4");for(unsigned j=0;j<18;j++){
  render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);CHECK(draw_pointer(bank[3][gray[j]],MIRROR_NORMAL)==1);CHECK(assets[272+j].density==4);
 }
}
static void rows_and_residency(void)
{
 reset("full8");for(unsigned j=0;j<44;j++)render_mirror_bind_terrain(1,old[j],bank[1][old[j]]);
 for(unsigned j=0;j<15;j++)render_mirror_bind_terrain(2,clouds[j],bank[2][clouds[j]]);
 for(unsigned j=0;j<18;j++)render_mirror_bind_terrain(3,gray[j],bank[3][gray[j]]);
 CHECK(terrain_source_count==77);
 for(unsigned j=0;j<44;j++){CHECK(draw_pointer(bank[1][old[j]],MIRROR_NORMAL)==1);CHECK(assets[old_slots[j]].valid&&assets[old_slots[j]].index==(int)old[j]);}
 for(unsigned j=0;j<15;j++){CHECK(!draw_pointer(bank[2][clouds[j]],MIRROR_BLEND));CHECK(!draws&&!traces);CHECK(draw_pointer(bank[2][clouds[j]],MIRROR_NORMAL)==1);CHECK(assets[186+j].valid);}
 for(unsigned j=0;j<18;j++){CHECK(draw_pointer(bank[3][gray[j]],MIRROR_NORMAL)==1);CHECK(assets[272+j].valid&&assets[272+j].index==(int)gray[j]);}
 unsigned initialized=0;for(unsigned i=0;i<321;i++)initialized+=assets[i].initialized;CHECK(initialized==77);reserved_untouched();
 const unsigned masks[]={0,1,2048,0x555,0xaaa,0xfff,0xa91};
 for(unsigned start=0;start<18;start++)for(unsigned reverse=0;reverse<2;reverse++)for(unsigned m=0;m<7;m++){
  Uint8 *row[12];unsigned ids[12],n=0;
  for(unsigned j=0;j<12;j++){ids[j]=gray[(start+(reverse?11-j:j))%18];row[j]=(masks[m]&(1u<<j))?bank[3][ids[j]]:j%2?NULL:bank[1][121];}
  clear_draws();CHECK(render_mirror_terrain_row(game_screen,16,-13,row,MIRROR_NORMAL)==masks[m]);
  for(unsigned j=0;j<12;j++)if(masks[m]&(1u<<j)){CHECK(draw_ids[n]==ids[j]&&trace_ids[n]==ids[j]);CHECK(draw_x[n]==16+(int)j*24&&draw_y[n]==-13&&trace_style[n]==MIRROR_NORMAL&&trace_mirrored[n]);n++;}
  CHECK(draws==n&&traces==n&&!suppress);
 }
}
static Uint8 *source_pointer(unsigned layer,unsigned slot)
{return layer==1?megaData1.shapes[slot].sh:layer==2?megaData2.shapes[slot].sh:megaData3.shapes[slot].sh;}
static void loader_and_capacity(void)
{
 reset("full8");memcpy(mapSh,actual_lookup,sizeof(mapSh));memcpy(source_blank,actual_blank,sizeof(source_blank));run_loader();
 CHECK(terrain_source_count==100);unsigned k=0,counts[3]={0};
 for(unsigned id=1;id<=600;id++)for(unsigned layer=1;layer<=3;layer++)for(unsigned slot=0;slot<72;slot++){
  bool present=mapSh[layer-1][slot]==id&&(layer==1||(slot<(layer==2?71u:70u)&&!source_blank[id-1]));
  if(present&&accepted(layer,id)){CHECK(k<100&&terrain_sources[k].id==id&&terrain_sources[k].data==source_pointer(layer,slot));CHECK(ref[layer-1][slot]==source_pointer(layer,slot));counts[layer-1]++;k++;}
 }
 CHECK(k==100&&counts[0]==54&&counts[1]==15&&counts[2]==31);
 CHECK(megaData1.shapes[12].sh!=megaData1.shapes[70].sh);CHECK(mapSh[0][12]==351&&mapSh[0][70]==351);
 CHECK(draw_pointer(megaData1.shapes[12].sh,MIRROR_NORMAL)==1);CHECK(draw_pointer(megaData1.shapes[70].sh,MIRROR_NORMAL)==1);CHECK(draw_pointer(megaData3.shapes[5].sh,MIRROR_NORMAL)==1);
 CHECK(!ref[2][70]&&!ref[2][71]);
 /* Each accepted pointer survives even when every eligible slot aliases one ID. */
 reset("full8");memset(source_blank,0,sizeof(source_blank));for(unsigned s=0;s<128;s++){mapSh[0][s]=99;mapSh[1][s]=41;mapSh[2][s]=121;}
 run_loader();CHECK(terrain_source_count==162);k=0;unsigned eligible=0;
 for(unsigned id=1;id<=600;id++)for(unsigned layer=1;layer<=3;layer++)for(unsigned slot=0;slot<(layer==1?72u:layer==2?71u:70u);slot++)if(mapSh[layer-1][slot]==id){
  bool registered=eligible<162;Uint8 *ptr=source_pointer(layer,slot);
  if(registered){CHECK(terrain_sources[k].data==ptr&&terrain_sources[k].id==id);k++;}
  CHECK(draw_pointer(ptr,MIRROR_NORMAL)==(unsigned)registered);CHECK(draws==(unsigned)registered&&traces==draws);eligible++;
 }
 CHECK(k==162&&eligible==213);CHECK(!draw_pointer(megaData3.shapes[19].sh,MIRROR_NORMAL));CHECK(!draws&&!traces);
 /* Explicit overflow and reset: no prior record is overwritten or aliased. */
 reset("full8");for(unsigned i=0;i<601;i++)render_mirror_bind_terrain(3,121,bank[3][i]);CHECK(terrain_source_count==162);
 for(unsigned i=0;i<162;i++)CHECK(terrain_sources[i].data==bank[3][i]&&terrain_sources[i].id==121);
 CHECK(draw_pointer(bank[3][161],MIRROR_NORMAL)==1);CHECK(!draw_pointer(bank[3][162],MIRROR_NORMAL));CHECK(!draws&&!traces);
 render_mirror_map_begin('Z');CHECK(!terrain_source_count);CHECK(!draw_pointer(bank[3][161],MIRROR_NORMAL));
}
int main(int argc,char **argv)
{
 CHECK(argc==2);root=argv[1];whitelist();guards();missing_invalid();rows_and_residency();loader_and_capacity();reset("empty");
 printf("PASS: %lu assertions; exact gray18 IDs and slots272..289 plus purple13 registration scope, bankZ/layer3/pointer guards, non-NORMAL no-load skip, missing/null/malformed fallback, all38 malformed input cases, map reset, original loader100 registrations including duplicate351, bound162 overflow preserves existing pointers and later classic fallback, 77 simultaneous terrain assets,252 ordered full/partial rows, inherited4x fallback; reserved269..271 untouched.\n",checks);
 return 0;
}
