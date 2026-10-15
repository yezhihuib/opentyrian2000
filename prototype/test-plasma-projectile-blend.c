/* Exact-production original Plasma projectile blend units. No engine launch. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
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
#define SPRITE_TABLES_MAX 8
#define SPRITES_PER_TABLE_MAX 152
#define OPTION_SHAPES 5
#define COUNTOF(a) (sizeof(a)/sizeof(*(a)))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "sprite-types.inc"
static Sprite_array sprite_table[SPRITE_TABLES_MAX];
static inline Sprite *sprite(unsigned table,unsigned index)
{ assert(table<COUNTOF(sprite_table)&&index<SPRITES_PER_TABLE_MAX); return &sprite_table[table].sprite[index]; }
static inline bool sprite_exists(unsigned table,unsigned index)
{ return sprite(table,index)->data!=NULL; }
enum { MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW,ASSET_NEWSH2=2 };
typedef struct { SDL_Rect rect; int bank,index,style; bool live; } HdRegion;
static HdRegion regions[8];
static unsigned region_count,local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index,occlusions;
static char all_rejections[512];
static bool active=true,suppress,suppress_cloud,suppress_green_smoke;
static bool game_probe_known_blend=true,game_probe_original_reference,game_probe_local_blend=true;
static int game_probe_density=8;
static const char *reject_reason;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},hd,*game_screen=&screen,*VGAScreen=&screen,*canvas=&hd;
static Uint32 rgb_palette[256],game_palette[256];
static Uint8 expected[64000],selected[64000],restored_mask[64000],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static unsigned checks,admission_calls,decode_calls,raw_calls,pixel_calls,fallback_calls,font_effects,shadow_ends;
static unsigned guard_cases,mutation_cases,draw_cases,clip_cases,composition_cases,palette_cases,pixel_guard_cases;
static size_t indexed_bytes,rgba_bytes;
#define CHECK(test) do { ++checks; if(!(test)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#test); exit(1); } } while(0)

static void render_mirror_shadow_end(void) { ++shadow_ends; }
static void vulcan_shadow_clear(void) {}
static bool vulcan_shadow_pixel(SDL_Surface *s,int x,int y,Uint8 b,Uint8 a,int style)
{ (void)s;(void)x;(void)y;(void)b;(void)a;(void)style;return false; }
static bool font_pixel(int x,int y,Uint8 a,int style)
{ (void)x;(void)y;(void)a;(void)style;return false; }
static void font_before_effect(SDL_Rect r) { CHECK(r.w>0&&r.h>0);++font_effects; }
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
static void game_probe_restore_region(unsigned source,SDL_Rect requested,SDL_Rect result,unsigned groups,unsigned blocks)
{ (void)source;(void)requested;(void)result;(void)groups;(void)blocks; }
static void render_mirror_pixel(SDL_Surface *,Uint8 *,Uint8,int);
static bool hud_sprite_decode(unsigned,unsigned,unsigned,unsigned,Uint8 *,Uint8 *);
#include "functions.inc"

/* These wrappers change names only, preserving every production function body. */
static bool hud_sprite_decode(unsigned t,unsigned i,unsigned w,unsigned h,Uint8 *p,Uint8 *m)
{ ++decode_calls;return production_hud_sprite_decode(t,i,w,h,p,m); }
static bool admitted;
static bool render_mirror_plasma_projectile_begin(SDL_Surface *s,int x,int y,unsigned t,unsigned i)
{ ++admission_calls;admitted=production_render_mirror_plasma_projectile_begin(s,x,y,t,i);return admitted; }
typedef struct { ptrdiff_t offset; Uint8 source,value; } Write;
static Write candidate_writes[4096],baseline_writes[4096];
static unsigned candidate_count,baseline_count;
static void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style)
{ ++fallback_calls;CHECK(style==MIRROR_BLEND);production_render_mirror_pixel(s,p,v,style); }
static void render_mirror_plasma_projectile_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,bool ok)
{
 CHECK(candidate_count<COUNTOF(candidate_writes));
 candidate_writes[candidate_count++]=(Write){p-(Uint8 *)s->pixels,v,*p};++pixel_calls;
 production_render_mirror_plasma_projectile_pixel(s,p,v,ok);
}
#include "candidate-blit.inc"
static void blit_sprite_blend(SDL_Surface *s,int x,int y,unsigned t,unsigned i)
{ ++raw_calls;production_blit_sprite_blend(s,x,y,t,i); }
static void baseline_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style)
{
 CHECK(style==MIRROR_BLEND&&baseline_count<COUNTOF(baseline_writes));
 baseline_writes[baseline_count++]=(Write){p-(Uint8 *)s->pixels,v,*p};
}
#define render_mirror_pixel baseline_pixel
#include "baseline-blit.inc"
#undef render_mirror_pixel

