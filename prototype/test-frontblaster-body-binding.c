/* Bounded FrontBlaster option20 QUAD body production extraction. Never invokes the engine. */
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
static unsigned blit_indices[16];
static int blit_x[16],blit_y[16];
static const unsigned quad_ids[4]={83,84,102,103};
static const int quad_dx[4]={0,12,0,12},quad_dy[4]={0,0,14,14};
static unsigned body_slot(void){return 540;}
static struct{ptrdiff_t offset;Uint8 value;int style;}writes[4096];
static unsigned cases,identity_cases,variant_cases,pixel_cases,dispatch_cases,scope_cases,coverage_cases,malformed_cases;
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
static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){assert(blit_calls<COUNTOF(blit_indices));blit_indices[blit_calls]=i;blit_x[blit_calls]=x;blit_y[blit_calls++]=y;production_blit_sprite2(s,x,y,b,i);}
#include "quad.inc"
static void blit_sprite2x2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){quad_calls++;production_blit_sprite2x2(s,x,y,b,i);}
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
static bool head(unsigned index,unsigned option,unsigned style,unsigned charge){unsigned before=draws;bool got=render_mirror_frontblaster_body(&screen,94,73,spriteSheet10,index,option,style,charge);assert(draws==before+(unsigned)got);render_mirror_entity_end();cases++;return got;}
static bool quad_decode(Sprite2_array b,Uint8*c,Uint8*m){memset(c,0,24*28);memset(m,0,24*28);for(unsigned k=0;k<4;k++)if(!decode_tile(b,quad_ids[k],c,m,24,quad_dx[k],quad_dy[k]))return false;return true;}
static size_t encoded_tile(Uint8*dst,size_t at,const Uint8*colors,const Uint8*mask){
 for(unsigned y=0;y<14;y++){unsigned x0=0;for(unsigned x=0;x<12;x++)if(mask[y*12+x]){dst[at++]=(Uint8)(0x10|(x-x0));dst[at++]=colors[y*12+x];x0=x+1;}dst[at++]=(Uint8)(12-x0);}dst[at++]=15;return at;
}
/* Private data enters only through argv files. No source pixels are embedded. */
static void identity(Uint8*normal,size_t ns,Uint8*christmas,size_t cs,const char*full){
 game_probe_assets=full;size_t cap=MAX(ns,cs)+4096;Uint8*allocation=malloc(cap);assert(allocation&&ns<65536&&cs<65536);
 Uint8 original[24*28],original_mask[24*28],holiday[24*28],holiday_mask[24*28];
 assert(quad_decode((Sprite2_array){normal,ns},original,original_mask)&&quad_decode((Sprite2_array){christmas,cs},holiday,holiday_mask));assert(!memcmp(original,holiday,sizeof(original))&&!memcmp(original_mask,holiday_mask,sizeof(original_mask)));
 for(int warm=0;warm<2;warm++){
  clear_assets();memcpy(allocation,normal,ns);spriteSheet10=(Sprite2_array){allocation,ns};xmas=false;
  if(warm)assert(head(83,20,2,0));
  Uint8*loaded=assets[540].rgba;
  /* Normal and Christmas have equal current quad semantics, including reloads
   * at the same address. The scene flag itself is not a blanket exclusion. */
  for(int flag=0;flag<2;flag++){
   xmas=flag;memcpy(allocation,flag?christmas:normal,flag?cs:ns);spriteSheet10.size=flag?cs:ns;if(!warm){clear_assets();loaded=NULL;}assert(head(83,20,2,0));if(loaded)assert(assets[540].rgba==loaded);loaded=assets[540].rgba;
   memcpy(allocation,christmas,cs);spriteSheet10.size=cs;assert(head(83,20,2,0)&&assets[540].rgba==loaded);
   memcpy(allocation,normal,ns);spriteSheet10.size=ns;assert(head(83,20,2,0)&&assets[540].rgba==loaded);
  }
  xmas=false;identity_cases++;
 }
 /* Every source quadrant is checked on every cold and warm cache lookup. */
 for(unsigned k=0;k<4;k++)for(int warm=0;warm<2;warm++){
  clear_assets();memcpy(allocation,normal,ns);spriteSheet10=(Sprite2_array){allocation,ns};xmas=false;
  if(warm)assert(head(83,20,2,0));Uint8*loaded=assets[540].rgba;
  size_t table=2*(quad_ids[k]-1),off=(size_t)allocation[table]|((size_t)allocation[table+1]<<8),p=off;
  while(!(allocation[p]>>4))p++;
  Uint8 saved=allocation[p+1];allocation[p+1]^=1;
  assert(!head(83,20,2,0)&&assets[540].rgba==loaded&&assets[540].initialized==(warm!=0));xmas=true;assert(!head(83,20,2,0)&&assets[540].rgba==loaded);xmas=false;
  allocation[p+1]=saved;assert(head(83,20,2,0));loaded=assets[540].rgba;
  saved=allocation[p];allocation[p]=(saved&0xf0)|((saved+1)&15);assert(!head(83,20,2,0)&&assets[540].rgba==loaded);allocation[p]=saved;assert(head(83,20,2,0));
  const size_t truncated[]={0,1,2,table,table+1,off,off+1,p+1};
  for(unsigned z=0;z<COUNTOF(truncated);z++){spriteSheet10.size=truncated[z];assert(!frontblaster_body_source_matches(spriteSheet10));malformed_cases++;}spriteSheet10.size=ns;
  Uint8 lo=allocation[table],hi=allocation[table+1];allocation[table]=255;allocation[table+1]=255;assert(!head(83,20,2,0));allocation[table]=lo;allocation[table+1]=hi;malformed_cases++;
  /* Malformed streams go only to the bounded HD guard, never raw RLE. */
  Uint8*temp=malloc(ns);assert(temp);memcpy(temp,allocation,ns);memset(allocation+off,0,ns-off);assert(!head(83,20,2,0));memcpy(allocation,temp,ns);malformed_cases++;
  allocation[off]=0xf0;spriteSheet10.size=off+1;assert(!head(83,20,2,0));spriteSheet10.size=ns;memcpy(allocation,temp,ns);free(temp);malformed_cases++;
  /* A semantically equivalent RLE encoding remains eligible. */
  Uint8 c[168]={0},m[168]={0};assert(decode_tile(spriteSheet10,quad_ids[k],c,m,12,0,0));size_t end=encoded_tile(allocation,ns,c,m);assert(end<cap);
  allocation[table]=(Uint8)ns;allocation[table+1]=(Uint8)(ns>>8);spriteSheet10.size=end;assert(head(83,20,2,0)&&assets[540].rgba==loaded);
  /* Coverage-only mutation adds index0 at an uncovered, zero-color cell.
   * Indices remain byte-identical; independently decoded mask must change. */
  unsigned empty=0;while(empty<168&&(c[empty]||m[empty]))empty++;assert(empty<168);m[empty]=255;end=encoded_tile(allocation,ns,c,m);spriteSheet10.size=end;
  Uint8 altered[24*28],altered_mask[24*28];assert(quad_decode(spriteSheet10,altered,altered_mask));assert(!memcmp(original,altered,sizeof(original))&&memcmp(original_mask,altered_mask,sizeof(original_mask)));
  if(!warm){clear_assets();loaded=NULL;}assert(!head(83,20,2,0)&&assets[540].rgba==loaded&&assets[540].initialized==(warm!=0));xmas=true;assert(!head(83,20,2,0)&&assets[540].rgba==loaded);xmas=false;coverage_cases++;
  memcpy(allocation,normal,ns);spriteSheet10.size=ns;assert(head(83,20,2,0));identity_cases++;
 }
 /* Scope must fail before asset initialization, both cold and warm. */
 for(int warm=0;warm<2;warm++){
  clear_assets();memcpy(allocation,normal,ns);spriteSheet10=(Sprite2_array){allocation,ns};if(warm)assert(head(83,20,2,0));Uint8*loaded=assets[540].rgba;
  Sprite2_array other={normal,ns};assert(!frontblaster_body_asset(other,83,20,2,0));other=spriteSheet10;other.size--;assert(!frontblaster_body_asset(other,83,20,2,0));other.data=NULL;assert(!frontblaster_body_asset(other,83,20,2,0));assert(!frontblaster_body_asset(spriteSheet8,83,20,2,0));assert(!frontblaster_body_asset(spriteSheet9,83,20,2,0));
  for(unsigned i=0;i<300;i++)if(i!=83){assert(!head(i,20,2,0));scope_cases++;}
  for(unsigned st=0;st<8;st++)if(st!=2){assert(!head(83,20,st,0));scope_cases++;}
  for(unsigned op=0;op<40;op++)if(op!=20){assert(!head(83,op,2,0));scope_cases++;}
  for(unsigned ch=1;ch<8;ch++){assert(!head(83,20,2,ch));scope_cases++;}
  for(int d=0;d<=16;d++){if(d==4||d==8)continue;game_probe_density=d;assert(!head(83,20,2,0));scope_cases++;}game_probe_density=8;
  assert(assets[540].rgba==loaded&&assets[540].initialized==(warm!=0));
  assert(get_asset(spriteSheet10,83,ENTITY_TILE)==NULL&&get_asset(spriteSheet10,83,ENTITY_QUAD)==NULL);
  for(int st=0;st<3;st++)for(int la=0;la<2;la++)assert(!render_mirror_entity(&screen,94,73,spriteSheet10,83,st,la));
  assert(head(83,20,2,0));identity_cases++;
 }
 clear_assets();free(allocation);spriteSheet10=(Sprite2_array){normal,ns};xmas=false;
}
static Uint32 reference_blend(Uint32 dst,const Uint8*s,unsigned a){unsigned r=(((dst>>16)&255)*(255-a)+s[0]*a+127)/255,g=(((dst>>8)&255)*(255-a)+s[1]*a+127)/255,b=((dst&255)*(255-a)+s[2]*a+127)/255;return 0xff000000|r<<16|g<<8|b;}
/* Independent per-tile row-major oracle, including physical row wrapping,
 * original four-tile order, and every raw write address/value/style. */
