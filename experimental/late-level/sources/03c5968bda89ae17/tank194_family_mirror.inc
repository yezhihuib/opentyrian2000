/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private ordinary E1 physical2 ASTEROID2 record194. Only original births
 * 6/25/26 in pool75..99. TANK194_REPEAT8_ENABLE=1 adds only the eight
 * pinned repeat births; this expansion defaults OFF and latches per level.
 * TANK194_NEXT7_ENABLE=1 plus REPEAT8 adds seven exact later births and
 * original continuations through event258; it also defaults OFF and latches.
 * Base family is default OFF: TANK194_FAMILY_ENABLE=1 plus asset root.
 * Material only at witnessed unmodified native cells. No display admission,
 * native state, RNG, life, equipment, event, sprite or palette writes.
 */
#include "tank194_native.inc"
typedef struct {
 int exc,eyc,fixedmovey;unsigned cycle,freq[3],die;
} T194Script;
static struct {uint64_t generation,witness,script_serial;bool exhausted,pending,initialized,live;
 Tank194Birth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;
 T194Script script;unsigned script_event,birth_armor;int birth_value;
} t194_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded,stream_broken,repeat8,next7;unsigned consumed,next_event;
 char root[1024];const struct JE_EventRecType *events;unsigned mutated31,mutated106;uint64_t mutated106_epoch;
 unsigned mutated_next7[2];uint64_t mutated_next7_epoch[2];
 struct {bool live;uint64_t token,epoch,generation;unsigned event;int slot,x,y,map1;} call;
 struct {bool live;unsigned event,type;int d[6];uint64_t epoch,generation[25];bool live_slot[25];} step;
} t194_life;
static struct {bool checked,valid;char root[1024];Asset member[8];} t194_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,part,pixels;
 Tank194Draw draw[25];Tank194Write writes[25][168];} t194_frame;
