#ifndef B313_FAMILY_INPUT_H
#define B313_FAMILY_INPUT_H
#include "SDL.h"

/* Independent SDL-consumption invalidation, not a script-event entry.
 * Safe before a session, between frames, and after finish. Never opens a
 * frame, grants a lease, changes game state, or reports script ORDER merely
 * because no frame is open. Implemented by the family source observer. */
void b313_family_observer_external_event(void);

/* The safety hook follows the existing diagnostic build switches: there is
 * deliberately no separate run-time switch that can disable it while the
 * family source/canvas mode is requested. Ordinary builds are no-ops. */
#if (defined(B313_FAMILY_OBSERVER_DIAGNOSTIC) && B313_FAMILY_OBSERVER_DIAGNOSTIC) || \
    (defined(B313_FAMILY_CANVAS_DIAGNOSTIC) && B313_FAMILY_CANVAS_DIAGNOSTIC)
/* Call exactly once for each successful SDL_PollEvent, before any legacy
 * observer, dispatch, discard or early return. All event types revoke; the
 * type is used only for additional renderer-reset cleanup, not admission. */
void b313_family_input_consumed(Uint32 type);
/* Called at the existing SDL_QUIT -> exit(0) branch. Revokes new state and
 * writes its final receipts; the caller retains all original exit behavior.
 * A discarded QUIT is still only a consumed event, not a request to exit. */
void b313_family_input_quit(void);
#else
static inline void b313_family_input_consumed(Uint32 type){(void)type;}
static inline void b313_family_input_quit(void){}
#endif
#endif
