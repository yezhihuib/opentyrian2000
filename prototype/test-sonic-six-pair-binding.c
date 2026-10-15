/* Focused exact production-source units. Never launches the engine. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void*pixels;SDL_PixelFormat*format;} SDL_Surface;
#include "sprite-type.inc"
typedef int EntityDrawStyle;typedef int EntityDrawLayout;
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW,ENTITY_TILE=0,ENTITY_QUAD=1};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#define MIN(a,b) ((a)<(b)?(a):(b))
#define COUNT(a) (sizeof(a)/sizeof(*(a)))
#include "types.inc"
static bool xmas,active=true,game_probe_missing,game_probe_invalid,game_probe_original_reference;
static int game_probe_density=8;static const char*game_probe_assets,*reject_reason;
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value;
static SDL_PixelFormat format={8,1};static SDL_Surface screen={320,200,320,NULL,&format},*game_screen=&screen,*VGAScreen=&screen;
static unsigned banking_draw_player;static uint64_t mirror_logic_tick;static TalonBank talon_banks[2];
static struct{const Uint8*rgba;char path[1024];}vulcan_shadow_resource[13],vulcan_shadow_coverage_resource[3];
static unsigned draw_calls,pixel_calls,original_calls,end_calls,shadow_begins,shadow_ends,probe_calls;
static unsigned cases,identity_cases,variants,binding_cases,cache_cases,shadow_cases;static size_t index_checks;
static int last_style,last_x,last_y;static bool last_mirrored;
static const unsigned ids[2]={6,44};
static Uint8 references[4][336];
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
static void render_mirror_shadow_begin(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(s==&screen&&b.data==spriteSheet8.data&&(i==6||i==44));(void)x;(void)y;shadow_begins++;}
static struct {ptrdiff_t offset;Uint8 value;int style;} writes[200];static unsigned write_count;
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style){assert(s==&screen&&p>=(Uint8*)s->pixels&&p<(Uint8*)s->pixels+s->pitch*s->h);assert(style==MIRROR_NORMAL||style==MIRROR_SHADOW);assert(write_count<COUNT(writes));writes[write_count].offset=p-(Uint8*)s->pixels;writes[write_count].value=v;writes[write_count++].style=style;pixel_calls++;}
#include "blitters.inc"
static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){original_calls++;production_blit_sprite2(s,x,y,b,i);}
static void blit_sprite2_darken(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){original_calls++;production_blit_sprite2_darken(s,x,y,b,i);}
#define blit_sprite2_blend(...) assert(!"unexpected blend")
#define blit_sprite2x2(...) assert(!"unexpected quad")
#define blit_sprite2x2_blend(...) assert(!"unexpected quad blend")
#define blit_sprite2x2_darken(...) assert(!"unexpected quad shadow")
static void render_mirror_entity_end(void){end_calls++;}
static void game_probe_draw(int role,unsigned i,int x,int y,int style,int layout,bool mirrored){assert(role==8&&(i==6||i==44)&&layout==ENTITY_TILE);(void)x;(void)y;(void)style;probe_calls++;last_mirrored=mirrored;}
#include "wrappers.inc"
static Uint8*read_file(const char*p,size_t*n){FILE*f=fopen(p,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long z=ftell(f);assert(z>0&&!fseek(f,0,SEEK_SET));Uint8*r=malloc((size_t)z);assert(r&&fread(r,1,(size_t)z,f)==(size_t)z&&!fclose(f));*n=(size_t)z;return r;}
static void clear_assets(void){for(size_t i=0;i<COUNT(assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}}
static void head(unsigned k,bool accepted){unsigned before=draw_calls;bool got=render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_NORMAL,ENTITY_TILE);if(got!=accepted)fprintf(stderr,"head k=%u expected=%d got=%d xmas=%d size=%zu density=%d missing=%d invalid=%d calls=%u root=%s\n",k,accepted,got,xmas,spriteSheet8.size,game_probe_density,game_probe_missing,game_probe_invalid,cases,game_probe_assets?game_probe_assets:"NULL");assert(got==accepted&&draw_calls==before+(unsigned)accepted);if(accepted){assert(last_style==MIRROR_NORMAL&&last_x==94&&last_y==73);Asset*a=&assets[546+k];assert(a->valid&&a->bank==8&&a->index==(int)ids[k]&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&a->density==8);}cases++;}
static void unchanged(const Asset*before){assert(!memcmp(before,assets,sizeof(assets)));}
static void identity(Uint8*normal,size_t ns,Uint8*christmas,size_t cs,const char*full){
 game_probe_assets=full;size_t cap=ns>cs?ns:cs;Uint8*allocation=malloc(cap);assert(allocation);
 for(unsigned k=0;k<2;k++)for(int warm=0;warm<2;warm++){
  clear_assets();memcpy(allocation,normal,ns);spriteSheet8=(Sprite2_array){.data=allocation,.size=ns};xmas=false;
  if(warm)head(k,!BASELINE);Asset before[548];memcpy(before,assets,sizeof(assets));
  xmas=true;head(k,false);unchanged(before);xmas=false;
  memcpy(allocation,christmas,cs);spriteSheet8.size=cs;head(k,!BASELINE);memcpy(before,assets,sizeof(assets));xmas=true;head(k,false);unchanged(before);xmas=false;
  memcpy(allocation,normal,ns);spriteSheet8.size=ns;head(k,!BASELINE);
  size_t p=(size_t)allocation[2*(ids[k]-1)]|((size_t)allocation[2*(ids[k]-1)+1]<<8);while(!(allocation[p]>>4))p++;
  if(!warm)clear_assets();Uint8 saved=allocation[p+1];allocation[p+1]^=1;memcpy(before,assets,sizeof(assets));head(k,false);unchanged(before);head(1-k,!BASELINE);allocation[p+1]=saved;head(k,!BASELINE);
  if(!warm)clear_assets();saved=allocation[p];allocation[p]=(saved&0xf0)|((saved+1)&15);head(k,false);allocation[p]=saved;head(k,!BASELINE);
  if(!warm)clear_assets();saved=allocation[2*(ids[k]-1)];Uint8 saved2=allocation[2*(ids[k]-1)+1];allocation[2*(ids[k]-1)]=255;allocation[2*(ids[k]-1)+1]=255;head(k,false);allocation[2*(ids[k]-1)]=saved;allocation[2*(ids[k]-1)+1]=saved2;head(k,!BASELINE);
  spriteSheet8.size=2*(ids[k]-1);head(k,false);spriteSheet8.size=ns;head(k,!BASELINE);
  spriteSheet8.size=0;head(k,false);spriteSheet8.size=ns;head(k,!BASELINE);
  Sprite2_array mismatched=spriteSheet8;mismatched.size--;memcpy(before,assets,sizeof(assets));assert(!get_asset(mismatched,ids[k],ENTITY_TILE));unchanged(before);
  Sprite2_array saved_bank=spriteSheet8;spriteSheet8.data=NULL;head(k,false);spriteSheet8=saved_bank;
  Sprite2_array other={.data=normal,.size=ns};assert(!get_asset(other,ids[k],ENTITY_TILE));assert(!get_asset(spriteSheet8,ids[k],ENTITY_QUAD));assert(!get_asset(spriteSheet9,ids[k],ENTITY_TILE));
  SDL_Surface alternate=screen;unsigned draws=draw_calls;assert(!render_mirror_entity(&alternate,94,73,spriteSheet8,ids[k],MIRROR_NORMAL,ENTITY_TILE)&&draw_calls==draws);
  active=false;head(k,false);active=true;reject_reason="test";head(k,false);reject_reason=NULL;
  identity_cases+=25;
 }
 clear_assets();free(allocation);spriteSheet8=(Sprite2_array){.data=normal,.size=ns};
}
static void gates(const char*full){
 for(unsigned k=0;k<2;k++)for(int warm=0;warm<2;warm++)for(int gate=0;gate<9;gate++){
  clear_assets();game_probe_assets=full;if(warm)head(k,!BASELINE);Asset snapshot[548];memcpy(snapshot,assets,sizeof(assets));
  switch(gate){case 0:game_probe_density=1;break;case 1:game_probe_density=2;break;case 2:game_probe_density=16;break;case 3:game_probe_missing=true;break;case 4:game_probe_invalid=true;break;case 5:game_probe_original_reference=true;break;case 6:game_probe_assets=NULL;break;case 7:xmas=true;break;case 8:active=false;break;}
  head(k,false);unchanged(snapshot);game_probe_density=8;game_probe_missing=game_probe_invalid=game_probe_original_reference=xmas=false;game_probe_assets=full;active=true;identity_cases++;
 }
 clear_assets();
}
static int expected_slot(int b,unsigned id,int layout){
 if(b==0&&layout==ENTITY_TILE){
  if(!xmas){if(!BASELINE&&(id==6||id==44))return id==6?546:547;if(id==27)return 535;if(id==67)return 522;if(id==70)return 523;const unsigned multi[]={121,122,163,164,201,202,279,280};for(unsigned i=0;i<COUNT(multi);i++)if(id==multi[i])return 524+(int)i;if(id==225)return 469;if(id==244)return 470;if(id==226)return 471;}
  if(id>=31&&id<=33)return 333+(int)id-31;if(id>=252&&id<=254)return 330+(int)id-252;if(id==59)return 5;if(id==103)return 325;
  const unsigned pulse[]={58,60,62,165},guided[]={19,171,20,21};for(int i=0;i<4;i++){if(id==pulse[i])return 321+i;if(id==guided[i])return 326+i;}if(id>=214&&id<=217)return 182+(int)id-214;
 }
 if(b==1&&layout==ENTITY_QUAD&&id>=229&&id<=237&&id%2==1)return ((int)id-229)/2;
 if(b==3&&layout==ENTITY_TILE){const int r[][3]={{122,133,31},{3,14,43},{41,52,55},{22,33,67},{60,71,79},{146,152,91},{192,203,98},{154,165,110},{211,222,122},{173,184,134},{135,141,146},{78,84,175}};for(unsigned i=0;i<COUNT(r);i++)if(id>=(unsigned)r[i][0]&&id<=(unsigned)r[i][1])return r[i][2]+(int)id-r[i][0];const unsigned shield[]={229,230,231,232,233,234,235,236,237,248,249,250,252,253,254,255,256,267,268,269,272,275};for(unsigned i=0;i<COUNT(shield);i++)if(id==shield[i])return 153+(int)i;}
 return -1;
}
static void finite_bindings(void){
 assert(COUNT(assets)==(BASELINE?546:548));Uint8 token;Sprite2_array banks[]={spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet,{.data=&token,.size=1},{.data=NULL,.size=0}};const int layouts[]={ENTITY_TILE,ENTITY_QUAD,-1,2};
 for(int christmas=0;christmas<2;christmas++)for(int b=0;b<6;b++)for(int l=0;l<4;l++)for(unsigned n=0;n<602;n++){
  clear_assets();xmas=christmas;game_probe_invalid=false;game_probe_assets="/nonexistent-sonic-six-pair-unit-resources";unsigned id=n==601?UINT_MAX:n;int layout=layouts[l],slot=expected_slot(b,id,layout);assert(!get_asset(banks[b],id,layout));unsigned initialized=0;
  for(unsigned s=0;s<COUNT(assets);s++)if(assets[s].initialized){Asset*a=assets+s;initialized++;assert((int)s==slot&&!a->valid&&a->index==(int)id);assert(a->bank==(b==0?8:b==1?9:ASSET_EXPLOSION));assert(a->w==(layout==ENTITY_QUAD?24:12)&&a->h==(layout==ENTITY_QUAD?28:14));assert(a->anchor_x==(b==1?5:b==0&&id==59?-1:0)&&a->anchor_y==(b==1?7:0));}
  assert(initialized==(unsigned)(slot>=0));binding_cases++;
 }
 clear_assets();xmas=game_probe_invalid=false;
}
static void resource_wrapper(unsigned k,bool accepted){
 Uint8 actual[320*200],oracle[320*200];screen.pixels=actual;screen.pitch=320;
 for(int shadow=0;shadow<2;shadow++){
  for(unsigned i=0;i<sizeof(actual);i++)actual[i]=oracle[i]=(Uint8)(i*29+23);
  for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(references[k][168+yy*12+xx]){int p=(73+yy)*320+94+xx;oracle[p]=shadow?(oracle[p]&0xf0)|((oracle[p]&15)/2):references[k][yy*12+xx];}
  unsigned draws=draw_calls,originals=original_calls,ends=end_calls;write_count=0;
  draw_entity_sprite2(&screen,94,73,spriteSheet8,ids[k],shadow?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);
  assert(original_calls==originals+1&&end_calls==ends+1&&draw_calls==draws+(unsigned)(accepted&&!shadow)&&last_mirrored==(accepted&&!shadow)&&write_count==74&&!memcmp(actual,oracle,sizeof(actual)));index_checks+=sizeof(actual);cases++;
 }
 screen.pixels=NULL;
}
static void resource(const char*root){char line[2048];snprintf(line,sizeof(line),"%s/variants.tsv",root);FILE*f=fopen(line,"r");assert(f);char name[128];int valid[2],density[2];
 while(fscanf(f,"%127s %d %d %d %d",name,&valid[0],&valid[1],&density[0],&density[1])==5){
  char path[2048];snprintf(path,sizeof(path),"%s/%s",root,name);clear_assets();game_probe_assets=path;
  for(unsigned k=0;k<2;k++){resource_wrapper(k,!BASELINE&&valid[k]);resource_wrapper(k,!BASELINE&&valid[k]);Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert((a!=NULL)==(!BASELINE&&valid[k]));if(a){assert(a==assets+546+k&&a->density==density[k]&&a->bank==8&&a->index==(int)ids[k]&&!a->anchor_x&&!a->anchor_y&&a->rgba&&a->w==12&&a->h==14);}assert(get_asset(spriteSheet8,ids[k],ENTITY_TILE)==a);cache_cases++;}variants++;
 }
 assert(feof(f));fclose(f);clear_assets();
}
static void density_four(const char*root){
 const char*names[]={"only4","valid","invalid8-valid4"};
 game_probe_density=4;
 for(unsigned v=0;v<COUNT(names);v++){
  char path[2048];snprintf(path,sizeof(path),"%s/%s",root,names[v]);game_probe_assets=path;clear_assets();
  for(unsigned k=0;k<2;k++){bool accepted=!BASELINE&&v!=1;resource_wrapper(k,accepted);resource_wrapper(k,accepted);Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert((a!=NULL)==accepted);if(a)assert(a->density==4);}
 }
 game_probe_density=8;clear_assets();
}
static void indexed(const char*full,Uint8*normal,size_t ns,int reference_bank){
 clear_assets();game_probe_assets=full;spriteSheet8=(Sprite2_array){.data=normal,.size=ns};game_probe_density=8;
 Uint8 actual[328*200],oracle[328*200];screen.pixels=actual;
 const int xy[][2]={{94,73},{0,0},{308,0},{0,-13},{308,-1},{94,187},{0,199},{308,199},{-3,73},{315,73},{94,-14},{94,200}};
 for(unsigned k=0;k<2;k++){
  Uint8 colors[168]={0},mask[168]={0};assert(decode_tile(spriteSheet8,ids[k],colors,mask,12,0,0));unsigned support=0;for(int i=0;i<168;i++)support+=mask[i]!=0;assert(support==74&&!memcmp(colors,references[reference_bank*2+k],168)&&!memcmp(mask,references[reference_bank*2+k]+168,168));
  for(int pitch=320;pitch<=328;pitch+=8){screen.pitch=pitch;for(unsigned j=0;j<COUNT(xy);j++)for(int warm=0;warm<2;warm++)for(int shadow=0;shadow<2;shadow++)for(int missing=0;missing<2;missing++){
   clear_assets();game_probe_missing=false;if(warm)head(k,!BASELINE&&!xmas);game_probe_missing=missing;
   for(int i=0;i<328*200;i++)actual[i]=oracle[i]=(Uint8)(i*29+23);int x=xy[j][0],y=xy[j][1];
   unsigned before=draw_calls,originals=original_calls,ends=end_calls,probes=probe_calls;Asset snapshot[548];memcpy(snapshot,assets,sizeof(assets));
   unsigned expected_writes=0;ptrdiff_t offsets[168];Uint8 values[168];for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(mask[yy*12+xx]){int p=(y+yy)*pitch+x+xx;if(p>=0&&p<pitch*200){oracle[p]=shadow?(oracle[p]&0xf0)|((oracle[p]&15)/2):colors[yy*12+xx];offsets[expected_writes]=p;values[expected_writes++]=shadow?0:colors[yy*12+xx];}}
   write_count=0;draw_entity_sprite2(&screen,x,y,spriteSheet8,ids[k],shadow?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);
   bool accepted=!BASELINE&&!xmas&&!shadow&&!missing;assert(last_mirrored==accepted&&draw_calls==before+(unsigned)accepted&&original_calls==originals+1&&end_calls==ends+1&&probe_calls==probes+1);assert(!memcmp(actual,oracle,sizeof(actual)));assert(write_count==expected_writes);
   for(unsigned i=0;i<expected_writes;i++)assert(writes[i].offset==offsets[i]&&writes[i].value==values[i]&&writes[i].style==(shadow?MIRROR_SHADOW:MIRROR_NORMAL));
   if(shadow){unchanged(snapshot);shadow_cases++;}index_checks+=sizeof(actual);cases++;
  }}
 }
 screen.pitch=320;screen.pixels=NULL;game_probe_missing=false;clear_assets();
}
int main(int argc,char**argv){assert(argc==5);size_t ns,cs;Uint8*normal=read_file(argv[1],&ns),*christmas=read_file(argv[2],&cs);spriteSheet8=(Sprite2_array){.data=normal,.size=ns};Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){.data=tokens,.size=1};spriteSheet12=(Sprite2_array){.data=tokens+1,.size=1};explosionSpriteSheet=(Sprite2_array){.data=tokens+2,.size=1};char full[2048];snprintf(full,sizeof(full),"%s/valid",argv[3]);
 size_t refs_size;Uint8*refs=read_file(argv[4],&refs_size);assert(refs_size==sizeof(references));memcpy(references,refs,sizeof(references));free(refs);
 finite_bindings();identity(normal,ns,christmas,cs,full);resource(argv[3]);density_four(argv[3]);game_probe_assets=full;gates(full);
 for(unsigned k=0;k<2;k++){game_probe_density=1;head(k,false);game_probe_density=8;game_probe_missing=true;head(k,false);game_probe_missing=false;clear_assets();game_probe_invalid=true;head(k,false);game_probe_invalid=false;clear_assets();head(k,!BASELINE);}
 indexed(full,normal,ns,0);xmas=true;indexed(full,christmas,cs,1);xmas=false;free(normal);free(christmas);
 printf("{\"status\":\"PASS\",\"baseline\":%s,\"head_and_wrapper_cases\":%u,\"identity_cases\":%u,\"finite_binding_cases\":%u,\"resource_variants\":%u,\"cache_cases\":%u,\"shadow_cases\":%u,\"indexed_bytes_checked\":%zu,\"original_calls\":%u,\"game_runs\":0}\n",BASELINE?"true":"false",cases,identity_cases,binding_cases,variants,cache_cases,shadow_cases,index_checks,original_calls);return 0;}
