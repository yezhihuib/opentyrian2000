#include "b313_family_observer.h"
#include "b313_terrain_context.h"
#include "b313_family_input.h"
#include "native_writer_observer.h"
#if defined(B313_FAMILY_OBSERVER_DIAGNOSTIC) && B313_FAMILY_OBSERVER_DIAGNOSTIC
#include "b313_family_plan.h"
#include "b313_family_cache.h"
#include "varz.h"
#include "episodes.h"
#include "network.h"
#include "config.h"
#include "video.h"
#include "backgrnd.h"
#include "b313_family_writer.h"
#include "asset_debug.h"
#include "params.h"
#include "xmas.h"
/* Defined by the native dispatcher; existing code exposes no public declaration. */
extern struct JE_EventRecType eventRec[];
#include "game_probe.h"
#include <openssl/sha.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
static B313FamilyObserverStatus s;
static uint64_t session_serial,group_serial;
static bool configured,valid_config,frame_event,report_pending;
static bool entry_frame_enabled,entry_policy_failed;
static bool entry_requested(void)
{const char *e=getenv("BUILDING313_ENTRY_CLIP_ENABLE");return e&&!strcmp(e,"1");}
static bool entry_policy_current(void)
{return !entry_policy_failed&&entry_frame_enabled==entry_requested();}
static B313ComponentTailStatus tail;
static bool tail_requested(void)
{
 const char *t=getenv("BUILDING313_COMPONENT_TAIL_ENABLE");
 const char *o=getenv("BUILDING313_FAMILY_OBSERVER_ENABLE");
 const char *c=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return t&&!strcmp(t,"1")&&o&&!strcmp(o,"1")&&c&&!strcmp(c,"1");
}
static bool tail_policy_current(void)
{
 if(tail.session_enabled!=tail_requested()||tail.frame_enabled!=tail.session_enabled)tail.policy_failed=true;
 return !tail.policy_failed;
}
bool b313_family_observer_tail_enabled(void)
{return tail.session_enabled&&s.active&&!s.failed&&tail_policy_current();}
B313ComponentTailStatus b313_family_observer_tail_status(void)
{B313ComponentTailStatus out=tail;out.requested=tail_requested();return out;}
static B313FamilyCacheWindow window;
static const unsigned bases[4][3]={{191,195,199},{193,197,201},{153,157,161},{155,159,163}};
static const unsigned phase_by_cycle[20]={0,0,0,0,1,1,2,2,1,1,0,0,0,0,0,0,0,0,0,0};
typedef struct {bool loading,loaded,verified;uint64_t epoch;const void *data;size_t size;} Source;
static Source source[4];
typedef struct {bool live;uint64_t nonce,session;unsigned slots[4];uint64_t generation[4],epochs[4];B313Snapshot birth[4];
 bool tail_known;unsigned tail_index,retired_lower_mask,exit_parts[2];
 uint64_t exit_draw_frame[2],exit_draw_lifetime[2];
} Group;
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
/* Independent of HD admission. The second lower actor must still complete
 * its original calls after the first actor has invalidated the HD frame. */
static struct {
 bool active,failed,physical_pending;
 unsigned group,component,part,stores,pixels;
 uint64_t nonce,generation,epoch,session,frame,lifetime;
 int x,y;Target target;B313Snapshot actor;
 const void *physical_address;Uint8 physical_value;
} tail_call;

static void tail_call_discard(bool poison)
{
 if(poison&&tail_call.active&&tail_call.group<25&&tail_call.component<2){
  Group *g=groups+tail_call.group;unsigned c=tail_call.component;
  if(g->live&&g->nonce==tail_call.nonce){g->exit_draw_frame[c]=tail_call.frame;g->exit_draw_lifetime[c]=tail_call.lifetime;g->exit_parts[c]=4;}
 }
 memset(&tail_call,0,sizeof tail_call);
}
static uint64_t draw_serial,lifetime_serial;
uint64_t b313_family_observer_lifetime_serial(void){return lifetime_serial;}
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
 uint64_t continuity_lifetime;
 bool spawn_enabled;
} terrain;
/* A single synchronous witness for the actual ordinary random constructor.
 * Never changes the global lifetime, actor authority or copied terrain origin. */
