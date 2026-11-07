/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private, default-OFF observer. Included only by tyrian2.c.
 * No drawing, assets, file IO, native-state writes, RNG or sound calls.
 * The normal record fields below are the mapper's sparse byte scope only.
 */
#include "launcher271_lineage.h"
#include "xmas.h"
extern struct JE_EventRecType eventRec[EVENT_MAXIMUM];
enum { L271_NATIVE_RETIRE=1,L271_REALLOCATE,L271_POOL_RESET,L271_BANK_CHANGE,
       L271_LEVEL_END,L271_NATIVE_AVAILABILITY };
static Launcher271Status l271;
static struct {
 uint64_t generation;
 bool allocated,initialized,live,present;
 unsigned record;
 int unique;
 const Sprite2_array *bank;
 const void *data;
 size_t bytes;
 Launcher271Birth birth;
 uint64_t retired_frame;
 unsigned retirement_reason;
} l271_slot[100];
static struct {
 bool active,initialized,returned;
 unsigned kind,event,parent,pool,record,allocations,slot;
 uint64_t token,generation,allocation_start,epoch;
 int result,x,y;
 Launcher271Birth parent_birth;
 unsigned cycle,base;
} l271_call;

static bool l271_requested(void)
{ const char *v=getenv("LAUNCHER271_LINEAGE_ENABLE");return v&&!strcmp(v,"1"); }
static bool l271_ordinary(void)
{
 return episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!record_demo&&!stopped_demo&&!game_probe_enabled&&!asset_debug_enabled&&
 !isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!xmas&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static bool l271_scope(void)
{ return l271.enabled&&l271.loaded&&!l271.exhausted&&l271_requested()&&l271_ordinary(); }
static bool l271_increment(uint64_t *n)
{ if(*n==UINT64_MAX){l271.exhausted=true;return false;}++*n;return true; }
static bool l271_event(unsigned event)
{
 static const int x[4]={42,66,234,258};
 if(maxEvent!=731||event<493||event>496)return false;
 const struct JE_EventRecType *r=eventRec+event-1;
 return r->eventtime==4920&&r->eventtype==6&&r->eventdat==271&&
 r->eventdat2==x[event-493]&&!r->eventdat3&&!r->eventdat4&&!r->eventdat5&&!r->eventdat6;
}
static bool l271_records(void)
{
 static const unsigned records[2]={271,463};
 static const unsigned sequence[2][20]={{275,277,279,277,275},{191}};
 for(unsigned k=0;k<2;k++){
  unsigned r=records[k];
  if(enemyDat[r].ani!=(k?1:5)||enemyDat[r].esize!=1||enemyDat[r].animate!=(k?0:2)||
     enemyDat[r].shapebank!=8||enemyDat[r].xmove||enemyDat[r].ymove!=(k?4:0)||
     enemyDat[r].xaccel||enemyDat[r].yaccel||enemyDat[r].xcaccel||enemyDat[r].ycaccel||
     enemyDat[r].startx||enemyDat[r].starty||enemyDat[r].startxc||enemyDat[r].startyc||
     enemyDat[r].xrev||enemyDat[r].yrev||enemyDat[r].elaunchfreq!=(k?0:40)||
     enemyDat[r].elaunchtype!=(k?0:463))return false;
  for(unsigned j=0;j<3;j++)if(enemyDat[r].tur[j]||enemyDat[r].freq[j])return false;
  for(unsigned j=0;j<20;j++)if(enemyDat[r].egraphic[j]!=sequence[k][j])return false;
 }
 return true;
}
static bool l271_bank(void)
{
 const Sprite2_array *s=enemySpriteSheets;
 if(enemySpriteSheetIds[0]!=8||!s->data||s->size!=42012)return false;
 for(unsigned k=1;k<4;k++)if(enemySpriteSheetIds[k]==8)return false;
 uint64_t hash=UINT64_C(14695981039346656037);
 for(size_t k=0;k<s->size;k++){hash^=s->data[k];hash*=UINT64_C(1099511628211);}
 return hash==UINT64_C(0x913975450e0fc00d);
}
static bool l271_actor(unsigned slot,unsigned record)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=record||e->enemydatofs!=enemyDat+record||e->sprite2s!=enemySpriteSheets||
    e->size!=1||e->exc||e->eyc!=(record==463?4:0)||e->excc||e->eycc||
    e->xaccel||e->yaccel||e->fixedmovey||e->linknum||e->launchspecial||
    e->launchfreq!=(record==463?0:40)||e->launchtype!=(record==463?0:463))return false;
 for(unsigned k=0;k<20;k++)if(e->egr[k]!=enemyDat[record].egraphic[k])return false;
 return true;
}
static bool l271_current(unsigned slot)
{
 if(!l271_scope()||slot>=100||!l271_slot[slot].live||enemyAvail[slot]==1)return false;
 const Launcher271Birth *b=&l271_slot[slot].birth;
 const struct JE_SingleEnemyType *e=enemy+slot;
 return b->session==l271.session&&b->generation==l271_slot[slot].generation&&
 b->resource_epoch==l271.resource_epoch&&e->enemytype==b->record&&
 e->enemydatofs==enemyDat+b->record&&e->sprite2s==l271_slot[slot].bank&&
 enemySpriteSheetIds[0]==8&&enemySpriteSheets[0].data==l271_slot[slot].data&&
 enemySpriteSheets[0].size==l271_slot[slot].bytes;
}
static void l271_retire(unsigned slot,unsigned reason)
{
 if(!l271.enabled||slot>=100)return;
 if(l271_slot[slot].live){
  l271_slot[slot].retired_frame=l271.frame;l271_slot[slot].retirement_reason=reason;
  l271_increment(&l271.retirements);
 }
 l271_slot[slot].live=l271_slot[slot].allocated=l271_slot[slot].initialized=false;
}
static void l271_retire_all(unsigned reason)
{ if(l271.enabled)for(unsigned k=0;k<100;k++)l271_retire(k,reason);l271_call.active=false; }
static void l271_finish(void)
{ l271_retire_all(L271_LEVEL_END);l271.loaded=false; }
static void l271_level_begin(char map,char shape)
{
 l271_finish();
 uint64_t session=l271.session;
 bool exhausted=l271.exhausted;
 memset(&l271,0,sizeof l271);memset(l271_slot,0,sizeof l271_slot);memset(&l271_call,0,sizeof l271_call);
 l271.session=session;l271.exhausted=exhausted;l271.enabled=l271_requested();
 if(!l271.enabled||!l271_increment(&l271.session)||!l271_ordinary()||map!='D'||shape!='Z'||
    mapX!=1||mapX2!=1||mapX3!=1||!l271_records())return;
 for(unsigned k=493;k<=496;k++)if(!l271_event(k))return;
 const struct JE_EventRecType *r=eventRec+1;
 if(r->eventtime||r->eventtype!=5||r->eventdat!=8||r->eventdat2!=23||r->eventdat3!=20||
    r->eventdat4!=17||r->eventdat5||r->eventdat6)return;
 l271.loaded=true;
}
static void l271_bank_change(unsigned bank)
{
 if(!l271.enabled||bank!=0)return;
 l271_retire_all(L271_BANK_CHANGE);l271_increment(&l271.resource_epoch);
}
static void l271_reconcile(void)
{
 if(!l271.enabled)return;
 for(unsigned k=0;k<100;k++)if(l271_slot[k].live&&!l271_current(k))
  l271_retire(k,L271_NATIVE_AVAILABILITY);
}
static void l271_frame_begin(void)
{ if(l271_scope()){l271_reconcile();l271_increment(&l271.frame);} }
static int l271_object_slot(const void *object)
{
 /* Compare exact object addresses, never infer from position or record. */
 for(unsigned k=0;k<100;k++)if(object==enemy+k)return (int)k;
 return -1;
}
static void l271_allocated(const void *object,unsigned record,int unique)
{
 if(!l271_scope())return;
 int slot=l271_object_slot(object);if(slot<0){l271_call.active=false;return;}
 l271_retire((unsigned)slot,L271_REALLOCATE);
 uint64_t generation=l271_slot[slot].generation;
 memset(l271_slot+slot,0,sizeof l271_slot[slot]);l271_slot[slot].generation=generation;
 if(!l271_increment(&l271_slot[slot].generation)||!l271_increment(&l271.allocation_serial))return;
 l271_slot[slot].record=record;l271_slot[slot].unique=unique;
 l271_slot[slot].allocated=enemyAvail[slot]==1;
 if(!l271_call.active)return;
 ++l271_call.allocations;
 if(l271_call.allocations!=1||!l271_slot[slot].allocated||unique||record!=l271_call.record||
    slot<(int)l271_call.pool||slot>=(int)l271_call.pool+25){l271_call.active=false;return;}
 l271_call.slot=(unsigned)slot;l271_call.generation=l271_slot[slot].generation;
}
static void l271_initialized(const void *object,unsigned record,unsigned avail)
{
 if(!l271_scope()||!l271_call.active||l271_call.allocations!=1)return;
 int slot=l271_object_slot(object);
 if(slot!=(int)l271_call.slot||record!=l271_call.record||avail==1||
    l271_slot[slot].generation!=l271_call.generation||!l271_records()||!l271_bank()||
    !l271_actor((unsigned)slot,record))return;
 l271_call.initialized=l271_slot[slot].initialized=true;
}
static uint64_t l271_event_begin(unsigned event)
{
 l271_call.active=false;
 if(!l271_scope()||eventLoc!=event||!l271_event(event)||curLoc<4920||
    (l271.event_consumed&(1u<<(event-493)))||!l271_records()||!l271_bank())return 0;
 l271.event_consumed|=1u<<(event-493);
 if(!l271_increment(&l271.serial))return 0;
 memset(&l271_call,0,sizeof l271_call);
 l271_call.active=true;l271_call.kind=1;l271_call.token=l271.serial;l271_call.event=event;
 l271_call.pool=25;l271_call.record=271;l271_call.allocation_start=l271.allocation_serial;
 l271_call.epoch=l271.resource_epoch;return l271_call.token;
}
static bool l271_commit_ready(uint64_t token,int result)
{
 return token&&l271_scope()&&l271_call.active&&l271_call.token==token&&
 l271_call.allocations==1&&l271_call.initialized&&result>0&&result<=100&&
 (unsigned)(result-1)==l271_call.slot&&l271.allocation_serial==l271_call.allocation_start+1&&
 l271_slot[result-1].generation==l271_call.generation&&l271_slot[result-1].initialized&&
 enemyAvail[result-1]!=1&&l271.resource_epoch==l271_call.epoch&&l271_records()&&l271_bank()&&
 l271_actor((unsigned)(result-1),l271_call.record);
}
static void l271_store(unsigned slot,Launcher271Birth birth)
{
 l271_slot[slot].birth=birth;l271_slot[slot].live=l271_slot[slot].present=true;
 l271_slot[slot].bank=enemy[slot].sprite2s;l271_slot[slot].data=enemy[slot].sprite2s->data;
 l271_slot[slot].bytes=enemy[slot].sprite2s->size;
}
static void l271_event_commit(uint64_t token,int result)
{
 if(!token)return;
 if(l271_commit_ready(token,result)&&l271_call.kind==1&&l271_event(l271_call.event)){
  unsigned slot=(unsigned)result-1;const struct JE_SingleEnemyType *e=enemy+slot;
  if(e->ex==eventRec[l271_call.event-1].eventdat2-(mapX-1)*24-12&&e->ey==-28){
   Launcher271Birth birth={.session=l271.session,.token=token,.generation=l271_call.generation,
    .frame=l271.frame,.resource_epoch=l271.resource_epoch,.slot=slot,.record=271,
    .event=l271_call.event,.parent_slot=100,.bank=8,.physical_bank=0,
    .allocation_result=result,.x=e->ex,.y=e->ey,.source_cycle=e->enemycycle,
    .source_base=e->egr[0]};
   l271_store(slot,birth);l271_increment(&l271.parents);
  }
 }
 l271_call.active=false;
}
static uint64_t l271_launch_begin(unsigned parent,int pool,unsigned record)
{
 l271_call.active=false;
 if(!l271_scope()||parent<25||parent>=50||pool!=75||record!=463||!l271_current(parent)||
    l271_slot[parent].birth.record!=271||!l271_actor(parent,271)||!l271_records()||!l271_bank())return 0;
 const struct JE_SingleEnemyType *e=enemy+parent;
 if(e->enemycycle<1||e->enemycycle>5)return 0;
 if(!l271_increment(&l271.serial)||!l271_increment(&l271.launch_attempts))return 0;
 memset(&l271_call,0,sizeof l271_call);
 l271_call.active=true;l271_call.kind=2;l271_call.token=l271.serial;
 l271_call.parent=parent;l271_call.parent_birth=l271_slot[parent].birth;
 l271_call.pool=75;l271_call.record=463;l271_call.allocation_start=l271.allocation_serial;
 l271_call.epoch=l271.resource_epoch;l271_call.x=e->ex;l271_call.y=e->ey;
 l271_call.cycle=e->enemycycle;l271_call.base=e->egr[e->enemycycle-1];
 return l271_call.token;
}
static void l271_launch_return(uint64_t token,int result)
{
 if(!token||!l271_call.active||l271_call.token!=token||l271_call.kind!=2)return;
 l271_call.returned=true;l271_call.result=result;l271.last_allocation_result=result;
 if(result==0)l271_increment(&l271.no_child_results);
}
static void l271_launch_commit(uint64_t token,int result)
{
 if(!token)return;
 if(l271_commit_ready(token,result)&&l271_call.kind==2&&l271_call.returned&&
    l271_call.result==result&&l271_current(l271_call.parent)&&
    l271_slot[l271_call.parent].generation==l271_call.parent_birth.generation){
  unsigned slot=(unsigned)result-1;const struct JE_SingleEnemyType *e=enemy+slot;
  if(e->ex==l271_call.x&&e->ey==l271_call.y){
   Launcher271Birth birth={.session=l271.session,.token=token,.generation=l271_call.generation,
    .frame=l271.frame,.resource_epoch=l271.resource_epoch,
    .parent_token=l271_call.parent_birth.token,.parent_generation=l271_call.parent_birth.generation,
    .parent_frame=l271_call.parent_birth.frame,.slot=slot,.record=463,
    .event=l271_call.parent_birth.event,.parent_slot=l271_call.parent,.bank=8,.physical_bank=0,
    .allocation_result=result,.x=e->ex,.y=e->ey,.parent_x=l271_call.x,.parent_y=l271_call.y,
    .source_cycle=l271_call.cycle,.source_base=l271_call.base};
   l271_store(slot,birth);l271_increment(&l271.children);
  }
 }
 l271_call.active=false;
}
Launcher271Receipt launcher271_lineage_receipt(unsigned slot)
{
 Launcher271Receipt r={0};if(slot>=100||!l271.enabled)return r;
 r.present=l271_slot[slot].present;r.current=l271_current(slot);r.birth=l271_slot[slot].birth;
 r.retired_frame=l271_slot[slot].retired_frame;r.retirement_reason=l271_slot[slot].retirement_reason;
 return r;
}
Launcher271Status launcher271_lineage_status(void){return l271;}
