/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic five-observation ownership only: no game records or original art.
 * Phases 1/2 are observed pass-throughs; only phases 3/4/5 are drawable. */
#include "rear_multi_p1.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); exit(1); } } while (0)
static const unsigned ids[]={163,164,183,182,77};
static const int dx[]={-6,6,6,-6,0},dy[]={-6,-6,6,6,10};
static unsigned phase(unsigned start,unsigned ordinal)
{return (start+ordinal-2)%5+1;}
static bool drawable(unsigned p)
{return p>=3&&p<=5;}
static RearP1Shot shot(unsigned p)
{unsigned k=p-1;return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,dx[k],dy[k],0,0};}
static uint64_t begin(RearP1State *s)
{
 rear_p1_call_begin(s,7,10,1,3,1,1,268,true,true);
 CHECK(s->pending&&!s->lease&&s->budget==5&&s->record==268&&s->mode==2);
 uint64_t c=rear_p1_create_begin(s,7,10,1,268,1);
 CHECK(c&&s->lease&&!s->pending&&s->remaining==5&&s->next_ordinal==1&&!s->next_phase&&!s->used_count);
 return c;
}
static void emit(RearP1State *s,uint64_t c,unsigned n,unsigned slot,unsigned p)
{
 RearP1Shot q=shot(p),copy=q;
 rear_p1_emit(s,7,c,n,slot,10,1,268,1,p,ids[p-1],&q,true,true,true);
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
 /* Recycle a real mode1 birth, rather than relying on initially empty slots. */
 RearP1Shot q=shot(5);
 rear_p1_call_begin(s,6,10,1,3,0,1,257,true,true);
 uint64_t c=rear_p1_create_begin(s,6,10,1,257,1);
 rear_p1_emit(s,6,c,1,slot,10,1,257,1,5,77,&q,true,true,true);
 rear_p1_create_end(s,c);CHECK(old_current(s,slot));
 CHECK(s->birth[slot].record==257&&s->birth[slot].mode==1);
}
static void empty_birth(const RearP1State *s,unsigned slot)
{
 const RearP1Birth *b=&s->birth[slot];
 CHECK(!b->qualified&&!b->record&&!b->mode&&!b->phase&&!b->raw&&!b->generation);
}
static void observed(RearP1State *s,unsigned slot,unsigned p)
{
 /* Inspect before current() can revoke a stale recycled birth itself. */
 if(!drawable(p))empty_birth(s,slot);
 CHECK(current(s,slot,p)==drawable(p));
 if(drawable(p)) {
  CHECK(s->birth[slot].qualified&&s->birth[slot].record==268&&s->birth[slot].mode==2);
  CHECK(s->birth[slot].phase==p&&s->birth[slot].raw==ids[p-1]&&s->birth[slot].generation==s->generation);
 }
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
{for(unsigned n=1;n<=count;n++)CHECK(current(s,n,phase(start,n))==(n!=except&&drawable(phase(start,n))));}
static void cyclic_capacities(RearP1State *s)
{
 unsigned seen[5][5]={{0}};
 /* All five cyclic starts, previous capacities 0..4, new capacities 0..5. */
 for(unsigned start=1;start<=5;start++)for(unsigned prior=0;prior<=4;prior++)for(unsigned cap=0;cap<=5;cap++) {
  rear_p1_reset(s);
  for(unsigned n=1;n<=prior;n++)prime(s,20+n);
  for(unsigned n=1;n<=cap;n++)prime(s,10+n);
  uint64_t c=begin(s);
  for(unsigned n=1;n<=prior;n++) {emit(s,c,n,20+n,phase(start,n));observed(s,20+n,phase(start,n));}
  rear_p1_create_end(s,c);clear(s);
  unsigned next=phase(start,prior+1);c=begin(s);
  for(unsigned n=1;n<=cap;n++) {
   unsigned p=phase(next,n);emit(s,c,n,10+n,p);observed(s,10+n,p);
   /* Non-drawable observations must still consume budget, advance the cycle,
    * retain the live lease and participate in every-prior-slot uniqueness. */
   CHECK(s->remaining==5-n&&s->used_count==n&&s->next_ordinal==n+1);
   CHECK(s->next_phase==phase(next,n+1)&&s->lease==(n<5)&&s->call==c);
   for(unsigned k=1;k<=n;k++)CHECK(s->used_slots[k-1]==10+k);
   seen[p-1][n-1]++;
  }
  rear_p1_create_end(s,c);clear(s);
  for(unsigned n=1;n<=cap;n++)observed(s,10+n,phase(next,n));
  for(unsigned n=1;n<=prior;n++)observed(s,20+n,phase(start,n));
  emit(s,c,cap+1,0,phase(next,cap+1));CHECK(!current(s,0,phase(next,cap+1)));clear(s);
 }
 for(unsigned p=0;p<5;p++)for(unsigned n=0;n<5;n++)CHECK(seen[p][n]>0);
 /* Sixth and later distinct allocations cannot borrow the exhausted grant. */
 for(unsigned start=1;start<=5;start++) {
  rear_p1_reset(s);uint64_t c=begin(s);
  for(unsigned n=1;n<=5;n++)emit(s,c,n,n,phase(start,n));
  for(unsigned n=6;n<=9;n++) {
   emit(s,c,n,n,phase(start,n));CHECK(!current(s,n,phase(start,n)));clear(s);retained(s,start,5,0);
  }
 }
 /* Repeat ANY prior slot, explicitly including slots used by pass-throughs.
  * A reused slot is revoked; distinct earlier drawable births survive. */
 for(unsigned start=1;start<=5;start++)for(unsigned bad=2;bad<=6;bad++)for(unsigned reused=1;reused<bad;reused++) {
  rear_p1_reset(s);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,reused,phase(start,bad));clear(s);empty_birth(s,reused);retained(s,start,bad-1,reused);
  for(unsigned n=bad+1;n<=7;n++) {emit(s,c,n,n,phase(start,n));CHECK(!current(s,n,phase(start,n)));}
  retained(s,start,bad-1,reused);
 }
}
static void rejected_allocations(RearP1State *s)
{
 /* Reject every context component and immutable field at every ordinal and
  * cyclic start. In particular, malformed pass-throughs cancel the grant. */
 for(unsigned start=1;start<=5;start++)for(unsigned bad=1;bad<=5;bad++)for(unsigned kind=0;kind<43;kind++) {
  rear_p1_reset(s);prime(s,79);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  unsigned p=phase(start,bad),slot=kind==0?80:kind==1?81:kind==2?UINT_MAX:bad;
  unsigned raw=kind==3?0:kind==4?ids[p-1]+1000:kind==5?ids[p%5]:kind==39?UINT_MAX:ids[p-1];
  RearP1Shot q=shot(p);if(kind>=26&&kind<39)mutate(&q,kind-26);RearP1Shot copy=q;
  rear_p1_emit(s,kind==6?8:kind==7?UINT64_MAX:7,kind==8?c+1:kind==9?0:c,
   kind==10?0:kind==11?bad+1:kind==12?UINT_MAX:bad,slot,
   kind==13?37:10,kind==14?0:kind==41?UINT_MAX:1,kind==15?257:kind==16?267:kind==42?269:268,kind==17?2:kind==40?0:1,
   kind==18?0:kind==19?6:kind==20?UINT_MAX:kind==21?p%5+1:p,raw,
   kind==22?NULL:&q,kind!=23,kind!=24,kind!=25);
  CHECK(!memcmp(&q,&copy,sizeof q));clear(s);
  if(slot<REAR_P1_SLOTS)empty_birth(s,slot);
  CHECK(!current(s,slot,p));retained(s,start,bad-1,0);
  CHECK(old_current(s,79)&&s->birth[79].record==257&&s->birth[79].mode==1);
  if(slot<REAR_P1_SLOTS)CHECK(!s->birth[slot].qualified);else CHECK(old_current(s,bad));
  for(unsigned n=bad+1;n<=6;n++) {emit(s,c,n,n,phase(start,n));CHECK(!current(s,n,phase(start,n)));}
  retained(s,start,bad-1,0);CHECK(old_current(s,79));
 }
 /* Every slot, including both bounds, is valid for every observation phase. */
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)for(unsigned p=1;p<=5;p++) {
  rear_p1_reset(s);prime(s,slot);uint64_t c=begin(s);emit(s,c,1,slot,p);observed(s,slot,p);
  CHECK(s->lease&&s->remaining==4&&s->used_count==1&&s->used_slots[0]==slot);
  rear_p1_create_end(s,c);observed(s,slot,p);
  c=rear_p1_create_begin(s,7,10,1,268,1);emit(s,c,1,slot,p);CHECK(!current(s,slot,p));clear(s);
 }
 /* Out-of-bounds reads/writes preserve every in-bounds birth. */
 const unsigned outside[]={80,81,UINT_MAX};
 for(unsigned k=0;k<sizeof outside/sizeof *outside;k++) {
  rear_p1_reset(s);prime(s,79);uint64_t c=begin(s);for(unsigned n=1;n<=5;n++)emit(s,c,n,n,n);
  RearP1Birth copy[REAR_P1_SLOTS];memcpy(copy,s->birth,sizeof copy);
  CHECK(!current(s,outside[k],5));CHECK(!memcmp(copy,s->birth,sizeof copy));
  emit(s,c,6,outside[k],1);clear(s);CHECK(!memcmp(copy,s->birth,sizeof copy));retained(s,1,5,0);CHECK(old_current(s,79));
 }
}
static void isolation(RearP1State *s)
{
 for(unsigned start=1;start<=5;start++)for(unsigned after=0;after<=5;after++)for(unsigned kind=0;kind<10;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=after;n++)emit(s,c,n,n,phase(start,n));
  uint64_t inner=0;
  if(kind==0)inner=rear_p1_create_begin(s,7,10,1,268,1);
  if(kind==1)rear_p1_create_end(s,c);
  if(kind==2)rear_p1_call_end(s);
  if(kind==3)rear_p1_reset(s);
  if(kind>=4) {
   rear_p1_call_begin(s,7,10,1,3,1,1,268,true,true);
   inner=rear_p1_create_begin(s,kind==4?8:7,kind==5?37:10,kind==6?0:1,kind==7?257:kind==9?267:268,kind==8?2:1);
  }
  if(inner) {CHECK(inner!=c);emit(s,inner,1,10,start);CHECK(!current(s,10,start));rear_p1_create_end(s,inner);}
  emit(s,c,after+1,11,phase(start,after+1));CHECK(!current(s,11,phase(start,after+1)));clear(s);
  for(unsigned n=1;n<=after;n++)CHECK(current(s,n,phase(start,n))==(kind!=3&&drawable(phase(start,n))));
 }
 /* Pending without an actual creator, zero capacity, and stale calls. */
 rear_p1_reset(s);rear_p1_call_begin(s,7,10,1,3,1,1,268,true,true);
 emit(s,0,1,0,5);CHECK(!current(s,0,5));clear(s);
 rear_p1_reset(s);uint64_t c=begin(s);rear_p1_create_end(s,c);clear(s);
 uint64_t inner=rear_p1_create_begin(s,7,10,1,268,1);CHECK(inner!=c&&!s->lease);
 emit(s,inner,1,0,5);CHECK(!current(s,0,5));clear(s);
 c=begin(s);rear_p1_create_end(s,c);inner=begin(s);CHECK(inner!=c);
 rear_p1_create_end(s,c);CHECK(s->lease&&s->call==inner);
 emit(s,inner,1,0,5);CHECK(current(s,0,5));
 emit(s,c,2,1,1);CHECK(!current(s,1,1)&&current(s,0,5));clear(s);
 emit(s,inner,2,2,2);CHECK(!current(s,2,2));
 /* Token/generation wrapping never produces zero or revives old ownership. */
 rear_p1_reset(s);s->call_serial=UINT64_MAX;c=begin(s);CHECK(c==1);
 emit(s,c,1,0,5);CHECK(current(s,0,5));s->generation=UINT64_MAX;rear_p1_reset(s);
 CHECK(s->generation==1&&!current(s,0,5));clear(s);inner=begin(s);CHECK(inner!=c);
 emit(s,c,1,1,3);CHECK(!current(s,1,3));clear(s);
}
static bool admitted(unsigned power,unsigned mode,unsigned record)
{
 return (power<2&&mode<2&&record==(mode?265:254)+power)||
  (power==2&&mode<2&&record==(mode?267:256))||(power==3&&mode<2&&record==(mode?268:257))||(power==4&&mode==1&&record==269);
}
static void admission(RearP1State *s)
{
 const unsigned records[]={0,1,50,77,163,164,182,183,253,254,255,256,257,258,264,265,266,267,268,269,275,281,300,445,501,686,687,688,690,1257,1268,UINT_MAX};
 const unsigned powers[]={0,1,2,3,4,5,6,7,8,9,10,11,UINT_MAX};
 const unsigned modes[]={0,1,2,3,UINT_MAX};
 for(unsigned p=0;p<sizeof powers/sizeof *powers;p++)for(unsigned m=0;m<sizeof modes/sizeof *modes;m++)for(unsigned r=0;r<sizeof records/sizeof *records;r++) {
  unsigned power=powers[p],mode=modes[m],record=records[r];bool yes=admitted(power,mode,record);
  rear_p1_call_begin(s,7,10,1,power,mode,1,record,true,true);CHECK(s->pending==yes);
  CHECK(s->budget==(yes?(power==4?4:power==3?5:power==2?(mode?4:2):power+1):0));
  uint64_t c=rear_p1_create_begin(s,7,10,1,record,1);CHECK(s->lease==yes);
  if(!yes) {emit(s,c,1,0,5);CHECK(!current(s,0,5));clear(s);}else rear_p1_create_end(s,c);
 }
 const unsigned ports[]={0,10,19,22,27,32,37,UINT_MAX},bays[]={0,1,2,UINT_MAX},players[]={0,1,2,UINT_MAX};
 for(unsigned p=0;p<sizeof ports/sizeof *ports;p++)for(unsigned b=0;b<sizeof bays/sizeof *bays;b++)for(unsigned u=0;u<sizeof players/sizeof *players;u++)for(unsigned scope=0;scope<2;scope++)for(unsigned table=0;table<2;table++) {
  bool yes=ports[p]==10&&bays[b]==1&&players[u]==1&&scope&&table;
  rear_p1_call_begin(s,7,ports[p],bays[b],3,1,players[u],268,scope!=0,table!=0);CHECK(s->pending==yes);
  rear_p1_call_end(s);clear(s);
 }
 CHECK(REAR_P1_HEADS==13&&REAR_P1_OBSERVED==15&&REAR_P1_MAX_BUDGET==5);
 const unsigned members[]={39,1,281,282,301,300,40,2,77,182,183,277,278};
 const unsigned observations[]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278};
 for(unsigned k=0;k<9;k++)CHECK(rear_p1_member(members[k])==(int)k);
 for(unsigned raw=0;raw<8000;raw++) {
  bool draw=false,observe=false;
  for(unsigned k=0;k<sizeof members/sizeof *members;k++)draw|=raw==members[k];
  for(unsigned k=0;k<sizeof observations/sizeof *observations;k++)observe|=raw==observations[k];
  CHECK((rear_p1_member(raw)>=0)==draw);CHECK((rear_p1_observed(raw)>=0)==observe);
  if(draw)CHECK(rear_p1_member(raw)<REAR_P1_HEADS);
  if(observe)CHECK(rear_p1_observed(raw)<REAR_P1_OBSERVED);
 }
 for(unsigned a=0;a<REAR_P1_HEADS;a++)for(unsigned b=a+1;b<REAR_P1_HEADS;b++)CHECK(rear_p1_member(members[a])!=rear_p1_member(members[b]));
 for(unsigned a=0;a<REAR_P1_OBSERVED;a++)for(unsigned b=a+1;b<REAR_P1_OBSERVED;b++)CHECK(rear_p1_observed(observations[a])!=rear_p1_observed(observations[b]));
 CHECK(rear_p1_member(163)<0&&rear_p1_member(164)<0);
 CHECK(rear_p1_member(UINT_MAX)<0&&rear_p1_observed(UINT_MAX)<0);
}
static void one_way_revocation(RearP1State *s)
{
 for(unsigned p=3;p<=5;p++)for(unsigned field=0;field<13;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
  RearP1Shot q=shot(p);mutate(&q,field);RearP1Shot copy=q;
  CHECK(!rear_p1_current(s,79,ids[p-1],ids[p-1],&q,true,true,true));
  CHECK(!memcmp(&q,&copy,sizeof q));CHECK(!s->birth[79].qualified&&!current(s,79,p));
  rear_p1_create_end(s,c);c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
 }
 const unsigned aliases[]={0,1,2,39,40,77,163,164,182,183,281,282,300,301,1077,1163,1164,1182,1183,6077,6182,UINT_MAX};
 for(unsigned p=3;p<=5;p++)for(unsigned a=0;a<sizeof aliases/sizeof *aliases;a++)for(unsigned field=0;field<3;field++)if(aliases[a]!=ids[p-1]) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  unsigned index=field==0||field==2?aliases[a]:ids[p-1],raw=field==1||field==2?aliases[a]:ids[p-1];
  CHECK(!rear_p1_current(s,0,index,raw,&q,true,true,true));CHECK(!current(s,0,p));
 }
 for(unsigned p=3;p<=5;p++)for(unsigned kind=0;kind<4;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  CHECK(!rear_p1_current(s,0,ids[p-1],ids[p-1],kind==3?NULL:&q,kind!=0,kind!=1,kind!=2));CHECK(!current(s,0,p));
 }
 /* Each birth validates its own immutable mode/record, even for shared ID77. */
 for(unsigned p=3;p<=5;p++)for(unsigned field=0;field<11;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Birth before=s->birth[0];
  switch(field) {
  case 0:s->birth[0].generation++;break;case 1:s->birth[0].record=257;break;
  case 2:s->birth[0].phase=0;break;case 3:s->birth[0].phase=6;break;
  case 4:s->birth[0].raw++;break;case 5:s->birth[0].mode=1;break;
  case 6:s->birth[0].mode=0;break;case 7:s->birth[0].phase=p%5+1;break;
  case 8:s->birth[0].qualified=false;break;case 9:s->birth[0].record=269;break;
  case 10:s->birth[0].mode=UINT_MAX;break;
  }
  CHECK(!current(s,0,p)&&!s->birth[0].qualified);
  before.qualified=false;s->birth[0]=before;CHECK(!current(s,0,p));
 }
 /* Even a forged qualified bit cannot make pass-through IDs renderer-owned. */
 for(unsigned p=1;p<=2;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
  rear_p1_reset(s);prime(s,slot);uint64_t c=begin(s);emit(s,c,1,slot,p);observed(s,slot,p);
  s->birth[slot]=(RearP1Birth){true,268,2,p,ids[p-1],s->generation};
  CHECK(!current(s,slot,p)&&!s->birth[slot].qualified);CHECK(!current(s,slot,p));
 }
}
static void coexistence(RearP1State *s)
{
 const unsigned oldids[]={39,1,281,282,301,300,40,2,77};
 const int ox[]={-10,10,-9,9,9,-9,-10,10,0},oy[]={0,0,-2,-2,2,2,0,0,10};
 const unsigned records[]={254,255,256,265,266,267,257};
 RearP1Shot births[24];unsigned count=0;
 rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=5;n++)emit(s,c,n,70+n,n);rear_p1_create_end(s,c);
 /* Every admitted prior tuple and all phases coexist with the three new births. */
 for(unsigned r=0;r<sizeof records/sizeof *records;r++) {
  unsigned record=records[r],mode=record>=265,power=record-(mode?265:254),period=record==257?5:mode?4:2;
  for(unsigned p=1;p<=period;p++) {
   unsigned k=record==256?p+5:record==257?(p==5?8:p+1):mode?p+1:p-1;
   RearP1Shot q={oldids[k],0,1,1,255,0,0,0,208,ox[k],oy[k],0,0};
   rear_p1_call_begin(s,8,10,1,power,mode,1,record,true,true);c=rear_p1_create_begin(s,8,10,1,record,1);
   rear_p1_emit(s,8,c,1,count,10,1,record,1,p,oldids[k],&q,true,true,true);
   CHECK(rear_p1_current(s,count,oldids[k],oldids[k],&q,true,true,true));births[count++]=q;
   rear_p1_create_end(s,c);for(unsigned n=1;n<=5;n++)observed(s,70+n,n);
  }
 }
 CHECK(count==23);
 /* Active equipment, including unsupported power/mode combinations, cannot
  * reinterpret either retained mode1 ID77 or retained mode2 ID77. */
 c=begin(s);for(unsigned n=1;n<=5;n++)emit(s,c,n,70+n,n);rear_p1_create_end(s,c);
 for(unsigned power=0;power<12;power++)for(unsigned mode=0;mode<3;mode++) {
  rear_p1_call_begin(s,9,10,1,power,mode,1,(mode?265:254)+power,true,true);rear_p1_call_end(s);
  for(unsigned n=1;n<=5;n++)observed(s,70+n,n);
  for(unsigned k=0;k<count;k++)CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true));
 }
 CHECK(s->birth[22].record==257&&s->birth[22].mode==1&&s->birth[22].raw==77);
 CHECK(s->birth[75].record==268&&s->birth[75].mode==2&&s->birth[75].raw==77);
 /* Two valid pass-throughs recycle one old/new drawable slot apiece. They
  * preserve distinct births and keep the grant usable for the three draws. */
 c=begin(s);emit(s,c,1,22,1);observed(s,22,1);CHECK(s->lease&&s->used_count==1);
 emit(s,c,2,75,2);observed(s,75,2);CHECK(s->lease&&s->used_count==2);
 for(unsigned p=3;p<=5;p++) {emit(s,c,p,60+p,p);observed(s,60+p,p);}
 rear_p1_create_end(s,c);clear(s);
 for(unsigned k=0;k<count-1;k++)CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true));
 for(unsigned p=3;p<=4;p++)observed(s,70+p,p);
 rear_p1_reset(s);
 for(unsigned n=1;n<=5;n++)CHECK(!current(s,70+n,n));
 for(unsigned p=3;p<=5;p++)CHECK(!current(s,60+p,p));
 for(unsigned k=0;k<count;k++)CHECK(!rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true));
}
int main(void)
{
 RearP1State state={0};cyclic_capacities(&state);rejected_allocations(&state);isolation(&state);
 admission(&state);one_way_revocation(&state);coexistence(&state);
 printf("Rear P4 mode2 ownership PASS: %u checks; five cyclic starts, prior0..4/new0..5 capacities, pass-through lease and slot accounting, all-prior reuse, fail-closed rejection, exact admission and mixed-mode births\n",checks);
 return 0;
}
