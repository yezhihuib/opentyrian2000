/* SPDX-License-Identifier: GPL-2.0-or-later
 * ISOLATED SYNTHETIC ORACLE. No game integration or asset approval implied. */
#ifndef WORLD_MATERIAL_H
#define WORLD_MATERIAL_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
enum {
 G101_DENSITY=8, G101_TILE_W=24, G101_TILE_H=28,
 G101_ATLAS_W=768, G101_ATLAS_H=896,
 G101_MAP_ROWS=300, G101_MAP_COLS=14, G101_MAX_MASKS=61,
 G101_TILE_PIXELS=192*224,
 G101_ATLAS_BYTES=768*896*4,
 G101_MASK_BYTES=61*192*224
};
typedef struct { bool valid, rejected; int64_t world_x,world_y; } G101Context;
typedef struct { const uint8_t *rgba; size_t bytes; int width,height,density; } G101Atlas;
typedef struct {
 int role,base;
 bool layer1_draw, verified_static_identity, score_item, independent_motion;
} G101Actor;
/* Three ordered byte-weight blends model the 119/120 footer arithmetic.
 * Production masks/clean sources and reconstruction proof are NOT implemented. */
typedef struct {
 const uint8_t *accepted_rgba;  /* Immutable accepted 856a365 source pixel. */
 const uint8_t *clean_rgba;     /* Source BEFORE the first material blend, never a baked composite. */
 uint8_t primary_weight,footer_weight;
 const uint8_t *generated_footer_rgba;
 uint8_t generated_weight;
 bool reconstruction_verified;
} G101Pixel;
void g101_begin_frame(G101Context *context);
bool g101_observe_row(G101Context *context,const void *map_base,size_t map_bytes,
 const void *actual_cell,size_t cell_size,unsigned tile_count,int x,int y);
/* Preflight a complete normal eight-row Layer1 pass before any new draw. */
bool g101_preflight_layer1(G101Context *context,const void *map_base,size_t map_bytes,
 const void *first_cell,size_t cell_size,int x,int first_y);
typedef struct { size_t atlas_bytes,mask_bytes,clean_bytes,footer_bytes,generated_bytes,total_bytes; } G101MemoryPlan;
bool g101_memory_plan(unsigned masks,unsigned clean_bases,unsigned footer_tiles,G101MemoryPlan *plan);
int g101_positive_mod(int64_t value,int period);
bool g101_atlas_valid(const G101Atlas *atlas);
bool g101_sample(const G101Context *context,const G101Atlas *atlas,
 int density,int64_t screen_x_hd,int64_t screen_y_hd,uint8_t out[4]);
bool g101_actor_eligible(const G101Actor *actor);
bool g101_full_actor_origin(int x,int y,int part,int *full_x,int *full_y);
/* Returns true only for replacement. Missing context/atlas/clean base or
 * verification means byte-exact accepted fallback, including alpha. */
bool g101_select_pixel(const G101Context *context,const G101Atlas *atlas,
 const G101Pixel *source,bool eligible,int density,int64_t screen_x_hd,
 int64_t screen_y_hd,uint8_t out[4]);
void g101_compose_layers(const uint8_t clean[4],const uint8_t material[4],
 uint8_t primary_weight,uint8_t footer_weight,uint8_t out[4]);
void g101_compose_footer(const uint8_t clean[4],const uint8_t material[4],
 const uint8_t generated[4],uint8_t primary_weight,uint8_t generated_weight,
 uint8_t ground_weight,uint8_t out[4]);
#endif
