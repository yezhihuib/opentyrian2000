/* Private acceptance instrumentation. Never part of the product checkpoint. */
#ifndef SETTINGS_FIXTURE_H
#define SETTINGS_FIXTURE_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
void sf_fixture_init(void);
void sf_fixture_title(size_t selected);
void sf_fixture_frame(unsigned menu,size_t selected,unsigned picker,size_t picker_selected);
void sf_fixture_ready(void);
void sf_fixture_advance(void);
void sf_fixture_exit(void);
void sf_fixture_present(SDL_Renderer *,const char *owner);
void sf_fixture_lease(bool active,bool frame,unsigned commands,unsigned generation);
void sf_fixture_pixel(SDL_Surface *,Uint8 *,int style);
void sf_fixture_rect(SDL_Surface *,const SDL_Rect *);
void sf_fixture_fade(int remaining,unsigned first,unsigned last);
void sf_fixture_wait(const char *,int argument);
void sf_fixture_jukebox_enter(void);
void sf_fixture_jukebox_poll(void);
void sf_fixture_jukebox_exit(void);
void sf_fixture_recreate_video(void);
#endif
