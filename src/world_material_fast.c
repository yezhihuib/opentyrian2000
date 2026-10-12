/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "world_material_fast.h"
#include <string.h>
void g101_fast_invalidate(G101FastContext *f)
{f->valid=false;f->rgba=NULL;}
bool g101_fast_prepare(G101FastContext *f,const G101Context *c,const G101Atlas *a,int density)
{
 g101_fast_invalidate(f);
 if(!c||!c->valid||c->rejected||density!=8||!g101_atlas_valid(a))return false;
 /* Reduce before multiplication, just like the overflow-safe scalar oracle.
  * There are no modulo operations or atlas-header checks in the pixel path. */
 int ax=(g101_positive_mod(c->world_x,G101_ATLAS_W)*8)%G101_ATLAS_W;
 int ay=(g101_positive_mod(c->world_y,G101_ATLAS_H)*8)%G101_ATLAS_H;
 for(int x=0;x<G101_CANVAS_W_HD;x++) {
  f->columns[x]=(uint16_t)(ax*4);
  if(++ax==G101_ATLAS_W)ax=0;
 }
 for(int y=0;y<G101_CANVAS_H_HD;y++) {
  f->rows[y]=(uint32_t)(ay*G101_ATLAS_W*4);
  if(++ay==G101_ATLAS_H)ay=0;
 }
 f->rgba=a->rgba;f->valid=true;return true;
}
bool g101_fast_sample(const G101FastContext *f,int x,int y,uint8_t out[4])
{
 if(!f||!f->valid||(unsigned)x>=G101_CANVAS_W_HD||(unsigned)y>=G101_CANVAS_H_HD)return false;
 memcpy(out,f->rgba+f->rows[y]+f->columns[x],4);return true;
}
bool g101_fast_select_pixel(const G101FastContext *f,const G101Pixel *p,bool eligible,int x,int y,uint8_t out[4])
{
 memcpy(out,p->accepted_rgba,4);
 if(!eligible||!p->accepted_rgba[3]||(!p->primary_weight&&!p->footer_weight&&!p->generated_weight)||
    !p->clean_rgba||!p->reconstruction_verified||(p->generated_weight&&!p->generated_footer_rgba)||
    !f||!f->valid||(unsigned)x>=G101_CANVAS_W_HD||(unsigned)y>=G101_CANVAS_H_HD)return false;
 const uint8_t *material=f->rgba+f->rows[y]+f->columns[x];
 /* Exact full-primary identity, after all guards. Keep selected-pack alpha. */
 if(p->primary_weight==255&&!p->generated_weight&&!p->footer_weight) {
  memcpy(out,material,3);return true;
 }
 uint8_t composed[4];
 /* Same ordered integer compositor as the scalar oracle, including alpha. */
 g101_compose_footer(p->clean_rgba,material,p->generated_footer_rgba,
  p->primary_weight,p->generated_weight,p->footer_weight,composed);
 memcpy(out,composed,3);return true;
}
