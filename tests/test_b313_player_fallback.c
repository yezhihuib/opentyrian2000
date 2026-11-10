#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include "SDL.h"
#include "b313_family_writer.h"
#include "b313_terrain_fallback.h"
#include "b313_player_fallback.h"
#include "player_ship_family.h"
extern bool b313_family_writer_peek_current(uint64_t);
#define FG_RGBA_BYTES 172032
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
#define REAR_STAT struct stat
#define REAR_OPEN(path) open(path,O_RDONLY)
#define REAR_FSTAT fstat
#define REAR_REGULAR(mode) S_ISREG(mode)
#define REAR_READ read
#define REAR_CLOSE close
typedef enum {MIRROR_OUTPUT_UNSUPPORTED,MIRROR_OUTPUT_ORDINARY} MirrorOutputKind;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
static SDL_Surface *fc_source,*fc_output,*canvas,*game_screen,*VGAScreen;
static void *fc_source_pixels,*fc_output_pixels;
static uint64_t fc_generation,fc_frame,fc_session;
static struct {bool frame_failed,frame_active,ready;} fc;
static Uint32 rgb_palette[256];
static bool parent_requested=true,geometry_ok=true,ground_ok=true;
static bool scope_ok=true,source_ok=true,palette_ok=true,fc_native_call,suppress;
static struct {int x,y;unsigned invulnerable_ticks;} player[1];
static Sprite2_array spriteSheet9;
static uint64_t bank_pin;
static struct {bool enabled;} rp;
static struct {Uint8 *rgba[10];Uint8 ground_mask[64000];} fg;
static struct {bool enabled;Uint8 *rgba[12];Uint8 mask[64000];} fl;
static struct {bool enabled;Uint8 *rgba;Uint8 mask[64000];} fk,fs340;
static uint64_t fg_payload_pins[10],fg_cliff_payload_pins[12],fg_corner_payload_pin,fg_static340_payload_pin;
static unsigned checks,readbacks,hud_calls,mutate_lock,lock_calls,callback_mode,callback_number;
static Uint8 *oracle_art[5];
static SDL_Renderer *renderer;
static const char *asset_root;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAILED line %d: %s\n",__LINE__,#x);abort();}}while(0)
#include "player_ship_native.inc"
#include "player_fallback_helpers.inc"
#include "player_fallback_oracle.inc"
static bool render_mirror_family_requested(void){return parent_requested;}
static bool family_rgb(SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==2560&&s->h==1600&&s->pitch==10240&&s->format->format==SDL_PIXELFORMAT_ARGB8888&&!s->locked;}
static bool indexed(SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==320&&s->h==200&&s->pitch==320&&s->format->format==SDL_PIXELFORMAT_INDEX8&&!s->locked;}
static bool family_geometry(bool rgb){return geometry_ok&&indexed(fc_source)&&indexed(fc_output)&&fc_source->pixels==fc_source_pixels&&fc_output->pixels==fc_output_pixels&&fc_source_pixels!=fc_output_pixels&&(!rgb||family_rgb(canvas));}
static bool fg_terrain_snapshot_current(void){return ground_ok&&family_geometry(true);}
static uint64_t fg_hash(const Uint8 *p,size_t n){return asteroid1_stamp(p,n);}
static Uint32 palette_rgb(Uint8 v){return UINT32_C(0xff000000)|rgb_palette[v];}
static Uint32 color(Uint8 v){return UINT32_C(0xff000000)|rgb_palette[v];}
static bool family_upscale_8x(SDL_Surface *out,SDL_Surface *in)
{
 if(!family_rgb(out)||!indexed(in))return false;
 for(unsigned y=0;y<200;y++)for(unsigned x=0;x<320;x++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)
  ((Uint32 *)out->pixels)[(y*8+sy)*2560+x*8+sx]=color(((Uint8 *)in->pixels)[y*320+x]);
 return true;
}
static void family_static_hud_compose_surface(SDL_Surface *s){++hud_calls;((Uint32 *)s->pixels)[1599*2560+2559]=UINT32_C(0xff123456);}
static bool ps_requested(void){const char *v=getenv("PLAYER_SHIP_FAMILY_ENABLE");return parent_requested&&v&&!strcmp(v,"1");}
static bool ps_scope(void){return scope_ok&&ps_requested();}
/* Synthetic source identity, checked on every call. Original bank digest and
 * real gameplay/palette admission are deliberately outside this fixture. */
