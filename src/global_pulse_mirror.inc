/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reconstructed Pulse5 semantic owner. Exact authored assets are unchanged.
 * Included after decode_tile; no level/episode/map predicate grants this owner. */
#include "global_asset_registry.h"
static Uint8 *global_pulse_rgba[5];
static bool global_pulse_loaded,global_pulse_good,global_pulse_cached;
/* Survives ownership transfer (for example to antialiased HUD glyphs). */
static bool global_pulse_contributed;

static size_t global_pulse_capacity;
static Uint32 global_pulse_output_palette[256],global_pulse_underlay_palette[256];
static Uint8 global_pulse_used_colors[256];
static struct {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;int pitch;} global_pulse_fade_lease;
static struct {
 SDL_Surface *surface,*final_surface,*canvas_surface,*output_surface;
 void *pixels,*final_pixels,*canvas_pixels,*output_pixels;
 SDL_PixelFormat *format,*final_format,*canvas_format,*output_format;
 int pitch,final_pitch,canvas_pitch,output_pitch,density;
} global_pulse_source_lease;
/* Only the real normal front-weapon call may establish this envelope. */
static uint64_t global_front_serial;
static struct {bool live,creating,on;unsigned port,bay,level,mode,player,record;uint64_t token,tick;} global_front_call;
static struct {uint64_t generation,witnessed,tick,head_tick,shadow_tick,record_stamp;bool pending,role,on;unsigned record,phase,player;PlayerShotDataType born;} global_pulse_slots[MAX_PWEAPON];
static uint64_t global_pulse_used_records[11];
static Uint8 global_front_port_name[30],global_front_port_length;
static bool global_front_port_pending,global_front_port_valid;
static uint64_t global_front_port_runtime;
static uint64_t global_front_record_stamp(const JE_WeaponType *w)
{
 Uint8 b[80];size_t n=0;
#define FRONT_BYTE(v) do {b[n++]=(Uint8)(v);} while(0)
#define FRONT_WORD(v) do {unsigned value_=(unsigned)(v);FRONT_BYTE(value_);FRONT_BYTE(value_>>8);} while(0)
 FRONT_WORD(w->drain);FRONT_BYTE(w->shotrepeat);FRONT_BYTE(w->multi);FRONT_WORD(w->weapani);
 FRONT_BYTE(w->max);FRONT_BYTE(w->tx);FRONT_BYTE(w->ty);FRONT_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)FRONT_WORD(w->sg[i]);
 FRONT_BYTE(w->acceleration);FRONT_BYTE(w->accelerationx);FRONT_BYTE(w->circlesize);
 FRONT_BYTE(w->sound);FRONT_BYTE(w->trail);FRONT_BYTE(w->shipblastfilter);
