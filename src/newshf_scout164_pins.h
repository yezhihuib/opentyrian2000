/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite record164 bank10 identity. Hashes only; no original records/pixels.
 * Bank/table/palette remain pinned by newshf_prototype_pins.h. */
#ifndef NEWSHF_SCOUT164_PINS_H
#define NEWSHF_SCOUT164_PINS_H
static const uint64_t newshf_scout164_record_fnv=UINT64_C(0xae513132cadf4ce2);
static const struct {unsigned index;uint64_t fnv;} newshf_scout164_tiles[]={
 {9u,UINT64_C(0x4b386153520258b4)},
 {10u,UINT64_C(0xa3d1d86d427af25e)},
 {11u,UINT64_C(0x459d1b8b76e42781)},
 {12u,UINT64_C(0xa96f7de82114ee70)},
 {13u,UINT64_C(0x8c865146907698af)},
 {14u,UINT64_C(0x97b31bd7e5356ec8)},
 {28u,UINT64_C(0x7c342eaa7aa30cb0)},
 {29u,UINT64_C(0x91c630273552fffc)},
 {30u,UINT64_C(0x5802e06c6665d07b)},
 {31u,UINT64_C(0x043289b1851ab2ae)},
 {32u,UINT64_C(0xe76b81d5a9130bcc)},
 {33u,UINT64_C(0x39cc3bcb82389097)},
};
#endif
