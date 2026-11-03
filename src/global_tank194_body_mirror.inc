/* SPDX-License-Identifier: GPL-2.0-or-later
 * NEW private finite owner for actual bank20 actor194, native frames91/93.
 * Reuses reviewed type15 material IDs1010041/1010131 without changing INDEX8.
 * Include after the ordinary shared owners. No projectile member bit is added.
 */
#include "global_tank194_pins.h"
static Uint8 *global_tank194_rgba[2],*global_tank194_ever;
static bool global_tank194_loaded,global_tank194_good;
static unsigned global_tank194_used_resources,global_tank194_dependencies;
static size_t global_tank194_capacity;
static Uint32 global_tank194_output_palette[256],global_tank194_underlay_palette[256];
static Uint8 global_tank194_used_colors[256];
static uint64_t global_tank194_platform_dependency,global_tank194_cyan_dependency;
static struct {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;int pitch;} global_tank194_fade_lease;
static struct {
 SDL_Surface *surface,*final_surface,*canvas_surface,*output_surface;
 void *pixels,*final_pixels,*canvas_pixels,*output_pixels;
 SDL_PixelFormat *format,*final_format,*canvas_format,*output_format;
 int pitch,final_pitch,canvas_pitch,output_pitch,density;
 const Uint8 *bank_data;size_t bank_size;
} global_tank194_source_lease;
static struct {bool live;int x,y;unsigned left;Uint8 source[168],mask[168],seen[168];} global_tank194_call;
static struct {bool live;unsigned slot,next,base;uint64_t generation,tick;int x,y;} global_tank194_quartet;
static struct {uint64_t generation,witnessed,born_tick;bool pending,role,exhausted;} global_tank194_slots[100];
static void global_tank194_fail(void);
static bool global_tank194_output_safe(void);
/* Source audit: asteroid_hd_enabled is assigned only by CLI parsing before
 * main enters the frame loop (game_probe.c/opentyr.c at the pinned baseline).
 * There is no runtime mode setter that could hide an on/off transition. */
static bool global_tank194_requested(void)
{
#if defined(NEWSHF_HD_COMPOSITOR) && NEWSHF_HD_COMPOSITOR
 return false;
#else
 return global_asset_directory[0]&&game_probe_density==8&&!game_probe_assets&&!asteroid_hd_enabled&&!xmas&&
  !game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;
#endif
}
static Sprite2_array global_tank194_bank(void)
{
 Sprite2_array result={0};unsigned count=0;
 for(unsigned i=0;i<COUNTOF(enemySpriteSheetIds);i++)if(enemySpriteSheetIds[i]==20){result=enemySpriteSheets[i];count++;}
 return count==1&&result.data&&result.size?result:(Sprite2_array){0};
}
static uint64_t global_tank194_record_stamp(void)
{
 const unsigned record=194;
 Uint8 bytes[77];size_t n=0;
#define TANK194_BYTE(v) do {bytes[n++]=(Uint8)(v);} while(0)
#define TANK194_WORD(v) do {unsigned cv_=(unsigned)(v);TANK194_BYTE(cv_);TANK194_BYTE(cv_>>8);} while(0)
 TANK194_BYTE(enemyDat[record].ani);
 for(unsigned i=0;i<3;i++)TANK194_BYTE(enemyDat[record].tur[i]);
 for(unsigned i=0;i<3;i++)TANK194_BYTE(enemyDat[record].freq[i]);
 TANK194_BYTE(enemyDat[record].xmove);TANK194_BYTE(enemyDat[record].ymove);
 TANK194_BYTE(enemyDat[record].xaccel);TANK194_BYTE(enemyDat[record].yaccel);
 TANK194_BYTE(enemyDat[record].xcaccel);TANK194_BYTE(enemyDat[record].ycaccel);
 TANK194_WORD(enemyDat[record].startx);TANK194_WORD(enemyDat[record].starty);
 TANK194_BYTE(enemyDat[record].startxc);TANK194_BYTE(enemyDat[record].startyc);
 TANK194_BYTE(enemyDat[record].armor);TANK194_BYTE(enemyDat[record].esize);
 for(unsigned i=0;i<20;i++)TANK194_WORD(enemyDat[record].egraphic[i]);
 TANK194_BYTE(enemyDat[record].explosiontype);TANK194_BYTE(enemyDat[record].animate);TANK194_BYTE(enemyDat[record].shapebank);
 TANK194_BYTE(enemyDat[record].xrev);TANK194_BYTE(enemyDat[record].yrev);TANK194_WORD(enemyDat[record].dgr);
 TANK194_BYTE(enemyDat[record].dlevel);TANK194_BYTE(enemyDat[record].dani);TANK194_BYTE(enemyDat[record].elaunchfreq);
 TANK194_WORD(enemyDat[record].elaunchtype);TANK194_WORD(enemyDat[record].value);TANK194_WORD(enemyDat[record].eenemydie);
#undef TANK194_BYTE
#undef TANK194_WORD
 return n==77?global_bytes_hash(bytes,n):0;
}

