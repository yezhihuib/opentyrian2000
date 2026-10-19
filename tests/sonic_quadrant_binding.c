/* Portable, extracted-production Sonic quadrant regression harness. No engine. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef SANITIZED
#include <sanitizer/asan_interface.h>
#endif
typedef uint8_t Uint8; typedef uint16_t Uint16; typedef uint32_t Uint32;
typedef struct { int x,y,w,h; } SDL_Rect;
typedef struct { int BitsPerPixel,BytesPerPixel; } SDL_PixelFormat;
typedef struct { int w,h,pitch; void *pixels; SDL_PixelFormat *format; } SDL_Surface;
#include "sprite-type.inc"
typedef int EntityDrawStyle; typedef int EntityDrawLayout;
enum { ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW,ENTITY_TILE=0,ENTITY_QUAD=1 };
enum { MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW };
#define MIN(a,b) ((a)<(b)?(a):(b))
#define COUNT(a) (sizeof(a)/sizeof(*(a)))
#include "types.inc"
static bool asteroid_hd_enabled; /* Optional enemy catalog stays disabled here. */
static bool twoPlayerMode,galagaMode,twoPlayerLinked,xmas,active=true;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference;
static int game_probe_density=8; static const char *game_probe_assets,*reject_reason;
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value,data_fixed_value,fixed_pickup_flash;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},*game_screen=&screen,*VGAScreen=&screen;
static unsigned banking_draw_player; static uint64_t mirror_logic_tick; static TalonBank talon_banks[2];
static struct {const Uint8 *rgba; char path[1024];} vulcan_shadow_resource[17],vulcan_shadow_coverage_resource[3];
static unsigned draw_calls,original_calls,end_calls,probe_calls,file_opens,allocations;
static unsigned cases,rejects,shadow_cases,mode_cases,source_cases,resource_cases,wrapper_cases;
static size_t indexed_bytes;
static int last_x,last_y,last_style; static bool last_mirrored;
static const unsigned ids[4]={105,106,124,125};
static const unsigned previous[17]={6,44,73,63,82,16,54,130,131,149,150,223,224,242,243,143,144};
static const unsigned previous_slots[17]={546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562};
static Uint8 references[2][4][336];
static unsigned member(unsigned id) {for(unsigned k=0;k<4;k++)if(ids[k]==id)return k;assert(0);return 0;}
static int vulcan_shadow_member(unsigned id){(void)id;return -1;}
static void render_mirror_shadow_end(void){}
static bool draw_vulcan_shadow(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;return false;}
static bool cash25_surface_ready(SDL_Surface*s,int x,int y){(void)s;(void)x;(void)y;assert(0);return false;}
#define cash25_family_ready() false
#define cash75_family_ready() false
#define cash50_family_ready() false
#define gem100_family_ready() false
#define gem250_family_ready() false
#define game_probe_scene_draw(...) ((void)0)
#define fixed_pickup_flash_draw(...) (false)
#define data_value_draw(...) (false)
static Asset *talon_frame(unsigned i){(void)i;assert(0);return NULL;}
static bool draw_asset(int x,int y,Asset *a,int style,const SDL_Rect *p){assert(a&&a->valid&&!p);draw_calls++;last_x=x;last_y=y;last_style=style;return true;}
#include "functions.inc"
static Uint16 SDL_SwapLE16(Uint16 v){Uint8 b[2];memcpy(b,&v,2);return (Uint16)(b[0]|b[1]<<8);}
#define asset_debug_effect(...) ((void)0)
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define load_font_arrow_sprite_end() ((void)0)
#define pregame_font_sprite2_end() ((void)0)
static void render_mirror_shadow_begin(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(s==&screen&&b.data==spriteSheet8.data);(void)x;(void)y;(void)i;}
static struct {ptrdiff_t offset;Uint8 value;int style;} writes[200];static unsigned write_count;
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style){assert(s==&screen&&p>=(Uint8*)s->pixels&&p<(Uint8*)s->pixels+s->pitch*s->h&&write_count<COUNT(writes));writes[write_count].offset=p-(Uint8*)s->pixels;writes[write_count].value=v;writes[write_count++].style=style;}
static void render_mirror_sprite2_blend_pixel(SDL_Surface*s,Uint8*p,Uint8 v,Sprite2_array b,unsigned id,int x,int y){(void)v;(void)b;(void)id;(void)x;(void)y;render_mirror_pixel(s,p,*p,MIRROR_BLEND);}
#include "blitters.inc"
static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned id){original_calls++;production_blit_sprite2(s,x,y,b,id);}
static void blit_sprite2_blend(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned id){original_calls++;production_blit_sprite2_blend(s,x,y,b,id);}
static void blit_sprite2_darken(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned id){original_calls++;production_blit_sprite2_darken(s,x,y,b,id);}
#define blit_sprite2x2(...) assert(!"unexpected quad")
#define blit_sprite2x2_blend(...) assert(!"unexpected quad blend")
#define blit_sprite2x2_darken(...) assert(!"unexpected quad shadow")
static void render_mirror_entity_end(void){end_calls++;}
static void game_probe_draw(int role,unsigned i,int x,int y,int style,int layout,bool mirrored){assert(role==8&&layout==ENTITY_TILE);(void)i;(void)x;(void)y;(void)style;probe_calls++;last_mirrored=mirrored;}
#include "wrappers.inc"
FILE *__real_fopen(const char*,const char*);void *__real_malloc(size_t);
FILE *__wrap_fopen(const char*a,const char*b){file_opens++;return __real_fopen(a,b);}
void *__wrap_malloc(size_t n){allocations++;return __real_malloc(n);}
static Uint8 *read_file(const char *path,size_t *n){FILE*f=fopen(path,"rb");assert(f&&!fseek(f,0,SEEK_END));long len=ftell(f);assert(len>0&&!fseek(f,0,SEEK_SET));Uint8*p=malloc((size_t)len);assert(p&&fread(p,1,(size_t)len,f)==(size_t)len&&!fclose(f));*n=(size_t)len;return p;}
static void clear_assets(void){for(size_t i=0;i<COUNT(assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}}
static void flags(unsigned bits){twoPlayerMode=!!(bits&1);galagaMode=!!(bits&2);twoPlayerLinked=!!(bits&4);}
static unsigned flags_now(void){return (unsigned)twoPlayerMode|((unsigned)galagaMode<<1)|((unsigned)twoPlayerLinked<<2);}
static void unchanged(const Asset *before){assert(!memcmp(before,assets,sizeof(assets)));}
static void head(unsigned k,bool expected){unsigned before=draw_calls;bool got=render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_NORMAL,ENTITY_TILE);if(got!=expected)fprintf(stderr,"head id=%u expected=%d got=%d density=%d flags=%u xmas=%d size=%zu root=%s\n",ids[k],expected,got,game_probe_density,flags_now(),xmas,spriteSheet8.size,game_probe_assets?game_probe_assets:"NULL");assert(got==expected&&draw_calls==before+(unsigned)expected);if(got){Asset*a=&assets[QUADRANT_SLOT+k];assert(a->valid&&a->bank==8&&a->index==(int)ids[k]&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&last_x==94&&last_y==73&&last_style==MIRROR_NORMAL);}cases++;}
/* Reject before any asset cache reads, writes, allocation, or disk lookup. */
static void reject_no_cache(unsigned k){Asset before[COUNT(assets)];memcpy(before,assets,sizeof(assets));unsigned opens=file_opens,allocs=allocations,f=flags_now();bool xm=xmas;
#ifdef SANITIZED
 __asan_poison_memory_region(assets,sizeof(assets));
#endif
 assert(!get_asset(spriteSheet8,ids[k],ENTITY_TILE));head(k,false);
#ifdef SANITIZED
 __asan_unpoison_memory_region(assets,sizeof(assets));
#endif
 unchanged(before);assert(file_opens==opens&&allocations==allocs&&flags_now()==f&&xmas==xm);rejects++;
}
static void mode_and_gates(const char *root){game_probe_assets=root;
 for(int density=4;density<=8;density+=4)for(unsigned k=0;k<4;k++)for(int warm=0;warm<2;warm++)for(unsigned bits=0;bits<8;bits++){
  flags(0);game_probe_density=density;clear_assets();if(warm)head(k,true);flags(bits);if(bits)reject_no_cache(k);else head(k,true);assert(flags_now()==bits);flags(0);head(k,true);mode_cases++;
 }
 for(int density=4;density<=8;density+=4)for(unsigned k=0;k<4;k++)for(int warm=0;warm<2;warm++)for(int gate=0;gate<9;gate++){
  flags(0);game_probe_density=density;game_probe_assets=root;clear_assets();if(warm)head(k,true);
  switch(gate){case 0:game_probe_density=1;break;case 1:game_probe_density=2;break;case 2:game_probe_density=16;break;case 3:game_probe_missing=true;break;case 4:game_probe_invalid=true;break;case 5:game_probe_original_reference=true;break;case 6:game_probe_assets=NULL;break;case 7:xmas=true;break;case 8:game_probe_density=0;break;}
  reject_no_cache(k);game_probe_density=density;game_probe_missing=game_probe_invalid=game_probe_original_reference=xmas=false;game_probe_assets=root;head(k,true);
 }
 clear_assets();game_probe_density=8;
}
static size_t encode_source(Uint8 *dst,const Uint8 *colors,const Uint8 *mask){size_t n=0;for(unsigned y=0;y<14;y++){unsigned x=0;for(unsigned xx=0;xx<12;xx++)if(mask[y*12+xx]){dst[n++]=(Uint8)(0x10|(xx-x));dst[n++]=colors[y*12+xx];x=xx+1;}dst[n++]=(Uint8)(12-x);}dst[n++]=15;return n;}
static void source_matrix(Uint8 *normal,size_t ns,Uint8 *christmas,size_t cs,const char *root){size_t cap=(ns>cs?ns:cs)+512;Uint8*allocation=malloc(cap);assert(allocation);game_probe_assets=root;
 for(int density=4;density<=8;density+=4)for(unsigned k=0;k<4;k++)for(int warm=0;warm<2;warm++){
  game_probe_density=density;clear_assets();memcpy(allocation,normal,ns);spriteSheet8=(Sprite2_array){.data=allocation,.size=ns};if(warm)head(k,true);
  unsigned id=ids[k],dir=2*(id-1);size_t pos=(size_t)allocation[dir]|((size_t)allocation[dir+1]<<8);while(!(allocation[pos]>>4))pos++;
  Uint8 original=allocation[pos+1];if(!warm)clear_assets();allocation[pos+1]^=1;reject_no_cache(k);head((k+1)%4,true);allocation[pos+1]=original;head(k,true);source_cases++;
  Uint8 a=allocation[dir],b=allocation[dir+1];if(!warm)clear_assets();allocation[dir]=allocation[dir+1]=255;reject_no_cache(k);allocation[dir]=a;allocation[dir+1]=b;head(k,true);source_cases++;
  size_t end=pos;while(allocation[end]!=15)end+=1+(allocation[end]>>4);const size_t sizes[]={0,1,dir,dir+1,pos,pos+1,end};
  for(unsigned j=0;j<COUNT(sizes);j++){if(!warm)clear_assets();spriteSheet8.size=sizes[j];reject_no_cache(k);spriteSheet8.size=ns;head(k,true);source_cases++;}
  for(unsigned j=0;j<4;j++)if(j!=k){if(!warm)clear_assets();unsigned q=2*(ids[j]-1);allocation[dir]=allocation[q];allocation[dir+1]=allocation[q+1];reject_no_cache(k);allocation[dir]=a;allocation[dir+1]=b;head(k,true);source_cases++;}
  /* Equal decoded pixels/coverage with different valid RLE must be accepted. */
  Uint8 colors[168]={0},mask[168]={0};assert(decode_tile(spriteSheet8,id,colors,mask,12,0,0));assert(!memcmp(colors,references[0][k],168)&&!memcmp(mask,references[0][k]+168,168));
  assert(ns<65536);allocation[dir]=(Uint8)ns;allocation[dir+1]=(Uint8)(ns>>8);spriteSheet8.size=ns+encode_source(allocation+ns,colors,mask);head(k,true);
  /* Coverage-only mutation writes palette index zero into a former hole. */
  unsigned hole=0;while(hole<168&&mask[hole])hole++;assert(hole<168&&!colors[hole]);mask[hole]=255;if(!warm)clear_assets();spriteSheet8.size=ns+encode_source(allocation+ns,colors,mask);
  Uint8 cc[168]={0},mm[168]={0};assert(decode_tile(spriteSheet8,id,cc,mm,12,0,0)&&!memcmp(colors,cc,168)&&memcmp(mm,references[0][k]+168,168));reject_no_cache(k);source_cases++;
  memcpy(allocation,normal,ns);spriteSheet8.size=ns;head(k,true);
  Sprite2_array mismatched=spriteSheet8;mismatched.size--;Asset before[COUNT(assets)];memcpy(before,assets,sizeof(assets));assert(!get_asset(mismatched,id,ENTITY_TILE));unchanged(before);
  Sprite2_array other={.data=normal,.size=ns};assert(!get_asset(other,id,ENTITY_TILE)&&!get_asset(spriteSheet9,id,ENTITY_TILE)&&!get_asset(spriteSheet8,id,ENTITY_QUAD));unchanged(before);
  Sprite2_array save=spriteSheet8;spriteSheet8.data=NULL;reject_no_cache(k);spriteSheet8=save;
  xmas=true;reject_no_cache(k);xmas=false;head(k,true);
  if(christmas){memcpy(allocation,christmas,cs);spriteSheet8.size=cs;reject_no_cache(k);xmas=true;reject_no_cache(k);xmas=false;memcpy(allocation,normal,ns);spriteSheet8.size=ns;head(k,true);source_cases+=2;}
 }
 clear_assets();free(allocation);spriteSheet8=(Sprite2_array){.data=normal,.size=ns};game_probe_density=8;
}
static void shadow_matrix(const char *root){game_probe_assets=root;
 for(int density=4;density<=8;density+=4)for(unsigned k=0;k<4;k++)for(int warm=0;warm<2;warm++)for(unsigned bits=0;bits<8;bits++){
  game_probe_density=density;flags(0);clear_assets();if(warm)head(k,true);flags(bits);Asset before[COUNT(assets)];memcpy(before,assets,sizeof(assets));unsigned opens=file_opens,allocs=allocations,draws=draw_calls;
#ifdef SANITIZED
  __asan_poison_memory_region(assets,sizeof(assets));
#endif
  assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));
