/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef GAMEPLAY_HUD_STORM_H
#define GAMEPLAY_HUD_STORM_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Independent, finite observer. No game surface or retained RGB writes. */
typedef struct {
 const void *surface, *format;
 const uint8_t *pixels;
 int width, height, pitch, bits, bytes;
} HudStormView;
typedef struct {
 const uint8_t *data;
 unsigned size, width, height, count;
} HudStormSource;
void hud_storm_reset(void);
void hud_storm_shutdown(void);
bool hud_storm_start(const char *, const HudStormView *, const HudStormSource *);
void hud_storm_suspend(void);
void hud_storm_resume(const HudStormView *, bool scope);
void hud_storm_begin(const HudStormView *, const HudStormSource *, unsigned slot,
                     unsigned option, unsigned icon, int x, int y, bool scope);
void hud_storm_pixel(const HudStormView *, const uint8_t *address);
void hud_storm_rect(const HudStormView *, int x, int y, int w, int h);
void hud_storm_end(const HudStormView *, const HudStormSource *, unsigned slot, bool scope);
/* Called only after the existing renderer accepted and executed a fade step. */
void hud_storm_fade_palette(const uint32_t palette[256]);
/* Preflight finishes before the first write. Only the 25x5 label is written to
 * the locked texture. RGB underlay, original INDEX8, and fades remain untouched. */
bool hud_storm_present(const HudStormView *, const HudStormSource *, bool scope,
 const uint32_t palette[256], const uint8_t *rgb, int rgb_pitch,
 uint8_t *texture, int texture_pitch, int width, int height, int density);
#endif
