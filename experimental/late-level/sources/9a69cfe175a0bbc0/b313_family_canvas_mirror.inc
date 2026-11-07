/* Private family-only lease. Included in the real ordered compositor after
 * draw_asset_filtered. No old active/probe/tail permission is extended. */
#ifndef B313_FAMILY_CANVAS_DIAGNOSTIC
#define B313_FAMILY_CANVAS_DIAGNOSTIC 0
#endif
static B313FamilyCanvasStatus fc;
static bool fc_configured,fc_valid,fc_canvas_ready,fc_has_identity,fc_native_call;
static uint64_t fc_session,fc_frame,fc_generation,fc_lease_generation;
static B313FamilyFrameIdentity fc_identity;
static SDL_Surface *fc_source,*fc_output,*fc_canvas_surface,*fc_rgb_output_surface;
static const void *fc_owner,*fc_cloud,*fc_green_first,*fc_green_under,*fc_green_owner;
static SDL_Renderer *fc_texture_renderer;
static void *fc_source_pixels,*fc_output_pixels,*fc_canvas_pixels,*fc_rgb_output_pixels;
static SDL_PixelFormat *fc_source_format,*fc_output_format,*fc_canvas_format,*fc_rgb_output_format;
static Uint32 fc_palette[256];

#include "b313_building_blend_retire.h"
static B313BuildingBlendRetireStatus fbb;
/* Slot+1 is claimed only by a paired, ordered original building callback.
 * This receipt is distinct from selected and every other family's mask. */
static uint8_t fbb_owner[64000],fbb_retired[64000];
static bool family_building_blend_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_BUILDING_BLEND_RETIRE_ENABLE");
 return e&&!strcmp(e,"1");
#else
 return false;
#endif
}
static void family_building_blend_frame_begin(uint64_t frame)
{
 fbb.frame=frame;fbb.frame_enabled=family_building_blend_requested();
 fbb.frame_claimed=fbb.frame_eligible=fbb.frame_retired=0;
 fbb.current_reason=0;fbb.last_complete=fbb.last_ownership_cleared=false;
 fbb.last_x=fbb.last_y=-1;fbb.last_before_slot_plus1=0;
 fbb.last_native_index=fbb.last_native_rgb=fbb.last_subpixel_writes=0;
 fbb.last_store_min=fbb.last_store_max=0;
 memset(fbb_owner,0,sizeof fbb_owner);memset(fbb_retired,0,sizeof fbb_retired);
}

/* Independent frame-bound opt-in. Diagnostics never grant ownership. */
static B313TerrainBlendRetireStatus fbr;
static uint8_t fbr_retired[64000];
#include "b313_offcrop_blend.h"
static OffcropBlendStatus fcoc;
static uint32_t fcoc_before[64],fcoc_after[64];
static uint8_t fcoc_owner_before[64],fcoc_owner_after[64];
static bool family_offcrop_blend_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_OFFCROP_BLEND_RETIRE_ENABLE");
 return e&&!strcmp(e,"1");
#else
 return false;
#endif
}
static bool family_offcrop_cell(unsigned x,unsigned y)
{return x<320&&y<200&&(x<24||x>=288||y>=184);}
static void family_offcrop_frame_begin(uint64_t frame)
{
 fcoc.frame=frame;fcoc.frame_enabled=family_offcrop_blend_requested();
 fcoc.frame_cells=fcoc.frame_subpixel_writes=fcoc.frame_crop_writes=0;
 fcoc.first_x=fcoc.first_y=fcoc.last_x=fcoc.last_y=-1;
 fcoc.last_complete=false;fcoc.last_written=fcoc.last_crop_writes=0;
}
static void family_offcrop_cell_begin(unsigned x,unsigned y,uint8_t native)
{
 fcoc.last_x=(int)x;fcoc.last_y=(int)y;fcoc.last_native_index=native;
 fcoc.last_native_rgb=palette_rgb(native);fcoc.last_complete=false;
 fcoc.last_written=fcoc.last_crop_writes=0;
 fcoc.last_store_min=UINT_MAX;fcoc.last_store_max=0;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;unsigned k=sy*8+sx;
  fcoc_before[k]=((Uint32 *)canvas->pixels)[n];fcoc_owner_before[k]=hd_owner[n];
 }
}
static void family_offcrop_store_observed(const Uint32 *pixel)
{
 /* Audit the actual destination pointer, not just the requested cell. */
 size_t n=((uintptr_t)pixel-(uintptr_t)canvas->pixels)/sizeof *pixel;
 unsigned x=(unsigned)(n%2560),y=(unsigned)(n/2560);
 ++fcoc.last_written;
 if(n<fcoc.last_store_min)fcoc.last_store_min=(unsigned)n;
 if(n>fcoc.last_store_max)fcoc.last_store_max=(unsigned)n;
 if(x>=192&&x<2304&&y<1472)++fcoc.last_crop_writes;
}
static void family_offcrop_cell_end(unsigned x,unsigned y)
{
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;unsigned k=sy*8+sx;
  fcoc_after[k]=((Uint32 *)canvas->pixels)[n];fcoc_owner_after[k]=hd_owner[n];
 }
 if(!fcoc.frame_cells){fcoc.first_x=(int)x;fcoc.first_y=(int)y;}
 ++fcoc.frame_cells;++fcoc.total_cells;
 fcoc.frame_subpixel_writes+=fcoc.last_written;fcoc.total_subpixel_writes+=fcoc.last_written;
 fcoc.frame_crop_writes+=fcoc.last_crop_writes;fcoc.total_crop_writes+=fcoc.last_crop_writes;
 fcoc.last_complete=fcoc.last_written==64&&!fcoc.last_crop_writes;
}
OffcropBlendStatus render_mirror_offcrop_blend_status(void)
{OffcropBlendStatus out=fcoc;out.requested=family_offcrop_blend_requested();return out;}
bool render_mirror_offcrop_blend_last(uint32_t *before,uint32_t *after,
 uint8_t *owner_before,uint8_t *owner_after,size_t count)
{
 if(!before||!after||!owner_before||!owner_after||count!=64||!fcoc.last_complete||!fcoc.frame||fcoc.frame!=fc_frame)return false;
 memcpy(before,fcoc_before,sizeof fcoc_before);memcpy(after,fcoc_after,sizeof fcoc_after);
 memcpy(owner_before,fcoc_owner_before,sizeof fcoc_owner_before);memcpy(owner_after,fcoc_owner_after,sizeof fcoc_owner_after);return true;
}
static bool family_terrain_blend_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_TERRAIN_BLEND_RETIRE_ENABLE");
 return e&&!strcmp(e,"1");
#else
 return false;
#endif
}
static bool family_entry_config_current(void);
static bool family_terrain_blend_config_current(void)
{return family_entry_config_current()&&fbr.frame_enabled==family_terrain_blend_requested()&&
 fcoc.frame_enabled==family_offcrop_blend_requested();}

#include "b313_entry_clip.h"
static B313EntryClipStatus fce;
static bool family_entry_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_ENTRY_CLIP_ENABLE");
 return e&&!strcmp(e,"1");
#else
 return false;
