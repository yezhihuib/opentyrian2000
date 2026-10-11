/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "entity_draw.h"
#include "render_mirror.h"
#ifndef RENDER_MIRROR_DISABLED
#include "game_probe.h"
#endif

void draw_entity_sprite2(SDL_Surface *target, int x, int y,
                         Sprite2_array bank, unsigned int index,
                         EntityDrawStyle style, EntityDrawLayout layout)
{
	ae_before(target,x,y,bank,index,style);
	bool mirrored=render_mirror_entity(target,x,y,bank,index,style,layout);
#ifndef RENDER_MIRROR_DISABLED
	int role=bank.data==spriteSheet9.data?9:bank.data==spriteSheet8.data?8:bank.data==explosionSpriteSheet.data?6:0;
	game_probe_draw(role,index,x,y,style,layout,mirrored);
#else
	(void)mirrored;
#endif
	ae_after_mirror(mirrored);
	if (layout == ENTITY_QUAD)
	{
		switch (style)
		{
		case ENTITY_NORMAL: blit_sprite2x2(target, x, y, bank, index); break;
		case ENTITY_BLEND: blit_sprite2x2_blend(target, x, y, bank, index); break;
		case ENTITY_SHADOW: blit_sprite2x2_darken(target, x, y, bank, index); break;
		}
	}
	else
	{
		switch (style)
		{
		case ENTITY_NORMAL: blit_sprite2(target, x, y, bank, index); break;
		case ENTITY_BLEND: blit_sprite2_blend(target, x, y, bank, index); break;
		case ENTITY_SHADOW: blit_sprite2_darken(target, x, y, bank, index); break;
		}
	}
	ae_after_original();
	render_mirror_entity_end();
}
