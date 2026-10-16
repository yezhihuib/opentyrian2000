/* Compile the actual integration adapter against minimal SDL/game declarations.
 * No engine writer or original game data is needed. */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "storm_test_pins.h"
#include "../src/gameplay_hud_storm.c"
typedef uint8_t Uint8;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {void *pixels;SDL_PixelFormat *format;int w,h,pitch;SDL_Rect clip_rect;} SDL_Surface;
typedef struct {Uint8 *data;unsigned size,width,height;} Sprite;
static struct {Sprite sprite[152];unsigned count;} sprite_table[8];
static struct {struct {unsigned sidekick[2];} items;struct {unsigned style,charge;} sidekick[2];} player[2];
static struct {unsigned icongr,wpnum,ammo;} options[40];
enum {OPTION_SHAPES=5,LEFT_SIDEKICK=0,RIGHT_SIDEKICK=1,DIFFICULTY_NORMAL=2,DIFFICULTY_HARD=3,SA_NONE=0};
static int episodeNum=1,lvlFileNum=9,initialDifficulty=DIFFICULTY_NORMAL;
static int xmas,isNetworkGame,twoPlayerMode,twoPlayerLinked,galagaMode,play_demo,record_demo;
static int onePlayerAction,superTyrian,superArcadeMode,timedBattleMode,bonusLevel,normalBonusLevelCurrent,bonusLevelCurrent;
static const char *game_probe_assets,*reject_reason;
static bool game_probe_original_reference;
static int game_probe_density=4;
static SDL_Surface *VGAScreenSeg,*output;
static uint32_t rgb_palette[256];
static bool mirror_enabled(void){return true;}
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "../src/gameplay_hud_storm_mirror.inc"
int main(int argc,char **argv)
{
 assert(argc==2);game_probe_assets=argv[1];
 static Uint8 bytes[64000],raw[312];memset(bytes,17,sizeof(bytes));unsigned n=0;
 for(unsigned y=0;y<13;y++){raw[n++]=255;raw[n++]=3;for(unsigned x=3;x<25;x++)raw[n++]=(Uint8)(192+(x+y)%16);}
 SDL_PixelFormat format={8,1};SDL_Surface screen={bytes,&format,320,200,320,{0,0,320,200}};
 VGAScreenSeg=&screen;output=&screen;
 sprite_table[5].count=70;sprite_table[5].sprite[37]=(Sprite){raw,sizeof(raw),25,13};
 player[0].items.sidekick[1]=9;options[9].icongr=38;options[9].wpnum=88;options[9].ammo=6;
 storm_start(&screen);assert(state.live&&state.loaded);storm_resume();
 render_mirror_hud_storm_begin(&screen,1,9,38,284,82);
 for(unsigned y=82;y<98;y++)memset(bytes+y*320+284,0,29);
 SDL_Rect clear={284,82,29,16};storm_rect(&screen,&clear);assert(state.cleared);
 for(unsigned y=0;y<13;y++)for(unsigned x=3;x<25;x++){Uint8 *p=bytes+(82+y)*320+284+x;*p=(Uint8)(192+(x+y)%16);storm_pixel(&screen,p);}
 render_mirror_hud_storm_end(&screen,1);assert(state.recorded);
 SDL_Rect extremes[]={{INT_MAX,INT_MAX,INT_MAX,INT_MAX},{INT_MIN,INT_MIN,INT_MAX,INT_MAX},{INT_MIN,0,INT_MIN,200},{0,INT_MIN,320,INT_MIN},{284,82,INT_MAX,INT_MAX}};
 for(unsigned i=0;i<4;i++){storm_rect(&screen,&extremes[i]);assert(state.recorded);}
 storm_rect(&screen,&extremes[4]);assert(!state.recorded);
 state.recorded=true;screen.clip_rect=(SDL_Rect){INT_MAX,INT_MAX,INT_MAX,INT_MAX};storm_rect(&screen,&clear);assert(!state.recorded);
 state.recorded=true;screen.clip_rect=(SDL_Rect){0,0,320,200};screen.pitch=319;storm_rect(&screen,&clear);assert(!state.live);
 render_mirror_hud_storm_source_reset(5);assert(!state.live);
 /* Ensure the actual texture adapter is compiled/called, with a revoked lease
  * so no writes occur even though these deliberately tiny mock layouts differ. */
 storm_present(bytes,320);puts("STORM adapter overflow/history tests passed");return 0;
}
