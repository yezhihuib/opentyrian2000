#ifndef B313_TAIL414_H
#define B313_TAIL414_H
#include "b313_v6_prefix_preparation.h"
typedef struct {
 bool enabled,active,failed,birth_seen,anchored,pending,taken,finished,candidate_ready;
 bool runtime_eligible,v6_runtime_validated,write_allowed;
 unsigned reasons,tick,events,allocations,census_reads;
 uint64_t allocation_serial,generation[100],resource_epoch[4],anchor_preparation;
} B313Tail414Status;
bool b313_tail414_enabled(void);
void b313_tail414_lifetime_begin(bool target);
void b313_tail414_allocated(unsigned slot);
void b313_tail414_resource(unsigned pool);
void b313_tail414_birth(const B313Group *group);
/* Call only AFTER complete409 transaction, snapshot AND recovery report succeed. */
void b313_tail414_anchor409(const B313V6PrefixEvidence *e);
void b313_tail414_event_before(unsigned tick,unsigned entry,unsigned type,const int args[6]);
void b313_tail414_event_after(unsigned tick,unsigned entry,unsigned type,const int args[6]);
void b313_tail414_external_event(unsigned tick);
/* Diagnostic-only details; rejection predicate remains unchanged. */
void b313_tail414_external_event_detail(unsigned tick,unsigned domain,unsigned type);
void b313_tail414_controller_cancel(unsigned tick);
/* Service switch diagnostics; never changes event dispatch or admission. */
bool b313_tail414_window_dispatch_begin(unsigned tick,unsigned domain,unsigned type,unsigned window_id,unsigned subtype,bool focus_before);
void b313_tail414_window_dispatch_end(bool recorded,unsigned handler_branch,bool focus_after);
void b313_tail414_begin(unsigned tick);
void b313_tail414_end(unsigned tick);
bool b313_tail414_take(B313Group *birth,uint64_t generations[100]);
bool b313_tail414_continuity414(void);
B313Tail414Status b313_tail414_status(void);
bool b313_tail414_report(void);
#endif
