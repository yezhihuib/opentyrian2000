/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reconstructed Shield22 semantic owner. Exact authored assets are unchanged.
 * Included after decode_tile; no level/episode/map predicate grants this owner. */
#include "global_asset_registry.h"
static Uint8 *global_shield_rgba[27];
static bool global_shield_loaded,global_shield_good,global_shield_cached;
/* Survives ownership transfer (for example to antialiased HUD glyphs). */
static bool global_shield_contributed;

static size_t global_shield_capacity;
static Uint32 global_shield_output_palette[256],global_shield_underlay_palette[256];
static Uint8 global_shield_used_colors[256];
static struct {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;int pitch;} global_shield_fade_lease;
static struct {
 SDL_Surface *surface,*final_surface,*canvas_surface,*output_surface;
 void *pixels,*final_pixels,*canvas_pixels,*output_pixels;
 SDL_PixelFormat *format,*final_format,*canvas_format,*output_format;
 int pitch,final_pitch,canvas_pitch,output_pitch,density;
} global_shield_source_lease;
static struct {
 uint64_t generation, witnessed_generation, tick, allocated_tick; bool role,follow,pending; unsigned type,next_ttl;
} global_shield_slots[MAX_EXPLOSIONS];
static struct {bool live;unsigned player,type;int x,y;bool follow;} global_shield_birth;
static bool global_shield_talon_dependency;
static bool global_shield_is_index(unsigned index)
{for(unsigned i=0;i<27;i++)if(global_shield_phase_indices[i]==index)return true;return false;}
void render_mirror_shield_birth_begin(unsigned pnum,unsigned type,int x,int y,bool follow)
{
 static const int dx[9]={-17,-5,7,19,-17,19,-17,-5,7},dy[9]={-12,-12,-12,-12,2,2,16,16,16};
 global_shield_birth.live=false;
 if(pnum<1||pnum>2||type<14||type>22||follow!=!twoPlayerMode||
    x!=player[pnum-1].x+dx[type-14]||y!=player[pnum-1].y+dy[type-14])return;
 global_shield_birth.live=true;global_shield_birth.player=pnum;global_shield_birth.type=type;
 global_shield_birth.x=x;global_shield_birth.y=y;global_shield_birth.follow=follow;
}
void render_mirror_shield_birth_end(void){global_shield_birth.live=false;}
void render_mirror_explosion_allocated(unsigned slot)
{
 if(slot>=MAX_EXPLOSIONS)return;
 if(++global_shield_slots[slot].generation==0)++global_shield_slots[slot].generation;
 global_shield_slots[slot].role=false;global_shield_slots[slot].next_ttl=0;
 global_shield_slots[slot].pending=explosions[slot].ttl==0;global_shield_slots[slot].allocated_tick=mirror_logic_tick;
}
void render_mirror_explosion_initialized(unsigned slot,unsigned type)
{
 if(slot>=MAX_EXPLOSIONS)return;
 bool fresh=global_shield_slots[slot].pending&&global_shield_slots[slot].allocated_tick==mirror_logic_tick;
 global_shield_slots[slot].pending=false;
 if(!fresh||!global_shield_birth.live)return;
 const Explosion *e=explosions+slot;unsigned k=type>=14?type-14:9;
 bool good=k<9&&type==global_shield_birth.type&&e->x==global_shield_birth.x&&e->y==global_shield_birth.y&&
  e->ttl==3&&e->sprite+2u==global_shield_phase_indices[k*3]&&!e->fixedPosition&&e->deltaY==0&&e->followPlayer==global_shield_birth.follow;
 global_shield_slots[slot].role=good;global_shield_slots[slot].type=type;
 global_shield_slots[slot].follow=e->followPlayer;global_shield_slots[slot].next_ttl=good?3:0;
 global_shield_slots[slot].tick=UINT64_MAX;
 global_shield_slots[slot].witnessed_generation=global_shield_slots[slot].generation;
 global_shield_birth.live=false;
}
static struct {bool live;int x,y,style;unsigned left;Uint8 source[168],mask[168],seen[168];} global_shield_call;

