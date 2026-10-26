/* SPDX-License-Identifier: GPL-2.0-or-later
 * Linked NEWSHF immutable identity extension. No source pixels or records.
 * Same verified bank/table/palette as newshf_prototype_pins.h. */
#ifndef NEWSHF_LINKED_PINS_H
#define NEWSHF_LINKED_PINS_H
static const unsigned newshf_linked_record_ids[3]={171u,172u,173u};
static const uint64_t newshf_linked_record_fnv[3]={UINT64_C(0x656a7f4ab4ebc44f),UINT64_C(0xbdae56ed74b89f8f),UINT64_C(0x94b060cc94be0f87)};
static const struct {unsigned index; uint64_t fnv;} newshf_linked_tiles[]={
 {43u,UINT64_C(0x7d37741a00010321)},
 {44u,UINT64_C(0x4c4910fa18d0cb26)},
 {45u,UINT64_C(0x7d37741a00010321)},
 {46u,UINT64_C(0x4c4910fa18d0cb26)},
 {62u,UINT64_C(0x87ff99d82e52751b)},
 {63u,UINT64_C(0xec92ac7013587fa8)},
 {64u,UINT64_C(0x87ff99d82e52751b)},
 {65u,UINT64_C(0xec92ac7013587fa8)},
 {81u,UINT64_C(0x7b1a35995a273932)},
 {82u,UINT64_C(0x904bab8fb0044907)},
 {83u,UINT64_C(0x7b1a35995a273932)},
 {84u,UINT64_C(0x904bab8fb0044907)},
 {100u,UINT64_C(0xbca1c3cd9136af94)},
 {101u,UINT64_C(0x4d46fb6f5030a9ae)},
 {102u,UINT64_C(0x4fdc76e888f9fdd4)},
 {103u,UINT64_C(0x4a2662210c7b98ce)},
 {119u,UINT64_C(0xd0959544861c9c98)},
 {120u,UINT64_C(0xe1bee86437a6b088)},
 {121u,UINT64_C(0x3bf22419293300ac)},
 {122u,UINT64_C(0xa875e8de7c1836cb)},
 {138u,UINT64_C(0x51795983e22e1d65)},
 {139u,UINT64_C(0x51795983e22e1d65)},
 {140u,UINT64_C(0x51795983e22e1d65)},
 {141u,UINT64_C(0x51795983e22e1d65)},
};
#endif
