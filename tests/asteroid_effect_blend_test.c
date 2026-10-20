/* SPDX-License-Identifier: GPL-2.0-or-later
 * Offline production-extraction regression fixture. No game-loop emulation.
 * Original sheet bytes are read in memory only and never emitted.
 */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {Uint32 format;Uint8 BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;SDL_Rect clip_rect;} SDL_Surface;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
#define SDL_PIXELFORMAT_INDEX8 UINT32_C(0x13000801)
#define SDL_PIXELFORMAT_ARGB8888 UINT32_C(0x16362004)
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
#define SDL_SwapLE16(x) (x)
#else
#define SDL_SwapLE16(x) __builtin_bswap16(x)
#endif
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define CHECK(x) do { ++checks;if(!(x)) {fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);} } while(0)
static unsigned long checks;static unsigned cases,positive_cases,negative_cases,full_blits;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW,ASSET_NEWSH2=101};
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[16];static unsigned region_count;
static SDL_Surface *canvas,*game_screen,*VGAScreen;
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;static Uint32 rgb_palette[256];
static Uint8 expected[64000],selected[64000],restored_mask[64000];
static bool active,suppress,suppress_cloud,suppress_green_smoke,game_probe_original_reference;
static bool game_probe_known_blend,game_probe_local_blend,asteroid_hd_enabled,xmas,level_scope,game_probe_enabled,asteroid_hd_lease,actor_scope;
static unsigned fixture_policy;
static int game_probe_density;static const char *reject_reason;
static unsigned local_blocks,local_regions,expanded_regions,boundary_crossings,occlusions,blend_source_index;
static Sprite2_array explosionSpriteSheet,spriteSheet9;
static bool twoPlayerMode,galagaMode,twoPlayerLinked;
static uint64_t mirror_logic_tick;
#define ENTITY_QUAD 1
static unsigned fallback_calls,font_calls,shadow_ends,restore_calls,restore_index,font_reject;
static SDL_Rect restored_request,restored_rect;
static struct {unsigned calls,index,subpixels,blocks;int ox,oy,x,y;Uint8 before,source,after;bool known,rgba;} metric;
static bool asteroid1_level_scope(void){return level_scope;}
static bool asteroid1_scope(void){return actor_scope;}
static void render_mirror_unsupported(const char *reason){if(active&&!reject_reason)reject_reason=reason;}
static void render_mirror_shadow_end(void){++shadow_ends;}
static void font_before_effect(SDL_Rect r){(void)r;++font_calls;if(font_reject)render_mirror_unsupported("font-fixture-rejection");}
static void game_probe_restore_region(unsigned index,SDL_Rect request,SDL_Rect rect,unsigned groups,unsigned blocks)
{(void)groups;(void)blocks;++restore_calls;restore_index=index;restored_request=request;restored_rect=rect;}
static void game_probe_blend_write(bool known,unsigned index,int ox,int oy,int x,int y,Uint8 before,Uint8 source,Uint8 after,unsigned subpixels,unsigned blocks,bool rgba)
{++metric.calls;metric.known=known;metric.index=index;metric.ox=ox;metric.oy=oy;metric.x=x;metric.y=y;metric.before=before;metric.source=source;metric.after=after;metric.subpixels=subpixels;metric.blocks=blocks;metric.rgba=rgba;}
static Uint32 palette_rgb(Uint8 index);
#define data_frame_pixel(...) ((void)0)
#define data_portrait_pixel(...) ((void)0)
#define storm_pixel(...) ((void)0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
#define vulcan_shadow_clear(...) ((void)0)
#define vulcan_shadow_pixel(...) false
#define font_pixel(...) false
#include "actual_primitives.inc"
#define render_mirror_pixel actual_render_mirror_pixel
#include "actual_pixel.inc"
#undef render_mirror_pixel
static void render_mirror_pixel(SDL_Surface *s,Uint8 *address,Uint8 source,int style)
{++fallback_calls;actual_render_mirror_pixel(s,address,source,style);}
#include "actual_talon.inc"
#include "actual_asteroid.inc"
#include "actual_callback.inc"
#define asset_debug_effect(...) ((void)0)
#include "actual_blitter.inc"

/* Independent RLE walker supplies support coordinates and exact byte locations.
 * It does not call decode_tile or reuse production pin/hash code. */