static bool global_shield_requested(void)
{return global_asset_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool global_shield_palette_matches(void)
{
 for(unsigned i=0;i<COUNTOF(global_shield_palette);i++)
  if((rgb_palette[global_shield_palette[i].index]&0xffffffu)!=global_shield_palette[i].rgb)return false;
 return true;
}
static bool global_shield_underlay_matches(void)
{
 for(unsigned i=0;i<256;i++)if(global_shield_used_colors[i]&&
  (rgb_palette[i]&0xffffffu)!=global_shield_underlay_palette[i])return false;
 return true;
}
static void global_shield_use_color(unsigned i)
{if(!global_shield_used_colors[i]){global_shield_used_colors[i]=1;global_shield_underlay_palette[i]=rgb_palette[i]&0xffffffu;}}
static bool global_shield_source_matches(Sprite2_array bank)
{
 if(!bank.data||bank.data!=explosionSpriteSheet.data||bank.size!=GLOBAL_SHIELD_BANK_BYTES||bank.size!=explosionSpriteSheet.size)return false;
 for(unsigned i=0;i<COUNTOF(global_shield_source);i++) {
  Uint8 decoded[336]={0};
  if(!decode_tile(bank,global_shield_source[i].index,decoded,decoded+168,12,0,0)||
     global_bytes_hash(decoded,sizeof(decoded))!=global_shield_source[i].fnv)return false;
 }
 return true;
}
static bool global_shield_disjoint(const SDL_Surface *a,const SDL_Surface *b)
{
 uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;
 return x<y?y-x>=(size_t)a->pitch*a->h:x-y>=(size_t)b->pitch*b->h;
}
static bool global_shield_layout(void)
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
 for(unsigned i=0;i<4;i++)for(unsigned j=0;j<i;j++)if(!global_shield_disjoint(all[i],all[j]))return false;
 return true;
}
static bool global_shield_final_surface_matches(void)
{
 SDL_Surface *s=VGAScreenSeg;
 return s&&s==global_shield_source_lease.final_surface&&s->pixels&&s->pixels==global_shield_source_lease.final_pixels&&
  s->format&&s->format==global_shield_source_lease.final_format&&s->w==320&&s->h==200&&s->pitch>=320&&s->pitch==global_shield_source_lease.final_pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1;
}
static bool global_shield_surface_matches(void)
{
 SDL_Surface *s=game_screen;
 return global_shield_layout()&&canvas==global_shield_source_lease.canvas_surface&&output==global_shield_source_lease.output_surface&&
  canvas->pixels==global_shield_source_lease.canvas_pixels&&output->pixels==global_shield_source_lease.output_pixels&&
  canvas->format==global_shield_source_lease.canvas_format&&output->format==global_shield_source_lease.output_format&&
  canvas->pitch==global_shield_source_lease.canvas_pitch&&output->pitch==global_shield_source_lease.output_pitch&&
  s&&s==global_shield_source_lease.surface&&s->pixels&&s->pixels==global_shield_source_lease.pixels&&
  s->format&&s->format==global_shield_source_lease.format&&s->w==320&&s->h==200&&s->pitch==320&&s->pitch==global_shield_source_lease.pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&
  game_probe_density==global_shield_source_lease.density;
}


