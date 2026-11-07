#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
#include "native_writer_observer.h"
#include "b313_family_writer.h"
#include "b313_component_tail.h"
#include "persistent_hud_family.h"
#include "building313_final_proof.h"
#include "building313_precommit.h"
#include "native_writer_lineage.h"
#include "old_hd_sample_observer.h"
#include "native_writer_scope.h"
#if defined(NATIVE_WRITER_SCOPE_DIAGNOSTIC) && NATIVE_WRITER_SCOPE_DIAGNOSTIC
#include "building313_identity.h"
#include <inttypes.h>
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

/* Bounded physical-byte ledger, including row padding. Never a pixel buffer. */
#define NWO_CAPACITY 65536u
#define NWO_SURFACES 3u
#define NWO_HASH_START UINT64_C(14695981039346656037)
#define NWO_HASH_PRIME UINT64_C(1099511628211)
#ifndef NATIVE_WRITER_OBSERVER_DIAGNOSTIC
#define NATIVE_WRITER_OBSERVER_DIAGNOSTIC 0
#endif
struct NwoSurface {
 SDL_Surface *surface;
 void *pixels;
 SDL_PixelFormat *format;
 int w,h,pitch;
 Uint32 format_code;
 Uint8 bpp,bytes_per_pixel;
 size_t bytes;
 uint64_t last_event[NWO_CAPACITY];
 unsigned char last_writer[NWO_CAPACITY];
};
static struct NwoSurface surfaces[NWO_SURFACES];
static NwoStatus state,revoked_state;
static uint64_t observer_epoch,fill_nonce;
/* Never dereference ticket_address. Its identity is compared before after()
 * reads the caller's live ticket; all observation data is a value snapshot. */
static struct {
 bool active;
 uintptr_t ticket_address;
 NwoFillCall snapshot;
} pending_fill;
struct NwoMissedFill { bool present; unsigned tick; uint64_t epoch,nonce; };
static const char *const gap_names[NWO_GAP_LIMIT]={
 "none","unregistered","vga-pixel","vga-fill","vga-shade","bright-rectangle",
 "background-sdl-clear","brightness","hue-filter","darken","lava","water",
 "iced-blur","blur","special-output","present-skipped","smoothie",
 "whoa","scene-transition","ui-transition","sdl-fill-error","sdl-fill-context","sdl-fill-overflow",
 "fill-missing-after","fill-reentrant","fill-token-mismatch","fill-nonce-overflow",
 "help-entry","f11-context","palette-mutation","skipped-end","early-scene-jump",
 "scene-begin","early-frame-exit"
};