#endif
}
static bool family_entry_config_current(void)
{return fce.frame_enabled==family_entry_requested()&&fbb.frame_enabled==family_building_blend_requested();}
B313EntryClipStatus render_mirror_entry_clip_status(void){return fce;}
static bool family_entry_support(const B313FamilyPlan *p,int x,int y,int part)
{
 unsigned q=part==0?0:part==1?1:part==19?2:part==20?3:4;
 int min_y=fce.frame_enabled?(q<2?-19:-18):0;
 if(q==4||x<0||x>308||y<min_y||y>186)return false;
 unsigned row0=y<0?(unsigned)(-y):0;if(row0>14)row0=14;
 return p->planned&&!p->write_allowed&&!p->runtime_eligible&&!p->reasons&&
  p->part==(unsigned)part&&p->component<4&&p->phase<3&&p->cycle>=1&&p->cycle<=20&&
  p->width==12&&p->height==14&&p->width_hd==96&&p->height_hd==112&&
  p->destination_x==x&&p->destination_y==y&&p->destination_x_hd==x*8&&p->destination_y_hd==y*8&&
  p->source_row0==row0&&p->visible_rows==14-row0&&p->support_y==(y<0?0:y)&&
  p->expected_callbacks==12*(14-row0);
}
static SDL_Rect fc_call_rect;
static unsigned fc_call_expected;
static uint64_t fc_call_pixels;
static unsigned fc_frame_draws;
enum {FCT_NONE=0,FCT_ACTOR=1,FCT_TERRAIN=2};
static struct {
 bool requested,has_context,actor_attempt;
 unsigned mode;
 B313TerrainContext context;
} fct;
static B313TerrainContinuityStatus fct_status;
static bool family_terrain_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *t=getenv("BUILDING313_TERRAIN_CONTINUITY_ENABLE");
 const char *f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 const char *g=getenv("BUILDING313_FAMILY_GROUND_ENABLE");
 return t&&!strcmp(t,"1")&&f&&!strcmp(f,"1")&&g&&!strcmp(g,"1");
#else
 return false;