static bool global_shield_family_ready(void)
{
 if(global_shield_loaded)return global_shield_good;
 global_shield_loaded=true;global_shield_good=true;
 for(unsigned i=0;i<27;i++) {
  const GlobalAssetResource *r=NULL;
  for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_shield_resource_ids[i])r=global_asset_resources+j;
  if(!global_shield_resource_ids[i])continue;
  if(!r||r->width!=12||r->height!=14||r->anchor_x!=0||r->anchor_y!=0||!(global_shield_rgba[i]=global_resource_load(r)))global_shield_good=false;
 }
 if(!global_shield_good)for(unsigned i=0;i<27;i++){free(global_shield_rgba[i]);global_shield_rgba[i]=NULL;}
 return global_shield_good;
}
static void global_shield_fail(void);
static void global_shield_reset(void)
{
 /* Retire the actual RGB contribution before its proof bits. A still-active
  * legacy composition must not copy a disabled global owner's stale pixels. */
 if(global_shield_frame) {
  bool safe=global_shield_surface_matches();global_shield_fail();
  if(!safe){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 }
 if(global_shield_contributed){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 if(global_shield_cached){ready=last_output_valid=have_fade_saved=false;fade_mode=0;}
 global_shield_frame=global_shield_cached=global_shield_fault=global_shield_contributed=false;global_shield_call.live=false;
 memset(global_shield_slots,0,sizeof(global_shield_slots));global_shield_birth.live=false;global_shield_talon_dependency=false;memset(&global_shield_source_lease,0,sizeof(global_shield_source_lease));
 memset(&global_shield_fade_lease,0,sizeof(global_shield_fade_lease));
 if(global_shield_owner)memset(global_shield_owner,0,global_shield_capacity);
 if(global_shield_foreign)memset(global_shield_foreign,0,global_shield_capacity);
}
static void global_shield_shutdown(void)
{
 global_shield_reset();
 for(unsigned i=0;i<27;i++){free(global_shield_rgba[i]);global_shield_rgba[i]=NULL;}
 global_shield_loaded=global_shield_good=false;
 free(global_shield_owner);free(global_shield_foreign);global_shield_owner=global_shield_foreign=NULL;global_shield_capacity=0;
}
static void global_shield_frame_begin(void)
{
 global_shield_frame=global_shield_cached=global_shield_fault=global_shield_contributed=false;global_shield_call.live=false;
 memset(global_shield_used_colors,0,sizeof(global_shield_used_colors));global_shield_talon_dependency=false;
 if(!global_shield_requested()||!global_shield_layout()||!VGAScreenSeg||!VGAScreenSeg->pixels||!VGAScreenSeg->format||
  VGAScreenSeg->w!=320||VGAScreenSeg->h!=200||VGAScreenSeg->pitch<320||VGAScreenSeg->format->format!=SDL_PIXELFORMAT_INDEX8)return;
 size_t n=(size_t)canvas->w*canvas->h;
 if(global_shield_capacity!=n) {
  Uint8 *owner=calloc(n,1),*foreign=calloc(n,1);
  if(!owner||!foreign){free(owner);free(foreign);return;}
  free(global_shield_owner);free(global_shield_foreign);global_shield_owner=owner;global_shield_foreign=foreign;global_shield_capacity=n;
 }
 memset(global_shield_owner,0,n);memset(global_shield_foreign,0,n);
 global_shield_source_lease.final_surface=VGAScreenSeg;global_shield_source_lease.final_pixels=VGAScreenSeg->pixels;
 global_shield_source_lease.final_format=VGAScreenSeg->format;global_shield_source_lease.final_pitch=VGAScreenSeg->pitch;
 global_shield_source_lease.canvas_surface=canvas;global_shield_source_lease.canvas_pixels=canvas->pixels;
 global_shield_source_lease.canvas_format=canvas->format;global_shield_source_lease.canvas_pitch=canvas->pitch;
 global_shield_source_lease.output_surface=output;global_shield_source_lease.output_pixels=output->pixels;
 global_shield_source_lease.output_format=output->format;global_shield_source_lease.output_pitch=output->pitch;
 global_shield_source_lease.surface=game_screen;global_shield_source_lease.pixels=game_screen->pixels;
 global_shield_source_lease.format=game_screen->format;global_shield_source_lease.pitch=game_screen->pitch;global_shield_source_lease.density=game_probe_density;
 global_shield_frame=true;
}

static void global_shield_fail(void)
{
 global_shield_fault=true;global_shield_call.live=false;
 if(!global_shield_surface_matches()||!canvas||!global_shield_owner)return;
 int d=game_probe_density;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;if(!global_shield_owner[n])continue;
  ((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch))[x]=palette_rgb(((Uint8 *)game_screen->pixels)[(y/d)*320+x/d]);
  global_shield_owner[n]=global_shield_foreign[n]=hd_owner[n]=cloud_owner[n]=0;
 }
}
int render_mirror_global_shield(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,unsigned slot)
{
 if(!global_asset_directory[0]||slot>=MAX_EXPLOSIONS||!global_shield_slots[slot].role)return -1;
 const Explosion *e=explosions+slot;
 unsigned type=global_shield_slots[slot].type,ttl=e->ttl;
 bool witness=type>=14&&type<=22&&ttl>=1&&ttl<=3&&ttl==global_shield_slots[slot].next_ttl&&
  global_shield_slots[slot].witnessed_generation==global_shield_slots[slot].generation&&global_shield_slots[slot].tick!=mirror_logic_tick&&
  index==global_shield_phase_indices[(type-14)*3+3-ttl]&&e->sprite+1u==index&&e->x==x&&e->y==y&&
  !e->fixedPosition&&e->followPlayer==global_shield_slots[slot].follow&&e->deltaY==0;
 global_shield_slots[slot].tick=mirror_logic_tick;
 if(!witness){global_shield_slots[slot].role=false;return 0;}
 --global_shield_slots[slot].next_ttl;
 if(!global_shield_requested()||!global_shield_frame||global_shield_fault||surface!=game_screen||
  !global_shield_surface_matches()||(style!=MIRROR_NORMAL&&style!=MIRROR_BLEND)||
  x<0||x>308||y<-13||y>=200||!global_shield_source_matches(bank)||!global_shield_palette_matches()||!global_shield_underlay_matches())return 0;
 if(!global_shield_family_ready())return 0;
 if(global_shield_call.live){global_shield_fail();return 0;}
 unsigned phase=(type-14)*3+3-ttl;
 memset(&global_shield_call,0,sizeof(global_shield_call));
 if(!decode_tile(bank,index,global_shield_call.source,global_shield_call.mask,12,0,0))return 0;
 for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(global_shield_call.mask[yy*12+xx]&&y+yy>=0&&y+yy<200)++global_shield_call.left;
 global_shield_call.x=x;global_shield_call.y=y;global_shield_call.style=style;global_shield_call.live=true;
 if(!global_shield_resource_ids[phase])return 1; /* Authenticated empty source phase. */
 font_before_effect((SDL_Rect){x,y,12,14});
 int d=game_probe_density;const Uint8 *rgba=global_shield_rgba[phase];
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++) {
  int dx=x*d+ax,dy=y*d+ay;if(dy<0||dy>=canvas->h)continue;
  size_t n=(size_t)dy*canvas->w+dx;const Uint8 *a=rgba+4*((ay*8/d)*96+ax*8/d);
  bool native=global_shield_call.mask[(ay/d)*12+ax/d]!=0;
  if(!a[3]&&!native)continue;
  bool foreign=global_shield_owner[n]?global_shield_foreign[n]:hd_owner[n]!=0;
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx;
  if(!hd_owner[n]) {Uint8 v=((Uint8 *)game_screen->pixels)[(dy/d)*320+dx/d];*p=palette_rgb(v);global_shield_use_color(v);}
  else if(foreign)for(unsigned i=0;i<256;i++)global_shield_use_color(i);
  if(global_talon_owner&&global_talon_owner[n])global_shield_talon_dependency=true;
  if(a[3]) {unsigned alpha=style==MIRROR_BLEND?(a[3]+1u)/2u:a[3];*p=blend_rgba(*p,a,(int)alpha);if(alpha==255)foreign=false;}
  if(global_talon_owner)global_talon_owner[n]=global_talon_foreign[n]=0;
  global_shield_contributed=true;
  if(global_pulse_owner)global_pulse_owner[n]=global_pulse_foreign[n]=0;
  if(global_hitflare_owner)global_hitflare_owner[n]=global_hitflare_foreign[n]=0;
  if(global_smoke_owner)global_smoke_owner[n]=global_smoke_foreign[n]=0;
  if(global_small_explosion_owner)global_small_explosion_owner[n]=global_small_explosion_foreign[n]=0;
  if(global_vulcan_owner)global_vulcan_owner[n]=global_vulcan_foreign[n]=0;
  global_shield_owner[n]=1;global_shield_foreign[n]=foreign;hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  selected[(dy/d)*320+dx/d]=1;
 }
 ++draws;return 1;
}
static bool global_shield_pixel(int x,int y,Uint8 before,Uint8 after,int style)
{
 if(!global_shield_frame||!global_shield_owner)return false;
 if(!global_shield_surface_matches()){global_shield_fail();render_mirror_unsupported("global-source-layout");return false;}
 int d=game_probe_density;
 if(global_shield_call.live) {
  int dx=x-global_shield_call.x,dy=y-global_shield_call.y;
  if(dx<0||dx>=12||dy<0||dy>=14){global_shield_fail();return false;}
  unsigned n=(unsigned)(dy*12+dx);Uint8 source=global_shield_call.source[n];
  Uint8 want=style==MIRROR_NORMAL?source:style==MIRROR_BLEND?(Uint8)((source&240)|(((source&15)+(before&15))/2)):(Uint8)((before&240)|((before&15)/2));
  if(style!=global_shield_call.style||!global_shield_call.mask[n]||global_shield_call.seen[n]||after!=want){global_shield_fail();return false;}
  global_shield_call.seen[n]=1;--global_shield_call.left;return true;
 }
 bool shadow=style==MIRROR_SHADOW&&after==(Uint8)((before&240)|((before&15)/2));
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
  if(!global_shield_owner[n]||(!suppress&&shadow))continue;
  global_shield_owner[n]=global_shield_foreign[n]=0;
  if(!suppress&&style!=MIRROR_NORMAL){hd_owner[n]=0;cloud_owner[n]=0;}
 }
 return false;
}
static void global_shield_end(void)
{if(global_shield_call.live&&global_shield_call.left)global_shield_fail();global_shield_call.live=false;}
/* A later owner may have copied our RGB. Fail the complete current Present,
 * not merely the pixels that still bear our owner bit. */
