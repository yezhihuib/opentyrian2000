/* Finite optional Layer1 plateau-cap extension, dependent on accepted ground101. */
#ifndef PLATEAU_CAP_MATERIAL_H
#define PLATEAU_CAP_MATERIAL_H
#include "ground101_material.h"
typedef struct {unsigned index,slot,mask_offset;} PCapRecord;
/* Callback must return the selected density8, 24x28, anchor0,0 RGBA asset. */
typedef const uint8_t *(*PCapSourceLookup)(unsigned index,unsigned slot,void *context);
bool plateau_cap_bundle_load(const char *asset_directory);
bool plateau_cap_verify_sources(PCapSourceLookup,void *context);
const PCapRecord *plateau_cap_record(unsigned index);
void plateau_cap_select(const PCapRecord *,const uint8_t accepted[4],unsigned n,int x,int y,uint8_t out[4]);
#ifdef PLATEAU_CAP_MATERIAL_TEST
bool plateau_cap_test_layout(const PCapRecord *,size_t count,size_t bytes,unsigned base109_offset);
bool plateau_cap_test_payload(const uint8_t *,size_t bytes);
#endif
#endif
