#ifndef B313_PLAYER_FALLBACK_H
#define B313_PLAYER_FALLBACK_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct {
 bool requested,active,complete,ready,presenting;
 uint64_t frame,frames,poses,bodies,completed,prepared,presents,rejected,retired;
 unsigned index,callback_count,surviving_cells,reason,first_reason;
 int x,y;
} B313PlayerFallbackStatus;
B313PlayerFallbackStatus render_mirror_player_fallback_status(void);
/* Actual independent Present only. Relative 24x28 logical ownership and a
 * 192x224 ARGB patch, anchored at status.x/y. Unowned samples grant nothing. */
bool render_mirror_player_fallback_sample(uint8_t *owners,size_t owner_bytes,
 uint32_t *argb,size_t pixels);
#endif
