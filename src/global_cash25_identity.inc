/* SPDX-License-Identifier: GPL-2.0-or-later
 * Native records391–395 body identity; no level or sprite-ID-only authorization.
 * Included by the Cash25 owner after the global registry and byte hasher. */
static struct {
 uint64_t generation,witnessed,born_tick,last_tick,animation_tick,record;
 bool pending,role;
 unsigned next_phase,observed_phase;
 int value,profile;
} global_cash25_body_slots[100];

static int global_cash25_body_profile(unsigned record)
{return record>=391&&record<=395?(int)record-391:-1;}
static unsigned global_cash25_body_first_index(unsigned profile)
{return profile==0?7:profile==1?26:profile==2?20:profile==3?32:14;}
static unsigned global_cash25_body_frame_count(unsigned profile)
{return profile<3?6:5;}
static unsigned global_cash25_body_animation_length(unsigned profile)
{return profile<3?6:16;}
/* Canonical on-disk order, not compiler struct padding. */
static uint64_t global_cash25_body_record_stamp_for(unsigned profile)
{
 if(profile>=5)return 0;
 unsigned record=391+profile;
 Uint8 bytes[77];size_t n=0;
#define CASH_BYTE(v) do {bytes[n++]=(Uint8)(v);} while(0)
#define CASH_WORD(v) do {unsigned cv_=(unsigned)(v);CASH_BYTE(cv_);CASH_BYTE(cv_>>8);} while(0)
 CASH_BYTE(enemyDat[record].ani);
 for(unsigned i=0;i<3;i++)CASH_BYTE(enemyDat[record].tur[i]);
 for(unsigned i=0;i<3;i++)CASH_BYTE(enemyDat[record].freq[i]);
 CASH_BYTE(enemyDat[record].xmove);CASH_BYTE(enemyDat[record].ymove);
 CASH_BYTE(enemyDat[record].xaccel);CASH_BYTE(enemyDat[record].yaccel);
 CASH_BYTE(enemyDat[record].xcaccel);CASH_BYTE(enemyDat[record].ycaccel);
 CASH_WORD(enemyDat[record].startx);CASH_WORD(enemyDat[record].starty);
 CASH_BYTE(enemyDat[record].startxc);CASH_BYTE(enemyDat[record].startyc);
 CASH_BYTE(enemyDat[record].armor);CASH_BYTE(enemyDat[record].esize);
 for(unsigned i=0;i<20;i++)CASH_WORD(enemyDat[record].egraphic[i]);
 CASH_BYTE(enemyDat[record].explosiontype);CASH_BYTE(enemyDat[record].animate);CASH_BYTE(enemyDat[record].shapebank);
 CASH_BYTE(enemyDat[record].xrev);CASH_BYTE(enemyDat[record].yrev);CASH_WORD(enemyDat[record].dgr);
 CASH_BYTE(enemyDat[record].dlevel);CASH_BYTE(enemyDat[record].dani);CASH_BYTE(enemyDat[record].elaunchfreq);
 CASH_WORD(enemyDat[record].elaunchtype);CASH_WORD(enemyDat[record].value);CASH_WORD(enemyDat[record].eenemydie);
#undef CASH_BYTE
#undef CASH_WORD
 return n==77?global_bytes_hash(bytes,n):0;
}
static uint64_t global_cash25_body_record_stamp(void)
{return global_cash25_body_record_stamp_for(0);}
static bool global_cash25_body_record_matches(unsigned profile)
{
 if(profile>=5)return false;
 uint64_t h=global_cash25_body_record_stamp_for(profile);
 const uint64_t *pins=profile==0?global_cash25_record_fnv:profile==1?global_cash50_record_fnv:profile==2?global_cash75_record_fnv:profile==3?global_gem100_record_fnv:global_gem250_record_fnv;
 unsigned count=profile==0?COUNTOF(global_cash25_record_fnv):profile==1?COUNTOF(global_cash50_record_fnv):profile==2?COUNTOF(global_cash75_record_fnv):profile==3?COUNTOF(global_gem100_record_fnv):COUNTOF(global_gem250_record_fnv);
 for(unsigned i=0;i<count;i++)if(h==pins[i])return true;
 return false;
}
static bool global_cash25_body_records_match(void)
{for(unsigned p=0;p<5;p++)if(!global_cash25_body_record_matches(p))return false;return true;}
static int global_cash25_body_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
static bool global_cash25_body_shape(unsigned slot)
{
 const struct JE_SingleEnemyType *e=enemy+slot;
 int profile=global_cash25_body_slots[slot].profile;if(profile<0||profile>=5)return false;
 unsigned record=391+(unsigned)profile;
 if(e->enemytype!=record||e->enemydatofs!=&enemyDat[record]||e->sprite2s!=&spriteSheet11||
    !spriteSheet11.data||!spriteSheet11.size||e->size!=0||!e->scoreitem||e->edamaged||
    e->filter||e->ani!=global_cash25_body_animation_length((unsigned)profile)||e->animin!=1||e->aniactive!=1||e->animax||e->aniwhenfire||
    e->armorleft!=255||e->edani!=enemyDat[record].dani||e->edgr!=enemyDat[record].dgr||
    e->edlevel!=enemyDat[record].dlevel)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=enemyDat[record].egraphic[i])return false;
 return true;
}
static void global_cash25_body_identity_reset(void)
{memset(global_cash25_body_slots,0,sizeof(global_cash25_body_slots));}
static void global_cash25_body_identity_frame_begin(void)
{
 bool record=global_cash25_body_records_match();
 for(unsigned i=0;i<COUNTOF(global_cash25_body_slots);i++)
  if(global_cash25_body_slots[i].role&&(!record||enemyAvail[i]!=2||!global_cash25_body_shape(i)||
    enemy[i].evalue!=global_cash25_body_slots[i].value))global_cash25_body_slots[i].role=false;
}
void render_mirror_cash25_enemy_allocated(void *ptr,unsigned record,int unique_shape)
{
 int slot=global_cash25_body_slot(ptr);if(slot<0)return;
 if(++global_cash25_body_slots[slot].generation==0)++global_cash25_body_slots[slot].generation;
 global_cash25_body_slots[slot].role=false;global_cash25_body_slots[slot].next_phase=0;
 global_cash25_body_slots[slot].profile=global_cash25_body_profile(record);
 global_cash25_body_slots[slot].pending=enemyAvail[slot]==1&&global_cash25_body_slots[slot].profile>=0&&
  (unique_shape<=0||unique_shape==21)&&global_cash25_body_records_match();
 global_cash25_body_slots[slot].born_tick=mirror_logic_tick;
 global_cash25_body_slots[slot].record=global_cash25_body_record_stamp_for((unsigned)global_cash25_body_slots[slot].profile);
}
void render_mirror_cash25_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=global_cash25_body_slot(ptr);if(slot<0)return;
 bool fresh=global_cash25_body_slots[slot].pending&&global_cash25_body_slots[slot].born_tick==mirror_logic_tick;
 global_cash25_body_slots[slot].pending=false;
 bool good=fresh&&global_cash25_body_profile(record)==global_cash25_body_slots[slot].profile&&avail==2&&enemyAvail[slot]==1&&global_cash25_body_records_match()&&
  global_cash25_body_slots[slot].record==global_cash25_body_record_stamp_for((unsigned)global_cash25_body_slots[slot].profile)&&global_cash25_body_shape(slot)&&enemy[slot].enemycycle==0;
 global_cash25_body_slots[slot].role=good;
 global_cash25_body_slots[slot].next_phase=good?1:0;
 global_cash25_body_slots[slot].witnessed=global_cash25_body_slots[slot].generation;
 global_cash25_body_slots[slot].last_tick=UINT64_MAX;
 global_cash25_body_slots[slot].animation_tick=UINT64_MAX;global_cash25_body_slots[slot].observed_phase=0;
 global_cash25_body_slots[slot].value=enemy[slot].evalue;
}
/* The real animation block runs before the vertical visibility gate. Observe
 * its exact phase even while a negative-y coin cannot yet draw. Horizontal
 * offscreen skips do not call this hook and do not advance native animation. */
