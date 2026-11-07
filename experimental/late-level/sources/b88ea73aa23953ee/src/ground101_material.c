/* Optional finite display material. FNV64 is accidental-corruption detection,
 * not authentication. Structural bounds are validated independently first. */
#include "ground101_material.h"
#include "world_material_fast.h"
#include "game_probe.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include "ground101_bundle_index.h"
/* Two transport parts reconstruct the original bundle byte-for-byte. Only
 * part0 contains its existing header; part1 adds no transport header. */
enum { G101_PART0_BYTES=8388608, G101_PART1_BYTES=7998204 };
static bool attempted,ready;
static uint8_t *payload;
static G101Context world;
static G101FastContext fast_world;
static G101Atlas atlas;
static const void *map_base;
static size_t map_bytes,map_stride;
#ifdef GROUND101_MATERIAL_TRACE
static unsigned terrain_draws,actor_draws;
static FILE *trace,*actor_trace;
static unsigned first_row,first_col;
static int first_x,first_y;
static unsigned last_report=~0u;
#endif
static uint32_t u32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}

static bool span(size_t *cursor,size_t offset,size_t length,size_t limit)
{
 if(offset!=*cursor||offset>limit||length>limit-offset)return false;
 *cursor=offset+length;return true;
}
static bool valid_layout(const G101Record *records,size_t count,size_t bytes)
{
 G101MemoryPlan plan;
 if(!records||count!=61||!g101_memory_plan(61,61,2,&plan)||bytes!=plan.total_bytes)return false;
 size_t cursor=G101_ATLAS_BYTES;unsigned footers=0,terrain=0,actors=0;
 for(size_t i=0;i<count;i++) {
  const G101Record *r=records+i;
  if(r->role==201)++terrain;else if(r->role==101||r->role==110)++actors;else return false;
  if(!r->index||r->slot>=330)return false;
  for(size_t j=0;j<i;j++)if((records[j].role==r->role&&records[j].index==r->index)||records[j].slot==r->slot)return false;
  if(!span(&cursor,r->base_offset,G101_TILE_PIXELS*4,bytes)||!span(&cursor,r->mask_offset,G101_TILE_PIXELS,bytes))return false;
  bool footer=r->role==201&&(r->index==119||r->index==120);
  if(footer) {
   ++footers;
   if(!span(&cursor,r->generated_offset,G101_TILE_PIXELS*4,bytes)||
      !span(&cursor,r->generated_weight_offset,G101_TILE_PIXELS,bytes)||
      !span(&cursor,r->ground_weight_offset,G101_TILE_PIXELS,bytes))return false;
  } else if(r->generated_offset||r->generated_weight_offset||r->ground_weight_offset)return false;
 }
 return cursor==bytes&&footers==2&&terrain==41&&actors==20;
}
static bool exact_file_length(FILE *f,long bytes)
{return f&&!fseek(f,0,SEEK_END)&&ftell(f)==bytes&&!fseek(f,0,SEEK_SET);}
#ifdef GROUND101_MATERIAL_TEST
bool ground101_test_layout(const G101Record *r,size_t count,size_t bytes)
{return valid_layout(r,count,bytes);}
#endif
bool ground101_bundle_load(const char *asset_directory)
{
 if(attempted)return ready;
 attempted=true;
 if(!asset_directory||!*asset_directory)return false;
 /* Both fixed optional parts are required; no environment or legacy override. */
 char path0[1024],path1[1024];
 int length0=snprintf(path0,sizeof(path0),"%s/ground101-world-material.g101.0",asset_directory);
 int length1=snprintf(path1,sizeof(path1),"%s/ground101-world-material.g101.1",asset_directory);
 if(length0<0||(size_t)length0>=sizeof(path0)||length1<0||(size_t)length1>=sizeof(path1))return false;
 if(G101_BUNDLE_RECORD_COUNT!=61||sizeof(g101_records)/sizeof(*g101_records)!=61||
    G101_BUNDLE_HEADER_BYTES!=32+61*12||
    G101_BUNDLE_PAYLOAD_BYTES>SIZE_MAX-G101_BUNDLE_HEADER_BYTES||
    G101_BUNDLE_FILE_BYTES!=G101_BUNDLE_HEADER_BYTES+G101_BUNDLE_PAYLOAD_BYTES||
    G101_PART0_BYTES<G101_BUNDLE_HEADER_BYTES||
    G101_PART0_BYTES>G101_BUNDLE_FILE_BYTES||
    G101_PART1_BYTES!=G101_BUNDLE_FILE_BYTES-G101_PART0_BYTES||
    !valid_layout(g101_records,61,G101_BUNDLE_PAYLOAD_BYTES))return false;
 FILE *f0=fopen(path0,"rb"),*f1=fopen(path1,"rb");
 uint8_t header[G101_BUNDLE_HEADER_BYTES];bool ok=false;
 if(!exact_file_length(f0,G101_PART0_BYTES)||!exact_file_length(f1,G101_PART1_BYTES))goto done;
 if(fread(header,1,sizeof(header),f0)!=sizeof(header))goto done;
 if(memcmp(header,"G101AT1\0",8)||u32(header+8)!=1||u32(header+12)!=61||
    u32(header+16)!=G101_ATLAS_W||u32(header+20)!=G101_ATLAS_H||u32(header+24)!=8||
    u32(header+28)!=G101_BUNDLE_PAYLOAD_BYTES)goto done;
 for(unsigned i=0;i<61;i++) {
  const uint8_t *m=header+32+12*i;const G101Record *r=&g101_records[i];
  if(u32(m)!=r->role||u32(m+4)!=r->index||u32(m+8)!=(r->generated_offset!=0))goto done;
 }
 /* Both lengths and the original header/inventory precede the allocation.
  * Read directly into one payload, with no combined-file buffer or temp file. */
 payload=malloc(G101_BUNDLE_PAYLOAD_BYTES);if(!payload)goto done;
 const size_t first_payload=G101_PART0_BYTES-G101_BUNDLE_HEADER_BYTES;
 if(fread(payload,1,first_payload,f0)!=first_payload||fgetc(f0)!=EOF||ferror(f0)||
    fread(payload+first_payload,1,G101_PART1_BYTES,f1)!=G101_PART1_BYTES||fgetc(f1)!=EOF||ferror(f1))goto done;
 uint64_t fingerprint=game_probe_hash(UINT64_C(14695981039346656037),header,sizeof(header));
 fingerprint=game_probe_hash(fingerprint,payload,G101_BUNDLE_PAYLOAD_BYTES);
 if(fingerprint!=G101_BUNDLE_FNV64)goto done;
 for(unsigned n=3;n<G101_ATLAS_BYTES;n+=4)if(payload[n]!=255)goto done;
 atlas=(G101Atlas){payload,G101_ATLAS_BYTES,768,896,8};ready=ok=true;
#ifdef GROUND101_MATERIAL_TRACE
 trace=fopen("ground101-material.tsv","w");
 if(trace){fputs("tick\tvalid\trow\tcol\torigin_x\torigin_y\tworld_x\tworld_y\tterrain_draws\tactor_quadrants\trejection\n",trace);fflush(trace);}
 actor_trace=fopen("ground101-actors.tsv","w");
 if(actor_trace){fputs("tick\ttype\tslot\tavailability\tdamaged\trole\tbase\tpart\tfilter\tfull_x\tfull_y\tworld_x\tworld_y\teligible\n",actor_trace);fflush(actor_trace);}
#endif
done:
 if(f0)fclose(f0);
 if(f1)fclose(f1);
 if(!ok){free(payload);payload=NULL;}
#ifdef GROUND101_MATERIAL_TRACE
 fprintf(stderr,"ground101 optional bundle: %s (%u payload bytes maximum)\n",ok?"verified":"disabled; selected pack unchanged",G101_BUNDLE_PAYLOAD_BYTES);
#endif
 return ready;
}
const G101Record *ground101_record_at(unsigned i){return ready&&i<61?&g101_records[i]:NULL;}
const G101Record *ground101_record(unsigned role,unsigned index)
{
 if(!ready)return NULL;
 for(unsigned i=0;i<61;i++)if(g101_records[i].role==role&&g101_records[i].index==index)return &g101_records[i];
 return NULL;
}
const uint8_t *ground101_base(const G101Record *r){return ready&&r?payload+r->base_offset:NULL;}
const G101FastContext *ground101_fast_context(void)
{return ready&&world.valid&&!world.rejected&&fast_world.valid?&fast_world:NULL;}
bool ground101_weights_disjoint(const G101Record *r,const uint8_t *weights,size_t bytes)
{
 if(!ready||!r||!weights||bytes!=G101_TILE_PIXELS)return false;
 bool member=false;for(unsigned i=0;i<61;i++)if(r==&g101_records[i])member=true;
 if(!member)return false;
 for(unsigned n=0;n<G101_TILE_PIXELS;n++)if(weights[n]&&
    (payload[r->mask_offset+n]||
     (r->generated_weight_offset&&payload[r->generated_weight_offset+n])||
     (r->ground_weight_offset&&payload[r->ground_weight_offset+n])))return false;
 return true;
}
void ground101_frame_reset(void)
{
 g101_fast_invalidate(&fast_world);g101_begin_frame(&world);map_base=NULL;map_bytes=map_stride=0;
#ifdef GROUND101_MATERIAL_TRACE
 terrain_draws=actor_draws=0;
#endif
}
bool ground101_layer1_preflight(const void *map,size_t bytes,const void *first,size_t stride,int x,int y)
{
 g101_fast_invalidate(&fast_world);
 if(!ready)return false;
 map_base=map;map_bytes=bytes;map_stride=stride;
 bool ok=g101_preflight_layer1(&world,map,bytes,first,stride,x,y);
 if(ok)ok=g101_fast_prepare(&fast_world,&world,&atlas,8);
#ifdef GROUND101_MATERIAL_TRACE
 if(ok){size_t index=((uintptr_t)first-(uintptr_t)map)/stride;first_row=(unsigned)(index/14);first_col=(unsigned)(index%14);first_x=x;first_y=y;}
#endif
 return ok;
}
int ground101_layer1_row(const void *cell,int x,int y)
{
 if(!ready||!world.valid||!map_base)return 0;
 uintptr_t base=(uintptr_t)map_base,p=(uintptr_t)cell;
 if(p<base||p-base>=map_bytes)return 0;
 if(g101_observe_row(&world,map_base,map_bytes,cell,map_stride,12,x,y))return 1;
 g101_fast_invalidate(&fast_world);return -1;
}
bool ground101_enemy_eligible(const G101EnemyContext *e,unsigned role,unsigned base)
{
 if(!ready||!world.valid||!fast_world.valid||!e||e->size!=1||e->score_item||e->independent_motion||!e->static_animation)return false;
 if(!((e->pool_slot>=25&&e->pool_slot<50)||(e->pool_slot>=75&&e->pool_slot<100)))return false;
 static const unsigned h2[8]={115,117,77,79,119,121,81,83};
 static const unsigned he[6]={1,3,5,39,41,43},dead[6]={7,9,11,45,47,49};
 if(role==101&&e->type>=121&&e->type<=128)
  return base==h2[e->type-121]&&e->availability==0&&!e->damaged;
 if(role==110&&e->type>=516&&e->type<=527) {
  unsigned n=(e->type-516)%6;
  if(base==he[n]&&e->availability==0&&!e->damaged)return true;
  return e->type>=522&&base==dead[n]&&e->availability==2&&e->damaged;
 }
 return false;
}
#ifdef GROUND101_MATERIAL_TRACE
void ground101_actor_trace(unsigned tick,const G101EnemyContext *e,unsigned role,unsigned base,int part,int filter,int x,int y,bool eligible)
{
 if(!actor_trace||!e||!ground101_record(role,base))return;
 int fx,fy;if(!g101_full_actor_origin(x,y,part,&fx,&fy))return;
 fprintf(actor_trace,"%u\t%u\t%u\t%u\t%d\t%u\t%u\t%d\t%d\t%d\t%d\t%" PRId64 "\t%" PRId64 "\t%d\n",tick,e->type,e->pool_slot,e->availability,e->damaged,role,base,part,filter,fx,fy,world.world_x,world.world_y,eligible);
}
void ground101_note_draw(const G101Record *r,bool actor)
{if(r){if(actor)++actor_draws;else ++terrain_draws;}}
#endif
void ground101_select(const G101Record *r,const uint8_t *accepted,unsigned n,int dx,int dy,uint8_t out[4])
{
 G101Pixel p={.accepted_rgba=accepted,.clean_rgba=payload+r->base_offset+n*4,
  .primary_weight=payload[r->mask_offset+n],
  .footer_weight=r->ground_weight_offset?payload[r->ground_weight_offset+n]:0,
  .generated_footer_rgba=r->generated_offset?payload+r->generated_offset+n*4:NULL,
  .generated_weight=r->generated_weight_offset?payload[r->generated_weight_offset+n]:0,
  .reconstruction_verified=true};
 g101_fast_select_pixel(&fast_world,&p,true,dx,dy,out);
}
#ifdef GROUND101_MATERIAL_TRACE
void ground101_frame_report(unsigned tick,const char *rejection)
{
 if(!trace||last_report==tick)return;
 last_report=tick;
 fprintf(trace,"%u\t%d\t%u\t%u\t%d\t%d\t%" PRId64 "\t%" PRId64 "\t%u\t%u\t%s\n",tick,world.valid,first_row,first_col,first_x,first_y,world.world_x,world.world_y,terrain_draws,actor_draws,rejection?rejection:"none");
 fflush(trace);
 if(actor_trace)fflush(actor_trace);
}

#endif
