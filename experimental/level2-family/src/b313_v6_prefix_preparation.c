#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
#define _POSIX_C_SOURCE 200809L
#include "b313_v6_prefix_preparation.h"
#ifndef B313_V6_PREPARATION_DIAGNOSTIC
#define B313_V6_PREPARATION_DIAGNOSTIC 0
#endif
static B313V6PreparationStatus result;
#if B313_V6_PREPARATION_DIAGNOSTIC
#include "b313_v6_binding.h"
#include "b313_v6_catalog.h"
#include "building313_precommit.h"
#include "native_writer_scope.h"
#include "native_writer_lineage.h"
#include "b313_platform.h"
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum { PHASE_BYTES=384*448*4 };
static const unsigned char *cache;
static const unsigned char *phase_cache[3];
static bool phase_set;
static uint64_t cache_generation,serial;
static bool busy,poisoned,saved_valid;
typedef struct {
 B313PreLease lease;
 B313PreIdentity identity;
 B313V6Binding binding;
 uint64_t first[16],last[16];
 unsigned calls,cells,samples,matched,unknown,bottom;
} Preparation;
static Preparation saved;
static bool enabled(void)
{const char *v=getenv("BUILDING313_V6_PREPARATION_ENABLE");return v&&strcmp(v,"1")==0;}
static void reject(unsigned reason)
{result.reasons|=reason;result.prefix_prepared=false;result.recheck_passed=false;saved_valid=false;}
static void observe_disabled(void)
{
 if(busy)poisoned=true;
 result.requested=false;reject(V6P_DISABLED);
}
static bool cache_current(void)
{unsigned phase=b313_slice_phase();
 if(phase_set)return phase<3&&phase_cache[phase]&&result.phase_cache_mask==7&&result.immutable_phase_set&&
  result.cache_ready&&cache_generation&&cache_generation==b313_v6_catalogue_generation()&&b313_slice_payload_sha();
 return cache&&result.cache_ready&&cache_generation&&cache_generation==b313_v6_catalogue_generation()&&
  b313_slice_payload_sha()&&!strcmp(result.payload_sha256,b313_slice_payload_sha());}
static bool source_window_active(void)
{NwlStatus n=nwl_status();return nws_status().active||b313_sampling()||(n.enabled&&!n.sealed);}
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool b313_v6_prefix_frame_retire(void)
{
 if(busy||poisoned){reject(V6P_REENTRY);return false;}
 saved_valid=false;memset(&saved,0,sizeof(saved));result.prefix_prepared=false;result.recheck_passed=false;
 return true;
}
#endif
void b313_v6_material_unload(void)
{
 if(busy){poisoned=true;reject(V6P_REENTRY);return;}
 free((void *)cache);cache=NULL;
 for(unsigned p=0;p<3;p++){free((void *)phase_cache[p]);phase_cache[p]=NULL;}
 phase_set=false;result.phase_cache_mask=0;result.immutable_phase_set=false;
 cache_generation=0;b313_v6_catalogue_close();
 result.cache_ready=false;result.pack_generation=0;reject(V6P_CACHE);
}
bool b313_v6_material_load(const char *path)
{
 if(!enabled()){observe_disabled();return false;}
 result.requested=true;
 if(busy){poisoned=true;reject(V6P_REENTRY);return false;}
 if(source_window_active()){reject(V6P_SCOPE);return false;}
 b313_v6_material_unload();result.reasons=0;
 if(!path){reject(V6P_IO);return false;}
 ++result.file_read_calls;FILE *f=fopen(path,"rb");
 if(!f){reject(V6P_IO);return false;}
 uint64_t file_size;
 if(!b313_regular_file_size(f,&file_size)||file_size!=PHASE_BYTES){fclose(f);reject(V6P_LAYOUT);return false;}
 unsigned char *candidate=malloc(PHASE_BYTES);
 if(!candidate){fclose(f);reject(V6P_IO);return false;}
 size_t got=fread(candidate,1,PHASE_BYTES,f);int tail=fgetc(f);bool read_ok=got==PHASE_BYTES&&tail==EOF&&!ferror(f);
 int closed=fclose(f);
 if(!read_ok||closed){free(candidate);reject(V6P_IO);return false;}
 unsigned char digest[B313_SHA256_BYTES];char hex[65];
 ++result.sha256_calls;
 if(!b313_sha256(candidate,PHASE_BYTES,digest)){free(candidate);reject(V6P_DIGEST);return false;}
 static const char digits[]="0123456789abcdef";
 for(unsigned i=0;i<B313_SHA256_BYTES;i++){hex[2*i]=digits[digest[i]>>4];hex[2*i+1]=digits[digest[i]&15];}hex[64]=0;
 if(!b313_slice_payload_sha()||strcmp(hex,b313_slice_payload_sha())){free(candidate);reject(V6P_DIGEST);return false;}
 for(unsigned p=0;p<PHASE_BYTES;p+=4){
  uint32_t argb=(uint32_t)candidate[p]|((uint32_t)candidate[p+1]<<8)|((uint32_t)candidate[p+2]<<16)|((uint32_t)candidate[p+3]<<24);
  if((argb>>24)!=255){free(candidate);reject(V6P_LAYOUT);return false;}
 }
 if(!b313_v6_catalogue_activate(B313_V6_CATALOG_SHA256)){free(candidate);reject(V6P_CACHE);return false;}
 /* Candidate becomes an immutable private canonical LE buffer only here. */
 cache=candidate;cache_generation=b313_v6_catalogue_generation();result.cache_ready=true;result.pack_generation=cache_generation;
 memcpy(result.catalogue_sha256,B313_V6_CATALOG_SHA256,65);memcpy(result.payload_sha256,hex,65);
 return true;
}
/* No phase switches load files. This routine is valid only at the same
 * inactive startup source boundary as the original single-phase loader. */
