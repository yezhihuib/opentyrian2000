#include "b313_tail414_material.h"
#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
#include "b313_v6_transaction.h"
#if defined(B313_V6_TRANSACTION_DIAGNOSTIC) && B313_V6_TRANSACTION_DIAGNOSTIC
#if !B313_V6_LOCK_DIAGNOSTIC || !B313_V6_PREPARATION_DIAGNOSTIC || !B313_V6_BINDING_DIAGNOSTIC
#error The private phase0 transaction requires all three v6 diagnostic modules
#endif
#include "b313_v6_lock_bridge.h"
#include "b313_v6_prefix_preparation.h"
#include "building313_snapshot_transaction.h"
#include "old_hd_sample_observer.h"
#include "common_pause.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static B313V6TransactionStatus result;
static bool flush_attempted;
static SDL_Rect roi;
enum {ROI_BYTES=384*448*4};
#ifdef B313_V6_TRANSACTION_TESTING
static int stop_after_rows=-1;static bool fail_first_stage;
void b313_v6_transaction_test_faults(int n,bool f){stop_after_rows=n;fail_first_stage=f;}
#endif
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool b313_v6_transaction_frame_retire(void)
{
 if(result.attempted&&(!result.flushed||result.io_failed||result.reasons||!result.unlocked||!result.present_called||result.present_calls!=1||!result.snapshot_valid||result.snapshot_pending))return false;
 memset(&result,0,sizeof(result));roi=(SDL_Rect){0};flush_attempted=false;return true;
}
#endif
static bool env_one(const char *name){const char *v=getenv(name);return v&&!strcmp(v,"1");}
bool b313_v6_transaction_enabled(unsigned tick)
{return tick==b313_slice_tick()&&env_one("BUILDING313_V6_TRANSACTION_ENABLE")&&
 (b313_tail414_material_write_tick(tick)|| (b313_recovery_enabled()?(b313_recovery_write_tick(tick)&&((tick==411&&b313_slice_phase()==2)||((tick==408||tick==409)&&b313_slice_phase()==1))):
 (!b313_sequence_enabled()||((tick==408||tick==409)&&b313_slice_phase()==1))));}
