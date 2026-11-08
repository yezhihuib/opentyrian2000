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

/* Independent frame-bound opt-in. Diagnostics never grant ownership. */
static B313TerrainBlendRetireStatus fbr;
static uint8_t fbr_retired[64000];
static bool family_terrain_blend_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_TERRAIN_BLEND_RETIRE_ENABLE");
 return e&&!strcmp(e,"1");
#else
 return false;
#endif
}
static bool family_terrain_blend_config_current(void)
{return fbr.frame_enabled==family_terrain_blend_requested();}

static SDL_Rect fc_call_rect;
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
{if(!fc.frame_active&&!fc.ready)return;if(!fc.first_reason)fc.first_reason=reason;if(!fbr.first_reason)fbr.first_reason=reason;fc.frame_failed=true;fc.ready=false;ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
static void family_reset(void)
{
 private_lamp272_reset();private_triple275_reset();private_ember269_reset();f284_reset();tp_reset();private_gray325_reset();private_longface573_reset();
 fg_reset();
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
 private_lamp272_tick();private_triple275_tick();private_ember269_tick();f284_tick();tp_tick();private_gray325_tick();private_longface573_tick();
 memset(&fct,0,sizeof fct);fct.requested=family_terrain_requested();
 if(fct.requested)++fct_status.frames;
 B313FamilyObserverStatus s=b313_family_observer_status();
 fbr.frame=s.frame;fbr.frame_enabled=family_terrain_blend_requested();
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
static void family_pixel(SDL_Surface *s,Uint8 *address,int style)
{
 if(!fc.frame_active||fc.frame_failed)return;
 if(!tp_write_current()){tp_fail(20);family_fault(FC_SOURCE);return;}
 if(!f284_write_current()){f284_fail(20);family_fault(FC_SOURCE);return;}
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
 bool terrain_owned=style==MIRROR_BLEND&&fc_canvas_ready&&fg_terrain_cell_survives((unsigned)off);
 unsigned x=(unsigned)off%320,y=(unsigned)off/320;Uint8 before=expected[off];expected[off]=*address;++fc.native_pixels;fg_native_written((unsigned)off,style);
 if(!fc_canvas_ready)return;
 if(!family_geometry(true)){family_fault(FC_CONTEXT);return;}
 /* Retire sparse ownership before all early-return family writers. */
 bool fork_owned=f284_retire((unsigned)off,style);
 bool turret_owned=tp_retire((unsigned)off,style);
 if(f284_pixel(x,y,style))return;
 if(tp_pixel(x,y,style))return;
 if(lamp272_pixel(x,y,style))return;
 if(triple275_pixel(x,y,style))return;
 if(private_ember269_pixel(x,y,style))return;
 if(gray325_pixel(x,y,style))return;
 if(longface573_pixel(x,y,style))return;
 if(fc_native_call){
  lamp272_clear((unsigned)off);triple275_clear((unsigned)off);private_ember269_clear((unsigned)off);gray325_clear((unsigned)off);longface573_clear((unsigned)off);
  if(!suppress||style!=MIRROR_NORMAL||x<(unsigned)fc_call_rect.x||x>=(unsigned)(fc_call_rect.x+12)||y<(unsigned)fc_call_rect.y||y>=(unsigned)(fc_call_rect.y+14)||fc_call_pixels>=168){family_fault(FC_ORDER);return;}
  if(x!=(unsigned)fc_call_rect.x+fc_call_pixels%12||y!=(unsigned)fc_call_rect.y+fc_call_pixels/12){family_fault(FC_ORDER);return;}
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
 if(selected[off]){++fc.occlusions;selected[off]=0;}
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *pixel=(Uint32 *)canvas->pixels+n;
  if(style==MIRROR_BLEND&&hd_owner[n]&&!lamp_owned&&!gray_owned&&!longface_owned&&!triple_owned&&!ember_owned&&!fork_owned&&!turret_owned&&!terrain_retire){++fc.blend_fallbacks;family_fault(FC_EFFECT);return;}
  if(style==MIRROR_SHADOW&&hd_owner[n]){
   if(*address!=(Uint8)((before&240)|((before&15)/2))){family_fault(FC_EFFECT);return;}
   *pixel=darken_rgba(*pixel,255);++fc.shadow_pixels;
  }else{*pixel=palette_rgb(*address);hd_owner[n]=0;}
  cloud_owner[n]=0;green_first[n]=0;
 }
 /* Record only a completed 64-pixel retirement, never an attempted write. */
 if(style==MIRROR_SHADOW&&turret_owned)tp_shadow((unsigned)off);
 if(style==MIRROR_SHADOW&&fork_owned)f284_shadow((unsigned)off);
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
 if(!f284_before_tile(slot,part)||!tp_before_tile(slot,part))return false;
 if(slot<100&&enemy[slot].enemytype==273)return tp_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot>=50&&slot<75&&enemy[slot].enemytype==284)return f284_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==272)return lamp272_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==275)return triple275_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==269)return private_ember269_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype==325)return gray325_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot<100&&enemy[slot].enemytype>=573&&enemy[slot].enemytype<=576)return longface573_tile(s,slot,x,y,sheet,base,part,filter);
 if(slot>=100||enemy[slot].enemytype<313||enemy[slot].enemytype>316)return false;
 fg_before_actor();if(fc.frame_failed)return false;
 B313FamilyDrawBorrow b={0};
 if(fc_native_call||suppress||!family_geometry(false)||s!=game_screen||s!=VGAScreen||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||!b313_family_observer_consume(s,slot,x,y,base,part,filter,sheet,*sheet,&b)){family_fault(FC_SOURCE);return false;}
 if(b.frame.session!=fc_session||b.frame.frame!=fc_frame||b.nonce<=fc.last_nonce||b.plan.width!=12||b.plan.height!=14||b.plan.destination_x!=x||b.plan.destination_y!=y||!b313_family_cache_tile_current(&b.tile)){family_fault(FC_SOURCE);return false;}
 if(fc_has_identity&&memcmp(&fc_identity,&b.frame,sizeof fc_identity)){family_fault(FC_SOURCE);return false;}
 if(!fc_has_identity){fc_identity=b.frame;fc_has_identity=true;}
 if(!family_prepare_canvas()){family_fault(FC_ALLOCATION);return false;}
 Asset a={.initialized=true,.valid=true,.bank=158,.index=(int)(b.plan.phase*16+b.tile.tile_index),.w=12,.h=14,.density=8,.rgba=(Uint8 *)b.tile.rgba};
 fc_draw_lease=&a;bool drawn=draw_asset_filtered(x,y,&a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL);fc_draw_lease=NULL;
 if(!drawn){family_fault(FC_ORDER);return false;}
 fc_native_call=true;fc_call_rect=(SDL_Rect){x,y,12,14};fc_call_pixels=0;fc.last_nonce=b.nonce;++fc.draws;++fc_frame_draws;++fc.phase_draws[b.plan.phase];fc.cycle_mask|=UINT64_C(1)<<(b.plan.cycle-1);return true;
}
static void family_entity_end(void)
{
 lamp272_end();triple275_end();private_ember269_end();f284_end();tp_end();gray325_end();longface573_end();
 if(fc_native_call&&(!b313_family_writer_draw_ready(fc_frame)||fc_call_pixels!=168))family_fault(FC_ORDER);
 fc_native_call=false;fc_draw_lease=NULL;suppress=suppress_green_smoke=suppress_cloud=false;
}
/* Shared pure snapshot gate. This validates only the same pre-ground token;
 * neither this helper nor a support receipt can create/upgrade admission. */
