/* SPDX-License-Identifier: GPL-2.0-or-later
 * Small vector lettering for the original diagonal DATA collection label.
 * D@(0,1), A@(3,3), T@(6,6), A@(9,8); no sprite-derived pixel tracing.
 */
#include "data_pickup_glyph.h"
#include <math.h>
#include <string.h>

enum { DENSITY=8, WIDTH=12, HEIGHT=14 };
static uint8_t pixels[WIDTH*HEIGHT*DENSITY*DENSITY*4];
static uint32_t saved_palette[16];
static bool ready;

bool data_pickup_glyph_eligible(bool fixed, bool following, int delta_y,
                              unsigned sprite, unsigned ttl)
{
 return fixed&&!following&&delta_y==0&&sprite==265&&ttl>=1&&ttl<=14;
}

static double segment_distance(double x,double y,double ax,double ay,double bx,double by)
{
 double vx=bx-ax,vy=by-ay,t=((x-ax)*vx+(y-ay)*vy)/(vx*vx+vy*vy);
 if(t<0)t=0;else if(t>1)t=1;
 return hypot(x-ax-t*vx,y-ay-t*vy);
}

static double glyph_distance(int letter,double x,double y)
{
 double d=10;
 if(letter==0) {
  /* Flat stem and a smoothly rounded D bowl, sampled from its analytic arc. */
  d=segment_distance(x,y,.55,.55,.55,4.45);
  double px=.55,py=.55;
  for(int i=0;i<=12;i++) {
   double angle=-1.5707963267948966+i*3.141592653589793/12;
   double nx=.85+1.55*cos(angle),ny=2.5+1.95*sin(angle);
   double q=segment_distance(x,y,px,py,nx,ny);if(q<d)d=q;
   px=nx;py=ny;
  }
  double q=segment_distance(x,y,px,py,.55,4.45);if(q<d)d=q;
 } else if(letter==2) {
  d=segment_distance(x,y,.45,.55,2.55,.55);
  double q=segment_distance(x,y,1.5,.55,1.5,4.45);if(q<d)d=q;
 } else {
  d=segment_distance(x,y,.5,4.45,1.5,.55);
  double q=segment_distance(x,y,1.5,.55,2.5,4.45);if(q<d)d=q;
  q=segment_distance(x,y,.9,2.95,2.1,2.95);if(q<d)d=q;
 }
 return d;
}

uint8_t *data_pickup_glyph_rgba(const uint32_t palette[256])
{
 if(ready&&!memcmp(saved_palette,palette+0x70,sizeof(saved_palette)))return pixels;
 memcpy(saved_palette,palette+0x70,sizeof(saved_palette));ready=true;
 static const int origin[4][2]={{0,1},{3,3},{6,6},{9,8}};
 /* Four area samples per 8x texel give a steady thin edge at native 640x400.
  * The narrow dark rim and gold interior remain separate, without a glow. */
 for(int y=0;y<HEIGHT*DENSITY;y++)for(int x=0;x<WIDTH*DENSITY;x++) {
  unsigned accum[4]={0};
  for(int sy=0;sy<2;sy++)for(int sx=0;sx<2;sx++) {
   double px=(x+(sx+.5)/2)/DENSITY,py=(y+(sy+.5)/2)/DENSITY;
   double distance=10,local_y=0;
   for(int letter=0;letter<4;letter++) {
    double q=glyph_distance(letter,px-origin[letter][0],py-origin[letter][1]);
    if(q<distance){distance=q;local_y=py-origin[letter][1];}
   }
   if(distance>.64)continue;
   double shade=distance>.34?0:4.7+local_y*1.55;
   if(shade>13)shade=13;
   unsigned lo=(unsigned)shade,hi=lo<15?lo+1:lo;
   unsigned fraction=(unsigned)((shade-lo)*256);
   for(int c=0;c<3;c++) {
    unsigned shift=(2-c)*8;
    accum[c]+=(((palette[0x70+lo]>>shift)&255)*(256-fraction)+
               ((palette[0x70+hi]>>shift)&255)*fraction+128)/256;
   }
   accum[3]++;
  }
  uint8_t *p=pixels+4*(y*WIDTH*DENSITY+x);
  for(int c=0;c<3;c++)p[c]=accum[3]?(uint8_t)((accum[c]+accum[3]/2)/accum[3]):0;
  p[3]=(uint8_t)((accum[3]*255+2)/4);
 }
 return pixels;
}
