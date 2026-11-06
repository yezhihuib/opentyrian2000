/* Private read-only diagnostic. No texture writes or rendering permit API. */
#ifndef B313_V6_LOCK_BRIDGE_H
#define B313_V6_LOCK_BRIDGE_H
#include <stdbool.h>
#include <stdint.h>
#include "b313_v6_prefix_preparation.h"
enum B313V6LockReason { V6L_DISABLED=1u,V6L_PRELOAD=2u,V6L_ORDER=4u,
 V6L_REENTRY=8u,V6L_CONTEXT=16u,V6L_GEOMETRY=32u,V6L_PREFIX=64u,
 V6L_REVOKED=128u,V6L_ECHO=256u,V6L_OVERFLOW=512u };
typedef struct {
 bool attempted,preloaded,probe_attempted,before_unlock_verified,closed,flushed,io_failed;
 bool runtime_eligible,v6_runtime_validated,transaction_claimed;
 unsigned reasons,entries,opens,closes,tick,io_error;
 uint64_t nonce,sample_epoch,query_ticks,query_frequency;
 B313V6PreparationStatus prefix;
} B313V6LockStatus;
#if defined(B313_V6_LOCK_DIAGNOSTIC) && B313_V6_LOCK_DIAGNOSTIC
void b313_v6_lock_preload(bool target);
void b313_v6_lock_revoke(void);
void b313_v6_lock_present_entry(unsigned tick);
uint64_t b313_v6_lock_open(unsigned tick,const void *renderer,const void *texture,
 const void *pixels,int pitch,int width,int height,unsigned density,bool repeat);
void b313_v6_lock_probe(uint64_t nonce,const void *renderer,const void *texture,
 const void *pixels,int pitch,int width,int height,unsigned density);
void b313_v6_lock_close(uint64_t nonce);
bool b313_v6_lock_current(uint64_t nonce);
#if defined(B313_V6_TRANSACTION_DIAGNOSTIC) && B313_V6_TRANSACTION_DIAGNOSTIC
bool b313_v6_lock_claim(uint64_t nonce,const void *renderer,const void *texture,
 const void *pixels,int pitch,int width,int height,unsigned density,uint64_t preparation_id);
#endif
void b313_v6_lock_flush(void);
const B313V6LockStatus *b313_v6_lock_status(void);
#else
#define b313_v6_lock_preload(...) ((void)0)
#define b313_v6_lock_revoke() ((void)0)
#define b313_v6_lock_present_entry(...) ((void)0)
#define b313_v6_lock_open(...) UINT64_C(0)
#define b313_v6_lock_probe(...) ((void)0)
#define b313_v6_lock_close(n) ((void)(n))
#define b313_v6_lock_flush() ((void)0)
#endif
#endif
