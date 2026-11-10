#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "SDL.h"
#include "b313_family_writer.h"
#include "b313_terrain_fallback.h"
extern bool b313_family_writer_peek_current(uint64_t);
#define FG_RGBA_BYTES 172032
#define MIRROR_NORMAL 0
#define MIRROR_SHADOW 1
#define MIRROR_BLEND 2
typedef enum {MIRROR_OUTPUT_UNSUPPORTED,MIRROR_OUTPUT_ORDINARY} MirrorOutputKind;
static SDL_Surface *fc_source,*fc_output,*canvas;
static void *fc_source_pixels,*fc_output_pixels;
static uint64_t fc_generation,fc_frame;
static struct {bool frame_failed,frame_active,ready;unsigned first_reason,blend_fallbacks;} fc;
static struct {unsigned first_reason;} fbr;
static bool ready,last_output_valid,last_output_scene_hd,have_fade_saved;
static int fade_mode;
enum {FC_SOURCE=3,FC_PRESENT=9,FC_EFFECT=10};
static Uint32 rgb_palette[256];
static bool parent_requested=true,geometry_ok=true,ground_ok=true;
static struct {bool enabled;} rp;
static struct {Uint8 *rgba[10];Uint8 ground_mask[64000];} fg;
static struct {bool enabled;Uint8 *rgba[12];Uint8 mask[64000];} fl;
static struct {bool enabled;Uint8 *rgba;Uint8 mask[64000];} fk,fs340;
static uint64_t fg_payload_pins[10],fg_cliff_payload_pins[12],fg_corner_payload_pin,fg_static340_payload_pin;
static unsigned checks,readbacks,hud_calls,mutate_lock,lock_calls;
static SDL_Renderer *renderer;
static SDL_Surface *alternate;
static SDL_PixelFormat format_copy;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAILED line %d: %s\n",__LINE__,#x);abort();}}while(0)
static bool render_mirror_family_requested(void){return parent_requested;}
static bool family_rgb(SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==2560&&s->h==1600&&s->pitch==10240&&s->format->format==SDL_PIXELFORMAT_ARGB8888&&!s->locked;}
static bool indexed(SDL_Surface *s){return s&&s->pixels&&s->format&&s->w==320&&s->h==200&&s->pitch==320&&s->format->format==SDL_PIXELFORMAT_INDEX8&&!s->locked;}
static bool family_geometry(bool rgb){return geometry_ok&&indexed(fc_source)&&indexed(fc_output)&&fc_source->pixels==fc_source_pixels&&fc_output->pixels==fc_output_pixels&&fc_source_pixels!=fc_output_pixels&&(!rgb||family_rgb(canvas));}
static bool fg_terrain_snapshot_current(void){return ground_ok&&family_geometry(true);}
static uint64_t fg_hash(const Uint8 *p,size_t n){uint64_t h=UINT64_C(0xcbf29ce484222325);while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}return h;}
static Uint32 color(Uint8 v){return UINT32_C(0xff000000)|rgb_palette[v];}
static bool family_upscale_8x(SDL_Surface *out,SDL_Surface *in)
{
 if(!family_rgb(out)||!indexed(in))return false;
 for(unsigned y=0;y<200;y++)for(unsigned x=0;x<320;x++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)
  ((Uint32 *)out->pixels)[(y*8+sy)*2560+x*8+sx]=color(((Uint8 *)in->pixels)[y*320+x]);
 return true;
}
static void family_static_hud_compose_surface(SDL_Surface *s){++hud_calls;((Uint32 *)s->pixels)[1599*2560+2559]=UINT32_C(0xff123456);}
static void asset_debug_readback(SDL_Renderer *r)
{
 CHECK(render_mirror_terrain_fallback_status().presenting);CHECK(r==renderer);++readbacks;
}
/* This fixture isolates terrain; the independent player adapter is covered
 * by test_b313_player_fallback with its real include and native writer. */