static bool reference_decode(Sprite2_array b,unsigned index,Uint8 color[168],Uint8 coverage[168],size_t raw[168])
{
 memset(color,0,168);memset(coverage,0,168);if(raw)memset(raw,0,168*sizeof(*raw));
 if(!index||index*2u>b.size)return false;
 size_t pos=(size_t)b.data[(index-1)*2]+256u*b.data[(index-1)*2+1];int cursor=0;
 for(size_t step=0;step<b.size;step++) {
  if(pos>=b.size)return false;unsigned code=b.data[pos++];if(code==15)return true;
  cursor+=(int)(code%16);unsigned fill=code/16;
  if(!fill)continue;
  while(fill--) {if(cursor<0||cursor>=168||pos>=b.size)return false;color[cursor]=b.data[pos];coverage[cursor]=255;if(raw)raw[cursor]=pos;++cursor;++pos;}
 }
 return false;
}
static bool shield_supported(unsigned i)
{return (i>=229&&i<=237)||(i>=248&&i<=250)||(i>=252&&i<=256)||(i>=267&&i<=269)||i==272||i==275;}
static bool supported(unsigned i)
{return shield_supported(i)|| (i>=3&&i<=14)||(i>=22&&i<=33)||(i>=41&&i<=52)||(i>=60&&i<=71)||(i>=122&&i<=133)||i==145||(i>=146&&i<=152)||(i>=154&&i<=165)||(i>=173&&i<=184)||(i>=192&&i<=203)||(i>=211&&i<=222);}
static unsigned first_cell(const Uint8 c[168],const Uint8 m[168],int hue)
{for(unsigned i=0;i<168;i++)if(m[i]&&(hue<0||(c[i]&240)==hue))return i;CHECK(false);return 0;}
static Uint8 indexed_after(Uint8 before,Uint8 source)
{return (Uint8)((source&240)|(((unsigned)(before%16)+(unsigned)(source%16))/2));}
static Uint32 reference_blend(Uint32 prior,Uint8 source)
{
 unsigned component[3]={(prior>>16)&255,(prior>>8)&255,prior&255};unsigned peak=component[0];for(unsigned c=1;c<3;c++)if(component[c]>peak)peak=component[c];
 unsigned fixed=(unsigned)(((uint64_t)peak*3840+127)/255);fixed=(fixed+256u*(source%16))/2;
 unsigned low=fixed/256,high=low<15?low+1:15,fraction=fixed-256*low;Uint32 out=UINT32_C(0xff000000);
 for(unsigned c=0;c<3;c++){unsigned shift=16-8*c;unsigned a=(rgb_palette[(source&240)+low]>>shift)&255,b=(rgb_palette[(source&240)+high]>>shift)&255;out|=((a*(256-fraction)+b*fraction+128)/256)<<shift;}
 return out;
}
static size_t canvas_n(void){return (size_t)canvas->w*canvas->h;}
static Uint32 *rgba_at(int x,int y){return (Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x;}
static Uint8 *index_at(int x,int y){return (Uint8 *)game_screen->pixels+y*game_screen->pitch+x;}
static void set_palette(void)
{for(unsigned h=0;h<16;h++)for(unsigned v=0;v<16;v++)rgb_palette[h*16+v]=(v*(5+h%7)<<16)|(v*(4+h*3%12)<<8)|(v*(3+h*5%13));}
static void reset(int d)
{
 ++cases;asteroid1_talon_blend_reset();twoPlayerMode=galagaMode=twoPlayerLinked=false;game_probe_density=d;canvas->w=320*d;canvas->h=200*d;canvas->pitch=canvas->w*4;
 active=asteroid_hd_enabled=game_probe_known_blend=game_probe_local_blend=level_scope=true;
 suppress=suppress_cloud=suppress_green_smoke=game_probe_original_reference=xmas=false;game_probe_enabled=fixture_policy==0;asteroid_hd_lease=fixture_policy==1;actor_scope=fixture_policy==1;
 reject_reason=NULL;local_blocks=local_regions=expanded_regions=boundary_crossings=occlusions=blend_source_index=0;
 fallback_calls=font_calls=shadow_ends=restore_calls=font_reject=0;memset(&metric,0,sizeof(metric));region_count=0;
 memset(expected,0x3d,sizeof(expected));memset(game_screen->pixels,0x3d,64000);memset(selected,0,sizeof(selected));memset(restored_mask,0,sizeof(restored_mask));set_palette();
}
static unsigned prepare_block(int x,int y,int owners,Uint32 out[64],Uint8 own[64])
{
 unsigned hd=0;int d=game_probe_density;selected[y*320+x]=1;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  unsigned k=(unsigned)(sy*d+sx);size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
  Uint8 o=(Uint8)(owners<0?k%3:(unsigned)owners);Uint32 p=UINT32_C(0xff000000)|((k*3497u+0x2965a7u)&0xffffffu);
  *rgba_at(x*d+sx,y*d+sy)=out[k]=p;hd_owner[n]=own[k]=o;cloud_owner[n]=1;green_first[n]=99;green_under_owner[n]=2;if(o==1)++hd;
 }
 return hd;
}
static void positive(unsigned index,int d,int requested_hue,int ox,int oy,unsigned cell)
{
 reset(d);++positive_cases;Uint8 c[168],m[168];CHECK(reference_decode(explosionSpriteSheet,index,c,m,NULL));
 if(cell==UINT_MAX)cell=first_cell(c,m,requested_hue);CHECK(m[cell]);int x=ox+(int)cell%12,y=oy+(int)cell/12;CHECK(x>=0&&x<320&&y>=0&&y<200);
 Uint32 prior[64];Uint8 own[64];unsigned hd=prepare_block(x,y,-1,prior,own);Uint8 source=c[cell],after=indexed_after(0x3d,source);*index_at(x,y)=after;
 render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),source,explosionSpriteSheet,index,ox,oy);
 CHECK(!reject_reason);CHECK(!fallback_calls);CHECK(metric.calls==1&&metric.rgba&&metric.known);CHECK(metric.index==index&&metric.ox==ox&&metric.oy==oy&&metric.x==x&&metric.y==y);CHECK(metric.before==0x3d&&metric.after==after&&metric.source==source&&metric.subpixels==hd&&metric.blocks==0);CHECK(expected[y*320+x]==after&&*index_at(x,y)==after);CHECK(!selected[y*320+x]&&occlusions==1&&font_calls==1);
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {unsigned k=(unsigned)(sy*d+sx);size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;CHECK(*rgba_at(x*d+sx,y*d+sy)==(own[k]==1?reference_blend(prior[k],source):palette_rgb(after)));CHECK(hd_owner[n]==own[k]&&!cloud_owner[n]&&!green_first[n]&&green_under_owner[n]==2);}
}
static void source_tests(void)
{
 reset(8);Uint8 c[168],m[168],actual[336];size_t raw[168];unsigned accepted=0;
 for(unsigned i=1;i<=275;i++) {CHECK(reference_decode(explosionSpriteSheet,i,c,m,NULL));memset(actual,0,sizeof(actual));CHECK(decode_tile(explosionSpriteSheet,i,actual,actual+168,12,0,0));CHECK(!memcmp(c,actual,168)&&!memcmp(m,actual+168,168));
  for(unsigned cell=0;cell<168;cell++)if(m[cell]) {bool ok=asteroid1_effect_blend_source(explosionSpriteSheet,i,c[cell],100,80,100+(int)cell%12,80+(int)cell/12);CHECK(ok==(supported(i)&&((shield_supported(i)&&(c[cell]&240)==0x80)||(!shield_supported(i)&&((c[cell]&240)==0x70||(c[cell]&240)==0x40)))));if(ok)++accepted;}
 }
 CHECK(accepted>5000);CHECK(sizeof(asteroid1_effect_blend_pins)/sizeof(*asteroid1_effect_blend_pins)==116);CHECK(sizeof(asteroid1_shield_blend_pins)/sizeof(*asteroid1_shield_blend_pins)==22);
 CHECK(reference_decode(explosionSpriteSheet,122,c,m,raw));unsigned cell=first_cell(c,m,-1);int x=100+(int)cell%12,y=80+(int)cell/12;Uint8 v=c[cell];
 #define SOURCE(b,i,s,ox,oy,px,py) asteroid1_effect_blend_source(b,i,s,ox,oy,px,py)
 CHECK(SOURCE(explosionSpriteSheet,122,v,100,80,x,y));CHECK(!SOURCE(explosionSpriteSheet,0,v,100,80,x,y));CHECK(!SOURCE(explosionSpriteSheet,UINT_MAX,v,100,80,x,y));CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,INT_MIN,INT_MAX));CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,INT_MAX,INT_MIN));
 Sprite2_array foreign={explosionSpriteSheet.size,malloc(explosionSpriteSheet.size)};CHECK(foreign.data);memcpy(foreign.data,explosionSpriteSheet.data,foreign.size);
 CHECK(!SOURCE(foreign,122,v,100,80,x,y));Sprite2_array missing=explosionSpriteSheet;missing.data=NULL;CHECK(!SOURCE(missing,122,v,100,80,x,y));
 Sprite2_array wrong=explosionSpriteSheet;wrong.size--;CHECK(!SOURCE(wrong,122,v,100,80,x,y));wrong.size+=2;CHECK(!SOURCE(wrong,122,v,100,80,x,y));
 size_t original_size=explosionSpriteSheet.size;explosionSpriteSheet.size--;CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,y));CHECK(!SOURCE(wrong,122,v,100,80,x,y));explosionSpriteSheet.size+=2;CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,y));explosionSpriteSheet.size=original_size;
 CHECK(!SOURCE(explosionSpriteSheet,122,(Uint8)(v^1),100,80,x,y));CHECK(!SOURCE(explosionSpriteSheet,122,0x80,100,80,x,y));
 for(unsigned empty=0;empty<168;empty++)if(!m[empty]) {CHECK(!SOURCE(explosionSpriteSheet,122,0x70,100,80,100+(int)empty%12,80+(int)empty/12));break;}
 CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,99,y));CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,112,y));CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,79));CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,94));
 int badx[]={-1,309,INT_MIN,INT_MAX};for(unsigned i=0;i<4;i++)CHECK(!SOURCE(explosionSpriteSheet,122,v,badx[i],80,x,y));
 int bady[]={-14,200,INT_MIN,INT_MAX};for(unsigned i=0;i<4;i++)CHECK(!SOURCE(explosionSpriteSheet,122,v,100,bady[i],x,y));
 xmas=true;CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,y));xmas=false;
 Uint8 saved=explosionSpriteSheet.data[raw[cell]];explosionSpriteSheet.data[raw[cell]]^=1;CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,y));CHECK(!SOURCE(explosionSpriteSheet,122,(Uint8)(v^1),100,80,x,y));explosionSpriteSheet.data[raw[cell]]=saved;CHECK(SOURCE(explosionSpriteSheet,122,v,100,80,x,y));
 size_t start=(size_t)explosionSpriteSheet.data[242]+256u*explosionSpriteSheet.data[243];saved=explosionSpriteSheet.data[start];explosionSpriteSheet.data[start]=15;CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,y));explosionSpriteSheet.data[start]=saved;
 Uint8 table[2]={explosionSpriteSheet.data[242],explosionSpriteSheet.data[243]};explosionSpriteSheet.data[242]=explosionSpriteSheet.data[244];explosionSpriteSheet.data[243]=explosionSpriteSheet.data[245];CHECK(!SOURCE(explosionSpriteSheet,122,v,100,80,x,y));memcpy(explosionSpriteSheet.data+242,table,2);
 Uint8 *original=explosionSpriteSheet.data;explosionSpriteSheet.data=foreign.data;Sprite2_array old={original_size,original};CHECK(!SOURCE(old,122,v,100,80,x,y));CHECK(SOURCE(explosionSpriteSheet,122,v,100,80,x,y));explosionSpriteSheet.data=original;free(foreign.data);
 #undef SOURCE
}
/* Independently mutate each original shield frame in place, including an
 * off-callback painted cell and its coverage stream. No cached source trust. */
