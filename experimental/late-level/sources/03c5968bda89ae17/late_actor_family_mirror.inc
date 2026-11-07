/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private ordinary E1 physical2 normal records282/283/285, exact12 original events.
 * Default OFF: LATE_ACTORS_ENABLE=1 and LATE_ACTORS_ASSET_DIR. This sparse material
 * cannot grant a display lease. Never writes gameplay, events, RNG or palette.
 */
#include "late_actor_pins.inc"

static struct {uint64_t generation,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate;uint64_t phase_tick;LateActorBirth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} la_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;unsigned consumed;char root[1024];
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned event,ei,record,pool;int slot,x,y;bool bg3x1,bg3x1b;int map1,map3;} call;
} la_life;
static struct {bool checked,valid;char root[1024];Asset member[7];} la_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,part,pixels,image;
 LateActorDraw draw[100];LateActorWrite writes[100][672];} la_frame;
static uint8_t la_owned[64000],la_shadows[64000];
/* Authored alpha in exactly103 pinned subpixels, never native/HD rectangular ownership. */
static uint8_t la_extra_owner[4096000],la_extra_cell[64000];
static uint64_t la_extra_retirements,la_phase_observations,la_shot_resumptions;
static bool la_extra(size_t n){return la_frame.contributed&&n<4096000&&la_extra_owner[n]!=0;}
static uint64_t la_blend_retirements,la_normal_retirements,la_shadow_writes;
static uint64_t la_clipped,la_unwitnessed,la_lifetime_losses,la_bank_losses,la_contract_faults;
static unsigned la_first_reason;
static bool la_resources_current(void);
static const char *la_root(void){const char *p=getenv("LATE_ACTORS_ASSET_DIR");return p?p:"";}
static bool la_enabled(void)
{
 const char *e=getenv("LATE_ACTORS_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool la_level_scope(void)
{
 return la_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static int la_record_index(unsigned r){return r==282?0:r==283?1:r==285?2:-1;}
static int la_event_index(unsigned e){for(unsigned i=0;i<12;i++)if(la_events[i].event==e)return (int)i;return -1;}
static int la_image(unsigned b){for(unsigned i=0;i<7;i++)if(la_images[i].base==b)return (int)i;return -1;}
static bool la_pool(unsigned slot,unsigned record){return record==282?slot>=50&&slot<75:(record==283||record==285)&&slot<25;}
static bool la_event_matches(unsigned event)
{
 int ei=la_event_index(event);
 if(!la_life.events||ei<0||maxEvent!=731)return false;
 const struct JE_EventRecType *r=la_life.events+event-1;
 return r->eventtime==la_events[ei].time&&r->eventtype==la_events[ei].type&&r->eventdat==la_events[ei].record&&
 r->eventdat2==la_events[ei].x&&r->eventdat3==la_events[ei].dy&&r->eventdat4==la_events[ei].link&&!r->eventdat5&&!r->eventdat6;
}
static bool la_events_current(void)
{
 for(unsigned e=0;e<12;e++)if(!la_event_matches(la_events[e].event))return false;
 return true;
}
static bool la_scope(void)
{
 return la_life.loaded&&!la_life.exhausted&&la_level_scope()&&terrain_file=='z'&&
 la_events_current()&&!strcmp(la_life.root,la_root());
}
static void la_fail(unsigned reason)
{
 /* Only real renderer/lifecycle failures latch resource integrity loss. */
 if(la_resources.checked&&!la_resources_current())la_resources.valid=false;
 if(!la_first_reason)la_first_reason=reason;
 la_frame.fault=true;la_frame.accepted=false;la_frame.active=false;la_frame.pending=false;
 if(la_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_late_actor_retired(unsigned slot)
{
 if(slot>=100)return;
 if(la_slots[slot].live||la_slots[slot].pending){
  ++la_lifetime_losses;
  if(la_frame.draw[slot].token)la_fail(1);
 }
 la_slots[slot].live=la_slots[slot].pending=la_slots[slot].initialized=false;
 la_slots[slot].birth.live=false;
}
static void la_reset(void)
{
 bool tracked=la_life.loaded||la_life.call.live||la_frame.contributed||la_frame.pending;
 if(la_frame.contributed||la_frame.pending)la_fail(2);
 if(tracked)for(unsigned i=0;i<100;i++)render_mirror_late_actor_retired(i);
 la_life.call.live=false;
 if(la_life.epoch==UINT64_MAX)la_life.exhausted=true;else ++la_life.epoch;
 /* Only real level begin clears consumed event origins. */
}
void render_mirror_late_actor_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 la_reset();la_life.loaded=false;la_life.events=events;la_life.consumed=0;
 if(!la_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!la_events_current()||
 !la_root()[0]||strlen(la_root())>=sizeof la_life.root){la_life.events=NULL;return;}
 for(unsigned i=0;i<100;i++)memset(&la_slots[i].birth,0,sizeof la_slots[i].birth);
 strcpy(la_life.root,la_root());la_life.loaded=true;
}
static int la_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool la_source(Sprite2_array *bank,unsigned record)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=42012)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank==enemySpriteSheets+i)bound=true;
 return bound&&asteroid1_stamp(bank->data,bank->size)==UINT64_C(0x913975450e0fc00d)&&
 la_record_index(record)>=0&&asteroid1_record_stamp(record)==la_records[la_record_index(record)].stamp;
}
static bool la_colors(void)
{
 for(unsigned i=0;i<COUNTOF(la_palette);i++)if((rgb_palette[la_palette[i].index]&0xffffffu)!=la_palette[i].rgb)return false;
 return true;
}
/* stage0: live, stage1: exact initialized constructor, stage2: event commit.
 * Positions and idle countdowns are birth-only. Finish uses saved draw origin. */
static bool la_shape(unsigned slot,unsigned stage)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;unsigned r=e->enemytype;int ri=la_record_index(r);bool firing=r!=283;
 if(ri<0||!la_pool(slot,r)||e->enemydatofs!=enemyDat+r||!la_source(e->sprite2s,r)||
 e->size!=1||e->filter||e->ani!=la_records[ri].ani||e->animin!=1||e->animax!=(firing?e->ani:0)||e->aniwhenfire!=(firing?2:0)||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->enemydie||
 e->exc||e->eyc!=(r==282&&stage!=1?4:2)||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||!e->enemyground||e->explonum!=3||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]!=(i?0:la_records[ri].tur)||e->freq[i]!=(i?0:la_records[ri].freq))return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=la_records[ri].sequence[i])return false;
 if(stage&&(e->mapoffset||e->iced||e->launchwait||e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||
 e->exccadd!=-1||e->eyccadd!=-1||e->exca!=-1||e->eyca!=-1||
 e->xminbounce!=-10000||e->xmaxbounce!=10000||e->yminbounce!=-10000||e->ymaxbounce!=10000))return false;
 if(stage)for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=(i?255:20))return false;
 if(stage==1&&(e->ey!=-12||e->ex<6||e->ex>255||e->linknum))return false;
 if(stage==2&&e->linknum!=la_events[la_life.call.ei].link)return false;
 if(!stage&&e->linknum!=la_slots[slot].birth.link)return false;
 if(stage)return e->enemycycle==1&&e->aniactive==(firing?2:0);
 return firing?((e->aniactive==2&&(e->enemycycle==1||e->enemycycle==e->ani))||
  (e->aniactive==1&&e->enemycycle>=1&&e->enemycycle<=e->ani)):(e->enemycycle==1&&!e->aniactive);
}
uint64_t render_mirror_late_actor_event_begin(unsigned event,unsigned typeofs,unsigned pool,int unique)
{
 if(la_life.call.live){la_life.call.live=false;la_fail(3);return 0;}
 int ei=la_event_index(event);
 if(!la_scope()||ei<0||event!=eventLoc||typeofs||pool!=la_events[ei].pool||unique||!la_event_matches(event)||
 curLoc!=la_events[ei].time)return 0;
 unsigned bit=1u<<ei;
 if(la_life.consumed&bit)return 0;
 la_life.consumed|=bit;
 if(la_life.serial==UINT64_MAX){la_life.exhausted=true;return 0;}
 la_life.call.live=true;la_life.call.token=++la_life.serial;la_life.call.epoch=la_life.epoch;
 la_life.call.event=event;la_life.call.ei=(unsigned)ei;la_life.call.record=la_events[ei].record;la_life.call.pool=pool;
 la_life.call.slot=-1;la_life.call.generation=0;
 la_life.call.bg3x1=background3x1;la_life.call.bg3x1b=background3x1b;
 la_life.call.map1=mapX;la_life.call.map3=mapX3;
 la_life.call.x=pool==0?la_events[ei].x-(mapX-1)*24:
  background3x1?la_events[ei].x-(mapX-1)*24-12:la_events[ei].x-mapX3*24-24*2+6;
 if(pool==50&&background3x1b)la_life.call.x-=6;
 la_life.call.y=-28+(pool==50&&background3x1b?4:0);
 return la_life.call.token;
}
void render_mirror_late_actor_enemy_allocated(void *p,unsigned record,int unique)
{
 if(!la_life.loaded)return;
 int s=la_slot(p);if(s<0)return;
 render_mirror_late_actor_retired((unsigned)s);
 if(la_slots[s].generation==UINT64_MAX){la_slots[s].exhausted=true;return;}
 if(la_slots[s].exhausted)return;
 ++la_slots[s].generation; /* All allocations, including unrelated records. */
 if(la_life.call.live&&la_scope()&&la_pool((unsigned)s,record)&&enemyAvail[s]==1&&!unique&&record==la_life.call.record&&la_life.call.slot==-1){
  la_slots[s].pending=true;la_slots[s].record=record;la_life.call.slot=s;la_life.call.generation=la_slots[s].generation;
 }
}
void render_mirror_late_actor_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 if(!la_life.loaded)return;
 int s=la_slot(p);if(s<0)return;
 la_slots[s].initialized=la_slots[s].pending&&la_life.call.live&&la_scope()&&
 la_life.call.slot==s&&la_life.call.generation==la_slots[s].generation&&
 record==la_life.call.record&&avail==0&&enemyAvail[s]==1&&la_shape((unsigned)s,1);
}
void render_mirror_late_actor_event_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=la_life.call.slot;
 bool ok=la_life.call.live&&token==la_life.call.token&&la_life.call.epoch==la_life.epoch&&la_scope()&&
 s>=0&&s<100&&la_pool((unsigned)s,la_life.call.record)&&one_based==(unsigned)s+1&&eventLoc==la_life.call.event&&
 curLoc==la_events[la_life.call.ei].time&&background3x1==la_life.call.bg3x1&&
 background3x1b==la_life.call.bg3x1b&&mapX==la_life.call.map1&&mapX3==la_life.call.map3;
 if(ok)ok=la_slots[s].pending&&la_slots[s].initialized&&la_life.call.generation==la_slots[s].generation&&
 enemyAvail[s]==0&&la_shape((unsigned)s,2)&&enemy[s].ex==la_life.call.x&&enemy[s].ey==la_life.call.y;
 if(s>=0&&s<100){
  la_slots[s].live=ok;la_slots[s].pending=la_slots[s].initialized=false;
  if(ok){la_slots[s].cycle=1;la_slots[s].gate=la_slots[s].record==283?0:2;la_slots[s].phase_tick=0;la_slots[s].witness=la_slots[s].generation;la_slots[s].bank=enemy[s].sprite2s;
   la_slots[s].data=enemy[s].sprite2s->data;la_slots[s].bytes=enemy[s].sprite2s->size;
   la_slots[s].birth=(LateActorBirth){.epoch=la_life.epoch,.token=token,.generation=la_slots[s].generation,
    .slot=(unsigned)s,.event=la_life.call.event,.record=la_slots[s].record,.link=enemy[s].linknum,.cycle=1,.gate=la_slots[s].gate,.bank_role=8,.bank_bytes=42012,
    .bank_stamp=UINT64_C(0x913975450e0fc00d),.record_stamp=la_records[la_record_index(la_slots[s].record)].stamp,
    .bank_object=(uintptr_t)la_slots[s].bank,.bank_data=(uintptr_t)la_slots[s].data,
    .event_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 la_life.call.live=false;
}
void render_mirror_late_actor_bank_changed(Sprite2_array *bank)
{
 if(!la_life.loaded&&!la_life.call.live)return;
 for(unsigned i=0;i<100;i++)if(la_slots[i].live&&la_slots[i].bank==bank){++la_bank_losses;render_mirror_late_actor_retired(i);}
 if(la_life.call.live){la_life.call.live=false;la_fail(4);}
}
static bool la_witness(unsigned s)
{
 return s<100&&la_pool(s,la_slots[s].record)&&la_slots[s].live&&!la_slots[s].exhausted&&
 la_slots[s].birth.epoch==la_life.epoch&&la_event_matches(la_slots[s].birth.event)&&
 la_slots[s].generation==la_slots[s].witness&&enemyAvail[s]==0&&enemy[s].enemytype==la_slots[s].record&&enemy[s].sprite2s&&
 la_slots[s].bank==enemy[s].sprite2s&&la_slots[s].data==enemy[s].sprite2s->data&&la_slots[s].bytes==enemy[s].sprite2s->size;
}
void render_mirror_late_actor_enemy_animated(unsigned slot)
{
 if(slot>=100||!la_slots[slot].live)return;
 if(!la_scope()||!la_witness(slot)||!la_shape(slot,0)||la_slots[slot].phase_tick==fc_frame){render_mirror_late_actor_retired(slot);return;}
 unsigned cycle=la_slots[slot].cycle,gate=la_slots[slot].gate,ani=la_records[la_record_index(la_slots[slot].record)].ani;
 if(gate==1){++cycle;if(cycle==ani)gate=2;else if(cycle>ani)cycle=1;}
 if(enemy[slot].enemycycle!=cycle||enemy[slot].aniactive!=gate){render_mirror_late_actor_retired(slot);return;}
 la_slots[slot].cycle=cycle;la_slots[slot].gate=gate;la_slots[slot].phase_tick=fc_frame;
 LateActorBirth *b=&la_slots[slot].birth;b->cycle=cycle;b->gate=gate;b->phase_tick=fc_frame;
 ++b->phase_observations;++la_phase_observations;
}
void render_mirror_late_actor_shot_fired(unsigned slot,unsigned weapon,unsigned turret,unsigned shot_slot)
{
 if(slot>=100||!la_slots[slot].live||la_slots[slot].record==283)return;
 unsigned r=la_slots[slot].record,ani=la_records[la_record_index(r)].ani;
 if(!la_scope()||!la_witness(slot)||!la_shape(slot,0)||turret!=1||
 !((r==282&&weapon==59)||(r==285&&weapon==24))||shot_slot>=ENEMY_SHOT_MAX||enemyShotAvail[shot_slot]!=0||
 la_slots[slot].phase_tick!=fc_frame||la_slots[slot].gate!=2||
 (la_slots[slot].cycle!=1&&la_slots[slot].cycle!=ani)||enemy[slot].enemycycle!=la_slots[slot].cycle||enemy[slot].aniactive!=1){
 render_mirror_late_actor_retired(slot);return;}
 la_slots[slot].gate=1;la_slots[slot].birth.gate=1;++la_slots[slot].birth.shot_count;++la_shot_resumptions;
 LateActorDraw *d=la_frame.draw+slot;
 if(d->token&&d->generation==la_slots[slot].generation&&d->cycle==enemy[slot].enemycycle&&d->draw_gate==2)d->shot_resumed=true;
}
/* Birth-only interface for the independently gated shot family. No art/load/draw
 * prerequisite; successful own-shot lifetimes do not depend on later parent life. */
static bool late_actor_emitter(unsigned slot,unsigned weapon,uint64_t *token,unsigned *event)
{
 if(!token||!event||!la_scope()||!la_witness(slot)||!la_shape(slot,0))return false;
 unsigned r=la_slots[slot].record;
 if(!((r==282&&weapon==59)||(r==285&&weapon==24))||la_slots[slot].phase_tick!=fc_frame||
 la_slots[slot].cycle!=enemy[slot].enemycycle||la_slots[slot].gate!=enemy[slot].aniactive)return false;
 *token=la_slots[slot].birth.token;*event=la_slots[slot].birth.event;return true;
}
static void la_tick(void)
{
 /* Inactive feature: no resource access, census, array clear or slot scan. */
 if(!la_life.loaded&&!la_frame.contributed&&!la_frame.pending)return;
 if(la_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&la_frame,0,sizeof la_frame);memset(la_owned,0,sizeof la_owned);memset(la_shadows,0,sizeof la_shadows);
 memset(la_extra_owner,0,sizeof la_extra_owner);memset(la_extra_cell,0,sizeof la_extra_cell);la_first_reason=0;
 if(la_life.loaded&&!la_scope()){la_reset();la_life.loaded=false;return;}
 for(unsigned i=0;i<100;i++)if(la_slots[i].live&&(!la_witness(i)||!la_shape(i,0)))render_mirror_late_actor_retired(i);
}
static bool la_load(unsigned image)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-%u-8.hda",la_resources.root,la_images[image].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==la_images[image].id&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==la_images[image].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 la_resources.member[image]=(Asset){true,true,ASSET_ASTEROID1,la_images[image].base,24,28,0,0,8,rgba};return true;
}
static bool la_resources_current(void)
{
 if(!la_resources.checked||!la_resources.valid||strcmp(la_resources.root,la_root()))return false;
 for(unsigned image=0;image<7;image++){
 const Asset *a=la_resources.member+image;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=la_images[image].base||a->w!=24||a->h!=28||
 a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,172032)!=la_images[image].rgba)return false;
 }
 return true;
}
static bool la_ready(void)
{
 if(!la_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!la_resources.checked){la_resources.checked=true;strcpy(la_resources.root,la_life.root);la_resources.valid=true;for(unsigned i=0;i<7;i++)if(!la_load(i))la_resources.valid=false;}
 if(!la_resources_current()){la_resources.valid=false;return false;}
 return true;
}
static void la_shutdown(void)
{
 la_reset();la_life.loaded=false;for(unsigned i=0;i<7;i++)free(la_resources.member[i].rgba);memset(&la_resources,0,sizeof la_resources);
}
static bool la_dependencies(bool partial)
{
 if(!la_frame.contributed)return true;
 if(la_frame.fault||!la_scope()||!la_colors()||!la_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<100;i++)if(la_frame.draw[i].token){const LateActorDraw *d=la_frame.draw+i;unsigned s=i;
  if(!la_witness(s)||!la_shape(s,0)||d->generation!=la_slots[s].generation||
  d->token!=la_slots[s].birth.token||d->epoch!=la_life.epoch||d->event!=la_slots[s].birth.event||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||d->record!=la_slots[s].record||la_image(d->base)<0||
  d->cycle!=enemy[s].enemycycle||d->base!=enemy[s].egr[d->cycle-1]||
  !(enemy[s].aniactive==d->draw_gate||(d->draw_gate==2&&enemy[s].aniactive==1&&d->shot_resumed)))return false;
  if(!d->complete){if(!partial||!la_frame.pending||la_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=la_totals[la_image(d->base)]||(!partial&&d->extra_stores!=la_images[la_image(d->base)].extra))return false;
 }
 return partial||(!la_frame.active&&!la_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool la_finish(void){return la_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool la_guard(void)
{
 if(la_finish())return true;
 la_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool la_before_tile(unsigned slot,int part)
{
 if(la_frame.contributed&&!la_dependencies(true)){la_fail(5);return false;}
 if(la_frame.pending&&(la_frame.active||slot!=la_frame.slot||
 la_frame.draw[slot].next>=4||part!=(int)la_parts[la_frame.draw[slot].next])){la_fail(6);return false;}
 return true;
}
static bool la_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool la_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!la_life.loaded||slot>=100||la_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!la_witness(slot)){++la_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)la_parts[k];k++);
 if(k==4){if(la_frame.contributed)la_fail(7);return false;}
 int64_t ox=(int64_t)x-la_px[k],oy=(int64_t)y-la_py[k];
 LateActorDraw *d=la_frame.draw+slot;
 if(!la_geometry(ox,oy)){++la_clipped;if(d->token)la_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !la_scope()||sheet!=enemy[slot].sprite2s||!la_shape(slot,0)||la_slots[slot].phase_tick!=fc_frame||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||la_image(base)<0||!la_colors()||!la_ready()){
  if(d->token||la_frame.contributed)la_fail(9);
  return false;
 }
 if(k==0){if(d->token||la_frame.pending){la_fail(10);return false;}}
 else if(!la_frame.pending||la_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||la_frame.pending)la_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||la_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++la_contract_faults;la_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++la_contract_faults;la_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(LateActorDraw){.frame=fc_frame,.epoch=la_life.epoch,.token=la_slots[slot].birth.token,
   .generation=la_slots[slot].generation,.slot=slot,.event=la_slots[slot].birth.event,.record=la_slots[slot].record,.cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,
   .base=base,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  la_frame.pending=true;la_frame.slot=slot;la_frame.image=(unsigned)la_image(base);
 }
 d->part_order[k]=(unsigned)part;
 la_frame.part=k;la_frame.pixels=0;la_frame.active=true;la_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool la_retire(unsigned off,int style)
{
 if(!la_frame.contributed)return false;
 bool owned=off<64000&&la_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++la_blend_retirements;else ++la_normal_retirements;
 la_owned[off]=la_shadows[off]=0;}
 if(off<64000&&style!=MIRROR_SHADOW&&la_extra_cell[off]){
  unsigned x=off%320,y=off/320;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   size_t n=(y*8+sy)*2560+x*8+sx;la_extra_retirements+=la_extra_owner[n]!=0;la_extra_owner[n]=0;
  }
  la_extra_cell[off]=0;
 }
 return owned;
}
static bool la_pixel(unsigned x,unsigned y,int style)
{
 if(!la_frame.active){if(la_frame.pending){la_fail(14);return true;}return false;}
 LateActorDraw *d=la_frame.draw+la_frame.slot;
 unsigned k=la_frame.part;
 if(k>=4||la_frame.pixels>=la_counts[la_frame.image][k]){++la_contract_faults;la_fail(15);return true;}
 const LateActorWrite *w=la_native[la_frame.image][k]+la_frame.pixels;
 unsigned lx=la_px[k]+w->x,ly=la_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++la_contract_faults;la_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&la_resources.member[la_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 la_owned[off]=(uint8_t)(la_frame.slot+1);la_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){la_fail(17);return true;}
 la_frame.writes[la_frame.slot][d->callback_count++]=(LateActorWrite){(uint8_t)lx,(uint8_t)ly,w->index};
 ++la_frame.pixels;d->part_count[k]=la_frame.pixels;return true;
}
static void la_shadow(unsigned off)
{
 if(off<64000&&la_owned[off]){if(la_shadows[off]<255)++la_shadows[off];++la_shadow_writes;}
}
/* Same narrow authored-support policy as firing_rock462: exact nonzero-alpha
 * native-hole subpixels only, after a complete observed native quartet. No
 * native INDEX, selected[], native owner, global permission or cached underlay. */
static void la_authored_support(LateActorDraw *d)
{
 if(d->record!=283)return;
 const Asset *a=la_resources.member+la_frame.image;
 for(unsigned i=0;i<COUNTOF(la_extra283);i++){
  unsigned ax=la_extra283[i].x,ay=la_extra283[i].y;
  const Uint8 *art=a->rgba+(ay*192+ax)*4;
  unsigned off=((unsigned)d->y+ay/8)*320+(unsigned)d->x+ax/8;
  if(la_native_mask283[(ay/8)*24+ax/8]||!art[3]||expected[off]!=((const Uint8 *)fc_source_pixels)[off]){
   la_fail(21);family_fault(FC_ORDER);return;
  }
  size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
  Uint32 *dst=(Uint32 *)canvas->pixels+n;*dst=blend_rgba(*dst,art,art[3]);
  la_extra_owner[n]=(uint8_t)(d->slot+1);la_extra_cell[off]=1;++d->extra_stores;
 }
 if(d->extra_stores!=la_images[la_frame.image].extra){la_fail(21);family_fault(FC_ORDER);}
}
static void la_end(void)
{
 if(!la_frame.active)return;
 unsigned k=la_frame.part;LateActorDraw *d=la_frame.draw+la_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||la_frame.pixels!=la_counts[la_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++la_contract_faults;la_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;la_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==la_totals[la_frame.image];la_frame.pending=false;
  if(!d->complete){la_fail(19);return;}
  if(!la_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   la_fail(22);family_fault(FC_SOURCE);return;
  }
  la_authored_support(d);
 }
}
static void la_accept(void){la_frame.accepted=fc.ready&&!fc.frame_failed&&la_finish();}
LateActorFamilyStatus render_mirror_late_actor_family_status(void)
{
 LateActorFamilyStatus s={0};s.requested=la_enabled();s.loaded=la_life.loaded;s.contributed=la_frame.contributed;
 s.failed=fc.frame_failed||la_frame.fault;s.accepted=la_frame.accepted;s.frame=fc_frame;
 s.active=la_frame.active;s.pending=la_frame.pending;s.active_slot=la_frame.slot;
 s.active_part=la_frame.part<4?la_parts[la_frame.part]:UINT_MAX;s.consumed_events=la_life.consumed;
 s.blend_retirements=la_blend_retirements;s.normal_retirements=la_normal_retirements;s.shadow_writes=la_shadow_writes;
 s.clipped=la_clipped;s.unwitnessed=la_unwitnessed;s.lifetime_losses=la_lifetime_losses;s.bank_losses=la_bank_losses;
 s.contract_faults=la_contract_faults;s.first_reason=la_first_reason;
 s.phase_observations=la_phase_observations;s.shot_resumptions=la_shot_resumptions;s.extra_retirements=la_extra_retirements;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=la_extra_owner[i]!=0;
 for(unsigned i=0;i<100;i++)s.births[i]=la_slots[i].birth;
 memcpy(s.draw,la_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=la_owned[i]!=0;s.shadowed_cells+=la_owned[i]&&la_shadows[i];}return s;
}
bool render_mirror_late_actor_pre_draw(LateActorDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!la_frame.active||la_frame.part||la_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=la_frame.draw[la_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_late_actor_pre_part(LateActorDraw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!la_frame.active||la_frame.pixels||
 la_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=la_frame.draw[la_frame.slot];unsigned k=la_frame.part;*part=la_parts[k];
 unsigned x=(unsigned)d->x+la_px[k],y=(unsigned)d->y+la_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_late_actor_callbacks(unsigned slot,LateActorWrite *out,size_t capacity)
{
 if(slot>=100||!out||capacity<la_frame.draw[slot].callback_count)return 0;
 unsigned n=la_frame.draw[slot].callback_count;memcpy(out,la_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_late_actor_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!la_frame.accepted||fc.frame_active||fc.frame_failed||
 !la_frame.contributed||!la_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,la_owned,64000);memcpy(shadows,la_shadows,64000);return true;
}
bool render_mirror_late_actor_extra_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=4096000||!la_frame.accepted||fc.frame_active||fc.frame_failed||
 !la_frame.contributed||!la_finish()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
 !b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(out,la_extra_owner,bytes);return true;
}
