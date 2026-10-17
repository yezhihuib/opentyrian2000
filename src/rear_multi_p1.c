/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite renderer provenance. The inputs are observations, never game writers. */
#include "rear_multi_p1.h"
#include <string.h>
/* Separate index spaces preserve every existing resource/cache and source pin.
 * Observed-only 163/164 must never become drawable through prefix growth. */
static const unsigned drawable_ids[REAR_P1_HEADS]={39,1,281,282,301,300,40,2,77,182,183,277,278,41,3,296,297,294,295};
static const unsigned ids[REAR_P1_OBSERVED]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278,41,3,296,297,294,295};
static const int velocity[REAR_P1_OBSERVED][2]={{-10,0},{10,0},{-9,-2},{9,-2},{9,2},{-9,2},{-10,0},{10,0},{0,10},{-6,6},{6,6},{-6,-6},{6,-6},{-9,-2},{9,-2},{-10,0},{10,0},{-9,2},{9,2},{-6,6},{6,6}};
uint64_t rear_p1_stamp(const void *data,size_t size)
{
 const uint8_t *p=data;uint64_t h=UINT64_C(14695981039346656037);
 for(size_t i=0;i<size;i++)h=(h^p[i])*UINT64_C(1099511628211);
 return h;
}
int rear_p1_member(unsigned raw)
{for(unsigned i=0;i<REAR_P1_HEADS;i++)if(drawable_ids[i]==raw)return (int)i;return -1;}
int rear_p1_observed(unsigned raw)
{for(unsigned i=0;i<REAR_P1_OBSERVED;i++)if(ids[i]==raw)return (int)i;return -1;}
void rear_p1_reset(RearP1State *s)
{uint64_t g=s->generation+1,c=s->call_serial;memset(s,0,sizeof(*s));s->generation=g?g:1;s->call_serial=c;}
void rear_p1_call_end(RearP1State *s)
{s->pending=false;s->lease=false;s->call=0;s->budget=0;s->remaining=0;s->next_ordinal=0;s->next_phase=0;s->used_count=0;memset(s->used_slots,0,sizeof(s->used_slots));}
void rear_p1_call_begin(RearP1State *s,uint64_t tick,unsigned port,unsigned bay,
 unsigned power_index,unsigned mode_index,unsigned player,unsigned record,bool scope,bool table)
{
 rear_p1_call_end(s);
 s->pending=scope&&table&&port==10&&bay==1&&player==1&&
  ((power_index==0&&((mode_index==0&&record==254)||(mode_index==1&&record==265)))||
   (power_index==1&&((mode_index==0&&record==255)||(mode_index==1&&record==266)))||
   (power_index==2&&((mode_index==0&&record==256)||(mode_index==1&&record==267)))||
   (power_index==3&&((mode_index==0&&record==257)||(mode_index==1&&record==268)))||
   (power_index==4&&((mode_index==0&&record==258)||(mode_index==1&&record==269)))||
   (power_index==5&&((mode_index==0&&record==259)||(mode_index==1&&record==270)))||
   (power_index==6&&((mode_index==0&&record==260)||(mode_index==1&&record==271)))||
   (power_index==7&&((mode_index==0&&record==261)||(mode_index==1&&record==272)))||
   (power_index==8&&mode_index==0&&record==262));
 s->tick=tick;s->record=record;s->mode=mode_index+1;
 /* Exact record budgets: P3=2/4, P4=5/5, P5=2/4; P6=3/5; P7=4/5; P8=6/7; P9 mode1=6. */
 if(s->pending)s->budget=record==262?6:record==272?7:record==261?6:record==260?4:record==259?3:(record==257||record==268||record==270||record==271)?5:(record==256||record==258)?2:(record==267||record==269)?4:power_index+1;
}
uint64_t rear_p1_create_begin(RearP1State *s,uint64_t tick,unsigned port,unsigned bay,
 unsigned record,unsigned player)
{
 /* Every actual invocation claims or destroys the pending grant. Nested and
  * unwrapped calls cannot borrow an outer call, even with an identical tuple. */
 bool allowed=s->pending&&s->tick==tick&&port==10&&bay==1&&player==1&&record==s->record;
 unsigned budget=s->budget;rear_p1_call_end(s);
 if(++s->call_serial==0)++s->call_serial;
 s->call=s->call_serial;s->lease=allowed;
 if(allowed){s->remaining=budget;s->next_ordinal=1;}
 return s->call;
}
void rear_p1_create_end(RearP1State *s,uint64_t call)
{if(s->call==call)rear_p1_call_end(s);}
static bool shot_ok(const RearP1Shot *s,unsigned raw)
{
 int k=rear_p1_observed(raw);
 return k>=0&&s&&s->gr==raw&&!s->ani&&s->ani_max==1&&s->player==1&&
  s->trail==255&&!s->aim&&!s->chain&&!s->complicated&&s->filter==208&&
  s->xm==velocity[k][0]&&s->ym==velocity[k][1]&&!s->xc&&!s->yc;
}
static bool phase_ok(unsigned record,unsigned phase,unsigned raw)
{
 if(record==254||record==255)return phase>=1&&phase<=2&&raw==ids[phase-1];
 if(record==256)return phase>=1&&phase<=2&&raw==ids[phase+5];
 if(record==258)return phase>=1&&phase<=2&&raw==(phase==1?41u:3u);
 if(record==259) {
  static const unsigned observed[3]={41,3,77};
  return phase>=1&&phase<=3&&raw==observed[phase-1];
 }
 if(record==260) {
  static const unsigned observed[4]={277,278,297,296};
  return phase>=1&&phase<=4&&raw==observed[phase-1];
 }
 if(record==261) {
  static const unsigned observed[6]={277,278,297,296,39,1};
  return phase>=1&&phase<=6&&raw==observed[phase-1];
 }
 if(record==262) {
  static const unsigned observed[6]={277,278,297,296,41,3};
  return phase>=1&&phase<=6&&raw==observed[phase-1];
 }
 if(record==272) {
  static const unsigned observed[7]={277,278,295,294,77,39,1};
  return phase>=1&&phase<=7&&raw==observed[phase-1];
 }
 if(record==271) {
  static const unsigned observed[5]={277,278,295,294,77};
  return phase>=1&&phase<=5&&raw==observed[phase-1];
 }
 if(record==270) {
  static const unsigned observed[5]={277,278,183,182,77};
  return phase>=1&&phase<=5&&raw==observed[phase-1];
 }
 if(record==269) {
  static const unsigned observed[4]={277,278,183,182};
  return phase>=1&&phase<=4&&raw==observed[phase-1];
 }
 if(record==268) {
  static const unsigned observed[5]={163,164,183,182,77};
  return phase>=1&&phase<=5&&raw==observed[phase-1];
 }
 if(record==257)return phase>=1&&phase<=5&&raw==ids[phase==5?8:phase+1];
 return (record==265||record==266||record==267)&&phase>=1&&phase<=4&&raw==ids[phase+1];
}
/* Same-mode records can share canonical phases (268/269: 183/182).
 * Retain the original admitted identity rather than reclassifying a birth.
 * Fixed-width values exclude structure padding; this is an integrity check,
 * not a cryptographic boundary against coordinated memory corruption. */
