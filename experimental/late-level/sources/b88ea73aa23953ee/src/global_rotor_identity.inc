/* SPDX-License-Identifier: GPL-2.0-or-later
 * Native rotor records 5/11: independent lifetime, animation and ordered quartet proof. */
static struct {
 uint64_t generation,witnessed,born_tick,animation_tick,record;
 bool pending,role; unsigned next_phase,observed_phase,remaining;
 int value,profile,origin_x,origin_y,filter;
} global_rotor_body_slots[100];
static int global_rotor_body_profile(unsigned record){return record==5?0:record==11?1:-1;}
/* Require one actually loaded NEWSH2 bank, never a stale pointer inherited when
 * JE_makeEnemy could not find a requested shape table. */
static Sprite2_array global_rotor_bank(void)
{
 Sprite2_array result={0};unsigned count=0;
 for(unsigned i=0;i<COUNTOF(enemySpriteSheetIds);i++)if(enemySpriteSheetIds[i]==1){result=enemySpriteSheets[i];count++;}
 if(count!=1||!result.data||!result.size)return (Sprite2_array){0};
 return result;
}
/* Canonical on-disk order, not compiler struct padding. */
static uint64_t global_rotor_body_record_stamp_for(unsigned profile)
{
 if(profile>=2)return 0;
 unsigned record=profile==0?5:11;
 Uint8 bytes[77];size_t n=0;
#define ROTOR_BYTE(v) do {bytes[n++]=(Uint8)(v);} while(0)
#define ROTOR_WORD(v) do {unsigned cv_=(unsigned)(v);ROTOR_BYTE(cv_);ROTOR_BYTE(cv_>>8);} while(0)
 ROTOR_BYTE(enemyDat[record].ani);
 for(unsigned i=0;i<3;i++)ROTOR_BYTE(enemyDat[record].tur[i]);
 for(unsigned i=0;i<3;i++)ROTOR_BYTE(enemyDat[record].freq[i]);
 ROTOR_BYTE(enemyDat[record].xmove);ROTOR_BYTE(enemyDat[record].ymove);
 ROTOR_BYTE(enemyDat[record].xaccel);ROTOR_BYTE(enemyDat[record].yaccel);
 ROTOR_BYTE(enemyDat[record].xcaccel);ROTOR_BYTE(enemyDat[record].ycaccel);
 ROTOR_WORD(enemyDat[record].startx);ROTOR_WORD(enemyDat[record].starty);
 ROTOR_BYTE(enemyDat[record].startxc);ROTOR_BYTE(enemyDat[record].startyc);
 ROTOR_BYTE(enemyDat[record].armor);ROTOR_BYTE(enemyDat[record].esize);
 for(unsigned i=0;i<20;i++)ROTOR_WORD(enemyDat[record].egraphic[i]);
 ROTOR_BYTE(enemyDat[record].explosiontype);ROTOR_BYTE(enemyDat[record].animate);ROTOR_BYTE(enemyDat[record].shapebank);
 ROTOR_BYTE(enemyDat[record].xrev);ROTOR_BYTE(enemyDat[record].yrev);ROTOR_WORD(enemyDat[record].dgr);
 ROTOR_BYTE(enemyDat[record].dlevel);ROTOR_BYTE(enemyDat[record].dani);ROTOR_BYTE(enemyDat[record].elaunchfreq);
 ROTOR_WORD(enemyDat[record].elaunchtype);ROTOR_WORD(enemyDat[record].value);ROTOR_WORD(enemyDat[record].eenemydie);
#undef ROTOR_BYTE
#undef ROTOR_WORD
 return n==77?global_bytes_hash(bytes,n):0;
}
static bool global_rotor_body_record_matches(unsigned profile)
{
 if(profile>=2)return false;
 uint64_t h=global_rotor_body_record_stamp_for(profile);
 const uint64_t *pins=profile?global_rotor_record11_fnv:global_rotor_record5_fnv;
 unsigned count=profile?COUNTOF(global_rotor_record11_fnv):COUNTOF(global_rotor_record5_fnv);
 for(unsigned i=0;i<count;i++)if(h==pins[i])return true;
 return false;
}
static bool global_rotor_body_records_match(void)
{return global_rotor_body_record_matches(0)&&global_rotor_body_record_matches(1);}
static int global_rotor_body_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
static bool global_rotor_body_shape(unsigned slot)
{
 const struct JE_SingleEnemyType *e=enemy+slot;
 int profile=global_rotor_body_slots[slot].profile;if(profile<0||profile>=2)return false;
 unsigned record=profile?11:5;Sprite2_array bank=global_rotor_bank();bool exact=false;
 for(unsigned i=0;i<COUNTOF(enemySpriteSheetIds);i++)if(enemySpriteSheetIds[i]==1&&e->sprite2s==&enemySpriteSheets[i])exact=true;
 if(!exact||!bank.data||e->enemytype!=record||e->enemydatofs!=&enemyDat[record]||
    e->size!=1||e->scoreitem||e->edamaged||e->ani!=8||e->animin!=1||e->aniactive!=1||e->animax||e->aniwhenfire||
    e->edani!=enemyDat[record].dani||e->edgr!=enemyDat[record].dgr||e->edlevel!=enemyDat[record].dlevel)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=enemyDat[record].egraphic[i])return false;
 return true;
}
static void global_rotor_body_identity_reset(void){memset(global_rotor_body_slots,0,sizeof(global_rotor_body_slots));}
static void global_rotor_body_identity_frame_begin(void)
{
 bool records=global_rotor_body_records_match();
 for(unsigned i=0;i<COUNTOF(global_rotor_body_slots);i++)if(global_rotor_body_slots[i].role&&
  (global_rotor_body_slots[i].remaining||!records||enemyAvail[i]!=0||!global_rotor_body_shape(i)||enemy[i].evalue!=global_rotor_body_slots[i].value))global_rotor_body_slots[i].role=false;
}
void render_mirror_rotor_enemy_allocated(void *ptr,unsigned record,int unique_shape)
{
 int slot=global_rotor_body_slot(ptr);if(slot<0)return;
 if(++global_rotor_body_slots[slot].generation==0)++global_rotor_body_slots[slot].generation;
 global_rotor_body_slots[slot].role=false;global_rotor_body_slots[slot].remaining=0;
 global_rotor_body_slots[slot].profile=global_rotor_body_profile(record);
 global_rotor_body_slots[slot].pending=enemyAvail[slot]==1&&global_rotor_body_slots[slot].profile>=0&&
  (unique_shape<=0||unique_shape==1)&&global_rotor_body_records_match()&&global_rotor_bank().data;
 global_rotor_body_slots[slot].born_tick=mirror_logic_tick;
 global_rotor_body_slots[slot].record=global_rotor_body_record_stamp_for((unsigned)global_rotor_body_slots[slot].profile);
}
void render_mirror_rotor_enemy_initialized(void *ptr,unsigned record,unsigned avail)
{
 int slot=global_rotor_body_slot(ptr);if(slot<0)return;
 bool fresh=global_rotor_body_slots[slot].pending&&global_rotor_body_slots[slot].born_tick==mirror_logic_tick;
 global_rotor_body_slots[slot].pending=false;
 bool good=fresh&&global_rotor_body_profile(record)==global_rotor_body_slots[slot].profile&&avail==0&&enemyAvail[slot]==1&&global_rotor_body_records_match()&&
  global_rotor_body_slots[slot].record==global_rotor_body_record_stamp_for((unsigned)global_rotor_body_slots[slot].profile)&&global_rotor_body_shape(slot)&&enemy[slot].enemycycle==0;
 global_rotor_body_slots[slot].role=good;global_rotor_body_slots[slot].next_phase=good?1:0;
 global_rotor_body_slots[slot].witnessed=global_rotor_body_slots[slot].generation;
 global_rotor_body_slots[slot].animation_tick=UINT64_MAX;global_rotor_body_slots[slot].observed_phase=0;
 global_rotor_body_slots[slot].value=enemy[slot].evalue;
}
/* Observe the original animation block before vertical visibility tests. */
void render_mirror_rotor_enemy_animated(unsigned slot)
{
 if(slot>=COUNTOF(global_rotor_body_slots))return;
 const struct JE_SingleEnemyType *e=enemy+slot;
 bool good=global_rotor_body_slots[slot].role&&!global_rotor_body_slots[slot].remaining&&global_rotor_body_slots[slot].witnessed==global_rotor_body_slots[slot].generation&&
  global_rotor_body_slots[slot].animation_tick!=mirror_logic_tick&&enemyAvail[slot]==0&&global_rotor_body_shape(slot)&&global_rotor_body_records_match()&&
  global_rotor_body_slots[slot].record==global_rotor_body_record_stamp_for((unsigned)global_rotor_body_slots[slot].profile)&&e->evalue==global_rotor_body_slots[slot].value&&
  (int)e->ex+(int)tempMapXOfs>-29&&(int)e->ex+(int)tempMapXOfs<300&&e->enemycycle>=1&&e->enemycycle<=8&&e->enemycycle==global_rotor_body_slots[slot].next_phase;
 if(!good){global_rotor_body_slots[slot].role=false;return;}
 global_rotor_body_slots[slot].animation_tick=mirror_logic_tick;global_rotor_body_slots[slot].observed_phase=e->enemycycle;
 global_rotor_body_slots[slot].next_phase=e->enemycycle==8?1:e->enemycycle+1;
 global_rotor_body_slots[slot].remaining=(e->ey>-13?3:0)|(e->ey>-26&&e->ey<182?12:0);
 global_rotor_body_slots[slot].origin_x=(int)e->ex+(int)tempMapXOfs;global_rotor_body_slots[slot].origin_y=e->ey;
 global_rotor_body_slots[slot].filter=e->filter;
}
static bool global_rotor_body_identity(int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *context)
{
 if(!context||context->pool_slot>=COUNTOF(global_rotor_body_slots))return false;
 unsigned slot=context->pool_slot;const struct JE_SingleEnemyType *e=enemy+slot;Sprite2_array source=global_rotor_bank();
 unsigned q=part==0?0:part==1?1:part==19?2:part==20?3:4;
 unsigned bit=q<4?1u<<q:0,remaining=global_rotor_body_slots[slot].remaining;
 bool good=global_rotor_body_slots[slot].role&&global_rotor_body_slots[slot].witnessed==global_rotor_body_slots[slot].generation&&
  global_rotor_body_records_match()&&global_rotor_body_slots[slot].record==global_rotor_body_record_stamp_for((unsigned)global_rotor_body_slots[slot].profile)&&
  enemyAvail[slot]==0&&global_rotor_body_shape(slot)&&e->evalue==global_rotor_body_slots[slot].value&&
  global_rotor_body_profile(context->type)==global_rotor_body_slots[slot].profile&&context->availability==0&&context->size==1&&!context->score_item&&!context->damaged&&
  q<4&&bit==(remaining&(~remaining+1u))&&filter==e->filter&&filter==global_rotor_body_slots[slot].filter&&filter>=0&&filter<=255&&
  bank.data==source.data&&bank.size==source.size&&source.data&&
  global_rotor_body_slots[slot].animation_tick==mirror_logic_tick&&e->enemycycle==global_rotor_body_slots[slot].observed_phase&&
  e->enemycycle>=1&&e->enemycycle<=8&&base==e->egr[e->enemycycle-1]&&base>=229&&base<=243&&(base&1)&&
  (int)e->ex+(int)tempMapXOfs==global_rotor_body_slots[slot].origin_x&&(int)e->ey==global_rotor_body_slots[slot].origin_y&&
  x==global_rotor_body_slots[slot].origin_x+(q&1?6:-6)&&y==global_rotor_body_slots[slot].origin_y+(q>=2?7:-7);
 if(!good){global_rotor_body_slots[slot].role=false;return false;}
 global_rotor_body_slots[slot].remaining&=~bit;return true;
}
/* Finish cannot retain a prefix of an interrupted native quartet. */
static bool global_rotor_body_identity_complete(void)
{
 bool complete=true;
 for(unsigned i=0;i<COUNTOF(global_rotor_body_slots);i++)if(global_rotor_body_slots[i].role&&global_rotor_body_slots[i].remaining){global_rotor_body_slots[i].role=false;complete=false;}
 return complete;
}
