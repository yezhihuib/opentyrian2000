/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef GAME_PROBE_H
#define GAME_PROBE_H
#include "opentyr.h"
#include "SDL.h"
#include <stdint.h>
extern bool game_probe_enabled;
/* Display-only opt-in; never enables replay, diagnostics or scripted input. */
extern bool manual_hd_enabled;
extern int game_probe_density;
extern bool game_probe_missing, game_probe_repeat, game_probe_invalid;
extern bool game_probe_coverage_fault;
extern bool game_probe_skip;
extern bool game_probe_local_blend;
extern bool game_probe_original_reference;
extern unsigned int game_probe_scene_assets;
extern bool game_probe_known_blend,game_probe_blend_capture;
extern const char *game_probe_assets;
extern unsigned int game_probe_tick;
void game_probe_parse(int *argc, char **argv);
void game_probe_start(void);
bool game_probe_level(void);
bool game_probe_input(void);
bool game_probe_end_tick(void);
void game_probe_collision(const char *kind, int a, int b, int value);
void game_probe_frame(unsigned int hd_draws, unsigned int occlusions, unsigned int mismatch, const char *reason, const char *all_rejections, unsigned int local_entities, unsigned int local_regions, unsigned int local_blocks);
void game_probe_present(unsigned int count, uint64_t before, uint64_t after);
uint64_t game_probe_hash(uint64_t h, const void *data, size_t size);
void game_probe_export(SDL_Surface *surface, const char *name);
bool game_probe_capture_tick(void);
bool game_probe_capture_disabled(void);
void game_probe_effects(unsigned int brightness_blocks, unsigned int restored_checks, unsigned int restored_mismatches, unsigned int expanded_regions, unsigned int boundary_crossings);
void game_probe_fade_sample(SDL_Surface *, int remaining_steps, unsigned int hd_pixels, int mode);
void game_probe_pose(int player_number, int bank, int base, int index, int banking, int x, int y, int velocity, int delta, unsigned int invulnerable, int has_shadow, int shadow_x, int shadow_y);
void game_probe_fire(int player_number, int port, int bay, int x, int y, int weapon, int last_slot);
unsigned int game_probe_shot_begin(unsigned int port,unsigned int bay,unsigned int weapon,unsigned int player,int x,int y);
void game_probe_shot_result(unsigned int call,const char *result,unsigned int emitted,int slot);
void game_probe_shot_emit(unsigned int call,unsigned int multi,unsigned int pattern,int slot);
void game_probe_shot_draw(int slot,unsigned int raw,int bank,unsigned int index,int x,int y,int style,int width,int height);
void game_probe_draw(int bank, unsigned int index, int x, int y, int style, int layout, bool mirrored);
void game_probe_scene_draw(int role, unsigned int index, int x, int y, int part, int style, bool mirrored);
void game_probe_rgb_audit(SDL_Surface *, unsigned int classic_mismatches);
void game_probe_blend_write(bool known,unsigned int index,int origin_x,int origin_y,int x,int y,Uint8 before,Uint8 source,Uint8 after,unsigned int subpixels,unsigned int restored_blocks,bool rgba);
void game_probe_restore_region(unsigned int source_index,SDL_Rect requested,SDL_Rect restored,unsigned int groups,unsigned int blocks);
#endif
