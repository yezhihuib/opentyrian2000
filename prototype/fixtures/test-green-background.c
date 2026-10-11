#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef uint8_t Uint8; typedef uint16_t Uint16; typedef uint32_t Uint32;
#define MAX(a,b) ((a)>(b)?(a):(b))
typedef struct {int w,h,pitch;void *pixels;} Surface;
static int game_probe_density; static Surface *canvas; static Uint8 *hd_owner,*green_under_owner; static Uint16 *green_first; static Uint32 *green_under;
#include "green-background-under-test.inc"

int main(void) {
 int xs[]={-13,-12,-11,-1,0,1,307,308,319,320,321};
 int ys[]={-15,-14,-13,-1,0,1,185,186,199,200,201};
 unsigned long checks=0;
 for(int d=4;d<=8;d*=2) {
  game_probe_density=d;
  Surface c={320*d,200*d,320*d*4,NULL};canvas=&c;
  size_t n=(size_t)c.w*c.h;Uint32 *orig=malloc(n*4);c.pixels=malloc(n*4);hd_owner=malloc(n);green_first=calloc(n,sizeof(*green_first));green_under=calloc(n,sizeof(*green_under));green_under_owner=calloc(n,1);
  for(int yi=0;yi<11;yi++)for(int xi=0;xi<11;xi++) {
   int x=xs[xi],y=ys[yi];
   for(size_t i=0;i<n;i++) {
    unsigned v=((i/c.w/d)*43+(i%c.w/d)*17)%256;
    orig[i]=0xff000000u|v*0x010101u;((Uint32*)c.pixels)[i]=orig[i];
    hd_owner[i]=i%37==0?1:0;
   }
   GreenBackground b;green_background_snapshot(&b,x,y);
   for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++) {
    int dx=x*d+ax,dy=y*d+ay;
    if(dx<0||dy<0||dx>=c.w||dy>=c.h)continue;
    int idx=dy*c.w+dx;unsigned current=orig[idx]&255;
    double fx=(dx+0.5)/d-0.5,fy=(dy+0.5)/d-0.5;
    int bx=(int)floor(fx),by=(int)floor(fy);double wx=fx-bx,wy=fy-by,expected=0;
    for(int iy=0;iy<2;iy++)for(int ix=0;ix<2;ix++) {
     int tx=(bx+ix)*d+d/2,ty=(by+iy)*d+d/2;unsigned val=current;
     if(tx>=0&&ty>=0&&tx<c.w&&ty<c.h&&(ty*c.w+tx)%37!=0)val=orig[ty*c.w+tx]&255;
     expected+=val*(ix?wx:1-wx)*(iy?wy:1-wy);
    }
    unsigned got=green_background_peak(&b,ax,ay,orig[idx]);
    if(got!=(unsigned)floor(expected+0.5)) {fprintf(stderr,"Mismatch d=%d x=%d y=%d ax=%d ay=%d got=%u expected=%f\n",d,x,y,ax,ay,got,expected);return 1;}
    assert(got<=255);checks++;
    ((Uint32*)c.pixels)[idx]=0xffff00ffu;hd_owner[idx]=1;
   }
  }
  free(orig);free(c.pixels);free(hd_owner);free(green_first);free(green_under);free(green_under_owner);
 }
 printf("PASS: %lu clipped-edge/interpolation/immutable-snapshot checks at d=4,8\n",checks);
 return 0;
}
