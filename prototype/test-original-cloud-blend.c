/* Source-extracted original shapesZ cloud compatibility regression units. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct { int x,y,w,h; } SDL_Rect;
typedef struct { int BitsPerPixel,BytesPerPixel; } SDL_PixelFormat;
typedef struct { int w,h,pitch; void *pixels; SDL_PixelFormat *format; } SDL_Surface;
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define COUNTOF(a) (sizeof(a)/sizeof(*(a)))
enum { MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW,ASSET_NEWSH2=2 };
typedef struct { SDL_Rect rect; int bank,index,style; bool live; } HdRegion;
static HdRegion regions[8];
static unsigned region_count,local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index,occlusions;
static char all_rejections[512];
static bool active=true,suppress,suppress_cloud,suppress_green_smoke,forest_registry_ok;
static bool game_probe_known_blend=true,game_probe_original_reference,game_probe_local_blend=true;
static int game_probe_density=8,game_probe_scene_assets=2;
static char terrain_file='z';
static struct {const Uint8 *data;unsigned id;} terrain_sources[199];
static unsigned terrain_source_count;
static const char *reject_reason;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},hd,*game_screen=&screen,*VGAScreen=&screen,*canvas=&hd;
static Uint32 rgb_palette[256],game_palette[256];
static Uint8 expected[64000],selected[64000],restored_mask[64000],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static unsigned checks,admissions,pixels,fallbacks,terrain_fallbacks,font_effects,raw_calls,baseline_calls;
static unsigned draw_cases,guard_cases,mutation_cases,binding_cases,palette_cases,clip_cases,shadow_cases,composition_cases,pixel_guard_cases;
static unsigned zero_value_callbacks,transparent_cells,local_restore_cases;
static size_t indexed_bytes,rgba_bytes;
#define CHECK(test) do { ++checks;if(!(test)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#test);exit(1);} } while(0)
static void render_mirror_shadow_end(void) {}
static void vulcan_shadow_clear(void) {}
static bool vulcan_shadow_pixel(SDL_Surface *s,int x,int y,Uint8 b,Uint8 a,int style)
{(void)s;(void)x;(void)y;(void)b;(void)a;(void)style;return false;}
static bool font_pixel(int x,int y,Uint8 a,int style)
{(void)x;(void)y;(void)a;(void)style;return false;}
static void font_before_effect(SDL_Rect r) {CHECK(r.w>0&&r.h>0);++font_effects;}
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
static void game_probe_restore_region(unsigned s,SDL_Rect a,SDL_Rect b,unsigned c,unsigned d)
{(void)s;(void)a;(void)b;(void)c;(void)d;}
static void render_mirror_pixel(SDL_Surface *,Uint8 *,Uint8,int);
static void render_mirror_terrain_pixel(SDL_Surface *,Uint8 *,Uint8,int,bool);
#include "functions.inc"
static void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style)
{++fallbacks;production_render_mirror_pixel(s,p,v,style);}
static void render_mirror_terrain_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style,bool replaced)
{++terrain_fallbacks;production_render_mirror_terrain_pixel(s,p,v,style,replaced);}
static unsigned admitted_mask,replacement_mask;
static unsigned render_mirror_cloud_blend_row(SDL_Surface *s,int x,int y,Uint8 **m)
{++admissions;return admitted_mask=production_render_mirror_cloud_blend_row(s,x,y,m);}
typedef struct {ptrdiff_t offset;Uint8 source,value;bool compatible,replaced;} Write;
static Write candidate_writes[8192],baseline_writes[8192];
static unsigned candidate_count,baseline_count;
static void render_mirror_cloud_blend_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,bool ok,bool replaced)
{
 CHECK(candidate_count<COUNTOF(candidate_writes));
 candidate_writes[candidate_count++]=(Write){p-(Uint8 *)s->pixels,v,*p,ok,replaced};++pixels;
 if(v==0x80)++zero_value_callbacks;
 production_render_mirror_cloud_blend_pixel(s,p,v,ok,replaced);
}
static void asset_debug_terrain_row(int x,int y,Uint8 **m) {(void)x;(void)y;(void)m;}
static unsigned render_mirror_terrain_row(SDL_Surface *s,int x,int y,Uint8 **m,int style)
{(void)s;(void)x;(void)y;(void)m;CHECK(style==MIRROR_BLEND);return replacement_mask;}
#include "candidate-blit.inc"
static void blit_background_row_blend(SDL_Surface *s,int x,int y,Uint8 **m)
{++raw_calls;production_blit_background_row_blend(s,x,y,m);}
static void baseline_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style,bool replaced)
{
 CHECK(style==MIRROR_BLEND&&baseline_count<COUNTOF(baseline_writes));
 baseline_writes[baseline_count++]=(Write){p-(Uint8 *)s->pixels,v,*p,false,replaced};
}
#define render_mirror_terrain_pixel baseline_pixel
#include "baseline-blit.inc"
#undef render_mirror_terrain_pixel
static void baseline_blit(SDL_Surface *s,int x,int y,Uint8 **m)
{++baseline_calls;production_baseline_blit_background_row_blend(s,x,y,m);}

enum {PAD=65536,STORAGE=328*200+2*PAD};
static Uint8 screen_store[STORAGE],baseline_store[STORAGE],oracle_store[STORAGE];
static SDL_Surface baseline_screen={320,200,320,baseline_store+PAD,&format};
static const unsigned ids[15]={41,42,43,44,45,51,52,53,54,55,61,62,63,64,65};
static const uint64_t pins[15]={UINT64_C(0x1e1978471660308e),UINT64_C(0xf827022613316057),UINT64_C(0xa8cbc7adae4db91f),
 UINT64_C(0x1c86f35edb926029),UINT64_C(0x27ec422415762368),UINT64_C(0x5bd2c58855182732),
 UINT64_C(0xe2b1309cbd1fcece),UINT64_C(0x3ab26c5cda44cde1),UINT64_C(0xf35212a11fb5188b),
 UINT64_C(0xb4e6e16ac2e7de2d),UINT64_C(0xfae994aab7685046),UINT64_C(0x3b671118097700be),
 UINT64_C(0xff82eada994a23ad),UINT64_C(0xa8af8a7b2806f91a),UINT64_C(0x8567e7d4a59c3882)};
static Uint8 originals[15][672],allocation[15][672],*map[12],*wanted_owner,*wanted_cloud,*wanted_selected;
static Uint16 *wanted_green;
static Uint32 *wanted_rgba;
static size_t hd_pixels;
static unsigned owner_pattern,palette_variant;
static bool covered_seen[15],zero_seen[15],transparent_seen[15];
static bool callback_tile_seen[15],callback_zero_seen[15],draw_transparent_seen[15];
static uint64_t hash_bytes(const Uint8 *p,size_t n)
{uint64_t h=UINT64_C(14695981039346656037);for(size_t i=0;i<n;i++){h^=p[i];h*=UINT64_C(1099511628211);}return h;}
static Uint32 reference_color(Uint8 i) {return UINT32_C(0xff000000)|(rgb_palette[i]&UINT32_C(0xffffff));}
static Uint32 reference_blend(Uint32 color,Uint8 source)
{
 unsigned channels[]={color&255,(color>>8)&255,(color>>16)&255},peak=0;
 for(unsigned k=0;k<3;k++)if(channels[k]>peak)peak=channels[k];
 uint64_t v=(((uint64_t)peak*3840+127)/255+256*(source%16))/2;
 unsigned low=(unsigned)(v>>8),high=low<15?low+1:15,weight=(unsigned)(v&255);
 Uint32 out=UINT32_C(0xff000000);
 for(unsigned c=0;c<3;c++) {
  unsigned a=(rgb_palette[(source/16)*16+low]>>(c*8))&255,b=(rgb_palette[(source/16)*16+high]>>(c*8))&255;
  out|=(Uint32)(((uint64_t)a*(256-weight)+(uint64_t)b*weight+128)>>8)<<(c*8);
 }
 return out;
}
static Uint32 reference_shadow(Uint32 color,Uint8 before,Uint8 after)
{
 Uint32 out=UINT32_C(0xff000000);
 for(unsigned c=0;c<3;c++) {
  unsigned old=(rgb_palette[before]>>(c*8))&255,next=(rgb_palette[after]>>(c*8))&255,current=(color>>(c*8))&255;
  unsigned result=before==after||!old?current:(current*next+old/2)/old;
  out|=MIN(result,255u)<<(c*8);
 }
 return out;
}
static Uint32 reference_darken(Uint32 color)
{
 Uint32 out=UINT32_C(0xff000000);for(unsigned c=0;c<3;c++)out|=((((color>>(c*8))&255)*255+255)/510)<<(c*8);return out;
}
static void select_original(unsigned shift)
{
 terrain_source_count=0;terrain_file='z';forest_registry_ok=true;
 for(unsigned k=0;k<15;k++){memcpy(allocation[k],originals[k],672);render_mirror_bind_terrain(2,ids[k],allocation[k]);}
 CHECK(terrain_source_count==15);
 for(unsigned k=0;k<12;k++)map[k]=allocation[(k+shift)%15];
}
static void set_palette(unsigned variant)
{
 palette_variant=variant;memcpy(rgb_palette,game_palette,sizeof(rgb_palette));
 for(unsigned hue=3;hue<=8;hue++)if(hue==3||hue==6||hue==8)for(unsigned i=0;i<16;i++) {
  unsigned r,g,b;
  switch(variant) {
  case 0:continue;
  case 1:r=g=b=i*17;break;
  case 2:r=18+i*10;g=5+i*i;b=24+i*13;break;
  case 3:r=73;g=i*11;b=4+i*16;break;
  default:r=g=b=i*17;break;
  }
  rgb_palette[hue*16+i]=(r<<16)|(g<<8)|b;
 }
 if(variant>=4&&variant<=6) {
  unsigned shift=(variant-4)*8;
  /* Break every used hue in one channel, leaving other channels monotone. */
  for(unsigned h=3;h<=8;h++)if(h==3||h==6||h==8)rgb_palette[h*16+7]=(rgb_palette[h*16+7]&~(255u<<shift))|(1u<<shift);
 }
}
static void set_density(int d)
{game_probe_density=d;hd.w=320*d;hd.h=200*d;hd.pitch=hd.w*4;hd_pixels=(size_t)hd.w*hd.h;}
static void reset_scene(unsigned owner)
{
 owner_pattern=owner;active=true;suppress=suppress_cloud=suppress_green_smoke=false;
 game_probe_known_blend=game_probe_local_blend=true;game_probe_original_reference=false;game_probe_scene_assets=2;terrain_file='z';
 reject_reason=NULL;all_rejections[0]=0;game_screen=VGAScreen=&screen;canvas=&hd;replacement_mask=0;
 memset(restored_mask,0,sizeof(restored_mask));memset(selected,1,sizeof(selected));memset(wanted_selected,1,64000);
 for(size_t i=0;i<sizeof(screen_store);i++)screen_store[i]=baseline_store[i]=oracle_store[i]=(Uint8)(i*29+17);
 for(int y=0;y<200;y++)memcpy(expected+y*320,(Uint8 *)screen.pixels+y*screen.pitch,320);
 for(size_t i=0;i<hd_pixels;i++) {
  Uint8 own=owner<3?(Uint8)owner:(Uint8)((i+i/(unsigned)hd.w)%3);
  Uint32 color=UINT32_C(0xff000000)|((Uint32)((i*23+11)%256)<<16)|((Uint32)((i*7+41)%256)<<8)|(Uint32)((i*13+71)%256);
  if(own!=1) {
   size_t y=(i/(unsigned)hd.w)/(unsigned)game_probe_density,x=(i%(unsigned)hd.w)/(unsigned)game_probe_density;
   color=reference_color(((Uint8 *)screen.pixels)[y*(unsigned)screen.pitch+x]);
  }
  ((Uint32 *)hd.pixels)[i]=wanted_rgba[i]=color;hd_owner[i]=wanted_owner[i]=own;
  cloud_owner[i]=wanted_cloud[i]=1;green_first[i]=wanted_green[i]=77;green_under_owner[i]=0;
 }
 region_count=1;regions[0]=(HdRegion){{0,0,320,200},9,233,MIRROR_NORMAL,true};
 local_regions=local_blocks=expanded_regions=boundary_crossings=occlusions=0;
}
static void oracle_restore(void)
{
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  Uint32 c=reference_color(oracle_store[PAD+y*screen.pitch+x]);wanted_selected[y*320+x]=0;
  for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++) {
   size_t n=(size_t)(y*game_probe_density+sy)*hd.w+x*game_probe_density+sx;
   wanted_rgba[n]=c;wanted_owner[n]=0;wanted_cloud[n]=0;wanted_green[n]=0;
  }
 }
}
static void oracle_pixel(ptrdiff_t off,Uint8 source,Uint8 value,bool compatible,bool replaced)
{
 int y=(int)(off/screen.pitch),x=(int)(off%screen.pitch);if(x>=320||y>=200)return;
 if(!replaced)wanted_selected[y*320+x]=0;
 for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++) {
  size_t n=(size_t)(y*game_probe_density+sy)*hd.w+x*game_probe_density+sx;
  if(replaced){wanted_owner[n]=game_probe_original_reference?2:1;wanted_selected[y*320+x]=1;continue;}
  wanted_rgba[n]=compatible&&wanted_owner[n]==1?reference_blend(wanted_rgba[n],source):reference_color(value);
  wanted_green[n]=0;wanted_cloud[n]=compatible&&wanted_owner[n]==1?1:0;
 }
}
static void compare_scene(void)
{
 CHECK(!memcmp(screen_store,oracle_store,sizeof(screen_store))&&!memcmp(screen_store,baseline_store,sizeof(screen_store)));
 CHECK(!memcmp(hd.pixels,wanted_rgba,hd_pixels*4));
 CHECK(!memcmp(hd_owner,wanted_owner,hd_pixels)&&!memcmp(cloud_owner,wanted_cloud,hd_pixels));
 CHECK(!memcmp(green_first,wanted_green,hd_pixels*2)&&!memcmp(selected,wanted_selected,64000));
 for(int y=0;y<200;y++)CHECK(!memcmp(expected+y*320,(Uint8 *)screen.pixels+y*screen.pitch,320));
 CHECK(!reject_reason&&!suppress&&!suppress_cloud);
 indexed_bytes+=sizeof(screen_store)*2+64000;rgba_bytes+=hd_pixels*4;
}
static void draw(int x,int y,unsigned mask)
{
 unsigned oldraw=raw_calls,oldbase=baseline_calls,oldbegin=admissions,oldpixel=pixels,oldfallback=terrain_fallbacks,oldregions=local_regions;
 uint64_t sourcehash[12];for(unsigned t=0;t<12;t++)sourcehash[t]=map[t]?hash_bytes(map[t],672):0;
 candidate_count=baseline_count=0;baseline_screen.pitch=screen.pitch;
 baseline_blit(&baseline_screen,x,y,map);blit_background_row_blend(&screen,x,y,map);
 CHECK(raw_calls==oldraw+1&&baseline_calls==oldbase+1&&admissions==oldbegin+1&&admitted_mask==mask);
 unsigned n=0,fallback_count=0;bool restored=false;
 for(int yy=0;yy<28;yy++)for(unsigned tile=0;tile<12;tile++)for(int xx=0;xx<24;xx++) {
  ptrdiff_t off=(ptrdiff_t)(y+yy)*screen.pitch+x+(int)tile*24+xx;
  if(map[tile]==NULL)continue;
  if(off>=(ptrdiff_t)screen.pitch*200)goto done;
  Uint8 source=map[tile][yy*24+xx];
  if(!source){++transparent_cells;for(unsigned k=0;k<15;k++)if(map[tile]==allocation[k])draw_transparent_seen[k]=true;continue;}if(off<0)continue;
  for(unsigned k=0;k<15;k++)if(map[tile]==allocation[k]){callback_tile_seen[k]=true;if(source==0x80)callback_zero_seen[k]=true;}
  Uint8 value=(Uint8)((source&240)|(((oracle_store[PAD+off]&15)+(source&15))/2));oracle_store[PAD+off]=value;
  bool ok=(mask&(1u<<tile))!=0,replaced=(replacement_mask&(1u<<tile))!=0;
  CHECK(n<candidate_count&&n<baseline_count);
  CHECK(candidate_writes[n].offset==off&&baseline_writes[n].offset==off);
  CHECK(candidate_writes[n].source==source&&baseline_writes[n].source==source);
  CHECK(candidate_writes[n].value==value&&baseline_writes[n].value==value);
  CHECK(candidate_writes[n].compatible==ok&&candidate_writes[n].replaced==replaced&&baseline_writes[n].replaced==replaced);n++;
  if(!ok||replaced)fallback_count++;
  if(!ok&&!replaced&&off%screen.pitch<320&&!restored) {
   bool any=false;int ly=(int)(off/screen.pitch),lx=(int)(off%screen.pitch);
   for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++)
    if(wanted_owner[(ly*game_probe_density+sy)*hd.w+lx*game_probe_density+sx])any=true;
   if(any){oracle_restore();restored=true;}
  }
  oracle_pixel(off,source,value,ok,replaced);
 }
 done:
 CHECK(candidate_count==n&&baseline_count==n&&pixels==oldpixel+n&&terrain_fallbacks==oldfallback+fallback_count);
 for(unsigned t=0;t<12;t++)CHECK(sourcehash[t]==(map[t]?hash_bytes(map[t],672):0));
 if(restored){CHECK(local_regions==oldregions+1);++local_restore_cases;}else CHECK(local_regions==oldregions);
 compare_scene();draw_cases++;
}
static unsigned begin(int x,int y)
{++guard_cases;return render_mirror_cloud_blend_row(&screen,x,y,map);}
static void check_binding(void)
{
 set_density(4);set_palette(0);reset_scene(1);
 for(unsigned k=0;k<15;k++) {
  CHECK(hash_bytes(originals[k],672)==pins[k]);CHECK(cloud_terrain_slot(ids[k])==(int)(186+k));
  for(unsigned cell=0;cell<672;cell++) {
   Uint8 v=originals[k][cell];if(v)covered_seen[k]=true;else transparent_seen[k]=true;if(v==0x80)zero_seen[k]=true;
   CHECK(!v||(v&240)==0x30||(v&240)==0x60||(v&240)==0x80);
  }
 }
 for(unsigned id=0;id<=700;id++) {
  bool cloud=false;for(unsigned k=0;k<15;k++)if(ids[k]==id)cloud=true;
  if(!cloud)CHECK(cloud_terrain_slot(id)<0);
  if(cloud)CHECK(ground_terrain_slot(id)<0&&plateau_terrain_slot(id)<0&&underlay_terrain_slot(id)<0&&road_terrain_slot(id)<0&&
   terrain_holes_slot(id)<0&&stone_foundation_slot(id)<0&&layer3_gray_slot(id)<0&&layer3_purple_slot(id)<0&&grass_sand_slot(id)<0&&
   forest_terrain_slot(id)<0&&layer3_circuit_slot(id)<0&&layer3_mechanical_slot(id)<0&&layer3_linked31_slot(id)<0);
  for(unsigned layer=0;layer<=4;layer++) {
   terrain_source_count=0;render_mirror_bind_terrain(layer,id,allocation[0]);
   if(cloud)CHECK(terrain_source_count==(layer==2?1u:0u));
   if(terrain_source_count)CHECK(terrain_sources[0].id==id&&terrain_sources[0].data==allocation[0]);
   binding_cases++;
  }
 }
 for(unsigned layer=0;layer<4;layer++) {
  terrain_file='x';terrain_source_count=0;render_mirror_bind_terrain(layer,41,allocation[0]);CHECK(!terrain_source_count);
 }
 terrain_file='z';terrain_source_count=199;render_mirror_bind_terrain(2,41,allocation[0]);CHECK(terrain_source_count==199);
 select_original(0);CHECK(begin(0,0)==4095u);
}
static void check_mutations(void)
{
 set_density(4);set_palette(0);screen.pitch=320;
 for(unsigned k=0;k<15;k++) {
  select_original(k);reset_scene(3);CHECK(begin(0,70)==4095u);
  Uint8 *same=allocation[k];unsigned opaque=0,empty=0;while(!same[opaque])opaque++;while(empty<672&&same[empty])empty++;
  same[opaque]^=1;CHECK(map[0]==same&&begin(0,70)==4094u);draw(0,70,4094u);mutation_cases++;
  same[opaque]^=1;reset_scene(1);CHECK(begin(0,70)==4095u);draw(0,70,4095u);
  if(empty<672) {
   same[empty]=0x80;CHECK(begin(0,70)==4094u);reset_scene(2);draw(0,70,4094u);mutation_cases++;
   same[empty]=0;CHECK(begin(0,70)==4095u);
  }
  /* Every byte is hashed on every call, including bytes clipped out of view. */
  for(unsigned hidden=0;hidden<2;hidden++) {
   unsigned cell=hidden?671:0;Uint8 old=same[cell];same[cell]^=1;
   CHECK(begin(0,hidden?199:-27)==4094u);reset_scene(3);draw(0,hidden?199:-27,4094u);same[cell]=old;mutation_cases++;
  }
  /* An equal, newly registered allocation is accepted; unregistered is not. */
  Uint8 relocated[672];memcpy(relocated,same,672);map[0]=relocated;CHECK(begin(0,70)==4094u);
  render_mirror_bind_terrain(2,ids[k],relocated);CHECK(begin(0,70)==4095u);mutation_cases+=2;
  /* Same pointer, different ID, or correct ID, wrong source bytes, is rejected. */
  select_original(k);terrain_sources[k].id=ids[(k+1)%15];CHECK(begin(0,70)==4094u);mutation_cases++;
  select_original(k);map[0]=allocation[(k+1)%15];CHECK(begin(0,70)==4095u); /* Independent valid tile. */
  terrain_sources[(k+1)%15].id=ids[k];CHECK((begin(0,70)&1u)==0);mutation_cases++;
 }
 select_original(0);reset_scene(3);map[3]=NULL;CHECK(begin(0,70)==(4095u&~8u));draw(0,70,4095u&~8u);
 /* Mutating one tile invalidates all uses of that tile, leaving others valid. */
 select_original(0);map[7]=map[2];allocation[2][17]^=1;CHECK(begin(0,70)==(4095u&~((1u<<2)|(1u<<7))));
 reset_scene(3);draw(0,70,4095u&~((1u<<2)|(1u<<7)));select_original(0);
}
static void check_context_guards(void)
{
 select_original(0);set_palette(0);set_density(4);reset_scene(1);CHECK(begin(0,70)==4095u);
 SDL_Surface other=screen;Uint8 *owner=hd_owner,*cloud=cloud_owner;
 CHECK(!production_render_mirror_cloud_blend_row(NULL,0,70,map));CHECK(!production_render_mirror_cloud_blend_row(&other,0,70,map));
 for(unsigned i=0;i<23;i++) {
  switch(i) {
  case 0:active=false;break;case 1:suppress=true;break;case 2:reject_reason="test";break;
  case 3:game_probe_known_blend=false;break;case 4:game_probe_original_reference=true;break;
  case 5:canvas=NULL;break;case 6:hd_owner=NULL;break;case 7:cloud_owner=NULL;break;
  case 8:screen.w=319;break;case 9:screen.h=199;break;case 10:screen.pitch=319;break;
  case 11:screen.pixels=NULL;break;case 12:screen.format=NULL;break;case 13:format.BitsPerPixel=32;break;
  case 14:format.BytesPerPixel=4;break;case 15:VGAScreen=&other;break;case 16:game_screen=&other;break;
  case 17:game_probe_density=0;break;case 18:game_probe_scene_assets=1;break;case 19:terrain_file='x';break;
  case 20:terrain_source_count=0;break;case 21:terrain_file='Z';break;default:game_probe_scene_assets=0;break;
  }
  CHECK(!begin(0,70));active=true;suppress=false;reject_reason=NULL;game_probe_known_blend=true;game_probe_original_reference=false;
  canvas=&hd;hd_owner=owner;cloud_owner=cloud;screen=(SDL_Surface){320,200,320,screen_store+PAD,&format};
  format=(SDL_PixelFormat){8,1};VGAScreen=game_screen=&screen;game_probe_density=4;game_probe_scene_assets=2;terrain_file='z';select_original(0);
 }
 CHECK(!production_render_mirror_cloud_blend_row(&screen,0,70,NULL));
 for(int d=-1;d<=16;d++)if(d!=4&&d!=8){game_probe_density=d;CHECK(!begin(0,70));}game_probe_density=4;
 const int xy[][2]={{-1,70},{33,70},{0,-28},{0,200},{INT_MIN,70},{INT_MAX,70},{0,INT_MIN},{0,INT_MAX}};
 for(unsigned i=0;i<COUNTOF(xy);i++)CHECK(!begin(xy[i][0],xy[i][1]));
 CHECK(begin(0,-27)==4095u&&begin(32,199)==4095u);
 game_probe_local_blend=false;CHECK(begin(0,70)==4095u);game_probe_local_blend=true;
}
static void check_palettes(void)
{
 set_density(4);screen.pitch=328;select_original(0);
 for(unsigned variant=0;variant<7;variant++) {
  set_palette(variant);
  for(unsigned hue=3;hue<=8;hue++)if(hue==3||hue==6||hue==8) {
   CHECK(effect_ramp_monotone(hue*16)==(variant<4));
   for(unsigned peak=0;peak<256;peak++)for(unsigned value=0;value<16;value++) {
    Uint32 c=UINT32_C(0xff000000)|(peak<<16)|((peak/3)<<8)|(peak/7);
    CHECK(explosion_blend_rgba(c,(Uint8)(hue*16+value))==reference_blend(c,(Uint8)(hue*16+value)));palette_cases++;
   }
  }
  for(unsigned shift=0;shift<2;shift++) {select_original(shift*3);reset_scene(3);draw(16,70,variant<4?4095u:0u);}
 }
 /* Hue-specific rejection: tiles without that hue stay independent. */
 for(unsigned hue=3;hue<=8;hue++)if(hue==3||hue==6||hue==8) {
  set_palette(1);rgb_palette[hue*16+7]=0;select_original(0);unsigned mask=4095u;
  for(unsigned k=0;k<12;k++)for(unsigned c=0;c<672;c++)if(originals[k][c]&&(originals[k][c]&240)==hue*16){mask&=~(1u<<k);break;}
  reset_scene(3);draw(16,70,mask);
 }
 set_palette(0);screen.pitch=320;
}
static void check_draw_matrix(void)
{
 for(int d=4;d<=8;d+=4)for(int pitch=320;pitch<=328;pitch+=8)for(unsigned owner=0;owner<4;owner++) {
  set_density(d);screen.pitch=pitch;set_palette(0);
  for(unsigned shift=0;shift<2;shift++) {
   select_original(shift*3);reset_scene(owner);draw(shift?32:0,70,4095u);draw(shift?32:0,70,4095u);composition_cases+=2;
   for(unsigned edge=0;edge<2;edge++) {
    reset_scene(owner);
    for(int visible=1;visible<28;visible++){draw(visible%2?0:32,edge?200-visible:visible-28,4095u);clip_cases++;}
   }
  }
 }
 /* Every original tile and every visible height against synthetic ramp classes. */
 set_density(4);screen.pitch=328;
 for(unsigned variant=1;variant<7;variant++)for(unsigned shift=0;shift<2;shift++)for(unsigned edge=0;edge<2;edge++) {
  select_original(shift*3);set_palette(variant);reset_scene(3);
  for(int visible=1;visible<28;visible++) {
   if(variant>=4)reset_scene(3);draw(16,edge?200-visible:visible-28,variant<4?4095u:0u);clip_cases++;
  }
 }
 /* Horizontal legacy wrapping, full offscreen, and non-target contexts keep
  * exactly the baseline indexed buffer and callback order. */
 set_palette(0);
 const int xy[][2]={{-1,70},{33,70},{-1,-1},{33,199},{0,-28},{0,-29},{0,-90},{0,200},{0,201},{0,280}};
 for(int d=4;d<=8;d+=4)for(int pitch=320;pitch<=328;pitch+=8)for(unsigned shift=0;shift<2;shift++) {
  set_density(d);screen.pitch=pitch;select_original(shift*3);
  for(unsigned j=0;j<COUNTOF(xy);j++){reset_scene(3);draw(xy[j][0],xy[j][1],0);clip_cases++;}
 }
 screen.pitch=320;set_density(4);select_original(0);reset_scene(1);game_probe_known_blend=false;draw(0,70,0);
 reset_scene(2);game_probe_original_reference=true;draw(0,70,0);
 reset_scene(1);game_probe_local_blend=false;draw(0,70,4095u);
 /* Replace a subset through the unchanged suppression callback. */
 for(unsigned owner=0;owner<4;owner++)for(unsigned shift=0;shift<2;shift++){select_original(shift*3);reset_scene(owner);replacement_mask=0x555u;draw(0,70,4095u);composition_cases++;}
 screen.pitch=320;
}
static void logical_write(int x,int y,int style)
{
 ptrdiff_t off=(ptrdiff_t)y*screen.pitch+x;Uint8 before=oracle_store[PAD+off];
 Uint8 after=style==MIRROR_SHADOW?(Uint8)((before&240)|((before&15)/2)):(Uint8)(0x60|((before+3)&15));
 oracle_store[PAD+off]=baseline_store[PAD+off]=screen_store[PAD+off]=after;wanted_selected[y*320+x]=0;
 for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++) {
  size_t n=(size_t)(y*game_probe_density+sy)*hd.w+x*game_probe_density+sx;
  if(style==MIRROR_SHADOW&&wanted_owner[n]==1) {
   wanted_rgba[n]=wanted_cloud[n]?reference_shadow(wanted_rgba[n],before,after):reference_darken(wanted_rgba[n]);
  }else {wanted_rgba[n]=reference_color(after);if(style==MIRROR_NORMAL)wanted_owner[n]=0;}
  if(style!=MIRROR_SHADOW||wanted_owner[n]!=1)wanted_cloud[n]=0;wanted_green[n]=0;
 }
 render_mirror_pixel(&screen,screen_store+PAD+off,after,style);shadow_cases++;
}
static void check_shadows(void)
{
 for(int d=4;d<=8;d+=4)for(unsigned owner=0;owner<4;owner++)for(unsigned variant=0;variant<4;variant++)for(unsigned shift=0;shift<2;shift++) {
  set_density(d);set_palette(variant);screen.pitch=variant%2?328:320;select_original(shift*3);reset_scene(owner);draw(16,70,4095u);
  /* Shadow every covered original pixel, then repeat enough to reach floor. */
  for(unsigned repeat=0;repeat<6;repeat++)for(unsigned tile=0;tile<12;tile++)for(unsigned c=0;c<672;c++)if(map[tile][c])
   logical_write(16+(int)tile*24+(int)(c%24),70+(int)(c/24),MIRROR_SHADOW);
  compare_scene();
  /* Indexed normal writes erase cloud provenance; later cloud/overlap restores
   * it only for genuinely HD owner1 subpixels. */
  for(unsigned tile=0;tile<12;tile++){logical_write(16+(int)tile*24,80,MIRROR_NORMAL);logical_write(16+(int)tile*24,80,MIRROR_SHADOW);}
  compare_scene();draw(20,75,4095u);draw(0,199,4095u);draw(32,-10,4095u);composition_cases+=3;
 }
 set_palette(0);screen.pitch=320;
 /* A synthetic palette floor with zero channels checks the guarded ratio. */
 set_density(4);select_original(0);reset_scene(1);rgb_palette[0x80]=0;rgb_palette[0x81]=0x000005;
 Uint8 before=0x81,after=0x80;Uint32 color=0xffc86432u;
 CHECK(cloud_shadow_rgba(color,before,after)==reference_shadow(color,before,after));
 CHECK(cloud_shadow_rgba(color,after,after)==color);set_palette(0);
}
static void check_pixel_guards(void)
{
 set_density(4);screen.pitch=320;set_palette(0);select_original(0);
 for(unsigned which=0;which<13;which++) {
  reset_scene(0);Uint8 *p=(Uint8 *)screen.pixels+70*320+100,source=0x8b,before=*p;
  *p=(Uint8)(0x80|(((before&15)+11)/2));SDL_Surface other=screen,*target=&screen;bool compatible=true,replaced=false;
  switch(which) {
  case 0:source=0x7b;break;case 1:*p^=1;break;case 2:compatible=false;break;case 3:active=false;break;
  case 4:suppress=true;break;case 5:reject_reason="test";break;case 6:target=&other;break;
  case 7:VGAScreen=&other;break;case 8:p=(Uint8 *)screen.pixels-1;break;
  case 9:p=(Uint8 *)screen.pixels+screen.pitch*200;break;
  case 10:screen.pitch=328;p=(Uint8 *)screen.pixels+70*328+324;break;
  case 11:source=0;break;default:replaced=true;break;
  }
  unsigned old=terrain_fallbacks,oldfont=font_effects;production_render_mirror_cloud_blend_pixel(target,p,source,compatible,replaced);
  CHECK(terrain_fallbacks==old+(which==10?0u:1u));CHECK(font_effects==oldfont);pixel_guard_cases++;
  if(which==8||which==9)CHECK(reject_reason&&!strcmp(reject_reason,"invalid-write-address"));
  if(which==10)CHECK(!reject_reason&&!memcmp(hd.pixels,wanted_rgba,hd_pixels*4));
  if(which==3||which==6)CHECK(expected[70*320+100]==before);
  screen.pitch=320;
 }
 /* Covered source0x80 must transform HD value even though its low nibble is0. */
 for(unsigned owner=0;owner<4;owner++)for(unsigned source=0x30;source<=0x80;source+=source==0x30?0x30:0x20) {
  reset_scene(owner);Uint8 *p=(Uint8 *)screen.pixels+70*320+100,before=*p;
  *p=(Uint8)((source&240)|((before&15)/2));unsigned old=terrain_fallbacks;
  production_render_mirror_cloud_blend_pixel(&screen,p,(Uint8)source,true,false);CHECK(terrain_fallbacks==old);
  oracle_store[PAD+70*320+100]=baseline_store[PAD+70*320+100]=*p;oracle_pixel(70*320+100,(Uint8)source,*p,true,false);compare_scene();pixel_guard_cases++;
 }
 active=true;reject_reason=NULL;suppress=false;VGAScreen=&screen;
}
int main(int argc,char **argv)
{
 CHECK(argc==3);screen.pixels=screen_store+PAD;FILE *f=fopen(argv[1],"rb");CHECK(f);
 CHECK(fread(originals,1,sizeof(originals),f)==sizeof(originals)&&fgetc(f)==EOF&&!fclose(f));
 f=fopen(argv[2],"rb");CHECK(f);
 for(unsigned i=0;i<256;i++){unsigned r=(unsigned)fgetc(f),g=(unsigned)fgetc(f),b=(unsigned)fgetc(f);CHECK(r<64&&g<64&&b<64);
  game_palette[i]=(((r<<2)|(r>>4))<<16)|(((g<<2)|(g>>4))<<8)|((b<<2)|(b>>4));}
 CHECK(!fclose(f));set_density(8);size_t cap=hd_pixels;
 hd.pixels=malloc(cap*4);wanted_rgba=malloc(cap*4);Uint8 *owners=malloc(cap*2);hd_owner=owners;wanted_owner=owners+cap;
 cloud_owner=malloc(cap);wanted_cloud=malloc(cap);green_first=malloc(cap*2);wanted_green=malloc(cap*2);green_under_owner=malloc(cap);wanted_selected=malloc(64000);
 CHECK(hd.pixels&&wanted_rgba&&owners&&cloud_owner&&wanted_cloud&&green_first&&wanted_green&&green_under_owner&&wanted_selected);
 check_binding();check_mutations();check_context_guards();hd_owner=owners;check_palettes();check_draw_matrix();check_shadows();check_pixel_guards();
 CHECK(raw_calls==baseline_calls&&raw_calls==draw_cases&&zero_value_callbacks>0&&transparent_cells>0&&local_restore_cases>0);
 for(unsigned k=0;k<15;k++){CHECK(covered_seen[k]&&callback_tile_seen[k]);if(zero_seen[k])CHECK(callback_zero_seen[k]);if(transparent_seen[k])CHECK(draw_transparent_seen[k]);}
 printf("{\"status\":\"PASS\",\"checks\":%u,\"draws\":%u,\"baseline_raw_calls\":%u,\"admissions\":%u,\"pixel_callbacks\":%u,\"fallback_callbacks\":%u,\"binding_cases\":%u,\"mutations\":%u,\"guard_cases\":%u,\"palette_formula_cases\":%u,\"clip_draws\":%u,\"shadow_pixel_writes\":%u,\"composition_draws\":%u,\"pixel_guard_cases\":%u,\"covered_ramp_zero_callbacks\":%u,\"transparent_cells\":%u,\"local_restores\":%u,\"indexed_bytes_compared\":%zu,\"rgba_bytes_compared\":%zu}\n",
 checks,draw_cases,baseline_calls,admissions,pixels,terrain_fallbacks,binding_cases,mutation_cases,guard_cases,palette_cases,clip_cases,shadow_cases,composition_cases,pixel_guard_cases,zero_value_callbacks,transparent_cells,local_restore_cases,indexed_bytes,rgba_bytes);
 free(hd.pixels);free(wanted_rgba);free(owners);free(cloud_owner);free(wanted_cloud);free(green_first);free(wanted_green);free(green_under_owner);free(wanted_selected);return 0;
}