enum { MAX_CELLS=65*28, PAD=32768, STORAGE=328*200+2*PAD };
static Uint8 screen_store[STORAGE],baseline_store[STORAGE],oracle_store[STORAGE];
static SDL_Surface baseline_screen={320,200,320,baseline_store+PAD,&format};
typedef struct { Sprite s; Uint8 indices[MAX_CELLS],mask[MAX_CELLS]; } Original;
static Original originals[2][3];
static const Original *reference_override;
static Uint8 allocation[3][MAX_CELLS*3],*wanted_owner,*wanted_cloud,*wanted_selected;
static Uint16 *wanted_green;
static Uint32 *wanted_rgba;
static size_t hd_pixels;
static unsigned owner_pattern,palette_variant;

static Uint16 read_u16(FILE *f)
{ int a=fgetc(f),b=fgetc(f);CHECK(a>=0&&b>=0);return (Uint16)(a|(b<<8)); }
static void load_original(const char *name,unsigned mode)
{
 FILE *f=fopen(name,"rb");CHECK(f);
 for(unsigned k=0;k<3;k++) {
  Original *o=&originals[mode][k];o->s.width=read_u16(f);o->s.height=read_u16(f);o->s.size=read_u16(f);
  o->s.data=malloc(o->s.size);CHECK(o->s.data);
  CHECK(fread(o->s.data,1,o->s.size,f)==o->s.size);
  size_t cells=(size_t)o->s.width*o->s.height;
  CHECK(cells<=MAX_CELLS&&fread(o->indices,1,cells,f)==cells&&fread(o->mask,1,cells,f)==cells);
 }
 CHECK(fgetc(f)==EOF&&!fclose(f));
}
static void select_original(unsigned mode)
{
 sprite_table[OPTION_SHAPES].count=25;
 for(unsigned k=0;k<3;k++) {
  Original *o=&originals[mode][k];CHECK(o->s.size<=sizeof(allocation[k]));
  memcpy(allocation[k],o->s.data,o->s.size);
  sprite_table[OPTION_SHAPES].sprite[22+k]=o->s;
  sprite_table[OPTION_SHAPES].sprite[22+k].data=allocation[k];
 }
}
static uint64_t hash_bytes(const Uint8 *p,size_t size)
{ uint64_t h=UINT64_C(14695981039346656037);for(size_t i=0;i<size;i++){h^=p[i];h*=UINT64_C(1099511628211);}return h; }
static void set_palette(unsigned variant)
{
 palette_variant=variant;memcpy(rgb_palette,game_palette,sizeof(rgb_palette));
 for(unsigned i=0;i<16;i++) {
  unsigned r,g,b;
  switch(variant) {
  case 0: continue; /* Actual original palette5. */
  case 1: r=g=b=i*17;break;
  case 2: r=18+i*10;g=5+i*i;b=24+i*13;break;
  case 3: r=73;g=i*11;b=4+i*16;break;
  default:r=g=b=i*17;break;
  }
  rgb_palette[0x70+i]=(r<<16)|(g<<8)|b;
 }
 if(variant>=4&&variant<=6) {
  /* Independently break red, green and blue while peak remains monotone. */
  unsigned shift=(variant-4)*8;
  rgb_palette[0x77]=(rgb_palette[0x77]&~(255u<<shift))|(1u<<shift);
 }
}
static Uint32 reference_color(Uint8 index)
{ return UINT32_C(0xff000000)|(rgb_palette[index]&UINT32_C(0xffffff)); }
static Uint32 reference_blend(Uint32 color,Uint8 source)
{
 unsigned channels[3]={color&255,(color>>8)&255,(color>>16)&255},peak=0;
 for(unsigned c=0;c<3;c++)if(channels[c]>peak)peak=channels[c];
 uint64_t v=((uint64_t)peak*3840+127)/255;
 v=(v+256*(source%16))/2;
 unsigned low=(unsigned)(v>>8),high=low<15?low+1:15,weight=(unsigned)(v&255);
 Uint32 out=UINT32_C(0xff000000);
 for(unsigned channel=0;channel<3;channel++) {
  unsigned a=(rgb_palette[(source/16)*16+low]>>(channel*8))&255;
  unsigned b=(rgb_palette[(source/16)*16+high]>>(channel*8))&255;
  out|=(Uint32)(((uint64_t)a*(256-weight)+(uint64_t)b*weight+128)>>8)<<(channel*8);
 }
 return out;
}
static void set_density(int d)
{
 game_probe_density=d;hd.w=320*d;hd.h=200*d;hd.pitch=hd.w*4;hd_pixels=(size_t)hd.w*hd.h;
}
static void reset_scene(unsigned pattern)
{
 owner_pattern=pattern;active=true;suppress=suppress_cloud=suppress_green_smoke=false;
 game_probe_known_blend=game_probe_local_blend=true;game_probe_original_reference=false;
 reject_reason=NULL;all_rejections[0]=0;game_screen=VGAScreen=&screen;canvas=&hd;
 memset(restored_mask,0,sizeof(restored_mask));memset(selected,1,sizeof(selected));memset(wanted_selected,1,64000);
 for(size_t i=0;i<sizeof(screen_store);i++)screen_store[i]=baseline_store[i]=oracle_store[i]=(Uint8)(i*29+17);
 for(int y=0;y<200;y++)memcpy(expected+y*320,(Uint8 *)screen.pixels+y*screen.pitch,320);
 for(size_t i=0;i<hd_pixels;i++) {
  Uint8 owner=pattern<3?(Uint8)pattern:(Uint8)((i+i/(unsigned)hd.w)%3);
  Uint32 color=UINT32_C(0xff000000)|((Uint32)((i*23+11)%256)<<16)|((Uint32)((i*7+41)%256)<<8)|(Uint32)((i*13+71)%256);
  if(owner!=1) {
   size_t logical_y=(i/(unsigned)hd.w)/(unsigned)game_probe_density;
   size_t logical_x=(i%(unsigned)hd.w)/(unsigned)game_probe_density;
   color=reference_color(((Uint8 *)screen.pixels)[logical_y*(unsigned)screen.pitch+logical_x]);
  }
  ((Uint32 *)hd.pixels)[i]=wanted_rgba[i]=color;hd_owner[i]=wanted_owner[i]=owner;
  cloud_owner[i]=wanted_cloud[i]=1;green_first[i]=wanted_green[i]=77;green_under_owner[i]=0;
 }
 region_count=1;regions[0]=(HdRegion){{0,0,320,200},9,233,MIRROR_NORMAL,true};
 local_regions=local_blocks=expanded_regions=boundary_crossings=occlusions=0;
}
static void oracle_pixel(ptrdiff_t off,Uint8 source,Uint8 value,bool compatible)
{
 int y=(int)(off/screen.pitch),x=(int)(off%screen.pitch);if(x>=320||y>=200)return;
 wanted_selected[y*320+x]=0;
 for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++) {
  size_t n=(size_t)(y*game_probe_density+sy)*hd.w+x*game_probe_density+sx;
  wanted_rgba[n]=compatible&&wanted_owner[n]==1?reference_blend(wanted_rgba[n],source):reference_color(value);
  wanted_green[n]=0;wanted_cloud[n]=0;
 }
}
static void oracle_restore(void)
{
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  Uint32 color=reference_color(oracle_store[PAD+y*screen.pitch+x]);
  wanted_selected[y*320+x]=0;
  for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++) {
   size_t n=(size_t)(y*game_probe_density+sy)*hd.w+x*game_probe_density+sx;
   wanted_rgba[n]=color;wanted_owner[n]=0;wanted_green[n]=0;wanted_cloud[n]=0;
  }
 }
}
static void draw(unsigned k,int x,int y,bool compatible)
{
 const Original *o=reference_override?reference_override:&originals[0][k];const Sprite *s=sprite(OPTION_SHAPES,22+k);
 unsigned old_raw=raw_calls,old_begin=admission_calls,old_decode=decode_calls,old_pixels=pixel_calls,old_fallback=fallback_calls;
 unsigned old_regions=local_regions,old_blocks=local_blocks;
 uint64_t source_before=hash_bytes(s->data,s->size);candidate_count=baseline_count=0;
 baseline_screen.pitch=screen.pitch;
 baseline_blit_sprite_blend(&baseline_screen,x,y,OPTION_SHAPES,22+k);
 blit_sprite_blend(&screen,x,y,OPTION_SHAPES,22+k);
 CHECK(raw_calls==old_raw+1&&admission_calls==old_begin+1&&admitted==compatible);
 if(compatible)CHECK(decode_calls==old_decode+1);
 CHECK(hash_bytes(s->data,s->size)==source_before);
 unsigned n=0;bool restored=false;
 for(unsigned yy=0;yy<o->s.height;yy++)for(unsigned xx=0;xx<o->s.width;xx++)if(o->mask[yy*o->s.width+xx]) {
  ptrdiff_t off=(ptrdiff_t)(y+(int)yy)*screen.pitch+x+(int)xx;
  if(off>=(ptrdiff_t)screen.pitch*200)goto done;
  if(off<0)continue;
  Uint8 src=o->indices[yy*o->s.width+xx],before=oracle_store[PAD+off];
  Uint8 value=(Uint8)((src&240)|(((before&15)+(src&15))/2));oracle_store[PAD+off]=value;
  CHECK(n<candidate_count&&n<baseline_count);
  CHECK(candidate_writes[n].offset==off&&baseline_writes[n].offset==off);
  CHECK(candidate_writes[n].source==src&&baseline_writes[n].source==src);
  CHECK(candidate_writes[n].value==value&&baseline_writes[n].value==value);n++;
  if(!compatible&&owner_pattern!=0&&!restored){oracle_restore();restored=true;}
  oracle_pixel(off,src,value,compatible);
 }
 done:
 CHECK(candidate_count==n&&baseline_count==n&&pixel_calls==old_pixels+n);
 CHECK(fallback_calls==old_fallback+(compatible?0:n));
 CHECK(!memcmp(screen_store,oracle_store,sizeof(screen_store))&&!memcmp(screen_store,baseline_store,sizeof(screen_store)));
 CHECK(!memcmp(hd.pixels,wanted_rgba,hd_pixels*4));
 CHECK(!memcmp(hd_owner,wanted_owner,hd_pixels)&&!memcmp(cloud_owner,wanted_cloud,hd_pixels));
 CHECK(!memcmp(green_first,wanted_green,hd_pixels*2)&&!memcmp(selected,wanted_selected,64000));
 for(int row=0;row<200;row++)CHECK(!memcmp(expected+row*320,(Uint8 *)screen.pixels+row*screen.pitch,320));
 CHECK(!reject_reason&&!suppress);if(compatible)CHECK(local_regions==old_regions&&local_blocks==old_blocks);
 indexed_bytes+=sizeof(screen_store)*2+64000;rgba_bytes+=hd_pixels*4;draw_cases++;
}

