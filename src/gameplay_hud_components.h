/* Optional, immutable single-player PIC3 word and shield artwork.
 * This finite component loader has no SDL or original-game-data dependency. */
#ifndef GAMEPLAY_HUD_COMPONENTS_H
#define GAMEPLAY_HUD_COMPONENTS_H

#include <stdbool.h>
#include <stdint.h>

/* One selected-directory gameplay-hud-components-v1.hda attempt per shutdown,
 * including missing/NULL/invalid paths. Success means a valid HUC1 asset, not
 * that PIC3 was captured. One fixed 38528-byte allocation; no later I/O. */
bool hud_components_load(const char *directory);
/* Requires 200 readable rows of at least 320 indexed pixels. Hashes all 64000
 * pixels, excludes padding, and requires every pristine shield-window index
 * in [270,137,279,195) to be zero. Retains only the 350 label indices.
 * Every capture attempt revokes the previous capture and shield draw stamp. */
bool hud_components_capture(const uint8_t *indices, int pitch);
void hud_components_forget_source(void);
void hud_components_shutdown(void);
bool hud_components_ready(void);
/* Hashes 256 sequential R,G,B triples from 0x??RRGGBB entries, ignoring the high
 * byte. Caller must gate both component families on this normal palette. */
bool hud_components_palette_matches(const uint32_t packed_rgb[256]);

/* Word boxes (half-open logical coordinates): FRONT [285,5,309,10), front GUN
 * [285,11,299,16), REAR [285,26,303,31), rear GUN [285,32,299,37).
 * These are the only static coordinates owned here; captured index zero is
 * permitted inside these boxes. The independent static HUD is not relaxed.
 * sx/sy are in [0,density); density 4 is authored, density 8 repeats each sample
 * 2x. NULL means classic fallback. Returned opaque RGBA lives until shutdown. */
const uint8_t *hud_components_label_sample(int x, int y, int sx, int sy,
                                          int density, uint8_t current_index);

/* Stamp only a fresh original shield draw with 0 <= shield <= maximum <= 28.
 * Invalid draws and wipes revoke only the shield stamp; labels stay ready.
 * A wipe never manufactures the two-row zero-shield baseline. */
void hud_components_shield_drawn(int shield, int maximum);
void hud_components_shield_wiped(void);
bool hud_components_shield_ready(void);
/* Check all 522 original-index pixels, including black and the capacity marker,
 * against the last fresh valid draw. Does not mutate its stamp. Requires the
 * same 320x200 readable-row contract as capture; no allocation or I/O. */
bool hud_components_shield_matches(const uint8_t *indices, int pitch);
/* Owns only stamped fill indices 146..159 inside [270,137,279,195), never black
 * or capacity-marker index 68. Fourteen opaque 36x8 RGBA tiles represent 9x2
 * logical row pairs. First tile row maps to odd source rows (137,139,...,193).
 * Requires matching current index and the same subpixel rules as labels.
 * Caller must also gate on shield_matches, palette_matches, compatible gameplay
 * mode and source lifetime. An equal index alone cannot detect a stale redraw. */
const uint8_t *hud_components_shield_sample(int x, int y, int sx, int sy,
                                           int density, uint8_t current_index);

#endif
