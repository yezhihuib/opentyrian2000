#include "b313_continuity.h"
#include "b313_tail414.h"
#include "b313_v6_recovery.h"
#include "b313_v6_slice.h"
#include "building313_identity.h"
#include "building313_precommit.h"
#include "native_writer_lineage.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

static B313Status state;
static B313Group groups[B313_GROUP_CAPACITY];
static B313Call calls[B313_CALL_CAPACITY];
static uint64_t generations[B313_SLOT_COUNT],scene_nonce,group_nonce,call_nonce,frame_nonce;
static unsigned membership[B313_SLOT_COUNT]; /* group array index +1 */
static uint64_t pending_group,pending_call;
/* Pinned to tyrian.hdt fde850...a17745b, records313..316; IDENTITY-PINS.json. */
static const unsigned bases[4][3]={{191,195,199},{193,197,201},{153,157,161},{155,159,163}};
static bool enabled(void)
{
#if defined(BUILDING313_IDENTITY_DIAGNOSTIC) && BUILDING313_IDENTITY_DIAGNOSTIC
 const char *v=getenv("BUILDING313_IDENTITY_ENABLE");return v&&strcmp(v,"1")==0;
#else
 return false;
#endif
}
static void fail(unsigned reason){state.reasons|=reason;state.scene_valid=false;}
static bool next_nonce(uint64_t *p){if(*p==UINT64_MAX){fail(B313_OVERFLOW);return false;}++*p;return true;}
static B313Group *find_group(uint64_t nonce)
{
 if(!nonce)return NULL;
 for(unsigned i=0;i<state.groups;i++)if(groups[i].nonce==nonce&&groups[i].scene==state.scene)return &groups[i];
 return NULL;
}
static uint64_t building_lineage_lease;
static bool lineage_tag(uint64_t nonce,NwlIdentity *out)
{
 if(!nonce||!out)return false;
 for(unsigned i=0;i<state.calls;i++)if(calls[i].nonce==nonce){
  B313Call *c=&calls[i];B313Group *g=find_group(c->group);
  if(!g||g->scene!=state.scene||!g->complete||g->reasons||c->filter||!c->generation||c->slot>=100||generations[c->slot]!=c->generation)return false;
  *out=(NwlIdentity){state.scene,state.frame,c->group,c->nonce,c->generation,state.tick,c->slot,c->type,c->part,c->base,c->x,c->y};return true;
 }
 return false;
}
void b313_lineage_open(void)
{
 building_lineage_lease=0;
 if(!b313_sampling())return;
 building_lineage_lease=nwl_open(state.scene,state.frame,state.tick);
}
NwlToken b313_lineage_native_begin(uint64_t nonce,SDL_Surface *surface)
{
 if(!nonce)return (NwlToken){0,0};
 NwlIdentity id;
 if(!b313_sampling()||!lineage_tag(nonce,&id)){nwl_discard(NWL_IDENTITY);return (NwlToken){0,0};}
 return nwl_call_begin(building_lineage_lease,&id,surface);
}
void b313_lineage_native_end(NwlToken token){nwl_call_end(token);}
static void building_lineage_report(FILE *f)
{
 NwlStatus ls=nwl_status();unsigned joined=0,stores=0,unique=0,source=0,output=0,bottom_source=0,bottom_output=0;
 NwlResult result[B313_CALL_CAPACITY];memset(result,0,sizeof(result));
 for(unsigned i=0;i<state.calls;i++){
  NwlIdentity id;
  if(calls[i].ended&&lineage_tag(calls[i].nonce,&id))result[i]=nwl_query(building_lineage_lease,&id);
  if(result[i].available&&result[i].completed){
   joined++;stores+=result[i].stores;unique+=result[i].unique_cells;source+=result[i].source_owned;output+=result[i].output_owned;
   if((calls[i].type==313||calls[i].type==314)&&(calls[i].part==19||calls[i].part==20)){bottom_source+=result[i].last_row_source_owned;bottom_output+=result[i].last_row_output_owned;}
  }
 }
 bool intact=state.scene_valid&&state.identity_groups>0&&ls.enabled&&ls.valid&&ls.sealed&&state.calls==state.identity_groups*16&&joined==state.calls&&ls.calls==joined&&stores==state.calls*168&&unique==stores&&source==stores&&output==stores;
 fprintf(f,"{\"enabled\":%s,\"valid_subset\":%s,\"sealed\":%s,\"lease\":%llu,\"reasons\":%u,\"identity_calls\":%u,\"verified_native_calls\":%u,\"joined_calls\":%u,\"missing_joins\":%u,\"copy_rows\":%u,\"actual_store_events\":%u,\"unique_support_cells\":%u,\"source_cells_owned\":%u,\"output_cells_owned\":%u,\"bottom_row_source_cells_owned\":%u,\"bottom_row_output_cells_owned\":%u,\"observed_native_support_intact\":%s,\"ledger_complete\":false,\"old_hd_coverage_complete\":false,\"eligible\":false,\"calls\":[",ls.enabled?"true":"false",ls.valid?"true":"false",ls.sealed?"true":"false",(unsigned long long)ls.lease,ls.reasons,state.calls,ls.calls,joined,state.calls-joined,ls.copy_rows,stores,unique,source,output,bottom_source,bottom_output,intact?"true":"false");
 for(unsigned i=0;i<state.calls;i++)fprintf(f,"%s{\"identity_call\":%llu,\"joined\":%s,\"first_event\":%llu,\"last_event\":%llu,\"stores\":%u,\"unique_cells\":%u,\"source_owned\":%u,\"output_owned\":%u}",i?",":"",(unsigned long long)calls[i].nonce,result[i].available?"true":"false",(unsigned long long)result[i].first_event,(unsigned long long)result[i].last_event,result[i].stores,result[i].unique_cells,result[i].source_owned,result[i].output_owned);
 fputs("]}",f);
}

