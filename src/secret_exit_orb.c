/* SPDX-License-Identifier: GPL-2.0-or-later
 * Secret-route collectible: one curved gold globe, three luminance levels.
 * No bitmap, source-pixel contour tracing, new clock, random state or halo.
 */
#include "secret_exit_orb.h"
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
enum { DENSITY=8,WIDTH=24,HEIGHT=28 };
static uint8_t pixels[3][WIDTH*HEIGHT*DENSITY*DENSITY*4];
static uint32_t saved_palette[17];
static bool ready;

int secret_exit_orb_phase(unsigned base)
{return base==85?0:base==131?1:base==233?2:-1;}

static double smoothstep(double lo,double hi,double v)
{
 double t=(v-lo)/(hi-lo);if(t<0)t=0;else if(t>1)t=1;
 return t*t*(3-2*t);
}

uint8_t *secret_exit_orb_rgba(unsigned base,const uint32_t palette[256])
{
 int phase=secret_exit_orb_phase(base);if(phase<0||!palette)return NULL;
 if(ready&&saved_palette[0]==palette[1]&&!memcmp(saved_palette+1,palette+0x70,16*sizeof(uint32_t)))return pixels[phase];
 saved_palette[0]=palette[1];memcpy(saved_palette+1,palette+0x70,16*sizeof(uint32_t));ready=true;
 for(int y=0;y<HEIGHT*DENSITY;y++)for(int x=0;x<WIDTH*DENSITY;x++) {
  double px=(x+.5)/DENSITY,py=(y+.5)/DENSITY;
  double dx=px-11.5,dy=py-14.5,r=hypot(dx,dy);
  double alpha=1-smoothstep(10.25,10.60,r);
  /* The dark perimeter and every curve remain identical across the pulse.
   * A broad upper-left core and two lower-right swept arcs identify the
   * original collectible, distinct from a projectile or a soft effect ball. */
  double core=exp(-((px-8.1)*(px-8.1)/21+(py-10.7)*(py-10.7)/14.5));
  double ar=hypot((px-10.5)/1.04,py-12.8),angle=atan2(py-12.8,px-10.5);
  double sector=smoothstep(-.05,.30,angle)*(1-smoothstep(1.55,1.95,angle));
  double arc=exp(-pow((ar-8.1)/.88,2))*sector;
  double inner=exp(-pow((ar-6.1)/.78,2))*sector;
  double light=1-smoothstep(1,10.1,hypot((px-8)/1.1,py-10.5));
  double theta=atan2(dy,dx);
  double curl=exp(-pow((r-(6.0+.7*sin(theta+1.6)))/.58,2));
  curl*=.5+.5*cos(theta+1.3);
  double shade=3.4+2.4*light+10.5*core+6.6*arc+2.0*inner+1.5*curl;
  double body=1-smoothstep(9.85,10.35,r);
  for(int f=0;f<3;f++) {
   static const double pulse[3]={0,2,5};
   double value=shade+pulse[f];if(value>15)value=15;
   unsigned lo=(unsigned)value,hi=lo<15?lo+1:lo;
   unsigned fraction=(unsigned)((value-lo)*256);
   uint8_t *p=pixels[f]+4*(y*WIDTH*DENSITY+x);
   p[3]=(uint8_t)(255*alpha+.5);
   for(int c=0;c<3;c++) {
    unsigned shift=(2-c)*8;
    double warm=(((palette[0x70+lo]>>shift)&255)*(256-fraction)+((palette[0x70+hi]>>shift)&255)*fraction)/256.0;
    p[c]=p[3]?(uint8_t)(warm*body+((palette[1]>>shift)&255)*(1-body)+.5):0;
   }
  }
 }
 return pixels[phase];
}
