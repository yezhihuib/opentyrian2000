#ifndef B313_COMPONENT_TAIL_H
#define B313_COMPONENT_TAIL_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Historical metadata only; no borrowing or rendering permission. */
typedef struct {
 bool committed,live;
 unsigned event,slots[4],retired_lower_mask;
 uint64_t nonce,generation[4],epochs[4],birth_frame,lower_exit_frame[2];
 int birth_x[4],birth_y[4];
} B313ComponentTailGroup;
typedef struct {
 bool requested,session_enabled,frame_enabled,policy_failed;
 uint64_t session,frame,accepted_groups,lower_exits,upper_retirements;
 unsigned last_exit_slot;
 uint64_t last_exit_generation,last_exit_frame;
 int last_exit_y;
 B313ComponentTailGroup groups[2];
} B313ComponentTailStatus;
bool b313_family_observer_tail_enabled(void);
B313ComponentTailStatus b313_family_observer_tail_status(void);
/* Original dispatch hooks. Observe only; never alter the native actor/store. */
void b313_family_observer_native_store(SDL_Surface *,const void *,size_t,unsigned);
void b313_family_observer_native_pixel(SDL_Surface *,const void *,int);
void b313_family_observer_draw_end(SDL_Surface *,unsigned,int);
void b313_family_observer_bottom_exit(unsigned);
#endif
