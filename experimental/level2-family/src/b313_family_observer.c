#define _POSIX_C_SOURCE 200809L
#include "b313_family_observer.h"
#include "b313_terrain_context.h"
#include "b313_family_input.h"
#if defined(B313_FAMILY_OBSERVER_DIAGNOSTIC) && B313_FAMILY_OBSERVER_DIAGNOSTIC
#include "b313_family_plan.h"
#include "b313_family_cache.h"
#include "varz.h"
#include "episodes.h"
#include "network.h"
#include "config.h"
#include "video.h"
#include "backgrnd.h"
#include "game_probe.h"
#include "b313_platform.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
static B313FamilyObserverStatus s;
static uint64_t session_serial,group_serial;
static bool configured,valid_config,frame_event,report_pending;
static B313FamilyCacheWindow window;
static const unsigned bases[4][3]={{191,195,199},{193,197,201},{153,157,161},{155,159,163}};
static const unsigned phase_by_cycle[20]={0,0,0,0,1,1,2,2,1,1,0,0,0,0,0,0,0,0,0,0};
typedef struct {bool loading,loaded,verified;uint64_t epoch;const void *data;size_t size;} Source;
static Source source[4];
typedef struct {bool live;uint64_t nonce,session;unsigned slots[4];uint64_t generation[4],epochs[4];B313Snapshot birth[4];} Group;
static Group groups[25];static unsigned membership[100];
static struct {bool active,failed;uint64_t nonce,allocation_start;unsigned mask,pool_offset,link;Group group;} birth;
typedef struct {
 SDL_Surface *surface;
 const void *pixels;
 const SDL_PixelFormat *format;
} Target;
typedef struct {
 bool ready;
 unsigned group;
 uint64_t group_nonce,slot_generation,source_epoch;
 int map_offset;
 Target target;
 B313Snapshot actor;
 B313FamilyDrawBorrow borrow;
} Pending;
static Pending pending;
static uint64_t draw_serial,lifetime_serial;
static bool bridge_exhausted;
static uint32_t used_groups;
static uint64_t used_group_nonce[25];
static Target frame_target;
static B313FamilyFrameIdentity first_frame;
/* New metadata only. Neither the old observer status layout nor the actor
 * frame_current/consume qualification is repurposed for terrain. */
