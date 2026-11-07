/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private ordinary E1 physical2 twelve tall-structure bodies, six original events.
 * Default OFF: TALL_STRUCTURES_ENABLE=1 and TALL_STRUCTURES_ASSET_DIR. This sparse material
 * cannot grant a display lease. Never writes gameplay, events, RNG or palette.
 */
#include "tall_structure_pins.inc"

static struct {uint64_t generation,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate;uint64_t phase_tick;TallStructureBirth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} ts_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;unsigned consumed;char root[1024];
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned event,ei,record,pool,component;int slot,x,y,map1;} call;
} ts_life;
static struct {bool checked,valid;char root[1024];Asset member[12];} ts_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,part,pixels,image;
 TallStructureDraw draw[100];TallStructureWrite writes[100][672];} ts_frame;
static uint8_t ts_owned[64000],ts_shadows[64000];
/* Complete authored nonzero-alpha native-hole subpixels; never rectangular ownership. */
static uint8_t ts_extra_owner[4096000],ts_extra_cell[64000];
static uint64_t ts_extra_retirements,ts_phase_observations,ts_shot_resumptions;
static bool ts_extra(size_t n){return ts_frame.contributed&&n<4096000&&ts_extra_owner[n]!=0;}
static uint64_t ts_blend_retirements,ts_normal_retirements,ts_shadow_writes;
static uint64_t ts_clipped,ts_unwitnessed,ts_lifetime_losses,ts_bank_losses,ts_contract_faults;
static unsigned ts_first_reason;
static bool ts_resources_current(void);
static const char *ts_root(void){const char *p=getenv("TALL_STRUCTURES_ASSET_DIR");return p?p:"";}
static bool ts_enabled(void)
{
 const char *e=getenv("TALL_STRUCTURES_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool ts_level_scope(void)
{
 return ts_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static int ts_record_index(unsigned r){for(unsigned i=0;i<12;i++)if(ts_records[i].record==r)return (int)i;return -1;}
static int ts_event_index(unsigned e){for(unsigned i=0;i<6;i++)if(ts_events[i].event==e)return (int)i;return -1;}
static int ts_image(unsigned b){for(unsigned i=0;i<12;i++)if(ts_images[i].base==b)return (int)i;return -1;}
static bool ts_pool(unsigned slot,unsigned record){return slot>=25&&slot<50&&ts_record_index(record)>=0;}
static bool ts_event_matches(unsigned event)
{
 int ei=ts_event_index(event);
 if(!ts_life.events||ts_life.events!=eventRec||ei<0||maxEvent!=731)return false;
 const struct JE_EventRecType *r=ts_life.events+event-1;
 return r->eventtime==ts_events[ei].time&&r->eventtype==ts_events[ei].type&&r->eventdat==ts_events[ei].record&&
 r->eventdat2==ts_events[ei].x&&r->eventdat3==ts_events[ei].dy&&r->eventdat4==ts_events[ei].link&&r->eventdat5==ts_events[ei].y&&!r->eventdat6;
}
static bool ts_events_current(void)
{
 for(unsigned e=0;e<6;e++)if(!ts_event_matches(ts_events[e].event))return false;
 return true;
}
/* Only original tail rows, with changes admitted through actual native
 * before/after event callbacks. No RNG reads, replay or gameplay writes. */
static struct {bool active,failed;unsigned event,next;struct JE_EventRecType expected[119];} ts_script;
static bool ts_row_equal(const struct JE_EventRecType *a,const struct JE_EventRecType *b)
{
 return a->eventtime==b->eventtime&&a->eventtype==b->eventtype&&a->eventdat==b->eventdat&&
 a->eventdat2==b->eventdat2&&a->eventdat3==b->eventdat3&&a->eventdat4==b->eventdat4&&
 a->eventdat5==b->eventdat5&&a->eventdat6==b->eventdat6;
}
static bool ts_tail_current(void)
{
 if(ts_script.failed||ts_life.events!=eventRec||maxEvent!=731)return false;
 for(unsigned i=612;i<731;i++)if(!ts_row_equal(eventRec+i,ts_script.expected+i-612))return false;
 return true;
}
static bool ts_scope(void)
{
 return ts_life.loaded&&!ts_life.exhausted&&ts_level_scope()&&terrain_file=='z'&&
 ts_events_current()&&ts_tail_current()&&!strcmp(ts_life.root,ts_root());
}
static void ts_fail(unsigned reason)
{
 /* Only real renderer/lifecycle failures latch resource integrity loss. */
 if(ts_resources.checked&&!ts_resources_current())ts_resources.valid=false;
 if(!ts_first_reason)ts_first_reason=reason;
 ts_frame.fault=true;ts_frame.accepted=false;ts_frame.active=false;ts_frame.pending=false;
 if(ts_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_tall_structure_retired(unsigned slot)
{
 if(slot>=100)return;
 if(ts_slots[slot].live||ts_slots[slot].pending){
  ++ts_lifetime_losses;
  if(ts_frame.draw[slot].token)ts_fail(1);
 }
 ts_slots[slot].live=ts_slots[slot].pending=ts_slots[slot].initialized=false;
 ts_slots[slot].birth.live=false;
}
static void ts_reset(void)
{
 bool tracked=ts_life.loaded||ts_life.call.live||ts_frame.contributed||ts_frame.pending;
 if(ts_frame.contributed||ts_frame.pending)ts_fail(2);
 if(tracked)for(unsigned i=0;i<100;i++)render_mirror_tall_structure_retired(i);
 ts_life.call.live=false;
 if(ts_life.epoch==UINT64_MAX)ts_life.exhausted=true;else ++ts_life.epoch;
 /* Only real level begin clears consumed event origins. */
}
void render_mirror_tall_structure_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 ts_reset();ts_life.loaded=false;ts_life.events=events;ts_life.consumed=0;
 if(!ts_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!ts_events_current()||!late_reuse_stream_matches(events)||
 !ts_root()[0]||strlen(ts_root())>=sizeof ts_life.root){ts_life.events=NULL;return;}
 for(unsigned i=0;i<100;i++)memset(&ts_slots[i].birth,0,sizeof ts_slots[i].birth);
 strcpy(ts_life.root,ts_root());ts_life.loaded=true;
 memset(&ts_script,0,sizeof ts_script);ts_script.next=613;
 memcpy(ts_script.expected,events+612,sizeof ts_script.expected);
}
static void ts_script_before(unsigned event)
{
 if(!ts_life.loaded||event<613)return;
 if(ts_script.active||ts_script.failed||event!=ts_script.next||event>731||event!=eventLoc||
 !ts_scope()||curLoc<eventRec[event-1].eventtime){ts_script.failed=true;ts_fail(23);return;}
 ts_script.active=true;ts_script.event=event;
}
static void ts_script_after(unsigned event)
{
 if(!ts_life.loaded||event<613)return;
 if(!ts_script.active||ts_script.failed||event!=ts_script.event||event!=eventLoc||event>731){
  ts_script.failed=true;ts_fail(24);return;
 }
 struct JE_EventRecType next=ts_script.expected[event-613];
 const struct JE_EventRecType *actual=eventRec+event-1;
 /* Exact unrelated case33 random drop is observed, never predicted. */
 if(event==633&&next.eventtype==33&&next.eventdat==533&&
 (actual->eventdat==533||(actual->eventdat>=829&&actual->eventdat<=834)))next.eventdat=actual->eventdat;
 /* These original case12 rows select a pool, then zero only dat6. */
 if(next.eventtype==12)next.eventdat6=0;
 if(!ts_row_equal(&next,actual)){ts_script.failed=true;ts_fail(25);return;}
 ts_script.expected[event-613]=next;ts_script.active=false;ts_script.next=event+1;
 if(!ts_tail_current()){ts_script.failed=true;ts_fail(26);}
}
static int ts_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool ts_source(Sprite2_array *bank,unsigned record)
{
 int ri=ts_record_index(record);
 if(ri<0||!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==ts_records[ri].bank&&bank==enemySpriteSheets+i)bound=true;
 return bound&&bank->size==ts_records[ri].bytes&&asteroid1_stamp(bank->data,bank->size)==ts_records[ri].bank_stamp&&
 asteroid1_record_stamp(record)==ts_records[ri].stamp;
}
static bool ts_colors(void)
{
 for(unsigned i=0;i<COUNTOF(ts_palette);i++)if((rgb_palette[ts_palette[i].index]&0xffffffu)!=ts_palette[i].rgb)return false;
 return true;
}
/* stage0: live, stage1: exact initialized constructor, stage2: event commit.
 * Positions and idle countdowns are birth-only. Finish uses saved draw origin. */
static bool ts_shape(unsigned slot,unsigned stage)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;unsigned r=e->enemytype;int ri=ts_record_index(r);
 if(ri<0||!ts_pool(slot,r)||e->enemydatofs!=enemyDat+r||!ts_source(e->sprite2s,r)||
 e->size!=1||e->filter||e->ani!=1||e->animin!=1||e->animax||e->aniwhenfire||e->enemycycle!=1||e->aniactive||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->enemydie||
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=12||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr!=ts_records[ri].dgr||
 e->edlevel!=ts_records[ri].dlevel||e->edani!=ts_records[ri].dani)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]||e->freq[i])return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=ts_records[ri].sequence[i])return false;
 if(e->iced||e->launchwait||e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||
 e->exccadd!=-1||e->eyccadd!=-1||e->exca!=-1||e->eyca!=-1||
 e->xminbounce!=-10000||e->xmaxbounce!=10000||e->yminbounce!=-10000||e->ymaxbounce!=10000)return false;
 if(stage)for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=255)return false;
 if(stage==1&&(e->mapoffset||e->ey!=-12||e->ex<6||e->ex>255||e->linknum))return false;
 if(stage==2&&e->linknum!=ts_events[ts_life.call.ei].link)return false;
 if(!stage&&e->linknum!=ts_slots[slot].birth.link)return false;
 return true;
}
static uint64_t ts_event_begin(unsigned event,unsigned typeofs,unsigned pool,int unique)
{
 if(ts_life.call.live){ts_life.call.live=false;ts_fail(3);return 0;}
 int ei=ts_event_index(event);
 if(!ts_scope()||ei<0||event!=eventLoc||pool!=25||unique||!ts_event_matches(event)||
 curLoc!=6264||(ei<4?typeofs!=0:typeofs>3))return 0;
 unsigned origin=ei<4?(unsigned)ei:4+((unsigned)ei-4)*4+typeofs;
 unsigned bit=1u<<origin;
 if(ts_life.consumed&bit)return 0;
 ts_life.consumed|=bit; /* A failed original allocation still consumes the source. */
 if(ts_life.serial==UINT64_MAX){ts_life.exhausted=true;return 0;}
 ts_life.call.live=true;ts_life.call.token=++ts_life.serial;ts_life.call.epoch=ts_life.epoch;
 ts_life.call.event=event;ts_life.call.ei=(unsigned)ei;ts_life.call.record=ts_events[ei].record+typeofs;
 ts_life.call.pool=pool;ts_life.call.component=typeofs;ts_life.call.slot=-1;ts_life.call.generation=0;
 ts_life.call.map1=mapX;
 ts_life.call.x=ts_events[ei].x-(mapX-1)*24-12+(typeofs%2?24:0);
 ts_life.call.y=-28+ts_events[ei].y-(typeofs>=2?28:0);
 return ts_life.call.token;
}
void render_mirror_tall_structure_enemy_allocated(void *p,unsigned record,int unique)
{
 if(!ts_life.loaded)return;
 int s=ts_slot(p);if(s<0)return;
 render_mirror_tall_structure_retired((unsigned)s);
 if(ts_slots[s].generation==UINT64_MAX){ts_slots[s].exhausted=true;return;}
 if(ts_slots[s].exhausted)return;
 ++ts_slots[s].generation; /* All allocations, including unrelated records. */
 if(ts_life.call.live&&ts_scope()&&ts_pool((unsigned)s,record)&&enemyAvail[s]==1&&!unique&&record==ts_life.call.record&&ts_life.call.slot==-1){
  ts_slots[s].pending=true;ts_slots[s].record=record;ts_life.call.slot=s;ts_life.call.generation=ts_slots[s].generation;
 }
}
void render_mirror_tall_structure_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 if(!ts_life.loaded)return;
 int s=ts_slot(p);if(s<0)return;
 ts_slots[s].initialized=ts_slots[s].pending&&ts_life.call.live&&ts_scope()&&
 ts_life.call.slot==s&&ts_life.call.generation==ts_slots[s].generation&&
 record==ts_life.call.record&&avail==0&&enemyAvail[s]==1&&ts_shape((unsigned)s,1);
}
void render_mirror_tall_structure_event_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=ts_life.call.slot;
 bool ok=ts_life.call.live&&token==ts_life.call.token&&ts_life.call.epoch==ts_life.epoch&&ts_scope()&&
 s>=0&&s<100&&ts_pool((unsigned)s,ts_life.call.record)&&one_based==(unsigned)s+1&&eventLoc==ts_life.call.event&&
 curLoc==6264&&mapX==ts_life.call.map1&&ts_event_matches(ts_life.call.event);
 if(ok)ok=ts_slots[s].pending&&ts_slots[s].initialized&&ts_life.call.generation==ts_slots[s].generation&&
 enemyAvail[s]==0&&enemy[s].enemytype==ts_life.call.record&&ts_shape((unsigned)s,2)&&enemy[s].ex==ts_life.call.x&&enemy[s].ey==ts_life.call.y;
 if(s>=0&&s<100){
  ts_slots[s].live=ok;ts_slots[s].pending=ts_slots[s].initialized=false;
  if(ok){ts_slots[s].cycle=1;ts_slots[s].gate=0;ts_slots[s].phase_tick=0;ts_slots[s].witness=ts_slots[s].generation;ts_slots[s].bank=enemy[s].sprite2s;
   ts_slots[s].data=enemy[s].sprite2s->data;ts_slots[s].bytes=enemy[s].sprite2s->size;
   ts_slots[s].birth=(TallStructureBirth){.epoch=ts_life.epoch,.token=token,.generation=ts_slots[s].generation,
    .slot=(unsigned)s,.event=ts_life.call.event,.record=ts_slots[s].record,.link=enemy[s].linknum,.component=ts_life.call.component,.cycle=1,.gate=0,
    .bank_role=ts_records[ts_record_index(ts_slots[s].record)].bank,.bank_bytes=ts_records[ts_record_index(ts_slots[s].record)].bytes,
    .bank_stamp=ts_records[ts_record_index(ts_slots[s].record)].bank_stamp,.record_stamp=ts_records[ts_record_index(ts_slots[s].record)].stamp,
    .bank_object=(uintptr_t)ts_slots[s].bank,.bank_data=(uintptr_t)ts_slots[s].data,
    .event_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 ts_life.call.live=false;
}
void render_mirror_tall_structure_bank_changed(Sprite2_array *bank)
{
 if(!ts_life.loaded&&!ts_life.call.live)return;
 for(unsigned i=0;i<100;i++)if(ts_slots[i].live&&ts_slots[i].bank==bank){++ts_bank_losses;render_mirror_tall_structure_retired(i);}
 if(ts_life.call.live){ts_life.call.live=false;ts_fail(4);}
}
static bool ts_witness(unsigned s)
{
 return s<100&&ts_pool(s,ts_slots[s].record)&&ts_slots[s].live&&!ts_slots[s].exhausted&&
 ts_slots[s].birth.epoch==ts_life.epoch&&ts_event_matches(ts_slots[s].birth.event)&&
 ts_slots[s].generation==ts_slots[s].witness&&enemyAvail[s]==0&&enemy[s].enemytype==ts_slots[s].record&&enemy[s].sprite2s&&
 ts_slots[s].bank==enemy[s].sprite2s&&ts_slots[s].data==enemy[s].sprite2s->data&&ts_slots[s].bytes==enemy[s].sprite2s->size;
}
static void ts_enemy_animated(unsigned slot)
{
 if(slot>=100||!ts_slots[slot].live)return;
 if(!ts_scope()||!ts_witness(slot)||!ts_shape(slot,0)||ts_slots[slot].phase_tick==fc_frame){render_mirror_tall_structure_retired(slot);return;}
 ts_slots[slot].cycle=1;ts_slots[slot].gate=0;ts_slots[slot].phase_tick=fc_frame;
 TallStructureBirth *b=&ts_slots[slot].birth;b->cycle=1;b->gate=0;b->phase_tick=fc_frame;
 ++b->phase_observations;++ts_phase_observations;
}

/* Static normal body only: no shot or authored normal-phase interface. */

static void ts_tick(void)
{
 /* Inactive feature: no resource access, census, array clear or slot scan. */
 if(!ts_life.loaded&&!ts_frame.contributed&&!ts_frame.pending)return;
 if(ts_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 if(!ts_life.consumed&&!ts_frame.contributed&&!ts_frame.pending)return;
 memset(&ts_frame,0,sizeof ts_frame);memset(ts_owned,0,sizeof ts_owned);memset(ts_shadows,0,sizeof ts_shadows);
 memset(ts_extra_owner,0,sizeof ts_extra_owner);memset(ts_extra_cell,0,sizeof ts_extra_cell);ts_first_reason=0;
 if(ts_life.loaded&&!ts_scope()){ts_reset();ts_life.loaded=false;return;}
 for(unsigned i=0;i<100;i++)if(ts_slots[i].live&&(!ts_witness(i)||!ts_shape(i,0)))render_mirror_tall_structure_retired(i);
}
static bool ts_load(unsigned image)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-%s-%u-8.hda",ts_resources.root,ts_images[image].bank==20?"newshp":"newshs",ts_images[image].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==ts_images[image].id&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==ts_images[image].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 ts_resources.member[image]=(Asset){true,true,ASSET_ASTEROID1,ts_images[image].base,24,28,0,0,8,rgba};return true;
}
static bool ts_resources_current(void)
{
 if(!ts_resources.checked||!ts_resources.valid||strcmp(ts_resources.root,ts_root()))return false;
 for(unsigned image=0;image<12;image++){
 const Asset *a=ts_resources.member+image;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=ts_images[image].base||a->w!=24||a->h!=28||
 a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,172032)!=ts_images[image].rgba)return false;
 }
 return true;
}
static bool ts_ready(void)
{
 if(!ts_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!ts_resources.checked){ts_resources.checked=true;strcpy(ts_resources.root,ts_life.root);ts_resources.valid=true;for(unsigned i=0;i<12;i++)if(!ts_load(i))ts_resources.valid=false;}
 if(!ts_resources_current()){ts_resources.valid=false;return false;}
 return true;
}
static void ts_shutdown(void)
{
 ts_reset();ts_life.loaded=false;for(unsigned i=0;i<12;i++)free(ts_resources.member[i].rgba);memset(&ts_resources,0,sizeof ts_resources);
}
static bool ts_dependencies(bool partial)
{
 if(!ts_frame.contributed)return true;
 if(ts_frame.fault||!ts_scope()||!ts_colors()||!ts_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<100;i++)if(ts_frame.draw[i].token){const TallStructureDraw *d=ts_frame.draw+i;unsigned s=i;
  if(!ts_witness(s)||!ts_shape(s,0)||d->generation!=ts_slots[s].generation||
  d->token!=ts_slots[s].birth.token||d->epoch!=ts_life.epoch||d->event!=ts_slots[s].birth.event||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||d->record!=ts_slots[s].record||ts_image(d->base)<0||
  d->cycle!=1||enemy[s].enemycycle!=1||d->base!=enemy[s].egr[0]||d->draw_gate||enemy[s].aniactive)return false;
  if(!d->complete){if(!partial||!ts_frame.pending||ts_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=ts_totals[ts_image(d->base)]||(!partial&&d->extra_stores!=ts_images[ts_image(d->base)].extra))return false;
 }
 return partial||(!ts_frame.active&&!ts_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool ts_finish(void){return ts_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool ts_guard(void)
{
 if(ts_finish())return true;
 ts_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool ts_before_tile(unsigned slot,int part)
{
 if(ts_frame.contributed&&!ts_dependencies(true)){ts_fail(5);return false;}
 if(ts_frame.pending&&(ts_frame.active||slot!=ts_frame.slot||
 ts_frame.draw[slot].next>=4||part!=(int)ts_parts[ts_frame.draw[slot].next])){ts_fail(6);return false;}
 return true;
}
static bool ts_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool ts_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!ts_life.loaded||slot>=100||ts_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!ts_witness(slot)){++ts_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)ts_parts[k];k++);
 if(k==4){if(ts_frame.contributed)ts_fail(7);return false;}
 int64_t ox=(int64_t)x-ts_px[k],oy=(int64_t)y-ts_py[k];
 TallStructureDraw *d=ts_frame.draw+slot;
 if(!ts_geometry(ox,oy)){++ts_clipped;if(d->token)ts_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !ts_scope()||sheet!=enemy[slot].sprite2s||!ts_shape(slot,0)||ts_slots[slot].phase_tick!=fc_frame||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||ts_image(base)<0||!ts_colors()||!ts_ready()){
  if(d->token||ts_frame.contributed)ts_fail(9);
  return false;
 }
 if(k==0){if(d->token||ts_frame.pending){ts_fail(10);return false;}}
 else if(!ts_frame.pending||ts_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||ts_frame.pending)ts_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||ts_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++ts_contract_faults;ts_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++ts_contract_faults;ts_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  ts_frame.image=(unsigned)ts_record_index(enemy[slot].enemytype);
  *d=(TallStructureDraw){.frame=fc_frame,.epoch=ts_life.epoch,.token=ts_slots[slot].birth.token,
   .generation=ts_slots[slot].generation,.slot=slot,.event=ts_slots[slot].birth.event,.record=ts_slots[slot].record,.cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,
   .base=base,.cur_loc=curLoc,.bank_role=ts_images[ts_frame.image].bank,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  ts_frame.pending=true;ts_frame.slot=slot;
 }
 d->part_order[k]=(unsigned)part;
 ts_frame.part=k;ts_frame.pixels=0;ts_frame.active=true;ts_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool ts_retire(unsigned off,int style)
{
 if(!ts_frame.contributed)return false;
 bool owned=off<64000&&ts_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++ts_blend_retirements;else ++ts_normal_retirements;
 ts_owned[off]=ts_shadows[off]=0;}
 if(off<64000&&style!=MIRROR_SHADOW&&ts_extra_cell[off]){
  unsigned x=off%320,y=off/320;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   size_t n=(y*8+sy)*2560+x*8+sx;ts_extra_retirements+=ts_extra_owner[n]!=0;ts_extra_owner[n]=0;
  }
  ts_extra_cell[off]=0;
 }
 return owned;
}
static bool ts_pixel(unsigned x,unsigned y,int style)
{
 if(!ts_frame.active){if(ts_frame.pending){ts_fail(14);return true;}return false;}
 TallStructureDraw *d=ts_frame.draw+ts_frame.slot;
 unsigned k=ts_frame.part;
 if(k>=4||ts_frame.pixels>=ts_counts[ts_frame.image][k]){++ts_contract_faults;ts_fail(15);return true;}
 const TallStructureWrite *w=ts_native[ts_frame.image][k]+ts_frame.pixels;
 unsigned lx=ts_px[k]+w->x,ly=ts_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++ts_contract_faults;ts_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&ts_resources.member[ts_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here. Exact authored extras are separate. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 ts_owned[off]=(uint8_t)(ts_frame.slot+1);ts_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){ts_fail(17);return true;}
 ts_frame.writes[ts_frame.slot][d->callback_count++]=(TallStructureWrite){(uint8_t)lx,(uint8_t)ly,w->index};
 ++ts_frame.pixels;d->part_count[k]=ts_frame.pixels;return true;
}
static void ts_shadow(unsigned off)
{
 if(off<64000&&ts_owned[off]){if(ts_shadows[off]<255)++ts_shadows[off];++ts_shadow_writes;}
}
/* Same narrow authored-support policy as firing_rock462: exact nonzero-alpha
 * native-hole subpixels only, after a complete observed native quartet. No
 * native INDEX, selected[], native owner, global permission or cached underlay. */
static void ts_authored_support(TallStructureDraw *d)
{
 
 const Asset *a=ts_resources.member+ts_frame.image;
 for(unsigned i=0;i<ts_images[ts_frame.image].extra;i++){
  unsigned ax=ts_extras[ts_frame.image][i].x,ay=ts_extras[ts_frame.image][i].y;
  const Uint8 *art=a->rgba+(ay*192+ax)*4;
  unsigned off=((unsigned)d->y+ay/8)*320+(unsigned)d->x+ax/8;
  if(ts_native_mask[ts_frame.image][(ay/8)*24+ax/8]||!art[3]||expected[off]!=((const Uint8 *)fc_source_pixels)[off]){
   ts_fail(21);family_fault(FC_ORDER);return;
  }
  size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
  Uint32 *dst=(Uint32 *)canvas->pixels+n;*dst=blend_rgba(*dst,art,art[3]);
  ts_extra_owner[n]=(uint8_t)(d->slot+1);ts_extra_cell[off]=1;++d->extra_stores;
 }
 if(d->extra_stores!=ts_images[ts_frame.image].extra){ts_fail(21);family_fault(FC_ORDER);}
}
static void ts_end(void)
{
 if(!ts_frame.active)return;
 unsigned k=ts_frame.part;TallStructureDraw *d=ts_frame.draw+ts_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||ts_frame.pixels!=ts_counts[ts_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++ts_contract_faults;ts_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;ts_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==ts_totals[ts_frame.image];ts_frame.pending=false;
  if(!d->complete){ts_fail(19);return;}
  if(!ts_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   ts_fail(22);family_fault(FC_SOURCE);return;
  }
  ts_authored_support(d);
 }
}
static void ts_accept(void){ts_frame.accepted=fc.ready&&!fc.frame_failed&&ts_finish();}
TallStructureFamilyStatus render_mirror_tall_structure_family_status(void)
{
 TallStructureFamilyStatus s={0};s.requested=ts_enabled();s.loaded=ts_life.loaded;s.contributed=ts_frame.contributed;
 s.failed=fc.frame_failed||ts_frame.fault;s.accepted=ts_frame.accepted;s.frame=fc_frame;
 s.active=ts_frame.active;s.pending=ts_frame.pending;s.active_slot=ts_frame.slot;
 s.active_part=ts_frame.part<4?ts_parts[ts_frame.part]:UINT_MAX;s.consumed_events=ts_life.consumed;
 s.blend_retirements=ts_blend_retirements;s.normal_retirements=ts_normal_retirements;s.shadow_writes=ts_shadow_writes;
 s.clipped=ts_clipped;s.unwitnessed=ts_unwitnessed;s.lifetime_losses=ts_lifetime_losses;s.bank_losses=ts_bank_losses;
 s.contract_faults=ts_contract_faults;s.first_reason=ts_first_reason;
 s.phase_observations=ts_phase_observations;s.shot_resumptions=ts_shot_resumptions;s.extra_retirements=ts_extra_retirements;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=ts_extra_owner[i]!=0;
 for(unsigned i=0;i<100;i++)s.births[i]=ts_slots[i].birth;
 memcpy(s.draw,ts_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=ts_owned[i]!=0;s.shadowed_cells+=ts_owned[i]&&ts_shadows[i];}return s;
}
bool render_mirror_tall_structure_pre_draw(TallStructureDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!ts_frame.active||ts_frame.part||ts_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=ts_frame.draw[ts_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_tall_structure_pre_part(TallStructureDraw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!ts_frame.active||ts_frame.pixels||
 ts_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=ts_frame.draw[ts_frame.slot];unsigned k=ts_frame.part;*part=ts_parts[k];
 unsigned x=(unsigned)d->x+ts_px[k],y=(unsigned)d->y+ts_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_tall_structure_callbacks(unsigned slot,TallStructureWrite *out,size_t capacity)
{
 if(slot>=100||!out||capacity<ts_frame.draw[slot].callback_count)return 0;
 unsigned n=ts_frame.draw[slot].callback_count;memcpy(out,ts_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_tall_structure_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!ts_frame.accepted||fc.frame_active||fc.frame_failed||
 !ts_frame.contributed||!ts_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,ts_owned,64000);memcpy(shadows,ts_shadows,64000);return true;
}
bool render_mirror_tall_structure_extra_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=4096000||!ts_frame.accepted||fc.frame_active||fc.frame_failed||
 !ts_frame.contributed||!ts_finish()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
 !b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(out,ts_extra_owner,bytes);return true;
}