static void shield_source_mutations(void)
{
 reset(8);Uint8 c[168],m[168];size_t raw[168];unsigned frames=0;
 for(unsigned index=229;index<=275;index++)if(shield_supported(index)) {
  ++frames;CHECK(reference_decode(explosionSpriteSheet,index,c,m,raw));unsigned cell=first_cell(c,m,0x80);
  int x=100+(int)cell%12,y=80+(int)cell/12;Uint8 v=c[cell];
  CHECK(asteroid1_effect_blend_source(explosionSpriteSheet,index,v,100,80,x,y));
  CHECK(!asteroid1_effect_blend_source(explosionSpriteSheet,index,(Uint8)(v^1),100,80,x,y));
  CHECK(!asteroid1_effect_blend_source(explosionSpriteSheet,index,(Uint8)(0x70|(v&15)),100,80,x,y));
  for(unsigned other=0;other<168;other++)if(m[other]) {
   size_t at=raw[other];Uint8 save=explosionSpriteSheet.data[at];explosionSpriteSheet.data[at]^=1;
   CHECK(!asteroid1_effect_blend_source(explosionSpriteSheet,index,v,100,80,x,y));
   explosionSpriteSheet.data[at]=save;CHECK(asteroid1_effect_blend_source(explosionSpriteSheet,index,v,100,80,x,y));
  }
  size_t start=(size_t)explosionSpriteSheet.data[2*(index-1)]+256u*explosionSpriteSheet.data[2*(index-1)+1];
  Uint8 save=explosionSpriteSheet.data[start];explosionSpriteSheet.data[start]=15;
  CHECK(!asteroid1_effect_blend_source(explosionSpriteSheet,index,v,100,80,x,y));
  explosionSpriteSheet.data[start]=save;CHECK(asteroid1_effect_blend_source(explosionSpriteSheet,index,v,100,80,x,y));
 }
 CHECK(frames==22);
 const unsigned empty[]={251,270,271,273,274};
 for(unsigned i=0;i<5;i++) {CHECK(reference_decode(explosionSpriteSheet,empty[i],c,m,NULL));
  for(unsigned cell=0;cell<168;cell++) {CHECK(!m[cell]);CHECK(!asteroid1_effect_blend_source(explosionSpriteSheet,empty[i],0x80,100,80,100+(int)cell%12,80+(int)cell/12));}
 }
}

