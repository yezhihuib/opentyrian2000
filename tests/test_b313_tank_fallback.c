#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <limits.h>
#include <unistd.h>
#include <sys/stat.h>
#include "SDL.h"
#include "b313_family_writer.h"
#include "b313_terrain_fallback.h"
#include "b313_player_fallback.h"
#include "player_ship_family.h"
#include "tank194_family.h"
#include "b313_tank_fallback.h"
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
static bool expect_player_present;
static const char *tank_root;
static void tank_lock_mutation(unsigned mode);
static void descriptor_mutation(unsigned mode);
static struct {int x,y;unsigned invulnerable_ticks;} player[1];
static Sprite2_array spriteSheet9;
static uint64_t bank_pin;
static struct {bool enabled;} rp;
static struct {Uint8 *rgba[10];Uint8 ground_mask[64000];} fg;
static struct {bool enabled;Uint8 *rgba[12];Uint8 mask[64000];} fl;
static struct {bool enabled;Uint8 *rgba;Uint8 mask[64000];} fk,fs340;
static uint64_t fg_payload_pins[10],fg_cliff_payload_pins[12],fg_corner_payload_pin,fg_static340_payload_pin;
static uint64_t checks;
static unsigned readbacks,hud_calls,mutate_lock,lock_calls,callback_mode,callback_number;
static Uint8 *oracle_art[5];
static SDL_Renderer *renderer;
static SDL_Surface *renderer_screen;
static const char *asset_root;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAILED line %d: %s\n",__LINE__,#x);abort();}}while(0)
#include "player_ship_native.inc"
#include "player_fallback_helpers.inc"
#include "player_fallback_oracle.inc"
#include "tank_fallback_oracle.inc"
#include "tank_fallback_lifetime.inc"
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
static void kf_begin(void);
static void kf_reset(void);
static void kf_shared_fail(void);
static void kf_end(void);
static void kf_finish(void);
static void kf_release(void);
static void kf_pixel(unsigned,int);
static void kf_present_begin(uint32_t);
static void kf_present_end(void);
static uint32_t kf_compose(void);
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
#include "b313_tank_fallback_mirror.inc"

static void tank_readback(SDL_Renderer *r);
static void asset_debug_readback(SDL_Renderer *r){tank_readback(r);}
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
 if(mutate_lock>=100)tank_lock_mutation(mutate_lock);
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
static void render_mirror_sprite2_blend_pixel(SDL_Surface *s,Uint8 *p,Uint8 value,Sprite2_array bank,unsigned index,int x,int y)
{(void)bank;(void)index;(void)x;(void)y;render_mirror_pixel(s,p,value,MIRROR_BLEND);}
#define render_mirror_shadow_begin(...) ((void)0)
#define render_mirror_shadow_end() ((void)0)
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
/* Independent native/terrain/actor model. No expected ownership or colour is
 * read from kf/pf state, and the archived callback arrays are immutable inputs. */
