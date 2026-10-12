/* Optional, immutable PIC3 top lens and complete paired MODE assembly.
 * This bounded loader has no SDL or original-game-data dependency. */
#ifndef GAMEPLAY_HUD_INDICATORS_H
#define GAMEPLAY_HUD_INDICATORS_H

#include <stdbool.h>
#include <stdint.h>

/* One selected-directory gameplay-hud-indicators-v1.hda attempt per shutdown,
 * including NULL/missing/invalid paths. A valid HUL1 uses one fixed 28992-byte
 * allocation. Source guards are pinned independently of HUD1 and HUC1. */
bool hud_indicators_load(const char *directory);
/* Requires 200 readable rows of at least 320 indices. Hashes the complete
 * 64000-byte PIC3, excluding padding. The two decoded row-major 10x8 arrays
 * are OPTION18 then OPTION19; each opacity byte must equal 255. Caller checks
 * sprite dimensions and decoding bounds. Capture verifies their fixed hashes
 * and constructs both complete 216-byte assembly expectations, retaining only
 * those and the 21 top-lens indices. Every attempt revokes prior capture/stamp. */
bool hud_indicators_capture(const uint8_t *indices, int pitch,
                            const uint8_t mode_indices[2][80],
                            const uint8_t mode_opaque[2][80]);
/* Read-only current sprite-table guard. Requires a loaded asset, independently
 * of capture. This grants no draw stamp and performs no allocation or I/O. */
bool hud_indicators_verify_modes(const uint8_t mode_indices[2][80],
                                 const uint8_t mode_opaque[2][80]);
void hud_indicators_forget_source(void);
void hud_indicators_shutdown(void);
bool hud_indicators_ready(void);
/* Hashes 256 sequential RGB triples from 0x??RRGGBB, ignoring the high byte. */
bool hud_indicators_palette_matches(const uint32_t packed_rgb[256]);

/* Stamp only an actual completed original mode-1 or mode-2 paired-sprite draw.
 * Mode 1 uses (18,19), mode 2 uses (19,18). Invalid modes and wipes revoke only
 * the mode stamp. Equal pixels alone never manufacture a fresh draw event. */
void hud_indicators_mode_drawn(int mode);
void hud_indicators_mode_wiped(void);
bool hud_indicators_mode_ready(void);
/* Whole-rectangle indexed equality, including black, sprite rims and center.
 * Same readable-row contract as capture. Neither check changes the stamp. */
bool hud_indicators_mode_matches(const uint8_t *indices, int pitch);
bool hud_indicators_top_matches(const uint8_t *indices, int pitch);

/* Owns only top [269,4,276,7) and mode [285,44,312,52), half-open. Top requires
 * capture; mode additionally requires its actual draw stamp. Caller must gate
 * each rectangle on its whole-rectangle match, current sprite-table/palette
 * guards, source lifetime, compatible gameplay mode and modal/fade ownership.
 * Captured black is allowed only inside these fixed rectangles. density 4 is
 * authored; density 8 repeats each texel 2x. sx/sy must be within density.
 * NULL requests classic fallback. Opaque RGBA pointers live until shutdown.
 * This lookup never mutates state, allocates, or performs I/O. */
const uint8_t *hud_indicators_sample(int x, int y, int sx, int sy,
                                    int density, uint8_t current_index);

#endif
