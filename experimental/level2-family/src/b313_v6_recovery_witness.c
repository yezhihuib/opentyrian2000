#include "b313_v6_recovery_witness.h"
#if defined(B313_V6_RECOVERY_DIAGNOSTIC) && B313_V6_RECOVERY_DIAGNOSTIC
#include "b313_v6_recovery.h"
#include <stdlib.h>
#include <string.h>
#include <limits.h>
enum {RW_ORDER=1u,RW_IDENTITY=2u,RW_ALLOCATION=4u,RW_RESOURCE=8u,RW_EVENT=16u,RW_OVERFLOW=32u,RW_READER=64u};
static B313RecoveryStatus s;
static bool initialized,enabled,begun;
static uint64_t generation[100],anchor_serial,anchor_resources[4],birth_resource;
static B313Group birth_fact;
static bool anchor_prepared;
static uint64_t prepared_serial,prepared_resources[4],prepared_group,prepared_scene;
static const unsigned bases[4][3]={{191,195,199},{193,197,201},{153,157,161},{155,159,163}};
static bool fail(unsigned why){s.failed=true;s.reasons|=why;return false;}
bool b313_recovery_enabled(void)
{
 if(!initialized){const char *v=getenv("BUILDING313_V6_RECOVERY_ENABLE");enabled=v&&!strcmp(v,"1");initialized=true;}
 return enabled;
}
static bool live(void){return b313_recovery_enabled()&&s.active&&!s.failed;}
static bool bump(uint64_t *v){if(*v==UINT64_MAX)return fail(RW_OVERFLOW);++*v;return true;}
void b313_recovery_lifetime_begin(bool target)
{
 if(!b313_recovery_enabled())return;
 if(begun||!target){fail(RW_ORDER);return;}
 begun=true;s.active=true; /* Resource epochs survive this boundary. */
}
void b313_recovery_lifetime_end(void)
{
 if(!b313_recovery_enabled())return;
 s.active=false;if(begun)fail(RW_ORDER); /* Not a permit-revocation callback. */
}
void b313_recovery_allocated(unsigned slot)
{
 if(!b313_recovery_enabled()||s.failed)return;
 if(!s.active||slot>=100){fail(RW_ALLOCATION);return;}
 if(!bump(&s.allocation_serial)||!bump(&generation[slot]))return;
 if(s.anchored)fail(RW_ALLOCATION);
}
void b313_recovery_resource(unsigned pool)
{
 if(!b313_recovery_enabled()||s.failed)return;
 if(pool>=4){fail(RW_RESOURCE);return;}
 if(!bump(&s.resource_epoch[pool]))return;
 if(s.anchored)fail(RW_RESOURCE);
}
static bool identity_source(const B313Snapshot *v,unsigned c)
{
 return v&&c<4&&v->slot==25+c&&v->type==313+c&&v->record==313+c&&v->record_verified&&v->graphics_verified&&
  v->avail==0&&v->size==1&&!v->damaged&&!v->scoreitem&&!v->filter&&v->bank==20&&v->pool<4&&
  v->sheet_identity&&v->data_identity;
}
static bool identity(const B313Snapshot *v,unsigned c)
{return identity_source(v,c)&&v->cycle>=1&&v->cycle<=20;}
static bool same_source(const B313Snapshot *a,const B313Snapshot *b)
{
 return a->slot==b->slot&&a->type==b->type&&a->record==b->record&&a->pool==b->pool&&a->bank==b->bank&&
  a->sheet_identity==b->sheet_identity&&a->data_identity==b->data_identity;
}
void b313_recovery_birth(const B313Group *g)
{
 if(!live())return;
 if(s.birth_seen||!g||!g->complete||g->reasons||g->members!=15||!g->nonce||!g->scene||g->birth_tick!=244||g->cur_loc!=244||g->event_loc!=18||g->link!=20||g->pool!=25){fail(RW_IDENTITY);return;}
 for(unsigned c=0;c<4;c++){
  const B313Member *m=&g->member[c];B313Snapshot current;unsigned link=0;
  /* Birth is the fixed animate1 constructor, before the first draw advances0->1.
   * It is not a drawable phase and cannot replace the live-cycle check above. */
  if(m->slot!=25+c||m->generation!=1||generation[25+c]!=1||!identity_source(&m->birth,c)||m->birth.cycle!=0||m->birth.base!=0||
   !b313_recovery_read_birth(m->slot,&current,&link)||link!=20||!identity_source(&current,c)||
   current.cycle!=0||current.base!=0||!same_source(&m->birth,&current)||current.ex!=m->birth.ex||current.ey!=m->birth.ey||
   m->birth.pool!=g->member[0].birth.pool||m->birth.sheet_identity!=g->member[0].birth.sheet_identity||
   m->birth.data_identity!=g->member[0].birth.data_identity||
   (int64_t)m->birth.ex!=(int64_t)g->member[0].birth.ex+(c%2)*24||
   (int64_t)m->birth.ey!=(int64_t)g->member[0].birth.ey-(c/2)*28){fail(RW_IDENTITY);return;}
 }
 birth_resource=s.resource_epoch[g->member[0].birth.pool];
 if(!birth_resource){fail(RW_RESOURCE);return;}
 birth_fact=*g;s.birth_seen=true;
}
static bool scan(unsigned tick)
{
 s.census_reads=0;s.census_members=0;
 memset(s.current,0,sizeof(s.current));memset(s.current_links,0,sizeof(s.current_links));memset(s.slot_generation,0,sizeof(s.slot_generation));
 unsigned seen=0;B313Snapshot first;memset(&first,0,sizeof(first));
 for(unsigned slot=0;slot<100;slot++){
  B313Snapshot v;unsigned link=0;memset(&v,0,sizeof(v));
  ++s.census_reads;
  if(!b313_recovery_read_slot(slot,&v,&link)||v.slot!=slot||v.avail>2)return fail(RW_READER);
  bool expected=slot>=25&&slot<=28;
  bool target=v.avail==0&&v.type>=313&&v.type<=316;
  if(expected!=target)return fail(RW_IDENTITY);
  if(!target)continue;
  unsigned c=slot-25;
  s.current[c]=v;s.current_links[c]=link;s.slot_generation[c]=generation[slot];++s.census_members;
  if(!identity(&v,c)||link!=20||generation[slot]!=birth_fact.member[c].generation||
   !same_source(&birth_fact.member[c].birth,&v)||s.resource_epoch[v.pool]!=birth_resource||
   v.base!=bases[c][tick==409?1:2])return fail(RW_IDENTITY);
  if(!c)first=v;
  if((int64_t)v.ex!=(int64_t)first.ex+(c%2)*24||(int64_t)v.ey!=(int64_t)first.ey-(c/2)*28)return fail(RW_IDENTITY);
  seen|=1u<<c;
 }
 return seen==15&&s.census_reads==100&&s.census_members==4?true:fail(RW_IDENTITY);
}
static bool validate_anchor(const B313Group *g)
{
 if(!live())return false;
 if(!s.birth_seen||s.anchored||!g||!g->complete||g->reasons||g->members!=15||g->nonce!=birth_fact.nonce||g->scene!=birth_fact.scene||
  g->birth_tick!=244||g->cur_loc!=244||g->event_loc!=18||g->link!=20||g->pool!=25)return fail(RW_ORDER);
 for(unsigned c=0;c<4;c++){
  const B313Member *m=&g->member[c];
  if(m->slot!=25+c||m->generation!=1||!m->drawn||m->parts!=15||m->phase!=1||m->base!=bases[c][1]||
   !same_source(&m->birth,&birth_fact.member[c].birth)||
   (int64_t)m->draw_x!=(int64_t)g->member[0].draw_x+(c%2)*24||
   (int64_t)m->draw_y!=(int64_t)g->member[0].draw_y-(c/2)*28)return fail(RW_IDENTITY);
 }
 return scan(409);
}
bool b313_recovery_anchor_prepare(const B313Group *g)
{
 if(!b313_conservative_enabled()||anchor_prepared||!validate_anchor(g))return fail(RW_ORDER);
 prepared_serial=s.allocation_serial;memcpy(prepared_resources,s.resource_epoch,sizeof(prepared_resources));
 prepared_group=g->nonce;prepared_scene=g->scene;anchor_prepared=true;return true;
}
bool b313_recovery_anchor(const B313Group *g)
{
 if(!validate_anchor(g))return false;
 if(b313_conservative_enabled()&&(!anchor_prepared||g->nonce!=prepared_group||g->scene!=prepared_scene||
  s.allocation_serial!=prepared_serial||memcmp(prepared_resources,s.resource_epoch,sizeof(prepared_resources))))return fail(RW_ORDER);
 anchor_serial=s.allocation_serial;memcpy(anchor_resources,s.resource_epoch,sizeof(anchor_resources));
 s.anchor_serial=anchor_serial;memcpy(s.anchor_resources,anchor_resources,sizeof(anchor_resources));s.anchored=true;s.last_census=409;return true;
}
void b313_recovery_event(unsigned tick,unsigned event_loc,unsigned cur_loc,unsigned type,int d1,int d2,int d3,int d4,int d5,int d6)
{
 if(!b313_recovery_enabled()||s.failed)return;
 if(tick<409){if(s.anchored)fail(RW_ORDER);return;}
 if(!live()||!s.anchored||tick!=410||s.event_seen||s.census410||event_loc!=35||cur_loc!=410||type!=19||d1!=0||d2!=-1||d3!=0||d4!=1||d5!=7||d6!=0){fail(RW_EVENT);return;}
 s.event_seen=true;s.event_cur_loc=cur_loc;
}
bool b313_recovery_census(unsigned tick)
{
 if(!live())return false;
 if(!s.anchored||!s.event_seen||(tick!=410&&tick!=411)||
  (tick==410&&(s.census410||s.census411||s.taken))||(tick==411&&!s.census410))return fail(RW_ORDER);
 if(s.allocation_serial!=anchor_serial)return fail(RW_ALLOCATION);
 for(unsigned i=0;i<4;i++)if(s.resource_epoch[i]!=anchor_resources[i])return fail(RW_RESOURCE);
 if(!scan(tick))return false;
 s.last_census=tick;if(tick==410)s.census410=true;else s.census411=true;return true;
}
bool b313_recovery_take(B313Group *out,uint64_t gens[100])
{
 if(!live())return false;
 if(!out||!gens||s.taken||!s.census411||s.last_census!=411)return fail(RW_ORDER);
 if(!b313_recovery_census(411))return false;
 *out=birth_fact;memcpy(gens,generation,sizeof(generation));s.taken=true;return true;
}
bool b313_recovery_continuity(void)
{
 if(!live())return false;
 if(!s.taken)return fail(RW_ORDER);
 return b313_recovery_census(411);
}
B313RecoveryStatus b313_recovery_status(void){return s;}
#else
typedef int b313_v6_recovery_witness_disabled_translation_unit;
#endif
