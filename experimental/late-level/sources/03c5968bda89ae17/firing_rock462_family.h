#ifndef FIRING_ROCK462_FAMILY_H
#define FIRING_ROCK462_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
enum { FIRING_ROCK462_HD_STORE_TAG = 13, FIRING_ROCK462_EXTRA_STORE_TAG = 19 }; /* Existing normal HD material store tag. */
typedef struct {uint8_t x,y,index;} FiringRock462Write;
typedef struct {
 uint64_t epoch,token,generation,bank_stamp,record_stamp;
 unsigned slot,record,bank_role,bank_bytes,birth_time;
 uintptr_t bank_object,bank_data;
 int birth_x,birth_y,birth_eyc;
 bool live,initialized;
 uint64_t birth_frame,retired_frame,phase_tick,phase_observations,shot_count,last_shot_frame;
 unsigned cycle,gate,retirement_reason;int retired_y;
} FiringRock462Birth;
typedef struct {
 uint64_t frame,epoch,token,generation;
 unsigned slot,record,base,cur_loc,bank_role,bank_bytes;
 uintptr_t bank_object,bank_data;
 unsigned cycle,draw_gate,draw_filter,final_gate,extra_stores;bool shot_resumed;
 int x,y; /* Actual whole-body draw origin, never postmovement coordinates. */
 unsigned mask,next,callback_count,part_count[4],part_order[4];
 bool complete;
} FiringRock462Draw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted,active,pending;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults;
 unsigned first_reason,material_mask,witnessed_records,active_slot,active_part,surviving_cells,shadowed_cells;
 uint64_t witnessed_count[1]; /* type462 only. */
 uint64_t phase_observations,shot_resumptions,filtered_fallbacks,extra_retirements;
 unsigned extra_pixels;
 FiringRock462Birth births[25]; /* pool slots0..24; historical witnesses survive retirement. */
 FiringRock462Draw draw[25];
} FiringRock462FamilyStatus;
/* Diagnostic getters neither admit rendering nor change gameplay.
 * pre_draw: actual whole192x224 RGB /24x28 indexed crop, after part0 prepare
 * and before the first native store. Callback receipts are full-body local
 * x/y/index triples, concatenated in exact original four-call order.
 * Support owner is actual slot+1, independent of selected[] and art alpha. */
FiringRock462FamilyStatus render_mirror_firing_rock462_family_status(void);
bool render_mirror_firing_rock462_pre_draw(FiringRock462Draw *,uint32_t *,size_t,uint8_t *,size_t);
/* pre_part: 10752 RGB pixels, 168 native bytes, original native part number. */
bool render_mirror_firing_rock462_pre_part(FiringRock462Draw *,unsigned *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_firing_rock462_callbacks(unsigned,FiringRock462Write *,size_t);
bool render_mirror_firing_rock462_family_support(uint8_t *,size_t,uint8_t *,size_t);
/* Separate authored RGB support; no native or INDEX ownership is inferred. */
bool render_mirror_firing_rock462_extra_support(uint8_t *,size_t);
#endif
