#ifndef COMBAT_FAMILY_H
#define COMBAT_FAMILY_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
enum { COMBAT_PULSE=1,COMBAT_HITFLARE=2,COMBAT_SMALL_EXPLOSION=3,
 COMBAT_NATIVE_STORE_TAG=13,COMBAT_EXTRA_STORE_TAG=19,COMBAT_MAX_DRAWS=562 };
typedef struct {uint8_t x,y,index;} CombatWrite;
typedef struct {
 uint64_t serial,generation,frame;unsigned kind,slot,record,phase,role,initial_ttl;
 int x,y,delta_y;bool witnessed;
} CombatBirth;
typedef struct {
 uint64_t frame,birth_serial,generation,bank_stamp;uintptr_t bank_data;
 unsigned kind,slot,index,style,ttl,record,phase,role,bank_bytes,callbacks,core_stores,extra_stores;
 int x,y;bool complete;
} CombatDraw;
typedef struct {
 bool requested,loaded,active,contributed,failed,accepted;unsigned first_reason,draw_count,material_mask;
 uint64_t frame,births[3],normal_retirements,blend_retirements,shadow_cells,extra_retirements,clipped,unwitnessed;
 unsigned native_cells,extra_pixels;CombatDraw last;
} CombatFamilyStatus;
/* All getters are read-only. Frame draws remain available until the next begin.
 * No returned rectangle or receipt grants rendering authority. */
CombatFamilyStatus render_mirror_combat_family_status(void);
unsigned render_mirror_combat_draws(CombatDraw *,size_t);
bool render_mirror_combat_birth(unsigned,unsigned,CombatBirth *);
bool render_mirror_combat_pre_draw(CombatDraw *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_combat_callbacks(CombatWrite *,size_t);
bool render_mirror_combat_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