static void layout_tests(void)
{
 reset(8);CHECK(asteroid1_effect_blend_layout(game_screen));
 #define BAD(field,value) do {__typeof__(field) save=(field);(field)=(value);CHECK(!asteroid1_effect_blend_layout(game_screen));(field)=save;} while(0)
 BAD(game_probe_density,1);BAD(game_probe_density,3);BAD(game_probe_density,16);BAD(VGAScreen,NULL);BAD(game_screen->pixels,NULL);BAD(game_screen->format,NULL);BAD(game_screen->w,319);BAD(game_screen->h,199);BAD(game_screen->pitch,324);BAD(game_screen->format->format,SDL_PIXELFORMAT_ARGB8888);BAD(game_screen->format->BitsPerPixel,16);BAD(game_screen->format->BytesPerPixel,2);
 BAD(canvas->pixels,NULL);BAD(canvas->format,NULL);BAD(canvas->w,2559);BAD(canvas->h,1599);BAD(canvas->pitch,canvas->w*4-4);BAD(canvas->pitch,canvas->w*4+1);BAD(canvas->format->format,SDL_PIXELFORMAT_INDEX8);BAD(canvas->format->BitsPerPixel,24);BAD(canvas->format->BytesPerPixel,3);BAD(hd_owner,NULL);BAD(cloud_owner,NULL);BAD(green_first,NULL);
 void *save=canvas->pixels;canvas->pixels=(Uint8 *)save+1;CHECK(!asteroid1_effect_blend_layout(game_screen));canvas->pixels=game_screen->pixels;CHECK(!asteroid1_effect_blend_layout(game_screen));canvas->pixels=save;
 SDL_Surface *saved=canvas;canvas=NULL;CHECK(!asteroid1_effect_blend_layout(game_screen));canvas=saved;CHECK(!asteroid1_effect_blend_layout(NULL));
 reset(4);CHECK(asteroid1_effect_blend_layout(game_screen));
 #undef BAD
}
/* Negative paths use the real callback, real pixel fallback, and real complete
 * rectangle restore. No fake fallback substitutes for restoration behavior. */
