/* Private frozen-path lease. Never native/HD eligibility. */
#ifndef NATIVE_WRITER_SCOPE_H
#define NATIVE_WRITER_SCOPE_H
#include "SDL.h"
#include <stdbool.h>
#include <stdint.h>
enum NwsStage { NWS_BEGIN=0,NWS_POST_EVENTS,NWS_PRE_INPUT,NWS_PRE_FILTER,NWS_PRE_SHOW,NWS_POST_SHOW,NWS_STAGE_COUNT };
enum NwsReason { NWS_CONTEXT=1u,NWS_ORDER=2u,NWS_SURFACE=4u,NWS_EVENT=8u,NWS_SCALER=16u,NWS_PRESENTER=32u,NWS_FALLBACK=64u,NWS_NATIVE=128u,NWS_IO=256u };
typedef struct {
 unsigned tick,episode,level,smoothies,processor;
 bool probe,demo,record,network,any_smoothies,super_wild,filter_active,filter_fade,filtration,transparent,player_end,skip;
 int special,filter,brightness;
 SDL_Surface *game,*output,*aux,*draw;
} NwsContext;
typedef struct {
 bool enabled,active,valid,sealed,reported,io_failed;
 uint64_t epoch;
 unsigned tick,reasons,stages,events,last_event,video_entries,scaler_begins,scaler_ends,mirror_success;
 bool scaler_pending,foreign_owner,mirror_owner,cursor_active,scaler_identity,original_source;
 NwsContext context[NWS_STAGE_COUNT];
} NwsStatus;
#if defined(NATIVE_WRITER_SCOPE_DIAGNOSTIC) && NATIVE_WRITER_SCOPE_DIAGNOSTIC
bool nws_enabled_for_tick(unsigned tick);
bool nws_observing(void);
void nws_checkpoint(unsigned stage,const NwsContext *context);
void nws_before_event(unsigned type);
void nws_video_entry(SDL_Surface *source,bool foreign_owner,bool mirror_owner);
void nws_before_scaler(SDL_Surface *source,SDL_Surface *actual,bool identity,bool format32,bool cursor_active);
void nws_after_scaler(void);
void nws_video_mirror_success(void);
void nws_fallback(void);
void nws_end(unsigned tick);
NwsStatus nws_status(void);
#else
#define nws_enabled_for_tick(...) false
#define nws_observing() false
#define nws_checkpoint(...) ((void)0)
#define nws_before_event(...) ((void)0)
#define nws_video_entry(...) ((void)0)
#define nws_before_scaler(...) ((void)0)
#define nws_after_scaler() ((void)0)
#define nws_video_mirror_success() ((void)0)
#define nws_fallback() ((void)0)
#define nws_end(...) ((void)0)
#endif
#endif
