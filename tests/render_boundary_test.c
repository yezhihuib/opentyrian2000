/* SPDX-License-Identifier: GPL-2.0-or-later
 * Isolated generic rendering observer. No original art, levels, RNG or profiles.
 */
#include <assert.h>
#ifdef NDEBUG
#error This independent fixture requires active assertions
#endif
#ifdef _MSC_VER
#include <crtdbg.h>
#endif
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
/* PRODUCTION_ENUMS */
#define MIN(a,b) ((a)<(b)?(a):(b))
#define SDL_SwapLE16(x) (x)
typedef int G101Record;
typedef int PCapRecord;
typedef int Forest13Record;
typedef int GreenBackground;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
typedef struct {Asset *a;int x,y;} GreenHead;
typedef struct {bool valid;uint64_t last_tick;int logical_index,visual_index;} TalonBank;
static Asset assets[567];
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static bool active=true,shared_hud_frame,global_talon_frame,global_shield_frame,global_pulse_frame,
 global_hitflare_frame,global_small_explosion_frame,global_rotor_frame,global_cash25_frame,
 global_green_frame,global_smoke_frame,global_vulcan_frame;
static bool xmas,twoPlayerMode,galagaMode,twoPlayerLinked,asteroid_hd_enabled;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend;
static int game_probe_density=4;
static const char *game_probe_assets,*reject_reason;
static char global_asset_directory[1024];
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,
 gem250_fixed_value,data_fixed_value,fixed_pickup_flash,suppress,suppress_green_smoke,suppress_cloud;
static Asset *pulsing272_draw_lease,*triple275_draw_lease,*columns276_draw_lease,*turret273_draw_lease,
 *projectile304_draw_lease,*firing270_draw_lease,*firing285_draw_lease,*enemy_orb112113_draw_lease,*terrain144_draw_lease;
static TalonBank talon_banks[2];
static unsigned banking_draw_player;
static uint64_t mirror_logic_tick;
static Uint32 rgb_palette[256];
static SDL_Surface screen,display,*game_screen=&screen,*VGAScreen=&screen,*canvas=&display;
static Uint8 indexed[320*200],expected[320*200],selected[320*200];
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static GreenHead green_heads[256];
static unsigned green_head_count,region_count,local_entities,draws,occlusions;
static HdRegion regions[1024];
/* FEATURE_STUBS */
static bool read_asset(Asset *a,int d){(void)a;(void)d;assert(!"authoring excluded");return false;}
static void render_mirror_unsupported(const char *reason){reject_reason=reason;}
static bool draw_asset(int,int,Asset *,int,const SDL_Rect *);
static void render_mirror_pixel(SDL_Surface *,Uint8 *,Uint8,int);
static void render_mirror_entity_end(void);
/* PRODUCTION_FUNCTIONS */

