#ifndef B313_BUILDING_BLEND_RETIRE_H
#define B313_BUILDING_BLEND_RETIRE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Pure diagnostic copies. Neither ownership nor a completed native-cell
 * retirement is a frame admission or a presentation grant. */
typedef struct {
 uint64_t frame,frame_claimed,frame_eligible,frame_retired;
 uint64_t total_claimed,total_eligible,total_retired;
 bool requested,frame_enabled,last_complete,last_ownership_cleared;
 unsigned current_reason,last_before_slot_plus1,last_native_index;
 unsigned last_subpixel_writes,last_store_min,last_store_max;
 int last_x,last_y;
 uint32_t last_native_rgb;
} B313BuildingBlendRetireStatus;
B313BuildingBlendRetireStatus render_mirror_building_blend_retire_status(void);
bool render_mirror_building_blend_retire_mask(uint8_t *,size_t);
bool render_mirror_building_blend_owner(uint8_t *,size_t);
/* Row-major 8x8 cell; owner bits: HD=1, cloud=2, green_first=4,
 * green_under_owner=8. Available after a frame fault if storage is intact. */
bool render_mirror_building_blend_cell_snapshot(unsigned,uint32_t *,uint8_t *,size_t);
#endif
