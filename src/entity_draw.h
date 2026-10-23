/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef ENTITY_DRAW_H
#define ENTITY_DRAW_H

#include "sprite.h"

/* A deliberately small drawing boundary. Coordinates and sprite IDs are
 * captured at the original call site, before subsequent gameplay updates.
 * This interface has no access to players, weapons, timers or random state.
 * The game currently uses the exact classic blitters through this boundary.
 */
typedef enum { ENTITY_NORMAL, ENTITY_BLEND, ENTITY_SHADOW } EntityDrawStyle;
typedef enum { ENTITY_TILE, ENTITY_QUAD } EntityDrawLayout;

void draw_entity_sprite2(SDL_Surface *target, int x, int y,
                         Sprite2_array bank, unsigned int index,
                         EntityDrawStyle style, EntityDrawLayout layout);

/* Ordinary player QUAD semantic boundary; original indexed draw remains once. */
void draw_player_ship_sprite2(SDL_Surface *,int,int,Sprite2_array,unsigned,EntityDrawStyle,unsigned,int);

/* Dedicated provenance-gated bank8 normal head; fallback keeps existing roles. */
void draw_player_shot_sprite2(SDL_Surface *,int x,int y,Sprite2_array,unsigned index,unsigned slot,unsigned raw);
void draw_player_shot_shadow_sprite2(SDL_Surface *,int x,int y,Sprite2_array,unsigned index,unsigned slot,unsigned raw);

/* Dedicated surviving enemy-shot normal tile; no player-shadow binding. */
void draw_enemy_shot_sprite2(SDL_Surface *, int x, int y, Sprite2_array, unsigned int index);

/* Dedicated normal TILE body boundary; gameplay state is only inspected. */
void draw_sidekick_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,
                               unsigned int index,unsigned int option,
                               unsigned int sidekick_style,unsigned int charge);

/* Dedicated three-phase normal Mint body; original indexed call always runs. */
void draw_mint_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,
                           unsigned int index,unsigned int option,
                           unsigned int sidekick_style,unsigned int charge);

/* Dedicated static FrontBlaster QUAD; the original four-tile draw always runs. */
void draw_frontblaster_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,
                                   unsigned int index,unsigned int option,
                                   unsigned int sidekick_style,unsigned int charge);

/* Dedicated five-frame normal Plasma body; original indexed call always runs. */
void draw_plasma_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,
                             unsigned int index,unsigned int option,
                             unsigned int sidekick_style,unsigned int charge);

/* Dedicated normal Charge body; no runtime animation or charge state changes. */
void draw_charge_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,
                             unsigned int index,unsigned int option,
                             unsigned int sidekick_style,unsigned int charge);

void draw_explosion_sprite2(SDL_Surface *,int,int,Sprite2_array,unsigned,EntityDrawStyle,unsigned slot);
#endif
