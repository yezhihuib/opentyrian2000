#ifndef B313_ENTRY_CLIP_H
#define B313_ENTRY_CLIP_H
#include "b313_family_plan.h"
#include <stdbool.h>
#include <stdint.h>
/* Read-only diagnostics. Counts describe native-completed calls, not final
 * presentation permission. HD stores are independently observable through
 * the unchanged OHS_SURVIVAL_WRITE tag13 in draw_asset_filtered. */
typedef struct {
 uint64_t frame,last_nonce;
 bool frame_enabled,last_complete;
 unsigned last_slot,last_part,last_callbacks;
 B313FamilyPlan last_plan;
 uint64_t frame_empty_calls,frame_partial_calls,frame_visible_calls;
 uint64_t total_empty_calls,total_partial_calls,total_visible_calls;
} B313EntryClipStatus;
B313EntryClipStatus render_mirror_entry_clip_status(void);
#endif
