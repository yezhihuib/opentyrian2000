/* Extracted production loader/routes and optional original RLE differential.
 * Unit recorder only: no game, capture, forced combat, or renderer claim. */
#include <assert.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int pitch,w,h;SDL_PixelFormat *format;void *pixels;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int size;} G101EnemyContext;
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
static SDL_Surface surface_storage={320,320,200,&pixel_format,NULL},*game_screen=&surface_storage;
static SDL_Surface *VGAScreen=&surface_storage;
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
#define asset_debug_effect(...) ((void)0)
#define render_mirror_pixel(...) ((void)0)
static Uint16 SDL_SwapLE16(Uint16 value){Uint8 b[2];memcpy(b,&value,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}
static bool draw_asset_filtered(int x,int y,Asset*a,int style,const SDL_Rect*part,Uint8 filter,const G101Record*m,const PCapRecord*c,const Forest13Record*f)
{
 assert(a&&a->valid&&!m&&!c&&!f);recorded.calls++;recorded.slot=(int)(a-assets);recorded.x=x;recorded.y=y;recorded.style=style;recorded.filter=filter;recorded.part_present=!!part;if(part)recorded.part=*part;
 /* No first quadrant, including an empty one, can draw before all six load. */
#if !BASELINE
 if(recorded.slot>=416&&recorded.slot<422)for(int i=416;i<422;i++)assert(assets[i].initialized&&assets[i].valid&&assets[i].density==8);
#endif
 return true;
}
static unsigned allocation_calls,entry_reads[6][2];
static int fail_allocation=-1;
static void *test_malloc(size_t n){unsigned call=allocation_calls++;return (int)call==fail_allocation?NULL:malloc(n);}
static FILE *test_fopen(const char *path,const char *mode)
{
 const unsigned ids[6]={171,190,209,228,247,266};const char *leaf=strrchr(path,'/');leaf=leaf?leaf+1:path;
 for(int k=0;k<6;k++)for(int density=0;density<2;density++){char wanted[64];snprintf(wanted,sizeof(wanted),"enemy-newsh2-%u-%d.hda",ids[k],density?8:4);if(!strcmp(leaf,wanted))entry_reads[k][density]++;}
 return fopen(path,mode);
}
#define fopen test_fopen
#define malloc test_malloc
#include "production-helpers.inc"
#undef malloc
#undef fopen
#include "production-original.inc"
static const unsigned actor_ids[6]={171,190,209,228,247,266};
static Uint8 terrain_data[601][2];
static G101EnemyContext small_context={0};
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));memset(&recorded,0,sizeof(recorded));memset(entry_reads,0,sizeof(entry_reads));
 linked31_checked=linked31_valid=false;newsh4_long7_checked=newsh4_long7_valid=false;newsh4_opposite7_checked=newsh4_opposite7_valid=false;
 type15_eightheading_checked=type15_eightheading_valid=false;late_spike_checked=late_spike_valid=false;newsh4_entry6_checked=newsh4_entry6_valid=false;
#if !BASELINE
 type3_small_checked=type3_small_valid=false;