static unsigned oracle_indexed(Uint8*dst,Sprite2_array bank,unsigned index,int x,int y,int pitch,unsigned count,bool trace){Uint8 c[168]={0},m[168]={0};assert(decode_tile(bank,index,c,m,12,0,0));for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(m[yy*12+xx]){int p=(y+yy)*pitch+x+xx;if(p>=pitch*200)return count;if(p>=0){dst[p]=c[yy*12+xx];if(trace){assert(count<pixel_calls&&writes[count].offset==p&&writes[count].value==c[yy*12+xx]&&writes[count].style==MIRROR_NORMAL);}count++;}}return count;}
static void oracle_asset(Uint32*dst,Asset*a,int x,int y){int d=game_probe_density,ad=a->density;for(int yy=0;yy<a->h*d;yy++)for(int xx=0;xx<a->w*d;xx++){int dx=x*d+xx,dy=y*d+yy;if(dx<0||dy<0||dx>=hd.w||dy>=hd.h)continue;const Uint8*s=a->rgba+4*((yy*ad/d)*a->w*ad+xx*ad/d);if(s[3])dst[dy*hd.w+dx]=reference_blend(dst[dy*hd.w+dx],s,s[3]);}}
static void oracle_classic(Uint32*dst,Uint8*indexed){int d=game_probe_density;for(unsigned i=0;i<pixel_calls;i++){int y=(int)(writes[i].offset/screen.pitch),x=(int)(writes[i].offset%screen.pitch);if(x>=320||y>=200)continue;Uint8 v=indexed[writes[i].offset];for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)dst[(y*d+sy)*hd.w+x*d+sx]=0xff000000|v*0x010101u;}}
static void wrapped_case(int x,int y,bool accepted,Uint8*oracle,Uint32*rgba){
 size_t n=(size_t)screen.pitch*200,hn=(size_t)hd.w*hd.h;memcpy(oracle,screen.pixels,n);memcpy(rgba,hd.pixels,hn*4);unsigned bd=draws;blit_calls=pixel_calls=quad_calls=0;draw_frontblaster_body_sprite2(&screen,x,y,spriteSheet10,83,20,2,0);wrapper_calls++;
 assert(quad_calls==1&&blit_calls==4&&draws==bd+(unsigned)accepted&&!suppress&&!suppress_cloud&&!suppress_green_smoke);
 unsigned count=0;for(unsigned k=0;k<4;k++){assert(blit_indices[k]==quad_ids[k]&&blit_x[k]==x+quad_dx[k]&&blit_y[k]==y+quad_dy[k]);count=oracle_indexed(oracle,spriteSheet10,quad_ids[k],x+quad_dx[k],y+quad_dy[k],screen.pitch,count,true);}assert(count==pixel_calls);if(x==94&&y==73)assert(count==282);
 if(accepted)oracle_asset(rgba,&assets[540],x,y);else oracle_classic(rgba,oracle);
 assert(!memcmp(oracle,screen.pixels,n));assert(!memcmp(rgba,hd.pixels,hn*4));checked_indexed_bytes+=n;checked_rgba_bytes+=hn*4;pixel_cases++;
}
static void resources_and_pixels(const char*root){char line[2048],name[128];int accepted,density;snprintf(line,sizeof(line),"%s/variants.tsv",root);FILE*f=fopen(line,"r");assert(f);Uint8*oracle=malloc(328*200);Uint32*rgba=malloc((size_t)hd.w*hd.h*4);assert(oracle&&rgba);
 while(fscanf(f,"%127s %d %d",name,&accepted,&density)==3){char path[2048];snprintf(path,sizeof(path),"%s/%s",root,name);game_probe_assets=path;clear_assets();reset_scene();wrapped_case(94,73,accepted,oracle,rgba);if(accepted)assert(assets[540].density==density&&assets[540].bank==128&&assets[540].index==83&&assets[540].w==24&&assets[540].h==28&&assets[540].anchor_x==0&&assets[540].anchor_y==0);wrapped_case(94,73,accepted,oracle,rgba);variant_cases++;}
 fclose(f);char full[2048];snprintf(full,sizeof(full),"%s/valid",root);game_probe_assets=full;clear_assets();
 const int xy[][2]={{94,73},{0,0},{296,0},{0,-27},{296,-1},{94,173},{0,199},{296,199},{-3,73},{297,73},{315,73},{94,-28},{94,200},{94,73},{97,75}};
 for(int holiday=0;holiday<2;holiday++){xmas=holiday;for(int pitch=320;pitch<=328;pitch+=8){screen.pitch=pitch;for(unsigned j=0;j<COUNTOF(xy);j++){reset_scene();int x=xy[j][0],y=xy[j][1];bool ok=x>=0&&x<=296&&y>=-27&&y<=199;wrapped_case(x,y,ok,oracle,rgba);wrapped_case(x,y,ok,oracle,rgba);}reset_scene();wrapped_case(94,73,true,oracle,rgba);wrapped_case(97,75,true,oracle,rgba);wrapped_case(94,73,true,oracle,rgba);}}
 xmas=false;screen.pitch=320;reset_scene();
 /* No dedicated body lease escapes into unrelated raw indexed writes. */
 wrapped_case(94,73,true,oracle,rgba);unsigned old=draws;blit_calls=pixel_calls=quad_calls=0;blit_sprite2x2(&screen,94,73,spriteSheet10,83);assert(quad_calls==1&&blit_calls==4&&pixel_calls==282&&draws==old&&!suppress);
 void*saved_pixels=screen.pixels;screen.pixels=NULL;assert(!head(83,20,2,0));screen.pixels=saved_pixels;
 SDL_Surface alt=screen;assert(!render_mirror_frontblaster_body(&alt,94,73,spriteSheet10,83,20,2,0));assert(!render_mirror_frontblaster_body(NULL,94,73,spriteSheet10,83,20,2,0));
 int saved=screen.w;screen.w=319;assert(!head(83,20,2,0));screen.w=saved;saved=screen.h;screen.h=199;assert(!head(83,20,2,0));screen.h=saved;saved=screen.pitch;screen.pitch=319;assert(!head(83,20,2,0));screen.pitch=saved;
 format.BitsPerPixel=32;assert(!head(83,20,2,0));format.BitsPerPixel=8;format.BytesPerPixel=4;assert(!head(83,20,2,0));format.BytesPerPixel=1;screen.format=NULL;assert(!head(83,20,2,0));screen.format=&format;VGAScreen=&alt;assert(!head(83,20,2,0));VGAScreen=&screen;
 active=false;assert(!head(83,20,2,0));active=true;reject_reason="test";assert(!head(83,20,2,0));reject_reason=NULL;game_probe_missing=true;assert(!head(83,20,2,0));game_probe_missing=false;game_probe_invalid=true;assert(!head(83,20,2,0));game_probe_invalid=false;game_probe_original_reference=true;assert(!head(83,20,2,0));game_probe_original_reference=false;
 char four[2048];snprintf(four,sizeof(four),"%s/only4",root);game_probe_assets=four;clear_assets();game_probe_density=4;hd.w=1280;hd.h=800;hd.pitch=5120;reset_scene();wrapped_case(94,73,true,oracle,rgba);assert(assets[540].density==4);clear_assets();game_probe_density=8;hd.w=2560;hd.h=1600;hd.pitch=10240;
 clear_assets();free(oracle);free(rgba);
}
static void dispatch(const char*full){
 game_probe_assets=full;options[0]=(JE_OptionType){0};
 for(unsigned op=0;op<40;op++)options[op]=(JE_OptionType){.option=1,.ani=1,.pwr=0,.gr={83}};
 Uint8 after[328*200];unsigned seq[16];int xs[16],ys[16];
 /* FrontBlaster and shared original body options22/26; every style, side,
  * alive/mode/endlevel/player combination keeps identical state and writes. */
 const unsigned opts[]={20,22,26};
 for(unsigned z=0;z<COUNTOF(opts);z++)for(unsigned st=1;st<=2;st++)for(unsigned mode=0;mode<3;mode++)for(unsigned flags=0;flags<16;flags++){
  unsigned op=opts[z];Player a={.x=160,.y=100,.is_alive=(flags&1)!=0,.items={{mode==1?0:op,mode==0?0:op}},.sidekick={{100,73,st,0,1,0,true},{109,79,st,0,20,0,true}}},b=a;
  /* Empty slots have no draw while their original state logic still runs. */
  options[0]=(JE_OptionType){0};twoPlayerMode=(flags&2)!=0;endLevel=(flags&4)!=0;unsigned pnum=(flags&8)?2:1;reset_scene();
  for(unsigned tick=0;tick<4;tick++){
   memset(screen.pixels,49,64000);blit_calls=pixel_calls=quad_calls=0;baseline_dispatch(&a,pnum);memcpy(after,screen.pixels,64000);unsigned bc=blit_calls,qc=quad_calls;memcpy(seq,blit_indices,sizeof(seq));memcpy(xs,blit_x,sizeof(xs));memcpy(ys,blit_y,sizeof(ys));
   memset(screen.pixels,49,64000);blit_calls=pixel_calls=quad_calls=0;unsigned before=draws;candidate_dispatch(&b,pnum);
   assert(!memcmp(&a,&b,sizeof(a))&&!memcmp(after,screen.pixels,64000)&&blit_calls==bc&&quad_calls==qc&&!suppress);assert(!memcmp(seq,blit_indices,bc*sizeof(*seq))&&!memcmp(xs,blit_x,bc*sizeof(*xs))&&!memcmp(ys,blit_y,bc*sizeof(*ys)));
   if((pnum==2||!twoPlayerMode)&&!endLevel){unsigned bodies=mode==2?2u:1u;assert(qc==bodies&&bc==bodies*4&&pixel_calls==bodies*282);assert(draws==before+((op==20&&st==2)?bodies:0));for(unsigned j=0;j<bc;j++)assert(seq[j]==quad_ids[j%4]);}
   else assert(draws==before&&bc==0);dispatch_cases++;
  }
 }
 /* Charge, index or style mismatches cannot enter the dedicated route. */
 twoPlayerMode=endLevel=false;
 for(unsigned z=0;z<3;z++){unsigned charge=z==0?1:0,st=z==2?1:2;unsigned index=z==1?84:83;options[20].gr[0]=index;Player a={.items={{20,0}},.sidekick={{100,73,st,charge,20,0,true},{0}}},b=a;reset_scene();baseline_dispatch(&a,1);memcpy(after,screen.pixels,64000);unsigned bc=blit_calls,qc=quad_calls;reset_scene();candidate_dispatch(&b,1);assert(!memcmp(&a,&b,sizeof(a))&&!memcmp(after,screen.pixels,64000)&&draws==0&&blit_calls==bc&&quad_calls==qc);dispatch_cases++;}
 clear_assets();
}
int main(int argc,char**argv){
 assert(argc==5);size_t ns,cs,bs;Uint8*normal=read_file(argv[1],&ns),*christmas=read_file(argv[2],&cs),*bullets=read_file(argv[3],&bs);spriteSheet10=(Sprite2_array){normal,ns};spriteSheet8=(Sprite2_array){bullets,bs};Uint8 token[3]={0};spriteSheet9=(Sprite2_array){token,1};spriteSheet12=(Sprite2_array){token+1,1};explosionSpriteSheet=(Sprite2_array){token+2,1};
 screen.pixels=malloc(328*200);size_t hn=(size_t)hd.w*hd.h;hd.pixels=malloc(hn*4);hd_owner=calloc(hn,1);cloud_owner=calloc(hn,1);green_first=calloc(hn,sizeof(*green_first));green_under=calloc(hn,4);green_under_owner=calloc(hn,1);assert(screen.pixels&&hd.pixels&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);for(unsigned i=0;i<256;i++)rgb_palette[i]=i*0x010101u;reset_scene();char full[2048];snprintf(full,sizeof(full),"%s/valid",argv[4]);
 Uint8 c[24*28],m[24*28];assert(quad_decode(spriteSheet10,c,m));unsigned support=0;uint64_t stamp=UINT64_C(0xcbf29ce484222325);for(unsigned i=0;i<24*28;i++)support+=!!m[i];for(unsigned i=0;i<24*28*2;i++){stamp^=i<24*28?c[i]:m[i-24*28];stamp*=UINT64_C(0x100000001b3);}assert(support==282&&stamp==UINT64_C(0xeb8e5d2261e22274));
 identity(normal,ns,christmas,cs,full);resources_and_pixels(argv[4]);dispatch(full);
 clear_assets();free(normal);free(christmas);free(bullets);free(screen.pixels);free(hd.pixels);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);
 printf("{\"status\":\"PASS\",\"head_cases\":%u,\"source_identity_cases\":%u,\"coverage_only_cases\":%u,\"malformed_source_cases\":%u,\"wrong_scope_cases\":%u,\"resource_variants\":%u,\"wrapper_calls\":%u,\"pixel_cases\":%u,\"dispatch_cases\":%u,\"indexed_bytes_compared\":%zu,\"rgba_bytes_compared\":%zu,\"source_body_writes\":282,\"game_runs\":0}\n",cases,identity_cases,coverage_cases,malformed_cases,scope_cases,variant_cases,wrapper_calls,pixel_cases,dispatch_cases,checked_indexed_bytes,checked_rgba_bytes);return 0;
}