/* Bounded call-to-event intervals. last_event remains the sole per-byte lineage. */
#define NWL_CALL_CAPACITY 128u
struct NwlCall {NwlIdentity id;uint64_t first,last;unsigned stores,unique;unsigned char seen[21];bool closed;};
static NwlStatus lineage;
static struct NwlCall lineage_calls[NWL_CALL_CAPACITY];
static unsigned lineage_pending_index;
static void lineage_fail(unsigned reason){if(lineage.enabled){lineage.valid=false;lineage.reasons|=reason;}}
void nwl_discard(unsigned reason){lineage_fail(reason);lineage.sealed=false;lineage.pending=false;}
static bool lineage_enabled(void)
{
#if defined(BUILDING313_LINEAGE_DIAGNOSTIC) && BUILDING313_LINEAGE_DIAGNOSTIC
 const char *v=getenv("BUILDING313_LINEAGE_ENABLE");return v&&strcmp(v,"1")==0;
#else
 return false;
#endif
}
static bool lineage_identity_equal(const NwlIdentity *a,const NwlIdentity *b)
{
 return a->scene==b->scene&&a->frame==b->frame&&a->group==b->group&&a->call==b->call&&a->generation==b->generation&&a->tick==b->tick&&a->slot==b->slot&&a->type==b->type&&a->part==b->part&&a->base==b->base&&a->x==b->x&&a->y==b->y;
}
uint64_t nwl_open(uint64_t scene,uint64_t frame,unsigned tick)
{
 if(lineage.enabled&&lineage.lease==state.frame_epoch&&lineage.tick==tick){lineage_fail(NWL_CONTEXT);return 0;}
 memset(&lineage,0,sizeof(lineage));memset(lineage_calls,0,sizeof(lineage_calls));
 if(!lineage_enabled())return 0;
 lineage.enabled=true;lineage.scene=scene;lineage.frame=frame;lineage.tick=tick;
 if(!scene||!frame||tick!=b313_slice_tick()||!state.active||!state.valid||!state.structural_valid||state.tick!=tick||pending_fill.active){lineage_fail(NWL_CONTEXT);return 0;}
 lineage.lease=state.frame_epoch;lineage.valid=true;return lineage.lease;
}
static bool lineage_open_valid(uint64_t lease)
{
 return lineage.enabled&&lineage.valid&&!lineage.sealed&&state.active&&state.valid&&state.structural_valid&&lease&&lease==lineage.lease&&lease==state.frame_epoch&&state.tick==lineage.tick;
}
NwlToken nwl_call_begin(uint64_t lease,const NwlIdentity *id,SDL_Surface *surface)
{
 const NwlToken none={0,0};
 if(!lineage.enabled)return none;
 if(!lineage_open_valid(lease)||!id||pending_fill.active){lineage_fail(NWL_CONTEXT);return none;}
 if(lineage.pending){lineage_fail(NWL_PENDING);return none;}
 if(!id->group||!id->call||!id->generation||id->scene!=lineage.scene||id->frame!=lineage.frame||id->tick!=lineage.tick||id->slot>=100||id->type<313||id->type>316||(id->part!=0&&id->part!=1&&id->part!=19&&id->part!=20)){lineage_fail(NWL_IDENTITY);return none;}
 if(surface!=surfaces[0].surface||id->x<0||id->y<0||(int64_t)id->x+12>surfaces[0].w||(int64_t)id->y+14>surfaces[0].h){lineage_fail(NWL_RANGE);return none;}
 if(lineage.calls>=NWL_CALL_CAPACITY||state.sequence==UINT64_MAX){lineage_fail(NWL_OVERFLOW);return none;}
 for(unsigned i=0;i<lineage.calls;i++)if(lineage_calls[i].id.call==id->call||!lineage_calls[i].closed||lineage_calls[i].last>=state.sequence+1){lineage_fail(NWL_SEQUENCE);return none;}
 unsigned i=lineage.calls++;struct NwlCall *c=&lineage_calls[i];memset(c,0,sizeof(*c));c->id=*id;c->first=state.sequence+1;
 lineage.pending=true;lineage_pending_index=i;
 ohs_native_call_begin(lease,id,surface);
 return (NwlToken){lease,id->call};
}
static void lineage_store(unsigned slot,size_t offset,size_t bytes,enum NwoWriter writer)
{
 if(!lineage.enabled||!lineage.valid)return;
 if(lineage.sealed){lineage_fail(NWL_AFTER_SEAL);return;}
 if(!lineage.pending)return; /* Foreign writes still replace the ordinary last_event. */
 struct NwlCall *c=&lineage_calls[lineage_pending_index];
 if(slot!=0||bytes!=1||writer!=NWO_SPRITE2){lineage_fail(NWL_WRITER);return;}
 if(state.sequence!=c->first+c->stores||c->stores>=168){lineage_fail(NWL_SEQUENCE);return;}
 size_t row=offset/(size_t)surfaces[0].pitch,col=offset%(size_t)surfaces[0].pitch;
 if(row<(unsigned)c->id.y||row>=(unsigned)c->id.y+14||col<(unsigned)c->id.x||col>=(unsigned)c->id.x+12){lineage_fail(NWL_RANGE);return;}
 unsigned cell=(unsigned)(row-c->id.y)*12+(unsigned)(col-c->id.x),mask=1u<<(cell%8);
 if(c->seen[cell/8]&mask){lineage_fail(NWL_DUPLICATE);return;}
 if(cell!=c->stores){lineage_fail(NWL_SEQUENCE);return;}
 c->seen[cell/8]|=(unsigned char)mask;c->unique++;c->stores++;c->last=state.sequence;
 ohs_native_event(lineage.lease,&c->id,state.sequence,offset);
}
static void lineage_copy(unsigned source,size_t from,unsigned dest,size_t to,size_t bytes)
{
 if(!lineage.enabled||!lineage.valid)return;
 if(lineage.pending){lineage_fail(NWL_PENDING|NWL_COPY);return;}
 unsigned row=lineage.copy_rows;
 if(source!=0||dest!=1||row>=184||bytes!=264||from!=(size_t)row*surfaces[0].pitch+24||to!=(size_t)row*surfaces[1].pitch||surfaces[0].w<288||surfaces[1].w<264||surfaces[0].h<184||surfaces[1].h<184){lineage_fail(NWL_COPY);return;}
 lineage.copy_rows++;
}
void nwl_call_end(NwlToken token)
{
 if(!lineage.enabled)return;
 if(!token.lease&&!token.call){if(lineage.pending)lineage_fail(NWL_PENDING);return;}
 if(!lineage_open_valid(token.lease)||!lineage.pending){lineage_fail(NWL_CONTEXT|NWL_PENDING);return;}
 struct NwlCall *c=&lineage_calls[lineage_pending_index];
 if(token.call!=c->id.call){lineage_fail(NWL_IDENTITY);return;}
 lineage.pending=false;
 if(pending_fill.active||c->stores!=168||c->unique!=168||c->last<c->first||c->last-c->first+1!=168||state.sequence!=c->last){lineage_fail(NWL_PARTIAL|NWL_SEQUENCE);return;}
 c->closed=true;
 ohs_native_call_end(token,c->first,c->last);
}
static void lineage_seal(unsigned tick)
{
 if(!lineage.enabled)return;
 if(!state.valid||!state.structural_valid||state.gap_count||pending_fill.active||lineage.pending||tick!=lineage.tick||lineage.lease!=state.frame_epoch||lineage.copy_rows!=184)lineage_fail(NWL_NATIVE_INVALID|NWL_PARTIAL);
 for(unsigned i=0;i<lineage.calls;i++)if(!lineage_calls[i].closed)lineage_fail(NWL_PENDING);
 lineage.sealed=true;
}
NwlStatus nwl_status(void){return lineage;}
NwlResult nwl_query(uint64_t lease,const NwlIdentity *id)
{
 NwlResult result={0};
 if(!lineage.enabled||!lineage.valid||!lineage.sealed||lineage.pending||!id||state.active||!state.valid||!state.structural_valid||!lease||lease!=lineage.lease||lease!=state.frame_epoch||state.tick!=lineage.tick)return result;
 const struct NwlCall *c=NULL;
 for(unsigned i=0;i<lineage.calls;i++)if(lineage_identity_equal(id,&lineage_calls[i].id)){c=&lineage_calls[i];break;}
 if(!c||!c->closed)return result;
 result.available=true;result.completed=true;result.first_event=c->first;result.last_event=c->last;result.stores=c->stores;result.unique_cells=c->unique;
 /* No SDL or native-buffer read. Geometry is the sealed validated value copy. */
 for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
  size_t source=(size_t)(id->y+(int)y)*surfaces[0].pitch+(unsigned)id->x+x;
  uint64_t expected=c->first+y*12+x;
  uint64_t e=surfaces[0].last_event[source];bool owned=e==expected&&surfaces[0].last_writer[source]==NWO_SPRITE2;
  result.source_owned+=owned;if(y==13)result.last_row_source_owned+=owned;
  if(id->x>=24&&(int64_t)id->x+12<=288&&(int64_t)id->y+14<=184){
   size_t output=(size_t)(id->y+(int)y)*surfaces[1].pitch+(unsigned)(id->x-24)+x;
   e=surfaces[1].last_event[output];owned=e==expected&&surfaces[1].last_writer[output]==NWO_SPRITE2;
   result.output_owned+=owned;if(y==13)result.last_row_output_owned+=owned;
  }
 }
 return result;
}

static void mix(uint64_t v)
{
 for(unsigned i=0;i<8;i++){state.trace_hash^=(unsigned char)(v>>(i*8));state.trace_hash*=NWO_HASH_PRIME;}
}
void nwo_invalidate(unsigned reason)
{
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(!state.active)return;
 lineage_fail(NWL_NATIVE_INVALID);
 state.valid=false;state.reasons|=reason;
 if(reason&~(NWO_COVERAGE_GAP|NWO_UNKNOWN_WRITE))state.structural_valid=false;
 /* Deliberately permanent in this prototype, including when valid=true. */
 state.ledger_complete=false;state.eligible=false;
}
static bool geometry(SDL_Surface *s,size_t *bytes)
{
 if(!s||!s->pixels||!s->format||s->w<=0||s->h<=0||s->pitch<s->w||s->pitch<=0||
    s->format->format!=SDL_PIXELFORMAT_INDEX8||s->format->BitsPerPixel!=8||s->format->BytesPerPixel!=1)return false;
 if((size_t)s->h>NWO_CAPACITY/(size_t)s->pitch)return false;
 *bytes=(size_t)s->pitch*(size_t)s->h;
 if((uintptr_t)s->pixels>UINTPTR_MAX-*bytes)return false;
 return true;
}

static bool fill_counter(uint64_t *value)
{
 if(*value==UINT64_MAX){nwo_invalidate(NWO_OVERFLOW);return false;}
 ++*value;return true;
}
/* End/rollover checks consult only owned values, never a saved stack pointer. */
static struct NwoMissedFill retire_pending(bool at_begin)
{
 struct NwoMissedFill missed={false,0,0,0};
 if(!pending_fill.active)return missed;
 missed=(struct NwoMissedFill){true,pending_fill.snapshot.tick,pending_fill.snapshot.epoch,pending_fill.snapshot.nonce};
 pending_fill.active=false;state.fill_pending=false;state.fill_pending_nonce=0;
 state.fill_missing_tick=missed.tick;state.fill_missing_epoch=missed.epoch;state.fill_missing_nonce=missed.nonce;
 fill_counter(&state.fill_missing_after);
 fill_counter(at_begin?&state.fill_missing_on_begin:&state.fill_missing_on_end);
 nwo_coverage_gap(NWO_GAP_FILL_MISSING_AFTER);
 return missed;
}
static struct NwoMissedFill retire_before_begin(void)
{
 struct NwoMissedFill missed=retire_pending(true);
 /* Persist the old failed lease even if the next frame is not enabled.
  * Its invalid state prevents end_frame from reading any pixel buffer. */
 if(missed.present&&state.active)nwo_end_frame(state.tick);
 return missed;
}

