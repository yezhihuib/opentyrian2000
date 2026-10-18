/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "secret_exit_orb.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
enum { BYTES=24*28*8*8*4 };
static uint8_t copy[3][BYTES];
int main(void)
{
 const unsigned bases[3]={85,131,233};uint32_t pal[256]={0};
 pal[1]=0x080808;for(unsigned i=0;i<16;i++)pal[0x70+i]=(i*17)<<16|(i*10)<<8|i*3;
 assert(secret_exit_orb_phase(85)==0&&secret_exit_orb_phase(131)==1&&secret_exit_orb_phase(233)==2);
 for(unsigned i=0;i<300;i++)if(i!=85&&i!=131&&i!=233){assert(secret_exit_orb_phase(i)<0);assert(!secret_exit_orb_rgba(i,pal));}
 assert(!secret_exit_orb_rgba(85,NULL));
 for(unsigned f=0;f<3;f++)memcpy(copy[f],secret_exit_orb_rgba(bases[f],pal),BYTES);
 unsigned partial=0,opaque=0;double area=0;
 for(unsigned i=0;i<BYTES;i+=4) {
  unsigned x=(i/4)%192,y=(i/4)/192;
  assert(copy[0][i+3]==copy[1][i+3]&&copy[1][i+3]==copy[2][i+3]);
  unsigned a=copy[0][i+3];area+=a/255.0/64;
  if(a==255)opaque++;else if(a)partial++;
  if(a){assert(x>=7&&x<177&&y>=31&&y<201);}
  for(unsigned f=0;f<3;f++)for(unsigned c=0;c<3;c++) {
   if(!a)assert(!copy[f][i+c]);
   if(f)assert(copy[f][i+c]>=copy[f-1][i+c]);
  }
 }
 assert(area>335&&area<360&&opaque>20000&&partial>500);
 for(unsigned f=0;f<3;f++)assert(!memcmp(copy[f],secret_exit_orb_rgba(bases[f],pal),BYTES));
 pal[2]^=0xffffff;assert(!memcmp(copy[0],secret_exit_orb_rgba(85,pal),BYTES));
 pal[0x78]^=0xffffff;assert(memcmp(copy[0],secret_exit_orb_rgba(85,pal),BYTES));
 pal[0x78]^=0xffffff;assert(!memcmp(copy[0],secret_exit_orb_rgba(85,pal),BYTES));
 pal[1]^=0xffffff;assert(memcmp(copy[0],secret_exit_orb_rgba(85,pal),BYTES));
 puts("secret exit orb: three fixed contours, monotone pulse, bounded geometry and warm palette cache passed");
 return 0;
}
