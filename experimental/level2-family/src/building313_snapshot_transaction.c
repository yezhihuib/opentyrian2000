/* Private tick415 locked texture experiment. Engine mode is echo only. */
#include "building313_snapshot_transaction.h"
#if defined(BUILDING313_SNAPSHOT_TRANSACTION_DIAGNOSTIC) && BUILDING313_SNAPSHOT_TRANSACTION_DIAGNOSTIC
#include "building313_precommit.h"
#include "old_hd_sample_observer.h"
#include "common_pause.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static B313TxnStatus result;
static bool flush_attempted;
static const SDL_Rect roi={116*8,108*8,48*8,56*8};
/* No locked texture address is retained by this module. */
bool b313_snapshot_transaction_enabled(unsigned tick)
{const char *v=getenv("BUILDING313_SNAPSHOT_TRANSACTION_ENABLE");return tick==415&&v&&strcmp(v,"1")==0;}
static uint64_t checksum(const void *data,size_t bytes)
{const unsigned char *p=data;uint64_t h=UINT64_C(14695981039346656037);while(bytes--)h=(h^*p++)*UINT64_C(1099511628211);return h;}
static uint64_t elapsed(uint64_t start)
{uint64_t end=SDL_GetPerformanceCounter();return end>=start?end-start:0;}
static bool prefix(void)
{
 const B313PreStatus *p=b313_precommit_status();
 if(!p->attempted||!p->consumed||!p->precommit_probe_allow||p->prepared||p->reasons||p->tick!=415||!p->native_epoch||!p->sample_epoch)return false;
 B313PreLease lease={p->native_epoch,p->sample_epoch,p->sequence,p->scene,p->frame,p->tick};
 B313PreIdentity id;
 return nws_precommit_matches(&lease)&&ohs_precommit_matches(&lease)&&b313_precommit_identity(&id)&&
  id.state.scene==p->scene&&id.state.frame==p->frame&&id.state.tick==p->tick&&id.group.nonce==p->group;
}
static bool frame_ok(const void *pixels,int pitch,int width,int height,unsigned d)
{return pixels&&d==8&&width==2560&&height==1600&&pitch>=width*4&&pitch%4==0&&(uintptr_t)pixels%4==0&&
 (uintptr_t)pixels<=UINTPTR_MAX-(size_t)pitch*(size_t)height;}