static Uint8 *tank_oracle_art[8],model_native[64000],model_terrain[64000];
static struct {bool valid;unsigned pose;int x,y;Uint8 mask[672];Uint32 patch[43008];} model[26];
static Uint8 sampled_mask[672];
static Uint32 sampled_patch[43008],readback[43008];
static uint32_t wanted_slots;
static unsigned alpha_zero,alpha_partial,alpha_full,model_holes;
static Uint16 tank_encoded[23102];
static uint64_t fixture_identity=10;
static void model_retire(unsigned off,Uint8 value)
{
 unsigned x=off%320,y=off/320;
 for(unsigned a=0;a<26;a++)if(model[a].valid&&(int)x>=model[a].x&&(int)x<model[a].x+24&&(int)y>=model[a].y&&(int)y<model[a].y+28)
  model[a].mask[(y-(unsigned)model[a].y)*24+x-(unsigned)model[a].x]=0;
 model_terrain[off]=0;model_native[off]=value;
}
static Uint32 independent_blend(Uint32 before,const Uint8 *rgba)
{
 Uint32 result=UINT32_C(0xff000000);unsigned alpha=rgba[3];
 for(unsigned c=0;c<3;c++)result|=(((((before>>(16-c*8))&255)*(255-alpha)+rgba[c]*alpha+127)/255)<<(16-c*8));
 return result;
}
static void model_actor(unsigned a,unsigned pose,int x,int y,bool admitted)
{
 model[a].valid=admitted;model[a].pose=pose;model[a].x=x;model[a].y=y;memset(model[a].mask,0,672);
 for(unsigned ly=0;ly<28;ly++)for(unsigned lx=0;lx<24;lx++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  unsigned off=(y+(int)ly)*320+x+lx,n=(ly*8+sy)*192+lx*8+sx;
  model[a].patch[n]=model_terrain[off]?terrain_color(x+lx,y+ly,sx,sy):color(model_native[off]);
 }
 for(unsigned part=0;part<4;part++){
  unsigned begin=a==25?(part?oracle_specs[pose].ends[part-1]:0):0;
  unsigned end=a==25?oracle_specs[pose].ends[part]:oracle_tank_counts[pose][part];
  for(unsigned n=begin;n<end;n++){
   unsigned lx,ly,index;
   if(a==25){const PlayerShipWrite *w=oracle_specs[pose].writes+n;lx=w->x;ly=w->y;index=w->index;}
   else{const Tank194Write *w=&oracle_tank_native[pose][part][n];lx=oracle_tank_px[part]+w->x;ly=oracle_tank_py[part]+w->y;index=w->index;}
   unsigned off=(y+(int)ly)*320+x+lx;model_retire(off,(Uint8)index);
   if(!admitted)continue;
   model[a].mask[ly*24+lx]=1;
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    unsigned ax=lx*8+sx,ay=ly*8+sy,at=ay*192+ax;
    const Uint8 *art=a==25?oracle_art[pose]+at*4:tank_oracle_art[pose]+at*4;
    model[a].patch[at]=independent_blend(model[a].patch[at],art);
    alpha_zero+=art[3]==0;alpha_partial+=art[3]>0&&art[3]<255;alpha_full+=art[3]==255;
   }
  }
 }
 for(unsigned n=0;n<672;n++)model_holes+=!model[a].mask[n];
}
static void tank_readback(SDL_Renderer *r)
{
 CHECK(r==renderer&&render_mirror_terrain_fallback_status().presenting);
 B313TankFallbackStatus s=render_mirror_tank_fallback_status();
 if(s.presented_slots!=wanted_slots)fprintf(stderr,"Present mutation=%u wanted=%u got=%u reasons=%u,%u\n",mutate_lock,wanted_slots,s.presented_slots,kf.draw[0].reason,kf.draw[1].reason);
 CHECK(s.presenting==(wanted_slots!=0));CHECK(s.presented_slots==wanted_slots);
 for(unsigned a=0;a<25;a++){
  bool selected=(wanted_slots&(UINT32_C(1)<<a))!=0;CHECK(s.draw[a].presenting==selected);
  CHECK(render_mirror_tank_fallback_sample(a+75,sampled_mask,672,sampled_patch,43008)==selected);
  if(selected){
   CHECK(!memcmp(sampled_mask,model[a].mask,672));
   for(unsigned n=0;n<43008;n++)if(model[a].mask[(n/192/8)*24+(n%192/8)])CHECK(sampled_patch[n]==model[a].patch[n]);
  }
 }
 CHECK(!render_mirror_tank_fallback_sample(74,sampled_mask,672,sampled_patch,43008));
 CHECK(!render_mirror_tank_fallback_sample(100,sampled_mask,672,sampled_patch,43008));
 CHECK(!render_mirror_tank_fallback_sample(75,sampled_mask,671,sampled_patch,43008));
 CHECK(!render_mirror_tank_fallback_sample(75,sampled_mask,672,sampled_patch,43007));
 CHECK(!render_mirror_tank_fallback_sample(75,NULL,672,sampled_patch,43008));
 CHECK(!render_mirror_tank_fallback_sample(75,sampled_mask,672,NULL,43008));
 CHECK(render_mirror_player_fallback_status().presenting==expect_player_present);
 if(expect_player_present){CHECK(render_mirror_player_fallback_sample(sampled_mask,672,sampled_patch,43008));CHECK(!memcmp(sampled_mask,model[25].mask,672));}
 ++readbacks;
}
static void verify_region(int x,int y)
{
 SDL_Rect rect={(x-24)*8,y*8,192,224};CHECK(SDL_RenderReadPixels(renderer,&rect,SDL_PIXELFORMAT_ARGB8888,readback,192*4)==0);
 for(unsigned ly=0;ly<28;ly++)for(unsigned lx=0;lx<24;lx++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  unsigned nx=x+lx,ny=y+ly,off=ny*320+nx,n=(ly*8+sy)*192+lx*8+sx;
  Uint32 want=model_terrain[off]?terrain_color(nx,ny,sx,sy):color(model_native[off]);unsigned owners=0;
  for(unsigned a=0;a<26;a++)if(model[a].valid&&(a==25?expect_player_present:(wanted_slots&(UINT32_C(1)<<a)))&&
      (int)nx>=model[a].x&&(int)nx<model[a].x+24&&(int)ny>=model[a].y&&(int)ny<model[a].y+28){
   unsigned ax=nx-(unsigned)model[a].x,ay=ny-(unsigned)model[a].y;
   if(model[a].mask[ay*24+ax]){want=model[a].patch[(ay*8+sy)*192+ax*8+sx];++owners;}
  }
  CHECK(owners<=1);CHECK(readback[n]==want);
  CHECK(((Uint32 *)tf.result->pixels)[(ny*8+sy)*2560+(nx-24)*8+sx]==want);
 }
}
static void present_models(uint32_t slots,bool player_used)
{
 wanted_slots=slots;expect_player_present=player_used;unsigned before=readbacks;
 CHECK(tf.ready);CHECK(tf_present(renderer,fc_output,&destination));CHECK(readbacks==before+1&&!tf.ready);
 for(unsigned a=0;a<25;a++)CHECK(!render_mirror_tank_fallback_sample(a+75,sampled_mask,672,sampled_patch,43008));
 verify_region(48,40);verify_region(52,43);
 CHECK(!tf_present(renderer,fc_output,&destination));CHECK(readbacks==before+1);
}
static void make_tank_bank(void)
{
 Uint8 *data=(Uint8 *)tank_encoded;memset(data,0,sizeof tank_encoded);unsigned at=600;
 for(unsigned pose=0;pose<8;pose++)for(unsigned part=0;part<4;part++){
  unsigned tile=oracle_tank_bases[pose]+oracle_tank_parts[part];data[(tile-1)*2]=(Uint8)at;data[(tile-1)*2+1]=(Uint8)(at>>8);
  for(unsigned row=0;row<14;row++){
   unsigned cursor=0;
   for(unsigned n=0;n<oracle_tank_counts[pose][part];n++){
    const Tank194Write *w=&oracle_tank_native[pose][part][n];if(w->y!=row)continue;
    CHECK(w->x>=cursor&&w->x<12);data[at++]=(Uint8)(0x10+w->x-cursor);data[at++]=w->index;cursor=w->x+1;
   }
   data[at++]=(Uint8)(12-cursor);
  }
  data[at++]=0x0f;
 }
 CHECK(at<sizeof tank_encoded);enemySpriteSheets[0]=(Sprite2_array){data,sizeof tank_encoded};enemySpriteSheetIds[0]=20;
 synthetic_tank_bank_pin=asteroid1_stamp(data,sizeof tank_encoded);
}
static void receipt(unsigned slot,unsigned pose,unsigned event,int x,int y,bool replacement)
{
 if(replacement)++fixture_identity;
 memset(enemy+slot,0,sizeof enemy[slot]);struct JE_SingleEnemyType *e=enemy+slot;
 e->sprite2s=enemySpriteSheets;e->enemydatofs=enemyDat+194;e->enemytype=194;e->size=1;
 e->enemycycle=pose+1;e->ani=8;e->animin=1;e->armorleft=30;e->evalue=50;e->exrev=e->eyrev=100;e->explonum=1;
 e->exccadd=e->eyccadd=e->exca=e->eyca=-1;e->xminbounce=e->yminbounce=-10000;e->xmaxbounce=e->ymaxbounce=10000;
 e->ex=x+6;e->ey=y+7;for(unsigned i=0;i<3;i++)e->tur[i]=i+2;for(unsigned i=0;i<8;i++)e->egr[i]=oracle_tank_bases[i];
 memset(t194_slots+slot,0,sizeof t194_slots[slot]);
 t194_slots[slot].live=t194_slots[slot].initialized=true;t194_slots[slot].generation=t194_slots[slot].witness=fixture_identity;
 t194_slots[slot].bank=enemySpriteSheets;t194_slots[slot].data=enemySpriteSheets[0].data;t194_slots[slot].bytes=enemySpriteSheets[0].size;
 t194_slots[slot].birth=(Tank194Birth){.epoch=t194_life.epoch,.token=fixture_identity,.generation=fixture_identity,.event=event,.slot=slot,.record=194,.bank_role=20,.bank_bytes=46204,.bank_object=(uintptr_t)enemySpriteSheets,.bank_data=(uintptr_t)enemySpriteSheets[0].data,.live=true,.initialized=true};
 t194_slots[slot].birth_value=50;t194_slots[slot].birth_armor=30;t194_slots[slot].script=t194_script(slot);enemyAvail[slot]=0;
 CHECK(t194_witness(slot)&&t194_shape(slot,0));
}
static void tank_start(void)
{
 setenv("BUILDING313_TANK_FALLBACK_ENABLE","1",1);setenv("TANK194_FAMILY_ENABLE","1",1);setenv("BUILDING313_FAMILY_CANVAS_ENABLE","1",1);setenv("TANK194_FAMILY_ASSET_DIR",tank_root,1);
 start(2);tank_scope_ok=true;make_tank_bank();
 for(unsigned i=0;i<COUNTOF(oracle_tank_palette);i++)rgb_palette[oracle_tank_palette[i].index]=oracle_tank_palette[i].rgb;
 for(unsigned n=0;n<258;n++){
  const int *d=oracle_tank_events[n].d;fixture_events[n]=(struct JE_EventRecType){oracle_tank_events[n].time,oracle_tank_events[n].type,d[0],d[1],d[2],d[3],d[4],d[5]};
 }
 memset(t194_slots,0,sizeof t194_slots);memset(&t194_life,0,sizeof t194_life);t194_life.epoch=++fixture_identity;t194_life.loaded=true;t194_life.events=fixture_events;t194_life.next_event=7;t194_life.consumed=6;strcpy(t194_life.root,tank_root);
 memset(model,0,sizeof model);memset(model_native,17,sizeof model_native);memset(model_terrain,0,sizeof model_terrain);
 for(unsigned y=38;y<70;y++)for(unsigned x=46;x<80;x++)if(terrain_cell(x,y)){
  fg.ground_mask[y*320+x]=model_terrain[y*320+x]=1;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)((Uint32 *)canvas->pixels)[(y*8+sy)*2560+x*8+sx]=terrain_color(x,y,sx,sy);
 }
 tf_reset();tf_begin();tf_capture();CHECK(tf.valid&&tf.captured);
 receipt(75,0,6,48,40,true);receipt(76,1,25,52,43,true);
}
static void tank_part(unsigned slot,unsigned pose,unsigned part,int x,int y,int filter)
{
 render_mirror_tank_fallback_tile_begin(game_screen,slot,x+(int)oracle_tank_px[part],y+(int)oracle_tank_py[part],enemySpriteSheets,oracle_tank_bases[pose],(int)oracle_tank_parts[part],filter);
 if(filter)blit_sprite2_filter(game_screen,x+(int)oracle_tank_px[part],y+(int)oracle_tank_py[part],enemySpriteSheets[0],oracle_tank_bases[pose]+oracle_tank_parts[part],(Uint8)filter);
 else blit_sprite2(game_screen,x+(int)oracle_tank_px[part],y+(int)oracle_tank_py[part],enemySpriteSheets[0],oracle_tank_bases[pose]+oracle_tank_parts[part]);
 kf_end();
}
static void tank_draw(unsigned slot,unsigned pose,int x,int y,bool admitted)
{
 model_actor(slot-75,pose,x,y,admitted);
 for(unsigned part=0;part<4;part++)tank_part(slot,pose,part,x,y,0);
}
static void tank_phase(void){render_mirror_tank_fallback_phase_begin();}
static void tank_phase_end(void){render_mirror_tank_fallback_phase_end();}
static void player_draw(bool admitted)
{model_actor(25,2,48,40,admitted);draw(2);}
static void model_store(unsigned off,Uint8 value,int style)
{model_retire(off,value);store(off,value,style);}
static void test_eight_poses_and_births(void)
{
 for(unsigned pose=0;pose<8;pose++){
  tank_start();receipt(75,pose,6,48,40,true);fc.frame_failed=true;
  tank_phase();tank_draw(75,pose,48,40,true);tank_phase_end();CHECK(kf.draw[0].complete&&kf.draw[0].valid);
  CHECK(kf.draw[0].draw.callback_count==oracle_tank_totals[pose]);CHECK(!memcmp(kf.draw[0].mask,model[0].mask,672));
  finish();CHECK(kf.draw[0].ready&&tf.ready);present_models(1,false);
 }
 CHECK(alpha_zero&&alpha_partial&&alpha_full&&model_holes);
 const unsigned births[18]={6,25,26,36,37,76,77,78,89,90,91,177,208,209,210,211,246,247};
 for(unsigned n=0;n<18;n++){
  tank_start();receipt(75,n%8,births[n],48,40,true);tank_phase();tank_draw(75,n%8,48,40,true);tank_phase_end();finish();CHECK(kf.draw[0].ready);present_models(1,false);
 }
 for(unsigned slot=75;slot<100;slot++){
  tank_start();receipt(slot,0,6,48,40,true);tank_phase();tank_draw(slot,0,48,40,true);tank_phase_end();finish();CHECK(kf.draw[slot-75].ready);present_models(UINT32_C(1)<<(slot-75),false);
 }
}
static void test_cross_actor_retirement(void)
{
 /* All orderings use native/terrain-only alpha underlays, never earlier actor
  * HD patches. Later native stores retire every earlier actor at their cells. */
 tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_draw(76,1,52,43,true);tank_phase_end();finish();present_models(3,false);
 tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();player_draw(true);finish();present_models(1,true);
 tank_start();player_draw(true);tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();present_models(1,true);
 for(unsigned style=0;style<3;style++){
  tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();
  const Tank194Write *w=&oracle_tank_native[0][0][0];unsigned off=(40+w->y)*320+48+w->x;
  model_store(off,model_native[off],(int)style);CHECK(!kf.draw[0].mask[w->y*24+w->x]);
  model_store(40*320+48,44,(int)style);CHECK(!kf.draw[0].mask[0]);
  finish();present_models(1,false);
 }
 tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();
 SDL_Rect rect={53,44,3,3};uint64_t token=b313_family_writer_fill_before(fc_source,&rect,NWO_SDL_VGA_FILL);CHECK(token);
 int result=SDL_FillRect(fc_source,&rect,17);b313_family_writer_fill_after(token,result);CHECK(!result);CHECK(b313_family_writer_rect_begin(fc_source,&rect));
 for(int y=rect.y;y<rect.y+rect.h;y++)for(int x=rect.x;x<rect.x+rect.w;x++){unsigned off=(unsigned)y*320+(unsigned)x;model_retire(off,17);CHECK(tf_pixel(fc_source,(Uint8 *)fc_source_pixels+off,MIRROR_NORMAL));}
 CHECK(b313_family_writer_rect_end(fc_source));finish();present_models(1,false);
}
static void test_real_native_effects(void)
{
 for(unsigned style=0;style<3;style++){
  tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();
  for(unsigned n=0;n<oracle_tank_counts[0][0];n++){
   const Tank194Write *w=&oracle_tank_native[0][0][n];unsigned off=(40+w->y)*320+48+w->x;
   Uint8 before=model_native[off],value=style==MIRROR_NORMAL?w->index:style==MIRROR_BLEND?
    (Uint8)((((w->index&15)+(before&15))/2)|(w->index&240)):(Uint8)((before&240)+(before&15)/2);
   model_retire(off,value);
  }
  if(style==MIRROR_NORMAL)blit_sprite2(game_screen,48,40,enemySpriteSheets[0],13);
  else if(style==MIRROR_BLEND)blit_sprite2_blend(game_screen,48,40,enemySpriteSheets[0],13);
  else blit_sprite2_darken(game_screen,48,40,enemySpriteSheets[0],13);
  finish();present_models(1,false);
 }
 /* Simultaneously active acquisition cannot smuggle a second independent
  * transaction through the callback stream. Neither may keep mixed writes. */
 tank_start();tank_phase();pose_body(2);CHECK(pf.active);
 tank_draw(75,0,48,40,false);tank_phase_end();CHECK(!kf.draw[0].valid&&!pf.valid);finish();present_models(0,false);
}
static void test_local_sequences(void)
{
 for(unsigned mode=0;mode<8;mode++){
  tank_start();tank_phase();model_actor(0,0,48,40,false);
  if(mode==0){for(unsigned p=0;p<3;p++)tank_part(75,0,p,48,40,0);} /* Missing part. */
  if(mode==1){tank_part(75,0,1,48,40,0);tank_part(75,0,0,48,40,0);} /* Reordered. */
  if(mode==2){tank_part(75,0,0,48,40,0);tank_part(75,0,0,48,40,0);} /* Duplicate. */
  if(mode==3){tank_draw(75,0,48,40,false);tank_part(75,0,3,48,40,0);} /* Extra. */
  if(mode==4){tank_part(75,0,0,48,40,0);model_store(17,77,MIRROR_NORMAL);} /* Between parts. */
  if(mode==5){render_mirror_tank_fallback_tile_begin(game_screen,75,48,40,enemySpriteSheets,13,0,0);blit_sprite2(game_screen,48,40,enemySpriteSheets[0],13);} /* Missing end. */
  if(mode==6){callback_mode=4;for(unsigned p=0;p<4;p++)tank_part(75,0,p,48,40,0);callback_mode=0;} /* Wrong style. */
  if(mode==7){tank_part(75,0,0,48,40,1);} /* Filtered genuine call. */
  /* Incomplete operations intentionally leave different final native images;
   * model those from real known input stores but never grant them HD ownership. */
  memcpy(model_native,fc_source_pixels,64000);memcpy(model_terrain,tf.mask,64000);
  tank_draw(76,1,52,43,true);tank_phase_end();CHECK(!kf.draw[0].valid&&kf.draw[1].complete);
  player_draw(true);finish();CHECK(!kf.draw[0].ready&&kf.draw[1].ready&&pf.ready);present_models(2,true);
 }
 /* Shared ledger failures revoke every tank, including already completed. */
 for(unsigned mode=1;mode<=8;mode++){
  if(mode==1||mode==4||mode==5)continue;
  tank_start();tank_phase();tank_draw(76,1,52,43,true);callback_mode=mode;callback_number=0;tank_draw(75,0,48,40,false);tank_phase_end();finish();CHECK(!tf.ready&&!kf.draw[1].ready);
 }
 tank_start();tank_draw(75,0,48,40,false);finish();CHECK(!kf.draw[0].ready);present_models(0,false);
 tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_phase();finish();CHECK(!kf.draw[0].ready);present_models(0,false);
 tank_start();tank_phase();tank_draw(75,0,48,40,true);finish();CHECK(!kf.draw[0].ready);present_models(0,false);
}
static void restart_same_identity(bool release)
{
 if(release)tf_release();else tf_reset();b313_family_writer_reset();++fc_frame;++fc_generation;fc.frame_failed=false;
 memset(fc_source_pixels,17,64000);memset(fc_output_pixels,17,64000);memset(model,0,sizeof model);memset(model_native,17,64000);
 for(unsigned off=0;off<64000;off++)model_terrain[off]=fg.ground_mask[off];
 CHECK(b313_family_writer_begin(fc_frame,fc_source,fc_output));tf_begin();tf_capture();CHECK(tf.valid);
}
static void test_sticky_identity(void)
{
 for(unsigned boundary=0;boundary<4;boundary++){
  tank_start();tank_phase();enemy[75].filter=1;tank_draw(75,0,48,40,false);tank_phase_end();CHECK(kf_denied[0].valid);enemy[75].filter=0;
  restart_same_identity(boundary>=2);if(boundary==1){fc.frame_failed=true;fc.ready=false;}
  if(boundary==3){SDL_DestroyRenderer(renderer);renderer=SDL_CreateSoftwareRenderer(renderer_screen);CHECK(renderer);}
  tank_phase();tank_draw(75,0,48,40,false);tank_draw(76,1,52,43,true);tank_phase_end();finish();CHECK(!kf.draw[0].ready&&kf.draw[1].ready);present_models(2,false);
  restart_same_identity(false);receipt(75,0,6,48,40,true);tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();CHECK(!kf_denied[0].valid&&kf.draw[0].ready);present_models(1,false);
 }
}
static void test_sticky_post_draw_loss(void)
{
 for(unsigned mode=0;mode<3;mode++){
  tank_start();uint64_t generation=t194_slots[75].generation,token=t194_slots[75].birth.token;
  tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();CHECK(kf.draw[0].ready);
  mutate_lock=mode==0?101:mode==1?102:103;present_models(0,false);CHECK(kf_denied[0].valid);
  t194_slots[75].generation=generation;t194_slots[75].birth.token=token;t194_slots[75].script_serial=0;mutate_lock=0;
  restart_same_identity(false);tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();CHECK(!kf.draw[0].ready);present_models(0,false);
  /* Token-only and generation-only replacements are not a new verified birth. */
  restart_same_identity(false);t194_slots[75].birth.token=token+1;tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();present_models(0,false);
  t194_slots[75].birth.token=token;
  restart_same_identity(false);t194_slots[75].generation=t194_slots[75].witness=t194_slots[75].birth.generation=generation+1;
  tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();present_models(0,false);
  restart_same_identity(false);receipt(75,0,6,48,40,true);tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();CHECK(kf.draw[0].ready);present_models(1,false);
 }
}
static void test_admission_and_bounds(void)
{
 for(unsigned mode=0;mode<16;mode++){
  tank_start();tank_phase();
  switch(mode){
  case 0:t194_slots[75].live=false;break;case 1:t194_slots[75].witness++;break;case 2:t194_slots[75].birth.epoch++;break;
  case 3:t194_slots[75].birth.event=248;break;case 4:enemyAvail[75]=1;break;case 5:enemy[75].enemytype=193;break;
  case 6:enemy[75].size=0;break;case 7:enemy[75].enemycycle=9;break;case 8:enemy[75].scoreitem=1;break;
  case 9:enemySpriteSheets[0].data[44000]^=1;break;case 10:enemySpriteSheetIds[0]=19;break;
  case 11:fixture_events[257].eventtime++;break;case 12:t194_life.stream_broken=true;break;
  case 13:t194_life.exhausted=true;break;case 14:t194_life.loaded=false;break;case 15:enemy[75].exc++;break;
  }
  tank_draw(75,0,48,40,false);tank_phase_end();finish();CHECK(!kf.draw[0].ready);present_models(0,false);
 }
 const int allowed[4][2]={{24,0},{264,0},{24,156},{264,156}};
 for(unsigned n=0;n<4;n++){
  tank_start();int x=allowed[n][0],y=allowed[n][1];receipt(75,0,6,x,y,true);tank_phase();tank_draw(75,0,x,y,true);tank_phase_end();finish();CHECK(kf.draw[0].ready);
  wanted_slots=1;expect_player_present=false;CHECK(tf_present(renderer,fc_output,&destination));verify_region(x,y);
 }
 const int rejected[4][2]={{23,40},{265,40},{48,-1},{48,157}};
 for(unsigned n=0;n<4;n++){
  tank_start();int x=rejected[n][0],y=rejected[n][1];receipt(75,0,6,x,y,true);tank_phase();
  render_mirror_tank_fallback_tile_begin(game_screen,75,x,y,enemySpriteSheets,13,0,0);CHECK(!kf.draw[0].active&&!kf.draw[0].ready);
 }
}
static void tank_lock_mutation(unsigned mode)
{
 if(mode>=200){descriptor_mutation(mode-200);return;}
 switch(mode){
 case 100:enemy[75].filter=1;break;case 101:t194_slots[75].generation++;break;case 102:t194_slots[75].birth.token++;break;
 case 103:t194_slots[75].script_serial++;break;case 104:enemySpriteSheets[0].data[44000]^=1;break;
 case 105:kf_art.rgba[0][42]^=1;break;case 106:kf_art.rgba[0]=tank_oracle_art[0];break;
 case 107:kf.draw[0].patch[123]^=1;break;case 108:kf.draw[0].mask[0]=1;break;
 case 109:setenv("TANK194_FAMILY_ASSET_DIR","other",1);break;case 110:kf_art.valid=false;break;
 case 111:enemy[75].enemycycle=2;break;case 112:t194_life.stream_broken=true;break;
 }
}
static void test_post_lock_and_resources(int argc,char **argv)
{
 for(unsigned mode=1;mode<=14;mode++){
  tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_draw(76,1,52,43,true);tank_phase_end();finish();CHECK(kf.draw[0].ready&&kf.draw[1].ready);
  mutate_lock=mode;unsigned before=readbacks;CHECK(!tf_present(renderer,fc_output,&destination));CHECK(readbacks==before&&!tf.ready&&!kf.draw[0].ready&&!kf.draw[1].ready);
 }
 for(unsigned mode=100;mode<=112;mode++){
  tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_draw(76,1,52,43,true);tank_phase_end();player_draw(true);finish();CHECK(kf.draw[0].ready&&kf.draw[1].ready&&pf.ready);
  Uint8 *art=kf_art.rgba[0];mutate_lock=mode;
  bool all_tanks=mode==104||mode==105||mode==106||mode==109||mode==110||mode==112;
  present_models(all_tanks?0:2,true);
  if(mode==105)art[42]^=1;
  kf_art.rgba[0]=art;kf_art.valid=true;
 }
 for(int n=3;n<argc;n++){
  kf_release();tank_start();setenv("TANK194_FAMILY_ASSET_DIR",argv[n],1);strcpy(t194_life.root,argv[n]);
  tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();CHECK(!kf.draw[0].ready&&!kf_art.valid);
  for(unsigned p=0;p<8;p++)CHECK(!kf_art.rgba[p]);
  present_models(0,false);
 }
 kf_release();tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();present_models(1,false);
}
/* Regressions independently found after the original matrix: semantic actor
 * drift, mutable sealed descriptors, and denial receipt rollback. */
