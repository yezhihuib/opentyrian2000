/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private default-OFF type462 NEWSHD18/55/93. Native random allocation,
 * initialization, animation advancement and successful shot release only.
 * Writes renderer sidecars/RGB only. No gameplay, INDEX, RNG or event writes.
 * Separate from the six randomprops records and their unchanged contracts.
 */
#include "firing_rock462_native.inc"
#include "firing_rock462_asset_pins.inc"
/* Existing engine-owned table, inspected read-only. */
extern JE_word levelEnemyMax,levelEnemy[40];
static const unsigned fr462_table[33]={317,318,319,320,321,322,323,324,317,318,319,320,321,322,323,324,317,318,319,320,321,322,323,324,462,260,261,263,265,266,268,135,136};
static struct {uint64_t generation,epoch,token,witness;bool exhausted,pending,initialized,live;
 unsigned record,cycle,gate;uint64_t phase_tick;FiringRock462Birth birth;Sprite2_array *bank;const Uint8 *data;size_t bytes;} fr462_slots[100];
static struct {uint64_t epoch,serial;bool exhausted,loaded;char root[1024];
 struct {bool live;uint64_t token,epoch,generation;unsigned record;int slot;} call;} fr462_life;
static struct {bool checked,valid;char root[1024];Asset member[3];} fr462_resources;
static struct {bool contributed,fault,active,pending,accepted;unsigned slot,image,part,pixels,used;
 FiringRock462Draw draw[25];FiringRock462Write writes[25][672];} fr462_frame;
static unsigned fr462_witnessed_records;
static uint64_t fr462_witnessed_count[1];
static uint64_t fr462_phase_observations,fr462_shot_resumptions,fr462_filtered_fallbacks;
static bool fr462_resources_current(void);
static int fr462_record_index(unsigned record)
{
 for(unsigned i=0;i<1;i++)if(fr462_records[i].record==record)return (int)i;
 return -1;
}
static uint8_t fr462_owned[64000],fr462_shadows[64000];
/* Alpha-only art beyond native support is separately owned. In particular it
 * never grants a native blend exemption for a foreign hd_owner. */
static uint8_t fr462_extra_owner[4096000],fr462_extra_cell[64000];
static uint64_t fr462_extra_retirements;
static bool fr462_extra(size_t n){return n<4096000&&fr462_extra_owner[n]!=0;}
static uint64_t fr462_blend_retirements,fr462_normal_retirements,fr462_shadow_writes;
static uint64_t fr462_clipped,fr462_unwitnessed,fr462_lifetime_losses,fr462_bank_losses,fr462_contract_faults;
static unsigned fr462_first_reason;
static const char *fr462_root(void){const char *p=getenv("FIRING_ROCK462_ASSET_DIR");return p?p:"";}
static bool fr462_enabled(void)
{
 const char *e=getenv("FIRING_ROCK462_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return B313_FAMILY_CANVAS_DIAGNOSTIC&&e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
}
static bool fr462_level_scope(void)
{
 return fr462_enabled()&&episodeNum==1&&lvlFileNum==2&&mainLevel==6&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!manual_hd_enabled&&!asteroid_hd_enabled&&
 !xmas&&!isNetworkGame&&!twoPlayerMode&&!twoPlayerLinked&&!galagaMode&&!record_demo&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode&&!onePlayerAction&&!superTyrian&&superArcadeMode==SA_NONE&&
 !timedBattleMode&&!bonusLevel&&!normalBonusLevelCurrent&&!bonusLevelCurrent;
}
static bool fr462_table_current(void)
{
 if(levelEnemyMax!=33)return false;
 for(unsigned i=0;i<33;i++)if(levelEnemy[i]!=fr462_table[i])return false;
 return true;
}
static bool fr462_scope(void)
{
 return fr462_life.loaded&&!fr462_life.exhausted&&fr462_level_scope()&&terrain_file=='z'&&
 fr462_table_current()&&!strcmp(fr462_life.root,fr462_root());
}
static void fr462_fail(unsigned reason)
{
 if(!fr462_first_reason)fr462_first_reason=reason;
 fr462_frame.fault=true;fr462_frame.accepted=false;fr462_frame.active=fr462_frame.pending=false;
 if(fr462_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;family_fault(FC_SOURCE);}
}
void render_mirror_firing_rock462_retired(unsigned slot)
{
 if(slot>=100)return;
 if(fr462_slots[slot].live||fr462_slots[slot].pending){
  ++fr462_lifetime_losses;
  if(slot<25&&fr462_frame.draw[slot].token)fr462_fail(1);
 }
 fr462_slots[slot].live=fr462_slots[slot].pending=fr462_slots[slot].initialized=false;
 if(fr462_slots[slot].birth.live){
  fr462_slots[slot].birth.retired_frame=fc_frame;
  fr462_slots[slot].birth.retired_y=enemy[slot].ey;
  fr462_slots[slot].birth.retirement_reason=enemy[slot].ey>190?1:enemy[slot].ey<-112?2:
   (enemy[slot].ex<-80||enemy[slot].ex>340)?3:4;
 }
 fr462_slots[slot].birth.live=false;
}
static void fr462_reset(void)
{
 if(fr462_frame.contributed||fr462_frame.active||fr462_frame.pending)fr462_fail(2);
 for(unsigned i=0;i<100;i++)render_mirror_firing_rock462_retired(i);
 fr462_life.call.live=false;
 if(fr462_life.epoch==UINT64_MAX)fr462_life.exhausted=true;else ++fr462_life.epoch;
}
void render_mirror_firing_rock462_level_begin(char map,char shape)
{
 fr462_reset();fr462_life.loaded=false;fr462_witnessed_records=0;memset(fr462_witnessed_count,0,sizeof fr462_witnessed_count);
 for(unsigned i=0;i<100;i++)memset(&fr462_slots[i].birth,0,sizeof fr462_slots[i].birth);
 if(!fr462_level_scope()||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||!fr462_table_current()||
 !fr462_root()[0]||strlen(fr462_root())>=sizeof fr462_life.root)return;
 strcpy(fr462_life.root,fr462_root());fr462_life.loaded=true;
}
static int fr462_slot(const void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 return a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0]?-1:(int)((a-b)/sizeof enemy[0]);
}
static bool fr462_source(Sprite2_array *bank)
{
 if(!bank||bank==&spriteSheet8||!bank->data||bank->data==spriteSheet8.data||bank->size!=42012)return false;
 bool bound=false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]==8&&bank==enemySpriteSheets+i)bound=true;
 if(!bound||asteroid1_stamp(bank->data,bank->size)!=UINT64_C(0x913975450e0fc00d))return false;
 if(asteroid1_record_stamp(462)!=UINT64_C(0xd2a0e655d0091793)||
 global_front_record_stamp(weapons+116)!=UINT64_C(0xdb5459e53be5c84c))return false;
 return true;
}
static bool fr462_colors(void)
{
 for(unsigned i=0;i<COUNTOF(fr462_palette);i++)if((rgb_palette[fr462_palette[i].index]&0xffffffu)!=fr462_palette[i].rgb)return false;
 return true;
}
/* stage0 constructor, stage1 original draw, stage2 post-draw currentness.
 * Filters0x70 and0xD0 are legal native effects, never damaged resources. */
