/* SPDX-License-Identifier: GPL-2.0-or-later
 * Finite display-only enemy projectile provenance. No simulation state writes.
 * Native E1 ASTEROID2 record550/weapon76 and DELIANI record240/weapon143, plus E2 GYGES record379/weapon153.
 * Allocation generations and a single-use draw witness prohibit slot borrowing.
 */
#include "enemy_reuse_identity.h"
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
#include "episodes.h"
#include "varz.h"
#include "game_probe.h"
#include "xmas.h"
#include <stdint.h>
#include <string.h>
static uint64_t allocation_serial;
static struct { uint64_t generation; unsigned record; const Sprite2_array *bank; const Uint8 *bank_data; size_t bank_size; bool pending,valid; } actors[100];
static struct { uint64_t generation,actor_generation; unsigned actor,weapon,phase,frame,native_phase; bool valid; } shots[ENEMY_SHOT_MAX];
/* One transition at a time, produced only around the original animation update.
 * Per-shot native_phase persists across pauses or draws declined by the mirror;
 * an unused transition is superseded by the next native update, never replayed. */
static struct { bool pending,complete; unsigned slot; uint64_t generation; EnemyShotType before; } transition;
static struct { bool valid; unsigned slot; uint64_t generation; EnemyShotType shot; } witness;
static uint64_t stamp(const unsigned char *b,unsigned n)
{uint64_t v=UINT64_C(0xcbf29ce484222325);for(unsigned i=0;i<n;i++){v^=b[i];v*=UINT64_C(0x100000001b3);}return v;}
static uint64_t weapons_stamp(unsigned id)
{
 unsigned char b[80];unsigned n=0;
#define B(v) do { b[n++]=(unsigned char)(v); } while(0)
#define W(v) do { unsigned w=(unsigned)(v);B(w);B(w>>8); } while(0)
 W(weapons[id].drain);
 B(weapons[id].shotrepeat);
 B(weapons[id].multi);
 W(weapons[id].weapani);
 B(weapons[id].max);
 B(weapons[id].tx);
 B(weapons[id].ty);
 B(weapons[id].aim);
 for(unsigned i=0;i<8;i++)B(weapons[id].attack[i]);
 for(unsigned i=0;i<8;i++)B(weapons[id].del[i]);
 for(unsigned i=0;i<8;i++)B(weapons[id].sx[i]);
 for(unsigned i=0;i<8;i++)B(weapons[id].sy[i]);
 for(unsigned i=0;i<8;i++)B(weapons[id].bx[i]);
 for(unsigned i=0;i<8;i++)B(weapons[id].by[i]);
 for(unsigned i=0;i<8;i++)W(weapons[id].sg[i]);
 B(weapons[id].acceleration);
 B(weapons[id].accelerationx);
 B(weapons[id].circlesize);
 B(weapons[id].sound);
 B(weapons[id].trail);
 B(weapons[id].shipblastfilter);

#undef B
#undef W
 return n==sizeof(b)?stamp(b,n):0;
}
static uint64_t enemyDat_stamp(unsigned id)
{
 unsigned char b[77];unsigned n=0;
#define B(v) do { b[n++]=(unsigned char)(v); } while(0)
#define W(v) do { unsigned w=(unsigned)(v);B(w);B(w>>8); } while(0)
 B(enemyDat[id].ani);
 for(unsigned i=0;i<3;i++)B(enemyDat[id].tur[i]);
 for(unsigned i=0;i<3;i++)B(enemyDat[id].freq[i]);
 B(enemyDat[id].xmove);
 B(enemyDat[id].ymove);
 B(enemyDat[id].xaccel);
 B(enemyDat[id].yaccel);
 B(enemyDat[id].xcaccel);
 B(enemyDat[id].ycaccel);
 W(enemyDat[id].startx);
 W(enemyDat[id].starty);
 B(enemyDat[id].startxc);
 B(enemyDat[id].startyc);
 B(enemyDat[id].armor);
 B(enemyDat[id].esize);
 for(unsigned i=0;i<20;i++)W(enemyDat[id].egraphic[i]);
 B(enemyDat[id].explosiontype);
 B(enemyDat[id].animate);
 B(enemyDat[id].shapebank);
 B(enemyDat[id].xrev);
 B(enemyDat[id].yrev);
 W(enemyDat[id].dgr);
 B(enemyDat[id].dlevel);
 B(enemyDat[id].dani);
 B(enemyDat[id].elaunchfreq);
 W(enemyDat[id].elaunchtype);
 W(enemyDat[id].value);
 W(enemyDat[id].eenemydie);

#undef B
#undef W
 return n==sizeof(b)?stamp(b,n):0;
}
static bool records(unsigned record,unsigned weapon)
{
 if(record==133&&weapon==141)return enemyDat_stamp(133)==UINT64_C(0x9c877679a5ede691)&&weapons_stamp(141)==UINT64_C(0x11ebca5d1ae1dfeb);
 if(record==129&&weapon==134)return enemyDat_stamp(129)==UINT64_C(0x481af40b89888070)&&weapons_stamp(134)==UINT64_C(0xfdd291f76a044203);
 if(record==550&&weapon==76)return enemyDat_stamp(550)==UINT64_C(0x30aff29d6a15a94a)&&weapons_stamp(76)==UINT64_C(0x9d72508524054476);
 if(record==379&&weapon==153)return enemyDat_stamp(379)==UINT64_C(0xad8714656b44632b)&&weapons_stamp(153)==UINT64_C(0x0e1d756bd4135441);
 if(record==240&&weapon==143)return enemyDat_stamp(240)==UINT64_C(0x92741a0be762219f)&&weapons_stamp(143)==UINT64_C(0x72ba48c78dfc3c53);
 return false;
}
static bool scope(unsigned record)
{return game_probe_enabled&&!xmas&&((episodeNum==1&&((record==550&&lvlFileNum==2)||(record==240&&lvlFileNum==5)))||
 (episodeNum==2&&record==379&&lvlFileNum==2)||(episodeNum==3&&lvlFileNum==1&&(record==133||record==129)));}
