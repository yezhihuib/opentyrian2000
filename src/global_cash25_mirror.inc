/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared coins/gems body/value owner (five independent native identities). Exact authored assets are unchanged.
 * Included after decode_tile; no level/episode/map predicate grants this owner. */
#include "global_asset_registry.h"
enum { GLOBAL_CASH_PROFILE_COUNT=5, GLOBAL_CASH_RESOURCE_COUNT=33 };
static Uint8 *global_cash25_rgba[GLOBAL_CASH_RESOURCE_COUNT];
/* Storage/composition is shared; native records, phases and slot roles are not. */
static const unsigned global_cash_body_first[5]={7,26,20,32,14};
static const unsigned global_cash_body_count[5]={6,6,6,5,5};
static const unsigned global_cash_resource_offset[5]={0,7,14,21,27};
static const unsigned global_cash_value_index[5]={185,204,223,169,188};
static const unsigned *const global_cash_resource_sets[5]={global_cash25_resource_ids,global_cash50_resource_ids,global_cash75_resource_ids,global_gem100_resource_ids,global_gem250_resource_ids};
static const GlobalAssetSourceTile *const global_cash_source_sets[5]={global_cash25_source,global_cash50_source,global_cash75_source,global_gem100_source,global_gem250_source};
static const GlobalAssetSourceTile *const global_cash_value_sources[5]={global_cash25_value_source,global_cash50_value_source,global_cash75_value_source,global_gem100_value_source,global_gem250_value_source};
static const GlobalAssetPaletteColor *const global_cash_palette_sets[5]={global_cash25_palette,global_cash50_palette,global_cash75_palette,global_gem100_palette,global_gem250_palette};
static const unsigned global_cash_palette_counts[5]={COUNTOF(global_cash25_palette),COUNTOF(global_cash50_palette),COUNTOF(global_cash75_palette),COUNTOF(global_gem100_palette),COUNTOF(global_gem250_palette)};
static unsigned global_cash_resource_id(unsigned phase)
{
 for(unsigned p=0;p<GLOBAL_CASH_PROFILE_COUNT;p++)
  if(phase>=global_cash_resource_offset[p]&&phase<=global_cash_resource_offset[p]+global_cash_body_count[p])
   return global_cash_resource_sets[p][phase-global_cash_resource_offset[p]];
 return 0;
}
static int global_cash_popup_profile(int type)
{return type>=36&&type<=40?type-36:-1;}
static bool global_cash25_loaded,global_cash25_good,global_cash25_cached;
/* Survives ownership transfer (for example to antialiased HUD glyphs). */
static bool global_cash25_contributed;

static size_t global_cash25_capacity;
static Uint32 global_cash25_output_palette[256],global_cash25_underlay_palette[256];
static Uint8 global_cash25_used_colors[256];
static struct {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;int pitch;} global_cash25_fade_lease;
static struct {
 SDL_Surface *surface,*final_surface,*canvas_surface,*output_surface;
 void *pixels,*final_pixels,*canvas_pixels,*output_pixels;
 SDL_PixelFormat *format,*final_format,*canvas_format,*output_format;
 int pitch,final_pitch,canvas_pitch,output_pitch,density;
} global_cash25_source_lease;
static struct {
 uint64_t generation,witnessed_generation,tick,allocated_tick;
 bool role,pending;unsigned next_ttl,profile;
 int x,y,deltaY,original_type;
} global_cash25_slots[MAX_EXPLOSIONS];
static bool global_cash25_talon_dependency;
static bool global_cash25_is_index(unsigned index)
{return index==185||index==204||index==223||index==169||index==188;}
/* Called only after the native allocator chooses a free slot, before writes.
 * Capture fixed types 36–40, never moving aliases. A genuine type39 popup
 * also belongs to record509 callers; this does not authorize their body/reward. */
