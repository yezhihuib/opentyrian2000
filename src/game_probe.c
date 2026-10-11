/* SPDX-License-Identifier: GPL-2.0-or-later
 * Opt-in bounded scene; does not play or alter any bundled demo file.
 */
#include "game_probe.h"
#include "asset_debug.h"
#include "backgrnd.h"
#include "config.h"
#include "episodes.h"
#include "mainint.h"
#include "mtrand.h"
#include "palette.h"
#include "player.h"
#include "shots.h"
#include "varz.h"
#include "video.h"
#include "render_mirror.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool game_probe_enabled;
int game_probe_density = 1;
bool game_probe_missing, game_probe_repeat, game_probe_invalid;
bool game_probe_coverage_fault;
bool game_probe_skip;
bool game_probe_local_blend;
bool game_probe_original_reference;
unsigned int game_probe_scene_assets;
bool game_probe_known_blend,game_probe_blend_capture;
const char *game_probe_assets;
unsigned int game_probe_tick;
static unsigned int tick_limit = 600;
static FILE *trace, *collisions, *frames, *presentations, *effects, *projectiles, *fade_steps;
static FILE *poses, *fire_events, *player_projectiles, *draw_commands;
static FILE *scene_draw_commands;
static FILE *scene_enemies,*scene_hits;
static FILE *rgb_audits;
static FILE *blend_writes;
static FILE *restore_regions,*blend_palette;
static bool blend_palette_recorded;
static bool sdl_runtime_recorded;
static unsigned int last_scene_hit_tick=UINT32_MAX;
static bool enemy_hit_scene;
static bool fade_cycle_scene;
static bool banking_scene;
static bool capture_pose_change;
static int previous_pose;
static unsigned int fade_sequence;
static unsigned int last_enemy_hit_tick=UINT32_MAX;
static unsigned int hits;
static uint64_t hit_hash = UINT64_C(14695981039346656037);
#define HASH_START UINT64_C(14695981039346656037)
#define H(v) h = game_probe_hash(h, &(v), sizeof(v))
#define F(p,v) H((p)->v)

uint64_t game_probe_hash(uint64_t h, const void *data, size_t size)
{
 const unsigned char *p = data;
 while (size--) { h ^= *p++; h *= UINT64_C(1099511628211); }
 return h;
}

static uint64_t players_hash(void)
{
 uint64_t h=HASH_START;
 for(int i=0;i<2;i++) {
  const Player *p=&player[i];
  F(p,cash); F(p,items); F(p,last_items); F(p,is_dragonwing);
  Uint8 lives=p->lives?*p->lives:0; H(lives);
  F(p,shield_max); F(p,initial_armor); F(p,shot_hit_area_x); F(p,shot_hit_area_y);
  F(p,is_alive); F(p,invulnerable_ticks); F(p,exploding_ticks); F(p,shield); F(p,armor);
  F(p,weapon_mode); F(p,superbombs); F(p,purple_balls_needed); F(p,x); F(p,y);
  F(p,old_x); F(p,old_y); F(p,x_velocity); F(p,y_velocity); F(p,x_friction_ticks); F(p,y_friction_ticks);
  F(p,delta_x_shot_move); F(p,delta_y_shot_move); F(p,last_x_shot_move); F(p,last_y_shot_move);
  F(p,last_x_explosion_follow); F(p,last_y_explosion_follow);
  for(int j=0;j<2;j++) {
   F(p,sidekick[j].ammo_max); F(p,sidekick[j].ammo_refill_ticks_max); F(p,sidekick[j].style);
   F(p,sidekick[j].x); F(p,sidekick[j].y); F(p,sidekick[j].ammo); F(p,sidekick[j].ammo_refill_ticks);
   F(p,sidekick[j].animation_enabled); F(p,sidekick[j].animation_frame);
   F(p,sidekick[j].charge); F(p,sidekick[j].charge_ticks);
  }
 }
 return h;
}

#include "game_probe_fields.inc"