static unsigned char *read_immutable_phase(const char *path,unsigned phase,unsigned *why)
{
 static const char *const expected[3]={B313_V6_PHASE0_SHA256,B313_V6_PHASE1_SHA256,B313_V6_PHASE2_SHA256};
 if(!path||phase>=3){*why=V6P_IO;return NULL;}
 ++result.file_read_calls;FILE *f=fopen(path,"rb");
 if(!f){*why=V6P_IO;return NULL;}
 uint64_t file_size;
 if(!b313_regular_file_size(f,&file_size)||file_size!=PHASE_BYTES){fclose(f);*why=V6P_LAYOUT;return NULL;}
 unsigned char *candidate=malloc(PHASE_BYTES);
 if(!candidate){fclose(f);*why=V6P_IO;return NULL;}
 size_t got=fread(candidate,1,PHASE_BYTES,f);int tail=fgetc(f);bool ok=got==PHASE_BYTES&&tail==EOF&&!ferror(f);int closed=fclose(f);
 if(!ok||closed){free(candidate);*why=V6P_IO;return NULL;}
 unsigned char digest[B313_SHA256_BYTES];char hex[65];static const char digits[]="0123456789abcdef";
 ++result.sha256_calls;
 if(!b313_sha256(candidate,PHASE_BYTES,digest)){free(candidate);*why=V6P_DIGEST;return NULL;}
 for(unsigned i=0;i<B313_SHA256_BYTES;i++){hex[2*i]=digits[digest[i]>>4];hex[2*i+1]=digits[digest[i]&15];}hex[64]=0;
 if(strcmp(hex,expected[phase])){free(candidate);*why=V6P_DIGEST;return NULL;}
 for(unsigned p=0;p<PHASE_BYTES;p+=4)if(candidate[p+3]!=255){free(candidate);*why=V6P_LAYOUT;return NULL;}
 return candidate;
}
bool b313_v6_material_preload_phases(const char *const paths[3])
{
 if(!enabled()){observe_disabled();return false;}
 result.requested=true;
 if(busy){poisoned=true;reject(V6P_REENTRY);return false;}
 if(source_window_active()){reject(V6P_SCOPE);return false;}
 b313_v6_material_unload();result.reasons=0;
 if(!paths){reject(V6P_IO);return false;}
 busy=true;poisoned=false;unsigned why=0;unsigned char *candidate[3]={0};
 for(unsigned p=0;p<3;p++){candidate[p]=read_immutable_phase(paths[p],p,&why);if(!candidate[p])break;}
 bool complete=candidate[0]&&candidate[1]&&candidate[2]&&!poisoned&&enabled();
 busy=false;
 if(!complete){for(unsigned p=0;p<3;p++)free(candidate[p]);reject(why?why:V6P_REENTRY);return false;}
 if(!b313_v6_catalogue_activate(B313_V6_CATALOG_SHA256)){for(unsigned p=0;p<3;p++)free(candidate[p]);reject(V6P_CACHE);return false;}
 for(unsigned p=0;p<3;p++)phase_cache[p]=candidate[p];
 phase_set=true;cache_generation=b313_v6_catalogue_generation();result.cache_ready=true;result.pack_generation=cache_generation;
 result.phase_cache_mask=7;result.immutable_phase_set=true;
 memcpy(result.catalogue_sha256,B313_V6_CATALOG_SHA256,65);
 const char *selected=b313_slice_payload_sha();if(selected)memcpy(result.payload_sha256,selected,65);else memset(result.payload_sha256,0,65);
 return true;
}

