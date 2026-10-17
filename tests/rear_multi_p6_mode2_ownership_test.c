/* SPDX-License-Identifier: GPL-2.0-or-later
 * Generated/synthetic observations only. No game records or original art.
 * P6 mode2 grants exactly five allocations in cyclic 277/278/183/182/77 order. */
#include "rear_multi_p1.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); exit(1); } } while (0)
enum { PERIOD=5, BUDGET=5 };
static const unsigned ids[]={277,278,183,182,77};
static const int dx[]={-9,9,6,-6,0},dy[]={-2,-2,6,6,10};
static unsigned phase(unsigned start,unsigned ordinal)
{return (start+ordinal-2)%PERIOD+1;}
static RearP1Shot shot(unsigned p)
{unsigned k=p-1;return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,dx[k],dy[k],0,0};}
static uint64_t begin(RearP1State *s)
{
 rear_p1_call_begin(s,7,10,1,5,1,1,270,true,true);
 CHECK(s->pending&&!s->lease&&s->budget==BUDGET&&s->record==270&&s->mode==2);
 uint64_t c=rear_p1_create_begin(s,7,10,1,270,1);
 CHECK(c&&s->lease&&!s->pending&&s->remaining==BUDGET&&s->next_ordinal==1&&!s->next_phase&&!s->used_count);
 return c;
}
static void emit(RearP1State *s,uint64_t c,unsigned n,unsigned slot,unsigned p)
{
 RearP1Shot q=shot(p),copy=q;
 rear_p1_emit(s,7,c,n,slot,10,1,270,1,p,ids[p-1],&q,true,true,true);
 CHECK(!memcmp(&q,&copy,sizeof q));
}
static bool current(RearP1State *s,unsigned slot,unsigned p)
{RearP1Shot q=shot(p);return rear_p1_current(s,slot,ids[p-1],ids[p-1],&q,true,true,true);}
static void clear(const RearP1State *s)
{
 CHECK(!s->pending&&!s->lease&&!s->call&&!s->remaining&&!s->budget&&!s->next_ordinal&&!s->next_phase&&!s->used_count);
 for(unsigned i=0;i<REAR_P1_MAX_BUDGET;i++)CHECK(!s->used_slots[i]);
}
static bool old_current(RearP1State *s,unsigned slot)
{RearP1Shot q=shot(5);return rear_p1_current(s,slot,77,77,&q,true,true,true);}
static void prime(RearP1State *s,unsigned slot)
{
 /* Use a real retained, same-raw P4 birth before a recycled allocation. */
 RearP1Shot q=shot(5);
 rear_p1_call_begin(s,6,10,1,3,0,1,257,true,true);
 uint64_t c=rear_p1_create_begin(s,6,10,1,257,1);
 rear_p1_emit(s,6,c,1,slot,10,1,257,1,5,77,&q,true,true,true);
 rear_p1_create_end(s,c);CHECK(old_current(s,slot));
 CHECK(s->birth[slot].record==257&&s->birth[slot].mode==1&&s->birth[slot].phase==5);
}
static void empty_birth(const RearP1State *s,unsigned slot)
{
 const RearP1Birth *b=&s->birth[slot];
 CHECK(!b->qualified&&!b->record&&!b->mode&&!b->phase&&!b->raw&&!b->generation);
 CHECK(!s->birth_identity[slot]);
}
static void observed(RearP1State *s,unsigned slot,unsigned p)
{
 CHECK(current(s,slot,p));
 CHECK(s->birth[slot].qualified&&s->birth[slot].record==270&&s->birth[slot].mode==2);
 CHECK(s->birth[slot].phase==p&&s->birth[slot].raw==ids[p-1]&&s->birth[slot].generation==s->generation);
 CHECK(s->birth_identity[slot]);
}
static void mutate(RearP1Shot *q,unsigned f)
{
 switch(f) {
 case 0:q->gr++;break;case 1:q->ani++;break;case 2:q->ani_max++;break;
 case 3:q->player++;break;case 4:q->trail--;break;case 5:q->aim++;break;
 case 6:q->chain++;break;case 7:q->complicated++;break;case 8:q->filter=112;break;
 case 9:q->xm++;break;case 10:q->ym++;break;case 11:q->xc++;break;case 12:q->yc++;break;
 }
}
static void retained(RearP1State *s,unsigned start,unsigned count,unsigned except)
{for(unsigned n=1;n<=count;n++)CHECK(current(s,n,phase(start,n))==(n!=except));}
static void cyclic_capacities(RearP1State *s)
{
 unsigned seen[PERIOD][BUDGET]={{0}},cases=0;
 /* Zero/partial/full creators continue the original cyclic phase, but each
  * receives a fresh ordinal and the same five successful-allocation budget. */
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned prior=0;prior<=BUDGET;prior++)
 for(unsigned cap=0;cap<=BUDGET;cap++) {
  cases++;rear_p1_reset(s);
  for(unsigned n=1;n<=prior;n++)prime(s,20+n);
  for(unsigned n=1;n<=cap;n++)prime(s,10+n);
  uint64_t c=begin(s);
  for(unsigned n=1;n<=prior;n++) {emit(s,c,n,20+n,phase(start,n));observed(s,20+n,phase(start,n));}
  rear_p1_create_end(s,c);clear(s);
  unsigned next=phase(start,prior+1);c=begin(s);
  for(unsigned n=1;n<=cap;n++) {
   unsigned p=phase(next,n);emit(s,c,n,10+n,p);observed(s,10+n,p);
   CHECK(s->remaining==BUDGET-n&&s->used_count==n&&s->next_ordinal==n+1);
   CHECK(s->next_phase==phase(next,n+1)&&s->lease==(n<BUDGET)&&s->call==c);
   for(unsigned k=1;k<=n;k++)CHECK(s->used_slots[k-1]==10+k);
   seen[p-1][n-1]++;
  }
  rear_p1_create_end(s,c);clear(s);
  for(unsigned n=1;n<=cap;n++)observed(s,10+n,phase(next,n));
  for(unsigned n=1;n<=prior;n++)observed(s,20+n,phase(start,n));
  emit(s,c,cap+1,0,phase(next,cap+1));empty_birth(s,0);CHECK(!current(s,0,phase(next,cap+1)));clear(s);
 }
 CHECK(cases==180);
 for(unsigned p=0;p<PERIOD;p++)for(unsigned n=0;n<BUDGET;n++)CHECK(seen[p][n]>0);
 /* Sixth and later allocations cannot borrow a fresh grant. */
 for(unsigned start=1;start<=PERIOD;start++) {
  rear_p1_reset(s);for(unsigned n=BUDGET+1;n<=8;n++)prime(s,n);uint64_t c=begin(s);
  for(unsigned n=1;n<=BUDGET;n++)emit(s,c,n,n,phase(start,n));
  CHECK(!s->lease&&!s->remaining&&s->used_count==BUDGET&&s->next_ordinal==BUDGET+1);
  for(unsigned n=BUDGET+1;n<=8;n++) {
   emit(s,c,n,n,phase(start,n));empty_birth(s,n);CHECK(!current(s,n,phase(start,n)));clear(s);retained(s,start,BUDGET,0);
  }
 }
 /* A duplicate of any earlier allocation, including non-adjacent first,
  * revokes only that recycled slot and destroys the remaining grant. */
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned bad=2;bad<=BUDGET+1;bad++)
 for(unsigned reused=1;reused<bad;reused++) {
  rear_p1_reset(s);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,reused,phase(start,bad));clear(s);empty_birth(s,reused);retained(s,start,bad-1,reused);
  for(unsigned n=bad+1;n<=8;n++) {emit(s,c,n,n,phase(start,n));CHECK(!current(s,n,phase(start,n)));}
  retained(s,start,bad-1,reused);
 }
}
static void rejected_allocations(RearP1State *s)
{
 /* Every negative has a valid grant and real recycled old birth; earlier
  * accepted observations and the unrelated old birth must remain retained. */
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned bad=1;bad<=BUDGET;bad++)
 for(unsigned kind=0;kind<67;kind++) {
  rear_p1_reset(s);prime(s,79);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  unsigned p=phase(start,bad),slot=bad,raw=ids[p-1],ord=bad,port=10,bay=1,record=270,player=1,ph=p;
  uint64_t tick=7,call=c;bool scope=true,table=true,source=true,nonnull=true;
  RearP1Shot q=shot(p);
  switch(kind) {
  case 0:slot=80;break;case 1:slot=81;break;case 2:slot=UINT_MAX;break;
  case 3:raw=0;break;case 4:raw+=1000;break;case 5:raw=ids[p%PERIOD];break;
  case 6:tick=8;break;case 7:tick=UINT64_MAX;break;case 8:call=c+1;break;case 9:call=0;break;
  case 10:ord=0;break;case 11:ord=bad+1;break;case 12:ord=UINT_MAX;break;
  case 13:port=37;break;case 14:bay=0;break;case 15:record=259;break;case 16:record=267;break;
  case 17:player=2;break;case 18:ph=0;break;case 19:ph=PERIOD+1;break;case 20:ph=UINT_MAX;break;
  case 21:ph=p%PERIOD+1;break;case 22:nonnull=false;break;case 23:scope=false;break;
  case 24:table=false;break;case 25:source=false;break;
  case 39:raw=UINT_MAX;break;case 40:player=0;break;case 41:bay=UINT_MAX;break;
  case 42:record=268;break;case 43:raw=163;break;case 44:raw=164;break;case 45:tick=0;break;
  case 46:port=0;break;case 47:port=UINT_MAX;break;case 48:bay=2;break;case 49:record=0;break;
  case 50:record=UINT_MAX;break;case 51:player=UINT_MAX;break;case 52:ph=p+PERIOD;break;
  case 53:record=258;break;case 54:port=22;break;case 55:port=38;break;case 56:record=451;break;
  case 57:ord=bad-1;break;case 58:record=260;break;case 59:record=264;break;case 60:raw+=6000;break;
  case 61:record=1270;break;case 62:record=269;break;case 63:record=51;break;
  case 64:record=52;break;case 65:record=81;break;case 66:record=90;break;
  default:mutate(&q,kind-26);break;
  }
  RearP1Shot copy=q;
  rear_p1_emit(s,tick,call,ord,slot,port,bay,record,player,ph,raw,nonnull?&q:NULL,scope,table,source);
  CHECK(!memcmp(&q,&copy,sizeof q));clear(s);
  if(slot<REAR_P1_SLOTS)empty_birth(s,slot);
  CHECK(!current(s,slot,p));retained(s,start,bad-1,0);
  CHECK(old_current(s,79)&&s->birth[79].record==257&&s->birth[79].phase==5);
  if(slot>=REAR_P1_SLOTS)CHECK(old_current(s,bad));
  for(unsigned n=bad+1;n<=7;n++) {emit(s,c,n,n,phase(start,n));CHECK(!current(s,n,phase(start,n)));}
  retained(s,start,bad-1,0);CHECK(old_current(s,79));
 }
 /* Every physical slot, including zero and 79, accepts all five starts. */
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)for(unsigned p=1;p<=PERIOD;p++) {
  rear_p1_reset(s);prime(s,slot);uint64_t c=begin(s);emit(s,c,1,slot,p);observed(s,slot,p);
  CHECK(s->lease&&s->remaining==BUDGET-1&&s->used_count==1&&s->used_slots[0]==slot);
  rear_p1_create_end(s,c);observed(s,slot,p);
  c=rear_p1_create_begin(s,7,10,1,270,1);emit(s,c,1,slot,p);empty_birth(s,slot);CHECK(!current(s,slot,p));clear(s);
 }
 const unsigned outside[]={80,81,UINT_MAX};
 for(unsigned k=0;k<sizeof outside/sizeof *outside;k++) {
  rear_p1_reset(s);prime(s,79);uint64_t c=begin(s);for(unsigned n=1;n<=BUDGET;n++)emit(s,c,n,n,n);
  RearP1Birth copy[REAR_P1_SLOTS];memcpy(copy,s->birth,sizeof copy);
  uint64_t seals[REAR_P1_SLOTS];memcpy(seals,s->birth_identity,sizeof seals);
  CHECK(!current(s,outside[k],1));CHECK(!memcmp(copy,s->birth,sizeof copy));
  emit(s,c,BUDGET+1,outside[k],1);clear(s);
  CHECK(!memcmp(copy,s->birth,sizeof copy)&&!memcmp(seals,s->birth_identity,sizeof seals));
  retained(s,1,BUDGET,0);CHECK(old_current(s,79));
 }
}
static void canonical_mismatches(RearP1State *s)
{
 /* Raw/live fields agree: exact phase provenance must independently reject
  * all other known heads, including existing drawable and generic roles. */
 const unsigned rawids[]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278,41,3,296,297};
 const int vx[]={-10,10,-9,9,9,-9,-10,10,0,-6,6,-6,6,-9,9,-10,10,-9,9};
 const int vy[]={0,0,-2,-2,2,2,0,0,10,6,6,-6,-6,-2,-2,0,0,2,2};
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned bad=1;bad<=BUDGET;bad++)
 for(unsigned k=0;k<sizeof rawids/sizeof *rawids;k++) {
  unsigned p=phase(start,bad);if(rawids[k]==ids[p-1])continue;
  rear_p1_reset(s);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  RearP1Shot q={rawids[k],0,1,1,255,0,0,0,208,vx[k],vy[k],0,0},copy=q;
  rear_p1_emit(s,7,c,bad,bad,10,1,270,1,p,q.gr,&q,true,true,true);
  CHECK(!memcmp(&q,&copy,sizeof q));empty_birth(s,bad);clear(s);retained(s,start,bad-1,0);
  emit(s,c,bad+1,bad+1,phase(start,bad+1));CHECK(!current(s,bad+1,phase(start,bad+1)));
 }
 /* A wrong cyclic successor with its own correct raw/live fields still fails. */
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned bad=2;bad<=BUDGET;bad++)
 for(unsigned p=1;p<=PERIOD;p++) {
  if(p==phase(start,bad))continue;
  rear_p1_reset(s);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,bad,p);empty_birth(s,bad);clear(s);retained(s,start,bad-1,0);
  emit(s,c,bad+1,bad+1,phase(start,bad+1));CHECK(!current(s,bad+1,phase(start,bad+1)));
 }
 /* Raw aliases cannot become members just because gr and raw agree. */
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned delta=1000;delta<=6000;delta+=5000) {
  rear_p1_reset(s);prime(s,0);uint64_t c=begin(s);RearP1Shot q=shot(p);q.gr+=delta;
  rear_p1_emit(s,7,c,1,0,10,1,270,1,p,q.gr,&q,true,true,true);empty_birth(s,0);clear(s);
  c=begin(s);emit(s,c,1,0,p);CHECK(!rear_p1_current(s,0,q.gr,q.gr,&q,true,true,true));CHECK(!current(s,0,p));
 }
}
static void every_slot_pair(RearP1State *s)
{
 /* Exhaust every first/second pair and every start. The third allocation
  * reuses the non-adjacent first while budget remains; zero is not a sentinel. */
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned first=0;first<REAR_P1_SLOTS;first++)
 for(unsigned second=0;second<REAR_P1_SLOTS;second++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,first,start);
  emit(s,c,2,second,phase(start,2));
  if(first==second) {empty_birth(s,first);clear(s);continue;}
  observed(s,first,start);observed(s,second,phase(start,2));
  CHECK(s->lease&&s->remaining==BUDGET-2&&s->used_count==2&&s->next_ordinal==3);
  CHECK(s->used_slots[0]==first&&s->used_slots[1]==second);
  emit(s,c,3,first,phase(start,3));empty_birth(s,first);clear(s);observed(s,second,phase(start,2));
  emit(s,c,4,first,start);empty_birth(s,first);observed(s,second,phase(start,2));
 }
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)
 for(unsigned bad=2;bad<=BUDGET+1;bad++)for(unsigned reused=1;reused<bad;reused++) {
  rear_p1_reset(s);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,(slot+n-1)%REAR_P1_SLOTS,phase(start,n));
  unsigned target=(slot+reused-1)%REAR_P1_SLOTS;
  emit(s,c,bad,target,phase(start,bad));empty_birth(s,target);clear(s);
  for(unsigned n=1;n<bad;n++)
   CHECK(current(s,(slot+n-1)%REAR_P1_SLOTS,phase(start,n))==(n!=reused));
  emit(s,c,bad+1,(slot+BUDGET)%REAR_P1_SLOTS,phase(start,bad+1));
  empty_birth(s,(slot+BUDGET)%REAR_P1_SLOTS);clear(s);
 }

}
static void isolation(RearP1State *s)
{
 for(unsigned start=1;start<=PERIOD;start++)for(unsigned after=0;after<=BUDGET;after++)
 for(unsigned kind=0;kind<20;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=after;n++)emit(s,c,n,n,phase(start,n));
  uint64_t inner=0;
  if(kind==0)inner=rear_p1_create_begin(s,7,10,1,270,1);
  if(kind==1)rear_p1_create_end(s,c);
  if(kind==2)rear_p1_call_end(s);
  if(kind==3)rear_p1_reset(s);
  if(kind>=4) {
   rear_p1_call_begin(s,7,10,1,5,1,1,270,true,true);
   inner=rear_p1_create_begin(s,kind==4?8:kind==10?0:kind==11?UINT64_MAX:7,
    kind==5?37:kind==12?UINT_MAX:kind==15?22:kind==16?38:10,
    kind==6?0:kind==13?UINT_MAX:1,
    kind==7?259:kind==9?258:kind==14?UINT_MAX:kind==17?451:kind==18?260:270,
    kind==8?2:kind==19?0:1);
  }
  if(inner) {CHECK(inner!=c);emit(s,inner,1,10,start);CHECK(!current(s,10,start));rear_p1_create_end(s,inner);}
  emit(s,c,after+1,11,phase(start,after+1));CHECK(!current(s,11,phase(start,after+1)));clear(s);
  for(unsigned n=1;n<=after;n++)CHECK(current(s,n,phase(start,n))==(kind!=3));
 }
 /* Pending alone is insufficient; stale end must not cancel a newer grant. */
 rear_p1_reset(s);prime(s,0);rear_p1_call_begin(s,7,10,1,5,1,1,270,true,true);
 emit(s,0,1,0,1);empty_birth(s,0);CHECK(!current(s,0,1));clear(s);
 rear_p1_reset(s);uint64_t c=begin(s);rear_p1_create_end(s,c);clear(s);
 uint64_t inner=rear_p1_create_begin(s,7,10,1,270,1);CHECK(inner!=c&&!s->lease);
 emit(s,inner,1,0,1);CHECK(!current(s,0,1));clear(s);
 c=begin(s);rear_p1_create_end(s,c);inner=begin(s);CHECK(inner!=c);
 rear_p1_create_end(s,c);CHECK(s->lease&&s->call==inner);
 emit(s,inner,1,0,1);CHECK(current(s,0,1));
 emit(s,c,2,1,2);CHECK(!current(s,1,2)&&current(s,0,1));clear(s);
 emit(s,inner,2,2,2);CHECK(!current(s,2,2));
 rear_p1_reset(s);s->call_serial=UINT64_MAX;c=begin(s);CHECK(c==1);
 emit(s,c,1,0,1);CHECK(current(s,0,1));s->generation=UINT64_MAX;rear_p1_reset(s);
 CHECK(s->generation==1&&!current(s,0,1));clear(s);inner=begin(s);CHECK(inner!=c);
 emit(s,c,1,1,1);CHECK(!current(s,1,1));clear(s);
}
static bool admitted(unsigned power,unsigned mode,unsigned record)
{
 return (power<2&&mode<2&&record==(mode?265:254)+power)||
  (power==2&&mode<2&&record==(mode?267:256))||(power==3&&mode<2&&record==(mode?268:257))||
  (power==4&&mode<2&&record==(mode?269:258))||(power==5&&mode<2&&record==(mode?270:259))||(power==6&&mode==0&&record==260);
}
static unsigned budget(unsigned power,unsigned mode)
{return power==6?4:power==5?(mode?5:3):power==4?(mode?4:2):power==3?5:power==2?(mode?4:2):power+1;}
static void admission(RearP1State *s)
{
 const unsigned records[]={0,1,50,77,163,164,182,183,253,254,255,256,257,258,259,260,261,262,263,264,
  265,266,267,268,269,270,271,272,273,274,275,277,278,281,300,445,451,501,686,687,688,690,1259,1269,1270,UINT_MAX};
 const unsigned powers[]={0,1,2,3,4,5,6,7,8,9,10,11,UINT_MAX},modes[]={0,1,2,3,UINT_MAX};
 for(unsigned p=0;p<sizeof powers/sizeof *powers;p++)for(unsigned m=0;m<sizeof modes/sizeof *modes;m++)
 for(unsigned r=0;r<sizeof records/sizeof *records;r++) {
  unsigned power=powers[p],mode=modes[m],record=records[r];bool yes=admitted(power,mode,record);
  rear_p1_call_begin(s,7,10,1,power,mode,1,record,true,true);CHECK(s->pending==yes);
  CHECK(s->budget==(yes?budget(power,mode):0));
  uint64_t c=rear_p1_create_begin(s,7,10,1,record,1);CHECK(s->lease==yes);
  CHECK(s->remaining==(yes?budget(power,mode):0));
  if(!yes) {emit(s,c,1,0,1);CHECK(!current(s,0,1));clear(s);}else rear_p1_create_end(s,c);
 }
 const unsigned ports[]={0,10,19,22,27,32,37,38,UINT_MAX},bays[]={0,1,2,UINT_MAX},players[]={0,1,2,UINT_MAX};
 for(unsigned p=0;p<sizeof ports/sizeof *ports;p++)for(unsigned b=0;b<sizeof bays/sizeof *bays;b++)
 for(unsigned u=0;u<sizeof players/sizeof *players;u++)for(unsigned scope=0;scope<2;scope++)for(unsigned table=0;table<2;table++) {
  bool yes=ports[p]==10&&bays[b]==1&&players[u]==1&&scope&&table;
  rear_p1_call_begin(s,7,ports[p],bays[b],5,1,players[u],270,scope!=0,table!=0);CHECK(s->pending==yes);
  rear_p1_call_end(s);clear(s);
 }
 CHECK(REAR_P1_HEADS==17&&REAR_P1_OBSERVED==19&&REAR_P1_MAX_BUDGET==5);
 const unsigned members[]={39,1,281,282,301,300,40,2,77,182,183,277,278,41,3,296,297};
 const unsigned observations[]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278,41,3,296,297};
 for(unsigned k=0;k<sizeof members/sizeof *members;k++)CHECK(rear_p1_member(members[k])==(int)k);
 for(unsigned k=0;k<sizeof observations/sizeof *observations;k++)CHECK(rear_p1_observed(observations[k])==(int)k);
 for(unsigned raw=0;raw<8000;raw++) {
  bool draw=false,observe=false;
  for(unsigned k=0;k<sizeof members/sizeof *members;k++)draw|=raw==members[k];
  for(unsigned k=0;k<sizeof observations/sizeof *observations;k++)observe|=raw==observations[k];
  CHECK((rear_p1_member(raw)>=0)==draw);CHECK((rear_p1_observed(raw)>=0)==observe);
 }
 CHECK(rear_p1_member(163)<0&&rear_p1_member(164)<0);
 CHECK(rear_p1_member(UINT_MAX)<0&&rear_p1_observed(UINT_MAX)<0);
}
static void one_way_revocation(RearP1State *s)
{
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned field=0;field<13;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
  RearP1Shot q=shot(p);mutate(&q,field);RearP1Shot copy=q;
  CHECK(!rear_p1_current(s,79,ids[p-1],ids[p-1],&q,true,true,true));
  CHECK(!memcmp(&q,&copy,sizeof q));CHECK(!s->birth[79].qualified&&!s->birth_identity[79]&&!current(s,79,p));
  rear_p1_create_end(s,c);c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
 }
 const unsigned aliases[]={0,1,2,3,39,40,41,77,163,164,182,183,277,278,281,282,300,301,1003,1041,1077,6041,6077,UINT_MAX};
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned a=0;a<sizeof aliases/sizeof *aliases;a++)
 for(unsigned field=0;field<3;field++)if(aliases[a]!=ids[p-1]) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  unsigned index=field==0||field==2?aliases[a]:ids[p-1],raw=field==1||field==2?aliases[a]:ids[p-1];
  CHECK(!rear_p1_current(s,0,index,raw,&q,true,true,true));CHECK(!current(s,0,p)&&!s->birth_identity[0]);
 }
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned kind=0;kind<4;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  CHECK(!rear_p1_current(s,0,ids[p-1],ids[p-1],kind==3?NULL:&q,kind!=0,kind!=1,kind!=2));CHECK(!current(s,0,p));
 }
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned field=0;field<16;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Birth before=s->birth[0];
  switch(field) {
  case 0:s->birth[0].generation++;break;case 1:s->birth[0].record=258;break;
  case 2:s->birth[0].phase=0;break;case 3:s->birth[0].phase=PERIOD+1;break;
  case 4:s->birth[0].raw++;break;case 5:s->birth[0].mode=1;break;
  case 6:s->birth[0].mode=0;break;case 7:s->birth[0].phase=p%PERIOD+1;break;
  case 8:s->birth[0].qualified=false;break;case 9:s->birth[0].record=259;break;
  case 10:s->birth[0].mode=UINT_MAX;break;case 11:s->birth[0].record=0;break;
  case 12:s->birth[0].record=UINT_MAX;break;case 13:s->birth[0].phase=UINT_MAX;break;
  case 14:s->birth[0].generation=0;break;case 15:s->birth[0].record=451;break;
  }
  CHECK(!current(s,0,p)&&!s->birth[0].qualified);
  before.qualified=false;s->birth[0]=before;CHECK(!current(s,0,p));
 }
 /* Observed-only roles never become drawable through a forged qualified bit. */
 for(unsigned p=1;p<=2;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
  rear_p1_reset(s);RearP1Shot q={p==1?163:164,0,1,1,255,0,0,0,208,p==1?-6:6,-6,0,0};
  s->birth[slot]=(RearP1Birth){true,268,2,p,q.gr,s->generation};
  CHECK(!rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true)&&!s->birth[slot].qualified);
 }
}
static void shared_birth(RearP1State *s,unsigned record,unsigned slot,unsigned p)
{
 CHECK((record==270&&p>=1&&p<=5)||(record==269&&p>=1&&p<=4)||(record==268&&p>=3&&p<=5));
 rear_p1_call_begin(s,13,10,1,record-265,1,1,record,true,true);
 uint64_t c=rear_p1_create_begin(s,13,10,1,record,1);RearP1Shot q=shot(p);
 rear_p1_emit(s,13,c,1,slot,10,1,record,1,p,q.gr,&q,true,true,true);rear_p1_create_end(s,c);
 CHECK(current(s,slot,p)&&s->birth[slot].record==record&&s->birth_identity[slot]);
}
static void original_identity_seal(RearP1State *s)
{
 /* All shared canonical phases, both record-substitution directions and all
  * 80 physical slots: matching raw and live vectors cannot forge ownership. */
 for(unsigned other=268;other<=269;other++)for(unsigned direction=0;direction<2;direction++)
 for(unsigned p=other==268?3:1;p<=(other==268?5u:4u);p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
  unsigned record=direction?other:270,replacement=direction?270:other;
  rear_p1_reset(s);shared_birth(s,record,slot,p);
  RearP1Birth original=s->birth[slot];uint64_t identity=s->birth_identity[slot];
  s->birth[slot].record=replacement;
  CHECK(!current(s,slot,p)&&!s->birth[slot].qualified&&!s->birth_identity[slot]);
  s->birth[slot]=original;CHECK(!current(s,slot,p)&&!s->birth_identity[slot]);
  shared_birth(s,record,slot,p);CHECK(s->birth_identity[slot]==identity);
  rear_p1_call_begin(s,14,10,1,replacement-265,1,1,replacement,true,true);rear_p1_call_end(s);
  CHECK(current(s,slot,p)&&s->birth_identity[slot]==identity&&s->birth[slot].record==record);
 }
 /* A complete 77 metadata substitution also changes mode/phase for the
  * canonical mode1 records257/259; immutable original identity still wins. */
 const unsigned same77[]={257,259,268,270},same77phase[]={5,3,5,5};
 for(unsigned a=0;a<4;a++)for(unsigned b=0;b<4;b++)if(a!=b)
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
  unsigned record=same77[a],mode=record>=265,power=record-(mode?265:254);
  rear_p1_reset(s);rear_p1_call_begin(s,17,10,1,power,mode,1,record,true,true);
  uint64_t c=rear_p1_create_begin(s,17,10,1,record,1);RearP1Shot q=shot(5);
  rear_p1_emit(s,17,c,1,slot,10,1,record,1,same77phase[a],77,&q,true,true,true);rear_p1_create_end(s,c);
  CHECK(current(s,slot,5));RearP1Birth original=s->birth[slot];
  s->birth[slot].record=same77[b];s->birth[slot].mode=same77[b]>=265?2:1;s->birth[slot].phase=same77phase[b];
  CHECK(!current(s,slot,5)&&!s->birth[slot].qualified&&!s->birth_identity[slot]);
  s->birth[slot]=original;CHECK(!current(s,slot,5)&&!s->birth_identity[slot]);
 }
 /* Every ordered distinct slot pair rejects metadata-only or full-seal copy. */
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)
 for(unsigned target=0;target<REAR_P1_SLOTS;target++)if(target!=slot)
 for(unsigned copy_seal=0;copy_seal<2;copy_seal++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,slot,p);rear_p1_create_end(s,c);
  s->birth[target]=s->birth[slot];
  if(copy_seal)s->birth_identity[target]=s->birth_identity[slot];
  CHECK(!current(s,target,p)&&!s->birth[target].qualified&&!s->birth_identity[target]);observed(s,slot,p);
 }
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned bit=0;bit<64;bit++) {
  rear_p1_reset(s);prime(s,79);uint64_t c=begin(s);emit(s,c,1,0,p);
  RearP1Birth original=s->birth[0];uint64_t identity=s->birth_identity[0];
  s->birth_identity[0]^=UINT64_C(1)<<bit;RearP1Shot q=shot(p),copy=q;
  CHECK(!rear_p1_current(s,0,q.gr,q.gr,&q,true,true,true));
  CHECK(!memcmp(&q,&copy,sizeof q)&&!s->birth[0].qualified&&!s->birth_identity[0]);
  s->birth[0]=original;CHECK(!current(s,0,p)&&!s->birth_identity[0]);CHECK(old_current(s,79));
  c=begin(s);emit(s,c,1,0,p);CHECK(s->birth_identity[0]==identity);observed(s,0,p);
 }
 /* All record bits are significant, even when an XOR produces another
  * valid route. Restoration after detection cannot resurrect the old birth. */
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned bit=0;bit<sizeof(unsigned)*CHAR_BIT;bit++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);rear_p1_create_end(s,c);
  RearP1Birth original=s->birth[0];s->birth[0].record^=1u<<bit;
  CHECK(!current(s,0,p)&&!s->birth[0].qualified&&!s->birth_identity[0]);
  s->birth[0]=original;CHECK(!current(s,0,p)&&!s->birth_identity[0]);
 }
 /* Live selection cannot reclassify retained births; generation loss revokes
  * ownership and restoring mutable metadata does not resurrect a seal. */
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,slot,p);rear_p1_create_end(s,c);
  uint64_t identity=s->birth_identity[slot];RearP1Birth original=s->birth[slot];
  for(unsigned power=0;power<12;power++)for(unsigned mode=0;mode<3;mode++) {
   rear_p1_call_begin(s,11,10,1,power,mode,1,(mode?265:254)+power,true,true);rear_p1_call_end(s);
   observed(s,slot,p);CHECK(s->birth_identity[slot]==identity);
   CHECK(!memcmp(&original,&s->birth[slot],sizeof original));
  }
  s->generation++;CHECK(!current(s,slot,p)&&!s->birth_identity[slot]);
  s->generation--;s->birth[slot]=original;CHECK(!current(s,slot,p));
 }
 rear_p1_reset(s);for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)empty_birth(s,slot);
}
/* Source-specific synthetic observations; never extracted original records. */
typedef struct {
 unsigned record,power,mode,budget,period;
 unsigned raw[5];int vx[5],vy[5];
} Source;
static const Source sources[]={
 {254,0,0,1,2,{39,1},{-10,10},{0,0}},
 {255,1,0,2,2,{39,1},{-10,10},{0,0}},
 {256,2,0,2,2,{40,2},{-10,10},{0,0}},
 {257,3,0,5,5,{281,282,301,300,77},{-9,9,9,-9,0},{-2,-2,2,2,10}},
 {258,4,0,2,2,{41,3},{-10,10},{0,0}},
 {265,0,1,1,4,{281,282,301,300},{-9,9,9,-9},{-2,-2,2,2}},
 {266,1,1,2,4,{281,282,301,300},{-9,9,9,-9},{-2,-2,2,2}},
 {267,2,1,4,4,{281,282,301,300},{-9,9,9,-9},{-2,-2,2,2}},
 {268,3,1,5,5,{163,164,183,182,77},{-6,6,6,-6,0},{-6,-6,6,6,10}},
 {269,4,1,4,4,{277,278,183,182},{-9,9,6,-6},{-2,-2,6,6}},
 {259,5,0,3,3,{41,3,77},{-10,10,0},{0,0,10}},
 {270,5,1,5,5,{277,278,183,182,77},{-9,9,6,-6,0},{-2,-2,6,6,10}}
};
static RearP1Shot source_shot(const Source *a,unsigned p)
{return (RearP1Shot){a->raw[p-1],0,1,1,255,0,0,0,208,a->vx[p-1],a->vy[p-1],0,0};}
static uint64_t source_begin(RearP1State *s,const Source *a)
{
 rear_p1_call_begin(s,9,10,1,a->power,a->mode,1,a->record,true,true);
 CHECK(s->pending&&s->budget==a->budget&&s->record==a->record&&s->mode==a->mode+1);
 uint64_t c=rear_p1_create_begin(s,9,10,1,a->record,1);
 CHECK(c&&s->lease&&s->remaining==a->budget&&!s->next_phase&&s->next_ordinal==1&&!s->used_count);
 return c;
}
static void source_emit(RearP1State *s,const Source *a,uint64_t c,unsigned n,unsigned slot,unsigned p)
{
 RearP1Shot q=source_shot(a,p),copy=q;
 rear_p1_emit(s,9,c,n,slot,10,1,a->record,1,p,q.gr,&q,true,true,true);CHECK(!memcmp(&q,&copy,sizeof q));
}
static bool source_current(RearP1State *s,const Source *a,unsigned slot,unsigned p)
{RearP1Shot q=source_shot(a,p);return rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true);}
static void source_budgets(RearP1State *s)
{
 /* Exhaust all 12x12 source transitions after every possible prior capacity.
  * Each creator receives exactly its own source budget and cyclic period. */
 for(unsigned previous=0;previous<sizeof sources/sizeof *sources;previous++)
 for(unsigned next=0;next<sizeof sources/sizeof *sources;next++)
 for(unsigned prior=0;prior<=sources[previous].budget;prior++)
 for(unsigned start=1;start<=sources[next].period;start++) {
  const Source *a=&sources[previous],*b=&sources[next];
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,79,1);rear_p1_create_end(s,c);
  c=source_begin(s,a);
  for(unsigned n=1;n<=prior;n++)source_emit(s,a,c,n,20+n,(n-1)%a->period+1);
  rear_p1_create_end(s,c);clear(s);c=source_begin(s,b);
  for(unsigned n=1;n<=b->budget;n++) {
   unsigned p=(start+n-2)%b->period+1;source_emit(s,b,c,n,n,p);
   CHECK(s->remaining==b->budget-n&&s->next_ordinal==n+1&&s->used_count==n);
   CHECK(s->next_phase==p%b->period+1&&s->lease==(n<b->budget));
   CHECK(source_current(s,b,n,p)==(b->raw[p-1]!=163&&b->raw[p-1]!=164));
  }
  source_emit(s,b,c,b->budget+1,10,(start+b->budget-1)%b->period+1);empty_birth(s,10);clear(s);
  for(unsigned n=1;n<=b->budget;n++) {
   unsigned p=(start+n-2)%b->period+1;
   CHECK(source_current(s,b,n,p)==(b->raw[p-1]!=163&&b->raw[p-1]!=164));
  }
  for(unsigned n=1;n<=prior;n++) {
   unsigned p=(n-1)%a->period+1;
   CHECK(source_current(s,a,20+n,p)==(a->raw[p-1]!=163&&a->raw[p-1]!=164));
  }
  observed(s,79,1);
 }
}
static void excluded_sources(RearP1State *s)
{
 /* The physical1270 payload alias, wrong-context270, P7+, direct shared
  * consumers and linked records stay unowned even with matching live heads. */
 const unsigned records[]={0,1,41,3,51,52,77,81,90,163,164,260,261,262,263,264,
  268,269,270,271,272,273,274,275,277,278,445,451,502,504,505,793,1268,1269,1270,1793,UINT_MAX};
 const unsigned powers[]={0,1,2,3,4,5,6,7,8,9,10,11,UINT_MAX},ports[]={0,10,19,22,27,32,36,37,38};
 for(unsigned r=0;r<sizeof records/sizeof *records;r++)for(unsigned power=0;power<sizeof powers/sizeof *powers;power++)
 for(unsigned mode=0;mode<3;mode++)for(unsigned port=0;port<sizeof ports/sizeof *ports;port++)
 for(unsigned p=1;p<=PERIOD;p++) {
  if(ports[port]==10&&admitted(powers[power],mode,records[r]))continue;
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);emit(s,c,2,79,phase(p,2));rear_p1_create_end(s,c);
  rear_p1_call_begin(s,7,ports[port],1,powers[power],mode,1,records[r],true,true);CHECK(!s->pending&&!s->budget);
  c=rear_p1_create_begin(s,7,ports[port],1,records[r],1);CHECK(!s->lease);
  RearP1Shot q=shot(p),copy=q;
  rear_p1_emit(s,7,c,1,0,ports[port],1,records[r],1,p,q.gr,&q,true,true,true);
  CHECK(!memcmp(&q,&copy,sizeof q));empty_birth(s,0);clear(s);observed(s,79,phase(p,2));
  c=begin(s);rear_p1_create_end(s,c);CHECK(!current(s,0,p));observed(s,79,phase(p,2));
 }
}
static void local_invalidation(RearP1State *s)
{
 /* The caller supplies record-local table/source validity. Invalidating one
  * same-head record must leave unrelated sealed records alive, in all orders. */
 for(unsigned p=3;p<=4;p++)for(unsigned invalid=268;invalid<=270;invalid++)
 for(unsigned cause=0;cause<2;cause++) {
  rear_p1_reset(s);for(unsigned record=268;record<=270;record++)shared_birth(s,record,record-268,p);
  RearP1Shot q=shot(p);unsigned slot=invalid-268;RearP1Birth original=s->birth[slot];
  CHECK(!rear_p1_current(s,slot,q.gr,q.gr,&q,true,cause!=0,cause!=1));
  CHECK(!current(s,slot,p)&&!s->birth_identity[slot]);
  s->birth[slot]=original;CHECK(!current(s,slot,p)&&!s->birth_identity[slot]);
  for(unsigned record=268;record<=270;record++)if(record!=invalid)
   CHECK(current(s,record-268,p)&&s->birth[record-268].record==record);
 }
 /* An invalid source cancels only the allocated slot and remaining grant;
  * a valid earlier observation and a different record remain retained. */
 for(unsigned p=1;p<=PERIOD;p++)for(unsigned cause=0;cause<2;cause++) {
  rear_p1_reset(s);prime(s,79);uint64_t c=begin(s);emit(s,c,1,0,p);
  unsigned next=phase(p,2);RearP1Shot q=shot(next);
  rear_p1_emit(s,7,c,2,1,10,1,270,1,next,q.gr,&q,true,cause!=0,cause!=1);
  clear(s);empty_birth(s,1);observed(s,0,p);CHECK(old_current(s,79));
  emit(s,c,3,2,phase(p,3));empty_birth(s,2);clear(s);observed(s,0,p);CHECK(old_current(s,79));
 }
}
static void stale_slots(RearP1State *s)
{
 /* Same-slot replacement gets a new exact birth. Old metadata, or a seal
  * copied from a different generation, cannot recover old ownership. */
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)for(unsigned p=1;p<=PERIOD;p++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,slot,p);rear_p1_create_end(s,c);
  RearP1Birth old=s->birth[slot];uint64_t seal=s->birth_identity[slot];
  unsigned next=phase(p,2);c=begin(s);emit(s,c,1,slot,next);rear_p1_create_end(s,c);
  CHECK(current(s,slot,next));s->birth[slot]=old;
  CHECK(!current(s,slot,p)&&!s->birth_identity[slot]);
  rear_p1_reset(s);s->birth[slot]=old;s->birth_identity[slot]=seal;
  CHECK(!current(s,slot,p)&&!s->birth_identity[slot]);
  c=begin(s);emit(s,c,1,slot,p);rear_p1_create_end(s,c);observed(s,slot,p);
 }
}
static void coexistence(RearP1State *s)
{
 RearP1Shot births[42];unsigned records[42],modes[42],phases[42],count=0;
 rear_p1_reset(s);uint64_t c=begin(s);
 for(unsigned p=1;p<=PERIOD;p++)emit(s,c,p,70+p,p);
 rear_p1_create_end(s,c);
 /* All eleven old routes plus270, all42 phase observations and unchanged
  * observed-only163/164 behavior coexist with every new phase. */
 for(unsigned r=0;r<sizeof sources/sizeof *sources;r++)for(unsigned p=1;p<=sources[r].period;p++) {
  const Source *a=&sources[r];CHECK(count<42);c=source_begin(s,a);source_emit(s,a,c,1,count,p);rear_p1_create_end(s,c);
  births[count]=source_shot(a,p);records[count]=a->record;modes[count]=a->mode+1;phases[count]=p;
  bool drawable=births[count].gr!=163&&births[count].gr!=164;
  CHECK(source_current(s,a,count,p)==drawable);
  if(drawable)CHECK(s->birth[count].record==a->record&&s->birth[count].mode==a->mode+1&&s->birth[count].phase==p);
  else empty_birth(s,count);
  count++;for(unsigned k=1;k<=PERIOD;k++)observed(s,70+k,k);
 }
 CHECK(count==42);
 for(unsigned power=0;power<12;power++)for(unsigned mode=0;mode<3;mode++) {
  rear_p1_call_begin(s,9,10,1,power,mode,1,(mode?265:254)+power,true,true);rear_p1_call_end(s);
  for(unsigned p=1;p<=PERIOD;p++)observed(s,70+p,p);
  for(unsigned k=0;k<count;k++) {
   bool drawable=births[k].gr!=163&&births[k].gr!=164;
   CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true)==drawable);
   if(drawable)CHECK(s->birth[k].record==records[k]&&s->birth[k].mode==modes[k]&&s->birth[k].phase==phases[k]);
  }
 }
 /* Pass-through observations consume capacity and revoke recycled drawables. */
 c=source_begin(s,&sources[8]);source_emit(s,&sources[8],c,1,71,1);empty_birth(s,71);
 CHECK(s->lease&&s->remaining==4&&s->used_count==1);observed(s,75,5);
 source_emit(s,&sources[8],c,2,72,2);empty_birth(s,72);
 CHECK(s->lease&&s->remaining==3&&s->used_count==2);observed(s,75,5);rear_p1_create_end(s,c);
 c=begin(s);emit(s,c,1,71,1);emit(s,c,2,72,2);emit(s,c,3,73,3);emit(s,c,4,74,4);emit(s,c,5,75,5);rear_p1_create_end(s,c);
 for(unsigned p=1;p<=PERIOD;p++)observed(s,70+p,p);
 for(unsigned k=0;k<count;k++)CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true)==(births[k].gr!=163&&births[k].gr!=164));
 rear_p1_reset(s);clear(s);
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)empty_birth(s,slot);
 for(unsigned k=0;k<count;k++)CHECK(!rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true));
}
int main(void)
{
 RearP1State state={0};cyclic_capacities(&state);rejected_allocations(&state);canonical_mismatches(&state);
 every_slot_pair(&state);isolation(&state);admission(&state);one_way_revocation(&state);original_identity_seal(&state);
 source_budgets(&state);excluded_sources(&state);local_invalidation(&state);stale_slots(&state);coexistence(&state);
 printf("Rear P6 mode2 ownership PASS: %u checks; five starts,180 prior0..5/new0..5 capacities, every80x80 slot pair, every-slot ordinal2..6 duplicates, exact270 budget5/period5, retained270/269/268 seals, physical1270 and linked451 exclusions, twelve source tuples and42 phases\n",checks);
 return 0;
}
