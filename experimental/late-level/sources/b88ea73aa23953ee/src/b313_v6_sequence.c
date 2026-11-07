#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
#if !B313_V6_ANIMATION_DIAGNOSTIC || !B313_V6_TRANSACTION_DIAGNOSTIC || !B313_V6_LOCK_DIAGNOSTIC || !B313_V6_PREPARATION_DIAGNOSTIC || !BUILDING313_PRECOMMIT_DIAGNOSTIC || !BUILDING313_FINAL_PROOF_DIAGNOSTIC || !NATIVE_WRITER_SCOPE_DIAGNOSTIC
#error The four-frame diagnostic requires every existing proof module
#endif
#include "b313_v6_slice.h"
#include "b313_v6_lock_bridge.h"
#include "b313_v6_prefix_preparation.h"
#include "b313_v6_transaction.h"
#include "building313_precommit.h"
#include "building313_final_proof.h"
#include "building313_identity.h"
#include "building313_snapshot_transaction.h"
#include "native_writer_scope.h"
#include "native_writer_observer.h"
#include "old_hd_sample_observer.h"
#include "common_pause.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <limits.h>
static bool initialized,enabled,started,ended,halted,retired;
static unsigned previous,halt_reason,level_events,last_level_event;
static uint64_t last_lock,last_preparation,last_native,last_sample,last_frame;
enum {SQ_ORDER=1u,SQ_RETIRE=2u,SQ_PROOF=4u,SQ_EVENT=8u,SQ_SNAPSHOT=16u,SQ_IO=32u};
bool b313_sequence_enabled(void)
{
 if(!initialized){const char *v=getenv("BUILDING313_V6_SEQUENCE_ENABLE");enabled=v&&!strcmp(v,"1");initialized=true;}
 return enabled;
}
static void halt(unsigned why)
{halted=true;halt_reason|=why;b313_v6_lock_revoke();nwo_revoke_frame(NWO_GAP_UNREGISTERED);ohs_revoke(OHS_REASON_SCOPE);b313_scene_end();(void)b313_v6_prefix_frame_retire();}
void b313_sequence_before_level_event(unsigned type)
{
 /* This explicit hook is the level-script domain, unlike keyboard SDL events. */
 if(b313_recovery_enabled()||!b313_sequence_enabled()||!started||ended||previous<408||previous>410)return;
 if(level_events==UINT_MAX){halt(SQ_ORDER);return;}
 ++level_events;last_level_event=type;
 /* Revoke before JE_eventSystem enters its switch or mutates gameplay state. */
 nws_before_event(type);
}
void b313_sequence_begin(unsigned tick)
{
 if(b313_recovery_enabled()){b313_recovery_begin(tick);return;}
 if(!b313_sequence_enabled())return;
 if(tick<408){if(started)halt(SQ_ORDER);b313_slice_sequence_frame(tick,false);return;}
 if(tick>411){if(started&&!ended)halt(SQ_ORDER);b313_slice_sequence_frame(tick,false);return;}
 if((!started&&tick!=408)||(started&&(!ended||tick!=previous+1)))halt(SQ_ORDER);
 started=true;previous=tick;ended=false;level_events=last_level_event=0;
 /* Old snapshot storage may be reused, but never remains a valid prior frame. */
 retired=b313_pause_sequence_retire();if(!retired)halt(SQ_RETIRE);
 if(!halted){
  if(!b313_v6_prefix_frame_retire()||!b313_v6_lock_frame_retire()||!b313_v6_transaction_frame_retire()||
     !b313_precommit_frame_retire()||!b313_final_frame_retire()||!nws_sequence_frame_retire()||!ohs_sequence_frame_retire())halt(SQ_RETIRE);
 }
 /* 411 is an explicit retired continuation, never a new identity/permit. */
 if(tick==411&&!halted)halt(SQ_PROOF);
 b313_slice_sequence_frame(tick,!halted);
}
void b313_sequence_end(unsigned tick)
{
 if(b313_recovery_enabled()){b313_recovery_end(tick);return;}
 if(!b313_sequence_enabled()||tick<408||tick>411)return;
 if(!started||ended||tick!=previous){halt(SQ_ORDER);return;}
 const B313V6TransactionStatus *t=b313_v6_transaction_status();
 const B313V6LockStatus *l=b313_v6_lock_status();
 const B313PreStatus *p=b313_precommit_status();
 const B313FinalStatus *f=b313_final_status();
 const OhsStatus *o=ohs_status();NwsStatus n=nws_status();B313Status i=b313_status();
 bool current=t->attempted&&t->tick==tick,applied=current&&t->applied;
 bool event=level_events&&n.enabled&&n.tick==tick&&n.events>=level_events;
 if(!halted&&tick<410){
  bool ok=current&&applied&&t->rows_written==448&&!t->rollback_rows&&!t->reasons&&t->flushed&&!t->io_failed&&
   t->unlocked&&t->present_calls==1&&t->snapshot_valid&&!t->snapshot_pending&&
   l->tick==tick&&l->before_unlock_verified&&l->closed&&l->transaction_claimed&&!l->reasons&&l->flushed&&!l->io_failed&&
   p->tick==tick&&p->consumed&&!p->reasons&&p->flushed&&!p->io_failed&&
   f->tick==tick&&f->reported&&!f->io_failed&&!f->valid&&
   n.enabled&&n.tick==tick&&n.valid&&n.sealed&&!n.active&&!n.events&&!n.reasons&&n.reported&&!n.io_failed&&
   o->selected&&o->tick==tick&&o->valid_subset&&o->committed&&o->present_count==1&&
   i.tracking&&i.scene_valid&&!i.sampling&&i.tick==tick&&i.identity_groups==1&&i.calls==16&&!i.reasons&&
   l->nonce>last_lock&&l->prefix.preparation_id>last_preparation&&l->prefix.native_epoch>last_native&&l->prefix.sample_epoch>last_sample&&i.frame>last_frame;
  if(!ok)halt(SQ_PROOF);
  else{last_lock=l->nonce;last_preparation=l->prefix.preparation_id;last_native=l->prefix.native_epoch;last_sample=l->prefix.sample_epoch;last_frame=i.frame;}
 }
 if(tick==410&&!halted){
  /* Original nws_fail must have retired the scene; never reconstruct its birth. */
  if(!event||last_level_event!=19||n.last_event!=19||n.valid||i.tracking||i.scene_valid||applied||(current&&t->rows_written))halt(SQ_PROOF);
  if(event)halt(SQ_EVENT);
 }
 if(tick==411&&(current||applied||i.tracking))halt(SQ_PROOF);
 char snapshot[96],report[96],tmp[100];
 snprintf(snapshot,sizeof(snapshot),"building313-sequence-snapshot-%04u.bmp",tick);
 bool captured=b313_pause_sequence_capture(snapshot);if(!captured)halt(SQ_SNAPSHOT);
 i=b313_status(); /* Current post-revocation state, not the proof-time copy. */
 snprintf(report,sizeof(report),"building313-v6-sequence-%04u.json",tick);snprintf(tmp,sizeof(tmp),"%s.tmp",report);
 FILE *file=fopen(tmp,"w");if(!file){halt(SQ_IO);ended=true;return;}
 fprintf(file,"{\n\"tick\":%u,\"expected_phase\":%u,\"expected_top\":%u,\"new_material_applied\":%s,\"current_transaction\":%s,\"rows_written\":%u,\"snapshot_retired_at_begin\":%s,\"snapshot_valid\":%s,\"snapshot_pending\":%s,\"snapshot_captured\":%s,\"halted\":%s,\"halt_reason\":%u,\"level_event_observed_this_frame\":%s,\"level_event_count\":%u,\"last_level_event_type\":%u,\"event_domain\":\"level-script\",\"scene_tracking\":%s,\"scene_valid\":%s,\"lock_nonce\":%"PRIu64",\"preparation_id\":%"PRIu64",\"native_epoch\":%"PRIu64",\"sample_epoch\":%"PRIu64",\"identity_frame\":%"PRIu64",\"runtime_eligible\":false,\"v6_runtime_validated\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\",\"scope\":\"Fixed408-411 same-process segment. Only408/409 phase1 may write.410 explicit level-script hook ends identity,411 stays original output. Snapshot BMP is current committed cache, readback is before Present, no P/ESC proof.\"\n}\n",tick,tick<410?1u:2u,tick-307,applied?"true":"false",current?"true":"false",current?t->rows_written:0,retired?"true":"false",b313_pause_valid()?"true":"false",b313_pause_pending()?"true":"false",captured?"true":"false",halted?"true":"false",halt_reason,event?"true":"false",level_events,last_level_event,i.tracking?"true":"false",i.scene_valid?"true":"false",current?l->nonce:0,current?l->prefix.preparation_id:0,current?l->prefix.native_epoch:0,current?l->prefix.sample_epoch:0,i.frame);
 bool bad=ferror(file)!=0;int closed=fclose(file);if(bad||closed||rename(tmp,report)){remove(tmp);halt(SQ_IO);}
 ended=true;
}
#else
typedef int b313_v6_sequence_disabled_translation_unit;
#endif
