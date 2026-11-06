#ifndef B313_CONTINUITY_H
#define B313_CONTINUITY_H
#include "continuity.h"
#include "building313_identity.h"
/* Private observational state only. No caller may turn these facts into a lease. */
enum {BC_ORDER=1,BC_INPUT=2,BC_RESOURCE=4,BC_ALLOC=8,BC_BIRTH=16,BC_SCOPE=32,BC_OVERFLOW=64,BC_IO=128};
typedef struct {
 bool enabled,failed,birth_pending,birth_closed,first_tick_known,raw_args_recorded;
 bool write_allowed,runtime_eligible;
 unsigned reasons,first_reason,first_tick,birth_allocations,resource_notifications;
 uint64_t session,serial,entry_serial,attempt,group,scene,generation[100],resources[4];
 int raw_args[6];
 CoObserver consumption;
} BcoStatus;
bool bco_enabled(void);
void bco_session_begin(bool empty_pool);
uint64_t bco_session(void);
void bco_interrupt(unsigned kind);
uint64_t bco_consumed(unsigned tick,unsigned domain,unsigned type);
void bco_complete(uint64_t token,unsigned domain,unsigned disposition);
void bco_command(void);
void bco_resource(unsigned pool);
void bco_allocated(unsigned slot);
uint64_t bco_birth_begin(const CoContext *,unsigned tick,unsigned entry,unsigned cur,unsigned type,unsigned pool,const int args[6],bool census_known);
void bco_birth_bind(uint64_t attempt,uint64_t group);
void bco_group_complete(const B313Group *);
void bco_birth_end(uint64_t attempt,uint64_t group);
BcoStatus bco_status(void);
void bco_checkpoint(const CoContext *);
/* Reporter-only fail path. Never recursively persists. */
void bco_report_io_failure(void);
/* Read-only adapters over real game state. */
void bco_game_begin(void);
uint64_t bco_game_birth(unsigned tick,unsigned entry,unsigned cur,unsigned type,unsigned pool,const int args[6]);
void bco_game_checkpoint(void);
#endif