#if NATIVE_WRITER_OBSERVER_DIAGNOSTIC || defined(NWO_TESTING)
static void begin(unsigned tick,SDL_Surface *game,SDL_Surface *output,SDL_Surface *aux)
{
 struct NwoMissedFill missed=retire_before_begin();
 nwl_discard(NWL_STALE);
 memset(&state,0,sizeof(state));state.active=true;state.valid=true;state.structural_valid=true;state.tick=tick;
 /* Fixed uncovered classes: SDL clears, other primitives, raw UI/loader copies,
  * palette/lifecycle transitions and final non-native coverage. Never zero. */
 state.uncovered_mask=31u;state.coverage_gate_ok=false;
 state.reasons=NWO_PARTIAL_SCOPE;state.trace_hash=NWO_HASH_START;
 if(observer_epoch==UINT64_MAX){nwo_invalidate(NWO_OVERFLOW);return;}
 ++observer_epoch;state.frame_epoch=observer_epoch;
 bool inherited=false;
 if(revoked_state.boundary_revoked&&revoked_state.tick==tick){
  /* A backedge may reuse game_probe_tick. It gets a new epoch, but may not
   * erase this tick's failed boundary or reacquire a valid observation. */
  state.boundary_revoked=true;state.boundary_inherited=true;
  state.boundary_reason=revoked_state.boundary_reason;
  state.boundary_origin_tick=revoked_state.boundary_origin_tick;
  state.boundary_origin_epoch=revoked_state.boundary_origin_epoch;
  state.boundary_origin_sequence=revoked_state.boundary_origin_sequence;
  state.fill_missing_after=revoked_state.fill_missing_after;
  state.fill_missing_on_begin=revoked_state.fill_missing_on_begin;
  state.fill_missing_on_end=revoked_state.fill_missing_on_end;
  state.fill_missing_tick=revoked_state.fill_missing_tick;
  state.fill_missing_epoch=revoked_state.fill_missing_epoch;
  state.fill_missing_nonce=revoked_state.fill_missing_nonce;
  nwo_coverage_gap((enum NwoGap)state.boundary_reason);inherited=true;
 }
 if(missed.present){
  fill_counter(&state.fill_missing_after);fill_counter(&state.fill_missing_on_begin);
  state.fill_missing_tick=missed.tick;state.fill_missing_epoch=missed.epoch;state.fill_missing_nonce=missed.nonce;
  nwo_coverage_gap(NWO_GAP_FILL_MISSING_AFTER);inherited=true;
 }
 if(inherited){state.structural_valid=false;return;} /* New surfaces were not validated or read. */
 SDL_Surface *input[NWO_SURFACES]={game,output,aux};
 for(unsigned i=0;i<NWO_SURFACES;i++){
  size_t bytes=0;struct NwoSurface *v=&surfaces[i];
  memset(v,0,sizeof(*v));
  if(!geometry(input[i],&bytes)){nwo_invalidate(NWO_BAD_SURFACE);return;}
  SDL_Surface *s=input[i];v->surface=s;v->pixels=s->pixels;v->format=s->format;
  v->w=s->w;v->h=s->h;v->pitch=s->pitch;v->format_code=s->format->format;
  v->bpp=s->format->BitsPerPixel;v->bytes_per_pixel=s->format->BytesPerPixel;v->bytes=bytes;
  for(unsigned j=0;j<i;j++){
   uintptr_t a=(uintptr_t)v->pixels,b=(uintptr_t)surfaces[j].pixels;
   if(a<b+surfaces[j].bytes&&b<a+v->bytes){nwo_invalidate(NWO_OVERLAPPING_STORAGE);return;}
  }
 }
}

#endif
void nwo_begin_frame(unsigned tick,bool requested,SDL_Surface *game,SDL_Surface *output,SDL_Surface *aux)
{
 /* Tick is the game_probe tick, not mirror_logic_tick. Never enables new HD. */
#if NATIVE_WRITER_OBSERVER_DIAGNOSTIC
 const char *enabled=getenv("NATIVE_WRITER_OBSERVER_ENABLE");
 if(requested&&tick==b313_slice_tick()&&enabled&&!strcmp(enabled,"1")){begin(tick,game,output,aux);return;}
#else
 (void)tick;(void)requested;(void)game;(void)output;(void)aux;
#endif
 (void)retire_before_begin();nwl_discard(NWL_STALE);state.active=false;
}
static int locate(SDL_Surface *s,const void *address,size_t bytes,size_t *offset)
{
 for(unsigned i=0;i<NWO_SURFACES;i++)if(s==surfaces[i].surface){
  struct NwoSurface *v=&surfaces[i];size_t now=0;
  if(!geometry(s,&now)||s->pixels!=v->pixels||s->format!=v->format||s->w!=v->w||s->h!=v->h||s->pitch!=v->pitch||
     s->format->format!=v->format_code||s->format->BitsPerPixel!=v->bpp||s->format->BytesPerPixel!=v->bytes_per_pixel||now!=v->bytes){nwo_invalidate(NWO_BAD_SURFACE);return -1;}
  uintptr_t a=(uintptr_t)address,b=(uintptr_t)v->pixels;
  if(a<b||a-b>v->bytes||bytes>v->bytes-(size_t)(a-b)){nwo_invalidate(NWO_BAD_RANGE);return -1;}
  *offset=(size_t)(a-b);return (int)i;
 }
 nwo_invalidate(NWO_BAD_SURFACE);return -1;
}

void nwo_coverage_gap(enum NwoGap reason)
{
 b313_family_writer_gap((unsigned)reason);
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(!state.active)return;
 if(reason<=0||reason>=NWO_GAP_LIMIT)reason=NWO_GAP_UNREGISTERED;
 if(state.gap_count==UINT64_MAX||state.gap_counts[reason]==UINT64_MAX){nwo_invalidate(NWO_OVERFLOW);return;}
 if(!state.gap_count){state.first_gap=(unsigned)reason;state.first_gap_after_sequence=state.sequence;}
 ++state.gap_count;++state.gap_counts[reason];
 mix(3);mix((unsigned)reason);mix(state.sequence);
 /* Fail closed on the first explicit gap. Later calls collect gap statistics
  * only; no store/copy event may resume this observation lease. */
 nwo_invalidate(NWO_COVERAGE_GAP);
}
void nwo_unknown_write(SDL_Surface *s,const void *address,size_t bytes,enum NwoGap reason)
{
 render_mirror_persistent_unknown(s,address,bytes);
 b313_family_writer_unknown(s,address,bytes,(unsigned)reason);
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(!state.active)return;
 if(state.unknown_write_calls==UINT64_MAX){nwo_invalidate(NWO_OVERFLOW);return;}
 ++state.unknown_write_calls;size_t offset=0;
 bool known=state.structural_valid&&address&&bytes&&locate(s,address,bytes,&offset)>=0;
 if(known){if(state.unknown_ranges_verified==UINT64_MAX)nwo_invalidate(NWO_OVERFLOW);else ++state.unknown_ranges_verified;}
 else {if(state.unknown_ranges_unverified==UINT64_MAX)nwo_invalidate(NWO_OVERFLOW);else ++state.unknown_ranges_unverified;nwo_invalidate(NWO_BAD_RANGE);}
 nwo_coverage_gap(reason);nwo_invalidate(NWO_UNKNOWN_WRITE);
}

