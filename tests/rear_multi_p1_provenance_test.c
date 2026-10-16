/* Independent reviewer fixture: compile the actual production core unchanged. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "rear_multi_p1.h"
static unsigned checks;
#define CHECK(x) do { ++checks; if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);} } while(0)
/* These P1 regression helpers model caller grant followed by actual entry.
 * The P2 ownership fixture exercises the new API directly without wrappers. */
static void p1_begin(RearP1State *s,uint64_t tick,unsigned port,unsigned bay,unsigned power,
 unsigned mode,unsigned player,unsigned record,bool scope,bool table)
{
 rear_p1_call_begin(s,tick,port,bay,power,mode,player,record,scope,table);
 (void)rear_p1_create_begin(s,tick,port,bay,record,player);
}
#define rear_p1_call_begin p1_begin
#define rear_p1_emit(s,t,...) rear_p1_emit(s,t,(s)->call,1,__VA_ARGS__)
static const unsigned ids[]={39,1,281,282,301,300};
static const int xm[]={-10,10,-9,9,9,-9},ym[]={0,0,-2,-2,2,2};
static RearP1Shot shot(unsigned k){return (RearP1Shot){ids[k],0,1,1,255,0,0,0,208,xm[k],ym[k],0,0};}
static void birth(RearP1State*s,unsigned slot,unsigned k){RearP1Shot q=shot(k);unsigned r=k<2?254:265,m=k<2?0:1,p=k<2?k+1:k-1;rear_p1_call_begin(s,7,10,1,0,m,1,r,true,true);rear_p1_emit(s,7,slot,10,1,r,1,p,ids[k],&q,true,true,true);rear_p1_call_end(s);}
static bool now(RearP1State*s,unsigned slot,unsigned k){RearP1Shot q=shot(k);return rear_p1_current(s,slot,ids[k],ids[k],&q,true,true,true);}
static void mutate(RearP1Shot*q,unsigned f){switch(f){case 0:q->gr++;break;case 1:q->ani++;break;case 2:q->ani_max++;break;case 3:q->player++;break;case 4:q->trail--;break;case 5:q->aim++;break;case 6:q->chain++;break;case 7:q->complicated++;break;case 8:q->filter=112;break;case 9:q->xm++;break;case 10:q->ym++;break;case 11:q->xc++;break;case 12:q->yc++;break;}}
int main(void){
 RearP1State s={0};rear_p1_reset(&s);CHECK(s.generation==1);CHECK(!s.lease);
 CHECK(rear_p1_stamp("hello",5)==UINT64_C(0xa430d84680aabd0b));
 for(unsigned k=0;k<6;k++){
  CHECK(rear_p1_member(ids[k])==(int)k);RearP1Shot q=shot(k),copy=q;unsigned r=k<2?254:265,m=k<2?0:1,p=k<2?k+1:k-1;
  for(unsigned slot=0;slot<80;slot++){
   birth(&s,slot,k);CHECK(now(&s,slot,k));CHECK(now(&s,slot,k));CHECK(s.birth[slot].raw==ids[k]);CHECK(s.birth[slot].record==r);
   rear_p1_call_end(&s);CHECK(now(&s,slot,k)); /* presentation/call end does not lose old birth */
   /* An excluded/unleased new allocation overwrites the reused slot even if raw ID matches. */
   rear_p1_emit(&s,7,slot,10,1,r,1,p,ids[k],&q,true,true,true);CHECK(!now(&s,slot,k));
  }
  for(unsigned f=0;f<13;f++){
   birth(&s,0,k);RearP1Shot bad=q;mutate(&bad,f);CHECK(!rear_p1_current(&s,0,ids[k],ids[k],&bad,true,true,true));CHECK(!now(&s,0,k));
   birth(&s,0,k);CHECK(now(&s,0,k)); /* fresh emission can qualify */
  }
  for(unsigned f=0;f<3;f++){
   birth(&s,0,k);CHECK(!rear_p1_current(&s,0,ids[k],ids[k],&q,f!=0,f!=1,f!=2));CHECK(!now(&s,0,k));
   rear_p1_call_begin(&s,7,10,1,0,m,1,r,true,true);rear_p1_emit(&s,7,0,10,1,r,1,p,ids[k],&q,f!=0,f!=1,f!=2);CHECK(!now(&s,0,k));
  }
  for(unsigned rawi=0;rawi<6;rawi++)if(rawi!=k){birth(&s,0,k);CHECK(!rear_p1_current(&s,0,ids[rawi],ids[rawi],&q,true,true,true));CHECK(!now(&s,0,k));}
  birth(&s,0,k);CHECK(!rear_p1_current(&s,0,ids[k],1000+ids[k],&q,true,true,true));CHECK(!now(&s,0,k));
  birth(&s,0,k);CHECK(!rear_p1_current(&s,0,ids[k]+1,ids[k],&q,true,true,true));CHECK(!now(&s,0,k));
  for(unsigned f=0;f<10;f++){
   birth(&s,0,k);
   rear_p1_call_begin(&s,7,f==0?37:10,f==1?0:1,f==2?1:0,f==3?m+2:m,f==4?2:1,f==5?445:r,f!=6,f!=7);
   rear_p1_emit(&s,f==8?8:7,0,10,1,r,1,f==9?0:p,ids[k],&q,true,true,true);CHECK(!now(&s,0,k));
  }
  for(unsigned f=0;f<5;f++){
   birth(&s,0,k);rear_p1_call_begin(&s,7,10,1,0,m,1,r,true,true);
   rear_p1_emit(&s,7,0,f==0?37:10,f==1?0:1,f==2?500:r,f==3?2:1,f==4?9:p,ids[k],&q,true,true,true);CHECK(!now(&s,0,k));
  }
  rear_p1_call_begin(&s,7,10,1,0,m,1,r,true,true);rear_p1_emit(&s,7,0,10,1,r,1,p,ids[k],&q,true,true,true);rear_p1_emit(&s,7,1,10,1,r,1,p,ids[k],&q,true,true,true);CHECK(now(&s,0,k));CHECK(!now(&s,1,k));
  for(unsigned field=0;field<5;field++){birth(&s,0,k);switch(field){case 0:s.birth[0].generation++;break;case 1:s.birth[0].record=445;break;case 2:s.birth[0].phase=0;break;case 3:s.birth[0].raw++;break;case 4:s.birth[0].mode+=2;break;}CHECK(!now(&s,0,k));CHECK(!s.birth[0].qualified);}
  birth(&s,0,k);rear_p1_reset(&s);CHECK(!now(&s,0,k));CHECK(!s.lease);CHECK(!memcmp(&q,&copy,sizeof q));
 }
 for(unsigned i=0;i<1000;i++){bool allowed=i==40||i==2||i==77||i==182||i==183||i==277||i==278;for(unsigned k=0;k<6;k++)allowed|=ids[k]==i;CHECK((rear_p1_member(i)>=0)==allowed);}
 for(unsigned slot=80;slot<84;slot++){RearP1State old=s;RearP1Shot q=shot(0);rear_p1_emit(&s,7,slot,10,1,254,1,1,39,&q,true,true,true);CHECK(!rear_p1_current(&s,slot,39,39,&q,true,true,true));CHECK(!memcmp(s.birth,old.birth,sizeof s.birth));}
 {RearP1Shot q=shot(0);CHECK(!rear_p1_current(&s,UINT_MAX,39,39,&q,true,true,true));rear_p1_emit(&s,7,UINT_MAX,10,1,254,1,1,39,&q,true,true,true);}
 s.generation=UINT64_MAX;s.lease=true;rear_p1_reset(&s);CHECK(s.generation==1);CHECK(!s.lease);
 printf("Independent provenance PASS: %u checks\n",checks);return 0;
}
