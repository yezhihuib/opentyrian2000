#ifndef TRIPLE275_FAMILY_H
#define TRIPLE275_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {
 bool requested,loaded,contributed,failed;
 uint64_t frame,blend_retirements;
 unsigned state_mask,surviving_cells;
 unsigned slot_mask[100],base[100],cycle[100];
 int x[100],y[100];
} Triple275FamilyStatus;
/* Diagnostic only. No draw, source admission or presentation permission.
 * Support is native 320x200 coordinates, valid after finish until next begin
 * or lifecycle invalidation. It may be read inside Present's wrapper. */
Triple275FamilyStatus render_mirror_triple275_family_status(void);
bool render_mirror_triple275_family_support(uint8_t *,size_t);
#endif