static bool next_event(void)
{
 if(state.sequence==UINT64_MAX){nwo_invalidate(NWO_OVERFLOW);return false;}
 ++state.sequence;return true;
}
void nwo_observe_store(SDL_Surface *s,const void *address,size_t bytes,enum NwoWriter writer)
{
 render_mirror_persistent_store(s,address,bytes,(unsigned)writer);
 b313_family_observer_native_store(s,address,bytes,(unsigned)writer);
 b313_family_writer_store(s,address,bytes,writer);
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(!state.active||!state.valid||!bytes)return;
 if(writer<=0||writer>=NWO_WRITER_LIMIT){nwo_invalidate(NWO_BAD_WRITER);return;}
 size_t offset=0;int slot=locate(s,address,bytes,&offset);if(slot<0)return;
 if(state.stores==UINT64_MAX||bytes>UINT64_MAX-state.stored_bytes||state.writer_counts[writer]==UINT64_MAX){nwo_invalidate(NWO_OVERFLOW);return;}
 if(!next_event())return;
 ++state.stores;state.stored_bytes+=bytes;++state.writer_counts[writer];
 mix(1);mix(state.sequence);mix((unsigned)slot);mix(offset);mix(bytes);mix((unsigned)writer);
 for(size_t i=0;i<bytes;i++){surfaces[slot].last_event[offset+i]=state.sequence;surfaces[slot].last_writer[offset+i]=(unsigned char)writer;}
 lineage_store((unsigned)slot,offset,bytes,writer);
}
void nwo_observe_copy(SDL_Surface *dst,const void *dst_address,SDL_Surface *src,const void *src_address,size_t bytes)
{
 b313_family_writer_copy(dst,dst_address,src,src_address,bytes);
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(!state.active||!state.valid||!bytes)return;
 size_t to=0,from=0;int d=locate(dst,dst_address,bytes,&to),s=locate(src,src_address,bytes,&from);
 if(d<0||s<0)return;
 /* Only independently allocated game->output storage is in this contract. */
 if(s!=0||d!=1){nwo_invalidate(NWO_NONORDINARY);return;}
 if(state.copies==UINT64_MAX||bytes>UINT64_MAX-state.copied_bytes){nwo_invalidate(NWO_OVERFLOW);return;}
 if(!next_event())return;
 ++state.copies;state.copied_bytes+=bytes;
 lineage_copy((unsigned)s,from,(unsigned)d,to,bytes);
 mix(2);mix(state.sequence);mix((unsigned)s);mix(from);mix((unsigned)d);mix(to);mix(bytes);
 for(size_t i=0;i<bytes;i++){
  surfaces[d].last_event[to+i]=surfaces[s].last_event[from+i];
  surfaces[d].last_writer[to+i]=surfaces[s].last_writer[from+i];
 }
}
/* SDL2 FillRect takes const SDL_Rect*: snapshot the verified clip/intersection
 * before the ORIGINAL call, then consume its actual return. This adapter never
 * calls SDL, fills pixels, changes error/lock state, or substitutes old returns. */
static bool safe_endpoint(int origin,int extent)
{
 int64_t end=(int64_t)origin+extent;return end>=INT_MIN&&end<=INT_MAX;
}
uint64_t nwo_fill_before(NwoFillCall *call,SDL_Surface *s,const SDL_Rect *rect,enum NwoWriter writer)
{
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(lineage.pending)lineage_fail(NWL_PENDING);
 if(!state.active){if(call)memset(call,0,sizeof(*call));return 0;}
 if(!fill_counter(&state.fill_calls))return 0;
 /* Do not overwrite the original ticket when the same address reenters. */
 if(pending_fill.active){nwo_coverage_gap(NWO_GAP_FILL_REENTRANT);return 0;}
 if(!call){nwo_coverage_gap(NWO_GAP_FILL_TOKEN);return 0;}
 memset(call,0,sizeof(*call));
 if(fill_nonce==UINT64_MAX){nwo_coverage_gap(NWO_GAP_FILL_NONCE_OVERFLOW);nwo_invalidate(NWO_OVERFLOW);return 0;}
 call->started=true;call->tick=state.tick;call->epoch=observer_epoch;call->nonce=++fill_nonce;
 pending_fill.active=true;pending_fill.ticket_address=(uintptr_t)call;pending_fill.snapshot=*call;
 state.fill_pending=true;state.fill_pending_nonce=call->nonce;
 if(!fill_counter(&state.fill_registered)||!state.valid)return call->nonce;
 if(writer!=NWO_SDL_BACKGROUND_CLEAR&&writer!=NWO_SDL_VGA_FILL&&writer!=NWO_SDL_VIDEO_CLEAR){nwo_coverage_gap(NWO_GAP_SDL_FILL_CONTEXT);return call->nonce;}
 size_t offset=0;
 if(locate(s,s?s->pixels:NULL,0,&offset)<0){nwo_coverage_gap(NWO_GAP_SDL_FILL_CONTEXT);return call->nonce;}
 SDL_Rect clip=s->clip_rect;
 if(s->locked||SDL_MUSTLOCK(s)||clip.x<0||clip.y<0||clip.w<0||clip.h<0||
    !safe_endpoint(clip.x,clip.w)||!safe_endpoint(clip.y,clip.h)||
    (int64_t)clip.x+clip.w>s->w||(int64_t)clip.y+clip.h>s->h){nwo_coverage_gap(NWO_GAP_SDL_FILL_CONTEXT);return call->nonce;}
 SDL_Rect requested=rect?*rect:clip;
 if(!safe_endpoint(requested.x,requested.w)||!safe_endpoint(requested.y,requested.h)){nwo_coverage_gap(NWO_GAP_SDL_FILL_OVERFLOW);return call->nonce;}
 SDL_Rect effective={0,0,0,0};
 if(requested.w>0&&requested.h>0&&clip.w>0&&clip.h>0){
  int64_t left=requested.x>clip.x?requested.x:clip.x;
  int64_t top=requested.y>clip.y?requested.y:clip.y;
  int64_t right=(int64_t)requested.x+requested.w,bottom=(int64_t)requested.y+requested.h;
  if(right>(int64_t)clip.x+clip.w)right=(int64_t)clip.x+clip.w;
  if(bottom>(int64_t)clip.y+clip.h)bottom=(int64_t)clip.y+clip.h;
  if(right>left&&bottom>top)effective=(SDL_Rect){(int)left,(int)top,(int)(right-left),(int)(bottom-top)};
 }
 call->surface=s;call->pixels=s->pixels;call->format=s->format;
 call->w=s->w;call->h=s->h;call->pitch=s->pitch;call->flags=s->flags;call->locked=s->locked;
 call->clip=clip;call->effective=effective;call->writer=writer;call->sequence=state.sequence;call->pending=true;
 pending_fill.snapshot=*call;return call->nonce;
}
void nwo_fill_after(NwoFillCall *call,uint64_t nonce,int original_result)
{
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(!state.active)return;
 /* Compare owned identity and explicit by-value token before caller reads.
  * A copied ticket, old stack reuse, or stale token cannot consume this slot. */
 if(!pending_fill.active||(uintptr_t)call!=pending_fill.ticket_address||!nonce||nonce!=pending_fill.snapshot.nonce){nwo_coverage_gap(NWO_GAP_FILL_TOKEN);return;}
 if(!call->started||call->completed||call->nonce!=nonce||call->tick!=pending_fill.snapshot.tick||call->epoch!=pending_fill.snapshot.epoch){nwo_coverage_gap(NWO_GAP_FILL_TOKEN);return;}
 NwoFillCall saved=pending_fill.snapshot;
 pending_fill.active=false;state.fill_pending=false;state.fill_pending_nonce=0;
 call->completed=true;call->pending=false;
 if(!fill_counter(&state.fill_consumed))return;
 if(saved.tick!=state.tick||saved.epoch!=observer_epoch){nwo_coverage_gap(NWO_GAP_FILL_TOKEN);return;}
 if(original_result!=0){fill_counter(&state.fill_returns_error);nwo_coverage_gap(NWO_GAP_SDL_FILL_ERROR);return;}
 if(!fill_counter(&state.fill_returns_ok)||!saved.pending||!state.valid)return;
 SDL_Surface *s=saved.surface;size_t offset=0;
 if(locate(s,saved.pixels,0,&offset)<0){nwo_coverage_gap(NWO_GAP_SDL_FILL_CONTEXT);return;}
 if(s->pixels!=saved.pixels||s->format!=saved.format||s->w!=saved.w||s->h!=saved.h||s->pitch!=saved.pitch||
    s->flags!=saved.flags||s->locked!=saved.locked||state.sequence!=saved.sequence||
    s->clip_rect.x!=saved.clip.x||s->clip_rect.y!=saved.clip.y||s->clip_rect.w!=saved.clip.w||s->clip_rect.h!=saved.clip.h){nwo_coverage_gap(NWO_GAP_SDL_FILL_CONTEXT);return;}
 SDL_Rect e=saved.effective;
 if(e.w<=0||e.h<=0){fill_counter(&state.fill_observed_empty);return;}
 for(int row=0;row<e.h&&state.valid;row++){
  const unsigned char *address=(const unsigned char *)s->pixels+(size_t)(e.y+row)*(size_t)s->pitch+(size_t)e.x;
  nwo_observe_store(s,address,(size_t)e.w,saved.writer);
  if(state.valid&&!fill_counter(&state.fill_observed_rows))return;
 }
}

