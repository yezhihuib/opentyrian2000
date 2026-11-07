#include "b313_v6_slice.h"
#include "b313_v6_binding.h"
#ifndef B313_V6_BINDING_DIAGNOSTIC
#define B313_V6_BINDING_DIAGNOSTIC 0
#endif
#if B313_V6_BINDING_DIAGNOSTIC
#include "b313_v6_catalog.h"
#include <string.h>
/* Pinned to frozen building313_identity.c:15 and v6 static inventory. */
static const unsigned bases[4][3]={{191,195,199},{193,197,201},{153,157,161},{155,159,163}};
static uint64_t generation;
static bool active;
static unsigned phase_of(unsigned component,unsigned base)
{
 for(unsigned p=0;p<3;p++)if(bases[component][p]==base)return p;
 return 3;
}
static bool valid_context(const B313V6Context *c)
{
 if(!c||c->tick!=b313_slice_tick()||!c->scene||!c->frame||!c->group||!c->native_epoch||!c->sample_epoch||!c->sequence)return false;
 unsigned phase=3;
 for(unsigned i=0;i<4;i++){
  const B313V6Member *m=c->member+i;
  if(m->type!=313+i||m->record!=313+i||m->bank!=20||m->pool>=4||m->pool!=c->member[0].pool||m->slot>=100||!m->slot_generation)return false;
  for(unsigned j=0;j<i;j++)if(c->member[j].slot==m->slot)return false;
  unsigned p=phase_of(i,m->base);
  if(p>=3||(i&&p!=phase))return false;
  phase=p;
 }
 /* Only the immutable tick/phase table can select a loaded phase. */
 return phase==b313_slice_phase()&&phase<3;
}
static bool same_context(const B313V6Context *a,const B313V6Context *b)
{
 if(a->scene!=b->scene||a->frame!=b->frame||a->group!=b->group||a->tick!=b->tick||
  a->native_epoch!=b->native_epoch||a->sample_epoch!=b->sample_epoch||a->sequence!=b->sequence)return false;
 for(unsigned i=0;i<4;i++){
  const B313V6Member *x=a->member+i,*y=b->member+i;
  if(x->type!=y->type||x->record!=y->record||x->bank!=y->bank||x->pool!=y->pool||x->slot!=y->slot||x->base!=y->base||x->slot_generation!=y->slot_generation)return false;
 }
 return true;
}
bool b313_v6_catalogue_activate(const char *expected_content_sha256)
{
 active=false;
 if(!expected_content_sha256||strcmp(expected_content_sha256,B313_V6_CATALOG_SHA256)||generation==UINT64_MAX)return false;
 ++generation;active=true;return true;
}
void b313_v6_catalogue_close(void){active=false;}
uint64_t b313_v6_catalogue_generation(void){return active?generation:0;}
bool b313_v6_select_slice(const B313V6Context *context,B313V6Binding *out)
{
 if(!out)return false;
 memset(out,0,sizeof(*out));
 if(!active||!b313_slice_payload_sha()||!valid_context(context))return false;
 out->metadata_match=true;out->binding_input_origin=B313_V6_INPUT_FIXTURE;
 out->catalogue_index=b313_slice_phase();out->phase=b313_slice_phase();out->width=384;out->height=448;out->density=8;out->pitch=1536;
 out->format=B313_V6_FORMAT_ARGB32_LE;out->pack_generation=generation;
 memcpy(out->catalogue_sha256,B313_V6_CATALOG_SHA256,sizeof(out->catalogue_sha256));
 memcpy(out->payload_sha256,b313_slice_payload_sha(),sizeof(out->payload_sha256));
 out->context=*context;
 /* Both runtime flags remain false. This is not a consumable rendering token. */
 return true;
}
bool b313_v6_binding_matches(const B313V6Context *current,const B313V6Binding *saved)
{
 if(!b313_slice_payload_sha()||!saved||!saved->metadata_match||saved->runtime_eligible||saved->v6_runtime_validated||
  saved->binding_input_origin!=B313_V6_INPUT_FIXTURE||!active||saved->pack_generation!=generation||
  saved->catalogue_index!=b313_slice_phase()||saved->phase!=b313_slice_phase()||saved->width!=384||saved->height!=448||saved->density!=8||saved->pitch!=1536||saved->format!=B313_V6_FORMAT_ARGB32_LE)return false;
 if(memcmp(saved->catalogue_sha256,B313_V6_CATALOG_SHA256,sizeof(saved->catalogue_sha256))||
  memcmp(saved->payload_sha256,b313_slice_payload_sha(),sizeof(saved->payload_sha256)))return false;
 return valid_context(current)&&same_context(current,&saved->context);
}
#else
bool b313_v6_catalogue_activate(const char *id){(void)id;return false;}
void b313_v6_catalogue_close(void){}
uint64_t b313_v6_catalogue_generation(void){return 0;}
bool b313_v6_select_slice(const B313V6Context *c,B313V6Binding *out){(void)c;if(out)*out=(B313V6Binding){0};return false;}
bool b313_v6_binding_matches(const B313V6Context *c,const B313V6Binding *s){(void)c;(void)s;return false;}
#endif