static bool begin(unsigned k,int x,int y)
{ guard_cases++;return render_mirror_plasma_projectile_begin(&screen,x,y,OPTION_SHAPES,22+k); }
static size_t encode(Uint8 *dst,unsigned w,unsigned h,const Uint8 *pixels,const Uint8 *mask)
{
 size_t at=0;
 for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++) {
  /* Use 253 for every transparent cell. This deliberately differs from originals. */
  dst[at++]=mask[y*w+x]?pixels[y*w+x]:253;
 }
 return at;
}
static void check_identity(void)
{
 set_palette(0);set_density(4);reset_scene(1);
 for(unsigned k=0;k<3;k++)for(unsigned warm=0;warm<2;warm++) {
  select_original(0);if(warm)CHECK(begin(k,100,70));
  Uint8 *address=sprite(OPTION_SHAPES,22+k)->data;
  select_original(1);CHECK(sprite(OPTION_SHAPES,22+k)->data==address&&begin(k,100,70));
  select_original(0);CHECK(begin(k,100,70));Sprite saved=*sprite(OPTION_SHAPES,22+k);Sprite *s=sprite(OPTION_SHAPES,22+k);
  const Original *o=&originals[0][k];unsigned cells=s->width*s->height;
  Uint8 pixels[MAX_CELLS],mask[MAX_CELLS];memcpy(pixels,o->indices,cells);memcpy(mask,o->mask,cells);
  unsigned opaque=0,empty=0;while(!mask[opaque])opaque++;while(mask[empty])empty++;
  /* Current value mutation, no data pointer change. */
  pixels[opaque]^=1;s->size=(Uint16)encode(address,s->width,s->height,pixels,mask);CHECK(!begin(k,100,70));mutation_cases++;
  pixels[opaque]^=1;s->size=(Uint16)encode(address,s->width,s->height,pixels,mask);CHECK(begin(k,100,70));
  /* Semantic equality permits alternate valid bytecode and relocated backing. */
  Uint8 relocated[MAX_CELLS*2];memcpy(relocated,address,s->size);s->data=relocated;CHECK(begin(k,100,70));s->data=address;
  /* An index0 coverage-only change must fail even though decoded indices agree. */
  CHECK(!pixels[empty]);mask[empty]=255;s->size=(Uint16)encode(address,s->width,s->height,pixels,mask);CHECK(!begin(k,100,70));mutation_cases++;
  Uint8 verify[MAX_CELLS],coverage[MAX_CELLS];CHECK(hud_sprite_decode(OPTION_SHAPES,22+k,s->width,s->height,verify,coverage));
  CHECK(!memcmp(verify,o->indices,cells)&&coverage[empty]==255);mask[empty]=0;
  select_original(0);s=sprite(OPTION_SHAPES,22+k);
  for(unsigned which=0;which<8;which++) {
   *s=saved;
   switch(which) {
   case 0:s->width--;break;case 1:s->height--;break;case 2:s->width++;break;case 3:s->height++;break;
   case 4:s->size=0;break;case 5:s->size=(Uint16)(2u*s->width*s->height+s->height+1);break;
   case 6:s->data=NULL;break;default:s->size=1;break;
   }
   CHECK(!begin(k,100,70));mutation_cases++;
  }
  *s=saved;
  /* Truncated 255, overshooting skip, extra row and all-opaque overrun. */
  const Uint8 malformed[][4]={{255,0,0,0},{255,255,0,0},{254,254,254,254}};
  for(unsigned j=0;j<2;j++) {memcpy(address,malformed[j],4);s->size=j==0?1:2;CHECK(!begin(k,100,70));mutation_cases++;}
  memset(address,254,s->height+1);s->size=s->height+1;CHECK(!begin(k,100,70));mutation_cases++;
  memset(address,0,cells+1);s->size=(Uint16)(cells+1);CHECK(!begin(k,100,70));mutation_cases++;
  select_original(0);s=sprite(OPTION_SHAPES,22+k);
  for(unsigned other=0;other<3;other++)if(other!=k) {Sprite current=*s;*s=*sprite(OPTION_SHAPES,22+other);CHECK(!begin(k,100,70));*s=current;mutation_cases++;}
  sprite_table[OPTION_SHAPES].count=22+k;CHECK(!begin(k,100,70));mutation_cases++;
  sprite_table[OPTION_SHAPES].count=SPRITES_PER_TABLE_MAX+1;CHECK(!begin(k,100,70));mutation_cases++;
  select_original(0);CHECK(begin(k,100,70));
  /* Every repeat re-decodes current bytes, including after a valid warm draw. */
  for(unsigned repeat=0;repeat<4;repeat++) {
   unsigned calls=decode_calls;CHECK(begin(k,100,70)&&decode_calls==calls+1);
   s=sprite(OPTION_SHAPES,22+k);Uint8 p=s->data[0];s->data[0]=253;
   CHECK(!begin(k,100,70));s->data[0]=p;CHECK(begin(k,100,70));mutation_cases++;
  }
 }
 select_original(0);
 for(unsigned table=0;table<=SPRITE_TABLES_MAX;table++)if(table!=OPTION_SHAPES) {
  CHECK(!render_mirror_plasma_projectile_begin(&screen,100,70,table,22));guard_cases++;
 }
 for(unsigned index=0;index<=SPRITES_PER_TABLE_MAX+1;index++)if(index<22||index>24) {
  CHECK(!render_mirror_plasma_projectile_begin(&screen,100,70,OPTION_SHAPES,index));guard_cases++;
 }
}

