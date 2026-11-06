/* Private fixed 409 anchor -> 410 revoke -> 411 fresh proof, default disabled. */
#ifndef B313_V6_RECOVERY_H
#define B313_V6_RECOVERY_H
#include "b313_v6_recovery_witness.h"
#if defined(B313_V6_RECOVERY_DIAGNOSTIC) && B313_V6_RECOVERY_DIAGNOSTIC
bool b313_conservative_enabled(void);
bool b313_conservative_save_prefix(uint64_t nonce,uint64_t preparation_id);
enum {B313_INPUT_SERVICE=1,B313_INPUT_FLUSH=2,B313_INPUT_ASSET_POLL=3,B313_INPUT_ASSET_COMMAND=4};
void b313_recovery_external_event_at(unsigned tick,unsigned domain,unsigned type);
void b313_recovery_begin(unsigned tick);
void b313_recovery_end(unsigned tick);
void b313_recovery_before_event(unsigned tick,unsigned loc,unsigned cur,unsigned type,int d1,int d2,int d3,int d4,int d5,int d6);
bool b313_recovery_permit_ready(void);
bool b313_recovery_write_tick(unsigned tick);
bool b313_identity_reacquire(void);
bool b313_identity_tail414_reacquire(void);
bool nws_recovery_rearm(void);
bool ohs_recovery_rearm(void);
#else
#define b313_conservative_enabled() false
#define b313_conservative_save_prefix(...) false
#define b313_recovery_external_event_at(...) ((void)0)
enum {B313_INPUT_SERVICE=1,B313_INPUT_FLUSH=2,B313_INPUT_ASSET_POLL=3,B313_INPUT_ASSET_COMMAND=4};
#define b313_recovery_begin(...) ((void)0)
#define b313_recovery_end(...) ((void)0)
#define b313_recovery_before_event(...) ((void)0)
#define b313_recovery_permit_ready() false
#define b313_recovery_write_tick(...) false
#endif
#endif
