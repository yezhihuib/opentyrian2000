#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
/* Private scoped proof of final candidate CLASSIC provenance, not HD admission. */
#include "building313_final_proof.h"
#if defined(BUILDING313_FINAL_PROOF_DIAGNOSTIC) && BUILDING313_FINAL_PROOF_DIAGNOSTIC
#include "building313_identity.h"
#include "native_writer_scope.h"
#include "old_hd_sample_observer.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static B313FinalStatus result;
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool b313_final_frame_retire(void)
{
 if(result.attempted&&(!result.reported||result.io_failed))return false;
 memset(&result,0,sizeof(result));return true;
}
#endif
static void reject(unsigned reason){result.reasons|=reason;result.valid=false;}
static bool requested(unsigned tick)
{const char *v=getenv("BUILDING313_FINAL_PROOF_ENABLE");return tick==b313_slice_tick()&&v&&strcmp(v,"1")==0;}
static void report(void)
{
 const char *tmp=b313_slice_path(B313_REPORT_FINAL,true);
 FILE *f=fopen(tmp,"w");
 if(!f){result.io_failed=true;result.io_error=1;reject(BFP_IO);return;}
 fprintf(f,"{\n\"schema\":\"building313-final-candidate-proof-v1\",\"tick\":%u,\"scoped_final_candidate_classic\":%s,\"final_candidate_query\":\"%s\",\"reasons\":%u,\n",result.tick,result.valid?"true":"false",result.valid?"CLASSIC_CANDIDATE":"UNKNOWN",result.reasons);
 fprintf(f,"\"native_epoch\":%" PRIu64 ",\"sample_epoch\":%" PRIu64 ",\"scene\":%" PRIu64 ",\"frame\":%" PRIu64 ",\"group\":%" PRIu64 ",\n",result.native_epoch,result.sample_epoch,result.scene,result.frame,result.group);
 fprintf(f,"\"joined_calls\":%u,\"unique_native_cells\":%u,\"queried_final_samples\":%u,\"matching_classic_samples\":%u,\"unknown_samples\":%u,\"bottom_matching_samples\":%u,\"first_bad_sample\":[%d,%d],\n",result.calls,result.cells,result.samples,result.classic_samples,result.unknown_samples,result.bottom_samples,result.first_bad_x,result.first_bad_y);
 fprintf(f,"\"final_old_hd_obstruction_absent_for_this_candidate\":%s,\"io_failed\":false,\"uncovered_mask\":31,\"ledger_complete\":false,\"eligible\":false,\"legacy_final_roi_query\":\"UNKNOWN\",\n",result.valid?"true":"false");
 fputs("\"scope\":\"Only this selected immutable tick group and 172032 submitted texture samples. Exact candidate palette event provenance, not general OLD_HD classification or display readback. Requires independently audited source/build inputs.\",\"limit\":\"An entirely unwitnessed same-value write is not discovered by this runtime query. Unknown or revoked evidence remains UNKNOWN. This observer never enables material.\"\n}\n",f);
 bool failed=ferror(f)!=0;int closed=fclose(f);
 if(failed||closed){remove(tmp);result.io_failed=true;result.io_error=(failed?2u:0u)|(closed?4u:0u);reject(BFP_IO);return;}
 if(rename(tmp,b313_slice_path(B313_REPORT_FINAL,false))){remove(tmp);result.io_failed=true;result.io_error=8;reject(BFP_IO);return;}
 result.reported=true;
}
static bool join(void)
{
 B313Status bs=b313_status();NwlStatus ns=nwl_status();const OhsStatus *os=ohs_status();
 if(!os){reject(BFP_CONTEXT);return false;}
 OhsStatus o=*os;result.native_epoch=ns.lease;result.sample_epoch=o.epoch;
 result.scene=bs.scene;result.frame=bs.frame;
 if(!nws_final_lease_matches(result.tick,ns.lease,o.epoch)||!o.selected||!o.valid_subset||!o.bound||!o.committed||o.phase!=7||o.tick!=b313_slice_tick()||o.density!=8||
  !ns.enabled||!ns.valid||!ns.sealed||ns.pending||ns.tick!=b313_slice_tick()||ns.copy_rows!=184||ns.calls!=16||
  !bs.tracking||bs.sampling||!bs.scene_valid||bs.reasons||bs.tick!=b313_slice_tick()||!bs.scene||!bs.frame||bs.calls!=16||bs.identity_groups!=1||bs.groups>B313_GROUP_CAPACITY||
  ns.scene!=bs.scene||ns.frame!=bs.frame){reject(BFP_CONTEXT);return false;}
 B313Group group={0};unsigned groups=0;
 for(unsigned i=0;i<bs.groups;i++){
  B313Group g;if(!b313_get_group(i,&g)){reject(BFP_IDENTITY);return false;}
  if(g.identity_observed){group=g;++groups;}
 }
 if(groups!=1||!group.nonce||group.scene!=bs.scene||!group.complete||group.reasons||group.members!=15){reject(BFP_IDENTITY);return false;}
 result.group=group.nonce;
 unsigned char cells[2688]={0};uint64_t firsts[16]={0},lasts[16]={0},calls[16]={0};
 for(unsigned i=0;i<16;i++){
  B313Call c;if(!b313_get_call(i,&c)||!c.ended||!c.nonce||c.group!=group.nonce||c.type<313||c.type>316||c.record!=c.type||c.bank!=20||c.filter||!c.generation){reject(BFP_IDENTITY);return false;}
  unsigned component=c.type-313,q=c.part==0?0:c.part==1?1:c.part==19?2:c.part==20?3:4;
  B313Member *m=group.member+component;
  if(q==4||!m->drawn||m->parts!=15||c.slot!=m->slot||c.generation!=m->generation||c.base!=m->base||c.phase!=m->phase||c.pool!=m->birth.pool||c.bank!=m->birth.bank||c.type!=m->birth.type||
   (int64_t)c.x!=(int64_t)m->draw_x+(int)(q%2)*12||(int64_t)c.y!=(int64_t)m->draw_y+(int)(q/2)*14){reject(BFP_IDENTITY);return false;}
  if(c.x<140||c.x>176||c.y<b313_slice_top()||c.y>(b313_slice_top()+42)){reject(BFP_GEOMETRY);return false;}
  NwlIdentity id={bs.scene,bs.frame,c.group,c.nonce,c.generation,b313_slice_tick(),c.slot,c.type,c.part,c.base,c.x,c.y};
  NwlResult n=nwl_query(ns.lease,&id);
  if(!n.available||!n.completed||n.stores!=168||n.unique_cells!=168||n.source_owned!=168||n.output_owned!=168||!n.first_event||n.last_event<n.first_event||n.last_event-n.first_event!=167){reject(BFP_NATIVE);return false;}
  if(!ohs_final_call_matches(o.epoch,ns.lease,&id,n.first_event,n.last_event)){reject(BFP_SAMPLE);return false;}
  for(unsigned j=0;j<i;j++)if(c.nonce==calls[j]||!(n.last_event<firsts[j]||n.first_event>lasts[j])){reject(BFP_NATIVE);return false;}
  calls[i]=c.nonce;firsts[i]=n.first_event;lasts[i]=n.last_event;++result.calls;
  for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
   unsigned cell=(unsigned)(c.y+(int)y-b313_slice_top())*48+(unsigned)(c.x+(int)x-140);
   if(cell>=2688||cells[cell]){reject(BFP_GEOMETRY);return false;}
   cells[cell]=1;++result.cells;uint64_t expected=n.first_event+y*12+x;
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
    int px=(c.x-24+(int)x)*8+(int)sx,py=(c.y+(int)y)*8+(int)sy;uint64_t actual=0;
    bool ok=ohs_final_texture_token(o.epoch,ns.lease,px,py,&actual);++result.samples;
    if(!ok||actual!=expected){++result.unknown_samples;reject(BFP_SAMPLE);if(result.first_bad_x<0){result.first_bad_x=px;result.first_bad_y=py;}}
    else{++result.classic_samples;if(c.y+(int)y==(b313_slice_top()+55))++result.bottom_samples;}
   }
  }
 }
 for(unsigned i=0;i<2688;i++)if(!cells[i]){reject(BFP_GEOMETRY);return false;}
 if(result.calls!=16||result.cells!=2688||result.samples!=172032||result.classic_samples!=172032||result.unknown_samples||result.bottom_samples!=3072){reject(BFP_SAMPLE);return false;}
 /* Recheck live metadata after all queries; do not trust the prior file. */
 if(!nws_final_lease_matches(result.tick,ns.lease,o.epoch)){reject(BFP_CONTEXT);return false;}
 result.checked=true;return !result.reasons;
}
void b313_final_proof(unsigned tick)
{
 if(!requested(tick))return;
 if(result.attempted){reject(BFP_REPEAT);return;} /* Preserve the first artifact. */
 memset(&result,0,sizeof(result));result.attempted=true;result.tick=tick;result.first_bad_x=result.first_bad_y=-1;
 result.valid=join();report();
}
const B313FinalStatus *b313_final_status(void){return &result;}
#else
typedef int building313_final_proof_disabled_translation_unit;
#endif
