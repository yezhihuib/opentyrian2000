/* SPDX-License-Identifier: GPL-2.0-or-later
 * A small horizontal orange ember for the original stationary pickup flash.
 * Analytic soft contour and warm core; no sprite tracing, animation or RNG.
 */
#include "fixed_pickup_flash.h"
#include <math.h>
#include <string.h>

enum { DENSITY=8, WIDTH=12, HEIGHT=14 };
static uint8_t pixels[WIDTH*HEIGHT*DENSITY*DENSITY*4];
static uint32_t saved_palette[16];
static bool ready;

bool fixed_pickup_flash_eligible(bool fixed, bool following, int delta_y,
                                 unsigned sprite, unsigned ttl)
{
 return fixed&&!following&&delta_y==0&&sprite==144&&ttl>=1&&ttl<=7;
}

static double smoothstep(double lo,double hi,double x)
{
 double t=(x-lo)/(hi-lo);if(t<0)t=0;else if(t>1)t=1;
 return t*t*(3-2*t);
}

uint8_t *fixed_pickup_flash_rgba(const uint32_t palette[256])
{
 if(ready&&!memcmp(saved_palette,palette+0x70,sizeof(saved_palette)))return pixels;
 memcpy(saved_palette,palette+0x70,sizeof(saved_palette));ready=true;
 for(int y=0;y<HEIGHT*DENSITY;y++)for(int x=0;x<WIDTH*DENSITY;x++) {
  double dx=(x+.5)/DENSITY-6,dy=(y+.5)/DENSITY-7.5;
  /* Slightly irregular tapered ends avoid a hard circular disk. The core
   * stays orange (at most 0x7b), unlike the brighter moving flash146. */
  double radius=hypot(dx/3,dy/2.3);
  radius*=1+.055*sin(2.6*dx+.8*dy);
  double alpha=1-smoothstep(.70,1,radius);
  uint8_t *p=pixels+4*(y*WIDTH*DENSITY+x);
  p[3]=(uint8_t)(255*alpha+.5);
  if(!p[3]){p[0]=p[1]=p[2]=0;continue;}
  double shade=1+10*exp(-((dx+.15)*(dx+.15)/2.2+(dy+.1)*(dy+.1)/.55));
  unsigned lo=(unsigned)shade,hi=lo<11?lo+1:lo;
  unsigned fraction=(unsigned)((shade-lo)*256);
  for(int c=0;c<3;c++) {
   unsigned shift=(2-c)*8;
   p[c]=(uint8_t)((((palette[0x70+lo]>>shift)&255)*(256-fraction)+
                   ((palette[0x70+hi]>>shift)&255)*fraction+128)/256);
  }
 }
 return pixels;
}
