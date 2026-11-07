/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef FIXED_PICKUP_FLASH_H
#define FIXED_PICKUP_FLASH_H
#include <stdbool.h>
#include <stdint.h>

/* Display-only original type-0 collection flash; owns no clock or game state. */
bool fixed_pickup_flash_eligible(bool fixed, bool following, int delta_y,
                                 unsigned sprite, unsigned ttl);
/* One 12x14, 8x RGBA cache, using only the current warm 0x70 palette ramp. */
uint8_t *fixed_pickup_flash_rgba(const uint32_t palette[256]);
#endif