void render_mirror_cash25_enemy_animated(unsigned slot)
{
 if(slot>=COUNTOF(global_cash25_body_slots))return;
 const struct JE_SingleEnemyType *e=enemy+slot;
 bool good=global_cash25_body_slots[slot].role&&
  global_cash25_body_slots[slot].witnessed==global_cash25_body_slots[slot].generation&&
  global_cash25_body_slots[slot].animation_tick!=mirror_logic_tick&&
  enemyAvail[slot]==2&&global_cash25_body_shape(slot)&&global_cash25_body_records_match()&&
  global_cash25_body_slots[slot].record==global_cash25_body_record_stamp_for((unsigned)global_cash25_body_slots[slot].profile)&&
  e->evalue==global_cash25_body_slots[slot].value&&
  (int)e->ex+(int)tempMapXOfs>-29&&(int)e->ex+(int)tempMapXOfs<300&&
  e->enemycycle>=1&&e->enemycycle<=global_cash25_body_animation_length((unsigned)global_cash25_body_slots[slot].profile)&&e->enemycycle==global_cash25_body_slots[slot].next_phase;
 if(!good){global_cash25_body_slots[slot].role=false;return;}
 global_cash25_body_slots[slot].animation_tick=mirror_logic_tick;
 global_cash25_body_slots[slot].observed_phase=e->enemycycle;
 global_cash25_body_slots[slot].next_phase=e->enemycycle==global_cash25_body_animation_length((unsigned)global_cash25_body_slots[slot].profile)?1:e->enemycycle+1;
}
/* Call once on every attempted native body draw, before resource gating. The
 * matching animation witness is mandatory, including the first visible draw. */