static struct {
 bool requested,valid,target_seen,consume_seen;
 B313TerrainContext origin;
} terrain;
static bool terrain_requested(void)
{
 const char *t=getenv("BUILDING313_TERRAIN_CONTINUITY_ENABLE");
 const char *f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 const char *g=getenv("BUILDING313_FAMILY_GROUND_ENABLE");
 return t&&!strcmp(t,"1")&&f&&!strcmp(f,"1")&&g&&!strcmp(g,"1");
}
static bool terrain_empty(void)
{
 bool empty=true;
 for(unsigned i=0;i<100;i++)if(enemyAvail[i]!=1&&enemy[i].enemytype>=313&&enemy[i].enemytype<=316)empty=false;
 return empty;
}
static void revoke_pending(void){memset(&pending,0,sizeof pending);}
static void revoke_lifetime(void)
{
 revoke_pending();
 /* Bridge overflow cannot change the established observer diagnostics. */
 if(lifetime_serial==UINT64_MAX)bridge_exhausted=true;else ++lifetime_serial;
}
static void reset_consumed_frame(void)
{
 used_groups=0;memset(used_group_nonce,0,sizeof used_group_nonce);
 memset(&frame_target,0,sizeof frame_target);memset(&first_frame,0,sizeof first_frame);
}
static void note(unsigned reason,unsigned slot,unsigned part)
{if(!s.first_reason){s.first_reason=reason;s.first_slot=slot;s.first_part=part;}s.reasons|=reason;}
static void fatal(unsigned reason){note(reason,100,UINT_MAX);s.failed=true;}
static bool scope(void){return episodeNum==1&&lvlFileNum==2&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode;}
bool b313_family_observer_enabled(void)
{
 if(!configured){const char *v=getenv("BUILDING313_FAMILY_OBSERVER_ENABLE");s.requested=v&&strcmp(v,"0");valid_config=v&&!strcmp(v,"1");configured=true;}
 return s.requested;
}
static bool live(void){return b313_family_observer_enabled()&&s.active&&!s.failed;}
static void retire_group(unsigned n)
{if(n>=25||!groups[n].live)return;groups[n].live=false;++s.groups_retired;for(unsigned c=0;c<4;c++)if(groups[n].slots[c]<100&&membership[groups[n].slots[c]]==n+1)membership[groups[n].slots[c]]=0;}
static bool increment(uint64_t *n){if(*n==UINT64_MAX){fatal(B313FO_ORDER);return false;}++*n;return true;}
static void close_window(void)
{revoke_pending();if(window.pack_generation){if(!b313_family_cache_frame_end(&window))fatal(B313FO_CACHE);memset(&window,0,sizeof window);}}
static bool source_matches(unsigned pool,bool verify)
{
 if(pool>=4)return false;Source *v=source+pool;Sprite2_array *bank=enemySpriteSheets+pool;
 if(v->loading||!v->loaded||enemySpriteSheetIds[pool]!=20||!bank->data||bank->size!=46204)return false;
 for(unsigned p=0;p<4;p++)if(p!=pool&&enemySpriteSheets[p].data==bank->data)return false;
 if(v->verified)return v->epoch==s.resource_epoch[pool]&&v->data==bank->data&&v->size==bank->size;
 if(!verify)return false;
 static const char expected[]="4bd9a72339e30440c172e385f258c8895b516ff84026a9a6b5a65ada4cf0ab90";
 unsigned char digest[B313_SHA256_BYTES];char hex[65];static const char digits[]="0123456789abcdef";
 ++s.source_hash_calls;if(!b313_sha256(bank->data,bank->size,digest))return false;
 for(unsigned i=0;i<B313_SHA256_BYTES;i++){hex[2*i]=digits[digest[i]>>4];hex[2*i+1]=digits[digest[i]&15];}hex[64]=0;
 if(strcmp(hex,expected))return false;
 v->verified=true;v->epoch=s.resource_epoch[pool];v->data=bank->data;v->size=bank->size;return true;
}
/* Reads actual live objects and record pointers, not caller-provided booleans.
 * Hash verification occurs only at completed birth; draw uses that source epoch.
 * No source bytes, game state, palette or renderer are modified. */