static void check_valid_mutated_draws(void)
{
 /* Mutated but valid art keeps exact baseline writes, invoking generic fallback.
  * Malformed streams below are deliberately restricted to admission checks. */
 set_density(4);set_palette(0);screen.pitch=320;
 for(unsigned mode=0;mode<2;mode++)for(unsigned k=0;k<3;k++)for(unsigned warm=0;warm<2;warm++) {
  select_original(mode);reset_scene(3);if(warm)draw(k,100,70,true);
  Original changed=originals[mode][k];unsigned cells=changed.s.width*changed.s.height,cell=0;
  while(!changed.mask[cell])cell++;
  changed.indices[cell]^=1;
  Sprite *current=sprite(OPTION_SHAPES,22+k);
  current->size=(Uint16)encode(current->data,current->width,current->height,changed.indices,changed.mask);
  reference_override=&changed;unsigned calls=decode_calls;draw(k,100,70,false);CHECK(decode_calls==calls+1);mutation_cases++;
  select_original(mode);reset_scene(2);changed=originals[mode][k];cell=0;while(changed.mask[cell])cell++;
  CHECK(!changed.indices[cell]&&cell<cells);changed.mask[cell]=255;
  current=sprite(OPTION_SHAPES,22+k);current->size=(Uint16)encode(current->data,current->width,current->height,changed.indices,changed.mask);
  reference_override=&changed;calls=decode_calls;draw(k,100,70,false);CHECK(decode_calls==calls+1);mutation_cases++;
  reference_override=NULL;select_original(mode);reset_scene(1);
  current=sprite(OPTION_SHAPES,22+k);current->size=(Uint16)encode(current->data,current->width,current->height,changed.indices,originals[mode][k].mask);
  draw(k,100,70,true);mutation_cases++;
 }
 select_original(0);
}