static bool fr462_shape(unsigned slot,unsigned stage)
{
 if(slot>=25)return false;
 const struct JE_SingleEnemyType *e=enemy+slot;
 if(e->enemytype!=462||e->enemydatofs!=enemyDat+462||!fr462_source(e->sprite2s)||
 e->size!=1||(e->filter&&e->filter!=0x70&&e->filter!=0xd0)||e->ani!=9||e->animin!=1||e->animax!=9||e->aniwhenfire!=2||
 e->scoreitem||e->special||e->edamaged||!e->armorleft||e->linknum||e->enemydie||
 e->exc||e->eyc!=1||e->fixedmovey||e->excc||e->eycc||e->xaccel||e->yaccel||
 e->exrev!=100||e->eyrev!=100||!e->enemyground||e->explonum||
 e->tur[0]!=116||e->tur[1]||e->tur[2]!=255||e->freq[0]!=100||e->freq[1]||e->freq[2]!=100||
 e->launchfreq||e->launchtype||e->launchspecial||e->edgr||e->edlevel||e->edani)return false;
 static const unsigned sequence[20]={93,55,18,18,18,55,55,55,93};
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=sequence[i])return false;
 if(stage==0){
  if(e->enemycycle!=1||e->aniactive!=2||e->filter||e->mapoffset||e->ey!=-12||e->ex<6||e->ex>255||e->iced||e->launchwait||
   e->exccw||e->eyccw||e->exccwmax||e->eyccwmax||e->exccadd!=-1||e->eyccadd!=-1||
   e->exca!=-1||e->eyca!=-1||e->xminbounce!=-10000||e->xmaxbounce!=10000||
   e->yminbounce!=-10000||e->ymaxbounce!=10000)return false;
  for(unsigned i=0;i<3;i++)if(e->eshotmultipos[i]||e->eshotwait[i]!=(i==1?255:20))return false;
 }else if(e->enemycycle<1||e->enemycycle>9||
  !((e->aniactive==1&&(stage==2||e->enemycycle<9))||
    (e->aniactive==2&&(e->enemycycle==1||e->enemycycle==9))))return false;
 return true;
}
static int fr462_image(unsigned base)
{for(unsigned i=0;i<3;i++)if(fr462_images[i].base==base)return (int)i;return -1;}
uint64_t render_mirror_firing_rock462_spawn_begin(unsigned record,unsigned pool,int unique)
{
 if(fr462_life.call.live){fr462_life.call.live=false;fr462_fail(3);return 0;}
 if(!fr462_scope()||fr462_record_index(record)<0||pool||unique||!enemiesActive)return 0;
 if(fr462_life.serial==UINT64_MAX){fr462_life.exhausted=true;return 0;}
 fr462_life.call.live=true;fr462_life.call.token=++fr462_life.serial;fr462_life.call.epoch=fr462_life.epoch;
 fr462_life.call.record=record;fr462_life.call.slot=-1;fr462_life.call.generation=0;
 return fr462_life.call.token;
}
void render_mirror_firing_rock462_enemy_allocated(void *p,unsigned record,int unique)
{
 int s=fr462_slot(p);if(s<0)return;
 render_mirror_firing_rock462_retired((unsigned)s);
 if(fr462_slots[s].generation==UINT64_MAX){fr462_slots[s].exhausted=true;return;}
 if(fr462_slots[s].exhausted)return;
 ++fr462_slots[s].generation; /* Every allocation, including unrelated records. */
 if(fr462_life.call.live&&fr462_scope()&&s<25&&enemyAvail[s]==1&&!unique&&
 record==fr462_life.call.record&&fr462_life.call.slot==-1){
  fr462_slots[s].pending=true;fr462_slots[s].record=record;fr462_life.call.slot=s;
  fr462_life.call.generation=fr462_slots[s].generation;
 }
}
void render_mirror_firing_rock462_enemy_initialized(void *p,unsigned record,unsigned avail)
{
 int s=fr462_slot(p);if(s<0)return;
 fr462_slots[s].initialized=fr462_slots[s].pending&&fr462_life.call.live&&fr462_scope()&&s<25&&
 fr462_life.call.slot==s&&fr462_life.call.generation==fr462_slots[s].generation&&
 record==fr462_life.call.record&&avail==0&&enemyAvail[s]==1&&fr462_shape((unsigned)s,0);
}
void render_mirror_firing_rock462_spawn_commit(uint64_t token,unsigned one_based)
{
 if(!token)return;
 int s=fr462_life.call.slot;
 bool ok=fr462_life.call.live&&token==fr462_life.call.token&&fr462_life.call.epoch==fr462_life.epoch&&fr462_scope()&&
 s>=0&&s<25&&one_based==(unsigned)s+1;
 if(ok)ok=fr462_slots[s].pending&&fr462_slots[s].initialized&&fr462_life.call.generation==fr462_slots[s].generation&&
 enemyAvail[s]==0&&fr462_slots[s].record==fr462_life.call.record&&fr462_shape((unsigned)s,0);
 if(s>=0&&s<100){
  fr462_slots[s].live=ok;fr462_slots[s].pending=fr462_slots[s].initialized=false;
  if(ok){fr462_slots[s].cycle=1;fr462_slots[s].gate=2;fr462_slots[s].phase_tick=0;fr462_slots[s].witness=fr462_slots[s].generation;fr462_slots[s].epoch=fr462_life.epoch;fr462_slots[s].token=token;
   fr462_slots[s].bank=enemy[s].sprite2s;fr462_slots[s].data=enemy[s].sprite2s->data;fr462_slots[s].bytes=enemy[s].sprite2s->size;
   unsigned ri=(unsigned)fr462_record_index(fr462_slots[s].record);fr462_witnessed_records|=1u<<ri;++fr462_witnessed_count[ri];
   fr462_slots[s].birth=(FiringRock462Birth){.epoch=fr462_life.epoch,.token=token,.generation=fr462_slots[s].generation,
    .slot=(unsigned)s,.record=fr462_slots[s].record,.bank_role=8,.bank_bytes=42012,
    .bank_stamp=UINT64_C(0x913975450e0fc00d),.record_stamp=fr462_records[ri].stamp,
    .bank_object=(uintptr_t)fr462_slots[s].bank,.bank_data=(uintptr_t)fr462_slots[s].data,
    .birth_frame=fc_frame,.cycle=1,.gate=2,.birth_time=curLoc,.birth_x=enemy[s].ex,.birth_y=enemy[s].ey,.birth_eyc=enemy[s].eyc,.live=true,.initialized=true};
  }
 }
 fr462_life.call.live=false; /* Allocation failure closes rather than rearms token. */
}
void render_mirror_firing_rock462_bank_changed(Sprite2_array *bank)
{
 for(unsigned i=0;i<100;i++)if(fr462_slots[i].live&&fr462_slots[i].bank==bank){++fr462_bank_losses;render_mirror_firing_rock462_retired(i);}
 if(fr462_life.call.live){fr462_life.call.live=false;fr462_fail(4);}
}
static bool fr462_witness(unsigned s)
{
 return s<25&&fr462_slots[s].live&&!fr462_slots[s].exhausted&&fr462_slots[s].epoch==fr462_life.epoch&&
 fr462_slots[s].generation==fr462_slots[s].witness&&enemyAvail[s]==0&&
 enemy[s].sprite2s&&fr462_slots[s].bank==enemy[s].sprite2s&&fr462_slots[s].data==enemy[s].sprite2s->data&&
 fr462_slots[s].bytes==enemy[s].sprite2s->size;
}
/* Native semantic observers do not depend on canvas/frame admission. A rejected
 * world frame still advances this actual actor's lifetime witness. */
