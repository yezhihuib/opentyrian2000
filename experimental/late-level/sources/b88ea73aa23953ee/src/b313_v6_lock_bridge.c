#include "b313_tail414_material.h"
#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
#include "b313_v6_lock_bridge.h"
#if defined(B313_V6_LOCK_DIAGNOSTIC) && B313_V6_LOCK_DIAGNOSTIC
#include "old_hd_sample_observer.h"
#include "building313_precommit.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static B313V6LockStatus result;
static uint64_t serial;
static bool preload_attempted,active,poisoned,busy,flush_attempted;
static const void *locked_renderer,*locked_texture,*locked_pixels;
static int locked_pitch,locked_width,locked_height;
static unsigned locked_density;
static bool env_one(const char *name){const char *v=getenv(name);return v&&!strcmp(v,"1");}
static bool enabled(void){return env_one("BUILDING313_V6_LOCK_ENABLE");}
static void clear_lock(void)
{active=false;locked_renderer=locked_texture=locked_pixels=NULL;locked_pitch=locked_width=locked_height=0;locked_density=0;}
static void reject(unsigned why)
{poisoned=true;result.reasons|=why;result.before_unlock_verified=false;clear_lock();}
void b313_v6_lock_revoke(void)
{if(active||busy)reject(V6L_REVOKED);else clear_lock();}
void b313_v6_lock_preload(bool target)
{
 if(!enabled()){b313_v6_lock_revoke();return;}
 if(!target)return;
 if(preload_attempted||active||busy){reject(V6L_REENTRY);return;}
 preload_attempted=true;
 if(env_one("BUILDING313_SNAPSHOT_TRANSACTION_ENABLE")){reject(V6L_ECHO);return;}
 if(b313_conservative_enabled()){
  const char *paths[3]={getenv("BUILDING313_V6_PHASE0"),getenv("BUILDING313_V6_PHASE1"),getenv("BUILDING313_V6_PHASE2")};
  result.preloaded=b313_v6_material_preload_phases(paths);
 }else result.preloaded=b313_v6_material_load(getenv("BUILDING313_V6_PAYLOAD"));
 if(!result.preloaded)reject(V6L_PRELOAD);
}
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool b313_v6_lock_frame_retire(void)
{
 if(active||busy||poisoned||(result.attempted&&(!result.flushed||result.io_failed||!result.closed||result.reasons))){reject(V6L_ORDER);return false;}
 bool loaded=result.preloaded;clear_lock();memset(&result,0,sizeof(result));result.preloaded=loaded;flush_attempted=false;
 return true;
}
#endif
void b313_v6_lock_present_entry(unsigned tick)
{
 if(b313_recovery_enabled()&&!b313_recovery_write_tick(tick)&&!b313_tail414_material_write_tick(tick))return;
 if(!enabled()){if(active||busy)reject(V6L_DISABLED);return;}
 if(active||busy){reject(V6L_REENTRY);return;}
 if(tick!=b313_slice_tick())return;
 result.attempted=true;result.tick=tick;
 if(++result.entries!=1)reject(V6L_REENTRY);
}
uint64_t b313_v6_lock_open(unsigned tick,const void *renderer,const void *texture,
 const void *pixels,int pitch,int width,int height,unsigned density,bool repeat)
{
 if(b313_recovery_enabled()&&!b313_recovery_write_tick(tick)&&!b313_tail414_material_write_tick(tick))return 0;
 if(!enabled()){if(active||busy)reject(V6L_DISABLED);return 0;}
 if(active||busy){reject(V6L_REENTRY);return 0;}
 if(tick!=b313_slice_tick())return 0;
 if(++result.opens!=1||result.entries!=1||poisoned){reject(V6L_ORDER);return 0;}
 if(!result.preloaded){reject(V6L_PRELOAD);return 0;}
 if(repeat||env_one("BUILDING313_SNAPSHOT_TRANSACTION_ENABLE")){reject(V6L_ECHO);return 0;}
 const OhsStatus *s=ohs_status();
 if(!s->selected||!s->valid_subset||s->tick!=tick||s->density!=8||s->phase!=4||!s->epoch||s->committed){reject(V6L_CONTEXT);return 0;}
 if(!renderer||!texture||!pixels||width!=2560||height!=1600||density!=8||pitch<10240||pitch%4||
  (uintptr_t)pixels%4||(uintptr_t)pixels>UINTPTR_MAX-(size_t)pitch*1600){reject(V6L_GEOMETRY);return 0;}
 if(serial==UINT64_MAX){reject(V6L_OVERFLOW);return 0;}
 locked_renderer=renderer;locked_texture=texture;locked_pixels=pixels;
 locked_pitch=pitch;locked_width=width;locked_height=height;locked_density=density;
 result.nonce=++serial;result.sample_epoch=s->epoch;active=true;return result.nonce;
}
bool b313_v6_lock_current(uint64_t nonce)
{
 if(!enabled()){if(active||busy)reject(V6L_DISABLED);return false;}
 if(!active||poisoned||!nonce||nonce!=result.nonce)return false;
 const OhsStatus *s=ohs_status();
 if(!s->selected||!s->valid_subset||s->epoch!=result.sample_epoch||s->tick!=b313_slice_tick()||s->density!=8||
  s->phase<4||s->phase>6||s->committed||s->present_count){reject(V6L_CONTEXT);return false;}
 if(env_one("BUILDING313_SNAPSHOT_TRANSACTION_ENABLE")){reject(V6L_ECHO);return false;}
 return true;
}
void b313_v6_lock_probe(uint64_t nonce,const void *renderer,const void *texture,
 const void *pixels,int pitch,int width,int height,unsigned density)
{
 if(!enabled()){if(active||busy)reject(V6L_DISABLED);return;}
 /* Non-target frames have no nonce. Do not mutate the saved target-frame fact. */
 if(!nonce&&!active&&!busy)return;
 if(result.tick!=b313_slice_tick())return;
 if(busy||result.probe_attempted){reject(V6L_REENTRY);return;}
 result.probe_attempted=true;
 if(!b313_v6_lock_current(nonce)||renderer!=locked_renderer||texture!=locked_texture||pixels!=locked_pixels||
  pitch!=locked_pitch||width!=locked_width||height!=locked_height||density!=locked_density||ohs_status()->phase!=6){reject(V6L_CONTEXT);return;}
 const uint64_t frequency=SDL_GetPerformanceFrequency(),start=SDL_GetPerformanceCounter();
 busy=true;
 const uint64_t id=b313_v6_prefix_prepare();
 const bool ok=id&&b313_v6_prefix_recheck(id);
 busy=false;
 const uint64_t end=SDL_GetPerformanceCounter();
 result.query_frequency=frequency;result.query_ticks=end>=start?end-start:0;
 result.prefix=*b313_v6_preparation_status();
 if(!ok||!b313_v6_lock_current(nonce)||!result.prefix.prefix_prepared||!result.prefix.recheck_passed||
  result.prefix.sample_epoch!=result.sample_epoch||result.prefix.tick!=b313_slice_tick()){reject(V6L_PREFIX);return;}
 /* Historical fact at this exact synchronous call site, never a pixel permit. */
 result.before_unlock_verified=true;
}
#if defined(B313_V6_TRANSACTION_DIAGNOSTIC) && B313_V6_TRANSACTION_DIAGNOSTIC
bool b313_v6_lock_claim(uint64_t nonce,const void *renderer,const void *texture,
 const void *pixels,int pitch,int width,int height,unsigned density,uint64_t id)
{
 if(result.transaction_claimed||!result.before_unlock_verified||!id||
    id!=result.prefix.preparation_id||!b313_v6_lock_current(nonce)||
    renderer!=locked_renderer||texture!=locked_texture||pixels!=locked_pixels||
    pitch!=locked_pitch||width!=locked_width||height!=locked_height||density!=locked_density||
    ohs_status()->phase!=6||!b313_v6_prefix_recheck(id))return false;
 result.transaction_claimed=true;return true;
}
#endif

