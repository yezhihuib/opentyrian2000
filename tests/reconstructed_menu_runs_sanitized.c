/* Fresh bounded sanitizer/lifecycle checks for reconstructed resource APIs. */
#include "common_menu_runs.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(int argc,char **argv)
{
 assert(argc==2);assert(common_menu_runs_set_directory(argv[1]));unsigned checks=0;
 for(unsigned f=0;f<COMMON_MENU_FAMILY_COUNT;f++){
  assert(common_menu_runs_load((enum CommonMenuFamily)f));
  for(unsigned id=0;id<common_menu_runs_count((enum CommonMenuFamily)f);id++){
   CommonMenuRun r;assert(common_menu_runs_get((enum CommonMenuFamily)f,id,&r));
   assert(r.alpha&&r.roles&&r.width&&r.height&&r.pitch==r.width&&r.advance256);
   assert(common_menu_runs_find((enum CommonMenuFamily)f,r.text)==(int)id);
   for(unsigned y=0;y<r.height;y++)for(unsigned x=0;x<r.width;x++){
    unsigned n=y*r.pitch+x;assert(r.alpha[n]?(r.roles[n]>=r.role_min&&r.roles[n]<=r.role_max):r.roles[n]==0);
    if(r.stroke)assert(r.stroke[n]>=r.alpha[n]);checks++;
   }
  }
 }
 assert(common_menu_numeric_runs_load());
 for(unsigned i=0;i<65536;i++){
  char text[32];CommonMenuNumericRun r;snprintf(text,sizeof(text),"Cost: %u",i);assert(common_menu_numeric_runs_layout(text,&r));
  assert(r.count&&r.count<=20&&r.width<512&&r.height<=40);
  for(unsigned y=0;y<r.height;y++)for(unsigned x=0;x<r.width;x++){
   Uint8 a,v;assert(common_menu_numeric_runs_sample(&r,r.dx+x,r.dy+y,&a,&v));assert(a?v==7:v==0);checks++;
  }
 }
 CommonMenuNumericRun r;assert(common_menu_numeric_runs_layout("-2147483648",&r));
 Uint8 a,v;r.token[0].mask=64;assert(!common_menu_numeric_runs_sample(&r,0,0,&a,&v));
 assert(common_menu_numeric_runs_layout("1",&r));r.count=21;assert(!common_menu_numeric_runs_sample(&r,0,0,&a,&v));
 for(unsigned f=0;f<6;f++){
  uint64_t old=common_menu_runs_generation((enum CommonMenuFamily)f);common_menu_runs_shutdown((enum CommonMenuFamily)f);
  CommonMenuRun v;assert(!common_menu_runs_get((enum CommonMenuFamily)f,0,&v));assert(common_menu_runs_generation((enum CommonMenuFamily)f)!=old);
  assert(common_menu_numeric_runs_ready());assert(common_menu_runs_load((enum CommonMenuFamily)f));
 }
 assert(common_menu_numeric_runs_layout("0",&r));common_menu_numeric_runs_shutdown();assert(!common_menu_numeric_runs_sample(&r,0,0,&a,&v));
 assert(common_menu_numeric_runs_load());assert(common_menu_runs_set_directory(NULL));
 for(unsigned f=0;f<6;f++)assert(!common_menu_runs_ready((enum CommonMenuFamily)f));assert(!common_menu_numeric_runs_ready());
 common_menu_runs_shutdown_all();printf("PASS %u sample checks; all65536 Uint16 costs,171 runs, lifecycle and malformed layouts\n",checks);return 0;
}