#ifdef SANITIZED
  __asan_unpoison_memory_region(assets,sizeof(assets));
#endif
  unchanged(before);assert(file_opens==opens&&allocations==allocs&&draw_calls==draws);shadow_cases++;
 }
 flags(0);clear_assets();game_probe_density=8;
}
/* Native INDEX8 bytes, indexed write order, origin, call counts, and libc RNG. */
static void wrapper_one(unsigned k,int x,int y,int pitch,bool accepted){Uint8 actual[328*200],oracle[328*200];screen.pixels=actual;screen.pitch=pitch;
 for(int style=ENTITY_NORMAL;style<=ENTITY_SHADOW;style++){
  bool shadow=style==ENTITY_SHADOW;for(unsigned i=0;i<sizeof(actual);i++)actual[i]=oracle[i]=(Uint8)(i*29+23);
  unsigned support=0;ptrdiff_t offsets[168];Uint8 values[168];
  for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(references[0][k][168+yy*12+xx]){int p=(y+yy)*pitch+x+xx;if(p>=0&&p<pitch*200){Uint8 v=references[0][k][yy*12+xx];oracle[p]=shadow?(oracle[p]&0xf0)|((oracle[p]&15)/2):style==ENTITY_BLEND?(v&0xf0)|(((v&15)+(oracle[p]&15))/2):v;offsets[support]=p;values[support++]=shadow?0:oracle[p];}}
  Asset before[COUNT(assets)];memcpy(before,assets,sizeof(assets));unsigned draws=draw_calls,originals=original_calls,ends=end_calls,probes=probe_calls;write_count=0;
  srand(163);int expected_rand=rand();srand(163);unsigned oldflags=flags_now();bool oldxmas=xmas;Sprite2_array oldbank=spriteSheet8;
  draw_entity_sprite2(&screen,x,y,spriteSheet8,ids[k],style,ENTITY_TILE);
  assert(rand()==expected_rand&&flags_now()==oldflags&&xmas==oldxmas&&spriteSheet8.data==oldbank.data&&spriteSheet8.size==oldbank.size);
  assert(original_calls==originals+1&&end_calls==ends+1&&probe_calls==probes+1&&draw_calls==draws+(unsigned)(accepted&&!shadow)&&last_mirrored==(accepted&&!shadow));
  assert(!memcmp(actual,oracle,sizeof(actual))&&write_count==support);for(unsigned i=0;i<support;i++)assert(writes[i].offset==offsets[i]&&writes[i].value==values[i]&&writes[i].style==style);if(shadow)unchanged(before);indexed_bytes+=sizeof(actual);wrapper_cases++;
 }
 screen.pixels=NULL;screen.pitch=320;
}
static void indexed_matrix(const char *root){const int xy[][2]={{94,73},{0,0},{308,0},{0,-13},{308,-1},{94,187},{0,199},{308,199},{-3,73},{315,73},{94,-14},{94,200}};game_probe_assets=root;
 for(int density=4;density<=8;density+=4)for(unsigned k=0;k<4;k++)for(int pitch=320;pitch<=328;pitch+=8)for(unsigned p=0;p<COUNT(xy);p++)for(int warm=0;warm<2;warm++)for(unsigned bits=0;bits<8;bits++){
  flags(0);game_probe_density=density;clear_assets();if(warm)head(k,true);flags(bits);wrapper_one(k,xy[p][0],xy[p][1],pitch,!bits);
 }
 flags(0);game_probe_density=8;clear_assets();
}
static void resources(const char *root){char path[2048];snprintf(path,sizeof(path),"%s/variants.tsv",root);FILE*f=fopen(path,"r");assert(f);char name[128];unsigned id;int ok8,d8,ok4,d4;
 while(fscanf(f,"%127s %u %d %d %d %d",name,&id,&ok8,&d8,&ok4,&d4)==6){snprintf(path,sizeof(path),"%s/%s",root,name);game_probe_assets=path;unsigned k=member(id);
  for(int mode=0;mode<2;mode++){game_probe_density=mode?4:8;clear_assets();bool expected=mode?ok4:ok8;int density=mode?d4:d8;
   for(int warm=0;warm<2;warm++){head(k,expected);Asset*a=get_asset(spriteSheet8,id,ENTITY_TILE);assert((a!=NULL)==expected);if(a)assert(a==assets+QUADRANT_SLOT+k&&a->density==density);wrapper_one(k,94,73,320,expected);}resource_cases++;
  }
 }
 assert(feof(f)&&!fclose(f));clear_assets();game_probe_density=8;
}
static uint64_t payload_stamp(const Asset *a){uint64_t h=UINT64_C(0xcbf29ce484222325);size_t n=(size_t)a->w*a->h*a->density*a->density*4;for(size_t i=0;i<n;i++){h^=a->rgba[i];h*=UINT64_C(0x100000001b3);}return h;}
static void bindings_and_coexistence(const char *root){game_probe_assets=root;assert(COUNT(assets)==QUADRANT_SLOT+4);
 for(unsigned id=0;id<602;id++){int expected=-1;for(unsigned k=0;k<4;k++)if(ids[k]==id)expected=(int)k;assert(QUADRANT_MEMBER(id)==expected);}assert(QUADRANT_MEMBER(UINT_MAX)==-1);
 uint64_t stamps[COUNT(previous)];clear_assets();for(unsigned i=0;i<COUNT(previous);i++){Asset*a=get_asset(spriteSheet8,previous[i],ENTITY_TILE);assert(a==assets+previous_slots[i]&&a->valid);stamps[i]=payload_stamp(a);}
 Asset before[COUNT(assets)];memcpy(before,assets,sizeof(assets));
 for(unsigned k=0;k<4;k++){head(k,true);assert(get_asset(spriteSheet8,ids[k],ENTITY_TILE)==assets+QUADRANT_SLOT+k);for(unsigned i=0;i<COUNT(previous);i++)assert(!memcmp(before+previous_slots[i],assets+previous_slots[i],sizeof(Asset))&&payload_stamp(assets+previous_slots[i])==stamps[i]);}
 clear_assets();SDL_Surface alternative=screen;for(unsigned k=0;k<4;k++){assert(!render_mirror_entity(&alternative,0,0,spriteSheet8,ids[k],MIRROR_NORMAL,ENTITY_TILE));active=false;head(k,false);active=true;reject_reason="test";head(k,false);reject_reason=NULL;}
 clear_assets();
}
int main(int argc,char **argv){assert(argc==6);size_t ns,cs=0,rs;Uint8*normal=read_file(argv[1],&ns),*christmas=NULL;if(strcmp(argv[2],"-"))christmas=read_file(argv[2],&cs);spriteSheet8=(Sprite2_array){.data=normal,.size=ns};Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){.data=tokens,.size=1};spriteSheet12=(Sprite2_array){.data=tokens+1,.size=1};explosionSpriteSheet=(Sprite2_array){.data=tokens+2,.size=1};Uint8*refs=read_file(argv[4],&rs);assert(rs==sizeof(references));memcpy(references,refs,rs);free(refs);
 mode_and_gates(argv[3]);source_matrix(normal,ns,christmas,cs,argv[3]);shadow_matrix(argv[3]);indexed_matrix(argv[3]);resources(argv[5]);bindings_and_coexistence(argv[3]);free(normal);free(christmas);
 printf("{\"status\":\"PASS\",\"head_cases\":%u,\"no_cache_rejections\":%u,\"mode_states\":%u,\"source_rejections\":%u,\"early_shadow_cases\":%u,\"resource_cases\":%u,\"wrapper_cases\":%u,\"indexed_bytes_checked\":%zu,\"rng_preserved\":true,\"game_runs\":0}\n",cases,rejects,mode_cases,source_cases,shadow_cases,resource_cases,wrapper_cases,indexed_bytes);return 0;}
