/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef ASSET_DEBUG_H
#define ASSET_DEBUG_H
#include "opentyr.h"
#include "SDL.h"
#include "sprite.h"
extern bool asset_debug_enabled;
extern int asset_debug_exit_code;
void asset_debug_parse(int *,char **);
void asset_debug_level(void);
bool asset_debug_fast_forward(void);
bool asset_debug_before_tick(void);
void asset_debug_end_tick(void);
void asset_debug_finish(void);
void asset_debug_projectile(void);
void asset_debug_readback(SDL_Renderer *);
bool asset_debug_capture_tick(void);
bool asset_debug_window_only(void);
void asset_debug_reference(const char *,const char *,unsigned int,unsigned int,int,int,int,int);
void asset_debug_bind_terrain(char,unsigned int,unsigned int,const Uint8 *);
void asset_debug_terrain_row(int,int,Uint8 **);
void asset_debug_effect(SDL_Surface *,Sprite2_array,unsigned int,int,int);
#endif
