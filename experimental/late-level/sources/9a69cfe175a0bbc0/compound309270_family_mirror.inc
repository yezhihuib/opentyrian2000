/* Default-OFF E1 physical2 compound309..312 (events242/243) and firing270
 * (244/245). Ten independent native allocations; no quartet liveness gate.
 * Sidecars only. Native event, movement, collision, weapon, RNG and disposal
 * remain authoritative. Four native stores per body, exact fullrect672 support. */
#include "compound309270_native.inc"
static struct {uint64_t generation,epoch,token,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate;uint64_t phase_tick;Compound309270Birth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} c309_slots[100];
static struct {uint64_t epoch,serial,hit_serial;bool exhausted,loaded;char root[1024];unsigned consumed;
 const struct JE_EventRecType *events;
 struct {bool live;uint64_t token,epoch,generation;unsigned record,event,component;int slot;} call;
 struct {bool live;uint64_t token;unsigned slot,link,damage,armor,shot;} hit;
} c309_life;
static struct {bool checked,valid;char root[1024];Asset member[15];} c309_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,image,part,pixels,used;
 Compound309270Draw draw[100];Compound309270Write writes[100][672];} c309_frame;
static unsigned c309_witnessed_records;
static uint64_t c309_witnessed_count[5],c309_phase_observations,c309_hit_count,c309_linked_retirements,c309_shot_resumptions;
static bool c309_resources_current(void);
static uint8_t c309_owned[64000],c309_shadows[64000];
static uint64_t c309_blend_retirements,c309_normal_retirements,c309_shadow_writes;
static uint64_t c309_clipped,c309_unwitnessed,c309_lifetime_losses,c309_bank_losses,c309_contract_faults;
static unsigned c309_first_reason;
static const char *c309_root(void){const char *p=getenv("COMPOUND309270_ASSET_DIR");return p?p:"";}
static bool c309_enabled(void)
{
 const char *e=getenv("COMPOUND309270_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool c309_level_scope(void)
{
 return c309_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static int c309_record_index(unsigned r){return r==270?4:r>=309&&r<=312?(int)(r-309):-1;}
static bool c309_event_matches(unsigned event)
{
 if(!c309_life.events||maxEvent!=731||event<242||event>245)return false;
 const struct JE_EventRecType *r=c309_life.events+event-1;
 static const unsigned xs[4]={66,162,90,162};unsigned k=event-242;
 return r->eventtime==(k<2?1840:1896)&&r->eventtype==(k<2?12:6)&&r->eventdat==(k<2?309:270)&&
 r->eventdat2==(int)xs[k]&&!r->eventdat3&&r->eventdat4==(k<2?24+k:0)&&!r->eventdat5&&!r->eventdat6;
}
static bool c309_scope(void)
{
 return c309_life.loaded&&!c309_life.exhausted&&c309_level_scope()&&terrain_file=='z'&&
 !strcmp(c309_life.root,c309_root())&&curLoc<1960&&eventLoc<=259;
}
static void c309_fail(unsigned reason)
{
 if(!c309_first_reason)c309_first_reason=reason;
 c309_frame.fault=true;c309_frame.accepted=false;c309_frame.active=c309_frame.pending=false;
 if(c309_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_compound309270_retired(unsigned slot,unsigned reason,unsigned source)
{
 if(reason!=C309_INVALIDATED&&reason!=C309_BANK&&reason!=C309_REUSE)render_mirror_linked338_normal_retired(slot); /* Linked338 normal: independent native observer. */
 if(reason!=C309_INVALIDATED&&reason!=C309_BANK&&reason!=C309_REUSE)render_mirror_turret273_retired(slot); /* Turret273: independent native observer. */
 if(reason!=C309_INVALIDATED&&reason!=C309_BANK&&reason!=C309_REUSE)render_mirror_tall_structure_retired(slot); /* Tall sidecar: independent native retirement only. */
 if(slot>=100)return;
 if(c309_slots[slot].live||c309_slots[slot].pending){
  ++c309_lifetime_losses;
  if(c309_frame.draw[slot].token)c309_fail(1);
 }
 Compound309270Birth *b=&c309_slots[slot].birth;
 if(b->live){
  b->retired_frame=fc_frame;b->retired_y=enemy[slot].ey;b->retirement_reason=reason;b->retirement_source_slot=source;
  if((reason==C309_DIRECT_LETHAL||reason==C309_LINKED_LETHAL)&&c309_life.hit.live&&
   source==c309_life.hit.slot&&c309_life.hit.armor<=c309_life.hit.damage&&
   (source==slot||(b->link&&b->link==c309_life.hit.link))){
   b->retirement_hit_token=c309_life.hit.token;
   if(source!=slot)++c309_linked_retirements;
  }
 }
 b->live=false;
 c309_slots[slot].live=c309_slots[slot].pending=c309_slots[slot].initialized=false;
}
static void c309_reset(void)
{
 if(c309_frame.contributed||c309_frame.active||c309_frame.pending)c309_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_compound309270_retired(i,C309_INVALIDATED,100);
 c309_life.call.live=c309_life.hit.live=false;
 if(c309_life.epoch==UINT64_MAX)c309_life.exhausted=true;else ++c309_life.epoch;
 /* Original event consumption survives renderer resets, not real level loads. */
}
void render_mirror_compound309270_level_begin(char map,char shape,const struct JE_EventRecType *events)
{
 lpf_level_begin(map,shape,events); /* Launcher271: read-only native draw observation. */
 render_mirror_linked338_normal_level_begin(map,shape,events); /* Linked338 normal: independent native observer. */
 render_mirror_turret273_level_begin(map,shape,events); /* Turret273: independent native observer. */
 render_mirror_tall_structure_level_begin(map,shape,events); /* Tall sidecar: independent admission. */
 c309_reset();c309_life.loaded=false;c309_life.consumed=0;c309_life.events=events;
 c309_witnessed_records=0;memset(c309_witnessed_count,0,sizeof c309_witnessed_count);
 for(unsigned i=0;i<100;i++)memset(&c309_slots[i].birth,0,sizeof c309_slots[i].birth);
 if(!c309_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||
 !c309_event_matches(242)||!c309_event_matches(243)||!c309_event_matches(244)||!c309_event_matches(245)||
 !c309_root()[0]||strlen(c309_root())>=sizeof c309_life.root)return;
 strcpy(c309_life.root,c309_root());c309_life.loaded=true;
}
static int c309_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static uint64_t c309_weapon_stamp(unsigned weapon)
{
 const JE_WeaponType *w=&weapons[weapon];Uint8 b[80];size_t n=0;
#define C309_BYTE(v) do{b[n++]=(Uint8)(v);}while(0)
#define C309_WORD(v) do{unsigned word_=(unsigned)(v);C309_BYTE(word_);C309_BYTE(word_>>8);}while(0)
 C309_WORD(w->drain);C309_BYTE(w->shotrepeat);C309_BYTE(w->multi);C309_WORD(w->weapani);
 C309_BYTE(w->max);C309_BYTE(w->tx);C309_BYTE(w->ty);C309_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)C309_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)C309_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)C309_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)C309_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)C309_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)C309_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)C309_WORD(w->sg[i]);
 C309_BYTE(w->acceleration);C309_BYTE(w->accelerationx);C309_BYTE(w->circlesize);
 C309_BYTE(w->sound);C309_BYTE(w->trail);C309_BYTE(w->shipblastfilter);