void nwo_revoke_frame(enum NwoGap reason)
{
 b313_family_writer_gap((unsigned)reason);
 if(lineage.sealed)lineage_fail(NWL_AFTER_SEAL);
 if(!state.active)return; /* Default off: no I/O, SDL or surface access. */
 if(reason<=0||reason>=NWO_GAP_LIMIT)reason=NWO_GAP_UNREGISTERED;
 if(!state.boundary_revoked){
  state.boundary_revoked=true;state.boundary_reason=(unsigned)reason;
  state.boundary_origin_tick=state.tick;state.boundary_origin_epoch=observer_epoch;
  state.boundary_origin_sequence=state.sequence;
 }
 nwo_coverage_gap(reason);
 /* Gap precedes end: pending is retired using owned values, then invalid end
  * persists diagnostics without dereferencing any native surface or ticket. */
 nwo_end_frame(state.tick);
 revoked_state=state;
}

static uint64_t indexed_hash(const struct NwoSurface *v)
{
 /* Hash only, no raw byte/palette output. Physical bytes include padding. */
 uint64_t h=NWO_HASH_START;const unsigned char *p=v->pixels;
 for(size_t i=0;i<v->bytes;i++){h^=p[i];h*=NWO_HASH_PRIME;}return h;
}
void nwo_end_frame(unsigned tick)
{
 if(!state.active)return;
 (void)retire_pending(false);
 if(tick!=state.tick)nwo_invalidate(NWO_STALE_FRAME);
 /* Recheck identities before any optional read. Invalid surfaces are not read. */
 for(unsigned i=0;i<NWO_SURFACES&&state.valid;i++){size_t off=0;(void)locate(surfaces[i].surface,surfaces[i].pixels,0,&off);}
 FILE *f=fopen(b313_slice_path(B313_REPORT_NATIVE,false),"w");
 if(!f){nwo_invalidate(NWO_IO_ERROR);state.active=false;return;}
 fprintf(f,"{\n  \"tick\": %u,\n  \"valid_subset_observation\": %s,\n  \"ledger_complete\": false,\n  \"eligible\": false,\n  \"reasons\": %u,\n  \"sequence\": %llu,\n  \"stores\": %llu,\n  \"stored_bytes\": %llu,\n  \"copies\": %llu,\n  \"copied_bytes\": %llu,\n  \"trace_hash\": \"%016llx\",\n  \"writer_counts\": [",state.tick,state.valid?"true":"false",state.reasons,(unsigned long long)state.sequence,(unsigned long long)state.stores,(unsigned long long)state.stored_bytes,(unsigned long long)state.copies,(unsigned long long)state.copied_bytes,(unsigned long long)state.trace_hash);
 for(unsigned i=0;i<NWO_WRITER_LIMIT;i++)fprintf(f,"%s%llu",i?", ":"",(unsigned long long)state.writer_counts[i]);
 fprintf(f,"],\n  \"structural_valid\": %s,\n  \"coverage_gate_ok\": false,\n  \"uncovered_mask\": %u,\n  \"recording_stopped_after_gap\": %s,\n  \"gap_count\": %llu,\n  \"first_gap\": %u,\n  \"first_gap_after_sequence\": %llu,\n  \"unknown_write_calls\": %llu,\n  \"unknown_ranges_verified\": %llu,\n  \"unknown_ranges_unverified\": %llu,\n  \"gap_counts\": [",state.structural_valid?"true":"false",state.uncovered_mask,state.gap_count?"true":"false",(unsigned long long)state.gap_count,state.first_gap,(unsigned long long)state.first_gap_after_sequence,(unsigned long long)state.unknown_write_calls,(unsigned long long)state.unknown_ranges_verified,(unsigned long long)state.unknown_ranges_unverified);
 for(unsigned i=0;i<NWO_GAP_LIMIT;i++)fprintf(f,"%s%llu",i?", ":"",(unsigned long long)state.gap_counts[i]);
 fprintf(f,"],\n  \"fill_calls\": %llu,\n  \"fill_returns_ok\": %llu,\n  \"fill_returns_error\": %llu,\n  \"fill_observed_empty\": %llu,\n  \"fill_observed_rows\": %llu,\n",(unsigned long long)state.fill_calls,(unsigned long long)state.fill_returns_ok,(unsigned long long)state.fill_returns_error,(unsigned long long)state.fill_observed_empty,(unsigned long long)state.fill_observed_rows);
 fprintf(f,"  \"fill_registry_capacity\": 1,\n  \"fill_pending\": %s,\n  \"fill_registered\": %llu,\n  \"fill_consumed\": %llu,\n  \"fill_missing_after\": %llu,\n  \"fill_missing_on_begin\": %llu,\n  \"fill_missing_on_end\": %llu,\n  \"fill_missing_tick\": %u,\n  \"fill_missing_epoch\": %llu,\n  \"fill_missing_nonce\": %llu,\n",state.fill_pending?"true":"false",(unsigned long long)state.fill_registered,(unsigned long long)state.fill_consumed,(unsigned long long)state.fill_missing_after,(unsigned long long)state.fill_missing_on_begin,(unsigned long long)state.fill_missing_on_end,state.fill_missing_tick,(unsigned long long)state.fill_missing_epoch,(unsigned long long)state.fill_missing_nonce);
 fprintf(f,"  \"frame_epoch\": %llu,\n  \"boundary_revoked\": %s,\n  \"boundary_inherited\": %s,\n  \"boundary_reason\": %u,\n  \"boundary_origin_tick\": %u,\n  \"boundary_origin_epoch\": %llu,\n  \"boundary_origin_sequence\": %llu,\n",(unsigned long long)state.frame_epoch,state.boundary_revoked?"true":"false",state.boundary_inherited?"true":"false",state.boundary_reason,state.boundary_origin_tick,(unsigned long long)state.boundary_origin_epoch,(unsigned long long)state.boundary_origin_sequence);
 fprintf(f,"  \"first_gap_name\": \"%s\",\n  \"gap_semantics\": \"marked uncovered entry, not automatic detection of every missing writer\",\n  \"indexed_storage_hashes\": [",state.first_gap<NWO_GAP_LIMIT?gap_names[state.first_gap]:"invalid");
 if(state.valid)for(unsigned i=0;i<NWO_SURFACES;i++)fprintf(f,"%s\"%016llx\"",i?", ":"",(unsigned long long)indexed_hash(&surfaces[i]));
 fprintf(f,"]\n}\n");
 if(fclose(f)!=0)nwo_invalidate(NWO_IO_ERROR);
 lineage_seal(tick);
 state.active=false;
}
#ifdef NWO_TESTING
void nwo_test_begin(unsigned tick,SDL_Surface *game,SDL_Surface *output,SDL_Surface *aux){begin(tick,game,output,aux);}
NwoStatus nwo_test_status(void){return state;}
uint64_t nwo_test_last_event(unsigned slot,size_t offset){return slot<NWO_SURFACES&&offset<surfaces[slot].bytes?surfaces[slot].last_event[offset]:0;}
unsigned nwo_test_last_writer(unsigned slot,size_t offset){return slot<NWO_SURFACES&&offset<surfaces[slot].bytes?surfaces[slot].last_writer[offset]:0;}
void nwo_test_set_sequence(uint64_t sequence){state.sequence=sequence;}
void nwo_test_set_fill_nonce(uint64_t nonce){fill_nonce=nonce;}
#endif

