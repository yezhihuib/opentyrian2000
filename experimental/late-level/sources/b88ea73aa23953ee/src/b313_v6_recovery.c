#include "b313_continuity.h"
#include "b313_continuity_link.h"
#include "b313_tail414_control.h"
#include "b313_tail414.h"
#include "b313_v6_recovery.h"
#if defined(B313_V6_RECOVERY_DIAGNOSTIC) && B313_V6_RECOVERY_DIAGNOSTIC
#if !B313_V6_SEQUENCE_DIAGNOSTIC || !B313_V6_ANIMATION_DIAGNOSTIC || !B313_V6_TRANSACTION_DIAGNOSTIC || !B313_V6_LOCK_DIAGNOSTIC || !B313_V6_PREPARATION_DIAGNOSTIC || !BUILDING313_PRECOMMIT_DIAGNOSTIC || !BUILDING313_FINAL_PROOF_DIAGNOSTIC || !NATIVE_WRITER_SCOPE_DIAGNOSTIC
#error Recovery requires the existing full diagnostic proof path
#endif
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
#include "b313_v6_lock_bridge.h"
#include "b313_v6_transaction.h"
#include "building313_precommit.h"
#include "building313_final_proof.h"
#include "building313_snapshot_transaction.h"
#include "native_writer_scope.h"
#include "native_writer_observer.h"
#include "old_hd_sample_observer.h"
#include "common_pause.h"
#include <stdio.h>
#include <inttypes.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#include "b313_v6_prefix_preparation.h"
static bool started,ended,failed,ready,retired,anchored,event_retired;
static B313V6PrefixEvidence anchor_prefix;
static B313RecoveryStatus anchor_lifetime;
static uint64_t anchor_nonce,anchor_token;
static bool prefix_saved,anchor_committed,conservative_initialized,conservative_mode,terminal;
bool b313_conservative_enabled(void)
{
 if(!conservative_initialized){const char *v=getenv("BUILDING313_V6_CONSERVATIVE_ENABLE");conservative_mode=v&&!strcmp(v,"1");conservative_initialized=true;}
 return conservative_mode&&b313_recovery_enabled();
}
static unsigned previous,reasons,input_events,input_domains,last_input_tick,last_input_domain,last_input_type;
static uint64_t old_scene,old_group,old_frame,old_native,old_sample;
static uint64_t last_lock,last_preparation,last_native,last_sample,last_frame;
enum {RC_ORDER=1,RC_RETIRE=2,RC_ANCHOR=4,RC_EVENT=8,RC_CENSUS=16,RC_REACQUIRE=32,RC_PROOF=64,RC_SNAPSHOT=128,RC_IO=256};
static void reject(unsigned reason)
{
 reasons|=reason;failed=true;ready=false;prefix_saved=false;b313_recovery_lifetime_end();
 b313_v6_lock_revoke();nwo_revoke_frame(NWO_GAP_UNREGISTERED);ohs_revoke(OHS_REASON_SCOPE);b313_scene_end();
}
/* Historical evidence only. This never exports a live lease or authorizes 411. */
bool b313_conservative_save_prefix(uint64_t nonce,uint64_t id)
{
 if(!b313_conservative_enabled()||failed||!started||ended||previous!=409||prefix_saved||anchor_committed){reject(RC_ANCHOR);return false;}
 const B313V6LockStatus *l=b313_v6_lock_status();const B313PreStatus *p=b313_precommit_status();
 B313V6PrefixEvidence e;memset(&e,0,sizeof(e));
 if(!nonce||!id||!b313_v6_lock_current(nonce)||l->nonce!=nonce||!l->transaction_claimed||!l->before_unlock_verified||l->reasons||
  !p->attempted||!p->consumed||p->prepared||p->reasons||!p->token||p->tick!=409||
  !b313_v6_prefix_evidence_copy(id,&e)||e.preparation_id!=id||e.lease.tick!=409||e.binding.phase!=1||
  e.binding.context.tick!=409||e.binding.context.scene!=e.lease.scene||e.binding.context.frame!=e.lease.frame||
  e.binding.context.group!=e.identity.group.nonce||e.binding.context.native_epoch!=e.lease.native_epoch||
  e.binding.context.sample_epoch!=e.lease.sample_epoch||e.binding.context.sequence!=e.lease.sequence||
  !e.binding.metadata_match||!e.binding.pack_generation||e.binding.pack_generation!=l->prefix.pack_generation||
  e.calls!=16||e.cells!=2688||e.samples!=172032||e.matched!=172032||e.unknown||e.bottom!=3072||
  e.lease.scene!=p->scene||e.lease.frame!=p->frame||e.identity.group.nonce!=p->group||
  e.lease.native_epoch!=p->native_epoch||e.lease.sample_epoch!=p->sample_epoch||e.lease.sequence!=p->sequence||
  l->prefix.preparation_id!=id||l->prefix.scene!=p->scene||l->prefix.frame!=p->frame||l->prefix.group!=p->group||
  l->prefix.native_epoch!=p->native_epoch||l->prefix.sample_epoch!=p->sample_epoch||l->prefix.sequence!=p->sequence){reject(RC_ANCHOR);return false;}
 B313RecoveryStatus w=b313_recovery_status();
 if(!w.active||w.failed||!w.birth_seen||w.anchored||w.event_seen){reject(RC_ANCHOR);return false;}
 if(!b313_recovery_anchor_prepare(&e.identity.group)){reject(RC_ANCHOR);return false;}
 anchor_prefix=e;anchor_lifetime=w;anchor_nonce=nonce;anchor_token=p->token;prefix_saved=true;return true;
}
static bool complete_transaction(unsigned tick,const B313V6TransactionStatus *t,const B313V6LockStatus *l,const B313PreStatus *p,const B313FinalStatus *f)
{
 return t->attempted&&t->tick==tick&&t->claimed&&t->wrote&&t->applied&&!t->rolled_back&&t->observer_unknown&&
  t->rows_written==448&&!t->rollback_rows&&!t->reasons&&t->flushed&&!t->io_failed&&t->unlocked&&
  t->present_called&&t->present_calls==1&&!t->submit_failed&&t->snapshot_ready&&t->snapshot_valid&&!t->snapshot_pending&&
  l->attempted&&l->tick==tick&&l->entries==1&&l->opens==1&&l->closes==1&&l->before_unlock_verified&&l->closed&&
  l->transaction_claimed&&!l->reasons&&l->flushed&&!l->io_failed&&
  t->nonce==l->nonce&&t->preparation_id==l->prefix.preparation_id&&t->pack_generation==l->prefix.pack_generation&&
  p->attempted&&p->tick==tick&&p->consumed&&!p->prepared&&!p->reasons&&p->flushed&&!p->io_failed&&
  p->scene==l->prefix.scene&&p->frame==l->prefix.frame&&p->group==l->prefix.group&&
  p->native_epoch==l->prefix.native_epoch&&p->sample_epoch==l->prefix.sample_epoch&&p->sequence==l->prefix.sequence&&
  f->attempted&&f->tick==tick&&f->reported&&!f->io_failed&&!f->valid&&!f->checked&&f->reasons==BFP_SAMPLE&&
  f->scene==l->prefix.scene&&f->frame==l->prefix.frame&&f->group==l->prefix.group&&
  f->native_epoch==l->prefix.native_epoch&&f->sample_epoch==l->prefix.sample_epoch;
}
static bool saved_anchor_matches(const B313Group *g,const B313V6TransactionStatus *t,const B313PreStatus *p)
{
 const B313V6PrefixEvidence *e=&anchor_prefix;B313RecoveryStatus w=b313_recovery_status();
 if(!prefix_saved||anchor_committed||!w.active||w.failed||w.anchored||w.event_seen||
  w.allocation_serial!=anchor_lifetime.allocation_serial||memcmp(w.resource_epoch,anchor_lifetime.resource_epoch,sizeof(w.resource_epoch))||
  t->nonce!=anchor_nonce||p->token!=anchor_token||t->preparation_id!=e->preparation_id||t->pack_generation!=e->binding.pack_generation||
  p->scene!=e->lease.scene||p->frame!=e->lease.frame||p->group!=e->identity.group.nonce||
  p->native_epoch!=e->lease.native_epoch||p->sample_epoch!=e->lease.sample_epoch||p->sequence!=e->lease.sequence||
  g->nonce!=e->identity.group.nonce||g->scene!=e->identity.group.scene)return false;
 for(unsigned c=0;c<4;c++){
  const B313Member *a=&g->member[c],*b=&e->identity.group.member[c];
  if(a->slot!=b->slot||a->generation!=b->generation||a->parts!=b->parts||a->base!=b->base||a->phase!=b->phase||
   a->draw_x!=b->draw_x||a->draw_y!=b->draw_y||a->birth.sheet_identity!=b->birth.sheet_identity||a->birth.data_identity!=b->birth.data_identity)return false;
 }
 return true;
}
void b313_recovery_external_event_at(unsigned tick,unsigned domain,unsigned type)
{
 b313_tail414_external_event_detail(tick,domain,type);
 if(!b313_recovery_enabled())return;
 /* Debug polling precedes sequence_begin: use the actual tick as well as
  * the prior boundary. Never let an inactive NWS hide a consumed event. */
 if(b313_conservative_enabled()){if((tick<408||tick>415)&&!(started&&previous>=408&&previous<=415))return;}
 else if((tick<409||tick>411)&&!(started&&previous>=409&&previous<=411))return;
 if(input_events!=UINT_MAX)++input_events;
 if(domain>=1&&domain<=4)input_domains|=1u<<domain;
 last_input_tick=tick;last_input_domain=domain;last_input_type=type;
 nws_before_event(type);
 reject(RC_EVENT);
}
bool b313_recovery_permit_ready(void){return b313_recovery_enabled()&&ready&&!failed;}
bool b313_recovery_write_tick(unsigned tick)
{return b313_conservative_enabled()?(!failed&&!terminal&&started&&!ended&&previous==tick&&((tick==411&&b313_recovery_permit_ready())||tick==408||tick==409)):(tick==411&&b313_recovery_permit_ready());}
void b313_recovery_before_event(unsigned tick,unsigned loc,unsigned cur,unsigned type,int d1,int d2,int d3,int d4,int d5,int d6)
{
 if(!b313_recovery_enabled())return;
 b313_recovery_event(tick,loc,cur,type,d1,d2,d3,d4,d5,d6);
 if(tick>=(b313_conservative_enabled()?408u:409u)&&tick<=(b313_conservative_enabled()?415u:411u)){
  /* All events independently witnessed, including after NWS stops observing. */
  nws_before_event(type);
  if(tick!=410||!started||ended||previous!=410)reject(RC_EVENT);
 }
}
void b313_recovery_begin(unsigned tick)
{
 if(!b313_recovery_enabled())return;
 unsigned first=b313_conservative_enabled()?408u:409u;
 if(tick<first){if(started)reject(RC_ORDER);b313_slice_sequence_frame(tick,false);return;}
 if(tick>411){
  if(b313_conservative_enabled()&&!terminal){
   terminal=true;
   if(!started||!ended||previous!=411||tick!=412)reject(RC_ORDER);
   bool tail_retired=b313_pause_sequence_retire()&&b313_v6_prefix_frame_retire()&&b313_v6_lock_frame_retire()&&b313_v6_transaction_frame_retire()&&b313_precommit_frame_retire()&&b313_final_frame_retire()&&nws_sequence_frame_retire()&&ohs_sequence_frame_retire();
   if(!tail_retired)reject(RC_RETIRE);
   b313_tail414_control_old_retire(!failed&&tail_retired);
   reject(RC_RETIRE); /* Terminal sticky fallback, never a rearm boundary. */
  }else if(started){ready=false;b313_scene_end();b313_recovery_lifetime_end();}
  b313_slice_sequence_frame(tick,false);return;
 }
 if((!started&&tick!=first)||(started&&(!ended||tick!=previous+1)))reject(RC_ORDER);
 started=true;ended=false;previous=tick;ready=false;
 if(b313_conservative_enabled()){B313RecoveryStatus w=b313_recovery_status();if(!w.active||w.failed)reject(RC_CENSUS);}
 retired=b313_pause_sequence_retire();if(!retired)reject(RC_RETIRE);
 if(!failed&&(!b313_v6_prefix_frame_retire()||!b313_v6_lock_frame_retire()||!b313_v6_transaction_frame_retire()||!b313_precommit_frame_retire()||!b313_final_frame_retire()))reject(RC_RETIRE);
 if(!failed&&tick<411&&(!nws_sequence_frame_retire()||!ohs_sequence_frame_retire()))reject(RC_RETIRE);
 if(tick==411&&!failed){
  if(!anchored||!event_retired||!b313_recovery_census(411))reject(RC_CENSUS);
  if(!failed&&!b313_identity_reacquire())reject(RC_REACQUIRE);
  if(!failed){ready=true;if(!nws_recovery_rearm()||!ohs_recovery_rearm())reject(RC_REACQUIRE);}
 }
 b313_slice_sequence_frame(tick,!failed);
}
void b313_recovery_end(unsigned tick)
{
 if(!b313_recovery_enabled()||tick<(b313_conservative_enabled()?408u:409u)||tick>411)return;
 if(!started||ended||previous!=tick){reject(RC_ORDER);return;}
 const B313V6TransactionStatus *t=b313_v6_transaction_status();
 const B313V6LockStatus *l=b313_v6_lock_status();const B313PreStatus *p=b313_precommit_status();const B313FinalStatus *f=b313_final_status();
 const OhsStatus *o=ohs_status();NwsStatus n=nws_status();B313Status i=b313_status();B313Group g={0};
 /* Sample reporting has its own failure latch, separate from OhsStatus. */
 if(b313_conservative_enabled()&&!failed){
  OhsIoStatus io=ohs_io_status();
  /* Normal frames report at stage and successful commit; the revoked410
   * frame reports once at revocation and never stages/commits. */
  unsigned expected_reports=tick==410?1u:2u;
  if(io.failed||io.error||io.attempts!=expected_reports||io.successful_writes!=expected_reports)reject(RC_IO);
 }
 bool current=t->attempted&&t->tick==tick,applied=current&&t->applied;
 bool identity=i.tracking&&i.scene_valid&&!i.sampling&&i.tick==tick&&i.identity_groups==1&&i.calls==16&&!i.reasons&&b313_get_group(0,&g)&&i.groups==1&&g.identity_observed&&g.complete&&!g.reasons&&g.members==15;
 bool observed=n.enabled&&n.tick==tick&&n.valid&&n.sealed&&!n.active&&!n.events&&!n.reasons&&n.reported&&!n.io_failed&&o->selected&&o->tick==tick&&o->valid_subset&&o->committed&&o->present_count==1;
 if(b313_conservative_enabled()&&!failed&&(tick==408||tick==409)){
  if(!identity||!observed||!complete_transaction(tick,t,l,p,f)||
   l->nonce<=last_lock||l->prefix.preparation_id<=last_preparation||n.epoch<=last_native||o->epoch<=last_sample||i.frame<=last_frame||
   l->prefix.scene!=i.scene||l->prefix.frame!=i.frame||l->prefix.group!=g.nonce||l->prefix.native_epoch!=n.epoch||l->prefix.sample_epoch!=o->epoch||
   (tick==409&&!saved_anchor_matches(&g,t,p)))reject(RC_PROOF);
  else{last_lock=l->nonce;last_preparation=l->prefix.preparation_id;last_native=n.epoch;last_sample=o->epoch;last_frame=i.frame;}
 }
 if(!failed&&tick==409&&!b313_conservative_enabled()){
  if(current||l->attempted||p->attempted||!identity||!observed||!f->valid||f->tick!=409||f->calls!=16||f->cells!=2688||f->samples!=172032||f->classic_samples!=172032||f->unknown_samples||!f->reported||f->io_failed||!b313_recovery_anchor(&g))reject(RC_ANCHOR);
  else{anchored=true;old_scene=i.scene;old_group=g.nonce;old_frame=i.frame;old_native=n.epoch;old_sample=o->epoch;}
 }
 if(!failed&&tick==410){
  if(!anchored||current||l->attempted||p->attempted||i.tracking||i.scene_valid||!n.enabled||n.tick!=410||n.valid||n.active||n.sealed||!n.reported||n.io_failed||n.reasons!=NWS_EVENT||n.events!=1||n.last_event!=19||o->valid_subset||!b313_recovery_census(410))reject(RC_EVENT);
  else event_retired=true;
 }
 if(!failed&&tick==411){
  if(b313_conservative_enabled()&&(!complete_transaction(tick,t,l,p,f)||l->nonce<=last_lock||l->prefix.preparation_id<=last_preparation||
   l->prefix.scene!=i.scene||l->prefix.frame!=i.frame||l->prefix.group!=g.nonce||l->prefix.native_epoch!=n.epoch||l->prefix.sample_epoch!=o->epoch))reject(RC_PROOF);
  if(!ready||!identity||!observed||!b313_recovery_continuity()||i.scene<=old_scene||g.nonce<=old_group||i.frame<=old_frame||n.epoch<=old_native||o->epoch<=old_sample||
   !current||!applied||t->rows_written!=448||t->rollback_rows||t->reasons||!t->flushed||t->io_failed||!t->unlocked||t->present_calls!=1||!t->snapshot_valid||t->snapshot_pending||
   l->tick!=411||!l->before_unlock_verified||!l->closed||!l->transaction_claimed||l->reasons||!l->flushed||l->io_failed||p->tick!=411||!p->consumed||p->reasons||!p->flushed||p->io_failed||f->tick!=411||!f->reported||f->io_failed||f->valid)reject(RC_PROOF);
 }
 char snapshot[96],report[96],tmp[100];snprintf(snapshot,sizeof(snapshot),"building313-recovery-snapshot-%04u.bmp",tick);
 bool captured=b313_pause_sequence_capture(snapshot);if(!captured||!b313_pause_valid()||b313_pause_pending())reject(RC_SNAPSHOT);
 if(b313_conservative_enabled()&&!failed&&tick==409){
  /* Complete submitted transaction + saved prewrite evidence, never final.valid. */
  if(!saved_anchor_matches(&g,t,p)||!b313_recovery_anchor(&anchor_prefix.identity.group))reject(RC_ANCHOR);
  else{anchor_committed=true;anchored=true;old_scene=anchor_prefix.lease.scene;old_group=anchor_prefix.identity.group.nonce;old_frame=anchor_prefix.lease.frame;old_native=anchor_prefix.lease.native_epoch;old_sample=anchor_prefix.lease.sample_epoch;}
 }
 snprintf(report,sizeof(report),"building313-v6-recovery-%04u.json",tick);snprintf(tmp,sizeof(tmp),"%s.tmp",report);
 FILE *file=fopen(tmp,"w");if(!file){reject(RC_IO);ended=true;return;}
 i=b313_status();
 fprintf(file,"{\n\"tick\":%u,\"failed\":%s,\"reasons\":%u,\"anchor409\":%s,\"event410_retired\":%s,\"fresh_identity_ready\":%s,\"new_material_applied\":%s,\"rows_written\":%u,\"current_transaction\":%s,\"snapshot_retired\":%s,\"snapshot_captured\":%s,\"snapshot_valid\":%s,\"snapshot_pending\":%s,\"old_scene\":%"PRIu64",\"old_group\":%"PRIu64",\"old_frame\":%"PRIu64",\"scene\":%"PRIu64",\"group\":%"PRIu64",\"frame\":%"PRIu64",\"native_epoch\":%"PRIu64",\"sample_epoch\":%"PRIu64",\"tracking\":%s,\"identity_groups\":%u,\"identity_calls\":%u,\"runtime_eligible\":false,\"v6_runtime_validated\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\",\"scope\":\"Legacy mode:409 no-material anchor. Conservative mode:408/409 transactions and saved prewrite409 CLASSIC anchor. Both:410 original revoke,411 fresh phase2 proof. Conservative412+ sticky fallback. No generic recovery, scanout or P/ESC proof.\",\n",tick,failed?"true":"false",reasons,anchored?"true":"false",event_retired?"true":"false",ready?"true":"false",applied?"true":"false",current?t->rows_written:0,current?"true":"false",retired?"true":"false",captured?"true":"false",b313_pause_valid()?"true":"false",b313_pause_pending()?"true":"false",old_scene,old_group,old_frame,i.scene,g.nonce,i.frame,n.epoch,o->epoch,i.tracking?"true":"false",i.identity_groups,i.calls);
 fprintf(file,"\"external_inputs\":{\"events\":%u,\"domains\":%u,\"last_tick\":%u,\"last_domain\":%u,\"last_type\":%u},\n",input_events,input_domains,last_input_tick,last_input_domain,last_input_type);
 fprintf(file,"\"conservative_mode\":%s,\"prewrite_prefix_saved\":%s,\"successful_transaction_anchor\":%s,\"anchor_lock_nonce\":%"PRIu64",\"anchor_preparation_id\":%"PRIu64",\n",b313_conservative_enabled()?"true":"false",prefix_saved?"true":"false",anchor_committed&&!failed?"true":"false",anchor_nonce,anchor_prefix.preparation_id);
 B313RecoveryStatus w=b313_recovery_status();
 fprintf(file,"\"lifecycle\":{\"active\":%s,\"failed\":%s,\"reasons\":%u,\"birth_seen\":%s,\"anchored\":%s,\"event_seen\":%s,\"event_cur_loc\":%u,\"census410\":%s,\"census411\":%s,\"taken\":%s,\"last_census\":%u,\"census_reads\":%u,\"census_members\":%u,\"allocation_serial\":%"PRIu64",\"anchor_serial\":%"PRIu64",\"resource_epochs\":[%"PRIu64",%"PRIu64",%"PRIu64",%"PRIu64"],\"anchor_resources\":[%"PRIu64",%"PRIu64",%"PRIu64",%"PRIu64"],\"members\":[",w.active?"true":"false",w.failed?"true":"false",w.reasons,w.birth_seen?"true":"false",w.anchored?"true":"false",w.event_seen?"true":"false",w.event_cur_loc,w.census410?"true":"false",w.census411?"true":"false",w.taken?"true":"false",w.last_census,w.census_reads,w.census_members,w.allocation_serial,w.anchor_serial,w.resource_epoch[0],w.resource_epoch[1],w.resource_epoch[2],w.resource_epoch[3],w.anchor_resources[0],w.anchor_resources[1],w.anchor_resources[2],w.anchor_resources[3]);
 for(unsigned c=0;c<4;c++){
  const B313Snapshot *v=w.current+c;
  fprintf(file,"%s{\"slot\":%u,\"generation\":%"PRIu64",\"type\":%u,\"record\":%u,\"pool\":%u,\"bank\":%u,\"avail\":%u,\"link\":%u,\"record_verified\":%s,\"graphics_verified\":%s,\"sheet_identity\":%"PRIuPTR",\"data_identity\":%"PRIuPTR",\"base\":%u,\"cycle\":%u,\"ex\":%d,\"ey\":%d}",c?",":"",v->slot,w.slot_generation[c],v->type,v->record,v->pool,v->bank,v->avail,w.current_links[c],v->record_verified?"true":"false",v->graphics_verified?"true":"false",v->sheet_identity,v->data_identity,v->base,v->cycle,v->ex,v->ey);
 }
 fputs("]}\n}\n",file);
 bool bad=ferror(file)!=0;int closed=fclose(file);if(bad||closed||rename(tmp,report)){remove(tmp);reject(RC_IO);}
 if(tick==409&&!failed&&anchor_committed){
  if(bco_link_independent()){bco_game_checkpoint();bco_link_anchor409(tick,anchor_prefix.preparation_id,&anchor_prefix.identity.group,captured,true);}
  b313_tail414_anchor409(&anchor_prefix);
 }
 b313_tail414_control_old_end(tick,!failed);
 ended=true;
}
#else
typedef int b313_v6_recovery_disabled_translation_unit;
#endif
