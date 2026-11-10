#ifndef B313_TERRAIN_FALLBACK_H
#define B313_TERRAIN_FALLBACK_H
#include <stdbool.h>
#include <stdint.h>
typedef struct {
 bool requested,active,ready,presenting;
 uint64_t frames,captures,prepared,presents,rejected,retired;
 unsigned first_reason,surviving_cells;
} B313TerrainFallbackStatus;
B313TerrainFallbackStatus render_mirror_terrain_fallback_status(void);
#endif
