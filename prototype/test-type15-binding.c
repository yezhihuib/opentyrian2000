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
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int pitch,w,h;SDL_PixelFormat *format;void *pixels;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int unused;} G101Record;
typedef struct {int unused;} PCapRecord;
typedef struct {int unused;} Forest13Record;
enum {MIRROR_NORMAL=0,MIRROR_BLEND=1,MIRROR_SHADOW=2};
#include "production-types.inc"
static bool active=true,game_probe_missing,game_probe_invalid,game_probe_original_reference,suppress,forest_registry_ok=true;
static int game_probe_density=8,game_probe_scene_assets=3;
static const char *game_probe_assets,*reject_reason;
static SDL_PixelFormat pixel_format={8,1};
static SDL_Surface surface_storage={320,320,200,&pixel_format,NULL},*game_screen=&surface_storage,*VGAScreen=&surface_storage;
static Sprite2_array enemySpriteSheets[4],spriteSheet11;static unsigned enemySpriteSheetIds[4];
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
 if(recorded.slot>=396&&recorded.slot<404)for(int i=396;i<404;i++)assert(assets[i].initialized&&assets[i].valid&&assets[i].density==8);
 return true;
}
static unsigned allocation_calls,reads[8][2];
static const unsigned actor_ids[8]={39,41,43,45,91,93,129,131};
static FILE *test_fopen(const char *path,const char *mode)
{
 assert(!strcmp(mode,"rb"));const char *leaf=strrchr(path,'/');leaf=leaf?leaf+1:path;
 for(int k=0;k<8;k++)for(int d=0;d<2;d++){char wanted[64];snprintf(wanted,sizeof(wanted),"enemy-newsh2-%u-%d.hda",actor_ids[k],d?8:4);if(!strcmp(leaf,wanted))reads[k][d]++;}
 return fopen(path,mode);
}
static int fail_allocation=-1;
static void *test_malloc(size_t n){unsigned call=allocation_calls++;return (int)call==fail_allocation?NULL:malloc(n);}
#define fopen test_fopen
#define malloc test_malloc
#include "production-helpers.inc"
#undef malloc
#undef fopen
static Uint8 terrain_data[601][2];
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));memset(&recorded,0,sizeof(recorded));
 memset(reads,0,sizeof(reads));
#include "production-reset.inc"
 allocation_calls=0;fail_allocation=-1;game_probe_density=8;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;active=true;game_probe_scene_assets=3;reject_reason=NULL;render_mirror_map_begin('Z');
}
static bool actor(unsigned id,int part,int filter){int px=part==1||part==20?12:0,py=part==19||part==20?14:0;return render_mirror_enemy_tile(game_screen,94+px,73+py,enemySpriteSheets[0],id,part,filter,NULL);}
static bool neighbor(void){return render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],153,0,0,NULL);}
static unsigned terrain(unsigned id,int style){Uint8*row[12]={terrain_data[id]};return render_mirror_terrain_row(game_screen,0,37,row,style);}
static void filters(void)
{
 reset();
 for(unsigned i=0;i<256;i++)rgb_palette[i]=((i*73u%256)<<16)|((i*151u%256)<<8)|(i*199u%256);
 uint64_t synthetic=0,authored=0,alpha_classes[3]={0};
 /* Every byte alpha at every brightness and filter, with three possible max
  * channels. RGB is checked against independently evaluated palette ramps. */
 for(unsigned filter=0;filter<256;filter++)for(unsigned peak=0;peak<256;peak++)for(unsigned alpha=0;alpha<256;alpha++) {
  unsigned pos=(filter+alpha)%3;
  Uint8 src[4]={0,0,0,(Uint8)alpha},actual[4];src[pos]=(Uint8)peak;src[(pos+1)%3]=(Uint8)(peak/2);
  enemy_filter_rgba(src,(Uint8)filter,actual);
  unsigned value=(peak*15*256+127)/255,lo=value/256,hi=MIN(15,lo+1),fraction=value%256;
  for(unsigned c=0;c<3;c++) {
   unsigned shift=(2-c)*8,a=(rgb_palette[(Uint8)(filter|lo)]>>shift)&255,b=(rgb_palette[(Uint8)(filter|hi)]>>shift)&255;
   assert(actual[c]==(a*(256-fraction)+b*fraction+128)/256);
  }
  assert(actual[3]==alpha);synthetic++;
 }
 for(int k=0;k<8;k++) {
  assert(actor(actor_ids[k],0,0));Asset *a=&assets[396+k];
  for(size_t p=0;p<(size_t)a->w*a->h*a->density*a->density;p++) {
   const Uint8 *src=a->rgba+p*4;alpha_classes[src[3]==0?0:src[3]==255?2:1]++;
   for(unsigned filter=0;filter<256;filter++) {
    Uint8 actual[4];enemy_filter_rgba(src,(Uint8)filter,actual);assert(actual[3]==src[3]);authored++;
   }
  }
 }
 assert(alpha_classes[0]&&alpha_classes[1]&&alpha_classes[2]);
 printf("PASS alpha retained: %llu synthetic filter/peak/alpha combinations, %llu authored pixel/filter combinations; zero/fractional/opaque pixels %llu/%llu/%llu\n",
  (unsigned long long)synthetic,(unsigned long long)authored,(unsigned long long)alpha_classes[0],(unsigned long long)alpha_classes[1],(unsigned long long)alpha_classes[2]);
 reset();
}

