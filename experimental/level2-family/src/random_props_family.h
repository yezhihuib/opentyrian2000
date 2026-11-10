#ifndef RANDOM_PROPS_FAMILY_H
#define RANDOM_PROPS_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
enum { RANDOM_PROPS_HD_STORE_TAG = 13 }; /* Existing normal HD material store tag. */
typedef struct {uint8_t x,y,index;} RandomPropsWrite;
typedef struct {
 uint64_t epoch,token,generation,bank_stamp,record_stamp;
 unsigned slot,record,bank_role,bank_bytes,birth_time;
 uintptr_t bank_object,bank_data;
 int birth_x,birth_y,birth_eyc;
 bool live,initialized;
} RandomPropsBirth;
typedef struct {
 uint64_t frame,epoch,token,generation;
 unsigned slot,record,base,cur_loc,bank_role,bank_bytes;
 uintptr_t bank_object,bank_data;
 int x,y; /* Actual whole-body draw origin, never postmovement coordinates. */
 unsigned mask,next,callback_count,part_count[4],part_order[4];
 bool complete;
} RandomPropsDraw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted,active,pending;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults;
 unsigned first_reason,material_mask,witnessed_records,active_slot,active_part,surviving_cells,shadowed_cells;
 uint64_t witnessed_count[8]; /* record order135,136,260,261,263,265,266,268. */
 RandomPropsBirth births[25]; /* pool slots0..24; historical witnesses survive retirement. */
 RandomPropsDraw draw[25];
} RandomPropsFamilyStatus;
/* Diagnostic getters neither admit rendering nor change gameplay.
 * pre_draw: actual whole192x224 RGB /24x28 indexed crop, after part0 prepare
 * and before the first native store. Callback receipts are full-body local
 * x/y/index triples, concatenated in exact original four-call order.
 * Support owner is actual slot+1, independent of selected[] and art alpha. */
RandomPropsFamilyStatus render_mirror_random_props_family_status(void);
bool render_mirror_random_props_pre_draw(RandomPropsDraw *,uint32_t *,size_t,uint8_t *,size_t);
/* pre_part: 10752 RGB pixels, 168 native bytes, original native part number. */
bool render_mirror_random_props_pre_part(RandomPropsDraw *,unsigned *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_random_props_callbacks(unsigned,RandomPropsWrite *,size_t);
bool render_mirror_random_props_family_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
