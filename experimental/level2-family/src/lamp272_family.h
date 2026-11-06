#ifndef LAMP272_FAMILY_H
#define LAMP272_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {
 bool requested,loaded,contributed,failed;
 uint64_t frame,blend_retirements;
 unsigned state_mask,surviving_cells;
 unsigned slot_mask[100],base[100],cycle[100];
 int x[100],y[100];
 /* Read-only registry/configuration witnesses. Bits 0..4 retain one-based
  * events 23,24,138,147,148; bits 5..6 name 50,51. origin_event is one-based,
  * zero when absent. The two extension flags are independent. */
 bool later_requested,later_level_enabled,later_frame_enabled;
 unsigned consumed_origins,origin_event[100];
 bool middle_requested,middle_level_enabled,middle_frame_enabled;
} Lamp272FamilyStatus;
/* Diagnostic only. No draw, source admission or presentation permission.
 * Support is native 320x200 coordinates, valid after finish until next begin
 * or lifecycle invalidation. It may be read inside Present's wrapper. */
Lamp272FamilyStatus render_mirror_lamp272_family_status(void);
bool render_mirror_lamp272_family_support(uint8_t *,size_t);
#endif
