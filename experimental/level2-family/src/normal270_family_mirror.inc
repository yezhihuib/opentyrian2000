/* Narrow normal270-only body observer. Original compound indices retained but inaccessible.
 * Only two origins244/245; render window curLoc<1960 and eventLoc<=259.
 * No309..312 assets or admission; no projectile rendering. */
/* Default-OFF E1 physical2 compound309..312 (events242/243) and firing270
 * (244/245). Ten independent native allocations; no quartet liveness gate.
 * Sidecars only. Native event, movement, collision, weapon, RNG and disposal
 * remain authoritative. Four native stores per body, exact fullrect672 support. */
#include "normal270_native.inc"
static struct {uint64_t generation,epoch,token,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate;uint64_t phase_tick;Normal270Birth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} f270_slots[100];
static struct {uint64_t epoch,serial,hit_serial;bool exhausted,loaded;char root[1024];unsigned consumed;
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned record,event,component;int slot;} call;
 struct {bool live;uint64_t token;unsigned slot,link,damage,armor,shot;} hit;
} f270_life;
static struct {bool checked,valid;char root[1024];Asset member[15];} f270_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,image,part,pixels,used;
 Normal270Draw draw[100];Normal270Write writes[100][672];} f270_frame;
static unsigned f270_witnessed_records;
static uint64_t f270_witnessed_count[5],f270_phase_observations,f270_hit_count,f270_linked_retirements,f270_shot_resumptions;
static bool f270_resources_current(void);
static uint8_t f270_owned[64000],f270_shadows[64000];
static uint64_t f270_blend_retirements,f270_normal_retirements,f270_shadow_writes;
static uint64_t f270_clipped,f270_unwitnessed,f270_lifetime_losses,f270_bank_losses,f270_contract_faults;
static unsigned f270_first_reason;
static const char *f270_root(void){const char *p=getenv("NORMAL270_ASSET_DIR");return p?p:"";}
static bool f270_enabled(void)
{
 const char *e=getenv("NORMAL270_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool f270_level_scope(void)
{
 return f270_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static int f270_record_index(unsigned r){return r==270?4:-1;}
static bool f270_event_matches(unsigned event)
{
 if(!f270_life.events||f270_life.events!=eventRec||maxEvent!=731||event<244||event>245)return false;
 const struct JE_EventRecType *r=f270_life.events+event-1;
 static const unsigned xs[4]={66,162,90,162};unsigned k=event-242;
 return r->eventtime==(k<2?1840:1896)&&r->eventtype==(k<2?12:6)&&r->eventdat==(k<2?309:270)&&
 r->eventdat2==(int)xs[k]&&!r->eventdat3&&r->eventdat4==(k<2?24+k:0)&&!r->eventdat5&&!r->eventdat6;
}
static struct {bool active,failed;unsigned event,next;uint64_t observations,mutations;
 struct JE_EventRecType before,expected[731];} f270_script;
static bool f270_row_equal(const struct JE_EventRecType *a,const struct JE_EventRecType *b)
{
 return a->eventtime==b->eventtime&&a->eventtype==b->eventtype&&a->eventdat==b->eventdat&&
 a->eventdat2==b->eventdat2&&a->eventdat3==b->eventdat3&&a->eventdat4==b->eventdat4&&
 a->eventdat5==b->eventdat5&&a->eventdat6==b->eventdat6;
}
static bool f270_events_current(void)
{
 return f270_event_matches(244)&&f270_event_matches(245);
}
static bool f270_scope(void)
{
 return f270_life.loaded&&!f270_life.exhausted&&f270_level_scope()&&terrain_file=='z'&&
 !f270_script.failed&&f270_events_current()&&!strcmp(f270_life.root,f270_root())&&curLoc<1960&&eventLoc<=259;
}
static void f270_fail(unsigned reason)
{
 if(!f270_first_reason)f270_first_reason=reason;
 f270_frame.fault=true;f270_frame.accepted=false;f270_frame.active=f270_frame.pending=false;
 if(f270_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_normal270_retired(unsigned slot,unsigned reason,unsigned source)
{
 if(slot>=100)return;
 if(f270_slots[slot].live||f270_slots[slot].pending){
  ++f270_lifetime_losses;
  if(f270_frame.draw[slot].token)f270_fail(1);
 }
 Normal270Birth *b=&f270_slots[slot].birth;
 if(b->live){
  b->retired_frame=fc_frame;b->retired_y=enemy[slot].ey;b->retirement_reason=reason;b->retirement_source_slot=source;
  if((reason==F270_DIRECT_LETHAL||reason==F270_LINKED_LETHAL)&&f270_life.hit.live&&
   source==f270_life.hit.slot&&f270_life.hit.armor<=f270_life.hit.damage&&
   (source==slot||(b->link&&b->link==f270_life.hit.link))){
   b->retirement_hit_token=f270_life.hit.token;
   if(source!=slot)++f270_linked_retirements;
  }
 }
 b->live=false;
 f270_slots[slot].live=f270_slots[slot].pending=f270_slots[slot].initialized=false;
}
static void f270_reset(void)
{
 if(f270_frame.contributed||f270_frame.active||f270_frame.pending)f270_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_normal270_retired(i,F270_INVALIDATED,100);
 f270_life.call.live=f270_life.hit.live=false;
 if(f270_life.epoch==UINT64_MAX)f270_life.exhausted=true;else ++f270_life.epoch;
 /* Original event consumption survives renderer resets, not real level loads. */
}
void render_mirror_normal270_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 f270_reset();f270_life.loaded=false;f270_life.consumed=0;f270_life.events=events;
 f270_witnessed_records=0;memset(f270_witnessed_count,0,sizeof f270_witnessed_count);
 for(unsigned i=0;i<100;i++)memset(&f270_slots[i].birth,0,sizeof f270_slots[i].birth);
 if(!f270_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
 !f284_stream_matches(events)||!f270_event_matches(244)||!f270_event_matches(245)||
 !f270_root()[0]||strlen(f270_root())>=sizeof f270_life.root)return;
 strcpy(f270_life.root,f270_root());f270_life.loaded=true;
 memset(&f270_script,0,sizeof f270_script);f270_script.next=1;
 memcpy(f270_script.expected,events,sizeof f270_script.expected);
}
void render_mirror_normal270_script_before(unsigned event)
{
 if(!f270_life.loaded)return;
 if(f270_script.active||(!f270_life.loaded||f270_life.exhausted||!f270_level_scope()||f270_script.failed||!f270_events_current())||event<1||event>731||event!=eventLoc||event!=f270_script.next||
 !f270_row_equal(eventRec+event-1,f270_script.expected+event-1)||curLoc<eventRec[event-1].eventtime){f270_script.failed=true;f270_fail(23);return;}
 f270_script.active=true;f270_script.event=event;f270_script.before=eventRec[event-1];
}
void render_mirror_normal270_script_after(unsigned event)
{
 if(!f270_life.loaded)return;
 if(!f270_script.active||f270_script.failed||event!=f270_script.event||event!=eventLoc||event>731){
  f270_script.failed=true;f270_fail(24);return;
 }
 struct JE_EventRecType next=f270_script.before;
 const struct JE_EventRecType *actual=eventRec+event-1;
 if(next.eventtype==12)next.eventdat6=0;
 if(next.eventtype==33&&next.eventdat==533&&
 (actual->eventdat==533||(actual->eventdat>=829&&actual->eventdat<=834)))next.eventdat=actual->eventdat;
 if(!f270_row_equal(&next,actual)||!f270_events_current()){f270_script.failed=true;f270_fail(25);return;}
 f270_script.mutations+=!f270_row_equal(&f270_script.before,actual);
 f270_script.expected[event-1]=next;++f270_script.observations;f270_script.next=event+1;f270_script.active=false;
}
static int f270_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static uint64_t f270_weapon_stamp(unsigned weapon)
{
 const JE_WeaponType *w=&weapons[weapon];Uint8 b[80];size_t n=0;
#define F270_BYTE(v) do{b[n++]=(Uint8)(v);}while(0)
#define F270_WORD(v) do{unsigned word_=(unsigned)(v);F270_BYTE(word_);F270_BYTE(word_>>8);}while(0)
 F270_WORD(w->drain);F270_BYTE(w->shotrepeat);F270_BYTE(w->multi);F270_WORD(w->weapani);
 F270_BYTE(w->max);F270_BYTE(w->tx);F270_BYTE(w->ty);F270_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)F270_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)F270_WORD(w->sg[i]);
 F270_BYTE(w->acceleration);F270_BYTE(w->accelerationx);F270_BYTE(w->circlesize);
 F270_BYTE(w->sound);F270_BYTE(w->trail);F270_BYTE(w->shipblastfilter);
#undef F270_WORD
#undef F270_BYTE
 return n==sizeof(b)?asteroid1_stamp(b,sizeof(b)):0;
}
static bool f270_source(Sprite2_array *bank,unsigned record)
{
 int ri=f270_record_index(record);if(ri<0||!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data)return false;
 const unsigned role=record==270?8:23,bytes=record==270?42012:46566;
 const uint64_t stamp=record==270?UINT64_C(0x913975450e0fc00d):F270_NEWSHS_STAMP;
 bool bound=false;for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==role&&bank==enemySpriteSheets+i)bound=true;
 if(!bound||bank->size!=bytes||asteroid1_stamp(bank->data,bank->size)!=stamp||
 asteroid1_record_stamp(record)!=f270_records[ri].stamp)return false;
 return record!=270||(f270_weapon_stamp(145)==UINT64_C(0x387b219ee9cab017)&&f270_weapon_stamp(146)==UINT64_C(0x4623a676db5268a8));
}
static bool f270_colors(void)
{
 for(unsigned i=0;i<COUNTOF(f270_palette);i++)if((rgb_palette[f270_palette[i].index]&0xffffffu)!=f270_palette[i].rgb)return false;
 return true;
}
/* Constructor cycle0 for compound, cycle1/idle2 for turret. Pose derives only
 * from actual native phase and successful native bullet allocation observers. */
static bool f270_shape(unsigned slot,unsigned stage)
{
 if(slot<25||slot>=50)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;unsigned r=e->enemytype;int ri=f270_record_index(r);bool turret=r==270;
 if(ri<0||e->enemydatofs!=enemyDat+r||!f270_source(e->sprite2s,r)||
 e->size!=1||e->ani!=(turret?6:20)||e->animin!=1||e->animax!=(turret?6:0)||e->aniwhenfire!=(turret?2:0)||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->enemydie||
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=(turret?2:12)||
 e->tur[0]!=(turret?145:0)||e->tur[1]!=(turret?146:0)||e->tur[2]||
 e->freq[0]!=(turret?40:0)||e->freq[1]!=(turret?41:0)||e->freq[2]||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=f270_sequences[ri][i])return false;
 if(stage==0)return !e->linknum&&!e->filter&&e->enemycycle==(turret?1:0)&&e->aniactive==(turret?2:1)&&!e->mapoffset&&e->ey==1&&e->ex==1;
 if(e->linknum!=f270_slots[slot].birth.link)return false;
 if(!turret)return e->aniactive==1&&e->enemycycle<=20;
 return (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==6))||
 (e->aniactive==1&&e->enemycycle>=1&&e->enemycycle<=6);
}
static int f270_image(unsigned base)
{for(unsigned i=12;i<15;i++)if(i>=12&&f270_images[i].base==base)return (int)i;return -1;}
uint64_t render_mirror_normal270_event_begin(unsigned event,unsigned ofs,unsigned pool,int unique)
{
 if(f270_life.call.live){f270_life.call.live=false;f270_fail(3);return 0;}
 if(!f270_scope()||event!=eventLoc||pool!=25||unique||!f270_event_matches(event)||
 curLoc!=f270_life.events[event-1].eventtime||ofs||!f270_script.active||f270_script.event!=event)return 0;
 unsigned bit=1u<<(event-244);
 if(f270_life.consumed&bit)return 0;
 f270_life.consumed|=bit; /* First-free allocation failure consumes this origin. */
 if(f270_life.serial==UINT64_MAX){f270_life.exhausted=true;return 0;}
 f270_life.call.live=true;f270_life.call.token=++f270_life.serial;f270_life.call.epoch=f270_life.epoch;
 f270_life.call.record=f270_life.events[event-1].eventdat+ofs;f270_life.call.event=event;f270_life.call.component=ofs;
 f270_life.call.slot=-1;f270_life.call.generation=0;
 return f270_life.call.token;
}
void render_mirror_normal270_enemy_allocated(void *p,unsigned record,int unique)
{
 int s=f270_slot(p);if(s<0)return;
 render_mirror_normal270_retired((unsigned)s,F270_REUSE,100);
 if(f270_slots[s].generation==UINT64_MAX){f270_slots[s].exhausted=true;return;}
 if(f270_slots[s].exhausted)return;
 ++f270_slots[s].generation;
 if(f270_life.call.live&&f270_scope()&&s>=25&&s<50&&enemyAvail[s]==1&&!unique&&
 record==f270_life.call.record&&f270_life.call.slot==-1){
  f270_slots[s].pending=true;f270_slots[s].record=record;f270_life.call.slot=s;
  f270_life.call.generation=f270_slots[s].generation;
 }
}
void render_mirror_normal270_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 int s=f270_slot(p);if(s<0)return;
 f270_slots[s].initialized=f270_slots[s].pending&&f270_life.call.live&&f270_scope()&&s>=25&&s<50&&
 f270_life.call.slot==s&&f270_life.call.generation==f270_slots[s].generation&&
 record==f270_life.call.record&&avail==0&&enemyAvail[s]==1&&f270_shape((unsigned)s,0);
}
void render_mirror_normal270_event_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=f270_life.call.slot;unsigned ev=f270_life.call.event;
 bool ok=f270_life.call.live&&token==f270_life.call.token&&f270_life.call.epoch==f270_life.epoch&&f270_scope()&&
 s>=25&&s<50&&one_based==(unsigned)s+1&&eventLoc==ev&&f270_event_matches(ev)&&curLoc==f270_life.events[ev-1].eventtime&&f270_script.active&&f270_script.event==ev;
 if(ok){const struct JE_EventRecType *r=f270_life.events+ev-1;
  ok=f270_slots[s].pending&&f270_slots[s].initialized&&f270_life.call.generation==f270_slots[s].generation&&
  enemyAvail[s]==0&&enemy[s].enemytype==f270_life.call.record&&
  enemy[s].ex==r->eventdat2-(mapX-1)*24-12+(f270_life.call.component%2?24:0)&&
  enemy[s].ey==-28-(f270_life.call.component>=2?28:0)&&
  enemy[s].linknum==r->eventdat4&&!enemy[s].eyc&&!enemy[s].fixedmovey;
 }
 if(s>=0&&s<100){
  f270_slots[s].live=ok;f270_slots[s].pending=f270_slots[s].initialized=false;
  if(ok){
   unsigned ri=(unsigned)f270_record_index(f270_slots[s].record);bool turret=ri==4;
   f270_slots[s].cycle=turret?1:0;f270_slots[s].gate=turret?2:1;f270_slots[s].phase_tick=0;
   f270_slots[s].witness=f270_slots[s].generation;f270_slots[s].epoch=f270_life.epoch;f270_slots[s].token=token;
   f270_slots[s].bank=enemy[s].sprite2s;f270_slots[s].data=enemy[s].sprite2s->data;f270_slots[s].bytes=enemy[s].sprite2s->size;
   f270_slots[s].birth=(Normal270Birth){.epoch=f270_life.epoch,.token=token,.generation=f270_slots[s].generation,
    .slot=(unsigned)s,.record=f270_slots[s].record,.event=ev,.link=enemy[s].linknum,.bank_role=turret?8:23,.bank_bytes=turret?42012:46566,
    .bank_stamp=turret?UINT64_C(0x913975450e0fc00d):F270_NEWSHS_STAMP,.record_stamp=f270_records[ri].stamp,
    .bank_object=(uintptr_t)f270_slots[s].bank,.bank_data=(uintptr_t)f270_slots[s].data,
    .birth_frame=fc_frame,.cycle=turret?1:0,.gate=turret?2:1,.birth_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,
    .birth_eyc=enemy[s].eyc,.live=true,.initialized=true,.retirement_source_slot=100};
   if(!f270_shape((unsigned)s,1))render_mirror_normal270_retired((unsigned)s,F270_INVALIDATED,100);
   else {f270_witnessed_records|=1u<<ri;++f270_witnessed_count[ri];}
  }
 }
 f270_life.call.live=false;
}
void render_mirror_normal270_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(f270_slots[i].live&&f270_slots[i].bank==bank){++f270_bank_losses;render_mirror_normal270_retired(i,F270_BANK,100);}
 if(f270_life.call.live){f270_life.call.live=false;f270_fail(4);}
}
static bool f270_witness(unsigned s)
{
 return s>=25&&s<50&&f270_slots[s].live&&!f270_slots[s].exhausted&&f270_slots[s].epoch==f270_life.epoch&&
 f270_slots[s].generation==f270_slots[s].witness&&enemyAvail[s]==0&&
 enemy[s].sprite2s&&f270_slots[s].bank==enemy[s].sprite2s&&f270_slots[s].data==enemy[s].sprite2s->data&&
 f270_slots[s].bytes==enemy[s].sprite2s->size&&enemy[s].linknum==f270_slots[s].birth.link;
}
void render_mirror_normal270_enemy_animated(unsigned slot)
{
 if(slot>=100||!f270_slots[slot].live)return;
 if(!f270_scope()||!f270_witness(slot)||!f270_shape(slot,1)||f270_slots[slot].phase_tick==fc_frame){
  render_mirror_normal270_retired(slot,F270_INVALIDATED,100);return;
 }
 unsigned cycle=f270_slots[slot].cycle,gate=f270_slots[slot].gate;bool turret=f270_slots[slot].record==270;
 if(gate==1){++cycle;if(turret&&cycle==6)gate=2;else if(cycle>(turret?6u:20u))cycle=1;}
 if(enemy[slot].enemycycle!=cycle||enemy[slot].aniactive!=gate){render_mirror_normal270_retired(slot,F270_INVALIDATED,100);return;}
 f270_slots[slot].cycle=cycle;f270_slots[slot].gate=gate;f270_slots[slot].phase_tick=fc_frame;
 Normal270Birth *b=&f270_slots[slot].birth;b->cycle=cycle;b->gate=gate;b->phase_tick=fc_frame;
 ++b->phase_observations;++f270_phase_observations;
}
void render_mirror_normal270_shot_fired(unsigned slot,unsigned weapon,unsigned turret,unsigned shot_slot)
{
 if(slot>=100||!f270_slots[slot].live||f270_slots[slot].record!=270)return;
 if(!f270_scope()||!f270_witness(slot)||!f270_shape(slot,2)||
 !((weapon==145&&turret==1)||(weapon==146&&turret==2))||shot_slot>=ENEMY_SHOT_MAX||enemyShotAvail[shot_slot]!=0||
 f270_slots[slot].phase_tick!=fc_frame||f270_slots[slot].gate!=2||
 (f270_slots[slot].cycle!=1&&f270_slots[slot].cycle!=6)||enemy[slot].enemycycle!=f270_slots[slot].cycle||enemy[slot].aniactive!=1){
 render_mirror_normal270_retired(slot,F270_INVALIDATED,100);return;}
 f270_slots[slot].gate=1;Normal270Birth *b=&f270_slots[slot].birth;b->gate=1;
 ++b->shot_count;b->last_shot_frame=fc_frame;b->last_shot_weapon=weapon;b->last_shot_turret=turret;b->last_shot_slot=shot_slot;
 ++b->shot_weapon_count[weapon-145];++f270_shot_resumptions;
 Normal270Draw *d=f270_frame.draw+slot;
 if(d->token&&d->generation==f270_slots[slot].generation&&d->cycle==enemy[slot].enemycycle&&d->draw_gate==2)d->shot_resumed=true;
}
/* Hit receipts originate after native normalization of damage, before the
 * original armor/link branches. They never manufacture or perform damage. */
