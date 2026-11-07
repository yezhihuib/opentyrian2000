#ifndef NATIVE_WRITER_OBSERVER_H
#define NATIVE_WRITER_OBSERVER_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "SDL.h"

/* Private diagnostic only. It has no renderer/admission or pixel-write API. */
enum NwoWriter {
 NWO_SPRITE2=1,NWO_SPRITE2_CLIP,NWO_SPRITE2_BLEND,NWO_SPRITE2_DARK,
 NWO_SPRITE2_FILTER,NWO_SPRITE2_FILTER_CLIP,NWO_RECT_SPAN,NWO_RECT_SIDE,
 NWO_SPRITE1,NWO_SPRITE1_BLEND,NWO_SPRITE1_HV_UNSAFE,NWO_SPRITE1_HV,
 NWO_SPRITE1_HV_BLEND,NWO_SPRITE1_DARK,NWO_TERRAIN,NWO_TERRAIN_BLEND,
 NWO_STARFIELD,NWO_SUPERPIXEL,
 NWO_SDL_BACKGROUND_CLEAR,NWO_SDL_VGA_FILL,NWO_SDL_VIDEO_CLEAR,
 NWO_VGA_PIXEL,NWO_VGA_SHADE,NWO_VGA_BRIGHT,
 NWO_WRITER_LIMIT
};
enum NwoReason {
 NWO_PARTIAL_SCOPE=1u,NWO_BAD_SURFACE=2u,NWO_BAD_RANGE=4u,
 NWO_OVERFLOW=8u,NWO_BAD_WRITER=16u,NWO_NONORDINARY=32u,NWO_IO_ERROR=64u,
 NWO_STALE_FRAME=128u,NWO_OVERLAPPING_STORAGE=256u,
 NWO_COVERAGE_GAP=512u,NWO_UNKNOWN_WRITE=1024u
};
enum NwoGap {
 NWO_GAP_UNREGISTERED=1,NWO_GAP_VGA_PIXEL,NWO_GAP_VGA_FILL,NWO_GAP_VGA_SHADE,
 NWO_GAP_BRIGHT_RECT,NWO_GAP_BACKGROUND_CLEAR,NWO_GAP_BRIGHTNESS,NWO_GAP_HUE_FILTER,
 NWO_GAP_DARKEN,NWO_GAP_LAVA,NWO_GAP_WATER,NWO_GAP_ICED_BLUR,NWO_GAP_BLUR,
 NWO_GAP_SPECIAL_OUTPUT,NWO_GAP_PRESENT_SKIPPED,NWO_GAP_SMOOTHIE,NWO_GAP_WHOA,
 NWO_GAP_SCENE_TRANSITION,NWO_GAP_UI_TRANSITION,
 NWO_GAP_SDL_FILL_ERROR,NWO_GAP_SDL_FILL_CONTEXT,NWO_GAP_SDL_FILL_OVERFLOW,
 NWO_GAP_FILL_MISSING_AFTER,NWO_GAP_FILL_REENTRANT,NWO_GAP_FILL_TOKEN,
 NWO_GAP_FILL_NONCE_OVERFLOW,NWO_GAP_HELP_ENTRY,NWO_GAP_F11_CONTEXT,
 NWO_GAP_PALETTE_MUTATION,NWO_GAP_SKIPPED_END,NWO_GAP_EARLY_SCENE_JUMP,
 NWO_GAP_SCENE_BEGIN,NWO_GAP_EARLY_FRAME_EXIT,NWO_GAP_LIMIT
};
typedef struct {
 bool active,valid,structural_valid,coverage_gate_ok,ledger_complete,eligible;
 unsigned uncovered_mask,first_gap;
 uint64_t gap_count,first_gap_after_sequence,unknown_write_calls,unknown_ranges_verified,unknown_ranges_unverified;
 uint64_t gap_counts[NWO_GAP_LIMIT];
 uint64_t fill_calls,fill_returns_ok,fill_returns_error,fill_observed_empty,fill_observed_rows;
 bool fill_pending;
 unsigned fill_missing_tick;
 uint64_t fill_registered,fill_consumed,fill_missing_after,fill_missing_on_begin,fill_missing_on_end;
 uint64_t fill_pending_nonce,fill_missing_epoch,fill_missing_nonce;
 bool boundary_revoked,boundary_inherited;
 unsigned boundary_reason,boundary_origin_tick;
 uint64_t frame_epoch,boundary_origin_epoch,boundary_origin_sequence;
 unsigned tick,reasons;
 uint64_t sequence,stores,stored_bytes,copies,copied_bytes,trace_hash;
 uint64_t writer_counts[NWO_WRITER_LIMIT];
} NwoStatus;
typedef struct {
 bool started,pending,completed;
 unsigned tick;
 uint64_t epoch,sequence,nonce;
 SDL_Surface *surface;
 void *pixels;
 SDL_PixelFormat *format;
 SDL_Rect clip,effective;
 int w,h,pitch,locked;
 Uint32 flags;
 enum NwoWriter writer;
} NwoFillCall;
uint64_t nwo_fill_before(NwoFillCall *call,SDL_Surface *surface,const SDL_Rect *rect,enum NwoWriter writer);
/* Synchronous, single pending slot. Preserve the returned token by value. */
void nwo_fill_after(NwoFillCall *call,uint64_t nonce,int original_result);
void nwo_begin_frame(unsigned tick,bool requested,SDL_Surface *game,SDL_Surface *output,SDL_Surface *aux);
void nwo_observe_store(SDL_Surface *s,const void *address,size_t bytes,enum NwoWriter writer);
void nwo_observe_copy(SDL_Surface *dst,const void *dst_address,SDL_Surface *src,const void *src_address,size_t bytes);
void nwo_invalidate(unsigned reason);
void nwo_coverage_gap(enum NwoGap reason);
void nwo_unknown_write(SDL_Surface *s,const void *address,size_t bytes,enum NwoGap reason);
void nwo_end_frame(unsigned tick);
/* Fail closed and persist before an explicitly unsupported context transition. */
void nwo_revoke_frame(enum NwoGap reason);
#ifdef NWO_TESTING
void nwo_test_begin(unsigned tick,SDL_Surface *game,SDL_Surface *output,SDL_Surface *aux);
NwoStatus nwo_test_status(void);
uint64_t nwo_test_last_event(unsigned slot,size_t offset);
unsigned nwo_test_last_writer(unsigned slot,size_t offset);
void nwo_test_set_sequence(uint64_t sequence);
void nwo_test_set_fill_nonce(uint64_t nonce);
#endif
#endif
