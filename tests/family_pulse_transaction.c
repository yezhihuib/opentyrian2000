/* Pure transaction oracle. Synthetic fixtures, no original game data. */
#include <assert.h>
#include <stdio.h>
#include "family_pulse_transaction.h"
static FamilyPulseTransaction t;
static uint8_t source[168],mask[168],before[168],art[43008],foreign[10752];
static uint32_t lower[10752],palette[256];
static void setup(void){
 for(unsigned i=0;i<168;i++){source[i]=(uint8_t)i;mask[i]=i%3?255:0;before[i]=0x25;}
 for(unsigned i=0;i<10752;i++){lower[i]=0xff102030;art[i*4]=240;art[i*4+1]=128;art[i*4+2]=32;art[i*4+3]=(uint8_t)(i%256);foreign[i]=i%2;}
 for(unsigned i=0;i<256;i++)palette[i]=0xff000000|i*0x010101;
}
static void begin(int y,int style){assert(fpt_begin(&t,42,y,style,source,mask,before,art,lower,foreign,palette));}
static void stores(void){for(unsigned i=0;i<t.count;i++){unsigned c=t.order[i];assert(fpt_store(&t,t.x+c%12,t.y+c/12,t.style,before[c],t.after[c]));}}
int main(void){setup();unsigned cases=0;
 for(int y=-13;y<200;y++)for(int style=0;style<=2;style+=2){begin(y,style);stores();assert(fpt_end(&t,t.after));
 for(unsigned c=0;c<168;c++){int yy=y+c/12;if(yy<0||yy>=200)continue;for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
 const uint32_t *p=fpt_sample(&t,42+c%12,yy,sx,sy);assert(!t.owned[c]||p);if(p){unsigned n=(c/12*8+sy)*96+c%12*8+sx,a=art[n*4+3];uint32_t want=0xff000000;
 for(unsigned ch=0;ch<3;ch++){unsigned shift=(2-ch)*8,l=(lower[n]>>shift)&255,hi=art[n*4+ch];
 if(style==2)hi=foreign[n]?(l+1)/2:(palette[(before[c]&240)|((before[c]&15)/2)]>>shift)&255;
 want|=((l*(255-a)+hi*a+127)/255)<<shift;}assert(*p==want);}}
 fpt_retire(&t,42+c%12,yy);assert(!fpt_sample(&t,42+c%12,yy,0,0));}cases++;}
 for(unsigned bad=0;bad<7;bad++){begin(20,0);unsigned c=t.order[0];int x=42+c%12,y=20+c/12;uint8_t b=before[c],a=t.after[c];
 if(bad==0)x++;
 if(bad==1)y++;
 if(bad==2)b++;
 if(bad==3)a++;
 if(bad<5)assert(!fpt_store(&t,x,y,bad==4?2:0,b,a));
 if(bad==5)assert(!fpt_end(&t,t.after));
 if(bad==6){stores();uint8_t final[168];memcpy(final,t.after,168);final[0]++;assert(!fpt_end(&t,final));}
 assert(!t.valid&&!fpt_sample(&t,x,y,0,0));cases++;}
 begin(20,0);stores();assert(!fpt_store(&t,42,20,0,0,0));cases++;
 mask[5]=1;assert(!fpt_begin(&t,42,20,0,source,mask,before,art,lower,foreign,palette));cases++;
 printf("%u transaction cases passed\n",cases);return 0;
}
