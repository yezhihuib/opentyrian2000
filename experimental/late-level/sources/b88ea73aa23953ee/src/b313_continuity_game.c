#include "b313_continuity_report.h"
#include "b313_continuity.h"
#include "b313_v6_recovery_witness.h"
#include "asset_debug.h"
#include "game_probe.h"
#include "keyboard.h"
#include "mainint.h"
#include "episodes.h"
#include "network.h"
#include "varz.h"
static CoContext context(void)
{
 CoContext c={.known=true,.probe=game_probe_enabled,.asset_debug=asset_debug_enabled,
  .demo=play_demo,.record=record_demo,.network=isNetworkGame,.stopped_demo=stopped_demo,
  .end_requested=reallyEndLevel||endLevel||playerEndLevel||quitRequested,
  .episode=episodeNum,.level=lvlFileNum,.session=bco_session(),
  .residual_known=CO_ALL_RESIDUAL,.residual=bco_keyboard_residual()};
 if(pause_pressed)c.residual|=CO_PAUSE_REQUEST;
 if(ingamemenu_pressed)c.residual|=CO_MENU_REQUEST;
 if(asset_debug_continuity_residual())c.residual|=CO_DEBUG_PENDING;
 return c;
}
void bco_game_begin(void)
{
 if(!bco_enabled())return;
 bool empty=true;for(unsigned i=0;i<100;i++)if(enemyAvail[i]!=1)empty=false;
 bco_session_begin(empty);
 /* Current mode is real data, not supplied fixture defaults. */
 CoContext c=context();bco_checkpoint(&c);
 (void)bco_report_emit(BCO_REPORT_BEGIN,game_probe_tick,true);
}
uint64_t bco_game_birth(unsigned tick,unsigned entry,unsigned cur,unsigned type,unsigned pool,const int args[6])
{
 if(!bco_enabled())return 0;
 bool known=true;
 for(unsigned i=0;i<100;i++){
  B313Snapshot v={0};unsigned link=0;
  if(!b313_recovery_read_slot(i,&v,&link)||v.slot!=i||v.avail>2){known=false;continue;}
  if(v.avail==0&&v.type>=313&&v.type<=316)known=false;
  if(i>=25&&i<=28&&v.avail!=1)known=false;
 }
 CoContext c=context();uint64_t attempt=bco_birth_begin(&c,tick,entry,cur,type,pool,args,known);
 if(bco_status().attempt)(void)bco_report_emit(BCO_REPORT_BIRTH_PENDING,tick,true);
 return bco_status().failed?0:attempt;
}
void bco_game_checkpoint(void)
{
 if(!bco_enabled())return;
 CoContext c=context();bco_checkpoint(&c);
}
