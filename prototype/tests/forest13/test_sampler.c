/* Synthetic-only production forest sampler oracle. No game or asset approval. */
#include "forest13_material.h"
#include "forest13_bundle_index.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned allocations,frees,callbacks;
static uint64_t pixels;
static G101FastContext fast,snapshot;
static uint8_t lower[G101_ATLAS_BYTES],source[G101_TILE_PIXELS*4];
void *forest13_test_malloc(size_t n){++allocations;return malloc(n);}
void forest13_test_free(void *p){if(p)++frees;free(p);}
uint64_t game_probe_hash(uint64_t h,const void *data,size_t bytes)
{const uint8_t *p=data;while(bytes--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
const G101FastContext *ground101_fast_context(void){return fast.valid?&fast:NULL;}
static void base_pixel(unsigned i,unsigned n,uint8_t out[4])
{out[0]=(uint8_t)(n+31*i);out[1]=(uint8_t)(3*n+i);out[2]=(uint8_t)(n/17+11*i);out[3]=255;}
static const uint8_t *selected(unsigned id,unsigned slot,void *context)
{
 assert(context==&fast&&slot>=336&&slot<349);++callbacks;
 unsigned i=slot-336;assert(forest13_records[i].index==id);
 for(unsigned n=0;n<G101_TILE_PIXELS;n++)base_pixel(i,n,source+4*n);
 return source;
}
static unsigned mod(int64_t value,unsigned period)
{int64_t r=value%period;return (unsigned)(r<0?r+period:r);}
static void oracle(const G101Context *world,unsigned i,unsigned n,
 const uint8_t accepted[4],int x,int y,uint8_t out[4])
{
 memcpy(out,accepted,4);
 if(!world->valid||world->rejected||(unsigned)x>=2560||(unsigned)y>=1600||!accepted[3])return;
 unsigned ax=(mod(world->world_x,768)*8+(unsigned)x)%768;
 unsigned ay=(mod(world->world_y,896)*8+(unsigned)y)%896;
 unsigned rgb[3]={(ax^ay)&255,(ax/3+5*ay)&255,(7*ax+ay/2)&255};
 unsigned w=(n+17*i)&255;
 for(unsigned c=0;c<3;c++)out[c]=(uint8_t)(((uint64_t)accepted[c]*(255-w)+(uint64_t)rgb[c]*w+127)/255);
}
static void prepare(const G101Context *world)
{
 G101Atlas atlas={lower,sizeof(lower),768,896,8};
 assert(g101_fast_prepare(&fast,world,&atlas,8));snapshot=fast;
}
static void pixel(const G101Context *world,unsigned i,unsigned n,int x,int y,uint8_t alpha)
{
 uint8_t accepted[4],actual[4],expected[4];base_pixel(i,n,accepted);accepted[3]=alpha;
 const Forest13Record *r=forest13_record(forest13_records[i].index);assert(r);
 forest13_select(r,accepted,n,x,y,actual);oracle(world,i,n,accepted,x,y,expected);
 assert(!memcmp(actual,expected,4));assert(actual[3]==alpha);++pixels;
}
int main(int argc,char **argv)
{
 assert(argc==2);
 /* Make the lower atlas deliberately unrelated to canopy to catch accidental
  * use of fast.rgba rather than the independent sidecar atlas. */
 for(unsigned n=0;n<G101_ATLAS_BYTES;n+=4){lower[n]=29;lower[n+1]=173;lower[n+2]=61;lower[n+3]=255;}
 static const int64_t origins[][2]={{0,0},{37,7919},{48,8009},{-1,-1},{-1000,47},
  {96,112},{-96,-112},{INT64_MIN,INT64_MAX},{INT64_MAX,INT64_MIN}};
 G101Context world={true,false,0,0};prepare(&world);
 assert(forest13_prepare(argv[1],selected,&fast));assert(allocations==1&&callbacks==13&&!frees);
 for(unsigned o=0;o<sizeof(origins)/sizeof(*origins);o++) {
  world.world_x=origins[o][0];world.world_y=origins[o][1];prepare(&world);
  for(unsigned i=0;i<13;i++)for(unsigned n=0;n<G101_TILE_PIXELS;n++) {
   int x=(int)(n%192)+(int)((i*177)%2369);
   int y=(int)(n/192)+(int)((i*131)%1377);
   pixel(&world,i,n,x,y,255);
  }
  const int xs[]={0,1,7,8,191,192,767,768,1535,1536,2559,-1,2560,INT_MIN,INT_MAX};
  const int ys[]={0,1,7,8,223,224,895,896,1599,-1,1600,INT_MIN,INT_MAX};
  for(unsigned x=0;x<sizeof(xs)/sizeof(*xs);x++)
   for(unsigned y=0;y<sizeof(ys)/sizeof(*ys);y++)
    for(unsigned n=0;n<256;n++)pixel(&world,n%13,n,xs[x],ys[y],(uint8_t)n);
  assert(!memcmp(&snapshot,&fast,sizeof(fast)));
  assert(forest13_prepare(argv[1],selected,&fast));assert(allocations==1&&callbacks==13&&!frees);
 }
 /* Every visible pixel across both atlas axes, independent local mask phase. */
 world=(G101Context){true,false,-7,199*28+1};prepare(&world);
 for(int y=0;y<1600;y++)for(int x=0;x<2560;x++)
  pixel(&world,(unsigned)(x/192)%13,(unsigned)(y%224)*192+(unsigned)(x%192),x,y,255);
 /* Preserve world phase when scroll carries a pixel eight HD pixels down. */
 uint8_t accepted[4]={71,139,211,177},a[4],b[4];
 const Forest13Record *r=forest13_record(211);assert(r);
 for(int y=0;y<1592;y++) {
  world=(G101Context){true,false,48,199*28+1};prepare(&world);
  forest13_select(r,accepted,255,177,y,a);
  --world.world_y;prepare(&world);forest13_select(r,accepted,255,177,y+8,b);
  assert(!memcmp(a,b,4));
 }
 /* Negative/clipped tile origins keep local mask indexing and saved phase. */
 const int clipped[][2]={{-7,-9},{315,196},{-23,199},{319,-27}};
 for(unsigned o=0;o<sizeof(clipped)/sizeof(*clipped);o++) {
  world=(G101Context){true,false,48-clipped[o][0],40*28-clipped[o][1]};prepare(&world);
  for(unsigned n=0;n<G101_TILE_PIXELS;n++) {
   int x=clipped[o][0]*8+(int)(n%192),y=clipped[o][1]*8+(int)(n/192);
   if(x>=0&&x<2560&&y>=0&&y<1600)pixel(&world,0,n,x,y,255);
  }
 }
 assert(allocations==1&&callbacks==13&&!frees);
 g101_fast_invalidate(&fast);assert(!forest13_record(211));
 forest13_select(r,accepted,255,177,777,a);assert(!memcmp(a,accepted,4));
 prepare(&world);assert(forest13_record(211)==r);
 assert(!memcmp(&snapshot,&fast,sizeof(fast)));
 forest13_test_reset();assert(frees==1);
 printf("PASS synthetic forest sampler: %" PRIu64 " pixels, all13 masks, all alpha/weights, wraps/extreme origins, scroll, clipping, lower isolation; one setup allocation, zero frame allocations\n",pixels);
 return 0;
}
