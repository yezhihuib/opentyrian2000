/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef RENDER_MIRROR_H
#define RENDER_MIRROR_H
#include "sprite.h"
#include "ground101_material.h"
#include "gameplay_hud_meters.h"
enum { MIRROR_NORMAL, MIRROR_BLEND, MIRROR_SHADOW };
#ifdef RENDER_MIRROR_DISABLED
#define render_mirror_owns_display() false
#define render_mirror_text_begin(...) ((void)0)
#define render_mirror_text_end(...) ((void)0)
#define render_mirror_text_glyph_begin(...) ((void)0)
#define render_mirror_text_glyph_end(...) ((void)0)
#define render_mirror_text_level_begin(...) ((void)0)
#define render_mirror_text_level_end(...) ((void)0)
#define render_mirror_text_message_begin(...) ((void)0)
#define render_mirror_text_message_backdrop(...) ((void)0)
#define render_mirror_text_message_end(...) ((void)0)
#define render_mirror_text_message_erase_begin(...) ((void)0)
#define render_mirror_text_message_erased(...) ((void)0)
#define render_mirror_hud_shutdown(...) ((void)0)
#define render_mirror_hud_reset(...) ((void)0)
#define render_mirror_hud_start(...) ((void)0)
#define render_mirror_hud_suspend(...) ((void)0)
#define render_mirror_hud_shield_wiped(...) ((void)0)
#define render_mirror_hud_shield_drawn(...) ((void)0)
#define render_mirror_hud_mode_drawn(...) ((void)0)
#define render_mirror_hud_meter_begin(...) ((void)0)
#define render_mirror_hud_meter_end(...) ((void)0)
#define render_mirror_begin(...) ((void)0)
#define render_mirror_pixel(...) ((void)0)
#define render_mirror_rect(...) ((void)0)
#define render_mirror_unsupported(...) ((void)0)
#define render_mirror_coin25_value_begin(...) ((void)0)
#define render_mirror_coin75_value_begin(...) ((void)0)
#define render_mirror_coin50_value_begin(...) ((void)0)
#define render_mirror_entity(...) false
#define render_mirror_entity_end(...) ((void)0)
#define render_mirror_finish(...) ((void)0)
#define render_mirror_present(...) false
#define render_mirror_release_texture(...) ((void)0)
#define render_mirror_brightness_pixel(...) ((void)0)
#define render_mirror_fade_start(...) ((void)0)
#define render_mirror_fade_step(...) ((void)0)
#define render_mirror_enemy_tile(...) false
#define render_mirror_enemy_shot(...) false
#define render_mirror_map_begin(...) ((void)0)
#define render_mirror_bind_terrain(...) ((void)0)
#define render_mirror_terrain_row(...) 0u
#define render_mirror_ground101_layer1(...) ((void)0)
#define render_mirror_terrain_pixel(...) ((void)0)
#define render_mirror_sprite2_blend_pixel(...) ((void)0)
#define render_mirror_set_talon_banking(...) ((void)0)
#define render_mirror_reset_banking(...) ((void)0)
#define render_mirror_player_pose(...) ((void)0)
#else
bool render_mirror_owns_display(void);
void render_mirror_text_begin(SDL_Surface *,unsigned kind,int x,int y,const char *,unsigned hue,int value);
void render_mirror_text_end(void);
void render_mirror_text_glyph_begin(SDL_Surface *,int x,int y,unsigned table,unsigned id,bool black,unsigned hue,int value);
void render_mirror_text_glyph_end(void);
void render_mirror_text_level_begin(SDL_Surface *,const char *);
void render_mirror_text_level_end(void);
void render_mirror_text_message_begin(const char *,bool will_erase);
void render_mirror_text_message_backdrop(void);
void render_mirror_text_message_end(void);
void render_mirror_text_message_erase_begin(void);
void render_mirror_text_message_erased(bool help_prompt);
void render_mirror_hud_shutdown(void);
void render_mirror_hud_reset(void);
void render_mirror_hud_start(SDL_Surface *decoded_pic3);
void render_mirror_hud_suspend(void);
void render_mirror_hud_mode_drawn(SDL_Surface *surface,unsigned int mode);
void render_mirror_hud_meter_begin(SDL_Surface *surface,SDL_Surface *draw_surface,unsigned int kind,unsigned int a,unsigned int b);
void render_mirror_hud_meter_end(SDL_Surface *surface,unsigned int kind);
void render_mirror_hud_shield_wiped(SDL_Surface *surface);
void render_mirror_hud_shield_drawn(SDL_Surface *surface,unsigned int shield,unsigned int maximum);
void render_mirror_begin(void);
bool render_mirror_enemy_shot(SDL_Surface *, int x, int y, Sprite2_array, unsigned int index);
void render_mirror_pixel(SDL_Surface *, Uint8 *address, Uint8 source, int style);
void render_mirror_rect(SDL_Surface *, const SDL_Rect *);
void render_mirror_unsupported(const char *reason);
void render_mirror_coin25_value_begin(bool fixed);
void render_mirror_coin75_value_begin(bool fixed);
void render_mirror_coin50_value_begin(bool fixed);
bool render_mirror_entity(SDL_Surface *, int x, int y, Sprite2_array, unsigned int index, int style, int layout);
void render_mirror_entity_end(void);
void render_mirror_finish(bool ordinary_crop);
bool render_mirror_present(SDL_Renderer *, SDL_Surface *, const SDL_Rect *);
void render_mirror_release_texture(void);
void render_mirror_brightness_pixel(SDL_Surface *, Uint8 *address, int value);
void render_mirror_fade_start(const SDL_Color *colors, const SDL_Color *solid, unsigned int first, unsigned int last);
void render_mirror_fade_step(int steps);
bool render_mirror_enemy_tile(SDL_Surface *, int x, int y, Sprite2_array, unsigned int base, int part, int filter, const G101EnemyContext *);
void render_mirror_ground101_layer1(SDL_Surface *, const void *first_cell, int x, int y);
void render_mirror_map_begin(char shape_file);
void render_mirror_bind_terrain(unsigned int layer, unsigned int id, const Uint8 *data);
unsigned int render_mirror_terrain_row(SDL_Surface *, int x, int y, Uint8 **map, int style);
void render_mirror_terrain_pixel(SDL_Surface *, Uint8 *, Uint8 source, int style, bool replaced);
void render_mirror_sprite2_blend_pixel(SDL_Surface *, Uint8 *, Uint8 source, Sprite2_array, unsigned int index, int origin_x, int origin_y);
void render_mirror_set_talon_banking(bool enabled);
void render_mirror_reset_banking(void);
void render_mirror_player_pose(unsigned int player_number, Sprite2_array, int base, int index, unsigned int invulnerable_ticks);
#endif
#endif