void render_mirror_firing_rock462_enemy_animated(unsigned slot)
{
 if(slot>=25||!fr462_slots[slot].live)return;
 if(!fr462_scope()||!fr462_witness(slot)||!fr462_shape(slot,1)||
 fr462_slots[slot].phase_tick==fc_frame){render_mirror_firing_rock462_retired(slot);return;}
 unsigned cycle=fr462_slots[slot].cycle,gate=fr462_slots[slot].gate;
 if(gate==1){++cycle;if(cycle==9)gate=2;else if(cycle>9)cycle=1;}
 if(enemy[slot].enemycycle!=cycle||enemy[slot].aniactive!=gate){render_mirror_firing_rock462_retired(slot);return;}
 fr462_slots[slot].cycle=cycle;fr462_slots[slot].gate=gate;fr462_slots[slot].phase_tick=fc_frame;
 FiringRock462Birth *b=&fr462_slots[slot].birth;b->cycle=cycle;b->gate=gate;b->phase_tick=fc_frame;
 ++b->phase_observations;++fr462_phase_observations;
}
void render_mirror_firing_rock462_shot_fired(unsigned slot,unsigned weapon,unsigned turret,unsigned shot_slot)
{
 if(slot>=25||!fr462_slots[slot].live)return;
 if(!fr462_scope()||!fr462_witness(slot)||!fr462_shape(slot,2)||weapon!=116||turret!=1||
 shot_slot>=ENEMY_SHOT_MAX||enemyShotAvail[shot_slot]!=0||fr462_slots[slot].phase_tick!=fc_frame||
 fr462_slots[slot].gate!=2||(fr462_slots[slot].cycle!=1&&fr462_slots[slot].cycle!=9)||
 enemy[slot].enemycycle!=fr462_slots[slot].cycle||enemy[slot].aniactive!=1){render_mirror_firing_rock462_retired(slot);return;}
 fr462_slots[slot].gate=1;FiringRock462Birth *b=&fr462_slots[slot].birth;b->gate=1;
 ++b->shot_count;b->last_shot_frame=fc_frame;++fr462_shot_resumptions;
 FiringRock462Draw *d=fr462_frame.draw+slot;
 if(d->token&&d->generation==fr462_slots[slot].generation&&d->cycle==enemy[slot].enemycycle&&d->draw_gate==2)d->shot_resumed=true;
}
static void fr462_tick(void)
{
 if(!fr462_enabled()&&!fr462_life.loaded&&!fr462_frame.contributed&&!fr462_frame.active&&!fr462_frame.pending)return;
 if(fr462_frame.contributed){ready=last_output_valid=last_output_scene_hd=have_fade_saved=false;fade_mode=0;}
 memset(&fr462_frame,0,sizeof fr462_frame);memset(fr462_owned,0,sizeof fr462_owned);memset(fr462_shadows,0,sizeof fr462_shadows);
 memset(fr462_extra_owner,0,sizeof fr462_extra_owner);memset(fr462_extra_cell,0,sizeof fr462_extra_cell);fr462_first_reason=0;
 if(fr462_life.loaded&&!fr462_scope()){fr462_reset();fr462_life.loaded=false;return;}
 for(unsigned i=0;i<25;i++)if(fr462_slots[i].live&&(!fr462_witness(i)||!enemy[i].armorleft||
 enemy[i].enemytype!=fr462_slots[i].record||enemy[i].enemydatofs!=enemyDat+fr462_slots[i].record))render_mirror_firing_rock462_retired(i);
}
static bool fr462_load(unsigned k)
{
 char path[1200];Uint8 header[28],extra,*rgba=NULL;REAR_STAT st;
 int n=snprintf(path,sizeof path,"%s/enemy-newshd-%u-8.hda",fr462_resources.root,fr462_images[k].base);
 if(n<0||(size_t)n>=sizeof path)return false;
 int fd=REAR_OPEN(path);if(fd<0)return false;
 const size_t bytes=172032;
 bool ok=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==(long)(28+bytes)&&
 REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
 uint32_t v[6]={0};
 if(ok){for(unsigned i=0;i<6;i++)for(unsigned j=0;j<4;j++)v[i]|=(uint32_t)header[4+i*4+j]<<(8*j);
 ok=v[0]==1080000+fr462_images[k].base&&v[1]==8&&v[2]==24&&v[3]==28&&!v[4]&&!v[5];}
 if(ok){rgba=malloc(bytes);ok=rgba!=NULL;}
 if(ok)ok=REAR_READ(fd,rgba,bytes)==(int)bytes&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(rgba,bytes)==fr462_images[k].rgba;
 if(REAR_CLOSE(fd))ok=false;
 if(!ok){free(rgba);return false;}
 fr462_resources.member[k]=(Asset){true,true,ASSET_ASTEROID1,(int)fr462_images[k].base,24,28,0,0,8,rgba};return true;
}
static bool fr462_resources_current(void)
{
 if(!fr462_resources.checked||!fr462_resources.valid||strcmp(fr462_resources.root,fr462_root()))return false;
 for(unsigned i=0;i<3;i++){const Asset *a=fr462_resources.member+i;
  if(!a->initialized||!a->valid||a->bank!=ASSET_ASTEROID1||a->index!=(int)fr462_images[i].base||
  a->w!=24||a->h!=28||a->anchor_x||a->anchor_y||a->density!=8||!a->rgba||
  asteroid1_stamp(a->rgba,172032)!=fr462_images[i].rgba)return false;
 }return true;
}
static bool fr462_ready(void)
{
 if(!fr462_scope()||game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 if(!fr462_resources.checked){fr462_resources.checked=true;fr462_resources.valid=true;strcpy(fr462_resources.root,fr462_life.root);
 for(unsigned i=0;i<3;i++)if(!fr462_load(i))fr462_resources.valid=false;}
 if(!fr462_resources_current()){fr462_resources.valid=false;return false;}return true;
}
static void fr462_shutdown(void)
{
 fr462_reset();fr462_life.loaded=false;
 for(unsigned i=0;i<3;i++)free(fr462_resources.member[i].rgba);
 memset(&fr462_resources,0,sizeof fr462_resources);
}
static bool fr462_dependencies(bool partial)
{
 if(!fr462_frame.contributed)return true;
 if(fr462_frame.fault||!fr462_scope()||!fr462_colors()||!fr462_resources_current()||
 game_probe_missing||game_probe_invalid||game_probe_original_reference)return false;
 for(unsigned i=0;i<25;i++)if(fr462_frame.draw[i].token){const FiringRock462Draw *d=fr462_frame.draw+i;unsigned s=i;
  if(!fr462_witness(s)||!fr462_shape(s,2)||d->generation!=fr462_slots[s].generation||
  d->token!=fr462_slots[s].birth.token||d->epoch!=fr462_life.epoch||d->record!=fr462_slots[s].record||
  d->bank_object!=(uintptr_t)enemy[s].sprite2s||d->bank_data!=(uintptr_t)enemy[s].sprite2s->data||
  d->cycle!=enemy[s].enemycycle||d->base!=enemy[s].egr[d->cycle-1]||
  !(enemy[s].aniactive==d->draw_gate||(d->draw_gate==2&&enemy[s].aniactive==1&&d->shot_resumed)))return false;
  if(!d->complete){if(!partial||!fr462_frame.pending||fr462_frame.slot!=s)return false;}
  else if(d->mask!=15||d->next!=4||d->callback_count!=355||
   (!partial&&d->extra_stores!=fr462_images[fr462_image(d->base)].extra))return false;
 }
 return partial||(!fr462_frame.active&&!fr462_frame.pending);
}
/* Pure predicate shared by diagnostic snapshots. */
static bool fr462_finish(void){return fr462_dependencies(false);}
/* Mutating gate used only by actual finish/Present, never support getters. */
static bool fr462_guard(void)
{
 if(fr462_finish())return true;
 fr462_fail(20);return false;
}
/* Invoked before all family tile dispatches, including other families. */
static bool fr462_before_tile(unsigned slot,int part)
{
 if(fr462_frame.contributed&&!fr462_dependencies(true)){fr462_fail(5);return false;}
 if(fr462_frame.pending&&(fr462_frame.active||slot!=fr462_frame.slot||
 fr462_frame.draw[slot].next>=4||part!=(int)fr462_parts[fr462_frame.draw[slot].next])){fr462_fail(6);return false;}
 return true;
}
static bool fr462_geometry(int64_t x,int64_t y){return x>=24&&x<=264&&y>=0&&y<=156;}
static bool fr462_tile(SDL_Surface *surface,unsigned slot,int x,int y,Sprite2_array *sheet,unsigned base,int part,int filter)
{
 if(!fr462_enabled()||slot>=25||fr462_record_index(enemy[slot].enemytype)<0)return false;
 if(!fc.frame_active||fc.frame_failed||!fr462_witness(slot)){++fr462_unwitnessed;return false;}
 unsigned k;for(k=0;k<4&&part!=(int)fr462_parts[k];k++);
 if(k==4){if(fr462_frame.draw[slot].token)fr462_fail(7);return false;}
 int64_t ox=(int64_t)x-fr462_px[k],oy=(int64_t)y-fr462_py[k];
 FiringRock462Draw *d=fr462_frame.draw+slot;
 if(!fr462_geometry(ox,oy)){++fr462_clipped;if(d->token)fr462_fail(8);return false;}
 if(ox!=(int64_t)enemy[slot].ex+enemy[slot].mapoffset-6||oy!=(int64_t)enemy[slot].ey-7||filter!=enemy[slot].filter||(filter&&filter!=0x70)||
 fr462_slots[slot].phase_tick!=fc_frame||
 !fr462_scope()||sheet!=enemy[slot].sprite2s||!fr462_shape(slot,1)||base!=enemy[slot].egr[enemy[slot].enemycycle-1]||fr462_image(base)<0||!fr462_colors()||!fr462_ready()){
  if(filter==0xd0&&k==0)++fr462_filtered_fallbacks;
  if(d->token)fr462_fail(9);
  return false;
 }
 if(k==0){if(d->token||fr462_frame.pending){fr462_fail(10);return false;}}
 else if(!fr462_frame.pending||fr462_frame.slot!=slot||!d->token||d->next!=k||d->x!=ox||d->y!=oy){
  /* No part0 means entirely classic (e.g. top-clipped native bottom calls). */
  if(d->token||fr462_frame.pending)fr462_fail(11);
  return false;
 }
 fg_before_actor();
 if(fc.frame_failed||fc_native_call||fr462_frame.active||suppress||surface!=game_screen||surface!=VGAScreen||
 !family_geometry(false)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_draw_ready(fc_frame)||
 !family_prepare_canvas()){++fr462_contract_faults;fr462_fail(12);family_fault(FC_SOURCE);return false;}
 /* Full body decided before part0. Each native12x14 source is checked before
  * that part's first store. No cached or rectangular restoration follows. */
 for(int row=0;row<14;row++)if(memcmp((const Uint8 *)surface->pixels+(y+row)*320+x,expected+(y+row)*320+x,12)){
 ++fr462_contract_faults;fr462_fail(13);family_fault(FC_WRITER);return false;}
 if(k==0){
  *d=(FiringRock462Draw){.frame=fc_frame,.epoch=fr462_life.epoch,.token=fr462_slots[slot].birth.token,
   .generation=fr462_slots[slot].generation,.slot=slot,.record=fr462_slots[slot].record,
   .cycle=enemy[slot].enemycycle,.draw_gate=enemy[slot].aniactive,.draw_filter=(unsigned)filter,.base=base,.cur_loc=curLoc,.bank_role=8,.bank_bytes=(unsigned)sheet->size,
   .bank_object=(uintptr_t)sheet,.bank_data=(uintptr_t)sheet->data,.x=(int)ox,.y=(int)oy};
  fr462_frame.pending=true;fr462_frame.slot=slot;fr462_frame.image=(unsigned)fr462_image(base);fr462_frame.used|=1u<<fr462_frame.image;
 }
 d->part_order[k]=(unsigned)part;
 fr462_frame.part=k;fr462_frame.pixels=0;fr462_frame.active=true;fr462_frame.contributed=true;return true;
}
/* Central pre-hook retirement occurs before ALL private writer early returns. */
static bool fr462_retire(unsigned off,int style)
{
 bool owned=off<64000&&fr462_owned[off];
 if(owned&&style!=MIRROR_SHADOW){if(style==MIRROR_BLEND)++fr462_blend_retirements;else ++fr462_normal_retirements;
 fr462_owned[off]=fr462_shadows[off]=0;}
 if(off<64000&&style!=MIRROR_SHADOW&&fr462_extra_cell[off]){
  unsigned x=off%320,y=off/320;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   size_t n=(y*8+sy)*2560+x*8+sx;fr462_extra_retirements+=fr462_extra_owner[n]!=0;fr462_extra_owner[n]=0;
  }
  fr462_extra_cell[off]=0;
 }
 return owned;
}
static bool fr462_pixel(unsigned x,unsigned y,int style)
{
 if(!fr462_frame.active){if(fr462_frame.pending){fr462_fail(14);return true;}return false;}
 FiringRock462Draw *d=fr462_frame.draw+fr462_frame.slot;
 unsigned k=fr462_frame.part;
 if(k>=4||fr462_frame.pixels>=fr462_counts[fr462_frame.image][k]){++fr462_contract_faults;fr462_fail(15);return true;}
 const FiringRock462Write *w=fr462_native[fr462_frame.image][k]+fr462_frame.pixels;
 unsigned lx=fr462_px[k]+w->x,ly=fr462_py[k]+w->y;
 Uint8 index=d->draw_filter?(Uint8)(d->draw_filter|(w->index&15)):w->index;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+lx||y!=(unsigned)d->y+ly||
 ((const Uint8 *)fc_source_pixels)[y*320+x]!=index||expected[y*320+x]!=index){
 ++fr462_contract_faults;fr462_fail(16);family_fault(FC_ORDER);return true;}
 const Asset *a=&fr462_resources.member[fr462_frame.image];
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
  size_t n=(y*8+sy)*2560+x*8+sx;Uint32 *dst=(Uint32 *)canvas->pixels+n;
  const Uint8 *art=a->rgba+(((ly*8+sy)*192+lx*8+sx)*4);
  Uint8 filtered[4];if(d->draw_filter){enemy_filter_rgba(art,(Uint8)d->draw_filter,filtered);art=filtered;}
  /* Actual current canvas underlay. Alpha0 retains RGB but gains native
   * ownership; native holes never call here and remain entirely untouched. */
  *dst=blend_rgba(*dst,art,art[3]);hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;
  OHS_SURVIVAL_WRITE(canvas,dst,FIRING_ROCK462_HD_STORE_TAG);
 }
 unsigned off=y*320+x;
 lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);
 fr462_owned[off]=(uint8_t)(fr462_frame.slot+1);fr462_shadows[off]=0;selected[off]=1;
 if(d->callback_count>=672){fr462_fail(17);return true;}
 fr462_frame.writes[fr462_frame.slot][d->callback_count++]=(FiringRock462Write){(uint8_t)lx,(uint8_t)ly,index};
 ++fr462_frame.pixels;d->part_count[k]=fr462_frame.pixels;return true;
}
static void fr462_shadow(unsigned off)
{
 if(off<64000&&fr462_owned[off]){if(fr462_shadows[off]<255)++fr462_shadows[off];++fr462_shadow_writes;}
}
/* Complete authentic body order authorizes authored nonzero-alpha coverage
 * in the finite24x28 rectangle only. Native holes retain their INDEX bytes.
 * Current RGB is used directly, never cached/background reconstruction. */
