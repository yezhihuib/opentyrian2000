#ifndef B313_FAMILY_CORNER_H
#define B313_FAMILY_CORNER_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
enum { B313_FAMILY_CORNER_COUNT=1, B313_FAMILY_CORNER_SUPPORT_BYTES=64000 };
typedef struct {
 bool requested,enabled,cache_ready,frame_failed,pass_active,row_active,pass_done,support_ready;
 unsigned first_reason,id;
 uint64_t session,frame,map_epoch,cache_loads;
 uint64_t frames,target_tiles,target_pixels,rejected_frames;
 uint64_t frame_family_draws,frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
} B313FamilyCornerStatus;
/* Read-only accepted snapshot, 320x200 source coordinates. Surviving corner366
 * cells are 1; all others and cells outside x=24..287,y=0..183 are zero.
 * This API grants no draw/finish/present lease. */
#ifndef RENDER_MIRROR_DISABLED
B313FamilyCornerStatus render_mirror_family_corner_status(void);
bool render_mirror_family_corner_support(uint8_t *out,size_t bytes);
#else
static inline B313FamilyCornerStatus render_mirror_family_corner_status(void){const B313FamilyCornerStatus s={0};return s;}
static inline bool render_mirror_family_corner_support(uint8_t *out,size_t bytes){(void)out;(void)bytes;return false;}
#endif
#endif