static uint64_t globals_hash(void)
{
 uint64_t h=HASH_START;
 H(power); H(powerAdd); H(lastPower); H(shieldWait); H(shieldT); H(shotRepeat); H(shotMultiPos);
 H(eventLoc); H(maxEvent); H(curLoc); H(globalFlags); H(totalEnemy); H(enemyKilled); H(enemyOnScreen);
 H(endLevel); H(reallyEndLevel); H(levelEnd); H(levelEndWarp); H(playerEndLevel); H(stopBackgrounds);
 H(stopBackgroundNum); H(levelTimer); H(levelTimerCountdown); H(levelTimerJumpTo);
 H(mapX); H(mapY); H(mapX2); H(mapX3); H(mapY2); H(mapY3); H(mapXOfs); H(mapX2Ofs); H(mapX3Ofs);
 H(mapXPos); H(mapX2Pos); H(mapX3Pos); H(map1YDelay); H(map2YDelay); H(backMove); H(backMove2); H(backMove3);
 intptr_t row1=(intptr_t)mapYPos-(intptr_t)megaData1.mainmap;
 intptr_t row2=(intptr_t)mapY2Pos-(intptr_t)megaData2.mainmap;
 intptr_t row3=(intptr_t)mapY3Pos-(intptr_t)megaData3.mainmap;
 H(row1); H(row2); H(row3); H(flareDuration); H(zinglonDuration); H(astralDuration); H(specialWait);
 H(levelFilter); H(levelBrightness); H(levelBrightnessChg); H(filterFade); H(filterActive);
 H(smoothies); H(button); H(soundQueue); H(last_superpixel); H(episodeNum); H(lvlFileNum);
 return h;
}

static uint64_t surface_hash(SDL_Surface *s)
{
 uint64_t h=HASH_START;
 for(int y=0;y<s->h;y++) h=game_probe_hash(h,(Uint8 *)s->pixels+y*s->pitch,(size_t)s->w);
 return h;
}

void game_probe_parse(int *argc, char **argv)
{
 asset_debug_parse(argc,argv);
 if(asset_debug_enabled){game_probe_enabled=true;game_probe_density=8;game_probe_local_blend=true;game_probe_known_blend=true;game_probe_scene_assets=3;enemy_hit_scene=true;tick_limit=6000;}
 int out=1;
 for(int i=1;i<*argc;i++) {
  if(strncmp(argv[i],"--render-test=",14)==0) {
   const char *mode=argv[i]+14; game_probe_enabled=true;
   if(strcmp(mode,"classic")==0) game_probe_density=1;
   else if(strcmp(mode,"4")==0) game_probe_density=4;
   else if(strcmp(mode,"8")==0) game_probe_density=8;
   else if(strcmp(mode,"missing")==0) { game_probe_density=8; game_probe_missing=true; }
   else if(strcmp(mode,"repeat")==0) { game_probe_density=8; game_probe_repeat=true; }
   else if(strcmp(mode,"invalid")==0) { game_probe_density=8; game_probe_invalid=true; }
   else if(strcmp(mode,"coverage-fault")==0) { game_probe_density=8; game_probe_coverage_fault=true; }
   else if(strcmp(mode,"skip")==0) { game_probe_density=8; game_probe_skip=true; }
   else if(strcmp(mode,"local")==0) { game_probe_density=8; game_probe_local_blend=true; }
   else { fprintf(stderr,"Invalid --render-test mode\n"); exit(2); }
  } else if(strncmp(argv[i],"--render-ticks=",15)==0) {
   char *end=NULL; unsigned long v=strtoul(argv[i]+15,&end,10);
   if(!end||*end||v<60||v>6000) { fprintf(stderr,"Render ticks must be 60..6000\n");exit(2); }
   tick_limit=(unsigned int)v;
  } else if(strncmp(argv[i],"--render-assets=",16)==0) game_probe_assets=argv[i]+16;
  else if(strcmp(argv[i],"--render-local-blend")==0) game_probe_local_blend=true;
  else if(strcmp(argv[i],"--render-original-reference")==0) game_probe_original_reference=true;
  else if(strcmp(argv[i],"--render-known-explosion-blend")==0) game_probe_known_blend=true;
  else if(strcmp(argv[i],"--render-capture-blend")==0) game_probe_blend_capture=true;
  else if(strcmp(argv[i],"--render-talon-bank=13")==0) render_mirror_set_talon_banking(true);
  else if(strcmp(argv[i],"--render-talon-bank=5")==0) render_mirror_set_talon_banking(false);
  else if(strncmp(argv[i],"--render-scene-assets=",22)==0) {
   const char *scope=argv[i]+22;
   if(strcmp(scope,"off")==0)game_probe_scene_assets=0;
   else if(strcmp(scope,"enemy")==0)game_probe_scene_assets=1;
   else if(strcmp(scope,"terrain")==0)game_probe_scene_assets=2;
   else if(strcmp(scope,"all")==0)game_probe_scene_assets=3;
   else {fprintf(stderr,"Invalid render scene asset scope\n");exit(2);}
  }
  else if(strncmp(argv[i],"--render-scene=",15)==0) {
   const char *scene=argv[i]+15;
   enemy_hit_scene=fade_cycle_scene=banking_scene=false;
   if(strcmp(scene,"v1")==0) {}
   else if(strcmp(scene,"enemy-hit")==0)enemy_hit_scene=true;
   else if(strcmp(scene,"fade-cycle")==0)fade_cycle_scene=true;
   else if(strcmp(scene,"banking")==0)banking_scene=true;
   else {fprintf(stderr,"Invalid render scene\n");exit(2);}
  }
  else argv[out++]=argv[i];
 }
 argv[out]=NULL; *argc=out;
}