int main(int argc,char**argv)
{
 assert(argc==4||argc==5);game_probe_assets=argv[1];Uint8 data[5][2]={{0}};unsigned bank_ids[4]={1,2,9,0};
 for(int i=0;i<4;i++){enemySpriteSheets[i]=(Sprite2_array){data[i],2};enemySpriteSheetIds[i]=bank_ids[i];}
 spriteSheet11=(Sprite2_array){data[4],2};
 if(!strcmp(argv[2],"filter")){filters();reset();return 0;}
 if(!strcmp(argv[2],"trace")){
  /* All sheet identities, not just the new bank; bank3 is also checked. */
  G101EnemyContext context={.type=1,.size=0};
  for(unsigned bank_id=0;bank_id<=36;bank_id++) {
   reset();enemySpriteSheetIds[3]=bank_id;
   for(unsigned id=0;id<=700;id++)if(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[3],id,0,0,&context))printf("a %u %u %d\n",bank_id,id,recorded.slot);
  }
  for(unsigned type=391;type<=394;type++){reset();context.type=type;for(unsigned id=0;id<=700;id++)if(render_mirror_enemy_tile(game_screen,94,73,spriteSheet11,id,0,0,&context))printf("p %u %u %d\n",type,id,recorded.slot);}
  for(unsigned layer=1;layer<=3;layer++)for(unsigned id=1;id<=600;id++){
   render_mirror_map_begin('Z');render_mirror_bind_terrain(layer,id,terrain_data[id]);
   if(terrain(id,MIRROR_NORMAL))printf("t %u %u %d\n",layer,id,recorded.slot);
  }
  reset();return 0;
 }
 if(!strcmp(argv[2],"density4")){
  unsigned found=0;
  for(int k=0;k<8;k++){
   char path[1024];snprintf(path,sizeof(path),"%s/enemy-newsh2-%u-4.hda",game_probe_assets,actor_ids[k]);
   FILE *f=fopen(path,"rb");if(!f)continue;fclose(f);
   Asset a={.bank=101,.index=(int)actor_ids[k],.w=24,.h=28,.anchor_x=6,.anchor_y=7};
   assert(read_asset(&a,4)&&a.density==4&&a.rgba);free(a.rgba);found++;
  }
  assert(found);reset();
 }
 bool present=!!atoi(argv[3]);const int parts[4]={0,1,19,20},xs[4]={0,12,0,12},ys[4]={0,0,14,14};
 for(unsigned bits=0;bits<4;bits++){
  reset();game_probe_scene_assets=(int)bits;
  assert(actor(39,0,0)==(present&&(bits&1)));
  if(!(bits&1))assert(allocation_calls==0);
  game_probe_scene_assets=1;assert(actor(39,0,0)==present);unsigned loaded=allocation_calls;assert(loaded<=8&&(!present||loaded==8));
  for(int n=0;n<32;n++)assert(actor(131,0,0)==present);
  assert(allocation_calls==loaded);
 }
 if(present)for(int failed=0;failed<8;failed++){
  reset();fail_allocation=failed;assert(!actor(39,0,0)&&allocation_calls==8&&!recorded.calls);fail_allocation=-1;
  for(int k=0;k<8;k++)assert(!actor(actor_ids[k],0,0));
  assert(allocation_calls==8);assert(neighbor()&&allocation_calls==9&&recorded.slot==269);
  reset();assert(actor(131,0,0)&&allocation_calls==8);
 }
 /* Every possible first member must preflight the whole family. */
 for(int first=0;first<8;first++){
  reset();assert(actor(actor_ids[first],0,0)==present);
  for(int k=0;k<8;k++)assert(reads[k][1]==1&&reads[k][0]==0&&assets[396+k].initialized);
  for(int k=0;k<8;k++)for(int q=0;q<4;q++)for(int f=0;f<256;f++){
   unsigned n=recorded.calls;assert(actor(actor_ids[k],parts[q],f)==present);
   if(present){Asset*a=&assets[396+k];assert(recorded.calls==n+1&&recorded.slot==396+k&&recorded.x==94&&recorded.y==73&&recorded.style==MIRROR_NORMAL&&recorded.filter==f);assert(recorded.part.x==xs[q]&&recorded.part.y==ys[q]&&recorded.part.w==12&&recorded.part.h==14);assert(a->bank==101&&a->index==(int)actor_ids[k]&&a->w==24&&a->h==28&&a->anchor_x==6&&a->anchor_y==7);}
   else assert(recorded.calls==n);
  }
  for(int k=0;k<8;k++)assert(reads[k][1]==1&&reads[k][0]==0);
  for(int mode=0;mode<9;mode++){
   int old_bits=game_probe_scene_assets;const char*old_assets=game_probe_assets;
   if(mode==0)game_probe_missing=true;if(mode==1)game_probe_invalid=true;if(mode==2)game_probe_density=4;if(mode==3)game_probe_density=1;if(mode==4)game_probe_scene_assets=0;if(mode==5)game_probe_scene_assets=2;if(mode==6)active=false;if(mode==7)game_probe_assets=NULL;if(mode==8)reject_reason="test";
   for(int k=0;k<8;k++)assert(!actor(actor_ids[k],0,0));
   game_probe_scene_assets=old_bits;game_probe_assets=old_assets;game_probe_missing=game_probe_invalid=false;game_probe_density=8;active=true;reject_reason=NULL;
  }
  for(int k=0;k<8;k++)assert(!actor(actor_ids[k],2,0)&&!actor(actor_ids[k],-1,0)&&!actor(actor_ids[k],21,0));
  assert(neighbor()&&recorded.slot==269);
  /* Existing numeric aliases and both bank2 families remain independently live. */
  assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[2],39,0,0,NULL)&&recorded.slot==256);
  const unsigned bank2[14]={153,155,157,159,191,193,195,231,233,235,267,269,271,273};
  for(int k=0;k<14;k++)assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],bank2[k],0,0,NULL)&&recorded.slot==382+k);
  for(int k=0;k<8;k++)assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],actor_ids[k],0,0,NULL));
  Sprite2_array foreign={data[0]+1,1};assert(!render_mirror_enemy_tile(game_screen,94,73,foreign,39,0,0,NULL));
  SDL_Surface wrong=surface_storage;assert(!render_mirror_enemy_tile(&wrong,94,73,enemySpriteSheets[0],39,0,0,NULL));
 }
 /* Existing registry capacity is unchanged, no new terrain entries. */
 reset();for(unsigned i=0;i<199;i++)render_mirror_bind_terrain(3,161,terrain_data[i]);assert(terrain_source_count==199);render_mirror_bind_terrain(3,162,terrain_data[200]);assert(terrain_source_count==199);
 /* Cache failure remains sticky even if a good pack becomes available. This
  * deliberately exercises the helper in isolation; runtime pack selection is
  * startup-only and the Python source guard proves no reload writer exists. */
 if(argc==5){
  const char *original=game_probe_assets;reset();assert(actor(39,0,0)==present);
  unsigned loaded=allocation_calls;game_probe_assets=argv[4];
  for(int k=0;k<8;k++)assert(actor(actor_ids[k],0,0)==present);
  assert(allocation_calls==loaded);reset();assert(actor(91,0,0)&&allocation_calls==8);
  game_probe_assets=original;
 }
 if(present){
  const char *original=game_probe_assets;reset();assert(actor(45,0,0));
  unsigned loaded=allocation_calls;game_probe_assets="/no-such-type15-unit-pack";
  for(int k=0;k<8;k++)assert(actor(actor_ids[k],0,0));
  assert(allocation_calls==loaded);reset();
  for(int k=0;k<8;k++)assert(!actor(actor_ids[k],0,0));
  assert(!recorded.calls);game_probe_assets=original;reset();assert(actor(93,0,0));
 }
 /* Every density gate is checked cold, before any resource read. */
 for(int density=1;density<=4;density+=3){reset();game_probe_density=density;for(int k=0;k<8;k++)assert(!actor(actor_ids[k],0,0)&&reads[k][0]==0&&reads[k][1]==0);assert(allocation_calls==0&&!recorded.calls);}
 reset();puts("PASS eight-member preflight including source-only91, cached coherence, four quadrants/all filters, exact identities, aliases, terrain capacity and both prior bank2 families");return 0;
}
