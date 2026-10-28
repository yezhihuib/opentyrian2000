/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite record170 bank10 identity. Hashes only; no original records/pixels.
 * Only exact E1-E3 HDT identity; alternate E4/E5 tur[1] identity stays classic. */
#ifndef NEWSHF_AIRCRAFT170_PINS_H
#define NEWSHF_AIRCRAFT170_PINS_H
static const uint64_t newshf_aircraft170_record_fnv=UINT64_C(0xf8c8b976f22146de);
static const struct {unsigned index;uint64_t fnv;} newshf_aircraft170_tiles[]={
 {15u,UINT64_C(0xb091c025b02f0497)},
 {16u,UINT64_C(0xe5efb6dacd0c3c91)},
 {34u,UINT64_C(0x39890b8a151e8022)},
 {35u,UINT64_C(0x4d26db726a3816fb)},
 {53u,UINT64_C(0x7fece8c128575f88)},
 {54u,UINT64_C(0x594b2eeacc42d348)},
 {72u,UINT64_C(0x255db6e44b6634c7)},
 {73u,UINT64_C(0xaf50fbd766cc4112)},
 {91u,UINT64_C(0xcc98286d1d020108)},
 {92u,UINT64_C(0x852d9d2e1dd3c88d)},
 {110u,UINT64_C(0x816073d0d88e64af)},
 {111u,UINT64_C(0x4cf9c271b24e80d1)},
};
#endif
