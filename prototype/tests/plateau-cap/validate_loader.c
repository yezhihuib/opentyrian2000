#include "plateau_cap_material.h"
#include "plateau_cap_bundle_index.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void *map[300][14];
static unsigned allocations;static size_t allocated;
void *__real_malloc(size_t);
void *__wrap_malloc(size_t n){allocations++;allocated+=n;return __real_malloc(n);}
static uint8_t source[4*G101_TILE_PIXELS],raw[PCAP_BUNDLE_PAYLOAD_BYTES];
static uint8_t lower_snapshot[61][G101_TILE_PIXELS*4];
static bool snapshot_taken;
static unsigned mismatch_id,callback_count;static const char *selected_pack;
static const uint8_t *selected(unsigned id,unsigned slot,void *context)
{
 (void)context;callback_count++;assert(slot<330);
 char path[4096];assert(snprintf(path,sizeof(path),"%s/terrain-shapesz-%u-8.hda",selected_pack,id)>0);
 FILE *f=fopen(path,"rb");if(!f)return NULL;
 uint8_t h[28];assert(fread(h,1,28,f)==28);assert(!memcmp(h,"HDR1",4));
 assert(fread(source,1,sizeof(source),f)==sizeof(source));assert(fgetc(f)==EOF);fclose(f);
 if(id==mismatch_id)source[0]^=1;
 return source;
}
static void layout(void)
{
 PCapRecord r[13];memcpy(r,pcap_records,sizeof(r));
 assert(plateau_cap_test_layout(r,13,3397632,3225600));
 assert(!plateau_cap_test_layout(NULL,13,3397632,3225600));
 assert(!plateau_cap_test_layout(r,12,3397632,3225600));assert(!plateau_cap_test_layout(r,14,3397632,3225600));
 assert(!plateau_cap_test_layout(r,13,3397631,3225600));assert(!plateau_cap_test_layout(r,13,SIZE_MAX,3225600));
 assert(!plateau_cap_test_layout(r,13,3397632,UINT32_MAX));
 for(unsigned i=0;i<13;i++) {
  memcpy(r,pcap_records,sizeof(r));r[i].index=1000;assert(!plateau_cap_test_layout(r,13,3397632,3225600));
  memcpy(r,pcap_records,sizeof(r));r[i].slot=330;assert(!plateau_cap_test_layout(r,13,3397632,3225600));
  memcpy(r,pcap_records,sizeof(r));r[i].mask_offset++;assert(!plateau_cap_test_layout(r,13,3397632,3225600));
 }
 memcpy(r,pcap_records,sizeof(r));r[1]=r[0];assert(!plateau_cap_test_layout(r,13,3397632,3225600));
}
static uint64_t lower_hash(void)
{
 uint64_t hash=14695981039346656037ULL;
 for(unsigned i=0;i<61;i++) {
  const G101Record *r=ground101_record_at(i);if(!r)continue;
  const uint8_t *base=ground101_base(r);
  for(unsigned n=0;n<G101_TILE_PIXELS;n++) {
   uint8_t out[4];ground101_select(r,base+n*4,n,(int)(n%192)+65,(int)(n/192)+71,out);
   if(snapshot_taken)assert(!memcmp(lower_snapshot[i]+n*4,out,4));
   else memcpy(lower_snapshot[i]+n*4,out,4);
   for(int c=0;c<4;c++)hash=(hash^out[c])*1099511628211ULL;
  }
 }
 snapshot_taken=true;return hash;
}
static void check_payload(void)
{
 assert(plateau_cap_test_payload(raw,sizeof(raw)));
 assert(!plateau_cap_test_payload(NULL,sizeof(raw)));assert(!plateau_cap_test_payload(raw,sizeof(raw)-1));
 raw[3]=254;assert(!plateau_cap_test_payload(raw,sizeof(raw)));raw[3]=255;
 for(unsigned i=0;i<13;i++)if(pcap_records[i].mask_offset) {
  unsigned off=pcap_records[i].mask_offset;
  if(pcap_records[i].index==109){raw[off]=254;assert(!plateau_cap_test_payload(raw,sizeof(raw)));raw[off]=255;continue;}
  const G101Record *r=ground101_record(201,pcap_records[i].index);assert(r);
  const uint8_t *lower=ground101_base(r)-r->base_offset;
  unsigned offsets[3]={r->mask_offset,r->generated_weight_offset,r->ground_weight_offset};
  for(unsigned k=0;k<3;k++)if(offsets[k]) {
   unsigned n=0;while(n<G101_TILE_PIXELS&&!lower[offsets[k]+n])n++;
   assert(n<G101_TILE_PIXELS&&raw[off+n]==0);raw[off+n]=1;
   assert(!plateau_cap_test_payload(raw,sizeof(raw)));raw[off+n]=0;
  }
 }
}
static void complete_pixels(void)
{
 unsigned tested=0,noncap=0,full=0,partial=0,protected_lower=0;
 for(unsigned i=0;i<13;i++) {
  const PCapRecord *p=&pcap_records[i];const PCapRecord *cap=plateau_cap_record(p->index);
  assert((cap!=NULL)==(p->mask_offset!=0));
  const G101Record *lower=ground101_record(201,p->index);
  const uint8_t *base=p->index==109?raw+PCAP_BASE109_OFFSET:ground101_base(lower);assert(base);
  for(unsigned n=0;n<G101_TILE_PIXELS;n++) {
   int x=(int)(n%192)+57,y=(int)(n/192)+67;uint8_t accepted[4],out[4],sample[4];
   if(lower)ground101_select(lower,base+4*n,n,x,y,accepted);else memcpy(accepted,base+4*n,4);
   plateau_cap_select(cap,accepted,n,x,y,out);
   unsigned w=cap?raw[p->mask_offset+n]:0;
   G101Context ctx={true,false,35,577};G101Atlas atlas={raw,G101_ATLAS_BYTES,768,896,8};
   assert(g101_sample(&ctx,&atlas,8,x,y,sample));
   assert(out[3]==accepted[3]);
   for(unsigned c=0;c<3;c++)assert(out[c]==(accepted[c]*(255-w)+sample[c]*w+127)/255);
   if(!w){assert(!memcmp(out,accepted,4));noncap++;}else if(w==255)full++;else partial++;
   if(lower) {
    const uint8_t *lp=ground101_base(lower)-lower->base_offset;
    if(lp[lower->mask_offset+n]||(lower->generated_weight_offset&&lp[lower->generated_weight_offset+n])||(lower->ground_weight_offset&&lp[lower->ground_weight_offset+n])) {
     assert(w==0&&!memcmp(out,accepted,4));protected_lower++;
    }
   }
   if(p->index==98||p->index==118)assert(!memcmp(out,accepted,4));
   if((p->index==119||p->index==120)&&n>=184*192)assert(!memcmp(out,accepted,4));
   tested++;
  }
 }
 assert(noncap&&full&&partial&&protected_lower);
 for(unsigned id=0;id<700;id++) {bool member=false;for(unsigned i=0;i<13;i++)if(pcap_records[i].index==id&&pcap_records[i].mask_offset)member=true;assert((plateau_cap_record(id)!=NULL)==member);}
 printf("PASS exact %u authored tile pixels: zero=%u full=%u partial=%u protected_lower=%u; guards retain lower material\n",tested,noncap,full,partial,protected_lower);
}
int main(int argc,char **argv)
{
 assert(argc==9);layout();assert(!allocations);
 const char *lower_pack=argv[1],*capdir=argv[2];selected_pack=argv[3];
 bool want_load=atoi(argv[4]),want_source=atoi(argv[5]),want_lower=atoi(argv[8]);unsigned want_alloc=(unsigned)atoi(argv[6]);mismatch_id=(unsigned)atoi(argv[7]);
 assert(!plateau_cap_record(109));
 assert(!plateau_cap_bundle_load(capdir)&&!allocations); /*dependent cap before lower must stay inert*/
 assert(ground101_bundle_load(lower_pack)==want_lower);
 if(want_lower)assert(ground101_layer1_preflight(map,sizeof(map),&map[20][2],sizeof(void *),13,-17));
 unsigned prior=allocations;size_t prior_bytes=allocated;uint64_t before=lower_hash();
 assert(plateau_cap_bundle_load(capdir)==want_load);assert(plateau_cap_bundle_load(capdir)==want_load);
 assert(allocations-prior==want_alloc&&allocated-prior_bytes==want_alloc*3397632u);
 assert(!plateau_cap_record(109)); /*bundle loaded alone is insufficient*/
 assert(plateau_cap_verify_sources(selected,NULL)==want_source);
 assert(plateau_cap_verify_sources(selected,NULL)==want_source);
 assert(lower_hash()==before);
 if(want_source) {
  assert(callback_count==13);char path[4096];snprintf(path,sizeof(path),"%s/plateau-cap-world-material.pcap",capdir);
  FILE *f=fopen(path,"rb");assert(f);assert(!fseek(f,PCAP_BUNDLE_HEADER_BYTES,SEEK_SET));assert(fread(raw,1,sizeof(raw),f)==sizeof(raw));fclose(f);
  check_payload();complete_pixels();
  const PCapRecord *r=plateau_cap_record(109);assert(r);uint8_t accepted[4]={3,5,7,127},out[4];
  plateau_cap_select(r,accepted,G101_TILE_PIXELS,0,0,out);assert(!memcmp(accepted,out,4));
  ground101_frame_reset();assert(!plateau_cap_record(109));plateau_cap_select(r,accepted,0,0,0,out);assert(!memcmp(accepted,out,4));
  assert(ground101_layer1_preflight(map,sizeof(map),&map[20][2],sizeof(void *),13,-17));assert(plateau_cap_record(109));
  assert(ground101_layer1_row(&map[21][2],13,12)==-1);assert(!plateau_cap_record(109));
 } else {
  for(unsigned id=0;id<700;id++)assert(!plateau_cap_record(id));
  uint8_t in[4]={19,37,73,127},out[4];plateau_cap_select(NULL,in,0,0,0,out);assert(!memcmp(in,out,4));
 }
 assert(allocations==prior+want_alloc&&allocated==prior_bytes+want_alloc*3397632u);
 printf("PASS cap load=%d sources=%d checks=%u allocations=%u bytes=%zu; all61 lower outputs byte-exact; no frame allocation\n",want_load,want_source,callback_count,allocations-prior,allocated-prior_bytes);
 return 0;
}
