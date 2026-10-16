/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic renderer-identity tests. No original game payloads or decoded art. */
#include "../src/rear_multi_p1.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
static const unsigned ids[6]={39,1,281,282,301,300};
static const int velocities[6][2]={{-10,0},{10,0},{-9,-2},{9,-2},{9,2},{-9,2}};
static RearP1Shot shot(unsigned k)
{return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,velocities[k][0],velocities[k][1],0,0};}
static void emit(RearP1State *s,unsigned slot,unsigned k)
{
 unsigned mode=k<2?0:1,record=k<2?254:265,phase=k<2?k+1:k-1;RearP1Shot v=shot(k);
 rear_p1_call_begin(s,7,10,1,0,mode,1,record,true,true);
 rear_p1_emit(s,7,slot,10,1,record,1,phase,ids[k],&v,true,true,true);
}
static bool current(RearP1State *s,unsigned slot,unsigned k)
{RearP1Shot v=shot(k);return rear_p1_current(s,slot,ids[k],ids[k],&v,true,true,true);}
int main(void)
{
 RearP1State s={0};rear_p1_reset(&s);
 assert(s.generation==1);
 assert(rear_p1_stamp("",0)==UINT64_C(0xcbf29ce484222325));
 assert(rear_p1_stamp("a",1)==UINT64_C(0xaf63dc4c8601ec8c));
 for(unsigned k=0;k<6;k++) {
  emit(&s,k,k);assert(current(&s,k,k));assert(current(&s,k,k));
  assert(s.birth[k].phase==(k<2?k+1:k-1));
 }
 /* Current P1/P2 and mode selections cannot promote/demote existing shots. */
 for(unsigned mode=0;mode<2;mode++)for(unsigned power=0;power<11;power++) {
  rear_p1_call_begin(&s,8,10,1,power,mode,1,mode?265:254,true,true);rear_p1_call_end(&s);
  for(unsigned k=0;k<6;k++)assert(current(&s,k,k));
 }
 /* Every false allocation clears an earlier valid birth, including no graphics. */
 const unsigned ports[]={37,10,19,22,27,32,0,UINT_MAX};
 const unsigned records[]={254,265,49,50,51,445,500,501,0,UINT_MAX};
 for(unsigned p=0;p<sizeof(ports)/sizeof(*ports);p++)for(unsigned r=0;r<sizeof(records)/sizeof(*records);r++) {
  emit(&s,0,0);RearP1Shot v=shot(0);
  rear_p1_emit(&s,7,0,ports[p],1,records[r],1,1,39,&v,true,true,true);
  assert(!current(&s,0,0));
 }
 for(unsigned field=0;field<13;field++) {
  emit(&s,0,0);RearP1Shot v=shot(0),save=v;
  switch(field) {
   case 0:v.gr=1;break;case 1:v.ani=1;break;case 2:v.ani_max=2;break;
   case 3:v.player=2;break;case 4:v.trail=0;break;case 5:v.aim=1;break;
   case 6:v.chain=49;break;case 7:v.complicated=1;break;case 8:v.filter=0;break;
   case 9:v.xm++;break;case 10:v.ym++;break;case 11:v.xc=1;break;default:v.yc=1;break;
  }
  RearP1Shot before=v;assert(!rear_p1_current(&s,0,39,39,&v,true,true,true));
  assert(!memcmp(&v,&before,sizeof(v)));assert(!rear_p1_current(&s,0,39,39,&save,true,true,true));
 }
 /* Source/table/context/index/raw invalidity is one-way for this emission. */
 for(unsigned kind=0;kind<5;kind++) {
  emit(&s,0,0);RearP1Shot v=shot(0);
  assert(!rear_p1_current(&s,0,kind==3?1:39,kind==4?1:39,&v,kind!=0,kind!=1,kind!=2));
  assert(!current(&s,0,0));emit(&s,0,0);assert(current(&s,0,0));
 }
 for(unsigned kind=0;kind<3;kind++) {
  RearP1Shot v=shot(0);rear_p1_call_begin(&s,7,10,1,0,0,1,254,true,true);
  rear_p1_emit(&s,7,0,10,1,254,1,1,39,&v,kind!=0,kind!=1,kind!=2);
  assert(!current(&s,0,0));
 }
 /* Lease clearing on frame/end covers bounds/power/capacity no-allocation exits. */
 for(unsigned i=0;i<3;i++) {
  rear_p1_call_begin(&s,7,10,1,0,0,1,254,true,true);rear_p1_call_end(&s);
  RearP1Shot v=shot(0);rear_p1_emit(&s,7,0,10,1,254,1,1,39,&v,true,true,true);
  assert(!current(&s,0,0));emit(&s,0,0);assert(current(&s,0,0));
 }
 /* Wrong tick, tuple, mode, phase, power and nested second emission. */
 for(unsigned kind=0;kind<10;kind++) {
  rear_p1_call_begin(&s,7,kind==0?37:10,kind==1?0:1,kind==2?1:0,kind==3?1:0,kind==4?2:1,254,true,true);
  RearP1Shot v=shot(0);
  rear_p1_emit(&s,kind==5?8:7,0,kind==6?37:10,kind==7?0:1,kind==8?265:254,1,kind==9?2:1,39,&v,true,true,true);
  assert(!current(&s,0,0));
 }
 emit(&s,0,0);RearP1Shot v=shot(0);rear_p1_emit(&s,7,1,10,1,254,1,1,39,&v,true,true,true);assert(!current(&s,1,0));
 for(unsigned k=0;k<6;k++)emit(&s,k,k);
 rear_p1_reset(&s);for(unsigned k=0;k<6;k++)assert(!current(&s,k,k));
 unsigned invalid[]={80,81,UINT_MAX};
 for(unsigned i=0;i<3;i++) {emit(&s,invalid[i],0);assert(!current(&s,invalid[i],0));}
 s.generation=UINT64_MAX;rear_p1_reset(&s);assert(s.generation==1);
 puts("Rear P1 core: six phases, provenance, slot reuse, immutable identity, lease/reset and one-way revocation passed");
 return 0;
}
