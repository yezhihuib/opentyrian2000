/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic observations only; exact P9 mode1 record262 ownership. */
#include "rear_multi_p1.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);exit(1);}} while(0)
static const unsigned ids[]={277,278,297,296,41,3};
static const int vx[]={-9,9,9,-9,-10,10},vy[]={-2,-2,2,2,0,0};
static unsigned phase(unsigned start,unsigned n){return (start+n-2)%6+1;}
static RearP1Shot shot(unsigned p){return (RearP1Shot){ids[p-1],0,1,1,255,0,0,0,208,vx[p-1],vy[p-1],0,0};}
static uint64_t begin(RearP1State *s)
{
 rear_p1_call_begin(s,7,10,1,8,0,1,262,true,true);
 CHECK(s->pending&&!s->lease&&s->budget==6&&s->mode==1&&s->record==262);
 uint64_t c=rear_p1_create_begin(s,7,10,1,262,1);
 CHECK(c&&s->lease&&!s->pending&&s->remaining==6&&s->next_ordinal==1&&!s->next_phase&&!s->used_count);return c;
}
static void emit(RearP1State *s,uint64_t c,unsigned n,unsigned slot,unsigned p)
{RearP1Shot q=shot(p),save=q;rear_p1_emit(s,7,c,n,slot,10,1,262,1,p,q.gr,&q,true,true,true);CHECK(!memcmp(&q,&save,sizeof q));}
static bool current(RearP1State *s,unsigned slot,unsigned p)
{RearP1Shot q=shot(p);return rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true);}
static void observed(RearP1State *s,unsigned slot,unsigned p)
{CHECK(current(s,slot,p));CHECK(s->birth[slot].record==262&&s->birth[slot].mode==1&&s->birth[slot].phase==p&&s->birth_identity[slot]);}
static void clear(const RearP1State *s)
{CHECK(!s->pending&&!s->lease&&!s->call&&!s->budget&&!s->remaining&&!s->next_ordinal&&!s->next_phase&&!s->used_count);for(unsigned i=0;i<6;i++)CHECK(!s->used_slots[i]);}
static void empty(const RearP1State *s,unsigned slot)
{RearP1Birth b={0};CHECK(!memcmp(&b,&s->birth[slot],sizeof b)&&!s->birth_identity[slot]);}
static void mutate(RearP1Shot *q,unsigned f)
{switch(f){case 0:q->gr++;break;case 1:q->ani++;break;case 2:q->ani_max++;break;case 3:q->player++;break;case 4:q->trail--;break;case 5:q->aim++;break;case 6:q->chain++;break;case 7:q->complicated++;break;case 8:q->filter++;break;case 9:q->xm++;break;case 10:q->ym++;break;case 11:q->xc++;break;case 12:q->yc++;break;}}
typedef struct {unsigned record,power,mode,budget,period,raw[7];int dx[7],dy[7];} Route;
static const Route routes[]={
 {254,0,0,1,2,{39,1},{-10,10},{0,0}},{265,0,1,1,4,{281,282,301,300},{-9,9,9,-9},{-2,-2,2,2}},
 {255,1,0,2,2,{39,1},{-10,10},{0,0}},{266,1,1,2,4,{281,282,301,300},{-9,9,9,-9},{-2,-2,2,2}},
 {256,2,0,2,2,{40,2},{-10,10},{0,0}},{267,2,1,4,4,{281,282,301,300},{-9,9,9,-9},{-2,-2,2,2}},
 {257,3,0,5,5,{281,282,301,300,77},{-9,9,9,-9,0},{-2,-2,2,2,10}},
 {268,3,1,5,5,{163,164,183,182,77},{-6,6,6,-6,0},{-6,-6,6,6,10}},
 {258,4,0,2,2,{41,3},{-10,10},{0,0}},{269,4,1,4,4,{277,278,183,182},{-9,9,6,-6},{-2,-2,6,6}},
 {259,5,0,3,3,{41,3,77},{-10,10,0},{0,0,10}},{270,5,1,5,5,{277,278,183,182,77},{-9,9,6,-6,0},{-2,-2,6,6,10}},
 {260,6,0,4,4,{277,278,297,296},{-9,9,9,-9},{-2,-2,2,2}},
 {271,6,1,5,5,{277,278,295,294,77},{-9,9,6,-6,0},{-2,-2,6,6,10}},
 {261,7,0,6,6,{277,278,297,296,39,1},{-9,9,9,-9,-10,10},{-2,-2,2,2,0,0}},
 {272,7,1,7,7,{277,278,295,294,77,39,1},{-9,9,6,-6,0,-10,10},{-2,-2,6,6,10,0,0}},
 {262,8,0,6,6,{277,278,297,296,41,3},{-9,9,9,-9,-10,10},{-2,-2,2,2,0,0}},
 {273,8,1,7,7,{277,278,295,294,77,298,299},{-9,9,6,-6,0,-2,2},{-2,-2,6,6,10,9,9}}
};
static unsigned route_budget(unsigned power,unsigned mode,unsigned record)
{for(unsigned i=0;i<sizeof routes/sizeof *routes;i++)if(routes[i].power==power&&routes[i].mode==mode&&routes[i].record==record)return routes[i].budget;return 0;}
static void admission(RearP1State *s)
{
 const unsigned powers[]={0,1,2,3,4,5,6,7,8,9,10,11,UINT_MAX},modes[]={0,1,2,3,UINT_MAX};
 for(unsigned p=0;p<sizeof powers/sizeof *powers;p++)for(unsigned m=0;m<sizeof modes/sizeof *modes;m++)for(unsigned r=0;r<=1819;r++) {
  unsigned b=route_budget(powers[p],modes[m],r);rear_p1_call_begin(s,7,10,1,powers[p],modes[m],1,r,true,true);
  CHECK(s->pending==(b!=0)&&s->budget==b);uint64_t c=rear_p1_create_begin(s,7,10,1,r,1);CHECK(s->lease==(b!=0)&&s->remaining==b);rear_p1_create_end(s,c);clear(s);
 }
 const unsigned ports[]={0,10,19,22,27,32,36,37,38,UINT_MAX},bays[]={0,1,2,UINT_MAX},players[]={0,1,2,UINT_MAX};
 for(unsigned p=0;p<sizeof ports/sizeof *ports;p++)for(unsigned b=0;b<4;b++)for(unsigned u=0;u<4;u++)for(unsigned sc=0;sc<2;sc++)for(unsigned t=0;t<2;t++) {
  bool yes=ports[p]==10&&bays[b]==1&&players[u]==1&&sc&&t;rear_p1_call_begin(s,7,ports[p],bays[b],8,0,players[u],262,sc!=0,t!=0);CHECK(s->pending==yes);rear_p1_call_end(s);clear(s);
 }
 const unsigned members[]={39,1,281,282,301,300,40,2,77,182,183,277,278,41,3,296,297,294,295,298,299};
 const unsigned observed[]={39,1,281,282,301,300,40,2,77,182,183,163,164,277,278,41,3,296,297,294,295,298,299};
 CHECK(REAR_P1_HEADS==21&&REAR_P1_OBSERVED==23&&REAR_P1_MAX_BUDGET==7&&REAR_P1_SLOTS==80);
 for(unsigned raw=0;raw<8000;raw++){int m=-1,o=-1;for(unsigned i=0;i<21;i++)if(members[i]==raw)m=(int)i;for(unsigned i=0;i<23;i++)if(observed[i]==raw)o=(int)i;CHECK(rear_p1_member(raw)==m&&rear_p1_observed(raw)==o);}
 CHECK(rear_p1_member(UINT_MAX)<0&&rear_p1_observed(UINT_MAX)<0&&rear_p1_member(298)==19&&rear_p1_member(299)==20&&rear_p1_observed(298)==21&&rear_p1_observed(299)==22);
}
static void capacities(RearP1State *s)
{
 unsigned cases=0,seen[6][6]={{0}};
 for(unsigned start=1;start<=6;start++)for(unsigned prior=0;prior<=6;prior++)for(unsigned cap=0;cap<=6;cap++) {
  cases++;rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=prior;n++)emit(s,c,n,40+n,phase(start,n));rear_p1_create_end(s,c);clear(s);
  unsigned next=phase(start,prior+1);c=begin(s);
  for(unsigned n=1;n<=cap;n++){unsigned p=phase(next,n);emit(s,c,n,10+n,p);observed(s,10+n,p);CHECK(s->remaining==6-n&&s->used_count==n&&s->next_ordinal==n+1&&s->next_phase==p%6+1&&s->lease==(n<6));seen[p-1][n-1]++;}
  rear_p1_create_end(s,c);clear(s);for(unsigned n=1;n<=prior;n++)observed(s,40+n,phase(start,n));for(unsigned n=1;n<=cap;n++)observed(s,10+n,phase(next,n));
  emit(s,c,cap+1,0,phase(next,cap+1));empty(s,0);clear(s);
 }
 CHECK(cases==294);for(unsigned p=0;p<6;p++)for(unsigned n=0;n<6;n++)CHECK(seen[p][n]);
 for(unsigned base=0;base<80;base++)for(unsigned start=1;start<=6;start++)for(unsigned bad=2;bad<=7;bad++)for(unsigned dup=1;dup<bad;dup++) {
  rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<bad;n++)emit(s,c,n,(base+n-1)%80,phase(start,n));
  emit(s,c,bad,(base+dup-1)%80,phase(start,bad));empty(s,(base+dup-1)%80);clear(s);for(unsigned n=1;n<bad;n++)if(n!=dup)observed(s,(base+n-1)%80,phase(start,n));
 }
 for(unsigned a=0;a<80;a++)for(unsigned b=0;b<80;b++)for(unsigned start=1;start<=6;start++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,a,start);emit(s,c,2,b,phase(start,2));
  if(a==b){empty(s,a);clear(s);}else{observed(s,a,start);observed(s,b,phase(start,2));emit(s,c,3,a,phase(start,3));empty(s,a);observed(s,b,phase(start,2));clear(s);}
 }
 for(unsigned start=1;start<=6;start++){rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=6;n++)emit(s,c,n,n,phase(start,n));for(unsigned n=7;n<=11;n++){emit(s,c,n,n,phase(start,n));empty(s,n);clear(s);for(unsigned k=1;k<=6;k++)observed(s,k,phase(start,k));}}
}
static void rejection(RearP1State *s)
{
 for(unsigned start=1;start<=6;start++)for(unsigned bad=1;bad<=7;bad++)for(unsigned kind=0;kind<59;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,79,1);rear_p1_create_end(s,c);c=begin(s);for(unsigned n=1;n<bad;n++)emit(s,c,n,n,phase(start,n));
  unsigned p=phase(start,bad),slot=bad,raw=ids[p-1],ordinal=bad,port=10,bay=1,record=262,player=1,ph=p;uint64_t call=c,tick=7;bool sc=true,tab=true,src=true,nonnull=true;RearP1Shot q=shot(p);
  if(kind<13)mutate(&q,kind);else switch(kind){
   case 13:slot=80;break;case 14:slot=UINT_MAX;break;case 15:raw=0;break;case 16:raw+=1000;break;case 17:raw+=6000;break;case 18:ph=0;break;case 19:ph=7;break;case 20:ph=UINT_MAX;break;
   case 21:ph=p%6+1;break;case 22:ordinal=0;break;case 23:ordinal=bad+1;break;case 24:ordinal=UINT_MAX;break;case 25:call=0;break;case 26:call++;break;case 27:tick++;break;case 28:port=22;break;case 29:port=38;break;
   case 30:bay=0;break;case 31:player=2;break;case 32:record=1262;break;case 33:record=260;break;case 34:record=451;break;case 35:sc=false;break;case 36:tab=false;break;case 37:src=false;break;case 38:nonnull=false;break;
   case 39:raw=UINT_MAX;break;case 40:record=269;break;case 41:record=270;break;case 42:slot=81;break;case 43:bay=UINT_MAX;break;case 44:port=UINT_MAX;break;case 45:player=UINT_MAX;break;case 46:record=UINT_MAX;break;case 47:record=0;break;case 48:raw=ids[p%6];break;
   case 49:record=272;break;case 50:record=273;break;case 51:record=274;break;case 52:record=275;break;case 53:record=1272;break;case 54:record=1273;break;case 55:record=1274;break;case 56:record=1275;break;case 57:raw=182;break;case 58:raw=183;break;
  }
  RearP1Shot save=q;rear_p1_emit(s,tick,call,ordinal,slot,port,bay,record,player,ph,raw,nonnull?&q:NULL,sc,tab,src);CHECK(!memcmp(&save,&q,sizeof q));clear(s);if(slot<80)empty(s,slot);observed(s,79,1);
  for(unsigned n=1;n<bad;n++)observed(s,n,phase(start,n));
  for(unsigned n=bad+1;n<=6;n++){emit(s,c,n,n,phase(start,n));empty(s,n);}
 }
 for(unsigned p=1;p<=6;p++)for(unsigned raw=0;raw<8000;raw++)if(raw!=ids[p-1]){rear_p1_reset(s);uint64_t c=begin(s);RearP1Shot q=shot(p);q.gr=raw;rear_p1_emit(s,7,c,1,0,10,1,262,1,p,raw,&q,true,true,true);empty(s,0);clear(s);}
}
static void leases(RearP1State *s)
{
 for(unsigned start=1;start<=6;start++)for(unsigned after=0;after<=6;after++)for(unsigned kind=0;kind<9;kind++) {
  rear_p1_reset(s);uint64_t c=begin(s);for(unsigned n=1;n<=after;n++)emit(s,c,n,n,phase(start,n));uint64_t inner=0;
  switch(kind){case 0:rear_p1_call_end(s);break;case 1:rear_p1_create_end(s,c);break;case 2:rear_p1_reset(s);break;
   case 3:inner=rear_p1_create_begin(s,7,10,1,262,1);break;case 4:inner=rear_p1_create_begin(s,7,22,1,262,1);break;case 5:inner=rear_p1_create_begin(s,7,10,1,1262,1);break;
   case 6:rear_p1_call_begin(s,7,10,1,6,0,1,260,true,true);break;case 7:rear_p1_call_begin(s,8,10,1,8,0,1,262,true,true);inner=rear_p1_create_begin(s,7,10,1,262,1);break;case 8:rear_p1_call_begin(s,7,10,1,8,0,1,262,true,true);inner=rear_p1_create_begin(s,7,10,1,262,1);break;}
  if(inner){CHECK(inner!=c);rear_p1_create_end(s,inner);}emit(s,c,after+1,20,phase(start,after+1));empty(s,20);clear(s);for(unsigned n=1;n<=after;n++)CHECK(current(s,n,phase(start,n))==(kind!=2));
 }
 rear_p1_reset(s);rear_p1_call_begin(s,7,10,1,8,0,1,262,true,true);emit(s,0,1,0,1);empty(s,0);clear(s);
 uint64_t c=begin(s);rear_p1_create_end(s,c);uint64_t newer=begin(s);rear_p1_create_end(s,c);CHECK(s->call==newer&&s->lease);emit(s,newer,1,0,1);observed(s,0,1);emit(s,c,2,1,2);empty(s,1);clear(s);observed(s,0,1);
 rear_p1_reset(s);s->call_serial=UINT64_MAX;c=begin(s);CHECK(c==1);emit(s,c,1,0,1);s->generation=UINT64_MAX;rear_p1_reset(s);CHECK(s->generation==1);empty(s,0);
}
static void integrity(RearP1State *s)
{
 for(unsigned p=1;p<=6;p++)for(unsigned f=0;f<24;f++) {
  rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);RearP1Birth save=s->birth[0];RearP1Shot q=shot(p),copy=q;unsigned index=q.gr,raw=q.gr;bool sc=true,tab=true,src=true;
  if(f<13)mutate(&q,f);else switch(f){case 13:s->birth[0].record=269;break;case 14:s->birth[0].record=270;break;case 15:s->birth[0].record=1262;break;case 16:s->birth[0].mode=2;break;case 17:s->birth[0].phase=p%6+1;break;case 18:s->birth[0].generation++;break;case 19:index+=1000;break;case 20:raw+=6000;break;case 21:sc=false;break;case 22:tab=false;break;case 23:src=false;break;}
  CHECK(!rear_p1_current(s,0,index,raw,&q,sc,tab,src));CHECK(!s->birth[0].qualified&&!s->birth_identity[0]);s->birth[0]=save;CHECK(!current(s,0,p));q=copy;(void)q;
 }
 for(unsigned p=1;p<=6;p++)for(unsigned bit=0;bit<64;bit++){rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,0,p);s->birth_identity[0]^=UINT64_C(1)<<bit;CHECK(!current(s,0,p));CHECK(!s->birth_identity[0]);}
 for(unsigned p=1;p<=6;p++)for(unsigned a=0;a<80;a++)for(unsigned b=0;b<80;b++)if(a!=b){rear_p1_reset(s);uint64_t c=begin(s);emit(s,c,1,a,p);s->birth[b]=s->birth[a];s->birth_identity[b]=s->birth_identity[a];CHECK(!current(s,b,p));observed(s,a,p);}
}
/* Matching raw277/278/297/296/41/3 and every other live field do not allow a birth
 * to change its original record, mode, canonical phase or physical slot. */
