/* SPDX-License-Identifier: GPL-2.0-or-later
 * Byte-level HDR1 reading only. This grants no rendering role or cache lease.
 * Callers retain geometry, source, lifecycle and family-failure policy.
 */
#ifndef SHARED_ASSET_READER_H
#define SHARED_ASSET_READER_H
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "global_asset_registry.h"

static inline uint32_t shared_asset_u32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static inline uint64_t shared_asset_hash(const uint8_t *p,size_t n)
{uint64_t h=UINT64_C(14695981039346656037);for(size_t i=0;i<n;i++)h=(h^p[i])*UINT64_C(1099511628211);return h;}
static inline bool shared_asset_header_matches(const uint8_t h[28],const GlobalAssetResource *r)
{
 return !memcmp(h,"HDR1",4)&&shared_asset_u32(h+4)==r->identity&&
  shared_asset_u32(h+8)==r->density&&shared_asset_u32(h+12)==r->width&&shared_asset_u32(h+16)==r->height&&
  (int32_t)shared_asset_u32(h+20)==r->anchor_x&&(int32_t)shared_asset_u32(h+24)==r->anchor_y;
}
/* Preserve the global reader's established stdio behavior: one header/payload
 * read, EOF sentinel (not an added ferror predicate), and ignored close status.
 * Do not silently replace this with SHOP's regular-file fd policy. */
static inline uint8_t *shared_asset_load_stdio(const char *path,const GlobalAssetResource *r)
{
 FILE *f=fopen(path,"rb");if(!f)return NULL;
 uint8_t h[28];bool ok=fread(h,1,sizeof(h),f)==sizeof(h)&&shared_asset_header_matches(h,r);
 uint8_t *rgba=ok?malloc(r->bytes-28u):NULL;
 ok=rgba&&fread(rgba,1,r->bytes-28u,f)==r->bytes-28u&&fgetc(f)==EOF&&
  shared_asset_hash(rgba,r->bytes-28u)==r->payload_fnv;
 fclose(f);if(!ok){free(rgba);return NULL;}return rgba;
}
#endif