static struct {
 bool active,failed,allocated;
 uint64_t serial,token,lifetime,allocation,generation;
 unsigned record,slot;
 B313FamilyFrameIdentity frame;
 B313FamilyWriterStatus writer;
 uint64_t epochs[4];
 Source sources[4];
 Sprite2_array banks[4];
 unsigned bank_ids[4];
 SDL_Surface *vga;
} terrain_spawn;
static bool script19_current(const B313FamilyFrameIdentity *frame);
static bool script19_blocks(void);
static bool terrain_spawn_requested(void)
{
 const char *e=getenv("BUILDING313_TERRAIN_SPAWN_CONTINUITY_ENABLE");
 const char *o=getenv("BUILDING313_FAMILY_OBSERVER_ENABLE");
 return e&&!strcmp(e,"1")&&o&&!strcmp(o,"1");
}
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
 revoke_pending();tail_call_discard(true);
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
{if(n>=25||!groups[n].live)return;groups[n].live=false;if(groups[n].tail_known)tail.groups[groups[n].tail_index].live=false;++s.groups_retired;for(unsigned c=0;c<4;c++)if(groups[n].slots[c]<100&&membership[groups[n].slots[c]]==n+1)membership[groups[n].slots[c]]=0;}
static bool increment(uint64_t *n){if(*n==UINT64_MAX){fatal(B313FO_ORDER);return false;}++*n;return true;}
static bool close_window(void)
{
 bool success=false;revoke_pending();
 if(window.pack_generation){success=b313_family_cache_frame_end(&window);if(!success)fatal(B313FO_CACHE);memset(&window,0,sizeof window);}
 return success;
}
static bool source_matches(unsigned pool,bool verify)
{
 if(pool>=4)return false;Source *v=source+pool;Sprite2_array *bank=enemySpriteSheets+pool;
 if(v->loading||!v->loaded||enemySpriteSheetIds[pool]!=20||!bank->data||bank->size!=46204)return false;
 for(unsigned p=0;p<4;p++)if(p!=pool&&enemySpriteSheets[p].data==bank->data)return false;
 if(v->verified)return v->epoch==s.resource_epoch[pool]&&v->data==bank->data&&v->size==bank->size;
 if(!verify)return false;
 static const char expected[]="4bd9a72339e30440c172e385f258c8895b516ff84026a9a6b5a65ada4cf0ab90";
 unsigned char digest[SHA256_DIGEST_LENGTH];char hex[65];static const char digits[]="0123456789abcdef";
 ++s.source_hash_calls;if(!SHA256(bank->data,bank->size,digest))return false;
 for(unsigned i=0;i<SHA256_DIGEST_LENGTH;i++){hex[2*i]=digits[digest[i]>>4];hex[2*i+1]=digits[digest[i]&15];}hex[64]=0;
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
/* Active native drivers only: dormant exccadd/eyccadd are normally -1. */
static bool tail_motion(unsigned slot)
{
 const struct JE_SingleEnemyType *e=enemy+slot;
 unsigned r=e->enemytype;
 if(r<313||r>316||e->enemydatofs!=enemyDat+r)return false;
 return !e->exc&&!e->eyc&&!e->fixedmovey&&!e->excc&&!e->eycc&&!e->xaccel&&!e->yaccel&&
  !enemyDat[r].xmove&&!enemyDat[r].ymove&&!enemyDat[r].xcaccel&&!enemyDat[r].ycaccel&&
  !enemyDat[r].xaccel&&!enemyDat[r].yaccel;
}
static bool component_matches(unsigned n,unsigned c,B313Snapshot *out)
{
 Group *g=groups+n;unsigned slot=g->slots[c];const B313Snapshot *b=g->birth+c;
 if(slot>=100||membership[slot]!=n+1||s.generation[slot]!=g->generation[c]||
    !read_actor(slot,false,out)||out->type!=313+c||out->pool!=b->pool||
    out->sheet_identity!=b->sheet_identity||out->data_identity!=b->data_identity||
    s.resource_epoch[out->pool]!=g->epochs[c])return false;
 if(g->tail_known&&(!tail_policy_current()||!tail_motion(slot)||
    enemy[slot].linknum!=(g->tail_index?21:20)||out->ex!=b->ex||out->ey<b->ey||out->ey>191))return false;
 return true;
}
/* Pure counterpart of the observer's retiring check, for the renderer bridge. */
static bool group_matches(unsigned n)
{
 if(n>=25||!groups[n].live||groups[n].session!=s.session)return false;Group *g=groups+n;
 for(unsigned c=0;c<4;c++){
  if(g->tail_known&&c<2&&(g->retired_lower_mask&(1u<<c)))continue;
  B313Snapshot a;if(!component_matches(n,c,&a))return false;
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
 if(!entry_policy_current()||!tail_policy_current()||!frame||bridge_exhausted||!configured||!valid_config||!s.requested||!s.active||s.failed||
    !s.frame_open||frame_event||birth.active||!scope()||!frame->session||!frame->frame||
    !frame->lifetime_serial||!frame->pack_generation||!frame->frame_generation)return false;
 B313FamilyFrameIdentity now=frame_identity();
 if(!same_frame(frame,&now)||frame->pack_generation!=s.pack_generation)return false;
 B313FamilyCacheStatus cache=b313_family_cache_status();
 return cache.ready&&cache.frame_open&&cache.phase_mask==7&&
  cache.pack_generation==frame->pack_generation&&cache.frame_generation==frame->frame_generation;
}
/* The only permitted translation is the chain committed at the exact native
 * call. Any other revocation remains visible to the unchanged frame_matches. */
static bool terrain_frame_matches(const B313FamilyFrameIdentity *frame)
{
 if(terrain_spawn.active)return false;
 if(script19_blocks())return script19_current(frame);
 if(frame_matches(frame))return true;
 if(!terrain.spawn_enabled||!terrain_spawn_requested()||
    terrain.continuity_lifetime<=terrain.origin.frame.lifetime_serial)return false;
 B313FamilyFrameIdentity witnessed=*frame;
 witnessed.lifetime_serial=terrain.continuity_lifetime;
 return frame_matches(&witnessed);
}
bool b313_family_observer_terrain_context_current(SDL_Surface *surface,const B313TerrainContext *context)
{
 if(!context||!terrain.requested||!terrain.valid||!terrain_requested()||
    terrain.target_seen||terrain.consume_seen||pending.ready||used_groups||
    s.target_calls!=terrain.origin.target_calls||context->target_calls!=terrain.origin.target_calls||
    !same_frame(&context->frame,&terrain.origin.frame)||!terrain_frame_matches(&context->frame)||
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

static uint64_t terrain_spawn_stamp(const Uint8 *p,size_t n)
{
 uint64_t h=UINT64_C(0xcbf29ce484222325);
 while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}return h;
}
static uint64_t terrain_spawn_record_stamp(unsigned type)
{
 Uint8 b[77];size_t n=0;
#define AST_BYTE(v) do {b[n++]=(Uint8)(v);} while(0)
#define AST_WORD(v) do {unsigned word_=(unsigned)(v);AST_BYTE(word_);AST_BYTE(word_>>8);} while(0)
 AST_BYTE(enemyDat[type].ani);
 for(unsigned i=0;i<3;i++)AST_BYTE(enemyDat[type].tur[i]);
 for(unsigned i=0;i<3;i++)AST_BYTE(enemyDat[type].freq[i]);
 AST_BYTE(enemyDat[type].xmove);AST_BYTE(enemyDat[type].ymove);
 AST_BYTE(enemyDat[type].xaccel);AST_BYTE(enemyDat[type].yaccel);
 AST_BYTE(enemyDat[type].xcaccel);AST_BYTE(enemyDat[type].ycaccel);
 AST_WORD(enemyDat[type].startx);AST_WORD(enemyDat[type].starty);
 AST_BYTE(enemyDat[type].startxc);AST_BYTE(enemyDat[type].startyc);
 AST_BYTE(enemyDat[type].armor);AST_BYTE(enemyDat[type].esize);
 for(unsigned i=0;i<20;i++)AST_WORD(enemyDat[type].egraphic[i]);
 AST_BYTE(enemyDat[type].explosiontype);AST_BYTE(enemyDat[type].animate);
 AST_BYTE(enemyDat[type].shapebank);AST_BYTE(enemyDat[type].xrev);AST_BYTE(enemyDat[type].yrev);
 AST_WORD(enemyDat[type].dgr);AST_BYTE(enemyDat[type].dlevel);AST_BYTE(enemyDat[type].dani);
 AST_BYTE(enemyDat[type].elaunchfreq);AST_WORD(enemyDat[type].elaunchtype);
 AST_WORD(enemyDat[type].value);AST_WORD(enemyDat[type].eenemydie);
#undef AST_WORD
#undef AST_BYTE
 return n==sizeof(b)?terrain_spawn_stamp(b,sizeof(b)):0;
}

static uint64_t terrain_spawn_known_record(unsigned r)
{
 static const struct {unsigned record;uint64_t stamp;} known[]={
 {135,UINT64_C(0x50100b90790211f7)},{136,UINT64_C(0x75cc21d83286ca9e)},
 {260,UINT64_C(0x1542a4d2be1f9e22)},{261,UINT64_C(0x8191d64b6f9dc2f5)},
 {263,UINT64_C(0xb5b242a28c967a41)},{265,UINT64_C(0xf73069ce11d02c67)},
 {317,UINT64_C(0x77b90388a71496a7)},{318,UINT64_C(0x82e36d9b60719ab1)},
 {319,UINT64_C(0x438e34fc179d35fb)},{320,UINT64_C(0xd4dd0adbd842dda9)},
 {321,UINT64_C(0x61dd3333c84054f2)},{322,UINT64_C(0x5ae7c07c97ca0228)},
 {323,UINT64_C(0x67ce4e8c6ec817a3)},{324,UINT64_C(0x53b9f3cb5db6e6b1)},
 {462,UINT64_C(0xd2a0e655d0091793)}};
 for(unsigned i=0;i<sizeof known/sizeof known[0];i++)if(known[i].record==r)return known[i].stamp;
 return 0;
}
static bool terrain_spawn_scope(void)
{
 return scope()&&mainLevel==6&&!strncmp(levelName,"ASTEROID2",9)&&
 (levelName[9]==0||levelName[9]==' ')&&enemiesActive&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!record_demo&&!stopped_demo&&!constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&
 !superTyrian&&superArcadeMode==SA_NONE&&!timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static bool terrain_spawn_quiet(void)
{
 if(pending.ready||tail_call.active||birth.active||used_groups||terrain.target_seen||terrain.consume_seen||
    s.target_calls!=terrain.origin.target_calls||!terrain_empty())return false;
 for(unsigned i=0;i<100;i++)if(membership[i])return false;
 for(unsigned i=0;i<25;i++)if(groups[i].live)return false;
 return true;
}
#include "b313_terrain_script_private.inc"

static Sprite2_array *terrain_spawn_bank(void)
{
 Sprite2_array *bank=NULL;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8)bank=enemySpriteSheets+i;
 return bank&&bank->data&&bank->size==42012&&
  terrain_spawn_stamp(bank->data,bank->size)==UINT64_C(0x913975450e0fc00d)?bank:NULL;
}
static bool terrain_spawn_resources_current(void)
{
 for(unsigned i=0;i<4;i++){
  const Source *a=source+i,*b=terrain_spawn.sources+i;
  if(s.resource_epoch[i]!=terrain_spawn.epochs[i]||enemySpriteSheetIds[i]!=terrain_spawn.bank_ids[i]||
     enemySpriteSheets[i].data!=terrain_spawn.banks[i].data||enemySpriteSheets[i].size!=terrain_spawn.banks[i].size||
     a->loading!=b->loading||a->loaded!=b->loaded||a->verified!=b->verified||
     a->epoch!=b->epoch||a->data!=b->data||a->size!=b->size)return false;
 }
 return true;
}
static bool terrain_spawn_writer_current(void)
{
 B313FamilyWriterStatus now=b313_family_writer_status(),*old=&terrain_spawn.writer;
 return b313_family_writer_peek_draw(s.frame)&&now.frame==old->frame&&
  now.stores==old->stores&&now.store_bytes==old->store_bytes&&now.pixels==old->pixels&&
  now.fills==old->fills&&now.fill_rows_suppressed==old->fill_rows_suppressed&&
  now.copy_rows==old->copy_rows&&now.reasons==old->reasons&&now.first_reason==old->first_reason;
}
/* This is checked only after JE_newEnemy returns from the unmodified native
 * constructor. No saved pre-allocation enemytype is treated as the new type. */
static bool terrain_spawn_completed(unsigned slot,unsigned r)
{
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(slot>=25||enemyAvail[slot]!=0||e->enemytype!=r||e->enemydatofs!=enemyDat+r||
    terrain_spawn_record_stamp(r)!=terrain_spawn_known_record(r)||enemyDat[r].shapebank!=8||
    e->sprite2s!=terrain_spawn_bank()||!e->sprite2s||e->size!=enemyDat[r].esize||
    e->mapoffset||e->filter||e->linknum||e->special||e->iced||e->scoreitem||e->edamaged||!e->armorleft||
    e->ani!=enemyDat[r].ani||e->animin!=1||e->animax!=(enemyDat[r].animate==2?e->ani:0)||
    e->aniwhenfire!=(enemyDat[r].animate==2?2:0)||
    e->enemycycle!=(enemyDat[r].animate==1?0:1)||e->aniactive!=enemyDat[r].animate||
    e->exc!=enemyDat[r].xmove||e->eyc!=enemyDat[r].ymove||e->fixedmovey||
    e->excc!=enemyDat[r].xcaccel||e->eycc!=enemyDat[r].ycaccel||
    e->xaccel!=enemyDat[r].xaccel||e->yaccel!=enemyDat[r].yaccel||
    e->launchfreq!=enemyDat[r].elaunchfreq||e->launchwait!=enemyDat[r].elaunchfreq||
    e->launchtype!=enemyDat[r].elaunchtype%1000||e->launchspecial!=enemyDat[r].elaunchtype/1000||
    e->enemydie!=enemyDat[r].eenemydie||e->edani!=enemyDat[r].dani||e->edgr!=enemyDat[r].dgr||e->edlevel!=enemyDat[r].dlevel)return false;
 int x=enemyDat[r].startx+1,y=enemyDat[r].starty+1;
 if((enemyDat[r].startxc?(e->ex<x-enemyDat[r].startxc||e->ex>=x+enemyDat[r].startxc):e->ex!=x)||
    (enemyDat[r].startyc?(e->ey<y-enemyDat[r].startyc||e->ey>=y+enemyDat[r].startyc):e->ey!=y))return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=enemyDat[r].egraphic[i])return false;
 for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->tur[i]!=enemyDat[r].tur[i]||e->freq[i]!=enemyDat[r].freq[i]||
    e->eshotwait[i]!=(e->tur[i]==252?1:e->tur[i]?20:255))return false;
 return true;
}
uint64_t b313_family_observer_terrain_spawn_begin(unsigned record,unsigned pool,int unique)
{
 if(terrain_spawn.active){terrain_spawn.failed=true;terrain.valid=false;return 0;}
 if(script19.attempted||!terrain.spawn_enabled||!terrain_spawn_requested()||!terrain_requested()||pool||unique||
    !terrain_spawn_scope()||!terrain_spawn_quiet()||!terrain_spawn_known_record(record)||
    terrain_spawn_record_stamp(record)!=terrain_spawn_known_record(record)||
    !b313_family_observer_terrain_context_current(game_screen,&terrain.origin)||
    !b313_family_writer_peek_draw(s.frame)||!terrain_spawn_bank()||VGAScreen!=game_screen)return 0;
 unsigned slot=0;while(slot<25&&enemyAvail[slot]!=1)++slot;
 if(slot==25||terrain_spawn.serial==UINT64_MAX||lifetime_serial==UINT64_MAX||
    s.allocation_serial==UINT64_MAX||s.generation[slot]==UINT64_MAX)return 0;
 terrain_spawn.active=true;terrain_spawn.failed=terrain_spawn.allocated=false;
 terrain_spawn.token=++terrain_spawn.serial;terrain_spawn.record=record;terrain_spawn.slot=slot;
 terrain_spawn.frame=frame_identity();terrain_spawn.lifetime=lifetime_serial;
 terrain_spawn.allocation=s.allocation_serial;terrain_spawn.generation=s.generation[slot];
 terrain_spawn.writer=b313_family_writer_status();terrain_spawn.vga=VGAScreen;
 for(unsigned i=0;i<4;i++){
  terrain_spawn.epochs[i]=s.resource_epoch[i];terrain_spawn.sources[i]=source[i];
  terrain_spawn.banks[i]=enemySpriteSheets[i];terrain_spawn.bank_ids[i]=enemySpriteSheetIds[i];
 }
 return terrain_spawn.token;
}
void b313_family_observer_terrain_spawn_commit(uint64_t token,unsigned slot1)
{
 if(!token)return;
 bool ok=terrain_spawn.active&&!terrain_spawn.failed&&terrain_spawn.allocated&&token==terrain_spawn.token&&
  terrain.spawn_enabled&&terrain_spawn_requested()&&terrain.requested&&terrain.valid&&terrain_requested()&&
  terrain_spawn_scope()&&terrain_spawn_quiet()&&slot1==terrain_spawn.slot+1&&
  lifetime_serial==terrain_spawn.lifetime+1&&s.allocation_serial==terrain_spawn.allocation+1&&
  s.generation[terrain_spawn.slot]==terrain_spawn.generation+1&&
  terrain_spawn_resources_current()&&terrain_spawn_writer_current()&&VGAScreen==terrain_spawn.vga&&
  target_matches(game_screen,&(Target){terrain.origin.surface,terrain.origin.pixels,terrain.origin.format})&&
  terrain_spawn_completed(terrain_spawn.slot,terrain_spawn.record);
 B313FamilyFrameIdentity expected=terrain_spawn.frame;
 expected.lifetime_serial=terrain_spawn.lifetime+1;
 ok=ok&&frame_matches(&expected);
 terrain_spawn.active=false;
 if(ok)terrain.continuity_lifetime=lifetime_serial;
 else terrain.valid=false; /* Never recover or regrant a failed constructor. */
}

static bool same_actor(const B313Snapshot *a,const B313Snapshot *b)
{
 return a->slot==b->slot&&a->type==b->type&&a->record==b->record&&a->pool==b->pool&&
  a->bank==b->bank&&a->avail==b->avail&&a->size==b->size&&a->cycle==b->cycle&&
  a->filter==b->filter&&a->record_verified==b->record_verified&&a->graphics_verified==b->graphics_verified&&
  a->damaged==b->damaged&&a->scoreitem==b->scoreitem&&a->sheet_identity==b->sheet_identity&&
  a->data_identity==b->data_identity&&a->ex==b->ex&&a->ey==b->ey&&a->base==b->base;
}
/* Only the two authenticated case12 births may detach a component. */
static int tail_birth_index(unsigned pool,unsigned link)
{
 if(!b313_family_observer_tail_enabled()||pool!=25||eventLoc<1||eventLoc>maxEvent)return -1;
 const struct JE_EventRecType *e=eventRec+eventLoc-1;
 int k=eventLoc==18?0:eventLoc==75?1:-1;
 if(k<0||tail.groups[k].committed||e->eventtime!=(k?664:244)||e->eventtype!=12||
    e->eventdat!=313||e->eventdat2!=(k?210:138)||e->eventdat3||
    e->eventdat4!=(k?21:20)||e->eventdat5||e->eventdat6||link!=(unsigned)(k?21:20))return -1;
 return k;
}
static void tail_native_begin(SDL_Surface *surface,unsigned slot,int xo,int yo,int part)
{
 tail_call_discard(true);
 if(!b313_family_observer_tail_enabled()||!s.frame_open||!scope()||slot>=100||
    !membership[slot]||!target_context(surface))return;
 unsigned n=membership[slot]-1;Group *g=groups+n;
 if(!g->live||!g->tail_known||g->session!=s.session)return;
 unsigned c=enemy[slot].enemytype-313;
 if(c>=2||g->slots[c]!=slot||g->retired_lower_mask&(1u<<c))return;
 B313Snapshot a;
 if(!component_matches(n,c,&a)||a.ey!=191||a.filter||(part!=0&&part!=1)||
    xo!=(part?6:-6)||yo!=-7||enemy[slot].mapoffset!=tempMapXOfs)return;
 int x=a.ex+xo+tempMapXOfs,y=a.ey+yo;
 if(x<0||x>308||y!=184||surface->w!=320||surface->h!=200||surface->pitch!=320)return;
 tail_call.active=true;tail_call.group=n;tail_call.component=c;tail_call.part=(unsigned)part;
 tail_call.nonce=g->nonce;tail_call.generation=g->generation[c];tail_call.epoch=g->epochs[c];
 tail_call.session=s.session;tail_call.frame=s.frame;tail_call.lifetime=lifetime_serial;tail_call.x=x;tail_call.y=y;
 tail_call.target=(Target){surface,surface->pixels,surface->format};tail_call.actor=a;
}
void b313_family_observer_native_store(SDL_Surface *surface,const void *address,size_t bytes,unsigned writer)
{
 if(!tail_call.active)return;
 if(tail_call.failed)return;
 unsigned k=tail_call.stores;
 const void *expected_address=(const Uint8 *)tail_call.target.pixels+(tail_call.y+(int)(k/12))*320+tail_call.x+k%12;
 if(k>=168||tail_call.physical_pending||bytes!=1||writer!=NWO_SPRITE2||
    !target_matches(surface,&tail_call.target)||address!=expected_address){tail_call.failed=true;return;}
 ++tail_call.stores;tail_call.physical_pending=true;tail_call.physical_address=address;
 tail_call.physical_value=*(const Uint8 *)address;
}
void b313_family_observer_native_pixel(SDL_Surface *surface,const void *address,int style)
{
 if(!tail_call.active||tail_call.failed)return;
 if(style!=0||!tail_call.physical_pending||surface!=tail_call.target.surface||
    address!=tail_call.physical_address||tail_call.pixels>=168||*(const Uint8 *)address!=tail_call.physical_value){tail_call.failed=true;return;}
 ++tail_call.pixels;tail_call.physical_pending=false;
}
void b313_family_observer_draw_end(SDL_Surface *surface,unsigned slot,int part)
{
 if(!tail_call.active)return;
 bool ok=!tail_call.failed&&!tail_call.physical_pending&&tail_call.stores==168&&tail_call.pixels==168&&
  b313_family_observer_tail_enabled()&&s.frame_open&&scope()&&tail_call.session==s.session&&
  tail_call.frame==s.frame&&tail_call.lifetime==lifetime_serial&&slot==tail_call.actor.slot&&part==(int)tail_call.part&&
  target_matches(surface,&tail_call.target);
 Group *g=groups+tail_call.group;unsigned c=tail_call.component;B313Snapshot a;
 ok=ok&&g->live&&g->tail_known&&g->nonce==tail_call.nonce&&g->generation[c]==tail_call.generation&&
  g->epochs[c]==tail_call.epoch&&component_matches(tail_call.group,c,&a)&&same_actor(&a,&tail_call.actor);
 if(ok){
  if(g->exit_draw_frame[c]!=s.frame||g->exit_draw_lifetime[c]!=lifetime_serial){g->exit_draw_frame[c]=s.frame;g->exit_draw_lifetime[c]=lifetime_serial;g->exit_parts[c]=0;}
  unsigned expected=part==0?0:1;
  if(g->exit_parts[c]==expected)g->exit_parts[c]|=1u<<(unsigned)part;
  else g->exit_parts[c]=4; /* repeated/out-of-order original dispatch */
 }
 tail_call_discard(!ok);
}
void b313_family_observer_bottom_exit(unsigned slot)
{
 if(!tail.session_enabled||!live()||slot>=100||!membership[slot])return;
 unsigned n=membership[slot]-1;Group *g=groups+n;
 if(!g->tail_known)return;
 unsigned c=enemy[slot].enemytype-313;B313Snapshot a;
 bool ok=c<4&&g->slots[c]==slot&&b313_family_observer_tail_enabled()&&s.frame_open&&scope()&&
  component_matches(n,c,&a)&&a.ey==191&&!a.filter&&!tail_call.active;
 if(!ok){revoke_lifetime();retire_group(n);return;}
 if(c>=2){++tail.upper_retirements;revoke_lifetime();retire_group(n);return;}
 if(g->exit_draw_frame[c]!=s.frame||g->exit_draw_lifetime[c]!=lifetime_serial||g->exit_parts[c]!=3){revoke_lifetime();retire_group(n);return;}
 /* This historical receipt survives only for the other independently live
  * members. Retired storage is never read again or used as an anchor. */
 g->retired_lower_mask|=1u<<c;membership[slot]=0;
 B313ComponentTailGroup *r=tail.groups+g->tail_index;
 r->retired_lower_mask=g->retired_lower_mask;r->lower_exit_frame[c]=s.frame;
 ++tail.lower_exits;tail.last_exit_slot=slot;tail.last_exit_generation=s.generation[slot];
 tail.last_exit_frame=s.frame;tail.last_exit_y=a.ey;
 revoke_lifetime(); /* Keep the transition frame conservative. */
}

void b313_family_observer_begin(void)
{
 revoke_lifetime();reset_consumed_frame();
 if(!b313_family_observer_enabled())return;
 if(s.active){fatal(B313FO_ORDER);return;}
 bool requested=s.requested;memset(&s,0,sizeof s);s.requested=requested;report_pending=true;
 memset(&tail,0,sizeof tail);tail.session_enabled=tail.frame_enabled=tail_requested();
 memset(groups,0,sizeof groups);memset(membership,0,sizeof membership);memset(source,0,sizeof source);memset(&birth,0,sizeof birth);memset(&window,0,sizeof window);
 if(!valid_config||!scope()){fatal(B313FO_CONFIG);return;}
 for(unsigned i=0;i<100;i++)if(enemyAvail[i]!=1){fatal(B313FO_SESSION);return;}
 if(!increment(&session_serial))return;s.session=session_serial;s.active=true;tail.session=s.session;
 const char *paths[3]={getenv("BUILDING313_V6_PHASE0"),getenv("BUILDING313_V6_PHASE1"),getenv("BUILDING313_V6_PHASE2")};
 if(!b313_family_cache_prepare(paths)){fatal(B313FO_CACHE);return;}
 B313FamilyCacheStatus cache=b313_family_cache_status();s.pack_generation=cache.pack_generation;
}
void b313_family_observer_frame_begin(void)
{
 /* Capture is opt-in. OFF performs no new census, borrow or diagnostics. */
 bool script_enabled=script19_requested(),script31_enabled=script31_requested();
 if(script19.enabled||script_enabled||script19.enabled31||script31_enabled)memset(&script19,0,sizeof script19);
 script19.enabled=script_enabled;script19.enabled31=script31_enabled;
 if(script_enabled!=script19_stream.enabled||script31_enabled!=script19_stream.enabled31)script19_stream.policy_failed=true;
 entry_frame_enabled=entry_requested();entry_policy_failed=false;
 tail.frame_enabled=tail_requested();
 if(tail.frame_enabled!=tail.session_enabled)tail.policy_failed=true;
 terrain_spawn.active=false;terrain_spawn.failed=false;terrain_spawn.allocated=false;
 terrain.spawn_enabled=terrain_spawn_requested();terrain.continuity_lifetime=0;
 terrain.requested=terrain_requested();terrain.valid=false;
 if(terrain.requested){terrain.target_seen=terrain.consume_seen=false;memset(&terrain.origin,0,sizeof terrain.origin);}
 revoke_lifetime();reset_consumed_frame();
 if(!live())return;if(s.frame_open||birth.active){fatal(B313FO_ORDER);return;}
 if(!scope()||!increment(&s.frame)){fatal(B313FO_CONTEXT);return;}
 tail.frame=s.frame;frame_event=false;s.frame_open=true;if(!b313_family_cache_frame_begin(&window))fatal(B313FO_CACHE);
 for(unsigned n=0;n<25;n++)if(groups[n].live)(void)group_current(n);
 if(terrain.requested){
  B313FamilyFrameIdentity origin=frame_identity();
  Target target={game_screen,game_screen?game_screen->pixels:NULL,game_screen?game_screen->format:NULL};
  if(frame_matches(&origin)&&target_matches(game_screen,&target)&&terrain_empty()){
   terrain.origin=(B313TerrainContext){origin,game_screen,target.pixels,target.format,s.target_calls};
   terrain.valid=true;terrain.continuity_lifetime=origin.lifetime_serial;
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
{
 const bool expected=script19_close_before();
 revoke_lifetime();if(!live())return;if(!s.frame_open){fatal(B313FO_ORDER);return;}
 if(!frame_event)++s.event_frames;frame_event=true;
 const bool closed=close_window();script19_close_after(expected,closed);
}
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
 /* Observe the free slot before the unconditional legacy revocation. This
  * alone cannot certify a record: only the call-site commit sees completion. */
 bool witnessed=terrain_spawn.active&&!terrain_spawn.failed&&!terrain_spawn.allocated&&
  terrain_spawn.slot<25&&object==enemy+terrain_spawn.slot&&enemyAvail[terrain_spawn.slot]==1&&
  lifetime_serial==terrain_spawn.lifetime&&s.allocation_serial==terrain_spawn.allocation&&
  s.generation[terrain_spawn.slot]==terrain_spawn.generation&&terrain_spawn_quiet();
 if(terrain_spawn.active&&!witnessed)terrain_spawn.failed=true;
 revoke_lifetime();
 if(!live())return;unsigned slot=100;for(unsigned i=0;i<100;i++)if(object==enemy+i){slot=i;break;}
 if(slot==100){fatal(B313FO_ALLOC);return;}if(membership[slot])retire_group(membership[slot]-1);
 if(!increment(&s.allocation_serial)||!increment(s.generation+slot))return;
 if(witnessed)terrain_spawn.allocated=true;
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
 if(!increment(&group_serial))return 0;memset(&birth,0,sizeof birth);birth.active=true;birth.nonce=group_serial;birth.allocation_start=s.allocation_serial;birth.pool_offset=pool_offset;birth.link=link;birth.group.nonce=group_serial;birth.group.session=s.session;
 int tail_index=tail_birth_index(pool_offset,link);
 if(tail_index>=0){birth.group.tail_known=true;birth.group.tail_index=(unsigned)tail_index;}
 return birth.nonce;
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
 if(birth.group.tail_known)for(unsigned c=0;c<4;c++){
  B313Snapshot *a=birth.group.birth+c;unsigned slot=birth.group.slots[c];
  if(slot>=100||a->pool!=2||a->ex!=(birth.group.tail_index?198:126)+(int)(c%2)*24||
     a->ey!=-28-(int)(c/2)*28||!tail_motion(slot))birth.group.tail_known=false;
 }
 unsigned n=0;while(n<25&&groups[n].live)++n;if(n==25)ok=false;
 if(ok){groups[n]=birth.group;groups[n].live=true;for(unsigned c=0;c<4;c++)membership[groups[n].slots[c]]=n+1;++s.groups_committed;}
 else{++s.birth_rejected;note(B313FO_BIRTH,100,UINT_MAX);}
 if(ok&&groups[n].tail_known){
  Group *g=groups+n;B313ComponentTailGroup *r=tail.groups+g->tail_index;
  r->committed=r->live=true;r->event=g->tail_index?75:18;r->nonce=g->nonce;r->birth_frame=s.frame;
  for(unsigned c=0;c<4;c++){r->slots[c]=g->slots[c];r->generation[c]=g->generation[c];r->epochs[c]=g->epochs[c];r->birth_x[c]=g->birth[c].ex;r->birth_y[c]=g->birth[c].ey;}
  ++tail.accepted_groups;
 }
 birth.active=false;
}
void b313_family_observer_draw(SDL_Surface *surface,unsigned slot,int xo,int yo,int part)
{
 revoke_pending();tail_call_discard(true);
 if(!live())return;if(slot>=100){fatal(B313FO_ALLOC);return;}if(enemy[slot].enemytype<313||enemy[slot].enemytype>316)return;
 if(terrain.requested)terrain.target_seen=true; /* Sticky even if rejected, cleared or destroyed later. */
 tail_native_begin(surface,slot,xo,yo,part);
 ++s.target_calls;unsigned why=0;B313Snapshot a={0};B313FamilyPlan plan={0};B313FamilyCacheTile tile={0};
 if(!tail_policy_current()){tail.policy_failed=true;why=B313FO_CONFIG;}
 else if(!entry_policy_current()){entry_policy_failed=true;why=B313FO_CONFIG;}
 else if(!s.frame_open||!scope())why=B313FO_CONTEXT;
 else if(!membership[slot]||!group_current(membership[slot]-1))why=B313FO_LIFETIME;
 else if(!read_actor(slot,false,&a))why=B313FO_SOURCE;
 else if(frame_event)why=B313FO_EVENT;
 else if(!target_context(surface))why=B313FO_CONTEXT;
 else {
  int q=part==0?0:part==1?1:part==19?2:part==20?3:-1;
  int64_t x=(int64_t)enemy[slot].ex+xo+tempMapXOfs,y=(int64_t)enemy[slot].ey+yo;
  if(q<0||xo!=-6+(q%2)*12||yo!=-7+(q/2)*14||enemy[slot].mapoffset!=tempMapXOfs||x<INT_MIN||x>INT_MAX||y<INT_MIN||y>INT_MAX)why=B313FO_CONTEXT;
  else {B313FamilyCall call={.actor=a,.part=(unsigned)part,.density=8,.x=(int)x,.y=(int)y,.surface_width=surface->w,.surface_height=surface->h,.surface_pitch=surface->pitch,.entry_clip=entry_frame_enabled};
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
 if(!entry_policy_current())entry_policy_failed=true;
 if(!tail_policy_current())tail.policy_failed=true;
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
void b313_family_observer_script_level_begin(char m,char s){(void)m;(void)s;}
void b313_family_observer_script_dispatch_begin(void){}
void b313_family_observer_script_dispatch_end(void){}
void b313_family_observer_script_event_before(unsigned e){(void)e;}
void b313_family_observer_script_event_after(unsigned e){(void)e;}
B313TerrainScriptReceipt b313_family_observer_script_receipt(void){return(B313TerrainScriptReceipt){0};}
B313TerrainScript31PolicyReceipt b313_family_observer_script31_policy_receipt(void){return(B313TerrainScript31PolicyReceipt){0};}
bool b313_family_observer_tail_enabled(void){return false;}
B313ComponentTailStatus b313_family_observer_tail_status(void){return(B313ComponentTailStatus){0};}
void b313_family_observer_native_store(SDL_Surface *s,const void *p,size_t n,unsigned w){(void)s;(void)p;(void)n;(void)w;}
void b313_family_observer_native_pixel(SDL_Surface *s,const void *p,int t){(void)s;(void)p;(void)t;}
void b313_family_observer_draw_end(SDL_Surface *s,unsigned i,int p){(void)s;(void)i;(void)p;}
void b313_family_observer_bottom_exit(unsigned i){(void)i;}
uint64_t b313_family_observer_lifetime_serial(void){return 0;}
bool b313_family_observer_enabled(void){return false;}
void b313_family_observer_begin(void){}
void b313_family_observer_finish(unsigned r){(void)r;}
void b313_family_observer_frame_begin(void){}
void b313_family_observer_frame_end(void){}
void b313_family_observer_abandon(void){}
void b313_family_observer_event(void){}
void b313_family_observer_external_event(void){}
void b313_family_observer_allocated(const void *p){(void)p;}
uint64_t b313_family_observer_terrain_spawn_begin(unsigned r,unsigned p,int u){(void)r;(void)p;(void)u;return 0;}
void b313_family_observer_terrain_spawn_commit(uint64_t t,unsigned s){(void)t;(void)s;}
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
