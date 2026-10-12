/* Reuse SDL stubs and unchanged production-helper extraction, not a renderer
 * rewrite. This test never uses screenshots, original data or final artwork. */
#define main existing_hud_test_main
#include "../gameplay-hud/test_renderer.c"
#undef main

static Uint8 pristine[64000], exact_mask[64000];
static int textErase;
typedef int8_t Sint8;
#define MIRROR_NORMAL 0
static bool sprite_exists(unsigned table,unsigned index)
{return index<sprite_table[table].count&&sprite_table[table].sprite[index].data;}
static Sprite *sprite(unsigned table,unsigned index) {return &sprite_table[table].sprite[index];}
static void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style) {(void)s;(void)p;(void)v;(void)style;}
static void blit_sprite_dark(SDL_Surface *s,int x,int y,unsigned table,unsigned index,bool dark) {assert(false);}
/* Only the unchanged classic eraser is modeled: its exact audited footprint is
 * [16,189,244,198). The text layout and unsafe RLE writer below are production. */
static void blit_sprite(SDL_Surface *s,int x,int y,unsigned table,unsigned index)
{
 assert(s==VGAScreenSeg&&x==16&&y==189&&table==OPTION_SHAPES&&index==36);
 for(int row=189;row<198;row++)memcpy((Uint8 *)s->pixels+row*s->pitch+16,pristine+row*320+16,228);
}
#include "message-writers.inc"

