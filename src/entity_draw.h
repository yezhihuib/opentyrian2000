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

#endif
