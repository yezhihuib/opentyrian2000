/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SELECTOR_FONT_OUTPUT_H
#define SELECTOR_FONT_OUTPUT_H

#include "video_scale.h"

enum { SELECTOR_FONT_CANONICAL_W = 1280, SELECTOR_FONT_CANONICAL_H = 800 };

/* The layer is an already ordered, transparent, premultiplied 0xAARRGGBB
 * 1280x800 image. Reduction integrates this layer, never the indexed scene.
 * Underlay is the original indexed scene with replaced glyphs removed and the
 * original cursor retained. Neither input is modified. support includes BOTH
 * authored coverage and removed original glyphs, in canonical coordinates.
 * cursor_mask is NULL or a tightly packed 320x200 original cursor write mask.
 * scaler_radius is the input dependency radius: nearest=0, Scale/HQ=1.
 * A conservative cursor neighbourhood uses the exact classic texture, so
 * filtered cursors remain opaque/last without a font-erasure halo.
 *
 * The arithmetic reference is this 8-bit premultiplied layer, with one final
 * rounded RGB integration. It does not promise legacy per-operation rounding.
 * CPU staging is one fixed tile. Cursor snapshot textures are reusable tiles
 * whose total size follows only the visible cursor/filter neighbourhood;
 * allocation failure declines enhancement, without a window-size whitelist.
 *
 * On false, the caller must execute its normal classic draw/present. The
 * reference texture is never changed. Call release BEFORE renderer teardown.
 */
bool selector_font_output_present(SDL_Renderer *renderer,
 SDL_Texture *reference_texture, SDL_Surface *indexed_underlay,
 ScalerFunction scale, const SDL_Rect *destination,
 const Uint32 *canonical_premul_argb, const SDL_Rect *support,
 const Uint8 *cursor_mask, unsigned scaler_radius);
void selector_font_output_release(void);
size_t selector_font_output_static_bytes(void);

#endif
