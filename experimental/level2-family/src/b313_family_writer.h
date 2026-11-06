#ifndef B313_FAMILY_WRITER_H
#define B313_FAMILY_WRITER_H
#include "SDL.h"
#include "native_writer_observer.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifndef B313_FAMILY_CANVAS_DIAGNOSTIC
#define B313_FAMILY_CANVAS_DIAGNOSTIC 0
#endif

/* Independent synchronous native-write/callback pairing, not an NWO lease.
 * Never reads native pixels, writes pixels, allocates, performs IO, or grants
 * renderer/production permission. One serialized owner, as for the renderer. */
enum B313FamilyWriterReason {
 B313FW_FRAME=1u, B313FW_SURFACE=2u, B313FW_RANGE=4u,
 B313FW_WRITER=8u, B313FW_PENDING=16u, B313FW_DUPLICATE=32u,
 B313FW_FILL=64u, B313FW_TOKEN=128u, B313FW_CONTEXT=256u,
 B313FW_COPY=512u, B313FW_GAP=1024u, B313FW_UNKNOWN=2048u,
 B313FW_AFTER_SEAL=4096u, B313FW_OVERFLOW=8192u
};
typedef struct {
 bool diagnostic_enabled,active,valid,sealed;
 bool fill_pending,rect_pending,rect_active,crop_started;
 unsigned reasons,first_reason,copy_rows,pending_pixels;
 uint64_t frame,stores,store_bytes,pixels,fills,fill_rows_suppressed;
} B313FamilyWriterStatus;

#if B313_FAMILY_CANVAS_DIAGNOSTIC
bool b313_family_writer_begin(uint64_t frame,SDL_Surface *game,SDL_Surface *output);
void b313_family_writer_store(SDL_Surface *,const void *,size_t,enum NwoWriter);
void b313_family_writer_copy(SDL_Surface *,const void *,SDL_Surface *,const void *,size_t);
void b313_family_writer_gap(unsigned reason);
void b313_family_writer_unknown(SDL_Surface *,const void *,size_t,unsigned reason);
/* Wrap old before -> original SDL call -> old after inside this independent
 * before/after pair. The return is a by-value token, unrelated to NWO nonce. */
uint64_t b313_family_writer_fill_before(SDL_Surface *,const SDL_Rect *,enum NwoWriter);
void b313_family_writer_fill_after(uint64_t token,int original_result);
/* For a successful fill, rect_begin validates the original requested rect.
 * Consume precisely its clip intersection through pixel, then call rect_end.
 * It also accepts one exact unconsumed ordinary NWO_RECT_SPAN row.
 * Do not also pass the same fill through the old renderer's pixel loop. */
bool b313_family_writer_rect_begin(SDL_Surface *,const SDL_Rect *);
bool b313_family_writer_rect_end(SDL_Surface *);
bool b313_family_writer_pixel(SDL_Surface *,const void *);
bool b313_family_writer_draw_ready(uint64_t frame);
bool b313_family_writer_seal(uint64_t frame);
bool b313_family_writer_current(uint64_t frame);
/* Explicit lifecycle reset closes the frame. Fill-token serial is retained. */
void b313_family_writer_reset(void);
B313FamilyWriterStatus b313_family_writer_status(void);
#else
static inline bool b313_family_writer_begin(uint64_t f,SDL_Surface *g,SDL_Surface *o)
{(void)f;(void)g;(void)o;return false;}
static inline void b313_family_writer_store(SDL_Surface *s,const void *p,size_t n,enum NwoWriter w)
{(void)s;(void)p;(void)n;(void)w;}
static inline void b313_family_writer_copy(SDL_Surface *d,const void *p,SDL_Surface *s,const void *q,size_t n)
{(void)d;(void)p;(void)s;(void)q;(void)n;}
static inline void b313_family_writer_gap(unsigned r){(void)r;}
static inline void b313_family_writer_unknown(SDL_Surface *s,const void *p,size_t n,unsigned r)
{(void)s;(void)p;(void)n;(void)r;}
static inline uint64_t b313_family_writer_fill_before(SDL_Surface *s,const SDL_Rect *r,enum NwoWriter w)
{(void)s;(void)r;(void)w;return 0;}
static inline void b313_family_writer_fill_after(uint64_t t,int r){(void)t;(void)r;}
static inline bool b313_family_writer_rect_begin(SDL_Surface *s,const SDL_Rect *r)
{(void)s;(void)r;return false;}
static inline bool b313_family_writer_rect_end(SDL_Surface *s){(void)s;return false;}
static inline bool b313_family_writer_pixel(SDL_Surface *s,const void *p)
{(void)s;(void)p;return false;}
static inline bool b313_family_writer_draw_ready(uint64_t f){(void)f;return false;}
static inline bool b313_family_writer_seal(uint64_t f){(void)f;return false;}
static inline bool b313_family_writer_current(uint64_t f){(void)f;return false;}
static inline void b313_family_writer_reset(void){}
static inline B313FamilyWriterStatus b313_family_writer_status(void)
{const B313FamilyWriterStatus s={0};return s;}
#endif
#endif