static uint8_t t194_owned[64000],t194_shadows[64000];
static uint64_t t194_blend_retirements,t194_normal_retirements,t194_shadow_writes;
static uint64_t t194_clipped,t194_unwitnessed,t194_lifetime_losses,t194_bank_losses,t194_contract_faults,t194_script_losses;
static unsigned t194_first_reason;
static bool t194_resources_current(void);
static const char *t194_root(void){const char *p=getenv("TANK194_FAMILY_ASSET_DIR");return p?p:"";}
static bool t194_enabled(void)
{
 const char *e=getenv("TANK194_FAMILY_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool t194_repeat8_requested(void)
{
 const char *e=getenv("TANK194_REPEAT8_ENABLE");return e&&!strcmp(e,"1");
}
static bool t194_next7_requested(void)
{
 const char *e=getenv("TANK194_NEXT7_ENABLE");return e&&!strcmp(e,"1");
}
static bool t194_next7_enabled(void){return t194_life.repeat8&&t194_life.next7;}
static unsigned t194_prefix_events(void){return t194_next7_enabled()?258u:t194_life.repeat8?148u:75u;}
static bool t194_repeat8_current(void)
{
 return t194_repeat8_requested()==t194_life.repeat8&&t194_next7_requested()==t194_life.next7;
}
static void t194_repeat8_observe(void)
{
 /* Only actual event/render work may poison an epoch; getters stay pure. */
 if(t194_life.loaded&&!t194_repeat8_current())t194_life.stream_broken=true;
}
static bool t194_level_scope(void)
{
 return t194_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static bool t194_event_matches(unsigned event,bool original)
{
 if(!t194_life.events||event<1||event>t194_prefix_events()||maxEvent!=731)return false;
 const struct JE_EventRecType *r=t194_life.events+event-1;
 const int d[6]={r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6};
 if(r->eventtime!=t194_events[event-1].time||r->eventtype!=t194_events[event-1].type)return false;
 for(unsigned i=0;i<6;i++){
  int v=t194_events[event-1].d[i];
  /* This exception exists only after the actual epoch-local type33 operation.
   * At level begin and at original entry the row must still contain533. */
  if(!original&&event==31&&i==0&&t194_life.mutated31)v=(int)t194_life.mutated31;
  /* Only the witnessed epoch-local event106 type12 result may replace4. */
  if(!original&&event==106&&i==5&&t194_life.mutated106_epoch==t194_life.epoch&&
   t194_life.mutated106_epoch)v=(int)t194_life.mutated106;
  /* The later type12 rows have their own actual, epoch-local receipts.
   * Neither precleared rows nor any other changed field is admitted. */
  if(!original&&t194_next7_enabled()&&i==5&&(event==230||event==240)){
   unsigned k=event==230?0u:1u;
   if(t194_life.mutated_next7_epoch[k]&&t194_life.mutated_next7_epoch[k]==t194_life.epoch)
    v=(int)t194_life.mutated_next7[k];
  }
  if(d[i]!=v)return false;
 }
 return true;
}
static bool t194_events_current(void)
{
 for(unsigned e=1;e<=t194_prefix_events();e++)if(!t194_event_matches(e,false))return false;
 return true;
}
static bool t194_scope(void)
{
 return t194_life.loaded&&!t194_life.exhausted&&!t194_life.stream_broken&&t194_repeat8_current()&&t194_level_scope()&&terrain_file=='z'&&
 t194_events_current()&&!strcmp(t194_life.root,t194_root());
}
static void t194_fail(unsigned reason)
{
 if(t194_resources.checked&&!t194_resources_current())t194_resources.valid=false;
 if(!t194_first_reason)t194_first_reason=reason;
 t194_frame.fault=true;t194_frame.accepted=false;t194_frame.active=false;t194_frame.pending=false;
 if(t194_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_tank194_family_retired(unsigned slot)
{
 if(slot>=100)return;
 if(t194_slots[slot].live||t194_slots[slot].pending){
  ++t194_lifetime_losses;
  if(slot>=75&&t194_frame.draw[slot-75].token)t194_fail(1);
 }
 t194_slots[slot].live=t194_slots[slot].pending=t194_slots[slot].initialized=false;
 t194_slots[slot].birth.live=false;
}
static void t194_reset(void)
{
 if(t194_frame.contributed||t194_frame.pending)t194_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_tank194_family_retired(i);
 t194_life.call.live=t194_life.step.live=false;
 if(t194_life.epoch==UINT64_MAX)t194_life.exhausted=true;else ++t194_life.epoch;
}
void render_mirror_tank194_family_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 t194_reset();t194_life.loaded=false;t194_life.events=events;t194_life.consumed=0;
 t194_life.mutated31=0;t194_life.mutated106=0;t194_life.mutated106_epoch=0;t194_life.next_event=1;t194_life.stream_broken=false;t194_life.repeat8=t194_repeat8_requested();
 t194_life.next7=t194_next7_requested();
 memset(t194_life.mutated_next7,0,sizeof t194_life.mutated_next7);
 memset(t194_life.mutated_next7_epoch,0,sizeof t194_life.mutated_next7_epoch);
 for(unsigned i=0;i<100;i++)memset(&t194_slots[i].birth,0,sizeof t194_slots[i].birth);
 if(!t194_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!t194_events_current()||
 !t194_root()[0]||strlen(t194_root())>=sizeof t194_life.root){t194_life.events=NULL;return;}
 strcpy(t194_life.root,t194_root());t194_life.loaded=true;
}
static int t194_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static int t194_birth_index(unsigned event)
{
 if(event==6)return 0;if(event==25)return 1;if(event==26)return 2;
 if(!t194_life.repeat8)return -1;
 switch(event){case 36:return 3;case 37:return 4;case 76:return 5;case 77:return 6;
 case 78:return 7;case 89:return 8;case 90:return 9;case 91:return 10;default:break;}
 if(!t194_next7_enabled())return -1;
 switch(event){case 177:return 11;case 208:return 12;case 209:return 13;case 210:return 14;
 case 211:return 15;case 246:return 16;case 247:return 17;default:return -1;}
}
static bool t194_source(Sprite2_array *bank)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=46204)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==20&&bank==enemySpriteSheets+i)bound=true;
 return bound&&asteroid1_stamp(bank->data,bank->size)==UINT64_C(0xe2413e3aeab4d908)&&
 asteroid1_record_stamp(194)==UINT64_C(0xa9beba644b307039);
}
static bool t194_colors(void)
{
 for(unsigned i=0;i<COUNTOF(t194_palette);i++)if((rgb_palette[t194_palette[i].index]&0xffffffu)!=t194_palette[i].rgb)return false;
 return true;
}
static T194Script t194_script(unsigned s)
{
 const struct JE_SingleEnemyType *e=enemy+s;
 return (T194Script){e->exc,e->eyc,e->fixedmovey,e->enemycycle,{e->freq[0],e->freq[1],e->freq[2]},e->enemydie};
}
static bool t194_script_equal(T194Script a,T194Script b)
{
 return a.exc==b.exc&&a.eyc==b.eyc&&a.fixedmovey==b.fixedmovey&&a.cycle==b.cycle&&a.die==b.die&&
 a.freq[0]==b.freq[0]&&a.freq[1]==b.freq[1]&&a.freq[2]==b.freq[2];
}
/* Exact record194 constructor outputs for the engine difficulty enum0..10
 * (and legacy-1). These compare native results; they never assign gameplay. */
static bool t194_constructor_stats(const struct JE_SingleEnemyType *e)
{
 static const unsigned armor[11]={16,23,30,36,45,54,60,90,120,240,240};
 static const int value[11]={37,50,50,56,75,100,125,200,200,400,400};
 int d=difficultyLevel;
 if(d==-1)d=0;
 return d>=0&&d<=10&&e->armorleft==armor[d]&&e->evalue==value[d];
}
/* stage0 live; stage1 exact constructor; stage2 event commit. Live position,
 * armor damage and shot countdown/multipos are native state, never frozen. */
static bool t194_shape(unsigned slot,unsigned stage)
{
 if(slot<75||slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=194||e->enemydatofs!=enemyDat+194||!t194_source(e->sprite2s)||
 e->size!=1||e->filter||e->enemycycle<1||e->enemycycle>8||e->ani!=8||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=1||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani||e->iced||
 e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||e->exccadd!=-1||e->eyccadd!=-1||e->exca!=-1||e->eyca!=-1||
 e->xminbounce!=-10000||e->xmaxbounce!=10000||e->yminbounce!=-10000||e->ymaxbounce!=10000)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]!=i+2)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=(i<8?t194_bases[i]:0))return false;
 if(stage){
  if(!t194_constructor_stats(e)||e->mapoffset||e->launchwait||e->exc||e->eyc||e->enemycycle!=1||e->enemydie)return false;
  for(unsigned i=0;i<3;i++)if(e->freq[i]||e->eshotmultipos[i]||e->eshotwait[i]!=20)return false;
  if(stage==1&&(e->ey!=-12||e->ex<6||e->ex>255||e->linknum))return false;
 }else if(e->linknum!=t194_slots[slot].birth.link||e->evalue!=t194_slots[slot].birth_value||
 e->armorleft>t194_slots[slot].birth_armor||!t194_script_equal(t194_script(slot),t194_slots[slot].script))return false;
 return true;
}
static bool t194_witness(unsigned s)
{
 return s>=75&&s<100&&t194_slots[s].live&&!t194_slots[s].exhausted&&
 t194_slots[s].birth.epoch==t194_life.epoch&&t194_birth_index(t194_slots[s].birth.event)>=0&&
 t194_event_matches(t194_slots[s].birth.event,true)&&t194_slots[s].generation==t194_slots[s].witness&&enemyAvail[s]==0&&enemy[s].sprite2s&&
 t194_slots[s].bank==enemy[s].sprite2s&&t194_slots[s].data==enemy[s].sprite2s->data&&t194_slots[s].bytes==enemy[s].sprite2s->size;
}
/* Selectors are the native selectors. Type19 dat4==0 is not a wildcard.
 * Returning false proves no selected actor field is changed by that operation. */