static bool read_actor(unsigned slot,bool at_birth,B313Snapshot *out)
{
 memset(out,0,sizeof *out);if(slot>=100)return false;const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype<313||e->enemytype>316||enemyAvail[slot]!=0||e->enemydatofs!=&enemyDat[e->enemytype]||e->size!=1||e->edamaged||e->scoreitem||e->ani!=20||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive!=1)return false;
 unsigned c=e->enemytype-313;if(enemyDat[e->enemytype].shapebank!=20||enemyDat[e->enemytype].esize!=1||enemyDat[e->enemytype].animate!=1||enemyDat[e->enemytype].ani!=20)return false;
 for(unsigned j=0;j<20;j++)if(e->egr[j]!=bases[c][phase_by_cycle[j]]||enemyDat[e->enemytype].egraphic[j]!=bases[c][phase_by_cycle[j]])return false;
 unsigned pool=4;for(unsigned p=0;p<4;p++)if(e->sprite2s==enemySpriteSheets+p){pool=p;break;}
 if(pool==4||!source_matches(pool,at_birth)||(at_birth&&e->enemycycle!=0)||e->enemycycle>20)return false;
 *out=(B313Snapshot){.slot=slot,.type=e->enemytype,.record=e->enemytype,.pool=pool,.bank=20,.avail=enemyAvail[slot],.size=e->size,.cycle=e->enemycycle,.filter=e->filter,.record_verified=true,.graphics_verified=true,.damaged=e->edamaged,.scoreitem=e->scoreitem,.sheet_identity=(uintptr_t)e->sprite2s,.data_identity=(uintptr_t)e->sprite2s->data,.ex=e->ex,.ey=e->ey,.base=e->enemycycle?e->egr[e->enemycycle-1]:0};return true;
}
/* Pure counterpart of the observer's retiring check, for the renderer bridge. */
static bool group_matches(unsigned n)
{
 if(n>=25||!groups[n].live||groups[n].session!=s.session)return false;Group *g=groups+n;
 for(unsigned c=0;c<4;c++){
  B313Snapshot a;unsigned slot=g->slots[c];const B313Snapshot *b=g->birth+c;
  if(slot>=100||membership[slot]!=n+1||s.generation[slot]!=g->generation[c]||!read_actor(slot,false,&a)||a.type!=313+c||a.pool!=b->pool||a.sheet_identity!=b->sheet_identity||a.data_identity!=b->data_identity||s.resource_epoch[a.pool]!=g->epochs[c])return false;
 }
 return true;
}
static bool group_current(unsigned n)
{
 /* Preserve the original observer's non-retiring early rejection. */
 if(n>=25||!groups[n].live||groups[n].session!=s.session)return false;
 if(group_matches(n))return true;retire_group(n);return false;
}
static bool target_context(SDL_Surface *surface)
{
 return surface&&surface==game_screen&&surface->pixels&&surface->format&&
  surface->format->format==SDL_PIXELFORMAT_INDEX8&&surface->format->BitsPerPixel==8&&
  surface->format->BytesPerPixel==1&&!surface->locked&&!SDL_MUSTLOCK(surface)&&
  !surface->clip_rect.x&&!surface->clip_rect.y&&surface->clip_rect.w==320&&surface->clip_rect.h==200;
}
static bool target_matches(SDL_Surface *surface,const Target *target)
{
 return target_context(surface)&&surface==target->surface&&
  surface->pixels==target->pixels&&surface->format==target->format&&
  surface->w==320&&surface->h==200&&surface->pitch==320;
}
static B313FamilyFrameIdentity frame_identity(void)
{return(B313FamilyFrameIdentity){s.session,s.frame,lifetime_serial,window.pack_generation,window.frame_generation};}
static bool same_frame(const B313FamilyFrameIdentity *a,const B313FamilyFrameIdentity *b)
{
 return a->session==b->session&&a->frame==b->frame&&a->lifetime_serial==b->lifetime_serial&&
  a->pack_generation==b->pack_generation&&a->frame_generation==b->frame_generation;
}
static bool frame_matches(const B313FamilyFrameIdentity *frame)
{
 if(!frame||bridge_exhausted||!configured||!valid_config||!s.requested||!s.active||s.failed||
    !s.frame_open||frame_event||birth.active||!scope()||!frame->session||!frame->frame||
    !frame->lifetime_serial||!frame->pack_generation||!frame->frame_generation)return false;
 B313FamilyFrameIdentity now=frame_identity();
 if(!same_frame(frame,&now)||frame->pack_generation!=s.pack_generation)return false;
 B313FamilyCacheStatus cache=b313_family_cache_status();
 return cache.ready&&cache.frame_open&&cache.phase_mask==7&&
  cache.pack_generation==frame->pack_generation&&cache.frame_generation==frame->frame_generation;
}
bool b313_family_observer_terrain_context_current(SDL_Surface *surface,const B313TerrainContext *context)
{
 if(!context||!terrain.requested||!terrain.valid||!terrain_requested()||
    terrain.target_seen||terrain.consume_seen||pending.ready||used_groups||
    s.target_calls!=terrain.origin.target_calls||context->target_calls!=terrain.origin.target_calls||
    !same_frame(&context->frame,&terrain.origin.frame)||!frame_matches(&context->frame)||
    context->surface!=terrain.origin.surface||context->pixels!=terrain.origin.pixels||
    context->format!=terrain.origin.format)return false;
 Target target={context->surface,context->pixels,context->format};
 return target_matches(surface,&target)&&terrain_empty();
}
bool b313_family_observer_terrain_context_begin(SDL_Surface *surface,B313TerrainContext *out)
{
 if(out)memset(out,0,sizeof *out);
 if(!out||!b313_family_observer_terrain_context_current(surface,&terrain.origin))return false;
 *out=terrain.origin;return true;
}
static bool same_actor(const B313Snapshot *a,const B313Snapshot *b)
{
 return a->slot==b->slot&&a->type==b->type&&a->record==b->record&&a->pool==b->pool&&
  a->bank==b->bank&&a->avail==b->avail&&a->size==b->size&&a->cycle==b->cycle&&
  a->filter==b->filter&&a->record_verified==b->record_verified&&a->graphics_verified==b->graphics_verified&&
  a->damaged==b->damaged&&a->scoreitem==b->scoreitem&&a->sheet_identity==b->sheet_identity&&
  a->data_identity==b->data_identity&&a->ex==b->ex&&a->ey==b->ey&&a->base==b->base;
}
void b313_family_observer_begin(void)
{
 revoke_lifetime();reset_consumed_frame();
 if(!b313_family_observer_enabled())return;
 if(s.active){fatal(B313FO_ORDER);return;}
 bool requested=s.requested;memset(&s,0,sizeof s);s.requested=requested;report_pending=true;
 memset(groups,0,sizeof groups);memset(membership,0,sizeof membership);memset(source,0,sizeof source);memset(&birth,0,sizeof birth);memset(&window,0,sizeof window);
 if(!valid_config||!scope()){fatal(B313FO_CONFIG);return;}
 for(unsigned i=0;i<100;i++)if(enemyAvail[i]!=1){fatal(B313FO_SESSION);return;}
 if(!increment(&session_serial))return;s.session=session_serial;s.active=true;
 const char *paths[3]={getenv("BUILDING313_V6_PHASE0"),getenv("BUILDING313_V6_PHASE1"),getenv("BUILDING313_V6_PHASE2")};
 if(!b313_family_cache_prepare(paths)){fatal(B313FO_CACHE);return;}
 B313FamilyCacheStatus cache=b313_family_cache_status();s.pack_generation=cache.pack_generation;
}
void b313_family_observer_frame_begin(void)
{
 /* Capture is opt-in. OFF performs no new census, borrow or diagnostics. */
 terrain.requested=terrain_requested();terrain.valid=false;
 if(terrain.requested){terrain.target_seen=terrain.consume_seen=false;memset(&terrain.origin,0,sizeof terrain.origin);}
 revoke_lifetime();reset_consumed_frame();
 if(!live())return;if(s.frame_open||birth.active){fatal(B313FO_ORDER);return;}
 if(!scope()||!increment(&s.frame)){fatal(B313FO_CONTEXT);return;}
 frame_event=false;s.frame_open=true;if(!b313_family_cache_frame_begin(&window))fatal(B313FO_CACHE);
 for(unsigned n=0;n<25;n++)if(groups[n].live)(void)group_current(n);
 if(terrain.requested){
  B313FamilyFrameIdentity origin=frame_identity();
  Target target={game_screen,game_screen?game_screen->pixels:NULL,game_screen?game_screen->format:NULL};
  if(frame_matches(&origin)&&target_matches(game_screen,&target)&&terrain_empty()){
   terrain.origin=(B313TerrainContext){origin,game_screen,target.pixels,target.format,s.target_calls};
   terrain.valid=true;
  }
 }
}
void b313_family_observer_frame_end(void)
{
 revoke_lifetime();reset_consumed_frame();
 if(!b313_family_observer_enabled()||!s.active)return;if(!s.frame_open){fatal(B313FO_ORDER);return;}
 close_window();s.frame_open=false;if(birth.active){birth.active=false;fatal(B313FO_BIRTH);}
 for(unsigned n=0;n<25;n++)if(groups[n].live)(void)group_current(n);
}
void b313_family_observer_abandon(void)
{revoke_lifetime();reset_consumed_frame();if(!b313_family_observer_enabled()||!s.active)return;close_window();if(s.frame_open)++s.abandoned_frames;s.frame_open=false;birth.active=false;}
void b313_family_observer_event(void)
{revoke_lifetime();if(!live())return;if(!s.frame_open){fatal(B313FO_ORDER);return;}if(!frame_event)++s.event_frames;frame_event=true;close_window();}
void b313_family_observer_external_event(void)
{
 /* SDL consumption is legal at every lifecycle boundary. Unlike a script
  * event it must not require/open a frame, nor depend on legacy probe scope.
  * Revoke even an already failed session before closing its borrow window. */
 if(!b313_family_observer_enabled())return;
 revoke_lifetime();
 /* A consumed external event also breaks an in-flight birth transaction;
  * later members/end cannot publish that interrupted construction. */
 if(birth.active)birth.failed=true;
 if(s.active&&s.frame_open){if(!frame_event)++s.event_frames;frame_event=true;}
 close_window();
}
void b313_family_observer_allocated(const void *object)
{
 revoke_lifetime();
 if(!live())return;unsigned slot=100;for(unsigned i=0;i<100;i++)if(object==enemy+i){slot=i;break;}
 if(slot==100){fatal(B313FO_ALLOC);return;}if(membership[slot])retire_group(membership[slot]-1);
 if(!increment(&s.allocation_serial)||!increment(s.generation+slot))return;
}
void b313_family_observer_resource(unsigned pool,unsigned operation)
{
 revoke_lifetime();
 if(!live())return;if(pool>=4||(operation!=1&&operation!=2)){fatal(B313FO_RESOURCE);return;}
 if(!increment(s.resource_epoch+pool))return;source[pool]=(Source){.loading=operation==1};
 for(unsigned n=0;n<25;n++)if(groups[n].live)for(unsigned c=0;c<4;c++)if(groups[n].birth[c].pool==pool){retire_group(n);break;}
 if(birth.active)birth.failed=true;
 if(s.frame_open){frame_event=true;close_window();}
}
void b313_family_observer_resource_done(unsigned pool)
{
 revoke_lifetime();
 if(!live())return;if(pool>=4||!source[pool].loading){fatal(B313FO_RESOURCE);return;}
 source[pool].loading=false;source[pool].loaded=true;
}
uint64_t b313_family_observer_birth_begin(unsigned type,unsigned pool_offset,unsigned link)
{
 revoke_lifetime();
 if(!live()||type!=313)return 0;if(birth.active||!s.frame_open||!frame_event||pool_offset>75||pool_offset%25){fatal(B313FO_BIRTH);return 0;}
 if(!increment(&group_serial))return 0;memset(&birth,0,sizeof birth);birth.active=true;birth.nonce=group_serial;birth.allocation_start=s.allocation_serial;birth.pool_offset=pool_offset;birth.link=link;birth.group.nonce=group_serial;birth.group.session=s.session;return birth.nonce;
}
void b313_family_observer_birth_member(uint64_t group,unsigned c,unsigned slot1)
{
 revoke_lifetime();
 if(!group)return;if(!live()||!birth.active||group!=birth.nonce||c>=4){fatal(B313FO_BIRTH);return;}
 if(birth.mask&(1u<<c)){birth.failed=true;return;}birth.mask|=1u<<c;
 if(!slot1||slot1>100){birth.failed=true;return;}unsigned slot=slot1-1;B313Snapshot a;
 if(slot<birth.pool_offset||slot>=birth.pool_offset+25||!s.generation[slot]||membership[slot]||!read_actor(slot,true,&a)||a.type!=313+c||enemy[slot].linknum!=birth.link){birth.failed=true;return;}
 for(unsigned j=0;j<c;j++)if((birth.mask&(1u<<j))&&birth.group.generation[j]&&birth.group.slots[j]==slot){birth.failed=true;return;}
 birth.group.slots[c]=slot;birth.group.generation[c]=s.generation[slot];birth.group.epochs[c]=s.resource_epoch[a.pool];birth.group.birth[c]=a;
}
void b313_family_observer_birth_end(uint64_t group)
{
 revoke_lifetime();
 if(!group)return;if(!live()||!birth.active||birth.nonce!=group){fatal(B313FO_BIRTH);return;}
 bool ok=!birth.failed&&birth.mask==15&&s.allocation_serial>=birth.allocation_start&&s.allocation_serial-birth.allocation_start==4;
 for(unsigned c=0;c<4;c++){
  B313Snapshot *a=birth.group.birth+c,*b=birth.group.birth;
  B313Snapshot now={0};unsigned slot=birth.group.slots[c];
  if(slot>=100||s.generation[slot]!=birth.group.generation[c]||membership[slot]||!read_actor(slot,true,&now)||now.type!=a->type||now.record!=a->record||now.pool!=a->pool||now.bank!=a->bank||now.sheet_identity!=a->sheet_identity||now.data_identity!=a->data_identity||now.ex!=a->ex||now.ey!=a->ey||now.filter!=a->filter||enemy[slot].linknum!=birth.link)ok=false;
  if(!birth.group.generation[c]||a->pool!=b->pool||a->sheet_identity!=b->sheet_identity||a->data_identity!=b->data_identity||(int64_t)a->ex!=(int64_t)b->ex+(c%2)*24||(int64_t)a->ey!=(int64_t)b->ey-(c/2)*28||a->pool>=4||birth.group.epochs[c]!=s.resource_epoch[a->pool])ok=false;
 }
 unsigned n=0;while(n<25&&groups[n].live)++n;if(n==25)ok=false;
 if(ok){groups[n]=birth.group;groups[n].live=true;for(unsigned c=0;c<4;c++)membership[groups[n].slots[c]]=n+1;++s.groups_committed;}
 else{++s.birth_rejected;note(B313FO_BIRTH,100,UINT_MAX);}
 birth.active=false;
}
void b313_family_observer_draw(SDL_Surface *surface,unsigned slot,int xo,int yo,int part)
{
 revoke_pending();
 if(!live())return;if(slot>=100){fatal(B313FO_ALLOC);return;}if(enemy[slot].enemytype<313||enemy[slot].enemytype>316)return;
 if(terrain.requested)terrain.target_seen=true; /* Sticky even if rejected, cleared or destroyed later. */
 ++s.target_calls;unsigned why=0;B313Snapshot a={0};B313FamilyPlan plan={0};B313FamilyCacheTile tile={0};
 if(!s.frame_open||!scope())why=B313FO_CONTEXT;
 else if(!membership[slot]||!group_current(membership[slot]-1))why=B313FO_LIFETIME;
 else if(!read_actor(slot,false,&a))why=B313FO_SOURCE;
 else if(frame_event)why=B313FO_EVENT;
 else if(!target_context(surface))why=B313FO_CONTEXT;
 else {
  int q=part==0?0:part==1?1:part==19?2:part==20?3:-1;
  int64_t x=(int64_t)enemy[slot].ex+xo+tempMapXOfs,y=(int64_t)enemy[slot].ey+yo;
  if(q<0||xo!=-6+(q%2)*12||yo!=-7+(q/2)*14||enemy[slot].mapoffset!=tempMapXOfs||x<INT_MIN||x>INT_MAX||y<INT_MIN||y>INT_MAX)why=B313FO_CONTEXT;
  else {B313FamilyCall call={.actor=a,.part=(unsigned)part,.density=8,.x=(int)x,.y=(int)y,.surface_width=surface->w,.surface_height=surface->h,.surface_pitch=surface->pitch};
   if(!b313_family_plan(&call,&plan))why=B313FO_PLAN;
   else {unsigned index=(unsigned)(plan.source_y_hd/112)*4+(unsigned)(plan.source_x_hd/96);
    if(!b313_family_cache_borrow(&window,plan.phase,index,&tile)||!b313_family_cache_tile_current(&tile)||tile.pack_generation!=s.pack_generation)why=B313FO_CACHE;
   }
  }
 }
 if(why){++s.rejected;note(why,slot,part<0?UINT_MAX:(unsigned)part);return;}
 ++s.candidates;++s.phase_calls[plan.phase];s.cycle_mask|=UINT64_C(1)<<(plan.cycle-1);
 /* Statistics remain this single observer pass. Only the immediate original
  * blit may consume this internal descriptor; no tile pixels are read here. */
 if(bridge_exhausted||draw_serial==UINT64_MAX){bridge_exhausted=true;return;}
 unsigned n=membership[slot]-1;
 pending=(Pending){.ready=true,.group=n,.group_nonce=groups[n].nonce,
  .slot_generation=s.generation[slot],.source_epoch=s.resource_epoch[a.pool],
  .map_offset=tempMapXOfs,.target={surface,surface->pixels,surface->format},.actor=a,
  .borrow={.nonce=++draw_serial,.frame=frame_identity(),.plan=plan,.tile=tile}};
}
bool b313_family_observer_frame_current(SDL_Surface *surface,const B313FamilyFrameIdentity *frame)
{
 if(!frame_matches(frame)||!used_groups||!same_frame(frame,&first_frame)||
    !target_matches(surface,&frame_target))return false;
 for(unsigned n=0;n<25;n++)if(used_groups&(UINT32_C(1)<<n))
  if(groups[n].nonce!=used_group_nonce[n]||!group_matches(n))return false;
 return true;
}
bool b313_family_observer_consume(SDL_Surface *surface,unsigned slot,int x,int y,
                                 unsigned base,int part,int filter,
                                 const Sprite2_array *sheet_identity,
                                 Sprite2_array bank,B313FamilyDrawBorrow *out)
{
 if(terrain.requested)terrain.consume_seen=true; /* Every attempt, including a failed one. */
 Pending p=pending;
 revoke_pending(); /* Consume before validation, including every failed attempt. */
 if(out)memset(out,0,sizeof *out);
 if(!out||!p.ready||!p.borrow.nonce||slot>=100||slot!=p.actor.slot||part<0||filter<0||
    (unsigned)part!=p.borrow.plan.part||base!=p.actor.base||(unsigned)filter!=p.actor.filter||
    x!=p.borrow.plan.destination_x||y!=p.borrow.plan.destination_y||
    !target_matches(surface,&p.target)||!frame_matches(&p.borrow.frame)||
    p.group>=25||membership[slot]!=p.group+1||groups[p.group].nonce!=p.group_nonce||
    s.generation[slot]!=p.slot_generation||p.actor.pool>=4||
    s.resource_epoch[p.actor.pool]!=p.source_epoch||!group_matches(p.group))return false;
 B313Snapshot a;
 if(!read_actor(slot,false,&a)||!same_actor(&a,&p.actor)||
    (uintptr_t)sheet_identity!=a.sheet_identity||(uintptr_t)bank.data!=a.data_identity||
    bank.size!=source[a.pool].size||bank.size!=enemySpriteSheets[a.pool].size||
    tempMapXOfs!=p.map_offset||enemy[slot].mapoffset!=tempMapXOfs)return false;
 int64_t now_x=(int64_t)a.ex-6+p.borrow.plan.part_x+tempMapXOfs;
 int64_t now_y=(int64_t)a.ey-7+p.borrow.plan.part_y;
 if(now_x!=x||now_y!=y||!b313_family_cache_tile_current(&p.borrow.tile)||
    p.borrow.tile.pack_generation!=p.borrow.frame.pack_generation||
    p.borrow.tile.frame_generation!=p.borrow.frame.frame_generation)return false;
 /* A lifecycle change after any consumption poisons this entire frame, not
  * just the next quadrant. Qualification never silently starts a new lease. */
 if(used_groups&&!b313_family_observer_frame_current(surface,&first_frame))return false;
 if(!used_groups){first_frame=p.borrow.frame;frame_target=p.target;}
 used_groups|=UINT32_C(1)<<p.group;used_group_nonce[p.group]=p.group_nonce;
 *out=p.borrow;return true;
}
void b313_family_observer_finish(unsigned reason)
{
 revoke_lifetime();reset_consumed_frame();
 if(!b313_family_observer_enabled()||(!s.active&&!report_pending))return;report_pending=false;b313_family_observer_abandon();
 B313FamilyCacheStatus before=b313_family_cache_status();for(unsigned n=0;n<25;n++)retire_group(n);s.active=false;b313_family_cache_close();B313FamilyCacheStatus after=b313_family_cache_status();
 FILE *f=fopen("building313-family-observer.json.tmp","w");if(!f){fatal(B313FO_IO);fprintf(stderr,"B313_FAMILY_REPORT_FAILED\n");return;}
 fprintf(f,"{\"schema\":1,\"session\":%"PRIu64",\"frames\":%"PRIu64",\"finish_reason\":%u,\"failed\":%s,\"reasons\":%u,\"first_reason\":%u,\"first_slot\":%u,\"first_part\":%u,\"groups_committed\":%"PRIu64",\"groups_retired\":%"PRIu64",\"birth_rejected\":%"PRIu64",\"allocation_serial\":%"PRIu64",\"target_calls\":%"PRIu64",\"candidates\":%"PRIu64",\"rejected\":%"PRIu64",\"event_frames\":%"PRIu64",\"abandoned_frames\":%"PRIu64",\"source_hash_calls\":%"PRIu64",\"phase_calls\":[%"PRIu64",%"PRIu64",%"PRIu64"],\"cycle_mask\":%"PRIu64",\"pack_generation\":%"PRIu64",\"cache_ready_before_close\":%s,\"cache_ready_after_close\":%s,\"phase_mask_before_close\":%u,\"cache_read_calls\":%"PRIu64",\"cache_hash_calls\":%"PRIu64",\"cache_reasons_before_close\":%u,\"write_allowed\":false,\"runtime_eligible\":false,\"production_enabled\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\",\"scope\":\"Actual before-draw source/lifetime metadata and borrowed legal tile availability only. No tile pixels read or drawn, no renderer activation, no material permission.\"}\n",s.session,s.frame,reason,s.failed?"true":"false",s.reasons,s.first_reason,s.first_slot,s.first_part,s.groups_committed,s.groups_retired,s.birth_rejected,s.allocation_serial,s.target_calls,s.candidates,s.rejected,s.event_frames,s.abandoned_frames,s.source_hash_calls,s.phase_calls[0],s.phase_calls[1],s.phase_calls[2],s.cycle_mask,s.pack_generation,before.ready?"true":"false",after.ready?"true":"false",before.phase_mask,before.read_calls,before.hash_calls,before.reasons);
 bool bad=ferror(f)!=0;int closed=fclose(f);if(bad||closed||rename("building313-family-observer.json.tmp","building313-family-observer.json")){fatal(B313FO_IO);fprintf(stderr,"B313_FAMILY_REPORT_FAILED\n");}
}
B313FamilyObserverStatus b313_family_observer_status(void){return s;}
#else
bool b313_family_observer_enabled(void){return false;}
void b313_family_observer_begin(void){}
void b313_family_observer_finish(unsigned r){(void)r;}
void b313_family_observer_frame_begin(void){}
void b313_family_observer_frame_end(void){}
void b313_family_observer_abandon(void){}
void b313_family_observer_event(void){}
void b313_family_observer_external_event(void){}
void b313_family_observer_allocated(const void *p){(void)p;}
void b313_family_observer_resource(unsigned p,unsigned o){(void)p;(void)o;}
void b313_family_observer_resource_done(unsigned p){(void)p;}
uint64_t b313_family_observer_birth_begin(unsigned t,unsigned p,unsigned l){(void)t;(void)p;(void)l;return 0;}
void b313_family_observer_birth_member(uint64_t g,unsigned c,unsigned s){(void)g;(void)c;(void)s;}
void b313_family_observer_birth_end(uint64_t g){(void)g;}
void b313_family_observer_draw(SDL_Surface *s,unsigned i,int x,int y,int p){(void)s;(void)i;(void)x;(void)y;(void)p;}
bool b313_family_observer_consume(SDL_Surface *s,unsigned i,int x,int y,unsigned b,int p,int f,const Sprite2_array *identity,Sprite2_array bank,B313FamilyDrawBorrow *out)
{(void)s;(void)i;(void)x;(void)y;(void)b;(void)p;(void)f;(void)identity;(void)bank;if(out)*out=(B313FamilyDrawBorrow){0};return false;}
bool b313_family_observer_frame_current(SDL_Surface *s,const B313FamilyFrameIdentity *f){(void)s;(void)f;return false;}
bool b313_family_observer_terrain_context_begin(SDL_Surface *s,B313TerrainContext *out)
{(void)s;if(out)*out=(B313TerrainContext){0};return false;}
bool b313_family_observer_terrain_context_current(SDL_Surface *s,const B313TerrainContext *c)
{(void)s;(void)c;return false;}
B313FamilyObserverStatus b313_family_observer_status(void){return(B313FamilyObserverStatus){0};}
#endif