static void test_semantic_type_stays_denied(void)
{
 for(unsigned late=0;late<2;late++){
  tank_start();tank_phase();model_actor(0,0,48,40,false);
  if(late)tank_part(75,0,0,48,40,0);
  enemy[75].enemytype=193;
  for(unsigned part=late;part<4;part++)tank_part(75,0,part,48,40,0);
  CHECK(kf_denied[0].valid&&!kf.draw[0].ready);
  tank_draw(76,1,52,43,true);tank_phase_end();player_draw(true);finish();present_models(2,true);
  enemy[75].enemytype=194;restart_same_identity(false);tank_phase();
  tank_draw(75,0,48,40,false);tank_phase_end();finish();CHECK(!kf.draw[0].ready&&kf_denied[0].valid);present_models(0,false);
  restart_same_identity(false);receipt(75,0,6,48,40,true);tank_phase();tank_draw(75,0,48,40,true);
  tank_phase_end();finish();CHECK(kf.draw[0].ready&&!kf_denied[0].valid);present_models(1,false);
 }
}
static void test_semantics_after_frame_rejection(void)
{
 for(unsigned rejection=0;rejection<3;rejection++)for(unsigned semantic=0;semantic<4;semantic++){
  tank_start();CHECK(kf_load());tank_phase();
  if(rejection==0)tank_part(75,0,1,48,40,0); /* Initial part order failure. */
  if(rejection==1){
   enemy[75].ex=29;render_mirror_tank_fallback_tile_begin(game_screen,75,23,40,enemySpriteSheets,13,0,0);enemy[75].ex=54;
  }
  if(rejection==2){
   kf_art.valid=false;render_mirror_tank_fallback_tile_begin(game_screen,75,48,40,enemySpriteSheets,13,0,0);kf_art.valid=true;
  }
  CHECK(kf.draw[0].seen&&!kf.draw[0].valid&&!kf_denied[0].valid);
  if(semantic==0)enemy[75].filter=1;
  if(semantic==1)enemySpriteSheets[0].data[44000]^=1;
  if(semantic==2)enemy[75].scoreitem=1;
  if(semantic==3)enemy[75].enemytype=193;
  render_mirror_tank_fallback_tile_begin(game_screen,75,48,40,enemySpriteSheets,13,0,semantic==0?1:0);
  CHECK(kf_denied[0].valid&&!kf.draw[0].valid);
  enemy[75].filter=0;enemy[75].scoreitem=0;enemy[75].enemytype=194;
  if(semantic==1)enemySpriteSheets[0].data[44000]^=1;
  tank_phase_end();restart_same_identity(false);tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();
  CHECK(!kf.draw[0].ready);present_models(0,false);
  restart_same_identity(false);receipt(75,0,6,48,40,true);tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();
  CHECK(kf.draw[0].ready&&!kf_denied[0].valid);present_models(1,false);
 }
}
static void descriptor_mutation(unsigned mode)
{
 Tank194Draw *d=&kf.draw[0].draw;
 switch(mode){
 case 0:d->x++;break;case 1:d->y++;break;
 case 2:d->x=23;break;case 3:d->x=265;break;case 4:d->y=-1;break;case 5:d->y=157;break;
 case 6:d->x=INT_MIN;break;case 7:d->x=INT_MAX;break;case 8:d->y=INT_MIN;break;case 9:d->y=INT_MAX;break;
 case 10:d->frame++;break;case 11:d->epoch++;break;case 12:d->token++;break;case 13:d->generation++;break;
 case 14:d->script_serial++;break;case 15:d->slot=74;break;case 16:d->slot=100;break;case 17:d->slot=76;break;
 case 18:d->event++;break;case 19:d->record++;break;case 20:d->base++;break;case 21:d->pose=8;break;
 case 22:d->cur_loc++;break;case 23:d->bank_role++;break;case 24:d->bank_bytes--;break;
 case 25:d->bank_object++;break;case 26:d->bank_data++;break;case 27:d->script_event++;break;
 case 28:d->mask^=1;break;case 29:d->next++;break;case 30:d->callback_count++;break;
 case 31:d->part_count[0]++;break;case 32:d->part_order[0]++;break;case 33:d->complete=false;break;
 default:CHECK(false);
 }
}
static void test_sealed_descriptor_is_immutable(void)
{
 for(unsigned mode=0;mode<34;mode++){
  /* Direct compose is forbidden to write even one byte for a changed proof,
   * including otherwise-valid +1 origins and extreme out-of-bounds origins. */
  tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();CHECK(kf.draw[0].ready);
  descriptor_mutation(mode);uint64_t before=asteroid1_stamp(tf.result->pixels,16384000);
  CHECK(!kf_sealed_current(kf.draw));CHECK(kf_compose()==0);
  CHECK(asteroid1_stamp(tf.result->pixels,16384000)==before);present_models(0,false);
  /* Repeat at the actual SDL lock boundary with another tank and the player:
   * descriptor loss must remain local and must not write through bad bounds. */
  tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_draw(76,1,52,43,true);tank_phase_end();player_draw(true);finish();
  CHECK(kf.draw[0].ready&&kf.draw[1].ready&&pf.ready);mutate_lock=200+mode;present_models(2,true);
 }
}
static void test_acquisition_binding_before_seal(void)
{
 for(unsigned mode=0;mode<7;mode++){
  tank_start();tank_phase();tank_draw(75,0,48,40,true);tank_draw(76,1,52,43,true);tank_phase_end();player_draw(true);
  CHECK(kf.draw[0].complete&&kf.draw[1].complete&&pf.complete);
  switch(mode){
  case 0:kf.draw[0].draw.x++;break;
  case 1:kf.draw[0].draw.y++;break;
  case 2:kf.draw[0].draw.cur_loc++;break;
  case 3:kf.draw[0].origin.x++;break;
  case 4:kf.draw[0].origin_stamp^=1;break;
  case 5:kf.draw[0].draw.x++;kf.draw[0].origin.x++;break;
  case 6:kf.draw[0].origin.token++;break;
  }
  /* A finish-time hash of already-mutated state cannot replace an immutable
   * acquisition binding. Reject this slot before sealing anything for it. */
  finish();CHECK(!kf.draw[0].ready&&kf.draw[1].ready&&pf.ready);present_models(2,true);
 }
}
static void install_receipt_identity(uint64_t epoch,uint64_t generation,uint64_t token)
{
 t194_life.epoch=t194_slots[75].birth.epoch=epoch;
 t194_slots[75].generation=t194_slots[75].witness=t194_slots[75].birth.generation=generation;
 t194_slots[75].birth.token=token;
}
static void test_denial_componentwise_high_water(void)
{
 /* Every mixed-coordinate rollback: no earlier epoch, generation or token
  * can overwrite a higher denied coordinate when another coordinate rises. */
 const int deltas[7][3]={{-1,-1,-1},{1,-1,-1},{-1,1,-1},{-1,-1,1},{1,-1,1},{-1,1,1},{1,1,-1}};
 for(unsigned mode=0;mode<7;mode++){
  tank_start();uint64_t epoch=t194_life.epoch,generation=t194_slots[75].generation,token=t194_slots[75].birth.token;
  tank_phase();enemy[75].filter=1;tank_draw(75,0,48,40,false);tank_phase_end();finish();CHECK(kf_denied[0].valid);present_models(0,false);
  CHECK(kf_denied[0].epoch==epoch&&kf_denied[0].generation==generation&&kf_denied[0].token==token);
  restart_same_identity(false);
  uint64_t candidate_epoch=epoch+deltas[mode][0],candidate_generation=generation+deltas[mode][1],candidate_token=token+deltas[mode][2];
  install_receipt_identity(candidate_epoch,candidate_generation,candidate_token);enemy[75].filter=1;
  tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();present_models(0,false);
  uint64_t high_epoch=epoch>candidate_epoch?epoch:candidate_epoch;
  uint64_t high_generation=generation>candidate_generation?generation:candidate_generation;
  uint64_t high_token=token>candidate_token?token:candidate_token;
  CHECK(kf_denied[0].valid&&kf_denied[0].epoch==high_epoch&&kf_denied[0].generation==high_generation&&kf_denied[0].token==high_token);
  /* Restore the original identity after reset and renderer-storage release.
   * Neither boundary, nor the invalid intervening receipt, can revive it. */
  for(unsigned release=0;release<2;release++){
   install_receipt_identity(epoch,generation,token);enemy[75].filter=0;restart_same_identity(release!=0);
   tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();CHECK(!kf.draw[0].ready);present_models(0,false);
   CHECK(kf_denied[0].epoch==high_epoch&&kf_denied[0].generation==high_generation&&kf_denied[0].token==high_token);
  }
  restart_same_identity(false);t194_life.epoch=high_epoch+1;
  fixture_identity=high_generation>high_token?high_generation:high_token;
  receipt(75,0,6,48,40,true);tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();
  CHECK(kf.draw[0].ready&&!kf_denied[0].valid);present_models(1,false);
  uint64_t newer_epoch=t194_life.epoch,newer_generation=t194_slots[75].generation,newer_token=t194_slots[75].birth.token;
  /* Clearing active denial after a verified replacement must not erase its
   * numeric high-water or permit the older identity to return later. */
  install_receipt_identity(epoch,generation,token);restart_same_identity(false);
  tank_phase();tank_draw(75,0,48,40,false);tank_phase_end();finish();
  CHECK(!kf.draw[0].ready&&kf_denial_matches(75));present_models(0,false);
  CHECK(kf_denied[0].epoch==high_epoch&&kf_denied[0].generation==high_generation&&kf_denied[0].token==high_token);
  install_receipt_identity(newer_epoch,newer_generation,newer_token);restart_same_identity(false);
  tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();
  CHECK(kf.draw[0].ready&&!kf_denial_matches(75));present_models(1,false);
 }
}

