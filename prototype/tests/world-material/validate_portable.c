#include "ground101_material.h"
#include "ground101_bundle_index.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static void *map[300][14];
static unsigned allocations;
static size_t allocation_bytes;
void *__real_malloc(size_t);
void *__wrap_malloc(size_t n){++allocations;allocation_bytes+=n;return __real_malloc(n);}
static void test_layout(void)
{
 G101Record records[61],copy[61];
 memcpy(records,g101_records,sizeof(records));
 assert(ground101_test_layout(records,61,16386048));
 assert(!ground101_test_layout(records,60,16386048));assert(!ground101_test_layout(records,62,16386048));
 assert(!ground101_test_layout(records,61,16386047));assert(!ground101_test_layout(records,61,SIZE_MAX));
 memcpy(copy,records,sizeof(copy));copy[0].base_offset++;assert(!ground101_test_layout(copy,61,16386048));
 memcpy(copy,records,sizeof(copy));copy[0].base_offset=UINT32_MAX;assert(!ground101_test_layout(copy,61,16386048));
 memcpy(copy,records,sizeof(copy));copy[0].mask_offset=16386048;assert(!ground101_test_layout(copy,61,16386048));
 memcpy(copy,records,sizeof(copy));copy[1].role=copy[0].role;copy[1].index=copy[0].index;assert(!ground101_test_layout(copy,61,16386048));
 memcpy(copy,records,sizeof(copy));copy[1].slot=copy[0].slot;assert(!ground101_test_layout(copy,61,16386048));
 memcpy(copy,records,sizeof(copy));copy[0].slot=330;assert(!ground101_test_layout(copy,61,16386048));
 memcpy(copy,records,sizeof(copy));copy[0].role=999;assert(!ground101_test_layout(copy,61,16386048));
 memcpy(copy,records,sizeof(copy));copy[0].generated_offset=1;assert(!ground101_test_layout(copy,61,16386048));
 for(unsigned i=0;i<61;i++)if(records[i].generated_offset){memcpy(copy,records,sizeof(copy));copy[i].ground_weight_offset=UINT32_MAX;assert(!ground101_test_layout(copy,61,16386048));}
}
static void put32(uint8_t *p,uint32_t v)
{for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(i*8));}
static void synthetic_bundle(const char *path)
{
 uint8_t h[G101_BUNDLE_HEADER_BYTES]={0},zero[4096]={0};
 memcpy(h,"G101AT1\0",8);put32(h+8,1);put32(h+12,61);put32(h+16,768);put32(h+20,896);put32(h+24,8);put32(h+28,G101_BUNDLE_PAYLOAD_BYTES);
 for(unsigned i=0;i<61;i++){put32(h+32+12*i,g101_records[i].role);put32(h+36+12*i,g101_records[i].index);put32(h+40+12*i,g101_records[i].generated_offset!=0);}
 FILE *f=fopen(path,"wb");assert(f);assert(fwrite(h,1,sizeof(h),f)==sizeof(h));
 size_t left=G101_BUNDLE_PAYLOAD_BYTES;while(left){size_t n=left<sizeof(zero)?left:sizeof(zero);assert(fwrite(zero,1,n,f)==n);left-=n;}assert(!fclose(f));
}
int main(int argc,char **argv)
{
 test_layout();assert(!allocations);
 if(argc==3&&!strcmp(argv[1],"--synthetic-bundle")){synthetic_bundle(argv[2]);return 0;}
 assert(argc==4);bool expected=atoi(argv[2])!=0;
 assert(ground101_bundle_load(argv[1])==expected);assert(ground101_bundle_load(argv[1])==expected);
 assert(allocations==(unsigned)atoi(argv[3])&&allocations<=1&&allocation_bytes<=16386048);
 printf("allocations=%u bytes=%zu\n",allocations,allocation_bytes);
 if(!expected){assert(ground101_record(201,101)==NULL);assert(ground101_record_at(0)==NULL);assert(ground101_base(NULL)==NULL);assert(!ground101_layer1_preflight(map,sizeof(map),&map[20][2],sizeof(void *),13,-17));G101EnemyContext e={123,25,0,1,false,false,false,true};assert(!ground101_enemy_eligible(&e,101,77));puts("PASS disabled bundle, no records/context/eligible actors; selected pack untouched");return 0;}
 assert(ground101_layer1_preflight(map,sizeof(map),&map[20][2],sizeof(void *),13,-17));
 unsigned states=0;
 for(unsigned type=121;type<=527;type++)for(unsigned role=101;role<=110;role+=9)for(unsigned base=1;base<=121;base++) {
  G101EnemyContext e={type,25,0,1,false,false,false,true};
  if(ground101_enemy_eligible(&e,role,base)) {
   states++;e.pool_slot=0;assert(!ground101_enemy_eligible(&e,role,base));e.pool_slot=25;
   e.score_item=true;assert(!ground101_enemy_eligible(&e,role,base));e.score_item=false;
   e.independent_motion=true;assert(!ground101_enemy_eligible(&e,role,base));e.independent_motion=false;
   e.static_animation=false;assert(!ground101_enemy_eligible(&e,role,base));e.static_animation=true;
   e.size=0;assert(!ground101_enemy_eligible(&e,role,base));e.size=1;
   e.availability=2;assert(!ground101_enemy_eligible(&e,role,base));
  }
  e=(G101EnemyContext){type,75,2,1,false,true,false,true};
  if(ground101_enemy_eligible(&e,role,base)) {
   states++;assert(type>=522&&type<=527&&role==110);e.damaged=false;assert(!ground101_enemy_eligible(&e,role,base));
  }
 }
 assert(allocations==1&&allocation_bytes==16386048);
 assert(states==26);assert(ground101_record(201,111)==NULL);assert(ground101_record(201,47)==NULL);
 for(unsigned n=0;n<61;n++)assert(ground101_record_at(n));
 assert(!ground101_record_at(61));
 assert(ground101_layer1_row(&map[21][2],13,11)==1);
 assert(ground101_layer1_row(&map[22][2],13,40)==-1);
 G101EnemyContext e={123,25,0,1,false,false,false,true};assert(!ground101_enemy_eligible(&e,101,77));
 ground101_frame_reset();assert(!ground101_enemy_eligible(&e,101,77));
 assert(!ground101_layer1_preflight(map,sizeof(map),&map[299][2],sizeof(void *),13,-17));
 puts("PASS structural spans/counts/duplicates/overflow/footer guards, bounded single allocation, 26 actor states, bad-row/frame reset");return 0;
}
