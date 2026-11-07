/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private ordinary E1 physical2 normal record273, exact original case6 events476/477.
 * Default OFF: TURRET273_COMBAT_ENABLE=1 and TURRET273_BODY_ASSET_DIR. This sparse material
 * cannot grant a display lease. Never writes gameplay, events, RNG or palette.
 */
#include "turret273_family_pins.inc"

static struct {uint64_t generation,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate;uint64_t phase_tick;Turret273Birth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} tp_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;unsigned consumed;char root[1024];
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned event,ei,record,pool;int slot,x,y,map1;} call;
} tp_life;
static struct {bool checked,valid;char root[1024];Asset member[9];} tp_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,part,pixels,image;
 Turret273Draw draw[100];Turret273Write writes[100][672];} tp_frame;
static uint8_t tp_owned[64000],tp_shadows[64000];
/* Exact full authored alpha support. The nine normal source bodies fully cover their native cells. */
static uint8_t tp_extra_owner[4096000],tp_extra_cell[64000];
static uint64_t tp_extra_retirements,tp_phase_observations,tp_shot_resumptions;
static bool tp_extra(size_t n){return tp_frame.contributed&&n<4096000&&tp_extra_owner[n]!=0;}
static uint64_t tp_blend_retirements,tp_normal_retirements,tp_shadow_writes;
static uint64_t tp_clipped,tp_unwitnessed,tp_lifetime_losses,tp_bank_losses,tp_contract_faults;
static unsigned tp_first_reason;
static bool tp_resources_current(void);
static const char *tp_root(void){const char *p=getenv("TURRET273_BODY_ASSET_DIR");return p?p:"";}
static bool tp_enabled(void)
{
 const char *e=getenv("TURRET273_COMBAT_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool tp_level_scope(void)
{
 return tp_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static int tp_record_index(unsigned r){return r==273?0:-1;}
static int tp_event_index(unsigned e){for(unsigned i=0;i<2;i++)if(tp_events[i].event==e)return (int)i;return -1;}
static int tp_image(unsigned b){for(unsigned i=0;i<9;i++)if(tp_images[i].base==b)return (int)i;return -1;}
static bool tp_pool(unsigned slot,unsigned record){return slot>=25&&slot<50&&record==273;}
static bool tp_event_matches(unsigned event)
{
 int ei=tp_event_index(event);
 if(!tp_life.events||tp_life.events!=eventRec||ei<0||maxEvent!=731)return false;
 const struct JE_EventRecType *r=tp_life.events+event-1;
 return r->eventtime==tp_events[ei].time&&r->eventtype==tp_events[ei].type&&r->eventdat==tp_events[ei].record&&
 r->eventdat2==tp_events[ei].x&&r->eventdat3==tp_events[ei].dy&&r->eventdat4==tp_events[ei].link&&!r->eventdat5&&!r->eventdat6;
}
static bool tp_events_current(void)
{
 for(unsigned e=0;e<2;e++)if(!tp_event_matches(tp_events[e].event))return false;
 return true;
}
static bool tp_scope(void)
{
 return tp_life.loaded&&!tp_life.exhausted&&tp_level_scope()&&terrain_file=='z'&&
 tp_events_current()&&!strcmp(tp_life.root,tp_root());
}
static void tp_fail(unsigned reason)
{
 /* Only real renderer/lifecycle failures latch resource integrity loss. */
 if(tp_resources.checked&&!tp_resources_current())tp_resources.valid=false;
 if(!tp_first_reason)tp_first_reason=reason;
 tp_frame.fault=true;tp_frame.accepted=false;tp_frame.active=false;tp_frame.pending=false;
 if(tp_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_turret273_retired(unsigned slot)
{
 if(slot>=100)return;
 if(tp_slots[slot].live||tp_slots[slot].pending){
  ++tp_lifetime_losses;
  if(tp_frame.draw[slot].token)tp_fail(1);
 }
 tp_slots[slot].live=tp_slots[slot].pending=tp_slots[slot].initialized=false;
 tp_slots[slot].birth.live=false;
}
static void tp_reset(void)
{
 bool tracked=tp_life.loaded||tp_life.call.live||tp_frame.contributed||tp_frame.pending;
 if(tp_frame.contributed||tp_frame.pending)tp_fail(2);
 if(tracked)for(unsigned i=0;i<100;i++)render_mirror_turret273_retired(i);
 tp_life.call.live=false;
 if(tp_life.epoch==UINT64_MAX)tp_life.exhausted=true;else ++tp_life.epoch;
 /* Only real level begin clears consumed event origins. */
}
void render_mirror_turret273_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 tp_reset();tp_life.loaded=false;tp_life.events=events;tp_life.consumed=0;
 if(!tp_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!tp_events_current()||!late_reuse_stream_matches(events)||
 !tp_root()[0]||strlen(tp_root())>=sizeof tp_life.root){tp_life.events=NULL;return;}
 for(unsigned i=0;i<100;i++)memset(&tp_slots[i].birth,0,sizeof tp_slots[i].birth);
 strcpy(tp_life.root,tp_root());tp_life.loaded=true;
}
static int tp_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool tp_source(Sprite2_array *bank,unsigned record)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=42012)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank==enemySpriteSheets+i)bound=true;
 return bound&&asteroid1_stamp(bank->data,bank->size)==UINT64_C(0x913975450e0fc00d)&&
 tp_record_index(record)>=0&&asteroid1_record_stamp(record)==tp_records[tp_record_index(record)].stamp;
}
static bool tp_colors(void)
{
 for(unsigned i=0;i<COUNTOF(tp_palette);i++)if((rgb_palette[tp_palette[i].index]&0xffffffu)!=tp_palette[i].rgb)return false;
 return true;
}
/* stage0: live, stage1: exact initialized constructor, stage2: event commit.
 * Positions and idle countdowns are birth-only. Finish uses saved draw origin. */
static bool tp_shape(unsigned slot,unsigned stage)
{
 if(slot>=100)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(!tp_pool(slot,e->enemytype)||e->enemydatofs!=enemyDat+273||!tp_source(e->sprite2s,273)||
 e->size!=1||e->filter||e->ani!=20||e->animin!=1||e->animax||e->aniwhenfire||e->aniactive!=1||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->evalue||e->enemydie||e->linknum||
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=2||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<3;i++)if(e->tur[i]!=(i?0:144)||e->freq[i]!=(i?0:20))return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=tp_records[0].sequence[i])return false;
 if(stage&&(e->mapoffset||e->iced||e->launchwait||e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||
 e->exccadd!=-1||e->eyccadd!=-1||e->exca!=-1||e->eyca!=-1||
 e->xminbounce!=-10000||e->xmaxbounce!=10000||e->yminbounce!=-10000||e->ymaxbounce!=10000))return false;
 if(stage)for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=(i?255:20))return false;
 if(stage==1&&(e->ey!=1||e->ex!=1))return false;
 return stage?e->enemycycle==0:e->enemycycle<=20;
}

