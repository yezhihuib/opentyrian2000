/* SPDX-License-Identifier: GPL-2.0-or-later
 * Generated/synthetic observations only. No game records or original art.
 * P5 mode1 is an exact two-observation renderer-ownership grant. */
#include "rear_multi_p1.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); exit(1); } } while (0)
static const unsigned ids[]={41,3};
static const int dx[]={-10,10},dy[]={0,0};
static unsigned phase(unsigned start,unsigned ordinal)
{return (start+ordinal-2)%2+1;}
static RearP1Shot shot(unsigned p)
{unsigned k=p-1;return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,dx[k],dy[k],0,0};}
static uint64_t begin(RearP1State *s)
{
 rear_p1_call_begin(s,7,10,1,4,0,1,258,true,true);
 CHECK(s->pending&&!s->lease&&s->budget==2&&s->record==258&&s->mode==1);
 uint64_t c=rear_p1_create_begin(s,7,10,1,258,1);
 CHECK(c&&s->lease&&!s->pending&&s->remaining==2&&s->next_ordinal==1&&!s->next_phase&&!s->used_count);
 return c;
}
static void emit(RearP1State *s,uint64_t c,unsigned n,unsigned slot,unsigned p)
{
 RearP1Shot q=shot(p),copy=q;
 rear_p1_emit(s,7,c,n,slot,10,1,258,1,p,ids[p-1],&q,true,true,true);
 CHECK(!memcmp(&q,&copy,sizeof q));
}
static bool current(RearP1State *s,unsigned slot,unsigned p)
{RearP1Shot q=shot(p);return rear_p1_current(s,slot,ids[p-1],ids[p-1],&q,true,true,true);}
static void clear(const RearP1State *s)
{
 CHECK(!s->pending&&!s->lease&&!s->call&&!s->remaining&&!s->budget&&!s->next_ordinal&&!s->next_phase&&!s->used_count);
 for(unsigned i=0;i<REAR_P1_MAX_BUDGET;i++)CHECK(!s->used_slots[i]);
}
static RearP1Shot old_shot(void)
{return (RearP1Shot){77,0,1,1,255,0,0,0,208,0,10,0,0};}
static bool old_current(RearP1State *s,unsigned slot)
{RearP1Shot q=old_shot();return rear_p1_current(s,slot,77,77,&q,true,true,true);}
static void prime(RearP1State *s,unsigned slot)
{
 /* Recycling must revoke actual retained ownership, not an already empty slot. */
 RearP1Shot q=old_shot();
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
 CHECK(!s->birth_identity[slot]);
}
static void observed(RearP1State *s,unsigned slot,unsigned p)
{
 CHECK(current(s,slot,p));
 CHECK(s->birth[slot].qualified&&s->birth[slot].record==258&&s->birth[slot].mode==1);
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
 unsigned seen[2][2]={{0}};
 /* The real phase may continue after any partial capacity, including zero.
  * Each new creator has a fresh ordinal and two-allocation budget. */
 for(unsigned start=1;start<=2;start++)for(unsigned prior=0;prior<=2;prior++)for(unsigned cap=0;cap<=2;cap++) {
  rear_p1_reset(s);
  for(unsigned n=1;n<=prior;n++)prime(s,20+n);
  for(unsigned n=1;n<=cap;n++)prime(s,10+n);
  uint64_t c=begin(s);
  for(unsigned n=1;n<=prior;n++) {emit(s,c,n,20+n,phase(start,n));observed(s,20+n,phase(start,n));}
  rear_p1_create_end(s,c);clear(s);
  unsigned next=phase(start,prior+1);c=begin(s);
  for(unsigned n=1;n<=cap;n++) {
   unsigned p=phase(next,n);emit(s,c,n,10+n,p);observed(s,10+n,p);
   CHECK(s->remaining==2-n&&s->used_count==n&&s->next_ordinal==n+1);
   CHECK(s->next_phase==phase(next,n+1)&&s->lease==(n<2)&&s->call==c);
   for(unsigned k=1;k<=n;k++)CHECK(s->used_slots[k-1]==10+k);
   seen[p-1][n-1]++;
  }
  rear_p1_create_end(s,c);clear(s);
  for(unsigned n=1;n<=cap;n++)observed(s,10+n,phase(next,n));
  for(unsigned n=1;n<=prior;n++)observed(s,20+n,phase(start,n));
  emit(s,c,cap+1,0,phase(next,cap+1));empty_birth(s,0);CHECK(!current(s,0,phase(next,cap+1)));clear(s);
 }
 for(unsigned p=0;p<2;p++)for(unsigned n=0;n<2;n++)CHECK(seen[p][n]>0);
 /* Third and later allocations cannot inherit P4's five-shot or P5 mode2's four-shot budget. */
 for(unsigned start=1;start<=2;start++) {
  rear_p1_reset(s);for(unsigned n=3;n<=7;n++)prime(s,n);uint64_t c=begin(s);
  for(unsigned n=1;n<=2;n++)emit(s,c,n,n,phase(start,n));
  for(unsigned n=3;n<=7;n++) {
   emit(s,c,n,n,phase(start,n));empty_birth(s,n);CHECK(!current(s,n,phase(start,n)));clear(s);retained(s,start,2,0);
  }
 }
 /* Every earlier slot must be checked, not just the immediately previous one. */
 for(unsigned start=1;start<=2;start++)for(unsigned bad=2;bad<=3;bad++)for(unsigned reused=1;reused<bad;reused++) {
  rear_p1_reset(s);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,reused,phase(start,bad));clear(s);empty_birth(s,reused);retained(s,start,bad-1,reused);
  for(unsigned n=bad+1;n<=7;n++) {emit(s,c,n,n,phase(start,n));CHECK(!current(s,n,phase(start,n)));}
  retained(s,start,bad-1,reused);
 }
}
static void rejected_allocations(RearP1State *s)
{
 /* Each actual invalid observation revokes its recycled slot and destroys only
  * the remaining grant. Earlier distinct births and unrelated old births live. */
 for(unsigned start=1;start<=2;start++)for(unsigned bad=1;bad<=2;bad++)for(unsigned kind=0;kind<54;kind++) {
  rear_p1_reset(s);prime(s,79);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  unsigned p=phase(start,bad),slot=kind==0?80:kind==1?81:kind==2?UINT_MAX:bad;
  unsigned raw=kind==3?0:kind==4?ids[p-1]+1000:kind==5?ids[p%2]:kind==39?UINT_MAX:kind==43?163:kind==44?164:ids[p-1];
  RearP1Shot q=shot(p);if(kind>=26&&kind<39)mutate(&q,kind-26);RearP1Shot copy=q;
  rear_p1_emit(s,kind==6?8:kind==7?UINT64_MAX:kind==45?0:7,kind==8?c+1:kind==9?0:c,
   kind==10?0:kind==11?bad+1:kind==12?UINT_MAX:bad,slot,
   kind==13?37:kind==46?0:kind==47?UINT_MAX:10,
   kind==14?0:kind==41?UINT_MAX:kind==48?2:1,
   kind==15?269:kind==16?267:kind==42?268:kind==49?0:kind==50?UINT_MAX:258,
   kind==17?2:kind==40?0:kind==51?UINT_MAX:1,
   kind==18?0:kind==19?3:kind==20?UINT_MAX:kind==21?p%2+1:kind==52?p+2:p,raw,
   kind==22?NULL:&q,kind!=23,kind!=24,kind!=25&&kind!=53);
  CHECK(!memcmp(&q,&copy,sizeof q));clear(s);
  if(slot<REAR_P1_SLOTS)empty_birth(s,slot);
  CHECK(!current(s,slot,p));retained(s,start,bad-1,0);
  CHECK(old_current(s,79)&&s->birth[79].record==257&&s->birth[79].mode==1);
  if(slot>=REAR_P1_SLOTS)CHECK(old_current(s,bad));
  for(unsigned n=bad+1;n<=6;n++) {emit(s,c,n,n,phase(start,n));CHECK(!current(s,n,phase(start,n)));}
  retained(s,start,bad-1,0);CHECK(old_current(s,79));
 }
 /* The entire fixed slot range and every canonical phase can start a call. */
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)for(unsigned p=1;p<=2;p++) {
  rear_p1_reset(s);prime(s,slot);uint64_t c=begin(s);emit(s,c,1,slot,p);observed(s,slot,p);
  CHECK(s->lease&&s->remaining==1&&s->used_count==1&&s->used_slots[0]==slot);
  rear_p1_create_end(s,c);observed(s,slot,p);
  c=rear_p1_create_begin(s,7,10,1,258,1);emit(s,c,1,slot,p);empty_birth(s,slot);CHECK(!current(s,slot,p));clear(s);
 }
 const unsigned outside[]={80,81,UINT_MAX};
 for(unsigned k=0;k<sizeof outside/sizeof *outside;k++) {
  rear_p1_reset(s);prime(s,79);uint64_t c=begin(s);for(unsigned n=1;n<=2;n++)emit(s,c,n,n,n);
  RearP1Birth copy[REAR_P1_SLOTS];memcpy(copy,s->birth,sizeof copy);
  CHECK(!current(s,outside[k],1));CHECK(!memcmp(copy,s->birth,sizeof copy));
  emit(s,c,3,outside[k],1);clear(s);CHECK(!memcmp(copy,s->birth,sizeof copy));retained(s,1,2,0);CHECK(old_current(s,79));
 }
}
static void canonical_mismatches(RearP1State *s)
{
 /* Keep raw and live-shot identity internally valid so phase/order checks are
  * independently necessary, rather than hidden by a second malformed field. */
 const unsigned rawids[]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278,41,3,296,297};
 const int vx[]={-10,10,-9,9,9,-9,-10,10,0,-6,6,-6,6,-9,9,-10,10,-9,9};
 const int vy[]={0,0,-2,-2,2,2,0,0,10,6,6,-6,-6,-2,-2,0,0,2,2};
 for(unsigned start=1;start<=2;start++)for(unsigned bad=1;bad<=2;bad++)for(unsigned k=0;k<sizeof rawids/sizeof *rawids;k++) {
  unsigned p=phase(start,bad);if(rawids[k]==ids[p-1])continue;
  rear_p1_reset(s);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  RearP1Shot q={rawids[k],0,1,1,255,0,0,0,208,vx[k],vy[k],0,0},copy=q;
  rear_p1_emit(s,7,c,bad,bad,10,1,258,1,p,rawids[k],&q,true,true,true);
  CHECK(!memcmp(&q,&copy,sizeof q));empty_birth(s,bad);clear(s);retained(s,start,bad-1,0);
  emit(s,c,bad+1,bad+1,phase(start,bad+1));CHECK(!current(s,bad+1,phase(start,bad+1)));
 }
 /* A canonical but reordered phase must cancel, even with its own correct
  * raw ID and shot fields. The first phase remains free to start anywhere. */
 for(unsigned start=1;start<=2;start++)for(unsigned bad=2;bad<=2;bad++)for(unsigned p=1;p<=2;p++) {
  if(p==phase(start,bad))continue;
  rear_p1_reset(s);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,bad,p);empty_birth(s,bad);clear(s);retained(s,start,bad-1,0);
  emit(s,c,bad+1,bad+1,phase(start,bad+1));CHECK(!current(s,bad+1,phase(start,bad+1)));
 }
 /* Slot zero is a valid used slot, not a sentinel that can bypass uniqueness. */
 for(unsigned start=1;start<=2;start++)for(unsigned bad=2;bad<=3;bad++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,start);
  for(unsigned n=2;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,0,phase(start,bad));empty_birth(s,0);clear(s);
  for(unsigned n=2;n<bad;n++)observed(s,n,phase(start,n));
 }
}
static void isolation(RearP1State *s)
{
 for(unsigned start=1;start<=2;start++)for(unsigned after=0;after<=2;after++)for(unsigned kind=0;kind<15;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=after;n++)emit(s,c,n,n,phase(start,n));
  uint64_t inner=0;
  if(kind==0)inner=rear_p1_create_begin(s,7,10,1,258,1);
  if(kind==1)rear_p1_create_end(s,c);
  if(kind==2)rear_p1_call_end(s);
  if(kind==3)rear_p1_reset(s);
  if(kind>=4) {
   rear_p1_call_begin(s,7,10,1,4,0,1,258,true,true);
   inner=rear_p1_create_begin(s,kind==4?8:kind==10?0:kind==11?UINT64_MAX:7,
    kind==5?37:kind==12?UINT_MAX:10,kind==6?0:kind==13?UINT_MAX:1,
    kind==7?269:kind==9?268:kind==14?UINT_MAX:258,kind==8?2:1);
  }
  if(inner) {CHECK(inner!=c);emit(s,inner,1,10,start);CHECK(!current(s,10,start));rear_p1_create_end(s,inner);}
  emit(s,c,after+1,11,phase(start,after+1));CHECK(!current(s,11,phase(start,after+1)));clear(s);
  for(unsigned n=1;n<=after;n++)CHECK(current(s,n,phase(start,n))==(kind!=3));
 }
 /* Pending without a real creator, zero capacity, stale ends and stale emits. */
 rear_p1_reset(s);prime(s,0);rear_p1_call_begin(s,7,10,1,4,0,1,258,true,true);
 emit(s,0,1,0,1);empty_birth(s,0);CHECK(!current(s,0,1));clear(s);
 rear_p1_reset(s);uint64_t c=begin(s);rear_p1_create_end(s,c);clear(s);
 uint64_t inner=rear_p1_create_begin(s,7,10,1,258,1);CHECK(inner!=c&&!s->lease);
 emit(s,inner,1,0,1);CHECK(!current(s,0,1));clear(s);
 c=begin(s);rear_p1_create_end(s,c);inner=begin(s);CHECK(inner!=c);
 rear_p1_create_end(s,c);CHECK(s->lease&&s->call==inner);
 emit(s,inner,1,0,1);CHECK(current(s,0,1));
 emit(s,c,2,1,2);CHECK(!current(s,1,2)&&current(s,0,1));clear(s);
 emit(s,inner,2,2,2);CHECK(!current(s,2,2));
 /* Token and generation wrap never produce zero or revive earlier births. */
 rear_p1_reset(s);s->call_serial=UINT64_MAX;c=begin(s);CHECK(c==1);
 emit(s,c,1,0,1);CHECK(current(s,0,1));s->generation=UINT64_MAX;rear_p1_reset(s);
 CHECK(s->generation==1&&!current(s,0,1));clear(s);inner=begin(s);CHECK(inner!=c);
 emit(s,c,1,1,1);CHECK(!current(s,1,1));clear(s);
}
static bool admitted(unsigned power,unsigned mode,unsigned record)
{
 return (power<2&&mode<2&&record==(mode?265:254)+power)||
  (power==2&&mode<2&&record==(mode?267:256))||(power==3&&mode<2&&record==(mode?268:257))||
  (power==4&&mode<2&&record==(mode?269:258))||(power==5&&mode<2&&record==(mode?270:259))||(power==6&&mode<2&&record==(mode?271:260));
}
static unsigned budget(unsigned power,unsigned mode)
{return power==6?(mode?5:4):power==5?(mode?5:3):power==4?(mode?4:2):power==3?5:power==2?(mode?4:2):power+1;}
static void admission(RearP1State *s)
{
 const unsigned records[]={0,1,50,77,163,164,182,183,253,254,255,256,257,258,259,264,265,266,267,268,269,270,275,277,278,281,300,445,501,686,687,688,690,1257,1269,UINT_MAX};
 const unsigned powers[]={0,1,2,3,4,5,6,7,8,9,10,11,UINT_MAX};
 const unsigned modes[]={0,1,2,3,UINT_MAX};
 for(unsigned p=0;p<sizeof powers/sizeof *powers;p++)for(unsigned m=0;m<sizeof modes/sizeof *modes;m++)for(unsigned r=0;r<sizeof records/sizeof *records;r++) {
  unsigned power=powers[p],mode=modes[m],record=records[r];bool yes=admitted(power,mode,record);
  rear_p1_call_begin(s,7,10,1,power,mode,1,record,true,true);CHECK(s->pending==yes);
  CHECK(s->budget==(yes?budget(power,mode):0));
  uint64_t c=rear_p1_create_begin(s,7,10,1,record,1);CHECK(s->lease==yes);
  CHECK(s->remaining==(yes?budget(power,mode):0));
  if(!yes) {emit(s,c,1,0,1);CHECK(!current(s,0,1));clear(s);}else rear_p1_create_end(s,c);
 }
 const unsigned ports[]={0,10,19,22,27,32,37,UINT_MAX},bays[]={0,1,2,UINT_MAX},players[]={0,1,2,UINT_MAX};
 for(unsigned p=0;p<sizeof ports/sizeof *ports;p++)for(unsigned b=0;b<sizeof bays/sizeof *bays;b++)for(unsigned u=0;u<sizeof players/sizeof *players;u++)for(unsigned scope=0;scope<2;scope++)for(unsigned table=0;table<2;table++) {
  bool yes=ports[p]==10&&bays[b]==1&&players[u]==1&&scope&&table;
  rear_p1_call_begin(s,7,ports[p],bays[b],4,0,players[u],258,scope!=0,table!=0);CHECK(s->pending==yes);
  rear_p1_call_end(s);clear(s);
 }
 CHECK(REAR_P1_HEADS==19&&REAR_P1_OBSERVED==21&&REAR_P1_MAX_BUDGET==5);
 const unsigned members[]={39,1,281,282,301,300,40,2,77,182,183,277,278,41,3,296,297,294,295};
 const unsigned observations[]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278,41,3,296,297,294,295};
 /* Append-only role maps are intentionally different after the original 11. */
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
 for(unsigned p=1;p<=2;p++)for(unsigned field=0;field<13;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
  RearP1Shot q=shot(p);mutate(&q,field);RearP1Shot copy=q;
  CHECK(!rear_p1_current(s,79,ids[p-1],ids[p-1],&q,true,true,true));
  CHECK(!memcmp(&q,&copy,sizeof q));CHECK(!s->birth[79].qualified&&!current(s,79,p));
  rear_p1_create_end(s,c);c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
 }
 const unsigned aliases[]={0,1,2,3,39,40,41,77,163,164,182,183,277,278,281,282,300,301,1003,1041,1182,1183,1277,1278,6041,UINT_MAX};
 for(unsigned p=1;p<=2;p++)for(unsigned a=0;a<sizeof aliases/sizeof *aliases;a++)for(unsigned field=0;field<3;field++)if(aliases[a]!=ids[p-1]) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  unsigned index=field==0||field==2?aliases[a]:ids[p-1],raw=field==1||field==2?aliases[a]:ids[p-1];
  CHECK(!rear_p1_current(s,0,index,raw,&q,true,true,true));CHECK(!current(s,0,p));
 }
 for(unsigned p=1;p<=2;p++)for(unsigned kind=0;kind<4;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  CHECK(!rear_p1_current(s,0,ids[p-1],ids[p-1],kind==3?NULL:&q,kind!=0,kind!=1,kind!=2));CHECK(!current(s,0,p));
 }
 for(unsigned p=1;p<=2;p++)for(unsigned field=0;field<15;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Birth before=s->birth[0];
  switch(field) {
  case 0:s->birth[0].generation++;break;case 1:s->birth[0].record=257;break;
  case 2:s->birth[0].phase=0;break;case 3:s->birth[0].phase=3;break;
  case 4:s->birth[0].raw++;break;case 5:s->birth[0].mode=2;break;
  case 6:s->birth[0].mode=0;break;case 7:s->birth[0].phase=p%2+1;break;
  case 8:s->birth[0].qualified=false;break;case 9:s->birth[0].record=269;break;
  case 10:s->birth[0].mode=UINT_MAX;break;case 11:s->birth[0].record=0;break;
  case 12:s->birth[0].record=UINT_MAX;break;case 13:s->birth[0].phase=UINT_MAX;break;
  case 14:s->birth[0].generation=0;break;
  }
  CHECK(!current(s,0,p)&&!s->birth[0].qualified);
  before.qualified=false;s->birth[0]=before;CHECK(!current(s,0,p));
 }
 /* Pass-through ownership remains forbidden, even with a forged qualified bit. */
 for(unsigned p=1;p<=2;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
  rear_p1_reset(s);RearP1Shot q={p==1?163:164,0,1,1,255,0,0,0,208,p==1?-6:6,-6,0,0};
  s->birth[slot]=(RearP1Birth){true,268,2,p,q.gr,s->generation};
  CHECK(!rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true)&&!s->birth[slot].qualified);
 }
}
/* Explicit source-specific synthetic observations. No original records are read. */
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
 {269,4,1,4,4,{277,278,183,182},{-9,9,6,-6},{-2,-2,6,6}}
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
 rear_p1_emit(s,9,c,n,slot,10,1,a->record,1,p,q.gr,&q,true,true,true);
 CHECK(!memcmp(&q,&copy,sizeof q));
}
static bool source_current(RearP1State *s,const Source *a,unsigned slot,unsigned p)
{RearP1Shot q=source_shot(a,p);return rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true);}
static void source_budgets(RearP1State *s)
{
 /* Changing power/mode/source cannot inherit the preceding creator's budget,
  * even after zero, partial, or full capacity. Check every source transition. */
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
static void every_slot_pair(RearP1State *s)
{
 /* Exhaust all 80x80 pairs, including both edges, gaps and slot zero. A third
  * allocation reusing the non-adjacent first slot clears only that old birth. */
 for(unsigned start=1;start<=2;start++)for(unsigned first=0;first<REAR_P1_SLOTS;first++)
 for(unsigned second=0;second<REAR_P1_SLOTS;second++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,first,start);
  emit(s,c,2,second,phase(start,2));
  if(first==second) {empty_birth(s,first);clear(s);continue;}
  observed(s,first,start);observed(s,second,phase(start,2));
  CHECK(!s->lease&&!s->remaining&&s->used_count==2&&s->next_ordinal==3);
  CHECK(s->used_slots[0]==first&&s->used_slots[1]==second);
  emit(s,c,3,first,start);empty_birth(s,first);clear(s);observed(s,second,phase(start,2));
 }
}
static void excluded_shared_sources(RearP1State *s)
{
 /* P6/P9 mode1 also share 3/41. Valid raw IDs and canonical live fields are
  * deliberately insufficient without exact P5 record258 provenance. */
 const unsigned records[]={259,260,261,262,263,264,270,273,41,3,1258,0,UINT_MAX};
 const unsigned powers[]={0,1,2,3,4,5,6,7,8,9,10,11,UINT_MAX};
 for(unsigned r=0;r<sizeof records/sizeof *records;r++)
 for(unsigned power=0;power<sizeof powers/sizeof *powers;power++)
 for(unsigned mode=0;mode<3;mode++)for(unsigned p=1;p<=2;p++) {
  if(powers[power]==6&&records[r]==(mode?271u:260u))continue; /* Exact P7 route has its own tests. */
  if(powers[power]==5&&((records[r]==259&&mode==0)||(records[r]==270&&mode==1)))continue; /* Exact P6 routes have their own tests. */
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);emit(s,c,2,79,phase(p,2));rear_p1_create_end(s,c);
  rear_p1_call_begin(s,7,10,1,powers[power],mode,1,records[r],true,true);CHECK(!s->pending&&!s->budget);
  c=rear_p1_create_begin(s,7,10,1,records[r],1);CHECK(!s->lease);
  RearP1Shot q=shot(p),copy=q;
  rear_p1_emit(s,7,c,1,0,10,1,records[r],1,p,q.gr,&q,true,true,true);
  CHECK(!memcmp(&q,&copy,sizeof q));empty_birth(s,0);clear(s);observed(s,79,phase(p,2));
  /* Returning current selection to P5 never promotes an excluded emission. */
  c=begin(s);rear_p1_create_end(s,c);CHECK(!current(s,0,p));observed(s,79,phase(p,2));
 }
 /* Same-source sprite aliases (+1000 and +6000) must fail even when gr and
  * raw agree, so this cannot pass accidentally via the gr==raw guard alone. */
 for(unsigned p=1;p<=2;p++)for(unsigned delta=1000;delta<=6000;delta+=5000) {
  rear_p1_reset(s);prime(s,0);uint64_t c=begin(s);RearP1Shot q=shot(p);q.gr+=delta;
  rear_p1_emit(s,7,c,1,0,10,1,258,1,p,q.gr,&q,true,true,true);empty_birth(s,0);clear(s);
  c=begin(s);emit(s,c,1,0,p);CHECK(!rear_p1_current(s,0,q.gr,q.gr,&q,true,true,true));
  CHECK(!current(s,0,p));
 }
}
static void original_identity_seal(RearP1State *s)
{
 /* All slot identities, both phases, and either metadata-only or full-seal
  * copies must fail at the different physical slot without damaging source. */
 for(unsigned p=1;p<=2;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)
 for(unsigned copy_seal=0;copy_seal<2;copy_seal++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,slot,p);rear_p1_create_end(s,c);
  unsigned target=(slot+1)%REAR_P1_SLOTS;s->birth[target]=s->birth[slot];
  if(copy_seal)s->birth_identity[target]=s->birth_identity[slot];
  CHECK(!current(s,target,p)&&!s->birth[target].qualified&&!s->birth_identity[target]);observed(s,slot,p);
 }
 for(unsigned p=1;p<=2;p++)for(unsigned bit=0;bit<64;bit++) {
  rear_p1_reset(s);prime(s,79);uint64_t c=begin(s);emit(s,c,1,0,p);
  RearP1Birth original=s->birth[0];uint64_t identity=s->birth_identity[0];
  s->birth_identity[0]^=UINT64_C(1)<<bit;RearP1Shot q=shot(p),copy=q;
  CHECK(!rear_p1_current(s,0,q.gr,q.gr,&q,true,true,true));
  CHECK(!memcmp(&q,&copy,sizeof q)&&!s->birth[0].qualified&&!s->birth_identity[0]);
  s->birth[0]=original;CHECK(!current(s,0,p)&&!s->birth_identity[0]);CHECK(old_current(s,79));
  c=begin(s);emit(s,c,1,0,p);CHECK(s->birth_identity[0]==identity);observed(s,0,p);
 }
 /* The retained seal and birth are independent of live caller power/mode.
  * A generation change, unlike a caller selection change, revokes the birth. */
 for(unsigned p=1;p<=2;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
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
 rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,1);emit(s,c,2,79,2);rear_p1_create_end(s,c);
 uint64_t identities[REAR_P1_SLOTS];memcpy(identities,s->birth_identity,sizeof identities);
 CHECK(!current(s,UINT_MAX,1));emit(s,0,1,80,1);clear(s);
 CHECK(!memcmp(identities,s->birth_identity,sizeof identities));observed(s,0,1);observed(s,79,2);
 rear_p1_reset(s);for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)empty_birth(s,slot);
}
static void coexistence(RearP1State *s)
{
 RearP1Shot births[34];unsigned records[34],modes[34],phases[34],count=0;
 rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,78,1);emit(s,c,2,79,2);rear_p1_create_end(s,c);
 /* Ten admitted tuples and all 34 phase observations, including 163/164
  * pass-through. Retain the complete originating record, mode and phase. */
 for(unsigned r=0;r<sizeof sources/sizeof *sources;r++)for(unsigned p=1;p<=sources[r].period;p++) {
  const Source *a=&sources[r];c=source_begin(s,a);source_emit(s,a,c,1,count,p);rear_p1_create_end(s,c);
  births[count]=source_shot(a,p);records[count]=a->record;modes[count]=a->mode+1;phases[count]=p;
  bool drawable=births[count].gr!=163&&births[count].gr!=164;
  CHECK(source_current(s,a,count,p)==drawable);
  if(drawable)CHECK(s->birth[count].record==a->record&&s->birth[count].mode==a->mode+1&&s->birth[count].phase==p);
  else empty_birth(s,count);
  count++;observed(s,78,1);observed(s,79,2);
 }
 CHECK(count==34);
 for(unsigned power=0;power<12;power++)for(unsigned mode=0;mode<3;mode++) {
  rear_p1_call_begin(s,9,10,1,power,mode,1,(mode?265:254)+power,true,true);rear_p1_call_end(s);
  observed(s,78,1);observed(s,79,2);
  for(unsigned k=0;k<count;k++) {
   bool drawable=births[k].gr!=163&&births[k].gr!=164;
   CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true)==drawable);
   if(drawable)CHECK(s->birth[k].record==records[k]&&s->birth[k].mode==modes[k]&&s->birth[k].phase==phases[k]);
  }
 }
 /* An old generic pass-through consumes two of P4's five allocations while
  * recycling a P5 drawable. The unrelated retained P5 birth stays owned. */
 c=source_begin(s,&sources[8]);source_emit(s,&sources[8],c,1,78,1);empty_birth(s,78);
 CHECK(s->lease&&s->remaining==4&&s->used_count==1);observed(s,79,2);
 source_emit(s,&sources[8],c,2,70,2);empty_birth(s,70);
 CHECK(s->lease&&s->remaining==3&&s->used_count==2);observed(s,79,2);rear_p1_create_end(s,c);
 /* A fresh P5 emission may recycle either generic slot with a complete new
  * birth, while all nine other source tuples keep their retained ownership. */
 c=begin(s);emit(s,c,1,78,1);emit(s,c,2,70,2);rear_p1_create_end(s,c);
 observed(s,78,1);observed(s,70,2);observed(s,79,2);
 for(unsigned k=0;k<count;k++)CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true)==(births[k].gr!=163&&births[k].gr!=164));
 rear_p1_reset(s);clear(s);CHECK(!current(s,78,1)&&!current(s,70,2)&&!current(s,79,2));
 for(unsigned k=0;k<count;k++)CHECK(!rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true));
}
int main(void)
{
 RearP1State state={0};cyclic_capacities(&state);rejected_allocations(&state);canonical_mismatches(&state);isolation(&state);
 admission(&state);one_way_revocation(&state);source_budgets(&state);every_slot_pair(&state);
 excluded_shared_sources(&state);original_identity_seal(&state);coexistence(&state);
 printf("Rear P5 mode1 ownership PASS: %u checks; two cyclic starts, prior0..2/new0..2 capacities, every80x80 slot pair, exact258 admission/budget2, append-only maps, P6/P9 shared-raw exclusions, one-way revocation, retained identity seals and all ten source tuples\n",checks);
 return 0;
}