#endif
}
enum {FC_CONFIG=1,FC_CONTEXT=2,FC_SOURCE=3,FC_WRITER=4,FC_ORDER=5,FC_ALLOCATION=6,FC_PALETTE=7,FC_OUTPUT=8,FC_PRESENT=9,FC_EFFECT=10,FC_RESET=11,FC_GROUND=12};
bool render_mirror_family_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 if(!fc_configured){const char *e=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");fc.requested=e&&strcmp(e,"0");fc_valid=e&&!strcmp(e,"1");fc_configured=true;}
#endif
 return fc.requested;
}
static void family_fault(unsigned reason)
{if(!fc.frame_active&&!fc.ready)return;if(!fbb.current_reason)fbb.current_reason=reason;memset(fbb_owner,0,sizeof fbb_owner);if(!fc.first_reason)fc.first_reason=reason;if(!fbr.first_reason)fbr.first_reason=reason;fc.frame_failed=true;fc.ready=false;ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
static void family_reset(void)
{
 es_reset();cb_reset();private_lamp272_reset();private_triple275_reset();private_ember269_reset();smallrocks_reset();rp_reset();fr462_reset();lp287_reset();c309_reset();ps_reset();f284_reset();la_reset();ts_reset();ln_reset();tp_reset();lpf_reset();t194_reset();private_gray325_reset();private_longface573_reset();
 fg_reset();
 memset(&fcoc,0,sizeof fcoc);
 memset(&fbb,0,sizeof fbb);memset(fbb_owner,0,sizeof fbb_owner);memset(fbb_retired,0,sizeof fbb_retired);
 memset(fbr_retired,0,sizeof fbr_retired);fbr.frame=0;fbr.frame_eligible=fbr.frame_retired=0;fbr.first_reason=0;fbr.first_x=fbr.first_y=-1;
 fct.mode=FCT_NONE;fct.has_context=false;
 if(!render_mirror_family_requested())return;
 if(fc.frame_active||fc.ready)family_fault(FC_RESET);
 if(fc_generation<UINT64_MAX)++fc_generation;else fc_valid=false;fc.canvas_generation=fc_generation;
 fc.frame_active=false;fc.ready=false;fc_native_call=false;fc_draw_lease=NULL;suppress=false;
 b313_family_writer_reset();
}
static bool family_indexed(SDL_Surface *s)
{return s&&s->pixels&&s->format&&s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&s->w==320&&s->h==200&&s->pitch==320&&!s->locked&&!SDL_MUSTLOCK(s)&&!s->clip_rect.x&&!s->clip_rect.y&&s->clip_rect.w==320&&s->clip_rect.h==200;}
static bool family_rgb(SDL_Surface *s)
{return s&&s->pixels&&s->format&&s->format->format==SDL_PIXELFORMAT_ARGB8888&&s->format->BitsPerPixel==32&&s->format->BytesPerPixel==4&&s->w==2560&&s->h==1600&&s->pitch==10240&&!s->locked&&!SDL_MUSTLOCK(s)&&!s->clip_rect.x&&!s->clip_rect.y&&s->clip_rect.w==2560&&s->clip_rect.h==1600;}
/* Family-only fixed 8x conversion. Callers retain the existing lease,
 * palette and native-writer gates. Refuse unknown geometry or overlapping
 * storage before writing. The pinned ohs_upscale_row closure writes only
 * observer metadata, never either pixel buffer or rgb_palette. */
static bool family_upscale_8x(SDL_Surface *dst,SDL_Surface *src)
{
 if(!family_indexed(src)||!family_rgb(dst))return false;
 uintptr_t a=(uintptr_t)src->pixels,b=(uintptr_t)dst->pixels;
 const size_t source_bytes=(size_t)320*200,output_bytes=(size_t)10240*1600;
 if(b%sizeof(Uint32)||a>UINTPTR_MAX-source_bytes||b>UINTPTR_MAX-output_bytes||
    (a<b+output_bytes&&b<a+source_bytes))return false;
 for(int y=0;y<200;y++) {
  Uint32 *row=(Uint32 *)((Uint8 *)dst->pixels+y*8*dst->pitch);
  const Uint8 *in=(const Uint8 *)src->pixels+y*src->pitch;
  for(int x=0;x<320;x++) {
   Uint32 color=palette_rgb(in[x]);
   for(int sx=0;sx<8;sx++)row[x*8+sx]=color;
  }
  ohs_upscale_row(dst,src,y*8);
  for(int sy=1;sy<8;sy++) {
   memcpy((Uint8 *)dst->pixels+(y*8+sy)*dst->pitch,row,10240);
   ohs_upscale_row(dst,src,y*8+sy);
  }
 }
 return true;
}
static bool family_scope(void)
{return fc_valid&&episodeNum==1&&lvlFileNum==2&&!xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent&&!manual_hd_enabled&&!asteroid_hd_enabled&&!shared_hud_requested()&&!global_asset_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid&&!game_probe_repeat&&!game_probe_skip;}
static bool family_geometry(bool rgb)
{
 if(fc_lease_generation!=fc_generation||!family_scope()||!family_indexed(game_screen)||!family_indexed(VGAScreenSeg)||game_screen!=fc_source||VGAScreenSeg!=fc_output||game_screen->pixels!=fc_source_pixels||VGAScreenSeg->pixels!=fc_output_pixels||game_screen->format!=fc_source_format||VGAScreenSeg->format!=fc_output_format||game_screen->pixels==VGAScreenSeg->pixels)return false;
 if(rgb&&(canvas!=fc_canvas_surface||output!=fc_rgb_output_surface||hd_owner!=fc_owner||cloud_owner!=fc_cloud||green_first!=fc_green_first||green_under!=fc_green_under||green_under_owner!=fc_green_owner||!family_rgb(canvas)||!family_rgb(output)||canvas->pixels!=fc_canvas_pixels||output->pixels!=fc_rgb_output_pixels||canvas->format!=fc_canvas_format||output->format!=fc_rgb_output_format||!hd_owner||!cloud_owner||!green_first||!green_under||!green_under_owner))return false;
 return true;
}
static void family_begin(void)
{
 ph_frame_begin();
 es_tick();cb_tick();private_lamp272_tick();private_triple275_tick();private_ember269_tick();smallrocks_tick();rp_tick();fr462_tick();lp287_tick();c309_tick();ps_tick();f284_tick();la_tick();ts_tick();ln_tick();tp_tick();lpf_tick();t194_tick();private_gray325_tick();private_longface573_tick();
 memset(&fct,0,sizeof fct);fct.requested=family_terrain_requested();
 if(fct.requested)++fct_status.frames;
 B313FamilyObserverStatus s=b313_family_observer_status();
 family_building_blend_frame_begin(s.frame);
 fce.frame=s.frame;fce.frame_enabled=family_entry_requested();fce.last_complete=false;
 fce.last_nonce=0;fce.last_callbacks=0;memset(&fce.last_plan,0,sizeof fce.last_plan);
 fce.frame_empty_calls=fce.frame_partial_calls=fce.frame_visible_calls=0;
 fbr.frame=s.frame;fbr.frame_enabled=family_terrain_blend_requested();
 family_offcrop_frame_begin(s.frame);
 fbr.frame_eligible=fbr.frame_retired=0;fbr.first_reason=0;fbr.first_x=fbr.first_y=-1;
 memset(fbr_retired,0,sizeof fbr_retired);
 if(fc.frame_active||fc.ready||(s.session==fc_session&&s.frame<=fc_frame)){fc.frame_active=true;family_fault(FC_ORDER);return;}
 b313_family_writer_reset();
 active=shared_hud_frame=false;global_talon_frame=global_shield_frame=global_pulse_frame=global_hitflare_frame=global_projectile91_frame=global_tank194_frame=global_rotor_frame=global_cash25_frame=global_small_explosion_frame=global_green_frame=global_smoke_frame=global_vulcan_frame=false;
#if defined(NEWSHF_HD_COMPOSITOR) && NEWSHF_HD_COMPOSITOR
 global_newshf_frame=false;
#endif
 ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;suppress=suppress_green_smoke=suppress_cloud=false;
 fc.frame_active=true;fc.frame_failed=false;fc.ready=false;fc_canvas_ready=fc_has_identity=fc_native_call=false;fc_draw_lease=NULL;fc_frame_draws=0;
 ++fc.frames;if(fc_generation==UINT64_MAX){family_fault(FC_ORDER);return;}fc.canvas_generation=++fc_generation;fc_lease_generation=fc_generation;
 fc_session=s.session;fc_frame=s.frame;
 if(asset_debug_fast_forward()||!family_scope()||!s.active||s.failed||!s.frame_open||!fc_frame||!family_indexed(game_screen)||!family_indexed(VGAScreenSeg)||game_screen->pixels==VGAScreenSeg->pixels){family_fault(FC_CONTEXT);return;}
 fc_source=game_screen;fc_output=VGAScreenSeg;fc_source_pixels=game_screen->pixels;fc_output_pixels=VGAScreenSeg->pixels;fc_source_format=game_screen->format;fc_output_format=VGAScreenSeg->format;
 memcpy(fc_palette,rgb_palette,sizeof fc_palette);
 for(int y=0;y<200;y++)memcpy(expected+y*320,(Uint8 *)game_screen->pixels+y*320,320);
 memset(selected,0,sizeof selected);region_count=green_head_count=0;draws=occlusions=mismatch=0;reject_reason=NULL;
 memset(restored_mask,0,sizeof restored_mask);all_rejections[0]=0;local_entities=local_regions=local_blocks=0;
 if(!b313_family_writer_begin(fc_frame,game_screen,VGAScreenSeg))family_fault(FC_WRITER);
 /* One attempt at the original frame-begin token, before fg starts. A
  * denial is never upgraded at finish or Present, including after an actor. */
 if(!fc.frame_failed&&fct.requested){
  fct.has_context=b313_family_observer_terrain_context_begin(fc_source,&fct.context);
  if(fct.has_context)++fct_status.begin_grants;
 }
 if(!fc.frame_failed)fg_frame_begin();
}
static bool family_prepare_canvas(void)
{
 if(fc_canvas_ready)return family_geometry(true);
 if(!canvas){canvas=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);output=SDL_CreateRGBSurfaceWithFormat(0,2560,1600,32,SDL_PIXELFORMAT_ARGB8888);hd_owner=calloc(4096000,1);cloud_owner=calloc(4096000,1);green_first=calloc(4096000,sizeof *green_first);green_under=malloc(4096000*sizeof *green_under);green_under_owner=malloc(4096000);}
 if(!family_rgb(canvas)||!family_rgb(output)||!hd_owner||!cloud_owner||!green_first||!green_under||!green_under_owner){family_fault(FC_ALLOCATION);return false;}
 fc_canvas_surface=canvas;fc_rgb_output_surface=output;fc_owner=hd_owner;fc_cloud=cloud_owner;fc_green_first=green_first;fc_green_under=green_under;fc_green_owner=green_under_owner;
 fc_canvas_pixels=canvas->pixels;fc_rgb_output_pixels=output->pixels;fc_canvas_format=canvas->format;fc_rgb_output_format=output->format;
 if(!family_upscale_8x(canvas,game_screen)){family_fault(FC_CONTEXT);return false;}memset(hd_owner,0,4096000);memset(cloud_owner,0,4096000);memset(green_first,0,4096000*sizeof *green_first);fc_canvas_ready=true;return true;
}
/* Called only after the current physical store/callback pair was consumed.
 * No in-flight or failed call, stale member, identity, palette or partial
 * HD cell can turn its provenance into a blend exemption. */