static bool in_corner(int x,int y) {return x>=248&&x<269&&y>=184&&y<200;}
static void corner_setup(const char *directory,int density)
{
 setup(density,directory);valid_bindings();expanded_test=true;textErase=0;
 read_fixture(directory,"source.indices",pristine,64000);
 read_fixture(directory,"synthetic.mask",exact_mask,64000);
 memcpy(VGAScreenSeg->pixels,pristine,64000);memcpy(expansion_mask,exact_mask,64000);
 render_mirror_hud_start(VGAScreenSeg);assert(hud_gameplay&&gameplay_hud_ready());
}
static void check_corner(bool visible,bool scene)
{
 int d=game_probe_density;unsigned count=0;
 for(int y=0;y<200;y++)for(int x=0;x<320;x++) {
  Uint8 index=((Uint8 *)VGAScreenSeg->pixels)[y*VGAScreenSeg->pitch+x];
  bool owned=exact_mask[y*320+x]&&index==pristine[y*320+x]&&(!in_corner(x,y)||visible);
  assert(hud_output_owner[y*320+x]==owned);if(in_corner(x,y))count+=owned;
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   Uint32 want=owned?authored(x,y,sx,sy,d):palette_rgb(index);
   if(x<264&&y<184)want=palette_rgb(((Uint8 *)game_screen->pixels)[y*320+x+24]);
   if(scene&&x*d+sx==30*d&&y*d+sy==20*d)want=0xffdc51a3u;
   assert(*pixel(output,x*d+sx,y*d+sy)==want);
  }
 }
 assert(count==(visible?336u:0u));
}
static void digest_state(void)
{
 digest(output->pixels,(size_t)output->pitch*output->h);
 digest(hud_output_owner,sizeof(hud_output_owner));digest(hud_saved_owner,sizeof(hud_saved_owner));
 digest(&last_output_valid,sizeof(last_output_valid));digest(&have_fade_saved,sizeof(have_fade_saved));
 digest(&fade_mode,sizeof(fade_mode));digest(&ready,sizeof(ready));
 if(have_fade_saved)digest(fade_saved->pixels,(size_t)fade_saved->pitch*fade_saved->h);
}
static void legacy_equivalence(const char *directory,int d)
{
 corner_setup(directory,d);frame(true,true);check_frame(true,true);digest_state();
 unsigned count=0;for(int i=0;i<64000;i++)count+=hud_output_owner[i];assert(count==6667);
 Uint32 saved_palette[256];memcpy(saved_palette,rgb_palette,sizeof(saved_palette));
 for(unsigned solid=0;solid<=255;solid+=255) {
  SDL_Color target={solid,solid,solid,255};render_mirror_fade_start(NULL,&target,0,255);digest_state();
  for(int step=3;step;step--) {palette_step(solid,step,NULL);render_mirror_fade_step(step);digest_state();}
  SDL_Color restore[256];for(int i=0;i<256;i++)restore[i]=(SDL_Color){saved_palette[i]>>16,saved_palette[i]>>8,saved_palette[i],255};
  render_mirror_fade_start(restore,NULL,0,255);
  for(int step=3;step;step--) {palette_step(0,step,saved_palette);render_mirror_fade_step(step);digest_state();}
  check_frame(true,true);if(solid==255)break;
 }
 render_mirror_hud_suspend();digest_state();check_frame(false,true);
 frame(true,true);check_frame(true,true);digest_state();
 JE_drawTextWindow("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");frame(true,true);digest_state();
 JE_drawTextWindow("A");frame(true,true);digest_state();
 render_mirror_release_texture();digest_state();frame(true,true);digest_state();
 render_mirror_hud_reset();digest_state();
}
#ifndef CORNER_BASELINE
static void corner_suite(const char *directory,int d)
{
 corner_setup(directory,d);frame(true,true);check_corner(true,true);
 unsigned count=0;for(int i=0;i<64000;i++)count+=hud_output_owner[i];assert(count==6853);
 unsigned old_allocations=allocations;frame(true,true);assert(old_allocations==allocations);check_corner(true,true);
 const int altered[][2]={{248,184},{268,184},{248,199},{268,199},{248,190},{267,191}};
 for(unsigned k=0;k<sizeof(altered)/sizeof(altered[0]);k++) {
  int at=altered[k][1]*320+altered[k][0];((Uint8 *)VGAScreenSeg->pixels)[at]^=1;
  frame(true,true);check_corner(false,true);
  ((Uint8 *)VGAScreenSeg->pixels)[at]^=1;frame(true,true);check_corner(true,true);
 }
 /* Production JE_outText + unsafe RLE writes can cross into the corner.
  * A shorter next message erases only the normal text area: its tail persists. */
 JE_drawTextWindow("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");frame(true,true);check_corner(false,true);
 Uint8 tail[336];unsigned at=0,changed=0;
 for(int y=184;y<200;y++)for(int x=248;x<269;x++) {
  tail[at++]=((Uint8 *)VGAScreenSeg->pixels)[y*320+x];changed+=tail[at-1]!=pristine[y*320+x];
 }
 assert(changed>0);JE_drawTextWindow("A");frame(true,true);check_corner(false,true);
 at=0;for(int y=184;y<200;y++)for(int x=248;x<269;x++)assert(((Uint8 *)VGAScreenSeg->pixels)[y*320+x]==tail[at++]);
 /* Simulate message expiry's same original eraser; no presentation cleanup. */
 blit_sprite(VGAScreenSeg,16,189,OPTION_SHAPES,36);frame(true,true);check_corner(false,true);
 at=0;for(int y=184;y<200;y++)for(int x=248;x<269;x++)assert(((Uint8 *)VGAScreenSeg->pixels)[y*320+x]==tail[at++]);
 Uint32 text_palette[256];memcpy(text_palette,rgb_palette,sizeof(text_palette));
 SDL_Color text_black={0,0,0,255};render_mirror_fade_start(NULL,&text_black,0,255);
 for(int step=2;step;step--) {
  palette_step(0,step,NULL);render_mirror_fade_step(step);
  at=0;for(int y=184;y<200;y++)for(int x=248;x<269;x++) {
   assert(!hud_output_owner[y*320+x]&&!hud_saved_owner[y*320+x]);
   assert(((Uint8 *)VGAScreenSeg->pixels)[y*320+x]==tail[at]);
   for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)
    assert(*pixel(output,x*d+sx,y*d+sy)==palette_rgb(tail[at]));
   ++at;
  }
 }
 SDL_Color text_restore[256];for(int i=0;i<256;i++)text_restore[i]=(SDL_Color){text_palette[i]>>16,text_palette[i]>>8,text_palette[i],255};
 render_mirror_fade_start(text_restore,NULL,0,255);
 for(int step=2;step;step--){palette_step(0,step,text_palette);render_mirror_fade_step(step);}
 check_corner(false,true);render_mirror_hud_suspend();frame(true,true);check_corner(false,true);
 render_mirror_release_texture();frame(true,true);check_corner(false,true);
 /* Restore only by a real pristine source grant, never by HUD composition. */
 corner_setup(directory,d);frame(true,true);check_corner(true,true);
 Uint32 saved_palette[256];memcpy(saved_palette,rgb_palette,sizeof(saved_palette));
 for(unsigned solid=0;solid<=255;solid+=255) {
  SDL_Color target={solid,solid,solid,255};render_mirror_fade_start(NULL,&target,0,255);
  assert(have_fade_saved&&fade_mode==(solid?2:1));
  for(int step=3;step;step--) {
   Uint32 prior=*pixel(output,248*d,190*d);
   palette_step(solid,step,NULL);render_mirror_fade_step(step);
   assert(*pixel(output,248*d,190*d)==channel_step(prior,solid?0xffffffffu:0xff000000u,step));
   assert(sample_hd==6853u*d*d+1);
  }
  SDL_Color restore[256];for(int i=0;i<256;i++)restore[i]=(SDL_Color){saved_palette[i]>>16,saved_palette[i]>>8,saved_palette[i],255};
  render_mirror_fade_start(restore,NULL,0,255);
  for(int step=3;step;step--){palette_step(0,step,saved_palette);render_mirror_fade_step(step);}
  check_corner(true,true);
  frame(true,true);render_mirror_fade_start(NULL,&target,0,255);
  palette_step(solid,3,NULL);render_mirror_fade_step(3);
  Uint32 current_scene=*pixel(output,30*d,20*d),saved_scene=*pixel(fade_saved,30*d,20*d);
  render_mirror_hud_suspend();render_mirror_hud_suspend();
  assert(hud_suspended&&have_fade_saved&&last_output_valid);
  assert(*pixel(output,30*d,20*d)==current_scene&&*pixel(fade_saved,30*d,20*d)==saved_scene);
  for(int y=184;y<200;y++)for(int x=248;x<269;x++)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   assert(!hud_output_owner[y*320+x]&&!hud_saved_owner[y*320+x]);
   assert(*pixel(output,x*d+sx,y*d+sy)==palette_rgb(pristine[y*320+x]));
   assert(*pixel(fade_saved,x*d+sx,y*d+sy)==(0xff000000u|saved_palette[pristine[y*320+x]]));
  }
  memcpy(rgb_palette,saved_palette,sizeof(saved_palette));frame(true,true);check_corner(true,true);
  if(solid==255)break;
 }
 SDL_Color black={0,0,0,255};
 for(int boundary=0;boundary<3;boundary++) {
  corner_setup(directory,d);frame(true,true);
  if(boundary==1)render_mirror_fade_start(NULL,&black,0,255);
  ((Uint8 *)VGAScreenSeg->pixels)[190*320+248]^=1;
  if(boundary==0)render_mirror_fade_start(NULL,&black,0,255);
  if(boundary==1)render_mirror_fade_step(2);
  if(boundary==2)assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
  assert(!ready&&!last_output_valid&&!fade_mode);
  frame(true,true);check_corner(false,true);
 }
 /* Lease revocation, mode change and rejected output still dominate geometry. */
 corner_setup(directory,d);frame(true,true);render_mirror_release_texture();
 assert(hud_suspended&&hud_gameplay);frame(true,true);check_corner(true,true);
 render_mirror_begin();scene_pixel();twoPlayerMode=true;render_mirror_finish(true);
 assert(!hud_gameplay&&!memchr(hud_output_owner,1,64000));twoPlayerMode=false;
 frame(true,true);assert(!memchr(hud_output_owner,1,64000));
 corner_setup(directory,d);frame(true,false);assert(!memchr(hud_output_owner,1,64000));
 corner_setup(directory,d);frame(true,true);VGAScreenSeg->pitch++;
 render_mirror_hud_suspend();assert(!hud_gameplay&&!ready&&!last_output_valid);VGAScreenSeg->pitch--;
}
#endif
int main(int argc,char **argv)
{
 assert(argc==2);char legacy[2048],corner[2048];
 assert(snprintf(legacy,sizeof(legacy),"%s/legacy",argv[1])<(int)sizeof(legacy));
 assert(snprintf(corner,sizeof(corner),"%s/corner",argv[1])<(int)sizeof(corner));
 for(int d=4;d<=8;d+=4)legacy_equivalence(legacy,d);
 printf("LEGACY %016llx\n",(unsigned long long)aggregate);
#ifndef CORNER_BASELINE
 for(int d=4;d<=8;d+=4)corner_suite(corner,d);
 puts("PASS: 4x/8x atomic composition; production long-text/short-text/expiry tails; black/white restoration; modal/cache/fade/lease/mode guards.");
#endif
 cleanup();return 0;
}
