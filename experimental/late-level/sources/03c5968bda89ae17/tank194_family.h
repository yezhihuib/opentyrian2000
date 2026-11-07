#ifndef TANK194_FAMILY_H
#define TANK194_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {uint8_t x,y,index;} Tank194Write;
typedef struct {
 uint64_t epoch,token,generation,bank_stamp,record_stamp;
 unsigned slot,event,record,bank_role,bank_bytes,event_time,link;
 uintptr_t bank_object,bank_data;
 int birth_x,birth_y,birth_eyc;
 bool live,initialized;
} Tank194Birth;
typedef struct {
 uint64_t frame,epoch,token,generation,script_serial;
 unsigned slot,event,record,base,pose,cur_loc,bank_role,bank_bytes,script_event;
 uintptr_t bank_object,bank_data;
 int x,y; /* Saved whole-body origin; no postmovement position comparison. */
 unsigned mask,next,callback_count,part_count[4],part_order[4];
 bool complete;
} Tank194Draw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted,active,pending;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults,script_losses;
 unsigned first_reason,consumed_events,active_slot,active_part,surviving_cells,shadowed_cells;
 unsigned next_event,mutable_event31_result;
 Tank194Birth births[25]; /* Pool slots75..99; historical witnesses persist. */
 Tank194Draw draw[25];
} Tank194FamilyStatus;
/* Pure diagnostics. pre_draw: actual192x224 RGB and24x28 native crop.
 * pre_part: actual96x112 RGB and12x14 native crop before native stores.
 * Writes are exact ordered whole-body-local x/y/native-index triples.
 * Support is actual slot+1 ownership, independent of art alpha/selected[]. */
Tank194FamilyStatus render_mirror_tank194_family_status(void);
bool render_mirror_tank194_family_pre_draw(Tank194Draw *,uint32_t *,size_t,uint8_t *,size_t);
bool render_mirror_tank194_family_pre_part(Tank194Draw *,unsigned *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_tank194_family_callbacks(unsigned,Tank194Write *,size_t);
bool render_mirror_tank194_family_support(uint8_t *,size_t,uint8_t *,size_t);
bool render_mirror_tank194_family_canvas_part(int,int,uint32_t *,size_t,uint8_t *,size_t);
#endif
