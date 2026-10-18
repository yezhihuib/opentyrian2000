/* SPDX-License-Identifier: GPL-2.0-or-later
 * Synthetic finite-call ownership. No game records or decoded original art. */
#include "rear_multi_p1.h"
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
static const unsigned ids[]={39,1,281,282,301,300};
static const int dx[]={-10,10,-9,9,9,-9},dy[]={0,0,-2,-2,2,2};
static unsigned member(unsigned mode,unsigned phase){return mode?phase+1:phase-1;}
static RearP1Shot shot(unsigned k){return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,dx[k],dy[k],0,0};}
static uint64_t begin(RearP1State*s,unsigned power,unsigned mode){unsigned record=(mode?265:254)+power;rear_p1_call_begin(s,7,10,1,power,mode,1,record,true,true);assert(s->pending&&!s->lease);return rear_p1_create_begin(s,7,10,1,record,1);}
static void emit(RearP1State*s,uint64_t call,unsigned ordinal,unsigned slot,unsigned mode,unsigned phase){unsigned k=member(mode,phase);RearP1Shot q=shot(k);rear_p1_emit(s,7,call,ordinal,slot,10,1,s->record,1,phase,ids[k],&q,true,true,true);}
static bool current(RearP1State*s,unsigned slot,unsigned mode,unsigned phase){unsigned k=member(mode,phase);RearP1Shot q=shot(k);return rear_p1_current(s,slot,ids[k],ids[k],&q,true,true,true);}
int main(void){RearP1State s={0};rear_p1_reset(&s);
 for(unsigned power=0;power<2;power++)for(unsigned mode=0;mode<2;mode++)for(unsigned phase=1;phase<=(mode?4u:2u);phase++){
  unsigned period=mode?4:2,next=phase==period?1:phase+1;uint64_t c=begin(&s,power,mode);
  assert(s.remaining==power+1&&s.next_ordinal==1&&!s.next_phase);
  emit(&s,c,1,0,mode,phase);assert(current(&s,0,mode,phase));assert(s.remaining==power&&s.next_ordinal==2&&s.next_phase==next);
  emit(&s,c,2,1,mode,next);assert(current(&s,1,mode,next)==(power==1));assert(current(&s,0,mode,phase));
  emit(&s,c,3,2,mode,phase);assert(!current(&s,2,mode,phase));assert(!s.lease&&!s.remaining);
  rear_p1_create_end(&s,c);assert(!s.call&&!s.remaining&&!s.next_phase&&!s.next_ordinal);
  assert(current(&s,0,mode,phase));if(power)assert(current(&s,1,mode,next));
  /* A partial call consumes one canonical phase; a later call may start at
   * its cyclic successor, including (2,1), (2,3), (4,1) P2 pairs. */
  c=begin(&s,power,mode);emit(&s,c,1,0,mode,phase);rear_p1_create_end(&s,c);
  c=begin(&s,power,mode);emit(&s,c,1,1,mode,next);assert(current(&s,1,mode,next));rear_p1_create_end(&s,c);
 }
 for(unsigned mode=0;mode<2;mode++)for(unsigned phase=1;phase<=(mode?4u:2u);phase++){
  unsigned period=mode?4:2,next=phase==period?1:phase+1,k=member(mode,phase),r=mode?266:255;
  /* A rejected allocated position consumes and cancels the whole remainder.
   * Source/shot/raw rejection and invalid slots cannot donate another shot. */
  for(unsigned kind=0;kind<7;kind++){
   uint64_t c=begin(&s,1,mode);RearP1Shot q=shot(k);if(kind==0)q.ani=1;
   rear_p1_emit(&s,7,c,1,kind==3?80:kind==4?UINT_MAX:0,10,1,r,1,phase,kind==1?0:ids[k],kind==2?NULL:&q,true,true,kind!=5);
   if(kind<6)assert(!current(&s,0,mode,phase)||kind==3||kind==4);
   assert(s.remaining==(kind==6?1u:0u));emit(&s,c,2,1,mode,next);assert(current(&s,1,mode,next)==(kind==6));
   emit(&s,c,3,2,mode,phase);assert(!current(&s,2,mode,phase));rear_p1_create_end(&s,c);
  }
  /* Repeated slot is an actual reuse: clear that birth and reject ordinal2.
   * A rejected second at a distinct slot leaves the valid first birth alone. */
  for(unsigned kind=0;kind<7;kind++){
   uint64_t c=begin(&s,1,mode);emit(&s,c,1,0,mode,phase);assert(current(&s,0,mode,phase));
   unsigned nk=member(mode,next);RearP1Shot q=shot(nk);if(kind==0)q.ani=1;
   rear_p1_emit(&s,7,c,2,kind==3?80:kind==4?UINT_MAX:kind==6?0:1,10,1,r,1,next,kind==1?0:ids[nk],kind==2?NULL:&q,true,true,kind!=5);
   assert(!s.remaining&&!s.lease);assert(current(&s,0,mode,phase)==(kind!=6));assert(!current(&s,1,mode,next));
  }
  /* Protocol/context failures terminate the entire remaining grant. */
  for(unsigned kind=0;kind<11;kind++){
   uint64_t c=begin(&s,1,mode);RearP1Shot q=shot(k);
   rear_p1_emit(&s,kind==0?8:7,kind==1?c+1:c,kind==2?2:1,0,kind==3?37:10,kind==4?0:1,kind==5?254:r,kind==6?2:1,kind==7?0:phase,ids[k],&q,kind!=8,kind!=9,true);
   if(kind==10){emit(&s,c,2,1,mode,phase);assert(!current(&s,1,mode,phase));}
   else assert(!current(&s,0,mode,phase));
   emit(&s,c,2,1,mode,next);assert(!current(&s,1,mode,next));assert(!s.remaining&&!s.lease);
  }
  /* Same tuple, same tick nested/unwrapped calls cannot claim an active
   * token; ending the inner call never restores the outer grant. */
  uint64_t c=begin(&s,1,mode),inner=rear_p1_create_begin(&s,7,10,1,r,1);assert(c!=inner&&!s.lease);
  emit(&s,inner,1,0,mode,phase);assert(!current(&s,0,mode,phase));rear_p1_create_end(&s,inner);
  emit(&s,c,1,0,mode,phase);assert(!current(&s,0,mode,phase));
  c=begin(&s,1,mode);emit(&s,c,1,0,mode,phase);inner=rear_p1_create_begin(&s,7,10,1,r,1);emit(&s,inner,1,1,mode,next);emit(&s,c,2,2,mode,next);assert(current(&s,0,mode,phase)&&!current(&s,1,mode,next)&&!current(&s,2,mode,next));
  /* No allocation (bounds/power/full capacity), call end, and frame end
   * cannot leak a pending grant into a later shop/shared consumer. */
  c=begin(&s,1,mode);rear_p1_create_end(&s,c);inner=rear_p1_create_begin(&s,7,10,1,r,1);emit(&s,inner,1,0,mode,phase);assert(!current(&s,0,mode,phase));
  rear_p1_call_begin(&s,7,10,1,1,mode,1,r,true,true);rear_p1_call_end(&s);inner=rear_p1_create_begin(&s,7,10,1,r,1);emit(&s,inner,1,0,mode,phase);assert(!current(&s,0,mode,phase));
  c=begin(&s,1,mode);rear_p1_reset(&s);inner=begin(&s,1,mode);assert(c!=inner);emit(&s,c,1,0,mode,phase);assert(!current(&s,0,mode,phase));
  for(unsigned power=2;power<11;power++){if((power==10&&mode==1)||power==2||power==3||power==4||power==5||power==6||power==7||power==8||power==9)continue;rear_p1_call_begin(&s,7,10,1,power,mode,1,r+power-1,true,true);assert(!s.pending);inner=rear_p1_create_begin(&s,7,10,1,r+power-1,1);emit(&s,inner,1,0,mode,phase);assert(!current(&s,0,mode,phase));}
 }
 puts("Rear P1/P2 ownership: finite ordinal budget, cyclic partial continuation, rejection consumption, token isolation and higher-power exclusions passed");return 0;}
