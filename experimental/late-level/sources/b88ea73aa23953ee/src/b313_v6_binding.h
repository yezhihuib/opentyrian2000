#ifndef B313_V6_BINDING_H
#define B313_V6_BINDING_H
#include <stdbool.h>
#include <stdint.h>
/* Offline metadata only. No asset pointer, file loader, game-state read or permit. */
enum { B313_V6_INPUT_FIXTURE=1, B313_V6_FORMAT_ARGB32_LE=1 };
typedef struct {
 unsigned type,record,bank,pool,slot,base;
 uint64_t slot_generation;
} B313V6Member;
typedef struct {
 uint64_t scene,frame,group,native_epoch,sample_epoch,sequence;
 unsigned tick;
 B313V6Member member[4]; /* Ordered by actor313,314,315,316, not slot number. */
} B313V6Context;
typedef struct {
 bool metadata_match,runtime_eligible,v6_runtime_validated;
 unsigned binding_input_origin,catalogue_index,phase,width,height,density,pitch,format;
 uint64_t pack_generation;
 char catalogue_sha256[65],payload_sha256[65];
 B313V6Context context;
} B313V6Binding;
/* This activates only a compiled metadata catalogue, not a loaded pixel package. */
bool b313_v6_catalogue_activate(const char *expected_content_sha256);
void b313_v6_catalogue_close(void);
uint64_t b313_v6_catalogue_generation(void);
bool b313_v6_select_slice(const B313V6Context *context,B313V6Binding *out);
bool b313_v6_binding_matches(const B313V6Context *current,const B313V6Binding *saved);
#endif
