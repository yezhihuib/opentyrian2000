/* Focused production loader/source/hook and original RLE tests. No engine run. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void*pixels;SDL_PixelFormat*format;} SDL_Surface;
typedef struct {Uint8*data;size_t size;} Sprite2_array;
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW,ENTITY_TILE=0,ENTITY_QUAD=1};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#define MIN(a,b) ((a)<(b)?(a):(b))
#include "types.inc"
static bool xmas,active=true,game_probe_missing,game_probe_invalid,game_probe_original_reference;
static int game_probe_density=8;static const char*game_probe_assets,*reject_reason;
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value;
static SDL_PixelFormat format={8,1};static SDL_Surface screen={320,200,320,NULL,&format},*game_screen=&screen,*VGAScreen=&screen;
static unsigned banking_draw_player;static uint64_t mirror_logic_tick;static TalonBank talon_banks[2];
static struct{const Uint8*rgba;char path[1024];}vulcan_shadow_resource[13],vulcan_shadow_coverage_resource[3];
static unsigned draw_calls,pixel_calls,shadow_begins,shadow_ends;static int last_style,last_x,last_y;
static int vulcan_shadow_member(unsigned index){(void)index;return -1;}
static void render_mirror_shadow_end(void){shadow_ends++;}
static bool draw_vulcan_shadow(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;assert(0);return false;}
static bool cash25_surface_ready(SDL_Surface*s,int x,int y){(void)s;(void)x;(void)y;assert(0);return false;}
#define cash25_family_ready() false
#define cash75_family_ready() false
#define cash50_family_ready() false
#define gem100_family_ready() false
#define gem250_family_ready() false
#define game_probe_scene_draw(...) ((void)0)
static Asset*talon_frame(unsigned i){(void)i;assert(0);return NULL;}
static bool draw_asset(int x,int y,Asset*a,int style,const SDL_Rect*p){assert(a&&a->valid&&!p);draw_calls++;last_style=style;last_x=x;last_y=y;return true;}
#include "functions.inc"
static Uint16 SDL_SwapLE16(Uint16 v){Uint8 b[2];memcpy(b,&v,2);return(Uint16)(b[0]|b[1]<<8);}
#define asset_debug_effect(...) ((void)0)
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define load_font_arrow_sprite_end() ((void)0)
#define pregame_font_sprite2_end() ((void)0)
static void render_mirror_shadow_begin(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(s==&screen&&b.data==spriteSheet8.data&&i==27);(void)x;(void)y;shadow_begins++;}
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style){assert(s==&screen&&p>=(Uint8*)s->pixels&&p<(Uint8*)s->pixels+s->pitch*s->h);(void)v;assert(style==MIRROR_NORMAL||style==MIRROR_SHADOW);pixel_calls++;}
#include "blitters.inc"
static unsigned cases,identity_cases,variants,shadow_cases,index_checks;
static Uint8*read_file(const char*p,size_t*n){FILE*f=fopen(p,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long z=ftell(f);assert(z>0&&!fseek(f,0,SEEK_SET));Uint8*r=malloc((size_t)z);assert(r&&fread(r,1,(size_t)z,f)==(size_t)z&&!fclose(f));*n=(size_t)z;return r;}
static void clear_assets(void){for(size_t i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}}
static void head(bool accepted){unsigned before=draw_calls;bool got=render_mirror_entity(&screen,94,73,spriteSheet8,27,MIRROR_NORMAL,ENTITY_TILE);assert(got==accepted&&draw_calls==before+(unsigned)accepted);if(accepted){assert(last_style==MIRROR_NORMAL&&last_x==94&&last_y==73);Asset*a=&assets[535];assert(a->valid&&a->bank==8&&a->index==27&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&a->density==8);}cases++;}
static void identity(Uint8*normal,size_t ns,Uint8*christmas,size_t cs,const char*full){
 game_probe_assets=full;size_t cap=ns>cs?ns:cs;Uint8*allocation=malloc(cap);assert(allocation);
 for(int warm=0;warm<2;warm++){
  clear_assets();memcpy(allocation,normal,ns);spriteSheet8=(Sprite2_array){allocation,ns};xmas=false;
  if(warm)head(true);Uint8*loaded=assets[535].rgba;
  xmas=true;head(false);assert(assets[535].rgba==loaded);xmas=false;
  memcpy(allocation,christmas,cs);spriteSheet8.size=cs;head(false);assert(assets[535].rgba==loaded);
  xmas=true;head(false);xmas=false;
  memcpy(allocation,normal,ns);spriteSheet8.size=ns;head(true);loaded=assets[535].rgba;
  size_t p=(size_t)allocation[52]|((size_t)allocation[53]<<8);while(!(allocation[p]>>4))p++;Uint8 saved=allocation[p+1];allocation[p+1]^=1;head(false);allocation[p+1]=saved;head(true);assert(assets[535].rgba==loaded);
  saved=allocation[p];allocation[p]=(saved&0xf0)|((saved+1)&15);head(false);allocation[p]=saved;head(true);
  spriteSheet8.size=54;head(false);spriteSheet8.size=ns;head(true);
  spriteSheet8.size=0;head(false);spriteSheet8.size=ns;head(true);
  assert(get_asset(spriteSheet8,27,ENTITY_QUAD)==NULL);assert(get_asset(spriteSheet9,27,ENTITY_TILE)==NULL);
  Sprite2_array other={normal,ns};assert(get_asset(other,27,ENTITY_TILE)==NULL);
  SDL_Surface alternate=screen;unsigned before=draw_calls;assert(!render_mirror_entity(&alternate,94,73,spriteSheet8,27,MIRROR_NORMAL,ENTITY_TILE)&&draw_calls==before);
  active=false;head(false);active=true;reject_reason="test";head(false);reject_reason=NULL;
  identity_cases+=17;
 }
 clear_assets();free(allocation);spriteSheet8=(Sprite2_array){normal,ns};
}
static void resource(const char*root){char line[2048];FILE*f;snprintf(line,sizeof(line),"%s/variants.tsv",root);f=fopen(line,"r");assert(f);
 char name[128];int expected,density;
 while(fscanf(f,"%127s %d %d",name,&expected,&density)==3){
  char path[2048];snprintf(path,sizeof(path),"%s/%s",root,name);clear_assets();game_probe_assets=path;
  Asset*a=get_asset(spriteSheet8,27,ENTITY_TILE);assert((a!=NULL)==expected);if(a){assert(a->density==density&&a->bank==8&&a->index==27&&!a->anchor_x&&!a->anchor_y);assert(a->rgba&&a->w==12&&a->h==14);}
  assert(get_asset(spriteSheet8,27,ENTITY_TILE)==a);variants++;
 }
 fclose(f);clear_assets();
}
static void shadows(const char*full,Uint8*normal,size_t ns){
 clear_assets();game_probe_assets=full;spriteSheet8=(Sprite2_array){normal,ns};game_probe_density=8;head(true);
 Uint8 colors[168]={0},mask[168]={0};assert(decode_tile(spriteSheet8,27,colors,mask,12,0,0));unsigned support=0;for(int i=0;i<168;i++)support+=mask[i]!=0;assert(support==37);
 Uint8 actual[328*200],oracle[328*200];screen.pixels=actual;
 const int xy[][2]={{94,73},{0,0},{308,0},{0,-13},{308,-1},{94,187},{0,199},{308,199},{-3,73},{315,73},{94,-14},{94,200}};
 for(int pitch=320;pitch<=328;pitch+=8){screen.pitch=pitch;
  for(unsigned j=0;j<sizeof(xy)/sizeof(*xy);j++)for(int warm=0;warm<2;warm++){
   if(!warm){clear_assets();}else head(true);
   for(int i=0;i<328*200;i++)actual[i]=oracle[i]=(Uint8)(i*29+23);
   int x=xy[j][0],y=xy[j][1];unsigned before=draw_calls;assert(!render_mirror_entity(&screen,x,y,spriteSheet8,27,MIRROR_SHADOW,ENTITY_TILE));assert(draw_calls==before);
   for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(mask[yy*12+xx]){int p=(y+yy)*pitch+x+xx;if(p>=0&&p<pitch*200)oracle[p]=(oracle[p]&0xf0)|((oracle[p]&15)/2);}
   pixel_calls=0;blit_sprite2_darken(&screen,x,y,spriteSheet8,27);assert(!memcmp(actual,oracle,sizeof(actual)));index_checks+=sizeof(actual);shadow_cases++;
   // Also prove the normal original-index write is unchanged by a successful head hook.
   for(int i=0;i<328*200;i++)actual[i]=oracle[i]=(Uint8)(i*29+23);
   for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(mask[yy*12+xx]){int p=(y+yy)*pitch+x+xx;if(p>=0&&p<pitch*200)oracle[p]=colors[yy*12+xx];}
   blit_sprite2(&screen,x,y,spriteSheet8,27);assert(!memcmp(actual,oracle,sizeof(actual)));index_checks+=sizeof(actual);
  }
 }
 screen.pitch=320;screen.pixels=NULL;clear_assets();
}
int main(int argc,char**argv){assert(argc==4);size_t ns,cs;Uint8*normal=read_file(argv[1],&ns),*christmas=read_file(argv[2],&cs);spriteSheet8=(Sprite2_array){normal,ns};Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){tokens,1};spriteSheet12=(Sprite2_array){tokens+1,1};explosionSpriteSheet=(Sprite2_array){tokens+2,1};char full[2048];snprintf(full,sizeof(full),"%s/valid",argv[3]);
 identity(normal,ns,christmas,cs,full);resource(argv[3]);game_probe_assets=full;game_probe_density=1;head(false);game_probe_density=8;game_probe_missing=true;head(false);game_probe_missing=false;game_probe_invalid=true;head(false);game_probe_invalid=false;clear_assets();head(true);shadows(full,normal,ns);free(normal);free(christmas);
 printf("{\"status\":\"PASS\",\"head_calls\":%u,\"identity_cases\":%u,\"resource_variants\":%u,\"shadow_cases\":%u,\"indexed_bytes_checked\":%u,\"game_runs\":0}\n",cases,identity_cases,variants,shadow_cases,index_checks);return 0;}
