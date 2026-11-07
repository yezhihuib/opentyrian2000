/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SETTINGS_FONT_H
#define SETTINGS_FONT_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
enum SettingsRun { SETTINGS_HEADING, SETTINGS_LABEL, SETTINGS_VALUE, SETTINGS_FOOTER, SETTINGS_PICKER };
enum SettingsGlyph { SETTINGS_DARK, SETTINGS_BLACK, SETTINGS_FACE, SETTINGS_UNSAFE };
size_t settings_font_static_bytes(void);
bool settings_font_owns_display(void);
void settings_font_set_directory(const char *directory);
void settings_font_begin(SDL_Surface *screen, SDL_Surface *backup);
void settings_font_end(void);
void settings_font_release_texture(void);
void settings_font_invalidate(void);
void settings_font_table_reset(unsigned table);
void settings_font_frame_begin(unsigned menu, size_t selected, unsigned picker);
void settings_font_run_begin(enum SettingsRun role, unsigned row, SDL_Surface *, int x, int y, const char *, unsigned font, int alignment, unsigned hue, int value);
void settings_font_run_end(void);
void settings_font_glyph_begin(SDL_Surface *, int x, int y, unsigned font, unsigned id, enum SettingsGlyph op, unsigned hue, int value);
void settings_font_glyph_end(void);
void settings_font_bar_begin(unsigned row, unsigned color, unsigned amount);
void settings_font_picker_begin(size_t count, size_t selected, int y);
void settings_font_primitive_end(void);
void settings_font_frame_end(void);
void settings_font_pixel(SDL_Surface *, Uint8 *address, int style);
void settings_font_rect(SDL_Surface *, const SDL_Rect *);
void settings_font_cursor_begin(void);
void settings_font_cursor_done(void);
void settings_font_cursor_sprite_begin(SDL_Surface *, int x, int y, const void *data, size_t size, unsigned id);
void settings_font_cursor_sprite_end(void);
void settings_font_cursor_erased(void);
void settings_font_fade_start(const SDL_Color *, const SDL_Color *, unsigned first, unsigned last);
void settings_font_fade_step(int remaining, unsigned first, unsigned last);
bool settings_font_present(SDL_Renderer *, SDL_Texture *, SDL_Surface *, const SDL_Rect *, bool foreign_owner);
#endif
