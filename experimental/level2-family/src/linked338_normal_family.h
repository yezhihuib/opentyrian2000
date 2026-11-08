#ifndef LINKED338_NORMAL_FAMILY_H
#define LINKED338_NORMAL_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {uint8_t x,y,index;} Linked338NormalWrite;
struct Linked338NormalExtra {uint8_t x,y;};
typedef struct {
 uint64_t epoch,token,generation,bank_stamp,record_stamp;
 unsigned slot,event,record,bank_role,bank_bytes,event_time;
 uintptr_t bank_object,bank_data;
 int birth_x,birth_y,birth_eyc;
 unsigned link,component,cycle,gate; uint64_t phase_tick,phase_observations,shot_count;
 bool live,initialized;
} Linked338NormalBirth;
typedef struct {
 uint64_t frame,epoch,token,generation;
 unsigned slot,event,record,base,cur_loc,bank_role,bank_bytes;
 uintptr_t bank_object,bank_data;
 int x,y; /* Actual whole-body draw origin, never postmovement coordinates. */
 unsigned mask,next,callback_count,part_count[4],part_order[4];
 unsigned cycle,draw_gate,extra_stores; bool shot_resumed,complete;
} Linked338NormalDraw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted,active,pending;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults;
 uint64_t phase_observations,shot_resumptions,extra_retirements; unsigned extra_pixels;
 unsigned first_reason,consumed_events,active_slot,active_part,surviving_cells,shadowed_cells;
 Linked338NormalBirth births[100]; /* exact pool25..49; historical witnesses survive retirement. */
 Linked338NormalDraw draw[100];
} Linked338NormalFamilyStatus;
/* Diagnostic getters neither admit rendering nor change gameplay.
 * pre_draw: actual whole192x224 RGB /24x28 indexed crop, after part0 prepare
 * and before the first native store. Callback receipts are full-body local
 * x/y/index triples, concatenated in exact original four-call order.
 * Support owner is actual slot+1, independent of selected[] and art alpha. */
Linked338NormalFamilyStatus render_mirror_linked338_normal_family_status(void);
bool render_mirror_linked338_normal_pre_draw(Linked338NormalDraw *,uint32_t *,size_t,uint8_t *,size_t);
/* pre_part: 10752 RGB pixels, 168 native bytes, original native part number. */
bool render_mirror_linked338_normal_pre_part(Linked338NormalDraw *,unsigned *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_linked338_normal_callbacks(unsigned,Linked338NormalWrite *,size_t);
bool render_mirror_linked338_normal_family_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
