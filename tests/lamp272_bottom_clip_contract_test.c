/* SPDX-License-Identifier: GPL-2.0-or-later */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "../experimental/level2-family/src/lamp272_bottom_clip_contract.h"
int main(void){
 const int parts[]={0,1,19,20};unsigned cases=0,stores=0,visible=0;
 for(int bx=24;bx<=264;bx+=12)for(int by=157;by<=174;by++)for(unsigned k=0;k<4;k++){
  int part=parts[k],px=(part==1||part==20)?12:0,py=part>=19?14:0;
  Lamp272BottomClipPlan p;assert(lamp272_bottom_clip_plan(bx+px,by+py,part,&p));unsigned n=0;
  for(unsigned row=0;row<14;row++)for(unsigned col=0;col<12;col++){
   int address=(by+py+(int)row)*320+bx+px+(int)col;if(address>=320*200)goto ended;
   unsigned x=(unsigned)address%320,y=(unsigned)address/320;
   assert(lamp272_bottom_clip_store(&p,n,x,y,0));
   assert(!lamp272_bottom_clip_store(&p,n,x+1,y,0));assert(!lamp272_bottom_clip_store(&p,n,x,y,1));
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    size_t expected=((size_t)(py+(int)row)*8+sy)*192*4+((size_t)(px+(int)col)*8+sx)*4;
    assert(lamp272_bottom_clip_rgba_offset(&p,n,sx,sy)==expected);assert(expected+3<192u*224u*4u);
   }
   if(y<184)++visible;
   ++n;
  }
ended:
  assert(n==p.stores&&n>=144);assert(!lamp272_bottom_clip_store(&p,n,(unsigned)(bx+px),(unsigned)(by+py),0));
  assert(lamp272_bottom_clip_rgba_offset(&p,n,0,0)==SIZE_MAX);assert(lamp272_bottom_clip_rgba_offset(&p,0,8,0)==SIZE_MAX);
  stores+=n;++cases;
 }
 /* Mirror the original four-call scheduler, including its lower-half gate.
  * The unsupported two-call tail must be rejected before a quartet opens. */
 for(int by=156;by<=183;by++){
  int ey=by+7;unsigned calls=0,admitted=0;
  for(unsigned k=0;k<4;k++){
   int part=parts[k];bool dispatched=part<19?(ey> -13):(ey> -26&&ey<182);
   if(!dispatched)continue;
   ++calls;Lamp272BottomClipPlan q;
   if(lamp272_bottom_clip_plan(24+((part==1||part==20)?12:0),by+(part>=19?14:0),part,&q))++admitted;
  }
  if(by>=157&&by<=174){assert(calls==4&&admitted==4);}
  else assert(admitted==0);
 }
 Lamp272BottomClipPlan p;
 const int bad[][3]={{23,157,0},{265,157,0},{24,156,0},{24,175,0},{24,183,0},{24,184,0},{24,-1,0},{24,157,2},{INT_MIN,157,20},{INT_MAX,INT_MAX,0}};
 for(unsigned i=0;i<sizeof bad/sizeof*bad;i++)assert(!lamp272_bottom_clip_plan(bad[i][0],bad[i][1],bad[i][2],&p));
 assert(!lamp272_bottom_clip_plan(24,157,0,NULL));assert(!lamp272_bottom_clip_store(NULL,0,24,157,0));
 assert(lamp272_bottom_clip_rgba_offset(NULL,0,0,0)==SIZE_MAX);
 printf("PASS: %u cases, %u physical stores, %u playfield stores\n",cases,stores,visible);return 0;
}
