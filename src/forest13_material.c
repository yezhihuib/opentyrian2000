/* Additive finite canopy material. FNV64 detects accidental corruption, not
 * authentication. No lower data, frame context, gameplay or RNG is changed. */
#if !defined(TARGET_WIN32) && !defined(_WIN32) && !defined(_POSIX_C_SOURCE)
#define _POSIX_C_SOURCE 200809L
#endif
#include "forest13_material.h"
#include "game_probe.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#if defined(TARGET_WIN32) || defined(_WIN32)
#include <windows.h>
/* The Microsoft CRT exposes the underscored mode constants. */
#ifndef S_ISREG
#define S_ISREG(mode) (((mode) & _S_IFMT) == _S_IFREG)
#endif
#endif
#include "forest13_bundle_index.h"

enum { FOREST13_COUNT=13, FOREST13_HEADER_BYTES=188,
 FOREST13_PAYLOAD_BYTES=3311616, FOREST13_FILE_BYTES=3311804 };
static bool policy_checked,policy_declared,policy_valid,attempted,ready;
static uint8_t *payload;
static uint32_t u32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}

static bool valid_layout(const Forest13Record *records,size_t count,size_t bytes)
{
 static const unsigned ids[FOREST13_COUNT]={211,212,213,215,221,222,223,224,225,231,232,233,234};
 if(!records||count!=FOREST13_COUNT||bytes!=FOREST13_PAYLOAD_BYTES||
    G101_ATLAS_BYTES!=2752512||G101_TILE_PIXELS!=43008)return false;
 size_t cursor=G101_ATLAS_BYTES;
 for(unsigned i=0;i<FOREST13_COUNT;i++) {
  const Forest13Record *r=records+i;
  /* Exact order also proves unique IDs, slots, and contiguous mask ranges. */
  if(r->index!=ids[i]||r->slot!=336+i||r->mask_offset!=cursor||
     cursor>bytes||G101_TILE_PIXELS>bytes-cursor)return false;
  cursor+=G101_TILE_PIXELS;
 }
 return cursor==bytes;
}

static bool valid_payload(const uint8_t *data,size_t bytes)
{
 if(!data||bytes!=FOREST13_PAYLOAD_BYTES)return false;
 for(unsigned n=3;n<G101_ATLAS_BYTES;n+=4)if(data[n]!=255)return false;
 /* The whole-file fingerprint pins every approved L8 mask byte. Canopy-domain
  * and protected-detail checks belong to the frozen build-time art audit. */
 return true;
}

/* Inspect the directory entry rather than following a dangling link into
 * ENOENT. Only a genuinely absent declaration opts out of coupled fallback. */
static bool policy_regular_file(const char *path,struct stat *status,bool *absent)
{
 *absent=false;
#if defined(TARGET_WIN32) || defined(_WIN32)
 DWORD attributes=GetFileAttributesA(path);
 if(attributes==INVALID_FILE_ATTRIBUTES) {
  DWORD error=GetLastError();
  *absent=error==ERROR_FILE_NOT_FOUND||error==ERROR_PATH_NOT_FOUND;
  return false;
 }
 if(attributes&(FILE_ATTRIBUTE_DIRECTORY|FILE_ATTRIBUTE_REPARSE_POINT))return false;
 return !stat(path,status)&&S_ISREG(status->st_mode);
#else
 if(lstat(path,status)) {
  *absent=errno==ENOENT;
  return false;
 }
 return S_ISREG(status->st_mode);
#endif
}

bool forest13_policy_check(const char *directory)
{
 static const char expected[]="forest13-coupled-original-v1\n";
 if(policy_checked)return policy_valid;
 policy_checked=true;
 if(!directory||!*directory)return false;
 char path[1024];int length=snprintf(path,sizeof(path),"%s/forest13.policy",directory);
 /* An uninspectable nonempty pack path cannot silently opt out. */
 policy_declared=true;
 if(length<0||(size_t)length>=sizeof(path))return false;
 struct stat status;bool absent;
 if(!policy_regular_file(path,&status,&absent)) {
  if(absent)policy_declared=false;
  return false;
 }
 /* Reject special files before fopen, including FIFOs that could block. */
 if(!S_ISREG(status.st_mode)||status.st_size!=(long)(sizeof(expected)-1))return false;
 FILE *f=fopen(path,"rb");if(!f)return false;
 uint8_t contents[sizeof(expected)]; /* Expected bytes plus one, never unbounded. */
 size_t bytes=fread(contents,1,sizeof(contents),f);
 bool ok=bytes==sizeof(expected)-1&&!memcmp(contents,expected,sizeof(expected)-1)&&
  feof(f)&&!ferror(f);
 if(fclose(f))ok=false;
 policy_valid=ok;return ok;
}

bool forest13_declared(void)
{return policy_declared;}

static bool exact_length(FILE *f,long bytes)
{return f&&!fseek(f,0,SEEK_END)&&ftell(f)==bytes&&!fseek(f,0,SEEK_SET);}

