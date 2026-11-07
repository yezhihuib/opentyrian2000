#ifndef B313_V6_PREFIX_PREPARATION_H
#define B313_V6_PREFIX_PREPARATION_H
#include <stdbool.h>
#include <stdint.h>
#include "building313_precommit.h"
#include "b313_v6_binding.h"
typedef struct {
 B313PreLease lease; B313PreIdentity identity; B313V6Binding binding;
 uint64_t first[16],last[16];
 unsigned calls,cells,samples,matched,unknown,bottom;
 uint64_t preparation_id;
} B313V6PrefixEvidence;
bool b313_v6_prefix_evidence_copy(uint64_t preparation_id,B313V6PrefixEvidence *out);

enum B313V6PreparationReason {
 V6P_DISABLED=1u,V6P_IO=2u,V6P_LAYOUT=4u,V6P_DIGEST=8u,V6P_CACHE=16u,
 V6P_SCOPE=32u,V6P_IDENTITY=64u,V6P_NATIVE=128u,V6P_SAMPLE=256u,
 V6P_CHANGED=512u,V6P_REENTRY=1024u,V6P_SEQUENCE=2048u
};
typedef struct {
 bool requested,cache_ready,prefix_prepared,recheck_passed;
 bool before_unlock_verified,runtime_eligible,v6_runtime_validated;
 unsigned reasons,tick,calls,cells,samples,matched,unknown,bottom;
 uint64_t pack_generation,preparation_id,native_epoch,sample_epoch,sequence,scene,frame,group;
 uint64_t file_read_calls,sha256_calls;
 unsigned phase_cache_mask;
 bool immutable_phase_set;
 char catalogue_sha256[65],payload_sha256[65];
} B313V6PreparationStatus;
#if defined(B313_V6_TRANSACTION_DIAGNOSTIC) && B313_V6_TRANSACTION_DIAGNOSTIC
/* Fixed-size caller-owned copy only; no cache pointer escapes. */
bool b313_v6_material_copy_selected(uint64_t preparation_id,uint32_t out[384*448]);
#endif
/* Private CPU cache only. No pixel pointer or renderer write API is exported. */
bool b313_v6_material_load(const char *path);
/* Startup boundary only; all three legal immutable phases commit together. */
bool b313_v6_material_preload_phases(const char *const paths[3]);
void b313_v6_material_unload(void);
/* Current-prefix snapshots only. Phase6 cannot independently prove a texture lock. */
uint64_t b313_v6_prefix_prepare(void);
bool b313_v6_prefix_recheck(uint64_t preparation_id);
const B313V6PreparationStatus *b313_v6_preparation_status(void);
/* Fact observer only: pure peek, no disabled-state normalization or invalidation. */
const B313V6PreparationStatus *b313_v6_preparation_peek(void);
#endif