#undef FRONT_BYTE
#undef FRONT_WORD
 return n==80?global_bytes_hash(b,n):0;
}
static uint64_t global_front_port_stamp(bool disk)
{
 Uint8 b[82];size_t n=0;b[n++]=global_front_port_length;
 memcpy(b+n,disk?global_front_port_name:(const Uint8 *)weaponPort[1].name,30);n+=30;
 b[n++]=weaponPort[1].opnum;
 for(unsigned j=0;j<2;j++)for(unsigned i=0;i<11;i++){unsigned v=weaponPort[1].op[j][i];b[n++]=v;b[n++]=v>>8;}
 unsigned tail[3]={weaponPort[1].cost,weaponPort[1].itemgraphic,weaponPort[1].poweruse};
 for(unsigned i=0;i<3;i++){b[n++]=tail[i];b[n++]=tail[i]>>8;}
 return n==82?global_bytes_hash(b,n):0;
}
void render_mirror_front_port_name(unsigned port,unsigned length,const char *name)
{
 if(port!=1)return;
 global_front_port_valid=false;global_front_port_pending=true;
 global_front_port_length=(Uint8)length;memcpy(global_front_port_name,name,30);
}
void render_mirror_front_port_loaded(unsigned port)
{
 if(port!=1)return;
 global_front_port_valid=global_front_port_pending&&global_front_port_stamp(true)==GLOBAL_PULSE_PORT_FNV;
 global_front_port_pending=false;global_front_port_runtime=global_front_port_stamp(false);
}
static bool global_pulse_table(unsigned record)
{
 if(record<155||record>165||!global_front_port_valid||weaponPort[1].name[30]!=0||global_front_port_stamp(false)!=global_front_port_runtime)return false;
 uint64_t h=global_front_record_stamp(weapons+record);
 for(unsigned i=0;i<3;i++)if(h==global_pulse_record_fnv[record-155][i])return true;
 return false;
}
static bool global_pulse_records_match(void)
{for(unsigned i=0;i<11;i++)if(global_pulse_used_records[i]&&(!global_pulse_table(155+i)||global_front_record_stamp(weapons+155+i)!=global_pulse_used_records[i]))return false;return true;}
static bool global_pulse_is_index(unsigned index)
{for(unsigned i=0;i<5;i++)if(global_pulse_source[i].index==index)return true;return false;}
void render_mirror_front_call_begin(unsigned port,unsigned bay,unsigned level,unsigned mode,unsigned pnum,unsigned record)
{
 memset(&global_front_call,0,sizeof(global_front_call));
 if(port!=1||bay!=FRONT_WEAPON||level>=11||mode||pnum<1||pnum>2||record!=weaponPort[1].op[0][level]||!global_pulse_table(record))return;
 if(player[pnum-1].items.weapon[FRONT_WEAPON].id!=port||
    level!=(galagaMode?0u:(unsigned)player[pnum-1].items.weapon[FRONT_WEAPON].power-1u))return;
 global_front_call.live=true;global_front_call.on=global_asset_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;
 global_front_call.port=port;global_front_call.bay=bay;global_front_call.level=level;global_front_call.mode=mode;
 global_front_call.player=pnum;global_front_call.record=record;global_front_call.tick=mirror_logic_tick;
}
void render_mirror_front_call_end(void){memset(&global_front_call,0,sizeof(global_front_call));}
uint64_t render_mirror_front_create_begin(unsigned port,unsigned bay,unsigned record,unsigned pnum)
{
 if(!global_front_call.live||global_front_call.creating||global_front_call.tick!=mirror_logic_tick||port!=global_front_call.port||bay!=global_front_call.bay||record!=global_front_call.record||pnum!=global_front_call.player){render_mirror_front_call_end();return 0;}
 global_front_call.creating=true;if(++global_front_serial==0)++global_front_serial;
 return global_front_call.token=global_front_serial;
}
void render_mirror_front_create_end(uint64_t token)
{if(token&&token==global_front_call.token)render_mirror_front_call_end();}
void render_mirror_shot_allocated(unsigned slot)
{
 if(slot>=MAX_PWEAPON)return;
 if(++global_pulse_slots[slot].generation==0)++global_pulse_slots[slot].generation;
 global_pulse_slots[slot].role=false;global_pulse_slots[slot].pending=shotAvail[slot]==0;
 global_pulse_slots[slot].tick=mirror_logic_tick;
}
void render_mirror_front_shot_initialized(uint64_t token,unsigned slot,unsigned port,unsigned bay,unsigned record,unsigned pnum,unsigned phase)
{
 if(slot>=MAX_PWEAPON)return;
 bool fresh=global_pulse_slots[slot].pending&&global_pulse_slots[slot].tick==mirror_logic_tick;global_pulse_slots[slot].pending=false;
 if(!fresh||!token||token!=global_front_call.token||!global_front_call.live||!global_front_call.creating||global_front_call.tick!=mirror_logic_tick||
 port!=1||bay!=FRONT_WEAPON||record!=global_front_call.record||pnum!=global_front_call.player||phase<1||phase>8||!global_pulse_table(record))return;
 const PlayerShotDataType *s=playerShotData+slot;const JE_WeaponType *w=weapons+record;
 unsigned k=phase-1;
 if(!shotAvail[slot]||!global_pulse_is_index(s->shotGr)||s->shotGr!=w->sg[k]||s->playerNumber!=pnum||s->shotAni!=0||
 s->shotAniMax!=w->weapani+1||s->shotComplicated||s->aimAtEnemy||s->chainReaction||s->shotTrail!=w->trail||
 s->shotXC!=w->accelerationx||s->shotYC!=-w->acceleration||s->shotXM!=w->sx[k]||s->shotYM!=-w->sy[k]||
 s->shotDmg!=w->attack[k]||s->shotBlastFilter!=w->shipblastfilter)return;
 global_pulse_slots[slot].role=true;global_pulse_slots[slot].on=global_front_call.on;
 global_pulse_slots[slot].record_stamp=global_front_record_stamp(w);global_pulse_slots[slot].record=record;global_pulse_slots[slot].phase=phase;global_pulse_slots[slot].player=pnum;
 global_pulse_slots[slot].born=*s;global_pulse_slots[slot].witnessed=global_pulse_slots[slot].generation;
 global_pulse_slots[slot].head_tick=global_pulse_slots[slot].shadow_tick=UINT64_MAX;
}
static bool global_pulse_talon_dependency,global_pulse_shield_dependency;
static struct {bool live;int x,y,style;unsigned left;Uint8 source[168],mask[168],seen[168];} global_pulse_call;