static void check_context_guards(void)
{
 select_original(0);set_palette(0);set_density(4);reset_scene(1);CHECK(begin(0,100,70));
 Uint8 *saved_owner=hd_owner;SDL_Surface other=screen;CHECK(!production_render_mirror_plasma_projectile_begin(NULL,100,70,OPTION_SHAPES,22));
 CHECK(!production_render_mirror_plasma_projectile_begin(&other,100,70,OPTION_SHAPES,22));guard_cases+=2;
 for(unsigned i=0;i<17;i++) {
  switch(i) {
  case 0:active=false;break;case 1:suppress=true;break;case 2:reject_reason="test";break;
  case 3:game_probe_known_blend=false;break;case 4:game_probe_original_reference=true;break;
  case 5:canvas=NULL;break;case 6:hd_owner=NULL;break;case 7:screen.w=319;break;case 8:screen.h=199;break;
  case 9:screen.pitch=319;break;case 10:screen.pixels=NULL;break;case 11:screen.format=NULL;break;
  case 12:format.BitsPerPixel=32;break;case 13:format.BytesPerPixel=4;break;
  case 14:VGAScreen=&other;break;case 15:game_screen=&other;break;default:game_probe_density=0;break;
  }
  CHECK(!begin(0,100,70));
  active=true;suppress=false;reject_reason=NULL;game_probe_known_blend=true;game_probe_original_reference=false;
  canvas=&hd;hd_owner=saved_owner;
  screen.w=320;screen.h=200;screen.pitch=320;screen.pixels=screen_store+PAD;screen.format=&format;
  format.BitsPerPixel=8;format.BytesPerPixel=1;VGAScreen=game_screen=&screen;game_probe_density=4;
 }
 for(int d=-1;d<=16;d++)if(d!=4&&d!=8) {game_probe_density=d;CHECK(!begin(0,100,70));}
 game_probe_density=4;
}

