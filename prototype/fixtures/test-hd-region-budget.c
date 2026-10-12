/* Extracted production functions, independent per-channel pixel oracle.
 * This executable is a bounded unit harness. It never starts the game or SDL. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int w,h,pitch;void *pixels;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
enum {ENTITY_TILE,ENTITY_QUAD};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#include "production-types.inc"
static Uint8 bank_tokens[5];
static Sprite2_array spriteSheet8={bank_tokens,1},spriteSheet9={bank_tokens+1,1},explosionSpriteSheet={bank_tokens+3,1};
static SDL_Surface screen,*canvas,*output,*game_screen=&screen;
static bool active=true,suppress,suppress_green_smoke,suppress_cloud;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend,game_probe_known_blend;
static const char *reject_reason,*game_probe_assets=".";
static int game_probe_density=8;
static Uint32 rgb_palette[256];
static Uint8 selected[320*200],restored_mask[320*200],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static GreenHead green_heads[256];
static unsigned int green_head_count,region_count,draws,local_entities,local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
static unsigned int banking_draw_player;
static uint64_t mirror_logic_tick;
static TalonBank talon_banks[2];
static const int original_visual_indices[5]={0,2,6,10,12};
static unsigned long long checks;
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(3);}checks++;}while(0)
static void game_probe_restore_region(unsigned int n,SDL_Rect a,SDL_Rect b,unsigned int g,unsigned int k){(void)n;(void)a;(void)b;(void)g;(void)k;}
static bool last_output_valid,have_fade_saved,ready,game_probe_enabled=true,have_initial_palette;
static bool fast_forward;
static int fade_mode;
static Uint32 initial_palette[256];
static Uint8 expected[320*200];
static unsigned int occlusions,mismatch,brightness_blocks,restored_checks,restored_mismatches;
static char all_rejections[512];
#define SDL_PIXELFORMAT_ARGB8888 1
static bool asset_debug_fast_forward(void){return fast_forward;}
static SDL_Surface *SDL_CreateRGBSurfaceWithFormat(unsigned f,int w,int h,int b,unsigned fmt)
{(void)f;(void)b;(void)fmt;SDL_Surface*s=malloc(sizeof(*s));CHECK(s);*s=(SDL_Surface){w,h,w*4+12,NULL};s->pixels=malloc((size_t)s->pitch*h);CHECK(s->pixels);memset(s->pixels,0xcd,(size_t)s->pitch*h);return s;}
static void render_mirror_unsupported(const char *reason);
#include "production-helpers.inc"
static Uint8 parent_rgba[4]={180,90,30,127},head_rgba[4]={200,220,90,128},smoke_rgba[4]={20,170,90,80};
static void cache_assets(void)
{
 assets[325]=(Asset){true,true,8,103,1,1,0,0,1,parent_rgba};
 assets[182]=(Asset){true,true,8,214,1,1,0,0,1,head_rgba};
 assets[175]=(Asset){true,true,ASSET_EXPLOSION,78,1,1,0,0,1,smoke_rgba};
}
static Uint32 alpha(Uint32 dst,const Uint8*s)
{Uint32 out=0xff000000;for(int c=0;c<3;c++){unsigned shift=(2-c)*8,n=((dst>>shift)&255)*(255-s[3])+s[c]*s[3];out|=(n/255+(n%255>=128))<<shift;}return out;}
static uint64_t digest(void)
{uint64_t h=1469598103934665603ULL;for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++){size_t n=(size_t)y*canvas->w+x;Uint32 v=*((Uint32*)((Uint8*)canvas->pixels+y*canvas->pitch)+x);for(int b=0;b<4;b++){h^=(v>>(8*b))&255;h*=1099511628211ULL;}h^=hd_owner[n];h*=1099511628211ULL;h^=green_first[n];h*=1099511628211ULL;h^=cloud_owner[n];h*=1099511628211ULL;}return h;}
static void begin(void)
{render_mirror_begin();CHECK(active&&!reject_reason&&!region_count&&!green_head_count&&!suppress&&!suppress_cloud&&!suppress_green_smoke&&!all_rejections[0]);CHECK(!draws&&!occlusions&&!mismatch&&!local_entities&&!local_regions&&!local_blocks);}
static bool parent(int x,int y,int style)
{bool ok=render_mirror_entity(game_screen,x,y,spriteSheet8,103,style,ENTITY_TILE);render_mirror_entity_end();return ok;}
static void green_scene(void)
{
 begin();CHECK(render_mirror_entity(game_screen,5,5,spriteSheet8,214,MIRROR_NORMAL,ENTITY_TILE));render_mirror_entity_end();CHECK(region_count==1&&green_head_count==1);
 CHECK(render_mirror_entity(game_screen,5,5,explosionSpriteSheet,78,MIRROR_BLEND,ENTITY_TILE));render_mirror_entity_end();CHECK(region_count==2&&green_head_count==1);
 Uint32 base=palette_rgb(17);unsigned peak=MAX((base>>16)&255,MAX((base>>8)&255,base&255)),next=(170+peak+1)/2;Uint8 adj[4];for(int c=0;c<3;c++)adj[c]=(smoke_rgba[c]*next+85)/170;adj[3]=smoke_rgba[3];Uint32 under=alpha(base,adj),want=alpha(under,head_rgba);
 int d=game_probe_density;
 for(int y=5*d;y<6*d;y++)for(int x=5*d;x<6*d;x++){int n=y*canvas->w+x;CHECK(*((Uint32*)((Uint8*)canvas->pixels+y*canvas->pitch)+x)==want);CHECK(green_first[n]==1&&green_under[n]==under&&green_under_owner[n]==1&&hd_owner[n]==1);}
 CHECK(parent(5,5,MIRROR_NORMAL));CHECK(!green_first[5*d*canvas->w+5*d]);CHECK(parent(5,5,MIRROR_SHADOW));
 Uint8 *q=(Uint8*)game_screen->pixels+5*game_screen->pitch+5;*q=42;render_mirror_pixel(game_screen,q,42,MIRROR_NORMAL);
 for(int y=5*d;y<6*d;y++)for(int x=5*d;x<6*d;x++){int n=y*canvas->w+x;CHECK(*((Uint32*)((Uint8*)canvas->pixels+y*canvas->pitch)+x)==palette_rgb(42));CHECK(!green_first[n]&&!hd_owner[n]);}
 *q=17;
}
static void overflow_case(void)
{
 begin();size_t cap=sizeof(regions)/sizeof(*regions);CHECK(cap==65536&&sizeof(HdRegion)==32&&sizeof(regions)==2097152);
 /* Seed valid distinct records in O(n), then use production registration at the boundary. */
 for(unsigned i=0;i<cap-1;i++)regions[i]=(HdRegion){{-3-(int)i,-3,1,1},8,103,MIRROR_NORMAL,true};
 region_count=(unsigned int)cap-1;
 CHECK(parent(-3-(int)(cap-1),-3,MIRROR_NORMAL));CHECK(region_count==cap&&!reject_reason);
 CHECK(parent(-3,-3,MIRROR_NORMAL));CHECK(region_count==cap);uint64_t before=digest();unsigned old_draws=draws;CHECK(!parent(0,0,MIRROR_NORMAL));CHECK(region_count==cap&&draws==old_draws&&digest()==before);CHECK(reject_reason&&!strcmp(reject_reason,"hd-region-capacity"));CHECK(!strcmp(all_rejections,"hd-region-capacity"));CHECK(!suppress);
 CHECK(!parent(-3,-3,MIRROR_NORMAL));CHECK(region_count==cap&&digest()==before);begin();CHECK(parent(0,0,MIRROR_NORMAL)&&region_count==1);
 /* Dead region records are not silently reused: their existing semantics stay. */
 restore_classic_rect((SDL_Rect){0,0,1,1});CHECK(!regions[0].live&&region_count==1);CHECK(parent(0,0,MIRROR_NORMAL)&&region_count==2);
 /* 1122 conservative demands fit without relying on duplicate suppression. */
 begin();for(int i=0;i<1122;i++)CHECK(parent(-3-i,-3,MIRROR_NORMAL));CHECK(region_count==1122&&!reject_reason);
 /* Four ordinary enemy quadrant draws normalize to one rectangle. */
 begin();Uint8 qrgba[24*28*4];for(int i=0;i<24*28;i++)memcpy(qrgba+4*i,parent_rgba,4);Asset enemy={true,true,ASSET_NEWSH2,153,24,28,6,7,1,qrgba};
 for(int j=0;j<100;j++)for(int part=0;part<4;part++){SDL_Rect r={(part%2)*12,(part/2)*14,12,14};CHECK(draw_asset_filtered(-40-j*25,-40,&enemy,MIRROR_NORMAL,&r,0));render_mirror_entity_end();CHECK(region_count==(unsigned)j+1);}
 CHECK(region_count==100&&!reject_reason);
 /* Reset executes after full capacity, including all ownership state. */
 region_count=65536;green_head_count=17;reject_reason="sentinel";strcpy(all_rejections,"sentinel");suppress=suppress_cloud=suppress_green_smoke=true;memset(hd_owner,1,(size_t)canvas->w*canvas->h);memset(cloud_owner,1,(size_t)canvas->w*canvas->h);memset(green_first,1,(size_t)canvas->w*canvas->h*2);begin();
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++){size_t n=(size_t)y*canvas->w+x;CHECK(!hd_owner[n]&&!cloud_owner[n]&&!green_first[n]);CHECK(*((Uint32*)((Uint8*)canvas->pixels+y*canvas->pitch)+x)==palette_rgb(17));}
 game_probe_enabled=false;render_mirror_begin();CHECK(!active&&!parent(0,0,MIRROR_NORMAL));game_probe_enabled=true;fast_forward=true;render_mirror_begin();CHECK(!active&&!parent(0,0,MIRROR_NORMAL));fast_forward=false;begin();CHECK(parent(0,0,MIRROR_NORMAL));
}
int main(int argc,char**argv)
{
 CHECK(argc==2);bool stress=!strcmp(argv[1],"stress");screen=(SDL_Surface){320,200,328,NULL};screen.pixels=malloc((size_t)screen.pitch*screen.h);CHECK(screen.pixels);memset(screen.pixels,17,(size_t)screen.pitch*screen.h);for(int i=0;i<256;i++)rgb_palette[i]=((Uint32)((i*3)%256)<<16)|((Uint32)((i*7)%256)<<8)|((i*11)%256);cache_assets();
 for(int d=2;d<=8;d*=2){game_probe_density=d;begin();green_scene();for(int i=0;i<120;i++)CHECK(parent((i*13)%320,(i*7)%200,i%2?MIRROR_NORMAL:MIRROR_SHADOW));CHECK(region_count<=124&&!reject_reason);printf("composition d=%d digest=%016llx regions=%u green=%u\n",d,(unsigned long long)digest(),region_count,green_head_count);if(stress)overflow_case();
  for(int y=0;y<canvas->h;y++)for(int x=canvas->w*4;x<canvas->pitch;x++)CHECK(((Uint8*)canvas->pixels)[y*canvas->pitch+x]==0xcd);
  free(canvas->pixels);free(canvas);canvas=NULL;free(output->pixels);free(output);output=NULL;free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);hd_owner=cloud_owner=green_under_owner=NULL;green_first=NULL;green_under=NULL;
 }
 free(screen.pixels);printf("PASS region %s: %llu checks; capacity=%zu.\n",stress?"boundary/reset/green stress":"nonoverflow composition",checks,sizeof(regions)/sizeof(*regions));return 0;
}
