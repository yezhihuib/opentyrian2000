/* Private, process-immutable table of three witnessed single-frame slices. */
#ifndef B313_V6_SLICE_H
#define B313_V6_SLICE_H
#include <stdbool.h>
#include <stddef.h>
#include "b313_v6_catalog.h"
enum B313SliceReport {B313_REPORT_NATIVE,B313_REPORT_SCOPE,B313_REPORT_IDENTITY,
 B313_REPORT_SAMPLES,B313_REPORT_PRECOMMIT,B313_REPORT_FINAL,B313_REPORT_LOCK,B313_REPORT_TRANSACTION,B313_REPORT_COUNT};
#if defined(B313_V6_ANIMATION_DIAGNOSTIC) && B313_V6_ANIMATION_DIAGNOSTIC
unsigned b313_slice_tick(void);
void b313_slice_tail414_select(void);
unsigned b313_slice_phase(void);
int b313_slice_top(void);
const char *b313_slice_payload_sha(void);
const char *b313_slice_path(unsigned report,bool temporary);
#else
#define b313_slice_tick() 415u
#define b313_slice_phase() 0u
#define b313_slice_top() 108
#define b313_slice_payload_sha() B313_V6_PHASE0_SHA256
static inline const char *b313_slice_path(unsigned report,bool temporary)
{
 static const char *const names[B313_REPORT_COUNT][2]={
 {"native-writer-observer-0415.json","native-writer-observer-0415.json.tmp"},
 {"building313-native-scope-0415.json","building313-native-scope-0415.json.tmp"},
 {"building313-identity-0415.json","building313-identity-0415.json.tmp"},
 {"building313-sample-tags-0415.json","building313-sample-tags-0415.json.tmp"},
 {"building313-precommit-0415.json","building313-precommit-0415.json.tmp"},
 {"building313-final-proof-0415.json","building313-final-proof-0415.json.tmp"},
 {"building313-v6-locked-prefix-0415.json","building313-v6-locked-prefix-0415.json.tmp"},
 {"building313-v6-phase0-transaction-0415.json","building313-v6-phase0-transaction-0415.json.tmp"}};
 return report<B313_REPORT_COUNT?names[report][temporary?1:0]:NULL;
}
#endif
#endif
