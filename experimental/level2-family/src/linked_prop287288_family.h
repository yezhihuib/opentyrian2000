#ifndef LINKED_PROP287288_FAMILY_H
#define LINKED_PROP287288_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
enum { LINKED_PROP287288_HD_STORE_TAG=13 };
enum { LP287_OFFSCREEN=1,LP287_DIRECT_LETHAL=2,LP287_LINKED_LETHAL=3,
 LP287_DAMAGE_TRANSFORM=4,LP287_EVENT_RETIRE=5,LP287_BANK=6,LP287_REUSE=7,LP287_INVALIDATED=8 };
typedef struct {uint8_t x,y,index;} LinkedProp287288Write;
typedef struct {
 uint64_t epoch,token,generation,bank_stamp,record_stamp;
 unsigned slot,record,event,link,bank_role,bank_bytes,birth_time;
 uintptr_t bank_object,bank_data;
 int birth_x,birth_y,birth_eyc;
 bool live,initialized;
 uint64_t birth_frame,retired_frame,phase_tick,phase_observations;
 unsigned cycle,gate,retirement_reason;int retired_y;
 uint64_t hit_count,last_hit_token,last_hit_frame,retirement_hit_token;
 unsigned hit_damage,hit_armor_before,hit_armor_after,hit_source_slot,retirement_source_slot;
} LinkedProp287288Birth;
typedef struct {
 uint64_t frame,epoch,token,generation;
 unsigned slot,record,event,link,base,cur_loc,bank_role,bank_bytes;
 uintptr_t bank_object,bank_data;
 unsigned cycle,draw_gate,draw_filter,final_gate;
 int x,y;
 unsigned mask,next,callback_count,part_count[4],part_order[4];bool complete;
} LinkedProp287288Draw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted,active,pending;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults;
 unsigned first_reason,material_mask,witnessed_records,consumed_events,active_slot,active_part,surviving_cells,shadowed_cells;
 uint64_t witnessed_count[2],phase_observations,hit_count,linked_retirements;
 LinkedProp287288Birth births[100];
 LinkedProp287288Draw draw[100];
} LinkedProp287288FamilyStatus;
/* Read-only diagnostics. Full-body pre_draw is 43008 RGB pixels /672 INDEX
 * bytes. pre_part is 10752 RGB /168 INDEX bytes. Native holes have no owner. */
LinkedProp287288FamilyStatus render_mirror_linked_prop287288_family_status(void);
bool render_mirror_linked_prop287288_pre_draw(LinkedProp287288Draw *,uint32_t *,size_t,uint8_t *,size_t);
bool render_mirror_linked_prop287288_pre_part(LinkedProp287288Draw *,unsigned *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_linked_prop287288_callbacks(unsigned,LinkedProp287288Write *,size_t);
bool render_mirror_linked_prop287288_family_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
