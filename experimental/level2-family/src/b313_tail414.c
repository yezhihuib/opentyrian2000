/* Independent observation only. Never exports an old renderer lease or permission. */
#include "b313_tail414.h"
#include "b313_continuity.h"
#include "b313_continuity_link.h"
#include "b313_continuity_report.h"
#include "b313_v6_recovery.h"
#include "varz.h"
#include "config.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <inttypes.h>
#include <limits.h>
enum {T_ORDER=1,T_IDENTITY=2,T_ALLOC=4,T_RESOURCE=8,T_EVENT=16,T_OVERFLOW=32,T_IO=64};
static B313Tail414Status s;
static bool initialized,started,frame_open,continuity_mode;
static B313Group birth;
static uint64_t birth_resources[4];
static Sprite2_array resource_shapes[4];
static Uint8 resource_banks[4];
static JE_MultiEnemyType expected;
static JE_byte expected_avail[100];
static unsigned expected_alloc,expected_entry,expected_type;
static int expected_args[6];
static bool mode_two,mode_one,mode_super;
static unsigned mode_arcade;
static const struct {unsigned tick,entry,type;int a[6];} events[]={
 {410,35,19,{0,-1,0,1,7,0}},
 {412,36,10,{194,-6,0,3,0,0}}, {412,37,10,{194,282,0,5,0,0}},
 {412,38,19,{2,0,0,3,5,0}}, {412,39,19,{-2,0,0,5,4,0}},
 {412,40,33,{512,0,0,5,0,0}}, {412,41,45,{619,0,0,5,0,0}},
 {412,42,45,{628,0,0,3,0,0}}, {413,43,19,{0,-2,0,1,7,0}}
};
/* Diagnostics only. Captured once; never consulted by any admission predicate. */
static struct {bool captured,tick_known,event_domain_known,event_type_known,birth_seen,anchored;unsigned tick,domain,type,reason,origin,observed_tick;uint64_t allocation_serial;} first_rejection;
enum {TF_INTERNAL=0,TF_EXTERNAL_DETAILED=1,TF_EXTERNAL_LEGACY=2,TF_CONTROLLER_CANCEL=3};
static void remember_rejection(unsigned reason,unsigned tick,unsigned domain,unsigned type,unsigned origin,bool tick_known,bool type_known)
{
 if(first_rejection.captured)return;
 first_rejection.captured=true;first_rejection.tick=tick;first_rejection.domain=domain;first_rejection.type=type;first_rejection.reason=reason;first_rejection.origin=origin;first_rejection.tick_known=tick_known;first_rejection.event_type_known=type_known;first_rejection.event_domain_known=origin==TF_EXTERNAL_DETAILED&&domain>=1&&domain<=4;first_rejection.birth_seen=s.birth_seen;first_rejection.anchored=s.anchored;first_rejection.observed_tick=s.tick;first_rejection.allocation_serial=s.allocation_serial;
}
/* Only describes the first rejected service window event's actual switch path.
 * The capture result is never used to choose a game handler or grant permission. */