static bool ps_source(Sprite2_array bank){return source_ok&&bank.data==spriteSheet9.data&&bank.size==33484&&bank.size==spriteSheet9.size&&asteroid1_stamp(bank.data,bank.size)==bank_pin;}
static bool global_talon_palette_matches(void){return palette_ok;}
static const char *ps_root(void){const char *v=getenv("PLAYER_SHIP_FAMILY_ASSET_DIR");return v?v:"";}
static void asset_debug_readback(SDL_Renderer *r);
static int injected_lock(SDL_Texture *,const SDL_Rect *,void **,int *);
/* The adapter forward declarations below match the production include order. */
static void pf_reset(void);
static void pf_shared_fail(void);
static void pf_release(void);
static void pf_begin(void);
static void pf_pixel(unsigned,int);
static void pf_finish(void);
static bool pf_compose(void);
static void pf_present_begin(bool);
static void pf_present_end(void);
#define SDL_LockTexture injected_lock
#include "b313_terrain_fallback_mirror.inc"
#undef SDL_LockTexture
#include "b313_player_fallback_mirror.inc"

static Uint8 sampled_mask[672];
static Uint32 sampled_patch[43008];
static bool expect_player_present;
static void asset_debug_readback(SDL_Renderer *r)
{
 CHECK(r==renderer);CHECK(render_mirror_terrain_fallback_status().presenting);
 B313PlayerFallbackStatus s=render_mirror_player_fallback_status();
 CHECK(s.presenting==expect_player_present);
 if(expect_player_present){
  CHECK(render_mirror_player_fallback_sample(sampled_mask,672,sampled_patch,43008));
  CHECK(!render_mirror_player_fallback_sample(sampled_mask,671,sampled_patch,43008));
  CHECK(!render_mirror_player_fallback_sample(sampled_mask,672,sampled_patch,43007));
  CHECK(!render_mirror_player_fallback_sample(NULL,672,sampled_patch,43008));
  CHECK(!render_mirror_player_fallback_sample(sampled_mask,672,NULL,43008));
 }
 else CHECK(!render_mirror_player_fallback_sample(sampled_mask,672,sampled_patch,43008));
 ++readbacks;
}
static int injected_lock(SDL_Texture *target,const SDL_Rect *rect,void **pixels,int *pitch)
{
 int result=SDL_LockTexture(target,rect,pixels,pitch);++lock_calls;if(result)return result;
 switch(mutate_lock){
 case 1:rgb_palette[1]^=1;break;
 case 2:geometry_ok=false;break;
 case 3:ground_ok=false;break;
 case 4:fg.rgba[0][0]^=1;break;
 case 5:((Uint8 *)fc_source_pixels)[0]^=1;break;
 case 6:((Uint8 *)fc_output_pixels)[0]^=1;break;
 case 7:++fc_generation;break;
 case 8:++fc_frame;break;
 case 9:setenv("BUILDING313_TERRAIN_FALLBACK_ENABLE","0",1);break;
 case 10:SDL_SetTextureScaleMode(target,SDL_ScaleModeLinear);break;
 case 11:SDL_SetTextureBlendMode(target,SDL_BLENDMODE_BLEND);break;
 case 12:b313_family_writer_gap(NWO_GAP_UNREGISTERED);break;
 case 13:*pitch=10239;break;
 case 14:*pixels=NULL;break;
 /* Ship-only changes must drop ship pixels, retaining proven terrain. */
 case 20:scope_ok=false;break;
 case 21:source_ok=false;break;
 case 22:palette_ok=false;break;
 case 23:++fc_session;break;
 case 24:++player[0].x;break;
 case 25:++player[0].y;break;
 case 26:player[0].invulnerable_ticks=1;break;
 case 27:spriteSheet9.data[33300]^=1;break;
 case 28:setenv("BUILDING313_PLAYER_FALLBACK_ENABLE","0",1);break;
 case 29:setenv("PLAYER_SHIP_FAMILY_ENABLE","0",1);break;
 case 30:setenv("PLAYER_SHIP_FAMILY_ASSET_DIR","unrelated",1);break;
 case 31:pf_art.rgba[2][42]^=1;break;
 case 32:pf_art.rgba[2]=oracle_art[2];break;
 case 33:pf.art=oracle_art[2];break;
 case 34:pf.patch[123]^=1;break;
 case 35:pf.mask[0]=1;break;
 case 36:pf_art.valid=false;break;
 case 37:spriteSheet9.data++;break;
 case 38:spriteSheet9.size--;break;
 }
 return result;
}
/* Exact overlay RLE loop, including its actual physical-store observation.
 * Other unrelated diagnostic observers are no-ops; no writer proof is forged. */