static Uint8 source_a[1024],source_b[1024];
static void bank_init(Uint8 *bank,Uint8 color)
{
 memset(bank,0,1024);
 for(unsigned i=0;i<256;i++){bank[i*2]=0;bank[i*2+1]=2;}
 unsigned n=512;
 for(unsigned y=0;y<14;y++){bank[n++]=0xc0;for(unsigned x=0;x<12;x++)bank[n++]=color;bank[n++]=0;}
 bank[n]=15;
}
static void clear_assets(void)
{for(unsigned i=0;i<567;i++){free(assets[i].rgba);memset(assets+i,0,sizeof(assets[i]));}}
static void setup(int density)
{
 clear_assets();game_probe_density=density;
 static SDL_PixelFormat indexed_format={8,1},rgba_format={32,4};
 screen=(SDL_Surface){320,200,320,indexed,&indexed_format};
 display=(SDL_Surface){320*density,200*density,320*density*4,NULL,&rgba_format};
 size_t n=(size_t)display.w*display.h;
 display.pixels=calloc(n,sizeof(Uint32));hd_owner=calloc(n,1);cloud_owner=calloc(n,1);
 green_first=calloc(n,sizeof(Uint16));green_under=calloc(n,sizeof(Uint32));green_under_owner=calloc(n,1);
 assert(display.pixels&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);
 spriteSheet8=(Sprite2_array){sizeof(source_a),source_a};spriteSheet9=(Sprite2_array){sizeof(source_b),source_b};
 memset(indexed,0,sizeof(indexed));memset(expected,0,sizeof(expected));memset(selected,0,sizeof(selected));
 region_count=draws=occlusions=green_head_count=0;reject_reason=NULL;render_mirror_entity_end();
 for(size_t p=0;p<n;p++)((Uint32 *)display.pixels)[p]=palette_rgb(0);
}
static void teardown(void)
{
 clear_assets();free(display.pixels);free(hd_owner);free(cloud_owner);free(green_first);
 free(green_under);free(green_under_owner);
}
static uint64_t index_hash(const Uint8 *p,size_t n)
{uint64_t h=UINT64_C(14695981039346656037);for(size_t i=0;i<n;i++)h=(h^p[i])*UINT64_C(1099511628211);return h;}
static void valid_source(Sprite2_array bank,unsigned index,Uint8 expected_color)
{
 Uint8 colors[168]={0},mask[168]={0};
 assert(decode_tile(bank,index,colors,mask,12,0,0));
 for(unsigned i=0;i<168;i++)assert(colors[i]==expected_color&&mask[i]==255);
}
static void clipping_case(int density,int x,int y,bool baseline,bool quad)
{
 setup(density);
 Sprite2_array bank=quad?spriteSheet9:spriteSheet8;
 unsigned index=quad?229:59;
 int width=quad?24:12;
 bool wraps=x<0||x>320-width;
 assert(active&&!game_probe_assets&&!game_probe_missing&&!game_probe_invalid&&!game_probe_original_reference&&!global_asset_directory[0]);
 const unsigned parts[4]={0,1,19,20};
 for(unsigned i=0;i<(quad?4u:1u);i++)valid_source(bank,index+parts[i],quad?0x42:0x21);
 draw_entity_sprite2(&screen,x,y,bank,index,ENTITY_NORMAL,quad?ENTITY_QUAD:ENTITY_TILE);
 assert(!reject_reason&&!suppress&&!suppress_cloud&&!suppress_green_smoke);
 assert(!memcmp(indexed,expected,sizeof(indexed)));
 unsigned mismatches=0,writes=0;
 for(int py=0;py<200;py++)for(int px=0;px<320;px++)if(indexed[py*320+px]) {
  writes++;
  Uint32 got=((Uint32 *)display.pixels)[(py*density)*display.w+px*density];
  if((got&0xffffffu)!=(rgb_palette[indexed[py*320+px]]&0xffffffu))mismatches++;
 }
 assert(writes);
 uint64_t native_hash=index_hash(indexed,sizeof(indexed));
 if(baseline&&wraps)assert(mismatches&&draws==1);
 else assert(!mismatches&&draws==(unsigned)!wraps);
 /* A later ordinary pixel must not inherit the entity's suppress lease. */
 indexed[100*320+100]=0x42;render_mirror_pixel(&screen,indexed+100*320+100,0x42,MIRROR_NORMAL);
 assert(((Uint32 *)display.pixels)[(100*density)*display.w+100*density]==palette_rgb(0x42));
 printf("clip d=%d %s x=%d y=%d original_writes=%u mismatches=%u hd_draws=%u source_valid=1 index_hash=%016llx\n",density,quad?"quad":"tile",x,y,writes,mismatches,draws,(unsigned long long)native_hash);
 teardown();
}
static void cache_cases(bool baseline)
{
 setup(4);
 valid_source(spriteSheet8,59,0x21);valid_source((Sprite2_array){sizeof(source_b),source_b},59,0x42);
 Asset *a=get_asset(spriteSheet8,59,ENTITY_TILE);assert(a&&a->rgba[0]==0x12);
 assert(a->initialized&&a->valid&&a->w==12&&a->h==14&&a->density==4&&a->rgba[1]==0x34&&a->rgba[2]==0x56&&a->rgba[3]==255);
 Uint8 *warm_rgba=a->rgba;assert(get_asset(spriteSheet8,59,ENTITY_TILE)==a&&a->rgba==warm_rgba&&!reject_reason);
 puts("cache_precondition source_a_valid=1 source_b_valid=1 initialized=1 valid=1 warm_hit=1 rgba=123456ff density=4");
 spriteSheet8=(Sprite2_array){sizeof(source_b),source_b};
 a=get_asset(spriteSheet8,59,ENTITY_TILE);
 printf("cache_pointer declined=%d reason=%s\n",a==NULL,reject_reason?reject_reason:"none");
 if(!baseline){assert(!a&&reject_reason&&!assets[5].rgba);reject_reason=NULL;a=get_asset(spriteSheet8,59,ENTITY_TILE);}
 assert(a);
 assert(a->rgba[0]==(baseline?0x12:0xab));
 printf("cache_pointer_recovery rgba=%02x%02x%02x%02x valid=%d density=%d\n",a->rgba[0],a->rgba[1],a->rgba[2],a->rgba[3],a->valid,a->density);
 spriteSheet8.size=2;a=get_asset(spriteSheet8,59,ENTITY_TILE);
 printf("cache_size declined=%d reason=%s\n",a==NULL,reject_reason?reject_reason:"none");
 assert(baseline?a!=NULL:a==NULL);
 if(!baseline){assert(reject_reason&&!assets[5].rgba);reject_reason=NULL;assert(!get_asset(spriteSheet8,59,ENTITY_TILE));}
 spriteSheet8.size=sizeof(source_b);a=get_asset(spriteSheet8,59,ENTITY_TILE);
 assert(a&&a->rgba[0]==(baseline?0x12:0xab));
 assert(a->valid&&a->density==4);
 printf("cache_final_recovery rgba=%02x%02x%02x%02x valid=%d density=%d\n",a->rgba[0],a->rgba[1],a->rgba[2],a->rgba[3],a->valid,a->density);
 puts(baseline?"cache: reproduced stale pointer+length reuse":"cache: pointer+length changes rebuild or decline; valid source recovers");
 teardown();
}
int main(int argc,char **argv)
{
#ifdef _MSC_VER
 _set_error_mode(_OUT_TO_STDERR);
 _set_abort_behavior(0,_WRITE_ABORT_MSG|_CALL_REPORTFAULT);
 _CrtSetReportMode(_CRT_ASSERT,_CRTDBG_MODE_FILE);_CrtSetReportFile(_CRT_ASSERT,_CRTDBG_FILE_STDERR);
#endif
 setvbuf(stdout,NULL,_IONBF,0);
 assert(argc==2||argc==3);bool baseline=!strcmp(argv[1],"baseline");
 bool only_cache=argc==3&&!strcmp(argv[2],"cache"),only_clips=argc==3&&!strcmp(argv[2],"clips");
 assert(argc==2||only_cache||only_clips);
 bank_init(source_a,0x21);bank_init(source_b,0x42);
 rgb_palette[0]=0;rgb_palette[0x21]=0x123456;rgb_palette[0x42]=0xabcdef;
 if(!only_clips)cache_cases(baseline);
 if(!only_cache)for(int d=4;d<=8;d+=4){
  for(unsigned q=0;q<2;q++){
   clipping_case(d,-1,50,baseline,q);clipping_case(d,q?297:309,50,baseline,q);
   clipping_case(d,0,50,baseline,q);clipping_case(d,q?296:308,50,baseline,q);
   clipping_case(d,100,-1,baseline,q);clipping_case(d,100,199,baseline,q);
  }
 }
 if(!baseline&&!only_cache){
  setup(8);
  const int values[]={INT_MIN,INT_MAX,-1000000,1000000};
  for(unsigned i=0;i<4;i++){
   assert(!render_mirror_entity(&screen,values[i],50,spriteSheet8,59,MIRROR_NORMAL,ENTITY_TILE));
   assert(!render_mirror_entity(&screen,50,values[i],spriteSheet8,59,MIRROR_NORMAL,ENTITY_TILE));
  }
  assert(!draws&&!reject_reason);teardown();puts("integer extremes: rejected before scale/multiply");
 }
 puts("PASS");return 0;
}
