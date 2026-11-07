#ifndef COMPOUND309270_FAMILY_H
#define COMPOUND309270_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
enum { COMPOUND309270_HD_STORE_TAG=14 };
enum { C309_OFFSCREEN=1,C309_DIRECT_LETHAL=2,C309_LINKED_LETHAL=3,
 C309_DAMAGE_TRANSFORM=4,C309_EVENT_RETIRE=5,C309_BANK=6,C309_REUSE=7,C309_INVALIDATED=8 };
typedef struct {uint8_t x,y,index;} Compound309270Write;
typedef struct {
 uint64_t epoch,token,generation,bank_stamp,record_stamp;
 unsigned slot,record,event,link,bank_role,bank_bytes,birth_time;
 uintptr_t bank_object,bank_data;
 int birth_x,birth_y,birth_eyc;
 bool live,initialized;
 uint64_t birth_frame,retired_frame,phase_tick,phase_observations,shot_count,last_shot_frame;
 unsigned last_shot_weapon,last_shot_turret,last_shot_slot;uint64_t shot_weapon_count[2];
 unsigned cycle,gate,retirement_reason;int retired_y;
 uint64_t hit_count,last_hit_token,last_hit_frame,retirement_hit_token;
 unsigned hit_damage,hit_armor_before,hit_armor_after,hit_source_slot,retirement_source_slot;
} Compound309270Birth;
typedef struct {
 uint64_t frame,epoch,token,generation;
 unsigned slot,record,event,link,base,cur_loc,bank_role,bank_bytes;
 uintptr_t bank_object,bank_data;
 unsigned cycle,draw_gate,draw_filter,final_gate;
 int x,y;
 unsigned mask,next,callback_count,part_count[4],part_order[4];bool complete,shot_resumed;
} Compound309270Draw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted,active,pending;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults;
 unsigned first_reason,material_mask,witnessed_records,consumed_events,active_slot,active_part,surviving_cells,shadowed_cells;
 uint64_t witnessed_count[5],phase_observations,hit_count,linked_retirements,shot_resumptions;
 Compound309270Birth births[100];
 Compound309270Draw draw[100];
} Compound309270FamilyStatus;
/* Read-only diagnostics. Full-body pre_draw is 43008 RGB pixels /672 INDEX
 * bytes. pre_part is 10752 RGB /168 INDEX bytes. Native holes have no owner. */
Compound309270FamilyStatus render_mirror_compound309270_family_status(void);
bool render_mirror_compound309270_pre_draw(Compound309270Draw *,uint32_t *,size_t,uint8_t *,size_t);
bool render_mirror_compound309270_pre_part(Compound309270Draw *,unsigned *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_compound309270_callbacks(unsigned,Compound309270Write *,size_t);
bool render_mirror_compound309270_family_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
