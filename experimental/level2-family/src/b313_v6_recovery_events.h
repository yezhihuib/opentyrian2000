/* Every application SDL queue consumer uses this exact pre-return observer. */
#ifndef B313_V6_RECOVERY_EVENTS_H
#define B313_V6_RECOVERY_EVENTS_H
#include "SDL.h"
#include "b313_v6_recovery.h"
#include "b313_continuity.h"
#include "b313_family_input.h"
static inline int b313_recovery_poll_event(SDL_Event *event,unsigned tick,unsigned domain,uint64_t *token)
{
 (void)tick;(void)domain; /* Macro-disabled build retains plain SDL semantics. */
 if(token)*token=0;
 int found=SDL_PollEvent(event);
 if(found)b313_family_input_consumed(event?event->type:0);
 if(found)b313_recovery_external_event_at(tick,domain,event?event->type:0);
 if(found){uint64_t observed=bco_consumed(tick,domain,event?event->type:0);if(token)*token=observed;}
 return found;
}
#endif
