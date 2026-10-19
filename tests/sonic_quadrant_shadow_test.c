/* Extracted-production shadow compositor tests. No engine or replacement blitter. */
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
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
#include "sprite-type.inc"
typedef int EntityDrawStyle; typedef int EntityDrawLayout;
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW,ENTITY_TILE=0,ENTITY_QUAD=1};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#define MIN(a,b) ((a)<(b)?(a):(b))
#define COUNT(a) (sizeof(a)/sizeof(*(a)))
#include "types.inc"
static bool asteroid_hd_enabled; /* Optional enemy catalog stays disabled here. */
static bool twoPlayerMode,galagaMode,twoPlayerLinked,xmas,active=true,suppress,suppress_cloud,suppress_green_smoke;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend=true;
static int game_probe_density=8; static const char *game_probe_assets,*reject_reason;
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value,data_fixed_value,fixed_pickup_flash;
static SDL_PixelFormat format={8,1},canvas_format={32,4};
static Uint8 indexed[328*200];
static SDL_Surface screen={320,200,320,indexed,&format},*game_screen=&screen,*VGAScreen=&screen;
static SDL_Surface hd={2560,1600,2560*4,NULL,&canvas_format},*canvas=&hd;
static unsigned banking_draw_player;static uint64_t mirror_logic_tick=100;static TalonBank talon_banks[2];
static VulcanShadowCall vulcan_shadow;
static struct {const Uint8 *rgba;char path[1024];} vulcan_shadow_resource[COUNT(vulcan_shadow_pins)],vulcan_shadow_coverage_resource[3];
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[65536];static unsigned region_count,draws,occlusions;
static Uint8 expected[320*200],selected[320*200],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;static char all_rejections[512];
static Uint32 *oracle;static Uint8 *oracle_owner,*oracle_cloud,*oracle_selected;static Uint16 *oracle_green;
static unsigned draw_calls,original_calls,end_calls,probe_calls,file_opens,allocations,font_effects;
static unsigned geometry_cases,indexed_cases,gate_cases,source_cases,resource_cases,begin_cases,pixel_cases,classic_cases,old_pin_cases,later_write_cases;
static uint64_t rgb_checked,indexed_checked,zero_samples,full_samples,partial_samples;
static bool last_mirrored;
#if defined(TEN_WEAPON_SHADOW_BATCH)
static const unsigned ids[10]={31,32,33,252,253,254,214,215,216,217};
#elif defined(ENERGY_SHADOW_BATCH)
static const unsigned ids[18]={6,44,73,63,82,16,54,130,131,149,150,223,224,242,243,143,144,27};
#else
static const unsigned ids[4]={105,106,124,125};
#endif
#ifdef TEN_WEAPON_SHADOW_BATCH
static const unsigned old_ids[35]={67,70,121,122,163,164,201,202,279,280,225,244,226,105,106,124,125,6,44,73,63,82,16,54,130,131,149,150,223,224,242,243,143,144,27};
#else
static const unsigned old_ids[13]={67,70,121,122,163,164,201,202,279,280,225,244,226};
#endif
static Uint8 references[COUNT(ids)][336];static const char *full_root;
static Asset *rear_p11_shadow_current(const VulcanShadowCall*v,SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){(void)v;(void)s;(void)x;(void)y;(void)b;(void)i;assert(0);return NULL;}
static bool rear_p11_shadow_birth(const VulcanShadowCall*v){(void)v;assert(0);return false;}
static bool cash25_surface_ready(SDL_Surface*s,int x,int y){(void)s;(void)x;(void)y;assert(0);return false;}
#define cash25_family_ready() false
#define cash75_family_ready() false
#define cash50_family_ready() false
#define gem100_family_ready() false
#define gem250_family_ready() false
#define game_probe_scene_draw(...) ((void)0)
#define fixed_pickup_flash_draw(...) (false)
#define data_value_draw(...) (false)
#define data_frame_pixel(...) ((void)0)
#define data_portrait_pixel(...) ((void)0)
#define storm_pixel(...) ((void)0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
static bool font_pixel(int x,int y,Uint8 v,int style){(void)x;(void)y;(void)v;(void)style;return false;}
static void font_before_effect(SDL_Rect r){assert(r.w==12&&r.h==14);font_effects++;}
static void restore_classic_rect(SDL_Rect r){(void)r;assert(!"blend restoration outside this shadow test");}
static Asset *talon_frame(unsigned i){(void)i;assert(0);return NULL;}
static bool draw_asset(int x,int y,Asset*a,int style,const SDL_Rect*r){(void)x;(void)y;assert(a&&a->valid&&!r);if(style==MIRROR_SHADOW)return false;draw_calls++;return true;}
#include "functions.inc"
static Uint16 SDL_SwapLE16(Uint16 v){Uint8 b[2];memcpy(b,&v,2);return (Uint16)(b[0]|b[1]<<8);}
#define asset_debug_effect(...) ((void)0)
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define load_font_arrow_sprite_end() ((void)0)
#define pregame_font_sprite2_end() ((void)0)
static struct {ptrdiff_t offset;Uint8 value,source;int style;} writes[200];static unsigned write_count;
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style){assert(s==&screen&&p>=(Uint8*)s->pixels&&p<(Uint8*)s->pixels+s->pitch*s->h&&write_count<COUNT(writes));writes[write_count].offset=p-(Uint8*)s->pixels;writes[write_count].value=*p;writes[write_count].source=v;writes[write_count++].style=style;production_render_mirror_pixel(s,p,v,style);}
static void render_mirror_sprite2_blend_pixel(SDL_Surface*s,Uint8*p,Uint8 v,Sprite2_array b,unsigned i,int x,int y){(void)b;(void)i;(void)x;(void)y;render_mirror_pixel(s,p,v,MIRROR_BLEND);}
#include "blitters.inc"
static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){original_calls++;production_blit_sprite2(s,x,y,b,i);}
static void blit_sprite2_blend(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){original_calls++;production_blit_sprite2_blend(s,x,y,b,i);}
static void blit_sprite2_darken(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){original_calls++;production_blit_sprite2_darken(s,x,y,b,i);}
#define blit_sprite2x2(...) assert(!"unexpected quad")
#define blit_sprite2x2_blend(...) assert(!"unexpected quad blend")
#define blit_sprite2x2_darken(...) assert(!"unexpected quad shadow")
static void game_probe_draw(int role,unsigned i,int x,int y,int style,int layout,bool mirrored){assert(role==8&&layout==ENTITY_TILE&&style==ENTITY_SHADOW);(void)i;(void)x;(void)y;probe_calls++;last_mirrored=mirrored;}
#include "wrappers.inc"
FILE *__real_fopen(const char*,const char*);void *__real_malloc(size_t);
FILE *__wrap_fopen(const char*a,const char*b){file_opens++;return __real_fopen(a,b);}
void *__wrap_malloc(size_t n){allocations++;return __real_malloc(n);}
static Uint8 *read_file(const char*p,size_t*n){FILE*f=fopen(p,"rb");assert(f&&!fseek(f,0,SEEK_END));long l=ftell(f);assert(l>0&&!fseek(f,0,SEEK_SET));Uint8*b=malloc((size_t)l);assert(b&&fread(b,1,(size_t)l,f)==(size_t)l&&!fclose(f));*n=(size_t)l;return b;}
static void clear_assets(void){for(size_t i=0;i<COUNT(assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(assets[i]));}memset(vulcan_shadow_resource,0,sizeof(vulcan_shadow_resource));memset(vulcan_shadow_coverage_resource,0,sizeof(vulcan_shadow_coverage_resource));}
static void flags(unsigned b){twoPlayerMode=!!(b&1);galagaMode=!!(b&2);twoPlayerLinked=!!(b&4);}
static void defaults(void){flags(0);xmas=false;active=true;reject_reason=NULL;game_probe_density=8;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;game_probe_assets=full_root;game_screen=VGAScreen=&screen;screen=(SDL_Surface){320,200,320,indexed,&format};format=(SDL_PixelFormat){8,1};canvas=&hd;hd.w=2560;hd.h=1600;hd.pitch=2560*4;suppress=suppress_cloud=suppress_green_smoke=false;region_count=0;vulcan_shadow_clear();all_rejections[0]=0;write_count=0;}
static Uint8 native_before(int x,int y){return (Uint8)((y*320+x)*29+23);}
static Uint32 palette_oracle(Uint8 i){return 0xff000000u|(rgb_palette[i]&0xffffffu);}
static Uint32 half_oracle(Uint32 c){Uint32 v=0xff000000u;for(unsigned shift=0;shift<24;shift+=8)v|=(((((c>>shift)&255u)+1)/2)<<shift);return v;}
static Uint32 cloud_oracle(Uint32 c,Uint8 b,Uint8 a){if(b==a)return c;Uint32 v=0xff000000u;for(unsigned s=0;s<24;s+=8){unsigned den=(rgb_palette[b]>>s)&255u,num=(rgb_palette[a]>>s)&255u,n=(c>>s)&255u;n=den?(n*num+den/2)/den:n;if(n>255)n=255;v|=n<<s;}return v;}
static Uint32 weighted_oracle(Uint32 c,Uint32 dark,unsigned a){Uint32 v=0xff000000u;for(unsigned s=0;s<24;s+=8)v|=(((((c>>s)&255u)*(255-a)+((dark>>s)&255u)*a+127)/255)<<s);return v;}
static void scene(int x,int y,int underlay,int pitch){defaults();screen.pitch=pitch;for(unsigned n=0;n<sizeof(indexed);n++)indexed[n]=0xcd;for(int yy=0;yy<200;yy++)for(int xx=0;xx<320;xx++)indexed[yy*pitch+xx]=expected[yy*320+xx]=native_before(xx,yy);memset(selected,0,sizeof(selected));memset(oracle_selected,0,sizeof(selected));
 int x0=x>0?x-1:0,x1=x+13<320?x+13:320,y0=y>0?y-1:0,y1=y+15<200?y+15:200;
 for(int yy=y0;yy<y1;yy++)for(int xx=x0;xx<x1;xx++)for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  unsigned n=(unsigned)(yy*8+sy)*2560+xx*8+sx;Uint32 rgb=underlay?0xff000000u|((n*53u+sx*17u)&0xffffffu):palette_oracle(native_before(xx,yy));
  ((Uint32*)hd.pixels)[n]=oracle[n]=rgb;hd_owner[n]=oracle_owner[n]=underlay?1:0;cloud_owner[n]=oracle_cloud[n]=underlay==2;green_first[n]=oracle_green[n]=7;
 }
}
static void oracle_shadow(unsigned id,int x,int y,bool accepted){Uint8 source[336]={0};assert(decode_tile(spriteSheet8,id,source,source+168,12,0,0));int k=vulcan_shadow_member(id);const Uint8*rgba=NULL;if(accepted){assert(k>=0);rgba=vulcan_shadow_pins[k].coverage_slot?assets[vulcan_shadow_pins[k].coverage_slot].rgba:assets[vulcan_shadow_pins[k].slot].rgba;assert(rgba);}
 for(int cy=0;cy<14;cy++)for(int cx=0;cx<12;cx++){int xx=x+cx,yy=y+cy;if(xx<0||xx>=320||yy<0||yy>=200)continue;Uint8 before=native_before(xx,yy),after=(Uint8)((before&240)|((before&15)/2));bool covered=source[168+cy*12+cx]!=0;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){unsigned n=(unsigned)(yy*8+sy)*2560+xx*8+sx;Uint32 old=oracle[n];
   if(accepted){unsigned a=rgba[4*((cy*8+sy)*96+cx*8+sx)+3];if(!a)zero_samples++;else if(a==255)full_samples++;else partial_samples++;
    if(a){Uint32 dark=oracle_owner[n]==1?(oracle_cloud[n]?cloud_oracle(old,before,after):half_oracle(old)):palette_oracle(after);Uint32 next=weighted_oracle(old,dark,a);if(next!=old){oracle_owner[n]=1;oracle_selected[yy*320+xx]=1;}oracle[n]=next;oracle_green[n]=0;}
    if(covered){if(before!=after)oracle_owner[n]=1;oracle_green[n]=0;if(before!=after)oracle_selected[yy*320+xx]=1;}
   }else if(covered){oracle_green[n]=0;bool cloud=oracle_cloud[n]&&oracle_owner[n]==1;if(!cloud)oracle_cloud[n]=0;oracle[n]=cloud?cloud_oracle(old,before,after):oracle_owner[n]==1?half_oracle(old):palette_oracle(after);}
  }
 }
}
static void check_scene(int x,int y){int x0=x>0?x-1:0,x1=x+13<320?x+13:320,y0=y>0?y-1:0,y1=y+15<200?y+15:200;
 for(int yy=y0;yy<y1;yy++)for(int xx=x0;xx<x1;xx++)for(int sy=0;sy<8;sy++){unsigned n=(unsigned)(yy*8+sy)*2560+xx*8;assert(!memcmp((Uint32*)hd.pixels+n,oracle+n,8*4));assert(!memcmp(hd_owner+n,oracle_owner+n,8));assert(!memcmp(cloud_owner+n,oracle_cloud+n,8));assert(!memcmp(green_first+n,oracle_green+n,8*2));rgb_checked+=8;}
 assert(!memcmp(selected,oracle_selected,sizeof(selected)));
}
static void whole_canvas(void){assert(!memcmp(hd.pixels,oracle,2560u*1600*4));assert(!memcmp(hd_owner,oracle_owner,2560u*1600));assert(!memcmp(cloud_owner,oracle_cloud,2560u*1600));assert(!memcmp(green_first,oracle_green,2560u*1600*2));}
static void wrapper_case(unsigned id,int x,int y,int pitch,int underlay,bool accepted,bool cold){if(cold)clear_assets();scene(x,y,underlay,pitch);if(!cold&&accepted){unsigned h=draw_calls;assert(render_mirror_entity(&screen,x,y,spriteSheet8,id,MIRROR_NORMAL,ENTITY_TILE));assert(draw_calls==h+1);render_mirror_entity_end();}
 unsigned o=original_calls,p=probe_calls,d=draws;write_count=0;srand(3821);int r=rand();srand(3821);
 draw_entity_sprite2(&screen,x,y,spriteSheet8,id,ENTITY_SHADOW,ENTITY_TILE);assert(rand()==r&&original_calls==o+1&&probe_calls==p+1&&last_mirrored==accepted&&!vulcan_shadow.live&&!reject_reason&&draws==d+(unsigned)accepted);
 oracle_shadow(id,x,y,accepted);check_scene(x,y);Uint8 decoded[336]={0};assert(decode_tile(spriteSheet8,id,decoded,decoded+168,12,0,0));unsigned wi=0;
 for(int yy=0;yy<200;yy++)for(int xx=0;xx<pitch;xx++){Uint8 value=xx<320?native_before(xx,yy):0xcd;if(xx>=x&&xx<x+12&&yy>=y&&yy<y+14&&decoded[168+(yy-y)*12+xx-x]){value=(Uint8)((value&240)|((value&15)/2));assert(wi<write_count&&writes[wi].offset==yy*pitch+xx&&writes[wi].value==value&&!writes[wi].source&&writes[wi].style==MIRROR_SHADOW);wi++;}assert(indexed[yy*pitch+xx]==value);if(xx<320)assert(expected[yy*320+xx]==value);}
 assert(wi==write_count);indexed_checked+=(size_t)pitch*200;indexed_cases++;
}
static void geometry(void){for(unsigned k=0;k<COUNT(ids);k++)for(int pitch=320;pitch<=328;pitch+=8)for(int under=0;under<3;under++)for(int warm=0;warm<2;warm++){
#if defined(ENERGY_SHADOW_BATCH) || defined(TEN_WEAPON_SHADOW_BATCH)
 /* Pairwise representative coordinates, plus every boundary and all IDs.
  * Avoid multiplying all309x/213y positions by all finite authored resources. */
 const int xs[]={0,1,94,153,307,308},ys[]={-13,-12,-1,0,73,186,187,198,199};
 for(unsigned p=0;p<COUNT(xs);p++){wrapper_case(ids[k],xs[p],73,pitch,under,true,!warm);geometry_cases++;}
 for(unsigned p=0;p<COUNT(ys);p++){wrapper_case(ids[k],94,ys[p],pitch,under,true,!warm);geometry_cases++;}
#else
 for(int x=0;x<=308;x++){wrapper_case(ids[k],x,73,pitch,under,true,!warm);geometry_cases++;}
 for(int y=-13;y<=199;y++){wrapper_case(ids[k],94,y,pitch,under,true,!warm);geometry_cases++;}
#endif
 const int xy[][2]={{0,-13},{308,-13},{0,-1},{308,-1},{0,187},{308,187},{0,199},{308,199}};
 for(unsigned p=0;p<COUNT(xy);p++){wrapper_case(ids[k],xy[p][0],xy[p][1],pitch,under,true,!warm);geometry_cases++;}
 whole_canvas();}assert(zero_samples&&full_samples&&partial_samples);}
