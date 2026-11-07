#include "b313_continuity_report.h"
#include "b313_continuity_link.h"
#include "b313_v6_recovery.h"
#include "b313_continuity.h"
#include "b313_tail414.h"
#include <stdlib.h>
#include <string.h>
#include <limits.h>
static BcoStatus s;
static bool configured,group_complete;
static uint64_t entry_resources[4];
static BcoLinkStatus association;
static B313Group source_birth;
static bool fail_no_report(unsigned reason,unsigned tick)
{
 if(!s.failed){s.first_reason=reason;s.first_tick_known=tick!=UINT_MAX;s.first_tick=s.first_tick_known?tick:0;}
 s.failed=true;s.reasons|=reason;s.consumption.boundary_observed=false;return false;
}
static bool fail(unsigned reason,unsigned tick)
{
 bool first=!s.failed;(void)fail_no_report(reason,tick);if(first)bco_report_first_failure();return false;
}
void bco_report_io_failure(void){if(bco_enabled())(void)fail_no_report(BC_IO,UINT_MAX);}
bool bco_enabled(void)
{
 if(!configured){
  const char *v=getenv("BUILDING313_CONTINUITY_OBSERVER_ENABLE");
  const char *ind=getenv("BUILDING313_CONTINUITY_INDEPENDENT_ENABLE");
  const char *tail=getenv("BUILDING313_TAIL414_PREFLIGHT_ENABLE");
  association.independent_requested=ind&&strcmp(ind,"0")!=0;
  bool tail_requested=tail&&strcmp(tail,"0")!=0;
  association.configuration_conflict=association.independent_requested&&tail_requested;
  association.configuration_valid=association.independent_requested&&!strcmp(ind,"1")&&!tail_requested&&b313_conservative_enabled();
  s.enabled=association.independent_requested||(v&&!strcmp(v,"1")&&b313_tail414_enabled());
  configured=true;
 }
 return s.enabled;
}
static bool live(void){return bco_enabled()&&s.session&&!s.failed&&!s.consumption.failed;}
void bco_session_begin(bool empty_pool)
{
 if(!bco_enabled())return;
 if(association.independent_requested&&!association.configuration_valid){fail(BC_SCOPE,UINT_MAX);return;}
 if(s.session||s.failed||!empty_pool){fail(BC_ORDER,UINT_MAX);return;}
 s.session=1; /* One actual physical session per process. No reset or reuse API. */
 if(!co_begin(&s.consumption,s.session))fail(BC_ORDER,UINT_MAX);
}
uint64_t bco_session(void){return s.session;}
void bco_interrupt(unsigned kind)
{
 if(!bco_enabled()||!s.session)return;
 co_interrupt(&s.consumption,kind);fail(BC_SCOPE,UINT_MAX);
}
uint64_t bco_consumed(unsigned tick,unsigned domain,unsigned type)
{
 if(!live())return 0;
 if(s.birth_pending||s.birth_closed){fail(BC_INPUT,tick);return 0;}
 uint64_t token=co_consumed(&s.consumption,domain,tick,type);
 if(!token)fail(BC_INPUT,tick);
 return token;
}
void bco_complete(uint64_t token,unsigned domain,unsigned disposition)
{
 if(!live())return;
 if(!co_complete(&s.consumption,token,domain,disposition))fail(BC_INPUT,UINT_MAX);
}
void bco_command(void)
{
 if(!live())return;
 co_command(&s.consumption);fail(BC_INPUT,UINT_MAX);
}
void bco_resource(unsigned pool)
{
 if(!bco_enabled()||s.failed)return;
 if(pool>=4||s.resources[pool]==UINT64_MAX||s.resource_notifications==UINT_MAX){fail(BC_RESOURCE,UINT_MAX);return;}
 ++s.resources[pool];++s.resource_notifications;
 if(s.birth_pending||s.birth_closed)fail(BC_RESOURCE,UINT_MAX);
}
void bco_allocated(unsigned slot)
{
 if(!live())return;
 if(slot>=100||s.serial==UINT64_MAX||s.generation[slot]==UINT64_MAX){fail(BC_ALLOC,UINT_MAX);return;}
 if(s.birth_pending&&(s.birth_allocations>=4||slot!=25+s.birth_allocations||s.generation[slot])){fail(BC_ALLOC,UINT_MAX);return;}
 if(s.birth_closed&&slot>=25&&slot<=28){fail(BC_ALLOC,UINT_MAX);return;}
 ++s.serial;++s.generation[slot];if(s.birth_pending)++s.birth_allocations;
}
uint64_t bco_birth_begin(const CoContext *c,unsigned tick,unsigned entry,unsigned cur,unsigned type,unsigned pool,const int a[6],bool census_known)
{
 if(!live())return 0;
 if(s.birth_pending||s.birth_closed||s.attempt){fail(BC_ORDER,tick);return 0;}
 /* Protected before checking any prerequisite or calling the real constructor. */
 s.birth_pending=true;s.attempt=1;s.entry_serial=s.serial;
 if(!co_observe_boundary(&s.consumption,c)){fail(BC_SCOPE,tick);return 0;}
 if(!census_known||tick!=244||entry!=18||cur!=244||type!=12||pool!=25||!a||a[0]!=313||a[3]!=20||(a[5]!=0&&a[5]!=1)||s.serial>UINT64_MAX-4){fail(BC_BIRTH,tick);return 0;}
 for(unsigned i=0;i<4;i++)if(!s.resources[i]){fail(BC_RESOURCE,tick);return 0;}
 for(unsigned i=25;i<29;i++)if(s.generation[i]){fail(BC_ALLOC,tick);return 0;}
 memcpy(s.raw_args,a,sizeof(s.raw_args));s.raw_args_recorded=true;memcpy(entry_resources,s.resources,sizeof(entry_resources));return s.attempt;
}
void bco_birth_bind(uint64_t attempt,uint64_t group)
{
 if(!live())return;
 if(!s.birth_pending||attempt!=s.attempt||!attempt||!group||s.group){fail(BC_BIRTH,UINT_MAX);return;}
 s.group=group;
}
void bco_group_complete(const B313Group *g)
{
 if(!live())return;
 if(!s.birth_pending||group_complete||!g||!g->complete||g->reasons||g->members!=15||!g->scene||g->nonce!=s.group||g->birth_tick!=244||g->event_loc!=18||g->cur_loc!=244||g->pool!=25||g->link!=20){fail(BC_BIRTH,UINT_MAX);return;}
 for(unsigned i=0;i<4;i++)if(g->member[i].slot!=25+i||g->member[i].generation!=1||s.generation[25+i]!=1){fail(BC_BIRTH,UINT_MAX);return;}
 if(s.birth_allocations!=4||s.serial!=s.entry_serial+4||memcmp(entry_resources,s.resources,sizeof(entry_resources))||s.consumption.pending){fail(BC_BIRTH,UINT_MAX);return;}
 if(association.independent_requested){
  B313RecoveryStatus w=b313_recovery_status();
  if(!association.configuration_valid||!w.active||w.failed||!w.birth_seen||w.anchored||w.event_seen||w.allocation_serial!=s.serial||memcmp(w.resource_epoch,s.resources,sizeof(s.resources))){fail(BC_BIRTH,UINT_MAX);return;}
  source_birth=*g;association.birth_source_observed=true;association.birth_scene=g->scene;association.birth_group=g->nonce;association.birth_serial=s.serial;
 }
 s.scene=g->scene;group_complete=true;
}
void bco_birth_end(uint64_t attempt,uint64_t group)
{
 if(!live())return;
 if(!s.birth_pending||!group_complete||!attempt||attempt!=s.attempt||!group||group!=s.group){fail(BC_BIRTH,UINT_MAX);return;}
 s.birth_pending=false;s.birth_closed=true;
 (void)bco_report_emit(BCO_REPORT_BIRTH_CLOSED,0,false);
}
BcoStatus bco_status(void){return s;}

