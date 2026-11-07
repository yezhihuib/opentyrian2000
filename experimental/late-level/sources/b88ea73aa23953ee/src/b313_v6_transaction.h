/* Private single-frame legal phase0 transaction. Not production admission. */
#ifndef B313_V6_TRANSACTION_H
#define B313_V6_TRANSACTION_H
#include "SDL.h"
#include <stdbool.h>
#include <stdint.h>
enum B313V6TransactionReason {V6T_CONTEXT=1u,V6T_GEOMETRY=2u,V6T_PREFIX=4u,
 V6T_ALLOC=8u,V6T_WRITE=16u,V6T_SNAPSHOT=32u,V6T_REPEAT=64u,V6T_ORDER=128u,V6T_ECHO=256u};
typedef struct {
 bool attempted,claimed,wrote,applied,rolled_back,observer_unknown,unlocked;
 bool snapshot_ready,snapshot_pending,snapshot_valid,present_called,submit_failed;
 bool flushed,io_failed,runtime_eligible,v6_runtime_validated;
 unsigned tick,reasons,rows_written,rollback_rows,snapshot_calls,present_calls;
 uint64_t nonce,preparation_id,pack_generation;
} B313V6TransactionStatus;
#if defined(B313_V6_TRANSACTION_DIAGNOSTIC) && B313_V6_TRANSACTION_DIAGNOSTIC
bool b313_v6_transaction_enabled(unsigned tick);
void b313_v6_transaction_locked(uint64_t nonce,unsigned tick,const void *renderer,const void *texture,
 SDL_Surface *src,void *pixels,int pitch,int width,int height,unsigned density,bool configured,bool single_present);
void b313_v6_transaction_unlocked(void);
void b313_v6_transaction_submit(bool called);
void b313_v6_transaction_flush(void);
const B313V6TransactionStatus *b313_v6_transaction_status(void);
#ifdef B313_V6_TRANSACTION_TESTING
/* Bounded control-flow faults only. Never changes/shortens package bytes. */
void b313_v6_transaction_test_faults(int stop_after_rows,bool fail_first_stage);
#endif
#else
#define b313_v6_transaction_enabled(...) false
#define b313_v6_transaction_locked(...) ((void)0)
#define b313_v6_transaction_unlocked() ((void)0)
#define b313_v6_transaction_submit(...) ((void)0)
#define b313_v6_transaction_flush() ((void)0)
#endif
#endif
