/* Bounded five-frame Plasma body production extraction. Never invokes the engine. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;typedef unsigned int uint;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {Uint8*data;size_t size;} Sprite2_array;
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW,ENTITY_TILE=0,ENTITY_QUAD=1};
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define COUNTOF(a) (sizeof(a)/sizeof(*(a)))
#include "types.inc"
typedef struct {int unused;} G101Record;typedef G101Record PCapRecord;typedef G101Record Forest13Record;
static bool xmas,active=true,suppress,suppress_green_smoke,suppress_cloud,game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend=true;
static int game_probe_density=8;static const char *game_probe_assets,*reject_reason;
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet10,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value;
static SDL_PixelFormat format={8,1};static SDL_Surface screen={320,200,320,NULL,&format},hd={2560,1600,2560*4,NULL,NULL},*canvas=&hd,*game_screen=&screen,*VGAScreen=&screen;
static unsigned banking_draw_player;static uint64_t mirror_logic_tick;static TalonBank talon_banks[2];
static Asset talon_frames[13];static const int original_visual_indices[5]={0,2,6,10,12};
static struct{const Uint8*rgba;char path[1024];}vulcan_shadow_resource[13],vulcan_shadow_coverage_resource[3];
static HdRegion regions[65536];static unsigned region_count,local_entities,draws,occlusions;
static Uint8 expected[320*200],selected[320*200],*hd_owner,*cloud_owner,*green_under_owner;static Uint16 *green_first;static Uint32 *green_under;
static GreenHead green_heads[256];static unsigned green_head_count;
static unsigned shadow_ends,blit_calls,pixel_calls,wrapper_calls,quad_calls;
static unsigned blit_indices[8];
static const unsigned body_ids[5]={224,243,262,281,300};
static unsigned body_index=224;
static unsigned body_slot(void){for(unsigned i=0;i<5;i++)if(body_ids[i]==body_index)return 541+i;assert(0);return 0;}
static struct{ptrdiff_t offset;Uint8 value;int style;}writes[4096];
static unsigned cases,identity_cases,variant_cases,pixel_cases,dispatch_cases,regression_cases,animation_phases;
static size_t checked_indexed_bytes,checked_rgba_bytes;
static int vulcan_shadow_member(unsigned index){(void)index;return -1;}
static void render_mirror_shadow_end(void){shadow_ends++;}
static void vulcan_shadow_clear(void){}
static bool vulcan_shadow_pixel(SDL_Surface*s,int x,int y,Uint8 b,Uint8 a,int st){(void)s;(void)x;(void)y;(void)b;(void)a;(void)st;return false;}
static bool font_pixel(int x,int y,Uint8 a,int st){(void)x;(void)y;(void)a;(void)st;return false;}
static void render_mirror_unsupported(const char*r){reject_reason=r;}
static void restore_classic_rect(SDL_Rect r){(void)r;assert(!"unexpected local blend restoration");}
static void font_before_effect(SDL_Rect r){(void)r;}
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
static void ground101_select(const G101Record*a,const Uint8*b,unsigned c,int d,int e,Uint8*f){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;assert(0);}
#define plateau_cap_select ground101_select
#define forest13_select ground101_select
static bool draw_vulcan_shadow(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;assert(0);return false;}
static bool cash25_surface_ready(SDL_Surface*s,int x,int y){(void)s;(void)x;(void)y;assert(0);return false;}
#define cash25_family_ready() false
#define cash75_family_ready() false
#define cash50_family_ready() false
#define gem100_family_ready() false
#define gem250_family_ready() false
#define game_probe_scene_draw(...) ((void)0)
#include "functions.inc"
static Uint16 SDL_SwapLE16(Uint16 v){Uint8 b[2];memcpy(b,&v,2);return(Uint16)(b[0]|b[1]<<8);}
#define asset_debug_effect(...) ((void)0)
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define load_font_arrow_sprite_end() ((void)0)
#define pregame_font_sprite2_end() ((void)0)
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style){assert(pixel_calls<COUNTOF(writes));writes[pixel_calls].offset=p-(Uint8*)s->pixels;writes[pixel_calls].value=v;writes[pixel_calls].style=style;pixel_calls++;production_render_mirror_pixel(s,p,v,style);}
#include "blitters.inc"
static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(blit_calls<COUNTOF(blit_indices));blit_indices[blit_calls++]=i;production_blit_sprite2(s,x,y,b,i);}
static void blit_sprite2x2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;quad_calls++;}
#include "wrapper.inc"
typedef struct {unsigned option,ani,pwr;unsigned gr[20];} JE_OptionType;
typedef struct {int x,y;unsigned style,charge,charge_ticks,animation_frame;bool animation_enabled;} Sidekick;
typedef struct {int x,y;bool is_alive;struct{unsigned sidekick[2];}items;Sidekick sidekick[2];} Player;
static JE_OptionType options[40];static bool twoPlayerMode,endLevel;
enum{LEFT_SIDEKICK,RIGHT_SIDEKICK};
#include "dispatch.inc"

static Uint8*read_file(const char*p,size_t*n){FILE*f=fopen(p,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long z=ftell(f);assert(z>0&&!fseek(f,0,SEEK_SET));Uint8*r=malloc((size_t)z);assert(r&&fread(r,1,(size_t)z,f)==(size_t)z&&!fclose(f));*n=(size_t)z;return r;}
static void clear_assets(void){for(size_t i=0;i<COUNTOF(assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}for(size_t i=0;i<COUNTOF(talon_frames);i++){free(talon_frames[i].rgba);memset(&talon_frames[i],0,sizeof(talon_frames[i]));}}
static void reset_scene(void){
 const size_t n=(size_t)hd.w*hd.h;Uint32*p=hd.pixels;for(size_t i=0;i<n;i++)p[i]=0xff313131;
 memset(hd_owner,0,n);memset(cloud_owner,0,n);memset(green_first,0,n*sizeof(*green_first));memset(green_under_owner,0,n);memset(selected,0,sizeof(selected));
 for(int y=0;y<200;y++)for(int x=0;x<320;x++)expected[y*320+x]=49;
 memset(screen.pixels,49,(size_t)screen.pitch*screen.h);region_count=draws=occlusions=local_entities=green_head_count=0;reject_reason=NULL;suppress=suppress_cloud=suppress_green_smoke=false;blit_calls=pixel_calls=quad_calls=0;active=true;
}
static bool head(unsigned index,unsigned option,unsigned style,unsigned charge){unsigned before=draws;bool got=render_mirror_plasma_body(&screen,94,73,spriteSheet9,index,option,style,charge);assert(draws==before+(unsigned)got);render_mirror_entity_end();cases++;return got;}
static size_t encoded_tile(Uint8*dst,size_t at,const Uint8*colors,const Uint8*mask){
 for(unsigned y=0;y<14;y++){unsigned x0=0;for(unsigned x=0;x<12;x++)if(mask[y*12+x]){dst[at++]=(Uint8)(0x10|(x-x0));dst[at++]=colors[y*12+x];x0=x+1;}dst[at++]=(Uint8)(12-x0);}dst[at++]=15;return at;
}
static void identity(Uint8*normal,size_t ns,Uint8*christmas,size_t cs,const char*full){
 game_probe_assets=full;size_t cap=MAX(ns,cs)+1024;Uint8*allocation=malloc(cap);assert(allocation);
 for(unsigned k=0;k<5;k++)for(int warm=0;warm<2;warm++){
  body_index=body_ids[k];size_t table=2*(body_index-1);clear_assets();memcpy(allocation,normal,ns);spriteSheet9=(Sprite2_array){allocation,ns};xmas=false;
  if(warm)assert(head(body_index,9,0,0));Uint8*loaded=assets[body_slot()].rgba;
  xmas=true;assert(head(body_index,9,0,0));loaded=assets[body_slot()].rgba;xmas=false;
  // The currently selected normal and Christmas bank9 frames decode identically.
  memcpy(allocation,christmas,cs);spriteSheet9.size=cs;assert(head(body_index,9,0,0)&&assets[body_slot()].rgba==loaded);
  xmas=true;assert(head(body_index,9,0,0)&&assets[body_slot()].rgba==loaded);xmas=false;
  memcpy(allocation,normal,ns);spriteSheet9.size=ns;assert(head(body_index,9,0,0));loaded=assets[body_slot()].rgba;
  size_t off=(size_t)allocation[table]|((size_t)allocation[table+1]<<8),p=off;while(!(allocation[p]>>4))p++;
  Uint8 saved=allocation[p+1];allocation[p+1]^=1;assert(!head(body_index,9,0,0));reset_scene();draw_plasma_body_sprite2(&screen,94,73,spriteSheet9,body_index,9,0,0);assert(blit_calls==1&&pixel_calls==97&&draws==0&&!suppress);wrapper_calls++;allocation[p+1]=saved;assert(head(body_index,9,0,0)&&assets[body_slot()].rgba==loaded);
  saved=allocation[p];allocation[p]=(saved&0xf0)|((saved+1)&15);assert(!head(body_index,9,0,0));allocation[p]=saved;assert(head(body_index,9,0,0));
  const size_t truncated[]={0,1,2,table,table+1,off,off+1,p+1,p+2};
  for(unsigned z=0;z<COUNTOF(truncated);z++){spriteSheet9.size=truncated[z];assert(!plasma_body_source_matches(spriteSheet9,body_index));}spriteSheet9.size=ns;
  Uint8 lo=allocation[table],hi=allocation[table+1];allocation[table]=255;allocation[table+1]=255;assert(!head(body_index,9,0,0));allocation[table]=lo;allocation[table+1]=hi;
  // Malformed streams reach only the bounded HD decoder, never raw RLE.
  Uint8*temp=malloc(ns);assert(temp);memcpy(temp,allocation,ns);memset(allocation+off,0,ns-off);assert(!head(body_index,9,0,0));memcpy(allocation,temp,ns);
  allocation[off]=0xf0;spriteSheet9.size=off+1;assert(!head(body_index,9,0,0));spriteSheet9.size=ns;memcpy(allocation,temp,ns);free(temp);
  Sprite2_array other={normal,ns};assert(!plasma_body_asset(other,body_index,9,0,0));other=spriteSheet9;other.size--;assert(!plasma_body_asset(other,body_index,9,0,0));
  other=spriteSheet9;other.data=NULL;assert(!plasma_body_asset(other,body_index,9,0,0));assert(!plasma_body_asset(spriteSheet8,body_index,9,0,0));
  for(unsigned i=0;i<=320;i++)if(i!=224&&i!=243&&i!=262&&i!=281&&i!=300)assert(!head(i,9,0,0));
  for(unsigned st=1;st<7;st++)assert(!head(body_index,9,st,0));for(unsigned op=0;op<40;op++)if(op!=9)assert(!head(body_index,op,0,0));
  assert(!head(body_index,9,0,1));assert(!head(body_index,9,0,20));
  for(int d=0;d<=16;d++){if(d==4||d==8)continue;game_probe_density=d;assert(!head(body_index,9,0,0));}game_probe_density=8;
  assert(get_asset(spriteSheet9,body_index,ENTITY_TILE)==NULL&&get_asset(spriteSheet9,body_index,ENTITY_QUAD)==NULL);
  for(int st=0;st<3;st++)for(int la=0;la<2;la++)assert(!render_mirror_entity(&screen,94,73,spriteSheet9,body_index,st,la));
  assert(head(body_index,9,0,0));
  // Same-address reallocation and another valid RLE encoding bind by semantics.
  Uint8 colors[168]={0},mask[168]={0};assert(decode_tile(spriteSheet9,body_index,colors,mask,12,0,0));
  size_t end=encoded_tile(allocation,ns,colors,mask);allocation[table]=(Uint8)ns;allocation[table+1]=(Uint8)(ns>>8);spriteSheet9.size=end;assert(head(body_index,9,0,0)&&assets[body_slot()].rgba==loaded);
  // A valid coverage-only mutation adds an index0 at one empty source cell.
  unsigned empty=0;while(empty<168&&(mask[empty]||colors[empty]))empty++;assert(empty<168);mask[empty]=255;end=encoded_tile(allocation,ns,colors,mask);spriteSheet9.size=end;
  Uint8 altered[168]={0},altered_mask[168]={0};assert(decode_tile(spriteSheet9,body_index,altered,altered_mask,12,0,0));assert(!memcmp(altered,colors,168)&&altered_mask[empty]==255);assert(!head(body_index,9,0,0));
  memcpy(allocation,normal,ns);spriteSheet9.size=ns;assert(head(body_index,9,0,0));
  // Authorized frames may not borrow another frame's identity.
  for(unsigned j=0;j<5;j++)if(j!=k){size_t t=2*(body_ids[j]-1);allocation[table]=allocation[t];allocation[table+1]=allocation[t+1];assert(!head(body_index,9,0,0));allocation[table]=lo;allocation[table+1]=hi;}
  // Invalid current source is rejected before both cold and warm cache reads.
  saved=allocation[p+1];allocation[p+1]^=1;if(!warm)clear_assets();assert(!head(body_index,9,0,0));allocation[p+1]=saved;assert(head(body_index,9,0,0));
  identity_cases++;
 }
 // Explicit cold loads using each selected bank and normal/Christmas flag.
 for(unsigned k=0;k<5;k++)for(unsigned variant=0;variant<4;variant++){clear_assets();body_index=body_ids[k];bool christmas_bank=(variant&1)!=0;xmas=(variant&2)!=0;memcpy(allocation,christmas_bank?christmas:normal,christmas_bank?cs:ns);spriteSheet9=(Sprite2_array){allocation,christmas_bank?cs:ns};assert(head(body_index,9,0,0));identity_cases++;}
 xmas=false;clear_assets();free(allocation);spriteSheet9=(Sprite2_array){normal,ns};body_index=224;
}
static Uint32 reference_blend(Uint32 dst,const Uint8*s,unsigned a){unsigned r=(((dst>>16)&255)*(255-a)+s[0]*a+127)/255,g=(((dst>>8)&255)*(255-a)+s[1]*a+127)/255,b=((dst&255)*(255-a)+s[2]*a+127)/255;return 0xff000000|r<<16|g<<8|b;}
/* Independent row-major source oracle, also checking raw write order and values. */
static unsigned oracle_indexed(Uint8*dst,Sprite2_array bank,unsigned index,int x,int y,int pitch,bool trace){Uint8 c[168]={0},m[168]={0};assert(decode_tile(bank,index,c,m,12,0,0));unsigned count=0;for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(m[yy*12+xx]){int p=(y+yy)*pitch+x+xx;if(p>=pitch*200)return count;if(p>=0){dst[p]=c[yy*12+xx];if(trace){assert(count<pixel_calls&&writes[count].offset==p&&writes[count].value==c[yy*12+xx]&&writes[count].style==MIRROR_NORMAL);}count++;}}return count;}
static void oracle_asset(Uint32*dst,Asset*a,int x,int y,bool half){int d=game_probe_density,ad=a->density;for(int yy=0;yy<a->h*d;yy++)for(int xx=0;xx<a->w*d;xx++){int dx=x*d+xx,dy=y*d+yy;if(dx<0||dy<0||dx>=hd.w||dy>=hd.h)continue;const Uint8*s=a->rgba+4*((yy*ad/d)*a->w*ad+xx*ad/d);if(s[3])dst[dy*hd.w+dx]=reference_blend(dst[dy*hd.w+dx],s,half?(s[3]+1)/2:s[3]);}}
static void oracle_rgba(Uint32*dst,Asset*a,int x,int y){oracle_asset(dst,a,x,y,false);}
static void oracle_classic(Uint32*dst,Uint8*indexed){int d=game_probe_density;for(unsigned i=0;i<pixel_calls;i++){int y=(int)(writes[i].offset/screen.pitch),x=(int)(writes[i].offset%screen.pitch);if(x>=320||y>=200)continue;Uint8 v=indexed[writes[i].offset];for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)dst[(y*d+sy)*hd.w+x*d+sx]=0xff000000|v*0x010101u;}}
static void wrapped_case(int x,int y,bool accepted,Uint8*oracle,Uint32*rgba){
 size_t n=(size_t)screen.pitch*200,hn=(size_t)hd.w*hd.h;memcpy(oracle,screen.pixels,n);memcpy(rgba,hd.pixels,hn*4);unsigned bd=draws;blit_calls=pixel_calls=0;draw_plasma_body_sprite2(&screen,x,y,spriteSheet9,body_index,9,0,0);wrapper_calls++;
 assert(blit_calls==1&&draws==bd+(unsigned)accepted&&!suppress&&!suppress_cloud&&!suppress_green_smoke);unsigned count=oracle_indexed(oracle,spriteSheet9,body_index,x,y,screen.pitch,true);assert(count==pixel_calls);if(x==97&&y==73)assert(count==97);
 if(accepted)oracle_rgba(rgba,&assets[body_slot()],x,y);else oracle_classic(rgba,oracle);
 assert(!memcmp(oracle,screen.pixels,n));assert(!memcmp(rgba,hd.pixels,hn*4));checked_indexed_bytes+=n;checked_rgba_bytes+=hn*4;pixel_cases++;
}
static void resources_and_pixels(const char*root){char line[2048],name[128];int accepted,density;snprintf(line,sizeof(line),"%s/variants.tsv",root);FILE*f=fopen(line,"r");assert(f);Uint8*oracle=malloc(328*200);Uint32*rgba=malloc((size_t)hd.w*hd.h*4);assert(oracle&&rgba);
 while(fscanf(f,"%127s %d %d",name,&accepted,&density)==3){for(unsigned k=0;k<5;k++){body_index=body_ids[k];char path[2048];snprintf(path,sizeof(path),"%s/%s",root,name);game_probe_assets=path;clear_assets();reset_scene();wrapped_case(94,73,accepted,oracle,rgba);if(accepted)assert(assets[body_slot()].density==density&&assets[body_slot()].bank==129&&assets[body_slot()].index==(int)body_index&&assets[body_slot()].anchor_x==0&&assets[body_slot()].anchor_y==0);wrapped_case(94,73,accepted,oracle,rgba);variant_cases++;}}
 fclose(f);
 // Each frame has an independent 8x->4x->indexed fallback and cache slot.
 char mixed[2048];snprintf(mixed,sizeof(mixed),"%s/mixed",root);game_probe_assets=mixed;clear_assets();
 const bool mixed_accept[5]={true,false,true,true,false};const int mixed_density[5]={8,0,4,4,0};
 for(unsigned repeat=0;repeat<2;repeat++)for(unsigned k=0;k<5;k++){body_index=body_ids[k];reset_scene();wrapped_case(94,73,mixed_accept[k],oracle,rgba);if(mixed_accept[k])assert(assets[body_slot()].density==mixed_density[k]);variant_cases++;}
 char full[2048];snprintf(full,sizeof(full),"%s/valid",root);game_probe_assets=full;clear_assets();
 const int xy[][2]={{94,73},{0,0},{308,0},{0,-13},{308,-1},{94,187},{0,199},{308,199},{-3,73},{315,73},{94,-14},{94,200},{94,73},{97,75}};
 for(unsigned k=0;k<5;k++){body_index=body_ids[k];for(int pitch=320;pitch<=328;pitch+=8){screen.pitch=pitch;for(unsigned j=0;j<COUNTOF(xy);j++){reset_scene();int x=xy[j][0],y=xy[j][1];bool ok=x>=0&&x<=308&&y>=-13&&y<=199;wrapped_case(x,y,ok,oracle,rgba);wrapped_case(x,y,ok,oracle,rgba);}reset_scene();wrapped_case(94,73,true,oracle,rgba);wrapped_case(97,75,true,oracle,rgba);wrapped_case(94,73,true,oracle,rgba);}
 }screen.pitch=320;reset_scene();
 // Different pulse resources preserve command order at identical/overlapping sites.
 for(unsigned j=0;j<6;j++){body_index=body_ids[j%5];wrapped_case(j%2?97:94,j%2?75:73,true,oracle,rgba);}body_index=224;
 // No source/body lease escapes into an unrelated direct indexed write.
 reset_scene();wrapped_case(94,73,true,oracle,rgba);unsigned old=draws;blit_calls=pixel_calls=0;blit_sprite2(&screen,94,73,spriteSheet9,body_index);assert(blit_calls==1&&pixel_calls==97&&draws==old&&!suppress);
 // Surface/context diagnostics fail closed before cache, preserving wrapper call.
 SDL_Surface alt=screen;assert(!render_mirror_plasma_body(&alt,94,73,spriteSheet9,body_index,9,0,0));
 assert(!render_mirror_plasma_body(NULL,94,73,spriteSheet9,body_index,9,0,0));
 int saved=screen.w;screen.w=319;assert(!head(body_index,9,0,0));screen.w=saved;saved=screen.h;screen.h=199;assert(!head(body_index,9,0,0));screen.h=saved;saved=screen.pitch;screen.pitch=319;assert(!head(body_index,9,0,0));screen.pitch=saved;
 format.BitsPerPixel=32;assert(!head(body_index,9,0,0));format.BitsPerPixel=8;format.BytesPerPixel=4;assert(!head(body_index,9,0,0));format.BytesPerPixel=1;screen.format=NULL;assert(!head(body_index,9,0,0));screen.format=&format;VGAScreen=&alt;assert(!head(body_index,9,0,0));VGAScreen=&screen;
 void*saved_pixels=screen.pixels;screen.pixels=NULL;assert(!head(body_index,9,0,0));screen.pixels=saved_pixels;active=false;assert(!head(body_index,9,0,0));active=true;reject_reason="test";assert(!head(body_index,9,0,0));reject_reason=NULL;game_probe_missing=true;assert(!head(body_index,9,0,0));game_probe_missing=false;game_probe_invalid=true;assert(!head(body_index,9,0,0));game_probe_invalid=false;game_probe_original_reference=true;assert(!head(body_index,9,0,0));game_probe_original_reference=false;
 // A direct 4x mode loads 4x authored fallback without any undefined density.
 char four[2048];snprintf(four,sizeof(four),"%s/only4",root);game_probe_assets=four;clear_assets();game_probe_density=4;hd.w=1280;hd.h=800;hd.pitch=5120;for(unsigned k=0;k<5;k++){body_index=body_ids[k];reset_scene();wrapped_case(94,73,true,oracle,rgba);assert(assets[body_slot()].density==4);}body_index=224;clear_assets();game_probe_density=8;hd.w=2560;hd.h=1600;hd.pitch=10240;
 clear_assets();free(oracle);free(rgba);
}
static void regression(const char*full){game_probe_assets=full;reset_scene();clear_assets();assert(talon_frames_ready());Uint32*pose_oracle=malloc((size_t)hd.w*hd.h*4);assert(pose_oracle);for(unsigned i=0;i<13;i++){Asset*a=talon_frame(i);assert(a&&a->anchor_x==5&&a->anchor_y==7);banking_draw_player=1;talon_banks[0].valid=true;talon_banks[0].last_tick=mirror_logic_tick;talon_banks[0].logical_index=233;talon_banks[0].visual_index=(int)i;memcpy(pose_oracle,hd.pixels,(size_t)hd.w*hd.h*4);oracle_asset(pose_oracle,a,130,90,false);assert(render_mirror_entity(&screen,130,90,spriteSheet9,233,MIRROR_NORMAL,ENTITY_QUAD));render_mirror_entity_end();assert(!memcmp(pose_oracle,hd.pixels,(size_t)hd.w*hd.h*4));oracle_asset(pose_oracle,a,130,90,true);assert(render_mirror_entity(&screen,130,90,spriteSheet9,233,MIRROR_BLEND,ENTITY_QUAD));render_mirror_entity_end();assert(!memcmp(pose_oracle,hd.pixels,(size_t)hd.w*hd.h*4));checked_rgba_bytes+=(size_t)hd.w*hd.h*8;banking_draw_player=0;regression_cases+=2;}
 assert(get_asset(spriteSheet8,27,ENTITY_TILE));assert(!render_mirror_entity(&screen,80,90,spriteSheet8,27,MIRROR_SHADOW,ENTITY_TILE));assert(get_asset(spriteSheet8,67,ENTITY_TILE)&&get_asset(spriteSheet8,70,ENTITY_TILE));regression_cases+=4;
 // Existing Marlo slot and ordered Talon/body overlap retain original compositing.
 assert(marlo152_asset(spriteSheet9,152,30,4,0)==&assets[536]);assert(assets[536].bank==126);unsigned mb=blit_calls;draw_sidekick_body_sprite2(&screen,94,73,spriteSheet9,152,30,4,0);assert(blit_calls==mb+1&&!suppress);regression_cases++;
 Asset*talon=get_asset(spriteSheet9,233,ENTITY_QUAD);assert(talon);reset_scene();assert(draw_asset(90,70,talon,MIRROR_NORMAL,NULL));render_mirror_entity_end();Uint32*oracle=malloc((size_t)hd.w*hd.h*4);Uint8*indices=malloc(328*200);assert(oracle&&indices);wrapped_case(94,73,true,indices,oracle);memcpy(oracle,hd.pixels,(size_t)hd.w*hd.h*4);oracle_asset(oracle,talon,94,73,true);assert(draw_asset(94,73,talon,MIRROR_BLEND,NULL));render_mirror_entity_end();assert(!suppress&&!memcmp(oracle,hd.pixels,(size_t)hd.w*hd.h*4));checked_rgba_bytes+=(size_t)hd.w*hd.h*4;free(pose_oracle);free(oracle);free(indices);clear_assets();}