#define EQ(f) do{if(a->f!=b->f)return false;}while(0)
static bool same_snapshot(const B313Snapshot *a,const B313Snapshot *b)
{
 EQ(slot);EQ(type);EQ(record);EQ(pool);EQ(bank);EQ(avail);EQ(size);EQ(cycle);EQ(filter);
 EQ(record_verified);EQ(graphics_verified);EQ(damaged);EQ(scoreitem);EQ(sheet_identity);EQ(data_identity);EQ(ex);EQ(ey);EQ(base);return true;
}
static bool same_member(const B313Member *a,const B313Member *b)
{EQ(slot);EQ(parts);EQ(base);EQ(phase);EQ(generation);EQ(draw_x);EQ(draw_y);EQ(drawn);return same_snapshot(&a->birth,&b->birth);}
static bool same_group(const B313Group *a,const B313Group *b)
{
 EQ(nonce);EQ(scene);EQ(event_loc);EQ(cur_loc);EQ(birth_tick);EQ(pool);EQ(link);EQ(members);EQ(reasons);EQ(complete);EQ(identity_observed);
 for(unsigned i=0;i<4;i++)if(!same_member(a->member+i,b->member+i))return false;
 return true;
}
static bool same_status(const B313Status *a,const B313Status *b)
{
 EQ(tracking);EQ(sampling);EQ(scene_valid);EQ(eligible);EQ(ledger_complete);EQ(old_hd_coverage_complete);
 EQ(scene);EQ(frame);EQ(enemy_blit_ordinal);EQ(tick);EQ(groups);EQ(calls);EQ(reasons);EQ(identity_groups);return true;
}
static bool same_call(const B313Call *a,const B313Call *b)
{
 EQ(nonce);EQ(group);EQ(generation);EQ(slot);EQ(type);EQ(record);EQ(pool);EQ(bank);EQ(base);EQ(phase);EQ(part);EQ(filter);EQ(cycle);EQ(x);EQ(y);EQ(ended);return true;
}
static bool same_identity(const B313PreIdentity *a,const B313PreIdentity *b)
{
 if(!same_status(&a->state,&b->state)||!same_group(&a->group,&b->group))return false;
 for(unsigned i=0;i<16;i++)if(!same_call(a->calls+i,b->calls+i))return false;
 return true;
}
static bool same_lease(const B313PreLease *a,const B313PreLease *b)
{EQ(native_epoch);EQ(sample_epoch);EQ(sequence);EQ(scene);EQ(frame);EQ(tick);return true;}
#undef EQ
static bool gather(Preparation *p,unsigned *reason)
{
 memset(p,0,sizeof(*p));
 if(!cache_current()){*reason=V6P_CACHE;return false;}
 uint64_t generation=cache_generation;
 if(!nws_precommit_capture(&p->lease)||!ohs_precommit_matches(&p->lease)){*reason=V6P_SCOPE;return false;}
 if(!b313_precommit_identity(&p->identity)||p->identity.state.scene!=p->lease.scene||p->identity.state.frame!=p->lease.frame||p->identity.state.tick!=p->lease.tick){*reason=V6P_IDENTITY;return false;}
 B313V6Context context={0};context.scene=p->lease.scene;context.frame=p->lease.frame;context.tick=p->lease.tick;context.group=p->identity.group.nonce;
 context.native_epoch=p->lease.native_epoch;context.sample_epoch=p->lease.sample_epoch;context.sequence=p->lease.sequence;
 for(unsigned i=0;i<4;i++){
  const B313Member *m=p->identity.group.member+i;const B313Snapshot *birth=&m->birth;
  /* Current helper validates birth/live source identity; base is the drawn member's. */
  context.member[i]=(B313V6Member){birth->type,birth->record,birth->bank,birth->pool,m->slot,m->base,m->generation};
  if(m->phase!=b313_slice_phase()){*reason=V6P_IDENTITY;return false;}
 }
 if(!b313_v6_select_slice(&context,&p->binding)||p->binding.pack_generation!=generation){*reason=V6P_CACHE;return false;}
 unsigned char cells[2688]={0};
 for(unsigned i=0;i<16;i++){
  const B313Call *c=p->identity.calls+i;
  if(c->x<140||c->x>176||c->y<b313_slice_top()||c->y>(b313_slice_top()+42)){*reason=V6P_IDENTITY;return false;}
  NwlIdentity id={p->lease.scene,p->lease.frame,c->group,c->nonce,c->generation,p->lease.tick,c->slot,c->type,c->part,c->base,c->x,c->y};
  NwlResult n=nwl_precommit_query(&p->lease,&id);
  if(!n.available||!n.completed||n.stores!=168||n.unique_cells!=168||n.source_owned!=168||n.output_owned!=168||
   !n.first_event||n.last_event<n.first_event||n.last_event-n.first_event!=167){*reason=V6P_NATIVE;return false;}
  for(unsigned j=0;j<i;j++)if(!(n.last_event<p->first[j]||n.first_event>p->last[j])){*reason=V6P_NATIVE;return false;}
  p->first[i]=n.first_event;p->last[i]=n.last_event;
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
   unsigned cell=(unsigned)(c->y+(int)y-b313_slice_top())*48+(unsigned)(c->x+(int)x-140);
   if(cell>=2688||cells[cell]){*reason=V6P_IDENTITY;return false;}cells[cell]=1;++p->cells;
  }
  B313PreSamples found={0};
  if(!ohs_precommit_call(&p->lease,&id,n.first_event,n.last_event,&found)||found.samples!=10752||found.matched!=10752||found.unknown){*reason=V6P_SAMPLE;return false;}
  ++p->calls;p->samples+=found.samples;p->matched+=found.matched;p->unknown+=found.unknown;p->bottom+=found.bottom;
 }
 for(unsigned i=0;i<2688;i++)if(!cells[i]){*reason=V6P_IDENTITY;return false;}
 if(p->calls!=16||p->cells!=2688||p->samples!=172032||p->matched!=172032||p->unknown||p->bottom!=3072){*reason=V6P_SAMPLE;return false;}
 B313PreIdentity now;
 if(!cache_current()||cache_generation!=generation||!b313_v6_binding_matches(&context,&p->binding)||
  !nws_precommit_matches(&p->lease)||!ohs_precommit_matches(&p->lease)||!b313_precommit_identity(&now)||!same_identity(&p->identity,&now)){*reason=V6P_CHANGED;return false;}
 return true;
}
static void publish(const Preparation *p)
{
 result.tick=p->lease.tick;result.native_epoch=p->lease.native_epoch;result.sample_epoch=p->lease.sample_epoch;result.sequence=p->lease.sequence;
 result.scene=p->lease.scene;result.frame=p->lease.frame;result.group=p->identity.group.nonce;result.pack_generation=p->binding.pack_generation;
 memcpy(result.payload_sha256,p->binding.payload_sha256,65);
 result.calls=p->calls;result.cells=p->cells;result.samples=p->samples;result.matched=p->matched;result.unknown=p->unknown;result.bottom=p->bottom;
 /* No function here observes SDL Lock/Unlock or Present. These stay false. */
 result.before_unlock_verified=false;result.runtime_eligible=false;result.v6_runtime_validated=false;
}
uint64_t b313_v6_prefix_prepare(void)
{
 if(!enabled()){observe_disabled();return 0;}
 result.requested=true;
 if(busy){poisoned=true;reject(V6P_REENTRY);return 0;}
 saved_valid=false;result.prefix_prepared=false;result.recheck_passed=false;result.reasons=0;
 busy=true;poisoned=false;unsigned reason=0;Preparation now;
 bool ok=gather(&now,&reason);busy=false;
 if(!enabled()){observe_disabled();return 0;}
 if(!ok||poisoned){reject(reason|(poisoned?V6P_REENTRY:0));return 0;}
 if(serial==UINT64_MAX){reject(V6P_SEQUENCE);return 0;}
 saved=now;saved_valid=true;publish(&saved);result.preparation_id=++serial;result.prefix_prepared=true;return serial;
}
bool b313_v6_prefix_recheck(uint64_t id)
{
 if(!enabled()){observe_disabled();return false;}
 if(busy){poisoned=true;reject(V6P_REENTRY);return false;}
 if(!saved_valid||!id||id!=result.preparation_id){reject(V6P_SEQUENCE);return false;}
 busy=true;poisoned=false;unsigned reason=0;Preparation now;
 bool ok=gather(&now,&reason);busy=false;
 if(!enabled()){observe_disabled();return false;}
 if(!ok||poisoned){reject(reason|(poisoned?V6P_REENTRY:0));return false;}
 if(!same_lease(&saved.lease,&now.lease)||!same_identity(&saved.identity,&now.identity)||saved.binding.pack_generation!=now.binding.pack_generation||
  memcmp(saved.first,now.first,sizeof(saved.first))||memcmp(saved.last,now.last,sizeof(saved.last))){reject(V6P_CHANGED);return false;}
 result.recheck_passed=true;return true;
}
/* Full proof value, not an authority bit. Must be copied while current and
 * still before any material write or provenance invalidation. */