static bool global_tank194_record_matches(void)
{return COUNTOF(global_tank194_record_fnv)==1&&global_tank194_record_stamp()==global_tank194_record_fnv[0];}
static bool global_tank194_source_matches(Sprite2_array bank)
{
 Sprite2_array current=global_tank194_bank();
 if(!current.data||current.size!=GLOBAL_TANK194_BANK_BYTES||bank.data!=current.data||bank.size!=current.size||
  !global_tank194_record_matches()||global_bytes_hash(bank.data,bank.size)!=GLOBAL_TANK194_BANK_FNV)return false;
 for(unsigned i=0;i<COUNTOF(global_tank194_source);i++){
  Uint8 decoded[336]={0};
  if(!decode_tile(bank,global_tank194_source[i].index,decoded,decoded+168,12,0,0)||
   global_bytes_hash(decoded,sizeof(decoded))!=global_tank194_source[i].fnv)return false;
 }
 return true;
}
static bool global_tank194_palette_matches(void)
{
 for(unsigned i=0;i<COUNTOF(global_tank194_palette);i++)if((rgb_palette[global_tank194_palette[i].index]&0xffffffu)!=global_tank194_palette[i].rgb)return false;
 return true;
}
static bool global_tank194_underlay_matches(void)
{
 for(unsigned i=0;i<256;i++)if(global_tank194_used_colors[i]&&(rgb_palette[i]&0xffffffu)!=global_tank194_underlay_palette[i])return false;
 return true;
}
static void global_tank194_use_color(unsigned i)
{if(!global_tank194_used_colors[i]){global_tank194_used_colors[i]=1;global_tank194_underlay_palette[i]=rgb_palette[i]&0xffffffu;}}
static bool global_tank194_disjoint(const SDL_Surface *a,const SDL_Surface *b)
{
 uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;
 return x<y?y-x>=(size_t)a->pitch*a->h:x-y>=(size_t)b->pitch*b->h;
}
static bool global_tank194_layout(void)
{
 int d=game_probe_density;
 if(d!=8||!game_screen||!game_screen->pixels||!game_screen->format||
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
 for(unsigned i=0;i<4;i++)for(unsigned j=0;j<i;j++)if(!global_tank194_disjoint(all[i],all[j]))return false;
 return true;
}
static bool global_tank194_final_surface_matches(void)
{
 SDL_Surface *s=VGAScreenSeg;
 return s&&s==global_tank194_source_lease.final_surface&&s->pixels&&s->pixels==global_tank194_source_lease.final_pixels&&
  s->format&&s->format==global_tank194_source_lease.final_format&&s->w==320&&s->h==200&&s->pitch>=320&&s->pitch==global_tank194_source_lease.final_pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1;
}
static bool global_tank194_surface_matches(void)
{
 SDL_Surface *s=game_screen;
 return global_tank194_layout()&&canvas==global_tank194_source_lease.canvas_surface&&output==global_tank194_source_lease.output_surface&&
  canvas->pixels==global_tank194_source_lease.canvas_pixels&&output->pixels==global_tank194_source_lease.output_pixels&&
  canvas->format==global_tank194_source_lease.canvas_format&&output->format==global_tank194_source_lease.output_format&&
  canvas->pitch==global_tank194_source_lease.canvas_pitch&&output->pitch==global_tank194_source_lease.output_pitch&&
  s&&s==global_tank194_source_lease.surface&&s->pixels&&s->pixels==global_tank194_source_lease.pixels&&
  s->format&&s->format==global_tank194_source_lease.format&&s->w==320&&s->h==200&&s->pitch==320&&s->pitch==global_tank194_source_lease.pitch&&
  s->format->format==SDL_PIXELFORMAT_INDEX8&&s->format->BitsPerPixel==8&&s->format->BytesPerPixel==1&&
  game_probe_density==global_tank194_source_lease.density;
}



static bool global_tank194_resources_match(unsigned used)
{
 if(!global_tank194_good)return false;
 for(unsigned i=0;i<2;i++)if(used&(1u<<i)){
  const GlobalAssetResource *r=global_tank194_resources+i;
  if(r->identity!=(i?1010131u:1010041u)||r->bytes!=172060u||r->density!=8||r->width!=24||r->height!=28||r->anchor_x!=6||r->anchor_y!=7||
   !global_tank194_rgba[i]||global_bytes_hash(global_tank194_rgba[i],172032u)!=r->payload_fnv)return false;
 }
 return true;
}
static bool global_tank194_family_ready(void)
{
 if(!global_tank194_loaded){
  global_tank194_loaded=true;global_tank194_good=COUNTOF(global_tank194_resources)==2;
  for(unsigned i=0;i<2;i++)if(!(global_tank194_rgba[i]=global_resource_load(global_tank194_resources+i)))global_tank194_good=false;
 }
 return global_tank194_resources_match(3u);
}
static int global_tank194_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
static bool global_tank194_shape(unsigned slot)
{
 if(slot>=COUNTOF(global_tank194_slots))return false;
 const struct JE_SingleEnemyType *e=enemy+slot;bool exact=false;
 for(unsigned i=0;i<COUNTOF(enemySpriteSheetIds);i++)if(enemySpriteSheetIds[i]==20&&e->sprite2s==enemySpriteSheets+i)exact=true;
 if(!exact||e->enemytype!=194||e->enemydatofs!=&enemyDat[194]||e->size!=1||e->scoreitem||e->edamaged||
  e->ani!=enemyDat[194].ani||e->filter||e->edani!=enemyDat[194].dani||e->edgr!=enemyDat[194].dgr||e->edlevel!=enemyDat[194].dlevel)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=enemyDat[194].egraphic[i])return false;
 return true;
}
void render_mirror_tank194_enemy_allocated(void *ptr,unsigned record,int unique_shape)
{
 int slot=global_tank194_slot(ptr);if(slot<0)return;
 if(global_tank194_quartet.live&&global_tank194_quartet.slot==(unsigned)slot)global_tank194_fail();
 global_tank194_slots[slot].role=global_tank194_slots[slot].pending=false;
 if(global_tank194_slots[slot].generation==UINT64_MAX){global_tank194_slots[slot].exhausted=true;return;}
 if(global_tank194_slots[slot].exhausted)return;
 ++global_tank194_slots[slot].generation;
 global_tank194_slots[slot].pending=record==194&&enemyAvail[slot]==1&&(unique_shape<=0||unique_shape==20)&&
  global_tank194_record_matches()&&global_tank194_source_matches(global_tank194_bank());
 global_tank194_slots[slot].born_tick=mirror_logic_tick;
}
void render_mirror_tank194_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=global_tank194_slot(ptr);if(slot<0)return;
 global_tank194_slots[slot].role=global_tank194_slots[slot].pending&&global_tank194_slots[slot].born_tick==mirror_logic_tick&&
  record==194&&avail==0&&enemyAvail[slot]==1&&global_tank194_record_matches()&&global_tank194_shape((unsigned)slot);
 global_tank194_slots[slot].pending=false;global_tank194_slots[slot].witnessed=global_tank194_slots[slot].generation;
}
/* Retiring a coverage bit never retires proof obligations or contribution. */
static void global_tank194_retire(size_t n)
{
 /* This hook identifies an actual foreign RGB writer, including alpha-only
  * writes with no following native pixel callback. A quartet is continuous. */
 if(global_tank194_quartet.live&&!global_tank194_call.live)global_tank194_fail();
 if(n<global_tank194_capacity&&global_tank194_owner){global_tank194_owner[n]=0;global_tank194_foreign[n]=0;}
}
static void global_tank194_unsafe_sample(size_t n)
{
 if(global_tank194_quartet.live&&!global_tank194_call.live)global_tank194_fail();
 if(global_tank194_contributed&&n<global_tank194_capacity&&global_tank194_ever&&global_tank194_ever[n])global_tank194_fail();
}
static void global_tank194_fail(void)
{
 global_tank194_fault=true;global_tank194_call.live=false;global_tank194_quartet.live=false;
 if(global_tank194_contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;global_tank194_cached=false;}
}
static void global_tank194_reset(void)
{
 if(global_tank194_contributed||global_tank194_quartet.live)global_tank194_fail();
 global_tank194_frame=global_tank194_cached=false;
 global_tank194_call.live=global_tank194_quartet.live=false;
 memset(global_tank194_slots,0,sizeof(global_tank194_slots));
 if(global_tank194_owner)memset(global_tank194_owner,0,global_tank194_capacity);
 if(global_tank194_foreign)memset(global_tank194_foreign,0,global_tank194_capacity);
}
static void global_tank194_shutdown(void)
{
 global_tank194_reset();
 for(unsigned i=0;i<2;i++){free(global_tank194_rgba[i]);global_tank194_rgba[i]=NULL;}
 global_tank194_loaded=global_tank194_good=false;
 free(global_tank194_owner);free(global_tank194_foreign);free(global_tank194_ever);
 global_tank194_owner=global_tank194_foreign=global_tank194_ever=NULL;global_tank194_capacity=0;
}
/* No allocation or surface access: run before every begin's early-return
 * branch. Actor lifetime generations are deliberately independent of frames. */