static void test_prebody_partial_identity_denial(void)
{
 /* Six zeroable fields, every nonempty combination, except erasing every
  * monotonic axis. Bits: epoch, token, record, slotgen, birthgen, witness.
  * Also test both increment mismatches and completely stripped birth records
  * with a surviving observer witness. Repeat with/without prior rejection,
  * and with native type194/type193, to exercise candidate classification. */
 for(unsigned mutation=1;mutation<=67;mutation++)for(unsigned rejected=0;rejected<2;rejected++)for(unsigned other_type=0;other_type<2;other_type++){
  if(mutation==59||mutation==63)continue; /* Completely unidentifiable. */
  tank_start();CHECK(t194_witness(75)&&kf_lifetime(75));
  Tank194Birth birth=t194_slots[75].birth;
  uint64_t generation=t194_slots[75].generation,witness=t194_slots[75].witness;
  tank_phase();
  if(rejected){tank_part(75,0,1,48,40,0);CHECK(kf.draw[0].seen&&!kf.draw[0].valid&&!kf.draw[0].origin.token);}
  if(mutation<64){
   if(mutation&1)t194_slots[75].birth.epoch=0;
   if(mutation&2)t194_slots[75].birth.token=0;
   if(mutation&4)t194_slots[75].birth.record=0;
   if(mutation&8)t194_slots[75].generation=0;
   if(mutation&16)t194_slots[75].birth.generation=0;
   if(mutation&32)t194_slots[75].witness=0;
  }else if(mutation==64)t194_slots[75].generation++;
  else if(mutation==65)t194_slots[75].birth.generation++;
  else{
   memset(&t194_slots[75].birth,0,sizeof t194_slots[75].birth);
   if(mutation==67){t194_slots[75].generation=0;t194_slots[75].live=t194_slots[75].initialized=false;}
  }
  if(other_type)enemy[75].enemytype=193;
  tank_draw(75,0,48,40,false);CHECK(!kf.draw[0].valid&&!kf.draw[0].origin.token);
  tank_draw(76,1,52,43,true);tank_phase_end();player_draw(true);finish();present_models(2,true);
  t194_slots[75].birth=birth;t194_slots[75].generation=generation;t194_slots[75].witness=witness;
  t194_slots[75].live=t194_slots[75].initialized=true;enemy[75].enemytype=194;
  CHECK(t194_witness(75)&&kf_lifetime(75));
  restart_same_identity(rejected!=0);tank_phase();tank_draw(75,0,48,40,false);
  tank_draw(76,1,52,43,true);tank_phase_end();player_draw(true);finish();
  if(kf.draw[0].ready)fprintf(stderr,"Receipt restoration revived mutation=%u prior_rejection=%u other_type=%u\n",mutation,rejected,other_type);
  CHECK(!kf.draw[0].ready&&kf_denial_matches(75));present_models(2,true);
  /* A receipt with only epoch remaining conservatively closes that epoch.
   * Every positive here is an actual fully verified newer-epoch birth. */
  restart_same_identity(false);++t194_life.epoch;receipt(75,0,6,48,40,true);
  tank_phase();tank_draw(75,0,48,40,true);tank_phase_end();finish();
  CHECK(kf.draw[0].ready&&!kf_denial_matches(75));present_models(1,false);
 }
 /* A normal non-tank pool allocation without a known tank birth is ignored.
  * An ordinary allocation generation alone cannot invent tank authority. */
 tank_start();memset(t194_slots+99,0,sizeof t194_slots[99]);enemy[99].enemytype=193;t194_slots[99].generation=17;
 Uint8 prior_denial[sizeof kf_denied[24]];memcpy(prior_denial,kf_denied+24,sizeof prior_denial);
 tank_phase();render_mirror_tank_fallback_tile_begin(game_screen,99,48,40,enemySpriteSheets,13,0,0);
 CHECK(!kf.draw[24].seen&&!kf.draw[24].valid&&!memcmp(prior_denial,kf_denied+24,sizeof prior_denial));
 tank_phase_end();finish();present_models(0,false);
}

