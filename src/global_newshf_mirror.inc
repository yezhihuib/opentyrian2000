/* SPDX-License-Identifier: GPL-2.0-or-later
 * Default-off NEWSHF owner: finite, independently loaded authored groups.
 * Included after decode_tile; no level/episode/map predicate grants this owner. */
#include "current_newshf_hd_assets.h"
#include "current_linked_newshf_hd_assets.h"
#include "current_dualmissile_newshf_hd_assets.h"
enum { GLOBAL_NEWSHF_RESOURCE_COUNT=16 };
static Uint8 *global_newshf_rgba[GLOBAL_NEWSHF_RESOURCE_COUNT];
static uint64_t global_newshf_rgba_stamp[GLOBAL_NEWSHF_RESOURCE_COUNT];
static unsigned global_newshf_used_resources;
static bool global_newshf_linked_loaded,global_newshf_linked_good;
static bool global_newshf_dualmissile_loaded,global_newshf_dualmissile_good;
/* Per-allocation decision made before the first visible dualmissile quadrant. */
static uint64_t global_newshf_dual_preflight_generation[100];
static Uint8 global_newshf_dual_preflight_state[100];
static bool global_newshf_assets_match(void)
{
 for(unsigned i=0;i<GLOBAL_NEWSHF_RESOURCE_COUNT;i++)
  if((global_newshf_used_resources&(1u<<i))&&(!global_newshf_rgba[i]||global_bytes_hash(global_newshf_rgba[i],192u*224u*4u)!=global_newshf_rgba_stamp[i]))return false;
 return true;
}
static bool global_newshf_loaded,global_newshf_good,global_newshf_cached;
/* Survives ownership transfer (for example to antialiased HUD glyphs). */
static bool global_newshf_contributed,global_newshf_rejected_frame;

static size_t global_newshf_capacity;
static Uint32 global_newshf_output_palette[256],global_newshf_underlay_palette[256];
static Uint8 global_newshf_used_colors[256];
static struct {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;int pitch;} global_newshf_fade_lease;
static struct {
 SDL_Surface *surface,*final_surface,*canvas_surface,*output_surface;
 void *pixels,*final_pixels,*canvas_pixels,*output_pixels;
 SDL_PixelFormat *format,*final_format,*canvas_format,*output_format;
 int pitch,final_pitch,canvas_pitch,output_pitch,density;
} global_newshf_source_lease;
static bool global_newshf_talon_dependency;
static uint64_t global_newshf_shapesy_dependency,global_newshf_dual_shapesy_serial[100];
static struct {bool live;int x,y,style,filter;unsigned left;Uint8 source[168],mask[168],seen[168];} global_newshf_call;

