/* Optional finite HUF1 coverage atlas. Original font bytes remain game-owned. */
#ifndef GAMEPLAY_HUD_FONT_H
#define GAMEPLAY_HUD_FONT_H

#include <stdbool.h>
#include <stdint.h>

typedef struct HudFontGlyph {
	uint16_t width, height, size;
	const uint8_t *data;
} HudFontGlyph;

/* One regular-file attempt and one fixed 163840-byte allocation per shutdown. */
bool hud_font_load(const char *directory);
/* Requires 200 readable rows of 320 indices and 127 readable glyph records.
 * The source is checked before normal palette installation. Only dimensions
 * are retained; no original indices, encoded bytes, or source pointers are. */
bool hud_font_capture(const uint8_t *indices, int pitch, const int map[256],
                      const HudFontGlyph glyphs[127]);
bool hud_font_source_matches(const int map[256], const HudFontGlyph glyphs[127]);
bool hud_font_palette_matches(const uint32_t packed_rgb[256]);
bool hud_font_ready(void);
void hud_font_forget_source(void);
void hud_font_shutdown(void);
/* Captured dimensions for eligible IDs 0..85; otherwise zero. */
int hud_font_width(unsigned id);
int hud_font_height(unsigned id);
/* Glyph-local subpixel coordinates. IDs 0..85 only; 8x repeats 4x exactly.
 * Unsupported inputs and all samples outside the original glyph return zero. */
uint8_t hud_font_alpha(unsigned id, int xsub, int ysub, int density);

#endif
