/* SPDX-License-Identifier: GPL-2.0-or-later
 * Isolated native Rotor identity proof, not an engine/gameplay test.
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
#include "rotor_identity_types.h"
#include "../src/global_asset_registry.h"
static JE_EnemyDatType enemyDat;
static JE_MultiEnemyType enemy;
static Uint8 enemyAvail[100];
static Uint8 bankbytes[10];
static Sprite2_array enemySpriteSheets[4]={{sizeof(bankbytes),bankbytes}};
static Uint8 enemySpriteSheetIds[4]={1,0,0,0};
static JE_word tempMapXOfs;
static uint64_t mirror_logic_tick;
static uint64_t global_bytes_hash(const void *v,size_t n)
{const Uint8 *b=v;uint64_t h=UINT64_C(0xcbf29ce484222325);for(size_t i=0;i<n;i++){h^=b[i];h*=UINT64_C(0x100000001b3);}return h;}
#include "../src/global_rotor_identity.inc"
static unsigned checks;
#define CHECK(x) do {assert(x);checks++;} while(0)
static Uint8 original[77], originals[2][77];
static unsigned current_record=5;
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
{return (G101EnemyContext){current_record,slot,enemyAvail[slot],1,false,false,true,false};}
static void fields(unsigned slot)
{
 struct JE_SingleEnemyType *e=enemy+slot;memset(e,0,sizeof(*e));
 e->enemytype=current_record;e->enemydatofs=&enemyDat[current_record];e->sprite2s=&enemySpriteSheets[0];e->size=1;
 e->armorleft=6;e->ani=8;e->animin=1;e->aniactive=1;e->evalue=nominal_value();
 memcpy(e->egr,enemyDat[current_record].egraphic,sizeof(e->egr));e->ex=100;e->ey=100;
}
static void birth(unsigned slot)
{
 enemyAvail[slot]=1;render_mirror_rotor_enemy_allocated(enemy+slot,current_record,0);fields(slot);
 render_mirror_rotor_enemy_initialized(enemy+slot,current_record,0);enemyAvail[slot]=0;CHECK(global_rotor_body_slots[slot].role);
}
static bool part(unsigned slot,int q)
{
 int offsets[4]={0,1,19,20};G101EnemyContext c=context(slot);struct JE_SingleEnemyType *e=enemy+slot;
 return global_rotor_body_identity(e->ex+tempMapXOfs+(q&1?6:-6),e->ey+(q>=2?7:-7),enemySpriteSheets[0],e->egr[e->enemycycle-1],offsets[q],e->filter,&c);
}
static void phase(unsigned slot,unsigned p)
{mirror_logic_tick++;enemy[slot].enemycycle=p;render_mirror_rotor_enemy_animated(slot);}
static void profile(void)
{
 global_rotor_body_identity_reset();birth(0);
 for(unsigned turn=0;turn<3;turn++)for(unsigned p=1;p<=8;p++){
  enemy[0].filter=(turn*79+p)&255;enemy[0].armorleft=1;phase(0,p);
  for(int q=0;q<4;q++)CHECK(part(0,q));CHECK(global_rotor_body_identity_complete());
 }
 /* Exact partial visibility branches: upper row omitted, lower row omitted, all omitted. */
 for(int y=-30;y<=190;y++){
  birth(0);enemy[0].ey=y;phase(0,1);
  if(y>-13){CHECK(part(0,0));CHECK(part(0,1));}
  if(y>-26&&y<182){CHECK(part(0,2));CHECK(part(0,3));}
  CHECK(global_rotor_body_identity_complete());
 }
 /* Duplicate/out-of-order, truncated quartet and restored identity never revive. */
 birth(0);phase(0,1);CHECK(!part(0,1));CHECK(!part(0,0));
 birth(0);phase(0,1);CHECK(part(0,0));CHECK(!part(0,0));
 birth(0);phase(0,1);CHECK(part(0,0));CHECK(!global_rotor_body_identity_complete());CHECK(!part(0,1));
 birth(0);phase(0,1);CHECK(part(0,0));phase(0,2);CHECK(!global_rotor_body_slots[0].role);
 birth(0);phase(0,1);CHECK(part(0,0));global_rotor_body_identity_frame_begin();CHECK(!global_rotor_body_slots[0].role);
 /* Each full serialized byte matters, even after restoration. */
 unsigned profile=current_record==5?0:1;memcpy(original,originals[profile],77);
 for(unsigned i=0;i<77;i++){
  birth(0);Uint8 altered[77];memcpy(altered,original,77);altered[i]^=1;record_load(altered);
  CHECK(!global_rotor_body_record_matches(profile));global_rotor_body_identity_frame_begin();record_load(original);
  CHECK(!global_rotor_body_slots[0].role);
 }
 birth(0);enemySpriteSheetIds[1]=1;CHECK(!global_rotor_bank().data);global_rotor_body_identity_frame_begin();enemySpriteSheetIds[1]=0;CHECK(!global_rotor_body_slots[0].role);
 birth(0);enemySpriteSheetIds[0]=2;phase(0,1);CHECK(!global_rotor_body_slots[0].role);enemySpriteSheetIds[0]=1;
 birth(0);phase(0,1);enemy[0].ex++;CHECK(!part(0,0));
 birth(0);phase(0,1);enemy[0].filter++;CHECK(!part(0,0));
 birth(0);phase(0,1);enemy[0].evalue++;CHECK(!part(0,0));
 birth(0);phase(0,1);enemy[0].edamaged=true;CHECK(!part(0,0));
 birth(0);phase(0,2);CHECK(!global_rotor_body_slots[0].role);
 /* Hidden vertical entries retain observed animation rather than restart. */
 birth(0);enemy[0].ey=-30;
 for(unsigned p=1;p<=4;p++)phase(0,p);
 enemy[0].ey=20;phase(0,5);for(int q=0;q<4;q++)CHECK(part(0,q));
 /* Pool reuse retires a previous same-source role. */
 enemyAvail[0]=1;render_mirror_rotor_enemy_allocated(enemy,4,0);CHECK(!global_rotor_body_slots[0].role);
}
int main(void)
{
 CHECK(fread(originals,77,2,stdin)==2);
 current_record=5;record_load(originals[0]);current_record=11;record_load(originals[1]);
 CHECK(global_rotor_body_records_match());
 current_record=5;profile();current_record=11;profile();
 printf("PASS rotor identity %u checks\n",checks);return 0;
}