static bool global_newshf_requested(void)
{return global_asset_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool global_newshf_palette_matches(void)
{return newshf_validation_palette();}
static Sprite2_array global_newshf_bank(void)
{const Sprite2_array *b=newshf_validation_bank();return b?*b:(Sprite2_array){0};}
static uint64_t global_newshf_generations[100],global_newshf_epoch;
static bool global_newshf_identity_complete(void)
{
 if(global_newshf_epoch!=newshf_validation_bank_epoch)return false;
 for(unsigned i=0;i<100;i++)if(global_newshf_generations[i]) {
  if(global_newshf_generations[i]!=newshf_validation_slots[i].generation||
   !newshf_validation_slots[i].role||newshf_validation_slots[i].remaining||
   !newshf_validation_shape(i))return false;
  if((newshf_profiles[newshf_validation_slots[i].profile].linked||newshf_validation_slots[i].profile>=6)&&
   (enemy[i].enemycycle!=newshf_validation_slots[i].pose||enemy[i].evalue!=newshf_validation_slots[i].value))return false;
 }
 return true;
}
static bool global_newshf_underlay_matches(void)
{
 for(unsigned i=0;i<256;i++)if(global_newshf_used_colors[i]&&
  (rgb_palette[i]&0xffffffu)!=global_newshf_underlay_palette[i])return false;
 return true;
}
static void global_newshf_use_color(unsigned i)
{if(!global_newshf_used_colors[i]){global_newshf_used_colors[i]=1;global_newshf_underlay_palette[i]=rgb_palette[i]&0xffffffu;}}
static bool global_newshf_source_matches(Sprite2_array bank)
{
 const Sprite2_array *b=newshf_validation_bank();
 return b&&b->data==bank.data&&b->size==bank.size&&newshf_validation_bank_valid(b)&&newshf_validation_records();
}
static bool global_newshf_disjoint(const SDL_Surface *a,const SDL_Surface *b)
{
 uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;
 return x<y?y-x>=(size_t)a->pitch*a->h:x-y>=(size_t)b->pitch*b->h;
}
static bool global_newshf_layout(void)
{
 int d=game_probe_density;
 if((d!=4&&d!=8)||!game_screen||!game_screen->pixels||!game_screen->format||
  game_screen->w!=320||game_screen->h!=200||game_screen->pitch!=320||game_screen->format->format!=SDL_PIXELFORMAT_INDEX8||
  game_screen->format->BitsPerPixel!=8||game_screen->format->BytesPerPixel!=1)return false;
 SDL_Surface *surfaces[2]={canvas,output};
 for(unsigned i=0;i<2;i++) {SDL_Surface *v=surfaces[i];if(!v||!v->pixels||!v->format||v->w!=320*d||v->h!=200*d||
  v->pitch<v->w*4||v->pitch%4||(uintptr_t)v->pixels%sizeof(Uint32)||
  v->format->format!=SDL_PIXELFORMAT_ARGB8888||v->format->BitsPerPixel!=32||v->format->BytesPerPixel!=4)return false;}
 SDL_Surface *f=VGAScreenSeg;
 if(!f||!f->pixels||!f->format||f->w!=320||f->h!=200||f->pitch<320||
  f->format->format!=SDL_PIXELFORMAT_INDEX8||f->format->BitsPerPixel!=8||f->format->BytesPerPixel!=1)return false;
 SDL_Surface *all[4]={game_screen,f,canvas,output};
 for(unsigned i=0;i<4;i++)for(unsigned j=0;j<i;j++)if(!global_newshf_disjoint(all[i],all[j]))return false;
 return true;
}
static bool global_newshf_final_surface_matches(void)
{
 SDL_Surface *s=VGAScreenSeg;
 return s&&s==global_newshf_source_lease.final_surface&&s->pixels&&s->pixels==global_newshf_source_lease.final_pixels&&
  s->format&&s->format==global_newshf_source_lease.final_format&&s->w==320&&s->h==200&&s->pitch>=320&&s->pitch==global_newshf_source_lease.final_pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1;
}
static bool global_newshf_surface_matches(void)
{
 SDL_Surface *s=game_screen;
 return global_newshf_layout()&&canvas==global_newshf_source_lease.canvas_surface&&output==global_newshf_source_lease.output_surface&&
  canvas->pixels==global_newshf_source_lease.canvas_pixels&&output->pixels==global_newshf_source_lease.output_pixels&&
  canvas->format==global_newshf_source_lease.canvas_format&&output->format==global_newshf_source_lease.output_format&&
  canvas->pitch==global_newshf_source_lease.canvas_pitch&&output->pitch==global_newshf_source_lease.output_pitch&&
  s&&s==global_newshf_source_lease.surface&&s->pixels&&s->pixels==global_newshf_source_lease.pixels&&
  s->format&&s->format==global_newshf_source_lease.format&&s->w==320&&s->h==200&&s->pitch==320&&s->pitch==global_newshf_source_lease.pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&
  game_probe_density==global_newshf_source_lease.density;
}


static bool global_newshf_group_ready(unsigned phase)
{
 if(phase>=GLOBAL_NEWSHF_RESOURCE_COUNT)return false;
 bool dual=phase>=15,linked=phase>=9&&!dual;
 bool *loaded=dual?&global_newshf_dualmissile_loaded:linked?&global_newshf_linked_loaded:&global_newshf_loaded;
 bool *good=dual?&global_newshf_dualmissile_good:linked?&global_newshf_linked_good:&global_newshf_good;
 unsigned begin=dual?15:linked?9:0,end=dual?16:linked?15:9;
 if(!*loaded){
  *loaded=true;*good=true;
  for(unsigned i=begin;i<end;i++){
   const GlobalAssetResource *r=dual?dualmissile_newshf_hd_resources+i-15:linked?linked_newshf_hd_resources+i-9:newshf_hd_resources+i;
   if(r->width!=24||r->height!=28||r->anchor_x!=6||r->anchor_y!=7||!(global_newshf_rgba[i]=global_resource_load(r)))*good=false;
   if(global_newshf_rgba[i])global_newshf_rgba_stamp[i]=global_bytes_hash(global_newshf_rgba[i],192u*224u*4u);
  }
  if(!*good)for(unsigned i=begin;i<end;i++){free(global_newshf_rgba[i]);global_newshf_rgba[i]=NULL;}
 }
 if(!*good)return false;
 for(unsigned i=begin;i<end;i++)if(!global_newshf_rgba[i]||global_bytes_hash(global_newshf_rgba[i],192u*224u*4u)!=global_newshf_rgba_stamp[i])return false;
 return true;
}
/* Historical harness entry point retains the old-nine contract. */
static bool global_newshf_family_ready(void){return global_newshf_group_ready(0);}
static void global_newshf_fail(void);
static void global_newshf_reset(void)
{
 /* Retire the actual RGB contribution before its proof bits. A still-active
  * legacy composition must not copy a disabled global owner's stale pixels. */
 if(global_newshf_frame) {
  bool safe=global_newshf_surface_matches();global_newshf_fail();
  if(!safe){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 }
 if(global_newshf_contributed){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 if(global_newshf_cached){ready=last_output_valid=have_fade_saved=false;fade_mode=0;}
 global_newshf_frame=global_newshf_cached=global_newshf_fault=global_newshf_contributed=false;global_newshf_call.live=false;
 global_newshf_talon_dependency=false;global_newshf_shapesy_dependency=0;memset(&global_newshf_source_lease,0,sizeof(global_newshf_source_lease));
 memset(&global_newshf_fade_lease,0,sizeof(global_newshf_fade_lease));
 if(global_newshf_owner)memset(global_newshf_owner,0,global_newshf_capacity);
 if(global_newshf_foreign)memset(global_newshf_foreign,0,global_newshf_capacity);
}
static void global_newshf_shutdown(void)
{
 global_newshf_reset();
 for(unsigned i=0;i<GLOBAL_NEWSHF_RESOURCE_COUNT;i++){free(global_newshf_rgba[i]);global_newshf_rgba[i]=NULL;}
 global_newshf_loaded=global_newshf_good=false;
 global_newshf_linked_loaded=global_newshf_linked_good=false;
 global_newshf_dualmissile_loaded=global_newshf_dualmissile_good=false;global_newshf_used_resources=0;
 free(global_newshf_owner);free(global_newshf_foreign);global_newshf_owner=global_newshf_foreign=NULL;global_newshf_capacity=0;
}
static void global_newshf_frame_begin(void)
{
 global_newshf_rejected_frame=false;global_newshf_used_resources=0;
 memset(global_newshf_dual_preflight_state,0,sizeof(global_newshf_dual_preflight_state));
 memset(global_newshf_dual_preflight_generation,0,sizeof(global_newshf_dual_preflight_generation));
 memset(global_newshf_dual_shapesy_serial,0,sizeof(global_newshf_dual_shapesy_serial));global_newshf_shapesy_dependency=0;
 memset(global_newshf_generations,0,sizeof(global_newshf_generations));global_newshf_epoch=newshf_validation_bank_epoch;
 global_newshf_frame=global_newshf_cached=global_newshf_fault=global_newshf_contributed=false;global_newshf_call.live=false;
 memset(global_newshf_used_colors,0,sizeof(global_newshf_used_colors));global_newshf_talon_dependency=false;
 if(!global_newshf_requested()||!global_newshf_layout()||!VGAScreenSeg||!VGAScreenSeg->pixels||!VGAScreenSeg->format||
  VGAScreenSeg->w!=320||VGAScreenSeg->h!=200||VGAScreenSeg->pitch<320||VGAScreenSeg->format->format!=SDL_PIXELFORMAT_INDEX8)return;
 size_t n=(size_t)canvas->w*canvas->h;
 if(global_newshf_capacity!=n) {
  Uint8 *owner=calloc(n,1),*foreign=calloc(n,1);
  if(!owner||!foreign){free(owner);free(foreign);return;}
  free(global_newshf_owner);free(global_newshf_foreign);global_newshf_owner=owner;global_newshf_foreign=foreign;global_newshf_capacity=n;
 }
 memset(global_newshf_owner,0,n);memset(global_newshf_foreign,0,n);
 global_newshf_source_lease.final_surface=VGAScreenSeg;global_newshf_source_lease.final_pixels=VGAScreenSeg->pixels;
 global_newshf_source_lease.final_format=VGAScreenSeg->format;global_newshf_source_lease.final_pitch=VGAScreenSeg->pitch;
 global_newshf_source_lease.canvas_surface=canvas;global_newshf_source_lease.canvas_pixels=canvas->pixels;
 global_newshf_source_lease.canvas_format=canvas->format;global_newshf_source_lease.canvas_pitch=canvas->pitch;
 global_newshf_source_lease.output_surface=output;global_newshf_source_lease.output_pixels=output->pixels;
 global_newshf_source_lease.output_format=output->format;global_newshf_source_lease.output_pitch=output->pitch;
 global_newshf_source_lease.surface=game_screen;global_newshf_source_lease.pixels=game_screen->pixels;
 global_newshf_source_lease.format=game_screen->format;global_newshf_source_lease.pitch=game_screen->pitch;global_newshf_source_lease.density=game_probe_density;
 global_newshf_frame=true;
}

static void global_newshf_fail(void)
{
 if(global_newshf_contributed)global_newshf_rejected_frame=true;
 global_newshf_fault=true;global_newshf_call.live=false;
 if(!global_newshf_surface_matches()||!canvas||!global_newshf_owner)return;
 int d=game_probe_density;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;if(!global_newshf_owner[n])continue;
  ((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch))[x]=palette_rgb(((Uint8 *)game_screen->pixels)[(y/d)*320+x/d]);
  global_newshf_owner[n]=global_newshf_foreign[n]=hd_owner[n]=cloud_owner[n]=0;
 }
}
static void global_newshf_observed_preflight(void)
{
 if(global_newshf_contributed&&(!global_newshf_requested()||!global_newshf_surface_matches()||
    !global_newshf_final_surface_matches()||!global_newshf_source_matches(global_newshf_bank())||
    !global_newshf_palette_matches()||!global_newshf_underlay_matches()))global_newshf_fail();
}
static int global_newshf_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int filter,unsigned phase,int part,uint64_t shapesy_serial)
{
 if(!global_newshf_requested()||!global_newshf_frame||global_newshf_fault||surface!=game_screen||
  !global_newshf_surface_matches()||(filter<0||filter>255)||
  !global_newshf_source_matches(bank)||!global_newshf_palette_matches()||!global_newshf_underlay_matches()){
  if(global_newshf_contributed)global_newshf_fail();return 0;}
 /* Native quadrant visibility is actor-based and can still issue an entirely
  * clipped top tile. Keep it classic without poisoning other valid quadrants.
  * Physical-row wrapping is likewise deliberately not reinterpreted as HD. */
 if(x<0||x>308){global_newshf_fail();return 0;}
 /* Missing optional art leaves this actor classic, not other groups revoked. */
 if(phase>=GLOBAL_NEWSHF_RESOURCE_COUNT){global_newshf_fail();return 0;}
 unsigned group_mask=phase<9?0x1ffu:phase<15?0x7e00u:0x8000u;
 if(!(phase<9?global_newshf_family_ready():global_newshf_group_ready(phase))){if(phase<9||(global_newshf_used_resources&group_mask))global_newshf_fail();return 0;}
 global_newshf_used_resources|=group_mask;
 if(global_newshf_call.live){global_newshf_fail();return 0;}
 memset(&global_newshf_call,0,sizeof(global_newshf_call));
 if(!decode_tile(bank,index,global_newshf_call.source,global_newshf_call.mask,12,0,0))return 0;
 for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(global_newshf_call.mask[yy*12+xx]&&y+yy>=0&&y+yy<200)++global_newshf_call.left;
 global_newshf_call.x=x;global_newshf_call.y=y;global_newshf_call.style=MIRROR_NORMAL;global_newshf_call.filter=filter;global_newshf_call.live=true;
 font_before_effect((SDL_Rect){x,y,12,14});
 int d=game_probe_density;const Uint8 *rgba=global_newshf_rgba[phase];
 int qx=part==1||part==20?12:0,qy=part==19||part==20?14:0;
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++) {
  int dx=x*d+ax,dy=y*d+ay;if(dy<0||dy>=canvas->h)continue;
  size_t n=(size_t)dy*canvas->w+dx;const Uint8 *a=rgba+4*((qy*8+ay*8/d)*192+qx*8+ax*8/d);
  Uint8 filtered[4];if(filter){enemy_filter_rgba(a,(Uint8)filter,filtered);a=filtered;for(unsigned c=0;c<16;c++)global_newshf_use_color((Uint8)(filter|c));}
  bool native=global_newshf_call.mask[(ay/d)*12+ax/d]!=0;
  if(!a[3]&&!native)continue;
  bool foreign=global_newshf_owner[n]?global_newshf_foreign[n]:hd_owner[n]!=0;
  /* Transparent or partial-alpha art needs a proven underlay. This finite
   * owner may retain its own RGB, never another owner's unproven lifetime. */
  if(a[3]<255&&foreign){
   Uint32 color=*((Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx);
   if(phase!=15||!shapesy_borrow_sample(shapesy_serial,n,color)||
      (global_newshf_shapesy_dependency&&global_newshf_shapesy_dependency!=shapesy_serial)){global_newshf_fail();return 0;}
   global_newshf_shapesy_dependency=shapesy_serial;foreign=false;
  }
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx;
  if(!hd_owner[n]) {Uint8 v=((Uint8 *)game_screen->pixels)[(dy/d)*320+dx/d];*p=palette_rgb(v);global_newshf_use_color(v);}
  else if(foreign)for(unsigned i=0;i<256;i++)global_newshf_use_color(i);
  /* Opaque art replaces foreign RGB; all nonopaque foreign sampling declined above. */
  if(a[3]) {unsigned alpha=a[3];
   *p=blend_rgba(*p,a,(int)alpha);
   if(alpha==255)foreign=false;
  }
  if(global_talon_owner)global_talon_owner[n]=global_talon_foreign[n]=0;
  if(global_rotor_owner)global_rotor_owner[n]=global_rotor_foreign[n]=0;
  if(global_projectile91_owner)global_projectile91_owner[n]=global_projectile91_foreign[n]=0;
  global_newshf_contributed=true;
  if(global_pulse_owner)global_pulse_owner[n]=global_pulse_foreign[n]=0;
  if(global_shield_owner)global_shield_owner[n]=global_shield_foreign[n]=0;
  if(global_vulcan_owner)global_vulcan_owner[n]=global_vulcan_foreign[n]=0;
  if(global_hitflare_owner)global_hitflare_owner[n]=global_hitflare_foreign[n]=0;
  if(global_smoke_owner)global_smoke_owner[n]=global_smoke_foreign[n]=0;
  if(global_green_owner)global_green_owner[n]=global_green_foreign[n]=0;
  if(global_small_explosion_owner)global_small_explosion_owner[n]=global_small_explosion_foreign[n]=0;
  if(global_cash25_owner)global_cash25_owner[n]=global_cash25_foreign[n]=0;
  global_newshf_owner[n]=1;global_newshf_foreign[n]=foreign;hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  selected[(dy/d)*320+dx/d]=1;
 }
 ++draws;return 1;
}
/* A soft sprite must not consume an unproven foreign RGB lifetime. For this
 * new static group, decline its entire quartet before contributing any pixels,
 * rather than allowing a later quadrant to revoke unrelated scene HD. Existing
 * groups retain their established policy; the per-pixel guard remains active. */
static bool global_newshf_dual_preflight(unsigned slot,Sprite2_array bank,unsigned base)
{
 uint64_t generation=newshf_validation_slots[slot].generation;
 if(global_newshf_dual_preflight_generation[slot]==generation&&global_newshf_dual_preflight_state[slot])
  return global_newshf_dual_preflight_state[slot]==2;
 global_newshf_dual_preflight_generation[slot]=generation;
 global_newshf_dual_preflight_state[slot]=1;
 if(!global_newshf_requested()||!global_newshf_frame||global_newshf_fault||
    !global_newshf_surface_matches()||!global_newshf_source_matches(bank)||
    !global_newshf_palette_matches()||!global_newshf_underlay_matches()||!global_newshf_group_ready(15))return false;
 Uint8 native[4][336];const unsigned parts[4]={0,1,19,20};
 for(unsigned q=0;q<4;q++)if(!decode_tile(bank,base+parts[q],native[q],native[q]+168,12,0,0))return false;
 int d=game_probe_density,cx=newshf_validation_slots[slot].x,cy=newshf_validation_slots[slot].y;
 const Uint8 *rgba=global_newshf_rgba[15];uint64_t shapesy_serial=shapesy_borrow_ready();
 for(int ay=0;ay<28*d;ay++)for(int ax=0;ax<24*d;ax++){
  int nx=ax/d,ny=ay/d;
  if(ny<14?cy<=-13:cy<=-26||cy>=182)continue;
  int x=(cx-6)*d+ax,y=(cy-7)*d+ay;if(y<0||y>=canvas->h)continue;
  unsigned q=(ny>=14?2u:0u)+(nx>=12?1u:0u);
  bool covered=native[q][168+(ny%14)*12+nx%12]!=0;
  unsigned alpha=rgba[4*((ay*8/d)*192+ax*8/d)+3];
  if((!alpha&&!covered)||alpha==255)continue;
  size_t n=(size_t)y*canvas->w+x;
  bool foreign=global_newshf_owner[n]?global_newshf_foreign[n]:hd_owner[n]!=0;
  if(foreign){Uint32 color=*((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch)+x);
   if(!shapesy_borrow_sample(shapesy_serial,n,color))return false;
   global_newshf_dual_shapesy_serial[slot]=shapesy_serial;
  }
 }
 global_newshf_dual_preflight_state[slot]=2;return true;
}
static int global_newshf_body(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *context,bool identity)
{
 global_newshf_observed_preflight();
 if(!context||newshf_validation_profile(context->type)<0)return -1;
 if(!identity){if(global_newshf_contributed)global_newshf_fail();return 0;}
 unsigned slot=context->pool_slot;
 /* Reject physical row wrapping as a complete family, never an HD prefix. */
 if(newshf_validation_slots[slot].x<6||newshf_validation_slots[slot].x>302){global_newshf_fail();return 0;}
 unsigned phase=newshf_profiles[newshf_validation_slots[slot].profile].resources[newshf_validation_slots[slot].pose-1];
 if(phase==15&&!global_newshf_dual_preflight(slot,bank,base))return 0;
 int result=global_newshf_draw(surface,x,y,bank,base+(unsigned)part,filter,phase,part,phase==15?global_newshf_dual_shapesy_serial[slot]:0);
 if(result)global_newshf_generations[slot]=newshf_validation_slots[slot].generation;
 return result;
}
static bool global_newshf_pixel(int x,int y,Uint8 before,Uint8 after,int style)
{
 if(!global_newshf_frame||!global_newshf_owner)return false;
 if(!global_newshf_surface_matches()){global_newshf_fail();render_mirror_unsupported("global-source-layout");return false;}
 int d=game_probe_density;
 if(global_newshf_call.live) {
  int dx=x-global_newshf_call.x,dy=y-global_newshf_call.y;
  if(dx<0||dx>=12||dy<0||dy>=14){global_newshf_fail();return false;}
  unsigned n=(unsigned)(dy*12+dx);Uint8 source=global_newshf_call.source[n];
  Uint8 want=style==MIRROR_NORMAL?(global_newshf_call.filter?(Uint8)(global_newshf_call.filter|(source&15)):source):style==MIRROR_BLEND?(Uint8)((source&240)|(((source&15)+(before&15))/2)):(Uint8)((before&240)|((before&15)/2));
  if(style!=global_newshf_call.style||!global_newshf_call.mask[n]||global_newshf_call.seen[n]||after!=want){global_newshf_fail();return false;}
  global_newshf_call.seen[n]=1;--global_newshf_call.left;return true;
 }
 bool shadow=style==MIRROR_SHADOW&&after==(Uint8)((before&240)|((before&15)/2));
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
  if(!global_newshf_owner[n]||(!suppress&&shadow))continue;
  global_newshf_owner[n]=global_newshf_foreign[n]=0;
  if(!suppress&&style!=MIRROR_NORMAL){hd_owner[n]=0;cloud_owner[n]=0;}
 }
 return false;
}
static void global_newshf_end(void)
{if(global_newshf_call.live&&global_newshf_call.left)global_newshf_fail();global_newshf_call.live=false;}
/* A later owner may have copied our RGB. Fail the complete current Present,
 * not merely the pixels that still bear our owner bit. */
