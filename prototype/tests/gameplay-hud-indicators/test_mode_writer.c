#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#define OPTION_SHAPES 5
typedef struct {uint8_t pixels[64000];} SDL_Surface;
static SDL_Surface surface,*VGAScreenSeg=&surface;
static uint8_t original[64000],expected[64000];
static bool twoPlayerMode;
static struct {unsigned int weapon_mode;} player[2];
static unsigned int calls,events,mode_event;
static void blit_sprite(SDL_Surface *s,int x,int y,int table,int sprite)
{
 assert(s==VGAScreenSeg&&table==5&&y==44&&x==(calls?302:285)&&calls<2);
 int expected_id=player[0].weapon_mode==1?(calls?19:18):(calls?18:19);assert(sprite==expected_id);
 ++calls;
 for(int yy=0;yy<8;yy++)for(int xx=0;xx<10;xx++)s->pixels[(y+yy)*320+x+xx]=(uint8_t)(sprite*3+yy+xx);
}
static void render_mirror_hud_mode_drawn(SDL_Surface *s,unsigned int mode)
{assert(s==VGAScreenSeg&&calls==2&&memcmp(s->pixels,expected,64000)==0);++events;mode_event=mode;}
#include "writer.inc"
int main(void)
{
 unsigned int modes[]={1,2,0,3,UINT_MAX};
 for(unsigned i=0;i<64000;i++)original[i]=(uint8_t)(i*17);
 for(unsigned m=0;m<sizeof(modes)/sizeof(modes[0]);m++)for(int two=0;two<2;two++) {
  memcpy(surface.pixels,original,64000);memcpy(expected,original,64000);player[0].weapon_mode=modes[m];twoPlayerMode=two;calls=events=mode_event=0;
  if(!two)for(int y=44;y<52;y++)for(int x=285;x<312;x++)if(x<295||x>=302){int side=x>=302,sprite=(modes[m]==1)^side?18:19;expected[y*320+x]=(uint8_t)(sprite*3+y-44+x-(side?302:285));}
  JE_drawPortConfigButtons();assert(calls==(two?0u:2u)&&events==(two?0u:1u));assert(two||mode_event==modes[m]);assert(memcmp(surface.pixels,expected,64000)==0&&player[0].weapon_mode==modes[m]);
 }
 puts("PASS original MODE writer: both real states, unsupported stamps, two-player early return, exact 64000-byte raster and post-both-blits event ordering");return 0;
}
