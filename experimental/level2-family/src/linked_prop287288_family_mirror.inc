/* SPDX-License-Identifier: GPL-2.0-or-later
 * Default-OFF independent actors287/288, all six exact origins under one narrow opt-in.
 * Renderer-side witnesses only: native allocation, event commit, animation,
 * hit and retirement call sites remain the sole gameplay authorities.
 * No pair allocation/liveness requirement. No old paired-adapter allowlist.
 */
#include "linked_prop287288_native.inc"
static struct {uint64_t generation,epoch,token,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate;uint64_t phase_tick;LinkedProp287288Birth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} lp287_slots[100];
static struct {uint64_t epoch,serial,hit_serial;bool exhausted,loaded;char root[1024];unsigned consumed,mode;
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned record,event;int slot;} call;
 struct {bool live;uint64_t token;unsigned slot,link,damage,armor,shot;} hit;
} lp287_life;
static struct {bool checked,valid;char root[1024];Asset member[3];} lp287_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,image,part,pixels,used;
 LinkedProp287288Draw draw[100];LinkedProp287288Write writes[100][672];} lp287_frame;
static unsigned lp287_witnessed_records;
static uint64_t lp287_witnessed_count[2],lp287_phase_observations,lp287_hit_count,lp287_linked_retirements;
static bool lp287_resources_current(void);
static uint8_t lp287_owned[64000],lp287_shadows[64000];
static uint64_t lp287_blend_retirements,lp287_normal_retirements,lp287_shadow_writes;
static uint64_t lp287_clipped,lp287_unwitnessed,lp287_lifetime_losses,lp287_bank_losses,lp287_contract_faults;
static unsigned lp287_first_reason;
static const char *lp287_root(void){const char *p=getenv("LINKED_PROP287288_ASSET_DIR");return p?p:"";}
static unsigned lp287_mode(void)
{
 const char *e=getenv("LINKED_PROP287288_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&f&&!strcmp(f,"1")&&e&&!strcmp(e,"1")?6u:0u;
}
static bool lp287_enabled(void){return lp287_mode()!=0;}
static bool lp287_level_scope(void)
{
 return lp287_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static const struct {unsigned event,time,record;int x;unsigned link;int y;} lp287_origins[6]={
 {183,1392,287,210,23,-28},
 {184,1392,288,90,22,0},
 {185,1392,287,90,22,-28},
 {186,1392,288,210,23,0},
 {286,2456,288,162,26,0},
 {287,2456,287,162,26,-28}
};
static int lp287_origin(unsigned event)
{for(unsigned i=0;i<COUNTOF(lp287_origins);i++)if(lp287_origins[i].event==event)return (int)i;return -1;}
static bool lp287_origin_enabled(int origin)
{return origin>=0&&origin<(int)COUNTOF(lp287_origins)&&(lp287_life.mode&(origin<4?2u:4u));}
static bool lp287_event_matches(unsigned event)
{
 int k=lp287_origin(event);
 if(!lp287_life.events||lp287_life.events!=eventRec||maxEvent!=731||k<0)return false;
 const struct JE_EventRecType *r=lp287_life.events+event-1;
 return r->eventtime==lp287_origins[k].time&&r->eventtype==6&&r->eventdat==(int)lp287_origins[k].record&&
 r->eventdat2==lp287_origins[k].x&&!r->eventdat3&&r->eventdat4==lp287_origins[k].link&&
 r->eventdat5==lp287_origins[k].y&&!r->eventdat6;
}
static bool lp287_scope(void)
{
 return lp287_life.loaded&&!lp287_life.exhausted&&lp287_level_scope()&&terrain_file=='z'&&
 lp287_mode()==lp287_life.mode&&!strcmp(lp287_life.root,lp287_root());
}
static void lp287_fail(unsigned reason)
{
 if(!lp287_first_reason)lp287_first_reason=reason;
 lp287_frame.fault=true;lp287_frame.accepted=false;lp287_frame.active=lp287_frame.pending=false;
 if(lp287_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_linked_prop287288_retired(unsigned slot,unsigned reason,unsigned source)
{
 if(slot>=100)return;
 if(lp287_slots[slot].live||lp287_slots[slot].pending){
  ++lp287_lifetime_losses;
  if(lp287_frame.draw[slot].token)lp287_fail(1);
 }
 LinkedProp287288Birth *b=&lp287_slots[slot].birth;
 if(b->live){
  b->retired_frame=fc_frame;b->retired_y=enemy[slot].ey;b->retirement_reason=reason;b->retirement_source_slot=source;
  if((reason==LP287_DIRECT_LETHAL||reason==LP287_LINKED_LETHAL)&&lp287_life.hit.live&&
   source==lp287_life.hit.slot&&lp287_life.hit.armor<=lp287_life.hit.damage&&
   (source==slot||b->link==lp287_life.hit.link)){
   b->retirement_hit_token=lp287_life.hit.token;
   if(source!=slot)++lp287_linked_retirements;
  }
 }
 b->live=false;
 lp287_slots[slot].live=lp287_slots[slot].pending=lp287_slots[slot].initialized=false;
}
static void lp287_reset(void)
{
 if(lp287_frame.contributed||lp287_frame.active||lp287_frame.pending)lp287_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_linked_prop287288_retired(i,LP287_INVALIDATED,100);
 lp287_life.call.live=lp287_life.hit.live=false;
 if(lp287_life.epoch==UINT64_MAX)lp287_life.exhausted=true;else ++lp287_life.epoch;
 /* Original event consumption survives renderer resets, not real level loads. */
}
void render_mirror_linked_prop287288_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 lp287_reset();lp287_life.loaded=false;lp287_life.consumed=0;lp287_life.events=events;lp287_life.mode=lp287_mode();
 lp287_witnessed_records=0;memset(lp287_witnessed_count,0,sizeof lp287_witnessed_count);
 for(unsigned i=0;i<100;i++)memset(&lp287_slots[i].birth,0,sizeof lp287_slots[i].birth);
 if(!lp287_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
 !lp287_event_matches(183)||!lp287_event_matches(184)||!lp287_event_matches(185)||!lp287_event_matches(186)||
 !f284_stream_matches(events)||!lp287_event_matches(286)||!lp287_event_matches(287)||
 !lp287_root()[0]||strlen(lp287_root())>=sizeof lp287_life.root)return;
 strcpy(lp287_life.root,lp287_root());lp287_life.loaded=true;
}
static int lp287_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool lp287_source(Sprite2_array *bank)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=42012)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank==enemySpriteSheets+i)bound=true;
 if(!bound||asteroid1_stamp(bank->data,bank->size)!=UINT64_C(0x913975450e0fc00d))return false;
 for(unsigned i=0;i<2;i++)if(asteroid1_record_stamp(lp287_records[i].record)!=lp287_records[i].stamp)return false;
 return true;
}
static bool lp287_colors(void)
{
 for(unsigned i=0;i<COUNTOF(lp287_palette);i++)if((rgb_palette[lp287_palette[i].index]&0xffffffu)!=lp287_palette[i].rgb)return false;
 return true;
}
/* Native287 is static cycle1;288 starts at0 and advances before drawing. */
static bool lp287_shape(unsigned slot,unsigned stage)
{
 if(slot<25||slot>=50)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 unsigned r=e->enemytype;
 if((r!=287&&r!=288)||e->enemydatofs!=enemyDat+r||!lp287_source(e->sprite2s)||
 e->size!=1||e->filter||e->ani!=(r==287?1:20)||e->animin!=1||e->animax||e->aniwhenfire||
 e->aniactive!=(r==288)||e->scoreitem||e->special||e->edamaged||!e->armorleft||e->enemydie||
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=13||
 e->tur[0]||e->tur[1]||e->tur[2]||e->freq[0]||e->freq[1]||e->freq[2]||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=(r==287?(i==0?245:0):((i==6||i==9)?281:283)))return false;
 if(stage==0)return !e->linknum&&e->enemycycle==(r==287?1:0)&&!e->mapoffset&&e->ey==-12&&e->ex>=6&&e->ex<=255;
 if(e->linknum!=lp287_slots[slot].birth.link)return false;
 return r==287?e->enemycycle==1:e->enemycycle<=(unsigned)20;
}
static int lp287_image(unsigned base)
{for(unsigned i=0;i<3;i++)if(lp287_images[i].base==base)return (int)i;return -1;}
uint64_t render_mirror_linked_prop287288_event_begin(unsigned event,unsigned ofs,unsigned pool,int unique)
{
 if(lp287_life.call.live){lp287_life.call.live=false;lp287_fail(3);return 0;}
 int origin=lp287_origin(event);
 if(!lp287_scope()||event!=eventLoc||ofs||pool!=25||unique||!lp287_origin_enabled(origin)||
 !lp287_event_matches(event)||curLoc!=lp287_origins[origin].time)return 0;
 unsigned bit=1u<<(unsigned)origin;
 if(lp287_life.consumed&bit)return 0;
 lp287_life.consumed|=bit; /* First-free allocation failure consumes this origin. */
 if(lp287_life.serial==UINT64_MAX){lp287_life.exhausted=true;return 0;}
 lp287_life.call.live=true;lp287_life.call.token=++lp287_life.serial;lp287_life.call.epoch=lp287_life.epoch;
 lp287_life.call.record=lp287_life.events[event-1].eventdat;lp287_life.call.event=event;
 lp287_life.call.slot=-1;lp287_life.call.generation=0;
 return lp287_life.call.token;
}
void render_mirror_linked_prop287288_enemy_allocated(void *p,unsigned record,int unique)
{
 int s=lp287_slot(p);if(s<0)return;
 render_mirror_linked_prop287288_retired((unsigned)s,LP287_REUSE,100);
 if(lp287_slots[s].generation==UINT64_MAX){lp287_slots[s].exhausted=true;return;}
 if(lp287_slots[s].exhausted)return;
 ++lp287_slots[s].generation;
 if(lp287_life.call.live&&lp287_scope()&&s>=25&&s<50&&enemyAvail[s]==1&&!unique&&
 record==lp287_life.call.record&&lp287_life.call.slot==-1){
  lp287_slots[s].pending=true;lp287_slots[s].record=record;lp287_life.call.slot=s;
  lp287_life.call.generation=lp287_slots[s].generation;
 }
}
void render_mirror_linked_prop287288_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 int s=lp287_slot(p);if(s<0)return;
 lp287_slots[s].initialized=lp287_slots[s].pending&&lp287_life.call.live&&lp287_scope()&&s>=25&&s<50&&
 lp287_life.call.slot==s&&lp287_life.call.generation==lp287_slots[s].generation&&
 record==lp287_life.call.record&&avail==0&&enemyAvail[s]==1&&lp287_shape((unsigned)s,0);
}
void render_mirror_linked_prop287288_event_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=lp287_life.call.slot;unsigned ev=lp287_life.call.event;int origin=lp287_origin(ev);
 bool ok=lp287_life.call.live&&token==lp287_life.call.token&&lp287_life.call.epoch==lp287_life.epoch&&lp287_scope()&&
 s>=25&&s<50&&one_based==(unsigned)s+1&&eventLoc==ev&&lp287_origin_enabled(origin)&&
 lp287_event_matches(ev)&&curLoc==lp287_origins[origin].time&&(lp287_life.consumed&(1u<<(unsigned)origin));
 if(ok){const struct JE_EventRecType *r=lp287_life.events+ev-1;
  ok=lp287_slots[s].pending&&lp287_slots[s].initialized&&lp287_life.call.generation==lp287_slots[s].generation&&
  enemyAvail[s]==0&&enemy[s].enemytype==lp287_life.call.record&&
  enemy[s].ex==r->eventdat2-(mapX-1)*24-12&&enemy[s].ey==-28+r->eventdat5&&
  enemy[s].linknum==r->eventdat4&&!enemy[s].eyc&&!enemy[s].fixedmovey;
 }
 if(s>=0&&s<100){
  lp287_slots[s].live=ok;lp287_slots[s].pending=lp287_slots[s].initialized=false;
  if(ok){
   unsigned ri=lp287_slots[s].record-287;
   lp287_slots[s].cycle=ri?0:1;lp287_slots[s].gate=ri;lp287_slots[s].phase_tick=0;
   lp287_slots[s].witness=lp287_slots[s].generation;lp287_slots[s].epoch=lp287_life.epoch;lp287_slots[s].token=token;
   lp287_slots[s].bank=enemy[s].sprite2s;lp287_slots[s].data=enemy[s].sprite2s->data;lp287_slots[s].bytes=enemy[s].sprite2s->size;
   lp287_slots[s].birth=(LinkedProp287288Birth){.epoch=lp287_life.epoch,.token=token,.generation=lp287_slots[s].generation,
    .slot=(unsigned)s,.record=lp287_slots[s].record,.event=ev,.link=enemy[s].linknum,.bank_role=8,.bank_bytes=42012,
    .bank_stamp=UINT64_C(0x913975450e0fc00d),.record_stamp=lp287_records[ri].stamp,
    .bank_object=(uintptr_t)lp287_slots[s].bank,.bank_data=(uintptr_t)lp287_slots[s].data,
    .birth_frame=fc_frame,.cycle=ri?0:1,.gate=ri,.birth_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,
    .birth_eyc=enemy[s].eyc,.live=true,.initialized=true,.retirement_source_slot=100};
   if(!lp287_shape((unsigned)s,1))render_mirror_linked_prop287288_retired((unsigned)s,LP287_INVALIDATED,100);
   else {lp287_witnessed_records|=1u<<ri;++lp287_witnessed_count[ri];}
  }
 }
 lp287_life.call.live=false;
}
void render_mirror_linked_prop287288_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(lp287_slots[i].live&&lp287_slots[i].bank==bank){++lp287_bank_losses;render_mirror_linked_prop287288_retired(i,LP287_BANK,100);}
 if(lp287_life.call.live){lp287_life.call.live=false;lp287_fail(4);}
}
static bool lp287_witness(unsigned s)
{
 if(s>=100)return false;
 int origin=lp287_origin(lp287_slots[s].birth.event);
 return s>=25&&s<50&&lp287_slots[s].live&&!lp287_slots[s].exhausted&&lp287_slots[s].epoch==lp287_life.epoch&&
 lp287_slots[s].generation==lp287_slots[s].witness&&enemyAvail[s]==0&&
 lp287_origin_enabled(origin)&&lp287_event_matches(lp287_slots[s].birth.event)&&
 (lp287_life.consumed&(1u<<(unsigned)origin))&&
 lp287_slots[s].record==lp287_origins[origin].record&&lp287_slots[s].birth.birth_time==lp287_origins[origin].time&&
 enemy[s].sprite2s&&lp287_slots[s].bank==enemy[s].sprite2s&&lp287_slots[s].data==enemy[s].sprite2s->data&&
 lp287_slots[s].bytes==enemy[s].sprite2s->size&&enemy[s].linknum==lp287_slots[s].birth.link;
}
void render_mirror_linked_prop287288_enemy_animated(unsigned slot)
{
 if(slot>=100||!lp287_slots[slot].live)return;
 if(!lp287_scope()||!lp287_witness(slot)||!lp287_shape(slot,1)||lp287_slots[slot].phase_tick==fc_frame){
  render_mirror_linked_prop287288_retired(slot,LP287_INVALIDATED,100);return;
 }
 unsigned cycle=lp287_slots[slot].cycle;
 if(lp287_slots[slot].record==288){if(++cycle>20)cycle=1;}
 if(enemy[slot].enemycycle!=cycle){render_mirror_linked_prop287288_retired(slot,LP287_INVALIDATED,100);return;}
 lp287_slots[slot].cycle=cycle;lp287_slots[slot].phase_tick=fc_frame;
 LinkedProp287288Birth *b=&lp287_slots[slot].birth;b->cycle=cycle;b->phase_tick=fc_frame;
 ++b->phase_observations;++lp287_phase_observations;
}
/* Hit receipts originate after native normalization of damage, before the
 * original armor/link branches. They never manufacture or perform damage. */
