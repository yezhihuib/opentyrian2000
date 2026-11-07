#include "b313_tail414_control.h"
#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
/* Phase6, single-threaded no-op permit. No native/RGBA/cache write API. */
#include "building313_precommit.h"
#if defined(BUILDING313_PRECOMMIT_DIAGNOSTIC) && BUILDING313_PRECOMMIT_DIAGNOSTIC
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static B313PreStatus result;
static B313PreLease prepared_lease;
static B313PreIdentity prepared_identity;
static uint64_t serial;
static bool flush_attempted;
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool b313_precommit_frame_retire(void)
{
 if(result.attempted&&(!result.flushed||result.io_failed||result.reasons||!result.consumed||result.prepared))return false;
 memset(&result,0,sizeof(result));memset(&prepared_lease,0,sizeof(prepared_lease));memset(&prepared_identity,0,sizeof(prepared_identity));flush_attempted=false;return true;
}
#endif
static bool requested(unsigned tick)
{const char *v=getenv("BUILDING313_PRECOMMIT_ENABLE");return (!b313_recovery_enabled()||b313_recovery_write_tick(tick)||b313_tail414_probe_tick(tick))&&tick==b313_slice_tick()&&v&&strcmp(v,"1")==0;}
static void reject(unsigned reason)
{result.reasons|=reason;result.prepared=false;result.precommit_probe_allow=false;}
static bool same_identity(const B313PreIdentity *a,const B313PreIdentity *b)
{
 if(a->state.scene!=b->state.scene||a->state.frame!=b->state.frame||a->state.tick!=b->state.tick||
  a->group.nonce!=b->group.nonce||a->group.scene!=b->group.scene||a->group.event_loc!=b->group.event_loc||
  a->group.birth_tick!=b->group.birth_tick||a->group.cur_loc!=b->group.cur_loc)return false;
 for(unsigned i=0;i<4;i++){
  const B313Member *x=a->group.member+i,*y=b->group.member+i;
  if(x->slot!=y->slot||x->generation!=y->generation||x->base!=y->base||x->phase!=y->phase||
   x->draw_x!=y->draw_x||x->draw_y!=y->draw_y||x->birth.sheet_identity!=y->birth.sheet_identity||x->birth.data_identity!=y->birth.data_identity)return false;
 }
 for(unsigned i=0;i<16;i++){
  const B313Call *x=a->calls+i,*y=b->calls+i;
  if(x->nonce!=y->nonce||x->group!=y->group||x->generation!=y->generation||x->slot!=y->slot||x->type!=y->type||
   x->record!=y->record||x->pool!=y->pool||x->bank!=y->bank||x->base!=y->base||x->phase!=y->phase||
   x->part!=y->part||x->filter!=y->filter||x->cycle!=y->cycle||x->x!=y->x||x->y!=y->y||x->ended!=y->ended)return false;
 }
 return true;
}
uint64_t b313_precommit_prepare(unsigned tick)
{
 if(!requested(tick))return 0;
 if(result.attempted){reject(BPC_REPEAT);return 0;}
 memset(&result,0,sizeof(result));result.attempted=true;result.tick=tick;
 if(!nws_precommit_capture(&prepared_lease)||!ohs_precommit_matches(&prepared_lease)){reject(BPC_CONTEXT);return 0;}
 result.native_epoch=prepared_lease.native_epoch;result.sample_epoch=prepared_lease.sample_epoch;
 result.sequence=prepared_lease.sequence;result.scene=prepared_lease.scene;result.frame=prepared_lease.frame;
 if(!b313_precommit_identity(&prepared_identity)||prepared_identity.state.scene!=prepared_lease.scene||prepared_identity.state.frame!=prepared_lease.frame){reject(BPC_IDENTITY);return 0;}
 result.group=prepared_identity.group.nonce;
 unsigned char cells[2688]={0};uint64_t firsts[16]={0},lasts[16]={0};
 for(unsigned i=0;i<16;i++){
  const B313Call *c=prepared_identity.calls+i;
  if(c->x<140||c->x>176||c->y<b313_slice_top()||c->y>(b313_slice_top()+42)){reject(BPC_GEOMETRY);return 0;}
  NwlIdentity id={result.scene,result.frame,c->group,c->nonce,c->generation,b313_slice_tick(),c->slot,c->type,c->part,c->base,c->x,c->y};
  NwlResult n=nwl_precommit_query(&prepared_lease,&id);
  if(!n.available||!n.completed||n.stores!=168||n.unique_cells!=168||n.source_owned!=168||n.output_owned!=168||
   !n.first_event||n.last_event<n.first_event||n.last_event-n.first_event!=167){reject(BPC_NATIVE);return 0;}
  for(unsigned j=0;j<i;j++)if(!(n.last_event<firsts[j]||n.first_event>lasts[j])){reject(BPC_NATIVE);return 0;}
  firsts[i]=n.first_event;lasts[i]=n.last_event;
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
   unsigned cell=(unsigned)(c->y+(int)y-b313_slice_top())*48+(unsigned)(c->x+(int)x-140);
   if(cell>=2688||cells[cell]){reject(BPC_GEOMETRY);return 0;}
   cells[cell]=1;++result.cells;
  }
  B313PreSamples found;
  if(!ohs_precommit_call(&prepared_lease,&id,n.first_event,n.last_event,&found)){reject(BPC_SAMPLE);return 0;}
  ++result.calls;result.samples+=found.samples;result.matched+=found.matched;result.unknown+=found.unknown;result.bottom+=found.bottom;
 }
 for(unsigned i=0;i<2688;i++)if(!cells[i]){reject(BPC_GEOMETRY);return 0;}
 if(result.calls!=16||result.cells!=2688||result.samples!=172032||result.matched!=172032||result.unknown||result.bottom!=3072){reject(BPC_SAMPLE);return 0;}
 if(!nws_precommit_matches(&prepared_lease)||!ohs_precommit_matches(&prepared_lease)){reject(BPC_CHANGED);return 0;}
 if(serial==UINT64_MAX){reject(BPC_TOKEN);return 0;}
 result.token=++serial;result.prepared=true;return result.token;
}
bool b313_precommit_consume(uint64_t token)
{
 if(!requested(result.tick))return false;
 if(!result.attempted||!result.prepared||result.consumed||!token||token!=result.token){reject(BPC_TOKEN);return false;}
 B313PreIdentity now;
 if(!nws_precommit_matches(&prepared_lease)||!ohs_precommit_matches(&prepared_lease)||
  !b313_precommit_identity(&now)||!same_identity(&prepared_identity,&now)){reject(BPC_CHANGED);return false;}
 result.prepared=false;result.consumed=true;result.precommit_probe_allow=true;
 /* Deliberate no-op: zero pixel/native/cache/material writes on either branch. */
 return true;
}
void b313_precommit_probe(unsigned tick)
{
 if(!requested(tick))return;
 if(result.attempted){reject(BPC_REPEAT);return;}
 Uint64 frequency=SDL_GetPerformanceFrequency(),start=SDL_GetPerformanceCounter();
 uint64_t token=b313_precommit_prepare(tick);
 if(token)(void)b313_precommit_consume(token);
 Uint64 end=SDL_GetPerformanceCounter();
 result.query_counter_frequency=frequency;
 result.timing_valid=frequency!=0&&end>=start;
 if(result.timing_valid)result.query_counter_ticks=end-start;
}
void b313_precommit_flush(void)
{
 if(!result.attempted||flush_attempted)return;
 flush_attempted=true;
 /* Only the saved phase6 decision is serialized. No future-state query. */
 const char *tmp=b313_slice_path(B313_REPORT_PRECOMMIT,true);
 FILE *f=fopen(tmp,"w");if(!f){result.io_failed=true;result.io_error=1;return;}
 fprintf(f,"{\n\"schema\":\"building313-precommit-noop-v1\",\"tick\":%u,\"precommit_probe_allow\":%s,\"prepared\":%s,\"consumed\":%s,\"reasons\":%u,\n",result.tick,result.precommit_probe_allow?"true":"false",result.prepared?"true":"false",result.consumed?"true":"false",result.reasons);
 fprintf(f,"\"native_epoch\":%" PRIu64 ",\"sample_epoch\":%" PRIu64 ",\"sequence\":%" PRIu64 ",\"scene\":%" PRIu64 ",\"frame\":%" PRIu64 ",\"group\":%" PRIu64 ",\n",result.native_epoch,result.sample_epoch,result.sequence,result.scene,result.frame,result.group);
 fprintf(f,"\"joined_calls\":%u,\"native_cells\":%u,\"scanned_samples\":%u,\"matching_samples\":%u,\"unknown_samples\":%u,\"bottom_samples\":%u,\n",result.calls,result.cells,result.samples,result.matched,result.unknown,result.bottom);
 fprintf(f,"\"timing_valid\":%s,\"query_counter_ticks\":%" PRIu64 ",\"query_counter_frequency\":%" PRIu64 ",\"query_ms\":%.6f,\n",result.timing_valid?"true":"false",result.query_counter_ticks,result.query_counter_frequency,result.timing_valid?1000.0*(double)result.query_counter_ticks/(double)result.query_counter_frequency:0.0);
 fputs("\"decision_point\":\"phase6 staged, before Unlock/RenderCopy/Present; active unsealed native prefix\",\"new_path_pixel_writes\":0,\"new_materials\":0,\"future_present_or_seal_used\":false,\"eligible\":false,\"uncovered_mask\":31,\"legacy_final_roi_query\":\"UNKNOWN\",\"io_failed\":false,\n",f);
 fputs("\"scope\":\"Single selected immutable tick group, immediate no-op prepare/consume only. Rejection preserves the original old-HD texture/presentation. Saved decision is not successful presentation or real-material admission.\",\"limit\":\"Pinned independent source coverage is still required; unwitnessed same-value writes are not automatically discovered. Deferred reporting never upgrades a failed prefix from future facts.\"\n}\n",f);
 bool failed=ferror(f)!=0;int closed=fclose(f);
 if(failed||closed){remove(tmp);result.io_failed=true;result.io_error=(failed?2u:0u)|(closed?4u:0u);return;}
 if(rename(tmp,b313_slice_path(B313_REPORT_PRECOMMIT,false))){remove(tmp);result.io_failed=true;result.io_error=8;return;}
 result.flushed=true;
}
const B313PreStatus *b313_precommit_status(void){return &result;}
#else
typedef int building313_precommit_disabled_translation_unit;
#endif