static void dispatch(const char*full){
 game_probe_assets=full;options[0]=(JE_OptionType){0};options[9]=(JE_OptionType){.option=1,.ani=20,.pwr=0,.gr={224,224,224,224,243,243,243,243,262,262,262,262,281,281,281,281,300,300,300,300}};
 options[30]=(JE_OptionType){.option=1,.ani=1,.pwr=0,.gr={152}};options[10]=(JE_OptionType){.option=1,.ani=1,.pwr=0,.gr={224}};
 Uint8 after[328*200];const unsigned phase[20]={224,224,224,243,243,243,243,262,262,262,262,281,281,281,281,300,300,300,300,224};
 for(unsigned mode=0;mode<3;mode++)for(unsigned flags=0;flags<16;flags++)for(unsigned enabled=0;enabled<2;enabled++){
  Player a={.x=160,.y=100,.is_alive=(flags&1)!=0,.items={{mode==1?0:9,mode==0?0:9}},.sidekick={{94,73,0,0,1,0,enabled!=0},{103,79,0,0,20,0,enabled!=0}}},b=a;
  twoPlayerMode=(flags&2)!=0;endLevel=(flags&4)!=0;unsigned pnum=(flags&8)?2:1;reset_scene();
  for(unsigned tick=0;tick<40;tick++){
   memset(screen.pixels,49,64000);blit_calls=pixel_calls=0;baseline_dispatch(&a,pnum);memcpy(after,screen.pixels,64000);unsigned bc=blit_calls;unsigned seq[8];memcpy(seq,blit_indices,sizeof(seq));
   memset(screen.pixels,49,64000);blit_calls=pixel_calls=0;unsigned before=draws;candidate_dispatch(&b,pnum);
   assert(!memcmp(&a,&b,sizeof(a))&&!memcmp(after,screen.pixels,64000)&&blit_calls==bc&&!suppress);assert(!memcmp(seq,blit_indices,bc*sizeof(*seq)));
   if((pnum==2||!twoPlayerMode)&&!endLevel){assert(draws==before+bc);assert(bc==(mode==2?2u:1u));for(unsigned j=0;j<bc;j++)assert(seq[j]==(enabled?phase[tick%20]:224));assert(pixel_calls==bc*97);animation_phases++;}
   else assert(draws==before&&bc==0);dispatch_cases++;
  }
 }
 // Other options and nonzero styles keep their published raw paths.
 twoPlayerMode=endLevel=false;
 for(unsigned st=0;st<=4;st++){
  Player a={.items={{10,0}},.sidekick={{94,73,st,0,1,0,true},{0}}},b=a;reset_scene();baseline_dispatch(&a,1);memcpy(after,screen.pixels,64000);unsigned bc=blit_calls,qc=quad_calls;reset_scene();candidate_dispatch(&b,1);assert(!memcmp(&a,&b,sizeof(a))&&!memcmp(after,screen.pixels,64000)&&blit_calls==bc&&quad_calls==qc&&draws==0);dispatch_cases++;
 }
 Player a={.items={{30,0}},.sidekick={{94,73,4,0,1,0,true},{0}}},b=a;reset_scene();baseline_dispatch(&a,1);memcpy(after,screen.pixels,64000);reset_scene();candidate_dispatch(&b,1);assert(!memcmp(&a,&b,sizeof(a))&&!memcmp(after,screen.pixels,64000)&&draws==1&&blit_indices[0]==152);dispatch_cases++;
 for(unsigned charge=0;charge<2;charge++)for(unsigned st=0;st<5;st++){if(!charge&&!st)continue;Player p={.items={{9,0}},.sidekick={{94,73,st,charge,20,0,true},{0}}};reset_scene();candidate_dispatch(&p,1);assert(draws==0);dispatch_cases++;}
 clear_assets();body_index=224;
}
int main(int argc,char**argv){assert(argc==5);size_t ns,cs,bs;Uint8*normal=read_file(argv[1],&ns),*christmas=read_file(argv[2],&cs),*bullets=read_file(argv[3],&bs);spriteSheet9=(Sprite2_array){normal,ns};spriteSheet8=(Sprite2_array){bullets,bs};Uint8 token[3]={0};spriteSheet10=(Sprite2_array){token,1};spriteSheet12=(Sprite2_array){token+1,1};explosionSpriteSheet=(Sprite2_array){token+2,1};screen.pixels=malloc(328*200);size_t hn=(size_t)hd.w*hd.h;hd.pixels=malloc(hn*4);hd_owner=calloc(hn,1);cloud_owner=calloc(hn,1);green_first=calloc(hn,sizeof(*green_first));green_under=calloc(hn,4);green_under_owner=calloc(hn,1);assert(screen.pixels&&hd.pixels&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);for(unsigned i=0;i<256;i++)rgb_palette[i]=i*0x010101u;reset_scene();char full[2048];snprintf(full,sizeof(full),"%s/valid",argv[4]);
 for(unsigned k=0;k<5;k++){Uint8 c[168]={0},m[168]={0};assert(decode_tile(spriteSheet9,body_ids[k],c,m,12,0,0));unsigned support=0;for(unsigned i=0;i<168;i++)support+=!!m[i];assert(support==97);}identity(normal,ns,christmas,cs,full);resources_and_pixels(argv[4]);regression(full);dispatch(full);
 clear_assets();free(normal);free(christmas);free(bullets);free(screen.pixels);free(hd.pixels);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 printf("{\"status\":\"PASS\",\"head_cases\":%u,\"source_identity_cases\":%u,\"resource_variants\":%u,\"wrapper_calls\":%u,\"pixel_cases\":%u,\"dispatch_cases\":%u,\"regression_cases\":%u,\"verified_animation_phases\":%u,\"indexed_bytes_compared\":%zu,\"rgba_bytes_compared\":%zu,\"source_body_writes\":97,\"game_runs\":0}\n",cases,identity_cases,variant_cases,wrapper_calls,pixel_cases,dispatch_cases,regression_cases,animation_phases,checked_indexed_bytes,checked_rgba_bytes);return 0;}