static void shared_seals(RearP1State *s)
{
 for(unsigned a=0;a<sizeof routes/sizeof *routes;a++)for(unsigned b=0;b<sizeof routes/sizeof *routes;b++)
 if(a!=b&&(routes[a].record==262||routes[b].record==262))
 for(unsigned pa=1;pa<=routes[a].period;pa++)for(unsigned pb=1;pb<=routes[b].period;pb++)
 if(routes[a].raw[pa-1]==routes[b].raw[pb-1])for(unsigned slot=0;slot<80;slot++) {
  const Route *r=&routes[a],*other=&routes[b];RearP1Shot q={r->raw[pa-1],0,1,1,255,0,0,0,208,r->dx[pa-1],r->dy[pa-1],0,0};
  rear_p1_reset(s);rear_p1_call_begin(s,7,10,1,r->power,r->mode,1,r->record,true,true);
  uint64_t c=rear_p1_create_begin(s,7,10,1,r->record,1);rear_p1_emit(s,7,c,1,slot,10,1,r->record,1,pa,q.gr,&q,true,true,true);rear_p1_create_end(s,c);
  CHECK(rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true));RearP1Birth saved=s->birth[slot];
  s->birth[slot].record=other->record;s->birth[slot].mode=other->mode+1;s->birth[slot].phase=pb;
  CHECK(!rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true)&&!s->birth_identity[slot]);
  s->birth[slot]=saved;CHECK(!rear_p1_current(s,slot,q.gr,q.gr,&q,true,true,true));
 }
}
static void coexistence(RearP1State *s)
{
 RearP1Shot shots[80];unsigned records[80],modes[80],phases[80],count=0;rear_p1_reset(s);
 for(unsigned i=0;i<sizeof routes/sizeof *routes;i++)for(unsigned p=1;p<=routes[i].period;p++) {
  const Route *r=&routes[i];RearP1Shot q={r->raw[p-1],0,1,1,255,0,0,0,208,r->dx[p-1],r->dy[p-1],0,0};
  rear_p1_call_begin(s,7,10,1,r->power,r->mode,1,r->record,true,true);uint64_t c=rear_p1_create_begin(s,7,10,1,r->record,1);
  rear_p1_emit(s,7,c,1,count,10,1,r->record,1,p,q.gr,&q,true,true,true);rear_p1_create_end(s,c);shots[count]=q;records[count]=r->record;modes[count]=r->mode+1;phases[count]=p;count++;
 }
 CHECK(count==77);
 for(unsigned pi=0;pi<12;pi++)for(unsigned mode=0;mode<3;mode++) {
  rear_p1_call_begin(s,8,10,1,pi,mode,1,(mode?265:254)+pi,true,true);rear_p1_call_end(s);
  for(unsigned i=0;i<count;i++){RearP1Shot *q=&shots[i];bool expected=q->gr!=163&&q->gr!=164;CHECK(rear_p1_current(s,i,q->gr,q->gr,q,true,true,true)==expected);if(expected)CHECK(s->birth[i].record==records[i]&&s->birth[i].mode==modes[i]&&s->birth[i].phase==phases[i]);}
 }
 /* Invalidating only one route cannot revoke any other matching raw birth. */
 for(unsigned i=0;i<count;i++)if(records[i]==262){RearP1Shot *q=&shots[i];CHECK(!rear_p1_current(s,i,q->gr,q->gr,q,true,false,true));}
 for(unsigned i=0;i<count;i++){RearP1Shot *q=&shots[i];CHECK(rear_p1_current(s,i,q->gr,q->gr,q,true,true,true)==(records[i]!=262&&q->gr!=163&&q->gr!=164));}
 rear_p1_reset(s);for(unsigned i=0;i<80;i++)empty(s,i);
}
int main(void)
{RearP1State s={0};admission(&s);capacities(&s);rejection(&s);leases(&s);integrity(&s);shared_seals(&s);coexistence(&s);printf("Rear P9 mode1 ownership PASS: %u checks; exact262 budget6/period6,294 cyclic capacity designs,80x80 slot reuse,leases,seals,18 routes/77 phases,1262, opposite273 and wrong-mode exclusions\n",checks);return 0;}