static void no_cache(unsigned id,SDL_Surface*s,int x,int y,Sprite2_array bank){Asset before[COUNT(assets)];memcpy(before,assets,sizeof(assets));unsigned f=file_opens,a=allocations;assert(!vulcan_shadow.live);
#ifdef SANITIZED
 __asan_poison_memory_region(assets,sizeof(assets));
#endif
 assert(!draw_vulcan_shadow(s,x,y,bank,id));
#ifdef SANITIZED
 __asan_unpoison_memory_region(assets,sizeof(assets));
#endif
 assert(!vulcan_shadow.live&&file_opens==f&&allocations==a&&!memcmp(before,assets,sizeof(assets)));gate_cases++;
}
static void gates(void){for(unsigned k=0;k<COUNT(ids);k++)for(int warm=0;warm<2;warm++)for(unsigned mode=1;mode<8;mode++){scene(94,73,1,320);clear_assets();if(warm)assert(get_asset(spriteSheet8,ids[k],ENTITY_TILE));flags(mode);no_cache(ids[k],&screen,94,73,spriteSheet8);}
 for(unsigned k=0;k<COUNT(ids);k++)for(int warm=0;warm<2;warm++)for(unsigned g=0;g<37;g++){scene(94,73,1,320);clear_assets();if(warm)assert(get_asset(spriteSheet8,ids[k],ENTITY_TILE));SDL_Surface alt=screen,*s=&screen;Sprite2_array b=spriteSheet8;int x=94,y=73;
  switch(g){case 0:game_probe_density=0;break;case 1:game_probe_density=1;break;case 2:game_probe_density=2;break;case 3:game_probe_density=4;break;case 4:game_probe_density=16;break;case 5:game_probe_missing=true;break;case 6:game_probe_invalid=true;break;case 7:game_probe_original_reference=true;break;case 8:game_probe_assets=NULL;break;case 9:xmas=true;break;case 10:active=false;break;case 11:reject_reason="existing-reject";break;case 12:s=&alt;break;case 13:s=NULL;break;case 14:screen.pixels=NULL;break;case 15:screen.w--;break;case 16:screen.h--;break;case 17:screen.pitch=319;break;case 18:screen.format=NULL;break;case 19:format.BitsPerPixel=32;break;case 20:format.BytesPerPixel=4;break;case 21:b.data=NULL;break;case 22:b.data++;break;case 23:b.size--;break;case 24:x=-1;break;case 25:x=309;break;case 26:y=-14;break;case 27:y=200;break;case 28:canvas=NULL;break;case 29:hd.w--;break;case 30:hd.h--;break;case 31:VGAScreen=&alt;break;case 32:game_screen=&alt;break;case 33:game_probe_density=-8;break;case 34:b.size=0;break;case 35:b.size=1;break;case 36:region_count=COUNT(regions);break;}
  if(g==36){Asset before[COUNT(assets)];memcpy(before,assets,sizeof(assets));assert(!draw_vulcan_shadow(s,x,y,b,ids[k])&&!vulcan_shadow.live);if(warm)assert(!memcmp(before,assets,sizeof(assets)));gate_cases++;}else no_cache(ids[k],s,x,y,b);
 }defaults();clear_assets();}
