#ifndef B313_OFFCROP_BLEND_H
#define B313_OFFCROP_BLEND_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Diagnostics only. This is never an ownership or presentation lease. */
typedef struct {
 bool requested,frame_enabled,last_complete;
 uint64_t frame,frame_cells,total_cells;
 uint64_t frame_subpixel_writes,total_subpixel_writes;
 uint64_t frame_crop_writes,total_crop_writes;
 int first_x,first_y,last_x,last_y;
 unsigned last_written,last_crop_writes,last_store_min,last_store_max;
 uint8_t last_native_index;
 uint32_t last_native_rgb;
} OffcropBlendStatus;
OffcropBlendStatus render_mirror_offcrop_blend_status(void);
/* Exactly 64 current-cell samples, source coordinates in status.last_x/y.
 * Pure readback, including after a later unrelated frame failure. */
bool render_mirror_offcrop_blend_last(uint32_t *before,uint32_t *after,
 uint8_t *owner_before,uint8_t *owner_after,size_t count);
#endif
