/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SELECTOR_FONT_H
#define SELECTOR_FONT_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
enum SelectorContext { SELECTOR_GAMEPLAY, SELECTOR_EPISODE, SELECTOR_DIFFICULTY, SELECTOR_TIMED };
enum SelectorRun { SELECTOR_HEADING, SELECTOR_ROW };
enum SelectorGlyph { SELECTOR_DARK, SELECTOR_BLACK, SELECTOR_FACE, SELECTOR_UNSAFE };
void selector_font_set_directory(const char *);
void selector_font_begin(enum SelectorContext, SDL_Surface *screen, SDL_Surface *backup);
void selector_font_end(void);
void selector_font_release_texture(void);
void selector_font_invalidate(void);
void selector_font_table_reset(unsigned);
bool selector_font_owns_display(void);
size_t selector_font_static_bytes(void);
void selector_font_frame_begin(size_t selected, size_t visible);
void selector_font_run_begin(enum SelectorRun, unsigned row, SDL_Surface *, int x, int y, const char *, unsigned font, int alignment, unsigned hue, int value);
void selector_font_run_end(void);
void selector_font_glyph_begin(SDL_Surface *, int x, int y, unsigned font, unsigned id, enum SelectorGlyph, unsigned hue, int value);
void selector_font_glyph_end(void);
void selector_font_frame_end(void);
void selector_font_pixel(SDL_Surface *, Uint8 *address, int style);
void selector_font_rect(SDL_Surface *, const SDL_Rect *);
void selector_font_cursor_begin(void);
void selector_font_cursor_done(void);
void selector_font_cursor_sprite_begin(SDL_Surface *, int x, int y, const void *data, size_t size, unsigned id);
void selector_font_cursor_sprite_end(void);
void selector_font_cursor_erased(void);
void selector_font_fade_declare(int steps);
void selector_font_fade_start(const SDL_Color *, const SDL_Color *, unsigned first, unsigned last);
void selector_font_fade_step(int remaining, unsigned first, unsigned last);
bool selector_font_present(SDL_Renderer *, SDL_Texture *, SDL_Surface *, const SDL_Rect *, bool foreign_owner);
#endif
