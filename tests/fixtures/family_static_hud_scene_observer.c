/* Diagnostic-only original-input scene harness. Never linked by the game build. */

#include "SDL.h"
#include "config.h"
#include "keyboard.h"
#include "player.h"
#include "video.h"
#include "varz.h"
#include "palette.h"
#include "player_ship_family.h"
#include "b313_family_canvas.h"
#include "gameplay_hud.h"
#ifdef TERRAIN_FALLBACK_OBSERVER
#include "b313_terrain_fallback.h"
#endif
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <stdbool.h>
static unsigned tick=0,presents;
void original_test_state(FILE *);
void original_test_input(void){
 for(unsigned i=0;i<8;i++)keysactive[keySettings[i]]=0;
 keysactive[keySettings[KEY_SETTING_FIRE]]=1;
 unsigned phase=tick%240;
 keysactive[keySettings[KEY_SETTING_LEFT]]=phase>=30&&phase<54;
 keysactive[keySettings[KEY_SETTING_RIGHT]]=phase>=90&&phase<138;
 keysactive[keySettings[KEY_SETTING_UP]]=tick>=150&&tick<165;
 keysactive[keySettings[KEY_SETTING_DOWN]]=tick>=210&&tick<225;
}
static void save_frame(SDL_Renderer *r){
 static const unsigned frames[]={1,20,40,90,99,100,101,130,180,239,320,400,500};
 bool save=false;for(unsigned i=0;i<sizeof frames/sizeof *frames;i++)save|=tick==frames[i];
 if(!save)return;
 int w,h;if(SDL_GetRendererOutputSize(r,&w,&h)||w<=0||h<=0)abort();
 unsigned char *pixels=malloc((size_t)w*h*3);if(!pixels)abort();
 if(SDL_RenderReadPixels(r,NULL,SDL_PIXELFORMAT_RGB24,pixels,w*3))abort();
 const char *out=getenv("ORIGINAL_TEST_OUT");char p[4096];snprintf(p,sizeof p,"%s/frame-%04u-%04u.ppm",out,tick,presents);
 FILE*f=fopen(p,"wb");if(!f)abort();fprintf(f,"P6\n%d %d\n255\n",w,h);if(fwrite(pixels,3,(size_t)w*h,f)!=(size_t)w*h||fclose(f))abort();free(pixels);
}
void __real_SDL_RenderPresent(SDL_Renderer *r);
static void audit_hud(SDL_Renderer *renderer)
{
 B313FamilyCanvasStatus status=render_mirror_family_status();
 if(!status.frames)return;
 static FILE *f;static uint64_t previous_accepted;
 if(!f){char path[4096];snprintf(path,sizeof path,"%s/hud-present.csv",getenv("ORIGINAL_TEST_OUT"));f=fopen(path,"w");if(!f)abort();fputs("tick,scene_accepted,playfield_hash,owned_pixels,hud_mismatches,unowned_mismatches,terrain_presenting,terrain_cells,terrain_presents,family_failed\n",f);}
 unsigned terrain_presenting=0,terrain_cells=0;uint64_t terrain_presents=0;
#ifdef TERRAIN_FALLBACK_OBSERVER
 B313TerrainFallbackStatus terrain=render_mirror_terrain_fallback_status();
 terrain_presenting=terrain.presenting;terrain_cells=terrain.surviving_cells;terrain_presents=terrain.presents;
#endif
 int w,h;if(SDL_GetRendererOutputSize(renderer,&w,&h)||w%320||h%200||w/320!=h/200)abort();
 int scale=w/320;if(scale!=2&&scale!=4)abort();
 Uint32 *pixels=malloc((size_t)w*h*sizeof *pixels);if(!pixels)abort();
 if(SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,pixels,w*4))abort();
 uint64_t hash=UINT64_C(14695981039346656037);unsigned owned=0,bad=0,native_bad=0;
 bool enabled=getenv("BUILDING313_FAMILY_HUD_ENABLE")!=NULL;
 for(int y=0;y<h;y++)for(int x=0;x<w;x++){
  Uint32 actual=pixels[y*w+x]&0xffffffu;
  if(x<264*scale&&y<184*scale){for(int b=16;b>=0;b-=8)hash=(hash^((actual>>b)&255))*UINT64_C(1099511628211);continue;}
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[(y/scale)*VGAScreenSeg->pitch+x/scale];
  const Uint8 *rgba=enabled?gameplay_hud_sample(x/scale,y/scale,(x%scale)*(8/scale)+(4/scale),(y%scale)*(8/scale)+(4/scale),8,index):NULL;
  if(rgba){++owned;bad+=actual!=(((Uint32)rgba[0]<<16)|((Uint32)rgba[1]<<8)|rgba[2]);}
  else native_bad+=actual!=(rgb_palette[index]&0xffffffu);
 }
 fprintf(f,"%u,%u,%016"PRIx64",%u,%u,%u,%u,%u,%"PRIu64",%u\n",tick,
         status.accepted_frames>previous_accepted&&!status.frame_failed&&!terrain_presenting,
         hash,owned,bad,native_bad,terrain_presenting,terrain_cells,terrain_presents,status.frame_failed);
 if(fflush(f))abort();previous_accepted=status.accepted_frames;free(pixels);
}
void __wrap_SDL_RenderPresent(SDL_Renderer *r){audit_hud(r);save_frame(r);presents++;__real_SDL_RenderPresent(r);}
bool original_test_end(void){
 static FILE *f;
 if(!f){char p[4096];snprintf(p,sizeof p,"%s/state.csv",getenv("ORIGINAL_TEST_OUT"));f=fopen(p,"w");if(!f)abort();
 fprintf(f,"tick,players,enemies,shots,particles,globals,rng,native,output,x,y,inv,armor,shield,ship_pose,ship_contributed,ship_accepted,ship_failed,ship_reason,ship_style,ship_cells,normal_retire,blend_retire,shadow_writes,family_ready,family_reason,family_presents,presents,terrain_presents\n");}
 PlayerShipFamilyStatus s=render_mirror_player_ship_family_status();B313FamilyCanvasStatus c=render_mirror_family_status();
 uint64_t terrain_presents=0;
#ifdef TERRAIN_FALLBACK_OBSERVER
 terrain_presents=render_mirror_terrain_fallback_status().presents;
#endif
 fprintf(f,"%u,",tick);original_test_state(f);
 fprintf(f,",%d,%d,%u,%u,%u,%u,%u,%u,%u,%u,%d,%u,%"PRIu64",%"PRIu64",%"PRIu64",%u,%u,%"PRIu64",%u,%"PRIu64"\n",player[0].x,player[0].y,player[0].invulnerable_ticks,player[0].armor,player[0].shield,s.draw.index,s.draw.contributed,s.draw.accepted,s.draw.failed,s.first_reason,s.draw.style,s.surviving_cells,s.normal_retirements,s.blend_retirements,s.shadow_writes,c.ready,c.first_reason,c.presents,presents,terrain_presents);fflush(f);
 return ++tick>=(unsigned)strtoul(getenv("ORIGINAL_TEST_TICKS"),NULL,10);
}