static bool global_pulse_requested(void)
{return global_asset_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;}
static bool global_pulse_palette_matches(void)
{
 for(unsigned i=0;i<COUNTOF(global_pulse_palette);i++)
  if((rgb_palette[global_pulse_palette[i].index]&0xffffffu)!=global_pulse_palette[i].rgb)return false;
 return true;
}
static bool global_pulse_underlay_matches(void)
{
 for(unsigned i=0;i<256;i++)if(global_pulse_used_colors[i]&&
  (rgb_palette[i]&0xffffffu)!=global_pulse_underlay_palette[i])return false;
 return true;
}
static void global_pulse_use_color(unsigned i)
{if(!global_pulse_used_colors[i]){global_pulse_used_colors[i]=1;global_pulse_underlay_palette[i]=rgb_palette[i]&0xffffffu;}}
static bool global_pulse_source_matches(Sprite2_array bank)
{
 if(!bank.data||bank.data!=spriteSheet8.data||bank.size!=GLOBAL_PULSE_BANK_BYTES||bank.size!=spriteSheet8.size)return false;
 for(unsigned i=0;i<COUNTOF(global_pulse_source);i++) {
  Uint8 decoded[336]={0};
  if(!decode_tile(bank,global_pulse_source[i].index,decoded,decoded+168,12,0,0)||
     global_bytes_hash(decoded,sizeof(decoded))!=global_pulse_source[i].fnv)return false;
 }
 return true;
}
static bool global_pulse_disjoint(const SDL_Surface *a,const SDL_Surface *b)
{
 uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;
 return x<y?y-x>=(size_t)a->pitch*a->h:x-y>=(size_t)b->pitch*b->h;
}
static bool global_pulse_layout(void)
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
 for(unsigned i=0;i<4;i++)for(unsigned j=0;j<i;j++)if(!global_pulse_disjoint(all[i],all[j]))return false;
 return true;
}
static bool global_pulse_final_surface_matches(void)
{
 SDL_Surface *s=VGAScreenSeg;
 return s&&s==global_pulse_source_lease.final_surface&&s->pixels&&s->pixels==global_pulse_source_lease.final_pixels&&
  s->format&&s->format==global_pulse_source_lease.final_format&&s->w==320&&s->h==200&&s->pitch>=320&&s->pitch==global_pulse_source_lease.final_pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1;
}
static bool global_pulse_surface_matches(void)
{
 SDL_Surface *s=game_screen;
 return global_pulse_layout()&&canvas==global_pulse_source_lease.canvas_surface&&output==global_pulse_source_lease.output_surface&&
  canvas->pixels==global_pulse_source_lease.canvas_pixels&&output->pixels==global_pulse_source_lease.output_pixels&&
  canvas->format==global_pulse_source_lease.canvas_format&&output->format==global_pulse_source_lease.output_format&&
  canvas->pitch==global_pulse_source_lease.canvas_pitch&&output->pitch==global_pulse_source_lease.output_pitch&&
  s&&s==global_pulse_source_lease.surface&&s->pixels&&s->pixels==global_pulse_source_lease.pixels&&
  s->format&&s->format==global_pulse_source_lease.format&&s->w==320&&s->h==200&&s->pitch==320&&s->pitch==global_pulse_source_lease.pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&
  game_probe_density==global_pulse_source_lease.density;
}