uint64_t render_mirror_turret273_event_begin(unsigned event,unsigned typeofs,unsigned pool,int unique)
{
 if(tp_life.call.live){tp_life.call.live=false;tp_fail(3);return 0;}
 int ei=tp_event_index(event);
 if(!tp_scope()||ei<0||event!=eventLoc||typeofs||pool!=tp_events[ei].pool||unique||!tp_event_matches(event)||
 curLoc!=tp_events[ei].time)return 0;
 unsigned bit=1u<<ei;
 if(tp_life.consumed&bit)return 0;
 tp_life.consumed|=bit;
 if(tp_life.serial==UINT64_MAX){tp_life.exhausted=true;return 0;}
 tp_life.call.live=true;tp_life.call.token=++tp_life.serial;tp_life.call.epoch=tp_life.epoch;
 tp_life.call.event=event;tp_life.call.ei=(unsigned)ei;tp_life.call.record=tp_events[ei].record;tp_life.call.pool=pool;
 tp_life.call.slot=-1;tp_life.call.generation=0;
 tp_life.call.map1=mapX;
 tp_life.call.x=tp_events[ei].x-(mapX-1)*24-12;
 tp_life.call.y=-28;
 return tp_life.call.token;
}
void render_mirror_turret273_enemy_allocated(void *p,unsigned record,int unique)
{
 if(!tp_life.loaded)return;
 int s=tp_slot(p);if(s<0)return;
 render_mirror_turret273_retired((unsigned)s);
 if(tp_slots[s].generation==UINT64_MAX){tp_slots[s].exhausted=true;return;}
 if(tp_slots[s].exhausted)return;
 ++tp_slots[s].generation; /* All allocations, including unrelated records. */
 if(tp_life.call.live&&tp_scope()&&tp_pool((unsigned)s,record)&&enemyAvail[s]==1&&!unique&&record==tp_life.call.record&&tp_life.call.slot==-1){
  tp_slots[s].pending=true;tp_slots[s].record=record;tp_life.call.slot=s;tp_life.call.generation=tp_slots[s].generation;
 }
}
void render_mirror_turret273_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 if(!tp_life.loaded)return;
 int s=tp_slot(p);if(s<0)return;
 tp_slots[s].initialized=tp_slots[s].pending&&tp_life.call.live&&tp_scope()&&
 tp_life.call.slot==s&&tp_life.call.generation==tp_slots[s].generation&&
 record==tp_life.call.record&&avail==0&&enemyAvail[s]==1&&tp_shape((unsigned)s,1);
}
void render_mirror_turret273_event_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=tp_life.call.slot;
 bool ok=tp_life.call.live&&token==tp_life.call.token&&tp_life.call.epoch==tp_life.epoch&&tp_scope()&&
 s>=0&&s<100&&tp_pool((unsigned)s,tp_life.call.record)&&one_based==(unsigned)s+1&&eventLoc==tp_life.call.event&&
 curLoc==tp_events[tp_life.call.ei].time&&mapX==tp_life.call.map1;
 if(ok)ok=tp_slots[s].pending&&tp_slots[s].initialized&&tp_life.call.generation==tp_slots[s].generation&&
 enemyAvail[s]==0&&enemy[s].enemytype==273&&tp_shape((unsigned)s,2)&&enemy[s].ex==tp_life.call.x&&enemy[s].ey==tp_life.call.y;
 if(s>=0&&s<100){
  tp_slots[s].live=ok;tp_slots[s].pending=tp_slots[s].initialized=false;
  if(ok){tp_slots[s].cycle=0;tp_slots[s].gate=1;tp_slots[s].phase_tick=UINT64_MAX;tp_slots[s].witness=tp_slots[s].generation;tp_slots[s].bank=enemy[s].sprite2s;
   tp_slots[s].data=enemy[s].sprite2s->data;tp_slots[s].bytes=enemy[s].sprite2s->size;
   tp_slots[s].birth=(Turret273Birth){.epoch=tp_life.epoch,.token=token,.generation=tp_slots[s].generation,
    .slot=(unsigned)s,.event=tp_life.call.event,.record=tp_slots[s].record,.link=enemy[s].linknum,.cycle=0,.gate=tp_slots[s].gate,.bank_role=8,.bank_bytes=42012,
    .bank_stamp=UINT64_C(0x913975450e0fc00d),.record_stamp=tp_records[tp_record_index(tp_slots[s].record)].stamp,
    .bank_object=(uintptr_t)tp_slots[s].bank,.bank_data=(uintptr_t)tp_slots[s].data,
    .event_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 tp_life.call.live=false;
}
void render_mirror_turret273_bank_changed(Sprite2_array *bank)
{
 if(!tp_life.loaded&&!tp_life.call.live)return;
 for(unsigned i=0;i<100;i++)if(tp_slots[i].live&&tp_slots[i].bank==bank){++tp_bank_losses;render_mirror_turret273_retired(i);}
 if(tp_life.call.live){tp_life.call.live=false;tp_fail(4);}
}
static bool tp_witness(unsigned s)
{
 return s<100&&tp_pool(s,tp_slots[s].record)&&tp_slots[s].live&&!tp_slots[s].exhausted&&
 tp_slots[s].birth.epoch==tp_life.epoch&&tp_event_matches(tp_slots[s].birth.event)&&
 tp_slots[s].generation==tp_slots[s].witness&&enemyAvail[s]==0&&enemy[s].enemytype==tp_slots[s].record&&enemy[s].sprite2s&&
 tp_slots[s].bank==enemy[s].sprite2s&&tp_slots[s].data==enemy[s].sprite2s->data&&tp_slots[s].bytes==enemy[s].sprite2s->size;
}
static void tp_enemy_animated(unsigned slot)
{
 if(slot>=100||!tp_slots[slot].live)return;
 if(!tp_scope()||!tp_witness(slot)||!tp_shape(slot,0)||tp_slots[slot].phase_tick==fc_frame||
 enemy[slot].ex+tempMapXOfs<=-29||enemy[slot].ex+tempMapXOfs>=300){render_mirror_turret273_retired(slot);return;}
 unsigned cycle=tp_slots[slot].cycle+1;if(cycle>20)cycle=1;
 if(enemy[slot].enemycycle!=cycle||enemy[slot].aniactive!=1){render_mirror_turret273_retired(slot);return;}
 tp_slots[slot].cycle=cycle;tp_slots[slot].gate=1;tp_slots[slot].phase_tick=fc_frame;
 Turret273Birth *b=&tp_slots[slot].birth;b->cycle=cycle;b->gate=1;b->phase_tick=fc_frame;
 ++b->phase_observations;++tp_phase_observations;
}
/* Birth-only exact native provenance. Shot lifetime retains its own token and
 * generation after this parent dies, exits, changes bank, or is reused. */
static bool turret273_emitter(unsigned slot,unsigned weapon,uint64_t *token,unsigned *event)
{
 if(!token||!event||weapon!=144||!tp_scope()||!tp_witness(slot)||!tp_shape(slot,0)||
 tp_slots[slot].phase_tick!=fc_frame||tp_slots[slot].cycle!=enemy[slot].enemycycle||
 tp_slots[slot].gate!=enemy[slot].aniactive)return false;
 *token=tp_slots[slot].birth.token;*event=tp_slots[slot].birth.event;return true;
}

static void tp_tick(void)
{
 /* Inactive feature: no resource access, census, array clear or slot scan. */
 if(!tp_life.loaded&&!tp_frame.contributed&&!tp_frame.pending)return;
 if(tp_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&tp_frame,0,sizeof tp_frame);memset(tp_owned,0,sizeof tp_owned);memset(tp_shadows,0,sizeof tp_shadows);
 memset(tp_extra_owner,0,sizeof tp_extra_owner);memset(tp_extra_cell,0,sizeof tp_extra_cell);tp_first_reason=0;
 if(tp_life.loaded&&!tp_scope()){tp_reset();tp_life.loaded=false;return;}
 for(unsigned i=0;i<100;i++)if(tp_slots[i].live&&(!tp_witness(i)||!tp_shape(i,0)||enemy[i].enemycycle!=tp_slots[i].cycle||enemy[i].aniactive!=tp_slots[i].gate))render_mirror_turret273_retired(i);
}
static bool tp_load(unsigned image)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-%u-8.hda",tp_resources.root,tp_images[image].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==tp_images[image].id&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==tp_images[image].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 tp_resources.member[image]=(Asset){true,true,ASSET_ASTEROID1_TURRET273,tp_images[image].base,24,28,0,0,8,rgba};return true;
}
static bool tp_resources_current(void)
{
 if(!tp_resources.checked||!tp_resources.valid||strcmp(tp_resources.root,tp_root()))return false;
 for(unsigned image=0;image<9;image++){
 const Asset *a=tp_resources.member+image;
 if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1_TURRET273||a->index!=tp_images[image].base||a->w!=24||a->h!=28||
 a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||asteroid1_stamp(a->rgba,172032)!=tp_images[image].rgba)return false;
 }
 return true;
}
static bool tp_ready(void)
{
 if(!tp_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!tp_resources.checked){tp_resources.checked=true;strcpy(tp_resources.root,tp_life.root);tp_resources.valid=true;for(unsigned i=0;i<9;i++)if(!tp_load(i))tp_resources.valid=false;}
 if(!tp_resources_current()){tp_resources.valid=false;return false;}
 return true;
}
static void tp_shutdown(void)
{
 tp_reset();tp_life.loaded=false;for(unsigned i=0;i<9;i++)free(tp_resources.member[i].rgba);memset(&tp_resources,0,sizeof tp_resources);
}
static bool tp_dependencies(bool partial)
{
 if(!tp_frame.contributed)return true;
 if(tp_frame.fault||!tp_scope()||!tp_colors()||!tp_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<100;i++)if(tp_frame.draw[i].token){const Turret273Draw *d=tp_frame.draw+i;unsigned s=i;
  if(!tp_witness(s)||!tp_shape(s,0)||d->generation!=tp_slots[s].generation||
  d->token!=tp_slots[s].birth.token||d->epoch!=tp_life.epoch||d->event!=tp_slots[s].birth.event||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||d->record!=tp_slots[s].record||tp_image(d->base)<0||
  d->cycle!=enemy[s].enemycycle||d->base!=enemy[s].egr[d->cycle-1]||
  enemy[s].aniactive!=d->draw_gate)return false;
  if(!d->complete){if(!partial||!tp_frame.pending||tp_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=tp_totals[tp_image(d->base)]||(!partial&&d->extra_stores!=tp_images[tp_image(d->base)].extra))return false;
 }
 return partial||(!tp_frame.active&&!tp_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool tp_finish(void){return tp_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool tp_guard(void)
{
 if(tp_finish())return true;
 tp_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool tp_before_tile(unsigned slot,int part)
{
 if(tp_frame.contributed&&!tp_dependencies(true)){tp_fail(5);return false;}
 if(tp_frame.pending&&(tp_frame.active||slot!=tp_frame.slot||
 tp_frame.draw[slot].next>=4||part!=(int)tp_parts[tp_frame.draw[slot].next])){tp_fail(6);return false;}
 return true;
}
static bool tp_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool tp_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!tp_life.loaded||slot>=100||tp_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!tp_witness(slot)){++tp_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)tp_parts[k];k++);
 if(k==4){if(tp_frame.contributed)tp_fail(7);return false;}
 int64_t ox=(int64_t)x-tp_px[k],oy=(int64_t)y-tp_py[k];
 Turret273Draw *d=tp_frame.draw+slot;
 if(!tp_geometry(ox,oy)){++tp_clipped;if(d->token)tp_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter||
 !tp_scope()||sheet!=enemy[slot].sprite2s||!tp_shape(slot,0)||tp_slots[slot].phase_tick!=fc_frame||enemy[slot].enemycycle<1||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||tp_image(base)<0||!tp_colors()||!tp_ready()){
  if(d->token||tp_frame.contributed)tp_fail(9);
  return false;
 }
 if(k==0){if(d->token||tp_frame.pending){tp_fail(10);return false;}}
 else if(!tp_frame.pending||tp_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||tp_frame.pending)tp_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||tp_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++tp_contract_faults;tp_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++tp_contract_faults;tp_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(Turret273Draw){.frame=fc_frame,.epoch=tp_life.epoch,.token=tp_slots[slot].birth.token,
   .generation=tp_slots[slot].generation,.slot=slot,.event=tp_slots[slot].birth.event,.record=tp_slots[slot].record,.cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,
   .base=base,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  tp_frame.pending=true;tp_frame.slot=slot;tp_frame.image=(unsigned)tp_image(base);
 }
 d->part_order[k]=(unsigned)part;
 tp_frame.part=k;tp_frame.pixels=0;tp_frame.active=true;tp_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool tp_retire(unsigned off,int style)
{
 if(!tp_frame.contributed)return false;
 bool owned=off<64000&&tp_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++tp_blend_retirements;else ++tp_normal_retirements;
 tp_owned[off]=tp_shadows[off]=0;}
 if(off<64000&&style!=MIRROR_SHADOW&&tp_extra_cell[off]){
  unsigned x=off%320,y=off/320;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   size_t n=(y*8+sy)*2560+x*8+sx;tp_extra_retirements+=tp_extra_owner[n]!=0;tp_extra_owner[n]=0;
  }
  tp_extra_cell[off]=0;
 }
 return owned;
}
static bool tp_pixel(unsigned x,unsigned y,int style)
{
 if(!tp_frame.active){if(tp_frame.pending){tp_fail(14);return true;}return false;}
 Turret273Draw *d=tp_frame.draw+tp_frame.slot;
 unsigned k=tp_frame.part;
 if(k>=4||tp_frame.pixels>=tp_counts[tp_frame.image][k]){++tp_contract_faults;tp_fail(15);return true;}
 const Turret273Write *w=tp_native[tp_frame.image][k]+tp_frame.pixels;
 unsigned lx=tp_px[k]+w->x,ly=tp_py[k]+w->y;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=w->index||expected[y*320+x]!=w->index){
 ++tp_contract_faults;tp_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&tp_resources.member[tp_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 tp_owned[off]=(uint8_t)(tp_frame.slot+1);tp_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){tp_fail(17);return true;}
 tp_frame.writes[tp_frame.slot][d->callback_count++]=(Turret273Write){(uint8_t)lx,(uint8_t)ly,w->index};
 ++tp_frame.pixels;d->part_count[k]=tp_frame.pixels;return true;
}
static void tp_shadow(unsigned off)
{
 if(off<64000&&tp_owned[off]){if(tp_shadows[off]<255)++tp_shadows[off];++tp_shadow_writes;}
}
/* Same narrow authored-support policy as firing_rock462: exact nonzero-alpha
 * native-hole subpixels only, after a complete observed native quartet. No
 * native INDEX, selected[], native owner, global permission or cached underlay. */
static void tp_authored_support(Turret273Draw *d)
{
 
 const Asset *a=tp_resources.member+tp_frame.image;
 for(unsigned i=0;i<tp_images[tp_frame.image].extra;i++){
  unsigned ax=tp_extras[tp_frame.image][i].x,ay=tp_extras[tp_frame.image][i].y;
  const Uint8 *art=a->rgba+(ay*192+ax)*4;
  unsigned off=((unsigned)d->y+ay/8)*320+(unsigned)d->x+ax/8;
  if(tp_native_mask[tp_frame.image][(ay/8)*24+ax/8]||!art[3]||expected[off]!=((const Uint8 *)fc_source_pixels)[off]){
   tp_fail(21);family_fault(FC_ORDER);return;
  }
  size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
  Uint32 *dst=(Uint32 *)canvas->pixels+n;*dst=blend_rgba(*dst,art,art[3]);
  tp_extra_owner[n]=(uint8_t)(d->slot+1);tp_extra_cell[off]=1;++d->extra_stores;
 }
 if(d->extra_stores!=tp_images[tp_frame.image].extra){tp_fail(21);family_fault(FC_ORDER);}
}
static void tp_end(void)
{
 if(!tp_frame.active)return;
 unsigned k=tp_frame.part;Turret273Draw *d=tp_frame.draw+tp_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||tp_frame.pixels!=tp_counts[tp_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++tp_contract_faults;tp_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;tp_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==tp_totals[tp_frame.image];tp_frame.pending=false;
  if(!d->complete){tp_fail(19);return;}
  if(!tp_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   tp_fail(22);family_fault(FC_SOURCE);return;
  }
  tp_authored_support(d);
 }
}
static void tp_accept(void){tp_frame.accepted=fc.ready&&!fc.frame_failed&&tp_finish();}
Turret273FamilyStatus render_mirror_turret273_family_status(void)
{
 Turret273FamilyStatus s={0};s.requested=tp_enabled();s.loaded=tp_life.loaded;s.contributed=tp_frame.contributed;
 s.failed=fc.frame_failed||tp_frame.fault;s.accepted=tp_frame.accepted;s.frame=fc_frame;
 s.active=tp_frame.active;s.pending=tp_frame.pending;s.active_slot=tp_frame.slot;
 s.active_part=tp_frame.part<4?tp_parts[tp_frame.part]:UINT_MAX;s.consumed_events=tp_life.consumed;
 s.blend_retirements=tp_blend_retirements;s.normal_retirements=tp_normal_retirements;s.shadow_writes=tp_shadow_writes;
 s.clipped=tp_clipped;s.unwitnessed=tp_unwitnessed;s.lifetime_losses=tp_lifetime_losses;s.bank_losses=tp_bank_losses;
 s.contract_faults=tp_contract_faults;s.first_reason=tp_first_reason;
 s.phase_observations=tp_phase_observations;s.shot_resumptions=tp_shot_resumptions;s.extra_retirements=tp_extra_retirements;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=tp_extra_owner[i]!=0;
 for(unsigned i=0;i<100;i++)s.births[i]=tp_slots[i].birth;
 memcpy(s.draw,tp_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=tp_owned[i]!=0;s.shadowed_cells+=tp_owned[i]&&tp_shadows[i];}return s;
}
bool render_mirror_turret273_pre_draw(Turret273Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!tp_frame.active||tp_frame.part||tp_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=tp_frame.draw[tp_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_turret273_pre_part(Turret273Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!tp_frame.active||tp_frame.pixels||
 tp_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=tp_frame.draw[tp_frame.slot];unsigned k=tp_frame.part;*part=tp_parts[k];
 unsigned x=(unsigned)d->x+tp_px[k],y=(unsigned)d->y+tp_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_turret273_callbacks(unsigned slot,Turret273Write *out,size_t capacity)
{
 if(slot>=100||!out||capacity<tp_frame.draw[slot].callback_count)return 0;
 unsigned n=tp_frame.draw[slot].callback_count;memcpy(out,tp_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_turret273_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!tp_frame.accepted||fc.frame_active||fc.frame_failed||
 !tp_frame.contributed||!tp_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,tp_owned,64000);memcpy(shadows,tp_shadows,64000);return true;
}
bool render_mirror_turret273_extra_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=4096000||!tp_frame.accepted||fc.frame_active||fc.frame_failed||
 !tp_frame.contributed||!tp_finish()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||
 !b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(out,tp_extra_owner,bytes);return true;
}
