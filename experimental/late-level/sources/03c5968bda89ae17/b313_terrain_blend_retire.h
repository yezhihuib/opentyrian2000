#ifndef B313_TERRAIN_BLEND_RETIRE_H
#define B313_TERRAIN_BLEND_RETIRE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Private read-only diagnostics, not a lease or observer permission. Counts
 * include completed callbacks in rejected frames; mask is historical perframe
 * retirement (later native writers may overwrite the cell). Source coordinates. */
typedef struct {
 bool requested,frame_enabled;
 uint64_t frame,frame_eligible,frame_retired,total_eligible,total_retired;
 unsigned first_reason; /* Per-frame first family fault, independent of lifetime fc.first_reason. */
 int first_x,first_y;
} B313TerrainBlendRetireStatus;
#ifndef RENDER_MIRROR_DISABLED
B313TerrainBlendRetireStatus render_mirror_terrain_blend_retire_status(void);
bool render_mirror_terrain_blend_retire_mask(uint8_t *out,size_t bytes);
/* Before-callback terrain provenance probe. Does not consume a native writer. */
bool render_mirror_terrain_blend_cell(unsigned off);
/* Exact full 2560x1600 canvas copy and optional HD-owner copy. Caller-owned
 * storage only. May inspect a faulted frame for OFF-path comparison. */
bool render_mirror_terrain_blend_snapshot(uint32_t *pixels,size_t count,uint8_t *owners,size_t owner_bytes);
#else
static inline B313TerrainBlendRetireStatus render_mirror_terrain_blend_retire_status(void)
{const B313TerrainBlendRetireStatus s={0};return s;}
static inline bool render_mirror_terrain_blend_retire_mask(uint8_t *p,size_t n)
{(void)p;(void)n;return false;}
static inline bool render_mirror_terrain_blend_cell(unsigned o){(void)o;return false;}
static inline bool render_mirror_terrain_blend_snapshot(uint32_t *p,size_t n,uint8_t *o,size_t b)
{(void)p;(void)n;(void)o;(void)b;return false;}
#endif
#endif