void game_probe_start(void)
{
 trace=fopen("state.tsv","w"); collisions=fopen("collisions.tsv","w"); frames=fopen("frames.tsv","w");
 presentations=fopen("presentation.tsv","w");
 effects=fopen("effects.tsv","w");projectiles=fopen("enemy-projectiles.tsv","w");
 fade_steps=fopen("fade-steps.tsv","w");
 poses=fopen("poses.tsv","w");fire_events=fopen("fire-events.tsv","w");
 player_projectiles=fopen("player-projectiles.tsv","w");draw_commands=fopen("draw-commands.tsv","w");
 scene_draw_commands=fopen("scene-draw-commands.tsv","w");
 scene_enemies=fopen("scene-enemies.tsv","w");scene_hits=fopen("scene-hits.tsv","w");
 rgb_audits=fopen("rgb-audit.tsv","w");
 blend_writes=fopen("blend-writes.tsv","w");
 restore_regions=fopen("restore-regions.tsv","w");blend_palette=fopen("blend-palette.tsv","w");
 if(!trace||!collisions||!frames||!presentations||!effects||!projectiles||!fade_steps||!poses||!fire_events||!player_projectiles||!draw_commands||!scene_draw_commands||!scene_enemies||!scene_hits||!rgb_audits||!blend_writes||!restore_regions||!blend_palette) { fprintf(stderr,"Unable to create local probe records\n");exit(2); }
 fprintf(trace,"tick\tplayers\tenemies\tshots\tparticles\tglobals\trng\thits\thit_hash\tgame_pixels\toutput_pixels\tx\ty\tarmor\tshield\n");
 fprintf(collisions,"tick\tkind\ta\tb\tvalue\n");
 fprintf(frames,"tick\thd_draws\toccluded_blocks\tcoverage_mismatch\treason\tall_rejections\tlocal_entities\tlocal_regions\tlocal_blocks\n");
 fprintf(presentations,"tick\tpresent_calls\trng_before\trng_after\n");
 fprintf(effects,"tick\tbrightness_hd_blocks\trestored_classic_blocks_checked\trestored_mismatches\texpanded_regions\tboundary_crossings\tinvulnerable_ticks\tlevel_brightness\tfilter_fade\n");
 fprintf(projectiles,"tick\tslot\tx\ty\tvx\tvy\tdamage\n");
 fprintf(fade_steps,"tick\tsequence\tmode\tremaining_steps\thd_pixels\trng\tgame_pixels\toutput_pixels\n");
 fprintf(poses,"tick\tplayer\tbank\tbase\tindex\tbanking\tx\ty\tvelocity\tdelta\tinvulnerable\thas_shadow\tshadow_x\tshadow_y\n");
 fprintf(fire_events,"tick\tplayer\tport\tbay\tx\ty\tweapon\tlast_slot\tlast_active\tlast_x\tlast_y\tlast_index\n");
 fprintf(player_projectiles,"tick\tslot\tx\ty\tvx\tvy\tindex\tanimation\tactive\tplayer\n");
 fprintf(draw_commands,"tick\tbank\tindex\tx\ty\tstyle\tlayout\tmirrored\n");
 fprintf(scene_draw_commands,"tick\trole\tindex\tx\ty\tpart\tstyle\tmirrored\n");
 fprintf(scene_enemies,"tick\tslot\ttype\tavail\tx\ty\tarmor\tcycle\tbase\tfilter\tdamaged\tlink\n");
 fprintf(scene_hits,"tick\tslot\ttype\tarmor_before\tdamage\tbase\tlink\n");
 fprintf(rgb_audits,"tick\tdensity\trgb_hash\tclassic_mismatches\n");
 fprintf(blend_writes,"tick\tknown_sheet\tindex\torigin_x\torigin_y\tx\ty\tbefore\tsource\tafter\thd_subpixels_before\trestored_blocks\trgba\n");
 fprintf(restore_regions,"tick\tsource_index\trequested_x\trequested_y\trequested_w\trequested_h\tx\ty\tw\th\tvisual_groups\trestored_hd_blocks\n");
 fprintf(blend_palette,"index\tr\tg\tb\n");
 mt_srand(0x5eedUL);
 JE_initEpisode(1); JE_initPlayerData();
 play_demo=true; record_demo=false; stopped_demo=false;
 gameLoaded=false; jumpSection=false;
 printf("Controlled scene v1: episode=1 TYRIAN lvlFileNum=9 ship=1 front-port=1 power=1 seed=0x5eed ticks=%u\n",tick_limit);
 printf("Input scene: %s\n",enemy_hit_scene?"enemy-hit: no firing, stationary, natural enemies/projectiles":banking_scene?"banking: finite left/release/right/release/left/release inputs, original pose selection":"v1: fixed fire and left/right sequence");
}