static unsigned phase(unsigned component,unsigned base)
{
 if(component<4)for(unsigned p=0;p<3;p++)if(bases[component][p]==base)return p;
 return 3;
}
static bool identity(const B313Snapshot *s,unsigned component)
{
 return s&&s->slot<B313_SLOT_COUNT&&s->type==313+component&&s->record==313+component&&s->record_verified&&s->graphics_verified&&s->bank==20&&s->pool<4&&s->sheet_identity&&s->data_identity&&s->avail==0&&s->size==1&&!s->damaged&&!s->scoreitem;
}
static bool unchanged(const B313Snapshot *a,const B313Snapshot *b)
{
 return a->slot==b->slot&&a->type==b->type&&a->record==b->record&&a->pool==b->pool&&a->bank==b->bank&&a->sheet_identity==b->sheet_identity&&a->data_identity==b->data_identity;
}
void b313_scene_end(void){nwl_discard(NWL_STALE);building_lineage_lease=0;state.tracking=false;state.sampling=false;state.scene_valid=false;pending_group=0;pending_call=0;}
void b313_scene_begin(bool target_scope)
{
 b313_scene_end();
 if(!target_scope||!enabled())return;
 memset(&state,0,sizeof(state));memset(groups,0,sizeof(groups));memset(calls,0,sizeof(calls));
 memset(generations,0,sizeof(generations));memset(membership,0,sizeof(membership));
 state.tracking=true;state.scene_valid=true;
 if(!next_nonce(&scene_nonce))return;
 state.scene=scene_nonce;
}
bool b313_tracking(void){return state.tracking;}
bool b313_sampling(void){return state.tracking&&state.sampling;}
void b313_frame_begin(unsigned tick,bool target_scope)
{
 if(!state.tracking)return;
 if(!target_scope){fail(B313_SCOPE);b313_scene_end();return;}
 if(pending_group||pending_call){fail(B313_CALL_TOKEN);pending_group=0;pending_call=0;}
 state.tick=tick;state.sampling=tick==b313_slice_tick();state.calls=0;state.identity_groups=0;state.enemy_blit_ordinal=0;
 if(!state.sampling)return;
 if(!next_nonce(&frame_nonce))return;
 state.frame=frame_nonce;
 memset(calls,0,sizeof(calls));
 for(unsigned i=0;i<state.groups;i++)for(unsigned c=0;c<4;c++){
  groups[i].identity_observed=false;groups[i].member[c].parts=0;groups[i].member[c].drawn=false;
 }
}
void b313_slot_allocated(unsigned slot)
{
 if(!state.tracking)return;
 if(slot>=B313_SLOT_COUNT){fail(B313_IDENTITY);return;}
 if(membership[slot]){groups[membership[slot]-1].reasons|=B313_REUSED;membership[slot]=0;}
 if(!next_nonce(&generations[slot]))return;
}
uint64_t b313_group_begin(unsigned event_loc,unsigned cur_loc,unsigned tick,int type,unsigned pool,unsigned link)
{
 if(!state.tracking||type!=313)return 0;
 if(!state.scene_valid)return 0;
 if(pending_group){fail(B313_CALL_TOKEN);return 0;}
 if(state.groups==B313_GROUP_CAPACITY||!next_nonce(&group_nonce)){fail(B313_OVERFLOW);return 0;}
 B313Group *g=&groups[state.groups++];memset(g,0,sizeof(*g));
 g->nonce=group_nonce;g->scene=state.scene;g->event_loc=event_loc;g->cur_loc=cur_loc;g->birth_tick=tick;g->pool=pool;g->link=link;
 pending_group=g->nonce;return g->nonce;
}
void b313_group_member(uint64_t nonce,unsigned component,unsigned slot1,const B313Snapshot *s)
{
 if(!state.tracking||!nonce)return;
 B313Group *g=find_group(nonce);
 if(!g||pending_group!=nonce||component>=4){fail(B313_CALL_TOKEN);return;}
 unsigned bit=1u<<component;
 if(g->members&bit){g->reasons|=B313_DUPLICATE;return;}
 g->members|=bit;
 if(!slot1||slot1>B313_SLOT_COUNT||!s||s->slot!=slot1-1||!identity(s,component)||!generations[slot1-1]){g->reasons|=B313_IDENTITY|B313_PARTIAL;return;}
 unsigned slot=slot1-1;
 if(membership[slot]){g->reasons|=B313_DUPLICATE;groups[membership[slot]-1].reasons|=B313_DUPLICATE;return;}
 B313Member *m=&g->member[component];m->slot=slot;m->generation=generations[slot];m->birth=*s;
 membership[slot]=(unsigned)(g-groups)+1;
}
void b313_group_end(uint64_t nonce)
{
 if(!state.tracking||!nonce)return;
 B313Group *g=find_group(nonce);
 if(!g||pending_group!=nonce){fail(B313_CALL_TOKEN);return;}
 pending_group=0;
 if(g->members!=15)g->reasons|=B313_PARTIAL;
 for(unsigned c=0;c<4;c++)if(!g->member[c].generation)g->reasons|=B313_PARTIAL;
 if(!g->reasons){
  int x=g->member[0].birth.ex,y=g->member[0].birth.ey;
  for(unsigned c=0;c<4;c++)if(g->member[c].birth.pool!=g->member[0].birth.pool||g->member[c].birth.sheet_identity!=g->member[0].birth.sheet_identity||g->member[c].birth.data_identity!=g->member[0].birth.data_identity)g->reasons|=B313_IDENTITY;
  for(unsigned c=0;c<4;c++)if((int64_t)g->member[c].birth.ex!=(int64_t)x+(c%2)*24||(int64_t)g->member[c].birth.ey!=(int64_t)y-(c/2)*28)g->reasons|=B313_GEOMETRY;
 }
 g->complete=!g->reasons;
 b313_recovery_birth(g);
 b313_tail414_birth(g);
 bco_group_complete(g);
}
uint64_t b313_draw_begin(const B313Snapshot *s,unsigned part,int x,int y,bool full_native_quad)
{
 if(!b313_sampling())return 0;
 if(!next_nonce(&call_nonce))return 0;
 state.enemy_blit_ordinal++;
 if(!s)return 0; /* Other enemy dispatch: ordinal only, no family claim. */
 if(pending_call){fail(B313_CALL_TOKEN);return 0;}
 if(state.calls==B313_CALL_CAPACITY){fail(B313_OVERFLOW);return 0;}
 B313Call *call=&calls[state.calls++];memset(call,0,sizeof(*call));
 call->nonce=call_nonce;call->slot=s->slot;call->type=s->type;call->record=s->record;call->pool=s->pool;call->bank=s->bank;
 call->base=s->base;call->filter=s->filter;call->cycle=s->cycle;call->part=part;call->x=x;call->y=y;
 pending_call=call_nonce;
 if(s->slot>=B313_SLOT_COUNT||!membership[s->slot]){fail(B313_UNBOUND);return call_nonce;}
 B313Group *g=&groups[membership[s->slot]-1];call->group=g->nonce;
 unsigned c=s->type>=313&&s->type<=316?s->type-313:4;
 if(c>=4||!identity(s,c)){g->reasons|=B313_IDENTITY;return call_nonce;}
 B313Member *m=&g->member[c];call->generation=generations[s->slot];
 if(m->generation!=generations[s->slot]||!unchanged(&m->birth,s)){g->reasons|=B313_IDENTITY;return call_nonce;}
 unsigned q=part==0?0:part==1?1:part==19?2:part==20?3:4;
 if(q==4){g->reasons|=B313_PARTIAL;return call_nonce;}
 if(m->parts&(1u<<q))g->reasons|=B313_DUPLICATE;
 m->parts|=1u<<q;
 unsigned p=phase(c,s->base);call->phase=p;
 if(p==3||s->cycle<1||s->cycle>20)g->reasons|=B313_PHASE;
 if(s->filter)g->reasons|=B313_FILTER;
 if(!full_native_quad)g->reasons|=B313_GEOMETRY;
 int64_t left=(int64_t)x-(q%2)*12,top=(int64_t)y-(q/2)*14;
 if(left<INT_MIN||left>INT_MAX||top<INT_MIN||top>INT_MAX){g->reasons|=B313_GEOMETRY;return call_nonce;}
 if(m->drawn&&(m->base!=s->base||m->phase!=p))g->reasons|=B313_PHASE;
 if(m->drawn&&(m->draw_x!=left||m->draw_y!=top))g->reasons|=B313_GEOMETRY;
 m->drawn=true;m->base=s->base;m->phase=p;m->draw_x=(int)left;m->draw_y=(int)top;
 return call_nonce;
}
void b313_draw_end(uint64_t nonce)
{
 if(!state.tracking||!nonce)return;
 if(!state.sampling||!pending_call||nonce!=pending_call||!state.calls||calls[state.calls-1].nonce!=nonce){fail(B313_CALL_TOKEN);return;}
 calls[state.calls-1].ended=true;pending_call=0;
}
bool b313_wants_slot(unsigned slot){return b313_sampling()&&slot<B313_SLOT_COUNT&&membership[slot]!=0;}
void b313_live_slot(unsigned slot,const B313Snapshot *s)
{
 if(!b313_wants_slot(slot))return;
 B313Group *g=&groups[membership[slot]-1];unsigned c=4;
 for(unsigned i=0;i<4;i++)if(g->member[i].generation&&g->member[i].slot==slot)c=i;
 if(c==4||!identity(s,c)||!unchanged(&g->member[c].birth,s)||generations[slot]!=g->member[c].generation)g->reasons|=B313_IDENTITY;
}
void b313_frame_end(unsigned tick)
{
 if(!b313_sampling())return;
 if(tick!=state.tick||pending_call||pending_group)fail(B313_CALL_TOKEN);
 for(unsigned i=0;i<state.groups;i++){
  B313Group *g=&groups[i];bool any=false;
  for(unsigned c=0;c<4;c++)any|=g->member[c].drawn;
  if(!any)continue;
  for(unsigned c=0;c<4;c++){
   B313Member *m=&g->member[c];
   if(!m->drawn||m->parts!=15)g->reasons|=B313_PARTIAL;
   if(m->drawn&&m->phase!=g->member[0].phase)g->reasons|=B313_PHASE;
   if(m->drawn&&((int64_t)m->draw_x!=(int64_t)g->member[0].draw_x+(c%2)*24||(int64_t)m->draw_y!=(int64_t)g->member[0].draw_y-(c/2)*28))g->reasons|=B313_GEOMETRY;
  }
  g->identity_observed=state.scene_valid&&g->complete&&!g->reasons;
  if(g->identity_observed)state.identity_groups++;
 }
 FILE *f=fopen(b313_slice_path(B313_REPORT_IDENTITY,false),"w");
 if(!f){fail(B313_IO);state.sampling=false;return;}
 fprintf(f,"{\n\"schema\":\"building313-identity-v1\",\"eligible\":false,\"ledger_complete\":false,\"old_hd_coverage_complete\":false,\"scene\":%llu,\"frame\":%llu,\"tick\":%u,\"scene_valid\":%s,\"reasons\":%u,\"identity_groups\":%u,\"enemy_blit_ordinal\":%llu,\"groups\":[",(unsigned long long)state.scene,(unsigned long long)state.frame,tick,state.scene_valid?"true":"false",state.reasons,state.identity_groups,(unsigned long long)state.enemy_blit_ordinal);
 for(unsigned i=0;i<state.groups;i++){
  B313Group *g=&groups[i];fprintf(f,"%s{\"nonce\":%llu,\"birth_tick\":%u,\"event_loc\":%u,\"cur_loc\":%u,\"allocation_pool_offset\":%u,\"link\":%u,\"complete_birth\":%s,\"identity_observed\":%s,\"reasons\":%u,\"members\":[",i?",":"",(unsigned long long)g->nonce,g->birth_tick,g->event_loc,g->cur_loc,g->pool,g->link,g->complete?"true":"false",g->identity_observed?"true":"false",g->reasons);
  for(unsigned c=0;c<4;c++){B313Member *m=&g->member[c];fprintf(f,"%s{\"component\":%u,\"slot\":%u,\"generation\":%llu,\"type\":%u,\"parts\":%u,\"base\":%u,\"phase\":%u}",c?",":"",c,m->slot,(unsigned long long)m->generation,m->birth.type,m->parts,m->base,m->phase);}fputs("]}",f);
 }
 fputs("],\"calls\":[",f);
 for(unsigned i=0;i<state.calls;i++){
  B313Call *c=&calls[i];fprintf(f,"%s{\"nonce\":%llu,\"group\":%llu,\"generation\":%llu,\"slot\":%u,\"type\":%u,\"record\":%u,\"sprite_pool\":%u,\"bank\":%u,\"base\":%u,\"phase\":%u,\"cycle\":%u,\"part\":%u,\"filter\":%u,\"x\":%d,\"y\":%d,\"ended\":%s}",i?",":"",(unsigned long long)c->nonce,(unsigned long long)c->group,(unsigned long long)c->generation,c->slot,c->type,c->record,c->pool,c->bank,c->base,c->phase,c->cycle,c->part,c->filter,c->x,c->y,c->ended?"true":"false");
 }
 fputs("],\"native_lineage\":",f);building_lineage_report(f);fputs("}\n",f);fclose(f);state.sampling=false;
}
B313Status b313_status(void){return state;}
bool b313_get_group(unsigned i,B313Group *out){if(i>=state.groups||!out)return false;*out=groups[i];return true;}
bool b313_get_call(unsigned i,B313Call *out){if(i>=state.calls||!out)return false;*out=calls[i];return true;}
#ifdef B313_TESTING
void b313_test_reset(void){memset(&state,0,sizeof(state));memset(groups,0,sizeof(groups));memset(calls,0,sizeof(calls));memset(membership,0,sizeof(membership));memset(generations,0,sizeof(generations));scene_nonce=group_nonce=call_nonce=frame_nonce=pending_group=pending_call=0;}
void b313_test_nonces(uint64_t scene,uint64_t group,uint64_t call){scene_nonce=scene;group_nonce=group;call_nonce=call;}
#endif