static bool global_pulse_family_ready(void)
{
 if(global_pulse_loaded)return global_pulse_good;
 global_pulse_loaded=true;global_pulse_good=true;
 for(unsigned i=0;i<5;i++) {
  const GlobalAssetResource *r=NULL;
  for(unsigned j=0;j<GLOBAL_ASSET_RESOURCE_COUNT;j++)if(global_asset_resources[j].identity==global_pulse_resource_ids[i])r=global_asset_resources+j;
  if(!global_pulse_resource_ids[i])continue;
  if(!r||r->width!=12||r->height!=14||r->anchor_x!=(i==1?-1:0)||r->anchor_y!=0||!(global_pulse_rgba[i]=global_resource_load(r)))global_pulse_good=false;
 }
 if(!global_pulse_good)for(unsigned i=0;i<5;i++){free(global_pulse_rgba[i]);global_pulse_rgba[i]=NULL;}
 return global_pulse_good;
}
static void global_pulse_fail(void);
static void global_pulse_reset(void)
{
 /* Retire the actual RGB contribution before its proof bits. A still-active
  * legacy composition must not copy a disabled global owner's stale pixels. */
 if(global_pulse_frame) {
  bool safe=global_pulse_surface_matches();global_pulse_fail();
  if(!safe){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 }
 if(global_pulse_contributed){active=shared_hud_frame=ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 if(global_pulse_cached){ready=last_output_valid=have_fade_saved=false;fade_mode=0;}
 global_pulse_frame=global_pulse_cached=global_pulse_fault=global_pulse_contributed=false;global_pulse_call.live=false;
 memset(global_pulse_slots,0,sizeof(global_pulse_slots));render_mirror_front_call_end();global_pulse_talon_dependency=global_pulse_shield_dependency=false;memset(&global_pulse_source_lease,0,sizeof(global_pulse_source_lease));
 memset(&global_pulse_fade_lease,0,sizeof(global_pulse_fade_lease));
 if(global_pulse_owner)memset(global_pulse_owner,0,global_pulse_capacity);
 if(global_pulse_foreign)memset(global_pulse_foreign,0,global_pulse_capacity);
}
static void global_pulse_shutdown(void)
{
 global_pulse_reset();
 for(unsigned i=0;i<5;i++){free(global_pulse_rgba[i]);global_pulse_rgba[i]=NULL;}
 global_pulse_loaded=global_pulse_good=false;
 free(global_pulse_owner);free(global_pulse_foreign);global_pulse_owner=global_pulse_foreign=NULL;global_pulse_capacity=0;
}
static void global_pulse_frame_begin(void)
{
 global_pulse_frame=global_pulse_cached=global_pulse_fault=global_pulse_contributed=false;global_pulse_call.live=false;
 memset(global_pulse_used_records,0,sizeof(global_pulse_used_records));
 memset(global_pulse_used_colors,0,sizeof(global_pulse_used_colors));global_pulse_talon_dependency=global_pulse_shield_dependency=false;
 if(!global_pulse_requested()||!global_pulse_layout()||!VGAScreenSeg||!VGAScreenSeg->pixels||!VGAScreenSeg->format||
  VGAScreenSeg->w!=320||VGAScreenSeg->h!=200||VGAScreenSeg->pitch<320||VGAScreenSeg->format->format!=SDL_PIXELFORMAT_INDEX8)return;
 size_t n=(size_t)canvas->w*canvas->h;
 if(global_pulse_capacity!=n) {
  Uint8 *owner=calloc(n,1),*foreign=calloc(n,1);
  if(!owner||!foreign){free(owner);free(foreign);return;}
  free(global_pulse_owner);free(global_pulse_foreign);global_pulse_owner=owner;global_pulse_foreign=foreign;global_pulse_capacity=n;
 }
 memset(global_pulse_owner,0,n);memset(global_pulse_foreign,0,n);
 global_pulse_source_lease.final_surface=VGAScreenSeg;global_pulse_source_lease.final_pixels=VGAScreenSeg->pixels;
 global_pulse_source_lease.final_format=VGAScreenSeg->format;global_pulse_source_lease.final_pitch=VGAScreenSeg->pitch;
 global_pulse_source_lease.canvas_surface=canvas;global_pulse_source_lease.canvas_pixels=canvas->pixels;
 global_pulse_source_lease.canvas_format=canvas->format;global_pulse_source_lease.canvas_pitch=canvas->pitch;
 global_pulse_source_lease.output_surface=output;global_pulse_source_lease.output_pixels=output->pixels;
 global_pulse_source_lease.output_format=output->format;global_pulse_source_lease.output_pitch=output->pitch;
 global_pulse_source_lease.surface=game_screen;global_pulse_source_lease.pixels=game_screen->pixels;
 global_pulse_source_lease.format=game_screen->format;global_pulse_source_lease.pitch=game_screen->pitch;global_pulse_source_lease.density=game_probe_density;
 global_pulse_frame=true;
}

static void global_pulse_fail(void)
{
 global_pulse_fault=true;global_pulse_call.live=false;
 if(!global_pulse_surface_matches()||!canvas||!global_pulse_owner)return;
 int d=game_probe_density;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++) {
  size_t n=(size_t)y*canvas->w+x;if(!global_pulse_owner[n])continue;
  ((Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch))[x]=palette_rgb(((Uint8 *)game_screen->pixels)[(y/d)*320+x/d]);
  global_pulse_owner[n]=global_pulse_foreign[n]=hd_owner[n]=cloud_owner[n]=0;
 }
}
int render_mirror_global_pulse(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,unsigned slot,unsigned raw)
{
 if(!global_asset_directory[0]||slot>=MAX_PWEAPON||!global_pulse_slots[slot].role)return -1;
 const PlayerShotDataType *s=playerShotData+slot,*born=&global_pulse_slots[slot].born;
 unsigned phase=0;while(phase<5&&global_pulse_source[phase].index!=index)++phase;
 bool shadow=style==MIRROR_SHADOW;
 uint64_t *seen=shadow?&global_pulse_slots[slot].shadow_tick:&global_pulse_slots[slot].head_tick;
 bool witness=global_pulse_slots[slot].on&&global_pulse_slots[slot].witnessed==global_pulse_slots[slot].generation&&
  global_pulse_table(global_pulse_slots[slot].record)&&global_front_record_stamp(weapons+global_pulse_slots[slot].record)==global_pulse_slots[slot].record_stamp&&phase<5&&raw==index&&s->shotGr==born->shotGr&&
  s->shotAniMax==born->shotAniMax&&s->shotAniMax&&raw>=s->shotGr&&raw<s->shotGr+s->shotAniMax&&
  s->shotAni==(raw-s->shotGr+1)%s->shotAniMax&&s->playerNumber==born->playerNumber&&
  !s->shotComplicated&&!s->aimAtEnemy&&!s->chainReaction&&s->shotTrail==born->shotTrail&&s->shotDmg==born->shotDmg&&
  s->shotBlastFilter==born->shotBlastFilter&&s->shotXC==born->shotXC&&s->shotYC==born->shotYC&&
  x==s->shotX+1&&y==s->shotY+(shadow?(int)shadowYDist:0)&&*seen!=mirror_logic_tick&&
  (!shadow||(background2&&s->shotXM<100&&y<190));
 *seen=mirror_logic_tick;
 if(!witness)return 0;
 if(!global_pulse_requested()||!global_pulse_frame||global_pulse_fault||surface!=game_screen||
  !global_pulse_surface_matches()||(style!=MIRROR_NORMAL&&style!=MIRROR_SHADOW)||
  x<0||x>308||y<-13||y>=200||!global_pulse_source_matches(bank)||!global_pulse_palette_matches()||!global_pulse_underlay_matches())return 0;
 if(!global_pulse_family_ready())return 0;
 global_pulse_used_records[global_pulse_slots[slot].record-155]=global_pulse_slots[slot].record_stamp;
 if(global_pulse_call.live){global_pulse_fail();return 0;}

 memset(&global_pulse_call,0,sizeof(global_pulse_call));
 if(!decode_tile(bank,index,global_pulse_call.source,global_pulse_call.mask,12,0,0))return 0;
 for(int yy=0;yy<14;yy++)for(int xx=0;xx<12;xx++)if(global_pulse_call.mask[yy*12+xx]&&y+yy>=0&&y+yy<200)++global_pulse_call.left;
 global_pulse_call.x=x;global_pulse_call.y=y;global_pulse_call.style=style;global_pulse_call.live=true;

 /* Anchor -1 is authenticated file metadata; the accepted legacy asset is
  * already aligned to the native draw origin. Do not shift it a second time. */
 font_before_effect((SDL_Rect){x,y,12,14});
 int d=game_probe_density;const Uint8 *rgba=global_pulse_rgba[phase];
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++) {
  int dx=x*d+ax,dy=y*d+ay;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;
  size_t n=(size_t)dy*canvas->w+dx;const Uint8 *a=rgba+4*((ay*8/d)*96+ax*8/d);
  bool native=ax>=0&&ax<12*d&&global_pulse_call.mask[(ay/d)*12+ax/d]!=0;
  if(!a[3]&&!native)continue;
  bool foreign=global_pulse_owner[n]?global_pulse_foreign[n]:hd_owner[n]!=0;
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+dy*canvas->pitch)+dx;
  if(!hd_owner[n]) {Uint8 v=((Uint8 *)game_screen->pixels)[(dy/d)*320+dx/d];*p=palette_rgb(v);global_pulse_use_color(v);if(shadow)global_pulse_use_color((v&240)|((v&15)/2));}
  else if(foreign)for(unsigned i=0;i<256;i++)global_pulse_use_color(i);
  if(global_talon_owner&&global_talon_owner[n])global_pulse_talon_dependency=true;
  if(global_shield_owner&&global_shield_owner[n])global_pulse_shield_dependency=true;
  if(a[3]) {if(shadow){
   Uint8 v=((Uint8 *)game_screen->pixels)[(dy/d)*320+dx/d];
   Uint32 dark=hd_owner[n]?darken_rgba(*p,255):palette_rgb((v&240)|((v&15)/2));
   Uint8 c[4]={(Uint8)(dark>>16),(Uint8)(dark>>8),(Uint8)dark,255};*p=blend_rgba(*p,c,a[3]);}
   else {*p=blend_rgba(*p,a,a[3]);if(a[3]==255)foreign=false;}}
  if(global_shield_owner)global_shield_owner[n]=global_shield_foreign[n]=0;
  if(global_talon_owner)global_talon_owner[n]=global_talon_foreign[n]=0;
  global_pulse_contributed=true;
  if(global_hitflare_owner)global_hitflare_owner[n]=global_hitflare_foreign[n]=0;
  if(global_smoke_owner)global_smoke_owner[n]=global_smoke_foreign[n]=0;
  if(global_green_owner)global_green_owner[n]=global_green_foreign[n]=0;
  if(global_small_explosion_owner)global_small_explosion_owner[n]=global_small_explosion_foreign[n]=0;
  if(global_cash25_owner)global_cash25_owner[n]=global_cash25_foreign[n]=0;
  if(global_rotor_owner)global_rotor_owner[n]=global_rotor_foreign[n]=0;
  global_newshf_clear(n);
  if(global_vulcan_owner)global_vulcan_owner[n]=global_vulcan_foreign[n]=0;
  global_pulse_owner[n]=1;global_pulse_foreign[n]=foreign;hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  selected[(dy/d)*320+dx/d]=1;
 }
 ++draws;return 1;
}
static bool global_pulse_pixel(int x,int y,Uint8 before,Uint8 after,int style)
{
 if(!global_pulse_frame||!global_pulse_owner)return false;
 if(!global_pulse_surface_matches()){global_pulse_fail();render_mirror_unsupported("global-source-layout");return false;}
 int d=game_probe_density;
 if(global_pulse_call.live) {
  int dx=x-global_pulse_call.x,dy=y-global_pulse_call.y;
  if(dx<0||dx>=12||dy<0||dy>=14){global_pulse_fail();return false;}
  unsigned n=(unsigned)(dy*12+dx);Uint8 source=global_pulse_call.source[n];
  Uint8 want=style==MIRROR_NORMAL?source:style==MIRROR_BLEND?(Uint8)((source&240)|(((source&15)+(before&15))/2)):(Uint8)((before&240)|((before&15)/2));
  if(style!=global_pulse_call.style||!global_pulse_call.mask[n]||global_pulse_call.seen[n]||after!=want){global_pulse_fail();return false;}
  global_pulse_call.seen[n]=1;--global_pulse_call.left;return true;
 }
 bool shadow=style==MIRROR_SHADOW&&after==(Uint8)((before&240)|((before&15)/2));
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  size_t n=(size_t)(y*d+sy)*canvas->w+x*d+sx;
  if(!global_pulse_owner[n]||(!suppress&&shadow))continue;
  global_pulse_owner[n]=global_pulse_foreign[n]=0;
  if(!suppress&&style!=MIRROR_NORMAL){hd_owner[n]=0;cloud_owner[n]=0;}
 }
 return false;
}
static void global_pulse_end(void)
{if(global_pulse_call.live&&global_pulse_call.left)global_pulse_fail();global_pulse_call.live=false;}
/* A later owner may have copied our RGB. Fail the complete current Present,
 * not merely the pixels that still bear our owner bit. */