static bool global_newshf_finish_proof(void)
{
 if(global_newshf_rejected_frame)return false;
 if(!global_newshf_contributed)return true;
 if(!global_newshf_identity_complete()||(global_newshf_shapesy_dependency&&!shapesy_borrow_check(global_newshf_shapesy_dependency)))global_newshf_fail();
 if(global_newshf_surface_matches())for(int y=0;y<200;y++)
  if(memcmp(expected+y*320,(Uint8 *)game_screen->pixels+y*320,320)){global_newshf_fail();break;}
 return global_newshf_assets_match()&&global_newshf_requested()&&!global_newshf_fault&&!global_newshf_call.live&&
  global_newshf_surface_matches()&&global_newshf_final_surface_matches()&&
  global_newshf_source_matches(global_newshf_bank())&&global_newshf_palette_matches()&&
  global_newshf_underlay_matches()&&(!global_newshf_talon_dependency||
   (!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()));
}
static bool global_newshf_output_proof(MirrorOutputKind kind,int lightx,int lighty)
{
 if(global_newshf_rejected_frame)return false;
 if(!global_newshf_contributed)return true;
 if(kind!=MIRROR_OUTPUT_ORDINARY&&kind!=MIRROR_OUTPUT_NORMAL15_LOW_DETAIL&&kind!=MIRROR_OUTPUT_NORMAL15_NIGHT)return false;
 if(!global_newshf_surface_matches()||!global_newshf_final_surface_matches())return false;
 bool night=kind==MIRROR_OUTPUT_NORMAL15_NIGHT;
 if(night&&(VGAScreenSeg->pitch!=320||!normal15_palette()||!normal15_indices_match(kind,lightx,lighty)))return false;
 /* Prove the complete scene mapping before any owner can compose copied RGB. */
 for(int y=0;y<184;y++)for(int x=24;x<288;x++) {
  Uint8 before=((Uint8 *)game_screen->pixels)[y*320+x];
  Uint8 after=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24];
  if(after!=(night?normal15_index(before,x-24,y,lightx,lighty):before))return false;
 }
 return true;
}
static bool global_newshf_compose(MirrorOutputKind kind,int lightx,int lighty)
{
 global_newshf_end();
 if(!global_newshf_frame||!global_newshf_owner)return false;
 if(!global_newshf_surface_matches()||!global_newshf_final_surface_matches()) {
  global_newshf_frame=global_newshf_cached=false;return false;
 }
 bool valid=global_newshf_requested()&&!global_newshf_fault&&global_newshf_surface_matches()&&global_newshf_source_matches(global_newshf_bank())&&
  global_newshf_palette_matches()&&global_newshf_underlay_matches()&&(!global_newshf_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()))&&(kind==MIRROR_OUTPUT_ORDINARY||kind==MIRROR_OUTPUT_NORMAL15_LOW_DETAIL||kind==MIRROR_OUTPUT_NORMAL15_NIGHT)&&
  VGAScreenSeg&&VGAScreenSeg->pixels&&VGAScreenSeg->w==320&&VGAScreenSeg->h==200&&VGAScreenSeg->pitch>=320&&
  VGAScreenSeg->format&&VGAScreenSeg->format->format==SDL_PIXELFORMAT_INDEX8;
 if(valid)for(int y=0;y<200;y++)if(memcmp(expected+y*320,(Uint8 *)game_screen->pixels+y*320,320)){valid=false;break;}
 /* Night is a native output operation, never a level or scene permission.
  * Its exact palette and complete final INDEX8 mapping are independently proven. */
 if(valid&&kind==MIRROR_OUTPUT_NORMAL15_NIGHT)valid=VGAScreenSeg->pitch==320&&normal15_palette()&&normal15_indices_match(kind,lightx,lighty);
 int d=game_probe_density;bool retained=false;
 for(int y=0;y<184;y++)for(int x=24;x<288;x++) {
  Uint8 before=((Uint8 *)game_screen->pixels)[y*320+x],after=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24];
  bool night=kind==MIRROR_OUTPUT_NORMAL15_NIGHT;
  bool cell=valid&&after==(night?normal15_index(before,x-24,y,lightx,lighty):before);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   int px=x*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_newshf_owner[n])continue;
   bool keep=cell&&(!reject_reason||!global_newshf_foreign[n]);
   Uint32 *p=(Uint32 *)((Uint8 *)output->pixels+py*output->pitch)+px-24*d;
   if(keep){Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px];
    *p=night?normal15_rgba(color,before,after,normal15_branch(x-24,y,lightx,lighty)<0):color;hd_owner[n]=1;retained=true;}
   else {*p=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24]);global_newshf_owner[n]=hd_owner[n]=0;}
  }
 }
 if(retained||global_newshf_contributed)memcpy(global_newshf_output_palette,rgb_palette,sizeof(global_newshf_output_palette));
 global_newshf_cached=retained||(valid&&global_newshf_contributed);global_newshf_frame=false;return retained;
}
static bool global_newshf_cache_source_matches(void)
{
 bool valid=global_newshf_assets_match()&&global_newshf_identity_complete()&&(!global_newshf_shapesy_dependency||shapesy_borrow_check(global_newshf_shapesy_dependency))&&!global_newshf_fault&&global_newshf_requested()&&global_newshf_surface_matches()&&global_newshf_final_surface_matches()&&global_newshf_source_matches(global_newshf_bank())&&(!global_newshf_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)));
 if(valid)for(int y=0;y<200;y++)if(memcmp(expected+y*320,(Uint8 *)game_screen->pixels+y*320,320)){valid=false;break;}
 if(valid)for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)){valid=false;break;}
 return valid;
}
static bool global_newshf_cache_decline(void)
{ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;global_newshf_cached=false;return false;}
static void global_newshf_check_cache(void)
{
 if(global_newshf_cached&&(!global_newshf_cache_source_matches()||
  memcmp(global_newshf_output_palette,rgb_palette,sizeof(global_newshf_output_palette))))global_newshf_cache_decline();
}
/* Prototype deliberately declines every fade with NEWSHF provenance, including
 * pixels already transferred to another owner. Ordinary Present is re-proven. */
