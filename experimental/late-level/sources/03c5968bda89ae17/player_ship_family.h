#ifndef PLAYER_SHIP_FAMILY_H
#define PLAYER_SHIP_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
enum { PLAYER_SHIP_HD_STORE_TAG = 30 }; /* Existing Talon blend-store tag. */
typedef struct {uint8_t x,y,index;} PlayerShipWrite;
typedef struct {
 uint64_t frame,session,generation;
 uintptr_t bank_data;
 unsigned bank_bytes,ship_record,index,callback_count,part_mask;
 unsigned invulnerable_ticks; /* Original pose value, before mainint decrement. */
 int x,y,style;
 bool pose_seen,contributed,complete,accepted,failed;
} PlayerShipDraw;
typedef struct {
 bool requested,loaded;
 unsigned surviving_cells,shadowed_cells,first_reason;
 uint64_t normal_retirements,blend_retirements,shadow_writes;
 PlayerShipDraw draw;
} PlayerShipFamilyStatus;
/* Read-only receipts. None grants admission. Pre-draw: immediately after the
 * original ship semantic call returns1, before its native QUAD starts. */
PlayerShipFamilyStatus render_mirror_player_ship_family_status(void);
bool render_mirror_player_ship_pre_draw(PlayerShipDraw *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_player_ship_callbacks(PlayerShipWrite *,size_t);
bool render_mirror_player_ship_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
