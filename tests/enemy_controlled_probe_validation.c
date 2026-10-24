/* Native fixture-only phase tests plus exact private session unit tests.
 * No harness spawn is reported as original-event acceptance. */
#include "native_p09_observer_helpers.inc"
void enemy_controlled_probe_fixture_start(void);
void enemy_controlled_probe_fixture_profile_change(void);
static void controlled_setup(void)
{
 p09_setup(0);enemy_controlled_probe_fixture_start();
 CHECK(enemy_reuse_probe_requested()&&enemy_reuse_probe_generation());
 render_mirror_begin();p09_spawn();p05_update();CHECK(enemy_reuse_frame.contributed);
}
static void output_alias(void)
{
 controlled_setup();Uint32 *want=canvas_copy();
 VGAScreen=VGAScreenSeg;verify_rgb(want);free(want);
 CHECK(last_output_valid&&enemy_reuse_cache_check());
 /* Returning to draw after finish cannot borrow the output-phase permission. */
 VGAScreen=game_screen;unsigned n=draws;p05_update();CHECK(draws==n);
 enemy_reuse_probe_revoke();CHECK(!enemy_reuse_cache_check()&&!last_output_valid&&!ready);
}
static void output_negatives(void)
{
 for(unsigned bad=0;bad<11;bad++){
  controlled_setup();SDL_Surface *gs=game_screen,*fs=VGAScreenSeg;
  void *gp=gs->pixels,*fp=fs->pixels;SDL_PixelFormat *gf=gs->format,*ff=fs->format;
  SDL_Surface *other=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(other);
  VGAScreen=fs;
  switch(bad){
   case 0:VGAScreen=other;break;
   case 1:gs->pixels=other->pixels;break;
   case 2:fs->pixels=other->pixels;break;
   case 3:gs->format=other->format;break;
   case 4:fs->format=other->format;break;
   case 5:game_screen=other;break;
   case 6:VGAScreenSeg=other;break;
   case 7:enemy_reuse_probe_revoke();break;
   case 8:record_demo=true;break;
   case 9:enemy_controlled_probe_fixture_profile_change();break;
   case 10:enemy_controlled_probe_fixture_start();break; /* new generation */
  }
  render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(!ready&&!last_output_valid);
  CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));
  game_screen=gs;VGAScreenSeg=fs;gs->pixels=gp;fs->pixels=fp;gs->format=gf;fs->format=ff;VGAScreen=gs;record_demo=false;
  enemy_reuse_probe_revoke();SDL_FreeSurface(other);
 }
 /* Same original assets/level/demo flag without a live contract cannot draw. */
 p09_setup(0);play_demo=true;enemy_reuse_probe_revoke();render_mirror_begin();p09_spawn();p05_update();CHECK(!enemy_reuse_frame.contributed);
}
int main(int argc,char **argv)
{
 CHECK(legacy_p09_main(argc,argv)==0);
 char *args[]={argv[0],"--asset-debug=custom","--asset-debug-reference",NULL};int count=3;asset_debug_parse(&count,args);
 output_alias();output_negatives();
 printf("PASS explicit controlled probe fixture contract/owner/output phases: %u assertions; not original-event gameplay acceptance\n",checks);
 return 0;
}