void bco_checkpoint(const CoContext *c){if(!live())return;if(s.birth_pending){fail(BC_BIRTH,UINT_MAX);return;}if(!co_observe_boundary(&s.consumption,c))fail(BC_SCOPE,UINT_MAX);}

bool bco_link_independent(void){return bco_enabled()&&association.independent_requested;}
BcoLinkStatus bco_link_status(void){return association;}
void bco_link_anchor409(unsigned tick,uint64_t preparation,const B313Group *g,bool snapshot_saved,bool report_published)
{
 if(!bco_link_independent()||!live())return;
 B313RecoveryStatus w=b313_recovery_status();
 if(!association.configuration_valid||association.anchor_observed||!association.birth_source_observed||!s.birth_closed||s.birth_pending||!s.consumption.boundary_observed||s.consumption.pending||tick!=409||!preparation||!snapshot_saved||!report_published||!g||!g->complete||g->reasons||g->members!=15||g->scene!=s.scene||g->nonce!=s.group||g->scene!=association.birth_scene||g->nonce!=association.birth_group||!w.active||w.failed||!w.birth_seen||!w.anchored||w.event_seen||w.last_census!=409||w.census_reads!=100||w.census_members!=4||w.allocation_serial!=s.serial||w.anchor_serial!=s.serial||memcmp(w.resource_epoch,s.resources,sizeof(s.resources))||memcmp(w.anchor_resources,s.resources,sizeof(s.resources))){fail(BC_BIRTH,tick);return;}
 for(unsigned c=0;c<4;c++){
  const B313Member *m=g->member+c,*b=source_birth.member+c;
  if(m->slot!=25+c||m->generation!=s.generation[25+c]||m->generation!=b->generation||w.slot_generation[c]!=m->generation||!m->drawn||m->parts!=15||m->phase!=1||m->birth.slot!=b->birth.slot||m->birth.type!=b->birth.type||m->birth.record!=b->birth.record||m->birth.pool!=b->birth.pool||m->birth.bank!=b->birth.bank||m->birth.sheet_identity!=b->birth.sheet_identity||m->birth.data_identity!=b->birth.data_identity){fail(BC_BIRTH,tick);return;}
 }
 association.anchor_observed=true;association.anchor_tick=tick;association.anchor_serial=s.serial;association.anchor_preparation=preparation;association.anchor_snapshot_saved=snapshot_saved;association.anchor_report_published=report_published;
 (void)bco_report_emit(BCO_REPORT_ANCHOR409,tick,true);
}
