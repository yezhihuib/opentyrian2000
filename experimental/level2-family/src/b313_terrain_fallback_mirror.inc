/* Independent, opt-in terrain-only transaction. Building observers grant no
 * permission here. All actors use the final native framebuffer on this path.
 * Captured terrain is retained only until the next actual native store. */
enum {TF_CONTEXT=1,TF_WRITER=2,TF_EFFECT=3,TF_GROUND=4,TF_OUTPUT=5,TF_PRESENT=6,TF_RESET=7};
static struct {
 bool enabled,valid,captured,ready,presenting;
 uint64_t generation,frame;
 unsigned char expected[64000],final[64000],mask[64000];
 SDL_Surface *terrain,*result,*terrain_surface,*result_surface;
 void *terrain_pixels,*result_pixels;
 SDL_PixelFormat *terrain_format,*result_format;
 SDL_Texture *texture;
 SDL_Renderer *renderer;
 Uint32 palette[256];
} tf;
static B313TerrainFallbackStatus tf_status;
static bool tf_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *v=getenv("BUILDING313_TERRAIN_FALLBACK_ENABLE");
 return v&&!strcmp(v,"1")&&render_mirror_family_requested();
#else
 return false;
#endif
}
static void tf_fail(unsigned reason)
{
 if(!tf.enabled)return;
 pf_shared_fail();
 if(tf.valid){++tf_status.rejected;if(!tf_status.first_reason)tf_status.first_reason=reason;}
 tf.valid=false;tf.ready=false;
}
static void tf_reset(void)
{
 pf_reset();
 /* Lifecycle retirement is not a proof rejection. Never retain a candidate. */
 tf.enabled=tf.valid=tf.captured=tf.ready=tf.presenting=false;
 memset(tf.mask,0,sizeof tf.mask);
}
static bool tf_tracking(void){return tf.enabled;}
static bool tf_geometry(void)
{
 return tf.enabled&&tf.valid&&tf_requested()&&tf.generation==fc_generation&&tf.frame==fc_frame&&
  family_geometry(false)&&!memcmp(tf.palette,rgb_palette,sizeof tf.palette);
}
static void tf_begin(void)
{
 tf.enabled=tf.valid=tf.captured=tf.ready=tf.presenting=false;
 memset(tf.mask,0,sizeof tf.mask);
 if(!tf_requested()||fc.frame_failed||!family_geometry(false))return;
 tf_status.surviving_cells=0;
 tf.enabled=tf.valid=true;tf.generation=fc_generation;tf.frame=fc_frame;
 memcpy(tf.palette,rgb_palette,sizeof tf.palette);
 memcpy(tf.expected,fc_source_pixels,sizeof tf.expected);++tf_status.frames;pf_begin();
}
/* Called before the legacy actor-failure early return. This is the ONLY
 * writer-ledger consumption when enabled, even after this candidate fails. */
static bool tf_pixel(SDL_Surface *s,Uint8 *address,int style)
{
 bool paired=b313_family_writer_pixel(s,address);
 if(!paired){tf_fail(TF_WRITER);return false;}
 if(!tf.valid)return true;
 if(!tf_geometry()){tf_fail(TF_CONTEXT);return true;}
 if(style!=MIRROR_NORMAL&&style!=MIRROR_SHADOW&&style!=MIRROR_BLEND){tf_fail(TF_EFFECT);return true;}
 if(s!=fc_source)return true;
 uintptr_t off=(uintptr_t)address-(uintptr_t)fc_source_pixels;
 if(off>=64000){tf_fail(TF_CONTEXT);return true;}
 pf_pixel((unsigned)off,style);
 tf.expected[off]=*address;
 if(tf.mask[off]){tf.mask[off]=0;++tf_status.retired;}
 return true;
}
/* Pure resource check. Map/source validation is shared, actor lifetime is not.
 * The optional red-vent extension has no independent proof in this candidate. */
