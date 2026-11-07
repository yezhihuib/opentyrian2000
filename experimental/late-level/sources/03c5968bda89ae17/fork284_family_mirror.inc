/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private ordinary E1 physical2 record284, only original events12..15.
 * Default OFF: FORK284_ENABLE=1 and FORK284_ASSET_DIR. This sparse material
 * cannot grant a display lease. Never writes gameplay, events, RNG or palette.
 */
#include "fork284_native.inc"
static const struct {unsigned time;int x;} f284_events[4]={{140,70},{140,280},{160,120},{160,230}};
static struct {uint64_t generation,witness;bool exhausted,pending,initialized,live;
 Fork284Birth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} f284_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;unsigned consumed;char root[1024];
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot,x,y;bool bg3x1,bg3x1b;int map1,map3;} call;
} f284_life;
static struct {bool checked,valid;char root[1024];Asset member;} f284_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,part,pixels;
 Fork284Draw draw[25];Fork284Write writes[25][270];} f284_frame;
static uint8_t f284_owned[64000],f284_shadows[64000];
static uint64_t f284_blend_retirements,f284_normal_retirements,f284_shadow_writes;
static uint64_t f284_clipped,f284_unwitnessed,f284_lifetime_losses,f284_bank_losses,f284_contract_faults;
static unsigned f284_first_reason;
static bool f284_resources_current(void);
static const char *f284_root(void){const char *p=getenv("FORK284_ASSET_DIR");return p?p:"";}
static bool f284_enabled(void)
{
 const char *e=getenv("FORK284_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool f284_level_scope(void)
{
 return f284_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static bool f284_event_matches(unsigned event)
{
 if(!f284_life.events||event<12||event>15||maxEvent!=731)return false;
 const struct JE_EventRecType *r=f284_life.events+event-1;
 /* Immutable original pins, never constructed from mutable eventRec bytes. */
 return r->eventtime==f284_events[event-12].time&&r->eventtype==7&&r->eventdat==284&&
 r->eventdat2==f284_events[event-12].x&&r->eventdat3==2&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6;
}
static bool f284_events_current(void)
{
 for(unsigned e=12;e<=15;e++)if(!f284_event_matches(e))return false;
 return true;
}
static bool f284_scope(void)
{
 return f284_life.loaded&&!f284_life.exhausted&&f284_level_scope()&&terrain_file=='z'&&
 f284_events_current()&&!strcmp(f284_life.root,f284_root());
}
static void f284_fail(unsigned reason)
{
 /* Only real renderer/lifecycle failures latch resource integrity loss. */
 if(f284_resources.checked&&!f284_resources_current())f284_resources.valid=false;
 if(!f284_first_reason)f284_first_reason=reason;
 f284_frame.fault=true;f284_frame.accepted=false;f284_frame.active=false;f284_frame.pending=false;
 if(f284_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_fork284_retired(unsigned slot)
{
 if(slot>=100)return;
 if(f284_slots[slot].live||f284_slots[slot].pending){
  ++f284_lifetime_losses;
  if(slot>=50&&slot<75&&f284_frame.draw[slot-50].token)f284_fail(1);
 }
 f284_slots[slot].live=f284_slots[slot].pending=f284_slots[slot].initialized=false;
 f284_slots[slot].birth.live=false;
}
static void f284_reset(void)
{
 if(f284_frame.contributed||f284_frame.pending)f284_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_fork284_retired(i);
 f284_life.call.live=false;
 if(f284_life.epoch==UINT64_MAX)f284_life.exhausted=true;else ++f284_life.epoch;
 /* Only real level begin clears consumed event origins. */
}
void render_mirror_fork284_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 f284_reset();f284_life.loaded=false;f284_life.events=events;f284_life.consumed=0;
 for(unsigned i=0;i<100;i++)memset(&f284_slots[i].birth,0,sizeof f284_slots[i].birth);
 if(!f284_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!f284_events_current()||
 !f284_root()[0]||strlen(f284_root())>=sizeof f284_life.root){f284_life.events=NULL;return;}
 strcpy(f284_life.root,f284_root());f284_life.loaded=true;
}
static int f284_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool f284_source(Sprite2_array *bank)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=42012)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank==enemySpriteSheets+i)bound=true;
 return bound&&asteroid1_stamp(bank->data,bank->size)==UINT64_C(0x913975450e0fc00d)&&
 asteroid1_record_stamp(284)==UINT64_C(0x09e7101d27e463b8);
}
static bool f284_colors(void)
{
 for(unsigned i=0;i<COUNTOF(f284_palette);i++)if((rgb_palette[f284_palette[i].index]&0xffffffu)!=f284_palette[i].rgb)return false;
 return true;
}
/* stage0: live, stage1: exact initialized constructor, stage2: event commit.
 * Positions and idle countdowns are birth-only. Finish uses saved draw origin. */
static bool f284_shape(unsigned slot,unsigned stage)
{
 if(slot<50||slot>=75)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=284||e->enemydatofs!=enemyDat+284||!f284_source(e->sprite2s)||
 e->size!=1||e->filter||e->enemycycle!=1||e->ani!=1||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->linknum||e->enemydie||
 e->exc||e->eyc!=(stage==1?2:4)||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||!e->enemyground||e->explonum!=3||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]||e->freq[i])return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=(i?0:121))return false;
 if(stage&&(e->mapoffset||e->iced||e->launchwait||e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||
 e->exccadd!=-1||e->eyccadd!=-1||e->exca!=-1||e->eyca!=-1||
 e->xminbounce!=-10000||e->xmaxbounce!=10000||e->yminbounce!=-10000||e->ymaxbounce!=10000))return false;
 if(stage)for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=255)return false;
 if(stage==1&&(e->ey!=-12||e->ex<6||e->ex>255))return false;
 return true;
}
uint64_t render_mirror_fork284_event_begin(unsigned event,unsigned typeofs,unsigned pool,int unique)
{
 if(f284_life.call.live){f284_life.call.live=false;f284_fail(3);return 0;}
 if(!f284_scope()||event!=eventLoc||typeofs||pool!=50||unique||background3x1b||!f284_event_matches(event)||
 curLoc!=f284_events[event-12].time)return 0;
 unsigned bit=1u<<(event-12);
 if(f284_life.consumed&bit)return 0;
 f284_life.consumed|=bit; /* Failed allocation consumes the original origin. */
 if(f284_life.serial==UINT64_MAX){f284_life.exhausted=true;return 0;}
 f284_life.call.live=true;f284_life.call.token=++f284_life.serial;f284_life.call.epoch=f284_life.epoch;
 f284_life.call.event=event;f284_life.call.slot=-1;f284_life.call.generation=0;
 f284_life.call.bg3x1=background3x1;f284_life.call.bg3x1b=background3x1b;
 f284_life.call.map1=mapX;f284_life.call.map3=mapX3;
 /* Exact case50 branch of JE_createNewEventEnemy, not the ground-pool path. */
 f284_life.call.x=background3x1?f284_events[event-12].x-(mapX-1)*24-12:
 f284_events[event-12].x-mapX3*24-24*2+6;
 if(background3x1b)f284_life.call.x-=6;
 f284_life.call.y=-28+(background3x1b?4:0);
 return f284_life.call.token;
}
void render_mirror_fork284_enemy_allocated(void *p,unsigned record,int unique)
{
 int s=f284_slot(p);if(s<0)return;
 render_mirror_fork284_retired((unsigned)s);
 if(f284_slots[s].generation==UINT64_MAX){f284_slots[s].exhausted=true;return;}
 if(f284_slots[s].exhausted)return;
 ++f284_slots[s].generation; /* All allocations, including unrelated records. */
 if(f284_life.call.live&&f284_scope()&&s>=50&&s<75&&enemyAvail[s]==1&&!unique&&record==284&&f284_life.call.slot==-1){
  f284_slots[s].pending=true;f284_life.call.slot=s;f284_life.call.generation=f284_slots[s].generation;
 }
}
void render_mirror_fork284_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 int s=f284_slot(p);if(s<0)return;
 f284_slots[s].initialized=f284_slots[s].pending&&f284_life.call.live&&f284_scope()&&
 f284_life.call.slot==s&&f284_life.call.generation==f284_slots[s].generation&&
 record==284&&avail==0&&enemyAvail[s]==1&&f284_shape((unsigned)s,1);
}
void render_mirror_fork284_event_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=f284_life.call.slot;
 bool ok=f284_life.call.live&&token==f284_life.call.token&&f284_life.call.epoch==f284_life.epoch&&f284_scope()&&
 s>=50&&s<75&&one_based==(unsigned)s+1&&eventLoc==f284_life.call.event&&
 curLoc==f284_events[f284_life.call.event-12].time&&background3x1==f284_life.call.bg3x1&&
 background3x1b==f284_life.call.bg3x1b&&mapX==f284_life.call.map1&&mapX3==f284_life.call.map3;
 if(ok)ok=f284_slots[s].pending&&f284_slots[s].initialized&&f284_life.call.generation==f284_slots[s].generation&&
 enemyAvail[s]==0&&f284_shape((unsigned)s,2)&&enemy[s].ex==f284_life.call.x&&enemy[s].ey==f284_life.call.y;
 if(s>=0&&s<100){
  f284_slots[s].live=ok;f284_slots[s].pending=f284_slots[s].initialized=false;
  if(ok){f284_slots[s].witness=f284_slots[s].generation;f284_slots[s].bank=enemy[s].sprite2s;
   f284_slots[s].data=enemy[s].sprite2s->data;f284_slots[s].bytes=enemy[s].sprite2s->size;
   f284_slots[s].birth=(Fork284Birth){.epoch=f284_life.epoch,.token=token,.generation=f284_slots[s].generation,
    .slot=(unsigned)s,.event=f284_life.call.event,.record=284,.bank_role=8,.bank_bytes=42012,
    .bank_stamp=UINT64_C(0x913975450e0fc00d),.record_stamp=UINT64_C(0x09e7101d27e463b8),
    .bank_object=(uintptr_t)f284_slots[s].bank,.bank_data=(uintptr_t)f284_slots[s].data,
    .event_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 f284_life.call.live=false;
}
void render_mirror_fork284_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(f284_slots[i].live&&f284_slots[i].bank==bank){++f284_bank_losses;render_mirror_fork284_retired(i);}
 if(f284_life.call.live){f284_life.call.live=false;f284_fail(4);}
}
static bool f284_witness(unsigned s)
{
 return s>=50&&s<75&&f284_slots[s].live&&!f284_slots[s].exhausted&&
 f284_slots[s].birth.epoch==f284_life.epoch&&f284_event_matches(f284_slots[s].birth.event)&&
 f284_slots[s].generation==f284_slots[s].witness&&enemyAvail[s]==0&&enemy[s].sprite2s&&
 f284_slots[s].bank==enemy[s].sprite2s&&f284_slots[s].data==enemy[s].sprite2s->data&&f284_slots[s].bytes==enemy[s].sprite2s->size;
}
static void f284_tick(void)
{
 if(f284_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&f284_frame,0,sizeof f284_frame);memset(f284_owned,0,sizeof f284_owned);memset(f284_shadows,0,sizeof f284_shadows);f284_first_reason=0;
 if(f284_life.loaded&&!f284_scope()){f284_reset();f284_life.loaded=false;return;}
 for(unsigned i=50;i<75;i++)if(f284_slots[i].live&&(!f284_witness(i)||!f284_shape(i,0)))render_mirror_fork284_retired(i);
}
static bool f284_load(void)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-121-8.hda",f284_resources.root);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==1080121&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==UINT64_C(0x56eb78103f545e7e);
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 f284_resources.member=(Asset){true,true,ASSET_ASTEROID1,121,24,28,0,0,8,rgba};return true;
}
static bool f284_resources_current(void)
{
 const Asset *a=&f284_resources.member;
 bool ok=f284_resources.checked&&f284_resources.valid&&!strcmp(f284_resources.root,f284_root())&&
 a->initialized&&a->valid&&a->bank==ASSET_ASTEROID1&&a->index==121&&a->w==24&&a->h==28&&
 !a->anchor_x&&!a->anchor_y&&a->density==8&&a->rgba&&asteroid1_stamp(a->rgba,172032)==UINT64_C(0x56eb78103f545e7e);
 return ok;
}
static bool f284_ready(void)
{
 if(!f284_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!f284_resources.checked){f284_resources.checked=true;strcpy(f284_resources.root,f284_life.root);f284_resources.valid=f284_load();}
 if(!f284_resources_current()){f284_resources.valid=false;return false;}
 return true;
}
static void f284_shutdown(void)
{
 f284_reset();f284_life.loaded=false;free(f284_resources.member.rgba);memset(&f284_resources,0,sizeof f284_resources);
}
static bool f284_dependencies(bool partial)
{
 if(!f284_frame.contributed)return true;
 if(f284_frame.fault||!f284_scope()||!f284_colors()||!f284_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<25;i++)if(f284_frame.draw[i].token){const Fork284Draw *d=f284_frame.draw+i;unsigned s=i+50;
  if(!f284_witness(s)||!f284_shape(s,0)||d->generation!=f284_slots[s].generation||
  d->token!=f284_slots[s].birth.token||d->epoch!=f284_life.epoch||d->event!=f284_slots[s].birth.event||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data)return false;
  if(!d->complete){if(!partial||!f284_frame.pending||f284_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=270)return false;
 }
 return partial||(!f284_frame.active&&!f284_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool f284_finish(void){return f284_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool f284_guard(void)
{
 if(f284_finish())return true;
 f284_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool f284_before_tile(unsigned slot,int part)
{
 if(f284_frame.contributed&&!f284_dependencies(true)){f284_fail(5);return false;}
 if(f284_frame.pending&&(f284_frame.active||slot!=f284_frame.slot||
 f284_frame.draw[slot-50].next>=4||part!=(int)f284_parts[f284_frame.draw[slot-50].next])){f284_fail(6);return false;}
 return true;
}
static bool f284_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool f284_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!f284_enabled()||slot<50||slot>=75||enemy[slot].enemytype!=284)return false;
 if(!fc.frame_active||fc.frame_failed||!f284_witness(slot)){++f284_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)f284_parts[k];k++);
 if(k==4){if(f284_frame.contributed)f284_fail(7);return false;}
 int64_t ox=(int64_t)x-f284_px[k],oy=(int64_t)y-f284_py[k];
 Fork284Draw *d=f284_frame.draw+slot-50;
 if(!f284_geometry(ox,oy)){++f284_clipped;if(d->token)f284_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !f284_scope()||sheet!=enemy[slot].sprite2s||!f284_shape(slot,0)||base!=121||!f284_colors()||!f284_ready()){
  if(d->token||f284_frame.contributed)f284_fail(9);
  return false;
 }
 if(k==0){if(d->token||f284_frame.pending){f284_fail(10);return false;}}
 else if(!f284_frame.pending||f284_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||f284_frame.pending)f284_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||f284_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++f284_contract_faults;f284_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++f284_contract_faults;f284_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(Fork284Draw){.frame=fc_frame,.epoch=f284_life.epoch,.token=f284_slots[slot].birth.token,
   .generation=f284_slots[slot].generation,.slot=slot,.event=f284_slots[slot].birth.event,.record=284,
   .base=121,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  f284_frame.pending=true;f284_frame.slot=slot;
 }
 d->part_order[k]=(unsigned)part;
 f284_frame.part=k;f284_frame.pixels=0;f284_frame.active=true;f284_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool f284_retire(unsigned off,int style)
{
 bool owned=off<64000&&f284_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++f284_blend_retirements;else ++f284_normal_retirements;
 f284_owned[off]=f284_shadows[off]=0;}
 return owned;
}
static bool f284_pixel(unsigned x,unsigned y,int style)
{
 if(!f284_frame.active){if(f284_frame.pending){f284_fail(14);return true;}return false;}
 Fork284Draw *d=f284_frame.draw+f284_frame.slot-50;
 unsigned k=f284_frame.part;
 if(k>=4||f284_frame.pixels>=f284_counts[k]){++f284_contract_faults;f284_fail(15);return true;}
 const Fork284Write *w=f284_native[k]+f284_frame.pixels;
 unsigned lx=f284_px[k]+w->x,ly=f284_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++f284_contract_faults;f284_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&f284_resources.member;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 f284_owned[off]=(uint8_t)(f284_frame.slot+1);f284_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=270){f284_fail(17);return true;}
 f284_frame.writes[f284_frame.slot-50][d->callback_count++]=(Fork284Write){(uint8_t)lx,(uint8_t)ly,w->index};
 ++f284_frame.pixels;d->part_count[k]=f284_frame.pixels;return true;
}
static void f284_shadow(unsigned off)
{
 if(off<64000&&f284_owned[off]){if(f284_shadows[off]<255)++f284_shadows[off];++f284_shadow_writes;}
}
static void f284_end(void)
{
 if(!f284_frame.active)return;
 unsigned k=f284_frame.part;Fork284Draw *d=f284_frame.draw+f284_frame.slot-50;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||f284_frame.pixels!=f284_counts[k]||!b313_family_writer_draw_ready(fc_frame)){
 ++f284_contract_faults;f284_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;f284_frame.active=false;
 if(k==3){d->complete=d->mask==15&&d->callback_count==270;f284_frame.pending=false;if(!d->complete)f284_fail(19);}
}
static void f284_accept(void){f284_frame.accepted=fc.ready&&!fc.frame_failed&&f284_finish();}
Fork284FamilyStatus render_mirror_fork284_family_status(void)
{
 Fork284FamilyStatus s={0};s.requested=f284_enabled();s.loaded=f284_life.loaded;s.contributed=f284_frame.contributed;
 s.failed=fc.frame_failed||f284_frame.fault;s.accepted=f284_frame.accepted;s.frame=fc_frame;
 s.active=f284_frame.active;s.pending=f284_frame.pending;s.active_slot=f284_frame.slot;
 s.active_part=f284_frame.part<4?f284_parts[f284_frame.part]:UINT_MAX;s.consumed_events=f284_life.consumed;
 s.blend_retirements=f284_blend_retirements;s.normal_retirements=f284_normal_retirements;s.shadow_writes=f284_shadow_writes;
 s.clipped=f284_clipped;s.unwitnessed=f284_unwitnessed;s.lifetime_losses=f284_lifetime_losses;s.bank_losses=f284_bank_losses;
 s.contract_faults=f284_contract_faults;s.first_reason=f284_first_reason;
 for(unsigned i=0;i<25;i++)s.births[i]=f284_slots[i+50].birth;
 memcpy(s.draw,f284_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=f284_owned[i]!=0;s.shadowed_cells+=f284_owned[i]&&f284_shadows[i];}return s;
}
bool render_mirror_fork284_pre_draw(Fork284Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!f284_frame.active||f284_frame.part||f284_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=f284_frame.draw[f284_frame.slot-50];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_fork284_pre_part(Fork284Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!f284_frame.active||f284_frame.pixels||
 f284_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=f284_frame.draw[f284_frame.slot-50];unsigned k=f284_frame.part;*part=f284_parts[k];
 unsigned x=(unsigned)d->x+f284_px[k],y=(unsigned)d->y+f284_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_fork284_callbacks(unsigned slot,Fork284Write *out,size_t capacity)
{
 if(slot<50||slot>=75||!out||capacity<f284_frame.draw[slot-50].callback_count)return 0;
 unsigned n=f284_frame.draw[slot-50].callback_count;memcpy(out,f284_frame.writes[slot-50],n*sizeof *out);return n;
}
bool render_mirror_fork284_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!f284_frame.accepted||fc.frame_active||fc.frame_failed||
 !f284_frame.contributed||!f284_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,f284_owned,64000);memcpy(shadows,f284_shadows,64000);return true;
}