static size_t encode(Uint8*d,const Uint8*c,const Uint8*m){size_t n=0;for(unsigned y=0;y<14;y++){unsigned x=0;for(unsigned xx=0;xx<12;xx++)if(m[y*12+xx]){d[n++]=(Uint8)(16|(xx-x));d[n++]=c[y*12+xx];x=xx+1;}d[n++]=(Uint8)(12-x);}d[n++]=15;return n;}
static void sources(Uint8*normal,size_t ns,Uint8*christmas,size_t cs){Uint8*copy=malloc((ns>cs?ns:cs)+512);assert(copy);for(unsigned k=0;k<COUNT(ids);k++)for(int warm=0;warm<2;warm++)for(unsigned g=0;g<13;g++){defaults();clear_assets();memcpy(copy,normal,ns);spriteSheet8=(Sprite2_array){ns,copy};if(warm)assert(get_asset(spriteSheet8,ids[k],ENTITY_TILE));unsigned dir=2*(ids[k]-1);size_t pos=copy[dir]|((size_t)copy[dir+1]<<8);while(!(copy[pos]>>4))pos++;size_t end=pos;while(copy[end]!=15)end+=1+(copy[end]>>4);
 switch(g){case 0:copy[pos+1]^=1;break;case 1:copy[dir]=copy[dir+1]=255;break;case 2:spriteSheet8.size=0;break;case 3:spriteSheet8.size=dir+1;break;case 4:spriteSheet8.size=pos;break;case 5:spriteSheet8.size=pos+1;break;case 6:spriteSheet8.size=end;break;case 7:{unsigned d=2*(ids[(k+1)%COUNT(ids)]-1);copy[dir]=copy[d];copy[dir+1]=copy[d+1];break;}case 8:if(!christmas)continue;memcpy(copy,christmas,cs);spriteSheet8.size=cs;xmas=true;break;
 case 9:{Uint8 c[168],m[168];memcpy(c,references[k],168);memcpy(m,references[k]+168,168);unsigned hole=0;while(m[hole])hole++;assert(hole<168&&!c[hole]);m[hole]=255;copy[dir]=(Uint8)ns;copy[dir+1]=(Uint8)(ns>>8);spriteSheet8.size=ns+encode(copy+ns,c,m);break;}
 case 10:copy[pos]=0xf0;break;case 11:copy[pos]=0x1f;break;case 12:spriteSheet8.data=NULL;break;}
 no_cache(ids[k],&screen,94,73,spriteSheet8);source_cases++;
 /* Restore the same allocation, not a fresh pointer or a new cache. */
 xmas=false;memcpy(copy,normal,ns);spriteSheet8=(Sprite2_array){ns,copy};assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));render_mirror_shadow_end();source_cases++;
 }
 for(unsigned k=0;k<COUNT(ids);k++){defaults();clear_assets();memcpy(copy,normal,ns);spriteSheet8=(Sprite2_array){ns,copy};unsigned dir=2*(ids[k]-1);copy[dir]=(Uint8)ns;copy[dir+1]=(Uint8)(ns>>8);spriteSheet8.size=ns+encode(copy+ns,references[k],references[k]+168);assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));render_mirror_shadow_end();source_cases++;}
 clear_assets();free(copy);spriteSheet8=(Sprite2_array){ns,normal};defaults();}
