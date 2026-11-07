#include "b313_tail414_material.h"
#include "b313_v6_prefix_preparation.h"
/* Private414 orchestration: default read-only; explicit isolated material mode.
 * No production admission. Current locked prefix is required before first write. */
#include "b313_tail414_control.h"
/* The legacy controller requires its complete diagnostic providers.
 * Absent providers cannot be replaced with successful status/retirement facts. */
#if B313_V6_RECOVERY_DIAGNOSTIC && B313_V6_SEQUENCE_DIAGNOSTIC && \
    B313_V6_ANIMATION_DIAGNOSTIC && B313_V6_LOCK_DIAGNOSTIC && \
    B313_V6_PREPARATION_DIAGNOSTIC && B313_V6_TRANSACTION_DIAGNOSTIC && \
    BUILDING313_PRECOMMIT_DIAGNOSTIC && BUILDING313_FINAL_PROOF_DIAGNOSTIC && \
    NATIVE_WRITER_SCOPE_DIAGNOSTIC && OLD_HD_SAMPLE_OBSERVER_DIAGNOSTIC
#include "b313_tail414.h"
#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
#include "b313_v6_lock_bridge.h"
#include "b313_v6_transaction.h"
#include "building313_identity.h"
#include "building313_precommit.h"
#include "building313_final_proof.h"
#include "building313_snapshot_transaction.h"
#include "native_writer_observer.h"
#include "native_writer_scope.h"
#include "old_hd_sample_observer.h"
#include "common_pause.h"
#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
static bool selected,failed,retired,proof_complete;
static unsigned old_frames,reasons;
static uint64_t old_scene,old_group,old_frame,old_native,old_sample;
enum {TC_OLD=1,TC_LIFETIME=2,TC_RETIRE=4,TC_IDENTITY=8,TC_PROOF=16,TC_SNAPSHOT=32,TC_IO=64};
static void fail(unsigned why){failed=true;reasons|=why;selected=false;b313_tail414_controller_cancel(414);b313_scene_end();nwo_revoke_frame(NWO_GAP_UNREGISTERED);}
static bool material_configured,material_requested,material_valid,material_saved;
static B313V6PrefixEvidence material_prefix;
static uint64_t material_nonce,material_token;
static void material_configure(void)
{
 if(material_configured)return;material_configured=true;
 const char *v=getenv("BUILDING313_TAIL414_MATERIAL_ENABLE");
 const char *bridge=getenv("BUILDING313_TAIL414_CONTINUITY_ENABLE");
 const char *ind=getenv("BUILDING313_CONTINUITY_INDEPENDENT_ENABLE");
 const char *legacy=getenv("BUILDING313_TAIL414_PREFLIGHT_ENABLE");
 material_requested=v&&strcmp(v,"0");
 material_valid=material_requested&&!strcmp(v,"1")&&bridge&&!strcmp(bridge,"1")&&ind&&!strcmp(ind,"1")&&(!legacy||!strcmp(legacy,"0"))&&b313_conservative_enabled();
}
bool b313_tail414_material_write_tick(unsigned tick)
{
 material_configure();
 return material_valid&&tick==414&&selected&&!failed&&retired&&old_frames==15&&b313_slice_tick()==414&&b313_slice_phase()==0&&b313_slice_top()==107&&b313_tail414_probe_tick(414);
}
bool b313_tail414_material_save_prefix(uint64_t nonce,uint64_t id)
{
 if(!b313_tail414_material_write_tick(414)||material_saved){fail(TC_PROOF);return false;}
 const B313V6LockStatus *l=b313_v6_lock_status();const B313PreStatus *p=b313_precommit_status();
 B313V6PrefixEvidence e={0};
 if(!nonce||!id||!b313_v6_lock_current(nonce)||l->nonce!=nonce||!l->transaction_claimed||!l->before_unlock_verified||l->reasons||!p->attempted||!p->consumed||p->prepared||!p->precommit_probe_allow||p->reasons||!p->token||p->tick!=414||!b313_v6_prefix_evidence_copy(id,&e)||e.preparation_id!=id||e.lease.tick!=414||e.binding.phase!=0||!e.binding.metadata_match||!e.binding.pack_generation||e.binding.pack_generation!=l->prefix.pack_generation||l->prefix.phase_cache_mask!=7||!l->prefix.immutable_phase_set||e.calls!=16||e.cells!=2688||e.samples!=172032||e.matched!=172032||e.unknown||e.bottom!=3072||e.lease.scene!=p->scene||e.lease.frame!=p->frame||e.identity.group.nonce!=p->group||e.lease.native_epoch!=p->native_epoch||e.lease.sample_epoch!=p->sample_epoch||e.lease.sequence!=p->sequence||e.binding.context.tick!=414||e.binding.context.scene!=p->scene||e.binding.context.frame!=p->frame||e.binding.context.group!=p->group||e.binding.context.native_epoch!=p->native_epoch||e.binding.context.sample_epoch!=p->sample_epoch||e.binding.context.sequence!=p->sequence||l->prefix.preparation_id!=id||l->prefix.scene!=p->scene||l->prefix.frame!=p->frame||l->prefix.group!=p->group||l->prefix.native_epoch!=p->native_epoch||l->prefix.sample_epoch!=p->sample_epoch||l->prefix.sequence!=p->sequence||!b313_tail414_material_write_tick(414)){fail(TC_PROOF);return false;}
 material_prefix=e;material_nonce=nonce;material_token=p->token;material_saved=true;return true;
}
static void material_end(unsigned tick)
{
 B313Status i=b313_status();B313Group g={0};NwsStatus n=nws_status();const OhsStatus *o=ohs_status();OhsIoStatus io=ohs_io_status();
 const B313PreStatus *p=b313_precommit_status();const B313FinalStatus *f=b313_final_status();const B313V6TransactionStatus *tx=b313_v6_transaction_status();const B313V6LockStatus *l=b313_v6_lock_status();const B313V6PrefixEvidence *e=&material_prefix;
 bool complete=material_valid&&!failed&&selected&&material_saved&&b313_tail414_continuity414()&&b313_get_group(0,&g)&&i.tracking&&i.scene_valid&&!i.sampling&&!i.reasons&&i.tick==414&&i.groups==1&&i.identity_groups==1&&i.calls==16&&g.identity_observed&&!g.reasons&&g.complete&&g.members==15&&i.scene>old_scene&&g.nonce>old_group&&i.frame>old_frame&&n.epoch>old_native&&o->epoch>old_sample&&
  n.enabled&&n.tick==414&&n.valid&&n.sealed&&!n.active&&!n.events&&!n.reasons&&n.reported&&!n.io_failed&&o->selected&&o->tick==414&&o->valid_subset&&o->committed&&o->present_count==1&&!io.failed&&!io.error&&io.attempts==2&&io.successful_writes==2&&
  p->attempted&&p->tick==414&&p->consumed&&!p->prepared&&p->precommit_probe_allow&&!p->reasons&&p->flushed&&!p->io_failed&&p->token==material_token&&p->calls==16&&p->cells==2688&&p->samples==172032&&p->matched==172032&&!p->unknown&&p->bottom==3072&&p->scene==i.scene&&p->frame==i.frame&&p->group==g.nonce&&p->native_epoch==n.epoch&&p->sample_epoch==o->epoch&&
  e->preparation_id==tx->preparation_id&&e->binding.phase==0&&e->binding.pack_generation==tx->pack_generation&&e->lease.tick==414&&e->lease.scene==i.scene&&e->lease.frame==i.frame&&e->identity.group.nonce==g.nonce&&e->lease.native_epoch==n.epoch&&e->lease.sample_epoch==o->epoch&&e->lease.sequence==p->sequence&&e->calls==16&&e->cells==2688&&e->samples==172032&&e->matched==172032&&!e->unknown&&e->bottom==3072&&
  tx->attempted&&tx->tick==414&&tx->nonce==material_nonce&&tx->claimed&&tx->wrote&&tx->applied&&!tx->rolled_back&&tx->observer_unknown&&tx->rows_written==448&&!tx->rollback_rows&&!tx->reasons&&tx->flushed&&!tx->io_failed&&tx->unlocked&&tx->present_called&&tx->present_calls==1&&!tx->submit_failed&&tx->snapshot_ready&&tx->snapshot_valid&&!tx->snapshot_pending&&
  l->attempted&&l->tick==414&&l->nonce==material_nonce&&l->entries==1&&l->opens==1&&l->closes==1&&l->before_unlock_verified&&l->closed&&l->transaction_claimed&&!l->reasons&&l->flushed&&!l->io_failed&&l->prefix.preparation_id==tx->preparation_id&&l->prefix.pack_generation==tx->pack_generation&&l->prefix.phase_cache_mask==7&&l->prefix.immutable_phase_set&&
  f->attempted&&f->tick==414&&f->reported&&!f->io_failed&&!f->checked&&!f->valid&&f->reasons==BFP_SAMPLE&&f->scene==i.scene&&f->frame==i.frame&&f->group==g.nonce&&f->native_epoch==n.epoch&&f->sample_epoch==o->epoch&&!b313_recovery_write_tick(414);
 static const unsigned bases[4]={191,193,153,155};
 for(unsigned c=0;c<4;c++)if(g.member[c].slot!=25+c||g.member[c].generation!=1||g.member[c].phase!=0||g.member[c].base!=bases[c]||g.member[c].parts!=15||g.member[c].generation!=e->identity.group.member[c].generation||g.member[c].slot!=e->identity.group.member[c].slot||g.member[c].parts!=e->identity.group.member[c].parts||g.member[c].base!=e->identity.group.member[c].base||g.member[c].phase!=e->identity.group.member[c].phase||g.member[c].draw_x!=e->identity.group.member[c].draw_x||g.member[c].draw_y!=e->identity.group.member[c].draw_y||g.member[c].birth.sheet_identity!=e->identity.group.member[c].birth.sheet_identity||g.member[c].birth.data_identity!=e->identity.group.member[c].birth.data_identity)complete=false;
 if(!complete)fail(TC_PROOF);
 bool captured=complete&&b313_pause_sequence_capture("building313-tail414-material-snapshot.bmp")&&b313_pause_valid()&&!b313_pause_pending();if(!captured)fail(TC_SNAPSHOT);
 b313_tail414_end(tick);B313Tail414Status life=b313_tail414_status();if(life.failed||!life.finished||!life.taken||!b313_tail414_report())fail(TC_LIFETIME);
 bool completed=complete&&captured&&!failed;selected=false;
 FILE *file=fopen("building313-tail414-material.json.tmp","w");if(!file){fail(TC_IO);fprintf(stderr,"TAIL414_MATERIAL_REPORT_FAILED\n");return;}
 fprintf(file,"{\"tick\":414,\"transaction_complete\":%s,\"failed\":%s,\"reasons\":%u,\"prewrite_prefix_saved\":%s,\"prewrite_classic_samples\":%u,\"scene\":%"PRIu64",\"group\":%"PRIu64",\"frame\":%"PRIu64",\"native_epoch\":%"PRIu64",\"sample_epoch\":%"PRIu64",\"lock_nonce\":%"PRIu64",\"preparation_id\":%"PRIu64",\"pack_generation\":%"PRIu64",\"phase\":0,\"old_retirement_verified\":%s,\"new_material_applied\":%s,\"rows_written\":%u,\"snapshot_captured\":%s,\"postwrite_classic\":false,\"postwrite_expected_sample_unknown\":%s,\"write_allowed\":false,\"runtime_eligible\":false,\"production_enabled\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\",\"scope\":\"Private single414 transaction. Admission uses same-frame locked prewrite prefix, not prior or final CLASSIC facts. No production or generic recovery permission.\"}\n",completed?"true":"false",failed?"true":"false",reasons,material_saved?"true":"false",e->matched,i.scene,g.nonce,i.frame,n.epoch,o->epoch,tx->nonce,tx->preparation_id,tx->pack_generation,retired?"true":"false",tx->applied?"true":"false",tx->rows_written,captured?"true":"false",(!f->valid&&!f->checked&&f->reasons==BFP_SAMPLE)?"true":"false");
 bool bad=ferror(file)!=0;int closed=fclose(file);if(bad||closed||rename("building313-tail414-material.json.tmp","building313-tail414-material.json")){fail(TC_IO);fprintf(stderr,"TAIL414_MATERIAL_REPORT_FAILED\n");}
}
void b313_tail414_control_old_end(unsigned tick,bool success)
{
 if(!b313_tail414_enabled())return;
 if(tick<408||tick>411||!success||old_frames!=(1u<<(tick-408))-1u){fail(TC_OLD);return;}
 old_frames|=1u<<(tick-408);
 if(tick==411){B313Status i=b313_status();B313Group g={0};NwsStatus n=nws_status();const OhsStatus *o=ohs_status();
  if(!b313_get_group(0,&g)||!i.scene_valid||i.groups!=1||g.reasons||!g.identity_observed||!n.valid||!n.sealed||n.io_failed||!o->valid_subset||!o->committed){fail(TC_OLD);return;}
  old_scene=i.scene;old_group=g.nonce;old_frame=i.frame;old_native=n.epoch;old_sample=o->epoch;
 }
}
void b313_tail414_control_old_retire(bool success){if(!b313_tail414_enabled())return;if(retired||old_frames!=15||!success)fail(TC_OLD);else retired=true;}
bool b313_tail414_probe_tick(unsigned tick){return tick==414&&b313_tail414_enabled()&&selected&&!failed&&b313_tail414_continuity414();}
void b313_tail414_control_begin(unsigned tick)
{
 if(!b313_tail414_enabled())return;
 b313_tail414_begin(tick);
 if(tick!=414){selected=false;return;}
 material_configure();if(material_requested&&!material_valid){fail(TC_PROOF);return;}
 B313Tail414Status t=b313_tail414_status();NwsStatus n=nws_status();const OhsStatus *o=ohs_status();
 if(failed||old_frames!=15||!retired||!t.candidate_ready||t.failed||!b313_tail414_continuity414()){fail(TC_LIFETIME);return;}
 if(material_requested&&(!b313_v6_prefix_frame_retire()||!b313_v6_lock_frame_retire()||!b313_v6_transaction_frame_retire())){fail(TC_RETIRE);return;}
 if(n.enabled||o->selected||!nws_sequence_frame_retire()||!ohs_sequence_frame_retire()||!b313_precommit_frame_retire()||!b313_final_frame_retire()||!b313_pause_sequence_retire()){fail(TC_RETIRE);return;}
 if(!b313_identity_tail414_reacquire()){fail(TC_IDENTITY);return;}
 selected=true;b313_slice_tail414_select();
 if(b313_slice_tick()!=414||b313_slice_phase()!=0||b313_slice_top()!=107){fail(TC_IDENTITY);return;}
}
void b313_tail414_control_end(unsigned tick)
{
 if(!b313_tail414_enabled()||tick<408||tick>414)return;
 if(tick!=414){b313_tail414_end(tick);if(!b313_tail414_report())fail(TC_LIFETIME);return;}
 material_configure();if(material_requested){material_end(tick);return;}
 B313Status i=b313_status();B313Group g={0};NwsStatus n=nws_status();const OhsStatus *o=ohs_status();OhsIoStatus io=ohs_io_status();
 const B313PreStatus *p=b313_precommit_status();const B313FinalStatus *f=b313_final_status();const B313V6TransactionStatus *tx=b313_v6_transaction_status();const B313V6LockStatus *l=b313_v6_lock_status();
 bool complete=!failed&&selected&&b313_tail414_continuity414()&&b313_get_group(0,&g)&&i.tracking&&i.scene_valid&&!i.sampling&&!i.reasons&&i.tick==414&&i.groups==1&&i.identity_groups==1&&i.calls==16&&g.identity_observed&&!g.reasons&&g.complete&&g.members==15&&
  i.scene>old_scene&&g.nonce>old_group&&i.frame>old_frame&&n.epoch>old_native&&o->epoch>old_sample&&
  n.enabled&&n.tick==414&&n.valid&&n.sealed&&!n.active&&!n.events&&!n.reasons&&n.reported&&!n.io_failed&&
  o->selected&&o->tick==414&&o->valid_subset&&o->committed&&o->present_count==1&&!io.failed&&!io.error&&io.attempts==2&&io.successful_writes==2&&
  p->attempted&&p->tick==414&&p->consumed&&!p->prepared&&p->precommit_probe_allow&&!p->reasons&&p->flushed&&!p->io_failed&&p->calls==16&&p->cells==2688&&p->samples==172032&&p->matched==172032&&!p->unknown&&p->bottom==3072&&
  p->scene==i.scene&&p->frame==i.frame&&p->group==g.nonce&&p->native_epoch==n.epoch&&p->sample_epoch==o->epoch&&
  f->attempted&&f->tick==414&&f->checked&&f->valid&&f->reported&&!f->io_failed&&!f->reasons&&f->calls==16&&f->cells==2688&&f->samples==172032&&f->classic_samples==172032&&!f->unknown_samples&&f->bottom_samples==3072&&
  f->scene==i.scene&&f->frame==i.frame&&f->group==g.nonce&&f->native_epoch==n.epoch&&f->sample_epoch==o->epoch&&!tx->attempted&&!tx->applied&&!l->attempted&&!b313_recovery_write_tick(414);
 static const unsigned bases[4]={191,193,153,155};for(unsigned c=0;c<4;c++)if(g.member[c].slot!=25+c||g.member[c].generation!=1||g.member[c].phase!=0||g.member[c].base!=bases[c]||g.member[c].parts!=15)complete=false;
 if(!complete)fail(TC_PROOF);
 bool captured=complete&&b313_pause_sequence_capture("building313-tail414-snapshot.bmp")&&b313_pause_valid()&&!b313_pause_pending();if(!captured)fail(TC_SNAPSHOT);
 b313_tail414_end(tick);B313Tail414Status lifetime=b313_tail414_status();if(lifetime.failed||!lifetime.finished||!lifetime.taken||!b313_tail414_report())fail(TC_LIFETIME);
 proof_complete=complete&&captured&&!failed;selected=false;
 FILE *file=fopen("building313-tail414-proof.json.tmp","w");if(!file){fail(TC_IO);return;}
 fprintf(file,"{\"tick\":414,\"proof_complete\":%s,\"failed\":%s,\"reasons\":%u,\"old_frames\":%u,\"old_retirement_verified\":%s,\"scene\":%"PRIu64",\"group\":%"PRIu64",\"frame\":%"PRIu64",\"native_epoch\":%"PRIu64",\"sample_epoch\":%"PRIu64",\"old_scene\":%"PRIu64",\"old_group\":%"PRIu64",\"old_frame\":%"PRIu64",\"old_native_epoch\":%"PRIu64",\"old_sample_epoch\":%"PRIu64",\"precommit_samples\":%u,\"final_classic_samples\":%u,\"snapshot_captured\":%s,\"new_material_applied\":false,\"write_allowed\":false,\"runtime_eligible\":false,\"v6_runtime_validated\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\",\"scope\":\"Independent same-run lifetime and fresh whole-frame414 CLASSIC observation. No new material or inherited renderer lease.\"}\n",proof_complete?"true":"false",failed?"true":"false",reasons,old_frames,retired?"true":"false",i.scene,g.nonce,i.frame,n.epoch,o->epoch,old_scene,old_group,old_frame,old_native,old_sample,p->matched,f->classic_samples,captured?"true":"false");
 bool bad=ferror(file)!=0;int close_result=fclose(file);if(bad||close_result||rename("building313-tail414-proof.json.tmp","building313-tail414-proof.json")){remove("building313-tail414-proof.json.tmp");fail(TC_IO);}
}

#else
/* Disabled orchestration has no state, IO, recovery or write permission. */
void b313_tail414_control_old_end(unsigned tick,bool success){(void)tick;(void)success;}
void b313_tail414_control_old_retire(bool success){(void)success;}
void b313_tail414_control_begin(unsigned tick){(void)tick;}
void b313_tail414_control_end(unsigned tick){(void)tick;}
bool b313_tail414_probe_tick(unsigned tick){(void)tick;return false;}
bool b313_tail414_material_write_tick(unsigned tick){(void)tick;return false;}
bool b313_tail414_material_save_prefix(uint64_t nonce,uint64_t preparation_id)
{(void)nonce;(void)preparation_id;return false;}
#endif