void render_mirror_cash25_value_allocated(unsigned slot,int type,int x,int y,int deltaY,bool fixed,bool follow)
{
 if(slot>=MAX_EXPLOSIONS)return;
 if(++global_cash25_slots[slot].generation==0)++global_cash25_slots[slot].generation;
 global_cash25_slots[slot].role=false;global_cash25_slots[slot].next_ttl=0;
 global_cash25_slots[slot].pending=explosions[slot].ttl==0&&
  global_cash_popup_profile(type)>=0&&fixed&&!follow&&deltaY==0&&y>-16&&y<190;
 global_cash25_slots[slot].allocated_tick=mirror_logic_tick;
 global_cash25_slots[slot].x=(JE_integer)x;
 global_cash25_slots[slot].y=(JE_integer)y;
 global_cash25_slots[slot].deltaY=deltaY;global_cash25_slots[slot].original_type=type;
 global_cash25_slots[slot].profile=(unsigned)global_cash_popup_profile(type);
}
void render_mirror_cash25_value_initialized(unsigned slot,unsigned type)
{
 if(slot>=MAX_EXPLOSIONS)return;
 bool fresh=global_cash25_slots[slot].pending&&global_cash25_slots[slot].allocated_tick==mirror_logic_tick;
 global_cash25_slots[slot].pending=false;
 if(!fresh)return;
 const Explosion *e=explosions+slot;
 unsigned profile=global_cash25_slots[slot].profile;
 bool good=profile<GLOBAL_CASH_PROFILE_COUNT&&type==36+profile&&e->x==global_cash25_slots[slot].x&&e->y==global_cash25_slots[slot].y&&
  e->ttl==8&&e->sprite==global_cash_value_index[profile]-1&&e->fixedPosition&&!e->followPlayer&&e->deltaY==global_cash25_slots[slot].deltaY;
 global_cash25_slots[slot].role=good;global_cash25_slots[slot].next_ttl=good?8:0;
 global_cash25_slots[slot].tick=UINT64_MAX;
 global_cash25_slots[slot].witnessed_generation=global_cash25_slots[slot].generation;
}
static struct {bool live;int x,y,style;unsigned left;Uint8 source[168],mask[168],seen[168];} global_cash25_call;

static bool global_cash25_requested(void)
{return global_asset_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool global_cash25_palette_matches(void)
{
 for(unsigned p=0;p<GLOBAL_CASH_PROFILE_COUNT;p++)for(unsigned i=0;i<global_cash_palette_counts[p];i++)
  if((rgb_palette[global_cash_palette_sets[p][i].index]&0xffffffu)!=global_cash_palette_sets[p][i].rgb)return false;
 return true;
}
static bool global_cash25_underlay_matches(void)
{
 for(unsigned i=0;i<256;i++)if(global_cash25_used_colors[i]&&
  (rgb_palette[i]&0xffffffu)!=global_cash25_underlay_palette[i])return false;
 return true;
}
static void global_cash25_use_color(unsigned i)
{if(!global_cash25_used_colors[i]){global_cash25_used_colors[i]=1;global_cash25_underlay_palette[i]=rgb_palette[i]&0xffffffu;}}
#include "global_cash25_identity.inc"
/* The body and popup are a single all-or-classic resource family, but their
 * native role and lifecycle witnesses are independent. */
static bool global_cash25_source_matches(Sprite2_array bank)
{
 (void)bank;
 if(!spriteSheet11.data||spriteSheet11.size!=GLOBAL_CASH25_BANK_BYTES||
    !explosionSpriteSheet.data||explosionSpriteSheet.size!=GLOBAL_CASH25_VALUE_BANK_BYTES||
    !global_cash25_body_records_match())return false;
 for(unsigned p=0;p<GLOBAL_CASH_PROFILE_COUNT;p++) {
  for(unsigned i=0;i<global_cash_body_count[p];i++) {
   Uint8 decoded[336]={0};
   if(!decode_tile(spriteSheet11,global_cash_source_sets[p][i].index,decoded,decoded+168,12,0,0)||
      global_bytes_hash(decoded,sizeof(decoded))!=global_cash_source_sets[p][i].fnv)return false;
  }
  Uint8 decoded[336]={0};
  if(!decode_tile(explosionSpriteSheet,global_cash_value_index[p],decoded,decoded+168,12,0,0)||
     global_bytes_hash(decoded,sizeof(decoded))!=global_cash_value_sources[p][0].fnv)return false;
 }
 return true;
}
static bool global_cash25_disjoint(const SDL_Surface *a,const SDL_Surface *b)
{
 uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;
 return x<y?y-x>=(size_t)a->pitch*a->h:x-y>=(size_t)b->pitch*b->h;
}
static bool global_cash25_layout(void)
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
 for(unsigned i=0;i<4;i++)for(unsigned j=0;j<i;j++)if(!global_cash25_disjoint(all[i],all[j]))return false;
 return true;
}
static bool global_cash25_final_surface_matches(void)
{
 SDL_Surface *s=VGAScreenSeg;
 return s&&s==global_cash25_source_lease.final_surface&&s->pixels&&s->pixels==global_cash25_source_lease.final_pixels&&
  s->format&&s->format==global_cash25_source_lease.final_format&&s->w==320&&s->h==200&&s->pitch>=320&&s->pitch==global_cash25_source_lease.final_pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1;
}
static bool global_cash25_surface_matches(void)
{
 SDL_Surface *s=game_screen;
 return global_cash25_layout()&&canvas==global_cash25_source_lease.canvas_surface&&output==global_cash25_source_lease.output_surface&&
  canvas->pixels==global_cash25_source_lease.canvas_pixels&&output->pixels==global_cash25_source_lease.output_pixels&&
  canvas->format==global_cash25_source_lease.canvas_format&&output->format==global_cash25_source_lease.output_format&&
  canvas->pitch==global_cash25_source_lease.canvas_pitch&&output->pitch==global_cash25_source_lease.output_pitch&&
  s&&s==global_cash25_source_lease.surface&&s->pixels&&s->pixels==global_cash25_source_lease.pixels&&
  s->format&&s->format==global_cash25_source_lease.format&&s->w==320&&s->h==200&&s->pitch==320&&s->pitch==global_cash25_source_lease.pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&
  game_probe_density==global_cash25_source_lease.density;
}


