/* SPDX-License-Identifier: GPL-2.0-or-later
 * Isolated native Cash25 identity proof, not an engine/gameplay test.
 * Original record is supplied on stdin and never saved. Types are extracted
 * unchanged from current production headers by the Python driver. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
typedef uint8_t Uint8;
typedef uint8_t JE_byte;
typedef int8_t JE_shortint;
typedef int16_t JE_integer;
typedef uint16_t JE_word;
typedef bool JE_boolean;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
#define ENEMY_NUM 1850
#define COUNTOF(a) (sizeof(a)/sizeof((a)[0]))
#include "cash25_identity_types.h"
#include "../src/global_asset_registry.h"
static JE_EnemyDatType enemyDat;
static JE_MultiEnemyType enemy;
static Uint8 enemyAvail[100];
static Uint8 bankbytes[10];
static Sprite2_array spriteSheet11={sizeof(bankbytes),bankbytes};
static JE_word tempMapXOfs;
static uint64_t mirror_logic_tick;
static uint64_t global_bytes_hash(const void *v,size_t n)
{const Uint8 *b=v;uint64_t h=UINT64_C(0xcbf29ce484222325);for(size_t i=0;i<n;i++){h^=b[i];h*=UINT64_C(0x100000001b3);}return h;}
#include "../src/global_cash25_identity.inc"
static unsigned checks;
#define CHECK(x) do {assert(x);checks++;} while(0)
static Uint8 original[77], originals[5][77];
static unsigned current_record=391;
static unsigned first_index(void){return global_cash25_body_first_index(current_record-391);}
static int nominal_value(void){return enemyDat[current_record].value;}
static void record_load(const Uint8 *b)
{
 size_t n=0;
#define RBYTE(v) do {(v)=b[n++];} while(0)
#define RWORD(v) do {(v)=(unsigned)b[n]|((unsigned)b[n+1]<<8);n+=2;} while(0)
 RBYTE(enemyDat[current_record].ani);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[current_record].tur[i]);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[current_record].freq[i]);
 RBYTE(enemyDat[current_record].xmove);RBYTE(enemyDat[current_record].ymove);RBYTE(enemyDat[current_record].xaccel);RBYTE(enemyDat[current_record].yaccel);
 RBYTE(enemyDat[current_record].xcaccel);RBYTE(enemyDat[current_record].ycaccel);RWORD(enemyDat[current_record].startx);RWORD(enemyDat[current_record].starty);
 RBYTE(enemyDat[current_record].startxc);RBYTE(enemyDat[current_record].startyc);RBYTE(enemyDat[current_record].armor);RBYTE(enemyDat[current_record].esize);
 for(unsigned i=0;i<20;i++)RWORD(enemyDat[current_record].egraphic[i]);
 RBYTE(enemyDat[current_record].explosiontype);RBYTE(enemyDat[current_record].animate);RBYTE(enemyDat[current_record].shapebank);
 RBYTE(enemyDat[current_record].xrev);RBYTE(enemyDat[current_record].yrev);RWORD(enemyDat[current_record].dgr);RBYTE(enemyDat[current_record].dlevel);
 RBYTE(enemyDat[current_record].dani);RBYTE(enemyDat[current_record].elaunchfreq);RWORD(enemyDat[current_record].elaunchtype);
 RWORD(enemyDat[current_record].value);RWORD(enemyDat[current_record].eenemydie);
#undef RBYTE
#undef RWORD
 CHECK(n==77);
}
static G101EnemyContext context(unsigned slot)
{
 return (G101EnemyContext){current_record,slot,enemyAvail[slot],enemy[slot].size,enemy[slot].scoreitem,enemy[slot].edamaged,true,false};
}
static void fields(unsigned slot)
{
 struct JE_SingleEnemyType *e=enemy+slot;memset(e,0,sizeof(*e));
 e->enemytype=current_record;e->enemydatofs=&enemyDat[current_record];e->sprite2s=&spriteSheet11;e->scoreitem=true;
 e->armorleft=255;e->ani=enemyDat[current_record].ani;e->animin=1;e->aniactive=1;e->evalue=nominal_value();
 memcpy(e->egr,enemyDat[current_record].egraphic,sizeof(e->egr));e->ex=100;e->ey=100;
}
static void birth(unsigned slot)
{
 enemyAvail[slot]=1;render_mirror_cash25_enemy_allocated(enemy+slot,current_record,0);fields(slot);
 render_mirror_cash25_enemy_initialized(enemy+slot,current_record,2);enemyAvail[slot]=2;
 CHECK(global_cash25_body_slots[slot].role);
}
static bool draw(unsigned slot,unsigned phase)
{
 enemy[slot].enemycycle=phase;render_mirror_cash25_enemy_animated(slot);G101EnemyContext c=context(slot);
 return global_cash25_body_identity(enemy[slot].ex+tempMapXOfs,enemy[slot].ey,spriteSheet11,enemyDat[current_record].egraphic[phase-1],0,0,&c);
}
static void run_profile(void)
{
 memcpy(original,originals[current_record-391],77);record_load(original);CHECK(global_cash25_body_records_match());
 CHECK(global_cash25_body_record_stamp_for(current_record-391)==global_bytes_hash(original,77));
 for(unsigned p=0;p<77;p++){Uint8 m[77];memcpy(m,original,77);m[p]^=1;record_load(m);CHECK(!global_cash25_body_records_match());}
 record_load(original);global_cash25_body_identity_reset();fields(0);enemyAvail[0]=2;CHECK(!draw(0,1));
 for(unsigned slot=0;slot<100;slot++){
  ++mirror_logic_tick;birth(slot);
  for(unsigned n=0;n<3*enemyDat[current_record].ani;n++){mirror_logic_tick+=n%3+1;enemy[slot].ex-=1;enemy[slot].ey+=1;tempMapXOfs=n;CHECK(draw(slot,n%enemyDat[current_record].ani+1));}
 }
 birth(0);++mirror_logic_tick;CHECK(draw(0,1));CHECK(!draw(0,1));++mirror_logic_tick;CHECK(!draw(0,2));
 birth(0);++mirror_logic_tick;CHECK(!draw(0,2));++mirror_logic_tick;CHECK(!draw(0,1));
 birth(0);enemy[0].filter=0x20;global_cash25_body_identity_frame_begin();enemy[0].filter=0;CHECK(!draw(0,1));
 birth(0);enemyAvail[0]=1;global_cash25_body_identity_frame_begin();enemyAvail[0]=2;CHECK(!draw(0,1));
 birth(0);enemy[0].evalue=nominal_value()+1;CHECK(!draw(0,1));enemy[0].evalue=nominal_value();CHECK(!draw(0,1));
 birth(0);++mirror_logic_tick;CHECK(draw(0,1));enemyAvail[0]=1;CHECK(global_cash25_body_records_match());birth(0);++mirror_logic_tick;CHECK(draw(0,1));
 for(unsigned i=0;i<20;i++){birth(0);enemy[0].egr[i]^=1;CHECK(!draw(0,1));}
 birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);G101EnemyContext c=context(0);
 CHECK(!global_cash25_body_identity(enemy[0].ex+tempMapXOfs+1,enemy[0].ey,spriteSheet11,first_index(),0,0,&c));
 birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);c=context(0);c.type=current_record==391?392:391;CHECK(!global_cash25_body_identity(enemy[0].ex+tempMapXOfs,enemy[0].ey,spriteSheet11,first_index(),0,0,&c));
 birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);c=context(0);c.pool_slot=100;CHECK(!global_cash25_body_identity(0,0,spriteSheet11,first_index(),0,0,&c));
 CHECK(global_cash25_body_slot(NULL)<0);CHECK(global_cash25_body_slot((Uint8*)enemy+1)<0);CHECK(global_cash25_body_slot(enemy+100)<0);
 birth(0);render_mirror_cash25_enemy_initialized(enemy,current_record,2);CHECK(!global_cash25_body_slots[0].role);
 for(int unique=-2;unique<=22;unique++){
  enemyAvail[0]=1;render_mirror_cash25_enemy_allocated(enemy,current_record,unique);fields(0);render_mirror_cash25_enemy_initialized(enemy,current_record,2);enemyAvail[0]=2;
  CHECK(global_cash25_body_slots[0].role==(unique<=0||unique==21));
 }
 enemyAvail[0]=1;render_mirror_cash25_enemy_allocated(enemy,current_record==391?392:391,0);fields(0);render_mirror_cash25_enemy_initialized(enemy,current_record,2);CHECK(!global_cash25_body_slots[0].role);
 enemyAvail[0]=2;render_mirror_cash25_enemy_allocated(enemy,current_record,0);fields(0);render_mirror_cash25_enemy_initialized(enemy,current_record,2);CHECK(!global_cash25_body_slots[0].role);
 birth(0);Uint8 bad[77];memcpy(bad,original,77);bad[21]^=1;record_load(bad);global_cash25_body_identity_frame_begin();record_load(original);CHECK(!draw(0,1));
 for(unsigned variant=0;variant<9;variant++){
  birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);c=context(0);
  int part=0,filter=0,x=enemy[0].ex+tempMapXOfs,y=enemy[0].ey;unsigned base=first_index();Sprite2_array bank=spriteSheet11;
  if(variant==0)c.size=1;if(variant==1)c.availability=0;if(variant==2)c.score_item=false;if(variant==3)c.damaged=true;
  if(variant==4)part=1;if(variant==5)filter=1;if(variant==6)bank.size--;if(variant==7)base=first_index()+1;if(variant==8)y++;
  CHECK(!global_cash25_body_identity(x,y,bank,base,part,filter,&c));
 }
 /* Legitimate spawn above the viewport advances before its first visible draw. */
 birth(0);enemy[0].ey=-28;
 for(unsigned phase=1;phase<=4;phase++){++mirror_logic_tick;enemy[0].enemycycle=phase;render_mirror_cash25_enemy_animated(0);CHECK(global_cash25_body_slots[0].role);}
 ++mirror_logic_tick;enemy[0].ey=0;CHECK(draw(0,5));
 for(unsigned phase=6;phase<=enemyDat[current_record].ani;phase++){++mirror_logic_tick;CHECK(draw(0,phase));}
 ++mirror_logic_tick;CHECK(draw(0,1));
 /* A same-tick unmatched or repeated animation witness cannot mint a draw. */
 birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;c=context(0);
 CHECK(!global_cash25_body_identity(enemy[0].ex+tempMapXOfs,enemy[0].ey,spriteSheet11,first_index(),0,0,&c));
 birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);render_mirror_cash25_enemy_animated(0);CHECK(!global_cash25_body_slots[0].role);
 birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);++mirror_logic_tick;c=context(0);
 CHECK(!global_cash25_body_identity(enemy[0].ex+tempMapXOfs,enemy[0].ey,spriteSheet11,first_index(),0,0,&c));
 /* Same source sprite at repeated/reverse positions is not a phase witness. */
 if(current_record>=394){
  birth(0);++mirror_logic_tick;CHECK(draw(0,1));
  ++mirror_logic_tick;CHECK(!draw(0,3)); /* Must observe second repeated step. */
  birth(0);for(unsigned phase=1;phase<=16;phase++){++mirror_logic_tick;CHECK(draw(0,phase));}
  ++mirror_logic_tick;enemy[0].enemycycle=17;render_mirror_cash25_enemy_animated(0);CHECK(!global_cash25_body_slots[0].role);
  birth(0);for(unsigned phase=1;phase<=9;phase++){++mirror_logic_tick;CHECK(draw(0,phase));}
  ++mirror_logic_tick;enemy[0].enemycycle=9;render_mirror_cash25_enemy_animated(0);CHECK(!global_cash25_body_slots[0].role);
  birth(0);++mirror_logic_tick;enemy[0].enemycycle=1;render_mirror_cash25_enemy_animated(0);c=context(0);c.type=509;
  CHECK(!global_cash25_body_identity(enemy[0].ex+tempMapXOfs,enemy[0].ey,spriteSheet11,first_index(),0,0,&c));
 }
 birth(0);global_cash25_body_identity_reset();CHECK(!draw(0,1));
 }