void render_mirror_normal270_hit_begin(unsigned slot,unsigned damage,unsigned shot)
{
 f270_life.hit.live=false;
 if(!f270_scope()||slot>=100||enemyAvail[slot]==1)return;
 unsigned link=enemy[slot].linknum;bool relevant=false;
 for(unsigned s=25;s<50;s++)if(f270_witness(s)&&(s==slot||(link&&f270_slots[s].birth.link==link)))relevant=true;
 if(!relevant||f270_life.hit_serial==UINT64_MAX)return;
 f270_life.hit.live=true;f270_life.hit.token=++f270_life.hit_serial;f270_life.hit.slot=slot;
 f270_life.hit.link=link;f270_life.hit.damage=damage;f270_life.hit.armor=enemy[slot].armorleft;f270_life.hit.shot=shot;
 ++f270_hit_count;
 if(f270_witness(slot)){Normal270Birth *b=&f270_slots[slot].birth;
  ++b->hit_count;b->last_hit_token=f270_life.hit.token;b->last_hit_frame=fc_frame;
  b->hit_damage=damage;b->hit_armor_before=enemy[slot].armorleft;b->hit_source_slot=shot;
 }
}
void render_mirror_normal270_hit_end(void)
{
 if(f270_life.hit.live){unsigned s=f270_life.hit.slot;
  if(s<100&&f270_slots[s].birth.last_hit_token==f270_life.hit.token)f270_slots[s].birth.hit_armor_after=enemy[s].armorleft;
 }
 f270_life.hit.live=false;
}
static void f270_tick(void)
{
 if(!f270_enabled()&&!f270_life.loaded&&!f270_frame.contributed&&!f270_frame.active&&!f270_frame.pending)return;
 if(f270_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&f270_frame,0,sizeof f270_frame);memset(f270_owned,0,sizeof f270_owned);memset(f270_shadows,0,sizeof f270_shadows);f270_first_reason=0;
 if(f270_life.loaded&&!f270_scope()){f270_reset();f270_life.loaded=false;return;}
 for(unsigned i=25;i<50;i++)if(f270_slots[i].live&&(!f270_witness(i)||!f270_shape(i,1)))render_mirror_normal270_retired(i,F270_INVALIDATED,100);
}
static bool f270_load(unsigned k)
{
 if(k<12||k>=15)return false;
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-%s-%u-8.hda",f270_resources.root,f270_images[k].bank==23?"newshs":"newshd",f270_images[k].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==f270_images[k].role*10000+f270_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==f270_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 f270_resources.member[k]=(Asset){true,true,(int)f270_images[k].role,(int)f270_images[k].base,24,28,0,0,8,rgba};return true;
}
static bool f270_resources_current(void)
{
 if(!f270_resources.checked||!f270_resources.valid||strcmp(f270_resources.root,f270_root()))return false;
 for(unsigned i=12;i<15;i++){const Asset *a=f270_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=(int)f270_images[i].role||a->index!=(int)f270_images[i].base||
  a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,172032)!=f270_images[i].rgba)return false;
 }return true;
}
static bool f270_ready(void)
{
 if(!f270_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!f270_resources.checked){f270_resources.checked=true;f270_resources.valid=true;strcpy(f270_resources.root,f270_life.root);
 for(unsigned i=12;i<15;i++)if(!f270_load(i))f270_resources.valid=false;}
 if(!f270_resources_current()){f270_resources.valid=false;return false;}return true;
}
static void f270_shutdown(void)
{
 f270_reset();f270_life.loaded=false;
 for(unsigned i=12;i<15;i++)free(f270_resources.member[i].rgba);
 memset(&f270_resources,0,sizeof f270_resources);
}
static bool f270_dependencies(bool partial)
{
 if(!f270_frame.contributed)return true;
 if(f270_frame.fault||!f270_scope()||!f270_colors()||!f270_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<100;i++)if(f270_frame.draw[i].token){const Normal270Draw *d=f270_frame.draw+i;unsigned s=i;
  if(!f270_witness(s)||!f270_shape(s,2)||d->generation!=f270_slots[s].generation||
  d->token!=f270_slots[s].birth.token||d->epoch!=f270_life.epoch||d->record!=f270_slots[s].record||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||
  d->cycle<1||d->cycle>6||f270_image(d->base)<0||d->cycle!=enemy[s].enemycycle||d->base!=enemy[s].egr[d->cycle-1]||
  !(enemy[s].aniactive==d->draw_gate||(d->draw_gate==2&&enemy[s].aniactive==1&&d->shot_resumed))||enemy[s].linknum!=d->link)return false;
  if(!d->complete){if(!partial||!f270_frame.pending||f270_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=f270_totals[f270_image(d->base)])return false;
 }
 return partial||(!f270_frame.active&&!f270_frame.pending);
}
/* Cheap native-write gate: no art/source hash or731-row scan. */
static bool f270_write_current(void)
{
 return !f270_frame.contributed||(!f270_frame.fault&&f270_scope()&&f270_resources.checked&&f270_resources.valid&&
 !strcmp(f270_resources.root,f270_root())&&(!f270_frame.active||f270_witness(f270_frame.slot)));
}
/* Pure predicate shared by diagnostic snapshots. */
static bool f270_finish(void){return f270_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool f270_guard(void)
{
 if(f270_finish())return true;
 f270_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool f270_before_tile(unsigned slot,int part)
{
 if(f270_frame.contributed&&!f270_dependencies(true)){f270_fail(5);return false;}
 if(f270_frame.pending&&(f270_frame.active||slot!=f270_frame.slot||
 f270_frame.draw[slot].next>=4||part!=(int)f270_parts[f270_frame.draw[slot].next])){f270_fail(6);return false;}
 return true;
}
static bool f270_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool f270_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!f270_enabled()||slot<25||slot>=50||f270_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!f270_witness(slot)){++f270_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)f270_parts[k];k++);
 if(k==4){if(f270_frame.draw[slot].token)f270_fail(7);return false;}
 int64_t ox=(int64_t)x-f270_px[k],oy=(int64_t)y-f270_py[k];
 Normal270Draw *d=f270_frame.draw+slot;
 if(!f270_geometry(ox,oy)){++f270_clipped;if(d->token)f270_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter!=enemy[slot].filter||(filter&&filter!=0x70)||
 f270_slots[slot].phase_tick!=fc_frame||
 !f270_scope()||sheet!=enemy[slot].sprite2s||!f270_shape(slot,1)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||f270_image(base)<0||!f270_colors()||!f270_ready()){
  if(d->token)f270_fail(9);
  return false;
 }
 if(k==0){if(d->token||f270_frame.pending){f270_fail(10);return false;}}
 else if(!f270_frame.pending||f270_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||f270_frame.pending)f270_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||f270_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++f270_contract_faults;f270_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++f270_contract_faults;f270_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(Normal270Draw){.frame=fc_frame,.epoch=f270_life.epoch,.token=f270_slots[slot].birth.token,
   .generation=f270_slots[slot].generation,.slot=slot,.record=f270_slots[slot].record,
   .event=f270_slots[slot].birth.event,.link=f270_slots[slot].birth.link,
   .cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,.draw_filter=(unsigned)filter,.base=base,.cur_loc=curLoc,.bank_role=enemy[slot].enemytype==270?8:23,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  f270_frame.pending=true;f270_frame.slot=slot;f270_frame.image=(unsigned)f270_image(base);f270_frame.used|=1u<<f270_frame.image;
 }
 d->part_order[k]=(unsigned)part;
 f270_frame.part=k;f270_frame.pixels=0;f270_frame.active=true;f270_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool f270_retire(unsigned off,int style)
{
 bool owned=off<64000&&f270_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++f270_blend_retirements;else ++f270_normal_retirements;
 f270_owned[off]=f270_shadows[off]=0;}
 return owned;
}
static bool f270_pixel(unsigned x,unsigned y,int style)
{
 if(!f270_frame.active){if(f270_frame.pending){f270_fail(14);return true;}return false;}
 Normal270Draw *d=f270_frame.draw+f270_frame.slot;
 unsigned k=f270_frame.part;
 if(k>=4||f270_frame.pixels>=f270_counts[f270_frame.image][k]){++f270_contract_faults;f270_fail(15);return true;}
 const Normal270Write *w=f270_native[f270_frame.image][k]+f270_frame.pixels;
 unsigned lx=f270_px[k]+w->x,ly=f270_py[k]+w->y;
 Uint8 index=d->draw_filter?(Uint8)(d->draw_filter|(w->index&15)):w->index;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=index||expected[y*320+x]!=index){
 ++f270_contract_faults;f270_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&f270_resources.member[f270_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  Uint8 filtered[4];if(d->draw_filter){enemy_filter_rgba(art,(Uint8)d->draw_filter,filtered);art=filtered;}
  /* Exact existing native-written cells are opaque. Art alpha never creates
   * coverage: native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  OHS_SURVIVAL_WRITE(canvas,dst,NORMAL270_HD_STORE_TAG);
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 f270_owned[off]=(uint8_t)(f270_frame.slot+1);f270_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){f270_fail(17);return true;}
 f270_frame.writes[f270_frame.slot][d->callback_count++]=(Normal270Write){(uint8_t)lx,(uint8_t)ly,index};
 ++f270_frame.pixels;d->part_count[k]=f270_frame.pixels;return true;
}
static void f270_shadow(unsigned off)
{
 if(off<64000&&f270_owned[off]){if(f270_shadows[off]<255)++f270_shadows[off];++f270_shadow_writes;}
}
static void f270_end(void)
{
 if(!f270_frame.active)return;
 unsigned k=f270_frame.part;Normal270Draw *d=f270_frame.draw+f270_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||f270_frame.pixels!=f270_counts[f270_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++f270_contract_faults;f270_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;f270_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==f270_totals[f270_frame.image];f270_frame.pending=false;
  if(!d->complete){f270_fail(19);return;}
  if(!f270_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   f270_fail(22);family_fault(FC_SOURCE);return;
  }
 }
}
static void f270_accept(void){f270_frame.accepted=fc.ready&&!fc.frame_failed&&f270_finish();}
Normal270FamilyStatus render_mirror_normal270_family_status(void)
{
 Normal270FamilyStatus s={0};s.requested=f270_enabled();s.loaded=f270_life.loaded;s.contributed=f270_frame.contributed;
 s.failed=fc.frame_failed||f270_frame.fault;s.accepted=f270_frame.accepted;s.frame=fc_frame;
 s.active=f270_frame.active;s.pending=f270_frame.pending;s.active_slot=f270_frame.slot;
 s.active_part=f270_frame.part<4?f270_parts[f270_frame.part]:UINT_MAX;s.material_mask=f270_frame.used;s.witnessed_records=f270_witnessed_records;
 memcpy(s.witnessed_count,f270_witnessed_count,sizeof s.witnessed_count);
 s.phase_observations=f270_phase_observations;s.shot_resumptions=f270_shot_resumptions;s.hit_count=f270_hit_count;s.linked_retirements=f270_linked_retirements;s.consumed_events=f270_life.consumed;
 s.blend_retirements=f270_blend_retirements;s.normal_retirements=f270_normal_retirements;s.shadow_writes=f270_shadow_writes;
 s.clipped=f270_clipped;s.unwitnessed=f270_unwitnessed;s.lifetime_losses=f270_lifetime_losses;s.bank_losses=f270_bank_losses;
 s.contract_faults=f270_contract_faults;s.first_reason=f270_first_reason;
 for(unsigned i=0;i<100;i++)s.births[i]=f270_slots[i].birth;
 memcpy(s.draw,f270_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<100;i++)if(s.draw[i].token)s.draw[i].final_gate=enemy[i].aniactive;
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=f270_owned[i]!=0;s.shadowed_cells+=f270_owned[i]&&f270_shadows[i];}return s;
}
bool render_mirror_normal270_pre_draw(Normal270Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!f270_frame.active||f270_frame.part||f270_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=f270_frame.draw[f270_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_normal270_pre_part(Normal270Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!f270_frame.active||f270_frame.pixels||
 f270_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=f270_frame.draw[f270_frame.slot];unsigned k=f270_frame.part;*part=f270_parts[k];
 unsigned x=(unsigned)d->x+f270_px[k],y=(unsigned)d->y+f270_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_normal270_callbacks(unsigned slot,Normal270Write *out,size_t capacity)
{
 if(slot>=100||!out||capacity<f270_frame.draw[slot].callback_count)return 0;
 unsigned n=f270_frame.draw[slot].callback_count;memcpy(out,f270_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_normal270_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!f270_frame.accepted||fc.frame_active||fc.frame_failed||
 !f270_frame.contributed||!f270_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,f270_owned,64000);memcpy(shadows,f270_shadows,64000);return true;
}