static bool global_newshf_fade_decline(void)
{if(global_newshf_cached||global_newshf_contributed)return global_newshf_cache_decline();return true;}
static void global_newshf_final_pixel(SDL_Surface *s,Uint8 *address)
{
 if((!global_newshf_frame&&!global_newshf_cached)||s!=VGAScreenSeg||!s||!s->pixels||!s->format||
  s->format->format!=SDL_PIXELFORMAT_INDEX8||s->w!=320||s->h!=200||s->pitch<320||!global_newshf_surface_matches()||!global_newshf_final_surface_matches()||!global_newshf_owner)return;
 if(global_newshf_cached&&have_fade_saved){global_newshf_cache_decline();return;}
 intptr_t offset=(intptr_t)address-(intptr_t)s->pixels;if(offset<0||offset>=(intptr_t)s->pitch*200)return;
 int y=(int)(offset/s->pitch),x=(int)(offset%s->pitch),d=game_probe_density;if(x>=264||y>=184)return;
 bool changed=false;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  int px=(x+24)*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_newshf_owner[n])continue;
  global_newshf_owner[n]=global_newshf_foreign[n]=hd_owner[n]=cloud_owner[n]=0;changed=true;
  ((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px]=palette_rgb(*address);
  if(global_newshf_cached) {
   ((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px-24*d]=palette_rgb(*address);
   if(have_fade_saved&&fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+py*fade_saved->pitch))[px-24*d]=0xff000000u|(fade_saved_palette[*address]&0xffffffu);
  }
 }
 if(changed&&global_newshf_cached)last_output_indices[y*320+x]=*address;
}
static void global_newshf_final_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if((!global_newshf_frame&&!global_newshf_cached)||s!=VGAScreenSeg||!s||!s->pixels)return;
 int64_t x=r?r->x:0,y=r?r->y:0,right=r?x+r->w:320,bottom=r?y+r->h:200;
 x=MAX(MAX(x,s->clip_rect.x),0);y=MAX(MAX(y,s->clip_rect.y),0);
 right=MIN(MIN(right,(int64_t)s->clip_rect.x+s->clip_rect.w),264);bottom=MIN(MIN(bottom,(int64_t)s->clip_rect.y+s->clip_rect.h),184);
 for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)global_newshf_final_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx);
}

static bool global_newshf_observe_blend(SDL_Surface *s,Uint8 *address)
{
 if(!global_newshf_frame||s!=game_screen)return false;
 if(global_newshf_call.live||!active)return true;
 if(!global_newshf_surface_matches())return true;
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;if(off<0||off>=64000)return true;
 int x=(int)(off%320),y=(int)(off/320),d=game_probe_density;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)if(global_newshf_owner[(y*d+sy)*canvas->w+x*d+sx])return true;
 return false;
}

static void global_newshf_invalidate(void)
{
 if(global_newshf_contributed||global_newshf_cached){
  global_newshf_rejected_frame=true;global_newshf_fault=true;active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
 }
}

/* Simulation-boundary retirement precedes all renderer admission early exits. */
static void global_newshf_tick_begin(void)
{
 if(global_newshf_contributed||global_newshf_cached){ready=last_output_valid=have_fade_saved=false;fade_mode=0;}
 global_newshf_frame=global_newshf_cached=global_newshf_contributed=global_newshf_fault=global_newshf_rejected_frame=false;
 global_newshf_call.live=false;
}
