/* SPDX-License-Identifier: GPL-2.0-or-later
 * Shared dual-missile identity: hashes only, no original game records/pixels.
 * Bank/table/palette remain pinned by newshf_prototype_pins.h. */
#ifndef NEWSHF_DUALMISSILE_PINS_H
#define NEWSHF_DUALMISSILE_PINS_H
static const unsigned newshf_dualmissile_record_ids[2]={2u,500u};
static const uint64_t newshf_dualmissile_record_fnv[2]={UINT64_C(0x4f7817e45c41f01c),UINT64_C(0xd0d960ce10401c6d)};
static const struct {unsigned index; uint64_t fnv;} newshf_dualmissile_tiles[]={
 {169u,UINT64_C(0x1dddfa45396db314)},
 {170u,UINT64_C(0x1dddfa45396db314)},
 {188u,UINT64_C(0x01c808c02c652944)},
 {189u,UINT64_C(0x01c808c02c652944)},
};
#endif