#if defined(BUILDING313_PRECOMMIT_DIAGNOSTIC) && BUILDING313_PRECOMMIT_DIAGNOSTIC
/* Pure current-prefix identity view: do not finish the frame or change flags. */
bool b313_precommit_identity(B313PreIdentity *out)
{
 if(b313_recovery_enabled()&&state.tick==411&&!b313_recovery_continuity())return false;
 if(b313_tail414_enabled()&&state.tick==414&&!b313_tail414_continuity414())return false;
 if(!out||!state.tracking||!state.sampling||!state.scene_valid||state.reasons||state.tick!=b313_slice_tick()||
  !state.scene||!state.frame||state.calls!=16||state.groups>B313_GROUP_CAPACITY||pending_group||pending_call)return false;
 const B313Group *g=NULL;unsigned drawn=0;
 for(unsigned i=0;i<state.groups;i++){
  bool any=false;for(unsigned c=0;c<4;c++)any|=groups[i].member[c].drawn;
  if(any){g=groups+i;++drawn;}
 }
 if(drawn!=1||!g||g->scene!=state.scene||!g->nonce||!g->complete||g->reasons||g->members!=15)return false;
 for(unsigned c=0;c<4;c++){
  const B313Member *m=g->member+c;B313Snapshot live;
  if(!m->drawn||m->parts!=15||m->slot>=B313_SLOT_COUNT||!m->generation||
   generations[m->slot]!=m->generation||membership[m->slot]!=(unsigned)(g-groups)+1||
   !b313_precommit_read_live(m->slot,&live)||!identity(&live,c)||!unchanged(&m->birth,&live)||
   m->phase!=g->member[0].phase||m->phase>=3||
   (int64_t)m->draw_x!=(int64_t)g->member[0].draw_x+(c%2)*24||
   (int64_t)m->draw_y!=(int64_t)g->member[0].draw_y-(c/2)*28)return false;
 }
 unsigned seen[4]={0};
 for(unsigned i=0;i<16;i++){
  const B313Call *c=calls+i;
  if(!c->ended||!c->nonce||c->group!=g->nonce||c->type<313||c->type>316||c->record!=c->type||c->filter||c->bank!=20)return false;
  unsigned component=c->type-313,q=c->part==0?0:c->part==1?1:c->part==19?2:c->part==20?3:4;
  const B313Member *m=g->member+component;
  if(q==4||seen[component]&(1u<<q)||c->slot!=m->slot||c->generation!=m->generation||
   c->pool!=m->birth.pool||c->base!=m->base||c->phase!=m->phase||
   (int64_t)c->x!=(int64_t)m->draw_x+(q%2)*12||(int64_t)c->y!=(int64_t)m->draw_y+(q/2)*14)return false;
  for(unsigned j=0;j<i;j++)if(calls[j].nonce==c->nonce)return false;
  seen[component]|=1u<<q;
 }
 for(unsigned c=0;c<4;c++)if(seen[c]!=15)return false;
 memset(out,0,sizeof(*out));out->state=state;out->group=*g;memcpy(out->calls,calls,sizeof(out->calls));return true;
}
#endif