bool game_probe_level(void)
{
 if(!game_probe_enabled) return false;
 difficultyLevel=DIFFICULTY_NORMAL; bonusLevelCurrent=false;
 JE_initEpisode(1); initial_episode_num=1;
 strcpy(levelName,"TYRIAN    "); lvlFileNum=9; levelSong=18;
 asset_debug_level();
 /* The item configuration remains JE_initPlayerData's default. */
 return true;
}

bool game_probe_input(void)
{
 /* Dedicated finite sequence: fire constantly; stay central for 180 ticks,
  * then left 60, right 120, left 60. Vertical position is unchanged. */
 if(banking_scene) {
  int direction=game_probe_tick>=180&&game_probe_tick<204 ? -1 :
                game_probe_tick>=234&&game_probe_tick<282 ? 1 :
                game_probe_tick>=312&&game_probe_tick<336 ? -1 : 0;
  player[0].x+=direction*CURRENT_KEY_SPEED;
 } else if(!enemy_hit_scene&&game_probe_tick>=180) {
  unsigned int phase=(game_probe_tick-180)%240;
  player[0].x += phase<60||phase>=180 ? -CURRENT_KEY_SPEED:CURRENT_KEY_SPEED;
 }
 button[0]=!enemy_hit_scene; button[1]=button[2]=button[3]=false;
 return true;
}

void game_probe_pose(int pnum,int bank,int base,int index,int banking,int x,int y,int velocity,int delta,unsigned int invulnerable,int has_shadow,int shadow_x,int shadow_y)
{
 if(!game_probe_enabled)return;
 if(poses)fprintf(poses,"%u\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%u\t%d\t%d\t%d\n",game_probe_tick,pnum,bank,base,index,banking,x,y,velocity,delta,invulnerable,has_shadow,shadow_x,shadow_y);
 if(banking_scene&&pnum==1&&index!=previous_pose)capture_pose_change=true;
 previous_pose=index;
}

void game_probe_fire(int pnum,int port,int bay,int x,int y,int weapon,int slot)
{
 if(!game_probe_enabled||!fire_events)return;
 bool valid=slot>=0&&slot<MAX_PWEAPON;
 fprintf(fire_events,"%u\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%u\t%d\t%d\t%u\n",game_probe_tick,pnum,port,bay,x,y,weapon,slot,valid?shotAvail[slot]:0,valid?playerShotData[slot].shotX:0,valid?playerShotData[slot].shotY:0,valid?playerShotData[slot].shotGr:0);
}

void game_probe_draw(int bank,unsigned int index,int x,int y,int style,int layout,bool mirrored)
{
 if(!game_probe_enabled||!draw_commands)return;
 if(asset_debug_enabled&&(bank==9||bank==8))asset_debug_reference(bank==9?"player":"player-projectile",bank==9?"shapes9.dat":"shapes8.dat",index,index,x,y,layout?24:12,layout?28:14);
 if((bank==9&&index>=229&&index<=237&&index%2==1)||(bank==8&&index==59))
  fprintf(draw_commands,"%u\t%d\t%u\t%d\t%d\t%d\t%d\t%d\n",game_probe_tick,bank,index,x,y,style,layout,mirrored);
}

