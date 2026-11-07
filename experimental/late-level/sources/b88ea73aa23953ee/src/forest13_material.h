/* Finite optional Layer1 canopy extension, dependent on accepted ground101. */
#ifndef FOREST13_MATERIAL_H
#define FOREST13_MATERIAL_H
#include "ground101_material.h"
typedef struct {
 unsigned index,slot,mask_offset;
 uint64_t source_fnv64;
} Forest13Record;
/* Return only the selected role201/index, density8, 24x28, anchor0,0 RGBA
 * asset at this exact slot. NULL means missing or incompatible. */
typedef const uint8_t *(*Forest13SourceLookup)(unsigned index,unsigned slot,void *context);
/* Cached for the immutable selected pack's process lifetime. This check is
 * independent of lower readiness. True means an exact supported declaration;
 * declared() also includes present-invalid or unreadable declarations. */
bool forest13_policy_check(const char *asset_directory);
bool forest13_declared(void);
/* The sole payload/source attempt is deferred until lower context is valid.
 * A failure is forest-local; it never changes the lower renderer/context. */
bool forest13_prepare(const char *asset_directory,Forest13SourceLookup,void *context);
const Forest13Record *forest13_record(unsigned index);
void forest13_select(const Forest13Record *,const uint8_t accepted[4],unsigned n,int x,int y,uint8_t out[4]);
#ifdef FOREST13_MATERIAL_TEST
bool forest13_test_layout(const Forest13Record *,size_t count,size_t bytes);
bool forest13_test_payload(const uint8_t *,size_t bytes);
void forest13_test_reset(void);
#endif
#endif
