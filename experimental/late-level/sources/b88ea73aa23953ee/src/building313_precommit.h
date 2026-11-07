/* Private phase6 no-op probe. Never a material/rendering admission API. */
#ifndef BUILDING313_PRECOMMIT_H
#define BUILDING313_PRECOMMIT_H
#include "building313_identity.h"
#include "native_writer_lineage.h"
typedef struct {uint64_t native_epoch,sample_epoch,sequence,scene,frame;unsigned tick;} B313PreLease;
typedef struct {B313Status state;B313Group group;B313Call calls[16];} B313PreIdentity;
typedef struct {unsigned samples,matched,unknown,bottom;int first_bad_x,first_bad_y;} B313PreSamples;
enum B313PreReason { BPC_CONTEXT=1u,BPC_IDENTITY=2u,BPC_NATIVE=4u,BPC_SAMPLE=8u,
 BPC_GEOMETRY=16u,BPC_TOKEN=32u,BPC_CHANGED=64u,BPC_REPEAT=128u,BPC_IO=256u };
typedef struct {
 bool attempted,prepared,consumed,precommit_probe_allow,flushed,io_failed,timing_valid;
 unsigned tick,reasons,calls,cells,samples,matched,unknown,bottom,io_error;
 uint64_t token,native_epoch,sample_epoch,sequence,scene,frame,group,query_counter_ticks,query_counter_frequency;
} B313PreStatus;
#if defined(BUILDING313_PRECOMMIT_DIAGNOSTIC) && BUILDING313_PRECOMMIT_DIAGNOSTIC
bool b313_precommit_read_live(unsigned slot,B313Snapshot *out);
bool b313_precommit_identity(B313PreIdentity *out);
bool nws_precommit_capture(B313PreLease *out);
bool nws_precommit_matches(const B313PreLease *lease);
NwlResult nwl_precommit_query(const B313PreLease *lease,const NwlIdentity *identity);
bool ohs_precommit_matches(const B313PreLease *lease);
bool ohs_precommit_call(const B313PreLease *lease,const NwlIdentity *identity,uint64_t first,uint64_t last,B313PreSamples *out);
uint64_t b313_precommit_prepare(unsigned tick);
bool b313_precommit_consume(uint64_t token);
void b313_precommit_probe(unsigned tick);
void b313_precommit_flush(void);
const B313PreStatus *b313_precommit_status(void);
#else
#define b313_precommit_probe(...) ((void)0)
#define b313_precommit_flush() ((void)0)
#endif
#endif
