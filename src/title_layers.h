/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef TITLE_LAYERS_H
#define TITLE_LAYERS_H
#include "SDL.h"
#include <stdbool.h>

enum TitleWriter { TITLE_WRITE_LOGO, TITLE_WRITE_FONT, TITLE_WRITE_SHADOW, TITLE_WRITE_CURSOR };
enum TitleCheckpoint { TITLE_BACKGROUND, TITLE_MENU };
bool title_layers_owns_display(void);
void title_layers_set_directory(const char *directory);
void title_layers_begin(SDL_Surface *source, const SDL_Color *target, bool animate);
void title_layers_end(void);
void title_layers_sprite_table_reset(unsigned int table);
void title_layers_release_texture(void);
void title_layers_version_done(void);
void title_layers_save_before(enum TitleCheckpoint checkpoint);
void title_layers_save_after(enum TitleCheckpoint checkpoint);
void title_layers_restore_before(enum TitleCheckpoint checkpoint);
void title_layers_restore_after(enum TitleCheckpoint checkpoint);
void title_layers_logo(unsigned int id, int x, int y);
void title_layers_art_ready(void);
void title_layers_menu_begin(void);
void title_layers_menu_done(void);
/* Keep all original 35 base and one selected calls and their indexed writes.
 * MAIN7 is an independently optional display lease over those witnesses;
 * missing MAIN7 preserves legacy TMF, while missing TMF does not disable MAIN7.
 * Common run resources are configured separately through common_menu_runs. */
void title_layers_menu_text_begin(SDL_Surface *surface, int x, int y, const char *text, int font, int alignment, Uint8 hue, Sint8 value);
void title_layers_menu_text_done(void);
void title_layers_highlight_done(void);
void title_layers_cursor_begin(void);
void title_layers_cursor_done(void);
void title_layers_cursor_erased(void);
void title_layers_pixel(SDL_Surface *surface, Uint8 *address, enum TitleWriter writer);
void title_layers_fade_start(const SDL_Color *target, const SDL_Color *solid, unsigned int first, unsigned int last);
void title_layers_fade_step(int remaining, unsigned int first, unsigned int last);
bool title_layers_present(SDL_Renderer *renderer, SDL_Surface *source, const SDL_Rect *destination);
#endif