#endif
 surface_storage=(SDL_Surface){320,320,200,&pixel_format,NULL};pixel_format=(SDL_PixelFormat){8,1};small_context.size=0;
 allocation_calls=0;fail_allocation=-1;game_probe_density=8;game_probe_missing=game_probe_invalid=false;active=true;game_probe_scene_assets=3;reject_reason=NULL;render_mirror_map_begin('Z');
}
static void preflight_was_complete(void)
{
#if !BASELINE
 for(int k=0;k<6;k++)assert(assets[416+k].initialized&&entry_reads[k][0]==0&&entry_reads[k][1]==1);
#endif
}
static bool actor(unsigned id,int part,int filter){return render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],id,part,filter,&small_context);}
static bool neighbor(void){return render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],153,0,0,NULL);}
static unsigned terrain(unsigned id,int style){Uint8*row[12]={terrain_data[id]};return render_mirror_terrain_row(game_screen,0,37,row,style);}
static void prior_families(const char *failed)
{
 const unsigned ids[6][8]={{153,155,157,159,191,193,195},{231,233,235,267,269,271,273},{1,3,5,7,9,11},{39,41,43,45,91,93,129,131},{81,83,85,119,121,123},{15,17,53,55}};
 const unsigned counts[6]={7,7,6,8,6,4},sheet[6]={1,1,0,0,1,0},slots[6]={382,389,404,396,410,378};
 const char *labels[6]={"long7","opposite7","spike","type15","entry6","linked31"};
 for(unsigned f=0;f<6;f++)for(unsigned k=0;k<counts[f];k++) {
  bool expected=!failed||strcmp(failed,labels[f]);unsigned n=recorded.calls;
  bool result=render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[sheet[f]],ids[f][k],0,0,NULL);
  assert(result==expected&&recorded.calls==n+(unsigned)expected);if(expected)assert(recorded.slot==(int)(slots[f]+k));
 }
 const unsigned tids[4]={161,162,171,172};
 for(unsigned k=0;k<4;k++){render_mirror_map_begin('Z');render_mirror_bind_terrain(3,tids[k],terrain_data[tids[k]]);bool expected=!failed||strcmp(failed,"linked31");assert(!!terrain(tids[k],MIRROR_NORMAL)==expected);if(expected)assert(recorded.slot==374+(int)k);}
}
static void geometry(void)
{
 const int pitches[]={INT_MIN,-1,0,11,12,319,320,321,INT_MAX};
 const int bx[]={INT_MIN,-321,-34,-13,-12,-1,0,1,12,24,286,287,288,307,308,309,319,320,321,INT_MAX};
 const int by[]={INT_MIN,INT_MIN+13,-214,-28,-15,-14,-13,-12,-1,0,1,183,184,185,186,198,199,200,213,214,INT_MAX-14,INT_MAX};
 unsigned cases=0;
 for(unsigned p=0;p<sizeof(pitches)/sizeof(*pitches);p++) {
  reset();game_screen->pitch=pitches[p];
  for(int k=0;k<6;k++)for(int f=0;f<256;f++)for(unsigned xi=0;xi<sizeof(bx)/sizeof(*bx);xi++)for(unsigned yi=0;yi<sizeof(by)/sizeof(*by);yi++) {
   int x=bx[xi],y=by[yi];unsigned n=recorded.calls;bool safe=pitches[p]==320&&x>=0&&x<=308&&y>=-13&&y<=199;
   assert(render_mirror_enemy_tile(game_screen,x,y,enemySpriteSheets[0],actor_ids[k],0,f,&small_context)==safe&&recorded.calls==n+(unsigned)safe);
   if(safe)assert(recorded.slot==416+k&&recorded.x==x&&recorded.y==y&&recorded.filter==f&&!recorded.part_present);
   cases++;
  }
  game_screen->pitch=320;assert(actor(171,0,0)&&recorded.slot==416);
 }
 for(int mode=0;mode<15;mode++) {
  reset();
  if(mode==0)game_screen->w=319;if(mode==1)game_screen->w=321;if(mode==2)game_screen->w=INT_MIN;if(mode==3)game_screen->w=INT_MAX;
  if(mode==4)game_screen->h=199;if(mode==5)game_screen->h=201;if(mode==6)game_screen->h=INT_MIN;if(mode==7)game_screen->h=INT_MAX;
  if(mode==8)pixel_format.BitsPerPixel=0;if(mode==9)pixel_format.BitsPerPixel=32;if(mode==10)pixel_format.BitsPerPixel=7;
  if(mode==11)game_screen->format=NULL;if(mode==12)pixel_format.BytesPerPixel=0;if(mode==13)pixel_format.BytesPerPixel=4;if(mode==14)pixel_format.BytesPerPixel=2;
  for(int k=0;k<6;k++)for(int f=0;f<256;f++)assert(!actor(actor_ids[k],0,f));
  assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],39,0,0,NULL)&&recorded.slot==396);
 }
 reset();printf("PASS %u all-filter Cartesian physical-layout/row/partial-y geometry cases plus all format fields\n",cases);
}
static void original_rle(const char *path)
{
 FILE *f=fopen(path,"rb");assert(f&&fseek(f,0,SEEK_END)==0);long length=ftell(f);assert(length>0&&fseek(f,0,SEEK_SET)==0);
 Uint8 *bytes=malloc((size_t)length);assert(bytes&&fread(bytes,1,(size_t)length,f)==(size_t)length&&fclose(f)==0);
 reset();enemySpriteSheets[0]=(Sprite2_array){bytes,(size_t)length};
 enum {PAD=16384,SCREEN=64000,TOTAL=SCREEN+2*PAD};static Uint8 actual[TOTAL],expected[TOTAL],clipped[SCREEN];
 const int bx[]={-321,-34,-13,-12,-1,0,1,12,307,308,309,319,320,321},by[]={-28,-14,-13,-1,0,1,183,184,185,186,199,200,214};
 const int filters[]={0,1,9,15,16,31,63,99,127,128,208,224,240,247,254,255};
 unsigned cases=0,wrapped=0,opaque=0;
 for(int k=0;k<6;k++) {
  unsigned index=actor_ids[k],pos=bytes[(index-1)*2]|(unsigned)bytes[(index-1)*2+1]<<8,linear=0,count=0;Uint8 values[168]={0},mask[168]={0};
  while(pos<(unsigned)length&&bytes[pos]!=15){unsigned code=bytes[pos++];linear+=code&15;for(unsigned n=0;n<(code>>4);n++){assert(linear<168&&pos<(unsigned)length);values[linear]=bytes[pos++];mask[linear++]=1;count++;}}
  assert(pos<(unsigned)length);opaque+=count;assert(actor(index,0,0));Asset*a=&assets[416+k];
  for(int ly=0;ly<14;ly++)for(int lx=0;lx<12;lx++)for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)assert(a->rgba[((size_t)(ly*8+sy)*96+lx*8+sx)*4+3]==(mask[ly*12+lx]?255:0));
  for(unsigned xi=0;xi<sizeof(bx)/sizeof(*bx);xi++)for(unsigned yi=0;yi<sizeof(by)/sizeof(*by);yi++)for(int fi=-1;fi<(int)(sizeof(filters)/sizeof(*filters));fi++) {
   int x=bx[xi],y=by[yi],filter=fi<0?0:filters[fi];unsigned writes=0;
   memset(actual,0xa5,sizeof(actual));memset(expected,0xa5,sizeof(expected));memset(clipped,0xa5,sizeof(clipped));game_screen->pixels=actual+PAD;
   for(int cy=0;cy<14;cy++)for(int cx=0;cx<12;cx++)if(mask[cy*12+cx]) {
    int address=(y+cy)*320+x+cx;Uint8 v=fi<0?values[cy*12+cx]:(Uint8)(filter|(values[cy*12+cx]&15));
    if(address>=0&&address<SCREEN){expected[PAD+address]=v;writes++;}if(y+cy>=0&&y+cy<200&&x+cx>=0&&x+cx<320)clipped[(y+cy)*320+x+cx]=v;
   }
   if(fi<0)blit_sprite2(game_screen,x,y,enemySpriteSheets[0],index);else blit_sprite2_filter(game_screen,x,y,enemySpriteSheets[0],index,(Uint8)filter);
   assert(!memcmp(actual,expected,sizeof(actual)));bool safe=x>=0&&x<=308&&y>=-13&&y<=199;
   assert(render_mirror_enemy_tile(game_screen,x,y,enemySpriteSheets[0],index,0,filter,&small_context)==safe);assert(!memcmp(actual,expected,sizeof(actual)));
   if(safe)assert(!memcmp(actual+PAD,clipped,SCREEN));if(x>=0&&x<=308&&(y< -13||y>199))assert(!writes);
   if(memcmp(actual+PAD,clipped,SCREEN)){assert(!safe&&(x<0||x>308));wrapped++;}cases++;
  }
 }
 assert(opaque==500&&wrapped>0);printf("PASS original normal/filter RLE: %u cases, %u row-wrap differences, 500 exact opaque cells\n",cases,wrapped);
 reset();free(bytes);enemySpriteSheets[0]=(Sprite2_array){NULL,0};
}
int main(int argc,char**argv)
{
 assert(argc==4);game_probe_assets=argv[1];Uint8 data[4][2]={{0}};unsigned bank_ids[4]={1,2,9,0};
 for(int i=0;i<4;i++){enemySpriteSheets[i]=(Sprite2_array){data[i],2};enemySpriteSheetIds[i]=bank_ids[i];}
 if(!strcmp(argv[2],"trace")) {
  for(unsigned bank_id=0;bank_id<=36;bank_id++){enemySpriteSheetIds[3]=bank_id;for(unsigned id=0;id<=700;id++)if(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[3],id,0,0,&small_context))printf("a %u %u %d\n",bank_id,id,recorded.slot);}
  for(unsigned layer=1;layer<=3;layer++)for(unsigned id=1;id<=600;id++){render_mirror_map_begin('Z');render_mirror_bind_terrain(layer,id,terrain_data[id]);if(terrain(id,MIRROR_NORMAL))printf("t %u %u %d\n",layer,id,recorded.slot);}
  reset();return 0;
 }
 assert(!BASELINE);
 if(!strcmp(argv[2],"geometry")){geometry();return 0;}
 if(!strcmp(argv[2],"original")){original_rle(argv[3]);return 0;}
 if(!strcmp(argv[2],"independent")){reset();prior_families(argv[3]);for(int k=0;k<6;k++)assert(actor(actor_ids[k],0,0)&&recorded.slot==416+k);unsigned loaded=allocation_calls;prior_families(argv[3]);assert(allocation_calls==loaded);reset();puts("PASS prior family failure independent of small family");return 0;}
 bool present=!!atoi(argv[3]);
 if(!strcmp(argv[2],"unavailable")){reset();for(int k=0;k<6;k++)assert(!actor(actor_ids[k],0,0));preflight_was_complete();assert(!allocation_calls&&!recorded.calls);reset();puts("PASS absent or4x-only family: no4x retry");return 0;}
 if(!strcmp(argv[2],"cache")){reset();assert(actor(171,0,0)==present);preflight_was_complete();unsigned loaded=allocation_calls;puts("READY");fflush(stdout);assert(getchar()=='\n');for(int k=0;k<6;k++)assert(actor(actor_ids[k],0,0)==present);assert(allocation_calls==loaded);preflight_was_complete();reset();for(int k=0;k<6;k++)assert(actor(actor_ids[k],0,0)==!present);reset();puts("PASS unchanged cached success/failure until reset");return 0;}
 for(unsigned bits=0;bits<4;bits++){reset();game_probe_scene_assets=(int)bits;assert(actor(171,0,0)==(present&&(bits&1)));if(!(bits&1))assert(!allocation_calls);game_probe_scene_assets=1;assert(actor(171,0,0)==present);unsigned loaded=allocation_calls;for(int n=0;n<32;n++)assert(actor(266,0,0)==present);assert(allocation_calls==loaded);}
 for(int mode=0;mode<9;mode++) {
  reset();const char *old_assets=game_probe_assets;
  if(mode==0)game_probe_missing=true;if(mode==1)game_probe_invalid=true;if(mode==2)game_probe_density=4;if(mode==3)game_probe_density=1;if(mode==4)game_probe_scene_assets=0;if(mode==5)game_probe_scene_assets=2;if(mode==6)active=false;if(mode==7)game_probe_assets=NULL;if(mode==8)reject_reason="test";
  for(int k=0;k<6;k++)assert(!actor(actor_ids[k],0,0));assert(!allocation_calls&&!recorded.calls);
  game_probe_assets=old_assets;game_probe_scene_assets=3;game_probe_missing=game_probe_invalid=false;game_probe_density=8;active=true;reject_reason=NULL;assert(actor(266,0,0)==present);
 }
 if(present)for(int failed=0;failed<6;failed++){reset();fail_allocation=failed;assert(!actor(171,0,0)&&allocation_calls==6&&!recorded.calls);fail_allocation=-1;for(int k=0;k<6;k++)assert(!actor(actor_ids[k],0,0));assert(allocation_calls==6);assert(neighbor()&&allocation_calls==7&&recorded.slot==269);prior_families(NULL);reset();assert(actor(266,0,0)&&allocation_calls==6);}
 for(int first=0;first<6;first++) {
  reset();assert(actor(actor_ids[first],0,0)==present);preflight_was_complete();unsigned loaded=allocation_calls;
  for(int k=0;k<6;k++)for(int f=0;f<256;f++) {
   unsigned n=recorded.calls;assert(actor(actor_ids[k],0,f)==present);
   if(present){Asset*a=&assets[416+k];assert(recorded.calls==n+1&&recorded.slot==416+k&&recorded.x==94&&recorded.y==73&&recorded.style==MIRROR_NORMAL&&recorded.filter==f&&!recorded.part_present);assert(a->bank==101&&a->index==(int)actor_ids[k]&&a->w==12&&a->h==14&&a->anchor_x==0&&a->anchor_y==0);}else assert(recorded.calls==n);
  }
  assert(allocation_calls==loaded);preflight_was_complete();const int parts[]={INT_MIN,-1,1,2,18,19,20,21,INT_MAX};
  for(int k=0;k<6;k++){
   for(unsigned q=0;q<sizeof(parts)/sizeof(*parts);q++)assert(!actor(actor_ids[k],parts[q],0));
   assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],actor_ids[k],0,0,NULL));
   small_context.size=1;assert(!actor(actor_ids[k],0,0));small_context.size=-1;assert(!actor(actor_ids[k],0,0));small_context.size=0;
   assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],actor_ids[k],0,0,&small_context));
  }
  assert(neighbor()&&recorded.slot==269);prior_families(NULL);
  const unsigned raw[]={170,172,189,191,208,210,227,229,246,248,265,268};
  for(unsigned k=0;k<sizeof(raw)/sizeof(*raw);k++)if(raw[k]!=191&&raw[k]!=229)assert(!actor(raw[k],0,0));
  Sprite2_array foreign={data[0]+1,1},null_sheet={NULL,0};SDL_Surface wrong={320,320,200,&pixel_format,NULL};
  assert(!render_mirror_enemy_tile(game_screen,94,73,foreign,171,0,0,&small_context));assert(!render_mirror_enemy_tile(game_screen,94,73,null_sheet,171,0,0,&small_context));assert(!render_mirror_enemy_tile(&wrong,94,73,enemySpriteSheets[0],171,0,0,&small_context));
 }
 reset();for(unsigned i=0;i<199;i++)render_mirror_bind_terrain(3,161,terrain_data[i]);assert(terrain_source_count==199);render_mirror_bind_terrain(3,162,terrain_data[200]);assert(terrain_source_count==199);
 for(unsigned i=0;i<256;i++)rgb_palette[i]=(i<<16)|(i<<8)|i;
 for(unsigned f=0;f<256;f++)for(unsigned peak=0;peak<256;peak++){Uint8 src[4]={(Uint8)peak,(Uint8)(peak/2),0,173},out[4];enemy_filter_rgba(src,(Uint8)f,out);unsigned v=(peak*15*256+127)/255,lo=v/256,hi=MIN(15,lo+1),frac=v%256,expected=((f|lo)*(256-frac)+(f|hi)*frac+128)/256;assert(out[0]==expected&&out[1]==expected&&out[2]==expected&&out[3]==173);}
 reset();puts("PASS small six coherent preflight/cache/allocation, six first orders, all filters, context/part/namespace/geometry and six independent prior families");return 0;
}
