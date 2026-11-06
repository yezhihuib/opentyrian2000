#ifndef B313_FAMILY_GROUND_H
#define B313_FAMILY_GROUND_H
#include <stdbool.h>
#include <stdint.h>
typedef struct {
 bool requested,enabled,cache_ready,frame_failed,pass_active,row_active,pass_done;
 unsigned first_reason;
 uint64_t session,frame,map_epoch,cache_loads;
 uint64_t frames,passes,rows,target_tiles,target_pixels,native_callbacks,rejected_frames;
 uint64_t frame_family_draws,frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
} B313FamilyGroundStatus;
#ifndef RENDER_MIRROR_DISABLED
B313FamilyGroundStatus render_mirror_family_ground_status(void);
#else
static inline B313FamilyGroundStatus render_mirror_family_ground_status(void){const B313FamilyGroundStatus s={0};return s;}
#endif
#endif