static bool global_cash25_body_identity(int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *context)
{
 if(!context||context->pool_slot>=COUNTOF(global_cash25_body_slots))return false;
 unsigned slot=context->pool_slot;const struct JE_SingleEnemyType *e=enemy+slot;
 bool good=global_cash25_body_slots[slot].role&&
  global_cash25_body_slots[slot].witnessed==global_cash25_body_slots[slot].generation&&
  global_cash25_body_slots[slot].last_tick!=mirror_logic_tick&&global_cash25_body_records_match()&&
  global_cash25_body_slots[slot].record==global_cash25_body_record_stamp_for((unsigned)global_cash25_body_slots[slot].profile)&&
  enemyAvail[slot]==2&&global_cash25_body_shape(slot)&&e->evalue==global_cash25_body_slots[slot].value&&
  global_cash25_body_profile(context->type)==global_cash25_body_slots[slot].profile&&context->availability==2&&context->size==0&&context->score_item&&!context->damaged&&
  !part&&!filter&&bank.data==spriteSheet11.data&&bank.size==spriteSheet11.size&&
  e->enemycycle>=1&&e->enemycycle<=global_cash25_body_animation_length((unsigned)global_cash25_body_slots[slot].profile)&&
  global_cash25_body_slots[slot].animation_tick==mirror_logic_tick&&e->enemycycle==global_cash25_body_slots[slot].observed_phase&&
  e->ey>-13&&base==e->egr[e->enemycycle-1]&&base>=global_cash25_body_first_index((unsigned)global_cash25_body_slots[slot].profile)&&base<global_cash25_body_first_index((unsigned)global_cash25_body_slots[slot].profile)+global_cash25_body_frame_count((unsigned)global_cash25_body_slots[slot].profile)&&
  x==(int)e->ex+(int)tempMapXOfs&&y==(int)e->ey;
 if(!good){global_cash25_body_slots[slot].role=false;return false;}
 global_cash25_body_slots[slot].last_tick=mirror_logic_tick;
 return true;
}