static bool family_building_blend_current(unsigned off,unsigned owner)
{
 if(!owner||off>=64000||!fbb.frame_enabled||fbb.frame!=fc_frame||
    !fc.frame_active||fc.frame_failed||fc_native_call||suppress||!fc_has_identity||
    !fce.last_complete||!fc_canvas_ready||!family_terrain_blend_config_current()||
    !family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_peek_draw(fc_frame)||
    !b313_family_observer_frame_current(fc_source,&fc_identity))return false;
 unsigned x=off%320,y=off/320;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)
  if(hd_owner[(y*8+sy)*2560+x*8+sx]!=1)return false;
 return true;
}
static void family_building_blend_cell_begin(unsigned x,unsigned y,unsigned owner,Uint8 native)
{
 ++fbb.frame_eligible;++fbb.total_eligible;
 fbb.last_x=(int)x;fbb.last_y=(int)y;fbb.last_before_slot_plus1=owner;
 fbb.last_native_index=native;fbb.last_native_rgb=palette_rgb(native);
 fbb.last_complete=fbb.last_ownership_cleared=false;fbb.last_subpixel_writes=0;
 fbb.last_store_min=UINT_MAX;fbb.last_store_max=0;
}
static void family_building_blend_store_observed(const Uint32 *pixel)
{
 size_t n=((uintptr_t)pixel-(uintptr_t)canvas->pixels)/sizeof *pixel;
 ++fbb.last_subpixel_writes;
 if(n<fbb.last_store_min)fbb.last_store_min=(unsigned)n;
 if(n>fbb.last_store_max)fbb.last_store_max=(unsigned)n;
}
static void family_pixel(SDL_Surface *s,Uint8 *address,int style)
{
 if(!fc.frame_active||fc.frame_failed)return;
 if(!family_terrain_blend_config_current()){family_fault(FC_CONFIG);return;}
 /* Unknown effects poison only the explicitly requested new mode even if
  * the first terrain tile has not yet prepared the canvas. */
 if(fct.requested&&style!=MIRROR_NORMAL&&style!=MIRROR_SHADOW&&style!=MIRROR_BLEND){family_fault(FC_EFFECT);return;}
 if(!fg_writer_entry()){family_fault(FC_GROUND);return;}
 if(!b313_family_writer_pixel(s,address)){family_fault(FC_WRITER);return;}
 if(s!=fc_source){if(fc_native_call)family_fault(FC_ORDER);return;}
 if(!family_geometry(false)){family_fault(FC_CONTEXT);return;}
 uintptr_t off=(uintptr_t)address-(uintptr_t)fc_source_pixels;
 if(off>=64000){family_fault(FC_CONTEXT);return;}
 /* Snapshot only after storage validation, before native-written revokes
  * the terrain provenance masks. Nonterrain owners cannot acquire this bit. */
 if(fc_canvas_ready&&!family_geometry(true)){family_fault(FC_CONTEXT);return;}
 unsigned building_owner=fbb_owner[off];
 /* Revoke before every private writer can return. Valid shadows retain the
  * prior receipt; an invalid shadow faults/revokes the entire frame. */
 if(style!=MIRROR_SHADOW)fbb_owner[off]=0;
 bool terrain_owned=style==MIRROR_BLEND&&fc_canvas_ready&&fg_terrain_cell_survives((unsigned)off);
 unsigned x=(unsigned)off%320,y=(unsigned)off/320;Uint8 before=expected[off];expected[off]=*address;++fc.native_pixels;fg_native_written((unsigned)off,style);
 if(!fc_canvas_ready)return;
 if(!family_geometry(true)){family_fault(FC_CONTEXT);return;}
 /* Retire before every private early-return writer. Preserve the prior owner
  * for the generic blend path. Shadows retain ownership until validated. */
 bool enemy_shot_owned=es_retire((unsigned)off,style);
 bool combat_owned=cb_retire((unsigned)off,style);
 bool ship_owned=ps_retire((unsigned)off,style);
 bool tank_owned=t194_retire((unsigned)off,style);
 bool fork_owned=f284_retire((unsigned)off,style);
 bool late_actor_owned=la_retire((unsigned)off,style);
 bool tall_owned=ts_retire((unsigned)off,style);
 bool linked_normal_owned=ln_retire((unsigned)off,style);
 bool turret_owned=tp_retire((unsigned)off,style);
 bool launcher_owned=lpf_retire((unsigned)off,style);
 bool rock_owned=smallrocks_retire((unsigned)off,style);
 bool random_prop_owned=rp_retire((unsigned)off,style);
 bool firing_rock_owned=fr462_retire((unsigned)off,style);
 bool linked_prop_owned=lp287_retire((unsigned)off,style);
 bool compound_owned=c309_retire((unsigned)off,style);
 if(es_pixel(x,y,style))return;
 if(cb_pixel(x,y,style,before)){
  /* The authenticated combat callback consumed the same native shadow.
   * Preserve each actually retained prior owner's existing receipt once,
   * just as the unchanged generic shadow path below does. No RGB store. */
  if(!fc.frame_failed&&style==MIRROR_SHADOW){
   if(ship_owned)ps_shadow((unsigned)off);
   if(rock_owned)smallrocks_shadow((unsigned)off);
   if(random_prop_owned)rp_shadow((unsigned)off);
   if(firing_rock_owned)fr462_shadow((unsigned)off);
   if(linked_prop_owned)lp287_shadow((unsigned)off);
   if(compound_owned)c309_shadow((unsigned)off);
   if(fork_owned)f284_shadow((unsigned)off);
   if(late_actor_owned)la_shadow((unsigned)off);
   if(tall_owned)ts_shadow((unsigned)off);
   if(linked_normal_owned)ln_shadow((unsigned)off);
   if(turret_owned)tp_shadow((unsigned)off);
   if(launcher_owned)lpf_shadow((unsigned)off);
   if(tank_owned)t194_shadow((unsigned)off);
  }
  return;
 }
 if(ps_pixel(x,y,style))return;
 if(t194_pixel(x,y,style))return;
 if(f284_pixel(x,y,style))return;
 if(la_pixel(x,y,style))return;
 if(ts_pixel(x,y,style))return;
 if(ln_pixel(x,y,style))return;
 if(tp_pixel(x,y,style))return;
 if(lpf_pixel(x,y,style))return;
 if(smallrocks_pixel(x,y,style))return;
 if(rp_pixel(x,y,style))return;
 if(fr462_pixel(x,y,style))return;
 if(lp287_pixel(x,y,style))return;
 if(c309_pixel(x,y,style))return;
 if(lamp272_pixel(x,y,style))return;
 if(triple275_pixel(x,y,style))return;
 if(private_ember269_pixel(x,y,style))return;
 if(gray325_pixel(x,y,style))return;
 if(longface573_pixel(x,y,style))return;
 if(fc_native_call){
  lamp272_clear((unsigned)off);triple275_clear((unsigned)off);private_ember269_clear((unsigned)off);gray325_clear((unsigned)off);longface573_clear((unsigned)off);
  if(!suppress||style!=MIRROR_NORMAL||x<(unsigned)fc_call_rect.x||x>=(unsigned)(fc_call_rect.x+12)||y<(unsigned)fc_call_rect.y||y>=(unsigned)(fc_call_rect.y+fc_call_rect.h)||fc_call_pixels>=fc_call_expected){family_fault(FC_ORDER);return;}
  if(x!=(unsigned)fc_call_rect.x+fc_call_pixels%12||y!=(unsigned)fc_call_rect.y+fc_call_pixels/12){family_fault(FC_ORDER);return;}
  fbb_owner[off]=(uint8_t)(fce.last_slot+1);++fbb.frame_claimed;++fbb.total_claimed;
  ++fc_call_pixels;return;
 }
 if(suppress){family_fault(FC_ORDER);return;}
 if(style!=MIRROR_NORMAL&&style!=MIRROR_SHADOW&&style!=MIRROR_BLEND){family_fault(FC_EFFECT);return;}
 bool triple_owned=triple275_cell((unsigned)off);
 bool ember_owned=private_ember269_cell((unsigned)off);
 bool lamp_owned=lamp272_cell((unsigned)off);
 bool gray_owned=gray325_cell((unsigned)off);
 bool longface_owned=longface573_cell((unsigned)off);
 if(longface_owned&&style==MIRROR_BLEND)longface573_blend_retired();
 if(gray_owned&&style==MIRROR_BLEND)gray325_blend_retired();
 if(triple_owned&&style==MIRROR_BLEND)triple275_blend_retired();
 if(ember_owned&&style==MIRROR_BLEND)private_ember269_blend_retired();
 if(lamp_owned&&style==MIRROR_BLEND)lamp272_blend_retired();
 if(style!=MIRROR_SHADOW){lamp272_clear((unsigned)off);triple275_clear((unsigned)off);private_ember269_clear((unsigned)off);gray325_clear((unsigned)off);longface573_clear((unsigned)off);}
 if(terrain_owned){
  if(!fbr.frame_eligible){fbr.first_x=(int)x;fbr.first_y=(int)y;}
  ++fbr.frame_eligible;++fbr.total_eligible;
 }
 bool terrain_retire=terrain_owned&&fbr.frame_enabled;
 bool building_retire=style==MIRROR_BLEND&&family_building_blend_current((unsigned)off,building_owner);
 if(building_retire)family_building_blend_cell_begin(x,y,building_owner,*address);
 /* Discard only a known generic native blend outside the fixed copied world
  * crop. No owner is inferred, and all earlier writer/style/actor gates stand. */
 bool offcrop_retire=fcoc.frame_enabled&&style==MIRROR_BLEND&&family_offcrop_cell(x,y);
 bool offcrop_bypassed=false;
 if(offcrop_retire&&!lamp_owned&&!gray_owned&&!longface_owned&&!triple_owned&&
    !ember_owned&&!enemy_shot_owned&&!combat_owned&&!ship_owned&&!rock_owned&&!random_prop_owned&&!firing_rock_owned&&!linked_prop_owned&&!fork_owned&&!late_actor_owned&&!tall_owned&&!linked_normal_owned&&!launcher_owned&&!tank_owned&&!terrain_retire&&!building_retire){
  for(unsigned sy=0;sy<8&&!offcrop_bypassed;sy++)for(unsigned sx=0;sx<8;sx++)
   if(hd_owner[(y*8+sy)*2560+x*8+sx]){offcrop_bypassed=true;break;}
  if(offcrop_bypassed)family_offcrop_cell_begin(x,y,*address);
 }
 if(selected[off]){++fc.occlusions;selected[off]=0;}
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *pixel=(Uint32 *)canvas->pixels+n;
  if(style==MIRROR_BLEND&&hd_owner[n]&&!lamp_owned&&!gray_owned&&!longface_owned&&!triple_owned&&!ember_owned&&!enemy_shot_owned&&!combat_owned&&!ship_owned&&!rock_owned&&!random_prop_owned&&!firing_rock_owned&&!linked_prop_owned&&!fork_owned&&!late_actor_owned&&!tall_owned&&!linked_normal_owned&&!launcher_owned&&!tank_owned&&!terrain_retire&&!offcrop_retire&&!building_retire){++fc.blend_fallbacks;family_fault(FC_EFFECT);return;}
  if(style==MIRROR_SHADOW&&(hd_owner[n]||cb_extra(n)||fr462_extra(n)||es_extra(n)||la_extra(n)||ts_extra(n)||ln_extra(n)||tp_extra(n)||lpf_extra(n))){
   if(*address!=(Uint8)((before&240)|((before&15)/2))){family_fault(FC_EFFECT);return;}
   *pixel=darken_rgba(*pixel,255);++fc.shadow_pixels;
  }else{*pixel=palette_rgb(*address);hd_owner[n]=0;}
  cloud_owner[n]=0;green_first[n]=0;
  if(building_retire){
   green_under_owner[n]=0;
   OHS_SURVIVAL_WRITE(canvas,pixel,14);
   family_building_blend_store_observed(pixel);
  }
  if(offcrop_bypassed)family_offcrop_store_observed(pixel);
 }
 if(building_retire){
  /* Completion is recorded only after all actual stores and owner clears. */
  fbb_retired[off]=1;++fbb.frame_retired;++fbb.total_retired;
  fbb.last_complete=fbb.last_subpixel_writes==64;
  fbb.last_ownership_cleared=fbb_owner[off]==0;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   size_t n=(y*8+sy)*2560+x*8+sx;
   if(hd_owner[n]||cloud_owner[n]||green_first[n]||green_under_owner[n])fbb.last_ownership_cleared=false;
  }
 }
 if(offcrop_bypassed)family_offcrop_cell_end(x,y);
 if(style==MIRROR_SHADOW&&ship_owned)ps_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&rock_owned)smallrocks_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&random_prop_owned)rp_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&firing_rock_owned)fr462_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&linked_prop_owned)lp287_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&compound_owned)c309_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&fork_owned)f284_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&late_actor_owned)la_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&tall_owned)ts_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&linked_normal_owned)ln_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&turret_owned)tp_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&launcher_owned)lpf_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&tank_owned)t194_shadow((unsigned)off);
 /* Record only a completed 64-pixel retirement, never an attempted write. */
 if(terrain_retire){fbr_retired[off]=1;++fbr.frame_retired;++fbr.total_retired;}
}
static void family_rect(SDL_Surface *s,const SDL_Rect *rect)
{
 if(!fc.frame_active||fc.frame_failed)return;
 if(!b313_family_writer_rect_begin(s,rect)){family_fault(FC_WRITER);return;}
 if(!family_indexed(s)){family_fault(FC_CONTEXT);return;}
 int x0=rect?rect->x:0,y0=rect?rect->y:0,x1=rect?rect->x+rect->w:320,y1=rect?rect->y+rect->h:200;
 x0=MAX(0,x0);y0=MAX(0,y0);x1=MIN(320,x1);y1=MIN(200,y1);
 for(int y=y0;y<y1;y++)for(int x=x0;x<x1;x++)family_pixel(s,(Uint8 *)s->pixels+y*320+x,MIRROR_NORMAL);
 if(!b313_family_writer_rect_end(s))family_fault(FC_WRITER);
}
bool render_mirror_family_tile(SDL_Surface *s,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!render_mirror_family_requested())return false;
 if(fct.requested&&(fc.frame_active||fc.ready)&&slot<100&&enemy[slot].enemytype>=313&&enemy[slot].enemytype<=316)fct.actor_attempt=true;
 if(!fc.frame_active||fc.frame_failed||!sheet)return false;
 if(!t194_before_tile(slot,part))return false;
 if(!f284_before_tile(slot,part))return false;
 if(!la_before_tile(slot,part))return false;
 if(!ts_before_tile(slot,part))return false;
 if(!ln_before_tile(slot,part))return false;
 if(!tp_before_tile(slot,part))return false;
 if(!lpf_before_tile(slot,part))return false;
 if(!rp_before_tile(slot,part))return false;
 if(!fr462_before_tile(slot,part)||!lp287_before_tile(slot,part)||!c309_before_tile(slot,part))return false;
 if(slot>=25&&slot<50&&(enemy[slot].enemytype==270||(enemy[slot].enemytype>=309&&enemy[slot].enemytype<=312)))return c309_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot>=25&&slot<50&&(enemy[slot].enemytype==287||enemy[slot].enemytype==288))return lp287_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<25&&enemy[slot].enemytype==462)return fr462_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot>=75&&slot<100&&enemy[slot].enemytype==194)return t194_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot>=50&&slot<75&&enemy[slot].enemytype==284)return f284_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&((enemy[slot].enemytype>=326&&enemy[slot].enemytype<=331)||(enemy[slot].enemytype>=343&&enemy[slot].enemytype<=348)))return ts_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype>=338&&enemy[slot].enemytype<=342)return ln_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&(enemy[slot].enemytype==271||enemy[slot].enemytype==463))return lpf_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==273)return tp_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&(enemy[slot].enemytype==282||enemy[slot].enemytype==283||enemy[slot].enemytype==285))return la_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<25&&(enemy[slot].enemytype==135||enemy[slot].enemytype==136||enemy[slot].enemytype==260||enemy[slot].enemytype==261||enemy[slot].enemytype==263||enemy[slot].enemytype==265))return rp_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==272)return lamp272_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==275)return triple275_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==269)return private_ember269_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<25&&enemy[slot].enemytype>=317&&enemy[slot].enemytype<=324)return smallrocks_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==325)return gray325_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype>=573&&enemy[slot].enemytype<=576)return longface573_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot>=100||enemy[slot].enemytype<313||enemy[slot].enemytype>316)return false;
 fg_before_actor();if(fc.frame_failed)return false;
 B313FamilyDrawBorrow b={0};
 if(!family_entry_config_current()||fc_native_call||suppress||!family_geometry(false)||s!=game_screen||s!=VGAScreen||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||!b313_family_observer_consume(s,slot,x,y,base,part,filter,sheet,*sheet,&b)){family_fault(FC_SOURCE);return false;}
 if(b.frame.session!=fc_session||b.frame.frame!=fc_frame||b.nonce<=fc.last_nonce||!family_entry_support(&b.plan,x,y,part)||!b313_family_cache_tile_current(&b.tile)){family_fault(FC_SOURCE);return false;}
 if(fc_has_identity&&memcmp(&fc_identity,&b.frame,sizeof fc_identity)){family_fault(FC_SOURCE);return false;}
 if(!fc_has_identity){fc_identity=b.frame;fc_has_identity=true;}
 if(!family_prepare_canvas()){family_fault(FC_ALLOCATION);return false;}
 Asset a={.initialized=true,.valid=true,.bank=158,.index=(int)(b.plan.phase*16+b.tile.tile_index),.w=12,.h=14,.density=8,.rgba=(Uint8 *)b.tile.rgba};
 fc_draw_lease=&a;bool drawn=draw_asset_filtered(x,y,&a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);fc_draw_lease=NULL;
 if(!drawn){family_fault(FC_ORDER);return false;}
 fc_native_call=true;fc_call_rect=(SDL_Rect){x,b.plan.support_y,12,(int)b.plan.visible_rows};
 fc_call_expected=b.plan.expected_callbacks;fc_call_pixels=0;fc.last_nonce=b.nonce;
 fce.last_nonce=b.nonce;fce.last_slot=slot;fce.last_part=(unsigned)part;
 fce.last_plan=b.plan;fce.last_callbacks=0;fce.last_complete=false;
 /* Empty calls consume identity/nonce and validate their native zero count,
  * but cannot create visible success or reopen the terrain path. */
 if(fc_call_expected){++fc.draws;++fc_frame_draws;++fc.phase_draws[b.plan.phase];fc.cycle_mask|=UINT64_C(1)<<(b.plan.cycle-1);}
 return true;
}
static void family_entity_end(void)
{
 es_end();cb_end();lamp272_end();triple275_end();private_ember269_end();smallrocks_end();rp_end();fr462_end();lp287_end();c309_end();ps_end();f284_end();la_end();ts_end();ln_end();tp_end();lpf_end();t194_end();gray325_end();longface573_end();
 if(fc_native_call){
  fce.last_callbacks=(unsigned)fc_call_pixels;
  if(!family_entry_config_current()||!b313_family_writer_draw_ready(fc_frame)||fc_call_pixels!=fc_call_expected)family_fault(FC_ORDER);
  fce.last_complete=!fc.frame_failed;
  if(fce.last_complete){
   if(!fc_call_expected){++fce.frame_empty_calls;++fce.total_empty_calls;}
   else {++fce.frame_visible_calls;++fce.total_visible_calls;
    if(fce.last_plan.source_row0){++fce.frame_partial_calls;++fce.total_partial_calls;}}
  }
 }
 fc_native_call=false;fc_draw_lease=NULL;suppress=suppress_green_smoke=suppress_cloud=false;
}
/* Shared pure snapshot gate. This validates only the same pre-ground token;
 * neither this helper nor a support receipt can create/upgrade admission. */