static void global_tank194_tick_begin(void)
{
 if(global_tank194_cached||global_tank194_contributed){
  ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;
 }
 global_tank194_frame=global_tank194_cached=global_tank194_fault=global_tank194_contributed=false;
 memset(&global_tank194_call,0,sizeof(global_tank194_call));
 memset(&global_tank194_quartet,0,sizeof(global_tank194_quartet));
 global_tank194_used_resources=global_tank194_dependencies=0;
 global_tank194_platform_dependency=global_tank194_cyan_dependency=0;
 memset(global_tank194_used_colors,0,sizeof(global_tank194_used_colors));
 memset(&global_tank194_source_lease,0,sizeof(global_tank194_source_lease));
 memset(&global_tank194_fade_lease,0,sizeof(global_tank194_fade_lease));
 if(global_tank194_owner)memset(global_tank194_owner,0,global_tank194_capacity);
 if(global_tank194_foreign)memset(global_tank194_foreign,0,global_tank194_capacity);
 if(global_tank194_ever)memset(global_tank194_ever,0,global_tank194_capacity);
}
static void global_tank194_frame_begin(void)
{
 global_tank194_tick_begin();
 if(!global_tank194_requested()||!global_tank194_layout())return;
 size_t n=(size_t)canvas->w*canvas->h;
 if(n!=global_tank194_capacity){
  Uint8 *a=calloc(n,1),*b=calloc(n,1),*c=calloc(n,1);
  if(!a||!b||!c){free(a);free(b);free(c);return;}
  free(global_tank194_owner);free(global_tank194_foreign);free(global_tank194_ever);
  global_tank194_owner=a;global_tank194_foreign=b;global_tank194_ever=c;global_tank194_capacity=n;
 }
 global_tank194_source_lease.surface=game_screen;global_tank194_source_lease.pixels=game_screen->pixels;
 global_tank194_source_lease.format=game_screen->format;global_tank194_source_lease.pitch=game_screen->pitch;
 global_tank194_source_lease.final_surface=VGAScreenSeg;global_tank194_source_lease.final_pixels=VGAScreenSeg->pixels;
 global_tank194_source_lease.final_format=VGAScreenSeg->format;global_tank194_source_lease.final_pitch=VGAScreenSeg->pitch;
 global_tank194_source_lease.canvas_surface=canvas;global_tank194_source_lease.canvas_pixels=canvas->pixels;
 global_tank194_source_lease.canvas_format=canvas->format;global_tank194_source_lease.canvas_pitch=canvas->pitch;
 global_tank194_source_lease.output_surface=output;global_tank194_source_lease.output_pixels=output->pixels;
 global_tank194_source_lease.output_format=output->format;global_tank194_source_lease.output_pitch=output->pitch;
 global_tank194_source_lease.density=8;
 Sprite2_array bank=global_tank194_bank();global_tank194_source_lease.bank_data=bank.data;global_tank194_source_lease.bank_size=bank.size;
 global_tank194_frame=true;
}
/* HUF can preserve RGB underneath transparent glyph samples and later restore
 * it. Reject intersecting body history before that history can be captured. */
