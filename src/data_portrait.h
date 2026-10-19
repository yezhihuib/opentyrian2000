/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef DATA_PORTRAIT_H
#define DATA_PORTRAIT_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
void data_portrait_set_directory(const char *);
void data_portrait_begin(unsigned menu,SDL_Surface *,bool rebuilt);
void data_portrait_capture(SDL_Surface *,unsigned face,unsigned palette,int x,int y,const void *rle,size_t bytes,unsigned w,unsigned h);
void data_portrait_face_done(SDL_Surface *);
void data_portrait_pixel(SDL_Surface *,const Uint8 *);
void data_portrait_rect(SDL_Surface *,const SDL_Rect *);
void data_portrait_cursor_begin(SDL_Surface *);
void data_portrait_cursor_done(void);
void data_portrait_cursor_restored(SDL_Surface *);
bool data_portrait_active(SDL_Surface *);
void data_portrait_end(void);
void data_portrait_invalidate(void);
void data_portrait_transition(bool);
bool data_portrait_present(SDL_Renderer *,SDL_Surface *,const SDL_Rect *,const Uint32 *,const SDL_PixelFormat *);
#endif