#undef C309_WORD
#undef C309_BYTE
 return n==sizeof(b)?asteroid1_stamp(b,sizeof(b)):0;
}
static bool c309_source(Sprite2_array *bank,unsigned record)
{
 int ri=c309_record_index(record);if(ri<0||!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data)return false;
 const unsigned role=record==270?8:23,bytes=record==270?42012:46566;
 const uint64_t stamp=record==270?UINT64_C(0x913975450e0fc00d):C309_NEWSHS_STAMP;
 bool bound=false;for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==role&&bank==enemySpriteSheets+i)bound=true;
 if(!bound||bank->size!=bytes||asteroid1_stamp(bank->data,bank->size)!=stamp||
 asteroid1_record_stamp(record)!=c309_records[ri].stamp)return false;
 return record!=270||(c309_weapon_stamp(145)==UINT64_C(0x387b219ee9cab017)&&c309_weapon_stamp(146)==UINT64_C(0x4623a676db5268a8));
}
static bool c309_colors(void)
{
 for(unsigned i=0;i<COUNTOF(c309_palette);i++)if((rgb_palette[c309_palette[i].index]&0xffffffu)!=c309_palette[i].rgb)return false;
 return true;
}
/* Constructor cycle0 for compound, cycle1/idle2 for turret. Pose derives only
 * from actual native phase and successful native bullet allocation observers. */
