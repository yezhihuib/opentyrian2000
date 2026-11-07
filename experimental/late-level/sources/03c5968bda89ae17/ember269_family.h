#ifndef EMBER269_FAMILY_H
#define EMBER269_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {
 bool requested,loaded,contributed,failed;
 uint64_t frame,blend_retirements;
 unsigned state_mask,surviving_cells;
 unsigned slot_mask[100],base[100],cycle[100];
 int x[100],y[100];
} Ember269FamilyStatus;
/* Diagnostic only. No draw, source admission or presentation permission.
 * Support is native 320x200 coordinates, valid after finish until next begin
 * or lifecycle invalidation. It may be read inside Present's wrapper. */
Ember269FamilyStatus render_mirror_ember269_family_status(void);
bool render_mirror_ember269_family_support(uint8_t *,size_t);
#endif