void game_probe_rgb_audit(SDL_Surface *surface,unsigned int classic_mismatches)
{
 if(!game_probe_enabled||!rgb_audits)return;
 uint64_t h=HASH_START;
 for(int y=0;y<surface->h;y++)h=game_probe_hash(h,(Uint8 *)surface->pixels+y*surface->pitch,(size_t)surface->w*4);
 fprintf(rgb_audits,"%u\t%d\t%016llx\t%u\n",game_probe_tick,game_probe_density,(unsigned long long)h,classic_mismatches);
}

void game_probe_blend_write(bool known,unsigned int index,int ox,int oy,int x,int y,Uint8 before,Uint8 source,Uint8 after,unsigned int subpixels,unsigned int restored_blocks,bool rgba)
{
 if(blend_palette&&!blend_palette_recorded) {
  for(int i=0;i<256;i++)fprintf(blend_palette,"%d\t%u\t%u\t%u\n",i,(rgb_palette[i]>>16)&255,(rgb_palette[i]>>8)&255,rgb_palette[i]&255);
  blend_palette_recorded=true;
 }
 if(blend_writes)fprintf(blend_writes,"%u\t%d\t%u\t%d\t%d\t%d\t%d\t%u\t%u\t%u\t%u\t%u\t%d\n",game_probe_tick,known,index,ox,oy,x,y,before,source,after,subpixels,restored_blocks,rgba);
}

void game_probe_restore_region(unsigned int source,SDL_Rect requested,SDL_Rect restored,unsigned int groups,unsigned int blocks)
{
 if(restore_regions)fprintf(restore_regions,"%u\t%u\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%u\t%u\n",game_probe_tick,source,requested.x,requested.y,requested.w,requested.h,restored.x,restored.y,restored.w,restored.h,groups,blocks);
}

void game_probe_scene_draw(int role,unsigned int index,int x,int y,int part,int style,bool mirrored)
{
 if(!game_probe_enabled||!scene_draw_commands)return;
 fprintf(scene_draw_commands,"%u\t%d\t%u\t%d\t%d\t%d\t%d\t%d\n",game_probe_tick,role,index,x,y,part,style,mirrored);
}

void game_probe_collision(const char *kind, int a, int b, int value)
{
 if(!game_probe_enabled) return;
 if(!strcmp(kind,"player-shot")&&b>=0&&b<100&&scene_hits) {
  const struct JE_SingleEnemyType *e=&enemy[b];
  if(e->enemytype>=121&&e->enemytype<=124) {
   last_scene_hit_tick=game_probe_tick;
   fprintf(scene_hits,"%u\t%d\t%u\t%u\t%d\t%u\t%u\n",game_probe_tick,b,e->enemytype,e->armorleft,value,e->enemycycle?e->egr[e->enemycycle-1]:0,e->linknum);
  }
 }
 if(strcmp(kind,"enemy-shot")==0)last_enemy_hit_tick=game_probe_tick;
 fprintf(collisions,"%u\t%s\t%d\t%d\t%d\n",game_probe_tick,kind,a,b,value);
 hit_hash=game_probe_hash(hit_hash,kind,strlen(kind));
 hit_hash=game_probe_hash(hit_hash,&a,sizeof(a)); hit_hash=game_probe_hash(hit_hash,&b,sizeof(b));
 hit_hash=game_probe_hash(hit_hash,&value,sizeof(value)); ++hits;
}

void game_probe_frame(unsigned int draws,unsigned int covered,unsigned int mismatch,const char *reason,const char *all_rejections,unsigned int local_entities,unsigned int local_regions,unsigned int local_blocks)
{
 if(frames) fprintf(frames,"%u\t%u\t%u\t%u\t%s\t%s\t%u\t%u\t%u\n",game_probe_tick,draws,covered,mismatch,reason,all_rejections,local_entities,local_regions,local_blocks);
}

