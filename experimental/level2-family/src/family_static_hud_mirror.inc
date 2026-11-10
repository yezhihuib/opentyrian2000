/* Optional output-only static border for the private level-2 family renderer.
 * This never enables a scene, shared HUD, font, meter or texture lease. The
 * family configuration and HUD source proof are required. Output-only HUD
 * readiness is independent of actor-canvas admission: rejected scenes may
 * retain the border over a separately witnessed native indexed frame.
 * The existing HUD1 parser/sampler owns the finite source-pinned artwork. */
static bool family_scope(void);
static bool family_indexed(SDL_Surface *);
static bool family_rgb(SDL_Surface *);
static bool shared_hud_palette_matches(void);

static bool family_static_hud_captured, family_static_hud_painted;
static bool family_static_hud_suspended;
static bool family_static_hud_frame_ready;
static SDL_Surface *family_static_hud_surface;
static void *family_static_hud_pixels;
static SDL_PixelFormat *family_static_hud_format;
static SDL_Texture *family_static_hud_texture;
static SDL_Renderer *family_static_hud_renderer;
static Uint8 family_static_hud_final[64000];
static Uint32 family_static_hud_palette[256];

static bool family_static_hud_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *value=getenv("BUILDING313_FAMILY_HUD_ENABLE");
 return value&&!strcmp(value,"1")&&render_mirror_family_requested();
#else
 return false;
#endif
}


#include "family_dynamic_hud_mirror.inc"
#include "family_hud_font_mirror.inc"

static void family_static_hud_reset(void)
{
 fdh_reset();fhf_reset();
 if(family_static_hud_captured)gameplay_hud_forget_source();
 family_static_hud_captured=family_static_hud_painted=false;
 family_static_hud_suspended=family_static_hud_frame_ready=false;
 family_static_hud_surface=NULL;family_static_hud_pixels=NULL;family_static_hud_format=NULL;
}

static void family_static_hud_start(SDL_Surface *source)
{
 if(!family_static_hud_requested()||!family_scope()||source!=VGAScreenSeg||
    !family_indexed(source))return;
 if(!gameplay_hud_load("assets/hd/shared-ui-v1")||
    !gameplay_hud_capture(source->pixels,source->pitch))return;
 if(!hud_runtime_compatible(false)){gameplay_hud_forget_source();return;}
 family_static_hud_surface=source;family_static_hud_pixels=source->pixels;
 family_static_hud_format=source->format;family_static_hud_captured=true;
 fdh_start(source);fhf_start(source);
}

static void family_static_hud_begin(void)
{
 fhf_begin();
 /* family_finish rebuilds output from native pixels on every accepted frame. */
 family_static_hud_painted=family_static_hud_frame_ready=false;family_static_hud_suspended=false;
}

static void family_static_hud_suspend(void)
{fhf_suspend();family_static_hud_suspended=true;family_static_hud_frame_ready=false;}

static void family_static_hud_invalidate_frame(void)
{family_static_hud_frame_ready=false;family_static_hud_painted=false;}

static void family_static_hud_release_texture(void)
{
 if(family_static_hud_texture)SDL_DestroyTexture(family_static_hud_texture);
 family_static_hud_texture=NULL;family_static_hud_renderer=NULL;
 family_static_hud_frame_ready=false;
}

static bool family_static_hud_current(void)
{
 if(!family_static_hud_captured||!family_static_hud_requested()||
    family_static_hud_suspended||!family_scope())return false;
 if(!family_indexed(VGAScreenSeg)||VGAScreenSeg!=family_static_hud_surface||
    VGAScreenSeg->pixels!=family_static_hud_pixels||
    VGAScreenSeg->format!=family_static_hud_format||!gameplay_hud_ready()||
    !hud_runtime_compatible(true)){
  /* An identity/layout or semantic-source change requires a fresh PIC3. */
  gameplay_hud_forget_source();family_static_hud_captured=false;return false;
 }
 return shared_hud_palette_matches();
}