static bool global_cash25_family_ready(void)
{
 if(global_cash25_loaded)return global_cash25_good;
 global_cash25_loaded=true;global_cash25_good=true;
 for(unsigned i=0;i<GLOBAL_CASH_RESOURCE_COUNT;i++) {
  const GlobalAssetResource *r=NULL;
  for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_cash_resource_id(i))r=global_asset_resources+j;
  if(!global_cash_resource_id(i))continue;
  if(!r||r->width!=12||r->height!=14||r->anchor_x!=0||r->anchor_y!=0||!(global_cash25_rgba[i]=global_resource_load(r)))global_cash25_good=false;
 }
 if(!global_cash25_good)for(unsigned i=0;i<GLOBAL_CASH_RESOURCE_COUNT;i++){free(global_cash25_rgba[i]);global_cash25_rgba[i]=NULL;}
 return global_cash25_good;
}
static void global_cash25_fail(void);
static void global_cash25_reset(void)
{
 /* Retire the actual RGB contribution before its proof bits. A still-active
  * legacy composition must not copy a disabled global owner's stale pixels. */
 if(global_cash25_frame) {
  bool safe=global_cash25_surface_matches();global_cash25_fail();
  if(!safe){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 }
 if(global_cash25_contributed){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 if(global_cash25_cached){ready=last_output_valid=have_fade_saved=false;fade_mode=0;}
 global_cash25_frame=global_cash25_cached=global_cash25_fault=global_cash25_contributed=false;global_cash25_call.live=false;
 global_cash25_body_identity_reset();memset(global_cash25_slots,0,sizeof(global_cash25_slots));global_cash25_talon_dependency=false;memset(&global_cash25_source_lease,0,sizeof(global_cash25_source_lease));
 memset(&global_cash25_fade_lease,0,sizeof(global_cash25_fade_lease));
 if(global_cash25_owner)memset(global_cash25_owner,0,global_cash25_capacity);
 if(global_cash25_foreign)memset(global_cash25_foreign,0,global_cash25_capacity);
}
static void global_cash25_shutdown(void)
{
 global_cash25_reset();
 for(unsigned i=0;i<GLOBAL_CASH_RESOURCE_COUNT;i++){free(global_cash25_rgba[i]);global_cash25_rgba[i]=NULL;}
 global_cash25_loaded=global_cash25_good=false;
 free(global_cash25_owner);free(global_cash25_foreign);global_cash25_owner=global_cash25_foreign=NULL;global_cash25_capacity=0;
}
static void global_cash25_frame_begin(void)
{
 global_cash25_body_identity_frame_begin();
 /* Once an original slot is observed retired or repurposed, restoring its
  * fields cannot revive this generation without a new native allocation. */
 for(unsigned i=0;i<MAX_EXPLOSIONS;i++)if(global_cash25_slots[i].role) {
  const Explosion *e=explosions+i;
  if(!e->ttl||e->ttl!=global_cash25_slots[i].next_ttl||global_cash25_slots[i].profile>=GLOBAL_CASH_PROFILE_COUNT||e->sprite!=global_cash_value_index[global_cash25_slots[i].profile]-1||
     !e->fixedPosition||e->followPlayer||e->deltaY||
     e->x!=global_cash25_slots[i].x||e->y!=global_cash25_slots[i].y)
   global_cash25_slots[i].role=false;
 }
 global_cash25_frame=global_cash25_cached=global_cash25_fault=global_cash25_contributed=false;global_cash25_call.live=false;
 memset(global_cash25_used_colors,0,sizeof(global_cash25_used_colors));global_cash25_talon_dependency=false;
 if(!global_cash25_requested()||!global_cash25_layout()||!VGAScreenSeg||!VGAScreenSeg->pixels||!VGAScreenSeg->format||
  VGAScreenSeg->w!=320||VGAScreenSeg->h!=200||VGAScreenSeg->pitch<320||VGAScreenSeg->format->format!=SDL_PIXELFORMAT_INDEX8)return;
 size_t n=(size_t)canvas->w*canvas->h;
 if(global_cash25_capacity!=n) {
  Uint8 *owner=calloc(n,1),*foreign=calloc(n,1);
  if(!owner||!foreign){free(owner);free(foreign);return;}
  free(global_cash25_owner);free(global_cash25_foreign);global_cash25_owner=owner;global_cash25_foreign=foreign;global_cash25_capacity=n;
 }
 memset(global_cash25_owner,0,n);memset(global_cash25_foreign,0,n);
 global_cash25_source_lease.final_surface=VGAScreenSeg;global_cash25_source_lease.final_pixels=VGAScreenSeg->pixels;
 global_cash25_source_lease.final_format=VGAScreenSeg->format;global_cash25_source_lease.final_pitch=VGAScreenSeg->pitch;
 global_cash25_source_lease.canvas_surface=canvas;global_cash25_source_lease.canvas_pixels=canvas->pixels;
 global_cash25_source_lease.canvas_format=canvas->format;global_cash25_source_lease.canvas_pitch=canvas->pitch;
 global_cash25_source_lease.output_surface=output;global_cash25_source_lease.output_pixels=output->pixels;
 global_cash25_source_lease.output_format=output->format;global_cash25_source_lease.output_pitch=output->pitch;
 global_cash25_source_lease.surface=game_screen;global_cash25_source_lease.pixels=game_screen->pixels;
 global_cash25_source_lease.format=game_screen->format;global_cash25_source_lease.pitch=game_screen->pitch;global_cash25_source_lease.density=game_probe_density;
 global_cash25_frame=true;
}

static void global_cash25_fail(void)
{
 global_cash25_fault=true;global_cash25_call.live=false;
 if(!global_cash25_surface_matches()||!canvas||!global_cash25_owner)return;
 int d=game_probe_density;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;if(!global_cash25_owner[n])continue;
  ((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch))[x]=palette_rgb(((Uint8 *)game_screen->pixels)[(y/d)*320+x/d]);
  global_cash25_owner[n]=global_cash25_foreign[n]=hd_owner[n]=cloud_owner[n]=0;
 }
}
static void global_cash25_observed_preflight(void)
{
 if(global_cash25_contributed&&(!global_cash25_requested()||!global_cash25_surface_matches()||
    !global_cash25_final_surface_matches()||!global_cash25_source_matches(explosionSpriteSheet)||
    !global_cash25_palette_matches()||!global_cash25_underlay_matches()))global_cash25_fail();
}
static int global_cash25_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,unsigned phase)
{
 if(!global_cash25_requested()||!global_cash25_frame||global_cash25_fault||surface!=game_screen||
  !global_cash25_surface_matches()||(style!=MIRROR_NORMAL&&style!=MIRROR_BLEND)||
  x<0||x>308||y<-13||y>=200||!global_cash25_source_matches(bank)||!global_cash25_palette_matches()||!global_cash25_underlay_matches()){
  if(global_cash25_contributed)global_cash25_fail();return 0;}
 if(!global_cash25_family_ready())return 0;
 if(global_cash25_call.live){global_cash25_fail();return 0;}
 memset(&global_cash25_call,0,sizeof(global_cash25_call));
 if(!decode_tile(bank,index,global_cash25_call.source,global_cash25_call.mask,12,0,0))return 0;
 for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(global_cash25_call.mask[yy*12+xx]&&y+yy>=0&&y+yy<200)++global_cash25_call.left;
 global_cash25_call.x=x;global_cash25_call.y=y;global_cash25_call.style=style;global_cash25_call.live=true;
 if(!global_cash_resource_id(phase))return 1; /* Authenticated empty source phase. */
 font_before_effect((SDL_Rect){x,y,12,14});
 int d=game_probe_density;const Uint8 *rgba=global_cash25_rgba[phase];
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++) {
  int dx=x*d+ax,dy=y*d+ay;if(dy<0||dy>=canvas->h)continue;
  size_t n=(size_t)dy*canvas->w+dx;const Uint8 *a=rgba+4*((ay*8/d)*96+ax*8/d);
  bool native=global_cash25_call.mask[(ay/d)*12+ax/d]!=0;
  if(!a[3]&&!native)continue;
  bool foreign=global_cash25_owner[n]?global_cash25_foreign[n]:hd_owner[n]!=0;
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx;
  if(!hd_owner[n]) {Uint8 v=((Uint8 *)game_screen->pixels)[(dy/d)*320+dx/d];*p=palette_rgb(v);global_cash25_use_color(v);}
  else if(foreign)for(unsigned i=0;i<256;i++)global_cash25_use_color(i);
  if(global_talon_owner&&global_talon_owner[n])global_cash25_talon_dependency=true;
  if(a[3]) {unsigned alpha=a[3];
   if(style==MIRROR_BLEND){Uint8 blended[4];explosion_asset_blend_rgba(*p,a,blended);*p=blend_rgba(*p,blended,(int)alpha);}
   else *p=blend_rgba(*p,a,(int)alpha);
   /* Value-average blending still depends on the destination even at alpha255. */
   if(alpha==255&&style==MIRROR_NORMAL)foreign=false;
  }
  if(global_talon_owner)global_talon_owner[n]=global_talon_foreign[n]=0;
  global_cash25_contributed=true;
  if(global_pulse_owner)global_pulse_owner[n]=global_pulse_foreign[n]=0;
  if(global_shield_owner)global_shield_owner[n]=global_shield_foreign[n]=0;
  if(global_vulcan_owner)global_vulcan_owner[n]=global_vulcan_foreign[n]=0;
  if(global_hitflare_owner)global_hitflare_owner[n]=global_hitflare_foreign[n]=0;
  if(global_smoke_owner)global_smoke_owner[n]=global_smoke_foreign[n]=0;
  if(global_green_owner)global_green_owner[n]=global_green_foreign[n]=0;
  if(global_small_explosion_owner)global_small_explosion_owner[n]=global_small_explosion_foreign[n]=0;
  if(global_rotor_owner)global_rotor_owner[n]=global_rotor_foreign[n]=0;
  if(global_projectile91_owner)global_projectile91_owner[n]=global_projectile91_foreign[n]=0;
  global_newshf_clear(n);
  global_cash25_owner[n]=1;global_cash25_foreign[n]=foreign;hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  selected[(dy/d)*320+dx/d]=1;
 }
 ++draws;return 1;
}
int render_mirror_global_cash25_value(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,unsigned slot)
{
 global_cash25_observed_preflight();
 if(!global_asset_directory[0]||slot>=MAX_EXPLOSIONS||!global_cash25_slots[slot].role)return -1;
 const Explosion *e=explosions+slot;unsigned ttl=e->ttl,profile=global_cash25_slots[slot].profile;
 bool witness=profile<GLOBAL_CASH_PROFILE_COUNT&&ttl>=1&&ttl<=8&&ttl==global_cash25_slots[slot].next_ttl&&
  global_cash25_slots[slot].witnessed_generation==global_cash25_slots[slot].generation&&
  global_cash25_slots[slot].tick!=mirror_logic_tick&&index==global_cash_value_index[profile]&&e->sprite==global_cash_value_index[profile]-1&&e->x==x&&e->y==y&&
  e->x==global_cash25_slots[slot].x&&e->y==global_cash25_slots[slot].y&&
  e->fixedPosition&&!e->followPlayer&&e->deltaY==0&&bank.data==explosionSpriteSheet.data&&bank.size==explosionSpriteSheet.size;
 global_cash25_slots[slot].tick=mirror_logic_tick;
 if(!witness){global_cash25_slots[slot].role=false;if(global_cash25_contributed)global_cash25_fail();return 0;}
 --global_cash25_slots[slot].next_ttl;
 return global_cash25_draw(surface,x,y,bank,index,style,global_cash_resource_offset[profile]+global_cash_body_count[profile]);
}
int render_mirror_global_cash25_body(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *context)
{
 global_cash25_observed_preflight();
 if(!global_asset_directory[0])return -1;
 /* Decline the old route on both success and failure for this record or bank
  * range; another entity cannot borrow the old unscoped cache. */
 int profile=context?global_cash25_body_profile(context->type):-1;
 bool known_body=(base>=7&&base<=12)||(base>=14&&base<=18)||(base>=20&&base<=36);
 bool candidate=profile>=0||(bank.data==spriteSheet11.data&&known_body);
 if(!candidate)return -1;
 if(!global_cash25_body_identity(x,y,bank,base,part,filter,context)) {
  if(global_cash25_contributed)global_cash25_fail();return 0;
 }
 return global_cash25_draw(surface,x,y,bank,base,MIRROR_NORMAL,global_cash_resource_offset[profile]+base-global_cash_body_first[profile]);
}
static bool global_cash25_pixel(int x,int y,Uint8 before,Uint8 after,int style)
{
 if(!global_cash25_frame||!global_cash25_owner)return false;
 if(!global_cash25_surface_matches()){global_cash25_fail();render_mirror_unsupported("global-source-layout");return false;}
 int d=game_probe_density;
 if(global_cash25_call.live) {
  int dx=x-global_cash25_call.x,dy=y-global_cash25_call.y;
  if(dx<0||dx>=12||dy<0||dy>=14){global_cash25_fail();return false;}
  unsigned n=(unsigned)(dy*12+dx);Uint8 source=global_cash25_call.source[n];
  Uint8 want=style==MIRROR_NORMAL?source:style==MIRROR_BLEND?(Uint8)((source&240)|(((source&15)+(before&15))/2)):(Uint8)((before&240)|((before&15)/2));
  if(style!=global_cash25_call.style||!global_cash25_call.mask[n]||global_cash25_call.seen[n]||after!=want){global_cash25_fail();return false;}
  global_cash25_call.seen[n]=1;--global_cash25_call.left;return true;
 }
 bool shadow=style==MIRROR_SHADOW&&after==(Uint8)((before&240)|((before&15)/2));
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
  if(!global_cash25_owner[n]||(!suppress&&shadow))continue;
  global_cash25_owner[n]=global_cash25_foreign[n]=0;
  if(!suppress&&style!=MIRROR_NORMAL){hd_owner[n]=0;cloud_owner[n]=0;}
 }
 return false;
}
static void global_cash25_end(void)
{if(global_cash25_call.live&&global_cash25_call.left)global_cash25_fail();global_cash25_call.live=false;}
/* A later owner may have copied our RGB. Fail the complete current Present,
 * not merely the pixels that still bear our owner bit. */
