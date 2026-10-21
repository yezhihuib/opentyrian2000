/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reconstructed P/ESC observer. None of these calls mutates engine pixels,
 * input, timing, economy, settings, audio, or performs an additional Present. */
#ifndef COMMON_PAUSE_H
#define COMMON_PAUSE_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
enum CommonPauseKind { COMMON_PAUSE_P, COMMON_PAUSE_ESC };
enum CommonPauseRun { COMMON_PAUSE_LABEL, COMMON_PAUSE_NAME, COMMON_PAUSE_DETAIL, COMMON_PAUSE_SPEED, COMMON_PAUSE_HELP };
enum CommonPauseGlyph { COMMON_PAUSE_DARK, COMMON_PAUSE_BLACK, COMMON_PAUSE_FACE, COMMON_PAUSE_UNSAFE, COMMON_PAUSE_ORIGINAL, COMMON_PAUSE_BLEND };
/* In-memory adapter only, NOT an on-disk RFR layout. The separately verified
 * resource family supplies exactly 16 immutable English runs, indexed by the
 * names returned by common_pause_esc_text(). All samples are canonical4.
 * x/y are offsets from the original native run's top-left anchor. */
typedef struct CommonPauseNaturalRun {
 int x,y;unsigned width,height,pitch;
 const Uint8 *alpha,*roles; /* Separate planes, roles12..15 where alpha!=0. */
} CommonPauseNaturalRun;
typedef struct CommonPauseEscProvider {
 void *context;
 bool (*acquire)(void *);
 bool (*validate)(void *);
 bool (*get)(void *,unsigned,CommonPauseNaturalRun *);
 void (*release)(void *);
} CommonPauseEscProvider;
const char *common_pause_esc_text(unsigned index);
void common_pause_set_esc_provider(const CommonPauseEscProvider *);
void common_pause_set_directory(const char *);
/* Renderer seam: stage AFTER all texture-only overlays, BEFORE unlock. Commit
 * only after the corresponding RenderPresent. A new stage intentionally
 * retires the previous snapshot: this is a single-buffer conservative lease.
 * Failed staging/submission falls back classic until a later successful
 * stage/commit. Repeated commit, and discard with no pending stage, are no-ops;
 * repeated Present of the same texture must not restage or reset the lease.
 * density4/8, ARGB8888 opaque full canvas, source==VGAScreenSeg are mandatory. */
void common_pause_snapshot_stage(SDL_Surface *,const void *rgba,int pitch,int width,int height,unsigned density);
void common_pause_snapshot_commit(void);
void common_pause_snapshot_discard_candidate(void);
/* True source/level/video lifetime or non-gameplay submitted replacement. Not
 * ordinary HUD suspension, and not each gameplay simulation begin. */
void common_pause_snapshot_reset(void);
/* Add to render_mirror's top-level write fanout exactly once per actual write.
 * Rect observes actual clipped fill writes; equal-index writes are significant. */
void common_pause_pixel(SDL_Surface *,Uint8 *address,int style);
void common_pause_rect(SDL_Surface *,const SDL_Rect *);
/* Call before existing HUD suspend. P uses backup=NULL; ESC requires the real
 * VGAScreen2. Missing ESC family declines ESC only; P is independent. */
bool common_pause_begin(enum CommonPauseKind,SDL_Surface *screen,SDL_Surface *backup);
void common_pause_end(void);
bool common_pause_owns_display(void);
/* ESC startup: bracket the four existing JE_barShade calls with box0..3 and
 * primitive_end. Bracket the existing initial memcpy with save_before/after.
 * Each ordinary memcpy restore is similarly bracketed; never add a copy. */
void common_pause_box_begin(unsigned box);
void common_pause_primitive_end(void);
void common_pause_save_before(void);
void common_pause_save_after(void);
void common_pause_restore_before(void);
void common_pause_restore_after(void);
/* Immediately after native restore; parameter values are snapshots, not new
 * computations or setters. Detail/speed are the original zero-based indexes. */
void common_pause_frame_begin(unsigned selected,unsigned detail,unsigned speed,unsigned music_volume,unsigned effects_volume,bool music_disabled,bool effects_disabled);
void common_pause_bar_begin(unsigned row);
void common_pause_run_begin(enum CommonPauseRun,unsigned row,SDL_Surface *,int x,int y,const char *text,unsigned font,unsigned alignment,unsigned hue,int value);
void common_pause_run_end(void);
void common_pause_frame_end(void);
/* Bracket the actual native sprite routines, including every early return. */
void common_pause_glyph_begin(SDL_Surface *,int x,int y,unsigned font,unsigned id,enum CommonPauseGlyph,unsigned hue,int value);
void common_pause_glyph_end(void);
void common_pause_cursor_begin(void);
void common_pause_cursor_sprite_begin(SDL_Surface *,int x,int y,const void *,size_t,unsigned id);
void common_pause_cursor_sprite_end(void);
void common_pause_cursor_done(void);
void common_pause_cursor_erased(void);
/* Exactly one Present only when returning true. On false the existing caller
 * must execute its original fallback. Common owner retains native cursor. */
bool common_pause_present(SDL_Renderer *,SDL_Texture *reference,SDL_Surface *,const SDL_Rect *,bool foreign_owner);
void common_pause_release_texture(void);
void common_pause_invalidate(void);
void common_pause_table_reset(unsigned);
size_t common_pause_retained_bytes(void);
#endif
