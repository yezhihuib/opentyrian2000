#include "world_material_fast.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
static uint8_t texels[G101_ATLAS_BYTES];
static G101FastContext fast;
static uint64_t count;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static void test_full_primary_identity(void)
{
 G101Atlas atlas={texels,sizeof(texels),768,896,8};
 G101Context world={true,false,0,0};CHECK(g101_fast_prepare(&fast,&world,&atlas,8));
 uint8_t saved[4];memcpy(saved,texels,4);
 uint8_t old[4]={91,73,45,0},base[4]={0},gen[4]={13,177,239,0},a[4],b[4];
 G101Pixel p={.accepted_rgba=old,.clean_rgba=base,.primary_weight=255,.reconstruction_verified=true};
 uint64_t cases=0,replacements=0;
 /* Alpha is independent of every weight. Exhaust all channel-value pairs
  * and all selected-pack alpha bytes, including successful nonzero alpha. */
 for(unsigned alpha=0;alpha<256;alpha++)for(unsigned clean=0;clean<256;clean++)for(unsigned material=0;material<256;material++) {
  old[3]=(uint8_t)alpha;
  base[0]=(uint8_t)clean;base[1]=(uint8_t)(clean*73);base[2]=(uint8_t)(255-clean);base[3]=(uint8_t)(255-alpha);
  texels[0]=(uint8_t)material;texels[1]=(uint8_t)(255-material);texels[2]=(uint8_t)(material*151);texels[3]=255;
  /* A zero generated weight permits either a present or absent input. */
  p.generated_footer_rgba=(clean&1)?gen:NULL;
  bool scalar=g101_select_pixel(&world,&atlas,&p,true,8,0,0,a);
  bool speedy=g101_fast_select_pixel(&fast,&p,true,0,0,b);
  CHECK(scalar==speedy&&speedy==(alpha!=0)&&!memcmp(a,b,4));
  CHECK(b[3]==alpha);CHECK(!memcmp(b,alpha?texels:old,3));
  ++cases;replacements+=speedy;
 }
 /* Secondary stages must prevent the shortcut even with primary255.
  * Independently sweep both secondary weights and representative primary
  * weights/alphas, comparing both return status and all four output bytes. */
 const uint8_t values[]={0,1,127,254,255};uint64_t mixed=0;
 for(unsigned ai=0;ai<5;ai++)for(unsigned pi=0;pi<5;pi++)for(unsigned g=0;g<256;g++)for(unsigned f=0;f<256;f++) {
  old[3]=values[ai];p.primary_weight=values[pi];p.generated_weight=(uint8_t)g;p.footer_weight=(uint8_t)f;p.generated_footer_rgba=gen;
  bool scalar=g101_select_pixel(&world,&atlas,&p,true,8,0,0,a);
  bool speedy=g101_fast_select_pixel(&fast,&p,true,0,0,b);
  CHECK(scalar==speedy&&!memcmp(a,b,4));CHECK(b[3]==old[3]);++mixed;
 }
 p.primary_weight=255;p.generated_weight=p.footer_weight=0;p.generated_footer_rgba=NULL;old[3]=173;
 CHECK(!g101_fast_select_pixel(&fast,&p,false,0,0,b)&&!memcmp(b,old,4));
 p.clean_rgba=NULL;CHECK(!g101_fast_select_pixel(&fast,&p,true,0,0,b)&&!memcmp(b,old,4));p.clean_rgba=base;
 p.reconstruction_verified=false;CHECK(!g101_fast_select_pixel(&fast,&p,true,0,0,b)&&!memcmp(b,old,4));p.reconstruction_verified=true;
 p.generated_weight=1;CHECK(!g101_fast_select_pixel(&fast,&p,true,0,0,b)&&!memcmp(b,old,4));p.generated_weight=0;
 p.primary_weight=0;CHECK(!g101_fast_select_pixel(&fast,&p,true,0,0,b)&&!memcmp(b,old,4));p.primary_weight=255;
 CHECK(!g101_fast_select_pixel(NULL,&p,true,0,0,b)&&!memcmp(b,old,4));
 const int outside[][2]={{-1,0},{0,-1},{2560,0},{0,1600}};
 for(unsigned i=0;i<4;i++)CHECK(!g101_fast_select_pixel(&fast,&p,true,outside[i][0],outside[i][1],b)&&!memcmp(b,old,4));
 g101_fast_invalidate(&fast);CHECK(!g101_fast_select_pixel(&fast,&p,true,0,0,b)&&!memcmp(b,old,4));
 memcpy(texels,saved,4);
 printf("PASS independent full-primary alpha/color identity: %" PRIu64 " cases, %" PRIu64 " nonzero-alpha replacements; %" PRIu64 " secondary-weight cases; guards and exact return/RGBA parity\n",cases,replacements,mixed);
}
int main(void)
{
 for(unsigned i=0;i<G101_ATLAS_W*G101_ATLAS_H;i++) {
  texels[4*i]=(uint8_t)i;texels[4*i+1]=(uint8_t)(i>>8);texels[4*i+2]=(uint8_t)(i>>16);texels[4*i+3]=255;
 }
 G101Atlas atlas={texels,sizeof(texels),768,896,8};
 const int64_t origins[][2]={{0,0},{48,8009},{37,7919},{37,7918},{-1,-1},{-1000,-1000},{96,112},{-96,-112},{24*299,28*299},{INT64_MIN,INT64_MAX},{INT64_MAX,INT64_MIN},{47,-27}};
 for(unsigned n=0;n<sizeof(origins)/sizeof(*origins);n++) {
  G101Context world={true,false,origins[n][0],origins[n][1]};CHECK(g101_fast_prepare(&fast,&world,&atlas,8));
  for(int y=0;y<1600;y++)for(int x=0;x<2560;x++) {
   uint8_t a[4],b[4];CHECK(g101_sample(&world,&atlas,8,x,y,a));CHECK(g101_fast_sample(&fast,x,y,b));CHECK(!memcmp(a,b,4));++count;
  }
 }
 uint8_t out[4];CHECK(!g101_fast_sample(&fast,-1,0,out));CHECK(!g101_fast_sample(&fast,0,-1,out));
 CHECK(!g101_fast_sample(&fast,2560,0,out));CHECK(!g101_fast_sample(&fast,0,1600,out));
 g101_fast_invalidate(&fast);CHECK(!g101_fast_sample(&fast,0,0,out));
 G101Context world={true,false,48,8009};CHECK(!g101_fast_prepare(&fast,&world,&atlas,4));CHECK(!fast.valid);
 world.rejected=true;CHECK(!g101_fast_prepare(&fast,&world,&atlas,8));world.rejected=false;world.valid=false;
 CHECK(!g101_fast_prepare(&fast,&world,&atlas,8));world.valid=true;G101Atlas bad=atlas;bad.bytes--;
 CHECK(!g101_fast_prepare(&fast,&world,&bad,8));CHECK(!fast.valid);
 CHECK(g101_fast_prepare(&fast,&world,&atlas,8));
 for(unsigned v=0;v<256;v++) {
  uint8_t old[4]={91,73,45,(uint8_t)v},base[4]={34,56,89,255},gen[4]={13,177,239,0},a[4],b[4];
  for(unsigned w=0;w<256;w++) {
   G101Pixel p={.accepted_rgba=old,.clean_rgba=base,.primary_weight=(uint8_t)w,.footer_weight=(uint8_t)(255-w),.generated_footer_rgba=gen,.generated_weight=(uint8_t)v,.reconstruction_verified=true};
   bool scalar=g101_select_pixel(&world,&atlas,&p,true,8,(int)w*8,(int)v*6,a);
   bool speedy=g101_fast_select_pixel(&fast,&p,true,(int)w*8,(int)v*6,b);
   CHECK(scalar==speedy&&!memcmp(a,b,4));
   p.clean_rgba=NULL;CHECK(!g101_fast_select_pixel(&fast,&p,true,0,0,b));CHECK(!memcmp(old,b,4));
  }
 }
 printf("PASS exhaustive full-canvas scalar/fast equality: %" PRIu64 " samples across12 transforms; negative origins/extremes/rowwrap;65536 composite/alpha cases; bounds and invalidation\n",count);
 printf("Lookup table payload=%zu bytes, context sizeof=%zu bytes, no frame heap allocation\n",sizeof(fast.columns)+sizeof(fast.rows),sizeof(fast));
 test_full_primary_identity();
 return 0;
}