static void pf_shared_fail(void){}
static void pf_reset(void){}
static void pf_begin(void){}
static void pf_pixel(unsigned off,int style){(void)off;(void)style;}
static void pf_finish(void){}
static bool pf_compose(void){return false;}
static void pf_present_begin(bool used){(void)used;}
static void pf_present_end(void){}
static void pf_release(void){}
static int injected_lock(SDL_Texture *,const SDL_Rect *,void **,int *);
#define SDL_LockTexture injected_lock
#include "b313_terrain_fallback_mirror.inc"
#undef SDL_LockTexture
#include "b313_fault_helpers.inc"
static int injected_lock(SDL_Texture *target,const SDL_Rect *rect,void **pixels,int *pitch)
{
 int result=SDL_LockTexture(target,rect,pixels,pitch);++lock_calls;
 if(result)return result;
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
 case 12:tf.ready=false;break;
 case 13:b313_family_writer_gap(NWO_GAP_UNREGISTERED);break;
 case 14:*pitch=10239;break;
 case 15:*pixels=NULL;break;
 case 16:tf.terrain->pixels=tf.result->pixels;break;
 case 17:tf.result->pixels=tf.terrain->pixels;break;
 case 18:format_copy=*tf.terrain->format;tf.terrain->format=&format_copy;break;
 case 19:format_copy=*tf.result->format;tf.result->format=&format_copy;break;
 case 20:tf.terrain=alternate;break;
 case 21:tf.result=alternate;break;
 case 22:fc_source->pixels=fc_output->pixels;break;
 case 23:fc_output->pixels=fc_source->pixels;break;
 case 24:fc_source->pitch=319;break;
 case 25:fc_source->clip_rect.w=319;break;
 case 26:tf.result->pitch=10236;break;
 case 27:tf.texture=NULL;break;
 case 28:tf.renderer=NULL;break;
 }
 return result;
}
static void start(void)
{
 tf_reset();b313_family_writer_reset();
 parent_requested=geometry_ok=ground_ok=true;fc.frame_failed=false;fc.frame_active=true;fc.ready=false;fc.first_reason=fbr.first_reason=0;mutate_lock=0;
 setenv("BUILDING313_TERRAIN_FALLBACK_ENABLE","1",1);
 for(unsigned i=0;i<256;i++)rgb_palette[i]=i*UINT32_C(0x010101);
 memset(fc_source->pixels,17,64000);memset(fc_output->pixels,17,64000);
 fc_source_pixels=fc_source->pixels;fc_output_pixels=fc_output->pixels;
 ++fc_generation;++fc_frame;
 CHECK(b313_family_writer_begin(fc_frame,fc_source,fc_output));
 memset(fg.ground_mask,0,64000);memset(fl.mask,0,64000);memset(fk.mask,0,64000);memset(fs340.mask,0,64000);
 fl.enabled=fk.enabled=fs340.enabled=rp.enabled=false;
 for(unsigned i=0;i<10;i++){memset(fg.rgba[i],i+1,FG_RGBA_BYTES);fg_payload_pins[i]=fg_hash(fg.rgba[i],FG_RGBA_BYTES);}
 tf_begin();CHECK(tf_tracking());CHECK(tf.valid);
}
static void capture(void)
{
 for(unsigned x=24;x<28;x++){
  unsigned off=5*320+x;fg.ground_mask[off]=1;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)((Uint32 *)canvas->pixels)[(40+sy)*2560+x*8+sx]=UINT32_C(0xff000000)|((x-23)<<16)|(sy<<8)|sx;
 }
 /* Outside crop is captured but must never be displayed as terrain. */
 fg.ground_mask[0]=1;tf_capture();CHECK(tf.captured);CHECK(tf.valid);
}
static void store(unsigned off,Uint8 value,int style)
{
 Uint8 *p=(Uint8 *)fc_source->pixels+off;
 b313_family_writer_store(fc_source,p,1,NWO_SPRITE2);*p=value;CHECK(tf_pixel(fc_source,p,style));
}
static void crop(void)
{
 for(unsigned y=0;y<184;y++){
  Uint8 *a=(Uint8 *)fc_source_pixels+y*320+24,*b=(Uint8 *)fc_output_pixels+y*320;
  b313_family_writer_copy(fc_output,b,fc_source,a,264);memcpy(b,a,264);
 }
}
static void finish(void){crop();tf_finish(MIRROR_OUTPUT_ORDINARY);}
static SDL_Rect destination={0,0,320,200};
static void test_retirement_and_pixels(void)
{
 start();capture();fc.frame_failed=true;
 store(5*320+24,17,MIRROR_NORMAL);store(5*320+25,33,MIRROR_SHADOW);store(5*320+26,44,MIRROR_BLEND);
 CHECK(!tf.mask[5*320+24]&&!tf.mask[5*320+25]&&!tf.mask[5*320+26]&&tf.mask[5*320+27]);
 finish();CHECK(tf.ready);CHECK(tf_status.surviving_cells==1);
 for(unsigned y=0;y<200;y++)for(unsigned x=0;x<320;x++)for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  Uint32 want=color(((Uint8 *)fc_output_pixels)[y*320+x]);
  if(y==5&&x==3)want=UINT32_C(0xff040000)|(sy<<8)|sx;
  CHECK(((Uint32 *)tf.result->pixels)[(y*8+sy)*2560+x*8+sx]==want);
 }
 unsigned before=readbacks;CHECK(tf_present(renderer,fc_output,&destination));CHECK(readbacks==before+1);CHECK(!tf.ready);
 CHECK(!tf_present(renderer,fc_output,&destination));CHECK(readbacks==before+1);CHECK(hud_calls>0);
}
static void test_failures(void)
{
 start();capture();geometry_ok=false;finish();CHECK(!tf.ready);
 start();capture();store(5*320+24,5,99);CHECK(!tf.valid);finish();CHECK(!tf.ready);
 start();capture();b313_family_writer_unknown(fc_source,fc_source_pixels,1,NWO_UNKNOWN_WRITE);finish();CHECK(!tf.ready);
 start();capture();b313_family_writer_store(fc_source,fc_source_pixels,2,NWO_SPRITE2);
 ((Uint8 *)fc_source_pixels)[0]=5;CHECK(tf_pixel(fc_source,fc_source_pixels,MIRROR_NORMAL));finish();CHECK(!tf.ready);
 start();capture();CHECK(!tf_pixel(fc_source,fc_source_pixels,MIRROR_NORMAL));CHECK(!tf.valid);
 start();capture();b313_family_writer_store(fc_source,fc_source_pixels,2,NWO_SPRITE2);
 ((Uint8 *)fc_source_pixels)[0]=5;((Uint8 *)fc_source_pixels)[1]=6;
 CHECK(tf_pixel(fc_source,fc_source_pixels,MIRROR_NORMAL));CHECK(tf_pixel(fc_source,(Uint8 *)fc_source_pixels+1,MIRROR_NORMAL));finish();CHECK(tf.ready);
 start();capture();((Uint8 *)fc_source_pixels)[123]=22;finish();CHECK(!tf.ready);
 start();capture();crop();((Uint8 *)fc_output_pixels)[10]^=1;tf_finish(MIRROR_OUTPUT_ORDINARY);CHECK(!tf.ready);
 start();capture();tf_capture();CHECK(!tf.valid);
 start();capture();tf_finish(MIRROR_OUTPUT_ORDINARY);CHECK(!tf.ready); /* no crop */
 start();capture();crop();tf_finish(MIRROR_OUTPUT_UNSUPPORTED);CHECK(!tf.ready);
 start();capture();ground_ok=false;finish();CHECK(!tf.ready);
 start();capture();fg.rgba[0][42]^=1;finish();CHECK(!tf.ready);
 start();capture();rp.enabled=true;finish();CHECK(!tf.ready);
 start();capture();for(unsigned x=24;x<28;x++)store(5*320+x,17,MIRROR_NORMAL);finish();CHECK(!tf.ready);
 start();capture();finish();CHECK(tf.ready);tf_reset();CHECK(!tf_present(renderer,fc_output,&destination));CHECK(!tf_tracking());
 start();capture();finish();CHECK(tf.ready);tf_begin();CHECK(!tf.ready&&!tf.captured); /* no prior output reused */
 start();capture();finish();CHECK(tf.ready);SDL_Rect bad={INT32_MAX,0,320,200};CHECK(!tf_present(renderer,fc_output,&bad));
}
static void actual_effect_route(int style,Uint8 before,Uint8 *address)
{
 unsigned char hd_owner[1]={1};unsigned n=0;
 bool lamp_owned=false,gray_owned=false,longface_owned=false,triple_owned=false,ember_owned=false,
 fork_owned=false,turret_owned=false,linked_owned=false,linked_prop_owned=false,late_actor_owned=false,
 normal270_owned=false,rock_owned=false,random_prop_owned=false,tank_owned=false,ship_owned=false,
 enemy_shot_owned=false,terrain_retire=false;
#include "b313_effect_branches.inc"
}
static void test_known_blend_scene_failure(void)
{
 start();capture();unsigned off=5*320+24;Uint8 *address=(Uint8 *)fc_source_pixels+off;
 store(off,31,MIRROR_BLEND);CHECK(tf.valid&&!tf.mask[off]);
 unsigned fallbacks=fc.blend_fallbacks;actual_effect_route(MIRROR_BLEND,17,address);
 CHECK(fc.frame_failed&&fc.first_reason==FC_EFFECT&&fc.blend_fallbacks==fallbacks+1&&tf.valid);
 finish();CHECK(tf.ready&&tf_status.surviving_cells==3);
 CHECK(((Uint32 *)tf.result->pixels)[40*2560]==color(31));
 CHECK(tf_present(renderer,fc_output,&destination));CHECK(!tf.ready);
 start();capture();CHECK(!tf_pixel(fc_source,fc_source_pixels,MIRROR_BLEND));CHECK(!tf.valid);finish();CHECK(!tf.ready);
 start();capture();store(off,31,99);actual_effect_route(99,17,address);CHECK(fc.frame_failed&&!tf.valid);finish();CHECK(!tf.ready);
 start();capture();store(off,31,MIRROR_SHADOW);CHECK(tf.valid);actual_effect_route(MIRROR_SHADOW,17,address);
 CHECK(fc.frame_failed&&!tf.valid);finish();CHECK(!tf.ready);
}
static void test_configuration_and_resources(void)
{
 start();setenv("BUILDING313_TERRAIN_FALLBACK_ENABLE","0",1);tf_begin();CHECK(!tf_tracking()&&!tf.ready);
 setenv("BUILDING313_TERRAIN_FALLBACK_ENABLE","invalid",1);tf_begin();CHECK(!tf_tracking());
 setenv("BUILDING313_TERRAIN_FALLBACK_ENABLE","1",1);parent_requested=false;tf_begin();CHECK(!tf_tracking());
 start();fc.frame_failed=true;tf_begin();CHECK(!tf_tracking());
 start();tf_finish(MIRROR_OUTPUT_ORDINARY);CHECK(!tf.ready&&!tf.valid); /* incomplete terrain pass */
 start();fl.enabled=true;for(unsigned i=0;i<12;i++){memset(fl.rgba[i],i+10,FG_RGBA_BYTES);fg_cliff_payload_pins[i]=fg_hash(fl.rgba[i],FG_RGBA_BYTES);}
 capture();fl.rgba[11][FG_RGBA_BYTES-1]^=1;finish();CHECK(!tf.ready);
 start();fk.enabled=true;memset(fk.rgba,7,FG_RGBA_BYTES);fg_corner_payload_pin=fg_hash(fk.rgba,FG_RGBA_BYTES);
 capture();fk.rgba[0]^=1;finish();CHECK(!tf.ready);
 start();fs340.enabled=true;memset(fs340.rgba,9,FG_RGBA_BYTES);fg_static340_payload_pin=fg_hash(fs340.rgba,FG_RGBA_BYTES);
 capture();fs340.rgba[0]^=1;finish();CHECK(!tf.ready);
 start();capture();finish();CHECK(tf.ready);tf_reset();CHECK(!tf_present(renderer,fc_output,&destination)); /* successful old scene retires unused candidate */
 start();capture();finish();CHECK(tf.ready);b313_family_writer_store(fc_source,fc_source_pixels,1,NWO_SPRITE2);
 CHECK(!tf_pixel(fc_source,fc_source_pixels,MIRROR_NORMAL));CHECK(!tf.ready); /* after seal */
 start();capture();fc.frame_failed=true;
 SDL_Rect rect={24,5,2,1};uint64_t token=b313_family_writer_fill_before(fc_source,&rect,NWO_SDL_BACKGROUND_CLEAR);
 CHECK(token);CHECK(SDL_FillRect(fc_source,&rect,17)==0);b313_family_writer_fill_after(token,0);
 CHECK(b313_family_writer_rect_begin(fc_source,&rect));
 CHECK(tf_pixel(fc_source,(Uint8 *)fc_source_pixels+5*320+24,MIRROR_NORMAL));
 CHECK(tf_pixel(fc_source,(Uint8 *)fc_source_pixels+5*320+25,MIRROR_NORMAL));
 CHECK(b313_family_writer_rect_end(fc_source));finish();CHECK(tf.ready&&tf_status.surviving_cells==2);
}
static void test_post_lock(void)
{
 for(unsigned mode=1;mode<=28;mode++){
  start();capture();finish();CHECK(tf.ready);mutate_lock=mode;
  SDL_Surface *terrain=tf.terrain,*result=tf.result;
  void *tp=terrain->pixels,*rpixels=result->pixels,*sp=fc_source->pixels,*op=fc_output->pixels;
  SDL_PixelFormat *tformat=terrain->format,*rformat=result->format;
  SDL_Texture *texture_before=tf.texture;SDL_Renderer *renderer_before=tf.renderer;
  unsigned before=readbacks,locks=lock_calls;CHECK(!tf_present(renderer,fc_output,&destination));CHECK(lock_calls==locks+1);CHECK(readbacks==before);CHECK(!tf.ready);
  tf.terrain=terrain;tf.result=result;terrain->pixels=tp;result->pixels=rpixels;
  terrain->format=tformat;result->format=rformat;fc_source->pixels=sp;fc_output->pixels=op;
  fc_source->pitch=320;fc_source->clip_rect.w=320;result->pitch=10240;
  tf.texture=texture_before;tf.renderer=renderer_before;
 }
}
int main(void)
{
 CHECK(SDL_Init(SDL_INIT_VIDEO)==0);
 fc_source=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 fc_output=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 canvas=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,32,SDL_PIXELFORMAT_ARGB8888);
 alternate=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 renderer=SDL_CreateSoftwareRenderer(screen);CHECK(fc_source&&fc_output&&canvas&&screen&&renderer);
 for(unsigned i=0;i<10;i++){fg.rgba[i]=malloc(FG_RGBA_BYTES);CHECK(fg.rgba[i]);}
 for(unsigned i=0;i<12;i++){fl.rgba[i]=malloc(FG_RGBA_BYTES);CHECK(fl.rgba[i]);}
 fk.rgba=malloc(FG_RGBA_BYTES);fs340.rgba=malloc(FG_RGBA_BYTES);CHECK(fk.rgba&&fs340.rgba);
 test_retirement_and_pixels();test_failures();test_configuration_and_resources();test_known_blend_scene_failure();test_post_lock();
 tf_release();for(unsigned i=0;i<12;i++)free(fl.rgba[i]);free(fk.rgba);free(fs340.rgba);for(unsigned i=0;i<10;i++)free(fg.rgba[i]);SDL_DestroyRenderer(renderer);SDL_FreeSurface(alternate);SDL_FreeSurface(screen);SDL_FreeSurface(canvas);SDL_FreeSurface(fc_source);SDL_FreeSurface(fc_output);SDL_Quit();
 printf("PASS: terrain fallback %u assertions; actual native ledger, exact pixels, lifecycle and 28 post-lock mutations\n",checks);
}
