/* SPDX-License-Identifier: GPL-2.0-or-later
 * Optional original-event replay. No map/event pointer jumps or save-state system.
 */
#include "asset_debug.h"
#include "game_probe.h"
#include "episodes.h"
#include "enemy_reuse_probe.h"
#include "lvllib.h"
#include "varz.h"
#include "shots.h"
#include "mouse.h"
#include "mtrand.h"
#include "video.h"
#include "nortsong.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
bool asset_debug_enabled;
int asset_debug_exit_code;
static unsigned int episode=1,level=9,target=890,target_event;
static unsigned int first_visible=UINT32_MAX,last_capture=UINT32_MAX;
static unsigned int capture_start=UINT32_MAX,capture_count=36;
static bool window_only,explosion_log_enabled;
static FILE *explosion_log;
static unsigned int preset_target=890;
static int preset_kind=1;
static bool shot_fixture;
static bool index_only;
static FILE *material_log,*clock_log;
static double nominal_ms;
static struct {const Uint8 *data;unsigned int id,layer;char sheet[24];} terrain_refs[216];
static unsigned int terrain_ref_count;
static bool fast=true,reference,paused=true,arrived,step,quitting,capture;
static int pending_slot=-1,pending_damage;
static const char *control_path;
static long control_offset;
static FILE *control_log;
static Uint64 started;
static unsigned int number(const char *s,unsigned int lo,unsigned int hi,const char *name)
{char *end;unsigned long n=strtoul(s,&end,10);if(!*s||*end||n<lo||n>hi){fprintf(stderr,"Asset debug: invalid %s (%u..%u)\n",name,lo,hi);exit(2);}return (unsigned int)n;}
static void log_control(const char *action)
{if(!control_log){control_log=fopen("asset-debug-control.tsv","w");if(!control_log)exit(2);fprintf(control_log,"next_tick\taction\tpaused\tRNG\twall_ms\n");}fprintf(control_log,"%u\t%s\t%d\t%016llx\t%.3f\n",game_probe_tick,action,paused,(unsigned long long)mt_state_fingerprint(),1000.0*(SDL_GetPerformanceCounter()-started)/SDL_GetPerformanceFrequency());fflush(control_log);}
void asset_debug_parse(int *argc,char **argv)
{
 int out=1;bool custom_tick=false,custom_episode=false,custom_level=false;
 for(int i=1;i<*argc;i++){
  const char *s=argv[i];
  if(!strncmp(s,"--asset-debug=",14)){asset_debug_enabled=true;s+=14;if(!strcmp(s,"blue")){preset_target=890;preset_kind=1;}else if(!strcmp(s,"turret")){preset_target=232;preset_kind=2;}else if(!strcmp(s,"type10")){preset_target=150;preset_kind=3;}else if(!strcmp(s,"custom")){}else{fprintf(stderr,"Asset debug: unknown preset\n");exit(2);}}
  else if(!strncmp(s,"--asset-debug-episode=",22)){episode=number(s+22,1,EPISODE_MAX,"episode");custom_episode=true;}
  else if(!strncmp(s,"--asset-debug-level=",20)){level=number(s+20,1,255,"level");custom_level=true;}
  else if(!strncmp(s,"--asset-debug-tick=",19)){target=number(s+19,0,5999,"tick");custom_tick=true;}
  else if(!strncmp(s,"--asset-debug-event=",20))target_event=number(s+20,1,65534,"event ordinal");
  else if(!strncmp(s,"--asset-debug-control=",22))control_path=s+22;
  else if(!strcmp(s,"--asset-debug-reference"))reference=true;
  else if(!strcmp(s,"--asset-debug-running"))paused=false;
  else if(!strcmp(s,"--asset-debug-capture"))capture=true;
  else if(!strncmp(s,"--asset-debug-capture-start=",28))capture_start=number(s+28,0,5999,"capture start");
  else if(!strncmp(s,"--asset-debug-capture-count=",28))capture_count=number(s+28,1,120,"capture count");
  else if(!strcmp(s,"--asset-debug-window-only"))window_only=true;
  else if(!strcmp(s,"--asset-debug-explosion-log"))explosion_log_enabled=true;
  else if(!strcmp(s,"--asset-debug-index-only"))index_only=true;
  else argv[out++]=argv[i];
 }
 if(!asset_debug_enabled&&(custom_tick||custom_episode||custom_level||target_event||control_path||reference||capture||capture_start!=UINT32_MAX||capture_count!=36||window_only||explosion_log_enabled||index_only||!paused)){fprintf(stderr,"Asset debug options require --asset-debug=preset\n");exit(2);}
 if(asset_debug_enabled&&target_event&&custom_tick){fprintf(stderr,"Asset debug: select a tick or event, not both\n");exit(2);}
 if((capture_start!=UINT32_MAX||capture_count!=36||window_only)&&!capture){fprintf(stderr,"Asset debug capture bounds/window-only require --asset-debug-capture\n");exit(2);}
 if(!custom_tick)target=preset_target;
 argv[out]=NULL;*argc=out;started=SDL_GetPerformanceCounter();fast=!reference;
}
bool asset_debug_fast_forward(void){return asset_debug_enabled&&fast;}
void asset_debug_level(void)
{
 if(!asset_debug_enabled)return;
 if(!episodeAvail[episode-1]){fprintf(stderr,"Asset debug: episode data unavailable\n");exit(2);}
 JE_initEpisode((JE_byte)episode);initial_episode_num=(JE_byte)episode;
 if((level-1)*2+1>=lvlNum){fprintf(stderr,"Asset debug: invalid playable level %u in episode%u\n",level,episode);exit(2);}
 lvlFileNum=(JE_byte)level;strcpy(levelName,"ASSET DBG ");levelSong=18;
 fprintf(stdout,"ASSET DEBUG episode=%u physical_level=%u target_tick=%u event=%u input=existing-controlled-script fast=%d\n",episode,level,target,target_event,fast);fflush(stdout);
}
static void command(const char *s)
{
 if(!strcmp(s,"reload")||!strcmp(s,"quit")||!strncmp(s,"hit ",4)||!strncmp(s,"destroy ",8))enemy_reuse_probe_revoke();
 if(!strcmp(s,"pause")){paused=true;log_control("pause");}
 else if(!strcmp(s,"resume")){paused=false;log_control("resume");}
 else if(!strcmp(s,"toggle")){paused=!paused;log_control(paused?"pause":"resume");}
 else if(!strcmp(s,"step")){paused=true;step=true;log_control("step-request");}
 else if(!strcmp(s,"reload")){quitting=true;asset_debug_exit_code=75;log_control("reload-fresh-process");}
 else if(!strcmp(s,"quit")){quitting=true;log_control("quit");}
 else if(!strncmp(s,"hit ",4)||!strncmp(s,"destroy ",8)){bool lethal=s[0]=='d';pending_slot=(int)number(s+(lethal?8:4),0,99,"enemy slot");pending_damage=lethal?0:1;paused=true;step=true;log_control(lethal?"artificial-destroy-shot-request":"artificial-hit-shot-request");}
 else{fprintf(stderr,"Asset debug: unknown control '%s'\n",s);log_control("rejected-control");}
}
static void poll_control(void)
{
 SDL_Event e;while(SDL_PollEvent(&e)){
  if(e.type==SDL_QUIT)command("quit");
  else if(e.type==SDL_KEYDOWN&&!e.key.repeat){switch(e.key.keysym.sym){case SDLK_SPACE:case SDLK_p:command("toggle");break;case SDLK_n:case SDLK_PERIOD:command("step");break;case SDLK_r:command("reload");break;case SDLK_ESCAPE:command("quit");break;case SDLK_h:case SDLK_d:{int slot=-1;for(int i=0;i<100;i++)if(enemyAvail[i]==0&&((preset_kind==1&&(enemy[i].enemytype==8||enemy[i].enemytype==9))||(preset_kind==2&&enemy[i].enemytype>=121&&enemy[i].enemytype<=124)||(preset_kind==3&&enemy[i].enemytype==10))){slot=i;break;}if(slot>=0){char s[64];snprintf(s,sizeof(s),"%s %d",e.key.keysym.sym==SDLK_h?"hit":"destroy",slot);command(s);}else log_control("rejected-no-preset-enemy");break;}default:break;}}
 }
 if(control_path){FILE*f=fopen(control_path,"r");if(f){if(!fseek(f,control_offset,SEEK_SET)){char s[128];if(fgets(s,sizeof(s),f)&&strchr(s,'\n')){control_offset=ftell(f);s[strcspn(s,"\r\n")]='\0';command(s);}}fclose(f);}}
}
bool asset_debug_before_tick(void)
{
 if(!asset_debug_enabled)return false;
 if(target_event>maxEvent){fprintf(stderr,"Asset debug: event ordinal exceeds this level's %u events\n",maxEvent);exit(2);}
 if(index_only)return false;
 if(first_visible==UINT32_MAX&&(target_event?eventLoc>target_event:game_probe_tick>=target)){
  fast=false;first_visible=game_probe_tick;fprintf(stdout,"Asset debug target reached at tick%u eventLoc%u in %.3fms\n",game_probe_tick,eventLoc,1000.0*(SDL_GetPerformanceCounter()-started)/SDL_GetPerformanceFrequency());fflush(stdout);
 }
 if(first_visible==UINT32_MAX)return false;
 if(arrived){do{poll_control();if(paused&&!step&&!quitting)SDL_Delay(8);}while(paused&&!step&&!quitting);}
 return quitting;
}
void asset_debug_end_tick(void)
{
 if(!asset_debug_enabled)return;
 if(explosion_log_enabled) {
  if(!explosion_log){explosion_log=fopen("asset-debug-explosion-pools.tsv","w");if(!explosion_log)exit(2);fprintf(explosion_log,"tick\tactive_explosions\tactive_repeaters\tmax_explosion_ttl\tmax_repeater_ttl\tmax_repeater_delay\n");}
  unsigned int active=0,repeating=0,ttl=0,rep_ttl=0,delay=0;
  for(int i=0;i<MAX_EXPLOSIONS;i++)if(explosions[i].ttl){++active;ttl=MAX(ttl,explosions[i].ttl);}
  for(int i=0;i<MAX_REPEATING_EXPLOSIONS;i++)if(rep_explosions[i].ttl){++repeating;rep_ttl=MAX(rep_ttl,rep_explosions[i].ttl);delay=MAX(delay,rep_explosions[i].delay);}
  fprintf(explosion_log,"%u\t%u\t%u\t%u\t%u\t%u\n",game_probe_tick,active,repeating,ttl,rep_ttl,delay);fflush(explosion_log);
 }
 if(!clock_log){clock_log=fopen("asset-debug-clock.tsv","w");if(!clock_log)exit(2);fprintf(clock_log,"tick\tstart_ms\tstep_ms\tend_ms\tevent_next\tcurLoc\n");}
 double duration=logic_tick_duration_ms();fprintf(clock_log,"%u\t%.6f\t%.6f\t%.6f\t%u\t%u\n",game_probe_tick,nominal_ms,duration,nominal_ms+duration,eventLoc,curLoc);nominal_ms+=duration;fflush(clock_log);
 if(first_visible==UINT32_MAX)return;
 if(!arrived){arrived=true;log_control("target-frame-complete");}
 if(step){step=false;paused=true;log_control("step-complete");}
 char title[220];snprintf(title,sizeof(title),"ASSET DEBUG%s | e%u level%u tick%u | %s | P pause N step R reload H hit D destroy Esc quit",shot_fixture?" / SHOT FIXTURE":"",episode,level,game_probe_tick,paused?"PAUSED":"RUNNING");SDL_SetWindowTitle(main_window,title);
}
void asset_debug_finish(void)
{enemy_reuse_probe_revoke();if(asset_debug_enabled&&!index_only&&!arrived&&!quitting){fprintf(stderr,"Asset debug: target not reached before level/test ended\n");asset_debug_exit_code=2;}}
void asset_debug_projectile(void)
{
 if(!asset_debug_enabled||pending_slot<0)return;
 int slot=pending_slot;pending_slot=-1;struct JE_SingleEnemyType*e=&enemy[slot];
 if(enemyAvail[slot]!=0||!e->enemycycle||!e->armorleft||e->armorleft==255){log_control("rejected-inactive-or-invincible-shot-target");return;}
 int shot=player_shot_create(1,SHOT_MISC,e->ex+e->mapoffset,e->ey-6,mouseX,mouseY,155,1);
 if(shot<0||shot>=MAX_PWEAPON||!shotAvail[shot]){log_control("rejected-shot-capacity");return;}
 PlayerShotDataType*s=&playerShotData[shot];s->shotX=e->ex+e->mapoffset;s->shotY=e->ey-6;s->shotXM=s->shotYM=s->shotXC=s->shotYC=0;s->shotComplicated=false;s->shotDmg=pending_damage?pending_damage:e->armorleft;s->chainReaction=0;s->aimAtEnemy=0;
 shot_fixture=true;
 char action[100];snprintf(action,sizeof(action),"ARTIFICIAL Pulse155 shot slot%d enemy%d type%u link%u damage%u",shot,slot,e->enemytype,e->linknum,s->shotDmg);log_control(action);
}
bool asset_debug_capture_tick(void)
{
 if(game_probe_capture_disabled())return false;
 unsigned int start=capture_start==UINT32_MAX?first_visible:capture_start;
 return asset_debug_enabled&&capture&&first_visible!=UINT32_MAX&&game_probe_tick>=first_visible&&game_probe_tick>=start&&game_probe_tick-start<capture_count;
}
bool asset_debug_window_only(void){return asset_debug_enabled&&window_only;}
void asset_debug_readback(SDL_Renderer *renderer)
{
 if(!asset_debug_capture_tick()||game_probe_tick==last_capture)return;
 int w,h;if(SDL_GetRendererOutputSize(renderer,&w,&h))exit(2);SDL_Surface*s=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_ARGB8888);if(!s||SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,s->pixels,s->pitch))exit(2);
 char name[80];snprintf(name,sizeof(name),"asset-debug-window-%04u.bmp",game_probe_tick);if(SDL_SaveBMP(s,name))exit(2);SDL_FreeSurface(s);last_capture=game_probe_tick;
}
void asset_debug_reference(const char *category,const char *sheet,unsigned int id,unsigned int tile,int x,int y,int w,int h)
{
 if(!asset_debug_enabled||x>=288||x+w<=24||y>=184||y+h<=0)return;
 if(!material_log){material_log=fopen("asset-debug-materials.tsv","w");if(!material_log)exit(2);fprintf(material_log,"tick\tcategory\tsheet\tid\ttile_id\tx\ty\n");}
 fprintf(material_log,"%u\t%s\t%s\t%u\t%u\t%d\t%d\n",game_probe_tick,category,sheet,id,tile,x,y);
}
void asset_debug_bind_terrain(char shape,unsigned int layer,unsigned int id,const Uint8 *data)
{
 if(!asset_debug_enabled)return;if(terrain_ref_count>=216){fprintf(stderr,"Asset debug: terrain registry capacity exceeded\n");exit(2);}
 unsigned int n=terrain_ref_count++;terrain_refs[n].data=data;terrain_refs[n].id=id;terrain_refs[n].layer=layer;snprintf(terrain_refs[n].sheet,sizeof(terrain_refs[n].sheet),"shapes%c.dat",shape);
}
void asset_debug_terrain_row(int x,int y,Uint8 **map)
{
 if(!asset_debug_enabled||y>=184||y+28<=0)return;
 for(int tile=0;tile<12;tile++)if(map[tile])for(unsigned int n=0;n<terrain_ref_count;n++)if(map[tile]==terrain_refs[n].data){char category[32];snprintf(category,sizeof(category),"terrain-layer%u",terrain_refs[n].layer);asset_debug_reference(category,terrain_refs[n].sheet,terrain_refs[n].id,terrain_refs[n].id,x+tile*24,y,24,28);break;}
}
void asset_debug_effect(SDL_Surface *surface,Sprite2_array bank,unsigned int index,int x,int y)
{if(asset_debug_enabled&&surface==game_screen&&bank.data==explosionSpriteSheet.data)asset_debug_reference("effect","explosions-shapes6",index,index,x,y,12,14);}