static bool global_pulse_finish_proof(void)
{
 if(!global_pulse_contributed)return true;
 return global_pulse_requested()&&!global_pulse_fault&&!global_pulse_call.live&&
  global_pulse_surface_matches()&&global_pulse_final_surface_matches()&&
  global_pulse_source_matches(spriteSheet8)&&global_pulse_records_match()&&global_pulse_palette_matches()&&
  global_pulse_underlay_matches()&&(!global_pulse_talon_dependency||
   (!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()))&&(!global_pulse_shield_dependency||(!global_shield_fault&&global_shield_source_matches(explosionSpriteSheet)&&global_shield_palette_matches()));
}
static bool global_pulse_compose(MirrorOutputKind kind,int lightx,int lighty)
{
 global_pulse_end();
 if(!global_pulse_frame||!global_pulse_owner)return false;
 if(!global_pulse_surface_matches()||!global_pulse_final_surface_matches()) {
  global_pulse_frame=global_pulse_cached=false;return false;
 }
 bool valid=global_pulse_requested()&&!global_pulse_fault&&global_pulse_surface_matches()&&global_pulse_source_matches(spriteSheet8)&&global_pulse_records_match()&&
  global_pulse_palette_matches()&&global_pulse_underlay_matches()&&(!global_pulse_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)&&global_talon_palette_matches()))&&(!global_pulse_shield_dependency||(!global_shield_fault&&global_shield_source_matches(explosionSpriteSheet)&&global_shield_palette_matches()))&&(kind==MIRROR_OUTPUT_ORDINARY||kind==MIRROR_OUTPUT_NORMAL15_LOW_DETAIL||kind==MIRROR_OUTPUT_NORMAL15_NIGHT)&&
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
   int px=x*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_pulse_owner[n])continue;
   bool keep=cell&&(!reject_reason||!global_pulse_foreign[n]);
   Uint32 *p=(Uint32 *)((Uint8 *)output->pixels+py*output->pitch)+px-24*d;
   if(keep){Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px];
    *p=night?normal15_rgba(color,before,after,normal15_branch(x-24,y,lightx,lighty)<0):color;hd_owner[n]=1;retained=true;}
   else {*p=palette_rgb(((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x-24]);global_pulse_owner[n]=hd_owner[n]=0;}
  }
 }
 if(retained||global_pulse_contributed)memcpy(global_pulse_output_palette,rgb_palette,sizeof(global_pulse_output_palette));
 global_pulse_cached=retained||(valid&&global_pulse_contributed);global_pulse_frame=false;return retained;
}
static bool global_pulse_cache_source_matches(void)
{
 bool valid=!global_pulse_fault&&global_pulse_requested()&&global_pulse_surface_matches()&&global_pulse_final_surface_matches()&&global_pulse_source_matches(spriteSheet8)&&global_pulse_records_match()&&(!global_pulse_talon_dependency||(!global_talon_fault&&global_talon_source_matches(spriteSheet9)))&&(!global_pulse_shield_dependency||(!global_shield_fault&&global_shield_source_matches(explosionSpriteSheet)));
 if(valid)for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)){valid=false;break;}
 return valid;
}
static bool global_pulse_cache_decline(void)
{ready=last_output_valid=have_fade_saved=false;fade_mode=0;global_pulse_cached=false;return false;}
static void global_pulse_check_cache(void)
{
 if(global_pulse_cached&&(!global_pulse_cache_source_matches()||
  memcmp(global_pulse_output_palette,rgb_palette,sizeof(global_pulse_output_palette))))global_pulse_cache_decline();
}
static bool global_pulse_fade_buffer_layout(void)
{
 SDL_Surface *s=fade_saved;int d=game_probe_density;
 if(!s||!s->pixels||!s->format||s->w!=320*d||s->h!=200*d||s->pitch<s->w*4||s->pitch%4||
  (uintptr_t)s->pixels%sizeof(Uint32)||s->format->format!=SDL_PIXELFORMAT_ARGB8888||
  s->format->BitsPerPixel!=32||s->format->BytesPerPixel!=4)return false;
 SDL_Surface *others[4]={game_screen,VGAScreenSeg,canvas,output};
 for(unsigned i=0;i<4;i++)if(!global_pulse_disjoint(s,others[i]))return false;
 return true;
}
static bool global_pulse_fade_buffer_safe(void)
{
 if(!global_pulse_cached)return true;
 return (global_pulse_cache_source_matches()&&global_pulse_fade_buffer_layout())||global_pulse_cache_decline();
}
static bool global_pulse_fade_lease_matches(void)
{
 return global_pulse_fade_buffer_layout()&&fade_saved==global_pulse_fade_lease.surface&&
  fade_saved->pixels==global_pulse_fade_lease.pixels&&fade_saved->format==global_pulse_fade_lease.format&&fade_saved->pitch==global_pulse_fade_lease.pitch;
}
static bool global_pulse_fade_capture(void)
{
 if(!global_pulse_cached)return true;
 if(!global_pulse_cache_source_matches()||!global_pulse_fade_buffer_layout()||
  (fade_mode==3&&!global_pulse_fade_lease_matches()))return global_pulse_cache_decline();
 global_pulse_fade_lease.surface=fade_saved;global_pulse_fade_lease.pixels=fade_saved->pixels;
 global_pulse_fade_lease.format=fade_saved->format;global_pulse_fade_lease.pitch=fade_saved->pitch;
 return true;
}
static bool global_pulse_fade_step_valid(int steps)
{
 if(!global_pulse_cached)return true;
 if(steps<=0||fade_mode<1||fade_mode>3||!have_fade_saved||!global_pulse_cache_source_matches()||!global_pulse_fade_lease_matches())return global_pulse_cache_decline();
 /* The engine updates the indexed palette before this callback. Prove that
  * actual integer step, not equality with the deliberately older palette. */
 for(unsigned i=0;i<256;i++)for(int shift=0;shift<24;shift+=8) {
  int before=(global_pulse_output_palette[i]>>shift)&255;
  int target=fade_mode==1?0:fade_mode==2?255:(int)((fade_saved_palette[i]>>shift)&255);
  if((int)((rgb_palette[i]>>shift)&255)!=before+(target-before)/steps)return global_pulse_cache_decline();
 }
 return true;
}