static void global_tank194_font_begin(SDL_Rect box)
{
 if(!global_tank194_contributed||box.w<=0||box.h<=0)return;
 if(!global_tank194_surface_matches()||!global_tank194_ever){global_tank194_fail();return;}
 int64_t left=MAX((int64_t)box.x,0),top=MAX((int64_t)box.y,0);
 int64_t right=MIN((int64_t)box.x+box.w,320),bottom=MIN((int64_t)box.y+box.h,200);
 for(int y=(int)top;y<bottom;y++)for(int x=(int)left;x<right;x++)for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  size_t n=(size_t)(y*8+sy)*canvas->w+x*8+sx;
  if(global_tank194_ever[n]||global_tank194_owner[n]){global_tank194_fail();return;}
 }
}
static bool global_tank194_font_cell_live(int x,int y)
{
 for(unsigned i=0;i<FONT_SCENE_COUNT;i++){
  const FontScene *f=font_scenes+i;
  if(f->canvas_live&&x>=f->rect.x&&y>=f->rect.y&&
   (int64_t)x<(int64_t)f->rect.x+f->rect.w&&(int64_t)y<(int64_t)f->rect.y+f->rect.h)return true;
 }
 return false;
}
/* These are finite ordinary peers, not a general owner registry. */
static unsigned global_tank194_peer_bits(size_t n)
{
 unsigned bits=0;
#define T194_PEER(name,bit) if(global_##name##_owner&&global_##name##_owner[n])bits|=(bit)
 T194_PEER(talon,1u);T194_PEER(shield,2u);T194_PEER(pulse,4u);T194_PEER(vulcan,8u);
 T194_PEER(hitflare,16u);T194_PEER(smoke,32u);T194_PEER(green,64u);T194_PEER(small_explosion,128u);
 T194_PEER(cash25,256u);T194_PEER(rotor,512u);T194_PEER(projectile91,1024u);
#if defined(NEWSHF_HD_COMPOSITOR) && NEWSHF_HD_COMPOSITOR
 T194_PEER(newshf,2048u);
#endif
#undef T194_PEER
 return bits;
}
static void global_tank194_clear_peers(size_t n)
{
#define T194_CLEAR(name) if(global_##name##_owner)global_##name##_owner[n]=global_##name##_foreign[n]=0
 T194_CLEAR(talon);T194_CLEAR(shield);T194_CLEAR(pulse);T194_CLEAR(vulcan);T194_CLEAR(hitflare);
 T194_CLEAR(smoke);T194_CLEAR(green);T194_CLEAR(small_explosion);T194_CLEAR(cash25);T194_CLEAR(rotor);T194_CLEAR(projectile91);
#undef T194_CLEAR
 global_newshf_clear(n);
}
static bool global_tank194_peer_calls_live(void)
{
 return global_talon_call.live||global_shield_call.live||global_pulse_call.live||global_vulcan_call.live||
  global_hitflare_call.live||global_smoke_call.live||global_green_call.live||global_small_explosion_call.live||
  global_cash25_call.live||global_rotor_call.live||global_projectile91_call.live;
}
static bool global_tank194_dependencies_match(void)
{
 unsigned d=global_tank194_dependencies;
 /* Peer proofs retain their own contributing payload and palette evidence even
  * after their visible coverage transfers to this body. Never clear those. */
 return !(d&~2047u)&&(!(d&1u)||(global_talon_contributed&&global_talon_finish_proof()))&&(!(d&2u)||(global_shield_contributed&&global_shield_finish_proof()))&&
  (!(d&4u)||(global_pulse_contributed&&global_pulse_finish_proof()))&&(!(d&8u)||(global_vulcan_contributed&&global_vulcan_finish_proof()))&&
  (!(d&16u)||(global_hitflare_contributed&&global_hitflare_finish_proof()))&&(!(d&32u)||(global_smoke_contributed&&global_smoke_finish_proof()))&&
  (!(d&64u)||(global_green_contributed&&global_green_finish_proof()))&&(!(d&128u)||(global_small_explosion_contributed&&global_small_explosion_finish_proof()))&&
  (!(d&256u)||(global_cash25_contributed&&global_cash25_finish_proof()))&&(!(d&512u)||(global_rotor_contributed&&global_rotor_finish_proof()))&&
  (!(d&1024u)||(global_projectile91_contributed&&global_projectile91_finish_proof()))&&
  (!global_tank194_platform_dependency||shapesy_borrow_check(global_tank194_platform_dependency))&&
  (!global_tank194_cyan_dependency||cyan_borrow_check(global_tank194_cyan_dependency));
}
static bool global_tank194_integrity(void)
{
 Sprite2_array b=global_tank194_bank();
 return global_tank194_requested()&&!global_tank194_fault&&global_tank194_surface_matches()&&global_tank194_final_surface_matches()&&
  b.data==global_tank194_source_lease.bank_data&&b.size==global_tank194_source_lease.bank_size&&
  global_tank194_source_matches(b)&&global_tank194_resources_match(global_tank194_used_resources)&&
  global_tank194_palette_matches()&&global_tank194_underlay_matches()&&global_tank194_dependencies_match();
}
static bool global_tank194_identity(int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!c||c->pool_slot>=COUNTOF(global_tank194_slots))return false;
 unsigned slot=c->pool_slot,q=part==0?0:part==1?1:part==19?2:part==20?3:4;
 const struct JE_SingleEnemyType *e=enemy+slot;Sprite2_array b=global_tank194_bank();
 if(q==4||c->type!=194||c->availability!=0||c->size!=1||c->score_item||c->damaged||filter||enemyAvail[slot]!=0||
  !global_tank194_slots[slot].role||global_tank194_slots[slot].witnessed!=global_tank194_slots[slot].generation||
  !global_tank194_shape(slot)||e->enemycycle<1||e->enemycycle>e->ani||e->enemycycle>20||
  (base!=91&&base!=93)||base!=e->egr[e->enemycycle-1]||!b.data||bank.data!=b.data||bank.size!=b.size||
  x!=(int)e->ex+(int)tempMapXOfs+(q&1?6:-6)||y!=(int)e->ey+(q>=2?7:-7))return false;
 int ox=x-(q&1?12:0),oy=y-(q>=2?14:0);
 /* The original caller must issue all four quadrants. Actual visible support
  * is checked for the entire composite before quadrant zero contributes. */
 if(e->ey<=-13||e->ey>=182||(int)e->ex+(int)tempMapXOfs<=-29||(int)e->ex+(int)tempMapXOfs>=300)return false;
 if(!global_tank194_quartet.live){
  if(q)return false;
  global_tank194_quartet.live=true;global_tank194_quartet.slot=slot;global_tank194_quartet.next=0;
  global_tank194_quartet.base=base;global_tank194_quartet.generation=global_tank194_slots[slot].generation;
  global_tank194_quartet.tick=mirror_logic_tick;global_tank194_quartet.x=ox;global_tank194_quartet.y=oy;
 }
 return global_tank194_quartet.slot==slot&&global_tank194_quartet.next==q&&global_tank194_quartet.base==base&&
  global_tank194_quartet.generation==global_tank194_slots[slot].generation&&global_tank194_quartet.tick==mirror_logic_tick&&
  global_tank194_quartet.x==ox&&global_tank194_quartet.y==oy;
}
static bool global_tank194_support_fits(Sprite2_array bank,unsigned base,int ox,int oy,const Uint8 *rgba)
{
 Uint8 indices[672]={0},mask[672]={0};
 if(!decode_tile(bank,base,indices,mask,24,0,0)||!decode_tile(bank,base+1,indices,mask,24,12,0)||
  !decode_tile(bank,base+19,indices,mask,24,0,14)||!decode_tile(bank,base+20,indices,mask,24,12,14))return false;
 for(int ay=0;ay<224;ay++)for(int ax=0;ax<192;ax++){
  if(!rgba[4*(ay*192+ax)+3]&&!mask[(ay/8)*24+ax/8])continue;
  int64_t dx=(int64_t)ox*8+ax,dy=(int64_t)oy*8+ay;
  if(dx<24*8||dx>=288*8||dy<0||dy>=184*8)return false;
 }
 return true;
}
static int render_mirror_global_tank194_body(SDL_Surface *s,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(global_tank194_contributed&&!global_tank194_integrity())global_tank194_fail();
 if(!global_tank194_requested())return -1;
 Sprite2_array b=global_tank194_bank();
 bool candidate=(c&&c->type==194)||(b.data&&bank.data==b.data&&(base==91||base==93));
 if(!candidate){if(global_tank194_quartet.live||global_tank194_call.live)global_tank194_fail();return -1;}
 if(global_tank194_fault||!global_tank194_frame||s!=game_screen||global_tank194_call.live||
  !global_tank194_surface_matches()||!global_tank194_source_matches(bank)||!global_tank194_palette_matches()||
  !global_tank194_underlay_matches()||!global_tank194_family_ready()||global_tank194_peer_calls_live()||suppress||vulcan_shadow.live){
  if(global_tank194_contributed||global_tank194_quartet.live)global_tank194_fail();return 0;}
 bool pending=global_tank194_quartet.live;
 if(part==0&&!global_tank194_support_fits(bank,base,x,y,global_tank194_rgba[base==91?0:1])){
  if(pending)global_tank194_fail();return 0;
 }
 if(!global_tank194_identity(x,y,bank,base,part,filter,c)){if(pending)global_tank194_fail();return 0;}
 memset(&global_tank194_call,0,sizeof(global_tank194_call));
 if(!decode_tile(bank,base+(unsigned)part,global_tank194_call.source,global_tank194_call.mask,12,0,0)){global_tank194_fail();return 0;}
 unsigned member=base==91?0:1;int qx=(part==1||part==20)?12:0,qy=(part==19||part==20)?14:0;
 const Uint8 *rgba=global_tank194_rgba[member];
 uint64_t platform=shapesy_borrow_ready(),cyan=cyan_borrow_ready();
 font_before_effect((SDL_Rect){x,y,12,14});
 /* Preflight every sample before the first RGB write of this quadrant. */
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){
  size_t n=(size_t)(y*8+ay)*canvas->w+x*8+ax;
  const Uint8 *a=rgba+4*((qy*8+ay)*192+qx*8+ax);
  if(!a[3]&&!global_tank194_call.mask[(ay/8)*12+ax/8])continue;
  unsigned peers=global_tank194_peer_bits(n);Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+(y*8+ay)*canvas->pitch))[x*8+ax];
  if((peers&&(peers&(peers-1)))||(global_tank194_owner[n]&&peers)||hd_owner[n]>1||
   (!hd_owner[n]&&(peers||global_tank194_owner[n]||color!=palette_rgb(((Uint8 *)game_screen->pixels)[(y+ay/8)*320+x+ax/8])))){
   global_tank194_fail();return 0;}
  if(hd_owner[n]&&!global_tank194_owner[n]&&!peers){
   bool p=platform&&shapesy_borrow_sample(platform,n,color),c2=cyan&&cyan_borrow_sample(cyan,n,color);
   if(!p&&!c2){global_tank194_fail();return 0;}
   if(c2){if(global_tank194_cyan_dependency&&global_tank194_cyan_dependency!=cyan){global_tank194_fail();return 0;}global_tank194_cyan_dependency=cyan;}
   else {if(global_tank194_platform_dependency&&global_tank194_platform_dependency!=platform){global_tank194_fail();return 0;}global_tank194_platform_dependency=platform;}
  }
  global_tank194_dependencies|=peers;
 }
 if(!global_tank194_dependencies_match()){global_tank194_fail();return 0;}
 global_tank194_used_resources|=1u<<member;
 global_tank194_call.x=x;global_tank194_call.y=y;global_tank194_call.live=true;
 for(unsigned i=0;i<168;i++)if(global_tank194_call.mask[i])global_tank194_call.left++;
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++){
  size_t n=(size_t)(y*8+ay)*canvas->w+x*8+ax;const Uint8 *a=rgba+4*((qy*8+ay)*192+qx*8+ax);
  if(!a[3]&&!global_tank194_call.mask[(ay/8)*12+ax/8])continue;
  Uint32 *p=(Uint32 *)((Uint8 *)canvas->pixels+(y*8+ay)*canvas->pitch)+x*8+ax;
  bool foreign=global_tank194_owner[n]?global_tank194_foreign[n]:hd_owner[n]!=0;
  if(!hd_owner[n])global_tank194_use_color(((Uint8 *)game_screen->pixels)[(y+ay/8)*320+x+ax/8]);
  else if(foreign)for(unsigned i=0;i<256;i++)global_tank194_use_color(i);
  if(a[3]){*p=blend_rgba(*p,a,a[3]);if(a[3]==255)foreign=false;}
  /* Sample/blend first, then transfer ownership. */
  global_tank194_clear_peers(n);global_tank194_contributed=true;global_tank194_ever[n]=1;
  global_tank194_owner[n]=1;global_tank194_foreign[n]=foreign;hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  selected[(y+ay/8)*320+x+ax/8]=1;
 }
 ++draws;return 1;
}
static bool global_tank194_pixel(int x,int y,Uint8 before,Uint8 after,int style)
{
 (void)before;
 if(!global_tank194_call.live)return false;
 int dx=x-global_tank194_call.x,dy=y-global_tank194_call.y;
 if(dx<0||dx>=12||dy<0||dy>=14||style!=MIRROR_NORMAL){global_tank194_fail();return false;}
 unsigned n=(unsigned)(dy*12+dx);
 if(!global_tank194_call.mask[n]||global_tank194_call.seen[n]||after!=global_tank194_call.source[n]||!global_tank194_call.left){global_tank194_fail();return false;}
 global_tank194_call.seen[n]=1;--global_tank194_call.left;return true;
}
static void global_tank194_end(void)
{
 if(!global_tank194_call.live)return;
 if(global_tank194_call.left){global_tank194_fail();return;}
 global_tank194_call.live=false;
 if(!global_tank194_quartet.live){global_tank194_fail();return;}
 if(++global_tank194_quartet.next==4)global_tank194_quartet.live=false;
}
static bool global_tank194_finish_proof(void)
{
 if(!global_tank194_contributed)return true;
 bool ok=!global_tank194_call.live&&!global_tank194_quartet.live&&global_tank194_integrity();
 if(!ok)global_tank194_fail();return ok;
}
static bool global_tank194_final_preflight_pixel(SDL_Surface *s,Uint8 *address)
{
 if(!global_tank194_contributed)return true;
 if(global_tank194_fault)return false;
 if(s!=VGAScreenSeg)return true;
 if(!global_tank194_surface_matches()||!global_tank194_final_surface_matches()){global_tank194_fail();return false;}
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;
 if(off<0||off>=(intptr_t)s->pitch*200){global_tank194_fail();return false;}
 int x=(int)(off%s->pitch),y=(int)(off/s->pitch);if(x>=264||y>=184)return true;
 unsigned owned=0;bool inherited=false;
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  size_t n=(size_t)(y*8+sy)*canvas->w+(x+24)*8+sx;
  inherited=inherited||(global_tank194_ever[n]&&(hd_owner[n]||global_tank194_peer_bits(n)));
  if(!global_tank194_owner[n])continue;
  ++owned;
  if(global_tank194_foreign[n]||hd_owner[n]!=1||global_tank194_peer_bits(n)||cloud_owner[n]||green_first[n]){global_tank194_fail();return false;}
 }
 /* A peer may retain our RGB after every current body bit has retired. Its
  * final hook must not validate a whole logical cell on that partial history. */
 if((owned||inherited)&&owned!=64){global_tank194_fail();return false;}
 return true;
}
/* Returns false only for a fully handled shadow or a permanent frame rejection.
 * The original INDEX8 write already happened; validate all 64 RGB samples before
 * changing any sample or advancing expected. Native caller remains untouched. */
