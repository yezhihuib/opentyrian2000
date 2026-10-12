/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private unit driver: exercise the actual get_asset implementation without
 * changing any game data or running a gameplay fixture. Unused renderer entry
 * points are discarded by -ffunction-sections/-Wl,--gc-sections. */
#include <assert.h>
#include <limits.h>
#include "../src/render_mirror.c"

bool game_probe_enabled;
int game_probe_density = 8;
bool game_probe_missing, game_probe_repeat, game_probe_invalid;
bool game_probe_original_reference;
const char *game_probe_assets;
Sprite2_array spriteSheet8, spriteSheet9, explosionSpriteSheet;
Uint32 rgb_palette[256];

int main(int argc, char **argv)
{
 assert(argc == 2);
 game_probe_assets = argv[1];
 Uint8 sheet8[2]={0},sheet9[2]={0},explosion[2]={0},other_data[2]={0};
 spriteSheet8=(Sprite2_array){.data=sheet8,.size=sizeof(sheet8)};
 spriteSheet9=(Sprite2_array){.data=sheet9,.size=sizeof(sheet9)};
 explosionSpriteSheet=(Sprite2_array){.data=explosion,.size=sizeof(explosion)};
 Sprite2_array other={.data=other_data,.size=sizeof(other_data)};
 assert(sizeof(assets)/sizeof(assets[0]) == 333);
 for(unsigned int id=252;id<=254;id++) {
  Asset *a=get_asset(spriteSheet8,id,ENTITY_TILE);
  assert(a==&assets[330+id-252] && a->valid && a->index==(int)id && a->bank==8);
  assert(a->w==12 && a->h==14 && a->anchor_x==0 && a->anchor_y==0 && a->density==8);
  assert(get_asset(spriteSheet8,id,ENTITY_QUAD)==NULL);
  assert(get_asset(spriteSheet9,id,ENTITY_TILE)==NULL);
  assert(get_asset(spriteSheet9,id,ENTITY_QUAD)==NULL);
  assert(get_asset(other,id,ENTITY_TILE)==NULL);
  Asset *shield=get_asset(explosionSpriteSheet,id,ENTITY_TILE);
  assert(shield && shield!=a && shield->bank==ASSET_EXPLOSION && shield->index==(int)id);
  assert(shield < &assets[330]);
 }
 assert(get_asset(spriteSheet8,0,ENTITY_TILE)==NULL);
 assert(get_asset(spriteSheet8,251,ENTITY_TILE)==NULL);
 assert(get_asset(spriteSheet8,255,ENTITY_TILE)==NULL);
 assert(get_asset(spriteSheet8,UINT_MAX,ENTITY_TILE)==NULL);
 for(int id=254;id>=252;id--) {
  Asset *a=get_asset(spriteSheet8,(unsigned int)id,ENTITY_TILE);
  assert(a==&assets[330+id-252] && a->bank==8 && a->index==id);
 }
 /* Preceding finite family ends at329; its cache entry is distinct. */
 Asset *previous=get_asset(spriteSheet8,21,ENTITY_TILE);
 assert(previous==&assets[329] && previous->bank==8 && previous->index==21);
 assert(assets[330].index==252 && assets[331].index==253 && assets[332].index==254);
 for(unsigned int i=0;i<333;i++)free(assets[i].rgba);
 puts("PASS: exact bank/layout/index boundaries,333 capacity,330..332 unique caches, original explosion namespace and preceding329 remain distinct");
 return 0;
}