static void resource_mutations(void){for(unsigned k=0;k<COUNT(ids);k++)for(unsigned g=0;g<18;g++){scene(94,73,1,320);clear_assets();Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert(a);Asset save=*a;int slot=vulcan_shadow_member(ids[k]);const Uint8*record=vulcan_shadow_resource[slot].rgba;char path[1024];memcpy(path,vulcan_shadow_resource[slot].path,sizeof(path));Uint8 byte=a->rgba[g==1?3:0];Uint8*clone=NULL;char longroot[1100];
  switch(g){case 0:a->rgba[0]^=1;break;case 1:a->rgba[3]^=1;break;case 2:a->valid=false;break;case 3:a->bank=9;break;case 4:a->index++;break;case 5:a->w--;break;case 6:a->h--;break;case 7:a->anchor_x++;break;case 8:a->anchor_y++;break;case 9:a->density=4;break;case 10:a->rgba=NULL;break;case 11:clone=malloc(43008);assert(clone);memcpy(clone,a->rgba,43008);a->rgba=clone;break;case 12:vulcan_shadow_resource[slot].rgba++;break;case 13:vulcan_shadow_resource[slot].path[0]^=1;break;case 14:game_probe_assets="different-root";break;case 15:memset(longroot,'q',sizeof(longroot)-1);longroot[sizeof(longroot)-1]=0;game_probe_assets=longroot;break;case 16:{Asset*other=get_asset(spriteSheet8,ids[(k+1)%COUNT(ids)],ENTITY_TILE);assert(other&&other->rgba&&other->rgba!=a->rgba);a->rgba=other->rgba;break;}case 17:a->bank=ASSET_PROTRON_SHADOW;break;}
  assert(!draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k])&&!vulcan_shadow.live);if(g<2)save.rgba[g==1?3:0]=byte;*a=save;vulcan_shadow_resource[slot].rgba=record;memcpy(vulcan_shadow_resource[slot].path,path,sizeof(path));free(clone);resource_cases++;check_scene(94,73);game_probe_assets=full_root;assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));render_mirror_shadow_end();resource_cases++;
 }defaults();clear_assets();}
