/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef DATA_TEXT_H
#define DATA_TEXT_H
#include "SDL.h"
#include <stdbool.h>
void data_text_set_directory(const char *directory);
void data_text_set_language(const char *language);
const char *data_text_language(void);
void data_text_toggle(void);
void data_text_episode(unsigned episode, const char *directory);
void data_text_bind(unsigned slot, unsigned occurrence);
void data_text_begin(unsigned menu, unsigned selected_slot, unsigned slots, SDL_Surface *screen);
void data_text_end(void);
void data_text_transition(bool begin);
bool data_text_body_active(void);
void data_text_scroll(int lines);
void data_text_page(int direction);
void data_text_scroll_held(int direction, bool page);
void data_text_home(bool end);
void data_text_wheel(int lines);
void data_text_mouse_scroll(int direction);
void data_text_present(SDL_Renderer *renderer, SDL_Surface *screen, const SDL_Rect *output);
void data_text_cursor_frame_owner(bool owner);
void data_text_cursor_begin(SDL_Surface *screen);
void data_text_cursor_pixel(SDL_Surface *screen, const Uint8 *pixel);
void data_text_cursor_done(void);
void data_text_cursor_clear(void);
void data_text_cursor_present(SDL_Renderer *renderer, SDL_Surface *screen, const SDL_Rect *output, const Uint32 *rgb, const SDL_PixelFormat *format);
void data_text_invalidate(void);
#endif