static bool global_tank194_pre_native(SDL_Surface *s,Uint8 *address,int style)
{
 if(!global_tank194_contributed)return true;
 if(global_tank194_fault)return false;
 if(global_tank194_quartet.live&&!global_tank194_call.live){global_tank194_fail();return false;}
 if(s==VGAScreenSeg)return global_tank194_final_preflight_pixel(s,address);
 if(s!=game_screen)return true;
 if(!global_tank194_requested()||!global_tank194_surface_matches()){global_tank194_fail();return false;}
 if(global_tank194_call.live)return true;
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;
 if(off<0||off>=64000){global_tank194_fail();return false;}
 int x=(int)(off%320),y=(int)(off/320);unsigned owned=0;bool inherited=false;
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  size_t n=(size_t)(y*8+sy)*canvas->w+x*8+sx;
  owned+=global_tank194_owner[n]!=0;
  inherited=inherited||(global_tank194_ever[n]&&hd_owner[n]);
 }
 if(!owned){
  if(inherited&&style!=MIRROR_NORMAL&&!global_tank194_peer_calls_live()){global_tank194_fail();return false;}
  return true;
 }
 if(style==MIRROR_NORMAL){
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
   size_t n=(size_t)(y*8+sy)*canvas->w+x*8+sx;if(!global_tank194_owner[n])continue;
   /* Leave RGB/hd_owner intact for the original downstream font or peer
    * observer to sample; ordinary fallback performs the opaque overwrite. */
   global_tank194_retire(n);
  }
  return true;
 }
 Uint8 before=expected[y*320+x],after=*address;
 if(style!=MIRROR_SHADOW||!global_tank194_frame||global_tank194_cached||global_tank194_quartet.live||
  suppress||suppress_cloud||suppress_green_smoke||vulcan_shadow.live||font_glyph_active||font_context>=0||
  global_tank194_peer_calls_live()||global_tank194_font_cell_live(x,y)||
  after!=(Uint8)((before&0xf0)|((before&15)/2))||!global_tank194_integrity()){
  global_tank194_fail();return false;}
 Uint32 result[64];unsigned k=0;
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++,k++){
  size_t n=(size_t)(y*8+sy)*canvas->w+x*8+sx;
  Uint32 color=((Uint32 *)((Uint8 *)canvas->pixels+(y*8+sy)*canvas->pitch))[x*8+sx];
  if(global_tank194_foreign[n]||global_tank194_peer_bits(n)||cloud_owner[n]||green_first[n]||(color>>24)!=255){global_tank194_fail();return false;}
  if(global_tank194_owner[n]){
   if(hd_owner[n]!=1||!global_tank194_ever[n]){global_tank194_fail();return false;}
   result[k]=darken_rgba(color,255);
  }else{
   if(hd_owner[n]||color!=palette_rgb(before)){global_tank194_fail();return false;}
   result[k]=palette_rgb(after);
  }
 }
 /* No mutation in the proof loop above. Body RGB is darkened exactly once;
  * classic samples get the palette's native result, not half their RGB. */
 k=0;
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++,k++)
  ((Uint32 *)((Uint8 *)canvas->pixels+(y*8+sy)*canvas->pitch))[x*8+sx]=result[k];
 global_tank194_use_color(before);global_tank194_use_color(after);
 expected[y*320+x]=after;return false;
}
static bool global_tank194_final_preflight_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if(!global_tank194_contributed)return true;
 if(global_tank194_fault)return false;
 if(s!=VGAScreenSeg&&s!=game_screen)return true;
 if(!global_tank194_surface_matches()||!global_tank194_final_surface_matches()||global_tank194_call.live||global_tank194_quartet.live){global_tank194_fail();return false;}
 int64_t x=r?r->x:0,y=r?r->y:0,right=r?x+r->w:320,bottom=r?y+r->h:200;
 x=MAX(MAX(x,s->clip_rect.x),0);y=MAX(MAX(y,s->clip_rect.y),0);
 right=MIN(MIN(right,(int64_t)s->clip_rect.x+s->clip_rect.w),320);bottom=MIN(MIN(bottom,(int64_t)s->clip_rect.y+s->clip_rect.h),200);
 if(s==VGAScreenSeg){
  for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)
   if(!global_tank194_final_preflight_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx))return false;
 }else{
  /* An ordinary native rectangle is an opaque logical-cell overwrite. */
  for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
   size_t n=(size_t)(yy*8+sy)*canvas->w+xx*8+sx;if(!global_tank194_owner[n])continue;
   global_tank194_retire(n);
  }
 }
 return true;
}
static bool global_tank194_compose(MirrorOutputKind kind,int lightx,int lighty)
{
 (void)lightx;(void)lighty;
 if(!global_tank194_contributed){global_tank194_frame=false;return false;}
 if(kind!=MIRROR_OUTPUT_ORDINARY||!global_tank194_finish_proof()){global_tank194_fail();return false;}
 for(int y=0;y<200;y++)if(memcmp(expected+y*320,(Uint8 *)game_screen->pixels+y*320,320)){global_tank194_fail();return false;}
 /* Prove the entire native scene crop before copying any body contribution. */
 for(int y=0;y<184;y++)if(memcmp((Uint8 *)game_screen->pixels+y*320+24,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,264)){
  global_tank194_fail();return false;}
 bool retained=false;
 for(int y=0;y<184;y++)for(int x=24;x<288;x++)for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  int px=x*8+sx,py=y*8+sy;size_t n=(size_t)py*canvas->w+px;if(!global_tank194_owner[n])continue;
  if(reject_reason&&global_tank194_foreign[n]){global_tank194_fail();return false;}
  ((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px-192]=((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px];retained=true;
 }
 memcpy(global_tank194_output_palette,rgb_palette,sizeof(global_tank194_output_palette));
 global_tank194_cached=true;global_tank194_frame=false;return retained;
}
static bool global_tank194_cache_dependencies_match(void)
{
 unsigned d=global_tank194_dependencies;
 return !(d&~2047u)&&(!(d&1u)||(global_talon_contributed&&global_talon_cache_source_matches()))&&(!(d&2u)||(global_shield_contributed&&global_shield_cache_source_matches()))&&
  (!(d&4u)||(global_pulse_contributed&&global_pulse_cache_source_matches()))&&(!(d&8u)||(global_vulcan_contributed&&global_vulcan_cache_source_matches()))&&
  (!(d&16u)||(global_hitflare_contributed&&global_hitflare_cache_source_matches()))&&(!(d&32u)||(global_smoke_contributed&&global_smoke_cache_source_matches()))&&
  (!(d&64u)||(global_green_contributed&&global_green_cache_source_matches()))&&(!(d&128u)||(global_small_explosion_contributed&&global_small_explosion_cache_source_matches()))&&
  (!(d&256u)||(global_cash25_contributed&&global_cash25_cache_source_matches()))&&(!(d&512u)||(global_rotor_contributed&&global_rotor_cache_source_matches()))&&
  (!(d&1024u)||(global_projectile91_contributed&&global_projectile91_cache_source_matches()))&&
  (!global_tank194_platform_dependency||shapesy_borrow_check(global_tank194_platform_dependency))&&
  (!global_tank194_cyan_dependency||cyan_borrow_check(global_tank194_cyan_dependency));
}
static bool global_tank194_cache_source_matches(void)
{
 Sprite2_array b=global_tank194_bank();
 bool ok=global_tank194_requested()&&!global_tank194_fault&&!global_tank194_call.live&&!global_tank194_quartet.live&&
  global_tank194_surface_matches()&&global_tank194_final_surface_matches()&&
  b.data==global_tank194_source_lease.bank_data&&b.size==global_tank194_source_lease.bank_size&&
  global_tank194_source_matches(b)&&global_tank194_resources_match(global_tank194_used_resources)&&global_tank194_cache_dependencies_match();
 if(ok)for(int y=0;y<200;y++)if(memcmp(last_output_indices+y*320,(Uint8 *)VGAScreenSeg->pixels+y*VGAScreenSeg->pitch,320)){ok=false;break;}
 return ok;
}
static bool global_tank194_cache_decline(void)
{global_tank194_fail();return false;}
static void global_tank194_check_cache(void)
{
 if(!global_tank194_contributed)return;
 if(global_tank194_fault||(global_tank194_cached&&(!global_tank194_cache_source_matches()||
  memcmp(global_tank194_output_palette,rgb_palette,sizeof(global_tank194_output_palette)))))global_tank194_fail();
}
static bool global_tank194_output_safe(void)
{
 if(!global_tank194_contributed)return true;
 bool ok=global_tank194_cached?global_tank194_cache_source_matches()&&!memcmp(global_tank194_output_palette,rgb_palette,sizeof(global_tank194_output_palette)):
  global_tank194_frame&&global_tank194_finish_proof();
 if(!ok)global_tank194_fail();return ok;
}
static bool global_tank194_fade_buffer_layout(void)
{
 SDL_Surface *s=fade_saved;int d=game_probe_density;
 if(!s||!s->pixels||!s->format||s->w!=320*d||s->h!=200*d||s->pitch<s->w*4||s->pitch%4||
  (uintptr_t)s->pixels%sizeof(Uint32)||s->format->format!=SDL_PIXELFORMAT_ARGB8888||
  s->format->BitsPerPixel!=32||s->format->BytesPerPixel!=4)return false;
 SDL_Surface *others[4]={game_screen,VGAScreenSeg,canvas,output};
 for(unsigned i=0;i<4;i++)if(!global_tank194_disjoint(s,others[i]))return false;
 return true;
}
static bool global_tank194_fade_buffer_safe(void)
{
 if(!global_tank194_contributed)return true;
 if(global_tank194_fault||!global_tank194_cached)return global_tank194_cache_decline();
 return (global_tank194_cache_source_matches()&&global_tank194_fade_buffer_layout())||global_tank194_cache_decline();
}
static bool global_tank194_fade_lease_matches(void)
{
 return global_tank194_fade_buffer_layout()&&fade_saved==global_tank194_fade_lease.surface&&
  fade_saved->pixels==global_tank194_fade_lease.pixels&&fade_saved->format==global_tank194_fade_lease.format&&fade_saved->pitch==global_tank194_fade_lease.pitch;
}
static bool global_tank194_fade_capture(void)
{
 if(!global_tank194_contributed)return true;
 if(global_tank194_fault||!global_tank194_cached)return global_tank194_cache_decline();
 if(!global_tank194_cache_source_matches()||!global_tank194_fade_buffer_layout()||
  (fade_mode==3&&!global_tank194_fade_lease_matches()))return global_tank194_cache_decline();
 global_tank194_fade_lease.surface=fade_saved;global_tank194_fade_lease.pixels=fade_saved->pixels;
 global_tank194_fade_lease.format=fade_saved->format;global_tank194_fade_lease.pitch=fade_saved->pitch;
 return true;
}
static bool global_tank194_fade_step_valid(int steps)
{
 if(!global_tank194_contributed)return true;
 if(global_tank194_fault||!global_tank194_cached)return global_tank194_cache_decline();
 if(steps<=0||fade_mode<1||fade_mode>3||!have_fade_saved||!global_tank194_cache_source_matches()||!global_tank194_fade_lease_matches())return global_tank194_cache_decline();
 /* The engine updates the indexed palette before this callback. Prove that
  * actual integer step, not equality with the deliberately older palette. */
 for(unsigned i=0;i<256;i++)for(int shift=0;shift<24;shift+=8) {
  int before=(global_tank194_output_palette[i]>>shift)&255;
  int target=fade_mode==1?0:fade_mode==2?255:(int)((fade_saved_palette[i]>>shift)&255);
  if((int)((rgb_palette[i]>>shift)&255)!=before+(target-before)/steps)return global_tank194_cache_decline();
 }
 return true;
}

static void global_tank194_fade_palette(void)
{if(global_tank194_cached)memcpy(global_tank194_output_palette,rgb_palette,sizeof(global_tank194_output_palette));}
static void global_tank194_final_pixel(SDL_Surface *s,Uint8 *address)
{
 if(!global_tank194_contributed||s!=VGAScreenSeg||global_tank194_fault)return;
 if(!global_tank194_final_preflight_pixel(s,address))return;
 if(global_tank194_cached&&have_fade_saved&&!global_tank194_fade_lease_matches()){global_tank194_fail();return;}
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;
 if(off<0||off>=(intptr_t)s->pitch*200)return;
 int x=(int)(off%s->pitch),y=(int)(off/s->pitch);if(x>=264||y>=184)return;
 bool changed=false;
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  int px=(x+24)*8+sx,py=y*8+sy;size_t n=(size_t)py*canvas->w+px;
  if(!global_tank194_owner[n])continue;
  global_tank194_retire(n);hd_owner[n]=cloud_owner[n]=0;green_first[n]=0;changed=true;
  ((Uint32 *)((Uint8 *)canvas->pixels+py*canvas->pitch))[px]=palette_rgb(*address);
  if(global_tank194_cached){
   ((Uint32 *)((Uint8 *)output->pixels+py*output->pitch))[px-192]=palette_rgb(*address);
   if(have_fade_saved)((Uint32 *)((Uint8 *)fade_saved->pixels+py*fade_saved->pitch))[px-192]=0xff000000u|(fade_saved_palette[*address]&0xffffffu);
  }
 }
 if(changed&&global_tank194_cached)last_output_indices[y*320+x]=*address;
}
static void global_tank194_final_rect(SDL_Surface *s,const SDL_Rect *r)
{
 if(!global_tank194_contributed||s!=VGAScreenSeg||global_tank194_fault)return;
 if(!global_tank194_final_preflight_rect(s,r))return;
 int64_t x=r?r->x:0,y=r?r->y:0,right=r?x+r->w:320,bottom=r?y+r->h:200;
 x=MAX(MAX(x,s->clip_rect.x),0);y=MAX(MAX(y,s->clip_rect.y),0);
 right=MIN(MIN(right,(int64_t)s->clip_rect.x+s->clip_rect.w),264);bottom=MIN(MIN(bottom,(int64_t)s->clip_rect.y+s->clip_rect.h),184);
 for(int yy=(int)y;yy<bottom;yy++)for(int xx=(int)x;xx<right;xx++)global_tank194_final_pixel(s,(Uint8 *)s->pixels+yy*s->pitch+xx);
}
static bool global_tank194_observe_blend(SDL_Surface *s,Uint8 *address)
{
 if(!global_tank194_contributed||s!=game_screen)return false;
 if(global_tank194_fault||global_tank194_call.live||!global_tank194_surface_matches())return true;
 intptr_t off=(intptr_t)address-(intptr_t)s->pixels;if(off<0||off>=64000)return true;
 int x=(int)(off%320),y=(int)(off/320);
 for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
  size_t n=(size_t)(y*8+sy)*canvas->w+x*8+sx;
  if(global_tank194_owner[n]||(global_tank194_ever[n]&&hd_owner[n]))return true;
 }
 return false;
}