static bool c309_shape(unsigned slot,unsigned stage)
{
 if(slot<25||slot>=50)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;unsigned r=e->enemytype;int ri=c309_record_index(r);bool turret=r==270;
 if(ri<0||e->enemydatofs!=enemyDat+r||!c309_source(e->sprite2s,r)||
 e->size!=1||e->ani!=(turret?6:20)||e->animin!=1||e->animax!=(turret?6:0)||e->aniwhenfire!=(turret?2:0)||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->enemydie||
 e->exc||e->eyc||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||e->enemyground||e->explonum!=(turret?2:12)||
 e->tur[0]!=(turret?145:0)||e->tur[1]!=(turret?146:0)||e->tur[2]||
 e->freq[0]!=(turret?40:0)||e->freq[1]!=(turret?41:0)||e->freq[2]||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=c309_sequences[ri][i])return false;
 if(stage==0)return !e->linknum&&!e->filter&&e->enemycycle==(turret?1:0)&&e->aniactive==(turret?2:1)&&!e->mapoffset&&e->ey==1&&e->ex==1;
 if(e->linknum!=c309_slots[slot].birth.link)return false;
 if(!turret)return e->aniactive==1&&e->enemycycle<=20;
 return (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==6))||
 (e->aniactive==1&&e->enemycycle>=1&&e->enemycycle<=6);
}
static int c309_image(unsigned base)
{for(unsigned i=0;i<15;i++)if(c309_images[i].base==base)return (int)i;return -1;}
uint64_t render_mirror_compound309270_event_begin(unsigned event,unsigned ofs,unsigned pool,int unique)
{
 (void)ln_event_begin(event,ofs,pool,unique); /* Linked338 normal: independent native observer. */
 (void)render_mirror_turret273_event_begin(event,ofs,pool,unique); /* Turret273: independent native observer. */
 (void)ts_event_begin(event,ofs,pool,unique); /* Tall sidecar: independent admission. */
 if(c309_life.call.live){c309_life.call.live=false;c309_fail(3);return 0;}
 if(!c309_scope()||event!=eventLoc||pool!=25||unique||!c309_event_matches(event)||
 curLoc!=c309_life.events[event-1].eventtime||(event<244?ofs>3:ofs!=0))return 0;
 unsigned bit=1u<<(event<244?(event-242)*4+ofs:8+event-244);
 if(c309_life.consumed&bit)return 0;
 c309_life.consumed|=bit; /* First-free allocation failure consumes this origin. */
 if(c309_life.serial==UINT64_MAX){c309_life.exhausted=true;return 0;}
 c309_life.call.live=true;c309_life.call.token=++c309_life.serial;c309_life.call.epoch=c309_life.epoch;
 c309_life.call.record=c309_life.events[event-1].eventdat+ofs;c309_life.call.event=event;c309_life.call.component=ofs;
 c309_life.call.slot=-1;c309_life.call.generation=0;
 return c309_life.call.token;
}
void render_mirror_compound309270_enemy_allocated(void *p,unsigned record,int unique)
{
 render_mirror_linked338_normal_enemy_allocated(p,record,unique); /* Linked338 normal: independent native observer. */
 render_mirror_turret273_enemy_allocated(p,record,unique); /* Turret273: independent native observer. */
 render_mirror_tall_structure_enemy_allocated(p,record,unique); /* Tall sidecar: independent admission. */
 int s=c309_slot(p);if(s<0)return;
 render_mirror_compound309270_retired((unsigned)s,C309_REUSE,100);
 if(c309_slots[s].generation==UINT64_MAX){c309_slots[s].exhausted=true;return;}
 if(c309_slots[s].exhausted)return;
 ++c309_slots[s].generation;
 if(c309_life.call.live&&c309_scope()&&s>=25&&s<50&&enemyAvail[s]==1&&!unique&&
 record==c309_life.call.record&&c309_life.call.slot==-1){
  c309_slots[s].pending=true;c309_slots[s].record=record;c309_life.call.slot=s;
  c309_life.call.generation=c309_slots[s].generation;
 }
}
void render_mirror_compound309270_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 render_mirror_linked338_normal_enemy_initialized(p,record,avail); /* Linked338 normal: independent native observer. */
 render_mirror_turret273_enemy_initialized(p,record,avail); /* Turret273: independent native observer. */
 render_mirror_tall_structure_enemy_initialized(p,record,avail); /* Tall sidecar: independent admission. */
 int s=c309_slot(p);if(s<0)return;
 c309_slots[s].initialized=c309_slots[s].pending&&c309_life.call.live&&c309_scope()&&s>=25&&s<50&&
 c309_life.call.slot==s&&c309_life.call.generation==c309_slots[s].generation&&
 record==c309_life.call.record&&avail==0&&enemyAvail[s]==1&&c309_shape((unsigned)s,0);
}
void render_mirror_compound309270_event_commit(uint64_t token,unsigned one_based)
{
 render_mirror_linked338_normal_event_commit(ln_life.call.live?ln_life.call.token:0,one_based); /* Linked338 normal: independent native observer. */
 render_mirror_turret273_event_commit(tp_life.call.live?tp_life.call.token:0,one_based); /* Turret273: independent native observer. */
 render_mirror_tall_structure_event_commit(ts_life.call.live?ts_life.call.token:0,one_based); /* Tall sidecar: independent admission. */
 if(!token)return;
 int s=c309_life.call.slot;unsigned ev=c309_life.call.event;
 bool ok=c309_life.call.live&&token==c309_life.call.token&&c309_life.call.epoch==c309_life.epoch&&c309_scope()&&
 s>=25&&s<50&&one_based==(unsigned)s+1&&eventLoc==ev&&c309_event_matches(ev)&&curLoc==c309_life.events[ev-1].eventtime;
 if(ok){const struct JE_EventRecType *r=c309_life.events+ev-1;
  ok=c309_slots[s].pending&&c309_slots[s].initialized&&c309_life.call.generation==c309_slots[s].generation&&
  enemyAvail[s]==0&&enemy[s].enemytype==c309_life.call.record&&
  enemy[s].ex==r->eventdat2-(mapX-1)*24-12+(c309_life.call.component%2?24:0)&&
  enemy[s].ey==-28-(c309_life.call.component>=2?28:0)&&
  enemy[s].linknum==r->eventdat4&&!enemy[s].eyc&&!enemy[s].fixedmovey;
 }
 if(s>=0&&s<100){
  c309_slots[s].live=ok;c309_slots[s].pending=c309_slots[s].initialized=false;
  if(ok){
   unsigned ri=(unsigned)c309_record_index(c309_slots[s].record);bool turret=ri==4;
   c309_slots[s].cycle=turret?1:0;c309_slots[s].gate=turret?2:1;c309_slots[s].phase_tick=0;
   c309_slots[s].witness=c309_slots[s].generation;c309_slots[s].epoch=c309_life.epoch;c309_slots[s].token=token;
   c309_slots[s].bank=enemy[s].sprite2s;c309_slots[s].data=enemy[s].sprite2s->data;c309_slots[s].bytes=enemy[s].sprite2s->size;
   c309_slots[s].birth=(Compound309270Birth){.epoch=c309_life.epoch,.token=token,.generation=c309_slots[s].generation,
    .slot=(unsigned)s,.record=c309_slots[s].record,.event=ev,.link=enemy[s].linknum,.bank_role=turret?8:23,.bank_bytes=turret?42012:46566,
    .bank_stamp=turret?UINT64_C(0x913975450e0fc00d):C309_NEWSHS_STAMP,.record_stamp=c309_records[ri].stamp,
    .bank_object=(uintptr_t)c309_slots[s].bank,.bank_data=(uintptr_t)c309_slots[s].data,
    .birth_frame=fc_frame,.cycle=turret?1:0,.gate=turret?2:1,.birth_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,
    .birth_eyc=enemy[s].eyc,.live=true,.initialized=true,.retirement_source_slot=100};
   if(!c309_shape((unsigned)s,1))render_mirror_compound309270_retired((unsigned)s,C309_INVALIDATED,100);
   else {c309_witnessed_records|=1u<<ri;++c309_witnessed_count[ri];}
  }
 }
 c309_life.call.live=false;
}
void render_mirror_compound309270_bank_changed(Sprite2_array *bank)
{
 render_mirror_linked338_normal_bank_changed(bank); /* Linked338 normal: independent native observer. */
 render_mirror_turret273_bank_changed(bank); /* Turret273: independent native observer. */
 render_mirror_tall_structure_bank_changed(bank); /* Tall sidecar: independent admission. */
 for(unsigned i=0;i<100;i++)if(c309_slots[i].live&&c309_slots[i].bank==bank){++c309_bank_losses;render_mirror_compound309270_retired(i,C309_BANK,100);}
 if(c309_life.call.live){c309_life.call.live=false;c309_fail(4);}
}
static bool c309_witness(unsigned s)
{
 return s>=25&&s<50&&c309_slots[s].live&&!c309_slots[s].exhausted&&c309_slots[s].epoch==c309_life.epoch&&
 c309_slots[s].generation==c309_slots[s].witness&&enemyAvail[s]==0&&
 enemy[s].sprite2s&&c309_slots[s].bank==enemy[s].sprite2s&&c309_slots[s].data==enemy[s].sprite2s->data&&
 c309_slots[s].bytes==enemy[s].sprite2s->size&&enemy[s].linknum==c309_slots[s].birth.link;
}
void render_mirror_compound309270_enemy_animated(unsigned slot)
{
 lpf_enemy_animated(slot); /* Launcher271: read-only native draw observation. */
 ln_enemy_animated(slot); /* Linked338 normal: independent native observer. */
 tp_enemy_animated(slot); /* Turret273: independent native observer. */
 ts_enemy_animated(slot); /* Tall sidecar: independent admission. */
 if(slot>=100||!c309_slots[slot].live)return;
 if(!c309_scope()||!c309_witness(slot)||!c309_shape(slot,1)||c309_slots[slot].phase_tick==fc_frame){
  render_mirror_compound309270_retired(slot,C309_INVALIDATED,100);return;
 }
 unsigned cycle=c309_slots[slot].cycle,gate=c309_slots[slot].gate;bool turret=c309_slots[slot].record==270;
 if(gate==1){++cycle;if(turret&&cycle==6)gate=2;else if(cycle>(turret?6u:20u))cycle=1;}
 if(enemy[slot].enemycycle!=cycle||enemy[slot].aniactive!=gate){render_mirror_compound309270_retired(slot,C309_INVALIDATED,100);return;}
 c309_slots[slot].cycle=cycle;c309_slots[slot].gate=gate;c309_slots[slot].phase_tick=fc_frame;
 Compound309270Birth *b=&c309_slots[slot].birth;b->cycle=cycle;b->gate=gate;b->phase_tick=fc_frame;
 ++b->phase_observations;++c309_phase_observations;
}
void render_mirror_compound309270_shot_fired(unsigned slot,unsigned weapon,unsigned turret,unsigned shot_slot)
{
 if(slot>=100||!c309_slots[slot].live||c309_slots[slot].record!=270)return;
 if(!c309_scope()||!c309_witness(slot)||!c309_shape(slot,2)||
 !((weapon==145&&turret==1)||(weapon==146&&turret==2))||shot_slot>=ENEMY_SHOT_MAX||enemyShotAvail[shot_slot]!=0||
 c309_slots[slot].phase_tick!=fc_frame||c309_slots[slot].gate!=2||
 (c309_slots[slot].cycle!=1&&c309_slots[slot].cycle!=6)||enemy[slot].enemycycle!=c309_slots[slot].cycle||enemy[slot].aniactive!=1){
 render_mirror_compound309270_retired(slot,C309_INVALIDATED,100);return;}
 c309_slots[slot].gate=1;Compound309270Birth *b=&c309_slots[slot].birth;b->gate=1;
 ++b->shot_count;b->last_shot_frame=fc_frame;b->last_shot_weapon=weapon;b->last_shot_turret=turret;b->last_shot_slot=shot_slot;
 ++b->shot_weapon_count[weapon-145];++c309_shot_resumptions;
 Compound309270Draw *d=c309_frame.draw+slot;
 if(d->token&&d->generation==c309_slots[slot].generation&&d->cycle==enemy[slot].enemycycle&&d->draw_gate==2)d->shot_resumed=true;
}
/* Hit receipts originate after native normalization of damage, before the
 * original armor/link branches. They never manufacture or perform damage. */