void b313_v6_lock_close(uint64_t nonce)
{
 if(!nonce){if(active)reject(V6L_ORDER);return;}
 if(!active||nonce!=result.nonce){if(!poisoned)reject(V6L_ORDER);clear_lock();return;}
 if(!b313_v6_lock_current(nonce)){clear_lock();return;}
 ++result.closes;result.closed=true;clear_lock();
}
const B313V6LockStatus *b313_v6_lock_status(void)
{if(!enabled()&&(active||busy))reject(V6L_DISABLED);return &result;}
void b313_v6_lock_flush(void)
{
 if(!result.attempted||flush_attempted)return;
 flush_attempted=true;
 if(active||busy)reject(V6L_ORDER);
 if(!result.closed)result.before_unlock_verified=false;
 const char *tmp=b313_slice_path(B313_REPORT_LOCK,true);
 FILE *f=fopen(tmp,"w");if(!f){result.io_failed=true;result.io_error=1;return;}
 fprintf(f,"{\n\"schema\":\"building313-v6-locked-prefix-v1\",\"tick\":%u,\"preloaded\":%s,\"before_unlock_verified\":%s,\"closed\":%s,\"active_at_flush\":false,\"reasons\":%u,\n",result.tick,result.preloaded?"true":"false",result.before_unlock_verified?"true":"false",result.closed?"true":"false",result.reasons);
 fprintf(f,"\"entries\":%u,\"opens\":%u,\"closes\":%u,\"lock_nonce\":%"PRIu64",\"sample_epoch\":%"PRIu64",\"native_epoch\":%"PRIu64",\"sequence\":%"PRIu64",\"scene\":%"PRIu64",\"frame\":%"PRIu64",\"group\":%"PRIu64",\n",result.entries,result.opens,result.closes,result.nonce,result.sample_epoch,result.prefix.native_epoch,result.prefix.sequence,result.prefix.scene,result.prefix.frame,result.prefix.group);
 fprintf(f,"\"preparation_id\":%"PRIu64",\"pack_generation\":%"PRIu64",\"calls\":%u,\"cells\":%u,\"samples\":%u,\"matched\":%u,\"unknown\":%u,\"bottom\":%u,\"prefix_reasons\":%u,\n",result.prefix.preparation_id,result.prefix.pack_generation,result.prefix.calls,result.prefix.cells,result.prefix.samples,result.prefix.matched,result.prefix.unknown,result.prefix.bottom,result.prefix.reasons);
 fprintf(f,"\"catalogue_sha256\":\"%s\",\"payload_sha256\":\"%s\",\"file_read_calls\":%"PRIu64",\"sha256_calls\":%"PRIu64",\"query_ticks\":%"PRIu64",\"query_frequency\":%"PRIu64",\"query_ms\":%.6f,\n",result.prefix.catalogue_sha256,result.prefix.payload_sha256,result.prefix.file_read_calls,result.prefix.sha256_calls,result.query_ticks,result.query_frequency,result.query_frequency?1000.0*(double)result.query_ticks/(double)result.query_frequency:0.0);
 fprintf(f,"\"phase_cache_mask\":%u,\"immutable_phase_set\":%s,\n",result.prefix.phase_cache_mask,result.prefix.immutable_phase_set?"true":"false");
 fprintf(f,"\"transaction_claimed\":%s,\n",result.transaction_claimed?"true":"false");
 fputs("\"prefix_before_unlock_verified\":false,\"runtime_eligible\":false,\"v6_runtime_validated\":false,\"bridge_pixel_writes\":0,\"io_failed\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\",\"scope\":\"Historical read-only prefix fact before any claimed transaction. No retained lock permit. See separate transaction report for material writes and submission; no future Present or seal facts used by prefix.\"\n}\n",f);
 const bool failed=ferror(f)!=0;const int closed=fclose(f);
 if(failed||closed){remove(tmp);result.io_failed=true;result.io_error=2;return;}
 if(rename(tmp,b313_slice_path(B313_REPORT_LOCK,false))){remove(tmp);result.io_failed=true;result.io_error=4;return;}
 result.flushed=true;
}
#else
typedef int b313_v6_lock_bridge_disabled_translation_unit;
#endif
