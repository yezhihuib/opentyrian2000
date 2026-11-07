#ifndef B313_CONTINUITY_MODEL_H
#define B313_CONTINUITY_MODEL_H
#include <stdbool.h>
#include <stdint.h>
/* Isolated non-authorizing model. No game hooks, renderer handles or asset APIs. */
enum CoDomain {CO_SERVICE=1,CO_FLUSH=2,CO_ASSET_POLL=3};
enum CoDisposition {CO_HANDLED=1,CO_DISCARDED=2};
enum CoInterrupt {CO_DEMO_END=1,CO_UI_PAUSE=2,CO_UI_MENU=3,CO_LEVEL_CHANGE=4,CO_EARLY_EXIT=5,CO_ASSET_COMMAND=6};
enum CoReason {CO_ORDER=1,CO_PENDING=2,CO_PAIR=4,CO_SCOPE=8,CO_RESIDUAL=16,CO_INTERRUPTED=32,CO_OVERFLOW=64};
enum CoResidual {CO_NEWKEY=1,CO_NEWMOUSE=2,CO_KEYS_HELD=4,CO_MOUSE_HELD=8,CO_PAUSE_REQUEST=16,CO_MENU_REQUEST=32,CO_DEBUG_PENDING=64,CO_ALL_RESIDUAL=127};
typedef struct {
 bool known,probe,asset_debug,demo,record,network,stopped_demo,end_requested;
 unsigned episode,level,residual_known,residual;
 uint64_t session;
 /* Focus is intentionally absent: this exact demo branch does not pause on it. */
} CoContext;
typedef struct {
 bool begun,failed,interrupted,pending,boundary_observed;
 bool write_allowed,runtime_eligible;
 unsigned reasons,first_reason,interrupt_kind,pending_domain,pending_tick,pending_type;
 uint64_t session,received,handled,discarded,commands,command_parent,pending_seq,boundary_seq;
} CoObserver;
bool co_begin(CoObserver *o,uint64_t session);
uint64_t co_consumed(CoObserver *o,unsigned domain,unsigned tick,unsigned type);
bool co_complete(CoObserver *o,uint64_t seq,unsigned domain,unsigned disposition);
void co_interrupt(CoObserver *o,unsigned kind);
void co_command(CoObserver *o);
bool co_observe_boundary(CoObserver *o,const CoContext *context);
#endif