static struct {bool captured,completed,focus_before,focus_after;unsigned tick,window_id,subtype,handler_branch;} first_window_dispatch;
bool b313_tail414_window_dispatch_begin(unsigned tick,unsigned domain,unsigned type,unsigned window_id,unsigned subtype,bool focus_before)
{
 if(first_window_dispatch.captured||!first_rejection.captured||first_rejection.origin!=TF_EXTERNAL_DETAILED||!first_rejection.tick_known||!first_rejection.event_domain_known||!first_rejection.event_type_known||first_rejection.tick!=tick||first_rejection.domain!=domain||domain!=B313_INPUT_SERVICE||first_rejection.type!=type||type!=SDL_WINDOWEVENT)return false;
 first_window_dispatch.captured=true;first_window_dispatch.tick=tick;first_window_dispatch.window_id=window_id;first_window_dispatch.subtype=subtype;first_window_dispatch.focus_before=focus_before;return true;
}
void b313_tail414_window_dispatch_end(bool recorded,unsigned handler_branch,bool focus_after)
{
 if(!recorded||!first_window_dispatch.captured||first_window_dispatch.completed)return;
 first_window_dispatch.handler_branch=handler_branch;first_window_dispatch.focus_after=focus_after;first_window_dispatch.completed=true;
}
static bool fail(unsigned r){remember_rejection(r,s.tick,0,0,TF_INTERNAL,false,false);s.failed=true;s.reasons|=r;s.active=false;s.candidate_ready=false;return false;}
bool b313_tail414_enabled(void)
{
 if(!initialized){
  initialized=true;
  const char *v=getenv("BUILDING313_TAIL414_PREFLIGHT_ENABLE");
  const char *mode=getenv("BUILDING313_TAIL414_CONTINUITY_ENABLE");
  const char *ind=getenv("BUILDING313_CONTINUITY_INDEPENDENT_ENABLE");
  continuity_mode=mode&&strcmp(mode,"0")!=0;
  if(continuity_mode){
   s.enabled=true;
   /* Parse only configuration here. Never recurse through bco_enabled. */
   if(strcmp(mode,"1")||!ind||strcmp(ind,"1")||(v&&strcmp(v,"0"))||!b313_conservative_enabled())fail(T_ORDER);
  }else s.enabled=v&&!strcmp(v,"1")&&b313_conservative_enabled();
 }
 return s.enabled;
}
static bool bridge_counts(const BcoStatus *c)
{return c->serial==s.allocation_serial&&!memcmp(c->generation,s.generation,sizeof(s.generation))&&!memcmp(c->resources,s.resource_epoch,sizeof(s.resource_epoch));}
static bool bridge_live(const BcoStatus *c)
{
 BcoLinkStatus a=bco_link_status();BcoReportStatus r=bco_report_status();
 return c->enabled&&c->session==1&&!c->failed&&!c->consumption.failed&&!c->consumption.interrupted&&!c->consumption.pending&&a.independent_requested&&a.configuration_valid&&!a.configuration_conflict&&!r.io_failed;
}
static bool bridge_birth(const B313Group *g)
{
 if(!continuity_mode)return true;
 BcoStatus c=bco_status();BcoReportStatus r=bco_report_status();
 return g&&bridge_live(&c)&&c.birth_pending&&!c.birth_closed&&c.attempt==1&&c.group==g->nonce&&c.birth_allocations==4&&c.consumption.boundary_observed&&(r.published_mask&2u)&&bridge_counts(&c);
}
static bool bridge_closed(void)
{
 if(!continuity_mode)return true;
 BcoStatus c=bco_status();BcoLinkStatus a=bco_link_status();BcoReportStatus r=bco_report_status();
 return bridge_live(&c)&&c.birth_closed&&!c.birth_pending&&c.consumption.boundary_observed&&a.birth_source_observed&&a.birth_scene==birth.scene&&a.birth_group==birth.nonce&&c.scene==birth.scene&&c.group==birth.nonce&&(r.published_mask&4u)&&bridge_counts(&c);
}
static bool bridge_anchor(const B313V6PrefixEvidence *e)
{
 if(!continuity_mode)return true;
 BcoLinkStatus a=bco_link_status();BcoReportStatus r=bco_report_status();
 return e&&bridge_closed()&&a.anchor_observed&&a.anchor_tick==409&&a.anchor_serial==s.allocation_serial&&a.anchor_preparation==e->preparation_id&&a.anchor_snapshot_saved&&a.anchor_report_published&&(r.published_mask&(1u<<BCO_REPORT_ANCHOR409));
}
static bool live(void){return b313_tail414_enabled()&&s.active&&!s.failed&&!s.finished;}
static bool bump(uint64_t *p){if(*p==UINT64_MAX)return fail(T_OVERFLOW);++*p;return true;}
void b313_tail414_lifetime_begin(bool target){if(!b313_tail414_enabled())return;if(started||!target){fail(T_ORDER);return;}started=true;s.active=true;}
void b313_tail414_resource(unsigned p){if(!b313_tail414_enabled()||s.failed||s.finished)return;if(p>=4){fail(T_RESOURCE);return;}if(!bump(s.resource_epoch+p))return;if(s.birth_seen||(continuity_mode&&bco_status().birth_pending))fail(T_RESOURCE);}
void b313_tail414_allocated(unsigned slot){if(!b313_tail414_enabled()||s.failed||s.finished)return;if(!s.active||slot>=100){fail(T_ALLOC);return;}if(s.anchored){if(!s.pending||expected_type!=10||expected_alloc!=slot||s.allocations>=2||slot!=78+s.allocations||s.generation[slot]!=0||s.allocation_serial!=27+s.allocations){fail(T_ALLOC);return;}++s.allocations;expected_alloc=100;}
 if(!bump(&s.allocation_serial)||!bump(s.generation+slot))return;
 if(s.birth_seen&&slot>=25&&slot<=28)fail(T_IDENTITY);
}
static bool source(const B313Snapshot *v,unsigned c){return v&&v->slot==25+c&&v->type==313+c&&v->record==313+c&&v->record_verified&&v->graphics_verified&&v->avail==0&&v->size==1&&!v->damaged&&!v->scoreitem&&!v->filter&&v->bank==20&&v->pool<4&&v->sheet_identity&&v->data_identity;}
static bool same(const B313Snapshot *a,const B313Snapshot *b){return a->slot==b->slot&&a->type==b->type&&a->record==b->record&&a->pool==b->pool&&a->bank==b->bank&&a->sheet_identity==b->sheet_identity&&a->data_identity==b->data_identity;}
static bool resources(void){if(continuity_mode&&s.birth_seen&&!bridge_closed())return fail(T_IDENTITY);for(unsigned p=0;p<4;p++)if(s.resource_epoch[p]!=birth_resources[p]||enemySpriteSheetIds[p]!=resource_banks[p]||enemySpriteSheets[p].data!=resource_shapes[p].data||enemySpriteSheets[p].size!=resource_shapes[p].size)return fail(T_RESOURCE);return true;}
void b313_tail414_birth(const B313Group *g){if(!live())return;if(!bridge_birth(g)||s.birth_seen||!g||!g->complete||g->reasons||g->members!=15||!g->scene||!g->nonce||g->birth_tick!=244||g->cur_loc!=244||g->event_loc!=18||g->pool!=25||g->link!=20){fail(T_IDENTITY);return;}
 for(unsigned c=0;c<4;c++){B313Snapshot v;unsigned link=0;const B313Member *m=g->member+c;if(m->slot!=25+c||m->generation!=1||s.generation[25+c]!=1||!source(&m->birth,c)||m->birth.cycle||m->birth.base||!b313_recovery_read_birth(25+c,&v,&link)||link!=20||!source(&v,c)||v.cycle||v.base||!same(&v,&m->birth)||v.ex!=m->birth.ex||v.ey!=m->birth.ey||v.pool!=g->member[0].birth.pool||v.sheet_identity!=g->member[0].birth.sheet_identity||v.data_identity!=g->member[0].birth.data_identity||(int64_t)v.ex!=(int64_t)g->member[0].birth.ex+(c%2)*24||(int64_t)v.ey!=(int64_t)g->member[0].birth.ey-(c/2)*28){fail(T_IDENTITY);return;}}
 birth=*g;memcpy(birth_resources,s.resource_epoch,sizeof(birth_resources));memcpy(resource_shapes,enemySpriteSheets,sizeof(resource_shapes));memcpy(resource_banks,enemySpriteSheetIds,sizeof(resource_banks));if(!birth_resources[g->member[0].birth.pool]){fail(T_RESOURCE);return;}s.birth_seen=true;
}
static bool census(void){if(!live()||!s.birth_seen||!resources())return false;B313Snapshot first={0};s.census_reads=0;for(unsigned slot=0;slot<100;slot++){B313Snapshot v={0};unsigned link=0;++s.census_reads;if(!b313_recovery_read_slot(slot,&v,&link)||v.slot!=slot||v.avail>2)return fail(T_IDENTITY);bool target=v.avail==0&&v.type>=313&&v.type<=316;if(target!=(slot>=25&&slot<=28))return fail(T_IDENTITY);if(!target)continue;unsigned c=slot-25;if(!source(&v,c)||link!=20||s.generation[slot]!=birth.member[c].generation||!same(&v,&birth.member[c].birth)||v.cycle<1||v.cycle>20)return fail(T_IDENTITY);if(!c)first=v;if((int64_t)v.ex!=(int64_t)first.ex+(c%2)*24||(int64_t)v.ey!=(int64_t)first.ey-(c/2)*28)return fail(T_IDENTITY);}return true;}
void b313_tail414_anchor409(const B313V6PrefixEvidence *e){if(!live())return;if(!bridge_anchor(e)||!frame_open||s.tick!=409||s.anchored||s.pending||!e||!e->preparation_id||e->lease.tick!=409||e->identity.group.nonce!=birth.nonce||e->identity.group.scene!=birth.scene||e->binding.phase!=1||!e->binding.metadata_match||!e->binding.pack_generation||e->binding.context.tick!=409||e->binding.context.scene!=e->lease.scene||e->binding.context.frame!=e->lease.frame||e->binding.context.group!=e->identity.group.nonce||e->binding.context.native_epoch!=e->lease.native_epoch||e->binding.context.sample_epoch!=e->lease.sample_epoch||e->binding.context.sequence!=e->lease.sequence||e->identity.group.scene!=e->lease.scene||!e->identity.group.complete||e->identity.group.reasons||e->identity.group.members!=15||e->calls!=16||e->cells!=2688||e->samples!=172032||e->matched!=172032||e->unknown||e->bottom!=3072||s.allocation_serial!=27||!census()){fail(T_IDENTITY);return;}for(unsigned c=0;c<4;c++)if(e->identity.group.member[c].slot!=25+c||!e->identity.group.member[c].drawn||e->identity.group.member[c].parts!=15||e->identity.group.member[c].phase!=1||e->identity.group.member[c].generation!=s.generation[25+c]||!same(&e->identity.group.member[c].birth,&birth.member[c].birth)){fail(T_IDENTITY);return;}s.anchored=true;s.anchor_preparation=e->preparation_id;}
/* Frozen successful record194 constructor result, NOT a newslot wildcard.
 * Copy the pre-event object first to preserve padding. Assign every named field.
 * Only two authorized fixed event outputs differ in ex/linknum. */