int main(int argc,char **argv)
{
 CHECK(argc>=4);asset_root=argv[1];tank_root=argv[2];CHECK(SDL_Init(SDL_INIT_VIDEO)==0);
 fc_source=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 fc_output=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 canvas=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 renderer_screen=screen;renderer=SDL_CreateSoftwareRenderer(screen);CHECK(fc_source&&fc_output&&canvas&&screen&&renderer);game_screen=VGAScreen=fc_source;destination=(SDL_Rect){0,0,2560,1600};
 for(unsigned i=0;i<10;i++){fg.rgba[i]=malloc(FG_RGBA_BYTES);CHECK(fg.rgba[i]);}
 for(unsigned a=0;a<13;a++){
  unsigned pose=a<8?a:a-8;char path[2048];
  CHECK(snprintf(path,sizeof path,a<8?"%s/enemy-newsh2-%u-8.hda":"%s/ship-%u-8.hda",a<8?tank_root:asset_root,a<8?oracle_tank_art[pose]:oracle_specs[pose].index)>0);
  FILE *file=fopen(path,"rb");CHECK(file);Uint8 header[28];CHECK(fread(header,1,28,file)==28&&!memcmp(header,"HDR1",4));
  Uint8 *art=malloc(FG_RGBA_BYTES);CHECK(art);CHECK(fread(art,1,FG_RGBA_BYTES,file)==FG_RGBA_BYTES&&fgetc(file)==EOF);CHECK(!fclose(file));
  CHECK(asteroid1_stamp(art,FG_RGBA_BYTES)==(a<8?oracle_tank_art_stamp[pose]:oracle_specs[pose].stamp));
  if(a<8)tank_oracle_art[pose]=art;else oracle_art[pose]=art;
 }
 test_prebody_partial_identity_denial();
 test_semantic_type_stays_denied();test_semantics_after_frame_rejection();test_sealed_descriptor_is_immutable();test_acquisition_binding_before_seal();test_denial_componentwise_high_water();
 test_eight_poses_and_births();test_cross_actor_retirement();test_real_native_effects();test_local_sequences();test_sticky_identity();test_sticky_post_draw_loss();test_admission_and_bounds();test_post_lock_and_resources(argc,argv);
 tf_release();for(unsigned i=0;i<10;i++)free(fg.rgba[i]);for(unsigned i=0;i<8;i++)free(tank_oracle_art[i]);for(unsigned i=0;i<5;i++)free(oracle_art[i]);
 SDL_DestroyRenderer(renderer);SDL_FreeSurface(screen);SDL_FreeSurface(canvas);SDL_FreeSurface(fc_source);SDL_FreeSurface(fc_output);SDL_Quit();
 printf("PASS: tank fallback %" PRIu64 " assertions; eight authored poses, 18 births/25 slots, independent native/alpha oracle, real writer/SDL Present, cross-actor retirement, sticky denial and adversarial post-lock checks\n",checks);return 0;
}