static bool global_cash25_finish_proof(void)
{
 if(!global_cash25_contributed)return true;
 return global_cash25_requested()&&!global_cash25_fault&&!global_cash25_call.live&&
  global_cash25_surface_matches()&&global_cash25_final_surface_matches()&&
  global_cash25_source_matches(explosionSpriteSheet)&&global_cash25_palette_matches()&&
  global_cash25_underlay_matches()&&(!global_cash25_talon_dependency||
   (!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()));
}
static bool global_cash25_compose(MirrorOutputKind kind,int lightx,int lighty)
{
 global_cash25_end();
 if(!global_cash25_frame||!global_cash25_owner)return false;
 if(!global_cash25_surface_matches()||!global_cash25_final_surface_matches()) {
  global_cash25_frame=global_cash25_cached=false;return false;
 }
 bool valid=global_cash25_requested()&&!global_cash25_fault&&global_cash25_surface_matches()&&global_cash25_source_matches(explosionSpriteSheet)&&
  global_cash25_palette_matches()&&global_cash25_underlay_matches()&&(!global_cash25_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()))&&(kind==MIRROR_OUTPUT_ORDINARY||kind==MIRROR_OUTPUT_NORMAL15_LOW_DETAIL||kind==MIRROR_OUTPUT_NORMAL15_NIGHT)&&
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
   int px=x*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_cash25_owner[n])continue;
   bool keep=cell&&(!reject_reason||!global_cash25_foreign[n]);
   Uint32 *p=(Uint32 *)((Uint8 *)output->pixels+py*output->pitch)+px-24*d;
   if(keep){Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px];
    *p=night?normal15_rgba(color,before,after,normal15_branch(x-24,y,lightx,lighty)<0):color;hd_owner[n]=1;retained=true;}
   else {*p=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24]);global_cash25_owner[n]=hd_owner[n]=0;}
  }
 }
 if(retained||global_cash25_contributed)memcpy(global_cash25_output_palette,rgb_palette,sizeof(global_cash25_output_palette));
 global_cash25_cached=retained||(valid&&global_cash25_contributed);global_cash25_frame=false;return retained;
}
static bool global_cash25_cache_source_matches(void)
{
 bool valid=!global_cash25_fault&&global_cash25_requested()&&global_cash25_surface_matches()&&global_cash25_final_surface_matches()&&global_cash25_source_matches(explosionSpriteSheet)&&(!global_cash25_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)));
 if(valid)for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)){valid=false;break;}
 return valid;
}
static bool global_cash25_cache_decline(void)
{ready=last_output_valid=have_fade_saved=false;fade_mode=0;global_cash25_cached=false;return false;}
static void global_cash25_check_cache(void)
{
 if(global_cash25_cached&&(!global_cash25_cache_source_matches()||
  memcmp(global_cash25_output_palette,rgb_palette,sizeof(global_cash25_output_palette))))global_cash25_cache_decline();
}
static bool global_cash25_fade_buffer_layout(void)
{
 SDL_Surface *s=fade_saved;int d=game_probe_density;
 if(!s||!s->pixels||!s->format||s->w!=320*d||s->h!=200*d||s->pitch<s->w*4||s->pitch%4||
  (uintptr_t)s->pixels%sizeof(Uint32)||s->format->format!=SDL_PIXELFORMAT_ARGB8888||
  s->format->BitsPerPixel!=32||s->format->BytesPerPixel!=4)return false;
 SDL_Surface *others[4]={game_screen,VGAScreenSeg,canvas,output};
 for(unsigned i=0;i<4;i++)if(!global_cash25_disjoint(s,others[i]))return false;
 return true;
}
static bool global_cash25_fade_buffer_safe(void)
{
 if(!global_cash25_cached)return true;
 return (global_cash25_cache_source_matches()&&global_cash25_fade_buffer_layout())||global_cash25_cache_decline();
}
static bool global_cash25_fade_lease_matches(void)
{
 return global_cash25_fade_buffer_layout()&&fade_saved==global_cash25_fade_lease.surface&&
  fade_saved->pixels==global_cash25_fade_lease.pixels&&fade_saved->format==global_cash25_fade_lease.format&&fade_saved->pitch==global_cash25_fade_lease.pitch;
}
static bool global_cash25_fade_capture(void)
{
 if(!global_cash25_cached)return true;
 if(!global_cash25_cache_source_matches()||!global_cash25_fade_buffer_layout()||
  (fade_mode==3&&!global_cash25_fade_lease_matches()))return global_cash25_cache_decline();
 global_cash25_fade_lease.surface=fade_saved;global_cash25_fade_lease.pixels=fade_saved->pixels;
 global_cash25_fade_lease.format=fade_saved->format;global_cash25_fade_lease.pitch=fade_saved->pitch;
 return true;
}
static bool global_cash25_fade_step_valid(int steps)
{
 if(!global_cash25_cached)return true;
 if(steps<=0||fade_mode<1||fade_mode>3||!have_fade_saved||!global_cash25_cache_source_matches()||!global_cash25_fade_lease_matches())return global_cash25_cache_decline();
 /* The engine updates the indexed palette before this callback. Prove that
  * actual integer step, not equality with the deliberately older palette. */
 for(unsigned i=0;i<256;i++)for(int shift=0;shift<24;shift+=8) {
  int before=(global_cash25_output_palette[i]>>shift)&255;
  int target=fade_mode==1?0:fade_mode==2?255:(int)((fade_saved_palette[i]>>shift)&255);
  if((int)((rgb_palette[i]>>shift)&255)!=before+(target-before)/steps)return global_cash25_cache_decline();
 }
 return true;
}

