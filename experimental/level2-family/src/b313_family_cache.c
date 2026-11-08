#define _POSIX_C_SOURCE 200809L
#include "b313_family_cache.h"
#include <string.h>
#ifndef B313_FAMILY_CACHE_DIAGNOSTIC
#define B313_FAMILY_CACHE_DIAGNOSTIC 0
#endif

#if B313_FAMILY_CACHE_DIAGNOSTIC
#include "b313_v6_catalog.h"
#include "b313_platform.h"
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#endif

static B313FamilyCacheStatus state={
 .diagnostic_enabled=B313_FAMILY_CACHE_DIAGNOSTIC!=0,
 .reasons=B313_FAMILY_CACHE_DIAGNOSTIC?B313FC_CLOSED:B313FC_DISABLED
};
static const unsigned char *current_pack;
static uint64_t frame_serial;
static bool preparing,poisoned;

static void close_window(void)
{
 state.frame_open=false;
 state.frame_generation=0;
}

/* Revoke public state before releasing any backing allocation. */
static void retire(unsigned reason)
{
 const unsigned char *old=current_pack;
 current_pack=NULL;
 close_window();
 state.ready=false;
 state.phase_mask=0;
 state.pack_generation=0;
 state.bytes=0;
 state.reasons|=reason;
#if B313_FAMILY_CACHE_DIAGNOSTIC
 free((void *)old);
#else
 (void)old;
#endif
}

static bool window_current(const B313FamilyCacheWindow *window)
{
 return window&&current_pack&&state.ready&&state.phase_mask==7&&
  state.frame_open&&window->pack_generation&&window->frame_generation&&
  window->pack_generation==state.pack_generation&&
  window->frame_generation==state.frame_generation;
}

#if B313_FAMILY_CACHE_DIAGNOSTIC
static void increment(uint64_t *count)
{
 if(*count!=UINT64_MAX)++*count;
}

/* Legal source loading only: fixed regular-file size, exact read plus EOF,
 * fixed digest, opaque alpha. No recovery, alternate layouts, or mutation. */
static unsigned char *read_immutable_phase(const char *path,unsigned phase,
                                           unsigned *reason)
{
 static const char *const expected[B313FC_PHASES]={
  B313_V6_PHASE0_SHA256,B313_V6_PHASE1_SHA256,B313_V6_PHASE2_SHA256
 };
 if(!path||!path[0]||phase>=B313FC_PHASES){*reason=B313FC_INPUT;return NULL;}
 increment(&state.read_calls);
 FILE *file=fopen(path,"rb");
 if(!file){*reason=B313FC_IO;return NULL;}
 uint64_t file_size;
 if(!b313_regular_file_size(file,&file_size)||file_size!=B313FC_PHASE_BYTES){
  fclose(file);*reason=B313FC_LAYOUT;return NULL;
 }
 unsigned char *raw=malloc(B313FC_PHASE_BYTES);
 if(!raw){fclose(file);*reason=B313FC_ALLOCATION;return NULL;}
 size_t got=fread(raw,1,B313FC_PHASE_BYTES,file);
 int tail=fgetc(file);
 bool read_ok=got==B313FC_PHASE_BYTES&&tail==EOF&&!ferror(file);
 int closed=fclose(file);
 if(!read_ok||closed){free(raw);*reason=B313FC_IO;return NULL;}
 unsigned char digest[B313_SHA256_BYTES];
 char hex[65];
 static const char digits[]="0123456789abcdef";
 increment(&state.hash_calls);
 if(!b313_sha256(raw,B313FC_PHASE_BYTES,digest)){
  free(raw);*reason=B313FC_DIGEST;return NULL;
 }
 for(unsigned i=0;i<B313_SHA256_BYTES;i++){
  hex[2*i]=digits[digest[i]>>4];
  hex[2*i+1]=digits[digest[i]&15];
 }
 hex[64]=0;
 if(strcmp(hex,expected[phase])){free(raw);*reason=B313FC_DIGEST;return NULL;}
 for(size_t i=3;i<B313FC_PHASE_BYTES;i+=4){
  if(raw[i]!=255){free(raw);*reason=B313FC_LAYOUT;return NULL;}
 }
 return raw;
}

static void split_rgba_tiles(unsigned char *tiles,const unsigned char *bgra)
{
 for(unsigned tile=0;tile<B313FC_TILES_PER_PHASE;tile++){
  unsigned origin_x=(tile%4)*B313FC_TILE_WIDTH;
  unsigned origin_y=(tile/4)*B313FC_TILE_HEIGHT;
  unsigned char *destination=tiles+(size_t)tile*B313FC_TILE_BYTES;
  for(unsigned y=0;y<B313FC_TILE_HEIGHT;y++){
   const unsigned char *source=bgra+
    ((size_t)(origin_y+y)*B313FC_PHASE_WIDTH+origin_x)*4;
   for(unsigned x=0;x<B313FC_TILE_WIDTH;x++){
    destination[0]=source[2];
    destination[1]=source[1];
    destination[2]=source[0];
    destination[3]=source[3];
    source+=4;destination+=4;
   }
  }
 }
}
#endif

