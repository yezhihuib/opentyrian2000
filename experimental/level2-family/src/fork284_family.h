#ifndef FORK284_FAMILY_H
#define FORK284_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {uint8_t x,y,index;} Fork284Write;
typedef struct {
 uint64_t epoch,token,generation,bank_stamp,record_stamp;
 unsigned slot,event,record,bank_role,bank_bytes,event_time;
 uintptr_t bank_object,bank_data;
 int birth_x,birth_y,birth_eyc;
 bool live,initialized;
} Fork284Birth;
typedef struct {
 uint64_t frame,epoch,token,generation;
 unsigned slot,event,record,base,cur_loc,bank_role,bank_bytes;
 uintptr_t bank_object,bank_data;
 int x,y; /* Actual whole-body draw origin, never postmovement coordinates. */
 unsigned mask,next,callback_count,part_count[4],part_order[4];
 bool complete;
} Fork284Draw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted,active,pending;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults;
 unsigned first_reason,consumed_events,active_slot,active_part,surviving_cells,shadowed_cells;
 Fork284Birth births[25]; /* pool slots50..74; historical witnesses survive retirement. */
 Fork284Draw draw[25];
} Fork284FamilyStatus;
/* Diagnostic getters neither admit rendering nor change gameplay.
 * pre_draw: actual whole192x224 RGB /24x28 indexed crop, after part0 prepare
 * and before the first native store. Callback receipts are full-body local
 * x/y/index triples, concatenated in exact original four-call order.
 * Support owner is actual slot+1, independent of selected[] and art alpha. */
Fork284FamilyStatus render_mirror_fork284_family_status(void);
bool render_mirror_fork284_pre_draw(Fork284Draw *,uint32_t *,size_t,uint8_t *,size_t);
/* pre_part: 10752 RGB pixels, 168 native bytes, original native part number. */
bool render_mirror_fork284_pre_part(Fork284Draw *,unsigned *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_fork284_callbacks(unsigned,Fork284Write *,size_t);
bool render_mirror_fork284_family_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
