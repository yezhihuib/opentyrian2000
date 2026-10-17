/* SPDX-License-Identifier: GPL-2.0-or-later
 * Generated/synthetic observations only. No game records or original art.
 * P5 mode2 is an exact four-observation renderer-ownership grant. */
#include "rear_multi_p1.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); exit(1); } } while (0)
static const unsigned ids[]={277,278,183,182};
static const int dx[]={-9,9,6,-6},dy[]={-2,-2,6,6};
static unsigned phase(unsigned start,unsigned ordinal)
{return (start+ordinal-2)%4+1;}
static RearP1Shot shot(unsigned p)
{unsigned k=p-1;return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,dx[k],dy[k],0,0};}
static uint64_t begin(RearP1State *s)
{
 rear_p1_call_begin(s,7,10,1,4,1,1,269,true,true);
 CHECK(s->pending&&!s->lease&&s->budget==4&&s->record==269&&s->mode==2);
 uint64_t c=rear_p1_create_begin(s,7,10,1,269,1);
 CHECK(c&&s->lease&&!s->pending&&s->remaining==4&&s->next_ordinal==1&&!s->next_phase&&!s->used_count);
 return c;
}
static void emit(RearP1State *s,uint64_t c,unsigned n,unsigned slot,unsigned p)
{
 RearP1Shot q=shot(p),copy=q;
 rear_p1_emit(s,7,c,n,slot,10,1,269,1,p,ids[p-1],&q,true,true,true);
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
 CHECK(s->birth[slot].qualified&&s->birth[slot].record==269&&s->birth[slot].mode==2);
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
 unsigned seen[4][4]={{0}};
 /* The real phase may continue after any partial capacity, including zero.
  * Each new creator has a fresh ordinal and four-allocation budget. */
 for(unsigned start=1;start<=4;start++)for(unsigned prior=0;prior<=4;prior++)for(unsigned cap=0;cap<=4;cap++) {
  rear_p1_reset(s);
  for(unsigned n=1;n<=prior;n++)prime(s,20+n);
  for(unsigned n=1;n<=cap;n++)prime(s,10+n);
  uint64_t c=begin(s);
  for(unsigned n=1;n<=prior;n++) {emit(s,c,n,20+n,phase(start,n));observed(s,20+n,phase(start,n));}
  rear_p1_create_end(s,c);clear(s);
  unsigned next=phase(start,prior+1);c=begin(s);
  for(unsigned n=1;n<=cap;n++) {
   unsigned p=phase(next,n);emit(s,c,n,10+n,p);observed(s,10+n,p);
   CHECK(s->remaining==4-n&&s->used_count==n&&s->next_ordinal==n+1);
   CHECK(s->next_phase==phase(next,n+1)&&s->lease==(n<4)&&s->call==c);
   for(unsigned k=1;k<=n;k++)CHECK(s->used_slots[k-1]==10+k);
   seen[p-1][n-1]++;
  }
  rear_p1_create_end(s,c);clear(s);
  for(unsigned n=1;n<=cap;n++)observed(s,10+n,phase(next,n));
  for(unsigned n=1;n<=prior;n++)observed(s,20+n,phase(start,n));
  emit(s,c,cap+1,0,phase(next,cap+1));empty_birth(s,0);CHECK(!current(s,0,phase(next,cap+1)));clear(s);
 }
 for(unsigned p=0;p<4;p++)for(unsigned n=0;n<4;n++)CHECK(seen[p][n]>0);
 /* Fifth and later allocations do not inherit P4's five-shot budget. */
 for(unsigned start=1;start<=4;start++) {
  rear_p1_reset(s);for(unsigned n=5;n<=9;n++)prime(s,n);uint64_t c=begin(s);
  for(unsigned n=1;n<=4;n++)emit(s,c,n,n,phase(start,n));
  for(unsigned n=5;n<=9;n++) {
   emit(s,c,n,n,phase(start,n));empty_birth(s,n);CHECK(!current(s,n,phase(start,n)));clear(s);retained(s,start,4,0);
  }
 }
 /* Every earlier slot must be checked, not just the immediately previous one. */
 for(unsigned start=1;start<=4;start++)for(unsigned bad=2;bad<=5;bad++)for(unsigned reused=1;reused<bad;reused++) {
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
 for(unsigned start=1;start<=4;start++)for(unsigned bad=1;bad<=4;bad++)for(unsigned kind=0;kind<54;kind++) {
  rear_p1_reset(s);prime(s,79);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  unsigned p=phase(start,bad),slot=kind==0?80:kind==1?81:kind==2?UINT_MAX:bad;
  unsigned raw=kind==3?0:kind==4?ids[p-1]+1000:kind==5?ids[p%4]:kind==39?UINT_MAX:kind==43?163:kind==44?164:ids[p-1];
  RearP1Shot q=shot(p);if(kind>=26&&kind<39)mutate(&q,kind-26);RearP1Shot copy=q;
  rear_p1_emit(s,kind==6?8:kind==7?UINT64_MAX:kind==45?0:7,kind==8?c+1:kind==9?0:c,
   kind==10?0:kind==11?bad+1:kind==12?UINT_MAX:bad,slot,
   kind==13?37:kind==46?0:kind==47?UINT_MAX:10,
   kind==14?0:kind==41?UINT_MAX:kind==48?2:1,
   kind==15?258:kind==16?267:kind==42?268:kind==49?0:kind==50?UINT_MAX:269,
   kind==17?2:kind==40?0:kind==51?UINT_MAX:1,
   kind==18?0:kind==19?5:kind==20?UINT_MAX:kind==21?p%4+1:kind==52?p+4:p,raw,
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
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)for(unsigned p=1;p<=4;p++) {
  rear_p1_reset(s);prime(s,slot);uint64_t c=begin(s);emit(s,c,1,slot,p);observed(s,slot,p);
  CHECK(s->lease&&s->remaining==3&&s->used_count==1&&s->used_slots[0]==slot);
  rear_p1_create_end(s,c);observed(s,slot,p);
  c=rear_p1_create_begin(s,7,10,1,269,1);emit(s,c,1,slot,p);empty_birth(s,slot);CHECK(!current(s,slot,p));clear(s);
 }
 const unsigned outside[]={80,81,UINT_MAX};
 for(unsigned k=0;k<sizeof outside/sizeof *outside;k++) {
  rear_p1_reset(s);prime(s,79);uint64_t c=begin(s);for(unsigned n=1;n<=4;n++)emit(s,c,n,n,n);
  RearP1Birth copy[REAR_P1_SLOTS];memcpy(copy,s->birth,sizeof copy);
  CHECK(!current(s,outside[k],1));CHECK(!memcmp(copy,s->birth,sizeof copy));
  emit(s,c,5,outside[k],1);clear(s);CHECK(!memcmp(copy,s->birth,sizeof copy));retained(s,1,4,0);CHECK(old_current(s,79));
 }
}
static void canonical_mismatches(RearP1State *s)
{
 /* Keep raw and live-shot identity internally valid so phase/order checks are
  * independently necessary, rather than hidden by a second malformed field. */
 const unsigned rawids[]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278};
 const int vx[]={-10,10,-9,9,9,-9,-10,10,0,-6,6,-6,6,-9,9};
 const int vy[]={0,0,-2,-2,2,2,0,0,10,6,6,-6,-6,-2,-2};
 for(unsigned start=1;start<=4;start++)for(unsigned bad=1;bad<=4;bad++)for(unsigned k=0;k<sizeof rawids/sizeof *rawids;k++) {
  unsigned p=phase(start,bad);if(rawids[k]==ids[p-1])continue;
  rear_p1_reset(s);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  RearP1Shot q={rawids[k],0,1,1,255,0,0,0,208,vx[k],vy[k],0,0},copy=q;
  rear_p1_emit(s,7,c,bad,bad,10,1,269,1,p,rawids[k],&q,true,true,true);
  CHECK(!memcmp(&q,&copy,sizeof q));empty_birth(s,bad);clear(s);retained(s,start,bad-1,0);
  emit(s,c,bad+1,bad+1,phase(start,bad+1));CHECK(!current(s,bad+1,phase(start,bad+1)));
 }
 /* A canonical but reordered phase must cancel, even with its own correct
  * raw ID and shot fields. The first phase remains free to start anywhere. */
 for(unsigned start=1;start<=4;start++)for(unsigned bad=2;bad<=4;bad++)for(unsigned p=1;p<=4;p++) {
  if(p==phase(start,bad))continue;
  rear_p1_reset(s);prime(s,bad);uint64_t c=begin(s);
  for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,bad,p);empty_birth(s,bad);clear(s);retained(s,start,bad-1,0);
  emit(s,c,bad+1,bad+1,phase(start,bad+1));CHECK(!current(s,bad+1,phase(start,bad+1)));
 }
 /* Slot zero is a valid used slot, not a sentinel that can bypass uniqueness. */
 for(unsigned start=1;start<=4;start++)for(unsigned bad=2;bad<=5;bad++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,start);
  for(unsigned n=2;n<bad;n++)emit(s,c,n,n,phase(start,n));
  emit(s,c,bad,0,phase(start,bad));empty_birth(s,0);clear(s);
  for(unsigned n=2;n<bad;n++)observed(s,n,phase(start,n));
 }
}
static void isolation(RearP1State *s)
{
 for(unsigned start=1;start<=4;start++)for(unsigned after=0;after<=4;after++)for(unsigned kind=0;kind<15;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=after;n++)emit(s,c,n,n,phase(start,n));
  uint64_t inner=0;
  if(kind==0)inner=rear_p1_create_begin(s,7,10,1,269,1);
  if(kind==1)rear_p1_create_end(s,c);
  if(kind==2)rear_p1_call_end(s);
  if(kind==3)rear_p1_reset(s);
  if(kind>=4) {
   rear_p1_call_begin(s,7,10,1,4,1,1,269,true,true);
   inner=rear_p1_create_begin(s,kind==4?8:kind==10?0:kind==11?UINT64_MAX:7,
    kind==5?37:kind==12?UINT_MAX:10,kind==6?0:kind==13?UINT_MAX:1,
    kind==7?258:kind==9?268:kind==14?UINT_MAX:269,kind==8?2:1);
  }
  if(inner) {CHECK(inner!=c);emit(s,inner,1,10,start);CHECK(!current(s,10,start));rear_p1_create_end(s,inner);}
  emit(s,c,after+1,11,phase(start,after+1));CHECK(!current(s,11,phase(start,after+1)));clear(s);
  for(unsigned n=1;n<=after;n++)CHECK(current(s,n,phase(start,n))==(kind!=3));
 }
 /* Pending without a real creator, zero capacity, stale ends and stale emits. */
 rear_p1_reset(s);prime(s,0);rear_p1_call_begin(s,7,10,1,4,1,1,269,true,true);
 emit(s,0,1,0,1);empty_birth(s,0);CHECK(!current(s,0,1));clear(s);
 rear_p1_reset(s);uint64_t c=begin(s);rear_p1_create_end(s,c);clear(s);
 uint64_t inner=rear_p1_create_begin(s,7,10,1,269,1);CHECK(inner!=c&&!s->lease);
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
 emit(s,c,1,1,3);CHECK(!current(s,1,3));clear(s);
}
static bool admitted(unsigned power,unsigned mode,unsigned record)
{
 return (power<2&&mode<2&&record==(mode?265:254)+power)||
  (power==2&&mode<2&&record==(mode?267:256))||(power==3&&mode<2&&record==(mode?268:257))||
  (power==4&&mode<2&&record==(mode?269:258))||(power==5&&mode<2&&record==(mode?270:259))||(power==6&&mode<2&&record==(mode?271:260))||(power==7&&mode==0&&record==261);
}
static unsigned budget(unsigned power,unsigned mode)
{return power==7?6:power==6?(mode?5:4):power==5?(mode?5:3):power==4?(mode?4:2):power==3?5:power==2?(mode?4:2):power+1;}
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
  rear_p1_call_begin(s,7,ports[p],bays[b],4,1,players[u],269,scope!=0,table!=0);CHECK(s->pending==yes);
  rear_p1_call_end(s);clear(s);
 }
 CHECK(REAR_P1_HEADS==19&&REAR_P1_OBSERVED==21&&REAR_P1_MAX_BUDGET==6);
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
 for(unsigned p=1;p<=4;p++)for(unsigned field=0;field<13;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
  RearP1Shot q=shot(p);mutate(&q,field);RearP1Shot copy=q;
  CHECK(!rear_p1_current(s,79,ids[p-1],ids[p-1],&q,true,true,true));
  CHECK(!memcmp(&q,&copy,sizeof q));CHECK(!s->birth[79].qualified&&!current(s,79,p));
  rear_p1_create_end(s,c);c=begin(s);emit(s,c,1,79,p);CHECK(current(s,79,p));
 }
 const unsigned aliases[]={0,1,2,39,40,77,163,164,182,183,277,278,281,282,300,301,1182,1183,1277,1278,6277,UINT_MAX};
 for(unsigned p=1;p<=4;p++)for(unsigned a=0;a<sizeof aliases/sizeof *aliases;a++)for(unsigned field=0;field<3;field++)if(aliases[a]!=ids[p-1]) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  unsigned index=field==0||field==2?aliases[a]:ids[p-1],raw=field==1||field==2?aliases[a]:ids[p-1];
  CHECK(!rear_p1_current(s,0,index,raw,&q,true,true,true));CHECK(!current(s,0,p));
 }
 for(unsigned p=1;p<=4;p++)for(unsigned kind=0;kind<4;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Shot q=shot(p);
  CHECK(!rear_p1_current(s,0,ids[p-1],ids[p-1],kind==3?NULL:&q,kind!=0,kind!=1,kind!=2));CHECK(!current(s,0,p));
 }
 for(unsigned p=1;p<=4;p++)for(unsigned field=0;field<15;field++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Birth before=s->birth[0];
  switch(field) {
  case 0:s->birth[0].generation++;break;case 1:s->birth[0].record=257;break;
  case 2:s->birth[0].phase=0;break;case 3:s->birth[0].phase=5;break;
  case 4:s->birth[0].raw++;break;case 5:s->birth[0].mode=1;break;
  case 6:s->birth[0].mode=0;break;case 7:s->birth[0].phase=p%4+1;break;
  case 8:s->birth[0].qualified=false;break;case 9:s->birth[0].record=258;break;
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
static void shared_birth(RearP1State *s,unsigned record,unsigned slot,unsigned p)
{
 RearP1Shot q=shot(p);
 rear_p1_call_begin(s,7,10,1,record-265,1,1,record,true,true);
 uint64_t c=rear_p1_create_begin(s,7,10,1,record,1);
 rear_p1_emit(s,7,c,1,slot,10,1,record,1,p,q.gr,&q,true,true,true);
 rear_p1_create_end(s,c);CHECK(current(s,slot,p));
 CHECK(s->birth[slot].record==record&&s->birth_identity[slot]);
}
static void original_identity_seal(RearP1State *s)
{
 /* Regression: records268/269 share canonical phases3/4. Validating only the
  * mutable birth tuple admitted an in-flight 268<->269 record substitution. */
 for(unsigned record=268;record<=269;record++)for(unsigned p=3;p<=4;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++) {
  rear_p1_reset(s);shared_birth(s,record,slot,p);
  RearP1Birth original=s->birth[slot];uint64_t identity=s->birth_identity[slot];
  s->birth[slot].record=record==268?269:268;
  CHECK(!current(s,slot,p)&&!s->birth[slot].qualified&&!s->birth_identity[slot]);
  /* Reverting metadata after detected corruption cannot resurrect ownership. */
  s->birth[slot]=original;CHECK(!current(s,slot,p)&&!s->birth_identity[slot]);
  shared_birth(s,record,slot,p);CHECK(s->birth_identity[slot]==identity);
  rear_p1_call_begin(s,9,10,1,4,0,1,258,true,true);rear_p1_call_end(s);
  CHECK(current(s,slot,p)&&s->birth_identity[slot]==identity);
 }
 /* Copying metadata alone or copying metadata plus its seal to a new physical
  * slot fails. The untouched source stays owned; the seal binds slot identity. */
 for(unsigned record=268;record<=269;record++)for(unsigned p=3;p<=4;p++)for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)for(unsigned copy_seal=0;copy_seal<2;copy_seal++) {
  unsigned target=(slot+1)%REAR_P1_SLOTS;
  rear_p1_reset(s);shared_birth(s,record,slot,p);
  s->birth[target]=s->birth[slot];
  if(copy_seal)s->birth_identity[target]=s->birth_identity[slot];
  CHECK(!current(s,target,p)&&!s->birth[target].qualified&&!s->birth_identity[target]);
  CHECK(current(s,slot,p));
 }
 /* Any single-bit seal corruption is detected without changing the gameplay
  * shot or the untouched birth in the other power's slot. */
 for(unsigned record=268;record<=269;record++)for(unsigned p=3;p<=4;p++)for(unsigned bit=0;bit<64;bit++) {
  rear_p1_reset(s);shared_birth(s,record,0,p);shared_birth(s,record==268?269:268,79,p);
  s->birth_identity[0]^=UINT64_C(1)<<bit;
  RearP1Shot q=shot(p),copy=q;
  CHECK(!rear_p1_current(s,0,q.gr,q.gr,&q,true,true,true));
  CHECK(!memcmp(&q,&copy,sizeof q)&&!s->birth[0].qualified&&!s->birth_identity[0]);
  CHECK(current(s,79,p));
 }
 /* Out-of-range observations cannot touch an in-bounds identity seal. */
 rear_p1_reset(s);shared_birth(s,268,0,3);shared_birth(s,269,79,4);
 uint64_t identities[REAR_P1_SLOTS];memcpy(identities,s->birth_identity,sizeof identities);
 CHECK(!current(s,UINT_MAX,3));emit(s,0,1,80,1);clear(s);
 CHECK(!memcmp(identities,s->birth_identity,sizeof identities));CHECK(current(s,0,3)&&current(s,79,4));
 rear_p1_reset(s);
 for(unsigned slot=0;slot<REAR_P1_SLOTS;slot++)empty_birth(s,slot);
}
static void coexistence(RearP1State *s)
{
 const unsigned oldids[]={39,1,281,282,301,300,40,2,77,163,164,183,182};
 const int ox[]={-10,10,-9,9,9,-9,-10,10,0,-6,6,6,-6},oy[]={0,0,-2,-2,2,2,0,0,10,-6,-6,6,6};
 const unsigned records[]={254,255,256,265,266,267,257,268};
 RearP1Shot births[28];unsigned count=0;
 rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=4;n++)emit(s,c,n,70+n,n);rear_p1_create_end(s,c);
 /* All eight old tuples and all their phases, including nondrawable 163/164. */
 for(unsigned r=0;r<sizeof records/sizeof *records;r++) {
  unsigned record=records[r],mode=record>=265,power=record-(mode?265:254),period=record==257||record==268?5:mode?4:2;
  for(unsigned p=1;p<=period;p++) {
   unsigned k=record==256?p+5:record==257?(p==5?8:p+1):record==268?(p==5?8:p+8):mode?p+1:p-1;
   RearP1Shot q={oldids[k],0,1,1,255,0,0,0,208,ox[k],oy[k],0,0};
   rear_p1_call_begin(s,8,10,1,power,mode,1,record,true,true);c=rear_p1_create_begin(s,8,10,1,record,1);
   rear_p1_emit(s,8,c,1,count,10,1,record,1,p,oldids[k],&q,true,true,true);
   CHECK(rear_p1_current(s,count,oldids[k],oldids[k],&q,true,true,true)==(k!=9&&k!=10));births[count++]=q;
   rear_p1_create_end(s,c);for(unsigned n=1;n<=4;n++)observed(s,70+n,n);
  }
 }
 CHECK(count==28);
 for(unsigned power=0;power<12;power++)for(unsigned mode=0;mode<3;mode++) {
  rear_p1_call_begin(s,9,10,1,power,mode,1,(mode?265:254)+power,true,true);rear_p1_call_end(s);
  for(unsigned n=1;n<=4;n++)observed(s,70+n,n);
  for(unsigned k=0;k<count;k++)CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true)==(k!=23&&k!=24));
 }
 CHECK(s->birth[22].record==257&&s->birth[22].mode==1&&s->birth[22].raw==77);
 CHECK(s->birth[27].record==268&&s->birth[27].mode==2&&s->birth[27].raw==77);
 CHECK(s->birth[25].record==268&&s->birth[25].phase==3&&s->birth[25].raw==183);
 CHECK(s->birth[73].record==269&&s->birth[73].phase==3&&s->birth[73].raw==183);
 /* An old pass-through recycles a new drawable slot without erasing another. */
 rear_p1_call_begin(s,8,10,1,3,1,1,268,true,true);c=rear_p1_create_begin(s,8,10,1,268,1);
 RearP1Shot q={163,0,1,1,255,0,0,0,208,-6,-6,0,0};
 rear_p1_emit(s,8,c,1,71,10,1,268,1,1,163,&q,true,true,true);empty_birth(s,71);
 CHECK(s->lease&&s->remaining==4&&s->used_count==1);for(unsigned n=2;n<=4;n++)observed(s,70+n,n);
 rear_p1_create_end(s,c);
 /* P5 can recycle old drawable and pass-through slots with its own birth tuple. */
 c=begin(s);emit(s,c,1,22,1);emit(s,c,2,23,2);emit(s,c,3,25,3);emit(s,c,4,26,4);rear_p1_create_end(s,c);
 observed(s,22,1);observed(s,23,2);observed(s,25,3);observed(s,26,4);
 CHECK(old_current(s,27));
 for(unsigned k=0;k<22;k++)CHECK(rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true));
 rear_p1_reset(s);clear(s);
 for(unsigned n=1;n<=4;n++)CHECK(!current(s,70+n,n));
 for(unsigned k=0;k<count;k++)CHECK(!rear_p1_current(s,k,births[k].gr,births[k].gr,&births[k],true,true,true));
}
int main(void)
{
 RearP1State state={0};cyclic_capacities(&state);rejected_allocations(&state);canonical_mismatches(&state);isolation(&state);
 admission(&state);one_way_revocation(&state);original_identity_seal(&state);coexistence(&state);
 printf("Rear P5 mode2 ownership PASS: %u checks; four cyclic starts, prior0..4/new0..4 capacities, all-prior reuse, exact269 admission, append-only role maps, fail-closed invalidities, original identity seals and mixed birth-owned modes\n",checks);
 return 0;
}
