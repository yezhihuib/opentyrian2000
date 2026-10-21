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
 int global=render_mirror_global_green_head(target,x,y,bank,index,ENTITY_NORMAL,slot,raw);
 if(global<0)global=render_mirror_global_vulcan(target,x,y,bank,index,ENTITY_NORMAL,slot,raw);
 if(global<0)global=render_mirror_global_pulse(target,x,y,bank,index,ENTITY_NORMAL,slot,raw);
 if(global>=0) {
  game_probe_draw(8,index,x,y,ENTITY_NORMAL,ENTITY_TILE,global>0);
  blit_sprite2(target,x,y,bank,index);render_mirror_entity_end();return;
 }

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
 int global=render_mirror_global_green_head(target,x,y,bank,index,ENTITY_SHADOW,slot,raw);
 if(global<0)global=render_mirror_global_vulcan(target,x,y,bank,index,ENTITY_SHADOW,slot,raw);
 if(global<0)global=render_mirror_global_pulse(target,x,y,bank,index,ENTITY_SHADOW,slot,raw);
 if(global>=0) {
  game_probe_draw(8,index,x,y,ENTITY_SHADOW,ENTITY_TILE,global>0);
  blit_sprite2_darken(target,x,y,bank,index);render_mirror_entity_end();return;
 }

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
  game_probe_scene_draw(asteroid_hd_enabled?142:108,index,x,y,0,ENTITY_NORMAL,mirrored);
 else if(bank.data==spriteSheet8.data&&(index==77||index==58||index==182||index==163||index==1||index==183||index==164))
  game_probe_scene_draw(111,index,x,y,0,ENTITY_NORMAL,mirrored);
 else if(bank.data==spriteSheet8.data&&(index==146||index==147))
  game_probe_scene_draw(122,index,x,y,0,ENTITY_NORMAL,mirrored);
 else if(bank.data==spriteSheet8.data&&index==304)
  game_probe_scene_draw(140,index,x,y,0,ENTITY_NORMAL,mirrored);
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

/* Tri-state admission prevents a rejected migrated identity from falling back
 * through a warm generic cache. Unsupported ships retain their old path. */
void draw_player_ship_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,
 unsigned index,EntityDrawStyle style,unsigned player,int base)
{
#ifndef RENDER_MIRROR_DISABLED
 int admitted=render_mirror_global_player_ship(target,x,y,bank,index,style,player,base);
 if(admitted<0){draw_entity_sprite2(target,x,y,bank,index,style,ENTITY_QUAD);return;}
 int role=bank.data==spriteSheet9.data?9:bank.data==spriteSheet8.data?8:bank.data==spriteSheet12.data?12:bank.data==explosionSpriteSheet.data?6:0;
 game_probe_draw(role,index,x,y,style,ENTITY_QUAD,admitted>0);
 switch(style){
 case ENTITY_NORMAL:blit_sprite2x2(target,x,y,bank,index);break;
 case ENTITY_BLEND:blit_sprite2x2_blend(target,x,y,bank,index);break;
 case ENTITY_SHADOW:blit_sprite2x2_darken(target,x,y,bank,index);break;
 }
 render_mirror_entity_end();
#else
 (void)player;(void)base;draw_entity_sprite2(target,x,y,bank,index,style,ENTITY_QUAD);
#endif
}

/* Authenticated shield slots bypass the generic cache on both success and decline. */
void draw_explosion_sprite2(SDL_Surface *target,int x,int y,Sprite2_array bank,unsigned index,EntityDrawStyle style,unsigned slot)
{
#ifndef RENDER_MIRROR_DISABLED
 int admitted=render_mirror_global_green_smoke(target,x,y,bank,index,style,slot);
 if(admitted<0)admitted=render_mirror_global_cash25_value(target,x,y,bank,index,style,slot);
 if(admitted<0)admitted=render_mirror_global_small_explosion(target,x,y,bank,index,style,slot);
 if(admitted<0)admitted=render_mirror_global_smoke(target,x,y,bank,index,style,slot);
 if(admitted<0)admitted=render_mirror_global_hitflare(target,x,y,bank,index,style,slot);
 if(admitted<0)admitted=render_mirror_global_shield(target,x,y,bank,index,style,slot);
 if(admitted<0){draw_entity_sprite2(target,x,y,bank,index,style,ENTITY_TILE);return;}
 game_probe_draw(6,index,x,y,style,ENTITY_TILE,admitted>0);
 if(style==ENTITY_BLEND)blit_sprite2_blend(target,x,y,bank,index);
 else blit_sprite2(target,x,y,bank,index);
 render_mirror_entity_end();
#else
 (void)slot;draw_entity_sprite2(target,x,y,bank,index,style,ENTITY_TILE);
#endif
}