static void global_pulse_fade_palette(void)
{if(global_pulse_cached)memcpy(global_pulse_output_palette,rgb_palette,sizeof(global_pulse_output_palette));}
static void global_pulse_final_pixel(SDL_Surface *s,Uint8 *address)
{
 if((!global_pulse_frame&&!global_pulse_cached)||s!=VGAScreenSeg||!s||!s->pixels||!s->format||
  s->format->format!=SDL_PIXELFORMAT_INDEX8||s->w!=320||s->h!=200||s->pitch<320||!global_pulse_surface_matches()||!global_pulse_final_surface_matches()||!global_pulse_owner)return;
 if(global_pulse_cached&&have_fade_saved&&!global_pulse_fade_lease_matches()){global_pulse_cache_decline();return;}
 intptr_t offset=(intptr_t)address-(intptr_t)s->pixels;if(offset<0||offset>=(intptr_t)s->pitch*200)return;
 int y=(int)(offset/s->pitch),x=(int)(offset%s->pitch),d=game_probe_density;if(x>=264||y>=184)return;
 bool changed=false;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
  int px=(x+24)*d+sx,py=y*d+sy;size_t n=(size_t)py*canvas->w+px;if(!global_pulse_owner[n])continue;
  global_pulse_owner[n]=global_pulse_foreign[n]=hd_owner[n]=cloud_owner[n]=0;changed=true;
  ((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px]=palette_rgb(*address);
  if(global_pulse_cached) {
   ((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px-24*d]=palette_rgb(*address);
   if(have_fade_saved&&fade_saved)
    ((Uint32 *)((Uint8 *)fade_saved->pixels+py*fade_saved->pitch))[px-24*d]=0xff000000u|(fade_saved_palette[*address]&0xffffffu);
  }
 }
 if(changed&&global_pulse_cached)last_output_indices[y*320+x]=*address;
}
static void global_pulse_final_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if((!global_pulse_frame&&!global_pulse_cached)||s!=VGAScreenSeg||!s||!s->pixels)return;
 int64_t x=r?r->x:0,y=r?r->y:0,right=r?x+r->w:320,bottom=r?y+r->h:200;
 x=MAX(MAX(x,s->clip_rect.x),0);y=MAX(MAX(y,s->clip_rect.y),0);
 right=MIN(MIN(right,(int64_t)s->clip_rect.x+s->clip_rect.w),264);bottom=MIN(MIN(bottom,(int64_t)s->clip_rect.y+s->clip_rect.h),184);
 for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)global_pulse_final_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx);
}

static bool global_pulse_observe_blend(SDL_Surface *s,Uint8 *address)
{
 if(!global_pulse_frame||s!=game_screen)return false;
 if(global_pulse_call.live||!active)return true;
 if(!global_pulse_surface_matches())return true;
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;if(off<0||off>=64000)return true;
 int x=(int)(off%320),y=(int)(off/320),d=game_probe_density;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)if(global_pulse_owner[(y*d+sy)*canvas->w+x*d+sx])return true;
 return false;
}