int main(void)
{
 CHECK(fread(originals,1,sizeof(originals),stdin)==sizeof(originals));
 for(current_record=391;current_record<=395;current_record++)record_load(originals[current_record-391]);
 for(current_record=391;current_record<=395;current_record++)run_profile();
 /* Cross-profile slot reuse needs a fresh birth, not a same-sprite alias. */
 current_record=391;birth(0);++mirror_logic_tick;CHECK(draw(0,1));
 current_record=392;fields(0);++mirror_logic_tick;CHECK(!draw(0,1));
 birth(0);++mirror_logic_tick;CHECK(draw(0,1));
 current_record=393;fields(0);++mirror_logic_tick;CHECK(!draw(0,1));
 birth(0);++mirror_logic_tick;CHECK(draw(0,1));
 CHECK(global_cash25_body_profile(390)<0);CHECK(global_cash25_body_profile(396)<0);CHECK(global_cash25_body_profile(509)<0);
 CHECK(global_cash25_body_record_stamp_for(5)==0);CHECK(!global_cash25_body_record_matches(5));
 /* Unsupported record509 cannot acquire a body role even with gem fields. */
 current_record=394;fields(0);enemyAvail[0]=1;render_mirror_cash25_enemy_allocated(enemy,509,0);
 render_mirror_cash25_enemy_initialized(enemy,509,2);CHECK(!global_cash25_body_slots[0].role);
 CHECK(global_cash25_body_record_stamp()==global_bytes_hash(originals[0],77));
 printf("Cash25/50/75 and Gem100/250 identity checks: %u\n",checks);return 0;
}