static bool tf_ground_current(void)
{
 if(rp.enabled||!fg_terrain_snapshot_current())return false;
 for(unsigned i=0;i<10;i++)if(!fg.rgba[i]||fg_hash(fg.rgba[i],FG_RGBA_BYTES)!=fg_payload_pins[i])return false;
 if(fl.enabled)for(unsigned i=0;i<12;i++)if(!fl.rgba[i]||fg_hash(fl.rgba[i],FG_RGBA_BYTES)!=fg_cliff_payload_pins[i])return false;
 if(fk.enabled&&(!fk.rgba||fg_hash(fk.rgba,FG_RGBA_BYTES)!=fg_corner_payload_pin))return false;
 if(fs340.enabled&&(!fs340.rgba||fg_hash(fs340.rgba,FG_RGBA_BYTES)!=fg_static340_payload_pin))return false;
 return true;
}
static void tf_capture(void)
{
 if(!tf.enabled||!tf.valid)return;
 if(tf.captured||!tf_geometry()||!tf_ground_current()||!b313_family_writer_draw_ready(tf.frame)){tf_fail(TF_GROUND);return;}
 if(!tf.terrain)tf.terrain=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 if(!tf.result)tf.result=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);
 if(!family_rgb(tf.terrain)||!family_rgb(tf.result)||!family_geometry(true)){tf_fail(TF_CONTEXT);return;}
 tf.terrain_surface=tf.terrain;tf.result_surface=tf.result;
 tf.terrain_pixels=tf.terrain->pixels;tf.result_pixels=tf.result->pixels;tf.terrain_format=tf.terrain->format;tf.result_format=tf.result->format;
 memset(tf.mask,0,sizeof tf.mask);
 for(unsigned off=0;off<64000;off++)if(fg.ground_mask[off]||(fl.enabled&&fl.mask[off])||(fk.enabled&&fk.mask[off])||(fs340.enabled&&fs340.mask[off])){
  unsigned x=off%320,y=off/320;
  for(unsigned sy=0;sy<8;sy++)memcpy((Uint32 *)tf.terrain->pixels+(y*8+sy)*2560+x*8,(Uint32 *)canvas->pixels+(y*8+sy)*2560+x*8,32);
  tf.mask[off]=1;
 }
 tf.captured=true;++tf_status.captures;
}
static bool tf_current(void)
{
 if(!tf_geometry()||!tf.captured||tf.terrain!=tf.terrain_surface||tf.result!=tf.result_surface||!family_rgb(tf.terrain)||!family_rgb(tf.result)||
    tf.terrain->pixels!=tf.terrain_pixels||tf.result->pixels!=tf.result_pixels||tf.terrain->format!=tf.terrain_format||tf.result->format!=tf.result_format||
    !tf_ground_current()||!b313_family_writer_peek_current(tf.frame)||
    memcmp(tf.expected,fc_source_pixels,64000)||memcmp(tf.final,fc_output_pixels,64000))return false;
 for(unsigned y=0;y<184;y++)if(memcmp((Uint8 *)fc_output_pixels+y*320,(Uint8 *)fc_source_pixels+y*320+24,264))return false;
 return true;
}
static void tf_finish(MirrorOutputKind kind)
{
 if(!tf.enabled||!tf.valid)return;
 if(kind!=MIRROR_OUTPUT_ORDINARY||!tf.captured||!tf_geometry()){tf_fail(TF_OUTPUT);return;}
 B313FamilyWriterStatus w=b313_family_writer_status();
 if((!w.sealed&&!b313_family_writer_seal(tf.frame))||!b313_family_writer_peek_current(tf.frame)){tf_fail(TF_WRITER);return;}
 memcpy(tf.final,fc_output_pixels,sizeof tf.final);
 if(!tf_current()||!family_upscale_8x(tf.result,fc_output)){tf_fail(TF_OUTPUT);return;}
 unsigned cells=0;
 for(unsigned y=0;y<184;y++)for(unsigned x=24;x<288;x++)if(tf.mask[y*320+x]){
  for(unsigned sy=0;sy<8;sy++)memcpy((Uint32 *)tf.result->pixels+(y*8+sy)*2560+(x-24)*8,(Uint32 *)tf.terrain->pixels+(y*8+sy)*2560+x*8,32);
  ++cells;
 }
 tf_status.surviving_cells=cells;
 if(!cells)return;
 tf.ready=true;++tf_status.prepared;pf_finish();
}
static bool tf_destination(SDL_Renderer *renderer,const SDL_Rect *dst)
{
 int w=0,h=0;
 return renderer&&dst&&dst->x>=0&&dst->y>=0&&dst->w>0&&dst->h>0&&
  !SDL_GetRendererOutputSize(renderer,&w,&h)&&(int64_t)dst->x+dst->w<=w&&(int64_t)dst->y+dst->h<=h;
}
static bool tf_present(SDL_Renderer *renderer,SDL_Surface *source,const SDL_Rect *dst)
{
 if(!tf.ready)return false;
 if(source!=fc_output||!tf_current()||!tf_destination(renderer,dst)){tf_fail(TF_PRESENT);return false;}
 if(!tf.texture){tf.texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,2560,1600);tf.renderer=renderer;}
 SDL_Texture *target=tf.texture;
 Uint32 format=0;int access=0,w=0,h=0;
 if(!target||renderer!=tf.renderer||SDL_QueryTexture(target,&format,&access,&w,&h)||format!=SDL_PIXELFORMAT_ARGB8888||access!=SDL_TEXTUREACCESS_STREAMING||w!=2560||h!=1600||SDL_SetTextureScaleMode(target,SDL_ScaleModeNearest)||SDL_SetTextureBlendMode(target,SDL_BLENDMODE_NONE)){tf_fail(TF_PRESENT);return false;}
 void *pixels=NULL;int pitch=0;
 if(SDL_LockTexture(target,NULL,&pixels,&pitch)){tf_fail(TF_PRESENT);return false;}
 SDL_ScaleMode scale=SDL_ScaleModeLinear;SDL_BlendMode blend=SDL_BLENDMODE_BLEND;
 bool current=pixels&&pitch>=10240&&(size_t)pitch<=SIZE_MAX/1600&&tf.ready&&target==tf.texture&&renderer==tf.renderer&&source==fc_output&&tf_destination(renderer,dst)&&
  !SDL_QueryTexture(target,&format,&access,&w,&h)&&format==SDL_PIXELFORMAT_ARGB8888&&access==SDL_TEXTUREACCESS_STREAMING&&w==2560&&h==1600&&
  !SDL_GetTextureScaleMode(target,&scale)&&scale==SDL_ScaleModeNearest&&!SDL_GetTextureBlendMode(target,&blend)&&blend==SDL_BLENDMODE_NONE&&tf_current();
 if(!current){SDL_UnlockTexture(target);tf_fail(TF_PRESENT);return false;}
 bool player_used=pf_compose();
 family_static_hud_compose_surface(tf.result);
 for(int y=0;y<1600;y++)memcpy((Uint8 *)pixels+(size_t)y*(size_t)pitch,(Uint8 *)tf.result->pixels+(size_t)y*10240,10240);
 SDL_UnlockTexture(target);
 tf.ready=false; /* Single use, including renderer failure. */
 if(SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,target,NULL,dst)){tf_fail(TF_PRESENT);return false;}
 tf.presenting=true;pf_present_begin(player_used);asset_debug_readback(renderer);SDL_RenderPresent(renderer);pf_present_end();tf.presenting=false;++tf_status.presents;
 return true;
}
static void tf_release(void)
{
 tf_reset();pf_release();if(tf.texture)SDL_DestroyTexture(tf.texture);tf.texture=NULL;tf.renderer=NULL;
 if(tf.terrain)SDL_FreeSurface(tf.terrain);
 if(tf.result)SDL_FreeSurface(tf.result);
 tf.terrain=tf.result=NULL;
}
B313TerrainFallbackStatus render_mirror_terrain_fallback_status(void)
{
 B313TerrainFallbackStatus s=tf_status;s.requested=tf_requested();s.active=tf.enabled&&tf.valid;s.ready=tf.ready;s.presenting=tf.presenting;return s;
}
