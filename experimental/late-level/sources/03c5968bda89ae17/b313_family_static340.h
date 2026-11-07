#ifndef B313_FAMILY_STATIC340_H
#define B313_FAMILY_STATIC340_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
enum { B313_FAMILY_STATIC340_COUNT=1, B313_FAMILY_STATIC340_SUPPORT_BYTES=64000 };
typedef struct {
 bool requested,enabled,cache_ready,frame_failed,pass_active,row_active,pass_done,support_ready;
 unsigned first_reason,id;
 uint64_t session,frame,map_epoch,cache_loads;
 uint64_t frames,target_tiles,target_pixels,rejected_frames;
 uint64_t frame_family_draws,frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
} B313FamilyStatic340Status;
/* Read-only accepted snapshot, 320x200 source coordinates. Surviving static340
 * cells are 1; all others and cells outside x=24..287,y=0..183 are zero.
 * The accepted snapshot remains readable after Present, but not after a new
 * frame, reset, fault, epoch or configuration change. A successful all-zero
 * snapshot is not evidence of a contribution or a Present. Failed reads do
 * not change the caller buffer. This API grants no draw/finish/present lease. */
#ifndef RENDER_MIRROR_DISABLED
B313FamilyStatic340Status render_mirror_family_static340_status(void);
bool render_mirror_family_static340_support(uint8_t *out,size_t bytes);
#else
static inline B313FamilyStatic340Status render_mirror_family_static340_status(void){const B313FamilyStatic340Status s={0};return s;}
static inline bool render_mirror_family_static340_support(uint8_t *out,size_t bytes){(void)out;(void)bytes;return false;}
#endif
#endif