static void constructor194(struct JE_SingleEnemyType *e,unsigned entry)
{
 e->fillbyte=0;
 e->ex=-18;
 e->ey=-28;
 e->exc=0;
 e->eyc=0;
 e->exca=-1;
 e->eyca=-1;
 e->excc=0;
 e->eycc=0;
 e->exccw=0;
 e->eyccw=0;
 e->armorleft=30;
 e->eshotwait[0]=20;
 e->eshotwait[1]=20;
 e->eshotwait[2]=20;
 e->eshotmultipos[0]=0;
 e->eshotmultipos[1]=0;
 e->eshotmultipos[2]=0;
 e->enemycycle=1;
 e->ani=8;
 e->egr[0]=13;
 e->egr[1]=15;
 e->egr[2]=17;
 e->egr[3]=51;
 e->egr[4]=55;
 e->egr[5]=89;
 e->egr[6]=91;
 e->egr[7]=93;
 e->egr[8]=0;
 e->egr[9]=0;
 e->egr[10]=0;
 e->egr[11]=0;
 e->egr[12]=0;
 e->egr[13]=0;
 e->egr[14]=0;
 e->egr[15]=0;
 e->egr[16]=0;
 e->egr[17]=0;
 e->egr[18]=0;
 e->egr[19]=0;
 e->size=1;
 e->linknum=3;
 e->aniactive=0;
 e->animax=0;
 e->aniwhenfire=0;
 e->sprite2s=&enemySpriteSheets[2];
 e->exrev=100;
 e->eyrev=100;
 e->exccadd=-1;
 e->eyccadd=-1;
 e->exccwmax=0;
 e->eyccwmax=0;
 e->enemydatofs=&enemyDat[194];
 e->edamaged=0;
 e->enemytype=194;
 e->animin=1;
 e->edgr=0;
 e->edlevel=0;
 e->edani=0;
 e->fill1=0;
 e->filter=0;
 e->evalue=50;
 e->fixedmovey=0;
 e->freq[0]=0;
 e->freq[1]=0;
 e->freq[2]=0;
 e->launchwait=0;
 e->launchtype=0;
 e->launchfreq=0;
 e->xaccel=0;
 e->yaccel=0;
 e->tur[0]=2;
 e->tur[1]=3;
 e->tur[2]=4;
 e->enemydie=0;
 e->enemyground=0;
 e->explonum=1;
 e->mapoffset=0;
 e->scoreitem=0;
 e->special=0;
 e->flagnum=0;
 e->setto=0;
 e->iced=0;
 e->launchspecial=0;
 e->xminbounce=-10000;
 e->xmaxbounce=10000;
 e->yminbounce=-10000;
 e->ymaxbounce=10000;
 e->fill[0]=0;
 e->fill[1]=0;
 e->fill[2]=0;
 if(entry==37){e->ex=270;e->linknum=5;}
}
static bool modes_unchanged(void){return mode_two==twoPlayerMode&&mode_one==onePlayerAction&&mode_super==superTyrian&&mode_arcade==superArcadeMode;}
void b313_tail414_event_before(unsigned tick,unsigned entry,unsigned type,const int a[6])
{
 if(!live())return;if(tick<409){if(s.anchored)fail(T_ORDER);return;}
 if(!s.anchored||!frame_open||s.tick!=tick||s.pending||!a||s.events>=sizeof(events)/sizeof(events[0])||events[s.events].tick!=tick||events[s.events].entry!=entry||events[s.events].type!=type||memcmp(a,events[s.events].a,sizeof(events[0].a))||!resources()){fail(T_EVENT);return;}
 memcpy(expected,enemy,sizeof(expected));memcpy(expected_avail,enemyAvail,sizeof(expected_avail));memcpy(expected_args,a,sizeof(expected_args));expected_entry=entry;expected_type=type;expected_alloc=100;s.pending=true;
 mode_two=twoPlayerMode;mode_one=onePlayerAction;mode_super=superTyrian;mode_arcade=superArcadeMode;
 if(type==10){unsigned slot=entry==36?78:79;unsigned first=100;for(unsigned i=75;i<100;i++)if(expected_avail[i]==1){first=i;break;}if(first!=slot||s.generation[slot]||enemySpriteSheetIds[2]!=20||!enemySpriteSheets[2].data||enemySpriteSheets[2].size!=46204){fail(T_ALLOC);return;}constructor194(expected+slot,entry);expected_avail[slot]=0;expected_alloc=slot;}
 else if(type==19){for(unsigned i=0;i<100;i++)if(expected[i].linknum==a[3]){expected[i].exc=a[0];expected[i].eyc=a[1];if(a[4]>0)expected[i].enemycycle=a[4];}}
 else if(type==33){/* Fixed512 cannot enter random/drop-rewrite branches. */if(!(mode_two||mode_one||mode_super))for(unsigned i=0;i<100;i++)if(expected[i].linknum==a[3])expected[i].enemydie=a[0];}
 else if(type==45){/* Fixed619/628 cannot enter random533 branch. */if(!mode_super&&(mode_two||mode_one))for(unsigned i=0;i<100;i++)if(expected[i].linknum==a[3])expected[i].enemydie=a[0];}
 else fail(T_EVENT);
}
void b313_tail414_event_after(unsigned tick,unsigned entry,unsigned type,const int a[6])
{
 if(!live())return;if(tick<409)return;
 if(!s.pending||!frame_open||s.tick!=tick||entry!=expected_entry||type!=expected_type||!a||memcmp(a,expected_args,sizeof(expected_args))||expected_alloc!=100||!modes_unchanged()||!resources()||memcmp(enemy,expected,sizeof(expected))||memcmp(enemyAvail,expected_avail,sizeof(expected_avail))){fail(T_EVENT);return;}
 s.pending=false;++s.events;
}
static void external_event(unsigned tick,unsigned domain,unsigned type,unsigned origin,bool type_known)
{
 if(!b313_tail414_enabled()||s.finished)return;
 if(continuity_mode){
  BcoStatus c=bco_status();
  /* Only real poll notification origins can defer to the following bco token.
   * No SDL event-type whitelist, no controller/legacy/command exemption. */
  if(started&&origin==TF_EXTERNAL_DETAILED&&domain>=B313_INPUT_SERVICE&&domain<=B313_INPUT_ASSET_POLL&&type_known&&type&&bridge_live(&c)&&!c.birth_pending&&!c.birth_closed&&!c.attempt)return;
  if(!started){remember_rejection(T_EVENT,tick,domain,type,origin,origin!=TF_CONTROLLER_CANCEL,type_known);fail(T_EVENT);return;}
 }
 if(started&&(tick<=414||frame_open)){remember_rejection(T_EVENT,tick,domain,type,origin,origin!=TF_CONTROLLER_CANCEL,type_known);fail(T_EVENT);}
}
void b313_tail414_external_event(unsigned tick){external_event(tick,0,0,TF_EXTERNAL_LEGACY,false);}
void b313_tail414_external_event_detail(unsigned tick,unsigned domain,unsigned type){external_event(tick,domain,type,TF_EXTERNAL_DETAILED,true);}
void b313_tail414_controller_cancel(unsigned tick){external_event(tick,0,0,TF_CONTROLLER_CANCEL,false);}
void b313_tail414_begin(unsigned tick)
{
 if(!live())return;if(tick<408)return;
 if(tick>414){if(!s.finished)fail(T_ORDER);return;}
 if(frame_open||(s.tick?tick!=s.tick+1:tick!=408)||s.pending){fail(T_ORDER);return;}
 s.tick=tick;frame_open=true;
 if(tick==414){if(!s.anchored||s.events!=9||s.allocations!=2||s.allocation_serial!=29||!census()){fail(T_IDENTITY);return;}s.candidate_ready=true;}
}
bool b313_tail414_continuity414(void){return live()&&frame_open&&s.tick==414&&s.candidate_ready&&!s.pending&&s.anchored&&s.events==9&&s.allocations==2&&s.allocation_serial==29&&s.generation[78]==1&&s.generation[79]==1&&census();}
bool b313_tail414_take(B313Group *out,uint64_t gens[100]){if(!out||!gens||s.taken||!b313_tail414_continuity414())return fail(T_ORDER);*out=birth;memcpy(gens,s.generation,sizeof(s.generation));s.taken=true;return true;}
void b313_tail414_end(unsigned tick)
{
 if(!live()||tick<408||tick>414)return;
 if(!frame_open||s.tick!=tick||s.pending){fail(T_ORDER);return;}
 unsigned n=tick<410?0:tick<412?1:tick==412?8:9;
 if(s.events!=n||(tick>=409&&!s.anchored)){fail(T_EVENT);return;}
 if(tick==414){if(!b313_tail414_continuity414()){fail(T_IDENTITY);return;}s.finished=true;s.active=false;}
 frame_open=false;
}
B313Tail414Status b313_tail414_status(void){return s;}
bool b313_tail414_report(void)
{
 if(!b313_tail414_enabled())return false;
 FILE *f=fopen("building313-tail414-lifetime.json.tmp","w");if(!f)return fail(T_IO);
 /* mode is emitted separately below; all original status fields remain. */
 fprintf(f,"{\"enabled\":true,\"active\":%s,\"failed\":%s,\"reasons\":%u,\"tick\":%u,\"birth_seen\":%s,\"anchored\":%s,\"candidate_ready\":%s,\"taken\":%s,\"finished\":%s,\"events\":%u,\"allocations\":%u,\"allocation_serial\":%"PRIu64",\"anchor_preparation\":%"PRIu64",\"census_reads\":%u,\"write_allowed\":false,\"runtime_eligible\":false,\"v6_runtime_validated\":false,\"generations\":[",s.active?"true":"false",s.failed?"true":"false",s.reasons,s.tick,s.birth_seen?"true":"false",s.anchored?"true":"false",s.candidate_ready?"true":"false",s.taken?"true":"false",s.finished?"true":"false",s.events,s.allocations,s.allocation_serial,s.anchor_preparation,s.census_reads);
 for(unsigned i=0;i<100;i++)fprintf(f,"%s%"PRIu64,i?",":"",s.generation[i]);fprintf(f,"],\"first_window_dispatch\":{\"captured\":%s,\"completed\":%s,\"tick\":%u,\"window_id\":%u,\"subtype\":%u,\"handler_branch\":%u,\"focus_before\":%s,\"focus_after\":%s},\"first_rejection\":{",first_window_dispatch.captured?"true":"false",first_window_dispatch.completed?"true":"false",first_window_dispatch.tick,first_window_dispatch.window_id,first_window_dispatch.subtype,first_window_dispatch.handler_branch,first_window_dispatch.focus_before?"true":"false",first_window_dispatch.focus_after?"true":"false");fprintf(f,"\"captured\":%s,\"tick\":%u,\"tick_known\":%s,\"domain\":%u,\"event_domain_known\":%s,\"event_type\":%u,\"event_type_known\":%s,\"reason\":%u,\"origin\":%u,\"observed_tick\":%u,\"birth_seen\":%s,\"anchored\":%s,\"allocation_serial\":%"PRIu64"},\"resource_epochs\":[",first_rejection.captured?"true":"false",first_rejection.tick,first_rejection.tick_known?"true":"false",first_rejection.domain,first_rejection.event_domain_known?"true":"false",first_rejection.type,first_rejection.event_type_known?"true":"false",first_rejection.reason,first_rejection.origin,first_rejection.observed_tick,first_rejection.birth_seen?"true":"false",first_rejection.anchored?"true":"false",first_rejection.allocation_serial);for(unsigned i=0;i<4;i++)fprintf(f,"%s%"PRIu64,i?",":"",s.resource_epoch[i]);fprintf(f,"],\"continuity_bridge_mode\":%s,",continuity_mode?"true":"false");fputs("\"scope\":\"Independent lifetime continuity only. No renderer lease, pixel ownership or material admission.\"}\n",f);
 bool bad=ferror(f)!=0;int close_result=fclose(f);if(bad||close_result||rename("building313-tail414-lifetime.json.tmp","building313-tail414-lifetime.json")){remove("building313-tail414-lifetime.json.tmp");return fail(T_IO);}return !s.failed;
}
