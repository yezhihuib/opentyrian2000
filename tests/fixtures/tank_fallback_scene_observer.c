/* Read-only original-input observer; never linked by the game build. */
#include "SDL.h"
#include "config.h"
#include "keyboard.h"
#include "player.h"
#include "video.h"
#include "varz.h"
#include "palette.h"
#include "player_ship_family.h"
#include "tank194_family.h"
#include "b313_family_canvas.h"
#include "b313_terrain_fallback.h"
#include "b313_player_fallback.h"
#include "b313_tank_fallback.h"
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
 if(n<0||(size_t)n>=sizeof path)abort();
 FILE *f=fopen(path,mode);if(!f)abort();return f;
}
static uint64_t hash_rgb(uint64_t hash,Uint32 pixel)
{
 for(int b=16;b>=0;b-=8)hash=(hash^((pixel>>b)&255))*UINT64_C(1099511628211);
 return hash;
}
static void audit_present(SDL_Renderer *renderer)
{
 static FILE *frames,*slots;static uint64_t previous_accepted;
 B313FamilyCanvasStatus scene=render_mirror_family_status();
 B313TerrainFallbackStatus terrain=render_mirror_terrain_fallback_status();
 B313PlayerFallbackStatus player_local=render_mirror_player_fallback_status();
 B313TankFallbackStatus local=render_mirror_tank_fallback_status();
 PlayerShipFamilyStatus ship=render_mirror_player_ship_family_status();
 Tank194FamilyStatus tank=render_mirror_tank194_family_status();
 bool enabled=getenv("BUILDING313_TANK_FALLBACK_ENABLE")!=NULL;
 if(!frames){
  frames=open_output("tank-present.csv","w");
  fputs("tick,family,terrain,player_legacy,player_local,legacy_mask,local_mask,eligible_mask,local_cells,inside_pixels,candidate_mismatches,outside_hash,inside_hash,local_presents\n",frames);
  slots=open_output("tank-slots.csv","w");
  fputs("tick,slot,epoch,token,generation,eligible,legacy,local,pose,x,y,cells,reason,denied,callbacks\n",slots);
 }
 int w,h;if(SDL_GetRendererOutputSize(renderer,&w,&h)||w%320||h%200||w/320!=h/200)abort();
 int scale=w/320;if(scale!=2&&scale!=4)abort();
 Uint32 *pixels=malloc((size_t)w*h*sizeof *pixels);if(!pixels)abort();
 if(SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,pixels,w*4))abort();
 bool family=scene.accepted_frames>previous_accepted&&!scene.frame_failed&&!terrain.presenting;
 uint8_t legacy_owners[64000]={0},shadows[64000]={0},owners[64000]={0};
 uint32_t legacy_mask=0,eligible_mask=0;unsigned local_cells=0,bad=0;
 if(family&&tank.contributed&&tank.accepted&&!tank.failed){
  if(!render_mirror_tank194_family_support(legacy_owners,sizeof legacy_owners,shadows,sizeof shadows))abort();
  for(unsigned i=0;i<64000;i++)if(legacy_owners[i]){
   if(legacy_owners[i]<76||legacy_owners[i]>100)abort();
   legacy_mask|=UINT32_C(1)<<(legacy_owners[i]-76);
  }
 }
 for(unsigned i=0;i<25;i++){
  const B313TankFallbackDrawStatus *d=local.draw+i;
  bool eligible=d->complete&&d->current&&d->surviving_cells;
  if(eligible)eligible_mask|=UINT32_C(1)<<i;
  bool used=(local.presented_slots&(UINT32_C(1)<<i))!=0;
  if(used){
   if(!enabled||!local.presenting||!terrain.presenting||family||!eligible||d->slot!=i+75||
      d->x<24||d->x>264||d->y<0||d->y>156)abort();
   uint8_t cells[672];uint32_t patch[43008];
   if(!render_mirror_tank_fallback_sample(i+75,cells,sizeof cells,patch,43008))abort();
   unsigned counted=0;
   for(unsigned ly=0;ly<28;ly++)for(unsigned lx=0;lx<24;lx++){
    if(cells[ly*24+lx]>1)abort();
    if(!cells[ly*24+lx])continue;
    unsigned off=((unsigned)d->y+ly)*320+(unsigned)d->x+lx;
    if(owners[off])abort();owners[off]=(uint8_t)(i+1);++counted;++local_cells;
    for(unsigned sy=0;sy<(unsigned)scale;sy++)for(unsigned sx=0;sx<(unsigned)scale;sx++){
     unsigned x=((unsigned)d->x+lx-24)*scale+sx,y=((unsigned)d->y+ly)*scale+sy;
     unsigned px=lx*8+sx*(8/scale)+(4/scale),py=ly*8+sy*(8/scale)+(4/scale);
     bad+=(pixels[y*w+x]&0xffffffu)!=(patch[py*192+px]&0xffffffu);
    }
   }
   if(!counted||counted!=d->surviving_cells)abort();
  }
  fprintf(slots,"%u,%u,%"PRIu64",%"PRIu64",%"PRIu64",%u,%u,%u,%u,%d,%d,%u,%u,%u,%u\n",tick,i+75,
   d->epoch,d->token,d->generation,eligible,(legacy_mask>>i)&1,used,d->pose,d->x,d->y,d->surviving_cells,d->reason,d->denied,d->callback_count);
 }
 if(local.presenting!=(local.presented_slots!=0)||((legacy_mask&local.presented_slots)!=0))abort();
 /* Independently displayed tank and player masks must be disjoint. */
 if(player_local.presenting){
  uint8_t cells[672];uint32_t patch[43008];
  if(!render_mirror_player_fallback_sample(cells,sizeof cells,patch,43008))abort();
  for(unsigned y=0;y<28;y++)for(unsigned x=0;x<24;x++)if(cells[y*24+x]&&
   owners[((unsigned)player_local.y+y)*320+(unsigned)player_local.x+x])abort();
 }
 uint32_t header[4]={tick,local.presented_slots,local_cells,64000};
 if(enabled){
  if(!mask_stream)mask_stream=open_output("ownership.bin","wb");
  if(fwrite(header,sizeof header,1,mask_stream)!=1||fwrite(owners,sizeof owners,1,mask_stream)!=1||fflush(mask_stream))abort();
 }else{
  if(local.presented_slots)abort();
  if(!mask_stream){mask_stream=fopen(getenv("TANK_FALLBACK_REFERENCE_MASK"),"rb");if(!mask_stream)abort();}
  if(fread(header,sizeof header,1,mask_stream)!=1||fread(owners,sizeof owners,1,mask_stream)!=1||header[0]!=tick||header[3]!=64000)abort();
 }
 uint64_t outside=UINT64_C(14695981039346656037),inside=outside;unsigned owned_pixels=0;
 for(int y=0;y<h;y++)for(int x=0;x<w;x++){
  Uint32 actual=pixels[y*w+x]&0xffffffu;
  if(x<264*scale&&y<184*scale&&owners[(y/scale)*320+x/scale+24]){++owned_pixels;inside=hash_rgb(inside,actual);}
  else outside=hash_rgb(outside,actual);
 }
 if(owned_pixels!=header[2]*(unsigned)scale*(unsigned)scale)abort();
 fprintf(frames,"%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%016"PRIx64",%016"PRIx64",%"PRIu64"\n",tick,
  family,terrain.presenting,family&&ship.draw.accepted&&!ship.draw.failed,player_local.presenting,
  legacy_mask,local.presented_slots,eligible_mask,local_cells,owned_pixels,bad,outside,inside,local.presents);
 if(fflush(frames)||fflush(slots))abort();previous_accepted=scene.accepted_frames;
 bool capture=false;for(unsigned i=0;i<sizeof capture_ticks/sizeof *capture_ticks;i++)capture|=tick==capture_ticks[i];
 if(capture){char name[80];snprintf(name,sizeof name,"frame-%04u.ppm",tick);FILE *out=open_output(name,"wb");
  fprintf(out,"P6\n%d %d\n255\n",w,h);
  for(int i=0;i<w*h;i++){Uint32 p=pixels[i];unsigned char rgb[3]={(unsigned char)(p>>16),(unsigned char)(p>>8),(unsigned char)p};if(fwrite(rgb,1,3,out)!=3)abort();}
  if(fclose(out))abort();}
 free(pixels);++presents;
}
void __real_SDL_RenderPresent(SDL_Renderer *);
void __wrap_SDL_RenderPresent(SDL_Renderer *renderer)
{if(render_mirror_family_status().frames)audit_present(renderer);__real_SDL_RenderPresent(renderer);}
bool original_test_end(void)
{
 static FILE *f;
 if(!f){f=open_output("state.csv","w");fputs("tick,players,enemies,shots,particles,globals,rng,native,output,x,y,inv,armor,shield,family_presents,terrain_presents,player_presents,tank_presents,presents\n",f);}
 fprintf(f,"%u,",tick);original_test_state(f);
 fprintf(f,",%d,%d,%u,%u,%u,%"PRIu64",%"PRIu64",%"PRIu64",%"PRIu64",%u\n",player[0].x,player[0].y,
  player[0].invulnerable_ticks,player[0].armor,player[0].shield,render_mirror_family_status().presents,
  render_mirror_terrain_fallback_status().presents,render_mirror_player_fallback_status().presents,
  render_mirror_tank_fallback_status().presents,presents);
 if(fflush(f))abort();
 bool done=++tick>=(unsigned)strtoul(getenv("ORIGINAL_TEST_TICKS"),NULL,10);
 if(done&&mask_stream&&!getenv("BUILDING313_TANK_FALLBACK_ENABLE")&&fgetc(mask_stream)!=EOF)abort();
 return done;
}