/* Native emitter banks: logical23/NEWSHS, logical7/NEWSHC, logical18/NEWSHN. */
static const Sprite2_array *actor_bank(unsigned record)
{
 if(record!=550&&record!=240&&record!=379&&record!=133&&record!=129)return NULL;
 unsigned id=record==550?23:record==379?18:(record==133||record==129)?3:7,count=0;const Sprite2_array *b=NULL;
 for(unsigned i=0;i<COUNTOF(enemySpriteSheetIds);i++)if(enemySpriteSheetIds[i]==id){b=&enemySpriteSheets[i];count++;}
 size_t bytes=record==550?46566:record==379?41201:(record==133||record==129)?44079:40714;
 uint64_t pin=(record==133||record==129)?UINT64_C(0x6da0d6176a1ddaae):record==550?UINT64_C(0xf22ec1295ced5d11):record==379?UINT64_C(0xc0c6df910c61dc88):UINT64_C(0x6e88a36b838be98b);
 return count==1&&b&&b->data&&b->size==bytes&&stamp(b->data,b->size)==pin?b:NULL;
}
static bool actor_bound(unsigned slot)
{
 const Sprite2_array *b=actor_bank(actors[slot].record);
 return b&&b==actors[slot].bank&&b==enemy[slot].sprite2s&&b->data==actors[slot].bank_data&&b->size==actors[slot].bank_size;
}
static bool actor_origin(unsigned slot,unsigned record)
{
 if(enemy[slot].enemytype!=record||enemy[slot].enemydatofs!=&enemyDat[record]||
  enemy[slot].scoreitem||enemy[slot].edamaged||enemy[slot].size!=enemyDat[record].esize)return false;
 for(unsigned i=0;i<20;i++)if(enemy[slot].egr[i]!=enemyDat[record].egraphic[i])return false;
 for(unsigned i=0;i<3;i++)if(enemy[slot].tur[i]!=enemyDat[record].tur[i])return false;
 return true;
}
static int actor_slot(const void *p)
{uintptr_t v=(uintptr_t)p,b=(uintptr_t)enemy;if(v<b||v-b>=sizeof(enemy)||(v-b)%sizeof(enemy[0]))return -1;return (int)((v-b)/sizeof(enemy[0]));}
void enemy_reuse_reset(void)
{memset(actors,0,sizeof(actors));memset(shots,0,sizeof(shots));memset(&witness,0,sizeof(witness));memset(&transition,0,sizeof(transition));}
void enemy_reuse_bank_changed(const void *p)
{
 if(p==&spriteSheet8){enemy_reuse_reset();return;}
 for(unsigned i=0;i<COUNTOF(enemySpriteSheets);i++)if(p==&enemySpriteSheets[i]){enemy_reuse_reset();return;}
}
uint64_t enemy_reuse_identity_generation(unsigned slot)
{
 if(slot>=ENEMY_SHOT_MAX||!shots[slot].valid||enemyShotAvail[slot])return 0;
 unsigned a=shots[slot].actor;
 return a<100&&shots[slot].actor_generation==actors[a].generation&&actor_bound(a)&&scope(actors[a].record)&&
  records(actors[a].record,shots[slot].weapon)?shots[slot].generation:0;
}
void enemy_reuse_actor_allocated(void *p,unsigned record,int unique_shape)
{
 int slot=actor_slot(p);if(slot<0)return;
 /* Any allocation invalidates old children, even if the record is unchanged. */
 for(unsigned i=0;i<ENEMY_SHOT_MAX;i++)if(shots[i].actor==(unsigned)slot)shots[i].valid=false;
 if(++allocation_serial==0)++allocation_serial;
 actors[slot].generation=allocation_serial;
 actors[slot].record=record;actors[slot].valid=false;
 actors[slot].pending=unique_shape<=0&&enemyAvail[slot]==1&&scope(record)&&records(record,record==133?141:record==129?134:record==550?76:record==379?153:143);
 const Sprite2_array *b=actors[slot].pending?actor_bank(record):NULL;
 actors[slot].pending=actors[slot].pending&&b;
 actors[slot].bank=b;actors[slot].bank_data=b?b->data:NULL;actors[slot].bank_size=b?b->size:0;
}
void enemy_reuse_actor_initialized(void *p,unsigned record,unsigned avail)
{
 int slot=actor_slot(p);if(slot<0)return;
 actors[slot].valid=actors[slot].pending&&actors[slot].record==record&&avail==0&&actor_bound(slot)&&
  actor_origin(slot,record)&&scope(record)&&records(record,record==133?141:record==129?134:record==550?76:record==379?153:143);
 actors[slot].pending=false;
}
void enemy_reuse_shot_retire(unsigned slot)
{if(slot<ENEMY_SHOT_MAX){shots[slot].valid=false;if(witness.slot==slot)witness.valid=false;if(transition.slot==slot)transition.pending=transition.complete=false;}}
void enemy_reuse_shot_spawn(unsigned slot,unsigned actor,unsigned weapon,unsigned turret,unsigned phase)
{
 if(slot>=ENEMY_SHOT_MAX)return;
 enemy_reuse_shot_retire(slot);if(++allocation_serial==0)++allocation_serial;shots[slot].generation=allocation_serial;
 if(actor>=100||!actors[actor].valid||enemyAvail[actor]!=0||turret!=1||!actor_bound(actor))return;
 unsigned record=actors[actor].record;
 if(!scope(record)||!records(record,weapon)||phase>=weapons[weapon].max||
  !actor_origin(actor,record)||enemy[actor].tur[0]!=weapon||
  enemyShotAvail[slot]||enemyShot[slot].sgr!=weapons[weapon].sg[phase]||
  enemyShot[slot].animate||enemyShot[slot].animax!=weapons[weapon].weapani||enemyShot[slot].sdmg!=weapons[weapon].attack[phase]||
  enemyShot[slot].tx!=weapons[weapon].tx||enemyShot[slot].ty!=weapons[weapon].ty||
  enemyShot[slot].duration!=weapons[weapon].del[phase])return;
 shots[slot].actor=actor;shots[slot].actor_generation=actors[actor].generation;
 shots[slot].weapon=weapon;shots[slot].phase=phase;shots[slot].frame=enemyShot[slot].sgr;shots[slot].native_phase=0;shots[slot].valid=true;
}
void enemy_reuse_shot_before_animation(unsigned slot)
{
 /* Advancing another shot supersedes any unused earlier draw witness. */
 transition.pending=transition.complete=false;witness.valid=false;
 if(slot>=ENEMY_SHOT_MAX||!shots[slot].valid||(shots[slot].weapon!=153&&shots[slot].weapon!=141))return;
 if(!enemy_reuse_identity_live(slot,shots[slot].frame+shots[slot].native_phase,enemyShot[slot].sx,enemyShot[slot].sy)){
  enemy_reuse_shot_retire(slot);return;
 }
 transition.slot=slot;transition.generation=shots[slot].generation;
 memcpy(&transition.before,&enemyShot[slot],sizeof(transition.before));transition.pending=true;
}
void enemy_reuse_shot_after_animation(unsigned slot)
{
 bool pending=transition.pending;transition.pending=transition.complete=false;
 if(slot>=ENEMY_SHOT_MAX||!shots[slot].valid||(shots[slot].weapon!=153&&shots[slot].weapon!=141))return;
 if(!pending||transition.slot!=slot||transition.generation!=shots[slot].generation||
  !enemy_reuse_identity_generation(slot)){
  enemy_reuse_shot_retire(slot);return;
 }
 /* The intervening production block changes animate only. No increment or
  * phase repair is applied to simulation state by this observational code. */
 EnemyShotType expected;memcpy(&expected,&transition.before,sizeof(expected));
 expected.animate=(expected.animate+1)%weapons[shots[slot].weapon].weapani;
 if(memcmp(&expected,&enemyShot[slot],sizeof(expected))){enemy_reuse_shot_retire(slot);return;}
 shots[slot].native_phase=expected.animate;transition.complete=true;
}
void enemy_reuse_shot_begin_draw(unsigned slot)
{
 witness.valid=false;
 bool advanced=transition.complete&&transition.slot==slot;
 uint64_t generation=transition.generation;
 transition.pending=transition.complete=false;
 if(slot>=ENEMY_SHOT_MAX||!shots[slot].valid||enemyShotAvail[slot])return;
 if((shots[slot].weapon==153||shots[slot].weapon==141)&&(!advanced||generation!=shots[slot].generation))return;
 unsigned a=shots[slot].actor,w=shots[slot].weapon,p=shots[slot].phase;
 if(a>=100||shots[slot].actor_generation!=actors[a].generation||!actor_bound(a)||!scope(actors[a].record)||!records(actors[a].record,w)||
  enemyShot[slot].sgr!=shots[slot].frame||enemyShot[slot].animate!=shots[slot].native_phase||enemyShot[slot].animax!=weapons[w].weapani||
  enemyShot[slot].sdmg!=weapons[w].attack[p]||enemyShot[slot].tx!=weapons[w].tx||enemyShot[slot].ty!=weapons[w].ty||
  enemyShot[slot].sxc!=weapons[w].accelerationx||enemyShot[slot].syc!=weapons[w].acceleration){shots[slot].valid=false;return;}
 witness.slot=slot;witness.generation=shots[slot].generation;witness.shot=enemyShot[slot];witness.valid=true;
}
void enemy_reuse_draw_end(void) {witness.valid=false;transition.pending=transition.complete=false;}
bool enemy_reuse_identity_live(unsigned slot,unsigned index,int x,int y)
{
 if(!enemy_reuse_identity_generation(slot))return false;
 unsigned w=shots[slot].weapon,p=shots[slot].phase;
 return index==shots[slot].frame+shots[slot].native_phase&&enemyShot[slot].sgr==shots[slot].frame&&
  x==enemyShot[slot].sx&&y==enemyShot[slot].sy&&enemyShot[slot].animate==shots[slot].native_phase&&enemyShot[slot].animax==weapons[w].weapani&&
  enemyShot[slot].sdmg==weapons[w].attack[p]&&enemyShot[slot].tx==weapons[w].tx&&enemyShot[slot].ty==weapons[w].ty&&
  enemyShot[slot].sxc==weapons[w].accelerationx&&enemyShot[slot].syc==weapons[w].acceleration;
}
bool enemy_reuse_identity_matches(unsigned slot,unsigned index,int x,int y)
{
 bool ready=witness.valid;witness.valid=false;transition.pending=transition.complete=false;
 return ready&&enemy_reuse_identity_live(slot,index,x,y)&&slot==witness.slot&&shots[slot].valid&&!enemyShotAvail[slot]&&
  witness.generation==shots[slot].generation&&shots[slot].actor_generation==actors[shots[slot].actor].generation&&
  scope(actors[shots[slot].actor].record)&&records(actors[shots[slot].actor].record,shots[slot].weapon)&&
  index==shots[slot].frame+shots[slot].native_phase&&x==enemyShot[slot].sx&&y==enemyShot[slot].sy&&
  !memcmp(&witness.shot,&enemyShot[slot],sizeof(witness.shot));
}
#endif