static bool global_shield_finish_proof(void)
{
 if(!global_shield_contributed)return true;
 return global_shield_requested()&&!global_shield_fault&&!global_shield_call.live&&
  global_shield_surface_matches()&&global_shield_final_surface_matches()&&
  global_shield_source_matches(explosionSpriteSheet)&&global_shield_palette_matches()&&
  global_shield_underlay_matches()&&(!global_shield_talon_dependency||
   (!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()));
}
static bool global_shield_compose(MirrorOutputKind kind,int lightx,int lighty)
{
 global_shield_end();
 if(!global_shield_frame||!global_shield_owner)return false;
 if(!global_shield_surface_matches()||!global_shield_final_surface_matches()) {
  global_shield_frame=global_shield_cached=false;return false;
 }
 bool valid=global_shield_requested()&&!global_shield_fault&&global_shield_surface_matches()&&global_shield_source_matches(explosionSpriteSheet)&&
  global_shield_palette_matches()&&global_shield_underlay_matches()&&(!global_shield_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()))&&(kind==MIRROR_OUTPUT_ORDINARY||kind==MIRROR_OUTPUT_NORMAL15_LOW_DETAIL||kind==MIRROR_OUTPUT_NORMAL15_NIGHT)&&
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
   int px=x*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_shield_owner[n])continue;
   bool keep=cell&&(!reject_reason||!global_shield_foreign[n]);
   Uint32 *p=(Uint32 *)((Uint8 *)output->pixels+py*output->pitch)+px-24*d;
   if(keep){Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px];
    *p=night?normal15_rgba(color,before,after,normal15_branch(x-24,y,lightx,lighty)<0):color;hd_owner[n]=1;retained=true;}
   else {*p=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24]);global_shield_owner[n]=hd_owner[n]=0;}
  }
 }
 if(retained||global_shield_contributed)memcpy(global_shield_output_palette,rgb_palette,sizeof(global_shield_output_palette));
 global_shield_cached=retained||(valid&&global_shield_contributed);global_shield_frame=false;return retained;
}
static bool global_shield_cache_source_matches(void)
{
 bool valid=!global_shield_fault&&global_shield_requested()&&global_shield_surface_matches()&&global_shield_final_surface_matches()&&global_shield_source_matches(explosionSpriteSheet)&&(!global_shield_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)));
 if(valid)for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)){valid=false;break;}
 return valid;
}
static bool global_shield_cache_decline(void)
{ready=last_output_valid=have_fade_saved=false;fade_mode=0;global_shield_cached=false;return false;}
static void global_shield_check_cache(void)
{
 if(global_shield_cached&&(!global_shield_cache_source_matches()||
  memcmp(global_shield_output_palette,rgb_palette,sizeof(global_shield_output_palette))))global_shield_cache_decline();
}
static bool global_shield_fade_buffer_layout(void)
{
 SDL_Surface *s=fade_saved;int d=game_probe_density;
 if(!s||!s->pixels||!s->format||s->w!=320*d||s->h!=200*d||s->pitch<s->w*4||s->pitch%4||
  (uintptr_t)s->pixels%sizeof(Uint32)||s->format->format!=SDL_PIXELFORMAT_ARGB8888||
  s->format->BitsPerPixel!=32||s->format->BytesPerPixel!=4)return false;
 SDL_Surface *others[4]={game_screen,VGAScreenSeg,canvas,output};
 for(unsigned i=0;i<4;i++)if(!global_shield_disjoint(s,others[i]))return false;
 return true;
}
static bool global_shield_fade_buffer_safe(void)
{
 if(!global_shield_cached)return true;
 return (global_shield_cache_source_matches()&&global_shield_fade_buffer_layout())||global_shield_cache_decline();
}
static bool global_shield_fade_lease_matches(void)
{
 return global_shield_fade_buffer_layout()&&fade_saved==global_shield_fade_lease.surface&&
  fade_saved->pixels==global_shield_fade_lease.pixels&&fade_saved->format==global_shield_fade_lease.format&&fade_saved->pitch==global_shield_fade_lease.pitch;
}
static bool global_shield_fade_capture(void)
{
 if(!global_shield_cached)return true;
 if(!global_shield_cache_source_matches()||!global_shield_fade_buffer_layout()||
  (fade_mode==3&&!global_shield_fade_lease_matches()))return global_shield_cache_decline();
 global_shield_fade_lease.surface=fade_saved;global_shield_fade_lease.pixels=fade_saved->pixels;
 global_shield_fade_lease.format=fade_saved->format;global_shield_fade_lease.pitch=fade_saved->pitch;
 return true;
}
static bool global_shield_fade_step_valid(int steps)
{
 if(!global_shield_cached)return true;
 if(steps<=0||fade_mode<1||fade_mode>3||!have_fade_saved||!global_shield_cache_source_matches()||!global_shield_fade_lease_matches())return global_shield_cache_decline();
 /* The engine updates the indexed palette before this callback. Prove that
  * actual integer step, not equality with the deliberately older palette. */
 for(unsigned i=0;i<256;i++)for(int shift=0;shift<24;shift+=8) {
  int before=(global_shield_output_palette[i]>>shift)&255;
  int target=fade_mode==1?0:fade_mode==2?255:(int)((fade_saved_palette[i]>>shift)&255);
  if((int)((rgb_palette[i]>>shift)&255)!=before+(target-before)/steps)return global_shield_cache_decline();
 }
 return true;
}