static void global_cash25_fade_palette(void)
{if(global_cash25_cached)memcpy(global_cash25_output_palette,rgb_palette,sizeof(global_cash25_output_palette));}
static void global_cash25_final_pixel(SDL_Surface *s,Uint8 *address)
{
 if((!global_cash25_frame&&!global_cash25_cached)||s!=VGAScreenSeg||!s||!s->pixels||!s->format||
  s->format->format!=SDL_PIXELFORMAT_INDEX8||s->w!=320||s->h!=200||s->pitch<320||!global_cash25_surface_matches()||!global_cash25_final_surface_matches()||!global_cash25_owner)return;
 if(global_cash25_cached&&have_fade_saved&&!global_cash25_fade_lease_matches()){global_cash25_cache_decline();return;}
 intptr_t offset=(intptr_t)address-(intptr_t)s->pixels;if(offset<0||offset>=(intptr_t)s->pitch*200)return;
 int y=(int)(offset/s->pitch),x=(int)(offset%s->pitch),d=game_probe_density;if(x>=264||y>=184)return;
 bool changed=false;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  int px=(x+24)*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_cash25_owner[n])continue;
  global_cash25_owner[n]=global_cash25_foreign[n]=hd_owner[n]=cloud_owner[n]=0;changed=true;
  ((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px]=palette_rgb(*address);
  if(global_cash25_cached) {
   ((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px-24*d]=palette_rgb(*address);
   if(have_fade_saved&&fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+py*fade_saved->pitch))[px-24*d]=0xff000000u|(fade_saved_palette[*address]&0xffffffu);
  }
 }
 if(changed&&global_cash25_cached)last_output_indices[y*320+x]=*address;
}
static void global_cash25_final_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if((!global_cash25_frame&&!global_cash25_cached)||s!=VGAScreenSeg||!s||!s->pixels)return;
 int64_t x=r?r->x:0,y=r?r->y:0,right=r?x+r->w:320,bottom=r?y+r->h:200;
 x=MAX(MAX(x,s->clip_rect.x),0);y=MAX(MAX(y,s->clip_rect.y),0);
 right=MIN(MIN(right,(int64_t)s->clip_rect.x+s->clip_rect.w),264);bottom=MIN(MIN(bottom,(int64_t)s->clip_rect.y+s->clip_rect.h),184);
 for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)global_cash25_final_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx);
}

static bool global_cash25_observe_blend(SDL_Surface *s,Uint8 *address)
{
 if(!global_cash25_frame||s!=game_screen)return false;
 if(global_cash25_call.live||!active)return true;
 if(!global_cash25_surface_matches())return true;
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;if(off<0||off>=64000)return true;
 int x=(int)(off%320),y=(int)(off/320),d=game_probe_density;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)if(global_cash25_owner[(y*d+sy)*canvas->w+x*d+sx])return true;
 return false;
}
