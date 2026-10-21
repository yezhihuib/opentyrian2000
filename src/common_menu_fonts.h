/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reconstructed 2026-10-20. Read-only source/atlas views, not a replacement
 * for the native font API. Every caller must witness complete native runs. */
#ifndef COMMON_MENU_FONTS_H
#define COMMON_MENU_FONTS_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>

typedef struct CommonMenuGlyph {
 unsigned width, height, advance;
 const Uint8 *source; /* width*height low nibbles; 255 means transparent. */
 const Uint8 *alpha, *roles; /* Optional 4x atlas tile, with atlas_pitch. */
 unsigned atlas_pitch;
} CommonMenuGlyph;
/* Banks 0/1/2 are original large/medium/tiny. Source banks and resource banks
 * are independent bitmasks; tiny has no optional atlas here. A failed bank
 * never invalidates a sibling. Paths are copied and remain caller-owned. */
bool common_menu_fonts_acquire(const char *directory, unsigned source_banks, unsigned resource_banks);
bool common_menu_fonts_validate(unsigned source_banks);
bool common_menu_fonts_glyph(unsigned bank, unsigned id, CommonMenuGlyph *out);
void common_menu_fonts_table_reset(unsigned bank);
void common_menu_fonts_shutdown(void);
size_t common_menu_fonts_retained_bytes(void);
#endif