static void resource_fixtures(const char*root){char path[2048],name[128];snprintf(path,sizeof(path),"%s/variants.tsv",root);FILE*f=fopen(path,"r");assert(f);unsigned id;int ok8,d8,ok4,d4;
 while(fscanf(f,"%127s %u %d %d %d %d",name,&id,&ok8,&d8,&ok4,&d4)==6){snprintf(path,sizeof(path),"%s/%s",root,name);for(unsigned warm=0;warm<2;warm++){scene(94,73,1,320);clear_assets();game_probe_assets=path;if(warm)(void)get_asset(spriteSheet8,id,ENTITY_TILE);bool expected8=ok8&&d8==8;unsigned d=draws;bool got=render_mirror_entity(&screen,94,73,spriteSheet8,id,MIRROR_SHADOW,ENTITY_TILE);assert(got==expected8);production_blit_sprite2_darken(&screen,94,73,spriteSheet8,id);render_mirror_entity_end();assert(!reject_reason&&!vulcan_shadow.live&&draws==d+(unsigned)expected8);oracle_shadow(id,94,73,expected8);check_scene(94,73);resource_cases++;}}
 assert(feof(f)&&!fclose(f));defaults();clear_assets();}
static uint64_t canvas_stamp(void){return vulcan_shadow_stamp(hd.pixels,2560u*1600*4);}
static void begin_faults(void){Uint8*normal=spriteSheet8.data;size_t ns=spriteSheet8.size;for(unsigned k=0;k<COUNT(ids);k++)for(unsigned g=0;g<34;g++){scene(94,73,1,320);assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));Asset*a=&assets[vulcan_shadow_pins[vulcan_shadow_member(ids[k])].slot],save=*a;int sk=vulcan_shadow_member(ids[k]);char path[1024];memcpy(path,vulcan_shadow_resource[sk].path,sizeof(path));Uint8 rgba=a->rgba[0];SDL_Surface alt=screen,*s=&screen;Sprite2_array bank=spriteSheet8;SDL_Surface hd_save=hd;int x=94,y=73;unsigned id=ids[k];Uint8*sourcebyte=NULL,sourcevalue=0;unsigned d=draws;uint64_t stamp=canvas_stamp();
  switch(g){case 0:twoPlayerMode=true;break;case 1:galagaMode=true;break;case 2:twoPlayerLinked=true;break;case 3:mirror_logic_tick++;break;case 4:s=&alt;break;case 5:screen.pixels=indexed+1;break;case 6:screen.format=&canvas_format;break;case 7:screen.pitch=328;break;case 8:screen.w--;break;case 9:screen.h--;break;case 10:bank.data++;break;case 11:bank.size--;break;case 12:spriteSheet8.data++;break;case 13:spriteSheet8.size--;break;case 14:x++;break;case 15:y++;break;case 16:id=ids[(k+1)%COUNT(ids)];break;case 17:game_probe_density=4;break;case 18:game_probe_missing=true;break;case 19:game_probe_invalid=true;break;case 20:game_probe_original_reference=true;break;case 21:game_probe_assets=NULL;break;case 22:game_probe_assets="different-root";break;case 23:xmas=true;break;case 24:active=false;break;case 25:reject_reason="prior";break;case 26:a->rgba[0]^=1;break;case 27:a->w--;break;case 28:vulcan_shadow_resource[sk].path[0]^=1;break;case 29:expected[73*320+94]^=1;break;case 30:region_count=COUNT(regions);break;case 31:hd.pixels=(Uint8*)hd.pixels+4;break;case 32:hd.pitch+=4;break;case 33:{size_t pos=normal[2*(id-1)]|((size_t)normal[2*(id-1)+1]<<8);while(!(normal[pos]>>4))pos++;sourcebyte=normal+pos+1;sourcevalue=*sourcebyte;*sourcebyte^=1;break;}}
  render_mirror_shadow_begin(s,x,y,bank,id);assert(!vulcan_shadow.live&&draws==d);hd=hd_save;assert(canvas_stamp()==stamp);*a=save;a->rgba[0]=rgba;memcpy(vulcan_shadow_resource[sk].path,path,sizeof(path));if(sourcebyte)*sourcebyte=sourcevalue;spriteSheet8=(Sprite2_array){ns,normal};begin_cases++;defaults();
 }
 /* A second begin after visual output has started rejects the frame. */
 scene(94,73,1,320);assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[0]));render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[0]);render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[0]);assert(reject_reason&&!strcmp(reject_reason,"vulcan-shadow-command-mismatch"));begin_cases++;defaults();clear_assets();}
