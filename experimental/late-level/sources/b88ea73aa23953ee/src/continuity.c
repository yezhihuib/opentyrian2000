#include "continuity.h"
#include <limits.h>
static bool reject(CoObserver *o,unsigned reason)
{
 if(!o)return false;
 if(!o->failed)o->first_reason=reason;
 o->failed=true;o->reasons|=reason;o->boundary_observed=false;return false;
}
static bool live(const CoObserver *o){return o&&o->begun&&!o->failed&&!o->interrupted;}
bool co_begin(CoObserver *o,uint64_t session)
{
 if(!o)return false;
 if(o->begun||o->failed||!session)return reject(o,CO_ORDER);
 o->begun=true;o->session=session;return true;
}
uint64_t co_consumed(CoObserver *o,unsigned domain,unsigned tick,unsigned type)
{
 if(!live(o))return 0;
 if(domain<CO_SERVICE||domain>CO_ASSET_POLL){reject(o,CO_SCOPE);return 0;}
 if(o->pending){reject(o,CO_PENDING);return 0;}
 if(o->received==UINT64_MAX){reject(o,CO_OVERFLOW);return 0;}
 o->pending=true;o->pending_seq=++o->received;o->pending_domain=domain;o->pending_tick=tick;o->pending_type=type;o->boundary_observed=false;
 return o->pending_seq;
}
bool co_complete(CoObserver *o,uint64_t seq,unsigned domain,unsigned disposition)
{
 if(!live(o))return false;
 if(!o->pending||!seq||seq!=o->pending_seq||domain!=o->pending_domain||disposition!=(domain==CO_FLUSH?CO_DISCARDED:CO_HANDLED))return reject(o,CO_PAIR);
 if(disposition==CO_DISCARDED)++o->discarded;else ++o->handled;
 o->pending=false;o->pending_seq=0;o->pending_domain=0;return true;
}
void co_interrupt(CoObserver *o,unsigned kind)
{
 if(!o||!o->begun)return;
 if(!o->interrupted)o->interrupt_kind=kind;
 o->interrupted=true;reject(o,CO_INTERRUPTED);
}
void co_command(CoObserver *o)
{
 if(!live(o))return;
 if(o->commands==UINT64_MAX){reject(o,CO_OVERFLOW);return;}
 ++o->commands;o->command_parent=o->pending?o->pending_seq:0;
 /* A command is a separate control interruption, not a second SDL consume. */
 if(o->pending&&o->pending_domain!=CO_ASSET_POLL)reject(o,CO_ORDER);
 co_interrupt(o,CO_ASSET_COMMAND);
}
bool co_observe_boundary(CoObserver *o,const CoContext *c)
{
 if(!live(o))return false;
 if(o->pending||o->received!=o->handled+o->discarded)return reject(o,CO_PENDING);
 if(!c||!c->known||c->session!=o->session||!c->probe||!c->asset_debug||!c->demo||c->record||c->network||c->episode!=1||c->level!=2||c->stopped_demo||c->end_requested)return reject(o,CO_SCOPE);
 if(c->residual_known!=CO_ALL_RESIDUAL||c->residual)return reject(o,CO_RESIDUAL);
 o->boundary_observed=true;o->boundary_seq=o->received;
 /* Historical metadata only. Neither write_allowed nor runtime_eligible is set. */
 return true;
}
