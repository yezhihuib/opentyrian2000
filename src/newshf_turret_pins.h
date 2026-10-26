/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared seven-slot turret identity: hashes only, no original records/pixels.
 * Bank/table/palette remain pinned by newshf_prototype_pins.h. */
#ifndef NEWSHF_TURRET_PINS_H
#define NEWSHF_TURRET_PINS_H
static const unsigned newshf_turret_record_ids[2]={162u,840u};
static const uint64_t newshf_turret_record_fnv[2]={UINT64_C(0x371ba15a128d3524),UINT64_C(0x50cc603227aa8844)};
static const struct {unsigned index; uint64_t fnv;} newshf_turret_tiles[]={
 {39u,UINT64_C(0x91c84416ab64ae87)},
 {40u,UINT64_C(0x0a769dd2b6955bf9)},
 {41u,UINT64_C(0x1ef063ac80eeb573)},
 {42u,UINT64_C(0x0a769dd2b6955bf9)},
 {58u,UINT64_C(0xa825e3f4f87b384e)},
 {59u,UINT64_C(0xd07a9e6ff4b73c3a)},
 {60u,UINT64_C(0xa825e3f4f87b384e)},
 {61u,UINT64_C(0xd07a9e6ff4b73c3a)},
};
#endif
