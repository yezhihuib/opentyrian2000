/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef PREGAME_FONT_H
#define PREGAME_FONT_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
enum PregameRun { PREGAME_HEADING, PREGAME_ROW, PREGAME_CASH, PREGAME_FOOTER, PREGAME_PRODUCT_NAME, PREGAME_PRODUCT_COST, PREGAME_POWER };
enum PregameGlyph { PREGAME_DARK, PREGAME_BLACK, PREGAME_FACE, PREGAME_UNSAFE, PREGAME_ORIGINAL };
enum PregamePhase { PREGAME_CUBES=10, PREGAME_BARS, PREGAME_SHIP };
size_t pregame_font_static_bytes(void);
/* Owner state, active payloads, all shared run caches and output CPU staging;
 * excludes unrelated owners and renderer-owned texture allocations. */
size_t pregame_font_retained_bytes(void);
bool pregame_font_owns_display(void);
void pregame_font_set_directory(const char *);
void pregame_font_begin(unsigned menu, unsigned selected, unsigned last, bool ordinary, unsigned long cash, unsigned cubes, SDL_Surface *, SDL_Surface *);
void pregame_font_product_begin(unsigned category, unsigned selected, unsigned last, bool ordinary, SDL_Surface *, SDL_Surface *);
void pregame_font_product_update_begin(void);
void pregame_font_product_update_end(void);
void pregame_font_end(void);
void pregame_font_release_texture(void);
void pregame_font_invalidate(void);
void pregame_font_table_reset(unsigned);
void pregame_font_run_begin(enum PregameRun, unsigned row, SDL_Surface *, int x, int y, const char *, unsigned font, unsigned hue, int value);
void pregame_font_run_end(void);
void pregame_font_phase_begin(enum PregamePhase, unsigned armor, unsigned shield);
void pregame_font_phase_end(void);
void pregame_font_glyph_begin(SDL_Surface *, int x, int y, unsigned font, unsigned id, enum PregameGlyph, unsigned hue, int value);
void pregame_font_glyph_end(void);
void pregame_font_sprite2_begin(SDL_Surface *, int x, int y, const void *, size_t, unsigned id);
void pregame_font_sprite2_end(void);
void pregame_font_frame_end(void);
void pregame_font_pixel(SDL_Surface *, Uint8 *, int style);
void pregame_font_rect(SDL_Surface *, const SDL_Rect *);
void pregame_font_cursor_begin(void);
void pregame_font_cursor_done(void);
void pregame_font_cursor_sprite_begin(SDL_Surface *, int x, int y, const void *, size_t, unsigned id);
void pregame_font_cursor_sprite_end(void);
void pregame_font_cursor_erased(void);
void pregame_font_fade_declare(int);
void pregame_font_fade_start(const SDL_Color *, const SDL_Color *, unsigned first, unsigned last);
void pregame_font_fade_step(int remaining, unsigned first, unsigned last);
bool pregame_font_present(SDL_Renderer *, SDL_Texture *, SDL_Surface *, const SDL_Rect *, bool foreign_owner);
#endif