#if defined(NATIVE_WRITER_SCOPE_DIAGNOSTIC) && NATIVE_WRITER_SCOPE_DIAGNOSTIC
/* Conditional path proof, separate from the unchanged globally-incomplete ledger. */
static NwsStatus nws;
static bool nws_report_attempted;
/* OHS and NWO epochs are independent; bind the actual OHS lease at begin. */
static uint64_t nws_ohs_epoch,nws_finish_epoch;
static unsigned nws_finish_phase;
static struct {SDL_Surface *surface;void *pixels;SDL_PixelFormat *format;SDL_Rect clip;Uint32 flags;int locked;} nws_surfaces[3];
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool nws_sequence_frame_retire(void)
{
 if(nws.enabled&&(!nws.valid||!nws.sealed||nws.active||!nws.reported||nws.io_failed||nws.reasons))return false;
 memset(&nws,0,sizeof(nws));memset(nws_surfaces,0,sizeof(nws_surfaces));nws_report_attempted=false;
 nws_ohs_epoch=nws_finish_epoch=0;nws_finish_phase=0;return true;
}
#endif
#if defined(B313_V6_RECOVERY_DIAGNOSTIC) && B313_V6_RECOVERY_DIAGNOSTIC
bool nws_recovery_rearm(void)
{
 if(!b313_recovery_permit_ready()||!b313_recovery_continuity()||!nws.enabled||nws.tick!=410||nws.valid||nws.active||nws.sealed||!nws.reported||nws.io_failed||nws.reasons!=NWS_EVENT||nws.events!=1||nws.last_event!=19||pending_fill.active||lineage.pending)return false;
 memset(&nws,0,sizeof(nws));memset(nws_surfaces,0,sizeof(nws_surfaces));nws_report_attempted=false;nws_ohs_epoch=nws_finish_epoch=0;nws_finish_phase=0;return true;
}
#endif
static bool nws_runtime_enabled(void)
{const char *v=getenv("BUILDING313_NATIVE_SCOPE_ENABLE");return v&&strcmp(v,"1")==0;}
bool nws_enabled_for_tick(unsigned tick){return tick==b313_slice_tick()&&nws_runtime_enabled();}
bool nws_observing(void){return nws.enabled&&nws.active&&nws.valid;}
static void nws_report(void)
{
 if(!nws.enabled||nws_report_attempted)return;
 nws_report_attempted=true;
 FILE *f=fopen(b313_slice_path(B313_REPORT_SCOPE,true),"w");
 if(!f){nws.valid=false;nws.io_failed=true;nws.reasons|=NWS_IO;return;}
 fprintf(f,"{\n\"scope\":\"selected immutable E1 physical2 tick demo/local ordinary, no event dispatch, Scale2x32 native-readonly\",\n");
 fprintf(f,"\"enabled\":true,\"path_lease_valid\":%s,\"sealed\":%s,\"epoch\":%" PRIu64 ",\"tick\":%u,\"reasons\":%u,\"stage_mask\":%u,\n",nws.valid?"true":"false",nws.sealed?"true":"false",nws.epoch,nws.tick,nws.reasons,nws.stages);
 fprintf(f,"\"events\":%u,\"last_event_type\":%u,\"video_entries\":%u,\"scaler_begins\":%u,\"scaler_ends\":%u,\"mirror_success\":%u,\"scaler_identity\":%s,\"original_source\":%s,\"cursor_active\":%s,\"foreign_owner\":%s,\"mirror_owner\":%s,\n",nws.events,nws.last_event,nws.video_entries,nws.scaler_begins,nws.scaler_ends,nws.mirror_success,nws.scaler_identity?"true":"false",nws.original_source?"true":"false",nws.cursor_active?"true":"false",nws.foreign_owner?"true":"false",nws.mirror_owner?"true":"false");
 fprintf(f,"\"sample_epoch\":%" PRIu64 ",\"finish_epoch\":%" PRIu64 ",\"finish_phase\":%u,\n",nws_ohs_epoch,nws_finish_epoch,nws_finish_phase);
 fprintf(f,"\"contexts\":[");
 for(unsigned i=0;i<NWS_STAGE_COUNT;i++){
  const NwsContext *c=&nws.context[i];
  fprintf(f,"%s{\"stage\":%u,\"observed\":%s,\"probe\":%s,\"demo\":%s,\"record\":%s,\"network\":%s,\"episode\":%u,\"level\":%u,\"smoothies\":%u,\"processor\":%u,\"any_smoothies\":%s,\"super_wild\":%s,\"filter_active\":%s,\"filter_fade\":%s,\"filter\":%d,\"brightness\":%d,\"filtration\":%s,\"transparent\":%s,\"special\":%d,\"player_end\":%s,\"skip\":%s,\"draw_alias\":%u}",i?",":"",i,(nws.stages&(1u<<i))?"true":"false",c->probe?"true":"false",c->demo?"true":"false",c->record?"true":"false",c->network?"true":"false",c->episode,c->level,c->smoothies,c->processor,c->any_smoothies?"true":"false",c->super_wild?"true":"false",c->filter_active?"true":"false",c->filter_fade?"true":"false",c->filter,c->brightness,c->filtration?"true":"false",c->transparent?"true":"false",c->special,c->player_end?"true":"false",c->skip?"true":"false",c->draw==c->game?0u:c->draw==c->output?1u:c->draw==c->aux?2u:3u);
 }
 fprintf(f,"],\"native_leaf_operations\":35,\"ordinary_copy_operations\":1,\"uncovered_mask\":31,\"ledger_complete\":false,\"eligible\":false,\"limit\":\"Requires independent frozen source/callee audit and build/input receipt. Not runtime discovery of unwitnessed raw writes.\"\n}\n");
 bool failed=ferror(f)!=0;int closed=fclose(f);
 if(failed||closed||rename(b313_slice_path(B313_REPORT_SCOPE,true),b313_slice_path(B313_REPORT_SCOPE,false))){
  remove(b313_slice_path(B313_REPORT_SCOPE,true));nws.valid=false;nws.io_failed=true;nws.reasons|=NWS_IO;return;
 }
 nws.reported=true;
}
static void nws_fail(unsigned reason)
{
 if(!nws.enabled)return;
 nws.reasons|=reason;nws.valid=false;nws.active=false;nws.sealed=false;
 /* Revoke before any external callback. Native end's invalid path only reads
  * owned metadata, including a pending-fill value snapshot, never pixel storage. */
 nwo_revoke_frame(NWO_GAP_UNREGISTERED);
 ohs_revoke(OHS_REASON_SCOPE);
 b313_scene_end();
 nws_report();
}
static bool nws_core(const NwsContext *c)
{return c&&c->tick==b313_slice_tick()&&c->episode==1&&c->level==2&&c->probe&&c->demo&&!c->record&&!c->network;}
static bool nws_geometry(const NwsContext *c,bool capture)
{
 SDL_Surface *v[3]={c->game,c->output,c->aux};
 for(unsigned i=0;i<3;i++){
  SDL_Surface *s=v[i];size_t off=0;
  if(s!=surfaces[i].surface||locate(s,surfaces[i].pixels,0,&off)!=(int)i||s->w!=320||s->h!=200||s->pitch!=320||
    s->locked||SDL_MUSTLOCK(s)||s->clip_rect.x||s->clip_rect.y||s->clip_rect.w!=320||s->clip_rect.h!=200)return false;
  if(capture){nws_surfaces[i].surface=s;nws_surfaces[i].pixels=s->pixels;nws_surfaces[i].format=s->format;nws_surfaces[i].clip=s->clip_rect;nws_surfaces[i].flags=s->flags;nws_surfaces[i].locked=s->locked;}
  else if(s!=nws_surfaces[i].surface||s->pixels!=nws_surfaces[i].pixels||s->format!=nws_surfaces[i].format||s->flags!=nws_surfaces[i].flags||s->locked!=nws_surfaces[i].locked||memcmp(&s->clip_rect,&nws_surfaces[i].clip,sizeof(SDL_Rect)))return false;
 }
 return true;
}
void nws_checkpoint(unsigned stage,const NwsContext *c)
{
 if(stage==NWS_BEGIN){
  if(!state.active||!nws_enabled_for_tick(state.tick))return;
  if(nws.enabled){nws_fail(NWS_ORDER);return;}
  memset(&nws,0,sizeof(nws));nws.enabled=nws.active=nws.valid=true;nws.tick=state.tick;nws.epoch=state.frame_epoch;
  if(!nws_core(c)||state.sequence){nws_fail(NWS_CONTEXT);return;}
  const OhsStatus *o=ohs_status();
  if(!o||!o->selected||!o->bound||!o->valid_subset||o->phase!=1||o->tick!=nws.tick||!o->epoch||o->staged||o->committed){nws_fail(NWS_PRESENTER);return;}
  nws_ohs_epoch=o->epoch;
 }else if(!nws_observing())return;
 if(!c){nws_fail(NWS_CONTEXT);return;}
 if(stage>=NWS_STAGE_COUNT||nws.stages!=(1u<<stage)-1u){nws_fail(NWS_ORDER);return;}
 nws.context[stage]=*c;nws.stages|=1u<<stage;
 if(!nws_core(c)||!state.active||!state.valid||state.frame_epoch!=nws.epoch||state.tick!=nws.tick){nws_fail(NWS_NATIVE|NWS_CONTEXT);return;}
 if(!nws_geometry(c,stage==NWS_BEGIN)){nws_fail(NWS_SURFACE);return;}
 SDL_Surface *expected=(stage==NWS_BEGIN||stage>=NWS_PRE_SHOW)?c->output:c->game;
 if(c->draw!=expected){nws_fail(NWS_SURFACE);return;}
 if(stage==NWS_POST_EVENTS&&(c->any_smoothies||c->super_wild)){nws_fail(NWS_CONTEXT);return;}
 if(stage==NWS_PRE_FILTER&&c->filter_active&&(c->filter_fade||(c->filter!=-99&&c->filtration)||(c->brightness!=-99&&c->transparent))){nws_fail(NWS_CONTEXT);return;}
 if(stage==NWS_PRE_SHOW&&(c->special||c->player_end||c->skip)){nws_fail(NWS_CONTEXT);return;}
 if(stage==NWS_POST_SHOW&&(nws.video_entries!=1||nws.scaler_begins!=1||nws.scaler_ends!=1||nws.scaler_pending||nws.mirror_success!=1)){nws_fail(NWS_ORDER);return;}
}
void nws_before_event(unsigned type)
{
 if(!nws_observing())return;
 ++nws.events;nws.last_event=type;nws_fail(NWS_EVENT);
}
void nws_video_entry(SDL_Surface *source,bool foreign_owner,bool mirror_owner)
{
 if(!nws_observing())return;
 nws.foreign_owner=foreign_owner;nws.mirror_owner=mirror_owner;
 const OhsStatus *o=ohs_status();
 nws_finish_phase=o?o->phase:0;nws_finish_epoch=o?o->epoch:0;
 /* finish has retired active; its valid OHS lease is now phase3, before Present. */
 bool finished=o&&o->selected&&o->bound&&o->valid_subset&&o->tick==nws.tick&&o->epoch==nws_ohs_epoch&&o->phase==3&&!o->staged&&!o->committed;
 if(nws.stages!=(1u<<NWS_POST_SHOW)-1u||nws.video_entries||source!=surfaces[1].surface||foreign_owner||mirror_owner||!finished){nws_fail(NWS_PRESENTER);return;}
 ++nws.video_entries;
}
void nws_before_scaler(SDL_Surface *source,SDL_Surface *actual,bool identity,bool format32,bool cursor_active)
{
 if(!nws_observing())return;
 nws.scaler_identity=identity;nws.original_source=source==actual&&actual==surfaces[1].surface;nws.cursor_active=cursor_active;
 if(nws.video_entries!=1||nws.scaler_begins||nws.scaler_pending||!identity||!format32||cursor_active||!nws.original_source){nws_fail(NWS_SCALER);return;}
 ++nws.scaler_begins;nws.scaler_pending=true;
}
void nws_after_scaler(void)
{
 if(!nws_observing())return;
 if(!nws.scaler_pending||nws.scaler_begins!=1||nws.scaler_ends){nws_fail(NWS_SCALER);return;}
 nws.scaler_pending=false;++nws.scaler_ends;
}
void nws_video_mirror_success(void)
{
 if(!nws_observing())return;
 const OhsStatus *o=ohs_status();
 if(nws.scaler_pending||nws.scaler_ends!=1||nws.mirror_success||!o||!o->selected||!o->valid_subset||!o->committed||o->phase!=7||o->epoch!=nws_ohs_epoch||o->tick!=nws.tick){nws_fail(NWS_PRESENTER);return;}
 ++nws.mirror_success;
}
void nws_fallback(void){if(nws_observing())nws_fail(NWS_FALLBACK);}
void nws_end(unsigned tick)
{
 if(!nws_observing())return;
 if(tick!=nws.tick||state.active||state.frame_epoch!=nws.epoch||state.tick!=tick||!state.valid||state.gap_count||pending_fill.active||state.fill_pending||state.fill_registered!=state.fill_consumed||nws.stages!=(1u<<NWS_STAGE_COUNT)-1u||!lineage.enabled||!lineage.valid||!lineage.sealed||lineage.copy_rows!=184||lineage.pending||nws.scaler_pending||nws.mirror_success!=1){nws_fail(NWS_NATIVE|NWS_ORDER);return;}
 nws.active=false;nws.sealed=true;nws_report();
}
NwsStatus nws_status(void){return nws;}
#if defined(BUILDING313_FINAL_PROOF_DIAGNOSTIC) && BUILDING313_FINAL_PROOF_DIAGNOSTIC
/* Read only owned, sealed metadata. OHS and NWO epochs are independent. */
bool nws_final_lease_matches(unsigned tick,uint64_t native_epoch,uint64_t sample_epoch)
{
 return tick==b313_slice_tick()&&native_epoch&&sample_epoch&&nws.enabled&&nws.valid&&nws.sealed&&!nws.active&&
  nws.reported&&!nws.io_failed&&!nws.reasons&&nws.tick==tick&&nws.epoch==native_epoch&&
  nws_ohs_epoch==sample_epoch&&nws_finish_epoch==sample_epoch&&nws_finish_phase==3&&
  nws.stages==63&&!nws.events&&!nws.scaler_pending&&nws.mirror_success==1&&
  !state.active&&state.valid&&state.structural_valid&&state.tick==tick&&state.frame_epoch==native_epoch&&
  !state.gap_count&&!pending_fill.active&&!state.fill_pending&&state.fill_registered==state.fill_consumed&&
  lineage.enabled&&lineage.valid&&lineage.sealed&&!lineage.pending&&lineage.lease==native_epoch&&lineage.copy_rows==184;
}
#endif
#endif

