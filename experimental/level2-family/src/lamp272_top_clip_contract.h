/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef LAMP272_TOP_CLIP_CONTRACT_H
#define LAMP272_TOP_CLIP_CONTRACT_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
 int body_x,body_y,x,y,part;
 unsigned first_row,stores;
} Lamp272TopClipPlan;

/* Only the known top boundary where all four native calls exist. Native
 * blit_sprite2 bounds physical addresses, not SDL's clip_rect. No side wrapping,
 * bottom clipping, fully invisible quadrant, blend or filter is modeled here. */
static bool lamp272_top_clip_plan(int x,int y,int part,Lamp272TopClipPlan *out)
{
 if(!out||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=(part==1||part==20)?12:0,py=part>=19?14:0;
 int64_t bx=(int64_t)x-px,by=(int64_t)y-py;
 if(bx<24||bx>264||by< -13||by> -1)return false;
 unsigned first=y<0?(unsigned)-y:0;
 if(first>=14)return false;
 *out=(Lamp272TopClipPlan){(int)bx,(int)by,x,y,part,first,(14-first)*12};
 return true;
}

/* Read only the exact, already pinned native source. Prove all 168 positions
 * are opaque stores in row order, including explicit palette-index zero.
 * Unknown or transparent layouts fail before any candidate RGB write. */
static bool lamp272_top_clip_source(const uint8_t *data,size_t bytes,unsigned index,uint8_t out[168])
{
 if(!data||!out||!index||index>255||(size_t)index*2>bytes)return false;
 size_t p=(size_t)data[(index-1)*2]|((size_t)data[(index-1)*2+1]<<8);
 unsigned offset=0,n=0;
 for(unsigned commands=0;commands<512;commands++){
  if(p>=bytes)return false;
  unsigned tag=data[p++];if(tag==15)return n==168;
  offset+=tag&15;unsigned count=tag>>4;
  if(!count){offset+=320-12;continue;}
  if(count>bytes-p)return false;
  while(count--){
   if(n>=168||offset!=(n/12)*320+n%12)return false;
   out[n++]=data[p++];++offset;
  }
 }
 return false;
}

static bool lamp272_top_clip_store(const Lamp272TopClipPlan *p,unsigned ordinal,
                                  unsigned x,unsigned y,int style)
{
 return p&&style==0&&ordinal<p->stores&&x==(unsigned)p->x+ordinal%12&&
        y==(unsigned)(p->y+(int)p->first_row)+ordinal/12;
}
static size_t lamp272_top_clip_rgba_offset(const Lamp272TopClipPlan *p,unsigned n,unsigned sx,unsigned sy)
{
 if(!p||n>=p->stores||sx>=8||sy>=8)return SIZE_MAX;
 unsigned ox=(p->part==1||p->part==20)?12:0,oy=p->part>=19?14:0;
 unsigned x=ox+n%12,y=oy+p->first_row+n/12;
 return ((size_t)(y*8+sy)*192+x*8+sx)*4;
}
#endif
