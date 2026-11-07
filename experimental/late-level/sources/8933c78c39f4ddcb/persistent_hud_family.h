/* Private persistent final-INDEX HUD. Observation hooks never grant world HD. */
#ifndef PERSISTENT_HUD_FAMILY_H
#define PERSISTENT_HUD_FAMILY_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct {
 bool requested,captured,composed; uint64_t generation,transactions,accepted,rejected,stores,callbacks,composes,restores;
 unsigned active_kind,expected_ops,observed_ops,layer_cells[6],text_valid,meters,mode;
} PersistentHudStatus;
#ifndef RENDER_MIRROR_DISABLED
void render_mirror_persistent_source_reset(unsigned);
void render_mirror_persistent_store(SDL_Surface *,const void *,size_t,unsigned);
void render_mirror_persistent_unknown(SDL_Surface *,const void *,size_t);
void render_mirror_persistent_fill_before(SDL_Surface *,const SDL_Rect *,Uint8);
void render_mirror_persistent_fill_after(SDL_Surface *,const SDL_Rect *,int);
void render_mirror_persistent_sprite_begin(SDL_Surface *,int,int,unsigned,unsigned);
void render_mirror_persistent_sprite_end(void);
void render_mirror_persistent_shield_begin(SDL_Surface *,unsigned,unsigned);
void render_mirror_persistent_wipe_begin(SDL_Surface *,unsigned);
void render_mirror_persistent_mode_begin(SDL_Surface *,unsigned);
PersistentHudStatus render_mirror_persistent_hud_status(void);
bool render_mirror_persistent_hud_owners(uint8_t *,size_t);
#else
#define render_mirror_persistent_source_reset(...) ((void)0)
#define render_mirror_persistent_store(...) ((void)0)
#define render_mirror_persistent_unknown(...) ((void)0)
#define render_mirror_persistent_fill_before(...) ((void)0)
#define render_mirror_persistent_fill_after(...) ((void)0)
#define render_mirror_persistent_sprite_begin(...) ((void)0)
#define render_mirror_persistent_sprite_end(...) ((void)0)
#define render_mirror_persistent_shield_begin(...) ((void)0)
#define render_mirror_persistent_wipe_begin(...) ((void)0)
#define render_mirror_persistent_mode_begin(...) ((void)0)
#endif
#endif