void game_probe_present(unsigned int count,uint64_t before,uint64_t after)
{
 if(!sdl_runtime_recorded&&main_window) {
  SDL_Renderer *renderer=SDL_GetRenderer(main_window);SDL_RendererInfo info={0};
  int w=0,h=0,rw=0,rh=0;SDL_GetWindowSize(main_window,&w,&h);
  int info_ok=renderer?SDL_GetRendererInfo(renderer,&info):-1;
  int output_ok=renderer?SDL_GetRendererOutputSize(renderer,&rw,&rh):-1;
  FILE *f=fopen("sdl-runtime.tsv","w");
  if(f) {
   fprintf(f,"video_driver\twindow_id\twindow_flags\twindow_shown\twindow_w\twindow_h\trenderer\trenderer_flags\trenderer_info_ok\trender_output_w\trender_output_h\trender_output_ok\n");
   fprintf(f,"%s\t%u\t%u\t%d\t%d\t%d\t%s\t%u\t%d\t%d\t%d\t%d\n",SDL_GetCurrentVideoDriver()?SDL_GetCurrentVideoDriver():"unavailable",SDL_GetWindowID(main_window),SDL_GetWindowFlags(main_window),(SDL_GetWindowFlags(main_window)&SDL_WINDOW_SHOWN)!=0,w,h,info_ok==0?info.name:"unavailable",info.flags,info_ok==0,rw,rh,output_ok==0);fclose(f);
  }
  sdl_runtime_recorded=true;
 }
 if(presentations) fprintf(presentations,"%u\t%u\t%016llx\t%016llx\n",game_probe_tick,count,(unsigned long long)before,(unsigned long long)after);
}

void game_probe_effects(unsigned int brightness,unsigned int checked,unsigned int residual,unsigned int expanded,unsigned int crossed)
{
 if(effects)fprintf(effects,"%u\t%u\t%u\t%u\t%u\t%u\t%u\t%d\t%d\n",game_probe_tick,brightness,checked,residual,expanded,crossed,player[0].invulnerable_ticks,levelBrightness,filterFade);
}

void game_probe_fade_sample(SDL_Surface *surface,int remaining,unsigned int hd_pixels,int mode)
{
 if(!fade_cycle_scene||!fade_steps)return;
 if(remaining==8)++fade_sequence;
 fprintf(fade_steps,"%u\t%u\t%d\t%d\t%u\t%016llx\t%016llx\t%016llx\n",game_probe_tick,fade_sequence,mode,remaining,hd_pixels,
  (unsigned long long)mt_state_fingerprint(),(unsigned long long)surface_hash(game_screen),(unsigned long long)surface_hash(VGAScreenSeg));
 if(remaining==8||remaining==4||remaining==1) {char name[80];snprintf(name,sizeof(name),"fade-%u-%d-%02d.bmp",fade_sequence,mode,remaining);game_probe_export(surface,name);}
}

void game_probe_export(SDL_Surface *s,const char *name)
{
 if(!game_probe_enabled) return;
 if(s->format->BytesPerPixel==4) {
  if(SDL_SaveBMP(s,name)!=0) fprintf(stderr,"RGBA frame export failed: %s\n",SDL_GetError());
  return;
 }
 SDL_Surface *rgb=SDL_CreateRGBSurfaceWithFormat(0,s->w,s->h,32,SDL_PIXELFORMAT_RGB888);
 if(!rgb) return;
 for(int y=0;y<s->h;y++) for(int x=0;x<s->w;x++)
  ((Uint32 *)((Uint8 *)rgb->pixels+y*rgb->pitch))[x]=rgb_palette[((Uint8 *)s->pixels)[y*s->pitch+x]];
 if(SDL_SaveBMP(rgb,name)!=0) fprintf(stderr,"Frame export failed: %s\n",SDL_GetError());
 SDL_FreeSurface(rgb);
}

bool game_probe_capture_tick(void)
{
 if(asset_debug_enabled)return asset_debug_capture_tick()&&!asset_debug_window_only();
 if(game_probe_blend_capture&&game_probe_tick>=192&&game_probe_tick<=212)return true;
 if(game_probe_tick>=128&&game_probe_tick<=360&&game_probe_tick%8==0)return true;
 if(last_scene_hit_tick!=UINT32_MAX&&game_probe_tick>=last_scene_hit_tick&&game_probe_tick-last_scene_hit_tick<=2)return true;
 if(banking_scene&&(capture_pose_change||(game_probe_tick>=164&&game_probe_tick<=356&&game_probe_tick%4==0)))return true;
 static const unsigned int samples[]={0,3,7,13,14,99,100,120,179,188,293,359,515,534,599};
 for(unsigned int i=0;i<sizeof(samples)/sizeof(samples[0]);i++) if(game_probe_tick==samples[i])return true;
 if(last_enemy_hit_tick!=UINT32_MAX&&game_probe_tick>=last_enemy_hit_tick&&game_probe_tick-last_enemy_hit_tick<=2)return true;
 return game_probe_tick==tick_limit-1;
}