static void pixel_faults(void){Uint8*normal=spriteSheet8.data;size_t ns=spriteSheet8.size;for(unsigned k=0;k<COUNT(ids);k++)for(unsigned g=0;g<25;g++){scene(94,73,2,320);assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);assert(vulcan_shadow.entered);unsigned cell=0;while(!references[k][168+cell])cell++;int x=94+(int)(cell%12),y=73+(int)(cell/12);Uint8*p=indexed+y*320+x;Uint8 before=*p;int style=MIRROR_SHADOW;SDL_Surface alt=screen,*s=&screen;SDL_Surface hd_save=hd;uint64_t stamp=canvas_stamp();
 switch(g){case 0:twoPlayerMode=true;break;case 1:galagaMode=true;break;case 2:twoPlayerLinked=true;break;case 3:mirror_logic_tick++;break;case 4:s=&alt;break;case 5:screen.pixels=indexed+1;break;case 6:screen.format=&canvas_format;break;case 7:screen.pitch=328;break;case 8:screen.w--;break;case 9:screen.h--;break;case 10:spriteSheet8.data++;break;case 11:spriteSheet8.size--;break;case 12:game_probe_density=4;break;case 13:game_probe_missing=true;break;case 14:game_probe_invalid=true;break;case 15:game_probe_original_reference=true;break;case 16:xmas=true;break;case 17:style=MIRROR_NORMAL;break;case 18:hd.pixels=(Uint8*)hd.pixels+4;break;case 19:hd.pitch+=4;break;case 20:expected[y*320+x]^=1;break;case 21:vulcan_shadow.coverage[cell]=0;break;case 22:p=indexed+y*320+93;break;case 23:VGAScreen=&alt;break;case 24:format.BitsPerPixel=32;break;}
 *p=(Uint8)((*p&240)|((*p&15)/2));bool consumed=vulcan_shadow_pixel(s,(int)(p-indexed)%320,(int)(p-indexed)/320,g==20?expected[y*320+x]:before,*p,style);assert(consumed&&reject_reason&&!strcmp(reject_reason,"vulcan-shadow-write-mismatch")&&!vulcan_shadow.live);hd=hd_save;assert(canvas_stamp()==stamp);spriteSheet8=(Sprite2_array){ns,normal};pixel_cases++;defaults();
 }
 for(unsigned k=0;k<COUNT(ids);k++){scene(94,73,1,320);assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);render_mirror_shadow_end();assert(reject_reason&&!strcmp(reject_reason,"incomplete-vulcan-shadow-command")&&!vulcan_shadow.live);pixel_cases++;}
 defaults();clear_assets();}
