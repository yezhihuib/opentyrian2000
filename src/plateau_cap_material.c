/* Additive finite material. FNV64 detects corruption, not authentication.
 * No lower bundle, HDA, gameplay state, RNG or per-frame allocations change. */
#include "plateau_cap_material.h"
#include "game_probe.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "plateau_cap_bundle_index.h"
static bool attempted,loaded,source_checked,source_valid;
static uint8_t *payload;
static uint32_t u32(const uint8_t *p)
{return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static bool valid_layout(const PCapRecord *records,size_t count,size_t bytes,unsigned base109_offset)
{
 static const unsigned ids[13]={96,97,98,99,100,106,107,108,109,110,118,119,120};
 static const unsigned slots[13]={227,228,229,201,202,203,204,230,205,206,207,208,209};
 if(!records||count!=13||bytes!=G101_ATLAS_BYTES+15u*G101_TILE_PIXELS)return false;
 size_t cursor=G101_ATLAS_BYTES;unsigned masks=0;
 for(unsigned i=0;i<13;i++) {
  const PCapRecord *r=records+i;
  if(r->index!=ids[i]||r->slot!=slots[i])return false;
  if(r->index==98||r->index==118) {if(r->mask_offset)return false;continue;}
  if(r->mask_offset!=cursor||cursor>bytes||G101_TILE_PIXELS>bytes-cursor)return false;
  cursor+=G101_TILE_PIXELS;++masks;
 }
 return masks==11&&base109_offset==cursor&&cursor<=bytes&&G101_TILE_PIXELS*4==bytes-cursor;
}
static bool valid_payload(const uint8_t *data,size_t bytes)
{
 if(!data||bytes!=PCAP_BUNDLE_PAYLOAD_BYTES)return false;
 for(unsigned n=3;n<G101_ATLAS_BYTES;n+=4)if(data[n]!=255)return false;
 for(unsigned i=0;i<13;i++) {
  const PCapRecord *r=&pcap_records[i];
  if(!r->mask_offset)continue; /*98/118 have no cap storage or sampling.*/
  const uint8_t *mask=data+r->mask_offset;bool nonempty=false;
  for(unsigned n=0;n<G101_TILE_PIXELS;n++) {
   if(mask[n])nonempty=true;
   if(r->index==109&&mask[n]!=255)return false;
   if((r->index==119||r->index==120)&&n>=184*192&&mask[n])return false;
  }
  if(!nonempty)return false;
  if(r->index!=109&&!ground101_weights_disjoint(ground101_record(201,r->index),mask,G101_TILE_PIXELS))return false;
 }
 return true;
}
#ifdef PLATEAU_CAP_MATERIAL_TEST
bool plateau_cap_test_layout(const PCapRecord *r,size_t n,size_t bytes,unsigned base)
{return valid_layout(r,n,bytes,base);}
bool plateau_cap_test_payload(const uint8_t *data,size_t bytes)
{return valid_payload(data,bytes);}
#endif
static bool exact_length(FILE *f,long bytes)
{return f&&!fseek(f,0,SEEK_END)&&ftell(f)==bytes&&!fseek(f,0,SEEK_SET);}
bool plateau_cap_bundle_load(const char *directory)
{
 /* Do not even attempt an allocation before the lower pass is verified and
  * preflighted. An absent/incompatible lower family disables dependent caps. */
 if(!ground101_fast_context())return false;
 if(attempted)return loaded;
 attempted=true;
 if(!directory||!*directory)return false;
 char path[1024];int length=snprintf(path,sizeof(path),"%s/plateau-cap-world-material.pcap",directory);
 if(length<0||(size_t)length>=sizeof(path))return false;
 if(PCAP_BUNDLE_RECORD_COUNT!=13||sizeof(pcap_records)/sizeof(*pcap_records)!=13||
    PCAP_BUNDLE_HEADER_BYTES!=32+13*12||
    PCAP_BUNDLE_PAYLOAD_BYTES>SIZE_MAX-PCAP_BUNDLE_HEADER_BYTES||
    PCAP_BUNDLE_FILE_BYTES!=PCAP_BUNDLE_HEADER_BYTES+PCAP_BUNDLE_PAYLOAD_BYTES||
    !valid_layout(pcap_records,13,PCAP_BUNDLE_PAYLOAD_BYTES,PCAP_BASE109_OFFSET))return false;
 FILE *f=fopen(path,"rb");uint8_t header[PCAP_BUNDLE_HEADER_BYTES];bool ok=false;
 if(!exact_length(f,PCAP_BUNDLE_FILE_BYTES))goto done;
 if(fread(header,1,sizeof(header),f)!=sizeof(header))goto done;
 if(memcmp(header,"PCAPAT1\0",8)||u32(header+8)!=1||u32(header+12)!=13||
    u32(header+16)!=768||u32(header+20)!=896||u32(header+24)!=8||u32(header+28)!=PCAP_BUNDLE_PAYLOAD_BYTES)goto done;
 for(unsigned i=0;i<13;i++) {
  const uint8_t *m=header+32+i*12;
  if(u32(m)!=201||u32(m+4)!=pcap_records[i].index||u32(m+8)!=(pcap_records[i].mask_offset!=0))goto done;
 }
 payload=malloc(PCAP_BUNDLE_PAYLOAD_BYTES);if(!payload)goto done;
 if(fread(payload,1,PCAP_BUNDLE_PAYLOAD_BYTES,f)!=PCAP_BUNDLE_PAYLOAD_BYTES||fgetc(f)!=EOF||ferror(f))goto done;
 uint64_t fingerprint=game_probe_hash(UINT64_C(14695981039346656037),header,sizeof(header));
 fingerprint=game_probe_hash(fingerprint,payload,PCAP_BUNDLE_PAYLOAD_BYTES);
 if(fingerprint!=PCAP_BUNDLE_FNV64||!valid_payload(payload,PCAP_BUNDLE_PAYLOAD_BYTES))goto done;
 ok=loaded=true;
done:
 if(f)fclose(f);
 if(!ok){free(payload);payload=NULL;}
 return loaded;
}
bool plateau_cap_verify_sources(PCapSourceLookup lookup,void *context)
{
 if(!loaded||!ground101_fast_context())return false;
 if(source_checked)return source_valid;
 source_checked=true;
 if(!lookup)return false;
 /* Recheck every selected enabled source and both guards, despite the ten
  * shared bases and guards already passing lower-family verification. */
 for(unsigned i=0;i<13;i++) {
  const PCapRecord *r=&pcap_records[i];
  const uint8_t *base=r->index==109?payload+PCAP_BASE109_OFFSET:ground101_base(ground101_record(201,r->index));
  const uint8_t *selected=lookup(r->index,r->slot,context);
  if(!base||!selected||memcmp(base,selected,G101_TILE_PIXELS*4))return false;
 }
 source_valid=true;return true;
}
const PCapRecord *plateau_cap_record(unsigned index)
{
 if(!loaded||!source_valid||!ground101_fast_context())return NULL;
 for(unsigned i=0;i<13;i++)if(pcap_records[i].index==index&&pcap_records[i].mask_offset)return &pcap_records[i];
 return NULL;
}
void plateau_cap_select(const PCapRecord *r,const uint8_t accepted[4],unsigned n,int x,int y,uint8_t out[4])
{
 memcpy(out,accepted,4);
 if(!loaded||!source_valid||!r||!r->mask_offset||n>=G101_TILE_PIXELS)return;
 g101_fast_select_cap(ground101_fast_context(),payload,accepted,payload[r->mask_offset+n],x,y,out);
}