static void snapshot_state(void)
{result.snapshot_pending=b313_pause_pending();result.snapshot_valid=b313_pause_valid();}
static bool stage(SDL_Surface *src,const void *pixels,int pitch,int w,int h,unsigned d)
{
 ++result.snapshot_calls;
#ifdef B313_V6_TRANSACTION_TESTING
 if(fail_first_stage){fail_first_stage=false;common_pause_snapshot_discard_candidate();result.snapshot_ready=false;result.reasons|=V6T_SNAPSHOT;snapshot_state();return false;}
#endif
 result.snapshot_ready=b313_pause_stage_checked(src,pixels,pitch,w,h,d,&roi);
 if(!result.snapshot_ready)result.reasons|=V6T_SNAPSHOT;
 snapshot_state();return result.snapshot_ready;
}
static void restore(void *pixels,int pitch,const unsigned char *backup)
{
 for(int y=0;y<roi.h;y++){
  memcpy((unsigned char *)pixels+(size_t)(roi.y+y)*pitch+(size_t)roi.x*4,backup+(size_t)y*roi.w*4,(size_t)roi.w*4);
  ++result.rollback_rows;
 }
 result.rolled_back=true;result.applied=false;
 /* Restoration does not restore the retired provenance tokens. */
}
void b313_v6_transaction_locked(uint64_t nonce,unsigned tick,const void *renderer,const void *texture,
 SDL_Surface *src,void *pixels,int pitch,int w,int h,unsigned d,bool configured,bool single_present)
{
 if(!b313_v6_transaction_enabled(tick))return;
 if(result.attempted){result.reasons|=V6T_REPEAT;return;}
 result.attempted=true;result.tick=tick;result.nonce=nonce;
 roi=(SDL_Rect){116*8,b313_slice_top()*8,48*8,56*8};
 unsigned char *backup=NULL;uint32_t *candidate=NULL;
 if(!src||!pixels||d!=8||w!=2560||h!=1600||pitch<10240||pitch%4||
    (uintptr_t)pixels%4||(uintptr_t)pixels>UINTPTR_MAX-(size_t)pitch*1600){
  result.reasons|=V6T_GEOMETRY;(void)b313_pause_stage_checked(NULL,NULL,0,0,0,0,NULL);goto done;
 }
 if(!configured||!single_present||common_pause_owns_display()){result.reasons|=V6T_CONTEXT;goto original;}
 if(env_one("BUILDING313_SNAPSHOT_TRANSACTION_ENABLE")){result.reasons|=V6T_ECHO;goto original;}
 const B313V6LockStatus *lock=b313_v6_lock_status();
 if(!nonce||!b313_v6_lock_current(nonce)||!lock->before_unlock_verified||lock->transaction_claimed){result.reasons|=V6T_PREFIX;goto original;}
 result.preparation_id=lock->prefix.preparation_id;result.pack_generation=lock->prefix.pack_generation;
 backup=malloc(ROI_BYTES);candidate=malloc(ROI_BYTES);
 if(!backup||!candidate){result.reasons|=V6T_ALLOC;goto original;}
 for(int y=0;y<roi.h;y++)memcpy(backup+(size_t)y*roi.w*4,(const unsigned char *)pixels+(size_t)(roi.y+y)*pitch+(size_t)roi.x*4,(size_t)roi.w*4);
 if(!b313_v6_material_copy_selected(result.preparation_id,candidate)||
    !b313_v6_lock_claim(nonce,renderer,texture,pixels,pitch,w,h,d,result.preparation_id)){result.reasons|=V6T_PREFIX;goto original;}
 result.claimed=true;
 if(b313_conservative_enabled()&&tick==409&&!b313_conservative_save_prefix(nonce,result.preparation_id)){result.reasons|=V6T_PREFIX;goto original;}
 if(tick==414&&!b313_tail414_material_save_prefix(nonce,result.preparation_id)){result.reasons|=V6T_PREFIX;goto original;}
 for(int y=0;y<roi.h;y++){
#ifdef B313_V6_TRANSACTION_TESTING
  if(y==stop_after_rows){result.reasons|=V6T_WRITE;break;}
#endif
  if(!result.wrote){OHS_SURVIVAL_UNKNOWN(OHS_SURVIVAL_UNKNOWN);result.observer_unknown=true;result.wrote=true;}
  memcpy((unsigned char *)pixels+(size_t)(roi.y+y)*pitch+(size_t)roi.x*4,candidate+(size_t)y*roi.w,(size_t)roi.w*4);
  ++result.rows_written;
 }
 if(result.rows_written!=(unsigned)roi.h){
  if(result.wrote)restore(pixels,pitch,backup);
  (void)stage(src,pixels,pitch,w,h,d);goto done;
 }
 result.applied=true;
 if(!stage(src,pixels,pitch,w,h,d)){restore(pixels,pitch,backup);(void)stage(src,pixels,pitch,w,h,d);}
 goto done;
original:
 if(configured&&!common_pause_owns_display())(void)stage(src,pixels,pitch,w,h,d);
done:
 free(candidate);free(backup);snapshot_state();
 /* All borrowed lock/source/cache pointers are stack-local and now dead. */
}
void b313_v6_transaction_unlocked(void)
{if(result.attempted){if(result.unlocked)result.reasons|=V6T_ORDER;result.unlocked=true;}}
void b313_v6_transaction_submit(bool called)
{
 if(!result.attempted)return;
 if(!result.unlocked){result.reasons|=V6T_ORDER;return;}
 if(result.present_calls||result.submit_failed){result.reasons|=V6T_ORDER;return;}
 if(called){result.present_called=true;++result.present_calls;}else result.submit_failed=true;
 snapshot_state();if(called&&result.applied&&!result.snapshot_valid)result.reasons|=V6T_SNAPSHOT;
}
const B313V6TransactionStatus *b313_v6_transaction_status(void){return &result;}
void b313_v6_transaction_flush(void)
{
 if(!result.attempted||flush_attempted)return;flush_attempted=true;
 const char *tmp=b313_slice_path(B313_REPORT_TRANSACTION,true);
 FILE *f=fopen(tmp,"w");if(!f){result.io_failed=true;return;}
#define B(x) ((x)?"true":"false")
 fprintf(f,"{\n\"schema\":\"building313-v6-phase0-transaction-v1\",\"tick\":%u,\"reasons\":%u,\"nonce\":%"PRIu64",\"preparation_id\":%"PRIu64",\"pack_generation\":%"PRIu64",\n",result.tick,result.reasons,result.nonce,result.preparation_id,result.pack_generation);
 fprintf(f,"\"phase\":%u,\"roi_y\":%d,\n",b313_slice_phase(),b313_slice_top());
 fprintf(f,"\"claimed\":%s,\"wrote\":%s,\"applied\":%s,\"rolled_back\":%s,\"observer_unknown\":%s,\"rows_written\":%u,\"rollback_rows\":%u,\"snapshot_calls\":%u,\n",B(result.claimed),B(result.wrote),B(result.applied),B(result.rolled_back),B(result.observer_unknown),result.rows_written,result.rollback_rows,result.snapshot_calls);
 fprintf(f,"\"unlocked\":%s,\"snapshot_ready\":%s,\"snapshot_pending\":%s,\"snapshot_valid\":%s,\"present_called\":%s,\"present_calls\":%u,\"submit_failed\":%s,\n",B(result.unlocked),B(result.snapshot_ready),B(result.snapshot_pending),B(result.snapshot_valid),B(result.present_called),result.present_calls,B(result.submit_failed));
 fputs("\"native_writes\":0,\"canvas_writes\":0,\"output_writes\":0,\"old_hd_cache_writes\":0,\"runtime_eligible\":false,\"v6_runtime_validated\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\",\"io_failed\":false,\"scope\":\"Private immutable selected tick/phase slice. Checked failure atomicity ends before Unlock. Post-Unlock failure discards pending snapshot and uses existing indexed fallback; no stale-pointer rollback. Snapshot consistency is not a real P/ESC menu proof.\"\n}\n",f);
#undef B
 const bool failed=ferror(f)!=0;const int closed=fclose(f);
 if(failed||closed||rename(tmp,b313_slice_path(B313_REPORT_TRANSACTION,false))){remove(tmp);result.io_failed=true;return;}
 result.flushed=true;
}
#else
typedef int b313_v6_transaction_disabled_translation_unit;
#endif
