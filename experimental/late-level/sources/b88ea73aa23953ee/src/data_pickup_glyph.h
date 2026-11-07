/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef DATA_PICKUP_GLYPH_H
#define DATA_PICKUP_GLYPH_H
#include <stdbool.h>
#include <stdint.h>

/* Display-only fixed DATA effect. No state or clock is owned here. */
bool data_pickup_glyph_eligible(bool fixed, bool following, int delta_y,
                              unsigned sprite, unsigned ttl);
/* One bounded 12x14, 8x RGBA cache, recolored only when its palette changes. */
uint8_t *data_pickup_glyph_rgba(const uint32_t palette[256]);
#endif