static bool family_terrain_snapshot_current(void)
{
 if((!es_finish()||!cb_finish()||!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!smallrocks_finish()||!rp_finish()||!fr462_finish()||!lp287_finish()||!c309_finish()||!ps_finish()||!f284_finish()||!la_finish()||!ts_finish()||!ln_finish()||!tp_finish()||!lpf_finish()||!t194_finish()||!private_gray325_finish()||!private_longface573_finish()))return false;
 if(!fct.requested||!fct.has_context||fct.actor_attempt||fc_frame_draws||fc_has_identity||
    fc.frame_failed||!family_terrain_blend_config_current()||!family_terrain_requested()||!fc_canvas_ready||
    !b313_family_observer_terrain_context_current(fc_source,&fct.context)||
    !b313_family_writer_peek_current(fc_frame)||!family_geometry(true)||
    memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!fg_terrain_snapshot_current()||!fg_terrain_survives())return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 for(int y=0;y<184;y++)if(memcmp((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264))return false;
 return true;
}
/* Actual finish/Present still use the original mutating writer and ground
 * validation; only the independent read-only receipt uses the pure guards. */
static bool family_terrain_current(void)
{
 if(!es_guard()||!cb_guard()||!f284_guard()||!la_guard()||!ts_guard()||!ln_guard()||!tp_guard()||!lpf_guard()||!t194_guard()||!rp_guard()||!fr462_guard()||!lp287_guard()||!c309_guard())return false;
 return b313_family_writer_current(fc_frame)&&fg_final_check()&&family_terrain_snapshot_current();
}
static void family_finish(MirrorOutputKind kind)
{
 if(!fc.frame_active)return;
 if(!family_terrain_blend_config_current())family_fault(FC_CONFIG);
 if((!es_guard()||!cb_guard()||!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!smallrocks_finish()||!rp_guard()||!fr462_guard()||!lp287_guard()||!c309_guard()||!ps_finish()||!f284_guard()||!la_guard()||!ts_guard()||!ln_guard()||!tp_guard()||!lpf_guard()||!t194_guard()||!private_gray325_finish()||!private_longface573_finish()))family_fault(FC_SOURCE);
 if(!fg_final_check())family_fault(FC_GROUND);
 if(fc_native_call||suppress)family_fault(FC_ORDER);
 if(!fc.frame_failed&&(!b313_family_writer_seal(fc_frame)||!family_geometry(fc_canvas_ready)))family_fault(FC_WRITER);
 if(!fc.frame_failed&&memcmp(fc_palette,rgb_palette,sizeof fc_palette))family_fault(FC_PALETTE);
 if(!fc.frame_failed&&kind!=MIRROR_OUTPUT_ORDINARY)family_fault(FC_OUTPUT);
 if(!fc.frame_failed&&fc_frame_draws&&(!fc_has_identity||!b313_family_observer_frame_current(fc_source,&fc_identity)))family_fault(FC_SOURCE);
 if(!fc.frame_failed)for(int i=0;i<64000;i++)if(expected[i]!=((Uint8 *)fc_source_pixels)[i]){family_fault(FC_WRITER);break;}
 if(!fc.frame_failed&&fc_frame_draws){
  if(!family_upscale_8x(output,VGAScreenSeg))family_fault(FC_CONTEXT);
  else for(int y=0;y<184;y++)if(memcmp((Uint8 *)VGAScreenSeg->pixels+y*320,(Uint8 *)game_screen->pixels+y*320+24,264)){family_fault(FC_OUTPUT);break;}
  if(!fc.frame_failed){for(int y=0;y<1472;y++)memcpy((Uint8 *)output->pixels+y*10240,(Uint8 *)canvas->pixels+y*10240+192*4,2112*4);fc.ready=true;++fc.accepted_frames;fg_on_accept();}
 }
 /* The actor block above is unchanged. Latch its original admission and
  * never retry its failed/attempted path as terrain. */
 if(fc.ready)fct.mode=FCT_ACTOR;
 else if(!fc.frame_failed&&fct.requested&&!fc_frame_draws&&!fc_has_identity&&!fct.actor_attempt&&family_terrain_current()){
  if(!family_upscale_8x(output,VGAScreenSeg))family_fault(FC_CONTEXT);
  else {
   for(int y=0;y<1472;y++)memcpy((Uint8 *)output->pixels+y*10240,(Uint8 *)canvas->pixels+y*10240+192*4,2112*4);
   fct.mode=FCT_TERRAIN;fc.ready=true;++fc.accepted_frames;++fct_status.accepted_frames;fg_on_accept();
  }
 }
 if(fc.ready)render_mirror_persistent_hud_compose();
 es_accept();cb_accept();lamp272_accept();triple275_accept();private_ember269_accept();smallrocks_accept();rp_accept();fr462_accept();lp287_accept();c309_accept();ps_accept();f284_accept();la_accept();ts_accept();ln_accept();tp_accept();lpf_accept();t194_accept();gray325_accept();longface573_accept();
 if(!fc.ready)++fc.fallback_frames;
 if(game_probe_capture_tick()&&fc.ready){char name[64];snprintf(name,sizeof name,"family-display-%04u.bmp",game_probe_tick);game_probe_export(output,name);}
 fc.frame_active=false;active=ready=false;last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
}
/* Separate terrain Present: actor failure can never arrive here. */
static bool family_terrain_present(SDL_Renderer *renderer,SDL_Surface *src,const SDL_Rect *dst)
{
 if(fct.mode!=FCT_TERRAIN||!fc.ready||fc.frame_failed)return false;
 if(!renderer||!dst||dst->w<=0||dst->h<=0||src!=fc_output||!family_terrain_current()){family_fault(FC_PRESENT);return false;}
 ph_present();
 int rw=0,rh=0;if(SDL_GetRendererOutputSize(renderer,&rw,&rh)||dst->x<0||dst->y<0||(int64_t)dst->x+dst->w>rw||(int64_t)dst->y+dst->h>rh){family_fault(FC_PRESENT);return false;}
 if(!texture){texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,2560,1600);fc_texture_renderer=renderer;}
 if(fc_texture_renderer!=renderer){family_fault(FC_PRESENT);return false;}
 Uint32 format=0;int access=0,w=0,h=0;
 if(!texture||SDL_QueryTexture(texture,&format,&access,&w,&h)||format!=SDL_PIXELFORMAT_ARGB8888||access!=SDL_TEXTUREACCESS_STREAMING||w!=2560||h!=1600||SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)||SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_NONE)){family_fault(FC_PRESENT);return false;}
 SDL_ScaleMode scale=SDL_ScaleModeLinear;SDL_BlendMode blend=SDL_BLENDMODE_BLEND;
 SDL_Texture *locked_texture=texture;
 void *pixels=NULL;int pitch=0;if(SDL_LockTexture(locked_texture,NULL,&pixels,&pitch)){family_fault(FC_PRESENT);return false;}
 /* Nothing touches texture storage before this second complete validation.
  * A lock callback, palette/writer gap, late actor or lifecycle boundary is
  * terminal for this frame; unlock and take the native fallback. */
 if(!pixels||pitch<10240||fct.mode!=FCT_TERRAIN||!fc.ready||src!=fc_output||
    texture!=locked_texture||fc_texture_renderer!=renderer||
    SDL_GetRendererOutputSize(renderer,&rw,&rh)||dst->x<0||dst->y<0||dst->w<=0||dst->h<=0||
    (int64_t)dst->x+dst->w>rw||(int64_t)dst->y+dst->h>rh||
    SDL_QueryTexture(texture,&format,&access,&w,&h)||format!=SDL_PIXELFORMAT_ARGB8888||
    access!=SDL_TEXTUREACCESS_STREAMING||w!=2560||h!=1600||
    SDL_GetTextureScaleMode(locked_texture,&scale)||scale!=SDL_ScaleModeNearest||
    SDL_GetTextureBlendMode(locked_texture,&blend)||blend!=SDL_BLENDMODE_NONE||
    texture!=locked_texture||fc_texture_renderer!=renderer||!family_terrain_current()){SDL_UnlockTexture(locked_texture);family_fault(FC_PRESENT);return false;}
 ph_present();
 for(int y=0;y<1600;y++)memcpy((Uint8 *)pixels+(size_t)y*(size_t)pitch,(Uint8 *)output->pixels+y*10240,10240);
 SDL_UnlockTexture(locked_texture);
 if(SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,texture,NULL,dst)){family_fault(FC_PRESENT);return false;}
 asset_debug_readback(renderer);fc.ready=false;fct.mode=FCT_NONE;SDL_RenderPresent(renderer);++fc.presents;++fct_status.presents;fg_on_present();return true;
}
static bool family_present(SDL_Renderer *renderer,SDL_Surface *src,const SDL_Rect *dst)
{
 if((fc.ready||fc.frame_active)&&!family_terrain_blend_config_current()){family_fault(FC_CONFIG);return false;}
 if(fct.mode==FCT_TERRAIN)return family_terrain_present(renderer,src,dst);
 if(!fc.ready||fc.frame_failed)return false;
 if((!es_guard()||!cb_guard()||!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!smallrocks_finish()||!rp_guard()||!fr462_guard()||!lp287_guard()||!c309_guard()||!ps_finish()||!f284_guard()||!la_guard()||!ts_guard()||!ln_guard()||!tp_guard()||!lpf_guard()||!t194_guard()||!private_gray325_finish()||!private_longface573_finish())){family_fault(FC_SOURCE);return false;}
 if(!fg_final_check())return false;
 if(!renderer||!dst||dst->w<=0||dst->h<=0||src!=fc_output||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_current(fc_frame)||!b313_family_observer_frame_current(fc_source,&fc_identity)){family_fault(FC_PRESENT);return false;}
 ph_present();
 int rw=0,rh=0;if(SDL_GetRendererOutputSize(renderer,&rw,&rh)||dst->x<0||dst->y<0||(int64_t)dst->x+dst->w>rw||(int64_t)dst->y+dst->h>rh){family_fault(FC_PRESENT);return false;}
 if(!texture){texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,2560,1600);fc_texture_renderer=renderer;}
 if(fc_texture_renderer!=renderer){family_fault(FC_PRESENT);return false;}
 Uint32 format=0;int access=0,w=0,h=0;
 if(!texture||SDL_QueryTexture(texture,&format,&access,&w,&h)||format!=SDL_PIXELFORMAT_ARGB8888||access!=SDL_TEXTUREACCESS_STREAMING||w!=2560||h!=1600||SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)||SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_NONE)){family_fault(FC_PRESENT);return false;}
 void *pixels=NULL;int pitch=0;if(SDL_LockTexture(texture,NULL,&pixels,&pitch)){family_fault(FC_PRESENT);return false;}
 if(!pixels||pitch<10240||(!es_guard()||!cb_guard()||!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!smallrocks_finish()||!rp_guard()||!fr462_guard()||!lp287_guard()||!c309_guard()||!ps_finish()||!f284_guard()||!la_guard()||!ts_guard()||!ln_guard()||!tp_guard()||!lpf_guard()||!t194_guard()||!private_gray325_finish()||!private_longface573_finish())||!fc.ready||fc.frame_failed||
    !family_terrain_blend_config_current()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_current(fc_frame)||!b313_family_observer_frame_current(fc_source,&fc_identity)){SDL_UnlockTexture(texture);family_fault(FC_PRESENT);return false;}
 ph_present();
 for(int y=0;y<1600;y++)memcpy((Uint8 *)pixels+y*pitch,(Uint8 *)output->pixels+y*10240,10240);
 SDL_UnlockTexture(texture);
 if(SDL_SetRenderDrawColor(renderer,0,0,0,255)||SDL_RenderClear(renderer)||SDL_RenderCopy(renderer,texture,NULL,dst)){family_fault(FC_PRESENT);return false;}
 asset_debug_readback(renderer);fc.ready=false;SDL_RenderPresent(renderer);++fc.presents;fg_on_present();return true;
}
bool render_mirror_terrain_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=64000||fct.mode!=FCT_TERRAIN||!fc.ready||!family_terrain_snapshot_current())return false;
 memset(out,0,bytes);
 for(unsigned y=0;y<184;y++)for(unsigned x=24;x<288;x++)
  if(fg_terrain_cell_survives(y*320+x))out[y*320+x]=1;
 return true;
}
B313TerrainContinuityStatus render_mirror_terrain_continuity_status(void)
{B313TerrainContinuityStatus status=fct_status;status.requested=family_terrain_requested();return status;}
B313FamilyCanvasStatus render_mirror_family_status(void){return fc;}
void render_mirror_family_report(void)
{
 fg_report();
 if(!render_mirror_family_requested()||!fc.frames)return;
 FILE *f=fopen("building313-family-canvas.json.tmp","w");if(!f){fprintf(stderr,"B313_FAMILY_CANVAS_REPORT_FAILED\n");return;}
 fprintf(f,"{\"schema\":1,\"frames\":%llu,\"draws\":%llu,\"accepted_frames\":%llu,\"fallback_frames\":%llu,\"presents\":%llu,\"occlusions\":%llu,\"phase_draws\":[%llu,%llu,%llu],\"cycle_mask\":%llu,\"first_reason\":%u,\"native_pixels\":%llu,\"shadow_pixels\":%llu,\"blend_fallbacks\":%llu,\"production_enabled\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\"}\n",(unsigned long long)fc.frames,(unsigned long long)fc.draws,(unsigned long long)fc.accepted_frames,(unsigned long long)fc.fallback_frames,(unsigned long long)fc.presents,(unsigned long long)fc.occlusions,(unsigned long long)fc.phase_draws[0],(unsigned long long)fc.phase_draws[1],(unsigned long long)fc.phase_draws[2],(unsigned long long)fc.cycle_mask,fc.first_reason,(unsigned long long)fc.native_pixels,(unsigned long long)fc.shadow_pixels,(unsigned long long)fc.blend_fallbacks);
 bool bad=ferror(f);int c=fclose(f);if(bad||c||rename("building313-family-canvas.json.tmp","building313-family-canvas.json"))fprintf(stderr,"B313_FAMILY_CANVAS_REPORT_FAILED\n");
}

