/* Real renderer unit adapter. No engine main, gameplay loop or SDL window. */
#include "render_mirror.c"
#include <assert.h>
static unsigned int policy_calls;
bool __real_forest13_policy_check(const char *directory);
bool __wrap_forest13_policy_check(const char *directory)
{++policy_calls;return __real_forest13_policy_check(directory);}

int manual_render_test(const char *directory,int head_ok,int talon_ok)
{
 manual_hd_enabled=true;game_probe_assets=directory;game_probe_density=8;
 game_probe_local_blend=game_probe_known_blend=true;game_probe_scene_assets=3;
 episodeNum=1;lvlFileNum=9;
 static Uint8 ship_data,bullet_data;
 spriteSheet9.data=&ship_data;spriteSheet8.data=&bullet_data;
 VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);
 assert(VGAScreenSeg&&game_screen);
 for(int i=0;i<256;i++)rgb_palette[i]=(Uint32)i*0x010101u;
 assert(manual_hd_scope()&&!mirror_enabled()); /* Stale title globals confer no lease. */
 render_mirror_player_pose(1,spriteSheet9,233,237,0);
 assert(!assets[0].initialized&&!talon_frames[1].initialized);
 render_mirror_begin();assert(!active&&!have_initial_palette);
 render_mirror_ground101_layer1(game_screen,NULL,0,0);assert(policy_calls==0);
 render_mirror_hud_start(NULL);assert(!manual_hd_lease);
 render_mirror_hud_start(game_screen);assert(!manual_hd_lease);
 VGAScreenSeg->w=319;render_mirror_hud_start(VGAScreenSeg);assert(!manual_hd_lease);VGAScreenSeg->w=320;
 int pitch=VGAScreenSeg->pitch;VGAScreenSeg->pitch=319;render_mirror_hud_start(VGAScreenSeg);assert(!manual_hd_lease);VGAScreenSeg->pitch=pitch;
 render_mirror_hud_start(VGAScreenSeg);assert(manual_hd_lease&&mirror_enabled());
 /* The deliberately missing/incompatible optional HUD never blocks scene art. */
 assert(!hud_gameplay);
 render_mirror_ground101_layer1(game_screen,NULL,0,0);assert(policy_calls==1);
 render_mirror_begin();assert(active&&have_initial_palette);
 assert((get_asset(spriteSheet8,59,ENTITY_TILE)!=NULL)==head_ok);
 assert((talon_frames_ready()!=0)==talon_ok);
 render_mirror_player_pose(1,spriteSheet9,233,237,0);
 if(talon_ok) {
  assert(talon_banks[0].valid&&talon_banks[0].visual_index==6);
  render_mirror_player_pose(1,spriteSheet9,233,237,0);assert(talon_banks[0].visual_index==6);
  render_mirror_begin();render_mirror_player_pose(1,spriteSheet9,233,237,0);
  assert(talon_banks[0].visual_index==7&&game_probe_tick==0);
  ready=false;assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));
  assert(talon_banks[0].visual_index==7); /* Present cannot advance banking. */
 }
 render_mirror_hud_suspend();assert(manual_hd_lease);
 render_mirror_release_texture();assert(manual_hd_lease&&!ready&&!talon_banks[0].valid);
 render_mirror_begin();assert(active);render_mirror_finish(true);
 assert(ready&&!reject_reason); /* Missing art still completes the classic mirror. */
 SDL_Color black={0,0,0,255};
 /* A finite synthetic display sample exercises the unchanged in-level fade. */
 ((Uint32 *)output->pixels)[0]=0xff808080u;hd_owner[24*8]=1;last_output_valid=true;
 render_mirror_fade_start(NULL,&black,0,255);assert(fade_mode==1&&have_fade_saved);
 render_mirror_fade_step(2);assert(ready&&((Uint32 *)output->pixels)[0]==0xff404040u);
 render_mirror_fade_step(1);assert(((Uint32 *)output->pixels)[0]==0xff000000u);
 ready=active=last_output_valid=have_fade_saved=have_initial_palette=true;fade_mode=1;
 render_mirror_hud_reset();assert(!manual_hd_lease&&!active&&!ready&&!last_output_valid&&!have_fade_saved&&!have_initial_palette&&!fade_mode);
 render_mirror_hud_reset();assert(!mirror_enabled());
 rgb_palette[12]^=0x010101u;render_mirror_hud_start(VGAScreenSeg);render_mirror_begin();
 assert(active&&initial_palette[12]==rgb_palette[12]);
 rgb_palette[12]^=0x020202u;render_mirror_finish(true);assert(reject_reason&&strstr(all_rejections,"hd-palette-change"));
 /* Every scope exclusion revokes pending scene ownership. */
 for(int which=0;which<7;which++) {
  render_mirror_hud_start(VGAScreenSeg);assert(mirror_enabled());
  switch(which){case 0:episodeNum=2;break;case 1:lvlFileNum=10;break;case 2:isNetworkGame=true;break;case 3:twoPlayerMode=true;break;case 4:galagaMode=true;break;case 5:play_demo=true;break;case 6:record_demo=true;break;}
  assert(!manual_hd_scope());ready=last_output_valid=have_fade_saved=true;fade_mode=1;
  assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));assert(!manual_hd_lease&&!ready&&!fade_mode);
  render_mirror_hud_start(VGAScreenSeg);assert(!manual_hd_lease);
  render_mirror_begin();assert(!active);
  render_mirror_fade_step(1);assert(!ready);
  episodeNum=1;lvlFileNum=9;isNetworkGame=twoPlayerMode=galagaMode=play_demo=record_demo=false;
  assert(!mirror_enabled());
 }
 /* Diagnostic reset historically retains scene/fade/palette state. */
 manual_hd_enabled=false;game_probe_enabled=true;
 ready=active=last_output_valid=have_fade_saved=have_initial_palette=true;fade_mode=2;
 render_mirror_hud_reset();assert(ready&&active&&last_output_valid&&have_fade_saved&&have_initial_palette&&fade_mode==2);
 game_probe_enabled=false;assert(!mirror_enabled());
 puts("renderer lease/scope/reset/fade/fallback/banking units passed");return 0;
}