#if defined(BUILDING313_PRECOMMIT_DIAGNOSTIC) && BUILDING313_PRECOMMIT_DIAGNOSTIC && defined(NATIVE_WRITER_SCOPE_DIAGNOSTIC) && NATIVE_WRITER_SCOPE_DIAGNOSTIC
bool nws_precommit_capture(B313PreLease *out)
{
 const OhsStatus *o=ohs_status();
 if(!out||!nws.enabled||!nws.active||!nws.valid||nws.sealed||nws.reported||nws.io_failed||nws.reasons||nws.tick!=b313_slice_tick()||
  nws.stages!=31||nws.events||nws.video_entries!=1||nws.scaler_begins!=1||nws.scaler_ends!=1||nws.scaler_pending||nws.mirror_success||
  !nws.scaler_identity||!nws.original_source||nws.foreign_owner||nws.mirror_owner||nws.cursor_active||
  !state.active||!state.valid||!state.structural_valid||state.tick!=b313_slice_tick()||state.frame_epoch!=nws.epoch||state.gap_count||
  pending_fill.active||state.fill_pending||state.fill_registered!=state.fill_consumed||
  !lineage.enabled||!lineage.valid||lineage.sealed||lineage.pending||lineage.tick!=b313_slice_tick()||lineage.calls!=16||lineage.copy_rows!=184||lineage.lease!=state.frame_epoch||
  !o||!o->selected||!o->valid_subset||!o->bound||o->tick!=b313_slice_tick()||o->epoch!=nws_ohs_epoch||o->epoch!=nws_finish_epoch||nws_finish_phase!=3||
  o->phase!=6||!o->staged||o->committed||o->present_count)return false;
 *out=(B313PreLease){state.frame_epoch,o->epoch,state.sequence,lineage.scene,lineage.frame,b313_slice_tick()};return true;
}
bool nws_precommit_matches(const B313PreLease *lease)
{
 B313PreLease now;
 return lease&&nws_precommit_capture(&now)&&now.native_epoch==lease->native_epoch&&now.sample_epoch==lease->sample_epoch&&
  now.sequence==lease->sequence&&now.scene==lease->scene&&now.frame==lease->frame&&now.tick==lease->tick;
}
NwlResult nwl_precommit_query(const B313PreLease *lease,const NwlIdentity *id)
{
 NwlResult result={0};if(!id||!nws_precommit_matches(lease))return result;
 const struct NwlCall *c=NULL;
 for(unsigned i=0;i<lineage.calls;i++)if(lineage_identity_equal(id,&lineage_calls[i].id)){c=&lineage_calls[i];break;}
 if(!c||!c->closed)return result;
 result.available=true;result.completed=true;result.first_event=c->first;result.last_event=c->last;result.stores=c->stores;result.unique_cells=c->unique;
 /* No SDL or native-buffer read. Geometry is the current validated value copy. */
 for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
  size_t source=(size_t)(id->y+(int)y)*surfaces[0].pitch+(unsigned)id->x+x;
  uint64_t expected=c->first+y*12+x;
  uint64_t e=surfaces[0].last_event[source];bool owned=e==expected&&surfaces[0].last_writer[source]==NWO_SPRITE2;
  result.source_owned+=owned;if(y==13)result.last_row_source_owned+=owned;
  if(id->x>=24&&(int64_t)id->x+12<=288&&(int64_t)id->y+14<=184){
   size_t output=(size_t)(id->y+(int)y)*surfaces[1].pitch+(unsigned)(id->x-24)+x;
   e=surfaces[1].last_event[output];owned=e==expected&&surfaces[1].last_writer[output]==NWO_SPRITE2;
   result.output_owned+=owned;if(y==13)result.last_row_output_owned+=owned;
  }
 }
 return result;
}
#endif