static void snapshot_state(void)
{result.snapshot_pending=b313_pause_pending();result.snapshot_valid=b313_pause_valid();}
static bool stage(SDL_Surface *src,void *pixels,int pitch,int width,int height,unsigned d)
{
 uint64_t start=SDL_GetPerformanceCounter();++result.snapshot_calls;
 bool ok=b313_pause_stage_checked(src,pixels,pitch,width,height,d,&roi);
 result.snapshot_ticks+=elapsed(start);result.snapshot_ready=ok;snapshot_state();
 if(!ok)result.reasons|=BTX_SNAPSHOT;
 return ok;
}
static void restore(void *pixels,int pitch,const unsigned char *backup)
{
 uint64_t start=SDL_GetPerformanceCounter();
 for(int y=0;y<roi.h;y++){
  memcpy((unsigned char *)pixels+(size_t)(roi.y+y)*(size_t)pitch+(size_t)roi.x*4,backup+(size_t)y*(size_t)roi.w*4,(size_t)roi.w*4);
  ++result.rollback_rows;
 }
 result.application_ticks+=elapsed(start);result.rolled_back=true;result.applied=false;
 /* Even exact restoration is a foreign write: never resurrect source tokens. */
}
static void locked(unsigned tick,SDL_Surface *src,void *pixels,int pitch,int width,int height,unsigned d,bool configured,bool single_present,const B313TxnPayload *payload,bool external,int fail_after_rows)
{
 if(!b313_snapshot_transaction_enabled(tick))return;
 if(result.attempted){
  result.reasons|=BTX_REPEAT;result.snapshot_ready=false;
  (void)b313_pause_stage_checked(NULL,NULL,0,0,0,0,NULL);snapshot_state();return;
 }
 memset(&result,0,sizeof(result));result.attempted=true;result.tick=tick;result.configured=configured;result.echo_only=!external;
 result.counter_frequency=SDL_GetPerformanceFrequency();uint64_t start=SDL_GetPerformanceCounter();
 unsigned char *backup=NULL,*candidate=NULL;
 if(!frame_ok(pixels,pitch,width,height,d)||!src){result.reasons|=BTX_GEOMETRY;(void)b313_pause_stage_checked(NULL,NULL,0,0,0,0,NULL);goto done;}
 if(!configured){result.reasons|=BTX_SCOPE;goto done;}
 if(!single_present||common_pause_owns_display()){result.reasons|=BTX_SCOPE;goto original;}
 result.precommit_allow=prefix();if(!result.precommit_allow){result.reasons|=BTX_PREFIX;goto original;}
 if(external){
  if(!payload||!payload->data){result.reasons|=BTX_MISSING;goto original;}
  if(payload->magic!=B313_TXN_MAGIC||payload->width!=384||payload->height!=448||payload->pitch!=1536||
   payload->bytes!=B313_TXN_ROI_BYTES||(uintptr_t)payload->data>UINTPTR_MAX-payload->bytes){result.reasons|=BTX_PAYLOAD;goto original;}
 }
 backup=malloc(B313_TXN_ROI_BYTES);candidate=malloc(B313_TXN_ROI_BYTES);
 if(!backup||!candidate){result.reasons|=BTX_ALLOC;goto original;}
 for(int y=0;y<roi.h;y++)memcpy(backup+(size_t)y*(size_t)roi.w*4,(const unsigned char *)pixels+(size_t)(roi.y+y)*(size_t)pitch+(size_t)roi.x*4,(size_t)roi.w*4);
 memcpy(candidate,external?payload->data:backup,B313_TXN_ROI_BYTES);
 if(external&&checksum(candidate,B313_TXN_ROI_BYTES)!=payload->checksum){result.reasons|=BTX_PAYLOAD;goto original;}
 for(size_t i=0;i<B313_TXN_ROI_BYTES/4;i++)if(((const Uint32 *)candidate)[i]>>24!=255){result.reasons|=BTX_PAYLOAD;goto original;}
 if(!external&&memcmp(candidate,backup,B313_TXN_ROI_BYTES)){result.reasons|=BTX_PAYLOAD;goto original;}
 if(!prefix()){result.reasons|=BTX_PREFIX;goto original;}
 result.prepared=true;result.validation_ticks=elapsed(start);start=SDL_GetPerformanceCounter();
 for(int y=0;y<roi.h;y++){
  if(fail_after_rows>=0&&y==fail_after_rows){result.reasons|=BTX_WRITE;break;}
  if(!result.wrote){OHS_SURVIVAL_UNKNOWN(OHS_SURVIVAL_UNKNOWN);result.observer_unknown=true;result.wrote=true;}
  memcpy((unsigned char *)pixels+(size_t)(roi.y+y)*(size_t)pitch+(size_t)roi.x*4,candidate+(size_t)y*(size_t)roi.w*4,(size_t)roi.w*4);
  ++result.rows_written;
 }
 result.application_ticks+=elapsed(start);
 if(result.rows_written!=(unsigned)roi.h){
  if(result.wrote)restore(pixels,pitch,backup);
  (void)stage(src,pixels,pitch,width,height,d);goto done;
 }
 result.applied=true;
 if(!stage(src,pixels,pitch,width,height,d)){
  restore(pixels,pitch,backup);
  (void)stage(src,pixels,pitch,width,height,d);
 }
 goto done;
original:
 result.validation_ticks=elapsed(start);(void)stage(src,pixels,pitch,width,height,d);
done:
 if(!result.validation_ticks&&!result.prepared)result.validation_ticks=elapsed(start);
 free(candidate);free(backup);snapshot_state();
}
void b313_snapshot_transaction_locked(unsigned tick,SDL_Surface *src,void *pixels,int pitch,int width,int height,unsigned d,bool configured,bool single_present)
{locked(tick,src,pixels,pitch,width,height,d,configured,single_present,NULL,false,-1);}
#ifdef BUILDING313_SNAPSHOT_TRANSACTION_TESTING
void b313_snapshot_transaction_test_locked(unsigned tick,SDL_Surface *src,void *pixels,int pitch,int width,int height,unsigned d,bool configured,bool single_present,const B313TxnPayload *payload,int fail_after_rows)
{locked(tick,src,pixels,pitch,width,height,d,configured,single_present,payload,true,fail_after_rows);}
#endif
void b313_snapshot_transaction_unlocked(void)
{if(result.attempted){if(result.unlocked)result.reasons|=BTX_ORDER;result.unlocked=true;}}
void b313_snapshot_transaction_submit(bool called)
{
 if(!result.attempted)return;
 if(!result.unlocked){result.reasons|=BTX_ORDER;return;}
 if(called){result.present_called=true;++result.present_calls;}else result.submit_failed=true;
 snapshot_state();
 if(called&&result.applied&&!result.snapshot_valid)result.reasons|=BTX_SNAPSHOT;
}
const B313TxnStatus *b313_snapshot_transaction_status(void){return &result;}
void b313_snapshot_transaction_flush(void)
{
 if(!result.attempted||flush_attempted)return;
 flush_attempted=true;
 const char *tmp="building313-snapshot-transaction-0415.json.tmp";
 FILE *f=fopen(tmp,"w");if(!f){result.io_failed=true;result.io_error=1;return;}
#define B(v) ((v)?"true":"false")
 fprintf(f,"{\n\"schema\":\"building313-locked-snapshot-transaction-v1\",\"tick\":%u,\"mode\":\"%s\",\"configured\":%s,\"reasons\":%u,\n",result.tick,result.echo_only?"echo":"unit-synthetic",B(result.configured),result.reasons);
 fprintf(f,"\"precommit_probe_allow\":%s,\"prepared\":%s,\"wrote\":%s,\"applied\":%s,\"rolled_back\":%s,\"observer_unknown\":%s,\n",B(result.precommit_allow),B(result.prepared),B(result.wrote),B(result.applied),B(result.rolled_back),B(result.observer_unknown));
 fprintf(f,"\"rows_written\":%u,\"bytes_written\":%u,\"rollback_rows\":%u,\"rollback_bytes\":%u,\"snapshot_calls\":%u,\"snapshot_ready\":%s,\"snapshot_pending\":%s,\"snapshot_valid\":%s,\n",result.rows_written,result.rows_written*1536,result.rollback_rows,result.rollback_rows*1536,result.snapshot_calls,B(result.snapshot_ready),B(result.snapshot_pending),B(result.snapshot_valid));
 fprintf(f,"\"unlocked\":%s,\"present_called\":%s,\"present_calls\":%u,\"submit_failed\":%s,\"counter_frequency\":%" PRIu64 ",\n",B(result.unlocked),B(result.present_called),result.present_calls,B(result.submit_failed),result.counter_frequency);
 fprintf(f,"\"validation_ticks\":%" PRIu64 ",\"application_ticks\":%" PRIu64 ",\"snapshot_ticks\":%" PRIu64 ",\"validation_ms\":%.6f,\"application_ms\":%.6f,\"snapshot_ms\":%.6f,\n",result.validation_ticks,result.application_ticks,result.snapshot_ticks,result.counter_frequency?1000.0*result.validation_ticks/result.counter_frequency:0.0,result.counter_frequency?1000.0*result.application_ticks/result.counter_frequency:0.0,result.counter_frequency?1000.0*result.snapshot_ticks/result.counter_frequency:0.0);
 fputs("\"native_writes\":0,\"canvas_writes\":0,\"output_writes\":0,\"old_hd_cache_writes\":0,\"eligible\":false,\"uncovered_mask\":31,\"io_failed\":false,\n",f);
 fputs("\"scope\":\"Single tick415 echo texture ROI; real different synthetic payloads only in unit fixtures. Snapshot pending/commit and Present invocation are distinct facts.\",\"atomicity\":\"Before Unlock only: whole ROI rollback and original snapshot restage on checked failure. After Unlock original SDL failure discards pending snapshot and takes indexed fallback; no stale locked pointer rollback or old-HD restoration promise.\",\"token_policy\":\"Any actual foreign write, even echo or rollback, makes old candidate survival UNKNOWN; no token resurrection.\",\"timing_scope\":\"Single counters only; snapshot timing includes the relocated pre-existing full-frame copy. No comparative performance conclusion.\"\n}\n",f);
#undef B
 bool failed=ferror(f)!=0;int closed=fclose(f);
 if(failed||closed){remove(tmp);result.io_failed=true;result.io_error=(failed?2u:0u)|(closed?4u:0u);return;}
 if(rename(tmp,"building313-snapshot-transaction-0415.json")){remove(tmp);result.io_failed=true;result.io_error=8;return;}
 result.flushed=true;
}
#else
typedef int building313_snapshot_transaction_disabled_translation_unit;
#endif
