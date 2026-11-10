/* Test-only SDL event injection and read-only observer. Never in the game build. */
#include "SDL.h"
#include "params.h"
#include "network.h"
#include "game_probe.h"
#include "asset_debug.h"
#include "episodes.h"
#include "player.h"
#include "shots.h"
#include "config.h"
#include "varz.h"
#include "video.h"
#include "palette.h"
#include "gameplay_hud.h"
#include "b313_family_canvas.h"
#include "b313_terrain_fallback.h"
#include "b313_player_fallback.h"
#include "b313_tank_fallback.h"
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

static unsigned frames,menu_frames;
static bool in_menu;
static uint64_t previous_frame;
static FILE *receipt;
static void key(SDL_Scancode scan,bool down)
{
 SDL_Event e={0};e.type=down?SDL_KEYDOWN:SDL_KEYUP;e.key.keysym.scancode=scan;
 e.key.state=down?SDL_PRESSED:SDL_RELEASED;
 if(SDL_PushEvent(&e)!=1)abort();
}
void __real_JE_doInGameSetup(void);
void __wrap_JE_doInGameSetup(void)
{
 in_menu=true;key(SDL_SCANCODE_ESCAPE,false);__real_JE_doInGameSetup();in_menu=false;
 if(!reallyEndLevel||!playerEndLevel)abort();
 fprintf(stderr,"NATIVE_PREVIEW_TEST_MENU_ABANDON_OK\n");
}
void __real_SDL_RenderPresent(SDL_Renderer *);
void __wrap_SDL_RenderPresent(SDL_Renderer *r)
{
 if(in_menu) {
  if(++menu_frames==1)key(SDL_SCANCODE_UP,true); /* first row -> Quit */
  else if(menu_frames==2){key(SDL_SCANCODE_UP,false);key(SDL_SCANCODE_RETURN,true);}
  else if(menu_frames>8)abort();
 } else {
  B313FamilyCanvasStatus c=render_mirror_family_status();
  if(c.frames&&c.frames!=previous_frame) {
   previous_frame=c.frames;
   if(!level2_preview_requested||game_probe_enabled||asset_debug_enabled||play_demo||record_demo||
      isNetworkGame||episodeNum!=1||lvlFileNum!=2||mainLevel!=6)abort();
   if(!receipt){receipt=fopen("native-preview.csv","w");if(!receipt)abort();
    fputs("frame,x,y,invulnerable,armor,shield,shots,family_presents,terrain_presents,player_presents,tank_presents,hud_owned,hud_mismatches,native_hud_mismatches\n",receipt);}
   B313TerrainFallbackStatus t=render_mirror_terrain_fallback_status();
   B313PlayerFallbackStatus p=render_mirror_player_fallback_status();
   B313TankFallbackStatus k=render_mirror_tank_fallback_status();
   unsigned shots=0,owned=0,bad=0,native_bad=0;
   for(unsigned i=0;i<MAX_PWEAPON;i++)shots+=shotAvail[i]!=0;
   int w,h;if(SDL_GetRendererOutputSize(r,&w,&h)||w%320||h%200||w/320!=h/200)abort();
   int scale=w/320;if(scale!=2&&scale!=4)abort();
   Uint32 *pixels=malloc((size_t)w*h*4);if(!pixels||SDL_RenderReadPixels(r,NULL,SDL_PIXELFORMAT_ARGB8888,pixels,w*4))abort();
   for(int y=0;y<h;y++)for(int x=0;x<w;x++) {
    if(x<264*scale&&y<184*scale)continue;
    Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[(y/scale)*VGAScreenSeg->pitch+x/scale];
    const Uint8 *rgba=gameplay_hud_sample(x/scale,y/scale,(x%scale)*(8/scale)+(4/scale),(y%scale)*(8/scale)+(4/scale),8,index);
    Uint32 actual=pixels[y*w+x]&0xffffffu;
    if(rgba){owned++;bad+=actual!=(((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2]);}
    else native_bad+=actual!=(rgb_palette[index]&0xffffffu);
   }
   free(pixels);
   fprintf(receipt,"%u,%d,%d,%u,%u,%u,%u,%"PRIu64",%"PRIu64",%"PRIu64",%"PRIu64",%u,%u,%u\n",
      frames,player[0].x,player[0].y,player[0].invulnerable_ticks,player[0].armor,player[0].shield,shots,c.presents,t.presents,p.presents,k.presents,owned,bad,native_bad);
   if(fflush(receipt))abort();
   /* Go through the real SDL event pump and ordinary keyboard path. No keysactive/player writes. */
   if(frames==10)key(SDL_SCANCODE_SPACE,true);
   if(frames==30)key(SDL_SCANCODE_LEFT,true);
   if(frames==54)key(SDL_SCANCODE_LEFT,false);
   if(frames==90)key(SDL_SCANCODE_RIGHT,true);
   if(frames==138)key(SDL_SCANCODE_RIGHT,false);
   if(frames==150)key(SDL_SCANCODE_UP,true);
   if(frames==165)key(SDL_SCANCODE_UP,false);
   if(frames==210)key(SDL_SCANCODE_DOWN,true);
   if(frames==225)key(SDL_SCANCODE_DOWN,false);
   if(++frames==(unsigned)strtoul(getenv("NATIVE_PREVIEW_TEST_FRAMES"),NULL,10)) {
    key(SDL_SCANCODE_SPACE,false);key(SDL_SCANCODE_ESCAPE,true);
   }
  }
 }
 __real_SDL_RenderPresent(r);
}