#define load_font_arrow_sprite_begin(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define load_font_arrow_sprite_end() ((void)0)
#define pregame_font_sprite2_end() ((void)0)
#define asset_debug_effect(...) ((void)0)
void nwo_observe_store(SDL_Surface *s,const void *p,size_t n,enum NwoWriter writer)
{if(callback_mode!=6)b313_family_writer_store(s,p,n,writer);}
static void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 value,int style)
{
 (void)value;unsigned call=callback_number++;
 if(!call){
  if(callback_mode==1)*p^=1;
  if(callback_mode==2){tf_pixel(s,p,style);tf_pixel(s,p,style);return;}
  if(callback_mode==3)return;
  if(callback_mode==4)style=MIRROR_BLEND;
  if(callback_mode==5)style=MIRROR_SHADOW;
  if(callback_mode==7)style=99;
  if(callback_mode==8){tf_pixel(s,p+1,style);return;}
 }
 tf_pixel(s,p,style);
}
#include "player_fallback_native.inc"
static const unsigned parts[4]={0,1,19,20};
static Uint16 encoded[16742];
static void make_bank(unsigned pose)
{
 Uint8 *data=(Uint8 *)encoded;memset(data,0,sizeof encoded);unsigned at=600;
 const PlayerShipSpec *spec=&oracle_specs[pose];
 for(unsigned part=0;part<4;part++){
  unsigned tile=spec->index+parts[part];data[(tile-1)*2]=(Uint8)at;data[(tile-1)*2+1]=(Uint8)(at>>8);
  for(unsigned row=0;row<14;row++){
   unsigned cursor=0;
   for(unsigned n=part?spec->ends[part-1]:0;n<spec->ends[part];n++){
    const PlayerShipWrite *w=spec->writes+n;if(w->y!=row+(part/2)*14)continue;
    unsigned col=w->x-(part%2)*12;CHECK(col>=cursor&&col<12);
    data[at++]=(Uint8)(0x10+col-cursor);data[at++]=w->index;cursor=col+1;
   }
   data[at++]=(Uint8)(12-cursor);
  }
  data[at++]=0x0f;
 }
 CHECK(at<sizeof encoded);spriteSheet9=(Sprite2_array){data,sizeof encoded};bank_pin=asteroid1_stamp(data,sizeof encoded);
}
static Uint32 terrain_color(unsigned x,unsigned y,unsigned sx,unsigned sy)
{return UINT32_C(0xff000000)|(((x*3+sx+53)&255)<<16)|(((y*5+sy+71)&255)<<8)|((x+y+sx+sy+91)&255);}
static bool terrain_cell(unsigned x,unsigned y){return (x+y)%3!=0;}
static void start(unsigned pose)
{
 pf_reset();tf_reset();b313_family_writer_reset();
 parent_requested=geometry_ok=ground_ok=scope_ok=source_ok=palette_ok=true;
 fc.frame_failed=false;fc.frame_active=true;fc.ready=false;fc_native_call=suppress=false;
 mutate_lock=callback_mode=callback_number=0;expect_player_present=false;
 setenv("BUILDING313_TERRAIN_FALLBACK_ENABLE","1",1);setenv("BUILDING313_PLAYER_FALLBACK_ENABLE","1",1);
 setenv("PLAYER_SHIP_FAMILY_ENABLE","1",1);setenv("PLAYER_SHIP_FAMILY_ASSET_DIR",asset_root,1);
 for(unsigned i=0;i<256;i++)rgb_palette[i]=((i*3&255)<<16)|((i*5&255)<<8)|(i*7&255);
 memset(fc_source->pixels,17,64000);memset(fc_output->pixels,17,64000);
 fc_source_pixels=fc_source->pixels;fc_output_pixels=fc_output->pixels;
 ++fc_generation;++fc_frame;++fc_session;player[0].x=53;player[0].y=47;player[0].invulnerable_ticks=0;make_bank(pose);
 CHECK(b313_family_writer_begin(fc_frame,fc_source,fc_output));
 memset(fg.ground_mask,0,64000);memset(fl.mask,0,64000);memset(fk.mask,0,64000);memset(fs340.mask,0,64000);
 fl.enabled=fk.enabled=fs340.enabled=rp.enabled=false;
 for(unsigned i=0;i<10;i++){memset(fg.rgba[i],i+1,FG_RGBA_BYTES);fg_payload_pins[i]=fg_hash(fg.rgba[i],FG_RGBA_BYTES);}
 tf_begin();CHECK(tf_tracking()&&tf.valid);
 for(unsigned y=38;y<70;y++)for(unsigned x=46;x<74;x++)if(terrain_cell(x,y)){
  fg.ground_mask[y*320+x]=1;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)((Uint32 *)canvas->pixels)[(y*8+sy)*2560+x*8+sx]=terrain_color(x,y,sx,sy);
 }
 tf_capture();CHECK(tf.captured&&tf.valid);
}
static void pose_body(unsigned pose)
{
 pf_pose(1,spriteSheet9,233,(int)oracle_specs[pose].index,0);
 pf_body(game_screen,48,40,spriteSheet9,oracle_specs[pose].index,MIRROR_NORMAL,1,233);
}
static void native_quad(unsigned pose,unsigned count)
{for(unsigned part=0;part<count;part++)blit_sprite2(game_screen,48+(int)(part%2)*12,40+(int)(part/2)*14,spriteSheet9,oracle_specs[pose].index+parts[part]);}
static void draw(unsigned pose){pose_body(pose);native_quad(pose,4);pf_end();}
static void store(unsigned off,Uint8 value,int style)
{Uint8 *p=(Uint8 *)fc_source_pixels+off;b313_family_writer_store(fc_source,p,1,NWO_SPRITE2);*p=value;CHECK(tf_pixel(fc_source,p,style));}
static void crop(void)
{
 for(unsigned y=0;y<184;y++){
  Uint8 *a=(Uint8 *)fc_source_pixels+y*320+24,*b=(Uint8 *)fc_output_pixels+y*320;
  b313_family_writer_copy(fc_output,b,fc_source,a,264);memcpy(b,a,264);
 }
}
static void finish(void){crop();tf_finish(MIRROR_OUTPUT_ORDINARY);}
static SDL_Rect destination={0,0,320,200};
/* Independent pixel oracle. Ownership comes from frozen records, not pf.mask;
 * underlay is recorded before body using the fixture's known native/terrain
 * model. Asset buffers are independent copies, never pf_art aliases. */
