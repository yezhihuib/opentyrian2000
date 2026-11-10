#ifndef B313_TANK_FALLBACK_H
#define B313_TANK_FALLBACK_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct {
 bool seen,valid,active,complete,ready,presenting,denied,current;
 uint64_t epoch,token,generation,script_serial;
 unsigned slot,event,base,pose,callback_count,part_mask,reason,surviving_cells;
 int x,y;
} B313TankFallbackDrawStatus;
typedef struct {
 bool requested,active,presenting,phase_open;
 uint64_t frame,frames,draws,completed,prepared,presents,rejected,retired;
 unsigned first_reason;
 uint32_t presented_slots; /* Bits0..24 correspond to slots75..99. */
 B313TankFallbackDrawStatus draw[25];
} B313TankFallbackStatus;
B313TankFallbackStatus render_mirror_tank_fallback_status(void);
/* Only an actually independently presented slot can provide this receipt.
 * Relative24x28 logical mask and192x224 ARGB patch, anchored at draw.x/y.
 * Unowned samples convey no ownership or presentation authority. */
bool render_mirror_tank_fallback_sample(unsigned slot,uint8_t *owners,size_t owner_bytes,
 uint32_t *argb,size_t pixels);
#endif
