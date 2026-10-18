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
	bool mirrored=render_mirror_entity(target,x,y,bank,index,style,layout);
#ifndef RENDER_MIRROR_DISABLED
	int role=bank.data==spriteSheet9.data?9:bank.data==spriteSheet8.data?8:bank.data==spriteSheet12.data?12:bank.data==explosionSpriteSheet.data?6:0;
	game_probe_draw(role,index,x,y,style,layout,mirrored);
#else
	(void)mirrored;
#endif
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
	render_mirror_entity_end();
}

/* A failed optional head retains the exact generic fallback. On success the
 * probe and one indexed blit remain in their original order. Shadows never enter. */
void draw_player_shot_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,
 unsigned index,unsigned slot,unsigned raw)
{
#ifndef RENDER_MIRROR_DISABLED
 if(render_mirror_rear_p1_head(target,x,y,bank,index,slot,raw)) {
  game_probe_draw(8,index,x,y,ENTITY_NORMAL,ENTITY_TILE,true);
  blit_sprite2(target,x,y,bank,index);
  render_mirror_entity_end();
  return;
 }
#else
 (void)slot;(void)raw;
#endif
 draw_entity_sprite2(target,x,y,bank,index,ENTITY_NORMAL,ENTITY_TILE);
}

/* The dedicated rear shadow leases only the immediately following original
 * darken call. Every declined context keeps the exact generic shadow path. */
void draw_player_shot_shadow_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,
 unsigned index,unsigned slot,unsigned raw)
{
#ifndef RENDER_MIRROR_DISABLED
 if(render_mirror_rear_p11_shadow(target,x,y,bank,index,slot,raw)) {
  game_probe_draw(8,index,x,y,ENTITY_SHADOW,ENTITY_TILE,true);
  blit_sprite2_darken(target,x,y,bank,index);
  render_mirror_entity_end();
  return;
 }
#else
 (void)slot;(void)raw;
#endif
 draw_entity_sprite2(target,x,y,bank,index,ENTITY_SHADOW,ENTITY_TILE);
}

/* The indexed original always executes once, even after successful HD output. */
void draw_enemy_shot_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,unsigned int index)
{
 bool mirrored=render_mirror_enemy_shot(target,x,y,bank,index);
#ifndef RENDER_MIRROR_DISABLED
 if(bank.data==spriteSheet8.data&&(index==112||index==113))
  game_probe_scene_draw(108,index,x,y,0,ENTITY_NORMAL,mirrored);
 else if(bank.data==spriteSheet8.data&&(index==77||index==58||index==182||index==163||index==1||index==183||index==164))
  game_probe_scene_draw(111,index,x,y,0,ENTITY_NORMAL,mirrored);
 else if(bank.data==spriteSheet8.data&&(index==146||index==147))
  game_probe_scene_draw(122,index,x,y,0,ENTITY_NORMAL,mirrored);
#else
 (void)mirrored;
#endif
 blit_sprite2(target,x,y,bank,index);
 render_mirror_entity_end();
}

/* Original sidekick body coordinates and indexed writes are never replaced. */
void draw_sidekick_body_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,
                               unsigned int index,unsigned int option,
                               unsigned int sidekick_style,unsigned int charge)
{
 (void)render_mirror_marlo_body(target,x,y,bank,index,option,sidekick_style,charge);
 blit_sprite2(target,x,y,bank,index);
 render_mirror_entity_end();
}

/* Mint16 keeps its original phase, placement and single indexed draw. */
void draw_mint_body_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,
                           unsigned int index,unsigned int option,
                           unsigned int sidekick_style,unsigned int charge)
{
 (void)render_mirror_mint_body(target,x,y,bank,index,option,sidekick_style,charge);
 blit_sprite2(target,x,y,bank,index);
 render_mirror_entity_end();
}

/* FrontBlaster20 keeps the original complete QUAD and four indexed tile calls. */
void draw_frontblaster_body_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,
                                   unsigned int index,unsigned int option,
                                   unsigned int sidekick_style,unsigned int charge)
{
 (void)render_mirror_frontblaster_body(target,x,y,bank,index,option,sidekick_style,charge);
 blit_sprite2x2(target,x,y,bank,index);
 render_mirror_entity_end();
}

/* Plasma9 keeps its original twenty-phase animation and single indexed draw. */
void draw_plasma_body_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,
                             unsigned int index,unsigned int option,
                             unsigned int sidekick_style,unsigned int charge)
{
 (void)render_mirror_plasma_body(target,x,y,bank,index,option,sidekick_style,charge);
 blit_sprite2(target,x,y,bank,index);
 render_mirror_entity_end();
}