static void global_shield_fade_palette(void)
{if(global_shield_cached)memcpy(global_shield_output_palette,rgb_palette,sizeof(global_shield_output_palette));}
static void global_shield_final_pixel(SDL_Surface *s,Uint8 *address)
{
 if((!global_shield_frame&&!global_shield_cached)||s!=VGAScreenSeg||!s||!s->pixels||!s->format||
  s->format->format!=SDL_PIXELFORMAT_INDEX8||s->w!=320||s->h!=200||s->pitch<320||!global_shield_surface_matches()||!global_shield_final_surface_matches()||!global_shield_owner)return;
 if(global_shield_cached&&have_fade_saved&&!global_shield_fade_lease_matches()){global_shield_cache_decline();return;}
 intptr_t offset=(intptr_t)address-(intptr_t)s->pixels;if(offset<0||offset>=(intptr_t)s->pitch*200)return;
 int y=(int)(offset/s->pitch),x=(int)(offset%s->pitch),d=game_probe_density;if(x>=264||y>=184)return;
 bool changed=false;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  int px=(x+24)*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_shield_owner[n])continue;
  global_shield_owner[n]=global_shield_foreign[n]=hd_owner[n]=cloud_owner[n]=0;changed=true;
  ((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px]=palette_rgb(*address);
  if(global_shield_cached) {
   ((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px-24*d]=palette_rgb(*address);
   if(have_fade_saved&&fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+py*fade_saved->pitch))[px-24*d]=0xff000000u|(fade_saved_palette[*address]&0xffffffu);
  }
 }
 if(changed&&global_shield_cached)last_output_indices[y*320+x]=*address;
}
static void global_shield_final_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if((!global_shield_frame&&!global_shield_cached)||s!=VGAScreenSeg||!s||!s->pixels)return;
 int64_t x=r?r->x:0,y=r?r->y:0,right=r?x+r->w:320,bottom=r?y+r->h:200;
 x=MAX(MAX(x,s->clip_rect.x),0);y=MAX(MAX(y,s->clip_rect.y),0);
 right=MIN(MIN(right,(int64_t)s->clip_rect.x+s->clip_rect.w),264);bottom=MIN(MIN(bottom,(int64_t)s->clip_rect.y+s->clip_rect.h),184);
 for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)global_shield_final_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx);
}

static bool global_shield_observe_blend(SDL_Surface *s,Uint8 *address)
{
 if(!global_shield_frame||s!=game_screen)return false;
 if(global_shield_call.live||!active)return true;
 if(!global_shield_surface_matches())return true;
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;if(off<0||off>=64000)return true;
 int x=(int)(off%320),y=(int)(off/320),d=game_probe_density;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)if(global_shield_owner[(y*d+sy)*canvas->w+x*d+sx])return true;
 return false;
}
