/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef LOAD_FONT_H
#define LOAD_FONT_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
enum LoadRun { LOAD_HEADING, LOAD_NAME, LOAD_LEVEL, LOAD_EPISODE, LOAD_EXIT, LOAD_FOOTER };
enum LoadGlyph { LOAD_DARK, LOAD_BLACK, LOAD_FACE, LOAD_UNSAFE };
void load_font_set_directory(const char *directory);
void load_font_begin(SDL_Surface *screen, SDL_Surface *backup);
void load_font_end(void);
void load_font_release_texture(void);
void load_font_invalidate(void);
void load_font_table_reset(unsigned table);
bool load_font_owns_display(void);
size_t load_font_static_bytes(void);
void load_font_frame_begin(unsigned page, size_t selected);
void load_font_run_begin(enum LoadRun role, unsigned row, SDL_Surface *, int x, int y, const char *, unsigned font, int alignment, unsigned hue, int value);
void load_font_run_end(void);
void load_font_glyph_begin(SDL_Surface *, int x, int y, unsigned font, unsigned id, enum LoadGlyph op, unsigned hue, int value);
void load_font_glyph_end(void);
void load_font_arrow_begin(void);
void load_font_arrow_sprite_begin(SDL_Surface *, int x, int y, const void *data, size_t size, unsigned id);
void load_font_arrow_sprite_end(void);
void load_font_arrow_end(void);
void load_font_help_begin(SDL_Surface *, int x, int y, const char *, unsigned width);
void load_font_help_line_begin(SDL_Surface *, int x, int y, const char *, unsigned hue, int value, unsigned shade_type);
void load_font_help_line_end(void);
void load_font_help_end(void);
void load_font_frame_end(void);
void load_font_pixel(SDL_Surface *, Uint8 *address, int style);
void load_font_rect(SDL_Surface *, const SDL_Rect *);
void load_font_cursor_begin(void);
void load_font_cursor_done(void);
void load_font_cursor_sprite_begin(SDL_Surface *, int x, int y, const void *data, size_t size, unsigned id);
void load_font_cursor_sprite_end(void);
void load_font_cursor_erased(void);
void load_font_fade_declare(int steps);
void load_font_fade_start(const SDL_Color *, const SDL_Color *, unsigned first, unsigned last);
void load_font_fade_step(int remaining, unsigned first, unsigned last);
bool load_font_present(SDL_Renderer *, SDL_Texture *, SDL_Surface *, const SDL_Rect *, bool foreign_owner);
#endif