static Uint8 expected_mask[672],under_native[672];
static Uint32 underlay[43008];
static unsigned alpha_zero,alpha_full,native_holes;
static void snapshot_underlay(void)
{
 for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++){
  unsigned off=(40+y)*320+48+x;under_native[y*24+x]=((Uint8 *)fc_source_pixels)[off];
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)underlay[(y*8+sy)*192+x*8+sx]=
   tf.mask[off]?terrain_color(48+x,40+y,sx,sy):color(under_native[y*24+x]);
 }
}
static const Uint8 *reference_sample(unsigned pose,unsigned x,unsigned y)
{
 static const Uint8 transparent[4]={0};const PlayerShipSpec *spec=&oracle_specs[pose];
 if(spec->index==233)return oracle_art[pose]+(y*192+x)*4;
 int nx=(int)x*100+spec->offset_x,ny=(int)y*100+spec->offset_y;
 if(nx<0||ny<0)return transparent;
 unsigned sx=(unsigned)nx/(unsigned)spec->scale_x,sy=(unsigned)ny/(unsigned)spec->scale_y;
 return sx<192&&sy<224?oracle_art[pose]+(sy*192+sx)*4:transparent;
}
static Uint32 reference_blend(Uint32 before,const Uint8 *rgba)
{
 Uint32 result=UINT32_C(0xff000000);unsigned alpha=rgba[3];
 for(unsigned c=0;c<3;c++)result|=(((((before>>(16-c*8))&255)*(255-alpha)+rgba[c]*alpha+127)/255)<<(16-c*8));
 return result;
}
static void expect_pose(unsigned pose)
{
 memset(expected_mask,0,sizeof expected_mask);const PlayerShipSpec *spec=&oracle_specs[pose];
 for(unsigned n=0;n<spec->count;n++){const PlayerShipWrite *w=spec->writes+n;CHECK(!expected_mask[w->y*24+w->x]);expected_mask[w->y*24+w->x]=1;}
}
static void successful_draw(unsigned pose)
{
 uint64_t pixels_before=b313_family_writer_status().pixels;
 snapshot_underlay();draw(pose);expect_pose(pose);CHECK(pf.complete&&!pf.active&&pf.valid);
 CHECK(pf.count==oracle_specs[pose].count&&pf.part_mask==15);
 CHECK(!memcmp(expected_mask,pf.mask,sizeof expected_mask));
 CHECK(b313_family_writer_status().pixels==pixels_before+oracle_specs[pose].count);
}
static void verify_pixels(unsigned pose,bool player_used)
{
 SDL_Rect rect={24*8,40*8,192,224};Uint32 readback[43008];
 CHECK(SDL_RenderReadPixels(renderer,&rect,SDL_PIXELFORMAT_ARGB8888,readback,192*4)==0);
 for(unsigned y=0;y<224;y++)for(unsigned x=0;x<192;x++){
  unsigned lx=x/8,ly=y/8,local=ly*24+lx,off=(40+ly)*320+48+lx;
  unsigned n=y*192+x;Uint32 want=color(((Uint8 *)fc_source_pixels)[off]);
  if(tf.mask[off])want=terrain_color(48+lx,40+ly,x%8,y%8);
  if(player_used&&expected_mask[local]){
   const Uint8 *art=reference_sample(pose,x,y);want=reference_blend(underlay[n],art);
   alpha_zero+=art[3]==0;alpha_full+=art[3]==255;
   CHECK(sampled_patch[n]==want);
  }else if(!expected_mask[local])++native_holes;
  CHECK(((Uint32 *)tf.result->pixels)[(320+y)*2560+192+x]==want);
  CHECK(readback[n]==want);
 }
 if(player_used)CHECK(!memcmp(sampled_mask,expected_mask,sizeof expected_mask));
}
static void present(unsigned pose,bool used)
{
 expect_player_present=used;unsigned before=readbacks;CHECK(tf.ready);CHECK(tf_present(renderer,fc_output,&destination));CHECK(readbacks==before+1);
 CHECK(!tf.ready&&!pf.ready&&!pf.presenting);CHECK(!render_mirror_player_fallback_sample(sampled_mask,672,sampled_patch,43008));
 verify_pixels(pose,used);CHECK(!tf_present(renderer,fc_output,&destination));CHECK(readbacks==before+1);
}
static void test_exact_five_poses(void)
{
 CHECK(sizeof pf.mask==672&&sizeof pf.patch==43008*sizeof(Uint32));
 for(unsigned pose=0;pose<5;pose++){
  start(pose);fc.frame_failed=true; /* Whole-scene admission lost before pose. */
  successful_draw(pose);finish();CHECK(pf.ready&&tf.ready);
  for(unsigned n=0;n<672;n++)CHECK(pf.mask[n]==expected_mask[n]);
  /* Patch composition must not happen until post-lock validation. */
  const PlayerShipWrite *w=&oracle_specs[pose].writes[0];unsigned off=(40+w->y)*320+48+w->x;
  CHECK(((Uint32 *)tf.result->pixels)[((40+w->y)*8)*2560+(24+w->x)*8]==color(((Uint8 *)fc_source_pixels)[off]));
  present(pose,true);
 }
 CHECK(alpha_zero>0&&alpha_full>0&&native_holes>0);
}
static void test_underlay_and_retirement(void)
{
 start(2);const PlayerShipSpec *spec=&oracle_specs[2];
 /* A real earlier same-value write retires terrain before the body snapshot. */
 const PlayerShipWrite *first=spec->writes;
 unsigned first_off=(40+first->y)*320+48+first->x;
 store(first_off,17,MIRROR_NORMAL);CHECK(!tf.mask[first_off]);
 snapshot_underlay();draw(2);expect_pose(2);CHECK(pf.complete&&pf.valid);
 uint64_t before=render_mirror_player_fallback_status().retired;
 for(unsigned n=0;n<3;n++){
  const PlayerShipWrite *w=spec->writes+n;unsigned off=(40+w->y)*320+48+w->x;
  Uint8 value=n?((Uint8)(n==1?0x2f:0x3c)):((Uint8 *)fc_source_pixels)[off];
  store(off,value,(int)n);expected_mask[w->y*24+w->x]=0;CHECK(!pf.mask[w->y*24+w->x]);
 }
 CHECK(render_mirror_player_fallback_status().retired==before+3);
 /* Native-hole later write cannot acquire player ownership. */
 CHECK(!expected_mask[0]);store(40*320+48,44,MIRROR_BLEND);CHECK(!pf.mask[0]);
 finish();CHECK(pf.ready);present(2,true);
 start(2);successful_draw(2);
 for(unsigned n=0;n<spec->count;n++){const PlayerShipWrite *w=spec->writes+n;unsigned off=(40+w->y)*320+48+w->x;store(off,((Uint8 *)fc_source_pixels)[off],MIRROR_NORMAL);}
 memset(expected_mask,0,sizeof expected_mask);finish();CHECK(tf.ready&&!pf.ready&&!pf_cells());present(2,false);
}
static void test_sequences(void)
{
 /* First callback mutation / duplicate / suppressed / wrong style / unpaired. */
 for(unsigned mode=1;mode<=8;mode++){
  start(2);snapshot_underlay();callback_mode=mode;draw(2);expect_pose(2);finish();CHECK(!pf.ready);
  if(mode==1||mode==4||mode==5){CHECK(tf.ready);present(2,false);}else CHECK(!tf.ready);
 }
 start(2);pose_body(2);native_quad(2,3);pf_end();CHECK(!pf.valid);finish();CHECK(!pf.ready);
 start(2);pose_body(2);native_quad(2,4); /* Missing end cannot complete. */
 finish();CHECK(!pf.ready);CHECK(tf.ready);expect_pose(2);present(2,false);
 start(2);pf_end();CHECK(!pf.complete);finish();CHECK(!pf.ready);
 start(2);pf_pose(1,spriteSheet9,233,233,0);pf_pose(1,spriteSheet9,233,233,0);CHECK(!pf.valid);draw(2);finish();CHECK(!pf.ready);
 start(2);pose_body(2);pf_body(game_screen,48,40,spriteSheet9,233,MIRROR_NORMAL,1,233);CHECK(!pf.valid);native_quad(2,4);pf_end();finish();CHECK(!pf.ready);
 start(2);pose_body(2);native_quad(2,4);
 const PlayerShipWrite *w=oracle_specs[2].writes;store((40+w->y)*320+48+w->x,w->index,MIRROR_NORMAL);
 pf_end();CHECK(!pf.valid);finish();CHECK(!pf.ready);
 start(2);pose_body(2);const PlayerShipWrite *second=oracle_specs[2].writes+1;
 store((40+second->y)*320+48+second->x,second->index,MIRROR_NORMAL);CHECK(!pf.valid);
 start(2);pose_body(2);store(17,77,MIRROR_NORMAL);CHECK(!pf.valid); /* Unrelated store interrupts body. */
 start(2);successful_draw(2);pf_end();CHECK(pf.complete); /* Generic entity-end after completion is harmless. */
 finish();present(2,true);
}
static void test_admission(void)
{
 for(unsigned mode=0;mode<16;mode++){
  start(2);unsigned pnum=1;int base=233,index=233;unsigned invulnerable=0;Sprite2_array bank=spriteSheet9;
  switch(mode){
  case 0:unsetenv("BUILDING313_PLAYER_FALLBACK_ENABLE");pf_begin();break;
  case 1:setenv("BUILDING313_PLAYER_FALLBACK_ENABLE","true",1);pf_begin();break;
  case 2:setenv("PLAYER_SHIP_FAMILY_ENABLE","0",1);pf_begin();break;
  case 3:setenv("BUILDING313_TERRAIN_FALLBACK_ENABLE","0",1);pf_begin();break;
  case 4:pnum=2;break;case 5:base=231;break;case 6:index=232;break;
  case 7:invulnerable=player[0].invulnerable_ticks=1;break;
  case 8:invulnerable=1;break; /* 1 -> 0 must not enter normal path. */
  case 9:player[0].invulnerable_ticks=1;break;
  case 10:bank.data++;break;case 11:bank.size--;break;
  case 12:scope_ok=false;break;case 13:source_ok=false;break;case 14:palette_ok=false;break;
  case 15:fc.frame_active=false;break;
  }
  pf_pose(pnum,bank,base,index,invulnerable);pf_body(game_screen,48,40,bank,(unsigned)index,MIRROR_NORMAL,pnum,base);
  CHECK(!pf.active);native_quad(2,4);pf_end();finish();CHECK(!pf.ready);
 }
 for(unsigned style=MIRROR_SHADOW;style<=MIRROR_BLEND;style++){
  start(2);pf_pose(1,spriteSheet9,233,233,0);pf_body(game_screen,48,40,spriteSheet9,233,(int)style,1,233);CHECK(!pf.active);
  native_quad(2,4);pf_end();finish();CHECK(!pf.ready);
 }
 for(unsigned mode=0;mode<12;mode++){
  start(2);pf_pose(1,spriteSheet9,233,233,0);SDL_Surface *surface=game_screen;Sprite2_array bank=spriteSheet9;int x=48,y=40;unsigned index=233;
  switch(mode){
  case 0:x++;break;case 1:y++;break;case 2:index=235;break;case 3:surface=fc_output;break;
  case 4:bank.data++;break;case 5:bank.size--;break;case 6:++fc_session;break;
  case 7:++player[0].x;break;case 8:++player[0].y;break;case 9:player[0].invulnerable_ticks=1;break;
  case 10:((Uint8 *)fc_source_pixels)[0]^=1;break;case 11:ground_ok=false;break;
  }
  pf_body(surface,x,y,bank,index,MIRROR_NORMAL,1,233);CHECK(!pf.active);finish();CHECK(!pf.ready);
 }
}
static void test_resources_and_lifecycle(void)
{
 for(unsigned mode=0;mode<11;mode++){
  start(2);successful_draw(2);Uint8 *art=pf_art.rgba[2];
  switch(mode){
  case 0:art[17]^=1;break;case 1:pf_art.rgba[2]=oracle_art[2];break;
  case 2:pf.art=oracle_art[2];break;case 3:pf_art.valid=false;break;
  case 4:spriteSheet9.data[33300]^=1;break;case 5:spriteSheet9.data++;break;
  case 6:spriteSheet9.size--;break;case 7:setenv("PLAYER_SHIP_FAMILY_ASSET_DIR","other",1);break;
  case 8:scope_ok=false;break;case 9:palette_ok=false;break;case 10:++fc_session;break;
  }
  finish();CHECK(tf.ready&&!pf.ready);present(2,false);
  if(mode==0)art[17]^=1;
  pf_art.rgba[2]=art;pf_art.valid=true;
 }
 start(2);successful_draw(2);finish();CHECK(pf.ready);tf_reset();CHECK(!pf.ready&&!pf.complete&&!pf_cells());CHECK(!tf_present(renderer,fc_output,&destination));
 start(2);successful_draw(2);finish();CHECK(pf.ready);tf_begin();CHECK(!pf.ready&&!pf.complete&&!pf_cells());
 start(2);successful_draw(2);finish();CHECK(pf.ready);
 Uint8 *p=(Uint8 *)fc_source_pixels+17;b313_family_writer_store(fc_source,p,1,NWO_SPRITE2);*p=17;
 CHECK(!tf_pixel(fc_source,p,MIRROR_NORMAL));CHECK(!pf.ready&&!tf.ready);
 start(2);successful_draw(2);finish();CHECK(pf.ready);pf_release();CHECK(!pf.ready&&!pf_art.checked&&!pf_cells());
 start(2);successful_draw(2);finish();present(2,true); /* Re-load after release. */
}
static void test_cold_assets(int argc,char **argv)
{
 for(int i=2;i<argc;i++){
  pf_release();start(2);setenv("PLAYER_SHIP_FAMILY_ASSET_DIR",argv[i],1);
  snapshot_underlay();draw(2);expect_pose(2);CHECK(!pf.valid&&!pf.active&&!pf_art.valid);
  for(unsigned pose=0;pose<5;pose++)CHECK(!pf_art.rgba[pose]);
  finish();CHECK(tf.ready&&!pf.ready);present(2,false);
  /* A failed cache cannot revive merely because its root changes. */
  setenv("PLAYER_SHIP_FAMILY_ASSET_DIR",asset_root,1);CHECK(!pf.ready);
 }
 pf_release();start(2);successful_draw(2);finish();present(2,true);
}
static void test_bounds_and_shared_proofs(void)
{
 const int allowed[4][2]={{24,0},{264,0},{24,156},{264,156}};
 for(unsigned i=0;i<4;i++){
  start(2);int x=allowed[i][0],y=allowed[i][1];player[0].x=x+5;player[0].y=y+7;
  pf_pose(1,spriteSheet9,233,233,0);pf_body(game_screen,x,y,spriteSheet9,233,MIRROR_NORMAL,1,233);CHECK(pf.active);
  for(unsigned part=0;part<4;part++)blit_sprite2(game_screen,x+(int)(part%2)*12,y+(int)(part/2)*14,spriteSheet9,233+parts[part]);
  pf_end();CHECK(pf.complete&&pf.valid);finish();CHECK(pf.ready&&tf.ready);
  expect_player_present=true;CHECK(tf_present(renderer,fc_output,&destination));CHECK(!pf.ready&&!tf.ready);
 }
 const int rejected[4][2]={{23,40},{265,40},{48,-1},{48,157}};
 for(unsigned i=0;i<4;i++){
  start(2);int x=rejected[i][0],y=rejected[i][1];player[0].x=x+5;player[0].y=y+7;
  pf_pose(1,spriteSheet9,233,233,0);pf_body(game_screen,x,y,spriteSheet9,233,MIRROR_NORMAL,1,233);CHECK(!pf.active&&!pf.valid);
 }
 for(unsigned mode=0;mode<10;mode++){
  start(2);successful_draw(2);
  switch(mode){
  case 0:ground_ok=false;break;
  case 1:geometry_ok=false;break;
  case 2:fg.rgba[0][11]^=1;break;
  case 3:rgb_palette[1]^=1;break;
  case 4:((Uint8 *)fc_source_pixels)[123]^=1;break;
  case 5:b313_family_writer_unknown(fc_source,fc_source_pixels,1,NWO_UNKNOWN_WRITE);break;
  case 6:b313_family_writer_gap(NWO_GAP_UNREGISTERED);break;
  case 7:tf_finish(MIRROR_OUTPUT_ORDINARY);break; /* No crop. */
  case 8:crop();tf_finish(MIRROR_OUTPUT_UNSUPPORTED);break;
  case 9:crop();((Uint8 *)fc_output_pixels)[123]^=1;tf_finish(MIRROR_OUTPUT_ORDINARY);break;
  }
  if(mode<7)finish();
  CHECK(!pf.ready&&!tf.ready);CHECK(!tf_present(renderer,fc_output,&destination));
 }
 /* Initial subset explicitly requires surviving terrain; it is not a new
  * ship-only display permission even when the entire ship proof succeeds. */
 start(2);
 for(unsigned off=0;off<64000;off++)if(tf.mask[off])store(off,17,MIRROR_NORMAL);
 successful_draw(2);finish();CHECK(!tf_status.surviving_cells&&!tf.ready&&!pf.ready);
 CHECK(!tf_present(renderer,fc_output,&destination));
}
static void test_post_lock(void)
{
 for(unsigned mode=1;mode<=14;mode++){
  start(2);successful_draw(2);finish();CHECK(pf.ready);mutate_lock=mode;
  unsigned before=readbacks,locks=lock_calls;CHECK(!tf_present(renderer,fc_output,&destination));
  CHECK(readbacks==before&&lock_calls==locks+1&&!tf.ready&&!pf.ready);
 }
 for(unsigned mode=20;mode<=38;mode++){
  start(2);successful_draw(2);finish();CHECK(pf.ready);Uint8 *art=pf_art.rgba[2];mutate_lock=mode;present(2,false);
  if(mode==31)art[42]^=1;
  pf_art.rgba[2]=art;pf_art.valid=true;
 }
 /* Same-content aliasing and payload mutations after seal fail closed. */
 for(unsigned mode=0;mode<6;mode++){
  start(2);successful_draw(2);finish();CHECK(pf.ready);Uint8 *art=pf_art.rgba[2];
  switch(mode){
  case 0:art[42]^=1;break;case 1:pf_art.rgba[2]=oracle_art[2];break;
  case 2:pf.art=oracle_art[2];break;case 3:pf.patch[123]^=1;break;
  case 4:pf.mask[0]=1;break;case 5:pf.mask[pf.index%672]^=1;break;
  }
  present(2,false);if(mode==0)art[42]^=1;pf_art.rgba[2]=art;
 }
}
int main(int argc,char **argv)
{
 CHECK(argc>=3);asset_root=argv[1];CHECK(SDL_Init(SDL_INIT_VIDEO)==0);
 fc_source=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 fc_output=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 canvas=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 renderer=SDL_CreateSoftwareRenderer(screen);CHECK(fc_source&&fc_output&&canvas&&screen&&renderer);game_screen=VGAScreen=fc_source;destination=(SDL_Rect){0,0,2560,1600};
 for(unsigned i=0;i<10;i++){fg.rgba[i]=malloc(FG_RGBA_BYTES);CHECK(fg.rgba[i]);}
 for(unsigned pose=0;pose<5;pose++){
  char path[2048];CHECK(snprintf(path,sizeof path,"%s/ship-%u-8.hda",asset_root,oracle_specs[pose].index)>0);
  FILE *file=fopen(path,"rb");CHECK(file);Uint8 header[28];CHECK(fread(header,1,28,file)==28&&!memcmp(header,"HDR1",4));
  oracle_art[pose]=malloc(FG_RGBA_BYTES);CHECK(oracle_art[pose]);CHECK(fread(oracle_art[pose],1,FG_RGBA_BYTES,file)==FG_RGBA_BYTES&&fgetc(file)==EOF);CHECK(!fclose(file));
  CHECK(asteroid1_stamp(oracle_art[pose],FG_RGBA_BYTES)==oracle_specs[pose].stamp);
 }
 test_exact_five_poses();test_underlay_and_retirement();test_sequences();test_admission();test_resources_and_lifecycle();test_cold_assets(argc,argv);test_bounds_and_shared_proofs();test_post_lock();
 tf_release();for(unsigned i=0;i<10;i++)free(fg.rgba[i]);for(unsigned i=0;i<5;i++)free(oracle_art[i]);
 SDL_DestroyRenderer(renderer);SDL_FreeSurface(screen);SDL_FreeSurface(canvas);SDL_FreeSurface(fc_source);SDL_FreeSurface(fc_output);SDL_Quit();
 printf("PASS: player fallback %u assertions; five real HDA poses, native RLE/writer, SDL pixels, retirement, adversarial lifecycle and post-lock mutation\n",checks);
 return 0;
}