void render_mirror_linked_prop287288_hit_begin(unsigned slot,unsigned damage,unsigned shot)
{
 lp287_life.hit.live=false;
 if(!lp287_scope()||slot>=100||enemyAvail[slot]==1)return;
 unsigned link=enemy[slot].linknum;bool relevant=false;
 for(unsigned s=25;s<50;s++)if(lp287_witness(s)&&(s==slot||lp287_slots[s].birth.link==link))relevant=true;
 if(!relevant||lp287_life.hit_serial==UINT64_MAX)return;
 lp287_life.hit.live=true;lp287_life.hit.token=++lp287_life.hit_serial;lp287_life.hit.slot=slot;
 lp287_life.hit.link=link;lp287_life.hit.damage=damage;lp287_life.hit.armor=enemy[slot].armorleft;lp287_life.hit.shot=shot;
 ++lp287_hit_count;
 if(lp287_witness(slot)){LinkedProp287288Birth *b=&lp287_slots[slot].birth;
  ++b->hit_count;b->last_hit_token=lp287_life.hit.token;b->last_hit_frame=fc_frame;
  b->hit_damage=damage;b->hit_armor_before=enemy[slot].armorleft;b->hit_source_slot=shot;
 }
}
void render_mirror_linked_prop287288_hit_end(void)
{
 if(lp287_life.hit.live){unsigned s=lp287_life.hit.slot;
  if(s<100&&lp287_slots[s].birth.last_hit_token==lp287_life.hit.token)lp287_slots[s].birth.hit_armor_after=enemy[s].armorleft;
 }
 lp287_life.hit.live=false;
}
static void lp287_tick(void)
{
 if(!lp287_enabled()&&!lp287_life.loaded&&!lp287_frame.contributed&&!lp287_frame.active&&!lp287_frame.pending)return;
 if(lp287_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&lp287_frame,0,sizeof lp287_frame);memset(lp287_owned,0,sizeof lp287_owned);memset(lp287_shadows,0,sizeof lp287_shadows);lp287_first_reason=0;
 if(lp287_life.loaded&&!lp287_scope()){lp287_reset();lp287_life.loaded=false;return;}
 for(unsigned i=25;i<50;i++)if(lp287_slots[i].live&&(!lp287_witness(i)||!lp287_shape(i,1)))render_mirror_linked_prop287288_retired(i,LP287_INVALIDATED,100);
}
static bool lp287_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-%u-8.hda",lp287_resources.root,lp287_images[k].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==1080000+lp287_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==lp287_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 lp287_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1,(int)lp287_images[k].base,24,28,0,0,8,rgba};return true;
}
static bool lp287_resources_current(void)
{
 if(!lp287_resources.checked||!lp287_resources.valid||strcmp(lp287_resources.root,lp287_root()))return false;
 for(unsigned i=0;i<3;i++){const Asset *a=lp287_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)lp287_images[i].base||
  a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,172032)!=lp287_images[i].rgba)return false;
 }return true;
}
static bool lp287_ready(void)
{
 if(!lp287_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!lp287_resources.checked){lp287_resources.checked=true;lp287_resources.valid=true;strcpy(lp287_resources.root,lp287_life.root);
 for(unsigned i=0;i<3;i++)if(!lp287_load(i))lp287_resources.valid=false;}
 if(!lp287_resources_current()){lp287_resources.valid=false;return false;}return true;
}
static void lp287_shutdown(void)
{
 lp287_reset();lp287_life.loaded=false;
 for(unsigned i=0;i<3;i++)free(lp287_resources.member[i].rgba);
 memset(&lp287_resources,0,sizeof lp287_resources);
}
static bool lp287_dependencies(bool partial)
{
 if(!lp287_frame.contributed)return true;
 if(lp287_frame.fault||!lp287_scope()||!lp287_colors()||!lp287_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<100;i++)if(lp287_frame.draw[i].token){const LinkedProp287288Draw *d=lp287_frame.draw+i;unsigned s=i;
  if(!lp287_witness(s)||!lp287_shape(s,2)||d->generation!=lp287_slots[s].generation||
  d->token!=lp287_slots[s].birth.token||d->epoch!=lp287_life.epoch||d->record!=lp287_slots[s].record||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||
  d->cycle<1||d->cycle!=enemy[s].enemycycle||lp287_image(d->base)<0||d->base!=enemy[s].egr[d->cycle-1]||
  enemy[s].aniactive!=d->draw_gate||enemy[s].linknum!=d->link)return false;
  if(!d->complete){if(!partial||!lp287_frame.pending||lp287_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=lp287_totals[lp287_image(d->base)])return false;
 }
 return partial||(!lp287_frame.active&&!lp287_frame.pending);
}
/* Per-native-write gate does not hash entire art or source banks. */
static bool lp287_write_current(void)
{
 return !lp287_frame.contributed||(!lp287_frame.fault&&lp287_scope()&&lp287_resources.checked&&lp287_resources.valid&&
 !strcmp(lp287_resources.root,lp287_root())&&(!lp287_frame.active||lp287_witness(lp287_frame.slot)));
}
/* Pure predicate shared by diagnostic snapshots. */
static bool lp287_finish(void){return lp287_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool lp287_guard(void)
{
 if(lp287_finish())return true;
 lp287_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool lp287_before_tile(unsigned slot,int part)
{
 if(lp287_frame.contributed&&!lp287_dependencies(true)){lp287_fail(5);return false;}
 if(lp287_frame.pending&&(lp287_frame.active||slot!=lp287_frame.slot||
 lp287_frame.draw[slot].next>=4||part!=(int)lp287_parts[lp287_frame.draw[slot].next])){lp287_fail(6);return false;}
 return true;
}
static bool lp287_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool lp287_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!lp287_enabled()||slot<25||slot>=50||(enemy[slot].enemytype!=287&&enemy[slot].enemytype!=288))return false;
 if(!fc.frame_active||fc.frame_failed||!lp287_witness(slot)){++lp287_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)lp287_parts[k];k++);
 if(k==4){if(lp287_frame.draw[slot].token)lp287_fail(7);return false;}
 int64_t ox=(int64_t)x-lp287_px[k],oy=(int64_t)y-lp287_py[k];
 LinkedProp287288Draw *d=lp287_frame.draw+slot;
 if(!lp287_geometry(ox,oy)){++lp287_clipped;if(d->token)lp287_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter!=enemy[slot].filter||filter||
 lp287_slots[slot].phase_tick!=fc_frame||
 !lp287_scope()||sheet!=enemy[slot].sprite2s||!lp287_shape(slot,1)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||lp287_image(base)<0||!lp287_colors()||!lp287_ready()){
  if(d->token)lp287_fail(9);
  return false;
 }
 if(k==0){if(d->token||lp287_frame.pending){lp287_fail(10);return false;}}
 else if(!lp287_frame.pending||lp287_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||lp287_frame.pending)lp287_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||lp287_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++lp287_contract_faults;lp287_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++lp287_contract_faults;lp287_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(LinkedProp287288Draw){.frame=fc_frame,.epoch=lp287_life.epoch,.token=lp287_slots[slot].birth.token,
   .generation=lp287_slots[slot].generation,.slot=slot,.record=lp287_slots[slot].record,
   .event=lp287_slots[slot].birth.event,.link=lp287_slots[slot].birth.link,
   .cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,.draw_filter=(unsigned)filter,.base=base,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  lp287_frame.pending=true;lp287_frame.slot=slot;lp287_frame.image=(unsigned)lp287_image(base);lp287_frame.used|=1u<<lp287_frame.image;
 }
 d->part_order[k]=(unsigned)part;
 lp287_frame.part=k;lp287_frame.pixels=0;lp287_frame.active=true;lp287_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool lp287_retire(unsigned off,int style)
{
 bool owned=off<64000&&lp287_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++lp287_blend_retirements;else ++lp287_normal_retirements;
 lp287_owned[off]=lp287_shadows[off]=0;}
 return owned;
}
static bool lp287_pixel(unsigned x,unsigned y,int style)
{
 if(!lp287_frame.active){if(lp287_frame.pending){lp287_fail(14);return true;}return false;}
 LinkedProp287288Draw *d=lp287_frame.draw+lp287_frame.slot;
 unsigned k=lp287_frame.part;
 if(k>=4||lp287_frame.pixels>=lp287_counts[lp287_frame.image][k]){++lp287_contract_faults;lp287_fail(15);return true;}
 const LinkedProp287288Write *w=lp287_native[lp287_frame.image][k]+lp287_frame.pixels;
 unsigned lx=lp287_px[k]+w->x,ly=lp287_py[k]+w->y;
 Uint8 index=w->index;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=index||expected[y*320+x]!=index){
 ++lp287_contract_faults;lp287_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&lp287_resources.member[lp287_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Exact existing native-written cells are opaque. Art alpha never creates
   * coverage: native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  OHS_SURVIVAL_WRITE(canvas,dst,LINKED_PROP287288_HD_STORE_TAG);
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 lp287_owned[off]=(uint8_t)(lp287_frame.slot+1);lp287_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){lp287_fail(17);return true;}
 lp287_frame.writes[lp287_frame.slot][d->callback_count++]=(LinkedProp287288Write){(uint8_t)lx,(uint8_t)ly,index};
 ++lp287_frame.pixels;d->part_count[k]=lp287_frame.pixels;return true;
}
static void lp287_shadow(unsigned off)
{
 if(off<64000&&lp287_owned[off]){if(lp287_shadows[off]<255)++lp287_shadows[off];++lp287_shadow_writes;}
}
static void lp287_end(void)
{
 if(!lp287_frame.active)return;
 unsigned k=lp287_frame.part;LinkedProp287288Draw *d=lp287_frame.draw+lp287_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||lp287_frame.pixels!=lp287_counts[lp287_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++lp287_contract_faults;lp287_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;lp287_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==lp287_totals[lp287_frame.image];lp287_frame.pending=false;
  if(!d->complete){lp287_fail(19);return;}
  if(!lp287_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   lp287_fail(22);family_fault(FC_SOURCE);return;
  }
 }
}
static void lp287_accept(void){lp287_frame.accepted=fc.ready&&!fc.frame_failed&&lp287_finish();}
LinkedProp287288FamilyStatus render_mirror_linked_prop287288_family_status(void)
{
 LinkedProp287288FamilyStatus s={0};s.requested=lp287_enabled();s.loaded=lp287_life.loaded;s.contributed=lp287_frame.contributed;
 s.failed=fc.frame_failed||lp287_frame.fault;s.accepted=lp287_frame.accepted;s.frame=fc_frame;
 s.active=lp287_frame.active;s.pending=lp287_frame.pending;s.active_slot=lp287_frame.slot;
 s.active_part=lp287_frame.part<4?lp287_parts[lp287_frame.part]:UINT_MAX;s.material_mask=lp287_frame.used;s.witnessed_records=lp287_witnessed_records;
 memcpy(s.witnessed_count,lp287_witnessed_count,sizeof s.witnessed_count);
 s.phase_observations=lp287_phase_observations;s.hit_count=lp287_hit_count;s.linked_retirements=lp287_linked_retirements;s.consumed_events=lp287_life.consumed;
 s.blend_retirements=lp287_blend_retirements;s.normal_retirements=lp287_normal_retirements;s.shadow_writes=lp287_shadow_writes;
 s.clipped=lp287_clipped;s.unwitnessed=lp287_unwitnessed;s.lifetime_losses=lp287_lifetime_losses;s.bank_losses=lp287_bank_losses;
 s.contract_faults=lp287_contract_faults;s.first_reason=lp287_first_reason;
 for(unsigned i=0;i<100;i++)s.births[i]=lp287_slots[i].birth;
 memcpy(s.draw,lp287_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<100;i++)if(s.draw[i].token)s.draw[i].final_gate=enemy[i].aniactive;
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=lp287_owned[i]!=0;s.shadowed_cells+=lp287_owned[i]&&lp287_shadows[i];}return s;
}
bool render_mirror_linked_prop287288_pre_draw(LinkedProp287288Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!lp287_frame.active||lp287_frame.part||lp287_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=lp287_frame.draw[lp287_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_linked_prop287288_pre_part(LinkedProp287288Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!lp287_frame.active||lp287_frame.pixels||
 lp287_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=lp287_frame.draw[lp287_frame.slot];unsigned k=lp287_frame.part;*part=lp287_parts[k];
 unsigned x=(unsigned)d->x+lp287_px[k],y=(unsigned)d->y+lp287_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_linked_prop287288_callbacks(unsigned slot,LinkedProp287288Write *out,size_t capacity)
{
 if(slot>=100||!out||capacity<lp287_frame.draw[slot].callback_count)return 0;
 unsigned n=lp287_frame.draw[slot].callback_count;memcpy(out,lp287_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_linked_prop287288_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!lp287_frame.accepted||fc.frame_active||fc.frame_failed||
 !lp287_frame.contributed||!lp287_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,lp287_owned,64000);memcpy(shadows,lp287_shadows,64000);return true;
}
