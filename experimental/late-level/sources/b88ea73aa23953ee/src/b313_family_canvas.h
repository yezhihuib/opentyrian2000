#ifndef B313_FAMILY_CANVAS_H
#define B313_FAMILY_CANVAS_H
#include <stdbool.h>
#include <stdint.h>
#include "sprite.h"
typedef struct {
 bool requested,frame_active,frame_failed,ready,production_enabled;
 unsigned first_reason;
 uint64_t frames,draws,accepted_frames,fallback_frames,presents,occlusions;
 uint64_t phase_draws[3],cycle_mask,last_nonce,canvas_generation;
 uint64_t native_pixels,shadow_pixels,blend_fallbacks;
} B313FamilyCanvasStatus;
#ifndef RENDER_MIRROR_DISABLED
bool render_mirror_family_requested(void);
bool render_mirror_family_tile(SDL_Surface *,unsigned,int,int,Sprite2_array *,unsigned,int,int);
void render_mirror_family_report(void);
B313FamilyCanvasStatus render_mirror_family_status(void);
#else
static inline bool render_mirror_family_requested(void){return false;}
static inline bool render_mirror_family_tile(SDL_Surface *s,unsigned i,int x,int y,Sprite2_array *b,unsigned a,int p,int f)
{(void)s;(void)i;(void)x;(void)y;(void)b;(void)a;(void)p;(void)f;return false;}
static inline void render_mirror_family_report(void){}
static inline B313FamilyCanvasStatus render_mirror_family_status(void){const B313FamilyCanvasStatus s={0};return s;}
#endif
#endif