bool game_probe_end_tick(void)
{
 if(!game_probe_enabled) return false;
 for(int i=0;i<100;i++) {
  const struct JE_SingleEnemyType *e=&enemy[i];
  if(e->enemytype>=121&&e->enemytype<=124)
   fprintf(scene_enemies,"%u\t%d\t%u\t%u\t%d\t%d\t%u\t%u\t%u\t%u\t%d\t%u\n",game_probe_tick,i,e->enemytype,enemyAvail[i],e->ex,e->ey,e->armorleft,e->enemycycle,e->enemycycle?e->egr[e->enemycycle-1]:0,e->filter,e->edamaged,e->linknum);
 }
 if(fade_cycle_scene&&game_probe_tick==120) {
  Palette saved;
  for(int i=0;i<256;i++) {saved[i].r=(rgb_palette[i]>>16)&255;saved[i].g=(rgb_palette[i]>>8)&255;saved[i].b=rgb_palette[i]&255;saved[i].a=0;}
  uint64_t rng=mt_state_fingerprint();
  fade_black(8);fade_palette(saved,8,0,255);fade_white(8);fade_palette(saved,8,0,255);
  if(rng!=mt_state_fingerprint()) {fprintf(stderr,"Original palette fades advanced RNG\n");exit(2);}
 }
 if(enemy_hit_scene)for(int i=0;i<ENEMY_SHOT_MAX;i++)if(!enemyShotAvail[i])
  fprintf(projectiles,"%u\t%d\t%d\t%d\t%d\t%d\t%u\n",game_probe_tick,i,enemyShot[i].sx,enemyShot[i].sy,enemyShot[i].sxm,enemyShot[i].sym,enemyShot[i].sdmg);
 for(int i=0;i<MAX_PWEAPON;i++)if(shotAvail[i]) {
  const PlayerShotDataType *s=&playerShotData[i];
  fprintf(player_projectiles,"%u\t%d\t%d\t%d\t%d\t%d\t%u\t%u\t%u\t%u\n",game_probe_tick,i,s->shotX,s->shotY,s->shotXM,s->shotYM,s->shotGr,s->shotAni,shotAvail[i],s->playerNumber);
 }
 fprintf(trace,"%u\t%016llx\t%016llx\t%016llx\t%016llx\t%016llx\t%016llx\t%u\t%016llx\t%016llx\t%016llx\t%d\t%d\t%u\t%u\n",
  game_probe_tick,(unsigned long long)players_hash(),(unsigned long long)enemies_hash(),
  (unsigned long long)shots_hash(),(unsigned long long)particles_hash(),(unsigned long long)globals_hash(),
  (unsigned long long)mt_state_fingerprint(),hits,(unsigned long long)hit_hash,
  (unsigned long long)surface_hash(game_screen),(unsigned long long)surface_hash(VGAScreenSeg),
  player[0].x,player[0].y,player[0].armor,player[0].shield);
 if(game_probe_capture_tick()) {
  char name[64]; snprintf(name,sizeof(name),"classic-%04u.bmp",game_probe_tick); game_probe_export(VGAScreenSeg,name);
 }
 fflush(trace); hits=0; hit_hash=HASH_START;capture_pose_change=false;
 asset_debug_end_tick();
 if(++game_probe_tick>=tick_limit) {
  fclose(trace);fclose(collisions);fclose(frames);fclose(presentations);fclose(effects);fclose(projectiles);fclose(fade_steps);fclose(poses);fclose(fire_events);fclose(player_projectiles);fclose(draw_commands);fclose(scene_draw_commands);fclose(scene_enemies);fclose(scene_hits);fclose(rgb_audits);fclose(blend_writes);fclose(restore_regions);fclose(blend_palette);
  trace=collisions=frames=presentations=effects=projectiles=fade_steps=poses=fire_events=player_projectiles=draw_commands=scene_draw_commands=NULL;
  printf("Controlled scene completed %u logic ticks\n",game_probe_tick); return true;
 }
 return false;
}