bool forest13_prepare(const char *directory,Forest13SourceLookup lookup,void *context)
{
 if(!forest13_policy_check(directory)||!ground101_fast_context())return false;
 if(attempted)return ready;
 attempted=true;
 if(!lookup||!directory||!*directory)return false;
 if(FOREST13_BUNDLE_RECORD_COUNT!=FOREST13_COUNT||
    sizeof(forest13_records)/sizeof(*forest13_records)!=FOREST13_COUNT||
    FOREST13_BUNDLE_HEADER_BYTES!=FOREST13_HEADER_BYTES||
    FOREST13_BUNDLE_PAYLOAD_BYTES!=FOREST13_PAYLOAD_BYTES||
    FOREST13_BUNDLE_FILE_BYTES!=FOREST13_FILE_BYTES||
    FOREST13_HEADER_BYTES!=32+FOREST13_COUNT*12||
    FOREST13_FILE_BYTES!=FOREST13_HEADER_BYTES+FOREST13_PAYLOAD_BYTES||
    !valid_layout(forest13_records,FOREST13_COUNT,FOREST13_PAYLOAD_BYTES))return false;
 char path[1024];int length=snprintf(path,sizeof(path),"%s/forest13-world-material.fcan",directory);
 if(length<0||(size_t)length>=sizeof(path))return false;
 struct stat status;
 if(stat(path,&status)||!S_ISREG(status.st_mode)||status.st_size!=FOREST13_FILE_BYTES)return false;
 FILE *f=fopen(path,"rb");uint8_t header[FOREST13_HEADER_BYTES];bool ok=false;
 if(!exact_length(f,FOREST13_FILE_BYTES))goto done;
 if(fread(header,1,sizeof(header),f)!=sizeof(header))goto done;
 if(memcmp(header,"FCANAT1\0",8)||u32(header+8)!=1||u32(header+12)!=FOREST13_COUNT||
    u32(header+16)!=768||u32(header+20)!=896||u32(header+24)!=8||
    u32(header+28)!=FOREST13_PAYLOAD_BYTES)goto done;
 for(unsigned i=0;i<FOREST13_COUNT;i++) {
  const uint8_t *entry=header+32+i*12;
  if(u32(entry)!=201||u32(entry+4)!=forest13_records[i].index||
     u32(entry+8)!=forest13_records[i].mask_offset)goto done;
 }
 /* Exact dimensions, count, inventory, offsets, and length all precede this
  * one bounded payload allocation. No base copies or per-frame allocations. */
 payload=malloc(FOREST13_PAYLOAD_BYTES);if(!payload)goto done;
 if(fread(payload,1,FOREST13_PAYLOAD_BYTES,f)!=FOREST13_PAYLOAD_BYTES||
    fgetc(f)!=EOF||ferror(f))goto done;
 uint64_t hash=game_probe_hash(UINT64_C(14695981039346656037),header,sizeof(header));
 hash=game_probe_hash(hash,payload,FOREST13_PAYLOAD_BYTES);
 if(hash!=FOREST13_BUNDLE_FNV64||!valid_payload(payload,FOREST13_PAYLOAD_BYTES))goto done;
 for(unsigned i=0;i<FOREST13_COUNT;i++) {
  const Forest13Record *r=&forest13_records[i];
  const uint8_t *selected=lookup(r->index,r->slot,context);
  if(!selected)goto done;
  for(unsigned n=3;n<G101_TILE_PIXELS*4;n+=4)if(selected[n]!=255)goto done;
  if(game_probe_hash(UINT64_C(14695981039346656037),selected,G101_TILE_PIXELS*4)!=r->source_fnv64)goto done;
 }
 ok=true;
done:
 if(f&&fclose(f))ok=false;
 if(!ok){free(payload);payload=NULL;}
 ready=ok;
 return ready&&ground101_fast_context()!=NULL;
}

const Forest13Record *forest13_record(unsigned index)
{
 if(!ready||!ground101_fast_context())return NULL;
 for(unsigned i=0;i<FOREST13_COUNT;i++)if(forest13_records[i].index==index)return &forest13_records[i];
 return NULL;
}

void forest13_select(const Forest13Record *r,const uint8_t accepted[4],unsigned n,int x,int y,uint8_t out[4])
{
 memcpy(out,accepted,4);
 if(!ready||!r||n>=G101_TILE_PIXELS)return;
 /* Constant-time membership guard before using the immutable mask offset. */
 if(r->slot<336||r->slot>=336+FOREST13_COUNT||r!=&forest13_records[r->slot-336])return;
 g101_fast_select_cap(ground101_fast_context(),payload,accepted,payload[r->mask_offset+n],x,y,out);
}

#ifdef FOREST13_MATERIAL_TEST
bool forest13_test_layout(const Forest13Record *r,size_t count,size_t bytes)
{return valid_layout(r,count,bytes);}
bool forest13_test_payload(const uint8_t *data,size_t bytes)
{return valid_payload(data,bytes);}
void forest13_test_reset(void)
{
 free(payload);payload=NULL;
 policy_checked=policy_declared=policy_valid=attempted=ready=false;
}
#endif
