/* SPDX-License-Identifier: GPL-2.0-or-later
 * Pure contract checks. No SDL/game entry, data files or admission state. */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "../experimental/level2-family/src/lamp272_top_clip_contract.h"
int main(void)
{
 const int parts[]={0,1,19,20};unsigned cases=0;
 for(int by=-13;by<0;by++)for(unsigned k=0;k<4;k++){
  int part=parts[k],px=(part==1||part==20)?12:0,py=part>=19?14:0;
  Lamp272TopClipPlan p;
  assert(lamp272_top_clip_plan(68+px,by+py,part,&p));
  unsigned n=0;
  /* Independent full-body source coordinates clipped against physical y=0. */
  for(unsigned sy=0;sy<14;sy++)for(unsigned sx=0;sx<12;sx++){
   int x=68+px+(int)sx,y=by+py+(int)sy;if(y<0)continue;
   assert(lamp272_top_clip_store(&p,n,(unsigned)x,(unsigned)y,0));
   assert(!lamp272_top_clip_store(&p,n,(unsigned)x+1,(unsigned)y,0));
   assert(!lamp272_top_clip_store(&p,n,(unsigned)x,(unsigned)y,1));
   for(unsigned yy=0;yy<8;yy++)for(unsigned xx=0;xx<8;xx++){
    size_t expected=((size_t)(py+(int)sy)*8+yy)*192*4+((size_t)(px+(int)sx)*8+xx)*4;
    assert(lamp272_top_clip_rgba_offset(&p,n,xx,yy)==expected);
   }
   ++n;
  }
  assert(n==p.stores);
  assert(!lamp272_top_clip_store(&p,n,68,0,0));
  assert(lamp272_top_clip_rgba_offset(&p,n,0,0)==SIZE_MAX);++cases;
 }
 Lamp272TopClipPlan p;
 assert(!lamp272_top_clip_plan(23,-1,0,&p));
 assert(!lamp272_top_clip_plan(265,-1,0,&p));
 assert(!lamp272_top_clip_plan(24,-14,0,&p));
 assert(!lamp272_top_clip_plan(24,0,0,&p));
 assert(!lamp272_top_clip_plan(24,157,0,&p));
 assert(!lamp272_top_clip_plan(24,-1,2,&p));
 assert(!lamp272_top_clip_plan(INT_MIN,-1,20,&p));
 assert(!lamp272_top_clip_plan(INT_MAX,INT_MAX,0,&p));
 uint8_t encoded[256]={2,0},decoded[168];size_t pos=2;
 for(unsigned y=0;y<14;y++){
  encoded[pos++]=0xc0;for(unsigned x=0;x<12;x++)encoded[pos++]=0;
  encoded[pos++]=0;
 }
 encoded[pos++]=15;
 assert(lamp272_top_clip_source(encoded,pos,1,decoded));
 for(unsigned i=0;i<168;i++)assert(decoded[i]==0); /* opaque zero stores */
 assert(!lamp272_top_clip_source(encoded,2,1,decoded));
 assert(!lamp272_top_clip_source(encoded,pos,0,decoded));
 assert(!lamp272_top_clip_source(encoded,pos,256,decoded));
 encoded[2]=0xc1;assert(!lamp272_top_clip_source(encoded,pos,1,decoded));
 printf("PASS: %u top/quadrant cases; boundary/order/style/source checks\n",cases);
 return 0;
}
