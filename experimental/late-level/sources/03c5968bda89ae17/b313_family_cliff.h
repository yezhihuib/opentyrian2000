#ifndef B313_FAMILY_CLIFF_H
#define B313_FAMILY_CLIFF_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
enum { B313_FAMILY_CLIFF_COUNT=12, B313_FAMILY_CLIFF_SUPPORT_BYTES=64000 };
typedef struct {
 bool requested,enabled,cache_ready,frame_failed,pass_active,row_active,pass_done,support_ready;
 unsigned first_reason;
 uint64_t session,frame,map_epoch,cache_loads;
 uint64_t frames,target_tiles,target_pixels,rejected_frames;
 uint64_t frame_family_draws,frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
 unsigned ids[B313_FAMILY_CLIFF_COUNT];
 uint64_t target_tiles_by_id[B313_FAMILY_CLIFF_COUNT],target_pixels_by_id[B313_FAMILY_CLIFF_COUNT];
 uint64_t frame_target_pixels_by_id[B313_FAMILY_CLIFF_COUNT],surviving_by_id[B313_FAMILY_CLIFF_COUNT];
} B313FamilyCliffStatus;
/* Diagnostic snapshot only: 320x200 source coordinates. Outside the ordinary
 * crop (x=24..287,y=0..183) is zero. Each surviving cell contains member+1,
 * indexed by status.ids. It never grants a draw, finish or present lease. */
#ifndef RENDER_MIRROR_DISABLED
B313FamilyCliffStatus render_mirror_family_cliff_status(void);
bool render_mirror_family_cliff_support(uint8_t *out,size_t bytes);
#else
static inline B313FamilyCliffStatus render_mirror_family_cliff_status(void){const B313FamilyCliffStatus s={0};return s;}
static inline bool render_mirror_family_cliff_support(uint8_t *out,size_t bytes){(void)out;(void)bytes;return false;}
#endif
#endif