static void fr462_authored_support(FiringRock462Draw *d)
{
 const Asset *a=fr462_resources.member+fr462_frame.image;
 for(unsigned ay=0;ay<224;ay++)for(unsigned ax=0;ax<192;ax++){
  if(fr462_native_mask[(ay/8)*24+ax/8])continue;
  const Uint8 *art=a->rgba+(ay*192+ax)*4;if(!art[3])continue;
  Uint8 filtered[4];if(d->draw_filter){enemy_filter_rgba(art,(Uint8)d->draw_filter,filtered);art=filtered;}
  size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
  Uint32 *dst=(Uint32 *)canvas->pixels+n;*dst=blend_rgba(*dst,art,art[3]);
  fr462_extra_owner[n]=(uint8_t)(d->slot+1);
  fr462_extra_cell[(d->y+(int)(ay/8))*320+d->x+ax/8]=1;++d->extra_stores;
  OHS_SURVIVAL_WRITE(canvas,dst,FIRING_ROCK462_EXTRA_STORE_TAG);
 }
 if(d->extra_stores!=fr462_images[fr462_frame.image].extra){fr462_fail(21);family_fault(FC_ORDER);}
}
static void fr462_end(void)
{
 if(!fr462_frame.active)return;
 unsigned k=fr462_frame.part;FiringRock462Draw *d=fr462_frame.draw+fr462_frame.slot;
 if(k>=4||d->next!=k||d->mask!=(1u<<k)-1||fr462_frame.pixels!=fr462_counts[fr462_frame.image][k]||!b313_family_writer_draw_ready(fc_frame)){
 ++fr462_contract_faults;fr462_fail(18);family_fault(FC_ORDER);return;}
 d->mask|=1u<<k;d->next=k+1;fr462_frame.active=false;
 if(k==3){
  d->complete=d->mask==15&&d->callback_count==fr462_totals[fr462_frame.image];fr462_frame.pending=false;
  if(!d->complete){fr462_fail(19);return;}
  if(!fr462_dependencies(true)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
   fr462_fail(22);family_fault(FC_SOURCE);return;
  }
  fr462_authored_support(d);
 }
}
static void fr462_accept(void){fr462_frame.accepted=fc.ready&&!fc.frame_failed&&fr462_finish();}
FiringRock462FamilyStatus render_mirror_firing_rock462_family_status(void)
{
 FiringRock462FamilyStatus s={0};s.requested=fr462_enabled();s.loaded=fr462_life.loaded;s.contributed=fr462_frame.contributed;
 s.failed=fc.frame_failed||fr462_frame.fault;s.accepted=fr462_frame.accepted;s.frame=fc_frame;
 s.active=fr462_frame.active;s.pending=fr462_frame.pending;s.active_slot=fr462_frame.slot;
 s.active_part=fr462_frame.part<4?fr462_parts[fr462_frame.part]:UINT_MAX;s.material_mask=fr462_frame.used;s.witnessed_records=fr462_witnessed_records;
 memcpy(s.witnessed_count,fr462_witnessed_count,sizeof s.witnessed_count);
 s.phase_observations=fr462_phase_observations;s.shot_resumptions=fr462_shot_resumptions;s.filtered_fallbacks=fr462_filtered_fallbacks;s.extra_retirements=fr462_extra_retirements;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=fr462_extra_owner[i]!=0;
 s.blend_retirements=fr462_blend_retirements;s.normal_retirements=fr462_normal_retirements;s.shadow_writes=fr462_shadow_writes;
 s.clipped=fr462_clipped;s.unwitnessed=fr462_unwitnessed;s.lifetime_losses=fr462_lifetime_losses;s.bank_losses=fr462_bank_losses;
 s.contract_faults=fr462_contract_faults;s.first_reason=fr462_first_reason;
 for(unsigned i=0;i<25;i++)s.births[i]=fr462_slots[i].birth;
 memcpy(s.draw,fr462_frame.draw,sizeof s.draw);
 for(unsigned i=0;i<25;i++)if(s.draw[i].token)s.draw[i].final_gate=enemy[i].aniactive;
 for(unsigned i=0;i<64000;i++){s.surviving_cells+=fr462_owned[i]!=0;s.shadowed_cells+=fr462_owned[i]&&fr462_shadows[i];}return s;
}
bool render_mirror_firing_rock462_pre_draw(FiringRock462Draw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=43008||!native||bytes!=672||!fr462_frame.active||fr462_frame.part||fr462_frame.pixels||
 !fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=fr462_frame.draw[fr462_frame.slot];
 for(unsigned y=0;y<224;y++)memcpy(argb+y*192,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,192*sizeof *argb);
 for(unsigned y=0;y<28;y++)memcpy(native+y*24,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,24);
 return true;
}
/* Per-part live-underlay copy, independent of the whole-body capture. */
bool render_mirror_firing_rock462_pre_part(FiringRock462Draw *d,unsigned *part,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!part||!argb||count!=10752||!native||bytes!=168||!fr462_frame.active||fr462_frame.pixels||
 fr462_frame.part>=4||!fc.frame_active||fc.frame_failed||!family_geometry(true))return false;
 *d=fr462_frame.draw[fr462_frame.slot];unsigned k=fr462_frame.part;*part=fr462_parts[k];
 unsigned x=(unsigned)d->x+fr462_px[k],y=(unsigned)d->y+fr462_py[k];
 for(unsigned row=0;row<112;row++)memcpy(argb+row*96,(const Uint32 *)canvas->pixels+(y*8+row)*2560+x*8,96*sizeof *argb);
 for(unsigned row=0;row<14;row++)memcpy(native+row*12,(const Uint8 *)fc_source_pixels+(y+row)*320+x,12);
 return true;
}
unsigned render_mirror_firing_rock462_callbacks(unsigned slot,FiringRock462Write *out,size_t capacity)
{
 if(slot>=25||!out||capacity<fr462_frame.draw[slot].callback_count)return 0;
 unsigned n=fr462_frame.draw[slot].callback_count;memcpy(out,fr462_frame.writes[slot],n*sizeof *out);return n;
}
bool render_mirror_firing_rock462_family_support(uint8_t *owners,size_t bytes,uint8_t *shadows,size_t shadow_bytes)
{
 if(!owners||bytes!=64000||!shadows||shadow_bytes!=64000||!fr462_frame.accepted||fc.frame_active||fc.frame_failed||
 !fr462_frame.contributed||!fr462_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(owners,fr462_owned,64000);memcpy(shadows,fr462_shadows,64000);return true;
}

bool render_mirror_firing_rock462_extra_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=4096000||!fr462_frame.accepted||fc.frame_active||fc.frame_failed||
 !fr462_frame.contributed||!fr462_finish()||!family_geometry(true)||
 memcmp(fc_palette,rgb_palette,sizeof fc_palette)||!b313_family_writer_peek_current(fc_frame))return false;
 for(unsigned i=0;i<64000;i++)if(expected[i]!=((const Uint8 *)fc_source_pixels)[i])return false;
 memcpy(out,fr462_extra_owner,bytes);return true;
}
