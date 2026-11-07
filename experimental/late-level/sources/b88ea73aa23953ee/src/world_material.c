/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "world_material.h"
#include <limits.h>
#include <string.h>

void g101_begin_frame(G101Context *c) { *c=(G101Context){0}; }

bool g101_observe_row(G101Context *c,const void *map_base,size_t map_bytes,
 const void *cell,size_t cell_size,unsigned count,int x,int y)
{
 /* Integer address arithmetic avoids subtracting unrelated C pointers. We
  * never dereference the supplied map: gameplay owns it and remains untouched. */
 uintptr_t begin=(uintptr_t)map_base,p=(uintptr_t)cell;
 if(c->rejected) return false;
 if(!begin||!p||!cell_size||map_bytes/cell_size!=G101_MAP_ROWS*G101_MAP_COLS||
    map_bytes%cell_size||p<begin||p-begin>=map_bytes||
    (p-begin)%cell_size||!count||count>G101_MAP_COLS) goto reject;
 size_t index=(p-begin)/cell_size;
 unsigned row=(unsigned)(index/G101_MAP_COLS),col=(unsigned)(index%G101_MAP_COLS);
 /* A flat pointer crossing a map row is NOT a new adjacent world column. */
 if(col+count>G101_MAP_COLS) goto reject;
 int64_t ox=(int64_t)G101_TILE_W*col-x,oy=(int64_t)G101_TILE_H*row-y;
 if(c->valid&&(c->world_x!=ox||c->world_y!=oy)) goto reject;
 c->world_x=ox;c->world_y=oy;c->valid=true;return true;
reject:
 c->valid=false;c->rejected=true;return false;
}

bool g101_preflight_layer1(G101Context *c,const void *base,size_t bytes,
 const void *first,size_t stride,int x,int first_y)
{
 g101_begin_frame(c);
 if(!stride||stride>SIZE_MAX/(7*G101_MAP_COLS)||
    (uintptr_t)first>UINTPTR_MAX-7*G101_MAP_COLS*stride||first_y>INT_MAX-7*28) {
  c->rejected=true;return false;
 }
 for(unsigned row=0;row<8;row++) {
  const void *cell=(const void *)((uintptr_t)first+row*G101_MAP_COLS*stride);
  if(!g101_observe_row(c,base,bytes,cell,stride,12,x,first_y+(int)row*28))return false;
 }
 return c->valid;
}

bool g101_memory_plan(unsigned masks,unsigned clean,unsigned footers,G101MemoryPlan *p)
{
 if(!p||masks>G101_MAX_MASKS||clean>G101_MAX_MASKS||footers>2||clean>masks||footers>masks)return false;
 *p=(G101MemoryPlan){G101_ATLAS_BYTES,(size_t)masks*G101_TILE_PIXELS,
  (size_t)clean*G101_TILE_PIXELS*4,(size_t)footers*G101_TILE_PIXELS*2,
  (size_t)footers*G101_TILE_PIXELS*4,0};
 p->total_bytes=p->atlas_bytes+p->mask_bytes+p->clean_bytes+p->footer_bytes+p->generated_bytes;
 return true;
}

int g101_positive_mod(int64_t value,int period)
{
 if(period<=0) return 0;
 int remainder=(int)(value%period);
 return remainder<0?remainder+period:remainder;
}

bool g101_atlas_valid(const G101Atlas *a)
{
 return a&&a->rgba&&a->bytes==G101_ATLAS_BYTES&&a->width==G101_ATLAS_W&&
  a->height==G101_ATLAS_H&&a->density==G101_DENSITY;
}

