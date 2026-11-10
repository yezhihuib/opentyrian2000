/* Pure finite Pulse5 draw transaction. No source/admission permission is granted
 * here: the host must bind actual birth/slot/draw/source/asset/underlay witnesses.
 * Native stores remain external and authoritative. No SDL or game state writes. */
#ifndef FAMILY_PULSE_TRANSACTION_H
#define FAMILY_PULSE_TRANSACTION_H
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
enum { FPT_WIDTH=12,FPT_HEIGHT=14,FPT_CELLS=168,FPT_DENSITY=8,
       FPT_PIXELS=10752,FPT_NORMAL=0,FPT_SHADOW=2 };
typedef struct {
 bool active,valid,complete;
 int x,y,style;
 unsigned next,count;
 uint16_t order[FPT_CELLS];
 uint8_t before[FPT_CELLS],after[FPT_CELLS],owned[FPT_CELLS];
 uint32_t rgba[FPT_PIXELS];
} FamilyPulseTransaction;
static inline uint32_t fpt_blend(uint32_t lower,const uint8_t *color,unsigned alpha)
{
 uint32_t out=UINT32_C(0xff000000);
 for(unsigned c=0;c<3;c++){
  unsigned shift=(2-c)*8;
  out|=((((lower>>shift)&255)*(255-alpha)+color[c]*alpha+127)/255)<<shift;
 }
 return out;
}
static inline void fpt_fail(FamilyPulseTransaction *t)
{t->valid=t->active=t->complete=false;memset(t->owned,0,sizeof t->owned);}
/* RGB buffers are glyph-local row-major 96x112. Native arrays are row-major
 * 12x14. foreign[] distinguishes already-authored RGB underlay from native
 * palette expansion for the established shadow analogue, independently for
 * each subpixel. The caller supplies a separately validated underlay per route;
 * accepted-family RGB must never be reused on the independent fallback route. */
static inline bool fpt_begin(FamilyPulseTransaction *t,int x,int y,int style,
 const uint8_t source[FPT_CELLS],const uint8_t opaque[FPT_CELLS],
 const uint8_t before[FPT_CELLS],const uint8_t artwork[FPT_PIXELS*4],
 const uint32_t underlay[FPT_PIXELS],const uint8_t foreign[FPT_PIXELS],
 const uint32_t palette[256])
{
 if(!t)return false;
 memset(t,0,sizeof *t);
 if(!source||!opaque||!before||!artwork||!underlay||!foreign||!palette||
  x<0||x>308||y<-13||y>=200||(style!=FPT_NORMAL&&style!=FPT_SHADOW))return false;
 t->x=x;t->y=y;t->style=style;
 memcpy(t->before,before,FPT_CELLS);memcpy(t->after,before,FPT_CELLS);
 for(unsigned cy=0;cy<FPT_HEIGHT;cy++)for(unsigned cx=0;cx<FPT_WIDTH;cx++){
  unsigned cell=cy*FPT_WIDTH+cx;
  if(opaque[cell]!=0&&opaque[cell]!=255){fpt_fail(t);return false;}
  if(y+(int)cy<0||y+(int)cy>=200)continue;
  if(opaque[cell]){
   t->order[t->count++]=(uint16_t)cell;t->owned[cell]=1;
   t->after[cell]=style==FPT_NORMAL?source[cell]:(uint8_t)((before[cell]&240)|((before[cell]&15)/2));
  }
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   unsigned pixel=(cy*8+sy)*96+cx*8+sx;
   const uint8_t *a=artwork+pixel*4;t->rgba[pixel]=underlay[pixel];
   if(!a[3])continue;
   t->owned[cell]=1;
   if(style==FPT_NORMAL)t->rgba[pixel]=fpt_blend(underlay[pixel],a,a[3]);
   else {
    uint32_t dark=UINT32_C(0xff000000);
    if(foreign[pixel]){
     for(unsigned shift=0;shift<24;shift+=8)dark|=((((underlay[pixel]>>shift)&255)*255+255)/510)<<shift;
    }else dark|=palette[(before[cell]&240)|((before[cell]&15)/2)]&UINT32_C(0xffffff);
    uint8_t rgb[3]={(uint8_t)(dark>>16),(uint8_t)(dark>>8),(uint8_t)dark};
    t->rgba[pixel]=fpt_blend(underlay[pixel],rgb,a[3]);
   }
  }
 }
 t->active=t->valid=true;return true;
}
static inline bool fpt_store(FamilyPulseTransaction *t,int x,int y,int style,uint8_t before,uint8_t after)
{
 if(!t||!t->valid||!t->active)return false;
 if(t->next>=t->count){fpt_fail(t);return false;}
 unsigned cell=t->order[t->next];
 if(x!=t->x+(int)(cell%12)||y!=t->y+(int)(cell/12)||style!=t->style||
    before!=t->before[cell]||after!=t->after[cell]){fpt_fail(t);return false;}
 t->next++;return true;
}
static inline bool fpt_end(FamilyPulseTransaction *t,const uint8_t final_indices[FPT_CELLS])
{
 if(!t||!t->active||!t->valid)return false;
 if(!final_indices||t->next!=t->count){fpt_fail(t);return false;}
 for(unsigned cell=0;cell<FPT_CELLS;cell++){
  int y=t->y+(int)(cell/12);
  if(y>=0&&y<200&&final_indices[cell]!=t->after[cell]){fpt_fail(t);return false;}
 }
 t->active=false;t->complete=true;return true;
}
/* Later native writes retire even same-index cells. A host must additionally
 * retire on overlapping later authored support, and revoke copied underlays
 * when any captured family dependency is invalidated. */
static inline void fpt_retire(FamilyPulseTransaction *t,int x,int y)
{
 if(!t||!t->valid)return;
 int dx=x-t->x,dy=y-t->y;
 if(dx>=0&&dx<12&&dy>=0&&dy<14)t->owned[dy*12+dx]=0;
}
static inline const uint32_t *fpt_sample(const FamilyPulseTransaction *t,int x,int y,unsigned sx,unsigned sy)
{
 if(!t||!t->valid||!t->complete||sx>=8||sy>=8)return NULL;
 int dx=x-t->x,dy=y-t->y;
 if(dx<0||dx>=12||dy<0||dy>=14||!t->owned[dy*12+dx])return NULL;
 return t->rgba+((unsigned)dy*8+sy)*96+(unsigned)dx*8+sx;
}
#endif