static void coexistence(void){
#ifdef TEN_WEAPON_SHADOW_BATCH
 const unsigned classic[]={30,34,251,255,213,218};
#else
 const unsigned classic[]={31,32,33,252,253,254,214,215,216,217};
#endif
for(unsigned j=0;j<COUNT(classic);j++)for(int under=0;under<3;under++){wrapper_case(classic[j],94,73,320,under,false,true);classic_cases++;}
 for(unsigned j=0;j<COUNT(old_ids);j++)for(int under=0;under<3;under++)for(int warm=0;warm<2;warm++){wrapper_case(old_ids[j],94,73,328,under,true,!warm);old_pin_cases++;}
 /* Existing thirteen contours retain their original mode scope. */
 for(unsigned j=0;j<13;j++)for(unsigned bits=1;bits<8;bits++){scene(94,73,1,320);flags(bits);assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,old_ids[j]));production_blit_sprite2_darken(&screen,94,73,spriteSheet8,old_ids[j]);assert(!reject_reason&&!vulcan_shadow.live);old_pin_cases++;}
 defaults();clear_assets();}
static void mid_command_modes(void){for(unsigned k=0;k<COUNT(ids);k++)for(unsigned bit=1;bit<=4;bit*=2){scene(94,73,2,320);assert(draw_vulcan_shadow(&screen,94,73,spriteSheet8,ids[k]));render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[k]);unsigned cell=0;while(!references[k][168+cell])cell++;for(unsigned step=0;step<2;step++){assert(cell<168);int x=94+(int)(cell%12),y=73+(int)(cell/12);Uint8*p=indexed+y*320+x;if(step)flags(bit);*p=(Uint8)((*p&240)|((*p&15)/2));production_render_mirror_pixel(&screen,p,0,MIRROR_SHADOW);if(!step){assert(vulcan_shadow.entered&&!reject_reason);do{cell++;}while(cell<168&&!references[k][168+cell]);}else assert(reject_reason&&!strcmp(reject_reason,"vulcan-shadow-write-mismatch")&&!vulcan_shadow.live);}pixel_cases++;}defaults();clear_assets();}
static void later_writes(void){for(unsigned k=0;k<COUNT(ids);k++)for(int under=0;under<3;under++){wrapper_case(ids[k],94,73,320,under,true,true);
 /* Execute the complete unmodified production normal blitter after the shadow,
  * then another native classic shadow. No HD-head draw stub participates. */
 for(unsigned step=0;step<2;step++){write_count=0;if(step)production_blit_sprite2_darken(&screen,94,73,spriteSheet8,ids[k]);else production_blit_sprite2(&screen,94,73,spriteSheet8,ids[k]);unsigned wi=0;
  for(unsigned cell=0;cell<168;cell++)if(references[k][168+cell]){int x=94+(int)(cell%12),y=73+(int)(cell/12);Uint8 v=references[k][cell];if(step)v=(Uint8)((v&240)|((v&15)/2));assert(indexed[y*320+x]==v&&expected[y*320+x]==v);assert(wi<write_count&&writes[wi].offset==y*320+x&&writes[wi].value==v&&writes[wi].style==(step?MIRROR_SHADOW:MIRROR_NORMAL));wi++;
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){unsigned n=(unsigned)(y*8+sy)*2560+x*8+sx;oracle[n]=palette_oracle(v);oracle_owner[n]=0;oracle_cloud[n]=0;oracle_green[n]=0;}oracle_selected[y*320+x]=0;
  }assert(wi==write_count&&!reject_reason&&!vulcan_shadow.live);check_scene(94,73);later_write_cases++;}
 }defaults();clear_assets();}
