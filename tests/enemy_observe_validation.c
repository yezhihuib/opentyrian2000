/* Native production-object session test. Deliberate fixture state setup is
 * confined to this harness; this is NOT original-event game-loop acceptance. */
#include "native_p09_observer_helpers.inc"
#include "enemy_reuse_observe.h"
#include "params.h"
static void observe_setup(unsigned profile)
{
 p09_setup(profile);
 game_probe_enabled=false;game_probe_assets=NULL;
 render_mirror_hud_start(VGAScreenSeg);
 CHECK(enemy_reuse_observe_requested());CHECK(enemy_reuse_observe_active());
 CHECK(!mirror_enabled());CHECK(!hud_gameplay&&!shared_hud_lease);
 render_mirror_begin();CHECK(active&&!reject_reason);
 CHECK(!global_talon_frame&&!global_green_frame&&!global_newshf_frame);
}
static void observe_modes(void)
{
 for(unsigned mode=0;mode<19;mode++){
  observe_setup(0);p09_spawn();p05_update();CHECK(enemy_reuse_frame.contributed);
  switch(mode){
   case 0:play_demo=true;break;case 1:record_demo=true;break;
   case 2:twoPlayerMode=true;break;case 3:galagaMode=true;break;
   case 4:twoPlayerLinked=true;break;case 5:isNetworkGame=true;break;
   case 6:onePlayerAction=true;break;case 7:superTyrian=true;break;
   case 8:superArcadeMode=1;break;case 9:timedBattleMode=true;break;
   case 10:bonusLevel=true;break;case 11:normalBonusLevelCurrent=true;break;
   case 12:bonusLevelCurrent=true;break;case 13:episodeNum=1;break;
   case 14:lvlFileNum=2;break;case 15:constantPlay=true;break;case 16:constantDie=true;break;case 17:richMode=true;break;case 18:xmas=true;break;
  }
  CHECK(!enemy_reuse_observe_active());finish();CHECK(!ready&&!last_output_valid);
  play_demo=record_demo=twoPlayerMode=galagaMode=twoPlayerLinked=isNetworkGame=false;
  onePlayerAction=superTyrian=timedBattleMode=bonusLevel=normalBonusLevelCurrent=bonusLevelCurrent=false;superArcadeMode=SA_NONE;constantPlay=constantDie=richMode=xmas=false;
 }
}
static void observe_roles(void)
{
 observe_setup(0);p09_spawn();unsigned n=draws;
 Uint8 rgba[4]={255,255,255,255};
 for(int role=0;role<150;role++)if(role!=146){
  Asset a={true,true,role,227,1,1,0,0,8,rgba};
  CHECK(!draw_asset_filtered(100,80,&a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));
 }
 CHECK(draws==n&&!enemy_reuse_frame.contributed);
 draw_player_shot_sprite2(game_screen,100,80,spriteSheet8,227,0,227);
 draw_enemy_shot_sprite2(game_screen,100,80,spriteSheet8,227);
 CHECK(draws==n&&!enemy_reuse_frame.contributed);
 p05_update();CHECK(draws==n+1&&enemy_reuse_frame.contributed);
 finish();CHECK(last_output_valid&&!reject_reason);
}
static void observe_mutations(void)
{
 for(unsigned bad=0;bad<5;bad++){
  observe_setup(0);p09_spawn();p05_update();CHECK(enemy_reuse_frame.contributed);
  Uint8 saved=bank_bytes[100];
  switch(bad){
   case 0:bank_bytes[100]^=1;break;
   case 1:enemy_reuse_resources.members[10].rgba[31]^=1;break;
   case 2:rgb_palette[0]^=1;break;
   case 3:weapons[141].sound++;break;
   case 4:enemy_reuse_actor_allocated(enemy,133,0);break;
  }
  finish();CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);bank_bytes[100]=saved;
 }
}
static void observe_lifecycle(void)
{
 /* A revoked lease cannot retain an empty scene/cache either. */
 observe_setup(0);CHECK(!enemy_reuse_frame.contributed);play_demo=true;
 finish();CHECK(!ready&&!last_output_valid&&!enemy_reuse_observe_active());play_demo=false;
 observe_setup(0);CHECK(!enemy_reuse_frame.contributed);record_demo=true;
 CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!enemy_reuse_observe_active());record_demo=false;
 observe_setup(0);p09_spawn();p05_update();finish();CHECK(last_output_valid);
 render_mirror_hud_reset();CHECK(!enemy_reuse_observe_active());
 render_mirror_hud_start(VGAScreenSeg);CHECK(enemy_reuse_observe_active());CHECK(!enemy_reuse_identity_generation(0));
 enemy_reuse_observe_reset();
 CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 observe_setup(0);p09_spawn();p05_update();finish();CHECK(last_output_valid);
 enemy_reuse_bank_changed(&spriteSheet8);CHECK(!enemy_reuse_identity_generation(0));
 CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));
 observe_setup(0);p09_spawn();p05_update();finish();CHECK(last_output_valid);
 render_mirror_hud_shutdown();CHECK(!enemy_reuse_observe_active());
 CHECK(!enemy_reuse_identity_generation(0));
}
/* Use the actual game_screen -> VGAScreenSeg phase transition, not the
 * legacy fixture helper's game-surface alias. */
