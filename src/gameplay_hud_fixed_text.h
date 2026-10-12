/* Finite, optional PIC3 MODE/SHIELD/ARMOR labels, independent of scene fonts. */
#ifndef GAMEPLAY_HUD_FIXED_TEXT_H
#define GAMEPLAY_HUD_FIXED_TEXT_H
#include <stdbool.h>
#include <stdint.h>
/* One regular-file attempt and fixed23680-byte allocation per shutdown. */
bool hud_fixed_text_load(const char *directory);
/* Requires200readable rows of320indices. Capture validates pristinePIC3 and
 * retains370indices only. It intentionally does not require the current palette:
 * the explicit gameplayPIC3 grant occurs before normal palette installation. */
bool hud_fixed_text_capture(const uint8_t *indices,int pitch);
void hud_fixed_text_forget_source(void);
void hud_fixed_text_shutdown(void);
bool hud_fixed_text_ready(void);
bool hud_fixed_text_palette_matches(const uint32_t packed_rgb[256]);
/* Three coherent groups: MODE95, verticalSHIELD150, verticalARMOR125. Caller
 * must validate group, normal palette, source lease and gameplay lifecycle. */
bool hud_fixed_text_group_matches(unsigned group,const uint8_t *indices,int pitch);
/* Pure finite geometry remains usable before assetload. Cells0..369 use tile
 * order. No dynamic fields or inter-letter gap rows are included. */
bool hud_fixed_text_position(unsigned cell,int *x,int *y);
int hud_fixed_text_cell(int x,int y);
/* AllopaqueRGBA,4xnative/8xexactrepeat. No I/O/allocation. */
const uint8_t *hud_fixed_text_sample(unsigned cell,int sx,int sy,int density);
#endif