int main(int argc,char**argv){assert(argc==6);size_t ns,cs=0,rs;Uint8*normal=read_file(argv[1],&ns),*christmas=NULL;if(strcmp(argv[2],"-"))christmas=read_file(argv[2],&cs);spriteSheet8=(Sprite2_array){ns,normal};Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){1,tokens};spriteSheet12=(Sprite2_array){1,tokens+1};explosionSpriteSheet=(Sprite2_array){1,tokens+2};full_root=argv[3];Uint8*ref=read_file(argv[4],&rs);assert(rs==sizeof(references));memcpy(references,ref,rs);free(ref);
 size_t np=2560u*1600;hd.pixels=calloc(np,4);oracle=calloc(np,4);hd_owner=calloc(np,1);oracle_owner=calloc(np,1);cloud_owner=calloc(np,1);oracle_cloud=calloc(np,1);green_first=calloc(np,2);oracle_green=calloc(np,2);green_under_owner=calloc(np,1);oracle_selected=calloc(320u*200,1);assert(hd.pixels&&oracle&&hd_owner&&oracle_owner&&cloud_owner&&oracle_cloud&&green_first&&oracle_green&&green_under_owner&&oracle_selected);
 for(unsigned i=0;i<256;i++){unsigned low=i&15;rgb_palette[i]=((low*15)<<16)|((((i>>4)*11+low*7)&255)<<8)|(i%7?low*13:0);}
 defaults();gates();sources(normal,ns,christmas,cs);resource_mutations();resource_fixtures(argv[5]);begin_faults();pixel_faults();mid_command_modes();later_writes();if(!getenv("SONIC_SHADOW_FAULTS_ONLY")){geometry();coexistence();}
 clear_assets();free(normal);free(christmas);free(hd.pixels);free(oracle);free(hd_owner);free(oracle_owner);free(cloud_owner);free(oracle_cloud);free(green_first);free(oracle_green);free(green_under_owner);free(oracle_selected);
 printf("{\"status\":\"PASS\",\"genuine_production_compositor\":true,\"geometry_cases\":%u,\"indexed_cases\":%u,\"early_gate_rejections\":%u,\"source_cases\":%u,\"resource_cases\":%u,\"begin_identity_epoch_cases\":%u,\"pixel_epoch_and_mode_cases\":%u,\"later_ordered_write_cases\":%u,\"unchanged_classic_route_cases\":%u,\"previous_thirteen_positive_cases\":%u,\"rgb_samples_checked\":%llu,\"indexed_bytes_checked\":%llu,\"alpha_zero_samples\":%llu,\"alpha_full_samples\":%llu,\"alpha_partial_samples\":%llu,\"rng_preserved\":true,\"game_runs\":0}\n",geometry_cases,indexed_cases,gate_cases,source_cases,resource_cases,begin_cases,pixel_cases,later_write_cases,classic_cases,old_pin_cases,(unsigned long long)rgb_checked,(unsigned long long)indexed_checked,(unsigned long long)zero_samples,(unsigned long long)full_samples,(unsigned long long)partial_samples);return 0;}