static uint64_t birth_stamp(const RearP1Birth *b,unsigned slot)
{
 const uint64_t fields[]={b->record,b->mode,b->phase,b->raw,b->generation,slot};
 return rear_p1_stamp(fields,sizeof(fields));
}
void rear_p1_emit(RearP1State *s,uint64_t tick,uint64_t call,unsigned ordinal,unsigned slot,unsigned port,unsigned bay,
 unsigned record,unsigned player,unsigned phase,unsigned raw,const RearP1Shot *shot,bool scope,bool table,bool source)
{
 /* Consume before validation, including rejected/zero-graphics/out-of-range
  * allocations. The first canonical phase can start anywhere in the cycle:
  * a prior partial-capacity call advances the original phase only once. */
 bool lease=s->lease&&s->remaining>0;
 if(s->remaining)--s->remaining;
 if(slot<REAR_P1_SLOTS){memset(&s->birth[slot],0,sizeof(s->birth[slot]));s->birth_identity[slot]=0;}
 unsigned period=s->record==262?6:s->record==272?7:s->record==261?6:s->record==260?4:s->record==259?3:(s->record==257||s->record==268||s->record==270||s->record==271)?5:s->mode==1?2:4;
 bool reused=false;
 for(unsigned i=0;i<s->used_count&&i<REAR_P1_MAX_BUDGET;i++)reused|=s->used_slots[i]==slot;
 if(!lease||s->call!=call||s->tick!=tick||ordinal!=s->next_ordinal||
  !scope||!table||port!=10||bay!=1||player!=1||record!=s->record||
  phase<1||phase>period||(s->next_phase&&phase!=s->next_phase)||
  (s->used_count>=REAR_P1_MAX_BUDGET||reused)) {
  rear_p1_call_end(s);return;
 }
 s->next_ordinal++;s->next_phase=phase==period?1:phase+1;
 if(!s->remaining)s->lease=false;
 if(slot>=REAR_P1_SLOTS||!source||!phase_ok(record,phase,raw)||!shot_ok(shot,raw)) {
  rear_p1_call_end(s);return;
 }
 s->used_slots[s->used_count++]=slot;
 /* Canonical 163/164 consume the call without claiming the rear role.
  * Their generic normal/head/shadow paths remain the original paths. */
 if(rear_p1_member(raw)<0)return;
 s->birth[slot]=(RearP1Birth){true,record,s->mode,phase,raw,s->generation};
 s->birth_identity[slot]=birth_stamp(&s->birth[slot],slot);
}
bool rear_p1_current(RearP1State *s,unsigned slot,unsigned index,unsigned raw,
 const RearP1Shot *shot,bool scope,bool table,bool source)
{
 if(slot>=REAR_P1_SLOTS)return false;
 RearP1Birth *b=&s->birth[slot];
 if(!b->qualified)return false;
 if(s->birth_identity[slot]!=birth_stamp(b,slot)||rear_p1_member(raw)<0||b->generation!=s->generation||!scope||!table||!source||b->raw!=raw||index!=raw||
  !phase_ok(b->record,b->phase,raw)||b->mode!=((b->record==254||b->record==255||b->record==256||b->record==257||b->record==258||b->record==259||b->record==260||b->record==261||b->record==262)?1u:2u)||!shot_ok(shot,raw)) {
  b->qualified=false;s->birth_identity[slot]=0;return false;
 }
 return true;
}
