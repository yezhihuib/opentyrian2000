/* SPDX-License-Identifier: GPL-2.0-or-later
 * Offline finite fixture: production admission/dispatch, compositor and indexed
 * blit_enemy are extracted verbatim. No game loop, drop injection or RNG.
 */
#include <SDL.h>
#include <assert.h>
#include <ctype.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "secret_exit_orb.h"
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define CHECK(x) do{++checks;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned long checks;static unsigned cases,indexed_blits,mirrored_calls,classic_calls;
#include "actual_types.inc"
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
typedef struct {int unused;} G101Record,PCapRecord,Forest13Record;
typedef struct {unsigned type,pool_slot,availability,size;bool score_item,damaged,independent_motion,static_animation;} G101EnemyContext;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
static SDL_Surface *canvas,*game_screen,*VGAScreen;
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;static Uint32 *green_under,*oracle;
static Uint8 selected[64000],expected[64000],restored_mask[64000];static Uint32 rgb_palette[256];
static bool active=true,suppress,suppress_green_smoke,suppress_cloud,scope=true;
static bool game_probe_known_blend=true,game_probe_local_blend=true,game_probe_original_reference,game_probe_missing,game_probe_invalid,xmas;
static int game_probe_density=8;static unsigned game_probe_scene_assets=1;static const char *game_probe_assets="fixture",*reject_reason;
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value,data_fixed_value,fixed_pickup_flash;
static unsigned draws,occlusions,local_entities,local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[128];static unsigned region_count;
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[8];static unsigned green_head_count;
typedef struct {Uint16 peak[16][14];} GreenBackground;
static Sprite2_array enemySpriteSheets[4];static Uint8 enemySpriteSheetIds[4];
static void font_before_effect(SDL_Rect r){(void)r;}
static void render_mirror_shadow_end(void){}
static bool mirror_enabled(void){return scope;}
static void render_mirror_unsupported(const char *s){reject_reason=s;}
static void game_probe_restore_region(unsigned b,SDL_Rect req,SDL_Rect r,unsigned g,unsigned n){(void)b;(void)req;(void)r;(void)g;(void)n;}
#define ground101_select(...) abort()
#define plateau_cap_select(...) abort()
#define forest13_select(...) abort()
static Uint32 palette_rgb(Uint8 index);
static int explosion_asset_slot(unsigned i){(void)i;return -1;}
#include "actual_compositor.inc"
#include "actual_adapter.inc"
static void game_probe_scene_draw(int r,unsigned b,int x,int y,int p,int s,bool ok){(void)r;(void)b;(void)x;(void)y;(void)p;(void)s;if(ok)mirrored_calls++;else classic_calls++;}
#include "actual_dispatch.inc"
#define storm_pixel(...) ((void)0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)
#define font_pixel(...) false
#define vulcan_shadow_clear(...) ((void)0)
#define vulcan_shadow_pixel(...) false
#include "actual_pixel.inc"
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define asset_debug_effect(...) ((void)0)
#define load_font_arrow_sprite_end(...) ((void)0)
#define pregame_font_sprite2_end(...) ((void)0)
#define blit_sprite2 indexed_sprite2
#define blit_sprite2_filter indexed_sprite2_filter
#include "actual_blit.inc"
#undef blit_sprite2
#undef blit_sprite2_filter
static void blit_sprite2(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){indexed_blits++;indexed_sprite2(s,x,y,b,i);}
static void blit_sprite2_filter(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i,Uint8 f){indexed_blits++;indexed_sprite2_filter(s,x,y,b,i,f);}
#include "actual_end.inc"
static struct {
 Sprite2_array *sprite2s;int ex,ey,egr[8],enemycycle,filter,enemytype,size,scoreitem,edamaged;
 int exc,eyc,fixedmovey,excc,eycc,xaccel,yaccel,ani,aniactive;
} enemy[1];static unsigned enemyAvail[1];static int tempMapXOfs;
#define asset_debug_enabled false
#define asset_debug_reference(...) ((void)0)
static const char shapeFile[]="123456789abcdefghijklmno";
#include "actual_wrapper.inc"
static Uint16 bank_words[46204/2];
#define bank ((Uint8*)bank_words)
static G101EnemyContext context={823,0,2,1,true,false,false,false};
static const int parts[4]={0,1,19,20};
static void reset(void)
{
 active=scope=true;reject_reason=NULL;game_probe_density=8;game_probe_assets="fixture";game_probe_scene_assets=1;
 game_probe_missing=game_probe_invalid=game_probe_original_reference=xmas=false;
 suppress=suppress_green_smoke=suppress_cloud=false;
 region_count=green_head_count=draws=occlusions=local_entities=local_regions=local_blocks=expanded_regions=boundary_crossings=0;
 memset(hd_owner,0,320*200*64);memset(cloud_owner,0,320*200*64);memset(green_first,0,320*200*64*2);memset(selected,0,sizeof(selected));
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  Uint8 q=(Uint8)(0x30+(x/11+y/9)%16);((Uint8*)game_screen->pixels)[y*320+x]=expected[y*320+x]=q;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)((Uint32*)canvas->pixels)[(y*8+sy)*2560+x*8+sx]=palette_rgb(q);
 }
}
static Uint32 over(Uint32 under,const Uint8 *p,int filter)
{
 unsigned color[3]={p[0],p[1],p[2]};
 if(filter) {
  unsigned peak=MAX(color[0],MAX(color[1],color[2])),v=(peak*15*256+127)/255,lo=v/256,hi=MIN(15,lo+1),f=v%256;
  for(unsigned c=0;c<3;c++){unsigned shift=16-c*8;color[c]=((((rgb_palette[filter|lo]>>shift)&255)*(256-f)+((rgb_palette[filter|hi]>>shift)&255)*f+128)/256);}
 }
 Uint32 out=0xff000000u;for(unsigned c=0;c<3;c++){unsigned shift=16-c*8;out|=((((under>>shift)&255)*(255-p[3])+color[c]*p[3]+127)/255)<<shift;}return out;
}
/* Independent linear-address indexed oracle, including physical row wrapping. */
static void index_oracle(Uint8 after[64000],int x,int y,unsigned base,int part,int filter)
{
 Uint8 src[168]={0},cov[168]={0};CHECK(decode_tile(enemySpriteSheets[0],base+(unsigned)part,src,cov,12,0,0));
 for(int iy=0;iy<14;iy++)for(int ix=0;ix<12;ix++)if(cov[iy*12+ix]) {
  int n=(y+iy)*320+x+ix;if(n<0||n>=64000)continue;after[n]=filter?(Uint8)(filter|(src[iy*12+ix]&15)):src[iy*12+ix];
 }
}
static void rgba_oracle(int x,int y,unsigned base,int part,int filter)
{
 const Uint8 *art=secret_exit_orb_rgba(base,rgb_palette);int px=part==1||part==20?12:0,py=part>=19?14:0;
 for(int iy=0;iy<112;iy++)for(int ix=0;ix<96;ix++) {
  int dx=x*8+ix,dy=y*8+iy;if(dx<0||dx>=2560||dy<0||dy>=1600)continue;
  const Uint8 *p=art+4*((py*8+iy)*192+px*8+ix);unsigned n=(unsigned)(dy*2560+dx);if(p[3])oracle[n]=over(oracle[n],p,filter);
 }
}
static void draw_call(int x,int y,unsigned base,int part,int filter,bool ok)
{
 Uint8 after[64000];memcpy(after,game_screen->pixels,64000);index_oracle(after,x,y,base,part,filter);
 memcpy(oracle,canvas->pixels,320*200*64*4);
 if(ok)rgba_oracle(x,y,base,part,filter);
 else {
  Uint8 src[168]={0},cov[168]={0};CHECK(decode_tile(enemySpriteSheets[0],base+(unsigned)part,src,cov,12,0,0));
  for(int iy=0;iy<14;iy++)for(int ix=0;ix<12;ix++)if(cov[iy*12+ix]) {
   int n=(y+iy)*320+x+ix;if(n<0||n>=64000)continue;
   for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++)oracle[((n/320)*8+sy)*2560+(n%320)*8+sx]=palette_rgb(after[n]);
  }
 }
 enemy[0].sprite2s=&enemySpriteSheets[0];enemy[0].ex=x;enemy[0].ey=y;enemy[0].egr[0]=(int)base;enemy[0].enemycycle=1;enemy[0].filter=filter;
 enemy[0].enemytype=(int)context.type;enemy[0].size=(int)context.size;enemy[0].scoreitem=context.score_item;enemy[0].edamaged=context.damaged;enemyAvail[0]=context.availability;
 unsigned b=indexed_blits,h=mirrored_calls;blit_enemy(game_screen,0,0,0,part);
 CHECK(indexed_blits==b+1);CHECK(mirrored_calls==h+(unsigned)ok);CHECK(!suppress);
 CHECK(!memcmp(after,game_screen->pixels,64000)&&!memcmp(after,expected,64000));
 CHECK(!memcmp(oracle,canvas->pixels,320*200*64*4));CHECK(!reject_reason);
 if(ok) {
  Uint8 src[168]={0},cov[168]={0};CHECK(decode_tile(enemySpriteSheets[0],base+(unsigned)part,src,cov,12,0,0));
  for(int iy=0;iy<14;iy++)for(int ix=0;ix<12;ix++)if(cov[iy*12+ix]&&y+iy>=0&&y+iy<200)
   for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){unsigned n=(unsigned)(((y+iy)*8+sy)*2560+(x+ix)*8+sx);CHECK(hd_owner[n]==1&&!cloud_owner[n]);}
 }
 ++cases;
}
static bool admit(SDL_Surface *surface,int x,int y,Sprite2_array b,unsigned base,int part,int filter,const G101EnemyContext *c)
{bool ok=render_mirror_enemy_tile(surface,x,y,b,base,part,filter,c);render_mirror_entity_end();++cases;return ok;}
#define NO(s,x,y,b,base,part,f,c) CHECK(!admit(s,x,y,b,base,part,f,c))
static void negatives(void)
{
 reset();Sprite2_array b=enemySpriteSheets[0];G101EnemyContext c=context;
 const unsigned other[]={577,591,593,688,690,822,824,842,844};for(unsigned i=0;i<sizeof(other)/sizeof(*other);i++){c.type=other[i];NO(game_screen,40,50,b,85,0,0,&c);}c=context;
 c.size=0;NO(game_screen,40,50,b,85,0,0,&c);c=context;c.availability=0;NO(game_screen,40,50,b,85,0,0,&c);c.availability=1;NO(game_screen,40,50,b,85,0,0,&c);c=context;c.score_item=false;NO(game_screen,40,50,b,85,0,0,&c);c=context;c.damaged=true;NO(game_screen,40,50,b,85,0,0,&c);
 NO(game_screen,40,50,b,85,0,0,NULL);
 const unsigned badbases[]={0,84,86,130,132,232,234,UINT_MAX};for(unsigned i=0;i<sizeof(badbases)/sizeof(*badbases);i++)NO(game_screen,40,50,b,badbases[i],0,0,&context);
 const int badparts[]={-1,2,18,21,INT_MAX};for(unsigned i=0;i<sizeof(badparts)/sizeof(*badparts);i++)NO(game_screen,40,50,b,85,badparts[i],0,&context);
 NO(game_screen,40,50,b,85,0,-1,&context);NO(game_screen,40,50,b,85,0,256,&context);
 const int badxy[][2]={{-1,50},{309,50},{INT_MIN,50},{INT_MAX,50},{40,-14},{40,200},{40,INT_MIN},{40,INT_MAX}};for(unsigned i=0;i<sizeof(badxy)/sizeof(*badxy);i++)NO(game_screen,badxy[i][0],badxy[i][1],b,85,0,0,&context);
 SDL_Surface other_surface=*game_screen;NO(&other_surface,40,50,b,85,0,0,&context);NO(NULL,40,50,b,85,0,0,&context);
 Uint8 id=enemySpriteSheetIds[0];enemySpriteSheetIds[0]=19;NO(game_screen,40,50,b,85,0,0,&context);enemySpriteSheetIds[0]=id;
 b.size--;NO(game_screen,40,50,b,85,0,0,&context);b=enemySpriteSheets[0];Uint8 alternate[46204];memcpy(alternate,bank,sizeof(alternate));b.data=alternate;NO(game_screen,40,50,b,85,0,0,&context);b=enemySpriteSheets[0];b.data=NULL;NO(game_screen,40,50,b,85,0,0,&context);b=enemySpriteSheets[0];
 /* Warm mutations: selected color/support/offset, other phases and unrelated
  * source data all revoke the exact whole-sheet lease on the next draw. */
 CHECK(admit(game_screen,40,50,b,85,0,0,&context));
 const unsigned offsets[]={0,168,260,464,1000,46203};for(unsigned i=0;i<sizeof(offsets)/sizeof(*offsets);i++){Uint8 save=bank[offsets[i]];bank[offsets[i]]^=1;NO(game_screen,40,50,b,85,0,0,&context);bank[offsets[i]]=save;CHECK(admit(game_screen,40,50,b,85,0,0,&context));}
 for(unsigned base=85;base<=233;base+=base==85?46:102){size_t pos=bank[2*(base-1)]|((size_t)bank[2*(base-1)+1]<<8);Uint8 save=bank[pos];bank[pos]^=1;NO(game_screen,40,50,b,85,0,0,&context);bank[pos]=save;save=bank[pos+1];bank[pos+1]^=1;NO(game_screen,40,50,b,85,0,0,&context);bank[pos+1]=save;}
 bool *gates[]={&active,&scope,&game_probe_missing,&game_probe_invalid,&game_probe_original_reference,&xmas};for(unsigned i=0;i<sizeof(gates)/sizeof(*gates);i++){bool v=*gates[i];*gates[i]=!v;NO(game_screen,40,50,b,85,0,0,&context);*gates[i]=v;}
 game_probe_scene_assets=0;NO(game_screen,40,50,b,85,0,0,&context);game_probe_scene_assets=1;
 reject_reason="prior";NO(game_screen,40,50,b,85,0,0,&context);reject_reason=NULL;
 game_probe_density=4;NO(game_screen,40,50,b,85,0,0,&context);game_probe_density=8;
 game_probe_assets=NULL;NO(game_screen,40,50,b,85,0,0,&context);game_probe_assets="fixture";
 SDL_Surface *cv=canvas;canvas=NULL;NO(game_screen,40,50,b,85,0,0,&context);canvas=cv;
 void *p=canvas->pixels;canvas->pixels=NULL;NO(game_screen,40,50,b,85,0,0,&context);canvas->pixels=(Uint8*)p+1;NO(game_screen,40,50,b,85,0,0,&context);canvas->pixels=game_screen->pixels;NO(game_screen,40,50,b,85,0,0,&context);canvas->pixels=p;
 p=game_screen->pixels;game_screen->pixels=NULL;NO(game_screen,40,50,b,85,0,0,&context);game_screen->pixels=p;
 int *dims[]={&canvas->w,&canvas->h,&canvas->pitch,&game_screen->w,&game_screen->h,&game_screen->pitch};for(unsigned i=0;i<6;i++){int v=*dims[i];--*dims[i];NO(game_screen,40,50,b,85,0,0,&context);*dims[i]=v;}
 int pitch=canvas->pitch;canvas->pitch=INT_MAX&~3;NO(game_screen,40,50,b,85,0,0,&context);canvas->pitch=pitch;
 Uint32 format=canvas->format->format;canvas->format->format=SDL_PIXELFORMAT_RGBA8888;NO(game_screen,40,50,b,85,0,0,&context);canvas->format->format=format;
 format=game_screen->format->format;game_screen->format->format=SDL_PIXELFORMAT_RGB332;NO(game_screen,40,50,b,85,0,0,&context);game_screen->format->format=format;
 Uint8 **owners[]={&hd_owner,&cloud_owner,&green_under_owner};for(unsigned i=0;i<3;i++){Uint8 *v=*owners[i];*owners[i]=NULL;NO(game_screen,40,50,b,85,0,0,&context);*owners[i]=v;}
 Uint16 *first=green_first;green_first=NULL;NO(game_screen,40,50,b,85,0,0,&context);green_first=(Uint16*)((Uint8*)first+1);NO(game_screen,40,50,b,85,0,0,&context);green_first=first;
 Uint32 *under=green_under;green_under=NULL;NO(game_screen,40,50,b,85,0,0,&context);green_under=(Uint32*)((Uint8*)under+1);NO(game_screen,40,50,b,85,0,0,&context);green_under=under;
 CHECK(admit(game_screen,40,50,b,85,0,0,&context));
}
static void native_capture(const char *out,const char *name)
{
 SDL_Surface *n=SDL_CreateRGBSurfaceWithFormat(0,640,400,32,SDL_PIXELFORMAT_ARGB8888);CHECK(n);SDL_Renderer *r=SDL_CreateSoftwareRenderer(n);CHECK(r);
 SDL_Texture *t=SDL_CreateTexture(r,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,2560,1600);CHECK(t);CHECK(!SDL_SetTextureScaleMode(t,SDL_ScaleModeNearest));CHECK(!SDL_SetTextureBlendMode(t,SDL_BLENDMODE_NONE));CHECK(!SDL_UpdateTexture(t,NULL,canvas->pixels,canvas->pitch));CHECK(!SDL_RenderCopy(r,t,NULL,NULL));SDL_RenderPresent(r);
 char path[2048];CHECK(snprintf(path,sizeof(path),"%s/%s.bmp",out,name)<(int)sizeof(path));CHECK(!SDL_SaveBMP(n,path));SDL_DestroyTexture(t);SDL_DestroyRenderer(r);SDL_FreeSurface(n);
}
int main(int argc,char **argv)
{
 CHECK(argc==4);CHECK(!SDL_Init(SDL_INIT_VIDEO));char path[2048];FILE *f;
 CHECK(snprintf(path,sizeof(path),"%s/newshp.shp",argv[1])<(int)sizeof(path));f=fopen(path,"rb");CHECK(f&&fread(bank,1,46204,f)==46204&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){46204,bank};enemySpriteSheetIds[0]=20;
 clock_t started=clock();for(unsigned i=0;i<2000;i++)CHECK(secret_exit_orb_source_matches(enemySpriteSheets[0]));
 double hash_seconds=(double)(clock()-started)/CLOCKS_PER_SEC;
 printf("source pin: 2000 full-sheet hashes, %.3f us/call, %.3f ms/4-part orb (CPU time, %s)\n",hash_seconds*1e6/2000,hash_seconds*1000/500,argv[3]);
 CHECK(snprintf(path,sizeof(path),"%s/palette.dat",argv[1])<(int)sizeof(path));f=fopen(path,"rb");CHECK(f&&!fseek(f,5*768,SEEK_SET));for(unsigned i=0;i<256;i++){Uint8 p[3];CHECK(fread(p,1,3,f)==3);rgb_palette[i]=0;for(unsigned c=0;c<3;c++)rgb_palette[i]|=(Uint32)((p[c]<<2)|(p[c]>>4))<<(16-c*8);}fclose(f);
 game_screen=VGAScreen=SDL_CreateRGBSurface(0,320,200,8,0,0,0,0);canvas=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);CHECK(game_screen&&canvas);
 hd_owner=calloc(320*200*64,1);cloud_owner=calloc(320*200*64,1);green_under_owner=calloc(320*200*64,1);green_first=calloc(320*200*64,2);green_under=calloc(320*200*64,4);oracle=malloc(320*200*64*4);CHECK(hd_owner&&cloud_owner&&green_under_owner&&green_first&&green_under&&oracle);
 const unsigned bases[]={85,131,233},cycle[]={85,85,131,131,233,233,131,131};
 for(unsigned obj=0;obj<2;obj++)for(unsigned b=0;b<3;b++)for(unsigned p=0;p<4;p++)for(unsigned filter=0;filter<2;filter++){reset();context.type=obj?843:823;draw_call(144+(p%2)*12,83+(p/2)*14,bases[b],parts[p],filter?0x90:0,true);}
 context.type=823;for(unsigned t=0;t<8;t++){reset();for(unsigned p=0;p<4;p++)draw_call(144+(p%2)*12,83+(p/2)*14,cycle[t],parts[p],0,true);}
 const int clips[][2]={{0,-13},{308,199},{0,199},{308,-13}};for(unsigned p=0;p<4;p++)for(unsigned k=0;k<4;k++){reset();draw_call(clips[k][0],clips[k][1],233,parts[p],0,true);}
 /* Prior HD/cloud detail beneath the orb, then complete-region restoration. */
 reset();for(int y=83*8;y<111*8;y++)for(int x=144*8;x<168*8;x++){unsigned n=(unsigned)(y*2560+x);((Uint32*)canvas->pixels)[n]=0xff336699;hd_owner[n]=cloud_owner[n]=1;}
 for(unsigned p=0;p<4;p++)draw_call(144+(p%2)*12,83+(p/2)*14,85,parts[p],0,true);
 CHECK(region_count==1);restore_classic_rect((SDL_Rect){150,90,1,1});CHECK(local_regions==1&&!boundary_crossings);
 for(int y=83*8;y<111*8;y++)for(int x=144*8;x<168*8;x++){CHECK(((Uint32*)canvas->pixels)[y*2560+x]==palette_rgb(((Uint8*)game_screen->pixels)[(y/8)*320+x/8]));CHECK(!hd_owner[y*2560+x]&&!cloud_owner[y*2560+x]);}
 reset();draw_call(144,83,85,0,0,true);Uint8 *pixel=(Uint8*)game_screen->pixels+90*320+150;*pixel=0x7d;render_mirror_pixel(game_screen,pixel,*pixel,MIRROR_NORMAL);CHECK(!selected[90*320+150]&&!hd_owner[(90*8)*2560+150*8]);
 /* Real classic fallback at row wrapping, excluded same-frame objects and flags. */
 const unsigned others[]={577,591,593,688,690};for(unsigned i=0;i<5;i++){reset();context.type=others[i];draw_call(144,83,85,0,0,false);}context.type=823;
 reset();draw_call(309,83,85,0,0,false);for(unsigned i=0;i<3;i++){reset();if(i==0)game_probe_missing=true;if(i==1)game_probe_invalid=true;if(i==2)scope=false;draw_call(144,83,85,0,0,false);}
 /* Prior HD fallback must overwrite covered source even when the indexed
  * source equals the previous INDEX8 value. */
 reset();scope=false;
 Uint8 matching[64000];memcpy(matching,game_screen->pixels,64000);index_oracle(matching,144,83,85,0,0);memcpy(game_screen->pixels,matching,64000);memcpy(expected,matching,64000);
 for(int y=83*8;y<97*8;y++)for(int x=144*8;x<156*8;x++){unsigned n=(unsigned)(y*2560+x);((Uint32*)canvas->pixels)[n]=0xff336699;hd_owner[n]=cloud_owner[n]=1;}
 draw_call(144,83,85,0,0,false);
 negatives();
 /* Native SDL nearest presenter, complete three-phase composites, explicit
  * synthetic scenery: never claim these captures came from hidden gameplay. */
 reset();for(unsigned b=0;b<3;b++)for(unsigned p=0;p<4;p++)draw_call(40+(int)b*90+(int)(p%2)*12,80+(int)(p/2)*14,bases[b],parts[p],0,true);native_capture(argv[2],"fixture-after-native640");
 reset();scope=false;for(unsigned b=0;b<3;b++)for(unsigned p=0;p<4;p++)draw_call(40+(int)b*90+(int)(p%2)*12,80+(int)(p/2)*14,bases[b],parts[p],0,false);native_capture(argv[2],"fixture-before-native640");
 CHECK(snprintf(path,sizeof(path),"%s/adapter-%s-receipt.json",argv[2],argv[3])<(int)sizeof(path));f=fopen(path,"w");CHECK(f);fprintf(f,"{\"cases\":%u,\"checks\":%lu,\"indexed_blits\":%u,\"mirrored_calls\":%u,\"classic_calls\":%u,\"native\":\"SDL nearest software, synthetic scenery, no gameplay\"}\n",cases,checks,indexed_blits,mirrored_calls,classic_calls);fclose(f);
 printf("secret orb: %u cases / %lu checks, exact INDEX8 + RGBA; %u original blits (%s)\n",cases,checks,indexed_blits,argv[3]);
 free(oracle);free(green_under);free(green_first);free(green_under_owner);free(cloud_owner);free(hd_owner);SDL_FreeSurface(canvas);SDL_FreeSurface(game_screen);SDL_Quit();return 0;
}
