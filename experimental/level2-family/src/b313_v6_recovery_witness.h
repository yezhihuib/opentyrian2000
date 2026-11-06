/* Non-authorizing lifetime facts for the fixed 409 -> 410 -> 411 experiment. */
#ifndef B313_V6_RECOVERY_WITNESS_H
#define B313_V6_RECOVERY_WITNESS_H
#include "building313_identity.h"
typedef struct {
 bool active,failed,birth_seen,anchored,event_seen,census410,census411,taken;
 unsigned reasons,last_census,event_cur_loc;
 unsigned census_reads,census_members;
 uint64_t slot_generation[4];
 B313Snapshot current[4];
 unsigned current_links[4];
 uint64_t anchor_serial,anchor_resources[4];
 uint64_t allocation_serial,resource_epoch[4];
} B313RecoveryStatus;
#if defined(B313_V6_RECOVERY_DIAGNOSTIC) && B313_V6_RECOVERY_DIAGNOSTIC
bool b313_recovery_enabled(void);
void b313_recovery_lifetime_begin(bool target);
void b313_recovery_lifetime_end(void);
void b313_recovery_allocated(unsigned slot);
void b313_recovery_resource(unsigned pool);
void b313_recovery_birth(const B313Group *g);
bool b313_recovery_anchor_prepare(const B313Group *g);
bool b313_recovery_anchor(const B313Group *g);
void b313_recovery_event(unsigned tick,unsigned event_loc,unsigned cur_loc,unsigned type,int d1,int d2,int d3,int d4,int d5,int d6);
bool b313_recovery_census(unsigned tick);
bool b313_recovery_take(B313Group *birth,uint64_t gens[100]);
bool b313_recovery_continuity(void);
B313RecoveryStatus b313_recovery_status(void);
bool b313_recovery_read_slot(unsigned slot,B313Snapshot *out,unsigned *link);
/* Only the true pre-first-draw constructor state may create birth facts. */
bool b313_recovery_read_birth(unsigned slot,B313Snapshot *out,unsigned *link);
#else
/* Disabled readers never inspect game state or grant a lifetime fact.
 * Clear caller-owned outputs so stale observations cannot survive a refusal. */
static inline bool b313_recovery_read_slot(unsigned slot,B313Snapshot *out,unsigned *link)
{
 (void)slot;
 if(out)*out=(B313Snapshot){0};
 if(link)*link=0;
 return false;
}
static inline bool b313_recovery_read_birth(unsigned slot,B313Snapshot *out,unsigned *link)
{return b313_recovery_read_slot(slot,out,link);}
#define b313_recovery_enabled() false
#define b313_recovery_lifetime_begin(...) ((void)0)
#define b313_recovery_lifetime_end() ((void)0)
#define b313_recovery_allocated(...) ((void)0)
#define b313_recovery_resource(...) ((void)0)
#define b313_recovery_birth(...) ((void)0)
#define b313_recovery_anchor_prepare(...) false
#define b313_recovery_anchor(...) false
#define b313_recovery_event(...) ((void)0)
#define b313_recovery_census(...) false
#define b313_recovery_take(...) false
#define b313_recovery_continuity() false
#define b313_recovery_status() ((B313RecoveryStatus){0})
#endif
#endif
