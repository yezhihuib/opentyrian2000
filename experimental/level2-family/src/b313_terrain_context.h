#ifndef B313_TERRAIN_CONTEXT_H
#define B313_TERRAIN_CONTEXT_H
#include "b313_family_observer.h"
#include <stddef.h>
/* Separate, source-only terrain qualification. This is never an actor draw
 * borrow or permission to write. The renderer must independently prove its
 * writer, terrain, canvas, output and locked-texture contracts.
 * Serialized owner, as for the existing observer and source cache. */
typedef struct {
 B313FamilyFrameIdentity frame;
 SDL_Surface *surface;
 const void *pixels;
 const SDL_PixelFormat *format;
 uint64_t target_calls;
} B313TerrainContext;
/* Exports only the immutable origin saved by the actual frame_begin. Never
 * refreshes/reissues identity after a lifecycle boundary. Failure clears out.
 * Only family_begin may take this token, once and before its terrain pass. */
bool b313_family_observer_terrain_context_begin(SDL_Surface *,B313TerrainContext *out);
/* Pure currentness check: no state change, IO, allocation, source hashing,
 * statistics or cache borrow. Every call repeats the conservative 100-slot
 * census. Existing frame_current/used-group actor authority is independent. */
bool b313_family_observer_terrain_context_current(SDL_Surface *,const B313TerrainContext *);
/* Cumulative diagnostics only: these counts are never a readiness/support
 * lease. No existing observer/canvas/ground ABI is enlarged. */
typedef struct {
 bool requested;
 uint64_t frames,begin_grants,accepted_frames,presents;
} B313TerrainContinuityStatus;
/* Independent pure counterpart of writer_current for read-only receipts.
 * It never calls the old mutating context/idle/fail helpers. */
bool b313_family_writer_peek_current(uint64_t frame);
/* Exactly 64000 bytes of 0/1 final support, in source coordinates. Only a
 * still-current, ready TERRAIN admission may export it. All 64 actual HD
 * owners of each supported cropped cell must survive. Failure leaves out
 * untouched. No allocation, IO, observer/writer changes or write permission. */
#ifndef RENDER_MIRROR_DISABLED
B313TerrainContinuityStatus render_mirror_terrain_continuity_status(void);
bool render_mirror_terrain_support(uint8_t *out,size_t bytes);
#else
static inline B313TerrainContinuityStatus render_mirror_terrain_continuity_status(void)
{const B313TerrainContinuityStatus status={0};return status;}
static inline bool render_mirror_terrain_support(uint8_t *out,size_t bytes)
{(void)out;(void)bytes;return false;}
#endif
#endif
