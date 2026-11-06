#ifndef NATIVE_WRITER_LINEAGE_H
#define NATIVE_WRITER_LINEAGE_H
#include <stdbool.h>
#include <stdint.h>
#include "SDL.h"
/* Identity-only diagnostic extension. Existing writer ABIs remain unchanged. */
enum NwlReason { NWL_CONTEXT=1u,NWL_IDENTITY=2u,NWL_PENDING=4u,NWL_RANGE=8u,NWL_WRITER=16u,NWL_DUPLICATE=32u,NWL_SEQUENCE=64u,NWL_PARTIAL=128u,NWL_COPY=256u,NWL_OVERFLOW=512u,NWL_NATIVE_INVALID=1024u,NWL_STALE=2048u,NWL_AFTER_SEAL=4096u };
typedef struct {uint64_t scene,frame,group,call,generation;unsigned tick,slot,type,part,base;int x,y;} NwlIdentity;
typedef struct {uint64_t lease,call;} NwlToken;
typedef struct {bool enabled,valid,sealed,pending;uint64_t lease,scene,frame;unsigned tick,reasons,calls,copy_rows;} NwlStatus;
typedef struct {bool available,completed;uint64_t first_event,last_event;unsigned stores,unique_cells,source_owned,output_owned,last_row_source_owned,last_row_output_owned;} NwlResult;
uint64_t nwl_open(uint64_t scene,uint64_t frame,unsigned tick);
void nwl_discard(unsigned reason);
NwlToken nwl_call_begin(uint64_t lease,const NwlIdentity *identity,SDL_Surface *surface);
void nwl_call_end(NwlToken token);
NwlStatus nwl_status(void);
NwlResult nwl_query(uint64_t lease,const NwlIdentity *identity);
/* Bridges implemented in building313_identity.c, with immutable identity joins. */
void b313_lineage_open(void);
NwlToken b313_lineage_native_begin(uint64_t identity_call,SDL_Surface *surface);
void b313_lineage_native_end(NwlToken token);
#endif
