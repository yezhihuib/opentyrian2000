/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic two-head invocation ownership; no original game payloads. */
#include "rear_multi_p1.h"
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static const unsigned ids[]={40,2};
static const int dx[]={-10,10},dy[]={0,0};
static unsigned phase(unsigned start,unsigned ordinal){return (start+ordinal-2)%2+1;}
static RearP1Shot shot(unsigned p){unsigned k=p-1;return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,dx[k],dy[k],0,0};}
static uint64_t begin(RearP1State*s){rear_p1_call_begin(s,7,10,1,2,0,1,256,true,true);CHECK(s->pending&&s->budget==2);uint64_t c=rear_p1_create_begin(s,7,10,1,256,1);CHECK(s->lease&&s->remaining==2&&s->next_ordinal==1&&!s->used_count);return c;}
static void emit(RearP1State*s,uint64_t c,unsigned n,unsigned slot,unsigned p){RearP1Shot q=shot(p);rear_p1_emit(s,7,c,n,slot,10,1,256,1,p,ids[p-1],&q,true,true,true);}
static bool current(RearP1State*s,unsigned slot,unsigned p){RearP1Shot q=shot(p);return rear_p1_current(s,slot,ids[p-1],ids[p-1],&q,true,true,true);}
static void clear(const RearP1State*s){CHECK(!s->pending&&!s->lease&&!s->call&&!s->remaining&&!s->budget&&!s->next_ordinal&&!s->next_phase&&!s->used_count);for(unsigned i=0;i<4;i++)CHECK(!s->used_slots[i]);}
int main(void){RearP1State s={0};
 /* Both cyclic starts, partial prior calls, capacities0..2 and both positions. */
 for(unsigned start=1;start<=2;start++)for(unsigned prior=0;prior<2;prior++)for(unsigned cap=0;cap<=2;cap++){
  rear_p1_reset(&s);uint64_t c=begin(&s);
  for(unsigned n=1;n<=prior;n++)emit(&s,c,n,20+n,phase(start,n));
  rear_p1_create_end(&s,c);clear(&s);unsigned next=phase(start,prior+1);c=begin(&s);
  for(unsigned n=1;n<=cap;n++){unsigned p=phase(next,n);emit(&s,c,n,10+n,p);CHECK(current(&s,10+n,p));CHECK(s.remaining==2-n&&s.used_count==n&&s.next_ordinal==n+1);}
  rear_p1_create_end(&s,c);clear(&s);
  for(unsigned n=1;n<=cap;n++)CHECK(current(&s,10+n,phase(next,n)));
  for(unsigned n=1;n<=prior;n++)CHECK(current(&s,20+n,phase(start,n)));
  emit(&s,c,cap+1,0,phase(next,cap+1));CHECK(!current(&s,0,phase(next,cap+1)));clear(&s);
 }
 /* A third position is rejected, retaining both immutable births. */
 for(unsigned start=1;start<=2;start++){
  rear_p1_reset(&s);uint64_t c=begin(&s);for(unsigned n=1;n<=2;n++)emit(&s,c,n,n,phase(start,n));
  emit(&s,c,3,3,start);CHECK(!current(&s,3,start));clear(&s);for(unsigned n=1;n<=2;n++)CHECK(current(&s,n,phase(start,n)));
 }
 /* Second-slot reuse clears that slot and cancels the invocation. */
 for(unsigned start=1;start<=2;start++)for(unsigned bad=2;bad<=2;bad++)for(unsigned reused=1;reused<bad;reused++){
  rear_p1_reset(&s);uint64_t c=begin(&s);for(unsigned n=1;n<bad;n++)emit(&s,c,n,n,phase(start,n));
  emit(&s,c,bad,reused,phase(start,bad));clear(&s);
  for(unsigned n=1;n<bad;n++)CHECK(current(&s,n,phase(start,n))==(n!=reused));
  for(unsigned n=bad+1;n<=2;n++){emit(&s,c,n,n,phase(start,n));CHECK(!current(&s,n,phase(start,n)));}
 }
 /* Reject at each position: invalid source/shot/raw/slot/context/protocol.
  * Every rejection destroys the remaining grant; earlier distinct births live. */
 for(unsigned start=1;start<=2;start++)for(unsigned bad=1;bad<=2;bad++)for(unsigned kind=0;kind<22;kind++){
  rear_p1_reset(&s);uint64_t c=begin(&s);for(unsigned n=1;n<bad;n++)emit(&s,c,n,n,phase(start,n));
  unsigned p=phase(start,bad),slot=kind==3?80:kind==4?UINT_MAX:kind==21?81:bad;RearP1Shot q=shot(p);if(kind==0)q.xm++;if(kind==20)q.chain=49;
  rear_p1_emit(&s,kind==6?8:7,kind==7?c+1:kind==19?0:c,kind==8?bad+1:kind==9?0:bad,slot,kind==10?37:10,kind==11?0:1,kind==12?255:256,kind==13?2:1,kind==14?0:kind==15?3:kind==16?(p%2+1):p,kind==1?0:ids[p-1],kind==2?NULL:&q,kind!=17,kind!=18,kind!=5);
  clear(&s);CHECK(!current(&s,slot,p));
  for(unsigned n=1;n<bad;n++)CHECK(current(&s,n,phase(start,n)));
  for(unsigned n=bad+1;n<=2;n++){emit(&s,c,n,n,phase(start,n));CHECK(!current(&s,n,phase(start,n)));}
 }
 /* Nested, stale, wrong-entry, no-entry and end/frame reset isolation. */
 for(unsigned after=0;after<=2;after++)for(unsigned kind=0;kind<9;kind++){
  rear_p1_reset(&s);uint64_t c=begin(&s);for(unsigned n=1;n<=after;n++)emit(&s,c,n,n,n);
  uint64_t inner=0;
  if(kind==0)inner=rear_p1_create_begin(&s,7,10,1,256,1);
  if(kind==1)rear_p1_create_end(&s,c);
  if(kind==2)rear_p1_call_end(&s);
  if(kind==3)rear_p1_reset(&s);
  if(kind==4){rear_p1_call_begin(&s,7,10,1,2,0,1,256,true,true);inner=rear_p1_create_begin(&s,8,10,1,256,1);}
  if(kind==5){rear_p1_call_begin(&s,7,10,1,2,0,1,256,true,true);inner=rear_p1_create_begin(&s,7,37,1,256,1);}
  if(kind==6){rear_p1_call_begin(&s,7,10,1,2,0,1,256,true,true);inner=rear_p1_create_begin(&s,7,10,0,256,1);}
  if(kind==7){rear_p1_call_begin(&s,7,10,1,2,0,1,256,true,true);inner=rear_p1_create_begin(&s,7,10,1,255,1);}
  if(kind==8){rear_p1_call_begin(&s,7,10,1,2,0,1,256,true,true);inner=rear_p1_create_begin(&s,7,10,1,256,2);}
  if(inner){CHECK(inner!=c);emit(&s,inner,1,10,1);CHECK(!current(&s,10,1));rear_p1_create_end(&s,inner);}
  emit(&s,c,after+1,11,phase(1,after+1));CHECK(!current(&s,11,phase(1,after+1)));clear(&s);
  for(unsigned n=1;n<=after;n++)CHECK(current(&s,n,n)==(kind!=3));
 }
 rear_p1_reset(&s);rear_p1_call_begin(&s,7,10,1,2,0,1,256,true,true);emit(&s,0,1,0,1);CHECK(!current(&s,0,1));clear(&s);
 /* Exhaustive power/mode/record admission including both P3 modes, P4 and shared uses. */
 const unsigned records[]={254,255,256,257,265,266,267,268,50,445,501,686,687,688,690,275,1256,1267,1275,0,UINT_MAX};
 for(unsigned power=0;power<12;power++)for(unsigned mode=0;mode<3;mode++)for(unsigned r=0;r<sizeof records/sizeof *records;r++){
  unsigned record=records[r];rear_p1_call_begin(&s,7,10,1,power,mode,1,record,true,true);
  bool yes=(power<2&&mode<2&&record==(mode?265:254)+power)||(power==2&&mode<2&&record==(mode?267:256));CHECK(s.pending==yes);
  if(yes)CHECK(s.budget==(power==2?(mode?4:2):power+1));
 }
 for(unsigned bad=0;bad<5;bad++){rear_p1_call_begin(&s,7,bad==0?37:10,bad==1?0:1,2,0,bad==2?2:1,256,bad!=3,bad!=4);CHECK(!s.pending);}
 /* Every raw alias and immutable field must fail closed at both phases. */
 for(unsigned p=1;p<=2;p++)for(unsigned field=0;field<13;field++){
  rear_p1_reset(&s);uint64_t c=begin(&s);emit(&s,c,1,79,p);CHECK(current(&s,79,p));RearP1Shot q=shot(p);
  switch(field){case 0:q.gr++;break;case 1:q.ani++;break;case 2:q.ani_max++;break;case 3:q.player++;break;case 4:q.trail--;break;case 5:q.aim++;break;case 6:q.chain++;break;case 7:q.complicated++;break;case 8:q.filter=112;break;case 9:q.xm++;break;case 10:q.ym++;break;case 11:q.xc++;break;case 12:q.yc++;break;}
  CHECK(!rear_p1_current(&s,79,ids[p-1],ids[p-1],&q,true,true,true));CHECK(!current(&s,79,p));
 }
 for(unsigned p=1;p<=2;p++)for(unsigned kind=0;kind<5;kind++){
  rear_p1_reset(&s);uint64_t c=begin(&s);emit(&s,c,1,0,p);RearP1Shot q=shot(p);
  CHECK(!rear_p1_current(&s,0,kind==3?ids[p-1]+1000:ids[p-1],kind==4?ids[p-1]+1000:ids[p-1],&q,kind!=0,kind!=1,kind!=2));CHECK(!current(&s,0,p));
 }
 /* Both new lateral births coexist with genuine old lateral/diagonal births.
  * Equipment selection alone retains them; an actual recycled slot revokes it. */
 rear_p1_reset(&s);uint64_t c=begin(&s);emit(&s,c,1,0,1);emit(&s,c,2,1,2);rear_p1_create_end(&s,c);
 const unsigned oldids[]={39,1,281,282,301,300};const int ox[]={-10,10,-9,9,9,-9},oy[]={0,0,-2,-2,2,2};
 for(unsigned k=0;k<6;k++){unsigned r=k<2?254:265,m=k<2?0:1,p=k<2?k+1:k-1;RearP1Shot q={oldids[k],0,1,1,255,0,0,0,208,ox[k],oy[k],0,0};rear_p1_call_begin(&s,8,10,1,0,m,1,r,true,true);c=rear_p1_create_begin(&s,8,10,1,r,1);rear_p1_emit(&s,8,c,1,k+2,10,1,r,1,p,oldids[k],&q,true,true,true);CHECK(rear_p1_current(&s,k+2,oldids[k],oldids[k],&q,true,true,true));rear_p1_create_end(&s,c);CHECK(current(&s,0,1)&&current(&s,1,2));}
 for(unsigned power=0;power<12;power++)for(unsigned mode=0;mode<2;mode++){rear_p1_call_begin(&s,9,10,1,power,mode,1,(mode?265:254)+power,true,true);rear_p1_call_end(&s);CHECK(current(&s,0,1)&&current(&s,1,2));}
 c=rear_p1_create_begin(&s,9,10,1,275,1);emit(&s,c,1,0,1);CHECK(!current(&s,0,1)&&current(&s,1,2));rear_p1_reset(&s);CHECK(!current(&s,1,2));
 CHECK(rear_p1_member(40)==6&&rear_p1_member(2)==7);CHECK(rear_p1_member(1040)<0&&rear_p1_member(1002)<0);
 printf("Rear P3 mode1 ownership PASS: %u checks; two ordinals, cyclic partial capacities, rejection, isolation and mixed births\n",checks);return 0;
}