static void check_palettes(void)
{
 select_original(0);set_density(4);
 for(unsigned variant=0;variant<7;variant++) {
  set_palette(variant);CHECK(effect_ramp_monotone(0x70)==(variant<4));
  CHECK(effect_ramp_monotone_to(0x70,0));
  for(unsigned peak=0;peak<256;peak++)for(unsigned value=0;value<16;value++) {
   Uint32 color=UINT32_C(0xff000000)|(peak<<16)|((peak/3)<<8)|(peak/7);
   CHECK(explosion_blend_rgba(color,(Uint8)(0x70+value))==reference_blend(color,(Uint8)(0x70+value)));palette_cases++;
  }
  for(unsigned k=0;k<3;k++) {reset_scene(variant<4?3:1);draw(k,100,70,variant<4);}
 }
 set_palette(0);
}
static void check_clip_and_ownership(void)
{
 for(unsigned mode=0;mode<2;mode++)for(int d=4;d<=8;d+=4) {
  set_density(d);select_original(mode);set_palette(0);
  for(unsigned owner=0;owner<4;owner++)for(unsigned k=0;k<3;k++) {
   reset_scene(owner);draw(k,100,70,true);draw(k,100,70,true);
  }
  for(unsigned k=0;k<3;k++)for(int pitch=320;pitch<=328;pitch+=8) {
   screen.pitch=pitch;unsigned w=originals[0][k].s.width,h=originals[0][k].s.height;
   const int xy[][2]={{0,0},{320-(int)w,0},{0,200-(int)h},{320-(int)w,200-(int)h},
    {-1,70},{321-(int)w,70},{100,-1},{100,201-(int)h},
    {-((int)w),70},{320,70},{100,-((int)h)},{100,200},{-1,-1},{320,199}};
   for(unsigned j=0;j<COUNTOF(xy);j++) {
    reset_scene(j<4?3:0);draw(k,xy[j][0],xy[j][1],j<4);clip_cases++;
   }
  }
  screen.pitch=320;
 }
}
static void check_compositions(void)
{
 static const unsigned order[6][3]={{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
 for(unsigned mode=0;mode<2;mode++)for(int d=4;d<=8;d+=4)for(unsigned owner=0;owner<4;owner++) {
  select_original(mode);set_density(d);set_palette(0);screen.pitch=320;
  for(unsigned geometry=0;geometry<3;geometry++)for(unsigned permutation=0;permutation<6;permutation++) {
   reset_scene(owner);
   for(unsigned repeat=0;repeat<2;repeat++)for(unsigned piece=0;piece<3;piece++) {
    unsigned k=order[permutation][piece];
    int dx=geometry==0?0:geometry==1?(int)k*11:(int)k*80;
    int dy=geometry==1?(int)k*7:0;
    draw(k,40+dx,70+dy,true);composition_cases++;
   }
  }
 }
}

static void check_independent_piece_admission(void)
{
 /* Each raw piece is admitted at its own exact rectangle, regardless of earlier
  * edge fallback or repeated pieces in the same call sequence. */
 set_density(4);select_original(0);set_palette(0);screen.pitch=320;reset_scene(3);
 draw(0,-1,70,false);draw(1,70,70,true);draw(2,92,77,true);draw(1,70,70,true);
 reset_scene(3);draw(2,92,77,true);draw(1,70,70,true);draw(0,-1,70,false);draw(2,92,77,true);
 /* Local-blend is irrelevant to the audited compatibility path, including HD.
  * Known-blend off and original-reference on use the generic fallback. */
 reset_scene(1);game_probe_local_blend=false;draw(0,100,70,true);
 reset_scene(1);game_probe_known_blend=false;draw(1,100,70,false);
 reset_scene(2);game_probe_original_reference=true;draw(2,100,70,false);
}

static void check_pixel_guards(void)
{
 set_density(4);set_palette(0);screen.pitch=320;
 for(unsigned which=0;which<11;which++) {
  reset_scene(0);Uint8 *p=(Uint8 *)screen.pixels+70*320+100;Uint8 before=*p,source=0x7b;
  *p=(Uint8)(0x70|(((before&15)+11)/2));
  SDL_Surface alt=screen;SDL_Surface *target=&screen;bool compatible=true;
  switch(which) {
  case 0:source=0x6b;break;case 1:*p^=1;break;case 2:compatible=false;break;case 3:active=false;break;
  case 4:suppress=true;break;case 5:reject_reason="test";break;case 6:target=&alt;break;
  case 7:VGAScreen=&alt;break;case 8:p=(Uint8 *)screen.pixels-1;break;
  case 9:p=(Uint8 *)screen.pixels+screen.pitch*200;break;
  default:screen.pitch=328;p=(Uint8 *)screen.pixels+70*328+324;break;
  }
  unsigned old=fallback_calls,old_font=font_effects;
  production_render_mirror_plasma_projectile_pixel(target,p,source,compatible);
  CHECK(fallback_calls==old+(which==10?0:1));CHECK(font_effects==old_font);pixel_guard_cases++;
  if(which<3||which==7) {
   CHECK(expected[70*320+100]==*p);
   size_t at=(size_t)(70*game_probe_density)*hd.w+100*game_probe_density;
   CHECK(((Uint32 *)hd.pixels)[at]==reference_color(*p));
  }
  if(which==3||which==6)CHECK(expected[70*320+100]==before);
  if(which==4) {
   CHECK(expected[70*320+100]==*p&&selected[70*320+100]);
   size_t at=(size_t)(70*game_probe_density)*hd.w+100*game_probe_density;CHECK(hd_owner[at]==1&&cloud_owner[at]==0);
  }
  if(which==5)CHECK(expected[70*320+100]==*p&&!strcmp(reject_reason,"test"));
  if(which==8||which==9)CHECK(reject_reason&&!strcmp(reject_reason,"invalid-write-address"));
  if(which==10)CHECK(!reject_reason&&!memcmp(hd.pixels,wanted_rgba,hd_pixels*4));
  CHECK(!memcmp(screen_store+PAD+64000,baseline_store+PAD+64000,sizeof(screen_store)-PAD-64000));
  screen.pitch=320;
 }
 /* Correct audited writes invoke only the compatibility path for owners0/1/2. */
 for(unsigned owner=0;owner<4;owner++) {
  reset_scene(owner);Uint8 *p=(Uint8 *)screen.pixels+70*320+100;Uint8 source=0x7b,before=*p;
  *p=(Uint8)(0x70|(((before&15)+11)/2));unsigned old=fallback_calls;
  production_render_mirror_plasma_projectile_pixel(&screen,p,source,true);CHECK(fallback_calls==old);pixel_guard_cases++;
  oracle_pixel(70*320+100,source,*p,true);
  CHECK(expected[70*320+100]==*p&&!selected[70*320+100]);
  CHECK(!memcmp(hd.pixels,wanted_rgba,hd_pixels*4)&&!memcmp(hd_owner,wanted_owner,hd_pixels));
  CHECK(!memcmp(green_first,wanted_green,hd_pixels*2)&&!memcmp(cloud_owner,wanted_cloud,hd_pixels));
 }
 active=true;reject_reason=NULL;suppress=false;VGAScreen=&screen;
}

int main(int argc,char **argv)
{
 CHECK(argc==4);screen.pixels=screen_store+PAD;load_original(argv[1],0);load_original(argv[2],1);
 FILE *f=fopen(argv[3],"rb");CHECK(f);for(unsigned i=0;i<256;i++) {
  unsigned r=(unsigned)fgetc(f),g=(unsigned)fgetc(f),b=(unsigned)fgetc(f);CHECK(r<64&&g<64&&b<64);
  game_palette[i]=(((r<<2)|(r>>4))<<16)|(((g<<2)|(g>>4))<<8)|((b<<2)|(b>>4));
 }
 CHECK(!fclose(f));set_density(8);size_t cap=hd_pixels;
 hd.pixels=malloc(cap*4);wanted_rgba=malloc(cap*4);Uint8 *owners=malloc(cap*2);
 hd_owner=owners;wanted_owner=owners+cap;cloud_owner=malloc(cap);wanted_cloud=malloc(cap);
 green_first=malloc(cap*2);wanted_green=malloc(cap*2);green_under_owner=malloc(cap);wanted_selected=malloc(64000);
 CHECK(hd.pixels&&wanted_rgba&&owners&&cloud_owner&&wanted_cloud&&green_first&&wanted_green&&green_under_owner&&wanted_selected);
 check_identity();check_context_guards();hd_owner=owners;check_valid_mutated_draws();
 check_palettes();check_clip_and_ownership();check_compositions();check_independent_piece_admission();check_pixel_guards();
 printf("{\"status\":\"PASS\",\"checks\":%u,\"draws\":%u,\"raw_original_calls\":%u,\"admissions\":%u,\"decodes\":%u,\"pixel_callbacks\":%u,\"fallback_callbacks\":%u,\"identity_mutations\":%u,\"guard_cases\":%u,\"clip_cases\":%u,\"composition_draws\":%u,\"palette_formula_cases\":%u,\"pixel_guard_cases\":%u,\"indexed_bytes_compared\":%zu,\"rgba_bytes_compared\":%zu}\n",
  checks,draw_cases,raw_calls,admission_calls,decode_calls,pixel_calls,fallback_calls,mutation_cases,guard_cases,clip_cases,composition_cases,palette_cases,pixel_guard_cases,indexed_bytes,rgba_bytes);
 for(unsigned mode=0;mode<2;mode++)for(unsigned k=0;k<3;k++)free(originals[mode][k].s.data);
 free(hd.pixels);free(wanted_rgba);free(owners);free(cloud_owner);free(wanted_cloud);free(green_first);free(wanted_green);free(green_under_owner);free(wanted_selected);
 return 0;
}
