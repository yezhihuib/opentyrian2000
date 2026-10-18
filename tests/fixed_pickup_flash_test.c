/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "fixed_pickup_flash.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
 for(unsigned ttl=0;ttl<=8;ttl++) {
  assert(fixed_pickup_flash_eligible(true,false,0,144,ttl)==(ttl>=1&&ttl<=7));
  assert(!fixed_pickup_flash_eligible(false,false,0,144,ttl));
  assert(!fixed_pickup_flash_eligible(true,true,0,144,ttl));
  assert(!fixed_pickup_flash_eligible(true,false,1,144,ttl));
  assert(!fixed_pickup_flash_eligible(true,false,-1,144,ttl));
  assert(!fixed_pickup_flash_eligible(true,false,0,143,ttl));
  assert(!fixed_pickup_flash_eligible(true,false,0,145,ttl));
 }
 uint32_t pal[256]={0};for(unsigned i=0;i<16;i++)pal[0x70+i]=(i*16)<<16|(i*8)<<8|i*2;
 uint8_t copy[12*14*8*8*4];uint8_t *art=fixed_pickup_flash_rgba(pal);memcpy(copy,art,sizeof(copy));
 unsigned opaque=0,partial=0;double sx=0,sy=0,weight=0;
 for(int y=0;y<112;y++)for(int x=0;x<96;x++) {
  const uint8_t *p=art+4*(y*96+x);
  if(p[3]==255)opaque++;else if(p[3])partial++;
  if(p[3]){assert(x>=22&&x<75&&y>=40&&y<80);sx+=(x+.5)*p[3]/8;sy+=(y+.5)*p[3]/8;weight+=p[3];}
  assert(p[3]||!(p[0]|p[1]|p[2]));assert(p[0]<=176);
 }
 assert(opaque>400&&partial>300);assert(sx/weight>5.8&&sx/weight<6.2);assert(sy/weight>7.3&&sy/weight<7.7);
 assert(fixed_pickup_flash_rgba(pal)==art);assert(!memcmp(copy,fixed_pickup_flash_rgba(pal),sizeof(copy)));
 pal[1]^=0xffffff;assert(!memcmp(copy,fixed_pickup_flash_rgba(pal),sizeof(copy)));
 pal[0x78]^=0xffffff;assert(memcmp(copy,fixed_pickup_flash_rgba(pal),sizeof(copy)));
 pal[0x78]^=0xffffff;assert(!memcmp(copy,fixed_pickup_flash_rgba(pal),sizeof(copy)));
 puts("fixed flash145: eligibility, bounded warm geometry, deterministic palette cache passed");return 0;
}
