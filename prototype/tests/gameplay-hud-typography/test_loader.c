#include "gameplay_hud_fixed_text.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static unsigned char source[64000],padded[200*337],payload[23680];
static uint32_t palette[256];
static void read_file(const char *base,const char *name,void *out,size_t n)
{char path[1200];snprintf(path,sizeof(path),"%s/%s",base,name);FILE *f=fopen(path,"rb");assert(f);assert(fread(out,1,n,f)==n);assert(fgetc(f)==EOF);fclose(f);}
int main(int argc,char **argv)
{
 assert(argc==2);const char *base=argv[1];char path[1200];
 read_file(base,"source.bin",source,sizeof(source));read_file(base,"payload.bin",payload,sizeof(payload));
 for(int i=0;i<256;i++)palette[i]=0xaa000000u|((uint32_t)((i*3)%256)<<16)|((uint32_t)((i*7)%256)<<8)|(uint32_t)((i*11)%256);
 assert(!hud_fixed_text_ready());assert(!hud_fixed_text_capture(source,320));
 assert(!hud_fixed_text_load(NULL));assert(!hud_fixed_text_load(base));hud_fixed_text_shutdown();
 assert(hud_fixed_text_load(base));assert(!hud_fixed_text_ready());assert(hud_fixed_text_palette_matches(palette));
 palette[1]^=1;assert(!hud_fixed_text_palette_matches(palette));
 /* Capture succeeds before any normalRGBpalette exists. */
 assert(hud_fixed_text_capture(source,320));assert(hud_fixed_text_ready());palette[1]^=1;
 unsigned count=0;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++)if(hud_fixed_text_cell(x,y)>=0)count++;
 assert(count==370);assert(hud_fixed_text_cell(-1,0)<0);assert(hud_fixed_text_cell(320,200)<0);
 for(unsigned cell=0;cell<370;cell++) {
  int x,y;assert(hud_fixed_text_position(cell,&x,&y));assert(hud_fixed_text_cell(x,y)==(int)cell);
  unsigned group=cell<95?0:cell<245?1:2;
  for(unsigned g=0;g<3;g++)assert(hud_fixed_text_group_matches(g,source,320));
  source[y*320+x]^=1;
  for(unsigned g=0;g<3;g++)assert(hud_fixed_text_group_matches(g,source,320)==(g!=group));
  source[y*320+x]^=1;
  unsigned offset,w,local;if(cell<95){offset=0;w=19;}else{offset=95+(cell-95)/25*25;w=5;}local=cell-offset;
  for(int sy=0;sy<4;sy++)for(int sx=0;sx<4;sx++) {
   size_t n=4*(offset*16+((local/w)*4+sy)*w*4+(local%w)*4+sx);
   assert(!memcmp(hud_fixed_text_sample(cell,sx,sy,4),payload+n,4));
   for(int ry=0;ry<2;ry++)for(int rx=0;rx<2;rx++)assert(!memcmp(hud_fixed_text_sample(cell,sx*2+rx,sy*2+ry,8),payload+n,4));
  }
 }
 for(int d=0;d<16;d++)if(d!=4&&d!=8)assert(!hud_fixed_text_sample(0,0,0,d));
 assert(!hud_fixed_text_sample(370,0,0,4));assert(!hud_fixed_text_sample(0,-1,0,4));assert(!hud_fixed_text_sample(0,0,4,4));
 assert(!hud_fixed_text_position(370,NULL,NULL));assert(!hud_fixed_text_group_matches(3,source,320));assert(!hud_fixed_text_group_matches(0,NULL,320));
 memset(padded,0xe3,sizeof(padded));for(int y=0;y<200;y++)memcpy(padded+y*337,source+y*320,320);
 assert(hud_fixed_text_capture(padded,337));assert(hud_fixed_text_group_matches(2,padded,337));
 source[0]^=1;assert(!hud_fixed_text_capture(source,320));assert(!hud_fixed_text_ready());source[0]^=1;
 assert(!hud_fixed_text_capture(source,319));assert(!hud_fixed_text_capture(NULL,320));assert(hud_fixed_text_capture(source,320));
 hud_fixed_text_forget_source();assert(!hud_fixed_text_sample(0,0,0,4));hud_fixed_text_shutdown();
 unsigned invalid=0;for(;;invalid++) {snprintf(path,sizeof(path),"%s/bad-%u",base,invalid);char file[1300];snprintf(file,sizeof(file),"%s/case",path);FILE *f=fopen(file,"rb");if(!f)break;fclose(f);assert(!hud_fixed_text_load(path));assert(!hud_fixed_text_load(base));hud_fixed_text_shutdown();}
 assert(invalid>=300);assert(hud_fixed_text_load(base));hud_fixed_text_shutdown();
 printf("HUT1 loader PASS: %u invalid resources,370 complete-group mutations,29600 exact4/8samples,source/palette timing and bounded lifecycle.\n",invalid);
}