bool g101_sample(const G101Context *c,const G101Atlas *a,int density,
 int64_t sx,int64_t sy,uint8_t out[4])
{
 if(!c||!c->valid||c->rejected||density!=G101_DENSITY||!g101_atlas_valid(a))return false;
 /* Modular reduction before addition/multiplication avoids overflow even at
  * extreme synthetic screen/world coordinates. All periods are positive. */
 int ax=(g101_positive_mod(sx,G101_ATLAS_W)+
         g101_positive_mod(c->world_x,G101_ATLAS_W)*density)%G101_ATLAS_W;
 int ay=(g101_positive_mod(sy,G101_ATLAS_H)+
         g101_positive_mod(c->world_y,G101_ATLAS_H)*density)%G101_ATLAS_H;
 memcpy(out,a->rgba+4*((size_t)ay*G101_ATLAS_W+(size_t)ax),4);return true;
}

bool g101_actor_eligible(const G101Actor *a)
{
 static const int h2[]={77,79,115,117,81,83,119,121};
 static const int he[]={1,3,5,39,41,43,7,9,11,45,47,49};
 if(!a||!a->layer1_draw||!a->verified_static_identity||a->score_item||a->independent_motion)return false;
 const int *ids=NULL;size_t count=0;
 if(a->role==101){ids=h2;count=sizeof(h2)/sizeof(*h2);}
 if(a->role==110){ids=he;count=sizeof(he)/sizeof(*he);}
 for(size_t i=0;i<count;i++)if(ids[i]==a->base)return true;
 return false;
}

bool g101_full_actor_origin(int x,int y,int part,int *fx,int *fy)
{
 if(part!=0&&part!=1&&part!=19&&part!=20)return false;
 int px=(part==1||part==20)?12:0,py=(part==19||part==20)?14:0;
 if(x<INT_MIN+px||y<INT_MIN+py)return false;
 *fx=x-px;*fy=y-py;return true;
}

static uint8_t mix(uint8_t base,uint8_t ground,uint8_t weight)
{ return (uint8_t)(((unsigned)base*(255-weight)+(unsigned)ground*weight+127)/255); }

void g101_compose_layers(const uint8_t clean[4],const uint8_t material[4],
 uint8_t weight,uint8_t footer,uint8_t out[4])
{
 for(int c=0;c<3;c++)out[c]=mix(mix(clean[c],material[c],weight),material[c],footer);
 out[3]=clean[3];
}

void g101_compose_footer(const uint8_t clean[4],const uint8_t material[4],
 const uint8_t generated[4],uint8_t primary,uint8_t gen,uint8_t ground,uint8_t out[4])
{
 for(int c=0;c<3;c++) {
  uint8_t first=mix(clean[c],material[c],primary);
  uint8_t second=gen?mix(first,generated[c],gen):first;
  out[c]=mix(second,material[c],ground);
 }
 out[3]=clean[3];
}

bool g101_select_pixel(const G101Context *ctx,const G101Atlas *atlas,
 const G101Pixel *p,bool eligible,int density,int64_t sx,int64_t sy,uint8_t out[4])
{
 memcpy(out,p->accepted_rgba,4);
 if(!eligible||!p->accepted_rgba[3]||(!p->primary_weight&&!p->footer_weight&&!p->generated_weight)||
    !p->clean_rgba||!p->reconstruction_verified||(p->generated_weight&&!p->generated_footer_rgba))return false;
 uint8_t material[4],composed[4];
 if(!g101_sample(ctx,atlas,density,sx,sy,material))return false;
 g101_compose_footer(p->clean_rgba,material,p->generated_footer_rgba,
  p->primary_weight,p->generated_weight,p->footer_weight,composed);
 memcpy(out,composed,3); /* Alpha is ALWAYS the immutable accepted asset alpha. */
 return true;
}

bool g101_select_cap_pixel(const G101Context *ctx,const G101Atlas *atlas,
 const uint8_t accepted[4],uint8_t weight,int density,int64_t sx,int64_t sy,uint8_t out[4])
{
 memcpy(out,accepted,4);
 if(!weight||!accepted[3])return false;
 uint8_t material[4];
 if(!g101_sample(ctx,atlas,density,sx,sy,material))return false;
 for(int c=0;c<3;c++)out[c]=mix(accepted[c],material[c],weight);
 return true;
}