static void observe_output_alias(void)
{
 for(unsigned profile=0;profile<2;profile++){
  observe_setup(profile);uint64_t generation=enemy_reuse_observe_generation();
  CHECK(generation&&!enemy_reuse_probe_generation());p09_spawn();
  Uint32 *want=canvas_copy();p05_update();
  for(unsigned i=0;i<(profile?3u:1u);i++)p09_oracle(want,i);
  /* Final-surface alias must not authorize a draw before finish. */
  VGAScreen=VGAScreenSeg;unsigned n=draws;
  EnemyShotType *shot=&enemyShot[0];
  CHECK(!render_mirror_enemy_reuse_shot(game_screen,shot->sx,shot->sy,spriteSheet8,shot->sgr+shot->animate,0,shot->sgr));
  CHECK(draws==n&&!enemy_reuse_frame.output_phase);
  verify_rgb(want);free(want);CHECK(enemy_reuse_cache_check());
  SDL_Surface *screen=SDL_CreateRGBSurfaceWithFormat(0,output->w,output->h,32,SDL_PIXELFORMAT_ARGB8888);CHECK(screen);
  SDL_Renderer *renderer=SDL_CreateSoftwareRenderer(screen);CHECK(renderer);
  uint64_t rng=mt_state_fingerprint();CHECK(!game_probe_skip);
  CHECK(render_mirror_present(renderer,VGAScreenSeg,NULL));CHECK(mt_state_fingerprint()==rng);
  for(int y=0;y<output->h;y++)CHECK(!memcmp((Uint8 *)screen->pixels+y*screen->pitch,(Uint8 *)output->pixels+y*output->pitch,output->w*4));
  CHECK(enemy_reuse_cache_check()&&enemy_reuse_observe_generation()==generation);
  /* A valid session cannot return to drawing after the output phase. */
  VGAScreen=game_screen;p05_update();CHECK(draws==n);
  SDL_DestroyTexture(texture);texture=NULL;SDL_DestroyRenderer(renderer);SDL_FreeSurface(screen);
 }
}
static void observe_output_negatives(void)
{
 for(unsigned cached=0;cached<2;cached++)for(unsigned bad=0;bad<26;bad++){
  observe_setup(0);p09_spawn();p05_update();final_copy();VGAScreen=VGAScreenSeg;
  if(cached){render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);CHECK(last_output_valid&&enemy_reuse_cache_check());}
  SDL_Surface *gs=game_screen,*fs=VGAScreenSeg;
  void *gp=gs->pixels,*fp=fs->pixels;SDL_PixelFormat *gf=gs->format,*ff=fs->format;
  SDL_Surface *other=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);CHECK(other);
  uint64_t generation=enemy_reuse_observe_generation();
  switch(bad){
   case 0:VGAScreen=other;break;
   case 1:gs->pixels=other->pixels;break;case 2:fs->pixels=other->pixels;break;
   case 3:gs->format=other->format;break;case 4:fs->format=other->format;break;
   case 5:game_screen=other;break;case 6:VGAScreenSeg=other;break;
   case 7:gs->w--;break;case 8:fs->h--;break;
   case 9:gs->pitch--;break;case 10:fs->pitch--;break;
   case 11:gf->format=SDL_PIXELFORMAT_RGB332;break;
   case 12:ff->BytesPerPixel=2;break;
   case 13:enemy_reuse_observe_reset();CHECK(!enemy_reuse_observe_generation());break;
   case 14:enemy_reuse_observe_start();CHECK(enemy_reuse_observe_generation()!=generation);break;
   case 15:game_probe_enabled=true;CHECK(!enemy_reuse_observe_generation());break;
   case 16:record_demo=true;break;case 17:play_demo=true;break;
   case 18:episodeNum=1;break;case 19:lvlFileNum=2;break;
   case 20:gs->h--;break;case 21:fs->w--;break;
   case 22:gf->BitsPerPixel=7;break;case 23:ff->BitsPerPixel=7;break;
   case 24:gf->BytesPerPixel=2;break;case 25:ff->format=SDL_PIXELFORMAT_RGB332;break;
  }
  if(!cached)render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);
  CHECK(!render_mirror_present(NULL,VGAScreenSeg,NULL));CHECK(!ready&&!last_output_valid&&!last_output_scene_hd);
  game_screen=gs;VGAScreenSeg=fs;gs->pixels=gp;fs->pixels=fp;gs->format=gf;fs->format=ff;VGAScreen=gs;
  gs->w=fs->w=320;gs->h=fs->h=200;gs->pitch=fs->pitch=320;
  gf->format=ff->format=SDL_PIXELFORMAT_INDEX8;gf->BytesPerPixel=ff->BytesPerPixel=1;gf->BitsPerPixel=ff->BitsPerPixel=8;
  game_probe_enabled=play_demo=record_demo=false;SDL_FreeSurface(other);
 }
 /* Same-tick restart invalidates even an empty captured frame. */
 observe_setup(0);uint64_t generation=enemy_reuse_observe_generation();
 enemy_reuse_observe_reset();CHECK(!enemy_reuse_observe_generation());
 enemy_reuse_observe_start();CHECK(enemy_reuse_observe_generation()&&enemy_reuse_observe_generation()!=generation);
 CHECK(!enemy_reuse_proof());finish();CHECK(!ready&&!last_output_valid);
 /* An unleased normal frame cannot borrow a newly started normal session. */
 observe_setup(0);enemy_reuse_observe_reset();render_mirror_begin();
 enemy_reuse_observe_start();CHECK(enemy_reuse_observe_generation());CHECK(!enemy_reuse_proof());
 /* Unsupported start/getter never mint authority. */
 enemy_reuse_observe_reset();play_demo=true;enemy_reuse_observe_start();CHECK(!enemy_reuse_observe_generation());play_demo=false;
 CHECK(!enemy_reuse_observe_generation());
}
int main(int argc,char **argv)
{
 CHECK(legacy_p09_main(argc,argv)==0);
 /* Uncontracted legacy probes still draw on the original game surface, but
  * cannot borrow either explicit session's final-output alias permission. */
 p09_setup(0);p09_spawn();p05_update();CHECK(enemy_reuse_frame.contributed);
 CHECK(!enemy_reuse_probe_requested()&&!enemy_reuse_observe_requested());
 VGAScreen=VGAScreenSeg;finish();CHECK(!ready&&!last_output_valid);
 VGAScreen=game_screen;
 game_probe_enabled=false;game_probe_assets=NULL;
 const char *resource_case=getenv("ENEMY_OBSERVE_RESOURCE_CASE");
 char selected_root[4096];CHECK(snprintf(selected_root,sizeof(selected_root),"%s%s%s",valid_root,resource_case?"/":"",resource_case?resource_case:"")<(int)sizeof(selected_root));
 char option[8192];CHECK(snprintf(option,sizeof(option),"--enemy-reuse-observe-assets=%s",selected_root)<(int)sizeof(option));
 char *args[]={argv[0],option,NULL};int count=2;game_probe_parse(&count,args);
 CHECK(count==1&&!game_probe_enabled&&!game_probe_assets&&game_probe_density==8);
 CHECK(enemy_reuse_observe_requested()&&!enemy_reuse_observe_active());
 if(resource_case){
  observe_setup(0);p09_spawn();p05_update();CHECK(!enemy_reuse_frame.contributed&&draws==0);
  finish();CHECK(!last_output_valid);printf("PASS observer independent root failure: %s\n",resource_case);return 0;
 }
 for(unsigned p=0;p<2;p++){
  observe_setup(p);p09_spawn();Uint32 *want=canvas_copy();p05_update();
  CHECK(draws==(p?3u:1u));for(unsigned i=0;i<(p?3u:1u);i++)p09_oracle(want,i);
  VGAScreen=VGAScreenSeg;verify_rgb(want);free(want);finish();CHECK(last_output_valid&&!reject_reason);
 }
 observe_modes();observe_roles();observe_mutations();observe_lifecycle();
 observe_output_alias();observe_output_negatives();
 printf("PASS non-probe observer native session: %u setups, %u assertions; not original-event gameplay acceptance\n",cases,checks);
 return 0;
}