#if defined(B313_V6_RECOVERY_DIAGNOSTIC) && B313_V6_RECOVERY_DIAGNOSTIC
bool b313_identity_reacquire(void)
{
 B313Group birth;uint64_t continuous[100];
 if(state.tracking||state.sampling||state.scene_valid||pending_group||pending_call||
    !b313_recovery_take(&birth,continuous)||!b313_recovery_continuity())return false;
 if(scene_nonce==UINT64_MAX||group_nonce==UINT64_MAX){fail(B313_OVERFLOW);return false;}
 for(unsigned c=0;c<4;c++){
  const B313Member *m=&birth.member[c];B313Snapshot live;unsigned link=0;
  if(m->slot>=100||!m->generation||continuous[m->slot]!=m->generation||
     !b313_recovery_read_slot(m->slot,&live,&link)||link!=20||!identity(&live,c)||!unchanged(&m->birth,&live))return false;
 }
 b313_scene_end();
 memset(&state,0,sizeof(state));memset(groups,0,sizeof(groups));memset(calls,0,sizeof(calls));memset(membership,0,sizeof(membership));
 memcpy(generations,continuous,sizeof(generations));
 state.scene=++scene_nonce;state.groups=1;state.tracking=true;state.scene_valid=true;
 B313Group *g=groups;g->scene=state.scene;g->nonce=++group_nonce;
 g->event_loc=birth.event_loc;g->cur_loc=birth.cur_loc;g->birth_tick=birth.birth_tick;g->pool=birth.pool;g->link=birth.link;g->members=15;g->complete=true;
 for(unsigned c=0;c<4;c++){g->member[c].slot=birth.member[c].slot;g->member[c].generation=birth.member[c].generation;g->member[c].birth=birth.member[c].birth;membership[g->member[c].slot]=1;}
 return true;
}
bool b313_identity_tail414_reacquire(void)
{
 B313Group birth;uint64_t continuous[100];
 if(state.tracking||state.sampling||state.scene_valid||pending_group||pending_call||
    !b313_tail414_take(&birth,continuous)||!b313_tail414_continuity414())return false;
 if(scene_nonce==UINT64_MAX||group_nonce==UINT64_MAX){fail(B313_OVERFLOW);return false;}
 for(unsigned c=0;c<4;c++){
  const B313Member *m=&birth.member[c];B313Snapshot live;unsigned link=0;
  if(m->slot>=100||!m->generation||continuous[m->slot]!=m->generation||
     !b313_recovery_read_slot(m->slot,&live,&link)||link!=20||!identity(&live,c)||!unchanged(&m->birth,&live))return false;
 }
 b313_scene_end();
 memset(&state,0,sizeof(state));memset(groups,0,sizeof(groups));memset(calls,0,sizeof(calls));memset(membership,0,sizeof(membership));
 memcpy(generations,continuous,sizeof(generations));
 state.scene=++scene_nonce;state.groups=1;state.tracking=true;state.scene_valid=true;
 B313Group *g=groups;g->scene=state.scene;g->nonce=++group_nonce;
 g->event_loc=birth.event_loc;g->cur_loc=birth.cur_loc;g->birth_tick=birth.birth_tick;g->pool=birth.pool;g->link=birth.link;g->members=15;g->complete=true;
 for(unsigned c=0;c<4;c++){g->member[c].slot=birth.member[c].slot;g->member[c].generation=birth.member[c].generation;g->member[c].birth=birth.member[c].birth;membership[g->member[c].slot]=1;}
 return true;
}
#endif