static bool family_terrain_snapshot_current(void)
{
 if((!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!f284_finish()||!tp_finish()||!private_gray325_finish()||!private_longface573_finish()))return false;
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
 return b313_family_writer_current(fc_frame)&&fg_final_check()&&family_terrain_snapshot_current();
}
static void family_finish(MirrorOutputKind kind)
{
 if(!fc.frame_active)return;
 if(!family_terrain_blend_config_current())family_fault(FC_CONFIG);
 if((!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!f284_guard()||!tp_guard()||!private_gray325_finish()||!private_longface573_finish()))family_fault(FC_SOURCE);
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
 lamp272_accept();triple275_accept();private_ember269_accept();f284_accept();tp_accept();gray325_accept();longface573_accept();
 if(!fc.ready)++fc.fallback_frames;
 if(game_probe_capture_tick()&&fc.ready){char name[64];snprintf(name,sizeof name,"family-display-%04u.bmp",game_probe_tick);game_probe_export(output,name);}
 fc.frame_active=false;active=ready=false;last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
}
/* Separate terrain Present: actor failure can never arrive here. */
static bool family_terrain_present(SDL_Renderer *renderer,SDL_Surface *src,const SDL_Rect *dst)
{
 if(fct.mode!=FCT_TERRAIN||!fc.ready||fc.frame_failed)return false;
 if(!renderer||!dst||dst->w<=0||dst->h<=0||src!=fc_output||!family_terrain_current()){family_fault(FC_PRESENT);return false;}
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
 if((!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!f284_guard()||!tp_guard()||!private_gray325_finish()||!private_longface573_finish())){family_fault(FC_SOURCE);return false;}
 if(!fg_final_check())return false;
 if(!renderer||!dst||dst->w<=0||dst->h<=0||src!=fc_output||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_current(fc_frame)||!b313_family_observer_frame_current(fc_source,&fc_identity)){family_fault(FC_PRESENT);return false;}
 int rw=0,rh=0;if(SDL_GetRendererOutputSize(renderer,&rw,&rh)||dst->x<0||dst->y<0||(int64_t)dst->x+dst->w>rw||(int64_t)dst->y+dst->h>rh){family_fault(FC_PRESENT);return false;}
 if(!texture){texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,2560,1600);fc_texture_renderer=renderer;}
 if(fc_texture_renderer!=renderer){family_fault(FC_PRESENT);return false;}
 Uint32 format=0;int access=0,w=0,h=0;
 if(!texture||SDL_QueryTexture(texture,&format,&access,&w,&h)||format!=SDL_PIXELFORMAT_ARGB8888||access!=SDL_TEXTUREACCESS_STREAMING||w!=2560||h!=1600||SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)||SDL_SetTextureBlendMode(texture,SDL_BLENDMODE_NONE)){family_fault(FC_PRESENT);return false;}
 void *pixels=NULL;int pitch=0;if(SDL_LockTexture(texture,NULL,&pixels,&pitch)){family_fault(FC_PRESENT);return false;}
 if(!pixels||pitch<10240||(!private_lamp272_finish()||!private_triple275_finish()||!private_ember269_finish()||!f284_finish()||!tp_finish()||!private_gray325_finish()||!private_longface573_finish())||!fc.ready||fc.frame_failed||
    !family_terrain_blend_config_current()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
    !b313_family_writer_current(fc_frame)||!b313_family_observer_frame_current(fc_source,&fc_identity)){SDL_UnlockTexture(texture);family_fault(FC_PRESENT);return false;}
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