static bool family_static_hud_paint(void *pixels,int pitch,bool full,bool admitted)
{
 if(admitted)gameplay_hud_prepare_corner(VGAScreenSeg->pixels,VGAScreenSeg->pitch);
 bool dynamic=admitted&&fdh_prepare();
 bool font=admitted&&fhf_prepare();
 bool painted=false;
 for(int y=0;y<200;y++)for(int x=(!full&&y<184?264:0);x<320;x++){
  Uint8 index=((const Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x];
  Uint32 native=palette_rgb(index);
  const Uint8 *sample=admitted&&(x>=264||y>=184)?gameplay_hud_sample(x,y,0,0,8,index):NULL;
  const Uint32 *font_sample=font?fhf_sample(x,y,0,0,index):NULL;
  const Uint8 *dynamic_sample=dynamic?fdh_sample(x,y,0,0,index):NULL;
  for(int sy=0;sy<8;sy++){
   Uint32 *row=(Uint32 *)((Uint8 *)pixels+(size_t)(y*8+sy)*(size_t)pitch)+x*8;
   for(int sx=0;sx<8;sx++){
    const Uint8 *rgba=sample?gameplay_hud_sample(x,y,sx,sy,8,index):NULL;
    if(dynamic_sample)rgba=fdh_sample(x,y,sx,sy,index);
    row[sx]=rgba?(UINT32_C(0xff000000)|((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2]):native;
    if(font_sample)row[sx]=*fhf_sample(x,y,sx,sy,index);
   }
  }
  painted=painted||sample!=NULL||dynamic_sample!=NULL||font_sample!=NULL;
 }
 return painted;
}

static void family_static_hud_compose_surface(SDL_Surface *target)
{
 /* Existing family admission has already succeeded. Refreshing just the HUD
  * at post-lock Present retires late changed cells without touching the scene. */
 if(!family_static_hud_captured&&!family_static_hud_painted)return;
 if(!family_indexed(VGAScreenSeg)||!family_rgb(target))return;
 bool admitted=family_static_hud_current();
 if(!admitted&&!family_static_hud_painted)return;
 family_static_hud_painted=family_static_hud_paint(target->pixels,target->pitch,false,admitted);
}

static void family_static_hud_compose(void){family_static_hud_compose_surface(output);}

static void family_static_hud_finish(MirrorOutputKind kind,bool scene_accepted)
{
 family_static_hud_frame_ready=false;
 if(kind!=MIRROR_OUTPUT_ORDINARY||!family_static_hud_current())return;
 memcpy(family_static_hud_final,VGAScreenSeg->pixels,sizeof family_static_hud_final);
 memcpy(family_static_hud_palette,rgb_palette,sizeof family_static_hud_palette);
 family_static_hud_frame_ready=true;
 if(scene_accepted)family_static_hud_compose();
}

static bool family_static_hud_final_current(SDL_Surface *source)
{
 return family_static_hud_frame_ready&&source==VGAScreenSeg&&family_static_hud_current()&&
  !memcmp(family_static_hud_final,source->pixels,sizeof family_static_hud_final)&&
  !memcmp(family_static_hud_palette,rgb_palette,sizeof family_static_hud_palette);
}

static bool family_static_hud_present_failed(void)
{family_static_hud_frame_ready=false;return false;}

static bool family_static_hud_present(SDL_Renderer *renderer,SDL_Surface *source,const SDL_Rect *dst)
{
 /* Separate HUD-only fallback. Never read the rejected family canvas/output,
  * set fc.ready, renew a family witness, or increment scene acceptance. */
 if(!renderer||!dst||!family_static_hud_final_current(source))return family_static_hud_present_failed();
 int rw=0,rh=0;
 if(SDL_GetRendererOutputSize(renderer,&rw,&rh)||dst->x<0||dst->y<0||dst->w<=0||dst->h<=0||
    (int64_t)dst->x+dst->w>rw||(int64_t)dst->y+dst->h>rh)return family_static_hud_present_failed();
 if(!family_static_hud_texture){
  family_static_hud_texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,2560,1600);
  family_static_hud_renderer=renderer;
 }
 SDL_Texture *target=family_static_hud_texture;
 Uint32 format=0;int access=0,w=0,h=0;
 if(!target||renderer!=family_static_hud_renderer||SDL_QueryTexture(target,&format,&access,&w,&h)||
    format!=SDL_PIXELFORMAT_ARGB8888||access!=SDL_TEXTUREACCESS_STREAMING||w!=2560||h!=1600||
    SDL_SetTextureScaleMode(target,SDL_ScaleModeNearest)||SDL_SetTextureBlendMode(target,SDL_BLENDMODE_NONE))return family_static_hud_present_failed();
 void *pixels=NULL;int pitch=0;
 if(SDL_LockTexture(target,NULL,&pixels,&pitch))return family_static_hud_present_failed();
 SDL_ScaleMode scale=SDL_ScaleModeLinear;SDL_BlendMode blend=SDL_BLENDMODE_BLEND;
 bool valid=pixels&&(uintptr_t)pixels%sizeof(Uint32)==0&&pitch>=10240&&pitch%4==0&&
  (size_t)pitch<=SIZE_MAX/1600&&target==family_static_hud_texture&&renderer==family_static_hud_renderer&&
  !SDL_GetRendererOutputSize(renderer,&rw,&rh)&&dst->x>=0&&dst->y>=0&&dst->w>0&&dst->h>0&&
  (int64_t)dst->x+dst->w<=rw&&(int64_t)dst->y+dst->h<=rh&&
  !SDL_QueryTexture(target,&format,&access,&w,&h)&&format==SDL_PIXELFORMAT_ARGB8888&&
  access==SDL_TEXTUREACCESS_STREAMING&&w==2560&&h==1600&&
  !SDL_GetTextureScaleMode(target,&scale)&&scale==SDL_ScaleModeNearest&&
  !SDL_GetTextureBlendMode(target,&blend)&&blend==SDL_BLENDMODE_NONE&&family_static_hud_final_current(source);
 bool painted=valid&&family_static_hud_paint(pixels,pitch,true,true);
 SDL_UnlockTexture(target);
 family_static_hud_frame_ready=false;
 if(!painted)return false;
 if(SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,target,NULL,dst))return false;
 asset_debug_readback(renderer);SDL_RenderPresent(renderer);return true;
}
