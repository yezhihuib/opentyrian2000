/* Private locked-ROI experiment. Runtime payload is echo only. */
#ifndef BUILDING313_SNAPSHOT_TRANSACTION_H
#define BUILDING313_SNAPSHOT_TRANSACTION_H
#include "SDL.h"
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#define B313_TXN_MAGIC UINT32_C(0x42333133)
#define B313_TXN_ROI_BYTES ((size_t)384*448*4)
typedef struct {uint32_t magic;unsigned width,height,pitch;size_t bytes;const void *data;uint64_t checksum;} B313TxnPayload;
enum B313TxnReason { BTX_SCOPE=1u,BTX_GEOMETRY=2u,BTX_PREFIX=4u,BTX_MISSING=8u,BTX_PAYLOAD=16u,
 BTX_ALLOC=32u,BTX_WRITE=64u,BTX_SNAPSHOT=128u,BTX_REPEAT=256u,BTX_ORDER=512u };
typedef struct {
 bool attempted,configured,echo_only,precommit_allow,prepared,wrote,applied,rolled_back,observer_unknown;
 bool snapshot_ready,unlocked,present_called,submit_failed,snapshot_pending,snapshot_valid,flushed,io_failed;
 unsigned tick,reasons,rows_written,rollback_rows,snapshot_calls,present_calls,io_error;
 uint64_t validation_ticks,application_ticks,snapshot_ticks,counter_frequency;
} B313TxnStatus;
#if (defined(BUILDING313_SNAPSHOT_TRANSACTION_DIAGNOSTIC) && BUILDING313_SNAPSHOT_TRANSACTION_DIAGNOSTIC) || (defined(B313_V6_TRANSACTION_DIAGNOSTIC) && B313_V6_TRANSACTION_DIAGNOSTIC)
bool b313_pause_stage_checked(SDL_Surface *src,const void *rgba,int pitch,int width,int height,unsigned density,const SDL_Rect *roi);
bool b313_pause_pending(void);
bool b313_pause_valid(void);
#endif
#if defined(BUILDING313_SNAPSHOT_TRANSACTION_DIAGNOSTIC) && BUILDING313_SNAPSHOT_TRANSACTION_DIAGNOSTIC
bool b313_snapshot_transaction_enabled(unsigned tick);
void b313_snapshot_transaction_locked(unsigned tick,SDL_Surface *src,void *pixels,int pitch,int width,int height,unsigned density,bool configured,bool single_present);
void b313_snapshot_transaction_unlocked(void);
void b313_snapshot_transaction_submit(bool called);
void b313_snapshot_transaction_flush(void);
const B313TxnStatus *b313_snapshot_transaction_status(void);
#ifdef BUILDING313_SNAPSHOT_TRANSACTION_TESTING
void b313_snapshot_transaction_test_locked(unsigned tick,SDL_Surface *src,void *pixels,int pitch,int width,int height,unsigned density,bool configured,bool single_present,const B313TxnPayload *payload,int fail_after_rows);
#endif
#else
#define b313_snapshot_transaction_enabled(...) false
#define b313_snapshot_transaction_locked(...) ((void)0)
#define b313_snapshot_transaction_unlocked() ((void)0)
#define b313_snapshot_transaction_submit(...) ((void)0)
#define b313_snapshot_transaction_flush() ((void)0)
#endif
#endif
