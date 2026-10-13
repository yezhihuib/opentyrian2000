/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef STARTUP_LOGOS_H
#define STARTUP_LOGOS_H
#include "SDL.h"
#include <stdbool.h>

/* Optional display-only PIC10/PIC12 ownership. No gameplay activation. */
bool startup_logos_owns_display(void);
bool startup_logos_set_directory(const char *directory);
bool startup_logos_configured(void);
void startup_logos_begin(void);
void startup_logos_bind(SDL_Surface *source, unsigned int pic, const SDL_Color *target);
void startup_logos_reset(void);
void startup_logos_end(void);
void startup_logos_shutdown(void);
void startup_logos_release_texture(void);
void startup_logos_fade_start(const SDL_Color *target, const SDL_Color *solid,
                             unsigned int first, unsigned int last);
void startup_logos_fade_step(int remaining, unsigned int first, unsigned int last);
bool startup_logos_present(SDL_Renderer *renderer, SDL_Surface *source, const SDL_Rect *destination);
#endif