static void negative_callback(unsigned seed_index,unsigned kind,int owners,bool live)
{
 reset(8);++negative_cases;Uint8 c[168],m[168];size_t raw[168];CHECK(reference_decode(explosionSpriteSheet,seed_index,c,m,raw));unsigned cell=first_cell(c,m,-1);int ox=100,oy=80,x=ox+(int)cell%12,y=oy+(int)cell/12;Uint8 source=c[cell];Uint32 prior[64];Uint8 own[64];prepare_block(x,y,owners,prior,own);Uint8 after=indexed_after(0x3d,source);*index_at(x,y)=after;
 Sprite2_array bank=explosionSpriteSheet;unsigned index=seed_index;Uint8 changed=0;size_t changed_at=0;
 if(live) {regions[0]=(HdRegion){{x-1,y-1,3,3},8,27,MIRROR_NORMAL,true};region_count=1;
  for(int yy=y-1;yy<=y+1;yy++)for(int xx=x-1;xx<=x+1;xx++) {Uint32 temp[64];Uint8 tempown[64];prepare_block(xx,yy,owners,temp,tempown);}
 }
 switch(kind) {
  case 0:level_scope=false;break;case 1:game_probe_enabled=false;asteroid_hd_lease=false;break;case 2:game_probe_original_reference=true;break;case 3:source^=1;break;case 4:*index_at(x,y)^=1;break;case 5:bank.size--;break;case 6:ox=-1;break;case 7:oy=INT_MAX;break;case 8:index=266;break;case 9:rgb_palette[(source&240)+7]=0xffffff;rgb_palette[(source&240)+8]=0;break;case 10:xmas=true;break;
  case 11:changed_at=raw[cell];changed=bank.data[changed_at];bank.data[changed_at]^=1;break;
  case 12:bank.data=malloc(bank.size);CHECK(bank.data);memcpy(bank.data,explosionSpriteSheet.data,bank.size);break;
  case 13:game_probe_enabled=false;asteroid_hd_lease=true;actor_scope=false;break;case 14:game_probe_enabled=false;asteroid_hd_lease=false;actor_scope=true;break;
  default:CHECK(false);
 }
 blend_source_index=73;render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),source,bank,index,ox,oy);CHECK(blend_source_index==73);CHECK(fallback_calls==1&&metric.calls==1&&!metric.rgba);CHECK(metric.index==index);CHECK(expected[y*320+x]==*index_at(x,y));CHECK(*index_at(x,y)==(kind==4?(Uint8)(after^1):after));
 if(live) {
  CHECK(!reject_reason&&restore_calls==1&&restore_index==index&&local_regions==1&&local_blocks==9);CHECK(!regions[0].live&&restored_rect.w==3&&restored_rect.h==3&&restored_request.w==3);
  for(int yy=y-1;yy<=y+1;yy++)for(int xx=x-1;xx<=x+1;xx++)for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++) {size_t n=(size_t)(yy*8+sy)*canvas->w+xx*8+sx;CHECK(*rgba_at(xx*8+sx,yy*8+sy)==palette_rgb(*index_at(xx,yy)));CHECK(!hd_owner[n]&&!cloud_owner[n]&&!green_first[n]);}
 } else if(owners==0) {CHECK(!reject_reason&&!restore_calls);for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)CHECK(*rgba_at(x*8+sx,y*8+sy)==palette_rgb(*index_at(x,y)));}
 else {CHECK(reject_reason&&!strcmp(reject_reason,"local-blend-owner-without-region"));CHECK(!restore_calls);for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)CHECK(*rgba_at(x*8+sx,y*8+sy)==prior[sy*8+sx]);}
 if(kind==11)explosionSpriteSheet.data[changed_at]=changed;if(kind==12)free(bank.data);
}
static void suppression_and_font(void)
{
 Uint8 c[168],m[168];CHECK(reference_decode(explosionSpriteSheet,122,c,m,NULL));unsigned cell=first_cell(c,m,-1);int x=100+(int)cell%12,y=80+(int)cell/12;Uint8 source=c[cell];
 for(unsigned mode=0;mode<4;mode++) {reset(8);Uint32 prior[64];Uint8 own[64];prepare_block(x,y,-1,prior,own);*index_at(x,y)=indexed_after(0x3d,source);
  if(mode<2){suppress=true;game_probe_original_reference=mode==1;}else if(mode==2)font_reject=1;else reject_reason="already-rejected";
  render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),source,explosionSpriteSheet,122,100,80);CHECK(fallback_calls==1&&metric.calls==1&&!metric.rgba);CHECK(expected[y*320+x]==*index_at(x,y));
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){size_t n=(size_t)(y*8+sy)*canvas->w+x*8+sx;CHECK(*rgba_at(x*8+sx,y*8+sy)==prior[sy*8+sx]);if(mode<2)CHECK(hd_owner[n]==(mode==1?2:1));else CHECK(hd_owner[n]==own[sy*8+sx]);}
  if(mode<2)CHECK(selected[y*320+x]&&font_calls==0);else CHECK(reject_reason);if(mode==2)CHECK(font_calls==1);
 }
}
static void bounds_and_no_write(void)
{
 reset(8);size_t bytes=canvas_n()*4;Uint32 *copy=malloc(bytes);CHECK(copy);memcpy(copy,canvas->pixels,bytes);Uint8 before[64000];memcpy(before,expected,sizeof(before));
 Uint8 *addresses[]={(Uint8 *)game_screen->pixels-1,(Uint8 *)game_screen->pixels+64000};
 for(unsigned i=0;i<2;i++) {reject_reason=NULL;metric.calls=0;render_mirror_sprite2_blend_pixel(game_screen,addresses[i],0x75,explosionSpriteSheet,122,100,80);CHECK(reject_reason&&!strcmp(reject_reason,"invalid-write-address"));CHECK(!metric.calls&&!memcmp(copy,canvas->pixels,bytes)&&!memcmp(before,expected,sizeof(before)));}
 reject_reason=NULL;metric.calls=0;render_mirror_sprite2_blend_pixel(NULL,index_at(100,80),0x75,explosionSpriteSheet,122,100,80);CHECK(!metric.calls&&!reject_reason&&!memcmp(copy,canvas->pixels,bytes)&&!memcmp(before,expected,sizeof(before)));
 SDL_Surface foreign=*game_screen;render_mirror_sprite2_blend_pixel(&foreign,index_at(100,80),0x75,explosionSpriteSheet,122,100,80);CHECK(!metric.calls&&!reject_reason&&!memcmp(copy,canvas->pixels,bytes)&&!memcmp(before,expected,sizeof(before)));
 game_screen->pitch=321;render_mirror_sprite2_blend_pixel(game_screen,(Uint8 *)game_screen->pixels+320,0x75,explosionSpriteSheet,122,100,80);game_screen->pitch=320;CHECK(!metric.calls&&!reject_reason&&!memcmp(copy,canvas->pixels,bytes)&&!memcmp(before,expected,sizeof(before)));
 reject_reason=NULL;active=false;metric.calls=0;render_mirror_sprite2_blend_pixel(game_screen,index_at(100,80),0x75,explosionSpriteSheet,122,100,80);CHECK(!metric.calls&&!reject_reason&&!memcmp(copy,canvas->pixels,bytes)&&!memcmp(before,expected,sizeof(before)));free(copy);
 /* A successful callback changes exactly its logical block and metadata cell. */
 reset(4);for(size_t n=0;n<canvas_n();n++){((Uint32 *)canvas->pixels)[n]=UINT32_C(0xff456789);hd_owner[n]=(Uint8)(n%3);cloud_owner[n]=1;green_first[n]=87;}
 Uint8 c[168],m[168];CHECK(reference_decode(explosionSpriteSheet,122,c,m,NULL));unsigned cell=first_cell(c,m,-1);int x=100+(int)cell%12,y=80+(int)cell/12;*index_at(x,y)=indexed_after(0x3d,c[cell]);render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),c[cell],explosionSpriteSheet,122,100,80);CHECK(metric.rgba);
 for(int yy=0;yy<canvas->h;yy++)for(int xx=0;xx<canvas->w;xx++){size_t n=(size_t)yy*canvas->w+xx;bool in=xx>=x*4&&xx<(x+1)*4&&yy>=y*4&&yy<(y+1)*4;CHECK(hd_owner[n]==n%3);if(!in){CHECK(*rgba_at(xx,yy)==UINT32_C(0xff456789));CHECK(cloud_owner[n]==1&&green_first[n]==87);}else CHECK(!cloud_owner[n]&&!green_first[n]);}
 for(unsigned i=0;i<64000;i++)CHECK(expected[i]==(i==(unsigned)(y*320+x)?*index_at(x,y):0x3d));
}
static void full_blit(unsigned index,int d,int ox,int oy)
{
 reset(d);++full_blits;Uint8 c[168],m[168],after[64000];CHECK(reference_decode(explosionSpriteSheet,index,c,m,NULL));memcpy(after,game_screen->pixels,sizeof(after));size_t pixels=canvas_n();Uint32 *oracle=malloc(pixels*4);CHECK(oracle);
 for(size_t n=0;n<pixels;n++){((Uint32 *)canvas->pixels)[n]=oracle[n]=UINT32_C(0xff000000)|((n*37+0x253749)&0xffffffu);hd_owner[n]=(Uint8)(n%3);cloud_owner[n]=1;green_first[n]=81;}
 unsigned writes=0;
 for(unsigned cell=0;cell<168;cell++)if(m[cell]) {int x=ox+(int)cell%12,y=oy+(int)cell/12;if(y<0||y>=200)continue;CHECK(x>=0&&x<320);++writes;after[y*320+x]=indexed_after(after[y*320+x],c[cell]);for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;oracle[n]=hd_owner[n]==1?reference_blend(oracle[n],c[cell]):palette_rgb(after[y*320+x]);}}
 blit_sprite2_blend(game_screen,ox,oy,explosionSpriteSheet,index);CHECK(!reject_reason&&!fallback_calls);CHECK(metric.calls==writes);CHECK(!memcmp(game_screen->pixels,after,sizeof(after))&&!memcmp(expected,after,sizeof(after)));CHECK(!memcmp(canvas->pixels,oracle,pixels*4));free(oracle);
}
static void legacy_tests(void)
{
 /* Legacy behavior is also source-compared to baseline by the Python runner. */
 reset(8);asteroid_hd_enabled=false;Uint32 prior[64];Uint8 own[64];int x=105,y=85;Uint8 source=0x75;prepare_block(x,y,-1,prior,own);*index_at(x,y)=indexed_after(0x3d,source);render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),source,explosionSpriteSheet,122,100,80);CHECK(metric.rgba&&!fallback_calls&&!reject_reason);
 reset(8);asteroid_hd_enabled=false;prepare_block(x,y,-1,prior,own);*index_at(x,y)=indexed_after(0x3d,source);render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),source,explosionSpriteSheet,3,100,80);CHECK(!metric.rgba&&fallback_calls&&reject_reason);
 reset(8);asteroid_hd_enabled=false;prepare_block(x,y,-1,prior,own);regions[0]=(HdRegion){{100,80,12,14},9,233,MIRROR_NORMAL,true};region_count=1;*index_at(x,y)=indexed_after(0x3d,source);render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),source,explosionSpriteSheet,3,100,80);CHECK(metric.rgba&&!fallback_calls&&!reject_reason);
 reset(8);asteroid_hd_enabled=false;game_probe_known_blend=false;prepare_block(x,y,0,prior,own);*index_at(x,y)=indexed_after(0x3d,source);render_mirror_sprite2_blend_pixel(game_screen,index_at(x,y),source,explosionSpriteSheet,122,100,80);CHECK(!metric.rgba&&fallback_calls&&!reject_reason);
}

