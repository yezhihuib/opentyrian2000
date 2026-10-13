/* Extracted current production units; never starts a game or records a capture. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef uint8_t Uint8;
typedef uint32_t Uint32;
typedef struct { int x,y,w,h; } SDL_Rect;
typedef struct { int BitsPerPixel,BytesPerPixel; } SDL_PixelFormat;
typedef struct { int pitch,w,h; SDL_PixelFormat *format; void *pixels; } SDL_Surface;
typedef struct { Uint8 *data; size_t size; } Sprite2_array;
typedef struct { int unused; } G101Record;
typedef struct { int unused; } PCapRecord;
typedef struct { int unused; } Forest13Record;
enum { MIRROR_NORMAL=0, MIRROR_BLEND=1, MIRROR_SHADOW=2 };
#include "production-types.inc"
#include "production-order.inc"
static bool active=true,game_probe_missing,game_probe_invalid,game_probe_original_reference;
static int game_probe_density=8,game_probe_scene_assets=3;
static const char *game_probe_assets,*reject_reason;
static SDL_PixelFormat pixel_format={8,1};
static SDL_Surface surface_storage={320,320,200,&pixel_format,NULL};
static SDL_Surface *game_screen=&surface_storage,*VGAScreen=&surface_storage;
static Sprite2_array enemySpriteSheets[4],spriteSheet11;
static unsigned int enemySpriteSheetIds[4];
static Uint32 rgb_palette[256];
static struct { unsigned calls; int slot,x,y,style,filter; bool part_present; SDL_Rect part; } recorded;
static unsigned reads[5][2],allocations;
static int fail_allocation=-1;
static const unsigned ids[5]={159,161,163,165,167};
static const G101EnemyContext type4_context={.type=4,.size=1};
static bool ground101_enemy_eligible(const G101EnemyContext *c,unsigned r,unsigned b)
{ (void)c;(void)r;(void)b;return false; }
static const G101Record *ground101_record(unsigned r,unsigned b)
{ (void)r;(void)b;assert(false);return NULL; }
#define ground101_actor_trace(...) ((void)0)
#define ground101_note_draw(...) ((void)0)
#define game_probe_scene_draw(...) ((void)0)
static bool draw_asset_filtered(int x,int y,Asset *a,int style,const SDL_Rect *part,Uint8 filter,const G101Record *m,const PCapRecord *c,const Forest13Record *f)
{
 assert(a&&a->valid&&!m&&!c&&!f);
 recorded.calls++;recorded.slot=(int)(a-assets);recorded.x=x;recorded.y=y;
 recorded.style=style;recorded.filter=filter;recorded.part_present=!!part;
 if(part)recorded.part=*part;
 return true;
}
static FILE *test_fopen(const char *path,const char *mode)
{
 assert(!strcmp(mode,"rb"));
 const char *leaf=strrchr(path,'/');leaf=leaf?leaf+1:path;
 for(int k=0;k<5;k++)for(int d=0;d<2;d++) {
  char wanted[64];snprintf(wanted,sizeof(wanted),"enemy-newsh2-%u-%d.hda",ids[k],d?8:4);
  if(!strcmp(leaf,wanted))reads[k][d]++;
 }
 return fopen(path,mode);
}
static void *test_malloc(size_t n)
{unsigned call=allocations++;return (int)call==fail_allocation?NULL:malloc(n);}
#define fopen test_fopen
#define malloc test_malloc
#include "production-helpers.inc"
#undef malloc
#undef fopen
static void reset(void)
{
 for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++)free(assets[i].rgba);
 memset(assets,0,sizeof(assets));memset(&recorded,0,sizeof(recorded));memset(reads,0,sizeof(reads));
#include "production-reset.inc"
 game_probe_density=8;game_probe_missing=false;game_probe_invalid=false;
 active=true;game_probe_scene_assets=3;reject_reason=NULL;game_probe_original_reference=false;
 allocations=0;fail_allocation=-1;
}
static bool draw(unsigned base,int q,int filter)
{
 return render_mirror_enemy_tile(game_screen,100+quadrants[q][0],80+quadrants[q][1],
  enemySpriteSheets[0],base,quadrants[q][2],filter,&type4_context);
}
static void other_banks(void)
{
 /* The identical numeric159 in newsh4 is a legitimate, independent long7. */
 unsigned n=recorded.calls;
 assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[1],159,0,0,NULL));
 assert(recorded.calls==n+1&&recorded.slot==385&&assets[385].bank==ASSET_NEWSH4);
 assert(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[2],1,0,9,NULL));
 assert(recorded.slot==253&&assets[253].bank==ASSET_NEWSHE);
 assert(draw(153,0,0)&&recorded.slot==269&&assets[269].bank==ASSET_NEWSH2);
 for(int k=0;k<5;k++)for(int b=1;b<4;b++) {
  n=recorded.calls;
  bool ok=render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[b],ids[k],0,0,&type4_context);
  assert(ok==(b==1&&k==0));
  assert(recorded.calls==n+(unsigned)ok);
  if(ok)assert(recorded.slot==385);
 }
 for(int k=0;k<5;k++)assert(!render_mirror_enemy_tile(game_screen,94,73,spriteSheet11,ids[k],0,0,&type4_context));
}
static void binding(unsigned mask)
{
 /* Each of five members may be requested first. Only that member is loaded;
  * no family-wide atomic cache or failure propagation is allowed. */
 for(int first=0;first<5;first++) {
  reset();assert(draw(ids[first],0,0)==!!(mask&(1u<<first)));
  for(int k=0;k<5;k++)assert(assets[369+k].initialized==(k==first));
  for(unsigned filter=0;filter<256;filter++)for(int t=0;t<20;t++)for(int q=0;q<4;q++) {
   unsigned k=(order[t]-159)/2,before=recorded.calls;
   bool ok=draw(order[t],q,(int)filter);
   assert(ok==!!(mask&(1u<<k))&&recorded.calls==before+(unsigned)ok);
   if(ok) {
    Asset *a=&assets[369+k];
    assert(recorded.slot==(int)(369+k));
    assert(a->bank==101&&a->index==(int)order[t]&&a->w==24&&a->h==28);
    assert(a->anchor_x==6&&a->anchor_y==7&&a->density==8);
    assert(recorded.x==94&&recorded.y==73&&recorded.style==MIRROR_NORMAL&&recorded.filter==(int)filter);
    assert(recorded.part_present&&recorded.part.x==quadrants[q][0]+6&&recorded.part.y==quadrants[q][1]+7);
    assert(recorded.part.w==12&&recorded.part.h==14);
   }
  }
  for(int k=0;k<5;k++) {
   assert(reads[k][1]==1&&reads[k][0]==!(mask&(1u<<k)));
   assert(assets[369+k].initialized&&assets[369+k].valid==!!(mask&(1u<<k)));
   const int badparts[5]={-1,2,18,21,100};
   for(unsigned j=0;j<sizeof(badparts)/sizeof(*badparts);j++)
    assert(!render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[0],ids[k],badparts[j],0,&type4_context));
  }
  other_banks();
 }
 Uint8 foreign[2]={0};Sprite2_array other={foreign,2};
 assert(!render_mirror_enemy_tile(game_screen,94,73,other,159,0,0,NULL));
 assert(!render_mirror_enemy_tile(NULL,94,73,enemySpriteSheets[0],159,0,0,NULL));
 for(unsigned id=158;id<=168;id+=2)assert(!draw(id,0,0));
 reset();puts("PASS five first-member orders x 256 filters x 20 steps x four ordered quadrants; independent per-member fallback/cache; neighbor153 and other banks");
}
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
 for(int k=0;k<5;k++) {
  assert(draw(ids[k],0,0));Asset *a=&assets[369+k];
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
static void gates(void)
{
 const char *pack=game_probe_assets;
 for(int mode=0;mode<10;mode++) {
  reset();
  if(mode==0)game_probe_missing=true;if(mode==1)game_probe_invalid=true;
  if(mode==2)game_probe_density=4;if(mode==3)game_probe_density=1;
  if(mode==4)game_probe_scene_assets=0;if(mode==5)game_probe_scene_assets=2;
  if(mode==6)active=false;if(mode==7)game_probe_assets=NULL;
  if(mode==8)reject_reason="unit";if(mode==9)game_probe_assets="/no-such-type4-unit-pack";
  for(int k=0;k<5;k++)assert(!draw(ids[k],0,0));
  assert(!recorded.calls);game_probe_assets=pack;
 }
 /* A failed allocation poisons only that member's cached load. Neighbors and
  * other banks continue; retrying all five does not silently reload it. */
 for(int first=0;first<5;first++) {
  reset();fail_allocation=0;
  assert(!draw(ids[first],0,0)&&assets[369+first].initialized&&!assets[369+first].valid);
  fail_allocation=-1;
  for(int k=0;k<5;k++)assert(draw(ids[k],0,0)==(k!=first));
  for(int k=0;k<5;k++)assert(reads[k][1]==1&&reads[k][0]==(k==first));
  other_banks();reset();assert(draw(ids[first],0,0));
 }
 reset();puts("PASS selected-pack/missing/invalid/density/scene/active/rejection gates and independent allocation-failure/cache behavior");
}
static void trace(void)
{
 G101EnemyContext c={.type=1,.size=0};
 for(unsigned b=0;b<=36;b++) {
  reset();enemySpriteSheetIds[3]=b;
  for(unsigned id=0;id<=700;id++)if(render_mirror_enemy_tile(game_screen,94,73,enemySpriteSheets[3],id,0,0,&c))
   printf("enemy %u %u %d\n",b,id,recorded.slot);
 }
 enemySpriteSheetIds[3]=0;
 for(unsigned type=391;type<=394;type++) {
  reset();c.type=type;
  for(unsigned id=0;id<=700;id++)if(render_mirror_enemy_tile(game_screen,94,73,spriteSheet11,id,0,0,&c))
   printf("pickup %u %u %d\n",type,id,recorded.slot);
 }
 reset();
}
int main(int argc,char **argv)
{
 assert(argc==4);game_probe_assets=argv[1];
 Uint8 data[5][2]={{0}};unsigned bank_ids[4]={1,2,9,0};
 for(int i=0;i<4;i++){enemySpriteSheets[i]=(Sprite2_array){data[i],2};enemySpriteSheetIds[i]=bank_ids[i];}
 spriteSheet11=(Sprite2_array){data[4],2};
 if(!strcmp(argv[2],"trace"))trace();
 else if(!strcmp(argv[2],"filter"))filters();
 else if(!strcmp(argv[2],"gates"))gates();
 else {assert(!strcmp(argv[2],"test"));binding((unsigned)strtoul(argv[3],NULL,0));}
 reset();return 0;
}