bool b313_v6_prefix_evidence_copy(uint64_t id,B313V6PrefixEvidence *out)
{
 if(!out)return false;
 memset(out,0,sizeof(*out));
 if(!b313_v6_prefix_recheck(id)||!saved_valid||id!=result.preparation_id)return false;
 out->lease=saved.lease;out->identity=saved.identity;out->binding=saved.binding;
 memcpy(out->first,saved.first,sizeof(out->first));memcpy(out->last,saved.last,sizeof(out->last));
 out->calls=saved.calls;out->cells=saved.cells;out->samples=saved.samples;out->matched=saved.matched;out->unknown=saved.unknown;out->bottom=saved.bottom;
 out->preparation_id=id;return true;
}
#if defined(B313_V6_TRANSACTION_DIAGNOSTIC) && B313_V6_TRANSACTION_DIAGNOSTIC
bool b313_v6_material_copy_selected(uint64_t id,uint32_t out[384*448])
{
 if(!out||!b313_v6_prefix_recheck(id)||!cache_current())return false;
 /* The stored package is canonical little-endian, SDL_ARGB8888 is host Uint32. */
 for(unsigned n=0;n<384u*448u;n++){
  const unsigned char *selected=phase_set?phase_cache[b313_slice_phase()]:cache;
  const unsigned char *p=selected+4*n;
  out[n]=(uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
 }
 return true;
}
#endif

#else
bool b313_v6_prefix_evidence_copy(uint64_t id,B313V6PrefixEvidence *out){(void)id;if(out)*out=(B313V6PrefixEvidence){0};return false;}
bool b313_v6_material_load(const char *path){(void)path;return false;}
bool b313_v6_material_preload_phases(const char *const paths[3]){(void)paths;return false;}
void b313_v6_material_unload(void){}
uint64_t b313_v6_prefix_prepare(void){return 0;}
bool b313_v6_prefix_recheck(uint64_t id){(void)id;return false;}
#endif
const B313V6PreparationStatus *b313_v6_preparation_status(void)
{
#if B313_V6_PREPARATION_DIAGNOSTIC
 if(!enabled())observe_disabled();
#endif
 return &result;
}

/* Does not grant admission or invoke status normalization. */
const B313V6PreparationStatus *b313_v6_preparation_peek(void){return &result;}