/* Bank9 is loaded read-only from the ordinary main shape container. Independent
 * offset parsing and RLE walking test all five finite Talon poses, never emit art. */
static unsigned le32(const Uint8 *b)
{return (unsigned)b[0]|((unsigned)b[1]<<8)|((unsigned)b[2]<<16)|((unsigned)b[3]<<24);}
static void talon_tests(const char *path)
{
 FILE *f=fopen(path,"rb");CHECK(f);Uint8 header[54];CHECK(fread(header,1,sizeof(header),f)==sizeof(header));
 CHECK(header[0]==13&&header[1]==0);unsigned begin=le32(header+2+8*4),end=le32(header+2+9*4);CHECK(end>begin&&end-begin==33484);
 spriteSheet9.size=end-begin;spriteSheet9.data=malloc(spriteSheet9.size);CHECK(spriteSheet9.data);CHECK(!fseek(f,begin,SEEK_SET));CHECK(fread(spriteSheet9.data,1,spriteSheet9.size,f)==spriteSheet9.size);CHECK(!fclose(f));
 for(unsigned base=229;base<=237;base+=2)for(unsigned piece=0;piece<4;piece++) {
  unsigned index=base+(piece&1)+(piece/2)*19;int ox=95+(piece&1)*12,oy=73+(piece/2)*14;
  Uint8 c[168],m[168];size_t raw[168];CHECK(reference_decode(spriteSheet9,index,c,m,raw));unsigned cell=first_cell(c,m,0x10);int x=ox+(int)cell%12,y=oy+(int)cell/12;Uint8 source=c[cell];
  for(int d=4;d<=8;d+=4)for(int owners=-1;owners<=1;owners++) {
   reset(d);asteroid1_talon_blend_pose(1,spriteSheet9,233,(int)base,10,100,80);asteroid1_talon_blend_begin(game_screen,95,73,spriteSheet9,base,MIRROR_BLEND,ENTITY_QUAD);
   CHECK(asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));
   Uint32 prior[64];Uint8 own[64];unsigned hd=prepare_block(x,y,owners,prior,own);*index_at(x,y)=indexed_after(0x3d,source);
   asteroid1_sprite2_blend_pixel(game_screen,index_at(x,y),source,spriteSheet9,index,ox,oy);
   CHECK(metric.rgba&&metric.subpixels==hd&&metric.blocks==0&&!fallback_calls);CHECK(expected[y*320+x]==indexed_after(0x3d,source));
   for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){unsigned k=(unsigned)(sy*d+sx);CHECK(*rgba_at(x*d+sx,y*d+sy)==(own[k]==1?reference_blend(prior[k],source):palette_rgb(*index_at(x,y))));}
   asteroid1_talon_blend_end();CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));
  }
  reset(8);asteroid1_talon_blend_pose(1,spriteSheet9,233,(int)base,10,100,80);asteroid1_talon_blend_begin(game_screen,95,73,spriteSheet9,base,MIRROR_BLEND,ENTITY_QUAD);
  for(unsigned k=0;k<168;k++)if(m[k]) {Uint8 save=spriteSheet9.data[raw[k]];spriteSheet9.data[raw[k]]^=1;CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));spriteSheet9.data[raw[k]]=save;CHECK(asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));}
  unsigned start=spriteSheet9.data[2*(index-1)]+256u*spriteSheet9.data[2*(index-1)+1];Uint8 save=spriteSheet9.data[start];spriteSheet9.data[start]=15;CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));spriteSheet9.data[start]=save;
  CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source^1,ox,oy,x,y));CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,0x80|(source&15),ox,oy,x,y));CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox+1,oy,x,y));
  ++mirror_logic_tick;CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));--mirror_logic_tick;
  twoPlayerMode=true;CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));twoPlayerMode=false;galagaMode=true;CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));galagaMode=false;twoPlayerLinked=true;CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));twoPlayerLinked=false;xmas=true;CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));xmas=false;
  Sprite2_array foreign=spriteSheet9;foreign.data=explosionSpriteSheet.data;CHECK(!asteroid1_talon_blend_source(foreign,index,source,ox,oy,x,y));foreign=spriteSheet9;foreign.size--;CHECK(!asteroid1_talon_blend_source(foreign,index,source,ox,oy,x,y));
  for(unsigned wrong=0;wrong<8;wrong++) {
   asteroid1_talon_blend_pose(wrong==0?2:1,spriteSheet9,wrong==1?1:233,(int)base,wrong==2?0:10,100,80);
   asteroid1_talon_blend_begin(game_screen,wrong==3?96:95,wrong==4?74:73,spriteSheet9,wrong==5?base+2:base,wrong==6?MIRROR_NORMAL:MIRROR_BLEND,wrong==7?0:ENTITY_QUAD);
   CHECK(!asteroid1_talon_blend_source(spriteSheet9,index,source,ox,oy,x,y));
   Uint32 prior[64];Uint8 own[64];prepare_block(x,y,1,prior,own);*index_at(x,y)=indexed_after(0x3d,source);fallback_calls=0;memset(&metric,0,sizeof(metric));
   asteroid1_sprite2_blend_pixel(game_screen,index_at(x,y),source,spriteSheet9,index,ox,oy);
   CHECK(metric.calls==1&&!metric.rgba&&fallback_calls==1&&*index_at(x,y)==indexed_after(0x3d,source));
  }
 }
 asteroid1_talon_blend_reset();free(spriteSheet9.data);memset(&spriteSheet9,0,sizeof(spriteSheet9));
 printf("Talon: all5 bank9 poses/20 quadrants, d4/8, classic/HD/mixed ownership, per-cell corruption, coverage mutation and finite role negatives passed\n");
}

