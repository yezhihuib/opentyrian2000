/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "data_pickup_glyph.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
 for(unsigned ttl=0;ttl<=15;ttl++) {
  assert(data_pickup_glyph_eligible(true,false,0,265,ttl)==(ttl>=1&&ttl<=14));
  assert(!data_pickup_glyph_eligible(false,false,0,265,ttl));
  assert(!data_pickup_glyph_eligible(true,true,0,265,ttl));
  assert(!data_pickup_glyph_eligible(true,false,1,265,ttl));
  assert(!data_pickup_glyph_eligible(true,false,-1,265,ttl));
  assert(!data_pickup_glyph_eligible(true,false,0,264,ttl));
  assert(!data_pickup_glyph_eligible(true,false,0,266,ttl));
 }
 uint32_t pal[256]={0};for(unsigned i=0;i<16;i++)pal[0x70+i]=(i*16)<<16|(i*8)<<8|i*2;
 uint8_t copy[12*14*8*8*4];uint8_t *art=data_pickup_glyph_rgba(pal);memcpy(copy,art,sizeof(copy));
 unsigned opaque=0,partial=0;
 for(unsigned i=0;i<sizeof(copy)/4;i++) {
  if(art[4*i+3]==255)opaque++;else if(art[4*i+3])partial++;
  assert(art[4*i+3]||!(art[4*i]|art[4*i+1]|art[4*i+2]));
 }
 assert(opaque>1000&&partial>50);assert(data_pickup_glyph_rgba(pal)==art);
 assert(!memcmp(copy,data_pickup_glyph_rgba(pal),sizeof(copy)));
 pal[1]^=0xffffff;assert(!memcmp(copy,data_pickup_glyph_rgba(pal),sizeof(copy)));
 pal[0x78]^=0xffffff;assert(memcmp(copy,data_pickup_glyph_rgba(pal),sizeof(copy)));
 pal[0x78]^=0xffffff;assert(!memcmp(copy,data_pickup_glyph_rgba(pal),sizeof(copy)));
 puts("DATA vector: eligibility boundaries, deterministic cache and palette recolor passed");return 0;
}
