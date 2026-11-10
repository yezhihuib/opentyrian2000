/* Read-only native scene observer; never linked by the normal game build. */
#include "SDL.h"
#include "config.h"
#include "keyboard.h"
#include "player.h"
#include "video.h"
#include "varz.h"
#include "palette.h"
#include "player_ship_family.h"
#include "b313_family_canvas.h"
#include "b313_terrain_fallback.h"
#include "b313_player_fallback.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

static unsigned tick,presents;
static FILE *mask_stream;
static const unsigned capture_ticks[]={1,20,40,90,99,100,101,130,140,143,180,239,293,320,400,462,500,539};
void original_test_state(FILE *);
void original_test_input(void)
{
 for(unsigned i=0;i<8;i++)keysactive[keySettings[i]]=0;
 keysactive[keySettings[KEY_SETTING_FIRE]]=1;
 unsigned phase=tick%240;
 keysactive[keySettings[KEY_SETTING_LEFT]]=phase>=30&&phase<54;
 keysactive[keySettings[KEY_SETTING_RIGHT]]=phase>=90&&phase<138;
 keysactive[keySettings[KEY_SETTING_UP]]=tick>=150&&tick<165;
 keysactive[keySettings[KEY_SETTING_DOWN]]=tick>=210&&tick<225;
}
static FILE *open_output(const char *name,const char *mode)
{
 char path[4096];int n=snprintf(path,sizeof path,"%s/%s",getenv("ORIGINAL_TEST_OUT"),name);
 if(n<0||(size_t)n>=sizeof path)abort();FILE *f=fopen(path,mode);if(!f)abort();return f;
}
static uint64_t hash_rgb(uint64_t hash,Uint32 pixel)
{
 for(int b=16;b>=0;b-=8)hash=(hash^((pixel>>b)&255))*UINT64_C(1099511628211);
 return hash;
}
static void audit_present(SDL_Renderer *renderer)
{
 static FILE *f;static uint64_t previous_accepted;
 B313FamilyCanvasStatus scene=render_mirror_family_status();
 B313TerrainFallbackStatus terrain=render_mirror_terrain_fallback_status();
 B313PlayerFallbackStatus local=render_mirror_player_fallback_status();
 PlayerShipFamilyStatus ship=render_mirror_player_ship_family_status();
 bool enabled=getenv("BUILDING313_PLAYER_FALLBACK_ENABLE")!=NULL;
 if(!f){f=open_output("player-present.csv","w");fputs("tick,family,terrain,legacy_ship,legacy_pose,local,local_pose,local_callbacks,local_cells,local_reason,inside_pixels,candidate_mismatches,outside_hash,inside_hash,local_presents\n",f);}
 int w,h;if(SDL_GetRendererOutputSize(renderer,&w,&h)||w%320||h%200||w/320!=h/200)abort();
 int scale=w/320;if(scale!=2&&scale!=4)abort();
 Uint32 *pixels=malloc((size_t)w*h*sizeof *pixels);if(!pixels)abort();
 if(SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,pixels,w*4))abort();
 uint8_t owners[672]={0};uint32_t patch[43008];int32_t header[4]={(int32_t)tick,0,0,0};
 if(enabled){
  if(local.presenting){
   if(!terrain.presenting||!render_mirror_player_fallback_sample(owners,sizeof owners,patch,43008))abort();
   header[1]=local.x;header[2]=local.y;header[3]=1;
   unsigned cells=0;for(unsigned i=0;i<672;i++){if(owners[i]>1)abort();cells+=owners[i];}
   if(!cells||cells!=local.surviving_cells)abort();
  }else if(render_mirror_player_fallback_sample(owners,sizeof owners,patch,43008))abort();
  if(!mask_stream)mask_stream=open_output("ownership.bin","wb");
  if(fwrite(header,sizeof header,1,mask_stream)!=1||fwrite(owners,sizeof owners,1,mask_stream)!=1||fflush(mask_stream))abort();
 }else{
  if(local.presenting)abort();
  if(!mask_stream){mask_stream=fopen(getenv("PLAYER_FALLBACK_REFERENCE_MASK"),"rb");if(!mask_stream)abort();}
  if(fread(header,sizeof header,1,mask_stream)!=1||fread(owners,sizeof owners,1,mask_stream)!=1||header[0]!=(int32_t)tick)abort();
 }
 if(header[3]&&(header[1]<24||header[1]>264||header[2]<0||header[2]>156))abort();
 uint64_t outside=UINT64_C(14695981039346656037),inside=outside;unsigned owned_pixels=0,bad=0;
 for(int y=0;y<h;y++)for(int x=0;x<w;x++){
  Uint32 actual=pixels[y*w+x]&0xffffffu;
  int lx=x/scale+24-header[1],ly=y/scale-header[2];
  bool owned=header[3]&&x<264*scale&&y<184*scale&&lx>=0&&lx<24&&ly>=0&&ly<28&&owners[ly*24+lx];
  if(owned){
   ++owned_pixels;inside=hash_rgb(inside,actual);
   if(enabled){unsigned sx=(unsigned)lx*8+(unsigned)(x%scale)*(8/scale)+(4/scale);
    unsigned sy=(unsigned)ly*8+(unsigned)(y%scale)*(8/scale)+(4/scale);
    bad+=actual!=(patch[sy*192+sx]&0xffffffu);}
  }else outside=hash_rgb(outside,actual);
 }
 bool family=scene.accepted_frames>previous_accepted&&!scene.frame_failed&&!terrain.presenting;
 bool legacy=family&&ship.draw.accepted&&!ship.draw.failed;
 if(legacy&&local.presenting)abort();
 fprintf(f,"%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%016"PRIx64",%016"PRIx64",%"PRIu64"\n",tick,
  family,terrain.presenting,legacy,ship.draw.index,local.presenting,local.index,local.callback_count,
  local.surviving_cells,local.reason,owned_pixels,bad,outside,inside,local.presents);
 if(fflush(f))abort();previous_accepted=scene.accepted_frames;
 bool capture=false;for(unsigned i=0;i<sizeof capture_ticks/sizeof *capture_ticks;i++)capture|=tick==capture_ticks[i];
 if(capture){char name[80];snprintf(name,sizeof name,"frame-%04u.ppm",tick);FILE *out=open_output(name,"wb");
  fprintf(out,"P6\n%d %d\n255\n",w,h);
  for(int i=0;i<w*h;i++){Uint32 pixel=pixels[i];unsigned char rgb[3]={(unsigned char)(pixel>>16),(unsigned char)(pixel>>8),(unsigned char)pixel};if(fwrite(rgb,1,3,out)!=3)abort();}
  if(fclose(out))abort();}
 free(pixels);++presents;
}
void __real_SDL_RenderPresent(SDL_Renderer *);
void __wrap_SDL_RenderPresent(SDL_Renderer *renderer)
{if(render_mirror_family_status().frames)audit_present(renderer);__real_SDL_RenderPresent(renderer);}
bool original_test_end(void)
{
 static FILE *f;
 if(!f){f=open_output("state.csv","w");fputs("tick,players,enemies,shots,particles,globals,rng,native,output,x,y,inv,armor,shield,family_presents,terrain_presents,local_presents,presents\n",f);}
 fprintf(f,"%u,",tick);original_test_state(f);
 fprintf(f,",%d,%d,%u,%u,%u,%"PRIu64",%"PRIu64",%"PRIu64",%u\n",player[0].x,player[0].y,
  player[0].invulnerable_ticks,player[0].armor,player[0].shield,render_mirror_family_status().presents,
  render_mirror_terrain_fallback_status().presents,render_mirror_player_fallback_status().presents,presents);
 if(fflush(f))abort();
 bool done=++tick>=(unsigned)strtoul(getenv("ORIGINAL_TEST_TICKS"),NULL,10);
 if(done&&mask_stream&&!getenv("BUILDING313_PLAYER_FALLBACK_ENABLE")&&fgetc(mask_stream)!=EOF)abort();
 return done;
}