int main(int argc,char **argv)
{
 CHECK(argc==2||argc==3);FILE *f=fopen(argv[1],"rb");CHECK(f);CHECK(!fseek(f,0,SEEK_END));long size=ftell(f);CHECK(size==17810);CHECK(!fseek(f,0,SEEK_SET));explosionSpriteSheet.size=(size_t)size;explosionSpriteSheet.data=malloc((size_t)size);CHECK(explosionSpriteSheet.data);CHECK(fread(explosionSpriteSheet.data,1,(size_t)size,f)==(size_t)size);CHECK(!fclose(f));
 SDL_PixelFormat sf={SDL_PIXELFORMAT_INDEX8,8,1},cf={SDL_PIXELFORMAT_ARGB8888,32,4};Uint8 *screen_allocation=malloc(64000*3);CHECK(screen_allocation);SDL_Surface s={320,200,320,screen_allocation+64000,&sf,{0,0,320,200}},cv={2560,1600,10240,malloc(2560u*1600*4),&cf,{0,0,2560,1600}};CHECK(cv.pixels);game_screen=VGAScreen=&s;canvas=&cv;
 hd_owner=malloc(2560u*1600);cloud_owner=malloc(2560u*1600);green_first=malloc(2560u*1600*2);green_under_owner=malloc(2560u*1600);CHECK(hd_owner&&cloud_owner&&green_first&&green_under_owner);memset(cv.pixels,0,2560u*1600*4);memset(hd_owner,0,2560u*1600);memset(cloud_owner,0,2560u*1600);memset(green_first,0,2560u*1600*2);memset(green_under_owner,0,2560u*1600);
 source_tests();shield_source_mutations();layout_tests();
 for(unsigned index=1;index<=275;index++)if(supported(index)){positive(index,4,-1,100,80,UINT_MAX);positive(index,8,-1,100,80,UINT_MAX);}
 fixture_policy=1;positive(122,8,0x40,100,80,UINT_MAX);positive(255,8,0x80,100,80,UINT_MAX);fixture_policy=0;positive(173,4,0x40,100,80,UINT_MAX);
 Uint8 c[168],m[168];CHECK(reference_decode(explosionSpriteSheet,3,c,m,NULL));unsigned bottom=UINT_MAX;for(unsigned i=156;i<168;i++)if(m[i]){bottom=i;break;}CHECK(bottom!=UINT_MAX);positive(3,8,-1,0,-13,bottom);
 CHECK(reference_decode(explosionSpriteSheet,173,c,m,NULL));unsigned top=UINT_MAX;for(unsigned i=0;i<12;i++)if(m[i]){top=i;break;}CHECK(top!=UINT_MAX);positive(173,4,-1,308,199,top);
 const unsigned negative_indices[]={122,230,255,275};for(unsigned i=0;i<4;i++)for(unsigned kind=0;kind<15;kind++){negative_callback(negative_indices[i],kind,1,false);negative_callback(negative_indices[i],kind,0,false);negative_callback(negative_indices[i],kind,1,true);}
 suppression_and_font();bounds_and_no_write();
 full_blit(122,4,100,80);full_blit(145,8,100,80);full_blit(173,8,308,80);full_blit(3,8,0,-13);full_blit(173,4,308,199);for(unsigned i=229;i<=275;i++)if((i>=229&&i<=237)||(i>=248&&i<=256)||i>=267){full_blit(i,4,100,80);full_blit(i,8,100,80);}legacy_tests();
 if(argc==3)talon_tests(argv[2]);
 printf("PASS %lu checks; %u reset cases; %u positive callback cases; %u negative callback cases; %u original indexed blits; 116 warm+22 shield source frames,27 original shield animation slots, d4/8, first-level baseline identity checked by runner\n",checks,cases,positive_cases,negative_cases,full_blits);
 free(explosionSpriteSheet.data);free(screen_allocation);free(cv.pixels);free(hd_owner);free(cloud_owner);free(green_first);free(green_under_owner);return 0;
}