B313TerrainBlendRetireStatus render_mirror_terrain_blend_retire_status(void)
{B313TerrainBlendRetireStatus status=fbr;status.requested=family_terrain_blend_requested();return status;}
bool render_mirror_terrain_blend_retire_mask(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=sizeof fbr_retired||!fbr.frame||fbr.frame!=fc_frame)return false;
 memcpy(out,fbr_retired,bytes);return true;
}
bool render_mirror_terrain_blend_cell(unsigned off)
{
 return fc.frame_active&&!fc.frame_failed&&fc_canvas_ready&&family_geometry(true)&&
  family_terrain_blend_config_current()&&!memcmp(fc_palette,rgb_palette,sizeof fc_palette)&&
  fg_terrain_cell_survives(off);
}
bool render_mirror_terrain_blend_snapshot(uint32_t *pixels,size_t count,uint8_t *owners,size_t owner_bytes)
{
 /* Readback only, deliberately available after a callback faults the frame.
  * It confers no eligibility, currentness, readiness or presentation grant. */
 if(!pixels||count!=4096000||!fbr.frame||fbr.frame!=fc_frame||!fc_canvas_ready||
    !family_geometry(true)||(owners?owner_bytes!=4096000:owner_bytes!=0))return false;
 memcpy(pixels,canvas->pixels,count*sizeof *pixels);
 if(owners)memcpy(owners,hd_owner,owner_bytes);
 return true;
}