void render_mirror_compound309270_hit_begin(unsigned slot,unsigned damage,unsigned shot)
{
 c309_life.hit.live=false;
 if(!c309_scope()||slot>=100||enemyAvail[slot]==1)return;
 unsigned link=enemy[slot].linknum;bool relevant=false;
 for(unsigned s=25;s<50;s++)if(c309_witness(s)&&(s==slot||(link&&c309_slots[s].birth.link==link)))relevant=true;
 if(!relevant||c309_life.hit_serial==UINT64_MAX)return;
 c309_life.hit.live=true;c309_life.hit.token=++c309_life.hit_serial;c309_life.hit.slot=slot;
 c309_life.hit.link=link;c309_life.hit.damage=damage;c309_life.hit.armor=enemy[slot].armorleft;c309_life.hit.shot=shot;
 ++c309_hit_count;
 if(c309_witness(slot)){Compound309270Birth *b=&c309_slots[slot].birth;
  ++b->hit_count;b->last_hit_token=c309_life.hit.token;b->last_hit_frame=fc_frame;
  b->hit_damage=damage;b->hit_armor_before=enemy[slot].armorleft;b->hit_source_slot=shot;
 }
}
void render_mirror_compound309270_hit_end(void)
{
 if(c309_life.hit.live){unsigned s=c309_life.hit.slot;
  if(s<100&&c309_slots[s].birth.last_hit_token==c309_life.hit.token)c309_slots[s].birth.hit_armor_after=enemy[s].armorleft;
 }
 c309_life.hit.live=false;
}
static void c309_tick(void)
{
 if(!c309_enabled()&&!c309_life.loaded&&!c309_frame.contributed&&!c309_frame.active&&!c309_frame.pending)return;
 if(c309_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&c309_frame,0,sizeof c309_frame);memset(c309_owned,0,sizeof c309_owned);memset(c309_shadows,0,sizeof c309_shadows);c309_first_reason=0;
 if(c309_life.loaded&&!c309_scope()){c309_reset();c309_life.loaded=false;return;}
 for(unsigned i=25;i<50;i++)if(c309_slots[i].live&&(!c309_witness(i)||!c309_shape(i,1)))render_mirror_compound309270_retired(i,C309_INVALIDATED,100);
}
static bool c309_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-%s-%u-8.hda",c309_resources.root,c309_images[k].bank==23?"newshs":"newshd",c309_images[k].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==c309_images[k].role*10000+c309_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==c309_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 c309_resources.member[k]=(Asset){true,true,(int)c309_images[k].role,(int)c309_images[k].base,24,28,0,0,8,rgba};return true;
}
static bool c309_resources_current(void)
{
 if(!c309_resources.checked||!c309_resources.valid||strcmp(c309_resources.root,c309_root()))return false;
 for(unsigned i=0;i<15;i++){const Asset *a=c309_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=(int)c309_images[i].role||a->index!=(int)c309_images[i].base||
  a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,172032)!=c309_images[i].rgba)return false;
 }return true;
}
static bool c309_ready(void)
{
 if(!c309_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!c309_resources.checked){c309_resources.checked=true;c309_resources.valid=true;strcpy(c309_resources.root,c309_life.root);
 for(unsigned i=0;i<15;i++)if(!c309_load(i))c309_resources.valid=false;}
 if(!c309_resources_current()){c309_resources.valid=false;return false;}return true;
}
static void c309_shutdown(void)
{
 c309_reset();c309_life.loaded=false;
 for(unsigned i=0;i<15;i++)free(c309_resources.member[i].rgba);
 memset(&c309_resources,0,sizeof c309_resources);
}
static bool c309_dependencies(bool partial)
{
 if(!c309_frame.contributed)return true;
 if(c309_frame.fault||!c309_scope()||!c309_colors()||!c309_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<100;i++)if(c309_frame.draw[i].token){const Compound309270Draw *d=c309_frame.draw+i;unsigned s=i;
  if(!c309_witness(s)||!c309_shape(s,2)||d->generation!=c309_slots[s].generation||
  d->token!=c309_slots[s].birth.token||d->epoch!=c309_life.epoch||d->record!=c309_slots[s].record||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||
  d->cycle!=enemy[s].enemycycle||d->base!=enemy[s].egr[d->cycle-1]||
  !(enemy[s].aniactive==d->draw_gate||(d->draw_gate==2&&enemy[s].aniactive==1&&d->shot_resumed))||enemy[s].linknum!=d->link)return false;
  if(!d->complete){if(!partial||!c309_frame.pending||c309_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=c309_totals[c309_image(d->base)])return false;
 }
 return partial||(!c309_frame.active&&!c309_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool c309_finish(void){return c309_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool c309_guard(void)
{
 if(c309_finish())return true;
 c309_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool c309_before_tile(unsigned slot,int part)
{
 if(c309_frame.contributed&&!c309_dependencies(true)){c309_fail(5);return false;}
 if(c309_frame.pending&&(c309_frame.active||slot!=c309_frame.slot||
 c309_frame.draw[slot].next>=4||part!=(int)c309_parts[c309_frame.draw[slot].next])){c309_fail(6);return false;}
 return true;
}
static bool c309_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool c309_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!c309_enabled()||slot<25||slot>=50||c309_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!c309_witness(slot)){++c309_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)c309_parts[k];k++);
 if(k==4){if(c309_frame.draw[slot].token)c309_fail(7);return false;}
 int64_t ox=(int64_t)x-c309_px[k],oy=(int64_t)y-c309_py[k];
 Compound309270Draw *d=c309_frame.draw+slot;
 if(!c309_geometry(ox,oy)){++c309_clipped;if(d->token)c309_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter!=enemy[slot].filter||(filter&&filter!=0x70)||
 c309_slots[slot].phase_tick!=fc_frame||
 !c309_scope()||sheet!=enemy[slot].sprite2s||!c309_shape(slot,1)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||c309_image(base)<0||!c309_colors()||!c309_ready()){
  if(d->token)c309_fail(9);
  return false;
 }
 if(k==0){if(d->token||c309_frame.pending){c309_fail(10);return false;}}
 else if(!c309_frame.pending||c309_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||c309_frame.pending)c309_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||c309_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++c309_contract_faults;c309_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++c309_contract_faults;c309_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(Compound309270Draw){.frame=fc_frame,.epoch=c309_life.epoch,.token=c309_slots[slot].birth.token,
   .generation=c309_slots[slot].generation,.slot=slot,.record=c309_slots[slot].record,
   .event=c309_slots[slot].birth.event,.link=c309_slots[slot].birth.link,
   .cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,.draw_filter=(unsigned)filter,.base=base,.cur_loc=curLoc,.bank_role=enemy[slot].enemytype==270?8:23,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  c309_frame.pending=true;c309_frame.slot=slot;c309_frame.image=(unsigned)c309_image(base);c309_frame.used|=1u<<c309_frame.image;
 }
 d->part_order[k]=(unsigned)part;
 c309_frame.part=k;c309_frame.pixels=0;c309_frame.active=true;c309_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool c309_retire(unsigned off,int style)
{
 bool owned=off<64000&&c309_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++c309_blend_retirements;else ++c309_normal_retirements;
 c309_owned[off]=c309_shadows[off]=0;}
 return owned;
}
static bool c309_pixel(unsigned x,unsigned y,int style)
{
 if(!c309_frame.active){if(c309_frame.pending){c309_fail(14);return true;}return false;}
 Compound309270Draw *d=c309_frame.draw+c309_frame.slot;
 unsigned k=c309_frame.part;
 if(k>=4||c309_frame.pixels>=c309_counts[c309_frame.image][k]){++c309_contract_faults;c309_fail(15);return true;}
 const Compound309270Write *w=c309_native[c309_frame.image][k]+c309_frame.pixels;
 unsigned lx=c309_px[k]+w->x,ly=c309_py[k]+w->y;
 Uint8 index=d->draw_filter?(Uint8)(d->draw_filter|(w->index&15)):w->index;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=index||expected[y*320+x]!=index){
 ++c309_contract_faults;c309_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&c309_resources.member[c309_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  Uint8 filtered[4];if(d->draw_filter){enemy_filter_rgba(art,(Uint8)d->draw_filter,filtered);art=filtered;}
  /* Exact existing native-written cells are opaque. Art alpha never creates
   * coverage: native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  OHS_SURVIVAL_WRITE(canvas,dst,COMPOUND309270_HD_STORE_TAG);
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 c309_owned[off]=(uint8_t)(c309_frame.slot+1);c309_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){c309_fail(17);return true;}
 c309_frame.writes[c309_frame.slot][d->callback_count++]=(Compound309270Write){(uint8_t)lx,(uint8_t)ly,index};
 ++c309_frame.pixels;d->part_count[k]=c309_frame.pixels;return true;
}
static void c309_shadow(unsigned off)
{
 if(off<64000&&c309_owned[off]){if(c309_shadows[off]<255)++c309_shadows[off];++c309_shadow_writes;}
}
static void c309_end(void)
{
 if(!c309_frame.active)return;
 unsigned k=c309_frame.part;Compound309270Draw *d=c309_frame.draw+c309_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||c309_frame.pixels!=c309_counts[c309_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++c309_contract_faults;c309_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;c309_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==c309_totals[c309_frame.image];c309_frame.pending=false;
  if(!d->complete){c309_fail(19);return;}
  if(!c309_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   c309_fail(22);family_fault(FC_SOURCE);return;
  }
 }
}
static void c309_accept(void){c309_frame.accepted=fc.ready&&!fc.frame_failed&&c309_finish();}
Compound309270FamilyStatus render_mirror_compound309270_family_status(void)
{
 Compound309270FamilyStatus s={0};s.requested=c309_enabled();s.loaded=c309_life.loaded;s.contributed=c309_frame.contributed;
 s.failed=fc.frame_failed||c309_frame.fault;s.accepted=c309_frame.accepted;s.frame=fc_frame;
 s.active=c309_frame.active;s.pending=c309_frame.pending;s.active_slot=c309_frame.slot;
 s.active_part=c309_frame.part<4?c309_parts[c309_frame.part]:UINT_MAX;s.material_mask=c309_frame.used;s.witnessed_records=c309_witnessed_records;
 memcpy(s.witnessed_count,c309_witnessed_count,sizeof s.witnessed_count);
 s.phase_observations=c309_phase_observations;s.shot_resumptions=c309_shot_resumptions;s.hit_count=c309_hit_count;s.linked_retirements=c309_linked_retirements;s.consumed_events=c309_life.consumed;
 s.blend_retirements=c309_blend_retirements;s.normal_retirements=c309_normal_retirements;s.shadow_writes=c309_shadow_writes;
 s.clipped=c309_clipped;s.unwitnessed=c309_unwitnessed;s.lifetime_losses=c309_lifetime_losses;s.bank_losses=c309_bank_losses;
 s.contract_faults=c309_contract_faults;s.first_reason=c309_first_reason;
 for(unsigned i=0;i<100;i++)s.births[i]=c309_slots[i].birth;
 memcpy(s.draw,c309_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<100;i++)if(s.draw[i].token)s.draw[i].final_gate=enemy[i].aniactive;
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=c309_owned[i]!=0;s.shadowed_cells+=c309_owned[i]&&c309_shadows[i];}return s;
}
bool render_mirror_compound309270_pre_draw(Compound309270Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!c309_frame.active||c309_frame.part||c309_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=c309_frame.draw[c309_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_compound309270_pre_part(Compound309270Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!c309_frame.active||c309_frame.pixels||
 c309_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=c309_frame.draw[c309_frame.slot];unsigned k=c309_frame.part;*part=c309_parts[k];
 unsigned x=(unsigned)d->x+c309_px[k],y=(unsigned)d->y+c309_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_compound309270_callbacks(unsigned slot,Compound309270Write *out,size_t capacity)
{
 if(slot>=100||!out||capacity<c309_frame.draw[slot].callback_count)return 0;
 unsigned n=c309_frame.draw[slot].callback_count;memcpy(out,c309_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_compound309270_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!c309_frame.accepted||fc.frame_active||fc.frame_failed||
 !c309_frame.contributed||!c309_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,c309_owned,64000);memcpy(shadows,c309_shadows,64000);return true;
}