bool b313_family_cache_prepare(const char *const paths[B313FC_PHASES])
{
 if(preparing){poisoned=true;retire(B313FC_REENTRY);return false;}
 if(state.frame_open){retire(B313FC_FRAME_OPEN);return false;}
 retire(0);
 state.reasons=0;
#if B313_FAMILY_CACHE_DIAGNOSTIC
 if(!paths){state.reasons=B313FC_INPUT;return false;}
 /* Reject missing path arguments before performing any IO. */
 for(unsigned phase=0;phase<B313FC_PHASES;phase++){
  if(!paths[phase]||!paths[phase][0]){state.reasons=B313FC_INPUT;return false;}
 }
 if(state.generation_serial==UINT64_MAX){state.reasons=B313FC_GENERATION;return false;}
 preparing=true;poisoned=false;
 unsigned char *candidate=malloc(B313FC_PACK_BYTES);
 unsigned reason=0,complete=0;
 if(!candidate)reason=B313FC_ALLOCATION;
 else for(unsigned phase=0;phase<B313FC_PHASES;phase++){
  unsigned char *raw=read_immutable_phase(paths[phase],phase,&reason);
  if(!raw)break;
  split_rgba_tiles(candidate+(size_t)phase*B313FC_PHASE_BYTES,raw);
  free(raw);
  ++complete;
 }
 preparing=false;
 if(complete!=B313FC_PHASES||poisoned){
  free(candidate);
  state.reasons|=reason|(poisoned?B313FC_REENTRY:0);
  return false;
 }
 /* Single-owner, all-or-nothing publication. No partial pack is borrowed. */
 current_pack=candidate;
 state.pack_generation=++state.generation_serial;
 state.phase_mask=7;
 state.bytes=B313FC_PACK_BYTES;
 state.ready=true;
 return true;
#else
 (void)paths;
 state.reasons=B313FC_DISABLED;
 return false;
#endif
}

bool b313_family_cache_frame_begin(B313FamilyCacheWindow *out)
{
 if(out)memset(out,0,sizeof(*out));
 if(preparing){poisoned=true;state.reasons|=B313FC_REENTRY;return false;}
 if(!out){close_window();state.reasons|=B313FC_INPUT;return false;}
 if(state.frame_open){close_window();state.reasons|=B313FC_FRAME_OPEN;return false;}
 if(!current_pack||!state.ready||state.phase_mask!=7||!state.pack_generation){
  state.reasons|=B313FC_NOT_READY;return false;
 }
 if(frame_serial==UINT64_MAX){state.reasons|=B313FC_GENERATION;return false;}
 state.frame_generation=++frame_serial;
 state.frame_open=true;
 out->pack_generation=state.pack_generation;
 out->frame_generation=state.frame_generation;
 return true;
}

bool b313_family_cache_frame_end(const B313FamilyCacheWindow *window)
{
 bool matches=window_current(window);
 /* Even an incorrectly ended window revokes all outstanding borrows. */
 close_window();
 if(!matches)state.reasons|=B313FC_WINDOW;
 return matches;
}

bool b313_family_cache_borrow(const B313FamilyCacheWindow *window,
                            unsigned phase,unsigned tile_index,
                            B313FamilyCacheTile *out)
{
 if(!out){state.reasons|=B313FC_INPUT;return false;}
 memset(out,0,sizeof(*out));
 if(!window_current(window)){state.reasons|=B313FC_WINDOW;return false;}
 if(phase>=B313FC_PHASES||tile_index>=B313FC_TILES_PER_PHASE){
  state.reasons|=B313FC_INPUT;return false;
 }
 out->rgba=current_pack+(size_t)phase*B313FC_PHASE_BYTES+
  (size_t)tile_index*B313FC_TILE_BYTES;
 out->bytes=B313FC_TILE_BYTES;
 out->stride=B313FC_TILE_STRIDE;
 out->phase=phase;out->tile_index=tile_index;
 out->width=B313FC_TILE_WIDTH;out->height=B313FC_TILE_HEIGHT;
 out->pack_generation=window->pack_generation;
 out->frame_generation=window->frame_generation;
 return true;
}

bool b313_family_cache_tile_current(const B313FamilyCacheTile *tile)
{
 if(!tile||tile->phase>=B313FC_PHASES||
    tile->tile_index>=B313FC_TILES_PER_PHASE)return false;
 B313FamilyCacheWindow window={tile->pack_generation,tile->frame_generation};
 return window_current(&window)&&tile->bytes==B313FC_TILE_BYTES&&
  tile->stride==B313FC_TILE_STRIDE&&tile->width==B313FC_TILE_WIDTH&&
  tile->height==B313FC_TILE_HEIGHT&&tile->rgba==
   current_pack+(size_t)tile->phase*B313FC_PHASE_BYTES+
   (size_t)tile->tile_index*B313FC_TILE_BYTES;
}

void b313_family_cache_invalidate(void)
{
 if(preparing)poisoned=true;
 retire(B313FC_INVALIDATED);
}

void b313_family_cache_close(void)
{
 if(preparing)poisoned=true;
 retire(B313FC_CLOSED);
}

B313FamilyCacheStatus b313_family_cache_status(void)
{
 return state;
}
