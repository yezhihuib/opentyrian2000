/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef DATA_FRAME_H
#define DATA_FRAME_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
void data_frame_set_directory(const char *);
void data_frame_begin(unsigned menu, SDL_Surface *, SDL_Surface *background, bool rebuilt);
void data_frame_surround_begin(SDL_Surface *, const void *rle, size_t bytes, unsigned w, unsigned h);
void data_frame_surround_end(SDL_Surface *);
void data_frame_pixel(SDL_Surface *, const Uint8 *);
void data_frame_rect(SDL_Surface *, const SDL_Rect *);
void data_frame_cursor_begin(SDL_Surface *);
void data_frame_cursor_done(void);
void data_frame_cursor_restored(SDL_Surface *);
bool data_frame_active(SDL_Surface *);
/* Portrait underlay reconstruction: ownership is captured before native face. */
bool data_frame_underlay_owned(SDL_Surface *,unsigned x,unsigned y);
/* Authenticate once immediately before bounded read-only sample calls. */
bool data_frame_underlay_ready(SDL_Surface *,const Uint32 *,const SDL_PixelFormat *);
bool data_frame_underlay_sample(SDL_Surface *,unsigned x,unsigned y,const Uint32 *,const SDL_PixelFormat *,Uint32 *);
void data_frame_end(void);
void data_frame_transition(bool);
void data_frame_invalidate(void);
bool data_frame_present(SDL_Renderer *, SDL_Surface *, const SDL_Rect *, const Uint32 *, const SDL_PixelFormat *);
#endif
