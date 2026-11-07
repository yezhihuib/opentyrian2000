/* Private fast sampling revision. The scalar core remains the reference. */
#ifndef WORLD_MATERIAL_FAST_H
#define WORLD_MATERIAL_FAST_H
#include "world_material.h"
enum { G101_CANVAS_W_HD=320*8,G101_CANVAS_H_HD=200*8 };
typedef struct {
 bool valid;
 const uint8_t *rgba;
 uint16_t columns[G101_CANVAS_W_HD]; /* byte offset within one atlas row */
 uint32_t rows[G101_CANVAS_H_HD];    /* byte offset of one atlas row */
} G101FastContext;
void g101_fast_invalidate(G101FastContext *);
bool g101_fast_prepare(G101FastContext *,const G101Context *,const G101Atlas *,int density);
bool g101_fast_sample(const G101FastContext *,int x,int y,uint8_t out[4]);
bool g101_fast_select_pixel(const G101FastContext *,const G101Pixel *,bool eligible,int x,int y,uint8_t out[4]);
/* cap_rgba is a separately verified atlas of the same finite dimensions.
 * Reuse the lower material's saved offsets, without a second lookup table. */
bool g101_fast_select_cap(const G101FastContext *,const uint8_t *cap_rgba,
 const uint8_t accepted[4],uint8_t weight,int x,int y,uint8_t out[4]);
#endif
