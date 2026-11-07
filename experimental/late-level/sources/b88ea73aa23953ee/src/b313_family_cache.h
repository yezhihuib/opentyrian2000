#ifndef B313_FAMILY_CACHE_H
#define B313_FAMILY_CACHE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Independent diagnostic source cache. Default build cannot load assets.
 * Enable only with B313_FAMILY_CACHE_DIAGNOSTIC=1 and an explicit prepare.
 * No existing prefix, catalogue activation, renderer, or writer is called.
 * All calls are serialized by one owner thread; not signal/thread safe. */
enum {
 B313FC_PHASES=3, B313FC_TILES_PER_PHASE=16,
 B313FC_PHASE_WIDTH=384, B313FC_PHASE_HEIGHT=448,
 B313FC_TILE_WIDTH=96, B313FC_TILE_HEIGHT=112,
 B313FC_TILE_STRIDE=96*4, B313FC_TILE_BYTES=96*112*4,
 B313FC_PHASE_BYTES=384*448*4,
 B313FC_PACK_BYTES=3*384*448*4
};
enum B313FamilyCacheReason {
 B313FC_DISABLED=1u, B313FC_INPUT=2u, B313FC_FRAME_OPEN=4u,
 B313FC_IO=8u, B313FC_LAYOUT=16u, B313FC_DIGEST=32u,
 B313FC_ALLOCATION=64u, B313FC_NOT_READY=128u,
 B313FC_WINDOW=256u, B313FC_GENERATION=512u,
 B313FC_REENTRY=1024u, B313FC_INVALIDATED=2048u, B313FC_CLOSED=4096u
};
typedef struct {
 uint64_t pack_generation,frame_generation;
} B313FamilyCacheWindow;
typedef struct {
 const unsigned char *rgba; /* Byte order R,G,B,A; never host-endian pixels. */
 size_t bytes,stride;
 unsigned phase,tile_index,width,height;
 uint64_t pack_generation,frame_generation;
} B313FamilyCacheTile;
typedef struct {
 bool diagnostic_enabled,ready,frame_open;
 /* Source availability is never write or production authorization. */
 bool write_allowed,runtime_eligible,production_enabled;
 unsigned phase_mask,reasons;
 uint64_t read_calls,hash_calls;
 uint64_t generation_serial,pack_generation,frame_generation;
 size_t bytes;
} B313FamilyCacheStatus;

/* Startup/closed-frame boundary only. Exactly three pinned legal BGRA files
 * commit together as 48 compact RGBA tiles. Every failure retires the old
 * cache and closes its borrow window; a partial phase set is never visible.
 * No file path is retained. Counters and serials survive close/invalidate. */
bool b313_family_cache_prepare(const char *const paths[B313FC_PHASES]);
bool b313_family_cache_frame_begin(B313FamilyCacheWindow *out);
bool b313_family_cache_frame_end(const B313FamilyCacheWindow *window);

/* Both generations must match the currently open window. tile_index is
 * row-major in a 4x4 phase grid, not actor/component order:
 *   (plan.source_y_hd / 112) * 4 + plan.source_x_hd / 96.
 * Failed borrows zero out and return false without replacing a ready pack.
 * begin/end/borrow/current perform no IO, allocation, or hashing.
 * Pointers must not be used after end, invalidate, close, or prepare.
 * Check current immediately before dereferencing a retained descriptor.
 * Copying a descriptor does not extend its lifetime or confer authority. */
bool b313_family_cache_borrow(const B313FamilyCacheWindow *window,
                            unsigned phase,unsigned tile_index,
                            B313FamilyCacheTile *out);
bool b313_family_cache_tile_current(const B313FamilyCacheTile *tile);
void b313_family_cache_invalidate(void);
void b313_family_cache_close(void);
B313FamilyCacheStatus b313_family_cache_status(void);
#endif