static bool t194_targets(unsigned type,const int d[6],unsigned s)
{
 switch(type){
 case 19: return d[2]==99||(d[2]==0&&enemy[s].linknum==d[3])||(d[2]>79&&d[2]<90);
 case 31: return d[3]==99||enemy[s].linknum==d[3];
 case 33: return enemy[s].linknum==d[3];
 case 45: return false; /* Scoped !twoPlayerMode&&!onePlayerAction&&!superTyrian. */
 case 2: case 5: case 6: case 7: case 9: case 10: case 12: case 14: case 21: return false;
 default: return true; /* Unknown operations cannot prove exclusion. */
 }
}
void render_mirror_tank194_family_event_before(unsigned event)
{
 ln_script_before(event); /* Linked338 normal: actual event observation. */
 ts_script_before(event); /* Independent tall native-script observer. */
 if(!t194_life.loaded)return;
 if(t194_life.step.live||!t194_scope()||event!=eventLoc||event!=t194_life.next_event||event<1||event>maxEvent||
 /* The later encounter ends at the original prefix, before map-stop.
  * Default-OFF retains the old post-prefix exclusion behavior verbatim. */
 (t194_next7_enabled()&&event>t194_prefix_events())||
 (event<=t194_prefix_events()&&(!t194_event_matches(event,true)||curLoc!=t194_events[event-1].time))){
  ++t194_script_losses;t194_life.stream_broken=true;
  for(unsigned s=75;s<100;s++)render_mirror_tank194_family_retired(s);
  t194_life.step.live=false;return;
 }
 const struct JE_EventRecType *r=t194_life.events+event-1;
 t194_life.step.live=true;t194_life.step.epoch=t194_life.epoch;t194_life.step.event=event;t194_life.step.type=r->eventtype;
 const int d[6]={r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6};
 memcpy(t194_life.step.d,d,sizeof d);
 for(unsigned s=75;s<100;s++){
  if(t194_slots[s].live&&(!t194_witness(s)||!t194_shape(s,0)))render_mirror_tank194_family_retired(s);
  bool target=t194_slots[s].live&&t194_targets(r->eventtype,d,s);
  if(target&&(event>t194_prefix_events()||(r->eventtype!=19&&r->eventtype!=31&&r->eventtype!=33))){
   ++t194_script_losses;render_mirror_tank194_family_retired(s);
  }
  t194_life.step.live_slot[s-75]=t194_slots[s].live;
  t194_life.step.generation[s-75]=t194_slots[s].generation;
 }
}
void render_mirror_tank194_family_event_after(unsigned event)
{
 ln_script_after(event); /* Linked338 normal: actual event observation. */
 ts_script_after(event); /* Independent tall native-script observer. */
 if(!t194_life.step.live)return;
 bool ok=event==t194_life.step.event&&event==eventLoc&&event==t194_life.next_event;
 unsigned type=t194_life.step.type;const int *d=t194_life.step.d;
 if(ok&&event==31){
  const struct JE_EventRecType *r=t194_life.events+30;
  unsigned v=(unsigned)r->eventdat;
  ok=type==33&&d[0]==533&&(v==533||(v>=829&&v<=834));
  if(ok)t194_life.mutated31=v; /* Native return value only; no RNG/life access. */
 }
 if(ok&&t194_life.repeat8&&event==106){
  const struct JE_EventRecType *r=t194_life.events+105;
  const int after[6]={r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6};
  /* Native type12 clears only dat6 after reading its original pool selector.
   * Require the exact original before-row and actual after-row in this epoch. */
  ok=t194_life.step.epoch==t194_life.epoch&&!t194_life.mutated106_epoch&&
   type==12&&r->eventtype==12&&curLoc==1084&&r->eventtime==1084;
  for(unsigned i=0;i<6;i++)if(d[i]!=t194_events[105].d[i]||
   after[i]!=(i==5?0:t194_events[105].d[i]))ok=false;
  if(ok){t194_life.mutated106=(unsigned)r->eventdat6;t194_life.mutated106_epoch=t194_life.epoch;}
 }
 if(ok&&t194_next7_enabled()&&(event==230||event==240)){
  unsigned k=event==230?0u:1u;
  const struct JE_EventRecType *r=t194_life.events+event-1;
  const int after[6]={r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6};
  /* Observe the native pool75 selector4 becoming0, after its constructor
   * dispatch. Do not patch the row, predict a token or relax the prefix. */
  ok=t194_life.step.epoch==t194_life.epoch&&!t194_life.mutated_next7_epoch[k]&&
   type==12&&r->eventtype==12&&curLoc==t194_events[event-1].time&&
   r->eventtime==t194_events[event-1].time&&d[5]==4;
  for(unsigned i=0;i<6;i++)if(d[i]!=t194_events[event-1].d[i]||
   after[i]!=(i==5?0:t194_events[event-1].d[i]))ok=false;
  if(ok){t194_life.mutated_next7[k]=(unsigned)r->eventdat6;t194_life.mutated_next7_epoch[k]=t194_life.epoch;}
 }
 ok=ok&&t194_scope();
 for(unsigned s=75;s<100;s++)if(t194_life.step.live_slot[s-75]&&t194_slots[s].live){
  bool current=ok&&t194_life.step.generation[s-75]==t194_slots[s].generation&&t194_witness(s);
  T194Script next=t194_slots[s].script;bool target=t194_targets(type,d,s);
  if(current&&target){
   if(type==19){if(d[0]!=-99)next.exc=d[0];if(d[1]!=-99)next.eyc=d[1];
    if(d[5])next.fixedmovey=d[5];if(d[5]==-99)next.fixedmovey=0;if(d[4]>0)next.cycle=(unsigned)d[4];}
   else if(type==31){for(unsigned j=0;j<3;j++){next.freq[j]=(unsigned)d[j];if(enemy[s].eshotwait[j]!=1)current=false;}}
   else if(type==33)next.die=event==31?t194_life.mutated31:(unsigned)d[0];
   else current=false;
  }
  current=current&&t194_script_equal(next,t194_script(s));
  if(current&&target){
   if(t194_slots[s].script_serial==UINT64_MAX)current=false;
   else {t194_slots[s].script=next;t194_slots[s].script_event=event;++t194_slots[s].script_serial;}
  }
  if(!current||!t194_shape(s,0)){++t194_script_losses;render_mirror_tank194_family_retired(s);}
 }
 if(!ok){t194_life.stream_broken=true;for(unsigned s=75;s<100;s++)render_mirror_tank194_family_retired(s);}
 else ++t194_life.next_event;
 t194_life.step.live=false;
}
uint64_t render_mirror_tank194_family_event_begin(unsigned event,unsigned typeofs,unsigned pool,int unique)
{
 t194_repeat8_observe();
 if(t194_life.call.live){t194_life.call.live=false;t194_fail(3);return 0;}
 int index=t194_birth_index(event);
 if(!t194_scope()||index<0||!t194_life.step.live||t194_life.step.event!=event||event!=eventLoc||typeofs||pool!=75||unique||
 !t194_event_matches(event,true)||curLoc!=t194_events[event-1].time)return 0;
 unsigned bit=1u<<(unsigned)index;
 if(t194_life.consumed&bit)return 0;
 t194_life.consumed|=bit;
 if(t194_life.serial==UINT64_MAX){t194_life.exhausted=true;return 0;}
 t194_life.call.live=true;t194_life.call.token=++t194_life.serial;t194_life.call.epoch=t194_life.epoch;
 t194_life.call.event=event;t194_life.call.slot=-1;t194_life.call.generation=0;t194_life.call.map1=mapX;
 t194_life.call.x=t194_events[event-1].d[1]-(mapX-1)*24-12;t194_life.call.y=-28;
 return t194_life.call.token;
}
void render_mirror_tank194_family_enemy_allocated(void *p,unsigned record,int unique)
{
 t194_repeat8_observe();
 int s=t194_slot(p);if(s<0)return;
 render_mirror_tank194_family_retired((unsigned)s);
 if(t194_slots[s].generation==UINT64_MAX){t194_slots[s].exhausted=true;return;}
 if(t194_slots[s].exhausted)return;
 ++t194_slots[s].generation;
 if(t194_life.call.live&&t194_scope()&&s>=75&&enemyAvail[s]==1&&!unique&&record==194&&t194_life.call.slot==-1){
  t194_slots[s].pending=true;t194_life.call.slot=s;t194_life.call.generation=t194_slots[s].generation;
 }
}
void render_mirror_tank194_family_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 t194_repeat8_observe();
 int s=t194_slot(p);if(s<0)return;
 t194_slots[s].initialized=t194_slots[s].pending&&t194_life.call.live&&t194_scope()&&
 t194_life.call.slot==s&&t194_life.call.generation==t194_slots[s].generation&&
 record==194&&avail==0&&enemyAvail[s]==1&&t194_shape((unsigned)s,1);
}
void render_mirror_tank194_family_event_commit(uint64_t token,unsigned one_based)
{
 t194_repeat8_observe();
 if(!token)return;
 int s=t194_life.call.slot;
 bool ok=t194_life.call.live&&token==t194_life.call.token&&t194_life.call.epoch==t194_life.epoch&&t194_scope()&&
 s>=75&&s<100&&one_based==(unsigned)s+1&&eventLoc==t194_life.call.event&&
 curLoc==t194_events[t194_life.call.event-1].time&&mapX==t194_life.call.map1;
 if(ok)ok=t194_slots[s].pending&&t194_slots[s].initialized&&t194_life.call.generation==t194_slots[s].generation&&
 enemyAvail[s]==0&&t194_shape((unsigned)s,2)&&enemy[s].ex==t194_life.call.x&&enemy[s].ey==t194_life.call.y&&
 enemy[s].linknum==t194_events[t194_life.call.event-1].d[3];
 if(s>=0&&s<100){
  t194_slots[s].live=ok;t194_slots[s].pending=t194_slots[s].initialized=false;
  if(ok){t194_slots[s].witness=t194_slots[s].generation;t194_slots[s].bank=enemy[s].sprite2s;
   t194_slots[s].data=enemy[s].sprite2s->data;t194_slots[s].bytes=enemy[s].sprite2s->size;
   t194_slots[s].script=t194_script((unsigned)s);t194_slots[s].script_event=eventLoc;t194_slots[s].script_serial=1;
   t194_slots[s].birth_armor=enemy[s].armorleft;t194_slots[s].birth_value=enemy[s].evalue;
   t194_slots[s].birth=(Tank194Birth){.epoch=t194_life.epoch,.token=token,.generation=t194_slots[s].generation,
    .slot=(unsigned)s,.event=t194_life.call.event,.record=194,.bank_role=20,.bank_bytes=46204,.link=enemy[s].linknum,
    .bank_stamp=UINT64_C(0xe2413e3aeab4d908),.record_stamp=UINT64_C(0xa9beba644b307039),
    .bank_object=(uintptr_t)t194_slots[s].bank,.bank_data=(uintptr_t)t194_slots[s].data,
    .event_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 t194_life.call.live=false;
}
void render_mirror_tank194_family_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(t194_slots[i].live&&t194_slots[i].bank==bank){++t194_bank_losses;render_mirror_tank194_family_retired(i);}
 if(t194_life.call.live){t194_life.call.live=false;t194_fail(4);}
}
static void t194_tick(void)
{
 if(t194_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&t194_frame,0,sizeof t194_frame);memset(t194_owned,0,sizeof t194_owned);memset(t194_shadows,0,sizeof t194_shadows);t194_first_reason=0;
 if(t194_life.loaded&&!t194_scope()){t194_reset();t194_life.loaded=false;return;}
 for(unsigned i=75;i<100;i++)if(t194_slots[i].live&&(!t194_witness(i)||!t194_shape(i,0)))render_mirror_tank194_family_retired(i);
}
static bool t194_load(void)
{
 for(unsigned p=0;p<8;p++){
  char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
  int n=snprintf(path,sizeof path,"%s/enemy-newsh2-%u-8.hda",t194_resources.root,t194_art[p]);
  if(n<0||(size_t)n>=sizeof path)return false;
  int fd=REAR_OPEN(path);if(fd<0)return false;
  const size_t bytes=172032;
  bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
  REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
  uint32_t v[6]={0};
  if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
   ok=v[0]==1010000+t194_art[p]&&v[1]==8&&v[2]==24&&v[3]==28&&v[4]==6&&v[5]==7;}
  if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
  if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==t194_art_stamp[p];
  if(REAR_CLOSE(fd))ok=false;
  if(!ok){free(rgba);return false;}
  t194_resources.member[p]=(Asset){true,true,ASSET_NEWSH2,(int)t194_art[p],24,28,6,7,8,rgba};
 }
 return true;
}
static bool t194_resources_current(void)
{
 if(!t194_resources.checked||!t194_resources.valid||strcmp(t194_resources.root,t194_root()))return false;
 for(unsigned p=0;p<8;p++){
  const Asset *a=t194_resources.member+p;
  if(!a->initialized||!a->valid||a->bank!=ASSET_NEWSH2||a->index!=(int)t194_art[p]||a->w!=24||a->h!=28||
  a->anchor_x!=6||a->anchor_y!=7||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,172032)!=t194_art_stamp[p])return false;
 }
 return true;
}
static bool t194_ready(void)
{
 if(!t194_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!t194_resources.checked){t194_resources.checked=true;strcpy(t194_resources.root,t194_life.root);t194_resources.valid=t194_load();}
 if(!t194_resources_current()){t194_resources.valid=false;return false;}
 return true;
}
static void t194_shutdown(void)
{
 t194_reset();t194_life.loaded=false;
 for(unsigned p=0;p<8;p++)free(t194_resources.member[p].rgba);
 memset(&t194_resources,0,sizeof t194_resources);
}
static bool t194_dependencies(bool partial)
{
 if(!t194_frame.contributed)return true;
 if(t194_frame.fault||!t194_scope()||!t194_colors()||!t194_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<25;i++)if(t194_frame.draw[i].token){const Tank194Draw *d=t194_frame.draw+i;unsigned s=i+75;
  if(!t194_witness(s)||!t194_shape(s,0)||d->generation!=t194_slots[s].generation||
  d->script_serial!=t194_slots[s].script_serial||d->script_event!=t194_slots[s].script_event||
  d->pose>=8||d->base!=t194_bases[d->pose]||d->pose+1!=enemy[s].enemycycle||
  d->token!=t194_slots[s].birth.token||d->epoch!=t194_life.epoch||d->event!=t194_slots[s].birth.event||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data)return false;
  if(!d->complete){if(!partial||!t194_frame.pending||t194_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->pose>=8||d->callback_count!=t194_totals[d->pose])return false;
 }
 return partial||(!t194_frame.active&&!t194_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool t194_finish(void){return t194_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool t194_guard(void)
{
 t194_repeat8_observe();
 if(t194_finish())return true;
 t194_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool t194_before_tile(unsigned slot,int part)
{
 t194_repeat8_observe();
 if(slot>=75&&slot<100&&t194_slots[slot].live&&
 (!t194_scope()||!t194_witness(slot)||!t194_shape(slot,0))){
  render_mirror_tank194_family_retired(slot);
  if(t194_frame.contributed)t194_fail(5);
  return false;
 }
 if(t194_frame.contributed&&!t194_dependencies(true)){t194_fail(5);return false;}
 if(t194_frame.pending&&(t194_frame.active||slot!=t194_frame.slot||
 t194_frame.draw[slot-75].next>=4||part!=(int)t194_parts[t194_frame.draw[slot-75].next])){t194_fail(6);return false;}
 return true;
}
static bool t194_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool t194_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 t194_repeat8_observe();
 if(!t194_enabled()||slot<75||slot>=100||enemy[slot].enemytype!=194)return false;
 if(!fc.frame_active||fc.frame_failed)return false; /* Frame availability is not lifetime evidence. */
 if(!t194_witness(slot)){
  ++t194_unwitnessed;
  if(t194_slots[slot].live){
   render_mirror_tank194_family_retired(slot);
   if(t194_frame.contributed)t194_fail(9);
  }
  return false; /* Unselected original births remain ordinary classic. */
 }
 unsigned k;for(k=0;k<4&&part!=(int)t194_parts[k];k++);
 if(k==4){render_mirror_tank194_family_retired(slot);if(t194_frame.contributed)t194_fail(7);return false;}
 int64_t ox=(int64_t)x-t194_px[k],oy=(int64_t)y-t194_py[k];
 Tank194Draw *d=t194_frame.draw+slot-75;
 /* Observed identity/shape/origin/filter failures retire this generation even
  * before its first contribution. Native filter clearing cannot re-admit it. */
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !t194_scope()||sheet!=enemy[slot].sprite2s||!t194_shape(slot,0)||base!=t194_bases[enemy[slot].enemycycle-1]){
  render_mirror_tank194_family_retired(slot);
  if(t194_frame.contributed)t194_fail(9);
  return false;
 }
 /* Ordinary entering/leaving geometry and cold/per-frame material availability
  * do not revoke an otherwise proven native lifetime. */
 if(!t194_geometry(ox,oy)){++t194_clipped;if(d->token)t194_fail(8);return false;}
 if(!t194_colors()||!t194_ready()){
  if(d->token||t194_frame.contributed)t194_fail(9);
  return false;
 }
 if(k==0){if(d->token||t194_frame.pending){t194_fail(10);return false;}}
 else if(!t194_frame.pending||t194_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||t194_frame.pending)t194_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||t194_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++t194_contract_faults;t194_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++t194_contract_faults;t194_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(Tank194Draw){.frame=fc_frame,.epoch=t194_life.epoch,.token=t194_slots[slot].birth.token,
   .generation=t194_slots[slot].generation,.slot=slot,.event=t194_slots[slot].birth.event,.record=194,
   .base=base,.pose=enemy[slot].enemycycle-1,.script_serial=t194_slots[slot].script_serial,.script_event=t194_slots[slot].script_event,.cur_loc=curLoc,.bank_role=20,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  t194_frame.pending=true;t194_frame.slot=slot;
 }
 d->part_order[k]=(unsigned)part;
 t194_frame.part=k;t194_frame.pixels=0;t194_frame.active=true;t194_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool t194_retire(unsigned off,int style)
{
 bool owned=off<64000&&t194_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++t194_blend_retirements;else ++t194_normal_retirements;
 t194_owned[off]=t194_shadows[off]=0;}
 return owned;
}
static bool t194_pixel(unsigned x,unsigned y,int style)
{
 if(!t194_frame.active){if(t194_frame.pending){t194_fail(14);return true;}return false;}
 Tank194Draw *d=t194_frame.draw+t194_frame.slot-75;
 unsigned k=t194_frame.part;
 if(k>=4||d->pose>=8||t194_frame.pixels>=t194_counts[d->pose][k]){++t194_contract_faults;t194_fail(15);return true;}
 const Tank194Write *w=t194_native[d->pose][k]+t194_frame.pixels;
 unsigned lx=t194_px[k]+w->x,ly=t194_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++t194_contract_faults;t194_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=t194_resources.member+d->pose;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 t194_owned[off]=(uint8_t)(t194_frame.slot+1);t194_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=168){t194_fail(17);return true;}
 t194_frame.writes[t194_frame.slot-75][d->callback_count++]=(Tank194Write){(uint8_t)lx,(uint8_t)ly,w->index};
 ++t194_frame.pixels;d->part_count[k]=t194_frame.pixels;return true;
}
static void t194_shadow(unsigned off)
{
 if(off<64000&&t194_owned[off]){if(t194_shadows[off]<255)++t194_shadows[off];++t194_shadow_writes;}
}
static void t194_end(void)
{
 if(!t194_frame.active)return;
 unsigned k=t194_frame.part;Tank194Draw *d=t194_frame.draw+t194_frame.slot-75;
 if(k>=4||d->pose>=8||d->next!=k||d->mask!=(1u<<k)-1||t194_frame.pixels!=t194_counts[d->pose][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++t194_contract_faults;t194_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;t194_frame.active=false;
 if(k==3){d->complete=d->mask==15&&d->callback_count==t194_totals[d->pose];t194_frame.pending=false;if(!d->complete)t194_fail(19);}
}
static void t194_accept(void){t194_frame.accepted=fc.ready&&!fc.frame_failed&&t194_finish();}
Tank194FamilyStatus render_mirror_tank194_family_status(void)
{
 Tank194FamilyStatus s={0};s.requested=t194_enabled();s.loaded=t194_life.loaded;s.contributed=t194_frame.contributed;
 s.failed=fc.frame_failed||t194_frame.fault;s.accepted=t194_frame.accepted;s.frame=fc_frame;
 s.active=t194_frame.active;s.pending=t194_frame.pending;s.active_slot=t194_frame.slot;
 s.active_part=t194_frame.part<4?t194_parts[t194_frame.part]:UINT_MAX;s.consumed_events=t194_life.consumed;
 s.blend_retirements=t194_blend_retirements;s.normal_retirements=t194_normal_retirements;s.shadow_writes=t194_shadow_writes;
 s.clipped=t194_clipped;s.unwitnessed=t194_unwitnessed;s.lifetime_losses=t194_lifetime_losses;s.bank_losses=t194_bank_losses;
 s.contract_faults=t194_contract_faults;s.first_reason=t194_first_reason;
 s.script_losses=t194_script_losses;s.next_event=t194_life.next_event;s.mutable_event31_result=t194_life.mutated31;
 for(unsigned i=0;i<25;i++)s.births[i]=t194_slots[i+75].birth;
 memcpy(s.draw,t194_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=t194_owned[i]!=0;s.shadowed_cells+=t194_owned[i]&&t194_shadows[i];}return s;
}
bool render_mirror_tank194_family_pre_draw(Tank194Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!t194_frame.active||t194_frame.part||t194_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=t194_frame.draw[t194_frame.slot-75];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_tank194_family_pre_part(Tank194Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!t194_frame.active||t194_frame.pixels||
 t194_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=t194_frame.draw[t194_frame.slot-75];unsigned k=t194_frame.part;*part=t194_parts[k];
 unsigned x=(unsigned)d->x+t194_px[k],y=(unsigned)d->y+t194_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_tank194_family_callbacks(unsigned slot,Tank194Write *out,size_t capacity)
{
 if(slot<75||slot>=100||!out||capacity<t194_frame.draw[slot-75].callback_count)return 0;
 unsigned n=t194_frame.draw[slot-75].callback_count;memcpy(out,t194_frame.writes[slot-75],n*sizeof *out);return n;
}
bool render_mirror_tank194_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!t194_frame.accepted||fc.frame_active||fc.frame_failed||
 !t194_frame.contributed||!t194_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,t194_owned,64000);memcpy(shadows,t194_shadows,64000);return true;
}

/* Pure OFF/ON diagnostic of the actual ordered canvas. Never prepares a
 * canvas, changes readiness, invokes a mutating guard or admits a material. */
bool render_mirror_tank194_family_canvas_part(int x,int y,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!argb||count!=10752||!native||bytes!=168||x<0||x>308||y<0||y>186||
 !fc.frame_active||fc.frame_failed||!fc_canvas_ready||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_draw(fc_frame))return false;
 for(unsigned row=0;row<14;row++)if(memcmp(expected+(y+row)*320+x,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12))return false;
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
