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
{uint64_t g=s->generation+1;memset(s,0,sizeof(*s));s->generation=g?g:1;}
void rear_p1_call_end(RearP1State *s){s->lease=false;}
void rear_p1_call_begin(RearP1State *s,uint64_t tick,unsigned port,unsigned bay,
 unsigned power_index,unsigned mode_index,unsigned player,unsigned record,bool scope,bool table)
{
 s->lease=scope&&table&&port==10&&bay==1&&power_index==0&&player==1&&
  ((mode_index==0&&record==254)||(mode_index==1&&record==265));
 s->tick=tick;s->record=record;s->mode=mode_index+1;
}
static bool shot_ok(const RearP1Shot *s,unsigned raw)
{
 int k=rear_p1_member(raw);
 return k>=0&&s&&s->gr==raw&&!s->ani&&s->ani_max==1&&s->player==1&&
  s->trail==255&&!s->aim&&!s->chain&&!s->complicated&&s->filter==208&&
  s->xm==velocity[k][0]&&s->ym==velocity[k][1]&&!s->xc&&!s->yc;
}
static bool phase_ok(unsigned record,unsigned phase,unsigned raw)
{
 if(record==254)return phase>=1&&phase<=2&&raw==ids[phase-1];
 return record==265&&phase>=1&&phase<=4&&raw==ids[phase+1];
}
void rear_p1_emit(RearP1State *s,uint64_t tick,unsigned slot,unsigned port,unsigned bay,
 unsigned record,unsigned player,unsigned phase,unsigned raw,const RearP1Shot *shot,bool scope,bool table,bool source)
{
 /* Consume the one-call lease even for a rejected or reserved emission. */
 bool lease=s->lease;s->lease=false;
 if(slot>=REAR_P1_SLOTS)return;
 memset(&s->birth[slot],0,sizeof(s->birth[slot]));
 if(!lease||s->tick!=tick||!scope||!table||!source||port!=10||bay!=1||player!=1||
  record!=s->record||!phase_ok(record,phase,raw)||!shot_ok(shot,raw))return;
 s->birth[slot]=(RearP1Birth){true,record,s->mode,phase,raw,s->generation};
}
bool rear_p1_current(RearP1State *s,unsigned slot,unsigned index,unsigned raw,
 const RearP1Shot *shot,bool scope,bool table,bool source)
{
 if(slot>=REAR_P1_SLOTS)return false;
 RearP1Birth *b=&s->birth[slot];
 if(!b->qualified)return false;
 if(b->generation!=s->generation||!scope||!table||!source||b->raw!=raw||index!=raw||
  !phase_ok(b->record,b->phase,raw)||b->mode!=(b->record==254?1u:2u)||!shot_ok(shot,raw)) {
  b->qualified=false;return false;
 }
 return true;
}
