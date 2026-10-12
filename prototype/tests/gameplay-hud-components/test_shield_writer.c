#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
typedef unsigned int uint;
typedef int JE_integer;
typedef uint8_t JE_byte;
typedef struct {uint8_t pixels[64000];} SDL_Surface;
static SDL_Surface surface,*VGAScreen=&surface,*VGAScreenSeg=&surface;
static bool twoPlayerMode,galagaMode;
static struct {uint shield,shield_max,armor;} player[2];
#define COUNTOF(x) (sizeof(x)/sizeof((x)[0]))
static unsigned draws,wipes,rectangles;
static unsigned last_s,last_m;
static void JE_rectangle(SDL_Surface *p,int x0,int y0,int x1,int y1,int color)
{assert(x0>=0&&x1<320&&y0>=0&&y1<200);for(int y=y0;y<=y1;y++)for(int x=x0;x<=x1;x++)p->pixels[y*320+x]=(uint8_t)color;++rectangles;}
static void fill_rectangle_xy(SDL_Surface *p,int x0,int y0,int x1,int y1,int color)
{JE_rectangle(p,x0,y0,x1,y1,color);}
static void render_mirror_hud_shield_drawn(SDL_Surface *p,unsigned s,unsigned m)
{assert(p==VGAScreen);++draws;last_s=s;last_m=m;}
static void render_mirror_hud_shield_wiped(SDL_Surface *p)
{assert(p==VGAScreenSeg);++wipes;}
#include "writers.inc"
static uint8_t scalar(int x,int y,unsigned s,unsigned m)
{
 if(x<270||x>278||y<137||y>194)return 77;
 if(s!=m&&y==193-(int)(2*m))return 68;
 int distance=194-y;
 if(distance>=(int)(2*(s+1)))return 0;
 /* Independently derive color from the original first-three, then pairs
  * progression. This does not execute or reuse the writer's zWait code. */
 int band=distance/2;
 return (uint8_t)(146+(band<3?0:1+(band-3)/2));
}
static void seed(void)
{memset(surface.pixels,77,64000);for(int y=137;y<195;y++)memset(surface.pixels+y*320+270,0,9);}
static void verify(unsigned s,unsigned m)
{for(int y=0;y<200;y++)for(int x=0;x<320;x++)assert(surface.pixels[y*320+x]==scalar(x,y,s,m));}
int main(void)
{
 unsigned states=0;
 for(unsigned m=0;m<=28;m++)for(unsigned s=0;s<=m;s++){
  seed();player[0].shield=s;player[0].shield_max=m;JE_drawShield();verify(s,m);assert(last_s==s&&last_m==m);++states;
 }
 assert(states==435&&draws==435);
 /* Consecutive regeneration writes preserve the old marker until full fill. */
 seed();player[0].shield_max=28;
 for(unsigned s=0;s<=28;s++){player[0].shield=s;JE_drawShield();verify(s,28);}
 /* Original wipe also touches armor; verify only the bounded shield channel. */
 for(int s=27;s>=0;s--){player[0].shield=(unsigned)s;JE_wipeShieldArmorBars();JE_drawShield();for(int y=137;y<195;y++)for(int x=270;x<279;x++)assert(surface.pixels[y*320+x]==scalar(x,y,(unsigned)s,28));}
 assert(wipes==28);
 /* A wipe-only constantDie event at zero is all black, unlike draw-at-zero. */
 player[0].shield=0;unsigned before=draws;JE_wipeShieldArmorBars();assert(draws==before);
 for(int y=137;y<195;y++)for(int x=270;x<279;x++)assert(surface.pixels[y*320+x]==0);
 JE_drawShield();assert(surface.pixels[194*320+270]==146);
 /* Changing live state without an original draw cannot change displayed bytes. */
 uint8_t previous[64000];memcpy(previous,surface.pixels,64000);player[0].shield=10;assert(!memcmp(previous,surface.pixels,64000));
 printf("PASS independent original shield writer: %u S/M states, %u rectangle calls, regeneration/depletion/wipe-only/stale-display semantics\n",states,rectangles);
 return 0;
}