B313BuildingBlendRetireStatus render_mirror_building_blend_retire_status(void)
{B313BuildingBlendRetireStatus out=fbb;out.requested=family_building_blend_requested();return out;}
bool render_mirror_building_blend_retire_mask(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=sizeof fbb_retired||!fbb.frame||fbb.frame!=fc_frame)return false;
 memcpy(out,fbb_retired,bytes);return true;
}
bool render_mirror_building_blend_owner(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=sizeof fbb_owner||!fbb.frame||fbb.frame!=fc_frame)return false;
 memcpy(out,fbb_owner,bytes);return true;
}
bool render_mirror_building_blend_cell_snapshot(unsigned off,uint32_t *pixels,uint8_t *owners,size_t count)
{
 if(off>=64000||!pixels||!owners||count!=64||!fc_canvas_ready||
    canvas!=fc_canvas_surface||!family_rgb(canvas)||canvas->pixels!=fc_canvas_pixels||
    hd_owner!=fc_owner||cloud_owner!=fc_cloud||green_first!=fc_green_first||
    green_under_owner!=fc_green_owner||!hd_owner||!cloud_owner||!green_first||!green_under_owner)return false;
 unsigned x=off%320,y=off/320;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;unsigned k=sy*8+sx;
  pixels[k]=((const Uint32 *)canvas->pixels)[n];
  owners[k]=(hd_owner[n]?1:0)|(cloud_owner[n]?2:0)|(green_first[n]?4:0)|(green_under_owner[n]?8:0);
 }
 return true;
}
