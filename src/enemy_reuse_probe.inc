/* SPDX-License-Identifier: GPL-2.0-or-later
 * Explicit original-event probe contract. This module only writes its own
 * display permission, never gameplay, event, input, RNG or asset state.
 * Included in game_probe.c so no public caller can mint a session.
 */
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
#include "network.h"
#include "params.h"
#include "xmas.h"
#include <sys/stat.h>
static bool probe_requested,probe_started,probe_live;
static uint64_t probe_serial,probe_lease;
static unsigned probe_episode,probe_level;
static uint64_t probe_config;
static char probe_assets[1024];
static uint64_t probe_config_identity(void)
{
 return (uint64_t)preview_port[0]|((uint64_t)preview_port[1]<<8)|((uint64_t)preview_power[0]<<16)|
  ((uint64_t)preview_power[1]<<24)|((uint64_t)preview_rear_mode<<32)|((uint64_t)enemy_hit_scene<<40)|((uint64_t)loadout_selected<<41);
}
static bool probe_profile(void)
{
 bool standard=!loadout_selected&&preview_port[0]==1&&preview_port[1]==0&&preview_power[0]==1&&preview_power[1]==1&&preview_rear_mode==1;
 bool strong=loadout_selected&&preview_port[0]==36&&preview_port[1]==37&&preview_power[0]==11&&preview_power[1]==11&&preview_rear_mode==1;
 return !sidekicks_selected&&!charge_stages&&!fade_cycle_scene&&!banking_scene&&(standard||strong);
}
static bool probe_mode(void)
{
 return game_probe_enabled&&asset_debug_enabled&&play_demo&&!record_demo&&!stopped_demo&&
  !enemy_reuse_observe_requested()&&!manual_hd_enabled&&!asteroid_hd_enabled&&
  !xmas&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!isNetworkGame&&
  !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
  !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent&&
  game_probe_density==8&&!game_probe_missing&&!game_probe_invalid&&!game_probe_original_reference&&
  !game_probe_repeat&&!game_probe_skip&&!game_probe_coverage_fault&&probe_profile();
}
bool enemy_reuse_probe_requested(void) {return probe_requested;}
void enemy_reuse_probe_revoke(void)
{
 if(probe_live)fprintf(stderr,"Enemy reuse controlled probe: revoke generation=%llu tick=%u\n",(unsigned long long)probe_lease,game_probe_tick);
 probe_live=probe_started=false;probe_lease=0;
}
uint64_t enemy_reuse_probe_generation(void)
{
 if(!probe_live)return 0;
 if(!probe_mode()||episodeNum!=probe_episode||lvlFileNum!=probe_level||probe_config_identity()!=probe_config||
    !game_probe_assets||strcmp(game_probe_assets,probe_assets)) {enemy_reuse_probe_revoke();return 0;}
 return probe_lease;
}
static void probe_parse_contract(void)
{
 if(!probe_requested)return;
 struct stat st;
 if(!game_probe_enabled||!asset_debug_enabled||!probe_profile()||enemy_reuse_observe_requested()||
    manual_hd_enabled||asteroid_hd_enabled||game_probe_density!=8||game_probe_missing||game_probe_invalid||
    game_probe_original_reference||game_probe_repeat||game_probe_skip||game_probe_coverage_fault||
    !game_probe_assets||!game_probe_assets[0]||strlen(game_probe_assets)>=sizeof(probe_assets)||stat(game_probe_assets,&st)||!S_ISDIR(st.st_mode)) {
  fprintf(stderr,"Enemy reuse controlled probe requires original asset-debug, density8, existing assets and v1/enemy-hit with default or strong(36/37,power11,mode1) loadout\n");exit(2);
 }
}
static void probe_prepare_contract(void)
{
 /* Inspect caller mode before the legacy probe initialization clears it.
  * A recording/demo invocation cannot be relabelled as our controlled run. */
 if(probe_requested&&(record_demo||play_demo)) {
  fprintf(stderr,"Enemy reuse controlled probe rejects pre-existing demo/record mode\n");exit(2);
 }
}
static void probe_start_contract(void)
{
 enemy_reuse_probe_revoke();
 if(probe_requested){++probe_serial;if(!probe_serial)exit(2);probe_started=true;}
}
static void probe_level_contract(void)
{
 if(!probe_requested)return;
 if(!probe_started||!probe_mode()||!((episodeNum==1&&(lvlFileNum==2||lvlFileNum==5))||
     (episodeNum==2&&lvlFileNum==2)||(episodeNum==3&&lvlFileNum==1))) {
  enemy_reuse_probe_revoke();fprintf(stderr,"Enemy reuse controlled probe: rejected original level/session\n");exit(2);
 }
 probe_episode=episodeNum;probe_level=lvlFileNum;probe_lease=probe_serial;probe_live=true;probe_started=false;
 probe_config=probe_config_identity();strcpy(probe_assets,game_probe_assets);
 fprintf(stderr,"Enemy reuse controlled probe: generation=%llu episode=%u physical=%u input=%s loadout=%s seed=0x5eed assisted-original-events\n",(unsigned long long)probe_lease,probe_episode,probe_level,enemy_hit_scene?"enemy-hit":"v1",loadout_selected?"strong":"default");
}
#else
#define probe_prepare_contract() ((void)0)
#define probe_parse_contract() ((void)0)
#define probe_start_contract() ((void)0)
#define probe_level_contract() ((void)0)
#endif
