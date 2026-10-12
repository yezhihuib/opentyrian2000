/* Isolated production-loader checks; no SDL, game, captures, or source edits. */
#include "forest13_material.h"
#include "forest13_bundle_index.h"
#include <assert.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned allocations,frees,callback_count,mismatch_id,source_mode;
static size_t allocation_bytes;
static bool fail_allocation,read_error;
static G101FastContext fast;
static uint8_t lower[G101_ATLAS_BYTES],source[G101_TILE_PIXELS*4];
static const char *source_directory;
void *forest13_test_malloc(size_t n)
{++allocations;allocation_bytes+=n;return fail_allocation?NULL:malloc(n);}
void forest13_test_free(void *p)
{if(p)++frees;free(p);}
size_t forest13_test_fread(void *p,size_t size,size_t n,FILE *f)
{
 size_t got=fread(p,size,n,f);
 if((source_mode==4&&n==30)||(source_mode==5&&n==188)||
    (source_mode==6&&n==FOREST13_BUNDLE_PAYLOAD_BYTES)) {
  read_error=true;
  if(source_mode!=4&&got)--got;
 }
 return got;
}
int forest13_test_ferror(FILE *f){return read_error||ferror(f);}
uint64_t game_probe_hash(uint64_t h,const void *data,size_t bytes)
{const uint8_t *p=data;while(bytes--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
const G101FastContext *ground101_fast_context(void)
{return fast.valid?&fast:NULL;}
static uint32_t u32(const uint8_t *p)
{return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;}
static const uint8_t *selected(unsigned id,unsigned slot,void *context)
{
 assert(context==&fast);++callback_count;
 assert(slot>=336&&slot<=348&&forest13_records[slot-336].index==id);
 if(id==mismatch_id&&source_mode==1)return NULL;
 char path[4096];int n=snprintf(path,sizeof(path),"%s/terrain-shapesz-%u-8.hda",source_directory,id);
 assert(n>0&&(size_t)n<sizeof(path));FILE *f=fopen(path,"rb");if(!f)return NULL;
 uint8_t h[28];bool ok=fread(h,1,sizeof(h),f)==sizeof(h)&&!memcmp(h,"HDR1",4)&&
  u32(h+4)==2010000+id&&u32(h+8)==8&&u32(h+12)==24&&u32(h+16)==28&&
  u32(h+20)==0&&u32(h+24)==0;
 if(ok)ok=fread(source,1,sizeof(source),f)==sizeof(source)&&fgetc(f)==EOF&&!ferror(f);
 fclose(f);if(!ok)return NULL;
 if(id==mismatch_id&&source_mode==2)source[0]^=1;
 if(id==mismatch_id&&source_mode==3)source[3]=254;
 return source;
}
static void context_prepare(void)
{
 G101Context world={true,false,35,577};
 G101Atlas a={lower,sizeof(lower),768,896,8};
 assert(g101_fast_prepare(&fast,&world,&a,8));
}
static void layout(void)
{
 Forest13Record r[13];memcpy(r,forest13_records,sizeof(r));
 assert(forest13_test_layout(r,13,3311616));
 assert(!forest13_test_layout(NULL,13,3311616));
 assert(!forest13_test_layout(r,0,3311616));assert(!forest13_test_layout(r,12,3311616));
 assert(!forest13_test_layout(r,14,3311616));assert(!forest13_test_layout(r,SIZE_MAX,3311616));
 assert(!forest13_test_layout(r,13,3311615));assert(!forest13_test_layout(r,13,3311617));
 assert(!forest13_test_layout(r,13,SIZE_MAX));
 for(unsigned i=0;i<13;i++) {
  memcpy(r,forest13_records,sizeof(r));r[i].index++;assert(!forest13_test_layout(r,13,3311616));
  memcpy(r,forest13_records,sizeof(r));r[i].slot++;assert(!forest13_test_layout(r,13,3311616));
  memcpy(r,forest13_records,sizeof(r));r[i].mask_offset++;assert(!forest13_test_layout(r,13,3311616));
  r[i].mask_offset=UINT_MAX;assert(!forest13_test_layout(r,13,3311616));
 }
 memcpy(r,forest13_records,sizeof(r));r[1]=r[0];assert(!forest13_test_layout(r,13,3311616));
}
static void payload_checks(void)
{
 uint8_t *p=calloc(1,FOREST13_BUNDLE_PAYLOAD_BYTES);assert(p);
 for(unsigned i=3;i<G101_ATLAS_BYTES;i+=4)p[i]=255;
 assert(forest13_test_payload(p,FOREST13_BUNDLE_PAYLOAD_BYTES));
 assert(!forest13_test_payload(NULL,FOREST13_BUNDLE_PAYLOAD_BYTES));
 assert(!forest13_test_payload(p,0));assert(!forest13_test_payload(p,FOREST13_BUNDLE_PAYLOAD_BYTES-1));
 assert(!forest13_test_payload(p,SIZE_MAX));
 for(unsigned i=3;i<G101_ATLAS_BYTES;i+=G101_ATLAS_BYTES-4) {
  p[i]=254;assert(!forest13_test_payload(p,FOREST13_BUNDLE_PAYLOAD_BYTES));p[i]=255;
 }
 free(p);
}
int main(int argc,char **argv)
{
 assert(argc==11);const char *directory=argv[1];source_directory=argv[2];
 bool declared=atoi(argv[3])!=0,policy=atoi(argv[4])!=0,want=atoi(argv[5])!=0;
 unsigned expected_allocations=(unsigned)atoi(argv[6]);mismatch_id=(unsigned)atoi(argv[7]);
 source_mode=(unsigned)atoi(argv[8]);bool lower_valid=atoi(argv[9])!=0;fail_allocation=atoi(argv[10])!=0;
 for(unsigned n=3;n<sizeof(lower);n+=4)lower[n]=255;
 layout();payload_checks();
 assert(!forest13_policy_check(NULL)&&!forest13_declared());forest13_test_reset();
 /* Even before lower exists, declaration state must be known and no payload
  * attempt consumed. An unrelated lower failure never mutates that context. */
 assert(!forest13_prepare(directory,selected,&fast));assert(!allocations&&!callback_count);
 assert(forest13_declared()==declared);assert(forest13_policy_check(directory)==policy);
 assert(!forest13_record(211));
 if(lower_valid)context_prepare();
 G101FastContext before=fast;
 assert(forest13_prepare(directory,selected,&fast)==want);
 assert(!memcmp(&fast,&before,sizeof(fast)));
 assert(allocations==expected_allocations);
 assert(allocation_bytes==expected_allocations*FOREST13_BUNDLE_PAYLOAD_BYTES);
 unsigned saved_calls=callback_count,saved_frees=frees;
 assert(forest13_prepare(directory,selected,&fast)==want);
 assert(allocations==expected_allocations&&callback_count==saved_calls&&frees==saved_frees);
 if(want)assert(callback_count==13&&frees==0);
 else if(expected_allocations&&!fail_allocation)assert(frees==1);
 for(unsigned i=0;i<13;i++) {
  const Forest13Record *r=forest13_record(forest13_records[i].index);
  assert((r!=NULL)==want);
  if(r)assert(r->index==forest13_records[i].index&&r->slot==forest13_records[i].slot&&
   r->mask_offset==forest13_records[i].mask_offset&&r->source_fnv64==forest13_records[i].source_fnv64);
 }
 assert(!forest13_record(0)&&!forest13_record(210)&&!forest13_record(214)&&!forest13_record(UINT_MAX));
 uint8_t accepted[4]={37,128,253,183},out[4];
 const Forest13Record *saved=forest13_record(211);
 Forest13Record forged={211,336,UINT_MAX,0};
 forest13_select(&forged,accepted,0,0,0,out);assert(!memcmp(out,accepted,4));
 forged.slot=UINT_MAX;forest13_select(&forged,accepted,0,0,0,out);assert(!memcmp(out,accepted,4));
 forest13_select(NULL,accepted,0,0,0,out);assert(!memcmp(out,accepted,4));
 forest13_select(saved,accepted,G101_TILE_PIXELS,0,0,out);assert(!memcmp(out,accepted,4));
 forest13_select(saved,accepted,UINT_MAX,0,0,out);assert(!memcmp(out,accepted,4));
 const int bad[][2]={{-1,0},{0,-1},{2560,0},{0,1600},{INT_MIN,INT_MAX}};
 for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++) {
  forest13_select(saved,accepted,0,bad[i][0],bad[i][1],out);assert(!memcmp(out,accepted,4));
 }
 g101_fast_invalidate(&fast);assert(!forest13_record(211));
 forest13_select(saved,accepted,0,0,0,out);assert(!memcmp(out,accepted,4));
 assert(!forest13_prepare(directory,selected,&fast));
 if(lower_valid) {
  context_prepare();assert((forest13_record(211)!=NULL)==want);
  assert(forest13_prepare(directory,selected,&fast)==want);
 }
 assert(allocations==expected_allocations&&callback_count==saved_calls);
 forest13_test_reset();assert(!forest13_declared()&&!forest13_record(211));
 printf("PASS declared=%u policy=%u ready=%u allocations=%u callbacks=%u\n",declared,policy,want,allocations,callback_count);
 return 0;
}
