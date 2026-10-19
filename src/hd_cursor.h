/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef HD_CURSOR_H
#define HD_CURSOR_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
/* Observe an authenticated native 2x2 draw at its original sprite-space
 * top-left, before any pixels change. Never write to the indexed surface. */
void hd_cursor_begin(SDL_Surface *,int x,int y,unsigned sprite,const void *sheet,size_t bytes,bool visible,int filter);
void hd_cursor_done(void);
void hd_cursor_clear(void);
void hd_cursor_release(void);
/* Preflight the entire display replacement before any layer omits native ink. */
void hd_cursor_prepare(SDL_Renderer *,SDL_Surface *,const SDL_Rect *,const Uint32 *palette,const SDL_PixelFormat *);
bool hd_cursor_active(void);
SDL_Surface *hd_cursor_underlay(SDL_Surface *);
bool hd_cursor_present(SDL_Renderer *,const SDL_Rect *);
#endif
