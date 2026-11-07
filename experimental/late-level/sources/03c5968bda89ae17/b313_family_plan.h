#ifndef B313_FAMILY_PLAN_H
#define B313_FAMILY_PLAN_H
#include "building313_identity.h"
/* Metadata-only, pure per-original-call adapter. No assets, pixels, leases,
 * cache pointers, global state, IO, tick table, or runtime admission. */
enum B313FamilyPlanReason {B313FP_INPUT=1u,B313FP_IDENTITY=2u,B313FP_PHASE=4u,B313FP_PART=8u,B313FP_GEOMETRY=16u,B313FP_MODE=32u};
typedef struct {
 B313Snapshot actor; /* Caller assertions only: a future live adapter must
  * compare egr[20], record egraphic[20], source identity and SDL context.
  * This kernel only checks the supplied current base/cycle mapping. */
 unsigned part,density;
 bool entry_clip; /* Default false: only bounded negative-y entry may differ. */
 int x,y,surface_width,surface_height,surface_pitch;
} B313FamilyCall;
typedef struct {
 bool planned,write_allowed,runtime_eligible;
 unsigned reasons,component,phase,cycle,part;
 /* Original 24x28 actor asset and the 12x14 original quadrant within it. */
 int actor_x,actor_y,part_x,part_y;
 /* 24x28 component extraction origin within the canonical48x56 phase pack. */
 int atlas_component_x,atlas_component_y;
 /* Source crop in native/8x coordinates; destination is original native x/y. */
 int atlas_tile_x,atlas_tile_y,source_x_hd,source_y_hd;
 int destination_x,destination_y,destination_x_hd,destination_y_hd;
 unsigned width,height,width_hd,height_hd;
 /* Separate native support; never change full tile/source metadata. */
 unsigned source_row0,visible_rows,expected_callbacks;
 int support_y;
} B313FamilyPlan;
bool b313_family_plan(const B313FamilyCall *call,B313FamilyPlan *out);
#endif
