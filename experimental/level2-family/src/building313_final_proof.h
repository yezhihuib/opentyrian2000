/* Private one-frame composition proof. No drawing or admission API. */
#ifndef BUILDING313_FINAL_PROOF_H
#define BUILDING313_FINAL_PROOF_H
#include "native_writer_lineage.h"
enum B313FinalReason { BFP_CONTEXT=1u,BFP_IDENTITY=2u,BFP_NATIVE=4u,BFP_SAMPLE=8u,
 BFP_GEOMETRY=16u,BFP_IO=32u,BFP_REPEAT=64u };
typedef struct {
 bool attempted,checked,valid,reported,io_failed;
 unsigned tick,reasons,io_error,calls,cells,samples,classic_samples,unknown_samples,bottom_samples;
 uint64_t native_epoch,sample_epoch,scene,frame,group;
 int first_bad_x,first_bad_y;
} B313FinalStatus;
#if defined(BUILDING313_FINAL_PROOF_DIAGNOSTIC) && BUILDING313_FINAL_PROOF_DIAGNOSTIC
bool nws_final_lease_matches(unsigned tick,uint64_t native_epoch,uint64_t sample_epoch);
bool ohs_final_call_matches(uint64_t sample_epoch,uint64_t native_lease,const NwlIdentity *identity,uint64_t first,uint64_t last);
bool ohs_final_texture_token(uint64_t sample_epoch,uint64_t native_lease,int x,int y,uint64_t *event);
void b313_final_proof(unsigned tick);
const B313FinalStatus *b313_final_status(void);
#else
#define b313_final_proof(...) ((void)0)
#endif
#endif
