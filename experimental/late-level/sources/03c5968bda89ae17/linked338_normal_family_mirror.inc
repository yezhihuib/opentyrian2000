/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private ordinary E1 physical2 normal338-342, four original events and ten independent attempts.
 * Default OFF: LINKED338_NORMAL_ENABLE=1 and LINKED338_NORMAL_ASSET_DIR. This sparse material
 * cannot grant a display lease. Never writes gameplay, events, RNG or palette.
 */
#include "linked338_normal_pins.inc"

static struct {uint64_t generation,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate,armor;int value;uint64_t phase_tick;Linked338NormalBirth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} ln_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;unsigned consumed;char root[1024];
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned event,ei,record,pool,component;int slot,x,y,map1;} call;
} ln_life;
static struct {bool checked,valid;char root[1024];Asset member[7];} ln_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,part,pixels,image;
 Linked338NormalDraw draw[100];Linked338NormalWrite writes[100][672];} ln_frame;
static uint8_t ln_owned[64000],ln_shadows[64000];
/* Complete authored nonzero-alpha native-hole subpixels; never rectangular ownership. */
static uint8_t ln_extra_owner[4096000],ln_extra_cell[64000];
static uint64_t ln_extra_retirements,ln_phase_observations,ln_shot_resumptions;
static bool ln_extra(size_t n){return ln_frame.contributed&&n<4096000&&ln_extra_owner[n]!=0;}
static uint64_t ln_blend_retirements,ln_normal_retirements,ln_shadow_writes;
static uint64_t ln_clipped,ln_unwitnessed,ln_lifetime_losses,ln_bank_losses,ln_contract_faults;
static unsigned ln_first_reason;
static bool ln_resources_current(void);
static const char *ln_root(void){const char *p=getenv("LINKED338_NORMAL_ASSET_DIR");return p?p:"";}
static bool ln_enabled(void)
{
 const char *e=getenv("LINKED338_NORMAL_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool ln_level_scope(void)
{
 return ln_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static int ln_record_index(unsigned r){for(unsigned i=0;i<5;i++)if(ln_records[i].record==r)return (int)i;return -1;}
static int ln_event_index(unsigned e){for(unsigned i=0;i<4;i++)if(ln_events[i].event==e)return (int)i;return -1;}
static int ln_image(unsigned b){for(unsigned i=0;i<7;i++)if(ln_images[i].base==b)return (int)i;return -1;}
static bool ln_pool(unsigned slot,unsigned record){return slot>=25&&slot<50&&ln_record_index(record)>=0;}
static bool ln_event_matches(unsigned event)
{
 int ei=ln_event_index(event);
 if(!ln_life.events||ln_life.events!=eventRec||ei<0||maxEvent!=731)return false;
 const struct JE_EventRecType *r=ln_life.events+event-1;
 return r->eventtime==ln_events[ei].time&&r->eventtype==ln_events[ei].type&&r->eventdat==ln_events[ei].record&&
 r->eventdat2==ln_events[ei].x&&r->eventdat3==ln_events[ei].dy&&r->eventdat4==ln_events[ei].link&&r->eventdat5==ln_events[ei].y&&!r->eventdat6;
}
static bool ln_events_current(void)
{
 for(unsigned e=0;e<4;e++)if(!ln_event_matches(ln_events[e].event))return false;
 return true;
}
static struct {bool active,failed;unsigned event,next;uint64_t observations,mutations;
 struct JE_EventRecType before,expected[731];} ln_script;
static bool ln_row_equal(const struct JE_EventRecType *a,const struct JE_EventRecType *b)
{
 return a->eventtime==b->eventtime&&a->eventtype==b->eventtype&&a->eventdat==b->eventdat&&
 a->eventdat2==b->eventdat2&&a->eventdat3==b->eventdat3&&a->eventdat4==b->eventdat4&&
 a->eventdat5==b->eventdat5&&a->eventdat6==b->eventdat6;
}
static bool ln_scope(void)
{
 return ln_life.loaded&&!ln_life.exhausted&&ln_level_scope()&&terrain_file=='z'&&
 ln_events_current()&&!ln_script.failed&&!strcmp(ln_life.root,ln_root());
}
static void ln_fail(unsigned reason)
{
 /* Only real renderer/lifecycle failures latch resource integrity loss. */
 if(ln_resources.checked&&!ln_resources_current())ln_resources.valid=false;
 if(!ln_first_reason)ln_first_reason=reason;
 ln_frame.fault=true;ln_frame.accepted=false;ln_frame.active=false;ln_frame.pending=false;
 if(ln_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_linked338_normal_retired(unsigned slot)
{
 if(slot>=100)return;
 if(ln_slots[slot].live||ln_slots[slot].pending){
  ++ln_lifetime_losses;
  if(ln_frame.draw[slot].token)ln_fail(1);
 }
 ln_slots[slot].live=ln_slots[slot].pending=ln_slots[slot].initialized=false;
 ln_slots[slot].birth.live=false;
}
static void ln_reset(void)
{
 bool tracked=ln_life.loaded||ln_life.call.live||ln_frame.contributed||ln_frame.pending;
 if(ln_frame.contributed||ln_frame.pending)ln_fail(2);
 if(tracked)for(unsigned i=0;i<100;i++)render_mirror_linked338_normal_retired(i);
 ln_life.call.live=false;
 if(ln_life.epoch==UINT64_MAX)ln_life.exhausted=true;else ++ln_life.epoch;
 /* Only real level begin clears consumed event origins. */
}
void render_mirror_linked338_normal_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 ln_reset();ln_life.loaded=false;ln_life.events=events;ln_life.consumed=0;
 if(!ln_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!ln_events_current()||!late_reuse_stream_matches(events)||
 !ln_root()[0]||strlen(ln_root())>=sizeof ln_life.root){ln_life.events=NULL;return;}
 for(unsigned i=0;i<100;i++)memset(&ln_slots[i].birth,0,sizeof ln_slots[i].birth);
 strcpy(ln_life.root,ln_root());ln_life.loaded=true;
 memset(&ln_script,0,sizeof ln_script);ln_script.next=1;
 memcpy(ln_script.expected,events,sizeof ln_script.expected);
}
/* Observe actual native event execution, never simulate its RNG or patch rows.
 * Unrelated rows need not retain their original load-time hash. Known native
 * current-row mutations are admitted only from their real before/after pair. */
static void ln_script_before(unsigned event)
{
 if(!ln_life.loaded)return;
 if(ln_script.active||!ln_scope()||event<1||event>731||event!=eventLoc||event!=ln_script.next||
 !ln_row_equal(eventRec+event-1,ln_script.expected+event-1)||curLoc<eventRec[event-1].eventtime){ln_script.failed=true;ln_fail(23);return;}
 ln_script.active=true;ln_script.event=event;ln_script.before=eventRec[event-1];
}
static void ln_script_after(unsigned event)
{
 if(!ln_life.loaded)return;
 if(!ln_script.active||ln_script.failed||event!=ln_script.event||event!=eventLoc||event>731){
  ln_script.failed=true;ln_fail(24);return;
 }
 struct JE_EventRecType next=ln_script.before;
 const struct JE_EventRecType *actual=eventRec+event-1;
 if(next.eventtype==12)next.eventdat6=0;
 if(next.eventtype==33&&next.eventdat==533&&
 (actual->eventdat==533||(actual->eventdat>=829&&actual->eventdat<=834)))next.eventdat=actual->eventdat;
 if(!ln_row_equal(&next,actual)||!ln_events_current()){ln_script.failed=true;ln_fail(25);return;}
 ln_script.mutations+=!ln_row_equal(&ln_script.before,actual);
 ln_script.expected[event-1]=next;++ln_script.observations;ln_script.next=event+1;ln_script.active=false;
}
static int ln_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool ln_source(Sprite2_array *bank,unsigned record)
{
 int ri=ln_record_index(record);
 if(ri<0||!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==20&&bank==enemySpriteSheets+i)bound=true;
 return bound&&bank->size==46204&&asteroid1_stamp(bank->data,bank->size)==UINT64_C(0xe2413e3aeab4d908)&&
 asteroid1_record_stamp(record)==ln_records[ri].stamp;
}
static bool ln_colors(void)
{
 for(unsigned i=0;i<COUNTOF(ln_palette);i++)if((rgb_palette[ln_palette[i].index]&0xffffffu)!=ln_palette[i].rgb)return false;
 return true;
}
/* Compare native constructor results, without consuming RNG or writing stats. */
static bool ln_constructor_stats(const struct JE_SingleEnemyType *e)
{
 static const unsigned armor[11]={16,23,30,36,45,54,60,90,120,240,240};
 static const int cap_value[11]={75,100,100,112,150,200,250,400,400,800,800};
 int d=difficultyLevel;if(d==-1)d=0;
 return d>=0&&d<=10&&e->armorleft==armor[d]&&e->evalue==(e->enemytype==338?cap_value[d]:0);
}
/* stage0: live, stage1: exact initialized constructor, stage2: event commit.
 * Positions and idle countdowns are birth-only. Finish uses saved draw origin. */
static bool ln_shape(unsigned slot,unsigned stage)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;unsigned r=e->enemytype;int ri=ln_record_index(r);
 if(ri<0||!ln_pool(slot,r)||e->enemydatofs!=enemyDat+r||!ln_source(e->sprite2s,r)||
 e->size!=1||e->filter||e->ani!=(r==338?12:1)||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive!=(r==338?1:0)||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->enemydie||
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=12||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr!=ln_records[ri].dgr||
 e->edlevel!=ln_records[ri].dlevel||e->edani!=ln_records[ri].dani)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]||e->freq[i])return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=ln_records[ri].sequence[i])return false;
 if(e->iced||e->launchwait||e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||
 e->exccadd!=-1||e->eyccadd!=-1||e->exca!=-1||e->eyca!=-1||
 e->xminbounce!=-10000||e->xmaxbounce!=10000||e->yminbounce!=-10000||e->ymaxbounce!=10000)return false;
 if(stage&&!ln_constructor_stats(e))return false;
 if(!stage&&(e->evalue!=ln_slots[slot].value||e->armorleft>ln_slots[slot].armor))return false;
 if(stage)for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=255)return false;
 if((r==338?(stage?e->enemycycle!=0:e->enemycycle>12):e->enemycycle!=1))return false;
 if(stage==1&&(e->mapoffset||e->ey!=-12||e->ex<6||e->ex>255||e->linknum))return false;
 if(stage==2&&e->linknum!=ln_events[ln_life.call.ei].link)return false;
 if(!stage&&e->linknum!=ln_slots[slot].birth.link)return false;
 return true;
}
static uint64_t ln_event_begin(unsigned event,unsigned typeofs,unsigned pool,int unique)
{
 if(ln_life.call.live){ln_life.call.live=false;ln_fail(3);return 0;}
 int ei=ln_event_index(event);
 if(!ln_scope()||ei<0||event!=eventLoc||pool!=25||unique||!ln_event_matches(event)||
 curLoc!=ln_events[ei].time||(ln_events[ei].type==6?typeofs!=0:typeofs>3)||
 !ln_script.active||ln_script.event!=event)return 0;
 unsigned origin=(unsigned)(ei/2)*5+(ei%2?1+typeofs:0);
 unsigned bit=1u<<origin;
 if(ln_life.consumed&bit)return 0;
 ln_life.consumed|=bit; /* A failed original allocation still consumes the source. */
 if(ln_life.serial==UINT64_MAX){ln_life.exhausted=true;return 0;}
 ln_life.call.live=true;ln_life.call.token=++ln_life.serial;ln_life.call.epoch=ln_life.epoch;
 ln_life.call.event=event;ln_life.call.ei=(unsigned)ei;ln_life.call.record=ln_events[ei].record+typeofs;
 ln_life.call.pool=pool;ln_life.call.component=typeofs;ln_life.call.slot=-1;ln_life.call.generation=0;
 ln_life.call.map1=mapX;
 ln_life.call.x=ln_events[ei].x-(mapX-1)*24-12+(typeofs%2?24:0);
 ln_life.call.y=-28+ln_events[ei].y-(typeofs>=2?28:0);
 return ln_life.call.token;
}
void render_mirror_linked338_normal_enemy_allocated(void *p,unsigned record,int unique)
{
 if(!ln_life.loaded)return;
 int s=ln_slot(p);if(s<0)return;
 render_mirror_linked338_normal_retired((unsigned)s);
 if(ln_slots[s].generation==UINT64_MAX){ln_slots[s].exhausted=true;return;}
 if(ln_slots[s].exhausted)return;
 ++ln_slots[s].generation; /* All allocations, including unrelated records. */
 if(ln_life.call.live&&ln_scope()&&ln_pool((unsigned)s,record)&&enemyAvail[s]==1&&!unique&&record==ln_life.call.record&&ln_life.call.slot==-1){
  ln_slots[s].pending=true;ln_slots[s].record=record;ln_life.call.slot=s;ln_life.call.generation=ln_slots[s].generation;
 }
}
void render_mirror_linked338_normal_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 if(!ln_life.loaded)return;
 int s=ln_slot(p);if(s<0)return;
 ln_slots[s].initialized=ln_slots[s].pending&&ln_life.call.live&&ln_scope()&&
 ln_life.call.slot==s&&ln_life.call.generation==ln_slots[s].generation&&
 record==ln_life.call.record&&avail==0&&enemyAvail[s]==1&&ln_shape((unsigned)s,1);
}
void render_mirror_linked338_normal_event_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=ln_life.call.slot;
 bool ok=ln_life.call.live&&token==ln_life.call.token&&ln_life.call.epoch==ln_life.epoch&&ln_scope()&&
 s>=0&&s<100&&ln_pool((unsigned)s,ln_life.call.record)&&one_based==(unsigned)s+1&&eventLoc==ln_life.call.event&&
 curLoc==ln_events[ln_life.call.ei].time&&ln_script.active&&ln_script.event==eventLoc&&mapX==ln_life.call.map1&&ln_event_matches(ln_life.call.event);
 if(ok)ok=ln_slots[s].pending&&ln_slots[s].initialized&&ln_life.call.generation==ln_slots[s].generation&&
 enemyAvail[s]==0&&enemy[s].enemytype==ln_life.call.record&&ln_shape((unsigned)s,2)&&enemy[s].ex==ln_life.call.x&&enemy[s].ey==ln_life.call.y;
 if(s>=0&&s<100){
  ln_slots[s].live=ok;ln_slots[s].pending=ln_slots[s].initialized=false;
  if(ok){ln_slots[s].armor=enemy[s].armorleft;ln_slots[s].value=enemy[s].evalue;ln_slots[s].cycle=ln_slots[s].record==338?0:1;ln_slots[s].gate=ln_slots[s].record==338?1:0;ln_slots[s].phase_tick=UINT64_MAX;ln_slots[s].witness=ln_slots[s].generation;ln_slots[s].bank=enemy[s].sprite2s;
   ln_slots[s].data=enemy[s].sprite2s->data;ln_slots[s].bytes=enemy[s].sprite2s->size;
   ln_slots[s].birth=(Linked338NormalBirth){.epoch=ln_life.epoch,.token=token,.generation=ln_slots[s].generation,
    .slot=(unsigned)s,.event=ln_life.call.event,.record=ln_slots[s].record,.link=enemy[s].linknum,.component=ln_life.call.component,.cycle=ln_slots[s].cycle,.gate=ln_slots[s].gate,
    .bank_role=20,.bank_bytes=46204,
    .bank_stamp=UINT64_C(0xe2413e3aeab4d908),.record_stamp=ln_records[ln_record_index(ln_slots[s].record)].stamp,
    .bank_object=(uintptr_t)ln_slots[s].bank,.bank_data=(uintptr_t)ln_slots[s].data,
    .event_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 ln_life.call.live=false;
}
void render_mirror_linked338_normal_bank_changed(Sprite2_array *bank)
{
 if(!ln_life.loaded&&!ln_life.call.live)return;
 for(unsigned i=0;i<100;i++)if(ln_slots[i].live&&ln_slots[i].bank==bank){++ln_bank_losses;render_mirror_linked338_normal_retired(i);}
 if(ln_life.call.live){ln_life.call.live=false;ln_fail(4);}
}
static bool ln_witness(unsigned s)
{
 return s<100&&ln_pool(s,ln_slots[s].record)&&ln_slots[s].live&&!ln_slots[s].exhausted&&
 ln_slots[s].birth.epoch==ln_life.epoch&&ln_event_matches(ln_slots[s].birth.event)&&
 ln_slots[s].generation==ln_slots[s].witness&&enemyAvail[s]==0&&enemy[s].enemytype==ln_slots[s].record&&enemy[s].sprite2s&&
 ln_slots[s].bank==enemy[s].sprite2s&&ln_slots[s].data==enemy[s].sprite2s->data&&ln_slots[s].bytes==enemy[s].sprite2s->size;
}
static void ln_enemy_animated(unsigned slot)
{
 if(slot>=100||!ln_slots[slot].live)return;
 if(!ln_scope()||!ln_witness(slot)||!ln_shape(slot,0)||ln_slots[slot].phase_tick==fc_frame||
 enemy[slot].ex+tempMapXOfs<=-29||enemy[slot].ex+tempMapXOfs>=300){render_mirror_linked338_normal_retired(slot);return;}
 unsigned cycle=1,gate=ln_slots[slot].record==338?1:0;
 if(gate){cycle=ln_slots[slot].cycle+1;if(cycle>12)cycle=1;}
 if(enemy[slot].enemycycle!=cycle||enemy[slot].aniactive!=gate){render_mirror_linked338_normal_retired(slot);return;}
 ln_slots[slot].cycle=cycle;ln_slots[slot].gate=gate;ln_slots[slot].phase_tick=fc_frame;
 Linked338NormalBirth *b=&ln_slots[slot].birth;b->cycle=cycle;b->gate=gate;b->phase_tick=fc_frame;
 ++b->phase_observations;++ln_phase_observations;
}
/* Strict normal-only family: no weapon, launcher or damage resource loader. */

static void ln_tick(void)
{
 /* Inactive feature: no resource access, census, array clear or slot scan. */
 if(!ln_life.loaded&&!ln_frame.contributed&&!ln_frame.pending)return;
 if(ln_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 if(!ln_life.consumed&&!ln_frame.contributed&&!ln_frame.pending)return;
 memset(&ln_frame,0,sizeof ln_frame);memset(ln_owned,0,sizeof ln_owned);memset(ln_shadows,0,sizeof ln_shadows);
 memset(ln_extra_owner,0,sizeof ln_extra_owner);memset(ln_extra_cell,0,sizeof ln_extra_cell);ln_first_reason=0;
 if(ln_life.loaded&&!ln_scope()){ln_reset();ln_life.loaded=false;return;}
 for(unsigned i=0;i<100;i++)if(ln_slots[i].live&&(!ln_witness(i)||!ln_shape(i,0)||enemy[i].enemycycle!=ln_slots[i].cycle||enemy[i].aniactive!=ln_slots[i].gate))render_mirror_linked338_normal_retired(i);
}
static bool ln_load(unsigned image)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshp-%u-8.hda",ln_resources.root,ln_images[image].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==ln_images[image].id&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==ln_images[image].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 ln_resources.member[image]=(Asset){true,true,ASSET_ASTEROID1,ln_images[image].base,24,28,0,0,8,rgba};return true;
}
static bool ln_resources_current(void)
{
 if(!ln_resources.checked||!ln_resources.valid||strcmp(ln_resources.root,ln_root()))return false;
 for(unsigned image=0;image<7;image++){
 const Asset *a=ln_resources.member+image;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=ln_images[image].base||a->w!=24||a->h!=28||
 a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,172032)!=ln_images[image].rgba)return false;
 }
 return true;
}
static bool ln_ready(void)
{
 if(!ln_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!ln_resources.checked){ln_resources.checked=true;strcpy(ln_resources.root,ln_life.root);ln_resources.valid=true;for(unsigned i=0;i<7;i++)if(!ln_load(i))ln_resources.valid=false;}
 if(!ln_resources_current()){ln_resources.valid=false;return false;}
 return true;
}
static void ln_shutdown(void)
{
 ln_reset();ln_life.loaded=false;for(unsigned i=0;i<7;i++)free(ln_resources.member[i].rgba);memset(&ln_resources,0,sizeof ln_resources);
}
static bool ln_dependencies(bool partial)
{
 if(!ln_frame.contributed)return true;
 if(ln_frame.fault||!ln_scope()||!ln_colors()||!ln_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<100;i++)if(ln_frame.draw[i].token){const Linked338NormalDraw *d=ln_frame.draw+i;unsigned s=i;
  if(!ln_witness(s)||!ln_shape(s,0)||d->generation!=ln_slots[s].generation||
  d->token!=ln_slots[s].birth.token||d->epoch!=ln_life.epoch||d->event!=ln_slots[s].birth.event||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||d->record!=ln_slots[s].record||ln_image(d->base)<0||
  d->cycle<1||d->cycle!=enemy[s].enemycycle||d->base!=enemy[s].egr[d->cycle-1]||d->draw_gate!=enemy[s].aniactive)return false;
  if(!d->complete){if(!partial||!ln_frame.pending||ln_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=ln_totals[ln_image(d->base)]||(!partial&&d->extra_stores!=ln_images[ln_image(d->base)].extra))return false;
 }
 return partial||(!ln_frame.active&&!ln_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool ln_finish(void){return ln_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool ln_guard(void)
{
 if(ln_finish())return true;
 ln_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool ln_before_tile(unsigned slot,int part)
{
 if(ln_frame.contributed&&!ln_dependencies(true)){ln_fail(5);return false;}
 if(ln_frame.pending&&(ln_frame.active||slot!=ln_frame.slot||
 ln_frame.draw[slot].next>=4||part!=(int)ln_parts[ln_frame.draw[slot].next])){ln_fail(6);return false;}
 return true;
}
static bool ln_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool ln_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!ln_life.loaded||slot>=100||ln_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!ln_witness(slot)){++ln_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)ln_parts[k];k++);
 if(k==4){if(ln_frame.contributed)ln_fail(7);return false;}
 int64_t ox=(int64_t)x-ln_px[k],oy=(int64_t)y-ln_py[k];
 Linked338NormalDraw *d=ln_frame.draw+slot;
 if(!ln_geometry(ox,oy)){++ln_clipped;if(d->token)ln_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !ln_scope()||sheet!=enemy[slot].sprite2s||!ln_shape(slot,0)||ln_slots[slot].phase_tick!=fc_frame||enemy[slot].enemycycle<1||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||ln_image(base)<0||!ln_colors()||!ln_ready()){
  if(d->token||ln_frame.contributed)ln_fail(9);
  return false;
 }
 if(k==0){if(d->token||ln_frame.pending){ln_fail(10);return false;}}
 else if(!ln_frame.pending||ln_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||ln_frame.pending)ln_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||ln_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++ln_contract_faults;ln_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++ln_contract_faults;ln_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  ln_frame.image=(unsigned)ln_image(base);
  *d=(Linked338NormalDraw){.frame=fc_frame,.epoch=ln_life.epoch,.token=ln_slots[slot].birth.token,
   .generation=ln_slots[slot].generation,.slot=slot,.event=ln_slots[slot].birth.event,.record=ln_slots[slot].record,.cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,
   .base=base,.cur_loc=curLoc,.bank_role=20,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  ln_frame.pending=true;ln_frame.slot=slot;
 }
 d->part_order[k]=(unsigned)part;
 ln_frame.part=k;ln_frame.pixels=0;ln_frame.active=true;ln_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool ln_retire(unsigned off,int style)
{
 if(!ln_frame.contributed)return false;
 bool owned=off<64000&&ln_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++ln_blend_retirements;else ++ln_normal_retirements;
 ln_owned[off]=ln_shadows[off]=0;}
 if(off<64000&&style!=MIRROR_SHADOW&&ln_extra_cell[off]){
  unsigned x=off%320,y=off/320;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   size_t n=(y*8+sy)*2560+x*8+sx;ln_extra_retirements+=ln_extra_owner[n]!=0;ln_extra_owner[n]=0;
  }
  ln_extra_cell[off]=0;
 }
 return owned;
}
static bool ln_pixel(unsigned x,unsigned y,int style)
{
 if(!ln_frame.active){if(ln_frame.pending){ln_fail(14);return true;}return false;}
 Linked338NormalDraw *d=ln_frame.draw+ln_frame.slot;
 unsigned k=ln_frame.part;
 if(k>=4||ln_frame.pixels>=ln_counts[ln_frame.image][k]){++ln_contract_faults;ln_fail(15);return true;}
 const Linked338NormalWrite *w=ln_native[ln_frame.image][k]+ln_frame.pixels;
 unsigned lx=ln_px[k]+w->x,ly=ln_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++ln_contract_faults;ln_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&ln_resources.member[ln_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here. Exact authored extras are separate. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 ln_owned[off]=(uint8_t)(ln_frame.slot+1);ln_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){ln_fail(17);return true;}
 ln_frame.writes[ln_frame.slot][d->callback_count++]=(Linked338NormalWrite){(uint8_t)lx,(uint8_t)ly,w->index};
 ++ln_frame.pixels;d->part_count[k]=ln_frame.pixels;return true;
}
static void ln_shadow(unsigned off)
{
 if(off<64000&&ln_owned[off]){if(ln_shadows[off]<255)++ln_shadows[off];++ln_shadow_writes;}
}
/* Same narrow authored-support policy as firing_rock462: exact nonzero-alpha
 * native-hole subpixels only, after a complete observed native quartet. No
 * native INDEX, selected[], native owner, global permission or cached underlay. */
static void ln_authored_support(Linked338NormalDraw *d)
{
 
 const Asset *a=ln_resources.member+ln_frame.image;
 for(unsigned i=0;i<ln_images[ln_frame.image].extra;i++){
  unsigned ax=ln_extras[ln_frame.image][i].x,ay=ln_extras[ln_frame.image][i].y;
  const Uint8 *art=a->rgba+(ay*192+ax)*4;
  unsigned off=((unsigned)d->y+ay/8)*320+(unsigned)d->x+ax/8;
  if(ln_native_mask[ln_frame.image][(ay/8)*24+ax/8]||!art[3]||expected[off]!=((const Uint8 *)fc_source_pixels)[off]){
   ln_fail(21);family_fault(FC_ORDER);return;
  }
  size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
  Uint32 *dst=(Uint32 *)canvas->pixels+n;*dst=blend_rgba(*dst,art,art[3]);
  ln_extra_owner[n]=(uint8_t)(d->slot+1);ln_extra_cell[off]=1;++d->extra_stores;
 }
 if(d->extra_stores!=ln_images[ln_frame.image].extra){ln_fail(21);family_fault(FC_ORDER);}
}
static void ln_end(void)
{
 if(!ln_frame.active)return;
 unsigned k=ln_frame.part;Linked338NormalDraw *d=ln_frame.draw+ln_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||ln_frame.pixels!=ln_counts[ln_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++ln_contract_faults;ln_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;ln_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==ln_totals[ln_frame.image];ln_frame.pending=false;
  if(!d->complete){ln_fail(19);return;}
  if(!ln_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   ln_fail(22);family_fault(FC_SOURCE);return;
  }
  ln_authored_support(d);
 }
}
static void ln_accept(void){ln_frame.accepted=fc.ready&&!fc.frame_failed&&ln_finish();}
Linked338NormalFamilyStatus render_mirror_linked338_normal_family_status(void)
{
 Linked338NormalFamilyStatus s={0};s.requested=ln_enabled();s.loaded=ln_life.loaded;s.contributed=ln_frame.contributed;
 s.failed=fc.frame_failed||ln_frame.fault;s.accepted=ln_frame.accepted;s.frame=fc_frame;
 s.active=ln_frame.active;s.pending=ln_frame.pending;s.active_slot=ln_frame.slot;
 s.active_part=ln_frame.part<4?ln_parts[ln_frame.part]:UINT_MAX;s.consumed_events=ln_life.consumed;
 s.blend_retirements=ln_blend_retirements;s.normal_retirements=ln_normal_retirements;s.shadow_writes=ln_shadow_writes;
 s.clipped=ln_clipped;s.unwitnessed=ln_unwitnessed;s.lifetime_losses=ln_lifetime_losses;s.bank_losses=ln_bank_losses;
 s.contract_faults=ln_contract_faults;s.first_reason=ln_first_reason;
 s.phase_observations=ln_phase_observations;s.shot_resumptions=ln_shot_resumptions;s.extra_retirements=ln_extra_retirements;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=ln_extra_owner[i]!=0;
 for(unsigned i=0;i<100;i++)s.births[i]=ln_slots[i].birth;
 memcpy(s.draw,ln_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=ln_owned[i]!=0;s.shadowed_cells+=ln_owned[i]&&ln_shadows[i];}return s;
}
bool render_mirror_linked338_normal_pre_draw(Linked338NormalDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!ln_frame.active||ln_frame.part||ln_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=ln_frame.draw[ln_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_linked338_normal_pre_part(Linked338NormalDraw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!ln_frame.active||ln_frame.pixels||
 ln_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=ln_frame.draw[ln_frame.slot];unsigned k=ln_frame.part;*part=ln_parts[k];
 unsigned x=(unsigned)d->x+ln_px[k],y=(unsigned)d->y+ln_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_linked338_normal_callbacks(unsigned slot,Linked338NormalWrite *out,size_t capacity)
{
 if(slot>=100||!out||capacity<ln_frame.draw[slot].callback_count)return 0;
 unsigned n=ln_frame.draw[slot].callback_count;memcpy(out,ln_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_linked338_normal_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!ln_frame.accepted||fc.frame_active||fc.frame_failed||
 !ln_frame.contributed||!ln_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,ln_owned,64000);memcpy(shadows,ln_shadows,64000);return true;
}
bool render_mirror_linked338_normal_extra_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=4096000||!ln_frame.accepted||fc.frame_active||fc.frame_failed||
 !ln_frame.contributed||!ln_finish()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
 !b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(out,ln_extra_owner,bytes);return true;
}
