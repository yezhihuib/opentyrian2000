#ifndef B313_FAMILY_OBSERVER_H
#define B313_FAMILY_OBSERVER_H
#include "SDL.h"
#include "sprite.h"
#include "b313_family_plan.h"
#include "b313_component_tail.h"
#include "b313_family_cache.h"
#include <stdbool.h>
#include <stdint.h>
enum B313FamilyObserverReason {B313FO_CONFIG=1u,B313FO_SESSION=2u,B313FO_ORDER=4u,B313FO_ALLOC=8u,B313FO_RESOURCE=16u,B313FO_BIRTH=32u,B313FO_SOURCE=64u,B313FO_LIFETIME=128u,B313FO_CONTEXT=256u,B313FO_PLAN=512u,B313FO_CACHE=1024u,B313FO_EVENT=2048u,B313FO_IO=4096u};
typedef struct {
 bool requested,active,failed,frame_open,write_allowed,runtime_eligible;
 unsigned reasons,first_reason,first_slot,first_part;
 uint64_t session,frame,allocation_serial,generation[100],resource_epoch[4];
 uint64_t groups_committed,groups_retired,birth_rejected,target_calls,candidates,rejected,event_frames,abandoned_frames,source_hash_calls;
 uint64_t phase_calls[3],cycle_mask,pack_generation;
} B313FamilyObserverStatus;
/* Source qualification only. These identities are not renderer/canvas leases.
 * All calls have one serialized owner, as does the source cache. */
typedef struct {
 uint64_t session,frame,lifetime_serial,pack_generation,frame_generation;
} B313FamilyFrameIdentity;
typedef struct {
 uint64_t nonce;
 B313FamilyFrameIdentity frame;
 B313FamilyPlan plan;
 B313FamilyCacheTile tile; /* Borrowed const RGBA; never retain across a call. */
} B313FamilyDrawBorrow;
bool b313_family_observer_enabled(void);
void b313_family_observer_begin(void);
void b313_family_observer_finish(unsigned reason);
void b313_family_observer_frame_begin(void);
void b313_family_observer_frame_end(void);
void b313_family_observer_abandon(void);
void b313_family_observer_event(void);
/* Private terrain-only close witness. No old public layout is changed. */
void b313_family_observer_script_level_begin(char map,char shape);
void b313_family_observer_script_dispatch_begin(void);
void b313_family_observer_script_dispatch_end(void);
void b313_family_observer_script_event_before(unsigned event);
void b313_family_observer_script_event_after(unsigned event);
typedef struct {
 bool requested,session_enabled,frame_enabled,policy_failed,loaded,stream_broken;
 bool dispatch_open,event_inflight,attempted,close_seen,close_success,committed,current;
 bool pending,target_seen,consume_seen,birth_active,tail_call_active,terrain_valid,spawn_active;
 unsigned next_event,event_count,stage,event,time,close_cause,live_groups,memberships,close_calls,successful_closes;
 uint32_t used_groups;int data[6];
 uint64_t close_order,close_lifetime,allocation_serial,target_calls,pending_nonce,spawn_continuity_lifetime;
 uint64_t origin_target_calls,frame_origin_target_calls;
 B313FamilyFrameIdentity origin,frame_origin;
 const void *origin_surface,*origin_pixels,*origin_format;
 const void *frame_origin_surface,*frame_origin_pixels,*frame_origin_format;
 B313FamilyCacheWindow old_window,current_window;
} B313TerrainScriptReceipt;
/* Pure recomputed receipt only. No counters, state updates, IO, allocation,
 * cache queries with side effects, new borrow or permissions. Used only by
 * private normal-scene observation; production does not call this getter. */
B313TerrainScriptReceipt b313_family_observer_script_receipt(void);
/* Independent case31 policy only; existing receipt/layouts remain unchanged.
 * This getter is pure and grants no actor, cache or terrain authority. */
typedef struct {
 bool requested,session_enabled,frame_enabled,policy_failed;
} B313TerrainScript31PolicyReceipt;
B313TerrainScript31PolicyReceipt b313_family_observer_script31_policy_receipt(void);

void b313_family_observer_allocated(const void *object);
/* Only the main ordinary random-spawn call may bracket its native constructor.
 * This is a terrain-only continuity witness, never an actor/source grant. */
uint64_t b313_family_observer_terrain_spawn_begin(unsigned record,unsigned pool,int unique);
void b313_family_observer_terrain_spawn_commit(uint64_t token,unsigned slot1);
/* Pure diagnostic read; not a lease or permission to draw. */
uint64_t b313_family_observer_lifetime_serial(void);
void b313_family_observer_resource(unsigned pool,unsigned operation);
void b313_family_observer_resource_done(unsigned pool);
uint64_t b313_family_observer_birth_begin(unsigned type,unsigned pool_offset,unsigned link);
void b313_family_observer_birth_member(uint64_t group,unsigned component,unsigned slot1);
void b313_family_observer_birth_end(uint64_t group);
void b313_family_observer_draw(SDL_Surface *,unsigned slot,int x_offset,int y_offset,int part);
/* Consume the immediately preceding successful observer_draw, at most once.
 * x/y/base/part/filter and bank are the actual arguments of the original blit;
 * sheet_identity is the actual enemy.sprite2s pointer, not &bank (a copy).
 * Every attempt consumes pending state before validation, even on failure.
 * Every subsequent observer_draw (including non-target draws) and lifecycle
 * entry revokes pending state. Success does no IO, allocation, hashing, pixel
 * reading or diagnostic accounting, and does not grant write permission.
 * Use tile synchronously, never copy/save it for later drawing. The renderer
 * must independently validate its canvas lease and reject repeated nonces. */
bool b313_family_observer_consume(SDL_Surface *,unsigned slot,int x,int y,
                                 unsigned base,int part,int filter,
                                 const Sprite2_array *sheet_identity,
                                 Sprite2_array bank,B313FamilyDrawBorrow *out);
/* Read-only pre-finish check for the FIRST consumed identity of this frame.
 * Includes all groups consumed in the frame. Any intervening lifecycle entry
 * invalidates that identity; later draws cannot reopen an invalidated frame.
 * A false result after HD use requires the renderer's full native fallback.
 * Must run before observer_frame_end/finish, which close the cache window. */
bool b313_family_observer_frame_current(SDL_Surface *,const B313FamilyFrameIdentity *);
B313FamilyObserverStatus b313_family_observer_status(void);
#endif
