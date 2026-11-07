/* SPDX-License-Identifier: GPL-2.0-or-later
 * Normal-game, default-off enemy projectile observation. No input, simulation,
 * RNG, level selection, save data or game-probe setup is written here.
 */
#include "enemy_reuse_observe.h"
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
#include "enemy_reuse_identity.h"
#include "episodes.h"
#include "game_probe.h"
#include "network.h"
#include "params.h"
#include "varz.h"
#include "xmas.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

static char asset_root[1024];
static bool gameplay_lease;
static uint64_t lease_serial,lease_generation;
static unsigned lease_episode,lease_level;

bool enemy_reuse_observe_requested(void) {return asset_root[0]!=0;}
const char *enemy_reuse_observe_assets(void) {return asset_root[0]?asset_root:NULL;}

/* These are the already approved physical campaign sections, not arbitrary
 * user-supplied level selectors. Per-record scope and byte pins remain in the
 * identity module; presentation/palette/resource checks remain in renderer. */
static bool normal_scope(void)
{
 return !game_probe_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
  !xmas&&!twoPlayerMode&&!galagaMode&&!twoPlayerLinked&&!isNetworkGame&&
  !play_demo&&!record_demo&&!constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
  !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent&&
  ((episodeNum==1&&(lvlFileNum==2||lvlFileNum==5))||
   (episodeNum==2&&lvlFileNum==2)||(episodeNum==3&&lvlFileNum==1));
}
void enemy_reuse_observe_reset(void)
{
 if(gameplay_lease)enemy_reuse_reset();
 gameplay_lease=false;lease_generation=0;lease_episode=lease_level=0;
}
bool enemy_reuse_observe_active(void)
{
 if(!gameplay_lease)return false;
 if(!normal_scope()||episodeNum!=lease_episode||lvlFileNum!=lease_level) {
  enemy_reuse_observe_reset();return false;
 }
 return true;
}
uint64_t enemy_reuse_observe_generation(void)
{return enemy_reuse_observe_active()?lease_generation:0;}
void enemy_reuse_observe_start(void)
{
 enemy_reuse_observe_reset();
 if(!enemy_reuse_observe_requested()||!normal_scope()||lease_serial==UINT64_MAX)return;
 /* Called only after the renderer validates the original gameplay PIC3. */
 enemy_reuse_reset();lease_episode=episodeNum;lease_level=lvlFileNum;
 lease_generation=++lease_serial;gameplay_lease=true;
 fprintf(stderr,"Enemy reuse observation: normal gameplay lease episode=%u physical=%u (probe=0)\n",lease_episode,lease_level);
}
void enemy_reuse_observe_parse(int *argc,char **argv)
{
 const char *prefix="--enemy-reuse-observe-assets=";
 const size_t length=strlen(prefix);
 const char *directory=NULL;unsigned requests=0;
 bool conflict=false;
 /* Scan before any parser consumes options, making conflicts order-independent. */
 for(int i=1;i<*argc;i++) {
  if(!strncmp(argv[i],prefix,length)){directory=argv[i]+length;requests++;}
  if(!strncmp(argv[i],"--render-",9)||!strncmp(argv[i],"--asset-debug",13)||
     !strncmp(argv[i],"--manual-hd-assets=",19)||!strncmp(argv[i],"--asteroid-hd-assets=",21)||
     !strncmp(argv[i],"--hud-assets=",13)||!strncmp(argv[i],"--global-assets=",16))conflict=true;
 }
 if(!requests)return;
 if(requests!=1||asset_root[0]||conflict) {
  fprintf(stderr,"Enemy reuse observation requires one exclusive option; cannot combine with render, asset-debug, manual, asteroid, HUD or global assets\n");exit(2);
 }
 struct stat st;
 if(!directory[0]||strlen(directory)>=sizeof(asset_root)||stat(directory,&st)||!S_ISDIR(st.st_mode)) {
  fprintf(stderr,"Enemy reuse observation requires a nonempty existing asset directory\n");exit(2);
 }
 memcpy(asset_root,directory,strlen(directory)+1);
 /* Resolution is presentation state only. In particular, game_probe_assets,
  * game_probe_enabled and all probe input/setup controls remain unchanged. */
 game_probe_density=8;
 int out=1;
 for(int i=1;i<*argc;i++)if(strncmp(argv[i],prefix,length))argv[out++]=argv[i];
 argv[out]=NULL;*argc=out;
 fprintf(stderr,"Enemy reuse observation: enabled; awaiting normal gameplay (probe=0)\n");
}
#endif
