/* Optional, immutable gameplay HUD artwork. No SDL or game-data dependency. */
#ifndef GAMEPLAY_HUD_H
#define GAMEPLAY_HUD_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Try exactly once per shutdown/reset, including NULL or missing directories.
 * True means the selected pack's asset is valid, not that source was captured. */
bool gameplay_hud_load(const char *directory);
/* Capture a canonical 320x200 source image, excluding row padding from its hash.
 * Expanded masks also require the exact zero-index SHIELD/ARMOR glyph moats.
 * Source-zero ownership is forbidden except for the exact pinned corner mask
 * and its independently pinned PIC3/336-cell source identities.
 * A failed capture always invalidates the previous capture. */
bool gameplay_hud_capture(const uint8_t *indices, int pitch);
/* True iff the loaded mask owns an exact approved expansion coordinate. */
bool gameplay_hud_has_expansion(void);
/* Bind both 10x8 mode source states to every actually owned mode-rim pixel and
 * captured PIC3. All owned points require opaque=255 and identical raw indices.
 * The caller must use one shared palette, giving identical RGBA as well.
 * Base-only masks need no capture or arrays. Expanded masks require capture;
 * arrays may be NULL only if no mode-rim pixels are owned. No allocation or I/O. */
bool gameplay_hud_verify_modes(const uint8_t indices[2][80],
                               const uint8_t opaque[2][80]);
/* Call immediately before each ordinary composition's samples. Only the exact
 * approved corner-union mask may replace source zero in [248,184,269,200).
 * All 336 current indices must match captured PIC3, or that entire rectangle
 * falls back. Returns false for legacy masks (whose sampling is unchanged).
 * Caller must already verify the persistent source-surface lease. No I/O or
 * allocation. Capture/forget/shutdown invalidate the corner preparation. */
bool gameplay_hud_prepare_corner(const uint8_t *indices, int pitch);
/* sx/sy are subpixel offsets in [0,density). Only density 4 or 8 is supported.
 * Returned RGBA remains owned by this module until shutdown. NULL means classic
 * fallback. The caller must gate this single-player PIC3 asset's gameplay mode
 * and prepare the conditional corner before each ordinary composition. */
const uint8_t *gameplay_hud_sample(int x, int y, int sx, int sy, int density,
                                 uint8_t current_index);
bool gameplay_hud_ready(void);
void gameplay_hud_forget_source(void);
void gameplay_hud_shutdown(void);
/* Standard FNV-1a 64-bit; corruption detection, not authentication. */
uint64_t gameplay_hud_fnv64(const uint8_t *bytes, size_t count);

#endif
