/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef LAMP272_BOTTOM_CLIP_CONTRACT_H
#define LAMP272_BOTTOM_CLIP_CONTRACT_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct { int body_x,body_y,x,y,part; unsigned stores; } Lamp272BottomClipPlan;
/* Only body y157..174, x24..264. Physical native stores reach row199;
 * the later compositor publishes only rows0..183. All four quadrants have
 * at least twelve stored rows. At body_y >=175 the production scheduler
 * stops issuing parts19/20 (enemy.ey >=182), so reject before any quartet.
 * No side wrap or invisible quadrant allowed. */
static bool lamp272_bottom_clip_plan(int x,int y,int part,Lamp272BottomClipPlan *out)
{
 if(!out||(part!=0&&part!=1&&part!=19&&part!=20))return false;
 int px=(part==1||part==20)?12:0,py=part>=19?14:0;
 int64_t bx=(int64_t)x-px,by=(int64_t)y-py;
 if(bx<24||bx>264||by<157||by>174)return false;
 unsigned rows=y>186?(unsigned)(200-y):14;
 *out=(Lamp272BottomClipPlan){(int)bx,(int)by,x,y,part,rows*12};
 return true;
}
static bool lamp272_bottom_clip_store(const Lamp272BottomClipPlan *p,unsigned n,unsigned x,unsigned y,int style)
{return p&&style==0&&n<p->stores&&x==(unsigned)p->x+n%12&&y==(unsigned)p->y+n/12;}
static size_t lamp272_bottom_clip_rgba_offset(const Lamp272BottomClipPlan *p,unsigned n,unsigned sx,unsigned sy)
{
 if(!p||n>=p->stores||sx>=8||sy>=8)return SIZE_MAX;
 unsigned ox=(p->part==1||p->part==20)?12:0,oy=p->part>=19?14:0;
 return ((size_t)((oy+n/12)*8+sy)*192+(ox+n%12)*8+sx)*4;
}
#endif
