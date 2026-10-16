/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite renderer provenance. The inputs are observations, never game writers. */
#include "rear_multi_p1.h"
#include <string.h>
static const unsigned ids[REAR_P1_HEADS]={39,1,281,282,301,300};
static const int velocity[REAR_P1_HEADS][2]={{-10,0},{10,0},{-9,-2},{9,-2},{9,2},{-9,2}};
uint64_t rear_p1_stamp(const void *data,size_t size)
{
 const uint8_t *p=data;uint64_t h=UINT64_C(14695981039346656037);
 for(size_t i=0;i<size;i++)h=(h^p[i])*UINT64_C(1099511628211);
 return h;
}
int rear_p1_member(unsigned raw)
{for(unsigned i=0;i<REAR_P1_HEADS;i++)if(ids[i]==raw)return (int)i;return -1;}
void rear_p1_reset(RearP1State *s)
{uint64_t g=s->generation+1,c=s->call_serial;memset(s,0,sizeof(*s));s->generation=g?g:1;s->call_serial=c;}
void rear_p1_call_end(RearP1State *s)
{s->pending=false;s->lease=false;s->call=0;s->budget=0;s->remaining=0;s->next_ordinal=0;s->next_phase=0;s->first_slot=REAR_P1_SLOTS;}
void rear_p1_call_begin(RearP1State *s,uint64_t tick,unsigned port,unsigned bay,
 unsigned power_index,unsigned mode_index,unsigned player,unsigned record,bool scope,bool table)
{
 rear_p1_call_end(s);
 s->pending=scope&&table&&port==10&&bay==1&&player==1&&
  ((power_index==0&&((mode_index==0&&record==254)||(mode_index==1&&record==265)))||
   (power_index==1&&((mode_index==0&&record==255)||(mode_index==1&&record==266))));
 s->tick=tick;s->record=record;s->mode=mode_index+1;
 if(s->pending)s->budget=power_index+1;
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
 int k=rear_p1_member(raw);
 return k>=0&&s&&s->gr==raw&&!s->ani&&s->ani_max==1&&s->player==1&&
  s->trail==255&&!s->aim&&!s->chain&&!s->complicated&&s->filter==208&&
  s->xm==velocity[k][0]&&s->ym==velocity[k][1]&&!s->xc&&!s->yc;
}
static bool phase_ok(unsigned record,unsigned phase,unsigned raw)
{
 if(record==254||record==255)return phase>=1&&phase<=2&&raw==ids[phase-1];
 return (record==265||record==266)&&phase>=1&&phase<=4&&raw==ids[phase+1];
}
void rear_p1_emit(RearP1State *s,uint64_t tick,uint64_t call,unsigned ordinal,unsigned slot,unsigned port,unsigned bay,
 unsigned record,unsigned player,unsigned phase,unsigned raw,const RearP1Shot *shot,bool scope,bool table,bool source)
{
 /* Consume before validation, including rejected/zero-graphics/out-of-range
  * allocations. The first canonical phase can start anywhere in the cycle:
  * a prior partial-capacity call advances the original phase only once. */
 bool lease=s->lease&&s->remaining>0;
 if(s->remaining)--s->remaining;
 if(slot<REAR_P1_SLOTS)memset(&s->birth[slot],0,sizeof(s->birth[slot]));
 unsigned period=s->mode==1?2:4;
 if(!lease||s->call!=call||s->tick!=tick||ordinal!=s->next_ordinal||
  !scope||!table||port!=10||bay!=1||player!=1||record!=s->record||
  phase<1||phase>period||(s->next_phase&&phase!=s->next_phase)||
  (ordinal>1&&slot==s->first_slot)) {
  rear_p1_call_end(s);return;
 }
 s->next_ordinal++;s->next_phase=phase==period?1:phase+1;
 if(!s->remaining)s->lease=false;
 if(slot>=REAR_P1_SLOTS||!source||!phase_ok(record,phase,raw)||!shot_ok(shot,raw)) {
  rear_p1_call_end(s);return;
 }
 if(ordinal==1)s->first_slot=slot;
 s->birth[slot]=(RearP1Birth){true,record,s->mode,phase,raw,s->generation};
}
bool rear_p1_current(RearP1State *s,unsigned slot,unsigned index,unsigned raw,
 const RearP1Shot *shot,bool scope,bool table,bool source)
{
 if(slot>=REAR_P1_SLOTS)return false;
 RearP1Birth *b=&s->birth[slot];
 if(!b->qualified)return false;
 if(b->generation!=s->generation||!scope||!table||!source||b->raw!=raw||index!=raw||
  !phase_ok(b->record,b->phase,raw)||b->mode!=((b->record==254||b->record==255)?1u:2u)||!shot_ok(shot,raw)) {
  b->qualified=false;return false;
 }
 return true;
}
